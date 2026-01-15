import streamlit as st

def render_intelligence_panel(producer):
    with st.expander("🧠 Project Intelligence Panel", expanded=True):

        # ======================================================
        # 1. Agent Message Stream
        # ======================================================
        st.subheader("📡 Agent Message Stream")

        messages = producer.intelligence_bus.messages[-100:]
        if not messages:
            st.write("No messages yet.")
        else:
            for msg in messages:
                agent = msg.get("agent", "system")
                msg_type = msg.get("type", "info")
                st.markdown(f"**{agent}** — *{msg_type}*")
                st.write(msg["content"])
                st.markdown("---")

        # ======================================================
        # 2. Human Feedback Injection
        # ======================================================
        st.subheader("🎤 Send Feedback to Agents")

        for agent_name in producer.agents.keys():
            st.markdown(f"### {agent_name}")

            feedback = st.text_area(
                f"Feedback for {agent_name}",
                key=f"fb_{agent_name}"
            )

            if st.button(f"Send to {agent_name}", key=f"send_{agent_name}"):
                producer.handle_feedback(agent_name, feedback)
                st.success("Feedback sent")

        # ======================================================
        # 3. Task Queue
        # ======================================================
        st.subheader("📋 Task Queue")

        tasks = producer.intelligence_bus.task_queue
        if not tasks:
            st.write("No tasks queued.")
        else:
            for task in tasks:
                st.json(task)
                st.markdown("---")

        # ======================================================
        # 4. Continuity Notes
        # ======================================================
        st.subheader("🔍 Continuity Notes")

        continuity = producer.intelligence_bus.continuity_notes
        if not continuity:
            st.write("No continuity notes yet.")
        else:
            for note in continuity:
                st.write(note)
                st.markdown("---")

        # ======================================================
        # 5. Canon Rules
        # ======================================================
        st.subheader("📜 Canon Rules")

        canon = producer.intelligence_bus.canon_rules
        if not canon:
            st.write("No canon rules yet.")
        else:
            for rule in canon:
                st.write(rule)
                st.markdown("---")

        # ======================================================
        # 6. Memory Events
        # ======================================================
        st.subheader("🧠 Memory Events")

        memory_events = producer.intelligence_bus.memory_events
        if not memory_events:
            st.write("No memory events yet.")
        else:
            for event in memory_events:
                st.json(event)
                st.markdown("---")

        # ======================================================
        # 7. Agent-to-Agent Messages
        # ======================================================
        st.subheader("🔗 Agent Conversations")

        agent_msgs = producer.intelligence_bus.agent_messages
        if not agent_msgs:
            st.write("No agent-to-agent messages yet.")
        else:
            for msg in agent_msgs:
                sender = msg.get("sender", "unknown")
                recipient = msg.get("recipient", "unknown")
                st.markdown(f"**{sender} → {recipient}**")
                st.write(msg.get("content", ""))
                st.markdown("---")
