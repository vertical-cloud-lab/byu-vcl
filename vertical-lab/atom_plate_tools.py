"""Tools, fixtures and racks for the plate swap (atom_plate.py, PR #353 for #303). All drawn with PyVista primitives.

What is the lab's and what is ours (notes/atom_plate.md has the sources):
* The plate, the connector, the sonotrodes, the door and its clamps are the rePowder model's (repowder/model.py).
  Three local overrides, drawn here and used only in this clip, because the model's parts can't do what the SOP needs:
  - the upper sonotrode gets two 17 mm wrench flats (the SOP torques it with a 17 mm wrench, step 13; the model draws
    it round) and two Sharpie lines (DAL #164);
  - the door's two swing bolts are redrawn standing 22 mm further off the front face, on lugs added to the door's
    front edge. As modelled, the knob's lobes reach 10 mm behind the face plane (y -110 against the face at -120), so
    swinging the bolt along the face would cut through the chamber, and the top bolt's pin sits inside the viewport
    hood (FCL: 8.7 mm deep shut, 37 mm at 180 deg). The top bolt here swings 60 deg up (the hood is in the way of
    more, and the lug's path rules out less); the lower one 180 deg over the top, as in T5 27:16. Pin heights are the
    model's; the top pin is 22 mm further left (clear of the hood).
* Ours, to make: the stack wrench (two coaxial 17 mm heads, one fixed to counter-hold the lower sonotrode's flats,
  one driven through a slip clutch set to 50 N m; the reaction closes inside the tool), its holder, the plate rack,
  the upper sonotrode's tray, the gauge plate's holder, the IPA dropper's holder and the wipe pad's holder.
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

import atom_base as AB
from scene import R, T

M = AB.M
g = AB.g

# ------------------------------------------------------------------------------------------------ the stack's frame
SD = np.asarray(M.STACK_DIR, float)
AL, AC = (np.asarray(v, float) for v in M.plate_dirs(M.SETUP.clock))
TIP = np.asarray(M.TIP, float)


def stack_frame() -> np.ndarray:
    """Model frame (door shut) of the stack: origin on the axis at the Ti sonotrode's tip face (the plate's back face),
    x along the plate towards its free end, y across it, z along the axis into the chamber (model.stack_parts)."""
    F = np.eye(4)
    F[:3, 0], F[:3, 1], F[:3, 2], F[:3, 3] = AL, AC, SD, TIP
    return F


FS = stack_frame()
FS_INV = np.linalg.inv(FS)

# sizes (model.py, #261) and the SOP's numbers
PLATE_L, PLATE_W, PLATE_T = M.PLATE_L, M.PLATE_W, M.PLATE_T
HOLE_E = M.HOLE_E
UPPER_R, UPPER_L = M.UPPER_R, M.UPPER_L
FLATS = 17.0                       # the SOP's 17 mm wrenches (253 step 13; 178 step 9)
UP_FLAT_Z = (M.PLATE_T + UPPER_L - 12.0, M.PLATE_T + UPPER_L)   # ours: 12 mm flats at the free end (not recorded)
LOW_FLAT_Z = (-14.0, -2.0)                           # the Ti sonotrode's flats (model.stack_parts)
SHARPIE_Z = (M.PLATE_T + 36.0, M.PLATE_T + 42.0)     # ours: 3 mm either side of #164's "about 3.9 cm"
M8_PITCH = 1.25                    # M8 coarse; the connector stud is M8 at the plate end (178 step 2, T7 29:31)
THREAD_TURNS = (M.CONN_HALF - M.PLATE_T) / M8_PITCH   # 7.6 turns of the upper sonotrode on the connector
TORQUE = 50.0                      # N m, upper to lower (253 step 13; 178 step 5: 55 allowed, 50 safer)

STEEL = (0.62, 0.64, 0.67)
DARK = (0.20, 0.21, 0.23)
TOOL_BLUE = (0.16, 0.33, 0.62)
TOOL_RED = (0.72, 0.16, 0.12)
BLACK = (0.07, 0.07, 0.08)
CF = M.CARBON
W_COAT = (0.50, 0.51, 0.55)        # plasma-sprayed W on CF: matte grey (colour assumed)
LABEL = (0.97, 0.97, 0.95)
SHARPIE = (0.05, 0.05, 0.06)
RACK = (0.86, 0.87, 0.88)


def box(x0, x1, y0, y1, z0, z1) -> pv.PolyData:
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))).triangulate()


def cyl(r, z0, z1, res=32, x=0.0, y=0.0) -> pv.PolyData:
    """A cylinder along z from z0 to z1, its axis at (x, y)."""
    return pv.Cylinder(center=(x, y, (z0 + z1) / 2), direction=(0, 0, 1), radius=r, height=abs(z1 - z0),
                       resolution=res, capping=True).triangulate()


def along(mesh: pv.PolyData, origin, direction) -> pv.PolyData:
    """A mesh built along +z from the origin, turned so +z is `direction` and moved to `origin`."""
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(z, d)
    s, c = np.linalg.norm(v), float(z @ d)
    if s < 1e-9:
        Rm = np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    else:
        K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        Rm = np.eye(3) + K + K @ K * ((1 - c) / s ** 2)
    Mx = np.eye(4)
    Mx[:3, :3], Mx[:3, 3] = Rm, origin
    return mesh.transform(Mx, inplace=False)


def merge(*ms) -> pv.PolyData:
    out = ms[0].copy()
    for m in ms[1:]:
        out = out.merge(m)
    return out


def put(mesh, Mx) -> pv.PolyData:
    return mesh.transform(np.asarray(Mx, float), inplace=False)


# ------------------------------------------------------------------------------------------------ the plate
def plate_local(ms) -> pv.PolyData:
    """The model's plate (119.6 x 20.8 x 2.5, its 8 mm hole HOLE_E from its back end) in the stack frame: the hole's
    centre at the origin, the plate's back face on z = 0."""
    return put(ms["plate"]["whole"], FS_INV)


def plate_tag(color=LABEL) -> pv.PolyData:
    """The plate's label: a tag on the face near the free end (ours: an engraved ID or a tag; 178: "label them")."""
    x = PLATE_L - HOLE_E - 20.0
    return box(x - 8, x + 8, -6, 6, PLATE_T, PLATE_T + 0.3)


# ------------------------------------------------------------------------------------------------ upper sonotrode
def upper_local() -> pv.PolyData:
    """The W-Ni-Fe upper sonotrode (19.9 x 56.6, #261) in the stack frame, its face on the plate (z = PLATE_T), with
    the 17 mm flats (ours: where) and its M8 bore."""
    z0, z1 = M.PLATE_T, M.PLATE_T + UPPER_L
    zb = M.CONN_HALF + 0.6                               # the M8 bore's end (model.stack_parts)
    body = cyl(UPPER_R, zb, z1, res=40)
    bore = merge(pv.Cylinder(center=(0, 0, (z0 + zb) / 2), direction=(0, 0, 1), radius=UPPER_R, height=zb - z0,
                             resolution=40, capping=False).triangulate(),
                 pv.Cylinder(center=(0, 0, (z0 + zb) / 2), direction=(0, 0, 1), radius=M.CONN_R + 0.4, height=zb - z0,
                             resolution=24, capping=False).triangulate(),
                 pv.Disc(center=(0, 0, z0), inner=M.CONN_R + 0.4, outer=UPPER_R, normal=(0, 0, 1), c_res=40).triangulate())
    f0, f1 = UP_FLAT_Z
    body = body.clip_box((FLATS / 2, UPPER_R + 2, -UPPER_R - 2, UPPER_R + 2, f0, f1), invert=True)
    body = body.clip_box((-UPPER_R - 2, -FLATS / 2, -UPPER_R - 2, UPPER_R + 2, f0, f1), invert=True)
    body = body.extract_surface().triangulate()
    # the flats' faces (clip_box leaves the cut open): thin plates to close them
    faces = [box(s * FLATS / 2 - 0.3 * s, s * FLATS / 2, -math.sqrt(UPPER_R ** 2 - (FLATS / 2) ** 2),
                 math.sqrt(UPPER_R ** 2 - (FLATS / 2) ** 2), f0, f1) for s in (-1, 1)]
    return merge(body, bore, *faces)


def sharpie_local() -> pv.PolyData:
    rings = [pv.Cylinder(center=(0, 0, z), direction=(0, 0, 1), radius=UPPER_R + 0.15, height=0.9, resolution=40,
                         capping=False).triangulate() for z in SHARPIE_Z]
    return merge(*rings)


# ------------------------------------------------------------------------------------------------ door bolts (ours)
BOLT_Y = M.CH_Y[0] - 30.0            # the rod's axis, 30 mm in front of the face (the model's: 8)
PIN_X = (-112.0, M.DCLAMP_X)         # top: 22 mm left of the model's -90, clear of the viewport hood; lower: -90
BOLT_Z = M.DCLAMP_Z                  # 1035, 840 (DAL #189 heights)
LUG_X = (M.CH_X[0] - M.DOOR_T, M.CH_X[0] - M.DOOR_T + 8.0)   # the model's ear: x -131..-123
KNOB_GAP = 1.5                       # the knob's face against the lug when tight (1.5: drawn a hair off, so the mesh
                                     # facets don't read as a contact)
KNOB_PITCH = 1.75                    # M12 coarse (assumed)
KNOB_TURNS = 1.0                     # the arm backs each knob off one turn, 1.75 mm (ours)
SWING_DEG = (60.0, 180.0)            # top: 60 deg up, clear of the hood and of the lug's path; lower: over the top (T5 27:16)
LOBES_R, LOBE_R, HUB_R, HUB_L = 13.0, 5.0, 10.0, 14.0


def bolt_geom(k):
    pin = np.array([PIN_X[k], BOLT_Y, BOLT_Z[k]])
    lug_out = LUG_X[0]                                        # the lug's outer face
    knob0 = pin[0] - lug_out                                  # pin to the knob's inner face, along the rod (-x)
    rod_l = knob0 + HUB_L + 6.0
    return pin, knob0, rod_l


def bolt_meshes(k):
    """(rod with pin head, knob, bracket) in the model frame, the bolt shut (rod pointing -x)."""
    pin, knob0, rod_l = bolt_geom(k)
    rod = merge(along(cyl(3.5, 0, rod_l), pin, (-1, 0, 0)),
                along(cyl(6.5, -6, 6), pin, (0, 1, 0)))
    c = pin + np.array([-(knob0 + KNOB_GAP), 0, 0])
    lobes = [along(cyl(LOBE_R, 0, 10), c + LOBES_R * np.array([0, math.cos(t), math.sin(t)]) + np.array([-2, 0, 0]),
                   (-1, 0, 0)) for t in np.linspace(math.pi / 2, math.pi / 2 + 2 * math.pi, 5, endpoint=False)]
    hub = merge(pv.Cylinder(center=(0, 0, HUB_L / 2), direction=(0, 0, 1), radius=HUB_R, height=HUB_L, resolution=32,
                            capping=False).triangulate(),
                pv.Cylinder(center=(0, 0, HUB_L / 2), direction=(0, 0, 1), radius=4.2, height=HUB_L, resolution=24,
                            capping=False).triangulate(),
                pv.Disc(center=(0, 0, 0), inner=4.2, outer=HUB_R, normal=(0, 0, 1), c_res=32).triangulate(),
                pv.Disc(center=(0, 0, HUB_L), inner=4.2, outer=HUB_R, normal=(0, 0, 1), c_res=32).triangulate())
    knob = merge(along(hub, c, (-1, 0, 0)), *lobes)       # the hub is bored for the rod (M12 thread, assumed)
    # the bracket: a block on the face and a standoff post out to the rod, the pin through it (along y)
    y0 = M.CH_Y[0]
    bracket = merge(box(pin[0] - 14, pin[0] + 14, y0 - 6, y0, pin[2] - 14, pin[2] + 14),
                    box(pin[0] - 9, pin[0] + 9, BOLT_Y + 7, y0 - 6, pin[2] - 9, pin[2] + 9))
    return rod, knob, bracket, c


def lug_meshes():
    """Lugs on the door's front edge, out to the bolts' line: a fork open on top for the rod (ours)."""
    out = []
    for k in range(2):
        pin, _, _ = bolt_geom(k)
        z = BOLT_Z[k]
        x0, x1 = LUG_X
        web = box(x0, x1, -M.DOOR_W / 2 + 2, BOLT_Y + 6, z - 11, z + 11)
        cheeks = [box(x0, x1, BOLT_Y - 12, BOLT_Y - 4.2, z - 11, z + 11),
                  box(x0, x1, BOLT_Y - 4.2, BOLT_Y + 6, z - 11, z - 4.2)]
        out.append(merge(web, *cheeks))
    return merge(*out)


def bolt_matrix(k, swing: float, turn: float) -> tuple[np.ndarray, np.ndarray]:
    """(rod's model-frame matrix, knob's matrix in the rod's frame): swing 0..1 of SWING_DEG[k] about the pin (+y:
    the rod's free end goes up), turn 0..1 of KNOB_TURNS (the knob unscrewed: it turns about the rod and backs off)."""
    pin, _, _ = bolt_geom(k)
    Mr = R((0, 1, 0), SWING_DEG[k] * swing, pin)
    ang = 360.0 * KNOB_TURNS * turn
    Mk = T((-KNOB_PITCH * KNOB_TURNS * turn, 0, 0)) @ R((1, 0, 0), -ang, pin)
    return Mr, Mk


def knob_centre(k, swing=0.0, turn=0.0) -> np.ndarray:
    """The knob's grip point (its lobes' mid-length on the rod's axis), model frame."""
    pin, knob0, _ = bolt_geom(k)
    Mr, Mk = bolt_matrix(k, swing, turn)
    p = pin + np.array([-(knob0 + KNOB_GAP + 7.0), 0, 0])
    return (Mr @ Mk @ np.r_[p, 1.0])[:3]


def rod_dir(k, swing=0.0) -> np.ndarray:
    Mr, _ = bolt_matrix(k, swing, 0.0)
    return Mr[:3, :3] @ np.array([-1.0, 0.0, 0.0])


# ------------------------------------------------------------------------------------------------ the stack wrench
# A C-frame beside the plate's long edge. Its lower end carries a fixed 17 mm open-end head that slides radially onto
# the Ti (lower) sonotrode's flats behind the plate and counter-holds them. Its upper end carries, on the stack's axis
# past the upper sonotrode's free end, a drive spindle that slides 14 mm down the axis so its slotted 17 mm socket
# takes the upper sonotrode's end flats; a gearmotor turns it through a slip clutch set to 50 N m. The reaction closes
# through the frame, so the arm only carries and places the tool (ours, to make; the drive is to choose).
# Frame: the stack frame when engaged (z along the axis, the heads' opening towards +y, the C-frame's spine on -y).
WR_SPINE_Y = (-74.0, -62.0)
WR_HANDLE = (-104.0, -74.0)    # the bar the 2F-85 holds, behind the spine
WR_TOP_Z = UP_FLAT_Z[1] + 22.0          # the upper arm's underside: 22 mm over the upper sonotrode's end
SOCKET_STROKE = 15.0           # the spindle slides this far down the axis to take the flats
WR_MASS_KG = 2.8               # ours: estimate (steel head and socket, aluminium frame, gearmotor)
LOW_HEAD_Z = (LOW_FLAT_Z[0] + 0.5, LOW_FLAT_Z[1] - 0.5)


def wrench_meshes() -> dict:
    """{name: (mesh, colour)} in the wrench's frame; the socket is separate (socket_meshes), it slides and turns."""
    out = {}
    jaw_x = FLATS / 2 + 0.3                       # each jaw's inner face 0.3 mm off its flat (ours)
    z0, z1 = LOW_HEAD_Z
    jaws = [box(s * jaw_x, s * (jaw_x + 8.0), -11.0, 24.0, z0, z1) for s in (-1, 1)]
    back = box(-jaw_x - 8, jaw_x + 8, -24.0, -11.0, z0, z1)
    out["low head"] = (merge(back, *jaws), STEEL)
    ys0, ys1 = WR_SPINE_Y
    zt0, zt1 = WR_TOP_Z, WR_TOP_Z + 16.0
    arm_lo = box(-12, 12, ys1, -24.0, z0, z1)
    spine = box(-14, 14, ys0, ys1, z0, zt1)
    arm_up = box(-16, 16, ys1, 18.0, zt0, zt1)
    out["frame"] = (merge(arm_lo, spine, arm_up), TOOL_BLUE)
    # the drive on the upper arm, on the axis: gearmotor and the slip clutch
    out["drive"] = (cyl(18, zt1, zt1 + 62, res=36), DARK)
    out["clutch"] = (cyl(20, zt1 + 62, zt1 + 74, res=36), TOOL_RED)
    out["handle"] = (box(-8, 8, WR_HANDLE[0], WR_HANDLE[1], z0 + 12, z0 + 52), BLACK)
    return out


def socket_meshes() -> dict:
    """The drive's slotted socket (the 17 mm slot across its open end), in the wrench frame, retracted: its open end
    SOCKET_STROKE + 1 over the upper sonotrode's flats (they start at UP_FLAT_Z[0])."""
    zb = UP_FLAT_Z[0] + 0.5 + SOCKET_STROKE         # the jaws' lower end when retracted
    tube = pv.Cylinder(center=(0, 0, zb + 7.0), direction=(0, 0, 1), radius=15.0, height=16.0, resolution=36,
                       capping=False).triangulate()
    inner = pv.Cylinder(center=(0, 0, zb + 7.0), direction=(0, 0, 1), radius=11.0, height=16.0, resolution=36,
                        capping=False).triangulate()
    ring = pv.Disc(center=(0, 0, zb - 1.0), inner=11.0, outer=15.0, normal=(0, 0, 1), c_res=36).triangulate()
    jaws = [box(s * (FLATS / 2 + 0.3), s * 11.2, -7.0, 7.0, zb, zb + 14.0) for s in (-1, 1)]
    stem = cyl(10, zb + 15.0, WR_TOP_Z + 0.5)
    lid = cyl(15, zb + 14.0, zb + 15.0)
    return {"socket": (merge(tube, inner, ring, lid, *jaws), (0.80, 0.81, 0.83)), "spindle": (stem, STEEL)}


WR_GRASP = np.array([0.0, (WR_HANDLE[0] + WR_HANDLE[1]) / 2 - 4.0, LOW_HEAD_Z[0] + 32.0])   # tips 1 mm off the spine

# ------------------------------------------------------------------------------------------------ fixtures on MiR 2
# MiR-local coordinates on a shelf over the cabinet top (z = TOP); the arm stands at (0, 130). Everything here is ours.
# The shelf lifts the fixtures 150 mm: on the bare cabinet top the arm had to fold down to its own mounting plane to
# reach them, and every IK branch put the upper arm into the cabinet.
CAB_TOP = AB.P.MIR["H"] + AB.P.CAB_H
RISER = 150.0
TOP = CAB_TOP + RISER
SHELF = dict(x=(-395.0, 395.0), y=(-288.0, -22.0))


def shelf_meshes() -> pv.PolyData:
    """The shelf: a 10 mm top on four legs and a back rail (ours)."""
    (x0, x1), (y0, y1) = SHELF["x"], SHELF["y"]
    top = box(x0, x1, y0, y1, TOP - 10.0, TOP)
    legs = [box(x - 15, x + 15, y - 15, y + 15, CAB_TOP, TOP - 10.0) for x in (x0 + 18, x1 - 18) for y in (y0 + 18, y1 - 18)]
    rail = box(x0 + 3, x1 - 3, y1 - 30, y1 - 3, CAB_TOP, CAB_TOP + 40)
    return merge(top, rail, *legs)
RACK_AT = (-215.0, -175.0)          # the plate rack's centre
RACK_SLOTS = 5
RACK_PITCH = 52.0                   # slot to slot (along x): room for the 2F-85's fingers either side of a plate
RACK_H = 40.0                       # the plates stand on their hole end in 40 mm deep slots
TRAY_AT = (95.0, -210.0)            # the upper sonotrode's tray (two sockets: used, spare)
WR_AT = (250.0, -150.0)             # the stack wrench's holder
GAUGE_AT = (200.0, -255.0)          # the gauge plate's holder
DROP_AT = (345.0, -125.0)          # the IPA dropper's holder
WIPE_AT = (345.0, -232.0)           # the wipe pad's holder

SLOT_NAMES = ("Al-10Si  CF  #02", "Al-10Si  CF  #03", "NAB  W-CF  new", "NAB  W-CF  used", "spare")


def slot_x(i):
    return RACK_AT[0] + (i - (RACK_SLOTS - 1) / 2) * RACK_PITCH


def plate_in_slot(i) -> np.ndarray:
    """MiR-local 4x4 of a plate (stack frame of the plate) standing in slot i: its hole end down, its free end up,
    its faces square to x, its width along y."""
    Mx = np.eye(4)
    Mx[:3, 0] = (0, 0, 1)            # along the plate: up
    Mx[:3, 1] = (0, -1, 0)           # across: along -y (the grasp comes from the arm's side, +y)
    Mx[:3, 2] = (1, 0, 0)            # the face normal: along x
    base = TOP + 6.0                 # the slot's floor
    Mx[:3, 3] = (slot_x(i) - PLATE_T / 2, RACK_AT[1], base + HOLE_E)
    return Mx


def rack_meshes() -> dict:
    out = {}
    x0, x1 = slot_x(0) - 30, slot_x(RACK_SLOTS - 1) + 30
    y0, y1 = RACK_AT[1] - 30, RACK_AT[1] + 30
    base = box(x0, x1, y0, y1, TOP, TOP + 6)
    walls = []
    for i in range(RACK_SLOTS + 1):                       # combs between the slots
        x = slot_x(i) - RACK_PITCH / 2 if i < RACK_SLOTS else slot_x(RACK_SLOTS - 1) + RACK_PITCH / 2
        walls.append(box(x - 3, x + 3, y0, y1, TOP + 6, TOP + RACK_H))
    for i in range(RACK_SLOTS):                           # each slot: two guides that hold the plate's edges
        x = slot_x(i)
        for s in (-1, 1):
            walls.append(box(x - 6, x + 6, RACK_AT[1] + s * (PLATE_W / 2 + 1.0), RACK_AT[1] + s * (PLATE_W / 2 + 7.0),
                             TOP + 6, TOP + RACK_H))
    out["rack"] = (merge(base, *walls), RACK)
    labels = [box(slot_x(i) - 20, slot_x(i) + 20, y0 - 0.6, y0, TOP + 8, TOP + 30) for i in range(RACK_SLOTS)]
    out["rack labels"] = (merge(*labels), LABEL)
    return out


def tray_meshes() -> dict:
    """Two sockets for upper sonotrodes standing on their plate end (the one coming off, and a spare)."""
    x, y = TRAY_AT
    out = []
    a, b = UPPER_R + 1.0, UPPER_R + 6.0          # a square socket, 1 mm round the sonotrode
    for s in (-1, 1):
        cx = x + s * 32
        h = TOP + 7.0                            # a 3 mm deep socket over its 4 mm floor: the fingertips stay clear
        out += [box(cx - b, cx + b, y - b, y - a, TOP, h), box(cx - b, cx + b, y + a, y + b, TOP, h),
                box(cx - b, cx - a, y - a, y + a, TOP, h), box(cx + a, cx + b, y - a, y + a, TOP, h),
                box(cx - b, cx + b, y - b, y + b, TOP, TOP + 4)]
    return {"tray": (merge(*out), (0.30, 0.32, 0.36))}


def upper_in_tray(s) -> np.ndarray:
    """MiR-local 4x4 of an upper sonotrode's stack frame standing in tray socket s (-1 or 1), plate end down."""
    x, y = TRAY_AT
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2] = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    Mx[:3, 3] = (x + s * 32, y, TOP + 4 - M.PLATE_T + 0.0)
    return Mx


def wrench_holder() -> pv.PolyData:
    """A base plate with a low fence round the wrench's heads, which stand on it axis-up (ours)."""
    x, y = WR_AT
    f0, f1 = TOP + 6.0, TOP + 18.0
    return merge(box(x - 45, x + 45, y - 45, y + 100, TOP, TOP + 6),
                 box(x - 37, x - 32, y - 36, y + 20, f0, f1), box(x + 32, x + 37, y - 36, y + 20, f0, f1),
                 box(x - 37, x + 37, y - 41, y - 36, f0, f1))


WR_LOW = LOW_HEAD_Z[0]                   # the wrench's lowest point (the head and the C-frame's spine), wrench frame z


def wrench_in_holder() -> np.ndarray:
    """MiR-local 4x4 of the wrench's frame in its holder: the axis (z) up, the heads' opening (+y) towards -y (away
    from the arm), the handle towards the arm."""
    x, y = WR_AT
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2] = (-1, 0, 0), (0, -1, 0), (0, 0, 1)
    Mx[:3, 3] = (x, y, TOP + 6.0 - WR_LOW + 0.3)
    return Mx


GAUGE_L, GAUGE_W, GAUGE_T = 60.0, 20.8, 1.0    # a retired Mo plate cut short (#164: "shortened a retired plate")


def gauge_meshes() -> dict:
    return {"gauge": (box(0, GAUGE_L, -GAUGE_W / 2, GAUGE_W / 2, 0, GAUGE_T), (0.66, 0.66, 0.70))}


def gauge_holder() -> pv.PolyData:
    """A slot that holds the gauge plate on its end (ours)."""
    x, y = GAUGE_AT
    return merge(box(x - 26, x + 26, y - 16, y + 16, TOP, TOP + 4),
                 box(x - 14, x + 14, y + 1.5, y + 5.0, TOP + 4, TOP + 16),
                 box(x - 14, x + 14, y - 5.0, y - 1.5, TOP + 4, TOP + 16))


def gauge_in_holder() -> np.ndarray:
    """The gauge plate standing on its end in the holder (MiR-local): its length up, its width along x."""
    x, y = GAUGE_AT
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2] = (0, 0, 1), (1, 0, 0), (0, 1, 0)
    Mx[:3, 3] = (x, y - GAUGE_T / 2, TOP + 4.0)
    return Mx


def dropper_meshes() -> dict:
    """A 30 mL IPA dropper bottle (ours: a lab wash bottle or dropper; the SOP uses a few drops of IPA): body, cap,
    tip. Frame: base centre at the origin, z up."""
    body = cyl(16, 0, 62, res=32)
    shoulder = cyl(9, 62, 70)
    tip = pv.Cone(center=(0, 0, 80), direction=(0, 0, 1), height=20, radius=5, resolution=24).triangulate()
    return {"bottle": (body, (0.92, 0.94, 0.97)), "cap": (merge(shoulder, tip), (0.95, 0.95, 0.95)),
            "ipa label": (pv.Cylinder(center=(0, 0, 30), direction=(0, 0, 1), radius=16.3, height=20, resolution=32,
                                      capping=False).triangulate(), (0.20, 0.45, 0.80))}


def dropper_holder() -> pv.PolyData:
    x, y = DROP_AT
    return merge(box(x - 26, x + 26, y - 26, y + 26, TOP, TOP + 4),
                 *[box(x + s * 17, x + s * 23, y - 20, y + 20, TOP + 4, TOP + 22) for s in (-1, 1)])


def wipe_meshes() -> dict:
    """A lint-free wipe folded over a foam pad on a short stem (ours), frame: the pad's face centre at the origin,
    the stem along -z."""
    pad = box(-20, 20, -15, 15, 0, 10)
    stem = box(-6, 6, -6, 6, 10, 70)
    return {"wipe pad": (pad, (0.97, 0.97, 0.99)), "wipe stem": (stem, (0.25, 0.27, 0.30))}


def wipe_holder() -> pv.PolyData:
    x, y = WIPE_AT
    return merge(box(x - 28, x + 28, y - 24, y + 24, TOP, TOP + 4),
                 *[box(x + s * 21, x + s * 27, y - 18, y + 18, TOP + 4, TOP + 30) for s in (-1, 1)])


# ------------------------------------------------------------------------------------------------ the BOM
BOM = [
    dict(item="Stack wrench: two coaxial 17 mm heads (fixed counter-hold + driven slotted ring), C-frame, handle",
         maker="ours", part_no=None, qty=1, unit_usd=None, source="ours (notes/atom_plate.md, 'Tool')",
         **{"for": "breaking loose and torquing the upper sonotrode to 50 N m with the reaction inside the tool"},
         status="ours: to make"),
    dict(item="Gearmotor + slip clutch (or a small DC nutrunner spindle) set to 50 N m, 24 V", maker="to choose",
         part_no=None, qty=1, unit_usd=None, source="ours: 50 N m from DAL 253 step 13 / 178 step 5",
         **{"for": "the stack wrench's drive"}, status="to buy"),
    dict(item="Stack wrench holder on MiR 2's cabinet top", maker="ours", part_no=None, qty=1, unit_usd=None,
         source="ours", **{"for": "parking the wrench where the arm can pick it"}, status="ours: to make"),
    dict(item="Per-alloy plate rack, 5 labelled slots", maker="ours", part_no=None, qty=1, unit_usd=None,
         source="ours; DAL 178 'Cleaning and maintenance': label plates, one alloy per plate (OCT2a 02:24)",
         **{"for": "storing plates by alloy, picked and returned by the arm"}, status="ours: to make"),
    dict(item="Plate ID labels (engraved or tag)", maker="to choose", part_no=None, qty=10, unit_usd=None,
         source="DAL 178: 'Label them: on Oct 2 nobody could tell the plates apart'",
         **{"for": "the plate log"}, status="to buy"),
    dict(item="Upper sonotrode tray (2 sockets)", maker="ours", part_no=None, qty=1, unit_usd=None, source="ours",
         **{"for": "the upper sonotrode while the plate is changed"}, status="ours: to make"),
    dict(item="Mo gauge plate (a retired plate cut short)", maker="lab", part_no=None, qty=1, unit_usd=0.0,
         source="DAL #164 (Gage, 2026-10-21: 'Shortened a retired plate to use as a guide')",
         **{"for": "setting the plate's height (253 step 15)"}, status="lab has"),
    dict(item="Gauge plate holder", maker="ours", part_no=None, qty=1, unit_usd=None, source="ours",
         **{"for": "the arm's pick of the gauge plate"}, status="ours: to make"),
    dict(item="IPA dropper bottle, 30 mL", maker="to choose", part_no=None, qty=1, unit_usd=None,
         source="DAL 253 step 16 (a few drops of IPA); 178 step 10 (water)", **{"for": "the wet test"},
         status="to buy"),
    dict(item="Isopropyl alcohol", maker="lab", part_no=None, qty=1, unit_usd=None, source="DAL 253 steps 3, 16, 18",
         **{"for": "the wet test and wiping the seals"}, status="lab has"),
    dict(item="Dropper holder", maker="ours", part_no=None, qty=1, unit_usd=None, source="ours",
         **{"for": "the arm's pick of the dropper"}, status="ours: to make"),
    dict(item="Wipe pad on a stem (foam pad, lint-free wipe folded over)", maker="ours", part_no=None, qty=1,
         unit_usd=None, source="ours; DAL 253 step 18 'Wipe the seals with IPA'",
         **{"for": "wiping the door seal and its face"}, status="ours: to make"),
    dict(item="Lint-free wipes", maker="to choose", part_no=None, qty=1, unit_usd=None, source="DAL 178_equipment",
         **{"for": "the wipe pad"}, status="lab has"),
    dict(item="Laser module in a printed holder, in the sealing rod's place", maker="to choose", part_no=None, qty=1,
         unit_usd=None, source="DAL #164 (Bartosz's laser down the nozzle, T5 63:28; the runs plan's G0 step)",
         **{"for": "the landing check (253 step 17)"}, status="to buy"),
    dict(item="Carbon-fibre plates, W plasma-coated (one new per Cu run)", maker="AMAZEMET", part_no=None, qty=4,
         unit_usd=None, source="DAL 253 'Copper Alloys' step 2; 178 plate table (T9 38:35); price range $10-80 (SP 09:33)",
         **{"for": "NAB / 630 bronze runs"}, status="to buy"),
    dict(item="Carbon-fibre plates, bare", maker="AMAZEMET", part_no=None, qty=2, unit_usd=None,
         source="DAL 178 plate table (T5 11:53: up to ~10 processes)", **{"for": "Al runs"}, status="lab has"),
    dict(item="Upper sonotrode, W-Ni-Fe, 19.9 x 56.6 mm", maker="AMAZEMET", part_no=None, qty=1, unit_usd=None,
         source="#261 measurements", **{"for": "the stack (already on the machine)"}, status="lab has"),
    dict(item="Torque wrench (the lab's, for the bench and to check the stack wrench's clutch)", maker="lab",
         part_no=None, qty=1, unit_usd=None, source="DAL 178 step 5 (T5 16:59, T7 38:33)",
         **{"for": "calibrating the clutch at 50 N m"}, status="lab has"),
]
