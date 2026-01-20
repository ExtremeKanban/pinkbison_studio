--------------------------------
QUICK REFERENCE
--------------------------------

**Project**: Local agentic AI creative studio  
**Current State**: EventBus + AuditLog architecture, full persistence layer complete, single-project orchestrator  
**Stack**: Python 3.x, Streamlit, FAISS, PyTorch, local Qwen LLMs (vLLM + Transformers)  
**Environment**: Windows 11 + WSL Ubuntu, Nvidia GPU

**Immediate Focus**: Real-time workflow & feedback (WebSocket, non-blocking UI)  
**Next Phases**: Smoke test isolation → Autonomous revision → GitHub setup

I'm building a modular, agentic AI creative studio in Python with Streamlit and a background Orchestrator. I want you to understand exactly what I've already built, what my current architecture looks like, and what's still on the roadmap.

Please read this carefully and treat it as the ground truth for this project.

--------------------------------
CURRENT ARCHITECTURE (WHAT EXISTS TODAY)
--------------------------------

--------------------------------
CURRENT FILE STRUCTURE
--------------------------------

```
project_root/
├── core/                          # Infrastructure components
│   ├── event_bus.py              # Ephemeral message passing
│   ├── audit_log.py              # Persistent event log
│   ├── project_state.py          # Unified state management
│   ├── agent_factory.py          # Stateless agent creation
│   ├── output_manager.py         # Chapter/draft file management
│   └── registry.py               # Project-scoped resource manager
├── agents/
│   ├── base_agent.py             # Base class for all agents
│   ├── plot_architect.py
│   ├── worldbuilder.py
│   ├── character_agent.py
│   ├── scene_generator.py
│   ├── continuity_agent.py
│   ├── editor_agent.py
│   ├── producer.py               # Does NOT inherit from AgentBase
│   ├── creative_director.py
│   └── memory_extractor.py
├── models/
│   ├── model_client.py           # Unified model client with retry
│   ├── fast_model_client.py     # vLLM client (Qwen2.5-3B)
│   └── heavy_model.py            # Transformers (Qwen2.5-7B)
├── ui/
│   ├── character_ui.py
│   ├── general_playground.py
│   ├── intelligence_panel.py     # EventBus + AuditLog viewer
│   ├── memory_add_ui.py
│   ├── memory_browser_ui.py
│   ├── memory_search_ui.py
│   ├── plot_architect_ui.py
│   ├── producer_agent_ui.py
│   ├── scene_pipeline_ui.py
│   ├── sidebar.py
│   ├── story_bible_ui.py
│   ├── worldbuilder_ui.py
│   ├── pipeline_history_ui.py    # View past pipeline results
│   ├── canon_rules_ui.py         # View/manage canon rules
│   └── continuity_notes_ui.py    # View continuity check history
├── project_manager/
│   ├── loader.py                 # Project loading/saving
│   ├── registry.py               # Project registry
│   └── state.py                  # Session state management
├── project_state/                # Per-project persistent data
│   └── <project_name>/
│       ├── state.json            # Unified project state
│       ├── graph.json            # Knowledge graph
│       ├── audit.jsonl           # Audit log
│       ├── tasks.json            # Task queue
│       ├── memory/
│       │   ├── index.faiss       # FAISS index
│       │   ├── texts.json        # Memory texts
│       │   └── embeddings.npy    # Embeddings
│       └── outputs/
│           ├── chapters/
│           │   ├── chapter_000.json
│           │   └── ...
│           ├── scenes/
│           └── drafts/
│               └── full_story_TIMESTAMP.txt
├── audit_logs/                   # Centralized audit logs
│   └── <project_name>_audit.jsonl
├── tests/
│   ├── smoke_test.py             # End-to-end test (needs isolation)
│   ├── migrations/               # Migration verification tests
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── docs/
│   ├── standards/                # Code standards & guidelines
│   └── migrations/               # Migration guides
├── Root files:
│   ├── orchestrator.py           # Single-project, blocking run_forever()
│   ├── task_manager.py
│   ├── memory_store.py           # ✓ PERSISTENT (FAISS + JSON)
│   ├── graph_store.py            # ✓ PERSISTENT (JSON)
│   ├── agent_bus.py
│   ├── run_orchestrator.py
│   └── studio_ui.py              # Main Streamlit entry point
```

**Key characteristics**:
- All project data in `project_state/<project>/` directory
- EventBus for ephemeral real-time coordination
- AuditLog for persistent event history
- ProjectState for unified state management
- OutputManager for chapter/draft file persistence
- Registry pattern for project-scoped resources
- Agents are stateless, created per-task via AgentFactory

--------------------------------
CORE COMPONENTS
--------------------------------

1. Core agents and orchestration

I have implemented the following agents:

- PlotArchitect
- Worldbuilder
- CharacterAgent
- SceneGenerator
- ContinuityAgent
- EditorAgent
- ProducerAgent
- CreativeDirectorAgent

All of these agents except ProducerAgent inherit from a shared AgentBase class. Each agent takes at least:

- name
- project_name
- event_bus (EventBus instance)
- audit_log (AuditLog instance)
- fast_model_url
- model_mode

The ProducerAgent orchestrates multi-step creative pipelines such as:

- Story bible generation (outline + world + characters)
- Chapter generation
- Full story workflows
- Director mode (autonomous multi-pass revision)

It runs agents sequentially and uses EventBus to pass messages and coordinate work.

I also have a CreativeDirectorAgent that analyzes critiques and turns them into canon rules and guidance, which are logged into the graph and memory.

2. Orchestrator

I have a ProjectOrchestrator 

- One orchestrator process
- Many projects
- No need to spawn/kill orchestrators per project
- Clean isolation between projects

3. EventBus (ephemeral coordination)

I have an EventBus class that is instantiated per project:

- It takes `project_name` in its constructor
- It maintains an in-memory ring buffer (last 100 events)
- It supports:
  - `publish(sender, recipient, event_type, payload)` - publish an event
  - `subscribe(agent_name, callback)` - subscribe to events
  - `get_recent(agent_name, limit)` - get recent events for an agent
- Events are for real-time coordination only

Important:  
The EventBus is:

- Project-specific in memory (one per orchestrator instance)
- NOT persisted to disk (ephemeral by design)
- Recreated fresh each time the orchestrator starts
- Events are lightweight and temporary

4. AuditLog (persistent event history)

I have an AuditLog class that provides persistent event logging:

- Append-only JSONL format
- Located at `audit_logs/<project_name>_audit.jsonl`
- Supports:
  - `append(event_type, sender, recipient, payload)` - log an event
  - `search(event_type, limit)` - search logged events
  - `get_recent(limit)` - get recent events

Important:
- AuditLog is the permanent record of all agent actions
- EventBus is for real-time coordination only
- Agents should log important actions to both (via AgentBase.send_message())

5. MemoryStore (persistent)

I have a MemoryStore class that is fully persistent per project:

- Uses FAISS for vector similarity search
- Stores memories in `project_state/<project>/memory/`
- Files:
  - `index.faiss` - FAISS index
  - `texts.json` - Memory texts
  - `embeddings.npy` - Embeddings
- Supports:
  - `add(text)` - add a memory
  - `search(query, k)` - semantic search
  - `clear()` - clear all memories

6. GraphStore (persistent)

I have a GraphStore class that is fully persistent per project:

- Stores knowledge graph in `project_state/<project>/graph.json`
- Tracks:
  - Entities (characters, locations, factions, items)
  - Relationships between entities
  - Events in the story world
  - Canon rules derived from critiques
- Supports:
  - `add_entity()`, `add_relationship()`, `add_event()`
  - `get_canon_rules()` - retrieve canon rules
  - `update()` - update the graph

7. ProjectState (unified state management)

I have a ProjectState class that manages all project state:

- Located at `project_state/<project>/state.json`
- Contains:
  - Project metadata (genre, tone, themes, setting)
  - Agent outputs (outline, world, characters)
  - Pipeline results history
  - Continuity notes
  - UI input fields
- Supports:
  - `save()` - save to disk
  - `load(project_name)` - load from disk
  - `add_pipeline_result()` - add pipeline result to history
  - `add_continuity_note()` - add continuity note
- Auto-migration from old `projects/*.json` format

8. OutputManager (chapter/draft persistence)

I have an OutputManager class that manages output files:

- Located at `project_state/<project>/outputs/`
- Directories:
  - `chapters/` - chapter JSON files
  - `scenes/` - scene text files
  - `drafts/` - full story drafts
- Supports:
  - `save_chapter(index, data)` - save chapter
  - `save_draft(name, content)` - save draft
  - `load_chapter(index)` - load chapter
  - `list_chapters()` - list all chapters

9. AgentFactory (stateless agent creation)

I have an AgentFactory class that creates fresh agent instances:

- Agents are created per-task, not stored
- Factory methods:
  - `create_plot_architect()`
  - `create_worldbuilder()`
  - `create_character_agent()`
  - `create_scene_generator()`
  - `create_continuity_agent()`
  - `create_editor_agent()`
- All agents get the same EventBus, AuditLog, and model URLs

10. Registry (project-scoped resources)

I have a Registry class that manages project-scoped infrastructure:

- Singleton pattern: `from core.registry import REGISTRY`
- Provides:
  - `get_event_bus(project_name)` - get/create EventBus
  - `get_audit_log(project_name)` - get/create AuditLog
  - `get_memory_store(project_name)` - get/create MemoryStore
  - `get_graph_store(project_name)` - get/create GraphStore
  - `get_task_manager(project_name)` - get/create TaskManager
  - `get_output_manager(project_name)` - get/create OutputManager
- Ensures one instance per project
- Supports `clear_project()` for cleanup

11. LLM setup

My current LLM setup is:

- **Fast model (via vLLM, running in WSL Ubuntu):**
  - Model: `Qwen/Qwen2.5-3B-Instruct`
  - Served as an OpenAI-compatible endpoint at:
    - `http://localhost:8000/v1/chat/completions`
  - Used via `model_client.py` with automatic retry logic

- **Heavy model (via Transformers, running in Windows environment):**
  - Model: `Qwen/Qwen2.5-7B-Instruct`
  - Loaded in `heavy_model.py` using:
    - `AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")`
    - `AutoModelForCausalLM.from_pretrained(..., torch_dtype=torch.float16, device_map="auto")`
  - Used for higher-quality creative generation

- **Embeddings server (for MemoryStore):**
  - Endpoint: `http://localhost:8001/v1/embeddings`
  - Model: `"BAAI/bge-small-en-v1.5"`
  - Runs in WSL Ubuntu

All models are running locally on my GPU.

12. My current terminal/tab workflow

On Windows, I typically have four terminal tabs:

- **Tab 1:** vLLM server (in WSL Ubuntu) running Qwen2.5-3B-Instruct at `http://localhost:8000/v1/chat/completions`
- **Tab 2:** Embeddings server (in WSL Ubuntu) running the BAAI/bge-small-en-v1.5 model at `http://localhost:8001/v1/embeddings`
- **Tab 3:** Streamlit UI running the creative studio interface
- **Tab 4:** Orchestrator process running `ProjectOrchestrator.run_forever()` for a single project (optional, not needed for UI-driven workflows)

13. Installed dependencies (high-level summary)

In my Windows "multimodal-assistant" environment, I have installed (among many others):

- transformers
- streamlit
- faiss-cpu
- torch
- filelock
- pdfplumber
- openpyxl
- requests
- rich

In WSL Ubuntu, I have a separate environment primarily for vLLM and its dependencies.

You don't need to reason about every package individually, but you should assume I have a full modern Python AI stack available.

14. Smoke test

I currently have a smoke test, but:

- It uses the default project
- It does NOT create and destroy its own project
- It does NOT isolate its state from my real project
- It does NOT validate persistence yet

This is something I want to fix as part of the roadmap.

--------------------------------
HARDWARE & ENVIRONMENT SPECS
--------------------------------

**Hardware**:
- CPU: Intel Core Ultra 7 265F, 20-core, 20-thread
- GPU: NVIDIA GeForce RTX 5080, 16GB VRAM
- RAM: 32 GB DDR5
- Storage: 1.8 TB NVMe SSD (primary)

**Software Environment**:
- OS: Windows 11 Pro (Build 26200)
- WSL: Ubuntu 24.04.3 LTS
- Python (Windows): 3.10.19 (multimodal-assistant conda environment)
- Python (WSL): 3.10.19 (qwen-server conda environment)
- CUDA Toolkit: 12.8 (Windows), Driver 591.44
- PyTorch: 2.7.0+cu128 (CUDA enabled)

**Key Python Packages** (multimodal-assistant environment):
- Streamlit: 1.52.1
- Transformers: 4.57.3
- FAISS: 1.13.2
- vLLM: 0.13.0 (WSL qwen-server environment)

**Terminal Workflow** (4 tabs):
1. WSL: vLLM server (Qwen2.5-3B-Instruct) → `localhost:8000`
2. WSL: Embeddings server (bge-small-en-v1.5) → `localhost:8001`
3. Windows: Streamlit UI → `localhost:8501`
4. Windows: Orchestrator process (blocking `run_forever()`) → optional

--------------------------------
ROADMAP 
--------------------------------

Real-Time Workflow and Feedback (NOT STARTED)
==============================================

I want to move from "batch pipeline" behavior to **real-time, interactive workflows**, including:

- Background execution of pipelines so the UI stays responsive
- Live updates in the Intelligence Panel as agents run
- The ability to inject human feedback into the EventBus during a run
- Agents that check for new feedback/messages between steps
- The ability to pause, resume, or step through pipelines

**Key features:**
- Non-blocking pipeline execution
- Real-time progress updates
- Mid-pipeline feedback injection
- Pause/resume/step controls
- Agent-aware of new feedback between tasks

Smoke Test Isolation and Validation (NOT STARTED)
==================================================

I want to upgrade the smoke test so that it:

- Creates a temporary project (e.g., `test_project_<uuid>`)
- Runs the full pipeline inside that project
- Validates that:
  - Memory is written
  - Graph is updated
  - Persistence files exist
  - EventBus messages are logged to AuditLog
  - Pipeline results are saved to ProjectState
  - Chapter files are created in outputs/
- Deletes the project folder afterward

This will keep my real projects clean and give me confidence that the system works end-to-end.

Higher-Level Autonomy and Canon Enforcement (PARTIAL)
=======================================================

**What exists:**
- CreativeDirectorAgent can analyze critiques
- Canon rules stored in GraphStore
- Canon rules UI panel for viewing

**What's missing:**
- Autonomous revision loops where agents critique and revise scenes/chapters
- CreativeDirectorAgent actively enforcing canon during generation
- Multi-chapter and multi-book orchestration
- Richer knowledge graph tracking entities, relationships, events over time
- Persistent story universe management with strong continuity

**Goals:**
- Agents that autonomously revise based on canon violations
- Director mode that runs multiple revision passes automatically
- Canon rules that actively guide generation, not just stored
- Multi-book series management with cross-book continuity

GitHub Setup and Documentation (NOT STARTED)
=============================================

Create clear and detailed setup instructions so anyone can use this code and set up a completely new environment of their own.

**Requirements:**
- Start from clean Windows 11 install with Nvidia GPU
- Complete step-by-step setup guide
- All dependencies and configuration clearly documented
- Hardware requirements specified
- Model download and setup instructions
- Troubleshooting guide

**Hardware documentation:**
- CPU: Intel Core Ultra 7 265F (20-core)
- GPU: NVIDIA GeForce RTX 5080 (16GB VRAM)
- RAM: 32 GB DDR5
- Storage: 1.8 TB NVMe SSD

**Software stack:**
- Windows 11 + WSL Ubuntu
- CUDA 12.8
- Python 3.10 (conda)
- vLLM server setup
- Embeddings server setup
- Streamlit configuration

--------------------------------
PROJECT VISION
--------------------------------

My ultimate goal is to build a **studio-grade, autonomous creative engine** that:

- Uses multiple specialized agents to generate, critique, and refine stories
- Maintains a persistent universe (characters, locations, factions, events, canon)
- Supports multi-book series and long-form narrative continuity
- Allows real-time human steering via feedback injected into the EventBus
- Feels less like "running a script" and more like operating a creative IDE or cockpit

I care about:

- Modularity
- Persistence
- Multi-project support
- Real-time interaction
- Canon enforcement
- Long-term scalability

--------------------------------
WHAT I WANT FROM YOU
--------------------------------

**Ground Rules**:
1. Treat this document as the authoritative snapshot of my current system
2. Always distinguish between: what exists | what we're designing | what's future work
3. Provide concrete, file-level changes with clear migration steps
4. Don't break existing workflows
5. Follow established code standards in `docs/standards/CODE_STANDARDS.md`
6. Follow all standards in docs/standards/*
7. Offer change suggestions to standards if they are incorrect, contradictory, or no longer serve the project

**Architecture Patterns to Follow**:
- Agents are stateless, created via AgentFactory
- Use EventBus for ephemeral coordination
- Use AuditLog for persistent event history
- Use ProjectState for state management
- Use Registry for project-scoped resources
- All persistence goes through appropriate managers

**Never Do**:
- Don't reference IntelligenceBus (it's been removed)
- Don't create agent instances directly (use AgentFactory)
- Don't write to `projects/*.json` (use ProjectState)
- Don't break backward compatibility without migration guide