"""
Project registry for managing project-scoped infrastructure.
Replaces global singletons with proper project isolation.
"""

from typing import Dict, Optional
from core.event_bus import EventBus
from core.audit_log import AuditLog
from agent_bus import AgentBus
from memory_store import MemoryStore
from graph_store import GraphStore
from task_manager import TaskManager


class ProjectRegistry:
    """
    Registry for project-scoped infrastructure.
    
    Manages EventBus, AuditLog, AgentBus, MemoryStore, GraphStore,
    and TaskManager instances per project.
    
    Design:
    - One instance per project (not global)
    - Easy cleanup for tests
    - Thread-safe (single-threaded for now)
    
    Example:
        >>> registry = ProjectRegistry()
        >>> event_bus = registry.get_event_bus("my_project")
        >>> audit_log = registry.get_audit_log("my_project")
    """
    
    def __init__(self):
        self._event_buses: Dict[str, EventBus] = {}
        self._audit_logs: Dict[str, AuditLog] = {}
        self._agent_buses: Dict[str, AgentBus] = {}
        self._memory_stores: Dict[str, MemoryStore] = {}
        self._graph_stores: Dict[str, GraphStore] = {}
        self._task_managers: Dict[str, TaskManager] = {}
    
    def get_event_bus(self, project_name: str) -> EventBus:
        """Get or create EventBus for project"""
        if project_name not in self._event_buses:
            self._event_buses[project_name] = EventBus(project_name)
        return self._event_buses[project_name]
    
    def get_audit_log(self, project_name: str) -> AuditLog:
        """Get or create AuditLog for project"""
        if project_name not in self._audit_logs:
            self._audit_logs[project_name] = AuditLog(project_name)
        return self._audit_logs[project_name]
    
    def get_agent_bus(self, project_name: str) -> AgentBus:
        """Get or create AgentBus for project"""
        if project_name not in self._agent_buses:
            self._agent_buses[project_name] = AgentBus()
        return self._agent_buses[project_name]
    
    def get_memory_store(self, project_name: str) -> MemoryStore:
        """Get or create MemoryStore for project"""
        if project_name not in self._memory_stores:
            self._memory_stores[project_name] = MemoryStore(project_name)
        return self._memory_stores[project_name]
    
    def get_graph_store(self, project_name: str) -> GraphStore:
        """Get or create GraphStore for project"""
        if project_name not in self._graph_stores:
            self._graph_stores[project_name] = GraphStore(project_name)
        return self._graph_stores[project_name]
    
    def get_task_manager(self, project_name: str) -> TaskManager:
        """Get or create TaskManager for project"""
        if project_name not in self._task_managers:
            self._task_managers[project_name] = TaskManager(project_name)
        return self._task_managers[project_name]
    
    def clear_project(self, project_name: str) -> None:
        """
        Remove all instances for a project.
        
        Useful for:
        - Test cleanup
        - Project deletion
        - Memory management
        """
        self._event_buses.pop(project_name, None)
        self._audit_logs.pop(project_name, None)
        self._agent_buses.pop(project_name, None)
        self._memory_stores.pop(project_name, None)
        self._graph_stores.pop(project_name, None)
        self._task_managers.pop(project_name, None)
    
    def clear_all(self) -> None:
        """Clear all projects (for tests)"""
        self._event_buses.clear()
        self._audit_logs.clear()
        self._agent_buses.clear()
        self._memory_stores.clear()
        self._graph_stores.clear()
        self._task_managers.clear()
    
    def get_all_projects(self) -> list[str]:
        """Get list of all active projects in registry"""
        # Union of all project names across all registries
        projects = set()
        projects.update(self._event_buses.keys())
        projects.update(self._audit_logs.keys())
        projects.update(self._agent_buses.keys())
        projects.update(self._memory_stores.keys())
        projects.update(self._graph_stores.keys())
        projects.update(self._task_managers.keys())
        return sorted(list(projects))


# Global registry instance
# This is the ONE global we keep - it manages everything else
REGISTRY = ProjectRegistry()