# Quick Start: Test REAL-TIME WORKFLOW & FEEDBACK Now

**Goal:** Verify your real-time features work correctly in under 1 hour.

---

## Step 1: Run Automated Tests (5-10 minutes)

```bash
# Navigate to project root
cd /path/to/PinkBison_creative_studio

# Activate your environment
conda activate multimodal-assistant

# Run all automated tests
python tests/realtime_features/run_tests.py
```

**Expected Output:**
```
================================================================================
  REAL-TIME WORKFLOW & FEEDBACK Test Suite
================================================================================

Layer 1: Unit Tests
--------------------------------------------------------------------------------
  WebSocketManager Unit Tests
--------------------------------------------------------------------------------
Running: python -m pytest tests/realtime_features/test_websocket_manager.py -v

[... test output ...]

✓ All automated tests passed!

Next Steps:
1. Run manual UI tests using: tests/manual_testing/manual_test_checklist.md
2. Start Streamlit and verify real-time features in browser
3. Document any issues found
```

**If tests fail:** Review output, check imports, verify environment is correct.

---

## Step 2: Start Your Servers (2 minutes)

Open 4 terminal tabs:

### Tab 1: vLLM Server (WSL)
```bash
# Start vLLM server for Qwen2.5-3B
# (your usual command here)
```

### Tab 2: Embeddings Server (WSL)
```bash
# Start embeddings server for bge-small
# (your usual command here)
```

### Tab 3: Streamlit UI (Windows)
```bash
conda activate multimodal-assistant
streamlit run studio_ui.py
```

### Tab 4: Optional Orchestrator
```bash
# If you want to test with orchestrator running
# (usually not needed for UI-driven workflows)
```

**Verify servers are running:**
- vLLM: `http://localhost:8000` responds
- Embeddings: `http://localhost:8001` responds
- Streamlit: `http://localhost:8501` opens in browser

---

## Step 3: Quick Smoke Test (5 minutes)

Open browser to `http://localhost:8501`

### Test 1: Check WebSocket Connection
1. Open browser console (F12 → Console tab)
2. Look for WebSocket connection logs
3. Check for "Connected" status indicator in UI

**Expected:** No WebSocket errors, connection established

### Test 2: Check Live Event Stream
1. Navigate to "Live Event Stream" or "Intelligence Panel"
2. Trigger any agent action (e.g., generate outline)
3. Watch for events to appear WITHOUT refreshing

**Expected:** Events appear in real-time as they happen

### Test 3: Test Pipeline Controls
1. Navigate to pipeline controls
2. Click "Start Pipeline" for any workflow
3. Verify status changes to "running"
4. Verify progress bar updates automatically

**Expected:** Pipeline starts, status updates in real-time

### Test 4: Test Feedback Injection
1. While pipeline is running, find feedback injection UI
2. Enter feedback: "Test feedback message"
3. Target any agent
4. Submit feedback

**Expected:** Feedback submits without UI freeze, appears in event stream

---

## Step 4: Quick Results Assessment (2 minutes)

### ✅ All Working
If all 4 smoke tests pass:
- **Verdict:** REAL-TIME WORKFLOW & FEEDBACK is functional!
- **Next:** Run full manual test checklist for comprehensive verification
- **Action:** Mark feature as VERIFIED in prompt.md

### ⚠️ Some Issues
If 2-3 tests pass:
- **Verdict:** Core functionality works, minor issues exist
- **Next:** Document issues, run full manual tests to identify scope
- **Action:** Create fix plan for issues found

### ❌ Major Problems
If 0-1 tests pass:
- **Verdict:** Implementation needs debugging
- **Next:** Check implementation files, review WebSocket logs
- **Action:** Debug before proceeding to full testing

---

## Step 5: Full Manual Testing (Optional, 1-2 hours)

If smoke tests pass, you can run comprehensive manual testing:

```bash
# Open the checklist
code tests/manual_testing/manual_test_checklist.md
# or
notepad tests/manual_testing/manual_test_checklist.md
```

Work through all 28 tests systematically, documenting results.

---

## Troubleshooting

### Issue: Automated tests fail to run

**Solution:**
```bash
# Verify pytest is installed
pip install pytest

# Try running individual test files
pytest tests/realtime_features/test_websocket_manager.py -v
```

### Issue: WebSocket connection fails in browser

**Check:**
1. Terminal running Streamlit - look for "WebSocket server started on port 8765"
2. Browser console (F12) for WebSocket errors
3. Port 8765 is not blocked by firewall

**Fix:**
- Restart Streamlit
- Check firewall settings
- Verify WebSocket server code exists in `studio_ui.py`

### Issue: Events don't appear in Live Event Stream

**Check:**
1. Live Event Stream component is rendered in UI
2. EventBus is publishing events (check terminal logs)
3. WebSocket is connected (check connection status)

**Debug:**
- Open browser console to see if WebSocket messages are received
- Check EventBus.publish() is being called
- Verify Live Event Stream component code

### Issue: UI freezes during pipeline execution

**This is a CRITICAL bug** - indicates blocking code still exists

**Check:**
- Producer agent is using async/await
- No `time.sleep()` + `st.rerun()` patterns
- Background threading is working

**Fix:**
- Review LEGACY CODE REMOVAL items in roadmap
- Ensure all blocking code has been removed

---

## Expected Timeline

- **Automated tests:** 5-10 minutes
- **Server startup:** 2 minutes
- **Smoke tests:** 5 minutes
- **Assessment:** 2 minutes
- **Total:** ~15-20 minutes for quick verification

**Full manual testing:** Add 1-2 hours for comprehensive coverage

---

## Success Checklist

Quick verification (minimum):
- [ ] Automated tests pass (90%+)
- [ ] WebSocket connects
- [ ] Events stream in real-time
- [ ] Pipeline controls respond
- [ ] Feedback injection works

Full verification (comprehensive):
- [ ] All 28 manual tests completed
- [ ] All critical tests pass
- [ ] Issues documented
- [ ] Results recorded

---

## What to Do With Results

### All Tests Pass ✅
1. Update `prompt.md` - mark REAL-TIME WORKFLOW & FEEDBACK as VERIFIED
2. Update roadmap - move to LEGACY CODE REMOVAL phase
3. Celebrate! 🎉

### Some Issues Found ⚠️
1. Document all issues in manual test checklist
2. Categorize: Critical / Major / Minor
3. Create fix plan
4. Re-test after fixes

### Major Problems ❌
1. Review implementation files
2. Check WebSocket server code
3. Verify EventBus integration
4. Debug before full testing

---

## Files You Need

**For automated testing:**
- `tests/realtime_features/run_tests.py` ← Run this

**For manual testing:**
- `tests/manual_testing/manual_test_checklist.md` ← Fill this out

**For reference:**
- `tests/TESTING_GUIDE_REALTIME.md` ← Complete guide
- `TEST_PLAN_REALTIME_FEATURES.md` ← Full test plan
- `EXECUTIVE_SUMMARY_TESTING.md` ← This summary

---

## Quick Commands Reference

```bash
# Run all automated tests
python tests/realtime_features/run_tests.py

# Run specific test file
pytest tests/realtime_features/test_websocket_manager.py -v

# Run with more detail
pytest tests/realtime_features/test_websocket_manager.py -v -s

# Start Streamlit
streamlit run studio_ui.py

# Check if servers are running
curl http://localhost:8000/v1/models  # vLLM
curl http://localhost:8001/v1/models  # Embeddings
```

---

## Ready? Let's Test!

1. Open terminal
2. Run: `python tests/realtime_features/run_tests.py`
3. Start your servers
4. Open browser to `localhost:8501`
5. Work through smoke tests
6. Document results

**You've got this!** The test suite is comprehensive and will give you confidence in your implementation.