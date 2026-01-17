import streamlit as st
from agents.producer import ProducerAgent
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session
from core.event_bus import EventBus
from core.audit_log import AuditLog
from config.settings import MODEL_CONFIG

def render_plot_architect(project_name):
    # Ensure ProducerAgent exists with EventBus
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
    
    st.header("Plot Architect Agent")

    st.text_area("Seed idea for the Plot Architect", key="seed_idea_plot")

    auto_memory = st.checkbox(
        "Auto-store Plot Architect facts in memory",
        value=False,
        key="auto_memory_plot",
    )

    if st.button("Generate 3‑Act Outline"):
        seed = st.session_state["seed_idea_plot"].strip()
        if seed:
            # Create fresh agent instance
            agent = producer.agent_factory.create_plot_architect()
            
            outline = agent.run(
                seed,
                st.session_state["project_genre"],
                st.session_state["project_tone"],
                st.session_state["project_themes"],
                st.session_state["project_setting"],
                auto_memory=auto_memory,
            )
            st.session_state["outline"] = outline
            st.subheader("3‑Act Outline")
            st.write(outline)

            save_project_state(project_name, extract_state_from_session())
        else:
            st.info("Enter a seed idea for the Plot Architect.")

    st.markdown("---")