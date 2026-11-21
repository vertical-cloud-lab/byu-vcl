#!/usr/bin/env python3
"""Mock-up: the stir module's fan under the CubXL deck, so the 9 mm deck is the spacer, in a version
that sits side by side with its neighbours.

Asked for by @benwhitney5463 on PR #348: the under-deck idea on 2026-11-19, side by side on 2026-11-20
("There is nothing under the deck right now, and there [is] plenty of clearance for the stir module").
A MOCK-UP to discuss, not checked for print. The first version (commit c549ed6) reached into the far
half of each slot, so it was 72 mm long and needed two rows (90 mm) in Y.

z = 0 is the deck's top face, the vial's axis is x = y = 0, mm. The vial sits between four deck slots
(25 mm columns, 45 mm rows), so it stands on solid polycarbonate: the nearest slot edge is 14.5 mm
from its axis, against its 13.75 mm radius.

Side by side: every part of a module stays inside a 49 x 44 mm cell round its vial, and uses only the
half of each slot nearest its vial (|y| 10 to 22). A neighbour 45 mm away in Y uses the other half of
the same slots; one 50 mm away in X uses other slots. So modules sit 50 mm apart in X (two slot
columns) and 45 mm apart in Y (one row), the closest a 40 mm fan allows on this grid.

  above the deck  collar: the 9-vial holder's cup (ring and four spring fingers) with NO floor, on two
                  44 mm bars that carry four half-length keys, 3 mm into the near half of each slot
  the deck        9 mm (Ben's measurement); the vial stands on it
  under the deck  frame: today's compact holder's flange (z 20 -> 23.83 in the stirrer's own frame,
                  49 x 44 mm) with the cup and floor gone, so its top face is against the deck's
                  underside; 0.5 mm pads on the fan's four corners (as the compact build's washers);
                  two half-length bosses, 5 mm up into the near halves of two diagonal slots
                  today's compact base, fan, carrier, magnets, Hall sensor and junction board,
                  unchanged, on two of the four fan screws (M3 x 16, diagonal)
  clamp           two M3 x 12 from the top, through the collar's keys, into heat-set inserts in the
                  frame's bosses (the other diagonal): they sandwich the deck, and keys and bosses in
                  the same slots line the magnets up with the vial

Why two and two: the fan's screws are at (+-16, +-16), under the near half of every slot, and a
screw at x = 16 can't pass a slot whose edge is at x = 17.5. So a fan screw's head blocks a boss
in its half-slot. Two fan screws on one diagonal leave the other diagonal's half-slots free for the
clamp.

    python under-deck/build_under_deck.py           # from hardware/vial-stirrer-cubxl: stl/under-deck/, step/under-deck/
    python under-deck/build_under_deck.py --check   # also the side-by-side clash check (side_by_side_check_output.txt)
"""
from __future__ import annotations

import itertools
import math
import pathlib
import sys

import cadquery as cq

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "compact"))
from build_compact import C, box, cyl, cone, rbox, make_base  # noqa: E402

DECK_T = 9.0                       # Ben, 2026-11-19 (Cubware's STEP says 10)
SLOT_W, SLOT_L = 10.0, 25.0        # deck slots, long axis along Y
COL, ROW = 25.0, 45.0              # slot pitch
PITCH_X, PITCH_Y = 2 * COL, ROW    # side by side: two columns in X, one row in Y
CELL_W, CELL_D = 49.0, 44.0        # frame, base and collar stay inside this (1 mm between neighbours)
KEY_W = 9.8                        # Cubware key width: 0.1 mm a side
END_C = ROW / 2 - SLOT_L / 2 + SLOT_W / 2    # 15: centre of a slot's near end circle, |y|
HALF_END = CELL_D / 2              # 22: keys and bosses stop here; the slot's middle is at 22.5
SLOTS = [(sx * COL / 2, sy * ROW / 2) for sx in (-1, 1) for sy in (-1, 1)]   # the four round the vial
CLAMP = [(COL / 2, 16.0), (-COL / 2, -16.0)]             # clamp screws, one diagonal
FAN_SCREWS = [(16.0, -16.0), (-16.0, 16.0)]              # fan screws, the other diagonal
KEY_D = 3.0                        # collar keys: 3 mm down into the slot
BOSS_H = 5.0                       # frame bosses: 5 mm up into the slot (1 mm short of the keys)
BAR_W, BAR_T = 12.0, 3.0           # the collar's bars, over the slot columns
PAD_T = 0.5                        # pads on the fan's corners (the compact build uses 0.5 mm washers)
CBORE_D, CBORE_DEPTH = 6.5, 3.2    # fan-screw heads (M3, 5.5 x 3) sit 0.2 mm below the deck's underside
FAN_SCREW_L, CLAMP_L = 16.0, 12.0
RING = C["CUP_RING"]               # 2.0: full ring above the floor, then the fingers
CUP_TOP = C["Z_TOP"] - C["Z_VIAL"] # 17.0: finger tips above the vial's bottom
# The stirrer's own frame (z 0 on the deck's top face when it sits on the deck) to this one: its
# holder's recess ceiling, z 23.83, goes to the deck's underside.
DZ = -DECK_T - C["Z_RECESS"]       # -32.83
Z_PLATE0, Z_PLATE1 = -DECK_T - (C["Z_RECESS"] - C["Z_WALL"]), -DECK_T   # frame plate, -12.83 to -9
# The pipette's offset from the capper on the CubXL head (cubos/configs/gantry/
# cub_xl_ben_3_instrument_stirrer.yaml: offset_x 55, offset_y 11). While the capper works a vial the
# pipette hangs here; while the pipette works one, the capper hangs at minus this.
PIPETTE_FROM_CAPPER = (55.0, 11.0)


def pill(cx, cy, w, l, z0, z1):
    """A slot-shaped solid, long axis along Y."""
    return (cq.Workplane("XY").workplane(offset=z0).center(cx, cy).slot2D(l, w, angle=90).extrude(z1 - z0))


def half_pill(cx, s, w, z0, z1):
    """The near half of a slot, as a solid: the slot's near end circle (shrunk to width w) and a
    straight part out to |y| = HALF_END. s is the sign of y."""
    r = w / 2
    yc, ye = s * END_C, s * HALF_END
    return cyl(cx, yc, z0, z1, r).union(box(cx - r, min(yc, ye), z0, cx + r, max(yc, ye), z1))


def deck(half_x=50.0, half_y=56.0, cx=0.0, cy=0.0):
    """A patch of the deck round (cx, cy), slots included."""
    d = box(cx - half_x, cy - half_y, -DECK_T, cx + half_x, cy + half_y, 0.0)
    i0, i1 = math.floor((cx - half_x) / COL) - 1, math.ceil((cx + half_x) / COL) + 1
    j0, j1 = math.floor((cy - half_y) / ROW) - 1, math.ceil((cy + half_y) / ROW) + 1
    for i in range(i0, i1):
        for j in range(j0, j1):
            d = d.cut(pill(COL / 2 + i * COL, ROW / 2 + j * ROW, SLOT_W, SLOT_L, -DECK_T - 1, 1))
    return d


def collar():
    """The cup with no floor, on two bars that carry four half-length keys."""
    r0 = C["CUP_R0"]
    r1 = r0 - (CUP_TOP + 1) * math.tan(math.radians(C["CUP_DRAFT"]))
    body = cyl(0, 0, 0, CUP_TOP, C["CUP_OD"] / 2)
    for sx in (-1, 1):
        body = body.union(rbox(BAR_W, CELL_D, 0, BAR_T, 3.0).translate((sx * COL / 2, 0, 0)))
    for x, y in SLOTS:
        body = body.union(half_pill(x, math.copysign(1, y), KEY_W, -KEY_D, 0.01))
    inside = cyl(0, 0, RING, CUP_TOP + 1, C["CUP_OD"] / 2 + 0.5)    # finger gaps only within the cup, not across the bars
    cuts = [cone(-1, CUP_TOP + 1, r0 + math.tan(math.radians(C["CUP_DRAFT"])), r1),            # the vial goes to the deck
            box(-C["CUP_OD"], -C["CUP_SLOT"] / 2, RING, C["CUP_OD"], C["CUP_SLOT"] / 2, CUP_TOP + 1).intersect(inside),
            box(-C["CUP_SLOT"] / 2, -C["CUP_OD"], RING, C["CUP_SLOT"] / 2, C["CUP_OD"], CUP_TOP + 1).intersect(inside)]
    for x, y in CLAMP:
        cuts.append(cyl(x, y, -KEY_D - 1, BAR_T + 1, 1.7))
    for c in cuts:
        body = body.cut(c)
    return body


def frame():
    """Today's compact holder's flange without the cup or the floor, with corner pads, two bosses,
    two fan-screw counterbores and two inserts."""
    z0, z1 = Z_PLATE0, Z_PLATE1
    body = rbox(CELL_W, CELL_D, z0, z1, 5.0)
    blades = cyl(0, 0, z0 - PAD_T - 1, z0 + 1, C["FAN_BORE"] / 2 + 1.0)                   # keep the pads off the blades
    for sx, sy in itertools.product((-1, 1), repeat=2):
        corner = box(min(sx * 13.0, sx * 19.6), min(sy * 13.0, sy * 19.6), z0 - PAD_T, max(sx * 13.0, sx * 19.6),
                     max(sy * 13.0, sy * 19.6), z0 + 0.01)
        body = body.union(corner.cut(blades))
    for x, y in CLAMP:
        body = body.union(half_pill(x, math.copysign(1, y), KEY_W, z1 - 0.01, z1 + BOSS_H))
    cuts = [cyl(0, 0, z0 - 1, z1 + 1, C["CAR_D"] / 2 + 0.8),                                  # carrier bore
            box(-13.4, -2.15, z1 - 1.7, -10.2, 2.15, z1 + 1),                                  # Hall pocket, -X
            box(-21.0, -1.3, z1 - 1.2, -13.0, 1.3, z1 + 1),                                    # its leads' groove
            box(-22.6, -1.3, z0 - 1, -20.6, 1.3, z1 + 1)]                                      # and down past the fan
    for x, y in FAN_SCREWS:
        cuts.append(cyl(x, y, z0 - PAD_T - 1, z1 + 1, 1.7))                                    # M3 x 16
        cuts.append(cyl(x, y, z1 - CBORE_DEPTH, z1 + 1, CBORE_D / 2))                          # head counterbores
    for x, y in CLAMP:
        cuts.append(cyl(x, y, z1 + BOSS_H - 6.5, z1 + BOSS_H + 1, C["INSERT_HOLE"] / 2))       # M3 x 5.7 inserts
    for c in cuts:
        body = body.cut(c)
    return body


def base():
    """Today's compact base, unchanged, in this frame."""
    return make_base(True).translate((0, 0, DZ))


def bought():
    """Fan, magnets, Hall sensor, vial, bar, screws and inserts, simplified, in this frame."""
    z = lambda v: v + DZ  # noqa: E731
    fan = rbox(40, 40, z(C["Z_FAN0"]), z(C["Z_FAN1"]), 2.0).cut(cyl(0, 0, z(C["Z_FAN0"]) - 1, z(C["Z_FAN1"]) + 1, 19.0))
    fan = fan.union(cyl(0, 0, z(C["Z_FAN0"] + 2.0), z(C["Z_FAN1"]), C["HUB_D"] / 2))
    for k in range(7):
        fan = fan.union(box(C["HUB_D"] / 2 - 1, -0.5, z(C["Z_FAN0"] + 2.8), 18.4, 0.5, z(C["Z_FAN1"] - 0.8))
                        .rotate((0, 0, 0), (0, 0, 1), k * 360 / 7 + 10))
    for sx in (-1, 1):
        for sy in (-1, 1):
            fan = fan.cut(cyl(sx * 16, sy * 16, z(C["Z_FAN0"]) - 1, z(C["Z_FAN1"]) + 1, 1.7))
    mag_top = z(22.645)
    mags = [cyl(s * C["MAG_CC"] / 2, 0, mag_top - C["MAG_T"], mag_top, C["MAG_D"] / 2) for s in (1, -1)]
    hall = box(-13.35, -2.03, z(22.23), -10.3, 2.03, z(22.23) + 1.52)
    vial = cyl(0, 0, 0, C["VIAL_H"], C["VIAL_OD"] / 2).cut(cyl(0, 0, C["VIAL_BOT"], C["VIAL_H"] + 1, C["VIAL_OD"] / 2 - C["VIAL_WALL"]))
    cap = cyl(0, 0, C["VIAL_H"] - 10.0, C["VIAL_H"] + 3.0, 12.6)
    barz = C["VIAL_BOT"] + C["BAR_D"] / 2
    stirbar = (cq.Workplane("YZ").workplane(offset=-(C["BAR_L"] - C["BAR_D"]) / 2).center(0, barz)
               .circle(C["BAR_D"] / 2).extrude(C["BAR_L"] - C["BAR_D"]))
    for s in (-1, 1):
        stirbar = stirbar.union(cq.Workplane("XY").sphere(C["BAR_D"] / 2).translate((s * (C["BAR_L"] - C["BAR_D"]) / 2, 0, barz)))
    screws, inserts = [], []
    zt = Z_PLATE1 + BOSS_H
    for x, y in CLAMP:
        screws.append(cyl(x, y, BAR_T, BAR_T + 3.0, 2.75).union(cyl(x, y, BAR_T - CLAMP_L, BAR_T, 1.5)))
        inserts.append(cyl(x, y, zt - C["INSERT_L"], zt, C["INSERT_OD"] / 2).cut(cyl(x, y, zt - 10, zt + 1, 1.5)))
    seat = Z_PLATE1 - CBORE_DEPTH
    fan_screws = [cyl(x, y, seat - FAN_SCREW_L, seat, 1.5).union(cyl(x, y, seat, seat + 3.0, 2.75)) for x, y in FAN_SCREWS]
    return dict(fan=fan, magnets=mags, hall=hall, vial=vial, cap=cap, bar=stirbar, screws=screws,
                inserts=inserts, fan_screws=fan_screws)


def screw_checks() -> list:
    """(what, value, limit, ok) for the four screws and the parts they go into."""
    out = []

    def add(what, value, limit, ok=None):
        out.append((what, value, limit, value >= limit if ok is None else ok))

    # fan screws, M3 x 16 from the frame's counterbores into the base's post inserts (stirrer frame)
    seat = Z_PLATE1 - CBORE_DEPTH - DZ                       # 20.63
    tip = seat - FAN_SCREW_L
    insert_bottom = C["Z_FAN0"] - C["INSERT_L"]              # the insert's lower end
    hole_floor = C["Z_FAN0"] - 7.5                           # compact base: 7.5 mm holes
    add("fan screw M3 x 16: thread in the base's insert (mm)", C["Z_FAN0"] - max(tip, insert_bottom), 3.0)
    add("fan screw M3 x 16: tip above the insert hole's floor (mm)", tip - hole_floor, 0.3)
    add("fan screw: plastic under its head, pad included (mm)", (Z_PLATE1 - CBORE_DEPTH) - (Z_PLATE0 - PAD_T), 1.0)
    add("fan screw head below the deck's underside (mm)", CBORE_DEPTH - 3.0, 0.1)
    # clamp screws, M3 x 12 from the collar's bars into the bosses' inserts (deck frame)
    tip = BAR_T - CLAMP_L
    top = Z_PLATE1 + BOSS_H
    add("clamp screw M3 x 12: thread in the insert (mm)", top - max(tip, top - C["INSERT_L"]), 4.0)
    add("clamp screw M3 x 12: tip above the insert hole's floor (mm)", tip - (top - 6.5), 0.3)
    add("collar key to frame boss, in the slot (mm)", -KEY_D - top, 0.5)
    # walls round the clamp inserts, in the boss (plan)
    r_ins = C["INSERT_OD"] / 2
    x, y = CLAMP[0]
    add("clamp insert: wall to the boss's sides (mm)", (KEY_W / 2) - r_ins, 1.2)
    add("clamp insert: wall to the boss's round end (mm)", KEY_W / 2 - (abs(y) - END_C) - r_ins, 1.2)
    add("clamp insert: wall to the boss's flat end (mm)", HALF_END - abs(y) - r_ins, 1.2)
    return out


def module_parts():
    """The parts a neighbour could touch, as CadQuery solids in this module's frame."""
    b = bought()
    return {"collar": collar(), "frame": frame(), "base": base(), "fan": b["fan"], "vial": b["vial"].union(b["cap"]),
            "clamp screws": b["screws"][0].union(b["screws"][1]), "fan screws": b["fan_screws"][0].union(b["fan_screws"][1])}


def side_by_side_check(out=print):
    """Gaps between every part of one module and every part of each neighbour on the 50 x 45 mm grid,
    and between each part and the deck."""
    parts = {k: v.val() for k, v in module_parts().items()}
    worst_all = math.inf
    out("Side by side: the smallest gap from each part of one module to any part of a neighbour (mm)")
    out(f"  neighbours at the grid's closest pitch, {PITCH_X:g} mm in X and {PITCH_Y:g} mm in Y\n")
    for name, (dx, dy) in {"X, +50": (PITCH_X, 0), "Y, +45": (0, PITCH_Y), "diagonal, +50 +45": (PITCH_X, PITCH_Y),
                           "diagonal, +50 -45": (PITCH_X, -PITCH_Y)}.items():
        best = (math.inf, "", "")
        for (ka, a), (kb, b) in itertools.product(parts.items(), repeat=2):
            d = a.distance(b.moved(cq.Location(cq.Vector(dx, dy, 0))))
            if d < best[0]:
                best = (d, ka, kb)
        worst_all = min(worst_all, best[0])
        out(f"  {name:18s} {best[0]:6.2f}   ({best[1]} to the neighbour's {best[2]})")
    out("\nEach part against the deck (slots included): overlap must be 0")
    d = deck(60, 60).val()
    worst_overlap = 0.0
    for k, v in parts.items():
        ov = v.intersect(d).Volume()
        worst_overlap = max(worst_overlap, ov)
        out(f"  {k:14s} overlap {ov:8.3f} mm3, gap {v.distance(d):5.2f} mm")
    out("\nFootprint of each part, x and y (the cell is 49 x 44, centred on the vial)")
    for k in ("collar", "frame", "base"):
        bb = parts[k].BoundingBox()
        out(f"  {k:7s} x {bb.xmin:7.2f} .. {bb.xmax:6.2f}   y {bb.ymin:7.2f} .. {bb.ymax:6.2f}")
    return worst_all, worst_overlap


def head_clearance(out=print):
    """Plan distance from where the pipette (or the capper) hangs to each neighbour's vial axis."""
    px, py = PIPETTE_FROM_CAPPER
    r_cup, r_vial, r_cap = C["CUP_OD"] / 2, C["VIAL_OD"] / 2, 12.6
    out(f"\nThe head: the pipette is {px:g} mm +X, {py:g} mm +Y of the capper (gantry file). While the capper")
    out("works vial V the pipette hangs over V + (55, 11), tip end about 21 mm above the deck; while the")
    out("pipette works deep in V the capper hangs over V - (55, 11), about at V's rim. Plan distance from")
    out(f"there to each neighbour's axis (cup radius {r_cup:.1f}, vial {r_vial:.2f}, cap {r_cap}; all are taller than 21 mm):")
    rows = []
    for name, (nx, ny) in {"X, 50 (two columns)": (50, 0), "X, 75 (three columns)": (75, 0), "X, 100": (100, 0),
                           "Y, 45 (one row)": (0, 45), "diagonal 50, 45": (50, 45), "diagonal 50, -45": (50, -45)}.items():
        dists = [math.hypot(s * px - sn * nx, s * py - sn * ny) for s in (1, -1) for sn in (1, -1)]
        d = min(dists)
        rows.append((name, d, d - r_cup))
        out(f"  neighbour at {name:22s} {d:6.1f} mm   ({d - r_cup:+6.1f} from the cup's edge)")
    return rows


def export_all():
    """STL and STEP into stl/under-deck/ and step/under-deck/, beside the compact parts (a folder named
    parts/ would be ignored by the repo's .gitignore)."""
    stl_dir, step_dir = ROOT / "stl" / "under-deck", ROOT / "step" / "under-deck"
    stl_dir.mkdir(parents=True, exist_ok=True)
    step_dir.mkdir(parents=True, exist_ok=True)
    parts = {"collar": collar(), "frame": frame()}
    for name, wp in parts.items():
        cq.exporters.export(wp, str(stl_dir / f"{name}.stl"), tolerance=0.02, angularTolerance=0.15)
        cq.exporters.export(wp, str(step_dir / f"{name}.step"))
    return parts


if __name__ == "__main__":
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    parts = export_all()
    for name, wp in parts.items():
        s = wp.val()
        bb = s.BoundingBox()
        out(f"{name:7s} valid {s.isValid()}, {len(wp.solids().vals())} solid, {s.Volume():8.1f} mm3, "
            f"x {bb.xmin:.2f}..{bb.xmax:.2f}, y {bb.ymin:.2f}..{bb.ymax:.2f}, z {bb.zmin:.2f}..{bb.zmax:.2f}")
    out(f"stirrer frame -> deck frame: z + {DZ:.2f}; the compact base hangs to z {DZ:.2f}, "
        f"{-DZ - DECK_T:.2f} mm under the deck's underside")
    out(f"magnet faces z {22.645 + DZ:.3f}; deck underside z {-DECK_T}; vial's outside bottom z 0: gap {-(22.645 + DZ):.3f} mm")
    if "--check" in sys.argv:
        out("\nScrews and inserts")
        bad = 0
        for what, v, lim, ok in screw_checks():
            bad += not ok
            out(f"  {'ok ' if ok else 'BAD'} {what:78s} {v:6.2f}   (need >= {lim:.2f})")
        fx = abs(FAN_SCREWS[0][0])
        out(f"  note: a fan screw's shank (x {fx - 1.5:g} to {fx + 1.5:g}) reaches its slot's edge (x {COL / 2 + SLOT_W / 2:g}),"
            " so it can't come up through the slot as the clamp")
        out()
        worst, overlap = side_by_side_check(out)
        head_clearance(out)
        bad += (worst < 0.4) + (overlap > 1e-3)
        out(f"\n{bad} check(s) failed")
        (HERE / "side_by_side_check_output.txt").write_text("\n".join(lines) + "\n")
