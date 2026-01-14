import requests
from agents.memory_extractor import MemoryExtractor
from memory_store import MemoryStore
from models.heavy_model import generate_with_heavy_model


class PlotArchitect:
    def __init__(
        self,
        project_name: str = "default_project",
        fast_model_url: str = "http://localhost:8000/v1/chat/completions",
        model_mode: str = "draft",
    ):
        self.fast_model_url = fast_model_url
        self.model_mode = model_mode
        self.extractor = MemoryExtractor(fast_model_url)
        self.memory = MemoryStore(project_name=project_name)


    def run(
        self,
        idea: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = False
    ) -> str:
        """Expand a seed idea into a structured 3‑act outline using project context."""
        prompt = f"""
        You are a Plot Architect.

        Use the following project context:
        - Genre: {genre}
        - Tone: {tone}
        - Themes: {themes}
        - Setting: {setting}

        Expand the following idea into a detailed 3‑act outline.

        Idea:
        \"\"\"{idea}\"\"\"

        Requirements:
        - Provide Act I, Act II, Act III
        - Include major beats
        - Identify key characters
        - Identify central conflict
        - Provide 1–2 twist options
        - Keep it clear and structured with headings for each act.
        """

        # --- Model selection ---
        if self.model_mode == "high_quality":
            # Use heavy local 7B model
            outline = generate_with_heavy_model(prompt)
        else:
            # Use fast model via HTTP
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

        return outline
