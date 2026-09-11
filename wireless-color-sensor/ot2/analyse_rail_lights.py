#!/usr/bin/env python3
"""Compare a rail-lights-on scan against a lights-off control at the same pose.

The OT-2's deck rail lights are the only controllable light source this rig
has -- the sensor module's own LEDs are inert (``led_probe.py``, 2026-09-09).
Every scan up to 2026-09-10 was therefore a survey of whatever the room
happened to be doing, and the room turned out to be the largest variable in
the experiment: a person walking up to the open machine moved the total 31.7 %
in 1.4 s, and an *empty* slot's spectral shape disagreed with itself between
three stops by 7.69 points of channel share.

This measures what the lights buy, on three axes that each broke a previous
session's conclusion:

  precision  -- read-to-read spread at one position, gantry parked. The only
                thing that can differ between those reads is light.
  uniformity -- how much the total swings across the three X stops of an empty
                slot. Anything here is instrument, not sample.
  colour     -- the largest disagreement, between stops, in any channel's
                *share* of its own total. This is the one that decides a
                colour test: it is how much the instrument disagrees with
                itself about the colour of a bare deck.

    python3 analyse_rail_lights.py --on FILE --off FILE [--plot OUT.png]
"""
from __future__ import annotations

import argparse
import json

CHANNELS = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
NM = [410, 440, 470, 510, 550, 583, 620, 670]
POSITIONS = ["pos1-dx-30", "pos2-dx+0", "pos3-dx+30"]
X_MM = [33.88, 63.88, 93.88]


def load(path):
    d = json.load(open(path))
    by = {}
    for r in d["readings"]:
        label = r.get("label") or ""
        stem = label.rsplit("-", 1)[0] if label[-1:].isdigit() else label
        by.setdefault(stem, []).append(r)
    return d, by


def mean_channels(reads):
    return [sum(r["channels"][c] for r in reads) / len(reads) for c in CHANNELS]


def spread_pct(reads):
    """Peak-to-peak of the totals at one position, as % of the mean."""
    totals = [r["total"] for r in reads]
    return 100.0 * (max(totals) - min(totals)) / (sum(totals) / len(totals))


def shares(vals):
    t = sum(vals)
    return [100.0 * v / t for v in vals] if t else [0.0] * len(vals)


def colour_disagreement(by):
    """Largest spread, across the three stops, of any channel's share."""
    sh = [shares(mean_channels(by[p])) for p in POSITIONS]
    return max(max(s[i] for s in sh) - min(s[i] for s in sh)
               for i in range(len(CHANNELS)))


def summarise(path):
    d, by = load(path)
    totals = [sum(mean_channels(by[p])) for p in POSITIONS]
    return {
        "path": path,
        "lights": d["run"]["lights"],
        "seated": sum(r["total"] for r in by["seated-baseline"]) / len(by["seated-baseline"]),
        "reseat": sum(r["total"] for r in by["reseat-confirm"]) / len(by["reseat-confirm"]),
        "grip": sum(r["total"] for r in by["grip-check"]) / len(by["grip-check"]),
        "totals": totals,
        "spreads": [spread_pct(by[p]) for p in POSITIONS],
        "uniformity": 100.0 * (max(totals) - min(totals)) / (sum(totals) / len(totals)),
        "colour": colour_disagreement(by),
        "means": {p: mean_channels(by[p]) for p in POSITIONS},
        "shares": {p: shares(mean_channels(by[p])) for p in POSITIONS},
    }


def report(on, off):
    print("\n=== rail lights on vs off, same pose, minutes apart ===\n")
    print(f"{'':<34}{'lights ON':>14}{'lights off':>14}{'factor':>12}")
    rows = [
        ("seated baseline (closed on base)", on["seated"], off["seated"], None),
        ("mean total over the 3 stops",
         sum(on["totals"]) / 3, sum(off["totals"]) / 3, None),
        ("worst read-to-read spread %", max(on["spreads"]), max(off["spreads"]), "lower"),
        ("total swing across 3 stops %", on["uniformity"], off["uniformity"], "lower"),
        ("colour disagreement, points", on["colour"], off["colour"], "lower"),
    ]
    for name, a, b, better in rows:
        if better == "lower":
            f = f"{b / a:.1f}x better" if a else "-"
        else:
            f = f"{a / b:.2f}x" if b else "-"
        print(f"{name:<34}{a:>14.3f}{b:>14.3f}{f:>12}")

    for tag, s in (("ON", on), ("off", off)):
        print(f"\n  lights {tag}: per position")
        print("    x (mm)  " + "".join(f"{n:>8}" for n in NM) + f"{'total':>10}{'spread%':>9}")
        for x, p, sp in zip(X_MM, POSITIONS, s["spreads"]):
            m = s["means"][p]
            print(f"    {x:>6.2f}  " + "".join(f"{v:>8.0f}" for v in m)
                  + f"{sum(m):>10.0f}{sp:>9.2f}")


def plot(on, off, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 3, figsize=(13, 4.0))
    for a, s, title in ((ax[0], on, "rail lights ON"), (ax[1], off, "rail lights off")):
        for x, p in zip(X_MM, POSITIONS):
            a.plot(NM, s["means"][p], "o-", lw=1.6, ms=4, label=f"x = {x:g}")
        a.set_title(f"{title}\nempty slot 7, z 129", fontsize=10)
        a.set_xlabel("wavelength (nm)")
        a.set_ylabel("counts")
        a.legend(fontsize=8)
        a.grid(alpha=0.3)
    top = max(max(sum(s["means"][p]) for p in POSITIONS) for s in (on, off))
    for a in ax[:2]:
        a.set_ylim(0, top * 0.28)

    labels = ["worst read-to-read\nspread (%)", "total swing across\n3 stops (%)",
              "colour disagreement\n(points of share)"]
    vals_on = [max(on["spreads"]), on["uniformity"], on["colour"]]
    vals_off = [max(off["spreads"]), off["uniformity"], off["colour"]]
    xs = range(len(labels))
    ax[2].bar([i - 0.19 for i in xs], vals_off, 0.38, label="lights off", color="#9aa0a6")
    ax[2].bar([i + 0.19 for i in xs], vals_on, 0.38, label="lights ON", color="#e8b30b")
    ax[2].set_yscale("log")
    ax[2].set_xticks(list(xs))
    ax[2].set_xticklabels(labels, fontsize=8)
    ax[2].set_title("lower is better (log scale)", fontsize=10)
    ax[2].legend(fontsize=8)
    ax[2].grid(alpha=0.3, axis="y")
    for i, (a, b) in enumerate(zip(vals_off, vals_on)):
        ax[2].text(i - 0.19, a, f"{a:.2f}", ha="center", va="bottom", fontsize=7)
        ax[2].text(i + 0.19, b, f"{b:.2f}", ha="center", va="bottom", fontsize=7)

    fig.suptitle("OT-2 rail lights: what controlled illumination buys "
                 "(empty slot 7, read z 129, 2026-09-10)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=130)
    print(f"\nwrote {out}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--on", required=True)
    p.add_argument("--off", required=True)
    p.add_argument("--plot")
    a = p.parse_args(argv)
    on, off = summarise(a.on), summarise(a.off)
    report(on, off)
    if a.plot:
        plot(on, off, a.plot)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
