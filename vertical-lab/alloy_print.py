"""Chapter 3 of the alloy route, start to finish (#303): the atomized powder through the sieve shaker, and into the
Aconity MIDI, which prints the plate that ``alloy_workflow.py`` (chapter 4) takes out.

    xvfb-run -a python3 alloy_print.py            # -> out/alloy_print.gif, out/mp4/alloy_print.mp4, .json, still
    PREVIEW=1 xvfb-run -a python3 alloy_print.py  # the last frame of each sub-step -> /tmp/preview_alloy_print.png

It starts where the atomizer chapter ends: the MiR250 parked in front of the AMAZEMET rePowder with the rePowder's
powder container on its cabinet (two 5N Al cups with Si: Al-10Si, ``out/alloy_recipe.json``). It ends where chapter
4 begins: the plate printed and buried in powder in the closed Aconity, the MiR back at x = 1400 with its arm parked,
and chapter 4's opening camera.

The scene is chapter 4's own (``alloy_workflow.build()``: the line, the opened Aconity MIDI, the EDM, the Instrons, the
MiR250 and its UR10e) plus the Retsch AS 200 control on a bench between the rePowder and the VLM. The shaker, its
8 in stack, lid, knobs and powder fractions are ``instruments_char.sieve()``'s, driven through its own joints. Every
arm move is a straight line of the gripper or a joint move between two solved poses (``robot.py``). See
``notes/alloy_print.md`` for what is measured and what is assumed.
"""
from __future__ import annotations

import math
import sys

import numpy as np
import pyvista as pv
from PIL import ImageDraw

import alloy_workflow as AW           # sets scene.GIF_FPS / GIF_SIZE as chapter 4 does
from scene import CLEAN, PREVIEW, T, S, font

import alloy_models as M              # noqa: E402
import animate as A                   # noqa: E402
import charge                         # noqa: E402
import instruments_char as IC         # noqa: E402
import line                           # noqa: E402
import props as P                     # noqa: E402
import robot as RB                    # noqa: E402
import tour                           # noqa: E402
from alloy_workflow import held_point, status  # noqa: E402

NAME = "alloy_print"
TITLE = "Vertical cloud lab: from the atomizer's powder to the printed plate"

# ------------------------------------------------------------------------------------------------- layout
BENCH = dict(x=-2015.0, w=1000.0, d=600.0, h=700.0)     # a lab bench between the rePowder and the VLM (assumed)
SIEVE_DX = -30.0                                        # the shaker's centre, from the bench's
START = (A.REPOWDER_AT[0] + 288.0, -2230.0)             # MiR parked in front of the rePowder's container axis, clear
MIR_END = 1400.0                                        # alloy_workflow.Mir's starting x: chapter 4 begins there
HOLDER_LOCAL = (-30.0, -150.0)                          # container/bottle cup on the MiR's cabinet (MiR frame)
HOLDER_H = 140.0
GRIP_HANDLE = 0.876                                     # 12 mm handle bar (alloy_workflow: 0.88 for the 12 mm lug)
GRIP_BAR36 = 0.59                                       # the lid's 36 mm crossbar
GRIP_KNOB = 0.36                                        # the 54 mm knob
GRIP_BOTTLE = 0.18                                      # the 70 mm bottle
LAYER_UM = 50.0                                         # assumed: AddUp's AlSi10Mg sheet (chapter 4) prints 50 um

POWDER = M.POWDER
STREAM = (0.42, 0.43, 0.46)
LASER = (1.0, 0.45, 0.12)

# the rePowder's container, as instruments_char.sieve() draws it (CONT_LINE, "DAL, assumed size"): Ø128 x 228, a
# handle bar at the top on the -y side. Its own frame: axis on z, base at z = 0
CONT_OUT = [(0.0, 0.0), (54.0, 0.0), (64.0, 10.0), (64.0, 190.0), (44.0, 200.0), (44.0, 228.0)]
HANDLE_GRASP = np.array([45.0, -94.0, 241.0])            # middle of the handle bar
MOUTH = np.array([0.0, 0.0, 228.0])
# a wide-mouth powder bottle (assumed: 250 mL HDPE, Ø70 x 112 with a Ø50 cap)
BOT_R, BOT_H, NECK_R, NECK_H, CAP_H = 35.0, 112.0, 22.0, 12.0, 14.0


def _shell(line_pts, t=1.5):
    """A thin revolved wall along an open (r, z) line, closed into a profile `t` thick (inside)."""
    inner = [(max(r - t, 0.0), z + (t if i == 0 else 0.0)) for i, (r, z) in enumerate(line_pts)]
    prof = list(line_pts) + list(reversed(inner))
    return charge.lathe(prof, res=64)


def container_meshes():
    can = _shell(CONT_OUT)
    collar = charge.lathe([(44.0, 222.0), (52.0, 222.0), (52.0, 249.0), (44.0, 249.0)], res=48)
    arm = pv.Box(bounds=(-8, 8, -88, -44.5, 233, 249)).triangulate()
    bar = pv.Box(bounds=(-4, 85, -100, -88, 235, 247)).triangulate()
    powder = pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=60.0, height=1.0, resolution=48).triangulate()
    return {"can": (can.merge(collar), (0.80, 0.81, 0.83)), "handle": (arm.merge(bar), (0.78, 0.12, 0.10))}, powder


def bottle_meshes():
    body = charge.lathe([(0, 0), (BOT_R - 4, 0), (BOT_R, 4), (BOT_R, BOT_H - 10), (NECK_R + 2, BOT_H - 2),
                         (NECK_R, BOT_H), (NECK_R, BOT_H + NECK_H), (NECK_R - 2, BOT_H + NECK_H),
                         (NECK_R - 2, BOT_H + 1), (BOT_R - 2, BOT_H - 11), (BOT_R - 2, 3), (0, 3)], res=56)
    cap = charge.lathe([(0, BOT_H + NECK_H - 6), (NECK_R + 3, BOT_H + NECK_H - 6), (NECK_R + 3, BOT_H + NECK_H + CAP_H - 6),
                        (0, BOT_H + NECK_H + CAP_H - 6)], res=48)
    powder = pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=BOT_R - 2.5, height=1.0,
                         resolution=40).triangulate()
    return body, cap, powder


def holder_mesh(top):
    hx, hy = HOLDER_LOCAL
    post = pv.Cylinder(center=(hx, hy, top + HOLDER_H / 2), direction=(0, 0, 1), radius=18, height=HOLDER_H).triangulate()
    foot = pv.Box(bounds=(hx - 50, hx + 50, hy - 50, hy + 50, top, top + 8)).triangulate()
    cup = charge.lathe([(0, 0), (72, 0), (72, 34), (66, 34), (66, 6), (0, 6)], res=56).translate(
        (hx, hy, top + HOLDER_H), inplace=False)
    return post.merge(foot).merge(cup)


def bench_mesh():
    b = BENCH
    x0, x1 = b["x"] - b["w"] / 2, b["x"] + b["w"] / 2
    y0, y1 = line.Y_FACE, line.Y_FACE + b["d"]
    top = pv.Box(bounds=(x0, x1, y0, y1, b["h"] - 30, b["h"])).triangulate()
    legs = None
    for (x, y) in ((x0 + 30, y0 + 30), (x1 - 30, y0 + 30), (x0 + 30, y1 - 30), (x1 - 30, y1 - 30)):
        leg = pv.Box(bounds=(x - 20, x + 20, y - 20, y + 20, 0, b["h"] - 30)).triangulate()
        legs = leg if legs is None else legs.merge(leg)
    shelf = pv.Box(bounds=(x0 + 10, x1 - 10, y0 + 10, y1 - 10, 160, 180)).triangulate()
    return top, legs.merge(shelf)


def stream_pts(top, bottom, t, n=34, on=1.0, spread=2.0):
    """Grains falling from `top` to `bottom` (world), animated by t."""
    s = (np.arange(n) / n + t * 1.9) % 1.0
    s = s[s < on]
    if not len(s):
        return np.zeros((0, 3))
    top, bottom = np.asarray(top, float), np.asarray(bottom, float)
    k = np.arange(len(s))
    xy = top[:2] + (bottom[:2] - top[:2]) * s[:, None] ** 0.6
    xy += np.c_[np.sin(k * 2.3), np.cos(k * 1.7)] * spread
    z = top[2] - (top[2] - bottom[2]) * s ** 2
    return np.c_[xy, z]


# ------------------------------------------------------------------------------------------------- the scene
class PrintScene(AW.AlloyScene):
    """Chapter 4's scene class plus the sieve fractions panel (instruments_char's, drawn on the right)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.panel_a = 0.0

    def overlay(self, img, scale, anchors):
        img = super().overlay(img, scale, anchors)
        if not CLEAN and self.panel_a > 0.02:
            _panel(img, scale, self.panel_a)
        return img


def _panel(img, scale, alpha):
    """instruments_char._sieve_panel, moved to the top right so the status table stays clear."""
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    s = max(scale, 0.8)
    a = int(255 * alpha)
    rows = [(f"No. {num}  ({op} um)" if num else "pan", txt, IC.MATERIALS[mat][:3])
            for _, num, op, txt, mat in reversed(IC.STACK)]
    lh, w = 24 * s, 312 * s
    h = (len(rows) + 2) * lh + 38 * s
    x0, y0 = W - w - 0.02 * W, 0.075 * H
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 8 * scale, fill=(255, 255, 255, int(236 * alpha)),
                        outline=(120, 124, 130, a))
    d.text((x0 + 10 * s, y0 + 6 * s), "What stays on each sieve", font=font(14.5 * s, bold=True), fill=(20, 20, 24, a))
    f = font(13 * s)
    for i, (name, txt, col) in enumerate(rows):
        yy = y0 + 32 * s + i * lh
        c = tuple(int(255 * v) for v in col)
        d.ellipse((x0 + 12 * s, yy + 3 * s, x0 + 26 * s, yy + 17 * s), fill=c + (a,))
        d.text((x0 + 34 * s, yy), name, font=f, fill=(20, 20, 24, a))
        d.text((x0 + 180 * s, yy), txt, font=font(13 * s, bold=True), fill=(20, 20, 24, a))
    yy = y0 + 32 * s + len(rows) * lh + 4 * s
    d.text((x0 + 12 * s, yy), "LPBF 20-63 um: No. 325 + pan", font=font(12.5 * s, bold=True), fill=(30, 60, 140, a))
    d.text((x0 + 12 * s, yy + 18 * s), "Amounts drawn are an example, not data", font=font(11.5 * s),
           fill=(150, 30, 30, a))


class Mir2:
    """alloy_workflow.Mir, which drives along x at MIR_Y, given a y as well, for the spot in front of the rePowder
    (whose front stands 300 mm proud of the line's)."""

    def __init__(self, amr):
        self.amr, self.sc, self.rb = amr, amr.sc, amr.rb
        self.y = AW.MIR_Y

    def place(self, x, y):
        self.amr.x, self.y = x, y
        self.sc.gmat["amr"] = T((x, y, 0))
        if self.rb.held is not None:
            self.rb.set()

    def drive(self, x1, y1=None):
        x0, y0 = self.amr.x, self.y
        y1 = AW.MIR_Y if y1 is None else y1

        def up(u):
            # turn the corner: y first for the first third, then along x
            uy = min(1.0, u / 0.35)
            ux = max(0.0, (u - 0.25) / 0.75) if abs(y1 - y0) > 1 else u
            self.place(x0 + (x1 - x0) * ux, y0 + (y1 - y0) * uy)
        return up

    def secs(self, x1, y1=None):
        y1 = AW.MIR_Y if y1 is None else y1
        return max(1.4, (abs(x1 - self.amr.x) + abs(y1 - self.y)) / AW.MIR_SPEED + 1.0)


def build():
    AW.NAME, AW.TITLE, AW.AlloyScene = NAME, TITLE, PrintScene      # chapter 4's build(), our name and scene class
    sc, L, rigs, W, E, amr = AW.build()
    AW.AlloyScene = PrintScene.__mro__[1]
    # the bench and the AS 200 on it
    top, legs = bench_mesh()
    sc.add("bench top", top, (0.28, 0.29, 0.31), "bench", specular=0.2)
    sc.add("bench frame", legs, (0.66, 0.67, 0.70), "bench", specular=0.4)
    inst, ents = tour.load(["sieve"])["sieve"]
    y_s = line.Y_FACE + 60.0 - inst.bbox()[2]
    sv = tour.Rig(sc, inst, ents, "sieve:", at=T((BENCH["x"] + SIEVE_DX, y_s, BENCH["h"])))
    sv.v["~container"] = 1.0 / 0.82                  # its own container: the arm carries ours instead
    sv.v["~carrier"] = 1.0 / 0.82
    sv.apply()
    # the MiR's cup for the container, then the bottle; the container on it
    mo = Mir2(amr)
    sc.add("amr/holder2", holder_mesh(amr.top), (0.94, 0.94, 0.92), "amr")
    parts, cpow = container_meshes()
    for name, (mesh, col) in parts.items():
        sc.add(f"pcont/{name}", mesh, col, "pcont", specular=0.5)
    sc.add("pcont/powder", cpow, POWDER, "pcont_pow", specular=0.05)
    sc.parent["pcont_pow"] = "pcont"
    seat = np.array([HOLDER_LOCAL[0], HOLDER_LOCAL[1], amr.top + HOLDER_H + 6.0])
    sc.parent["pcont"] = "amr"
    sc.gmat["pcont"] = T(seat)
    body, _cap, bpow = bottle_meshes()
    sc.add("bottle/body", body, (0.93, 0.93, 0.90), "bottle", opacity=0.55, specular=0.3)
    sc.add("bottle/powder", bpow, POWDER, "bottle_pow", specular=0.05)
    sc.parent["bottle_pow"] = "bottle"
    # streams and the laser
    sc.add("pstream", pv.PolyData(np.zeros((1, 3))), STREAM, "pstream", style="points", point_size=4.0,
           render_points_as_spheres=True)
    sc.alpha["pstream"] = 0.0
    beam = pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=1.6, height=1.0, resolution=12).triangulate()
    sc.add("laser beam", beam, LASER, "beam", ambient=1.0, diffuse=0.0, specular=0.0)
    sc.add("melt spot", pv.Sphere(radius=3.5, theta_resolution=12, phi_resolution=8), (1.0, 0.85, 0.55), "spot",
           ambient=1.0, diffuse=0.0, specular=0.0)
    sc.add("scan tracks", pv.PolyData(np.zeros((1, 3))), LASER, "tracks", ambient=1.0, diffuse=0.0, specular=0.0,
           line_width=3.0)
    for n_ in ("laser beam", "melt spot", "scan tracks"):
        sc.alpha[n_] = 0.0
    # the lug that grows during the print (chapter 4's lug is part of the plate group)
    x0, x1, y0, y1, z0, z1 = M.LUG
    sc.add("lug grow", pv.Box(bounds=(x0, x1, y0, y1, 0.0, 1.0)).triangulate(), M.AS_BUILT, "luggrow", specular=0.2)
    sc.parent["luggrow"] = "plate"
    sc.alpha["lug grow"] = 0.0
    mo.place(*START)
    return sc, L, rigs, W, E, amr, sv, mo


# ------------------------------------------------------------------------------------------------- moves
def level_y(p, spin):
    """Gripper level, pointing along +y (towards the machines), turned `spin` degrees about its own axis."""
    return P.tcp_frame(np.asarray(p, float), (0.0, 1.0, 0.0), spin)


def sieve_w(sv, p):
    return (sv.sc.world("sieve:body") @ np.r_[p, 1.0])[:3]


def hatch(z, step=1.6):
    """Scan vectors over the bars' outlines (while the build is under 6 mm) and the lug's, in the plate frame, as
    line segments; returns (bars, lug) point arrays of segment pairs."""
    q = M._half_outline()[:10]                      # the +x, +y quarter: (half width, y), y rising
    qx, qy = np.array([a for a, _ in q]), np.array([b for _, b in q])
    segs = []
    for x in M.BAR_X:
        for y in np.arange(-M.E8_SUB["L"] / 2 + 1, M.E8_SUB["L"] / 2 - 1, step * 2.2):
            w = float(np.interp(abs(y), qy, qx))
            segs.append(((x - w + 0.4, y, z), (x + w - 0.4, y, z)))
    lx0, lx1, ly0, ly1, _, _ = M.LUG
    lug = [((lx0 + 0.5, y, z), (lx1 - 0.5, y, z)) for y in np.arange(ly0 + 1, ly1 - 1, step * 2.0)]
    return segs, lug


def seg_poly(segs):
    if not segs:
        return pv.PolyData(np.zeros((1, 3)))
    pts = np.array([p for s in segs for p in s], float)
    lines = np.hstack([[2, 2 * i, 2 * i + 1] for i in range(len(segs))])
    return pv.PolyData(pts, lines=lines)


# ------------------------------------------------------------------------------------------------- the movie
def movie():
    sc, L, rigs, W, E, amr, sv, mo = build()
    rb = amr.rb
    PARK = np.radians(A.PARK_DEG)
    n = 5
    inst = sv.inst
    zl = 212.0 + 6 * IC.DEPTH - 8                       # the lid's datum (instruments_char.sieve: z_rim - 8)
    z_rim = 212.0 + 6 * IC.DEPTH
    rod_x = 132.0
    sv_c = sieve_w(sv, (0, 0, 0))
    aco_bp = W.world(W.bp())
    aco_x = aco_bp[0] - 146.0
    sup = W.world(M.build_point() + (0, M.ACO["sy"] - M.ACO["by"], 0))      # the supply cylinder's axis, floor level
    x_sv = sv_c[0] + 60.0                                                     # MiR at the bench

    CAM_RP = [(START[0] + 2300, -6400, 2600), (START[0] + 900, -1500, 900), (0, 0, 1)]
    CAM_SV = [tuple(sv_c + (-1250, -1650, 1250)), tuple(sv_c + (0, -120, 420)), (0, 0, 1)]
    CAM_SV_IN = [tuple(sv_c + (-980, -1380, 1000)), tuple(sv_c + (40, -60, 400)), (0, 0, 1)]
    CAM_JAR = [tuple(sv_c + (-700, -2600, 1650)), tuple(sv_c + (220, -560, 320)), (0, 0, 1)]
    CAM_FILL = [tuple(sup + (-420, -1350, 700)), tuple(sup + (0, -160, 40)), (0, 0, 1)]
    CAM_DRIVE = [(1200, -8800, 3600), (600, -1300, 900), (0, 0, 1)]
    CAM_ACO = [tuple(aco_bp + (-1700, -2300, 1500)), tuple(aco_bp + (100, -520, -120)), (0, 0, 1)]
    CAM_PRINT = [tuple(aco_bp + (-430, -390, 560)), tuple(aco_bp + (10, 40, -15)), (0, 0, 1)]
    CAM_LINE = [(aco_bp[0] + 2600, -9800, 4300), (aco_bp[0] + 2600, -1100, 900), (0, 0, 1)]    # chapter 4's first

    status(sc, Arm="UR10e on MiR250, parked", Powder="in the rePowder's container, on the MiR",
           Sieve="AS 200, empty", Aconity="idle")
    sc.cam = list(CAM_RP)
    lbl = [A.REPOWDER_LBL[:2] + ((0.12, 0.26),),
           ("Retsch AS 200 sieve shaker", tuple(sv_c + (0, 0, 600)), (0.50, 0.22)),
           ("the rePowder's powder container", tuple(mo.amr.world(np.r_[HOLDER_LOCAL, amr.top + HOLDER_H + 120])),
            (0.30, 0.62))]
    cap = "From the atomizer to the printer. The run's powder is in the rePowder's container, on the MiR250: two 5N Al " \
          "cups with Si, Al-10Si (78 g charged). Next, the sieve shaker beside the rePowder, then the Aconity MIDI."
    sc.step(f"1/{n}", cap, 2.4, None, hold=1.4, labels=lbl)

    # ------------------------------------------------------------------ 1. to the bench; container over the stack
    cap = "The MiR250 pulls up to the bench with the Retsch AS 200 and the lab's 8 in stack: No. 60, 100, 140, 230, " \
          "325 and a pan (DAL PR #175). The arm takes the container by its handle."
    status(sc, Arm="driving to the sieve shaker")
    sc.step(f"1/{n}", cap, mo.secs(x_sv), mo.drive(x_sv), hold=0.2, cam_to=CAM_SV,
            labels=[("Retsch AS 200 control, 8 in stack", tuple(sv_c + (180, 0, 560)), (0.62, 0.20))])
    g_hold = held_point(sc, "pcont", HANDLE_GRASP)
    status(sc, Arm="taking the container")
    sc.step(f"1/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=level_y(g_hold - (0, 140, -40), 90.0)), rb.grip_to(0.0)),
            hold=0.05)
    sc.step(f"1/{n}", cap, 0.9, rb.line_to(level_y(g_hold - (0, 0, 0), 90.0)), hold=0.05)
    sc.step(f"1/{n}", cap, 0.4, rb.grip_to(GRIP_HANDLE), hold=0.05)
    rb.grasp("pcont")
    sc.step(f"1/{n}", cap, 0.8, rb.line_to(level_y(g_hold + (0, 0, 120), 90.0)), hold=0.05)

    # ------------------------------------------------------------------ 2. pour, lid, knobs, shake
    th = 115.0
    m_rel = np.array([-45.0, 94.0, -13.0])                 # mouth from the grasp, upright
    c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
    m_rot = np.array([m_rel[0] * c + m_rel[2] * s_, m_rel[1], -m_rel[0] * s_ + m_rel[2] * c])
    target = sieve_w(sv, (-30.0, 0.0, z_rim + 90.0))
    p_tip = target - m_rot
    p_up = sieve_w(sv, (0, 0, 0)) + np.array([-215.0, -94.0, z_rim + 105.0])
    cap = "It tips the container into the No. 60 at the top of the stack."
    status(sc, Arm="pouring", Powder="onto the No. 60")
    sc.step(f"2/{n}", cap, 1.8, rb.joint_to(Tw=level_y(p_up, 90.0)), hold=0.05, cam_to=CAM_SV_IN)
    sc.step(f"2/{n}", cap, 1.6, rb.line_to(level_y(p_tip, 90.0 + th)), hold=0.05)
    heap_in = sv.move({f"frac_{k}": (0.0, 1.0) for k, *_ in IC.STACK})

    def pour(u):
        heap_in(min(1.0, u * 1.25))
        sc.gmat["pcont_pow"] = T((0, 0, 4)) @ S((1, 1, max(0.01, 60.0 * (1 - u))))
        sc.alpha["pcont/powder"] = 1.0 if u < 0.97 else 0.0
        mouth = held_point(sc, "pcont", MOUTH)
        pts = stream_pts(mouth, sieve_w(sv, (-20, 0, IC.MESH_DZ + z_rim - IC.DEPTH)), u * 5.0,
                         on=1.0 if 0.03 < u < 0.92 else 0.0)
        sc.alpha["pstream"] = 1.0 if len(pts) else 0.0
        if len(pts):
            sc.set_mesh("pstream", pv.PolyData(pts))
    sc.gmat["pcont_pow"] = T((0, 0, 4)) @ S((1, 1, 60.0))
    sc.step(f"2/{n}", cap, 2.4, pour, hold=0.2, live=False)
    sc.alpha["pstream"] = 0.0
    # the empty container down on the bench, at the shaker's left (where instruments_char's tour stands it)
    rest = sieve_w(sv, (-IC.SIEVE_SPECS["W"] / 2 - 150.0, -40.0, 0.0))
    g_rest = rest + HANDLE_GRASP
    cap = "The empty container goes down on the bench, to be cleaned before the next run."
    status(sc, Arm="setting the container down", Powder="on the No. 60")
    sc.step(f"2/{n}", cap, 1.2, rb.line_to(level_y(p_up, 90.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 1.4, rb.line_to(level_y(g_rest + (0, 0, 60), 90.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(level_y(g_rest, 90.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("sieve:body")
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(level_y(g_rest - (0, 130, -30), 90.0)), hold=0.05)

    # the lid: from the bench, up over the rods and down onto the stack, by its crossbar
    jl = inst.joints["lid"]

    def lid_grasp(v):
        return (sc.world("sieve:stack") @ jl.matrix(v) @ np.r_[0.0, 0.0, zl + 17.0, 1.0])[:3]
    cap = "The arm brings the AS 200's clamping lid over the two rods and down onto the stack, then turns its two " \
          "knobs to clamp it: no shaker found is sold for robot loading, so it does what a person does."
    status(sc, Arm="closing the lid")
    p_l0 = lid_grasp(0.0)
    sc.step(f"2/{n}", cap, 1.6, rb.joint_to(Tw=A.down(p_l0 + (0, 0, 120), spin=90.0)), hold=0.05, cam_to=CAM_SV)
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(A.down(p_l0, spin=90.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_BAR36), hold=0.05)
    rb.grasp("sieve:lid")
    path_u = [0.0, 1 / 3, 2 / 3, 1.0]                       # the joint's four path points
    for v in path_u[1:]:
        sc.step(f"2/{n}", cap, 0.8, rb.line_to(A.down(lid_grasp(v), spin=90.0)), hold=0.02)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("sieve:stack")
    sv.v["lid"] = 1.0
    sv.apply()
    for side in ("L", "R"):
        sx = -1 if side == "L" else 1
        k_top = sieve_w(sv, (sx * rod_x, 0, zl + 36.0))
        sc.step(f"2/{n}", cap, 0.7, rb.line_to(A.down(k_top + (0, 0, 70), spin=90.0)), hold=0.02)
        sc.step(f"2/{n}", cap, 0.4, rb.line_to(A.down(k_top, spin=90.0)), hold=0.02)
        sc.step(f"2/{n}", cap, 0.25, rb.grip_to(GRIP_KNOB), hold=0.02)
        q1 = rb.q.copy()
        q1[5] += -2 * math.pi if q1[5] > 0 else 2 * math.pi       # one full turn of the wrist, with the knob
        sc.step(f"2/{n}", cap, 0.9, RB.both(rb.joint_to(q1), sv.move({f"knob{side}": (0.0, 0.5)})), hold=0.02)
        sc.step(f"2/{n}", cap, 0.25, rb.grip_to(0.0), hold=0.02)
        sc.step(f"2/{n}", cap, 0.4, rb.line_to(A.down(k_top + (0, 0, 70), spin=90.0)), hold=0.02)
    sc.step(f"2/{n}", cap, 1.2, rb.joint_to(PARK), hold=0.05)
    status(sc, Arm="parked", Sieve="lid clamped")

    cap = "Sieving, the stack drawn see-through: 3-D throwing motion, amplitude 0.2-3 mm (Retsch). Each size class " \
          "falls until a cloth stops it. Al powder under 63 um is among the most ignitable metal dusts: the bench " \
          "wants bonding, grounding and extraction (DAL's sieve note)."
    status(sc, Sieve="shaking")
    sc.step(f"2/{n}", cap, 1.2, sv.move({"~stack": (0.0, 1.0), "~lid": (0.0, 1.0), "~knobL": (0.0, 1.0),
                                         "~knobR": (0.0, 1.0)}), hold=0.05, cam_to=CAM_SV_IN)
    sc.step(f"2/{n}", cap, 5.0, sv.move({"stack": (0.0, 1.0), **{f"fall_{k}": (0.0, 1.0) for k, *_ in IC.STACK}}),
            hold=0.1)

    def panel(u):
        sc.panel_a = u
    status(sc, Sieve="done: six fractions")
    cap = "The fractions, by the sieve that keeps each. The LPBF cut, 20-63 um, is the No. 325 and the pan: there " \
          "is no 20 um sieve, and DAL found under 20 um is about 0.05 % by mass."
    sc.step(f"2/{n}", cap, 0.8, panel, hold=3.4,
            labels=[("No. 325 (45 um)", tuple(sieve_w(sv, (IC.RW + IC.LIP, 0, 212.0 + IC.DEPTH + 10))), (0.40, 0.70)),
                    ("pan", tuple(sieve_w(sv, (IC.RW + IC.LIP, 0, 212.0 + 10))), (0.40, 0.80))])

    # ------------------------------------------------------------------ 3. the LPBF cut into a bottle (a person)
    bott_seat = sieve_w(sv, (IC.SIEVE_SPECS["W"] / 2 + 122.0, -215.0, 0.0))
    sc.gmat["bottle"] = T(bott_seat)
    sc.alpha["bottle/body"] = 0.0
    sc.alpha["bottle/powder"] = 0.0
    cap = "Taking the stack apart is left to a person, in a respirator, under extraction: the cut is the finest, " \
          "most ignitable powder of the run. The No. 325's and the pan's powder go into a jar."

    def unclamp(u):
        sv.move({"~stack": (1.0, 0.0), "~lid": (1.0, 0.0), "~knobL": (1.0, 0.0), "~knobR": (1.0, 0.0),
                 "knobL": (0.5, 0.0), "knobR": (0.5, 0.0)})(u)
        sc.panel_a = 1.0 - u
    status(sc, Sieve="unclamped (by hand)", Powder="20-63 um, into a jar (by hand)")
    sc.step(f"3/{n}", cap, 1.2, unclamp, hold=0.1, cam_to=CAM_SV)
    sc.panel_a = 0.0
    lid_home = sv.move({"lid": (1.0, 0.0)})

    def bottle_in(u):
        lid_home(u)
        sc.alpha["bottle/body"] = 0.55 * u
        sc.alpha["bottle/powder"] = u
        sc.gmat["bottle_pow"] = T((0, 0, 3.5)) @ S((1, 1, 58.0))
        for k in ("pan", "s325"):
            sv.v[f"frac_{k}"] = 1.0 - u
        sv.apply()
    sc.step(f"3/{n}", cap, 1.8, bottle_in, hold=0.8,
            labels=[("the LPBF cut, 20-63 um", tuple(bott_seat + (0, 0, 160)), (0.70, 0.30))])
    status(sc, Powder="20-63 um, in the jar")

    # the arm takes the bottle to the MiR's cup
    b_grasp = bott_seat + (0, 0, 58.0)
    seat = mo.amr.world(np.r_[HOLDER_LOCAL[0], HOLDER_LOCAL[1], amr.top + HOLDER_H + 6.0])
    cap = "The arm takes the jar and stands it in the cup on the MiR's cabinet."
    status(sc, Arm="taking the jar")
    sc.step(f"3/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=level_y(b_grasp - (0, 150, 0), 0.0)), rb.grip_to(0.0)), hold=0.05,
            cam_to=CAM_JAR)
    sc.step(f"3/{n}", cap, 0.9, rb.line_to(level_y(b_grasp, 0.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 0.4, rb.grip_to(GRIP_BOTTLE), hold=0.05)
    rb.grasp("bottle")
    sc.step(f"3/{n}", cap, 0.8, rb.line_to(level_y(b_grasp + (0, 0, 120), 0.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 1.6, rb.line_to(level_y(seat + (0, 0, 58.0 + 110), 0.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 0.8, rb.line_to(level_y(seat + (0, 0, 58.0), 0.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("amr")
    sc.step(f"3/{n}", cap, 0.7, rb.line_to(level_y(seat + (0, -140, 58.0), 0.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 1.2, rb.joint_to(PARK), hold=0.05)
    status(sc, Arm="parked", Powder="20-63 um, in the jar on the MiR")

    # ------------------------------------------------------------------ 4. to the Aconity; into the powder supply
    cap = f"To the Aconity MIDI, {(aco_x - x_sv) / 1000:.1f} m along the line, past the VLM's opening."
    status(sc, Arm="driving to the Aconity MIDI")
    sc.step(f"4/{n}", cap, mo.secs(aco_x), mo.drive(aco_x), hold=0.2, cam_to=CAM_DRIVE)
    cap = "The door opens, and the chamber is drawn see-through. The MIDI's 170 mm build cylinder is at the front; " \
          "the 170 mm powder supply cylinder is behind it (DAL PR #169). Its piston drops to take the powder."
    status(sc, Aconity="door open, supply down")
    sup_drop = 70.0

    def supply_down(u):
        sc.gmat["aco_supply"] = T((0, 0, -sup_drop * u))
    sc.step(f"4/{n}", cap, 1.6, RB.both(W.door(1.0), W.ghost(1.0)), hold=0.1, cam_to=CAM_ACO,
            labels=[("powder supply, 170 mm", tuple(sup + (0, 0, 40)), (0.16, 0.34)),
                    ("build cylinder, 170 mm", tuple(aco_bp + (0, 0, -40)), (0.18, 0.62))])
    sc.step(f"4/{n}", cap, 1.0, supply_down, hold=0.1)
    # take the bottle again, carry it in level, over the supply, and tip it
    seat_now = held_point(sc, "bottle", (0, 0, 58.0))
    cap = "The arm carries the jar in, level, over the supply cylinder, and turns its wrist to pour. One run's " \
          "cut is tens of grams; a 30 mm build in a 170 mm cylinder takes about 1 kg in the bed, so in practice " \
          "the supply is topped up from many runs, or a smaller build cylinder is fitted."
    status(sc, Arm="filling the supply")
    sc.step(f"4/{n}", cap, 1.4, RB.both(rb.joint_to(Tw=level_y(seat_now - (0, 150, 0), 0.0)), rb.grip_to(0.0)),
            hold=0.05, cam_to=CAM_FILL)
    sc.step(f"4/{n}", cap, 0.8, rb.line_to(level_y(seat_now, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.4, rb.grip_to(GRIP_BOTTLE), hold=0.05)
    rb.grasp("bottle")
    sc.step(f"4/{n}", cap, 0.8, rb.line_to(level_y(seat_now + (0, 0, 150), 0.0)), hold=0.05)
    door_front = W.world(np.array(M.door_pivot()))[1]
    p_in0 = np.array([sup[0] - 60.0, door_front - 150.0, sup[2] + 95.0])
    p_pour = np.array([sup[0] - 60.0, sup[1], sup[2] + 95.0])
    sc.step(f"4/{n}", cap, 1.6, rb.joint_to(Tw=level_y(p_in0, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 1.6, rb.line_to(level_y(p_pour, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 1.0, rb.line_to(level_y(p_pour, 112.0)), hold=0.05)

    def fill(u):
        sc.gmat["bottle_pow"] = T((0, 0, 3.5)) @ S((1, 1, max(0.01, 58.0 * (1 - u))))
        sc.alpha["bottle/powder"] = 1.0 if u < 0.97 else 0.0
        sc.gmat["aco_supply"] = T((0, 0, -sup_drop * (1 - u)))
        mouth = held_point(sc, "bottle", (0, 0, BOT_H + NECK_H))
        pts = stream_pts(mouth, (mouth[0] + 8, mouth[1], sup[2] - sup_drop * (1 - u) - 1), u * 5.0,
                         on=1.0 if 0.03 < u < 0.93 else 0.0)
        sc.alpha["pstream"] = 1.0 if len(pts) else 0.0
        if len(pts):
            sc.set_mesh("pstream", pv.PolyData(pts))
    sc.step(f"4/{n}", cap, 2.4, fill, hold=0.2, live=False)
    sc.alpha["pstream"] = 0.0
    status(sc, Aconity="supply filled")
    cap = "The empty jar goes back on the MiR, and the door shuts. The chamber is purged with argon before the " \
          "laser runs."
    sc.step(f"4/{n}", cap, 0.8, rb.line_to(level_y(p_pour, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 1.4, rb.line_to(level_y(p_in0, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 1.6, rb.joint_to(Tw=level_y(seat_now + (0, 0, 150), 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.8, rb.line_to(level_y(seat_now, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("amr")
    sc.step(f"4/{n}", cap, 0.7, rb.line_to(level_y(seat_now - (0, 140, 0), 0.0)), hold=0.05)
    status(sc, Arm="parked", Powder="in the MIDI's supply")
    sc.step(f"4/{n}", cap, 1.4, RB.both(rb.joint_to(PARK), W.door(0.0)), hold=0.2)

    # ------------------------------------------------------------------ 5. the print, as a time-lapse
    layers = int(round(W.build_h * 1000.0 / LAYER_UM))
    cap = f"The print, sped up and cut open: the recoater spreads a layer from the supply over the build cylinder, " \
          f"the laser melts the bars' and the lug's outlines, the platform drops one layer. {layers} layers of " \
          f"{LAYER_UM:.0f} um (assumed) make the {W.build_h:.0f} mm build."
    status(sc, Aconity="printing (argon)", Arm="parked; free for other work")
    plate_top0 = W.floor
    W.set_piston(plate_top0 - M.PLATE["t"])
    bar_groups = [f"bar{k}" for k in range(4)]
    sc.alpha["plate/lug"] = 0.0
    bar_names = [f"bar{k}/a" for k in range(4)] + [f"bar{AW.TEST}/b"]
    for nm in bar_names + ["lug grow"]:
        sc.alpha[nm] = 0.0                      # nothing on the plate before the first layer
    for g in bar_groups:
        sc.gmat[g] = T((M.BAR_X[int(g[3:])], 0, 0)) @ S((1, 1, 0.01))
    sc.gmat["luggrow"] = S((1, 1, 0.01))
    beam_top = W.world(M.build_point(M.ACO["floor"] + 270.0))
    segs_b, segs_l = hatch(0.0)
    cycles = 6
    rec_dy = -420.0

    def print_up(u):
        h = W.build_h * min(1.0, u * 1.0)
        W.set_piston(W.floor - M.PLATE["t"] - h)
        sc.alpha["aco powder cake"] = 0.38 if h > 0.6 else 0.0
        sb = min(1.0, h / M.E8_SUB["T"])
        for nm in bar_names + ["lug grow"]:
            sc.alpha[nm] = 1.0 if h > 0.05 else 0.0
        for g in bar_groups:
            sc.gmat[g] = T((M.BAR_X[int(g[3:])], 0, 0)) @ S((1, 1, max(0.01, sb)))
        sc.gmat["luggrow"] = S((1, 1, max(0.01, h)))
        c_ = (u * cycles) % 1.0
        if u >= 1.0:
            c_ = 1.0
        # recoat in the first 35 % of each cycle: to the front and back; then the scan
        if c_ < 0.35:
            w_ = c_ / 0.35
            sc.gmat["aco_recoater"] = T((0, rec_dy * math.sin(math.pi * w_), 0))
            on = False
        else:
            sc.gmat["aco_recoater"] = np.eye(4)
            on = u < 1.0
        segs = (segs_b if h < M.E8_SUB["T"] else []) + segs_l
        k = int(len(segs) * min(1.0, (c_ - 0.35) / 0.6)) if on else 0
        for nm in ("laser beam", "melt spot", "scan tracks"):
            sc.alpha[nm] = 1.0 if on and k > 0 else 0.0
        if on and k > 0:
            plate_w = sc.world("plate")
            pts = [((plate_w @ np.r_[a[0], a[1], h + 0.25, 1.0])[:3], (plate_w @ np.r_[b[0], b[1], h + 0.25, 1.0])[:3])
                   for a, b in segs[:k]]
            sc.set_mesh("scan tracks", seg_poly(pts))
            spot = pts[-1][1]
            sc.gmat["spot"] = T(spot)
            sc.gmat["beam"] = T(spot) @ S((1, 1, max(1.0, beam_top[2] - spot[2])))
        status(sc, Aconity=f"printing, layer {int(layers * min(1.0, u)):d} of {layers}")
    sc.step(f"5/{n}", cap, 1.4, W.ghost(1.0), hold=0.05, cam_to=CAM_PRINT,
            labels=[("recoater", tuple(W.world(M.build_point() + (0, 300, 40))), (0.70, 0.30)),
                    ("build platform", tuple(aco_bp + (0, 0, -20)), (0.18, 0.62))])
    handle = [nm for nm in W.names["door"] if "printer_black" in nm]     # the door's handle: in front of the plate
    for nm in handle:
        sc.alpha[nm] = 0.0
    lbl_laser = [("laser (beam drawn)", tuple(beam_top), (0.70, 0.18))]
    if PREVIEW:                     # a frame mid-scan in the preview sheet as well
        sc.step(f"5/{n}", cap, 4.0, lambda e: print_up(0.45 * e), hold=0.0, labels=lbl_laser)
        sc.step(f"5/{n}", cap, 5.0, lambda e: print_up(0.45 + 0.55 * e), hold=0.4, labels=lbl_laser)
    else:
        sc.step(f"5/{n}", cap, 9.0, print_up, hold=0.4, labels=lbl_laser)
    for nm in ("laser beam", "melt spot", "scan tracks"):
        sc.alpha[nm] = 0.0
    sc.gmat["aco_recoater"] = np.eye(4)
    for g in bar_groups:
        sc.gmat[g] = T((M.BAR_X[int(g[3:])], 0, 0))
    sc.alpha["plate/lug"] = 1.0
    for nm in bar_names:
        sc.alpha[nm] = 1.0
    sc.alpha["lug grow"] = 0.0
    W.set_piston(W.floor - W.build_h - M.PLATE["t"])
    status(sc, Aconity="print done, under powder")

    cap = "Printed: four ASTM E8 subsize bars and a handling lug on the 170 mm plate, buried in powder. The MiR " \
          "comes back along the line, and chapter 4 takes the plate from here."

    sc.step(f"5/{n}", cap, 1.2, W.ghost(0.0), hold=0.1, cam_to=CAM_ACO)
    status(sc, Arm="UR10e on MiR250, parked", Powder="", Sieve="", Aconity="", Plate="in the Aconity MIDI")
    sc.step(f"5/{n}", cap, mo.secs(MIR_END), mo.drive(MIR_END), hold=0.2, cam_to=CAM_LINE)
    sc.step(f"5/{n}", cap, 0.6, None, hold=1.6, still=True,
            labels=[("Aconity MIDI metal printer", (line.LINE["aconity"], line.Y_FACE + 300, 2400), (0.22, 0.20)),
                     ("UR10e on a MiR250", tuple(amr.world((0, 0, 1300))), (0.10, 0.45))])
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    info = sc.save()
    return info


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in ("movie",):
        raise SystemExit(__doc__)
    print(movie(), flush=True)
