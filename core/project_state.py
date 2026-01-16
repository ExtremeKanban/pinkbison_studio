"""
Unified project state management with versioning and validation.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from filelock import FileLock


@dataclass
class ProjectMeta:
    """Project metadata"""
    genre: str = "Sci-Fi"
    tone: str = "Epic, serious"
    themes: str = "Destiny, sacrifice, technology vs humanity"
    setting: str = "Far future galaxy"


@dataclass
class PipelineResult:
    """Result from a pipeline execution"""
    pipeline_type: str  # "story_bible", "chapter", "full_story", "director"
    timestamp: str
    result: Dict[str, Any]


@dataclass
class ProjectState:
    """
    Complete project state snapshot.
    
    Handles:
    - Metadata (genre, tone, themes, setting)
    - Agent outputs (outline, world, characters)
    - Pipeline results
    - UI inputs
    - Versioning and migration
    """
    
    project_name: str
    version: str = "1.0.0"
    
    # Metadata
    meta: ProjectMeta = field(default_factory=ProjectMeta)
    
    # Agent outputs
    outline: str = ""
    world: str = ""
    characters: str = ""
    
    # Scene outputs (legacy compatibility)
    scene_raw: str = ""
    scene_continuity: str = ""
    scene_final: str = ""
    
    # Pipeline outputs
    pipeline_outline: str = ""
    pipeline_world: str = ""
    pipeline_characters: str = ""
    
    # Pipeline results history
    pipeline_results: List[PipelineResult] = field(default_factory=list)
    
    # UI inputs
    inputs: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def save(self, base_dir: str = "project_state") -> None:
        """Save to disk with file locking"""
        self.updated_at = datetime.utcnow().isoformat()
        
        path = self._state_path(base_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        lock_path = f"{path}.lock"
        
        with FileLock(lock_path, timeout=10):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, project_name: str, base_dir: str = "project_state") -> "ProjectState":
        """Load with automatic migration"""
        path = cls._state_path_static(project_name, base_dir)
        
        if not path.exists():
            return cls.create_default(project_name)
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Migrate if needed
        current_version = data.get('version', '0.0.0')
        if current_version != '1.0.0':
            data = cls._migrate(data, current_version)
        
        return cls.from_dict(data)
    
    @classmethod
    def create_default(cls, project_name: str) -> "ProjectState":
        """Create default state for new project"""
        return cls(
            project_name=project_name,
            meta=ProjectMeta(),
            inputs={
                "seed_idea_plot": "",
                "outline_for_world": "",
                "world_notes_for_chars": "",
                "outline_for_chars": "",
                "scene_prompt": "",
                "scene_outline_snippet": "",
                "scene_world_notes": "",
                "scene_character_notes": "",
                "seed_idea_pipeline": "",
                "memory_search_query": "",
                "new_memory_text": "",
            }
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert ProjectMeta to dict
        data['meta'] = asdict(self.meta)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectState":
        """Create from dictionary"""
        # Handle nested ProjectMeta
        if 'meta' in data and isinstance(data['meta'], dict):
            data['meta'] = ProjectMeta(**data['meta'])
        
        # Handle pipeline_results
        if 'pipeline_results' in data:
            data['pipeline_results'] = [
                PipelineResult(**r) if isinstance(r, dict) else r
                for r in data['pipeline_results']
            ]
        
        return cls(**data)
    
    def _state_path(self, base_dir: str) -> Path:
        """Get path to state file"""
        return Path(base_dir) / self.project_name / "state.json"
    
    @staticmethod
    def _state_path_static(project_name: str, base_dir: str) -> Path:
        """Static version of _state_path"""
        return Path(base_dir) / project_name / "state.json"
    
    @classmethod
    def _migrate(cls, data: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """Migrate data from old version to current"""
        # Example migration logic
        if from_version == '0.0.0':
            # Old format from projects/*.json
            data['version'] = '1.0.0'
            
            # Ensure all required fields exist
            if 'meta' not in data:
                data['meta'] = asdict(ProjectMeta())
            
            if 'pipeline_results' not in data:
                data['pipeline_results'] = []
            
            if 'created_at' not in data:
                data['created_at'] = datetime.utcnow().isoformat()
            
            if 'updated_at' not in data:
                data['updated_at'] = datetime.utcnow().isoformat()
        
        return data