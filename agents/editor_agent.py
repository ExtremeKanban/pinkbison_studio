import requests
from models.heavy_model import generate_with_heavy_model
from intelligence_bus import IntelligenceBus


class EditorAgent:
    def __init__(
        self,
        project_name,
        fast_model_url: str = "http://localhost:8000/v1/chat/completions",
        model_mode: str = "draft",
    ):
        self.fast_model_url = fast_model_url
        self.model_mode = model_mode
        self.project_name = project_name
        self.feedback_inbox = []

    def receive_feedback(self, text):
        self.feedback_inbox.append(text)


    def run(
        self,
        text: str,
        style_goal: str = "clear, vivid, emotionally resonant prose"
    ) -> str:
        """
        Edit and improve text for style, clarity, pacing, and emotional impact.
        """

        if self.feedback_inbox:
            # Inject feedback into the context 
            context = {}
            context["human_feedback"] = self.feedback_inbox.copy()
            self.feedback_inbox.clear()
        else:
            context = {}
            
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

