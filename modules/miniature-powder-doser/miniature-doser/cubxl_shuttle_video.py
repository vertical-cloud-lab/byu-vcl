"""Ben's towed doser on the CubXL, start to finish, as a video in the style of byu-vcl PR 278's cubxl-cu-spot.mp4.
Writes cubxl_shuttle_workflow.mp4 (1280 x 720, 30 fps), a GIF of the run (640 x 360, about 3x the video's speed), the
chapters and captions with their times (cubxl_shuttle_workflow.json) and stills, next to this file.

What it shows, in order:
1. The real CubXL, empty (Ben's photo from byu-vcl#133), Ben's sketch of the idea and his photo of the right Y rail
   (byu-vcl PR 274).
2. cubxl_shuttle.py's model of the same machine, seen from the photo's side, turning to the working view.
3. Each part the doser adds, then what it needs on the gantry, and the head's tools, placed one at a time with a name.
4. What is done by hand before a run (cards): load and weigh the auger, calibrate on the bench, tare the vials, check
   the coupling.
5. The run, step by step: home and couple, tow outlet up, tilt, dose, tilt back, the next vial, the head passing in
   front, back to the dock, release. The part doing the work is outlined in orange and lit in the panel at the top
   left, its target is ringed, and a panel at the top right keeps the dose log.
6. After the run: weigh the vials and the cartridge (a card), and an outro.

All the geometry is cubxl_shuttle.py's: the one-servo doser from PR 176's STEP, Cubware's PandaDeck.step, and boxes
for the rest of the CubXL, placed from Ben's measurements of 2026-10-19. The doses, the rate and the heaps in the vials
come from the README's estimates (about 380 mg per turn, 10 mg/s, 1.2 g/cm3), not from measurements. Needs what
cubxl_shuttle.py needs, plus imageio and imageio-ffmpeg:
    POWDER_DOSER=/tmp/powder-doser/cad/text-to-cad PANDA_DECK=/tmp/PandaDeck.step \
        xvfb-run -a -s "-screen 0 1920x1080x24" python cubxl_shuttle_video.py        # the MP4, GIF and stills
    ... python cubxl_shuttle_video.py --stills 3,40,70     # PNG stills at these seconds, in /tmp, no video
    ... python cubxl_shuttle_video.py --part 0/4  (to 3/4, in parallel), then --assemble 4
"""
from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageOps

import cubxl_shuttle as CS
from module_views import D, HERE, font

W, H, FPS = 1280, 720, 30
GW, GH = 640, 360
NAME = "cubxl_shuttle_workflow"
MEDIA = HERE / "media"
TMP = Path(tempfile.gettempdir())

ORANGE = (235, 104, 52)
INK, INK2, MUTED, RULE, PAPER = (11, 11, 11), (82, 81, 78), (137, 135, 129), (225, 224, 217), (246, 245, 241)
FADED = 0.22                                            # the right Y rail, the gantry's right side and the beam

HOME = CS.TRAVEL[1]                                     # capper y (CubOS) at home: GRBL homes to +y, the back
ROWS = CS.lane_rows()                                   # the vials' centres, machine y
FY0 = CS.beam_front(0.0)                                # the moving parts are built for capper (0, 0), then moved
RHO, RATE, PER_TURN = 1.2, 10.0, 380.0                  # mg/mm3, mg/s, mg per turn: the README's estimates
REPOSE = math.radians(30.0)                             # the heaps' angle of repose (assumed)
PLAN = [(0, 20.0), (1, 50.0), (2, 100.0), (3, 200.0), (5, 50.0)]   # (vial, mg): a dose series, then a back vial
TOOLS = {"gantry": "Gantry (Y)", "magnets": "Magnets", "servo": "Tilt servo", "auger": "Auger + vibration",
         "head": "Head (X)"}


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def tilt_about(p, deg):
    """4x4: turn `deg` about the x axis through p. Positive lifts the cap end, outlet down, as in doser_cad."""
    a = math.radians(deg)
    r = np.eye(4)
    r[1:3, 1:3] = [[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]
    return T(*p) @ r @ T(*(-np.asarray(p, float)))


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


HINGE0 = CS.doser_pose(FY0, 0.0)[1]                     # the hinge, coupled to a gantry at capper y = 0


def at(i):
    """Capper y (CubOS) that puts the tip, dosing, over vial i."""
    return ROWS[i] - CS.REACH0[1] - CS.tip_y(0.0)


def tip(dty, deg):
    """The capillary's tip (machine) for a doser left at capper y `dty`, at tilt `deg`."""
    a = math.radians(deg)
    return HINGE0 + np.array([0.0, dty - CS.S * math.cos(a), -CS.S * math.sin(a)])


def heap(mg):
    """Radius and height (mm) of a cone of `mg` of powder at RHO and REPOSE."""
    r = (3.0 * mg / RHO / (math.pi * math.tan(REPOSE))) ** (1 / 3) if mg > 0 else 0.0
    return r, r * math.tan(REPOSE)


# ------------------------------------------------------------------ the scene
class Scene:
    """cubxl_shuttle.scene's parts as persistent actors, each with a placement group and a way of moving: static, with
    the gantry (y), with the head (x, y), with the shuttle (y), or with the doser's module (y, then the tilt)."""

    def __init__(self):
        pv.global_theme.allow_empty_mesh = True
        self.pl = pv.Plotter(off_screen=True, window_size=(W, H), lighting="light_kit")
        self.pl.set_background("#f6f5f1")
        self.pl.enable_depth_peeling(6)
        self.pl.enable_anti_aliasing("fxaa")
        self.actors, self.meshes, self.colors, self.opac, self.group, self.kind, self.fade = {}, {}, {}, {}, {}, {}, {}
        self.sil = {}
        self.build()

    def add(self, key, group, kind, mesh, color, spec=0.3, opacity=1.0, fade=False, **kw):
        kw.setdefault("smooth_shading", True)
        a = self.pl.add_mesh(mesh, color=color, specular=spec, specular_power=20, opacity=opacity, **kw)
        self.actors[key], self.meshes[key], self.colors[key], self.opac[key] = a, mesh, color, opacity
        self.group[key], self.kind[key], self.fade[key] = group, kind, fade
        return a

    def build(self):
        A, box, cyl = self.add, CS.box, CS.cyl
        A("deck", "machine", "static", CS.deck(), (0.86, 0.90, 0.94), 0.5, 0.55)
        for i, (x0, x1) in enumerate(CS.Y_RAILS):
            A(f"yrail{i}", "machine", "static", box((x0, x1), (-40, 530), (-50, -2)), CS.ALU, fade=bool(i))
            A(f"yscrew{i}", "machine", "static", cyl(((x0 + x1) / 2, 245, -10), (0, 1, 0), 6, 560), CS.STEEL, 0.5,
              fade=bool(i))
            for y0 in (-50, 530):
                A(f"ycorner{i}{y0}", "machine", "static", box((x0 - 5, x1 + 5), (y0, y0 + 10), (-55, 30)), CS.BLUE,
                  fade=bool(i))
        for y0 in (-40, 490):
            A(f"xmember{y0}", "machine", "static", box((-CS.RAIL_GAP, CS.DECK[0] + CS.RAIL_GAP), (y0, y0 + 40),
                                                       (-50, -10)), CS.ALU)
        fy = FY0
        for i, ((p0, p1), (r0, r1)) in enumerate(zip(CS.PLATE_X, CS.Y_RAILS)):
            o0, o1 = (r0 - 14.0, r0 - 4.0) if i == 0 else (r1 + 4.0, r1 + 14.0)
            for j, (q0, q1) in enumerate(((p0, p1), (o0, o1))):
                A(f"gplate{i}{j}", "machine", "gantry", box((q0, q1), (fy - 35, fy + 75), (-35, 75)), CS.ALU,
                  fade=bool(i))
            for k, wy in enumerate((fy - 15, fy + 20, fy + 55)):
                A(f"wheel{i}{k}", "machine", "gantry", cyl(((r0 + r1) / 2, wy, 10), (1, 0, 0), 11, r1 - r0 - 4),
                  CS.BLACK, 0.2, fade=bool(i))
            A(f"upright{i}", "machine", "gantry", box((min(p0, o0), max(p1, o1)), (fy - 10, fy + 50),
                                                      (75, CS.BEAM_UNDER + CS.BEAM_TALL)), CS.BLUE, fade=bool(i))
        A("beam", "machine", "gantry", box((CS.PLATE_X[0][1], CS.PLATE_X[1][0]), (fy, fy + CS.BEAM_DEPTH),
                                           (CS.BEAM_UNDER, CS.BEAM_UNDER + CS.BEAM_TALL)), CS.ALU, fade=True)
        # the head, built at capper (0, 0): the block, the backboard, the capper and the pipette
        cx, cy = CS.REACH0[0], fy - CS.BEAM_AHEAD
        bb = fy - (CS.BEAM_AHEAD - CS.HEAD_AHEAD)
        A("block", "machine", "head", box((cx - 40, cx + 45), (bb + 12, fy),
                                          (CS.HEAD_UNDER, CS.BEAM_UNDER + CS.BEAM_TALL + 30)), CS.ALU)
        A("backboard", "machine", "head", box((cx - 200, cx + 50), (bb, bb + 10), (150, 330)), CS.BLACK, 0.1)
        A("capper", "capper", "head", cyl((cx, cy, 140), (0, 0, 1), 24, 70), CS.BLACK, 0.2)
        A("capper_mount", "capper", "head", box((cx - 10, cx + 10), (cy + 20, bb), (150, 170)), CS.BLACK, 0.1)
        px, py = cx + CS.PIPETTE[0], cy + CS.PIPETTE[1]
        A("pip_body", "pipette", "head", box((px - 18, px + 18), (py - 15, bb), (150, 290)), (0.88, 0.88, 0.86))
        A("pip_shaft", "pipette", "head", cyl((px, py, 135), (0, 0, 1), 6, 30), (0.88, 0.88, 0.86))
        A("pip_tip", "pipette", "head", pv.Cone(center=(px, py, 112), direction=(0, 0, -1), height=16, radius=3.5,
                                                resolution=24), (0.92, 0.92, 0.9))
        self.capper_xyz, self.pip_xyz = np.array([cx, cy, 105.0]), np.array([px, py, 104.0])
        A("tab", "tab", "gantry", box((477.0, CS.PLATE_X[1][0]), (fy - 6.0, fy), (24, 78)), CS.STEEL, 0.5)
        # the row of vials, open, and a heap of powder in each (scaled per frame)
        r, h, z0 = CS.VIAL[0] / 2, CS.VIAL[1], CS.VIAL[2]
        A("holder", "vials", "static", box((CS.LANE_X - 20, CS.LANE_X + 20), (ROWS[0] - 22, ROWS[-1] + 22),
                                           (0, z0)), (0.93, 0.93, 0.95), 0.2)
        cone = pv.Cone(center=(0, 0, math.tan(REPOSE) / 2), direction=(0, 0, 1), height=math.tan(REPOSE), radius=1.0,
                       resolution=40)
        for i, y in enumerate(ROWS):
            glass = pv.Cylinder(center=(CS.LANE_X, y, z0 + h / 2), direction=(0, 0, 1), radius=r, height=h,
                                resolution=48, capping=False)
            bottom = pv.Disc(center=(CS.LANE_X, y, z0 + 1.5), inner=0.0, outer=r, normal=(0, 0, 1), c_res=48)
            A(f"vial{i}", "vials", "static", pv.merge([glass.triangulate(), bottom.triangulate()]), CS.GLASS, 0.6,
              0.4)
            A(f"heap{i}", "fx", "static", cone, (0.60, 0.61, 0.64), 0.4)
        # the rail and the dock on the deck's right margin
        end = CS.beam_front(HOME) + CS.TIP_GAP + CS.S + CS.CARRIAGE_Y + CS.CARRIAGE[1] / 2
        start = CS.beam_front(0.0) + CS.TIP_GAP + CS.S + CS.CARRIAGE_Y - CS.CARRIAGE[1] / 2 - 5.0
        A("rail", "rail", "static", box(CS.RAIL_X, (start, end + 1.0), CS.RAIL_Z), CS.STEEL)
        A("dock", "dock", "static", box(CS.RAIL_X, (end + 1.0, end + 6.0), (0, 30)), (0.2, 0.2, 0.22))
        self.dock_xyz = np.array([sum(CS.RAIL_X) / 2, end + 3.5, 30.0])
        # the doser at level, coupled at capper y = 0: its module tilts, its bracket rides with the shuttle
        meshes, hinge = CS.doser_pose(FY0, 0.0)
        for (grp, mat), m in meshes.items():
            color, spec = D.MATERIALS[mat]
            A(f"{grp}:{mat}", "doser", "module" if grp == "module" else "shuttle", m, color, spec)
        for j, (m, c) in enumerate(CS.shuttle_parts(hinge)):
            A(f"shuttle{j}", "shuttle", "shuttle", m, c)
        for z in (34.0, 62.0):
            A(f"magnet{z:g}", "magnets", "shuttle", cyl((490.0, FY0 + CS.MAGNET_L / 2, z), (0, 1, 0), CS.MAGNET_R,
                                                        CS.MAGNET_L), CS.MAGNET_OFF, 0.5)
        A("magblock", "magnets", "shuttle", box((477.0, 503.0), (FY0 + CS.MAGNET_L, FY0 + CS.MAGNET_L + 6),
                                                (CS.CARRIAGE[2] + 6.0, 78)), CS.ALU)
        # the falling powder, and the ring that marks a target
        self.n_p = 90
        self.stream = pv.PolyData(np.zeros((self.n_p, 3)))
        A("stream", "fx", "static", self.stream, (0.42, 0.43, 0.47), 0.2, style="points", point_size=4.0,
          render_points_as_spheres=True, smooth_shading=False)
        ring = pv.Disc(center=(0, 0, 0), inner=0.82, outer=1.0, normal=(0, 0, 1), r_res=1, c_res=72)
        A("marker", "fx", "static", ring, "#eb6834", 0.0, 0.95, lighting=False, smooth_shading=False)
        self.lit_sets = {"gantry": ["tab"], "magnets": ["magnet34", "magnet62"],
                         "servo": ["bracket:vac_motor", "module:alu"], "auger": ["module:ss_am", "module:vac_motor"],
                         "head": ["capper", "pip_body"]}

    def silhouette(self, key):
        if key in self.sil:
            return self.sil[key]
        import vtk
        clean = self.meshes[key].triangulate()
        clean = pv.PolyData(clean.points.copy(), clean.faces.copy())
        self.sil_src = getattr(self, "sil_src", []) + [clean]
        alg = vtk.vtkPolyDataSilhouette()
        alg.SetInputData(clean)
        alg.SetCamera(self.pl.renderer.GetActiveCamera())
        alg.SetProp3D(self.actors[key])
        alg.SetEnableFeatureAngle(True)
        alg.SetFeatureAngle(70)
        alg.BorderEdgesOn()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(alg.GetOutputPort())
        mapper.SetResolveCoincidentTopologyToPolygonOffset()
        mapper.SetRelativeCoincidentTopologyLineOffsetParameters(0, -66000)
        act = vtk.vtkActor()
        act.SetMapper(mapper)
        p = act.GetProperty()
        p.SetColor(*[c / 255 for c in ORANGE])
        p.SetLineWidth(3.5)
        p.LightingOff()
        self.pl.renderer.AddActor(act)
        self.sil[key] = act
        return act

    def set_state(self, st):
        mats = {"static": np.eye(4), "gantry": T(0, st["ty"], 0), "head": T(st["tx"], st["ty"], 0),
                "shuttle": T(0, st["dty"], 0), "module": T(0, st["dty"], 0) @ tilt_about(HINGE0, st["deg"])}
        hidden, drop, fade = st.get("hidden", set()), st.get("drop", {}), st.get("fade", 1.0)
        lit = {k for tool in st.get("lit", ()) for k in self.lit_sets[tool]}
        for k, a in self.actors.items():
            g = self.group[k]
            a.user_matrix = T(0, 0, drop.get(g, 0.0)) @ mats[self.kind[k]]
            a.visibility = g not in hidden
            if self.fade[k]:
                a.prop.opacity = self.opac[k] + (FADED - self.opac[k]) * fade
            col = self.colors[k]
            if k.startswith("magnet") and k != "magblock":
                col = CS.MAGNET_ON if st.get("magnets") else CS.MAGNET_OFF
            if isinstance(col, str):
                col = tuple(int(col.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
            on = k in lit and a.visibility
            if on:
                col = tuple(0.55 * c + 0.45 * o / 255 for c, o in zip(col, ORANGE))
            a.prop.color = col
            if on or k in self.sil:
                s = self.silhouette(k)
                s.SetVisibility(on)
                s.SetUserMatrix(a.GetUserMatrix())
        # the heaps, and the stream while a dose runs
        for i, mg in enumerate(st.get("doses", [0.0] * len(ROWS))):
            a = self.actors[f"heap{i}"]
            r, _ = heap(mg)
            a.visibility = bool(r > 0.05)
            a.user_matrix = T(CS.LANE_X, ROWS[i], CS.VIAL[2] + 1.5) @ np.diag([r, r, r, 1.0])
        s = st.get("stream")
        a = self.actors["stream"]
        a.visibility = s is not None
        if s is not None:
            i, t_on, mg = s
            p0 = tip(st["dty"], st["deg"])
            z1 = CS.VIAL[2] + 1.5 + heap(mg)[1]
            k = np.arange(self.n_p)
            ph = (t_on * 1.9 + k / self.n_p) % 1.0
            rng = np.random.default_rng(7)
            jx, jy = rng.normal(0, 0.9, self.n_p), rng.normal(0, 0.9, self.n_p)
            pts = np.c_[p0[0] + jx * ph, p0[1] + jy * ph, p0[2] - 1.6 - (p0[2] - 1.6 - z1) * ph ** 2]
            pts[ph > t_on * 1.9] = p0 - np.array([0.0, 0.0, 1.6])          # not yet out of the capillary
            self.stream.points = pts
            self.stream.Modified()
        tgt = st.get("target")
        m = self.actors["marker"]
        m.visibility = tgt is not None
        if tgt is not None:
            x, y, z, r = tgt
            pulse = 1.0 + 0.12 * math.sin(st.get("t", 0.0) * 2 * math.pi * 1.4)
            m.user_matrix = T(x, y, z + 0.4) @ np.diag([r * pulse, r * pulse, 1, 1])

    def set_camera(self, cam):
        pos, foc, angle = cam
        c = self.pl.camera
        c.position, c.focal_point, c.up = tuple(pos), tuple(foc), (0.0, 0.0, 1.0)
        c.view_angle = angle
        self.pl.renderer.ResetCameraClippingRange()

    def project(self, xyz):
        import vtk
        co = vtk.vtkCoordinate()
        co.SetCoordinateSystemToWorld()
        co.SetValue(*[float(v) for v in xyz])
        x, y = co.GetComputedDoubleDisplayValue(self.pl.renderer)
        return x, H - y

    def frame(self):
        self.pl.render()
        return self.pl.screenshot(return_img=True)


# ------------------------------------------------------------------ cameras (position, focus, view angle)
def cam_dir(focus, direction, dist, angle=30.0):
    v = np.asarray(direction, float)
    return (np.asarray(focus, float) + dist * v / np.linalg.norm(v), np.asarray(focus, float), angle)


FRONT = (np.array([240.0, -1500.0, 420.0]), np.array([240.0, 245.0, 70.0]), 26.0)
OVERVIEW = cam_dir((250.0, 255.0, 60.0), (1.0, -0.95, 0.85), 1700.0)
RUN_WIDE = cam_dir((320.0, 300.0, 85.0), (1.0, -0.9, 0.8), 1080.0)


def near(i, dist=430.0):
    """Close on vial i, from the front left and a little above: the tube at its tilt, the capillary and the vial
    under it, with nothing of the head in the way."""
    return cam_dir((CS.LANE_X, ROWS[i] + 25.0, 85.0), (-0.55, -1.0, 0.35), dist)


def doser_view(dty, dist=700.0):
    """The doser and its stretch of the row, from the front right, following the doser in y."""
    return cam_dir((CS.LANE_X - 30.0, tip(dty, CS.PARK)[1] + 45.0, 105.0), (1.0, -0.95, 0.85), dist)


def interp_cam(cams, t):
    if t <= cams[0][0]:
        return cams[0][1]
    if t >= cams[-1][0]:
        return cams[-1][1]
    j = max(i for i, (tk, _) in enumerate(cams) if tk <= t)
    (t0, c0), (t1, c1) = cams[j], cams[j + 1]
    u = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
    f = c0[1] + (c1[1] - c0[1]) * u                     # the focus moves straight; the camera swings round it,
    d0, d1 = c0[0] - c0[1], c1[0] - c1[1]               # so it doesn't cut through the machine on the way
    r0, r1 = np.linalg.norm(d0), np.linalg.norm(d1)
    v = d0 / r0 + (d1 / r1 - d0 / r0) * u
    return f + (r0 + (r1 - r0) * u) * v / np.linalg.norm(v), f, c0[2] + (c1[2] - c0[2]) * u


# ------------------------------------------------------------------ the run
class Story:
    """Keyframes for the gantry (ty), the head (tx), the doser (dty, deg) and the magnets; doses; captions; cameras."""

    def __init__(self, t0, **pose):
        self.t = t0
        self.pose = dict(pose)
        self.coupled = False
        self.keys = [(t0, dict(self.pose))]
        self.events, self.ramps, self.captions, self.cams = [], [], [], []
        self.dosed = [0.0] * len(ROWS)

    def move(self, dur, **kw):
        if self.coupled and "ty" in kw:
            kw["dty"] = kw["ty"]
        self.pose.update(kw)
        self.t += dur
        self.keys.append((self.t, dict(self.pose)))

    def wait(self, dur):
        self.move(dur)

    def ev(self, **kw):
        self.events.append((self.t, kw))

    def act(self, tool, target=None, what=""):
        self.ev(active=(tool, target, what))

    def caption(self, text):
        self.captions.append([self.t, None, text])

    def cam(self, dt, c):
        self.cams.append((self.t + dt, c))

    def dose(self, i, mg, dur):
        self.ramps.append((self.t, self.t + dur, i, self.dosed[i], self.dosed[i] + mg))
        self.dosed[i] += mg
        self.wait(dur)


def vial_ring(i):
    return (CS.LANE_X, ROWS[i], CS.VIAL[2] + CS.VIAL[1], CS.VIAL[0] / 2 + 5.0)


def build_story(t0):
    s = Story(t0, ty=120.0, tx=60.0, dty=HOME, deg=CS.PARK)
    s.ev(magnets=False, active=None)
    s.cam(0.0, OVERVIEW)
    s.cam(1.4, RUN_WIDE)
    fy_home = CS.beam_front(HOME)

    s.caption("1  Home: GRBL drives the gantry to +Y, the back. The steel tab on its right side plate stops against "
              "the docked shuttle")
    s.act("gantry", (490.0, fy_home, 0.0, 22.0), "homes to +Y, onto the docked shuttle")
    s.move(1.8, ty=HOME)
    s.wait(0.4)

    s.caption("2  Magnets on: two 5 V, 0.3 A electromagnets, switched by the doser's own board. A dock switch and a "
              "Hall sensor tell CubOS the doser is home and coupled")
    s.act("magnets", (490.0, fy_home, 0.0, 22.0), "on: 10 to 20 N, for about 2 N of load")
    s.ev(magnets=True)
    s.coupled = True
    s.wait(1.6)

    i0, mg0 = PLAN[0]
    s.caption("3  Forward to vial 1, outlet up at −10°: moving forwards, the tab pulls the shuttle through the magnets")
    s.act("gantry", vial_ring(i0), "pulls the doser to vial 1")
    s.cam(0.2, doser_view(at(i0)))
    s.move(2.2, ty=at(i0))
    s.wait(0.2)

    s.caption("4  Tilt to 35°: the tip drops 36 mm, to 17 mm over the rim, 129 mm behind the capper")
    s.cam(0.0, near(i0))
    s.act("servo", vial_ring(i0), "−10° to 35°, outlet down")
    s.move(1.1, deg=CS.DOSE)
    s.wait(0.2)

    s.caption(f"5  Dose {mg0:.0f} mg: the vibration motor runs and the auger turns about {mg0 / PER_TURN:.2f} turn "
              f"(estimates: {PER_TURN:.0f} mg per turn, {RATE:.0f} mg/s)")
    s.act("auger", vial_ring(i0), f"{mg0:.0f} mg into vial 1")
    s.dose(i0, mg0, mg0 / RATE)
    s.wait(0.4)

    s.caption("6  Back to park, −10°: the capillary slopes back into the tube, so shaking while towed should move "
              "powder back, not out")
    s.act("servo", vial_ring(i0), "35° to −10°, outlet up")
    s.move(0.9, deg=CS.PARK)
    s.wait(0.2)

    prev = i0
    for n, (i, mg) in enumerate(PLAN[1:]):
        dur = min(mg / RATE, 2.6)
        fast = mg / RATE / dur
        if n == 0:
            s.caption(f"7  Back to vial 2: moving back, the tab pushes the shuttle by contact. Then the same cycle, "
                      f"{mg:.0f} mg")
            s.cam(0.3, doser_view(at(i)))
        elif i == 5:
            s.caption(f"9  Vial 6, at the back of the row: only the doser reaches the back four vials. {mg:.0f} mg")
            s.cam(0.3, doser_view(at(i), 700.0))
        elif n == 1:
            s.caption("8  Vials 3 and 4: 100 and 200 mg. The dose series doubles; the front four vials are also in "
                      "the capper's and the pipette's reach")
        s.act("gantry", vial_ring(i), f"{'pushes' if at(i) > at(prev) else 'pulls'} the doser to vial {i + 1}")
        s.move(0.8 + 0.004 * abs(at(i) - at(prev)), ty=at(i))
        s.act("servo", vial_ring(i), "−10° to 35°")
        s.move(0.6, deg=CS.DOSE)
        what = f"{mg:.0f} mg into vial {i + 1}" + (f" (shown {fast:.0f}× faster)" if fast > 1.05 else "")
        s.act("auger", vial_ring(i), what)
        s.dose(i, mg, dur)
        s.act("servo", vial_ring(i), "back to −10°")
        s.move(0.55, deg=CS.PARK)
        prev = i

    s.caption("10  The head works in front of the doser: it runs to its right end and back. No part of the doser is "
              "ever in front of the beam's front face")
    s.cam(0.2, RUN_WIDE)
    s.act("head", None, "runs to its right end, in front of the doser")
    s.move(1.6, tx=CS.TRAVEL[0])
    s.move(1.3, tx=60.0)

    s.caption("11  Back to the dock: the tab pushes the shuttle home")
    s.act("gantry", tuple(s_ for s_ in (490.0, fy_home, 0.0, 22.0)), "pushes the doser back to the dock")
    s.move(1.3, ty=HOME)
    s.wait(0.2)

    s.caption("12  Magnets off: the doser stays on its dock, on its rail. With the power cut, it stays where it is")
    s.act("magnets", (490.0, fy_home, 0.0, 22.0), "off: released")
    s.ev(magnets=False)
    s.coupled = False
    s.wait(1.4)

    s.caption("13  The gantry goes on without it. The four front vials can now be capped or pipetted by the head")
    s.act("gantry", None, "goes on alone")
    s.cam(0.0, RUN_WIDE)
    s.cam(1.8, OVERVIEW)
    s.move(1.8, ty=40.0)
    s.act(None)
    s.wait(1.4)
    s.total = s.t
    for j, c in enumerate(s.captions):
        c[1] = s.captions[j + 1][0] if j + 1 < len(s.captions) else s.total
    return s


def run_state(s, t):
    st = {"t": t, "magnets": False}
    for te, kw in s.events:
        if te <= t + 1e-9:
            st.update(kw)
    keys = s.keys
    if t >= keys[-1][0]:
        pose = keys[-1][1]
    elif t <= keys[0][0]:
        pose = keys[0][1]
    else:
        j = max(i for i, (tk, _) in enumerate(keys) if tk <= t)
        (t0, p0), (t1, p1) = keys[j], keys[j + 1]
        u = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
        pose = {k: p0[k] + (p1[k] - p0[k]) * u for k in p0}
    st.update(pose)
    doses = [0.0] * len(ROWS)
    for a, b, i, m0, m1 in s.ramps:
        if t >= a:
            doses[i] = m0 + (m1 - m0) * min((t - a) / (b - a), 1.0)
            if t < b:
                st["stream"] = (i, t - a, doses[i])
    st["doses"] = doses
    act = st.get("active")
    if act and act[0]:
        tool, target, what = act
        st["lit"], st["target"], st["tool"], st["what"] = (tool,), target, tool, what
    return st


# ------------------------------------------------------------------ placing the parts
PLACE_POSE = dict(ty=60.0, tx=150.0, dty=HOME, deg=CS.PARK)
PARTS = [  # group, label (a few words), anchor (machine), on the gantry
    ("vials", "Vial row: 8 × 20 mL, 33 mm pitch", (CS.LANE_X, ROWS[2], 78.0), False),
    ("rail", "MGN12 rail on the deck's margin", (469.0, ROWS[1], 8.0), False),
    ("dock", "Dock: stop and detent", None, False),
    ("shuttle", "Shuttle and side frame", None, False),
    ("doser", "Miniature doser, one tilt servo", None, False),
    ("magnets", "Two electromagnets, faces forward", None, False),
    ("tab", "Steel tab on the gantry's side plate", None, True),
    ("capper", "Capper (on the head)", None, True),
    ("pipette", "Pipette (on the head)", None, True),
]
DROP, HOLD = 0.55, 1.15


def part_anchor(grp, st, scene):
    hinge = HINGE0 + np.array([0.0, st["dty"], 0.0])
    return {"dock": scene.dock_xyz, "shuttle": hinge + np.array([66.0, 20.0, 20.0]),
            "doser": tip(st["dty"], st["deg"]) + np.array([0.0, 0.0, 4.0]),
            "magnets": np.array([490.0, FY0 + st["dty"] + 10.0, 76.0]),
            "tab": np.array([490.0, FY0 + st["ty"] - 3.0, 78.0]),
            "capper": scene.capper_xyz + np.array([st["tx"], st["ty"], 0.0]),
            "pipette": scene.pip_xyz + np.array([st["tx"], st["ty"], 0.0])}.get(grp)


class Placement:
    def __init__(self, t0):
        self.t0 = t0
        self.items = []
        t = t0 + 0.4
        for grp, lab, anc, gantry in PARTS:
            self.items.append((t, grp, lab, anc, gantry))
            t += DROP + HOLD
        self.t1 = t + 0.4

    def state(self, t):
        st = dict(PLACE_POSE, t=t, magnets=False, hidden=set(), drop={}, lit=())
        for ts, grp, lab, anc, gantry in self.items:
            if t < ts:
                st["hidden"].add(grp)
            elif t < ts + DROP + HOLD:
                u = min((t - ts) / DROP, 1.0)
                st["drop"][grp] = (60.0 if gantry else 140.0) * (1 - u) ** 2
                st["label"] = (grp, lab, anc)
                st["placing"] = grp
        return st

    def cams(self):
        c = [(self.t0, OVERVIEW)]
        P0, F0 = OVERVIEW[0], OVERVIEW[1]
        for ts, grp, lab, anc, gantry in self.items:
            a = np.array(anc if anc is not None else (CS.LANE_X, 420.0, 80.0), float)
            if grp in ("tab", "capper", "pipette"):
                a = np.array((300.0, 160.0, 120.0))
            f = F0 + 0.45 * (a - F0)
            c.append((ts + 0.25, (f + 0.75 * (P0 - F0), f, 30.0)))
        c.append((self.t1 + 0.9, RUN_WIDE))
        return c


# ------------------------------------------------------------------ 2D: cards and overlays
def wrap(d, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    return lines


def topbar(d, chapter):
    d.rectangle([0, 0, W, 36], fill=(252, 252, 251, 230))
    ft = font(19, True)
    title = "Towed powder doser on the CubXL"
    d.text((16, 8), title, font=ft, fill=INK)
    d.text((16 + d.textlength(title, font=ft) + 14, 11), "·  " + chapter, font=font(15), fill=INK2)
    d.text((W - 16, 11), "PR #274 · concept, not built", font=font(13), fill=INK2, anchor="ra")


def caption_bar(d, text, size=17):
    f = font(size)
    lines = wrap(d, text, f, W - 40)
    hb = 14 + (size + 7) * len(lines)
    d.rectangle([0, H - hb, W, H], fill=(252, 252, 251, 232))
    for i, line in enumerate(lines):
        d.text((18, H - hb + 7 + (size + 7) * i), line, font=f, fill=INK)
    return hb


def label_at(d, xy, text, anchor_xy=None, size=16):
    f = font(size, True)
    x, y = xy
    tw = d.textlength(text, font=f)
    if anchor_xy is not None:
        d.line([anchor_xy, (x, y)], fill=ORANGE + (255,), width=2)
        d.ellipse([anchor_xy[0] - 4, anchor_xy[1] - 4, anchor_xy[0] + 4, anchor_xy[1] + 4], fill=ORANGE + (255,))
    d.rounded_rectangle([x - 8, y - size - 6, x + tw + 8, y + 6], radius=6, fill=(252, 252, 251, 235),
                        outline=ORANGE + (255,), width=2)
    d.text((x, y - size - 1), text, font=f, fill=INK)


def tool_panel(d, active):
    y = 46
    f = font(14, True)
    d.text((16, y + 5), "working now:", font=font(13), fill=INK2)
    xx = 16 + d.textlength("working now:", font=font(13)) + 10
    for k, name in TOOLS.items():
        on = k == active
        wpill = d.textlength(name, font=f) + 26
        d.rounded_rectangle([xx, y, xx + wpill, y + 26], radius=13, fill=ORANGE + (255,) if on else (252, 252, 251, 220),
                            outline=ORANGE + (255,) if on else (190, 188, 182, 255), width=2)
        d.text((xx + wpill / 2, y + 13), name, font=f, fill=(255, 255, 255) if on else MUTED, anchor="mm")
        xx += wpill + 8


def dose_panel(d, doses, active_vial):
    x0, y0, w = 16, 84, 246
    d.rounded_rectangle([x0, y0, x0 + w, y0 + 40 + 24 * len(PLAN)], radius=8, fill=(252, 252, 251, 232),
                        outline=RULE, width=1)
    d.text((x0 + 12, y0 + 9), "dose log (estimated)", font=font(14, True), fill=INK)
    for n, (i, mg) in enumerate(PLAN):
        y = y0 + 36 + 24 * n
        got = doses[i]
        done = got >= mg - 1e-6
        col = INK if got > 0 else MUTED
        if i == active_vial and not done:
            col = ORANGE
        d.text((x0 + 12, y), f"vial {i + 1}", font=font(14), fill=col)
        d.text((x0 + 92, y), f"{got:5.0f} / {mg:.0f} mg", font=font(14, done), fill=col)
        frac = min(got / mg, 1.0)
        d.rectangle([x0 + 200, y + 4, x0 + 234, y + 14], outline=(190, 188, 182), width=1)
        if frac > 0:
            d.rectangle([x0 + 200, y + 4, x0 + 200 + 34 * frac, y + 14], fill=(110, 112, 118) if done else ORANGE)


def icon(d, kind, x0, y0, s=1.0):
    """Small pictograms for the cards."""
    def R(a, b, c, e, **kw):
        d.rectangle([x0 + a * s, y0 + b * s, x0 + c * s, y0 + e * s], **kw)

    def E(a, b, c, e, **kw):
        d.ellipse([x0 + a * s, y0 + b * s, x0 + c * s, y0 + e * s], **kw)

    def L(pts, **kw):
        d.line([(x0 + a * s, y0 + b * s) for a, b in pts], **kw)
    grey, steel = (150, 152, 158), (190, 194, 200)
    if kind == "auger":
        R(20, 60, 200, 110, fill=steel, outline=INK2, width=2)                   # the tube
        for k in range(9):
            L([(40 + 18 * k, 62), (52 + 18 * k, 108)], fill=(120, 122, 128), width=3)   # the flight, seen through
        R(200, 55, 222, 115, fill=(90, 92, 98))                                  # the cap
        R(0, 80, 20, 90, fill=steel, outline=INK2)                               # the capillary
        rng = np.random.default_rng(2)
        for _ in range(60):
            u, v = rng.uniform(0, 1), rng.uniform(-1, 1)
            E(120 + 70 * u - 2, 20 + 30 * v * 0.3 + 10 - 2, 120 + 70 * u + 2, 20 + 30 * v * 0.3 + 10 + 2, fill=grey)
        L([(155, 35), (155, 55)], fill=ORANGE, width=3)
        R(40, 170, 200, 220, fill=(60, 60, 60))
        R(55, 160, 185, 170, fill=(140, 140, 140))
        d.text((x0 + 120 * s, y0 + 195 * s), "0.1 mg", font=font(int(16 * s), True), fill=(140, 230, 160),
               anchor="mm")
        d.text((x0 + 10 * s, y0 + 240 * s), "fill, cap, weigh the cartridge", font=font(int(13 * s)), fill=INK2)
    elif kind == "bench":
        R(30, 150, 210, 200, fill=(60, 60, 60))
        R(60, 140, 180, 150, fill=(140, 140, 140))
        d.text((x0 + 120 * s, y0 + 175 * s), "50.3 mg", font=font(int(16 * s), True), fill=(140, 230, 160),
               anchor="mm")
        R(95, 105, 145, 140, fill=(240, 244, 246), outline=INK2)                 # the cup
        L([(60, 20), (150, 60)], fill=INK2, width=10)                            # the doser at 35 degrees
        L([(150, 60), (162, 66)], fill=INK2, width=4)
        for k in range(8):
            E(118 + (k % 2) * 3, 72 + 8 * k, 122 + (k % 2) * 3, 76 + 8 * k, fill=grey)
        L([(10, 240), (40, 225), (70, 238), (100, 222), (130, 236), (160, 224), (190, 232), (220, 226)],
          fill=(42, 120, 214), width=2)
        d.text((x0 + 10 * s, y0 + 252 * s), "balance at 10 Hz: mg per turn", font=font(int(13 * s)), fill=INK2)
    elif kind == "vials":
        for k in range(8):
            xx = 10 + 27 * k
            R(xx, 60, xx + 21, 160, fill=(232, 240, 246), outline=INK2)
            if k < 4:
                R(xx - 2, 168, xx + 23, 176, fill=(42, 120, 214))
        R(0, 160, 225, 172, fill=(220, 220, 224))
        d.text((x0 + 10 * s, y0 + 190 * s), "front four: tools reach them too", font=font(int(13 * s)), fill=INK2)
        d.text((x0 + 10 * s, y0 + 212 * s), "back four: the doser only", font=font(int(13 * s)), fill=INK2)
    elif kind == "board":
        R(20, 40, 200, 150, fill=(18, 97, 51), outline=INK2, width=2)
        R(40, 60, 100, 100, fill=(26, 76, 122))
        R(120, 60, 180, 90, fill=(30, 30, 30))
        for k in range(2):
            E(40 + 90 * k, 180, 90 + 90 * k, 230, fill=(220, 46, 41), outline=INK2, width=2)
        L([(110, 150), (65, 180)], fill=INK2, width=2)
        L([(110, 150), (155, 180)], fill=INK2, width=2)
        d.text((x0 + 10 * s, y0 + 245 * s), "MOSFET + flyback diode, 5 V", font=font(int(13 * s)), fill=INK2)
    elif kind == "after":
        R(30, 150, 210, 200, fill=(60, 60, 60))
        R(60, 140, 180, 150, fill=(140, 140, 140))
        R(105, 60, 135, 140, fill=(232, 240, 246), outline=INK2)
        E(108, 128, 132, 140, fill=grey)
        d.text((x0 + 120 * s, y0 + 175 * s), "+50.1 mg", font=font(int(16 * s), True), fill=(140, 230, 160),
               anchor="mm")
        d.text((x0 + 10 * s, y0 + 230 * s), "delivered = after - before", font=font(int(13 * s)), fill=INK2)


PREP_CARDS = [
    ("1  Powder and the auger", "by hand, one powder per run",
     ["One powder at a time, changed by hand. Ben's sketch has the doser pouring Al into different vials",
      "Unscrew the auger's cap and fill the open store about half full: about 20 cm³ of bore, about 12 g at "
      "1.2 g/cm³",
      "Screw the cap back on; check the 3 mm capillary is clear",
      "Weigh the cartridge (tube and cap) on a 0.1 mg balance. Weighed again after the run, it gives the total "
      "delivered"],
     "README: What changed; Calibration and dose checks", "auger"),
    ("2  Calibrate on the bench", "on weight, before it goes on the machine",
     ["Dose onto a balance logged at 10 Hz or faster, at 35°, as in the bench tests",
      "mg per turn and per vibration setting. About 380 mg per turn is PR 176's DEM estimate, not a measurement",
      "Report the RSD over 0.1, 1, 5 and 30 s, the time with no flow, and the tail after a stop",
      "Choose the park angle: −10° drains the capillary (about 30 s to refill at 10 mg/s), level may keep it full"],
     "README: Bench tests; One servo", "bench"),
    ("3  Vials", "tare, place, leave open",
     ["Weigh each empty 20 mL vial on the 0.1 mg balance and label it",
      "Eight in the strip holder on the doser's row at 33 mm pitch, rims 75 mm up (assumed): all the same height",
      "Uncapped while the doser works the row: its body trails over the vials behind the tip",
      "The front four are in the capper's and the pipette's reach too; the back four only in the doser's"],
     "README: Towed by the gantry", "vials"),
    ("4  The coupling and the board", "before power-on",
     ["The doser on its dock, where homing will leave the gantry's tab",
      "The doser keeps PR 176's own board, not the CubXL's Uno: the stepper, the servo, and the magnets through a "
      "MOSFET with a flyback diode",
      "A dock switch and a Hall sensor at the coupling; the cable in a small drag chain",
      "In CubOS: a new instrument type, a Y offset of about +129 mm, a fixed X, Y moves only. Not written yet"],
     "README: Towed by the gantry", "board"),
]
AFTER_CARD = ("After the run", "weigh, compare, clean",
              ["Weigh each vial again on the 0.1 mg balance: delivered mass against the target, vial by vial",
               "Weigh the auger cartridge: the run's total, independent of everything else",
               "Look for powder on the deck along the row: did towing shake any out?",
               "Change the powder by hand: unscrew the cap, empty the store, brush out the capillary"],
              "README: Calibration and dose checks; Not checked", "after")
CARD_DUR = 6.0


def card_image(card, t_local, total=CARD_DUR, chapter="before the run, by hand"):
    title, sub, bullets, src, kind = card
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im, "RGBA")
    topbar(d, chapter)
    d.text((70, 78), title, font=font(34, True), fill=INK)
    d.text((72, 124), sub, font=font(18), fill=INK2)
    d.line([(70, 158), (W - 70, 158)], fill=RULE, width=2)
    icon(d, kind, 80, 200, 1.35)
    f = font(19)
    y = 190
    for i, b in enumerate(bullets):
        t_on = 0.5 + i * min(0.9, (total - 2.0) / max(len(bullets), 1))
        a = ease((t_local - t_on) / 0.35)
        if a <= 0:
            continue
        col = tuple(int(PAPER[j] + (INK[j] - PAPER[j]) * a) for j in range(3))
        lines = wrap(d, b, f, W - 470 - 70)
        d.ellipse([452, y + 9, 461, y + 18], fill=ORANGE + (int(255 * a),))
        for k, line in enumerate(lines):
            d.text((475, y + 27 * k), line, font=f, fill=col)
        y += 27 * len(lines) + 18
    d.text((70, H - 40), "Sources: " + src, font=font(13), fill=MUTED)
    return np.asarray(im)


PHOTOS = [  # file in media/, title, credit
    ("cubxl-empty-ben-2026-06-26.jpg", "The CubXL, empty", "Ben Whitney, #133, 2026-06-26"),
    ("towed-doser-sketch-ben-2026-10-16.png", "Ben's idea", "Ben Whitney, PR 274, 2026-10-16"),
    ("right-y-rail-ben-2026-10-19.jpg", "The right Y rail, measured", "Ben Whitney, PR 274, 2026-10-19"),
]


def photo_card(t_local):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im, "RGBA")
    topbar(d, "the real machine")
    ph_h, gap = 440, 34
    ims = []
    for fname, _, _ in PHOTOS:
        f = MEDIA / fname
        p = ImageOps.exif_transpose(Image.open(f)).convert("RGB") if f.exists() else Image.new("RGB", (3, 4), RULE)
        ims.append(p.resize((int(p.size[0] * ph_h / p.size[1]), ph_h), Image.LANCZOS))
    total_w = sum(p.size[0] for p in ims) + gap * (len(ims) - 1)
    x = (W - total_w) // 2
    for k, (p, (_, title, credit)) in enumerate(zip(ims, PHOTOS)):
        a = ease((t_local - 0.2 - 0.9 * k) / 0.5)
        if a <= 0:
            x += p.size[0] + gap
            continue
        y = 92
        d.rectangle([x - 8, y - 8, x + p.size[0] + 8, y + ph_h + 8], fill=(255, 255, 255), outline=RULE)
        blended = Image.blend(Image.new("RGB", p.size, PAPER), p, a)
        im.paste(blended, (x, y))
        d.text((x, y + ph_h + 20), title, font=font(20, True), fill=INK)
        d.text((x, y + ph_h + 48), credit, font=font(14), fill=INK2)
        x += p.size[0] + gap
    return np.asarray(im)


def overlay_3d(img, scene, st, chapter, caption=None, label=None, active=None, doses=None, vial_nums=False):
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im, "RGBA")
    if vial_nums and np.linalg.norm(np.subtract(scene.pl.camera.position, scene.pl.camera.focal_point)) > 600:
        for i, y in enumerate(ROWS):
            x_, y_ = scene.project((CS.LANE_X - 24.0, y, 0.0))
            if 0 < x_ < W and 40 < y_ < H - 60:
                d.text((x_ - 6, y_), str(i + 1), font=font(14, True), fill=INK2, anchor="rm", stroke_width=3,
                       stroke_fill=(252, 252, 251))
    topbar(d, chapter)
    if active is not None or doses is not None:
        tool_panel(d, active)
    if doses is not None:
        dose_panel(d, doses, st.get("stream", (None,))[0] if st.get("stream") else None)
    if caption:
        caption_bar(d, caption)
    if label is not None:
        text, xyz, offset = label
        ax, ay = scene.project(xyz)
        if 0 < ax < W and 0 < ay < H:
            lx, ly = ax + offset[0], ay + offset[1]
            lx = min(max(lx, 20 if doses is None else 280), W - 20 - font(16, True).getlength(text) - 16)
            ly = min(max(ly, 112), H - 76)
            label_at(d, (lx, ly), text, anchor_xy=(ax, ay))
    return np.asarray(im)


# ------------------------------------------------------------------ the timeline
class Video:
    def __init__(self):
        self.t_photo = (0.0, 5.4)
        self.t_dissolve = (5.4, 6.6)
        self.t_orbit = (6.6, 10.0)
        self.place = Placement(self.t_orbit[1])
        self.t_prep = (self.place.t1 + 0.9, self.place.t1 + 0.9 + CARD_DUR * len(PREP_CARDS))
        self.story = build_story(self.t_prep[1] + 0.3)
        self.t_run = (self.t_prep[1], self.story.total)
        self.t_after = (self.story.total, self.story.total + CARD_DUR)
        self.t_outro = (self.t_after[1], self.t_after[1] + 5.0)
        self.total = self.t_outro[1]
        self.cams = [(self.t_dissolve[0], FRONT), (self.t_orbit[0] + 0.2, FRONT), (self.t_orbit[1], OVERVIEW)]

    def kind(self, t):
        if t < self.t_dissolve[0]:
            return "photo"
        if t < self.t_orbit[1]:
            return "intro3d"
        if t < self.place.t1 + 0.9:
            return "place"
        if t < self.t_prep[1]:
            return "prep"
        if t < self.t_run[1]:
            return "run"
        if t < self.t_after[1]:
            return "after"
        return "outro"

    def chapters(self):
        return [("The real CubXL, Ben's idea and his measurements", 0.0),
                ("The same machine as a model", self.t_dissolve[0]),
                ("The doser's parts, one at a time", self.t_orbit[1]),
                ("Before the run, by hand", self.t_prep[0]),
                ("The run, step by step", self.t_run[0]),
                ("After the run", self.t_after[0]), ("Summary", self.t_outro[0])]


OUTRO_LINES = [
    "One powder, one row of 8 vials at 33 mm pitch, 4 of them also in the tools' reach",
    "Doses and rates are estimates: about 380 mg per turn (PR 176's DEM), 10 mg/s",
    "Fit on Ben's numbers: 8.3 mm under the beam at the worst pose (cubxl_shuttle.py --fit)",
    "Model and video: modules/miniature-powder-doser/miniature-doser/",
    "github.com/vertical-cloud-lab/byu-vcl/pull/274",
]


class Renderer:
    def __init__(self):
        self.v = Video()
        self.scene = Scene()

    def render3d(self, st, cam):
        self.scene.set_state(st)
        self.scene.set_camera(cam)
        return self.scene.frame()

    def frame(self, t):
        v, s = self.v, self.v.story
        k = v.kind(t)
        if k == "photo":
            return photo_card(t)
        if k == "intro3d":
            st = dict(PLACE_POSE, t=t, magnets=False, hidden={g for g, _, _, _ in PARTS}, drop={}, lit=(),
                      fade=ease((t - v.t_orbit[0]) / (v.t_orbit[1] - v.t_orbit[0])))
            raw = self.render3d(st, interp_cam(v.cams, t))
            img = overlay_3d(raw, self.scene, st, "the model",
                             caption="The same machine as a model: the deck is Cubware's PandaDeck.step, the rest is "
                                     "boxes placed from Ben's measurements. The right side and the beam turn "
                                     "see-through")
            if t < v.t_dissolve[1]:
                a = ease((t - v.t_dissolve[0]) / (v.t_dissolve[1] - v.t_dissolve[0]))
                img = (photo_card(v.t_dissolve[0]) * (1 - a) + img * a).astype(np.uint8)
            return img
        if k == "place":
            p = v.place
            st = p.state(t)
            raw = self.render3d(st, interp_cam(p.cams(), t))
            label = None
            if "label" in st:
                grp, lab, anc = st["label"]
                xyz = anc if anc is not None else part_anchor(grp, st, self.scene)
                label = (lab, xyz, (40, -60))
            cap = ("What the doser adds to the deck, one part at a time" if t < p.items[6][0] - 0.3 else
                   "On the gantry: the tab the magnets pull on. On the head: the tools, which stay in front of the doser")
            return overlay_3d(raw, self.scene, st, "placing the parts", caption=cap, label=label)
        if k == "prep":
            i = min(int((t - v.t_prep[0]) // CARD_DUR), len(PREP_CARDS) - 1)
            img = card_image(PREP_CARDS[i], t - v.t_prep[0] - i * CARD_DUR)
            if i == 0 and t - v.t_prep[0] < 0.5:
                a = ease((t - v.t_prep[0]) / 0.5)
                img = (img * a + 246 * (1 - a)).astype(np.uint8)
            return img
        if k == "run":
            st = run_state(s, t)
            raw = self.render3d(st, interp_cam(s.cams, t))
            cap = [c for c in s.captions if c[0] <= t + 1e-9]
            caption = cap[-1][2] if cap else "The run, start to finish"
            label = None
            tool = st.get("tool")
            if tool:
                pt = {"gantry": np.array([490.0, FY0 + st["ty"] - 3.0, 78.0]),
                      "magnets": np.array([490.0, FY0 + st["dty"] + 10.0, 76.0]),
                      "servo": HINGE0 + np.array([-50.0, st["dty"] + 8.0, 14.0]),
                      "auger": tip(st["dty"], st["deg"]),
                      "head": self.scene.capper_xyz + np.array([st["tx"], st["ty"], 0.0])}[tool]
                label = (f"{TOOLS[tool]}: {st['what']}", pt, (-330, -80) if tool == "servo" else (60, -80))
            return overlay_3d(raw, self.scene, st, "the run", caption=caption, label=label, active=tool,
                              doses=st["doses"], vial_nums=True)
        if k == "after":
            return card_image(AFTER_CARD, t - v.t_after[0], chapter="after the run")
        st = run_state(s, s.total)
        st.update(lit=(), target=None)
        raw = self.render3d(st, OVERVIEW)
        img = overlay_3d(raw, self.scene, st, "summary")
        im = Image.fromarray(img)
        d = ImageDraw.Draw(im, "RGBA")
        d.rectangle([40, 480, 860, 690], fill=(252, 252, 251, 238), outline=RULE)
        for i, line in enumerate(OUTRO_LINES):
            d.text((60, 496 + 36 * i), line, font=font(18, i == 0), fill=INK if i == 0 else INK2)
        return np.asarray(im)


# ------------------------------------------------------------------ main
def named_stills(v):
    s = v.story
    first = [r for r in s.ramps][0]
    return {"placement": v.place.items[4][0] + DROP + 0.6, "dose": (first[0] + first[1]) / 2,
            "head": [c[0] for c in s.captions if c[2].startswith("10 ")][0] + 1.6}


def write_json(v):
    s = v.story
    chapters = v.chapters()
    out = {"name": NAME, "fps": FPS, "size": [W, H], "duration_s": round(v.total, 2),
           "chapters": [{"title": c, "start_s": round(t, 2),
                         "end_s": round(chapters[i + 1][1] if i + 1 < len(chapters) else v.total, 2)}
                        for i, (c, t) in enumerate(chapters)],
           "run_captions": [{"caption": c, "start_s": round(a, 2), "end_s": round(b, 2)} for a, b, c in s.captions],
           "doses_mg": [{"vial": i + 1, "mg": mg} for i, mg in PLAN],
           "assumptions": {"mg_per_turn": PER_TURN, "rate_mg_per_s": RATE, "bulk_density_g_per_cm3": RHO,
                           "park_deg": CS.PARK, "dose_deg": CS.DOSE}}
    (HERE / f"{NAME}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="", help="comma-separated times in seconds to save as PNG stills, no video")
    ap.add_argument("--part", default="", help="i/n: render the i-th of n equal frame ranges to /tmp")
    ap.add_argument("--assemble", type=int, default=0, help="n: join the n parts and build the GIF")
    args = ap.parse_args()
    v = Video()
    n = int(math.ceil(v.total * FPS))
    gif_dir = TMP / f"{NAME}_gif"
    if args.assemble:
        import subprocess
        import imageio_ffmpeg
        lst = TMP / f"{NAME}_segs.txt"
        lst.write_text("".join(f"file '{TMP / f'{NAME}_seg_{i}.mp4'}'\n" for i in range(args.assemble)))
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(HERE / f"{NAME}.mp4")], check=True)
        frames = [Image.open(f).convert("RGB") for f in sorted(gif_dir.glob("*.png"))]
        sheet = Image.new("RGB", (GW, GH * 6))
        for i, j in enumerate(np.linspace(0, len(frames) - 1, 6).astype(int)):
            sheet.paste(frames[j], (0, GH * i))
        pal = sheet.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        gq = [g.quantize(palette=pal, dither=Image.Dither.NONE) for g in frames]
        gq[0].save(HERE / f"{NAME}.gif", save_all=True, append_images=gq[1:], duration=100, loop=0, optimize=True)
        write_json(v)
        print("assembled", n, "frames;", len(frames), "GIF frames", flush=True)
        return
    r = Renderer()
    print(f"{v.total:.1f} s, {n} frames; run {v.t_run[0]:.1f}-{v.t_run[1]:.1f} s", flush=True)
    stills = [float(x) for x in args.stills.split(",") if x.strip()]
    if stills:
        for t in stills:
            Image.fromarray(r.frame(t)).save(TMP / f"{NAME}_still_{t:06.2f}.png")
            print("still", t, flush=True)
        return
    k0, k1, out = 0, n, HERE / f"{NAME}.mp4"
    if args.part:
        i, m = (int(x) for x in args.part.split("/"))
        k0, k1 = n * i // m, n * (i + 1) // m
        out = TMP / f"{NAME}_seg_{i}.mp4"
    else:
        write_json(v)
    gif_dir.mkdir(exist_ok=True)
    import imageio.v2 as imageio
    writer = imageio.get_writer(out, fps=FPS, codec="libx264", quality=None, macro_block_size=8,
                                ffmpeg_params=["-crf", "21", "-preset", "slow", "-pix_fmt", "yuv420p", "-g", "60"])
    named = named_stills(v)
    for k in range(k0, k1):
        t = k / FPS
        img = r.frame(t)
        writer.append_data(img)
        for name, ts in named.items():
            if k == int(round(ts * FPS)):
                Image.fromarray(img).save(HERE / f"{NAME}_{name}.png", optimize=True)
        if k % 10 == 0 and v.t_run[0] <= t < v.t_run[1]:
            Image.fromarray(img).resize((GW, GH), Image.LANCZOS).save(gif_dir / f"{k:05d}.png")
        if (k - k0) % 150 == 0:
            print("frame", k, "of", n, flush=True)
    writer.close()
    print("done", k0, k1, flush=True)


if __name__ == "__main__":
    main()
