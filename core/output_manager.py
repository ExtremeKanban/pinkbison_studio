"""
Output file management for chapters, scenes, and drafts.
Manages persistent output files in project_state/<project>/outputs/
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class OutputManager:
    """
    Manages persistent output files for a project.
    
    File structure:
        project_state/<project>/outputs/
        ├── chapters/chapter_001.json
        ├── scenes/scene_001.txt
        └── drafts/full_story_20250116_120000.txt
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.base_dir = Path("project_state") / project_name / "outputs"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.chapters_dir = self.base_dir / "chapters"
        self.scenes_dir = self.base_dir / "scenes"
        self.drafts_dir = self.base_dir / "drafts"
        
        self.chapters_dir.mkdir(exist_ok=True)
        self.scenes_dir.mkdir(exist_ok=True)
        self.drafts_dir.mkdir(exist_ok=True)
    
    def save_chapter(self, chapter_index: int, chapter_data: Dict[str, Any]) -> Path:
        """Save chapter data as JSON"""
        filename = f"chapter_{chapter_index:03d}.json"
        path = self.chapters_dir / filename
        
        chapter_data_with_meta = {
            **chapter_data,
            "chapter_index": chapter_index,
            "saved_at": datetime.utcnow().isoformat(),
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(chapter_data_with_meta, f, indent=2, ensure_ascii=False)
        
        print(f"[OutputManager] Saved chapter {chapter_index} to {path}")
        return path
    
    def load_chapter(self, chapter_index: int) -> Dict[str, Any]:
        """Load chapter data"""
        filename = f"chapter_{chapter_index:03d}.json"
        path = self.chapters_dir / filename
        
        if not path.exists():
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_chapters(self) -> List[int]:
        """List all chapter indices that have been saved"""
        chapters = []
        for path in self.chapters_dir.glob("chapter_*.json"):
            try:
                idx = int(path.stem.split('_')[1])
                chapters.append(idx)
            except (ValueError, IndexError):
                continue
        return sorted(chapters)
    
    def save_scene(self, scene_index: int, content: str) -> Path:
        """Save a scene as text"""
        filename = f"scene_{scene_index:03d}.txt"
        path = self.scenes_dir / filename
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OutputManager] Saved scene {scene_index} to {path}")
        return path
    
    def load_scene(self, scene_index: int) -> str:
        """Load scene text"""
        filename = f"scene_{scene_index:03d}.txt"
        path = self.scenes_dir / filename
        
        if not path.exists():
            return ""
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def save_draft(self, draft_name: str, content: str) -> Path:
        """Save a draft with timestamp"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{draft_name}_{timestamp}.txt"
        path = self.drafts_dir / filename
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OutputManager] Saved draft '{draft_name}' to {path}")
        return path
    
    def list_drafts(self, draft_name: str = None) -> List[Path]:
        """List all draft files, optionally filtered by name"""
        if draft_name:
            pattern = f"{draft_name}_*.txt"
        else:
            pattern = "*.txt"
        
        return sorted(self.drafts_dir.glob(pattern), reverse=True)
    
    def get_latest_draft(self, draft_name: str) -> Path:
        """Get most recent draft with given name"""
        drafts = self.list_drafts(draft_name)
        return drafts[0] if drafts else None
    
    def clear_all(self) -> None:
        """Delete all outputs for this project"""
        import shutil
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.chapters_dir.mkdir(exist_ok=True)
            self.scenes_dir.mkdir(exist_ok=True)
            self.drafts_dir.mkdir(exist_ok=True)
        print(f"[OutputManager] Cleared all outputs for {self.project_name}")