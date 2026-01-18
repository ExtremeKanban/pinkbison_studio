"""
Project loader now uses ProjectState for unified state management.
Maintains backward compatibility with old projects/*.json format.
"""

import os
import json
from typing import Dict, Any, List
from pathlib import Path

from core.project_state import ProjectState
from config.settings import STORAGE_CONFIG

# Legacy directory for backward compatibility
LEGACY_PROJECTS_DIR = str(STORAGE_CONFIG.legacy_projects_dir)


def ensure_legacy_dir() -> None:
    """Ensure legacy projects directory exists"""
    if not os.path.exists(LEGACY_PROJECTS_DIR):
        os.makedirs(LEGACY_PROJECTS_DIR)


def get_legacy_project_path(project_name: str) -> str:
    """Get path to legacy project JSON"""
    ensure_legacy_dir()
    safe_name = project_name.strip().replace(" ", "_")
    return os.path.join(LEGACY_PROJECTS_DIR, f"{safe_name}.json")


def project_exists(project_name: str) -> bool:
    """Check if project exists (new or legacy format)"""
    # Check new format
    new_path = Path("project_state") / project_name / "state.json"
    if new_path.exists():
        return True
    
    # Check legacy format
    legacy_path = Path(get_legacy_project_path(project_name))
    return legacy_path.exists()


def list_projects() -> List[str]:
    """List all projects (new and legacy)"""
    projects = set()
    
    # List new format projects
    new_dir = Path("project_state")
    if new_dir.exists():
        for item in new_dir.iterdir():
            if item.is_dir() and (item / "state.json").exists():
                projects.add(item.name)
    
    # List legacy format projects
    ensure_legacy_dir()
    for fname in os.listdir(LEGACY_PROJECTS_DIR):
        if fname.endswith(".json"):
            projects.add(os.path.splitext(fname)[0])
    
    return sorted(list(projects))


def load_project_state(project_name: str) -> Dict[str, Any]:
    """
    Load project state, handling both new and legacy formats.
    Migrates legacy format to new format automatically.
    """
    # Try new format first
    new_path = Path("project_state") / project_name / "state.json"
    if new_path.exists():
        state = ProjectState.load(project_name)
        return state.to_dict()
    
    # Try legacy format
    legacy_path = Path(get_legacy_project_path(project_name))
    if legacy_path.exists():
        with open(legacy_path, 'r', encoding='utf-8') as f:
            legacy_data = json.load(f)
        
        # Migrate to new format
        state = _migrate_from_legacy(project_name, legacy_data)
        state.save()  # Save in new format
        
        return state.to_dict()
    
    # No existing project, create default
    state = ProjectState.create_default(project_name)
    state.save()
    return state.to_dict()


def save_project_state(project_name: str, state: Dict[str, Any]) -> None:
    """Save project state using new format"""
    project_state = ProjectState.from_dict(state)
    project_state.save()


def duplicate_project(src_project: str, dst_project: str) -> None:
    """Duplicate project (handles both formats)"""
    if not project_exists(src_project):
        raise ValueError(f"Source project '{src_project}' does not exist.")
    
    # Load source state
    src_state = load_project_state(src_project)
    
    # Update project name
    src_state['project_name'] = dst_project
    
    # Save as new project
    save_project_state(dst_project, src_state)


def delete_project(project_name: str) -> None:
    """Delete project (handles both formats)"""
    # Delete new format
    new_dir = Path("project_state") / project_name
    if new_dir.exists():
        import shutil
        shutil.rmtree(new_dir)
    
    # Delete legacy format
    legacy_path = Path(get_legacy_project_path(project_name))
    if legacy_path.exists():
        legacy_path.unlink()


def _migrate_from_legacy(project_name: str, legacy_data: Dict[str, Any]) -> ProjectState:
    """Migrate legacy project JSON to new ProjectState format"""
    from core.project_state import ProjectMeta
    
    # Extract metadata
    meta_data = legacy_data.get('meta', {})
    meta = ProjectMeta(
        genre=meta_data.get('genre', 'Sci-Fi'),
        tone=meta_data.get('tone', 'Epic, serious'),
        themes=meta_data.get('themes', 'Destiny, sacrifice, technology vs humanity'),
        setting=meta_data.get('setting', 'Far future galaxy')
    )
    
    # Create state
    state = ProjectState(
        project_name=project_name,
        meta=meta,
        outline=legacy_data.get('outline', ''),
        world=legacy_data.get('world', ''),
        characters=legacy_data.get('characters', ''),
        scene_raw=legacy_data.get('scene_raw', ''),
        scene_continuity=legacy_data.get('scene_continuity', ''),
        scene_final=legacy_data.get('scene_final', ''),
        pipeline_outline=legacy_data.get('pipeline_outline', ''),
        pipeline_world=legacy_data.get('pipeline_world', ''),
        pipeline_characters=legacy_data.get('pipeline_characters', ''),
        inputs=legacy_data.get('inputs', {}),
    )
    
    return state


# Legacy compatibility functions
def default_project_state(project_name: str) -> Dict[str, Any]:
    """Legacy function - now uses ProjectState"""
    state = ProjectState.create_default(project_name)
    return state.to_dict()


def merge_with_defaults(project_name: str, loaded: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function - now uses ProjectState migration"""
    # This is handled by ProjectState.load automatically
    return loaded


def reset_project(project_name: str) -> None:
    """Reset project to default state (clear all data)"""
    from core.registry import REGISTRY
    import shutil
    
    # Clear project state
    state = ProjectState.create_default(project_name)
    state.save()
    
    # Clear memory
    memory = REGISTRY.get_memory_store(project_name)
    memory.clear()
    
    # Clear graph
    graph = REGISTRY.get_graph_store(project_name)
    graph.replace_graph({"entities": [], "relationships": [], "events": [], "canon_rules": []})
    
    # Clear outputs
    outputs_dir = Path("project_state") / project_name / "outputs"
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
        outputs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[Loader] Reset project '{project_name}'")