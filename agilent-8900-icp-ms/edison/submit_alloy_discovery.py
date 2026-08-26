"""Submit a high-effort Edison literature query that enumerates up to 100 distinct
aluminum alloys spanning a wide range of compositions / alloying-element palettes.

The query asks for a machine-parseable JSON array (fenced ```json block) of objects
{"designation", "family", "nominal_composition"} so the downstream per-alloy
pipeline (parse_alloys.py -> submit_alloy_queries.py) can ingest it programmatically.

The task_id is recorded in tasks.json under "alloy_discovery" so the run can be
resumed / fetched in a later session if this run times out.
"""

import json
import os
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

HERE = Path(__file__).resolve().parent
TASKS_FILE = HERE / "tasks.json"

QUERY = (
    "Identify up to 100 distinct aluminum alloys (and aluminum-based feedstocks) that "
    "together span as wide a range of compositions as possible - i.e. collectively "
    "covering many different alloying elements (e.g. Si, Mg, Cu, Zn, Mn, Fe, Cr, Ni, "
    "Ti, Zr, Sc, V, Li, Ag, Sn, Pb, Bi, Ga, Ni, rare earths, etc.) across the major "
    "wrought (1xxx-8xxx) and cast (Axxx.x) families as well as additive-manufacturing "
    "and specialty alloys (e.g. AlSi10Mg, Scalmalloy, A356/A357, 6061, 7075, 2024, "
    "5083, 4047, 1100). For each alloy give: its common designation/name, its family or "
    "class, and its nominal/typical elemental composition (weight-percent ranges for "
    "the main alloying elements, balance Al). Prioritize diversity of the alloying-"
    "element palette over near-duplicates. "
    "Return TWO things: (1) a readable markdown table of the alloys with their nominal "
    "compositions, and (2) at the very END of your answer, a single fenced code block "
    "labelled ```json containing a JSON array where each element is an object with keys "
    '"designation" (string), "family" (string), and "nominal_composition" (string, a '
    "concise human-readable composition such as 'Al-10Si-0.4Mg' or 'Al-5.5Zn-2.5Mg-"
    "1.5Cu'). Include every alloy from the table in the JSON array, up to 100 entries."
)


def get_client() -> EdisonClient:
    key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
    if not key:
        raise SystemExit("No Edison API key found in environment")
    return EdisonClient(api_key=key)


def main() -> None:
    client = get_client()
    tasks = {}
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())

    if tasks.get("alloy_discovery", {}).get("task_id"):
        print(f"[skip] alloy_discovery already submitted: {tasks['alloy_discovery']['task_id']}")
        return

    req = TaskRequest(name=JobNames.LITERATURE_HIGH, query=QUERY)
    task_id = str(client.create_task(req))
    print(f"[submit] alloy_discovery -> {task_id}")
    tasks["alloy_discovery"] = {
        "task_id": task_id,
        "job": str(JobNames.LITERATURE_HIGH),
        "answer_file": "alloy_discovery.md",
    }
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    print(f"Wrote {TASKS_FILE}")


if __name__ == "__main__":
    main()
