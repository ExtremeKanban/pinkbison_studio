"""
Async multi-project orchestrator.
Manages multiple projects in a single event loop.
"""

import asyncio
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

from core.registry import REGISTRY
from agents.producer import ProducerAgent
from agents.creative_director import CreativeDirectorAgent
from task_manager import TaskStatus, TaskManager
from config.settings import MODEL_CONFIG


class ProjectStatus(Enum):
    """Status of a project within the orchestrator."""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ProjectContext:
    """All runtime state for a single project."""
    project_name: str
    status: ProjectStatus = ProjectStatus.ACTIVE
    
    # Infrastructure (via Registry)
    event_bus = None  # Will be populated
    audit_log = None  # Will be populated
    memory = None  # Will be populated
    graph = None  # Will be populated
    tasks = None  # Will be populated
    output_manager = None  # Will be populated
    
    # Statistics
    tasks_processed: int = 0
    last_processed: Optional[float] = None
    error_count: int = 0
    
    def __post_init__(self):
        """Initialize infrastructure from Registry."""
        self.event_bus = REGISTRY.get_event_bus(self.project_name)
        self.audit_log = REGISTRY.get_audit_log(self.project_name)
        self.memory = REGISTRY.get_memory_store(self.project_name)
        self.graph = REGISTRY.get_graph_store(self.project_name)
        self.tasks = REGISTRY.get_task_manager(self.project_name)
        self.output_manager = REGISTRY.get_output_manager(self.project_name)
    
    def create_producer(self) -> ProducerAgent:
        """Create fresh ProducerAgent instance."""
        return ProducerAgent(
            project_name=self.project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=MODEL_CONFIG.fast_model_url,
            model_mode="fast",
        )
    
    def create_creative_director(self) -> CreativeDirectorAgent:
        """Create fresh CreativeDirectorAgent instance."""
        return CreativeDirectorAgent(
            name="creative_director",
            project_name=self.project_name,
            event_bus=self.event_bus,
            audit_log=self.audit_log,
            fast_model_url=MODEL_CONFIG.fast_model_url,
            model_mode="fast",
        )


class MultiProjectOrchestrator:
    """
    Single orchestrator managing multiple projects.
    
    Design:
    - Async event loop for non-blocking I/O
    - Round-robin scheduling across projects
    - Configurable time slices per project
    - Resource limits per project
    - Graceful project pause/resume/stop
    """
    
    def __init__(
        self,
        poll_interval: float = 0.1,  # Fast polling for responsiveness
        max_projects: int = 10,
    ):
        self.poll_interval = poll_interval
        self.max_projects = max_projects
        
        # Project management
        self.projects: Dict[str, ProjectContext] = {}
        self.active_projects: Set[str] = set()
        
        # Event loop state
        self._running = False
        self._loop = None
        
        # Statistics
        self.total_tasks_processed = 0
        self.start_time = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    # === Project Management ===
    
    def add_project(self, project_name: str) -> ProjectContext:
        """
        Add a project to the orchestrator.
        
        Args:
            project_name: Name of project to add
            
        Returns:
            ProjectContext for the added project
            
        Raises:
            ValueError: If project already exists or max projects reached
        """
        if project_name in self.projects:
            raise ValueError(f"Project '{project_name}' already managed")
        
        if len(self.projects) >= self.max_projects:
            raise ValueError(f"Max projects ({self.max_projects}) reached")
        
        context = ProjectContext(project_name=project_name)
        self.projects[project_name] = context
        self.active_projects.add(project_name)
        
        self.logger.info(f"Added project '{project_name}' to orchestrator")
        return context
    
    def remove_project(self, project_name: str) -> None:
        """
        Remove a project from the orchestrator.
        
        Args:
            project_name: Name of project to remove
        """
        if project_name in self.projects:
            del self.projects[project_name]
            self.active_projects.discard(project_name)
            REGISTRY.clear_project(project_name)
            self.logger.info(f"Removed project '{project_name}' from orchestrator")
    
    def pause_project(self, project_name: str) -> None:
        """Pause processing for a project."""
        if project_name in self.projects:
            self.projects[project_name].status = ProjectStatus.PAUSED
            self.active_projects.discard(project_name)
            self.logger.info(f"Paused project '{project_name}'")
    
    def resume_project(self, project_name: str) -> None:
        """Resume processing for a project."""
        if project_name in self.projects:
            self.projects[project_name].status = ProjectStatus.ACTIVE
            self.active_projects.add(project_name)
            self.logger.info(f"Resumed project '{project_name}'")
    
    def get_project_stats(self, project_name: str) -> Dict:
        """Get statistics for a project."""
        if project_name not in self.projects:
            return {}
        
        ctx = self.projects[project_name]
        return {
            "project_name": project_name,
            "status": ctx.status.value,
            "tasks_processed": ctx.tasks_processed,
            "error_count": ctx.error_count,
            "last_processed": ctx.last_processed,
            "pending_tasks": len([t for t in ctx.tasks.get_all() 
                                if t.status == TaskStatus.PENDING]),
        }
    
    def list_projects(self) -> List[Dict]:
        """List all managed projects with stats."""
        return [
            self.get_project_stats(project_name)
            for project_name in self.projects
        ]
    
    def _get_next_processable_task(self, ctx: ProjectContext):
        """
        Get the next task that we know how to process.
        Skips unknown task types.
        """
        processable_types = {"SCENE_REVISION", "SCENE_CRITIQUE_ANALYSIS"}
        
        for task in ctx.tasks.get_all():
            if task.status == TaskStatus.PENDING and task.type in processable_types:
                return task
        
        return None
    
    # === Core Orchestration Loop ===
    
    async def _process_project(self, project_name: str) -> None:
        """
        Process one tick for a single project.
        
        This is the async version of the old ProjectOrchestrator.tick()
        """
        ctx = self.projects[project_name]
        
        try:
            # 1. Ingest continuity messages into tasks
            await self._ingest_continuity_messages(ctx)
            
            # 2. Get next PROCESSABLE task (only types we know)
            task = self._get_next_processable_task(ctx)
            if task:
                await self._execute_task(ctx, task)
            
            # 3. Update statistics
            ctx.last_processed = time.time()
            if task:
                ctx.tasks_processed += 1
                self.total_tasks_processed += 1
            
        except Exception as e:
            ctx.error_count += 1
            self.logger.error(f"Error processing project '{project_name}': {e}")
            
            # If too many errors, pause the project
            if ctx.error_count >= 10:
                self.pause_project(project_name)
                ctx.status = ProjectStatus.ERROR
                self.logger.error(f"Paused project '{project_name}' due to errors")
    
    async def _ingest_continuity_messages(self, ctx: ProjectContext) -> None:
        """
        Ingest CRITIQUE messages from EventBus and create tasks.
        
        Note: Since ProducerAgent is synchronous, run in thread pool.
        """
        loop = asyncio.get_event_loop()
        
        def sync_ingest():
            producer = ctx.create_producer()
            
            # Note: This method needs to exist in ProducerAgent
            # If not, we'll handle it gracefully
            try:
                messages = producer.get_continuity_critiques()
                return messages
            except AttributeError:
                # Fallback: Just return empty list
                self.logger.warning(f"ProducerAgent.get_continuity_critiques() not found for {ctx.project_name}")
                return []
        
        messages = await loop.run_in_executor(None, sync_ingest)
        
        for msg in messages:
            payload = msg.payload or {}
            ctx.tasks.add_task(
                task_type="SCENE_REVISION",
                payload={
                    "issues": payload.get("issues", ""),
                    "original_text": payload.get("original_text", ""),
                    "raw_output": payload.get("raw_output", ""),
                },
            )
            ctx.tasks.add_task(
                task_type="SCENE_CRITIQUE_ANALYSIS",
                payload={
                    "issues": payload.get("issues", ""),
                    "original_text": payload.get("original_text", ""),
                },
            )
    
    async def _execute_task(self, ctx: ProjectContext, task) -> None:
        """Execute a single task asynchronously."""
        ctx.tasks.update_status(task.id, TaskStatus.RUNNING)
        
        try:
            loop = asyncio.get_event_loop()
            
            if task.type == "SCENE_REVISION":
                await self._run_scene_revision(ctx, task)
            elif task.type == "SCENE_CRITIQUE_ANALYSIS":
                await self._run_critique_analysis(ctx, task)
            else:
                raise ValueError(f"Unknown task type: {task.type}")
            
            ctx.tasks.update_status(task.id, TaskStatus.DONE)
            
        except Exception as e:
            ctx.tasks.update_status(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=str(e),
            )
            raise
    
    async def _run_scene_revision(self, ctx: ProjectContext, task) -> None:
        """Async version of scene revision."""
        payload = task.payload or {}
        
        # Safely extract fields with defaults
        issues = str(payload.get("issues", ""))
        original_text = str(payload.get("original_text", ""))
        raw_output = str(payload.get("raw_output", ""))
        
        # Store in memory
        summary = f"[SCENE REVISION TASK]\nIssues:\n{issues}\n\nOriginal:\n{original_text[:500]}..."
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, ctx.memory.add, summary)
        
        # Log to audit
        ctx.audit_log.append(
            event_type="task_completed",
            sender="orchestrator",
            recipient="system",
            payload={"task_id": task.id, "type": "SCENE_REVISION"}
        )
    
    async def _run_critique_analysis(self, ctx: ProjectContext, task) -> None:
        """Async version of critique analysis."""
        payload = task.payload or {}
        
        # Safely extract fields with defaults
        issues = str(payload.get("issues", ""))
        original_text = str(payload.get("original_text", ""))
        
        loop = asyncio.get_event_loop()
        
        def sync_analysis():
            creative_director = ctx.create_creative_director()
            
            # Check if method exists
            if hasattr(creative_director, 'analyze_scene_critique'):
                return creative_director.analyze_scene_critique(
                    issues=issues,
                    original_text=original_text,
                )
            else:
                # Fallback: return empty result
                self.logger.warning(f"CreativeDirectorAgent.analyze_scene_critique() not found for {ctx.project_name}")
                return {
                    "core_problems": [],
                    "proposed_canon_rules": [],
                    "guidance": "",
                }
        
        result = await loop.run_in_executor(None, sync_analysis)
        
        core_problems = result.get("core_problems", [])
        proposed_rules = result.get("proposed_canon_rules", [])
        guidance = result.get("guidance", "")
        
        # Store problems in memory
        if core_problems:
            problems_text = "\n".join(f"- {p}" for p in core_problems)
            await loop.run_in_executor(
                None, ctx.memory.add, 
                f"[CREATIVE DIRECTOR PROBLEMS]\n{problems_text}"
            )
        
        # Log canon rules (this is sync)
        def sync_log_rules():
            creative_director = ctx.create_creative_director()
            if hasattr(creative_director, 'log_canon_rules'):
                creative_director.log_canon_rules(proposed_rules)
        
        await loop.run_in_executor(None, sync_log_rules)
        
        # Broadcast guidance
        def sync_broadcast():
            creative_director = ctx.create_creative_director()
            if hasattr(creative_director, 'send_guidance_message'):
                creative_director.send_guidance_message(guidance)
        
        await loop.run_in_executor(None, sync_broadcast)
        
        # Log to audit
        ctx.audit_log.append(
            event_type="task_completed",
            sender="orchestrator",
            recipient="system",
            payload={"task_id": task.id, "type": "SCENE_CRITIQUE_ANALYSIS"}
        )
    
    # === Main Orchestration Loop ===
    
    async def _orchestration_loop(self) -> None:
        """Main async orchestration loop."""
        self.logger.info("Starting multi-project orchestration loop")
        self.start_time = time.time()
        
        while self._running:
            start_cycle = time.time()
            
            # Process each active project
            for project_name in list(self.active_projects):
                try:
                    await self._process_project(project_name)
                    
                    # Small delay between projects for fairness
                    await asyncio.sleep(0.01)
                    
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    self.logger.error(f"Error in project '{project_name}' loop: {e}")
            
            # Rate limiting: sleep if we processed too quickly
            cycle_time = time.time() - start_cycle
            if cycle_time < self.poll_interval:
                await asyncio.sleep(self.poll_interval - cycle_time)
        
        self.logger.info("Orchestration loop stopped")
    
    def run_forever(self) -> None:
        """
        Start the orchestrator and run forever.
        
        This is a synchronous wrapper around the async loop.
        """
        self._running = True
        
        try:
            # Create new event loop for this thread
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            # Run the orchestration loop
            self._loop.run_until_complete(self._orchestration_loop())
            
        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
        finally:
            self._running = False
            if self._loop and not self._loop.is_closed():
                self._loop.close()
    
    def stop(self) -> None:
        """Gracefully stop the orchestrator."""
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
    
    def auto_discover_projects(self) -> List[str]:
        """
        Automatically discover projects in project_state/ directory.
        
        Returns:
            List of project names discovered
        """
        projects = []
        base_dir = Path("project_state")
        
        if not base_dir.exists():
            return projects
        
        for item in base_dir.iterdir():
            if item.is_dir():
                # Check if it has a state.json file
                state_file = item / "state.json"
                if state_file.exists():
                    projects.append(item.name)
        
        return projects
    
    def add_all_discovered_projects(self) -> List[str]:
        """
        Add all discovered projects to the orchestrator.
        
        Returns:
            List of project names added
        """
        discovered = self.auto_discover_projects()
        added = []
        
        for project_name in discovered:
            if project_name not in self.projects:
                try:
                    self.add_project(project_name)
                    added.append(project_name)
                except ValueError as e:
                    self.logger.warning(f"Could not add project '{project_name}': {e}")
        
        return added