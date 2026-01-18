"""
Plot Architect agent - generates 3-act story outlines.
Updated to use ModelClient for reliable model calls.
"""

import json
from typing import Optional
from agents.base_agent import AgentBase
from models.model_client import ModelClient
from models.exceptions import ModelError


class PlotArchitect(AgentBase):
    """
    Plot Architect: Generates structured 3-act outlines from story ideas.
    
    Responsibilities:
    - Create coherent story structure
    - Define major plot points and turning points
    - Establish narrative arc
    
    Now uses ModelClient for:
    - Automatic retry on failures
    - Proper error handling
    - Timeout management
    """

    def run(
        self,
        idea: str,
        genre: str,
        tone: str,
        themes: str,
        setting: str,
        auto_memory: bool = False,
    ) -> str:
        """
        Generate a 3-act outline from a story idea.

        Args:
            idea: Core story concept
            genre: Story genre (e.g., "sci-fi", "fantasy")
            tone: Desired tone (e.g., "dark", "lighthearted")
            themes: Key themes to explore
            setting: Story setting/world
            auto_memory: If True, store results in memory

        Returns:
            3-act outline as text

        Raises:
            ModelError: If model call fails after retries
        """
        # Optional: search memory for relevant context
        memory_context = ""
        if auto_memory:
            memory_hits = self.memory.search(idea, k=5)
            if memory_hits:
                memory_context = "\n[Relevant Memory]:\n" + "\n".join(memory_hits)

        # Build prompt
        prompt = f"""
You are the Plot Architect. Create a 3-act outline for the following story idea.

Idea: {idea}
Genre: {genre}
Tone: {tone}
Themes: {themes}
Setting: {setting}
{memory_context}

Provide a structured 3-act outline with clear turning points.
Format:
ACT 1: Setup
- [Opening scene/hook]
- [Inciting incident]
- [First act turning point]

ACT 2: Confrontation
- [Rising action]
- [Midpoint twist]
- [Second act turning point]

ACT 3: Resolution
- [Climax]
- [Falling action]
- [Resolution]
"""

        # Use ModelClient for reliable model call
        client = ModelClient(model_url=self.fast_model_url)
        
        try:
            outline = client.complete_simple(
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
                    "idea": idea[:100],
                },
            )
            # Re-raise so caller knows it failed
            raise

        # Emit success event
        self.event_bus.publish(
            sender=self.name,
            recipient="broadcast",
            msg_type="plot_outline_generated",
            payload={"outline": outline},
        )

        # Log completion
        self.audit_log.append(
            event_type="agent_completion",
            sender=self.name,
            recipient="user",
            payload={"outline": outline[:200]},  # First 200 chars
        )

        # Store in memory if requested
        if auto_memory:
            self.memory.add(f"Plot outline created: {outline[:300]}")

        return outline