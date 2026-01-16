import requests
from agents.memory_extractor import MemoryExtractor
from memory_store import MemoryStore
from models.heavy_model import generate_with_heavy_model
from agents.base_agent import AgentBase
from core.event_bus import EventBus
from core.audit_log import AuditLog


class PlotArchitect(AgentBase):
    def __init__(self, project_name, event_bus: EventBus, audit_log: AuditLog,
                 fast_model_url, model_mode):
        super().__init__("plot_architect", project_name, event_bus, audit_log,
                        fast_model_url, model_mode)
        self.extractor = MemoryExtractor(fast_model_url)
        self.memory = MemoryStore(project_name)

    def run(self, idea: str, genre: str, tone: str, themes: str, 
            setting: str, auto_memory: bool = False) -> str:
        """Expand a seed idea into a structured 3-act outline using project context."""
        
        # Check for feedback from EventBus
        recent_messages = self.get_recent_messages(limit=5)
        feedback_texts = [
            msg.get('content', '') 
            for msg in recent_messages 
            if msg.get('type') == 'feedback'
        ]
        
        prompt = f"""
        You are a Plot Architect.

        Use the following project context:
        - Genre: {genre}
        - Tone: {tone}
        - Themes: {themes}
        - Setting: {setting}

        Expand the following idea into a detailed 3-act outline.

        Idea:
        \"\"\"{idea}\"\"\"

        Requirements:
        - Provide Act I, Act II, Act III
        - Include major beats
        - Identify key characters
        - Identify central conflict
        - Provide 1-2 twist options
        - Keep it clear and structured with headings for each act.
        """
        
        if feedback_texts:
            prompt += f"\n\nRecent feedback:\n" + "\n".join(feedback_texts)

        # Model selection
        if self.model_mode == "high_quality":
            outline = generate_with_heavy_model(prompt)
        else:
            payload = {
                "model": "Qwen/Qwen2.5-3B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8
            }
            response = requests.post(self.fast_model_url, json=payload)
            outline = response.json()["choices"][0]["message"]["content"]

        if auto_memory:
            facts = self.extractor.extract(outline)
            for fact in facts:
                self.memory.add(fact)

        self.send_message(
            recipient="worldbuilder",
            msg_type="OUTLINE_READY",
            payload={"outline": outline}
        )

        return outline