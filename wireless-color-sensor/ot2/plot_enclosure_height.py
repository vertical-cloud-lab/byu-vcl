#!/usr/bin/env python3
"""Plot the light reading against nozzle height over the plate: 2026-09-29 and both 09-30 runs.

The enclosure's own sensor is the contact detector: while the enclosure still
moves down with the nozzle the reading keeps falling, and once its foot rests
on the plate the reading stops changing. The lower panel is the fall per mm
between consecutive readings, which goes to zero at contact.

    python3 plot_enclosure_height.py [enclosure-height-2026-09-30.json] [OUT.png]
"""
import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
# Categorical slots 1-3, validated all-pairs; slot 3 is below 3:1 on this
# surface, so every series is also labelled directly and run 2 has its own marker.
RUN1, BEFORE, RUN2 = "#2a78d6", "#eb6834", "#1baf7a"


def descending(points):
    """The way down only: skip readings taken on a step back up; a repeat keeps the later one."""
    out = []
    for z, r in points:
        if out and z > out[-1][0]:
            continue
        if out and z == out[-1][0]:
            out[-1] = (z, r)
            continue
        out.append((z, r))
    return out


def mean_reads(ladder):
    return descending([(p["z"], sum(p["reads"]) / len(p["reads"])) for p in ladder])


def falls(pts):
    mids, drops = [], []
    for (z0, r0), (z1, r1) in zip(pts, pts[1:]):
        if z0 - z1 <= 1.0 + 1e-9:          # the 1 mm and finer steps only
            mids.append((z0 + z1) / 2)
            drops.append((r0 - r1) / (z0 - z1))
    return mids, drops


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "enclosure-height-2026-09-30.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else "enclosure-height-2026-09-30.png"
    d = json.load(open(src))
    series = [
        ("2026-09-29", BEFORE, "o", mean_reads(d["correction_0929"]["0929_reads"])),
        ("09-30 run 1", RUN1, "o", mean_reads(d["ladder"])),
        ("09-30 run 2", RUN2, "s", mean_reads(d["run2"]["ladder"])),
    ]
    touches = (d["contact"]["nozzle_z_touch"], d["run2"]["contact"]["nozzle_z_touch"])
    read_z = d["recommendation"]["read_height_nozzle_z"]

    plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(8.2, 6.6), sharex=True,
                                  gridspec_kw={"height_ratios": [2.2, 1]}, facecolor=SURFACE)
    for a in (ax, ax2):
        a.set_facecolor(SURFACE)
        a.grid(True, color=GRID, linewidth=0.8)
        a.set_axisbelow(True)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.axvspan(min(touches), max(touches), color=GRID, zorder=0)
        a.axvline(read_z, color=INK2, linewidth=1, linestyle="--")
        a.axvline(98.9, color=INK2, linewidth=1, linestyle=":")

    for name, colour, marker, pts in series:
        zs, rs = zip(*pts)
        ax.plot(zs, rs, color=colour, linewidth=2, marker=marker, markersize=5,
                markeredgecolor=SURFACE, markeredgewidth=1.5, label=name)
    old, run1, run2 = (s[3] for s in series)
    ax.annotate("2026-09-29", xy=min(old, key=lambda p: abs(p[0] - 108.0)), xytext=(0, -12),
                textcoords="offset points", color=INK2, ha="center", va="top")
    ax.annotate("09-30 run 1", xy=min(run1, key=lambda p: abs(p[0] - 94.0)), xytext=(12, 6),
                textcoords="offset points", color=INK2, ha="left", va="bottom")
    ax.annotate("09-30 run 2", xy=min(run2, key=lambda p: abs(p[0] - 96.0)), xytext=(-10, -8),
                textcoords="offset points", color=INK2, ha="right", va="top")

    lo, hi = ax.get_ylim()
    ax.text(read_z + 0.3, lo + 0.62 * (hi - lo),
            f"touches the plate at\nz {touches[0]:g} and {touches[1]:g} (shaded);\n"
            f"read height z {read_z:g} (dashed)", va="top", ha="right", color=INK, fontsize=9)
    ax.text(98.9 - 0.3, hi, "09-29 estimate, z 98.9:\nstill falling here,\nno contact",
            va="top", ha="left", color=INK, fontsize=9)
    ax.set_ylabel("light reading, total counts")
    ax.legend(frameon=False, loc="lower left")
    ax.set_title("The enclosure's reading stops falling when its foot meets the plate",
                 loc="left", fontsize=11, color=INK)

    for name, colour, marker, pts in series[1:]:
        mids, drops = falls(pts)
        ax2.plot(mids, drops, color=colour, linewidth=2, marker=marker, markersize=5,
                 markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax2.axhline(0, color=INK2, linewidth=0.8)
    ax2.set_ylabel("fall per mm\n(counts)")
    ax2.set_xlabel("nozzle z over the plate's centre (mm); lower is closer to the plate")
    ax.invert_xaxis()
    fig.tight_layout()
    fig.savefig(dst, dpi=150, facecolor=SURFACE)
    print("wrote", dst)


if __name__ == "__main__":
    main()
