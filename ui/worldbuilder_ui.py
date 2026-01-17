"""
Worldbuilder UI component.
Uses standardized producer pattern from ui.common.
"""

import streamlit as st
from ui.common import get_producer
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session


def render_worldbuilder(project_name: str):
    """Render Worldbuilder UI panel"""
    # Get producer using standardized pattern
    producer = get_producer(project_name)

    st.header("Worldbuilder Agent")

    st.text_area("Outline for Worldbuilder", key="outline_for_world")

    auto_memory = st.checkbox(
        "Auto-store world facts in memory",
        value=True,
        key="auto_memory_world",
    )

    if st.button("Generate World Bible"):
        outline = st.session_state["outline_for_world"].strip()
        if outline:
            # Create fresh agent instance
            agent = producer.agent_factory.create_worldbuilder()
            
            world_doc = agent.run(
                outline=outline,
                genre=st.session_state["project_genre"],
                tone=st.session_state["project_tone"],
                themes=st.session_state["project_themes"],
                setting=st.session_state["project_setting"],
                auto_memory=auto_memory,
            )
            st.session_state["world"] = world_doc
            st.subheader("World Bible")
            st.write(world_doc)

            save_project_state(project_name, extract_state_from_session())
        else:
            st.info("Provide at least an outline for the Worldbuilder.")

    st.markdown("---")