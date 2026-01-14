from typing import Dict, Any
import streamlit as st


SESSION_KEYS = [
    "project_name",
    "project_genre",
    "project_tone",
    "project_themes",
    "project_setting",
    "outline",
    "world",
    "characters",
    "scene_raw",
    "scene_continuity",
    "scene_final",
    "pipeline_outline",
    "pipeline_world",
    "pipeline_characters",
    # input keys
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
]


def initialize_session_state() -> None:
    for key in SESSION_KEYS:
        if key not in st.session_state:
            st.session_state[key] = ""


def load_state_into_session(state: Dict[str, Any]) -> None:
    """
    Take a project state dict (from loader) and hydrate st.session_state.
    """
    meta = state.get("meta", {})

    st.session_state["project_name"] = state.get("project_name", "default_project")
    st.session_state["project_genre"] = meta.get("genre", "Sci‑Fi")
    st.session_state["project_tone"] = meta.get("tone", "Epic, serious")
    st.session_state["project_themes"] = meta.get("themes", "Destiny, sacrifice, technology vs humanity")
    st.session_state["project_setting"] = meta.get("setting", "Far future galaxy")

    st.session_state["outline"] = state.get("outline", "")
    st.session_state["world"] = state.get("world", "")
    st.session_state["characters"] = state.get("characters", "")

    st.session_state["scene_raw"] = state.get("scene_raw", "")
    st.session_state["scene_continuity"] = state.get("scene_continuity", "")
    st.session_state["scene_final"] = state.get("scene_final", "")

    st.session_state["pipeline_outline"] = state.get("pipeline_outline", "")
    st.session_state["pipeline_world"] = state.get("pipeline_world", "")
    st.session_state["pipeline_characters"] = state.get("pipeline_characters", "")

    inputs = state.get("inputs", {})
    st.session_state["seed_idea_plot"] = inputs.get("seed_idea_plot", "")
    st.session_state["outline_for_world"] = inputs.get("outline_for_world", "")
    st.session_state["world_notes_for_chars"] = inputs.get("world_notes_for_chars", "")
    st.session_state["outline_for_chars"] = inputs.get("outline_for_chars", "")
    st.session_state["scene_prompt"] = inputs.get("scene_prompt", "")
    st.session_state["scene_outline_snippet"] = inputs.get("scene_outline_snippet", "")
    st.session_state["scene_world_notes"] = inputs.get("scene_world_notes", "")
    st.session_state["scene_character_notes"] = inputs.get("scene_character_notes", "")
    st.session_state["seed_idea_pipeline"] = inputs.get("seed_idea_pipeline", "")
    st.session_state["memory_search_query"] = inputs.get("memory_search_query", "")
    st.session_state["new_memory_text"] = inputs.get("new_memory_text", "")


def extract_state_from_session() -> Dict[str, Any]:
    """
    Extract current st.session_state into a project state dict for saving.
    """
    state: Dict[str, Any] = {
        "project_name": st.session_state.get("project_name", "default_project"),
        "meta": {
            "genre": st.session_state.get("project_genre", "Sci‑Fi"),
            "tone": st.session_state.get("project_tone", "Epic, serious"),
            "themes": st.session_state.get("project_themes", "Destiny, sacrifice, technology vs humanity"),
            "setting": st.session_state.get("project_setting", "Far future galaxy"),
        },
        "outline": st.session_state.get("outline", ""),
        "world": st.session_state.get("world", ""),
        "characters": st.session_state.get("characters", ""),
        "scene_raw": st.session_state.get("scene_raw", ""),
        "scene_continuity": st.session_state.get("scene_continuity", ""),
        "scene_final": st.session_state.get("scene_final", ""),
        "pipeline_outline": st.session_state.get("pipeline_outline", ""),
        "pipeline_world": st.session_state.get("pipeline_world", ""),
        "pipeline_characters": st.session_state.get("pipeline_characters", ""),
        "inputs": {
            "seed_idea_plot": st.session_state.get("seed_idea_plot", ""),
            "outline_for_world": st.session_state.get("outline_for_world", ""),
            "world_notes_for_chars": st.session_state.get("world_notes_for_chars", ""),
            "outline_for_chars": st.session_state.get("outline_for_chars", ""),
            "scene_prompt": st.session_state.get("scene_prompt", ""),
            "scene_outline_snippet": st.session_state.get("scene_outline_snippet", ""),
            "scene_world_notes": st.session_state.get("scene_world_notes", ""),
            "scene_character_notes": st.session_state.get("scene_character_notes", ""),
            "seed_idea_pipeline": st.session_state.get("seed_idea_pipeline", ""),
            "memory_search_query": st.session_state.get("memory_search_query", ""),
            "new_memory_text": st.session_state.get("new_memory_text", ""),
        }
    }
    return state
