"""
Thread-safe feedback injection system for Phase 1.
"""

import threading
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


class FeedbackType(Enum):
    """Types of feedback that can be injected."""
    GUIDANCE = "guidance"
    CRITIQUE = "critique"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"
    CANON = "canon"
    PRIORITY = "priority"


class FeedbackPriority(Enum):
    """Priority levels for feedback."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


@dataclass
class FeedbackMessage:
    """A single feedback message."""
    id: str
    target_agent: str  # "ALL" for broadcast
    feedback_type: FeedbackType
    content: str
    priority: FeedbackPriority
    source: str  # "user", "agent", "system"
    created_at: str
    processed: bool = False
    processed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['feedback_type'] = self.feedback_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeedbackMessage':
        """Create from dictionary."""
        data = data.copy()
        data['feedback_type'] = FeedbackType(data['feedback_type'])
        data['priority'] = FeedbackPriority(data['priority'])
        return cls(**data)


class FeedbackManager:
    """
    Thread-safe feedback manager for real-time feedback injection.
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.feedback_messages: List[FeedbackMessage] = []
        self.lock = threading.RLock()
    
    def add_feedback(
        self,
        target_agent: str,
        feedback_type: FeedbackType,
        content: str,
        priority: FeedbackPriority = FeedbackPriority.NORMAL,
        source: str = "user"
    ) -> str:
        """
        Add a new feedback message.
        
        Args:
            target_agent: Agent name or "ALL" for broadcast
            feedback_type: Type of feedback
            content: Feedback content
            priority: Priority level
            source: Source of feedback
            
        Returns:
            Feedback message ID
        """
        with self.lock:
            feedback_id = str(uuid.uuid4())
            message = FeedbackMessage(
                id=feedback_id,
                target_agent=target_agent,
                feedback_type=feedback_type,
                content=content,
                priority=priority,
                source=source,
                created_at=datetime.now().isoformat(),
                processed=False
            )
            self.feedback_messages.append(message)
            return feedback_id
    
    def get_feedback_for_agent(
        self,
        agent_name: str,
        include_broadcast: bool = True,
        unprocessed_only: bool = True
    ) -> List[FeedbackMessage]:
        """
        Get feedback messages for a specific agent.
        
        Args:
            agent_name: Agent to get feedback for
            include_broadcast: Include "ALL" broadcast messages
            unprocessed_only: Only return unprocessed messages
            
        Returns:
            List of feedback messages
        """
        with self.lock:
            messages = []
            for msg in self.feedback_messages:
                # Check if message is for this agent
                matches_target = (msg.target_agent == agent_name)
                matches_broadcast = include_broadcast and (msg.target_agent == "ALL")
                
                # Check processing status
                matches_processed = not unprocessed_only or not msg.processed
                
                if (matches_target or matches_broadcast) and matches_processed:
                    messages.append(msg)
            
            # Sort by priority (highest first) and creation time (newest first)
            messages.sort(
                key=lambda x: (-x.priority.value, x.created_at),
                reverse=True
            )
            return messages
    
    def mark_as_processed(self, feedback_id: str) -> bool:
        """
        Mark a feedback message as processed.
        
        Args:
            feedback_id: ID of feedback message
            
        Returns:
            True if message was found and marked
        """
        with self.lock:
            for msg in self.feedback_messages:
                if msg.id == feedback_id:
                    msg.processed = True
                    msg.processed_at = datetime.now().isoformat()
                    return True
            return False
    
    def clear_processed(self) -> int:
        """
        Remove all processed messages.
        
        Returns:
            Number of messages removed
        """
        with self.lock:
            initial_count = len(self.feedback_messages)
            self.feedback_messages = [
                msg for msg in self.feedback_messages
                if not msg.processed
            ]
            return initial_count - len(self.feedback_messages)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about feedback messages.
        
        Returns:
            Dictionary with stats
        """
        with self.lock:
            total = len(self.feedback_messages)
            processed = sum(1 for msg in self.feedback_messages if msg.processed)
            unprocessed = total - processed
            
            # Count by priority
            by_priority = {}
            for priority in FeedbackPriority:
                count = sum(1 for msg in self.feedback_messages 
                          if msg.priority == priority)
                by_priority[priority.name] = count
            
            # Count by type
            by_type = {}
            for ftype in FeedbackType:
                count = sum(1 for msg in self.feedback_messages 
                          if msg.feedback_type == ftype)
                by_type[ftype.value] = count
            
            return {
                "total": total,
                "processed": processed,
                "unprocessed": unprocessed,
                "by_priority": by_priority,
                "by_type": by_type,
            }
    
    def reset(self) -> None:
        """Clear all feedback messages."""
        with self.lock:
            self.feedback_messages.clear()