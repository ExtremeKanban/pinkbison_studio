"""
Common utilities for Streamlit UI components.
Provides standardized patterns for agent creation and session management.
"""

import streamlit as st
from typing import Optional
from agents.producer import ProducerAgent
from core.event_bus import EventBus
from core.audit_log import AuditLog
from config.settings import MODEL_CONFIG


def get_producer(project_name: str, model_mode: str = "fast") -> ProducerAgent:
    """
    Get or create ProducerAgent for current project.
    
    Handles session state management automatically. Creates new ProducerAgent
    if project changes or if it doesn't exist yet.
    
    Args:
        project_name: Name of the project
        model_mode: Model mode ("fast" or "high_quality")
        
    Returns:
        ProducerAgent instance for the project
        
    Example:
        >>> producer = get_producer("my_project")
        >>> result = producer.run_story_bible_pipeline(...)
    """
    # Check if we need to create/recreate
    needs_create = (
        "producer" not in st.session_state or
        st.session_state.get("_producer_project") != project_name
    )
    
    if needs_create:
        # Create infrastructure for this project
        event_bus = EventBus(project_name)
        audit_log = AuditLog(project_name)
        
        # Create ProducerAgent
        st.session_state["producer"] = ProducerAgent(
            project_name=project_name,
            event_bus=event_bus,
            audit_log=audit_log,
            fast_model_url=MODEL_CONFIG.fast_model_url,
            model_mode=model_mode,
        )
        st.session_state["_producer_project"] = project_name
        
        # Also update session state with EventBus and AuditLog
        st.session_state["event_bus"] = event_bus
        st.session_state["_event_bus_project"] = project_name
        st.session_state["audit_log"] = audit_log
        st.session_state["_audit_log_project"] = project_name
    
    return st.session_state["producer"]