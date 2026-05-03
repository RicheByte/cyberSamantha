"""
Background Ingestion Daemon — Watches a drop folder for new files and auto-ingests them.

Monitors ~/CyberSamantha/DropBox/ (configurable) for new PDFs, code files, docs, etc.
When a file is added, it automatically:
  1. Parses the document
  2. Chunks and vectorizes it into ChromaDB
  3. Extracts knowledge graph entities via Gemini/Ollama
  4. Sends a desktop notification (if available)

Usage:
  # As a standalone daemon:
  python -m src.ingest.daemon

  # Programmatically:
  from src.ingest.daemon import IngestionDaemon
  daemon = IngestionDaemon()
  daemon.start()  # non-blocking background thread
  daemon.stop()
"""

import os
import sys
import time
import threading
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Set, Callable

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    class FileSystemEventHandler:
        pass
    Observer = None

from src.ingest.parsers import DocumentParser
from src.knowledge.vector_store import VectorStore
from src.knowledge.reality_graph import RealityGraph
from src.ingest.extractor import GraphExtractor


# ── Supported file extensions ────────────────────────────────────────────
WATCHED_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".txt", ".md",
    ".json", ".yaml", ".yml",
    ".py", ".js", ".ts", ".go", ".rs", ".c", ".cpp", ".h",
    ".java", ".sh", ".ps1", ".bat",
    ".log", ".conf", ".cfg", ".ini", ".xml",
}

# ── Default drop folder ─────────────────────────────────────────────────
DEFAULT_WATCH_DIR = os.path.join(Path.home(), "CyberSamantha", "DropBox")


class _IngestHandler(FileSystemEventHandler):
    """Watchdog event handler that triggers ingestion on new/modified files."""

    def __init__(self, daemon: "IngestionDaemon"):
        super().__init__()
        self.daemon = daemon
        self._debounce: dict = {}
        self._debounce_seconds = 2.0  # Wait 2s after last event before processing

    def on_created(self, event):
        if not event.is_directory:
            self._schedule(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._schedule(event.src_path)

    def _schedule(self, file_path: str):
        """Debounce rapid events (editors often write multiple times)."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in WATCHED_EXTENSIONS:
            return

        now = time.time()
        last = self._debounce.get(file_path, 0)
        if now - last < self._debounce_seconds:
            return
        self._debounce[file_path] = now

        # Run ingestion in a worker thread to not block the observer
        threading.Thread(
            target=self.daemon._ingest_file,
            args=(file_path,),
            daemon=True,
        ).start()


class IngestionDaemon:
    """
    Background daemon that watches a folder and auto-ingests new documents.
    
    Can run as:
      - A background thread inside the CLI (daemon.start())
      - A standalone process (python -m src.ingest.daemon)
    """

    def __init__(
        self,
        watch_dir: str = None,
        vector_store: VectorStore = None,
        graph_store: RealityGraph = None,
        on_ingest: Callable[[str, int], None] = None,
    ):
        self.watch_dir = watch_dir or os.getenv("CYBERSAMANTHA_DROPBOX", DEFAULT_WATCH_DIR)
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.graph_extractor: Optional[GraphExtractor] = None
        self.on_ingest = on_ingest  # callback(file_path, chunk_count)

        self._observer: Optional[Observer] = None
        self._running = False
        self._processed_hashes: Set[str] = set()
        self._lock = threading.Lock()
        self._ingest_log: list = []

        # Ensure the watch directory exists
        os.makedirs(self.watch_dir, exist_ok=True)

    def _lazy_init_stores(self):
        """Initialize vector/graph stores lazily (for standalone mode)."""
        if self.vector_store is None:
            self.vector_store = VectorStore()
        if self.graph_store is None:
            self.graph_store = RealityGraph()
        if self.graph_extractor is None:
            self.graph_extractor = GraphExtractor(self.graph_store)

    def start(self) -> bool:
        """Start watching in a background thread. Returns True if started successfully."""
        if not HAS_WATCHDOG:
            print("⚠️  'watchdog' package not installed. Run: pip install watchdog")
            return False

        if self._running:
            print("ℹ️  Daemon is already running.")
            return True

        self._lazy_init_stores()

        handler = _IngestHandler(self)
        self._observer = Observer()
        self._observer.schedule(handler, self.watch_dir, recursive=True)
        self._observer.daemon = True
        self._observer.start()
        self._running = True

        print(f"👁️  Ingestion daemon watching: {self.watch_dir}")
        return True

    def stop(self):
        """Stop the background watcher."""
        if self._observer and self._running:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._running = False
            print("🛑 Ingestion daemon stopped.")

    @property
    def is_running(self) -> bool:
        return self._running

    def get_log(self) -> list:
        """Return recent ingestion log entries."""
        return list(self._ingest_log)

    def _ingest_file(self, file_path: str):
        """Parse, chunk, vectorize, and extract graph entities from a single file."""
        with self._lock:
            try:
                # Check file hash to avoid re-processing identical content
                file_hash = DocumentParser.get_file_hash(file_path)
                if not file_hash or file_hash in self._processed_hashes:
                    return
                self._processed_hashes.add(file_hash)

                file_name = os.path.basename(file_path)
                relative_path = os.path.relpath(file_path, self.watch_dir)

                print(f"\n📥 Auto-ingesting: {file_name}")

                # 1. Parse the file
                content = DocumentParser.read_file(file_path)
                if not content or not content.strip():
                    print(f"  ⏭️  Empty file, skipping: {file_name}")
                    return

                # 2. Chunk the content
                chunks = DocumentParser.chunk_text(content)
                if not chunks:
                    return

                # 3. Vectorize into ChromaDB
                documents = []
                metadatas = []
                ids = []

                for i, chunk in enumerate(chunks):
                    chunk_id = f"drop_{relative_path}_chunk_{i}_{hashlib.md5(chunk.encode()).hexdigest()[:8]}"
                    documents.append(chunk)
                    metadatas.append({
                        "file_path": f"dropbox/{relative_path}",
                        "file_name": file_name,
                        "chunk_index": i,
                        "file_hash": file_hash,
                        "timestamp": datetime.now().isoformat(),
                        "chunk_size": len(chunk),
                        "source": "auto_ingest",
                        "embedding_model": self.vector_store.embedding_model_name,
                    })
                    ids.append(chunk_id)

                self.vector_store.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                )

                # 4. Extract graph entities
                if self.graph_extractor:
                    for chunk in chunks:
                        self.graph_extractor.extract_from_text(chunk, f"dropbox/{relative_path}")

                # 5. Log and notify
                log_entry = {
                    "file": file_name,
                    "path": relative_path,
                    "chunks": len(chunks),
                    "timestamp": datetime.now().isoformat(),
                }
                self._ingest_log.append(log_entry)

                print(f"  ✅ Ingested {len(chunks)} chunks from {file_name}")
                print(f"  📊 Total docs in vector store: {self.vector_store.collection.count()}")

                # Callback for CLI notification
                if self.on_ingest:
                    self.on_ingest(file_path, len(chunks))

            except Exception as e:
                print(f"  ❌ Error ingesting {file_path}: {e}")

    def ingest_existing(self):
        """One-shot: ingest all files already in the watch directory."""
        self._lazy_init_stores()

        count = 0
        for root, _, files in os.walk(self.watch_dir):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in WATCHED_EXTENSIONS:
                    self._ingest_file(os.path.join(root, fname))
                    count += 1

        if count == 0:
            print(f"📁 No files found in {self.watch_dir}")
        else:
            print(f"\n🎉 Finished ingesting {count} existing files.")


# ── Standalone entry point ───────────────────────────────────────────────
def main():
    """Run the daemon as a standalone process."""
    from dotenv import load_dotenv
    load_dotenv()

    print("=" * 60)
    print("  CyberSamantha — Background Ingestion Daemon")
    print("=" * 60)

    daemon = IngestionDaemon()

    # First pass: ingest anything already in the folder
    daemon.ingest_existing()

    # Start live watcher
    if daemon.start():
        print(f"\n💡 Drop files into: {daemon.watch_dir}")
        print("   Press Ctrl+C to stop.\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            daemon.stop()
    else:
        print("Failed to start daemon. Install watchdog: pip install watchdog")
        sys.exit(1)


if __name__ == "__main__":
    main()
