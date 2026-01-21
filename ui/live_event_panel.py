"""
Real-time event stream with WebSocket integration.
"""

import streamlit as st
import time
from datetime import datetime
from typing import List, Dict, Any

from core.registry import REGISTRY
from ui.websocket_client import initialize_websocket_client, StreamlitWebSocketClient


def render_live_event_panel(project_name: str):
    """
    Render live event stream with WebSocket real-time updates.
    """
    # Initialize WebSocket client
    client = initialize_websocket_client(project_name)
    
    with st.expander("📡 Live Event Stream", expanded=True):
        
        # Status indicator
        if client and client.running:
            st.success("✅ Connected (real-time)")
        else:
            st.warning("⚠️ Polling mode (no WebSocket)")
        
        # Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            event_limit = st.selectbox(
                "Max events",
                options=[10, 20, 50, 100],
                index=1,
                key=f"live_events_limit_{project_name}"
            )
        
        with col2:
            # Show WebSocket status
            if client and client.running:
                st.metric("Connection", "Active")
            else:
                st.metric("Connection", "Polling")
        
        # Control buttons
        col_refresh, col_clear = st.columns(2)
        
        with col_refresh:
            if st.button("🔄 Refresh", key=f"refresh_events_{project_name}"):
                st.rerun()
        
        with col_clear:
            if st.button("🗑️ Clear", key=f"clear_events_{project_name}"):
                if client:
                    StreamlitWebSocketClient.clear_messages(project_name)
                st.rerun()
        
        st.markdown("---")
        
        # Display events from multiple sources
        display_combined_events(project_name, event_limit)
        
        # Auto-refresh note
        if client and client.running:
            st.caption("🔔 Events update in real-time via WebSocket")
        else:
            st.caption("⏱️ Click Refresh to update events")


def display_combined_events(project_name: str, limit: int):
    """
    Display events from both EventBus buffer and WebSocket messages.
    """
    # Get EventBus events
    event_bus = REGISTRY.get_event_bus(project_name)
    bus_events = list(event_bus.buffer)[-limit:]
    
    # Get WebSocket events
    ws_events = StreamlitWebSocketClient.get_latest_messages(project_name, limit)
    
    # Combine and sort by timestamp
    all_events = []
    
    # Add EventBus events
    for event in bus_events:
        all_events.append({
            'source': 'eventbus',
            'type': event.type,
            'sender': event.sender,
            'recipient': event.recipient,
            'payload': event.payload,
            'timestamp': event.timestamp
        })
    
    # Add WebSocket events
    for event in ws_events:
        if event.get('type') == 'eventbus_message':
            data = event.get('data', {})
            all_events.append({
                'source': 'websocket',
                'type': data.get('event_type'),
                'sender': data.get('sender'),
                'recipient': data.get('recipient'),
                'payload': data.get('payload'),
                'timestamp': event.get('timestamp')
            })
    
    # Sort by timestamp (newest first)
    all_events.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # Display
    if not all_events:
        st.info("No events yet. Start a pipeline to see live events.")
        return
    
    # Limit display
    display_events = all_events[:limit]
    
    for idx, event in enumerate(display_events):
        render_event_card(event, idx, project_name)


def render_event_card(event: Dict[str, Any], idx: int, project_name: str):
    """
    Render a single event as a styled card.
    """
    # Determine color based on event type
    event_type = event.get('type', '').lower()
    
    if "error" in event_type:
        border_color = "#ff4444"
        icon = "❌"
        source_badge = "🔄" if event.get('source') == 'websocket' else "💾"
    elif "complete" in event_type or "success" in event_type:
        border_color = "#44ff44"
        icon = "✅"
        source_badge = "🔄" if event.get('source') == 'websocket' else "💾"
    elif "progress" in event_type:
        border_color = "#4488ff"
        icon = "📊"
        source_badge = "🔄" if event.get('source') == 'websocket' else "💾"
    elif "paused" in event_type or "stopped" in event_type:
        border_color = "#ffaa44"
        icon = "⏸️"
        source_badge = "🔄" if event.get('source') == 'websocket' else "💾"
    elif "start" in event_type:
        border_color = "#44ffaa"
        icon = "🚀"
        source_badge = "🔄" if event.get('source') == 'websocket' else "💾"
    else:
        border_color = "#888888"
        icon = "📝"
        source_badge = "🔄" if event.get('source') == 'websocket' else "💾"
    
    # Format timestamp
    timestamp = event.get('timestamp', time.time())
    try:
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%H:%M:%S.%f")[:-3]  # Milliseconds
    except:
        time_str = "Unknown"
    
    # Create card
    with st.container():
        st.markdown(f"""
        <div style="
            border-left: 4px solid {border_color};
            background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            padding: 12px;
            margin: 8px 0;
            border-radius: 4px;
            font-family: monospace;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{icon} {event.get('type', 'Unknown')}</strong>
                    <span style="color: #888; font-size: 0.9em; margin-left: 10px;">
                        {time_str}
                    </span>
                </div>
                <div style="color: #aaa; font-size: 0.9em;">
                    {source_badge} {event.get('sender', 'Unknown')} → {event.get('recipient', 'Unknown')}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Payload
        payload = event.get('payload')
        if payload:
            import json
            try:
                payload_str = json.dumps(payload, indent=2)
                with st.expander("Payload", expanded=False):
                    st.code(payload_str, language="json")
            except:
                pass
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_pipeline_status_card(project_name: str):
    """
    Render a status card for the current pipeline.
    """
    try:
        # Get pipeline controller
        from core.registry import REGISTRY
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        status = pipeline_controller.get_status()
        
        # Status indicators
        status_icons = {
            "idle": "💤",
            "running": "⚡",
            "paused": "⏸️",
            "stopped": "⏹️",
            "completed": "✅",
            "error": "❌"
        }
        
        status_icon = status_icons.get(status["status"], "❓")
        
        # Create status card
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(f"### {status_icon}")
            st.caption(f"Status: {status['status']}")
        
        with col2:
            if status["progress"]["percent_complete"] > 0:
                st.progress(
                    status["progress"]["percent_complete"] / 100,
                    text=f"{status['progress']['current_step']}"
                )
                st.caption(
                    f"Step {status['progress']['step_number']}/"
                    f"{status['progress']['total_steps']} - "
                    f"{status['progress']['percent_complete']:.1f}%"
                )
            else:
                st.caption("No active pipeline")
        
        with col3:
            stats = status.get("feedback_stats", {})
            if stats.get("unprocessed", 0) > 0:
                st.markdown(f"📬 {stats['unprocessed']} feedback")
            else:
                st.caption("No pending feedback")
        
        # Show current step description if available
        if status["progress"]["step_description"]:
            with st.expander("Current Step Details", expanded=False):
                st.write(status["progress"]["step_description"])
        
    except Exception as e:
        st.info("Pipeline controller not initialized")