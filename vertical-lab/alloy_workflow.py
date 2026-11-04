"""The alloy workflow along the line: a build plate from the Aconity MIDI, through a depowdering box, to the wire EDM,
and a tensile bar from the EDM, rinsed and dried, to the Instron 68FM-100, carried by the UR10e on its MiR250 (#303,
round 4; the depowdering and the rinse, round 5, take out the two steps that had been left to a person).

    xvfb-run -a python3 alloy_workflow.py            # -> out/alloy_workflow.gif, out/mp4/alloy_workflow.mp4, .json
    PREVIEW=1 xvfb-run -a python3 alloy_workflow.py  # the last frame of each sub-step -> /tmp/preview_alloy_workflow.png

The scene is ``line.py``'s layout (the VLM, the rePowder and the line's machines at ``line.LINE``), without the rail:
the arm is on the MiR250, which drives along the fronts. What is new is in ``alloy_models.py``: the Aconity MIDI with
its chamber opened up, the plate and its bars, the EDM's fixture and wire head, the holders on the MiR, the suction
lance on its post, the depowdering box (in the 544 mm between the printer and the 68FM-100) and the rinse cup (in the
410 mm between the 68SC-2 and the EDM). Every arm move
is a straight line of the gripper's grasp point solved with the UR's inverse kinematics every frame, or a joint move
between two solved poses (``robot.py``), as in ``animate.workflow()``. Where a machine is opened up to show the
inside, its shell is drawn see-through ("ghosted") while the process runs.

Real data on screen: the SEM image of the lab's AlSi10Mg powder (DAL ``figures/sem``, taken at BYU by Gage Erickson
on 2 April 2026, posted on byu-vcl#48). The stress-strain curve is not a measurement: it is a smooth curve through
the as-built values AddUp publishes for LPBF AlSi10Mg, and it says so on screen.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw

import scene
scene.GIF_FPS = 5                     # a 2-minute GIF under 4.9 MB: 5 fps at 640 x 360 (the MP4 keeps every frame)
scene.GIF_SIZE = (640, 360)
from scene import CLEAN, FPS, OUT, PREVIEW, Scene, T, R, S, font  # noqa: E402

import animate as A                   # noqa: E402
import alloy_models as M              # noqa: E402
import lab                            # noqa: E402
import line                           # noqa: E402
import props as P                     # noqa: E402
import robot as RB                    # noqa: E402
import tour                           # noqa: E402

TITLE = "Vertical cloud lab: from the metal printer to the tensile test"
NAME = "alloy_workflow"
HERE = Path(__file__).resolve().parent
SEM = Path("/tmp/dal/figures/sem/AlSi10Mg_carbon_adhesive_SEM.png")
SEM_LOCAL = HERE / "out" / "alloy_sem_AlSi10Mg_carbon_adhesive.png"      # a copy, so the render doesn't need /tmp/dal
SEM_CREDIT = ["The lab's stock AlSi10Mg powder: SEM, 500x, 5 kV,",
              "BYU's Apreo, Gage Erickson, 2 Apr 2026 (byu-vcl#48;",
              "DAL figures/sem). The powder a plate like this is printed from."]

# ------------------------------------------------------------------------------------------------- numbers
# stress-strain: AddUp's AlSi10Mg data sheet (US-10252023-0129, FormUp 350, 50 um layers, ASTM E8, machined, n >= 27),
# as built, XY: E 72 +- 3 GPa, YS 275 +- 8 MPa, UTS 412 +- 38 MPa, elongation 5 +- 2 %.
SS = dict(E=72000.0, ys=275.0, uts=412.0, elong=0.05, src="AddUp AlSi10Mg data sheet, as built, XY, ASTM E8")
AREA = M.E8_SUB["W"] * M.E8_SUB["T"]          # 6 x 6 mm reduced section
TEST = 3                                      # the bar the workflow tests: the first one the wire cuts
GRIP_LUG = 0.88                               # 2F-85 closure for the 12 mm lug (ur_arm.gripper_fk: 0.9 -> 10 mm)
GRIP_BAR = 0.90                               # for the bar's 10 mm grip end
GRIP_NEAR = 0.78                              # opened only 21 mm, to reach between the cut bars
TILT = 30.0                                   # the grasp in the Aconity's chamber points 30 deg down (see grasp_aco)
MIR_Y = line.Y_FACE - 230.0 - P.MIR["W"] / 2  # the MiR250 parks 230 mm off the fronts, broadside, arm towards them
MIR_SPEED = 1500.0                            # mm/s; the MiR250's maximum is 2.0 m/s (MiR250 data sheet)

BLUE = (30, 60, 140)
CURVE = (31, 94, 168)
MUTED = (110, 114, 120)


# ================================================================================================= the curve
def ss_points(n: int = 240) -> np.ndarray:
    """(strain, stress MPa): elastic at E, then Voce hardening, s = s0 + Q (1 - exp(-b ep)), through YS at 0.2 %
    plastic strain and UTS at the elongation, where as-built AlSi10Mg breaks (Kempen et al. 2012: "all samples were
    seen to break at UTS"). b = 100 sets the knee's roundness; the four published values are what it is fitted to."""
    E, ys, uts, epf = SS["E"], SS["ys"], SS["uts"], SS["elong"]
    b = 100.0
    a1, a2 = 1 - math.exp(-b * 0.002), 1 - math.exp(-b * epf)
    Q = (uts - ys) / (a2 - a1)
    s0 = ys - Q * a1
    ep = np.linspace(0, epf, n)
    s = s0 + Q * (1 - np.exp(-b * ep))
    e = s / E + ep
    return np.vstack([[0.0, 0.0], np.c_[e, s]])


SS_PTS = ss_points()


# ================================================================================================= the scene
class AlloyScene(Scene):
    """Scene with insets drawn over every frame: the SEM image, the stress-strain plot."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.sem_a = 0.0                 # SEM inset opacity
        self.ss_u = None                 # stress-strain: fraction of the curve drawn (None: hidden)
        self.ss_broken = False
        self._sem = None

    def overlay(self, img, scale, anchors):
        img = super().overlay(img, scale, anchors)
        if CLEAN:
            return img
        if self.sem_a > 0.02:
            self._draw_sem(img)
        if self.ss_u is not None:
            self._draw_ss(img)
        return img

    def _draw_sem(self, img):
        W, H = img.size
        k = W / 1280
        if self._sem is None:
            src = SEM_LOCAL if SEM_LOCAL.exists() else SEM
            self._sem = Image.open(src).convert("RGB")
        w = int(400 * k)
        h = int(w * self._sem.height / self._sem.width)
        pic = self._sem.resize((w, h), Image.LANCZOS)
        x0, y0 = W - w - int(14 * k), int(52 * k)
        s = max(k, 0.8)
        fc = font(12.5 * s)
        lh = 15 * s
        box = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(box)
        d.rounded_rectangle((x0 - 6 * k, y0 - 6 * k, x0 + w + 6 * k, y0 + h + 8 * k + len(SEM_CREDIT) * lh),
                            6 * k, fill=(255, 255, 255, 235), outline=(150, 154, 160, 255))
        a = int(255 * self.sem_a)
        box.paste(pic, (x0, y0))
        for i, t in enumerate(SEM_CREDIT):
            d.text((x0, y0 + h + 4 * k + i * lh), t, font=fc, fill=(20, 20, 24, 255))
        alpha = box.getchannel("A").point(lambda v: v * a // 255)
        box.putalpha(alpha)
        img.paste(box, (0, 0), box)

    def _draw_ss(self, img):
        W, H = img.size
        k = W / 1280
        s = max(k, 0.8)
        bw, bh = int(430 * k), int(300 * k)
        x0, y0 = W - bw - int(14 * k), int(52 * k)
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 6 * k, fill=(255, 255, 255, 238), outline=(150, 154, 160, 255))
        ft, fa, fn = font(13.5 * s, bold=True), font(11.5 * s), font(10.5 * s)
        d.text((x0 + 10 * k, y0 + 6 * k), "Stress-strain, as-built LPBF AlSi10Mg (XY)", font=ft, fill=(20, 20, 24))
        # plot area
        px0, px1 = x0 + 52 * k, x0 + bw - 14 * k
        py0, py1 = y0 + 34 * k, y0 + bh - 66 * k
        emax, smax = 0.06, 500.0

        def X(e):
            return px0 + (px1 - px0) * e / emax

        def Y(sg):
            return py1 - (py1 - py0) * sg / smax
        for sg in (0, 100, 200, 300, 400, 500):
            d.line([(px0, Y(sg)), (px1, Y(sg))], fill=(232, 234, 238), width=1)
            d.text((px0 - 6 * k, Y(sg)), f"{sg}", font=fa, fill=MUTED, anchor="rm")
        for e in (0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06):
            d.text((X(e), py1 + 4 * k), f"{e * 100:.0f}", font=fa, fill=MUTED, anchor="mt")
        d.line([(px0, py1), (px1, py1)], fill=(150, 154, 160), width=max(1, int(k)))
        d.line([(px0, py0), (px0, py1)], fill=(150, 154, 160), width=max(1, int(k)))
        d.text(((px0 + px1) / 2, py1 + 17 * k), "strain, %", font=fa, fill=MUTED, anchor="mt")
        d.text((px0 + 4 * k, py0 - 3 * k), "MPa", font=fa, fill=MUTED, anchor="lb")
        # the published values as reference lines, labelled in text ink
        for val, txt, left in ((SS["uts"], f"UTS {SS['uts']:.0f}", True), (SS["ys"], f"yield {SS['ys']:.0f}", False)):
            yy = Y(val)
            for xx in np.arange(px0, px1, 9 * k):
                d.line([(xx, yy), (min(xx + 5 * k, px1), yy)], fill=(140, 144, 150), width=max(1, int(k)))
            if left:
                d.text((px0 + 6 * k, yy - 2 * k), txt, font=fa, fill=(70, 72, 78), anchor="ld")
            else:
                d.text((px1 - 4 * k, yy - 2 * k), txt, font=fa, fill=(70, 72, 78), anchor="rd")
        # the curve, up to u
        n = max(2, int(round(self.ss_u * (len(SS_PTS) - 1))) + 1)
        pts = [(X(e), Y(sg)) for e, sg in SS_PTS[:n]]
        d.line(pts, fill=CURVE, width=max(2, int(round(2.4 * k))), joint="curve")
        ex, ey = pts[-1]
        r = 4.5 * k
        if self.ss_broken:
            d.line([(ex - r, ey - r), (ex + r, ey + r)], fill=(190, 30, 30), width=max(2, int(2 * k)))
            d.line([(ex - r, ey + r), (ex + r, ey - r)], fill=(190, 30, 30), width=max(2, int(2 * k)))
        else:
            d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=CURVE, outline=(255, 255, 255))
        e_now, s_now = SS_PTS[n - 1]
        d.text((px1, py0 + 2 * k), f"{s_now:.0f} MPa  {s_now * AREA / 1000:.1f} kN", font=fa, fill=(20, 20, 24),
               anchor="ra")
        d.text((x0 + 10 * k, y0 + bh - 30 * k), "Not measured here: a smooth curve through AddUp's published as-built",
               font=fn, fill=(70, 72, 78))
        d.text((x0 + 10 * k, y0 + bh - 16 * k), "values (E 72 GPa, YS 275, UTS 412 MPa, 5 %), ASTM E8, machined.",
               font=fn, fill=(70, 72, 78))


def status(sc, **kv):
    """The status table under the title."""
    rows = dict(sc._rows) if hasattr(sc, "_rows") else {}
    rows.update(kv)
    sc._rows = rows
    sc.gauges = [(k, v) for k, v in rows.items() if v]


def build():
    data = lab.meshes()
    idata = tour.load(["instron_floor", "instron_small", "wire_edm", "glovebox"])
    sc = AlloyScene(NAME, TITLE)
    sc.intro = 0.8
    L = A.Lab(sc, data, robot=False)
    L.show_gauges = False
    L.skin(0.0)(1.0)
    L.apply_state()
    sc.add("line floor", pv.Plane(center=(1200, -900, -1.5), direction=(0, 0, 1), i_size=34000, j_size=18000),
           A.FLOOR_C, "floor", ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
    rigs = {}
    for key in ("glovebox", "instron_floor", "instron_small", "wire_edm"):
        inst, ents = idata[key]
        rigs[key] = tour.Rig(sc, inst, ents, f"{key}:", at=line.place_floor(inst.bbox(), line.LINE[key]))
    rigs["wire_edm"].v["~load"] = 1.0 / 0.82        # its own plate and wire head: replaced by ours
    rigs["wire_edm"].v["~wirehead"] = 1.0 / 0.82
    rigs["wire_edm"].v["glow"] = 0.0
    rigs["instron_floor"].v["~specimen"] = 1.0 / 0.82
    for r in rigs.values():
        r.apply()
    W = Aconity(sc)
    E = Edm(sc, rigs["wire_edm"])
    amr = Mir(sc)
    sc.dbox = DBox(sc)
    sc.rinse = rinse_stand(sc, E)
    return sc, L, rigs, W, E, amr


# ------------------------------------------------------------------------------------------------- depowdering
DBOX_X = 4758.0           # centred in the 544 mm the line leaves between the Aconity (to x 4486) and the 68FM-100 (5030)
LSTAND_X = 3420.0         # the lance's post, in front of the Aconity right of its chamber: in reach from the MiR's spot
LANCE_TIP = M.LANCE["grip"] + M.LANCE["L"] + 26.0     # grasp point to the nozzle's mouth
LANCE_DOWN = 25.0         # the lance in the chamber points 25 deg down: the 280 mm chamber leaves no room for steeper


class DBox:
    """The depowdering box (alloy_models.depowder_box), its suction lance in the holster and the hose between them."""

    def __init__(self, sc):
        self.sc = sc
        sc.gmat["dbox"] = T((DBOX_X, line.Y_FACE, 0))
        self.names = {}
        for piece, parts in M.depowder_box().items():
            g = "dbox" if piece == "body" else f"dbox_{piece}"
            self.names[piece] = []
            for name, (mesh, col, spec, op) in parts.items():
                n = f"dbox/{piece}/{name}"
                sc.add(n, mesh, col, g, opacity=op, specular=spec)
                self.names[piece].append(n)
            if g != "dbox":
                sc.parent[g] = "dbox"
        self.door_f, self.angle, self._g = 0.0, 0.0, 0.0
        sc.gmat["lstand"] = T((LSTAND_X, line.Y_FACE, 0))
        for name, (mesh, col, spec, op) in M.lance_stand().items():
            sc.add(f"lstand/{name}", mesh, col, "lstand", opacity=op, specular=spec)
        for name, (mesh, col, spec) in M.lance().items():
            sc.add(f"lance/{name}", mesh, col, "lance", specular=spec)
        sc.parent["lance"] = "lstand"
        sc.gmat["lance"] = T(M.HOLSTER) @ R((1, 0, 0), -90.0)          # hanging nozzle down in its forks
        sc.add("lance hose", self.hose(), (0.16, 0.17, 0.19), "hose", specular=0.25)
        # the floor pipe from the post's port to the box's separator
        a = self.lworld(M.STAND_PORT)
        b = self.world(M.HOSE_INLET)
        yp = line.Y_FACE - 60.0
        pipe = pv.lines_from_points(np.array([(a[0], yp, 30.0), (b[0], yp, 30.0), (b[0], yp, b[2]), tuple(b)]))
        sc.add("floor pipe", pipe.tube(radius=17.0, n_sides=16).triangulate(), (0.62, 0.63, 0.66), "static",
               specular=0.4)
        sc.add("dbox fall", pv.PolyData(np.zeros((1, 3))), M.POWDER, "dbox_fall", style="points", point_size=4.0,
               render_points_as_spheres=True)
        sc.parent["dbox_fall"] = "dbox"
        sc.alpha["dbox fall"] = 0.0
        sc.add("lance suck", pv.PolyData(np.zeros((1, 3))), M.POWDER, "lance_suck", style="points", point_size=4.0,
               render_points_as_spheres=True)
        sc.alpha["lance suck"] = 0.0
        # what the lance leaves on the plate: loose grains round the bars and the lug, shaken off in the box
        rng = np.random.default_rng(3)
        pts = []
        while len(pts) < 260:
            x, y = rng.uniform(-82, 82, 2)
            if x * x + y * y < 80.0 ** 2:
                pts.append((x, y, rng.uniform(0.8, 3.0)))
        sc.add("plate residue", pv.PolyData(np.array(pts)), M.POWDER, "plate_res", style="points", point_size=3.5,
               render_points_as_spheres=True)
        sc.parent["plate_res"] = "plate"
        sc.alpha["plate residue"] = 0.0

    def world(self, p):
        return (self.sc.world("dbox") @ np.r_[p, 1.0])[:3]

    def lworld(self, p):
        return (self.sc.world("lstand") @ np.r_[p, 1.0])[:3]

    def hose(self):
        """The hose from the barb on the lance's handle to the port on its post: out along the barb, which points away
        from the gripper (down, or to the front), then forward of the machines' fronts before it drops to the port,
        so it never runs back through the gripper nor down through the printer's cabinet."""
        Lw = self.sc.world("lance")
        bx, by, _, bz = M.BARB
        p0 = (Lw @ np.r_[bx, by, bz, 1.0])[:3]
        a = p0 - Lw[:3, 2] * 45.0
        p1 = self.lworld(M.STAND_PORT) + (0, 0, 20.0)
        x = np.array([0.5 * (a[0] + p1[0]), min(a[1], line.Y_FACE - 60.0), max(min(a[2] - 60.0, 1080.0), 700.0)])
        pts = np.array([p0, a, x, p1 + (0, 0, 260.0), p1])
        return pv.Spline(pts, 80).tube(radius=13.0, n_sides=14).triangulate()

    def update_hose(self):
        self.sc.set_mesh("lance hose", self.hose())

    def with_hose(self, f):
        def up(u):
            if f is not None:
                f(u)
            self.update_hose()
        return up

    def door(self, f1):
        f0 = self.door_f

        def up(u):
            self.door_f = f0 + (f1 - f0) * u
            self.sc.gmat["dbox_door"] = T((0, 0, M.DBOX["lift"] * self.door_f))
        return up

    def ghost(self, f1):
        names = self.names["walls"] + self.names["door"] + [n for n in self.names["body"] if "cabinet" in n]
        f0 = self._g

        def up(u):
            self._g = f0 + (f1 - f0) * u
            for n in names:
                self.sc.alpha[n] = 1.0 - 0.80 * self._g
        return up

    def set_angle(self, deg, shake=0.0):
        self.angle = deg
        p = M.DBOX
        jit = T((0, 0.0, shake))
        self.sc.gmat["dbox_rotor"] = jit @ R((1, 0, 0), deg, (0.0, p["axis_y"], p["axis_z"]))

    def seat_tcp(self):
        """The TCP (lug grasp) when the plate sits on the chuck, rotor at 0, world."""
        p = M.DBOX
        return self.world((p["chuck_x"] - 78.0, p["axis_y"], p["chuck_top"] + M.PLATE["t"] + 28.0))


def rinse_stand(sc, E):
    """The dip-and-blow cup on its stand in front of the EDM, 380 mm left of where the MiR stands to load it."""
    x = line.LINE["wire_edm"] - 2120.0 / 2 - 120.0      # in the 410 mm between the 68SC-2 and the EDM (2120 wide)
    sc.gmat["rinse"] = T((x, line.Y_FACE - 80.0, 0))
    for name, (mesh, col, spec, op) in M.rinse_cup().items():
        sc.add(f"rinse/{name}", mesh, col, "rinse", opacity=op, specular=spec)
    sc.fluids = getattr(sc, "fluids", set()) | {"rinse/liquid"}   # the bar is dipped in it: not an obstacle (collide.py)
    return x


# ------------------------------------------------------------------------------------------------- Aconity
class Aconity:
    """The opened Aconity MIDI in the line, with its door, build piston, plate, bars and powder."""

    def __init__(self, sc):
        self.sc = sc
        ents = M.aconity_pieces()
        pts = np.vstack([e["mesh"].points for k, lst in ents.items() if k != "piston" for e in lst
                         if e["mesh"].n_points])
        lo, hi = pts.min(0), pts.max(0)
        sc.gmat["aco"] = line.place_floor((lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]), line.LINE["aconity"])
        self.names = {}
        for piece, lst in ents.items():
            g = "aco" if piece == "body" else f"aco_{piece}"
            self.names[piece] = []
            for i, e in enumerate(lst):
                n = f"aco/{piece}/{e['material']}{i}"
                sc.add(n, e["mesh"], e["color"], g, opacity=e["opacity"], specular=e["specular"])
                self.names[piece].append(n)
            if g != "aco":
                sc.parent[g] = "aco"
        self.floor = M.ACO["floor"]
        self.build_h = M.LUG[5]                       # the build is as tall as the lug: 40 mm
        self.piston_top = self.floor - self.build_h - M.PLATE["t"]
        self.door_f = 0.0
        # the plate, its lug and the bars, on the piston
        for name, (mesh, col, spec) in M.plate_parts().items():
            sc.add(f"plate/{name}", mesh, col, "plate", specular=spec)
        sc.parent["plate"] = "aco_piston"
        sc.gmat["plate"] = T((0, 0, M.PLATE["t"]))
        for k, x in enumerate(M.BAR_X):
            g = f"bar{k}"
            if k == TEST:
                sc.add(f"bar{k}/a", M.bar_mesh("lo"), M.AS_BUILT, g, specular=0.2)
                sc.add(f"bar{k}/b", M.bar_mesh("hi"), M.AS_BUILT, f"{g}_b", specular=0.2)
                sc.parent[f"{g}_b"] = g
            else:
                sc.add(f"bar{k}/a", M.bar_mesh(), M.AS_BUILT, g, specular=0.2)
            sc.parent[g] = "plate"
            sc.gmat[g] = T((x, 0, 0))
        # the powder cake around the parts: a cylinder of unit height, scaled
        cake = pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=M.ACO["bore"] / 2 - 0.3, height=1.0,
                           resolution=72).triangulate()
        sc.add("aco powder cake", cake, M.POWDER, "aco_cake", specular=0.05)
        sc.parent["aco_cake"] = "aco"
        self.set_piston(self.piston_top)

    def bp(self, z=None):
        return M.build_point(z)

    def set_piston(self, z_top):
        """The piston's top at z_top (model frame); the powder fills the bore from the plate up to the floor."""
        self.piston_top = z_top
        self.sc.gmat["aco_piston"] = T(self.bp(z_top))
        plate_top = z_top + M.PLATE["t"]
        h = self.floor - plate_top
        self.sc.alpha["aco powder cake"] = 1.0 if h > 0.6 else 0.0
        self.sc.gmat["aco_cake"] = T(self.bp(plate_top)) @ S((1, 1, max(h, 0.01)))

    def piston_to(self, z1):
        z0 = self.piston_top

        def up(u):
            self.set_piston(z0 + (z1 - z0) * u)
        return up

    def door(self, f1):
        f0 = self.door_f
        piv = M.door_pivot()

        def up(u):
            self.door_f = f0 + (f1 - f0) * u
            self.sc.gmat["aco_door"] = R((0, 0, 1), 100.0 * self.door_f, piv)
        return up

    def ghost(self, f1, pieces=("shell", "door", "cabinet")):
        """Shell, door and base cabinet from opaque (0) to see-through (1)."""
        names = [n for p in pieces for n in self.names[p]]
        f0 = getattr(self, "_g", 0.0)

        def up(u):
            self._g = f0 + (f1 - f0) * u
            for n in names:
                self.sc.alpha[n] = 1.0 - 0.80 * self._g
        return up

    def world(self, p):
        return (self.sc.world("aco") @ np.r_[p, 1.0])[:3]


# ------------------------------------------------------------------------------------------------- EDM
class Edm:
    """The FANUC's fixture, our wire head and the cut."""
    PC = np.array([-430.0, -880.0, 930.0])        # the plate's bar face, centre, in the EDM's frame (on edge)
    Z_LO, Z_HI = 840.0, 1020.0

    def __init__(self, sc, rig):
        self.sc, self.rig = sc, rig
        body = f"{rig.prefix}body"
        for name, (mesh, col) in M.edm_fixture(self.PC).items():
            sc.add(f"edm fix/{name}", mesh, col, "edm_fix", specular=0.3)
        sc.parent["edm_fix"] = body
        for name, (mesh, col) in M.wire_head(self.Z_LO, self.Z_HI).items():
            kw = dict(ambient=0.6, specular=0.8) if name == "wire" else {}
            sc.add(f"edm head/{name}", mesh, col, "edm_head", **kw)
        sc.parent["edm_head"] = body
        self.wire_y = self.PC[1] - 0.15                # the wire runs 0.15 mm off the plate's face: the cut plane
        self.head_x = self.PC[0] - 150.0
        self.set_head(self.head_x)
        # sparks: points along the wire where it is inside a bar
        sc.add("edm sparks", pv.PolyData(np.zeros((1, 3))), (1.0, 0.62, 0.15), "edm_spark", style="points",
               point_size=5.0, render_points_as_spheres=True, ambient=1.0, diffuse=0.0)
        sc.parent["edm_spark"] = body
        sc.alpha["edm sparks"] = 0.0

    def set_head(self, x):
        self.head_x = x
        self.sc.gmat["edm_head"] = T((x, self.wire_y, 0))

    def world(self, p):
        return (self.sc.world(f"{self.rig.prefix}body") @ np.r_[p, 1.0])[:3]

    def local(self, pw):
        Wm = self.sc.world(f"{self.rig.prefix}body")
        return (np.linalg.inv(Wm) @ np.r_[pw, 1.0])[:3]


# ------------------------------------------------------------------------------------------------- MiR250
class Mir:
    def __init__(self, sc):
        self.sc = sc
        for name, (mesh, col) in P.mir250().items():
            kw = dict(ambient=0.8) if "light" in name else {}
            sc.add(f"amr/{name}", mesh, col, "amr", **kw)
        top = P.MIR["H"] + P.CAB_H
        self.top = top
        for name, (mesh, col) in M.mir_fixtures(top).items():
            sc.add(f"amr/{name}", mesh, col, "amr")
        self.x = 1400.0
        self.set(self.x)
        self.rb = RB.Robot(sc, A.ROBOT, "amr", T((*A.ARM_LOCAL, P.AMR_TOP)), q0=A.PARK_DEG)

    def set(self, x):
        self.x = x
        self.sc.gmat["amr"] = T((x, MIR_Y, 0))

    def drive(self, x1):
        x0 = self.x

        def up(u):
            self.set(x0 + (x1 - x0) * u)
            if self.rb.held is not None:
                self.rb.set()
        return up

    def secs(self, x1):
        # plus 0.8 s for speeding up and slowing down: faster than MiR's 0.3 m/s^2 allows (see the notes)
        return max(1.2, abs(x1 - self.x) / MIR_SPEED + 0.8)

    def world(self, p):
        return (self.sc.world("amr") @ np.r_[p, 1.0])[:3]


# ================================================================================================= poses
def branch_q(rb, Tw, Tw_ref):
    """The IK solution for the tool pose Tw in the branch of the first clear solution for Tw_ref (collide.py), so that
    a straight line from one to the other stays in a branch that is clear at its end: the branch nearest the arm's
    current joints may reach Tw but put the forearm through the machine at Tw_ref."""
    import collide
    chk = rb.checker()
    Wd = chk.snapshot()
    Tb = np.linalg.inv(rb.sc.world(rb.root)) @ Tw_ref
    for q in collide.ik_all(rb.model, Tb, rb.q):
        if not chk.collisions(q, rb.close, Wd, chk.touching(q, rb.close, Wd)):
            return rb.solve(Tw, seed=q)
    return rb.solve(Tw)


def tilt(p, toward=(0.0, 1.0), down=TILT, spin=0.0):
    """Gripper pointing along `toward` (xy) and `down` degrees below level; fingers close along world x (spin 0)."""
    c, s = math.cos(math.radians(down)), math.sin(math.radians(down))
    return P.tcp_frame(np.asarray(p, float), (toward[0] * c, toward[1] * c, -s), spin)


def save_still(sc, name):
    """The current view with its text, as a PNG in out/ (not in a preview)."""
    if PREVIEW or CLEAN or scene.AUDIT:
        return
    base = sc.render_base()
    anchors = [sc.project(xyz) for _, xyz, _, _ in sc.labels]
    sc.overlay(Image.fromarray(base), 1.0, anchors).convert("RGB").save(OUT / name, optimize=True)


def held_point(sc, group, local):
    return (sc.world(group) @ np.r_[local, 1.0])[:3]


# ================================================================================================= the movie
def movie():
    sc, L, rigs, W, E, amr = build()
    rb = amr.rb
    edm, ins = rigs["wire_edm"], rigs["instron_floor"]
    PARK = np.radians(A.PARK_DEG)
    n = 6

    # key points in the world
    aco_bp = W.world(W.bp())
    aco_x = aco_bp[0] - 146.0                 # the MiR's spot at the Aconity: clear of the open door, on its left
    edm_pc = E.world(E.PC)
    edm_x = edm_pc[0]
    ins_axis = (sc.world(f"{ins.prefix}body") @ np.r_[0, 0, 700.0, 1.0])[:3]
    ins_x = ins_axis[0]

    CAM_LINE = [(aco_bp[0] + 2600, -9800, 4300), (aco_bp[0] + 2600, -1100, 900), (0, 0, 1)]
    CAM_ACO = [tuple(aco_bp + (-1700, -2300, 1500)), tuple(aco_bp + (100, -520, -120)), (0, 0, 1)]
    CAM_ACO_IN = [tuple(aco_bp + (-1250, -900, 850)), tuple(aco_bp + (30, -120, 10)), (0, 0, 1)]
    CAM_DRIVE = list(CAM_LINE)
    CAM_EDM = [tuple(edm_pc + (-1300, -1900, 900)), tuple(edm_pc + (60, -260, -40)), (0, 0, 1)]
    CAM_CUT = [tuple(edm_pc + (330, -560, 180)), tuple(edm_pc + (-15, -40, -5)), (0, 0, 1)]
    CAM_INS = [tuple(ins_axis + (-1500, -1750, 900)), tuple(ins_axis + (0, -200, 120)), (0, 0, 1)]
    CAM_GRIP = [tuple(ins_axis + (-520, -760, 260)), tuple(ins_axis + (0, -30, 40)), (0, 0, 1)]

    status(sc, Arm="UR10e on MiR250, parked", Plate="in the Aconity MIDI", Bar="", EDM="", Instron="")
    sc.cam = list(CAM_LINE)
    lbl_line = [("Aconity MIDI metal printer", (line.LINE["aconity"], line.Y_FACE + 300, 2400), (0.22, 0.20)),
                ("Instron 68FM-100, 100 kN", (line.LINE["instron_floor"], line.Y_FACE + 300, 2300), (0.46, 0.14)),
                ("FANUC ROBOCUT wire EDM", (line.LINE["wire_edm"], line.Y_FACE + 300, 2000), (0.80, 0.20)),
                ("UR10e on a MiR250", tuple(amr.world((0, 0, 1300))), (0.10, 0.45))]
    sc.step(f"1/{n}", "An example run on the alloy line: a build plate from the Aconity MIDI, through a depowdering "
            "box, to the wire EDM, which cuts the tensile bars off it, then one bar, rinsed and dried, to the Instron. "
            "The UR10e rides its MiR250 along the fronts.", 2.6, None, hold=1.6, labels=lbl_line)

    # ------------------------------------------------------------------ 1. the print
    cap = "The print is done: four ASTM E8 subsize tensile bars, 100 mm long and 6 mm thick, printed flat in " \
          "AlSi10Mg on a 170 mm plate (DAL PR #169's build at Utah), and a handling lug for the gripper. They are " \
          "still buried in the powder. The chamber is drawn see-through."
    status(sc, Plate="in the build cylinder, under powder")
    sc.step(f"1/{n}", cap, 3.2, W.ghost(1.0), hold=0.3, cam_to=CAM_ACO,
            labels=[("process chamber", tuple(W.world(M.build_point() + (250, 0, 250))), (0.20, 0.24)),
                    ("build cylinder, 170 mm", tuple(aco_bp + (0, 0, -60)), (0.16, 0.62))])

    def sem_in(u):
        sc.sem_a = u
    sc.step(f"1/{n}", cap, 1.0, sem_in, hold=3.4)

    # ------------------------------------------------------------------ 2. door, the suction lance, platform up
    D = sc.dbox
    box_c = D.world((M.DBOX["chuck_x"], M.DBOX["axis_y"], M.DBOX["chuck_top"]))
    mid = (aco_bp + box_c) / 2
    lance_c = D.lworld(M.HOLSTER)
    CAM_DEP = [tuple(lance_c + (700, -2500, 1250)), tuple(lance_c + (-250, -150, -280)), (0, 0, 1)]
    CAM_BOX = [tuple(box_c + (950, -1750, 850)), tuple(box_c + (-60, -60, -90)), (0, 0, 1)]
    p_hold = D.lworld(M.HOLSTER)
    box_x = box_c[0] - 78.0 - 146.0             # the MiR's spot at the box, as at the printer: the lug 146 mm right
    l_dir = np.array([0, math.cos(math.radians(LANCE_DOWN)), -math.sin(math.radians(LANCE_DOWN))])

    def lance_at(tip):
        return tilt(np.asarray(tip, float) - l_dir * LANCE_TIP, down=LANCE_DOWN)
    cap = "The chamber door opens and the MiR250 rolls up. The MIDI has no automatic depowdering, so the arm takes " \
          "a suction lance off its post beside the chamber. A pipe along the floor takes what it picks up to the " \
          "depowdering box's separator, in the gap between the printer and the Instron."

    def sem_out(u):
        sc.sem_a = 1.0 - u
    status(sc, Arm="driving to the Aconity", Plate="under powder")
    sc.step(f"2/{n}", cap, max(2.2, amr.secs(aco_x)), RB.both(W.door(1.0), amr.drive(aco_x), sem_out), hold=0.3,
            cam_to=CAM_DEP, labels=[("depowdering box", tuple(D.world((0, 0, M.DBOX["H"] + 60))), (0.80, 0.16)),
                                    ("suction lance", tuple(p_hold + (0, -30, 60)), (0.62, 0.30))])
    sc.sem_a = 0.0
    status(sc, Arm="taking the suction lance")
    sc.step(f"2/{n}", cap, 1.6, D.with_hose(RB.both(rb.joint_to(Tw=A.down(p_hold + (0, 0, 130), spin=0.0)),
                                                    rb.grip_to(0.0))), hold=0.05)
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(A.down(p_hold, spin=0.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_LUG), hold=0.05)
    rb.grasp("lance")
    sc.step(f"2/{n}", cap, 0.5, D.with_hose(rb.line_to(A.down(p_hold + (0, 0, 14), spin=0.0))), hold=0.02)
    sc.step(f"2/{n}", cap, 0.7, D.with_hose(rb.line_to(A.down(p_hold + (0, -120, 14), spin=0.0))), hold=0.02)
    sc.step(f"2/{n}", cap, 0.9, D.with_hose(rb.line_to(A.down(p_hold + (0, -300, 260), spin=0.0))), hold=0.02)
    # into the chamber, 25 deg down, the nozzle just over the chamber floor
    # the far row first, while the nozzle is lowest, so the gripper stays under the chamber's roof; the two middle
    # rows stop short of the lug, and the nozzle rides the build as it rises: its mouth (r 22 mm, 20 mm under its
    # centre at 25 deg) clear of the powder at the floor, then of the bars once they are out
    rows = (50.0, 15.0, -20.0, -55.0)
    path = []
    for i, dy in enumerate(rows):
        x_lo = -72.0 if abs(dy) > 40 else -36.0
        xs = (x_lo, 72.0) if i % 2 == 0 else (72.0, x_lo)
        path += [aco_bp + (xs[0], dy, 0.0), aco_bp + (xs[1], dy, 0.0)]
    path = np.array(path)
    seg = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    NOZ = 24.0                                    # the nozzle's centre over the powder, mm

    def noz_z(z_piston):
        """The nozzle's centre height (world) with the piston's top at z_piston: over the powder or the bars."""
        bars_top = z_piston + M.PLATE["t"] + M.E8_SUB["T"]
        return max(W.floor + NOZ, bars_top + NOZ + 2.0)
    path[:, 2] = noz_z(W.piston_top)
    entry = path[0] - l_dir * 150
    cap = "It vacuums the plate as the platform rises a step at a time, the nozzle sweeping the build cylinder at " \
          "floor level: what a person does with a brush and an ATEX vacuum. The powder goes to the box's separator, " \
          "to be sieved and reused."
    status(sc, Arm="vacuuming the build", Plate="rising out of the powder")
    sc.step(f"2/{n}", cap, 1.8, D.with_hose(rb.joint_to(Tw=lance_at(entry))), hold=0.05, cam_to=CAM_ACO_IN)
    sc.step(f"2/{n}", cap, 1.0, D.with_hose(rb.line_to(lance_at(path[0]))), hold=0.05)
    lift_to = W.floor + 18.0 - M.PLATE["t"]        # the plate's top 18 mm over the chamber floor
    z_p0 = W.piston_top
    ring = np.array([(math.cos(a), math.sin(a), 0.0) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)])

    def sweep(u):
        s = u * seg[-1]
        k = min(int(np.searchsorted(seg, s, side="right")) - 1, len(path) - 2)
        f = (s - seg[k]) / max(seg[k + 1] - seg[k], 1e-6)
        tip = path[k] + (path[k + 1] - path[k]) * f
        zp = z_p0 + (lift_to - z_p0) * u
        tip[2] = noz_z(zp)
        rb.set(rb.solve(lance_at(tip), rb.q))
        W.set_piston(zp)
        D.update_hose()
        ph = (u * 22.0 + np.arange(len(ring)) * 0.37) % 1.0
        pts = tip + ring * (34.0 * (1 - ph))[:, None] + np.c_[np.zeros((len(ring), 2)), 6.0 * (1 - ph)]
        sc.set_mesh("lance suck", pv.PolyData(pts))
        sc.alpha["lance suck"] = 1.0 if 0.02 < u < 0.98 else 0.0
    sc.step(f"2/{n}", cap, 6.4, sweep, hold=0.1,
            labels=[("bars and lug, as built", tuple(W.world(M.build_point(W.floor + 18) + (0, -60, 10))),
                     (0.18, 0.36))])
    sc.sem_a = 0.0
    sc.alpha["lance suck"] = 0.0
    sc.alpha["plate residue"] = 1.0
    cap = "The lance goes back on the box. What it leaves is loose grains round the bars and the lug."
    status(sc, Arm="putting the lance back", Plate="out of the powder; grains left on it")
    sc.step(f"2/{n}", cap, 0.9, D.with_hose(rb.line_to(lance_at(path[-1] + (0, 0, noz_z(lift_to) - path[-1][2])
                                                             - l_dir * 200))), hold=0.05)
    sc.step(f"2/{n}", cap, 1.8, D.with_hose(rb.joint_to(Tw=A.down(p_hold + (0, -300, 260), spin=0.0))), hold=0.02,
            cam_to=CAM_DEP)
    sc.step(f"2/{n}", cap, 0.9, D.with_hose(rb.line_to(A.down(p_hold + (0, -120, 14), spin=0.0))), hold=0.02)
    sc.step(f"2/{n}", cap, 0.7, D.with_hose(rb.line_to(A.down(p_hold + (0, 0, 14), spin=0.0))), hold=0.02)
    sc.step(f"2/{n}", cap, 0.4, D.with_hose(rb.line_to(A.down(p_hold, spin=0.0))), hold=0.02)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.02)
    rb.release("dbox")
    sc.step(f"2/{n}", cap, 0.6, rb.line_to(A.down(p_hold + (0, 0, 130), spin=0.0)), hold=0.05)

    # ------------------------------------------------------------------ 3. the plate through the depowdering box
    cap = "The platform's clamp lets go (a zero-point clamp: Aconity's platform takes a screwed plate, so this is an " \
          "assumption). The chamber is 280 mm tall inside, too low for the gripper pointing down, so it takes the " \
          "lug pointing 30° down and lifts the plate out."
    p_g = held_point(sc, "plate", (-78.0, 0, 28.0))   # the grasp point: the lug's centre line, 28 mm up
    a_dir = np.array([0, math.cos(math.radians(TILT)), -math.sin(math.radians(TILT))])
    status(sc, Arm="taking the plate")
    # in the way the plate comes out, fingers over the lug, then down onto it: backed off along its own axis, 30 deg
    # down, the gripper's wrist would be up in the chamber's roof
    p_out = p_g + (0, -470, 52)
    sc.step(f"3/{n}", cap, 1.8, RB.both(rb.joint_to(Tw=tilt(p_out)), rb.grip_to(0.0)), hold=0.05,
            cam_to=CAM_ACO_IN, labels=[("handling lug", tuple(p_g + (0, 0, 20)), (0.20, 0.30))])
    sc.step(f"3/{n}", cap, 1.2, rb.line_to(tilt(p_g + (0, -40, 32))), hold=0.05)
    sc.step(f"3/{n}", cap, 0.6, rb.line_to(tilt(p_g)), hold=0.05)
    sc.step(f"3/{n}", cap, 0.5, rb.grip_to(GRIP_LUG), hold=0.05)
    status(sc, Plate="clamp released; in the gripper")
    rb.grasp("plate")
    sc.step(f"3/{n}", cap, 0.8, rb.line_to(tilt(p_g + (0, 0, 32))), hold=0.05)
    sc.step(f"3/{n}", cap, 1.8, rb.line_to(tilt(p_out)), hold=0.05, labels=[])
    # tucked in over the MiR for the drive: held out of the chamber, the plate is still over the printer's cabinet,
    # in line with the lance's post and the box
    p_carry = amr.world((-330.0, 300.0, 0.0)) + (0, 0, 1250.0)
    sc.step(f"3/{n}", cap, 1.4, rb.joint_to(Tw=tilt(p_carry)), hold=0.05)
    p_box = D.seat_tcp()
    cap = "Into the depowdering box beside the printer: the door slides up and the arm sets the plate's stud in a " \
          "zero-point chuck on a turning shaft. The box is our design, on the principle of Solukon's SFM-AT200, the " \
          "smallest made for this (plates to 300 × 300 × 230 mm, 60 kg), which would need about a metre more of line."
    status(sc, Arm="loading the depowdering box")
    sc.step(f"3/{n}", cap, amr.secs(box_x), RB.both(amr.drive(box_x), D.door(1.0), W.door(0.0)), hold=0.05,
            cam_to=CAM_BOX)
    # the plate half in the door, the arm in the branch that reaches the chuck with its forearm clear of the box's frame
    p_mid = p_box + (0, -200, 100)
    sc.step(f"3/{n}", cap, 1.6, rb.joint_to(q1=branch_q(rb, tilt(p_mid), tilt(p_box))), hold=0.05,
            labels=[("zero-point chuck", tuple(box_c + (0, 0, -30)), (0.80, 0.40))])
    sc.step(f"3/{n}", cap, 1.2, rb.line_to(tilt(p_box + (0, 0, 14))), hold=0.05)
    sc.step(f"3/{n}", cap, 0.5, rb.line_to(tilt(p_box)), hold=0.05)
    sc.step(f"3/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("dbox_rotor")
    status(sc, Plate="in the depowdering box")
    sc.step(f"3/{n}", cap, 0.9, rb.line_to(tilt(p_box - a_dir * 260)), hold=0.05, labels=[])
    sc.step(f"3/{n}", cap, 1.2, rb.joint_to(PARK), hold=0.05)
    cap = "The door shuts and the box fills with argon. The shaft turns the plate over and back on a set path " \
          "while a vibrator on it shakes the grains loose; they fall through the hopper into a closed bottle."
    status(sc, Arm="waiting", Plate="turned and shaken, under argon")
    sc.step(f"3/{n}", cap, 1.2, RB.both(D.door(0.0), D.ghost(1.0)), hold=0.1,
            labels=[("vibrator", tuple(D.world((M.DBOX["chuck_x"] + 125, M.DBOX["axis_y"], M.DBOX["axis_z"]))),
                     (0.78, 0.30)),
                    ("hopper to a closed bottle", tuple(D.world((M.DBOX["chuck_x"], M.DBOX["axis_y"],
                                                                 M.DBOX["base"] + 90))), (0.78, 0.66))])
    keys = ([0.0, 0.22, 0.44, 0.70, 1.0], [0.0, 150.0, -150.0, 180.0, 0.0])
    gone = {"res": 1.0}
    rng = np.random.default_rng(11)
    drops = np.c_[rng.uniform(-60, 60, 40), rng.uniform(-40, 40, 40), rng.uniform(0, 1, 40)]
    pz0, pz1 = M.DBOX["axis_z"] - 60.0, M.DBOX["base"] + 60.0

    def cycle(u):
        ang = float(np.interp(u, *keys))
        D.set_angle(ang, 1.5 * math.sin(u * 2 * math.pi * 55.0))
        if abs(ang) > 95:
            gone["res"] = max(0.0, min(gone["res"], 1.0 - (abs(ang) - 95.0) / 45.0))
        sc.alpha["plate residue"] = gone["res"]
        on = 0.12 < u < 0.92 and abs(ang) > 100
        if on:
            ph = (drops[:, 2] + u * 9.0) % 1.0
            pts = np.c_[M.DBOX["chuck_x"] + drops[:, 0], M.DBOX["axis_y"] + drops[:, 1], pz0 + (pz1 - pz0) * ph ** 1.6]
            sc.set_mesh("dbox fall", pv.PolyData(pts))
        sc.alpha["dbox fall"] = 1.0 if on else 0.0
    sc.step(f"3/{n}", cap, 7.0, cycle, hold=0.2)
    D.set_angle(0.0)
    sc.alpha["dbox fall"] = 0.0
    sc.alpha["plate residue"] = 0.0
    status(sc, Plate="depowdered", Arm="taking the plate")
    cap = "Clean. The door opens and the arm takes the plate out by its lug."
    sc.step(f"3/{n}", cap, 1.2, RB.both(D.ghost(0.0), D.door(1.0)), hold=0.05, labels=[])
    sc.step(f"3/{n}", cap, 1.3, RB.both(rb.joint_to(Tw=tilt(p_box - a_dir * 260)), rb.grip_to(0.0)), hold=0.02)
    sc.step(f"3/{n}", cap, 0.7, rb.line_to(tilt(p_box - a_dir * 60)), hold=0.02)
    sc.step(f"3/{n}", cap, 0.5, rb.line_to(tilt(p_box)), hold=0.02)
    sc.step(f"3/{n}", cap, 0.4, rb.grip_to(GRIP_LUG), hold=0.02)
    rb.grasp("plate")
    sc.step(f"3/{n}", cap, 0.5, rb.line_to(tilt(p_box + (0, 0, 14))), hold=0.02)
    sc.step(f"3/{n}", cap, 1.0, rb.line_to(tilt(p_mid)), hold=0.05)
    # onto the carrier on the MiR: turned half a turn, so the lug ends up on the plate's right
    c_top = amr.world(M.carrier_top(amr.top))
    p_c = c_top + (78.0, 0, M.PLATE["t"] + 28.0)
    cdir = (0.0, -1.0)
    b_dir = np.array([0, -math.cos(math.radians(TILT)), -math.sin(math.radians(TILT))])
    cap = "It sets the plate on a carrier on the MiR250, half a turn round, so the lug ends up on the plate's right. " \
          "Plate and parts weigh about 1 kg, against the UR10e's 12.5 kg."
    sc.step(f"3/{n}", cap, 2.2, rb.joint_to(Tw=tilt(p_c + (0, 0, 120), toward=cdir, spin=180.0)),
            hold=0.05, cam_to=CAM_ACO)
    sc.step(f"3/{n}", cap, 1.0, rb.line_to(tilt(p_c, toward=cdir, spin=180.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 0.5, rb.grip_to(0.0), hold=0.05)
    rb.release("amr")
    status(sc, Plate="on the MiR's carrier")
    sc.step(f"3/{n}", cap, 0.8, rb.line_to(tilt(p_c - b_dir * 110, toward=cdir, spin=180.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 1.4, RB.both(rb.joint_to(PARK), D.door(0.0), W.door(0.0), W.ghost(0.0)), hold=0.1)
    status(sc, Arm="parked")

    # ------------------------------------------------------------------ 4. to the wire EDM, plate in
    cap = f"To the FANUC ROBOCUT wire EDM, {(edm_x - box_x) / 1000:.1f} m along the line, at up to " \
          f"{MIR_SPEED / 1000:.1f} m/s (the MiR250 does 2.0)."
    status(sc, Arm="driving to the wire EDM")
    sc.step(f"4/{n}", cap, amr.secs(edm_x), amr.drive(edm_x), hold=0.2, cam_to=CAM_DRIVE)
    cap = "The tank is drained and its yellow door drops. The arm takes the plate by the lug again, from above, " \
          "turns it on edge and pushes it onto a zero-point receiver on an angle plate on the table, bars to the front."
    status(sc, Arm="loading the plate", EDM="tank drained, door down")
    sc.step(f"4/{n}", cap, 1.8, edm.move({"door": (0.0, 1.0), "~body": (0.0, 0.55)}), hold=0.1, cam_to=CAM_EDM,
            labels=[("work tank", tuple(E.world((-430, -1200, 1150))), (0.18, 0.28))])
    p_l = held_point(sc, "plate", (-78.0, 0, 28.0))
    sc.step(f"4/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=A.down(p_l + (0, 0, 120), spin=0.0)), rb.grip_to(0.0)),
            hold=0.05, labels=[])
    sc.step(f"4/{n}", cap, 0.9, rb.line_to(A.down(p_l, spin=0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.5, rb.grip_to(GRIP_LUG), hold=0.05)
    rb.grasp("plate")
    status(sc, Plate="in the gripper")
    sc.step(f"4/{n}", cap, 0.9, rb.line_to(A.down(p_l + (0, 0, 160), spin=0.0)), hold=0.05)
    # the TCP at the lug once the plate is on the receiver: lug centre 78 mm right of the face centre, 28 mm out
    t_place = E.world(E.PC + (78.0, -28.0, 0.0))
    t_pre = t_place + (0, -45.0, 0)
    t_out = t_place + (0, -250.0, 80.0)
    sc.step(f"4/{n}", cap, 2.2, rb.joint_to(Tw=A.level(t_out, spin=0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 1.4, rb.line_to(A.level(t_pre, spin=0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.6, rb.line_to(A.level(t_place, spin=0.0)), hold=0.1,
            labels=[("zero-point receiver on an angle plate", tuple(E.world(E.PC + (-60, 30, 110))), (0.16, 0.30))])
    status(sc, Plate="clamped in the EDM, on edge")
    sc.step(f"4/{n}", cap, 0.5, rb.grip_to(0.0), hold=0.05)
    rb.release("edm_fix")
    sc.step(f"4/{n}", cap, 1.2, rb.line_to(A.level(t_out, spin=0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 1.4, rb.joint_to(PARK), hold=0.05, labels=[])
    cap = "Door up; the tank fills with deionised water, the dielectric. The plate is cut under water."
    status(sc, Arm="parked", EDM="tank filling")
    sc.step(f"4/{n}", cap, 1.4, edm.move({"door": (1.0, 0.0), "~door": (0.0, 0.6)}), hold=0.05)
    sc.step(f"4/{n}", cap, 1.6, edm.move({"glow": (0.0, 0.55)}), hold=0.3)

    # ------------------------------------------------------------------ 5. the cut
    cap = "The cut, with the machine drawn see-through: the brass wire (0.25 mm; FANUC takes 0.10-0.30 mm) runs " \
          "between its upper and lower guides, 0.15 mm off the plate, and sparks its way through the base of each bar."
    status(sc, EDM="cutting")
    sc.step(f"5/{n}", cap, 2.2, RB.both(edm.move({"~body": (0.55, 1.0), "~door": (0.6, 1.0 / 0.82)}),
                                        lambda u: E.set_head(E.PC[0] - 150 + 55 * u)),
            hold=0.1, cam_to=CAM_CUT,
            labels=[("wire, drawn thicker", tuple(E.world((E.PC[0] - 95, E.wire_y, E.Z_HI - 25))), (0.20, 0.30)),
                    ("upper guide", tuple(E.world((E.PC[0] - 95, E.wire_y, E.Z_HI + 60))), (0.20, 0.16))])
    bars = [f"bar{k}" for k in range(4)]
    bar_x = {g: E.local(held_point(sc, g, (0, 0, 3.0)))[0] for g in bars}
    bar_z = {g: sorted(E.local(held_point(sc, g, (0, y, 3.0)))[2] for y in (-50.0, 50.0)) for g in bars}
    x_start, x_end = E.PC[0] - 95.0, E.PC[0] + 58.0
    dropped = set()
    total = sum(M.bar_mesh().volume / M.E8_SUB["T"] for _ in bars)

    def cut(u):
        x = x_start + (x_end - x_start) * u
        E.set_head(x)
        pts = []
        done = 0.0
        for g in bars:
            bx = bar_x[g]
            if bx - 5.0 < x < bx + 5.0:          # the wire is in this bar's grip ends (10 mm wide)
                z0, z1 = bar_z[g]
                zz = np.linspace(z0, z1, 26)
                if abs(x - bx) > 3.0:            # beside the reduced section, only the grip ends are cut
                    zz = zz[(zz < z0 + 34) | (zz > z1 - 34)]
                jit = np.sin(np.arange(len(zz)) * 2.7 + u * 90.0) * 1.2
                # drawn on the bar's front face so they show: the real gap is inside the 0.3 mm kerf
                pts += [(x + j, E.wire_y - M.E8_SUB["T"] - 1.0, z) for j, z in zip(jit, zz)]
            if x >= bx + 5.0 and g not in dropped:
                dropped.add(g)
                rb.reparent(g, None)
            if g in dropped:
                done += 1
            elif x > bx - 5.0:
                done += (x - (bx - 5.0)) / 10.0
        for g in dropped:                        # each cut bar drops 14 mm onto the catch shelf
            base = sc.gmat.setdefault(f"_{g}_cut", sc.gmat[g].copy())
            sc.gmat[g] = T((0, 0, -14.0)) @ base
        if pts:
            sc.set_mesh("edm sparks", pv.PolyData(np.array(pts)))
            sc.alpha["edm sparks"] = 1.0
        else:
            sc.alpha["edm sparks"] = 0.0
        status(sc, EDM=f"cutting: {done:.1f} of 4 bars")
    def cut_part(u0, u1):
        def up(u):
            cut(u0 + (u1 - u0) * u)
        return up
    lbl_cut = [("bars drop onto a catch shelf", tuple(E.world((E.PC[0] - 40, E.PC[1] - 8, E.PC[2] - 70))),
                (0.18, 0.66))]
    sc.step(f"5/{n}", cap, 3.4, cut_part(0.0, 0.36), hold=0.0, labels=lbl_cut)
    save_still(sc, f"{NAME}_cut.png")
    sc.step(f"5/{n}", cap, 5.6, cut_part(0.36, 1.0), hold=0.2, labels=lbl_cut)
    sc.alpha["edm sparks"] = 0.0
    area = total
    cap = f"Four cuts, {area:.0f} mm² in all. FANUC gives no cutting rate for aluminium; at the 300 mm²/min GF " \
          "quotes as the maximum of its CUT AM 500, made for this job, it would take at least 11 minutes. The tank " \
          "drains and the door drops."
    status(sc, EDM="cut; draining")
    sc.step(f"5/{n}", cap, 1.6, edm.move({"glow": (0.55, 0.0)}), hold=0.1)
    sc.step(f"5/{n}", cap, 1.4, RB.both(edm.move({"door": (0.0, 1.0), "~body": (1.0, 0.55), "~door": (1.0 / 0.82, 0.0)}),
                                        lambda u: E.set_head(x_end + (E.PC[0] + 95 - x_end) * u)),
            hold=0.1, cam_to=CAM_EDM, labels=[])
    status(sc, EDM="door down")
    # the arm takes the tested bar by its top end
    g = f"bar{TEST}"
    end_up = -50.0 if held_point(sc, g, (0, -50.0, 3.0))[2] > held_point(sc, g, (0, 50.0, 3.0))[2] else 50.0
    top_local = (0.0, end_up, 3.0)
    p_top = held_point(sc, g, top_local)
    p_b = p_top + (0, 0, -13.0)
    cap = "The arm takes the first bar off the shelf by its end, the gripper opened just enough to fit between the " \
          "bars. Wire-cut parts come out wet with deionised water."
    status(sc, Arm="taking a bar", Bar="bar 1 of 4, wet")
    sc.step(f"5/{n}", cap, 1.8, RB.both(rb.joint_to(Tw=A.down(p_b + (0, -120, 140), spin=0.0)),
                                        rb.grip_to(GRIP_NEAR)), hold=0.05)
    sc.step(f"5/{n}", cap, 0.8, rb.line_to(A.down(p_b + (0, 0, 60), spin=0.0)), hold=0.05)
    sc.step(f"5/{n}", cap, 0.7, rb.line_to(A.down(p_b, spin=0.0)), hold=0.05)
    sc.step(f"5/{n}", cap, 0.4, rb.grip_to(GRIP_BAR), hold=0.05)
    rb.grasp(g)
    sc.step(f"5/{n}", cap, 0.8, rb.line_to(A.down(p_b + (0, 0, 70), spin=0.0)), hold=0.05)
    sc.step(f"5/{n}", cap, 1.0, rb.line_to(A.down(p_b + (0, -420, 120), spin=0.0)), hold=0.05)
    bot_local = (0.0, -end_up, 3.0)
    bottom_w = held_point(sc, g, bot_local)
    d_tcp = rb.tcp_world()[:3, 3] - bottom_w            # TCP relative to the bar's lower end (gripper pointing down)
    # rinse and dry: dipped in the cup's isopropanol, pulled out slowly through its air knife
    cup_w = (sc.world("rinse") @ np.r_[0.0, 0.0, M.RINSE["z0"] + 34.0, 1.0])[:3]
    # as deep as the fingers allow: their tips go into the cup, inside the air knife, and the fingers stop over it
    rim = (sc.world("rinse") @ np.r_[0.0, 0.0, M.RINSE["z1"], 1.0])[:3]
    p_r = np.array([rim[0] + d_tcp[0], rim[1] + d_tcp[1], rim[2] - 1.0])
    CAM_RINSE = [tuple(cup_w + (-520, -760, 380)), tuple(cup_w + (60, 0, 60)), (0, 0, 1)]
    cap = "A rinse and dry: the arm dips the bar in a cup of isopropanol in front of the EDM and pulls it out slowly " \
          "through the air knife on the cup's rim (our design, assumed)."
    status(sc, Arm="rinsing the bar", Bar="bar 1 of 4, rinsing")
    sc.step(f"5/{n}", cap, 1.6, rb.joint_to(Tw=A.down(p_r + (0, 0, 190), spin=0.0)), hold=0.05, cam_to=CAM_RINSE,
            labels=[("isopropanol cup, air knife on its rim", tuple(cup_w + (0, 0, 190)), (0.20, 0.30))])
    sc.step(f"5/{n}", cap, 1.0, rb.line_to(A.down(p_r, spin=0.0)), hold=0.6)
    sc.step(f"5/{n}", cap, 2.0, rb.line_to(A.down(p_r + (0, 0, 190), spin=0.0)), hold=0.1)
    status(sc, Bar="bar 1 of 4, rinsed and dry")
    # into the holder on the MiR
    seat = amr.world(M.holder_seat(amr.top))
    p_h = seat + d_tcp
    sc.step(f"5/{n}", cap, 1.8, rb.joint_to(Tw=A.down(p_h + (0, 0, 90), spin=0.0)), hold=0.05)
    sc.step(f"5/{n}", cap, 0.8, rb.line_to(A.down(p_h, spin=0.0)), hold=0.05)
    sc.step(f"5/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("amr")
    status(sc, Bar="in the holder on the MiR")
    sc.step(f"5/{n}", cap, 0.7, rb.line_to(A.down(p_h + (0, 0, 90), spin=0.0)), hold=0.05)
    sc.step(f"5/{n}", cap, 1.2, RB.both(rb.joint_to(PARK), edm.move({"door": (1.0, 0.0), "~body": (0.55, 0.0)})),
            hold=0.1)
    status(sc, Arm="parked", EDM="three bars wait in the tank")

    # ------------------------------------------------------------------ 6. the tensile test
    peak = SS["uts"] * AREA / 1000
    cap = f"To the Instron. The bar's 6 × 6 mm section at {SS['uts']:.0f} MPa is a {peak:.1f} kN pull: the 68SC-2 " \
          f"stops at 2 kN, so it goes to the 68FM-100 (100 kN). The crosshead rises out of the arm's way."
    status(sc, Arm="driving to the 68FM-100")
    sc.step(f"6/{n}", cap, amr.secs(ins_x), RB.both(amr.drive(ins_x), ins.move({"crosshead": (0.0, 1.0)})), hold=0.2,
            cam_to=CAM_INS,
            labels=[("wedge grips", tuple(ins_axis + (0, -40, 0)), (0.18, 0.62)),
                    ("Instron 68SC-2: 2 kN", (line.LINE["instron_small"], line.Y_FACE + 300, 1450), (0.80, 0.20))])
    # pick from the holder, insert in the lower grip: its jaws start at z 700 (instruments.INSTRON_FM), 30 mm deep
    p_hold = amr.world(M.holder_seat(amr.top)) + d_tcp
    status(sc, Arm="loading the bar")
    sc.step(f"6/{n}", cap, 1.6, rb.joint_to(Tw=A.down(p_hold + (0, 0, 90), spin=0.0)), hold=0.05, labels=[])
    sc.step(f"6/{n}", cap, 0.7, rb.line_to(A.down(p_hold, spin=0.0)), hold=0.05)
    sc.step(f"6/{n}", cap, 0.4, rb.grip_to(GRIP_BAR), hold=0.05)
    rb.grasp(g)
    sc.step(f"6/{n}", cap, 0.7, rb.line_to(A.down(p_hold + (0, 0, 90), spin=0.0)), hold=0.05)
    bottom_target = ins_axis + (0, 0, -30.0)               # the bar's lower 30 mm in the lower grip
    p_i = bottom_target + d_tcp
    cap = "The arm lowers the bar's end into the lower wedge grip, which closes on it (Instron sells 100 kN wedge " \
          "grips with automatic hydraulic actuation and front loading for flat specimens). The arm lets go and backs off."
    sc.step(f"6/{n}", cap, 1.8, rb.joint_to(Tw=A.down(p_i + (0, 0, 80), spin=0.0)), hold=0.05, cam_to=CAM_GRIP)
    sc.step(f"6/{n}", cap, 1.0, rb.line_to(A.down(p_i, spin=0.0)), hold=0.1)
    status(sc, Instron="lower grip closed", Bar="in the grips")
    sc.step(f"6/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release(f"{ins.prefix}body")
    sc.step(f"6/{n}", cap, 0.7, rb.line_to(A.down(p_i + (0, 0, 60), spin=0.0)), hold=0.05)
    sc.step(f"6/{n}", cap, 1.3, rb.line_to(A.down(p_i + (0, -380, 120), spin=0.0)), hold=0.05)
    sc.step(f"6/{n}", cap, 1.2, rb.joint_to(PARK), hold=0.05)
    status(sc, Arm="parked")
    # the crosshead comes down until the upper grip takes the bar's top 30 mm: its jaws end at z 1070 at v = 0
    v_close = (ins_axis[2] + 40.0 - (1070.0 + (sc.world(f"{ins.prefix}body")[2, 3]))) / 160.0
    cap = "The crosshead comes down until the upper grip takes the bar's other end, 40 mm of it free between the jaws, " \
          "and the upper grip closes."
    sc.step(f"6/{n}", cap, 2.0, ins.move({"crosshead": (1.0, v_close)}), hold=0.3)
    status(sc, Instron="both grips closed")
    # the test
    cap = f"The test: the crosshead pulls at a constant rate and the load cell reads the force. The curve is not a " \
          f"measurement: it runs through AddUp's published as-built values ({SS['src']}). The bar breaks at about " \
          f"{SS['uts']:.0f} MPa, {SS['elong'] * 100:.0f} % strain, with little necking."
    hi_up = held_point(sc, g, (0, 25.0, 3.0))[2] > held_point(sc, g, (0, -25.0, 3.0))[2]
    gauge = M.E8_SUB["G"]

    def pull(u):
        sc.ss_u = u
        e, s = SS_PTS[int(round(u * (len(SS_PTS) - 1)))]
        status(sc, Instron=f"{s * AREA / 1000:5.1f} kN, extension {e * gauge:4.2f} mm")
        ins.move({"crosshead": (v_close, v_close + e * gauge * 1.6 / 160.0)})(1.0)
    sc.ss_u = 0.0
    sc.step(f"6/{n}", cap, 8.0, pull, hold=0.2, cam_to=CAM_GRIP)
    # fracture: the upper half goes with the crosshead
    sc.ss_broken = True
    rb.reparent(f"{g}_b", f"{ins.prefix}crosshead" if hi_up else f"{ins.prefix}body")
    if not hi_up:
        rb.reparent(g, f"{ins.prefix}crosshead")
    v1 = ins.v["crosshead"]
    status(sc, Instron=f"broke at {SS['uts'] * AREA / 1000:.1f} kN", Bar="broken, two halves")
    cap = "Broken. The crosshead backs off 20 mm to show the break; the halves go on to the SEM for fractography."
    sc.step(f"6/{n}", cap, 1.6, ins.move({"crosshead": (v1, v1 + 20.0 / 160.0)}), hold=1.4, still=True)
    sc.step(f"6/{n}", "Done: printed, depowdered, cut, rinsed and tested, every arm move a real one, and no step "
            "left to a person. The depowdering box and the rinse cup are new stations of our own design.", 3.0, None,
            hold=3.4, cam_to=CAM_LINE, labels=lbl_line[:3] + [("depowdering box", tuple(D.world((0, 0, 1700))),
                                                               (0.34, 0.30))])
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    info = sc.save()
    if not PREVIEW and not scene.AUDIT:
        meta_path = OUT / f"{NAME}.json"
        meta = json.loads(meta_path.read_text())
        meta.update(numbers=dict(specimen=M.E8_SUB, plate=M.PLATE, cut_area_mm2=round(area), peak_kN=round(peak, 1),
                                 stress_strain=SS, mir_speed_mm_s=MIR_SPEED),
                    data=dict(sem=dict(file="DAL figures/sem/AlSi10Mg_carbon_adhesive_SEM.png",
                                       taken="BYU Apreo SEM, 500x, 5 kV, 0.10 nA, ETD, 2 April 2026",
                                       by="Gage Erickson (byu-vcl#48, comment 4181040112)"),
                              curve="illustrative fit through published values, not measured"))
        meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return info


if __name__ == "__main__":
    if not SEM_LOCAL.exists() and SEM.exists():
        SEM_LOCAL.parent.mkdir(parents=True, exist_ok=True)
        Image.open(SEM).convert("L").save(SEM_LOCAL, optimize=True)
    print(movie(), flush=True)
