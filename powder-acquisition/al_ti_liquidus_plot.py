"""Annotated Al-rich Al-Ti liquidus plot for issue #161.

Redrawn (approximate) from the assessed Al-Ti binary phase diagram:
Schuster & Palm, J. Phase Equilib. Diffus. 27 (2006) 255-277, and
Murray, Metall. Trans. A 19 (1988). Anchor points match the values
discussed in vertical-cloud-lab/byu-vcl#161. Mid-range liquidus values
carry roughly +/-20-30 degC of experimental scatter (undercooling).

Usage: python al_ti_liquidus_plot.py  ->  al-ti-liquidus-annotated.png
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator

# Anchors on the Al-rich liquidus (wt% Ti in liquid, temperature degC)
anchors_wt = np.array([0.0, 0.15, 0.19, 1.0, 2.0, 3.5, 7.0, 12.0, 20.0, 28.0, 37.2])
anchors_T = np.array([660.45, 665, 690, 825, 900, 1000, 1120, 1220, 1310, 1370, 1412])

liquidus = PchipInterpolator(anchors_wt, anchors_T)
x = np.linspace(0, 37.2, 500)

BLUE = "#2a78d6"   # liquidus (series)
RED = "#e34948"    # hard limit (status: serious)
INK = "#333333"
MUTED = "#777777"

fig, ax = plt.subplots(figsize=(9, 6.5), dpi=150)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Planned alloy range: <= 2 wt% Ti
ax.axvspan(0, 2, color=BLUE, alpha=0.08, zorder=0)
ax.text(1.0, 1560, "planned alloys\n(≤2 wt% Ti)", ha="center", va="top",
        fontsize=9, color=INK)

# Liquidus curve
ax.plot(x, liquidus(x), color=BLUE, lw=2, zorder=3)
ax.plot(anchors_wt[1:], anchors_T[1:], "o", color=BLUE, ms=5, zorder=4)

# Region labels
ax.text(9, 1450, "fully liquid (L)", fontsize=11, color=INK, style="italic")
ax.text(20, 1000, "L + Al$_3$Ti solid\n(slurry — stay above\nthe liquidus)",
        fontsize=10, color=MUTED, ha="center")

# Atomizer ceiling
ax.axhline(1500, color=RED, lw=1.8, ls="--", zorder=2)
ax.text(36.8, 1512, "atomizer ceiling ≈ 1500 °C", ha="right",
        fontsize=10, color=RED)

# Pure-Ti melting point, for contrast
ax.axhline(1668, color=MUTED, lw=1.2, ls=":", zorder=2)
ax.text(36.8, 1680, "pure Ti melts at 1668 °C — irrelevant: Ti dissolves into liquid Al",
        ha="right", fontsize=9, color=MUTED)

# Key point annotations
ax.annotate("peritectic: L + Al$_3$Ti → (Al)\n665 °C, ~0.15 wt% Ti",
            xy=(0.15, 665), xytext=(6, 640), fontsize=9, color=INK,
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
ax.annotate("Al$_3$Ti decomposes: 1412 °C, ~37 wt% Ti\n(highest liquidus on the Al-rich side)",
            xy=(37.0, 1405), xytext=(12.5, 1180), fontsize=9, color=INK,
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
ax.annotate("~1 wt% Ti liquid at ~825 °C", xy=(1.0, 825), xytext=(7, 790),
            fontsize=9, color=INK,
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))

ax.set_xlim(0, 38)
ax.set_ylim(600, 1750)
ax.set_xlabel("Ti content of the melt (wt%)", fontsize=11, color=INK)
ax.set_ylabel("Temperature (°C)", fontsize=11, color=INK)
ax.set_title("Al-rich Al–Ti liquidus vs. the 1500 °C atomizer limit\n"
             "(redrawn, after Schuster & Palm 2006; mid-range values ±20–30 °C)",
             fontsize=12, color=INK)

ax.grid(True, color="#e6e6e6", lw=0.7, zorder=0)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
for spine in ("left", "bottom"):
    ax.spines[spine].set_color(MUTED)
ax.tick_params(colors=INK)

fig.tight_layout()
fig.savefig("al-ti-liquidus-annotated.png", dpi=150, bbox_inches="tight",
            facecolor="white")
print("wrote al-ti-liquidus-annotated.png")
