import requests
from typing import List, Dict, Any


FAST_MODEL_URL = "http://localhost:8000/v1/chat/completions"
FAST_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"


def chat_fast(messages: List[Dict[str, str]], model: str = FAST_MODEL_NAME) -> str:
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    response = requests.post(FAST_MODEL_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
