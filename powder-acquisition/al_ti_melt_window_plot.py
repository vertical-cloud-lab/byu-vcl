"""Figure: Al-Ti liquidus vs. the atomizer's real operating window (issue #161).

Reads the CALPHAD results cached by al_ti_melt_window.py and draws two panels:
  (A) the campaign range, 0-2.5 wt% Ti, against the volatile-element ceilings
  (B) the whole Al-rich range against the induction module's 1300 degC ceiling

Usage: python al_ti_melt_window_plot.py  ->  al-ti-melt-window.png
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator

from al_ti_melt_window import load

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "al-ti-melt-window.png")

BLUE = "#2a78d6"       # series 1 -- the liquidus
CRITICAL = "#d03b3b"   # status: hard machine limit
SERIOUS = "#ec835a"    # status: Zn boils
WARNING = "#fab219"    # status: Mg boils
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e6e6"

data = load()
w = np.array([p[0] for p in data["al_ti"]])
T = np.array([p[1] for p in data["al_ti"]])
liq = PchipInterpolator(w, T)

# The July 2026 estimate this figure supersedes (see al_ti_liquidus_plot.py)
old_w = np.array([0.0, 0.15, 0.19, 1.0, 2.0, 3.5, 7.0, 12.0, 20.0, 28.0, 37.2])
old_T = np.array([660.45, 665, 690, 825, 900, 1000, 1120, 1220, 1310, 1370, 1412])
old = PchipInterpolator(old_w, old_T)

fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 6.0), dpi=150)
fig.patch.set_facecolor("white")


def dress(ax, xmax):
    ax.set_facecolor("white")
    ax.grid(True, color=GRID, lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=9)
    ax.set_xlim(0, xmax)
    ax.set_xlabel("Ti in the melt (wt%)", fontsize=10.5, color=INK)


# ---- Panel A: the campaign range --------------------------------------------
xa = np.linspace(0.02, 2.5, 400)
dress(axA, 2.5)
axA.set_ylim(600, 1200)
axA.set_ylabel("Melt temperature (°C)", fontsize=10.5, color=INK)

axA.fill_between(xa, liq(xa), liq(xa) + 150, color=BLUE, alpha=0.13, lw=0, zorder=1,
                 label="atomization window (+100–150 °C superheat)")
axA.plot(xa, old(xa), color=MUTED, lw=1.6, ls=(0, (5, 3)), zorder=2,
         label="July 2026 estimate (superseded, reads 20–55 °C low)")
axA.plot(xa, liq(xa), color=BLUE, lw=2.2, zorder=4, label="liquidus (CALPHAD, COST507)")

for y, c, lab in ((1091, WARNING, "Mg boils — 1091 °C"),
                  (907, SERIOUS, "Zn boils — 907 °C")):
    axA.axhline(y, color=c, lw=1.8, ls=":", zorder=3)
    axA.text(2.46, y + 9, lab, ha="right", va="bottom", fontsize=9, color=INK)

axA.plot([0.27], [740], "o", color=INK, ms=7, zorder=5)
axA.annotate("measured in situ by LIBS:\n0.27 wt% Ti → 740 °C",
             xy=(0.27, 740), xytext=(0.62, 663), fontsize=8.5, color=INK,
             arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
for wv, note in ((0.5, "0.5 wt% → 791 °C"), (1.0, "1 wt% → 868 °C"), (2.0, "2 wt% → 954 °C")):
    axA.plot([wv], [liq(wv)], "o", color=BLUE, ms=6.5, zorder=5)
    axA.annotate(note, xy=(wv, float(liq(wv))), xytext=(wv - 0.30, float(liq(wv)) + 45),
                 fontsize=8.5, color=INK, ha="left", va="bottom")

axA.set_title("A · Campaign range: what the melt must reach", fontsize=11, color=INK, loc="left")
axA.legend(loc="upper left", fontsize=8.5, frameon=False, labelcolor=INK)

# ---- Panel B: the whole Al-rich side ----------------------------------------
xb = np.linspace(0.02, 37.2, 600)
dress(axB, 38)
axB.set_ylim(600, 1750)

axB.fill_between(xb, liq(xb), liq(xb) + 150, color=BLUE, alpha=0.13, lw=0, zorder=1)
axB.plot(xb, liq(xb), color=BLUE, lw=2.2, zorder=4)

axB.axhline(1300, color=CRITICAL, lw=1.8, ls="--", zorder=3)
axB.text(0.5, 1315, "induction module ceiling — 1300 °C", ha="left", fontsize=9, color=CRITICAL)
axB.axhline(1668, color=MUTED, lw=1.2, ls=":", zorder=3)
axB.text(37.6, 1680, "pure Ti melts at 1668 °C — never reached in this process",
         ha="right", fontsize=8.5, color=MUTED)

axB.axvspan(0, 2, color=BLUE, alpha=0.10, lw=0, zorder=0)
axB.text(2.9, 700, "our alloys\n(≤2 wt% Ti)", fontsize=9, color=INK, ha="left")
axB.annotate("Al$_3$Ti, 37.2 wt% Ti\n1371 °C — the hottest point\non the whole Al-rich side",
             xy=(36.6, 1382), xytext=(20.0, 1120), fontsize=8.5, color=INK,
             arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
axB.annotate("Al-10Ti master alloy\n1187 °C to melt it outright",
             xy=(10, 1187), xytext=(11.2, 930), fontsize=8.5, color=INK,
             arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
axB.text(5.5, 1560, "fully liquid (L)", fontsize=10, color=MUTED, style="italic")
axB.text(28, 740, "L + Al$_3$Ti — a slurry;\natomizing here clogs the sonotrode",
         fontsize=9, color=MUTED, ha="center")
axB.set_title("B · Whole Al-rich range vs. the machine limit", fontsize=11, color=INK, loc="left")

fig.suptitle("Al–Ti melt-temperature window for induction + ultrasonic atomization",
             fontsize=13.5, color=INK, x=0.02, ha="left", y=0.985)
fig.text(0.02, 0.015,
         "Liquidus computed with pycalphad + COST507; validated against in-situ LIBS liquidus "
         "(Leosson 2022) and the ~1387 °C Al₃Ti melting point. Ti dissolves into liquid Al — it is never melted as pure Ti.",
         fontsize=8, color=MUTED, ha="left")
fig.tight_layout(rect=(0, 0.03, 1, 0.96))
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
