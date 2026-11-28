#!/usr/bin/env python3
"""The atomizer's turnaround after a run, in the automated cell (#353): who does what, in what order, and roughly
how long, from the end of the pour until the machine is ready for the next charge.

    python3 atom_timeline.py        # out/atom/turnaround.png and out/atom/turnaround.json

The order and the waits come from the lab's own SOP (DAL PR 253 "Cooldown", "Powder Collection and Cleaning";
PR 178 "After a run", "Cleaning and maintenance"; the BN recoat from PR 220). The arms' step times are ESTIMATES, set
from the clips' motions at a working pace (a UR10e at a few hundred mm/s, slower near graphite); none is measured.
A spare crucible, coated and dried the night before, goes in while the used one is cleaned and recoated, so the
overnight dry is not on the turnaround's path (DAL: keep per-alloy consumable sets).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "atom"

# the reference categorical palette (dataviz skill, light mode; validated: all checks pass, contrast relief by labels)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SURFACE, INK, INK2, GRID, NEUTRAL = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#b9b8b2"
PROC = ["The run, watched", "Latch and lid", "Container", "Vacuum", "Plate", "Crucible out", "Clean and BN",
        "Crucible in"]
COLOR = dict(zip(PROC, SERIES))
LANES = ["The machine", "Arm 1 (front, right)", "Arm 2 (door side)", "A person"]

# (lane, procedure or None for a machine state, start min, minutes, label, source)
STEPS = [
    ("The machine", "The run, watched", -6, 6, "pour (the cameras watch)", "PR 178: the pour lasts 2-5 min; DAL PR 189"),
    ("The machine", None, 0, 14, "cools to 400 °C", "SOP: open at or below 400 °C (time estimated)"),
    ("The machine", None, 14, 46, "vented; the furnace cools until it can be touched", "SOP Cooldown 3; PR 178: 150 °C is too hot (time estimated)"),
    ("The machine", None, 88, 8, "pump-down: the joints hold", "no 'Pressure crucible' warning (PR 178 / crucible_automation.md 13)"),
    ("Arm 1 (front, right)", "Latch and lid", 16, 3, "unlatch, lid up", "clip atom_latch"),
    ("Arm 1 (front, right)", "Container", 23, 4, "cup off", "SOP Powder Collection 3: one holds, one unclamps"),
    ("Arm 1 (front, right)", "Container", 49, 4, "clean cup on", "SOP Powder Collection 10"),
    ("Arm 1 (front, right)", "Crucible out", 60, 10, "crucible out", "clip atom_crucible_out"),
    ("Arm 1 (front, right)", "Crucible in", 70, 14, "spare crucible in, nut snug", "clip atom_crucible_in"),
    ("Arm 1 (front, right)", "Latch and lid", 84, 3, "lid, latch", "clip atom_latch"),
    ("Arm 1 (front, right)", "Clean and BN", 90, 26, "used crucible: cleaned, 3 BN passes", "clip atom_bn; DAL PR 220"),
    ("Arm 2 (door side)", "Container", 16, 6, "door; powder brushed into cup", "SOP Powder Collection 2"),
    ("Arm 2 (door side)", "Container", 23, 4, "(holds the cup)", "PR 178 Chamber and container 1"),
    ("Arm 2 (door side)", "Vacuum", 27, 10, "chamber vacuumed", "clip atom_vacuum; byu-vcl PR 80"),
    ("Arm 2 (door side)", "Plate", 37, 12, "plate swap", "clip atom_plate (on an alloy change or a cracked plate)"),
    ("Arm 2 (door side)", "Container", 49, 4, "(holds the cup)", "SOP / PR 178"),
    ("Arm 2 (door side)", "Crucible out", 63, 7, "holds the nut", "PR 178 Furnace and charge 1"),
    ("Arm 2 (door side)", "Crucible in", 72, 8, "threads the nut on", "PR 178 Furnace and charge 3"),
    ("Arm 2 (door side)", "Plate", 81, 3, "door shut", "SOP Configuring the tower 18"),
    ("A person", "Vacuum", 38, 3, "seals the vacuum's liner, if over 25 % full", "vacuum SOP §4 (not every run)"),
]


def rounded(ax, x, y, w, h, color):
    ax.add_patch(FancyBboxPatch((x + 0.15, y), max(0.3, w - 0.3), h, boxstyle="round,pad=0,rounding_size=0.35",
                                linewidth=0, facecolor=color, mutation_aspect=0.25))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(13, 5.0), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    row = {l: len(LANES) - 1 - i for i, l in enumerate(LANES)}
    h = 0.34
    free = {}                     # per lane: where the last label over / under the bars ends (minutes)
    for lane, proc, t0, dt, label, _ in sorted(STEPS, key=lambda r: r[2]):
        y = row[lane] - h / 2
        rounded(ax, t0, y, dt, h, COLOR[proc] if proc else NEUTRAL)
        if label.startswith("("):            # an unlabelled bar: the arm above says what it is part of
            continue
        over, under = free.get((lane, "over"), -99), free.get((lane, "under"), -99)
        below = t0 < over + 0.5 and t0 >= under + 0.5        # over the bar if there is room, else under it
        free[(lane, "under" if below else "over")] = t0 + 0.4 + 0.82 * len(label)
        ax.text(t0 + 0.4, row[lane] + (-(h / 2) - 0.07 if below else h / 2 + 0.07), label, fontsize=7.2, color=INK2,
                va="top" if below else "bottom", ha="left")
    ax.set_yticks(list(row.values()), list(row.keys()), fontsize=9, color=INK)
    ax.set_ylim(-0.7, len(LANES) - 0.2)
    ax.set_xlim(-8, 132)
    ax.set_xlabel("minutes from the end of the pour (step times estimated)", fontsize=9, color=INK2)
    ax.tick_params(axis="x", colors=INK2, labelsize=8)
    ax.tick_params(axis="y", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.text(117, row["Arm 1 (front, right)"], "→ dries overnight", fontsize=7.2, color=INK2, ha="left", va="center")
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLOR[p]) for p in PROC] + [plt.Rectangle((0, 0), 1, 1, color=NEUTRAL)]
    ax.legend(handles, PROC + ["the machine's own state"], loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=9,
              frameon=False, fontsize=7.5, handlelength=1.0, handleheight=0.8, columnspacing=1.0, labelcolor=INK2)
    ax.set_title("The turnaround after a run, automated: two arms, the machine, and what is left to a person",
                 fontsize=11, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "turnaround.png", facecolor=SURFACE)
    data = [dict(lane=l, procedure=p, start_min=t0, minutes=dt, step=lab, source=src) for l, p, t0, dt, lab, src in STEPS
            if lab]
    (OUT / "turnaround.json").write_text(json.dumps(dict(note=__doc__.split("\n\n")[1].replace("\n", " "), steps=data),
                                                    indent=1, ensure_ascii=False) + "\n")
    print(OUT / "turnaround.png")


if __name__ == "__main__":
    main()
