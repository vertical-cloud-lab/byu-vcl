#!/usr/bin/env python3
"""AgileX PiPER wrist camera mount: parametric CadQuery model.

Puts a Raspberry Pi 5, a Raspberry Pi HQ Camera (with the official 6 mm CS-mount lens)
and, optionally, a Camera Module 3 Wide on the PiPER's two-finger gripper. The HQ Camera
is for repeatable positioning; the Wide is for streaming. The printed parts are:

    bracket    -X side: a pad on the finger plate's side tab (AgileX's "reserved camera
               mounting platform", two M3 brass inserts), half of a clamp collar round
               the gripper body, and a web that carries the camera pod
    pod        the camera plate: HQ Camera and Camera Module 3 Wide, turned toe_deg toward
               the gripper axis and set back so the lenses sit behind the finger plate's
               front face. Two M3 screws hold it to the web
    carrier    +X side: the other half of the collar and a plate for the Pi 5
    spacers    4 x Pi 5 standoffs
    tag_wedge  2 x small wedges that turn a 5 mm AprilTag on each finger toward the HQ Camera

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

The cameras are built in a "station" frame: origin at the front face of the HQ Camera's
board, optical axis along -Y, Z up. `to_world` turns that frame toe_deg about Z (toward
+X, the gripper) and moves it into place, so the pod, its holes and the camera models
all turn together.

    python piper_mount.py               # build, run checks, export
    python piper_mount.py --check-only  # checks only, write nothing
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
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
    body_end_y: float = 47.98       # end of the motor housing; the jumper sockets follow (y 48-54, at +/-Z)
    flange_face_y: float = 64.98    # J6 face: nothing may go behind it
    tab_holes: tuple = ((-45.91, 7.92), (-45.91, -4.08))   # M3 brass inserts, 38.0 mm off the axis
    tab_depth: float = 6.5
    y_max: float = 63.5             # Pi 5 edge; its USB-C socket reaches 1 mm further

    # --- collar ------------------------------------------------------------------
    bore_clear: float = 0.15        # per side; the split closes up as the clamp screws tighten
    collar_wall: float = 5.0
    collar_y0: float = 14.5
    collar_y1: float = 46.0         # stops 2 mm short of the jumper sockets in the back cover
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

    # --- bracket (-X): the pad on the tab, and the web the pod sits on --------------
    pad_t: float = 6.0              # the pad on the tab
    web_x0: float = -51.0           # outer face of the web: 1.6 mm outside the hex-key channels
    web_x1_rear: float = -38.0      # inner face of the web behind the collar (1.6 mm off the flange)
    web_z: float = 20.0             # half height
    access_d: float = 7.0           # hex-key channels down to the two tab screws (through the pod too)
    tab_screw_len: float = 12.0

    # --- camera pod ------------------------------------------------------------------
    toe_deg: float = 17.0           # both cameras turned toward the gripper axis (about Z)
    hq_front_x: float = -68.0       # HQ lens front, centre: 31.9 mm further back than the first version,
    hq_front_y: float = 12.0        # and behind the finger plate's front face (y = -4.5)
    hq_roll: float = 90.0           # ribbon connector toward the gripper: the long side of the image runs
                                    # along the finger travel (the fingers stay in view to 60 mm open)
    pod_t: float = 6.0              # camera plate
    pod_x_out: float = -25.0        # station frame, from the HQ axis: outer edge
    pod_z0: float = -24.0           # below the HQ board
    pod_z1: float = 57.0            # above the Camera Module 3 Wide
    tongue_x0: float = 18.0         # the tongue that sits on the web
    tongue_x1: float = 40.0
    tongue_z: float = 21.0
    pod_screws: tuple = ((34.0, 15.0), (34.0, -15.0))   # station x, z: 2 x M3 x 16 into nuts in the web
    pod_screw_len: float = 16.0
    pod_nut_y: float = -18.3        # station y of the nut's centre

    # --- HQ Camera (CS mount), official drawing -------------------------------------
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
    cm_gap: float = 10.5            # its board's lower edge above the HQ board's upper edge: keeps the
                                    # HQ lens out of the bottom of the Wide's picture
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

    # --- finger tags ---------------------------------------------------------------------
    tag_size: float = 5.0           # AprilTag 36h11, black edge to black edge
    tag_y: float = -60.0            # tag centre, 17.5 mm behind the fingertips
    tag_tilt: float = 35.0          # wedge angle: turns the tag from the finger's flank toward the camera

    # ------------------------------------------------------------------------------
    @property
    def bore_r(self) -> float:
        return self.body_r + self.bore_clear

    @property
    def collar_r(self) -> float:
        return self.bore_r + self.collar_wall

    @property
    def cm_dz(self) -> float:
        """CM3 Wide lens centre above the HQ axis."""
        return self.hq_board / 2 + self.cm_gap + self.cm_lens_from_top

    @property
    def hq_front_dist(self) -> float:
        """HQ board front face to the front of the 6 mm lens, along the optical axis."""
        return self.hq_cs_seat + self.lens_len - self.lens_thread

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


def hex_y(af, y0, y1, x, z) -> cq.Workplane:
    """Hex prism along Y, flats facing +/-Z."""
    return cq.Workplane("XZ").polygon(6, af / math.cos(math.pi / 6)).extrude(-(y1 - y0)).translate((x, y0, z))


def cyl_z(d, z0, z1, x=0.0, y=0.0) -> cq.Workplane:
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def lbox(x0, x1, y0, y1, z0, z1) -> cq.Workplane:
    return box(x0, x1, y0, y1, z0, z1)


def ring_y(r_in, r_out, y0, y1, x, z) -> cq.Workplane:
    return cyl_y(2 * r_out, y0, y1, x, z).cut(cyl_y(2 * r_in, y0 - 1, y1 + 1, x, z))


# --- the station frame ----------------------------------------------------------------------
# Station frame: origin at the HQ board's front face, optical axis -Y, Z up, +X toward the
# gripper before the toe-in turn. The pod's plate lies at y in [-hq_standoff - pod_t, -hq_standoff].

def station_origin(p: Params) -> cq.Vector:
    t = math.radians(p.toe_deg)
    L = p.hq_front_dist
    return cq.Vector(p.hq_front_x - L * math.sin(t), p.hq_front_y + L * math.cos(t), p.ax_z + p.hq_dz)


def to_world(p: Params, wp):
    """Station frame -> gripper frame: turn toe_deg about Z (lens toward +X), then move."""
    o = station_origin(p)
    return wp.rotate((0, 0, 0), (0, 0, 1), p.toe_deg).translate(o.toTuple())


def station_vec(p: Params, x: float, y: float, z: float) -> cq.Vector:
    t = math.radians(p.toe_deg)
    o = station_origin(p)
    return cq.Vector(o.x + x * math.cos(t) - y * math.sin(t), o.y + x * math.sin(t) + y * math.cos(t), o.z + z)


# Each camera is built in its own frame: optical axis along local -Z, PCB front face at
# local z = 0, connector side toward local -Y. These map it into the station frame.

CM_ROLL = 0.0


def hq_to_station(p: Params, wp):
    return wp.rotate((0, 0, 0), (0, 0, 1), p.hq_roll).rotate((0, 0, 0), (1, 0, 0), -90)


def cm_to_station(p: Params, wp):
    wp = wp.rotate((0, 0, 0), (0, 0, 1), CM_ROLL).rotate((0, 0, 0), (1, 0, 0), -90)
    return wp.translate((0, -(p.hq_standoff - p.cm_standoff), p.cm_dz))


def hq_place(p):
    return lambda wp: to_world(p, hq_to_station(p, wp))


def cm_place(p):
    return lambda wp: to_world(p, cm_to_station(p, wp))


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


def hq_keepout_local(p: Params, c: float = 1.5) -> cq.Workplane:
    """The HQ Camera and lens grown by c: what the bracket's web must stay out of."""
    b, seat = p.hq_board, -p.hq_cs_seat
    k = lbox(-b / 2 - c, b / 2 + c, -b / 2 - c, b / 2 + c, -c, p.hq_pcb_t + 3.0)
    k = k.union(cyl_z(36.0 + 2 * c, seat - c, 0))
    k = k.union(lbox(-6.985 - c, 6.985 + c, -b / 2 - 11.2 - c, -b / 2 + 4.0, -12.0 - c, 0))
    k = k.union(lbox(-5.08 - c, 5.08 + c, b / 2 - 3.5, b / 2 + 1.5 + c, seat + 1.0 - c, seat + 6.0 + c))
    k = k.union(cyl_z(p.lens_od + 2 * c, seat - (p.lens_len - p.lens_thread) - c, seat))
    return k


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
        cut = cut.union(cyl_z(5.0, -80, -s - p.pod_t + 2.0, x, y))                       # head counterbore
    return cut


def cm_station_cuts(p: Params) -> cq.Workplane:
    s = p.cm_standoff
    cut = cyl_z(p.cm_hole_d, -80, -s + 0.5)
    for x, y in cm_holes(p):
        cut = cut.union(cyl_z(p.m2_clear_d, -80, 5, x, y))
        cut = cut.union(cyl_z(4.2, -80, -s - p.pod_t + 2.0, x, y))
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


def pod_screw_axes(p: Params):
    """(point on the axis at the pod's back face, unit direction into the web) per pod screw."""
    t = math.radians(p.toe_deg)
    down = cq.Vector(math.sin(t), -math.cos(t), 0)          # station -Y
    return [(station_vec(p, x, -p.hq_standoff, z), down) for x, z in p.pod_screws]


def make_pod_local(p: Params) -> cq.Workplane:
    """The camera plate in the station frame (not yet turned or moved)."""
    s, t = p.hq_standoff, p.pod_t
    y0, y1 = -s - t, -s
    main = box(p.pod_x_out, p.tongue_x0 + 6.0, y0, y1, p.pod_z0, p.pod_z1).edges("|Y").fillet(4.0)
    tongue = box(p.tongue_x0, p.tongue_x1, y0, y1, -p.tongue_z, p.tongue_z).edges("|Y").fillet(3.0)
    part = main.union(tongue)
    back = box(-300, 300, y0, 300, -300, 300)       # clip bosses to behind the plate's front face
    part = part.union(hq_to_station(p, bosses(hq_holes(p), p.boss_d, p.hq_standoff)).intersect(back))
    part = part.union(cm_to_station(p, bosses(cm_holes(p), 4.5, p.cm_standoff)).intersect(back))
    part = part.cut(hq_to_station(p, hq_station_cuts(p))).cut(cm_to_station(p, cm_station_cuts(p)))
    for x, z in p.pod_screws:
        part = part.cut(cyl_y(p.m3_clear_d, y0 - 1, y1 + 1, x, z))
    return part


def make_pod(p: Params) -> cq.Workplane:
    part = to_world(p, make_pod_local(p))
    # The hex-key channels to the tab screws run on through the tongue, so the pod can stay on.
    for x, z in p.tab_holes:
        part = part.cut(cyl_y(p.access_d, p.collar_y0 + p.pad_t, 90, x, z))
    return part


def make_bracket(p: Params) -> cq.Workplane:
    y0 = p.collar_y0
    zc = p.ax_z
    web = box(p.web_x0, p.ax_x - p.split_gap / 2, y0, p.collar_y1, zc - p.web_z, zc + p.web_z)
    web = web.union(box(p.web_x0, p.web_x1_rear, p.collar_y1 - 1.0, 75, zc - p.web_z, zc + p.web_z))
    # The web's top is the pod's front face: everything behind that plane goes.
    web = web.cut(to_world(p, box(-300, 300, -p.hq_standoff - p.pod_t, 300, -300, 300)))
    part = web.union(collar_half(p, -1))
    part = part.cut(cyl_y(2 * p.bore_r, y0 - 1, 80, p.ax_x, zc))
    part = part.cut(hq_place(p)(hq_keepout_local(p)))
    # The two tab screws: clearance through the pad, and hex-key channels down to their heads.
    for x, z in p.tab_holes:
        part = part.cut(cyl_y(p.m3_clear_d, y0 - 1, y0 + p.pad_t + 1, x, z))
        part = part.cut(cyl_y(p.access_d, y0 + p.pad_t, 90, x, z))
    # The pod's two screws: clearance holes along the screw axis, nuts slid in from the web's outer face.
    for x, z in p.pod_screws:
        hole = cyl_y(p.m3_clear_d, p.pod_nut_y - 6.0, -p.hq_standoff - p.pod_t + 1.0, x, z)
        nut = hex_y(p.m3_nut_af, p.pod_nut_y - p.m3_nut_depth / 2, p.pod_nut_y + p.m3_nut_depth / 2, x, z)
        slot = box(x - 40.0, x, p.pod_nut_y - p.m3_nut_depth / 2, p.pod_nut_y + p.m3_nut_depth / 2,
                   z - p.m3_nut_af / 2, z + p.m3_nut_af / 2)
        part = part.cut(to_world(p, hole.union(nut).union(slot)))
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


# --- finger tags --------------------------------------------------------------------------------
# A 5 mm AprilTag on the outer (-X) flank of each finger. Stuck flat on, it faces the HQ Camera at
# 66-68 degrees; on a 35 degree wedge, at 32-39 (fiducials.py). The wedge is printed, the tag is
# paper (exports/fiducials/tags.pdf) glued to its face.

WEDGE_BASE = 0.8     # mm of plastic under the thin end


def wedge_face(p: Params) -> float:
    return p.tag_size * 10 / 8 + 1.0          # the tag with its white border, plus 0.5 mm each side


def make_tag_wedge_local(p: Params) -> cq.Workplane:
    """Wedge in its own frame: base on z = 0, x along the finger toward the arm, y along the finger
    travel. The tag face falls toward +x at tag_tilt, so it faces back toward the camera."""
    a = math.radians(p.tag_tilt)
    f = wedge_face(p)
    L = f * math.cos(a)
    pts = [(0, 0), (L, 0), (L, WEDGE_BASE), (0, WEDGE_BASE + f * math.sin(a))]
    return cq.Workplane("XZ").polyline(pts).close().extrude(-f).translate((0, -f / 2, 0))


def finger_flank(p: Params, finger: int, y: float) -> tuple[float, float, float, float]:
    """(x, z_lo, z_hi, slope dx/dy) of a finger's outer flank at y, as AgileX models it."""
    sol = reference.gripper_solids()[finger]
    rows = []
    for yy in (y - 3.0, y, y + 3.0):
        s = sol.intersect(cq.Solid.makeBox(300, 0.2, 300, cq.Vector(-150, yy - 0.1, -150)))
        verts, _ = s.tessellate(0.02, 0.1)
        xs = min(v.x for v in verts)
        zs = [v.z for v in verts if abs(v.x - xs) < 0.6]
        rows.append((xs, min(zs), max(zs)))
    slope = (rows[2][0] - rows[0][0]) / 6.0
    return rows[1][0], rows[1][1], rows[1][2], slope


def tag_poses(p: Params, opening: float) -> list[dict]:
    """Where each finger tag sits at a given opening: centre, outward normal (toward the camera),
    in-plane right and up vectors, in the gripper frame."""
    shift = (opening - reference.OPENING_AS_MODELLED) / 2
    out = []
    for name, finger, sgn in (("upper", 7, 1), ("lower", 11, -1)):
        x, zl, zh, slope = finger_flank(p, finger, p.tag_y)
        flank_n = cq.Vector(-1.0, slope, 0).normalized()               # outward, slightly toward the tips
        along = cq.Vector(flank_n.y, -flank_n.x, 0)                     # along the flank, toward the arm
        a = math.radians(p.tag_tilt)
        ang = math.atan2(flank_n.y, flank_n.x) - a                      # the wedge turns it toward +Y
        n = cq.Vector(math.cos(ang), math.sin(ang), 0)
        up = cq.Vector(0, 0, 1)
        right = up.cross(n)
        foot = cq.Vector(x, p.tag_y, (zl + zh) / 2 + sgn * shift)
        centre = foot + flank_n * (WEDGE_BASE + wedge_face(p) * math.sin(a) / 2)
        out.append({"name": name, "finger": finger, "centre": centre, "normal": n, "right": right, "up": up,
                    "foot": foot, "flank_normal": flank_n, "along": along})
    return out


def place_tag_wedges(p: Params, opening: float) -> cq.Workplane:
    """Both wedges on their fingers: the same profile as make_tag_wedge_local, drawn on a plane
    whose x runs along the flank toward the arm and whose y is the flank's outward normal."""
    wedges = []
    a = math.radians(p.tag_tilt)
    f = wedge_face(p)
    L = f * math.cos(a)
    pts = [(0, 0), (L, 0), (L, WEDGE_BASE), (0, WEDGE_BASE + f * math.sin(a))]
    for t in tag_poses(p, opening):
        origin = t["foot"] - t["along"] * (L / 2) - cq.Vector(0, 0, f / 2)
        plane = cq.Plane(origin=origin, xDir=t["along"], normal=cq.Vector(0, 0, 1))
        wedges.append(cq.Workplane(plane).polyline(pts).close().extrude(f).val())
    return cq.Workplane("XY").add(cq.Compound.makeCompound(wedges))


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
FINGERTIP_Y = -77.52


def hq_fov(p: Params) -> tuple[float, float]:
    return tuple(2 * math.degrees(math.atan(s / 2 / p.lens_f)) for s in IMX477)


def optical_axes(p: Params) -> dict[str, tuple[cq.Vector, cq.Vector, cq.Vector]]:
    """(lens front point, unit view direction, image up) for each camera. Image up is the side
    away from the ribbon connector, as when the camera stands on its tripod foot: for the HQ with
    hq_roll = 90 that is away from the gripper, so the fingers are at the bottom of the picture."""
    t = math.radians(p.toe_deg)
    d = cq.Vector(math.sin(t), -math.cos(t), 0)
    hq_o = station_vec(p, 0, -p.hq_front_dist, 0)
    cm_o = station_vec(p, 0, -(p.hq_standoff - p.cm_standoff) - p.cm_lens_h, p.cm_dz)
    r = math.radians(p.hq_roll)
    # The connector side (-Y local) after the roll is (sin r, 0, cos r) in the station frame.
    up_st = (-math.sin(r), 0.0, -math.cos(r))
    hq_up = cq.Vector(up_st[0] * math.cos(t), up_st[0] * math.sin(t), up_st[2]).normalized()
    return {"hq": (hq_o, d, hq_up), "cm3w": (cm_o, d, cq.Vector(0, 0, 1))}


def hq_image_fov(p: Params) -> tuple[float, float]:
    """(across the image, up the image) in degrees; the sensor's long side is 'across'."""
    return hq_fov(p)


def view_pyramid(o: cq.Vector, d: cq.Vector, up: cq.Vector, hfov: float, vfov: float, depth: float,
                 aperture: float = 0.0) -> cq.Workplane:
    """Frustum of what a camera sees, out to `depth` along its axis. hfov is across the image."""
    up = (up - d * up.dot(d)).normalized()
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


def in_view(p: Params, pt: cq.Vector, which: str = "hq") -> tuple[bool, float, float]:
    """Is a point inside a camera's field of view? Also returns its angles off the axis
    (across, up) in degrees."""
    o, d, up = optical_axes(p)[which]
    hf, vf = hq_fov(p) if which == "hq" else CM3W_FOV
    up = (up - d * up.dot(d)).normalized()
    right = d.cross(up)
    v = pt - o
    z = v.dot(d)
    if z <= 0:
        return False, float("nan"), float("nan")
    ax = math.degrees(math.atan2(v.dot(right), z))
    ay = math.degrees(math.atan2(v.dot(up), z))
    return abs(ax) <= hf / 2 and abs(ay) <= vf / 2, ax, ay


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


def axis_in_view_beyond_tips(p: Params) -> float:
    """How far past the fingertips a point on the gripper axis first enters the HQ view
    (0 if the axis is already in view at the fingertips)."""
    for i in range(0, 3000):
        y = FINGERTIP_Y - i * 0.5
        if in_view(p, cq.Vector(p.ax_x, y, p.ax_z))[0]:
            return FINGERTIP_Y - y
    return float("nan")


def run_checks(p: Params, parts: dict[str, cq.Workplane]) -> dict:
    solids = ("bracket", "pod", "carrier", "hq_pcb", "hq_mount", "hq_lens", "cm_pcb", "cm_module", "pi5",
              "pi_spacers")
    res: dict = {"overlap_mm3": {}, "gap_mm": {}, "view": {}, "extent_mm": {}}
    for opening, tag in ((0.0, "closed"), (100.0, "fully open")):
        g = reference.gripper(opening)
        for name in solids:
            res["overlap_mm3"][f"{name} vs gripper fingers ({tag})"] = overlap(parts[name], g["fingers"])
        res["gap_mm"][f"mount to fingers ({tag})"] = min(
            gap(parts[n], g["fingers"]) for n in ("bracket", "pod", "carrier", "hq_lens", "hq_mount", "cm_module"))
        wedges = place_tag_wedges(p, opening)
        res["gap_mm"][f"finger tag wedges to the mount ({tag})"] = min(
            gap(wedges, parts[n]) for n in ("bracket", "pod", "carrier", "hq_lens", "hq_mount", "pi5"))
    g = reference.gripper()
    for name in solids:
        res["overlap_mm3"][f"{name} vs gripper body"] = overlap(parts[name], g["body"])
    pairs = [("bracket", "pod"), ("bracket", "carrier"), ("pod", "carrier"),
             ("bracket", "hq_pcb"), ("bracket", "hq_mount"), ("bracket", "hq_lens"), ("bracket", "cm_pcb"),
             ("bracket", "cm_module"), ("pod", "hq_pcb"), ("pod", "hq_mount"), ("pod", "hq_lens"),
             ("pod", "cm_pcb"), ("pod", "cm_module"), ("carrier", "pi_spacers"), ("carrier", "pi5"),
             ("pi_spacers", "pi5"), ("hq_mount", "cm_module"), ("hq_pcb", "cm_pcb"), ("hq_mount", "cm_pcb")]
    for a, b in pairs:
        res["overlap_mm3"][f"{a} vs {b}"] = overlap(parts[a], parts[b])
    res["gap_mm"]["bracket to gripper body"] = gap(parts["bracket"], g["body"])
    res["gap_mm"]["pod to gripper body"] = gap(parts["pod"], g["body"])
    res["gap_mm"]["carrier to gripper body"] = gap(parts["carrier"], g["body"])
    res["gap_mm"]["collar halves (split)"] = gap(parts["bracket"], parts["carrier"])
    res["gap_mm"]["HQ lens to the bracket"] = gap(parts["hq_lens"], parts["bracket"])
    res["gap_mm"]["HQ lens to the finger plate"] = gap(parts["hq_lens"], g["body"])
    # What the HQ Camera sees.
    hf, vf = hq_fov(p)
    axes = optical_axes(p)
    res["view"]["HQ field of view (deg, across x up the image)"] = [round(hf, 1), round(vf, 1)]
    res["view"]["HQ toe-in (deg)"] = p.toe_deg
    res["view"]["HQ lens front behind the fingertips (mm)"] = round(axes["hq"][0].y - FINGERTIP_Y, 1)
    res["view"]["HQ lens front behind the finger plate's front face (mm)"] = round(axes["hq"][0].y - (-4.52), 1)
    res["view"]["HQ lens front, off the gripper axis (mm)"] = round(p.ax_x - axes["hq"][0].x, 1)
    res["view"]["gripper axis enters the HQ view this far past the fingertips (mm)"] = round(
        axis_in_view_beyond_tips(p), 1)
    tips = {}
    for opening in (0.0, 20.0, 40.0, 60.0, 80.0, 100.0):
        shift = (opening - reference.OPENING_AS_MODELLED) / 2
        pts = {"centre between the fingertips": cq.Vector(p.ax_x, FINGERTIP_Y + 3, p.ax_z),
               "upper fingertip": cq.Vector(p.ax_x - 8, FINGERTIP_Y + 1, 31.11 + shift + 3),
               "lower fingertip": cq.Vector(p.ax_x - 8, FINGERTIP_Y + 1, -27.27 - shift - 3)}
        for t in tag_poses(p, opening):
            pts[f"{t['name']} finger tag"] = t["centre"]
        tips[f"{opening:.0f} mm open"] = {k: in_view(p, v)[0] for k, v in pts.items()}
    res["view"]["in the HQ view, by opening"] = tips
    everything = cq.Workplane("XY").add(cq.Compound.makeCompound([parts[n].val() for n in solids]))
    bb = everything.val().BoundingBox()
    res["extent_mm"] = {
        "rearmost point (must be < flange face 64.98)": round(bb.ymax, 2),
        "frontmost point": round(bb.ymin, 2),
        "max radius from the J6 axis": round(max(
            math.hypot(x - p.ax_x, z - p.ax_z) for x in (bb.xmin, bb.xmax) for z in (bb.zmin, bb.zmax)), 1),
        "x": [round(bb.xmin, 1), round(bb.xmax, 1)], "y": [round(bb.ymin, 1), round(bb.ymax, 1)],
        "z": [round(bb.zmin, 1), round(bb.zmax, 1)],
    }
    res["printed_volume_cm3"] = {n: round(parts[n].val().Volume() / 1000, 2)
                                 for n in ("bracket", "pod", "carrier", "spacers", "tag_wedge")}
    tol = 1e-3
    res["pass"] = all(v <= tol for v in res["overlap_mm3"].values()) and bb.ymax < p.flange_face_y
    return res


# --- build / export -----------------------------------------------------------------------------

def build(p: Params) -> dict[str, cq.Workplane]:
    hq, cm = hq_place(p), cm_place(p)
    parts = {
        "bracket": make_bracket(p),
        "pod": make_pod(p),
        "carrier": make_carrier(p),
        "spacers": make_spacers(p),
        "pi_spacers": place_spacers(p),
        "pi5": place_pi(p, make_pi5_local()),
        "tag_wedge": make_tag_wedge_local(p),
    }
    parts.update({k: hq(v) for k, v in make_hq_camera_local(p).items()})
    parts.update({k: cm(v) for k, v in make_cm_camera_local(p).items()})
    return parts


ASSEMBLY = ("bracket", "pod", "carrier", "pi_spacers", "hq_pcb", "hq_mount", "hq_lens", "cm_pcb", "cm_module",
            "pi5")
PRINTED = ("bracket", "pod", "carrier", "spacers", "tag_wedge")
ORANGE = (0.93, 0.45, 0.13)
COLORS = {
    "bracket": ORANGE, "pod": (0.96, 0.58, 0.20), "carrier": ORANGE, "pi_spacers": ORANGE, "spacers": ORANGE,
    "tag_wedge": ORANGE,
    "hq_pcb": (0.12, 0.48, 0.25), "hq_mount": (0.13, 0.13, 0.14), "hq_lens": (0.08, 0.08, 0.09),
    "cm_pcb": (0.12, 0.48, 0.25), "cm_module": (0.1, 0.1, 0.1), "pi5": (0.18, 0.55, 0.34),
}


def print_orientation(name: str, part: cq.Workplane, p: Params | None = None) -> cq.Workplane:
    """bracket: pad face down (build +Y); pod: camera plate's front face down (build station +Y);
    carrier: Pi plate down (build -X); tag_wedge: base down."""
    if name == "bracket":
        part = part.rotate((0, 0, 0), (1, 0, 0), 90)        # +Y -> +Z
    elif name == "pod":
        part = make_pod_local(p or Params()).rotate((0, 0, 0), (1, 0, 0), 90)   # station +Y -> +Z
    elif name == "carrier":
        part = part.rotate((0, 0, 0), (0, 1, 0), 90)        # -X -> +Z
    bb = part.val().BoundingBox()
    return part.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def export(p: Params, parts: dict, checks: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name in PRINTED:
        cq.exporters.export(parts[name], str(out / f"{name}.step"))
        cq.exporters.export(print_orientation(name, parts[name], p), str(out / f"{name}.stl"),
                            tolerance=0.02, angularTolerance=0.1)
    assy = cq.Assembly(name="piper_camera_mount")
    for name in ASSEMBLY:
        assy.add(parts[name], name=name, color=cq.Color(*COLORS[name]))
    assy.add(place_tag_wedges(p, 40.0), name="tag_wedges", color=cq.Color(*COLORS["tag_wedge"]))
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
