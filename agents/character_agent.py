import requests
from agents.memory_extractor import MemoryExtractor
from memory_store import MemoryStore
from models.heavy_model import generate_with_heavy_model
from agents.base_agent import AgentBase


class CharacterAgent(AgentBase):
    def __init__(self, project_name, intelligence_bus, fast_model_url, model_mode):
        super().__init__("character_agent", project_name, intelligence_bus, fast_model_url, model_mode)
        self.extractor = MemoryExtractor(fast_model_url)
        self.memory = MemoryStore(project_name)

    def receive_feedback(self, text):
        self.feedback_inbox.append(text)

    def run(
        self,
        outline: str,
        world_notes: str,
        auto_memory: bool = True
    ) -> str:
        """
        Generate character bios and arcs based on the outline and world.
        """
        if self.feedback_inbox:
            context = {"human_feedback": self.feedback_inbox.copy()}
            self.feedback_inbox.clear()
        else:
            context = {}

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

        return characters_doc
