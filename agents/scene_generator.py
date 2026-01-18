"""
Scene Generator agent - creates detailed scene prose.
Updated to use ModelClient for reliable model calls.
"""

import json
from typing import Optional
from agents.base_agent import AgentBase
from models.model_client import ModelClient
from models.exceptions import ModelError


class SceneGenerator(AgentBase):
    """
    Scene Generator: Creates detailed scene prose from prompts.
    
    Responsibilities:
    - Write vivid scene descriptions
    - Develop dialogue and action
    - Maintain narrative voice
    
    Now uses ModelClient for reliable model calls with retry logic.
    """

    def run(
        self,
        scene_prompt: str,
        outline_snippet: str = "",
        world_notes: str = "",
        character_notes: str = "",
        auto_memory: bool = False,
    ) -> str:
        """
        Generate scene prose from prompt and context.

        Args:
            scene_prompt: Scene goal/description
            outline_snippet: Relevant plot context
            world_notes: World details for scene
            character_notes: Character details for scene
            auto_memory: If True, store results in memory

        Returns:
            Scene prose

        Raises:
            ModelError: If model call fails after retries
        """
        # Optional: search memory for relevant context
        memory_context = ""
        if auto_memory:
            memory_hits = self.memory.search(scene_prompt, k=5)
            if memory_hits:
                memory_context = "\n[Relevant Memory]:\n" + "\n".join(memory_hits)

        # Build prompt
        prompt = f"""
You are the Scene Generator. Write a detailed scene for the following.

Scene Goal: {scene_prompt}
Plot Context: {outline_snippet}
World Notes: {world_notes}
Character Notes: {character_notes}
{memory_context}

Write a vivid, engaging scene with:
- Clear setting and atmosphere
- Natural dialogue
- Character actions and reactions
- Sensory details
"""

        # Use ModelClient for reliable model call
        client = ModelClient(model_url=self.fast_model_url)
        
        try:
            scene_text = client.complete_simple(
                prompt=prompt,
                temperature=0.8
            )
        except ModelError as e:
            # Log error with details
            self.audit_log.append(
                event_type="agent_error_model",
                sender=self.name,
                recipient="system",
                payload={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "prompt_length": len(prompt),
                    "scene_prompt": scene_prompt[:100],
                },
            )
            raise

        # Emit success event
        self.event_bus.publish(
            sender=self.name,
            recipient="ALL",
            event_type="scene_generated",
            payload={"scene": scene_text},
        )

        # Log completion
        self.audit_log.append(
            event_type="agent_completion",
            sender=self.name,
            recipient="user",
            payload={"scene": scene_text[:200]},
        )

        # Store in memory if requested
        if auto_memory:
            self.memory.add(f"Scene generated: {scene_text[:300]}")

        return scene_text