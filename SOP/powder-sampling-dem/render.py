"""Render the DEM runs as 3D animations (GIF for the PR comment, MP4 to download).

    python render.py fill open_tube piston thief spoon pour   # one GIF + MP4 each
    python render.py --combined                               # all of them in one MP4

A small software renderer: shaded spheres and triangle meshes into a z-buffer, drawn at
twice the output size and scaled down. Jar views are cut away along y = 0 so the inside
of the jar, tube or thief shows.
"""

import json
import math
import os
import sys

import imageio.v2 as imageio
import numpy as np
from matplotlib import font_manager
from numba import njit
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("DEM_OUT", "/tmp/dem-out")
MEDIA = os.path.join(HERE, "media")
RES = os.path.join(HERE, "results")
mm = 1e-3

def _hex(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


# validated with the dataviz skill's palette checker (light mode, adjacent pairs)
GROUP_HEX = ["#2a78d6", "#eda100", "#e34948", "#6250d6"]
GROUP_RGB = np.array([_hex(h) for h in GROUP_HEX], np.float32)  # bottom, middle, top third, sweepings
GROUP_TXT = ["made first (bottom third)", "middle third", "made last (top third)", "sweepings"]
TITLES = {
    "fill": "Filling the jar: colour = when the powder was made",
    "open_tube": "Open glass tube, pushed to the floor",
    "piston": "Piston corer: piston held at the surface",
    "thief": "Three-port sampling thief",
    "spoon": "Spoonula, one scoop per layer",
    "peel": "Scrape off whole layers (idealised)",
    "pour": "Pour along a line, sample along it",
}

W, H = 1280, 800
SS = 2  # supersampling

FONT = font_manager.findfont("DejaVu Sans")
FONT_B = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))


def _norm(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


LIGHT = _norm([-0.45, 0.65, -0.62]).astype(np.float32)
HALF = _norm(LIGHT + np.array([0, 0, -1.0])).astype(np.float32)


@njit(cache=True)
def splat(img, zb, P, rad, col, fpx, cx0, cy0, L, Hh):
    h, w = zb.shape
    for i in range(P.shape[0]):
        z = P[i, 2]
        if z < 1e-4:
            continue
        sx = cx0 + fpx * P[i, 0] / z
        sy = cy0 - fpx * P[i, 1] / z
        sr = fpx * rad[i] / z
        if sr < 0.5:
            sr = 0.5
        x0 = int(sx - sr)
        x1 = int(sx + sr) + 1
        y0 = int(sy - sr)
        y1 = int(sy + sr) + 1
        if x1 < 0 or y1 < 0 or x0 >= w or y0 >= h:
            continue
        x0 = max(x0, 0)
        y0 = max(y0, 0)
        x1 = min(x1, w - 1)
        y1 = min(y1, h - 1)
        inv = 1.0 / sr
        for py in range(y0, y1 + 1):
            dy = (py + 0.5 - sy) * inv
            for px in range(x0, x1 + 1):
                dx = (px + 0.5 - sx) * inv
                d2 = dx * dx + dy * dy
                if d2 >= 1.0:
                    continue
                nz = math.sqrt(1.0 - d2)
                depth = z - rad[i] * nz
                if depth >= zb[py, px]:
                    continue
                zb[py, px] = depth
                ndl = dx * L[0] - dy * L[1] - nz * L[2]
                if ndl < 0.0:
                    ndl = 0.0
                ndh = dx * Hh[0] - dy * Hh[1] - nz * Hh[2]
                sp = 0.0
                if ndh > 0.0:
                    sp = 0.22 * ndh ** 28
                shade = (0.30 + 0.70 * ndl) * (1.0 - 0.22 * d2 * d2)
                for c in range(3):
                    v = col[i, c] * shade + sp
                    img[py, px, c] = v if v < 1.0 else 1.0


@njit(cache=True)
def raster(img, zb, V, col, alpha, fpx, cx0, cy0, L, Hh, blend):
    h, w = zb.shape
    for t in range(V.shape[0]):
        z0 = V[t, 0, 2]
        z1 = V[t, 1, 2]
        z2 = V[t, 2, 2]
        if z0 < 1e-4 or z1 < 1e-4 or z2 < 1e-4:
            continue
        xa = cx0 + fpx * V[t, 0, 0] / z0
        ya = cy0 - fpx * V[t, 0, 1] / z0
        xb = cx0 + fpx * V[t, 1, 0] / z1
        yb = cy0 - fpx * V[t, 1, 1] / z1
        xc = cx0 + fpx * V[t, 2, 0] / z2
        yc = cy0 - fpx * V[t, 2, 1] / z2
        area = (xb - xa) * (yc - ya) - (xc - xa) * (yb - ya)
        if abs(area) < 1e-9:
            continue
        ux = V[t, 1, 0] - V[t, 0, 0]
        uy = V[t, 1, 1] - V[t, 0, 1]
        uz = V[t, 1, 2] - V[t, 0, 2]
        vx = V[t, 2, 0] - V[t, 0, 0]
        vy = V[t, 2, 1] - V[t, 0, 1]
        vz = V[t, 2, 2] - V[t, 0, 2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        nl = math.sqrt(nx * nx + ny * ny + nz * nz)
        if nl < 1e-20:
            continue
        nx /= nl
        ny /= nl
        nz /= nl
        if nx * V[t, 0, 0] + ny * V[t, 0, 1] + nz * V[t, 0, 2] > 0:
            nx = -nx
            ny = -ny
            nz = -nz
        ndl = nx * L[0] + ny * L[1] + nz * L[2]
        if ndl < 0:
            ndl = 0.0
        ndh = nx * Hh[0] + ny * Hh[1] + nz * Hh[2]
        sp = 0.0
        if ndh > 0:
            sp = (0.45 if blend else 0.18) * ndh ** 24
        shade = 0.42 + 0.58 * ndl
        xmin = max(int(min(xa, xb, xc)), 0)
        xmax = min(int(max(xa, xb, xc)) + 1, w - 1)
        ymin = max(int(min(ya, yb, yc)), 0)
        ymax = min(int(max(ya, yb, yc)) + 1, h - 1)
        b0 = (yb - yc) / area
        b1 = (yc - ya) / area
        b2 = -b0 - b1
        for py in range(ymin, ymax + 1):
            fy = py + 0.5
            # each barycentric weight is linear in x along the row: find where all are >= 0
            a0 = (xb * (yc - fy) - xc * (yb - fy)) / area
            a1 = (xc * (ya - fy) - xa * (yc - fy)) / area
            a2 = 1.0 - a0 - a1
            lo = -1e30
            hi = 1e30
            empty = False
            for aa, bb in ((a0, b0), (a1, b1), (a2, b2)):
                if bb > 1e-15:
                    v = -aa / bb
                    if v > lo:
                        lo = v
                elif bb < -1e-15:
                    v = -aa / bb
                    if v < hi:
                        hi = v
                elif aa < 0:
                    empty = True
            if empty or hi < lo:
                continue
            p0 = max(xmin, int(math.ceil(lo - 0.5)))
            p1 = min(xmax, int(math.floor(hi - 0.5)))
            for px in range(p0, p1 + 1):
                fx = px + 0.5
                w0 = a0 + b0 * fx
                w1 = a1 + b1 * fx
                w2 = 1.0 - w0 - w1
                if w0 < -1e-6 or w1 < -1e-6 or w2 < -1e-6:
                    continue
                depth = 1.0 / (w0 / z0 + w1 / z1 + w2 / z2)
                if depth >= zb[py, px]:
                    continue
                if blend:
                    a = alpha[t]
                    for c in range(3):
                        v = a * (col[t, c] * shade + sp) + (1 - a) * img[py, px, c]
                        img[py, px, c] = v if v < 1.0 else 1.0
                else:
                    zb[py, px] = depth
                    for c in range(3):
                        v = col[t, c] * shade + sp
                        img[py, px, c] = v if v < 1.0 else 1.0


# ---------------------------------------------------------------------------
# Meshes


def revolve_mesh(poly, cut, nth=None):
    poly = [tuple(p) for p in poly if not (p[0] == 0 and p[1] == 0 and False)]
    poly = [p for p in poly]
    span = math.pi if cut else 2 * math.pi
    nth = nth or (36 if cut else 72)
    th = np.linspace(0, span, nth + 1)
    c, s = np.cos(th), np.sin(th)
    tris = []
    n = len(poly)
    for k in range(n):
        (ar, az), (br, bz) = poly[k], poly[(k + 1) % n]
        if ar == 0 and br == 0:
            continue
        for j in range(nth):
            pa0 = (ar * c[j], ar * s[j], az)
            pb0 = (br * c[j], br * s[j], bz)
            pa1 = (ar * c[j + 1], ar * s[j + 1], az)
            pb1 = (br * c[j + 1], br * s[j + 1], bz)
            tris.append((pa0, pb0, pb1))
            tris.append((pa0, pb1, pa1))
    if cut:
        for sign in (1.0, -1.0):
            pts = [(sign * r, 0.0, z) for r, z in poly]
            for k in range(1, n - 1):
                tris.append((pts[0], pts[k], pts[k + 1]))
    return np.array(tris, float)


def box_mesh(half, ndiv=6):
    hx, hy, hz = half
    tris = []
    g = np.linspace(-1, 1, ndiv + 1)
    for axis in range(3):
        for sign in (-1, 1):
            u, v = [a for a in range(3) if a != axis]
            for i in range(ndiv):
                for j in range(ndiv):
                    quad = []
                    for (a, b) in ((g[i], g[j]), (g[i + 1], g[j]), (g[i + 1], g[j + 1]), (g[i], g[j + 1])):
                        p = [0.0, 0.0, 0.0]
                        p[axis] = sign
                        p[u] = a
                        p[v] = b
                        quad.append((p[0] * hx, p[1] * hy, p[2] * hz))
                    tris.append((quad[0], quad[1], quad[2]))
                    tris.append((quad[0], quad[2], quad[3]))
    return np.array(tris, float)


class Camera:
    def __init__(self, eye, target, fov_deg, w, h):
        self.eye = np.asarray(eye, float)
        f = _norm(np.asarray(target, float) - self.eye)
        r = _norm(np.cross(f, [0, 0, 1]))
        u = np.cross(r, f)
        self.B = np.stack([r, u, f])  # rows: right, up, forward
        self.fpx = (w / 2) / math.tan(math.radians(fov_deg) / 2)
        self.cx, self.cy = w / 2, h / 2

    def to_cam(self, X):
        return (np.asarray(X, float) - self.eye) @ self.B.T


def orbit(target, dist, az_deg, el_deg):
    az, el = math.radians(az_deg), math.radians(el_deg)
    t = np.asarray(target, float)
    return t + dist * np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)]), t


# ---------------------------------------------------------------------------


class Run:
    def __init__(self, name):
        d = np.load(os.path.join(OUT, f"{name}.npz"), allow_pickle=False)
        self.name = name
        self.X = d["X"]
        self.M = d["M"]
        self.TP, self.TR, self.TO = d["TP"], d["TR"], d["TO"]
        self.t = d["t"]
        self.caption = d["caption"]
        self.rad = d["rad"]
        self.group = d["group"]
        self.tools = json.loads(str(d["tools"]))
        self.extra = json.loads(str(d["extra"]))
        self.F = len(self.t)
        rp = os.path.join(RES, f"{name}.json")
        self.result = json.load(open(rp)) if os.path.exists(rp) else None
        self.cut = name != "pour"
        self.meshes = []
        for tl in self.tools:
            if tl["kind"] == "revolve":
                m = revolve_mesh(tl["poly"], self.cut and tl["cut"])
                self.meshes.append((m, False))
            else:
                self.meshes.append((box_mesh(tl["half"]), self.cut and tl["cut"]))
        self._cam_x = None

    def tool_index(self, name):
        for k, tl in enumerate(self.tools):
            if tl["name"] == name:
                return k
        return None

    def camera(self, f, w, h):
        n = self.name
        if n == "pour":
            eye, tgt = orbit([26 * mm, -16 * mm, 9 * mm], 178 * mm, -16, 26)
            return Camera(eye, tgt, 36, w, h)
        if n in ("open_tube", "piston"):
            k = self.tool_index("tube")
            x = float(self.TP[f, k, 0])
            want = max(0.0, x - 4 * mm)
            self._cam_x = want if self._cam_x is None else self._cam_x + 0.18 * (want - self._cam_x)
            eye, tgt = orbit([self._cam_x, 0, 16 * mm], 118 * mm, 16, 18)
            return Camera(eye, tgt, 33, w, h)
        if n == "spoon":
            eye, tgt = orbit([4 * mm, 0, 15 * mm], 112 * mm, 16, 20)
            return Camera(eye, tgt, 32, w, h)
        if n == "thief":
            eye, tgt = orbit([0, 0, 17 * mm], 112 * mm, 16, 18)
            return Camera(eye, tgt, 32, w, h)
        eye, tgt = orbit([0, 0, 12 * mm], 100 * mm, 16, 22)
        return Camera(eye, tgt, 30, w, h)

    def particles(self, f):
        X = self.X[f]
        alive = self.M[f] != 1
        idx = np.where(alive & np.isfinite(X[:, 0]))[0]
        pos = X[idx].astype(float)
        if self.name == "thief" and self.t[f] >= self.extra["capture_t"] - 1e-9:
            k = self.tool_index("thief core")
            ids = np.array([int(i) for i in self.extra["cap_rel"]], int)
            rel = np.array([self.extra["cap_rel"][str(i)] for i in ids])
            pos = np.vstack([pos, self.TP[f, k] + rel])
            idx = np.concatenate([idx, ids])
        if self.cut:
            keep = pos[:, 1] >= -0.05 * mm
            pos, idx = pos[keep], idx[keep]
        return pos, idx

    def frame(self, f, w=W, h=H, overlay=True, result=False):
        ws, hs = w * SS, h * SS
        cam = self.camera(f, ws, hs)
        if getattr(self, "_bg", None) is None or self._bg.shape[:2] != (hs, ws):
            y = np.linspace(0, 1, hs, dtype=np.float32)[:, None, None]
            self._bg = np.ones((hs, ws, 3), np.float32) * (0.985 - 0.06 * y)
        img = self._bg.copy()
        zb = np.full((hs, ws), np.inf, np.float32)
        opaque, glass = [], []
        for k, tl in enumerate(self.tools):
            if not self.TO[f, k]:
                continue
            mesh, clip = self.meshes[k]
            V = mesh @ self.TR[f, k].T + self.TP[f, k]
            if clip:
                cy = V[:, :, 1].mean(axis=1)
                V = V[cy >= -1e-6]
            Vc = cam.to_cam(V.reshape(-1, 3)).reshape(-1, 3, 3)
            (glass if tl["alpha"] < 1 else opaque).append((Vc, tl["color"], tl["alpha"]))
        for Vc, color, a in opaque:
            col = np.tile(np.asarray(color, np.float32), (len(Vc), 1))
            raster(img, zb, Vc.astype(np.float32), col, np.full(len(Vc), a, np.float32), cam.fpx, cam.cx, cam.cy,
                   LIGHT, HALF, False)
        pos, idx = self.particles(f)
        P = cam.to_cam(pos).astype(np.float32)
        col = GROUP_RGB[self.group[idx]]
        splat(img, zb, P, self.rad[idx].astype(np.float32), col, cam.fpx, cam.cx, cam.cy, LIGHT, HALF)
        for Vc, color, a in glass:
            col = np.tile(np.asarray(color, np.float32), (len(Vc), 1))
            raster(img, zb, Vc.astype(np.float32), col, np.full(len(Vc), a, np.float32), cam.fpx, cam.cx, cam.cy,
                   LIGHT, HALF, True)
        img = 0.25 * (img[0::2, 0::2] + img[1::2, 0::2] + img[0::2, 1::2] + img[1::2, 1::2])
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
        if overlay:
            self.draw_overlay(im, f, result)
        return im

    def draw_overlay(self, im, f, result):
        w, h = im.size
        s = w / 1280
        d = ImageDraw.Draw(im, "RGBA")
        fb = ImageFont.truetype(FONT_B, int(30 * s))
        fr = ImageFont.truetype(FONT, int(25 * s))
        fs = ImageFont.truetype(FONT, int(20 * s))
        d.text((int(24 * s), int(18 * s)), TITLES.get(self.name, self.name), font=fb, fill=(25, 25, 30))
        d.text((int(24 * s), int(58 * s)), str(self.caption[f]), font=fr, fill=(60, 60, 70))
        d.text((w - int(250 * s), int(22 * s)), f"t = {self.t[f]:.2f} s (simulated)", font=fs, fill=(90, 90, 100))
        y0 = h - int(122 * s)
        d.rounded_rectangle([int(12 * s), y0 - int(10 * s), int(330 * s), y0 + int(112 * s)], radius=int(8 * s),
                            fill=(255, 255, 255, 215))
        for k in range(4):
            yy = y0 + int(k * 26 * s)
            c = tuple(int(255 * v) for v in GROUP_RGB[k])
            d.ellipse([int(24 * s), yy, int(42 * s), yy + int(18 * s)], fill=c, outline=(40, 40, 40))
            d.text((int(52 * s), yy - int(2 * s)), GROUP_TXT[k], font=fs, fill=(40, 40, 48))
        note = "DEM, 6,600 coarse-grained 1 mm particles; cut away along the middle" if self.cut else \
            "DEM, 6,600 coarse-grained 1 mm particles"
        tw = d.textlength(note, font=fs)
        d.text((w - tw - int(20 * s), h - int(34 * s)), note, font=fs, fill=(110, 110, 120))
        if result and self.result:
            self.draw_result(d, w, h, s)

    def draw_result(self, d, w, h, s):
        samples = self.result["samples"]
        bw = int(330 * s)
        rh = int(34 * s)
        x0 = w - bw - int(300 * s)
        y0 = int(110 * s)
        fs = ImageFont.truetype(FONT, int(17 * s))
        fb = ImageFont.truetype(FONT_B, int(19 * s))
        d.rounded_rectangle([x0 - int(16 * s), y0 - int(44 * s), w - int(24 * s), y0 + rh * len(samples) + int(18 * s)],
                            radius=int(10 * s), fill=(255, 255, 255, 225), outline=(180, 180, 190))
        d.text((x0, y0 - int(36 * s)), "What each sample got", font=fb, fill=(25, 25, 30))
        for k, smp in enumerate(samples):
            yy = y0 + k * rh
            n = max(1, smp["n"])
            x = x0
            for g in range(4):
                ww = int(round(bw * smp["counts"][g] / n))
                if ww:
                    d.rectangle([x, yy, x + ww, yy + int(22 * s)], fill=tuple(int(255 * v) for v in GROUP_RGB[g]))
                x += ww
            label = smp["name"].split(" (")[0] if self.name in ("pour", "open_tube", "piston") else smp["name"]
            d.text((x0 + bw + int(10 * s), yy + int(1 * s)), f"{label}, n={smp['n']}", font=fs, fill=(40, 40, 48))


def frames_for(run, every=1, hold_s=2.0, fps=25, w=W, h=H):
    out = []
    for f in range(0, run.F, every):
        out.append(run.frame(f, w, h))
    last = run.frame(run.F - 1, w, h, result=True)
    out += [last] * int(hold_s * fps)
    return out


def write_gif(frames, path, fps):
    # One palette for the whole GIF: 104 colours from several frames, plus the group colours at
    # 24 shades pinned exactly, so the legend and the particles keep their colours in every frame.
    w, h = frames[0].size
    pick = np.linspace(0, len(frames) - 1, 6).astype(int)
    mosaic = Image.new("RGB", (w, h * len(pick)))
    for j, k in enumerate(pick):
        mosaic.paste(frames[k].convert("RGB"), (0, j * h))
    base = mosaic.quantize(colors=104, method=Image.Quantize.MEDIANCUT).getpalette()[: 104 * 3]
    pinned = []
    for c in GROUP_RGB:
        for shade in (0.35, 0.5, 0.65, 0.8, 0.9, 1.0):
            pinned += [int(255 * min(1.0, v * shade)) for v in c]
    pal = Image.new("P", (1, 1))
    pal.putpalette(base + pinned + [0, 0, 0] * (256 - 104 - len(pinned) // 3))
    q = [fr.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=int(1000 / fps), loop=0, optimize=True)


def gif_from_mp4(name, size=(800, 500), fps=20, hold=50):
    rd = imageio.get_reader(os.path.join(MEDIA, f"{name}.mp4"))
    frames = [Image.fromarray(f).resize(size, Image.LANCZOS) for f in rd]
    rd.close()
    frames = frames[: len(frames) - 75] + [frames[-1]] * hold
    write_gif(frames, os.path.join(MEDIA, f"{name}.gif"), fps)
    print(name, "gif", os.path.getsize(os.path.join(MEDIA, f"{name}.gif")) // 1024, "KB", flush=True)


def write_mp4(frames, path, fps):
    with imageio.get_writer(path, fps=fps, codec="libx264", quality=7, pixelformat="yuv420p",
                            macro_block_size=8) as wtr:
        for fr in frames:
            wtr.append_data(np.asarray(fr.convert("RGB")))


def title_card(text, sub, w=W, h=H):
    im = Image.new("RGB", (w, h), (246, 246, 248))
    d = ImageDraw.Draw(im)
    fb = ImageFont.truetype(FONT_B, 44)
    fr = ImageFont.truetype(FONT, 26)
    d.text((80, h // 2 - 60), text, font=fb, fill=(25, 25, 30))
    d.text((80, h // 2 + 6), sub, font=fr, fill=(80, 80, 90))
    return im


def main(args):
    os.makedirs(MEDIA, exist_ok=True)
    if args and args[0] == "--gif-from-mp4":
        for n in args[1:]:
            gif_from_mp4(n)
        return
    if args and args[0] == "--combined":
        # stitch the per-method MP4s together with a title card before each
        names = args[1:] or ["fill", "open_tube", "piston", "thief", "spoon", "peel", "pour"]
        fps = 30
        with imageio.get_writer(os.path.join(MEDIA, "all-methods.mp4"), fps=fps, codec="libx264", quality=7,
                                pixelformat="yuv420p", macro_block_size=8) as wtr:
            card = np.asarray(title_card("Sampling a layered powder jar (DEM)",
                                         "colour = when the powder was made; which method keeps the layers apart?"))
            for _ in range(75):
                wtr.append_data(card)
            for n in names:
                card = np.asarray(title_card(TITLES[n], ""))
                for _ in range(30):
                    wtr.append_data(card)
                rd = imageio.get_reader(os.path.join(MEDIA, f"{n}.mp4"))
                for fr in rd:
                    wtr.append_data(fr)
                rd.close()
        return
    for n in args:
        run = Run(n)
        frames = [run.frame(f) for f in range(run.F)]
        last = run.frame(run.F - 1, result=True)
        write_mp4(frames + [last] * 75, os.path.join(MEDIA, f"{n}.mp4"), 30)
        gif = [fr.resize((800, 500), Image.LANCZOS) for fr in frames + [last] * 50]
        write_gif(gif, os.path.join(MEDIA, f"{n}.gif"), 20)
        print(n, run.F, "frames;", os.path.getsize(os.path.join(MEDIA, f"{n}.gif")) // 1024, "KB gif,",
              os.path.getsize(os.path.join(MEDIA, f"{n}.mp4")) // 1024, "KB mp4", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
