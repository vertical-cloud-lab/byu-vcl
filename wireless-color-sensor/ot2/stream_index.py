"""Map every colour-sensor reading to the instant it was taken and to the livestream.

The readings carry no explicit timestamp. What they do carry is an
``experiment_id`` of the form ``"<label>-<epoch_ms>"``, minted by
``sensor_read.SensorLink.read`` immediately before the MQTT command is
published, plus ``latency_s``, the measured round trip. So the reading is
bracketed:

    request  = epoch_ms / 1000
    response = request + latency_s        <- the board has answered by here

The AS7341 integration happens between those two, much closer to ``response``
(the board reads, then publishes). ``response`` is what this module uses as
"the moment of measurement", and the bracket is carried along so the
uncertainty stays visible.

The OT-2 is livestreamed in rolling ~8 h segments to the ``BYU VCL Hardware
Streams`` channel. Given a segment's true start (``release_timestamp`` from the
YouTube metadata, *not* the scheduled time in its title), a reading at wall
clock ``t`` sits at video offset ``t - start`` seconds, which is what
``?v=<id>&t=<offset>s`` links to.

Usage::

    python3 stream_index.py                  # writes the JSON + markdown index
    python3 stream_index.py --offset-shift 4 # apply a measured a/v pipeline delay
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))

# Livestream segments covering the 2026-09-09 colour session. ``start_epoch`` is
# ``release_timestamp`` as reported by yt-dlp -- the moment the broadcast
# actually went live, which is what video offset 0 corresponds to. The title's
# "UTC 19:00" is the cron schedule and runs a minute or so early/late.
STREAMS = [
    {
        "video_id": "bQDrYpT3vaE",
        "title": "OT-2 stream picam-ot2, 2026-09-08 UTC 19:00",
        "start_epoch": 1788894076,  # 2026-09-08T19:01:16Z
        "duration_s": 28656,
    },
]

# Human-facing name for each run file, in the order they were executed.
RUNS = [
    ("xscan-run-2026-09-09.json", "slot 8, z 120", "first full cycle; slot empty"),
    ("xscan-slot7-2026-09-09.json", "slot 7, z 125", "requested +5 mm"),
    ("xscan-slot7-z120-2026-09-09.json", "slot 7, z 120", "height control"),
    ("xscan-slot7-z128-2026-09-09.json", "slot 7, z 128", "requested +3 mm; empty slot"),
    ("xscan-slot7-paint-2026-09-09.json", "slot 7, z 128, vials", "3-position paint run"),
    ("xscan-slot7-sweep-2026-09-09.json", "slot 7, z 128, vials", "9-position 10 mm sweep"),
    ("xscan-slot7-z129-press90-2026-09-09.json", "slot 7, z 129, press 90.0", "deeper press"),
]

CHANNELS = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")


def request_epoch(reading):
    """When the command went out, in epoch seconds.

    Readings taken after ``sensor_read`` learned to timestamp itself carry
    ``t_request_epoch`` outright. Older ones -- everything from 2026-09-09 --
    only have the epoch-ms suffix of ``experiment_id``, so fall back to that.

    Returns ``None`` rather than raising: a malformed id should cost one row of
    the index, not the whole index.
    """
    if reading.get("t_request_epoch") is not None:
        return float(reading["t_request_epoch"])
    tail = reading["experiment_id"].rsplit("-", 1)[-1]
    if not tail.isdigit():
        return None
    return int(tail) / 1000.0


def stream_for(epoch):
    for s in STREAMS:
        if s["start_epoch"] <= epoch <= s["start_epoch"] + s["duration_s"]:
            return s
    return None


def iso(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def hms(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 3600:d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"


def build(offset_shift=0.0):
    rows = []
    for filename, pose, note in RUNS:
        path = os.path.join(HERE, filename)
        if not os.path.exists(path):
            continue
        doc = json.load(open(path))
        run = doc["run"]
        for i, r in enumerate(doc["readings"]):
            req = request_epoch(r)
            if req is None:
                continue
            resp = (float(r["t_response_epoch"]) if r.get("t_response_epoch") is not None
                    else req + r.get("latency_s", 0.0))
            stream = stream_for(resp)
            row = {
                "run_file": filename,
                "pose": pose,
                "run_note": note,
                "run_started": run["started"],
                "index_in_run": i,
                "stage": r["stage"],
                "label": r["label"],
                "experiment_id": r["experiment_id"],
                "position": r.get("position"),
                "channels": r["channels"],
                "total": r["total"],
                "latency_s": r.get("latency_s"),
                "t_request_utc": iso(req),
                "t_response_utc": iso(resp),
                "t_request_epoch": round(req, 3),
                "t_response_epoch": round(resp, 3),
            }
            if stream:
                offset = resp - stream["start_epoch"] + offset_shift
                row.update({
                    "video_id": stream["video_id"],
                    "video_title": stream["title"],
                    "video_offset_s": round(offset, 1),
                    "video_offset_hms": hms(offset),
                    "url": f"https://www.youtube.com/watch?v={stream['video_id']}&t={int(round(offset))}s",
                })
            rows.append(row)
    rows.sort(key=lambda r: r["t_response_epoch"])
    return rows


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--offset-shift", type=float, default=-67.0,
                   help="seconds to add to every video offset. The archive "
                        "timeline is NOT wall clock: for bQDrYpT3vaE it runs "
                        "67 s behind from somewhere in the first three hours "
                        "onward, so a link computed from release_timestamp "
                        "alone lands a whole read position early. Verified at "
                        "27 points against the burned-in clock by "
                        "frames_from_stream.py.")
    p.add_argument("--json-out", default=os.path.join(HERE, "measurement-stream-index.json"))
    p.add_argument("--md-out", default=os.path.join(HERE, "measurement-stream-index.md"))
    args = p.parse_args(argv)

    rows = build(args.offset_shift)
    meta = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "offset_shift_s": args.offset_shift,
        "streams": STREAMS,
        "n_readings": len(rows),
        "method": ("t_request from the epoch-ms suffix of experiment_id; "
                   "t_response = t_request + latency_s; video offset = "
                   "t_response - stream release_timestamp + offset_shift"),
    }
    with open(args.json_out, "w") as fh:
        json.dump({"meta": meta, "readings": rows}, fh, indent=2)

    lines = [
        "# Every colour measurement, timestamped and linked to the livestream",
        "",
        f"{len(rows)} readings. Generated by `stream_index.py`; see that file for how the",
        "instant is recovered. Offset shift applied: "
        f"**{args.offset_shift:+.1f} s**.",
        "",
    ]
    for filename, pose, note in RUNS:
        sub = [r for r in rows if r["run_file"] == filename]
        if not sub:
            continue
        lines += [f"## `{filename}` — {pose} ({note})", "",
                  "| # | stage | x (mm) | total | measured at (UTC) | video | link |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        for r in sub:
            x = "" if not r["position"] else f"{r['position']['x']:.2f}"
            url = r.get("url", "")
            link = f"[{r.get('video_offset_hms','')}]({url})" if url else "—"
            lines.append(f"| {r['index_in_run']} | {r['stage']} | {x} | {r['total']} | "
                         f"{r['t_response_utc'][11:23]} | {r.get('video_id','—')} | {link} |")
        lines.append("")
    with open(args.md_out, "w") as fh:
        fh.write("\n".join(lines))

    print(f"{len(rows)} readings -> {os.path.basename(args.json_out)}, "
          f"{os.path.basename(args.md_out)}")
    linked = sum(1 for r in rows if "url" in r)
    print(f"{linked} of them fall inside a known livestream segment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
