#!/usr/bin/env python3
"""Fetch a live YouTube broadcast from its start as 2 s DASH fragments (url&sq=N), the way yt-dlp --live-from-start does,
but in parallel and resumable, so the part already broadcast can be had without waiting for the broadcast to end.
Usage: live_frags.py <format.json from yt-dlp --live-from-start -j> <format_id> <outdir> [first_sq] [last_sq]

Runs on the stream-cam Pi (YouTube refuses the player to a CI runner). The live HLS playlist only reaches back 15 min,
and yt-dlp's --download-sections refuses live-from-start formats, hence this. Used for the Oct 6 2026 run
(../runs/2026-10-06.md): 7,661 fragments of the 144p rendition, 13:01 to 17:16 MDT, 115 MB in 5.5 min.

    ~/.venvs/ytframes/bin/yt-dlp --js-runtimes node --live-from-start -f 160 -j URL > fmt.json
    python3 live_frags.py fmt.json 160 frags/        # X-Head-Seqnum, the newest fragment, is the default end
    cat frags/*.mp4 > joined.mp4                     # then anywhere: ffmpeg -i joined.mp4 -c copy stream.mp4

Fragment N starts 2N s into the broadcast. RATE caps the download for the Pi's Wi-Fi."""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
info = json.load(open(sys.argv[1])); fid = sys.argv[2]; out = sys.argv[3]
f = [x for x in info["formats"] if x["format_id"] == fid][0]
url, hdr = f["url"], f.get("http_headers", {})
first = int(sys.argv[4]) if len(sys.argv) > 4 else 0
req = urllib.request.Request(url + "&sq=0", headers=hdr)
with urllib.request.urlopen(req, timeout=60) as r:
    head = int(r.headers["X-Head-Seqnum"])
last = int(sys.argv[5]) if len(sys.argv) > 5 else head
RATE = 1.5e6  # bytes/s across all workers, well under the Wi-Fi cap
t0 = time.time(); got = [0]
def one(n):
    p = os.path.join(out, "%06d.mp4" % n)
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return n, 0
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url + "&sq=%d" % n, headers=hdr), timeout=60) as r:
                data = r.read()
            open(p + ".tmp", "wb").write(data); os.replace(p + ".tmp", p)
            got[0] += len(data)
            wait = got[0] / RATE - (time.time() - t0)
            if wait > 0: time.sleep(wait)
            return n, len(data)
        except Exception:  # noqa: BLE001 - retry transient network errors
            time.sleep(2 * (attempt + 1))
    return n, -1
print("head", head, "fetching", first, "to", last, flush=True)
bad = []
with ThreadPoolExecutor(4) as ex:
    for i, (n, size) in enumerate(ex.map(one, range(first, last + 1))):
        if size < 0: bad.append(n)
        if i % 500 == 0: print(time.strftime("%H:%M:%S"), "sq", n, "MB", round(got[0] / 1e6, 1), flush=True)
print("DONE", "bad", bad, "MB", round(got[0] / 1e6, 1), time.strftime("%H:%M:%S"), flush=True)
