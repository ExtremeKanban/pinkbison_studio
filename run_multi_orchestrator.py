"""
CLI for managing the multi-project orchestrator.
"""

import argparse
import sys
import logging
from typing import List
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from multi_orchestrator import MultiProjectOrchestrator


def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def start_orchestrator(args):
    """Start the multi-project orchestrator."""
    setup_logging()
    
    orchestrator = MultiProjectOrchestrator(
        poll_interval=args.poll_interval,
        max_projects=args.max_projects,
    )
    
    # Add projects
    if args.projects:
        projects = args.projects
    else:
        # Auto-discover all projects
        projects = orchestrator.auto_discover_projects()
    
    if not projects:
        print("No projects found. Create projects in the UI first.")
        return
    
    for project in projects:
        try:
            orchestrator.add_project(project)
            print(f"✓ Added project: {project}")
        except ValueError as e:
            print(f"✗ Error adding project {project}: {e}")
    
    print(f"\nStarting orchestrator with {len(orchestrator.projects)} projects:")
    for project_name in orchestrator.projects:
        print(f"  - {project_name}")
    
    print("\n" + "="*50)
    print("Multi-Project Orchestrator Running")
    print("="*50)
    print("\nCommands:")
    print("  Ctrl+C - Stop orchestrator")
    print("\nStatistics will be shown when you stop.")
    
    try:
        orchestrator.run_forever()
    except KeyboardInterrupt:
        print("\n" + "="*50)
        print("Orchestrator Stopped - Final Statistics")
        print("="*50)
        
        stats = orchestrator.list_projects()
        total_tasks = sum(p["tasks_processed"] for p in stats)
        
        print(f"\nTotal projects processed: {len(stats)}")
        print(f"Total tasks processed: {total_tasks}")
        print(f"Active projects: {len(orchestrator.active_projects)}")
        
        if stats:
            print("\nProject Details:")
            for project in stats:
                status_icon = "🟢" if project["status"] == "active" else "🟡" if project["status"] == "paused" else "🔴"
                print(f"  {status_icon} {project['project_name']}:")
                print(f"    Tasks: {project['tasks_processed']}, Errors: {project['error_count']}")
                print(f"    Pending: {project['pending_tasks']}, Status: {project['status']}")
    finally:
        print("\nGoodbye!")


def list_projects():
    """List available projects."""
    setup_logging()
    
    orchestrator = MultiProjectOrchestrator()
    projects = orchestrator.auto_discover_projects()
    
    if not projects:
        print("No projects found in project_state/ directory.")
        print("Create projects using the Streamlit UI first.")
        return
    
    print(f"Found {len(projects)} projects:")
    for project in projects:
        print(f"  - {project}")
    
    # Check project_state directory structure
    base_dir = Path("project_state")
    if base_dir.exists():
        print("\nProject state directory structure:")
        for item in base_dir.iterdir():
            if item.is_dir():
                state_file = item / "state.json"
                if state_file.exists():
                    print(f"  ✓ {item.name}/ (has state.json)")
                else:
                    print(f"  ⚠ {item.name}/ (missing state.json)")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Project Orchestrator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start                    # Start with all discovered projects
  %(prog)s start --projects my_project another_project  # Start specific projects
  %(prog)s list                     # List available projects
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Start orchestrator
    start_parser = subparsers.add_parser("start", help="Start orchestrator")
    start_parser.add_argument(
        "--projects",
        nargs="+",
        help="Projects to manage (default: all in project_state/)"
    )
    start_parser.add_argument(
        "--poll-interval",
        type=float,
        default=0.1,
        help="Poll interval in seconds (default: 0.1)"
    )
    start_parser.add_argument(
        "--max-projects",
        type=int,
        default=10,
        help="Maximum number of projects (default: 10)"
    )
    
    # List projects
    list_parser = subparsers.add_parser("list", help="List available projects")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_orchestrator(args)
    elif args.command == "list":
        list_projects()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()