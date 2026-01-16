# Type Hints Guide

## Philosophy

**Type hints improve:**
- Code readability
- IDE autocomplete
- Early error detection
- Self-documenting code

**Type hints are:**
- ✅ Required for all function signatures
- ✅ Required for complex variables
- ❌ Not enforced at runtime (Python is still dynamic)

---

## Basic Type Hints

### Primitives
```python
def process_text(
    text: str,
    count: int,
    ratio: float,
    enabled: bool
) -> str:
    """All primitive types must be annotated"""
    return text * count
```

### None and Optional
```python
from typing import Optional

# Function that might return None
def find_agent(name: str) -> Optional[AgentBase]:
    """Returns agent or None if not found"""
    if name in self.agents:
        return self.agents[name]
    return None

# Function with optional parameter
def run(self, idea: str, max_tokens: Optional[int] = None) -> str:
    tokens = max_tokens or 1000
    ...
```

### Collections
```python
from typing import List, Dict, Set, Tuple

def process_messages(
    messages: List[str],
    metadata: Dict[str, Any],
    tags: Set[str],
    coordinates: Tuple[int, int]
) -> List[Dict[str, str]]:
    """Type hint for collection contents"""
    return [{"msg": msg, "tag": tag} for msg in messages for tag in tags]
```

---

## Complex Type Hints

### Nested Collections
```python
from typing import Dict, List, Any

# Dictionary mapping strings to lists of dictionaries
AgentMessages = Dict[str, List[Dict[str, Any]]]

def get_agent_history(project_name: str) -> AgentMessages:
    """Type alias makes complex types readable"""
    return {
        "plot_architect": [
            {"type": "OUTLINE_READY", "payload": {...}},
            {"type": "FEEDBACK", "payload": {...}}
        ],
        "worldbuilder": [...]
    }
```

### Union Types
```python
from typing import Union

# Function that accepts multiple types
def format_output(data: Union[str, Dict[str, Any], List[str]]) -> str:
    """Accepts string, dict, or list"""
    if isinstance(data, str):
        return data
    elif isinstance(data, dict):
        return json.dumps(data)
    else:
        return "\n".join(data)
```

### Callable Types
```python
from typing import Callable

# Function that takes a callback
def subscribe(
    agent_name: str,
    callback: Callable[[Event], None]
) -> None:
    """Callback takes Event, returns None"""
    self.subscribers[agent_name].append(callback)

# Function that returns a function
def create_validator(min_length: int) -> Callable[[str], bool]:
    """Returns a validation function"""
    def validate(text: str) -> bool:
        return len(text) >= min_length
    return validate
```

---

## Type Hints for Classes

### Class Attributes
```python
from typing import Dict, List, Deque
from collections import deque

class EventBus:
    """Type hints for instance attributes"""
    
    project_name: str
    buffer: Deque[Event]
    subscribers: Dict[str, List[Callable]]
    
    def __init__(self, project_name: str, buffer_size: int = 100):
        self.project_name = project_name
        self.buffer = deque(maxlen=buffer_size)
        self.subscribers = {}
```

### Methods
```python
class AgentFactory:
    """All methods need type hints"""
    
    def __init__(self, project_name: str, event_bus: EventBus) -> None:
        self.project_name = project_name
        self.event_bus = event_bus
    
    def create_plot_architect(self) -> PlotArchitect:
        """Return type must be specific"""
        return PlotArchitect(...)
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Private methods need type hints too"""
        return "required_field" in config
```

### Class Methods and Static Methods
```python
from typing import ClassVar

class ProjectState:
    """Type hints for class and static methods"""
    
    version: ClassVar[str] = "1.0.0"  # Class variable
    
    @classmethod
    def load(cls, project_name: str) -> "ProjectState":
        """Returns instance of same class"""
        ...
    
    @classmethod
    def create_default(cls, project_name: str) -> "ProjectState":
        """Use string for forward reference"""
        return cls(project_name=project_name)
    
    @staticmethod
    def _state_path_static(project_name: str, base_dir: str) -> Path:
        """Static method type hints"""
        return Path(base_dir) / project_name / "state.json"
```

---

## Type Hints for Agent Code

### Agent Base Pattern
```python
from typing import Dict, Any, List

class AgentBase:
    """Standard agent type hints"""
    
    def __init__(
        self,
        name: str,
        project_name: str,
        event_bus: EventBus,
        audit_log: AuditLog,
        fast_model_url: str,
        model_mode: str
    ) -> None:
        self.name = name
        self.project_name = project_name
        self.event_bus = event_bus
        self.audit_log = audit_log
        self.fast_model_url = fast_model_url
        self.model_mode = model_mode
    
    def send_message(
        self,
        recipient: str,
        msg_type: str,
        payload: Dict[str, Any]
    ) -> None:
        """Type hints for all parameters"""
        ...
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return type must be specific"""
        events = self.event_bus.get_recent(self.name, limit=limit)
        return [e.payload for e in events]
```

### Specific Agent Pattern
```python
class PlotArchitect(AgentBase):
    """Type hints for agent-specific methods"""
    
    def run(
        self,
        idea: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = False
    ) -> str:
        """All parameters and return type annotated"""
        ...
```

---

## Type Hints for UI Code

### Streamlit Function Pattern
```python
import streamlit as st
from agents.producer import ProducerAgent

def render_plot_architect(project_name: str) -> None:
    """UI functions typically return None"""
    
    if "producer" not in st.session_state:
        st.session_state["producer"] = ProducerAgent(...)
    
    producer: ProducerAgent = st.session_state["producer"]
    
    # Type hint for local variables
    seed: str = st.session_state["seed_idea_plot"].strip()
    auto_memory: bool = st.checkbox("Auto-store facts")
```

---

## Advanced Type Hints

### Generic Types
```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Queue(Generic[T]):
    """Generic queue for any type"""
    
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def enqueue(self, item: T) -> None:
        self._items.append(item)
    
    def dequeue(self) -> T:
        return self._items.pop(0)

# Usage
event_queue: Queue[Event] = Queue()
event_queue.enqueue(Event(...))
```

### Literal Types
```python
from typing import Literal

ModelMode = Literal["fast", "high_quality"]

def create_agent(mode: ModelMode) -> AgentBase:
    """Only accepts 'fast' or 'high_quality'"""
    if mode == "fast":
        return FastAgent()
    else:
        return HighQualityAgent()
```

### Type Aliases
```python
from typing import Dict, Any, List

# Create readable aliases for complex types
AgentPayload = Dict[str, Any]
MessageList = List[Dict[str, Any]]
AgentConfig = Dict[str, str]

def send_payload(payload: AgentPayload) -> None:
    """Much more readable than Dict[str, Any]"""
    ...

def get_messages() -> MessageList:
    """Clear intent from type alias"""
    ...
```

### Protocol (Structural Subtyping)
```python
from typing import Protocol

class Runnable(Protocol):
    """Any class with a run() method"""
    
    def run(self, input: str) -> str:
        ...

def execute_agent(agent: Runnable, input: str) -> str:
    """Accepts any object with run() method"""
    return agent.run(input)

# Both of these work
plot_agent = PlotArchitect(...)
world_agent = WorldbuilderAgent(...)

result1 = execute_agent(plot_agent, "idea")
result2 = execute_agent(world_agent, "outline")
```

---

## Type Checking Tools

### MyPy Configuration

Create `mypy.ini` in project root:
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

# Per-module options
[mypy-tests.*]
disallow_untyped_defs = False

[mypy-streamlit.*]
ignore_missing_imports = True

[mypy-faiss.*]
ignore_missing_imports = True
```

### Run Type Checking
```bash
# Install mypy
conda activate multimodal-assistant
pip install mypy

# Check all files
mypy .

# Check specific file
mypy agents/plot_architect.py

# Check with strict mode
mypy --strict agents/
```

---

## Common Patterns

### Pattern 1: Function with All Features
```python
from typing import Optional, Dict, Any, List

def generate_with_options(
    prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.8,
    stop_sequences: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Complete function signature with all type hint features.
    
    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        stop_sequences: Optional stop sequences
        metadata: Optional metadata dictionary
        
    Returns:
        Generated text
    """
    if stop_sequences is None:
        stop_sequences = []
    
    if metadata is None:
        metadata = {}
    
    # Implementation...
    return result
```

### Pattern 2: Dataclass with Type Hints
```python
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Event:
    """Type hints are required in dataclasses"""
    id: str
    project_name: str
    sender: str
    recipient: str
    type: str
    payload: Dict[str, Any]
    timestamp: float
```

### Pattern 3: Context Manager
```python
from typing import Iterator, Any
from contextlib import contextmanager

@contextmanager
def agent_context(agent_name: str) -> Iterator[AgentBase]:
    """Context manager with type hints"""
    agent = create_agent(agent_name)
    try:
        yield agent
    finally:
        cleanup(agent)

# Usage
with agent_context("plot_architect") as agent:
    result = agent.run("idea")
```

---

## When to Skip Type Hints

### Acceptable Omissions
```python
# ✓ Simple comprehensions
items = [x.strip() for x in lines]

# ✓ Obvious local variables
count = 0
for item in items:
    count += 1

# ✓ Lambda functions (often too complex to annotate)
sorted_items = sorted(items, key=lambda x: x.priority)
```

### Must Still Annotate
```python
# ✓ Function signatures - ALWAYS
def process(items):  # ✗ Bad
def process(items: List[str]) -> List[str]:  # ✓ Good

# ✓ Class attributes - ALWAYS
class MyClass:
    count = 0  # ✗ Bad
    count: int = 0  # ✓ Good

# ✓ Complex variables - ALWAYS
data = json.load(f)  # ✗ Bad
data: Dict[str, Any] = json.load(f)  # ✓ Good
```

---

## Common Type Hint Mistakes

### Mistake 1: Using 'list' instead of 'List'
```python
# ✗ Bad - lowercase types don't support generics in Python <3.9
def process(items: list) -> list:
    ...

# ✓ Good - import from typing
from typing import List
def process(items: List[str]) -> List[str]:
    ...

# ✓ Also Good - Python 3.9+ supports lowercase
def process(items: list[str]) -> list[str]:  # Requires Python 3.9+
    ...
```

### Mistake 2: Forgetting Optional
```python
# ✗ Bad - suggests value is always present
def find(name: str) -> AgentBase:
    return self.agents.get(name)  # Returns None if not found!

# ✓ Good - indicates None is possible
def find(name: str) -> Optional[AgentBase]:
    return self.agents.get(name)
```

### Mistake 3: Too Broad Type Hints
```python
# ✗ Bad - not helpful
def process(data: Any) -> Any:
    ...

# ✓ Good - specific
def process(data: Dict[str, List[str]]) -> List[str]:
    ...
```

---

## Summary

**Type Hint Checklist:**
- [ ] All function signatures have parameter types
- [ ] All function signatures have return types
- [ ] Optional parameters use `Optional[T]`
- [ ] Collections specify element types `List[str]`, `Dict[str, Any]`
- [ ] Complex types use aliases for readability
- [ ] Class attributes have type hints
- [ ] No use of bare `Any` without good reason

**Golden Rules:**
1. Type hint ALL function signatures
2. Use specific types, not `Any`
3. Use `Optional[T]` for values that can be `None`
4. Create type aliases for complex nested types
5. Import from `typing` module
6. Run `mypy` to catch errors early

**When in doubt:** Look at existing type hints in similar code!