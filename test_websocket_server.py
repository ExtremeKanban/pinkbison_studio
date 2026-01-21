"""
Test WebSocket server functionality.
"""

import asyncio
import websockets
import json
import threading
import time

def test_websocket_server():
    """Test that WebSocket server starts and accepts connections."""
    print("🔍 Test 1: WebSocket Server")
    print("-" * 40)
    
    try:
        # Try to import and start WebSocket manager
        from core.websocket_manager import WEBSOCKET_MANAGER
        
        # Start server
        WEBSOCKET_MANAGER.start_server()
        print("✅ WebSocket server started")
        
        # Give server time to start
        time.sleep(1)
        
        # Test connection
        async def test_connection():
            try:
                uri = "ws://localhost:8765"
                async with websockets.connect(uri) as websocket:
                    # Send subscription
                    await websocket.send(json.dumps({
                        'action': 'subscribe',
                        'project': 'test_project'
                    }))
                    
                    # Wait for response
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    
                    if data.get('type') == 'subscription_confirmed':
                        print("✅ Connection and subscription successful")
                        return True
                    else:
                        print(f"❌ Unexpected response: {data}")
                        return False
                        
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return False
        
        # Run async test
        result = asyncio.run(test_connection())
        
        if result:
            print("✅ Test 1 PASSED")
        else:
            print("❌ Test 1 FAILED")
        
        return result
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False


if __name__ == "__main__":
    success = test_websocket_server()
    print("\n" + "=" * 40)
    if success:
        print("🎉 WebSocket server is working!")
    else:
        print("💥 WebSocket server has issues")
    exit(0 if success else 1)