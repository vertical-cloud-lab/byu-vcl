#!/usr/bin/env python3
"""Submit an Edison ANALYSIS task asking which TMS 2027 symposia would most
welcome the CubXL platform IF it is extended to autonomous electrochemistry
(potentiostat/electrode integration for electrodeposition, electrolyte
screening, corrosion, electrometallurgy, energy storage, etc.).

Reuses the same bundle as the top-10 task: the draft abstract plus the full
call-for-abstracts text of all TMS 2027 symposia scraped from ProgramMaster.
Writes a SUBMITTED placeholder with the task id so fetching is resumable.

Usage:
    EDISON_API_KEY=... python scripts/edison/submit_tms_symposium_electrochem.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

HERE = Path(__file__).resolve().parents[2]
BUNDLE = HERE / "edison-trajectories" / "tms-symposium-top10" / "bundle"
TRAJ = HERE / "edison-trajectories" / "tms-symposium-electrochem"
SUBMITTED = TRAJ / "tms-symposium-electrochem-SUBMITTED.json"

QUERY = """\
We are deciding where to submit a conference abstract for the TMS 2027 Annual
Meeting & Exhibition (Orlando, FL, March 14-18, 2027; abstracts due July 15,
2026). The attached bundle contains:

  - abstract.md: our draft 143-word abstract, "Modular Benchtop Self-Driving
    Laboratory for Closed-Loop Aqueous Materials Chemistry Using
    Interchangeable Powder, Liquid, and Sensing Modules." It presents the
    CubXL, a modular gantry-based benchtop self-driving laboratory (SDL)
    running the open-source CubOS control layer (version-controlled YAML
    protocols, offline motion validation, local experiment database), with
    interchangeable deck modules for liquid handling, single-powder dosing via
    manually swappable cartridges, in-line pH measurement, vial
    capping/decapping, and camera-based monitoring.

  - tms2027-symposia-full-text.md (and tms2027-symposia.json): the COMPLETE
    call-for-abstracts text of ALL TMS 2027 symposia (~108), scraped from
    ProgramMaster (the same content TMS renders into each symposium's flyer
    PDF): title, sponsoring division/committee, organizers with affiliations,
    full scope text, and deadline.

NEW CONTEXT: we are strongly considering extending the platform to
ELECTROCHEMISTRY processes -- e.g., adding a potentiostat/galvanostat module
and electrode handling so the SDL can run closed-loop electrochemical
campaigns (candidate directions: electrodeposition/electroplating,
electrolyte formulation and screening, electrowinning/electrorefining at
vial scale, corrosion/passivation screening, energy-storage/battery
electrolyte or electrode screening, electrocatalysis). Nothing is built yet;
the abstract would present the platform plus a credible electrochemistry
roadmap, or a reframed electrochemistry-forward version of the current
aqueous-chemistry abstract.

Your task: recommend, ranked, the TOP 10 TMS 2027 symposia that would MOST
WELCOME an AUTONOMOUS ELECTROCHEMISTRY platform talk of this kind.

Requirements:

1. FULL-TEXT SWEEP WITH AN ELECTROCHEMISTRY LENS. Systematically consider all
   symposia in the attached set; do not shortlist by title alone. Sweep for
   electrochemistry-relevant scope language: electrodeposition, electrolytes,
   electrometallurgy, electrowinning/electrorefining, corrosion, batteries,
   energy storage/conversion, electrocatalysis, molten salt vs aqueous
   electrochemistry, sensors, and any scope inviting autonomous/high-
   throughput/closed-loop or AI/ML-guided experimentation. Explicitly flag
   HIDDEN GEMS whose titles would never be shortlisted but whose full scope
   text fits.

2. ORGANIZER BACKGROUNDS. For each candidate, look up the research
   backgrounds of the listed organizers (electrochemistry, lab automation,
   self-driving labs, high-throughput experimentation, open hardware).
   Organizer receptiveness matters as much as scope fit. Note relevant
   organizer backgrounds in each rationale.

3. FOR EACH OF THE TOP 10, report:
   - rank, symposium title, sponsoring division/committee;
   - fit score out of 10 for an electrochemistry-forward CubXL abstract;
   - 2-4 sentence rationale quoting operative phrases from the scope text;
   - organizer-background notes (who, affiliation, receptive or not, why);
   - whether it is a HIDDEN GEM;
   - which electrochemistry application framing (electrodeposition,
     electrolyte screening, corrosion, electrometallurgy, batteries, ...)
     maximizes fit for that symposium, and whether a compliant <=150-word
     abstract can credibly make that framing given nothing is built yet.

4. RISK ASSESSMENT. For the top 3, note the risk of proposing an
   electrochemistry capability that is still a roadmap item rather than a
   demonstrated result, and how to word the abstract honestly (e.g.,
   "extensible to", "we present the architecture and initial integration
   of...") without overclaiming.

5. BOTTOM LINE. The single best-fit symposium for the electrochemistry
   direction, plus two backups, and one sentence each on why. Also state
   whether the electrochemistry framing opens meaningfully better venues than
   the aqueous-chemistry framing, or whether it is better kept as one line
   inside an aqueous-chemistry abstract ("future modules include a
   potentiostat for closed-loop electrochemistry").
"""


def main() -> None:
    api_key = (os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit("No EDISON_API_KEY / EDISON_PLATFORM_API_KEY in environment")

    client = EdisonClient(api_key=api_key)

    resp = client.store_file_content(name="tms-symposium-electrochem-bundle", file_path=str(BUNDLE), as_collection=True)
    uri = f"data_entry:{resp.data_storage.id}"
    print("uploaded bundle:", uri)

    task = TaskRequest(name=JobNames.ANALYSIS, query=QUERY)
    task_id = client.create_task(task, files=[uri])
    task_id = str(task_id)
    print("submitted ANALYSIS task:", task_id)

    TRAJ.mkdir(parents=True, exist_ok=True)
    SUBMITTED.write_text(json.dumps({"task_id": task_id, "bundle_uri": uri}, indent=2))
    print("wrote", SUBMITTED)


if __name__ == "__main__":
    main()
