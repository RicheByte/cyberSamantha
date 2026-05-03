# CyberSamantha: Autonomous Cybersecurity Cognitive Ecosystem

```text
                                       
  ▄▄▄▄  ▄▄▄  ▄▄   ▄▄  ▄▄▄  ▄▄  ▄▄ ▄▄▄▄▄▄ ▄▄ ▄▄  ▄▄▄  
 ███▄▄ ██▀██ ██▀▄▀██ ██▀██ ███▄██   ██   ██▄██ ██▀██ 
 ▄▄██▀ ██▀██ ██   ██ ██▀██ ██ ▀██   ██   ██ ██ ██▀██ 
                                                     
```

CyberSamantha is a fast, modular, and self-improving **Cognitive Ecosystem** for cybersecurity. Rather than functioning as a reactive chatbot, it simulates intelligence through an interconnected web of multi-agent delegation, probabilistic world modeling, retrieval-augmented generation (RAG), and Darwinian capability evolution.

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Multi-Agent Swarm Architecture](#2-multi-agent-swarm-architecture)
3. [The 5 Pillars of Cognition](#3-the-5-pillars-of-cognition)
4. [Tri-Layer Memory System](#4-tri-layer-memory-system)
5. [Continuous Ingestion & Vector RAG](#5-continuous-ingestion--vector-rag)
6. [Skill Genome System](#6-skill-genome-system)
7. [Installation & Setup](#7-installation--setup)
8. [CLI Commands & Usage](#8-cli-commands--usage)
9. [Data Sources & Update Pipeline](#9-data-sources--update-pipeline)
10. [Storage Cleanup & Optimization](#10-storage-cleanup--optimization)
11. [Directory Map](#11-directory-map)
12. [Environment Variables & Configuration](#12-environment-variables--configuration)
13. [How a Query Flows Through the System](#13-how-a-query-flows-through-the-system)
14. [Extending the System](#14-extending-the-system)

---

## 1. System Architecture Overview

CyberSamantha is composed of **five major subsystems** that work together:

```
┌─────────────────────────────────────────────────────┐
│  CLI (rich terminal UI)                             │
│  /status  /daemon  /wiki  /provider  /skills        │
├─────────────────────────────────────────────────────┤
│  AgentRouter (Manager)                              │
│  ├── LLMProvider (Gemini ↔ Ollama hot-swap)         │
│  ├── HackerAgent     → TerminalTool (nmap, curl)    │
│  ├── ResearcherAgent → WebSearchTool (Exa API)      │
│  ├── CoderAgent      → FileReaderTool + Terminal    │
│  ├── RAG Pipeline    → VectorStore (ChromaDB)       │
│  └── Wiki Pipeline   → RealityGraph (NetworkX)      │
├─────────────────────────────────────────────────────┤
│  Memory Layer                                       │
│  ├── EpisodicMemory  (sliding window + summarization)│
│  ├── SemanticMemory  (persistent user facts, JSON)  │
│  └── MetaMemory      (strategy outcome tracking)    │
├─────────────────────────────────────────────────────┤
│  Background Daemons                                 │
│  ├── IngestionDaemon  (watchdog → DropBox folder)   │
│  └── CuriosityDaemon  (contradiction detection)     │
├─────────────────────────────────────────────────────┤
│  Skill System                                       │
│  ├── GenomeEngine     (usage tracking, pruning)     │
│  ├── SkillLoader      (MD playbooks + Python tools) │
│  └── Skills: crypto, osint, pentest, code_review…   │
└─────────────────────────────────────────────────────┘
```

---

## 2. Multi-Agent Swarm Architecture

The system distributes cognitive load across **specialized agents** rather than relying on a single monolithic prompt.

### AgentRouter (Manager)
- **File:** `src/core/agent.py`
- The central orchestrator. Receives user queries, classifies intent, and decides whether to answer directly, delegate to a specialist sub-agent, or trigger a multi-agent debate.
- Implements a **ReAct-style autonomous loop** (Thought → Action → Observation → Final Answer) with up to 5 iterations.
- Has direct access to three built-in tools: `WebSearchTool`, `TerminalTool`, `FileReaderTool`.

### HackerAgent
- **File:** `src/agents/hacker.py`
- Specializes in **offensive security**: reconnaissance, vulnerability assessment, network scanning.
- Tools: `run_network_scan(target_ip, scan_type)` — wraps `nmap` with safe argument patterns; `check_headers(url)` — wraps `curl -s -I` for HTTP header inspection.
- Loaded with the `pentest_playbook` markdown skill.

### ResearcherAgent
- **File:** `src/agents/researcher.py`
- Specializes in **threat intelligence**, CVE lookups, and web research synthesis.
- Tools: `search_threat_intel(query)` — searches the web via Exa API; `search_cve(cve_id)` — targeted CVE lookup.
- Loaded with the `threat_intel` markdown skill.

### CoderAgent
- **File:** `src/agents/coder.py`
- Specializes in **code analysis, security review, and local file inspection**.
- Tools: `read_source_file(file_path)`, `analyze_directory(directory_path)`, `run_analysis_command(command)` — safe terminal commands for code analysis.
- Loaded with `code_review` and `log_analysis` markdown skills.

### DebateOrchestrator
- **File:** `src/agents/debate_orchestrator.py`
- Implements **Cross-Agent Thought Interference**. Pits a primary agent (thesis defender) against an adversarial agent (critic) over multiple rounds, then synthesizes a final conclusion.
- Used when the ThoughtRouter determines a task requires adversarial reasoning.

### Hybrid LLM Provider
- **File:** `src/core/llm_provider.py`
- Transparent hot-swap between **Google Gemini** (cloud) and **Ollama** (local).
- Priority order:
  1. If `GEMINI_API_KEY` is set → Gemini (`gemini-2.0-flash`)
  2. If Ollama is reachable at `http://localhost:11434` → Ollama (configurable model)
  3. Fallback → no generation capability (RAG still works for source retrieval)
- Supports both `generate()` (single prompt) and `chat()` (message history) modes.
- Environment variables: `LLM_PROVIDER` (`auto`/`gemini`/`ollama`), `OLLAMA_MODEL`, `OLLAMA_BASE_URL`.

---

## 3. The 5 Pillars of Cognition

### Pillar 1: Skill Genome Engine (Darwinian Capability Evolution)
- **File:** `src/skills/genome_engine.py`
- Tracks every skill's execution: **usage count**, **success rate** (rolling average), and **average execution time**.
- Registry stored in `skills/genome_registry.json`.
- Supports `mutate_skill()` (spawn variants) and `recombine_skills()` (merge two skills) — LLM-driven mutation is planned.
- `prune_weak_skills(threshold)` archives skills with success rate below the threshold after sufficient usage.

### Pillar 2: Reality Graph Layer (Probabilistic World State)
- **File:** `src/knowledge/reality_graph.py`
- Built on **NetworkX** as a directed graph persisted to `data/reality_graph.json`.
- Unlike standard knowledge graphs, every entity and relationship carries a **confidence score** (0.0–1.0) and timestamps (`discovered_at`, `last_verified`).
- `decay_confidence(drift_factor)` simulates **temporal drift** — unverified relationships lose confidence over time.
- `detect_contradictions()` scans for edges with confidence < 0.5 and flags them for the Curiosity Engine.

### Pillar 3: Cross-Agent Thought Interference (Debate Orchestrator)
- See `DebateOrchestrator` above. Triggered by the `ThoughtRouter` when Meta-Memory indicates debate produces better outcomes for a given task type.

### Pillar 4: Meta-Memory (Execution Strategy Tracking)
- **File:** `src/memory/meta_memory.py`
- Persisted to `data/meta_memory.json`.
- Logs every reasoning strategy execution: `task_type`, `strategy` (e.g., `debate` or `linear`), `agents_used`, `outcome_score`, and `context`.
- `query_best_strategy(task_type)` returns the highest-scoring strategy for a given task, enabling data-driven routing decisions.

### Pillar 5: Curiosity Engine (Autonomous Research Drive)
- **File:** `src/core/curiosity_daemon.py`
- Runs in a background thread on a configurable interval (default: 60 seconds).
- `evaluate_internal_pressure()` checks the RealityGraph for contradictions. When found, it autonomously dispatches the AgentRouter to research the conflict via web search or document analysis.
- If no contradictions exist, it triggers `decay_confidence()` to simulate temporal drift across the graph.

---

## 4. Tri-Layer Memory System

### Episodic Memory (Short-Term)
- **File:** `src/memory/episodic.py`
- Stores the current conversation session as a list of `{role, content}` messages.
- **Sliding window:** when history exceeds `max_history * 2` entries, it triggers `_summarize_and_decay()`.
- Summarization uses the LLM to compress the oldest half of the conversation into a persistent summary block, preventing context overflow while retaining key information.
- Falls back to simple truncation if no LLM is available.

### Semantic Memory (Long-Term Facts)
- **File:** `src/memory/semantic.py`
- Persisted to `data/memory.json` as a key-value dictionary.
- Users teach facts via `remember that <fact>` — facts are injected into every agent's system prompt.
- Enables permanent adaptation to the user's environment and preferences.

### Meta-Memory (Strategy Tracking)
- See Pillar 4 above.

---

## 5. Continuous Ingestion & Vector RAG

### Vector Store (ChromaDB)
- **File:** `src/knowledge/vector_store.py`
- Local ChromaDB instance stored in `chroma_db/`.
- Uses **SentenceTransformers** (`all-MiniLM-L6-v2`) for local embeddings — no documents are sent to external APIs for embedding.
- **Lazy loading:** the transformer model is only loaded when actually needed, keeping CLI startup under 1 second.
- `index_documents()` scans `data/` recursively for `.txt`, `.md`, `.json`, `.yaml`, `.pdf`, `.docx`, `.pptx` files.
- **Smart reindexing:** uses file hashes to skip unchanged files. Supports `--force` for full reindex.
- `search(query, n_results)` returns ranked results with cosine similarity scores.

### Background Ingestion Daemon
- **File:** `src/ingest/daemon.py`
- Uses **watchdog** to monitor a drop folder (default: `~/CyberSamantha/DropBox/`, configurable via `CYBERSAMANTHA_DROPBOX`).
- Watches 30+ file extensions: PDFs, DOCX, PPTX, code files, configs, logs, markdown, JSON, YAML, etc.
- **Debounce logic:** waits 2 seconds after the last file event before processing (prevents duplicate ingestion from editors that write multiple times).
- **Deduplication:** uses MD5 file hashes to avoid re-processing identical content.
- Pipeline per file:
  1. Parse the document (format-specific extraction)
  2. Chunk the text (smart chunking at sentence/paragraph boundaries)
  3. Vectorize into ChromaDB with rich metadata
  4. Extract knowledge graph entities via LLM (GraphExtractor)
  5. Log the ingestion and notify the CLI via callback
- Can run as a background thread inside the CLI or as a standalone process (`python -m src.ingest.daemon`).

### Document Parser
- **File:** `src/ingest/parsers.py`
- Multi-format text extraction:
  - **PDF:** PyPDF2 page-by-page extraction
  - **DOCX:** python-docx paragraph extraction
  - **PPTX:** python-pptx slide/shape text extraction
  - **JSON/YAML:** structured serialization to readable text
  - **Plain text:** direct read with UTF-8 encoding
- `chunk_text(text, chunk_size=1000, chunk_overlap=200)`: smart chunking that prefers breaking at sentence boundaries (`. `) or newlines.
- `get_file_hash(file_path)`: MD5 hashing for deduplication.

### Graph Extractor
- **File:** `src/ingest/extractor.py`
- Uses the LLM to extract cybersecurity entities (Vulnerabilities, Tools, Actors, Techniques, Mitigations) and their relationships from text chunks.
- Returns structured JSON with `source`, `target`, `relation`, `confidence`, `source_type`, `target_type`.
- Each extracted relationship is added to the RealityGraph with its confidence score and source file attribution.

---

## 6. Skill Genome System

CyberSamantha has **two types of skills**:

### Markdown Skills (Instruction Playbooks)
- Located in the `skills/` folder at the project root.
- `.md` files parsed by `SkillLoader` into `MarkdownSkill` objects.
- Must contain a `## Skill Info` block with:
  ```
  ## Skill Info
  - **Name:** skill_id
  - **Agent:** AgentName (or "all")
  - **Tags:** tag1, tag2
  ```
- The full markdown content is **injected into the agent's system prompt** as instruction playbooks.
- Current skills:
  | File | Name | Agent | Tags |
  |------|------|-------|------|
  | `threat_intel.md` | threat_intel | ResearcherAgent | intelligence, analysis, cve |
  | `pentest_playbook.md` | pentest_playbook | HackerAgent | offensive, recon, exploitation |
  | `incident_response.md` | incident_response | all | dfir, incident, forensics, blue-team |
  | `code_review.md` | code_review | CoderAgent | code, security, audit, owasp |
  | `log_analysis.md` | log_analysis | CoderAgent | forensics, logs, analysis, blue-team |

### Python Skills (Executable Tools)
- Located in `src/skills/`.
- Subclasses of `BaseSkill` that expose callable tool functions.
- Automatically discovered and registered at agent initialization.
- Current skills:
  - **CryptoSkill** (`crypto.py`): hashing (MD5, SHA-1/256/512), hash identification, Base64 encode/decode, hex encode/decode. Available to all agents.
  - **OsintSkill** (`osint.py`): DNS lookup, reverse DNS, port checking, WHOIS lookup. Available to HackerAgent and ResearcherAgent only.

### SkillLoader
- **File:** `src/skills/loader.py`
- Unified loader for both MD and Python skills.
- `discover()`: scans `skills/` for `.md` files and `src/skills/` for `BaseSkill` subclasses.
- `get_md_skills_for(agent_name)`: returns compatible markdown skills.
- `get_all_tools(agent_name)`: returns all callable Python tool functions.
- `enable()` / `disable()`: toggle skills at runtime.
- `get_summary()`: returns a combined summary for CLI display.

### BaseAgent
- **File:** `src/agents/base.py`
- All agents inherit from `BaseAgent`.
- Automatically builds system prompts by combining the base prompt with compatible markdown skill instructions.
- When Gemini is active, uses **native function calling** — Python skill tools are registered as callable functions.
- When Ollama is active, falls back to a **chat-based ReAct loop** with tool descriptions embedded in the system prompt.
- Wraps all skill tools with the Genome Engine tracker to record execution time and success rate.

---

## 7. Installation & Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key (optional, for cloud LLM)
- Ollama (optional, for local LLM fallback)
- Git (for data source cloning)

### Step-by-Step

1. **Clone and set up virtual environment:**
   ```bash
   git clone https://github.com/RicheByte/cyberSamantha
   cd cyberSamantha
   python -m venv myenv
   ```

2. **Activate the environment:**
   ```bash
   # Windows
   myenv\Scripts\activate
   # Linux/Mac
   source myenv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API key** — create or edit `.env`:
   ```env
   GEMINI_API_KEY=your_api_key_here
   EXA_API_KEY=your_exa_api_key_here   # optional, for web search
   CYBERSAMANTHA_DROPBOX=C:/Path/To/Your/Dropbox  # optional
   LLM_PROVIDER=auto                   # auto | gemini | ollama
   OLLAMA_MODEL=llama3                 # optional
   OLLAMA_BASE_URL=http://localhost:11434  # optional
   ```

5. **Run the setup checker:**
   ```bash
   python setup_check.py
   ```
   This verifies your OS, Python version, `.env` configuration, data directory, and vector database status.

6. **Update data sources (optional but recommended):**
   ```bash
   python update_data.py --update
   ```

7. **Index documents into the vector store:**
   ```bash
   python main.py --index
   ```

8. **Start the interactive shell:**
   ```bash
   python main.py
   ```

---

## 8. CLI Commands & Usage

### Launch Modes

| Command | Description |
|---------|-------------|
| `python main.py` | Start interactive chat shell |
| `python main.py --index` | Index documents from `data/` into ChromaDB |
| `python main.py --index --force` | Force full reindex (ignore file hashes) |
| `python main.py --question "What is XSS?"` | Ask a single question and exit |
| `python main.py --daemon` | Start the background ingestion daemon on launch |

### Interactive Shell Commands

| Command | Description |
|---------|-------------|
| *(any text)* | Natural language query → AgentRouter processes it |
| `/wiki <topic>` | Query the RealityGraph for a wiki-style entity summary |
| `search <query>` | Web search via Exa API for threat intelligence |
| `run <command>` | Execute a safe terminal command (allowlist enforced) |
| `read <file_path>` | Read a local file into context |
| `think` | Re-process the last query and print the Chain-of-Thought |
| `remember that <fact>` | Store a permanent fact in Semantic Memory |
| `/status` | Full system health table (LLM, vector store, graph, memory, daemon, skills) |
| `/daemon start` | Start the background file ingestion watcher |
| `/daemon stop` | Stop the background watcher |
| `/daemon log` | Show recent auto-ingested files |
| `/provider` | Show active LLM provider and model |
| `/skills` | List all loaded skills (type, agent, tags, status) |
| `/skills enable <name>` | Enable a skill |
| `/skills disable <name>` | Disable a skill |
| `quit` / `exit` / `q` | Exit the shell |

### Quick-Launch Scripts

| Platform | Command |
|----------|---------|
| Linux/Mac | `./ask.sh "What is XSS?"` |
| PowerShell | `.\ask.ps1 "What is XSS?"` |
| CMD | `ask.bat "What is XSS?"` |
| With banner | `./ask.sh "What is XSS?" --banner` |

---

## 9. Data Sources & Update Pipeline

### Data Sources (`update_data.py`)

The system can clone and maintain **four cybersecurity data repositories** into the `data/` folder:

| Source | URL | Description | Default |
|--------|-----|-------------|---------|
| **Handbooks** | `github.com/0xsyr0/Awesome-Cybersecurity-Handbooks` | Curated cybersecurity handbooks (recon, exploitation, forensics, etc.) | ✅ Enabled |
| **Exploits** | `gitlab.com/exploit-database/exploitdb` | Exploit database | ❌ Disabled |
| **Advisories** | `github.com/github/advisory-database` | GitHub security advisories | ❌ Disabled |
| **NVD CVE** | `github.com/olbat/nvdcve` | National Vulnerability Database CVE feeds | ❌ Disabled |

Sources 2–4 are disabled by default because they are very large. Enable them in `config.yaml`.

### Update Features
- **Shallow cloning** (`--depth 1`) to minimize download size.
- **Detached HEAD recovery:** automatically detects and fixes detached HEAD states.
- **Retry logic:** up to 3 retries with exponential backoff for failed git operations.
- **Network connectivity check:** verifies access to GitHub/GitLab before starting.
- **Metadata tracking:** records last update time, file counts, and source URLs in `data/update_metadata.json`.

### Update Commands

| Command | Description |
|---------|-------------|
| `python update_data.py --update` | Update all enabled data sources |
| `python update_data.py --update --cleanup` | Update + clean up git histories |
| `python update_data.py --status` | Show update status and file counts |
| `python update_data.py --update --skip-network-check` | Skip network connectivity check |

---

## 10. Storage Cleanup & Optimization

**File:** `cleanup_storage.py`

Large git repositories (especially advisories and nvdcve) can consume significant disk space. This tool provides granular storage management:

| Command | Description |
|---------|-------------|
| `python cleanup_storage.py --status` | Show current storage usage per repo |
| `python cleanup_storage.py --temp` | Remove temporary git pack files (`tmp_pack_*`) |
| `python cleanup_storage.py --remove-git` | Remove `.git` folders from advisories, nvdcve, exploits |
| `python cleanup_storage.py --remove-backups` | Remove `.broken` backup folders |
| `python cleanup_storage.py --gc` | Run aggressive git garbage collection on all repos |
| `python cleanup_storage.py --all` | Full cleanup (temp + backups + git history) |
| `python cleanup_storage.py --all --keep-handbooks` | Full cleanup but preserve handbooks `.git` for future updates |

After cleanup, reindex with: `python main.py --index --force`

---

## 11. Directory Map

```
cyberSamantha/
├── main.py                    # Entry point — loads dotenv, starts CLIApp
├── config.yaml                # Central configuration (data sources, RAG settings, LLM provider, daemon)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (API keys, provider settings)
├── setup_check.py             # Cross-platform setup verification script
├── update_data.py             # Data source updater (git clone/pull for 4 repos)
├── cleanup_storage.py         # Git storage cleanup and optimization tool
├── test_ecosystem.py          # Integration tests for core components
├── ask.sh / ask.ps1 / ask.bat # Quick-launch scripts for single-question mode
│
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py        # Exports BaseAgent, HackerAgent, ResearcherAgent, CoderAgent
│   │   ├── base.py            # BaseAgent — shared logic, tool wrapping, Gemini/Ollama routing
│   │   ├── hacker.py          # HackerAgent — offensive security, nmap, curl
│   │   ├── researcher.py      # ResearcherAgent — web search, CVE lookup
│   │   ├── coder.py           # CoderAgent — file reading, code analysis, safe terminal
│   │   └── debate_orchestrator.py  # Cross-agent adversarial debate + synthesis
│   ├── cli/
│   │   ├── __init__.py
│   │   └── app.py             # CLIApp — Rich-based interactive REPL, command parser
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py           # AgentRouter — central manager, ReAct loop, query routing
│   │   ├── config.py          # ConfigManager — singleton YAML config loader
│   │   ├── llm_provider.py    # LLMProvider — Gemini ↔ Ollama hot-swap
│   │   ├── thought_router.py  # ThoughtRouter — cognitive strategy selection via Meta-Memory
│   │   └── curiosity_daemon.py # CuriosityDaemon — autonomous contradiction resolution
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── daemon.py          # IngestionDaemon — watchdog-based file watcher + auto-ingest
│   │   ├── parsers.py         # DocumentParser — PDF/DOCX/PPTX/JSON/YAML/text extraction + chunking
│   │   └── extractor.py       # GraphExtractor — LLM-based entity/relationship extraction
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── vector_store.py    # VectorStore — ChromaDB wrapper, indexing, semantic search
│   │   ├── reality_graph.py   # RealityGraph — probabilistic knowledge graph with confidence scores
│   │   └── graph_store.py     # GraphStore — basic NetworkX graph operations (legacy)
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── episodic.py        # EpisodicMemory — sliding window + LLM summarization
│   │   ├── semantic.py        # SemanticMemory — persistent JSON fact storage
│   │   └── meta_memory.py     # MetaMemory — strategy outcome tracking and retrieval
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── base.py            # BaseSkill — abstract interface for pluggable skills
│   │   ├── loader.py          # SkillLoader — discovers MD playbooks + Python skill modules
│   │   ├── genome_engine.py   # GenomeEngine — usage tracking, success rates, pruning
│   │   ├── crypto.py          # CryptoSkill — hashing, encoding, hash identification
│   │   └── osint.py           # OsintSkill — DNS, WHOIS, port checking, reverse DNS
│   └── tools/
│       ├── __init__.py        # Exports BaseTool, WebSearchTool, TerminalTool, FileReaderTool
│       ├── base.py            # BaseTool + ToolResult — abstract tool interface
│       ├── terminal.py        # TerminalTool — safe command execution (allowlist/blocklist)
│       ├── file_reader.py     # FileReaderTool — safe local file reading with extension whitelist
│       └── web_search.py      # WebSearchTool — Exa API web search
│
├── skills/                    # Markdown skill playbooks (injected into agent prompts)
│   ├── threat_intel.md        # Threat intelligence analysis framework
│   ├── pentest_playbook.md    # Penetration testing methodology
│   ├── incident_response.md   # NIST SP 800-61 incident response procedure
│   ├── code_review.md         # OWASP Top 10 secure code review checklist
│   ├── log_analysis.md        # Log forensics and IOC pattern detection
│   └── genome_registry.json   # Skill fitness tracking (usage, success rate, lineage)
│
├── data/                      # Data repositories and runtime storage
│   ├── handbooks/             # Cloned cybersecurity handbooks (git submodule)
│   ├── memory.json            # Semantic memory (user facts)
│   ├── meta_memory.json       # Meta-memory (strategy outcomes)
│   ├── reality_graph.json     # RealityGraph (persisted knowledge graph)
│   └── update_metadata.json   # Data source update tracking
│
├── chroma_db/                 # Local ChromaDB vector database
└── assets/                    # Images and media for documentation
```

---

## 12. Environment Variables & Configuration

### `.env` Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | *(empty)* | Google Gemini API key for cloud LLM |
| `EXA_API_KEY` | *(empty)* | Exa AI API key for web search |
| `CYBERSAMANTHA_DROPBOX` | `~/CyberSamantha/DropBox` | Path for the auto-ingestion drop folder |
| `LLM_PROVIDER` | `auto` | Force provider: `auto`, `gemini`, or `ollama` |
| `OLLAMA_MODEL` | `llama3` | Ollama model name for local mode |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |

### `config.yaml` Sections

| Section | Purpose |
|---------|---------|
| `data_sources` | Toggle individual data repos on/off, configure shallow clone depth and git history removal |
| `storage` | Auto-cleanup git packs, temp files, aggressive gc, max data folder size warning |
| `rag_system` | Embedding model (`all-MiniLM-L6-v2`), Gemini model (`gemini-2.0-flash`), context chunks (5), chunk size (1000), overlap (200) |
| `llm_provider` | Provider mode (`auto`/`gemini`/`ollama`), Ollama base URL and model |
| `daemon` | Watch directory, auto-start toggle, watched file extensions |
| `updates` | Retry count (3), git timeout (600s), network check toggle |

---

## 13. How a Query Flows Through the System

```
User types: "What are the latest vulnerabilities in Apache Log4j?"
                    │
                    ▼
          ┌───────────────────┐
          │    CLIApp         │  (src/cli/app.py)
          │  Captures input   │
          └────────┬──────────┘
                   │
                   ▼
          ┌───────────────────┐
          │   AgentRouter     │  (src/core/agent.py)
          │   .query()        │
          └────────┬──────────┘
                   │
        ┌──────────┼──────────────────────┐
        │          │                      │
        ▼          ▼                      ▼
  "search/     "read/               Other:
   run" cmd    "remember"            ▼
        │          │          ┌───────────────┐
        │          │          │ ThoughtRouter │
        ▼          ▼          │ (check        │
  Direct tool   Store fact    │  Meta-Memory) │
  execution     in Semantic   └───────┬───────┘
                                      │
                          ┌───────────┼───────────┐
                          ▼           ▼           ▼
                     "debate"     "linear"     fallback
                          │           │
              ┌───────────┴───┐       │
              │DebateOrchestr.│       ▼
              │Coder vs Hacker│  ┌──────────────┐
              │+ Synthesis    │  │ ReAct Loop    │
              └───────────────┘  │ (max 5 iters) │
                                 └───────┬───────┘
                                         │
                    ┌───────────┬────────┼────────┬──────────┐
                    ▼           ▼        ▼        ▼          ▼
               web_search   terminal  file_rag  wiki_query  agent delegation
                    │           │        │        │          │
                    ▼           ▼        ▼        ▼          ▼
               Exa API      Subprocess  ChromaDB  NetworkX   HackerAgent
                                              Graph          ResearcherAgent
                                                             CoderAgent
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │ LLM generates │
                                 │ final answer  │
                                 │ + sources     │
                                 └───────────────┘
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │  EpisodicMem  │  ← add to history
                                 │  (summarize   │
                                 │   if too long)│
                                 └───────────────┘
                                         │
                                         ▼
                                 Rendered via Rich
                                 Markdown in CLI
```

---

## 14. Extending the System

### Adding a New Markdown Skill

1. Create a `.md` file in the `skills/` folder:
   ```markdown
   # My New Skill

   ## Skill Info
   - **Name:** my_new_skill
   - **Agent:** HackerAgent
   - **Tags:** recon, network

   ## Instructions
   Your detailed playbook goes here...
   ```
2. Restart CyberSamantha — the skill is auto-discovered and injected into the specified agent's prompt.

### Adding a New Python Skill

1. Create a file in `src/skills/` that subclasses `BaseSkill`:
   ```python
   from typing import List, Callable
   from src.skills.base import BaseSkill

   class MySkill(BaseSkill):
       name = "my_skill"
       description = "Does something useful"
       version = "1.0"
       tags = ["category"]
       compatible_agents = set()  # empty = all agents

       def get_tools(self) -> List[Callable]:
           def my_tool(input: str) -> str:
               """Description of what this tool does."""
               return f"Result: {input}"
           return [my_tool]
   ```
2. Restart — the skill is auto-discovered, and its tools become available to compatible agents via Gemini native function calling or Ollama ReAct parsing.

### Adding a New Agent

1. Create a file in `src/agents/` that subclasses `BaseAgent`.
2. Implement `__init__` with a system prompt and `get_tools()` returning callable functions.
3. Register it in `AgentRouter.__init__` in `src/core/agent.py`.
4. Add it to the ReAct loop's action dispatch in `_handle_auto_query()`.

### Adding a New Data Source

1. Add a new entry to `repo_configs` in `update_data.py` with URL, type, target directory, and shallow clone settings.
2. Add a corresponding `update_<name>()` method that counts and reports files.
3. Add it to `config.yaml` under `data_sources` with `enabled` toggle.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `google-generativeai` | Google Gemini API client |
| `chromadb` | Local vector database |
| `sentence-transformers` | Local embedding model (`all-MiniLM-L6-v2`) |
| `networkx` | Knowledge graph operations |
| `PyPDF2` | PDF text extraction |
| `python-docx` | DOCX text extraction |
| `python-pptx` | PPTX text extraction |
| `watchdog` | File system monitoring for ingestion daemon |
| `exa-py` | Web search API (requires `EXA_API_KEY`) |
| `requests` | HTTP requests (Ollama, network checks) |
| `PyYAML` | YAML config parsing |
| `python-dotenv` | `.env` file loading |
| `tqdm` | Progress bars |
| `rich` | Terminal UI (panels, tables, markdown rendering) |
| `tenacity` | Retry logic |

---

## Testing

Run the integration test suite:
```bash
python test_ecosystem.py
```

This tests:
- **RealityGraph** — initialization, relationship addition, contradiction detection
- **MetaMemory** — strategy logging, retrieval of best strategy
- **ThoughtRouter** — routing decisions based on Meta-Memory
- **GenomeEngine** — skill usage recording

---

*CyberSamantha — Your Cyber Second Brain.*
