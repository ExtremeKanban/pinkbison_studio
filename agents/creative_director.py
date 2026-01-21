"""
Creative Director agent - provides high-level creative guidance.
Updated to use ModelClient for reliable model calls.
"""

import json
from typing import Optional, Dict, Any, List
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

    def analyze_scene_critique(self, issues: str, original_text: str) -> Dict[str, Any]:
        """
        Analyze a scene critique and extract canon rules.
        
        This is used by the orchestrator to process continuity critiques.
        
        Args:
            issues: Continuity issues found
            original_text: Original scene text
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Safely convert inputs to strings
            issues_str = str(issues) if issues is not None else ""
            original_text_str = str(original_text) if original_text is not None else ""
            
            # Build analysis prompt
            prompt = f"""
Analyze the following continuity critique and extract canon rules.

Continuity Issues:
{issues_str}

Original Scene:
{original_text_str[:1000]}

Provide:
1. Core problems identified
2. Proposed canon rules to prevent similar issues
3. Guidance for agents

Return as JSON with keys: core_problems, proposed_canon_rules, guidance
"""
            
            # Use ModelClient
            from models.model_client import ModelClient
            client = ModelClient(model_url=self.fast_model_url)
            
            response = client.complete_simple(prompt=prompt, temperature=0.7)
            
            # Ensure response is string
            response_str = str(response) if response else "{}"
            
            # Try to parse JSON
            import re
            
            # Extract JSON from response
            try:
                # Remove markdown code blocks
                clean = re.sub(r'```(?:json)?\s*', '', response_str)
                clean = re.sub(r'\s*```', '', clean).strip()
                
                if clean:
                    result = json.loads(clean)
                else:
                    result = {}
            except (json.JSONDecodeError, TypeError):
                # Fallback structure
                result = {
                    "core_problems": ["Could not parse LLM response"],
                    "proposed_canon_rules": ["Review critique manually"],
                    "guidance": response_str[:500] if response_str else "No guidance provided",
                }
            
            # Ensure all required fields exist
            return {
                "core_problems": result.get("core_problems", []),
                "proposed_canon_rules": result.get("proposed_canon_rules", []),
                "guidance": result.get("guidance", ""),
            }
            
        except Exception as e:
            # Comprehensive error handling
            self.audit_log.append(
                event_type="agent_error",
                sender=self.name,
                recipient="system",
                payload={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "method": "analyze_scene_critique",
                },
            )
            
            # Fallback result
            return {
                "core_problems": [f"Analysis error: {type(e).__name__}"],
                "proposed_canon_rules": [],
                "guidance": f"Error during analysis: {str(e)[:200]}",
            }
    
    def log_canon_rules(self, rules: List[str]) -> None:
        """
        Log canon rules to graph store.
        
        Args:
            rules: List of canon rule strings to log
        """
        if not rules:
            return
        
        # Filter out non-strings
        valid_rules = [str(r).strip() for r in rules if r and str(r).strip()]
        
        if not valid_rules:
            return
        
        # Get graph store
        from graph_store import GraphStore
        graph = GraphStore(self.project_name)
        
        for rule in valid_rules:
            # Add to graph
            import uuid
            rule_id = f"canon_rule_{uuid.uuid4().hex[:8]}"
            
            graph.add_canon_rule(
                rule_id=rule_id,
                rule=rule,
                scope=["general"],
                notes="Generated from continuity critique",
            )
        
        # Log action
        self.audit_log.append(
            event_type="agent_completion",
            sender=self.name,
            recipient="system",
            payload={"action": "canon_rules_logged", "count": len(valid_rules)},
        )
    
    def send_guidance_message(self, guidance: str) -> None:
        """
        Send guidance to agents via EventBus.
        
        Args:
            guidance: Guidance message to broadcast
        """
        if not guidance:
            return
        
        guidance_str = str(guidance).strip()
        if not guidance_str:
            return
        
        self.event_bus.publish(
            sender=self.name,
            recipient="ALL",
            event_type="creative_guidance",
            payload={"guidance": guidance_str},
        )
        
        # Also log to audit
        self.audit_log.append(
            event_type="agent_message",
            sender=self.name,
            recipient="ALL",
            payload={"type": "creative_guidance", "guidance": guidance_str[:200]},
        )

    async def analyze_scene_critique_async(self, issues: str, original_text: str) -> Dict[str, Any]:
        """
        Async version of analyze_scene_critique.
        """
        import asyncio
        
        # Run the synchronous method in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.analyze_scene_critique(issues, original_text)
        )
        
        return result