"""Animated GIFs of how the charge parts get made and loaded (issue #222).

Same build123d model as ``charge_cad.py``: every frame re-revolves the real
profile with the cut taken so far, so what you are watching is the CAD, not a
cartoon.  Drilling is shown as a half section, so the hole is visible.

  machining_cup.gif   face, drill, part off -> the cup, then an annotated spin
  machining_plug.gif  turn down, chamfer, vent-drill, part off -> the lid
  fill_and_vent.gif   fill with powder, press the lid in, pump the chamber down

Usage (needs an X server):  xvfb-run -a python machining.py
"""

from __future__ import annotations

import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
from build123d import Align, Axis, Box, Cylinder, Plane, Polyline, Pos, Rot, extrude, make_face, revolve
from PIL import Image

import charge_cad as cad
import render as rr

rr.MAT["al"] = ("#c9ced5", "#e2e6ea")

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "anim"

SS = 2  # supersample, then downscale
W, H = 720, 410
IN = cad.IN
R = cad.STOCK_D / 2
RB = cad.CUP_BORE_D / 2
RV = cad.VENT_D / 2

STICK = 82.0  # bar out of the chuck jaws for the cup
STICK_PLUG = 46.0  # shorter stub for the lid
CUP_L = cad.SLUG_L
Z_PART = STICK - CUP_L  # parting plane, from the chuck face

INK, INK2 = rr.INK, rr.INK2
STEEL = ("#46525f", "#77828e")  # cutting tools: dark, so they read against the aluminium
TOOL = ("#3d4a57", "#76828e")  # holders and blades
CARBIDE = ("#b8912f", "#d8b969")  # the tip itself, so you can see where the cut is
CHUCK_C = ("#6d737b", "#a7adb5")
JAW_C = ("#98a0a8", "#c2c8ce")

STRIPE = "#d03b3b"
AIR = "#2a78d6"
HALO = [pe.withStroke(linewidth=3.0 * SS, foreground="white")]

CAM_DIR = (0.38, -0.92, 0.55)
CAM_FOCAL = (38, 0, -1)
CAM_SCALE = 46
CAM_FOCAL_PLUG = (22, 0, -1)
CAM_SCALE_PLUG = 32


def fs(px: float) -> float:
    """Font size in points that lands at `px` pixels in the finished GIF."""
    return px * SS * 0.72


# ---------------------------------------------------------------------------
# Geometry.  Only the workpiece changes shape frame to frame.
# ---------------------------------------------------------------------------
def turned(profile):
    return revolve(Plane.XZ * make_face(Polyline(*profile, close=True)), Axis.Z, 360)


def lay(shape):
    """Stand a Z-axis part on its side: local +Z becomes the lathe axis +X."""
    return Rot(0, 90, 0) * shape


def lay_rev(shape):
    """Same, but local +Z points back at the chuck - for a part cut nose-outward."""
    return Rot(0, -90, 0) * shape


def _clean(pts, eps=1e-6):
    """Drop repeated points - a zero-length edge makes the revolve fail outright."""
    out = [pts[0]]
    for q in pts[1:]:
        if abs(q[0] - out[-1][0]) > eps or abs(q[1] - out[-1][1]) > eps:
            out.append(q)
    return out


GROOVE_W = 2.8  # parting groove: a hair wider than the 2.2 mm blade, so nothing overlaps


def bar_profile(stick=STICK, face=0.0, face_r=None, bore_d=cad.CUP_BORE_D, bore=0.0,
                groove_z=None, groove_r=None, groove_w=GROOVE_W, step_z=None, step_r=None,
                lead=0.0, chamf_z=None, chamf=0.0):
    """Half-profile (r, z) of the bar with the cuts taken so far, z always increasing.

    face / face_r  facing cut `face` deep, reached in as far as radius `face_r`
    bore           hole `bore` deep, diameter `bore_d`, drilled into the free end
    step_z/step_r  OD turned down to `step_r`, from `step_z` out to the free end
    lead           15 deg lead-in of that length on the very end of the step
    chamf_z/chamf  45 deg break of size `chamf` on the +z side of a notch at `chamf_z`
    groove_*       parting groove `groove_w` wide, centred on `groove_z`, down to `groove_r`

    A groove is always cut at whatever the bar's diameter is *there*, which is what the
    earlier version got wrong: it grooved at full diameter inside a turned-down section,
    so the profile doubled back on itself and the revolve came out self-intersecting.
    """
    end = stick - face
    stepped = step_z is not None and step_r is not None and step_r < R

    def od(z):
        return step_r if stepped and z >= step_z - 1e-9 else R

    if face_r is not None and 0.05 < face_r < R - 0.02:  # part way through facing
        return _clean([(0.0, 0.0), (R, 0.0), (R, end), (face_r, end), (face_r, stick), (0.0, stick)])
    if face_r is not None and face_r >= R - 0.02:  # tool has only just touched
        return _clean([(0.0, 0.0), (R, 0.0), (R, stick), (0.0, stick)])

    pts = [(0.0, 0.0), (R, 0.0)]
    events = []
    if stepped:
        events.append((step_z, 0, "step"))
    if groove_z is not None and groove_r is not None:
        events.append((groove_z - groove_w / 2, 1, "groove"))
    if chamf_z is not None and chamf > 0:
        events.append((chamf_z, 2, "chamf"))
    # a chamfer sitting on the groove's far wall is one corner, not two features
    on_groove = (chamf_z is not None and chamf > 0 and groove_z is not None
                 and groove_r is not None and abs(groove_z + groove_w / 2 - chamf_z) < 1e-6)

    for _, _, kind in sorted(events):
        if kind == "step":
            pts += [(R, step_z), (step_r, step_z)]
        elif kind == "groove":
            r0 = od(groove_z)
            g0, g1 = groove_z - groove_w / 2, groove_z + groove_w / 2
            if groove_r < r0:
                pts += [(r0, g0), (groove_r, g0), (groove_r, g1)]
                pts += [(r0 - chamf, g1), (r0, g1 + chamf)] if on_groove else [(r0, g1)]
        elif not on_groove:
            r0 = od(chamf_z)
            pts += [(r0, chamf_z), (r0 - chamf, chamf_z), (r0, chamf_z + chamf)]

    if stepped:
        if lead > 0:
            pts += [(step_r, end - lead), (step_r - lead * math.tan(math.radians(15)), end)]
        else:
            pts += [(step_r, end)]
    else:
        pts += [(R, end)]
    if bore > 0:
        rb = bore_d / 2
        pts += [(rb, end), (rb, end - bore), (0.0, end - bore - cad.drill_point_h(bore_d))]
    else:
        pts += [(0.0, end)]

    return _clean(pts)


def drill(d, length, flute=None):
    """Twist drill laid along +X with its point at the origin.

    Drawn a hair under size so its flank does not z-fight the hole it just cut.
    A small drill gets a fatter shank behind the flutes, as a real one has.
    """
    r = d / 2 * 0.94
    flute = flute if flute is not None else length
    pts = [(0, 0), (r, cad.drill_point_h(d)), (r, flute)]
    if r < 2.0:  # a small drill gets a fatter shank behind the flutes
        pts += [(2.0, flute), (2.0, length)]
    elif flute < length:
        pts += [(r, length)]
    return lay(turned(pts + [(0, pts[-1][1])]))


def parting_blade():
    """Thin blade, cutting edge at the origin, body running back toward the operator."""
    return Box(2.2, 34, 19, align=(Align.CENTER, Align.MAX, Align.CENTER))


def turning_tool_insert():
    """The carbide tip only, nose at the origin, cutting edges facing the work (+Y)."""
    dia = [(0.0, 0.0), (8.2, -0.7), (8.9, -8.9), (0.7, -8.2)]  # 80 deg rhombic
    return Pos(0, 0, -1.8) * extrude(Plane.XY * make_face(Polyline(*dia, close=True)), 3.6)


def turning_tool_holder():
    """The shank the tip sits in, leaving toward +X and -Y - clear of the work.

    The previous version pointed the shank at the chuck along -X, so on any frame where
    the bar was bigger than the cut, the holder and tip were drawn buried inside it.
    """
    body = [(6.4, -1.6), (30.0, -15.6), (24.6, -24.7), (1.0, -10.7)]
    return Pos(0, 0, -3.4) * extrude(Plane.XY * make_face(Polyline(*body, close=True)), 6.8)


def chuck_body():
    return lay(Cylinder(30, 26, align=(Align.CENTER, Align.CENTER, Align.MAX)))


def chuck_jaws():
    jaws = None
    for k in range(3):
        jaw = Pos(-7, 0, R + 8) * Box(22, 13, 18, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        jaw += Pos(-7, 0, R + 17) * Box(22, 18, 12, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        jaw = Rot(120 * k, 0, 0) * jaw
        jaws = jaw if jaws is None else jaws + jaw
    return jaws


# ---------------------------------------------------------------------------
# build123d -> PyVista.  Fixed shapes are tessellated once and then moved.
# ---------------------------------------------------------------------------
CACHE: dict[str, tuple] = {}


def tessellate(shape, cut=False, tol=0.03, n=44):
    """(body mesh, cut-face mesh, edges); cut=True slices the near half away."""
    solid = rr.halve(shape) if cut else shape
    faces, section = [], []
    for f in solid.faces():
        (section if cut and rr.is_cut_face(f) else faces).append(f)
    return (rr.merged([rr.face_poly(f, tol) for f in faces]),
            rr.merged([rr.face_poly(f, tol) for f in section]),
            rr.edge_lines(solid, n=n))


def cached(key, make, **kw):
    if key not in CACHE:
        CACHE[key] = tessellate(make(), **kw)
    return CACHE[key]


def show(pl, trio, mat, lw=1.0, move=None, spin=None, powder=False):
    faces, section, lines = trio
    face_c, cut_c = mat if isinstance(mat, tuple) else (mat, mat)
    for mesh, colour, style in ((faces, face_c, rr.CUT_POWDER if powder else rr.BODY),
                                (section, cut_c, rr.CUT_POWDER if powder else rr.CUT),
                                (lines, rr.EDGE, None)):
        if mesh is None:
            continue
        if spin:
            mesh = mesh.rotate_x(spin, point=(0, 0, 0), inplace=False)
        if move is not None:
            mesh = mesh.translate(move, inplace=False)
        if style is None:
            pl.add_mesh(mesh, color=colour, line_width=lw * SS)
        else:
            pl.add_mesh(mesh, color=colour, **style)


def stripes(x0, x1, phase, front_only=False, n=3):
    """Marks on the bar surface, so you can see it turning."""
    out = []
    rad = R + 0.12
    for k in range(n):
        a = math.radians(phase + 360 / n * k)
        y, z = rad * math.cos(a), rad * math.sin(a)
        if front_only and y < 0.3 * rad:
            continue
        out.append(pv.lines_from_points(np.array([[x0, y, z], [x1, y, z]])))
    return pv.merge(out) if out else None


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------
class Scene:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.pl = pv.Plotter(off_screen=True, window_size=(w * SS, h * SS), lighting="light_kit")
        self.pl.set_background("white")
        self.pl.enable_parallel_projection()
        self.frames: list[np.ndarray] = []
        self.holds: list[float] = []

    def camera(self, focal, direction, scale):
        d = np.array(direction, float)
        d /= np.linalg.norm(d)
        self.pl.camera_position = [tuple(np.array(focal) + 900 * d), tuple(focal), (0, 0, 1)]
        self.pl.camera.parallel_scale = scale

    def grab(self, title=None, caption=None, callouts=(), dims=(), hold=1, step=None, note=None):
        img = self.pl.screenshot(return_img=True)
        anchors = rr.project(self.pl, [c[1] for c in callouts]) if callouts else []
        dim_px = [rr.project(self.pl, [d["p1"], d["p2"]]) for d in dims]
        self.frames.append(self._compose(img, title, caption, callouts, anchors, dims, dim_px, step, note))
        self.holds.append(hold)

    def _compose(self, img, title, caption, callouts, anchors, dims, dim_px, step, note):
        h, w = img.shape[:2]
        fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(img)
        ax.set_xlim(0, w)
        ax.set_ylim(h, 0)
        ax.axis("off")
        for (text, _, (tx, ty), ha), (x, y) in zip(callouts, anchors):
            ax.annotate(text, xy=(x, y), xytext=(tx * w, ty * h), fontsize=fs(11.5), color=INK, ha=ha,
                        va="center", linespacing=1.3, path_effects=HALO,
                        arrowprops=dict(arrowstyle="-", color=INK2, lw=0.9 * SS, shrinkA=4, shrinkB=1,
                                        path_effects=HALO))
            ax.plot([x], [y], "o", ms=3.0 * SS, color=INK2, markeredgecolor="white", markeredgewidth=0.8 * SS)
        for d, p in zip(dims, dim_px):
            ax.annotate("", xy=p[1], xytext=p[0],
                        arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.0 * SS, mutation_scale=7 * SS,
                                        shrinkA=0, shrinkB=0, path_effects=HALO))
            mid = p[0] + d.get("t", 0.5) * (p[1] - p[0])
            off = np.array(d.get("off", (0, -13)), float) * SS
            ax.text(*(mid + off), d["text"], fontsize=fs(11.5), color=INK, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.88))
        if title:
            ax.text(0.03 * w, 0.075 * h, f"{step}  {title}" if step else title, fontsize=fs(18), color=INK,
                    weight="bold", va="center")
        if note:
            ax.text(0.03 * w, 0.15 * h, note, fontsize=fs(11), color=INK2, va="center", style="italic",
                    path_effects=HALO)
        if caption:
            ax.text(0.03 * w, 0.935 * h, caption, fontsize=fs(13), color=INK2, va="center")
        fig.canvas.draw()
        arr = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
        plt.close(fig)
        return np.asarray(Image.fromarray(arr).resize((self.w, self.h), Image.LANCZOS))

    def save(self, name, ms=200, tail_ms=2400, colours=128):
        imgs = [Image.fromarray(f) for f in self.frames]
        sample = Image.fromarray(np.vstack(self.frames[:: max(1, len(self.frames) // 10)]))
        pal = sample.quantize(colors=colours, method=Image.MEDIANCUT)
        q = [im.quantize(palette=pal, dither=Image.NONE) for im in imgs]
        durations = [max(20, int(round(h * ms))) for h in self.holds]
        durations[-1] = tail_ms
        path = OUT / name
        q[0].save(path, save_all=True, append_images=q[1:], duration=durations, loop=0, optimize=True, disposal=2)
        self.pl.close()
        print(f"wrote anim/{name}  {len(q)} frames  {path.stat().st_size / 1024:.0f} kB")


def ease(i, n):
    """0..1 with a soft start and stop, so the tool does not jerk."""
    return 0.5 - 0.5 * math.cos(math.pi * i / max(1, n - 1))


RPM = 33.0  # degrees of spindle rotation per frame


def lathe_frame(sc, profile, phase, tools=(), cut=False, stick=STICK, focal=CAM_FOCAL, scale=CAM_SCALE,
                stripe_to=None, **kw):
    """One frame: chuck + workpiece + whatever tools are in the cut."""
    pl = sc.pl
    pl.clear()
    show(pl, cached("chuck", chuck_body), CHUCK_C, lw=0.7, spin=phase)
    show(pl, cached("jaws", chuck_jaws), JAW_C, lw=0.7, spin=phase)
    show(pl, tessellate(lay(turned(profile)), cut=cut), rr.MAT["al"], lw=1.1)
    marks = stripes(2.0, stripe_to if stripe_to is not None else stick, phase, front_only=cut)
    if marks is not None:
        pl.add_mesh(marks, color=STRIPE, line_width=2.0 * SS)
    for trio, mat, move in tools:
        show(pl, trio, mat, lw=0.8, move=move)
    sc.camera(focal, CAM_DIR, scale)
    sc.grab(**kw)


# ---------------------------------------------------------------------------
# 1. The cup
# ---------------------------------------------------------------------------
def cutter(x, y, z=0.0):
    """Tip and holder, placed with the cutting point at (x, y, z)."""
    pos = (x, y, z)
    return [(cached("tip", turning_tool_insert), CARBIDE, pos),
            (cached("holder", turning_tool_holder), TOOL, pos)]


def cup_gif():
    sc = Scene()
    spin = 0.0
    blade = cached("blade", parting_blade)
    bit = cached("bit", lambda: drill(cad.CUP_BORE_D, 40))
    depth = cad.CUP_BORE_DEPTH
    cap = "3/4 in 6063 bar. Two cups per run, so this is done twice."
    cut_face = 0.6  # how much comes off the end

    for i in range(4):  # bring the tool in, still clear of the bar
        t = ease(i, 4)
        lathe_frame(sc, bar_profile(), spin, hold=0.8,
                    tools=cutter(STICK + 1.4, -(R + 9 - 8.4 * t), 0),
                    title="Face the end", step="1 of 4", caption=cap)
        spin += RPM

    for i in range(9):  # sweep in from the OD to the centre
        t = ease(i, 9)
        fr = R * (1 - t)
        lathe_frame(sc, bar_profile(face=cut_face, face_r=fr), spin, hold=1 if i < 8 else 3.5,
                    stripe_to=STICK - cut_face,
                    tools=cutter(STICK - cut_face, -fr, 0),
                    title="Face the end", step="1 of 4", caption=cap)
        spin += RPM

    for i in range(12):  # drill
        t = ease(i, 12)
        d = depth * t
        lathe_frame(sc, bar_profile(face=cut_face, bore=d), spin, cut=True, stripe_to=STICK - cut_face,
                    tools=[(bit, STEEL, (STICK - cut_face - d, 0, 0))],
                    title="Drill the pocket", step="2 of 4", note="cut in half so you can see in",
                    caption=f"1/2 in hole, {depth / IN:.2f} in deep - three quarters of the way down.")
        spin += RPM
    lathe_frame(sc, bar_profile(face=cut_face, bore=depth), spin, cut=True, stripe_to=STICK - cut_face,
                tools=[(bit, STEEL, (STICK - cut_face - depth, 0, 0))],
                title="Then ream it", step="2 of 4", note="cut in half so you can see in", hold=6,
                caption="A reamer follows the drill, so the hole is round and on size for the lid.")
    spin += RPM

    gz = Z_PART - GROOVE_W / 2  # blade on the scrap side, so the cup comes out 2.5 in long
    for i in range(11):  # part off
        t = ease(i, 11)
        r = max(R - (R + 0.4) * t, 0.2)
        lathe_frame(sc, bar_profile(face=cut_face, bore=depth, groove_z=gz, groove_r=r), spin,
                    stripe_to=STICK - cut_face,
                    tools=[(blade, TOOL, (gz, -r, 0))], hold=1 if i < 10 else 2.5,
                    title="Cut it off at 2.5 in", step="3 of 4",
                    caption="A parting blade drops in and the cup comes free.")
        spin += RPM

    for i in range(6):  # the cup comes free
        t = ease(i, 6)
        pl = sc.pl
        pl.clear()
        show(pl, cached("chuck", chuck_body), CHUCK_C, lw=0.7, spin=spin)
        show(pl, cached("jaws", chuck_jaws), JAW_C, lw=0.7, spin=spin)
        show(pl, tessellate(lay(turned(bar_profile(stick=Z_PART - GROOVE_W)))), rr.MAT["al"], lw=1.1)
        show(pl, cached("cup_lathe", lambda: lay(cad.build()["std_cup"])), rr.MAT["al"], lw=1.1,
             move=(Z_PART + 14 * t, 0, -18 * t * t))
        marks = stripes(2.0, Z_PART - GROOVE_W - 0.4, spin)
        if marks is not None:
            pl.add_mesh(marks, color=STRIPE, line_width=2.0 * SS)
        sc.camera(CAM_FOCAL, CAM_DIR, CAM_SCALE)
        sc.grab(title="Cut it off at 2.5 in", step="3 of 4", hold=0.9,
                caption="A parting blade drops in and the cup comes free.")
        spin += RPM

    cup = cad.build()["std_cup"]
    wall = (cad.STOCK_D - cad.CUP_BORE_D) / 2
    n = 16
    for i in range(n):
        sc.pl.clear()
        last = i == n - 1
        show(sc.pl, cached(f"cup{i}", lambda i=i: Rot(0, 0, 360 / n * i) * cup, cut=last), rr.MAT["al"], lw=1.2)
        sc.camera((10, 5.5, CUP_L / 2), (0.55, -1.0, 0.42), 41)
        sc.grab(title="The cup", step="4 of 4", hold=0.7 if not last else 1,
                note="cut in half so you can see in" if last else None,
                caption="6063 for the trial runs; the same part in 4N or 5N aluminium for the real ones.",
                callouts=[("1/2 in hole, 1.9 in deep", (RB - 1, 0, CUP_L - 12), (0.70, 0.30), "left"),
                          (f"{wall:.1f} mm wall", (R, 0, CUP_L * 0.42), (0.70, 0.54), "left"),
                          ("solid bottom", (RB / 2, 0, 3.0), (0.70, 0.78), "left")] if last else [],
                dims=[dict(p1=(-R, 0, CUP_L + 4), p2=(R, 0, CUP_L + 4), text="3/4 in", off=(0, -15))] if last else [])
    sc.save("machining_cup.gif")


# ---------------------------------------------------------------------------
# 2. The lid (plug)
# ---------------------------------------------------------------------------
def plug_gif():
    sc = Scene()
    spin = 0.0
    blade = cached("blade", parting_blade)
    vent_bit = cached("vent", lambda: drill(cad.VENT_D, 30, flute=13))
    S = STICK_PLUG
    step_len = 16.0
    z_step = S - step_len
    z_cut = S - cad.PLUG_L  # the lid's top face
    gz = z_cut - GROOVE_W / 2
    frame = dict(stick=S, focal=CAM_FOCAL_PLUG, scale=CAM_SCALE_PLUG)
    cap1 = "Measure that cup's hole first, then turn this end one thou bigger, so it presses in."

    for i in range(4):  # in to depth, clear of the end
        t = ease(i, 4)
        lathe_frame(sc, bar_profile(S), spin, **frame, stripe_to=S, hold=0.8,
                    tools=cutter(S + 2.5, -(R + 8 - 8 * t - 1.6), 0),
                    title="Turn the lid to size", step="1 of 5", caption=cap1)
        spin += RPM

    for i in range(11):  # feed toward the chuck; the step follows the tool
        t = ease(i, 11)
        zt = S - step_len * t
        lathe_frame(sc, bar_profile(S, step_z=zt, step_r=RB), spin, **frame, stripe_to=zt,
                    tools=cutter(zt, -RB, 0), hold=1 if i < 10 else 3,
                    title="Turn the lid to size", step="1 of 5", caption=cap1)
        spin += RPM

    for i in range(6):  # lead-in on the nose
        t = ease(i, 6)
        lead = cad.PLUG_LEADIN_L * t
        lathe_frame(sc, bar_profile(S, step_z=z_step, step_r=RB, lead=lead), spin, **frame,
                    stripe_to=z_step, hold=1 if i < 5 else 3,
                    tools=cutter(S - lead / 2, -(RB - lead * math.tan(math.radians(15)) / 2), 0),
                    title="Taper the nose", step="2 of 5",
                    caption="1.5 mm at 15 deg. This is the end that goes in - it starts the lid square.")
        spin += RPM

    for i in range(9):  # vent
        t = ease(i, 9)
        d = 14.0 * t
        lathe_frame(sc, bar_profile(S, step_z=z_step, step_r=RB, lead=cad.PLUG_LEADIN_L, bore_d=cad.VENT_D,
                                    bore=d), spin, cut=True, **frame, stripe_to=z_step,
                    tools=[(vent_bit, STEEL, (S - d, 0, 0))], hold=1 if i < 8 else 3.5,
                    title="Drill the air hole", step="3 of 5", note="cut in half so you can see in",
                    caption="1 mm hole, all the way through. The last clip shows why it is there.")
        spin += RPM

    base = dict(step_z=z_step, step_r=RB, lead=cad.PLUG_LEADIN_L, bore_d=cad.VENT_D, bore=14.0)
    # 0.3 mm is nothing at the wide view, so this step is a close-up.  No tool in shot: the
    # tip is wider than the whole feature at this zoom and would sit right on top of it.
    close = dict(stick=S, focal=(z_cut + 1.0, 0, 0), scale=10, stripe_to=2.5)
    for i in range(7):
        t = ease(i, 7)
        c = cad.PLUG_TOP_CHAMFER * max(0.0, 1.35 * t - 0.35)
        lathe_frame(sc, bar_profile(S, **base, chamf_z=z_cut, chamf=c), spin, **close,
                    hold=1 if i < 6 else 4,
                    title="Break the top edge", step="4 of 5", note="close up - this corner is 0.3 mm",
                    callouts=[("sharp, as turned" if c < 0.05 else "0.3 mm break",
                               (z_cut, 0, RB), (0.60, 0.26), "left")],
                    caption="The tool corner takes it off at the part line, before parting. Deburr only "
                            "- it plays no part in the fit.")
        spin += RPM

    for i in range(10):  # part off
        t = ease(i, 10)
        r = max((RB - cad.PLUG_TOP_CHAMFER) * (1 - t), 0.2)
        lathe_frame(sc, bar_profile(S, **base, chamf_z=z_cut, chamf=cad.PLUG_TOP_CHAMFER, groove_z=gz, groove_r=r),
                    spin, **frame, stripe_to=z_step, hold=1 if i < 9 else 2.5,
                    tools=[(blade, TOOL, (gz, -r, 0))],
                    title="Cut the lid off", step="5 of 5",
                    caption="3/8 in long. Keep each lid bagged with the cup it was measured from.")
        spin += RPM

    for i in range(6):  # the lid comes free, nose still pointing at the tailstock
        t = ease(i, 6)
        pl = sc.pl
        pl.clear()
        show(pl, cached("chuck", chuck_body), CHUCK_C, lw=0.7, spin=spin)
        show(pl, cached("jaws", chuck_jaws), JAW_C, lw=0.7, spin=spin)
        show(pl, tessellate(lay(turned(bar_profile(S, step_z=z_step, step_r=RB, bore_d=cad.VENT_D, bore=14.0,
                                                   face=cad.PLUG_L + GROOVE_W)))), rr.MAT["al"], lw=1.1)
        show(pl, cached("plug_lathe", lambda: lay_rev(cad.build()["std_plug"])), rr.MAT["al"], lw=1.1,
             move=(S + 8 * t, 0, -11 * t * t))
        marks = stripes(2.0, z_step, spin)
        if marks is not None:
            pl.add_mesh(marks, color=STRIPE, line_width=2.0 * SS)
        sc.camera(CAM_FOCAL_PLUG, CAM_DIR, CAM_SCALE_PLUG)
        sc.grab(title="Cut the lid off", step="5 of 5", hold=0.9,
                caption="3/8 in long. Keep each lid bagged with the cup it was measured from.")
        spin += RPM

    plug = cad.build()["std_plug"]
    n = 16
    for i in range(n):
        sc.pl.clear()
        last = i == n - 1
        show(sc.pl, cached(f"plug{i}", lambda i=i: Rot(0, 0, 360 / n * i) * plug, cut=last), rr.MAT["al"], lw=1.2)
        sc.camera((0.0, 0.0, cad.PLUG_L / 2 - 1.4), (0.55, -1.0, 0.78), 11.5)
        sc.grab(title="The lid", step="5 of 5", hold=0.7 if not last else 1,
                note="cut in half so you can see in" if last else None,
                caption="One per cup, turned to that cup's measured hole. Shown about 4x the size of the cup clip.",
                callouts=[("1 mm air hole,\nstraight through", (RV, 0, cad.PLUG_L - 1.5), (0.68, 0.26), "left"),
                          ("0.3 mm break - deburr only,\nnot part of the fit",
                           (cad.CUP_BORE_D / 2 - 0.15, 0, cad.PLUG_L - 0.15), (0.68, 0.50), "left"),
                          ("1.5 mm taper - this end goes in", (RB - 0.3, 0, 0.8), (0.68, 0.80), "left")]
                if last else [],
                dims=[dict(p1=(-RB, 0, cad.PLUG_L + 2.2), p2=(RB, 0, cad.PLUG_L + 2.2),
                           text="cup's hole + .001 in", off=(0, -14))] if last else [])
    sc.save("machining_plug.gif")


# ---------------------------------------------------------------------------
# 3. Fill it, close it, pump the chamber down
# ---------------------------------------------------------------------------
def fill_gif():
    sc = Scene()
    parts = cad.build()
    cup, plug = parts["std_cup"], parts["std_plug"]
    floor = CUP_L - cad.CUP_BORE_DEPTH
    z_top = CUP_L - cad.PLUG_L
    focal, view, scale = (13, 5.5, CUP_L / 2 + 7), (0.42, -1.0, 0.30), 47
    cup_mesh = tessellate(cup, cut=True)
    plug_mesh = tessellate(plug, cut=True)

    def powder(pl, frac, heap=True):
        """The powder column, with a few loose grains on top so it reads as powder."""
        if frac < 0.01:
            return
        top = floor + (z_top - floor) * frac
        col = cad.turned(cad.powder_profile(cad.CUP_BORE_D, floor, top, point=True))
        show(pl, tessellate(col, cut=True, tol=0.05), rr.POWDER["AlSi10Mg"], lw=0.5, powder=True)
        if not heap:
            return
        for gx, gy, gr in surface_grains:
            if gy < 0.5:
                continue
            pl.add_mesh(pv.Sphere(radius=gr, center=(gx, gy, top + gr * 0.4)),
                        color=rr.POWDER["AlSi10Mg"], **rr.BODY)

    rng = np.random.default_rng(7)
    grains = rng.uniform(-1, 1, (30, 2)) * RB * 0.6
    ga = rng.uniform(0, 2 * math.pi, 14)
    gr = RB * np.sqrt(rng.uniform(0, 0.8, 14))
    surface_grains = list(zip(gr * np.cos(ga), gr * np.sin(ga), rng.uniform(0.35, 0.7, 14)))

    n = 15  # pour
    for i in range(n):
        pl = sc.pl
        pl.clear()
        show(pl, cup_mesh, rr.MAT["al"], lw=1.2)
        frac = i / (n - 1)
        powder(pl, frac)
        if i < n - 1:
            for k, (gx, gy) in enumerate(grains):
                z = z_top + 30 - ((i * 8 + k * 3.7) % 34)
                if gy < 0.6 or z < floor + (z_top - floor) * frac:
                    continue
                pl.add_mesh(pv.Sphere(radius=0.7, center=(gx, gy, z)), color=rr.POWDER["AlSi10Mg"], **rr.BODY)
        sc.camera(focal, view, scale)
        sc.grab(title="Fill it", step="1 of 3", note="cut in half so you can see in",
                caption="Tap the powder down to the line where the lid sits, and weigh what goes in.",
                callouts=[("AlSi10Mg powder, 8 g", (RB / 2, 0, floor + (z_top - floor) * 0.5), (0.66, 0.46),
                           "left")] if i == n - 1 else [])

    n = 12  # close
    for i in range(n):
        t = ease(i, n)
        pl = sc.pl
        pl.clear()
        show(pl, cup_mesh, rr.MAT["al"], lw=1.2)
        powder(pl, 1.0)
        show(pl, plug_mesh, rr.MAT["al"], lw=1.2, move=(0, 0, z_top + 32 * (1 - t)))
        sc.camera(focal, view, scale)
        sc.grab(title="Close it", step="2 of 3", note="cut in half so you can see in",
                caption="The lid is a press fit, about a thou tight: light taps, or the press for the squeeze run.")

    n = 16  # pump down
    for i in range(n):
        pl = sc.pl
        pl.clear()
        show(pl, cup_mesh, rr.MAT["al"], lw=1.2)
        powder(pl, 1.0)
        show(pl, plug_mesh, rr.MAT["al"], lw=1.2, move=(0, 0, z_top))
        for k in range(3):
            z = CUP_L + 1 + ((i * 2.2 + k * 4.7) % 14)
            fade = max(0.0, 1 - (z - CUP_L - 1) / 14)
            pl.add_mesh(pv.Arrow(start=(0, 0, z), direction=(0, 0, 1), tip_length=0.42, tip_radius=0.32,
                                 shaft_radius=0.13, scale=7.0),
                        color=AIR, opacity=0.25 + 0.65 * fade, **rr.BODY)
        sc.camera(focal, view, scale)
        last = i == n - 1
        sc.grab(title="Pump the chamber down", step="3 of 3", note="cut in half so you can see in",
                caption="Air under the lid leaves through the 1 mm hole. With no hole it has to come out "
                        "through the powder.",
                callouts=[("air out", (0, 0, CUP_L + 11), (0.60, 0.19), "left"),
                          ("1 mm hole in the lid", (RV, 0, CUP_L - 4), (0.62, 0.38), "left"),
                          ("powder stays where you put it", (RB / 2, 0, z_top - 14), (0.62, 0.62),
                           "left")] if last else [])
    sc.save("fill_and_vent.gif", ms=210, tail_ms=3000)


def main():
    OUT.mkdir(exist_ok=True)
    cup_gif()
    plug_gif()
    fill_gif()


if __name__ == "__main__":
    main()
