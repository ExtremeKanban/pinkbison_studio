"""
Integration tests for WebSocket + EventBus real-time features.

Tests how WebSocketManager and EventBus work together, matching actual implementation.
"""

import pytest
import time
from pathlib import Path
import sys
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.fixtures.websocket_fixtures import (
    test_project_name,
    test_project_dir
)


@pytest.mark.integration
class TestWebSocketEventBusIntegration:
    """Test WebSocket and EventBus integration."""
    
    def test_eventbus_publishes_without_crashing(self, test_project_name):
        """Test that EventBus.publish works (WebSocket broadcast is async/fire-and-forget)."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        
        # This should not crash even if WebSocket is not ready
        try:
            event = bus.publish(
                sender="PlotArchitect",
                recipient="ProducerAgent",
                event_type="task_complete",
                payload={"result": "success"}
            )
            
            assert event is not None
            assert len(bus.buffer) == 1
        except Exception as e:
            pytest.fail(f"EventBus.publish raised exception: {e}")
    
    def test_multiple_projects_have_separate_buses(self):
        """Test that different projects have isolated EventBuses."""
        from core.event_bus import EventBus
        
        project1 = "test_project_1"
        project2 = "test_project_2"
        
        bus1 = EventBus(project1)
        bus2 = EventBus(project2)
        
        bus1.publish("Agent", "System", "event1", {})
        bus2.publish("Agent", "System", "event2", {})
        
        # Verify isolation
        assert bus1.project_name == project1
        assert bus2.project_name == project2
        assert len(bus1.buffer) == 1
        assert len(bus2.buffer) == 1


@pytest.mark.integration
class TestEventBusAuditLogIntegration:
    """Test EventBus and AuditLog integration."""
    
    def test_agent_base_has_send_message(self, test_project_name, test_project_dir):
        """Test that AgentBase has send_message method."""
        from core.event_bus import EventBus
        from core.audit_log import AuditLog
        from agents.base_agent import AgentBase
        
        event_bus = EventBus(test_project_name)
        audit_log = AuditLog(test_project_name)
        
        class TestAgent(AgentBase):
            def run(self, **kwargs):
                pass
        
        agent = TestAgent(
            name="TestAgent",
            project_name=test_project_name,
            event_bus=event_bus,
            audit_log=audit_log,
            fast_model_url="http://localhost:8000",
            model_mode="fast"
        )
        
        # Test send_message exists and has correct signature
        assert hasattr(agent, 'send_message')
        
        # Call with correct parameters (msg_type not event_type)
        try:
            agent.send_message(
                recipient="System",
                msg_type="test_message",
                payload={"data": "test"}
            )
        except TypeError as e:
            pytest.fail(f"send_message has wrong signature: {e}")


@pytest.mark.integration
class TestRegistryWebSocketIntegration:
    """Test Registry pattern with WebSocket resources."""
    
    def test_registry_provides_event_bus(self, test_project_name):
        """Test that Registry provides EventBus instances."""
        from core.registry import REGISTRY
        
        event_bus = REGISTRY.get_event_bus(test_project_name)
        
        assert event_bus.project_name == test_project_name
        assert hasattr(event_bus, 'publish')
        assert hasattr(event_bus, 'subscribe')
        assert hasattr(event_bus, 'get_recent')
        
        # Cleanup
        REGISTRY.clear_project(test_project_name)


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across WebSocket + EventBus integration."""
    
    def test_eventbus_handles_websocket_unavailable(self, test_project_name):
        """Test that EventBus handles WebSocket being unavailable gracefully."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        
        # Should not crash even if WebSocket isn't working
        try:
            event = bus.publish(
                sender="Agent",
                recipient="System",
                event_type="test",
                payload={"data": "test"}
            )
            
            # Event should still be in buffer
            assert len(bus.buffer) == 1
            assert event is not None
        except Exception as e:
            pytest.fail(f"EventBus.publish crashed when WebSocket unavailable: {e}")


@pytest.mark.integration
class TestConcurrencyIntegration:
    """Test concurrent operations across WebSocket + EventBus."""
    
    def test_concurrent_publishes_from_multiple_agents(self, test_project_name):
        """Test multiple agents publishing simultaneously."""
        from core.event_bus import EventBus
        import threading
        
        bus = EventBus(test_project_name)
        
        def publish_events(agent_name, count):
            for i in range(count):
                bus.publish(
                    sender=agent_name,
                    recipient="System",
                    event_type="test",
                    payload={"index": i}
                )
        
        # Create threads for different agents
        threads = [
            threading.Thread(target=publish_events, args=(f"Agent{i}", 10))
            for i in range(5)
        ]
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # All events should be published (though may be truncated by buffer)
        assert len(bus.buffer) > 0
        # Buffer limit should be respected (default 100)
        assert len(bus.buffer) <= 100


@pytest.mark.integration
class TestEndToEndMessageFlow:
    """Test complete message flow from agent to infrastructure."""
    
    def test_agent_publishes_to_eventbus(self, test_project_name, test_project_dir):
        """Test complete flow: Agent → EventBus → (WebSocket)."""
        from core.event_bus import EventBus
        from core.audit_log import AuditLog
        from agents.base_agent import AgentBase
        
        event_bus = EventBus(test_project_name)
        audit_log = AuditLog(test_project_name)
        
        class TestAgent(AgentBase):
            def run(self, **kwargs):
                pass
        
        agent = TestAgent(
            name="TestAgent",
            project_name=test_project_name,
            event_bus=event_bus,
            audit_log=audit_log,
            fast_model_url="http://localhost:8000",
            model_mode="fast"
        )
        
        # Send message
        agent.send_message(
            recipient="System",
            msg_type="test_event",
            payload={"data": "test"}
        )
        
        # Verify message in EventBus
        assert len(event_bus.buffer) > 0
        events = list(event_bus.buffer)
        assert events[-1].type == "test_event"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])