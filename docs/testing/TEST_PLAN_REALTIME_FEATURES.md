# Test Plan: REAL-TIME WORKFLOW & FEEDBACK Verification

## Purpose
Comprehensive testing strategy to verify that all real-time features work correctly in the actual Streamlit UI and integration layer.

## Test Layers

### Layer 1: Component Unit Tests
Test individual components in isolation without dependencies.

**Components to Test:**
1. WebSocketManager (`core/websocket_manager.py`)
2. EventBus WebSocket integration (`core/event_bus.py`)
3. Streamlit WebSocket Client (`ui/websocket_client.py`)
4. Live Event Panel (`ui/live_event_panel.py`)
5. Pipeline Controls (`ui/pipeline_controls_ui.py`)
6. Feedback Injector (`ui/feedback_injector_ui.py`)

### Layer 2: Integration Tests
Test how components work together.

**Integration Points:**
1. WebSocketManager + EventBus
2. WebSocket Client + Streamlit Session State
3. EventBus + Pipeline Controls
4. Feedback Injector + EventBus
5. Full WebSocket message flow

### Layer 3: Manual UI Testing
Step-by-step verification in actual Streamlit UI.

**Test Scenarios:**
1. WebSocket connection establishment
2. Real-time event streaming
3. Pipeline start/pause/resume/stop
4. Feedback injection during execution
5. Multi-component simultaneous updates
6. Error handling and recovery

### Layer 4: End-to-End Workflow Tests
Full pipeline execution with real-time features.

**Workflows to Test:**
1. Story Bible Generation with live updates
2. Chapter Generation with feedback injection
3. Multi-step pipeline with pause/resume
4. Error handling during pipeline execution

---

## Test Execution Order

### Phase 1: Unit Tests (Automated)
**Goal:** Verify individual components work in isolation  
**Duration:** ~15-30 minutes  
**Prerequisites:** Python environment with all dependencies

### Phase 2: Integration Tests (Automated)
**Goal:** Verify components work together  
**Duration:** ~30-60 minutes  
**Prerequisites:** Phase 1 complete, test project created

### Phase 3: Manual UI Testing (Interactive)
**Goal:** Verify actual Streamlit UI functionality  
**Duration:** ~1-2 hours  
**Prerequisites:** Phase 1-2 complete, Streamlit running

### Phase 4: End-to-End Tests (Semi-automated)
**Goal:** Verify full workflows with real-time features  
**Duration:** ~2-3 hours  
**Prerequisites:** All previous phases complete

---

## Expected Outcomes

### Success Criteria
- [ ] WebSocket server starts automatically with Streamlit
- [ ] WebSocket clients can connect and subscribe to projects
- [ ] EventBus events appear in Live Event Stream in real-time
- [ ] Events update without page refresh (no st.rerun())
- [ ] Pipeline controls (start/pause/resume/stop) work correctly
- [ ] Pipeline status updates in real-time
- [ ] Progress bars update dynamically
- [ ] Feedback can be injected during pipeline execution
- [ ] Feedback appears for target agents
- [ ] Priority system works correctly
- [ ] UI doesn't freeze during pipeline execution
- [ ] Multiple components update simultaneously
- [ ] Error handling doesn't break UI
- [ ] Connection status shows correctly in UI

### Known Issues to Watch For
- WebSocket server "failed to start" when already running (expected behavior)
- Browser automation tests may fail (Playwright/Streamlit compatibility)
- Duplicate keys in UI components (minor cleanup needed)

### Failure Criteria
- WebSocket server doesn't start
- Events don't appear in Live Event Stream
- Pipeline controls don't respond
- UI freezes during pipeline execution
- Feedback injection doesn't work
- Critical errors crash the UI

---

## Test Documentation

Each test will document:
1. **Test Name:** Clear description
2. **Prerequisites:** What must be set up first
3. **Steps:** Exact steps to execute
4. **Expected Result:** What should happen
5. **Actual Result:** What actually happened
6. **Status:** Pass/Fail/Skip
7. **Notes:** Any observations or issues

---

## Post-Testing Actions

After testing is complete:

1. **If all tests pass:**
   - Document verified features
   - Plan legacy code removal
   - Update roadmap

2. **If issues found:**
   - Document issues with severity
   - Create fix plan
   - Re-test after fixes

3. **Update documentation:**
   - Mark features as verified in prompt.md
   - Update TESTING_REQUIREMENTS.md
   - Create user guide for real-time features

---

## Test Files to Create

```
tests/
├── realtime_features/
│   ├── __init__.py
│   ├── test_websocket_manager.py          # Layer 1
│   ├── test_eventbus_websocket.py         # Layer 1
│   ├── test_streamlit_websocket_client.py # Layer 1
│   ├── test_websocket_integration.py      # Layer 2
│   ├── test_eventbus_integration.py       # Layer 2
│   ├── test_ui_integration.py             # Layer 2
│   └── test_end_to_end_workflows.py       # Layer 4
├── manual_testing/
│   ├── __init__.py
│   ├── manual_test_checklist.md           # Layer 3 checklist
│   ├── manual_test_results.md             # Layer 3 results
│   └── test_scenarios.json                # Layer 3 scenarios
└── fixtures/
    ├── __init__.py
    ├── test_project_setup.py              # Test project creation/cleanup
    └── websocket_fixtures.py              # WebSocket test fixtures
```

---

## Next Steps

1. Create test file structure
2. Implement Layer 1 unit tests
3. Implement Layer 2 integration tests
4. Create Layer 3 manual testing checklist
5. Run all tests and document results
6. Address any issues found
7. Update project documentation