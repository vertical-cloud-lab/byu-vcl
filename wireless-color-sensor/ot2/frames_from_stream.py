"""Grab, and then *verify*, one livestream frame per colour measurement.

Two things make this more than a subtraction.

First, YouTube will not do player extraction from a datacenter IP, so the
fetching runs over SSH on the OT-2 stream-cam Pi (``grab.py`` lives there).

Second, the archive's timeline is not wall clock. For this stream, video offset
0 corresponds to ``release_timestamp`` at the very start but to
``release_timestamp + 67 s`` from somewhere in the first three hours onward --
a step, not a drift, presumably a stall the archive simply concatenates
across. Trusting the metadata alone would place every link ~67 s early, which
at a 17 s-per-position scan is more than one read position out.

The stream burns a ``%Y-%m-%d_%H-%M-%S`` clock into the top-left of every
frame, so the fix is a closed loop: grab at the estimated offset, OCR the
overlay, and if it disagrees with the wanted instant, shift by exactly the
error and grab again. Each frame therefore carries its own proof, and the
verified time is recorded next to it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
# The overlay is drawn in the lab's local time; Utah in September is MDT.
OVERLAY_UTC_OFFSET = timedelta(hours=-6)
OVERLAY_CROP = "crop=300:34:0:0,scale=900:-1,format=gray,negate"
STAMP_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})")


def ssh_host():
    user = os.environ["RPI_STREAM_CAM_USERNAME"]
    host = os.environ["RPI_STREAM_CAM_HOSTNAME"]
    return f"{user}@{host}"


def run_jobs(jobs):
    """Ask the Pi for a batch of frames; returns its per-frame result list."""
    payload = json.dumps(jobs)
    cmd = ["ssh", "-o", "StrictHostKeyChecking=no", ssh_host(),
           "cd ~/ytframes && python3 grab.py 2>/dev/null"]
    out = subprocess.run(cmd, input=payload, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def fetch_back(names, dest):
    """Pull a batch back in one round trip. tar rather than scp, because scp
    quoting of a remote file list is a minefield and these names contain +."""
    if not names:
        return
    os.makedirs(dest, exist_ok=True)
    remote = " ".join(shlex.quote(n) for n in names)
    subprocess.run(
        f"ssh -o StrictHostKeyChecking=no {ssh_host()} "
        f"{shlex.quote('cd ~/ytframes/out && tar cf - ' + remote)} "
        f"| tar xf - -C {shlex.quote(dest)}",
        shell=True, check=True, capture_output=True)


def read_stamp(path):
    """OCR the burned-in clock. Returns a naive local datetime, or None."""
    tmp = path + ".ocr.png"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", path,
                    "-vf", OVERLAY_CROP, tmp], check=True)
    text = subprocess.run(["tesseract", tmp, "-", "--psm", "7", "-c",
                           "tessedit_char_whitelist=0123456789-_"],
                          capture_output=True, text=True).stdout
    os.remove(tmp)
    m = STAMP_RE.search(text.replace("\n", ""))
    if not m:
        return None
    y, mo, d, h, mi, s = (int(g) for g in m.groups())
    return datetime(y, mo, d, h, mi, s)


def expected_local(t_utc_iso):
    t = datetime.strptime(t_utc_iso, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return (t + OVERLAY_UTC_OFFSET).replace(tzinfo=None)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--index", default=os.path.join(HERE, "measurement-stream-index.json"))
    p.add_argument("--out-dir", default=os.path.join(HERE, "frames"))
    p.add_argument("--report", default=os.path.join(HERE, "frames", "frames.json"))
    p.add_argument("--shift", type=float, default=-67.0,
                   help="initial guess for archive-timeline minus wall-clock")
    p.add_argument("--width", type=int, default=960)
    p.add_argument("--tolerance", type=float, default=1.0, help="seconds")
    p.add_argument("--max-rounds", type=int, default=3)
    p.add_argument("--stages", default="pos",
                   help="'pos' for scan positions only, 'all' for every reading")
    p.add_argument("--per-position", type=int, default=1,
                   help="1-based index of the repeated read at a position to photograph")
    args = p.parse_args(argv)

    index = json.load(open(args.index))
    rows = index["readings"]
    if args.stages == "pos":
        rows = [r for r in rows if r["stage"].startswith("pos")]
        by_pos = {}
        for r in rows:
            by_pos.setdefault((r["run_file"], r["stage"]), []).append(r)
        rows = [v[min(max(args.per_position - 1, 0), len(v) - 1)] for v in by_pos.values()]
        rows.sort(key=lambda r: r["t_response_epoch"])

    release = {s["video_id"]: s["start_epoch"] for s in index["meta"]["streams"]}
    targets = []
    for r in rows:
        if "video_id" not in r:
            continue
        # '+' is legal in a filename but reads as a space in some URL
        # contexts, and these paths end up in markdown image links.
        name = "%s-%s.jpg" % (os.path.splitext(r["run_file"])[0].replace("xscan-", ""),
                              r["stage"].replace("+", "p"))
        targets.append({
            "row": r,
            "name": name,
            "want_local": expected_local(r["t_response_utc"]),
            "offset": r["t_response_epoch"] - release[r["video_id"]] + args.shift,
        })

    resolved = {}
    for rnd in range(args.max_rounds):
        pending = [t for t in targets if t["name"] not in resolved]
        if not pending:
            break
        jobs = [{"video_id": t["row"]["video_id"], "offset": round(t["offset"], 2),
                 "name": t["name"], "width": args.width} for t in pending]
        results = {r["name"]: r for r in run_jobs(jobs)}
        fetch_back([t["name"] for t in pending if results.get(t["name"], {}).get("ok")],
                   args.out_dir)
        for t in pending:
            res = results.get(t["name"], {})
            if not res.get("ok"):
                continue
            path = os.path.join(args.out_dir, t["name"])
            got = read_stamp(path)
            if got is None:
                continue
            err = (got - t["want_local"]).total_seconds()
            if abs(err) <= args.tolerance:
                resolved[t["name"]] = {
                    "name": t["name"], "run_file": t["row"]["run_file"],
                    "stage": t["row"]["stage"], "position": t["row"]["position"],
                    "experiment_id": t["row"]["experiment_id"],
                    "total": t["row"]["total"], "channels": t["row"]["channels"],
                    "t_response_utc": t["row"]["t_response_utc"],
                    "video_id": t["row"]["video_id"],
                    "video_offset_s": round(t["offset"], 2),
                    "url": "https://www.youtube.com/watch?v=%s&t=%ds"
                           % (t["row"]["video_id"], int(round(t["offset"]))),
                    "overlay_local": got.strftime("%Y-%m-%d_%H-%M-%S"),
                    "overlay_error_s": err, "rounds": rnd + 1,
                }
            else:
                t["offset"] -= err  # the overlay is truth; walk straight to it
            print(f"  round {rnd+1} {t['name']}: want {t['want_local']}, "
                  f"got {got}, err {err:+.0f}s")

    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    out = [resolved[t["name"]] for t in targets if t["name"] in resolved]
    json.dump({"shift_used_s": args.shift, "frames": out}, open(args.report, "w"), indent=2)
    print(f"{len(out)}/{len(targets)} frames verified against the burned-in clock")
    return 0 if len(out) == len(targets) else 1


if __name__ == "__main__":
    raise SystemExit(main())
