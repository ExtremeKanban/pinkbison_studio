"""
Test the complete WebSocket system with EventBus integration.
"""

import asyncio
import json
import time
import threading
from core.event_bus import EventBus
from core.websocket_manager import WEBSOCKET_MANAGER
from ui.websocket_client import StreamlitWebSocketClient
import streamlit as st

def mock_streamlit_session():
    """Mock Streamlit session state for testing."""
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
            
            def get(self, key, default=None):
                return self._state.get(key, default)
        
        st.session_state = MockSessionState()

def test_eventbus_websocket_integration():
    """Test EventBus publishing to WebSocket."""
    print("\n🔍 Test 1: EventBus → WebSocket Integration")
    print("-" * 40)
    
    try:
        # Mock Streamlit
        mock_streamlit_session()
        
        # Ensure server is running
        if not WEBSOCKET_MANAGER.running:
            WEBSOCKET_MANAGER.start_server()
            time.sleep(2)
        
        # Create EventBus
        event_bus = EventBus(project_name="integration_test")
        print("✅ EventBus created")
        
        # Variables to capture WebSocket messages
        received_messages = []
        
        # WebSocket client to listen
        async def websocket_listener():
            import websockets
            uri = "ws://localhost:8765"
            try:
                async with websockets.connect(uri, ping_interval=None) as websocket:
                    # Subscribe
                    await websocket.send(json.dumps({
                        'action': 'subscribe',
                        'project': 'integration_test'
                    }))
                    
                    # Get subscription confirmation
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"✅ Subscription confirmed: {json.loads(response).get('type')}")
                    
                    # Listen for 3 seconds
                    start_time = time.time()
                    while time.time() - start_time < 3:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                            data = json.loads(message)
                            received_messages.append(data)
                            print(f"📨 Received: {data.get('type')}")
                        except asyncio.TimeoutError:
                            continue
                            
            except Exception as e:
                print(f"❌ WebSocket listener error: {e}")
        
        # Start listener in background
        listener_thread = threading.Thread(
            target=lambda: asyncio.run(websocket_listener()),
            daemon=True
        )
        listener_thread.start()
        
        # Give listener time to connect
        time.sleep(2)
        
        # Publish test events
        print("\n📤 Publishing test events...")
        test_events = [
            {
                "sender": "plot_architect",
                "recipient": "all",
                "event_type": "pipeline_start",
                "payload": {"pipeline_id": "test_123", "step": 1}
            },
            {
                "sender": "scene_generator", 
                "recipient": "producer",
                "event_type": "progress_update",
                "payload": {"progress": 50, "current_step": "Generating scene"}
            },
            {
                "sender": "producer",
                "recipient": "all", 
                "event_type": "pipeline_complete",
                "payload": {"success": True, "results": 5}
            }
        ]
        
        for i, event_data in enumerate(test_events):
            print(f"  Publishing: {event_data['event_type']}")
            event = event_bus.publish(
                sender=event_data["sender"],
                recipient=event_data["recipient"],
                event_type=event_data["event_type"],
                payload=event_data["payload"]
            )
            time.sleep(0.3)  # Small delay
        
        # Wait for events to be processed
        print("\n⏳ Waiting for WebSocket delivery...")
        time.sleep(2)
        
        # Check results
        print(f"\n📊 Results: Received {len(received_messages)} WebSocket messages")
        
        if len(received_messages) >= len(test_events):
            print("✅ All events delivered via WebSocket")
            
            # Verify event types
            received_types = [msg.get('type') for msg in received_messages]
            expected_types = ['eventbus_message'] * len(test_events)
            
            correct_count = sum(1 for msg in received_messages 
                              if msg.get('type') == 'eventbus_message')
            
            if correct_count == len(test_events):
                print("✅ All messages are eventbus_message type")
                
                # Show sample message
                if received_messages:
                    sample = received_messages[0]
                    print(f"\n📋 Sample message structure:")
                    print(f"  Type: {sample.get('type')}")
                    print(f"  Project: {sample.get('project')}")
                    print(f"  Data: {sample.get('data', {}).get('event_type')}")
                
                print("\n✅ Test 1 PASSED")
                return True
            else:
                print(f"❌ Only {correct_count}/{len(test_events)} messages are eventbus_message type")
                print(f"   Received types: {received_types}")
        else:
            print(f"❌ Only {len(received_messages)}/{len(test_events)} events received")
        
        print("❌ Test 1 FAILED")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_client_integration():
    """Test Streamlit WebSocket client."""
    print("\n🔍 Test 2: Streamlit WebSocket Client")
    print("-" * 40)
    
    try:
        # Mock Streamlit
        mock_streamlit_session()
        
        # Ensure server is running
        if not WEBSOCKET_MANAGER.running:
            WEBSOCKET_MANAGER.start_server()
            time.sleep(2)
        
        # Create and start client
        print("Creating Streamlit WebSocket client...")
        client = StreamlitWebSocketClient(project_name="client_test")
        
        # Register callback
        callback_called = []
        def test_callback(data):
            callback_called.append(data)
            print(f"  Callback received: {data.get('type')}")
        
        client.register_callback('test_event', test_callback)
        
        # Start client
        client.start()
        print("✅ Client started")
        
        # Give client time to connect
        time.sleep(2)
        
        # Send test message via WebSocket server
        print("\nSending test message...")
        WEBSOCKET_MANAGER.send_to_project(
            "client_test",
            "test_event",
            {"message": "Hello Streamlit client!", "test": True}
        )
        
        # Wait for callback
        print("Waiting for callback...")
        time.sleep(2)
        
        # Check results
        if callback_called:
            print(f"✅ Callback called {len(callback_called)} times")
            print(f"  Message: {callback_called[0].get('data')}")
        else:
            print("❌ Callback not called")
        
        # Test message storage
        print("\nTesting message storage...")
        messages = StreamlitWebSocketClient.get_latest_messages("client_test")
        if messages:
            print(f"✅ {len(messages)} messages stored in session")
            for msg in messages[:2]:  # Show first 2
                print(f"  - {msg.get('type')}: {msg.get('data', {}).get('message', 'No message')}")
        else:
            print("❌ No messages stored")
        
        # Stop client
        client.stop()
        time.sleep(0.5)
        
        if callback_called and messages:
            print("\n✅ Test 2 PASSED")
            return True
        else:
            print("\n❌ Test 2 FAILED")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_component():
    """Test UI components work with WebSocket."""
    print("\n🔍 Test 3: UI Component Integration")
    print("-" * 40)
    
    try:
        from ui.websocket_client import initialize_websocket_client
        
        print("Initializing WebSocket client via UI function...")
        client = initialize_websocket_client("ui_test")
        
        if client and client.running:
            print("✅ UI client initialized and running")
            
            # Test that client is in session state
            client_key = f"ws_client_ui_test"
            if client_key in st.session_state:
                print("✅ Client stored in session state")
            else:
                print("❌ Client not in session state")
            
            # Send a test message
            WEBSOCKET_MANAGER.send_to_project(
                "ui_test",
                "ui_test_event",
                {"component": "live_event_panel", "status": "ready"}
            )
            
            # Wait a bit
            time.sleep(1)
            
            # Check if message was stored
            messages = StreamlitWebSocketClient.get_latest_messages("ui_test")
            if messages:
                print(f"✅ UI can receive messages ({len(messages)} stored)")
            else:
                print("❌ UI not receiving messages")
            
            client.stop()
            
            if (client_key in st.session_state and messages):
                print("\n✅ Test 3 PASSED")
                return True
            else:
                print("\n❌ Test 3 FAILED")
                return False
        else:
            print("❌ UI client initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all WebSocket tests."""
    print("🧪 COMPLETE WEBSOCKET SYSTEM TEST")
    print("=" * 50)
    
    # Start WebSocket server if not running
    if not WEBSOCKET_MANAGER.running:
        print("Starting WebSocket server...")
        WEBSOCKET_MANAGER.start_server()
        time.sleep(2)
    
    if not WEBSOCKET_MANAGER.running:
        print("❌ WebSocket server failed to start")
        return False
    
    print("✅ WebSocket server is running")
    
    # Run tests
    tests = [
        ("EventBus Integration", test_eventbus_websocket_integration),
        ("Streamlit Client", test_streamlit_client_integration),
        ("UI Components", test_ui_component)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        result = test_func()
        results.append((test_name, result))
        if not result:
            print(f"⚠️  {test_name} FAILED - continuing with other tests...")
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! WebSocket system is fully functional!")
        return True
    else:
        print(f"\n💥 {failed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)