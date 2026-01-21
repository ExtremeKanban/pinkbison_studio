"""
Test EventBus WebSocket integration.
"""

import asyncio
import websockets
import json
import threading
import time
from core.event_bus import EventBus

def test_eventbus_websocket():
    """Test that EventBus publishes to WebSocket."""
    print("\n🔍 Test 2: EventBus WebSocket Integration")
    print("-" * 40)
    
    try:
        # Import WebSocket manager
        from core.websocket_manager import WEBSOCKET_MANAGER
        
        # Ensure server is running
        if not WEBSOCKET_MANAGER.running:
            WEBSOCKET_MANAGER.start_server()
            time.sleep(1)
        
        # Create EventBus instance
        event_bus = EventBus(project_name="test_project")
        
        # Variables to capture WebSocket messages
        received_messages = []
        
        # WebSocket client to listen for messages
        async def websocket_listener():
            uri = "ws://localhost:8765"
            try:
                async with websockets.connect(uri) as websocket:
                    # Subscribe
                    await websocket.send(json.dumps({
                        'action': 'subscribe',
                        'project': 'test_project'
                    }))
                    
                    # Listen for messages for 3 seconds
                    start_time = time.time()
                    while time.time() - start_time < 3:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                            data = json.loads(message)
                            received_messages.append(data)
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
        time.sleep(1)
        
        # Publish test event
        print("📤 Publishing test event...")
        test_payload = {"test": "data", "timestamp": time.time()}
        event = event_bus.publish(
            sender="test_sender",
            recipient="test_recipient",
            event_type="test_event",
            payload=test_payload
        )
        
        # Wait for WebSocket to receive it
        time.sleep(1)
        
        # Check if we received the event
        if received_messages:
            print(f"✅ Received {len(received_messages)} WebSocket messages")
            
            # Check if our test event was received
            for msg in received_messages:
                if (msg.get('type') == 'eventbus_message' and 
                    msg.get('data', {}).get('event_type') == 'test_event'):
                    print("✅ Test event successfully broadcast via WebSocket")
                    print(f"   Payload: {msg['data']['payload']}")
                    print("✅ Test 2 PASSED")
                    return True
            
            print("❌ Test event not found in WebSocket messages")
            print(f"   Messages received: {[m.get('type') for m in received_messages]}")
        else:
            print("❌ No WebSocket messages received")
        
        print("❌ Test 2 FAILED")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_eventbus_websocket()
    print("\n" + "=" * 40)
    if success:
        print("🎉 EventBus WebSocket integration is working!")
    else:
        print("💥 EventBus WebSocket integration has issues")
    exit(0 if success else 1)