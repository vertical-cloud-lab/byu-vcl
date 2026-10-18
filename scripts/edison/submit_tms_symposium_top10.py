#!/usr/bin/env python3
"""Submit an Edison ANALYSIS task asking for a top-10 TMS 2027 symposium
ranking for the CubXL self-driving-laboratory abstract, using the full
call-for-abstracts text of all TMS 2027 symposia (flyer-equivalent content
scraped from ProgramMaster) and the backgrounds of each symposium's organizers.

Attaches the draft abstract plus the full symposium set as a single zipped
collection. Writes a SUBMITTED placeholder with the task id so fetching is
resumable.

Usage:
    EDISON_API_KEY=... python scripts/edison/submit_tms_symposium_top10.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

HERE = Path(__file__).resolve().parents[2]
TRAJ = HERE / "edison-trajectories" / "tms-symposium-top10"
BUNDLE = TRAJ / "bundle"
SUBMITTED = TRAJ / "tms-symposium-top10-SUBMITTED.json"

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
    capping/decapping, and camera-based monitoring. The system targets
    closed-loop Bayesian-optimization campaigns for aqueous materials
    chemistry: solubility/dissolution measurements, pH-controlled
    precipitation, and leaching studies. The emphasis is the SYSTEM itself --
    modularity, low cost, open source, replicability -- and what it enables.

  - tms2027-symposia-full-text.md (and tms2027-symposia.json): the COMPLETE
    call-for-abstracts text of ALL TMS 2027 symposia (~108), scraped from
    ProgramMaster. This is the same content TMS renders into each symposium's
    flyer PDF: title, sponsoring division/committee, organizers with
    affiliations, full scope text, and deadline. Read the FULL SCOPE TEXT of
    every symposium, not just the titles -- several symposia have scopes far
    broader (or narrower) than their titles suggest.

Your task: recommend the TOP 10 symposia, ranked, for this abstract.

Requirements:

1. FULL-TEXT SWEEP. Systematically consider all symposia in the attached set.
   Do not shortlist by title alone. We specifically want HIDDEN GEMS: symposia
   whose titles would never be shortlisted but whose full scope text invites
   autonomous experimentation, robotic/high-throughput workflows, digital
   labs, open-source instrumentation, or solution-phase/hydrometallurgical
   chemistry where our platform's capabilities (powder dosing into liquids,
   pH tracking, sealed-vial handling) are directly relevant. Explicitly flag
   which of your top 10 are hidden gems versus obvious candidates.

2. ORGANIZER BACKGROUNDS. For each candidate symposium, look up and consider
   the research backgrounds of the listed organizers (publication record,
   research areas, involvement in self-driving labs / autonomous
   experimentation / materials acceleration platforms / open hardware).
   Organizer receptiveness matters as much as scope-text fit: an organizer
   who works on SDLs or lab automation is more likely to welcome and
   favorably schedule a systems-focused talk. Note relevant organizer
   backgrounds in your rationale for each ranked symposium.

3. FOR EACH OF THE TOP 10, report:
   - rank, symposium title, sponsoring division/committee;
   - fit score out of 10 for the abstract AS WRITTEN;
   - 2-4 sentence rationale grounded in specific language from the symposium's
     scope text (quote the operative phrases);
   - organizer-background notes (who, affiliation, why they would or would not
     be receptive);
   - whether it is a HIDDEN GEM (title alone would not have surfaced it);
   - any reframing/edits of the abstract that would strengthen the fit, and
     whether those edits fit within the 150-word TMS limit.

4. BOTTOM LINE. A clear recommendation: the single best-fit symposium, plus
   two backups, and one sentence on why. If the best home requires reframing
   (e.g., toward hydrometallurgy/leaching, characterization, or AI/ML
   workflows), say which reframing gives the highest acceptance likelihood
   for a systems-focused SDL talk.
"""


def main() -> None:
    api_key = (os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit("No EDISON_API_KEY / EDISON_PLATFORM_API_KEY in environment")

    client = EdisonClient(api_key=api_key)

    resp = client.store_file_content(name="tms-symposium-top10-bundle", file_path=str(BUNDLE), as_collection=True)
    uri = f"data_entry:{resp.data_storage.id}"
    print("uploaded bundle:", uri)

    task = TaskRequest(name=JobNames.ANALYSIS, query=QUERY)
    task_id = client.create_task(task, files=[uri])
    task_id = str(task_id)
    print("submitted ANALYSIS task:", task_id)

    SUBMITTED.write_text(json.dumps({"task_id": task_id, "bundle_uri": uri}, indent=2))
    print("wrote", SUBMITTED)


if __name__ == "__main__":
    main()
