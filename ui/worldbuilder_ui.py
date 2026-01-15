import streamlit as st
from agents.producer import ProducerAgent
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session

def render_worldbuilder(project_name):

    # Ensure a shared ProducerAgent exists
    if "producer" not in st.session_state:
        st.session_state["producer"] = ProducerAgent(project_name)

    producer = st.session_state["producer"]
    agent = producer.worldbuilder

    st.header("Worldbuilder Agent")

    st.text_area("Outline for Worldbuilder", key="outline_for_world")
    st.text_area("Genre", key="genre_for_world")
    st.text_area("Tone", key="tone_for_world")
    st.text_area("Themes", key="themes_for_world")
    st.text_area("Setting", key="setting_for_world")

    auto_memory = st.checkbox(
        "Auto-store world facts in memory",
        value=True,
        key="auto_memory_world",
    )

    if st.button("Generate World Bible"):
        outline = st.session_state["outline_for_world"].strip()
        if outline:
            world_doc = agent.run(
                outline=outline,
                genre=st.session_state["genre_for_world"],
                tone=st.session_state["tone_for_world"],
                themes=st.session_state["themes_for_world"],
                setting=st.session_state["setting_for_world"],
                auto_memory=auto_memory,
            )
            st.session_state["world"] = world_doc
            st.subheader("World Bible")
            st.write(world_doc)

            save_project_state(project_name, extract_state_from_session())
        else:
            st.info("Provide at least an outline for the Worldbuilder.")

    st.markdown("---")
