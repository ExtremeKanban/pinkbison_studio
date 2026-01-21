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
st.markdown("---")

# ============================================
# 1. CREATIVE PIPELINE (Main Workflow)
# ============================================
st.header("Creative Pipeline")

# Story idea input
st.text_area(
    "Story Idea",
    key="producer_seed_idea",
    height=120,
    placeholder="A retired astronaut discovers an alien signal that only she can decode..."
)

# Pipeline controls with real-time updates
from ui.producer_agent_ui import render_producer_agent_panel_by_name
render_producer_agent_panel_by_name(project_name)

st.markdown("---")

# ============================================
# 2. LIVE MONITORING
# ============================================
st.header("📊 Live Monitoring")

try:
    from ui.intelligence_panel import render_intelligence_panel  
    render_intelligence_panel(project_name)
except Exception as e:
    st.error(f"Intelligence Panel Error: {str(e)}")

st.markdown("---")

# ============================================
# 3. GENERATED CONTENT
# ============================================
st.header("📚 Generated Content")

from ui.pipeline_history_ui import render_pipeline_history
render_pipeline_history(project_name)

st.markdown("---")

# ============================================
# 4. PROJECT KNOWLEDGE
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
# 5. ADVANCED TOOLS (Collapsed)
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