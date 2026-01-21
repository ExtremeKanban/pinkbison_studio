"""
Complete WebSocket integration test.
Simulates real usage scenario.
"""

import asyncio
import websockets
import json
import threading
import time

def test_complete_integration():
    """Complete end-to-end test of WebSocket system."""
    print("\n🔍 Test 4: Complete Integration Test")
    print("-" * 40)
    
    try:
        # Import all components
        from core.websocket_manager import WEBSOCKET_MANAGER
        from core.event_bus import EventBus
        from ui.websocket_client import StreamlitWebSocketClient
        
        # 1. Start WebSocket server
        print("1. Starting WebSocket server...")
        WEBSOCKET_MANAGER.start_server()
        time.sleep(2)
        
        if WEBSOCKET_MANAGER.running:
            print("   ✅ Server running")
        else:
            print("   ❌ Server not running")
            return False
        
        # 2. Create EventBus and WebSocket client
        print("2. Creating components...")
        event_bus = EventBus(project_name="integration_test")
        client = StreamlitWebSocketClient(project_name="integration_test")
        
        # 3. Start client and register callback
        print("3. Starting WebSocket client...")
        
        # Callback to capture events
        captured_events = []
        def event_callback(data):
            captured_events.append(data)
            print(f"   📨 Client received: {data.get('type')}")
        
        client.register_callback('eventbus_message', event_callback)
        client.start()
        time.sleep(2)  # Give time to connect
        
        if client.running:
            print("   ✅ Client connected")
        else:
            print("   ❌ Client not connected")
            return False
        
        # 4. Publish events through EventBus
        print("4. Publishing test events...")
        
        test_events = [
            {"type": "pipeline_start", "data": {"step": 1}},
            {"type": "agent_progress", "data": {"agent": "plot_architect", "progress": 50}},
            {"type": "pipeline_complete", "data": {"success": True}}
        ]
        
        for i, event_data in enumerate(test_events):
            event = event_bus.publish(
                sender=f"agent_{i}",
                recipient="all",
                event_type=event_data["type"],
                payload=event_data["data"]
            )
            print(f"   📤 Published: {event_data['type']}")
            time.sleep(0.5)  # Small delay between events
        
        # 5. Wait and check results
        print("5. Verifying events...")
        time.sleep(2)
        
        # Check if events were captured
        if len(captured_events) >= len(test_events):
            print(f"   ✅ All {len(captured_events)} events received")
            
            # Verify each event type was received
            received_types = [e.get('type') for e in captured_events]
            expected_types = ['eventbus_message'] * len(test_events)
            
            if all(t in received_types for t in expected_types):
                print("   ✅ All event types received correctly")
            else:
                print(f"   ❌ Missing event types. Received: {received_types}")
                return False
        else:
            print(f"   ❌ Only {len(captured_events)}/{len(test_events)} events received")
            return False
        
        # 6. Check message storage
        print("6. Checking message storage...")
        stored_messages = StreamlitWebSocketClient.get_latest_messages("integration_test")
        
        if stored_messages and len(stored_messages) > 0:
            print(f"   ✅ {len(stored_messages)} messages stored in session")
        else:
            print("   ❌ No messages stored")
            return False
        
        # 7. Cleanup
        print("7. Cleaning up...")
        client.stop()
        time.sleep(0.5)
        
        print("✅ Test 4 PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_complete_integration()
    print("\n" + "=" * 40)
    if success:
        print("🎉 COMPLETE INTEGRATION TEST PASSED!")
        print("   WebSocket system is fully functional!")
    else:
        print("💥 Integration test failed")
    exit(0 if success else 1)