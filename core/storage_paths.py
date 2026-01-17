"""
Centralized path management for project files.
Provides unified directory structure for all project data.
"""

from pathlib import Path
from typing import NamedTuple
from config.settings import STORAGE_CONFIG


class ProjectPaths(NamedTuple):
    """
    All file paths for a project in one place.
    
    Ensures consistent directory structure across the application.
    """
    root: Path
    state: Path
    graph: Path
    audit: Path
    tasks: Path
    memory_dir: Path
    memory_index: Path
    memory_texts: Path
    memory_embeddings: Path
    
    @classmethod
    def for_project(cls, project_name: str, base_dir: str = None) -> "ProjectPaths":
        """
        Generate all paths for a project.
        
        Args:
            project_name: Name of the project
            base_dir: Optional base directory (defaults to config)
            
        Returns:
            ProjectPaths with all file locations
            
        Example:
            >>> paths = ProjectPaths.for_project("my_project")
            >>> paths.state
            Path('project_state/my_project/state.json')
        """
        base = Path(base_dir) if base_dir else STORAGE_CONFIG.base_dir
        root = base / project_name
        memory_dir = root / "memory"
        
        return cls(
            root=root,
            state=root / "state.json",
            graph=root / "graph.json",
            audit=root / "audit.jsonl",
            tasks=root / "tasks.json",
            memory_dir=memory_dir,
            memory_index=memory_dir / "index.faiss",
            memory_texts=memory_dir / "texts.json",
            memory_embeddings=memory_dir / "embeddings.npy",
        )
    
    def ensure_directories(self) -> None:
        """Create all necessary directories"""
        self.root.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)


# Legacy path helpers for backward compatibility during migration
class LegacyPaths:
    """
    Legacy file paths for migration.
    Maps old scattered file locations.
    """
    
    @staticmethod
    def memory_index(project_name: str) -> Path:
        """Legacy: project_root/PROJECT_memory.index"""
        return Path(f"{project_name}_memory.index")
    
    @staticmethod
    def memory_texts(project_name: str) -> Path:
        """Legacy: project_root/PROJECT_memory_texts.json"""
        return Path(f"{project_name}_memory_texts.json")
    
    @staticmethod
    def memory_embeddings(project_name: str) -> Path:
        """Legacy: project_root/PROJECT_embeddings.npy"""
        return Path(f"{project_name}_embeddings.npy")
    
    @staticmethod
    def graph(project_name: str) -> Path:
        """Legacy: graphs/PROJECT_graph.json"""
        return STORAGE_CONFIG.legacy_graphs_dir / f"{project_name}_graph.json"
    
    @staticmethod
    def state(project_name: str) -> Path:
        """Legacy: projects/PROJECT.json"""
        return STORAGE_CONFIG.legacy_projects_dir / f"{project_name}.json"
    
    @staticmethod
    def audit(project_name: str) -> Path:
        """Legacy: audit_logs/PROJECT_audit.jsonl"""
        return STORAGE_CONFIG.audit_log_dir / f"{project_name}_audit.jsonl"
    
    @staticmethod
    def tasks(project_name: str) -> Path:
        """Legacy: tasks/PROJECT_tasks.json"""
        return Path("tasks") / f"{project_name}_tasks.json"