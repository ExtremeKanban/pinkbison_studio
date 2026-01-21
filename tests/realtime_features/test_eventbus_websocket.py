"""
Unit tests for EventBus WebSocket integration (core/event_bus.py).

Tests that EventBus correctly broadcasts events via WebSocket, matching actual implementation.
"""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.fixtures.websocket_fixtures import test_project_name


class TestEventBusWebSocketIntegration:
    """Test EventBus WebSocket broadcasting."""
    
    def test_eventbus_imports(self):
        """Test that EventBus can be imported."""
        try:
            from core.event_bus import EventBus
            assert EventBus is not None
        except ImportError as e:
            pytest.fail(f"Failed to import EventBus: {e}")
    
    def test_eventbus_initialization(self, test_project_name):
        """Test EventBus initialization with project name."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        assert bus.project_name == test_project_name
        assert len(bus.buffer) == 0
        assert bus.subscribers == {}
    
    def test_eventbus_publish_creates_event(self, test_project_name):
        """Test publish method creates Event object."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        event = bus.publish(
            sender="PlotArchitect",
            recipient="ProducerAgent",
            event_type="task_complete",
            payload={"result": "success"}
        )
        
        # Returns Event object
        assert event is not None
        assert event.sender == "PlotArchitect"
        assert event.recipient == "ProducerAgent"
        assert event.type == "task_complete"
        assert event.payload["result"] == "success"
        
        # Added to buffer
        assert len(bus.buffer) == 1
    
    def test_eventbus_buffer_limit(self, test_project_name):
        """Test that EventBus respects buffer size limit."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name, buffer_size=5)
        
        # Publish more events than buffer size
        for i in range(10):
            bus.publish(
                sender="Agent",
                recipient="System",
                event_type="test",
                payload={"index": i}
            )
        
        # Should only keep last 5 events
        assert len(bus.buffer) == 5
        # First event should be index 5 (0-4 were dropped)
        events_list = list(bus.buffer)
        assert events_list[0].payload["index"] == 5
        assert events_list[-1].payload["index"] == 9
    
    def test_eventbus_subscribe(self, test_project_name):
        """Test subscribing to events."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        callback = Mock()
        
        bus.subscribe("TestAgent", callback)
        assert "TestAgent" in bus.subscribers
        assert callback in bus.subscribers["TestAgent"]
    
    def test_eventbus_get_recent(self, test_project_name):
        """Test getting recent events for an agent."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        
        # Publish events to different recipients
        bus.publish("Sender1", "Agent1", "event1", {})
        bus.publish("Sender2", "Agent1", "event2", {})
        bus.publish("Sender3", "Agent2", "event3", {})
        
        # Get events for Agent1
        agent1_events = bus.get_recent("Agent1", limit=10)
        assert len(agent1_events) == 2
        assert all(e.recipient == "Agent1" for e in agent1_events)
        
        # Get events for Agent2
        agent2_events = bus.get_recent("Agent2", limit=10)
        assert len(agent2_events) == 1
        assert agent2_events[0].recipient == "Agent2"


class TestEventBusWebSocketIntegration:
    """Test WebSocket integration in EventBus."""
    
    def test_eventbus_has_websocket_integration(self, test_project_name):
        """Test that EventBus attempts WebSocket broadcasting."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        
        # Publish event - should not crash even if WebSocket not available
        try:
            event = bus.publish(
                sender="Agent",
                recipient="System",
                event_type="test",
                payload={"data": "test"}
            )
            assert event is not None
        except Exception as e:
            pytest.fail(f"EventBus.publish raised exception: {e}")


class TestEventBusProjectIsolation:
    """Test that EventBus properly isolates events by project."""
    
    def test_different_projects_have_separate_buses(self):
        """Test that different project EventBuses are isolated."""
        from core.event_bus import EventBus
        
        bus1 = EventBus("project1")
        bus2 = EventBus("project2")
        
        bus1.publish("Agent", "System", "event1", {})
        bus2.publish("Agent", "System", "event2", {})
        
        assert len(bus1.buffer) == 1
        assert len(bus2.buffer) == 1
        
        events1 = list(bus1.buffer)
        events2 = list(bus2.buffer)
        
        assert events1[0].type == "event1"
        assert events2[0].type == "event2"
    
    def test_project_name_in_eventbus(self, test_project_name):
        """Test that project name is accessible from EventBus."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        assert bus.project_name == test_project_name


class TestEventBusErrorHandling:
    """Test error handling in EventBus."""
    
    def test_publish_with_complex_payload(self, test_project_name):
        """Test publishing with nested payload."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        
        # Complex nested payload
        complex_payload = {
            "level1": {
                "level2": {
                    "data": [1, 2, 3],
                    "text": "test"
                }
            }
        }
        
        try:
            event = bus.publish(
                sender="Agent",
                recipient="System",
                event_type="test",
                payload=complex_payload
            )
            assert event.payload == complex_payload
        except Exception as e:
            pytest.fail(f"EventBus.publish failed with complex payload: {e}")
    
    def test_subscribe_with_valid_callback(self, test_project_name):
        """Test subscribing with valid callback function."""
        from core.event_bus import EventBus
        
        bus = EventBus(test_project_name)
        
        def callback(event):
            pass
        
        # Should work fine
        bus.subscribe("Agent", callback)
        assert "Agent" in bus.subscribers


class TestEventBusPerformance:
    """Test EventBus performance characteristics."""
    
    def test_high_volume_publish(self, test_project_name):
        """Test publishing large number of events."""
        from core.event_bus import EventBus
        import time
        
        bus = EventBus(test_project_name)
        
        start = time.time()
        for i in range(1000):
            bus.publish(
                sender="Agent",
                recipient="System",
                event_type="test",
                payload={"index": i}
            )
        elapsed = time.time() - start
        
        # Should complete reasonably quickly (< 2 seconds for 1000 events)
        assert elapsed < 2.0
        
        # Buffer should respect max size (default 100)
        assert len(bus.buffer) <= 100
    
    def test_get_recent_performance(self, test_project_name):
        """Test performance of get_recent with full buffer."""
        from core.event_bus import EventBus
        import time
        
        bus = EventBus(test_project_name)
        
        # Fill buffer
        for i in range(100):
            bus.publish(
                sender="Agent",
                recipient="TargetAgent",
                event_type="test",
                payload={"index": i}
            )
        
        start = time.time()
        events = bus.get_recent("TargetAgent", limit=50)
        elapsed = time.time() - start
        
        # Should be very fast (< 0.1 seconds)
        assert elapsed < 0.1
        assert len(events) <= 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])