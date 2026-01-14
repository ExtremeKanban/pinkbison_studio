from typing import List
from .loader import list_projects, project_exists, duplicate_project, save_project_state, load_project_state

from .loader import delete_project as _delete_project

def delete_project(project_name: str) -> None:
    _delete_project(project_name)


def get_all_projects() -> List[str]:
    return list_projects()


def create_project_if_missing(project_name: str) -> None:
    """
    Ensure a project exists. If not, create a blank one by saving default state.
    """
    if not project_exists(project_name):
        # load_project_state will generate a default if file missing,
        # then we save it immediately.
        state = load_project_state(project_name)
        save_project_state(project_name, state)


def duplicate_project_state(src_project: str, dst_project: str) -> None:
    duplicate_project(src_project, dst_project)
