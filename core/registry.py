"""
Registry for project-scoped infrastructure.
Singleton pattern with lazy initialization.
"""

import os
from typing import Dict, Any, Optional
from .event_bus import EventBus
from .audit_log import AuditLog
from .project_state import ProjectState
from .agent_factory import AgentFactory
from .output_manager import OutputManager
from core.storage_paths import ProjectPaths  # CHANGED from StoragePaths to ProjectPaths


class ProjectRegistry:
    """
    Registry for project-scoped resources.
    Ensures one instance per project.
    """
    
    _instance = None
    _instances: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_event_bus(self, project_name: str) -> EventBus:
        """Get or create EventBus for project."""
        key = f"event_bus_{project_name}"
        if key not in self._instances:
            self._instances[key] = EventBus(project_name)
        return self._instances[key]
    
    def get_audit_log(self, project_name: str) -> AuditLog:
        """Get or create AuditLog for project."""
        key = f"audit_log_{project_name}"
        if key not in self._instances:
            self._instances[key] = AuditLog(project_name)
        return self._instances[key]
    
    def get_memory_store(self, project_name: str):
        """Get or create MemoryStore for project."""
        key = f"memory_store_{project_name}"
        if key not in self._instances:
            from memory_store import MemoryStore
            self._instances[key] = MemoryStore(project_name)
        return self._instances[key]
    
    def get_graph_store(self, project_name: str):
        """Get or create GraphStore for project."""
        key = f"graph_store_{project_name}"
        if key not in self._instances:
            from graph_store import GraphStore
            self._instances[key] = GraphStore(project_name)
        return self._instances[key]
    
    def get_task_manager(self, project_name: str):
        """Get or create TaskManager for project."""
        key = f"task_manager_{project_name}"
        if key not in self._instances:
            from task_manager import TaskManager
            self._instances[key] = TaskManager(project_name)
        return self._instances[key]
    
    def get_output_manager(self, project_name: str) -> OutputManager:
        """Get or create OutputManager for project."""
        key = f"output_manager_{project_name}"
        if key not in self._instances:
            self._instances[key] = OutputManager(project_name)
        return self._instances[key]
    
    def get_project_state(self, project_name: str) -> ProjectState:
        """Get or create ProjectState for project."""
        key = f"project_state_{project_name}"
        if key not in self._instances:
            self._instances[key] = ProjectState.load(project_name)
        return self._instances[key]
    
    def get_agent_factory(self, project_name: str) -> AgentFactory:
        """Get or create AgentFactory for project."""
        key = f"agent_factory_{project_name}"
        if key not in self._instances:
            self._instances[key] = AgentFactory(project_name)
        return self._instances[key]
    
    def get_storage_paths(self, project_name: str) -> ProjectPaths:  # CHANGED return type
        """Get or create StoragePaths for project."""
        key = f"storage_paths_{project_name}"
        if key not in self._instances:
            self._instances[key] = ProjectPaths.for_project(project_name)  # CHANGED call
        return self._instances[key]
    
    def get_pipeline_controller(self, project_name: str):
        """Get or create PipelineController for project."""
        key = f"pipeline_controller_{project_name}"
        if key not in self._instances:
            # Import here to avoid circular imports
            try:
                from core.pipeline_controller import PipelineController
                self._instances[key] = PipelineController(project_name)
            except ImportError as e:
                # Create a mock if not available
                print(f"Warning: PipelineController not available, using mock: {e}")
                self._instances[key] = MockPipelineController(project_name)
        return self._instances[key]
    
    def get_feedback_manager(self, project_name: str):
        """Get or create FeedbackManager for project."""
        key = f"feedback_manager_{project_name}"
        if key not in self._instances:
            # Import here to avoid circular imports
            try:
                from core.feedback_manager import FeedbackManager
                self._instances[key] = FeedbackManager(project_name)
            except ImportError as e:
                # Create a mock if not available
                print(f"Warning: FeedbackManager not available, using mock: {e}")
                self._instances[key] = MockFeedbackManager(project_name)
        return self._instances[key]
    
    def clear_project(self, project_name: str) -> None:
        """Clear all instances for a project."""
        keys_to_remove = []
        for key in self._instances:
            if key.endswith(f"_{project_name}"):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._instances[key]
    
    def clear_all(self) -> None:
        """Clear all instances."""
        self._instances.clear()


# Mock classes for when Phase 1 components aren't available
class MockPipelineController:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.status = "idle"
    
    def get_status(self):
        return {
            "status": "idle",
            "current_task": None,
            "progress": {"percent_complete": 0},
            "feedback_stats": {"unprocessed": 0}
        }
    
    def start_pipeline(self, *args, **kwargs):
        raise NotImplementedError("PipelineController not available")
    
    def pause(self):
        raise NotImplementedError("PipelineController not available")
    
    def resume(self):
        raise NotImplementedError("PipelineController not available")


class MockFeedbackManager:
    def __init__(self, project_name: str):
        self.project_name = project_name
    
    def get_stats(self):
        return {"unprocessed": 0, "total": 0}
    
    def add_feedback(self, *args, **kwargs):
        raise NotImplementedError("FeedbackManager not available")


# Global singleton instance
REGISTRY = ProjectRegistry()