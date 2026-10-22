#!/usr/bin/env python3
"""Room-stream movement on Oct 21 with the run video placed on the same clock.

    python timeline.py   # reads room_activity_10s.csv and alignment.json, writes timeline.png
"""
import csv, datetime as dt, json, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DAY = dt.date(2026, 10, 21)
SURFACE, INK, INK2, MUTED, SERIES, BAND, ALERT = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#2a78d6", "#e9e8e4", "#c4314b"
EVENTS = [  # (MDT, label), read off the run video at its aligned times
    ("13:35:43", "\"we really need a\nlaser pointer\""),
    ("13:37:32", "cold wash;\n\"holding pressure\""),
    ("13:50:25", "visitor\n13:50–13:56"),
    ("13:53:54", "500 °C,\nO2 11 ppm"),
    ("13:56:45", "setpoint\n1000 °C"),
    ("13:59:07", "charge sinks;\nsetpoint 800 °C"),
    ("14:02:33", "pour: graining\npressure, rod up"),
    ("14:02:57", "\"What the?\""),
    ("14:06:04", "generator off,\n736 °C"),
    ("14:10:02", "\"measure where\nthe plate is\""),
]


def t(hms):
    return dt.datetime.combine(DAY, dt.time.fromisoformat(hms))


def main():
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "room_activity_10s.csv"))) if "13:20:00" <= r["mdt"] <= "14:40:00"]
    x = [t(r["mdt"]) for r in rows]
    y = [max(float(r["mean_change"]), 2.01) for r in rows]
    vids = json.load(open(os.path.join(HERE, "alignment.json")))["videos"]

    fig, ax = plt.subplots(figsize=(13, 4.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    top = 1000
    for vid, v in vids.items():
        a, b = t(v["start_mdt"]), t(v["end_mdt"])
        ax.axvspan(a, b, color=BAND, lw=0, zorder=0)
        ax.text(a + (b - a) / 2, top * 0.9, "Run Video 1 (p6Itg-ngMZA)", ha="center", va="top",
                fontsize=10, color=INK2, fontweight="bold")
    ax.axvspan(t("14:02:33"), t("14:06:04"), color="#f6dfe3", lw=0, zorder=0.5)
    ax.plot(x, y, color=SERIES, lw=1.2, zorder=2)
    for k, (hms, label) in enumerate(EVENTS):
        c = ALERT if hms in ("14:02:33", "14:02:57") else MUTED
        ax.axvline(t(hms), color=c, lw=0.8, ls=(0, (2, 2)), zorder=1)
        ax.text(t(hms), top * 0.45 / 2.6 ** (k % 3), " " + label, fontsize=7.5, color=INK, va="top", ha="left",
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.6, alpha=0.85), zorder=3)
    ax.set_yscale("log")
    ax.set_ylim(2, top)
    ax.set_xlim(x[0], x[-1])
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 10, 20, 30, 40, 50]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_xlabel("Oct 21, lab time (MDT), read off the stream's burned-in clock", color=INK2)
    ax.set_ylabel("room movement, 10 s mean (log)", color=INK2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color="#e6e5e1", lw=0.6)
    ax.set_title("Room-stream movement (picam-ot2, 144p) with the Oct 21 run video on the same clock; pour shaded",
                 loc="left", color=INK, fontsize=11.5)
    fig.text(0.01, 0.01, "Idle room reads about 4-5. The phone points at the floor for most of the pour, so the plate is never in frame. "
             "People are in the room on and off after the video; the clean-up, to about 16:40, was not filmed.", fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(HERE, "timeline.png"), facecolor=SURFACE)
    print("timeline.png")


if __name__ == "__main__":
    main()
