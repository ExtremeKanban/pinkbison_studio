# Phase 1 Implementation Plan: Full Persistence Layer

## Overview
Complete the persistence layer so ALL important data is saved per project with auto-save/auto-load.

## Current Status

### ✅ Already Persisting:
- Memory (FAISS + JSON)
- Graph (JSON)
- Tasks (JSON)
- Audit log (JSONL)
- Project metadata (state.json via ProjectState)
- Basic agent outputs (outline, world, characters via ProjectState)

### ❌ Not Yet Persisting:
1. **Producer pipeline results** - Result objects from pipelines not saved to history
2. **Chapter/scene outputs** - Individual chapters/scenes not saved as files
3. **UI input fields** - seed_idea and other inputs not fully captured
4. **Continuity notes** - Only in memory/graph, no dedicated persistence
5. **Canon rules** - In GraphStore but no UI viewer/editor

## Implementation Steps

---

## Step 1: Enhance ProjectState for Pipeline Results

**File:** `core/project_state.py`

**Current State:**
```python
@dataclass
class PipelineResult:
    pipeline_type: str  # "story_bible", "chapter", "full_story", "director"
    timestamp: str
    result: Dict[str, Any]

@dataclass
class ProjectState:
    # ...
    pipeline_results: List[PipelineResult] = field(default_factory=list)
```

**Action:** Add method to append pipeline results
```python
def add_pipeline_result(self, pipeline_type: str, result: Dict[str, Any]) -> None:
    """Add a pipeline result to history"""
    pr = PipelineResult(
        pipeline_type=pipeline_type,
        timestamp=datetime.utcnow().isoformat(),
        result=result
    )
    self.pipeline_results.append(pr)
    self.save()  # Auto-save on change
```

---

## Step 2: Save Pipeline Results in Producer

**File:** `agents/producer.py`

**Modify methods:**
- `run_story_bible_pipeline()`
- `run_chapter_pipeline()`
- `run_full_story_pipeline()`
- `run_director_mode()`

**Pattern:**
```python
def run_story_bible_pipeline(...) -> dict:
    # ... existing code to generate result ...
    
    result = {
        "outline": outline,
        "world": world_doc,
        "characters": character_doc,
    }
    
    # NEW: Save to project state
    self._save_pipeline_result("story_bible", result)
    
    return result

def _save_pipeline_result(self, pipeline_type: str, result: Dict[str, Any]) -> None:
    """Save pipeline result to project state"""
    from core.project_state import ProjectState
    state = ProjectState.load(self.project_name)
    state.add_pipeline_result(pipeline_type, result)
    # Note: add_pipeline_result already calls save()
```

---

## Step 3: Persist Chapter/Scene Outputs as Files

**New Directory Structure:**
```
project_state/
└── <project_name>/
    ├── state.json
    ├── outputs/
    │   ├── chapters/
    │   │   ├── chapter_001.json
    │   │   ├── chapter_002.json
    │   │   └── ...
    │   ├── scenes/
    │   │   ├── scene_001.txt
    │   │   └── ...
    │   └── drafts/
    │       ├── draft_001_full_story.txt
    │       └── ...
```

**New File:** `core/output_manager.py`

```python
"""
Output file management for chapters, scenes, and drafts.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class OutputManager:
    """Manages persistent output files for a project"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.base_dir = Path("project_state") / project_name / "outputs"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.chapters_dir = self.base_dir / "chapters"
        self.scenes_dir = self.base_dir / "scenes"
        self.drafts_dir = self.base_dir / "drafts"
        
        self.chapters_dir.mkdir(exist_ok=True)
        self.scenes_dir.mkdir(exist_ok=True)
        self.drafts_dir.mkdir(exist_ok=True)
    
    def save_chapter(self, chapter_index: int, chapter_data: Dict[str, Any]) -> Path:
        """Save chapter data as JSON"""
        filename = f"chapter_{chapter_index:03d}.json"
        path = self.chapters_dir / filename
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(chapter_data, f, indent=2, ensure_ascii=False)
        
        return path
    
    def load_chapter(self, chapter_index: int) -> Dict[str, Any]:
        """Load chapter data"""
        filename = f"chapter_{chapter_index:03d}.json"
        path = self.chapters_dir / filename
        
        if not path.exists():
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_chapters(self) -> List[int]:
        """List all chapter indices"""
        chapters = []
        for path in self.chapters_dir.glob("chapter_*.json"):
            try:
                idx = int(path.stem.split('_')[1])
                chapters.append(idx)
            except (ValueError, IndexError):
                continue
        return sorted(chapters)
    
    def save_draft(self, draft_name: str, content: str) -> Path:
        """Save a draft (full story, etc.)"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{draft_name}_{timestamp}.txt"
        path = self.drafts_dir / filename
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return path
    
    def list_drafts(self) -> List[Path]:
        """List all draft files"""
        return sorted(self.drafts_dir.glob("*.txt"), reverse=True)
```

---

## Step 4: Integrate OutputManager into Producer

**File:** `agents/producer.py`

**Add to __init__:**
```python
from core.output_manager import OutputManager

class ProducerAgent:
    def __init__(self, ...):
        # ... existing code ...
        self.output_manager = OutputManager(project_name)
```

**Modify `run_full_story_pipeline`:**
```python
def run_full_story_pipeline(...) -> dict:
    # ... existing code generates chapters ...
    
    # Save each chapter
    for idx, chapter in enumerate(chapters):
        self.output_manager.save_chapter(idx, chapter)
    
    # Save full story draft
    full_story_text = "\n\n".join(ch["final"] for ch in chapters)
    self.output_manager.save_draft("full_story", full_story_text)
    
    return result
```

---

## Step 5: Capture All UI Inputs in ProjectState

**File:** `project_manager/state.py`

**Update `SESSION_KEYS`:**
```python
SESSION_KEYS = [
    # Project metadata
    "project_name",
    "project_genre",
    "project_tone",
    "project_themes",
    "project_setting",
    
    # Agent outputs
    "outline",
    "world",
    "characters",
    "scene_raw",
    "scene_continuity",
    "scene_final",
    
    # Pipeline outputs
    "pipeline_outline",
    "pipeline_world",
    "pipeline_characters",
    
    # UI inputs (NEW: add all missing inputs)
    "seed_idea_plot",
    "outline_for_world",
    "world_notes_for_chars",
    "outline_for_chars",
    "scene_prompt",
    "scene_outline_snippet",
    "scene_world_notes",
    "scene_character_notes",
    "seed_idea_pipeline",
    "memory_search_query",
    "new_memory_text",
    
    # Producer inputs (NEW)
    "producer_idea",
    "producer_max_chapters",
    "producer_auto_memory",
    "producer_run_continuity",
    "producer_run_editor",
    "producer_goal_mode",
]
```

**Update `extract_state_from_session`:**
```python
def extract_state_from_session() -> Dict[str, Any]:
    """Extract all session state into dict for saving"""
    state = {}
    
    # Extract standard keys
    for key in SESSION_KEYS:
        state[key] = st.session_state.get(key, "")
    
    # Extract inputs separately
    inputs = {}
    for key in SESSION_KEYS:
        if key.startswith(("seed_", "producer_", "memory_", "scene_", "outline_", "world_")):
            inputs[key] = st.session_state.get(key, "")
    
    state["inputs"] = inputs
    
    return state
```

---

## Step 6: Auto-Save After Pipeline Execution

**File:** `ui/producer_agent_ui.py`

**Pattern to add after each pipeline:**
```python
# After pipeline completes
result = producer.run_XXX_pipeline(...)

# Save result to session
st.session_state["producer_last_result"] = result

# AUTO-SAVE (NEW)
save_project_state(producer.project_name, extract_state_from_session())

# Render outputs
# ...
```

**Add to all pipeline execution blocks:**
- After `run_story_bible_pipeline`
- After `run_chapter_pipeline`
- After `run_full_story_pipeline`
- After `run_director_mode`

---

## Step 7: Add Continuity Notes to ProjectState

**File:** `core/project_state.py`

**Add field:**
```python
@dataclass
class ProjectState:
    # ... existing fields ...
    
    # Continuity tracking
    continuity_notes: List[str] = field(default_factory=list)
    
    def add_continuity_note(self, note: str) -> None:
        """Add a continuity note"""
        self.continuity_notes.append({
            "timestamp": datetime.utcnow().isoformat(),
            "note": note
        })
        self.save()
```

**File:** `agents/continuity_agent.py`

**Add after critique generation:**
```python
def run(self, scene_text: str) -> str:
    # ... existing code ...
    
    # Save continuity note to project state
    if self.project_name:
        from core.project_state import ProjectState
        state = ProjectState.load(self.project_name)
        state.add_continuity_note(f"Reviewed scene: {critique[:100]}...")
    
    return revised_scene
```

---

## Step 8: Create UI for Viewing Pipeline History

**New File:** `ui/pipeline_history_ui.py`

```python
"""
Pipeline History UI - View past pipeline results
"""

import streamlit as st
from core.project_state import ProjectState


def render_pipeline_history(project_name: str):
    """Render pipeline history viewer"""
    st.header("Pipeline History")
    
    state = ProjectState.load(project_name)
    
    if not state.pipeline_results:
        st.info("No pipeline results yet. Run a pipeline to see history here.")
        return
    
    st.write(f"Found {len(state.pipeline_results)} pipeline runs")
    
    # Show in reverse chronological order
    for idx, pr in enumerate(reversed(state.pipeline_results)):
        with st.expander(f"{pr.pipeline_type} - {pr.timestamp}", expanded=(idx == 0)):
            st.json(pr.result)
```

**File:** `studio_ui.py`

**Add new page:**
```python
# In page selection
pages = [
    "Plot Architect",
    "Worldbuilder",
    "Character Agent",
    "Scene Pipeline",
    "Story Bible",
    "Producer Agent",
    "Intelligence Panel",
    "Memory Browser",
    "Memory Search",
    "Memory Add",
    "General Playground",
    "Pipeline History",  # NEW
]

# In page rendering
elif page == "Pipeline History":
    from ui.pipeline_history_ui import render_pipeline_history
    render_pipeline_history(current_project)
```

---

## Step 9: Add Canon Rules Viewer

**New File:** `ui/canon_rules_ui.py`

```python
"""
Canon Rules UI - View and manage canon rules from GraphStore
"""

import streamlit as st
from core.registry import REGISTRY


def render_canon_rules(project_name: str):
    """Render canon rules viewer"""
    st.header("Canon Rules")
    
    graph = REGISTRY.get_graph_store(project_name)
    canon_rules = graph.get_canon_rules()
    
    if not canon_rules:
        st.info("No canon rules yet. Run Director Mode to generate canon rules.")
        return
    
    st.write(f"Found {len(canon_rules)} canon rules")
    
    for idx, rule in enumerate(canon_rules):
        with st.expander(f"Rule {idx + 1}: {rule.get('rule', '')[:50]}...", expanded=False):
            st.write("**Rule:**", rule.get('rule', ''))
            st.write("**Source:**", rule.get('source', 'Unknown'))
            if 'confidence' in rule:
                st.write("**Confidence:**", rule['confidence'])
```

**File:** `studio_ui.py`

**Add new page:**
```python
pages = [
    # ... existing pages ...
    "Canon Rules",  # NEW
]

elif page == "Canon Rules":
    from ui.canon_rules_ui import render_canon_rules
    render_canon_rules(current_project)
```

---

## Step 10: Add Project Reset Function

**File:** `project_manager/loader.py`

```python
def reset_project(project_name: str) -> None:
    """Reset project to default state (clear all data)"""
    # Clear project state
    state = ProjectState.create_default(project_name)
    state.save()
    
    # Clear memory
    from core.registry import REGISTRY
    memory = REGISTRY.get_memory_store(project_name)
    memory.clear()
    
    # Clear graph
    graph = REGISTRY.get_graph_store(project_name)
    graph.replace_graph({"entities": [], "relationships": [], "events": [], "canon_rules": []})
    
    # Clear tasks
    tasks = REGISTRY.get_task_manager(project_name)
    # Task manager doesn't have clear method yet - add it or delete file
    
    # Clear outputs
    import shutil
    outputs_dir = Path("project_state") / project_name / "outputs"
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
        outputs_dir.mkdir(parents=True, exist_ok=True)
```

**File:** `ui/sidebar.py`

**Add reset button:**
```python
# In Danger Zone section
if st.sidebar.button("Reset Current Project"):
    name = st.session_state["current_project"]
    from project_manager.loader import reset_project
    reset_project(name)
    load_state_into_session(load_project_state(name))
    st.sidebar.success(f"Reset project '{name}'.")
    st.rerun()
```

---

## Step 11: Update Registry to Support OutputManager

**File:** `core/registry.py`

```python
from core.output_manager import OutputManager

class ProjectRegistry:
    def __init__(self):
        # ... existing code ...
        self._output_managers: Dict[str, OutputManager] = {}
    
    def get_output_manager(self, project_name: str) -> OutputManager:
        """Get or create OutputManager for project"""
        if project_name not in self._output_managers:
            self._output_managers[project_name] = OutputManager(project_name)
        return self._output_managers[project_name]
    
    def clear_project(self, project_name: str) -> None:
        """Remove all instances for a project"""
        # ... existing code ...
        self._output_managers.pop(project_name, None)
```

---

## Testing Checklist

After implementation, verify:

- [ ] Run story bible pipeline → Check `pipeline_results` in state.json
- [ ] Run full story pipeline → Check chapters saved in `outputs/chapters/`
- [ ] Run full story pipeline → Check draft saved in `outputs/drafts/`
- [ ] Change UI inputs → Save project → Reload → Verify inputs restored
- [ ] Switch projects → Verify state saved/loaded correctly
- [ ] View Pipeline History page → Verify results appear
- [ ] View Canon Rules page → Verify rules from graph appear
- [ ] Reset project → Verify all data cleared
- [ ] Delete project → Verify all files removed

---

## Migration Notes

**Backward Compatibility:**
- Existing projects without `pipeline_results` will load with empty list
- Existing projects without `outputs/` directory will create it on first use
- ProjectState.load() handles missing fields gracefully

**File Locations:**
All project data now in unified location:
```
project_state/
└── <project_name>/
    ├── state.json           # ProjectState
    ├── memory.index         # MemoryStore
    ├── memory_texts.json    # MemoryStore
    ├── embeddings.npy       # MemoryStore
    ├── graph.json           # GraphStore
    ├── outputs/             # NEW
    │   ├── chapters/
    │   ├── scenes/
    │   └── drafts/
```

---

## Summary

This completes Phase 1 by ensuring:
1. ✅ All pipeline results saved to history
2. ✅ Chapters/scenes persisted as files
3. ✅ All UI inputs captured in state
4. ✅ Auto-save after every pipeline
5. ✅ Continuity notes persisted
6. ✅ Canon rules viewable in UI
7. ✅ Project reset functionality
8. ✅ Clean project deletion

**Next:** Phase 2 (Multi-Project Orchestrator)
