"""
Main Streamlit UI entry point.
Updated to use EventBus + AuditLog architecture.
"""

import streamlit as st

from project_manager.state import initialize_session_state
from ui.sidebar import render_sidebar
from ui.general_playground import render_general_playground
from ui.plot_architect_ui import render_plot_architect
from ui.worldbuilder_ui import render_worldbuilder
from ui.character_ui import render_character_agent
from ui.scene_pipeline_ui import render_scene_pipeline
from ui.story_bible_ui import render_story_bible_pipeline
from ui.producer_agent_ui import render_producer_agent_panel
from ui.intelligence_panel import render_intelligence_panel
from ui.memory_search_ui import render_memory_search
from ui.memory_add_ui import render_memory_add
from ui.memory_browser_ui import render_memory_browser

from agents.producer import ProducerAgent
from core.event_bus import EventBus
from core.audit_log import AuditLog

# Initialize session state for project data
initialize_session_state()

# Ensure current_project always exists
if "current_project" not in st.session_state:
    st.session_state["current_project"] = "default_project"

# Sidebar (project switching happens here)
project_name = render_sidebar()

# Initialize EventBus and AuditLog for this project
if "event_bus" not in st.session_state or st.session_state.get("_event_bus_project") != project_name:
    st.session_state["event_bus"] = EventBus(project_name)
    st.session_state["_event_bus_project"] = project_name

if "audit_log" not in st.session_state or st.session_state.get("_audit_log_project") != project_name:
    st.session_state["audit_log"] = AuditLog(project_name)
    st.session_state["_audit_log_project"] = project_name

event_bus = st.session_state["event_bus"]
audit_log = st.session_state["audit_log"]

# Model configuration
fast_model_url = "http://localhost:8000/v1/chat/completions"
model_mode = "fast"

# Create ProducerAgent for this project
if "producer" not in st.session_state or st.session_state.get("_producer_project") != project_name:
    st.session_state["producer"] = ProducerAgent(
        project_name=project_name,
        event_bus=event_bus,
        audit_log=audit_log,
        fast_model_url=fast_model_url,
        model_mode=model_mode,
    )
    st.session_state["_producer_project"] = project_name

producer = st.session_state["producer"]

# Main UI
st.title("PinkBison Creative Studio")
st.markdown("---")

# Render panels
render_general_playground(project_name)
render_plot_architect(project_name)
render_worldbuilder(project_name)
render_character_agent(project_name)
render_scene_pipeline(project_name)
render_story_bible_pipeline(project_name)
render_producer_agent_panel(producer)
render_intelligence_panel(producer)
render_memory_search(project_name)
render_memory_add(project_name)
render_memory_browser(project_name)