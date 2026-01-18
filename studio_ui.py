"""
Main Streamlit UI entry point.
Updated to use standardized UI patterns from ui.common.
"""

import streamlit as st

from project_manager.state import initialize_session_state
from ui.sidebar import render_sidebar
from ui.common import get_producer
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
from ui.pipeline_history_ui import render_pipeline_history
from ui.canon_rules_ui import render_canon_rules
from ui.continuity_notes_ui import render_continuity_notes

# Initialize session state for project data
initialize_session_state()

# Ensure current_project always exists
if "current_project" not in st.session_state:
    st.session_state["current_project"] = "default_project"

# Sidebar (project switching happens here)
project_name = render_sidebar()

# Get ProducerAgent for this project (creates infrastructure automatically)
producer = get_producer(project_name)

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
render_pipeline_history(project_name)
render_canon_rules(project_name)
render_continuity_notes(project_name)