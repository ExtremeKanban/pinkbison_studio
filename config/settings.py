"""
Centralized configuration management.
All configuration values are defined here as constants.
"""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Model server configuration"""
    
    # vLLM fast model server (running in WSL)
    fast_model_url: str = "http://localhost:8000/v1/chat/completions"
    fast_model_name: str = "Qwen/Qwen2.5-3B-Instruct"
    
    # Heavy model (Transformers)
    heavy_model_name: str = "Qwen/Qwen2.5-7B-Instruct"
    
    # Embeddings server (running in WSL)
    embeddings_url: str = "http://localhost:8001/v1/embeddings"
    embeddings_model: str = "BAAI/bge-small-en-v1.5"
    
    # Model parameters
    default_temperature: float = 0.8
    default_max_tokens: int = 1000
    request_timeout: int = 30


@dataclass
class StorageConfig:
    """Storage paths configuration"""
    
    base_dir: Path = Path("project_state")
    audit_log_dir: Path = Path("audit_logs")
    
    # Legacy directories (will be migrated in Phase 1)
    legacy_projects_dir: Path = Path("projects")
    legacy_graphs_dir: Path = Path("graphs")


# Global singleton instances
MODEL_CONFIG = ModelConfig()
STORAGE_CONFIG = StorageConfig()