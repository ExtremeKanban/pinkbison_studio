# Phase 0 Migration Guide

## Overview

This migration moves the project from IntelligenceBus (in-memory) to EventBus + AuditLog architecture.

## What Changed

### Architecture Changes

1. **IntelligenceBus → EventBus + AuditLog**
   - EventBus: Ephemeral, in-memory message passing (ring buffer)
   - AuditLog: Persistent, append-only log (JSON Lines)

2. **Agent Lifecycle**
   - Agents are now stateless (created per-task via AgentFactory)
   - No more `feedback_inbox` on agent instances
   - Feedback routed via EventBus

3. **Persistence**
   - New unified ProjectState class
   - All project data in `project_state/<project>/`
   - Automatic migration from legacy `projects/*.json`

4. **File Organization**
```
   project_state/
   ├── default_project/
   │   ├── state.json              # NEW: Unified state
   │   ├── memory.index            # MOVED from root
   │   ├── memory_texts.json       # MOVED from root
   │   ├── embeddings.npy          # MOVED from root
   │   └── graph.json              # MOVED from graphs/
   audit_logs/
   └── default_project_audit.jsonl # NEW: Persistent log
```

## Migration Steps

### Step 1: Install New Dependency
```bash
pip install filelock
```

### Step 2: Create New Directories
```bash
mkdir -p core
mkdir -p project_state
mkdir -p audit_logs
```

### Step 3: Backup Existing Data
```bash
# Backup projects
cp -r projects projects_backup

# Backup memory files
cp *_memory.index memory_backup/ 2>/dev/null || true
cp *_memory_texts.json memory_backup/ 2>/dev/null || true
cp *_embeddings.npy memory_backup/ 2>/dev/null || true

# Backup graphs
cp -r graphs graphs_backup
```

### Step 4: Apply File Changes

Replace/add files as specified in the implementation guide above:

**Delete:**
- `intelligence_bus.py`

**Add (new core/ directory):**
- `core/event_bus.py`
- `core/audit_log.py`
- `core/project_state.py`
- `core/agent_factory.py`
- `core/__init__.py`

**Replace (agents/):**
- `agents/base_agent.py`
- `agents/plot_architect.py`
- `agents/worldbuilder.py`
- `agents/character_agent.py`
- `agents/scene_generator.py`
- `agents/continuity_agent.py`
- `agents/editor_agent.py`
- `agents/creative_director.py`
- `agents/producer.py`

**Replace (project management):**
- `project_manager/loader.py`

**Replace (UI):**
- `studio_ui.py`
- `ui/intelligence_panel.py`
- `ui/plot_architect_ui.py`
- `ui/worldbuilder_ui.py`
- `ui/character_ui.py`
- `ui/scene_pipeline_ui.py`
- `ui/story_bible_ui.py`

**Replace (orchestrator):**
- `orchestrator.py`

### Step 5: Test Migration
```bash
# Start Streamlit
streamlit run studio_ui.py

# In another terminal, start orchestrator
python run_orchestrator.py
```

### Step 6: Verify Data Migration

1. Open Streamlit UI
2. Select `default_project`
3. Check that existing data appears correctly
4. Verify new files created:
```bash
   ls project_state/default_project/
   # Should show: state.json
   
   ls audit_logs/
   # Should show: default_project_audit.jsonl
```

### Step 7: Test New Features

1. **Send feedback to an agent:**
   - Open Intelligence Panel
   - Enter feedback in agent text box
   - Click "Send to [agent]"
   - Run a pipeline and verify agent receives feedback

2. **View AuditLog:**
   - Open Intelligence Panel
   - Click "Search Audit Log"
   - Verify historical messages appear

3. **Verify EventBus:**
   - Run any pipeline
   - Check "Recent Agent Messages (Live)" section
   - Should see real-time messages

## Troubleshooting

### Issue: "No module named 'core'"

**Solution:** Ensure `core/__init__.py` exists and contains proper imports.

### Issue: "No module named 'filelock'"

**Solution:** Run `pip install filelock`

### Issue: Legacy project data not appearing

**Solution:** 
1. Check `projects/default_project.json` exists
2. Run project once to trigger migration
3. Check `project_state/default_project/state.json` created

### Issue: Memory files not found

**Solution:**
Memory files stay in root directory for now. Phase 1 will move them to subdirectories.

### Issue: Orchestrator crashes on startup

**Solution:**
1. Check `audit_logs/` directory exists
2. Verify EventBus and AuditLog initialization in orchestrator
3. Check console for specific error

## Rollback Procedure

If you need to rollback:
```bash
# 1. Stop all processes
# 2. Restore backups
cp -r projects_backup/* projects/
cp memory_backup/* ./

# 3. Checkout previous commit (if using git)
git checkout <previous-commit>

# 4. Restart services
```

## Next Steps

After successful migration, you're ready for:
- **Phase 1:** Multi-project orchestrator
- **Phase 2:** Async architecture
- **Phase 3:** Real-time feedback

## Questions?

Check the architecture analysis in `prompt.md` for detailed rationale behind these changes.