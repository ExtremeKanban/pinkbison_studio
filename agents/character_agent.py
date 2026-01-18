"""
Character agent - creates character bibles and profiles.
Updated to use ModelClient for reliable model calls.
"""

import json
from typing import Optional
from agents.base_agent import AgentBase
from models.model_client import ModelClient
from models.exceptions import ModelError


class CharacterAgent(AgentBase):
    """
    Character Agent: Creates detailed character profiles and bibles.
    
    Responsibilities:
    - Define character personalities and arcs
    - Create character backstories
    - Establish character relationships
    
    Now uses ModelClient for reliable model calls with retry logic.
    """

    def run(
        self,
        outline: str,
        world_notes: str = "",
        auto_memory: bool = False,
    ) -> str:
        """
        Generate character bible from outline and world notes.

        Args:
            outline: Plot outline with character roles
            world_notes: World bible for context
            auto_memory: If True, store results in memory

        Returns:
            Character bible document

        Raises:
            ModelError: If model call fails after retries
        """
        # Optional: search memory for character-related context
        memory_context = ""
        if auto_memory:
            memory_hits = self.memory.search(outline[:200], k=5)
            if memory_hits:
                memory_context = "\n[Relevant Memory]:\n" + "\n".join(memory_hits)

        # Build prompt
        prompt = f"""
You are the Character Agent. Create detailed character profiles for the following story.

Outline: {outline}
World Notes: {world_notes}
{memory_context}

For each major character, provide:
- Name and role
- Physical description
- Personality traits
- Backstory and motivations
- Character arc
- Key relationships
- Unique quirks or flaws
"""

        # Use ModelClient for reliable model call
        client = ModelClient(model_url=self.fast_model_url)
        
        try:
            characters_doc = client.complete_simple(
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
                },
            )
            raise

        # Emit success event
        self.event_bus.publish(
            sender=self.name,
            recipient="ALL",
            event_type="character_bible_generated",
            payload={"characters": characters_doc},
        )

        # Log completion
        self.audit_log.append(
            event_type="agent_completion",
            sender=self.name,
            recipient="user",
            payload={"characters": characters_doc[:200]},
        )

        # Store in memory if requested
        if auto_memory:
            self.memory.add(f"Character bible created: {characters_doc[:300]}")

        return characters_doc