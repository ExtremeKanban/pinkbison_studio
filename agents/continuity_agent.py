"""
Continuity agent - checks for plot/world consistency.
Updated to use ModelClient for reliable model calls.
"""

import json
from typing import Optional
from agents.base_agent import AgentBase
from models.model_client import ModelClient
from models.exceptions import ModelError


class ContinuityAgent(AgentBase):
    """
    Continuity Agent: Checks for consistency in plot, world, and characters.
    
    Responsibilities:
    - Detect continuity errors
    - Verify world rule consistency
    - Check character behavior consistency
    
    Now uses ModelClient for reliable model calls with retry logic.
    """

    def run(
        self,
        scene_text: str,
        context: str = "",
        auto_memory: bool = False,
    ) -> str:
        """
        Check scene for continuity issues and provide corrections.

        Args:
            scene_text: Scene to check
            context: World/character context for checking
            auto_memory: If True, store results in memory

        Returns:
            Continuity report with corrections

        Raises:
            ModelError: If model call fails after retries
        """
        # Optional: search memory for continuity issues
        memory_context = ""
        if auto_memory:
            memory_hits = self.memory.search(scene_text[:200], k=5)
            if memory_hits:
                memory_context = "\n[Relevant Memory]:\n" + "\n".join(memory_hits)

        # Build prompt
        prompt = f"""
You are the Continuity Agent. Review the following scene for consistency issues.

Scene: {scene_text}
Context: {context}
{memory_context}

Check for:
- Plot consistency with established story
- Character behavior consistency
- World rule violations
- Timeline contradictions
- Factual errors

If issues found, provide:
1. List of specific issues
2. Suggested corrections
3. Revised scene (if needed)

If no issues, respond: "CONTINUITY CHECK PASSED"
"""

        # Use ModelClient for reliable model call
        client = ModelClient(model_url=self.fast_model_url)
        
        try:
            continuity_report = client.complete_simple(
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
        self.event_bus.publish(
            sender=self.name,
            recipient="ALL",
            event_type="continuity_check_complete",
            payload={"report": continuity_report},
        )

        # Log completion
        self.audit_log.append(
            event_type="agent_completion",
            sender=self.name,
            recipient="user",
            payload={"report": continuity_report[:200]},
        )

        # Store in memory if requested
        if auto_memory:
            if "PASSED" not in continuity_report:
                self.memory.add(f"Continuity issues found: {continuity_report[:300]}")

        return continuity_report