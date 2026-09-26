#!/usr/bin/env python3
"""OT-2 lid camera mount: parametric CadQuery model (path A).

Holds the Raspberry Pi HQ Camera and the Waveshare 8-50 mm C-mount zoom lens
pointing straight down through the OT-2's 5 mm top window, with the Raspberry Pi
5 riding on top. The printed parts are:

    base            plate, four posts and a light collar; tapes or bolts to the lid
    deck            the camera hangs underneath on four M2.5 bosses; the Pi 5 sits on top
    drill_template  2 mm plate for marking the lens cutout and the bolt holes
    spacers         4 x Pi 5 standoffs and 4 x 2 mm shims to raise the deck

Coordinates: the optical axis is X = Y = 0, Z = 0 is the top face of the lid,
+Z is up. The camera's ribbon connector and tripod foot face -Y. The long axis
of the sensor is X, so X should follow the 12-column axis of the plate (left to
right across the OT-2 deck).

    python lid_mount.py               # build, run clearance checks, export
    python lid_mount.py --check-only  # checks only, write nothing

Every derived height follows from the camera and lens stack in `Params`, so if
a measurement disagrees with an estimate below, change the number and rebuild.
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


@dataclass
class Params:
    # --- OT-2 lid (measure before drilling) --------------------------------
    lid_thickness: float = 5.0      # Opentrons CAD: 5.00 mm; only affects bolt length and the cone check
    cutout_d: float = 50.8          # lens hole in the lid: a 2" hole saw
    lid_bolt_d: float = 5.0         # bolt holes in the lid: M4 plus room for acrylic to expand

    # --- Waveshare 8-50 mm zoom (C-mount): O40 x 68.3 mm, 148 g -------------
    lens_od: float = 40.0
    lens_length: float = 68.3       # overall, including the C-mount thread
    lens_thread_len: float = 4.5    # estimate: thread length behind the flange
    lens_clear_ap: float = 36.0     # front glass; deliberately generous for the cone check
    ring_sweep_d: float = 64.0      # estimated sweep of the thumbscrews as the rings turn
    lens_front_gap: float = 3.0     # the lens front sits this far above the base top

    # --- Raspberry Pi HQ Camera (CS-mount), from the official drawing --------
    cam_board: float = 38.0
    cam_hole_pitch: float = 30.0    # 4 x O2.5 holes, 4 mm in from each edge
    cam_pcb_t: float = 1.4
    cs_seat_from_pcb_back: float = 15.83   # 18.58 overall minus the 2.75 connector
    c_cs_adapter: float = 5.03      # C (17.526) minus CS (12.5) flange focal distance
    cam_standoff: float = 6.0       # PCB back face to deck; clears the FPC connector

    # --- base --------------------------------------------------------------
    base_size: float = 112.0
    base_t: float = 6.0
    corner_r: float = 6.0
    aperture_d: float = 46.0        # 3 mm radial clearance around the O40 lens
    collar_h: float = 14.0          # above the base top; shades the lid under the lens
    collar_wall: float = 3.0
    post_w: float = 10.0
    post_c: float = 47.0            # post centres at (+-post_c, +-post_c)
    post_chamfer: float = 0.8       # round the post tops: a lead-in for the deck's sockets
    # The post tops rise into sockets in the deck's underside, so the deck is located without
    # the screws. An M3 nut slides into each post from outside (OpenFlexure style), and the
    # screw clamps the top of the post between the nut and the deck instead of tapping into PLA.
    socket_depth: float = 2.5
    # Fits chosen with slice/fit_sim.py: as sliced, then Bambu's A1 mini PLA error model on top.
    socket_clear: float = 0.20      # per side; prints about 0.15, a locating slip fit
    socket_corner_r: float = 1.0    # tighter than the post's 1.5 + clear, so only the flats touch:
                                    # small concave arcs print small, and would bind first
    m3_nut_slot_w: float = 5.8      # 5.5 mm across flats + 0.3; prints about 5.62
    m3_nut_slot_h: float = 3.0      # 2.4 mm nut + 0.6, as OpenFlexure's M3 slot; the roof is a bridge
    m3_nut_roof: float = 4.5        # post left above the slot
    m3_screw_len: float = 16.0
    bolt_xy: float = 33.0           # M4 bolts at (+-bolt_xy, +-bolt_xy)
    bolt_clear_d: float = 4.5
    m4_nut_af: float = 7.3          # 7.0 mm nut + 0.3 clearance
    m4_nut_h: float = 3.5           # 3.2 mm nut + 0.3
    tab_w: float = 30.0             # tape tabs in the middle of each side
    tab_len: float = 16.0
    tab_t: float = 2.0

    # --- deck --------------------------------------------------------------
    deck_t: float = 5.0
    m3_clear_d: float = 3.4
    boss_d: float = 6.0
    m25_clear_d: float = 2.8
    m25_nut_af: float = 5.3         # 5.0 mm nut + 0.3
    m25_nut_h: float = 2.3          # 2.0 mm nut + 0.3
    first_layer_flare: float = 0.4  # 45 deg flare on the camera nut traps, which open onto the bed
    slot_w: float = 22.0            # ribbon cable slot (X)
    slot_h: float = 6.0             # (Y)
    # Raspberry Pi 5: 85 x 56 mm board, M2.5 holes on 58 x 49 mm, 3.5 mm from
    # the left, top and bottom edges. Its USB/Ethernet edge faces +X.
    pi_hole_x: float = 58.0
    pi_hole_y: float = 49.0
    pi_cx: float = 0.0              # centre of the Pi's hole pattern on the deck
    pi_cy: float = 12.0
    pi_spacer_h: float = 5.0
    shim_t: float = 2.0

    # --- drill template ------------------------------------------------------
    template_t: float = 2.0
    template_center_d: float = 3.0  # centre-punch mark / hole-saw pilot
    template_bolt_d: float = 4.2    # guide for a pilot drill

    # ------------------------------------------------------------------------
    @property
    def z_lens_front(self) -> float:
        return self.base_t + self.lens_front_gap

    @property
    def z_lens_flange(self) -> float:
        return self.z_lens_front + self.lens_length - self.lens_thread_len

    @property
    def z_cs_seat(self) -> float:
        return self.z_lens_flange + self.c_cs_adapter

    @property
    def z_pcb_back(self) -> float:
        return self.z_cs_seat + self.cs_seat_from_pcb_back

    @property
    def z_deck(self) -> float:
        """Underside of the deck plate. The posts rise socket_depth above it, into the deck."""
        return self.z_pcb_back + self.cam_standoff

    @property
    def z_post_top(self) -> float:
        return self.z_deck + self.socket_depth

    @property
    def z_m3_slot(self) -> float:
        """Floor of the M3 nut slots in the posts."""
        return self.z_post_top - self.m3_nut_roof - self.m3_nut_slot_h

    def pi_holes(self) -> list[tuple[float, float]]:
        hx, hy = self.pi_hole_x / 2, self.pi_hole_y / 2
        return [(self.pi_cx + sx * hx, self.pi_cy + sy * hy) for sx in (-1, 1) for sy in (-1, 1)]

    def pi_board_box(self) -> tuple[float, float, float, float]:
        """x0, x1, y0, y1 of the Pi 5 board on the deck."""
        x0 = self.pi_cx - self.pi_hole_x / 2 - 3.5
        y0 = self.pi_cy - self.pi_hole_y / 2 - 3.5
        return x0, x0 + 85.0, y0, y0 + 56.0


# --- small helpers -----------------------------------------------------------

def box(x, y, z, cx=0.0, cy=0.0, z0=0.0) -> cq.Workplane:
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False)).translate((cx, cy, z0))


def cyl(d, h, cx=0.0, cy=0.0, z0=0.0) -> cq.Workplane:
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((cx, cy, z0))


def hex_prism(af, h, cx=0.0, cy=0.0, z0=0.0) -> cq.Workplane:
    return cq.Workplane("XY").polygon(6, af / math.cos(math.pi / 6)).extrude(h).translate((cx, cy, z0))


def corners(a: float) -> list[tuple[float, float]]:
    return [(sx * a, sy * a) for sx in (-1, 1) for sy in (-1, 1)]


def rounded_box(w, h, r, cx=0.0, cy=0.0, z0=0.0) -> cq.Workplane:
    """Square prism with its vertical edges rounded to r."""
    return box(w, w, h, cx, cy, z0).edges("|Z").fillet(r)


def nut_slot(af, h, reach, cx, cy, z0, angle_deg) -> cq.Workplane:
    """Side-entry nut slot: a channel as wide as the nut's flats, running out `reach` from
    (cx, cy) and turned to open at angle_deg, ending in a hex so the nut stops on the axis."""
    slot = hex_prism(af, h).union(box(reach, af, h, cx=reach / 2))
    return slot.rotate((0, 0, 0), (0, 0, 1), angle_deg).translate((cx, cy, z0))


def hex_flare(af, c, cx, cy, z_face) -> cq.Workplane:
    """A 45 degree flare, c deep, at the mouth of a hex pocket in a face that prints on the bed,
    so the squashed first layer (elephant's foot) can't close the mouth up."""
    k = 1 / math.cos(math.pi / 6)
    return (cq.Workplane("XY").workplane(offset=z_face - c).polygon(6, af * k)
            .workplane(offset=c + 1).polygon(6, (af + 2 * (c + 1)) * k).loft().translate((cx, cy, 0)))


def radial_cyl(d, r0, r1, z, angle_deg) -> cq.Workplane:
    """Cylinder along a radius of the optical axis, from r0 to r1 at height z."""
    return (cq.Workplane("YZ").circle(d / 2).extrude(r1 - r0)
            .translate((r0, 0, z)).rotate((0, 0, 0), (0, 0, 1), angle_deg))


def footprint(p: Params, t: float) -> cq.Workplane:
    """Plate outline shared by the base and the drill template: a rounded
    square plus four tape tabs, each with a V-notch on the optical axis line."""
    plate = box(p.base_size, p.base_size, t).edges("|Z").fillet(p.corner_r)
    half = p.base_size / 2
    tip = half + p.tab_len
    for ang in (0, 90, 180, 270):
        tab = box(p.tab_w, p.tab_len + 2, t, 0, half + p.tab_len / 2 - 1)
        tab = tab.edges("|Z and >Y").fillet(3.0)
        notch = (cq.Workplane("XY").polyline([(-3, tip + 1), (3, tip + 1), (0, tip - 4)]).close()
                 .extrude(t + 2).translate((0, 0, -1)))
        plate = plate.union(tab.cut(notch).rotate((0, 0, 0), (0, 0, 1), ang))
    return plate


# --- printed parts -------------------------------------------------------------

def make_base(p: Params) -> cq.Workplane:
    base = footprint(p, p.tab_t).union(
        box(p.base_size, p.base_size, p.base_t).edges("|Z").fillet(p.corner_r))
    collar_od = p.aperture_d + 2 * p.collar_wall
    base = base.union(cyl(collar_od, p.base_t + p.collar_h))
    post_h = p.z_post_top - p.base_t
    z_tip = p.z_deck + p.deck_t - p.m3_screw_len
    for x, y in corners(p.post_c):
        post = rounded_box(p.post_w, post_h + 0.5, 1.5, x, y, p.base_t - 0.5)
        base = base.union(post.faces(">Z").edges().chamfer(p.post_chamfer))
        # M3 clearance down past the screw tip, and the nut slot, opening outward along X.
        base = base.cut(cyl(p.m3_clear_d, p.z_post_top - z_tip + 2, x, y, z_tip - 1))
        base = base.cut(nut_slot(p.m3_nut_slot_w, p.m3_nut_slot_h, p.post_w / 2 + 1, x, y, p.z_m3_slot,
                                 0 if x > 0 else 180))
    base = base.cut(cyl(p.aperture_d, p.base_t + p.collar_h + 2, z0=-1))
    for x, y in corners(p.bolt_xy):
        base = base.cut(cyl(p.bolt_clear_d, p.base_t + 2, x, y, -1))
        base = base.cut(hex_prism(p.m4_nut_af, p.m4_nut_h + 1, x, y, p.base_t - p.m4_nut_h))
    # Engraved arrow pointing -Y: the cable side of the camera.
    arrow = (cq.Workplane("XY").polyline([(-5, -34), (5, -34), (0, -44)]).close()
             .extrude(1.0).translate((0, 0, p.base_t - 0.6)))
    return base.cut(arrow)


def make_socket(p: Params, x: float, y: float) -> cq.Workplane:
    """Pocket in the deck's underside that a post top slides into, with a 45 degree lead-in."""
    w, r, lead = p.post_w + 2 * p.socket_clear, p.socket_corner_r, 0.6
    pocket = rounded_box(w, p.socket_depth + 1, r, x, y, p.z_deck - 1)
    mouth = rounded_box(w + 2 * lead, lead + 1, r + lead, x, y, p.z_deck - 1).faces(">Z").edges().chamfer(lead)
    return pocket.union(mouth)


def make_deck(p: Params) -> cq.Workplane:
    z0 = p.z_deck
    deck = box(p.base_size, p.base_size, p.deck_t, z0=z0).edges("|Z").fillet(p.corner_r)
    cam_holes = corners(p.cam_hole_pitch / 2)
    for x, y in cam_holes:
        deck = deck.union(cyl(p.boss_d, p.cam_standoff + 0.5, x, y, z0 - p.cam_standoff))
    for x, y in corners(p.post_c):
        deck = deck.cut(cyl(p.m3_clear_d, p.deck_t + 2, x, y, z0 - 1))
        deck = deck.cut(make_socket(p, x, y))
    for x, y in cam_holes:
        # M2.5 up through the camera PCB and the boss; nut trapped in the deck top.
        deck = deck.cut(cyl(p.m25_clear_d, p.cam_standoff + p.deck_t + 2, x, y, z0 - p.cam_standoff - 1))
        deck = deck.cut(hex_prism(p.m25_nut_af, p.m25_nut_h + 1, x, y, z0 + p.deck_t - p.m25_nut_h))
        deck = deck.cut(hex_flare(p.m25_nut_af, p.first_layer_flare, x, y, z0 + p.deck_t))
    for x, y in p.pi_holes():
        # M2.5 down through the Pi and a spacer; nut trapped in the deck underside.
        deck = deck.cut(cyl(p.m25_clear_d, p.deck_t + 2, x, y, z0 - 1))
        deck = deck.cut(hex_prism(p.m25_nut_af, p.m25_nut_h + 1, x, y, z0 - 1))
    y_slot = -(p.cam_board / 2 + 2 + p.slot_h / 2)
    slot = box(p.slot_w, p.slot_h, p.deck_t + 2, 0, y_slot, z0 - 1).edges("|Z").fillet(1.5)
    return deck.cut(slot)


def make_drill_template(p: Params) -> cq.Workplane:
    t = p.template_t
    tpl = footprint(p, t)
    tpl = tpl.cut(cyl(p.template_center_d, t + 2, z0=-1))
    for x, y in corners(p.bolt_xy):
        tpl = tpl.cut(cyl(p.template_bolt_d, t + 2, x, y, -1))
    # Scribe line for the lens cutout, and axis lines out to the tab notches.
    groove = 0.8
    ring = cyl(p.cutout_d, groove + 1, z0=t - groove).cut(cyl(p.cutout_d - 2 * groove, groove + 3, z0=t - groove - 1))
    span = p.base_size + 2 * p.tab_len
    lines = box(span, groove, groove + 1, z0=t - groove).union(box(groove, span, groove + 1, z0=t - groove))
    lines = lines.cut(cyl(p.template_center_d + 4, t + 2, z0=-1))
    return tpl.cut(ring).cut(lines)


def make_spacers(p: Params) -> cq.Workplane:
    """Four Pi 5 standoffs and four deck shims, laid out for printing."""
    out = None
    for i in range(4):
        s = cyl(6.0, p.pi_spacer_h, cx=i * 10.0).cut(cyl(p.m25_clear_d, p.pi_spacer_h + 2, cx=i * 10.0, z0=-1))
        out = s if out is None else out.union(s)
    for i in range(4):
        s = cyl(10.0, p.shim_t, cx=i * 14.0, cy=14.0).cut(cyl(p.m3_clear_d, p.shim_t + 2, cx=i * 14.0, cy=14.0, z0=-1))
        out = out.union(s)
    return out


# --- reference models (not printed): for the assembly, renders and checks -------------

def make_camera_pcb(p: Params) -> cq.Workplane:
    z_front = p.z_pcb_back - p.cam_pcb_t
    pcb = box(p.cam_board, p.cam_board, p.cam_pcb_t, z0=z_front).edges("|Z").fillet(1.0)
    for x, y in corners(p.cam_hole_pitch / 2):
        pcb = pcb.cut(cyl(2.5, p.cam_pcb_t + 2, x, y, z_front - 1))
    return pcb.union(box(20.0, 5.7, 2.75, 0, -p.cam_board / 2 + 3.4, p.z_pcb_back))  # FPC connector


def make_camera_mount(p: Params) -> cq.Workplane:
    """The HQ Camera's aluminium CS mount, back-focus ring and tripod foot."""
    z_front = p.z_pcb_back - p.cam_pcb_t
    ring = cyl(36.0, 5.8, z0=p.z_cs_seat)                      # knurled back-focus ring
    body = cyl(30.75, z_front - p.z_cs_seat - 5.8, z0=p.z_cs_seat + 5.8)
    foot = box(13.97, 15.2, 12.0, 0, -p.cam_board / 2 - 11.2 + 7.6, z_front - 12.0)  # tripod foot
    clamp = box(10.16, 5.0, 5.0, 0, p.cam_board / 2 - 1.0, p.z_cs_seat + 1.0)       # back-focus lock
    return ring.union(body).union(foot).union(clamp)


def make_camera(p: Params) -> cq.Workplane:
    return make_camera_pcb(p).union(make_camera_mount(p))


def place_pi_spacers(p: Params) -> cq.Workplane:
    out = None
    for x, y in p.pi_holes():
        s = cyl(6.0, p.pi_spacer_h, x, y, p.z_deck + p.deck_t).cut(
            cyl(p.m25_clear_d, p.pi_spacer_h + 2, x, y, p.z_deck + p.deck_t - 1))
        out = s if out is None else out.union(s)
    return out


def make_adapter(p: Params) -> cq.Workplane:
    return cyl(31.0, p.c_cs_adapter, z0=p.z_lens_flange).cut(cyl(25.4, p.c_cs_adapter + 2, z0=p.z_lens_flange - 1))


def make_lens(p: Params) -> cq.Workplane:
    """Envelope of the Waveshare 8-50 mm zoom lens, with its three thumbscrews.
    Section lengths are estimated from product photos; only O40 x 68.3 is official."""
    zf, zfl = p.z_lens_front, p.z_lens_flange
    lens = cyl(p.lens_od, 17.0, z0=zf).cut(cyl(p.lens_clear_ap, 3.0, z0=zf - 1))  # front barrel, recessed glass
    lens = lens.union(cyl(38.5, 1.8, z0=zf + 17.0))                  # gold trim ring
    lens = lens.union(cyl(37.0, 13.0, z0=zf + 18.8))                 # zoom ring (TELE/WIDE)
    lens = lens.union(cyl(38.5, 10.0, z0=zf + 31.8))                 # knurled ring
    lens = lens.union(cyl(36.0, zfl - zf - 41.8, z0=zf + 41.8))      # focus and iris section
    lens = lens.union(cyl(25.4, p.lens_thread_len, z0=zfl))           # C-mount thread
    for dz, ang in ((25.0, 200.0), (48.0, 150.0), (53.0, 185.0)):     # zoom, iris, focus screws
        lens = lens.union(radial_cyl(3.0, 17.5, 23.5, zf + dz, ang))
        lens = lens.union(radial_cyl(6.5, 23.5, 27.5, zf + dz, ang))
    return lens


def make_ring_sweep(p: Params) -> cq.Workplane:
    """Volume the rings and thumbscrews sweep, plus finger room. Must stay empty."""
    z0 = p.z_lens_front + 20.0
    return cyl(p.ring_sweep_d, p.z_lens_flange - z0, z0=z0)


def make_pi5(p: Params) -> cq.Workplane:
    x0, x1, y0, y1 = p.pi_board_box()
    zb = p.z_deck + p.deck_t + p.pi_spacer_h
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    board = box(85.0, 56.0, 1.6, cx, cy, zb).edges("|Z").fillet(3.0)
    for x, y in p.pi_holes():
        board = board.cut(cyl(2.7, 4, x, y, zb - 1))
    zt = zb + 1.6
    pi = board.union(box(21.0, 16.0, 13.5, x1 - 10.0, y0 + 10.5, zt))    # Ethernet
    pi = pi.union(box(17.5, 13.0, 16.0, x1 - 8.0, y0 + 29.0, zt))        # USB 3 stack
    pi = pi.union(box(17.5, 13.0, 16.0, x1 - 8.0, y0 + 47.0, zt))        # USB 2 stack
    pi = pi.union(box(51.0, 5.0, 8.5, x0 + 32.5, y1 - 3.5, zt))          # GPIO header
    pi = pi.union(box(52.0, 40.0, 10.0, x0 + 30.0, cy + 2.0, zt))        # Active Cooler
    pi = pi.union(box(9.0, 7.5, 3.3, x0 + 11.2, y0 + 3.2, zt))           # USB-C power
    return pi


def make_lid(p: Params, size: float = 260.0) -> cq.Workplane:
    lid = box(size, size, p.lid_thickness, z0=-p.lid_thickness)
    lid = lid.cut(cyl(p.cutout_d, p.lid_thickness + 2, z0=-p.lid_thickness - 1))
    for x, y in corners(p.bolt_xy):
        lid = lid.cut(cyl(p.lid_bolt_d, p.lid_thickness + 2, x, y, -p.lid_thickness - 1))
    return lid


def half_diag_fov_deg(focal_mm: float) -> float:
    """IMX477 active area is 6.287 x 4.712 mm (7.857 mm diagonal)."""
    return math.degrees(math.atan(7.857 / 2 / focal_mm))


def make_view_cone(p: Params, focal_mm: float, depth: float) -> cq.Workplane:
    """Conservative envelope of the rays leaving the lens front at a given focal
    length: the full clear aperture, spreading at the half-diagonal field angle."""
    r1 = p.lens_clear_ap / 2 - 0.01
    r2 = r1 + depth * math.tan(math.radians(half_diag_fov_deg(focal_mm)))
    solid = cq.Solid.makeCone(r1, r2, depth, cq.Vector(0, 0, p.z_lens_front - 0.05), cq.Vector(0, 0, -1))
    return cq.Workplane("XY").add(solid)


# --- checks ---------------------------------------------------------------------------

def overlap(a: cq.Workplane, b: cq.Workplane) -> float:
    """Volume (mm^3) shared by two solids; 0 means no interference."""
    common = a.val().intersect(b.val())
    return sum(s.Volume() for s in common.Solids())


def gap(a: cq.Workplane, b: cq.Workplane) -> float:
    return a.val().distance(b.val())


def pi_to_screw_heads(p: Params, head_r: float = 2.75) -> float:
    """Plan-view gap between the Pi 5 board and the M3 heads on the posts, so
    the deck screws can be reached without lifting the Pi off."""
    x0, x1, y0, y1 = p.pi_board_box()
    gaps = []
    for x, y in corners(p.post_c):
        dx = max(x0 - x, 0.0, x - x1)
        dy = max(y0 - y, 0.0, y - y1)
        gaps.append(math.hypot(dx, dy) - head_r)
    return min(gaps)


def m3_thread_past_nut(p: Params, nut_h: float = 2.4) -> float:
    """How far the M3 screw reaches below its nut once the nut is pulled up against the slot roof."""
    nut_bottom = p.z_m3_slot + p.m3_nut_slot_h - nut_h
    return nut_bottom - (p.z_deck + p.deck_t - p.m3_screw_len)


def min_clear_focal(p: Params) -> float:
    """Shortest focal length whose view cone clears both the base aperture and
    the cutout in the lid (checked at the bottom face of each)."""
    for f10 in range(60, 510):
        f = f10 / 10
        t = math.tan(math.radians(half_diag_fov_deg(f)))
        at_base = p.lens_clear_ap + 2 * (p.z_lens_front - 0.0) * t
        at_lid = p.lens_clear_ap + 2 * (p.z_lens_front + p.lid_thickness) * t
        if at_base <= p.aperture_d and at_lid <= p.cutout_d:
            return f
    return float("nan")


def run_checks(p: Params, parts: dict[str, cq.Workplane]) -> dict:
    base, deck = parts["base"], parts["deck"]
    cam, lens, pi = parts["camera"], parts["lens"], parts["pi5"]
    lid, sweep = parts["lid"], make_ring_sweep(p)
    f_min = min_clear_focal(p)
    cone_depth = p.z_lens_front + p.lid_thickness + 1.0
    cone_min = make_view_cone(p, f_min, cone_depth)
    cone_work = make_view_cone(p, 25.0, cone_depth)   # working zoom at the lid
    results = {
        "overlap_mm3": {
            "base vs lens": overlap(base, lens),
            "base vs ring/thumbscrew sweep": overlap(base, sweep),
            "base vs camera": overlap(base, cam),
            "deck vs camera": overlap(deck, cam),
            "deck vs lens": overlap(deck, lens),
            "deck vs Pi 5": overlap(deck, pi),
            "base vs lid": overlap(base, lid),
            "base vs deck (posts in their sockets)": overlap(base, deck),
            f"view cone at {f_min:.1f} mm vs base": overlap(cone_min, base),
            f"view cone at {f_min:.1f} mm vs lid": overlap(cone_min, lid),
            "view cone at 25 mm vs lid": overlap(cone_work, lid),
        },
        "gap_mm": {
            "lens front barrel to collar": gap(lens, base),
            "lens front above lid top": p.z_lens_front,
            "thumbscrews to nearest post": gap(lens, base.intersect(box(300, 300, 200, z0=p.base_t + p.collar_h + 0.1))),
            "camera to base": gap(cam, base),
            "Pi 5 board to deck screw heads (plan)": pi_to_screw_heads(p),
            "post to socket wall, per side": p.socket_clear,
            "M3 screw tip below its nut": m3_thread_past_nut(p),
        },
        "heights_mm": {
            "lens front (Z)": p.z_lens_front,
            "lens flange": p.z_lens_flange,
            "CS seat": p.z_cs_seat,
            "camera PCB back": p.z_pcb_back,
            "deck underside": p.z_deck,
            "post top (in the deck's sockets)": p.z_post_top,
            "M3 nut slot, floor": p.z_m3_slot,
            "deck top": p.z_deck + p.deck_t,
            "Pi 5 board underside": p.z_deck + p.deck_t + p.pi_spacer_h,
            "overall height above lid (approx.)": p.z_deck + p.deck_t + p.pi_spacer_h + 1.6 + 16.0,
            "post height": p.z_post_top - p.base_t,
        },
        "optics": {
            "shortest vignette-free focal length (mm)": f_min,
            "cutout diameter (mm)": p.cutout_d,
        },
        "printed_volume_cm3": {
            name: round(parts[name].val().Volume() / 1000, 1)
            for name in ("base", "deck", "drill_template", "spacers")
        },
    }
    results["overlap_mm3"]["deck vs Pi spacers"] = overlap(deck, parts["pi_spacers"])
    results["overlap_mm3"]["Pi spacers vs Pi 5"] = overlap(parts["pi_spacers"], pi)
    tol = 1e-3
    results["pass"] = all(v <= tol for v in results["overlap_mm3"].values())
    return results


def build(p: Params) -> dict[str, cq.Workplane]:
    parts = {
        "base": make_base(p),
        "deck": make_deck(p),
        "drill_template": make_drill_template(p),
        "spacers": make_spacers(p),
        "pi_spacers": place_pi_spacers(p),
        "camera_pcb": make_camera_pcb(p),
        "camera_mount": make_camera_mount(p),
        "adapter": make_adapter(p),
        "lens": make_lens(p),
        "pi5": make_pi5(p),
        "lid": make_lid(p),
    }
    parts["camera"] = parts["camera_pcb"].union(parts["camera_mount"])
    return parts


# Parts shown in the assembly, and their colours.
ASSEMBLY = ("lid", "base", "deck", "pi_spacers", "camera_pcb", "camera_mount", "adapter", "lens", "pi5")
COLORS = {
    "base": (0.36, 0.42, 0.48), "deck": (0.45, 0.50, 0.56), "pi_spacers": (0.45, 0.50, 0.56),
    "camera_pcb": (0.12, 0.48, 0.25), "camera_mount": (0.13, 0.13, 0.14),
    "adapter": (0.75, 0.75, 0.78), "lens": (0.08, 0.08, 0.09), "pi5": (0.18, 0.55, 0.34),
    "lid": (0.75, 0.89, 1.0),
}


def print_orientation(name: str, part: cq.Workplane, p: Params) -> cq.Workplane:
    """Rotate and drop each printed part onto Z = 0, ready for slicing."""
    if name == "deck":   # camera bosses up, so nothing needs support
        part = part.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = part.val().BoundingBox()
    return part.translate((0, 0, -bb.zmin))


def export(p: Params, parts: dict[str, cq.Workplane], checks: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name in ("base", "deck", "drill_template", "spacers"):
        cq.exporters.export(parts[name], str(out / f"{name}.step"))
        cq.exporters.export(print_orientation(name, parts[name], p), str(out / f"{name}.stl"),
                            tolerance=0.02, angularTolerance=0.1)
    assy = cq.Assembly(name="ot2_lid_camera_mount")
    for name in ASSEMBLY:
        assy.add(parts[name], name=name, color=cq.Color(*COLORS[name]))
    assy.export(str(out / "assembly.step"))
    (out / "params.json").write_text(json.dumps(asdict(p), indent=2) + "\n")
    (out / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--out", type=Path, default=EXPORTS)
    args = ap.parse_args()
    p = Params()
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
