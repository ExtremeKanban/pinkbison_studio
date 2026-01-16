--------------------------------
QUICK REFERENCE
--------------------------------

**Project**: Local agentic AI creative studio
**Current State**: Single-project orchestrator, partial persistence (memory/graph only)
**Stack**: Python 3.x, Streamlit, FAISS, PyTorch, local Qwen LLMs (vLLM + Transformers)
**Environment**: Windows 11 + WSL Ubuntu, Nvidia GPU

**Immediate Focus**: Phase 0 - Architecture Review
**Next Phases**: 1. Full persistence → 2. Multi-project orchestrator → 3. Real-time feedback

**Current Pain Points** (priority order):
1. Must manually start/stop orchestrator per project
2. Agent outputs not persisted (lost on restart)
3. IntelligenceBus messages not persisted
4. Cannot give feedback during pipeline execution
5. Project switching is fragile
6. No isolation in smoke tests

I'm building a modular, agentic AI creative studio in Python with Streamlit and a background Orchestrator. I want you to understand exactly what I've already built, what my current architecture looks like, and what's still on the roadmap—starting with a multi-project orchestrator and full persistence.

Please read this carefully and treat it as the ground truth for this project.

--------------------------------
CURRENT ARCHITECTURE (WHAT EXISTS TODAY)
--------------------------------

--------------------------------
CURRENT FILE STRUCTURE
--------------------------------

```
project_root/
├── agents/
│   ├── base_agent.py              # Base class for all agents
│   ├── plot_architect.py
│   ├── worldbuilder.py
│   ├── character_agent.py
│   ├── scene_generator.py
│   ├── continuity_agent.py
│   ├── editor_agent.py
│   ├── producer.py                # Does NOT inherit from AgentBase
│   ├── creative_director.py
│   └── memory_extractor.py
├── models/
│   ├── fast_model_client.py       # vLLM client (Qwen2.5-3B)
│   └── heavy_model.py             # Transformers (Qwen2.5-7B)
├── ui/
│   ├── character_ui.py
│   ├── general_playground.py
│   ├── intelligence_panel.py      # Read-only agent message viewer
│   ├── memory_add_ui.py
│   ├── memory_browser_ui.py
│   ├── memory_search_ui.py
│   ├── plot_architect_ui.py
│   ├── producer_agent_ui.py
│   ├── scene_pipeline_ui.py
│   ├── sidebar.py
│   ├── story_bible_ui.py
│   └── worldbuilder_ui.py
├── project_manager/
│   ├── loader.py
│   ├── registry.py
│   └── state.py
├── tests/
│   ├── smoke_test.py              # Uses default project, no isolation yet
│   ├── utils.py
│   └── test_data/
│       └── sample_inputs.json
├── graphs/
│   └── default_project_graph.json # Per-project graph storage
├── projects/
│   ├── default_project.json
│   ├── test_project.json
│   └── test_project2.json
├── tasks/
│   └── default_project_tasks.json
├── Root files:
│   ├── orchestrator.py            # Single-project, blocking run_forever()
│   ├── intelligence_bus.py        # In-memory, per-project, NOT persistent
│   ├── task_manager.py
│   ├── memory_store.py            # ✓ PERSISTENT (FAISS + JSON)
│   ├── graph_store.py             # ✓ PERSISTENT (JSON)
│   ├── agent_bus.py
│   ├── run_orchestrator.py
│   └── studio_ui.py               # Main Streamlit entry point
└── Memory files (per project):
    ├── default_project_memory.index
    ├── default_project_memory_texts.json
    └── default_project_embeddings.npy
```

**Key observations**:
- Only memory files and `graphs/` directory persist data
- No `project_state/`, `outputs/`, or `bus_history/` directories yet
- Orchestrator and IntelligenceBus have no persistence mechanism
- UI fields, agent outputs, and tasks vanish on restart
- `project_manager/` directory exists but integration unclear

--------------------------------
CORE COMPONENTS
--------------------------------

1. Core agents and orchestration

I have implemented the following agents:

- PlotArchitectAgent
- WorldbuilderAgent
- CharacterAgent
- SceneGeneratorAgent
- ContinuityAgent
- EditorAgent
- ProducerAgent
- CreativeDirectorAgent

All of these agents except ProducerAgent inherit from a shared AgentBase class. Each agent takes at least:

- project_name
- intelligence_bus
- fast_model_url
- model_mode

The ProducerAgent orchestrates multi-step creative pipelines such as:

- Story bible generation
- Scene generation
- Full story workflows

It runs agents sequentially and uses an IntelligenceBus to pass structured messages and critiques around.

I also have a CreativeDirectorAgent that analyzes critiques and turns them into canon rules and guidance, which are logged into the graph and memory.

2. Orchestrator

I have a ProjectOrchestrator class that is designed for a single project at a time. It:

- Is initialized with a project_name and poll_interval
- Creates its own IntelligenceBus instance for that project:
  - `self.intelligence_bus = IntelligenceBus(project_name)`
- Creates:
  - ProducerAgent
  - CreativeDirectorAgent
  - TaskManager
  - GraphStore
  - MemoryStore
- Runs a blocking loop via `run_forever()` that:
  - Ingests continuity messages into tasks
  - Executes tasks (e.g., SCENE_REVISION, SCENE_CRITIQUE_ANALYSIS)
  - Uses CreativeDirectorAgent to derive canon rules and guidance from critiques
  - Logs canon rules into GraphStore and memory
  - Updates task statuses

Important:  
Right now, the orchestrator:

- Handles only one project at a time
- Must be started manually from the command line
- Creates a fresh IntelligenceBus each time it starts
- Does not support multiple projects simultaneously
- Does not persist its bus, tasks, or messages

3. IntelligenceBus

I have an IntelligenceBus class that is instantiated per project by the orchestrator:

- It takes `project_name` in its constructor
- It maintains in-memory structures:
  - `messages` (chronological log)
  - `agent_feedback`
  - `continuity_notes`
  - `canon_rules`
  - `task_queue`
  - `memory_events`
  - `agent_messages`
- It assigns incremental message IDs
- It supports:
  - `add_agent_message(sender, recipient, msg_type, payload)`
  - `get_messages_for(agent_name, since_id=None)`
  - `log(entry_type, content, agent=None)`
  - `add_feedback(agent_name, text)`

Important:  
The IntelligenceBus is:

- Project-specific in memory (one per orchestrator instance)
- Not persisted to disk
- Not shared across processes
- Recreated fresh each time the orchestrator starts

4. MemoryStore (persistent)

I have a MemoryStore class that is fully persistent per project. It:

- Uses FAISS for vector search
- Stores:
  - `<project_name>_memory.index` (FAISS index)
  - `<project_name>_memory_texts.json` (raw text entries)
  - `<project_name>_embeddings.npy` (embeddings)
- Uses an embeddings server at:
  - `http://localhost:8001/v1/embeddings`
  - Model: `"BAAI/bge-small-en-v1.5"`
- Supports:
  - `add(text)` → embeds, appends, updates FAISS, saves
  - `search(query, k=5)` → vector search with deduplication
  - `get_all()` → returns all memory entries
  - `delete(idx)` → deletes and rebuilds index
  - `clear()` → clears everything
  - `save()` → writes index, texts, embeddings to disk

So: **memory is persistent per project.**

5. GraphStore (persistent)

I have a GraphStore class that is also fully persistent per project. It:

- Stores its data in:
  - `graphs/<project_name>_graph.json`
- Initializes an empty graph if the file doesn't exist
- Maintains:
  - `entities` (character, location, faction, artifact, concept)
  - `relationships`
  - `events`
  - `canon_rules`
- Supports:
  - `add_entity(...)`
  - `get_entity(...)`
  - `get_entities_by_type(...)`
  - `add_relationship(...)`
  - `get_relationships_for(entity_id)`
  - `add_event(...)`
  - `get_events()`
  - `add_canon_rule(...)`
  - `get_canon_rules()`
  - `get_raw_graph()`
  - `replace_graph(new_graph)`
  - Flattened getters for UI

So: **the graph is persistent per project.**

6. What is NOT persistent today

Right now, the following are **not** persisted:

- IntelligenceBus messages
- Task queue
- Agent outputs (story bible, scenes, drafts, etc.)
- Producer pipeline results
- UI fields (seed idea, genre, tone, themes, etc.)
- Continuity notes (except where manually written into memory/graph)
- Any "project_state.json" or similar

Only MemoryStore and GraphStore are persistent.

7. Streamlit UI

I have a Streamlit UI that includes:

- Panels for each major agent
- A Producer panel to run pipelines
- An Intelligence Panel that displays internal agent messages (read-only)
- A project selector (but project switching is limited because the orchestrator is single-project and manually started)

Important:  
Right now:

- The UI does not start or manage the orchestrator process
- The UI does not support real-time updates during long pipelines
- The UI only shows results after the pipeline completes
- Feedback is effectively "batch" – I can give feedback after a run, not during

8. LLM setup

My current LLM setup is:

- **Fast model (via vLLM, running in WSL Ubuntu):**
  - Model: `Qwen/Qwen2.5-3B-Instruct`
  - Served as an OpenAI-compatible endpoint at:
    - `http://localhost:8000/v1/chat/completions`
  - Used via `fast_model_client.py` with:
    - `FAST_MODEL_URL = "http://localhost:8000/v1/chat/completions"`
    - `FAST_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"`

- **Heavy model (via Transformers, running in Windows environment):**
  - Model: `Qwen/Qwen2.5-7B-Instruct`
  - Loaded in `heavy_model.py` using:
    - `AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")`
    - `AutoModelForCausalLM.from_pretrained(..., torch_dtype=torch.float16, device_map="auto")`
  - Used for higher-quality creative generation via:
    - `generate_with_heavy_model(prompt: str, max_new_tokens: int = 300)`

- **Embeddings server (for MemoryStore):**
  - Endpoint: `http://localhost:8001/v1/embeddings`
  - Model: `"BAAI/bge-small-en-v1.5"`
  - This embeddings server runs inside WSL Ubuntu, just like the vLLM fast model server.


All models are running locally on my GPU.

9. My current terminal/tab workflow

On Windows, I typically have four terminal tabs:

- **Tab 1:** vLLM server (in WSL Ubuntu) running Qwen2.5-3B-Instruct at `http://localhost:8000/v1/chat/completions`
- **Tab 2:** Embeddings server (in WSL Ubuntu) running the BAAI/bge-small-en-v1.5 model at `http://localhost:8001/v1/embeddings`
- **Tab 3:** Streamlit UI running the creative studio interface
- **Tab 4:** Orchestrator process running `ProjectOrchestrator.run_forever()` for a single project

10. Installed dependencies (high-level summary)

In my Windows "multimodal-assistant" environment, I have installed (among many others):

- transformers
- streamlit
- faiss-cpu
- torch
- uv
- pdfplumber
- openpyxl
- instructor
- jsonref
- chromadb
- embedchain
- langchain
- langgraph
- semantic-kernel
- fastapi
- uvicorn
- tiktoken
- huggingface-hub
- requests
- rich

In WSL Ubuntu, I have a separate environment primarily for vLLM and its dependencies.

You don't need to reason about every package individually, but you should assume I have a full modern Python AI stack available.

11. Smoke test

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
4. Windows: Orchestrator process (blocking `run_forever()`)

--------------------------------
ROADMAP (WHAT I WANT TO BUILD NEXT)
--------------------------------

Now that you understand what exists today, here is the roadmap, in order.

0. Review Architecture

I want to do a sanity check of the current system architecture

- Looking forward on the roadmap and seeing where changes will occur, I want to re-evaluate the code architecture

Goals:

- Make changes related to stability and maintainability
- Create best practices and code guidelines that will keep AI generated code maintaining style, consistency, and quality  

1. Full persistence layer

I want to add a proper persistence layer so that **everything** important is saved per project, including:

- Agent outputs (story bible, scenes, drafts, etc.)
- Producer pipeline results
- UI fields (seed idea, genre, tone, themes, notes, etc.)
- IntelligenceBus messages (full conversation history)
- Task queue state
- Continuity notes
- Canon rules (beyond what's already in GraphStore)
- A project-level "project_state.json" or similar

Goals:

- Auto-save on every meaningful change (no manual "Save" button)
- Auto-load when a project is opened
- Project reset (clear or delete a project cleanly)
- Project switching without corrupting state

2. Multi-project orchestrator (single process, many projects)

Right now, the orchestrator is single-project. I want to evolve it into a **single multi-project orchestrator** that:

- Maintains a registry of all active projects
- Maintains a separate IntelligenceBus per project
- Maintains a separate agent set per project
- Maintains a separate task queue per project
- Polls all projects in a unified event loop
- Routes tasks and messages based on project_name
- Integrates cleanly with the persistence layer

The goal is:

- One orchestrator process
- Many projects
- No need to spawn/kill orchestrators per project
- Clean isolation between projects
- Perfect fit for a real creative IDE

3. Real-time workflow and feedback

I want to move from "batch pipeline" behavior to **real-time, interactive workflows**, including:

- Background execution of pipelines so the UI stays responsive
- Live updates in the Intelligence Panel as agents run
- The ability to inject human feedback into the IntelligenceBus during a run
- Agents that check for new feedback/messages between steps
- The ability to pause, resume, or step through pipelines

4. Smoke test isolation and validation

I want to upgrade the smoke test so that it:

- Creates a temporary project (e.g., `test_project_<uuid>`)
- Runs the full pipeline inside that project
- Validates that:
  - Memory is written
  - Graph is updated
  - Persistence files exist
  - Bus messages are logged (once persistence is added)
- Deletes the project folder afterward

This will keep my real projects clean and give me confidence that the system works end-to-end.

5. Higher-level autonomy and canon enforcement

Longer-term, I want:

- Autonomous revision loops where agents critique and revise scenes/chapters
- The CreativeDirectorAgent to enforce canon and style across the project
- Multi-chapter and multi-book orchestration
- A richer knowledge graph that tracks entities, relationships, events, and canon rules over time
- A system that can manage a persistent story universe with strong continuity

6. Exact setup instructions for GitHub readme
- create clear and detailed instructions so anyone can use this code and setup a completely new environment of their own
- include all instructions need to start with a clean install of Windows 11 running a dedicated Nvidia GPU
- List out exactly what I am running on this current system that is relevant to the setup (CPU, GPU, Memory, Disk, etc.)

--------------------------------
PROJECT VISION
--------------------------------

My ultimate goal is to build a **studio-grade, autonomous creative engine** that:

- Uses multiple specialized agents to generate, critique, and refine stories
- Maintains a persistent universe (characters, locations, factions, events, canon)
- Supports multi-book series and long-form narrative continuity
- Allows real-time human steering via feedback injected into the IntelligenceBus
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

**Your First Task: Phase 0 - Architecture Review**

Before we add any new features, I need you to analyze the current architecture and provide:

**Part 1: Critical Analysis** (respond to this first)
Analyze these specific concerns:

1. **IntelligenceBus Design**
   - Is in-memory message passing optimal for multi-project orchestration?
   - Should messages be treated as ephemeral events vs. persistent logs?
   - How should bus instances be managed in a multi-project context?

2. **Agent Lifecycle Management**
   - Should agents be singletons per project or created per-task?
   - What are the implications for memory usage with 10+ active projects?
   - How should agent state be handled across task executions?

3. **Persistence Strategy**
   - Given MemoryStore and GraphStore already persist, what's the pattern?
   - Should we use JSON, SQLite, or another format for ProjectState?
   - How do we handle concurrent writes in a multi-project orchestrator?
   - What's the migration path that preserves existing memory/graph data?

4. **Orchestrator Architecture**
   - Is the blocking `run_forever()` loop appropriate for multi-project?
   - Should we move to async/await or threading?
   - How do we prevent one project's slow task from blocking others?

**Part 2: Code Guidelines & Standards** (provide after Part 1)
Establish project-wide standards for:
- Error handling patterns
- Logging conventions (what level, what format)
- Type hints policy (strict or gradual)
- Docstring style (Google, NumPy, or reStructuredText)
- Configuration management approach
- Testing requirements for new code

**Part 3: Refactoring Recommendations** (provide after Part 2)
Based on the analysis, provide:
- Specific files that need refactoring before adding new features
- Technical debt that will bite us during multi-project implementation
- Quick wins that improve stability now

**Deliverable Format**:
Provide a design recommendations document with:
- Clear architectural decisions with rationale
- Specific refactoring steps (file-by-file)
- Risk assessment for each recommendation
- Estimated complexity (simple/moderate/complex)

**After Phase 0 is complete**, we'll move to:
- Phase 1: Implementing full persistence layer
- Phase 2: Multi-project orchestrator refactor
- Phase 3: Real-time workflow and feedback

**Break your response into these three parts. Start with Part 1 only.**