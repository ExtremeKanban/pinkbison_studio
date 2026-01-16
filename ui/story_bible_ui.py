import streamlit as st
from agents.producer import ProducerAgent
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session
from core.event_bus import EventBus
from core.audit_log import AuditLog


def render_story_bible_pipeline(project_name):
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

    st.header("Story Bible Pipeline (Producer Agent)")

    st.text_area(
        "Seed idea for full story bible pipeline",
        key="seed_idea_pipeline",
    )

    auto_memory = st.checkbox(
        "Auto-store facts in memory during pipeline",
        value=True,
        key="auto_memory_pipeline",
    )

    if st.button("Run Story Bible Pipeline"):
        seed = st.session_state["seed_idea_pipeline"].strip()
        if seed:
            results = producer.run_story_bible_pipeline(
                idea=seed,
                genre=st.session_state["project_genre"],
                tone=st.session_state["project_tone"],
                themes=st.session_state["project_themes"],
                setting=st.session_state["project_setting"],
                auto_memory=auto_memory,
            )

            st.session_state["pipeline_outline"] = results["outline"]
            st.session_state["pipeline_world"] = results["world"]
            st.session_state["pipeline_characters"] = results["characters"]

            st.subheader("Pipeline Output — 3‑Act Outline")
            st.write(results["outline"])

            st.subheader("Pipeline Output — World Bible")
            st.write(results["world"])

            st.subheader("Pipeline Output — Character Bible")
            st.write(results["characters"])

            save_project_state(project_name, extract_state_from_session())
        else:
            st.info("Provide a seed idea for the pipeline.")

    st.markdown("---")