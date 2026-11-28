"""If we were to build a facility like this, small: the #318 lab in high-bay buildings of 3,000-10,000 ft2.

    python3 facility/small_footprint.py    # -> facility/out/small_footprint.png, facility/out/small_footprint.json

Sterling asked on #343 (2026-11-28) to look at options of 3,000-10,000 ft2 and to keep the high ceiling. Two panels:

- **Plans.** Three buildings drawn to one scale, each holding a version of PR #318's lab as ``footprint.py`` places it
  (``setup_lab.FLOOR_PLAN``, ``r8_scale``), with the rooms a small building can't do without. Everything outside the
  #318 floor and the array is an illustrative allocation, not a design.
- **Section.** What height buys on the same floor: two Shuttles, as in #318, at the tallest height under each clear
  height, and how many trays they hold by ``scale.py``'s slot rule (re-implemented in ``footprint.py``).

Reuses ``footprint.py``'s geometry, slot rule and colours, so the two figures agree.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import footprint as fp  # noqa: E402
from footprint import (AISLE_318, ARRAY_D, AQUA, BLUE, GRID, H_LAB, H_TALL, INK, INK2, MM_FT, MUTED,  # noqa: E402
                       N_UNITS, ORANGE, PITCH_X, SKIN, SURFACE, UNIT_D, UNIT_W, Y_UNIT, box, machine_rects, tint,
                       trays_per_unit, tallest_under)

import matplotlib.pyplot as plt  # noqa: E402  (footprint has already chosen the Agg backend)
from matplotlib.patches import Rectangle  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
f = lambda v: v / MM_FT  # noqa: E731  mm -> ft
ROUND11 = {"glovebox", "rePowder", "sieving", "Shuttle 1", "Shuttle 2", "MIDI", "packaging", "Instron\n100 kN",
           "2 kN", "hood", "DED", "wire EDM"}
SHORT = {"Shuttle 1": "VLM", "Shuttle 2": "VLM", "EOS M 400-4": "EOS", "Meltio cell": "Meltio", "MIDI": "MIDI",
         "DED": "DED", "wire EDM": "EDM"}

# Three buildings (ours, illustrative). Width x depth in ft, and where Shuttle 1's centre lands (ox, oy).
BUILDINGS = [
    dict(key="3k", w=74.0, d=41.0, ox=35.0, oy=29.8, scaleup=False, door=("W", 16.0), pad=(-8.5, 1.5),
         title="3,000 ft² (74 x 41 ft): round 11's floor and nothing else",
         rooms=[("gas and powder cabinets, eyewash, panels, chiller", 0.0, 35.4, 74.0, 5.6)],
         note="Offices, receiving and a workshop stay on campus. No powder room: sprinklered, the jar store stays under one\n"
              "control area's limit if the powder tests as a flammable solid. No room for the EOS or the Meltio cell."),
    dict(key="6k", w=100.0, d=60.0, ox=39.4, oy=42.2, scaleup=True, door=("E", 43.0), pad=(101.5, 6.0),
         title="6,000 ft² (100 x 60 ft): with the EOS, the Meltio cell and the rooms it can't do without",
         rooms=[("powder room\n(outside wall;\nH room if over\nthe limits)", 80.0, 0.0, 20.0, 22.0),
                ("plant: chiller,\nair, N$_2$, 400 V\ntransformer", 80.0, 22.0, 20.0, 18.0),
                ("receiving", 80.0, 40.0, 20.0, 20.0),
                ("control room, lockers", 0.0, 48.6, 34.0, 11.4),
                ("workshop", 34.0, 48.6, 24.0, 11.4),
                ("staging", 58.0, 48.6, 22.0, 11.4)],
         note="Offices on campus. A 12 ft grade-level door into receiving takes the EOS and the Meltio cell."),
    dict(key="10k", w=125.0, d=80.0, ox=39.4, oy=42.2, scaleup=True, array=(83.0, 53.0), door=("N", 59.0),
         pad=(126.5, 6.0),
         title="10,000 ft² (125 x 80 ft): the same, plus the 50 ft array (8 x 15.15 m) in a high bay",
         rooms=[("powder room\n(outside wall)", 83.0, 0.0, 42.0, 24.0),
                ("plant and electrical", 83.0, 24.0, 42.0, 25.0),
                ("control room,\noffices", 0.0, 50.0, 28.0, 30.0),
                ("workshop", 28.0, 50.0, 24.0, 30.0),
                ("receiving and\nstaging", 52.0, 50.0, 28.0, 30.0)],
         note="The array needs 51-53 ft clear over its 956 ft²; the rest of the building can be lower.\n"
              "Under 36 ft, 13 units of 10.5 m hold the same 352 trays in 20.9 x 7.4 m (1,672 ft²)."),
]
SCALE_X0 = 0.0  # all plans share one scale: the axes are sized in proportion to each building's width


def plan(ax, b: dict) -> dict:
    W, D = b["w"], b["d"]
    ax.set_facecolor(SURFACE)
    for label, x0, y0, w, h in b["rooms"]:
        box(ax, x0, y0, w, h, tint(AQUA, 0.14), AQUA, 0.8)
        ax.text(x0 + w / 2, y0 + h / 2, label, ha="center", va="center", fontsize=5.6, color=INK, linespacing=1.1,
                zorder=6)
    ox, oy = b["ox"], b["oy"]
    ax0, ax1, ay0, ay1 = AISLE_318
    box(ax, ox + f(ax0), oy + f(ay0), f(ax1 - ax0), f(ay1 - ay0), tint(BLUE, 0.05), tint(BLUE, 0.6), 0.5,
        (0, (3, 2)), z=2)
    used = []
    for name, (x0, x1, y0, y1) in machine_rects():
        if not b["scaleup"] and name not in ROUND11:
            continue
        used.append((x0, x1, y0, y1))
        box(ax, ox + f(x0), oy + f(y0), f(x1 - x0), f(y1 - y0), tint(BLUE, 0.30), BLUE, 0.7, z=3)
        if name in SHORT:
            ax.text(ox + f((x0 + x1) / 2), oy + f((y0 + y1) / 2), SHORT[name], ha="center", va="center",
                    fontsize=4.8, color=INK, zorder=6)
    if "array" in b:
        axx, ayy = b["array"]
        aw, ad = f(N_UNITS / 2 * PITCH_X), f(ARRAY_D)
        box(ax, axx, ayy, aw, ad, tint(ORANGE, 0.06), ORANGE, 0.6, (0, (4, 2)), z=2)
        for row in (0, 1):
            for i in range(4):
                cx = axx + f((i + 0.5) * PITCH_X)
                cy = ayy + ad / 2 + (1 if row else -1) * f(Y_UNIT)
                w, d = f(UNIT_W + 2 * SKIN), f(UNIT_D + 2 * SKIN)
                box(ax, cx - w / 2, cy - d / 2, w, d, tint(ORANGE, 0.35), ORANGE, 0.7, z=3)
        ax.text(axx + aw / 2, ayy + ad / 2, "array", ha="center", va="center", fontsize=5.0, color=INK, zorder=6,
                bbox=dict(fc=SURFACE, ec="none", pad=0.3))
    side, at = b["door"]                                   # a 14 ft grade-level door (ours)
    door = {"W": (-1.2, at, 2.4, 14.0), "E": (W - 1.2, at, 2.4, 14.0), "N": (at, D - 1.2, 14.0, 2.4)}[side]
    ax.add_patch(Rectangle(door[:2], *door[2:], facecolor=INK2, edgecolor="none", zorder=10))
    px, py = b["pad"]                                      # a 7 x 7 ft pad for a 1,500 L microbulk tank
    box(ax, px, py, 7.0, 7.0, tint(INK2, 0.06), INK2, 0.6, "--", hatch="////", z=1)
    ax.text(px + 3.5, py + 8.0, "Ar\npad", ha="center", va="bottom", fontsize=4.8, color=INK2, linespacing=1.0)
    ax.add_patch(Rectangle((0, 0), W, D, facecolor="none", edgecolor=INK, linewidth=1.4, zorder=9))
    ax.text(0, D + 2.0, b["title"], ha="left", va="bottom", fontsize=7.2, color=INK)
    ax.text(0, -2.0, b["note"], ha="left", va="top", fontsize=5.8, color=INK2, linespacing=1.2)
    ax.set_xlim(-11, 135)
    ax.set_ylim(-11, D + 8)
    ax.set_aspect("equal")
    ax.set_anchor("W")
    ax.axis("off")
    xs = [v for r in used for v in r[:2]] + [ax0, ax1]
    ys = [v for r in used for v in r[2:]]
    return dict(building_ft=(W, D), building_ft2=round(W * D),
                lab_bbox_m=(round((max(xs) - min(xs)) / 1000, 1), round((max(ys) - min(ys)) / 1000, 1)),
                rooms_ft2={lbl.replace("\n", " "): round(w * h) for lbl, _, _, w, h in b["rooms"]})


NOTES = ("Notes (ours, from facility/needs.md):\n"
         "- Power: about 230 A at 480 V for round 11, 350 A with the EOS and\n"
         "  the Meltio cell; the array adds eight Shuttles of up to 8.6 kVA each\n"
         "  and whatever its trays draw.\n"
         "- The lab as drawn needs 16-18 ft clear. More height buys trays,\n"
         "  not floor: 36 ft is the usual top for warehouses here, and the\n"
         "  15.15 m array needs 51-53 ft.\n"
         "- Under 36 ft, two 10.5 m Shuttles hold 58 trays, four times the\n"
         "  14-15 of #318's pair, on the same 220 ft².\n"
         "- Grade-level doors (dark bars) about 14 ft wide; argon pads 7 x 7 ft\n"
         "  for a 1,500 L microbulk tank.\n"
         "- Trays by footprint.py's copy of scale.py's slot rule, which gives\n"
         "  14 for #318's two 3.95 m units against #318's 15.")
CASES = [("as in #318", None), ("18 ft", 18), ("24 ft", 24), ("32 ft", 32), ("36 ft", 36), ("51 ft", 51.2)]


def tray_table() -> list[dict]:
    rows = []
    for label, clear in CASES:
        h = H_LAB if clear is None else (H_TALL if clear == 51.2 else tallest_under(clear))
        n = trays_per_unit(h)
        rows.append(dict(case=label, clear_ft=clear, unit_mm=h, trays_per_unit=n, trays_two_units=2 * n))
    return rows


def section(ax, rows: list[dict]) -> None:
    ax.set_facecolor(SURFACE)
    w = f(UNIT_W + 2 * SKIN)
    gap = f(800.0)
    pair = 2 * w + gap
    step = pair + 6.0
    ax.plot([-3, len(rows) * step], [0, 0], color=INK, lw=1.1, zorder=3)
    for i, r in enumerate(rows):
        x = i * step
        h = f(r["unit_mm"])
        col, a = (BLUE, 0.30) if r["clear_ft"] is None else (ORANGE, 0.35)
        for k in (0, 1):
            box(ax, x + k * (w + gap), 0, w, h, tint(col, a), col, 0.8, z=5)
        if r["clear_ft"] is not None:
            c = r["clear_ft"]
            ax.plot([x - 1.2, x + pair + 1.2], [c, c], color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=4)
            ax.text(x + pair / 2, c + 0.6, f"{c:g} ft clear", ha="center", va="bottom", fontsize=5.9, color=INK2)
        m = f"{r['unit_mm'] / 1000:.2f}".rstrip("0").rstrip(".")
        ax.text(x + pair / 2, -1.0, f"{m} m units", ha="center", va="top", fontsize=5.6, color=INK2)
        ax.text(x + pair / 2, -4.2, f"{r['trays_two_units']} trays", ha="center", va="top", fontsize=6.8,
                color=INK, fontweight="bold")
        if r["clear_ft"] is None:
            ax.text(x + pair / 2, h + 0.8, "#318 today\n(15 trays)", ha="center", va="bottom", fontsize=5.6,
                    color=INK2, linespacing=1.1)
    for c in (10, 20, 30, 40, 50):
        ax.plot([-3, len(rows) * step - 6], [c, c], color=GRID, lw=0.4, ls=(0, (1, 3)), zorder=0.5)
        ax.text(-3.5, c, f"{c} ft", ha="right", va="center", fontsize=5.6, color=MUTED)
    ax.set_xlim(-9, len(rows) * step - 4)
    ax.set_ylim(-8, 56)
    ax.set_aspect("equal")
    ax.set_anchor("N")
    ax.axis("off")
    ax.set_title("Same floor, more trays: two Shuttles at the tallest\nheight under each clear height "
                 "(18 in under sprinklers)", fontsize=8.6, color=INK, loc="left", pad=4)


def main() -> dict:
    OUT.mkdir(exist_ok=True)
    fig = plt.figure(figsize=(12.0, 9.6), dpi=200, facecolor=SURFACE)
    heights = [b["d"] + 19 for b in BUILDINGS]
    gs = fig.add_gridspec(3, 2, width_ratios=[1.0, 0.62], height_ratios=heights, left=0.01, right=0.99, top=0.9,
                          bottom=0.04, wspace=0.04, hspace=0.06)
    out = {}
    for i, b in enumerate(BUILDINGS):
        out[b["key"]] = plan(fig.add_subplot(gs[i, 0]), b)
    rows = tray_table()
    section(fig.add_subplot(gs[0, 1]), rows)
    note = fig.add_subplot(gs[1:, 1])
    note.axis("off")
    note.text(0.0, 0.95, NOTES, ha="left", va="top", fontsize=6.6, color=INK2, linespacing=1.4,
              transform=note.transAxes)
    fig.suptitle("If we were to build a facility like this, small: PR #318's lab in 3,000-10,000 ft² with a high "
                 "ceiling", x=0.01, ha="left", fontsize=11.0, color=INK, y=0.985)
    fig.text(0.01, 0.958, "Plans to one scale. The #318 floor (blue) and the array (orange) are placed from the "
             "repo's own figures (footprint.py); the green rooms are one way the rest could go, not a design.\n"
             "Height costs no floor: on the same two footprints, Shuttles of 10.5 m hold about four times the trays "
             "of #318's 3.95 m units, and 15.15 m units six times.", fontsize=7.0, color=INK2, ha="left", va="top",
             linespacing=1.3)
    items = [(tint(BLUE, 0.30), BLUE, "PR #318's floor: round 11, or with round 8's EOS and Meltio cell"),
             (tint(ORANGE, 0.35), ORANGE, "Kardex Shuttles taller than #318's (scale.py's slot rule)"),
             (tint(AQUA, 0.14), AQUA, "support rooms: illustrative")]
    handles = [Rectangle((0, 0), 1, 1, facecolor=fc, edgecolor=ec, linewidth=0.8) for fc, ec, _ in items]
    fig.legend(handles, [t for *_, t in items], loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=3, frameon=False,
               fontsize=6.8, handlelength=1.4, labelcolor=INK2)
    fig.savefig(OUT / "small_footprint.png", facecolor=SURFACE)
    tab = dict(buildings=out, trays=rows, array_ft2=round(N_UNITS / 2 * PITCH_X * ARRAY_D / MM_FT ** 2),
               array_m=(round(N_UNITS / 2 * PITCH_X / 1000, 1), round(ARRAY_D / 1000, 1)),
               clear_for_array_ft=round((H_TALL + fp.SPRINKLER) / MM_FT, 1))
    (OUT / "small_footprint.json").write_text(json.dumps(tab, indent=1) + "\n")
    return tab


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
