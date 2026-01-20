# Storage Consolidation Migration Guide

## What Changed

**Before:** Files scattered across multiple directories
```
project_root/
├── PROJECT_memory.index
├── PROJECT_memory_texts.json
├── PROJECT_embeddings.npy
├── graphs/PROJECT_graph.json
├── projects/PROJECT.json
└── audit_logs/PROJECT_audit.jsonl
```

**After:** Unified structure per project
```
project_state/
└── PROJECT/
    ├── state.json
    ├── graph.json
    ├── audit.jsonl
    ├── tasks.json
    └── memory/
        ├── index.faiss
        ├── texts.json
        └── embeddings.npy
```

---

## Migration Process

### Automatic Migration

Migration happens automatically when you:
1. Import MemoryStore, GraphStore, AuditLog, or TaskManager
2. The module detects legacy files
3. Files are **copied** (not moved) to new location
4. Original files remain until you manually clean up

### Manual Cleanup

After verifying migration worked:
```powershell
# Dry run (safe - shows what would be deleted)
python scripts/cleanup_legacy_files.py

# Actually delete legacy files
python scripts/cleanup_legacy_files.py --execute
```

---

## Verification
```powershell
# Check new structure exists
ls project_state\default_project

# Should see:
# state.json
# graph.json
# audit.jsonl
# memory\

# Check memory files
ls project_state\default_project\memory

# Should see:
# index.faiss
# texts.json
# embeddings.npy
```

---

## Rollback

If something goes wrong:

1. Legacy files are still in place (migration copies, doesn't move)
2. Delete `project_state/` directory
3. Restart - system will use legacy files

---

## Benefits

1. **Organized**: All project files in one directory
2. **Portable**: Can move/backup entire project by copying one folder
3. **Multi-project ready**: Clean separation between projects
4. **Scalable**: Easy to add new file types per project