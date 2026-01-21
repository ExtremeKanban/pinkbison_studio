"""
Test fixtures for WebSocket and real-time feature testing.

Provides reusable fixtures for creating test projects, WebSocket connections,
and mock components for testing real-time features.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, MagicMock


@pytest.fixture
def test_project_name() -> str:
    """Provide a unique test project name."""
    return "test_realtime_project"


@pytest.fixture
def test_project_dir(test_project_name: str) -> Generator[Path, None, None]:
    """
    Create a temporary project directory for testing.
    
    Yields:
        Path to temporary project directory
        
    Cleanup:
        Removes directory after test completes
    """
    project_dir = Path(f"project_state/{test_project_name}")
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (project_dir / "memory").mkdir(exist_ok=True)
    (project_dir / "outputs" / "chapters").mkdir(parents=True, exist_ok=True)
    (project_dir / "outputs" / "scenes").mkdir(parents=True, exist_ok=True)
    (project_dir / "outputs" / "drafts").mkdir(parents=True, exist_ok=True)
    
    # Create empty state.json
    state_file = project_dir / "state.json"
    state_file.write_text(json.dumps({
        "metadata": {
            "genre": "test",
            "tone": "test",
            "themes": [],
            "setting": "test"
        },
        "agent_outputs": {},
        "pipeline_history": [],
        "continuity_notes": [],
        "ui_inputs": {}
    }, indent=2))
    
    # Create empty graph.json
    graph_file = project_dir / "graph.json"
    graph_file.write_text(json.dumps({
        "entities": [],
        "relationships": [],
        "events": [],
        "canon_rules": []
    }, indent=2))
    
    # Create empty audit.jsonl
    audit_file = project_dir / "audit.jsonl"
    audit_file.touch()
    
    yield project_dir
    
    # Cleanup
    if project_dir.exists():
        shutil.rmtree(project_dir)


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection for testing."""
    ws = Mock()
    ws.send = Mock()
    ws.recv = Mock(return_value='{"type": "ping"}')
    ws.close = Mock()
    return ws


@pytest.fixture
def mock_streamlit_session_state() -> Dict[str, Any]:
    """Create a mock Streamlit session state for testing."""
    return {
        "websocket_messages": [],
        "websocket_connected": False,
        "websocket_client": None,
        "pipeline_status": "idle",
        "pipeline_progress": 0.0,
        "current_step": "",
        "feedback_queue": []
    }


@pytest.fixture
def sample_eventbus_message() -> Dict[str, Any]:
    """Create a sample EventBus message for testing."""
    return {
        "sender": "PlotArchitect",
        "recipient": "ProducerAgent",
        "event_type": "task_complete",
        "payload": {
            "task": "generate_outline",
            "status": "success",
            "result": "Generated story outline"
        },
        "timestamp": "2025-01-21T12:00:00"
    }


@pytest.fixture
def sample_pipeline_event() -> Dict[str, Any]:
    """Create a sample pipeline event for testing."""
    return {
        "type": "pipeline_update",
        "project_name": "test_realtime_project",
        "data": {
            "status": "running",
            "current_step": "Generating outline",
            "progress": 0.25,
            "total_steps": 4,
            "completed_steps": 1
        }
    }


@pytest.fixture
def sample_feedback_message() -> Dict[str, Any]:
    """Create a sample feedback message for testing."""
    return {
        "target_agent": "SceneGenerator",
        "feedback": "Make the scene more suspenseful",
        "priority": "high",
        "timestamp": "2025-01-21T12:00:00"
    }


@pytest.fixture
def mock_event_bus():
    """Create a mock EventBus for testing."""
    bus = Mock()
    bus.project_name = "test_realtime_project"
    bus.publish = Mock()
    bus.subscribe = Mock()
    bus.get_recent = Mock(return_value=[])
    bus._send_websocket = Mock()
    return bus


@pytest.fixture
def mock_audit_log():
    """Create a mock AuditLog for testing."""
    log = Mock()
    log.project_name = "test_realtime_project"
    log.append = Mock()
    log.search = Mock(return_value=[])
    log.get_recent = Mock(return_value=[])
    return log


@pytest.fixture
def mock_websocket_manager():
    """Create a mock WebSocketManager for testing."""
    manager = Mock()
    manager.server_started = True
    manager.broadcast_to_project = Mock()
    manager.add_subscriber = Mock()
    manager.remove_subscriber = Mock()
    manager.stop = Mock()
    return manager


@pytest.fixture
def test_agent_factory(mock_event_bus, mock_audit_log):
    """Create a mock AgentFactory for testing."""
    factory = Mock()
    factory.event_bus = mock_event_bus
    factory.audit_log = mock_audit_log
    factory.create_plot_architect = Mock()
    factory.create_worldbuilder = Mock()
    factory.create_character_agent = Mock()
    factory.create_scene_generator = Mock()
    return factory


class WebSocketTestHelper:
    """Helper class for WebSocket testing operations."""
    
    @staticmethod
    def create_connection_message(project_name: str) -> str:
        """Create a WebSocket connection message."""
        return json.dumps({
            "type": "subscribe",
            "project_name": project_name
        })
    
    @staticmethod
    def create_unsubscribe_message(project_name: str) -> str:
        """Create a WebSocket unsubscribe message."""
        return json.dumps({
            "type": "unsubscribe",
            "project_name": project_name
        })
    
    @staticmethod
    def create_event_message(event_type: str, data: Dict[str, Any]) -> str:
        """Create a WebSocket event message."""
        return json.dumps({
            "type": event_type,
            "data": data
        })
    
    @staticmethod
    def parse_websocket_message(message: str) -> Dict[str, Any]:
        """Parse a WebSocket message."""
        return json.loads(message)


@pytest.fixture
def ws_helper():
    """Provide WebSocket test helper."""
    return WebSocketTestHelper()


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "websocket: mark test as requiring WebSocket server"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as UI test (manual or automated)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )