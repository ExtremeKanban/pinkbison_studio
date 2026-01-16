import requests
from agents.memory_extractor import MemoryExtractor
from memory_store import MemoryStore
from models.heavy_model import generate_with_heavy_model
from agents.base_agent import AgentBase
from core.event_bus import EventBus
from core.audit_log import AuditLog


class CharacterAgent(AgentBase):
    def __init__(self, project_name, event_bus: EventBus, audit_log: AuditLog,
                 fast_model_url, model_mode):
        super().__init__("character_agent", project_name, event_bus, audit_log,
                        fast_model_url, model_mode)
        self.extractor = MemoryExtractor(fast_model_url)
        self.memory = MemoryStore(project_name)

    def run(self, outline: str, world_notes: str, auto_memory: bool = True) -> str:
        """
        Generate character bios and arcs based on the outline and world.
        """
        
        # Check for feedback from EventBus
        recent_messages = self.get_recent_messages(limit=5)
        feedback_texts = [
            msg.get('content', '') 
            for msg in recent_messages 
            if msg.get('type') == 'feedback'
        ]
        
        memory_context = self.memory.search("characters relationships arcs motivations", k=10)
        memory_text = "\n".join(memory_context) if memory_context else "None yet."

        prompt = f"""
        You are a Character Architect for a long-form narrative project.

        Plot outline:
        \"\"\"{outline}\"\"\"

        World notes:
        \"\"\"{world_notes}\"\"\"

        Existing character-related memory:
        \"\"\"{memory_text}\"\"\"

        Task:
        - Identify the main and key supporting characters.
        - For each important character, provide:
          - name
          - role in the story
          - core motivation
          - strengths and flaws
          - internal conflict
          - external conflict
          - relationships with other key characters
          - transformation arc across the story

        Output:
        - Use a clear heading per character.
        - Use bullet points for attributes.
        - Ensure arcs align with the outline and world.
        """
        
        if feedback_texts:
            prompt += f"\n\nRecent feedback:\n" + "\n".join(feedback_texts)

        if self.model_mode == "high_quality":
            characters_doc = generate_with_heavy_model(prompt)
        else:
            payload = {
                "model": "Qwen/Qwen2.5-3B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8
            }
            response = requests.post(self.fast_model_url, json=payload)
            characters_doc = response.json()["choices"][0]["message"]["content"]

        if auto_memory:
            facts = self.extractor.extract(characters_doc)
            for fact in facts:
                self.memory.add(fact)

        self.send_message(
            recipient="scene_generator",
            msg_type="CHARACTERS_READY",
            payload={"characters": characters_doc}
        )

        return characters_doc