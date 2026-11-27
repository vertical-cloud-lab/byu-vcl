"""Edison literature queries behind notes/vertical_lab_worth_it.md (issue #407).

Three subcommands, each one blocking call so that it can run in a CI session (CLAUDE.md, "Edison Scientific"):

    python worth_it_edison.py submit     # create the tasks, write out/edison/worth_it_<slug>/_task_id.json
    python worth_it_edison.py wait       # poll until every task is finished (time.sleep inside Python)
    python worth_it_edison.py fetch      # write answer.md and trajectory.json.gz beside each _task_id.json

The answers are Edison's, not checked line by line. The note says where a claim rests on one. Needs
EDISON_PLATFORM_API_KEY and ``pip install edison-client`` on Python 3.10 to 3.13 (it does not install on 3.14).
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "out" / "edison"
DONE = {"success", "fail", "failed", "cancelled", "error", "truncated"}

# slug -> (job, query). LITERATURE_HIGH for the two questions the note leans on most, PRECEDENT for the yes/no one.
QUERIES: dict[str, tuple[str, str]] = {
    "worth_it_instruments_in_storage": (
        "PRECEDENT",
        "Has anyone housed powered, operating laboratory or production instruments (not passive inventory such as "
        "samples, reagents, tools or spare parts) inside the trays or carriers of a vertical lift module (VLM), "
        "vertical carousel, paternoster or other automated storage and retrieval system, so that the storage machine "
        "brings the instrument to a fixed access opening where a person or robot loads it, and the instrument keeps "
        "running (with power, data, gas or exhaust) while its tray is stored? Include laboratory automation, "
        "biobanks, pharmacies, incubator hotels, burn-in and test racks in electronics manufacturing, server or "
        "battery-cycling racks, and patents."),
    "worth_it_vlm_lab_storage": (
        "LITERATURE_HIGH",
        "Vertical lift modules (VLMs), vertical carousels and automated storage and retrieval systems (AS/RS) used "
        "in laboratories, biobanks, hospital and central-fill pharmacies, clean rooms and research facilities: what "
        "is stored (samples, consumables, reagents, tools, instruments), measured tray or carrier access times and "
        "picks per hour, reported benefits with numbers (floor space saved, pick accuracy, inventory traceability, "
        "ergonomics, access control), and reported problems (downtime, maintenance, being a single point of failure, "
        "what happens when the machine faults with items inside). Which of the reported benefits come from storing "
        "many passive items densely, and would any apply to a small number of instruments that run in place?"),
    "worth_it_goods_to_person": (
        "LITERATURE",
        "Goods-to-person versus person-to-goods order picking in manufacturing and warehousing, with vertical lift "
        "modules in particular: travel-time and throughput models for VLMs (for example Meller and Klote 2004; "
        "Dukic, Opetuk and Lerher 2015; Rosi et al. 2016; Sgarbossa, Calzavara and Persona 2019; Calzavara et al.), "
        "dual-command cycle times as a function of height, vertical speed and acceleration, typical trays per hour "
        "for one access opening, dual-tray (two-level) openings, the conditions under which a VLM is economical "
        "(number of stock-keeping units, pick frequency, floor cost) and when it is not, and comparisons with "
        "shelving, horizontal carousels, mini-load AS/RS, shuttle systems and autonomous mobile robots."),
    "worth_it_mobile_manipulators": (
        "LITERATURE_HIGH",
        "Mobile manipulators (a robot arm on an autonomous mobile base) working in chemistry, materials and "
        "life-science laboratories and in manufacturing machine tending, for example the Liverpool mobile robotic "
        "chemist (Burger et al. 2020, KUKA KMR iiwa), CELISCA Rostock's H20 robots, Fraunhofer's Kevin, Biosero and "
        "Thermo Fisher mobile robots, Astech's and others' MiR or Omron base with a UR arm: reported driving speeds "
        "and the speed limits set where people share the space, time to dock and localize at a station (touch-off, "
        "fiducial or camera calibration) and the positioning accuracy reached, pick-and-place cycle times, success "
        "rates and failures per number of operations, uptime, share of time spent charging, and what share of total "
        "workflow time is robot transport as opposed to instrument time. Include the requirements of ISO 3691-4, "
        "ISO 10218, ISO/TS 15066 and ANSI/RIA R15.08 on speed and separation where they are discussed."),
    "worth_it_lab_layouts": (
        "LITERATURE",
        "Published descriptions of facility-scale automated, self-driving or cloud laboratories (Emerald Cloud Lab "
        "and the Carnegie Mellon cloud lab, Strateos, the Acceleration Consortium, Ginkgo Bioworks' foundry and its "
        "reconfigurable automation carts, Automata LINQ, the A-Lab at Berkeley, Argonne's Polybot, the Liverpool "
        "autonomous labs, Samsung ASTRAL, BAM, IBM RoboRXN, biofoundries): how the instruments are arranged "
        "(benches served by people, benches served by mobile robots, rails or linear tracks, arm-centred workcells, "
        "conveyors or magnetic transport, vertical stacking or storage), floor area and number of instruments, what "
        "limits throughput (instrument time, transport, sample preparation, human decisions, maintenance), measured "
        "utilization, and lessons reported about layout choice, reconfigurability and serving several users at once."),
    "worth_it_vibration_moving_instruments": (
        "LITERATURE",
        "What happens to precision laboratory instruments when they are moved routinely rather than left in place: "
        "analytical and micro balances, optical microscopes and profilometers, tabletop SEMs, X-ray diffractometers "
        "and XRF, nanoindenters and hardness testers, laser-diffraction particle sizers, potentiostats. Shock and "
        "vibration limits in transport versus in operation, loss of levelling or calibration after a move and the "
        "requalification or settling and warm-up time needed (for example balance guidance in USP <41> and <1251>, "
        "OIML R 76, manufacturers' relocation guidance), and evidence from instruments mounted on moving platforms "
        "such as mobile laboratories, ships, vehicles, AGVs or automated storage systems."),
    "worth_it_shared_lab_queueing": (
        "LITERATURE",
        "Queueing and scheduling in shared automated laboratories and in flexible job shops with transport robots: "
        "how waiting time and throughput depend on the number of transport robots or AGVs, on a single shared "
        "transfer point, and on instruments that block for hours; effect of adding external or multi-user load to an "
        "automated lab or cloud lab (utilization against waiting, scheduling policies, priority between internal and "
        "external work); evidence on whether transport or instrument time is the bottleneck in laboratory "
        "automation, and published rules for sizing the number of mobile robots."),
}


def _client():
    from edison_client import EdisonClient

    return EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])


def submit() -> None:
    from edison_client import JobNames

    client = _client()
    for slug, (job, query) in QUERIES.items():
        folder = OUT / slug
        id_file = folder / "_task_id.json"
        if id_file.exists():
            print("already submitted:", slug, flush=True)
            continue
        task_id = client.create_task({"name": JobNames[job], "query": query})
        folder.mkdir(parents=True, exist_ok=True)
        id_file.write_text(json.dumps({"task_id": str(task_id), "job": job, "query": query,
                                       "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                                      indent=1))
        print("submitted:", slug, job, flush=True)


def _ids() -> dict[str, str]:
    return {slug: json.loads((OUT / slug / "_task_id.json").read_text())["task_id"]
            for slug in QUERIES if (OUT / slug / "_task_id.json").exists()}


def wait(max_minutes: float = 50.0, every_s: float = 120.0) -> None:
    client = _client()
    ids = _ids()
    t0 = time.time()
    while True:
        status = {}
        for slug, task_id in ids.items():
            try:
                status[slug] = str(client.get_task(task_id=task_id, lite=True).status)
            except Exception as exc:  # a transient API error should not end the wait
                status[slug] = "poll-error:" + type(exc).__name__
        left = [s for s, v in status.items() if v not in DONE]
        print(time.strftime("%H:%M:%SZ", time.gmtime()), {s.replace("worth_it_", ""): v for s, v in status.items()},
              flush=True)
        if not left or (time.time() - t0) > max_minutes * 60:
            break
        time.sleep(every_s)


def fetch() -> None:
    client = _client()
    for slug, task_id in _ids().items():
        folder = OUT / slug
        task = client.get_task(task_id=task_id, verbose=True)
        status = str(task.status)
        if status not in DONE:
            print("not finished:", slug, status, flush=True)
            continue
        data = json.loads(task.model_dump_json())
        with gzip.open(folder / "trajectory.json.gz", "wt", compresslevel=9) as fh:
            json.dump(data, fh, indent=1, default=str)
        answer = getattr(task, "formatted_answer", None) or getattr(task, "answer", None)
        if not answer:
            env = (data.get("environment_frame") or {}).get("state", {}).get("state", {})
            resp = env.get("response", {}).get("answer", {}) if isinstance(env, dict) else {}
            answer = resp.get("formatted_answer") or resp.get("answer")
        (folder / "answer.md").write_text((answer or f"(no answer text; status {status})").rstrip() + "\n")
        print("fetched:", slug, status, len(answer or ""), "chars", flush=True)


if __name__ == "__main__":
    {"submit": submit, "wait": wait, "fetch": fetch}[sys.argv[1]]()
