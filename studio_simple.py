"""
SIMPLE WORKING VERSION - No Phase 1, no complex initialization
"""

import streamlit as st

# Set page config first
st.set_page_config(layout="wide")

# Initialize basic session state
if "current_project" not in st.session_state:
    st.session_state["current_project"] = "default_project"
    st.session_state["project_genre"] = "Sci‑Fi"
    st.session_state["project_tone"] = "Epic, serious"
    st.session_state["project_themes"] = "Destiny, sacrifice"
    st.session_state["project_setting"] = "Far future galaxy"

# Simple sidebar
with st.sidebar:
    st.header("Project Management")
    
    # Project selection
    project_names = ["default_project", "test_project"]
    current = st.selectbox(
        "Active Project",
        project_names,
        index=0
    )
    st.session_state["current_project"] = current
    
    st.markdown("---")
    st.markdown("### Project Settings")
    
    # Project settings
    st.session_state["project_genre"] = st.text_input("Genre", st.session_state["project_genre"])
    st.session_state["project_tone"] = st.text_input("Tone", st.session_state["project_tone"])
    st.session_state["project_themes"] = st.text_area("Themes", st.session_state["project_themes"])
    st.session_state["project_setting"] = st.text_input("Setting", st.session_state["project_setting"])

# Main UI
st.title("PinkBison Creative Studio - Basic Working Version")
st.markdown("---")

# Only load the simplest, most reliable components
try:
    from ui.general_playground import render_general_playground
    st.header("General Playground")
    render_general_playground(st.session_state["current_project"])
except Exception as e:
    st.error(f"Playground error: {str(e)}")

# Simple test button
st.markdown("---")
st.header("Basic Test")

if st.button("Test Producer Agent"):
    try:
        from ui.common import get_producer
        producer = get_producer(st.session_state["current_project"])
        st.success("✓ Producer agent loaded successfully!")
        
        # Try to run a simple test
        st.info("Trying to generate a plot...")
        
        seed = "A space explorer discovers an ancient alien civilization"
        outline = "Test outline for verification"
        
        # This should work without Phase 1
        from agents.plot_architect import PlotArchitect
        from core.registry import REGISTRY
        
        project_name = st.session_state["current_project"]
        event_bus = REGISTRY.get_event_bus(project_name)
        audit_log = REGISTRY.get_audit_log(project_name)
        
        agent = PlotArchitect(
            project_name=project_name,
            event_bus=event_bus,
            audit_log=audit_log,
            fast_model_url="http://localhost:8000/v1/chat/completions",
            model_mode="fast"
        )
        
        st.success("✓ Plot architect agent created successfully!")
        
    except Exception as e:
        st.error(f"✗ Error: {str(e)}")

st.info("✅ UI is working! Phase 1 features are temporarily disabled for stability.")