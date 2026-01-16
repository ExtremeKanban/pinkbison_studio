# Testing Requirements

## Testing Philosophy

**Every new feature needs:**
1. **Unit tests** - Test individual components
2. **Integration tests** - Test component interactions
3. **Smoke test** - Verify end-to-end workflows

**Tests should be:**
- Fast (unit tests < 1s, integration tests < 10s)
- Isolated (no dependencies on other tests)
- Repeatable (same result every time)
- Clear (test name explains what's tested)

---

## Test Organization
```
tests/
├── migrations/              # Migration verification
│   ├── test_phase_0_migration.py
│   └── test_phase_1_migration.py
├── unit/                    # Fast, isolated tests
│   ├── core/
│   │   ├── test_event_bus.py
│   │   ├── test_audit_log.py
│   │   └── test_project_state.py
│   ├── agents/
│   │   ├── test_plot_architect.py
│   │   └── test_worldbuilder.py
│   └── models/
│       └── test_fast_model_client.py
├── integration/             # Multi-component tests
│   ├── test_story_bible_pipeline.py
│   ├── test_scene_pipeline.py
│   └── test_feedback_routing.py
├── smoke_test.py            # End-to-end verification
└── conftest.py              # Pytest fixtures
```

---

## Unit Test Requirements

### New Core Components

**Every new core component needs:**
```python
# tests/unit/core/test_new_component.py

def test_new_component_creation():
    """Verify component can be instantiated"""
    component = NewComponent(required_param="value")
    assert component.required_param == "value"

def test_new_component_basic_operation():
    """Verify basic operation works"""
    component = NewComponent()
    result = component.do_something()
    assert result is not None

def test_new_component_error_handling():
    """Verify errors are handled correctly"""
    component = NewComponent()
    with pytest.raises(ValueError):
        component.do_something(invalid_param=None)

def test_new_component_edge_cases():
    """Verify edge cases handled"""
    component = NewComponent()
    
    # Empty input
    assert component.process("") == ""
    
    # Very large input
    large_input = "x" * 100000
    result = component.process(large_input)
    assert len(result) > 0
```

### New Agents

**Every new agent needs:**
```python
# tests/unit/agents/test_new_agent.py
import pytest
from core.event_bus import EventBus
from core.audit_log import AuditLog
from core.agent_factory import AgentFactory

@pytest.fixture
def agent_factory():
    """Create factory for testing"""
    event_bus = EventBus("test_project")
    audit_log = AuditLog("test_project")
    
    return AgentFactory(
        project_name="test_project",
        event_bus=event_bus,
        audit_log=audit_log,
        fast_model_url="http://localhost:8000/v1/chat/completions",
        model_mode="fast"
    )

def test_new_agent_creation(agent_factory):
    """Verify agent can be created via factory"""
    agent = agent_factory.create_new_agent()
    assert agent.name == "new_agent"
    assert agent.project_name == "test_project"

def test_new_agent_sends_message(agent_factory):
    """Verify agent can send messages"""
    agent = agent_factory.create_new_agent()
    
    # Send message
    agent.send_message(
        recipient="other_agent",
        msg_type="TEST",
        payload={"data": "value"}
    )
    
    # Verify message in EventBus
    recent = agent.event_bus.get_recent("other_agent", limit=1)
    assert len(recent) == 1
    assert recent[0].payload["data"] == "value"

def test_new_agent_receives_feedback(agent_factory):
    """Verify agent receives feedback from EventBus"""
    agent = agent_factory.create_new_agent()
    
    # Send feedback
    agent.event_bus.publish(
        sender="user",
        recipient=agent.name,
        event_type="feedback",
        payload={"content": "test feedback", "type": "feedback"}
    )
    
    # Agent should be able to retrieve it
    messages = agent.get_recent_messages(limit=5)
    feedback = [m for m in messages if m.get("type") == "feedback"]
    assert len(feedback) == 1

@pytest.mark.slow
def test_new_agent_run_basic(agent_factory):
    """Verify agent.run() produces output"""
    agent = agent_factory.create_new_agent()
    
    result = agent.run(test_input="Sample input")
    
    assert result is not None
    assert len(result) > 0
    assert isinstance(result, str)
```

---

## Integration Test Requirements

### Pipeline Tests

**Every new pipeline needs:**
```python
# tests/integration/test_new_pipeline.py
import pytest
from agents.producer import ProducerAgent
from core.event_bus import EventBus
from core.audit_log import AuditLog

@pytest.fixture
def producer():
    """Create ProducerAgent for testing"""
    event_bus = EventBus("test_project")
    audit_log = AuditLog("test_project")
    
    return ProducerAgent(
        project_name="test_project",
        event_bus=event_bus,
        audit_log=audit_log,
        fast_model_url="http://localhost:8000/v1/chat/completions",
        model_mode="fast"
    )

@pytest.mark.slow
@pytest.mark.integration
def test_new_pipeline_end_to_end(producer):
    """Verify pipeline runs without errors"""
    
    result = producer.run_new_pipeline(
        idea="Test idea",
        genre="Sci-Fi",
        tone="Epic",
        themes="Test themes",
        setting="Test setting",
        auto_memory=False  # Don't pollute memory in tests
    )
    
    # Verify expected outputs
    assert "expected_key" in result
    assert len(result["expected_key"]) > 0

@pytest.mark.slow
@pytest.mark.integration
def test_new_pipeline_with_feedback(producer):
    """Verify pipeline responds to feedback"""
    
    # Send feedback to agent
    producer.handle_feedback("plot_architect", "Test feedback")
    
    # Run pipeline
    result = producer.run_new_pipeline(...)
    
    # Verify feedback was incorporated (check audit log)
    feedback_entries = producer.audit_log.search(
        event_type="user_feedback",
        limit=10
    )
    assert len(feedback_entries) > 0
```

---

## Smoke Test Requirements

### When to Update Smoke Test

**Update `tests/smoke_test.py` when:**
- Adding new UI panel
- Adding new pipeline
- Changing workflow
- Adding required configuration

### Smoke Test Pattern
```python
# tests/smoke_test.py
from playwright.sync_api import sync_playwright

def test_new_feature():
    """Test new feature in UI"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto("http://localhost:8501")
        
        # Navigate to new feature
        page.click("text=New Feature Panel")
        
        # Fill in inputs
        page.fill("textarea[aria-label='New input']", "Test data")
        
        # Click action button
        page.click("text=Run New Feature")
        
        # Wait for completion
        wait_for_streamlit_to_finish(page)
        
        # Verify output
        wait_for_text(page, "Expected Output Text")
        wait_for_no_errors(page)
        
        browser.close()
```

---

## Test Fixtures (Shared Setup)

### Create `tests/conftest.py`
```python
# tests/conftest.py
import pytest
from pathlib import Path
import shutil
from core.event_bus import EventBus
from core.audit_log import AuditLog
from core.agent_factory import AgentFactory
from core.project_state import ProjectState

@pytest.fixture
def test_project_name():
    """Unique test project name"""
    import uuid
    return f"test_project_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def event_bus(test_project_name):
    """Create EventBus for testing"""
    return EventBus(test_project_name)

@pytest.fixture
def audit_log(test_project_name):
    """Create AuditLog for testing"""
    log = AuditLog(test_project_name)
    yield log
    
    # Cleanup after test
    log_path = Path(f"audit_logs/{test_project_name}_audit.jsonl")
    if log_path.exists():
        log_path.unlink()

@pytest.fixture
def agent_factory(test_project_name, event_bus, audit_log):
    """Create AgentFactory for testing"""
    return AgentFactory(
        project_name=test_project_name,
        event_bus=event_bus,
        audit_log=audit_log,
        fast_model_url="http://localhost:8000/v1/chat/completions",
        model_mode="fast"
    )

@pytest.fixture
def project_state(test_project_name):
    """Create temporary project state"""
    state = ProjectState.create_default(test_project_name)
    state.save()
    
    yield state
    
    # Cleanup after test
    state_dir = Path(f"project_state/{test_project_name}")
    if state_dir.exists():
        shutil.rmtree(state_dir)
```

---

## Test Markers

### Define Pytest Markers

Create `pytest.ini`:
```ini
[pytest]
markers =
    slow: marks tests as slow (> 5 seconds)
    integration: marks tests as integration tests
    requires_model: marks tests that need LLM running
    requires_ui: marks tests that need Streamlit running
```

### Use Markers in Tests
```python
import pytest

@pytest.mark.slow
def test_expensive_operation():
    """This test takes a long time"""
    ...

@pytest.mark.integration
@pytest.mark.requires_model
def test_full_pipeline():
    """This test needs the model server running"""
    ...
```

### Run Specific Tests
```bash
# Run only fast tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run specific file
pytest tests/unit/core/test_event_bus.py

# Run specific test
pytest tests/unit/core/test_event_bus.py::test_event_bus_publish
```

---

## Mocking Guidelines

### When to Mock

**✅ Mock external dependencies:**
- LLM API calls
- File system operations (sometimes)
- Network requests

**❌ Don't mock internal components:**
- EventBus
- AuditLog
- ProjectState
- Agent interactions

### Mock LLM Calls
```python
import pytest
from unittest.mock import patch, Mock

@pytest.fixture
def mock_model_response():
    """Mock LLM response"""
    return {
        "choices": [{
            "message": {
                "content": "Mocked response text"
            }
        }]
    }

def test_agent_with_mock_model(agent_factory, mock_model_response):
    """Test agent without calling real model"""
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_model_response
        mock_post.return_value.raise_for_status = Mock()
        
        agent = agent_factory.create_plot_architect()
        result = agent.run(idea="Test", genre="Sci-Fi", ...)
        
        assert result == "Mocked response text"
        assert mock_post.called
```

---

## Test Data Management

### Test Data Location
```
tests/
├── test_data/
│   ├── sample_inputs.json
│   ├── sample_outline.txt
│   └── sample_world.txt
```

### Load Test Data
```python
import json
from pathlib import Path

def load_test_data(filename: str) -> dict:
    """Load test data from tests/test_data/"""
    path = Path(__file__).parent / "test_data" / filename
    with open(path) as f:
        return json.load(f)

def test_with_real_data():
    """Test using realistic data"""
    test_input = load_test_data("sample_inputs.json")
    
    agent = create_agent()
    result = agent.run(**test_input)
    
    assert len(result) > 100
```

---

## Coverage Requirements

### Minimum Coverage Targets
```
Overall:     70%+
Core modules: 90%+
Agents:      60%+
UI:          40%+ (hard to test Streamlit)
```

### Generate Coverage Report
```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=. --cov-report=html

# View report
open htmlcov/index.html
```

---

## Continuous Testing

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run fast tests before commit

echo "Running tests..."
pytest -m "not slow" --tb=short

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

### GitHub Actions (Future)
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest
```

---

## Summary

**Test Checklist for New Features:**
- [ ] Unit tests for core logic
- [ ] Integration tests for pipelines
- [ ] Smoke test updated if UI changed
- [ ] Test fixtures used for common setup
- [ ] Test markers added for slow/integration tests
- [ ] Mock external dependencies (LLM, network)
- [ ] Test data in `tests/test_data/`
- [ ] Coverage > 70% for new code

**Golden Rules:**
1. Write tests for new features before merging
2. Keep unit tests fast (< 1s each)
3. Use fixtures for common setup
4. Mock external dependencies
5. Don't mock internal components
6. Run full test suite before big changes

**When in doubt:** Look at existing tests for patterns!