# CyberSamantha: Your AI Cybersecurity "Second Brain"

![Diagram](/assets/how%20it%20works.png)

CyberSamantha has been completely re-architected into a fast, modular, and intelligent "second brain" that lives in your CLI. It combines your local cybersecurity documentation with regularly updated data from leading security repositories, a vector database, a local knowledge graph, and a robust memory layer to create an incredibly powerful knowledge base.

## 🚀 Key Features

*   **Intelligent Agent Routing**: Powered by Gemini 2.0 Flash, CyberSamantha intelligently routes queries to the most appropriate subsystem.
*   **Vector RAG (Retrieval-Augmented Generation)**: Uses ChromaDB and local sentence-transformers for fast, private document embedding and retrieval.
*   **Knowledge Graph (`/wiki`)**: Automatically extracts entities (Tools, Actors, Vulnerabilities) during indexing into a local GraphStore (`networkx`) for lightning-fast wiki-style entity summaries.
*   **Dual Memory Layer**:
    *   *Episodic*: Remembers short-term conversation history for context during chats.
    *   *Semantic*: Learns and stores facts (`remember that...`) to personalize and improve responses over time.
*   **Multi-format Document Support**: Handles PDF, DOCX, PPTX, JSON, YAML, TXT, and MD files.
*   **Modern CLI**: Beautiful, interactive terminal interface built with `rich`.

## 🛠️ Quick Start

### Prerequisites
*   Python 3.8+
*   Google Gemini API key (`GEMINI_API_KEY`)

### Installation

1.  Clone the repository and set up a virtual environment:
    ```bash
    git clone https://github.com/RicheByte/cyberSamantha
    cd cyberSamantha
    python -m venv myenv
    # Windows
    myenv\Scripts\activate
    # Linux/Mac
    source myenv/bin/activate
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    pip install networkx rich
    ```

3.  Configure your environment:
    Create a `.env` file in the root directory and add:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

### Usage

**1. Indexing your Knowledge Base:**
Place your documents in the `data/` folder, then run the indexer. This will chunk the documents for the Vector DB and use the LLM to extract entities for the Knowledge Graph.
```bash
python main.py --index
```

**2. Starting the Interactive Second Brain:**
```bash
python main.py
```

**Inside the CLI:**
*   **Standard Query**: Ask any question, and Samantha will use RAG and conversation history to answer.
    *   `You: What are the mitigation steps for Log4j?`
*   **Wiki Mode**: Query the Knowledge Graph for a structured summary of an entity.
    *   `You: /wiki APT29`
*   **Teach Samantha**: Save semantic facts directly to her long-term memory.
    *   `You: remember that my primary OS is Windows 11`

## 🧠 Architecture

CyberSamantha is built on a highly modular architecture located in `src/`:
*   `core/agent.py`: The brain that orchestrates tool use, memory access, and LLM generation.
*   `knowledge/vector_store.py`: ChromaDB integration for semantic document search.
*   `knowledge/graph_store.py`: Local NetworkX graph database for entity relationship mapping.
*   `memory/`: Short-term (`episodic.py`) and long-term (`semantic.py`) memory managers.
*   `ingest/`: Document parsers and the LLM-based graph entity extractor.
*   `cli/app.py`: The `rich`-powered command-line interface.
