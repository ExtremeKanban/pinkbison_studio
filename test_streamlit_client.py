"""
Test Streamlit WebSocket client integration.
"""

import streamlit as st
import time
import threading

def test_streamlit_client():
    """Test Streamlit WebSocket client."""
    print("\n🔍 Test 3: Streamlit WebSocket Client")
    print("-" * 40)
    
    try:
        # Mock Streamlit session state for testing
        if not hasattr(st, 'session_state'):
            class MockSessionState:
                def __init__(self):
                    self._state = {}
                
                def __getitem__(self, key):
                    return self._state.get(key)
                
                def __setitem__(self, key, value):
                    self._state[key] = value
                
                def __contains__(self, key):
                    return key in self._state
            
            st.session_state = MockSessionState()
        
        # Import and initialize client
        from ui.websocket_client import StreamlitWebSocketClient, initialize_websocket_client
        
        # Ensure WebSocket server is running
        from core.websocket_manager import WEBSOCKET_MANAGER
        if not WEBSOCKET_MANAGER.running:
            WEBSOCKET_MANAGER.start_server()
            time.sleep(1)
        
        # Test 3A: Client initialization
        print("Testing client initialization...")
        client = StreamlitWebSocketClient(project_name="test_client_project")
        
        if client:
            print("✅ StreamlitWebSocketClient created")
        else:
            print("❌ Failed to create client")
            return False
        
        # Test 3B: Client start/stop
        print("Testing client start/stop...")
        client.start()
        time.sleep(1)  # Give time to connect
        
        if client.running and client.thread and client.thread.is_alive():
            print("✅ Client started successfully")
        else:
            print("❌ Client failed to start")
            return False
        
        # Test 3C: Message storage
        print("Testing message storage...")
        
        # Simulate receiving a message
        test_message = {
            'type': 'test_message',
            'project': 'test_client_project',
            'data': {'test': 'data'},
            'timestamp': time.time()
        }
        
        # Store message using client method
        client._store_message_in_session(test_message)
        
        # Retrieve messages
        messages = StreamlitWebSocketClient.get_latest_messages("test_client_project")
        
        if messages and len(messages) > 0:
            print(f"✅ Messages stored and retrieved ({len(messages)} messages)")
            print(f"   Latest: {messages[-1].get('type')}")
        else:
            print("❌ Messages not stored properly")
            return False
        
        # Test 3D: Client stop
        print("Testing client stop...")
        client.stop()
        time.sleep(0.5)
        
        if not client.running:
            print("✅ Client stopped successfully")
        else:
            print("❌ Client failed to stop")
        
        # Test 3E: initialize_websocket_client function
        print("Testing initialize_websocket_client function...")
        client2 = initialize_websocket_client("test_project_2")
        
        if client2 and client2.running:
            print("✅ initialize_websocket_client works")
            client2.stop()
        else:
            print("❌ initialize_websocket_client failed")
        
        print("✅ Test 3 PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_streamlit_client()
    print("\n" + "=" * 40)
    if success:
        print("🎉 Streamlit WebSocket client is working!")
    else:
        print("💥 Streamlit WebSocket client has issues")
    exit(0 if success else 1)