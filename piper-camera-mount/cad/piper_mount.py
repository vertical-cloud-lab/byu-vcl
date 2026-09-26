#!/usr/bin/env python3
"""AgileX PiPER wrist camera mount: parametric CadQuery model.

Puts a Raspberry Pi 5, a Raspberry Pi HQ Camera (with the official 6 mm CS-mount lens)
and, optionally, a Camera Module 3 Wide on the PiPER's two-finger gripper. The HQ Camera
is for repeatable positioning; the Wide is for streaming. The printed parts are:

    bracket   -X side: a camera plate that also sits on the finger plate's side tab
              (two M3 tapped holes), plus half of a clamp collar round the gripper body
    carrier   +X side: the other half of the collar and a plate for the Pi 5
    spacers   4 x Pi 5 standoffs

The cameras hang on one side of the gripper and the Pi on the other, so the load on J6
roughly balances, and the collar (4 x M3 across its split) ties them together. The tab
screws stop the whole ring turning on the gripper body.

Coordinates are those of AgileX's own gripper STEP (see reference.py), so the real
gripper drops into every check and render untransformed:

    +Y   from the fingertips toward the arm. The J6 axis runs along Y through
         (x, z) = (ax_x, ax_z); the J6 flange face is at y = 64.98.
    Z    the direction the fingers travel.
    -X   the side with the finger plate's tab.

Nothing is allowed behind the flange face (y > 64), so the mount can never reach the J6
housing or link 5, whatever J5 and J6 do.

    python piper_mount.py               # build, run checks, export
    python piper_mount.py --check-only  # checks only, write nothing
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path

import cadquery as cq

import reference

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"


@dataclass
class Params:
    # --- PiPER gripper, measured from AgileX_Gripper.STEP ---------------------------
    ax_x: float = -7.91             # J6 axis
    ax_z: float = 1.92
    body_r: float = 28.5            # the O57 motor housing, back cover and flange
    plate_back_y: float = 14.48     # back face of the finger plate and of its tab
    body_end_y: float = 47.98       # end of the motor housing; a 0.2 mm groove follows
    flange_face_y: float = 64.98    # J6 face: nothing may go behind it
    tab_holes: tuple = ((-45.91, 7.92), (-45.91, -4.08))   # M3 tapped, 6.5 deep, from y = 14.48
    tab_depth: float = 6.5
    y_max: float = 63.5             # Pi 5 edge; its USB-C socket reaches 1 mm further

    # --- collar ------------------------------------------------------------------
    bore_clear: float = 0.15        # per side; the split closes up as the clamp screws tighten
    collar_wall: float = 5.0
    collar_y0: float = 14.5
    collar_y1: float = 46.0
    split_gap: float = 1.0          # between the two halves, so tightening squeezes the body
    ear_w: float = 9.0              # each half's ear, along X from the split
    ear_z0: float = 25.0            # ears run from here out to ear_z1, measured from the axis
    ear_z1: float = 44.0
    clamp_r: float = 38.65          # clamp screw axes, from the axis along Z
    clamp_y: tuple = (22.0, 38.5)
    clamp_head_seat: float = 5.5    # carrier side: screw head seat, from the split
    m3_clear_d: float = 3.4
    m3_head_cb_d: float = 6.5
    m3_nut_af: float = 5.8          # 5.5 + 0.3, as the OT-2 lid mount after its fit study
    m3_nut_depth: float = 3.0
    clamp_screw_len: float = 16.0

    # --- bracket (-X) ------------------------------------------------------------
    plate_t: float = 6.0            # camera plate; its front face is also the tab pad
    plate_x0: float = -93.0
    plate_x1: float = -37.4         # 1 mm clear of the O57 body
    plate_z0: float = -34.0         # from the axis
    plate_z1: float = 49.0
    web_x0: float = -51.0           # the block joining the plate to the collar
    web_z: float = 16.0             # half height
    access_d: float = 7.0           # hex-key channels down to the two tab screws
    tab_screw_len: float = 12.0

    # --- HQ Camera (CS mount), official drawing; connector and tripod foot face -Z
    hq_x: float = -71.0
    hq_dz: float = 0.0              # from the axis
    hq_standoff: float = 4.0
    hq_board: float = 38.0
    hq_hole_pitch: float = 30.0
    hq_pcb_t: float = 1.4
    hq_cs_seat: float = 14.43       # PCB front face to the CS lens seat (18.58 - 2.75 - 1.4)
    hq_hole_d: float = 37.0         # through the plate: the O36 back-focus ring
    m25_clear_d: float = 2.8
    boss_d: float = 5.5
    # Raspberry Pi 6 mm CS-mount lens (PT361060M3MP12): O30 x 34 mm, 53 g (maker's figures).
    lens_od: float = 30.0
    lens_len: float = 34.0
    lens_thread: float = 4.0        # estimate: thread inside the mount
    lens_f: float = 6.0

    # --- Camera Module 3 Wide, official drawing; connector faces +Z --------------------
    cm_x: float = -71.0
    cm_standoff: float = 2.5
    cm_w: float = 25.0
    cm_h: float = 23.862
    cm_lens_from_top: float = 9.462     # lens centre from the edge away from the connector
    cm_pcb_t: float = 1.12
    cm_lens_h: float = 8.3              # lens tip above the PCB front face
    m2_clear_d: float = 2.4
    cm_hole_d: float = 13.0             # through the plate, round the 8.5 mm lens module

    # --- carrier (+X) and Pi 5 ---------------------------------------------------------
    carrier_x0: float = 27.0        # inner face; 1.9 mm clear of the finger plate's edge
    carrier_t: float = 4.0
    carrier_y0: float = 8.0
    web2_z: float = 24.0            # carrier web half height: keeps ring overhangs at <= 45 deg
    pi_standoff: float = 5.0
    m25_nut_af: float = 5.3
    m25_nut_h: float = 2.3

    toe_deg: float = 0.0            # turn both cameras toward the gripper axis (about Z)

    # ------------------------------------------------------------------------------
    @property
    def bore_r(self) -> float:
        return self.body_r + self.bore_clear

    @property
    def collar_r(self) -> float:
        return self.bore_r + self.collar_wall

    @property
    def plate_y1(self) -> float:
        return self.collar_y0 + self.plate_t

    @property
    def cm_dz(self) -> float:
        """CM3 Wide lens centre above the axis: its board clears the HQ board by 2.5 mm."""
        return self.hq_dz + self.hq_board / 2 + 2.5 + self.cm_lens_from_top

    @property
    def pi_x(self) -> float:
        """Underside of the Pi 5 board."""
        return self.carrier_x0 + self.carrier_t + self.pi_standoff


# --- helpers ---------------------------------------------------------------------------

def box(x0, x1, y0, y1, z0, z1) -> cq.Workplane:
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_y(d, y0, y1, x, z) -> cq.Workplane:
    """Cylinder along Y."""
    return cq.Workplane("XZ").circle(d / 2).extrude(-(y1 - y0)).translate((x, y0, z))


def cyl_x(d, x0, x1, y, z) -> cq.Workplane:
    return cq.Workplane("YZ").circle(d / 2).extrude(x1 - x0).translate((x0, y, z))


def hex_x(af, x0, x1, y, z) -> cq.Workplane:
    """Hex prism along X, a vertex toward +Y (the build direction of the bracket)."""
    return (cq.Workplane("YZ").polygon(6, af / math.cos(math.pi / 6)).extrude(x1 - x0)
            .rotate((0, 0, 0), (1, 0, 0), 30).translate((x0, y, z)))


def cyl_z(d, z0, z1, x=0.0, y=0.0) -> cq.Workplane:
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def lbox(x0, x1, y0, y1, z0, z1) -> cq.Workplane:
    return box(x0, x1, y0, y1, z0, z1)


def ring_y(r_in, r_out, y0, y1, x, z) -> cq.Workplane:
    return cyl_y(2 * r_out, y0, y1, x, z).cut(cyl_y(2 * r_in, y0 - 1, y1 + 1, x, z))


# --- camera stations ----------------------------------------------------------------------
# Each camera is built in its own frame: optical axis along local -Z, PCB front face at
# local z = 0, connector side toward local -Y. `place` then puts it on the plate.

def station_frame(p: Params, x: float, dz: float, standoff: float, roll: float):
    """Returns a function that maps a camera-frame Workplane into the gripper frame."""
    y_front = p.plate_y1 + standoff

    def place(wp: cq.Workplane) -> cq.Workplane:
        wp = wp.rotate((0, 0, 0), (0, 0, 1), roll)          # 0: connector up; 180: down
        wp = wp.rotate((0, 0, 0), (1, 0, 0), -90)           # local -Z (lens) -> -Y
        wp = wp.rotate((0, 0, 0), (0, 0, 1), p.toe_deg)     # toe-in toward +X
        return wp.translate((x, y_front, p.ax_z + dz))
    return place


HQ_ROLL, CM_ROLL = 180.0, 0.0


def hq_place(p):
    return station_frame(p, p.hq_x, p.hq_dz, p.hq_standoff, HQ_ROLL)


def cm_place(p):
    return station_frame(p, p.cm_x, p.cm_dz, p.cm_standoff, CM_ROLL)


def hq_holes(p):
    h = p.hq_hole_pitch / 2
    return [(sx * h, sy * h) for sx in (-1, 1) for sy in (-1, 1)]


def cm_holes(p):
    top = p.cm_lens_from_top - 2.0           # holes 2 mm in from the edge away from the connector
    return [(sx * 10.5, y) for sx in (-1, 1) for y in (top, top - 12.5)]


def make_hq_camera_local(p: Params) -> dict[str, cq.Workplane]:
    b, t = p.hq_board, p.hq_pcb_t
    pcb = lbox(-b / 2, b / 2, -b / 2, b / 2, 0, t).edges("|Z").fillet(1.0)
    for x, y in hq_holes(p):
        pcb = pcb.cut(cyl_z(2.5, -1, t + 1, x, y))
    pcb = pcb.union(lbox(-10, 10, -b / 2 + 0.55, -b / 2 + 6.25, t, t + 2.75))            # FPC connector
    seat = -p.hq_cs_seat
    mount = cyl_z(36.0, seat, seat + 5.8).union(cyl_z(30.75, seat + 5.8, 0))              # ring + body
    mount = mount.union(lbox(-6.985, 6.985, -b / 2 - 11.2, -b / 2 + 4.0, -12.0, 0))      # tripod foot
    mount = mount.union(lbox(-5.08, 5.08, b / 2 - 3.5, b / 2 + 1.5, seat + 1.0, seat + 6.0))  # focus lock
    lens = cyl_z(25.4, seat, seat + p.lens_thread)                                        # thread, inside
    lens = lens.union(cyl_z(p.lens_od, seat - (p.lens_len - p.lens_thread), seat))
    return {"hq_pcb": pcb, "hq_mount": mount, "hq_lens": lens}


def make_cm_camera_local(p: Params) -> dict[str, cq.Workplane]:
    top, bot = p.cm_lens_from_top, -(p.cm_h - p.cm_lens_from_top)   # +Y edge, connector edge
    pcb = lbox(-p.cm_w / 2, p.cm_w / 2, bot, top, 0, p.cm_pcb_t)
    for x, y in cm_holes(p):
        pcb = pcb.cut(cyl_z(2.2, -1, 2, x, y))
    pcb = pcb.union(lbox(-10, 10, bot, bot + 5.71, p.cm_pcb_t, p.cm_pcb_t + 2.75))       # FPC connector
    module = lbox(-4.25, 4.25, -4.25, 4.25, -4.07, 0).union(cyl_z(6.95, -p.cm_lens_h, -4.07))
    return {"cm_pcb": pcb, "cm_module": module}


def hq_station_cuts(p: Params) -> cq.Workplane:
    """Lens hole, tripod-foot and focus-lock notches, and screw holes, in the camera frame."""
    s = p.hq_standoff
    cut = cyl_z(p.hq_hole_d, -80, -s + 0.5)
    cut = cut.union(lbox(-8.0, 8.0, -p.hq_board / 2 - 12.2, -14.0, -80, -s + 0.5))        # tripod foot
    cut = cut.union(lbox(-6.0, 6.0, 14.0, p.hq_board / 2 + 2.5, -80, -s + 0.5))          # focus lock
    for x, y in hq_holes(p):
        cut = cut.union(cyl_z(p.m25_clear_d, -80, 5, x, y))
        cut = cut.union(cyl_z(5.0, -80, -s - p.plate_t + 2.0, x, y))                     # head counterbore
    return cut


def cm_station_cuts(p: Params) -> cq.Workplane:
    s = p.cm_standoff
    cut = cyl_z(p.cm_hole_d, -80, -s + 0.5)
    for x, y in cm_holes(p):
        cut = cut.union(cyl_z(p.m2_clear_d, -80, 5, x, y))
        cut = cut.union(cyl_z(4.2, -80, -s - p.plate_t + 2.0, x, y))
    return cut


def bosses(holes, d, s) -> cq.Workplane:
    """Standoffs from the PCB plane back to (and through) the plate; clipped later."""
    out = None
    for x, y in holes:
        c = cyl_z(d, -s - 30, 0, x, y)
        out = c if out is None else out.union(c)
    return out


# --- printed parts ------------------------------------------------------------------------

def collar_half(p: Params, side: int) -> cq.Workplane:
    """side = -1: the bracket's half (x < axis); +1: the carrier's half."""
    y0 = p.collar_y0 if side < 0 else p.collar_y0 + 0.5
    ring = ring_y(p.bore_r, p.collar_r, y0, p.collar_y1, p.ax_x, p.ax_z)
    g = p.split_gap / 2
    keep = (box(p.ax_x - 200, p.ax_x - g, -50, 100, -200, 200) if side < 0
            else box(p.ax_x + g, p.ax_x + 200, -50, 100, -200, 200))
    ears = None
    for sz in (-1, 1):
        z0, z1 = sorted((p.ax_z + sz * p.ear_z0, p.ax_z + sz * p.ear_z1))
        x0, x1 = (p.ax_x - p.ear_w, p.ax_x - g) if side < 0 else (p.ax_x + g, p.ax_x + p.ear_w)
        e = box(x0, x1, y0, p.collar_y1, z0, z1)
        ears = e if ears is None else ears.union(e)
    return ring.union(ears).intersect(keep)


def make_bracket(p: Params) -> cq.Workplane:
    y0, y1 = p.collar_y0, p.plate_y1
    zc = p.ax_z
    plate = box(p.plate_x0, p.plate_x1, y0, y1, zc + p.plate_z0, zc + p.plate_z1).edges("|Y").fillet(4.0)
    web = box(p.web_x0, p.ax_x - p.split_gap / 2, y0, p.collar_y1, zc - p.web_z, zc + p.web_z)
    part = plate.union(web).union(collar_half(p, -1))
    part = part.cut(cyl_y(2 * p.bore_r, y0 - 1, p.collar_y1 + 1, p.ax_x, zc))
    # Camera stations: standoff bosses, then the holes.
    hq, cm = hq_place(p), cm_place(p)
    back = box(-300, 300, y0, 300, -300, 300)       # clip bosses to behind the plate's front face
    part = part.union(hq(bosses(hq_holes(p), p.boss_d, p.hq_standoff)).intersect(back))
    part = part.union(cm(bosses(cm_holes(p), 4.5, p.cm_standoff)).intersect(back))
    part = part.cut(hq(hq_station_cuts(p))).cut(cm(cm_station_cuts(p)))
    # The two tab screws: clearance through the pad, and hex-key channels down to their heads.
    for x, z in p.tab_holes:
        part = part.cut(cyl_y(p.m3_clear_d, y0 - 1, y1 + 1, x, z))
        part = part.cut(cyl_y(p.access_d, y1, p.collar_y1 + 1, x, z))
    # Clamp screws across the split: nuts in the bracket's ears.
    for sz in (-1, 1):
        for y in p.clamp_y:
            z = zc + sz * p.clamp_r
            part = part.cut(cyl_x(p.m3_clear_d, p.ax_x - p.ear_w - 1, p.ax_x, y, z))
            part = part.cut(hex_x(p.m3_nut_af, p.ax_x - p.ear_w - 1, p.ax_x - p.ear_w + p.m3_nut_depth, y, z))
    return part


def make_carrier(p: Params) -> cq.Workplane:
    zc = p.ax_z
    y0 = p.collar_y0 + 0.5
    x0, x1 = p.carrier_x0, p.carrier_x0 + p.carrier_t
    plate = box(x0, x1, p.carrier_y0, p.y_max, zc - 44.0, zc + 44.0).edges("|X").fillet(4.0)
    web = box(p.ax_x + 15.0, x0 + 0.5, y0, p.collar_y1, zc - p.web2_z, zc + p.web2_z)
    part = plate.union(web).union(collar_half(p, +1))
    # 45 degree gussets under the ears, so the carrier prints plate-down without supports.
    for sz in (-1, 1):
        zt, zb = zc + sz * p.ear_z1, zc + sz * p.web2_z
        xe = p.ax_x + p.ear_w
        pts = [(xe, zt), (xe, zb), (xe + abs(zt - zb), zb)]
        g = (cq.Workplane("XZ").polyline(pts).close().extrude(-(p.collar_y1 - y0)).translate((0, y0, 0)))
        part = part.union(g)
    part = part.cut(cyl_y(2 * p.bore_r, y0 - 1, p.collar_y1 + 1, p.ax_x, zc))
    # Clamp screws: heads seat 5.5 mm from the split; counterbored channels open toward +X.
    for sz in (-1, 1):
        for y in p.clamp_y:
            z = zc + sz * p.clamp_r
            part = part.cut(cyl_x(p.m3_clear_d, p.ax_x, p.ax_x + p.clamp_head_seat + 1, y, z))
            part = part.cut(cyl_x(p.m3_head_cb_d, p.ax_x + p.clamp_head_seat, x1 + 1, y, z))
    # Pi 5: M2.5 through the plate, nuts trapped in its inner face.
    for y, z in pi_holes(p):
        part = part.cut(cyl_x(p.m25_clear_d, x0 - 1, x1 + 1, y, z))
        part = part.cut(hex_x(p.m25_nut_af, x0 - 1, x0 + p.m25_nut_h, y, z))
    return part


def make_spacers(p: Params) -> cq.Workplane:
    out = None
    for i in range(4):
        s = cyl_z(6.0, 0, p.pi_standoff, i * 10.0).cut(cyl_z(p.m25_clear_d, -1, p.pi_standoff + 1, i * 10.0))
        out = s if out is None else out.union(s)
    return out


# --- Pi 5 ------------------------------------------------------------------------------------
# Board frame (u, v, w): u along the 85 mm edge toward the USB/Ethernet end, v along the 56 mm
# edge away from the USB-C / micro-HDMI / camera-connector edge, w up from the board's underside.
# On the carrier: u -> +Z, v -> -Y (the USB-C edge faces the arm), w -> +X.

PI_U0 = -42.5   # u = 0 sits this far below the axis


def pi_holes(p: Params) -> list[tuple[float, float]]:
    return [(p.y_max - v, p.ax_z + PI_U0 + u) for u in (3.5, 61.5) for v in (3.5, 52.5)]


def make_pi5_local() -> cq.Workplane:
    board = lbox(0, 85, 0, 56, 0, 1.6).edges("|Z").fillet(3.0)
    for u in (3.5, 61.5):
        for v in (3.5, 52.5):
            board = board.cut(cyl_z(2.7, -1, 3, u, v))
    top = 1.6
    parts = [
        lbox(64.0, 85.0 + 2.0, 2.5, 18.5, top, top + 13.5),     # Ethernet
        lbox(69.5, 85.0 + 2.0, 22.5, 35.5, top, top + 16.0),    # USB 3
        lbox(69.5, 85.0 + 2.0, 40.5, 53.5, top, top + 16.0),    # USB 2
        lbox(7.0, 58.0, 50.0, 55.0, top, top + 8.5),            # GPIO header
        lbox(4.0, 56.0, 12.0, 50.0, top, top + 10.0),           # Active Cooler
        lbox(6.7, 15.7, -1.0, 6.5, top, top + 3.3),             # USB-C
        lbox(22.8, 28.8, -1.0, 6.5, top, top + 3.0),            # micro HDMI 0
        lbox(36.2, 42.2, -1.0, 6.5, top, top + 3.0),            # micro HDMI 1
        lbox(45.5, 48.5, 4.0, 17.0, top, top + 4.0),            # CAM/DISP 0 and 1
        lbox(50.5, 53.5, 4.0, 17.0, top, top + 4.0),
    ]
    for c in parts:
        board = board.union(c)
    return board


def place_pi(p: Params, wp: cq.Workplane) -> cq.Workplane:
    # (u, v, w) -> (w, -v, u): a 90 degree turn about Y, then 180 about Z (see the frame note).
    wp = wp.rotate((0, 0, 0), (0, 1, 0), -90).rotate((0, 0, 0), (0, 0, 1), 180)
    return wp.translate((p.pi_x, p.y_max, p.ax_z + PI_U0))


def place_spacers(p: Params) -> cq.Workplane:
    out = None
    x = p.carrier_x0 + p.carrier_t
    for y, z in pi_holes(p):
        s = cyl_x(6.0, x, x + p.pi_standoff, y, z).cut(cyl_x(p.m25_clear_d, x - 1, x + p.pi_standoff + 1, y, z))
        out = s if out is None else out.union(s)
    return out


# --- optics -----------------------------------------------------------------------------------

IMX477 = (6.287, 4.712)       # active area, mm
CM3W_FOV = (102.0, 67.0)      # degrees, Raspberry Pi's figures


def hq_fov(p: Params) -> tuple[float, float]:
    return tuple(2 * math.degrees(math.atan(s / 2 / p.lens_f)) for s in IMX477)


def optical_axes(p: Params) -> dict[str, tuple[cq.Vector, cq.Vector]]:
    """(lens front point, unit view direction) for each camera."""
    d = cq.Vector(math.sin(math.radians(p.toe_deg)), -math.cos(math.radians(p.toe_deg)), 0)
    hq_front = p.hq_cs_seat + p.lens_len - p.lens_thread
    hq_o = cq.Vector(p.hq_x, p.plate_y1 + p.hq_standoff, p.ax_z + p.hq_dz) + d * hq_front
    cm_o = cq.Vector(p.cm_x, p.plate_y1 + p.cm_standoff, p.ax_z + p.cm_dz) + d * p.cm_lens_h
    return {"hq": (hq_o, d), "cm3w": (cm_o, d)}


def view_pyramid(o: cq.Vector, d: cq.Vector, hfov: float, vfov: float, depth: float,
                 aperture: float = 0.0) -> cq.Workplane:
    """Frustum of what a camera sees, out to `depth` along its axis."""
    up = cq.Vector(0, 0, 1)
    right = d.cross(up).normalized()
    th, tv = math.tan(math.radians(hfov / 2)), math.tan(math.radians(vfov / 2))
    near = [o + right * (sx * aperture) + up * (sy * aperture) for sx in (-1, 1) for sy in (-1, 1)]
    c = o + d * depth
    far = [c + right * (sx * (aperture + depth * th)) + up * (sy * (aperture + depth * tv))
           for sx in (-1, 1) for sy in (-1, 1)]
    order = [0, 1, 3, 2]
    w0 = cq.Wire.makePolygon([near[i] for i in order], close=True)
    w1 = cq.Wire.makePolygon([far[i] for i in order], close=True)
    return cq.Workplane("XY").add(cq.Solid.makeLoft([w0, w1], True))


# --- checks ------------------------------------------------------------------------------------

def overlap(a: cq.Workplane, b: cq.Workplane) -> float:
    """Volume (mm^3) shared by two parts, solid by solid. AgileX's gripper solids overlap each
    other (the back cover's spigot sits inside the flange), and a boolean against the flange
    solid returns the whole of the other part even when the two are far apart, so pairs that
    don't touch (by BRepExtrema distance, which is reliable here) count as zero."""
    total = 0.0
    for sa in a.val().Solids():
        for sb in b.val().Solids():
            if sa.distance(sb) > 1e-6:
                continue
            total += sum(s.Volume() for s in sa.intersect(sb).Solids())
    return total


def gap(a: cq.Workplane, b: cq.Workplane) -> float:
    return a.val().distance(b.val())


def axis_in_view_beyond_tips(p: Params, fingertip_y: float = -77.52) -> float:
    """How far past the fingertips a point on the gripper axis enters the HQ Camera's view."""
    (o, d) = optical_axes(p)["hq"]
    half = math.radians(hq_fov(p)[0] / 2)
    for i in range(0, 3000):
        y = fingertip_y - i * 0.5
        v = cq.Vector(p.ax_x, y, p.ax_z) - o
        ang = math.acos(max(-1.0, min(1.0, v.normalized().dot(d))))
        if ang <= half:
            return fingertip_y - y
    return float("nan")


def run_checks(p: Params, parts: dict[str, cq.Workplane]) -> dict:
    solids = ("bracket", "carrier", "hq_pcb", "hq_mount", "hq_lens", "cm_pcb", "cm_module", "pi5", "pi_spacers")
    res: dict = {"overlap_mm3": {}, "gap_mm": {}, "view": {}, "extent_mm": {}}
    for opening, tag in ((0.0, "closed"), (100.0, "fully open")):
        g = reference.gripper(opening)
        for name in solids:
            res["overlap_mm3"][f"{name} vs gripper fingers ({tag})"] = overlap(parts[name], g["fingers"])
        res["gap_mm"][f"mount to fingers ({tag})"] = min(
            gap(parts[n], g["fingers"]) for n in ("bracket", "carrier", "hq_lens", "hq_mount", "cm_module"))
    g = reference.gripper()
    for name in solids:
        res["overlap_mm3"][f"{name} vs gripper body"] = overlap(parts[name], g["body"])
    pairs = [("bracket", "carrier"), ("bracket", "hq_pcb"), ("bracket", "hq_mount"), ("bracket", "hq_lens"),
             ("bracket", "cm_pcb"), ("bracket", "cm_module"), ("carrier", "pi_spacers"), ("carrier", "pi5"),
             ("pi_spacers", "pi5"), ("hq_mount", "cm_module"), ("hq_pcb", "cm_pcb")]
    for a, b in pairs:
        res["overlap_mm3"][f"{a} vs {b}"] = overlap(parts[a], parts[b])
    res["gap_mm"]["bracket to gripper body"] = gap(parts["bracket"], g["body"])
    res["gap_mm"]["carrier to gripper body"] = gap(parts["carrier"], g["body"])
    res["gap_mm"]["collar halves (split)"] = gap(parts["bracket"], parts["carrier"])
    # Fields of view against the fingers, 250 mm deep.
    axes = optical_axes(p)
    hfov, vfov = hq_fov(p)
    cones = {"hq": view_pyramid(*axes["hq"], hfov, vfov, 250.0, aperture=6.0),
             "cm3w": view_pyramid(*axes["cm3w"], *CM3W_FOV, 250.0, aperture=1.5)}
    for opening, tag in ((0.0, "closed"), (100.0, "fully open")):
        f = reference.gripper(opening)["fingers"]
        for k, c in cones.items():
            res["view"][f"{k} view vs fingers ({tag}), mm3"] = round(overlap(c, f), 1)
    res["view"]["HQ field of view (deg, H x V)"] = [round(v, 1) for v in hfov_vfov(p)]
    res["view"]["gripper axis enters the HQ view this far past the fingertips (mm)"] = round(
        axis_in_view_beyond_tips(p), 1)
    res["view"]["HQ lens front behind the fingertips (mm)"] = round(axes["hq"][0].y - (-77.52), 1)
    res["view"]["optical axes off the gripper axis (mm)"] = round(p.ax_x - p.hq_x, 1)
    everything = cq.Workplane("XY").add(cq.Compound.makeCompound([parts[n].val() for n in solids]))
    bb = everything.val().BoundingBox()
    res["extent_mm"] = {
        "rearmost point (must be < flange face 64.98)": round(bb.ymax, 2),
        "max radius from the J6 axis": round(max(
            math.hypot(x - p.ax_x, z - p.ax_z) for x in (bb.xmin, bb.xmax) for z in (bb.zmin, bb.zmax)), 1),
        "x": [round(bb.xmin, 1), round(bb.xmax, 1)], "y": [round(bb.ymin, 1), round(bb.ymax, 1)],
        "z": [round(bb.zmin, 1), round(bb.zmax, 1)],
    }
    res["printed_volume_cm3"] = {n: round(parts[n].val().Volume() / 1000, 1) for n in ("bracket", "carrier", "spacers")}
    tol = 1e-3
    res["pass"] = all(v <= tol for v in res["overlap_mm3"].values()) and bb.ymax < p.flange_face_y
    return res


def hfov_vfov(p: Params):
    return hq_fov(p)


# --- build / export -----------------------------------------------------------------------------

def build(p: Params) -> dict[str, cq.Workplane]:
    hq, cm = hq_place(p), cm_place(p)
    parts = {
        "bracket": make_bracket(p),
        "carrier": make_carrier(p),
        "spacers": make_spacers(p),
        "pi_spacers": place_spacers(p),
        "pi5": place_pi(p, make_pi5_local()),
    }
    parts.update({k: hq(v) for k, v in make_hq_camera_local(p).items()})
    parts.update({k: cm(v) for k, v in make_cm_camera_local(p).items()})
    return parts


ASSEMBLY = ("bracket", "carrier", "pi_spacers", "hq_pcb", "hq_mount", "hq_lens", "cm_pcb", "cm_module", "pi5")
COLORS = {
    "bracket": (0.93, 0.45, 0.13), "carrier": (0.93, 0.45, 0.13), "pi_spacers": (0.93, 0.45, 0.13),
    "spacers": (0.93, 0.45, 0.13),
    "hq_pcb": (0.12, 0.48, 0.25), "hq_mount": (0.13, 0.13, 0.14), "hq_lens": (0.08, 0.08, 0.09),
    "cm_pcb": (0.12, 0.48, 0.25), "cm_module": (0.1, 0.1, 0.1), "pi5": (0.18, 0.55, 0.34),
}


def print_orientation(name: str, part: cq.Workplane) -> cq.Workplane:
    """bracket: camera-plate face down (build +Y); carrier: Pi plate down (build -X)."""
    if name == "bracket":
        part = part.rotate((0, 0, 0), (1, 0, 0), 90)        # +Y -> +Z
    elif name == "carrier":
        part = part.rotate((0, 0, 0), (0, 1, 0), 90)        # -X -> +Z
    bb = part.val().BoundingBox()
    return part.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def export(p: Params, parts: dict, checks: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name in ("bracket", "carrier", "spacers"):
        cq.exporters.export(parts[name], str(out / f"{name}.step"))
        cq.exporters.export(print_orientation(name, parts[name]), str(out / f"{name}.stl"),
                            tolerance=0.02, angularTolerance=0.1)
    assy = cq.Assembly(name="piper_camera_mount")
    for name in ASSEMBLY:
        assy.add(parts[name], name=name, color=cq.Color(*COLORS[name]))
    assy.export(str(out / "assembly.step"))
    (out / "params.json").write_text(json.dumps(asdict(p), indent=2) + "\n")
    (out / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--out", type=Path, default=EXPORTS)
    ap.add_argument("--toe", type=float, default=None, help="camera toe-in, degrees")
    args = ap.parse_args()
    p = Params()
    if args.toe is not None:
        p.toe_deg = args.toe
    parts = build(p)
    checks = run_checks(p, parts)
    print(json.dumps(checks, indent=2))
    if not args.check_only:
        export(p, parts, checks, args.out)
        print(f"exported to {args.out}")
    if not checks["pass"]:
        raise SystemExit("interference found; see overlap_mm3 above")


if __name__ == "__main__":
    main()
