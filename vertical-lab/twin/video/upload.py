"""Upload out/twin2/video/campaign.mp4 to the lab's YouTube channel: public, subscribers not notified. Only the lead
runs this, explicitly:

    python -m twin.video.upload --yes          # needs YOUTUBE_UPLOAD_TOKEN_PICKLE_B64 (upload + read only)
    python -m twin.video.upload --yes --file out/twin2/video/lab3d_preview.mp4 --meta out/twin2/video/\
        lab3d_preview_meta.json --privacy unlisted          # another cut: its own file, metadata and privacy

The same code path as longform.py's upload: youtube/yt_service.get_youtube_service("upload"), the channel checked
against youtube_upload.CHANNEL, the sha256 of the file looked up in out/youtube.json first (so the same bytes never go
up twice) and recorded there after. Title, description and tags come from out/twin2/video/youtube_meta.json
(twin.video.meta). The token is never printed.
"""
from __future__ import annotations

import datetime as dt
import json
import sys

from . import data as D

PRIVACY = "public"
NOTIFY = False


def upload(dst=None, meta_path=None, privacy: str = PRIVACY, notify: bool = NOTIFY, key: str | None = None) -> str:
    """Upload one file; the default is the public cut. Another cut passes its file, its metadata (title,
    description, tags) and its privacy; it is recorded in out/youtube.json under its own key."""
    sys.path.insert(0, str(D.HERE))
    sys.path.insert(0, str(D.HERE.parent))
    import youtube_upload as Y
    from googleapiclient.http import MediaFileUpload
    from youtube.yt_service import get_youtube_service, with_triggering_link
    from pathlib import Path

    default = dst is None
    dst = Path(dst) if dst is not None else D.VID / "campaign.mp4"
    if default:
        from . import meta as M                 # the description again, so its code link is the commit uploaded from
        M.write(json.loads((D.VID / "final_record.json").read_text()))
    meta = json.loads(Path(meta_path or D.VID / "youtube_meta.json").read_text())
    if meta.get("placeholder"):
        raise SystemExit("the metadata says the cut was built on placeholder data: rebuild it from final data")
    rec = Y.load_record()
    digest = Y.sha256(dst)
    key = key or ("twin2/video/campaign.mp4" if default else "twin2/video/" + dst.name)
    for v in rec["videos"].get(key, []):
        if v["sha256"] == digest:
            print(f"already up: https://www.youtube.com/watch?v={v['id']}")
            return v["id"]
    yt = get_youtube_service("upload")
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    if me != Y.CHANNEL:
        raise SystemExit(f"the token is for channel {me}, not {Y.CHANNEL}")
    desc = with_triggering_link(meta["description"])
    body = {"snippet": {"title": meta["title"][:100], "description": desc, "tags": meta["tags"],
                        "categoryId": meta.get("categoryId", "28"), "defaultLanguage": "en",
                        "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False, "embeddable": True}}
    media = MediaFileUpload(str(dst), mimetype="video/mp4", chunksize=16 << 20, resumable=True)
    print(f"uploading {dst.name}: {privacy}, subscribers {'notified' if notify else 'not notified'}", flush=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=notify)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"uploaded {status.progress():.0%}", flush=True)
    vid = resp["id"]
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec["videos"].setdefault(key, []).append(dict(id=vid, sha256=digest, bytes=dst.stat().st_size,
                                                  commit=meta.get("commit"), uploaded=now, title=meta["title"][:100],
                                                  privacy=privacy, notified_subscribers=notify))
    Y.save_record(rec)
    print(f"https://www.youtube.com/watch?v={vid}")
    return vid


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--yes" not in a:
        raise SystemExit(__doc__)

    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    upload(opt("--file"), opt("--meta"), opt("--privacy", PRIVACY), key=opt("--key"))
