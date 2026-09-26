#!/usr/bin/env python3
"""Raspberry Pi 5 dual-camera mount: parametric CadQuery model.

The Pi 5 counterpart of the Pi Zero 2 W "picam mount v2" from ac-dev-lab: one printed
L-bracket that sits on the same desk-clamp stand (1/4"-20 stud). The Pi 5 lies on the base,
and the upright carries two identical camera stations. Each station takes either a
Raspberry Pi HQ Camera (M2.5 holes, 30 x 30 mm) or a Camera Module 3 (M2 holes,
21 x 12.5 mm), so the mount holds an HQ Camera plus a Module 3, or two Module 3s (or two
HQ Cameras with short lenses).

The cameras sit on standoff bosses on the FRONT of the upright. The Zero 2 W mount clamps
its Module 3 behind the upright with the lens poking through, but the HQ Camera's integrated
tripod foot hangs 11 mm past its board, so it cannot sit behind a plate without the plate
being cut in two. On the front, the foot just hangs in air, and the lens and focus rings stay
fully reachable. The HQ bosses are 2.5 mm taller than the Module 3 bosses, so whichever
camera is fitted clears the other camera's bosses.

Every camera is fitted "cable up": its ribbon leaves the top edge of the board, passes
through a slot near the top of the upright and drops to the Pi 5's camera connectors,
keeping the cable clear of the Active Cooler. Flip the image 180 degrees in software.

Coordinates: X to the right as seen from the front, Y backwards (the cameras look along -Y),
Z up. Z = 0 is the underside of the base and Y = 0 is the front face of the upright.

    python mount.py               # build, run checks, export to ../exports
    python mount.py --check-only  # checks only
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
COS30 = math.cos(math.pi / 6)


@dataclass
class Params:
    # --- layout -------------------------------------------------------------------------
    station_pitch: float = 64.0     # between the two optical axes; 64 keeps a 16 mm HQ lens out
                                    # of a Module 3's view beside it (see the FOV check)
    axis_z: float = 24.0            # optical axes above the underside of the base

    # --- base ----------------------------------------------------------------------------
    base_t: float = 4.0
    apron_depth: float = 26.0       # full-width strip behind the upright (gussets, stand nut)
    base_corner_r: float = 5.0
    pi_gap: float = 18.0            # upright's back face to the Pi's microSD edge
    pi_margin: float = 4.0          # base beyond the Pi's outline
    pi_boss_d: float = 6.0
    pi_boss_h: float = 6.7          # PCB 1.3 + boss + base 4.0 = 12.0: an M2.5 x 12 ends flush
    vent_w: float = 30.0            # opening under the Pi (X), between its bosses
    vent_l: float = 40.0            # (Y)

    # --- 1/4"-20 stand stud (same interface as the Zero 2 W mount) -----------------------
    stud_clear_d: float = 7.0
    stand_nut_af: float = 11.5      # 7/16" thin nut (McMaster 91078A029) + 0.4
    stand_collar_h: float = 3.0     # stops the nut turning, so the mount screws onto the stud
    stand_collar_wall: float = 1.8

    # --- upright -------------------------------------------------------------------------
    upright_t: float = 4.0
    upright_margin: float = 3.0     # beyond an HQ board's edge
    top_r: float = 6.0
    gusset_t: float = 3.0
    gusset_len: float = 20.0        # along Y, behind the upright
    gusset_h: float = 28.0

    # --- camera stations (u across, v up, both from the optical axis) --------------------
    hq_board: float = 38.0
    hq_pitch: float = 30.0          # 4 x M2.5, 4 mm in from the edges
    hq_pcb_t: float = 1.4
    hq_boss_h: float = 6.5          # front face to the back of the HQ board
    hq_boss_d: float = 5.5
    m25_clear_d: float = 2.8
    m25_nut_af: float = 5.4         # 5.0 mm nut + 0.4
    m25_nut_depth: float = 2.3      # 2.0 mm nut + 0.3

    cm3_w: float = 25.0
    cm3_h: float = 23.862
    cm3_pcb_t: float = 1.12
    cm3_hole_du: float = 21.0       # 4 x M2 (slotted +-0.7 mm across)
    cm3_hole_v: tuple = (0.1, -12.4)  # lens axis is 14.4 mm from the far edge, holes 14.5 and 2.0
    cm3_lens_to_top: float = 9.462  # lens axis to the connector edge (23.862 - 14.4)
    cm3_boss_h: float = 4.0         # clears the 2.75 mm connector on the back
    cm3_boss_d: float = 4.5
    m2_clear_d: float = 2.4
    m2_nut_af: float = 4.4          # 4.0 mm nut + 0.4
    m2_nut_depth: float = 1.9       # 1.6 mm nut + 0.3

    slot_w: float = 18.0            # ribbon slot: the 15-way camera cable is 16 mm wide
    slot_h: float = 2.5
    slot_above_board: float = 4.5   # slot centre above the HQ board's top edge

    # ------------------------------------------------------------------------------------
    @property
    def stations(self) -> list[float]:
        return [-self.station_pitch / 2, self.station_pitch / 2]

    @property
    def upright_half_w(self) -> float:
        return self.station_pitch / 2 + self.hq_board / 2 + self.upright_margin

    @property
    def slot_v(self) -> float:
        return self.hq_board / 2 + self.slot_above_board

    @property
    def upright_top(self) -> float:
        return self.axis_z + self.slot_v + self.slot_h / 2 + 3.0

    @property
    def pi_y0(self) -> float:
        """Y of the Pi's microSD edge (its X = 0 edge)."""
        return self.upright_t + self.pi_gap

    @property
    def pi_x_edge(self) -> float:
        """X of the Pi's port edge (USB-C, HDMI, camera connectors): the Pi is centred."""
        return 28.0

    @property
    def pi_z(self) -> float:
        """Z of the Pi's PCB underside."""
        return self.base_t + self.pi_boss_h

    def pi_to_mount(self, xp: float, yp: float) -> tuple[float, float]:
        """Pi 5 board coordinates (X along the 85 mm edge, Y up from the port edge) to mount X, Y.
        The Pi lies with its microSD edge towards the upright."""
        return self.pi_x_edge - yp, self.pi_y0 + xp

    def pi_holes(self) -> list[tuple[float, float]]:
        return [self.pi_to_mount(x, y) for x in (3.5, 61.5) for y in (3.5, 52.5)]

    @property
    def stand_xy(self) -> tuple[float, float]:
        r = self.stand_nut_af / COS30 / 2 + self.stand_collar_wall
        return 0.0, self.upright_t + 1.0 + r


# --- small helpers ---------------------------------------------------------------------------

def box(x, y, z, cx=0.0, cy=0.0, z0=0.0) -> cq.Workplane:
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False)).translate((cx, cy, z0))


def box_span(x0, x1, y0, y1, z0, z1) -> cq.Workplane:
    return box(x1 - x0, y1 - y0, z1 - z0, (x0 + x1) / 2, (y0 + y1) / 2, z0)


def cyl(d, h, cx=0.0, cy=0.0, z0=0.0) -> cq.Workplane:
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((cx, cy, z0))


def hex_pts(af: float, vertex_up: bool) -> list[tuple[float, float]]:
    r = af / COS30 / 2
    a0 = 90 if vertex_up else 0
    return [(r * math.cos(math.radians(a0 + 60 * i)), r * math.sin(math.radians(a0 + 60 * i))) for i in range(6)]


def hex_prism(af, h, cx=0.0, cy=0.0, z0=0.0) -> cq.Workplane:
    return cq.Workplane("XY").polyline(hex_pts(af, False)).close().extrude(h).translate((cx, cy, z0))


def y_cyl(d, y0, y1, x, z) -> cq.Workplane:
    """Cylinder along Y from y0 to y1 (y1 < y0 extrudes towards the front)."""
    lo, hi = min(y0, y1), max(y0, y1)
    return cq.Workplane("XZ").center(x, z).circle(d / 2).extrude(hi - lo).translate((0, hi, 0))


def y_teardrop(d, y0, y1, x, z) -> cq.Workplane:
    """Boss along Y whose underside comes to a 45 degree point, so it prints with the
    base on the bed without support."""
    r = d / 2
    k = r / math.sqrt(2)
    lo, hi = min(y0, y1), max(y0, y1)
    drop = cq.Workplane("XZ").center(x, z).polyline([(-k, -k), (0, -r * math.sqrt(2)), (k, -k), (0, 0)]).close()
    return (cq.Workplane("XZ").center(x, z).circle(r).extrude(hi - lo)
            .union(drop.extrude(hi - lo)).translate((0, hi, 0)))


def y_hex(af, y0, y1, x, z) -> cq.Workplane:
    """Hex nut pocket along Y with a vertex on top, so its roof is self-supporting."""
    lo, hi = min(y0, y1), max(y0, y1)
    pts = [(x + px, z + pz) for px, pz in hex_pts(af, True)]
    return cq.Workplane("XZ").polyline(pts).close().extrude(hi - lo).translate((0, hi, 0))


def y_slot(w, h, x, z, y0, y1) -> cq.Workplane:
    lo, hi = min(y0, y1), max(y0, y1)
    return cq.Workplane("XZ").center(x, z).slot2D(w, h).extrude(hi - lo).translate((0, hi, 0))


# --- the printed part --------------------------------------------------------------------

def hq_holes(p: Params) -> list[tuple[float, float]]:
    a = p.hq_pitch / 2
    return [(su * a, sv * a) for su in (-1, 1) for sv in (-1, 1)]


def cm3_holes(p: Params) -> list[tuple[float, float]]:
    return [(su * p.cm3_hole_du / 2, v) for su in (-1, 1) for v in p.cm3_hole_v]


def make_base(p: Params) -> cq.Workplane:
    hw = p.upright_half_w
    xs = [x for x, _ in p.pi_holes()]
    pi_x0, pi_x1 = p.pi_x_edge - 56.0, p.pi_x_edge
    y_end = p.pi_y0 + 85.0 + 1.0
    apron = box_span(-hw, hw, 0, p.apron_depth, 0, p.base_t)
    stem = box_span(pi_x0 - p.pi_margin, pi_x1 + p.pi_margin, 0, y_end, 0, p.base_t)
    base = apron.union(stem).edges("|Z").fillet(p.base_corner_r)
    # Pi 5 bosses, with nut traps in the underside.
    for x, y in p.pi_holes():
        base = base.union(cyl(p.pi_boss_d, p.pi_boss_h + 0.5, x, y, p.base_t - 0.5))
        base = base.cut(cyl(p.m25_clear_d, p.base_t + p.pi_boss_h + 2, x, y, -1))
        base = base.cut(hex_prism(p.m25_nut_af, p.m25_nut_depth, x, y, 0).translate((0, 0, -0.01)))
    # Vent / lightening window under the middle of the Pi.
    ys = sorted({y for _, y in p.pi_holes()})
    vy = (ys[0] + ys[1]) / 2
    vent = box(p.vent_w, p.vent_l, p.base_t + 2, (min(xs) + max(xs)) / 2, vy, -1).edges("|Z").fillet(4)
    base = base.cut(vent)
    # 1/4"-20 stand stud: clearance hole and a collar that holds the thin nut.
    sx, sy = p.stand_xy
    r_out = p.stand_nut_af / COS30 / 2 + p.stand_collar_wall
    base = base.union(cyl(2 * r_out, p.stand_collar_h + 0.5, sx, sy, p.base_t - 0.5))
    base = base.cut(hex_prism(p.stand_nut_af, p.stand_collar_h + 1, sx, sy, p.base_t))
    base = base.cut(cyl(p.stud_clear_d, p.base_t + 2, sx, sy, -1))
    return base


def make_upright(p: Params) -> cq.Workplane:
    hw, t = p.upright_half_w, p.upright_t
    up = box_span(-hw, hw, 0, t, 0, p.upright_top)
    up = up.edges("|Y and >Z").fillet(p.top_r)
    for xc in p.stations:
        zc = p.axis_z
        for u, v in hq_holes(p):
            up = up.union(y_teardrop(p.hq_boss_d, 0.5, -p.hq_boss_h, xc + u, zc + v))
        for u, v in cm3_holes(p):
            up = up.union(y_teardrop(p.cm3_boss_d, 0.5, -p.cm3_boss_h, xc + u, zc + v))
    for xc in p.stations:
        zc = p.axis_z
        for u, v in hq_holes(p):
            up = up.cut(y_cyl(p.m25_clear_d, t + 1, -p.hq_boss_h - 1, xc + u, zc + v))
            up = up.cut(y_hex(p.m25_nut_af, t + 0.01, t - p.m25_nut_depth, xc + u, zc + v))
        for u, v in cm3_holes(p):
            up = up.cut(y_cyl(p.m2_clear_d, t + 1, -p.cm3_boss_h - 1, xc + u, zc + v))
            up = up.cut(y_hex(p.m2_nut_af, t + 0.01, t - p.m2_nut_depth, xc + u, zc + v))
        up = up.cut(y_slot(p.slot_w, p.slot_h, xc, zc + p.slot_v, -1, t + 1))
    return up


def make_gussets(p: Params) -> cq.Workplane:
    out = None
    for sx in (-1, 1):
        x = sx * (p.upright_half_w - p.gusset_t / 2)
        tri = (cq.Workplane("YZ").polyline([(p.upright_t - 0.5, p.base_t - 0.5),
                                            (p.upright_t + p.gusset_len, p.base_t - 0.5),
                                            (p.upright_t - 0.5, p.base_t + p.gusset_h)]).close()
               .extrude(p.gusset_t).translate((x - p.gusset_t / 2, 0, 0)))
        out = tri if out is None else out.union(tri)
    return out


def make_mount(p: Params) -> cq.Workplane:
    return make_base(p).union(make_upright(p)).union(make_gussets(p))


# --- reference models (not printed) ---------------------------------------------------------
# Raspberry Pi 5, from the official mechanical drawing and STEP model (connector positions
# and heights read from the STEP). Pi board coordinates: X along the 85 mm edge from the
# microSD end, Y up from the USB-C / HDMI / camera-connector edge, Z up from the PCB underside.

PI_PCB_T = 1.3


def pi_box(p: Params, x0, x1, y0, y1, z0, z1) -> cq.Workplane:
    """A box given in Pi board coordinates, placed in the mount."""
    (mx0, my0), (mx1, my1) = p.pi_to_mount(x0, y0), p.pi_to_mount(x1, y1)
    return box_span(min(mx0, mx1), max(mx0, mx1), min(my0, my1), max(my0, my1), p.pi_z + z0, p.pi_z + z1)


def pi_cyl(p: Params, d, x, y, z0, z1) -> cq.Workplane:
    mx, my = p.pi_to_mount(x, y)
    return cyl(d, z1 - z0, mx, my, p.pi_z + z0)


def make_pi5(p: Params) -> cq.Workplane:
    t = PI_PCB_T
    board = pi_box(p, 0, 85, 0, 56, 0, t).edges("|Z").fillet(3.0)
    for x, y in p.pi_holes():
        board = board.cut(cyl(2.7, 4, x, y, p.pi_z - 1))
    parts = [
        (66.45, 88.05, 2.29, 18.21, -0.66, 14.64),   # Ethernet
        (70.33, 88.00, 21.75, 36.25, -0.16, 17.53),  # USB 3
        (70.33, 88.00, 39.75, 54.25, -0.16, 17.53),  # USB 2
        (7.10, 57.90, 49.96, 55.04, t, 9.88),        # GPIO header with pins
        (6.73, 15.67, -1.20, 6.15, 0.34, 4.60),      # USB-C
        (22.0, 29.6, -1.00, 6.00, 0.30, 3.90),       # micro HDMI 0
        (35.4, 43.0, -1.00, 6.00, 0.30, 3.90),       # micro HDMI 1
        (47.10, 50.16, 0.14, 16.84, t, 5.29),        # camera/display connector
        (53.30, 56.35, 0.14, 16.84, t, 5.29),        # camera/display connector
        (59.91, 63.09, 7.91, 11.09, t, 9.88),        # PoE header
        (1.10, 4.16, 23.14, 36.84, t, 5.29),         # PCIe FFC connector
        (0.35, 2.95, 16.35, 20.45, t, 4.64),         # power button
        (2.25, 13.65, 22.11, 34.06, -1.42, 0.0),     # microSD card, underneath
    ]
    pi = board
    for b in parts:
        pi = pi.union(pi_box(p, *b))
    return pi


def make_active_cooler(p: Params) -> cq.Workplane:
    """Raspberry Pi Active Cooler: 63.5 x 42.5 mm, notched around the camera connectors,
    ~9 mm above the PCB, with its two push pins through the board."""
    t = PI_PCB_T
    x0, y1 = 0.1, 49.2
    body = pi_box(p, x0, x0 + 63.5, y1 - 42.5, y1, t, t + 9.0)
    body = body.cut(pi_box(p, 36.4, 70, -5, 18.6, t - 1, t + 10))
    for x, y in ((3.5, 9.5), (61.5, 46.5)):
        body = body.union(pi_cyl(p, 4.0, x, y, -3.4, t + 1))
    return body


def usb_c_plug(p: Params) -> cq.Workplane:
    """Envelope of a straight USB-C plug and the first bit of its cable."""
    return pi_box(p, 11.2 - 6.5, 11.2 + 6.5, -32.0, -1.2, 0.34 - 1.5, 4.6 + 1.5)


# HQ Camera, fitted "cable up" (tripod foot up). Dimensions from Raspberry Pi's CS-mount
# drawing; the foot and skirt outlines are estimates from the drawing and photos.

def station_to_mount(p: Params, xc: float, u: float, v: float) -> tuple[float, float]:
    return xc + u, p.axis_z + v


def cam_box(p: Params, xc, u0, u1, v0, v1, y0, y1) -> cq.Workplane:
    return box_span(xc + u0, xc + u1, min(y0, y1), max(y0, y1), p.axis_z + v0, p.axis_z + v1)


def make_hq_camera(p: Params, xc: float) -> dict[str, cq.Workplane]:
    yb = -p.hq_boss_h                  # back of the PCB
    yf = yb - p.hq_pcb_t               # front of the PCB
    h = p.hq_board / 2
    pcb = cam_box(p, xc, -h, h, -h, h, yb, yf).edges("|Y").fillet(1.0)
    for u, v in hq_holes(p):
        pcb = pcb.cut(y_cyl(2.5, yb + 1, yf - 1, xc + u, p.axis_z + v))
    conn = cam_box(p, xc, -9.8, 9.8, h - 5.71, h, yb, yb + 2.75)          # FPC connector (back)
    ring_front = yf - 14.43
    mount = y_cyl(30.75, yf, ring_front + 5.8, xc, p.axis_z)             # housing
    mount = mount.union(y_cyl(36.0, ring_front + 5.8, ring_front, xc, p.axis_z))  # back-focus ring
    mount = mount.union(cam_box(p, xc, -6.985, 6.985, 12.0, h + 11.0, yb, yb - 12.04))  # skirt + tripod foot
    mount = mount.union(cam_box(p, xc, -5.08, 5.08, -h - 2.7, -12.0, yf - 5.3, yf - 10.32))  # back-focus lock
    return {"pcb": pcb, "conn": conn, "mount": mount, "ring_front_y": ring_front}


# Lenses as simple envelopes: (outer diameter, length in front of the flange, needs C-CS adapter).
LENSES = {
    "6mm_CS": (30.0, 30.0, False),         # official 6 mm wide angle: 30 x 34 mm incl. thread
    "16mm_C": (39.0, 45.5, True),          # official 16 mm telephoto: 39 x 50 mm incl. thread
    "8-50mm_C_zoom": (40.0, 63.8, True),   # Waveshare 8-50 mm zoom used on the OT-2 lid mount
}


def make_hq_lens(p: Params, xc: float, ring_front_y: float, lens: str) -> cq.Workplane:
    d, length, adapter = LENSES[lens]
    y = ring_front_y
    out = None
    if adapter:
        out = y_cyl(31.0, y, y - 5.03, xc, p.axis_z)
        y -= 5.03
    body = y_cyl(d, y, y - length, xc, p.axis_z)
    return body if out is None else out.union(body)


# Camera Module 3, fitted cable up. Board, holes and connector from the official drawing and
# STEP model; lens housing 10.8 mm square, barrel 5.75 mm (standard) or 6.95 mm (wide).

CM3_LENS = {"standard": (5.75, 6.98, 66.0, 41.0), "wide": (6.95, 8.30, 102.0, 67.0)}


def make_cm3(p: Params, xc: float, variant: str = "standard") -> dict[str, cq.Workplane]:
    barrel_d, front, hfov, vfov = CM3_LENS[variant]
    yb = -p.cm3_boss_h
    yf = yb - p.cm3_pcb_t
    top = p.cm3_lens_to_top
    bot = top - p.cm3_h
    pcb = cam_box(p, xc, -p.cm3_w / 2, p.cm3_w / 2, bot, top, yb, yf)
    for u, v in cm3_holes(p):
        pcb = pcb.cut(y_cyl(2.2, yb + 1, yf - 1, xc + u, p.axis_z + v))
    for su in (-1, 1):   # the corners are notched: R2 arcs centred 0.73 mm in from each corner
        for v in (bot + 0.73, top - 0.73):
            pcb = pcb.cut(y_cyl(4.0, yb + 1, yf - 1, xc + su * (p.cm3_w / 2 - 0.73), p.axis_z + v))
    conn = cam_box(p, xc, -11.46, 11.46, top - 6.54, top, yb, yb + 2.75)
    rear = cam_box(p, xc, -1.05, 3.85, -9.4, -3.4, yb, yb + 1.75)         # tallest part on the back
    housing = cam_box(p, xc, -5.4, 5.4, -5.4, 5.4, yf, yf - 3.875)
    housing = housing.union(cam_box(p, xc, -5.4, 5.75, -12.7, -5.4, yf, yf - 1.04))  # sensor flex
    barrel = y_cyl(barrel_d, yf - 3.875, yf - front, xc, p.axis_z)
    return {"pcb": pcb, "conn": conn.union(rear), "lens": housing.union(barrel),
            "lens_front_y": yf - front, "hfov": hfov, "vfov": vfov}


def view_frustum(p: Params, xc: float, y_front: float, hfov: float, vfov: float, depth: float) -> cq.Workplane:
    """Rectangular view pyramid from the lens front, `depth` mm long, looking along -Y."""
    tx, tz = math.tan(math.radians(hfov / 2)), math.tan(math.radians(vfov / 2))
    apex = cq.Vector(xc, y_front, p.axis_z)
    far = [cq.Vector(xc + sx * depth * tx, y_front - depth, p.axis_z + sz * depth * tz)
           for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    faces = [cq.Face.makeFromWires(cq.Wire.makePolygon([apex, far[i], far[(i + 1) % 4]], close=True)) for i in range(4)]
    faces.append(cq.Face.makeFromWires(cq.Wire.makePolygon(far, close=True)))
    return cq.Workplane("XY").add(cq.Solid.makeSolid(cq.Shell.makeShell(faces)))


# --- configurations and checks -----------------------------------------------------------

def build_config(p: Params, cams: list[str], lens: str = "16mm_C", cm3_variant: str = "standard") -> dict:
    """cams[i] is "hq" or "cm3" for the left (-X) and right (+X) stations."""
    parts: dict[str, cq.Workplane] = {}
    meta = []
    for i, (kind, xc) in enumerate(zip(cams, p.stations)):
        tag = "L" if i == 0 else "R"
        if kind == "hq":
            hq = make_hq_camera(p, xc)
            parts[f"hq_pcb_{tag}"] = hq["pcb"]
            parts[f"hq_conn_{tag}"] = hq["conn"]
            parts[f"hq_mount_{tag}"] = hq["mount"]
            parts[f"hq_lens_{tag}"] = make_hq_lens(p, xc, hq["ring_front_y"], lens)
            meta.append({"station": tag, "camera": "HQ", "lens": lens})
        else:
            c = make_cm3(p, xc, cm3_variant)
            parts[f"cm3_pcb_{tag}"] = c["pcb"]
            parts[f"cm3_back_{tag}"] = c["conn"]
            parts[f"cm3_lens_{tag}"] = c["lens"]
            meta.append({"station": tag, "camera": f"Camera Module 3 ({cm3_variant})",
                         "lens_front_y": c["lens_front_y"], "hfov": c["hfov"], "vfov": c["vfov"], "xc": xc})
    return {"parts": parts, "meta": meta}


def overlap(a: cq.Workplane, b: cq.Workplane) -> float:
    common = a.val().intersect(b.val())
    return sum(s.Volume() for s in common.Solids())


def gap(a: cq.Workplane, b: cq.Workplane) -> float:
    return a.val().distance(b.val())


def fov_intrusion(p: Params, lens: str, cm3_variant: str, depth: float = 400.0) -> float:
    """Volume of the HQ lens (left station) inside the view pyramid of a Module 3 (right)."""
    hq = make_hq_camera(p, p.stations[0])
    obstacle = make_hq_lens(p, p.stations[0], hq["ring_front_y"], lens).union(hq["mount"])
    c = make_cm3(p, p.stations[1], cm3_variant)
    fr = view_frustum(p, p.stations[1], c["lens_front_y"], c["hfov"], c["vfov"], depth)
    return overlap(fr, obstacle)


def clear_pitch(p: Params, lens: str, cm3_variant: str) -> float:
    """Smallest station pitch at which the HQ lens stays out of the Module 3's view
    (horizontal edge of the view, to the lens barrel's far rim)."""
    d, length, adapter = LENSES[lens]
    hq_front = -p.hq_boss_h - p.hq_pcb_t - 14.43 - (5.03 if adapter else 0) - length
    c = make_cm3(p, 0, cm3_variant)
    reach = c["lens_front_y"] - hq_front
    return d / 2 + reach * math.tan(math.radians(c["hfov"] / 2))


def screw_stacks(p: Params) -> dict:
    return {
        "Pi 5: M2.5 x 12 (PCB + boss + base)": round(PI_PCB_T + p.pi_boss_h + p.base_t, 2),
        "HQ: M2.5 x 12 (PCB + boss + upright)": round(p.hq_pcb_t + p.hq_boss_h + p.upright_t, 2),
        "Module 3: M2 x 10 (PCB + boss + upright)": round(p.cm3_pcb_t + p.cm3_boss_h + p.upright_t, 2),
    }


def run_checks(p: Params, mount: cq.Workplane) -> dict:
    pi, cooler = make_pi5(p), make_active_cooler(p)
    res: dict = {"overlap_mm3": {}, "gap_mm": {}}
    ov, gp = res["overlap_mm3"], res["gap_mm"]
    ov["mount vs Pi 5"] = overlap(mount, pi)
    ov["mount vs Active Cooler (incl. push pins)"] = overlap(mount, cooler)
    ov["mount vs USB-C plug"] = overlap(mount, usb_c_plug(p))
    for name, cams in (("HQ + Module 3", ["hq", "cm3"]), ("Module 3 + HQ", ["cm3", "hq"]),
                       ("2 x Module 3", ["cm3", "cm3"]), ("2 x HQ (6 mm lenses)", ["hq", "hq"])):
        cfg = build_config(p, cams, lens="6mm_CS" if cams == ["hq", "hq"] else "16mm_C")
        cam_all = None
        for k, v in cfg["parts"].items():
            ov[f"{name}: mount vs {k}"] = overlap(mount, v)
            cam_all = v if cam_all is None else cam_all.union(v)
        ov[f"{name}: cameras vs Pi 5 + cooler"] = overlap(cam_all, pi.union(cooler))
    # How close each camera gets to the other camera's bosses.
    hq = make_hq_camera(p, p.stations[0])
    cm3 = make_cm3(p, p.stations[0])
    gp["HQ board back to Module 3 boss tops"] = round(p.hq_boss_h - p.cm3_boss_h, 2)
    gp["HQ connector to nearest boss"] = round(gap(hq["conn"], mount), 2)
    gp["Module 3 board to HQ bosses"] = round(gap(cm3["pcb"], make_upright(p).intersect(
        box_span(-200, 200, -p.hq_boss_h - 1, -p.cm3_boss_h - p.cm3_pcb_t - 0.01, -10, 200))), 2)
    gp["Module 3 connector to upright"] = round(gap(cm3["conn"], mount), 2)
    gp["Pi 5 underside to base (at the bosses)"] = p.pi_boss_h
    gp["Active Cooler push pins to base"] = round(gap(cooler, mount), 2)
    gp["USB-C plug to mount"] = round(gap(usb_c_plug(p), mount), 2)
    res["fov_intrusion_mm3"] = {}
    for lens in LENSES:
        for var in CM3_LENS:
            res["fov_intrusion_mm3"][f"{lens} HQ lens in a Module 3 {var}'s view"] = round(fov_intrusion(p, lens, var), 1)
    res["pitch_for_no_intrusion_mm"] = {f"{lens} beside Module 3 {var}": round(clear_pitch(p, lens, var), 1)
                                        for lens in LENSES for var in CM3_LENS}
    res["screw_stack_mm"] = screw_stacks(p)
    bb = mount.val().BoundingBox()
    res["mount"] = {
        "size_mm": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
        "volume_cm3": round(mount.val().Volume() / 1000, 1),
        "optical_axes": [[x, 0.0, p.axis_z] for x in p.stations],
        "stand_stud_xy": list(p.stand_xy),
    }
    tol = 1e-3
    res["pass"] = all(v <= tol for v in ov.values())
    return res


# Parts shown in the assembly exports, and their colours.
COLORS = {
    "mount": (0.36, 0.42, 0.48), "pi5": (0.18, 0.55, 0.34), "cooler": (0.72, 0.74, 0.78),
    "hq_pcb": (0.12, 0.48, 0.25), "hq_conn": (0.85, 0.85, 0.80), "hq_mount": (0.13, 0.13, 0.14),
    "hq_lens": (0.08, 0.08, 0.09), "cm3_pcb": (0.12, 0.48, 0.25), "cm3_back": (0.85, 0.85, 0.80),
    "cm3_lens": (0.10, 0.10, 0.11),
}


def color_for(name: str) -> tuple:
    return COLORS[name.rsplit("_", 1)[0] if name[-2:] in ("_L", "_R") else name]


def export(p: Params, mount: cq.Workplane, checks: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(mount, str(out / "mount.step"))
    cq.exporters.export(mount, str(out / "mount.stl"), tolerance=0.02, angularTolerance=0.1)
    for name, cams in (("assembly_hq_cm3", ["hq", "cm3"]), ("assembly_2x_cm3", ["cm3", "cm3"])):
        assy = cq.Assembly(name=name)
        assy.add(mount, name="mount", color=cq.Color(*COLORS["mount"]))
        assy.add(make_pi5(p), name="pi5", color=cq.Color(*COLORS["pi5"]))
        assy.add(make_active_cooler(p), name="cooler", color=cq.Color(*COLORS["cooler"]))
        for k, v in build_config(p, cams)["parts"].items():
            assy.add(v, name=k, color=cq.Color(*color_for(k)))
        assy.export(str(out / f"{name}.step"))
    d = asdict(p)
    (out / "params.json").write_text(json.dumps(d, indent=2) + "\n")
    (out / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--out", type=Path, default=EXPORTS)
    args = ap.parse_args()
    p = Params()
    mount = make_mount(p)
    checks = run_checks(p, mount)
    print(json.dumps(checks, indent=2))
    if not args.check_only:
        export(p, mount, checks, args.out)
        print(f"exported to {args.out}")
    if not checks["pass"]:
        raise SystemExit("interference found; see overlap_mm3 above")


if __name__ == "__main__":
    main()
