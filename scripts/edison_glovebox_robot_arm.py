"""Edison Scientific query: gloveboxes that integrate with robotic arms.

Follow-up to PR #78 (glovebox-options.md). Three subcommands, run separately so
the wait is always a single blocking foreground call (see CLAUDE.md):

    python scripts/edison_glovebox_robot_arm.py submit
    python scripts/edison_glovebox_robot_arm.py wait
    python scripts/edison_glovebox_robot_arm.py fetch

The API key comes from the EDISON_PLATFORM_API_KEY environment variable and is
never printed.
"""

import json
import os
import sys
import time
from pathlib import Path

from edison_client import EdisonClient, JobNames
from edison_client.models.app import TaskRequest

OUT = Path(__file__).resolve().parent.parent / "outputs" / "edison" / "glovebox-robot-arm-integration"
TASK_ID_FILE = OUT / "_task_id.json"

QUERY = """We are specifying an inert-atmosphere (argon) glovebox for an autonomous \
("self-driving") materials laboratory at Brigham Young University. The glovebox must house an \
automated powder dosing machine and store reactive, combustible metal powders (Al, Mg, Si, \
AlSi10Mg) at low O2 and H2O, and we want it to integrate cleanly with robotic arms - either an \
arm operating inside the box, or an external arm loading and unloading through an automated \
antechamber or load-lock. Budget context: we are choosing among a new LC Technologies LC-100/LC-180 \
(~$34K-$50K), used purifier-equipped systems (MBraun MB200MOD ~$12K, Vigor SG1200-750TS ~$14K, \
refurbished Labconco Protector + AtmosPure ~$28K), and a $3K purge-only Labconco that could be \
upgraded later.

Please survey the peer-reviewed literature, preprints, and technical documentation on gloveboxes \
and inert-atmosphere enclosures that have been successfully integrated with robotic manipulators \
in automated laboratories, and answer:

1. Which specific glovebox makes/models and enclosure designs have published precedent for \
robot-arm integration (e.g. MBraun, Inert, Vigor, LC Technologies, Angstrom Engineering, Terra \
Universal, or custom-built enclosures)? Cite the papers or preprints that describe them, and note \
which robot arm was used (UR3/UR5e, Kinova, Franka Emika, Dobot, Epson or Yaskawa SCARA, igus, \
Meca500, etc.) and how it was mounted and powered.

2. What are the design requirements and failure modes for operating a robot arm inside an argon \
glovebox? Specifically: outgassing and lubricant/grease compatibility with sub-ppm O2/H2O \
atmospheres; motor, driver and encoder heat rejection without convective air cooling; cable and \
power feedthrough options; particulate generation from gearboxes and belts and its effect on gas \
purifier columns and copper catalyst beds; servicing the arm without breaking atmosphere; and \
electrostatic discharge / ignition risk around combustible metal powders (NFPA 484 and 652).

3. What architectures exist for moving samples in and out without breaking atmosphere - motorized \
or automated antechambers, load-locks, pass-through chambers, vacuum transfer vessels, and \
glovebox-to-glovebox transfer? What cycle times and O2/H2O excursions have been reported for each, \
and how much argon do they consume per cycle?

4. What is published on automated powder dosing and dispensing inside an inert atmosphere - \
Mettler-Toledo Quantos dosing heads, screw/auger feeders, acoustic or vibratory dosing - including \
achievable accuracy for small masses (1 mg - 5 g) of reactive metal powders, triboelectric/static \
dosing errors in dry argon, powder flowability under argon, and how the dosing hardware was \
interfaced to robotics and to a lab information system?

5. Which published self-driving or autonomous laboratories operate inside gloveboxes for \
air-sensitive materials (battery, solid-state electrolyte, alloy, halide perovskite, air-sensitive \
catalysis)? For each, what do the authors report as practical lessons, maintenance burden, \
downtime causes, and what they would do differently?

6. Given the above, what would you recommend for our situation: (a) buy a purpose-built \
automation-ready glovebox, (b) retrofit a used purifier-equipped glovebox with an internal arm, or \
(c) keep the arm outside the box and automate only the antechamber transfer? Weigh capital cost, \
atmosphere integrity, data quality for reactive-powder work, and the risk of contaminating the \
purifier.

Prefer sources from 2015-2026. Provide direct citations with DOIs or URLs. Where vendor \
documentation or a product page is the only source, say so explicitly and keep it clearly separated \
from peer-reviewed evidence."""


def client() -> EdisonClient:
    return EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])


def submit() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "query.md").write_text(QUERY + "\n")
    job = JobNames.LITERATURE_HIGH
    task = client().create_task(
        TaskRequest(
            name=job,
            query=QUERY,
            tags=["byu-vcl", "glovebox", "robotic-arm", "pr-78"],
        )
    )
    task_id = getattr(task, "task_id", None) or str(task)
    payload = {"task_id": str(task_id), "job": str(job), "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    TASK_ID_FILE.write_text(json.dumps(payload, indent=2) + "\n")
    print("submitted:", json.dumps(payload))


TERMINAL = {"success", "fail", "failed", "cancelled", "error", "crashed"}


def wait(poll: int = 60, max_wall: int = 2100) -> None:
    task_id = json.loads(TASK_ID_FILE.read_text())["task_id"]
    c = client()
    t0 = time.time()
    while True:
        task = c.get_task(task_id=task_id)
        status = str(getattr(task, "status", task)).lower()
        elapsed = int(time.time() - t0)
        print(f"[{elapsed:>5}s] status: {status}", flush=True)
        if any(s in status for s in TERMINAL):
            print("terminal status reached")
            return
        if elapsed > max_wall:
            print("wall-clock budget exhausted; still running")
            return
        time.sleep(poll)


def fetch() -> None:
    task_id = json.loads(TASK_ID_FILE.read_text())["task_id"]
    c = client()
    task = c.get_task(task_id=task_id, verbose=True)
    data = task.model_dump(mode="json") if hasattr(task, "model_dump") else dict(task)
    (OUT / "task_verbose.json").write_text(json.dumps(data, indent=2, default=str) + "\n")
    answer = data.get("answer") or (data.get("environment_frame") or {})
    if isinstance(answer, str) and answer.strip():
        (OUT / "answer.md").write_text(answer.strip() + "\n")
        print("wrote answer.md", len(answer), "chars")
    else:
        print("no top-level answer string; see task_verbose.json")
    try:
        files = c.list_files(trajectory_id=str(task_id))
        (OUT / "files_listing.json").write_text(json.dumps(files, indent=2, default=str) + "\n")
        print("files:", json.dumps(files, default=str)[:2000])
    except Exception as exc:  # noqa: BLE001
        print("list_files failed:", type(exc).__name__, exc)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "submit"
    {"submit": submit, "wait": wait, "fetch": fetch}[cmd]()
