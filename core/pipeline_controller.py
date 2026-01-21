"""
Async pipeline controller with pause/resume capabilities.
"""

import asyncio
import threading
import time
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field

from core.feedback_manager import FeedbackManager, FeedbackType, FeedbackPriority


class PipelineStatus(Enum):
    """Pipeline status states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class PipelineProgress:
    """Track pipeline progress."""
    step_number: int = 0
    total_steps: int = 0
    current_step: str = ""
    step_description: str = ""
    percent_complete: float = 0.0


class PipelineController:
    """
    Controls pipeline execution with real-time feedback integration.
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.status = PipelineStatus.IDLE
        self.progress = PipelineProgress()
        self.feedback_manager = FeedbackManager(project_name)
        self.current_task: Optional[str] = None
        self.pipeline_thread: Optional[threading.Thread] = None
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.lock = threading.RLock()
        
        # Callbacks for UI updates
        self.on_progress_update: Optional[Callable] = None
        self.on_status_change: Optional[Callable] = None
    
    def start_pipeline(
        self,
        pipeline_func: Callable,
        task_name: str,
        total_steps: int = 10,
        **kwargs
    ) -> bool:
        """
        Start a pipeline in a background thread.
        
        Args:
            pipeline_func: Function to run as pipeline
            task_name: Name of the task
            total_steps: Total number of steps
            **kwargs: Arguments to pass to pipeline_func
            
        Returns:
            True if pipeline started successfully
        """
        with self.lock:
            if self.status in [PipelineStatus.RUNNING, PipelineStatus.PAUSED]:
                return False
            
            # Reset state
            self.status = PipelineStatus.RUNNING
            self.progress = PipelineProgress(total_steps=total_steps)
            self.current_task = task_name
            self.stop_event.clear()
            self.pause_event.clear()
            
            # Start pipeline in background thread
            self.pipeline_thread = threading.Thread(
                target=self._run_pipeline,
                args=(pipeline_func, kwargs),
                daemon=True
            )
            self.pipeline_thread.start()
            
            # Notify status change
            if self.on_status_change:
                self.on_status_change(self.get_status())
            
            return True
    
    def _run_pipeline(self, pipeline_func: Callable, kwargs: Dict[str, Any]):
        """Internal method to run pipeline with status broadcasts."""
        try:
            # Broadcast start
            self._broadcast_status()
            
            # Call the pipeline function
            result = pipeline_func(
                controller=self,
                feedback_manager=self.feedback_manager,
                **kwargs
            )
            
            # Pipeline completed successfully
            with self.lock:
                self.status = PipelineStatus.COMPLETED
                self.progress.percent_complete = 100.0
                self.current_task = None
                self._broadcast_status()
        
        except Exception as e:
            # Pipeline failed
            with self.lock:
                self.status = PipelineStatus.ERROR
                self.current_task = f"Error: {str(e)}"
                self._broadcast_status()
        
        finally:
            # Notify status change
            if self.on_status_change:
                self.on_status_change(self.get_status())
    
    def _broadcast_status(self):
        """Broadcast current status via WebSocket."""
        try:
            from core.websocket_manager import WEBSOCKET_MANAGER
            if WEBSOCKET_MANAGER.running:
                WEBSOCKET_MANAGER.broadcast_pipeline_status(
                    self.project_name,
                    self.get_status()
                )
        except Exception as e:
            print(f"[PipelineController] Status broadcast error: {e}")

    def pause(self) -> bool:
        """Pause the running pipeline."""
        with self.lock:
            if self.status == PipelineStatus.RUNNING:
                self.status = PipelineStatus.PAUSED
                self.pause_event.set()
                
                if self.on_status_change:
                    self.on_status_change(self.get_status())
                return True
            return False
    
    def resume(self) -> bool:
        """Resume a paused pipeline."""
        with self.lock:
            if self.status == PipelineStatus.PAUSED:
                self.status = PipelineStatus.RUNNING
                self.pause_event.clear()
                
                if self.on_status_change:
                    self.on_status_change(self.get_status())
                return True
            return False
    
    def stop(self) -> bool:
        """Stop the pipeline."""
        with self.lock:
            if self.status in [PipelineStatus.RUNNING, PipelineStatus.PAUSED]:
                self.status = PipelineStatus.STOPPED
                self.stop_event.set()
                self.pause_event.set()  # Also release pause if applicable
                
                if self.on_status_change:
                    self.on_status_change(self.get_status())
                return True
            return False
    
    def update_progress(
        self,
        step_number: int,
        current_step: str,
        step_description: str = ""
    ) -> None:
        """
        Update pipeline progress with WebSocket broadcast.
        
        Args:
            step_number: Current step number (1-indexed)
            current_step: Name of current step
            step_description: Description of current step
        """
        with self.lock:
            if self.status != PipelineStatus.RUNNING:
                return
            
            self.progress.step_number = step_number
            self.progress.current_step = current_step
            self.progress.step_description = step_description
            
            if self.progress.total_steps > 0:
                self.progress.percent_complete = (
                    (step_number / self.progress.total_steps) * 100
                )
            
            # Broadcast progress via WebSocket
            try:
                from core.websocket_manager import WEBSOCKET_MANAGER
                if WEBSOCKET_MANAGER.running:
                    WEBSOCKET_MANAGER.broadcast_pipeline_progress(
                        self.project_name,
                        {
                            'step_number': step_number,
                            'total_steps': self.progress.total_steps,
                            'current_step': current_step,
                            'step_description': step_description,
                            'percent_complete': self.progress.percent_complete
                        }
                    )
            except Exception as e:
                print(f"[PipelineController] WebSocket broadcast error: {e}")
            
            # Check for pause
            if self.pause_event.is_set():
                self.status = PipelineStatus.PAUSED
                self.pause_event.wait()  # Wait until resume is called
                self.status = PipelineStatus.RUNNING
            
            # Check for stop
            if self.stop_event.is_set():
                raise InterruptedError("Pipeline stopped by user")
            
            # Notify progress update
            if self.on_progress_update:
                self.on_progress_update(self.get_status())
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status.
        
        Returns:
            Dictionary with status information
        """
        with self.lock:
            feedback_stats = self.feedback_manager.get_stats()
            
            return {
                "status": self.status.value,
                "current_task": self.current_task or "None",
                "progress": {
                    "step_number": self.progress.step_number,
                    "total_steps": self.progress.total_steps,
                    "current_step": self.progress.current_step,
                    "step_description": self.progress.step_description,
                    "percent_complete": self.progress.percent_complete,
                },
                "feedback_stats": feedback_stats,
                "is_running": self.status == PipelineStatus.RUNNING,
                "is_paused": self.status == PipelineStatus.PAUSED,
                "is_stopped": self.status in [PipelineStatus.STOPPED, PipelineStatus.COMPLETED, PipelineStatus.ERROR],
            }
    
    def inject_feedback(
        self,
        target_agent: str,
        content: str,
        feedback_type: FeedbackType = FeedbackType.GUIDANCE,
        priority: FeedbackPriority = FeedbackPriority.NORMAL,
        source: str = "user"
    ) -> str:
        """
        Inject feedback during pipeline execution.
        
        Args:
            target_agent: Target agent name or "ALL"
            content: Feedback content
            feedback_type: Type of feedback
            priority: Priority level
            source: Source of feedback
            
        Returns:
            Feedback message ID
        """
        return self.feedback_manager.add_feedback(
            target_agent=target_agent,
            feedback_type=feedback_type,
            content=content,
            priority=priority,
            source=source
        )
    
    def wait_for_resume(self) -> bool:
        """
        Wait if pipeline is paused.
        
        Returns:
            True if should continue, False if stopped
        """
        if self.pause_event.is_set():
            self.status = PipelineStatus.PAUSED
            if self.on_status_change:
                self.on_status_change(self.get_status())
            
            # Wait for resume
            self.pause_event.wait()
            
            if self.stop_event.is_set():
                return False
            
            self.status = PipelineStatus.RUNNING
            if self.on_status_change:
                self.on_status_change(self.get_status())
        
        return not self.stop_event.is_set()