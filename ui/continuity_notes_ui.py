"""
Continuity Notes UI - View continuity check history
"""

import streamlit as st
from core.project_state import ProjectState
from datetime import datetime


def render_continuity_notes(project_name: str):
    """Render continuity notes viewer"""
    st.header("📋 Continuity Notes")
    
    state = ProjectState.load(project_name)
    
    if not state.continuity_notes:
        st.info("No continuity notes yet. Run a pipeline with continuity checks enabled.")
        st.markdown("""
        **How continuity notes are created:**
        1. Enable "Run Continuity checks" in Producer Agent
        2. Run any pipeline (Chapter, Full Story, or Director Mode)
        3. ContinuityAgent will check each scene and save notes
        
        **Continuity notes help track:**
        - Plot consistency issues found
        - Character behavior checks
        - World rule violations detected
        - Timeline contradictions
        """)
        return
    
    # Summary stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Notes", len(state.continuity_notes))
    with col2:
        sources = set(n.source for n in state.continuity_notes)
        st.metric("Sources", len(sources))
    
    st.markdown("---")
    
    # Filter options
    all_sources = sorted(set(n.source for n in state.continuity_notes))
    filter_source = st.selectbox(
        "Filter by Source",
        ["All"] + all_sources,
        key="continuity_filter"
    )
    
    # Filter notes
    if filter_source == "All":
        filtered_notes = state.continuity_notes
    else:
        filtered_notes = [n for n in state.continuity_notes if n.source == filter_source]
    
    st.write(f"Showing {len(filtered_notes)} / {len(state.continuity_notes)} notes")
    
    # Display notes in reverse chronological order
    for idx, note in enumerate(reversed(filtered_notes)):
        timestamp = datetime.fromisoformat(note.timestamp)
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        with st.expander(
            f"#{len(filtered_notes) - idx}: {note.source} - {time_str}",
            expanded=(idx == 0)
        ):
            st.write(note.note)
    
    # Clear option
    st.markdown("---")
    st.markdown("### 🗑️ Manage Notes")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Clear all continuity notes (cannot be undone)")
    with col2:
        if st.button("Clear Notes", type="secondary"):
            state.continuity_notes = []
            state.save()
            st.success("Notes cleared!")
            st.rerun()