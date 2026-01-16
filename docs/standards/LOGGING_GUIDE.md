# Logging Guide

## Logging Strategy Overview

We use a **dual-logging system**:

1. **AuditLog** - Persistent, structured, queryable history
2. **EventBus** - Ephemeral, real-time coordination
3. **Print statements** - Development debugging only

---

## When to Use Each

| Scenario | Use | Reason |
|----------|-----|--------|
| Agent completed action | AuditLog | Need historical record |
| Agent sends message to another agent | EventBus + AuditLog | Real-time + history |
| User provides feedback | EventBus + AuditLog | Route to agent + record |
| Task completed | AuditLog | Permanent record |
| Debug orchestrator flow | print() | Development only |
| Real-time UI updates | EventBus | Ephemeral coordination |

---

## AuditLog Patterns

### Basic Agent Action Logging
```python
class PlotArchitect(AgentBase):
    def run(self, idea: str, ...) -> str:
        # Log start of action
        self.log("Starting outline generation", event_type="info")
        
        # Do work
        outline = self._generate_outline(idea)
        
        # Log completion with metrics
        self.audit_log.append(
            event_type="agent_action_completed",
            sender=self.name,
            recipient="system",
            payload={
                "action": "generate_outline",
                "input_length": len(idea),
                "output_length": len(outline),
                "model_mode": self.model_mode
            }
        )
        
        return outline
```

### Logging with Context
```python
def _execute_task(self, task: Task) -> None:
    """Execute task with full audit trail"""
    
    # Log task start
    self.audit_log.append(
        event_type="task_started",
        sender="orchestrator",
        recipient="system",
        payload={
            "task_id": task.id,
            "task_type": task.type,
            "project_name": self.project_name,
            "timestamp": time.time()
        }
    )
    
    try:
        result = self._run_task_logic(task)
        
        # Log success
        self.audit_log.append(
            event_type="task_completed",
            sender="orchestrator",
            recipient="system",
            payload={
                "task_id": task.id,
                "task_type": task.type,
                "duration": time.time() - task.created_at,
                "result_summary": str(result)[:200]
            }
        )
        
    except Exception as e:
        # Log failure
        self.audit_log.append(
            event_type="task_failed",
            sender="orchestrator",
            recipient="system",
            payload={
                "task_id": task.id,
                "task_type": task.type,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "stack_trace": traceback.format_exc()
            }
        )
        raise
```

### Logging User Interactions
```python
def handle_feedback(self, agent_name: str, feedback_text: str) -> None:
    """Route feedback to agent via EventBus"""
    
    # Publish to EventBus (ephemeral, real-time)
    self.event_bus.publish(
        sender="user",
        recipient=agent_name,
        event_type="feedback",
        payload={"content": feedback_text, "type": "feedback"}
    )
    
    # Log to AuditLog (persistent, historical)
    self.audit_log.append(
        event_type="user_feedback",
        sender="user",
        recipient=agent_name,
        payload={
            "content": feedback_text,
            "feedback_length": len(feedback_text),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

---

## EventBus Patterns

### Agent-to-Agent Communication
```python
class PlotArchitect(AgentBase):
    def run(self, idea: str, ...) -> str:
        outline = self._generate_outline(idea)
        
        # Send message to next agent in pipeline
        self.send_message(
            recipient="worldbuilder",
            msg_type="OUTLINE_READY",
            payload={"outline": outline}
        )
        
        return outline
```

**Note:** `send_message()` in `AgentBase` automatically logs to both EventBus and AuditLog:
```python
def send_message(self, recipient: str, msg_type: str, payload: Dict[str, Any]) -> None:
    """Send message to another agent"""
    # Publish to EventBus (real-time)
    self.event_bus.publish(
        sender=self.name,
        recipient=recipient,
        event_type=msg_type,
        payload=payload
    )
    
    # Log to AuditLog (persistent)
    self.audit_log.append(
        event_type=f"agent_message_{msg_type}",
        sender=self.name,
        recipient=recipient,
        payload=payload
    )
```

### Broadcasting to All Agents
```python
def send_guidance_message(self, guidance: str) -> None:
    """Send guidance to ALL agents"""
    if not guidance:
        return
    
    self.event_bus.publish(
        sender=self.name,
        recipient="ALL",  # Broadcast
        event_type="GUIDANCE",
        payload={"guidance": guidance}
    )
```

---

## Event Type Naming Convention

### Structure: `{component}_{severity}_{category}`

**Examples:**
```python
# Agent actions
"agent_info_action"           # Normal agent action
"agent_info_message"          # Agent sent message
"agent_error_model"           # Model call failed
"agent_error_memory"          # Memory operation failed

# User interactions
"user_info_feedback"          # User provided feedback
"user_info_command"           # User triggered action

# Tasks
"task_info_created"           # Task created
"task_info_started"           # Task execution started
"task_info_completed"         # Task completed successfully
"task_error_failed"           # Task failed

# System events
"system_info_startup"         # Orchestrator started
"system_info_shutdown"        # Orchestrator stopped
"system_error_crash"          # Unexpected crash
```

### Severity Levels
```python
"info"     # Normal operations
"warning"  # Potential issues (degraded performance, retries)
"error"    # Failures (task failed, model error)
"critical" # System-level failures (orchestrator crash)
```

---

## Print Statement Guidelines

### When to Use Print

**✅ Acceptable uses:**
- Orchestrator debug output
- Pipeline progress indicators
- Development/testing feedback

**❌ Don't use for:**
- Agent actions (use AuditLog)
- User-facing messages (use Streamlit)
- Production logging (use AuditLog)

### Print Format
```python
# ✓ Good - clear prefix and context
print(f"[Orchestrator] Starting loop for project '{self.project_name}'")
print(f"[ProducerAgent] Generating chapter {idx + 1}: {title}")
print(f"[CreativeDirector] Analyzing {len(critiques)} critiques")

# ✗ Bad - unclear source
print("Starting...")
print(f"Chapter {idx}")
```

### Print in Pipelines (Progress Indicators)
```python
def run_full_story_pipeline(self, ...) -> dict:
    """Generate complete story with progress indicators"""
    
    print(f"\n[ProducerAgent] Starting full story pipeline")
    print(f"[ProducerAgent] Max chapters: {max_chapters}")
    
    # Generate story bible
    print(f"[ProducerAgent] Step 1/3: Generating story bible...")
    bible = self.run_story_bible_pipeline(...)
    
    # Plan chapters
    print(f"[ProducerAgent] Step 2/3: Planning chapters...")
    plan = self.plan_chapters_from_outline(...)
    
    # Generate chapters
    print(f"[ProducerAgent] Step 3/3: Generating {len(chapters_plan)} chapters...")
    for idx, chapter_plan in enumerate(chapters_plan):
        print(f"  → Chapter {idx + 1}/{len(chapters_plan)}: {chapter_plan.get('title')}")
        chapter = self._generate_chapter_from_plan(...)
        chapters.append(chapter)
    
    print(f"[ProducerAgent] ✓ Pipeline complete: {len(chapters)} chapters generated")
    
    return result
```

---

## Log Querying

### Search AuditLog from UI
```python
def render_intelligence_panel(producer):
    """Display audit log search interface"""
    
    st.subheader("🔍 Audit Log Search")
    
    search_type = st.selectbox(
        "Filter by event type",
        ["all", "agent_message", "user_feedback", "task_completed"],
        key="audit_search_type"
    )
    
    search_limit = st.number_input("Max results", value=50)
    
    if st.button("Search Audit Log"):
        event_type = None if search_type == "all" else search_type
        
        results = producer.audit_log.search(
            event_type=event_type,
            limit=search_limit
        )
        
        for entry in results:
            st.markdown(f"**{entry.sender} → {entry.recipient}** — {entry.event_type}")
            st.json(entry.payload)
```

### Search AuditLog Programmatically
```python
# Find all user feedback for a specific agent
feedback_entries = audit_log.search(
    event_type="user_feedback",
    sender="user",
    limit=100
)

for entry in feedback_entries:
    if entry.recipient == "plot_architect":
        print(f"Feedback: {entry.payload['content']}")
```

### Stream Large Logs
```python
# Memory-efficient streaming for large logs
for entry in audit_log.stream(since="2026-01-16T00:00:00"):
    if entry.event_type == "task_failed":
        print(f"Failed task: {entry.payload['task_id']}")
```

---

## Performance Considerations

### AuditLog Performance

**Fast operations:**
- ✅ `append()` - O(1), just writes one line to file
- ✅ `stream()` - Memory-efficient iterator
- ✅ `search()` with limit - Stops after N results

**Slow operations:**
- ⚠️ `read_all()` - Loads entire log into memory
- ⚠️ `search()` without limit - May scan thousands of entries

### EventBus Performance

**Fast operations:**
- ✅ `publish()` - O(1), just appends to ring buffer
- ✅ `get_recent()` - O(N) where N = buffer size (max 100)

**No slow operations** - EventBus is always fast (in-memory, bounded size)

---

## Monitoring & Debugging

### Check AuditLog Size
```python
import os
from pathlib import Path

log_path = Path("audit_logs/default_project_audit.jsonl")
size_mb = log_path.stat().st_size / (1024 * 1024)
print(f"Audit log size: {size_mb:.2f} MB")

# Count entries
with open(log_path) as f:
    line_count = sum(1 for _ in f)
print(f"Total entries: {line_count}")
```

### Rotate Large Logs
```python
def rotate_audit_log(project_name: str, max_size_mb: int = 100):
    """Rotate audit log if it exceeds size limit"""
    from datetime import datetime
    
    log_path = Path(f"audit_logs/{project_name}_audit.jsonl")
    
    if not log_path.exists():
        return
    
    size_mb = log_path.stat().st_size / (1024 * 1024)
    
    if size_mb > max_size_mb:
        # Rename old log with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = Path(f"audit_logs/{project_name}_audit_{timestamp}.jsonl")
        log_path.rename(archive_path)
        
        # Create new empty log
        log_path.touch()
        
        print(f"Rotated audit log: {log_path} → {archive_path}")
```

---

## Common Patterns Reference

### Pattern 1: Agent Action Logging
```python
def run(self, ...):
    self.log(f"Starting {action_name}", event_type="info")
    result = self._do_work(...)
    self.audit_log.append(
        event_type="agent_action_completed",
        sender=self.name,
        recipient="system",
        payload={"action": action_name, "result_size": len(result)}
    )
    return result
```

### Pattern 2: Error Logging
```python
try:
    result = risky_operation()
except Exception as e:
    self.audit_log.append(
        event_type="agent_error",
        sender=self.name,
        recipient="system",
        payload={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "operation": "risky_operation"
        }
    )
    raise
```

### Pattern 3: Pipeline Progress
```python
print(f"[{self.name}] Starting pipeline: {pipeline_name}")
for idx, step in enumerate(steps):
    print(f"  → Step {idx+1}/{len(steps)}: {step.name}")
    result = step.execute()
print(f"[{self.name}] ✓ Pipeline complete")
```

---

## Summary

**Logging Hierarchy:**
1. **AuditLog** - Persistent record (agent actions, tasks, errors)
2. **EventBus** - Real-time coordination (agent messages, feedback)
3. **Print** - Development debug (orchestrator, progress)

**Golden Rules:**
- Use AuditLog for anything you might need to debug later
- Use EventBus for real-time agent coordination
- Use print() sparingly, only for development
- Always log errors with full context
- Use consistent event_type naming
- Include metrics in logs (length, duration, etc.)

**When in doubt:** Look at existing logging in similar code!