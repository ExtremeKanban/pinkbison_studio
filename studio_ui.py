import streamlit as st

from project_manager.state import initialize_session_state
from ui.sidebar import render_sidebar
from ui.general_playground import render_general_playground
from ui.plot_architect_ui import render_plot_architect
from ui.worldbuilder_ui import render_worldbuilder
from ui.character_ui import render_character_agent
from ui.scene_pipeline_ui import render_scene_pipeline
from ui.story_bible_ui import render_story_bible_pipeline
from ui.producer_agent_ui import render_producer_agent_panel   # <-- NEW IMPORT
from ui.intelligence_panel import render_intelligence_panel
from ui.memory_search_ui import render_memory_search
from ui.memory_add_ui import render_memory_add
from ui.memory_browser_ui import render_memory_browser
from agents.producer import ProducerAgent
from intelligence_bus import IntelligenceBus

# Initialize session state for project data
initialize_session_state()

# Ensure current_project always exists
if "current_project" not in st.session_state:
    st.session_state["current_project"] = "default_project"

# Sidebar (project switching happens here)
project_name = render_sidebar()



fast_model_url = "http://localhost:8000/v1/chat/completions"
model_mode = "fast"

bus = IntelligenceBus(project_name)

producer = ProducerAgent(
    project_name=project_name,
    intelligence_bus=bus,
    fast_model_url=fast_model_url,
    model_mode=model_mode,
)



st.title("PinkBison Creative Studio")
st.markdown("---")

# Panels rendered in sequence (your existing structure)
render_general_playground(project_name)
render_plot_architect(project_name)
render_worldbuilder(project_name)
render_character_agent(project_name)
render_scene_pipeline(project_name)
render_story_bible_pipeline(project_name)

# NEW: Producer Agent panel (autonomous director)
render_producer_agent_panel(producer)

render_intelligence_panel(producer)
render_memory_search(project_name)
render_memory_add(project_name)
render_memory_browser(project_name)
