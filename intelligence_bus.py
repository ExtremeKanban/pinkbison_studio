import time

class IntelligenceBus:
    def __init__(self):
        self.messages = []          # chronological log of everything
        self.agent_feedback = {}    # {agent_name: [feedback entries]}
        self.continuity_notes = []
        self.canon_rules = []
        self.task_queue = []
        self.memory_events = []
        self.agent_messages = []    # raw agent-to-agent or agent-to-producer messages

    def log(self, entry_type, content, agent=None):
        self.messages.append({
            "type": entry_type,
            "content": content,
            "agent": agent,
            "timestamp": time.time()
        })

    def add_feedback(self, agent_name, text):
        if agent_name not in self.agent_feedback:
            self.agent_feedback[agent_name] = []
        self.agent_feedback[agent_name].append(text)
        self.log("human_feedback", text, agent=agent_name)
