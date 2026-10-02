#!/usr/bin/env python3
"""Does someone standing at the machine actually change what the sensor reads?

Raised on #197: the overhead camera is not the sensor, so a person appearing in
the livestream frame should not, on its own, move the enclosure's background.
That is correct about the camera. This script asks the separate question the
frames were only ever evidence for -- whether a person *at the machine* changes
the readings -- and answers it from the sensor's own numbers.

Three tests, in increasing order of how hard they are to argue with:

  1  How much of a reading is light from outside the enclosure at all?
     Compare the sealed level (module closed on its base) with the lifted level.

  2  Read-to-read spread at a fixed pose. The three reads at a position are
     1.4 s apart with the gantry parked, so nothing mechanical moves between
     them and the only thing that can change is the light. Split by whether a
     person was at the machine, stratified by aperture height so the height
     effect cannot masquerade as a person effect.

  3  The largest single 1.4 s step, per channel, against the same position
     with nobody there.

The practical output is the gate in `--gate`: because a quiet background repeats
to 0.03-0.13%, the reads at one position police themselves. A spread above
GATE_AT means the light moved while the position was being read, and that
reading cannot serve as a blank -- no video needed to tell you so.

Regenerates `person-effect-2026-09-10.png`.

Usage:  python3 analyse_person_effect.py            # the three tests + the figure
        python3 analyse_person_effect.py --gate FILE...   # screen a run for a moved background
"""
import glob
import json
import random
import statistics as st
import sys
from math import comb

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CH = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
WL = [410, 440, 470, 510, 550, 583, 620, 670]

SURFACE = "#fcfcfb"
INK, INK2, INK3 = "#0b0b0b", "#52514e", "#8a8984"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
GRID = "#e4e3df"

SEALED_MAX = 1000       # a reseat-confirm above this is the run where it fell off
FLAG_AT = 1.0           # spread threshold, in %, for the 2x2
GATE_AT = 0.5           # 4x the worst quiet position (0.13%), 2x below the mildest
                        # position with a person at the machine (0.99%)

# Was a person at the machine while this position was read? Taken from the 27
# frames in frames/ -- the frame is the evidence, not the cause. Checked against
# the images rather than trusted from the gallery captions.
PERSON = {
    ("xscan-run-2026-09-09.json", "pos1-dx-30"): 1,          # arm across the deck, head in shot
    ("xscan-run-2026-09-09.json", "pos2-dx+0"): 1,           # ditto, holding the yellow vial
    ("xscan-run-2026-09-09.json", "pos3-dx+30"): 0,
    ("xscan-slot7-2026-09-09.json", "pos1-dx-30"): 1,
    ("xscan-slot7-2026-09-09.json", "pos2-dx+0"): 1,
    ("xscan-slot7-2026-09-09.json", "pos3-dx+30"): 1,
    ("xscan-slot7-z120-2026-09-09.json", "pos1-dx-30"): 0,
    ("xscan-slot7-z120-2026-09-09.json", "pos2-dx+0"): 0,
    ("xscan-slot7-z120-2026-09-09.json", "pos3-dx+30"): 0,
    ("xscan-slot7-z128-2026-09-09.json", "pos1-dx-30"): 1,
    ("xscan-slot7-z128-2026-09-09.json", "pos2-dx+0"): 1,
    ("xscan-slot7-z128-2026-09-09.json", "pos3-dx+30"): 0,
    ("xscan-slot7-paint-2026-09-09.json", "pos1-dx-30"): 0,
    ("xscan-slot7-paint-2026-09-09.json", "pos2-dx+0"): 1,
    ("xscan-slot7-paint-2026-09-09.json", "pos3-dx+30"): 0,
    ("xscan-slot7-z129-press90-2026-09-09.json", "pos1-dx-30"): 1,
    ("xscan-slot7-z129-press90-2026-09-09.json", "pos2-dx+0"): 1,
    ("xscan-slot7-z129-press90-2026-09-09.json", "pos3-dx+30"): 0,
}
for _i, _dx in enumerate([-60, -50, -40, -30, -20, -10, 0, 10, 20], 1):
    _tag = f"pos{_i}-dx-{abs(_dx)}" if _dx < 0 else f"pos{_i}-dx+{_dx}"
    PERSON[("xscan-slot7-sweep-2026-09-09.json", _tag)] = 0      # all nine clear


def load():
    """One record per scan position, plus every sealed-enclosure read."""
    rows, sealed = [], []
    for fn in sorted(glob.glob("xscan-*.json")):
        d = json.load(open(fn))
        ap = d["run"]["plan"]["aperture_height_mm"]
        by_stage = {}
        for r in d["readings"]:
            stage = r.get("stage") or ""
            if stage.startswith("pos"):
                by_stage.setdefault(stage, []).append(r)
            elif stage in ("seated-baseline", "reseat-confirm"):
                sealed.append(r)
        for stage, reads in by_stage.items():
            tot = [r["total"] for r in reads]
            rows.append(dict(file=fn, stage=stage, ap=ap, reads=reads, totals=tot,
                             mean=st.mean(tot),
                             spread=100 * (max(tot) - min(tot)) / st.mean(tot),
                             person=PERSON[(fn, stage)]))
    return rows, sealed


def fisher(a, b, c, d):
    """Two-sided Fisher exact p for the 2x2 [[a, b], [c, d]]."""
    n = a + b + c + d
    def cell(w, x, y, z):
        return comb(w + x, w) * comb(y + z, y) / comb(n, w + y)
    obs = cell(a, b, c, d)
    total = 0.0
    for i in range(min(a + b, a + c) + 1):
        j, k = a + b - i, a + c - i
        l = c + d - k
        if j < 0 or k < 0 or l < 0:
            continue
        q = cell(i, j, k, l)
        if q <= obs + 1e-15:
            total += q
    return total


def permutation(rows, trials=200_000, seed=0):
    """Shuffle the person label *within* each aperture height, so height cannot leak in."""
    def gap(labels):
        p = [r["spread"] for r, x in zip(rows, labels) if x]
        c = [r["spread"] for r, x in zip(rows, labels) if not x]
        return st.median(p) - st.median(c)
    base = [r["person"] for r in rows]
    obs = gap(base)
    strata = {}
    for i, r in enumerate(rows):
        strata.setdefault(r["ap"], []).append(i)
    rng = random.Random(seed)
    hits = 0
    for _ in range(trials):
        shuffled = [0] * len(rows)
        for idx in strata.values():
            lab = [base[i] for i in idx]
            rng.shuffle(lab)
            for i, x in zip(idx, lab):
                shuffled[i] = x
        if gap(shuffled) >= obs - 1e-12:
            hits += 1
    return obs, hits / trials


def main():
    rows, sealed = load()
    seal_tot = [r["total"] for r in sealed if r["total"] < SEALED_MAX]
    dropped = [r["total"] for r in sealed if r["total"] >= SEALED_MAX]
    seal = st.mean(seal_tot)

    print(f"{len(rows)} scan positions, person at the machine for "
          f"{sum(r['person'] for r in rows)} of them\n")

    print("[1] how much of a reading is light from outside the enclosure")
    print(f"    sealed (module closed on its base): {seal:.1f} counts, sd {st.pstdev(seal_tot):.2f}, "
          f"over {len(seal_tot)} reads spanning ~8 h with people at the machine")
    if dropped:
        print(f"    excluded {dropped} - the run where the module came off its base")
    lo, hi = min(r["mean"] for r in rows), max(r["mean"] for r in rows)
    print(f"    lifted over the slot: {lo:.0f}-{hi:.0f} counts")
    print(f"    => {100 * (1 - seal / lo):.0f}-{100 * (1 - seal / hi):.0f}% of every lifted reading "
          f"is light that came in from outside\n")

    print("[2] read-to-read spread at a fixed pose (3 reads, 1.4 s apart, gantry parked)")
    n3 = [r for r in rows if len(r["totals"]) == 3]
    for ap in sorted({r["ap"] for r in n3}):
        grp = [r for r in n3 if r["ap"] == ap]
        p = sorted(r["spread"] for r in grp if r["person"])
        c = sorted(r["spread"] for r in grp if not r["person"])
        fmt = lambda v: (f"median {st.median(v):6.2f}%  ({min(v):.2f}-{max(v):.2f})"
                         if v else "none at this height")
        print(f"    aperture {ap:5.1f} mm   person n={len(p)}: {fmt(p):34s} | "
              f"clear n={len(c)}: {fmt(c)}")

    a = sum(1 for r in rows if r["person"] and r["spread"] > FLAG_AT)
    b = sum(1 for r in rows if not r["person"] and r["spread"] > FLAG_AT)
    c_ = sum(1 for r in rows if r["person"] and r["spread"] <= FLAG_AT)
    d = sum(1 for r in rows if not r["person"] and r["spread"] <= FLAG_AT)
    print(f"\n    all {len(rows)} positions, spread > {FLAG_AT:g}%:  person {a}/{a + c_}   "
          f"clear {b}/{b + d}   Fisher exact p = {fisher(a, b, c_, d):.5f}")
    obs, p = permutation(n3)
    print(f"    n=3 positions only, height-stratified permutation test: "
          f"median gap {obs:+.2f} pts, one-sided p = {p:.4f}\n")

    print("[3] the largest single step between two consecutive reads 1.4 s apart")
    worst = max(((y["total"] - x["total"]) / x["total"] * 100, r, x, y)
                for r in rows for x, y in zip(r["reads"], r["reads"][1:]))
    step, row, before, after = worst
    print(f"    {row['file']} {row['stage']} (person at the machine): "
          f"{before['total']} -> {after['total']} = {step:+.1f}% in 1.4 s")
    quiet = next(r for r in rows if r["file"] == "xscan-slot7-z120-2026-09-09.json"
                 and r["stage"] == "pos2-dx+0")
    qstep = max(abs(y["total"] - x["total"]) / x["total"] * 100
                for x, y in zip(quiet["reads"], quiet["reads"][1:]))
    print(f"    same aperture height, nobody there: {quiet['totals']} -> "
          f"largest step {qstep:.2f}%")
    print("    per-channel change across that step:")
    for ch, wl in zip(CH, WL):
        u, v = before["channels"][ch], after["channels"][ch]
        qv = [r["channels"][ch] for r in quiet["reads"]]
        print(f"      {wl:3d} nm  {u:5d} -> {v:5d}  {100 * (v - u) / u:+6.1f}%"
              f"     quiet: {qv}  range {max(qv) - min(qv)}")

    figure(rows, seal, seal_tot, before, after, quiet, step, obs, p,
           fisher(a, b, c_, d))


def figure(rows, seal, seal_tot, before, after, quiet, step, gap, pperm, pfisher):
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.4), facecolor=SURFACE)
    fig.subplots_adjust(left=0.055, right=0.985, top=0.80, bottom=0.155, wspace=0.28)
    for ax in axes:
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=9, length=0)

    # ------------------------------------------------------------ panel A
    ax = axes[0]
    rng = np.random.default_rng(3)
    for flag, colour, mark, name in ((0, S1, "o", "nobody at the machine"),
                                     (1, S2, "D", "person at the machine")):
        grp = [r for r in rows if r["person"] == flag]
        x = [r["ap"] + rng.uniform(-0.55, 0.55) for r in grp]
        y = [max(r["spread"], 0.015) for r in grp]
        ax.scatter(x, y, s=74, color=colour, marker=mark, zorder=3,
                   edgecolor=SURFACE, linewidth=1.6, label=name)
    ax.axhline(FLAG_AT, color=INK3, lw=1, ls=":")
    ax.annotate("1%", (40.6, 1.06), fontsize=9, color=INK3, ha="right", va="bottom")
    ax.set_yscale("log")
    ax.set_xlim(27.6, 41.0)
    ax.set_ylim(0.012, 60)
    ax.annotate("9 of 10\nabove 1%", (35.0, 24), fontsize=9.5, color=S2,
                ha="center", va="center", fontweight="bold")
    ax.annotate("14 of 17\nbelow 1%", (33.6, 0.075), fontsize=9.5, color=S1,
                ha="center", va="center", fontweight="bold")
    ax.annotate(f"Fisher exact p = {pfisher:.5f}\nheight-stratified permutation p = {pperm:.4f}",
                (40.85, 0.0155), fontsize=9.4, color=INK, ha="right", va="bottom")
    leg = ax.legend(loc="upper left", frameon=False, fontsize=9.5, handletextpad=0.3)
    for t in leg.get_texts():
        t.set_color(INK2)
    ax.set_xlabel("aperture height above the deck (mm)", color=INK2, fontsize=10)
    ax.set_ylabel("read-to-read spread at one pose (%, log)", color=INK2, fontsize=10)
    ax.set_title("A.  Every position, split by whether\nsomeone was standing there",
                 color=INK, fontsize=12, fontweight="bold", loc="left", pad=12)

    # ------------------------------------------------------------ panel B
    ax = axes[1]
    pct = [100 * (after["channels"][c] - before["channels"][c]) / before["channels"][c]
           for c in CH]
    qpct = []
    for c in CH:
        v = [r["channels"][c] for r in quiet["reads"]]
        qpct.append(100 * (max(v) - min(v)) / st.mean(v))
    idx = np.arange(8)
    ax.bar(idx - 0.19, pct, width=0.37, color=S2, zorder=3,
           label="person at the machine   (+31.7% total)")
    ax.bar(idx + 0.19, qpct, width=0.37, color=S1, zorder=3,
           label="nobody there   (+0.04% total)")
    for i, v in enumerate(pct):
        ax.annotate(f"{v:+.0f}%", (i - 0.19, v), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8.6, color=INK2)
    ax.axhline(0, color=INK3, lw=1)
    ax.annotate("the warm channels move most:\nan arm is a large, well-lit,\n"
                "orange diffuse reflector",
                (4.35, 34.5), fontsize=9.4, color=INK, ha="left", va="top")
    ax.set_xticks(idx)
    ax.set_xticklabels(WL)
    ax.set_ylim(-4, 56)
    leg = ax.legend(loc="upper left", frameon=False, fontsize=9.4, handlelength=1.4)
    for t in leg.get_texts():
        t.set_color(INK2)
    ax.set_xlabel("channel (nm)   ·   both at aperture 29.5 mm, gantry parked",
                  color=INK2, fontsize=10)
    ax.set_ylabel("change between two reads 1.4 s apart (%)", color=INK2, fontsize=10)
    ax.set_title("B.  1.4 seconds, nothing mechanical\nmoving — only the light",
                 color=INK, fontsize=12, fontweight="bold", loc="left", pad=12)

    # ------------------------------------------------------------ panel C
    ax = axes[2]
    lifted = sorted(r["mean"] for r in rows)
    ax.bar(range(len(lifted)), lifted, color=GRID, width=0.86, zorder=2,
           label="light from outside")
    ax.bar(range(len(lifted)), [seal] * len(lifted), color=S3, width=0.86, zorder=3,
           label=f"the enclosure's own sealed level ({seal:.0f} counts)")
    ax.annotate(f"sealed: {seal:.0f} ± {st.pstdev(seal_tot):.1f} counts over {len(seal_tot)} reads\n"
                f"and ~8 h, people coming and going.\nClosed, the background really is rock steady.",
                (0.4, 6550), fontsize=9.4, color=INK, ha="left", va="top")
    ax.annotate("", xy=(20.5, 439), xytext=(20.5, 6861),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.5))
    ax.annotate("79–94% of every\nreading taken over\nthe slot is room light",
                (19.7, 3600), fontsize=9.5, color=INK, ha="right", va="center",
                fontweight="bold")
    ax.set_xlim(-0.9, len(lifted) - 0.1)
    ax.set_ylim(0, 8100)
    ax.set_xticks([])
    leg = ax.legend(loc="upper left", frameon=False, fontsize=9.4, handlelength=1.4,
                    bbox_to_anchor=(0.0, 1.005))
    for t in leg.get_texts():
        t.set_color(INK2)
    ax.set_xlabel("the 27 scan positions, ordered by brightness", color=INK2, fontsize=10)
    ax.set_ylabel("total counts", color=INK2, fontsize=10)
    ax.set_title("C.  During a measurement the enclosure\nis not sealed — it is a light funnel",
                 color=INK, fontsize=12, fontweight="bold", loc="left", pad=12)

    fig.suptitle("The camera is not the sensor — but a person at the machine is. "
                 "A fixed pose moved 31.7% in 1.4 seconds",
                 color=INK, fontsize=14.5, fontweight="bold", x=0.055, ha="left", y=0.96)
    fig.text(0.055, 0.905,
             "27 scan positions across 7 runs, 2026-09-09 · OT-2 OT2CEP20210722R13 · "
             "AS7341 on the nozzle, module LEDs inert · person labels read off the 27 livestream frames",
             color=INK2, fontsize=10, ha="left")
    fig.savefig("person-effect-2026-09-10.png", dpi=150, facecolor=SURFACE)
    print("\nwrote person-effect-2026-09-10.png")


def gate(files):
    """Flag positions whose background moved while they were being read."""
    bad = 0
    for fn in files:
        d = json.load(open(fn))
        by_stage = {}
        for r in d["readings"]:
            stage = r.get("stage") or ""
            if stage.startswith("pos"):
                by_stage.setdefault(stage, []).append(r["total"])
        print(fn)
        for stage, tot in by_stage.items():
            spread = 100 * (max(tot) - min(tot)) / st.mean(tot)
            ok = spread <= GATE_AT
            bad += not ok
            print(f"  {stage:12s} {str(tot):26s} spread {spread:6.2f}%  "
                  f"{'ok' if ok else 'BACKGROUND MOVED - not usable as a blank'}")
    print(f"\n{bad} position(s) over the {GATE_AT:g}% gate")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gate":
        raise SystemExit(gate(sys.argv[2:] or sorted(glob.glob("xscan-*.json"))))
    main()
