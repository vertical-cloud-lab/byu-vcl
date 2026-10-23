"""Plot the four AS7341 readings from the 2026-08-10 full-cycle session.

Reads the committed sensor_reading_*.json files in this directory and renders
spectral counts vs channel wavelength to spectra.png.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent
WAVELENGTHS = [410, 440, 470, 510, 550, 583, 620, 670]

SERIES = [
    ("sensor_reading_midair_RYB50.json", "mid-air carry, R=Y=B=50", "#2a78d6"),
    ("sensor_reading_midair_ambient.json", "mid-air carry, ambient (0/0/0)", "#eb6834"),
    ("sensor_reading_seated_RYB50.json", "seated baseline, R=Y=B=50", "#1baf7a"),
    ("sensor_reading_reseated_RYB50.json", "reseated after cycle, R=Y=B=50", "#eda100"),
]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

for fname, label, color in SERIES:
    data = json.loads((HERE / fname).read_text())["sensor_data"]
    counts = [data[f"ch{wl}"] for wl in WAVELENGTHS]
    ax.plot(WAVELENGTHS, counts, color=color, lw=2, marker="o", ms=6,
            markerfacecolor=color, markeredgecolor=SURFACE, markeredgewidth=1,
            label=label, zorder=3)

# selective direct labels at the right end of each mid-air trace, and one
# shared label for the near-identical seated/reseated pair
ax.annotate("mid-air ambient", (670, 610), xytext=(676, 640),
            color=INK_2, fontsize=9)
ax.annotate("mid-air R=Y=B=50", (670, 526), xytext=(676, 480),
            color=INK_2, fontsize=9)
ax.annotate("seated / reseated", (670, 57), xytext=(676, 80),
            color=INK_2, fontsize=9)

ax.set_xlabel("AS7341 channel center wavelength (nm)", color=MUTED)
ax.set_ylabel("raw counts (16-bit, uncalibrated)", color=MUTED)
ax.set_title("Wireless color sensor readings — 2026-08-10 full-cycle test",
             color=INK, fontsize=12, loc="left")
ax.set_xticks(WAVELENGTHS)
ax.set_xlim(400, 745)
ax.tick_params(colors=MUTED, labelsize=9)
ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
for spine in ("left", "bottom"):
    ax.spines[spine].set_color(BASELINE)

leg = ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=INK_2)

fig.tight_layout()
fig.savefig(HERE / "spectra.png", facecolor=SURFACE, bbox_inches="tight")
print("wrote", HERE / "spectra.png")
