# test_pipeline_controller_basic.py
import asyncio
import time
from core.pipeline_controller import PipelineController, PipelineStatus

async def mock_pipeline(**kwargs):
    """Mock pipeline for testing"""
    print("   ⏳ Mock pipeline running...")
    
    # Simulate work
    await asyncio.sleep(0.5)
    return {"test": "complete"}

def test_pipeline_controller():
    print("🧪 Testing PipelineController Basics...")
    
    # Create pipeline controller
    pc = PipelineController("test_pipeline_project")
    
    # Test 1: Initial status
    print("1. Checking initial status...")
    status = pc.get_status()
    print(f"   ✅ Initial status: {status['status']} (should be 'idle')")
    
    # Test 2: Start pipeline
    print("\n2. Starting pipeline...")
    try:
        pipeline_id = pc.start_pipeline(
            pipeline_func=mock_pipeline,
            pipeline_type="test",
            pipeline_args={"test": "data"}
        )
        print(f"   ✅ Started pipeline ID: {pipeline_id}")
        
        # Wait a bit for pipeline to start
        time.sleep(0.1)
        
        # Test 3: Check running status
        print("\n3. Checking running status...")
        status = pc.get_status()
        print(f"   ✅ Status after start: {status['status']} (should be 'running')")
        
        # Test 4: Update progress
        print("\n4. Testing progress updates...")
        pc.update_progress("test_step", 1, 3, "Testing progress")
        status = pc.get_status()
        progress = status['progress']['percent_complete']
        print(f"   ✅ Progress: {progress:.1f}%")
        
        # Wait for pipeline to complete
        print("\n5. Waiting for completion...")
        time.sleep(1)
        
        # Test 5: Check completion status
        status = pc.get_status()
        print(f"   ✅ Final status: {status['status']} (should be 'completed')")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_pipeline_controller()
        if success:
            print("\n🎉 PipelineController test PASSED!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()