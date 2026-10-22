#!/usr/bin/env python3
"""Can stirrers sit side by side on the CubXL deck, in X and in Y? The deck's slot grid, what
sets the stirrer's 56 x 56 mm footprint, and a 49 x 44 mm layout that tiles at the grid's own
pitch, checked part by part. Draws img/deck_tiling.png and img/deck_tiling_plan.png.

The CubXL+ deck (Cubware PandaDeck.step at 352aa95) is a 480 x 490 x 10 mm plate with 10 x 25 mm
pill slots in 18 columns 25 mm apart (X) and 10 rows 45 mm apart (Y). A stirrer's two keys sit
in adjacent columns of one row, with the vial midway between them, so stirrers can only be a
whole number of columns and rows apart. Side by side therefore means 2 columns (50 mm) in X and
1 row (45 mm) in Y, and the footprint has to fit inside that, less a gap.

The stirrer's numbers come from onshape/vial_stirrer.fs: its constants are read from the file,
and the few positions written as literals inside its functions are copied here with the function
named. The compact layout is a proposal checked in plan, not a model: its parts are the same
parts, moved or trimmed as listed in COMPACT.

    python analysis/deck_tiling.py                              # prints deck_tiling_output.txt, draws both figures
    python analysis/deck_tiling.py --deck-step PandaDeck.step   # also re-reads the slot grid from Cubware's STEP

Needs numpy, shapely and matplotlib (and trimesh for the STL bounds, if installed).
"""

from __future__ import annotations

import argparse
import itertools
import math
import pathlib
import re

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, box

HERE = pathlib.Path(__file__).resolve().parent.parent
FS = HERE / "onshape" / "vial_stirrer.fs"

# CubXL+ deck, from Cubware PandaDeck.step (352aa95): the R5 slot ends' centres
DECK_W, DECK_D = 480.0, 490.0
N_COLS, N_ROWS = 18, 10
COL0 = 27.5                  # first column's X; rows are 45 apart, first at 45 from the edge

# Orion OD4010 drawing (rev. 6/19/2024): 40 +-0.5 frame, 32 +-0.5 hole square, 4 x 4.3 +-0.5 holes
FAN_TOL = 0.5
FAN_CORNER_R = 3.0           # makeFan's frame corner radius
KEY_PLAY = 0.1               # key in slot, a side (9.8 in 10, 24.8 in 25)
MIN_GAP = 1.0                # gap left between neighbours

# Literals inside vial_stirrer.fs's functions
POST_R = 4.0                 # makeBase: fan-post and corner-post bosses
BOARD = (-22.6, -8.9, -1.6, 8.9)     # makeBase rails / makeController: XIAO, or the 21 x 17.5 junction board
STOP = (-1.6, -5.0, -0.4, 5.0)       # makeBase: the board's stop
MOSFET = (-0.5, -5.0, 21.6, 5.0)     # makeDriver: TO-220 lying flat, leads to tab
DIODE = (4.0, -10.85, 9.2, -8.15)    # makeDriver: DO-41
HALL = (-13.3, -2.05, -10.3, 2.05)   # makeHall: US1881 on the recess ceiling
GROOVE = (-22.8, -2.6, -13.0, 2.6)   # makeHolder: groove for the Hall leads (from the recess edge)
USB_NOTCH = 6.5              # makeBase: the -X wall's notch, y +-6.5
INSERT_HOLE_D = 6.5          # makeBase: insert holes are 6.5 deep
HEAD_D, HEAD_H = 5.5, 3.0    # M3 socket head

# The compact layout. Everything not listed here is unchanged.
COMPACT = {
    "W": 49.0, "D": 44.0,    # footprint, X x Y
    "R": 5.0,                # corner radius, as now
    "WALL": 1.6,             # base walls, 4 perimeters
    "SCREW_L": 20.0,         # 4 x M3 x 20 through flange and fan into the fan-post inserts (in the kit)
    "CBORE_D": 6.5,          # their counterbores in the flange
    "PAD": 0.5,              # pads under the flange on the fan's corners: keeps today's 0.5 mm over the rotor
    "NOTCH": (-11.0, -3.0),  # cable notch, in the -Y wall between the fan posts
    "BOARD_IN": 0.5,         # the junction board's stop moves this far toward +X, so a hand-cut board clears the wall
    "CABLE_D": 5.0,          # 22 AWG x 4 jacket, allowed for
}


def fs_constants(path: pathlib.Path) -> dict:
    """The top-level `const NAME = expr;` lines of the FeatureScript, evaluated in order."""
    env: dict = {}
    for m in re.finditer(r"^const\s+([A-Z_0-9]+)\s*=\s*([^;]+);", path.read_text(), re.M):
        try:
            env[m.group(1)] = float(eval(m.group(2), {"__builtins__": {}}, dict(env)))
        except Exception:
            pass
    return env


def deck_grid_from_step(path: pathlib.Path) -> tuple[list, list]:
    """Slot-end circle centres (R5) in Cubware's deck STEP, in mm: the column X's and the row Y's."""
    txt = path.read_text()
    ent = dict(re.findall(r"#(\d+)\s*=\s*([^;]*);", txt, re.S))

    def point(i):
        m = re.search(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", ent[i])
        return [float(v) * 1000 for v in m.group(1).split(",")]      # Onshape writes metres

    xs, ys = set(), set()
    for v in ent.values():
        m = re.match(r"\s*CIRCLE\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*([-\d.Ee+]+)\s*\)", v)
        if m and abs(float(m.group(2)) * 1000 - 5.0) < 1e-6:
            a = re.search(r"AXIS2_PLACEMENT_3D\s*\(\s*'[^']*'\s*,\s*#(\d+)", ent[m.group(1)])
            x, y, _ = point(a.group(1))
            xs.add(round(x, 3))
            ys.add(round(y, 3))
    cols = sorted(xs)
    ends = sorted(ys)
    rows = [round((ends[i] + ends[i + 1]) / 2, 3) for i in range(0, len(ends), 2)]
    return cols, rows


def rrect(cx, cy, w, d, r, res=24):
    return box(cx - w / 2 + r, cy - d / 2 + r, cx + w / 2 - r, cy + d / 2 - r).buffer(r, resolution=res)


def pill(cx, cy, w, c):
    return LineString([(cx, cy - c / 2), (cx, cy + c / 2)]).buffer(w / 2, resolution=24)


def rect(b):
    return box(*b)


def moved_in(b):
    """A box from vial_stirrer.fs moved toward +X by COMPACT["BOARD_IN"]: the junction board and its stop."""
    return (b[0] + COMPACT["BOARD_IN"], b[1], b[2] + COMPACT["BOARD_IN"], b[3])


def pitch(size: float, grid: float, at_least: int) -> int:
    """Grid steps between neighbours for a footprint of this size, leaving MIN_GAP."""
    return max(at_least, math.ceil((size + MIN_GAP) / grid - 1e-9))


def per_deck(step_c: int, step_r: int) -> int:
    return ((N_COLS - 2) // step_c + 1) * ((N_ROWS - 1) // step_r + 1)


def check(c: dict) -> list:
    """(what, value, limit, ok) for every plan-view check of the compact layout, plus the screw."""
    W, D, R, wall = COMPACT["W"], COMPACT["D"], COMPACT["R"], COMPACT["WALL"]
    half_fan = c["FAN_W"] / 2 + FAN_TOL / 2
    outer = rrect(0, 0, W, D, R)
    inner = rrect(0, 0, W - 2 * wall, D - 2 * wall, R - wall)
    fan_max = rrect(0, 0, 2 * half_fan, 2 * half_fan, FAN_CORNER_R)
    fp = c["FAN_PITCH"] / 2
    posts = [Point(sx * fp, sy * fp).buffer(POST_R) for sx in (-1, 1) for sy in (-1, 1)]
    cbores = [Point(sx * fp, sy * fp).buffer(COMPACT["CBORE_D"] / 2) for sx in (-1, 1) for sy in (-1, 1)]
    cup = Point(0, 0).buffer(c["CUP_OD"] / 2, resolution=64)
    keys = [pill(sx * c["KEY_X"], 0, c["KEY_W"], c["SLOT_C"]) for sx in (-1, 1)]
    parts = {"junction board": rect(moved_in(BOARD)), "MOSFET": rect(MOSFET), "diode": rect(DIODE),
             "stop": rect(moved_in(STOP))}
    n0, n1 = COMPACT["NOTCH"]
    out = []

    def add(what, value, limit, ok=None):
        out.append((what, value, limit, value >= limit if ok is None else ok))

    add("X: footprint + gap fits 2 columns (mm)", 2 * c["PITCH_X"] - W, MIN_GAP)
    add("Y: footprint + gap fits 1 row (mm)", c["PITCH_Y"] - D, MIN_GAP)
    add("fan at +0.5 tolerance inside the walls, Y side (mm a side)", (D - 2 * wall) / 2 - half_fan, 0.1)
    add("fan at +0.5 tolerance inside the walls, at the corners (mm)",
        inner.exterior.distance(fan_max) if inner.contains(fan_max) else -1.0, 0.1)
    add("Hall and fan leads: gap from fan (+0.5) to the -X wall (mm)", (W - 2 * wall) / 2 - half_fan, 2.0)
    for name, g in parts.items():
        add(f"{name} inside the walls (mm)", inner.exterior.distance(g) if inner.contains(g) else -1.0, 0.2)
        add(f"{name} clear of the fan posts (mm)", min(p.distance(g) for p in posts), 0.2)
    add("Hall groove ends inside the walls (mm)", (W - 2 * wall) / 2 + GROOVE[0], 0.0)
    add("keys inside the footprint (mm)", min(outer.exterior.distance(k) for k in keys), 0.0)
    add("counterbores: wall to the flange edge (mm)", min(outer.exterior.distance(b) for b in cbores), 1.2)
    add("counterbores: wall to the cup (mm)", min(cup.distance(b) for b in cbores), 1.2)
    add("cable notch clear of the -X,-Y fan post (mm)", n0 - (-fp + POST_R), 0.5)
    add("cable notch clear of the diode (mm)", DIODE[0] - n1, 0.5)
    add("cable notch wide enough for the cable (mm)", n1 - n0, COMPACT["CABLE_D"] + 1.0)
    # the screw through flange and fan: seat, tip, engagement
    top = c["Z_WALL"] + c["FLANGE_T"]
    hole_bottom = c["Z_FAN0"] - INSERT_HOLE_D
    seat = hole_bottom + 0.5 + COMPACT["SCREW_L"]
    add("M3 x 20: counterbore depth (mm)", top - seat, 0.0, 0 < top - seat < c["FLANGE_T"] - 2.0)
    add("M3 x 20: thread in the insert (mm)", c["Z_FAN0"] - (seat - COMPACT["SCREW_L"]), c["INSERT_L"])
    add("M3 x 20: tip above the hole floor (mm)", seat - COMPACT["SCREW_L"] - hole_bottom, 0.3)
    return out


def neighbour_gaps(c: dict) -> dict:
    """Smallest gap to the X, Y and diagonal neighbour, each key anywhere in its slot's play."""
    W, D, R = COMPACT["W"], COMPACT["D"], COMPACT["R"]
    shape = rrect(0, 0, W, D, R, res=16)
    ks = c["KEY_X"]
    plays = []
    for dx, dy1, dy2 in itertools.product((-KEY_PLAY, 0, KEY_PLAY), repeat=3):
        ang = math.degrees(math.atan2(dy2 - dy1, 2 * ks))
        plays.append((dx, (dy1 + dy2) / 2, ang))

    def placed(cx, cy, p):
        return affinity.translate(affinity.rotate(shape, p[2], origin=(0, 0)), cx + p[0], cy + p[1])

    out = {}
    for name, (nx, ny) in {"X": (2 * c["PITCH_X"], 0), "Y": (0, c["PITCH_Y"]),
                           "diagonal": (2 * c["PITCH_X"], c["PITCH_Y"])}.items():
        a = [placed(0, 0, p) for p in plays]
        b = [placed(nx, ny, p) for p in plays]
        out[name] = min(sa.distance(sb) for sa in a for sb in b)
    return out


def draw(c: dict, out_deck: pathlib.Path, out_plan: pathlib.Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly

    INK, INK2, MUTED, SURF, BASE = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#dcdad4"
    OLD, NEW = "#2a78d6", "#eb6834"      # categorical slots 1 and 2: as in key_fit.png
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK})
    px, py = c["PITCH_X"], c["PITCH_Y"]
    W, D, F = COMPACT["W"], COMPACT["D"], c["FOOT"]

    def poly(ax, g, **kw):
        for gg in getattr(g, "geoms", [g]):
            ax.add_patch(MPoly(np.array(gg.exterior.coords), closed=True, **kw))
            for ring in gg.interiors:
                ax.add_patch(MPoly(np.array(ring.coords), closed=True, fc=SURF, ec="none", zorder=kw.get("zorder", 1)))

    # 1. The same window of the deck with today's stirrers, and with compact ones
    fig = plt.figure(figsize=(11.0, 7.7), dpi=110)
    fig.patch.set_facecolor(SURF)
    gs = fig.add_gridspec(1, 2, left=0.02, right=0.98, top=0.79, bottom=0.08, wspace=0.06)
    axes = [fig.add_subplot(gs[0, i]) for i in range(2)]
    win = (-9, 159, -9, 189)

    def deck(ax):
        ax.set_facecolor(SURF)
        poly(ax, box(win[0], win[2], win[1], win[3]), fc=BASE, ec="none", zorder=0)
        for i in range(-1, 8):
            for j in range(-1, 5):
                poly(ax, pill(12.5 + i * px, 22.5 + j * py, c["SLOT_W"], c["SLOT_C"]), fc="#f4f3ef", ec="#b9b6ae",
                     lw=0.6, zorder=1)
        ax.set_xlim(win[0], win[1])
        ax.set_ylim(win[2], win[3])
        ax.set_aspect("equal")
        ax.axis("off")

    def module(ax, cx, cy, w, d, colour, fill):
        poly(ax, rrect(cx, cy, w, d, c["FOOT_R"]), fc=fill, ec=colour, lw=1.6, zorder=3)
        for sx in (-1, 1):
            poly(ax, pill(cx + sx * c["KEY_X"], cy, c["KEY_W"], c["SLOT_C"]), fc="none", ec=colour, lw=0.8,
                 ls=(0, (2, 1.5)), zorder=4)
        ax.add_patch(plt.Circle((cx, cy), c["CUP_OD"] / 2, fc=SURF, ec=colour, lw=1.0, zorder=4))
        ax.add_patch(plt.Circle((cx, cy), c["VIAL_OD"] / 2, fc="none", ec=MUTED, lw=0.6, zorder=4))

    sc, sr = pitch(F, px, 2), pitch(F, py, 1)
    cc, cr = pitch(W, px, 2), pitch(D, py, 1)
    counts = []
    for ax, (w, d, step_c, step_r, colour, fill) in zip(axes, ((F, F, sc, sr, OLD, "#e6eefa"),
                                                             (W, D, cc, cr, NEW, "#fdebe2"))):
        deck(ax)
        n = 0
        for i in range(0, 5, step_c):          # i is the stirrer's first column of the window's 6
            for j in range(0, 4, step_r):
                module(ax, 25 + i * px, 22.5 + j * py, w, d, colour, fill)
                n += 1
        counts.append(n)
    axes[0].set_title(f"Today: {F:.0f} \u00d7 {F:.0f} mm \u2192 {counts[0]} stirrers in this window\n"
                      f"one per {sc} columns \u00d7 {sr} rows ({sc * px:.0f} \u00d7 {sr * py:.0f} mm). Any closer\n"
                      f"they overlap: {F - 2 * px:.0f} mm two columns over, {F - py:.0f} mm one row over",
                      fontsize=10.5, loc="left", color=INK)
    axes[1].set_title(f"Compact: {W:.0f} \u00d7 {D:.0f} mm \u2192 {counts[1]} stirrers in this window\n"
                      f"one per {cc} columns \u00d7 {cr} row ({cc * px:.0f} \u00d7 {cr * py:.0f} mm),\n"
                      f"{2 * px - W:.0f} mm apart both ways", fontsize=10.5, loc="left", color=INK)
    fig.suptitle("Stirrers side by side on the CubXL deck", x=0.02, y=0.975, ha="left", fontsize=13,
                 fontweight="bold", color=INK)
    fig.text(0.02, 0.915, "The fan (40 mm) and the cup (\u00d833.4) fit a 50 \u00d7 45 mm cell of the deck's slot grid; "
             "today's base doesn't.", fontsize=10.5, color=INK2)
    fig.text(0.02, 0.025, "The same 150 \u00d7 180 mm window of the deck (Cubware PandaDeck.step: slots in 18 columns "
             "25 mm apart, 10 rows 45 mm apart). Keys dashed, vial cups white.\nA stirrer's keys take two adjacent "
             "columns of one row, so stirrers can only sit whole columns and rows apart.", fontsize=8.8, color=INK2)
    fig.savefig(out_deck, facecolor=SURF)
    plt.close(fig)

    # 2. One compact stirrer in plan, to scale, with today's base behind it
    fig = plt.figure(figsize=(11.0, 7.0), dpi=110)
    fig.patch.set_facecolor(SURF)
    ax = fig.add_axes((0.0, 0.03, 0.66, 0.80))
    ax.set_facecolor(SURF)
    fp, wall = c["FAN_PITCH"] / 2, COMPACT["WALL"]
    hf = (c["FAN_W"] + FAN_TOL) / 2
    n0, n1 = COMPACT["NOTCH"]
    poly(ax, rrect(0, 0, F, F, c["FOOT_R"]), fc="none", ec=OLD, lw=1.2, ls=(0, (4, 2)), zorder=1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(plt.Circle((sx * c["POST"], sy * c["POST"]), POST_R, fc="#e6eefa", ec=OLD, lw=0.9, zorder=1))
            ax.add_patch(plt.Circle((sx * c["POST"], sy * c["POST"]), c["INSERT_HOLE"] / 2, fc=SURF, ec=OLD, lw=0.6,
                                    zorder=1))
    ring = rrect(0, 0, W, D, COMPACT["R"]).difference(rrect(0, 0, W - 2 * wall, D - 2 * wall, COMPACT["R"] - wall))
    poly(ax, ring.difference(box(n0, -D / 2 - 1, n1, -D / 2 + wall + 1)), fc=NEW, ec=NEW, lw=0.5, zorder=3)
    for b in (moved_in(BOARD), MOSFET, DIODE, moved_in(STOP)):     # under the fan
        poly(ax, rect(b), fc="#efede7", ec=INK2, lw=0.7, ls=(0, (1.5, 1.5)), zorder=2)
    x_in = -(W / 2 - wall)
    ax.add_patch(MPoly([(x_in, -9), (-hf, -9), (-hf, 9), (x_in, 9)], closed=True, fc="none", ec=NEW, hatch="////",
                       lw=0, zorder=4))
    for g, lw, ls in ((rrect(0, 0, c["FAN_W"], c["FAN_W"], FAN_CORNER_R), 1.3, "-"),
                      (rrect(0, 0, 2 * hf, 2 * hf, FAN_CORNER_R), 0.6, (0, (1, 1.5))),
                      (Point(0, 0).buffer(c["FAN_BORE"] / 2, resolution=64), 0.6, "-")):
        xy = np.array(g.exterior.coords)
        ax.plot(xy[:, 0], xy[:, 1], color=INK, lw=lw, ls=ls, zorder=5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(plt.Circle((sx * fp, sy * fp), COMPACT["CBORE_D"] / 2, fc=SURF, ec=NEW, lw=1.0, zorder=6))
            ax.add_patch(plt.Circle((sx * fp, sy * fp), HEAD_D / 2, fc="#c9c6be", ec=INK2, lw=0.8, zorder=6))
            ax.add_patch(plt.Circle((sx * fp, sy * fp), 1.3, fc=SURF, ec=INK2, lw=0.6, zorder=6))
    half = math.degrees(math.asin(c["CUP_SLOT"] / 2 / (c["CUP_OD"] / 2)))
    for k in range(4):                         # the cup's four fingers
        t = np.radians(np.linspace(45 + 90 * k - (45 - half), 45 + 90 * k + (45 - half), 40))
        ro, ri = c["CUP_OD"] / 2, c["CUP_R0"] - 0.1
        pts = np.vstack([np.c_[ro * np.cos(t), ro * np.sin(t)], np.c_[ri * np.cos(t[::-1]), ri * np.sin(t[::-1])]])
        ax.add_patch(MPoly(pts, closed=True, fc="#9fd3d4", ec="#1a9699", lw=0.9, zorder=7))
    ax.add_patch(plt.Circle((0, 0), c["RECESS_D"] / 2, fc="none", ec=MUTED, lw=0.7, ls=(0, (3, 2)), zorder=7))
    ax.add_patch(plt.Circle((0, 0), c["VIAL_OD"] / 2, fc="none", ec=MUTED, lw=0.7, zorder=7))
    poly(ax, rect(GROOVE), fc="none", ec=INK2, lw=0.7, ls=(0, (3, 2)), zorder=7)
    poly(ax, rect(HALL), fc=INK, ec=INK, lw=0.5, zorder=8)
    for sx in (-1, 1):
        poly(ax, pill(sx * c["KEY_X"], 0, c["KEY_W"], c["SLOT_C"]), fc="none", ec=INK2, lw=0.8, ls=(0, (2, 1.5)),
             zorder=8)
    xc = (n0 + n1) / 2                         # the cable: under the fan to the -Y notch, then out
    ax.plot([xc, xc], [BOARD[1], -D / 2 + wall], color="#7c7a74", lw=2.0, ls=(0, (1.2, 1.2)), zorder=4)
    ax.plot([xc, xc], [-D / 2 + wall, -D / 2 - 7], color=INK, lw=3.4, solid_capstyle="butt", zorder=9)
    ax.plot([xc, xc], [-D / 2 + wall, -D / 2 - 7], color="#7c7a74", lw=1.8, solid_capstyle="butt", zorder=9)
    ax.text(0, D / 2 + 0.9, f"{W:.0f}", ha="center", va="bottom", fontsize=10, color=NEW, fontweight="bold")
    ax.text(W / 2 + 0.9, 0, f"{D:.0f}", ha="left", va="center", fontsize=10, color=NEW, fontweight="bold",
            rotation=90)
    ax.text(F / 2, -F / 2 - 1.0, f"today: {F:.0f} \u00d7 {F:.0f}", ha="right", va="top", fontsize=9, color=OLD)

    def note(xy, text, xytext):
        ax.annotate(text, xy, xytext, fontsize=8.8, color=INK, ha="left", va="center", zorder=10,
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6, shrinkA=2, shrinkB=1))

    note((c["POST"] + 2.0, c["POST"] + 2.0), "today's corner posts and\nM3 \u00d7 12s set the 56 mm", (31.0, 34.0))
    note((c["FAN_W"] / 2, 13.0), "fan, 40 \u00b1 0.5", (31.0, 21.0))
    note((15.0, 7.5), "cup \u00d833.4, as in\nthe 9-vial holder", (31.0, 10.0))
    note((c["KEY_X"] + c["KEY_W"] / 2, -6.0), "deck keys,\nunder the floor", (31.0, -3.0))
    note((fp + 1.8, -fp - 1.8), "4 \u00d7 M3 \u00d7 20 through\nflange and fan", (31.0, -18.0))
    note((-hf - 1.3, 7.0), "Hall and fan leads\ndown a 2.6 mm gap", (-51.0, 30.0))
    note((-12.0, 1.5), "Hall sensor", (-51.0, 14.0))
    note((-18.0, -6.0), "junction board,\nunder the fan", (-51.0, -4.0))
    note((xc - 0.8, -D / 2 - 4.5), "cable out of the\n\u2212Y wall", (-51.0, -32.0))
    ax.set_xlim(-52, 58)
    ax.set_ylim(-40, 40)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.suptitle("A compact stirrer from above, to scale (mm)", x=0.02, y=0.975, ha="left", fontsize=13,
                 fontweight="bold", color=INK)
    fig.text(0.02, 0.915, f"{W:.0f} \u00d7 {D:.0f} mm in orange; today's {F:.0f} \u00d7 {F:.0f} mm base in blue, "
             "dashed. Under the fan: dotted.", fontsize=10.5, color=INK2)
    changes = [
        ("What changes", True),
        (f"\u2022 Base and holder flange: {F:.0f} \u00d7 {F:.0f} \u2192 {W:.0f} \u00d7 {D:.0f} mm", False),
        (f"\u2022 Base walls: {(F - c['CAV']) / 2:.1f} \u2192 {wall:.1f} mm (4 perimeters)", False),
        ("\u2022 Corner posts, their 4 inserts and\n   the 4 \u00d7 M3 \u00d7 12: gone", False),
        ("\u2022 Fan screws: M3 \u00d7 16 \u2192 M3 \u00d7 20, through\n   the flange and the fan into the same\n"
         "   post inserts, heads in 3 mm counterbores.\n   The M3 kit on the BOM has 20 mm", False),
        ("\u2022 The flange rests on the fan's corners, on\n   0.5 mm pads, so the gap over the rotor\n"
         "   stays 0.5 mm, as today", False),
        ("\u2022 The junction board's stop moves 0.5 mm\n   toward +X, to clear the nearer wall", False),
        ("\u2022 Cable notch: \u2212X wall \u2192 \u2212Y wall, so a\n   2-row block can face its cables out", False),
        ("Unchanged", True),
        ("Fan, magnets, carrier, the cup, the Hall\nsensor and its groove, the keys, the parts\n"
         "under the fan, every height: the vial bottom\nstays 25 mm above the deck", False),
    ]
    y = 0.83
    for text, head in changes:
        y -= 0.02 if text == "Unchanged" else 0
        fig.text(0.665, y, text, fontsize=10 if head else 9.2, color=INK if head else INK2, va="top",
                 fontweight="bold" if head else "normal", linespacing=1.3)
        y -= 0.0265 * (text.count("\n") + 1) + (0.012 if head else 0.02)
    fig.savefig(out_plan, facecolor=SURF)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--deck-step", type=pathlib.Path, help="Cubware PandaDeck.step, to re-read the slot grid")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    c = fs_constants(FS)
    px, py = c["PITCH_X"], c["PITCH_Y"]
    print(f"CubXL+ deck: {DECK_W:.0f} x {DECK_D:.0f} mm, {N_COLS} slot columns {px:.0f} mm apart from X = {COL0}, "
          f"{N_ROWS} rows {py:.0f} mm apart")
    if args.deck_step:
        cols, rows = deck_grid_from_step(args.deck_step)
        dc, dr = np.diff(cols), np.diff(rows)
        print(f"  re-read from {args.deck_step.name}: {len(cols)} columns, X {cols[0]}..{cols[-1]}, pitch "
              f"{dc.min():.3f}-{dc.max():.3f}; {len(rows)} rows, pitch {abs(dr).min():.3f}-{abs(dr).max():.3f}")
        assert len(cols) == N_COLS and len(rows) == N_ROWS and abs(cols[0] - COL0) < 1e-6
    print("  A stirrer's two keys take adjacent columns of one row; the vial sits midway between them.\n")

    try:
        import trimesh

        print("Printed parts today (STL bounds, mm):")
        for name in ("base", "vial_holder"):
            lo, hi = trimesh.load(HERE / "stl" / f"{name}.stl").bounds
            print(f"  {name:12s} {hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} x {hi[2] - lo[2]:.1f}")
        print()
    except ImportError:
        pass

    print("What sets today's footprint, half-widths from the centre (mm):      X       Y")
    rows = [("base walls and holder flange (FOOT / 2)", c["FOOT"] / 2, c["FOOT"] / 2),
            ("corner posts for the holder's M3 x 12s (POST + boss)", c["POST"] + POST_R, c["POST"] + POST_R),
            ("cavity inside the walls (CAV / 2)", c["CAV"] / 2, c["CAV"] / 2),
            ("Hall-lead groove end (makeHolder)", -GROOVE[0], GROOVE[3]),
            ("electronics under the fan (board to MOSFET tab; diode)", max(-BOARD[0], MOSFET[2]), -DIODE[1]),
            ("fan at +0.5 tolerance", c["FAN_W"] / 2 + FAN_TOL / 2, c["FAN_W"] / 2 + FAN_TOL / 2),
            ("fan posts (FAN_PITCH / 2 + boss)", c["FAN_PITCH"] / 2 + POST_R, c["FAN_PITCH"] / 2 + POST_R),
            ("keys (KEY_X + KEY_W / 2; (SLOT_C + KEY_W) / 2)", c["KEY_X"] + c["KEY_W"] / 2, (c["SLOT_C"] + c["KEY_W"]) / 2),
            ("vial cup (CUP_OD / 2)", c["CUP_OD"] / 2, c["CUP_OD"] / 2)]
    for what, hx, hy in rows:
        print(f"  {what:62s} {hx:6.2f}  {hy:6.2f}")

    print("\nPitch on the grid, leaving a 1 mm gap:")
    for name, w, d in (("today", c["FOOT"], c["FOOT"]), ("compact", COMPACT["W"], COMPACT["D"])):
        sc, sr = pitch(w, px, 2), pitch(d, py, 1)
        print(f"  {name:8s} {w:.0f} x {d:.0f} mm: every {sc} columns x every {sr} row(s) = one per "
              f"{sc * px:.0f} x {sr * py:.0f} mm; {per_deck(sc, sr)} on the whole plate if nothing else were on it")

    print("\nCompact layout, checked in plan (and the one screw that changes):")
    bad = 0
    for what, value, limit, ok in check(c):
        bad += not ok
        print(f"  {'ok ' if ok else 'BAD'} {what:66s} {value:7.2f}   (need >= {limit:.2f})")
    gaps = neighbour_gaps(c)
    print("\nGap to the neighbour with every key anywhere in its slot's 0.1 mm play (worst case):")
    for k, v in gaps.items():
        print(f"  {k:9s} {v:.2f} mm")
    print(f"\n{bad} check(s) failed")
    if not args.no_plot:
        draw(c, HERE / "img" / "deck_tiling.png", HERE / "img" / "deck_tiling_plan.png")
        print("wrote img/deck_tiling.png, img/deck_tiling_plan.png")


if __name__ == "__main__":
    main()
