"""
Scene Pipeline UI component.
Uses standardized producer pattern from ui.common.
"""

import streamlit as st
from ui.common import get_producer
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session


def render_scene_pipeline(project_name: str):
    """Render Scene Pipeline UI panel"""
    # Get producer using standardized pattern
    producer = get_producer(project_name)

    st.header("Scene Pipeline (Scene Generator → Continuity → Editor)")

    st.text_area("Scene goal / prompt", key="scene_prompt")
    st.text_area("Relevant outline snippet", key="scene_outline_snippet")
    st.text_area("World notes for scene", key="scene_world_notes")
    st.text_area("Character notes for scene", key="scene_character_notes")

    auto_memory = st.checkbox(
        "Auto-store Scene facts in memory",
        value=True,
        key="auto_memory_scene",
    )
    run_continuity = st.checkbox("Run Continuity check", value=True, key="run_continuity")
    run_editor = st.checkbox("Run Editor polish", value=True, key="run_editor")

    if st.button("Generate Scene Pipeline"):
        prompt = st.session_state["scene_prompt"].strip()
        if prompt:
            results = producer.generate_scene_with_checks(
                scene_prompt=prompt,
                outline_snippet=st.session_state["scene_outline_snippet"],
                world_notes=st.session_state["scene_world_notes"],
                character_notes=st.session_state["scene_character_notes"],
                auto_memory=auto_memory,
                run_continuity=run_continuity,
                run_editor=run_editor,
            )

            st.session_state["scene_raw"] = results["raw"]
            st.session_state["scene_continuity"] = results["after_continuity"]
            st.session_state["scene_final"] = results["final"]

            st.subheader("Raw Scene")
            st.write(results["raw"])

            if run_continuity:
                st.subheader("After Continuity Check")
                st.write(results["after_continuity"])

            if run_editor:
                st.subheader("Final Edited Scene")
                st.write(results["final"])

            save_project_state(project_name, extract_state_from_session())
        else:
            st.info("Provide at least a scene goal / prompt.")

    st.markdown("---")