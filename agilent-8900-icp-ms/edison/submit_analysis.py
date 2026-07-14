"""Submit an Edison ANALYSIS task that ingests all downloaded literature
artifacts and produces a single cohesive set of recommendations / SOP draft.

The artifacts directory is uploaded as a single zipped collection
(store_file_content(..., as_collection=True)); uploading individual files
separately is known to make the ANALYSIS task fail silently.

The resulting task_id is recorded in tasks.json (under "analysis" or
"analysis_hf_free" depending on ANALYSIS_MODE) so it can be fetched in a later
session if this run times out before it finishes.
"""

import json
import os
import shutil
import tempfile
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

# HF-avoidance-prioritized synthesis (reviewer constraint: the lab wants to avoid
# hydrofluoric acid entirely if at all possible).
QUERY_HF_FREE = (
    "The attached markdown files are four high-effort literature reviews about using "
    "an Agilent 8900 triple-quadrupole ICP-MS to characterize the elemental "
    "composition of aluminum alloys (AlSi10Mg, 1100 aluminum wire) and silicon "
    "powder, which must first be digested into a clear, particle-free, water-soluble "
    "solution. They cover (1) acid digestion protocols, (2) ICP-MS/MS measurement, "
    "(3) QA/QC and calibration, and (4) a dedicated review of HF-FREE digestion "
    "options. "
    "HARD CONSTRAINT FROM THE LAB: avoid hydrofluoric acid (HF) entirely if at all "
    "possible. Treat tetrafluoroboric acid (HBF4) as NOT genuinely HF-free, because "
    "it hydrolyzes to HF on heating/storage and requires HF-equivalent precautions; "
    "recommend it only as a last resort with explicit caveats. "
    "Synthesize ONE cohesive, non-redundant, HF-FREE-PRIORITIZED set of practical "
    "recommendations for a university lab setting up this workflow for the first "
    "time. Produce: (a) a concise executive summary that leads with the HF-free "
    "decision; (b) a step-by-step SOP outline built around two HF-free routes - "
    "Route A (lithium metaborate LiBO2 fusion) when silicon must be quantified, and "
    "Route B (aqua regia / HNO3+HCl digestion with filtration of the Si-rich residue) "
    "when silicon does not need to be quantified - plus simple non-HF digestion for "
    "low-Si 1100 aluminum; cover instrument setup/tuning, measurement, and QA/QC, "
    "including the extra dilution and Li/B matrix issues that fusion introduces and "
    "how to handle the Si-residue loss in Route B; (c) a consolidated table of "
    "recommended reagents, isotopes, reaction-gas modes, and internal standards; "
    "(d) a prioritized safety checklist for the HF-free reagents actually used "
    "(hot concentrated acids, high-temperature fusion, caustic), and an explicit "
    "note on why HF and HBF4 are avoided; and (e) the key open decisions the lab must "
    "resolve (e.g. whether silicon itself must be quantified at all, or whether Si "
    "can be measured by another technique). Reconcile conflicting advice and call out "
    "where the reports agree."
)


def select_query() -> tuple[str, str, str]:
    """Return (task_key, bundle_name, query) for the configured analysis run."""
    mode = os.environ.get("ANALYSIS_MODE", "hf_free")
    if mode == "hf_free":
        return "analysis_hf_free", "icpms_literature_bundle_hf_free", QUERY_HF_FREE
    return "analysis", "icpms_literature_bundle", QUERY


def get_client() -> EdisonClient:
    key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
    if not key:
        raise SystemExit("No Edison API key found in environment")
    return EdisonClient(api_key=key)


def main() -> None:
    client = get_client()
    tasks = json.loads(TASKS_FILE.read_text())

    task_key, bundle_name, query = select_query()

    if tasks.get(task_key, {}).get("task_id"):
        print(f"[skip] {task_key} already submitted: {tasks[task_key]['task_id']}")
        return

    # Upload only the numbered literature reviews; exclude any prior synthesis
    # output so the analysis agent synthesizes from primary reviews only.
    files = sorted(f for f in ART.glob("[0-9][0-9]_*.md"))
    if not files:
        raise SystemExit("No artifacts to upload")

    with tempfile.TemporaryDirectory(prefix="icpms_bundle_") as tmp:
        tmpdir = Path(tmp)
        print("Uploading artifacts as a zipped collection:")
        for f in files:
            shutil.copy2(f, tmpdir / f.name)
            print(f"  - {f.name}")

        resp = client.store_file_content(
            name=bundle_name,
            file_path=str(tmpdir),
            as_collection=True,
        )
    entry_id = resp.data_storage.id
    uri = f"data_entry:{entry_id}"
    print(f"Uploaded collection -> {uri}")

    req = TaskRequest(name=JobNames.ANALYSIS, query=query)
    task_id = str(client.create_task(req, files=[uri]))
    print(f"[submit] {task_key} -> {task_id}")

    tasks[task_key] = {
        "task_id": task_id,
        "job": str(JobNames.ANALYSIS),
        "data_entry": str(entry_id),
    }
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    print(f"Wrote {TASKS_FILE}")


if __name__ == "__main__":
    main()
