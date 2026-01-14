import streamlit as st
from memory_store import MemoryStore


def render_memory_browser(project_name):
    memory = MemoryStore(project_name)

    with st.expander("🧠 Memory Browser", expanded=False):
        if st.button("Refresh Memory Browser", key="refresh_memory"):
            st.rerun()

        all_memories = memory.get_all()
        if all_memories:
            for idx, text in all_memories:
                with st.expander(f"Memory #{idx}"):
                    st.write(text)
                    if st.button(f"Delete Memory #{idx}", key=f"delete_{idx}"):
                        memory.delete(idx)
                        st.rerun()
        else:
            st.write("No memories stored yet.")
