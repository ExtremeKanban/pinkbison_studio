# Multi-Project Orchestrator Guide

## Overview

The **Multi-Project Orchestrator** is a single background process that manages multiple creative projects simultaneously. It replaces the old single-project orchestrator with a more scalable, efficient design.

## Key Features

- **Single Process**: One orchestrator manages all projects
- **Async Architecture**: Non-blocking I/O for efficiency
- **Automatic Discovery**: Finds projects in `project_state/` directory
- **Fair Scheduling**: Round-robin processing between projects
- **Resource Isolation**: Each project has its own EventBus and state
- **Graceful Error Handling**: Errors in one project don't affect others

## File Structure
project_root/
├── multi_orchestrator.py # Core orchestrator logic
├── run_multi_orchestrator.py # CLI interface
├── ui/multi_orchestrator_panel.py # UI controls
└── docs/multi_orchestrator_guide.md (this file)


## Installation

No installation needed! The orchestrator uses your existing:
- Project persistence layer (`project_state/`)
- Registry pattern for resource management
- AgentFactory for stateless agents
- EventBus + AuditLog architecture

## Usage

### 1. Start the Orchestrator

```bash
# Start with all discovered projects
python run_multi_orchestrator.py start

# Start with specific projects
python run_multi_orchestrator.py start --projects space_epic fantasy_trilogy

# With custom settings
python run_multi_orchestrator.py start --poll-interval 0.2 --max-projects 20

### 2. List Available Projects

```bash
python run_multi_orchestrator.py list

### 3. From the UI
Open the Streamlit UI (studio_ui.py)

Scroll to the "🚀 Multi-Project Orchestrator" panel

Click "🚀 Start Orchestrator"

Follow the terminal instructions