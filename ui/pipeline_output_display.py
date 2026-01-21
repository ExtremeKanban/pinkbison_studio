"""
Pipeline Output Display - Shows results immediately after generation
"""

import streamlit as st
from core.project_state import ProjectState
from datetime import datetime


def render_pipeline_output(project_name: str):
    """
    Display the most recent pipeline output right after pipeline controls.
    Updates automatically when pipeline completes.
    """
    state = ProjectState.load(project_name)
    
    if not state.pipeline_results:
        st.info("💡 Run a pipeline above to see outputs here")
        return
    
    # Get most recent result
    latest = state.pipeline_results[-1]
    result = latest.result
    pipeline_type = latest.pipeline_type
    
    timestamp = datetime.fromisoformat(latest.timestamp)
    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    # Use timestamp in keys to make them unique
    key_suffix = latest.timestamp.replace(":", "-").replace(".", "-")
    
    st.subheader(f"📋 Latest Output: {pipeline_type.replace('_', ' ').title()}")
    st.caption(f"Generated at {time_str}")
    
    # Story Bible Output
    if pipeline_type == "story_bible":
        if "outline" in result:
            with st.expander("📝 3-Act Outline", expanded=True):
                st.text_area("Outline", value=result["outline"], height=200, 
                           key=f"latest_outline_{key_suffix}", label_visibility="collapsed")
        
        if "world" in result:
            with st.expander("🌍 World Bible", expanded=True):
                st.text_area("World", value=result["world"], height=200,
                           key=f"latest_world_{key_suffix}", label_visibility="collapsed")
        
        if "characters" in result:
            with st.expander("👥 Character Bible", expanded=True):
                st.text_area("Characters", value=result["characters"], height=200,
                           key=f"latest_characters_{key_suffix}", label_visibility="collapsed")
    
    # Chapter Output
    elif pipeline_type == "chapter" and "chapter" in result:
        ch = result["chapter"]
        st.subheader(f"📖 {ch.get('title', 'Chapter')}")
        
        tabs = st.tabs(["✨ Final", "🔍 After Continuity", "📝 Raw"])
        
        with tabs[0]:
            st.text_area("Final", value=ch.get("final", ""), height=400,
                       key=f"latest_chapter_final_{key_suffix}", label_visibility="collapsed")
        
        with tabs[1]:
            st.text_area("After Continuity", value=ch.get("after_continuity", ""), height=400,
                       key=f"latest_chapter_continuity_{key_suffix}", label_visibility="collapsed")
        
        with tabs[2]:
            st.text_area("Raw", value=ch.get("raw", ""), height=400,
                       key=f"latest_chapter_raw_{key_suffix}", label_visibility="collapsed")
    
    # Full Story Output
    elif pipeline_type == "full_story":
        if "chapters" in result:
            st.write(f"📚 Generated {len(result['chapters'])} chapters")
            
            for ch_idx, ch in enumerate(result["chapters"]):
                with st.expander(f"Chapter {ch_idx + 1}: {ch.get('title', 'Untitled')}"):
                    st.text_area("Chapter Content", value=ch.get("final", ch.get("after_continuity", ch.get("raw", ""))),
                               height=300, key=f"latest_full_ch_{ch_idx}_{key_suffix}", label_visibility="collapsed")
        
        if "full_story" in result:
            with st.expander("📜 Complete Story"):
                st.text_area("Full Story", value=result["full_story"], height=500,
                           key=f"latest_full_story_{key_suffix}", label_visibility="collapsed")
    
    # Director Mode Output
    elif pipeline_type == "director":
        st.info("Director mode output - check full story section")
    
    # Raw JSON for debugging
    with st.expander("🔧 View Raw Data"):
        st.json(result)