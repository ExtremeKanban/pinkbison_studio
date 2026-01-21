"""
Pipeline control UI with inline and expander versions
"""

import streamlit as st
from typing import Optional

from core.registry import REGISTRY
from ui.common import get_producer


def render_pipeline_controls_inline(project_name: str):
    """
    Render pipeline controls inline (no expander).
    Pipeline type dropdown + buttons in one row.
    """
    # Initialize session state
    if f"pipeline_render_count_{project_name}" not in st.session_state:
        st.session_state[f"pipeline_render_count_{project_name}"] = 0
    
    if f"selected_pipeline_type_{project_name}" not in st.session_state:
        st.session_state[f"selected_pipeline_type_{project_name}"] = "story_bible"
    
    render_id = st.session_state[f"pipeline_render_count_{project_name}"]
    
    # Get pipeline controller
    pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
    status = pipeline_controller.get_status()
    
    # Layout: Pipeline Type + Buttons in one row
    col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
    
    with col1:
        # Pipeline type dropdown - KEEP THE LABEL VISIBLE
        pipeline_type = st.selectbox(
            "Pipeline Type",
            options=["story_bible", "chapter", "full_story", "director"],
            format_func=lambda x: {
                "story_bible": "📖 Story Bible",
                "chapter": "📄 Single Chapter",
                "full_story": "📚 Full Story",
                "director": "🎬 Director Mode"
            }[x],
            key=f"pipeline_type_{project_name}_{render_id}",
            disabled=status["is_running"] or status["is_paused"]
        )
        st.session_state[f"selected_pipeline_type_{project_name}"] = pipeline_type
    
    with col2:
        # Chapter index (only for chapter pipeline)
        if pipeline_type == "chapter":
            chapter_index = st.number_input(
                "Ch #",
                min_value=0,
                max_value=99,
                value=0,
                key=f"chapter_idx_{project_name}_{render_id}",
                disabled=status["is_running"] or status["is_paused"],
                label_visibility="collapsed"
            )
        else:
            chapter_index = None
            st.write("")  # Empty space for alignment
    
    with col3:
        # Start button
        if not (status["is_running"] or status["is_paused"]):
            if st.button("▶️ Start",
                        type="secondary",
                        key=f"start_{project_name}_{render_id}",
                        use_container_width=True):
                st.session_state[f"pipeline_render_count_{project_name}"] += 1
                _start_pipeline_ui(project_name, str(render_id), pipeline_type, chapter_index)
        else:
            st.button("▶️ Start",
                     disabled=True,
                     key=f"start_disabled_{project_name}_{render_id}",
                     use_container_width=True)
    
    with col4:
        # Pause button
        if st.button("⏸️ Pause",
                    disabled=not status["is_running"],
                    type="secondary",
                    key=f"pause_{project_name}_{render_id}",
                    use_container_width=True):
            if pipeline_controller.pause():
                st.success("Paused")
                st.rerun()
    
    with col5:
        # Resume button
        if st.button("⏯️ Resume",
                    disabled=not status["is_paused"],
                    type="secondary",
                    key=f"resume_{project_name}_{render_id}",
                    use_container_width=True):
            if pipeline_controller.resume():
                st.success("Resumed")
                st.rerun()
    
    with col6:
        # Stop button
        if st.button("⏹️ Stop",
                    disabled=not (status["is_running"] or status["is_paused"]),
                    type="secondary",
                    key=f"stop_{project_name}_{render_id}",
                    use_container_width=True):
            if pipeline_controller.stop():
                st.success("Stopped")
                st.rerun()
    
    # Real-time status component AFTER the controls
    try:
        from ui.components.realtime_status import realtime_status
        realtime_status(project_name=project_name)
    except ImportError:
        pass  # Silently fail if component not available


def _start_pipeline_ui(
    project_name: str, 
    render_id: str, 
    pipeline_type: Optional[str] = None,
    chapter_index: Optional[int] = None
):
    """Start a pipeline from UI parameters."""
    try:
        # Get producer
        producer = get_producer(project_name)
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        
        # Build COMMON pipeline arguments
        common_args = {
            "idea": st.session_state.get("producer_seed_idea", ""),
            "genre": st.session_state.get("project_genre", ""),
            "tone": st.session_state.get("project_tone", ""),
            "themes": st.session_state.get("project_themes", ""),
            "setting": st.session_state.get("project_setting", ""),
            "auto_memory": True,
        }
        
        # Get the appropriate pipeline function (wrap async in sync for thread)
        import asyncio
        
        def run_async_in_thread(coro):
            """Helper to run async function in background thread"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
        
        if pipeline_type == "story_bible":
            # Story bible ONLY takes common args
            pipeline_args = common_args
            
            def pipeline_func(controller=None, feedback_manager=None, **kwargs):
                return run_async_in_thread(producer.run_story_bible_pipeline_async(**kwargs))
            task_name = "Story Bible Generation"
            total_steps = 3
            
        elif pipeline_type == "chapter":
            # Chapter takes additional args
            pipeline_args = {
                **common_args,
                "run_continuity": True,
                "run_editor": True,
                "max_chapters": 10,
                "chapter_index": chapter_index or 0
            }
            
            def pipeline_func(controller=None, feedback_manager=None, **kwargs):
                return run_async_in_thread(producer.run_chapter_pipeline_async(**kwargs))
            task_name = f"Chapter {chapter_index} Generation"
            total_steps = 5
            
        elif pipeline_type == "full_story":
            # Full story takes additional args
            pipeline_args = {
                **common_args,
                "run_continuity": True,
                "run_editor": True,
                "max_chapters": 10,
            }
            
            def pipeline_func(controller=None, feedback_manager=None, **kwargs):
                return run_async_in_thread(producer.run_full_story_pipeline_async(**kwargs))
            task_name = "Full Story Generation"
            total_steps = 13  # 10 chapters + 3 steps
            
        elif pipeline_type == "director":
            # Director mode takes additional args
            pipeline_args = {
                **common_args,
                "run_continuity": True,
                "run_editor": True,
                "max_chapters": 10,
            }
            
            def pipeline_func(controller=None, feedback_manager=None, **kwargs):
                return run_async_in_thread(producer.run_director_mode_async(**kwargs))
            task_name = "Director Mode"
            total_steps = 10
            
        else:
            st.error(f"Unknown pipeline type: {pipeline_type}")
            return
        
        # Start the pipeline
        print(f"[UI] Starting pipeline: {task_name}")
        print(f"[UI] Pipeline args: {list(pipeline_args.keys())}")
        print(f"[UI] Total steps: {total_steps}")
        
        success = pipeline_controller.start_pipeline(
            pipeline_func=pipeline_func,
            task_name=task_name,
            total_steps=total_steps,
            **pipeline_args
        )
        
        print(f"[UI] Pipeline start success: {success}")
        
        if success:
            st.success(f"✅ {task_name} started!")
            if hasattr(pipeline_controller, 'feedback_manager'):
                pipeline_controller.feedback_manager.clear_processed()
            st.rerun()
        else:
            st.error("❌ Could not start pipeline (already running?)")
            current_status = pipeline_controller.get_status()
            st.json(current_status)
            
    except Exception as e:
        st.error(f"❌ Error starting pipeline: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


def render_pipeline_status_overview(project_name: str):
    """Render compact pipeline status overview."""
    try:
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        status = pipeline_controller.get_status()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", status["status"].title())
        
        with col2:
            if status["is_running"] and status.get("progress"):
                progress = status["progress"]
                st.metric("Progress", f"{progress.get('step_number', 0)}/{progress.get('total_steps', 0)}")
            else:
                st.metric("Progress", "—")
        
        with col3:
            if status.get("current_task"):
                st.metric("Current Task", status["current_task"][:30])
            else:
                st.metric("Current Task", "None")
                
    except Exception as e:
        st.caption(f"Status unavailable: {str(e)}")