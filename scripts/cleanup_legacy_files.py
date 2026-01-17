"""
Cleanup legacy files after migration to unified storage.

This script safely removes old scattered files after verifying
they've been successfully migrated to project_state/ directory.

Run with: python scripts/cleanup_legacy_files.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.storage_paths import LegacyPaths, ProjectPaths


def verify_migration(project_name: str) -> bool:
    """
    Verify project has been migrated to unified storage.
    
    Returns True if all new files exist.
    """
    paths = ProjectPaths.for_project(project_name)
    
    required = [
        paths.state,
        paths.graph,
        paths.memory_texts,
    ]
    
    return all(p.exists() for p in required)


def cleanup_project(project_name: str, dry_run: bool = True) -> None:
    """
    Remove legacy files for a project.
    
    Args:
        project_name: Name of project to clean up
        dry_run: If True, only show what would be deleted
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Cleaning up {project_name}...")
    
    # Verify migration first
    if not verify_migration(project_name):
        print(f"  ⚠️  Skipping - migration not complete for {project_name}")
        return
    
    # List of legacy files to remove
    legacy_files = [
        LegacyPaths.memory_index(project_name),
        LegacyPaths.memory_texts(project_name),
        LegacyPaths.memory_embeddings(project_name),
        LegacyPaths.graph(project_name),
        LegacyPaths.state(project_name),
        LegacyPaths.audit(project_name),
        LegacyPaths.tasks(project_name),
    ]
    
    removed_count = 0
    for legacy_file in legacy_files:
        if legacy_file.exists():
            if dry_run:
                print(f"  Would remove: {legacy_file}")
            else:
                legacy_file.unlink()
                print(f"  ✓ Removed: {legacy_file}")
            removed_count += 1
    
    if removed_count == 0:
        print(f"  ✓ No legacy files to remove")
    else:
        print(f"  ✓ Cleaned up {removed_count} legacy files")


def main():
    """Main cleanup script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up legacy files after migration"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete files (default is dry-run)"
    )
    parser.add_argument(
        "--project",
        help="Clean up specific project (default: all projects)"
    )
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    print("=" * 60)
    print("Legacy File Cleanup Script")
    print("=" * 60)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be deleted")
        print("Run with --execute to actually delete files\n")
    else:
        print("\n⚠️  EXECUTE MODE - Files will be permanently deleted!")
        response = input("Are you sure? Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    # Determine which projects to clean
    if args.project:
        projects = [args.project]
    else:
        # Find all projects in project_state/
        base_dir = Path("project_state")
        if not base_dir.exists():
            print("No project_state/ directory found!")
            return
        
        projects = [
            p.name for p in base_dir.iterdir() 
            if p.is_dir() and (p / "state.json").exists()
        ]
    
    if not projects:
        print("No projects found to clean up")
        return
    
    print(f"Found {len(projects)} project(s): {', '.join(projects)}\n")
    
    # Clean up each project
    for project_name in projects:
        cleanup_project(project_name, dry_run=dry_run)
    
    print("\n" + "=" * 60)
    if dry_run:
        print("Dry run complete. Run with --execute to delete files.")
    else:
        print("Cleanup complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()