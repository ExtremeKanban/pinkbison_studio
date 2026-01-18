"""
Pipeline History UI - View past pipeline results
"""

import streamlit as st
from core.project_state import ProjectState
from datetime import datetime


def render_pipeline_history(project_name: str):
    """Render pipeline history viewer"""
    st.header("🕒 Pipeline History")
    
    state = ProjectState.load(project_name)
    
    if not state.pipeline_results:
        st.info("No pipeline results yet. Run a pipeline to see history here.")
        return
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Runs", len(state.pipeline_results))
    with col2:
        types = set(pr.pipeline_type for pr in state.pipeline_results)
        st.metric("Pipeline Types", len(types))
    with col3:
        if state.pipeline_results:
            latest = state.pipeline_results[-1]
            latest_time = datetime.fromisoformat(latest.timestamp)
            st.metric("Last Run", latest_time.strftime("%Y-%m-%d %H:%M"))
    
    st.markdown("---")
    
    # Filter options
    all_types = sorted(set(pr.pipeline_type for pr in state.pipeline_results))
    filter_type = st.selectbox(
        "Filter by Pipeline Type",
        ["All"] + all_types,
        key="pipeline_history_filter"
    )
    
    # Filter results
    if filter_type == "All":
        filtered_results = state.pipeline_results
    else:
        filtered_results = [pr for pr in state.pipeline_results if pr.pipeline_type == filter_type]
    
    st.write(f"Showing {len(filtered_results)} results")
    
    # Show results in reverse chronological order
    for idx, pr in enumerate(reversed(filtered_results)):
        timestamp = datetime.fromisoformat(pr.timestamp)
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        with st.expander(
            f"#{len(filtered_results) - idx}: {pr.pipeline_type} - {time_str}",
            expanded=(idx == 0)
        ):
            result = pr.result
            
            if "outline" in result:
                st.subheader("📝 Outline")
                st.text_area("Outline", value=result["outline"], height=200, 
                           key=f"history_outline_{idx}_{pr.timestamp}", label_visibility="collapsed")
            
            if "world" in result:
                st.subheader("🌍 World Bible")
                st.text_area("World", value=result["world"], height=200,
                           key=f"history_world_{idx}_{pr.timestamp}", label_visibility="collapsed")
            
            if "characters" in result:
                st.subheader("👥 Characters")
                st.text_area("Characters", value=result["characters"], height=200,
                           key=f"history_characters_{idx}_{pr.timestamp}", label_visibility="collapsed")
            
            if "chapter" in result:
                ch = result["chapter"]
                st.subheader(f"📖 {ch.get('title', 'Chapter')}")
                tabs = st.tabs(["Raw", "After Continuity", "Final"])
                with tabs[0]:
                    st.write(ch.get("raw", ""))
                with tabs[1]:
                    st.write(ch.get("after_continuity", ""))
                with tabs[2]:
                    st.write(ch.get("final", ""))
            
            if "chapters" in result:
                st.subheader("📚 Chapters")
                st.write(f"Total chapters: {len(result['chapters'])}")
                for ch_idx, ch in enumerate(result["chapters"]):
                    with st.expander(f"Chapter {ch_idx + 1}: {ch.get('title', 'Untitled')}"):
                        st.write(ch.get("final", ch.get("after_continuity", ch.get("raw", ""))))
            
            if "full_story" in result:
                st.subheader("📜 Full Story")
                st.text_area("Full Story", value=result["full_story"], height=400,
                           key=f"history_full_{idx}_{pr.timestamp}", label_visibility="collapsed")
            
            with st.expander("View Raw JSON"):
                st.json(result)
    
    # Cleanup option
    st.markdown("---")
    st.markdown("### 🗑️ Manage History")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Clear all pipeline history (cannot be undone)")
    with col2:
        if st.button("Clear History", type="secondary"):
            state.pipeline_results = []
            state.save()
            st.success("History cleared!")
            st.rerun()