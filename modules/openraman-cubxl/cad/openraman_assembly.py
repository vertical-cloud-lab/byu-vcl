"""The OpenRAMAN base spectrometer, assembled in one frame from the official files.

The official STEP exports (git.thepulsar.be/openraman/cad.git @ 778dfda, CC BY-SA 4.0,
Luc Boussemaere) are each in their own part frame; the SolidWorks assembly that places
them is not readable here. Every placement below is recovered from geometry in those
files, not eyeballed:

* the baseplate's hole pattern locates every mount (laser holder: two M4 at 22.5 mm,
  camera bracket: two M4 at 34.0 mm, FMP1s, KM100s, cage and sample-port brackets);
* P00006 OPTICAL PATH and P00007 LASER PATH are the Zemax optical layout as solids
  (lenses, mirrors, slit, grating, sensor). Aligning their filter, laser and lens
  elements with those holes puts the optical plane 22.0 mm above the baseplate and the
  Raman axis on y = 95.08 mm;
* the cover's three Ø4.8 holes match the baseplate's three cover taps by a rigid fit.

Vendor parts (Thorlabs mounts, laser, camera, lens) are simplified recreations from
the datasheet dimensions, not the vendors' CAD, which the OpenRAMAN repo keeps under
externals/ with their own licences.

Frame S, used everywhere: x along the baseplate's 300 mm length (sample port at +x),
y across its 150 mm width, z up, origin at the baseplate's top-surface corner.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq
import numpy as np
from OCP.gp import gp_Trsf

# ---------------------------------------------------------------------------
# Frames recovered from the official geometry (see module docstring)
# ---------------------------------------------------------------------------
PLATE_X_TOP, PLATE_Y_MIN, PLATE_Z_MIN = 57.16144, -57.90935, 38.22825   # P00001 part frame
BEAM_H = 22.0            # optical plane above the baseplate top (laser holder: 21.97, camera: 21.58)
AXIS_YP = 37.18          # Raman axis in the plate frame: sample-port and cage bracket holes
PATH_ZP = 329.5          # P00006 z-offset: laser exit face and FMP1 holes
LENS_BFL = 15.9          # AC127-019-A back focal length (Thorlabs spec), sample side

R_PS = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], float)   # plate frame -> S
T_PS = np.array([-PLATE_Z_MIN, -PLATE_Y_MIN, PLATE_X_TOP])


def plate_to_s(xp, yp, zp):
    return R_PS @ np.array([xp, yp, zp], float) + T_PS


AXIS_Y = plate_to_s(0, AXIS_YP, 0)[1]                 # 95.08
SAMPLE_LENS_X = 3.4 + PATH_ZP - PLATE_Z_MIN           # AC127-019-A centre, x = 294.7
SAMPLE_FOCUS = np.array([6.41 + LENS_BFL + PATH_ZP - PLATE_Z_MIN, AXIS_Y, BEAM_H])  # x = 313.6
LASER_EXIT = np.array([-79.5 + PATH_ZP - PLATE_Z_MIN, AXIS_Y - 50.0, BEAM_H])
FOLD_X = 261.3           # front-surface centres of the PF10 mirror and DMLP550 (y 45.06 / 95.07)


def trsf(R, t):
    """gp_Trsf from a 3x3 rotation and a translation."""
    T = gp_Trsf()
    T.SetValues(*R[0], t[0], *R[1], t[1], *R[2], t[2])
    return T


def place(shape, R, t):
    return shape.moved(cq.Location(trsf(np.asarray(R, float), np.asarray(t, float))))


def frame_from_axes(x_dir, z_dir, origin):
    """Rotation whose local +x maps to x_dir and +z to z_dir (both in S)."""
    z = np.asarray(z_dir, float); z /= np.linalg.norm(z)
    x = np.asarray(x_dir, float); x -= z * (x @ z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return np.column_stack([x, y, z]), np.asarray(origin, float)


@dataclass
class Part:
    name: str
    shape: cq.Shape
    color: str
    step: int                       # assembly step it appears in (see STEPS)
    approach: tuple = (0, 0, 1)     # direction it flies in from
    opacity: float = 1.0
    group: str = "spectrometer"
    tags: dict = field(default_factory=dict)


STEPS = [  # official drawing P00000, sheets 2..7 then 1
    "Sheet 2: laser holder onto the baseplate, CPS532 laser, clamp setscrew",
    "Sheet 3: camera bracket on dowels, MVL50M23 lens, Blackfly S camera",
    "Sheet 4: FMP1 mounts with the FELH0550 longpass and WG41050-A plate",
    "Sheet 5: KM100 mounts: PF10 mirror, DMLP550 dichroic, grating glued to its holder",
    "Sheet 6: cage: AC254-050-A, S50K slit in CRM1T/M, AC127-019-A, four ER3 rods",
    "Sheet 7: cage onto the baseplate; sample-port CP33B bracket",
    "Sheet 1: cover, three M4x10",
]

C_ALU = "#34343a"        # black-anodised aluminium
C_PLASTIC = "#26262b"
C_THOR = "#45454b"       # Thorlabs black anodise
C_STEEL = "#b9bcc2"
C_GLASS = "#9ad0ec"
C_MIRROR = "#d9dde3"
C_GRATING = "#c9a227"
C_LASER_BODY = "#c7c9cc"
C_CAMERA = "#8a8f98"


# ---------------------------------------------------------------------------
# Simplified vendor parts (local frames; dimensions from the vendors' datasheets)
# ---------------------------------------------------------------------------
def cyl(d, h, z0=0.0):
    return cq.Solid.makeCylinder(d / 2, h, cq.Vector(0, 0, z0))


def box(x, y, z, cx=0.0, cy=0.0, z0=0.0):
    return cq.Solid.makeBox(x, y, z, cq.Vector(cx - x / 2, cy - y / 2, z0))


def ring(od, id_, h, z0=0.0):
    return cyl(od, h, z0).cut(cyl(id_, h + 2, z0 - 1))


def km100():
    """Thorlabs KM100, optic axis = local +z, optic seat at z = 0, body behind (z < 0)."""
    front = box(38.1, 38.1, 6.4, z0=-6.4).cut(cyl(25.4, 20, -10))
    back = box(38.1, 38.1, 6.4, z0=-15.2).cut(cyl(18, 20, -20))
    knob = cyl(9.5, 9.0, -24.2)
    k1 = knob.moved(cq.Location(cq.Vector(13, 13, 0)))
    k2 = knob.moved(cq.Location(cq.Vector(-13, -13, 0)))
    return front.fuse(back).fuse(k1).fuse(k2).fuse(box(4, 4, 2.4, 13, -13, -8.8))


def fmp1(h_axis):
    """Thorlabs FMP1/M fixed mount: ring + foot; optic axis local +z, foot towards -y."""
    r = ring(33.0, 25.4, 9.5, -4.75)
    foot = box(20.0, h_axis - 12.0, 9.5, cy=-(12.0 + (h_axis - 12.0) / 2), z0=-4.75)
    return r.fuse(foot)


def cage_plate(thick, bore):
    p = box(41.0, 41.0, thick, z0=-thick / 2).cut(cyl(bore, thick + 2, -thick / 2 - 1))
    for sx in (-15, 15):
        for sy in (-15, 15):
            p = p.cut(cyl(6.1, thick + 2, -thick / 2 - 1).moved(cq.Location(cq.Vector(sx, sy, 0))))
    return p


def crm1t():
    body = cage_plate(12.7, 30.5)
    dial = ring(30.4, 22.0, 9.0, -4.5)
    return body.fuse(dial)


def cage_bracket_s(x):
    """CP33B in frame S at axis station x: clamps the two lower 30 mm cage rods
    (y = axis +-15, z = BEAM_H - 15) to the baseplate."""
    zr = BEAM_H - 15.0
    b = box(12.7, 50.0, zr + 4.0, cx=x, cy=AXIS_Y, z0=0.0).cut(box(14.0, 18.0, zr + 6.0, cx=x, cy=AXIS_Y, z0=2.5))
    for sy in (-15.0, 15.0):
        b = b.cut(cq.Solid.makeCylinder(3.05, 20.0, cq.Vector(x - 10.0, AXIS_Y + sy, zr), cq.Vector(1, 0, 0)))
    return b


def cps532():
    """Thorlabs CPS532, emission face at z = 0, body towards -z."""
    return cyl(11.0, 62.0, -62.0).fuse(cyl(6.0, 9.0, -71.0)).fuse(ring(11.6, 9.0, 1.0, -1.0))


def mvl50m23():
    """Navitar NMV-50M23 / Thorlabs MVL50M23, C-mount flange at z = 0, front towards -z."""
    b = cyl(34.0, 40.0, -40.0)
    for z in (-34.0, -24.0, -14.0):
        b = b.cut(ring(36.0, 33.0, 1.2, z))
    return b.fuse(cyl(25.0, 4.5, 0.0))


def blackfly_s():
    """Teledyne FLIR Blackfly S GigE, 29 x 29 x 30 mm; C-mount flange at z = 0, body +z."""
    body = box(29.0, 29.0, 30.0, z0=0.0)
    rj45 = box(16.0, 14.0, 9.0, cy=-3.0, z0=30.0)
    gpio = cyl(9.0, 6.0, 30.0).moved(cq.Location(cq.Vector(0, 9.0, 0)))
    return body.fuse(rj45).fuse(gpio)


def shcs_m4(length):
    """DIN 912 M4: head 7 x 4, shank along -z from the head's bearing face at z = 0."""
    return cyl(7.0, 4.0, 0.0).cut(cyl(3.0, 2.5, 1.6)).fuse(cyl(4.0, length, -length))


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build(openraman_cad: Path):
    exp = Path(openraman_cad) / "exports" / "spectrometer"
    imp = lambda n: cq.importers.importStep(str(exp / f"{n}.step"))
    parts: list[Part] = []
    up = (0, 0, 1)

    # -- baseplate (P00001)
    plate = imp("P00001 - BASEPLATE").val()
    parts.append(Part("P00001 baseplate", place(plate, R_PS, T_PS), C_ALU, 0, (0, 0, -1)))

    # -- optical elements from the official Zemax solids
    R6 = R_PS                                            # P00006 shares the plate's axes
    t6 = R_PS @ np.array([PLATE_X_TOP - BEAM_H, AXIS_YP, PATH_ZP]) + T_PS
    optics6 = imp("P00006 - OPTICAL PATH").solids().vals()
    # index -> (name, colour, step); order as stored in the STEP (checked by centroid)
    roles6 = {0: ("dock lens AC127-019-A (front)", C_GLASS, -1), 1: ("dock lens AC127-019-A (rear)", C_GLASS, -1),
              2: ("DMLP550 dichroic", "#f2b5d4", 3), 3: ("FELH0550 longpass", "#e8743b", 2),
              4: ("WG41050-A plate", C_GLASS, 2), 5: ("AC127-019-A (front)", C_GLASS, 4),
              6: ("AC127-019-A (rear)", C_GLASS, 4), 7: ("S50K slit", "#111111", 4),
              8: ("AC254-050-A (front)", C_GLASS, 4), 9: ("AC254-050-A (rear)", C_GLASS, 4),
              10: ("GR25-1205 grating", C_GRATING, 3), 11: ("lens element", C_GLASS, 1),
              12: ("lens element", C_GLASS, 1), 13: ("lens element", C_GLASS, 1),
              14: ("lens element", C_GLASS, 1), 15: ("sensor window", C_GLASS, 1),
              16: ("IMX265 sensor", "#3b2f63", 1)}
    for i, s in enumerate(optics6):
        name, col, step = roles6[i]
        if step < 0:
            continue                                     # the dock lens belongs to the CubXL part
        parts.append(Part(name, place(s, R6, t6), col, step, (0, 0, 1), 0.55 if col == C_GLASS else 1.0,
                          tags={"optic": True}))
    R7 = R6 @ np.diag([-1.0, -1.0, 1.0])                 # P00007 is P00006 turned 180 deg about its z
    t7 = t6 + R6 @ np.array([0.0, -50.0, -80.0])
    mirror = imp("P00007 - LASER PATH").solids().vals()[0]
    parts.append(Part("PF10-03-G01 mirror", place(mirror, R7, t7), C_MIRROR, 3, (0, 0, 1), tags={"optic": True}))
    dock_lens = [place(optics6[i], R6, t6) for i in (0, 1)]

    # -- sheet 2: laser holder, CPS532, SS4MN4
    R3 = np.array([[0, -1, 0], [0, 0, -1], [1, 0, 0]], float)
    t3 = np.array([35.19, -12.83, 217.9])                # P00003 -> plate frame (Xp, Yp, Zp), from its two M4 holes
    Rh, th = R_PS @ R3, R_PS @ t3 + T_PS
    parts.append(Part("P00003 laser holder", place(imp("P00003 - LASER HOLDER").val(), Rh, th), C_ALU, 0))
    Rl, tl = frame_from_axes((0, 1, 0), (1, 0, 0), LASER_EXIT)
    parts.append(Part("CPS532 laser", place(cps532(), Rl, tl), C_LASER_BODY, 0, (-1, 0, 0)))
    parts.append(Part("SS4MN4 setscrew", place(cyl(4.0, 4.0), np.eye(3), th + Rh @ np.array([16.0, 9.0, 0.0]) + [0, 0, 2.0]),
                      C_STEEL, 0))
    for zp in (222.70, 245.20):
        p = plate_to_s(62.76, -12.83, zp)
        parts.append(Part("DIN912 M4x12", place(shcs_m4(12), np.diag([1, -1, -1.0]), p), C_STEEL, 0, (0, 0, -1)))

    # -- sheet 3: camera bracket, lens, camera
    u = np.array([0.0, 0.6756, 0.7373])                 # bracket local x, plate frame (hole 1 -> hole 2)
    R5p = np.column_stack([u, [-1.0, 0, 0], np.cross(u, [-1.0, 0, 0])])
    t5p = np.array([35.58, -16.29, 134.94])
    R5, t5 = R_PS @ R5p, R_PS @ t5p + T_PS
    parts.append(Part("P00005 camera bracket", place(imp("P00005 - CAMERA BRACKET").val(), R5, t5), C_ALU, 1))
    cam_axis = R5[:, 2]                                  # towards the sensor
    sensor = R6 @ np.array([0, -84.29, -165.76]) + t6
    flange = sensor - cam_axis * 17.526                  # C-mount flange focal distance
    Rc, _ = frame_from_axes((0, 0, 1), cam_axis, flange)
    parts.append(Part("MVL50M23 lens", place(mvl50m23(), Rc, flange), "#2a2a2a", 1, tuple(-cam_axis)))
    parts.append(Part("Blackfly S BFS-PGE-31S4M-C", place(blackfly_s(), Rc, flange), C_CAMERA, 1, tuple(cam_axis)))
    for a, b in ((125.78, -31.46), (150.85, -8.49)):
        p = plate_to_s(62.76, b, a)
        parts.append(Part("DIN912 M4x12", place(shcs_m4(12), np.diag([1, -1, -1.0]), p), C_STEEL, 1, (0, 0, -1)))
    parts.append(Part("DIN912 M4x10", place(shcs_m4(10), R5 @ np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float),
                                            t5 + R5 @ np.array([24.0, 6.5, 5.0])), C_STEEL, 1))

    # -- sheet 4: FMP1/M with FELH0550 and WG41050-A (normals from P00006)
    for zp, yp, name, idx in ((249.65, 37.88, "FMP1/M (FELH0550)", 3), (229.61, 36.81, "FMP1/M (WG41050-A)", 4)):
        c = np.array(place(optics6[idx], R6, t6).Center().toTuple())
        n = _normal(place(optics6[idx], R6, t6))
        n = n if n[0] > 0 else -n
        Rm, _ = frame_from_axes(np.cross((0, 0, 1), n), n, c)
        parts.append(Part(name, place(fmp1(BEAM_H + 0.5), Rm, c), C_THOR, 2))
        p = plate_to_s(62.76, yp, zp)
        parts.append(Part("DIN912 M4x12", place(shcs_m4(12), np.diag([1, -1, -1.0]), p), C_STEEL, 2, (0, 0, -1)))

    # -- sheet 5: KM100 x3 (behind mirror, dichroic, grating), grating holder
    holes = {"grating": (67.23, 57.30), "dichroic": (290.82, 45.30), "mirror": (309.20, -23.08)}
    for key, elem in (("mirror", [p for p in parts if p.name.startswith("PF10")][0].shape),
                      ("dichroic", place(optics6[2], R6, t6)), ("grating", place(optics6[10], R6, t6))):
        c = np.array(elem.Center().toTuple())
        hole = plate_to_s(PLATE_X_TOP, holes[key][1], holes[key][0])
        n = _normal(elem)
        n = n if (c[:2] - hole[:2]) @ n[:2] > 0 else -n      # optic face points away from the mount
        half = {"mirror": 3.0, "dichroic": 1.6, "grating": 3.0}[key]
        seat = c - n * half                                  # optic's back face
        if key == "grating":                                 # glued to P00004, whose Ø25 boss sits in the KM100
            Rg, _ = frame_from_axes(np.cross((0, 0, 1), -n), -n, seat)
            gh = imp("P00004 - GRATING HOLDER").val()
            parts.append(Part("P00004 grating holder", place(gh, Rg, seat - 2.0 * n), C_ALU, 3))
            seat = seat - n * 5.0
        Rk, _ = frame_from_axes(np.cross((0, 0, 1), n), n, seat)
        parts.append(Part(f"KM100 ({key})", place(km100(), Rk, seat), C_THOR, 3))
        parts.append(Part("DIN912 M4x10", place(shcs_m4(10), np.eye(3), hole + [0, 0, BEAM_H + 19.05]), C_STEEL, 3))

    # -- sheets 6-7: cage on the Raman axis
    ax = lambda x: np.array([x, AXIS_Y, BEAM_H])
    Rx, _ = frame_from_axes((0, 1, 0), (1, 0, 0), (0, 0, 0))
    x_cp14, x_slit, x_cp35 = -120.1 + PATH_ZP - PLATE_Z_MIN, -138.78 + PATH_ZP - PLATE_Z_MIN, -186.35 + PATH_ZP - PLATE_Z_MIN
    parts += [Part("CP14 cage plate", place(cage_plate(8.9, 12.7), Rx, ax(x_cp14)), C_THOR, 4),
              Part("CRM1T/M rotation mount", place(crm1t(), Rx, ax(x_slit)), C_THOR, 4),
              Part("SM1RR retaining ring", place(ring(30.0, 26.0, 1.5), Rx, ax(x_slit - 2.5)), C_THOR, 4),
              Part("CP35/M cage plate", place(cage_plate(12.7, 25.4), Rx, ax(x_cp35)), C_THOR, 4)]
    for sy in (-15, 15):
        for sz in (-15, 15):
            parts.append(Part("ER3 rod", place(cyl(6.0, 76.2), Rx, ax(x_cp35 - 6.35) + [0, sy, sz]), C_STEEL, 4))
    bracket = lambda x: cage_bracket_s(x)
    parts.append(Part("CP33B cage bracket", bracket(plate_to_s(0, 0, 192.27)[0]), C_THOR, 5))
    parts.append(Part("CP33B sample-port bracket", bracket(plate_to_s(0, 0, 330.88)[0]), C_THOR, 5))
    p = plate_to_s(62.76, 37.17, 192.27)
    parts.append(Part("DIN912 M4x12", place(shcs_m4(12), np.diag([1, -1, -1.0]), p), C_STEEL, 5, (0, 0, -1)))
    for yp in (29.56, 44.80):
        parts.append(Part("DIN912 M4x6", place(shcs_m4(6), np.eye(3), plate_to_s(PLATE_X_TOP, yp, 330.88) + [0, 0, 7.0]), C_STEEL, 5))

    # -- sheet 1: cover, fitted to the three cover taps
    cover = imp("P00002 - COVER").val()
    Rcv, tcv = _fit_cover(cover)
    parts.append(Part("P00002 cover", place(cover, Rcv, tcv), C_PLASTIC, 6, (0, 0, 1), 0.92))
    for zp, yp in ((61.04, -19.42), (141.79, 80.30), (175.61, -8.35)):
        parts.append(Part("DIN912 M4x10", place(shcs_m4(10), np.eye(3), plate_to_s(PLATE_X_TOP, yp, zp) + [0, 0, 3.0]), C_STEEL, 6))

    beams = dict(laser=[LASER_EXIT, [FOLD_X, LASER_EXIT[1], BEAM_H], [FOLD_X, AXIS_Y, BEAM_H], SAMPLE_FOCUS],
                 raman=[SAMPLE_FOCUS, ax(FOLD_X), ax(x_cp35), np.array(place(optics6[10], R6, t6).Center().toTuple()), sensor])
    return parts, dock_lens, beams


def _normal(shape):
    v, _ = shape.tessellate(0.5, 0.5)
    P = np.array([(q.x, q.y, q.z) for q in v]); P -= P.mean(0)
    w, U = np.linalg.eigh(P.T @ P)
    return U[:, 0]


def _fit_cover(cover):
    """Rigid fit of the cover's three Ø4.8 holes onto the baseplate's three cover taps."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    src = []
    for f in cover.Faces():
        if f.geomType() == "CYLINDER":
            c = BRepAdaptor_Surface(f.wrapped).Cylinder()
            if abs(2 * c.Radius() - 4.8) < 0.05:
                src.append((2000.0, c.Location().Y(), c.Location().Z()))   # flange face is X = 2000
    src = np.array(sorted(set((round(a, 3), round(b, 3), round(c, 3)) for a, b, c in src)))
    dst_p = {(1998.5, 5.0, -21.5): (141.79, 80.30), (1998.5, -83.9, 11.6): (175.61, -8.35),
             (1998.5, -94.0, -103.1): (61.04, -19.42)}   # matched by pairwise distances 94.9 / 115.1 / 128.3
    A, B = [], []
    for s in src:
        key = min(dst_p, key=lambda k: (k[1] - s[1]) ** 2 + (k[2] - s[2]) ** 2)
        zp, yp = dst_p[key]
        A.append(s); B.append(plate_to_s(PLATE_X_TOP, yp, zp))
    A, B = np.array(A), np.array(B)
    # cover frame: +X is down (flange at X = 2000 rests on the plate). Solve R, t with R e_x = -e_z.
    a0, b0 = A.mean(0), B.mean(0)
    H = (A - a0)[:, 1:].T @ (B - b0)[:, :2]
    U, _, Vt = np.linalg.svd(H)
    # X_cover -> -z, so (Y, Z)_cover -> (x, y) must be a reflection for R to stay proper
    R2 = (U @ Vt).T
    if np.linalg.det(R2) > 0:
        R2 = (U @ np.diag([1.0, -1.0]) @ Vt).T
    resid = np.abs((A - a0)[:, 1:] @ R2.T - (B - b0)[:, :2]).max()
    if resid > 0.5:
        raise ValueError(f"cover holes do not fit the baseplate taps (max residual {resid:.2f} mm)")
    R = np.zeros((3, 3)); R[:2, 1:] = R2; R[2, 0] = -1.0
    if np.linalg.det(R) < 0:
        raise ValueError("improper cover rotation")
    t = b0 - R @ a0
    t[2] = 0.0 - R[2] @ np.array([2000.0, 0, 0])          # flange on the plate top
    return R, t
