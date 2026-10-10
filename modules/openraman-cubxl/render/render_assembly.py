"""Animate the build: the seven official assembly sheets, then the CubXL steps.

    xvfb-run -a python render_assembly.py /path/to/openraman/cad /path/to/PandaDeck.step
        [--fps 20] [--size 1280x720] [--preview]

Writes openraman_cubxl_assembly.mp4 and a smaller .gif next to this file
(--preview writes a handful of PNG stills instead).
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cad"))
import build_cad  # noqa: E402
import cubxl_parts as cx  # noqa: E402
import openraman_assembly as oa  # noqa: E402

pv.OFF_SCREEN = True

SEGMENTS = [  # name, seconds, title, subtitle
    ("intro", 2.0, "OpenRAMAN on the CubXL", "official design: Luc Boussemaere, CC BY-SA 4.0 · vendor parts recreated from datasheets"),
    ("s0", 3.0, "1  Laser holder, CPS532 laser, clamp setscrew   (drawing P00000, sheet 2)", "P00003 · CPS532 · SS4MN4 · DIN912 M4×12 ×2 from below"),
    ("s1", 3.0, "2  Camera bracket, lens, camera   (sheet 3)", "P00005 on two DIN7 3×8 pins · MVL50M23 · Blackfly S BFS-PGE-31S4M-C · DIN912 M4×12 ×2"),
    ("s2", 2.5, "3  Fixed mounts: longpass filter and steering plate   (sheet 4)", "FMP1/M ×2 · FELH0550 · WG41050-A · DIN912 M4×12 ×2"),
    ("s3", 3.0, "4  Kinematic mounts: fold mirror, dichroic, grating   (sheet 5)", "KM100 ×3 · PF10-03-G01 · DMLP550 · GR25-1205 epoxied to P00004 · DIN912 M4×10 ×3"),
    ("s4", 3.5, "5  Cage: focusing lens, 50 µm slit, collimator   (sheet 6)", "CP14 + AC127-019-A · CRM1T/M + S50K + SM1RR · CP35/M + AC254-050-A · ER3 ×4"),
    ("s5", 2.5, "6  Cage bracket and sample-port bracket   (sheet 7)", "CP33B ×2 (Thorlabs' replacement for CP02B) · DIN912 M4×12 · M4×6 ×2"),
    ("s6", 2.5, "7  Cover   (sheet 1)", "P00002 · DIN912 M4×10 ×3"),
    ("beam", 2.5, "Beam check: 532 nm laser (green), Raman light to the grating and camera (orange)", "CPS532, 4.5 mW, Class 3R"),
    ("adapter", 3.0, "8  NEW: PandaDeck adapter", "printed ASA · four ruthex M4 inserts · M4×12 through the baseplate's corner counterbores"),
    ("dock", 3.0, "9  NEW: pipette-tip dock on the sample-port bracket", "two ER1 rods · AC127-019-A glued in, as in the official liquid cuvette · black ASA beam trap"),
    ("deck", 3.5, "10  Keys drop into the PandaDeck slots", "θ = 90°: beam points to the back, the body sits in the band the gantry cannot reach"),
    ("head", 4.0, "11  The pipette parks its tip at the laser focus", "the capper, 54 mm to the left and 17 mm below the nozzle, clears every tall part"),
    ("orbit", 4.5, "OpenRAMAN on the CubXL", "parts ≈ $2,915 (BOM sections A–E) · modules/openraman-cubxl"),
]
SEG_T = {}
_t = 0.0
for name, dur, *_ in SEGMENTS:
    SEG_T[name] = (_t, _t + dur)
    _t += dur
TOTAL = _t
LIFT = 170.0                       # module height above its final pose until the "deck" step


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return p * p * (3 - 2 * p)


def seg_p(name, t, a=0.0, b=1.0):
    t0, t1 = SEG_T[name]
    return ease((t - (t0 + a * (t1 - t0))) / max(1e-6, (b - a) * (t1 - t0)))


def mat(R=np.eye(3), t=(0, 0, 0)):
    M = np.eye(4); M[:3, :3] = R; M[:3, 3] = t
    return M


def tr(v):
    return mat(np.eye(3), v)


def to_pv(shape, tol=0.15):
    v, t = shape.tessellate(tol, 0.25)
    V = np.array([(p.x, p.y, p.z) for p in v], float)
    T = np.asarray(t, int)
    return pv.PolyData(V, np.hstack([np.full((len(T), 1), 3), T]).ravel())


class Scene:
    def __init__(self, openraman_cad, deck_step, size):
        self.inst = build_cad.installation(openraman_cad, deck_step)
        R, t = self.inst["R"], self.inst["t"]
        self.M_final = mat(R, t)
        self.theta = self.inst["pose"]["theta"]
        self.pl = pv.Plotter(window_size=size, lighting="three lights")
        self.pl.set_background("#f7f8fa", top="#dfe6ee")
        self.pl.enable_anti_aliasing("ssaa")
        self.actors = []                      # dict(actor, kind, ...)
        self._add_spectrometer()
        self._add_cubxl()
        self.title = self.pl.add_text("", position="upper_left", font_size=13, color="#1d2733")
        self.sub = self.pl.add_text("", position="lower_left", font_size=10, color="#3b4a5a")

    # ---- scene content
    def add(self, shape_or_mesh, color, opacity=1.0, tol=0.15, **kw):
        m = shape_or_mesh if isinstance(shape_or_mesh, pv.DataSet) else to_pv(shape_or_mesh, tol)
        a = self.pl.add_mesh(m, color=color, opacity=opacity, smooth_shading=False, specular=0.35,
                             specular_power=20, ambient=0.18)
        d = dict(actor=a, base_opacity=opacity, **kw)
        self.actors.append(d)
        return d

    def _add_spectrometer(self):
        by_step = {}
        for p in self.inst["parts"]:
            by_step.setdefault(p.step, []).append(p)
        for step, ps in by_step.items():
            for j, p in enumerate(ps):
                app = np.asarray(p.approach, float)
                dist = 45.0 if app[2] < 0 else 85.0
                seg = "intro" if p.name.startswith("P00001") else f"s{step}"
                self.add(p.shape, p.color, p.opacity, group="module", seg=seg, j=j, n=len(ps),
                         approach=app * dist, name=p.name)
        # beams, in frame S
        laser = np.array(self.inst["beams"]["laser"] + [oa.SAMPLE_FOCUS + [20.0, 0, 0]], float)
        raman = np.array(self.inst["beams"]["raman"], float)
        self.laser = self.add(pv.lines_from_points(laser).tube(radius=0.55, n_sides=12), "#16e04a", 1.0,
                              group="module", kind="laser")
        self.raman = self.add(pv.lines_from_points(raman).tube(radius=2.6, n_sides=16), "#ff7a1a", 0.45,
                              group="module", kind="raman")

    def _add_cubxl(self):
        I = self.inst
        self.add(I["adapter"], "#59656e", 1.0, group="module", seg="adapter", j=0, n=1, approach=np.array([0, 0, -70.0]))
        for k, (x, y) in enumerate(cx.CORNER_HOLES):
            ins = oa.cyl(5.6, 8.0, -18.0).moved(oa.cq.Location(oa.cq.Vector(x, y, 0)))
            self.add(ins, "#c9a64b", 1.0, group="module", seg="adapter", j=1 + k, n=9, approach=np.array([0, 0, -40.0]))
        for k, (x, y) in enumerate(cx.CORNER_HOLES):
            sc = oa.shcs_m4(12).moved(oa.cq.Location(oa.cq.Vector(x, y, -4.4)))
            self.add(sc, oa.C_STEEL, 1.0, group="module", seg="adapter", j=5 + k, n=9, approach=np.array([0, 0, 60.0]))
        for k, sy in enumerate((-15.0, 15.0)):
            rod = oa.cq.Solid.makeCylinder(3.0, 25.4, oa.cq.Vector(286.3, oa.AXIS_Y + sy, oa.BEAM_H - 15.0), oa.cq.Vector(1, 0, 0))
            self.add(rod, oa.C_STEEL, 1.0, group="module", seg="dock", j=k, n=4, approach=np.array([-30.0, 0, 0]))
        self.add(I["dock"], "#2d2f36", 0.88, group="module", seg="dock", j=2, n=4, approach=np.array([70.0, 0, 0]))
        for s in I["dock_lens"]:
            self.add(s, oa.C_GLASS, 0.7, group="module", seg="dock", j=3, n=4, approach=np.array([70.0, 0, 0]))
        # deck, gantry context and head: world frame (PandaDeck)
        self.add(I["deck"], "#b9d3e3", 0.45, tol=0.4, group="world", seg="deck", fade=True)
        for x0 in (-48.0, cx.DECK_W + 8.0):
            self.add(oa.box(40.0, 600.0, 60.0, x0 + 20.0, -cx.DECK_D / 2, -55.0), "#c4c9cf", 0.9, group="world", seg="deck", fade=True)
        tip = self.inst["pose"]["tip_deck"]
        tip_end_z = oa.BEAM_H - cx.TIP_BELOW_BEAM + cx.Z_S_TO_D
        hp, self.capper_xy, _ = cx.head_parts(tip, tip_end_z)
        cols = {"tip": "#f1eee4", "pipette shaft": "#2b2b2b", "pipette body (P20 GEN2)": "#1f1f22",
                "capper": "#202024", "backboard": "#141416"}
        for name, s in hp.items():
            self.add(s, cols[name], 0.85 if name == "tip" else 1.0, group="head", seg="head", name=name)
        self.add(oa.box(cx.DECK_W + 100, 40.0, 70.0, cx.DECK_W / 2, tip[1] + 75.0, 270.0), "#c4c9cf", 0.3,
                 group="head", seg="head", name="gantry bridge")

    # ---- per-frame state
    def module_matrix(self, t):
        lift = LIFT * (1.0 - seg_p("deck", t, 0.15, 0.85))
        return tr((0, 0, lift)) @ self.M_final

    def head_offset(self, t):
        p_xy, p_z = seg_p("head", t, 0.0, 0.45), seg_p("head", t, 0.45, 0.8)
        start = np.array([-120.0, 110.0, 150.0])
        return np.array([start[0] * (1 - p_xy), start[1] * (1 - p_xy), start[2] * (1 - p_z)])

    def update(self, t):
        Mm = self.module_matrix(t)
        for d in self.actors:
            a, seg = d["actor"], d.get("seg")
            kind = d.get("kind")
            if kind in ("laser", "raman"):
                on = (SEG_T["beam"][0] + 0.3 <= t < SEG_T["adapter"][0] + 0.4) or t >= SEG_T["head"][0] + 0.82 * (
                    SEG_T["head"][1] - SEG_T["head"][0])
                a.SetVisibility(bool(on))
                a.user_matrix = Mm
                continue
            t0, t1 = SEG_T[seg]
            if t < t0:
                a.SetVisibility(False)
                continue
            a.SetVisibility(True)
            if d["group"] == "module":
                n, j = d.get("n", 1), d.get("j", 0)
                span = t1 - t0
                a0 = t0 + span * 0.55 * j / max(1, n)
                p = ease((t - a0) / (span * 0.45))
                off = d.get("approach", np.zeros(3)) * (1 - p)
                R = Mm[:3, :3]
                a.user_matrix = tr(R @ off) @ Mm
                if d.get("name") == "P00002 cover":
                    see = (SEG_T["beam"][0] <= t < SEG_T["adapter"][0]) or t >= SEG_T["head"][0]
                    a.GetProperty().SetOpacity(0.28 if see else d["base_opacity"])
            elif d["group"] == "head":
                a.user_matrix = tr(self.head_offset(t))
            else:
                a.GetProperty().SetOpacity(d["base_opacity"] * (seg_p(seg, t, 0.0, 0.3) if d.get("fade") else 1.0))
        for name, _, title, sub in SEGMENTS:
            if SEG_T[name][0] <= t < SEG_T[name][1] or (name == "orbit" and t >= SEG_T[name][0]):
                self.title.SetText(2, title)
                self.sub.SetText(0, sub)
        self.set_camera(t, Mm)

    # ---- camera: views in frame S (bench) or the deck frame, blended at segment starts
    def view(self, name, Mm):
        S = {  # focal point (frame S), azimuth from S +x (deg), elevation (deg), distance (mm)
            "intro": ((150, 75, 0), -125, 38, 620), "s0": ((195, 50, 15), -110, 35, 360),
            "s1": ((115, 45, 15), -150, 42, 500), "s2": ((205, 95, 20), -100, 38, 340),
            "s3": ((160, 75, 20), -120, 45, 520), "s4": ((140, 95, 22), -75, 30, 360),
            "s5": ((230, 95, 10), -70, 42, 460), "s6": ((90, 75, 25), -135, 35, 520),
            "beam": ((170, 75, 15), -115, 62, 560), "adapter": ((160, 75, -12), -120, 18, 640),
            "dock": ((300, 95, 12), -40, 34, 420)}
        if name in S:
            f, az, el, dist = S[name]
            f = (Mm @ np.array([*f, 1.0]))[:3]
            az = az + self.theta
        else:
            tip = np.array(self.inst["pose"]["tip_deck"] + [40.0])
            D = {"deck": (np.array([240.0, -260.0, 0.0]), -105, 42, 1150), "head": (tip + [-10, -70, 20], -125, 30, 640),
                 "orbit": (np.array([200.0, -280.0, 30.0]), -150, 40, 1000)}
            f, az, el, dist = D[name]
        return np.asarray(f, float), az, el, dist

    def set_camera(self, t, Mm):
        names = [s[0] for s in SEGMENTS]
        i = max(k for k, n in enumerate(names) if SEG_T[n][0] <= min(t, TOTAL - 1e-6))
        cur = self.view(names[i], Mm)
        prev = self.view(names[i - 1], Mm) if i > 0 else cur
        b = seg_p(names[i], t, 0.0, 0.35)
        f = prev[0] * (1 - b) + cur[0] * b
        az = prev[1] * (1 - b) + cur[1] * b
        el = prev[2] * (1 - b) + cur[2] * b
        dist = prev[3] * (1 - b) + cur[3] * b
        if names[i] == "orbit":
            az += 110.0 * seg_p("orbit", t, 0.0, 1.0)
        else:
            az += 6.0 * math.sin(2 * math.pi * t / 9.0)        # slow drift so stills breathe
        a, e = math.radians(az), math.radians(el)
        pos = f + dist * np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
        self.pl.camera_position = [tuple(pos), tuple(f), (0, 0, 1)]
        self.pl.camera.view_angle = 30.0
        self.pl.camera.clipping_range = (5.0, 6000.0)

    def frame(self, t):
        self.update(t)
        self.pl.render()
        return self.pl.screenshot(return_img=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("openraman_cad")
    ap.add_argument("deck_step")
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    size = tuple(int(v) for v in a.size.split("x"))
    sc = Scene(a.openraman_cad, a.deck_step, size)
    if a.preview:
        import imageio.v3 as iio
        for name, *_ in SEGMENTS:
            t0, t1 = SEG_T[name]
            iio.imwrite(HERE / f"preview_{name}.png", sc.frame(t0 + 0.9 * (t1 - t0)))
        return
    import imageio.v2 as imageio
    mp4 = HERE / "openraman_cubxl_assembly.mp4"
    w = imageio.get_writer(mp4, fps=a.fps, codec="libx264", quality=8, macro_block_size=8,
                           ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    n = int(round(TOTAL * a.fps))
    for k in range(n + int(a.fps)):                       # one extra second on the last frame
        w.append_data(sc.frame(min(k, n) / a.fps))
    w.close()
    gif = HERE / "openraman_cubxl_assembly.gif"
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    flt = "fps=8,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle"
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(mp4), "-vf", flt, str(gif)], check=True)
    print(json.dumps({"mp4": str(mp4), "mp4_MB": round(mp4.stat().st_size / 1e6, 2),
                      "gif": str(gif), "gif_MB": round(gif.stat().st_size / 1e6, 2), "seconds": TOTAL}))


if __name__ == "__main__":
    main()
