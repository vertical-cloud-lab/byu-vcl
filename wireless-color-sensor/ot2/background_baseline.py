#!/usr/bin/env python3
"""Characterise the enclosure's own background, with the module on its base.

Zero motion. Nothing is sent to the OT-2; this only talks to the sensor over
MQTT, so it runs from anywhere -- a laptop, a runner, the Pi.

Why this exists. A closed enclosure does not read zero: it reads ~440 counts
peaked at 510/550 nm, which is an indicator LED inside the box (Pico W or
breakout), not room light and not darkness. ``ch410`` was exactly 6 on all 26
seated reads across seven runs and eight hours on 2026-09-09. That is a fixed
*additive* term, and ``blank_correction.py`` subtracts it from both the sample
and the blank before dividing -- so if it moves, every normalised spectrum
computed against the old value is wrong by the difference.

It moves when the hardware moves. Run this after anything is unplugged,
re-seated, re-sited or re-batteried, and before trusting a blank taken with an
older offset.

    python3 background_baseline.py -n 30
    python3 background_baseline.py -n 30 --out background-2026-09-10.json
"""
import argparse
import glob
import json
import os
import statistics
import sys
import time

from sensor_read import CHANNELS, SensorLink

# The 2026-09-09 reference: every seated read in the committed run files.
SEATED_STAGES = ("seated-baseline", "reseat-confirm")


def seated_reference(pattern="xscan-*.json"):
    """Pull every seated read out of the committed runs, as the prior baseline.

    Excludes the 2026-09-09 sweep's reseat-confirm: that one read 15084 counts
    because the module had come off the nozzle and was lying on the deck, so it
    is not a seated read at all despite its label.
    """
    reads = []
    for path in sorted(glob.glob(pattern)):
        try:
            data = json.load(open(path))
        except (OSError, ValueError):
            continue
        for r in data.get("readings", []):
            if r.get("stage") in SEATED_STAGES and r.get("total", 0) < 1000:
                reads.append(r)
    return reads


def stats(reads):
    out = {}
    for ch in CHANNELS:
        vals = [r["channels"][ch] for r in reads]
        out[ch] = {
            "mean": statistics.mean(vals),
            "sd": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
            "min": min(vals), "max": max(vals),
        }
    totals = [r["total"] for r in reads]
    out["total"] = {
        "mean": statistics.mean(totals),
        "sd": statistics.pstdev(totals) if len(totals) > 1 else 0.0,
        "min": min(totals), "max": max(totals),
    }
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("-n", "--reads", type=int, default=30)
    p.add_argument("--gap", type=float, default=2.0,
                   help="seconds between reads (default 2.0)")
    p.add_argument("--out", default=None, help="write the readings JSON here")
    p.add_argument("--no-mongo", action="store_true")
    p.add_argument("--label", default="background-baseline")
    args = p.parse_args(argv)

    prior = seated_reference()
    link = SensorLink().connect()
    link.check_delivery()
    print(f"broker delivers: PASS -- taking {args.reads} seated reads\n")

    reads = []
    for i in range(1, args.reads + 1):
        r = link.read(label=f"{args.label}-{i}")
        r["stage"] = args.label
        r["position"] = None
        reads.append(r)
        ch = r["channels"]
        body = "  ".join(f"{c[2:]}={ch[c]:>4}" for c in CHANNELS)
        print(f"  {i:>3}/{args.reads}  {body}  total={r['total']:>5}")
        if i < args.reads:
            time.sleep(args.gap)
    link.close()

    now, before = stats(reads), stats(prior) if prior else None
    print(f"\n  now: {len(reads)} reads")
    if before:
        print(f"  2026-09-09 reference: {len(prior)} seated reads from the committed runs\n")
        print(f"  {'ch':>6} {'was':>9} {'sd':>6} {'now':>9} {'sd':>6} {'delta':>8} {'%':>8}")
        for ch in list(CHANNELS) + ["total"]:
            b, a = before[ch]["mean"], now[ch]["mean"]
            pct = (a - b) / b * 100.0 if b else float("nan")
            print(f"  {ch:>6} {b:>9.2f} {before[ch]['sd']:>6.2f} "
                  f"{a:>9.2f} {now[ch]['sd']:>6.2f} {a - b:>+8.2f} {pct:>+7.1f}%")
        # A shift many standard deviations wide is a step in the hardware, not
        # noise -- the point of the comparison is to say which it is.
        sd = max(before["total"]["sd"], 0.5)
        z = (now["total"]["mean"] - before["total"]["mean"]) / sd
        print(f"\n  total moved {now['total']['mean'] - before['total']['mean']:+.1f} counts "
              f"= {z:+.1f} sd of the old spread")
        if abs(z) > 3:
            print("  => the offset has MOVED. Blanks taken against the old vector are stale;\n"
                  "     re-take them, and use this run as blank_correction.py's offset.")
        else:
            print("  => unchanged within noise; the old offset vector is still good.")

    payload = {
        "started": reads[0].get("t_request_utc"),
        "finished": reads[-1].get("t_response_utc"),
        "label": args.label,
        "motion": "none -- sensor only, module closed on its base",
        "readings": reads,
        "stats": now,
        "reference_2026_09_09": before,
        "reference_n": len(prior),
    }
    if args.out:
        json.dump(payload, open(args.out, "w"), indent=2)
        print(f"\n  wrote {args.out}")

    uri = None if args.no_mongo else os.environ.get("MONGODB_URI")
    if uri:
        from run_xscan_test import store_in_mongodb
        store_in_mongodb(reads, {"started": payload["started"], "kind": args.label,
                                 "motion": "none"},
                         uri, os.environ.get("MONGODB_DATABASE", "digital-wetlab"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
