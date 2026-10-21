#!/usr/bin/env python3
"""Cut time windows out of a YouTube livestream (finished archive or live DVR).

Runs on a stream-cam Pi, because YouTube refuses player extraction from an
Actions runner. Segments are fetched with urllib at a capped rate and
concatenated into one .ts per window; ffmpeg never touches the network.

    clips.py probe VIDEO_ID FORMAT
    clips.py fetch < jobs.json   # [{"video_id", "format", "name", and either
                                  #   "start"/"end" (archive offsets, s) or
                                  #   "utc_start"/"utc_end" (live, ISO UTC)}]
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

YTDLP = os.path.expanduser("~/.venvs/ytframes/bin/yt-dlp")
UA = ("Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0 Safari/537.36")
OUT = "/tmp/vclclips"
RATE = 1.0e6  # bytes/s: the Pi is on residential wifi and carrying its own stream


def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def media_playlist(video_id, fmt):
    url = subprocess.run(
        [YTDLP, "--js-runtimes", "node", "-f", fmt, "-g",
         "https://www.youtube.com/watch?v=%s" % video_id],
        capture_output=True, text=True, check=True).stdout.strip().split("\n")[0]
    return fetch(url).decode("utf-8", "replace")


def parse(text):
    """[(start_s, dur_s, sq, pdt, url)] in playlist order."""
    segs, t, dur, pdt = [], 0.0, None, None
    for line in text.splitlines():
        if line.startswith("#EXT-X-PROGRAM-DATE-TIME:"):
            pdt = dt.datetime.fromisoformat(line.split(":", 1)[1].replace("Z", "+00:00"))
        elif line.startswith("#EXTINF:"):
            dur = float(line[len("#EXTINF:"):].split(",")[0])
        elif line.startswith("http") and dur is not None:
            m = re.search(r"/sq/(\d+)/", line)
            segs.append((t, dur, int(m.group(1)) if m else None, pdt, line))
            t += dur
            dur, pdt = None, None
    return segs


def probe(video_id, fmt):
    text = media_playlist(video_id, fmt)
    for line in text.splitlines():
        if line.startswith("#") and not line.startswith(("#EXTINF", "#EXT-X-PROGRAM")):
            print(line[:120])
    segs = parse(text)
    print("segments", len(segs), "total_s", round(sum(s[1] for s in segs), 1))
    for s in segs[:2] + segs[-2:]:
        print("  start %.1f dur %.3f sq %s pdt %s" % (s[0], s[1], s[2], s[3]))


def window(job):
    text = media_playlist(job["video_id"], job["format"])
    segs = parse(text)
    if "start" in job:  # finished archive: walk #EXTINF from offset 0
        return [s[4] for s in segs if s[0] + s[1] > job["start"] and s[0] < job["end"]]
    # live DVR: the playlist lists only recent segments, so build older ones by sq
    ref = next(s for s in segs if s[2] is not None and s[3] is not None)
    dur = ref[1]
    t0 = dt.datetime.fromisoformat(job["utc_start"])
    t1 = dt.datetime.fromisoformat(job["utc_end"])
    sq0 = ref[2] + int((t0 - ref[3]).total_seconds() // dur)
    sq1 = ref[2] + int((t1 - ref[3]).total_seconds() // dur)
    last = max(s[2] for s in segs if s[2] is not None)
    return [re.sub(r"/sq/\d+/", "/sq/%d/" % q, ref[4]) for q in range(sq0, min(sq1, last) + 1)]


def fetch_jobs(jobs):
    os.makedirs(OUT, exist_ok=True)
    for job in jobs:
        urls = window(job)
        path = os.path.join(OUT, job["name"] + ".ts")
        n, t_start = 0, time.time()
        with open(path, "wb") as fh:
            for url in urls:
                try:
                    data = fetch(url)
                except Exception as exc:  # noqa: BLE001 - note the gap, keep going
                    print(job["name"], "segment failed:", type(exc).__name__, file=sys.stderr)
                    continue
                fh.write(data)
                n += len(data)
                wait = n / RATE - (time.time() - t_start)
                if wait > 0:
                    time.sleep(wait)
        print(json.dumps({"name": job["name"], "segments": len(urls), "bytes": n}), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "probe":
        probe(sys.argv[2], sys.argv[3])
    else:
        fetch_jobs(json.load(sys.stdin))
