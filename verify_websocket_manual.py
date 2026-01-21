"""
Manual verification guide for WebSocket system.
Tells you exactly what to look for in the UI.
"""

import time
from core.event_bus import EventBus
from core.websocket_manager import WEBSOCKET_MANAGER

print("🎯 MANUAL WEBSOCKET VERIFICATION GUIDE")
print("=" * 60)

print("\n📋 PREREQUISITES:")
print("1. Streamlit UI should be running: http://localhost:8501")
print("2. WebSocket server should be running on port 8765")
print("3. Browser should be open to the Streamlit UI")

print("\n🔍 STEP 1: Check WebSocket Server")
print("-" * 40)

if not WEBSOCKET_MANAGER.running:
    print("Starting WebSocket server...")
    WEBSOCKET_MANAGER.start_server()
    time.sleep(2)

if WEBSOCKET_MANAGER.running:
    print("✅ WebSocket server is running")
else:
    print("❌ WebSocket server failed to start")
    print("   Check logs for errors")

print("\n🔍 STEP 2: Generate Test Events")
print("-" * 40)

print("Creating test events that will appear in the UI...")
event_bus = EventBus(project_name="manual_verification")

# Generate a series of test events
test_events = [
    ("system_start", "System started verification"),
    ("test_progress", "Progress update 25%"),
    ("test_progress", "Progress update 50%"),
    ("test_progress", "Progress update 75%"),
    ("test_complete", "Verification complete!"),
]

for i, (event_type, description) in enumerate(test_events):
    event_bus.publish(
        sender="verification_bot",
        recipient="ui",
        event_type=event_type,
        payload={
            "step": i + 1,
            "description": description,
            "timestamp": time.time(),
            "verification": True
        }
    )
    print(f"  📤 Event {i+1}: {event_type} - {description}")
    time.sleep(0.5)

print(f"\n✅ {len(test_events)} test events generated")

print("\n🔍 STEP 3: Manual UI Verification")
print("-" * 40)
print("\nIN YOUR BROWSER, DO THE FOLLOWING:")
print("=" * 40)

print("\n1. 📍 Navigate to:")
print("   http://localhost:8501")
print("   (Should already be open)")

print("\n2. 🔍 Find 'Live Event Stream':")
print("   - Look for section with 📡 icon")
print("   - It might be collapsed (click to expand)")

print("\n3. ✅ Check Connection Status:")
print("   Should show one of:")
print("   - '✅ Connected (real-time)'")
print("   - 'Active' connection status")
print("   - WebSocket indicator")

print("\n4. 📊 Look for Events:")
print("   You should see:")
print("   - 'system_start' event")
print("   - Multiple 'test_progress' events")
print("   - 'test_complete' event")
print("   - Events should have timestamps")
print("   - Events should appear without page refresh")

print("\n5. 🎯 Event Details:")
print("   Click on event cards to see:")
print("   - Sender: 'verification_bot'")
print("   - Payload with verification data")
print("   - Structured JSON data")

print("\n6. ⚡ Test Real-time Updates:")
print("   - Keep the UI open")
print("   - Run this command again:")
print("     python verify_websocket_manual.py")
print("   - New events should appear immediately")

print("\n🔍 STEP 4: Expected Results")
print("-" * 40)
print("✅ Events appear within 1-2 seconds")
print("✅ No page refresh needed")
print("✅ Connection status shows 'real-time'")
print("✅ Multiple events display correctly")
print("✅ Payload data is visible when expanded")

print("\n🔍 STEP 5: Troubleshooting")
print("-" * 40)
print("If events don't appear:")
print("1. ❌ Check browser console for errors (F12)")
print("2. ❌ Check Streamlit terminal for WebSocket errors")
print("3. ❌ Verify WebSocket server is running")
print("4. ❌ Check 'Live Event Stream' is expanded")
print("5. ❌ Try clicking 'Refresh' in the Live Event Stream")

print("\n" + "=" * 60)
print("🎯 VERIFICATION COMPLETE")
print("\nThe WebSocket system should be working if you can see")
print("the test events appearing in real-time in the UI.")
print("\nIf successful, Phase 1 WebSocket implementation is complete! 🎉")