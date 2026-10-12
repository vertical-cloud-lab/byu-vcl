#!/usr/bin/env python3
"""Fetch compact player info (storyboards + format list) for YouTube video IDs.

Runs on the stream-cam Pi because YouTube refuses player extraction from CI
runners. Reads IDs from the file given as argv[1], appends one JSON line per
video to argv[2]. Skips IDs already present in the output. Sleeps between
requests so as not to hammer YouTube from one residential IP.
"""
import json, os, subprocess, sys, time

YTDLP = os.path.expanduser("~/.venvs/ytframes/bin/yt-dlp")
ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
out = sys.argv[2]
done = set()
if os.path.exists(out):
    for l in open(out):
        try:
            done.add(json.loads(l)["id"])
        except Exception:
            pass
for vid in ids:
    if vid in done:
        continue
    t0 = time.time()
    p = None
    try:
        p = subprocess.run([YTDLP, "--js-runtimes", "node", "-J", "--no-warnings",
                            "https://www.youtube.com/watch?v=" + vid],
                           capture_output=True, text=True, timeout=180)
        d = json.loads(p.stdout)
        rec = {k: d.get(k) for k in ("id", "title", "duration", "timestamp",
                                     "release_timestamp", "upload_date",
                                     "live_status", "channel_id")}
        rec["description"] = (d.get("description") or "")[:1500]
        rec["sb"] = {}
        for f in d.get("formats", []):
            if f["format_id"] in ("sb0", "sb1"):
                rec["sb"][f["format_id"]] = {
                    k: f.get(k) for k in ("width", "height", "rows", "columns", "fps")}
                rec["sb"][f["format_id"]]["fragments"] = [
                    [fr["url"], fr.get("duration")] for fr in f.get("fragments", [])]
        rec["formats"] = [[f["format_id"], f.get("height"), f.get("protocol")]
                          for f in d.get("formats", [])
                          if f.get("vcodec") not in (None, "none")
                          and not f["format_id"].startswith("sb")]
        rec["ok"] = True
    except Exception as e:  # one bad video must not stop the batch
        rec = {"id": vid, "ok": False, "error": "%s: %s" % (type(e).__name__, str(e)[:300]),
               "stderr": p.stderr[-400:] if p is not None else ""}
    with open(out, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(vid, rec.get("ok"), round(time.time() - t0, 1), flush=True)
    time.sleep(2)
print("ALL DONE", flush=True)
