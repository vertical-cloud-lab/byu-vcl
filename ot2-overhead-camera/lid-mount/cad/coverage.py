#!/usr/bin/env python3
"""How much of the OT-2 deck the camera sees at each zoom setting, from two mount positions.

Writes ../renders/deck_coverage.png and ../exports/deck_coverage.json.

The camera is the pinhole ot2_context.py uses: PUPIL_IN_LENS behind the lens front, looking
straight down, with the IMX477's long side along X. Fields are given at the top of a 96-well
plate (14.35 mm above the deck), where the wells are. The slots, 128 x 86 mm on a
132.5 x 90.5 mm pitch, come from Opentrons' OT-2 deck definition. Two positions:

  * over slot 5, the default (README section 3);
  * over the middle of the deck, halfway between slots 5 and 8, where one wide view takes in
    every slot.

After homing, the pipette head parks at the back right: X 418, Y 353 in Opentrons' Smoothie
driver (api/src/opentrons/drivers/smoothie_drivers/constants.py, HOMED_POSITION). HEAD_HOME
is the head and carriage from Opentrons' STEP, moved so that the right pipette sits there.
The script projects it from the lens onto the plate-top plane and reports whether it lands
in each view.

Depth of field uses a circle of confusion of two pixels (3.1 um), focused on the plate top.

    python coverage.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from lid_mount import EXPORTS, Params
from ot2_context import PLATE, PUPIL_IN_LENS, SENSOR, SLOTS

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "renders" / "deck_coverage.png"

PX = (4056, 3040)                  # IMX477 full resolution
WINDOW_TOP = 590.2                 # deck surface to the top of the window (exports/ot2_fit.json)
SLOT_SIZE = (128.0, 86.0)
WELL_D, WELL_DEPTH = 6.86, 10.9    # the plate in ot2_context.py
COC = 2 * 0.00155                  # circle of confusion, mm: two pixels
ZOOMS = {8.0: "#86b6ef", 16.0: "#3987e5", 25.0: "#1c5cab", 50.0: "#0d366b"}   # light -> dark
WORKING_ZOOM = 25.0
POSITIONS = {
    "slot 5": ("Mount over slot 5 (the default)", SLOTS[5]),
    "deck centre": ("Mount over the middle of the deck, halfway between slots 5 and 8",
                    (SLOTS[5][0], (SLOTS[5][1] + SLOTS[8][1]) / 2)),
}
# Head (covers, carriage, pipettes) after homing, deck mm: (x0, x1), (y0, y1), (z0, z1).
# The STEP draws it with the right pipette at about (213.5, 134.7); homing moves it to (418, 353).
HEAD_HOME = ((131.7 + 204.5, 261.3 + 204.5), (84.6 + 218.3, 252.7 + 218.3), (219.7, 576.1))

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#a3a29c"


def slot_rect(n: int) -> tuple[float, float, float, float]:
    """Slot n's outline in deck mm, including slot 12, the fixed trash."""
    x0, y0 = ((n - 1) % 3) * 132.5, ((n - 1) // 3) * 90.5
    return x0, y0, x0 + SLOT_SIZE[0], y0 + SLOT_SIZE[1]


def wells(slot: int) -> np.ndarray:
    """Well centres of a 96-well plate centred in a slot, deck mm."""
    cx, cy = SLOTS[slot]
    return np.array([(cx - 49.5 + 9 * i, cy + 31.5 - 9 * j) for i in range(12) for j in range(8)])


def view(p: Params, axis: tuple[float, float], focal: float) -> dict:
    z_pin = WINDOW_TOP + p.z_lens_front + PUPIL_IN_LENS          # above the deck
    dist = z_pin - PLATE[2]
    w, h = SENSOR[0] * dist / focal, SENSOR[1] * dist / focal
    x0, x1, y0, y1 = axis[0] - w / 2, axis[0] + w / 2, axis[1] - h / 2, axis[1] + h / 2

    in_view = {}
    for n in range(1, 13):
        a = slot_rect(n)
        frac = (max(0.0, min(x1, a[2]) - max(x0, a[0])) * max(0.0, min(y1, a[3]) - max(y0, a[1]))
                / (SLOT_SIZE[0] * SLOT_SIZE[1]))
        if frac > 0:
            in_view[n] = round(frac, 2)
    whole = [n for n, f in in_view.items() if f >= 0.999]

    # Steepest look into a well: a plate in slot 5, and a plate in any slot that is wholly in view.
    def steepest(slots):
        pts = np.vstack([wells(s) for s in slots])
        r = np.hypot(pts[:, 0] - axis[0], pts[:, 1] - axis[1]).max()
        return math.degrees(math.atan(r / dist))
    plates = [n for n in whole if n != 12]
    a5 = steepest([5]) if 5 in whole else None
    a_all = steepest(plates) if plates else None

    # Depth of field around the plate top, at f/4 and f/8.
    dof = {}
    for n_stop in (4.0, 8.0):
        hyper = focal ** 2 / (n_stop * COC) + focal
        near = dist * (hyper - focal) / (hyper + dist - 2 * focal)
        far = dist * (hyper - focal) / (hyper - dist) if dist < hyper else math.inf
        dof[f"f/{n_stop:g}"] = [round(dist - near, 1), round(dist - far, 1)]

    # Does the parked head show? Project points of its box from the lens onto the plate-top plane.
    g = [np.linspace(lo, hi, 25) for lo, hi in HEAD_HOME]
    hx, hy, hz = (a.ravel() for a in np.meshgrid(*g))
    k = dist / (z_pin - hz)
    sx, sy = axis[0] + (hx - axis[0]) * k, axis[1] + (hy - axis[1]) * k
    head_in_view = bool(np.any((sx > x0) & (sx < x1) & (sy > y0) & (sy < y1)))

    pxmm = PX[0] / w
    return {
        "field at the plate top (mm)": [round(w, 1), round(h, 1)],
        "field (deck mm)": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
        "resolution (px/mm)": round(pxmm, 1),
        "pixels across one well": round(pxmm * WELL_D),
        "slots wholly in view": whole,
        "slots in view (fraction of each)": in_view,
        "steepest look into a well, plate in slot 5 (deg)": None if a5 is None else round(a5, 1),
        "near-wall shadow, plate in slot 5 (mm)":
            None if a5 is None else round(WELL_DEPTH * math.tan(math.radians(a5)), 1),
        "steepest look into a well, any whole slot (deg)": None if a_all is None else round(a_all, 1),
        "near-wall shadow, any whole slot (mm)":
            None if a_all is None else round(WELL_DEPTH * math.tan(math.radians(a_all)), 1),
        "in focus, mm above (+) and below (-) the plate top": dof,
        "pipette head in view after homing": head_in_view,
    }


def draw(ax, p: Params, axis: tuple[float, float], title: str, report: dict) -> None:
    ax.set_facecolor(SURFACE)
    for n in range(1, 13):
        x0, y0, x1, y1 = slot_rect(n)
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec=MUTED, lw=0.8, ls=(0, (4, 3))))
        ax.text(x0 + 3, y1 - 3, f"{n}" + (" (trash)" if n == 12 else ""), ha="left", va="top",
                fontsize=9, color=INK2)
    # A 96-well plate in slot 5.
    cx, cy = SLOTS[5]
    ax.add_patch(FancyBboxPatch((cx - PLATE[0] / 2 + 3, cy - PLATE[1] / 2 + 3), PLATE[0] - 6, PLATE[1] - 6,
                                boxstyle="round,pad=3", fc="#f1f1ee", ec=INK2, lw=0.8))
    for x, y in wells(5):
        ax.add_patch(Circle((x, y), WELL_D / 2, fc="none", ec=MUTED, lw=0.5))

    for f, colour in ZOOMS.items():
        x0, y0, x1, y1 = report[f"{f:g} mm"]["field (deck mm)"]
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec=colour,
                               lw=2.6 if f == WORKING_ZOOM else 1.6))
        ax.text(x0 + 2, y1 + 2, f"{f:g} mm", ha="left", va="bottom", fontsize=9, color=INK,
                fontweight="bold" if f == WORKING_ZOOM else "normal",
                bbox=dict(fc=SURFACE, ec="none", pad=1.0))
    ax.plot([axis[0] - 8, axis[0] + 8], [axis[1], axis[1]], color=INK, lw=1.2)
    ax.plot([axis[0], axis[0]], [axis[1] - 8, axis[1] + 8], color=INK, lw=1.2)

    ax.text(196.5, -62, "FRONT (door)", ha="center", va="top", fontsize=10, color=INK, fontweight="bold")
    ax.text(196.5, 392, "BACK", ha="center", va="bottom", fontsize=10, color=INK, fontweight="bold")
    ax.set_title(title, fontsize=11.5, color=INK, loc="left")
    ax.set_xlim(-60, 455)
    ax.set_ylim(-78, 410)
    ax.set_aspect("equal")
    ax.axis("off")


def main() -> None:
    p = Params()
    reports = {key: {f"{f:g} mm": view(p, axis, f) for f in (8.0, 10.0, 12.0, 16.0, 20.0, 25.0, 35.0, 50.0)}
               for key, (_, axis) in POSITIONS.items()}

    fig, axes = plt.subplots(1, 2, figsize=(15.5, 8.4), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    for ax, (key, (title, axis)) in zip(axes, POSITIONS.items()):
        draw(ax, p, axis, title, reports[key])

    handles, labels = [], []
    for f, colour in ZOOMS.items():
        r = reports["slot 5"][f"{f:g} mm"]
        w, h = r["field at the plate top (mm)"]
        above, below = r["in focus, mm above (+) and below (-) the plate top"]["f/8"]
        sharp = (f"from the deck to {above:.0f} mm above the plate" if -below >= PLATE[2]
                 else f"within about ±{(above - below) / 2:.0f} mm of the plate top")
        handles.append(Line2D([], [], color=colour, lw=2.6 if f == WORKING_ZOOM else 1.6))
        labels.append(f"{f:g} mm{' (working zoom, README §2)' if f == WORKING_ZOOM else ''}: "
                      f"{w:.0f} x {h:.0f} mm, {r['resolution (px/mm)']:.1f} px/mm, "
                      f"{r['pixels across one well']} px across a well; sharp at f/8 {sharp}")
    fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.03, 0.075), frameon=False, fontsize=9.5,
               labelcolor=INK, handlelength=2.4, title="Zoom setting: field of view at the plate top, "
               "resolution, depth of field", title_fontsize=9.5, alignment="left")
    fig.suptitle("What the camera sees of the OT-2 deck at each zoom setting (seen from above)",
                 x=0.03, y=0.975, ha="left", fontsize=13, color=INK)
    fig.text(0.03, 0.012,
             "The zoom is a ring on the lens, set by hand from 8 to 50 mm; the camera can't pan or tilt. "
             "+ is the lens axis. Dashed outlines: Opentrons' deck slots. The plate in slot 5 is a standard "
             "96-well plate.\n"
             "Fields are at the top of the plate. After homing, the pipette head parks at the back right "
             "and stays out of every view drawn here; during a run it blocks whatever is under it.\n"
             "Pinhole model, 20 mm inside the lens front (about ±3 % on the field); depth of field for a "
             "two-pixel blur. Numbers in exports/deck_coverage.json, from cad/coverage.py.",
             fontsize=8.5, color=INK2, ha="left", va="bottom", linespacing=1.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.235, wspace=0.03)
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"wrote {OUT}")

    out = {"model": {"sensor (mm)": list(SENSOR), "pixels": list(PX),
                     "pinhole above the deck (mm)": round(WINDOW_TOP + p.z_lens_front + PUPIL_IN_LENS, 1),
                     "plate top above the deck (mm)": PLATE[2],
                     "circle of confusion (mm)": COC,
                     "pipette head after homing, deck mm (x, y, z ranges)": [list(r) for r in HEAD_HOME]},
           "positions (deck mm)": {k: list(a) for k, (_, a) in POSITIONS.items()},
           "views": reports}
    (EXPORTS / "deck_coverage.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: {f: (v["field at the plate top (mm)"], v["slots wholly in view"],
                              v["pipette head in view after homing"]) for f, v in r.items()}
                      for k, r in reports.items()}, indent=1))


if __name__ == "__main__":
    main()
