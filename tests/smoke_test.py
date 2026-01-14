import json
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright
from utils import (
    reset_default_project,
    wait_for_text,
    wait_for_no_errors,
    wait_for_streamlit_to_start,
    wait_for_streamlit_to_finish,
)


REPORT_PATH = "tests/test_report.json"


def write_report(report):
    """Writes the JSON test report to disk."""
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def wait_for_any_label(page, labels, timeout=60000):
    """
    Waits for ANY of the provided text labels to appear.
    """
    for label in labels:
        try:
            wait_for_text(page, label, timeout=timeout)
            return label
        except Exception:
            continue
    raise TimeoutError(f"None of the expected labels appeared: {labels}")


def run_smoke_test():
    # Initialize report structure
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "passed",
        "results": {
            "Plot Architect": "pending",
            "Worldbuilder": "pending",
            "Character Agent": "pending",
            "Scene Pipeline": "pending",
            "Story Bible Pipeline": "pending",
            "Intelligence Panel": "pending",
            "Memory Browser": "pending",
        },
        "error": None,
    }

    # Reset default project before starting
    reset_default_project()

    with open("tests/test_data/sample_inputs.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print("Opening Streamlit UI...")
            page.goto("http://localhost:8501")

            wait_for_text(page, "PinkBison Creative Studio")
            wait_for_no_errors(page)

            # -----------------------------
            # Plot Architect
            # -----------------------------
            print("Testing Plot Architect...")
            page.fill("textarea[aria-label='Seed idea for the Plot Architect']", data["plot_seed"])
            page.click("text=Generate 3‑Act Outline")

            wait_for_streamlit_to_start(page)
            wait_for_streamlit_to_finish(page)

            wait_for_text(page, "3‑Act Outline")
            wait_for_no_errors(page)
            report["results"]["Plot Architect"] = "passed"

            # -----------------------------
            # Worldbuilder
            # -----------------------------
            print("Testing Worldbuilder...")
            page.fill("textarea[aria-label='Outline for Worldbuilder']", data["world_outline"])
            page.click("text=Generate World Bible")

            wait_for_streamlit_to_start(page)
            wait_for_streamlit_to_finish(page)

            wait_for_text(page, "World Bible")
            wait_for_no_errors(page)
            report["results"]["Worldbuilder"] = "passed"

            # -----------------------------
            # Character Agent
            # -----------------------------
            print("Testing Character Agent...")
            page.fill("textarea[aria-label='Outline for Character Agent']", data["character_outline"])
            page.fill("textarea[aria-label='World notes for Character Agent']", data["character_world_notes"])
            page.click("text=Generate Character Bible")

            wait_for_streamlit_to_start(page)
            wait_for_streamlit_to_finish(page)

            wait_for_text(page, "Character Bible")
            wait_for_no_errors(page)
            report["results"]["Character Agent"] = "passed"

            # -----------------------------
            # Scene Pipeline
            # -----------------------------
            print("Testing Scene Pipeline...")
            page.fill("textarea[aria-label='Scene goal / prompt']", data["scene_prompt"])
            page.fill("textarea[aria-label='Relevant outline snippet']", data["scene_outline_snippet"])
            page.fill("textarea[aria-label='World notes for scene']", data["scene_world_notes"])
            page.fill("textarea[aria-label='Character notes for scene']", data["scene_character_notes"])
            page.click("text=Generate Scene Pipeline")

            wait_for_streamlit_to_start(page)
            wait_for_streamlit_to_finish(page)

            page.wait_for_selector("text=Raw", timeout=30000)
            wait_for_no_errors(page)
            report["results"]["Scene Pipeline"] = "passed"

            # -----------------------------
            # Story Bible Pipeline
            # -----------------------------
            print("Testing Story Bible Pipeline...")
            page.fill("textarea[aria-label='Seed idea for full story bible pipeline']", data["pipeline_seed"])
            page.click("text=Run Story Bible Pipeline")

            wait_for_streamlit_to_start(page)
            wait_for_streamlit_to_finish(page)

            # Robust fallback: accept ANY of these labels
            wait_for_any_label(
                page,
                labels=["Pipeline Output", "Story Bible", "Output"],
                timeout=60000,
            )

            wait_for_no_errors(page)
            report["results"]["Story Bible Pipeline"] = "passed"

            # -----------------------------
            # Intelligence Panel (NO SPINNER)
            # -----------------------------
            print("Checking Intelligence Panel...")
            page.click("text=Project Intelligence Panel")

            wait_for_text(page, "Task Queue", timeout=30000)
            wait_for_no_errors(page)

            report["results"]["Intelligence Panel"] = "passed"

            # -----------------------------
            # Memory Browser (NO SPINNER)
            # -----------------------------
            print("Checking Memory Browser...")
            page.click("text=Memory Browser")

            wait_for_no_errors(page)
            report["results"]["Memory Browser"] = "passed"

            # -----------------------------
            # SUCCESS
            # -----------------------------
            print("""
=========================================
      SMOKE TEST PASSED SUCCESSFULLY 🎉
=========================================
""")

        except Exception as e:
            print("""
=========================================
           SMOKE TEST FAILED ❌
=========================================
""")

            # Mark failure
            report["status"] = "failed"

            # Identify which section failed
            for section, status in report["results"].items():
                if status == "pending":
                    report["results"][section] = "failed"
                    failing_section = section
                    break
            else:
                failing_section = "Unknown"

            # Capture error details
            stack = traceback.format_exc().splitlines()
            report["error"] = {
                "section": failing_section,
                "message": str(e),
                "stacktrace": stack,
            }

            # Save screenshot
            page.screenshot(path="tests/failure.png")

            # Save HTML snapshot
            with open("tests/failure_snapshot.html", "w", encoding="utf-8") as f:
                f.write(page.content())

            print("Saved: tests/failure.png and tests/failure_snapshot.html")
            print("Full traceback:")
            traceback.print_exc()

            write_report(report)
            browser.close()
            reset_default_project()
            exit(1)

        # Cleanup on success
        write_report(report)
        browser.close()
        reset_default_project()
        print("Default project cleaned. Test complete.")
        exit(0)


if __name__ == "__main__":
    run_smoke_test()
