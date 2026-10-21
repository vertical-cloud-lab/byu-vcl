#!/usr/bin/env python3
"""Fetch a live YouTube broadcast's HLS segments from its DVR, by media-sequence number.

Runs on a Pi: YouTube refuses player extraction from CI runners. A broadcast that is still
live has no archive playlist, only a sliding live playlist, but every segment URL carries
/sq/<n>/, so older segments can be fetched by rewriting n. On picam-ot2's broadcasts a
segment is 2 s of 144p (itag 269, ~19 kB) and sq 0 sits 2 s x n before the first one; check
the burned-in clock rather than trusting that. The DVR reaches back about 4 h 50 min; older
segments come back empty or 404, and are skipped.

  live_dvr_fetch.py VIDEO FMT SQ_START SQ_END OUTDIR
  e.g. live_dvr_fetch.py z13xp1AcKag 269 0 5700 oct20/live

Skips segments already on disk. 4 at a time, average rate capped; only urllib touches the
network. Join with `cat VIDEO_sq*.ts > stream.ts` (zero-length files first removed).
"""
import getpass, os, re, subprocess, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

YTDLP = "/home/%s/.venvs/ytframes/bin/yt-dlp" % getpass.getuser()
UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
MAX_BPS = 1.5e6


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


vid, fmt, a, b, outdir = sys.argv[1:6]
os.makedirs(outdir, exist_ok=True)
m3u8 = subprocess.run([YTDLP, "-f", fmt, "-g", "https://www.youtube.com/watch?v=" + vid],
                      capture_output=True, text=True, check=True).stdout.strip().split("\n")[0]
url = [l for l in get(m3u8).decode().splitlines() if l.startswith("http")][-1]
todo = [sq for sq in range(int(a), int(b) + 1)
        if not os.path.exists(os.path.join(outdir, "%s_sq%06d.ts" % (vid, sq)))]
t0, total, errors = time.time(), [0], []


def one(sq):
    for attempt in range(3):
        try:
            data = get(re.sub(r"/sq/\d+/", "/sq/%d/" % sq, url))
            if not data:  # aged out of the DVR: YouTube answers 200 with no body
                errors.append("%d: empty" % sq)
                return
            open(os.path.join(outdir, "%s_sq%06d.ts" % (vid, sq)), "wb").write(data)
            total[0] += len(data)
            ahead = total[0] / MAX_BPS - (time.time() - t0)
            if ahead > 0:
                time.sleep(ahead)
            return
        except Exception as exc:  # noqa: BLE001
            err = "%d: %s" % (sq, exc)
            if "404" in str(exc):  # outside the DVR window: gone, do not retry
                break
            time.sleep(1)
    errors.append(err)


with ThreadPoolExecutor(4) as ex:
    list(ex.map(one, todo))
print("filled %d segments, %.1f MB, %.0f s, %d errors %s" % (len(todo) - len(errors), total[0] / 1e6,
      time.time() - t0, len(errors), errors[:5]), flush=True)
