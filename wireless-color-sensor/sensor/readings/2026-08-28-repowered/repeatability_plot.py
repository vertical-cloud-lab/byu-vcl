"""Today's readings against the 2026-08-10 baseline, same pose, 18 days apart.

The AS7341 is uncalibrated and reports counts, so the only way to know whether
a number means anything is to re-measure an unchanged scene and see whether it
comes back. This plots the six 2026-08-28 readings (taken after the Pico W was
repowered) over the 2026-08-10 seated/reseated spectra, plus the mid-air
spectrum from the same session as a scale reference for what a *real* change
looks like.

Run: python repeatability_plot.py  ->  repeatability.png
"""

import json
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent
BASELINE_DIR = (HERE / ".." / ".." / ".." / "camera"
                / "pickup-test-2026-08-10-full-cycle-sensor-read").resolve()
WAVELENGTHS = [410, 440, 470, 510, 550, 583, 620, 670]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

TODAY = "#2a78d6"
RESEATED = "#eda100"
SEATED = "#1baf7a"
MIDAIR = "#eb6834"


def counts_of(path):
    return json.loads(path.read_text())["sensor_data"]


def series(data):
    return [data["ch%d" % wl] for wl in WAVELENGTHS]


today_docs = json.loads((HERE / "readings_2026-08-28.json").read_text())
today = [[d["counts"]["ch%d" % wl] for d in today_docs] for wl in WAVELENGTHS]
today_mean = [statistics.mean(v) for v in today]

reseated = counts_of(BASELINE_DIR / "sensor_reading_reseated_RYB50.json")
seated = counts_of(BASELINE_DIR / "sensor_reading_seated_RYB50.json")
midair = counts_of(BASELINE_DIR / "sensor_reading_midair_ambient.json")

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.6), dpi=150,
                              gridspec_kw={"width_ratios": [1.35, 1]})
for axis in (ax, ax2):
    axis.set_facecolor(SURFACE)
    axis.tick_params(colors=MUTED, labelsize=9)
    axis.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for spine in ("top", "right"):
        axis.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        axis.spines[spine].set_color(BASELINE)
fig.patch.set_facecolor(SURFACE)

# Left: the full dynamic range, so "the module is back" is judged against the
# only large signal change ever measured on this device (pose, not chemistry).
ax.plot(WAVELENGTHS, series(midair), color=MIDAIR, lw=2, marker="o", ms=5,
        markeredgecolor=SURFACE, label="2026-08-10 mid-air (pose change)",
        zorder=3)
ax.plot(WAVELENGTHS, series(seated), color=SEATED, lw=2, marker="o", ms=5,
        markeredgecolor=SURFACE, label="2026-08-10 seated", zorder=3)
ax.plot(WAVELENGTHS, series(reseated), color=RESEATED, lw=2, marker="o", ms=5,
        markeredgecolor=SURFACE, label="2026-08-10 reseated", zorder=4)
ax.plot(WAVELENGTHS, today_mean, color=TODAY, lw=2, ls="--", marker="s", ms=5,
        markeredgecolor=SURFACE, label="2026-08-28 (n=6, repowered)", zorder=5)
ax.set_xlabel("AS7341 channel center wavelength (nm)", color=MUTED)
ax.set_ylabel("raw counts (16-bit, uncalibrated)", color=MUTED)
ax.set_title("Full range: the 18-day gap is invisible next to a pose change",
             color=INK, fontsize=11, loc="left")
ax.set_xticks(WAVELENGTHS)
ax.legend(loc="upper left", frameon=False, fontsize=8.5, labelcolor=INK_2)

# Right: the same seated data with the mid-air trace dropped, which is the only
# way to see a 2-3% difference at all.
ax2.plot(WAVELENGTHS, series(reseated), color=RESEATED, lw=2, marker="o", ms=6,
         markeredgecolor=SURFACE, label="2026-08-10 reseated", zorder=3)
ax2.plot(WAVELENGTHS, today_mean, color=TODAY, lw=2, ls="--", marker="s", ms=6,
         markeredgecolor=SURFACE, label="2026-08-28 mean of 6", zorder=4)
lo = [min(v) for v in today]
hi = [max(v) for v in today]
ax2.fill_between(WAVELENGTHS, lo, hi, color=TODAY, alpha=0.25, lw=0,
                 label="2026-08-28 min-max (<=1 count)", zorder=2)
ax2.set_xlabel("AS7341 channel center wavelength (nm)", color=MUTED)
ax2.set_ylabel("raw counts", color=MUTED)
ax2.set_title("Seated pose only: agrees to 2-3% after 18 days",
              color=INK, fontsize=11, loc="left")
ax2.set_xticks(WAVELENGTHS)
# headroom so the legend never sits on the 550 nm peak
ax2.set_ylim(0, max(hi) * 1.45)
ax2.legend(loc="upper left", frameon=False, fontsize=8.5, labelcolor=INK_2)

fig.suptitle("Wireless color sensor back online — 2026-08-28 vs 2026-08-10",
             color=INK, fontsize=12.5, x=0.008, ha="left", y=1.02)
fig.tight_layout()
fig.savefig(HERE / "repeatability.png", facecolor=SURFACE, bbox_inches="tight")
print("wrote", HERE / "repeatability.png")
