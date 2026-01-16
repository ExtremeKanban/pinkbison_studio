import requests
from typing import List, Dict, Any

from memory_store import MemoryStore
from graph_store import GraphStore
from agent_bus import GLOBAL_AGENT_BUS
from intelligence_bus import IntelligenceBus


from agents.base_agent import AgentBase

class CreativeDirectorAgent(AgentBase):
    def __init__(
        self,
        project_name: str,
        intelligence_bus,
        fast_model_url: str,
        model_mode: str,
    ):
        super().__init__(
            "creative_director",
            project_name,
            intelligence_bus,
            fast_model_url,
            model_mode=model_mode,
        )

        self.memory = MemoryStore(project_name)
        self.graph = GraphStore(project_name)



    def receive_feedback(self, text):
        self.feedback_inbox.append(text)

    def _call_model(self, prompt: str) -> str:
        payload = {
            "model": "Qwen/Qwen2.5-3B-Instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4
        }
        resp = requests.post(self.fast_model_url, json=payload)
        return resp.json()["choices"][0]["message"]["content"]

    def analyze_scene_critique(self, issues: str, original_text: str) -> Dict[str, Any]:
        """
        Turn raw continuity issues into:
        - suggested canon rules
        - guidance for revision
        """
        # Inject human feedback if present
        if self.feedback_inbox:
            human_feedback = "\n".join(self.feedback_inbox)
            self.feedback_inbox.clear()
        else:
            human_feedback = "None"

        prompt = f"""
        You are a Creative Director overseeing a long-running sci-fi narrative.

        Human feedback:
        \"\"\"{human_feedback}\"\"\"

        Continuity issues detected:
        \"\"\"{issues}\"\"\"

        Original scene:
        \"\"\"{original_text}\"\"\"

        Task:
        - Summarize the core problem(s) in 2-4 bullet points.
        - Propose 1-3 canon rules that would prevent similar issues.
        - Provide high-level guidance for how scenes like this should be written in the future.

        Output format (JSON):
        {{
          "core_problems": ["...", "..."],
          "proposed_canon_rules": ["...", "..."],
          "guidance": "..."
        }}
        """
        raw = self._call_model(prompt)
        # We'll trust the model to output JSON-like; you can harden this later.
        try:
            import json
            data = json.loads(raw)
        except Exception:
            data = {
                "core_problems": [raw],
                "proposed_canon_rules": [],
                "guidance": raw,
            }
        return data

    def log_canon_rules(self, rules: List[str]) -> None:
        """
        Store canon rules in graph and memory.
        """
        if not rules:
            return

        for i, rule in enumerate(rules):
            rule_id = f"CANON_{self.project_name}_{i}"
            self.graph.add_canon_rule(rule_id=rule_id, rule=rule, scope=[], notes="Added by Creative Director")
            self.memory.add(f"[CANON RULE] {rule}")

    def send_guidance_message(self, guidance: str) -> None:
        """
        Send a message to ALL agents with high-level guidance.
        """
        if not guidance:
            return

        GLOBAL_AGENT_BUS.send(
            project_name=self.project_name,
            sender=self.name,
            recipient="ALL",
            msg_type="GUIDANCE",
            payload={"guidance": guidance},
        )
