#!/usr/bin/env python3
"""Upload Part 4 (corrections after the independent review): public, without notifying subscribers.
Same upload-only token helper as scripts/youtube_upload.py. Writes video/youtube_part4.json.
Usage: python scripts/youtube_upload_part4.py video/open_science_value_ai_part4.mp4"""
import json, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from youtube.yt_service import get_youtube_service, with_triggering_link
from googleapiclient.http import MediaFileUpload

path = sys.argv[1]
chapters = open("video/chapters_part4.txt").read().strip()
title = "The value of open science in the age of AI, Part 4: corrections after an independent review"
assert len(title) <= 100, len(title)
desc = f"""Part 4 of a research run for the BYU Vertical Cloud Lab (Part 1: https://www.youtube.com/watch?v=Aakq7PNsFpE ; Part 2: https://www.youtube.com/watch?v=uujMO9R1tMc ; Part 3: https://www.youtube.com/watch?v=8P7iqUaVHyE).

An independent review checked the report's numbers against its own files and found 39 issues. All are fixed in the written report. This video covers the corrections that change the story:
- Do VC-era firms close up? The earlier videos said yes (-0.67 on a 0-4 openness scale), but that grouping counted open infrastructure such as the PDB and LAMMPS as pre-2000 companies. Grouped properly, the raw gap is -0.61. Adjusted for where each firm started, it is -0.09 (95% CI -0.45 to +0.28): convergence to the middle, not VC-era closing.
- Science does not converge on "open core": lab-automation and AI-for-science firms average 0.57, while scientific software and infrastructure averages 2.70.
- Licence changes rose after 2020 per organization-year too, from 3.4 to 8.2 per 100.
- Smaller fixes: forks, AI-era startups, AI-for-science model scores, open-hardware savings and the PDB's value.

Chapters
{chapters}

Resolution log (REVIEW_FINDINGS.md), video notes and all data (open):
https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-380-20261123-2145/outputs/issue-380-open-science-ai

Narration is synthetic (Kokoro-82M, Apache-2.0); charts made with matplotlib. Research, scripts and video were produced by Claude (Anthropic) for the BYU Vertical Cloud Lab. The written report is the current version."""
assert "<" not in desc and ">" not in desc
desc = with_triggering_link(desc)
yt = get_youtube_service("upload")
body = {"snippet": {"title": title, "description": desc, "categoryId": "28",
                    "tags": ["open source", "open science", "AI", "open hardware", "self-driving labs", "materials science",
                             "open weights", "commercial open source", "corrections", "BYU", "Vertical Cloud Lab"]},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
media = MediaFileUpload(path, chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
req = yt.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=False)
resp = None
while resp is None:
    st, resp = req.next_chunk()
    if st: print(f"uploaded {st.progress():.0%}", flush=True)
vid = resp["id"]
json.dump({"part": 4, "id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "title": title, "privacy": "public",
           "notifySubscribers": False, "status": resp.get("status")}, open("video/youtube_part4.json", "w"), indent=1)
print("VIDEO", vid)
