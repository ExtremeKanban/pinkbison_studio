import requests
from memory_store import MemoryStore
from agent_bus import GLOBAL_AGENT_BUS
from models.heavy_model import generate_with_heavy_model


class ContinuityAgent:
    def __init__(
        self,
        project_name: str = "default_project",
        fast_model_url: str = "http://localhost:8000/v1/chat/completions",
        model_mode: str = "draft",
    ):
        self.project_name = project_name
        self.name = "continuity"
        self.fast_model_url = fast_model_url
        self.model_mode = model_mode
        self.memory = MemoryStore(project_name=project_name)


    def run(self, new_text: str) -> str:
        """
        Check new_text against project memory for contradictions and adjust if needed.
        Returns a revised version that is as consistent as possible.
        """
        memory_context = self.memory.search("core canon rules events characters world", k=20)
        memory_text = "\n".join(memory_context) if memory_context else "None yet."

        prompt = f"""
        You are a Continuity and Canon Enforcement Agent for a narrative universe.

        Canon memory (facts, rules, events, constraints):
        \"\"\"{memory_text}\"\"\"

        New candidate text:
        \"\"\"{new_text}\"\"\"

        Task:
        - Check the candidate text against the canon memory.
        - Identify any contradictions, violations of established rules, or inconsistencies.
        - Produce a revised version of the text that:
          - resolves contradictions
          - respects all canon rules and facts
          - preserves as much of the original intent and style as possible

        Output:
        - First, briefly list any issues you found.
        - Then provide the fully revised text under a heading: REVISED TEXT
        """

        # --- Model selection ---
        if self.model_mode == "high_quality":
            # Use heavy local 7B model for deeper canon enforcement
            checked_text = generate_with_heavy_model(prompt)
        else:
            # Use fast model via HTTP
            payload = {
                "model": "Qwen/Qwen2.5-3B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5
            }
            response = requests.post(self.fast_model_url, json=payload)
            checked_text = response.json()["choices"][0]["message"]["content"]


        # --- Extract issues ---
        issues = ""
        if "REVISED TEXT" in checked_text:
            issues = checked_text.split("REVISED TEXT")[0].strip()
        else:
            issues = "No explicit issues section found."

        # --- Send message to ProducerAgent ---
        GLOBAL_AGENT_BUS.send(
            project_name=self.project_name,
            sender=self.name,
            recipient="producer",
            msg_type="CRITIQUE",
            payload={
                "raw_output": checked_text,
                "issues": issues,
                "original_text": new_text,
            },
        )

        return checked_text
