"""
Pipeline control UI with start/pause/resume/stop buttons - CLEAN VERSION.
"""

import streamlit as st
from typing import Optional

from core.registry import REGISTRY
from ui.common import get_producer


def render_pipeline_controls(project_name: str):
    """
    Render pipeline control buttons and status.
    """
    # Initialize session state counter if not exists (more stable than timestamp)
    if f"pipeline_render_count_{project_name}" not in st.session_state:
        st.session_state[f"pipeline_render_count_{project_name}"] = 0
    
    # Use render count instead of timestamp for keys
    render_id = st.session_state[f"pipeline_render_count_{project_name}"]
    
    with st.expander("🎮 Pipeline Controls", expanded=True):
        
        # Get pipeline controller
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        status = pipeline_controller.get_status()
        
        # Current status display
        st.markdown(f"**Current Status:** `{status['status']}`")
        
        # Show error message if status is error
        if status['status'] == 'error' and status.get('current_task'):
            st.error(f"❌ {status['current_task']}")
        
        if status["progress"]["percent_complete"] > 0:
            st.progress(
                status["progress"]["percent_complete"] / 100,
                text=status["progress"]["current_step"]
            )
        
        # Control buttons in columns (only pause/resume/stop - start is via Quick Start below)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⏸️ Pause",
                        disabled=not status["is_running"],
                        use_container_width=True,
                        key=f"pipeline_pause_{project_name}_{render_id}"):
                if pipeline_controller.pause():
                    st.success("Pipeline paused")
                    st.rerun()
                else:
                    st.error("Could not pause pipeline")
        
        with col2:
            if st.button("⏯️ Resume",
                        disabled=not status["is_paused"],
                        use_container_width=True,
                        key=f"pipeline_resume_{project_name}_{render_id}"):
                if pipeline_controller.resume():
                    st.success("Pipeline resumed")
                    st.rerun()
                else:
                    st.error("Could not resume pipeline")
        
        with col3:
            if st.button("⏹️ Stop",
                        disabled=not (status["is_running"] or status["is_paused"]),
                        use_container_width=True,
                        type="secondary",
                        key=f"pipeline_stop_{project_name}_{render_id}"):
                if pipeline_controller.stop():
                    st.success("Pipeline stopped")
                    st.rerun()
                else:
                    st.error("Could not stop pipeline")
        
        # Pipeline type selection (for start)
        if not (status["is_running"] or status["is_paused"]):
            st.markdown("---")
            st.markdown("### Start New Pipeline")
            
            pipeline_type = st.selectbox(
                "Pipeline Type",
                options=["story_bible", "chapter", "full_story", "director"],
                format_func=lambda x: {
                    "story_bible": "📖 Story Bible",
                    "chapter": "📄 Single Chapter",
                    "full_story": "📚 Full Story",
                    "director": "🎬 Director Mode"
                }[x],
                key=f"pipeline_type_select_{project_name}_{render_id}"
            )
            
            # Show pipeline-specific options
            chapter_index = None
            if pipeline_type == "chapter":
                chapter_index = st.number_input(
                    "Chapter Index",
                    min_value=0,
                    max_value=99,
                    value=0,
                    key=f"pipeline_chapter_index_{project_name}_{render_id}"
                )
            
            # Start pipeline button
            if st.button("▶️ Start Pipeline", 
                        type="secondary",  # Less prominent than primary
                        use_container_width=True,
                        key=f"pipeline_quick_start_{project_name}_{render_id}"):
                # Increment counter on click
                st.session_state[f"pipeline_render_count_{project_name}"] += 1
                _start_pipeline_ui(project_name, str(render_id), pipeline_type, chapter_index)


def _start_pipeline_ui(
    project_name: str, 
    render_id: str, 
    pipeline_type: Optional[str] = None,
    chapter_index: Optional[int] = None
):
    """
    Start a pipeline from UI parameters.
    """
    try:
        # Get producer
        producer = get_producer(project_name)
        
        # Get pipeline controller
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        
        # Determine pipeline type if not specified
        if not pipeline_type:
            pipeline_type = st.session_state.get(
                f"pipeline_type_select_{project_name}_{render_id}", 
                "story_bible"
            )
        
        # Build pipeline arguments based on session state
        # Start with common args for all pipeline types
        common_args = {
            "idea": st.session_state.get("producer_seed_idea", "A thrilling adventure story"),
            "genre": st.session_state.get("project_genre", "Adventure"),
            "tone": st.session_state.get("project_tone", "Exciting"),
            "themes": st.session_state.get("project_themes", ""),
            "setting": st.session_state.get("project_setting", ""),
            "auto_memory": st.session_state.get("producer_auto_memory", True),
        }
        
        # Get pipeline-specific args
        if pipeline_type == "chapter":
            if chapter_index is None:
                chapter_index = st.session_state.get(
                    f"pipeline_chapter_index_{project_name}_{render_id}", 
                    0
                )
            pipeline_args = {
                **common_args,
                "run_continuity": st.session_state.get("producer_run_continuity", True),
                "run_editor": st.session_state.get("producer_run_editor", True),
                "max_chapters": st.session_state.get("producer_max_chapters", 10),
                "chapter_index": chapter_index,
            }
        elif pipeline_type in ["full_story", "director"]:
            pipeline_args = {
                **common_args,
                "run_continuity": st.session_state.get("producer_run_continuity", True),
                "run_editor": st.session_state.get("producer_run_editor", True),
                "max_chapters": st.session_state.get("producer_max_chapters", 10),
            }
        else:  # story_bible
            # Story bible only uses common args
            pipeline_args = common_args
        
        # Get the appropriate pipeline function with proper wrapper
        # Note: PipelineController passes controller and feedback_manager params
        # but Producer methods don't accept them, so we wrap to ignore them
        if pipeline_type == "story_bible":
            def pipeline_func(controller=None, feedback_manager=None, **kwargs):
                return producer.run_story_bible_pipeline(**kwargs)
            task_name = "Story Bible Generation"
            total_steps = 3
        elif pipeline_type == "chapter":
            def pipeline_func(controller=None, feedback_manager=None, **kwargs):
                return producer.run_chapter_pipeline(**kwargs)
            task_name = f"Chapter {chapter_index} Generation"
            total_steps = 5
        elif pipeline_type == "full_story":
            def pipeline_func(controller=None, feedback_manager=None, **kwargs):
                return producer.run_full_story_pipeline(**kwargs)
            task_name = "Full Story Generation"
            total_steps = pipeline_args["max_chapters"] + 3
        elif pipeline_type == "director":
            def pipeline_func(controller=None, feedback_manager=None, **kwargs):
                return producer.run_director_mode(**kwargs)
            task_name = "Director Mode"
            total_steps = 10
        else:
            st.error(f"Unknown pipeline type: {pipeline_type}")
            return
        
        # Start the pipeline
        success = pipeline_controller.start_pipeline(
            pipeline_func=pipeline_func,
            task_name=task_name,
            total_steps=total_steps,
            **pipeline_args
        )
        
        if success:
            st.success(f"✅ {task_name} started!")
            st.info("💡 Pipeline running in background - UI stays responsive!")
            # Clear any processed feedback
            if hasattr(pipeline_controller, 'feedback_manager'):
                pipeline_controller.feedback_manager.clear_processed()
            # Rerun once to show updated status
            st.rerun()
        else:
            st.error("❌ Could not start pipeline (already running?)")
            current_status = pipeline_controller.get_status()
            with st.expander("Show Status Details"):
                st.write(f"Current status: {current_status['status']}")
                st.write(f"Is running: {current_status['is_running']}")
                st.write(f"Is paused: {current_status['is_paused']}")
            
    except Exception as e:
        st.error(f"❌ Error starting pipeline")
        with st.expander("Show Error Details"):
            st.code(str(e))
            import traceback
            st.code(traceback.format_exc())


def render_pipeline_status_overview(project_name: str):
    """
    Render a compact pipeline status overview for the dashboard.
    """
    try:
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        status = pipeline_controller.get_status()
        
        # Status badge with color
        status_colors = {
            "idle": "#808080",
            "running": "#28a745",
            "paused": "#ffc107",
            "stopped": "#dc3545",
            "completed": "#007bff",
            "error": "#dc3545"
        }
        
        status_color = status_colors.get(status["status"], "#808080")
        
        # Create status HTML
        html = f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
            <div style="
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background-color: {status_color};
            "></div>
            <span>Pipeline: <strong>{status['status'].upper()}</strong></span>
        """
        
        if status["progress"]["percent_complete"] > 0:
            html += f"""
            <span style="margin-left: 20px; color: #666;">
                {status['progress']['percent_complete']:.1f}% - {status['progress']['current_step']}
            </span>
            """
        
        html += "</div>"
        
        st.markdown(html, unsafe_allow_html=True)
        
    except Exception as e:
        st.caption(f"Pipeline: Not initialized")