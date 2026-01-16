"""
Intelligence Panel - displays EventBus and AuditLog messages.
"""

import streamlit as st


def render_intelligence_panel(producer):
    """
    Display agent messages from EventBus and AuditLog.
    """
    with st.expander("🧠 Project Intelligence Panel", expanded=True):

        # ======================================================
        # 1. Recent EventBus Messages (live)
        # ======================================================
        st.subheader("📡 Recent Agent Messages (Live)")

        recent_events = list(producer.event_bus.buffer)[-50:]
        
        if not recent_events:
            st.write("No recent messages.")
        else:
            for event in recent_events:
                sender = event.sender
                recipient = event.recipient
                msg_type = event.type
                
                st.markdown(f"**{sender} → {recipient}** — *{msg_type}*")
                st.write(event.payload)
                st.markdown("---")

        # ======================================================
        # 2. Human Feedback Injection
        # ======================================================
        st.subheader("🎤 Send Feedback to Agents")

        agent_names = [
            "plot_architect",
            "worldbuilder",
            "character_agent",
            "scene_generator",
            "continuity",
            "editor",
        ]

        for agent_name in agent_names:
            st.markdown(f"### {agent_name}")

            feedback = st.text_area(
                f"Feedback for {agent_name}",
                key=f"fb_{agent_name}"
            )

            if st.button(f"Send to {agent_name}", key=f"send_{agent_name}"):
                if feedback.strip():
                    producer.handle_feedback(agent_name, feedback.strip())
                    st.success(f"Feedback sent to {agent_name}")
                else:
                    st.info("Enter feedback text first")

        # ======================================================
        # 3. AuditLog Search (historical)
        # ======================================================
        st.subheader("🔍 Audit Log Search")

        search_type = st.selectbox(
            "Filter by event type",
            ["all", "agent_message", "user_feedback", "agent_log"],
            key="audit_search_type"
        )

        search_limit = st.number_input(
            "Max results",
            min_value=10,
            max_value=1000,
            value=50,
            key="audit_search_limit"
        )

        if st.button("Search Audit Log"):
            event_type = None if search_type == "all" else search_type
            
            results = producer.audit_log.search(
                event_type=event_type,
                limit=search_limit
            )
            
            if not results:
                st.write("No results found.")
            else:
                st.write(f"Found {len(results)} entries:")
                for entry in results:
                    st.markdown(f"**{entry.sender} → {entry.recipient}** — *{entry.event_type}* ({entry.timestamp})")
                    st.json(entry.payload)
                    st.markdown("---")