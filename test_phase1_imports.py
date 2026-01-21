# test_phase1_imports.py
print("Testing Phase 1 imports (fixed version)...")
print("=" * 60)

test_results = []

# Test 1: Basic imports
print("\n1. Testing basic imports...")
try:
    from core.feedback_manager import FeedbackManager, FeedbackType, FeedbackPriority
    print("   ✅ FeedbackManager imported")
    test_results.append(("FeedbackManager", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    test_results.append(("FeedbackManager", False))

# Test 2: PipelineController
print("\n2. Testing PipelineController...")
try:
    from core.pipeline_controller import PipelineController, PipelineStatus
    print("   ✅ PipelineController imported")
    test_results.append(("PipelineController", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    test_results.append(("PipelineController", False))

# Test 3: ProducerAgent
print("\n3. Testing ProducerAgent...")
try:
    from agents.producer import ProducerAgent
    print("   ✅ ProducerAgent imported")
    
    # Check for async methods
    async_methods = [m for m in dir(ProducerAgent) if 'async' in m.lower()]
    print(f"   Found {len(async_methods)} async methods")
    
    if len(async_methods) >= 4:
        print(f"   ✅ Has all async methods: {async_methods}")
        test_results.append(("ProducerAgent async", True))
    else:
        print(f"   ⚠️  Missing some async methods: {async_methods}")
        test_results.append(("ProducerAgent async", False))
        
except Exception as e:
    print(f"   ❌ Failed: {e}")
    test_results.append(("ProducerAgent", False))

# Test 4: Registry
print("\n4. Testing Registry...")
try:
    from core.registry import REGISTRY
    print("   ✅ REGISTRY imported")
    test_results.append(("REGISTRY", True))
except Exception as e:
    print(f"   ❌ Failed: {e}")
    test_results.append(("REGISTRY", False))

# Test 5: New UI components
print("\n5. Testing UI components...")
ui_tests = [
    ("live_event_panel", "ui.live_event_panel", "render_live_event_panel"),
    ("pipeline_controls_ui", "ui.pipeline_controls_ui", "render_pipeline_controls"),
    ("feedback_injector_ui", "ui.feedback_injector_ui", "render_feedback_injector"),
    ("intelligence_panel", "ui.intelligence_panel", "render_intelligence_panel"),
]

for test_name, module_name, function_name in ui_tests:
    try:
        module = __import__(module_name, fromlist=[function_name])
        func = getattr(module, function_name)
        print(f"   ✅ {test_name}: {function_name} loaded")
        test_results.append((f"UI {test_name}", True))
    except Exception as e:
        print(f"   ❌ {test_name} failed: {e}")
        test_results.append((f"UI {test_name}", False))

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY:")
print("-" * 60)

passed = 0
total = len(test_results)

for test_name, success in test_results:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status:10} {test_name}")
    if success:
        passed += 1

print("-" * 60)
print(f"TOTAL: {passed}/{total} tests passed")

if passed == total:
    print("\n🌟 ALL TESTS PASSED! Phase 1 imports are working correctly.")
    print("   You can now start testing the real-time features in the UI.")
else:
    print(f"\n⚠️  {total - passed} tests failed. Check the errors above.")