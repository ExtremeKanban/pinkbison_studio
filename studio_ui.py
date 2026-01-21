"""
PinkBison Creative Studio - Main UI
Clean, modern interface with real-time WebSocket updates
"""

import streamlit as st

st.set_page_config(layout="wide", page_title="PinkBison Studio")

# ============================================
# INITIALIZATION
# ============================================
if "current_project" not in st.session_state:
    st.session_state["current_project"] = "default_project"
    st.session_state["project_genre"] = "Sci-Fi"
    st.session_state["project_tone"] = "Epic, serious"
    st.session_state["project_themes"] = "Destiny, sacrifice, technology vs humanity"
    st.session_state["project_setting"] = "Far future galaxy"

from ui.sidebar import render_sidebar
project_name = render_sidebar()

# Initialize WebSocket
try:
    from ui.websocket_client import initialize_websocket_client
    ws_client = initialize_websocket_client(project_name)
    if ws_client and ws_client.running:
        if "websocket_toast_shown" not in st.session_state:
            st.toast("✅ WebSocket connected", icon="🔌")
            st.session_state.websocket_toast_shown = True
except Exception as e:
    print(f"[WebSocket] Initialization failed: {e}")

# ============================================
# HEADER
# ============================================
st.title("🎬 PinkBison Creative Studio")
st.caption(f"**Project:** {project_name}")

# How to Use (right after project name)
with st.expander("ℹ️ How to Use", expanded=False):
    st.markdown("""
    ### Quick Start
    
    1. **Enter your story idea** below
    2. **Select pipeline type** and click **Start**
    3. **Watch real-time updates** as your story is generated
    
    ### Pipeline Types
    
    - **📖 Story Bible**: Generates outline, world, and characters (fastest)
    - **📄 Single Chapter**: Generates one chapter from the story bible
    - **📚 Full Story**: Generates complete story with all chapters (slowest)
    - **🎬 Director Mode**: Advanced multi-pass refinement with continuity checks
    """)

st.markdown("---")

# ============================================
# MAIN WORKFLOW
# ============================================

# Story idea input (bigger, more prominent)
st.text_area(
    "Story Idea",
    key="producer_seed_idea",
    height=150,
    placeholder="A retired astronaut discovers an alien signal that only she can decode..."
)

# Pipeline controls inline
from ui.pipeline_controls_ui import render_pipeline_controls_inline
render_pipeline_controls_inline(project_name)

# Auto-refresh when pipeline completes
from core.registry import REGISTRY
pc = REGISTRY.get_pipeline_controller(project_name)
status = pc.get_status()

# Show errors
if status["status"] == "error":
    st.error("❌ **Pipeline Error:**")
    if status.get("current_task"):
        st.code(status["current_task"])

# Auto-rerun when pipeline completes
if status["status"] == "completed":
    if f"pipeline_completed_{project_name}" not in st.session_state:
        st.session_state[f"pipeline_completed_{project_name}"] = True
        st.rerun()
elif status["status"] != "completed":
    st.session_state.pop(f"pipeline_completed_{project_name}", None)

st.markdown("---")

# Show latest output immediately
from ui.pipeline_output_display import render_pipeline_output
render_pipeline_output(project_name)

# DEBUG: Check if results are actually saved
from core.project_state import ProjectState
state = ProjectState.load(project_name)
st.write(f"DEBUG: Found {len(state.pipeline_results)} pipeline results in state")
if state.pipeline_results:
    latest = state.pipeline_results[-1]
    st.write(f"DEBUG: Latest result type: {latest.pipeline_type}, has {len(latest.result)} keys")

st.markdown("---")

# ============================================
# LIVE MONITORING
# ============================================
st.header("📊 Live Monitoring")

try:
    from ui.intelligence_panel import render_intelligence_panel  
    render_intelligence_panel(project_name)
except Exception as e:
    st.error(f"Intelligence Panel Error: {str(e)}")

st.markdown("---")

# ============================================
# GENERATED CONTENT
# ============================================
st.header("📚 Generated Content")

from ui.pipeline_history_ui import render_pipeline_history
render_pipeline_history(project_name)

st.markdown("---")

# ============================================
# PROJECT KNOWLEDGE
# ============================================
st.header("🧠 Project Knowledge")

tab1, tab2 = st.tabs(["Memory", "Canon Rules"])

with tab1:
    from ui.memory_browser_ui import render_memory_browser
    render_memory_browser(project_name)

with tab2:
    from ui.canon_rules_ui import render_canon_rules
    render_canon_rules(project_name)

st.markdown("---")

# ============================================
# ADVANCED TOOLS (Collapsed)
# ============================================
with st.expander("⚙️ Advanced Tools", expanded=False):
    from ui.memory_search_ui import render_memory_search
    from ui.memory_add_ui import render_memory_add
    from ui.continuity_notes_ui import render_continuity_notes
    
    st.subheader("Memory Management")
    col1, col2 = st.columns(2)
    
    with col1:
        render_memory_search(project_name)
    
    with col2:
        render_memory_add(project_name)
    
    st.markdown("---")
    st.subheader("Continuity Notes")
    render_continuity_notes(project_name)

st.markdown("---")

# ============================================
# FOOTER
# ============================================
from ui.pipeline_controls_ui import render_pipeline_status_overview
render_pipeline_status_overview(project_name)