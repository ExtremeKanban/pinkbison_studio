"""
Plot Architect UI component.
Uses standardized producer pattern from ui.common.
"""

import streamlit as st
from ui.common import get_producer
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session


def render_plot_architect(project_name: str):
    """Render Plot Architect UI panel"""
    # Get producer using standardized pattern
    producer = get_producer(project_name)
    
    st.header("Plot Architect Agent")

    st.text_area("Seed idea for the Plot Architect", key="seed_idea_plot")

    auto_memory = st.checkbox(
        "Auto-store Plot Architect facts in memory",
        value=False,
        key="auto_memory_plot",
    )

    if st.button("Generate 3‑Act Outline"):
        seed = st.session_state["seed_idea_plot"].strip()
        if seed:
            # Create fresh agent instance
            agent = producer.agent_factory.create_plot_architect()
            
            outline = agent.run(
                seed,
                st.session_state["project_genre"],
                st.session_state["project_tone"],
                st.session_state["project_themes"],
                st.session_state["project_setting"],
                auto_memory=auto_memory,
            )
            st.session_state["outline"] = outline
            st.subheader("3‑Act Outline")
            st.write(outline)

            save_project_state(project_name, extract_state_from_session())
        else:
            st.info("Enter a seed idea for the Plot Architect.")

    st.markdown("---")