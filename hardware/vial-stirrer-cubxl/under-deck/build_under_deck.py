#!/usr/bin/env python3
"""Mock-up: the stir module's fan under the CubXL deck, so the 9 mm deck is the spacer.

Asked for by @benwhitney5463 on PR #348 (2026-11-19). A MOCK-UP to discuss, not checked for print.

z = 0 is the deck's top face, the vial's axis is x = y = 0, mm. The vial sits between four deck
slots (25 mm columns, 45 mm rows), so it stands on solid polycarbonate: the nearest slot edge is
14.5 mm from its axis, against its 13.75 mm radius.

  above the deck  collar: the 9-vial holder's cup (ring and four spring fingers) with NO floor, on
                  two bars that carry four Cubware-style pill keys, 3 mm into four slots
  the deck        9 mm (Ben's measurement); the vial stands on it
  under the deck  frame: today's compact holder's flange (z 20 -> 23.83 in the stirrer's own
                  frame) with the cup and floor gone, so its top face is against the deck's
                  underside, plus four half-pill bosses that go 5 mm up into the same slots
                  today's compact base, fan, carrier, magnets, Hall sensor and junction board,
                  unchanged, on the same four M3 x 20 screws
  clamp           four M3 x 12 from the top, through the collar's keys, into heat-set inserts in
                  the frame's bosses: they sandwich the deck, and keys and bosses in the same
                  slots line the magnets up with the vial

    python under-deck/build_under_deck.py      # from hardware/vial-stirrer-cubxl: stl/under-deck/, step/under-deck/
"""
from __future__ import annotations

import math
import pathlib
import sys

import cadquery as cq

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "compact"))
from build_compact import C, box, cyl, cone, rbox  # noqa: E402

DECK_T = 9.0                       # Ben, 2026-11-19 (Cubware's STEP says 10)
SLOT_W, SLOT_L = 10.0, 25.0        # deck slots, long axis along Y
COL, ROW = 25.0, 45.0              # slot pitch
KEY_W, KEY_L = 9.8, 24.8           # Cubware key: 0.1 mm a side
SLOTS = [(sx * COL / 2, sy * ROW / 2) for sx in (-1, 1) for sy in (-1, 1)]   # the four round the vial
SCREW_Y = 28.0                     # clamp screws on the slot centreline, toward the far end
KEY_D = 3.0                        # collar keys: 3 mm down into the slot
BOSS_H = 5.0                       # frame bosses: 5 mm up into the slot (1 mm short of the keys)
BOSS_Y0 = 21.0                     # bosses fill each slot from here to its far end
BAR_W, BAR_T = 12.0, 3.0           # the collar's bars, over the slot columns
RING = C["CUP_RING"]               # 2.0: full ring above the floor, then the fingers
CUP_TOP = C["Z_TOP"] - C["Z_VIAL"] # 17.0: finger tips above the vial's bottom
# The stirrer's own frame (z 0 on the deck's top face when it sits on the deck) to this one: its
# holder's recess ceiling, z 23.83, goes to the deck's underside.
DZ = -DECK_T - C["Z_RECESS"]       # -32.83


def pill(cx, cy, w, l, z0, z1):
    """A slot-shaped solid, long axis along Y."""
    return (cq.Workplane("XY").workplane(offset=z0).center(cx, cy).slot2D(l, w, angle=90).extrude(z1 - z0))


def deck(half_x=50.0, half_y=56.0):
    d = box(-half_x, -half_y, -DECK_T, half_x, half_y, 0.0)
    for i in range(-2, 2):
        for j in (-1, 0):
            d = d.cut(pill(COL / 2 + i * COL, ROW / 2 + j * ROW, SLOT_W, SLOT_L, -DECK_T - 1, 1))
    return d


def collar():
    """The cup with no floor, on two bars that carry the keys."""
    r0 = C["CUP_R0"]
    r1 = r0 - (CUP_TOP + 1) * math.tan(math.radians(C["CUP_DRAFT"]))
    body = cyl(0, 0, 0, CUP_TOP, C["CUP_OD"] / 2)
    for sx in (-1, 1):
        body = body.union(rbox(BAR_W, 2 * (ROW / 2 + KEY_L / 2) + 1.0, 0, BAR_T, 3.0).translate((sx * COL / 2, 0, 0)))
    for x, y in SLOTS:
        body = body.union(pill(x, y, KEY_W, KEY_L, -KEY_D, 0.01))
    inside = cyl(0, 0, RING, CUP_TOP + 1, C["CUP_OD"] / 2 + 0.5)    # finger gaps only within the cup, not across the bars
    cuts = [cone(-1, CUP_TOP + 1, r0 + math.tan(math.radians(C["CUP_DRAFT"])), r1),            # the vial goes to the deck
            box(-C["CUP_OD"], -C["CUP_SLOT"] / 2, RING, C["CUP_OD"], C["CUP_SLOT"] / 2, CUP_TOP + 1).intersect(inside),
            box(-C["CUP_SLOT"] / 2, -C["CUP_OD"], RING, C["CUP_SLOT"] / 2, C["CUP_OD"], CUP_TOP + 1).intersect(inside)]
    for x, y in SLOTS:
        cuts.append(cyl(x, math.copysign(SCREW_Y, y), -KEY_D - 1, BAR_T + 1, 1.7))
    for c in cuts:
        body = body.cut(c)
    return body


def frame():
    """Today's compact holder's flange without the cup or the floor, plus four bosses."""
    z0, z1 = -DECK_T - (C["Z_RECESS"] - C["Z_WALL"]), -DECK_T          # -12.83 to -9
    W, D = 49.0, 2 * (ROW / 2 + SLOT_L / 2 + 1.0)                       # 49 x 72
    body = rbox(W, D, z0, z1, 5.0)
    for x, y in SLOTS:
        s = math.copysign(1, y)
        yc = s * (BOSS_Y0 + (ROW / 2 + KEY_L / 2 - BOSS_Y0) / 2)
        body = body.union(pill(x, yc, KEY_W, ROW / 2 + KEY_L / 2 - BOSS_Y0, z1 - 0.01, z1 + BOSS_H))
    cuts = [cyl(0, 0, z0 - 1, z1 + 1, C["CAR_D"] / 2 + 0.8),                                  # carrier bore
            box(-13.4, -2.15, z1 - 1.7, -10.2, 2.15, z1 + 1),                                  # Hall pocket, -X
            box(-25.5, -1.3, z1 - 1.2, -13.0, 1.3, z1 + 1)]                                    # its leads' groove
    fp = C["FAN_PITCH"] / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            cuts.append(cyl(sx * fp, sy * fp, z0 - 1, z1 + 1, 1.7))                             # M3 x 20, as today
            cuts.append(cyl(sx * fp, sy * fp, z1 - 3.0, z1 + 1, 3.25))                          # head counterbores
    for x, y in SLOTS:
        cuts.append(cyl(x, math.copysign(SCREW_Y, y), z1 + BOSS_H - 6.5, z1 + BOSS_H + 1, C["INSERT_HOLE"] / 2))
    for c in cuts:
        body = body.cut(c)
    return body


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
    zt = -DECK_T + BOSS_H
    for x, y in SLOTS:
        ys = math.copysign(SCREW_Y, y)
        screws.append(cyl(x, ys, BAR_T, BAR_T + 3.0, 2.75).union(cyl(x, ys, BAR_T - 12.0, BAR_T, 1.5)))
        inserts.append(cyl(x, ys, zt - C["INSERT_L"], zt, C["INSERT_OD"] / 2).cut(cyl(x, ys, zt - 10, zt + 1, 1.5)))
    fp = C["FAN_PITCH"] / 2
    fan_screws = [cyl(sx * fp, sy * fp, -DECK_T - 3.0 - 20.0, -DECK_T - 3.0, 1.5)
                  .union(cyl(sx * fp, sy * fp, -DECK_T - 3.0, -DECK_T - 0.2, 2.75)) for sx in (-1, 1) for sy in (-1, 1)]
    return dict(fan=fan, magnets=mags, hall=hall, vial=vial, cap=cap, bar=stirbar, screws=screws,
                inserts=inserts, fan_screws=fan_screws)


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
    parts = export_all()
    for name, wp in parts.items():
        s = wp.val()
        bb = s.BoundingBox()
        print(f"{name:7s} valid {s.isValid()}, {len(wp.solids().vals())} solid, {s.Volume():8.1f} mm3, "
              f"x {bb.xmin:.2f}..{bb.xmax:.2f}, y {bb.ymin:.2f}..{bb.ymax:.2f}, z {bb.zmin:.2f}..{bb.zmax:.2f}")
    print(f"stirrer frame -> deck frame: z + {DZ:.2f}; the compact base hangs to z {DZ:.2f}, "
          f"{-DZ - DECK_T:.2f} mm under the deck's underside")
    print(f"magnet faces z {22.645 + DZ:.3f}; deck underside z {-DECK_T}; vial's outside bottom z 0: gap {-(22.645 + DZ):.3f} mm")
