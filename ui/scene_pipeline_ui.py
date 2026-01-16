import streamlit as st
from agents.producer import ProducerAgent
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session
from core.event_bus import EventBus
from core.audit_log import AuditLog


def render_scene_pipeline(project_name):
    # Ensure ProducerAgent exists
    if "producer" not in st.session_state:
        fast_model_url = "http://localhost:8000/v1/chat/completions"
        model_mode = "fast"
        
        event_bus = EventBus(project_name)
        audit_log = AuditLog(project_name)

        st.session_state["producer"] = ProducerAgent(
            project_name=project_name,
            event_bus=event_bus,
            audit_log=audit_log,
            fast_model_url=fast_model_url,
            model_mode=model_mode,
        )

    producer = st.session_state["producer"]

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