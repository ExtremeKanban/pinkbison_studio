"""
Real-time status component with WebSocket updates.
No page refresh needed - updates via WebSocket in real-time.
"""

import streamlit.components.v1 as components
import os

# Component directory
_component_dir = os.path.dirname(os.path.abspath(__file__))

# Declare component
_realtime_status = components.declare_component(
    "realtime_status",
    path=os.path.join(_component_dir, "frontend")
)

def realtime_status(project_name: str, key=None):
    """
    Render real-time status component with WebSocket updates.
    
    Updates automatically without page refresh when:
    - Pipeline status changes (idle → running → completed)
    - Progress updates (step 1/3, 2/3, etc.)
    - Events occur (agent messages, etc.)
    
    Args:
        project_name: Name of project to monitor
        key: Unique key for component instance
        
    Returns:
        Component value (can be used for callbacks if needed)
    """
    component_value = _realtime_status(
        project_name=project_name,
        key=key or f"realtime_{project_name}",
        default=None
    )
    
    return component_value