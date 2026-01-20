"""
UI initialization utilities.
Ensures projects exist and are properly loaded.
"""

import streamlit as st
from project_manager.loader import project_exists, load_project_state, save_project_state
from project_manager.state import load_state_into_session


def ensure_project_exists(project_name: str) -> bool:
    """
    Ensure a project exists on disk.
    Creates it if missing.
    
    Args:
        project_name: Name of project to ensure exists
        
    Returns:
        True if project exists or was created, False on error
    """
    if project_exists(project_name):
        return True
    
    try:
        # Create the project by loading it (creates default if missing)
        state = load_project_state(project_name)
        save_project_state(project_name, state)
        print(f"[Initialization] Created project: {project_name}")
        return True
    except Exception as e:
        print(f"[Initialization] Failed to create project {project_name}: {e}")
        return False


def initialize_ui() -> None:
    """
    Initialize the UI with proper project state.
    Called at the start of studio_ui.py
    """
    from project_manager.state import initialize_session_state
    
    # Initialize session state
    initialize_session_state()
    
    # Ensure current_project exists in session
    if "current_project" not in st.session_state:
        st.session_state["current_project"] = "default_project"
    
    # Ensure the project exists on disk
    project_name = st.session_state["current_project"]
    if ensure_project_exists(project_name):
        # Load the project state into session
        state = load_project_state(project_name)
        load_state_into_session(state)
        print(f"[Initialization] Loaded project: {project_name}")
    else:
        print(f"[Initialization] Failed to initialize project: {project_name}")
        # Fallback to empty session state