"""Stand-alone views of the miniature powder doser, with no atomizer chamber around it: powder-doser PR 176's doser as
built next to the module folded from its own parts (doser_cad.compact_meshes), at the same scale, the module at its
35 deg mounting tilt, and a turntable of the module.

Needs doser_cad.py (in ../ods-lpbf-gifs/ here, or next to this file), the doser's STEP from powder-doser PR 176,
cadquery-ocp 7.9 (8.0 moved TDF_LabelSequence) and pyvista 0.49:
    git clone --filter=blob:none --no-checkout https://github.com/vertical-cloud-lab/powder-doser.git /tmp/powder-doser
    git -C /tmp/powder-doser fetch origin claude/issue-172-20261003-2216
    git -C /tmp/powder-doser checkout 509a0bf -- cad/text-to-cad/STEP
    pip install "cadquery-ocp>=7.9.3.1,<8.0" pyvista==0.49.0 pillow
    POWDER_DOSER=/tmp/powder-doser/cad/text-to-cad xvfb-run -a -s "-screen 0 1920x1080x24" python module_views.py
Writes module_views.png and module_turntable.gif next to this file.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "ods-lpbf-gifs"))
import doser_cad as D                                   # noqa: E402

TILT = 35.0                                             # deg, outlet down, as mounted in ods_c_gravity
VIEW = np.array([-0.95, -1.25, 0.80])                   # camera direction from the focus: front left, above
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
INK, MUTED = (20, 22, 28), (90, 96, 106)


def font(px, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, px)


def tilted(meshes, deg):
    """Lift the cap end `deg` about the x axis through the outlet, as the doser's tilt does."""
    return {k: m.rotate_x(deg, point=D.OUTLET, inplace=False) for k, m in meshes.items()}


def size(meshes):
    p = np.vstack([m.points for m in meshes.values()])
    return p.max(axis=0) - p.min(axis=0)


def render(meshes, w, h, scale, focus=None, view=VIEW):
    """One parallel-projection view. `scale` is the half-height of the view in mm, so equal scales mean equal sizes."""
    pl = pv.Plotter(off_screen=True, window_size=(w, h))
    pl.set_background("white")
    for (_, mat), m in meshes.items():
        color, spec = D.MATERIALS[mat]
        pl.add_mesh(m, color=color, specular=spec, specular_power=20, smooth_shading=True)
    p = np.vstack([m.points for m in meshes.values()])
    c = (p.min(axis=0) + p.max(axis=0)) / 2 if focus is None else focus
    pl.camera.focal_point = c
    pl.camera.position = c + 600.0 * view / np.linalg.norm(view)
    pl.camera.up = (0.0, 0.0, 1.0)
    pl.enable_parallel_projection()
    pl.camera.parallel_scale = scale
    pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(return_img=True)
    pl.close()
    return Image.fromarray(img)


def panel(img, title, lines):
    d = ImageDraw.Draw(img)
    d.text((18, 14), title, font=font(26, bold=True), fill=INK)
    for i, t in enumerate(lines):
        d.text((18, 50 + 28 * i), t, font=font(19), fill=MUTED)
    return img


def scale_bar(img, scale, h, mm=50):
    """A bar `mm` long at the panel's scale (parallel projection: `scale` mm is half the panel's height)."""
    px = mm * (h / 2) / scale
    d = ImageDraw.Draw(img)
    x0, y0 = 24, img.height - 34
    d.line((x0, y0, x0 + px, y0), fill=INK, width=4)
    for x in (x0, x0 + px):
        d.line((x, y0 - 8, x, y0 + 8), fill=INK, width=3)
    d.text((x0 + px + 10, y0 - 13), f"{mm} mm", font=font(19), fill=INK)


def views():
    full = D.meshes()
    mini = D.compact_meshes(nose=True)
    body = D.compact_meshes(nose=False)
    w, h, scale = 640, 600, 170.0                       # same scale for both, so the sizes compare directly
    sf, sm, sb = size(full), size(mini), size(body)
    a = panel(render(full, w, h, scale), "As built (powder-doser PR 176)",
              [f"{sf[0]:.0f} × {sf[1]:.0f} × {sf[2]:.0f} mm with its PCB holder",
               "tilt servos, tap solenoid, 250 mm auger tube"])
    scale_bar(a, scale, h)
    b = panel(render(mini, w, h, scale), "Miniature module, same scale",
              [f"{sb[0]:.0f} × {sb[1]:.0f} × {sb[2]:.0f} mm body, {sm[1]:.0f} mm long with the capillary",
               "same tube, gear, NEMA 11, pinion and brackets"])
    scale_bar(b, scale, h)
    c = panel(render(tilted(mini, TILT), w, h, 80.0, view=np.array([-1.0, -0.15, 0.10])),
              f"The module at its {TILT:.0f}° mounting tilt",
              ["capillary and outlet down, cap end up",
               "3 mm bore capillary on the v4 outlet"])
    scale_bar(c, 80.0, h, mm=20)
    sheet = Image.new("RGB", (3 * w + 4 * 12, h + 2 * 12), (232, 234, 238))
    for i, im in enumerate((a, b, c)):
        sheet.paste(im, (12 + i * (w + 12), 12))
    sheet.save(HERE / "module_views.png", optimize=True)
    print("module_views.png", sheet.size, "full", sf.round(1), "module", sb.round(1), "with capillary", sm.round(1))


def turntable(n=36, w=480, h=400):
    mini = tilted(D.compact_meshes(nose=True), TILT)
    p = np.vstack([m.points for m in mini.values()])
    c = (p.min(axis=0) + p.max(axis=0)) / 2
    frames = []
    for i in range(n):
        a = 2 * np.pi * i / n
        v = np.array([np.cos(a) * -0.95 - np.sin(a) * -1.25, np.sin(a) * -0.95 + np.cos(a) * -1.25, 0.80])
        im = render(mini, w, h, 75.0, focus=c, view=v)
        ImageDraw.Draw(im).text((12, 10), "Miniature powder doser module", font=font(18, bold=True), fill=INK)
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
    frames[0].save(HERE / "module_turntable.gif", save_all=True, append_images=frames[1:], duration=100, loop=0,
                   optimize=True)
    print("module_turntable.gif", n, "frames", (HERE / "module_turntable.gif").stat().st_size, "bytes")


if __name__ == "__main__":
    views()
    turntable()
