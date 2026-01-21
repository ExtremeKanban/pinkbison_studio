# Testing Guide: REAL-TIME WORKFLOW & FEEDBACK Verification

## Overview

This guide provides complete instructions for verifying the REAL-TIME WORKFLOW & FEEDBACK implementation in PinkBison Creative Studio.

## Testing Philosophy

We use a **4-layer testing approach**:

1. **Layer 1: Unit Tests** - Test individual components in isolation
2. **Layer 2: Integration Tests** - Test how components work together
3. **Layer 3: Manual UI Tests** - Interactive verification in actual Streamlit UI
4. **Layer 4: End-to-End Tests** - Full workflow verification

---

## Quick Start

### Prerequisites

Ensure you have:
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Python environment activated (multimodal-assistant)
- [ ] Test project created (or using default project)

### Run All Automated Tests

```bash
# From project root
python tests/realtime_features/run_tests.py
```

This runs:
- WebSocketManager unit tests
- EventBus WebSocket integration tests
- WebSocket + EventBus integration tests

### Run Manual UI Tests

1. Start all servers:
   ```bash
   # Terminal 1 (WSL): vLLM server
   # Terminal 2 (WSL): Embeddings server
   # Terminal 3 (Windows): Streamlit
   streamlit run studio_ui.py
   ```

2. Open browser to `localhost:8501`

3. Follow checklist: `tests/manual_testing/manual_test_checklist.md`

---

## Layer 1: Unit Tests

### WebSocketManager Tests

**File:** `tests/realtime_features/test_websocket_manager.py`

**What it tests:**
- WebSocketManager singleton pattern
- Subscriber add/remove operations
- Project-specific broadcasting
- Thread-safety of operations
- Message formatting

**Run individually:**
```bash
pytest tests/realtime_features/test_websocket_manager.py -v
```

**Expected results:**
- All tests pass (some may be skipped for server lifecycle tests)
- No import errors
- Subscriber operations work correctly

### EventBus WebSocket Tests

**File:** `tests/realtime_features/test_eventbus_websocket.py`

**What it tests:**
- EventBus initialization and publish
- WebSocket integration in publish method
- Event buffer management
- Subscribe/get_recent functionality
- Project isolation
- Error handling

**Run individually:**
```bash
pytest tests/realtime_features/test_eventbus_websocket.py -v
```

**Expected results:**
- All tests pass
- Events are properly structured
- WebSocket integration exists
- Error handling works

---

## Layer 2: Integration Tests

### WebSocket + EventBus Integration

**File:** `tests/realtime_features/test_websocket_integration.py`

**What it tests:**
- EventBus triggers WebSocket broadcasts
- Multiple projects are isolated
- AgentBase logs to both EventBus and AuditLog
- Registry provides properly integrated resources
- Error handling across integration
- Complete message flow: Agent → EventBus → WebSocket

**Run individually:**
```bash
pytest tests/realtime_features/test_websocket_integration.py -v
```

**Expected results:**
- Integration points work correctly
- Project isolation is maintained
- Errors don't break integration
- Message flow is complete

---

## Layer 3: Manual UI Tests

### Purpose

Verify that real-time features work correctly in the actual Streamlit UI, since automated UI testing is challenging with Streamlit.

### Test Checklist

**File:** `tests/manual_testing/manual_test_checklist.md`

This comprehensive checklist includes:

1. **WebSocket Connection** (3 tests)
   - Server startup
   - Connection status display
   - Reconnection handling

2. **Live Event Stream** (4 tests)
   - Panel display
   - Real-time updates
   - Multiple event types
   - Scrolling with many events

3. **Pipeline Controls** (6 tests)
   - Control panel display
   - Start pipeline
   - Pause pipeline
   - Resume pipeline
   - Stop pipeline
   - Real-time progress updates

4. **Feedback Injection** (4 tests)
   - Injector display
   - Inject during pipeline
   - Feedback reaches target
   - Multiple injections

5. **UI Responsiveness** (3 tests)
   - UI doesn't freeze
   - Multiple components update
   - Error handling

6. **Integration Scenarios** (3 tests)
   - Complete story bible workflow
   - Chapter generation with feedback
   - Pause/resume workflow

7. **Edge Cases** (3 tests)
   - Rapid event generation
   - WebSocket disconnection
   - Long-running pipelines

### How to Use the Checklist

1. Print or open `manual_test_checklist.md` in another window
2. Start Streamlit: `streamlit run studio_ui.py`
3. Work through each test sequentially
4. Mark PASS/FAIL/SKIP for each test
5. Document any issues in the notes section
6. Complete the summary at the end

### Recording Results

Create a copy of the checklist for each test session:
```bash
cp tests/manual_testing/manual_test_checklist.md tests/manual_testing/manual_test_results_YYYYMMDD.md
```

---

## Layer 4: End-to-End Tests

### Purpose

Verify complete workflows with all real-time features working together.

### Test Scenarios

Currently, E2E tests are covered by:
- Manual integration scenarios (Test Suite 6 in checklist)
- Real-world usage during manual testing

### Future E2E Tests

Once manual testing is complete and any issues fixed, we can create:
- Automated E2E tests using pytest
- Recorded test scenarios
- Performance benchmarks

---

## Test Results Documentation

### After Running Automated Tests

Document results in `tests/realtime_features/test_results.md`:

```markdown
# Test Results: REAL-TIME WORKFLOW & FEEDBACK

**Date:** YYYY-MM-DD
**Environment:** Windows 11, RTX 5080, Python 3.10
**Tested By:** [Your name]

## Automated Tests

### Layer 1: Unit Tests
- WebSocketManager: PASS/FAIL
- EventBus WebSocket: PASS/FAIL

### Layer 2: Integration Tests
- WebSocket Integration: PASS/FAIL

### Issues Found
1. [Issue description]
2. [Issue description]

### Notes
[Any observations]
```

### After Manual UI Testing

Document results in `tests/manual_testing/manual_test_results.md` (use the checklist as a template).

---

## Common Issues and Troubleshooting

### Issue: WebSocket server "failed to start" in tests

**Cause:** Server already running (expected behavior)

**Solution:** This is normal - the server starts automatically with Streamlit

**Action:** No action needed

### Issue: Browser automation tests fail

**Cause:** Playwright/Streamlit compatibility issues

**Solution:** Use manual testing instead

**Action:** Follow manual testing checklist

### Issue: Events don't appear in UI

**Possible causes:**
1. WebSocket not connected
2. EventBus not publishing
3. UI component not rendering

**Debugging steps:**
1. Check browser console (F12) for WebSocket errors
2. Check Streamlit terminal for WebSocket server logs
3. Verify EventBus.publish is being called
4. Check if Live Event Stream component is rendered

### Issue: UI freezes during pipeline

**Possible causes:**
1. Pipeline using blocking code
2. Streamlit auto-rerun triggered
3. Heavy computation in UI thread

**Debugging steps:**
1. Check if Producer uses async/await
2. Look for `time.sleep()` + `st.rerun()` patterns
3. Verify background threading is working

---

## Test Coverage

### What We Test

✅ **Core Components:**
- WebSocketManager initialization and operations
- EventBus WebSocket integration
- Message formatting and serialization
- Project isolation

✅ **Integration Points:**
- EventBus → WebSocket broadcasting
- AgentBase → EventBus → AuditLog
- Registry resource management
- Error handling across components

✅ **Real-World Usage:**
- WebSocket connection/reconnection
- Live event streaming
- Pipeline controls (start/pause/resume/stop)
- Feedback injection
- UI responsiveness

### What We Don't Test (Yet)

❌ **Advanced Scenarios:**
- Multi-user concurrent access
- Very long-running pipelines (hours)
- High-frequency event generation (100+ events/sec)
- Network failure recovery
- Browser compatibility (only Chrome tested)

### Future Testing Needs

📋 **Planned Additions:**
1. Performance benchmarks
2. Load testing (multiple projects)
3. Browser compatibility suite
4. Automated E2E tests
5. Regression test suite

---

## Success Criteria

### Automated Tests

**Must Pass:**
- All WebSocketManager unit tests
- All EventBus WebSocket tests
- All integration tests (except explicitly skipped)

### Manual Tests

**Must Pass:**
- WebSocket connection establishes
- Events appear in real-time
- Pipeline controls work (start/pause/resume/stop)
- Feedback injection works
- UI remains responsive

**Nice to Have:**
- All edge case tests pass
- No performance degradation
- Graceful error handling

---

## Next Steps After Testing

### If All Tests Pass

1. ✅ Mark REAL-TIME WORKFLOW & FEEDBACK as VERIFIED in `prompt.md`
2. 📝 Document verified features
3. 🧹 Plan legacy code removal (blocking code cleanup)
4. 📚 Update TESTING_REQUIREMENTS.md

### If Issues Found

1. 📋 Document all issues with severity
2. 🔧 Create fix plan with priorities
3. ⚠️ Mark critical vs. minor issues
4. 🔄 Re-test after fixes

---

## Contact and Support

### Getting Help

- **Test issues:** Review this guide and troubleshooting section
- **Code issues:** Check docs/standards/ for coding guidelines
- **Architecture questions:** Refer to prompt.md

### Reporting Issues

When documenting issues, include:
1. Test name/number
2. Steps to reproduce
3. Expected result
4. Actual result
5. Environment details
6. Screenshots/logs if applicable

---

## Appendix: Test File Structure

```
tests/
├── realtime_features/
│   ├── test_websocket_manager.py       # Layer 1: WebSocket unit tests
│   ├── test_eventbus_websocket.py      # Layer 1: EventBus unit tests
│   ├── test_websocket_integration.py   # Layer 2: Integration tests
│   ├── run_tests.py                    # Test runner script
│   └── __init__.py
├── manual_testing/
│   ├── manual_test_checklist.md        # Layer 3: Manual test checklist
│   └── manual_test_results_*.md        # Test results (generated)
├── fixtures/
│   ├── websocket_fixtures.py           # Test fixtures and helpers
│   └── __init__.py
└── __init__.py
```

---

## Version History

- **v1.0** (2025-01-21): Initial testing guide for REAL-TIME WORKFLOW & FEEDBACK verification