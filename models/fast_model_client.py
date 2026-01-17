"""
Fast model client using vLLM server with centralized configuration.
"""

import requests
from typing import List, Dict, Any
from config.settings import MODEL_CONFIG


def chat_fast(messages: List[Dict[str, str]], model: str = None) -> str:
    """
    Send chat completion request to fast model server.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name (defaults to configured fast model)
        
    Returns:
        Generated text content
        
    Raises:
        requests.HTTPError: If request fails
    """
    model = model or MODEL_CONFIG.fast_model_name
    
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    
    response = requests.post(MODEL_CONFIG.fast_model_url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    return data["choices"][0]["message"]["content"]