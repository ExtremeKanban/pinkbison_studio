"""
Test WebSocket updates in a live UI.
"""

import streamlit as st
import time
import threading
from core.event_bus import EventBus
from core.websocket_manager import WEBSOCKET_MANAGER
from ui.websocket_client import initialize_websocket_client, StreamlitWebSocketClient

def test_live_updates():
    """Test that UI receives live WebSocket updates."""
    st.set_page_config(layout="wide")
    st.title("🌐 Live WebSocket UI Test")
    
    # Initialize
    project_name = "live_test"
    
    # Start WebSocket if not running
    if not WEBSOCKET_MANAGER.running:
        WEBSOCKET_MANAGER.start_server()
        time.sleep(1)
    
    # Initialize client
    client = initialize_websocket_client(project_name)
    
    # Create EventBus
    event_bus = EventBus(project_name=project_name)
    
    # Status
    col1, col2 = st.columns(2)
    with col1:
        st.metric("WebSocket Server", "✅ Running" if WEBSOCKET_MANAGER.running else "❌ Stopped")
    with col2:
        st.metric("Client Connection", "✅ Connected" if client and client.running else "❌ Disconnected")
    
    st.markdown("---")
    
    # Test controls
    st.subheader("🧪 Test Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Send Test Event", key="send_test"):
            event_bus.publish(
                sender="test_user",
                recipient="all",
                event_type="test_event",
                payload={"message": "Hello from UI test!", "timestamp": time.time()}
            )
            st.success("Event sent!")
    
    with col2:
        if st.button("🔄 Send Progress Update", key="send_progress"):
            event_bus.publish(
                sender="pipeline",
                recipient="ui",
                event_type="progress_update",
                payload={"progress": 75, "step": "Processing", "details": "Test in progress"}
            )
            st.success("Progress update sent!")
    
    with col3:
        if st.button("🚀 Send Pipeline Complete", key="send_complete"):
            event_bus.publish(
                sender="producer",
                recipient="all",
                event_type="pipeline_complete",
                payload={"success": True, "results": 10, "duration": 5.2}
            )
            st.success("Completion event sent!")
    
    st.markdown("---")
    
    # Live message display
    st.subheader("📡 Live WebSocket Messages")
    
    # Refresh button
    if st.button("🔄 Refresh Messages", key="refresh_messages"):
        st.rerun()
    
    # Show messages
    messages = StreamlitWebSocketClient.get_latest_messages(project_name)
    
    if not messages:
        st.info("No WebSocket messages yet. Click buttons above to send test events.")
    else:
        st.write(f"Showing {len(messages)} latest messages:")
        
        for idx, msg in enumerate(reversed(messages[-10:])):  # Last 10 messages
            with st.expander(f"{msg.get('type')} - {msg.get('timestamp', '')}", expanded=idx<2):
                st.json(msg)
    
    st.markdown("---")
    
    # Auto-simulate events
    st.subheader("🤖 Auto Simulation")
    
    auto_simulate = st.checkbox("Enable auto-simulation", value=False)
    
    if auto_simulate:
        # Store simulation state in session
        if "simulation_counter" not in st.session_state:
            st.session_state.simulation_counter = 0
        
        # Simulate events
        event_types = [
            "agent_start", "progress_update", "memory_store", 
            "graph_update", "feedback_received", "pipeline_step"
        ]
        
        # Send simulated event
        if st.session_state.simulation_counter % 10 == 0:  # Every 10 refreshes
            import random
            event_type = random.choice(event_types)
            event_bus.publish(
                sender=f"simulated_agent_{random.randint(1, 5)}",
                recipient="all",
                event_type=event_type,
                payload={
                    "simulation": True,
                    "counter": st.session_state.simulation_counter,
                    "data": f"Simulated {event_type} event",
                    "random_value": random.random()
                }
            )
        
        st.session_state.simulation_counter += 1
        
        # Auto-refresh
        time.sleep(1)
        st.rerun()
    
    # Instructions
    with st.expander("📖 How to Use This Test"):
        st.markdown("""
        1. **WebSocket Server**: Should show "✅ Running"
        2. **Client Connection**: Should show "✅ Connected"
        3. **Send Test Events**: Click buttons to send events
        4. **Live Messages**: Watch events appear in real-time
        5. **Auto Simulation**: Enable to see continuous events
        
        **Expected Behavior**:
        - Events should appear immediately in the Live Messages section
        - No page reload should be needed
        - WebSocket connection should stay active
        
        **If messages don't appear**:
        1. Check WebSocket server is running
        2. Check client is connected
        3. Wait 1-2 seconds after sending events
        """)
    
    return client is not None and client.running

if __name__ == "__main__":
    test_live_updates()