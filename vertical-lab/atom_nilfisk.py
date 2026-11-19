"""The lab's explosion-proof vacuum (a Nilfisk CFM 118EXP), its conductive tools, the area's safety kit, and our own
fittings that let a UR10e + 2F-85 use it (PR #353, #303). Models only; the clip is atom_vacuum.py.

Every size below carries its source. "Brochure" is Nilfisk's 118 EXP / EXPW brochure as quoted by a web search on
2026-11-19 (its spec page and the maker's PDF were not fetchable: 403/429): 6.6 gal tank, 20 x 24 x 45 in (L x W x H),
57 lb. "Accessories doc" is byu-vcl PR 80's vacuum-accessories-options.md (the bin's 12.5 in / 320 mm ID, about 16 in
over the gasket, the 1.5 in / 38 mm inlet, the 360 mm antistatic main filter, every part number and price). "SOP" is
PR 80's vacuum-operating-sop.md. Anything else is estimated from photos and says so, with a tolerance.

Frames: each builder returns {name: (mesh, colour)} in its own local frame, origin on the floor (or at the part's
datum), z up, millimetres. The vacuum's +x is its inlet side; its handle is on -x.

Ours (not bought): the wand's clamp collar with the gripper fin and its locating pin, the station post with the
holster, the tool rack, the continuity fixture (a spring pad and three spring probes on a column, read through a relay
box by the milliohm meter) and the ground button. None of them drills or alters a Nilfisk part: the 118EXP manual says
any third-party alteration voids its certification (accessories doc, section 15.1).
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

IN = 25.4

# --------------------------------------------------------------------------------------------- colours
SS = (0.80, 0.81, 0.83)            # 304 stainless (brochure: container, filter chamber and trolley are 304 SS)
SS_DK = (0.60, 0.62, 0.65)
ALU = (0.84, 0.85, 0.87)           # the aluminium wand and tools (OEM manual's BOM 01760495: "Aluminium")
BLACK = (0.08, 0.08, 0.09)         # the conductive hose and cuff, the liner
RUBBER = (0.15, 0.15, 0.16)
GRN_YEL = (0.30, 0.65, 0.20)       # the ground cable (green/yellow)
RED = (0.80, 0.10, 0.08)
YELLOW = (0.98, 0.80, 0.10)
OURS = (0.20, 0.42, 0.75)          # our printed / machined fittings (blue, so they read as ours)
OURS_DK = (0.14, 0.24, 0.42)
BRASS = (0.80, 0.65, 0.32)
LCD = (0.55, 0.78, 0.55)

# --------------------------------------------------------------------------------------------- the 118EXP
TANK_GAL = 6.6                     # brochure (Fisher Scientific's listing says the same)
FOOT_L, FOOT_W, HEIGHT = 20 * IN, 24 * IN, 45 * IN     # brochure: 508 x 610 x 1143 mm overall (L x W x H)
MASS_KG = 57 * 0.4536              # brochure: 57 lb, 25.9 kg
BIN_ID = 320.0                     # accessories doc 9.5 and 10.4: about 12.5 in ID
BIN_OD_GASKET = 16 * IN            # accessories doc 10.7: "about 16 in" over the rim gasket (15-16 in)
BIN_DEPTH = TANK_GAL * 3.78541e6 / (math.pi * (BIN_ID / 2) ** 2)   # 311 mm: the tank's volume at that ID
FILTER_D = 360.0                   # accessories doc 2a: antistatic main filter 360 mm, 40000460
INLET_ID = 38.0                    # accessories doc header: 1.5 in (38 mm) hose inlet
INLET_Z = 410.0                    # inlet stub's axis: high on the container's side (estimated from photos, +-40)
CASTOR_R = 50.0                    # estimated from photos, +-15
TROLLEY = 440.0                    # wheelbase square (estimated: inside the brochure's 508 x 610 envelope, +-40)
Z_BIN = (110.0, 110.0 + 330.0)     # the bin on the trolley: 330 tall outside (311 inside + floor), estimated +-30
Z_HOUSING = (Z_BIN[1], 700.0)      # filter chamber over the bin (estimated from photos, +-50)
Z_MOTOR = (700.0, 905.0)           # motor head (estimated, +-50)
Z_HEPA = (905.0, 965.0)            # the downstream HEPA housing on the head (estimated, +-30)
ELEC = "120 V, 10 A, 1000 W; 130 CFM; 69 in water lift (accessories doc header)"


def _cyl(c, d, r, h, res=48):
    return pv.Cylinder(center=c, direction=d, radius=r, height=h, resolution=res).triangulate()


def _box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def lathe(profile, res=64) -> pv.PolyData:
    """A closed (r, z) profile revolved about z."""
    pts = np.array([(r, 0.0, z) for r, z in profile], float)
    face = pv.PolyData(pts, faces=np.r_[len(pts), np.arange(len(pts))])
    m = face.extrude_rotate(resolution=res, angle=360.0, capping=False, rotation_axis=(0, 0, 1))
    return m.triangulate().clean().compute_normals(split_vertices=True, feature_angle=50.0)


def tube_along(pts, r, sides=16) -> pv.PolyData:
    pts = np.asarray(pts, float)
    return pv.Spline(pts, max(len(pts) * 4, 40)).tube(radius=r, n_sides=sides, capping=True).triangulate()


def vacuum_meshes() -> dict:
    """The 118EXP on its trolley, in its own frame: the bin's axis at (0, 0), the inlet on +x, the handle on -x."""
    out = {}
    h = TROLLEY / 2
    frame = [_box(-h, h, -h, -h + 30, 90, 112), _box(-h, h, h - 30, h, 90, 112),
             _box(-h, -h + 30, -h, h, 90, 112), _box(h - 30, h, -h, h, 90, 112)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (h - 35), sy * (h - 35)
            frame.append(_cyl((cx, cy, 70), (0, 0, 1), 16, 40))                   # the castor's swivel
    out["vac trolley"] = (frame[0].merge(frame[1:]), SS)
    wheels = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            wheels.append(_cyl((sx * (h - 35), sy * (h - 35), CASTOR_R), (0, 1, 0), CASTOR_R, 28, 32))
    out["vac castors"] = (wheels[0].merge(wheels[1:]), RUBBER)
    rb = BIN_ID / 2 + 4.0
    out["vac bin"] = (lathe([(0, Z_BIN[0]), (rb - 12, Z_BIN[0]), (rb, Z_BIN[0] + 12), (rb, Z_BIN[1]),
                             (rb - 4, Z_BIN[1]), (rb - 4, Z_BIN[0] + 14), (0, Z_BIN[0] + 14)]), SS)
    out["vac gasket"] = (lathe([(rb, Z_BIN[1] - 6), (BIN_OD_GASKET / 2, Z_BIN[1] - 6), (BIN_OD_GASKET / 2, Z_BIN[1] + 8),
                                (rb, Z_BIN[1] + 8)]), RUBBER)
    # the conductive liner's fold over the rim, under the head (SOP 2.2: black carbon-loaded PE, seated on bare metal)
    out["vac liner lip"] = (lathe([(rb - 1, Z_BIN[1] - 40), (rb + 2, Z_BIN[1] - 40), (rb + 2, Z_BIN[1] - 6),
                                   (rb - 1, Z_BIN[1] - 6)]), BLACK)
    hr = BIN_OD_GASKET / 2 - 2
    out["vac housing"] = (lathe([(hr, Z_HOUSING[0] + 8), (hr, Z_HOUSING[1] - 10), (hr - 15, Z_HOUSING[1]),
                                 (0, Z_HOUSING[1]), (0, Z_HOUSING[0] + 8)]), SS)
    mr = 190.0
    out["vac motor head"] = (lathe([(0, Z_MOTOR[0]), (mr, Z_MOTOR[0]), (mr, Z_MOTOR[0] + 120), (mr - 40, Z_MOTOR[1]),
                                    (0, Z_MOTOR[1])]), SS_DK)
    out["vac hepa"] = (lathe([(0, Z_HEPA[0]), (130, Z_HEPA[0]), (130, Z_HEPA[1] - 10), (115, Z_HEPA[1]),
                              (0, Z_HEPA[1])]), SS)
    # two toggle clamps hold the head on the bin (estimated from photos), at +-y
    cl = [_box(-14, 14, s * (hr - 2), s * (hr + 22), Z_BIN[1] - 30, Z_BIN[1] + 50) for s in (-1, 1)]
    out["vac clamps"] = (cl[0].merge(cl[1]), SS_DK)
    # the inlet: a 1.5 in stub out of the bin's side on +x (the hose's cuff fits on it)
    out["vac inlet"] = (_cyl((rb + 35, 0, INLET_Z), (1, 0, 0), INLET_ID / 2 + 4, 70), SS_DK)
    # the switch: a sealed box on the motor head's +x side with a rocker (estimated from photos)
    out["vac switch"] = (_box(mr - 30, mr + 22, -36, 36, Z_MOTOR[0] + 40, Z_MOTOR[0] + 110), SS_DK)
    out["vac switch rocker"] = (_box(mr + 22, mr + 30, -14, 14, Z_MOTOR[0] + 60, Z_MOTOR[0] + 92), RED)
    # the push handle: two uprights from the trolley's -x side, a bar at the brochure's 45 in overall height
    up = [tube_along([(-h + 15, s * 150, 112), (-h - 10, s * 150, 700), (-h - 40, s * 150, HEIGHT - 15)], 13)
          for s in (-1, 1)]
    bar = _cyl((-h - 40, 0, HEIGHT - 15), (0, 1, 0), 15, 330)
    out["vac handle"] = (up[0].merge([up[1], bar]), SS)
    return out


def vacuum_local(name: str) -> np.ndarray:
    """Points on the vacuum in its own frame."""
    rb = BIN_ID / 2 + 4.0
    return {"inlet": np.array([rb + 70, 0, INLET_Z]), "ground_lug": np.array([-TROLLEY / 2, -120, 105]),
            "switch": np.array([190 + 30, 0, Z_MOTOR[0] + 76]), "cord": np.array([-120, 150, Z_MOTOR[0] + 60])}[name]


# --------------------------------------------------------------------------------------------- the tools
WAND_L = 20 * IN                   # 01768601 aluminium EXP wand: length not in our sources; 20 in assumed (+-6 in)
WAND_OD, WAND_BORE = 38.0, 35.0    # it takes the 38 mm tools in its tool-side socket (accessories doc 11.2); wall assumed
CUFF_L, CUFF_OD = 90.0, 52.0       # 4072000343 cuff, 38 mm thread x 40 mm slip (accessories doc 11): size estimated
CREVICE_L = 11 * IN                # 01768900, 11 in crevice tool (accessories doc 3b)
CREVICE_SLOT = (34.0, 11.0)        # its flat tip, estimated from photos (+-4)
BRUSH_L = 120.0                    # 01719401 dust brush: spigot top to bristle tips, estimated (+-30)
BRUSH_D = 3 * IN                   # a 3 in round head (the Ruwac kit's "3 in conductive brush"; Nilfisk's assumed)
BRISTLE_L = 28.0
# every tool: a spigot into the wand's socket, a collar ring that stops at the wand's end, a neck, then its body
SPIGOT_L, SPIGOT_R = 45.0, 17.4    # estimated from photos; the spigot is 0.1 mm under the wand's 35 mm bore
TOOL_COLLAR = (45.0, 55.0, 22.0)   # z from the spigot's top (down), and its radius
NECK = (55.0, 70.0, 19.0)
SEAT_GAP = 0.5                     # the wand's end face stops this short of the collar (drawn gap, not a real one)
# ours: the clamp collar and its fin, where the 2F-85 grips. Clamped, not drilled (no alteration of the wand).
COLLAR_AT = 95.0                   # collar centre, mm from the wand's hose end
COLLAR_L, COLLAR_R = 60.0, 27.0
FIN_T, FIN_OUT, FIN_L = 30.0, 82.0, 56.0     # fin thickness (the 2F-85 closes on it), radial reach, length
GRIP_R = 62.0                      # the grasp point's distance from the wand's axis, on the fin
PIN_R, PIN_AT = 3.0, 26.0          # the locating pin (6 mm) under the collar, on the side, for the holster's hole


def tool_reach(tool: str | None) -> float:
    """How far the tool's tip is past the wand's end when fitted."""
    L = {"crevice": CREVICE_L, "brush": BRUSH_L, None: 0.0}[tool]
    return L - TOOL_COLLAR[0] + SEAT_GAP if tool else 0.0


def wand_meshes(fin_dir=(0, -1, 0)) -> dict:
    """The wand with the cuff on its hose end and our collar, in the wand's frame: its axis on z, the hose end at z = 0,
    the tool end at z = -WAND_L (the wand points down -z), the fin along fin_dir (in the x-y plane). The wand is a
    tube (its bore open at the tool end, so a tool's spigot goes in)."""
    f = np.asarray(fin_dir, float)
    f /= np.linalg.norm(f)
    s = np.cross([0, 0, 1.0], f)
    tube = lathe([(WAND_BORE / 2, -WAND_L), (WAND_OD / 2, -WAND_L), (WAND_OD / 2, 0.0), (WAND_BORE / 2, 0.0)])
    out = {"wand tube": (tube, ALU),
           "wand cuff": (lathe([(WAND_OD / 2, -20.0), (CUFF_OD / 2 - 3, -20.0), (CUFF_OD / 2, -10.0),
                                (CUFF_OD / 2, CUFF_L - 20.0), (WAND_BORE / 2, CUFF_L - 20.0), (WAND_BORE / 2, 0.0),
                                (WAND_OD / 2, 0.0)]), BLACK)}
    zc = -COLLAR_AT
    collar = lathe([(WAND_OD / 2, zc - COLLAR_L / 2), (COLLAR_R, zc - COLLAR_L / 2), (COLLAR_R, zc + COLLAR_L / 2),
                    (WAND_OD / 2, zc + COLLAR_L / 2)])
    c = f * (COLLAR_R - 4 + FIN_OUT / 2)
    fin = pv.Box(bounds=(-FIN_OUT / 2, FIN_OUT / 2, -FIN_T / 2, FIN_T / 2, -FIN_L / 2, FIN_L / 2)).triangulate()
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2], Mx[:3, 3] = f, s, (0, 0, 1), (c[0], c[1], zc)
    out["wand collar (ours)"] = (collar.merge(fin.transform(Mx, inplace=False)), OURS)
    pc = s * PIN_AT
    out["wand pin (ours)"] = (_cyl((pc[0], pc[1], zc - COLLAR_L / 2 - 6), (0, 0, 1), PIN_R, 12, 16), BRASS)
    return out


def grasp_local(fin_dir=(0, -1, 0)) -> np.ndarray:
    """The wand-frame pose of the grasp point on the fin: tool z = -fin_dir (the approach, onto the fin), tool y
    along the wand (+z, towards the hose end), tool x across the fin's flats (where the 2F-85's fingers close)."""
    f = np.asarray(fin_dir, float)
    f /= np.linalg.norm(f)
    z = -f
    y = np.array([0, 0, 1.0])
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2] = np.cross(y, z), y, z
    Mx[:3, 3] = f * GRIP_R + np.array([0, 0, -COLLAR_AT])
    return Mx


def _tool_top(res=40) -> list:
    """The common (r, z) profile of a tool's spigot, collar and neck, from the spigot's top down."""
    return [(0, 0), (SPIGOT_R, 0), (SPIGOT_R, -TOOL_COLLAR[0]), (TOOL_COLLAR[2], -TOOL_COLLAR[0]),
            (TOOL_COLLAR[2], -TOOL_COLLAR[1]), (NECK[2], -TOOL_COLLAR[1]), (NECK[2], -NECK[1])]


def crevice_meshes() -> dict:
    """01768900 in its own frame: the spigot's top at z = 0, the tip at z = -CREVICE_L. The body flattens from the neck
    (round, 38) to a slot, its end cut at about 45 deg so it opens to -x (estimated from photos)."""
    top = lathe(_tool_top() + [(0, -NECK[1])], res=40)
    L, z0 = CREVICE_L, NECK[1]
    n, m = 12, 32
    th = np.linspace(0, 2 * math.pi, m + 1)[:-1]
    rings = []
    for k in range(n + 1):
        u = k / n
        z = -(z0 + u * (L - z0))
        a = NECK[2] * (1 - u) + CREVICE_SLOT[0] / 2 * u
        b = NECK[2] * (1 - u) + CREVICE_SLOT[1] / 2 * u
        ring = np.c_[a * np.cos(th), b * np.sin(th), np.full_like(th, z)]
        if k == n:
            ring[:, 2] += (ring[:, 0] + a) * 0.45          # the angled cut: higher on +x, the opening faces -x and down
        rings.append(ring)
    pts = np.vstack(rings)
    faces = []
    for k in range(n):
        for j in range(m):
            a0, a1 = k * m + j, k * m + (j + 1) % m
            faces += [3, a0, a1, a1 + m, 3, a0, a1 + m, a0 + m]
    body = pv.PolyData(pts, np.array(faces)).clean().compute_normals(auto_orient_normals=False)
    return {"crevice tool": (top.merge(body), ALU)}


def brush_meshes() -> dict:
    """01719401 in its own frame: the spigot's top at z = 0, the bristle tips at z = -BRUSH_L. The bristles are their
    own mesh: a soft part (they bend on the surface they brush), left out of the collision checks."""
    L = BRUSH_L
    zh = L - BRISTLE_L
    body = lathe(_tool_top() + [(BRUSH_D / 2, -(zh - 8)), (BRUSH_D / 2, -zh), (0, -zh)], res=48)
    bristles = lathe([(6, -zh), (BRUSH_D / 2 - 3, -zh), (BRUSH_D / 2 + 1, -L), (10, -L)], res=48)
    return {"dust brush": (body, ALU), "dust brush bristles": (bristles, (0.12, 0.12, 0.13))}


# --------------------------------------------------------------------------------------------- the hose
HOSE_L = 10 * 12 * IN              # 3048 mm: 1.5 in x 10 ft conductive hose (107413543; 01769218 complete)
HOSE_R = 25.0                      # its outside radius (estimated, +-3)


class Hose:
    """The hose as a chain of nodes relaxed every frame (position-based dynamics: gravity, fixed link lengths, a
    bend limit, the floor with friction, and obstacles), so it sags, lies on the floor and follows the wand without
    passing through what is round it. End A is the vacuum's inlet, end B the wand's cuff; each end leaves along its
    fitting's axis. Obstacles: boxes (x0, x1, y0, y1, z0, z1) and capsules (p, q, r), in the world."""

    def __init__(self, a, ta, b, tb, n: int = 70, guide=None):
        self.n = n
        self.seg = HOSE_L / (n - 1)
        self.boxes: list = []
        self.caps: list = []
        self.set_ends(a, ta, b, tb)
        if guide is None:
            guide = [self.a, self.b]
        g = np.asarray(guide, float)
        d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(g, axis=0), axis=1))]
        s = np.linspace(0, d[-1], n)
        self.p = np.c_[[np.interp(s, d, g[:, k]) for k in range(3)]].T
        self.relax(400)

    def set_ends(self, a, ta, b, tb):
        self.a, self.b = np.asarray(a, float), np.asarray(b, float)
        self.ta = np.asarray(ta, float) / np.linalg.norm(ta)
        self.tb = np.asarray(tb, float) / np.linalg.norm(tb)

    def _pin(self):
        p = self.p
        p[0], p[1] = self.a, self.a + self.ta * self.seg
        p[-1], p[-2] = self.b, self.b + self.tb * self.seg

    def relax(self, iters: int = 40, grav: float = 4.0):
        p = self.p
        n, seg = self.n, self.seg
        for _ in range(iters):
            on_floor = p[:, 2] <= HOSE_R + 0.5
            p[~on_floor, 2] -= grav
            self._pin()
            for _k in range(2):
                d = p[1:] - p[:-1]
                L = np.linalg.norm(d, axis=1) + 1e-9
                corr = (d.T * ((L - seg) / L) * 0.5).T
                p[:-1] += corr
                p[1:] -= corr
                d2 = p[2:] - p[:-2]                  # bend limit: neighbours two apart at least 1.75 links apart
                L2 = np.linalg.norm(d2, axis=1) + 1e-9
                short = L2 < 1.75 * seg
                c2 = (d2.T * (np.where(short, (L2 - 1.75 * seg) / L2, 0.0)) * 0.25).T
                p[:-2] += c2
                p[2:] -= c2
                self._pin()
            self._collide()
            self._pin()
        self.p = p

    def _collide(self):
        p = self.p
        r = HOSE_R
        p[:, 2] = np.maximum(p[:, 2], r)
        for (x0, x1, y0, y1, z0, z1) in self.boxes:
            lo = np.array([x0 - r, y0 - r, z0 - r])
            hi = np.array([x1 + r, y1 + r, z1 + r])
            inside = np.all((p > lo) & (p < hi), axis=1)
            inside[[0, 1, -2, -1]] = False
            if not inside.any():
                continue
            q = p[inside]
            pen = np.c_[q - lo, hi - q]                  # distance to each of the six faces
            k = np.argmin(pen, axis=1)
            for i, kk in enumerate(k):
                ax = kk % 3
                q[i, ax] = lo[ax] if kk < 3 else hi[ax]
            p[inside] = q
        for (a, b, rr) in self.caps:
            a, b = np.asarray(a, float), np.asarray(b, float)
            ab = b - a
            t = np.clip(((p - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
            c = a + np.outer(t, ab)
            d = p - c
            dist = np.linalg.norm(d, axis=1) + 1e-9
            hit = dist < rr + r
            hit[[0, 1, -2, -1]] = False
            if hit.any():
                p[hit] = c[hit] + (d[hit].T * ((rr + r) / dist[hit])).T

    def mesh(self) -> pv.PolyData:
        return pv.Spline(self.p, self.n * 3).tube(radius=HOSE_R, n_sides=14, capping=False).triangulate()

    def length(self) -> float:
        return float(np.linalg.norm(np.diff(self.p, axis=0), axis=1).sum())


# --------------------------------------------------------------------------------------------- the area's kit
PAIL_H, PAIL_OD_TOP, PAIL_OD_BOT = 13.4 * IN, 11.75 * IN, 10.75 * IN   # S-20030BL figures (a proxy for S-7344)


def pail_meshes() -> dict:
    """Uline S-7344, 5 gal open-top steel pail, its lid set on (not crimped: SOP 4.4), a bail and a bonding wire with
    a ring terminal (accessories doc 10.3). Sizes from Uline's S-20030BL listing (Hydrobuilder), a proxy."""
    rt, rb, h = PAIL_OD_TOP / 2, PAIL_OD_BOT / 2, PAIL_H
    body = lathe([(0, 0), (rb, 0), (rb, 6), (rt - 4, h - 12), (rt, h - 10), (rt, h - 4), (rt - 6, h - 4), (rb - 6, 8),
                  (0, 8)])
    lid = lathe([(0, h - 2), (rt + 4, h - 2), (rt + 4, h + 14), (0, h + 14)])
    bail = tube_along([(-rt - 3, 0, h - 40), (-rt * 0.7, 0, h + 70), (0, 0, h + 95), (rt * 0.7, 0, h + 70),
                       (rt + 3, 0, h - 40)], 2.5, 10)
    return {"pail": (body, (0.32, 0.33, 0.35)), "pail lid (set on, not crimped)": (lid, (0.28, 0.29, 0.31)),
            "pail bail": (bail, SS_DK)}


EXT = dict(model="Amerex B570", agent="sodium chloride (Class D)", lb=30, h=35 * IN, w=13 * IN, d=8 * IN)
# Airgas's B570 listing: 13 W x 8 D x 35 H in, 24 s discharge. (Amerex's B571 is the copper-powder unit, for lithium.)


def extinguisher_meshes() -> dict:
    """A 30 lb Class D extinguisher on a floor stand: a cylinder 8 in across, 35 in tall overall with its valve and
    the long applicator wand on its hose (Airgas listing sizes)."""
    r = EXT["d"] / 2
    h = EXT["h"]
    stand = _box(-150, 150, -150, 150, 0, 12).merge([_box(-150, -138, -30, 30, 12, 700), _box(-155, -133, -45, 45, 500, 540)])
    body = lathe([(0, 40), (r, 40), (r, h - 170), (r - 30, h - 120), (24, h - 105), (0, h - 105)])
    valve = _cyl((0, 0, h - 80), (0, 0, 1), 22, 50).merge(_box(-14, 70, -10, 10, h - 70, h - 50))
    applicator = tube_along([(20, 0, h - 90), (130, 20, h - 300), (r + 30, -40, 300)], 7, 10).merge(
        _cyl((r + 30, -40, 260), (0, 0, 1), 16, 120))
    return {"ext stand": (stand, (0.35, 0.36, 0.38)), "ext cylinder": (body, RED), "ext valve": (valve, SS_DK),
            "ext applicator": (applicator, BLACK)}


SIGN_LINES = ("COMBUSTIBLE METAL", "POWDER IN USE", "Authorized personnel only", "NO water, NO compressed air")
# SOP 2.3: "COMBUSTIBLE METAL POWDER IN USE - Authorized Personnel Only - NO Water, NO Compressed Air"


def sign_meshes() -> dict:
    """An A-frame floor sign (yellow) with the SOP's wording, its face toward -y."""
    w, h = 460.0, 620.0
    board = _box(-w / 2, w / 2, -8, 0, 300, 300 + h)
    legs = _box(-w / 2, -w / 2 + 25, -4, 160, 0, 300 + h).merge(_box(w / 2 - 25, w / 2, -4, 160, 0, 300 + h))
    texts = []
    for k, (line, size) in enumerate(zip(SIGN_LINES, (44, 44, 26, 26))):
        t = pv.Text3D(line, depth=2.0, height=size)
        b = t.bounds
        t.translate((-(b[0] + b[1]) / 2, 0, 0), inplace=True)
        t.rotate_x(90, inplace=True)
        t.translate((0, -10.0, 300 + h - 90 - k * 110 - (0 if k < 2 else 40)), inplace=True)
        texts.append(t.triangulate())
    return {"sign board": (board, YELLOW), "sign legs": (legs, (0.20, 0.20, 0.22)),
            "sign text": (texts[0].merge(texts[1:]), BLACK)}


# --------------------------------------------------------------------------------------------- our station
POST_H = 1090.0                    # the station's post (ours): bonded steel, 60 x 60
HOLSTER_Z = 1000.0                 # the holster fork's top: the collar's underside rests on it
HOLSTER_Y = -150.0                 # the hanging wand's axis, out from the post towards the MiR (-y)
RACK_Z = 600.0                     # the tool rack's support plates' tops (a parked tool's collar rests there)
RACK_X = (150.0, 245.0)            # pocket A (the crevice tool), pocket B (the dust brush), on the post's +x side
RACK_Y = -70.0
FIXTURE_Z = 200.0                  # the continuity fixture's spring pad (the tool tip lands on it)
FIXTURE_X = -175.0
BUTTON_Z = 420.0                   # the ground button (the equalization touch)
PLATE_T = 8.0


def _slotted(x, y, z0, z1, half_w, w=70.0, d=70.0):
    """A plate (x +-w/2, y +-d/2) with a slot of half-width half_w from its centre out to -y, built from three
    boxes so the slot is open."""
    return [_box(x - w / 2, x - half_w, y - d / 2, y + d / 2, z0, z1), _box(x + half_w, x + w / 2, y - d / 2, y + d / 2, z0, z1),
            _box(x - half_w, x + half_w, y + half_w, y + d / 2, z0, z1)]


def station_meshes() -> dict:
    """Ours: a bonded steel post on a base plate, in its own frame (the post at the origin; the MiR comes from -y). On
    it: the holster fork (the wand hangs in it nose down, the collar on the fork, the pin in the fork's hole), the
    tool rack's two keyhole pockets (+x), the continuity fixture (-x), the ground button, and the meter on a shelf."""
    out = {}
    out["stn base"] = (_box(-300, 300, -200, 120, 0, 14), SS_DK)
    out["stn post"] = (_box(-30, 30, -30, 30, 14, POST_H), SS_DK)
    hz, hy = HOLSTER_Z, HOLSTER_Y
    arm = _box(-20, 20, hy + 20, -30, hz - 40, hz - 14)
    tines = _slotted(0.0, hy, hz - 14, hz, 20.0, w=110.0, d=80.0)
    out["stn holster (ours)"] = (arm.merge(tines), OURS)
    # the pin's hole in the right tine (the collar's pin, PIN_AT along +x of the wand): drawn as a dark ring
    out["stn holster hole"] = (lathe([(PIN_R + 0.5, hz - 0.2), (PIN_R + 2.5, hz - 0.2), (PIN_R + 2.5, hz + 0.3),
                                     (PIN_R + 0.5, hz + 0.3)], 24).translate((PIN_AT, hy, 0), inplace=False), BLACK)
    # tool rack: each pocket is two slotted plates, the collar slides between them from -y: the lower one carries the
    # parked tool by its collar (slot 2 x 19.8 passes the neck, 38), the upper one holds it down while the wand pulls
    # off (slot 2 x 18.0 passes the spigot, 34.8); both under the collar's 44
    parts = [_box(30, 290, RACK_Y - 15, RACK_Y + 15 + 35, RACK_Z - 40, RACK_Z - 28)]
    col_h = TOOL_COLLAR[1] - TOOL_COLLAR[0]
    for x in RACK_X:
        parts += _slotted(x, RACK_Y, RACK_Z - PLATE_T, RACK_Z, 19.8)
        z2 = RACK_Z + 0.5 + col_h + 0.5
        parts += _slotted(x, RACK_Y, z2, z2 + PLATE_T, 18.0)
        parts.append(_box(x - 35, x - 25, RACK_Y + 25, RACK_Y + 35, RACK_Z - 40, z2 + PLATE_T))
    out["stn tool rack (ours)"] = (parts[0].merge(parts[1:]), OURS)
    fz, fx = FIXTURE_Z, FIXTURE_X
    out["stn fixture (ours)"] = (_box(fx - 35, -30, -85, -35, fz - 40, fz - 12), OURS)
    out["stn fixture pad (spring)"] = (_cyl((fx, -60, fz - 6), (0, 0, 1), 22, 12), BRASS)
    # the probe column: three spring probes, at the tool-to-wand joint, the wand's top and the cuff, when the wand
    # stands on the pad (heights set in the clip from the assembly's lengths)
    out["stn relay box (ours)"] = (_box(-140, -40, -150, -90, 20, 120), OURS_DK)
    out["stn meter shelf"] = (_box(-290, -150, -190, -40, 300, 310), SS_DK)
    out["stn meter"] = (_box(-280, -160, -175, -95, 310, 380), (0.25, 0.27, 0.30))
    out["stn meter display"] = (_box(-265, -175, -177, -174, 335, 372), LCD)
    out["stn ground button (spring)"] = (_cyl((0, -41, BUTTON_Z), (0, 1, 0), 14, 22), BRASS)
    out["stn ground lug"] = (_box(-20, 20, 30, 50, 20, 60), (0.55, 0.45, 0.25))
    return out


def probe_column(z_joints) -> pv.PolyData:
    """The fixture's probe column (ours): a bar beside the standing wand with a spring probe at each height in
    z_joints, each probe's tip 1 mm off the wand's surface (they touch when the wand leans on them)."""
    fx = FIXTURE_X
    bar = _box(fx - 75, fx - 60, -70, -50, FIXTURE_Z - 12, max(z_joints) + 30)
    probes = [_cyl((fx - 50.5, -60, z), (1, 0, 0), 4, 19, 16) for z in z_joints]
    return bar.merge(probes)


def station_points() -> dict:
    """Named points in the station's frame."""
    return {"holster": np.array([0.0, HOLSTER_Y, HOLSTER_Z + 0.3]),
            # a parked tool's spigot top: its collar's underside 0.5 mm over the lower plate
            "pocket_a": np.array([RACK_X[0], RACK_Y, RACK_Z + 0.5 + TOOL_COLLAR[1]]),
            "pocket_b": np.array([RACK_X[1], RACK_Y, RACK_Z + 0.5 + TOOL_COLLAR[1]]),
            "pad": np.array([FIXTURE_X, -60.0, FIXTURE_Z]), "button": np.array([0.0, -52.0, BUTTON_Z]),
            "meter": np.array([-220.0, -177.0, 355.0])}


SOFT = ("dust brush bristles", "stn fixture pad (spring)", "stn ground button (spring)")
