import json
import requests

from agents.plot_architect import PlotArchitect
from agents.worldbuilder import WorldbuilderAgent
from agents.character_agent import CharacterAgent
from agents.scene_generator import SceneGeneratorAgent
from agents.continuity_agent import ContinuityAgent
from agents.editor_agent import EditorAgent

from models.heavy_model import generate_with_heavy_model
from agent_bus import GLOBAL_AGENT_BUS
from intelligence_bus import IntelligenceBus


class ProducerAgent:
    """
    High-level orchestrator that coordinates other agents to run pipelines.
    Supports:
    - Draft Mode (fast model)
    - High‑Quality Mode (heavy local model)
    """

    def __init__(
        self,
        project_name: str,
        intelligence_bus,
        fast_model_url: str,
        model_mode: str,
    ):
        self.project_name = project_name
        self.name = "producer"
        self._last_msg_id = None

        self.model_mode = model_mode
        self.fast_model_url = fast_model_url
        self.intelligence_bus = intelligence_bus

        # Instantiate sub‑agents
        self.plot_architect = PlotArchitect(
            project_name=project_name,
            intelligence_bus=intelligence_bus,
            fast_model_url=fast_model_url,
            model_mode=model_mode,
        )

        self.worldbuilder = WorldbuilderAgent(
            project_name=project_name,
            intelligence_bus=intelligence_bus,
            fast_model_url=fast_model_url,
            model_mode=model_mode,
        )

        self.character_agent = CharacterAgent(
            project_name=project_name,
            intelligence_bus=intelligence_bus,
            fast_model_url=fast_model_url,
            model_mode=model_mode,
        )

        self.scene_generator = SceneGeneratorAgent(
            project_name=project_name,
            intelligence_bus=intelligence_bus,
            fast_model_url=fast_model_url,
            model_mode=model_mode,
        )

        self.continuity_agent = ContinuityAgent(
            project_name=project_name,
            intelligence_bus=intelligence_bus,
            fast_model_url=fast_model_url,
            model_mode=model_mode,
        )

        self.editor_agent = EditorAgent(
            project_name=project_name,
            intelligence_bus=intelligence_bus,
            fast_model_url=fast_model_url,
            model_mode=model_mode,
        )

        self.agents = {
            "plot_architect": self.plot_architect,
            "worldbuilder": self.worldbuilder,
            "character_agent": self.character_agent,
            "scene_generator": self.scene_generator,
            "continuity": self.continuity_agent,
            "editor": self.editor_agent,
        }


    def handle_feedback(self, agent_name, feedback_text):
        # Log it
        self.intelligence_bus.add_feedback(agent_name, feedback_text)

        # Route it to the agent
        agent = self.agents.get(agent_name)
        if agent:
            agent.receive_feedback(feedback_text)

    def poll_agent_messages(self):
        msgs = self.intelligence_bus.get_messages_for("producer", since_id=self._last_msg_id)
        if msgs:
            self._last_msg_id = msgs[-1]["id"]
        return msgs

    # ---------------------------------------------------------
    # Messaging
    # ---------------------------------------------------------
    def fetch_messages(self):
        msgs = GLOBAL_AGENT_BUS.get_for(
            project_name=self.project_name,
            agent_name=self.name,
            since_id=self._last_msg_id,
        )
        if msgs:
            self._last_msg_id = msgs[-1].id
        return msgs

    def get_continuity_critiques(self):
        msgs = self.fetch_messages()
        return [
            m for m in msgs
            if m.sender == "continuity" and m.type == "CRITIQUE"
        ]

    # ---------------------------------------------------------
    # Story Bible Pipeline
    # ---------------------------------------------------------
    def run_story_bible_pipeline(
        self,
        idea: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = True,
    ) -> dict:

        outline = self.plot_architect.run(
            idea=idea,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
        )

        world_doc = self.worldbuilder.run(
            outline=outline,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
        )

        character_doc = self.character_agent.run(
            outline=outline,
            world_notes=world_doc,
            auto_memory=auto_memory,
        )

        return {
            "outline": outline,
            "world": world_doc,
            "characters": character_doc,
        }

    # ---------------------------------------------------------
    # Scene Pipeline
    # ---------------------------------------------------------
    def generate_scene_with_checks(
        self,
        scene_prompt: str,
        outline_snippet: str,
        world_notes: str,
        character_notes: str,
        auto_memory: bool = True,
        run_continuity: bool = True,
        run_editor: bool = True,
    ) -> dict:

        scene_raw = self.scene_generator.run(
            scene_prompt=scene_prompt,
            outline_snippet=outline_snippet,
            world_notes=world_notes,
            character_notes=character_notes,
            auto_memory=auto_memory,
        )

        scene_after_continuity = scene_raw
        if run_continuity:
            scene_after_continuity = self.continuity_agent.run(scene_raw)

            critiques = self.get_continuity_critiques()
            if critiques:
                print("\n[ProducerAgent] Continuity messages received:")
                for c in critiques:
                    print(f"- {c.payload.get('issues')}")

        scene_final = scene_after_continuity
        if run_editor:
            scene_final = self.editor_agent.run(scene_after_continuity)

        return {
            "raw": scene_raw,
            "after_continuity": scene_after_continuity,
            "final": scene_final,
        }

    # ---------------------------------------------------------
    # Outline → JSON Chapter Plan
    # ---------------------------------------------------------
    def plan_chapters_from_outline(self, outline: str, max_chapters: int = 20) -> dict:

        prompt = f"""
        Convert the following outline into STRICT JSON with chapters:

        Outline:
        \"\"\"{outline}\"\"\"

        Requirements:
        - Return ONLY valid JSON.
        - Top-level key: "chapters"
        - Each chapter must have:
          - "title"
          - "summary"
          - "beats"
        - No commentary, no markdown.
        - Max chapters: {max_chapters}
        """

        if self.model_mode == "high_quality":
            raw = generate_with_heavy_model(prompt)
        else:
            payload = {
                "model": "Qwen/Qwen2.5-3B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
            }
            response = requests.post(self.fast_model_url, json=payload)
            raw = response.json()["choices"][0]["message"]["content"]

        raw = raw.strip()

        try:
            return json.loads(raw)
        except Exception:
            pass

        cleaned = raw
        if "```" in raw:
            parts = raw.split("```")
            blocks = [p for p in parts if "{" in p and "}" in p]
            if blocks:
                cleaned = blocks[0].replace("json\n", "").strip()

        return json.loads(cleaned)

    # ---------------------------------------------------------
    # Chapter Generation
    # ---------------------------------------------------------
    def _generate_chapter_from_plan(
        self,
        chapter_plan: dict,
        outline: str,
        world_doc: str,
        character_doc: str,
        auto_memory: bool = True,
        run_continuity: bool = True,
        run_editor: bool = True,
    ) -> dict:

        title = chapter_plan.get("title", "Untitled Chapter")
        beats = chapter_plan.get("beats", []) or []

        scenes = []
        for beat in beats:
            scene_text = self.scene_generator.run(
                scene_prompt=beat,
                outline_snippet=f"{title}\n{outline}",
                world_notes=world_doc,
                character_notes=character_doc,
                auto_memory=auto_memory,
            )
            scenes.append(scene_text)

        chapter_raw = "\n\n".join(scenes)

        chapter_after_continuity = chapter_raw
        if run_continuity:
            chapter_after_continuity = self.continuity_agent.run(chapter_raw)

        chapter_final = chapter_after_continuity
        if run_editor:
            chapter_final = self.editor_agent.run(chapter_after_continuity)

        return {
            "title": title,
            "raw": chapter_raw,
            "after_continuity": chapter_after_continuity,
            "final": chapter_final,
        }

    # ---------------------------------------------------------
    # Chapter Pipeline
    # ---------------------------------------------------------
    def run_chapter_pipeline(
        self,
        idea: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = True,
        run_continuity: bool = True,
        run_editor: bool = True,
        chapter_index: int = 0,
        max_chapters: int = 20,
    ) -> dict:

        bible = self.run_story_bible_pipeline(
            idea=idea,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
        )

        outline = bible["outline"]
        world_doc = bible["world"]
        character_doc = bible["characters"]

        plan = self.plan_chapters_from_outline(outline, max_chapters=max_chapters)
        chapters = plan.get("chapters", [])

        if not chapters:
            raise ValueError("Chapter plan has no chapters.")

        chapter_index = max(0, min(chapter_index, len(chapters) - 1))
        chapter_plan = chapters[chapter_index]

        chapter_result = self._generate_chapter_from_plan(
            chapter_plan,
            outline=outline,
            world_doc=world_doc,
            character_doc=character_doc,
            auto_memory=auto_memory,
            run_continuity=run_continuity,
            run_editor=run_editor,
        )

        return {
            "outline": outline,
            "world": world_doc,
            "characters": character_doc,
            "plan": plan,
            "chapter_index": chapter_index,
            "chapter": chapter_result,
        }

    # ---------------------------------------------------------
    # Full Story Pipeline
    # ---------------------------------------------------------
    def run_full_story_pipeline(
        self,
        idea: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = True,
        run_continuity: bool = True,
        run_editor: bool = True,
        max_chapters: int = 20,
    ) -> dict:

        bible = self.run_story_bible_pipeline(
            idea=idea,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
        )

        outline = bible["outline"]
        world_doc = bible["world"]
        character_doc = bible["characters"]

        plan = self.plan_chapters_from_outline(outline, max_chapters=max_chapters)
        chapters_plan = plan.get("chapters", [])

        chapter_results = []
        for idx, chapter_plan in enumerate(chapters_plan):
            if idx >= max_chapters:
                break

            print(f"[ProducerAgent] Generating chapter {idx + 1}: {chapter_plan.get('title', 'Untitled')}")
            chapter_result = self._generate_chapter_from_plan(
                chapter_plan,
                outline=outline,
                world_doc=world_doc,
                character_doc=character_doc,
                auto_memory=auto_memory,
                run_continuity=run_continuity,
                run_editor=run_editor,
            )
            chapter_results.append(chapter_result)

        full_story_text = "\n\n".join(ch["final"] for ch in chapter_results)

        return {
            "outline": outline,
            "world": world_doc,
            "characters": character_doc,
            "plan": plan,
            "chapters": chapter_results,
            "full_story": full_story_text,
        }

    # ---------------------------------------------------------
    # Director Mode
    # ---------------------------------------------------------
    def run_director_mode(
        self,
        idea: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = True,
        run_continuity: bool = True,
        run_editor: bool = True,
        max_chapters: int = 20,
        max_revision_passes: int = 2,
    ) -> dict:

        base = self.run_full_story_pipeline(
            idea=idea,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
            run_continuity=run_continuity,
            run_editor=run_editor,
            max_chapters=max_chapters,
        )

        chapters = base["chapters"]

        for pass_idx in range(max_revision_passes):
            print(f"[ProducerAgent] Director Mode revision pass {pass_idx + 1}/{max_revision_passes}")

            revised = []
            for ch in chapters:
                text = ch.get("final") or ch.get("after_continuity") or ch.get("raw") or ""
                if not text.strip():
                    revised.append(ch)
                    continue

                revised_text = self.editor_agent.run(text)
                new_ch = dict(ch)
                new_ch["final"] = revised_text
                revised.append(new_ch)

            chapters = revised

        full_story_text = "\n\n".join(ch["final"] for ch in chapters)

        return {
            "outline": base["outline"],
            "world": base["world"],
            "characters": base["characters"],
            "plan": base["plan"],
            "chapters": chapters,
            "full_story": full_story_text,
        }
