from orchestrator import ProjectOrchestrator

if __name__ == "__main__":
    # You can parameterize this later (CLI args)
    project_name = "default_project"

    orchestrator = ProjectOrchestrator(project_name=project_name, poll_interval=2.0)
    orchestrator.run_forever()
