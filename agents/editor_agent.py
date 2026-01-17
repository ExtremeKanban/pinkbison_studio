"""
Editor agent - polishes and improves scene prose.
Updated to use ModelClient for reliable model calls.
"""

import json
from typing import Optional
from agents.base_agent import AgentBase
from models.model_client import ModelClient
from models.exceptions import ModelError


class EditorAgent(AgentBase):
    """
    Editor Agent: Polishes and improves scene prose.
    
    Responsibilities:
    - Improve prose quality
    - Enhance descriptions
    - Refine dialogue
    - Fix grammar and style
    
    Now uses ModelClient for reliable model calls with retry logic.
    """

    def run(
        self,
        scene_text: str,
        notes: str = "",
        auto_memory: bool = False,
    ) -> str:
        """
        Edit and polish scene prose.

        Args:
            scene_text: Scene to edit
            notes: Editing notes or guidelines
            auto_memory: If True, store results in memory

        Returns:
            Polished scene text

        Raises:
            ModelError: If model call fails after retries
        """
        # Optional: search memory for style guidelines
        memory_context = ""
        if auto_memory:
            memory_hits = self.memory.search("writing style editing", k=3)
            if memory_hits:
                memory_context = "\n[Style Guidelines]:\n" + "\n".join(memory_hits)

        # Build prompt
        prompt = f"""
You are the Editor Agent. Polish and improve the following scene.

Scene: {scene_text}
Notes: {notes}
{memory_context}

Improve:
- Prose clarity and flow
- Dialogue naturalness
- Descriptive language
- Grammar and style
- Pacing

Maintain:
- Original plot and events
- Character voices
- Scene structure

Provide the polished scene.
"""

        # Use ModelClient for reliable model call
        client = ModelClient(model_url=self.fast_model_url)
        
        try:
            edited_scene = client.complete_simple(
                prompt=prompt,
                temperature=0.7
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
                },
            )
            raise

        # Emit success event
        self.event_bus.emit(
            event_type="scene_edited",
            sender=self.name,
            recipient="broadcast",
            payload={"edited_scene": edited_scene},
        )

        # Log completion
        self.audit_log.append(
            event_type="agent_completion",
            sender=self.name,
            recipient="user",
            payload={"edited_scene": edited_scene[:200]},
        )

        # Store in memory if requested
        if auto_memory:
            self.memory.add(f"Scene edited and polished")

        return edited_scene