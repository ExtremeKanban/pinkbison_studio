--------------------------------
QUICK REFERENCE
--------------------------------

**Project**: Local agentic AI creative studio  
**Current State**: EventBus + AuditLog architecture, full persistence layer complete, single-project orchestrator  
**Stack**: Python 3.x, Streamlit, FAISS, PyTorch, local Qwen LLMs (vLLM + Transformers)  
**Environment**: Windows 11 + WSL Ubuntu, Nvidia GPU

**Immediate Focus**: Review REAL-TIME WORKFLOW & FEEDBACK implementation & create comprehensive test suite  
**Next Phases**: Remove legacy blocking code → Cleanup test files → test suite → Autonomous revision → GitHub setup

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
├── config/                        # Centralized configuration
│   ├── __init__.py
│   └── settings.py               # MODEL_CONFIG, STORAGE_CONFIG
├── core/                          # Infrastructure components
│   ├── __init__.py
│   ├── event_bus.py              # Ephemeral message passing
│   ├── audit_log.py              # Persistent event log
│   ├── project_state.py          # Unified state management
│   ├── agent_factory.py          # Stateless agent creation
│   ├── output_manager.py         # Chapter/draft file management
│   ├── registry.py               # Project-scoped resource manager
│   └── storage_paths.py          # Centralized path management
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
│   ├── __init__.py
│   ├── common.py                 # Shared UI utilities
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
├── tests/
│   ├── smoke_test.py             # End-to-end test (needs isolation)
│   ├── utils.py                  # Test utilities
│   ├── test_data/
│   │   └── sample_inputs.json
│   ├── migrations/               # Migration verification tests
│   ├── unit/                     # Unit tests
│   │   └── config/
│   │       ├── __init__.py
│   │       └── test_settings.py
│   └── integration/              # Integration tests
├── scripts/
│   └── cleanup_legacy_files.py  # Legacy file cleanup utility
├── docs/
│   ├── standards/
│   │   ├── CODE_STANDARDS.md
│   │   ├── ERROR_HANDLING.md
│   │   └── TESTING_REQUIREMENTS.md
│   ├── migrations/
│   │   ├── phase_0_eventbus_migration.md
│   │   ├── phase1_implementation_plan.md
│   │   └── storage_consolidation.md
│   ├── setup/
│   │   └── PACKAGE_INVENTORY.md
│   └── multi_orchestrator_guide.md
├── Root files:
│   ├── orchestrator.py           # Single-project orchestrator (DEPRECATED)
│   ├── multi_orchestrator.py     # Multi-project orchestrator
│   ├── run_orchestrator.py       # Orchestrator CLI (DEPRECATED)
│   ├── run_multi_orchestrator.py # Multi-orchestrator CLI 
│   ├── task_manager.py           # Task queue management
│   ├── memory_store.py           # ✓ PERSISTENT (FAISS + JSON)
│   ├── graph_store.py            # ✓ PERSISTENT (JSON)
│   ├── agent_bus.py
│   ├── studio_ui.py              # Main Streamlit entry point
│   ├── copy_py_to_txt.ps1        # PowerShell utility script
│   ├── pytest.ini                # Pytest configuration
│   ├── requirements.txt
│   └── .gitignore
```

**Key characteristics**:
- All project data in `project_state/<project>/` directory
- EventBus for ephemeral real-time coordination
- AuditLog for persistent event history
- ProjectState for unified state management
- OutputManager for chapter/draft file persistence
- Registry pattern for project-scoped resources
- Agents are stateless, created per-task via AgentFactory
- Centralized configuration in `config/settings.py`
- Standardized UI utilities in `ui/common.py`
- Comprehensive testing structure with unit/integration tests
- Migration documentation and cleanup scripts


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
FEATURE STATUS: REAL-TIME WORKFLOW & FEEDBACK (IMPLEMENTED)
==============================================

We have implemented real-time workflow with the following components:

**✅ COMPLETED:**
1. **WebSocket Infrastructure** (`core/websocket_manager.py`)
   - WebSocket server running on port 8765
   - Thread-safe broadcasting to project subscribers
   - Automatic server startup with Streamlit

2. **EventBus WebSocket Integration** (`core/event_bus.py`)
   - Modified `publish()` method to broadcast events via WebSocket
   - Events sent as `eventbus_message` type with full metadata

3. **Streamlit WebSocket Client** (`ui/websocket_client.py`)
   - WebSocket client that runs in background thread
   - Message storage in Streamlit session state
   - Callback system for handling different message types

4. **Real-time UI Components** (`ui/live_event_panel.py`, `ui/pipeline_controls_ui.py`, `ui/feedback_injector_ui.py`)
   - Live Event Stream with WebSocket updates
   - Pipeline controls with start/pause/resume/stop
   - Feedback injection interface
   - Non-blocking UI updates

5. **Updated Main UI** (`studio_ui.py`)
   - WebSocket system initialization
   - Real-time status indicators
   - Integration of all feture components

**🔍 NEEDS VERIFICATION:**
- WebSocket events appearing in Live Event Stream
- Real-time updates without page refresh
- Pipeline controls working with WebSocket
- Feedback injection during pipeline execution

**🔧 KNOWN ISSUES:**
- WebSocket server shows "failed to start" in tests (because it's already running)
- Browser automation tests failing due to Playwright/Streamlit compatibility
- Some duplicate keys in UI components may need cleanup

**🎯 FEATURE IS FUNCTIONALLY COMPLETE BUT NEEDS PROPER TESTING**

--------------------------------
ROADMAP 
--------------------------------

REVIEW & TESTING: Verification & Test Suite (IMMEDIATE PRIORITY)
=======================================================================

We need to properly verify FEATURE REAL-TIME WORKFLOW & FEEDBACK implementation and create a comprehensive test suite.

**Primary Goal**: Verify that all of the real-time features work correctly in the actual Streamlit UI.

**Key Verification Points:**
1. **WebSocket Connectivity**
   - Server starts automatically with Streamlit
   - Clients can connect and subscribe
   - Connection status shows in UI

2. **Real-time Event Streaming**
   - EventBus events appear in Live Event Stream
   - Events update without page refresh
   - Multiple event types display correctly

3. **Pipeline Controls**
   - Start/pause/resume/stop buttons work
   - Pipeline status updates in real-time
   - Progress bars update dynamically

4. **Feedback Injection**
   - Can inject feedback during pipeline execution
   - Feedback appears for target agents
   - Priority system works correctly

5. **UI Responsiveness**
   - UI doesn't freeze during pipeline execution
   - Multiple components update simultaneously
   - Error handling doesn't break UI

**Testing Approach:**
1. **Manual UI Testing** - Step-by-step verification in browser
2. **Integration Tests** - Test WebSocket + EventBus + UI integration
3. **Component Tests** - Individual UI component testing
4. **End-to-End Tests** - Full workflow testing

**Expected Output:**
- Comprehensive test suite covering all REAL-TIME WORKFLOW & FEEDBACK
- Clear pass/fail criteria for each feature
- Documentation of any issues found
- Recommendations for fixes

LEGACY CODE REMOVAL: Cleanup Blocking Functionality (NEXT)
==========================================================

Once REAL-TIME WORKFLOW & FEEDBACK is verified, remove all legacy blocking code.

**Targets for Removal:**
1. **Old Producer Agent methods** that block UI
2. **Synchronous pipeline execution** patterns
3. **Legacy test files** from previous iterations
4. **Duplicate UI components** with "basic" or "simple" suffixes
5. **Any auto-refresh logic** using `time.sleep()` + `st.rerun()`

**Cleanup Tasks:**
1. Audit codebase for blocking patterns
2. Replace with async/WebSocket alternatives
3. Remove deprecated files
4. Update imports and dependencies
5. Verify all functionality still works

TEST FILE CLEANUP: Organize Test Structure (AFTER CLEANUP)
==========================================================

Consolidate and organize all test files.

**Current Test File Issues:**
- Multiple test files with similar names
- No clear test organization
- Some tests don't actually test anything
- Browser automation tests failing

**New Test Structure:**
tests/
├── unit/ # Unit tests
│ ├── core/ # Core component tests
│ ├── agents/ # Agent tests
│ └── ui/ # UI component tests
├── integration/ # Integration tests
│ ├── websocket/ # WebSocket integration tests
│ ├── eventbus/ # EventBus integration tests
│ └── persistence/ # Persistence layer tests
├── e2e/ # End-to-end tests
│ ├── websocket_ui/ # WebSocket UI tests
│ ├── pipeline_flows/ # Pipeline workflow tests
│ └── realtime_features/ # Real-time feature tests
└── fixtures/ # Test fixtures and data

**Cleanup Tasks:**
1. Delete unused/duplicate test files
2. Move tests to appropriate directories
3. Update test imports and dependencies
4. Create unified test runner
5. Add proper test documentation

Full Test Suite (NOT STARTED)
==================================================

I want a full test suite:

- Perform smoke tests that quickly show if the system is up and running
- Perform regression tests to make sure existing functionality hasn't broken
- A full deep set of tests that runs through the entire workflow and makes sure everything works perfectly
- Tests should use their own project and clean up after themselves.

This will keep my real projects clean and give me confidence that the system works end-to-end.
When completed, I want to rewrite the TESTING_REQUIREMENTS.md to document how testing works going forward

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
WHAT I WANT FROM YOU IN THIS CHAT
--------------------------------

**Immediate Focus**: 
1. Review the REAL-TIME WORKFLOW & FEEDBACK implementation for completeness
2. Create a comprehensive test plan to verify real-time features
3. Help me test the actual Streamlit UI functionality
4. Identify any issues with the current implementation

**Specifically Help With**:
1. **Test Strategy**: How to properly test WebSocket real-time features
2. **UI Verification**: Step-by-step manual testing procedures
3. **Integration Testing**: Test WebSocket + EventBus + UI together
4. **Issue Identification**: Find and document any bugs or issues
5. **Cleanup Planning**: Plan for legacy code removal after verification

**Ground Rules**:
1. Treat this document as the authoritative snapshot of my current system
2. Focus on TESTING and VERIFICATION of REAL-TIME WORKFLOW & FEEDBACK
3. Provide concrete, actionable testing steps
4. Don't break existing workflows
5. Follow established code standards
6. Do not number roadmap items, use their feature names especially in code comments. (it is ok to use numbers in our conversation for clarity, but don't use them in code, code comments, or file names)

**Architecture Patterns to Follow**:
- WebSocket for real-time communication
- EventBus for agent coordination
- Non-blocking UI updates
- Project-scoped resource management

**Never Do**:
- Don't create duplicate test files
- Don't break WebSocket functionality
- Don't revert to blocking patterns
- Don't skip proper testing procedures