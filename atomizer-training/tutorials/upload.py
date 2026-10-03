"""Upload the built tutorials to the BYU VCL channel as unlisted and record the ids in uploads.json, per draft.

Uses the upload-only token (YOUTUBE_UPLOAD_TOKEN_PICKLE_B64) through ../../youtube/yt_service.py. That token cannot delete
or replace a video, so each draft is a new set of uploads and older drafts stay up until someone removes them in Studio
(or an @claude-youtube run does). Playlists need the full token too: see ../../youtube/make_playlist.py.

    python upload.py                 # uploads every out/*.mp4 not yet in the current draft
    python upload.py 02-during       # one
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
sys.path.insert(0, REPO)
from youtube.yt_service import upload_video
from scripts import TUTORIALS, VOICE

DRAFT = "draft 4"
LOG = f"{HERE}/uploads.json"
PR = "https://github.com/vertical-cloud-lab/byu-vcl/pull/255"
DESC = ("Draft tutorial for review, assembled from the AMAZEMET rePowder training at BYU Vertical Cloud Lab (Sep 29–30 2026) "
        "and the team's first run (Oct 2 2026). Human narration: Bartosz Kalicki (AMAZEMET), cut from the training videos, "
        "stabilised and subtitled from Whisper. Synthetic narration: Microsoft Edge TTS " + VOICE + " at 1x, reading the SOP "
        "summary over 3D CadQuery/PyVista animations of each step and draw.io outlines. The written procedure, with a link to "
        f"every moment of the source videos: {PR} (atomizer-training/). Issue #124.")


def main():
    log = json.load(open(LOG)) if os.path.exists(LOG) else {}
    if log and DRAFT not in log and "draft 1" not in log:      # first-draft file: one flat dict of tutorials
        log = {"draft 1": log}
    done = log.setdefault(DRAFT, {})
    keys = sys.argv[1:] or [k for k in TUTORIALS if os.path.exists(f"{HERE}/out/{k}.mp4")]
    for k in keys:
        if k in done:
            print(k, "already uploaded:", done[k]["url"]); continue
        path = f"{HERE}/out/{k}.mp4"
        title = TUTORIALS[k]["title"]
        print("uploading", k, title, flush=True)
        vid = upload_video(path, title, DESC, privacy="unlisted", tags=["atomizer", "rePowder", "AMAZEMET", "BYU VCL", "tutorial"])
        done[k] = {"video_id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "title": title,
                   "uploaded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "privacy": "unlisted",
                   "size_bytes": os.path.getsize(path)}
        json.dump(log, open(LOG, "w"), indent=1)
        print(k, "->", done[k]["url"], flush=True)


if __name__ == "__main__":
    main()
