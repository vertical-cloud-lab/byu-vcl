"""Submit high-effort Edison Scientific literature queries on ICP-MS sample
preparation and analysis of aluminum alloys (Agilent 8900 triple-quad).

Task IDs are written to tasks.json so they can be polled / fetched in a later
session if this run times out before the queries finish.
"""

import json
import os
from pathlib import Path

from edison_client import EdisonClient, JobNames
from edison_client.models.app import TaskRequest

HERE = Path(__file__).resolve().parent
TASKS_FILE = HERE / "tasks.json"


def get_client() -> EdisonClient:
    key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
    if not key:
        raise SystemExit("No Edison API key found in environment")
    return EdisonClient(api_key=key)


# Context shared by every query so the literature agent stays on-topic.
CONTEXT = (
    "Context: We operate an Agilent 8900 triple-quadrupole ICP-MS (ICP-QQQ) and "
    "want to characterize the elemental composition of metallic alloy samples, "
    "primarily aluminum alloys such as AlSi10Mg (Al-Si-Mg, e.g. from laser powder "
    "bed fusion feedstock) and 1100 aluminum wire, and silicon powder feedstock. "
    "Samples must be acid-digested into a clear, water-soluble solution with no "
    "suspended particles before nebulization. We are a university lab setting up "
    "this workflow for the first time. "
)

QUERIES = {
    "01_acid_digestion": (
        CONTEXT
        + "Provide a detailed, evidence-based protocol for acid-digesting aluminum "
        "and aluminum-silicon alloys (AlSi10Mg) for ICP-MS analysis. Compare hot-plate "
        "/ open-vessel digestion versus closed-vessel microwave-assisted digestion. "
        "Recommend specific acid mixtures and concentrations (e.g. HNO3, HCl/aqua regia, "
        "HF, H2O2, H3PO4) and volumes, heating temperatures and times, and sample mass, "
        "needed to fully dissolve the aluminum matrix AND the silicon content so no "
        "particulates remain. Address whether HF is required to dissolve elemental "
        "silicon/silicides, how to handle and neutralize HF safely, and boric-acid "
        "complexation. Give the safety hazards of each reagent."
    ),
    "02_icpms_measurement": (
        CONTEXT
        + "Give detailed best practices for measuring aluminum-alloy digests on an "
        "Agilent 8900 triple-quadrupole ICP-MS. Cover isotope selection for Al, Si, Mg, "
        "Fe, Cu, Mn, Zn, Ti, Cr, Ni and trace elements; major spectral and polyatomic "
        "interferences in an aluminum/nitric-acid matrix and how MS/MS modes with He "
        "collision gas, H2, O2, and NH3 reaction gases (including mass-shift methods) "
        "remove them; recommended internal standards (Sc, Ge, Rh, In, Bi); plasma and "
        "torch settings; and how to deal with the very high aluminum matrix (e.g. via "
        "dilution) to avoid detector saturation and matrix suppression."
    ),
    "03_qaqc_calibration": (
        CONTEXT
        + "Describe a rigorous QA/QC and calibration strategy for quantitative ICP-MS "
        "of aluminum-alloy digests. Cover external calibration vs standard addition vs "
        "isotope dilution; matrix matching; appropriate dilution factors; selection of "
        "certified reference materials (CRMs) for aluminum alloys; method blanks and "
        "reagent blanks; spike/recovery tests; detection and quantification limits; "
        "contamination control and labware cleaning (acid washing); and sources of "
        "systematic error specific to high-aluminum matrices."
    ),
    "04_hf_free_digestion": (
        CONTEXT
        + "IMPORTANT CONSTRAINT: our lab wants to AVOID hydrofluoric acid (HF) entirely "
        "if at all possible, for safety reasons. Provide a detailed, evidence-based "
        "review of HF-FREE methods for getting silicon-bearing aluminum alloys "
        "(especially AlSi10Mg, ~10 wt% Si, with eutectic Si and silicide phases) and "
        "silicon powder into a clear, particle-free, water-soluble solution suitable "
        "for ICP-MS. Evaluate and compare, with specific reagents, concentrations, "
        "volumes, temperatures, times, and vessel types: (1) tetrafluoroboric acid "
        "(HBF4) digestion and how its hazards/handling compare to free HF; (2) alkaline "
        "fusion / sinter methods (e.g. NaOH, Na2O2, Na2CO3, LiBO2/Li2B4O7 lithium "
        "metaborate/tetraborate fusion) followed by acid dissolution; (3) alkaline "
        "dissolution (NaOH/KOH) of the aluminum matrix; (4) HNO3+HCl/aqua-regia-only "
        "digestion and whether the Si-rich phases can be dissolved or must be filtered; "
        "(5) pressurized/high-temperature microwave digestion without HF. For each "
        "route, state whether silicon itself can be quantitatively recovered, what "
        "happens to the undissolved silicon, the dissolved-solids/salt burden it adds "
        "to the ICP-MS, boron/sodium/lithium spectral or matrix consequences, blank and "
        "contamination implications, and which trace elements may be lost or "
        "contaminated. Conclude with a recommended HF-free workflow for a university "
        "lab: one route if silicon must be quantified, and one simpler route if silicon "
        "does NOT need to be quantified (e.g. only the Al matrix and trace metals)."
    ),
}


def main() -> None:
    client = get_client()
    tasks = {}
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())

    for key, query in QUERIES.items():
        if tasks.get(key, {}).get("task_id"):
            print(f"[skip] {key} already submitted: {tasks[key]['task_id']}")
            continue
        req = TaskRequest(name=JobNames.LITERATURE_HIGH, query=query)
        task_id = client.create_task(req)
        task_id = str(task_id)
        print(f"[submit] {key} -> {task_id}")
        tasks[key] = {"task_id": task_id, "job": str(JobNames.LITERATURE_HIGH)}
        TASKS_FILE.write_text(json.dumps(tasks, indent=2))

    print(f"\nWrote {TASKS_FILE}")


if __name__ == "__main__":
    main()
