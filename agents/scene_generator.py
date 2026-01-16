import requests
from agents.memory_extractor import MemoryExtractor
from memory_store import MemoryStore
from models.heavy_model import generate_with_heavy_model
from agents.base_agent import AgentBase
from core.event_bus import EventBus
from core.audit_log import AuditLog


class SceneGeneratorAgent(AgentBase):
    def __init__(self, project_name, event_bus: EventBus, audit_log: AuditLog,
                 fast_model_url, model_mode):
        super().__init__("scene_generator", project_name, event_bus, audit_log,
                        fast_model_url, model_mode)
        self.extractor = MemoryExtractor(fast_model_url)
        self.memory = MemoryStore(project_name)

    def run(self, scene_prompt: str, outline_snippet: str, world_notes: str,
            character_notes: str, auto_memory: bool = True) -> str:
        """
        Generate a draft scene using outline, world, characters, and memory.
        """
        
        # Check for feedback from EventBus
        recent_messages = self.get_recent_messages(limit=5)
        feedback_texts = [
            msg.get('content', '') 
            for msg in recent_messages 
            if msg.get('type') == 'feedback'
        ]
        
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
        
        if feedback_texts:
            prompt += f"\n\nRecent feedback:\n" + "\n".join(feedback_texts)

        # Model selection
        if self.model_mode == "high_quality":
            scene_text = generate_with_heavy_model(prompt)
        else:
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