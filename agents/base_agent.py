"""
Base class for all agents with EventBus + AuditLog integration.
Agents are now stateless - no feedback_inbox, fresh instance per task.
"""

from typing import Dict, Any, Optional
from core.event_bus import EventBus
from core.audit_log import AuditLog


class AgentBase:
    """
    Shared base class for all agents.
    
    Changes from old version:
    - No feedback_inbox (feedback routed via EventBus)
    - EventBus + AuditLog injected
    - Agents are stateless (created per-task)
    """
    
    def __init__(self, name: str, project_name: str, event_bus: EventBus,
             audit_log: AuditLog, fast_model_url: str, model_mode: str):
        self.name = name
        self.project_name = project_name
        self.event_bus = event_bus
        self.audit_log = audit_log
        self.fast_model_url = fast_model_url
        self.model_mode = model_mode
        
        # Add memory access
        from memory_store import MemoryStore
        self.memory = MemoryStore(project_name)
    
    def log(self, content: str, event_type: str = "info") -> None:
        """Log to both EventBus (ephemeral) and AuditLog (persistent)"""
        # Publish to EventBus for real-time notifications
        self.event_bus.publish(
            sender=self.name,
            recipient="ALL",
            event_type=event_type,
            payload={"content": content}
        )
        
        # Append to AuditLog for historical record
        self.audit_log.append(
            event_type=f"agent_log_{event_type}",
            sender=self.name,
            recipient="ALL",
            payload={"content": content}
        )
    
    def send_message(self, recipient: str, msg_type: str, payload: Dict[str, Any]) -> None:
        """Send message to another agent"""
        # Publish to EventBus
        self.event_bus.publish(
            sender=self.name,
            recipient=recipient,
            event_type=msg_type,
            payload=payload
        )
        
        # Log to AuditLog
        self.audit_log.append(
            event_type=f"agent_message_{msg_type}",
            sender=self.name,
            recipient=recipient,
            payload=payload
        )
    
    def get_recent_messages(self, limit: int = 10) -> list:
        """Get recent messages from EventBus"""
        events = self.event_bus.get_recent(self.name, limit=limit)
        return [e.payload for e in events]