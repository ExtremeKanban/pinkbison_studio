"""
Working WebSocket manager with proper handler signature.
"""

import asyncio
import json
import threading
import time
from typing import Dict, Set, Optional
import websockets


class WebSocketManager:
    """WebSocket server for real-time updates."""
    
    _instance: Optional['WebSocketManager'] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = WebSocketManager()
        return cls._instance
    
    def __init__(self):
        self.host = "localhost"
        self.port = 8765
        self.connections: Set[websockets.WebSocketServerProtocol] = set()
        self.subscriptions: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.running = False
        self.server_task: Optional[asyncio.Task] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
    
    async def _handler(self, websocket, path=None):
        """
        Handle WebSocket connections.
        Note: 'path' parameter might be omitted in some websockets versions.
        """
        client_addr = websocket.remote_address
        print(f"[WebSocket] New connection from {client_addr}")
        self.connections.add(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    action = data.get('action')
                    
                    if action == 'subscribe':
                        project_name = data['project']
                        if project_name not in self.subscriptions:
                            self.subscriptions[project_name] = set()
                        self.subscriptions[project_name].add(websocket)
                        
                        print(f"[WebSocket] {client_addr} subscribed to {project_name}")
                        
                        # Send acknowledgement
                        await websocket.send(json.dumps({
                            'type': 'subscription_confirmed',
                            'project': project_name,
                            'timestamp': time.time()
                        }))
                    
                    elif action == 'unsubscribe':
                        project_name = data['project']
                        if project_name in self.subscriptions:
                            self.subscriptions[project_name].discard(websocket)
                            print(f"[WebSocket] {client_addr} unsubscribed from {project_name}")
                    
                except json.JSONDecodeError as e:
                    print(f"[WebSocket] Invalid JSON from {client_addr}: {e}")
                except Exception as e:
                    print(f"[WebSocket] Error processing message from {client_addr}: {e}")
        
        except websockets.exceptions.ConnectionClosed as e:
            print(f"[WebSocket] Connection closed: {client_addr} - {e.code} {e.reason}")
        except Exception as e:
            print(f"[WebSocket] Error with connection {client_addr}: {e}")
        finally:
            self.connections.discard(websocket)
            # Remove from all subscriptions
            for project_name, connections in self.subscriptions.items():
                connections.discard(websocket)
            print(f"[WebSocket] Connection cleaned up: {client_addr}")
    
    async def _run_server(self):
        """Run the WebSocket server."""
        # Create handler that works with any websockets version
        async def universal_handler(websocket, path=None):
            await self._handler(websocket, path)
        
        print(f"[WebSocket] Starting server on ws://{self.host}:{self.port}")
        
        # Start server with ping_interval to keep connections alive
        async with websockets.serve(
            universal_handler, 
            self.host, 
            self.port,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=10
        ):
            self.running = True
            print(f"[WebSocket] Server is running")
            await asyncio.Future()  # Run forever
    
    def _start_background_loop(self):
        """Start asyncio event loop in background thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.server_task = self.loop.create_task(self._run_server())
        
        try:
            self.loop.run_until_complete(self.server_task)
        except asyncio.CancelledError:
            print("[WebSocket] Server task cancelled")
        except Exception as e:
            print(f"[WebSocket] Server error: {e}")
        finally:
            self.running = False
    
    def start_server(self):
        """Start WebSocket server in background thread."""
        if self.running:
            print("[WebSocket] Server already running")
            return
        
        print("[WebSocket] Starting server in background...")
        self.server_thread = threading.Thread(
            target=self._start_background_loop,
            daemon=True,
            name="WebSocketServer"
        )
        self.server_thread.start()
        
        # Wait for server to start
        for _ in range(10):  # Wait up to 2 seconds
            if self.running:
                print(f"[WebSocket] Server started successfully on ws://{self.host}:{self.port}")
                return
            time.sleep(0.2)
        
        print("[WebSocket] Warning: Server may not have started properly")
    
    async def _broadcast_async(self, project_name: str, event_type: str, data: dict):
        """Broadcast message to project subscribers (async version)."""
        if project_name not in self.subscriptions:
            return
        
        message = json.dumps({
            'type': event_type,
            'project': project_name,
            'data': data,
            'timestamp': time.time()
        })
        
        dead_connections = []
        for ws in self.subscriptions[project_name]:
            try:
                await ws.send(message)
            except Exception as e:
                print(f"[WebSocket] Error sending to connection: {e}")
                dead_connections.append(ws)
        
        # Clean up dead connections
        for ws in dead_connections:
            self.subscriptions[project_name].discard(ws)
    
    def send_to_project(self, project_name: str, event_type: str, data: dict):
        """Send message to project subscribers (thread-safe)."""
        if not self.running or not self.loop:
            print(f"[WebSocket] Cannot send: server not ready")
            return
        
        try:
            # Schedule the broadcast in the event loop
            asyncio.run_coroutine_threadsafe(
                self._broadcast_async(project_name, event_type, data),
                self.loop
            )
        except Exception as e:
            print(f"[WebSocket] Error scheduling broadcast: {e}")
    
    def stop_server(self):
        """Stop the WebSocket server."""
        if self.running and self.loop and self.server_task:
            print("[WebSocket] Stopping server...")
            self.loop.call_soon_threadsafe(self.server_task.cancel)
            self.running = False
            print("[WebSocket] Server stopped")


# Global instance
WEBSOCKET_MANAGER = WebSocketManager.get_instance()