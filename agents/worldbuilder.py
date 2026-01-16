import requests
from agents.memory_extractor import MemoryExtractor
from memory_store import MemoryStore
from models.heavy_model import generate_with_heavy_model
from intelligence_bus import IntelligenceBus
from agents.base_agent import AgentBase

class WorldbuilderAgent(AgentBase):
    def __init__(self, project_name, intelligence_bus, fast_model_url, model_mode):
        super().__init__("worldbuilder", project_name, intelligence_bus, fast_model_url, model_mode)
        self.extractor = MemoryExtractor(fast_model_url)
        self.memory = MemoryStore(project_name)


    def receive_feedback(self, text):
        self.feedback_inbox.append(text)


    def run(
        self,
        outline: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = True
    ) -> str:
        """
        Expand the plot outline into a rich world: geography, factions, cosmology, systems, history.
        """
        if self.feedback_inbox:
            # Inject feedback into the context 
            context = {}
            context["human_feedback"] = self.feedback_inbox.copy()
            self.feedback_inbox.clear()
        else:
            context = {}
            
        # Retrieve any existing world-related memory for context
        memory_context = self.memory.search("world geography factions cosmology history rules", k=10)
        memory_text = "\n".join(memory_context) if memory_context else "None yet."

        prompt = f"""
        You are a Worldbuilder for a long-form narrative project.

        Project context:
        - Genre: {genre}
        - Tone: {tone}
        - Themes: {themes}
        - Setting: {setting}

        Existing plot outline:
        \"\"\"{outline}\"\"\"

        Existing world memory (may be empty or partial):
        \"\"\"{memory_text}\"\"\"

        Task:
        - Develop a coherent world that supports the plot.
        - Cover at least:
          - geography and key locations
          - factions, cultures, and power structures
          - technology or magic systems (if any)
          - religions, philosophies, or belief systems
          - history and major past events that shape the present
          - social norms and taboos
          - any constraints or laws of reality that matter

        Output:
        - Use clear headings and subheadings.
        - Be concrete and specific, not vague.
        - Ensure the world logically supports the outline.
        """

        # --- Model selection ---
        if self.model_mode == "high_quality":
            # Use heavy local 7B model
            world_doc = generate_with_heavy_model(prompt)
        else:
            # Use fast model via HTTP
            payload = {
                "model": "Qwen/Qwen2.5-3B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8
            }
            response = requests.post(self.fast_model_url, json=payload)
            world_doc = response.json()["choices"][0]["message"]["content"]


        if auto_memory:
            facts = self.extractor.extract(world_doc)
            for fact in facts:
                self.memory.add(fact)

        self.send_message(
            recipient="character_agent",
            msg_type="WORLD_READY",
            payload={"world": world_doc}
        )

        return world_doc
