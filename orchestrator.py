import time
from typing import Optional

from agents.producer import ProducerAgent
from agents.creative_director import CreativeDirectorAgent
from agent_bus import GLOBAL_AGENT_BUS
from task_manager import TaskManager, TaskStatus
from graph_store import GraphStore
from memory_store import MemoryStore


class ProjectOrchestrator:
    """
    Fully agentic orchestrator for a single project.
    Runs a background-style loop when invoked.
    """

    def __init__(self, project_name: str, poll_interval: float = 2.0):
        self.project_name = project_name
        self.poll_interval = poll_interval

        self.producer = ProducerAgent(project_name=project_name)
        self.creative_director = CreativeDirectorAgent(project_name=project_name)
        self.tasks = TaskManager(project_name=project_name)
        self.graph = GraphStore(project_name=project_name)
        self.memory = MemoryStore(project_name=project_name)

        self._running = False

    # ---------- Message ingestion → tasks ----------

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

    # ---------- Task execution ----------

    def _execute_task(self, task) -> None:
        """
        Execute a single task using ProducerAgent / other agents.
        """
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
        """
        For now, we simply mark the scene as 'noted' and store the issues in memory.
        Later, this can:
        - regenerate scene using ProducerAgent
        - apply fixes to the project state
        """
        payload = task.payload or {}
        issues = payload.get("issues", "")
        original_text = payload.get("original_text", "")
        raw_output = payload.get("raw_output", "")

        # Log a summary into memory
        summary = f"[SCENE REVISION TASK]\nIssues:\n{issues}\n\nOriginal:\n{original_text[:500]}..."
        self.memory.add(summary)

        # TODO: later: call ProducerAgent to auto-revise scenes using issues
        self.tasks.update_status(task.id, TaskStatus.DONE)

    def _run_critique_analysis(self, task) -> None:
        """
        Use Creative Director to derive canon rules and guidance from critiques.
        """
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

        self.tasks.update_status(task.id, TaskStatus.DONE)

    # ---------- Main loop ----------

    def tick(self):
        """
        One 'cycle' of orchestration:
        - ingest messages
        - pick a pending task
        - execute it
        """
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
        """
        Blocking loop; call from a separate process/script.
        """
        self._running = True
        print(f"[Orchestrator] Starting loop for project '{self.project_name}'")
        try:
            while self._running:
                self.tick()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("\n[Orchestrator] Stopped by user.")
            self._running = False
