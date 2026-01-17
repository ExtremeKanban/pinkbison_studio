"""
Single-project orchestrator (legacy, Phase 0).
Uses new EventBus + AuditLog architecture.

This will be replaced by MultiProjectOrchestrator in Phase 1.
"""

import time
from typing import Optional

from agents.producer import ProducerAgent
from agents.creative_director import CreativeDirectorAgent
from agent_bus import GLOBAL_AGENT_BUS
from task_manager import TaskManager, TaskStatus
from graph_store import GraphStore
from memory_store import MemoryStore
from core.event_bus import EventBus
from core.audit_log import AuditLog
from config.settings import MODEL_CONFIG


class ProjectOrchestrator:
    """
    Single-project orchestrator using EventBus + AuditLog.
    
    NOTE: This is Phase 0 implementation. Will be replaced by
    async MultiProjectOrchestrator in Phase 1.
    """

    def __init__(self, project_name: str, poll_interval: float = 2.0):
        self.project_name = project_name
        self.poll_interval = poll_interval

        # Model configuration (from centralized config)
        self.fast_model_url = MODEL_CONFIG.fast_model_url
        self.model_mode = "fast"

        # Shared infrastructure
        self.event_bus = EventBus(project_name)
        self.audit_log = AuditLog(project_name)

        # Create agents
        self.producer = ProducerAgent(
            project_name=project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=self.fast_model_url,
            model_mode=self.model_mode,
        )

        self.creative_director = CreativeDirectorAgent(
            project_name=project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=self.fast_model_url,
            model_mode=self.model_mode,
        )

        self.tasks = TaskManager(project_name=project_name)
        self.graph = GraphStore(project_name=project_name)
        self.memory = MemoryStore(project_name=project_name)

        self._running = False

    def _ingest_continuity_messages(self):
        """
        Consume CRITIQUE messages from continuity and turn them into tasks.
        """
        messages = self.producer.get_continuity_critiques()
        for msg in messages:
            payload = msg.payload or {}
            self.tasks.add_task(
                task_type="SCENE_REVISION",
                payload={
                    "issues": payload.get("issues"),
                    "original_text": payload.get("original_text"),
                    "raw_output": payload.get("raw_output"),
                },
            )
            # Also create a meta-task for the creative director
            self.tasks.add_task(
                task_type="SCENE_CRITIQUE_ANALYSIS",
                payload={
                    "issues": payload.get("issues"),
                    "original_text": payload.get("original_text"),
                },
            )

    def _execute_task(self, task) -> None:
        """Execute a single task"""
        if task.type == "SCENE_REVISION":
            self._run_scene_revision(task)
        elif task.type == "SCENE_CRITIQUE_ANALYSIS":
            self._run_critique_analysis(task)
        else:
            self.tasks.update_status(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"Unknown task type: {task.type}",
            )

    def _run_scene_revision(self, task) -> None:
        """Handle scene revision task"""
        payload = task.payload or {}
        issues = payload.get("issues", "")
        original_text = payload.get("original_text", "")
        raw_output = payload.get("raw_output", "")

        # Log a summary into memory
        summary = f"[SCENE REVISION TASK]\nIssues:\n{issues}\n\nOriginal:\n{original_text[:500]}..."
        self.memory.add(summary)

        # Log to audit
        self.audit_log.append(
            event_type="task_completed",
            sender="orchestrator",
            recipient="system",
            payload={"task_id": task.id, "type": "SCENE_REVISION"}
        )

        self.tasks.update_status(task.id, TaskStatus.DONE)

    def _run_critique_analysis(self, task) -> None:
        """Use Creative Director to derive canon rules from critiques"""
        payload = task.payload or {}
        issues = payload.get("issues", "")
        original_text = payload.get("original_text", "")

        result = self.creative_director.analyze_scene_critique(
            issues=issues,
            original_text=original_text,
        )

        core_problems = result.get("core_problems", [])
        proposed_rules = result.get("proposed_canon_rules", [])
        guidance = result.get("guidance", "")

        # Store problems summary in memory
        if core_problems:
            problems_text = "\n".join(f"- {p}" for p in core_problems)
            self.memory.add(f"[CREATIVE DIRECTOR PROBLEMS]\n{problems_text}")

        # Log canon rules in graph + memory
        self.creative_director.log_canon_rules(proposed_rules)

        # Broadcast guidance to agents
        self.creative_director.send_guidance_message(guidance)

        # Log to audit
        self.audit_log.append(
            event_type="task_completed",
            sender="orchestrator",
            recipient="system",
            payload={"task_id": task.id, "type": "SCENE_CRITIQUE_ANALYSIS"}
        )

        self.tasks.update_status(task.id, TaskStatus.DONE)

    def tick(self):
        """One cycle of orchestration"""
        # 1) Ingest continuity messages into tasks
        self._ingest_continuity_messages()

        # 2) Execute one pending task
        task = self.tasks.get_next_pending()
        if task:
            self.tasks.update_status(task.id, TaskStatus.RUNNING)
            try:
                self._execute_task(task)
            except Exception as e:
                self.tasks.update_status(
                    task.id, TaskStatus.FAILED, error=str(e)
                )

    def run_forever(self):
        """Blocking loop; call from a separate process/script"""
        self._running = True
        print(f"[Orchestrator] Starting loop for project '{self.project_name}'")
        try:
            while self._running:
                self.tick()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("\n[Orchestrator] Stopped by user.")
            self._running = False