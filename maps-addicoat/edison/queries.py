"""Critical Edison Scientific (PaperQA3) literature queries on MAPS.

MAPS = Metal Additive manufacturing using Powder Sheets, a metal-powder-in-a-
polymer-binder sheet feedstock being commercialized by Addicoat (spin-out of
Trinity College Dublin) as a powder-bed-fusion / loose-powder alternative.

These queries are deliberately critical: they probe the scientific
underpinnings of the published MAPS studies (densification, binder pyrolysis
residue, grain-morphology control, austenitic-steel benchmarking) and the
commercial viability of the approach versus established laser powder bed
fusion (LPBF) and directed energy deposition (DED).

Run:  python queries.py dispatch     # create LITERATURE_HIGH tasks (resumable)
      python queries.py fetch         # poll + save answers to results/

The Edison API key is read from EDISON_API_KEY (fallback EDISON_PLATFORM_API_KEY)
and is never echoed.
"""

import json
import os
import sys
import time
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

HERE = Path(__file__).parent
TASKS_FILE = HERE / "tasks.json"
RESULTS_DIR = HERE / "results"

# Each query is critical / skeptical by design.
QUERIES = {
    "01_densification_and_defects": (
        "Critically evaluate the evidence that metal additive manufacturing "
        "using powder sheets (MAPS), in which metal powder is held in a polymer "
        "binder sheet and laser-fused, achieves relative density, porosity, and "
        "defect populations comparable to conventional laser powder bed fusion "
        "(LPBF). What independent or peer-reviewed evidence supports the claimed "
        ">99% density, and what porosity, lack-of-fusion, or delamination "
        "defects are reported between stacked sheets? Where is the evidence "
        "weak, single-source, or not independently reproduced?"
    ),
    "02_binder_pyrolysis_contamination": (
        "Critically assess the effect of the polymeric binder in powder-sheet "
        "metal additive manufacturing (MAPS) on the final part chemistry. How "
        "much carbon, oxygen, and nitrogen pickup results from binder pyrolysis "
        "during laser fusion, how is residual char/ash quantified, and how does "
        "this interstitial contamination affect mechanical properties, "
        "corrosion, and weldability compared with gas-atomized powder feedstock? "
        "Is binder burn-off complete and reproducible, and what is the evidence?"
    ),
    "03_grain_morphology_control_claim": (
        "Critically examine the claim that powder sheet / MAPS feedstock enables "
        "selection or control of grain morphology in laser additive "
        "manufacturing. Is there rigorous evidence that grain size, texture, or "
        "columnar-vs-equiaxed morphology can be controlled via the sheet "
        "feedstock independently of the laser thermal history, or is the "
        "microstructure governed by the same solidification physics as LPBF? "
        "Distinguish genuine new science from marketing claims."
    ),
    "04_austenitic_steel_benchmark": (
        "Critically review published benchmarking of MAPS / powder-sheet "
        "additive manufacturing using austenitic stainless steel (e.g. 316L) "
        "against conventional LPBF. How do yield strength, ductility, fatigue, "
        "anisotropy, and defect content compare, what sample sizes and "
        "statistics were used, and are the comparisons fair (same alloy, build "
        "parameters, post-processing)? Identify methodological weaknesses, "
        "missing fatigue/anisotropy data, and over-generalized conclusions."
    ),
    "05_commercial_viability_vs_lpbf": (
        "Provide a critical techno-economic assessment of metal additive "
        "manufacturing using powder sheets (MAPS, e.g. Addicoat) as a commercial "
        "alternative to loose-powder LPBF and DED. Consider build rate / "
        "throughput, sheet manufacturing cost and yield, feedstock cost per kg, "
        "achievable part size and geometric complexity, multi-material and "
        "functionally graded capability, machine retrofit cost, and the real "
        "magnitude of the powder-handling safety benefit. Where is the value "
        "proposition strongest and where is it likely overstated relative to "
        "incumbent metal AM and to sheet/foil-based AM such as ultrasonic "
        "additive manufacturing and laminated object manufacturing?"
    ),
}


def _client():
    key = os.environ.get("EDISON_API_KEY") or os.environ.get(
        "EDISON_PLATFORM_API_KEY"
    )
    if not key:
        raise SystemExit("No Edison API key in environment.")
    return EdisonClient(api_key=key.strip())


def _load_tasks():
    if TASKS_FILE.exists():
        return json.loads(TASKS_FILE.read_text())
    return {}


def _save_tasks(tasks):
    TASKS_FILE.write_text(json.dumps(tasks, indent=2, sort_keys=True))


def dispatch():
    client = _client()
    tasks = _load_tasks()
    for name, query in QUERIES.items():
        if tasks.get(name):
            print(f"skip {name}: already dispatched {tasks[name]}")
            continue
        task = TaskRequest(name=JobNames.LITERATURE_HIGH, query=query)
        task_id = client.create_task(task)
        tasks[name] = str(task_id)
        _save_tasks(tasks)
        print(f"dispatched {name}: {tasks[name]}")
        time.sleep(10)  # throttle to avoid 429
    print("all dispatched")


def fetch():
    client = _client()
    tasks = _load_tasks()
    RESULTS_DIR.mkdir(exist_ok=True)
    for name, task_id in tasks.items():
        resp = client.get_task(task_id)
        dump = resp.model_dump()
        status = dump.get("status")
        answer = dump.get("formatted_answer") or dump.get("answer") or ""
        print(f"{name}: status={status} answer_len={len(answer)}")
        if answer:
            (RESULTS_DIR / f"{name}.md").write_text(answer)
        (RESULTS_DIR / f"{name}.json").write_text(
            json.dumps(dump, indent=2, default=str)
        )


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "dispatch"
    {"dispatch": dispatch, "fetch": fetch}[cmd]()
