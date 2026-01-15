# agents/base_agent.py

class AgentBase:
    """
    Shared base class for all agents.
    Provides:
    - project_name
    - model_mode
    - fast_model_url
    - intelligence_bus (injected by ProducerAgent)
    - feedback inbox
    - standard logging helpers
    """

    def __init__(self, name, project_name, intelligence_bus, fast_model_url, model_mode):
        self.name = name
        self.project_name = project_name
        self.intelligence_bus = intelligence_bus
        self.fast_model_url = fast_model_url
        self.model_mode = model_mode
        self.feedback_inbox = []

    # -----------------------------
    # Feedback
    # -----------------------------
    def receive_feedback(self, text):
        self.feedback_inbox.append(text)

    def consume_feedback(self):
        fb = self.feedback_inbox[:]
        self.feedback_inbox.clear()
        return fb

    # -----------------------------
    # Logging
    # -----------------------------
    def log(self, content, type="info"):
        if self.intelligence_bus:
            self.intelligence_bus.add_message(self.name, content, type)

    # -----------------------------
    # Agent-to-agent messaging (Phase 7)
    # -----------------------------
    def send_message(self, recipient, msg_type, payload):
        if self.intelligence_bus:
            self.intelligence_bus.add_agent_message(
                sender=self.name,
                recipient=recipient,
                msg_type=msg_type,
                payload=payload,
            )
