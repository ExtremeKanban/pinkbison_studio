# Package Inventory - What's Installed Where

## Overview

PinkBison Creative Studio runs in a **hybrid environment**:
- **Windows (Conda)**: UI, orchestrator, heavy model
- **WSL Ubuntu**: vLLM server, embeddings server

---

## Windows Environment (multimodal-assistant)

**Location**: `C:\Users\hilto\miniconda3\envs\multimodal-assistant`

### Core Application
```
streamlit==1.52.1          # Web UI framework
torch==2.7.0+cu128         # PyTorch with CUDA support
transformers==4.57.3       # Hugging Face transformers
faiss-cpu==1.13.2          # Vector similarity search
requests==2.31.0           # HTTP client
filelock==3.13.0           # File locking (NEW in Phase 0)
```

### Testing (NEW - Added in Phase 0)
```
pytest==9.0.2              # Test framework
pytest-cov==7.0.0          # Coverage reporting
```

### AI/ML Frameworks
```
langchain                  # LLM application framework
chromadb                   # Vector database
```

### Utilities
```
rich                       # Terminal formatting
```

---

## WSL Ubuntu Environment (qwen-server)

**Purpose**: Run vLLM and embeddings servers

### vLLM Server
```
vllm==0.13.0               # Fast LLM inference
```

**Runs**: `Qwen/Qwen2.5-3B-Instruct` at `localhost:8000`

### Embeddings Server
**Runs**: `BAAI/bge-small-en-v1.5` at `localhost:8001`

---

## New in Phase 0 Refactoring

### Packages Added
1. **pytest** (9.0.2) - Test framework
2. **pytest-cov** (7.0.0) - Code coverage
3. **filelock** (3.13.0) - Safe concurrent file access

### Configuration Module Added

**Location**: `config/`

**Files**:
- `config/__init__.py` - Package initialization
- `config/settings.py` - Centralized configuration

**Purpose**: All hardcoded URLs and paths now in one place

**Values Defined**:
```python
# Model servers
FAST_MODEL_URL = "http://localhost:8000/v1/chat/completions"
EMBEDDINGS_URL = "http://localhost:8001/v1/embeddings"

# Storage paths
PROJECT_STATE_DIR = "project_state/"
AUDIT_LOG_DIR = "audit_logs/"
```

**Usage Example**:
```python
from config.settings import MODEL_CONFIG, STORAGE_CONFIG

url = MODEL_CONFIG.fast_model_url
path = STORAGE_CONFIG.base_dir
```

---

## Installation Commands

### Installing New Packages
```powershell
# Activate environment
conda activate multimodal-assistant

# Install testing tools
pip install pytest pytest-cov filelock

# Verify
pytest --version
```

---

## Directory Structure After Phase 0
```
pinkbison_studio/
├── config/                    # NEW - Configuration module
│   ├── __init__.py
│   └── settings.py
├── core/                      # Infrastructure
│   ├── audit_log.py
│   ├── event_bus.py
│   └── project_state.py
├── agents/                    # Agent implementations
├── ui/                        # Streamlit UI
│   └── common.py             # NEW - Shared UI utilities
├── tests/                     # All tests
│   └── unit/
│       └── config/           # NEW - Config tests
│           └── test_settings.py
├── docs/
│   ├── setup/                # NEW - Setup documentation
│   │   └── PACKAGE_INVENTORY.md
│   ├── standards/            # Code standards
│   └── migrations/           # Migration guides
├── pytest.ini                # NEW - Pytest configuration
└── requirements.txt          # Updated with new packages
```

---

## Verification
```powershell
# Test configuration works
python -c "from config.settings import MODEL_CONFIG; print('✓ Config works')"

# Run config tests
pytest tests/unit/config/test_settings.py -v

# Should see:
# test_model_config_defaults PASSED
# test_storage_config_defaults PASSED
# test_global_config_instances PASSED
```