"""
Character Agent UI component.
Uses standardized producer pattern from ui.common.
"""

import streamlit as st
from ui.common import get_producer
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session


def render_character_agent(project_name: str):
    """Render Character Agent UI panel"""
    # Get producer using standardized pattern
    producer = get_producer(project_name)

    st.header("Character Agent")

    st.text_area("Outline for Character Agent", key="outline_for_chars")
    st.text_area("World notes for Character Agent", key="world_notes_for_chars")

    auto_memory = st.checkbox(
        "Auto-store Character facts in memory",
        value=True,
        key="auto_memory_chars",
    )

    if st.button("Generate Character Bible"):
        outline = st.session_state["outline_for_chars"].strip()
        if outline:
            # Create fresh agent instance
            agent = producer.agent_factory.create_character_agent()
            
            characters_doc = agent.run(
                outline=outline,
                world_notes=st.session_state["world_notes_for_chars"],
                auto_memory=auto_memory,
            )
            st.session_state["characters"] = characters_doc
            st.subheader("Character Bible")
            st.write(characters_doc)

            save_project_state(project_name, extract_state_from_session())
        else:
            st.info("Provide at least an outline for the Character Agent.")

    st.markdown("---")