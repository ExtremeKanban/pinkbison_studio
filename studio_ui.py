"""
Main Streamlit UI entry point - WITH PHASE 1 ENABLED
"""

import streamlit as st

# ============================================
# 1. SETUP - Minimal initialization
# ============================================
st.set_page_config(layout="wide")

# Basic session state
if "current_project" not in st.session_state:
    st.session_state["current_project"] = "default_project"
    st.session_state["project_genre"] = "Sci‑Fi"
    st.session_state["project_tone"] = "Epic, serious"
    st.session_state["project_themes"] = "Destiny, sacrifice, technology vs humanity"
    st.session_state["project_setting"] = "Far future galaxy"

# ============================================
# 2. IMPORTS - Include Phase 1
# ============================================
from ui.sidebar import render_sidebar
from ui.general_playground import render_general_playground
from ui.plot_architect_ui import render_plot_architect
from ui.worldbuilder_ui import render_worldbuilder
from ui.character_ui import render_character_agent
from ui.scene_pipeline_ui import render_scene_pipeline
from ui.story_bible_ui import render_story_bible_pipeline
from ui.memory_search_ui import render_memory_search
from ui.memory_add_ui import render_memory_add
from ui.memory_browser_ui import render_memory_browser
from ui.pipeline_history_ui import render_pipeline_history
from ui.canon_rules_ui import render_canon_rules
from ui.continuity_notes_ui import render_continuity_notes
from ui.multi_orchestrator_panel import render_multi_orchestrator_panel

# PHASE 1 IMPORTS
from ui.live_event_panel import render_live_event_panel
from ui.pipeline_controls_ui import render_pipeline_controls, render_pipeline_status_overview
from ui.feedback_injector_ui import render_feedback_injector
from ui.intelligence_panel import render_intelligence_panel
from ui.producer_agent_ui import render_producer_agent_panel_by_name

# ============================================
# 3. SIDEBAR - Get current project
# ============================================
project_name = render_sidebar()

# ============================================
# 4. INITIALIZE WEBSOCKET SYSTEM (AFTER project_name is defined!)
# ============================================
try:
    from ui.websocket_client import initialize_websocket_client
    # This will start WebSocket server and client
    client = initialize_websocket_client(project_name)
    if client and client.running:
        # Use session state to show toast only once
        if "websocket_toast_shown" not in st.session_state:
            st.toast("✅ WebSocket connected (real-time updates enabled)", icon="🔌")
            st.session_state.websocket_toast_shown = True
except Exception as e:
    print(f"[WebSocket] Initialization failed: {e}")
    # Continue without WebSockets

# ============================================
# 5. MAIN UI
# ============================================
st.title("PinkBison Creative Studio")
st.markdown("---")

# Show current project
st.info(f"**Current Project:** `{project_name}`")

# ============================================
# 6. PHASE 1: REAL-TIME STATUS BAR
# ============================================
st.header("📊 Real-time Dashboard")
render_pipeline_status_overview(project_name)
st.markdown("---")

# ============================================
# 7. RENDER WORKING COMPONENTS
# ============================================
render_general_playground(project_name)
render_plot_architect(project_name)
render_worldbuilder(project_name)
render_character_agent(project_name)
render_scene_pipeline(project_name)
render_story_bible_pipeline(project_name)

# ============================================
# 8. PRODUCER AGENT WITH PHASE 1
# ============================================
try:
    render_producer_agent_panel_by_name(project_name)
except Exception as e:
    st.error(f"Producer Agent Error: {str(e)}")

# ============================================
# 9. INTELLIGENCE PANEL WITH PHASE 1
# ============================================
try:
    render_intelligence_panel(project_name)
except Exception as e:
    st.error(f"Intelligence Panel Error: {str(e)}")
    with st.expander("🧠 Basic Intelligence Panel", expanded=False):
        st.info("Phase 1 intelligence features temporarily unavailable")

# ============================================
# 10. RENDER OTHER COMPONENTS
# ============================================
render_memory_search(project_name)
render_memory_add(project_name)
render_memory_browser(project_name)
render_pipeline_history(project_name)
render_canon_rules(project_name)
render_continuity_notes(project_name)
render_multi_orchestrator_panel(project_name)

# ============================================
# 11. PHASE 1: FEEDBACK INJECTION
# ============================================
st.markdown("---")
st.header("💬 Real-time Feedback")
render_feedback_injector(project_name)

# ============================================
# 12. FOOTER
# ============================================
st.markdown("---")
st.success("✅ Phase 1: Real-time workflow enabled!")