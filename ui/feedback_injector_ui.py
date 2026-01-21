"""
UI for injecting feedback during pipeline execution.
"""

import streamlit as st
from typing import List, Dict, Any

from core.registry import REGISTRY
from core.feedback_manager import FeedbackType, FeedbackPriority


def render_feedback_injector(project_name: str):
    """
    Render feedback injection interface.
    """
    with st.expander("🎯 Inject Feedback", expanded=True):
        
        # Get pipeline controller
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        feedback_manager = pipeline_controller.feedback_manager
        
        # Current status
        status = pipeline_controller.get_status()
        
        if not status["is_running"] and not status["is_paused"]:
            st.info("Start a pipeline to inject feedback")
            return
        
        # Target agent selection
        col1, col2 = st.columns(2)
        
        with col1:
            target_agent = st.selectbox(
                "Target Agent",
                options=[
                    "ALL",
                    "plot_architect",
                    "worldbuilder",
                    "character_agent",
                    "scene_generator",
                    "continuity_agent",
                    "editor_agent",
                    "creative_director",
                    "producer"
                ],
                format_func=lambda x: {
                    "ALL": "🎯 All Agents (Broadcast)",
                    "plot_architect": "📝 Plot Architect",
                    "worldbuilder": "🌍 Worldbuilder",
                    "character_agent": "👤 Character Agent",
                    "scene_generator": "🎬 Scene Generator",
                    "continuity_agent": "🔍 Continuity Agent",
                    "editor_agent": "✏️ Editor Agent",
                    "creative_director": "🎨 Creative Director",
                    "producer": "🎬 Producer"
                }[x],
                key="feedback_target"
            )
        
        with col2:
            feedback_type = st.selectbox(
                "Feedback Type",
                options=list(FeedbackType),
                format_func=lambda x: x.value.title(),
                key="feedback_type"
            )
        
        # Priority selection
        priority = st.select_slider(
            "Priority",
            options=list(FeedbackPriority),
            value=FeedbackPriority.NORMAL,
            format_func=lambda x: f"{x.name} ({x.value})",
            key="feedback_priority"
        )
        
        # Feedback content
        feedback_content = st.text_area(
            "Feedback Content",
            placeholder="Enter specific, actionable feedback...",
            height=150,
            key="feedback_content"
        )
        
        # Template buttons for common feedback
        st.markdown("**Quick Templates:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("More detail", use_container_width=True):
                st.session_state.feedback_content = "Please add more detail and description here."
        
        with col2:
            if st.button("Simplify", use_container_width=True):
                st.session_state.feedback_content = "This is too complex. Please simplify and make it more accessible."
        
        with col3:
            if st.button("Check canon", use_container_width=True):
                st.session_state.feedback_content = "Please check this against established canon rules and ensure consistency."
        
        # Inject button
        if st.button("💬 Inject Feedback", type="primary", use_container_width=True):
            if feedback_content.strip():
                # Add feedback
                feedback_id = feedback_manager.add_feedback(
                    target_agent=target_agent,
                    feedback_type=feedback_type,
                    content=feedback_content.strip(),
                    priority=priority,
                    source="user"
                )
                
                # Also publish to EventBus for immediate visibility
                event_bus = REGISTRY.get_event_bus(project_name)
                event_bus.publish(
                    sender="user",
                    recipient=target_agent,
                    event_type=f"user_feedback_{feedback_type.value}",
                    payload={
                        "content": feedback_content.strip(),
                        "priority": priority.value,
                        "feedback_id": feedback_id
                    }
                )
                
                st.success(f"Feedback injected for {target_agent}")
                
                # Clear the text area
                st.session_state.feedback_content = ""
                
                # Trigger UI update
                st.rerun()
            else:
                st.warning("Please enter feedback content")
        
        # Show pending feedback
        st.markdown("---")
        st.markdown("### 📬 Pending Feedback")
        
        stats = feedback_manager.get_stats()
        if stats["unprocessed"] > 0:
            # Show feedback by agent
            agents = ["ALL", "plot_architect", "worldbuilder", "character_agent",
                     "scene_generator", "continuity_agent", "editor_agent",
                     "creative_director", "producer"]
            
            for agent in agents:
                feedback = feedback_manager.get_feedback_for_agent(
                    agent_name=agent,
                    include_broadcast=False,
                    unprocessed_only=True
                )
                
                if feedback:
                    with st.expander(f"{agent} ({len(feedback)})", expanded=False):
                        for msg in feedback:
                            render_feedback_message(msg, feedback_manager)
            
            # Clear all button
            if st.button("🗑️ Clear All Processed", type="secondary"):
                cleared = feedback_manager.clear_processed()
                st.success(f"Cleared {cleared} processed messages")
                st.rerun()
        else:
            st.info("No pending feedback")


def render_feedback_message(feedback, feedback_manager):
    """
    Render a single feedback message.
    """
    # Priority colors
    priority_colors = {
        1: "#666666",  # LOW
        2: "#44aa44",  # NORMAL
        3: "#ffaa44",  # HIGH
        4: "#ff4444",  # CRITICAL
        5: "#ff0000",  # URGENT
    }
    
    # Create message HTML
    html = f"""
    <div style="
        border-left: 4px solid {priority_colors.get(feedback.priority.value, '#666666')};
        padding: 10px;
        margin: 5px 0;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>{feedback.feedback_type.value.title()}</strong>
                <span style="color: #888; font-size: 0.9em; margin-left: 10px;">
                    Priority: {feedback.priority.name}
                </span>
            </div>
            <div style="color: #aaa; font-size: 0.8em;">
                {feedback.created_at[11:19]}  <!-- Show time only -->
            </div>
        </div>
        <div style="margin-top: 8px;">
            {feedback.content}
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Mark as processed button
    if st.button("✅ Mark Processed", key=f"mark_processed_{feedback.id}"):
        feedback_manager.mark_as_processed(feedback.id)
        st.rerun()