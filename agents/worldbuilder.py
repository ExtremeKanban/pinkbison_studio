"""
Worldbuilder agent - creates world bibles and setting details.
Updated to use ModelClient for reliable model calls.
"""

import json
from typing import Optional
from agents.base_agent import AgentBase
from models.model_client import ModelClient
from models.exceptions import ModelError


class Worldbuilder(AgentBase):
    """
    Worldbuilder: Creates detailed world bibles and setting information.
    
    Responsibilities:
    - Define world rules and systems
    - Create setting details
    - Establish worldbuilding consistency
    
    Now uses ModelClient for reliable model calls with retry logic.
    """

    def run(
        self,
        outline: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = False,
    ) -> str:
        """
        Generate world bible from story outline.

        Args:
            outline: Plot outline to base world on
            genre: Story genre
            tone: Desired tone
            themes: Key themes
            setting: Initial setting notes
            auto_memory: If True, store results in memory

        Returns:
            World bible document

        Raises:
            ModelError: If model call fails after retries
        """
        # Optional: search memory for relevant world details
        memory_context = ""
        if auto_memory:
            memory_hits = self.memory.search(f"{genre} {setting}", k=5)
            if memory_hits:
                memory_context = "\n[Relevant Memory]:\n" + "\n".join(memory_hits)

        # Build prompt
        prompt = f"""
You are the Worldbuilder. Create a detailed world bible for the following story.

Outline: {outline}
Genre: {genre}
Tone: {tone}
Themes: {themes}
Setting: {setting}
{memory_context}

Provide a comprehensive world bible covering:
- Geography and locations
- History and timeline
- Culture and society
- Magic/technology systems (if applicable)
- Key world rules and constraints
"""

        # Use ModelClient for reliable model call
        client = ModelClient(model_url=self.fast_model_url)
        
        try:
            world_doc = client.complete_simple(
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
                    "genre": genre,
                },
            )
            raise

        # Emit success event
        self.event_bus.publish(
            sender=self.name,
            recipient="ALL",
            event_type="world_bible_generated",
            payload={"world": world_doc},
        )

        # Log completion
        self.audit_log.append(
            event_type="agent_completion",
            sender=self.name,
            recipient="user",
            payload={"world": world_doc[:200]},
        )

        # Store in memory if requested
        if auto_memory:
            self.memory.add(f"World bible created: {world_doc[:300]}")

        return world_doc