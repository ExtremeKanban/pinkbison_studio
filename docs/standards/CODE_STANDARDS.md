# PinkBison Creative Studio - Code Standards

## Table of Contents
1. [File Organization](#file-organization)
2. [Naming Conventions](#naming-conventions)
3. [Import Organization](#import-organization)
4. [Error Handling](#error-handling)
5. [Logging](#logging)
6. [Type Hints](#type-hints)
7. [Docstrings](#docstrings)
8. [Configuration](#configuration)
9. [Testing](#testing)

---

## File Organization

### Directory Structure Rules
```
project_root/
├── core/              # Infrastructure (EventBus, AuditLog, ProjectState)
├── agents/            # Agent implementations (inherit from AgentBase)
├── models/            # LLM client wrappers
├── ui/                # Streamlit UI components
├── project_manager/   # Project state management
├── tests/             # All tests
│   ├── migrations/    # Migration verification tests
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
└── docs/              # Documentation
    ├── standards/     # Code standards (this file)
    ├── migrations/    # Migration guides
    └── architecture/  # Architecture snapshots
```

### File Naming
- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/methods**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore()`

### File Size Limits
- **Maximum 500 lines** per file (excluding tests)
- **Maximum 50 lines** per function
- If exceeding limits, refactor into multiple files/functions

---

## Naming Conventions

### Agents
```python
# Class names end with "Agent" (except ProducerAgent which is special)
class PlotArchitect(AgentBase):  # ✓ Good
class WorldbuilderAgent(AgentBase):  # ✓ Good
class Plotter(AgentBase):  # ✗ Bad - unclear

# Agent name attribute matches class
def __init__(self, ...):
    super().__init__("plot_architect", ...)  # ✓ Snake case of class name
```

### Methods
```python
# Public methods: Clear verb + noun
def generate_scene(self, ...):  # ✓ Good
def run(self, ...):  # ✓ Good for main entry point
def do_thing(self, ...):  # ✗ Bad - vague

# Private methods: Leading underscore
def _call_model(self, prompt: str) -> str:  # ✓ Good
def _execute_task(self, task: Task) -> None:  # ✓ Good
```

### Variables
```python
# Descriptive names
outline = agent.run(...)  # ✓ Good
result = agent.run(...)  # ✗ Bad - too generic
x = agent.run(...)  # ✗ Bad - meaningless

# Booleans: is/has/should prefix
is_valid = True  # ✓ Good
has_feedback = len(messages) > 0  # ✓ Good
should_retry = error_count < 3  # ✓ Good
valid = True  # ✗ Bad - unclear
```

---

## Import Organization

### Import Order (PEP 8)
```python
# 1. Standard library
import json
import os
from typing import Dict, Any, List
from pathlib import Path

# 2. Third-party packages
import streamlit as st
import requests
from dataclasses import dataclass

# 3. Local application imports
from core.event_bus import EventBus
from core.audit_log import AuditLog
from agents.base_agent import AgentBase
```

### Project-Specific Import Patterns

**For Agents:**
```python
# Required imports for all agents
from agents.base_agent import AgentBase
from core.event_bus import EventBus
from core.audit_log import AuditLog
from memory_store import MemoryStore

# Optional imports
from models.heavy_model import generate_with_heavy_model  # If using 7B model
import requests  # If using fast model
```

**For UI Components:**
```python
import streamlit as st
from agents.producer import ProducerAgent
from project_manager.loader import save_project_state
from project_manager.state import extract_state_from_session
from core.event_bus import EventBus
from core.audit_log import AuditLog
```

### Forbidden Imports
```python
# ✗ NEVER import these (deprecated)
from intelligence_bus import IntelligenceBus  # Removed in Phase 0
```

---

## Error Handling

See detailed guide: [ERROR_HANDLING.md](./ERROR_HANDLING.md)

### General Principles

**1. Always use specific exceptions**
```python
# ✓ Good
try:
    state = ProjectState.load(project_name)
except FileNotFoundError:
    state = ProjectState.create_default(project_name)
except json.JSONDecodeError as e:
    logger.error(f"Corrupt state file: {e}")
    raise

# ✗ Bad
try:
    state = ProjectState.load(project_name)
except:  # Too broad
    state = ProjectState.create_default(project_name)
```

**2. Never silently swallow exceptions**
```python
# ✓ Good
try:
    agent.run(...)
except ModelError as e:
    audit_log.append(
        event_type="agent_error",
        sender=self.name,
        recipient="system",
        payload={"error": str(e)}
    )
    raise  # Re-raise after logging

# ✗ Bad
try:
    agent.run(...)
except:
    pass  # Silent failure - debugging nightmare
```

**3. Provide context in exceptions**
```python
# ✓ Good
if not chapters:
    raise ValueError(
        f"Chapter plan has no chapters. "
        f"Outline length: {len(outline)} chars, "
        f"Max chapters requested: {max_chapters}"
    )

# ✗ Bad
if not chapters:
    raise ValueError("No chapters")  # Insufficient context
```

---

## Logging

See detailed guide: [LOGGING_GUIDE.md](./LOGGING_GUIDE.md)

### Logging Strategy

**For Agent Actions:**
```python
# Use AuditLog for all agent actions (persistent)
self.audit_log.append(
    event_type="agent_action",
    sender=self.name,
    recipient="system",
    payload={"action": "scene_generated", "length": len(scene_text)}
)
```

**For Real-Time Events:**
```python
# Use EventBus for coordination (ephemeral)
self.event_bus.publish(
    sender=self.name,
    recipient="producer",
    event_type="SCENE_READY",
    payload={"scene": scene_text}
)
```

**For Debug Output:**
```python
# Use print() only for orchestrator/development debugging
print(f"[ProducerAgent] Generating chapter {idx + 1}: {title}")
```

### Log Levels (AuditLog event_type Convention)
```python
# Structure: {component}_{severity}_{category}
"agent_info_action"      # Normal agent action
"agent_error_model"      # Model call failed
"user_info_feedback"     # User provided feedback
"task_info_completed"    # Task finished successfully
"task_error_failed"      # Task failed
```

---

## Type Hints

See detailed guide: [TYPE_HINTS_GUIDE.md](./TYPE_HINTS_GUIDE.md)

### Required Type Hints

**All function signatures must have type hints:**
```python
# ✓ Good
def run(self, idea: str, genre: str, auto_memory: bool = True) -> str:
    ...

# ✗ Bad
def run(self, idea, genre, auto_memory=True):  # No type hints
    ...
```

### Complex Types
```python
from typing import Dict, Any, List, Optional

# ✓ Good - specific types
def process_result(self, data: Dict[str, Any]) -> List[str]:
    ...

def find_agent(self, name: str) -> Optional[AgentBase]:
    ...

# ✗ Bad - using 'dict' and 'list' without specifics
def process_result(self, data: dict) -> list:
    ...
```

### Type Aliases for Readability
```python
# For frequently used complex types
from typing import Dict, Any

AgentPayload = Dict[str, Any]
ProjectConfig = Dict[str, str]

def send_message(self, payload: AgentPayload) -> None:
    ...
```

---

## Docstrings

### Style: Google Format

**Function docstrings:**
```python
def generate_scene(self, scene_prompt: str, outline_snippet: str,
                   world_notes: str, character_notes: str,
                   auto_memory: bool = True) -> str:
    """
    Generate a draft scene using outline, world, characters, and memory.
    
    Args:
        scene_prompt: Description of what should happen in the scene
        outline_snippet: Relevant portion of the plot outline
        world_notes: World-building context for the scene
        character_notes: Character details relevant to the scene
        auto_memory: Whether to extract and store facts in memory
        
    Returns:
        Generated scene text as prose
        
    Raises:
        ModelError: If LLM call fails
        MemoryError: If memory storage fails
    """
```

**Class docstrings:**
```python
class EventBus:
    """
    Ephemeral in-memory event bus for real-time agent coordination.
    
    Design:
        - Ring buffer (last 100 events only)
        - Subscriber pattern for real-time notifications
        - No persistence (use AuditLog for that)
        
    Example:
        >>> bus = EventBus("my_project")
        >>> bus.publish("agent_a", "agent_b", "MESSAGE", {"data": "hello"})
    """
```

**Module docstrings:**
```python
"""
Ephemeral message passing for real-time agent coordination.
Lives only during orchestrator runtime.
"""
```

### When Docstrings Are Required
- ✅ All public classes
- ✅ All public functions/methods
- ✅ All modules
- ✅ Complex private methods (use judgment)
- ❌ Simple getters/setters
- ❌ Obvious private helpers

---

## Configuration

### Configuration Sources (Priority Order)

1. **Environment variables** (highest priority)
2. **Config files** (`config/settings.json`)
3. **Code defaults** (lowest priority)

### Model Configuration
```python
# ✓ Good - centralized, injectable
class ModelConfig:
    FAST_MODEL_URL = os.getenv(
        "FAST_MODEL_URL",
        "http://localhost:8000/v1/chat/completions"
    )
    FAST_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
    HEAVY_MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

# ✗ Bad - hardcoded in agents
def __init__(self):
    self.model_url = "http://localhost:8000/v1/chat/completions"  # Hardcoded
```

### File Paths
```python
# ✓ Good - use Path, configurable base
from pathlib import Path

class Paths:
    BASE_DIR = Path(__file__).parent
    PROJECT_STATE_DIR = BASE_DIR / "project_state"
    AUDIT_LOG_DIR = BASE_DIR / "audit_logs"

# ✗ Bad - string paths, hardcoded
def save(self):
    with open("project_state/default/state.json", "w") as f:  # Hardcoded
        ...
```

---

## Testing

See detailed guide: [TESTING_REQUIREMENTS.md](./TESTING_REQUIREMENTS.md)

### Test Organization
```
tests/
├── migrations/          # Migration verification tests
├── unit/                # Unit tests for individual components
│   ├── test_event_bus.py
│   ├── test_audit_log.py
│   └── test_project_state.py
├── integration/         # Integration tests for pipelines
│   └── test_story_bible_pipeline.py
└── smoke_test.py        # End-to-end smoke test
```

### Testing Requirements

**New agents must have:**
```python
# tests/unit/test_new_agent.py
def test_agent_creation():
    """Verify agent can be created via factory"""
    factory = AgentFactory(...)
    agent = factory.create_new_agent()
    assert agent.name == "new_agent"

def test_agent_run():
    """Verify agent.run() produces output"""
    agent = factory.create_new_agent()
    result = agent.run(test_input)
    assert len(result) > 0
```

**New pipelines must have:**
```python
# tests/integration/test_new_pipeline.py
def test_pipeline_end_to_end():
    """Verify pipeline runs without errors"""
    producer = ProducerAgent(...)
    result = producer.run_new_pipeline(...)
    assert "expected_key" in result
```

### Test Naming Convention
```python
# Pattern: test_{what}_{condition}_{expected}
def test_event_bus_publish_creates_event():  # ✓ Good
def test_stuff():  # ✗ Bad - unclear
```

---

## Summary Checklist

Before submitting code, verify:

- [ ] File is under 500 lines
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Error handling uses specific exceptions
- [ ] Agent actions logged to AuditLog
- [ ] No hardcoded paths or URLs
- [ ] No deprecated imports (intelligence_bus)
- [ ] Follows existing patterns in similar files
- [ ] Tests added for new functionality
- [ ] No breaking changes without migration guide

---

## Questions?

For architectural decisions, see: `docs/architecture/phase_0_architecture.md`
For migration guides, see: `docs/migrations/`