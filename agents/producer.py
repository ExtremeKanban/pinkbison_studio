"""
ProducerAgent orchestrates multi-step creative pipelines.

Does NOT inherit from AgentBase.
Creates fresh agent instances via AgentFactory for each pipeline step.
Now includes async methods for real-time execution.
"""

import time
import asyncio
from typing import Dict, Any, List

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
    Now includes async methods for real-time execution with feedback.
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
    # Story Bible Pipeline (Synchronous - original)
    # ---------------------------------------------------------
    def run_story_bible_pipeline(self, idea: str, genre: str, tone: str,
                                 themes: str, setting: str,
                                 auto_memory: bool = True) -> dict:
        """
        Generate story bible (outline, world, characters).
        
        Creates fresh agent instances for each step.
        """
        # Get pipeline controller for progress updates
        from core.registry import REGISTRY
        pipeline_controller = REGISTRY.get_pipeline_controller(self.project_name)
        
        # 1) Outline
        pipeline_controller.update_progress(
            step_number=1,
            current_step="plot_outline",
            step_description="Generating 3-act plot outline"
        )
        
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
        pipeline_controller.update_progress(
            step_number=2,
            current_step="world_bible",
            step_description="Building world bible"
        )
        
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
        pipeline_controller.update_progress(
            step_number=3,
            current_step="character_bible",
            step_description="Creating character bible"
        )
        
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
    # Story Bible Pipeline (Async - NEW)
    # ---------------------------------------------------------
    async def run_story_bible_pipeline_async(
        self,
        idea: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = True
    ) -> dict:
        """
        Async version of story bible generation with progress updates.
        """
        # Get pipeline controller
        from core.registry import REGISTRY
        pipeline_controller = REGISTRY.get_pipeline_controller(self.project_name)
        
        # Publish start event
        self.event_bus.publish(
            sender="producer",
            recipient="ALL",
            event_type="pipeline_start",
            payload={
                "pipeline": "story_bible",
                "idea": idea[:100],
                "timestamp": time.time()
            }
        )
        
        try:
            # 1) Outline
            pipeline_controller.update_progress(
                current_step="plot_outline",
                step_number=1,
                step_description="Generating 3-act plot outline"
            )
            
            # Check for stop/pause
            if not pipeline_controller.wait_for_resume():
                return {"status": "stopped", "step": "plot_outline"}
            
            plot_agent = self.agent_factory.create_plot_architect()
            outline = await self._run_agent_with_feedback(
                agent=plot_agent,
                method_name="run",
                step_name="plot_outline",
                idea=idea,
                genre=genre,
                tone=tone,
                themes=themes,
                setting=setting,
                auto_memory=auto_memory
            )
            
            # 2) World
            pipeline_controller.update_progress(
                current_step="world_bible",
                step_number=2,
                step_description="Building world bible"
            )
            
            if not pipeline_controller.wait_for_resume():
                return {"status": "stopped", "step": "world_bible"}
            
            world_agent = self.agent_factory.create_worldbuilder()
            world_doc = await self._run_agent_with_feedback(
                agent=world_agent,
                method_name="run",
                step_name="world_bible",
                outline=outline,
                genre=genre,
                tone=tone,
                themes=themes,
                setting=setting,
                auto_memory=auto_memory
            )
            
            # 3) Characters
            pipeline_controller.update_progress(
                current_step="character_bible",
                step_number=3,
                step_description="Creating character bible"
            )
            
            if not pipeline_controller.wait_for_resume():
                return {"status": "stopped", "step": "character_bible"}
            
            char_agent = self.agent_factory.create_character_agent()
            character_doc = await self._run_agent_with_feedback(
                agent=char_agent,
                method_name="run",
                step_name="character_bible",
                outline=outline,
                world_notes=world_doc,
                auto_memory=auto_memory
            )
            
            result = {
                "outline": outline,
                "world": world_doc,
                "characters": character_doc,
            }
            
            # Save to pipeline history
            self._save_pipeline_result("story_bible", result)
            
            # Publish completion
            self.event_bus.publish(
                sender="producer",
                recipient="ALL",
                event_type="pipeline_complete",
                payload={
                    "pipeline": "story_bible",
                    "status": "success",
                    "result_size": len(str(result))
                }
            )
            
            return result
            
        except Exception as e:
            # Log error
            self.event_bus.publish(
                sender="producer",
                recipient="ALL",
                event_type="pipeline_error",
                payload={
                    "pipeline": "story_bible",
                    "error": str(e),
                    "timestamp": time.time()
                }
            )
            raise

    # ---------------------------------------------------------
    # Chapter Planning (Synchronous - original)
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

    # ---------------------------------------------------------
    # Chapter Generation (Synchronous - original)
    # ---------------------------------------------------------
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
    # Chapter Generation (Async - NEW)
    # ---------------------------------------------------------
    async def _generate_chapter_from_plan_async(
        self,
        chapter_plan: dict,
        outline: str,
        world_doc: str,
        character_doc: str,
        auto_memory: bool = True,
        run_continuity: bool = True,
        run_editor: bool = True
    ) -> dict:
        """
        Async version of chapter generation.
        """
        from core.registry import REGISTRY
        
        pipeline_controller = REGISTRY.get_pipeline_controller(self.project_name)
        
        title = chapter_plan.get("title", "Untitled Chapter")
        beats = chapter_plan.get("beats", []) or []
        
        scenes = []
        total_beats = len(beats)
        
        for beat_idx, beat in enumerate(beats):
            # Update progress for each scene
            pipeline_controller.update_progress(
                current_step=f"scene_{beat_idx + 1}",
                step_number=beat_idx + 1,
                step_description=f"Writing scene: {beat[:50]}..."
            )
            
            if not pipeline_controller.wait_for_resume():
                return {"status": "stopped", "scenes_completed": beat_idx}
            
            # Check for feedback before generating scene
            feedback_manager = pipeline_controller.feedback_manager
            feedback = feedback_manager.get_feedback_for_agent("scene_generator")
            
            # Incorporate feedback if available
            enhanced_prompt = beat
            if feedback:
                for fb in feedback[:3]:  # Use top 3 feedback items
                    enhanced_prompt += f"\n\nFeedback: {fb.content}"
                    feedback_manager.mark_as_processed(fb.id)
            
            scene_generator = self.agent_factory.create_scene_generator()
            scene_text = await self._run_agent_with_feedback(
                agent=scene_generator,
                method_name="run",
                step_name=f"scene_{beat_idx}",
                scene_prompt=enhanced_prompt,
                outline_snippet=f"{title}\n{outline}",
                world_notes=world_doc,
                character_notes=character_doc,
                auto_memory=auto_memory
            )
            scenes.append(scene_text)
        
        chapter_raw = "\n\n".join(scenes)
        
        chapter_after_continuity = chapter_raw
        if run_continuity:
            pipeline_controller.update_progress(
                current_step="continuity_check",
                step_number=total_beats + 1,
                step_description="Running continuity checks"
            )
            
            continuity_agent = self.agent_factory.create_continuity_agent()
            chapter_after_continuity = await self._run_agent_with_feedback(
                agent=continuity_agent,
                method_name="run",
                step_name="continuity_check",
                scene_text=chapter_raw
            )
        
        chapter_final = chapter_after_continuity
        if run_editor:
            pipeline_controller.update_progress(
                current_step="editor_polish",
                step_number=total_beats + 2,
                step_description="Polishing with editor"
            )
            
            editor_agent = self.agent_factory.create_editor_agent()
            chapter_final = await self._run_agent_with_feedback(
                agent=editor_agent,
                method_name="run",
                step_name="editor_polish",
                scene_text=chapter_after_continuity
            )
        
        return {
            "title": title,
            "raw": chapter_raw,
            "after_continuity": chapter_after_continuity,
            "final": chapter_final,
        }

    # ---------------------------------------------------------
    # Chapter Pipeline (Synchronous - original)
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
    # Chapter Pipeline (Async - NEW)
    # ---------------------------------------------------------
    async def run_chapter_pipeline_async(
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
        max_chapters: int = 20
    ) -> dict:
        """
        Async version of chapter pipeline.
        """
        from core.registry import REGISTRY
        
        pipeline_controller = REGISTRY.get_pipeline_controller(self.project_name)
        
        # Start with story bible
        pipeline_controller.update_progress(
            current_step="story_bible",
            step_number=1,
            step_description="Generating story foundation"
        )
        
        bible = await self.run_story_bible_pipeline_async(
            idea=idea,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory
        )
        
        if not pipeline_controller.wait_for_resume():
            return {"status": "stopped", "step": "story_bible"}
        
        outline = bible["outline"]
        world_doc = bible["world"]
        character_doc = bible["characters"]
        
        # Plan chapters
        pipeline_controller.update_progress(
            current_step="chapter_planning",
            step_number=2,
            step_description="Planning chapter structure"
        )
        
        if not pipeline_controller.wait_for_resume():
            return {"status": "stopped", "step": "chapter_planning"}
        
        plan = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.plan_chapters_from_outline(outline, max_chapters)
        )
        
        chapters = plan.get("chapters", [])
        if not chapters:
            raise ValueError("Chapter plan has no chapters.")
        
        chapter_index = max(0, min(chapter_index, len(chapters) - 1))
        chapter_plan = chapters[chapter_index]
        
        # Generate chapter
        pipeline_controller.update_progress(
            current_step="chapter_generation",
            step_number=3,
            step_description="Writing chapter content"
        )
        
        if not pipeline_controller.wait_for_resume():
            return {"status": "stopped", "step": "chapter_generation"}
        
        chapter_result = await self._generate_chapter_from_plan_async(
            chapter_plan,
            outline=outline,
            world_doc=world_doc,
            character_doc=character_doc,
            auto_memory=auto_memory,
            run_continuity=run_continuity,
            run_editor=run_editor
        )
        
        # Save chapter
        pipeline_controller.update_progress(
            current_step="saving_outputs",
            step_number=4,
            step_description="Saving chapter to outputs"
        )
        
        self.output_manager.save_chapter(chapter_index, chapter_result)
        
        result = {
            "outline": outline,
            "world": world_doc,
            "characters": character_doc,
            "plan": plan,
            "chapter_index": chapter_index,
            "chapter": chapter_result,
        }
        
        # Save to pipeline history
        self._save_pipeline_result("chapter", result)
        
        pipeline_controller.update_progress(
            current_step="complete",
            step_number=5,
            step_description="Chapter pipeline complete"
        )
        
        return result

    # ---------------------------------------------------------
    # Full Story Pipeline (Synchronous - original)
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
    # Full Story Pipeline (Async - NEW)
    # ---------------------------------------------------------
    async def run_full_story_pipeline_async(
        self,
        idea: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = True,
        run_continuity: bool = True,
        run_editor: bool = True,
        max_chapters: int = 20
    ) -> dict:
        """
        Async version of full story pipeline.
        """
        from core.registry import REGISTRY
        
        pipeline_controller = REGISTRY.get_pipeline_controller(self.project_name)
        
        # Start with story bible
        pipeline_controller.update_progress(
            current_step="story_bible",
            step_number=1,
            step_description="Generating story foundation"
        )
        
        bible = await self.run_story_bible_pipeline_async(
            idea=idea,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory
        )
        
        if not pipeline_controller.wait_for_resume():
            return {"status": "stopped", "step": "story_bible"}
        
        outline = bible["outline"]
        world_doc = bible["world"]
        character_doc = bible["characters"]
        
        # Plan chapters
        pipeline_controller.update_progress(
            current_step="chapter_planning",
            step_number=2,
            step_description="Planning chapter structure"
        )
        
        if not pipeline_controller.wait_for_resume():
            return {"status": "stopped", "step": "chapter_planning"}
        
        plan = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.plan_chapters_from_outline(outline, max_chapters)
        )
        
        chapters_plan = plan.get("chapters", [])
        if not chapters_plan:
            raise ValueError("Chapter plan has no chapters.")
        
        # Generate all chapters
        chapters = []
        total_chapters = len(chapters_plan)
        
        for idx, chapter_plan in enumerate(chapters_plan):
            pipeline_controller.update_progress(
                current_step=f"chapter_{idx + 1}",
                step_number=idx + 1,
                step_description=f"Generating chapter {idx + 1}/{total_chapters}: {chapter_plan.get('title', 'Untitled')}"
            )
            
            if not pipeline_controller.wait_for_resume():
                return {"status": "stopped", "chapters_completed": idx}
            
            chapter_result = await self._generate_chapter_from_plan_async(
                chapter_plan,
                outline=outline,
                world_doc=world_doc,
                character_doc=character_doc,
                auto_memory=auto_memory,
                run_continuity=run_continuity,
                run_editor=run_editor
            )
            
            chapters.append(chapter_result)
            
            # Save chapter as we go
            self.output_manager.save_chapter(idx, chapter_result)
        
        # Combine into full story
        pipeline_controller.update_progress(
            current_step="combining_story",
            step_number=total_chapters + 1,
            step_description="Combining chapters into full story"
        )
        
        full_story_text = "\n\n".join(ch["final"] for ch in chapters)
        
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
    # Director Mode (Synchronous - original)
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
    # Director Mode (Async - NEW)
    # ---------------------------------------------------------
    async def run_director_mode_async(
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
        max_revision_passes: int = 2
    ) -> dict:
        """
        Async version of director mode.
        """
        from core.registry import REGISTRY
        
        pipeline_controller = REGISTRY.get_pipeline_controller(self.project_name)
        
        # Generate base story
        pipeline_controller.update_progress(
            current_step="base_story",
            step_number=1,
            step_description="Generating base story"
        )
        
        base = await self.run_full_story_pipeline_async(
            idea=idea,
            genre=genre,
            tone=tone,
            themes=themes,
            setting=setting,
            auto_memory=auto_memory,
            run_continuity=run_continuity,
            run_editor=run_editor,
            max_chapters=max_chapters
        )
        
        if not pipeline_controller.wait_for_resume():
            return {"status": "stopped", "step": "base_story"}
        
        chapters = base["chapters"]
        
        # Revision passes
        for pass_idx in range(max_revision_passes):
            pipeline_controller.update_progress(
                current_step=f"revision_pass_{pass_idx + 1}",
                step_number=pass_idx + 2,
                step_description=f"Director revision pass {pass_idx + 1}/{max_revision_passes}"
            )
            
            if not pipeline_controller.wait_for_resume():
                return {"status": "stopped", "revision_pass": pass_idx}
            
            revised = []
            total_chapters = len(chapters)
            
            for ch_idx, ch in enumerate(chapters):
                # Update progress per chapter
                pipeline_controller.update_progress(
                    current_step=f"revision_pass_{pass_idx + 1}_chapter_{ch_idx + 1}",
                    step_number=ch_idx + 1,
                    step_description=f"Revising chapter {ch_idx + 1}/{total_chapters}"
                )
                
                text = ch.get("final") or ch.get("after_continuity") or ch.get("raw") or ""
                if not text.strip():
                    revised.append(ch)
                    continue
                
                # Check for feedback before editing
                feedback_manager = pipeline_controller.feedback_manager
                feedback = feedback_manager.get_feedback_for_agent("editor_agent")
                
                editor_agent = self.agent_factory.create_editor_agent()
                revised_text = await self._run_agent_with_feedback(
                    agent=editor_agent,
                    method_name="run",
                    step_name=f"revision_{pass_idx}_{ch_idx}",
                    scene_text=text
                )
                
                new_ch = dict(ch)
                new_ch["final"] = revised_text
                revised.append(new_ch)
            
            chapters = revised
        
        # Final combination
        pipeline_controller.update_progress(
            current_step="final_assembly",
            step_number=max_revision_passes + 1,
            step_description="Assembling final story"
        )
        
        full_story_text = "\n\n".join(ch["final"] for ch in chapters)
        
        # Save final outputs
        for idx, chapter in enumerate(chapters):
            self.output_manager.save_chapter(idx, chapter)
        
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
    # Helper Methods (NEW)
    # ---------------------------------------------------------
    async def _run_agent_with_feedback(self, agent, method_name: str, step_name: str, **kwargs):
        """
        Run an agent method with feedback checking and progress updates.
        """
        from core.registry import REGISTRY
        
        pipeline_controller = REGISTRY.get_pipeline_controller(self.project_name)
        
        # Check for feedback specific to this agent
        feedback_manager = pipeline_controller.feedback_manager
        feedback = feedback_manager.get_feedback_for_agent(agent.name)
        
        # Incorporate feedback into kwargs if available
        if feedback:
            # Add feedback as a parameter if the method accepts it
            try:
                if 'feedback' in agent.run.__code__.co_varnames:
                    kwargs['feedback'] = [fb.content for fb in feedback[:3]]
            except AttributeError:
                pass  # Agent doesn't have run method or it's not a function
        
        # Mark feedback as processed
        for fb in feedback[:3]:
            feedback_manager.mark_as_processed(fb.id)
        
        # Run the agent method
        method = getattr(agent, method_name)
        
        # Run in thread pool (since agent methods are synchronous)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: method(**kwargs)
        )
        
        # Publish completion event
        self.event_bus.publish(
            sender="producer",
            recipient="ALL",
            event_type="agent_step_complete",
            payload={
                "agent": agent.name,
                "step": step_name,
                "result_length": len(str(result)) if result else 0
            }
        )
        
        return result

    def handle_feedback(self, agent_name: str, feedback_text: str) -> None:
        """
        Send feedback to an agent via EventBus.
        
        Agent will receive it on next pipeline run.
        """
        self.event_bus.publish(
            sender="producer",
            recipient=agent_name,
            event_type="user_feedback",
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

    def get_continuity_critiques(self):
        """
        Get CRITIQUE messages from continuity agent.
        
        This is used by the orchestrator to ingest critiques into tasks.
        Returns empty list if not implemented.
        """
        # For now, return empty list
        # In the future, this would query EventBus for CRITIQUE messages
        return []