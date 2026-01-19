"""
ProducerAgent orchestrates multi-step creative pipelines.

Does NOT inherit from AgentBase.
Creates fresh agent instances via AgentFactory for each pipeline step.
"""

from typing import Dict, Any, List
from xmlrpc import client

from click import prompt
from agents.base_agent import AgentBase
from core.event_bus import EventBus
from core.audit_log import AuditLog
from core.agent_factory import AgentFactory
from core.project_state import ProjectState
from core.registry import REGISTRY
from models.model_client import ModelClient
        

class ProducerAgent:
    """
    Orchestrates multi-step creative pipelines.
    
    Does not inherit from AgentBase - it creates and coordinates other agents.
    Uses AgentFactory to create fresh agent instances for each step.
    """

    def __init__(self, project_name: str, event_bus: EventBus, audit_log: AuditLog,
                 fast_model_url: str, model_mode: str = "fast"):
        self.project_name = project_name
        self.event_bus = event_bus
        self.audit_log = audit_log
        self.fast_model_url = fast_model_url
        self.model_mode = model_mode
        
        self.agent_factory = AgentFactory(
            project_name=project_name,
            event_bus=event_bus,
            audit_log=audit_log,
            fast_model_url=fast_model_url,
            model_mode=model_mode
        )
        
        self.output_manager = REGISTRY.get_output_manager(project_name)

    # ---------------------------------------------------------
    # Story Bible Pipeline
    # ---------------------------------------------------------
    def run_story_bible_pipeline(self, idea: str, genre: str, tone: str,
                                 themes: str, setting: str,
                                 auto_memory: bool = True) -> dict:
        """
        Generate story bible (outline, world, characters).
        
        Creates fresh agent instances for each step.
        """
        
        # 1) Outline
        plot_agent = self.agent_factory.create_plot_architect()
        outline = plot_agent.run(
            idea=idea,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
        )

        # 2) World
        world_agent = self.agent_factory.create_worldbuilder()
        world_doc = world_agent.run(
            outline=outline,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
        )

        # 3) Characters
        char_agent = self.agent_factory.create_character_agent()
        character_doc = char_agent.run(
            outline=outline,
            world_notes=world_doc,
            auto_memory=auto_memory,
        )

        result = {
            "outline": outline,
            "world": world_doc,
            "characters": character_doc,
        }
        
        # Save to pipeline history
        self._save_pipeline_result("story_bible", result)
        
        return result

    # ---------------------------------------------------------
    # Chapter Planning
    # ---------------------------------------------------------
    def plan_chapters_from_outline(self, outline: str, max_chapters: int = 20) -> dict:
        """Generate chapter plan from outline"""
        
        prompt = f"""
Given this outline, create a chapter-by-chapter breakdown.

Outline:
{outline}

Create up to {max_chapters} chapters. For each chapter provide:
- Title
- 3-5 key beats/scenes

Return ONLY a JSON object with this structure:
{{
  "chapters": [
    {{
      "title": "Chapter 1 Title",
      "beats": ["Scene 1 description", "Scene 2 description", "Scene 3 description"]
    }},
    ...
  ]
}}

Do not include any other text, just the JSON.
"""

        from models.model_client import ModelClient
        client = ModelClient(model_url=self.fast_model_url)
        response = client.complete_simple(prompt=prompt, temperature=0.7)
        
        # Parse JSON response
        import json
        import re
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            clean = re.sub(r'```json\s*|\s*```', '', response).strip()
            plan = json.loads(clean)
        except json.JSONDecodeError:
            # Fallback: create simple plan
            print(f"[ProducerAgent] Failed to parse chapter plan, using fallback")
            plan = {
                "chapters": [
                    {
                        "title": f"Chapter {i+1}",
                        "beats": [f"Scene from outline section {i+1}"]
                    }
                    for i in range(min(3, max_chapters))
                ]
            }
        
        return plan

    def _generate_chapter_from_plan(self, chapter_plan: dict,
                                   outline: str,
                                   world_doc: str,
                                   character_doc: str,
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

        result = {
            "outline": outline,
            "world": world_doc,
            "characters": character_doc,
            "plan": plan,
            "chapter_index": chapter_index,
            "chapter": chapter_result,
        }
        
        # Save chapter to outputs
        self.output_manager.save_chapter(chapter_index, chapter_result)
        
        # Save to pipeline history
        self._save_pipeline_result("chapter", result)
        
        return result

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

        if not chapters_plan:
            raise ValueError("Chapter plan has no chapters.")

        chapters = []
        for idx, chapter_plan in enumerate(chapters_plan):
            print(f"[ProducerAgent] Generating chapter {idx + 1}/{len(chapters_plan)}")
            
            chapter_result = self._generate_chapter_from_plan(
                chapter_plan,
                outline=outline,
                world_doc=world_doc,
                character_doc=character_doc,
                auto_memory=auto_memory,
                run_continuity=run_continuity,
                run_editor=run_editor,
            )
            
            chapters.append(chapter_result)

        full_story_text = "\n\n".join(ch["final"] for ch in chapters)
        
        # Save each chapter to outputs
        for idx, chapter in enumerate(chapters):
            self.output_manager.save_chapter(idx, chapter)
        
        # Save full story draft
        self.output_manager.save_draft("full_story", full_story_text)

        result = {
            "outline": outline,
            "world": world_doc,
            "characters": character_doc,
            "plan": plan,
            "chapters": chapters,
            "full_story": full_story_text,
        }
        
        # Save to pipeline history
        self._save_pipeline_result("full_story", result)
        
        return result
    
    # ---------------------------------------------------------
    # Director Mode (with revision passes)
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
        
        # Save each chapter to outputs
        for idx, chapter in enumerate(chapters):
            self.output_manager.save_chapter(idx, chapter)
        
        # Save full story draft
        self.output_manager.save_draft("director_mode", full_story_text)

        result = {
            "outline": base["outline"],
            "world": base["world"],
            "characters": base["characters"],
            "plan": base["plan"],
            "chapters": chapters,
            "full_story": full_story_text,
        }
        
        # Save to pipeline history
        self._save_pipeline_result("director", result)
        
        return result
    
    # ---------------------------------------------------------
    # Helper Methods
    # ---------------------------------------------------------
    def handle_feedback(self, agent_name: str, feedback_text: str) -> None:
        """
        Send feedback to an agent via EventBus.
        
        Agent will receive it on next pipeline run.
        """
        self.event_bus.publish(
            sender="producer",
            recipient=agent_name,
            msg_type="user_feedback",
            payload={"feedback": feedback_text}
        )
        
        self.audit_log.append(
            event_type="user_feedback",
            sender="producer",
            recipient=agent_name,
            payload={"feedback": feedback_text}
        )
        
        print(f"[ProducerAgent] Sent feedback to {agent_name}")

    def _save_pipeline_result(self, pipeline_type: str, result: Dict[str, Any]) -> None:
        """Save pipeline result to project state"""
        state = ProjectState.load(self.project_name)
        state.add_pipeline_result(pipeline_type, result)