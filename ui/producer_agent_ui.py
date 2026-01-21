"""
Producer Agent UI - Simplified, non-blocking only
"""

import streamlit as st


def render_producer_agent_panel(producer):
    """
    Simplified Producer Agent UI - Pipeline Controls only
    
    Args:
        producer: ProducerAgent instance
    """
    project_name = producer.project_name
    
    st.header("🎬 Producer Agent")
    
    # Instructions (collapsed by default)
    with st.expander("ℹ️ How to Use", expanded=False):
        st.markdown("""
        ### Quick Start
        
        1. **Enter your story idea** in the text area above
        2. **Select pipeline type** (Story Bible, Chapter, Full Story, or Director Mode)
        3. **Click "▶️ Start Pipeline"**
        4. **Watch real-time updates** in the Live Monitoring section below
        
        ### Pipeline Types
        
        - **📖 Story Bible**: Generates outline, world, and characters (fastest)
        - **📄 Single Chapter**: Generates one chapter from the story bible
        - **📚 Full Story**: Generates complete story with all chapters (slowest)
        - **🎬 Director Mode**: Advanced multi-pass refinement with continuity checks
        
        ### Tips
        
        - Start with Story Bible to quickly explore ideas
        - Use the Pause button if you want to inject feedback mid-generation
        - Stop button will halt execution immediately
        - All outputs are saved to project history automatically
        """)
    
    st.markdown("---")
    
    # Pipeline Controls (the main interface)
    from ui.pipeline_controls_ui import render_pipeline_controls
    render_pipeline_controls(project_name)


def render_producer_agent_panel_by_name(project_name: str):
    """
    Alternative version that takes project_name instead of producer.
    
    Args:
        project_name: Name of the project
    """
    try:
        from ui.common import get_producer
        producer = get_producer(project_name)
        render_producer_agent_panel(producer)
    except Exception as e:
        st.error(f"Could not load producer for {project_name}: {str(e)}")
        st.info("Try refreshing the page")