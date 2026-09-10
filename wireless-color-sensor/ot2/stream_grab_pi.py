#!/usr/bin/env python3
"""Pull single frames out of a YouTube livestream archive, by video offset.

This is the half that runs *on the OT-2 stream-cam Pi*, as ~/ytframes/grab.py.
Committed here so the pair is reproducible; ``frames_from_stream.py`` on the
other side drives it over SSH. Needs ~/.venvs/ytframes (yt-dlp) and a static
ffmpeg/ffprobe in ~/ytframes/bin.

Runs on the OT-2 stream-cam Pi because YouTube refuses player extraction from
datacenter IPs ("Sign in to confirm you're not a bot" on any Actions runner).

Deliberately does *not* let ffmpeg touch the network: the static ffmpeg build
has no working DNS (statically linked glibc cannot use NSS), so segments are
fetched with urllib and ffmpeg only ever opens a local file. That also keeps
the download to one ~250 kB segment per frame instead of an index fetch plus a
range read per invocation.

The HLS media playlist for an 8 h archive lists ~4800 six-second segments in
order, so the segment holding offset t is found by walking #EXTINF durations.
The playlist is cached; segments are cached too, since three reads 1.4 s apart
usually land in the same one.

Job list arrives as JSON on stdin::

    [{"video_id": "...", "offset": 22228, "name": "frame.jpg"}, ...]
"""

import json
import os
import subprocess
import sys
import urllib.request

HERE = os.path.expanduser("~/ytframes")
FFMPEG = os.path.join(HERE, "bin", "ffmpeg")
FFPROBE = os.path.join(HERE, "bin", "ffprobe")
YTDLP = os.path.expanduser("~/.venvs/ytframes/bin/yt-dlp")
UA = ("Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0 Safari/537.36")


def fetch(url, path=None, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    if path:
        with open(path, "wb") as fh:
            fh.write(data)
    return data


def playlist(video_id, refresh=False):
    """Return [(start_s, duration_s, url)] for every segment of the archive."""
    cache = os.path.join(HERE, "pl-%s.json" % video_id)
    if os.path.exists(cache) and not refresh:
        return json.load(open(cache))
    url = subprocess.run(
        [YTDLP, "--js-runtimes", "node", "-f", "232", "-g",
         "https://www.youtube.com/watch?v=%s" % video_id],
        capture_output=True, text=True, check=True).stdout.strip().split("\n")[0]
    text = fetch(url).decode("utf-8", "replace")
    segs, t, dur = [], 0.0, None
    for line in text.splitlines():
        if line.startswith("#EXTINF:"):
            dur = float(line[len("#EXTINF:"):].rstrip(","))
        elif line.startswith("http") and dur is not None:
            segs.append([round(t, 3), dur, line])
            t += dur
            dur = None
    json.dump(segs, open(cache, "w"))
    return segs


def segment_index(segs, offset):
    lo, hi = 0, len(segs) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if segs[mid][0] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo


def grab(video_id, offset, out_path, width=960, quality=4):
    segs = playlist(video_id)
    i = segment_index(segs, offset)
    start, _dur, url = segs[i]
    seg_path = os.path.join(HERE, "segcache", "%s-%d.ts" % (video_id, i))
    os.makedirs(os.path.dirname(seg_path), exist_ok=True)
    if not os.path.exists(seg_path):
        fetch(url, seg_path)

    # YouTube TS segments keep the archive-absolute timeline: the segment that
    # begins 22225.67 s into the stream reports start_time=22225.666667. So the
    # input-side seek takes the absolute offset, not a within-segment one --
    # passing the latter seeks before the first packet and silently yields no
    # frame at all.
    probe = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=start_time",
         "-of", "default=nw=1:nk=1", seg_path],
        capture_output=True, text=True, check=True).stdout.strip()
    seg_t0 = float(probe) if probe not in ("", "N/A") else start
    within = max(0.0, offset - seg_t0)
    subprocess.run(
        [FFMPEG, "-nostdin", "-loglevel", "error", "-y",
         "-ss", "%.3f" % (seg_t0 + within), "-i", seg_path, "-frames:v", "1",
         "-vf", "scale=%d:-2" % width, "-q:v", str(quality), out_path],
        check=True)
    if not os.path.exists(out_path):  # fall back to decoding from the segment head
        subprocess.run(
            [FFMPEG, "-nostdin", "-loglevel", "error", "-y", "-i", seg_path,
             "-ss", "%.3f" % within, "-frames:v", "1",
             "-vf", "scale=%d:-2" % width, "-q:v", str(quality), out_path],
            check=True)
    return {"segment": i, "segment_start_s": start, "segment_t0_s": seg_t0,
            "within_s": round(within, 3)}


def main():
    jobs = json.load(sys.stdin)
    outdir = os.path.join(HERE, "out")
    os.makedirs(outdir, exist_ok=True)
    results = []
    for j in jobs:
        out = os.path.join(outdir, j["name"])
        try:
            info = grab(j["video_id"], j["offset"], out,
                        width=j.get("width", 960), quality=j.get("quality", 4))
            info.update(name=j["name"], offset=j["offset"], ok=True,
                        bytes=os.path.getsize(out))
        except Exception as exc:  # noqa: BLE001 - one bad frame must not kill the batch
            info = {"name": j["name"], "offset": j["offset"], "ok": False,
                    "error": "%s: %s" % (type(exc).__name__, exc)}
        results.append(info)
        print(json.dumps(info), file=sys.stderr, flush=True)
    print(json.dumps(results))


if __name__ == "__main__":
    main()
