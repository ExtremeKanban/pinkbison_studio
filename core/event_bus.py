"""
Ephemeral message passing for real-time agent coordination.
Lives only during orchestrator runtime.
"""

from typing import Dict, List, Callable, Any, Optional
from collections import deque
from dataclasses import dataclass, field
import time
import uuid


@dataclass
class Event:
    """Lightweight event for real-time coordination"""
    id: str
    project_name: str
    sender: str
    recipient: str  # agent name or "ALL"
    type: str
    payload: Dict[str, Any]
    timestamp: float
    
    @classmethod
    def create(cls, project_name: str, sender: str, recipient: str, 
               event_type: str, payload: Dict[str, Any]) -> "Event":
        return cls(
            id=str(uuid.uuid4()),
            project_name=project_name,
            sender=sender,
            recipient=recipient,
            type=event_type,
            payload=payload,
            timestamp=time.time()
        )


class EventBus:
    """
    Ephemeral in-memory event bus for real-time agent coordination.
    
    Design:
    - Ring buffer (last 100 events only)
    - Subscriber pattern for real-time notifications
    - No persistence (use AuditLog for that)
    """
    
    def __init__(self, project_name: str, buffer_size: int = 100):
        self.project_name = project_name
        self.buffer: deque[Event] = deque(maxlen=buffer_size)
        self.subscribers: Dict[str, List[Callable]] = {}
        self._event_counter = 0
    
    def publish(self, sender: str, recipient: str, event_type: str, 
                payload: Dict[str, Any]) -> Event:
        """Publish event to bus"""
        event = Event.create(
            project_name=self.project_name,
            sender=sender,
            recipient=recipient,
            event_type=event_type,
            payload=payload
        )
        
        self.buffer.append(event)
        self._notify_subscribers(event)
        return event
    
    def subscribe(self, agent_name: str, callback: Callable[[Event], None]) -> None:
        """Subscribe to events for a specific agent"""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)
    
    def get_recent(self, agent_name: str, limit: int = 10) -> List[Event]:
        """Get recent events for an agent (from ring buffer)"""
        return [
            e for e in list(self.buffer)[-limit:]
            if e.recipient in (agent_name, "ALL")
        ]
    
    def _notify_subscribers(self, event: Event) -> None:
        """Notify subscribers of new event"""
        # Notify specific recipient
        if event.recipient in self.subscribers:
            for callback in self.subscribers[event.recipient]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in subscriber callback: {e}")
        
        # Notify "ALL" subscribers
        if event.recipient == "ALL" and "ALL" in self.subscribers:
            for callback in self.subscribers["ALL"]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in subscriber callback: {e}")
    
    def clear(self) -> None:
        """Clear buffer (for testing)"""
        self.buffer.clear()