import streamlit as st

from project_manager.registry import (
    get_all_projects,
    create_project_if_missing,
    duplicate_project_state,
    delete_project,
)
from project_manager.loader import load_project_state, save_project_state
from project_manager.state import load_state_into_session, extract_state_from_session
from ui.initialization import ensure_project_exists


def render_sidebar():
    st.sidebar.header("Project Management")

    # Ensure default_project exists before listing
    ensure_project_exists("default_project")

    existing = get_all_projects()
    if "default_project" not in existing:
        existing.insert(0, "default_project")

    st.sidebar.markdown("### Active Project")
    current = st.sidebar.selectbox(
        "Active Project",
        existing,
        index=existing.index(st.session_state["current_project"]),
        label_visibility="collapsed",
    )

    switched = current != st.session_state["current_project"]

    if switched:
        prev = st.session_state["current_project"]
        save_project_state(prev, extract_state_from_session())

        st.session_state["current_project"] = current
        load_state_into_session(load_project_state(current))

    # Create / Duplicate toggles
    col_new, col_dup = st.sidebar.columns([1, 1])

    if "show_create" not in st.session_state:
        st.session_state["show_create"] = False
    if "show_duplicate" not in st.session_state:
        st.session_state["show_duplicate"] = False

    with col_new:
        if st.button("➕", help="Create New Project"):
            st.session_state["show_create"] = not st.session_state["show_create"]

    with col_dup:
        if st.button("⎘", help="Duplicate Project"):
            st.session_state["show_duplicate"] = not st.session_state["show_duplicate"]

    st.sidebar.markdown("---")

    # Create Project
    if st.session_state["show_create"]:
        st.sidebar.markdown("### Create New Project")
        name = st.sidebar.text_input("Name", key="new_project_name")

        if st.sidebar.button("Create", key="create_btn"):
            name = name.strip()
            if name:
                create_project_if_missing(name)
                st.session_state["current_project"] = name
                load_state_into_session(load_project_state(name))
                st.rerun()

        st.sidebar.markdown("---")

    # Duplicate Project
    if st.session_state["show_duplicate"]:
        st.sidebar.markdown("### Duplicate Project")
        dup_name = st.sidebar.text_input("Duplicate As", key="dup_project_name")

        if st.sidebar.button("Duplicate", key="dup_btn"):
            src = st.session_state["current_project"]
            dst = dup_name.strip()
            if dst:
                duplicate_project_state(src, dst)
                st.session_state["current_project"] = dst
                load_state_into_session(load_project_state(dst))
                st.rerun()

        st.sidebar.markdown("---")

    # Project Settings
    st.sidebar.markdown("### Project Settings")

    st.session_state["project_genre"] = st.sidebar.text_input(
        "Genre", st.session_state.get("project_genre", "Sci‑Fi")
    )
    st.session_state["project_tone"] = st.sidebar.text_input(
        "Tone", st.session_state.get("project_tone", "Epic, serious")
    )
    st.session_state["project_themes"] = st.sidebar.text_area(
        "Themes",
        st.session_state.get(
            "project_themes",
            "Destiny, sacrifice, technology vs humanity",
        ),
    )
    st.session_state["project_setting"] = st.sidebar.text_input(
        "Setting", st.session_state.get("project_setting", "Far future galaxy")
    )

    if st.sidebar.button("Save Project"):
        save_project_state(
            st.session_state["current_project"],
            extract_state_from_session(),
        )
        st.sidebar.success("Saved.")

    st.sidebar.markdown("---")

    # Danger Zone
    st.sidebar.markdown("### 🗑️ Danger Zone")
    
    if st.sidebar.button("Reset Current Project"):
        from project_manager.loader import reset_project
        name = st.session_state["current_project"]
        reset_project(name)
        load_state_into_session(load_project_state(name))
        st.sidebar.success(f"Reset project '{name}'.")
        st.rerun()
    
    if st.sidebar.button("Delete Current Project"):
        name = st.session_state["current_project"]
        if name == "default_project":
            st.sidebar.error("Cannot delete the default project.")
        else:
            delete_project(name)
            st.session_state["current_project"] = "default_project"
            load_state_into_session(load_project_state("default_project"))
            st.sidebar.success(f"Deleted project '{name}'.")
            st.rerun()

    return st.session_state["current_project"]