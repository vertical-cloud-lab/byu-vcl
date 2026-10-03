#!/usr/bin/env python3
"""Fetch time windows of YouTube videos at the best resolution available, as HLS segments, on the stream-cam Pi.

YouTube refuses player extraction from datacenter IPs, so this runs on the Pi (residential IP). The Pi's static ffmpeg
cannot resolve DNS, so, like ~/ytframes/grab.py, it never lets ffmpeg near the network: the media playlist and the
segments are fetched with urllib and simply concatenated (TS segments concatenate as they are; for fMP4 the
#EXT-X-MAP init segment goes first). Only the segments that overlap a window are fetched, so a 40 s clip out of an
hour-long video costs a few MB, not the whole file. Downloads are throttled (RATE bytes/s) for the Pi's Wi-Fi.

Job list on stdin, one window per entry (windows of the same video share one playlist fetch):

    [{"video_id": "58wJ_Khwgyk", "start": 400.0, "end": 460.0, "name": "58wJ_Khwgyk_400"}, ...]

Writes ~/atomizer-hls/<name>.ts (or .mp4 for fMP4) and <name>.json: the format, its height, and t0, the video time of
the first byte (the sum of #EXTINF durations before the first fetched segment). Video only: the clips take their
audio from the full .m4a already on the runner.

    python3 hls_sections.py < jobs.json
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

OUT = os.path.expanduser("~/atomizer-hls")
YTDLP = os.path.expanduser("~/.venvs/ytframes/bin/yt-dlp")
RATE = float(os.environ.get("HLS_RATE", 3e6))
UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
# best HLS video stream; prefer h264 at the same height (plays everywhere, decodes fast)
FORMAT = "bv*[protocol^=m3u8][vcodec^=avc1]/bv*[protocol^=m3u8]"


def fetch(url, timeout=120):
    t = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
            break
        except Exception:  # noqa: BLE001 - retry transient network errors
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    wait = len(data) / RATE - (time.time() - t)
    if wait > 0:
        time.sleep(wait)
    return data


def playlist(video_id):
    """[(start_s, duration_s, url)] for every segment, plus the init-segment URL (fMP4) and the format's info."""
    best = None
    for fmt in (FORMAT, "bv*[protocol^=m3u8]"):
        r = subprocess.run([YTDLP, "--js-runtimes", "node", "--no-warnings", "-f", fmt,
                            "-O", "%(format_id)s|%(height)s|%(vcodec)s|%(url)s",
                            "https://www.youtube.com/watch?v=%s" % video_id], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            best = r.stdout.strip().splitlines()[0].split("|", 3)
            break
    if not best:
        raise RuntimeError("no HLS video format: " + r.stderr[-300:])
    fmt_id, height, vcodec, url = best
    # a master playlist (rare here) would need one more hop to the media playlist
    text = fetch(url).decode("utf-8", "replace")
    if "#EXT-X-STREAM-INF" in text:
        url = [ln for ln in text.splitlines() if ln.startswith("http")][-1]
        text = fetch(url).decode("utf-8", "replace")
    segs, t, dur, init = [], 0.0, None, None
    for line in text.splitlines():
        if line.startswith("#EXT-X-MAP:"):
            init = line.split('URI="', 1)[1].split('"', 1)[0]
        elif line.startswith("#EXTINF:"):
            dur = float(line[len("#EXTINF:"):].split(",")[0])
        elif line.startswith("http") and dur is not None:
            segs.append((round(t, 3), dur, line))
            t += dur
            dur = None
    return segs, init, {"format_id": fmt_id, "height": int(height) if height.isdigit() else height, "vcodec": vcodec}


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = json.load(sys.stdin)
    by_video = {}
    for j in jobs:
        by_video.setdefault(j["video_id"], []).append(j)
    for vid, js in by_video.items():
        try:
            segs, init, info = playlist(vid)
        except Exception as exc:  # noqa: BLE001 - one bad video must not stop the rest
            print(json.dumps({"video_id": vid, "ok": False, "error": str(exc)[:300]}), flush=True)
            continue
        cache = {}
        for j in js:
            name = j["name"]
            if os.path.exists(os.path.join(OUT, name + ".json")):
                continue
            idx = [i for i, (s, d, _) in enumerate(segs) if s + d > j["start"] and s < j["end"]]
            if not idx:
                print(json.dumps({"name": name, "ok": False, "error": "window outside video"}), flush=True)
                continue
            ext = ".mp4" if init else ".ts"
            nbytes = 0
            with open(os.path.join(OUT, name + ext + ".part"), "wb") as fh:
                if init:
                    if "init" not in cache:
                        cache["init"] = fetch(init)
                    fh.write(cache["init"])
                for i in idx:
                    data = fetch(segs[i][2])
                    fh.write(data)
                    nbytes += len(data)
            os.rename(os.path.join(OUT, name + ext + ".part"), os.path.join(OUT, name + ext))
            meta = dict(info, video_id=vid, name=name, file=name + ext, t0=segs[idx[0]][0],
                        t1=round(segs[idx[-1]][0] + segs[idx[-1]][1], 3), window=[j["start"], j["end"]],
                        segments=[idx[0], idx[-1]], bytes=nbytes)
            json.dump(meta, open(os.path.join(OUT, name + ".json"), "w"))
            print(json.dumps(meta), flush=True)


if __name__ == "__main__":
    main()
