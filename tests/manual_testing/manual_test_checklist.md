# Manual Testing Checklist: REAL-TIME WORKFLOW & FEEDBACK

## Purpose
Step-by-step manual verification of real-time features in the actual Streamlit UI.

## Prerequisites
- [ ] All four terminal tabs running:
  - Tab 1: vLLM server (WSL) at `localhost:8000`
  - Tab 2: Embeddings server (WSL) at `localhost:8001`
  - Tab 3: Streamlit UI at `localhost:8501`
  - Tab 4: (Optional) Orchestrator process
- [ ] Test project created or default project available
- [ ] Browser open to `localhost:8501`

---

## Test Suite 1: WebSocket Connection

### Test 1.1: WebSocket Server Startup
**Objective:** Verify WebSocket server starts with Streamlit

**Steps:**
1. Start Streamlit: `streamlit run studio_ui.py`
2. Look for WebSocket server log message in terminal
3. Check browser console (F12 → Console tab)

**Expected Result:**
- [ ] Terminal shows "WebSocket server started on port 8765" or similar
- [ ] No error messages about port 8765 being in use
- [ ] Browser console shows no WebSocket connection errors

**Actual Result:**
- Server start message: _____________________
- Errors (if any): _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 1.2: WebSocket Connection Status in UI
**Objective:** Verify connection status displays correctly

**Steps:**
1. Navigate to "Intelligence Panel" or main page
2. Look for WebSocket connection indicator
3. Check if it shows "Connected" or "Disconnected"

**Expected Result:**
- [ ] Connection status indicator visible
- [ ] Shows "Connected" when WebSocket active
- [ ] Green/positive visual indicator

**Actual Result:**
- Status shown: _____________________
- Visual indicator: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 1.3: WebSocket Reconnection
**Objective:** Verify WebSocket reconnects after disconnection

**Steps:**
1. Verify WebSocket is connected
2. Stop Streamlit (Ctrl+C)
3. Restart Streamlit
4. Check if connection re-establishes

**Expected Result:**
- [ ] WebSocket reconnects automatically
- [ ] No manual page refresh needed
- [ ] Connection status updates to "Connected"

**Actual Result:**
- Reconnection time: _____________________
- Manual action needed: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

## Test Suite 2: Live Event Stream

### Test 2.1: Event Stream Display
**Objective:** Verify Live Event Stream panel displays

**Steps:**
1. Navigate to "Live Event Stream" tab/section
2. Verify panel is visible
3. Check for event list/display area

**Expected Result:**
- [ ] Live Event Stream panel visible
- [ ] Event display area present
- [ ] Controls (clear, filter) visible if implemented

**Actual Result:**
- Panel visible: _____________________
- Components present: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 2.2: Real-time Event Updates
**Objective:** Verify events appear in real-time without refresh

**Steps:**
1. Open Live Event Stream panel
2. Trigger an agent action (e.g., generate outline)
3. Watch for events to appear WITHOUT clicking refresh
4. Wait 30-60 seconds observing the stream

**Expected Result:**
- [ ] Events appear in stream as they occur
- [ ] No page refresh needed
- [ ] Events show sender, recipient, type, payload
- [ ] Timestamps are recent/current

**Actual Result:**
- Events appeared automatically: _____________________
- Refresh needed: _____________________
- Event details complete: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 2.3: Multiple Event Types
**Objective:** Verify different event types display correctly

**Steps:**
1. Trigger multiple different agent actions:
   - Plot outline generation
   - World building
   - Character creation
2. Check if all event types appear in stream

**Expected Result:**
- [ ] All event types visible
- [ ] Each shows correct event_type field
- [ ] Payloads contain expected data
- [ ] Events are distinguishable

**Actual Result:**
- Event types seen: _____________________
- All events captured: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 2.4: Event Stream Scrolling
**Objective:** Verify event stream handles many events

**Steps:**
1. Generate 20+ events (run a full pipeline)
2. Check if stream scrolls correctly
3. Verify older events remain accessible

**Expected Result:**
- [ ] Stream scrolls smoothly
- [ ] Can scroll to see older events
- [ ] No performance degradation
- [ ] Buffer limit respected (if implemented)

**Actual Result:**
- Scrolling behavior: _____________________
- Performance: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

## Test Suite 3: Pipeline Controls

### Test 3.1: Pipeline Control Panel Display
**Objective:** Verify pipeline controls are visible and functional

**Steps:**
1. Navigate to pipeline control section
2. Check for Start/Pause/Resume/Stop buttons
3. Verify initial state shows "idle" or similar

**Expected Result:**
- [ ] All control buttons visible
- [ ] Pipeline status display visible
- [ ] Progress indicator present
- [ ] Current step display visible

**Actual Result:**
- Buttons present: _____________________
- Status display: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 3.2: Start Pipeline
**Objective:** Verify pipeline starts correctly

**Steps:**
1. Click "Start Pipeline" or equivalent button
2. Observe status change
3. Check for progress updates

**Expected Result:**
- [ ] Status changes to "running"
- [ ] Progress bar appears/updates
- [ ] Current step displays
- [ ] UI remains responsive

**Actual Result:**
- Status change: _____________________
- Progress visible: _____________________
- UI responsive: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 3.3: Pause Pipeline
**Objective:** Verify pipeline can be paused

**Steps:**
1. Start a pipeline
2. Click "Pause" button mid-execution
3. Verify pipeline pauses

**Expected Result:**
- [ ] Status changes to "paused"
- [ ] Progress stops updating
- [ ] Current work completes before pause
- [ ] Resume button becomes available

**Actual Result:**
- Status change: _____________________
- Pause behavior: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 3.4: Resume Pipeline
**Objective:** Verify paused pipeline can resume

**Steps:**
1. Start and pause a pipeline
2. Click "Resume" button
3. Verify pipeline continues

**Expected Result:**
- [ ] Status changes to "running"
- [ ] Pipeline continues from where it paused
- [ ] Progress continues updating
- [ ] No work is lost

**Actual Result:**
- Resume successful: _____________________
- Work continued correctly: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 3.5: Stop Pipeline
**Objective:** Verify pipeline can be stopped

**Steps:**
1. Start a pipeline
2. Click "Stop" button
3. Verify pipeline stops completely

**Expected Result:**
- [ ] Status changes to "stopped" or "idle"
- [ ] Pipeline execution terminates
- [ ] Partial work is saved (if applicable)
- [ ] Can start new pipeline

**Actual Result:**
- Stop successful: _____________________
- Partial work handling: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 3.6: Real-time Progress Updates
**Objective:** Verify progress updates without page refresh

**Steps:**
1. Start a multi-step pipeline
2. Do NOT refresh the page
3. Watch progress bar and step indicators

**Expected Result:**
- [ ] Progress bar updates automatically
- [ ] Current step text updates
- [ ] Percentage/step count updates
- [ ] No manual refresh needed

**Actual Result:**
- Auto-update working: _____________________
- Update frequency: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

## Test Suite 4: Feedback Injection

### Test 4.1: Feedback Injector Display
**Objective:** Verify feedback injection interface is accessible

**Steps:**
1. Navigate to feedback injection section
2. Check for feedback input controls
3. Verify target agent selector present

**Expected Result:**
- [ ] Feedback input field visible
- [ ] Target agent dropdown/selector visible
- [ ] Priority selector visible (if implemented)
- [ ] Submit button visible

**Actual Result:**
- Components present: _____________________
- Interface usability: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 4.2: Inject Feedback During Pipeline
**Objective:** Verify feedback can be injected during execution

**Steps:**
1. Start a pipeline
2. While pipeline is running, inject feedback:
   - Target: "SceneGenerator"
   - Message: "Make the scene more suspenseful"
   - Priority: "high"
3. Check if feedback is acknowledged

**Expected Result:**
- [ ] Feedback form submits successfully
- [ ] Confirmation message appears
- [ ] No UI freeze or lag
- [ ] Feedback appears in event stream

**Actual Result:**
- Submission successful: _____________________
- Feedback visibility: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 4.3: Feedback Appears for Target Agent
**Objective:** Verify injected feedback reaches target agent

**Steps:**
1. Inject feedback during pipeline execution
2. Check Live Event Stream for feedback event
3. Verify target agent field is correct

**Expected Result:**
- [ ] Feedback event appears in stream
- [ ] Event shows correct target agent
- [ ] Feedback message content is preserved
- [ ] Priority is indicated

**Actual Result:**
- Event appeared: _____________________
- Correct targeting: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 4.4: Multiple Feedback Injections
**Objective:** Verify multiple feedbacks can be injected

**Steps:**
1. Start a pipeline
2. Inject 3-5 different feedback messages
3. Target different agents
4. Verify all are received

**Expected Result:**
- [ ] All feedback messages submit successfully
- [ ] All appear in event stream
- [ ] No messages are lost
- [ ] Correct ordering maintained

**Actual Result:**
- All messages received: _____________________
- Order preserved: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

## Test Suite 5: UI Responsiveness

### Test 5.1: UI Doesn't Freeze During Pipeline
**Objective:** Verify UI remains responsive during pipeline execution

**Steps:**
1. Start a long-running pipeline (story bible or chapter generation)
2. Try interacting with other UI elements:
   - Switch tabs
   - Scroll event stream
   - Click other buttons
3. Verify UI responds immediately

**Expected Result:**
- [ ] UI responds to all interactions
- [ ] No freezing or lag
- [ ] Can switch tabs freely
- [ ] Other controls remain functional

**Actual Result:**
- UI responsiveness: _____________________
- Any lag observed: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 5.2: Multiple Components Update Simultaneously
**Objective:** Verify multiple UI components can update together

**Steps:**
1. Start a pipeline
2. Observe simultaneously:
   - Live Event Stream
   - Pipeline progress bar
   - Current step text
   - Any status indicators
3. Verify all update in real-time

**Expected Result:**
- [ ] All components update independently
- [ ] No component blocks others
- [ ] Updates are smooth
- [ ] No visual glitches

**Actual Result:**
- Simultaneous updates: _____________________
- Visual quality: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 5.3: Error Handling Doesn't Break UI
**Objective:** Verify errors don't crash or freeze UI

**Steps:**
1. Deliberately cause an error (stop model server, invalid input, etc.)
2. Observe error handling in UI
3. Verify UI remains functional

**Expected Result:**
- [ ] Error message displays clearly
- [ ] UI doesn't crash
- [ ] Can continue using other features
- [ ] WebSocket connection recovers

**Actual Result:**
- Error handling: _____________________
- UI recovery: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

## Test Suite 6: Integration Scenarios

### Test 6.1: Complete Story Bible Workflow
**Objective:** Verify entire story bible generation with real-time features

**Steps:**
1. Navigate to Story Bible generation
2. Fill in required fields
3. Start generation
4. Monitor Live Event Stream
5. Inject feedback mid-generation
6. Verify completion

**Expected Result:**
- [ ] All events appear in stream
- [ ] Progress updates throughout
- [ ] Feedback is processed
- [ ] Final result is complete
- [ ] No errors or crashes

**Actual Result:**
- Workflow completion: _____________________
- Real-time features: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 6.2: Chapter Generation with Live Feedback
**Objective:** Verify chapter generation with real-time feedback

**Steps:**
1. Start chapter generation
2. Monitor real-time progress
3. Inject 2-3 feedback messages during generation
4. Verify chapter completes with feedback incorporated

**Expected Result:**
- [ ] Real-time progress visible
- [ ] Feedback submitted successfully
- [ ] Chapter generation completes
- [ ] Feedback influence visible (if applicable)

**Actual Result:**
- Progress tracking: _____________________
- Feedback integration: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 6.3: Pipeline Pause/Resume Workflow
**Objective:** Verify pause/resume works in real workflow

**Steps:**
1. Start a multi-step pipeline
2. Let it run for 2-3 steps
3. Pause the pipeline
4. Inject feedback while paused
5. Resume pipeline
6. Verify completion

**Expected Result:**
- [ ] Pipeline pauses cleanly
- [ ] Feedback can be injected while paused
- [ ] Pipeline resumes successfully
- [ ] No work is lost
- [ ] Pipeline completes correctly

**Actual Result:**
- Pause/resume behavior: _____________________
- Work preservation: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

## Test Suite 7: Edge Cases

### Test 7.1: Rapid Event Generation
**Objective:** Verify UI handles high-frequency events

**Steps:**
1. Trigger action that generates many events quickly
2. Observe Live Event Stream performance
3. Check for dropped events or lag

**Expected Result:**
- [ ] All events are captured
- [ ] UI remains responsive
- [ ] No visible lag or freezing
- [ ] Buffer management works correctly

**Actual Result:**
- Event capture rate: _____________________
- UI performance: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 7.2: WebSocket Disconnection During Pipeline
**Objective:** Verify system handles WebSocket disconnection

**Steps:**
1. Start a pipeline
2. Simulate WebSocket disconnection (disable network briefly, or restart WebSocket server)
3. Observe behavior
4. Restore connection

**Expected Result:**
- [ ] Pipeline continues in background
- [ ] UI shows disconnection
- [ ] Reconnection is automatic
- [ ] Events sync after reconnection

**Actual Result:**
- Disconnect handling: _____________________
- Reconnection: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

### Test 7.3: Long-Running Pipeline
**Objective:** Verify real-time features work for extended periods

**Steps:**
1. Start a very long pipeline (full story generation)
2. Monitor for 10-15 minutes
3. Check for memory leaks or degradation
4. Verify features remain functional

**Expected Result:**
- [ ] WebSocket connection stable
- [ ] Events continue appearing
- [ ] No performance degradation
- [ ] Memory usage stable

**Actual Result:**
- Stability: _____________________
- Performance over time: _____________________
- Status: ⬜ PASS ⬜ FAIL ⬜ SKIP

**Notes:**
_____________________________________

---

## Test Summary

**Total Tests:** 28
**Passed:** _____
**Failed:** _____
**Skipped:** _____

### Critical Issues Found
1. _____________________________________
2. _____________________________________
3. _____________________________________

### Minor Issues Found
1. _____________________________________
2. _____________________________________
3. _____________________________________

### Recommendations
1. _____________________________________
2. _____________________________________
3. _____________________________________

### Overall Assessment
- [ ] REAL-TIME WORKFLOW & FEEDBACK is fully functional
- [ ] REAL-TIME WORKFLOW & FEEDBACK needs minor fixes
- [ ] REAL-TIME WORKFLOW & FEEDBACK needs major fixes
- [ ] REAL-TIME WORKFLOW & FEEDBACK is not functional

**Tested By:** _____________________
**Date:** _____________________
**Environment:** Windows 11, RTX 5080, Streamlit 1.52.1
**Notes:** _____________________________________