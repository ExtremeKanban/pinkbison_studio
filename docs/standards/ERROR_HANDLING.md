# Error Handling Guide

## Philosophy

**Errors should be:**
1. **Specific** - Use precise exception types
2. **Logged** - Record to AuditLog for debugging
3. **Actionable** - Provide clear context for fixing
4. **User-friendly** - Show helpful messages in UI

---

## Exception Hierarchy

### Standard Python Exceptions We Use
```python
# File operations
FileNotFoundError       # File doesn't exist
PermissionError         # Can't access file
json.JSONDecodeError    # Invalid JSON

# Value errors
ValueError              # Invalid argument value
KeyError                # Missing dictionary key
IndexError              # List index out of range

# Type errors
TypeError               # Wrong type passed
AttributeError          # Missing attribute

# Network errors
requests.ConnectionError    # Can't reach server
requests.Timeout           # Request timed out
requests.HTTPError         # HTTP error response
```

### Custom Exceptions
```python
# models/exceptions.py
class ModelError(Exception):
    """Base exception for model-related errors"""
    pass

class ModelTimeoutError(ModelError):
    """Model inference timed out"""
    pass

class ModelResponseError(ModelError):
    """Model returned invalid response"""
    pass

class PipelineError(Exception):
    """Base exception for pipeline errors"""
    pass
```

---

## Error Handling Patterns

### Pattern 1: Try-Except-Log-Raise

**Use when:** Error should stop execution but needs logging
```python
def load_project_state(project_name: str) -> ProjectState:
    """Load project state with proper error handling"""
    try:
        state = ProjectState.load(project_name)
    except FileNotFoundError:
        # Expected case - create default
        return ProjectState.create_default(project_name)
    except json.JSONDecodeError as e:
        # Unexpected - log and raise
        logger.error(f"Corrupt state file for {project_name}: {e}")
        raise ValueError(
            f"Project '{project_name}' has corrupt state file. "
            f"Please delete project_state/{project_name}/ and restart."
        ) from e
    
    return state
```

### Pattern 2: Try-Except-Return-Default

**Use when:** Error is recoverable with sensible default
```python
def get_recent_messages(self, limit: int = 10) -> List[Event]:
    """Get recent events, returning empty list if unavailable"""
    try:
        events = self.event_bus.get_recent(self.name, limit=limit)
        return [e.payload for e in events]
    except AttributeError:
        # EventBus not initialized - return empty
        return []
```

### Pattern 3: Try-Except-Retry

**Use when:** Transient errors (network, model timeouts)
```python
def call_model_with_retry(self, prompt: str, max_retries: int = 3) -> str:
    """Call model with exponential backoff retry"""
    import time
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                self.fast_model_url,
                json={"model": "...", "messages": [...]},
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except requests.Timeout:
            if attempt == max_retries - 1:
                raise ModelTimeoutError(
                    f"Model timed out after {max_retries} attempts"
                )
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Timeout, retrying in {wait_time}s...")
            time.sleep(wait_time)
            
        except requests.RequestException as e:
            raise ModelError(f"Model request failed: {e}") from e
```

### Pattern 4: Context Manager for Cleanup

**Use when:** Resources need guaranteed cleanup
```python
from contextlib import contextmanager

@contextmanager
def agent_task_context(task_id: str, task_manager: TaskManager):
    """Ensure task status updated even if error occurs"""
    try:
        task_manager.update_status(task_id, TaskStatus.RUNNING)
        yield
        task_manager.update_status(task_id, TaskStatus.DONE)
    except Exception as e:
        task_manager.update_status(
            task_id,
            TaskStatus.FAILED,
            error=str(e)
        )
        raise

# Usage
with agent_task_context(task.id, self.tasks):
    result = self._execute_task(task)
```

---

## Streamlit UI Error Handling

### Pattern: User-Friendly Error Display
```python
def render_plot_architect(project_name):
    st.header("Plot Architect Agent")
    
    if st.button("Generate Outline"):
        try:
            agent = factory.create_plot_architect()
            outline = agent.run(...)
            st.success("Outline generated!")
            st.write(outline)
            
        except ModelError as e:
            st.error(
                f"⚠️ Model Error: {str(e)}\n\n"
                f"Please check that:\n"
                f"- vLLM server is running at localhost:8000\n"
                f"- Model is loaded correctly"
            )
            
        except ValueError as e:
            st.error(f"❌ Invalid Input: {str(e)}")
            
        except Exception as e:
            st.error(
                f"❌ Unexpected Error: {str(e)}\n\n"
                f"Please report this issue with the error above."
            )
            # Log full traceback for debugging
            import traceback
            print(traceback.format_exc())
```

---

## Logging Errors to AuditLog
```python
def _execute_task(self, task: Task) -> None:
    """Execute task with full audit trail"""
    try:
        # Attempt execution
        result = self._run_task_logic(task)
        
        # Log success
        self.audit_log.append(
            event_type="task_completed",
            sender="orchestrator",
            recipient="system",
            payload={
                "task_id": task.id,
                "task_type": task.type,
                "result_size": len(str(result))
            }
        )
        
    except Exception as e:
        # Log failure with full context
        self.audit_log.append(
            event_type="task_failed",
            sender="orchestrator",
            recipient="system",
            payload={
                "task_id": task.id,
                "task_type": task.type,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "task_payload": task.payload
            }
        )
        raise
```

---

## Validation Patterns

### Input Validation
```python
def run_story_bible_pipeline(
    self,
    idea: str,
    genre: str,
    tone: str,
    themes: str,
    setting: str,
    auto_memory: bool = True
) -> dict:
    """Generate story bible with input validation"""
    
    # Validate required inputs
    if not idea or not idea.strip():
        raise ValueError("Idea cannot be empty")
    
    if len(idea) < 10:
        raise ValueError(
            f"Idea too short ({len(idea)} chars). "
            f"Please provide at least 10 characters."
        )
    
    if len(idea) > 5000:
        raise ValueError(
            f"Idea too long ({len(idea)} chars). "
            f"Please keep under 5000 characters."
        )
    
    # Continue with validated inputs
    ...
```

### Output Validation
```python
def _call_model(self, prompt: str) -> str:
    """Call model and validate response"""
    response = requests.post(self.fast_model_url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    
    # Validate response structure
    if "choices" not in data:
        raise ModelResponseError(
            f"Invalid model response: missing 'choices' field. "
            f"Got: {list(data.keys())}"
        )
    
    if not data["choices"]:
        raise ModelResponseError("Model returned empty choices array")
    
    content = data["choices"][0]["message"]["content"]
    
    # Validate content
    if not content or not content.strip():
        raise ModelResponseError("Model returned empty content")
    
    return content
```

---

## Anti-Patterns (Don't Do This)

### ❌ Bare except
```python
# ✗ Bad - catches everything, including KeyboardInterrupt
try:
    result = agent.run(...)
except:
    return None
```

### ❌ Silent failures
```python
# ✗ Bad - error disappears without trace
try:
    save_state(state)
except Exception:
    pass  # Oops, state wasn't saved but no one knows
```

### ❌ Generic error messages
```python
# ✗ Bad - unhelpful
raise Exception("Something went wrong")

# ✓ Good - specific and actionable
raise FileNotFoundError(
    f"Project state file not found: {expected_path}. "
    f"Use ProjectState.create_default('{project_name}') to create."
)
```

### ❌ Catching too broad
```python
# ✗ Bad - catches unrelated errors
try:
    state = load_state()
    result = process(state)
    save_result(result)
except Exception:  # Too broad - which operation failed?
    return None
    
# ✓ Good - specific exception handling
try:
    state = load_state()
except FileNotFoundError:
    state = create_default()

try:
    result = process(state)
except ValueError as e:
    raise ProcessingError(f"Invalid state: {e}") from e

try:
    save_result(result)
except PermissionError as e:
    raise SaveError(f"Cannot write result: {e}") from e
```

---

## Summary

**Golden Rules:**
1. Use specific exception types
2. Always provide context in error messages
3. Log errors to AuditLog for agent actions
4. Show user-friendly messages in UI
5. Never silently swallow exceptions
6. Validate inputs and outputs
7. Use retry logic for transient failures

**When in doubt:** Look at existing error handling in similar code!