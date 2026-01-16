import requests
from agents.memory_extractor import MemoryExtractor
from memory_store import MemoryStore
from models.heavy_model import generate_with_heavy_model
from intelligence_bus import IntelligenceBus
from agents.base_agent import AgentBase

class SceneGeneratorAgent(AgentBase):
    def __init__(self, project_name, intelligence_bus, fast_model_url, model_mode):
        super().__init__("scene_generator", project_name, intelligence_bus, fast_model_url, model_mode)
        self.extractor = MemoryExtractor(fast_model_url)
        self.memory = MemoryStore(project_name)


    def receive_feedback(self, text):
        self.feedback_inbox.append(text)


    def run(
        self,
        scene_prompt: str,
        outline_snippet: str,
        world_notes: str,
        character_notes: str,
        auto_memory: bool = True
    ) -> str:
        """
        Generate a draft scene using outline, world, characters, and memory.
        """
        if self.feedback_inbox:
            # Inject feedback into the context 
            context = {}
            context["human_feedback"] = self.feedback_inbox.copy()
            self.feedback_inbox.clear()
        else:
            context = {}
            
        memory_context = self.memory.search("relevant scene context", k=15)
        memory_text = "\n".join(memory_context) if memory_context else "None yet."

        prompt = f"""
        You are a Scene Writer for a long-form narrative project.

        Scene goal / prompt:
        \"\"\"{scene_prompt}\"\"\"

        Relevant outline snippet:
        \"\"\"{outline_snippet}\"\"\"

        World notes:
        \"\"\"{world_notes}\"\"\"

        Character notes:
        \"\"\"{character_notes}\"\"\"

        Additional project memory:
        \"\"\"{memory_text}\"\"\"

        Task:
        - Write a single, coherent scene that advances the story.
        - Use strong visuals, clear blocking, and emotional beats.
        - Make sure character actions and dialogue reflect their motivations and arcs.
        - Ensure the scene respects world rules and established canon.

        Output:
        - Prose scene, not bullet points.
        - Keep it focused on this moment, not summary.
        """

        # --- Model selection ---
        if self.model_mode == "high_quality":
            # Use heavy local 7B model for richer prose
            scene_text = generate_with_heavy_model(prompt)
        else:
            # Use fast model via HTTP
            payload = {
                "model": "Qwen/Qwen2.5-3B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9
            }
            response = requests.post(self.fast_model_url, json=payload)
            scene_text = response.json()["choices"][0]["message"]["content"]


        if auto_memory:
            facts = self.extractor.extract(scene_text)
            for fact in facts:
                self.memory.add(fact)

        self.send_message(
            recipient="producer",
            msg_type="SCENE_READY",
            payload={"scene": scene_text}
        )

        return scene_text
