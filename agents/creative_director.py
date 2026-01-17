"""
Creative Director agent - provides high-level creative guidance.
Updated to use ModelClient for reliable model calls.
"""

import json
from typing import Optional, Dict, Any
from agents.base_agent import AgentBase
from models.model_client import ModelClient
from models.exceptions import ModelError


class CreativeDirectorAgent(AgentBase):
    """
    Creative Director: Provides high-level creative oversight and guidance.
    
    Responsibilities:
    - Evaluate creative quality
    - Provide artistic direction
    - Ensure thematic consistency
    - Guide overall vision
    
    Now uses ModelClient for reliable model calls with retry logic.
    """

    def evaluate_pipeline_output(
        self,
        outline: str,
        world: str,
        characters: str,
    ) -> Dict[str, Any]:
        """
        Evaluate story bible pipeline output.

        Args:
            outline: Generated plot outline
            world: Generated world bible
            characters: Generated character bible

        Returns:
            Dictionary with evaluation and suggestions

        Raises:
            ModelError: If model call fails after retries
        """
        # Build evaluation prompt
        prompt = f"""
You are the Creative Director. Evaluate the following story bible components.

OUTLINE:
{outline}

WORLD:
{world}

CHARACTERS:
{characters}

Evaluate:
1. Overall coherence and quality
2. Thematic consistency
3. Character depth and arcs
4. World richness and logic
5. Plot structure and pacing

Provide:
- Overall score (1-10)
- Strengths
- Weaknesses
- Specific improvement suggestions

Format as JSON:
{{
    "score": <number>,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "suggestions": ["suggestion1", "suggestion2"]
}}
"""

        # Use ModelClient for reliable model call
        client = ModelClient(model_url=self.fast_model_url)
        
        try:
            evaluation_text = client.complete_simple(
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

        # Try to parse JSON response
        try:
            evaluation = json.loads(evaluation_text)
        except json.JSONDecodeError:
            # If not valid JSON, create simple structure
            evaluation = {
                "score": 7,
                "strengths": ["Generated successfully"],
                "weaknesses": ["Response not in JSON format"],
                "suggestions": ["Re-run evaluation"],
                "raw_response": evaluation_text,
            }

        # Emit evaluation event
        self.event_bus.emit(
            event_type="creative_evaluation_complete",
            sender=self.name,
            recipient="broadcast",
            payload=evaluation,
        )

        # Log completion
        self.audit_log.append(
            event_type="agent_completion",
            sender=self.name,
            recipient="user",
            payload={"evaluation": evaluation},
        )

        return evaluation

    def provide_guidance(
        self,
        context: str,
        question: str,
    ) -> str:
        """
        Provide creative guidance for a specific question.

        Args:
            context: Relevant story/project context
            question: Creative question to answer

        Returns:
            Creative guidance response

        Raises:
            ModelError: If model call fails after retries
        """
        # Build guidance prompt
        prompt = f"""
You are the Creative Director. Provide creative guidance.

CONTEXT:
{context}

QUESTION:
{question}

Provide thoughtful, actionable creative guidance that:
- Addresses the question directly
- Considers artistic merit
- Suggests concrete next steps
- Maintains story vision
"""

        # Use ModelClient for reliable model call
        client = ModelClient(model_url=self.fast_model_url)
        
        try:
            guidance = client.complete_simple(
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
                    "question": question[:100],
                },
            )
            raise

        # Emit guidance event
        self.event_bus.emit(
            event_type="creative_guidance_provided",
            sender=self.name,
            recipient="broadcast",
            payload={"guidance": guidance},
        )

        # Log completion
        self.audit_log.append(
            event_type="agent_completion",
            sender=self.name,
            recipient="user",
            payload={"guidance": guidance[:200]},
        )

        return guidance