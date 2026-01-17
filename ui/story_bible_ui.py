"""
Story Bible Pipeline UI component.
Uses standardized producer pattern from ui.common.
"""

import streamlit as st
from ui.common import get_producer
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session


def render_story_bible_pipeline(project_name: str):
    """Render Story Bible Pipeline UI panel"""
    # Get producer using standardized pattern
    producer = get_producer(project_name)

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