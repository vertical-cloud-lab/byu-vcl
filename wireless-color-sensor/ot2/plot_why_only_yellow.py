#!/usr/bin/env python3
"""Why the colour scan only ever reports yellow.

Regenerates `why-only-yellow-2026-09-09.png` from the committed run JSONs.
Three panels, each answering one part of the question:

  A  the empty slot already varies more, position to position, than the paint does
  B  what changed when the vials went in is not what a yellow absorber does
  C  the 10 mm sweep finds one feature, not three

Usage:  python3 plot_why_only_yellow.py
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CH = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
WL = [410, 440, 470, 510, 550, 583, 620, 670]

SURFACE = "#fcfcfb"
INK, INK2, INK3 = "#0b0b0b", "#52514e", "#8a8984"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"     # validated categorical slots 1-3
GRID = "#e4e3df"

STOPS = [33.88, 63.88, 93.88]


def positions(fn):
    """Mean channel counts at each scan X, keyed by X (the base read is dropped)."""
    d = json.load(open(fn))
    out = {}
    for r in d["readings"]:
        p = r.get("position")
        if p:
            out.setdefault(round(p["x"], 2), []).append([r["channels"][c] for c in CH])
    return {x: np.array(v, float).mean(0) for x, v in sorted(out.items())
            if abs(x - 36.55) > 0.1}                     # drop the seated base read


def share(v):
    return 100 * v / v.sum()


empty120 = positions("xscan-slot7-z120-2026-09-09.json")
empty125 = positions("xscan-slot7-2026-09-09.json")
empty128 = positions("xscan-slot7-z128-2026-09-09.json")
vials128 = positions("xscan-slot7-paint-2026-09-09.json")
sweep = positions("xscan-slot7-sweep-2026-09-09.json")

fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.4), facecolor=SURFACE)
fig.subplots_adjust(left=0.055, right=0.985, top=0.80, bottom=0.14, wspace=0.28)

for ax in axes:
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9, length=0)

# ---------------------------------------------------------------- panel A
ax = axes[0]
series = [
    ("empty slot, z 120", empty120, S1, "-", "o"),
    ("empty slot, z 125", empty125, S3, "-", "s"),
    ("empty slot, z 128", empty128, S2, "-", "^"),
]
for label, data, c, ls, mk in series:
    y = [share(data[x])[1] for x in STOPS]
    ax.plot(STOPS, y, ls, color=c, lw=2, marker=mk, ms=8, zorder=3,
            markeredgecolor=SURFACE, markeredgewidth=2, label=label)

yv = [share(vials128[x])[1] for x in STOPS]
ax.plot(STOPS, yv, "--", color=INK, lw=2, marker="D", ms=7, zorder=4,
        markeredgecolor=SURFACE, markeredgewidth=2, label="WITH the vials, z 128")

# the paint effect, drawn against the artefact it has to beat
ax.annotate("", xy=(31.5, share(empty128[33.88])[1]), xytext=(31.5, yv[0]),
            arrowprops=dict(arrowstyle="<->", color=INK, lw=1.5))
ax.annotate("the entire\n'yellow' effect:\n1.3 pts", (35.5, 2.28), fontsize=9.5,
            color=INK, ha="left", va="center", fontweight="bold")
ax.annotate("", xy=(99.5, share(empty128[63.88])[1]), xytext=(99.5, share(empty128[93.88])[1]),
            arrowprops=dict(arrowstyle="<->", color=S2, lw=1.5))
ax.annotate("same empty slot,\nsame height,\nno sample at all:\n2.2 pts", (101.5, 4.0),
            fontsize=9.5, color=S2, ha="left", va="center", fontweight="bold")
ax.annotate("z 120: the three stops agree to 0.04 pts", (63.88, 6.28), fontsize=9.5,
            color=S1, ha="center", va="bottom")

ax.set_xlim(21, 130)
ax.set_ylim(1.6, 7.9)
leg = ax.legend(loc="lower right", frameon=False, fontsize=9.5,
                bbox_to_anchor=(1.0, -0.02), handlelength=2.4, labelspacing=0.35)
for t in leg.get_texts():
    t.set_color(INK2)
ax.set_xticks(STOPS)
ax.set_xlabel("scan position, X (mm)", color=INK2, fontsize=10)
ax.set_ylabel("440 nm share of the total (%)", color=INK2, fontsize=10)
ax.set_title("A.  The empty deck already 'has a colour' —\nand more of it than the paint",
             color=INK, fontsize=12, fontweight="bold", loc="left", pad=12)

# ---------------------------------------------------------------- panel B
ax = axes[1]
a, b = empty128[33.88], vials128[33.88]
pct = 100 * (b / a - 1)
cols = [S1 if p < 0 else INK3 for p in pct]
cols[0] = S2
bars = ax.bar(range(8), pct, color=cols, width=0.66, zorder=3)
for i, (r, p) in enumerate(zip(bars, pct)):
    off = -13 if p < 0 else (-14 if 14 < p < 21 else 5)
    ax.annotate(f"{p:+.0f}%", (i, p), textcoords="offset points",
                xytext=(0, off), ha="center", fontsize=9, color=INK2)
ax.axhline(0, color=INK3, lw=1)
ax.axhline(100 * (b.sum() / a.sum() - 1), color=INK, lw=1.4, ls=":")
ax.annotate("total light  +17%", (3.5, 19.4), ha="center", va="bottom", fontsize=9.5,
            color=INK, fontweight="bold")
ax.annotate("410 nm went UP", (0.05, 30.5), ha="left", va="center", fontsize=9.5,
            color=S2, fontweight="bold")
ax.annotate("Yellow paint absorbs 410 nm at least as hard\nas 440 nm — its absorption edge is monotone\nbelow ~480 nm. So this is not an absorber\nappearing under the sensor. It is the room\nlight changing between the two runs.",
            (1.75, -24.5), fontsize=9.4, color=INK, ha="left", va="center")
ax.set_xticks(range(8))
ax.set_xticklabels(WL)
ax.set_ylim(-38, 36)
ax.set_xlabel("channel (nm)", color=INK2, fontsize=10)
ax.set_ylabel("change in counts, empty → vials (%)", color=INK2, fontsize=10)
ax.set_title("B.  What changed at x = 33.88 is not\nwhat a yellow sample does",
             color=INK, fontsize=12, fontweight="bold", loc="left", pad=12)

# ---------------------------------------------------------------- panel C
ax = axes[2]
xs = [x for x in sweep if x > 3]
ys = [share(sweep[x])[1] for x in xs]
ax.plot(xs, ys, "-", color=S1, lw=2, marker="o", ms=7, zorder=3,
        markeredgecolor=SURFACE, markeredgewidth=2)
ax.axhspan(4.4, 5.6, color=GRID, zorder=1)
ax.annotate("bare-deck band", (90, 5.05), fontsize=9.5, color=INK2, ha="right", va="bottom")
ax.annotate("", xy=(90, 4.75), xytext=(90, 5.0), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.2))
ax.annotate("one feature,\n~20 mm wide,\ncentred x ≈ 29", (29, 3.30), fontsize=9.5,
            color=INK, ha="center", va="bottom", fontweight="bold")
for cx, c in ((29, "#eda100"), (54, "#2a78d6"), (79, "#e34948")):
    ax.axvspan(cx - 11, cx + 11, color=c, alpha=0.10, zorder=0)
    ax.annotate("", xy=(cx, 6.10), xytext=(cx, 5.70),
                arrowprops=dict(arrowstyle="-|>", color=c, lw=1.6))
ax.annotate("if three 22 mm vials were lined up along X,\nthe sweep passed over all three.\nTwo of them registered nothing at all.",
            (50, 6.30), fontsize=9.4, color=INK, ha="center", va="bottom")
ax.set_xlim(8, 92)
ax.set_ylim(1.7, 7.9)
ax.set_xlabel("scan position, X (mm)   ·   10 mm sweep, z 128, vials in place",
              color=INK2, fontsize=10)
ax.set_ylabel("440 nm share of the total (%)", color=INK2, fontsize=10)
ax.set_title("C.  The sweep crossed the whole slot and\nfound one colour, not three",
             color=INK, fontsize=12, fontweight="bold", loc="left", pad=12)

fig.suptitle("Why the scan only ever reports yellow — the sensor has no light of its own, "
             "so it measures the room, not the paint",
             color=INK, fontsize=14.5, fontweight="bold", x=0.055, ha="left", y=0.96)
fig.text(0.055, 0.905,
         "slot 7 · OT-2 OT2CEP20210722R13 · AS7341 on the nozzle · module LEDs confirmed inert "
         "(every R/Y/B level returns 437–439 counts)",
         color=INK2, fontsize=10, ha="left")
fig.savefig("why-only-yellow-2026-09-09.png", dpi=150, facecolor=SURFACE)
print("wrote why-only-yellow-2026-09-09.png")
