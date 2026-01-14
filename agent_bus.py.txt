# agent_bus.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import uuid
import time


@dataclass
class AgentMessage:
    id: str
    project_name: str
    sender: str
    recipient: str  # agent name or "ALL"
    type: str       # e.g. "REQUEST", "RESPONSE", "CRITIQUE", "INFO"
    payload: Dict[str, Any]
    timestamp: float
    in_reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentBus:
    """
    Simple in-memory message bus for agents, scoped by project.
    Can be made persistent later.
    """

    def __init__(self):
        # messages[project_name] = list[AgentMessage]
        self.messages: Dict[str, List[AgentMessage]] = {}

    def _ensure_project(self, project_name: str) -> None:
        if project_name not in self.messages:
            self.messages[project_name] = []

    def send(
        self,
        project_name: str,
        sender: str,
        recipient: str,
        msg_type: str,
        payload: Dict[str, Any],
        in_reply_to: Optional[str] = None,
    ) -> AgentMessage:
        self._ensure_project(project_name)
        msg = AgentMessage(
            id=str(uuid.uuid4()),
            project_name=project_name,
            sender=sender,
            recipient=recipient,
            type=msg_type,
            payload=payload,
            timestamp=time.time(),
            in_reply_to=in_reply_to,
        )
        self.messages[project_name].append(msg)
        return msg

    def get_for(
        self,
        project_name: str,
        agent_name: str,
        since_id: Optional[str] = None,
    ) -> List[AgentMessage]:
        """
        Get messages for a specific agent (or broadcast "ALL").
        Optionally filter to messages after a given message id.
        """
        self._ensure_project(project_name)
        msgs = [
            m
            for m in self.messages[project_name]
            if m.recipient in (agent_name, "ALL")
        ]

        if since_id is not None:
            # naive filter: only messages created after the message with since_id
            try:
                idx = next(
                    i for i, m in enumerate(self.messages[project_name]) if m.id == since_id
                )
                cutoff_time = self.messages[project_name][idx].timestamp
                msgs = [m for m in msgs if m.timestamp > cutoff_time]
            except StopIteration:
                # since_id not found, return all msgs
                pass

        return msgs

    def clear_project(self, project_name: str) -> None:
        self.messages.pop(project_name, None)


# Global bus instance for the process
GLOBAL_AGENT_BUS = AgentBus()
