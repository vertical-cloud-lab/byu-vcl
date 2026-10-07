"""Sc-Li slice of the design space showing the master-alloy half-space (issue #161).

Other elements fixed at the worst vertex of the 2026-09 plan (scenario D in
design_space_reachability.py): Zr 2 wt.% via Al-10Zr (20 g), Ti 0.5 via Al-10Ti (5 g),
Mn 5, Cr 2, Mg 6 elemental (13 g)  ->  62 g of the 100 g batch left for Sc, Li and Al.
The reachable region for Sc and Li is then  Sc/y_Sc + Li/y_Li <= 62 (wt.% units).

    python design_space_slice_plot.py   # writes design-space-sc-li-slice.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGET = 62.0          # g per 100 g batch left after the other sources
U_SC, U_LI = 0.8, 2.0  # wt.% upper bounds

SERIES = [  # label, y_Sc, y_Li, colour (validated categorical slots 1-3, light mode)
    ("Sc chips + Al-5Li (2026-09 plan)", 1.00, 0.05, "#2a78d6"),
    ("Al-2Sc + Al-5Li", 0.02, 0.05, "#eb6834"),
    ("Al-2Sc + Al-10Li", 0.02, 0.10, "#1baf7a"),
]
TEXT, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"

fig, ax = plt.subplots(figsize=(7.2, 5.0), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

# design box
ax.add_patch(Rectangle((0, 0), U_SC, U_LI, fill=False, lw=1.2, ec=TEXT, zorder=3))
ax.text(0.02, U_LI - 0.08, "design box\n0–0.8 wt.% Sc × 0–2 wt.% Li", va="top", ha="left",
        fontsize=8.5, color=TEXT, zorder=4)

sc = np.linspace(0, 1.0, 200)
for label, y_sc, y_li, col in SERIES:
    li = (BUDGET - sc / y_sc) * y_li          # Li wt.% on the boundary
    ax.plot(sc, li, lw=2, color=col, label=label, zorder=2)
    # direct label at the right edge of the plotted range
    x_lab = 0.86
    y_lab = (BUDGET - x_lab / y_sc) * y_li
    ax.text(x_lab + 0.01, y_lab, label, fontsize=8, color=TEXT, va="center", ha="left")

# lost corner for Al-2Sc + Al-5Li: above the orange line, inside the box
y_sc, y_li = SERIES[1][1], SERIES[1][2]
x_cross = (BUDGET - U_LI / y_li) * y_sc       # Sc where the line meets Li = U_LI
li_at_usc = (BUDGET - U_SC / y_sc) * y_li
lost = Polygon([(x_cross, U_LI), (U_SC, U_LI), (U_SC, li_at_usc)], closed=True,
               facecolor="none", edgecolor=SERIES[1][3], hatch="////", lw=0, zorder=1)
ax.add_patch(lost)
ax.text(0.62, 1.78, "unreachable with\nAl-2Sc + Al-5Li", fontsize=8, color=TEXT, ha="center",
        va="top", zorder=5)

ax.set_xlim(0, 1.0)
ax.set_ylim(0, 3.4)
ax.set_xlabel("Sc (wt.%)", color=TEXT)
ax.set_ylabel("Li (wt.%)", color=TEXT)
ax.set_title("Masters, not the Al ≥ 80 % cap, decide what is reachable\n"
             "Sc–Li slice with Zr 2 (Al-10Zr), Ti 0.5 (Al-10Ti), Mn 5, Cr 2, Mg 6 wt.% charged",
             fontsize=10, color=TEXT, loc="left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(MUTED)
ax.tick_params(colors=MUTED, labelsize=8.5)
ax.grid(True, color="#e6e5e2", lw=0.6, zorder=0)
ax.legend(loc="lower left", fontsize=8, frameon=False, bbox_to_anchor=(0.01, 0.02))
fig.text(0.01, 0.01, "Boundary of each line: Sc/y_Sc + Li/y_Li = 62 g (what is left of the 100 g "
         "batch). Below a line is reachable with that pair of sources.", fontsize=7, color=MUTED)
fig.tight_layout(rect=(0, 0.03, 1, 1))
out = os.path.join(HERE, "design-space-sc-li-slice.png")
fig.savefig(out, facecolor=SURFACE)
print("wrote", out)
