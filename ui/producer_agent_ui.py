"""
Producer Agent UI - Just renders pipeline controls
"""

import streamlit as st


def render_producer_agent_panel(producer):
    """
    Render inline pipeline controls
    
    Args:
        producer: ProducerAgent instance
    """
    from ui.pipeline_controls_ui import render_pipeline_controls_inline
    render_pipeline_controls_inline(producer.project_name)


def render_producer_agent_panel_by_name(project_name: str):
    """
    Alternative version that takes project_name instead of producer.
    
    Args:
        project_name: Name of the project
    """
    from ui.pipeline_controls_ui import render_pipeline_controls_inline
    render_pipeline_controls_inline(project_name)