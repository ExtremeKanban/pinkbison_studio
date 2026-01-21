"""
Real-time output display - updates via EventBus subscription
"""

import streamlit as st
from datetime import datetime
from core.registry import REGISTRY


def render_realtime_output(project_name: str):
    """Display outputs via AuditLog (persistent)"""
    
    if f"partial_{project_name}" not in st.session_state:
        st.session_state[f"partial_{project_name}"] = {
            "outline": None, "world": None, "characters": None
        }
    
    partial = st.session_state[f"partial_{project_name}"]
    
    # Read from AuditLog instead of EventBus buffer
    audit_log = REGISTRY.get_audit_log(project_name)
    recent = audit_log.search(event_type="partial_result", limit=50)
    
    st.write(f"DEBUG: Found {len(recent)} partial_result events in audit log")
    
    updated = False
    for entry in recent:
        step = entry.payload.get("step")
        content = entry.payload.get("content")
        
        if step in ["outline", "world", "characters"] and content:
            if partial.get(step) != content:
                partial[step] = content
                updated = True
                st.write(f"DEBUG: Updated {step} from audit log")
    
    st.write(f"DEBUG: State = outline:{bool(partial.get('outline'))}, world:{bool(partial.get('world'))}, characters:{bool(partial.get('characters'))}")
    
    if updated:
        st.rerun()
    
    if not any(partial.values()):
        st.info("💡 Run a pipeline above to see outputs here")
        return
    
    st.subheader("📋 Story Bible - Live")
    
    if partial.get("outline"):
        with st.expander("📝 Outline", expanded=True):
            st.text_area("", partial["outline"], height=200, key="o", disabled=True, label_visibility="collapsed")
    
    if partial.get("world"):
        with st.expander("🌍 World", expanded=True):
            st.text_area("", partial["world"], height=200, key="w", disabled=True, label_visibility="collapsed")
    
    if partial.get("characters"):
        with st.expander("👥 Characters", expanded=True):
            st.text_area("", partial["characters"], height=200, key="c", disabled=True, label_visibility="collapsed")

def clear_partial_results(project_name: str):
    """Clear when starting new pipeline"""
    st.session_state[f"partial_{project_name}"] = {
        "outline": None,
        "world": None,
        "characters": None
    }