"""
WebSocket client component for Streamlit.
"""

import streamlit as st
import json
import asyncio
import websockets
import threading
import time
from typing import Dict, Callable, Any


class StreamlitWebSocketClient:
    """
    WebSocket client that integrates with Streamlit session state.
    Runs in background thread.
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.ws_url = "ws://localhost:8765"
        self.running = False
        self.thread = None
        self.callbacks: Dict[str, Callable] = {}
        
        # Store in session state for persistence
        self.state_key = f"ws_client_{project_name}"
    
    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for specific event type."""
        self.callbacks[event_type] = callback
    
    def start(self):
        """Start WebSocket client in background."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        # Store in session state
        st.session_state[self.state_key] = self
    
    def stop(self):
        """Stop WebSocket client."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _run_loop(self):
        """Main WebSocket loop."""
        asyncio.run(self._async_run())
    
    async def _async_run(self):
        """Async WebSocket connection loop."""
        while self.running:
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    # Subscribe to project
                    await websocket.send(json.dumps({
                        'action': 'subscribe',
                        'project': self.project_name
                    }))
                    
                    # Wait for confirmation
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(response)
                        if data.get('type') == 'subscription_confirmed':
                            print(f"[WebSocket] Connected to {self.project_name}")
                    except asyncio.TimeoutError:
                        print(f"[WebSocket] No subscription confirmation")
                        continue
                    
                    # Listen for messages
                    while self.running:
                        try:
                            # Timeout to allow checking running flag
                            message = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=1.0
                            )
                            
                            # Process message
                            data = json.loads(message)
                            event_type = data.get('type')
                            
                            # Call registered callback
                            if event_type in self.callbacks:
                                self.callbacks[event_type](data)
                            
                            # Also store in session state for UI components
                            self._store_message_in_session(data)
                            
                        except asyncio.TimeoutError:
                            continue  # Check running flag and continue
                        except websockets.exceptions.ConnectionClosed:
                            print(f"[WebSocket] Connection closed, reconnecting...")
                            break  # Reconnect
                        
            except (websockets.exceptions.InvalidURI, ConnectionRefusedError) as e:
                print(f"[WebSocket] Server not available: {e}")
                await asyncio.sleep(5.0)  # Wait longer before retrying
            except Exception as e:
                print(f"[WebSocket] Connection error: {e}")
                # Wait before reconnecting
                await asyncio.sleep(2.0)
    
    def _store_message_in_session(self, data: dict):
        """Store latest messages in session state for UI access."""
        # Create session state key for this project
        messages_key = f"ws_messages_{self.project_name}"
        
        if messages_key not in st.session_state:
            st.session_state[messages_key] = []
        
        # Add new message
        st.session_state[messages_key].append(data)
        
        # Keep only last 50 messages
        if len(st.session_state[messages_key]) > 50:
            st.session_state[messages_key] = st.session_state[messages_key][-50:]
    
    @staticmethod
    def get_latest_messages(project_name: str, limit: int = 10):
        """Get latest WebSocket messages from session state."""
        messages_key = f"ws_messages_{project_name}"
        if messages_key in st.session_state:
            return st.session_state[messages_key][-limit:]
        return []
    
    @staticmethod
    def clear_messages(project_name: str):
        """Clear WebSocket messages from session state."""
        messages_key = f"ws_messages_{project_name}"
        if messages_key in st.session_state:
            st.session_state[messages_key] = []


def initialize_websocket_client(project_name: str):
    """
    Initialize WebSocket client for a project.
    Call this at the start of your UI.
    """
    # Start WebSocket server if not running
    try:
        from core.websocket_manager import WEBSOCKET_MANAGER
        WEBSOCKET_MANAGER.start_server()
    except Exception as e:
        print(f"[WebSocket] Could not start server: {e}")
        return None
    
    # Create or get existing client
    client_key = f"ws_client_{project_name}"
    
    if client_key not in st.session_state:
        client = StreamlitWebSocketClient(project_name)
        st.session_state[client_key] = client
        
        # Start the client
        client.start()
        
        # Register default callbacks
        def handle_eventbus_message(data):
            print(f"[WebSocket] EventBus message: {data.get('type')}")
        
        client.register_callback('eventbus_message', handle_eventbus_message)
        
        return client
    
    return st.session_state[client_key]