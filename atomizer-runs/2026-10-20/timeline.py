#!/usr/bin/env python3
"""Room-stream movement on Oct 20 with the four phone videos placed on the same clock.

    python timeline.py   # reads room_activity_10s.csv and alignment.json, writes timeline.png
"""
import csv, datetime as dt, json, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DAY = dt.date(2026, 10, 20)
SURFACE, INK, INK2, MUTED, SERIES, BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#2a78d6", "#e9e8e4"
EVENTS = [  # (MDT, label), all read off the phone videos at their aligned times
    ("13:29:40", "someone at the machine\n13:29–13:41, not filmed"),
    ("14:36:08", "argon out;\ncylinder swapped"),
    ("14:42:26", "furnace: Al at the\nbottom, cleaned"),
    ("14:54:08", "booster swap\nat the bench"),
    ("15:07:22", "bench scan\n39 562.5 Hz"),
    ("15:11:43", "\"discover a seal\""),
    ("15:26:30", "stack into\nthe door"),
    ("15:32:06", "scan\n39 645 Hz"),
    ("15:42:54", "regulator\nset"),
    ("15:43:49", "\"definitely a\nleak\""),
    ("15:50:45", "pump-down\nstarted"),
]


def t(hms):
    return dt.datetime.combine(DAY, dt.time.fromisoformat(hms))


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, "room_activity_10s.csv"))))
    x = [t(r["mdt"]) for r in rows]
    y = [float(r["mean_change"]) for r in rows]
    vids = json.load(open(os.path.join(HERE, "alignment.json")))["videos"]

    fig, ax = plt.subplots(figsize=(13, 4.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    top = 1000
    for vid, v in vids.items():
        a, b = t(v["start_mdt"]), t(v["end_mdt"])
        ax.axvspan(a, b, color=BAND, lw=0, zorder=0)
        ax.text(a + (b - a) / 2, top * 0.9, v["name"].replace("Video ", "V"), ha="center", va="top",
                fontsize=10, color=INK2, fontweight="bold")
    ax.plot(x, y, color=SERIES, lw=1.2, zorder=2)
    for k, (hms, label) in enumerate(EVENTS):
        ax.axvline(t(hms), color=MUTED, lw=0.8, ls=(0, (2, 2)), zorder=1)
        ax.text(t(hms), top * 0.45 / 2.6 ** (k % 3), " " + label, fontsize=7.5, color=INK, va="top", ha="left",
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.6, alpha=0.85), zorder=3)
    ax.set_yscale("log")
    ax.set_ylim(2, top)
    ax.set_xlim(x[0], x[-1])
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 15, 30, 45]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_xlabel("Oct 20, lab time (MDT), read off the stream's burned-in clock", color=INK2)
    ax.set_ylabel("room movement, 10 s mean (log)", color=INK2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color="#e6e5e1", lw=0.6)
    ax.set_title("Room-stream movement (picam-ot2, 144p) with Gage's four phone videos on the same clock",
                 loc="left", color=INK, fontsize=11.5)
    fig.text(0.01, 0.01, "Idle room reads about 4. Stream before 13:24:47 had aged out of YouTube's live DVR. "
             "At 15:59 someone handles the camera itself (a hand over the lens), so its view shifts slightly.",
             fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(HERE, "timeline.png"), facecolor=SURFACE)
    print("timeline.png")


if __name__ == "__main__":
    main()
