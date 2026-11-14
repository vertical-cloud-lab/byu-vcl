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

Round 8 (PR #318, 2026-11-05) re-stages the chapter, as the alloy route's chapter 5, in the whole lab as the set-up
movie leaves it (``build_lab()``, ``movie()``); ``build()`` above stays for chapter 3 (``alloy_print.py``), which
borrows it. See the comment above ``SPEC_ORDER`` and notes/alloy_workflow.md. ``CH5_FROM=6`` or ``7`` starts a
preview at the heat treatment or the Instron, from the state the earlier sections leave.
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
import instruments as I               # noqa: E402
import vlm as V                       # noqa: E402
import lab                            # noqa: E402
import line                           # noqa: E402
import props as P                     # noqa: E402
import robot as RB                    # noqa: E402
import tour                           # noqa: E402

TITLE = "Vertical cloud lab: from the metal printer to the tensile test"
NAME = __import__("os").environ.get("CH5_NAME", "alloy_workflow")   # CH5_NAME: a partial render under its own name
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
# round 11: each closure leaves 0.3 mm over the part (ur_arm.close_for): round 10's 0.88 squeezed the 12 mm lug and the
# tongs' handle by 0.17 mm and 0.79 the lid's 20 mm knob by 0.02, which the strict audit reads as 3-6 mm deep
GRIP_LUG = __import__("ur_arm").close_for(12.3)     # 2F-85 closure for the 12 mm lug
GRIP_BAR = __import__("ur_arm").close_for(10.3)     # for the bar's 10 mm grip end
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
    """The status table under the title (round 8: through the lab's own gauges, when the scene has a TwoLab)."""
    rows = dict(sc._rows) if hasattr(sc, "_rows") else {}
    rows.update(kv)
    sc._rows = rows
    sc.gauges = [(k, v) for k, v in rows.items() if v]
    L = getattr(sc, "_lab", None)
    if L is not None:
        L.extra_gauges = list(sc.gauges)
        L.show_gauges = True
        L.gauges()


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

    def __init__(self, sc, box_x=None, stand_x=None):
        self.sc = sc
        box_x = DBOX_X if box_x is None else box_x
        stand_x = LSTAND_X if stand_x is None else stand_x
        self.box_x, self.stand_x = box_x, stand_x
        sc.gmat["dbox"] = T((box_x, line.Y_FACE, 0))
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
        # round 9: three swing clamps on the rotor hold the plate down while it turns (alloy_models.CLAMPS)
        top = M.DBOX["chuck_top"]
        sc.add("dbox/rotor/clamp bodies", M.clamp_body(top), (0.30, 0.32, 0.36), "dbox_rotor", specular=0.3)
        self.names["rotor"].append("dbox/rotor/clamp bodies")
        for i in range(len(M.CLAMPS["angles"])):
            g = f"dbox_clamp{i}"
            sc.add(f"dbox/rotor/clamp {i}", M.clamp_arm(), (0.85, 0.42, 0.10), g, specular=0.35)
            sc.parent[g] = "dbox_rotor"
            sc.gmat[g] = M.clamp_pose(i, top, 0.0)
        self.clamp_f = 0.0
        sc.gmat["lstand"] = T((stand_x, line.Y_FACE, 0))
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
        if scene.AUDIT or PREVIEW:
            hits = self.hose_hits()
            if hits:
                log = self.sc.__dict__.setdefault("hose_log", [])
                log.append((self.sc.n, sorted(hits)))

    def hose_hits(self) -> set:
        """Round 9: the lance's hose against everything visible but the arm, the lance, its post and the floor pipe it
        runs into (collide.py's FCL on the drawn meshes). -> the names it goes through."""
        import collide
        sc = self.sc
        if getattr(sc, "_collide_world", None) is None:          # the arms' own (collide.Checker), built once
            sc._collide_world = collide.World(sc)
        W = sc._collide_world
        W.refresh()
        self._skip = {"hose", "lance", "lstand"}
        t = collide._tris(sc.actors["lance hose"].GetMapper().GetInput())
        if t is None:
            return set()
        hb = collide.Body("hose", "hose", *t)
        hb.place(np.eye(4))
        lo, hi = hb.box(np.eye(4))
        snap = W.current(self._skip | set(getattr(self, "robot_groups", set())))
        out = set()
        for b, blo, bhi, Mb in snap.items:
            if b.name == "floor pipe" or (blo > hi).any() or (bhi < lo).any():
                continue
            if b.pending is not None:
                b.ensure()
                b.place(Mb)
            if collide._hit(hb.obj, b.obj):
                out.add(b.name)
        return out

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

    def clamp(self, f1):
        """The swing clamps from clamp_f to f1 (0 open, under the chuck's top; 1 down on the plate's rim)."""
        f0 = self.clamp_f
        top = M.DBOX["chuck_top"]

        def up(u):
            self.clamp_f = f0 + (f1 - f0) * u
            for i in range(len(M.CLAMPS["angles"])):
                self.sc.gmat[f"dbox_clamp{i}"] = M.clamp_pose(i, top, self.clamp_f)
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

    def __init__(self, sc, place=None, tests=(TEST,), zbars=False):
        """place(bbox) -> the 4x4 that stands it on the floor (default: the old line's x); `tests`: the bars drawn in
        two halves, to break; zbars: the plate also carries round 9's two bars printed vertical (alloy_models.ZBARS),
        groups zbar0 and zbar1, which make the build 100 mm tall."""
        self.sc = sc
        ents = M.aconity_pieces()
        pts = np.vstack([e["mesh"].points for k, lst in ents.items() if k != "piston" for e in lst
                         if e["mesh"].n_points])
        lo, hi = pts.min(0), pts.max(0)
        bb = (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
        sc.gmat["aco"] = place(bb) if place is not None else line.place_floor(bb, line.LINE["aconity"])
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
        self.zbars = bool(zbars)
        self.build_h = M.E8_SUB["L"] if zbars else M.LUG[5]     # as tall as the vertical bars, or the lug
        self.piston_top = self.floor - self.build_h - M.PLATE["t"]
        self.door_f = 0.0
        # the plate, its lug and the bars, on the piston
        for name, (mesh, col, spec) in M.plate_parts().items():
            sc.add(f"plate/{name}", mesh, col, "plate", specular=spec)
        sc.parent["plate"] = "aco_piston"
        sc.gmat["plate"] = T((0, 0, M.PLATE["t"]))
        for k, x in enumerate(M.BAR_X):
            g = f"bar{k}"
            if k in tests:
                sc.add(f"bar{k}/a", M.bar_mesh("lo"), M.AS_BUILT, g, specular=0.2)
                sc.add(f"bar{k}/b", M.bar_mesh("hi"), M.AS_BUILT, f"{g}_b", specular=0.2)
                sc.parent[f"{g}_b"] = g
            else:
                sc.add(f"bar{k}/a", M.bar_mesh(), M.AS_BUILT, g, specular=0.2)
            sc.parent[g] = "plate"
            sc.gmat[g] = T((x, 0, 0))
        for k, (zx, zy) in enumerate(M.ZBARS if zbars else ()):
            g = f"zbar{k}"
            sc.add(f"zbar{k}/a", M.zbar_mesh(), M.AS_BUILT, g, specular=0.2)
            sc.parent[g] = "plate"
            sc.gmat[g] = T((zx, zy, 0.0))
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
        """The chamber door from door_f to f1 (0 shut, 1 open): it lifts about its top edge (alloy_models.door_T)."""
        f0 = self.door_f

        def up(u):
            self.door_f = f0 + (f1 - f0) * u
            self.sc.gmat["aco_door"] = M.door_T(self.door_f)
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
    Z_LO, Z_HI = 828.0, 1020.0     # round 11: the lower guide's top under the comb's ejector block (836), not 4 mm in it

    def __init__(self, sc, rig, comb=False):
        """comb=True: round 8's catch comb with its ejector pins instead of round 4's shelf (catch_comb())."""
        self.sc, self.rig = sc, rig
        body = f"{rig.prefix}body"
        for name, (mesh, col) in M.edm_fixture(self.PC).items():
            if comb and name == "catch shelf":
                continue
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
# Round 8 (PR #318 review of 2026-11-05). The chapter runs in the whole lab as the set-up movie leaves it
# (setup_lab.build: two Shuttles, every tray loaded, the floor plan), so the VLM in the background is the same one as in
# every other chapter. On that floor the Aconity MIDI stands in the north row at x 6950, the wire EDM across the aisle
# in the south row, the 68FM-100 at the south row's west end, and the furnace on tray F in Shuttle 1. What changed:
# * the cut bars no longer drop 14 mm onto a shelf: each settles 0.5 mm into a slot of a catch comb, walled on all
#   four sides, and an ejector pin lifts it for the gripper (alloy_models.catch_comb);
# * the IPA jar starts capped: the arm lifts its lid off onto a rest, and puts it back (alloy_models.ipa_jar);
# * all four bars go through it into a rack, specimens standing on end (r8_test.TRAY), and the rack is heat treated as
#   T6 on tray F: solution treatment, a quench through the tank's lift basket, ageing; hot, it is handled with tongs;
# * the 68FM-100 loads like Instron's AT6 cells (the lower grip first, then the upper grip comes down; the AVE 2 reads
#   the strain through the 3119-608 chamber's window): one bar at room temperature, one at 200 C in the chamber;
# * the MiR250 docks on the floor plan, turns on the spot and drives at its published 0.3 m/s^2 (props.ramp_*);
# * its plate carrier and bar holder are low pockets on the cabinet top, not posts (alloy_models.mir_pockets).
SPEC_ORDER = (3, 2, 1, 0)        # the order the bars come off the comb: the wire frees bar 3 first
JUMP = int(__import__("os").environ.get("CH5_FROM", "1"))   # previews: start at section 6 or 7 (not for renders)
# Round 9: CH5_TO=2 stops after section 2. With CH5_NAME, CH5_FROM=7 or CH5_TO=2 renders only those sections, under
# their own name, to be spliced into the whole render (frames of the other sections unchanged)
STOP = int(__import__("os").environ.get("CH5_TO", "7"))
HOT = 2                          # the bar pulled at temperature; TEST (3) is pulled at room temperature
HOT_C = 200.0                    # the chamber's set point (an example; the 3119-608 goes to 600 C)
GRIP_SPEC = GRIP_BAR             # 2F-85 on the specimen's 10 mm grip end
GRIP_HANDLE = GRIP_LUG           # on the tongs' 12 mm handle (as GRIP_LUG)
GRIP_KNOB = __import__("ur_arm").close_for(20.3)   # on the IPA lid's 20 mm knob
GRIP_HALF = 0.94                 # on a broken half's 6 mm reduced section
CAB_TOP = P.MIR["H"] + P.CAB_H   # 780: the MiR cabinet's top plate
XH_REST = 0.0                    # round 11: the Instron's crosshead at rest (the lab moved the junction box that stood
#                                  in its way to z 2350-2530 in 47219fc; until then it rested at -0.7)
COMB_DROP = 113.0                # round 11: the catch comb's slide: its top 3.5 mm under the plate's rim (845 mm) while
#                                  the plate goes on, its ejector block 2.5 mm over the tank's floor in the table's window
DRIVE_SHOWN = 4.0                # the long drives are shown at 4x, and say so
SS_HOT = dict(E=65000.0, ys=190.0, uts=245.0, elong=0.10,
              src="illustrative: AddUp's room-temperature values scaled to about 60 % at 200 C (assumed)")


def ss_points_for(ss: dict, n: int = 240) -> np.ndarray:
    E, ys, uts, epf = ss["E"], ss["ys"], ss["uts"], ss["elong"]
    b = 100.0 if epf < 0.07 else 60.0
    a1, a2 = 1 - math.exp(-b * 0.002), 1 - math.exp(-b * epf)
    Q = (uts - ys) / (a2 - a1)
    s0 = ys - Q * a1
    ep = np.linspace(0, epf, n)
    s = s0 + Q * (1 - np.exp(-b * ep))
    return np.vstack([[0.0, 0.0], np.c_[s / E + ep, s]])


SS_HOT_PTS = ss_points_for(SS_HOT)


def _draw_ss_r8(self, img):
    """Round 8's panel: the room-temperature curve, and the hot one over it in its own colour once it runs."""
    if not getattr(self, "ss_hot", False):
        return AlloyScene._draw_ss_r7(self, img)
    W, H = img.size
    k = W / 1280
    s = max(k, 0.8)
    bw, bh = int(430 * k), int(300 * k)
    x0, y0 = W - bw - int(14 * k), int(52 * k)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 6 * k, fill=(255, 255, 255, 238), outline=(150, 154, 160, 255))
    ft, fa, fn = font(13.5 * s, bold=True), font(11.5 * s), font(10.5 * s)
    d.text((x0 + 10 * k, y0 + 6 * k), f"Stress-strain: room temperature and {HOT_C:.0f} C", font=ft, fill=(20, 20, 24))
    px0, px1 = x0 + 52 * k, x0 + bw - 14 * k
    py0, py1 = y0 + 34 * k, y0 + bh - 66 * k
    emax, smax = 0.12, 500.0

    def X(e):
        return px0 + (px1 - px0) * e / emax

    def Y(sg):
        return py1 - (py1 - py0) * sg / smax
    for sg in (0, 100, 200, 300, 400, 500):
        d.line([(px0, Y(sg)), (px1, Y(sg))], fill=(232, 234, 238), width=1)
        d.text((px0 - 6 * k, Y(sg)), f"{sg}", font=fa, fill=MUTED, anchor="rm")
    for e in (0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12):
        d.text((X(e), py1 + 4 * k), f"{e * 100:.0f}", font=fa, fill=MUTED, anchor="mt")
    d.line([(px0, py1), (px1, py1)], fill=(150, 154, 160), width=max(1, int(k)))
    d.line([(px0, py0), (px0, py1)], fill=(150, 154, 160), width=max(1, int(k)))
    d.text(((px0 + px1) / 2, py1 + 17 * k), "strain, %", font=fa, fill=MUTED, anchor="mt")
    d.text((px0 + 4 * k, py0 - 3 * k), "MPa", font=fa, fill=MUTED, anchor="lb")
    rt = [(X(e), Y(sg)) for e, sg in SS_PTS]
    d.line(rt, fill=(150, 154, 160), width=max(2, int(round(2.0 * k))), joint="curve")
    d.text((rt[-1][0] + 4 * k, rt[-1][1] - 2 * k), "23 C", font=fa, fill=(110, 114, 120), anchor="ls")
    HOTC = (196, 78, 32)
    n = max(2, int(round(self.ss_u * (len(SS_HOT_PTS) - 1))) + 1)
    pts = [(X(e), Y(sg)) for e, sg in SS_HOT_PTS[:n]]
    d.line(pts, fill=HOTC, width=max(2, int(round(2.4 * k))), joint="curve")
    ex, ey = pts[-1]
    r = 4.5 * k
    if self.ss_broken:
        d.line([(ex - r, ey - r), (ex + r, ey + r)], fill=(190, 30, 30), width=max(2, int(2 * k)))
        d.line([(ex - r, ey + r), (ex + r, ey - r)], fill=(190, 30, 30), width=max(2, int(2 * k)))
    else:
        d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=HOTC, outline=(255, 255, 255))
    e_now, s_now = SS_HOT_PTS[n - 1]
    d.text((px1, py0 + 2 * k), f"{HOT_C:.0f} C: {s_now:.0f} MPa  {s_now * AREA / 1000:.1f} kN", font=fa,
           fill=(20, 20, 24), anchor="ra")
    d.text((x0 + 10 * k, y0 + bh - 30 * k), "Not measured: illustrative curves. 23 C through AddUp's as-built values;",
           font=fn, fill=(70, 72, 78))
    d.text((x0 + 10 * k, y0 + bh - 16 * k), f"{HOT_C:.0f} C assumed at about 60 % of its strength, twice its elongation.",
           font=fn, fill=(70, 72, 78))


def _draw_clock(self, img):
    """A box with a process clock or a temperature: self.clock = (title, value) or None."""
    if not getattr(self, "clock", None):
        return
    W, H = img.size
    k = W / 1280
    s = max(k, 0.8)
    title, value = self.clock
    ft, fv = font(12.5 * s), font(20 * s, bold=True)
    d = ImageDraw.Draw(img, "RGBA")
    bw = int(max(d.textlength(title, font=ft), d.textlength(value, font=fv)) + 26 * k)
    bh = int(56 * k)
    y0 = int(52 * k) + (int(312 * k) if self.ss_u is not None else 0)
    x0 = W - bw - int(14 * k)
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 6 * k, fill=(255, 255, 255, 238), outline=(150, 154, 160, 255))
    d.text((x0 + 12 * k, y0 + 7 * k), title, font=ft, fill=(70, 72, 78))
    d.text((x0 + 12 * k, y0 + 24 * k), value, font=fv, fill=(20, 20, 24))


AlloyScene._draw_ss_r7 = AlloyScene._draw_ss
AlloyScene._draw_ss = _draw_ss_r8
_overlay_r7 = AlloyScene.overlay


def _overlay_r8(self, img, scale, anchors):
    img = _overlay_r7(self, img, scale, anchors)
    if not CLEAN:
        _draw_clock(self, img)
    return img


AlloyScene.overlay = _overlay_r8


class Unit8:
    """setup_lab's unit 0 (MiR250 + UR10e with the D405 on its wrist) on the floor plan: turns on the spot and drives
    straight legs, each from rest to rest at the MiR250's 0.3 m/s^2 (props.ramp_*). Turning: 60 deg/s at most, at
    60 deg/s^2 (assumed; MiR publishes neither)."""

    def __init__(self, sc, unit):
        self.sc, self.u, self.rb = sc, unit, unit.robot
        self.name, self.cab = unit.name, f"{unit.name}_cab"
        self.top = CAB_TOP

    @property
    def pose(self):
        return list(self.u.pose)

    def set(self, x, y, hd):
        self.u.set((x, y, hd))
        if self.rb.held is not None:
            self.rb.set()

    def world(self, p):
        return (self.sc.world(self.name) @ np.r_[np.asarray(p, float), 1.0])[:3]

    def route(self, pts, end_heading=None, reverse_last=False, speed=MIR_SPEED, turn_rate=60.0, turn_acc=60.0):
        """-> (update(u), seconds) through the (x, y) points: pivot to face each leg, drive it; then pivot to
        end_heading. reverse_last backs the last leg in."""
        segs = []
        x, y, hd = self.u.pose
        for i, (px, py) in enumerate(pts):
            dist = math.hypot(px - x, py - y)
            if dist < 1:
                continue
            want = math.degrees(math.atan2(py - y, px - x)) + (180.0 if reverse_last and i == len(pts) - 1 else 0.0)
            turn = (want - hd + 180.0) % 360.0 - 180.0
            if abs(turn) > 0.5:
                segs.append(("turn", (x, y, hd), (x, y, hd + turn), P.ramp_secs(turn, turn_rate, turn_acc), turn))
                hd += turn
            segs.append(("drive", (x, y, hd), (px, py, hd), P.ramp_secs(dist, speed), dist))
            x, y = px, py
        if end_heading is not None:
            turn = (end_heading - hd + 180.0) % 360.0 - 180.0
            if abs(turn) > 0.5:
                segs.append(("turn", (x, y, hd), (x, y, hd + turn), P.ramp_secs(turn, turn_rate, turn_acc), turn))
        total = sum(sg[3] for sg in segs) or 1.0
        bounds = np.cumsum([0.0] + [sg[3] for sg in segs])

        def up(u):
            t = P.unease(u) * total
            for k, (kind, a, b, secs, d) in enumerate(segs):
                if t <= bounds[k + 1] + 1e-9 or k == len(segs) - 1:
                    f = min(1.0, max(0.0, (t - bounds[k]) / max(secs, 1e-9)))
                    g = P.ramp_frac(f, d, speed if kind == "drive" else turn_rate,
                                    P.MIR_ACCEL if kind == "drive" else turn_acc)
                    a, b = np.array(a), np.array(b)
                    self.set(*(a + (b - a) * g))
                    return
        return up, total


def build_lab():
    """The whole lab (setup_lab.build) with this chapter's own pieces in it. -> a dict of everything movie() uses."""
    import r8_test as RT
    import setup_lab as SL
    import warehouse as WH
    data = lab.meshes()
    idata = SL.load_all()
    il = getattr(SL, "item_label", None)
    if il is not None and not getattr(il, "_safe", False):      # setup_lab mid-edit (17:10): inst.name for title
        def safe_label(inst, il=il):
            try:
                return il(inst)
            except AttributeError:
                m = inst.model.strip()
                return f"{inst.title} (our design)" if m.lower() in ("our design", "ours", "(ours)") else m
        safe_label._safe = True
        SL.item_label = safe_label
    keep = SL.Scene
    SL.Scene = AlloyScene
    try:
        sc, L, F, items, rigs, units, util, ulabel, vp = SL.build(data, idata, name=NAME, title=TITLE)
    finally:
        SL.Scene = keep
    SL.add_bay_cams(sc)
    sc.intro = 0.8
    L.show_gauges = False
    L.extra_gauges = []
    L.skin(0.0)(1.0)                                  # the cladding as built: the trays in their slots stay inside
    sc.fluids = set(getattr(sc, "fluids", set())) | {"aco powder cake"}   # round 11: the bars are buried in it
    sc._lab = L
    # the Aconity MIDI opened up, in place of the set-up's closed one
    for nm in F.groups.get("aconity", []):
        sc.alpha[nm] = 0.0
        sc.base_alpha[nm] = 0.0
    cx, _, turn, _ = SL.FLOOR_PLAN["aconity"]
    W_ = Aconity(sc, place=lambda bb: WH.place(bb, cx, WH.Y_FACE_N, "N", turn), tests=(TEST, HOT), zbars=True)
    # the depowdering box and the lance's post, east of the printer as they stood beside it on the old line
    D = DBox(sc, box_x=cx + (DBOX_X - 3250.0), stand_x=cx + (LSTAND_X - 3250.0))
    sc.dbox = D
    # the EDM's fixture with the catch comb, the ejector pins, the IPA jar with its lid and the lid's rest
    erig, ins = F.rigs["wire_edm"], F.rigs["instron_floor"]
    E = Edm(sc, erig, comb=True)
    bar_xs = {k: E.PC[0] - M.BAR_X[k] for k in range(4)}     # on edge, the lug to +x: plate x -> EDM -x
    # round 11: the comb, its ejector pins and the troughs ride on a slide (group edm_comb): the plate goes onto the
    # receiver along its stud's axis, so its bars came in from the front through the comb's front wall and teeth
    # (the strict audit: 6-25 mm). The comb now waits COMB_DROP down in the table's window and rises under the bars
    # once the plate is clamped (a pneumatic slide, our design)
    for name, (mesh, col) in M.catch_comb(E.PC, list(bar_xs.values())).items():
        sc.add(f"edm fix/{name}", mesh, col, "edm_comb", specular=0.25)
    sc.add("edm fix/ejector block", M.ejector_body(E.PC, list(bar_xs.values())), (0.42, 0.44, 0.47), "edm_comb")
    for name, (mesh, col) in M.zbar_troughs(E.PC).items():          # round 9: under the vertical bars
        sc.add(f"edm fix/{name}", mesh, col, "edm_comb", specular=0.25)
    sc.parent["edm_comb"] = "edm_fix"
    sc.gmat["edm_comb"] = T((0.0, 0.0, -COMB_DROP))
    for k, bx in bar_xs.items():
        sc.add(f"edm pin/{k}", M.ejector_pin(E.PC, bx), (0.80, 0.81, 0.83), f"edm_pin{k}", specular=0.5)
        sc.parent[f"edm_pin{k}"] = "edm_comb"
        sc.gmat[f"edm_pin{k}"] = np.eye(4)
    ymin = erig.inst.bbox()[2]
    jar_at = E.world((E.PC[0] + 470.0, ymin - 95.0, 0.0))
    jar_at[2] = 0.0
    sc.gmat["rinse"] = T(tuple(jar_at))
    for name, (mesh, col, spec, op) in M.ipa_jar().items():
        sc.add(f"rinse/{name}", mesh, col, "rinse", opacity=op, specular=spec)
    sc.fluids |= {"rinse/liquid"}
    rest_at = E.world((E.PC[0] + 470.0 + 170.0, ymin - 95.0, 0.0))
    rest_at[2] = 0.0
    sc.add("lid rest", M.lid_rest(), (0.30, 0.32, 0.36), "lidrest", specular=0.3)
    sc.gmat["lidrest"] = T(tuple(rest_at))
    for name, (mesh, col) in M.rinse_lid().items():
        sc.add(f"ipa lid/{name}", mesh, col, "ipalid", specular=0.4)
    sc.gmat["ipalid"] = T(tuple(jar_at + (0, 0, M.JAR["z1"] + M.JAR["ring_h"])))
    # the MiR: setup_lab's unit 0, its cups holder swapped for this run's low pockets, the rack and the tongs
    u0 = Unit8(sc, units[0])
    sc.alpha[f"{u0.name}/holder"] = 0.0
    sc.base_alpha[f"{u0.name}/holder"] = 0.0
    for name, (mesh, col) in M.mir_pockets(CAB_TOP).items():
        sc.add(f"{u0.name}/{name}", mesh, col, u0.cab, specular=0.2)
    rack_mesh = lab.to_mesh(RT.spec_tray().val(), 0.6)
    sc.add("rack/rack", rack_mesh, (0.74, 0.75, 0.77), "rack", specular=0.45)
    sc.parent["rack"] = u0.cab
    sc.gmat["rack"] = T(tuple(M.rack_seat(CAB_TOP)))
    for name, (mesh, col) in M.tongs().items():
        sc.add(f"tongs/{name}", mesh, col, "tongs", specular=0.45)
    tx, ty = M.POCKETS["tongs"]
    sc.parent["tongs"] = u0.cab
    sc.gmat["tongs"] = T((M.TONGS_HANDLE[0], ty, CAB_TOP + 36.0 + M.TONGS["shaft_r"])) @ R((0, 0, 1), -90.0)
    # round 11: the specimen fingers (ur_arm.spec_finger_meshes), standing in their stand on the MiR (alloy_models.
    # FINGER_STAND) until the Instron: two groups, one per fingertip, under the container "sfing", placed where the
    # 2F-85's fingertips are when it stands over the stand pointing down, opened to the stand's 30 mm gap
    import ur_arm as UA
    sf_at = M.finger_stand_grasp(CAB_TOP)
    sf_close = UA.spec_close(M.FINGER_STAND["gap"])
    sf_tcp = P.tcp_frame(sf_at, (0.0, 0.0, -1.0), 0.0) @ T((0.0, 0.0, -(UA.spec_tcp_mm(sf_close) - UA.TCP_MM)))
    sf_tool0 = sf_tcp @ T((0.0, 0.0, -UA.TCP_MM))
    G_st = UA.gripper_fk(sf_close)
    sc.parent["sfing"] = u0.cab
    sc.gmat["sfing"] = T(tuple(sf_at))
    sf_parts = {}
    for tip, lst in UA.spec_finger_meshes().items():
        g_ = f"sfing_{tip}"
        for i, (mesh, col, spec) in enumerate(lst):
            sc.add(f"sfing/{tip}/{i}", mesh, col, g_, specular=spec)
        sc.parent[g_] = "sfing"
        sc.gmat[g_] = np.linalg.inv(T(tuple(sf_at))) @ sf_tool0 @ G_st[tip]
        sf_parts[tip] = g_
    # tray F's furnace and quench tank (setup_lab's rigs), their hidden pieces found by name
    fur = next(r for k_, r in rigs.items() if k_.startswith("F") and k_.endswith("_furnace"))
    qt = next(r for k_, r in rigs.items() if k_.startswith("F") and k_.endswith("_quench_tank"))
    sc.fluids |= {n for n in qt.all_names() if "/window" in n}
    glow = {"furnace": [n for n in sc.actors if n.startswith(f"{fur.prefix}glow/")],
            "chamber": [n for n in sc.actors if n.startswith(f"{ins.prefix}glow/")]}
    for n in (n for n in sc.actors if n.startswith(f"{ins.prefix}ave/")):   # the AVE 2: a prop in the tours
        sc.alpha[n] = 1.0
        sc.base_alpha[n] = 1.0
    sc.fluids |= set(glow["furnace"]) | set(glow["chamber"])
    L.apply_state()
    ins.move({"crosshead": (XH_REST, XH_REST)})(1.0)          # round 11: under the junction box (section 7)
    return dict(sc=sc, L=L, F=F, rigs=rigs, units=units, W=W_, D=D, E=E, erig=erig, ins=ins, fur=fur, qt=qt,
                u0=u0, bar_xs=bar_xs, glow=glow, jar_at=jar_at, rest_at=rest_at, sf_tcp=sf_tcp, sf_close=sf_close,
                sf_parts=sf_parts)


def movie():
    B = build_lab()
    try:
        return _movie(B)
    except Exception:
        if PREVIEW and getattr(B["sc"], "preview", None):
            B["sc"].save()                          # the stills up to the failure, to /tmp/preview_<name>.png
        raise


def _movie(B):
    import r8_test as RT
    import setup_lab as SL  # noqa: F401
    import warehouse as WH
    sc, L, W, D, E = B["sc"], B["L"], B["W"], B["D"], B["E"]
    edm, ins, fur, qt, amr = B["erig"], B["ins"], B["fur"], B["qt"], B["u0"]
    rb = amr.rb
    PARK = np.radians(A.PARK_DEG)
    n = 7
    st = {"lbl": "1/7", "cap": ""}
    chk_mir = None
    if scene.AUDIT:
        chk_mir = WH.MirCheck(sc, (amr.name,))
        sc.frame_hooks.append(chk_mir)

    # ---------------------------------------------------------------- helpers
    def step(secs, f=None, hold=0.05, cam=None, labels=None, still=False):
        kw = dict(hold=hold, cam_to=cam, still=still)
        if labels is not None:
            kw["labels"] = labels
        sc.step(st["lbl"], st["cap"], secs, f, **kw)

    def go(Tw=None, q=None, secs=1.6, grip=None, extra=None, **kw):
        f = rb.joint_to(Tw=Tw) if Tw is not None else rb.joint_to(q)
        step(secs, RB.both(f, rb.grip_to(grip) if grip is not None else None, extra), **kw)

    def lin(Tw, secs=0.8, extra=None, **kw):
        step(secs, RB.both(rb.line_to(Tw), extra), **kw)

    def grip(c, secs=0.4):
        step(secs, rb.grip_to(c))

    def park(secs=1.4, away=None, **kw):
        go(q=clear_park(away), secs=secs, **kw)

    def clear_park(away=None):
        """Round 9: PARK, or the first of a few variants of it (turned about the base, less folded) that touches
        nothing where the arm is now. Round 8's PARK put wrist 2 against the tongs on their rest and against the
        Instron chamber's open door."""
        import collide  # noqa: F401
        import ur_arm
        chk = rb.checker()
        Wd = chk.snapshot()
        clear = []
        for fold in (A.PARK_DEG, (-90.0, -120.0, 110.0, -80.0, -90.0, 180.0)):
            for dq0 in (0.0, 45.0, -45.0, 90.0, -90.0, 180.0):
                q = np.radians(fold).copy()
                q[0] += math.radians(dq0)
                if not chk.collisions(q, rb.close, Wd, set(), first=True):
                    if away is None:
                        return q
                    clear.append(q)
        if not clear:
            return PARK
        # `away`: of the clear ones, the one whose wrist is furthest from that point (the Instron's load string, so the
        # camera sees the test past the parked arm)
        Wr = sc.world(rb.root)

        def dist(q):
            w = (Wr @ ur_arm.fk(rb.model, q)["tool0"])[:2, 3]
            return float(np.hypot(*(w - np.asarray(away, float)[:2])))
        return max(clear, key=dist)

    def clear_q(Tw):
        """Round 9: the IK solution for the TCP pose Tw nearest the arm's joints now that touches nothing but what the
        gripper is handling (collide.py); None if there is none. A joint move to Tw alone may end in a folded branch:
        round 8's planner reported two such ends carrying a bar from the IPA jar to the rack."""
        import collide
        chk = rb.checker()
        Wd = chk.snapshot()
        Tb = np.linalg.inv(sc.world(rb.root)) @ Tw
        best = None
        for q in collide.ik_all(rb.model, Tb, rb.q):
            if not chk.collisions(q, rb.close, Wd, chk.touching(q, rb.close, Wd), first=True):
                d = float(np.abs(np.asarray(q) - rb.q).sum())
                if best is None or d < best[0]:
                    best = (d, np.asarray(q, float))
        return None if best is None else best[1]

    def go_clear(Tw, **kw):
        """go(Tw=Tw), but to a collision-free IK branch of it when there is one."""
        q = clear_q(Tw)
        if q is None:
            go(Tw=Tw, **kw)
        else:
            go(q=q, **kw)

    def pick_clear(make, options):
        """Round 9: the first of options (an approach direction, a spin) for which make(option) -> the TCP pose of the
        move's end has a collision-free IK branch, and that branch; -> (option, q or None). Round 8 went to one
        fixed pose at the IPA jar, the rack and the halves' cradle, and every branch of three of them was folded or
        put wrist 2 on the tongs."""
        for o in options:
            q = clear_q(make(o))
            if q is not None:
                return o, q
        return options[0], None

    def go_pick(make, options, **kw):
        o, q = pick_clear(make, options)
        if q is None:
            go(Tw=make(o), **kw)
        else:
            go(q=q, **kw)
        return o

    def turned(d, deg):
        c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        return (d[0] * c - d[1] * s_, d[0] * s_ + d[1] * c)

    def rack_dirs():
        """The two level approaches that keep a bar's 10 mm width along the rack's slots: along -y, then +y of the
        rack (world xy)."""
        ry = sc.world("rack")[:3, :3] @ np.array([0.0, 1.0, 0.0])
        return [(-ry[0], -ry[1]), (ry[0], ry[1])]

    def drive(pts, end_heading=None, reverse_last=False, extra=None, shown=1.0, **kw):
        up, secs = amr.route(pts, end_heading, reverse_last)
        step(max(1.0, secs / shown), RB.both(up, extra), **kw)
        return secs

    def lvl(p, toward, spin=0.0):
        """Gripper level at p, pointing along `toward` (xy), fingers closing horizontally."""
        t = np.array([toward[0], toward[1], 0.0], float)
        return P.tcp_frame(np.asarray(p, float), t / np.linalg.norm(t), spin)

    def back(Tw, d):
        """Tw moved d mm back along its own approach."""
        M_ = Tw.copy()
        M_[:3, 3] = M_[:3, 3] - M_[:3, 2] * d
        return M_

    def up_(Tw, dz):
        M_ = Tw.copy()
        M_[:3, 3] = M_[:3, 3] + np.array([0, 0, dz])
        return M_

    def edir(d):
        Mb = sc.world(f"{edm.prefix}body")
        return Mb[:3, :3] @ np.asarray(d, float)

    def rig_w(rig, p):
        return (sc.world(f"{rig.prefix}body") @ np.r_[np.asarray(p, float), 1.0])[:3]

    def rig_dir(rig, d):
        return sc.world(f"{rig.prefix}body")[:3, :3] @ np.asarray(d, float)

    def clock(title, fmt, t0, t1, unit="min"):
        def f(u):
            t = t0 + (t1 - t0) * u
            sc.clock = (title, fmt(t))
        return f

    def hm(t):                                     # minutes -> "1 h 05 min"
        return f"{int(t // 60)} h {int(t % 60):02d} min" if t >= 60 else f"{int(t)} min"

    def fade(names, a0, a1):
        def f(u):
            for nm in names:
                sc.alpha[nm] = a0 + (a1 - a0) * u
        return f

    UA = __import__("ur_arm")
    fs = RB.FingerSet(rb, "sfing", B["sf_parts"])
    C_ST = B["sf_close"]
    C_SPEC, C_SPEC_OPEN = UA.spec_close(10.3), UA.spec_close(22.0)     # the bar's 10 mm grip end; 6 mm a side open
    C_HALF, C_HALF_OPEN = UA.spec_close(6.3), UA.spec_close(16.0)      # a half's 6 mm reduced section; 5 mm a side
    C_HALF_REL = UA.spec_close(9.0)                                    # let go in the cradle's relief: 1.5 a side
    BACK_OFF = 60.0                                                    # mm: the crosshead after the break
    HALF_OUT = 40.0                                                    # mm: each half out of its grip (30 mm in it)
    HALF_IN = 10.0                                                     # the fingers' grasp, mm from the broken end

    def jaws(where, a, b):
        """The grip's two jaws (r8_test.JAW), 0 open, 1 closed on the specimen."""
        return {f"{where}_jaw_f": (a, b), f"{where}_jaw_b": (a, b)}

    def SF(Tw, c):
        """The TCP pose that puts the specimen fingers' grasp point (midway between the blades) at Tw."""
        return back(Tw, UA.spec_tcp_mm(c) - UA.TCP_MM)

    def fingers(on, cam=None, cap=None):
        """Fit the specimen fingers from their stand on the MiR (on), or put them back in it."""
        Ts = sc.world(amr.cab) @ B["sf_tcp"]
        st["cap"] = ("First the arm fits fingers made for the specimen, as automated tensile cells do (ZwickRoell's "
                     "roboTest C has a finger for each specimen thickness): two caps slip over the 2F-85's fingertips, "
                     "each ending in a blade 8 mm tall, 74 mm further out (our design)." if on else
                     "The specimen fingers go back in their stand on the MiR.") if cap is None else cap
        status(sc, Arm="fitting the specimen fingers" if on else "putting the specimen fingers back")
        go(Tw=up_(Ts, 90.0), secs=1.6, grip=C_ST, cam=cam,
           labels=[("specimen fingers, in their stand", tuple(Ts[:3, 3] + (0, 0, -60)), (0.30, 0.66))] if on else None)
        lin(Ts, 0.8)
        if on:
            rb.grasp("sfing")
            fs.on = True
        else:
            fs.on = False
            rb.release(amr.cab)
        lin(up_(Ts, 90.0), 0.7, labels=[])

    def cam_mir(at_local, back_=(700.0, -1000.0, 900.0)):
        """A camera on a point of the MiR's cabinet top (MiR frame), from its outer (-y) side and above."""
        a = np.asarray(at_local, float)
        return [tuple(amr.world(a + np.asarray(back_))), tuple(amr.world(a)), (0, 0, 1)]

    def take(g):
        """The fingers have closed on group g: the arm holds g from here, and the fingers ride on it (FingerSet)."""
        rb.release(None)
        rb.grasp(g)
        rb.reparent("sfing", g)

    def give(g, parent):
        """g goes to `parent`; the arm holds the fingers again."""
        rb.release(parent)
        rb.grasp("sfing")

    # key points
    aco_bp = W.world(W.bp())
    aco_x = aco_bp[0] - 146.0
    MIR_YN = MIR_Y
    MIR_YS = WH.Y_FACE_S + 230.0 + P.MIR["W"] / 2
    LANE = (WH.AISLE[0] + WH.AISLE[1]) / 2
    PIVOT_X = (V.SHUTTLE_X[1] + V.SHUTTLE_X[2]) / 2
    Y_TF = WH.DOCK_N - 350.0           # tray F's work: 350 mm further out than the dock, room for the tongs
    edm_pc = E.world(E.PC)
    ins_axis = rig_w(ins, (0.0, 0.0, 700.0))
    amr.set(aco_x, MIR_YN, 0.0)
    edm_x = edm_pc[0]
    rack_w = lambda p_: (sc.world("rack") @ np.r_[np.asarray(p_, float), 1.0])[:3]      # noqa: E731
    total_xy = 4 * M.bar_mesh().volume / M.E8_SUB["T"]
    total = total_xy + (len(M.ZBARS) * M.E8_SUB["C"] * M.E8_SUB["T"] if W.zbars else 0.0)
    if JUMP > 5:                       # CH5_FROM=6 or 7: start from the state the earlier sections leave
        sc.gmat["edm_comb"] = np.eye(4)
        for nm in sc.members("plate") + [n_ for n_ in sc.actors if n_.startswith("plate/")]:
            sc.alpha[nm] = 0.0
        for i, k in enumerate(SPEC_ORDER):
            g = f"bar{k}"
            sc.parent[g] = "rack"
            sc.gmat[g] = (T((RT.SPEC_X[RT.XY_SLOTS[3 - i]], 0.0, RT.TRAY["floor"] + M.E8_SUB["L"] / 2))
                          @ R((1, 0, 0), 90.0) @ T((0.0, 0.0, -M.E8_SUB["T"] / 2)))
        for j in range(len(M.ZBARS) if W.zbars else 0):
            g = f"zbar{j}"
            sc.parent[g] = "rack"
            sc.gmat[g] = T((RT.SPEC_X[RT.Z_SLOTS[j]], 0.0, RT.TRAY["floor"] + 0.5))
        amr.set(edm_x, WH.Y_FACE_S + 230.0 + P.MIR["W"] / 2, 180.0)
    if JUMP > 6:
        amr.set(0.0, Y_TF, 0.0)

    CAM_WIDE = [(aco_bp[0] - 1500, -12500, 6200), (aco_bp[0] - 2600, -3900, 700), (0, 0, 1)]
    CAM_ACO = [tuple(aco_bp + (-1700, -2300, 1500)), tuple(aco_bp + (100, -520, -120)), (0, 0, 1)]
    CAM_ACO_IN = [tuple(aco_bp + (-1250, -900, 850)), tuple(aco_bp + (30, -120, 10)), (0, 0, 1)]
    # round 9: the lance at work, seen through the open door from the front-left and above, the gripper outside
    CAM_LANCE = [tuple(aco_bp + (650, -1300, 300)), tuple(aco_bp + (-20, 0, -10)), (0, 0, 1)]
    sc.cam = list(CAM_WIDE)
    status(sc, Arm="UR10e on MiR250, at the Aconity", Plate="in the Aconity MIDI", Bar="", EDM="", Instron="")
    lbl = [("Aconity MIDI metal printer", (line.LINE["aconity"], WH.Y_FACE_N + 300, 2400), (0.80, 0.16)),
           ("FANUC ROBOCUT wire EDM", tuple(rig_w(edm, (0, 0, 2000))), (0.80, 0.80)),
           ("Instron 68FM-100 with a 3119-608 chamber", tuple(rig_w(ins, (0, 0, 2300))), (0.12, 0.78)),
           ("tray F: the furnace (Shuttle 1)", (0.0, -1500.0, 2600.0), (0.30, 0.14)),
           ("UR10e on a MiR250", tuple(amr.world((0, 0, 1300))), (0.62, 0.40))]
    st["lbl"], st["cap"] = f"1/{n}", ("The alloy route's chapter 5, in the lab as it was set up: the print comes out of the "
                                     "Aconity MIDI and is depowdered, the wire EDM across the aisle cuts the four "
                                     "tensile bars off it, they are heat treated on tray F, then two are pulled in the "
                                     "Instron 68FM-100, at room temperature and at 200 C.")
    step(3.0, None, hold=1.8, labels=lbl)

    if JUMP <= 5:
        # ---------------------------------------------------------------- 2. the print, the lance, the box (round 5)
        D_ = D
        D_.robot_groups = rb.checker().robot_groups()      # the hose's check leaves the arm to collide.py
        box_c = D_.world((M.DBOX["chuck_x"], M.DBOX["axis_y"], M.DBOX["chuck_top"]))
        lance_c = D_.lworld(M.HOLSTER)
        CAM_DEP = [tuple(lance_c + (700, -2500, 1250)), tuple(lance_c + (-250, -150, -280)), (0, 0, 1)]
        CAM_BOX = [tuple(box_c + (950, -1750, 850)), tuple(box_c + (-60, -60, -90)), (0, 0, 1)]
        CAM_CLAMP = [tuple(box_c + (250, -700, 300)), tuple(box_c + (0, 10, 10)), (0, 0, 1)]
        p_hold = D_.lworld(M.HOLSTER)
        box_x = box_c[0] - 78.0 - 146.0
        l_dir = np.array([0, math.cos(math.radians(LANCE_DOWN)), -math.sin(math.radians(LANCE_DOWN))])

        def lance_at(tip):
            return tilt(np.asarray(tip, float) - l_dir * LANCE_TIP, down=LANCE_DOWN)
        st["lbl"] = f"2/{n}"
        st["cap"] = ("The print is done: four ASTM E8 subsize tensile bars, 100 mm long and 6 mm thick, printed flat on a "
                     "170 mm plate from the route's own Al-10Si powder (DAL PR #169's build at Utah), and a handling lug "
                     "for the gripper. They are still buried in powder; the chamber is drawn see-through.")
        status(sc, Plate="in the build cylinder, under powder")
        step(3.0, W.ghost(1.0), hold=1.2, cam=CAM_ACO,
             labels=[("process chamber", tuple(W.world(M.build_point() + (250, 0, 250))), (0.20, 0.24)),
                     ("build cylinder, 170 mm", tuple(aco_bp + (0, 0, -60)), (0.16, 0.62))])
        st["cap"] = ("The chamber door opens. The MIDI has no automatic depowdering, so the arm takes a suction lance off "
                     "its post; a pipe along the floor takes the powder to the depowdering box's separator.")
        status(sc, Arm="taking the suction lance", Plate="under powder")
        # round 9: the door lifts in view (CAM_ACO), hinged along its top edge, before the shot moves to the lance
        flap_top = W.world(np.array(M.door_T(1.0) @ np.r_[np.array(M.door_pivot()) + (290.0, 0.0, -278.0), 1.0])[:3])
        step(1.6, RB.both(W.door(1.0), fade(W.names["door"], 0.2, 1.0), W.ghost(0.0, pieces=("shell", "cabinet"))),
             hold=0.4, labels=[("the door lifts, hinged along its top edge", tuple(flap_top + (0, 0, 40)),
                                (0.42, 0.14))])
        step(1.6, D_.with_hose(RB.both(rb.joint_to(Tw=A.down(p_hold + (0, 0, 130), spin=0.0)), rb.grip_to(0.0))),
             cam=CAM_DEP,
             labels=[("depowdering box", tuple(D_.world((0, 0, M.DBOX["H"] + 60))), (0.80, 0.16)),
                     ("suction lance", tuple(p_hold + (0, -30, 60)), (0.62, 0.30))])
        lin(A.down(p_hold, spin=0.0), 0.7)
        grip(GRIP_LUG)
        rb.grasp("lance")
        step(0.5, D_.with_hose(rb.line_to(A.down(p_hold + (0, 0, 14), spin=0.0))))
        step(0.7, D_.with_hose(rb.line_to(A.down(p_hold + (0, -120, 14), spin=0.0))))
        step(0.9, D_.with_hose(rb.line_to(A.down(p_hold + (0, -300, 260), spin=0.0))))
        # Round 9 (Sterling: "that vacuuming seems pretty clearly to have interference with the machine"). The lance is
        # 400 mm long now, so the gripper stays outside the chamber; the nozzle (22 mm flare) keeps its centre within
        # 60 mm of the bore's axis, so it stays inside the 170 mm cylinder, 36 mm right of the lug's rows and 28 mm off
        # the two vertical bars; the hose is checked against the machine (DBox.hose_hits) as the arm moves.
        R_NOZ = 60.0
        rows = (45.0, 15.0, -15.0, -45.0)
        x_right = M.ZBARS[0][0] - 5.0 - 28.0 if W.zbars else R_NOZ
        path = []
        for i, dy in enumerate(rows):
            half = math.sqrt(R_NOZ ** 2 - dy ** 2)
            x_lo = -half if abs(dy) > 40 else -36.0
            x_hi = min(half, x_right)
            xs = (x_lo, x_hi) if i % 2 == 0 else (x_hi, x_lo)
            path += [aco_bp + (xs[0], dy, 0.0), aco_bp + (xs[1], dy, 0.0)]
        path = np.array(path)
        seg = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
        NOZ = 24.0

        def noz_z(z_piston):
            bars_top = z_piston + M.PLATE["t"] + M.E8_SUB["T"]
            return max(W.floor + NOZ, bars_top + NOZ + 2.0)
        path[:, 2] = noz_z(W.piston_top)
        entry = path[0] - l_dir * 150
        st["cap"] = ("It vacuums the plate as the platform rises a step at a time, the nozzle sweeping the build cylinder at "
                     "floor level: what a person does with a brush and an ATEX vacuum. The powder goes to be sieved again.")
        status(sc, Arm="vacuuming the build", Plate="rising out of the powder")
        step(1.8, D_.with_hose(rb.joint_to(Tw=lance_at(entry))), cam=CAM_LANCE)
        step(1.0, D_.with_hose(rb.line_to(lance_at(path[0]))))
        lift_to = W.floor + 18.0 - M.PLATE["t"]
        z_p0 = W.piston_top
        ring = np.array([(math.cos(a), math.sin(a), 0.0) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)])

        def sweep(u):
            s_ = u * seg[-1]
            k = min(int(np.searchsorted(seg, s_, side="right")) - 1, len(path) - 2)
            f = (s_ - seg[k]) / max(seg[k + 1] - seg[k], 1e-6)
            tip = path[k] + (path[k + 1] - path[k]) * f
            zp = z_p0 + (lift_to - z_p0) * u
            tip[2] = noz_z(zp)
            rb.set(rb.solve(lance_at(tip), rb.q))
            W.set_piston(zp)
            D_.update_hose()
            ph = (u * 22.0 + np.arange(len(ring)) * 0.37) % 1.0
            pts = tip + ring * (34.0 * (1 - ph))[:, None] + np.c_[np.zeros((len(ring), 2)), 6.0 * (1 - ph)]
            sc.set_mesh("lance suck", pv.PolyData(pts))
            sc.alpha["lance suck"] = 1.0 if 0.02 < u < 0.98 else 0.0
        step(6.0, sweep, hold=0.1,
             labels=[("bars and lug, as built", tuple(W.world(M.build_point(W.floor + 18) + (0, -60, 10))),
                      (0.18, 0.36)),
                     ("two bars printed vertical", tuple(W.world(M.build_point(W.floor + 70) + (68, 0, 0))),
                      (0.70, 0.22))])
        sc.alpha["lance suck"] = 0.0
        sc.alpha["plate residue"] = 1.0
        st["cap"] = "The lance goes back on its post. It leaves loose grains round the bars and the lug."
        status(sc, Arm="putting the lance back", Plate="out of the powder; grains left on it")
        step(0.9, D_.with_hose(rb.line_to(lance_at(path[-1] + (0, 0, noz_z(lift_to) - path[-1][2]) - l_dir * 200))),
             labels=[])
        step(1.8, D_.with_hose(rb.joint_to(Tw=A.down(p_hold + (0, -300, 260), spin=0.0))), cam=CAM_DEP)
        step(0.9, D_.with_hose(rb.line_to(A.down(p_hold + (0, -120, 14), spin=0.0))))
        step(0.7, D_.with_hose(rb.line_to(A.down(p_hold + (0, 0, 14), spin=0.0))))
        step(0.4, D_.with_hose(rb.line_to(A.down(p_hold, spin=0.0))))
        grip(0.0)
        rb.release("dbox")
        lin(A.down(p_hold + (0, 0, 130), spin=0.0), 0.6)
        # the plate out by its lug, 30 deg down (the chamber is 280 mm tall inside), into the box
        st["cap"] = ("The platform's clamp lets go (a zero-point clamp: an assumption). The chamber is too low for the "
                     "gripper pointing down, so it takes the lug pointing 30 deg down and lifts the plate out.")
        p_g = held_point(sc, "plate", (-78.0, 0, 28.0))
        a_dir = np.array([0, math.cos(math.radians(TILT)), -math.sin(math.radians(TILT))])
        status(sc, Arm="taking the plate")
        p_out = p_g + (0, -470, 52)
        go(Tw=tilt(p_out), secs=1.8, grip=0.0, cam=CAM_LANCE, labels=[("handling lug", tuple(p_g + (0, 0, 20)),
                                                                          (0.20, 0.30))])
        lin(tilt(p_g + (0, -40, 32)), 1.2)
        lin(tilt(p_g), 0.6)
        grip(GRIP_LUG, 0.5)
        status(sc, Plate="clamp released; in the gripper")
        rb.grasp("plate")
        lin(tilt(p_g + (0, 0, 32)), 0.8)
        lin(tilt(p_out), 1.8, labels=[])
        # round 11: carried 150 mm further from the row than round 10's 300: driving past the lance's post to the box,
        # the plate and the bars standing on it went through the hose where it leaves the lance's barb (the strict
        # audit: 6-50 mm, three frames)
        p_carry = amr.world((-330.0, 150.0, 0.0)) + (0, 0, 1250.0)
        go(Tw=tilt(p_carry), secs=1.4)
        p_box = D_.seat_tcp()
        st["cap"] = ("Into the depowdering box beside the printer: the door slides up and the arm sets the plate's stud in "
                     "a zero-point chuck on a turning shaft. The box is our design, after Solukon's SFM-AT200.")
        status(sc, Arm="loading the depowdering box")
        drive([(box_x, MIR_YN)], extra=RB.both(D_.door(1.0), W.door(0.0)), cam=CAM_BOX)
        p_mid = p_box + (0, -200, 100)
        go(q=branch_q(rb, tilt(p_mid), tilt(p_box)), secs=1.6,
           labels=[("zero-point chuck", tuple(box_c + (0, 0, -30)), (0.80, 0.40))])
        lin(tilt(p_box + (0, 0, 30)), 1.2)    # round 11: the stud's tip 10 mm over the chuck, then straight down
        lin(tilt(p_box), 0.5)
        grip(0.0)
        rb.release("dbox_rotor")
        status(sc, Plate="in the depowdering box")
        lin(tilt(p_box - a_dir * 260), 0.9, labels=[])
        park(1.2)
        st["cap"] = ("Clamped, twice over: the chuck pulls the plate's stud down and locks it (a zero-point clamp), "
                     "and three swing clamps on the rotor rise, turn their arms over the plate's rim and pull it down.")
        status(sc, Plate="clamped: stud in the chuck, three swing clamps")
        step(1.6, RB.both(D_.clamp(1.0), D_.ghost(1.0)), hold=0.3, cam=CAM_CLAMP,
             labels=[("swing clamps (3), on the rotor", tuple(D_.world(M.clamp_pose(0, M.DBOX["chuck_top"], 1.0)[:3, 3]
                                                                   + (0, 0, 20))), (0.74, 0.30)),
                     ("zero-point chuck: the stud locked in it", tuple(box_c + (0, 0, -30)), (0.70, 0.66))])
        st["cap"] = ("The door shuts and the box fills with argon. The shaft turns the plate over and back while a "
                     "vibrator shakes the grains loose; they fall through the hopper into a closed bottle.")
        status(sc, Arm="waiting", Plate="turned and shaken, under argon")
        step(1.2, D_.door(0.0), hold=0.1, cam=CAM_BOX,
             labels=[("vibrator", tuple(D_.world((M.DBOX["chuck_x"] + 125, M.DBOX["axis_y"], M.DBOX["axis_z"]))),
                      (0.78, 0.30)),
                     ("hopper to a closed bottle", tuple(D_.world((M.DBOX["chuck_x"], M.DBOX["axis_y"],
                                                                   M.DBOX["base"] + 90))), (0.78, 0.66))])
        keys = ([0.0, 0.22, 0.44, 0.70, 1.0], [0.0, 150.0, -150.0, 180.0, 0.0])
        gone = {"res": 1.0}
        rng = np.random.default_rng(11)
        drops = np.c_[rng.uniform(-60, 60, 40), rng.uniform(-40, 40, 40), rng.uniform(0, 1, 40)]
        pz0, pz1 = M.DBOX["axis_z"] - 60.0, M.DBOX["base"] + 60.0

        def cycle(u):
            ang = float(np.interp(u, *keys))
            D_.set_angle(ang, 1.5 * math.sin(u * 2 * math.pi * 55.0))
            if abs(ang) > 95:
                gone["res"] = max(0.0, min(gone["res"], 1.0 - (abs(ang) - 95.0) / 45.0))
            sc.alpha["plate residue"] = gone["res"]
            on = 0.12 < u < 0.92 and abs(ang) > 100
            if on:
                ph = (drops[:, 2] + u * 9.0) % 1.0
                pts = np.c_[M.DBOX["chuck_x"] + drops[:, 0], M.DBOX["axis_y"] + drops[:, 1], pz0 + (pz1 - pz0) * ph ** 1.6]
                sc.set_mesh("dbox fall", pv.PolyData(pts))
            sc.alpha["dbox fall"] = 1.0 if on else 0.0
        step(6.0, cycle, hold=0.2, labels=None)
        D_.set_angle(0.0)
        sc.alpha["dbox fall"] = 0.0
        sc.alpha["plate residue"] = 0.0
        st["cap"] = ("Clean. The arm takes the plate out by its lug and sets it in the low pocket on the MiR250's cabinet: "
                     "the plate drops 12 mm into a bored block (round 7 asked for pockets, not posts).")
        status(sc, Plate="depowdered", Arm="taking the plate")
        step(1.2, RB.both(D_.ghost(0.0), D_.door(1.0)), hold=0.05, labels=[])
        status(sc, Plate="depowdered; clamps open")
        step(1.0, D_.clamp(0.0), hold=0.1)
        go(Tw=tilt(p_box - a_dir * 260), secs=1.3, grip=0.0)
        lin(tilt(p_box - a_dir * 60), 0.7)
        lin(tilt(p_box), 0.5)
        grip(GRIP_LUG)
        rb.grasp("plate")
        lin(tilt(p_box + (0, 0, 14)), 0.5)
        lin(tilt(p_mid), 1.0)
        seat = amr.world(M.plate_seat(CAB_TOP))
        # as it came out of the box, its lug to the left: on edge in the EDM that puts the lug at the plate's right,
        # clear of the wire's path, and the bars over the comb's slots (a half turn here put them 156 mm off)
        p_c = seat + (-78.0, 0, 28.0)
        CAM_POCKET = [tuple(seat + (-900, -1500, 900)), tuple(seat + (0, 0, 60)), (0, 0, 1)]
        go(Tw=tilt(p_c + (0, 0, 120)), secs=2.2, cam=CAM_POCKET,
           labels=[("plate pocket", tuple(seat + (0, 0, 40)), (0.30, 0.66))])
        lin(tilt(p_c), 1.0)
        grip(0.0, 0.5)
        rb.release(amr.cab)
        status(sc, Plate="in its pocket on the MiR")
        lin(tilt(p_c - a_dir * 110), 0.8, labels=[])
        park(1.4, extra=RB.both(D_.door(0.0), W.ghost(0.0)))
        status(sc, Arm="parked")
        if STOP <= 2:
            return sc.save()

        # ---------------------------------------------------------------- 3. across the aisle to the wire EDM
        st["lbl"] = f"3/{n}"
        CAM_EDM = [tuple(E.world(E.PC + (-1300, -1900, 900))), tuple(E.world(E.PC + (60, -260, -40))), (0, 0, 1)]
        CAM_CUT = [tuple(E.world(E.PC + (330, -560, 180))), tuple(E.world(E.PC + (-15, -40, -5))), (0, 0, 1)]
        CAM_DRIVE = [(edm_x + 4200, -11500, 5200), (edm_x - 300, -3900, 600), (0, 0, 1)]
        st["cap"] = ("Across the aisle to the FANUC ROBOCUT wire EDM in the south row. The MiR250 turns on the spot, "
                     "then drives, speeding up and slowing down at its published 0.3 m/s^2, and turns again to dock "
                     "broadside, its arm towards the machine.")
        status(sc, Arm="parked", Plate="on the MiR", EDM="", Instron="")
        # round 11: 350 mm along the row first, then the turn: turning on the spot at the box, the MiR's corners (494 mm
        # from its centre) swept over the floor pipe, 60 mm in front of the row, 25-50 mm deep (the movers check)
        drive([(amr.pose[0] + 350.0, MIR_YN), (edm_x, MIR_YS)], end_heading=180.0, cam=CAM_DRIVE)
        st["cap"] = ("The tank is drained and its yellow door drops. The arm takes the plate by the lug, from above, turns "
                     "it on edge and pushes it onto a zero-point receiver on an angle plate, bars to the front.")
        status(sc, Arm="loading the plate", EDM="tank drained, door down")
        step(1.8, edm.move({"door": (0.0, 1.0), "~body": (0.0, 0.55)}), hold=0.1, cam=CAM_EDM,
             labels=[("work tank", tuple(E.world((-430, -1200, 1150))), (0.18, 0.28))])
        p_l = held_point(sc, "plate", (-78.0, 0, 28.0))
        go(Tw=A.down(p_l + (0, 0, 120), spin=0.0), secs=1.6, grip=0.0, labels=[])
        lin(A.down(p_l, spin=0.0), 0.9)
        grip(GRIP_LUG, 0.5)
        rb.grasp("plate")
        status(sc, Plate="in the gripper")
        lin(A.down(p_l + (0, 0, 160), spin=0.0), 0.9)
        into = edir((0, 1, 0))
        t_place = E.world(E.PC + (78.0, -28.0, 0.0))
        t_pre = E.world(E.PC + (78.0, -28.0 - 45.0, 0.0))
        t_out = E.world(E.PC + (78.0, -28.0 - 250.0, 80.0))
        go(Tw=lvl(t_out, into), secs=2.2)
        lin(lvl(t_pre, into), 1.4)
        lin(lvl(t_place, into), 0.6, hold=0.1,
            labels=[("zero-point receiver on an angle plate", tuple(E.world(E.PC + (-60, 30, 110))), (0.16, 0.30))])
        status(sc, Plate="clamped in the EDM, on edge")
        grip(0.0, 0.5)
        rb.release("edm_fix")
        lin(lvl(t_out, into), 1.2)
        park(1.4, labels=[])
        st["cap"] = ("The catch comb rises on its slide under the bars, its pads 0.5 mm under their feet: it waited "
                     f"{COMB_DROP:.0f} mm down in the table's window while the plate went on (our design).")
        step(1.2, lambda u: sc.gmat.__setitem__("edm_comb", T((0.0, 0.0, -COMB_DROP * (1.0 - u)))), hold=0.2,
             cam=CAM_CUT)
        st["cap"] = "Door up; the tank fills with deionised water, the dielectric. The plate is cut under water."
        status(sc, Arm="parked", EDM="tank filling")
        step(1.4, edm.move({"door": (1.0, 0.0), "~door": (0.0, 0.6)}))
        step(1.6, edm.move({"glow": (0.0, 0.55)}), hold=0.3)

        # ---------------------------------------------------------------- 4. the cut, into the comb
        st["lbl"] = f"4/{n}"
        bars = [f"bar{k}" for k in range(4)]
        zbars = [f"zbar{k}" for k in range(len(M.ZBARS))] if W.zbars else []
        bar_x = {g: E.local(held_point(sc, g, (0, 0, 3.0)))[0] for g in bars}
        bar_x.update({g: E.local(held_point(sc, g, (0, 0, 2.0)))[0] for g in zbars})
        print("bars in the EDM (x, as placed / as the comb was built):",
              {g: (round(bar_x[g], 1), round(B["bar_xs"][int(g[3:])], 1)) for g in bars}, flush=True)
        bar_z = {g: sorted(E.local(held_point(sc, g, (0, y, 3.0)))[2] for y in (-50.0, 50.0)) for g in bars}
        bar_z.update({g: sorted(E.local(held_point(sc, g, (0, y, 2.0)))[2] for y in (-3.0, 3.0)) for g in zbars})
        n_all = len(bars) + len(zbars)
        x_start, x_end = E.PC[0] - 95.0, E.PC[0] + 58.0
        freed = set()
        wall = ["edm fix/comb wall"]
        st["cap"] = ("The cut, the machine see-through: the brass wire (0.25 mm) runs between its guides 0.15 mm off the "
                     "plate and sparks its way through the base of each bar, the vertical ones first. A comb waits under "
                     "the flat bars, each settling 0.5 mm into its own slot as it comes free; a trough under each "
                     "vertical bar, which stands out level from the plate's face, catches it the same way.")
        status(sc, EDM="cutting")
        step(2.2, RB.both(edm.move({"~body": (0.55, 1.0), "~door": (0.6, 1.0 / 0.82)}),
                          lambda u: E.set_head(E.PC[0] - 150 + 55 * u), fade(wall, 1.0, 0.35)),
             hold=0.1, cam=CAM_CUT,
             labels=[("wire, drawn thicker", tuple(E.world((E.PC[0] - 95, E.wire_y, E.Z_HI - 25))), (0.20, 0.30)),
                     ("catch comb: a slot for each bar, pads, front wall (see-through)",
                      tuple(E.world((E.PC[0], E.PC[1] - 10, M.comb_floor_z(E.PC) + 20))), (0.18, 0.70))])

        def cut(u):
            x = x_start + (x_end - x_start) * u
            E.set_head(x)
            pts = []
            done = 0.0
            for g in bars + zbars:
                bx = bar_x[g]
                if bx - 5.0 < x < bx + 5.0:
                    z0, z1 = bar_z[g]
                    if g in zbars:                 # a vertical bar: across its 10 x 6 mm foot, at the plate's face
                        zz = np.linspace(z0, z1, 6)
                        y_sp = E.wire_y - 1.0
                    else:
                        zz = np.linspace(z0, z1, 26)
                        if abs(x - bx) > 3.0:
                            zz = zz[(zz < z0 + 34) | (zz > z1 - 34)]
                        y_sp = E.wire_y - M.E8_SUB["T"] - 1.0
                    jit = np.sin(np.arange(len(zz)) * 2.7 + u * 90.0) * 1.2
                    pts += [(x + j, y_sp, z) for j, z in zip(jit, zz)]
                if x >= bx + 5.0 and g not in freed:
                    freed.add(g)
                    rb.reparent(g, f"{edm.prefix}body")
                    sc.gmat[g] = T((0, 0, -M.COMB["gap"])) @ sc.gmat[g]      # it settles 0.5 mm onto its pad
                if g in freed:
                    done += 1
                elif x > bx - 5.0:
                    done += (x - (bx - 5.0)) / 10.0
            if pts:
                sc.set_mesh("edm sparks", pv.PolyData(np.array(pts)))
                sc.alpha["edm sparks"] = 1.0
            else:
                sc.alpha["edm sparks"] = 0.0
            status(sc, EDM=f"cutting: {done:.1f} of {n_all} bars")

        def cut_part(u0, u1):
            def up(u):
                cut(u0 + (u1 - u0) * u)
            return up
        step(3.4, cut_part(0.0, 0.36), hold=0.0, labels=[])
        save_still(sc, f"{NAME}_cut.png")
        step(5.6, cut_part(0.36, 1.0), hold=0.2)
        sc.alpha["edm sparks"] = 0.0
        st["cap"] = (f"Six cuts, {total:.0f} mm^2 in all (each flat bar along its length, about {total_xy / 4:.0f} mm^2; "
                     f"each vertical one across its 10 x 6 mm foot): at the 300 mm^2/min GF quotes as the most its CUT "
                     f"AM 500 does, at least {total / 300.0:.0f} minutes. The tank drains and the door drops.")
        status(sc, EDM="cut; draining")
        step(1.6, edm.move({"glow": (0.55, 0.0)}), hold=0.1)
        step(1.4, RB.both(edm.move({"door": (0.0, 1.0), "~body": (1.0, 0.55), "~door": (1.0 / 0.82, 0.0)}),
                          lambda u: E.set_head(x_end + (E.PC[0] + 125 - x_end) * u), fade(wall, 0.35, 1.0)),
             hold=0.1, cam=CAM_EDM)
        status(sc, EDM="door down")

        # ---------------------------------------------------------------- 5. uncap, eject, rinse, into the rack
        st["lbl"] = f"5/{n}"
        jar = B["jar_at"]
        jz1 = M.JAR["z1"] + M.JAR["ring_h"]
        # round 11: the knob taken 4 mm under its top, not 12: the fingertips reach 19 mm past the grasp point, so at
        # 12 they were 5 mm into the lid under the knob (the strict audit)
        lid_g = jar + (0, 0, jz1 + M.LID["t"] + M.LID["knob_h"] - 4.0)
        rest_top = B["rest_at"] + (0, 0, jz1)
        rest_g = rest_top + (0, 0, M.LID["t"] + M.LID["knob_h"] - 4.0)
        CAM_JAR = [tuple(jar + (-650, 900, 1500)), tuple(jar + (120, -150, 950)), (0, 0, 1)]
        st["cap"] = ("A rinse before the furnace: wire-cut parts come out wet with deionised water. The IPA jar beside "
                     "the EDM is kept capped; the arm lifts the lid off by its knob onto a rest.")
        status(sc, Arm="uncapping the IPA jar", Bar="four flat bars in the comb, two vertical in troughs, wet")
        go(Tw=A.down(lid_g + (0, 0, 90), spin=0.0), secs=1.6, grip=0.0, cam=CAM_JAR,
           labels=[("IPA jar, capped; an air knife on its rim", tuple(jar + (0, 0, jz1 + 60)), (0.20, 0.30)),
                   ("lid rest", tuple(rest_top + (0, 0, 40)), (0.70, 0.30))])
        lin(A.down(lid_g, spin=0.0), 0.6)
        grip(GRIP_KNOB)
        rb.grasp("ipalid")
        lin(A.down(lid_g + (0, 0, 40), spin=0.0), 0.5)
        lin(A.down(rest_g + (0, 0, 40), spin=0.0), 0.9)
        lin(A.down(rest_g, spin=0.0), 0.5)
        grip(0.0)
        rb.release(None)
        lin(A.down(rest_g + (0, 0, 70), spin=0.0), 0.5, labels=[])
        # round 11: the bars are handled with the specimen fingers from here (see section 7): with the 2F-85's own
        # fingertips, 27 mm tall and 31 mm thick at their root, the strict audit found them 3-12 mm in the next bar in
        # the comb and in the rack, 12 mm in the jar's air knife at every dip and 12-50 mm in the wire head
        fingers(True, cam_mir((-300.0, 40.0, 850.0)), "Before the bars, the arm fits fingers made for the specimen, as automated tensile cells "
                "do (ZwickRoell's roboTest C has a finger for each specimen thickness): two caps slip over the 2F-85's "
                "fingertips, each ending in a blade 8 mm tall, 74 mm further out (our design).")
        out_dir = -into                                # from the EDM towards the aisle
        lift = M.COMB["lift"]
        for i, k in enumerate(SPEC_ORDER):
            g = f"bar{k}"
            fast = 1.0 if i == 0 else 0.32
            end_up = -50.0 if held_point(sc, g, (0, -50.0, 3.0))[2] > held_point(sc, g, (0, 50.0, 3.0))[2] else 50.0
            grasp_local = (0.0, end_up - math.copysign(13.0, end_up), 3.0)
            if i == 0:
                st["cap"] = ("An ejector pin in the comb lifts the first bar 65 mm, its foot still in its slot, so the "
                             "gripper takes its upper end clear of the other three and of the plate's rim.")
            elif i == 1:
                st["cap"] = "The other three the same way (shown faster)."
            status(sc, Arm=f"flat bar {i + 1} of 4", Bar=f"flat bar {i + 1} of 4, wet")
            rb.reparent(g, f"edm_pin{k}")
            step(0.9 * fast, lambda u, k=k: sc.gmat.__setitem__(f"edm_pin{k}", T((0, 0, lift * u))),
                 cam=CAM_EDM if i == 0 else None, labels=[])
            p_top = held_point(sc, g, grasp_local)
            go(Tw=back(SF(lvl(p_top, into), C_SPEC_OPEN), 130.0), secs=1.6 * fast, grip=C_SPEC_OPEN)
            lin(SF(lvl(p_top, into), C_SPEC), 0.7 * fast)
            grip(C_SPEC, 0.4 * fast)
            take(g)
            lin(up_(SF(lvl(p_top, into), C_SPEC), 75.0), 0.6 * fast)
            lin(back(up_(SF(lvl(p_top, into), C_SPEC), 75.0), 160.0), 0.7 * fast,
                extra=lambda u, k=k: sc.gmat.__setitem__(f"edm_pin{k}", T((0, 0, lift * (1 - u)))))
            bottom = held_point(sc, g, (0.0, -end_up, 3.0))
            hang = held_point(sc, g, grasp_local)[2] - bottom[2]     # the fingers' grasp point over the bar's foot
            dip_dir = (jar[:2] - amr.world((0, 0, 0))[:2])
            p_dip_top = np.r_[jar[:2], M.JAR["z1"] + M.JAR["ring_h"] + hang + 30.0]
            # as deep as the blades allow: their lower edges 2 mm over the air knife (65 mm of the bar in the IPA)
            p_dip = np.r_[jar[:2], max(M.JAR["z0"] + 45.0 + hang,
                                       M.JAR["z1"] + M.JAR["ring_h"] + UA.SPEC_FINGER["blade_h"] / 2 + 2.0)]
            if i == 0:
                st["cap"] = ("It dips the bar in the IPA up to its upper end and draws it out slowly through the air knife "
                             "on the jar's rim, which blows it dry.")
            # the heading chosen at the dip itself, not over it: the caps behind the blades must miss the air line
            dip_dir, _ = pick_clear(lambda d: SF(lvl(p_dip, d), C_SPEC),
                                    [turned(dip_dir, a) for a in (0, 45, -45, 90, -90, 135, -135, 180)])
            go_clear(SF(lvl(p_dip_top, dip_dir), C_SPEC), secs=1.4 * fast, cam=CAM_JAR if i == 0 else None)
            lin(SF(lvl(p_dip, dip_dir), C_SPEC), 0.8 * fast, hold=0.4 * fast)
            status(sc, Bar=f"flat bar {i + 1} of 4, rinsing")
            lin(SF(lvl(p_dip_top, dip_dir), C_SPEC), 1.6 * fast)
            status(sc, Bar=f"flat bar {i + 1} of 4, rinsed and dry")
            slot = rack_w((RT.SPEC_X[RT.XY_SLOTS[3 - i]], 0.0, RT.TRAY["floor"]))
            toward = (0.0, 1.0)                               # pointing at the rack's fin side: the arm's body behind it
            p_in = np.r_[slot[:2], slot[2] + 0.5 + hang]
            if i == 0:
                st["cap"] = ("Into the rack on the MiR's cabinet, standing on end in a slot 25 mm deep: the arm carries "
                             "every specimen this way, by its upper end, from here to the Instron's grips.")
            toward = go_pick(lambda d: up_(SF(lvl(p_in, d), C_SPEC), 70.0), rack_dirs(), secs=1.6 * fast,
                             cam=CAM_EDM if i == 0 else None,
                             labels=[("specimen rack, in its pocket on the MiR", tuple(rack_w((0, 0, 140))),
                                      (0.40, 0.66))] if i == 0 else [])
            lin(SF(lvl(p_in, toward), C_SPEC), 0.7 * fast)
            give(g, "rack")
            grip(C_SPEC_OPEN, 0.35 * fast)
            lin(up_(SF(lvl(p_in, toward), C_SPEC_OPEN), 60.0), 0.5 * fast, labels=[])
        # round 9: the two vertical bars, out of their troughs (the upper one first: the lower one's free end is under
        # it). Each is taken by its free end, level, lifted 2 mm and drawn straight out to the front; then it hangs
        # under the gripper, pointing down, for the jar and the rack, its 10 mm width along the rack's slots.
        rack_x = sc.world("rack")[:3, :3] @ np.array([1.0, 0.0, 0.0])
        spin_rack = math.degrees(math.atan2(-rack_x[1], rack_x[0]))
        CAM_ZB = [tuple(E.world(E.PC + (-820, -640, 360))), tuple(E.world(E.PC + (-70, -90, -10))), (0, 0, 1)]
        for j, g in enumerate(zbars):
            fast = 1.0 if j == 0 else 0.4
            if j == 0:
                st["cap"] = ("The two vertical bars lie level in their troughs, standing out of the plate's face. The "
                             "gripper takes each by its free end, lifts it 2 mm and draws it straight out; turned to hang "
                             "under the gripper, it is rinsed the same way and stands in the rack's end slots.")
            status(sc, Arm=f"vertical bar {j + 1} of 2", Bar=f"vertical bar {j + 1} of 2, wet")
            p_end = held_point(sc, g, M.zbar_grasp_local())
            go(Tw=back(SF(lvl(p_end, into), C_SPEC_OPEN), 140.0), secs=1.6 * fast, grip=C_SPEC_OPEN,
               cam=CAM_ZB if j == 0 else None,
               labels=[("troughs under the vertical bars", tuple(E.world(E.PC + (-68, -60, -40))), (0.20, 0.70)),
                       ("vertical bars, cut at the foot", tuple(E.world(E.PC + (-68, -100, 40))), (0.24, 0.26))]
               if j == 0 else [])
            lin(SF(lvl(p_end, into), C_SPEC), 0.7 * fast)
            grip(C_SPEC, 0.4 * fast)
            take(g)
            lin(up_(SF(lvl(p_end, into), C_SPEC), 2.0), 0.3 * fast)
            lin(back(up_(SF(lvl(p_end, into), C_SPEC), 2.0), 118.0), 0.9 * fast, labels=[])
            hang = M.E8_SUB["L"] - 13.0             # the bar under the fingers' grasp point, pointing down
            p_dip_top = np.r_[jar[:2], M.JAR["z1"] + M.JAR["ring_h"] + hang + 30.0]
            # the blades' tips, 10 mm past the grasp point, 2 mm over the air knife
            p_dip = np.r_[jar[:2], max(M.JAR["z0"] + 55.0 + hang, M.JAR["z1"] + M.JAR["ring_h"] +
                                       UA.SPEC_FINGER["pad_l"] / 2 + 2.0)]
            sp, _ = pick_clear(lambda a: SF(A.down(p_dip, spin=a), C_SPEC), [spin_rack + a for a in (0, 180, 90, -90)])
            go_clear(SF(A.down(p_dip_top, spin=sp), C_SPEC), secs=1.8 * fast, cam=CAM_JAR if j == 0 else None)
            lin(SF(A.down(p_dip, spin=sp), C_SPEC), 0.8 * fast, hold=0.4 * fast)
            status(sc, Bar=f"vertical bar {j + 1} of 2, rinsing")
            lin(SF(A.down(p_dip_top, spin=sp), C_SPEC), 1.6 * fast)
            status(sc, Bar=f"vertical bar {j + 1} of 2, rinsed and dry")
            slot = rack_w((RT.SPEC_X[RT.Z_SLOTS[j]], 0.0, RT.TRAY["floor"]))
            p_in = np.r_[slot[:2], slot[2] + 0.5 + hang]
            sp = go_pick(lambda a: up_(SF(A.down(p_in, spin=a), C_SPEC), 70.0), [spin_rack, spin_rack + 180.0],
                         secs=1.6 * fast, cam=CAM_EDM if j == 0 else None)
            lin(SF(A.down(p_in, spin=sp), C_SPEC), 0.7 * fast)
            give(g, "rack")
            grip(C_SPEC_OPEN, 0.35 * fast)
            lin(up_(SF(A.down(p_in, spin=sp), C_SPEC_OPEN), 60.0), 0.5 * fast)
        fingers(False, None, "The specimen fingers go back in their stand on the MiR until the Instron: the tongs and the jar's lid want the 2F-85's own fingertips.")
        status(sc, Arm="recapping the IPA jar", Bar=f"{4 + len(zbars)} specimens in the rack, dry")
        st["cap"] = "The lid goes back on the jar, and the EDM's door comes up with the plate still in it, for the bin."
        go(Tw=A.down(rest_g + (0, 0, 80), spin=0.0), secs=1.4, grip=0.0, cam=CAM_JAR)
        lin(A.down(rest_g, spin=0.0), 0.5)
        grip(GRIP_KNOB)
        rb.grasp("ipalid")
        lin(A.down(rest_g + (0, 0, 40), spin=0.0), 0.5)
        lin(A.down(lid_g + (0, 0, 40), spin=0.0), 0.9)
        lin(A.down(lid_g, spin=0.0), 0.5)
        grip(0.0)
        rb.release(None)
        lin(A.down(lid_g + (0, 0, 80), spin=0.0), 0.5)
        park(1.4, extra=edm.move({"door": (1.0, 0.0), "~body": (0.55, 0.0)}))
        status(sc, Arm="parked", EDM="")
        if STOP <= 5:                  # round 11: CH5_TO=5, sections 1-5 alone (an audit in two halves, in parallel)
            if chk_mir is not None:
                chk_mir.save()
            return sc.save()

    if JUMP <= 6:
        # ---------------------------------------------------------------- 6. heat treatment on tray F
        st["lbl"] = f"6/{n}"
        fw = lambda p: rig_w(fur, p)                     # noqa: E731
        FP = I.FURNACE
        yf = -FP["D"] / 2
        y1 = yf + FP["panel_t"]
        cz = FP["mouth_z0"] + (FP["mouth_h"] - FP["ch_h"]) / 2
        t_ = RT.TRAY
        rack_in = (FP["mouth_x"], y1 + 70 + t_["fin_l"] + t_["D"] / 2, cz)          # the rack's floor centre, inside
        fin_off = np.array(RT.tray_fin_grasp())
        f_in = fw(np.array(rack_in) + fin_off)                                     # the fin's grasp point, inside
        f_out = fw(np.array(rack_in) + fin_off + (0, -200.0, 4.0))                 # drawn out in front of the mouth
        f_dir = rig_dir(fur, (0, 1, 0))                                            # into the furnace
        CAM_F = [tuple(fw((1150, -1450, 1250))), tuple(fw((-80, -330, 280))), (0, 0, 1)]
        CAM_TRAYF = [(1800, -5200, 2600), (300, -1200, 1250), (0, 0, 1)]
        st["cap"] = (f"To Shuttle 1, where tray F holds the furnace. The long drives are shown at {DRIVE_SHOWN:.0f}x; the "
                     "MiR turns in the gap between the two Shuttles and backs in, 350 mm further out than the dock, "
                     "to leave room for the tongs.")
        status(sc, Arm="parked", Rack="six specimens, on the MiR", Furnace="tray F, stored")
        drive([(edm_x, LANE), (PIVOT_X, LANE), (PIVOT_X, Y_TF)], end_heading=0.0, shown=DRIVE_SHOWN,
              cam=[(9000, -14500, 6800), (2500, -3500, 600), (0, 0, 1)])
        drive([(0.0, Y_TF)], reverse_last=True, cam=CAM_TRAYF)
        st["cap"] = ("Tray F comes to the opening: the furnace, the quench tank with its lift basket, the PX500 and the "
                     "mounting press.")
        L.fetch("F", st["lbl"], st["cap"], fast=0.55, cam=CAM_TRAYF, hold=0.2)
        fw = lambda p: rig_w(fur, p)                     # noqa: E731
        f_in = fw(np.array(rack_in) + fin_off)
        f_out = fw(np.array(rack_in) + fin_off + (0, -200.0, 4.0))
        f_dir = rig_dir(fur, (0, 1, 0))
        CAM_F = [tuple(fw((1150, -1450, 1250))), tuple(fw((-80, -330, 280))), (0, 0, 1)]
        # the tongs: the rack is always handled with them (a gripper on the fin would sit over the specimens, and the rack
        # comes out at 530 C)
        tong_g = (sc.world("tongs") @ np.r_[0.0, 0.0, 0.0, 1.0])[:3]
        st["cap"] = ("The rack is handled with tongs that ride on the MiR: 300 mm of steel between the gripper and the jaws, "
                     "so the gripper stays out of the furnace's mouth at 530 C. Squeezing the handle closes the jaws on "
                     "the rack's fin (our design).")
        status(sc, Arm="taking the tongs")
        go(Tw=A.down(tong_g + (0, 0, 110), spin=90.0), secs=1.6, grip=0.0, cam=CAM_TRAYF,
           labels=[("tongs", tuple(tong_g + (0, 0, 60)), (0.30, 0.62))])
        lin(A.down(tong_g, spin=90.0), 0.6)
        grip(GRIP_HANDLE)
        rb.grasp("tongs")
        lin(A.down(tong_g + (0, 0, 120), spin=90.0), 0.6, labels=[])
        Tg = np.linalg.inv(rb.tcp_world()) @ sc.world("tongs")          # the tongs in the TCP's frame, fixed from here on
        bite = M.tongs_bite()

        def tcp_for_bite(p_fin, d_in):
            """The TCP pose that puts the jaws' bite on p_fin with the shaft level along d_in."""
            y_ = np.array([d_in[0], d_in[1], 0.0])
            y_ /= np.linalg.norm(y_)
            z_ = np.array([0.0, 0.0, 1.0])
            Mt = np.eye(4)
            Mt[:3, 0], Mt[:3, 1], Mt[:3, 2] = np.cross(y_, z_), y_, z_
            Mt[:3, 3] = np.asarray(p_fin, float) - Mt[:3, :3] @ bite
            return Mt @ np.linalg.inv(Tg)
        # The door hinges on the furnace's right, where the quench tank stands, and its free edge sweeps 472 mm in front:
        # so the rack waits LEFT of the mouth whenever the door moves, and crosses to the tank in front of the closed door.
        f_left = f_out + rig_dir(fur, (-380.0, 0.0, 0.0))                          # clear of the door's sweep
        q_plate = rig_w(qt, (0.0, -5.0, RT.QUENCH["plate_z"]))
        q_fin = q_plate + rig_dir(qt, fin_off)          # the rack's floor on the plate's centre: its fin's grasp point
        q_dir = rig_dir(qt, (0, 1, 0))
        q_front = np.r_[q_fin[0], f_out[1], q_fin[2] + 40.0]                     # in front of the tank, at the door's front
        TL = lambda p_: tcp_for_bite(p_, f_dir)          # noqa: E731
        fin_now = (sc.world("rack") @ np.r_[fin_off, 1.0])[:3]
        st["cap"] = ("The jaws take the rack's fin on the MiR. The furnace door opens (an actuator, assumed: the NAT "
                     "15/65's door is opened by hand) while the rack waits to its left, out of the door's swing.")
        go(Tw=TL(fin_now + (0, -60.0, 30.0)), secs=1.8)
        lin(TL(fin_now), 0.6)
        rb.reparent("rack", "tongs")
        lin(TL(fin_now + (0, 0, 60.0)), 0.6)
        go(Tw=TL(f_left + (0, 0, 6.0)), secs=1.6)
        status(sc, Furnace="door open", Arm="loading the rack")
        step(1.6, fur.move({"door": (0.0, 1.0)}), cam=CAM_F,
             labels=[("Nabertherm NAT 15/65", tuple(fw((0, 0, 520))), (0.20, 0.20)),
                     ("quench tank, lift basket", tuple(rig_w(qt, (0, 0, 330))), (0.80, 0.24))])
        st["cap"] = "The rack slides in, its fin 70 mm past the door's insulating plug."
        lin(TL(f_out + (0, 0, 6.0)), 0.8, labels=[])
        lin(TL(f_in + (0, 0, 6.0)), 1.4)
        lin(TL(f_in), 0.4)
        rb.reparent("rack", f"{fur.prefix}body")
        lin(TL(f_in - f_dir * 70.0), 0.6)
        lin(TL(f_out), 0.8)
        lin(TL(f_left), 0.8)
        glow_f = B["glow"]["furnace"]
        st["cap"] = ("Door shut. The T6: solution treatment at 530 C (shown here 1 h, an assumption; DAL's schedule is "
                     "still to be set), then a water quench, then ageing at 160 C.")
        status(sc, Furnace="530 C, solution treatment", Arm="waiting with the tongs")
        step(1.4, fur.move({"door": (1.0, 0.0)}))
        step(4.0, RB.both(fade(glow_f, 0.0, 1.0), clock("Furnace at 530 C", hm, 0, 60)), hold=0.3)
        st["cap"] = ("The quench: door open, the tongs draw the rack out to the left, the door shuts, and the rack crosses "
                     "in front of it to the lift basket over the water.")
        status(sc, Furnace="530 C, door open", Arm="quench")
        step(1.4, RB.both(fur.move({"door": (0.0, 1.0)}), clock("Furnace at 530 C", lambda t: "1 h 00 min", 0, 1)),
             cam=CAM_F)
        lin(TL(f_out), 0.7)
        lin(TL(f_in - f_dir * 70.0), 0.5)
        lin(TL(f_in), 0.5)
        rb.reparent("rack", "tongs")
        sc.clock = ("Quench delay", "0 s")
        lin(TL(f_in + (0, 0, 4.0)), 0.3)
        lin(TL(f_out + (0, 0, 4.0)), 0.9, extra=clock("Quench delay", lambda t: f"{t:.0f} s", 0, 1))
        lin(TL(f_left + (0, 0, 4.0)), 0.7, extra=clock("Quench delay", lambda t: f"{t:.0f} s", 1, 2))
        step(1.2, RB.both(fur.move({"door": (1.0, 0.0)}), clock("Quench delay", lambda t: f"{t:.0f} s", 2, 3)))
        lin(TL(q_front), 1.4, extra=clock("Quench delay", lambda t: f"{t:.0f} s", 3, 5))
        lin(TL(q_fin + (0, 0, 40.0)), 0.8, extra=clock("Quench delay", lambda t: f"{t:.0f} s", 5, 6))
        lin(TL(q_fin), 0.4)
        rb.reparent("rack", f"{qt.prefix}lift")
        lin(TL(q_fin - q_dir * 60.0), 0.5)
        st["cap"] = ("The basket drops the rack into the water about 7 s after the door opened (an aluminium alloy wants "
                     "its quench within seconds; the figure here is ours, to check), then lifts it out.")
        status(sc, Rack="quenched in water")
        step(1.0, RB.both(qt.move({"lift": (0.0, 1.0)}), clock("Quench delay", lambda t: f"{t:.0f} s", 6, 7)),
             hold=0.6)
        sc.clock = None
        step(1.0, qt.move({"lift": (1.0, 0.0)}), hold=0.2)
        st["cap"] = "Back into the furnace, now at 160 C, for the ageing: by the left again, as the door opens."
        status(sc, Furnace="160 C, ageing", Arm="loading the rack")
        lin(TL(q_fin), 0.5)
        rb.reparent("rack", "tongs")
        lin(TL(q_fin + (0, 0, 40.0)), 0.5)
        lin(TL(q_front), 0.8)
        lin(TL(f_left + (0, 0, 4.0)), 1.4)
        step(1.2, fur.move({"door": (0.0, 1.0)}))
        lin(TL(f_out + (0, 0, 4.0)), 0.8)
        lin(TL(f_in + (0, 0, 4.0)), 1.0)
        lin(TL(f_in), 0.3)
        rb.reparent("rack", f"{fur.prefix}body")
        lin(TL(f_in - f_dir * 70.0), 0.5)
        lin(TL(f_out), 0.8)
        lin(TL(f_left), 0.8)
        st["cap"] = "Ageing at 160 C, then the furnace cools with its door shut."
        status(sc, Furnace="160 C, ageing", Arm="waiting with the tongs")
        step(1.2, fur.move({"door": (1.0, 0.0)}))
        step(4.0, RB.both(fade(glow_f, 1.0, 0.45), clock("Furnace at 160 C", hm, 0, 6 * 60)), hold=0.2)
        step(2.0, RB.both(fade(glow_f, 0.45, 0.0), clock("Furnace cooling to 40 C", hm, 0, 90)), hold=0.2)
        sc.clock = None
        st["cap"] = "Cool: the rack comes out and goes back in its pocket on the MiR, and the tongs on their rest."
        status(sc, Furnace="cool, door open", Arm="unloading the rack", Rack="T6")
        step(1.4, fur.move({"door": (0.0, 1.0)}))
        lin(TL(f_out), 0.8)
        lin(TL(f_in - f_dir * 70.0), 0.6)
        lin(TL(f_in), 0.6)
        rb.reparent("rack", "tongs")
        lin(TL(f_in + (0, 0, 4.0)), 0.3)
        lin(TL(f_out + (0, 0, 4.0)), 1.0)
        lin(TL(f_left + (0, 0, 4.0)), 0.8)
        seat_r = amr.world(M.rack_seat(CAB_TOP) + fin_off)
        go(Tw=TL(seat_r + (0, 0, 60.0)), secs=2.0, extra=fur.move({"door": (1.0, 0.0)}))
        lin(TL(seat_r), 0.6)
        rb.reparent("rack", amr.cab)
        lin(TL(seat_r + (0, -60.0, 30.0)), 0.6)
        go(Tw=A.down(tong_g + (0, 0, 120), spin=90.0), secs=1.6)
        lin(A.down(tong_g, spin=90.0), 0.6)
        grip(0.0)
        rb.release(amr.cab)
        lin(A.down(tong_g + (0, 0, 120), spin=90.0), 0.5)
        park(1.2)
        L.store("F", st["lbl"], "Tray F goes back to its slot.", fast=0.55, hold=0.1, cam=CAM_TRAYF)
        L.focus = None
        if STOP <= 6:                  # round 11: CH5_FROM=6 CH5_TO=6, section 6 alone
            if chk_mir is not None:
                chk_mir.save()
            return sc.save()

    # ---------------------------------------------------------------- 7. the Instron
    st["lbl"] = f"7/{n}"
    MIR_YS = WH.Y_FACE_S + 230.0 + P.MIR["W"] / 2
    ins_x = ins_axis[0]
    ins_in = rig_dir(ins, (0, 1, 0))                 # from the chamber's door towards the load string
    CAM_INS = [tuple(rig_w(ins, (1600, -2000, 1600))), tuple(rig_w(ins, (0, -250, 900))), (0, 0, 1)]
    # Round 9 (Sterling: "The angle and transparency at 32:20 is off. Can't see the tensile test happening"). Round 8's
    # CAM_GRIP sat 760 mm in front of the frame at x 480, behind the MiR's arm and the open door, and looked through
    # the closed door's see-through window. Now: from the front-right, 1.6 m off, over the MiR's end, and the test is
    # shown as a cutaway: the chamber's back half (r8_test's "chamber_cut") without its front half and door, so the
    # specimen, the grips, the pull rods and the AVE 2 in front are all in plain view and opaque.
    CAM_GRIP = [tuple(rig_w(ins, (900, -1300, 1300))), tuple(rig_w(ins, (0, -60, 870))), (0, 0, 1)]
    # the parked arm stands in front of the frame, so the test is seen from the right, low, past the right column's
    # front face and the arm: the cut face, the specimen, both grips, the pull rods and the AVE 2 beyond them
    CAM_TEST = [tuple(rig_w(ins, (1300, -900, 1150))), tuple(rig_w(ins, (0, 10, 870))), (0, 0, 1)]
    cut_on = {"chamber": (1.0, 0.0), "chamber_cut": (0.0, 1.0), "~chamber_door": (0.0, 1.0 / 0.82)}
    cut_off = {"chamber": (0.0, 1.0), "chamber_cut": (1.0, 0.0), "~chamber_door": (1.0 / 0.82, 0.0)}
    st["cap"] = (f"West along the aisle to the Instron 68FM-100 (shown at {DRIVE_SHOWN:.0f}x). Its 3119-608 chamber "
                 "stays round the load string for both tests; the room-temperature one runs with it cold.")
    status(sc, Arm="parked", Rack="six T6 specimens, on the MiR", Furnace="", Instron="")
    # Round 11: the 3119-608's left-hinged door is 550 mm wide and swings out 95 deg, its free edge 432 mm in front of
    # the frame (its hinge is 118 mm behind the frame's front). The MiR used to stop 230 mm off the row's face, so the
    # door went through its cabinet, the tongs and the arm's base every time it opened (the movers check, round 11).
    # It stops 500 mm off now, 68 mm clear of the door's sweep; the arm still reaches the load string (its base 1053 mm
    # from it). The set-up's dock mark at the Instron moved there too (setup_lab, 47219fc).
    MIR_YI = WH.Y_FACE_S + 500.0 + P.MIR["W"] / 2
    drive([(PIVOT_X, Y_TF), (PIVOT_X, LANE), (ins_x, LANE), (ins_x, MIR_YI)], end_heading=180.0,
          shown=DRIVE_SHOWN, cam=[(-2500, -14500, 6000), (-4300, -3800, 600), (0, 0, 1)])
    LOW_TOP = RT.LOWER_TOP
    I_CH = RT.CHAMBER
    spec_c = rig_w(ins, (0.0, 0.0, LOW_TOP - 30.0 + M.E8_SUB["L"] / 2))
    spec_top = spec_c + (0, 0, M.E8_SUB["L"] / 2)
    v_close = (LOW_TOP - 30.0 + M.E8_SUB["L"] - 30.0 - RT.UPPER_BOTTOM0) / I.INSTRON_FM["travel"]
    door_open = {"chamber_door": (0.0, 1.0)}
    door_shut = {"chamber_door": (1.0, 0.0)}
    glow_c = B["glow"]["chamber"]

    # Round 11 (Sterling, PR #318, 2026-11-13: "Insertion / removal of the tensile bars (and the halves) have another
    # collision. Not sure if the gripper has enough clearance. Maybe OK if angled, otherwise needs it's own tool/end
    # effector"). What collided: the bar's foot went into the lower grip on a slant (40 mm down while 20 mm forward), so
    # it cut through the grip's front before it reached the slot; the second bar went in under the upper grip, which the
    # first test had left 210 mm down; and each half has 20 mm free between its broken end and its grip, against the
    # 2F-85's 27 mm fingertips and 35 mm inner knuckles in a level grasp, so the fingers took each half partly inside its
    # grip. An angled grasp doesn't help: the 57 mm fingertip then reaches down or up instead (ur_arm.SPEC_FINGER). Now
    # the arm fits specimen fingers from a stand on the MiR and keeps them on for both tests: the bar goes straight down
    # into the jaws, the crosshead backs off 60 mm after the break so that each half comes out of its grip straight (the
    # lower up, the upper down) without meeting the other, and the crosshead goes back up before the next bar.
    def half_low(grp):
        """The lowest point of a half: its box in the bar's frame (10 mm wide, 6 thick, its 50 mm of the length)."""
        ys = (0.0, M.E8_SUB["L"] / 2) if grp.endswith("_b") else (-M.E8_SUB["L"] / 2, 0.0)
        return min(held_point(sc, grp, (x_, y_, z_))[2] for x_ in (-5.0, 5.0) for y_ in ys
                   for z_ in (0.0, M.E8_SUB["T"]))

    def test_one(k, hot):
        g = f"bar{k}"
        fastr = 1.0 if not hot else 0.6
        end_up = -50.0 if held_point(sc, g, (0, -50.0, 3.0))[2] > held_point(sc, g, (0, 50.0, 3.0))[2] else 50.0
        grasp_local = (0.0, end_up - math.copysign(13.0, end_up), 3.0)
        p_top = held_point(sc, g, grasp_local)
        foot0 = held_point(sc, g, (0.0, -end_up, 3.0))[2]
        st["cap"] = ("As in Instron's AT6 cells: the arm takes a specimen from the rack by its upper end, now with the "
                     "specimen fingers. The chamber's door opens (an actuator, assumed)." if not hot else
                     f"The second specimen goes in the same way, cold, and the door shuts. The chamber heats the grips "
                     f"and the specimen to {HOT_C:.0f} C and holds it there so the temperature evens out.")
        status(sc, Arm=f"taking specimen {'2' if hot else '1'}", Instron="chamber door opening")
        d_r = go_pick(lambda d: SF(back(lvl(p_top, d), 120.0), C_SPEC_OPEN), rack_dirs(), secs=1.6 * fastr,
                      grip=C_SPEC_OPEN, cam=CAM_INS, extra=ins.move(door_open))
        lin(SF(lvl(p_top, d_r), C_SPEC), 0.6 * fastr)
        grip(C_SPEC, 0.4)
        take(g)
        lin(up_(SF(lvl(p_top, d_r), C_SPEC), 120.0), 0.7 * fastr)
        hang = p_top[2] - foot0                     # the fingers' grasp point over the specimen's foot
        p_ins = np.r_[spec_c[:2], spec_c[2] - M.E8_SUB["L"] / 2 + hang]
        if not hot:
            st["cap"] = ("Straight down between the lower wedge grip's open jaws, which close on its foot: the blades "
                         "hold it 53 mm over the grip, and the 2F-85 itself stays in front of the grips.")
        go(Tw=back(up_(SF(lvl(p_ins, ins_in), C_SPEC), 60.0), 260.0), secs=1.8 * fastr, cam=CAM_GRIP,
           labels=[("AVE 2 video extensometer", tuple(rig_w(ins, (RT.AVE["x"], RT.AVE["y"], RT.AVE["z"] + 60))),
                    (0.14, 0.40)), ("lower wedge grip", tuple(rig_w(ins, (0, -40, LOW_TOP - 40))), (0.70, 0.70))])
        lin(up_(SF(lvl(p_ins, ins_in), C_SPEC), 60.0), 1.0 * fastr)
        lin(SF(lvl(p_ins, ins_in), C_SPEC), 0.8 * fastr)
        status(sc, Instron="lower grip closed")
        step(0.4 * fastr, ins.move(jaws("lower", 0.0, 1.0)), hold=0.05)
        give(g, f"{ins.prefix}body")
        grip(C_SPEC_OPEN, 0.4)
        lin(back(SF(lvl(p_ins, ins_in), C_SPEC_OPEN), 260.0), 1.0 * fastr, labels=[])
        park(1.4 * fastr)
        st["cap"] = ("The door shuts and the crosshead brings the upper grip down until it takes the specimen's upper "
                     "end; the AVE 2 reads the strain through the door's heated window, so nothing is clipped on by "
                     "hand." if not hot else st["cap"])
        step(1.0 * fastr, ins.move(door_shut))
        if not hot:
            st["cap"] = ("Drawn as a cutaway from here: the chamber's front half and its door, with the heated window the "
                         "AVE 2 reads through, are left out, so the specimen, the wedge grips and the pull rods show. The "
                         "crosshead brings the upper grip down until it takes the specimen's upper end.")
        step(1.0 * fastr, ins.move(cut_on), cam=CAM_TEST,
             labels=[("3119-608 chamber, cut away", tuple(rig_w(ins, (230, 0, I_CH["z1"] - 40))), (0.78, 0.20)),
                     ("AVE 2 video extensometer", tuple(rig_w(ins, (RT.AVE["x"], RT.AVE["y"], RT.AVE["z"] + 60))),
                      (0.14, 0.40)),
                     ("upper and lower wedge grips, on pull rods", tuple(rig_w(ins, (40, 0, LOW_TOP + 40))),
                      (0.74, 0.62))])
        step(2.0 * fastr, ins.move({"crosshead": (XH_REST, v_close)}), hold=0.1)
        step(0.4 * fastr, ins.move(jaws("upper", 0.0, 1.0)), hold=0.1)
        status(sc, Instron="both grips closed")
        if hot:
            status(sc, Instron=f"heating to {HOT_C:.0f} C")
            step(3.0, RB.both(fade(glow_c, 0.0, 0.8), clock("Chamber", lambda t: f"{t:.0f} C", 23, HOT_C)), hold=0.1)
            step(1.6, clock("Chamber, soaking", lambda t: f"{HOT_C:.0f} C, {t:.0f} min", 0, 15), hold=0.2)
        sc.ss_hot = hot
        pts = SS_HOT_PTS if hot else SS_PTS
        hi_up = held_point(sc, g, (0, 25.0, 3.0))[2] > held_point(sc, g, (0, -25.0, 3.0))[2]
        st["cap"] = (f"The pull: the crosshead rises at a constant rate and the load cell reads the force. The curve is "
                     f"illustrative, not a measurement ({'assumed' if hot else SS['src']}).")

        def pull(u):
            sc.ss_u = u
            e, s_ = pts[int(round(u * (len(pts) - 1)))]
            status(sc, Instron=f"{s_ * AREA / 1000:5.1f} kN, extension {e * M.E8_SUB['G']:4.2f} mm")
            ins.move({"crosshead": (v_close, v_close + e * M.E8_SUB["G"] * 1.6 / I.INSTRON_FM["travel"])})(1.0)
        sc.ss_u = 0.0
        sc.ss_broken = False
        step(7.0 * fastr, pull, hold=0.2, cam=CAM_TEST)
        sc.ss_broken = True
        rb.reparent(f"{g}_b", f"{ins.prefix}crosshead" if hi_up else f"{ins.prefix}body")
        if not hi_up:
            rb.reparent(g, f"{ins.prefix}crosshead")
        v1 = ins.v["crosshead"]
        status(sc, Instron="broken", Bar="two halves")
        st["cap"] = (f"Broken. The crosshead backs off {BACK_OFF:.0f} mm, so that each half can come out of its grip "
                     "without meeting the other." if not hot else
                     "Broken. The chamber cools before the door opens: the gripper isn't made for hot work.")
        step(1.4, RB.both(ins.move({"crosshead": (v1, v1 + BACK_OFF / I.INSTRON_FM["travel"])}),
                          fade(glow_c, 0.8 if hot else 0.0, 0.0),
                          clock("Chamber", lambda t: f"{t:.0f} C", HOT_C, 40) if hot else None), hold=1.0, still=True)
        sc.clock = None
        sc.ss_u = None
        # the halves out: the lower one (in the lower grip) first, lifted out of its jaws, then the upper one, lowered
        up_grp = f"{g}_b" if hi_up else g
        dn_grp = g if hi_up else f"{g}_b"
        step(0.8, ins.move(cut_off), labels=[])
        step(1.0, ins.move(door_open), cam=CAM_GRIP)
        for grp, where in ((dn_grp, "lower"), (up_grp, "upper")):
            # HALF_IN mm into the half from its broken end (the bar's centre, y = 0 in its own frame), on its axis: the
            # blades' 8 mm then clear the grip and the broken end by 6 mm each
            p_h = held_point(sc, grp, (0.0, HALF_IN if grp.endswith("_b") else -HALF_IN, 3.0))
            st["cap"] = (("Each half as its grip lets go: the lower one lifted out of its jaws, the upper one lowered "
                          "out of its own. The blades take each 10 mm from its broken end, 6 mm clear of the grip; the "
                          "room-temperature halves lie in a cradle on the MiR, their fracture surfaces touching "
                          "nothing, for fractography in chapter 7.") if not hot else
                         "The hot test's halves go down the scrap chute right of the grips, as the AT6 drops them.")
            status(sc, Arm=f"taking the {where} half")
            go(Tw=back(SF(lvl(p_h, ins_in), C_HALF_OPEN), 240.0), secs=1.4, grip=C_HALF_OPEN, cam=CAM_GRIP)
            lin(SF(lvl(p_h, ins_in), C_HALF), 0.7)
            grip(C_HALF, 0.4)
            take(grp)
            status(sc, Instron=f"{where} grip open")
            step(0.3, ins.move(jaws(where, 1.0, 0.0)), hold=0.05)
            dz = HALF_OUT if where == "lower" else -HALF_OUT
            lin(up_(SF(lvl(p_h, ins_in), C_HALF), dz), 0.6)
            lin(back(up_(SF(lvl(p_h, ins_in), C_HALF), dz), 240.0), 0.9)
            if hot:
                chute = rig_w(ins, (RT.CHUTE["x"], RT.CHUTE["y"], I.INSTRON_FM["base_h"] + 260.0))
                go(Tw=SF(lvl(chute, ins_in), C_HALF), secs=1.4)
                give(grp, None)
                grip(C_HALF_OPEN, 0.3)
                # it drops onto the chute's floor (its top 626 mm up at the chute's middle: 120 + 6 mm over the base,
                # tilted 18 deg about it, so 1.6 mm higher 5 mm to one side) and slides away into the bin
                floor_z = rig_w(ins, (RT.CHUTE["x"], RT.CHUTE["y"], I.INSTRON_FM["base_h"] + 126.0))[2] + 3.0
                drop = max(0.0, half_low(grp) - floor_z)
                fall0 = sc.gmat[grp].copy()
                step(0.6, lambda u, grp=grp, fall0=fall0, drop=drop: sc.gmat.__setitem__(
                    grp, T((0, 0, -drop * u * u)) @ fall0), hold=0.1)
                for nm in sc.members(grp):
                    sc.alpha[nm] = 0.0
            else:
                # into the halves cradle on the MiR, lying flat: turned level -> pointing down about the fingers' axis,
                # so the half comes down horizontal, along the channel; the blades go into the relief across it
                ch = amr.world(M.cradle_seat(CAB_TOP, 0 if where == "upper" else 1)) + (0, 0, M.E8_SUB["T"] / 2 + 0.5)
                sp = go_pick(lambda a: up_(SF(A.down(ch, spin=a), C_HALF), 70.0), [0.0, 180.0], secs=1.8,
                             cam=cam_mir((250.0, 150.0, 820.0)) if where == "lower" else None)
                lin(SF(A.down(ch, spin=sp), C_HALF), 0.6)
                give(grp, amr.cab)
                grip(C_HALF_REL, 0.3)
                lin(up_(SF(A.down(ch, spin=sp), C_HALF_REL), 70.0), 0.5)
        park(1.2)                               # round 11: then the door: shutting as the arm left, it met the arm
        st["cap"] = "The door shuts and the crosshead goes back up, so the next specimen goes in under an open grip."
        step(1.0, ins.move(door_shut))
        step(1.2, ins.move({"crosshead": (None, XH_REST)}), hold=0.1)

    fingers(True, cam_mir((-300.0, 40.0, 850.0)), "The specimen fingers go back on for the two tensile tests: each half has 20 mm free "
            "between its broken end and its grip, where the 2F-85's own 27 mm fingertips don't fit.")
    test_one(TEST, hot=False)
    test_one(HOT, hot=True)
    fingers(False)
    st["cap"] = ("Done: printed flat and vertical, depowdered, cut, rinsed, heat treated and pulled at two temperatures, "
                 "every arm move collision-checked. The comb, the troughs, the clamps, the jar's lid, the rack, the tongs, "
                 "the quench basket and the specimen fingers are our designs.")
    status(sc, Arm="parked")
    step(3.0, None, hold=3.0, cam=CAM_WIDE, labels=lbl[:3])
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    if chk_mir is not None:
        chk_mir.save()
    info = sc.save()
    if not PREVIEW and not scene.AUDIT:
        meta_path = OUT / f"{NAME}.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            meta.update(numbers=dict(specimen=M.E8_SUB, plate=M.PLATE, cut_area_mm2=round(total),
                                     stress_strain=SS, stress_strain_hot=SS_HOT, hot_C=HOT_C, mir_speed_mm_s=MIR_SPEED,
                                     mir_accel_mm_s2=P.MIR_ACCEL, comb=M.COMB, jar=M.JAR, rack=RT.TRAY,
                                     quench=RT.QUENCH, tongs=M.TONGS),
                        data=dict(curve="illustrative: through AddUp's as-built values (room temperature) and an "
                                        "assumed 60 % of them at 200 C; not measured"))
            meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return info


if __name__ == "__main__":
    out = movie()
    print(out, flush=True)
    if not PREVIEW and not scene.AUDIT and NAME == "alloy_workflow":
        mp4 = OUT / "mp4" / f"{NAME}.mp4"
        if mp4.exists():
            # round 9: 380 px at 2 fps, gifsicle --lossy=130: 4.7 MB for the 385 s chapter (under the 4.9 MB cap);
            # 640 px at 5 fps came out at 24.7 MB and took minutes in gifsicle
            print(line.mp4_to_gif(mp4, OUT / f"{NAME}.gif", fps=2, width=380, lossy=130), flush=True)
