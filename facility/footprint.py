"""If we were to build a facility like this: the #318 lab floor and the 50 ft array drawn into a typical warehouse.

    python3 facility/footprint.py        # -> facility/out/footprint.png, facility/out/footprint.json

Two panels:

- **Plan.** A 250 x 160 ft warehouse (40,000 ft2, the top of the range from the 2026-11-12 conversation), with its west
  half (20,000 ft2, the bottom of the range) laid out: the lab floor of PR #318 exactly as ``setup_lab.FLOOR_PLAN``
  and ``r8_scale.FLOOR_PLACEMENT`` place it, the 50 ft array of ``scale.py``, and the support rooms a building would
  need. Everything outside the #318 floor and the array is an illustrative allocation, not a design.
- **Section.** The array against common warehouse clear heights, and three ways to fit it: a pit, a high bay over it,
  or shorter units.

Sources for the figures used here (all pinned commits on byu-vcl PR branches, as of 2026-11-12):

- ``vertical-lab/scale.py`` and ``vlm.py`` @ 03801d8: the 15.15 m Shuttle, eight units in two rows of four across an
  1100 mm aisle, unit pitch 2980 mm, module 2780 x 3074 mm with 25 mm cladding, the slot rule ``slots()``.
- ``vertical-lab/setup_lab.py`` @ PR #318's head: ``FLOOR_PLAN`` (x of each station, its row); ``warehouse.py``: the
  row fronts (y = -1562 mm north, -6238 mm south), the 3.0 m aisle (-2400 to -5400 mm), the aisle's ends (+-10.2 m).
- ``vertical-lab/r8_scale.py``: where the EOS M 400-4 and the Meltio cell stand (their plan extents, in its comments).
- Machine sizes: ``lab_models/equipment.py`` (rePowder 1000 x 800, Aconity MIDI 2450 x 1500), ``instruments.py``
  (Instron 68FM-100 1140 x 786, 68SC-2 460 x 615, FANUC wire EDM 2120 x 2540, glovebox 2005 x 834),
  ``warehouse.RESERVED`` (DED 3000 x 2400, packaging 2400 x 1500), ``setup_lab.SIEVE_BENCH`` (1065 x 600), Labconco
  hood 63.5 in wide (``LABCONCO``; 900 mm deep assumed here).

NFPA 13's 18 in between sprinkler deflectors and the top of storage is used as the clearance over a unit. Kardex's
own installation clearances will differ; treat the clear heights below as a screen, not a specification.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
MM_FT = 304.8

# --------------------------------------------------------------------------------------------- the array (scale.py)
UNIT_W, UNIT_D, SKIN = 2780.0, 3074.0, 25.0
PITCH_X = UNIT_W + 2 * SKIN + 150.0                       # 2980 mm between unit centres along a row
AISLE, LIP = 1100.0, 50.0
Y_UNIT = AISLE / 2 + LIP + SKIN + UNIT_D / 2              # a unit's centre from the aisle's centre line
ARRAY_D = 2 * (Y_UNIT + UNIT_D / 2 + SKIN)                # 7448 mm, both rows and the aisle
H_TALL = 15150.0                                          # the tallest Shuttle under 50 ft, 100 mm steps
H_LAB = 3950.0                                            # the lab floor's Shuttle (under 13 ft, #53)
N_UNITS = 8
SPRINKLER = 18 * 25.4                                     # NFPA 13: 18 in under the deflectors

# scale.py's slot rule (vlm.py @ 03801d8): both columns from the bottom, each slot its load's height + ~50 mm on the
# 25 mm pitch; the front column loses the opening's height
Z_SILL, Z_OPEN_TOP, T_FLOOR, PITCH = 833.0, 1700.0, 3.0, 25.0
TYPES = ("A", "D", "C", "E", "F", "A", "E", "D", "C", "F")
KIND_H = {"A": 662.0, "C": 488.0, "D": 626.0, "E": 505.0, "F": 482.5}


def trays_per_unit(H: float) -> int:
    top = H - 260.0 - 10.0
    zones = [[(300.0, top)], [(300.0, Z_SILL - 40.0), (Z_OPEN_TOP + 120.0, top)]]
    n = k = 0
    for zs in zones:
        for z0, z1 in zs:
            z = z0
            while True:
                kind = TYPES[k % len(TYPES)]
                h = KIND_H[kind]
                if z + T_FLOOR + h > z1:
                    if z1 - z < 600:
                        break
                    kind, h = "F", KIND_H["F"]
                    if z + T_FLOOR + h > z1:
                        break
                n += 1
                k += 1
                z += math.ceil((h + 50.0) / PITCH) * PITCH
    return n


def tallest_under(clear_ft: float) -> float:
    """The tallest Shuttle (100 mm steps from 2550 mm) whose top stays SPRINKLER under a clear height."""
    return math.floor((clear_ft * MM_FT - SPRINKLER) / 100.0) * 100.0


def height_table() -> dict:
    per_tall = trays_per_unit(H_TALL)
    total = N_UNITS * per_tall
    rows = []
    for clear in (24, 28, 32, 36, 40):
        h = tallest_under(clear)
        n = trays_per_unit(h)
        units = math.ceil(total / n)
        per_row = math.ceil(units / 2)
        rows.append(dict(clear_ft=clear, unit_mm=h, unit_ft=round(h / MM_FT, 1), trays_per_unit=n,
                         units_for_same_trays=units, array_m=(round(per_row * PITCH_X / 1000, 1),
                                                              round(ARRAY_D / 1000, 1)),
                         array_ft2=round(per_row * PITCH_X * ARRAY_D / MM_FT ** 2)))
    need_ft = (H_TALL + SPRINKLER) / MM_FT
    return dict(tall_unit_mm=H_TALL, trays_per_tall_unit=per_tall, trays_total=total,
                clear_needed_ft=round(need_ft, 1),
                pit_under_40ft_m=round((H_TALL + SPRINKLER - 40 * MM_FT) / 1000, 2),
                array_m=(round(N_UNITS / 2 * PITCH_X / 1000, 2), round(ARRAY_D / 1000, 2)),
                array_ft2=round(N_UNITS / 2 * PITCH_X * ARRAY_D / MM_FT ** 2), shorter_units=rows)


# --------------------------------------------------------------------------------------------- the #318 floor
Y_FACE_N, Y_FACE_S = -1562.0, -6238.0
X2 = UNIT_W + 2 * SKIN + 800.0                            # Shuttle 2's centre, 3630 mm right of Shuttle 1
# key: (label, x centre, row, width along x, depth away from the aisle, setback)
MACHINES = [
    ("glovebox", -7300.0, "N", 834.0, 2005.0, 400.0),     # turned -90 degrees: its 2005 mm runs north
    ("rePowder", -3775.0, "N*", 1000.0, 800.0, 0.0),      # REPOWDER_AT; stands 337 mm proud of the row
    ("sieving", -1982.5, "N", 1065.0, 600.0, 0.0),
    ("Shuttle 1", 0.0, "N", UNIT_W + 2 * SKIN, UNIT_D + 2 * SKIN, 0.0),
    ("Shuttle 2", X2, "N", UNIT_W + 2 * SKIN, UNIT_D + 2 * SKIN, 0.0),
    ("MIDI", 6950.0, "N", 2450.0, 1500.0, 0.0),
    ("packaging", 10050.0, "N", 2400.0, 1500.0, 0.0),
    ("Instron\n100 kN", -6400.0, "S", 1140.0, 786.0, 0.0),
    ("2 kN", -4300.0, "S", 460.0, 615.0, 0.0),
    ("hood", 1500.0, "S", 1613.0, 900.0, 0.0),
    ("DED", 3900.0, "S", 3000.0, 2400.0, 0.0),
    ("wire EDM", 6600.0, "S", 2120.0, 2540.0, 0.0),
]
SCALEUP = [("EOS M 400-4", (-11541.0, -7359.0, -11507.0, -9763.0)),
           ("Meltio cell", (7425.0, 11779.0, -12415.0, -8985.0))]
AISLE_318 = (-10200.0, 10200.0, -5400.0, -2400.0)


def machine_rects() -> list[tuple[str, tuple[float, float, float, float]]]:
    out = []
    for name, x, row, w, d, setback in MACHINES:
        if row == "N*":                                   # the rePowder: 337 mm south of the north fronts
            y0 = Y_FACE_N - 337.0
            out.append((name, (x - w / 2, x + w / 2, y0, y0 + d)))
        elif row == "N":
            y0 = Y_FACE_N + setback
            out.append((name, (x - w / 2, x + w / 2, y0, y0 + d)))
        else:
            out.append((name, (x - w / 2, x + w / 2, Y_FACE_S - d, Y_FACE_S)))
    return out + SCALEUP


# --------------------------------------------------------------------------------------------- colours
SURFACE = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"      # the reference palette's slots 1-3 (all-pairs validated)
GRID = "#d9d8d3"


def tint(hex_: str, a: float) -> tuple:
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    s = tuple(int(SURFACE[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return tuple(a * c + (1 - a) * w for c, w in zip((r, g, b), s))


def box(ax, x0, y0, w, h, fc, ec, lw=0.8, ls="-", hatch=None, z=2):
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, hatch=hatch,
                           zorder=z))


def plan(ax, tab: dict) -> None:
    BW, BD = 250.0, 160.0
    ax.set_facecolor(SURFACE)
    # yard outside the west wall: gas and the transformer
    box(ax, -40, 104, 36, 56, tint(INK2, 0.06), INK2, 0.6, "--", hatch="////", z=1)
    ax.text(-22, 132, "gas yard:\nbulk Ar, N$_2$,\ncylinders", ha="center", va="center", fontsize=6.0, color=INK2,
            zorder=5, bbox=dict(fc=SURFACE, ec="none", pad=0.6))
    box(ax, -30, 60, 26, 20, tint(INK2, 0.06), INK2, 0.6, "--", hatch="////", z=1)
    ax.text(-17, 70, "trans-\nformer", ha="center", va="center", fontsize=6.0, color=INK2, zorder=5,
            bbox=dict(fc=SURFACE, ec="none", pad=0.4))
    # column grid (typical, illustrative)
    for x in range(0, 251, 50):
        ax.plot([x, x], [0, BD], color=GRID, lw=0.5, ls=(0, (2, 3)), zorder=0.5)
    for y in (0, 53, 106, 160):
        ax.plot([0, BW], [y, y], color=GRID, lw=0.5, ls=(0, (2, 3)), zorder=0.5)
    # phase 2: room to grow
    box(ax, 125, 0, 125, BD, "none", MUTED, 0.9, (0, (5, 3)), z=1)
    ax.text(187.5, 92, "second 20,000 ft$^2$\n\nroom to grow to ten alloys a day\n(PR #332, rung R11: 3 rePowders,\n"
            "4 MIDIs, five floor cells with\nfixed arms), or a second array", ha="center", va="center",
            fontsize=7.0, color=INK2, linespacing=1.25)
    # support rooms (west half)
    sup = [("mechanical,\nelectrical:\nswitchgear,\nchiller, air,\nN$_2$ gen., UPS", 0, 106, 34, 54),
           ("powder room\nNFPA 484; a candidate\nH-2/H-3 control area,\nrated walls", 72, 53, 41, 43),
           ("offices, control room,\nvisitor gallery", 0, 0, 45, 44),
           ("workshop", 45, 0, 30, 44),
           ("receiving and\nstaging", 75, 0, 50, 44)]
    for label, x0, y0, w, h in sup:
        box(ax, x0, y0, w, h, tint(AQUA, 0.14), AQUA, 0.9)
        ax.text(x0 + w / 2, y0 + h / 2, label, ha="center", va="center", fontsize=6.4, color=INK, linespacing=1.15,
                zorder=6)
    # dock doors on the south wall
    for x in (80, 92, 104, 116):
        ax.add_patch(Rectangle((x - 4.5, -2.2), 9, 2.2, facecolor=INK2, edgecolor="none", zorder=7))
    ax.text(98, -6.5, "dock doors (9 x 10 ft)", ha="center", va="top", fontsize=6.2, color=INK2)
    # the #318 floor: Shuttle 1 at (x0, y0) in feet
    ox, oy = 76.0, 154.0
    f = lambda v: v / MM_FT  # noqa: E731
    ax0, ax1, ay0, ay1 = AISLE_318
    box(ax, ox + f(ax0), oy + f(ay0), f(ax1 - ax0), f(ay1 - ay0), tint(BLUE, 0.05), tint(BLUE, 0.6), 0.6,
        (0, (3, 2)), z=2)
    ax.text(ox + f(ax0) + 1.5, oy + f((ay0 + ay1) / 2), "3 m aisle, two MiR250 + UR10e", ha="left", va="center",
            fontsize=5.6, color=INK2, zorder=6)
    lab = {"Shuttle 1", "Shuttle 2", "MIDI", "EOS M 400-4", "Meltio cell"}
    for name, (x0, x1, y0, y1) in machine_rects():
        box(ax, ox + f(x0), oy + f(y0), f(x1 - x0), f(y1 - y0), tint(BLUE, 0.30), BLUE, 0.8, z=3)
        if name in lab:
            short = {"Shuttle 1": "VLM", "Shuttle 2": "VLM", "EOS M 400-4": "EOS", "Meltio cell": "Meltio"}.get(
                name, name)
            ax.text(ox + f((x0 + x1) / 2), oy + f((y0 + y1) / 2), short, ha="center", va="center",
                    fontsize=5.4 if len(short) < 9 else 5.0, color=INK, zorder=6)
    ax.text(ox, oy + f(-12415.0) - 1.5, "PR #318's lab floor as setup_lab places it:\ntwo 3.95 m Shuttles, the "
            "floor machines,\nround 8's EOS M 400-4 and Meltio cell", ha="center", va="top", fontsize=6.3,
            color=INK, zorder=8, linespacing=1.15)
    # the array (scale.py), plan
    aw, ad = f(N_UNITS / 2 * PITCH_X), f(ARRAY_D)
    axx, ayy = 20.0, 62.0
    box(ax, axx - 4, ayy - 4, aw + 8, ad + 8, "none", ORANGE, 0.7, (0, (4, 2)), z=2)
    for row in (0, 1):
        for i in range(4):
            cx = axx + f((i + 0.5) * PITCH_X)
            cy = ayy + ad / 2 + (1 if row else -1) * f(Y_UNIT)
            w, d = f(UNIT_W + 2 * SKIN), f(UNIT_D + 2 * SKIN)
            box(ax, cx - w / 2, cy - d / 2, w, d, tint(ORANGE, 0.35), ORANGE, 0.8, z=3)
    ax.plot([axx, axx + aw], [ayy + ad / 2] * 2, color=INK2, lw=0.8, zorder=4)
    ax.text(axx + aw / 2, ayy - 5.0, f"the 50 ft array: 8 Shuttles x 15.15 m,\n"
            f"{tab['array_m'][0]:.1f} x {tab['array_m'][1]:.1f} m ({tab['array_ft2']:,} ft$^2$),\nin a high bay or "
            f"a pit", ha="center", va="top", fontsize=6.3, color=INK, zorder=6, linespacing=1.15)
    # walls
    ax.add_patch(Rectangle((0, 0), BW, BD, facecolor="none", edgecolor=INK, linewidth=1.6, zorder=9))
    ax.plot([125, 125], [0, BD], color=INK, lw=0.0)
    # dimensions
    ax.annotate("", xy=(0, BD + 7), xytext=(BW, BD + 7), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.7))
    ax.text(BW / 2, BD + 8.5, "250 ft", ha="center", va="bottom", fontsize=7, color=INK2)
    ax.annotate("", xy=(0, BD + 2.5), xytext=(125, BD + 2.5), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.6))
    ax.text(62.5, BD + 3.4, "first 20,000 ft$^2$ (125 x 160 ft)", ha="center", va="bottom", fontsize=6.4,
            color=INK2)
    ax.annotate("", xy=(BW + 6, 0), xytext=(BW + 6, BD), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.7))
    ax.text(BW + 8, BD / 2, "160 ft", ha="left", va="center", fontsize=7, color=INK2, rotation=90)
    ax.set_xlim(-43, BW + 14)
    ax.set_ylim(-14, BD + 18)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Plan: a 40,000 ft$^2$ warehouse (250 x 160 ft), its first half laid out", fontsize=9.5,
                 color=INK, loc="left", pad=4)


def section(ax, tab: dict) -> None:
    ax.set_facecolor(SURFACE)
    ft = lambda mm: mm / MM_FT  # noqa: E731
    H = ft(H_TALL)
    d = ft(ARRAY_D)
    need = tab["clear_needed_ft"]
    pit = ft(tab["pit_under_40ft_m"] * 1000)
    # common clear heights
    for c in (24, 28, 32, 36, 40):
        ax.plot([-6, 154], [c, c], color=GRID if c != 40 else MUTED, lw=0.7, ls=(0, (2, 3)), zorder=0.5)
        ax.text(-7, c, f"{c} ft", ha="right", va="center", fontsize=6.6, color=INK2)
    ax.plot([-6, 154], [need, need], color=ORANGE, lw=0.8, ls=(0, (4, 2)), zorder=0.6)
    ax.text(-7, need, f"{need:.0f} ft", ha="right", va="center", fontsize=6.6, color=INK)
    ax.text(154, need - 0.9, f"the 15.15 m array needs\n{need:.1f} ft clear (18 in under sprinklers)",
            ha="right", va="top", fontsize=6.4, color=INK, linespacing=1.2)
    # ground
    ax.plot([-6, 154], [0, 0], color=INK, lw=1.2, zorder=3)

    def building(x0, w, clear, high=None):
        xs = [x0, x0, x0 + w, x0 + w]
        ys = [0, clear + 2, clear + 2, 0]
        if high:
            hx0, hx1, hz = high
            xs = [x0, x0, hx0, hx0, hx1, hx1, x0 + w, x0 + w]
            ys = [0, clear + 2, clear + 2, hz + 2, hz + 2, clear + 2, clear + 2, 0]
        ax.plot(xs, ys, color=INK, lw=1.3, zorder=4)

    def unit_side(x, z0, h, col=ORANGE, a=0.35):
        box(ax, x, z0, ft(UNIT_D + 2 * SKIN), h, tint(col, a), col, 0.8, z=5)

    def array_side(x, z0, h):
        unit_side(x, z0, h)
        unit_side(x + d - ft(UNIT_D + 2 * SKIN), z0, h)

    # a) pit under a 40 ft building
    x = 2.0
    building(x, 38, 40)
    box(ax, x + 4, -pit - 1.0, d + 2, pit + 1.0, tint(INK2, 0.08), INK2, 0.8, z=2)
    array_side(x + 5, -pit, H)
    ax.text(x + 19, -pit - 2.5, f"a) an {pit:.0f} ft ({tab['pit_under_40ft_m']:.1f} m) pit\nunder 40 ft clear",
            ha="center", va="top", fontsize=6.6, color=INK)
    # b) a high bay over the array
    x = 50.0
    building(x, 46, 40, high=(x + 6, x + 6 + d + 8, need))
    array_side(x + 10, 0, H)
    ax.text(x + 23, -2.5, f"b) a high bay over the array,\n{math.ceil(need)}+ ft clear; the rest at 40 ft",
            ha="center", va="top", fontsize=6.6, color=INK)
    # c) shorter units under 40 ft
    row40 = next(r for r in tab["shorter_units"] if r["clear_ft"] == 40)
    x = 105.0
    building(x, 40, 40)
    array_side(x + 6, 0, ft(row40["unit_mm"]))
    ax.text(x + 20, -2.5, f"c) {row40['unit_mm'] / 1000:.1f} m units under 40 ft:\n"
            f"{row40['units_for_same_trays']} units for the same {tab['trays_total']} trays",
            ha="center", va="top", fontsize=6.6, color=INK)
    # for scale: the lab Shuttle and a person
    box(ax, x + 34.0, 0, ft(UNIT_D + 2 * SKIN) / 2.2, ft(H_LAB), tint(BLUE, 0.30), BLUE, 0.8, z=5)
    ax.text(x + 36.3, ft(H_LAB) + 0.8, "3.95 m\nlab VLM", ha="center", va="bottom", fontsize=5.8, color=INK,
            linespacing=1.1, zorder=8, bbox=dict(fc=SURFACE, ec="none", pad=0.3))
    px = x + 2.5
    ax.add_patch(FancyBboxPatch((px - 0.6, 0), 1.2, 4.6, boxstyle="round,pad=0.1,rounding_size=0.5",
                                facecolor=INK2, edgecolor="none", zorder=6))
    ax.add_patch(plt.Circle((px, 5.3), 0.6, color=INK2, zorder=6))
    ax.set_xlim(-14, 156)
    ax.set_ylim(-pit - 9, need + 7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Section: the 50 ft array against warehouse clear heights", fontsize=9.5, color=INK, loc="left",
                 pad=4)


def legend(fig) -> None:
    items = [(tint(BLUE, 0.30), BLUE, "PR #318's lab floor (setup_lab.FLOOR_PLAN, r8_scale)"),
             (tint(ORANGE, 0.35), ORANGE, "the 50 ft array (scale.py): Kardex Shuttle XP 500, 15.15 m"),
             (tint(AQUA, 0.14), AQUA, "support rooms: an illustrative allocation, not a design")]
    handles = [Rectangle((0, 0), 1, 1, facecolor=fc, edgecolor=ec, linewidth=0.8) for fc, ec, _ in items]
    fig.legend(handles, [t for *_, t in items], loc="lower left", bbox_to_anchor=(0.012, 0.0), ncol=3,
               frameon=False, fontsize=7.2, handlelength=1.4, labelcolor=INK2)


def main() -> dict:
    OUT.mkdir(exist_ok=True)
    tab = height_table()
    fig = plt.figure(figsize=(13.5, 5.6), dpi=200, facecolor=SURFACE)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.42, 1.0], left=0.005, right=0.995, top=0.85, bottom=0.08,
                          wspace=0.03)
    plan(fig.add_subplot(gs[0]), tab)
    section(fig.add_subplot(gs[1]), tab)
    fig.suptitle("If we were to build a facility like this: the #303 / PR #318 lab in a typical warehouse",
                 x=0.012, ha="left", fontsize=11.5, color=INK, y=0.975)
    fig.text(0.012, 0.925, "To scale. The #318 floor and the array are placed from the repo's own figures; the "
             "rooms, docks and yard are one way the rest of the floor could go. Floor area is easy; height is the "
             "binding constraint.\nDashed lines in the section: common warehouse clear heights. Clearance over a "
             "unit is NFPA 13's 18 in under sprinklers; Kardex's own figure may differ.", fontsize=7.4,
             color=INK2, ha="left", va="top", linespacing=1.3)
    legend(fig)
    path = OUT / "footprint.png"
    fig.savefig(path, facecolor=SURFACE)
    rects = machine_rects()
    xs = [v for _, r in rects for v in r[:2]]
    ys = [v for _, r in rects for v in r[2:]]
    tab["floor_318"] = dict(x_m=(round(min(xs) / 1000, 2), round(max(xs) / 1000, 2)),
                            y_m=(round(min(ys) / 1000, 2), round(max(ys) / 1000, 2)),
                            bbox_ft2=round((max(xs) - min(xs)) * (max(ys) - min(ys)) / MM_FT ** 2))
    (OUT / "footprint.json").write_text(json.dumps(tab, indent=1) + "\n")
    return tab


if __name__ == "__main__":
    t = main()
    print(json.dumps(t, indent=1))
