"""
Test configuration management.
"""

import pytest
from pathlib import Path
from config.settings import ModelConfig, StorageConfig, MODEL_CONFIG, STORAGE_CONFIG


def test_model_config_defaults():
    """Verify ModelConfig has correct values"""
    config = ModelConfig()
    
    assert config.fast_model_url == "http://localhost:8000/v1/chat/completions"
    assert config.fast_model_name == "Qwen/Qwen2.5-3B-Instruct"
    assert config.heavy_model_name == "Qwen/Qwen2.5-7B-Instruct"
    assert config.embeddings_url == "http://localhost:8001/v1/embeddings"
    assert config.embeddings_model == "BAAI/bge-small-en-v1.5"
    assert config.default_temperature == 0.8
    assert config.default_max_tokens == 1000
    assert config.request_timeout == 30


def test_storage_config_defaults():
    """Verify StorageConfig has correct values"""
    config = StorageConfig()
    
    assert config.base_dir == Path("project_state")
    assert config.audit_log_dir == Path("audit_logs")
    assert config.legacy_projects_dir == Path("projects")
    assert config.legacy_graphs_dir == Path("graphs")


def test_global_config_instances():
    """Verify global config instances exist"""
    assert MODEL_CONFIG is not None
    assert STORAGE_CONFIG is not None
    assert isinstance(MODEL_CONFIG, ModelConfig)
    assert isinstance(STORAGE_CONFIG, StorageConfig)