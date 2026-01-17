"""
Persistent append-only log for historical agent activity.
Stored as JSON Lines for easy streaming and grep.
"""

import json
import os
from typing import Dict, Any, List, Optional, Iterator
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from config.settings import STORAGE_CONFIG

@dataclass
class AuditEntry:
    """Single audit log entry"""
    timestamp: str
    project_name: str
    event_type: str  # "agent_message", "task_update", "feedback", etc.
    sender: str
    recipient: str
    payload: Dict[str, Any]
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, line: str) -> "AuditEntry":
        data = json.loads(line)
        return cls(**data)


class AuditLog:
    """
    Persistent append-only audit log using JSON Lines format.
    
    Design:
    - One file per project: audit_logs/<project>_audit.jsonl
    - Append-only (never modify existing entries)
    - Efficient streaming for large logs
    - Optional replay capability
    """
    
    def __init__(self, project_name: str, base_dir: str = None):
        self.project_name = project_name
        
        # Get unified paths
        from core.storage_paths import ProjectPaths, LegacyPaths
        self.paths = ProjectPaths.for_project(project_name, base_dir)
        self.paths.ensure_directories()
        
        # Migrate from legacy location if needed
        self._migrate_from_legacy()
        
        # Use new unified path
        self.log_path = self.paths.audit
        self._ensure_log_exists()
    
    def _migrate_from_legacy(self) -> None:
        """Migrate audit log from legacy location"""
        import shutil
        from core.storage_paths import LegacyPaths
        
        legacy_path = LegacyPaths.audit(self.project_name)
        
        # Check if migration needed
        if not legacy_path.exists():
            return
        
        # Check if already migrated
        if self.paths.audit.exists():
            return
        
        print(f"[AuditLog] Migrating {self.project_name} audit log to unified storage...")
        shutil.copy2(legacy_path, self.paths.audit)
        print(f"  ✓ Migrated: {legacy_path} → {self.paths.audit}")
    
    def _ensure_log_exists(self) -> None:
        """Create log file if it doesn't exist"""
        if not self.log_path.exists():
            self.log_path.touch()
    
    def append(self, event_type: str, sender: str, recipient: str, 
               payload: Dict[str, Any]) -> None:
        """Append entry to audit log"""
        entry = AuditEntry(
            timestamp=datetime.utcnow().isoformat(),
            project_name=self.project_name,
            event_type=event_type,
            sender=sender,
            recipient=recipient,
            payload=payload
        )
        
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(entry.to_json() + '\n')
    
    def read_all(self) -> List[AuditEntry]:
        """Read all entries (use sparingly for large logs)"""
        return list(self.stream())
    
    def stream(self, since: Optional[str] = None) -> Iterator[AuditEntry]:
        """Stream entries (memory-efficient for large logs)"""
        if not self.log_path.exists():
            return
        
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                entry = AuditEntry.from_json(line)
                
                # Filter by timestamp if requested
                if since and entry.timestamp <= since:
                    continue
                
                yield entry
    
    def search(self, event_type: Optional[str] = None, 
               sender: Optional[str] = None,
               limit: Optional[int] = None) -> List[AuditEntry]:
        """Search audit log with filters"""
        results = []
        
        for entry in self.stream():
            if event_type and entry.event_type != event_type:
                continue
            if sender and entry.sender != sender:
                continue
            
            results.append(entry)
            
            if limit and len(results) >= limit:
                break
        
        return results
    
    def clear(self) -> None:
        """Clear audit log (destructive, use with caution)"""
        if self.log_path.exists():
            self.log_path.unlink()
        self._ensure_log_exists()