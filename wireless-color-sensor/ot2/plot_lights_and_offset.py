#!/usr/bin/env python3
"""Figure for the two questions asked on issue #197 on 2026-09-10.

Every number is a SHARE POINT unless the axis says otherwise: a channel's
counts divided by that same reading's total counts, times 100. It is the only
unit in which "colour" means anything for this sensor, because it is the only
one that survives the brightness of the room.

Reads only committed JSON -- no hardware, no motion.

    python3 plot_lights_and_offset.py
"""
import json
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from analyse_lights_and_offset import (
    CH, NM, load, mean_vec, scan_positions, sealed_reads, shares,
)

OUT = "lights-and-offset-2026-09-10.png"
SURFACE = "#fcfcfb"
INK, MUTED, GRID = "#1F2328", "#6B7280", "#E5E7EB"
LIT, UNLIT, THIRD = "#2a78d6", "#eb6834", "#1baf7a"


def floor_and_spread(d):
    """Resolution floor (share points) and read-to-read spread (% of total)."""
    off = mean_vec(sealed_reads(d))
    out = {}
    for lab, rs in scan_positions(d).items():
        per = [shares(r["channels"], off) for r in rs]
        sds = [st.stdev([p[c] for p in per]) for c in CH]
        tots = [r["total"] for r in rs]
        out[lab] = {"floor": 2 * max(sds),
                    "spread": 100 * (max(tots) - min(tots)) / st.mean(tots),
                    "shares": shares(mean_vec(rs), off),
                    "total": st.mean(tots)}
    return out


def main():
    on, off = (load("background-lightson-2026-09-10.json"),
               load("background-lightsoff-2026-09-10.json"))
    fon, foff = floor_and_spread(on), floor_and_spread(off)

    # the lamp: the lowest each channel has ever been seen, sealed
    conds = [mean_vec(sealed_reads(load(f))) for f in [
        "xscan-run-2026-09-09.json", "xscan-slot7-2026-09-09.json",
        "xscan-slot7-paint-2026-09-09.json", "xscan-slot7-sweep-2026-09-09.json",
        "xscan-slot7-z120-2026-09-09.json", "xscan-slot7-z128-2026-09-09.json",
        "xscan-slot7-z129-press90-2026-09-09.json",
        "background-2026-09-10.json", "background-lightsoff-2026-09-10.json",
        "background-lightson-2026-09-10.json"]]
    lamp = {c: min(v[c] for v in conds) for c in CH}
    swing = {c: max(v[c] for v in conds) - lamp[c] for c in CH}

    def lamp_bias(d, fs):
        lab = sorted(fs)[0]
        v = mean_vec(scan_positions(d)[lab])
        raw, no_lamp = shares(v), shares(v, lamp)
        return max(abs(raw[c] - no_lamp[c]) for c in CH)

    # the biggest colour feature this rig has produced, for scale
    sweep = load("xscan-slot7-sweep-2026-09-09.json")
    soff = mean_vec(sealed_reads(sweep))
    ssh = [shares(mean_vec(rs), soff) for rs in scan_positions(sweep).values()]
    signal = max(max(abs(s[c] - st.median([x[c] for x in ssh])) for s in ssh) for c in CH)

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    fig.patch.set_facecolor(SURFACE)

    # -- 1. everything on one ruler: share points -------------------------
    ax = axes[0]
    ax.set_facecolor(SURFACE)
    items = [
        ("lamp bias, rails OFF,\nnothing subtracted", lamp_bias(off, foff), UNLIT),
        ("lamp bias, rails ON,\nnothing subtracted", lamp_bias(on, fon), LIT),
        ("noise floor, rails OFF", max(v["floor"] for v in foff.values()), UNLIT),
        ("noise floor, rails ON", max(v["floor"] for v in fon.values()), LIT),
    ]
    ys = np.arange(len(items))[::-1]
    for y, (lab, val, colour) in zip(ys, items):
        ax.plot([val], [y], "o", ms=11, color=colour, mec=SURFACE, mew=2, zorder=3)
        ax.hlines(y, 0.008, val, color=colour, lw=2, alpha=0.35, zorder=2)
        ax.annotate(f"{val:.3g}", (val, y), xytext=(9, 0), textcoords="offset points",
                    va="center", fontsize=9.5, color=INK)
    ax.axvline(signal, color=THIRD, lw=2, zorder=1)
    ax.annotate(f"biggest colour feature\never measured: {signal:.2f}",
                (signal, 1.6), xytext=(-10, 0), textcoords="offset points",
                ha="right", va="center", fontsize=9, color="#0f6b4a")
    ax.set_xscale("log")
    ax.set_xlim(0.008, 20)
    ax.set_ylim(-0.6, len(items) - 0.4)
    ax.set_yticks(ys)
    ax.set_yticklabels([lab for lab, _, _ in items], fontsize=9)
    ax.set_xlabel("share points  (log scale)")
    ax.set_title("Is the error bigger than the signal?", fontsize=11, color=INK)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)

    # -- 2. the two kinds of error, lights on vs off ----------------------
    ax = axes[1]
    ax.set_facecolor(SURFACE)

    def disagree(fs):
        rows = list(fs.values())
        return max(max(r["shares"][c] for r in rows) - min(r["shares"][c] for r in rows)
                   for c in CH)

    groups = ["random\n(read to read,\nno blank can fix it)",
              "systematic\n(stop to stop,\na blank divides it out)"]
    vals_on = [max(v["floor"] for v in fon.values()), disagree(fon)]
    vals_off = [max(v["floor"] for v in foff.values()), disagree(foff)]
    x = np.arange(len(groups))
    w = 0.34
    ax.bar(x - w / 2 - 0.012, vals_on, width=w, color=LIT, label="rail lights ON")
    ax.bar(x + w / 2 + 0.012, vals_off, width=w, color=UNLIT, label="rail lights OFF")
    for xi, (a, b) in enumerate(zip(vals_on, vals_off)):
        ax.annotate(f"{a:.3f}", (xi - w / 2 - 0.012, a), xytext=(0, 4),
                    textcoords="offset points", ha="center", fontsize=9.5, color=INK)
        ax.annotate(f"{b:.3f}", (xi + w / 2 + 0.012, b), xytext=(0, 4),
                    textcoords="offset points", ha="center", fontsize=9.5, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=9)
    ax.set_ylabel("share points")
    ax.set_ylim(0, max(vals_off) * 1.28)
    ax.set_title("The lights trade random error for systematic",
                 fontsize=11, color=INK)
    ax.legend(frameon=False, fontsize=9.5)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)

    # -- 3. which part of the sealed offset is a lamp ----------------------
    ax = axes[2]
    ax.set_facecolor(SURFACE)
    nm = np.array(NM)
    lo = np.array([lamp[c] for c in CH])
    sw = np.array([swing[c] for c in CH])
    ax.bar(nm, lo, width=22, color=THIRD, label="never goes away  (the lamp)")
    ax.bar(nm, sw, width=22, bottom=lo, color=MUTED,
           label="moves with the room  (leak)")
    for w_, l_, s_ in zip(nm, lo, sw):
        ax.annotate(f"{100 * s_ / l_:.0f}%", (w_, l_ + s_), xytext=(0, 4),
                    textcoords="offset points", ha="center", fontsize=8.5,
                    color=MUTED)
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("counts, module sealed on its base")
    ax.set_title("510 + 550 nm hold to 5%; the rest swing 29-126%",
                 fontsize=11, color=INK)
    ax.set_ylim(0, (lo + sw).max() * 1.34)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)

    for a in axes:
        for side in ("top", "right"):
            a.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            a.spines[side].set_color(GRID)
        a.tick_params(colors=MUTED, labelsize=9)
        for t in a.get_yticklabels() + a.get_xticklabels():
            t.set_color(INK)

    fig.suptitle("Rail lights and the green lamp, 2026-09-10  --  "
                 "share point = a channel's counts / that reading's total counts x 100",
                 fontsize=10.5, color=MUTED, y=1.005)
    fig.tight_layout()
    fig.savefig(OUT, dpi=140, facecolor=SURFACE, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
