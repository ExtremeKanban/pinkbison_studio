"""
Unified model client with retry logic and error handling.
Replaces scattered model call code throughout the codebase.
"""

import time
import requests
from typing import List, Dict, Any, Optional
from config.settings import MODEL_CONFIG
from models.exceptions import (
    ModelError,
    ModelTimeoutError,
    ModelResponseError,
    ModelServerError,
    ModelConnectionError,
)


class ModelClient:
    """
    Unified client for model completions.
    
    Features:
    - Automatic retry with exponential backoff
    - Proper error handling and exceptions
    - Timeout management
    - Consistent interface
    
    Example:
        >>> client = ModelClient()
        >>> result = client.complete(
        ...     messages=[{"role": "user", "content": "Hello"}]
        ... )
    """
    
    def __init__(
        self,
        model_url: str = None,
        timeout: int = None,
        max_retries: int = 3,
    ):
        """
        Initialize model client.
        
        Args:
            model_url: Model server URL (defaults to config)
            timeout: Request timeout in seconds (defaults to config)
            max_retries: Maximum retry attempts
        """
        self.model_url = model_url or MODEL_CONFIG.fast_model_url
        self.timeout = timeout or MODEL_CONFIG.request_timeout
        self.max_retries = max_retries
    
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """
        Send completion request with retry logic.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to config)
            temperature: Sampling temperature (defaults to config)
            max_tokens: Max tokens to generate (defaults to config)
            
        Returns:
            Generated text content
            
        Raises:
            ModelTimeoutError: If request times out after retries
            ModelResponseError: If response is invalid
            ModelServerError: If server returns error status
            ModelConnectionError: If can't connect to server
            
        Example:
            >>> client = ModelClient()
            >>> result = client.complete(
            ...     messages=[{"role": "user", "content": "Write a haiku"}],
            ...     temperature=0.9
            ... )
        """
        model = model or MODEL_CONFIG.fast_model_name
        temperature = temperature or MODEL_CONFIG.default_temperature
        max_tokens = max_tokens or MODEL_CONFIG.default_max_tokens
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.model_url,
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=self.timeout,
                )
                
                # Check for server errors (5xx) - these are retriable
                if response.status_code >= 500:
                    if attempt == self.max_retries - 1:
                        # Last attempt - raise error
                        raise ModelServerError(
                            f"Server error {response.status_code} after {self.max_retries} attempts: {response.text}"
                        )
                    # Retry with backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                
                # Check for other HTTP errors (4xx) - these are NOT retriable
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # Validate response structure
                if "choices" not in data or not data["choices"]:
                    raise ModelResponseError(
                        f"Invalid response structure: {data}"
                    )
                
                content = data["choices"][0]["message"]["content"]
                
                if not content or not content.strip():
                    raise ModelResponseError("Empty response content")
                
                return content
                
            except requests.Timeout:
                if attempt == self.max_retries - 1:
                    raise ModelTimeoutError(
                        f"Model timed out after {self.max_retries} attempts"
                    )
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                
            except requests.ConnectionError as e:
                raise ModelConnectionError(
                    f"Failed to connect to model server at {self.model_url}: {e}"
                ) from e
                
            except requests.HTTPError as e:
                # Client errors (4xx) - don't retry
                raise ModelServerError(
                    f"Model server error {e.response.status_code}: {e.response.text}"
                ) from e
                    
            except (KeyError, IndexError, ValueError) as e:
                raise ModelResponseError(
                    f"Failed to parse model response: {e}"
                ) from e
        
        # Should never reach here, but just in case
        raise ModelError("Unexpected error in model completion")
    
    def complete_simple(self, prompt: str, **kwargs) -> str:
        """
        Simplified interface for single-turn prompts.
        
        Args:
            prompt: User prompt text
            **kwargs: Additional arguments for complete()
            
        Returns:
            Generated text
            
        Example:
            >>> client = ModelClient()
            >>> result = client.complete_simple("Write a haiku")
        """
        messages = [{"role": "user", "content": prompt}]
        return self.complete(messages, **kwargs)