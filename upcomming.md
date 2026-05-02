# CyberSamantha — Upgrade Roadmap

## Completed Features ✅

### 1. ✅ Native Function Calling (Reliability)
The `BaseAgent` class uses **Gemini's Native Function Calling** when the Gemini API is available. Sub-agents (HackerAgent, ResearcherAgent, CoderAgent) register their tools as native callable functions, eliminating text-parsing errors.

### 2. ✅ Background Daemons & Auto-Ingestion (Autonomy)
A `watchdog`-based daemon (`src/ingest/daemon.py`) monitors `~/CyberSamantha/DropBox/` for new files. When a file is dropped in, it automatically:
- Parses (PDF, DOCX, PPTX, code, configs, etc.)
- Chunks and vectorizes into ChromaDB
- Extracts knowledge graph entities
- Notifies the CLI in real-time

**CLI Commands:** `/daemon start`, `/daemon stop`, `/daemon log`
**CLI Flag:** `--daemon` to auto-start on launch

### 3. ✅ Memory Summarization & Decay (Scalability)
`EpisodicMemory._summarize_and_decay()` automatically summarizes the oldest half of the conversation when the history grows too long, promoting key context to a persistent summary block. Works with both Gemini and Ollama backends.

### 4. ✅ Sandbox / Execution Safeguards (Security)
`TerminalTool` enforces `SAFE_COMMANDS` allowlist and `BLOCKED_COMMANDS` blocklist. Dangerous operations like `rm`, `del`, `shutdown` are blocked. Safe argument patterns are enforced for tools like `nmap`.

### 5. ✅ Local LLM Fallback (Privacy)
`LLMProvider` (`src/core/llm_provider.py`) provides transparent hot-swapping between:
- **Gemini** (cloud) — when `GEMINI_API_KEY` is set
- **Ollama** (local) — when Ollama is running locally

Set `LLM_PROVIDER=ollama` or `OLLAMA_MODEL=deepseek-coder` in your `.env` to force local mode.

### 6. ✅ Multi-Agent Swarm (Specialization)
The `AgentRouter` acts as a **Manager Agent** that delegates to specialist sub-agents:
- **HackerAgent** 🥷 — Offensive security, nmap scans, recon
- **ResearcherAgent** 🔬 — Web research, CVE lookups, threat intel
- **CoderAgent** 💻 — Code analysis, security review, file inspection
- **Manager (AgentRouter)** 🧠 — Routes queries to the correct sub-agent

## Architecture Summary

```
┌─────────────────────────────────────────────────┐
│  CLI (rich)                                     │
│  /status  /daemon  /wiki  /provider             │
├─────────────────────────────────────────────────┤
│  AgentRouter (Manager)                          │
│  ├── LLMProvider (Gemini ↔ Ollama)              │
│  ├── HackerAgent     → Terminal (nmap, curl)    │
│  ├── ResearcherAgent → WebSearch (Exa API)      │
│  ├── CoderAgent      → FileReader + Terminal    │
│  ├── RAG Pipeline    → VectorStore (ChromaDB)   │
│  └── Wiki Pipeline   → GraphStore (NetworkX)    │
├─────────────────────────────────────────────────┤
│  Memory Layer                                   │
│  ├── EpisodicMemory (summarize & decay)         │
│  └── SemanticMemory (persistent facts)          │
├─────────────────────────────────────────────────┤
│  Ingestion Daemon (watchdog)                    │
│  └── ~/CyberSamantha/DropBox/ → auto-ingest    │
└─────────────────────────────────────────────────┘
```

## Current Rating: 10/10 🎯
All planned upgrades have been implemented.
