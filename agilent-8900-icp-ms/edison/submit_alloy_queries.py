"""Submit one LOW-effort Edison literature query per aluminum alloy from alloys.json.

Each query asks how EDS (SEM-EDS), XRF, ICP-OES, and ICP-MS compare for
characterizing that alloy's bulk composition, and - for the two solution
techniques (ICP-OES and ICP-MS) - which acids are needed to fully dissolve the
alloy (the answer may differ between ICP-OES and ICP-MS), under the lab's hard
constraint of avoiding hydrofluoric acid (HF).

Per-alloy task IDs are persisted in alloy_tasks.json so the run is fully
resumable: re-running skips alloys that were already submitted.
"""

import json
import os
import re
import time
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

HERE = Path(__file__).resolve().parent
ALLOYS = HERE / "alloys.json"
ALLOY_TASKS = HERE / "alloy_tasks.json"

# The Edison API rate-limits task creation (HTTP 429). Throttle submissions and
# back off when we get rate-limited so the (resumable) run can finish.
SUBMIT_DELAY = float(os.environ.get("EDISON_SUBMIT_DELAY", "10"))
MAX_RETRIES = int(os.environ.get("EDISON_SUBMIT_RETRIES", "6"))
BACKOFF = float(os.environ.get("EDISON_SUBMIT_BACKOFF", "60"))


def get_client() -> EdisonClient:
    key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
    if not key:
        raise SystemExit("No Edison API key found in environment")
    return EdisonClient(api_key=key)


def slugify(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    return slug or "alloy"


def build_query(alloy: dict) -> str:
    desig = alloy["designation"]
    comp = alloy.get("nominal_composition", "")
    family = alloy.get("family", "")
    comp_clause = f" (nominal composition {comp})" if comp else ""
    family_clause = f", {family} family" if family else ""
    return (
        f"For the aluminum alloy {desig}{family_clause}{comp_clause}, compare four "
        "elemental-composition characterization techniques - SEM-EDS (energy-dispersive "
        "X-ray spectroscopy), XRF (X-ray fluorescence), ICP-OES, and ICP-MS - for "
        "determining this alloy's bulk composition. For each technique state how well "
        "it quantifies this alloy's specific alloying elements (including light "
        "elements and the Al matrix), its accuracy/precision and limitations for this "
        "composition, and the sample-preparation burden. "
        "Then, specifically for the two solution-based techniques (ICP-OES and "
        "ICP-MS), specify which acids / digestion reagents are required to fully "
        "dissolve THIS alloy into a clear, particle-free solution. The recommended acid "
        "mixture may differ between ICP-OES and ICP-MS, so give each separately. HARD "
        "CONSTRAINT: avoid hydrofluoric acid (HF) - recommend HF-free digestion "
        "chemistry (e.g. HNO3, HCl, aqua regia, H2O2, alkaline fusion) and only mention "
        "HF/HBF4 if truly unavoidable, with an explicit caveat. Conclude with which "
        "single technique is the best first choice for this alloy's bulk composition."
    )


def main() -> None:
    if not ALLOYS.exists():
        raise SystemExit(f"{ALLOYS} not found; run parse_alloys.py first")
    alloys = json.loads(ALLOYS.read_text())

    tasks = {}
    if ALLOY_TASKS.exists():
        tasks = json.loads(ALLOY_TASKS.read_text())

    client = get_client()
    submitted = 0
    for alloy in alloys:
        key = slugify(alloy["designation"])
        if tasks.get(key, {}).get("task_id"):
            print(f"[skip] {key} already submitted: {tasks[key]['task_id']}")
            continue

        task_id = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                req = TaskRequest(name=JobNames.LITERATURE, query=build_query(alloy))
                task_id = str(client.create_task(req))
                break
            except Exception as exc:  # noqa: BLE001  (mostly HTTP 429 rate-limit)
                wait = BACKOFF * attempt
                print(f"[retry] {key} attempt {attempt}/{MAX_RETRIES} failed "
                      f"({type(exc).__name__}); sleeping {wait:.0f}s")
                time.sleep(wait)
        if task_id is None:
            print(f"[give-up] {key} not submitted after {MAX_RETRIES} attempts; "
                  "re-run this script later to resume")
            break

        print(f"[submit] {key} -> {task_id}")
        tasks[key] = {
            "task_id": task_id,
            "job": str(JobNames.LITERATURE),
            "designation": alloy["designation"],
            "nominal_composition": alloy.get("nominal_composition", ""),
            "answer_file": f"{key}.md",
        }
        ALLOY_TASKS.write_text(json.dumps(tasks, indent=2))
        submitted += 1
        time.sleep(SUBMIT_DELAY)

    print(f"\nSubmitted {submitted} new alloy queries; {len(tasks)} total in {ALLOY_TASKS}")


if __name__ == "__main__":
    main()
