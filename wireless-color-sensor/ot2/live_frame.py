#!/usr/bin/env python3
"""Grab the newest frame of the OT-2 livestream, from a Pi's residential IP.

YouTube refuses player extraction from datacenter IPs, so this runs on a Pi
with ``~/.venvs/ytframes`` (yt-dlp) and the static ffmpeg in ``~/ytframes/bin``.
It resolves the channel's live 720p HLS playlist once (cached for 50 min),
fetches only the newest 2-second segment with urllib -- the static ffmpeg
cannot resolve DNS -- and has ffmpeg keep the last frame of that local file.

    python3 live_frame.py OUT.jpg

The frame is ~3 s behind real time (measured 2.5-3.6 s on 2026-09-25 against
the clock the stream burns into every frame), so after a robot move wait ~5 s
before grabbing. ``frame_local`` in the output is when the frame was captured,
lab local time -- the same clock as the burned-in overlay -- so a frame can be
matched to a move without trusting the lag.

``grab()`` is what ``enclosure_height_cal.py`` and ``livestream_replay.py``
import.
"""
import json, os, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = os.path.expanduser("~/ytframes/bin/ffmpeg")
YTDLP = os.path.expanduser("~/.venvs/ytframes/bin/yt-dlp")
CHANNEL_LIVE = "https://www.youtube.com/channel/UCZ5KNGkEEqDsRVn0Nlfn0IA/live"
OT2_TITLE = "OT-2 stream"
CACHE = os.path.join(HERE, "live-playlist.json")
UA = ("Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0 Safari/537.36")


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def ot2_watch_url():
    """The channel's live OT-2 stream, picked by title.

    The channel carries more than one live stream. On 2026-09-29 its /live URL
    returned the powder doser's, so a frame from CHANNEL_LIVE was of the wrong
    machine. Fall back to CHANNEL_LIVE only if no live OT-2 stream is listed.
    """
    listing = subprocess.run(
        [YTDLP, "--js-runtimes", "node", "--no-warnings", "--flat-playlist",
         "--playlist-end", "8", "--print", "%(id)s|%(live_status)s|%(title)s",
         CHANNEL_LIVE.rsplit("/", 1)[0] + "/streams"],
        capture_output=True, text=True, timeout=120).stdout
    for line in listing.splitlines():
        vid, status, title = (line.split("|", 2) + ["", ""])[:3]
        if status == "is_live" and title.startswith(OT2_TITLE):
            return f"https://www.youtube.com/watch?v={vid}"
    return CHANNEL_LIVE


def resolve(refresh=False):
    if not refresh and os.path.exists(CACHE):
        c = json.load(open(CACHE))
        if time.time() - c["t"] < 3000:
            return c["url"]
    out = subprocess.run([YTDLP, "--js-runtimes", "node", "--no-warnings", "-f", "232",
                          "-g", ot2_watch_url()], capture_output=True, text=True,
                         timeout=120, check=True).stdout.strip().split("\n")[0]
    json.dump({"t": time.time(), "url": out}, open(CACHE, "w"))
    return out


def newest_segment(pl_url):
    """Return (start of the newest segment as UTC epoch s, its URL).

    YouTube states EXT-X-PROGRAM-DATE-TIME once, on the first segment, so the
    newest segment's start is that instant plus every EXTINF before it.
    """
    from datetime import datetime
    text = fetch(pl_url).decode()
    segs, t, dur = [], None, 0.0
    for line in text.splitlines():
        if line.startswith("#EXT-X-PROGRAM-DATE-TIME:"):
            t = datetime.fromisoformat(line.split(":", 1)[1]).timestamp()
        elif line.startswith("#EXTINF:"):
            dur = float(line.split(":", 1)[1].rstrip(","))
        elif line and not line.startswith("#"):
            segs.append((t, line))
            t = None if t is None else t + dur
    if not segs:
        raise RuntimeError("empty playlist")
    return segs[-1]


def grab(out):
    """Write the newest livestream frame to OUT; return what is known about it."""
    for attempt in range(2):
        try:
            seg_start, seg = newest_segment(resolve(refresh=attempt > 0))
            break
        except Exception as exc:  # stale URL -> re-resolve once
            if attempt:
                raise
            print("re-resolving:", exc, file=sys.stderr)
    data = fetch(seg)
    tmp = os.path.join(HERE, "seg.bin")
    with open(tmp, "wb") as fh:
        fh.write(data)
    # Decode the whole 2 s segment and keep overwriting one file, so what is
    # left is its last frame. (-sseof found no keyframe that late and wrote
    # nothing, silently.)
    if os.path.exists(out):
        os.remove(out)
    subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-i", tmp, "-update", "1",
                    "-q:v", "3", out], check=True)
    if not os.path.exists(out):
        raise RuntimeError("ffmpeg wrote no frame")
    now = time.time()
    seg_end = None if seg_start is None else seg_start + 2.0
    return {
        "out": out, "bytes": len(data), "frame_epoch": seg_end,
        "frame_local": None if seg_end is None else
            time.strftime("%H:%M:%S", time.localtime(seg_end)),
        "lag_s": None if seg_end is None else round(now - seg_end, 1),
    }


def main():
    print(json.dumps(grab(sys.argv[1])))


if __name__ == "__main__":
    main()
