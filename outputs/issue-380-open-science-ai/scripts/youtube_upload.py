#!/usr/bin/env python3
"""Upload the final MP4 to the BYU Vertical Cloud Lab channel: public, without notifying subscribers.

Uses the repo's upload-only token helper (youtube/yt_service.py) but calls videos.insert directly so
notifySubscribers=False can be passed (the helper does not expose it). Writes video/youtube.json.
Usage: python scripts/youtube_upload.py video/open_science_value_ai.mp4"""
import json, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from youtube.yt_service import get_youtube_service, with_triggering_link
from googleapiclient.http import MediaFileUpload

path = sys.argv[1]
PART2 = "--part2" in sys.argv
PART3 = "--part3" in sys.argv
chapters = open("video/chapters_part3.txt" if PART3 else ("video/chapters_part2.txt" if PART2 else "video/chapters.txt")).read().strip()
title = ("The value of open science in the age of AI, Part 3: forks, AI-era open source, science models" if PART3 else
         ("The value of open science in the age of AI, Part 2: the commons, openness over time, and our lab" if PART2 else "The value of open science in the age of AI: what the numbers show"))
intro2 = ("Part 2 of a research run for the BYU Vertical Cloud Lab (Part 1: https://www.youtube.com/watch?v=Aakq7PNsFpE). "
          "Openness as a function of time across 143 organizations; the open-science commons (PDB, arXiv, OSF, Papers with Code) under AI-era strain; "
          "how Anthropic and OpenAI talk about open source and science over time; the US open-source base (GitHub Innovation Graph); "
          "closed instruments and fragile additive-manufacturing makers; and an openness audit of the Digital Alloy Lab and the vertical cloud lab (#318).\n\n")
intro3 = ("Part 3 of a research run for the BYU Vertical Cloud Lab (Part 1: https://www.youtube.com/watch?v=Aakq7PNsFpE ; Part 2: https://www.youtube.com/watch?v=uujMO9R1tMc). "
          "Do open forks survive closing moves (GitHub activity); AI-era open-source infrastructure startups (17 case files); licence histories of 19 AI-for-science models; "
          "academic technology transfer vs open release; and AI agents writing the lab's own open record.\n\n")
desc = (intro3 if PART3 else (intro2 if PART2 else "")) + f"""What is open source and open science worth in the age of AI, and who captures that value? A six-hour research run for the BYU Vertical Cloud Lab: 9 Edison literature reviews, 121 company and project case files (904 cited sources), Epoch AI and OpenAlex data, market prices, 41 primary documents from AI labs and US policy, and 4,928 GitHub comments from AccelerationConsortium/ac-dev-lab and sparks-baird/self-driving-lab-demo. Software vs hardware vs the physical sciences; academia vs government (national labs) vs industry; long-standing companies vs VC startups; how Anthropic and OpenAI talk about open source and science; and what it means for the Digital Alloy Lab.

Chapters
{chapters}

Data, scripts, case files and sources (all open):
https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-380-20261123-2145/outputs/issue-380-open-science-ai

Narration is synthetic (Kokoro-82M, Apache-2.0); charts made with matplotlib. Research, scripts and video were produced by Claude (Anthropic) for the BYU Vertical Cloud Lab. Values are at the dates stated on screen; see the repository for sources and caveats."""
desc = with_triggering_link(desc)
yt = get_youtube_service("upload")
body = {"snippet": {"title": title, "description": desc, "categoryId": "28",
                    "tags": ["open source", "open science", "AI", "open hardware", "self-driving labs", "materials science",
                             "open weights", "commercial open source", "Anthropic", "OpenAI", "BYU", "Vertical Cloud Lab"]},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
media = MediaFileUpload(path, chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
req = yt.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=False)
resp = None
while resp is None:
    st, resp = req.next_chunk()
    if st: print(f"uploaded {st.progress():.0%}", flush=True)
vid = resp["id"]
json.dump({"part": 3 if PART3 else (2 if PART2 else 1), "id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "title": title, "privacy": "public",
           "notifySubscribers": False, "status": resp.get("status")}, open("video/youtube_part3.json" if PART3 else ("video/youtube_part2.json" if PART2 else "video/youtube.json"), "w"), indent=1)
print("VIDEO", vid)
