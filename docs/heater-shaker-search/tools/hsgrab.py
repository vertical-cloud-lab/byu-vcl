#!/usr/bin/env python3
"""Grab single full-resolution frames from YouTube videos by offset (runs on the Pi).

Based on ~/ytframes/grab.py, but picks the best HLS rendition up to 1080p for any
video (uploads as well as livestream archives), and fetches only the one ~5 s
segment that holds each requested offset. ffmpeg (static, no DNS) only ever
opens local files. Jobs on stdin: [{"video_id":..., "offset":..., "name":...}].
Frames land in /tmp/hs81/out/; delete /tmp/hs81 afterwards.
"""
import json, os, subprocess, sys, urllib.request
HERE = "/tmp/hs81"
FFMPEG = os.path.expanduser("~/ytframes/bin/ffmpeg")
FFPROBE = os.path.expanduser("~/ytframes/bin/ffprobe")
YTDLP = os.path.expanduser("~/.venvs/ytframes/bin/yt-dlp")
UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
FMT = "bv*[protocol=m3u8_native][height<=1080]/bv*[protocol=m3u8_native]"

def fetch(url, path=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120) as r:
        data = r.read()
    if path:
        open(path, "wb").write(data)
    return data

def playlist(vid):
    cache = os.path.join(HERE, "pl-%s.json" % vid)
    if os.path.exists(cache):
        return json.load(open(cache))
    url = subprocess.run([YTDLP, "--js-runtimes", "node", "--no-warnings", "-f", FMT, "-g",
                          "https://www.youtube.com/watch?v=" + vid],
                         capture_output=True, text=True, check=True).stdout.strip().split("\n")[0]
    segs, t, dur = [], 0.0, None
    init = None
    for line in fetch(url).decode("utf-8", "replace").splitlines():
        if line.startswith("#EXT-X-MAP:") and 'URI="' in line:
            init = line.split('URI="', 1)[1].split('"', 1)[0]
        elif line.startswith("#EXTINF:"):
            dur = float(line[8:].rstrip(","))
        elif line.startswith("http") and dur is not None:
            segs.append([round(t, 3), dur, line, init]); t += dur; dur = None
    json.dump(segs, open(cache, "w"))
    return segs

def grab(vid, offset, out):
    segs = playlist(vid)
    i = max(k for k, s in enumerate(segs) if s[0] <= offset) if offset >= 0 else 0
    seg = os.path.join(HERE, "seg", "%s-%d.ts" % (vid, i))
    os.makedirs(os.path.dirname(seg), exist_ok=True)
    if os.path.exists(seg[:-3] + ".mp4"):
        seg = seg[:-3] + ".mp4"
    if not os.path.exists(seg):
        data = fetch(segs[i][2])
        if len(segs[i]) > 3 and segs[i][3]:  # fMP4: prepend the init segment
            ipath = os.path.join(HERE, "seg", "%s-init.mp4" % vid)
            if not os.path.exists(ipath):
                fetch(segs[i][3], ipath)
            data = open(ipath, "rb").read() + data
            seg = seg[:-3] + ".mp4"
        open(seg, "wb").write(data)
    probe = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=start_time",
                            "-of", "default=nw=1:nk=1", seg], capture_output=True, text=True).stdout.strip()
    t0 = float(probe) if probe not in ("", "N/A") else segs[i][0]
    if seg.endswith(".mp4"):
        t0 = 0.0
    within = max(0.0, offset - segs[i][0])
    subprocess.run([FFMPEG, "-nostdin", "-loglevel", "error", "-y", "-ss", "%.3f" % (t0 + within),
                    "-i", seg, "-frames:v", "1", "-q:v", "2", out], check=True)
    if not os.path.exists(out):
        subprocess.run([FFMPEG, "-nostdin", "-loglevel", "error", "-y", "-i", seg, "-ss", "%.3f" % within,
                        "-frames:v", "1", "-q:v", "2", out], check=True)
    return {"segment": i, "bytes_segment": os.path.getsize(seg)}

jobs = json.load(sys.stdin)
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
res = []
for j in jobs:
    out = os.path.join(HERE, "out", j["name"])
    try:
        info = grab(j["video_id"], float(j["offset"]), out); info.update(name=j["name"], ok=True)
    except Exception as e:
        info = {"name": j["name"], "ok": False, "error": "%s: %s" % (type(e).__name__, str(e)[:200])}
    res.append(info); print(json.dumps(info), file=sys.stderr, flush=True)
print(json.dumps(res))
