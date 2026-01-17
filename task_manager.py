import json
import os
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import time
import uuid


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class Task:
    id: str
    project_name: str
    type: str              # e.g. "SCENE_REVISION", "WORLD_EXPANSION"
    payload: Dict[str, Any]
    status: TaskStatus
    created_at: float
    updated_at: float
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Task":
        return Task(
            id=data["id"],
            project_name=data["project_name"],
            type=data["type"],
            payload=data["payload"],
            status=TaskStatus(data["status"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            error=data.get("error"),
        )


class TaskManager:
    """
    Persistent, project-scoped task manager.
    Stores tasks in tasks/<project_name>_tasks.json
    """

    def __init__(self, project_name: str, base_dir: str = "tasks"):
        self.project_name = project_name
        
        # Get unified paths
        from core.storage_paths import ProjectPaths, LegacyPaths
        self.paths = ProjectPaths.for_project(project_name)
        self.paths.ensure_directories()
        
        # Migrate from legacy location if needed
        self._migrate_from_legacy()
        
        # Use new unified path
        self.path = str(self.paths.tasks)
        self._tasks: List[Task] = []
        self._load()
    
    def _migrate_from_legacy(self) -> None:
        """Migrate tasks from legacy location"""
        import shutil
        from core.storage_paths import LegacyPaths
        
        legacy_path = LegacyPaths.tasks(self.project_name)
        
        # Check if migration needed
        if not legacy_path.exists():
            return
        
        # Check if already migrated
        if self.paths.tasks.exists():
            return
        
        print(f"[TaskManager] Migrating {self.project_name} tasks to unified storage...")
        shutil.copy2(legacy_path, self.paths.tasks)
        print(f"  ✓ Migrated: {legacy_path} → {self.paths.tasks}")

    def _load(self) -> None:
        if not os.path.exists(self.path):
            self._tasks = []
            self._save()
            return
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self._tasks = [Task.from_dict(t) for t in raw]

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self._tasks], f, indent=2)

    def add_task(self, task_type: str, payload: Dict[str, Any]) -> Task:
        now = time.time()
        task = Task(
            id=str(uuid.uuid4()),
            project_name=self.project_name,
            type=task_type,
            payload=payload,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._tasks.append(task)
        self._save()
        return task

    def get_next_pending(self) -> Optional[Task]:
        for t in self._tasks:
            if t.status == TaskStatus.PENDING:
                return t
        return None

    def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        error: Optional[str] = None,
        new_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        for t in self._tasks:
            if t.id == task_id:
                t.status = status
                t.updated_at = time.time()
                if error is not None:
                    t.error = error
                if new_payload is not None:
                    t.payload = new_payload
                self._save()
                return

    def get_all(self) -> List[Task]:
        return list(self._tasks)
