import os
import json


def reset_default_project():
    """
    Clears the default_project state so the smoke test starts clean.
    """
    path = os.path.join("projects", "default_project.json")
    if os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)


def wait_for_text(page, text, timeout=60000):
    """
    Waits for text to appear anywhere on the page.
    """
    page.wait_for_selector(f"text={text}", timeout=timeout)


def wait_for_no_errors(page):
    """
    Ensures no Streamlit red error boxes are visible.
    """
    errors = page.query_selector_all("div.stAlert")
    if errors:
        raise AssertionError("Streamlit error box detected on page.")


def wait_for_streamlit_to_start(page, timeout=30000):
    """
    Waits for Streamlit's running spinner to appear.
    This indicates that a callback has started.
    """
    page.wait_for_selector(
        '[data-testid="stStatusWidgetRunningIcon"]',
        state="attached",
        timeout=timeout
    )


def wait_for_streamlit_to_finish(page, timeout=600000):
    """
    Waits for Streamlit's running spinner to disappear.
    This indicates that the callback has fully completed.
    """
    page.wait_for_selector(
        '[data-testid="stStatusWidgetRunningIcon"]',
        state="detached",
        timeout=timeout
    )
