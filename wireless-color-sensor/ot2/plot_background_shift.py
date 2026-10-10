#!/usr/bin/env python3
"""The enclosure's closed background, before and after the 2026-09-10 lab move.

Reads only committed JSON -- no hardware, no motion.

    python3 plot_background_shift.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from background_baseline import seated_reference, stats
from sensor_read import CHANNELS

WAVELENGTHS = np.array([410, 440, 470, 510, 550, 583, 620, 670])
NOW_FILE = "background-2026-09-10.json"
OUT = "background-shift-2026-09-10.png"


def main():
    now_payload = json.load(open(NOW_FILE))
    now_reads = now_payload["readings"]
    before_reads = seated_reference()
    now, before = stats(now_reads), stats(before_reads)

    b = np.array([before[c]["mean"] for c in CHANNELS])
    a = np.array([now[c]["mean"] for c in CHANNELS])
    b_sd = np.array([before[c]["sd"] for c in CHANNELS])
    a_sd = np.array([now[c]["sd"] for c in CHANNELS])

    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.3))

    # -- 1. the two background vectors ------------------------------------
    ax = axes[0]
    w = 12
    ax.bar(WAVELENGTHS - w / 2, b, width=w, yerr=b_sd, capsize=2,
           color="#9aa7b1", edgecolor="#5b6770",
           label=f"2026-09-09  (n={len(before_reads)})")
    ax.bar(WAVELENGTHS + w / 2, a, width=w, yerr=a_sd, capsize=2,
           color="#2f6f4e", edgecolor="#1d4732",
           label=f"2026-09-10, post-move  (n={len(now_reads)})")
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("counts")
    ax.set_title("Closed-enclosure background\n"
                 f"total {before['total']['mean']:.0f} → {now['total']['mean']:.0f}",
                 fontsize=10)
    ax.legend(fontsize=8, frameon=False)

    # -- 2. per-channel change --------------------------------------------
    # A flatter battery would dim the LED and move every channel by the same
    # percentage. The point of this panel is that they did not move together.
    ax = axes[1]
    pct = (a - b) / b * 100.0
    colors = plt.cm.rainbow((WAVELENGTHS - WAVELENGTHS.min()) /
                            (WAVELENGTHS.max() - WAVELENGTHS.min()))
    ax.bar(WAVELENGTHS, pct, width=22, color=colors, edgecolor="#333")
    overall = (now["total"]["mean"] - before["total"]["mean"]) / before["total"]["mean"] * 100
    ax.axhline(overall, color="#c0392b", ls="--", lw=1.4,
               label=f"uniform dimming would be flat at {overall:+.1f}%")
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("change (%)")
    ax.set_title("Not a uniform dimming\n"
                 "the 510/550 green core held; the wings fell", fontsize=10)
    ax.legend(fontsize=8, frameon=False, loc="lower left")

    # -- 3. stability of the new baseline ---------------------------------
    ax = axes[2]
    totals = [r["total"] for r in now_reads]
    ax.plot(range(1, len(totals) + 1), totals, "o-", ms=3.5, lw=1.2, color="#2f6f4e")
    ax.axhline(now["total"]["mean"], color="#c0392b", ls="--", lw=1.0)
    ax.fill_between([1, len(totals)],
                    before["total"]["mean"] - before["total"]["sd"],
                    before["total"]["mean"] + before["total"]["sd"],
                    color="#9aa7b1", alpha=0.45, label="2026-09-09 ±1 sd")
    ax.set_xlabel("read #")
    ax.set_ylabel("total counts")
    spread = (max(totals) - min(totals)) / np.mean(totals) * 100
    ax.set_title(f"New baseline is steadier\n"
                 f"sd {now['total']['sd']:.2f} vs {before['total']['sd']:.2f}, "
                 f"spread {spread:.2f}%", fontsize=10)
    ax.legend(fontsize=8, frameon=False)

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT, dpi=130)
    print(f"wrote {OUT}")

    # numbers worth quoting in the write-up
    z = (now["total"]["mean"] - before["total"]["mean"]) / max(before["total"]["sd"], 0.5)
    print(f"total {before['total']['mean']:.2f} -> {now['total']['mean']:.2f} "
          f"({overall:+.1f}%, {z:+.1f} sd)")
    for c, p in zip(CHANNELS, pct):
        print(f"  {c}: {before[c]['mean']:7.2f} -> {now[c]['mean']:7.2f}  {p:+6.1f}%")


if __name__ == "__main__":
    main()
