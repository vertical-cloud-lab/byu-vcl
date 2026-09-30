#!/usr/bin/env python3
"""Nozzle height over well A1 against time (2026-09-30 run 4), with the read-height pick marked.

Answers two questions from PR #202: where was the enclosure when the height was
picked by eye ("the height that it currently is at is perfect", 11:40:45 MDT),
and was the robot really standing still. Each step of the line is one move; the
flat stretches are the pauses between them. Below z ~87.9 the foot is on the plate.

    python3 plot_enclosure_height_a1_timeline.py   ->  enclosure-height-a1-timeline-2026-09-30.png
"""
import json
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = json.load(open(os.path.join(HERE, "enclosure-height-a1-2026-09-30.json")))

SURFACE, INK, INK_2, SERIES, BAND, GRID = (
    "#fcfcfb", "#0b0b0b", "#52514e", "#2a78d6", "#e9e8e4", "#e6e5e1")


def t(hms):
    return datetime.strptime(f"{RUN['date']} {hms}", "%Y-%m-%d %H:%M:%S")


def main():
    pts = [(s["t_local"], s["z"]) for k in ("descent_1", "descent_2", "descent_3")
           for s in RUN[k] if s.get("z") is not None]
    # Not in the descent lists; times from log.txt on the Pi (photos 64 and 79).
    pts += [("11:36:21", 90.0), ("11:41:34", 88.5)]
    pts.sort()
    pick = RUN["read_height_picked"]
    touch = RUN["contact_a1"]["nozzle_z_first_touch"]
    t_ret = t(RUN["return"]["cmd_local"])
    times = [t(p[0]) for p in pts] + [t_ret]
    zs = [p[1] for p in pts] + [pts[-1][1]]

    fig, ax = plt.subplots(figsize=(9, 4.4), dpi=110)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axhspan(85.9, touch, color=BAND, lw=0, zorder=0)
    ax.text(t("11:29:10"), 86.2, f"foot on the plate (below its first touch, z ≈ {touch:g})",
            color=INK_2, fontsize=9, va="bottom")
    ax.step(times, zs, where="post", color=SERIES, lw=2, zorder=3, solid_joinstyle="round")

    t_pick = t(pick["comment_local"])
    ax.axvline(t_pick, color=INK, lw=1, ls=(0, (4, 3)), zorder=2)
    ax.text(t_pick, 94.35, f"height picked (comment {pick['comment_local']})\nnozzle z {pick['nozzle_z']:g}",
            color=INK, fontsize=9, ha="right", va="top", linespacing=1.3,
            bbox=dict(boxstyle="square,pad=0.25", fc=SURFACE, ec="none"))
    ax.axvline(t_ret, color=INK_2, lw=1, ls=(0, (1, 2)), zorder=2)
    ax.text(t_ret, 94.35, " return", color=INK_2, fontsize=9, ha="left", va="top")

    ax.set_xlim(t("11:29:00"), t("11:42:30"))
    ax.set_ylim(85.9, 94.5)
    ax.set_yticks(range(86, 95))
    ax.set_ylabel("nozzle z (mm)", color=INK_2, fontsize=9)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.tick_params(colors=INK_2, labelsize=8.5, length=0)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)

    fig.text(0.012, 0.965, "Nozzle height over well A1, 2026-09-30 (MDT)",
             color=INK, fontsize=12, weight="bold", va="top")
    fig.text(0.012, 0.91,
             "Each step is one move; flat stretches are pauses. From z 90 down the moves were "
             "0.25–0.5 mm.\nBefore 11:29 it came down from z 125 in 1–4 mm steps.",
             color=INK_2, fontsize=9, va="top", linespacing=1.4)
    fig.subplots_adjust(left=0.07, right=0.985, top=0.79, bottom=0.09)
    out = os.path.join(HERE, "enclosure-height-a1-timeline-2026-09-30.png")
    fig.savefig(out, facecolor=SURFACE)
    print(out)


if __name__ == "__main__":
    main()
