"""Turn two runs -- one blank, one sample -- into a per-position reflectance ratio.

The background (blank) measurement is the same well, at the same pose, under the
same light, with no sample in it. Divide the sample by it channel-for-channel and
everything that is not the sample cancels: the room light's own colour, the
deck's colour, the enclosure's geometry, the sensor's per-channel responsivity.

Two rules, both learned the hard way on 2026-09-09 (see the README):

1. **Subtract before dividing.** ~439 counts of every reading are a fixed green
   glow inside the closed enclosure -- ``ch410`` was exactly 6 on all 26 seated
   reads across seven runs and eight hours. It is additive, so it must come off
   both numbers *before* the ratio, or it drags the ratio toward 1.0 by up to
   6% in ch510/ch550.

2. **One blank per position, not one per run.** An empty slot 7 at read z 128
   already disagrees with itself by position: the 620 nm share is 23.1% / 20.9%
   / 28.6% at the three stops with nothing on the deck. Borrowing a neighbour's
   blank injects a 37-92% error, which is larger than any colour signal these
   vials have ever produced.

Usage::

    python3 blank_correction.py --blank xscan-blank.json --sample xscan-paint.json

Positions are matched by the reading label that ``run_xscan_test.py`` writes
(``pos1-dx-30`` and so on), so the blank run and the sample run must use the
same ``--scan-dx``. Run them back to back, changing nothing but the sample.
"""

from __future__ import annotations

import argparse
import glob
import json
import statistics as st

CHANNELS = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")

# A seated read is the module closed on its base. It is not darkness -- it is
# whatever is lit inside the closed box, which is the offset we want.
SEATED_LABELS = ("seated-baseline", "reseat", "background-baseline")
# "background-baseline" is what background_baseline.py writes: a long burst
# of seated reads taken on its own, so a run can borrow a freshly measured
# offset via --offset-from instead of the four it took for itself.
SEATED_MAX_TOTAL = 1000.0   # a dislodged module reads ~15000; that is not a baseline


def _vec(reading):
    return [reading["channels"][c] for c in CHANNELS]


def positions(path):
    """Mean channel vector per scan position, keyed by label without the read index."""
    groups = {}
    for reading in json.load(open(path))["readings"]:
        label = reading.get("label") or ""
        if any(s in label for s in SEATED_LABELS) or "grip" in label:
            continue
        groups.setdefault(label.rsplit("-", 1)[0], []).append(_vec(reading))
    return {k: [st.mean(col) for col in zip(*v)] for k, v in groups.items()}


def seated_offset(paths):
    """The fixed in-enclosure glow, averaged over every genuinely seated read."""
    seated = []
    for path in paths:
        for reading in json.load(open(path))["readings"]:
            label = reading.get("label") or ""
            if any(s in label for s in SEATED_LABELS) and reading["total"] < SEATED_MAX_TOTAL:
                seated.append(_vec(reading))
    if not seated:
        raise SystemExit("no seated reads found -- pass --offset-from, or --no-offset")
    return [st.mean(col) for col in zip(*seated)], len(seated)


def ratio(sample, blank, offset):
    return [(s - k) / (b - k) for s, b, k in zip(sample, blank, offset)]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blank", required=True, help="run JSON of the empty well")
    ap.add_argument("--sample", required=True, help="run JSON of the same well with sample in it")
    ap.add_argument("--offset-from", nargs="*", default=None,
                    help="run JSONs to average the seated offset from (default: blank + sample)")
    ap.add_argument("--no-offset", action="store_true",
                    help="skip the additive correction (shows how much it was worth)")
    ap.add_argument("--cross-check", action="store_true",
                    help="also divide each sample by every OTHER position's blank")
    args = ap.parse_args()

    blank, sample = positions(args.blank), positions(args.sample)
    shared = sorted(set(blank) & set(sample))
    if not shared:
        raise SystemExit("no positions in common -- were both runs given the same --scan-dx?")

    if args.no_offset:
        offset, n = [0.0] * 8, 0
        print("additive offset: NOT removed")
    else:
        offset, n = seated_offset(args.offset_from or [args.blank, args.sample])
        print(f"additive offset from {n} seated read(s), total {sum(offset):.0f}: "
              + " ".join(f"{c[2:]}={v:.1f}" for c, v in zip(CHANNELS, offset)))

    header = "position      " + "".join(f"{c[2:]:>8}" for c in CHANNELS)
    print("\nsample / blank, per position  (1.000 = indistinguishable from the empty well)")
    print(header)
    for pos in shared:
        r = ratio(sample[pos], blank[pos], offset)
        print(f"{pos:14s}" + "".join(f"{v:8.3f}" for v in r))

    if args.cross_check:
        print("\ncross-check: the same sample divided by a DIFFERENT position's blank.")
        print("Large numbers here are the reason a blank has to be per-position.")
        for pos in shared:
            own = ratio(sample[pos], blank[pos], offset)
            for other in shared:
                if other == pos:
                    continue
                wrong = ratio(sample[pos], blank[other], offset)
                worst = max(abs(w / o - 1) * 100 for w, o in zip(wrong, own))
                print(f"  {pos} against {other}'s blank: worst-channel error {worst:.0f}%")


if __name__ == "__main__":
    main()
