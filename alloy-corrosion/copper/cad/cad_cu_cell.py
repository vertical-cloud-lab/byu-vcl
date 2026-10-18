"""Parametric CAD for one copper corrosion station on the CubXL: the electrode cap, its
electrode carrier, the well lid and the coupon tray, with the O-rings, steel disc, Ag/AgCl
reference, Pt coil and pogo pins as separate bodies. CadQuery 2.8.

Writes STEP and STL per part, a section-cut STL per part (the 90 degree wedge facing -y
removed: polar angles 225..315 deg about the well axis cut away, -45..225 kept),
assembly.step, cad_parts.json (frames and placement) and cad_preview.png.

Frames (mm, z up, x and y parallel to the CubOS deck):
- W, the well frame: origin on the well axis at the coupon face. Deck = W + (station x, 240, 20).
- C, the cap frame: origin at the centre of the skirt underside. Seated on a lid, C = W + (0, 0, 6).
- D, the deck frame (CubOS, Ben's 2026-10-02 calibration): the full tray only.

Two caps are built. electrode_cap is the recommended one: a close-clearance skirt over the
lid's 16 mm boss (no O-ring), held down by two small magnets in the lid. electrode_cap_oring
is the radial-seal version first proposed (AS568-016 in the skirt). cad_check.py explains why.

    python cad_cu_cell.py          # about 1 min
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
OUT = HERE

# ------------------------------------------------------------------ parameters (mm)
P = dict(
    # well, in W. Shared with ../sim_well*.py: do not change one without the other.
    face_oring_id=2.90, face_oring_cs=1.78,     # AS568-006, FKM 75A
    cbore_d=7.30, cbore_h=1.40,                 # face-seal counterbore: 21 % squeeze
    throat_d=2.90, throat_top=1.60,             # throat from z 1.40 to 1.60
    bore_d=8.0,                                 # 150 uL bore, z 1.60 up
    lid_top=6.0, lid_x=24.0, lid_y=35.0,
    boss_d=16.0, boss_h=4.0, boss_chamfer=0.8,
    clamp_y=14.0, clamp_hole=3.4, clamp_cbore_d=6.5, clamp_cbore_h=3.2,
    pad_r=(10.0, 12.0), pad_half_angle=30.0, foil_t=0.07, tail_x=(9.5, 11.5), eyelet_y=15.0,
    eyelet_x=10.0, eyelet_hole=1.6, eyelet_flange_d=2.8, eyelet_flange_t=0.2,
    hold_r=10.3, hold_angles=(60.0, 240.0), hold_mag_d=4.0, hold_mag_h=2.0, hold_skin=0.4, hold_steel_d=3.0, hold_steel_h=2.0,
    # cap, in C
    cap_d=25.0, flange_d=28.0, flange_z=12.0, cap_top=16.0,  # cap_top: magnet contact plane; 25 mm clears the next lid by 0.5
    recess_d=25.4, recess_h=0.5, disc_t=1.0, glue_t=0.13,
    skirt_clear=0.12,            # radial clearance over the boss (labyrinth)
    ceiling_z=4.3,               # boss top at 4.0 when seated
    socket_d=6.0, socket_h=3.0,  # electrode-carrier socket
    ref_d=2.0, ref_tip_w=3.0, ref_top_c=13.6,   # reference tip 3.0 above the metal (W)
    coil_r=2.625, coil_wire=0.25, coil_z_w=(2.4, 2.8, 3.2, 3.6, 4.0),
    leg_r=(2.75, 3.25), leg_w=0.8, leg_bottom_w=2.2, leg_angles=(30.0, 150.0, 270.0),
    pin_r=11.0, pin_angles=(0.0, 180.0), pin_barrel_d=1.02, pin_plunger_d=0.74,
    pin_protrude=1.0, pin_top_c=10.0,
    # O-ring variant
    rad_oring_id=15.60, rad_oring_cs=1.78,     # AS568-016
    gland_depth=1.55, groove_w=2.40, groove_z=(0.9, 3.3), vent_d=0.3, vent_r=5.0,
    # tray, in D
    tray_rect=(170.0, 220.0, 275.0, 260.0), tray_top=19.5, face_z=20.0,
    stations_x=(185.0, 210.0, 235.0, 260.0), station_y=240.0,
    pocket=20.6, pocket_floor=14.0, insert_d=4.0, insert_h=6.0,
    we_pin_hole=1.4, bus_w=4.0, bus_h=3.0, bus_y=(240.0, 255.0), exit_x=222.5,
    coupon=(20.0, 20.0, 6.0),
)
CUT_KEEP = (-45.0, 225.0)  # polar angles kept in the section versions


# ------------------------------------------------------------------ helpers
def rev(pts, angle=360.0):
    """Revolve a closed (r, z) polyline about the z axis."""
    return cq.Workplane("XZ").polyline(pts).close().revolve(angle, (0, 0, 0), (0, 1, 0)).val()


def cyl(d, z0, z1, x=0.0, y=0.0):
    return cq.Solid.makeCylinder(d / 2, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))


def boxs(x0, y0, z0, x1, y1, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def polar(r, ang):
    a = math.radians(ang)
    return r * math.cos(a), r * math.sin(a)


def wedge(cx=0.0, cy=0.0, R=400.0):
    """The removed wedge: polar angles 225..315 deg about (cx, cy), all z."""
    pts = [(cx, cy), (cx + R * math.cos(math.radians(225)), cy + R * math.sin(math.radians(225))),
           (cx, cy - R * math.sqrt(2)), (cx + R * math.cos(math.radians(315)), cy + R * math.sin(math.radians(315)))]
    return cq.Workplane("XY").workplane(offset=-200).polyline(pts).close().extrude(500).val()


def section(shape, cx=0.0, cy=0.0):
    return shape.cut(wedge(cx, cy))


def union(*shapes):
    s = shapes[0]
    for o in shapes[1:]:
        s = s.fuse(o)
    return s.clean()


def stadium_ring(rc, zc, h, area, axis="z"):
    """Area-conserving squeezed O-ring section: a stadium of height h (squeeze direction)
    with semicircular ends, centred on (rc, zc). axis='z': squeezed in z (face seal);
    axis='r': squeezed radially (radial seal). Returns the solid and the (r, z) outline."""
    w = (area - math.pi * (h / 2) ** 2) / h  # straight length of the flats
    n = 16
    pts = []
    if axis == "z":
        # flats top and bottom, semicircles inside and outside
        for t in [math.pi / 2 + math.pi * k / n for k in range(n + 1)]:  # inner end
            pts.append((rc - w / 2 + (h / 2) * math.cos(t), zc + (h / 2) * math.sin(t)))
        for t in [-math.pi / 2 + math.pi * k / n for k in range(n + 1)]:  # outer end
            pts.append((rc + w / 2 + (h / 2) * math.cos(t), zc + (h / 2) * math.sin(t)))
    else:
        for t in [math.pi + math.pi * k / n for k in range(n + 1)]:  # bottom end
            pts.append((rc + (h / 2) * math.cos(t), zc - w / 2 + (h / 2) * math.sin(t)))
        for t in [math.pi * k / n for k in range(n + 1)]:  # top end
            pts.append((rc + (h / 2) * math.cos(t), zc + w / 2 + (h / 2) * math.sin(t)))
    return rev(pts), pts, w


# ------------------------------------------------------------------ parts
def well_lid():
    """W frame. Printed PETG plate on the coupon face, the face-seal counterbore underneath,
    the 16 mm boss on top, two clamp holes, two pad eyelet holes, two hold-down magnet pockets."""
    p = P
    hx, hy = p["lid_x"] / 2, p["lid_y"] / 2
    lid = boxs(-hx, -hy, 0, hx, hy, p["lid_top"])
    boss = rev([(0, p["lid_top"] - 0.01), (p["boss_d"] / 2, p["lid_top"] - 0.01),
                (p["boss_d"] / 2, p["lid_top"] + p["boss_h"] - p["boss_chamfer"]),
                (p["boss_d"] / 2 - p["boss_chamfer"], p["lid_top"] + p["boss_h"]), (0, p["lid_top"] + p["boss_h"])])
    lid = lid.fuse(boss)
    # liquid path: counterbore, throat, bore
    lid = lid.cut(cyl(p["cbore_d"], -1, p["cbore_h"]))
    lid = lid.cut(cyl(p["throat_d"], p["cbore_h"] - 0.01, p["throat_top"] + 0.01))
    lid = lid.cut(cyl(p["bore_d"], p["throat_top"], p["lid_top"] + p["boss_h"] + 1))
    for sy in (-1, 1):  # M3 clamp screws into heat-set inserts in the tray
        y = sy * p["clamp_y"]
        lid = lid.cut(cyl(p["clamp_hole"], -1, 10, 0, y))
        lid = lid.cut(cyl(p["clamp_cbore_d"], p["lid_top"] - p["clamp_cbore_h"], 10, 0, y))
    for sx in (-1, 1):  # brass eyelets carry each pad through the lid to a tray spring pin
        lid = lid.cut(cyl(p["eyelet_hole"], -1, 10, sx * p["eyelet_x"], p["eyelet_y"]))
    for ang in p["hold_angles"]:  # magnet pockets, closed by a 0.4 mm skin (print pause)
        x, y = polar(p["hold_r"], ang)
        z1 = p["lid_top"] - p["hold_skin"]
        lid = lid.cut(cyl(p["hold_mag_d"] + 0.1, z1 - p["hold_mag_h"] - 0.1, z1, x, y))
    return lid.clean()


def lid_extras():
    """W frame: copper-foil pads with their tails, brass eyelets, hold-down magnets."""
    p = P
    z0, z1 = p["lid_top"], p["lid_top"] + p["foil_t"]
    pads = []
    for base_ang in (0.0, 180.0):
        a0, a1 = base_ang - p["pad_half_angle"], base_ang + p["pad_half_angle"]
        r0, r1 = p["pad_r"]
        n = 12
        pts = [polar(r0, a0 + (a1 - a0) * k / n) for k in range(n + 1)] + [polar(r1, a1 - (a1 - a0) * k / n) for k in range(n + 1)]
        arc = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(p["foil_t"]).val()
        sx = 1 if base_ang == 0 else -1
        xa, xb = sorted((sx * p["tail_x"][0], sx * p["tail_x"][1]))
        tail = boxs(xa, 0, z0, xb, p["eyelet_y"] + 1.4, z1)
        pads.append(arc.fuse(tail).clean())
    eyelets = []
    for sx in (-1, 1):
        x, y = sx * p["eyelet_x"], p["eyelet_y"]
        e = cyl(p["eyelet_hole"] - 0.05, -p["eyelet_flange_t"], p["lid_top"] + p["foil_t"], x, y)
        e = e.fuse(cyl(p["eyelet_flange_d"], p["lid_top"] + p["foil_t"], p["lid_top"] + p["foil_t"] + p["eyelet_flange_t"], x, y))
        e = e.fuse(cyl(p["eyelet_flange_d"], -p["eyelet_flange_t"], 0.0, x, y))
        e = e.cut(cyl(0.9, -1, 10, x, y))
        eyelets.append(e.clean())
    mags = []
    for ang in p["hold_angles"]:
        x, y = polar(p["hold_r"], ang)
        z1 = p["lid_top"] - p["hold_skin"]
        mags.append(cyl(p["hold_mag_d"], z1 - p["hold_mag_h"], z1, x, y))
    return union(*pads), union(*eyelets), union(*mags)


def face_oring():
    """W frame: the AS568-006 squeezed to the counterbore depth, area conserved."""
    p = P
    area = math.pi / 4 * p["face_oring_cs"] ** 2
    rc = p["face_oring_id"] / 2 + p["face_oring_cs"] / 2
    solid, pts, w = stadium_ring(rc, p["cbore_h"] / 2, p["cbore_h"], area, axis="z")
    return solid, pts, w, rc


def cap_body(variant="clearance"):
    """C frame. Printed PETG, skirt down on the bed. The top is the vial cap's: 28 mm across,
    a 25.4 mm recess 0.5 mm deep for the steel disc."""
    p = P
    floor = p["cap_top"] - p["disc_t"] - p["glue_t"]  # recess floor
    rim = floor + p["recess_h"]
    r_cap, r_fl = p["cap_d"] / 2, p["flange_d"] / 2
    outer = [(0, 0), (r_cap, 0), (r_cap, p["flange_z"] - (r_fl - r_cap)), (r_fl, p["flange_z"]), (r_fl, rim),
             (p["recess_d"] / 2, rim), (p["recess_d"] / 2, floor), (0, floor)]
    body = rev(outer)
    r_bore = p["boss_d"] / 2 + p["skirt_clear"]
    ch = 0.8
    bore = rev([(0, -1), (r_bore + ch + 1, -1), (r_bore + ch, 0.0), (r_bore, ch), (r_bore, p["ceiling_z"]), (0, p["ceiling_z"])])
    body = body.cut(bore)
    body = body.cut(cyl(p["socket_d"], p["ceiling_z"] - 0.01, p["ceiling_z"] + p["socket_h"]))
    body = body.cut(cyl(p["ref_d"] + 0.05, p["ceiling_z"], floor + 0.01))  # reference bore, opens to the recess floor
    # coil lead: a 0.6 mm hole from the socket to the recess floor at r 2.625 toward +x
    body = body.cut(cyl(0.6, p["ceiling_z"], floor + 0.01, p["coil_r"], 0.0))
    for ang in p["pin_angles"]:  # pogo pins, their wire holes up to the recess floor
        x, y = polar(p["pin_r"], ang)
        body = body.cut(cyl(p["pin_barrel_d"] - 0.02, -1, p["pin_top_c"], x, y))
        body = body.cut(cyl(1.6, p["pin_top_c"], floor + 0.01, x, y))
    # wire grooves in the recess floor (0.6 deep): reference to the -x pin, coil lead to the +x pin
    body = body.cut(boxs(-p["pin_r"], -0.6, floor - 0.6, 0.0, 0.6, floor + 0.01))
    body = body.cut(boxs(p["coil_r"], -0.6, floor - 0.6, p["pin_r"], 0.6, floor + 0.01))
    if variant == "clearance":
        for ang in p["hold_angles"]:  # steel hold-down slugs, 3 x 2 mm, in the skirt underside
            x, y = polar(p["hold_r"], ang)
            body = body.cut(cyl(p["hold_steel_d"] + 0.05, -1, p["hold_steel_h"], x, y))
    else:
        r_g = p["boss_d"] / 2 + p["gland_depth"]
        z0, z1 = p["groove_z"]
        # rectangular groove with a 45 degree roof so it prints skirt-down without support
        body = body.cut(rev([(r_bore - 0.01, z0), (r_g, z0), (r_g, z1), (r_bore - 0.01, z1 + (r_g - r_bore))]))
        # 0.3 mm vent through the ceiling into a printed 1 mm side channel
        vx, vy = polar(p["vent_r"], 90.0)
        body = body.cut(cyl(p["vent_d"], p["ceiling_z"] - 0.01, 9.0, vx, vy))
        body = body.cut(cq.Solid.makeCylinder(0.5, r_cap - p["vent_r"] + 1, cq.Vector(vx, vy, 9.0), cq.Vector(0, 1, 0)))
    return body.clean(), floor, rim


def electrode_carrier():
    """C frame. Separate PETG part, printed flange-down: press-fits into the cap's socket,
    holds the reference straight and carries the Pt coil on three legs."""
    p = P
    z_fl0 = p["ceiling_z"] - 0.6
    body = union(cyl(p["socket_d"] - 0.05, p["ceiling_z"] - 0.01, p["ceiling_z"] + p["socket_h"]),
                 cyl(7.6, z_fl0, p["ceiling_z"]), cyl(4.0, 0.5, z_fl0 + 0.01))
    zw = lambda z: z - p["lid_top"]  # W height to C height for the seated cap
    z_leg0 = zw(p["leg_bottom_w"])
    legs = []
    for ang in p["leg_angles"]:
        a = math.radians(ang)
        leg = boxs(p["leg_r"][0], -p["leg_w"] / 2, z_leg0, p["leg_r"][1], p["leg_w"] / 2, z_fl0 + 0.01)
        leg = leg.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), ang)
        legs.append(leg)
    body = union(body, *legs)
    body = body.cut(cyl(p["ref_d"] + 0.05, -10, 20))
    body = body.cut(cyl(0.6, -10, 20, p["coil_r"], 0.0))
    return body.clean()


def electrodes():
    """C frame: steel disc, Ag/AgCl reference, Pt coil (five rings plus the lead), pogo pins."""
    p = P
    floor = p["cap_top"] - p["disc_t"] - p["glue_t"]
    disc = cyl(p["recess_d"] - 0.1, floor + p["glue_t"], p["cap_top"])
    zw = lambda z: z - p["lid_top"]
    ref = cyl(p["ref_d"], zw(p["ref_tip_w"]), p["ref_top_c"])
    rings = [cq.Solid.makeTorus(p["coil_r"], p["coil_wire"] / 2, cq.Vector(0, 0, zw(z)), cq.Vector(0, 0, 1)) for z in p["coil_z_w"]]
    lead = cyl(p["coil_wire"], zw(p["coil_z_w"][-1]), p["ceiling_z"] + p["socket_h"], p["coil_r"], 0.0)
    coil = union(*rings, lead)
    pins = []
    for ang in p["pin_angles"]:
        x, y = polar(p["pin_r"], ang)
        barrel = cyl(p["pin_barrel_d"], 0.0, p["pin_top_c"], x, y)
        plunger = cyl(p["pin_plunger_d"], -p["pin_protrude"], 0.01, x, y)
        tip = cq.Solid.makeCone(p["pin_plunger_d"] / 2, 0.05, 0.4, cq.Vector(x, y, -p["pin_protrude"]), cq.Vector(0, 0, -1))
        pins.append(union(barrel, plunger, tip))
    steel = [cyl(p["hold_steel_d"], 0.0, p["hold_steel_h"], *polar(p["hold_r"], ang)) for ang in p["hold_angles"]]
    return disc, ref, coil, union(*pins), union(*steel)


def radial_oring():
    """C frame: AS568-016 in the skirt groove, squeezed radially onto the 16 mm boss (seated),
    and free in the groove (carried)."""
    p = P
    area = math.pi / 4 * p["rad_oring_cs"] ** 2
    h = p["gland_depth"]
    rc = p["boss_d"] / 2 + h / 2
    zc = sum(p["groove_z"]) / 2 - 0.1
    seated, pts, w = stadium_ring(rc, zc, h, area, axis="r")
    r_free = (p["boss_d"] / 2 + p["gland_depth"]) - p["rad_oring_cs"] / 2  # OD against the groove bottom
    free = cq.Solid.makeTorus(r_free, p["rad_oring_cs"] / 2, cq.Vector(0, 0, zc), cq.Vector(0, 0, 1))
    return seated, free, pts


def coupon_tray():
    """D frame. Printed PETG tray: four square pockets, WE spring pins from below, M3 inserts,
    pad spring pins, and the bus channels in the underside."""
    p = P
    x0, y0, x1, y1 = p["tray_rect"]
    tray = boxs(x0, y0, 0, x1, y1, p["tray_top"])
    q = p["pocket"] / 2
    for sx in p["stations_x"]:
        sy = p["station_y"]
        tray = tray.cut(boxs(sx - q, sy - q, p["pocket_floor"], sx + q, sy + q, 30))
        for cx, cy in ((sx - q, sy - q), (sx + q, sy - q), (sx - q, sy + q), (sx + q, sy + q)):
            tray = tray.cut(cyl(1.6, p["pocket_floor"], 30, cx, cy))  # corner reliefs
        tray = tray.cut(boxs(sx + 2.0, sy + q - 0.1, p["pocket_floor"] + 1.0, sx + 6.0, sy + q + 2.0, 30))  # pry slot
        tray = tray.cut(cyl(p["we_pin_hole"], 1.0, 30, sx, sy))  # WE spring pin
        for sgn in (-1, 1):
            tray = tray.cut(cyl(p["insert_d"], p["tray_top"] - p["insert_h"], 30, sx, sy + sgn * p["clamp_y"]))
        for sgn in (-1, 1):
            tray = tray.cut(cyl(p["we_pin_hole"], 1.0, 30, sx + sgn * p["eyelet_x"], sy + p["eyelet_y"]))
        # branches of the bus to the WE pin and the pad pins
        tray = tray.cut(boxs(sx - p["bus_w"] / 2, p["bus_y"][0], -1, sx + p["bus_w"] / 2, p["bus_y"][1], p["bus_h"]))
        for sgn in (-1, 1):
            xp = sx + sgn * p["eyelet_x"]
            tray = tray.cut(boxs(xp - 1.5, p["bus_y"][1], -1, xp + 1.5, sy + p["eyelet_y"] + 1.5, p["bus_h"]))
    for yb in p["bus_y"]:
        tray = tray.cut(boxs(p["stations_x"][0] - p["eyelet_x"] - 2, yb - p["bus_w"] / 2, -1,
                             p["stations_x"][-1] + p["eyelet_x"] + 2, yb + p["bus_w"] / 2, p["bus_h"]))
    tray = tray.cut(boxs(p["exit_x"] - p["bus_w"] / 2, p["bus_y"][0], -1, p["exit_x"] + p["bus_w"] / 2, y1 + 1, p["bus_h"]))
    return tray.clean()


def tray_pins():
    """D frame: the WE spring pins (one per pocket) and the pad spring pins (two per station)."""
    p = P
    pins = []
    for sx in p["stations_x"]:
        sy = p["station_y"]
        for x, y, top in [(sx, sy, p["pocket_floor"] + 1.0)] + [(sx + s * p["eyelet_x"], sy + p["eyelet_y"], p["tray_top"] + 1.0) for s in (-1, 1)]:
            pins.append(union(cyl(p["pin_barrel_d"], top - 11.0, top - 1.0, x, y), cyl(p["pin_plunger_d"], top - 1.01, top, x, y)))
    return union(*pins)


def coupon():
    """W frame: a 20 x 20 x 6 mm sectioned piece, face at z 0."""
    a, b, t = P["coupon"]
    return boxs(-a / 2, -b / 2, -t, a / 2, b / 2, 0)


def ptfe_blank():
    """W frame: S4's blank, a 20 mm PTFE disc 6 mm thick turned from rod, face at z 0."""
    return cyl(20.0, -6.0, 0.0)


def shim(t):
    a = P["pocket"] - 0.2
    return boxs(-a / 2, -a / 2, 0, a / 2, a / 2, t).cut(cyl(3.0, -1, t + 1))


# ------------------------------------------------------------------ export
def export(name, shape, tol=0.02, ang=0.25, section_about=(0.0, 0.0), step=True):
    files = {}
    if step:
        cq.exporters.export(cq.Workplane().add(shape), str(OUT / f"{name}.step"))
        files["step"] = f"{name}.step"
    cq.exporters.export(cq.Workplane().add(shape), str(OUT / f"{name}.stl"), tolerance=tol, angularTolerance=ang)
    files["stl"] = f"{name}.stl"
    if section_about is not None:
        sec = section(shape, *section_about)
        cq.exporters.export(cq.Workplane().add(sec), str(OUT / f"{name}_section.stl"), tolerance=tol, angularTolerance=ang)
        files["section_stl"] = f"{name}_section.stl"
    return files


def main():
    p = P
    parts = {}
    lid = well_lid()
    pads, eyelets, mags = lid_extras()
    f_oring, f_pts, f_w, f_rc = face_oring()
    cap, floor, rim = cap_body("clearance")
    cap_o, _, _ = cap_body("oring")
    carrier = electrode_carrier()
    disc, ref, coil, pins, steel = electrodes()
    r_seated, r_free, r_pts = radial_oring()
    tray = coupon_tray()
    tpins = tray_pins()
    cpn, blank = coupon(), ptfe_blank()

    W = "W: well frame, origin on the well axis at the coupon face; deck = W + (station_x, 240, 20)"
    Cs = "C: cap frame, origin at the centre of the skirt underside; seated on a lid, C = W + (0, 0, 6.0); carried, C = carriage + (0, 0, -(16 + 16))"
    D = "D: CubOS deck frame (Ben's 2026-10-02 calibration), use as is"
    table = [
        ("well_lid", lid, W, "printed PETG; one per station; boss top at W z 10.0, lid top 6.0", 0.02),
        ("lid_pads", pads, W, "copper-foil pads (3M 1181) at r 10-12, +/-30 deg about +x (CE) and -x (RE), tails to the eyelets", 0.01),
        ("lid_eyelets", eyelets, W, "brass eyelets, 1.6 mm, at (+/-10, 15)", 0.01),
        ("lid_hold_magnets", mags, W, "two 4 x 2 mm NdFeB discs under a 0.4 mm skin at r 10.3, 60 and 240 deg", 0.01),
        ("face_oring_006", f_oring, W, "AS568-006 FKM squeezed to 1.40 mm in the counterbore (assembly shape)", 0.005),
        ("electrode_cap", cap, Cs, "recommended: 0.12 mm clearance skirt, no O-ring; disc top (magnet contact) at C z 16.0", 0.02),
        ("electrode_cap_oring", cap_o, Cs, "alternative: AS568-016 radial seal in the skirt, 0.3 mm vent", 0.02),
        ("electrode_carrier", carrier, Cs, "press-fits into the cap; reference guide and three coil legs", 0.01),
        ("steel_disc", disc, Cs, "25.3 x 1.0 mm low-carbon steel on 0.13 mm 3M 468MP", 0.01),
        ("ag_agcl_ref", ref, Cs, "2.0 mm leak-free Ag/AgCl, tip at C z -3.0 (W z 3.0), top at C z 13.6", 0.005),
        ("pt_coil", coil, Cs, "0.25 mm Pt, five rings at W z 2.4-4.0, r 2.625, lead to the carrier", 0.01),
        ("cap_pogo_pins", pins, Cs, "P75-B1 class, at (+/-11, 0); drawn free (1.0 mm out); seated they compress to the pad", 0.005),
        ("cap_hold_steel", steel, Cs, "3 x 2 mm steel slugs in the skirt underside at r 10.3 (recommended cap only)", 0.01),
        ("radial_oring_016_seated", r_seated, Cs, "AS568-016 squeezed on the boss (O-ring cap, seated)", 0.005),
        ("radial_oring_016_free", r_free, Cs, "AS568-016 in its groove (O-ring cap, carried)", 0.005),
        ("coupon_20x20x6", cpn, W, "a sectioned piece, face at W z 0", 0.02),
        ("ptfe_blank", blank, W, "S4 blank, 20 mm PTFE disc, 6 mm thick", 0.02),
    ]
    for name, shape, frame, what, tol in table:
        files = export(name, shape, tol=tol)
        parts[name] = {"frame": frame.split(":")[0], "what": what, **files}
    for t in (1.0, 3.0):
        files = export(f"shim_{t:.0f}mm", shim(t), section_about=None)
        parts[f"shim_{t:.0f}mm"] = {"frame": "W (place at W z -6 for the pocket floor)", "what": f"{t:.0f} mm shim under a thinner piece", **files}
    # tray: the full tray in D, one station block (S1) in W, and the tray minus that block in D
    files = export("coupon_tray", tray, tol=0.05, ang=0.3, section_about=None)
    parts["coupon_tray"] = {"frame": "D", "what": "printed PETG tray, 105 x 40 x 19.5 mm, four stations", **files}
    files = export("tray_spring_pins", tpins, tol=0.01, section_about=None)
    parts["tray_spring_pins"] = {"frame": "D", "what": "WE pins under each pocket and pad pins under each lid's eyelets", **files}
    sx1 = p["stations_x"][0]
    block_d = boxs(p["tray_rect"][0], p["tray_rect"][1], -1, sx1 + 12.5, p["tray_rect"][3], 30)
    s1 = tray.intersect(block_d).translate(cq.Vector(-sx1, -p["station_y"], -p["face_z"]))
    files = export("tray_station", s1, tol=0.03)
    parts["tray_station"] = {"frame": "W", "what": "the S1 block of the tray (x 170-197.5 in D), for the section view", **files}
    rest = tray.cut(block_d)
    files = export("coupon_tray_minus_s1", rest, tol=0.05, ang=0.3, section_about=None)
    parts["coupon_tray_minus_s1"] = {"frame": "D", "what": "the tray without the S1 block; add tray_station(_section) at S1", **files}

    # the seated assembly at S1, in D, as one STEP
    def at_station(shape, frame, sx=sx1):
        off = (sx, p["station_y"], p["face_z"]) if frame == "W" else (sx, p["station_y"], p["face_z"] + p["lid_top"])
        return shape.translate(cq.Vector(*off))
    assy = cq.Assembly(name="cubxl_cu_station")
    rgb = {"lid": (0.91, 0.64, 0.49), "cap": (0.94, 0.91, 0.89), "grey": (0.55, 0.57, 0.59), "ref": (0.91, 0.90, 0.87),
           "pt": (0.78, 0.79, 0.80), "fkm": (0.11, 0.11, 0.11), "cuni": (0.72, 0.60, 0.54), "brass": (0.79, 0.65, 0.29),
           "tray": (0.96, 0.94, 0.90), "ptfe": (0.97, 0.97, 0.96)}
    colours = {"well_lid": "lid", "electrode_cap": "cap", "electrode_carrier": "grey", "steel_disc": "grey",
               "ag_agcl_ref": "ref", "pt_coil": "pt", "face_oring_006": "fkm", "coupon_20x20x6": "cuni"}
    col = lambda k: cq.Color(*rgb[k])
    assy.add(tray, name="coupon_tray", color=col("tray"))
    for name, shape, frame in (("well_lid", lid, "W"), ("face_oring_006", f_oring, "W"), ("coupon_20x20x6", cpn, "W"),
                               ("lid_pads", pads, "W"), ("lid_eyelets", eyelets, "W"), ("lid_hold_magnets", mags, "W"),
                               ("electrode_cap", cap, "C"), ("electrode_carrier", carrier, "C"), ("steel_disc", disc, "C"),
                               ("ag_agcl_ref", ref, "C"), ("pt_coil", coil, "C"), ("cap_pogo_pins", pins, "C"),
                               ("cap_hold_steel", steel, "C")):
        assy.add(at_station(shape, frame), name=name, color=col(colours.get(name, "brass")))
    for sx in p["stations_x"][1:]:
        assy.add(at_station(lid, "W", sx), name=f"well_lid_{sx:.0f}", color=col("lid"))
        assy.add(at_station(f_oring, "W", sx), name=f"face_oring_{sx:.0f}", color=col("fkm"))
        assy.add(at_station(blank if sx == p["stations_x"][-1] else cpn, "W", sx), name=f"piece_{sx:.0f}",
                 color=col("ptfe" if sx == p["stations_x"][-1] else "cuni"))
    assy.add(tpins, name="tray_spring_pins", color=col("brass"))
    assy.save(str(OUT / "assembly.step"))

    meta = {
        "units": "mm",
        "frames": {"W": W, "C": Cs, "D": D},
        "section_versions": "*_section.stl: the 90 degree wedge facing -y removed (polar angles 225..315 deg about the part's own well axis), "
                            "kept -45..225 deg; boolean cuts, so the cut faces are closed. tray_station_section is about S1's axis.",
        "placement": {
            "W_to_deck": "deck = W + (station_x, 240.0, 20.0); stations_x = " + str(list(p["stations_x"])),
            "C_seated_to_deck": "deck = C + (station_x, 240.0, 26.0)",
            "C_carried": "C origin = carriage reference - 32.0 (magnet face 16 below the carriage, cap top 16 above C origin)",
            "lowest_point_carried_C": min(-p["pin_protrude"] - 0.4, p["leg_bottom_w"] - p["lid_top"]),  # the carrier legs
            "reference_tip_C": -(p["lid_top"] - p["ref_tip_w"]),
            "coil_bottom_C": round(P["coil_z_w"][0] - p["lid_top"] - p["coil_wire"] / 2, 3),
            "carrier_legs_bottom_C": p["leg_bottom_w"] - p["lid_top"],
        },
        "heights": {
            "coupon_face_W": 0.0, "lid_top_W": p["lid_top"], "boss_top_W": p["lid_top"] + p["boss_h"], "pads_top_W": p["lid_top"] + p["foil_t"],
            "cap_ceiling_C": p["ceiling_z"], "cap_flange_C": p["flange_z"], "cap_rim_C": round(rim, 3), "recess_floor_C": round(floor, 3),
            "magnet_contact_plane_C": p["cap_top"], "cap_outer_d": p["cap_d"], "cap_flange_d": p["flange_d"],
            "tray_top_D": p["tray_top"], "pocket_floor_D": p["pocket_floor"], "lid_top_D": p["face_z"] + p["lid_top"],
            "cap_top_seated_D": p["face_z"] + p["lid_top"] + p["cap_top"],
        },
        "face_oring_section_rz": [[round(r, 4), round(z, 4)] for r, z in f_pts],
        "face_oring_contact_on_metal_r": [round(f_rc - f_w / 2, 4), round(f_rc + f_w / 2, 4)],
        "face_oring_inner_bulge_r": round(f_rc - f_w / 2 - p["cbore_h"] / 2, 4),
        "radial_oring_seated_section_rz": [[round(r, 4), round(z, 4)] for r, z in r_pts],
        "parameters": p,
        "parts": parts,
    }
    (OUT / "cad_parts.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps({k: meta[k] for k in ("heights", "face_oring_contact_on_metal_r", "face_oring_inner_bulge_r")}, indent=1))


if __name__ == "__main__":
    main()
