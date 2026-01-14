import streamlit as st
from memory_store import MemoryStore
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session


def render_memory_add(project_name):
    memory = MemoryStore(project_name)

    st.header("Add Memory")

    st.text_input("Memory text", key="new_memory_text")

    if st.button("Add to Memory"):
        new_memory = st.session_state["new_memory_text"].strip()
        if new_memory:
            memory.add(new_memory)
            st.success("Memory added!")
            st.session_state["new_memory_text"] = ""
            save_project_state(project_name, extract_state_from_session())
        else:
            st.info("Enter some text to add to memory.")

    st.markdown("---")
