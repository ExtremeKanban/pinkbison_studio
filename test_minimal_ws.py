"""
Minimal WebSocket test that works with any version.
"""

import websockets
import json
import time
import asyncio

async def test_connection():
    """Test basic WebSocket connection."""
    print("🧪 Testing WebSocket connection...")
    
    try:
        uri = "ws://localhost:8765"
        
        # Try to connect
        async with websockets.connect(uri, ping_interval=None) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Send subscription
            await websocket.send(json.dumps({
                'action': 'subscribe',
                'project': 'test_project'
            }))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ Server response: {data.get('type')}")
                return True
            except asyncio.TimeoutError:
                print("❌ No response from server")
                return False
                
    except ConnectionRefusedError:
        print("❌ Cannot connect to WebSocket server")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """Run the test."""
    print("=" * 50)
    
    # Import and start WebSocket manager
    from core.websocket_manager import WEBSOCKET_MANAGER
    
    print("Starting WebSocket server...")
    WEBSOCKET_MANAGER.start_server()
    
    # Wait for server to start
    time.sleep(2)
    
    if not WEBSOCKET_MANAGER.running:
        print("❌ Server failed to start")
        return False
    
    print("✅ Server is running")
    
    # Test connection
    result = asyncio.run(test_connection())
    
    print("\n" + "=" * 50)
    if result:
        print("🎉 WebSocket connection successful!")
    else:
        print("💥 WebSocket connection failed")
    
    return result

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)