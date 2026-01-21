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


# ============================================================================
# REAL-TIME CONFIGURATION
# ============================================================================

class RealTimeConfig:
    """Configuration for real-time workflow features."""
    
    # Pipeline execution
    PIPELINE_TIMEOUT = 3600  # 1 hour maximum per pipeline
    PIPELINE_CHECKPOINT_INTERVAL = 30  # Create checkpoint every 30 seconds
    
    # Event streaming
    EVENT_STREAM_BUFFER_SIZE = 1000  # Max events to keep in memory
    EVENT_STREAM_REFRESH_RATE = 2  # seconds between UI updates
    
    # Feedback system
    FEEDBACK_QUEUE_MAX_SIZE = 100  # Max feedback messages per project
    FEEDBACK_AUTO_CLEANUP_HOURS = 24  # Auto-clean processed feedback after 24h
    
    # UI settings
    UI_AUTO_REFRESH_ENABLED = True
    UI_PROGRESS_UPDATE_INTERVAL = 1  # seconds
    
    # Async execution
    ASYNC_MAX_WORKERS = 4  # Max concurrent async tasks
    ASYNC_IO_TIMEOUT = 30  # seconds for I/O operations


# Global instance
REALTIME_CONFIG = RealTimeConfig()