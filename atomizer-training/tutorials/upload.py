"""Upload the built tutorials to the BYU VCL channel as unlisted and record the ids in uploads.json.

Uses the upload-only token (YOUTUBE_UPLOAD_TOKEN_PICKLE_B64) through ../../youtube/yt_service.py. Playlists need the
full token, so the playlist is a separate step: see ../../youtube/make_playlist.py (an @claude-youtube run).

    python upload.py                 # uploads every out/*.mp4 not yet in uploads.json
    python upload.py 02-during       # one
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
sys.path.insert(0, REPO)
from youtube.yt_service import upload_video
from scripts import TUTORIALS

LOG = f"{HERE}/uploads.json"
PR = "https://github.com/vertical-cloud-lab/byu-vcl/pull/255"
DESC = ("Draft tutorial for review, assembled automatically from the AMAZEMET rePowder training at BYU Vertical Cloud Lab "
        "(Sep 29–30 2026) and the team's first run (Oct 2 2026). Human narration: Bartosz Kalicki (AMAZEMET), cut from the "
        "training videos. Synthetic narration: Microsoft Edge TTS en-US-SteffanNeural at 1x, reading the SOP summary. "
        "Step animations and the written procedure with a link to every moment of the source videos: "
        f"{PR} (atomizer-training/). Issue #124.")


def main():
    done = json.load(open(LOG)) if os.path.exists(LOG) else {}
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
        json.dump(done, open(LOG, "w"), indent=1)
        print(k, "->", done[k]["url"], flush=True)


if __name__ == "__main__":
    main()
