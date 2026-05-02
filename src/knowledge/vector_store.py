import os
import glob
import hashlib
from datetime import datetime
from typing import List, Dict, Any

try:
    import chromadb
    from chromadb.utils import embedding_functions
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"❌ Missing required package: {e}")

from src.ingest.parsers import DocumentParser

class LocalEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_name: str, get_transformer_fn):
        self.model_name = model_name
        self.get_transformer_fn = get_transformer_fn
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        transformer = self.get_transformer_fn()
        embeddings = transformer.encode(
            input, 
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings.tolist()

class VectorStore:
    def __init__(self, data_path: str = "data", chroma_path: str = "chroma_db", embedding_model: str = "all-MiniLM-L6-v2", lazy_load: bool = True):
        self.data_path = data_path
        self.chroma_path = chroma_path
        self.embedding_model_name = embedding_model
        self.sentence_transformer = None
        self.lazy_load = lazy_load

        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.chroma_path, exist_ok=True)

        self._setup_vector_db()

    def _get_sentence_transformer(self):
        if self.sentence_transformer is None:
            try:
                os.environ['TRANSFORMERS_OFFLINE'] = '0'
                os.environ['HF_HUB_OFFLINE'] = '0'
                self.sentence_transformer = SentenceTransformer(
                    self.embedding_model_name,
                    device='cpu'
                )
            except Exception as e:
                print(f"❌ Failed to load embedding model: {e}")
                raise
        return self.sentence_transformer

    def _setup_vector_db(self):
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            
            if not self.lazy_load:
                self._get_sentence_transformer()

            self.embedding_function = LocalEmbeddingFunction(
                self.embedding_model_name, 
                self._get_sentence_transformer
            )

            try:
                self.collection = self.chroma_client.get_collection(
                    name="cybersamatha_docs",
                    embedding_function=self.embedding_function
                )
            except Exception:
                self.collection = self.chroma_client.create_collection(
                    name="cybersamatha_docs",
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"}
                )
        except Exception as e:
            print(f"❌ Error setting up vector database: {e}")
            raise

    def index_documents(self, force_reindex: bool = False, extraction_callback=None):
        print("🔍 Scanning for documents...")
        extensions = ['*.txt', '*.md', '*.json', '*.yaml', '*.yml', '*.pdf', '*.docx', '*.pptx']
        all_files = []
        for ext in extensions:
            all_files.extend(glob.glob(os.path.join(self.data_path, '**', ext), recursive=True))
            all_files.extend(glob.glob(os.path.join(self.data_path, '**', ext.upper()), recursive=True))
        
        if not all_files:
            print("📁 No documents found in the 'data' folder")
            return
            
        print(f"📁 Found {len(all_files)} documents")
        processed_count = 0
        total_chunks = 0
        skipped_count = 0

        for file_path in all_files:
            try:
                file_hash = DocumentParser.get_file_hash(file_path)
                file_name = os.path.basename(file_path)
                relative_path = os.path.relpath(file_path, self.data_path)
                
                if not file_hash: continue

                if not force_reindex:
                    try:
                        existing = self.collection.get(
                            where={"file_path": relative_path},
                            include=["metadatas"]
                        )
                        if existing["metadatas"] and existing["metadatas"][0].get("file_hash") == file_hash:
                            print(f"⏭️  Skipping unchanged: {relative_path}")
                            skipped_count += 1
                            continue
                        elif existing["ids"]:
                            print(f"🔄 Updating: {relative_path}")
                            self.collection.delete(ids=existing["ids"])
                    except Exception:
                        pass

                print(f"📖 Processing: {relative_path}")
                content = DocumentParser.read_file(file_path)
                if not content or not content.strip(): continue

                chunks = DocumentParser.chunk_text(content)
                if not chunks: continue

                documents = []
                metadatas = []
                ids = []

                for i, chunk in enumerate(chunks):
                    chunk_id = f"{relative_path}_chunk_{i}_{hashlib.md5(chunk.encode()).hexdigest()[:8]}"
                    documents.append(chunk)
                    metadatas.append({
                        "file_path": relative_path,
                        "file_name": file_name,
                        "chunk_index": i,
                        "file_hash": file_hash,
                        "timestamp": datetime.now().isoformat(),
                        "chunk_size": len(chunk),
                        "embedding_model": self.embedding_model_name
                    })
                    ids.append(chunk_id)

                    if extraction_callback:
                        extraction_callback(chunk, relative_path)

                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                processed_count += 1
                total_chunks += len(chunks)
                print(f"✅ Indexed {len(chunks)} chunks from {relative_path}")
            except Exception as e:
                print(f"❌ Error processing {file_path}: {str(e)}")

        print("\n" + "="*60)
        if processed_count > 0:
            print(f"🎉 Indexing complete! Processed: {processed_count} files, Created: {total_chunks} chunks.")
        else:
            print("ℹ️  No new files to index.")
        print("="*60)

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            search_results = []
            if results["documents"] and results["documents"][0]:
                for doc, meta, distance in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                ):
                    search_results.append({
                        "content": doc,
                        "metadata": meta,
                        "score": 1 - distance,
                        "file_name": meta.get("file_name", "Unknown"),
                        "file_path": meta.get("file_path", "Unknown")
                    })
            return search_results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        try:
            return {
                "total_chunks": self.collection.count(),
                "collection_name": "cybersamatha_docs",
                "database_path": self.chroma_path,
                "embedding_model": self.embedding_model_name
            }
        except Exception as e:
            return {"error": str(e)}
