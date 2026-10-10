"""CubXL side of the integration: the PandaDeck, the head's envelope, and the two new
printed parts (deck adapter, pipette-tip dock).

Frames
------
S  spectrometer frame from openraman_assembly (baseplate top = z 0, sample port at +x).
D  PandaDeck frame, as in Cubware's PandaDeck.step: X 0..480, Y -490..0, top at Z 10.
   A pose (theta, tx, ty) maps S to D: xy_D = Rot(theta) xy_S + (tx, ty), Z_D = z_S + 28
   (baseplate 10 mm + adapter 8 mm, adapter bottom on the deck top).

CubOS deck coordinates <-> D (ASSUMED, see ../README.md#the-one-assumption): the pipette
reaches deck x 54..442 and y 13..246.7 (gantry 0..388 / 0..233.7 plus the pipette offset
54.0 / 12.999 from cub_xl_ben_pipette_capper.yaml). From Ben's 2026-10-09 photo the vial
column and the tip rack put CubOS x ~ X_D - 50 and CubOS y ~ -Y_D - 45 (y grows towards
the front). Jog the pipette over two slot centres and update CUBOS_FROM_DECK to pin it.
"""
from __future__ import annotations

import math

import cadquery as cq
import numpy as np

from openraman_assembly import AXIS_Y, BEAM_H, SAMPLE_FOCUS, SAMPLE_LENS_X, box, cyl

# --- PandaDeck (Cubware cubxl_plus/deck/polycarbonate_deck/PandaDeck.step, measured)
DECK_W, DECK_D, DECK_T = 480.0, 490.0, 10.0
SLOT_X = [27.5 + 25.0 * i for i in range(18)]          # 18 columns, 25 mm pitch
SLOT_Y = [-45.0 * j for j in range(1, 11)]             # 10 rows, 45 mm pitch
SLOT_W, SLOT_L = 10.0, 25.0                            # stadium, long axis along deck Y
KEY_W, KEY_L, KEY_H = 9.8, 24.8, 9.0                   # as Cubware's 9VialHolder-key (0.1 mm/side)

ADAPTER_T = 8.0
Z_S_TO_D = 10.0 + 10.0 + ADAPTER_T                     # deck top + baseplate + adapter
CUBOS_FROM_DECK = dict(x0=50.0, y0=45.0)               # CubOS x = X_D - x0, y = -Y_D - y0 (ASSUMED)
PIPETTE_REACH = dict(x=(54.0, 442.0), y=(12.999, 246.664))
CAPPER_FROM_PIPETTE = (-54.0, -12.999)                 # CubOS deck frame
CAPPER_BOX = (50.0, 32.0)                              # PAW-V2 electromagnet mount footprint, ../../electromagnetic-capper/cad
CAPPER_BELOW_NOZZLE = 17.0                             # capper depth -17.0 vs pipette 0.0
TIP_LEN = 35.0                                         # Ben, 2026-08-06
TIP_BELOW_BEAM = 4.0                                   # focus 4 mm above the tip's end: inside 20 uL
DOCK_TOP = BEAM_H + 8.0                                # 30 mm: leaves the capper 6 mm
CORNER_HOLES = [(8.0, 8.0), (8.0, 142.0), (292.0, 8.0), (292.0, 142.0)]   # P00001 M4 counterbores, frame S

# --- frames
def cubos_to_deck(x, y):
    return x + CUBOS_FROM_DECK["x0"], -(y + CUBOS_FROM_DECK["y0"])


def deck_to_cubos(X, Y):
    return X - CUBOS_FROM_DECK["x0"], -Y - CUBOS_FROM_DECK["y0"]


def pose_matrix(theta_deg, tx, ty):
    c, s = math.cos(math.radians(theta_deg)), math.sin(math.radians(theta_deg))
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])
    return R, np.array([tx, ty, Z_S_TO_D])


def reach_polygon_deck():
    (x0, x1), (y0, y1) = PIPETTE_REACH["x"], PIPETTE_REACH["y"]
    pts = [cubos_to_deck(x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    return pts


# --- deck
def panda_deck(step_path=None):
    if step_path:
        return cq.importers.importStep(str(step_path)).val()
    d = box(DECK_W, DECK_D, DECK_T, DECK_W / 2, -DECK_D / 2, 0.0)
    for x in SLOT_X:
        for y in SLOT_Y:
            d = d.cut(slot_solid(x, y, SLOT_W, SLOT_L, -1.0, DECK_T + 2))
    return d


def slot_solid(x, y, w, l, z0, h, angle_deg=0.0):
    """Stadium w x l (long axis along local y) at (x, y), rotated by angle about z."""
    s = (cq.Workplane("XY").workplane(offset=z0).slot2D(l, w, angle=90.0).extrude(h).val())
    return s.rotate(cq.Vector(), cq.Vector(0, 0, 1), angle_deg).moved(cq.Location(cq.Vector(x, y, 0)))


# --- new part 1: pipette-tip dock (frame S)
def tip_dock():
    """Black ASA. Rides the sample-port CP33B on two ER1 rods like the official liquid cuvette
    (rods at y = axis +-15, z = BEAM_H - 15), glues an AC127-019-A in its snout at the official
    cuvette-lens station, and puts the lens focus on a vertical tip channel; the beam then ends
    in a trap."""
    fx, ax_y, h = SAMPLE_FOCUS[0], AXIS_Y, BEAM_H
    x0, x1 = 300.6, 338.0
    body = box(x1 - x0, 44.0, DOCK_TOP + 10.0, (x0 + x1) / 2, ax_y, -10.0)
    snout = cq.Solid.makeCylinder(10.0, x0 - 289.0 + 0.5, cq.Vector(289.0, ax_y, h), cq.Vector(1, 0, 0))
    d = body.fuse(snout)
    # lens seat: Ø12.8 bore, 0.6 mm lip on the sample side of the lens (official station x = 294.7)
    d = d.cut(cq.Solid.makeCylinder(6.4, 298.0 - 288.0, cq.Vector(288.0, ax_y, h), cq.Vector(1, 0, 0)))
    d = d.cut(cq.Solid.makeCylinder(5.5, 40.0, cq.Vector(297.0, ax_y, h), cq.Vector(1, 0, 0)))   # clear aperture to the trap
    # rod bores for the two ER1s from the bracket, and side setscrews (SS4MN4)
    for sy in (-15.0, 15.0):
        d = d.cut(cq.Solid.makeCylinder(3.05, 12.0, cq.Vector(x0 - 0.1, ax_y + sy, h - 15.0), cq.Vector(1, 0, 0)))
        d = d.cut(cq.Solid.makeCylinder(1.65, 8.0, cq.Vector(x0 + 6.0, ax_y + sy + math.copysign(1, sy) * 9.0, h - 15.0),
                                        cq.Vector(0, -math.copysign(1, sy), 0)))
    # tip channel: funnel Ø14 -> Ø3.6 over the top 6 mm, then straight through for drips
    funnel = cq.Solid.makeCone(1.8, 7.0, 6.01, cq.Vector(fx, ax_y, DOCK_TOP - 6.0), cq.Vector(0, 0, 1))
    d = d.cut(funnel).cut(cq.Solid.makeCylinder(1.8, DOCK_TOP + 12.0, cq.Vector(fx, ax_y, -11.0)))
    # beam trap: the beam continues +x into a blind cavity whose back wall is inclined 45 deg
    trap = box(14.0, 12.0, 16.0, fx + 15.0, ax_y, h - 8.0)
    wedge = (cq.Workplane("XZ").polyline([(fx + 22.0, h - 8.0), (fx + 22.0, h + 8.0), (fx + 14.0, h + 8.0)]).close()
             .extrude(6.0, both=True).val().moved(cq.Location(cq.Vector(0, ax_y, 0))))
    d = d.cut(trap.cut(wedge))
    return d


def tip_shape(nozzle_xyz):
    """Opentrons 20 uL tip: Ø0.9 at the end -> Ø5.5 at the nozzle, 35 mm."""
    x, y, z = nozzle_xyz
    return cq.Solid.makeCone(0.45, 2.75, TIP_LEN, cq.Vector(x, y, z - TIP_LEN), cq.Vector(0, 0, 1))


# --- new part 2: deck adapter (frame S; keys depend on the pose)
def adapter_outline():
    """Plate outline in S: the baseplate plus 4 mm, and a tongue under the dock."""
    return [(-4, -4), (304, -4), (304, AXIS_Y - 26), (340, AXIS_Y - 26), (340, AXIS_Y + 26),
            (304, AXIS_Y + 26), (304, 154), (-4, 154)]


def keys_for_pose(theta_deg, tx, ty, max_keys=6, margin=2.0):
    """Slots fully under the adapter for this pose, spread out: up to max_keys, corners first."""
    from shapely.geometry import Point, Polygon
    R, t = pose_matrix(theta_deg, tx, ty)
    poly = Polygon([tuple((R[:2, :2] @ np.array(p) + t[:2])) for p in adapter_outline()]).buffer(-margin)
    inside = []
    for x in SLOT_X:
        for y in SLOT_Y:
            stadium = Point(x, y + 7.5).buffer(SLOT_W / 2).union(Point(x, y - 7.5).buffer(SLOT_W / 2)).convex_hull
            if poly.contains(stadium):
                inside.append((x, y))
    if not inside:
        return []
    P = np.array(inside)
    c = P.mean(0)
    chosen = []
    for corner in (np.array([P[:, 0].min(), P[:, 1].min()]), np.array([P[:, 0].max(), P[:, 1].min()]),
                   np.array([P[:, 0].min(), P[:, 1].max()]), np.array([P[:, 0].max(), P[:, 1].max()])):
        k = tuple(P[np.argmin(np.linalg.norm(P - corner, axis=1))])
        if k not in chosen:
            chosen.append(k)
    rest = sorted((tuple(p) for p in P if tuple(p) not in chosen), key=lambda p: -min(
        np.linalg.norm(np.array(p) - np.array(q)) for q in chosen))
    return (chosen + rest)[:max_keys]


def deck_adapter(theta_deg, tx, ty, keys_deck):
    """ASA plate under the baseplate: four ruthex M4 inserts at the baseplate's corner
    counterbores, and keys (9.8 x 24.8 x 9 mm, Cubware's key size) into PandaDeck slots."""
    pts = adapter_outline()
    plate = cq.Workplane("XY").workplane(offset=-10.0 - ADAPTER_T).polyline(pts).close().extrude(ADAPTER_T).val()
    for x, y in CORNER_HOLES:
        plate = plate.cut(cyl(5.6, ADAPTER_T + 2, -10.0 - ADAPTER_T - 1).moved(cq.Location(cq.Vector(x, y, 0))))
    # cable relief under the camera's RJ45 end and the laser's phono jack
    plate = plate.cut(box(40.0, 14.0, ADAPTER_T + 2, 130.0, -4.0, -10.0 - ADAPTER_T - 1))
    R, t = pose_matrix(theta_deg, tx, ty)
    Rinv = R[:2, :2].T
    for X, Y in keys_deck:
        xs, ys = Rinv @ (np.array([X, Y]) - t[:2])
        key = slot_solid(xs, ys, KEY_W, KEY_L, -10.0 - ADAPTER_T - KEY_H, KEY_H + 0.5, angle_deg=-theta_deg)
        plate = plate.fuse(key)
    return plate


# --- the head (frame D), for collision checks and the render
def head_parts(tip_xy_deck, tip_end_z_deck):
    """Simplified CubXL head around the pipette, positioned so the tip's end sits at the given point."""
    X, Y = tip_xy_deck
    nozzle_z = tip_end_z_deck + TIP_LEN
    dxc, dyc = CAPPER_FROM_PIPETTE
    cx, cy = X + dxc, Y - dyc                            # CubOS -y is deck +Y
    parts = {
        "tip": tip_shape((X, Y, nozzle_z)),
        "pipette shaft": cyl(9.0, 30.0, nozzle_z).moved(cq.Location(cq.Vector(X, Y, 0))),
        "pipette body (P20 GEN2)": box(34.0, 52.0, 150.0, X, Y + 8.0, nozzle_z + 30.0),
        "capper": box(*CAPPER_BOX, 70.0, cx, cy, nozzle_z - CAPPER_BELOW_NOZZLE),
        "backboard": box(170.0, 6.0, 190.0, X - 40.0, Y + 45.0, nozzle_z + 25.0),
    }
    return parts, (cx, cy), nozzle_z
