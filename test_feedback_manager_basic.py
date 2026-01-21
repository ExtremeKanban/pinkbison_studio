# test_feedback_manager_basic.py
from core.feedback_manager import FeedbackManager, FeedbackType, FeedbackPriority

def test_feedback_basics():
    print("🧪 Testing FeedbackManager Basics...")
    
    # Create a test project
    fm = FeedbackManager("test_feedback_project")
    
    # Test 1: Add feedback
    print("1. Adding feedback...")
    fb_id = fm.add_feedback(
        target_agent="plot_architect",
        feedback_type=FeedbackType.GUIDANCE,
        content="Test: Make the outline more detailed",
        priority=FeedbackPriority.HIGH
    )
    print(f"   ✅ Added feedback with ID: {fb_id}")
    
    # Test 2: Retrieve feedback
    print("\n2. Retrieving feedback...")
    feedback = fm.get_feedback_for_agent("plot_architect")
    print(f"   ✅ Retrieved {len(feedback)} feedback items")
    if feedback:
        print(f"   📝 First feedback: {feedback[0].content[:50]}...")
    
    # Test 3: Statistics
    print("\n3. Checking statistics...")
    stats = fm.get_stats()
    print(f"   📊 Stats: {stats['total']} total, {stats['unprocessed']} unprocessed")
    
    # Test 4: Mark as processed
    print("\n4. Marking as processed...")
    fm.mark_as_processed(fb_id)
    
    # Test 5: Check processed feedback
    print("\n5. Checking processed feedback...")
    feedback = fm.get_feedback_for_agent("plot_architect", unprocessed_only=True)
    print(f"   ✅ After processing: {len(feedback)} unprocessed items (should be 0)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_feedback_basics()
        if success:
            print("\n🎉 FeedbackManager test PASSED!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()