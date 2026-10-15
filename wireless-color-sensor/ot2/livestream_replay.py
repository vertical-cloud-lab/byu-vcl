#!/usr/bin/env python3
"""Pull frames out of the OT-2 livestream's last ~15 minutes, by lab clock time.

YouTube keeps a rolling DVR window on a live stream: the live HLS playlist
lists roughly the last 15 minutes of 2-second segments. So an event seen late
can still be replayed frame by frame, as long as it is fetched within that
window. On 2026-09-25 this is how the enclosure falling off the nozzle was
pinned to between 16:34:29 and 16:34:31, a minute after it happened, when the
only direct evidence was a hand in the next deck photo.

Runs on a Pi with a residential IP (YouTube refuses datacenter IPs), next to
``live_frame.py``, which does the playlist lookup:

    python3 livestream_replay.py 16:34:16 16:35:04          # one frame / second
    python3 livestream_replay.py 16:34:16 16:35:04 --step 2 --out replay/

Times are lab local time, the same clock the stream burns into each frame.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_frame as lf  # noqa: E402


def segments():
    """[(start epoch s, duration s, url)] for every segment still in the window."""
    text = lf.fetch(lf.resolve()).decode()
    out, t, dur = [], None, 0.0
    for line in text.splitlines():
        if line.startswith("#EXT-X-PROGRAM-DATE-TIME:"):
            t = datetime.fromisoformat(line.split(":", 1)[1]).timestamp()
        elif line.startswith("#EXTINF:"):
            dur = float(line.split(":", 1)[1].rstrip(","))
        elif line and not line.startswith("#"):
            out.append((t, dur, line))
            t = None if t is None else t + dur
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("start", help="HH:MM:SS, lab local time")
    p.add_argument("end", help="HH:MM:SS, lab local time")
    p.add_argument("--step", type=float, default=1.0, help="seconds between frames")
    p.add_argument("--out", default="replay")
    a = p.parse_args()

    day = datetime.now().strftime("%Y-%m-%d")
    t0 = datetime.strptime(f"{day} {a.start}", "%Y-%m-%d %H:%M:%S").timestamp()
    t1 = datetime.strptime(f"{day} {a.end}", "%Y-%m-%d %H:%M:%S").timestamp()
    os.makedirs(a.out, exist_ok=True)
    frames = []
    for start, dur, url in segments():
        if start is None or start + dur < t0 or start > t1:
            continue
        seg = os.path.join(a.out, f"seg_{int(start)}.ts")
        with open(seg, "wb") as fh:
            fh.write(lf.fetch(url))
        k = 0
        while k * a.step < dur:
            ts = start + k * a.step
            if t0 <= ts <= t1:
                name = os.path.join(a.out, "f_" + time.strftime("%H%M%S", time.localtime(ts))
                                    + f"_{int((ts % 1) * 10)}.jpg")
                # ffmpeg only ever sees a local file: the static build has no DNS.
                subprocess.run([lf.FFMPEG, "-loglevel", "error", "-y", "-ss", f"{k * a.step:.2f}",
                                "-i", seg, "-frames:v", "1", "-q:v", "4", name], check=True)
                frames.append(name)
            k += 1
        os.remove(seg)
    print(json.dumps(frames))
    if not frames:
        print("nothing in range -- the window only reaches back ~15 minutes", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
