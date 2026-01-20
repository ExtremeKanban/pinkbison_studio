"""
Multi-Project Orchestrator UI Panel
"""

import streamlit as st
import subprocess
import threading
import time
from pathlib import Path


def render_multi_orchestrator_panel(project_name: str):
    """Render multi-project orchestrator controls."""
    
    with st.expander("🚀 Multi-Project Orchestrator", expanded=False):
        st.markdown("""
        ### Single Orchestrator for All Projects
        
        The Multi-Project Orchestrator runs in the background and manages:
        - **Multiple projects simultaneously**
        - **Automatic task processing**
        - **Project isolation with shared resources**
        - **Round-robin fair scheduling**
        """)
        
        # Show current projects
        st.subheader("📁 Available Projects")
        
        base_dir = Path("project_state")
        projects = []
        
        if base_dir.exists():
            for item in base_dir.iterdir():
                if item.is_dir():
                    state_file = item / "state.json"
                    if state_file.exists():
                        projects.append(item.name)
        
        if projects:
            st.write(f"Found {len(projects)} projects:")
            for project in projects:
                col1, col2 = st.columns([3, 1])
                with col1:
                    status = "🟢" if project == project_name else "⚪"
                    st.write(f"{status} {project}")
                with col2:
                    if st.button("Select", key=f"select_{project}"):
                        st.session_state["current_project"] = project
                        st.rerun()
        else:
            st.info("No projects found. Create a project using the sidebar.")
        
        # Orchestrator controls
        st.subheader("🎛️ Orchestrator Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Orchestrator", type="primary", use_container_width=True):
                st.info("Starting orchestrator in background...")
                st.code("python run_multi_orchestrator.py start", language="bash")
                
                # In a real implementation, this would start a subprocess
                # For now, show instructions
                st.markdown("""
                **Run in terminal:**
                ```bash
                python run_multi_orchestrator.py start
                ```
                """)
        
        with col2:
            if st.button("📋 List Projects", use_container_width=True):
                st.code("python run_multi_orchestrator.py list", language="bash")
                st.markdown("""
                **Run in terminal:**
                ```bash
                python run_multi_orchestrator.py list
                ```
                """)
        
        with col3:
            if st.button("📖 View Documentation", use_container_width=True):
                st.markdown("""
                ### How it Works
                
                1. **Single Process**: One orchestrator manages all projects
                2. **Async Loop**: Non-blocking I/O for efficiency
                3. **Fair Scheduling**: Round-robin between projects
                4. **Resource Isolation**: Each project has its own EventBus
                5. **Automatic Discovery**: Finds projects in `project_state/`
                
                ### Benefits
                - No need to start/stop orchestrator per project
                - Efficient resource usage
                - Centralized monitoring
                - Graceful error handling
                
                ### Usage
                ```bash
                # Start with all projects
                python run_multi_orchestrator.py start
                
                # Start with specific projects
                python run_multi_orchestrator.py start --projects my_project another_project
                
                # List available projects
                python run_multi_orchestrator.py list
                ```
                """)
        
        # Quick start guide
        with st.expander("🚀 Quick Start Guide", expanded=False):
            st.markdown("""
            1. **Create a project** using the sidebar
            2. **Generate content** (plot, world, characters, chapters)
            3. **Open a new terminal tab**
            4. **Run the orchestrator:**
               ```bash
               python run_multi_orchestrator.py start
               ```
            5. **The orchestrator will:**
               - Process continuity critiques
               - Generate canon rules
               - Manage task queues
               - Update all projects simultaneously
            
            **Keep the UI open** to monitor progress in the Intelligence Panel!
            """)
        
        # Status information
        st.subheader("📊 Status")
        
        if projects:
            st.success(f"✅ System ready! {len(projects)} projects available.")
            st.info("""
            **Next Steps:**
            1. Open a new terminal tab
            2. Run: `python run_multi_orchestrator.py start`
            3. Return here to monitor activity
            """)
        else:
            st.warning("⚠️ No projects found. Create at least one project first.")