"""
Test real-time workflow features.
"""

import asyncio
import time
import threading
import pytest
from unittest.mock import Mock, patch

from core.feedback_manager import FeedbackManager, FeedbackType, FeedbackPriority
from core.pipeline_controller import PipelineController, PipelineStatus


class TestRealTimeFeatures:
    """Test real-time workflow components."""
    
    @pytest.fixture
    def feedback_manager(self):
        """Create a FeedbackManager for testing."""
        return FeedbackManager("test_project")
    
    @pytest.fixture
    def pipeline_controller(self):
        """Create a PipelineController for testing."""
        # Mock registry components
        with patch('core.pipeline_controller.REGISTRY') as mock_registry:
            mock_event_bus = Mock()
            mock_audit_log = Mock()
            
            mock_registry.get_event_bus.return_value = mock_event_bus
            mock_registry.get_audit_log.return_value = mock_audit_log
            
            controller = PipelineController("test_project")
            return controller
    
    def test_feedback_manager_basics(self, feedback_manager):
        """Test basic FeedbackManager operations."""
        # Add feedback
        fb_id = feedback_manager.add_feedback(
            target_agent="plot_architect",
            feedback_type=FeedbackType.GUIDANCE,
            content="Make the outline more detailed",
            priority=FeedbackPriority.HIGH
        )
        
        assert fb_id is not None
        
        # Get feedback for agent
        feedback = feedback_manager.get_feedback_for_agent("plot_architect")
        assert len(feedback) == 1
        assert feedback[0].content == "Make the outline more detailed"
        
        # Mark as processed
        feedback_manager.mark_as_processed(fb_id)
        feedback = feedback_manager.get_feedback_for_agent("plot_architect")
        assert len(feedback) == 0  # Should be empty (unprocessed only)
        
        # Stats
        stats = feedback_manager.get_stats()
        assert stats["total"] == 1
        assert stats["processed"] == 1
        assert stats["unprocessed"] == 0
    
    def test_feedback_manager_thread_safety(self, feedback_manager):
        """Test thread safety of FeedbackManager."""
        results = []
        
        def add_feedback_thread(thread_id):
            for i in range(100):
                fb_id = feedback_manager.add_feedback(
                    target_agent=f"agent_{thread_id}",
                    feedback_type=FeedbackType.GUIDANCE,
                    content=f"Message {i} from thread {thread_id}",
                    priority=FeedbackPriority.NORMAL
                )
                results.append(fb_id)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_feedback_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify no data corruption
        stats = feedback_manager.get_stats()
        assert stats["total"] == 500  # 5 threads * 100 messages each
        
        # Verify all feedback IDs are unique
        assert len(set(results)) == 500
    
    def test_pipeline_controller_status(self, pipeline_controller):
        """Test PipelineController status management."""
        assert pipeline_controller.status == PipelineStatus.IDLE
        
        # Mock pipeline function
        async def mock_pipeline(**kwargs):
            await asyncio.sleep(0.1)
            return {"result": "test"}
        
        # Start pipeline
        pipeline_id = pipeline_controller.start_pipeline(
            pipeline_func=mock_pipeline,
            pipeline_type="test",
            pipeline_args={}
        )
        
        assert pipeline_id is not None
        assert pipeline_controller.status == PipelineStatus.RUNNING
        
        # Update progress
        pipeline_controller.update_progress(
            current_step="test_step",
            step_number=1,
            total_steps=3,
            description="Testing progress"
        )
        
        # Check progress
        status = pipeline_controller.get_status()
        assert status["progress"]["current_step"] == "test_step"
        assert status["progress"]["percent_complete"] > 0
        
        # Pause and resume
        assert pipeline_controller.pause_pipeline() == True
        assert pipeline_controller.status == PipelineStatus.PAUSED
        
        assert pipeline_controller.resume_pipeline() == True
        assert pipeline_controller.status == PipelineStatus.RUNNING
        
        # Stop
        assert pipeline_controller.stop_pipeline() == True
        assert pipeline_controller.status == PipelineStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_async_pipeline_execution(self, pipeline_controller):
        """Test async pipeline execution."""
        execution_steps = []
        
        async def test_pipeline(**kwargs):
            execution_steps.append("start")
            
            # Simulate work with pause checks
            for i in range(3):
                pipeline_controller.update_progress(
                    current_step=f"step_{i}",
                    step_number=i + 1,
                    total_steps=3,
                    description=f"Processing step {i}"
                )
                
                # Check for pause
                pipeline_controller.wait_if_paused()
                
                # Check for stop
                if pipeline_controller.should_stop():
                    return {"status": "stopped"}
                
                await asyncio.sleep(0.01)
                execution_steps.append(f"step_{i}_done")
            
            execution_steps.append("complete")
            return {"status": "complete"}
        
        # Start pipeline
        pipeline_id = pipeline_controller.start_pipeline(
            pipeline_func=test_pipeline,
            pipeline_type="test_async",
            pipeline_args={}
        )
        
        # Wait for completion
        time.sleep(0.5)
        
        # Check execution steps
        assert "start" in execution_steps
        assert "step_0_done" in execution_steps
        assert "complete" in execution_steps
        
        # Verify final status
        status = pipeline_controller.get_status()
        assert status["status"] == "completed"
    
    def test_feedback_integration(self, pipeline_controller):
        """Test feedback integration with pipeline."""
        feedback_manager = pipeline_controller.feedback_manager
        
        # Add feedback before pipeline would check it
        feedback_manager.add_feedback(
            target_agent="test_agent",
            feedback_type=FeedbackType.CORRECTION,
            content="Fix the character motivation",
            priority=FeedbackPriority.HIGH
        )
        
        # Simulate agent checking for feedback
        feedback = feedback_manager.get_feedback_for_agent("test_agent")
        assert len(feedback) == 1
        assert "Fix the character motivation" in feedback[0].content
        
        # Mark as processed
        feedback_manager.mark_as_processed(feedback[0].id)
        
        # Should not appear in unprocessed feedback
        feedback = feedback_manager.get_feedback_for_agent("test_agent")
        assert len(feedback) == 0


if __name__ == "__main__":
    # Run tests
    import sys
    pytest.main(sys.argv)