"""How late the old MongoDB ``timestamp`` field was, per reading.

Before PR #201, ``store_in_mongodb`` stamped every document with ``utcnow()``
at insert, and insert happens once, after the last read of a run. So a run's
first reading was stamped with a time minutes after it happened, its last with
a time seconds after, and every document of the run landed on the same instant.

The lateness is measurable because the reading's true instant survives by
accident in the epoch-ms suffix of ``experiment_id``. This plots
``stored_timestamp - true_instant`` for every pre-fix document.

Usage::

    python3 plot_timestamp_lag.py               # query MongoDB, cache, plot
    python3 plot_timestamp_lag.py --from-cache  # plot from the committed JSON
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "timestamp-lag-2026-09-10.json")
PRE_FIX = "#2C6FBB"   # validated pair, light surface
AFTER = "#1F8A5B"
INK, MUTED = "#1F2328", "#6B7280"


def collect(uri, database):
    from pymongo import MongoClient
    client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    try:
        docs = list(client[database]["sensor-data"].find(
            {"source": "ot2-xscan-test", "stored_at": {"$exists": False}}))
    finally:
        client.close()
    runs = {}
    for d in docs:
        tail = d["experiment_id"].rsplit("-", 1)[-1]
        if not tail.isdigit():
            continue
        true_s = int(tail) / 1000.0
        stored_s = d["timestamp"].replace(tzinfo=timezone.utc).timestamp()
        runs.setdefault(d["run"]["started"], []).append(
            {"experiment_id": d["experiment_id"], "true_epoch": true_s,
             "stored_epoch": stored_s, "late_s": stored_s - true_s})
    for v in runs.values():
        v.sort(key=lambda r: r["true_epoch"])
    return {"runs": [{"started": k, "readings": v} for k, v in sorted(runs.items())]}


def plot(data, out_path):
    runs = [r for r in data["runs"] if len(r["readings"]) > 2]
    late = [x["late_s"] for r in data["runs"] for x in r["readings"]]
    fig, ax = plt.subplots(figsize=(6.6, 3.5), dpi=110)
    for i, run in enumerate(runs):
        ys = [x["late_s"] for x in run["readings"]]
        ax.plot(range(1, len(ys) + 1), ys, "-o", color=PRE_FIX, lw=1.6, ms=3.2,
                alpha=0.75, label="a run, as stored before the fix" if i == 0 else None)
    ax.axhline(0, color=AFTER, lw=2.4,
               label="after the fix: the reading's own instant")
    ax.set_xlabel("reading, in the order it was taken within its run", color=MUTED, fontsize=9)
    ax.set_ylabel("how late the stored\ntimestamp was (s)", color=MUTED, fontsize=9)
    ax.set_title("Every reading was stamped with the batch write time",
                 color=INK, fontsize=11, loc="left", pad=14)
    ax.text(0, 1.015, f"{len(late)} documents, {len(data['runs'])} runs · median "
            f"{sorted(late)[len(late) // 2]:.0f} s late · worst {max(late):.0f} s",
            transform=ax.transAxes, color=MUTED, fontsize=8.5)
    ax.grid(axis="y", color="#E5E7EB", lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#D1D5DB")
    ax.tick_params(colors=MUTED, labelsize=8.5)
    ax.legend(frameon=False, fontsize=8.5, labelcolor=MUTED, loc="upper right")
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    print(f"wrote {os.path.basename(out_path)}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--from-cache", action="store_true")
    p.add_argument("--out", default=os.path.join(HERE, "timestamp-lag-2026-09-10.png"))
    args = p.parse_args(argv)
    if args.from_cache:
        data = json.load(open(CACHE))
    else:
        data = collect(os.environ["MONGODB_URI"],
                       os.environ.get("MONGODB_DATABASE", "digital-wetlab"))
        with open(CACHE, "w") as fh:
            json.dump(data, fh, indent=2)
    plot(data, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
