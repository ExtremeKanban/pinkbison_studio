import streamlit as st
from task_manager import TaskManager
from agent_bus import GLOBAL_AGENT_BUS
from graph_store import GraphStore
from agents.producer import ProducerAgent


def render_intelligence_panel(project_name):
    graph = GraphStore(project_name)
    producer = ProducerAgent(project_name)
    tasks = TaskManager(project_name)

    with st.expander("🧠 Project Intelligence Panel (Read‑Only)", expanded=False):

        # Tasks
        st.markdown("### 📋 Task Queue")
        for t in tasks.get_all():
            st.write(t.__dict__)
            st.markdown("---")

        # Continuity
        st.markdown("### 🔍 Continuity Messages")
        try:
            msgs = producer.get_continuity_critiques()
        except Exception:
            msgs = []

        for m in msgs:
            st.write(m.__dict__)
            st.markdown("---")

        # Guidance
        st.markdown("### 🎬 Creative Director Guidance")
        try:
            guidance = GLOBAL_AGENT_BUS.get_for(project_name, "ALL")
            guidance = [m for m in guidance if getattr(m, "type", "") == "GUIDANCE"]
        except Exception:
            guidance = []

        for m in guidance:
            st.write(m.payload)
            st.markdown("---")

        # Canon Rules
        st.markdown("### 📜 Canon Rules")
        for rule in graph.get_canon_rules():
            st.write(rule)
            st.markdown("---")

        # Entities
        st.markdown("### 🧩 Graph Entities")
        for ent in graph.get_all_entities():
            st.write(ent)
            st.markdown("---")

        # Relationships
        st.markdown("### 🔗 Graph Relationships")
        for rel in graph.get_all_relationships():
            st.write(rel)
            st.markdown("---")
