import streamlit as st
from agents.producer import ProducerAgent
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session
from core.event_bus import EventBus
from core.audit_log import AuditLog
from config.settings import MODEL_CONFIG

def render_worldbuilder(project_name):
    # Ensure ProducerAgent exists
    if "producer" not in st.session_state:
        fast_model_url = MODEL_CONFIG.fast_model_url
        model_mode = "fast"
        
        event_bus = EventBus(project_name)
        audit_log = AuditLog(project_name)

        st.session_state["producer"] = ProducerAgent(
            project_name=project_name,
            event_bus=event_bus,
            audit_log=audit_log,
            fast_model_url=fast_model_url,
            model_mode=model_mode,
        )

    producer = st.session_state["producer"]

    st.header("Worldbuilder Agent")

    st.text_area("Outline for Worldbuilder", key="outline_for_world")

    auto_memory = st.checkbox(
        "Auto-store world facts in memory",
        value=True,
        key="auto_memory_world",
    )

    if st.button("Generate World Bible"):
        outline = st.session_state["outline_for_world"].strip()
        if outline:
            # Create fresh agent instance
            agent = producer.agent_factory.create_worldbuilder()
            
            world_doc = agent.run(
                outline=outline,
                genre=st.session_state["project_genre"],
                tone=st.session_state["project_tone"],
                themes=st.session_state["project_themes"],
                setting=st.session_state["project_setting"],
                auto_memory=auto_memory,
            )
            st.session_state["world"] = world_doc
            st.subheader("World Bible")
            st.write(world_doc)

            save_project_state(project_name, extract_state_from_session())
        else:
            st.info("Provide at least an outline for the Worldbuilder.")

    st.markdown("---")