import os
import json
from typing import Dict, Any, List

PROJECTS_DIR = "projects"


def ensure_projects_dir() -> None:
    if not os.path.exists(PROJECTS_DIR):
        os.makedirs(PROJECTS_DIR)


def get_project_path(project_name: str) -> str:
    ensure_projects_dir()
    safe_name = project_name.strip().replace(" ", "_")
    return os.path.join(PROJECTS_DIR, f"{safe_name}.json")


def project_exists(project_name: str) -> bool:
    return os.path.exists(get_project_path(project_name))


def list_projects() -> List[str]:
    ensure_projects_dir()
    projects = []
    for fname in os.listdir(PROJECTS_DIR):
        if fname.endswith(".json"):
            projects.append(os.path.splitext(fname)[0])
    projects.sort()
    return projects


def load_project_state(project_name: str) -> Dict[str, Any]:
    """
    Load a project's UI/state from JSON.
    If it does not exist, return a fresh default state.
    """
    path = get_project_path(project_name)
    if not os.path.exists(path):
        return default_project_state(project_name)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return merge_with_defaults(project_name, data)


def save_project_state(project_name: str, state: Dict[str, Any]) -> None:
    """
    Save a project's UI/state to JSON.
    """
    path = get_project_path(project_name)
    ensure_projects_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def duplicate_project(src_project: str, dst_project: str) -> None:
    """
    Duplicate src_project.json to dst_project.json (UI/state only).
    Memory (FAISS + embeddings) will be handled separately by MemoryStore when you use the new project.
    """
    if not project_exists(src_project):
        raise ValueError(f"Source project '{src_project}' does not exist.")

    src_path = get_project_path(src_project)
    dst_path = get_project_path(dst_project)

    with open(src_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    save_project_state(dst_project, data)

def delete_project(project_name: str) -> None:
    """
    Delete a project's JSON file.
    Does NOT delete memory files — those are handled by MemoryStore.
    """
    path = get_project_path(project_name)
    if os.path.exists(path):
        os.remove(path)


def default_project_state(project_name: str) -> Dict[str, Any]:
    """
    Default empty state for a new project.
    """
    return {
        "project_name": project_name,
        "meta": {
            "genre": "Sci‑Fi",
            "tone": "Epic, serious",
            "themes": "Destiny, sacrifice, technology vs humanity",
            "setting": "Far future galaxy"
        },
        "outline": "",
        "world": "",
        "characters": "",
        "scene_raw": "",
        "scene_continuity": "",
        "scene_final": "",
        "pipeline_outline": "",
        "pipeline_world": "",
        "pipeline_characters": "",
        "inputs": {
            "seed_idea_plot": "",
            "outline_for_world": "",
            "world_notes_for_chars": "",
            "outline_for_chars": "",
            "scene_prompt": "",
            "scene_outline_snippet": "",
            "scene_world_notes": "",
            "scene_character_notes": "",
            "seed_idea_pipeline": "",
            "memory_search_query": "",
            "new_memory_text": ""
        }
    }


def merge_with_defaults(project_name: str, loaded: Dict[str, Any]) -> Dict[str, Any]:
    """
    If we add new fields later, ensure old project files still work by merging with defaults.
    """
    defaults = default_project_state(project_name)

    def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(base)
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(result.get(k), dict):
                result[k] = deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    return deep_merge(defaults, loaded)
