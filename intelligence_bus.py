import time
from datetime import datetime   

class IntelligenceBus:
    def __init__(self, project_name: str):
        self.project_name = project_name

        # Core message structures
        self.messages = []            # chronological log of everything
        self.agent_feedback = {}      # {agent_name: [feedback entries]}
        self.continuity_notes = []
        self.canon_rules = []
        self.task_queue = []
        self.memory_events = []
        self.agent_messages = []      # raw agent-to-agent or agent-to-producer messages

        # Unique message ID counter
        self._msg_counter = 0

    def _next_id(self):          
        self._msg_counter += 1
        return self._msg_counter

    def add_agent_message(self, sender, recipient, msg_type, payload):
        msg = {
            "id": self._next_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "sender": sender,
            "recipient": recipient,
            "type": msg_type,
            "payload": payload,
        }
        self.messages.append(msg)

    def get_messages_for(self, agent_name, since_id=None):
        msgs = [m for m in self.messages if m["recipient"] in (agent_name, "ALL")]
        if since_id is not None:
            msgs = [m for m in msgs if m["id"] > since_id]
        return msgs

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
