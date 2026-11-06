"""C1 summary figure: OCP, the two LPRs and the +40 mV hold on the 10.00 kOhm (2026-10-26).

    python plot_c1_summary.py [offset_A]

Writes 20261026-C1-summary.png next to this file. offset_A is the 1 uA-100 uA
range's current offset, by default -0.1437e-6 A, where C1's LPR line crosses 0 V.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parents[1] / "analysis"))
from check_corrosion_runs import read_nuvdt  # noqa: E402

R_METER = 10000.0
OFFSET_A = float(sys.argv[1]) if len(sys.argv) > 1 else -0.1437e-6

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
    "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
    "axes.facecolor": SURF,
})

_, ocp = read_nuvdt(R / "20261026-C1-lpr.nuvdt")
lpr = np.genfromtxt(R / "20261026-C1-lpr.csv", delimiter=",", skip_header=1, usecols=(2, 3, 4))
lpr2 = np.genfromtxt(R / "20261026-C1-lpr2-export.csv", delimiter=",", skip_header=1, usecols=(2, 3, 4))
_, hold = read_nuvdt(R / "20261026-C1-hold2.nuvdt")

fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))

# A: OCP
ax = axs[0]
ax.plot(ocp["t"] / 60, ocp["V"] * 1e6, color=BLUE, lw=0.8)
m = np.mean(ocp["V"]) * 1e6
ax.axhline(0, color=INK2, lw=0.8)
ax.set_xlabel("time (min)")
ax.set_ylabel("potential (µV)")
ax.set_title(f"1. OCP, 20 min: mean {m:.0f} µV", loc="left", color=INK)

# B: LPR, C1 and the repeat
ax = axs[1]
x = np.linspace(-0.0105, 0.0105, 50)
rps = []
for d, color, mk, ms, name in ((lpr, BLUE, "o", 9, "C1, after 20 min OCP"), (lpr2, ORANGE, "s", 4.5, "repeat, after 1 min OCP")):
    E, I = d[:, 1], d[:, 2]
    g, b = np.polyfit(E, I, 1)
    rps.append(1 / g)
    ax.plot(x * 1e3, (g * x + b) * 1e6, color=color, lw=1.2, zorder=2)
    ax.plot(E * 1e3, I * 1e6, mk, ms=ms, color=color, mec=SURF, mew=1.2, zorder=3,
            label=f"{name}: {1 / g:,.0f} Ω")
ax.axhline(0, color=INK2, lw=0.8)
ax.set_xlabel("potential (mV)")
ax.set_ylabel("current (µA)")
ax.set_title("2. LPR ±10 mV at 10 mV/min, 9 points each", loc="left", color=INK)
ax.legend(loc="upper left", fontsize=8, frameon=False, labelcolor=INK)
ax.text(0.97, 0.05, "meter: 10.00 kΩ\nline misses 0 A at 0 V:\nthe range's −0.144 µA offset",
        transform=ax.transAxes, ha="right", va="bottom", color=INK2, fontsize=8)

# C: hold
ax = axs[2]
on = np.isfinite(hold["I"])
t, Ih, Vh = hold["t"][on], hold["I"][on], hold["V"][on]
sel = Vh > 0.02
ax.plot(t[sel] / 60, Ih[sel] * 1e6, color=BLUE, lw=0.8)
exp_ = np.mean(Vh[sel]) / R_METER
ax.axhline(exp_ * 1e6, color=INK2, lw=0.8, ls="--")
ax.text(t[sel][-1] / 60, exp_ * 1e6 + 0.01, "V/R, no offset", ha="right", va="bottom", color=INK2)
ax.axhline((exp_ + OFFSET_A) * 1e6, color=ORANGE, lw=0.8, ls="--")
ax.text(t[sel][-1] / 60, (exp_ + OFFSET_A) * 1e6 - 0.01, "V/R + offset (LPR, 0 V)", ha="right",
        va="top", color=INK2)
ax.set_ylim((exp_ + OFFSET_A) * 1e6 - 0.12, exp_ * 1e6 + 0.08)
ax.set_xlabel("time (min)")
ax.set_ylabel("current (µA)")
ax.set_title(f"3. +40 mV hold, 10 min: {np.mean(Ih[sel]) * 1e6:.3f} µA", loc="left", color=INK)

fig.suptitle("C1 on the 10.00 kΩ, EZstat-Pro, 1 µA–100 µA range, 2026-10-26", x=0.01, ha="left",
             color=INK, fontsize=10)
fig.tight_layout()
fig.savefig(R / "20261026-C1-summary.png", dpi=150)
print("saved")
