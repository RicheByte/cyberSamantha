# CyberSamantha: Autonomous Cybersecurity Cognitive Ecosystem

```text
                                       
 ▄▄▄▄  ▄▄▄  ▄▄   ▄▄  ▄▄▄  ▄▄  ▄▄ ▄▄▄▄▄▄ ▄▄ ▄▄  ▄▄▄  
███▄▄ ██▀██ ██▀▄▀██ ██▀██ ███▄██   ██   ██▄██ ██▀██ 
▄▄██▀ ██▀██ ██   ██ ██▀██ ██ ▀██   ██   ██ ██ ██▀██ 
                                                    
```

CyberSamantha has evolved from a standard Command Line Interface (CLI) tool into a fast, modular, and self-improving "Cognitive Ecosystem". Rather than functioning purely as a reactive assistant, the system is designed to simulate intelligence through an interconnected web of multi-agent delegation, probabilistic world modeling, and Darwinian capability evolution.

This document serves as a comprehensive guide to the theory, architecture, and mechanics driving the CyberSamantha ecosystem.

---

## 1. Multi-Agent Swarm Architecture

At the core of the system is the swarm architecture, which distributes cognitive load across specialized discrete entities rather than relying on a single monolithic prompt.

*   **AgentRouter (The Manager):** Acts as the central orchestrator. When a user submits a query, the AgentRouter processes the intent, consults the memory layers, and decides whether to handle the query directly or delegate it to a specialist sub-agent.
*   **HackerAgent:** Specialized in offensive security. Holds prompts and capabilities tailored for penetration testing, reconnaissance (e.g., Nmap analysis), and vulnerability identification.
*   **ResearcherAgent:** Specialized in threat intelligence. Capable of parsing complex CVE reports, gathering deep web intelligence, and synthesizing vast amounts of text into actionable reports.
*   **CoderAgent:** Specialized in reverse engineering, secure code review, and malware analysis. 

The swarm is backed by a **Hybrid LLM Provider**. The system defaults to the Google Gemini API for tasks requiring advanced reasoning, speed, and function calling. However, it is built with an abstraction layer that allows it to seamlessly fall back to local Ollama models when privacy or air-gapping is required.

---

## 2. The 5 Pillars of Cognition

The intelligence of CyberSamantha is built upon five foundational pillars that allow it to learn, debate, and evolve independently.

### Pillar 1: Skill Genome Engine (Darwinian Capability Evolution)
Traditional AI systems use static tools. CyberSamantha treats its capabilities (both Python functions and Markdown playbooks) as genetic material. The GenomeEngine tracks the execution of every tool. When an agent calls a skill, the engine records its execution duration and success state. Over time, a registry is built mapping the true "fitness" of each capability. Underperforming skills can be autonomously pruned by the system, while high-performing skills can be selected for LLM-driven mutation or recombination to spawn highly specialized variants.

### Pillar 2: Reality Graph Layer (Probabilistic World State)
Standard Knowledge Graphs operate on binary truth (a relationship either exists or it does not). The RealityGraph upgrades this by introducing a probabilistic world state built on NetworkX. When the background ingestion daemon reads a document, it uses the LLM to extract entities (e.g., Tools, Vulnerabilities, Actors) and assign a "confidence score" (0.0 to 1.0) to their relationships. Furthermore, unverified relationships experience simulated "temporal drift," decaying in confidence over time unless re-verified by new incoming data.

### Pillar 3: Cross-Agent Thought Interference (Debate Orchestrator)
When faced with a complex hypothesis or analytical task, linear delegation is insufficient. The ThoughtRouter can trigger the DebateOrchestrator to execute "Cross-Agent Thought Interference". The orchestrator pits two agents against each other—assigning one agent (e.g., the CoderAgent) as the primary defender of a thesis, and another (e.g., the HackerAgent) as the active adversary. The adversary rigorously critiques the thesis, the primary agent defends or modifies it, and a synthesis engine eventually collapses the multi-perspective debate into a single, highly refined conclusion.

### Pillar 4: Meta-Memory (Execution Strategy Tracking)
The system needs to know *how* to think. MetaMemory tracks the outcomes of cognitive strategies. When a task is completed, Meta-Memory logs whether a "linear" delegation or an "adversarial debate" produced a better result for that specific class of task. During future operations, the ThoughtRouter queries Meta-Memory to make data-driven decisions on the optimal execution path.

### Pillar 5: Curiosity Engine (Autonomous Research Drive)
Intelligence requires proactive action. The CuriosityDaemon runs silently in a background thread, continually evaluating the internal pressure of the RealityGraph. It actively scans for logical contradictions or relationships whose confidence scores have decayed below an acceptable threshold. When a contradiction is found, the daemon bypasses the user and autonomously dispatches a background agent swarm to research the conflict via web searches or document analysis, resolving the graph's internal tension.

---

## 3. Tri-Layer Memory System

CyberSamantha utilizes three distinct memory mechanisms to maintain context and adapt to the user.

1.  **Episodic Memory:** Short-term memory that manages the sliding window of the current conversation session. It provides immediate conversational context and clears when the application is restarted.
2.  **Semantic Memory:** Long-term factual storage. Users can explicitly teach the system facts using the command "remember that...". These facts are injected into the system prompt of every agent, ensuring the swarm permanently adapts to the user's environment, preferences, and operational parameters.
3.  **Meta-Memory:** (As detailed in Pillar 4) Tracks the performance metrics of the system's own reasoning pathways.

---

## 4. Continuous Ingestion & Vector RAG

To support its intelligence, the system requires continuous access to ground-truth data.

*   **Vector Store (ChromaDB):** Handles Retrieval-Augmented Generation (RAG). Documents are parsed, chunked, and embedded into a local ChromaDB instance using local sentence-transformers, ensuring high-speed semantic search without sending proprietary documents to external APIs.
*   **Background Ingestion Daemon:** The system monitors a configurable drop folder via the watchdog library. When a new file (PDF, code, log, markdown, etc.) is dropped into the folder, the daemon automatically wakes up. It reads the file, parses it, chunk it into the Vector Store, and simultaneously triggers the GraphExtractor to pull entities for the Reality Graph.

---

## 5. Installation and Setup

### Prerequisites
*   Python 3.8+
*   Google Gemini API key (GEMINI_API_KEY)
*   Ollama (Optional, for local fallback mode)

### Initialization Steps

1.  Clone the repository and set up a Python virtual environment:
    ```bash
    git clone https://github.com/RicheByte/cyberSamantha
    cd cyberSamantha
    python -m venv myenv
    ```

2.  Activate the environment:
    ```bash
    # Windows
    myenv\Scripts\activate
    # Linux/Mac
    source myenv/bin/activate
    ```

3.  Install all required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure environment variables by creating a .env file in the root directory:
    ```env
    GEMINI_API_KEY=your_api_key_here
    CYBERSAMANTHA_DROPBOX=C:/Path/To/Your/Dropbox
    ```

---

## 6. Advanced Usage and CLI Commands

Start the primary interactive shell:
```bash
python main.py
```

Within the interactive CLI, the following commands control the ecosystem:

*   **Standard Query**: Type any natural language query to trigger the AgentRouter and LLM reasoning loop.
*   `/wiki <topic>`: Query the Reality Graph directly for a structured summary of an entity.
*   `search <query>`: Execute an external web search for recent threat intelligence.
*   `run <command>`: Execute a terminal command locally (requires user confirmation if unsafe).
*   `read <file_path>`: Read the contents of a local file into the context window.
*   `think`: Re-process the previous query and explicitly print the Chain-of-Thought reasoning steps.
*   `remember that <fact>`: Store a permanent factual node in Semantic Memory.
*   `/status`: Print a comprehensive health and statistics table for all ecosystem components.
*   `/daemon start`: Boot the background ingestion and curiosity daemon.
*   `/daemon stop`: Halt the background daemon.
*   `/daemon log`: Print a history of files autonomously ingested by the background watcher.
*   `/provider`: Display the currently active LLM provider and model name.
*   `/skills`: List all loaded genetic skills, their types, compatibility, and execution status.
*   `/skills enable <name>`: Manually activate a specific capability.
*   `/skills disable <name>`: Manually deactivate a specific capability.

---

## 7. Architecture Directory Map

The internal source code is strictly structured to support modularity and ease of maintenance:

*   `src/agents/`: Contains the BaseAgent abstract class, specialized discrete agents (Hacker, Coder, Researcher), and the Debate Orchestrator.
*   `src/core/`: Houses the AgentRouter (Manager), the Curiosity Daemon, the Thought Router, and the Hybrid LLM Provider.
*   `src/ingest/`: Contains the FileSystemEventHandler daemon, format parsers, and the LLM Graph Extractor.
*   `src/knowledge/`: Integrates local storage systems including ChromaDB (VectorStore) and NetworkX (RealityGraph).
*   `src/memory/`: Implements the distinct memory tiers (Episodic, Semantic, Meta).
*   `src/skills/`: Holds the dynamic SkillLoader, the GenomeEngine registry, and all pluggable Python and Markdown capabilities.
