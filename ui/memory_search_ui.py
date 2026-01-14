import streamlit as st
from memory_store import MemoryStore


def render_memory_search(project_name):
    memory = MemoryStore(project_name)

    st.header("Memory Search")

    st.text_input("Search memory", key="memory_search_query")

    if st.button("Search Memory"):
        query = st.session_state["memory_search_query"].strip()
        if query:
            results = memory.search(query)
            st.subheader("Search Results")
            st.write(results)
        else:
            st.info("Enter a query to search memory.")

    st.markdown("---")
