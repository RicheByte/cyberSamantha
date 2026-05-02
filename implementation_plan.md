# CyberSamantha: Next-Gen "Second Brain" CLI Architecture Plan

This plan details the modernization of the CyberSamantha core to transform it into a fast, lightweight, and autonomous "second brain" operating directly in your CLI.

## 1. Architectural Overhaul: Modular & Event-Driven
Currently, `cybersamatha.py` is a monolithic script. We will break this down into a highly modular, event-driven architecture for speed and maintainability.

### New Project Structure
```text
cyberSamantha/
├── core/                  # Core orchestration and routing
│   ├── agent.py           # LLM agent routing & autonomous decision making
│   └── config.py          # Configuration management
├── memory/                # Memory Management
│   ├── episodic.py        # Short-term conversation history
│   └── semantic.py        # Long-term user facts and entity storage
├── knowledge/             # Knowledge representation
│   ├── vector_store.py    # ChromaDB wrapper (existing RAG)
│   └── graph_store.py     # New Knowledge Graph using NetworkX / JSON
├── ingest/                # Data ingestion pipelines
│   └── parsers.py         # Modular file parsers (PDF, DOCX, etc.)
└── cli/                   # Modern Command Line Interface
    └── app.py             # Rich-based interactive REPL
```

## 2. Memory Layer Implementation
We will implement a dual-tier memory system to make CyberSamantha "smarter" and capable of remembering past interactions.

*   **Short-Term (Episodic) Memory:** Stores the current session's conversation history to maintain context during a chat loop.
*   **Long-Term (Semantic) Memory:** A lightweight JSON-based storage that extracts facts about the user or preferences and persists them across sessions. The agent will proactively query this before answering.

## 3. Knowledge Graph Integration
To complement the vector database (ChromaDB), we will introduce a lightweight, local Knowledge Graph.

*   **Tech Stack:** `networkx` for fast, in-memory graph operations, serialized to local JSON (`graph.json`) for persistence.
*   **Functionality:** When documents are indexed, the LLM will extract key entities (e.g., Vulnerabilities, Actors, Tools) and relationships. 
*   **Wiki-Like Consumption:** The CLI will support a `/wiki <topic>` command that queries the graph for direct relationships and supplements it with vector search, generating a comprehensive summary without needing a heavy frontend.

## 4. Agentic Intelligence
We will upgrade the query pipeline from a simple RAG to an intelligent agent.

*   **Router:** When a user asks a question, the LLM will first classify the intent:
    *   *Question Answering:* Query Vector DB.
    *   *Fact Retrieval:* Query Knowledge Graph.
    *   *Memory Update:* Extract new fact and store it.
*   **Autonomy:** The agent can decide to perform multiple tool calls (search vector DB -> search Graph -> combine) before delivering the final answer to the user.

## 5. Performance Optimizations
*   **Lazy Loading:** Ensure heavy models (like SentenceTransformers) are strictly lazy-loaded only when indexing or generating embeddings, keeping the CLI startup time under 1 second.
*   **Async/Await:** Transition I/O bound tasks (like querying Gemini or reading files) to asynchronous patterns for a snappier feel.
*   **Rich UI:** Upgrade the terminal UI using `rich` for dynamic formatting, tables, syntax highlighting, and progress bars.

## Next Steps for Implementation
1.  **Refactoring:** Restructure the existing monolithic `cybersamatha.py` into the new `core/`, `ingest/`, and `cli/` modules.
2.  **Memory System:** Build the local JSON memory manager.
3.  **Knowledge Graph:** Integrate `networkx` and build the entity extraction pipeline for indexing.
4.  **Agentic Loop:** Implement the new smart query router using Gemini 2.0 Flash.

**Would you like me to begin Phase 1: Restructuring the monolithic codebase into the new modular architecture?**
