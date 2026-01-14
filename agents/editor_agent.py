import requests
from models.heavy_model import generate_with_heavy_model


class EditorAgent:
    def __init__(
        self,
        fast_model_url: str = "http://localhost:8000/v1/chat/completions",
        model_mode: str = "draft",
    ):
        self.fast_model_url = fast_model_url
        self.model_mode = model_mode


    def run(
        self,
        text: str,
        style_goal: str = "clear, vivid, emotionally resonant prose"
    ) -> str:
        """
        Edit and improve text for style, clarity, pacing, and emotional impact.
        """
        prompt = f"""
        You are a professional fiction line editor.

        Editing goal:
        \"\"\"{style_goal}\"\"\"

        Original text:
        \"\"\"{text}\"\"\"

        Task:
        - Improve clarity, rhythm, and emotional impact.
        - Tighten weak phrasing.
        - Preserve the author's voice as much as possible.
        - Do not change factual content or core events.

        Output:
        - Only return the revised text, no commentary.
        """

        # --- Model selection ---
        if self.model_mode == "high_quality":
            # Use heavy local 7B model for premium editing
            edited_text = generate_with_heavy_model(prompt)
        else:
            # Use fast model via HTTP
            payload = {
                "model": "Qwen/Qwen2.5-3B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.6
            }
            response = requests.post(self.fast_model_url, json=payload)
            edited_text = response.json()["choices"][0]["message"]["content"]

        return edited_text

