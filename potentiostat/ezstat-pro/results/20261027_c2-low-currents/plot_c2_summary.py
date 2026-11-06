"""C2 summary figure: the LPRs on the 100 kOhm, 1 MOhm and 10 MOhm (2026-10-27).

    python plot_c2_summary.py

Writes 20261027-C2-summary.png next to this file: one panel per resistor, with
its LPR points, the straight-line fit and the slope the meter reading implies,
then each fit's deviation from the meter, against C2's 5 % limit.
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parent

# run, meter reading (ohm), meter uncertainty (%, from listings of the same meter), label
RUNS = [
    ("20261027-C2-100k-export.csv", 99.5e3, 1.0, "100 kΩ", "99.5 kΩ"),
    ("20261027-C2-1M-export.csv", 1.022e6, 1.2, "1 MΩ", "1.022 MΩ"),
    ("20261027-C2-10M-export.csv", 10.16e6, 1.2, "10 MΩ", "10.16 MΩ"),
    ("20261027-C2-10M-rep-export.csv", 10.16e6, 1.2, "10 MΩ, repeat", "10.16 MΩ"),
]
RUNS = [r for r in RUNS if (R / r[0]).exists()]

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
    "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
    "axes.facecolor": SURF,
})

fig, axs = plt.subplots(1, len(RUNS) + 1, figsize=(3.0 * (len(RUNS) + 1), 3.3))
devs = []
for ax, (f, rm, unc, name, meter) in zip(axs, RUNS):
    d = np.genfromtxt(R / f, delimiter=",", skip_header=1, usecols=(2, 3, 4))
    E, I = d[:, 1], d[:, 2]
    g, b = np.polyfit(E, I, 1)
    rp = 1 / g
    dev = (rp / rm - 1) * 100
    devs.append((name, dev, unc))
    x = np.linspace(E.min() - 0.001, E.max() + 0.001, 50)
    scale = 1e9
    e0 = -b / g  # where the fit crosses zero current
    ax.plot(x * 1e3, (x - e0) / rm * scale, color=INK2, lw=0.9, ls="--", zorder=1,
            label=f"meter, {meter}")
    ax.plot(x * 1e3, (g * x + b) * scale, color=BLUE, lw=1.2, zorder=2,
            label=f"fit, {rp / 1e6:.4g} MΩ" if rp >= 1e6 else f"fit, {rp / 1e3:.4g} kΩ")
    ax.plot(E * 1e3, I * scale, "o", ms=6, color=BLUE, mec=SURF, mew=1.2, zorder=3)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.axvline(0, color=INK2, lw=0.6)
    ax.set_xlabel("potential (mV)")
    ax.set_ylabel("current (nA)")
    ax.set_title(f"{name}: {dev:+.1f} %", loc="left", color=INK)
    ax.legend(loc="upper left", fontsize=7.5, frameon=False, labelcolor=INK)

ax = axs[-1]
y = np.arange(len(devs))[::-1]
ax.axvspan(-5, 5, color=GRID, alpha=0.6, lw=0, zorder=0)
ax.axvline(0, color=INK2, lw=0.8)
for yi, (name, dev, unc) in zip(y, devs):
    ax.errorbar(dev, yi, xerr=unc, fmt="o", ms=6, color=BLUE, mec=SURF, mew=1.2, ecolor=INK2,
                elinewidth=1, capsize=3, zorder=3)
    ax.text(dev, yi + 0.22, f"{dev:+.1f} %", ha="center", va="bottom", color=INK, fontsize=8)
ax.set_yticks(y, [d[0] for d in devs])
ax.set_ylim(-0.6, len(devs) - 0.3)
ax.set_xlim(-6, 6)
ax.grid(axis="y", visible=False)
ax.set_xlabel("fit vs meter (%)")
ax.set_title("Fit vs meter. Grey: C2's ±5 %;\nbars: the meter's own ±", loc="left", color=INK, fontsize=8.5)

fig.suptitle("C2 on the EZstat-Pro, 10 nA–1 µA range, LPR ±10 mV at 10 mV/min, 2026-10-27",
             x=0.01, ha="left", color=INK, fontsize=10)
fig.tight_layout()
fig.savefig(R / "20261027-C2-summary.png", dpi=150)
print("saved")
