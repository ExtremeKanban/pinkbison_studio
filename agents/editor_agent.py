import requests
from models.heavy_model import generate_with_heavy_model
from agents.base_agent import AgentBase
from core.event_bus import EventBus
from core.audit_log import AuditLog


class EditorAgent(AgentBase):
    def __init__(self, project_name, event_bus: EventBus, audit_log: AuditLog,
                 fast_model_url, model_mode):
        super().__init__("editor", project_name, event_bus, audit_log,
                        fast_model_url, model_mode)

    def run(self, text: str, style_goal: str = "clear, vivid, emotionally resonant prose") -> str:
        """
        Edit and improve text for style, clarity, pacing, and emotional impact.
        """
        
        # Check for feedback from EventBus
        recent_messages = self.get_recent_messages(limit=5)
        feedback_texts = [
            msg.get('content', '') 
            for msg in recent_messages 
            if msg.get('type') == 'feedback'
        ]
        
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
        
        if feedback_texts:
            prompt += f"\n\nRecent feedback:\n" + "\n".join(feedback_texts)

        # Model selection
        if self.model_mode == "high_quality":
            edited_text = generate_with_heavy_model(prompt)
        else:
            payload = {
                "model": "Qwen/Qwen2.5-3B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.6
            }
            response = requests.post(self.fast_model_url, json=payload)
            edited_text = response.json()["choices"][0]["message"]["content"]

        return edited_text