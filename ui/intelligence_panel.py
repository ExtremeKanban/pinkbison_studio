"""
Enhanced Intelligence Panel with real-time components.
Integrates live event stream, feedback injection, and pipeline controls.
"""

import streamlit as st
from core.registry import REGISTRY

# Import new real-time components
from ui.live_event_panel import render_live_event_panel, render_pipeline_status_card
from ui.pipeline_controls_ui import render_pipeline_controls, render_pipeline_status_overview
from ui.feedback_injector_ui import render_feedback_injector


def render_intelligence_panel(project_name: str):
    """
    Main intelligence panel that integrates all real-time components.
    """
    with st.expander("🧠 Project Intelligence Panel", expanded=True):
        
        # Tab layout for different intelligence views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard",
            "📡 Live Events", 
            "🎯 Feedback",
            "📋 Audit Log"
        ])
        
        with tab1:
            render_intelligence_dashboard(project_name)
        
        with tab2:
            render_live_event_panel(project_name)
        
        with tab3:
            render_feedback_tab(project_name)
        
        with tab4:
            render_audit_log_tab(project_name)


def render_intelligence_dashboard(project_name: str):
    """
    Render intelligence dashboard with overview and controls.
    """
    st.subheader("📊 Intelligence Dashboard")
    
    # Pipeline status card
    render_pipeline_status_card(project_name)
    
    st.markdown("---")
    
    # Pipeline controls - REMOVE THIS LINE to avoid duplicate
    # render_pipeline_controls(project_name, context="intelligence")
    
    st.markdown("---")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
            stats = pipeline_controller.get_status()
            st.metric("Pipeline Status", stats["status"].title())
        except:
            st.metric("Pipeline Status", "Idle")
    
    with col2:
        try:
            event_bus = REGISTRY.get_event_bus(project_name)
            event_count = len(list(event_bus.buffer))
            st.metric("Recent Events", event_count)
        except:
            st.metric("Recent Events", 0)
    
    with col3:
        try:
            audit_log = REGISTRY.get_audit_log(project_name)
            # Count entries (approximate)
            import json
            count = 0
            try:
                with open(audit_log.log_path, 'r') as f:
                    for _ in f:
                        count += 1
                st.metric("Audit Entries", f"{count:,}")
            except:
                st.metric("Audit Entries", 0)
        except:
            st.metric("Audit Entries", 0)
    
    st.markdown("---")
    
    # Feedback injector (compact version)
    with st.expander("💬 Quick Feedback", expanded=False):
        render_feedback_injector_compact(project_name)


def render_feedback_tab(project_name: str):
    """
    Render full feedback management tab.
    """
    st.subheader("🎯 Feedback Management")
    
    # Full feedback injector
    render_feedback_injector(project_name)
    
    st.markdown("---")
    
    # Feedback statistics
    try:
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        stats = pipeline_controller.feedback_manager.get_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Feedback", stats["total"])
        
        with col2:
            st.metric("Unprocessed", stats["unprocessed"])
        
        with col3:
            st.metric("Processed", stats["processed"])
        
        # Priority distribution
        if stats["by_priority"]:
            st.markdown("#### Priority Distribution")
            for priority, count in stats["by_priority"].items():
                if count > 0:
                    # Progress bars don't need keys usually, but add one to be safe
                    st.progress(
                        count / max(stats["total"], 1),
                        text=f"{priority}: {count}"
                    )
        
    except Exception as e:
        st.info("Feedback manager not initialized")


def render_audit_log_tab(project_name: str):
    """
    Render audit log search and view tab.
    """
    st.subheader("📋 Audit Log Search")
    
    # Get audit log
    audit_log = REGISTRY.get_audit_log(project_name)
    
    # Search filters
    col1, col2 = st.columns(2)
    
    with col1:
        event_type = st.selectbox(
            "Event Type",
            options=["all", "agent_message", "user_feedback", "agent_log", 
                    "pipeline_start", "pipeline_complete", "pipeline_error"],
            key=f"audit_search_type_{project_name}"
        )
    
    with col2:
        search_limit = st.number_input(
            "Max Results",
            min_value=10,
            max_value=1000,
            value=100,
            key=f"audit_search_limit_{project_name}"
        )
    
    # Sender filter
    sender_filter = st.text_input(
        "Filter by Sender (optional)",
        placeholder="e.g., plot_architect, user",
        key=f"audit_sender_filter_{project_name}"
    )
    
    # Search button
    if st.button("🔍 Search Audit Log", type="primary", key=f"audit_search_btn_{project_name}"):
        event_type_param = None if event_type == "all" else event_type
        
        results = audit_log.search(
            event_type=event_type_param,
            limit=search_limit
        )
        
        # Apply sender filter if specified
        if sender_filter:
            results = [r for r in results if sender_filter.lower() in r.sender.lower()]
        
        # Display results
        if not results:
            st.info("No audit log entries found.")
        else:
            st.write(f"Found {len(results)} entries:")
            
            for idx, entry in enumerate(results):
                with st.expander(
                    f"{entry.sender} → {entry.recipient} - {entry.event_type} ({entry.timestamp})",
                    expanded=(idx < 3)
                ):
                    st.json(entry.payload)


def render_feedback_injector_compact(project_name: str):
    """
    Compact version of feedback injector for dashboard.
    """
    try:
        pipeline_controller = REGISTRY.get_pipeline_controller(project_name)
        feedback_manager = pipeline_controller.feedback_manager
        
        # Quick target selection
        target = st.selectbox(
            "To",
            options=["ALL", "plot_architect", "worldbuilder", "character_agent"],
            key=f"quick_feedback_target_{project_name}"
        )
        
        # Quick message
        message = st.text_area(
            "Message",
            placeholder="Quick feedback...",
            height=80,
            key=f"quick_feedback_message_{project_name}"
        )
        
        if st.button("💬 Send", use_container_width=True, key=f"quick_feedback_btn_{project_name}"):
            if message.strip():
                from core.feedback_manager import FeedbackType, FeedbackPriority
                
                feedback_manager.add_feedback(
                    target_agent=target,
                    feedback_type=FeedbackType.GUIDANCE,
                    content=message.strip(),
                    priority=FeedbackPriority.NORMAL,
                    source="user"
                )
                
                st.success("Feedback sent!")
                st.rerun()
            else:
                st.warning("Enter a message")
                
    except:
        st.info("Start pipeline to send feedback")