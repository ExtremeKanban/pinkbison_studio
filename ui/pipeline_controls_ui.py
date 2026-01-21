"""
Pipeline control UI with start/pause/resume/stop buttons.
"""

import streamlit as st
from typing import Optional, Dict, Any

from core.registry import REGISTRY
from ui.common import get_producer


def render_pipeline_controls(project_name: str):
    """
    Render pipeline control buttons and status.
    """
    import time
    
    # Use timestamp to make keys unique each time it's rendered
    timestamp = str(int(time.time() * 1000))[-6:]  # Last 6 digits of timestamp
    
    with st.expander("🎮 Pipeline Controls", expanded=True):
        
        # Get pipeline controller
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        status = pipeline_controller.get_status()
        
        # Current status display
        st.markdown(f"**Current Status:** `{status['status']}`")
        
        if status["progress"]["percent_complete"] > 0:
            st.progress(
                status["progress"]["percent_complete"] / 100,
                text=status["progress"]["current_step"]
            )
        
        # Control buttons in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("▶️ Start", 
                        disabled=status["is_running"] or status["is_paused"],
                        use_container_width=True,
                        key=f"pipeline_start_{project_name}_{timestamp}"):  # ADD timestamp
                _start_pipeline_ui(project_name)
        
        with col2:
            if st.button("⏸️ Pause",
                        disabled=not status["is_running"],
                        use_container_width=True,
                        key=f"pipeline_pause_{project_name}_{timestamp}"):  # ADD timestamp
                if pipeline_controller.pause():
                    st.success("Pipeline paused")
                    st.rerun()
                else:
                    st.error("Could not pause pipeline")
        
        with col3:
            if st.button("⏯️ Resume",
                        disabled=not status["is_paused"],
                        use_container_width=True,
                        key=f"pipeline_resume_{project_name}_{timestamp}"):  # ADD timestamp
                if pipeline_controller.resume():
                    st.success("Pipeline resumed")
                    st.rerun()
                else:
                    st.error("Could not resume pipeline")
        
        with col4:
            if st.button("⏹️ Stop",
                        disabled=not (status["is_running"] or status["is_paused"]),
                        use_container_width=True,
                        type="secondary",
                        key=f"pipeline_stop_{project_name}_{timestamp}"):  # ADD timestamp
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
                key=f"pipeline_type_select_{project_name}_{timestamp}"  # ADD timestamp
            )
            
            # Show pipeline-specific options
            if pipeline_type == "chapter":
                chapter_index = st.number_input(
                    "Chapter Index",
                    min_value=0,
                    max_value=99,
                    value=0,
                    key=f"pipeline_chapter_index_{project_name}_{timestamp}"  # ADD timestamp
                )
            
            # Quick start button
            if st.button("🚀 Quick Start", 
                        type="primary", 
                        use_container_width=True,
                        key=f"pipeline_quick_start_{project_name}_{timestamp}"):  # ADD timestamp
                _start_pipeline_ui(project_name, pipeline_type)


def _start_pipeline_ui(project_name: str, context: str, pipeline_type: Optional[str] = None):
    """
    Start a pipeline from UI parameters.
    
    Args:
        project_name: Name of the project
        context: Context identifier
        pipeline_type: Optional pipeline type
    """
    try:
        # Get producer
        producer = get_producer(project_name)
        
        # Get pipeline controller
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        
        # Determine pipeline type if not specified
        if not pipeline_type:
            pipeline_type = st.session_state.get(f"pipeline_type_select_{project_name}_{context}", "story_bible")  # UPDATED key
        
        # Build pipeline arguments based on type
        pipeline_args = {
            "idea": st.session_state.get("producer_seed_idea", ""),
            "genre": st.session_state.get("project_genre", ""),
            "tone": st.session_state.get("project_tone", ""),
            "themes": st.session_state.get("project_themes", ""),
            "setting": st.session_state.get("project_setting", ""),
            "auto_memory": st.session_state.get("producer_auto_memory", True),
            "run_continuity": st.session_state.get("producer_run_continuity", True),
            "run_editor": st.session_state.get("producer_run_editor", True),
            "max_chapters": st.session_state.get("producer_max_chapters", 10),
        }
        
        # Add type-specific args
        if pipeline_type == "chapter":
            pipeline_args["chapter_index"] = st.session_state.get(
                f"pipeline_chapter_index_{project_name}_{context}", 0  # UPDATED key
            )
        
        # Get the appropriate async pipeline function
        if pipeline_type == "story_bible":
            pipeline_func = lambda **kwargs: producer.run_story_bible_pipeline(**kwargs)
        elif pipeline_type == "chapter":
            pipeline_func = lambda **kwargs: producer.run_chapter_pipeline(**kwargs)
        elif pipeline_type == "full_story":
            pipeline_func = lambda **kwargs: producer.run_full_story_pipeline(**kwargs)
        elif pipeline_type == "director":
            pipeline_func = lambda **kwargs: producer.run_director_mode(**kwargs)
        else:
            st.error(f"Unknown pipeline type: {pipeline_type}")
            return
        
        # Start the pipeline
        success = pipeline_controller.start_pipeline(
            pipeline_func=pipeline_func,
            task_name=f"{pipeline_type}_{project_name}",
            total_steps=10,
            **pipeline_args
        )
        
        if success:
            st.success(f"{pipeline_type.replace('_', ' ').title()} pipeline started!")
            pipeline_controller.feedback_manager.clear_processed()
            st.rerun()
        else:
            st.error("Could not start pipeline (already running?)")
        
    except Exception as e:
        st.error(f"Failed to start pipeline: {str(e)}")
        import traceback
        with st.expander("Error details"):
            st.code(traceback.format_exc())


def render_pipeline_status_overview(project_name: str):
    """
    Render a compact pipeline status overview.
    """
    try:
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        status = pipeline_controller.get_status()
        
        # Status badge with color
        status_colors = {
            "idle": "gray",
            "running": "green",
            "paused": "yellow",
            "stopped": "red",
            "completed": "blue",
            "error": "red"
        }
        
        status_color = status_colors.get(status["status"], "gray")
        
        # Create status HTML
        html = f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background-color: {status_color};
            "></div>
            <span>Pipeline: <strong>{status['status']}</strong></span>
        """
        
        if status["progress"]["percent_complete"] > 0:
            html += f"""
            <span style="margin-left: 20px; color: #666;">
                {status['progress']['percent_complete']:.1f}%
            </span>
            """
        
        html += "</div>"
        
        st.markdown(html, unsafe_allow_html=True)
        
    except:
        st.caption("Pipeline: Not initialized")