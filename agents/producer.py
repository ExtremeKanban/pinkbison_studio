"""
ProducerAgent - High-level orchestrator for creative pipelines.

NOTE: ProducerAgent does NOT inherit from AgentBase because it manages
other agents rather than being a peer agent. It creates agents via
AgentFactory and coordinates their work.
"""

import json
import requests
from typing import Dict, Any, List

from core.event_bus import EventBus
from core.audit_log import AuditLog
from core.agent_factory import AgentFactory
from models.heavy_model import generate_with_heavy_model


class ProducerAgent:
    """
    High-level orchestrator that coordinates other agents to run pipelines.
    
    Changes from old version:
    - Uses AgentFactory to create fresh agent instances per task
    - EventBus + AuditLog integration
    - No longer stores agent instances (creates on-demand)
    """

    def __init__(self, project_name: str, event_bus: EventBus, audit_log: AuditLog,
                 fast_model_url: str, model_mode: str):
        self.project_name = project_name
        self.name = "producer"
        self._last_msg_id = None

        self.model_mode = model_mode
        self.fast_model_url = fast_model_url
        self.event_bus = event_bus
        self.audit_log = audit_log

        # Agent factory for creating fresh instances
        self.agent_factory = AgentFactory(
            project_name=project_name,
            event_bus=event_bus,
            audit_log=audit_log,
            fast_model_url=fast_model_url,
            model_mode=model_mode
        )

    def handle_feedback(self, agent_name: str, feedback_text: str) -> None:
        """Route feedback to agent via EventBus"""
        self.event_bus.publish(
            sender="user",
            recipient=agent_name,
            event_type="feedback",
            payload={"content": feedback_text, "type": "feedback"}
        )
        
        self.audit_log.append(
            event_type="user_feedback",
            sender="user",
            recipient=agent_name,
            payload={"content": feedback_text}
        )

    def poll_agent_messages(self):
        """Get recent messages from EventBus"""
        return self.event_bus.get_recent(self.name, limit=20)

    def get_intelligence_messages(
        self, 
        recipient: str = "all", 
        limit: int = 10
    ) -> list:
        """
        Get messages from agent bus for a recipient.
        
        Uses Registry pattern instead of global bus.
        
        Args:
            recipient: Agent name or "all" for broadcast
            limit: Maximum messages to return
            
        Returns:
            List of messages for the recipient
        """
        from core.registry import REGISTRY
        
        agent_bus = REGISTRY.get_agent_bus(self.project_name)
        msgs = agent_bus.get_for(
            recipient=recipient if recipient != "all" else "broadcast",
            limit=limit
        )
        return msgs

    def get_continuity_critiques(self):
        """Get continuity critiques from legacy bus"""
        msgs = self.fetch_messages()
        return [
            m for m in msgs
            if m.sender == "continuity" and m.type == "CRITIQUE"
        ]

    # ---------------------------------------------------------
    # Story Bible Pipeline
    # ---------------------------------------------------------
    def run_story_bible_pipeline(self, idea: str, genre: str, tone: str,
                                  themes: str, setting: str,
                                  auto_memory: bool = True) -> dict:
        """
        Generate story bible: outline + world + characters.
        Creates fresh agent instances for each step.
        """
        
        # Create fresh PlotArchitect
        plot_architect = self.agent_factory.create_plot_architect()
        outline = plot_architect.run(
            idea=idea,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
        )

        # Create fresh Worldbuilder
        worldbuilder = self.agent_factory.create_worldbuilder()
        world_doc = worldbuilder.run(
            outline=outline,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
        )

        # Create fresh CharacterAgent
        character_agent = self.agent_factory.create_character_agent()
        character_doc = character_agent.run(
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
    def generate_scene_with_checks(self, scene_prompt: str, outline_snippet: str,
                                    world_notes: str, character_notes: str,
                                    auto_memory: bool = True,
                                    run_continuity: bool = True,
                                    run_editor: bool = True) -> dict:
        """
        Generate scene with continuity and editor checks.
        Creates fresh agent instances for each step.
        """
        
        # Create fresh SceneGenerator
        scene_generator = self.agent_factory.create_scene_generator()
        scene_raw = scene_generator.run(
            scene_prompt=scene_prompt,
            outline_snippet=outline_snippet,
            world_notes=world_notes,
            character_notes=character_notes,
            auto_memory=auto_memory,
        )

        scene_after_continuity = scene_raw
        if run_continuity:
            continuity_agent = self.agent_factory.create_continuity_agent()
            scene_after_continuity = continuity_agent.run(scene_raw)

            critiques = self.get_continuity_critiques()
            if critiques:
                print("\n[ProducerAgent] Continuity messages received:")
                for c in critiques:
                    print(f"- {c.payload.get('issues')}")

        scene_final = scene_after_continuity
        if run_editor:
            editor_agent = self.agent_factory.create_editor_agent()
            scene_final = editor_agent.run(scene_after_continuity)

        return {
            "raw": scene_raw,
            "after_continuity": scene_after_continuity,
            "final": scene_final,
        }

    # ---------------------------------------------------------
    # Outline → JSON Chapter Plan
    # ---------------------------------------------------------
    def plan_chapters_from_outline(self, outline: str, max_chapters: int = 20) -> dict:
        """Convert outline into structured chapter plan"""
        
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

        # Clean markdown fences if present
        cleaned = raw
        if "```" in raw:
            parts = raw.split("```")
            blocks = [p for p in parts if "{" in p and "}" in p]
            if blocks:
                cleaned = blocks[0].replace("json\n", "").strip()

        return json.loads(cleaned)

    # ---------------------------------------------------------
    # Chapter Generation (internal helper)
    # ---------------------------------------------------------
    def _generate_chapter_from_plan(self, chapter_plan: dict, outline: str,
                                     world_doc: str, character_doc: str,
                                     auto_memory: bool = True,
                                     run_continuity: bool = True,
                                     run_editor: bool = True) -> dict:
        """
        Generate a single chapter from a chapter plan.
        Creates fresh agent instances.
        """
        
        title = chapter_plan.get("title", "Untitled Chapter")
        beats = chapter_plan.get("beats", []) or []

        scenes = []
        scene_generator = self.agent_factory.create_scene_generator()
        
        for beat in beats:
            scene_text = scene_generator.run(
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
            continuity_agent = self.agent_factory.create_continuity_agent()
            chapter_after_continuity = continuity_agent.run(chapter_raw)

        chapter_final = chapter_after_continuity
        if run_editor:
            editor_agent = self.agent_factory.create_editor_agent()
            chapter_final = editor_agent.run(chapter_after_continuity)

        return {
            "title": title,
            "raw": chapter_raw,
            "after_continuity": chapter_after_continuity,
            "final": chapter_final,
        }
    
    # ---------------------------------------------------------
    # Chapter Pipeline
    # ---------------------------------------------------------
    def run_chapter_pipeline(self, idea: str, genre: str, tone: str,
                            themes: str, setting: str,
                            auto_memory: bool = True,
                            run_continuity: bool = True,
                            run_editor: bool = True,
                            chapter_index: int = 0,
                            max_chapters: int = 20) -> dict:
        """Generate a single chapter from idea"""
        
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
    def run_full_story_pipeline(self, idea: str, genre: str, tone: str,
                                themes: str, setting: str,
                                auto_memory: bool = True,
                                run_continuity: bool = True,
                                run_editor: bool = True,
                                max_chapters: int = 20) -> dict:
        """Generate complete story with all chapters"""
        
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
    def run_director_mode(self, idea: str, genre: str, tone: str,
                         themes: str, setting: str,
                         auto_memory: bool = True,
                         run_continuity: bool = True,
                         run_editor: bool = True,
                         max_chapters: int = 20,
                         max_revision_passes: int = 2) -> dict:
        """Generate story with multiple revision passes"""
        
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
            editor_agent = self.agent_factory.create_editor_agent()
            
            for ch in chapters:
                text = ch.get("final") or ch.get("after_continuity") or ch.get("raw") or ""
                if not text.strip():
                    revised.append(ch)
                    continue

                revised_text = editor_agent.run(text)
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