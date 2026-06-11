"""Submit an Edison ANALYSIS task that ingests all downloaded literature
artifacts and produces a single cohesive set of recommendations / SOP draft.

The artifacts directory is uploaded as a single zipped collection
(store_file_content(..., as_collection=True)); uploading individual files
separately is known to make the ANALYSIS task fail silently.

The resulting task_id is appended to tasks.json under the "analysis" key so it
can be fetched in a later session if this run times out before it finishes.
"""

import json
import os
from pathlib import Path

from edison_client import EdisonClient, JobNames
from edison_client.models.app import TaskRequest

HERE = Path(__file__).resolve().parent
TASKS_FILE = HERE / "tasks.json"
ART = HERE / "artifacts"

QUERY = (
    "The attached markdown files are three high-effort literature reviews about "
    "using an Agilent 8900 triple-quadrupole ICP-MS to characterize the elemental "
    "composition of aluminum alloys (AlSi10Mg, 1100 aluminum wire) and silicon "
    "powder, which must first be acid-digested into a clear, particle-free, "
    "water-soluble solution. The three reports cover (1) acid digestion protocols, "
    "(2) ICP-MS/MS measurement best practices and interference removal, and (3) "
    "QA/QC and calibration. "
    "Read all of them and synthesize ONE cohesive, non-redundant set of practical "
    "recommendations for a university lab setting up this workflow for the first "
    "time. Produce: (a) a concise executive summary; (b) a step-by-step "
    "standard-operating-procedure outline covering sample prep / acid digestion "
    "(distinguishing low-Si Al like 1100 from high-Si AlSi10Mg requiring HF), "
    "instrument setup and tuning, measurement, and QA/QC; (c) a consolidated table "
    "of recommended reagents, isotopes, reaction-gas modes, and internal standards; "
    "(d) a prioritized safety checklist (especially HF handling); and (e) the key "
    "open questions / decisions the lab should resolve. Reconcile any conflicting "
    "advice between the reports and call out where they agree."
)


def get_client() -> EdisonClient:
    key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
    if not key:
        raise SystemExit("No Edison API key found in environment")
    return EdisonClient(api_key=key)


def main() -> None:
    client = get_client()
    tasks = json.loads(TASKS_FILE.read_text())

    if tasks.get("analysis", {}).get("task_id"):
        print(f"[skip] analysis already submitted: {tasks['analysis']['task_id']}")
        return

    files = sorted(ART.glob("*.md"))
    if not files:
        raise SystemExit("No artifacts to upload")
    print("Uploading artifacts as a zipped collection:")
    for f in files:
        print(f"  - {f.name}")

    resp = client.store_file_content(
        name="icpms_literature_bundle",
        file_path=str(ART),
        as_collection=True,
    )
    entry_id = resp.data_storage.id
    uri = f"data_entry:{entry_id}"
    print(f"Uploaded collection -> {uri}")

    req = TaskRequest(name=JobNames.ANALYSIS, query=QUERY)
    task_id = str(client.create_task(req, files=[uri]))
    print(f"[submit] analysis -> {task_id}")

    tasks["analysis"] = {
        "task_id": task_id,
        "job": str(JobNames.ANALYSIS),
        "data_entry": str(entry_id),
    }
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    print(f"Wrote {TASKS_FILE}")


if __name__ == "__main__":
    main()
