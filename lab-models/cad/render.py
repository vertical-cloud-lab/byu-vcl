"""PyVista renders of any list of `Model`s, plus contact sheets.

Needs a display; on a headless machine run the callers under Xvfb:

    xvfb-run -a -s "-screen 0 1920x1080x24" python build.py --render
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

from common import MATERIALS, Model

BG = "#fcfcfb"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_cache: dict[int, pv.PolyData] = {}


def to_mesh(shape, tol: float = 0.1) -> pv.PolyData:
    key = id(shape)
    if key not in _cache:
        verts, tris = shape.tessellate(tol, 0.25)
        if not tris:
            _cache[key] = pv.PolyData()
        else:
            pts = np.array([(v.x, v.y, v.z) for v in verts])
            _cache[key] = pv.PolyData(pts, np.hstack([[3, *t] for t in tris]))
    return _cache[key]


def plotter(size=(1400, 1050)) -> pv.Plotter:
    pl = pv.Plotter(off_screen=True, window_size=size, lighting="three lights")
    pl.set_background(BG)
    pl.enable_depth_peeling(12)
    return pl


def add_model(pl: pv.Plotter, model: Model, tol: float | None = None, opacity_scale: float = 1.0) -> None:
    bb = model.bbox()
    size = max(bb.xlen, bb.ylen, bb.zlen)
    tol = tol or max(0.02, size / 1500)
    for p in model.parts:
        mesh = to_mesh(p.shape, tol)
        if mesh.n_points == 0:
            continue
        r, g, b, a, spec = MATERIALS[p.material]
        pl.add_mesh(mesh, color=(r, g, b), opacity=a * opacity_scale, specular=spec, specular_power=40,
                    smooth_shading=True, split_sharp_edges=True, feature_angle=35)


def add_floor(pl: pv.Plotter, bb, margin: float = 3.0, z: float | None = None, color=(0.985, 0.985, 0.98)) -> None:
    """A floor the colour of the background, so only its contact shading (SSAO) shows."""
    w, d = max(bb.xlen, 1) * (1 + 2 * margin), max(bb.ylen, 1) * (1 + 2 * margin)
    s = max(w, d, bb.zlen * 6)
    pl.add_mesh(pv.Plane(center=(bb.center.x, bb.center.y, (bb.zmin if z is None else z) - 0.05), i_size=s, j_size=s),
                color=color, lighting=False)


def view(pl: pv.Plotter, bb, direction=(1.0, -1.35, 0.95), zoom: float = 1.0, parallel: bool = False,
         up=(0, 0, 1)) -> None:
    c = np.array([bb.center.x, bb.center.y, bb.center.z])
    d = np.array(direction, float)
    d /= np.linalg.norm(d)
    diag = math.sqrt(bb.xlen ** 2 + bb.ylen ** 2 + bb.zlen ** 2)
    pl.camera_position = [tuple(c + d * diag * 3), tuple(c), tuple(up)]
    pl.camera.view_angle = 25
    if parallel:
        pl.enable_parallel_projection()
    pl.reset_camera(bounds=(bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    pl.camera.zoom(zoom)


def render(models: list[Model], out: Path, size=(1400, 1050), direction=(1.0, -1.35, 0.95), zoom: float = 1.0,
           floor: bool = True, ssao: bool = True, title: str | None = None, parallel: bool = False,
           bounds_of: list[Model] | None = None) -> Path:
    import cadquery as cq
    pl = plotter(size)
    for m in models:
        add_model(pl, m)
    bb = cq.Compound.makeCompound([p.shape for m in (bounds_of or models) for p in m.parts]).BoundingBox()
    if floor:
        add_floor(pl, bb)
    if ssao:
        s = max(bb.xlen, bb.ylen, bb.zlen)
        pl.enable_ssao(radius=s / 40, bias=s / 2000, kernel_size=64)
    pl.enable_anti_aliasing("ssaa")
    view(pl, bb, direction, zoom, parallel)
    out.parent.mkdir(parents=True, exist_ok=True)
    pl.screenshot(str(out))
    pl.close()
    if title:
        caption(out, title)
    return out


def caption(path: Path, title: str, sub: str | None = None) -> None:
    im = Image.open(path).convert("RGB")
    dr = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FONT_B, max(18, im.width // 55))
    dr.text((24, 18), title, fill=(20, 20, 20), font=f1)
    if sub:
        f2 = ImageFont.truetype(FONT, max(14, im.width // 75))
        dr.text((24, 18 + int(f1.size * 1.4)), sub, fill=(80, 80, 78), font=f2)
    im.save(path)


def contact_sheet(tiles: list[tuple[Path, str, str]], out: Path, cols: int = 5, tile_w: int = 420,
                  title: str = "", sub: str = "") -> Path:
    """tiles: (image, label, sub-label). Crops each tile to its content, then grids them."""
    ims = []
    for path, label, sublabel in tiles:
        im = Image.open(path).convert("RGB")
        arr = np.asarray(im).astype(int)
        bg = np.array(Image.new("RGB", (1, 1), BG).getpixel((0, 0)))
        mask = np.abs(arr - bg).sum(axis=2) > 12
        ys, xs = np.nonzero(mask)
        if len(xs):
            pad = 10
            im = im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad),
                          min(im.height, ys.max() + pad)))
        im.thumbnail((tile_w - 20, int(tile_w * 0.78) - 20))
        ims.append((im, label, sublabel))
    th = int(tile_w * 0.78) + 58
    rows = math.ceil(len(ims) / cols)
    head = 96 if title else 0
    sheet = Image.new("RGB", (cols * tile_w, rows * th + head), BG)
    dr = ImageDraw.Draw(sheet)
    fl, fs = ImageFont.truetype(FONT_B, 17), ImageFont.truetype(FONT, 14)
    if title:
        dr.text((22, 16), title, fill=(15, 15, 15), font=ImageFont.truetype(FONT_B, 30))
        dr.text((22, 58), sub, fill=(90, 90, 88), font=ImageFont.truetype(FONT, 18))
    for i, (im, label, sublabel) in enumerate(ims):
        x0, y0 = (i % cols) * tile_w, head + (i // cols) * th
        sheet.paste(im, (x0 + (tile_w - im.width) // 2, y0 + (int(tile_w * 0.78) - im.height) // 2))
        dr.text((x0 + 12, y0 + int(tile_w * 0.78) + 4), label, fill=(20, 20, 20), font=fl)
        dr.text((x0 + 12, y0 + int(tile_w * 0.78) + 27), sublabel, fill=(95, 95, 92), font=fs)
    sheet.save(out)
    return out
