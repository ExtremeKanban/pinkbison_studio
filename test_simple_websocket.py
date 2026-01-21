"""
Simple test to verify WebSocket server works.
"""

import asyncio
import websockets
import json
import time
import threading

def test_simple():
    """Test basic WebSocket functionality."""
    print("🧪 Testing WebSocket Server")
    print("=" * 50)
    
    # Import and start WebSocket manager
    from core.websocket_manager import WEBSOCKET_MANAGER
    
    print("1. Starting WebSocket server...")
    WEBSOCKET_MANAGER.start_server()
    time.sleep(2)  # Give server time to start
    
    if not WEBSOCKET_MANAGER.running:
        print("❌ Server failed to start")
        return False
    print("✅ Server started")
    
    # Test connection
    print("\n2. Testing WebSocket connection...")
    
    async def connect_test():
        try:
            uri = "ws://localhost:8765"
            async with websockets.connect(uri) as websocket:
                # Send subscription
                await websocket.send(json.dumps({
                    'action': 'subscribe',
                    'project': 'test_project'
                }))
                
                # Wait for confirmation
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(response)
                
                if data.get('type') == 'subscription_confirmed':
                    print("✅ Connected and subscribed")
                    
                    # Test sending a message
                    WEBSOCKET_MANAGER.send_to_project(
                        'test_project',
                        'test_event',
                        {'message': 'Hello from test!'}
                    )
                    
                    # Wait for message
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(response)
                    
                    if data.get('type') == 'test_event':
                        print(f"✅ Received test event: {data.get('data')}")
                        return True
                    else:
                        print(f"❌ Unexpected response: {data}")
                        return False
                else:
                    print(f"❌ Unexpected confirmation: {data}")
                    return False
                    
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    # Run the async test
    try:
        result = asyncio.run(connect_test())
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        result = False
    
    print("\n" + "=" * 50)
    if result:
        print("🎉 WebSocket server is working correctly!")
    else:
        print("💥 WebSocket server has issues")
    
    return result

if __name__ == "__main__":
    success = test_simple()
    exit(0 if success else 1)