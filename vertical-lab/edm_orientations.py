"""Tensile bars printed at three build orientations, and how each comes off its plate on the wire EDM (#303, PR #318).

Sterling (PR #318, 2026-11-05 22:56): "Noting that sometimes we're going to be doing tensile bars at different
orientations. How is that going to work with the automated EDM process? Do this, and also open a new PR focused on
that." The answer is in ``notes/edm_orientations.md``; this script draws its set-ups, in the EDM's frame (x along the
wire's travel, y from the front into the machine, z up), the plate's bar face at y = 0:

1. flat (XY; XYZ in ISO/ASTM 52921's notation), on 2.5 mm of support ribs: the wire runs through the ribs, 1.2 mm off
   the plate's face, along each bar's length; a comb under the bars catches them (chapter 5's ``catch_comb``);
2. vertical (Z; ZXY): the bars stand out of the plate's face, level; the wire cuts across their 10 x 6 mm feet and each
   settles 0.5 mm into a trough (chapter 5's ``zbar_troughs``);
3. at 45 deg: the bars stand out forward and up, hung from their support walls; the wire cuts each one's oblique foot
   and its supports' roots, and a cradle at 45 deg takes the bar with its supports;
4. all three on one plate, cut in one pass on edge (the wire meets them in order of x);
5. sectioning first: the plate flat on the table, the wire cutting it into strips, one orientation per strip.

    python3 runner_guard.py slot --quick --mem 1500 --label edm-orient -- xvfb-run -a python3 edm_orientations.py
    -> out/edm_orientations.png (the five panels) and out/edm_orientations_<n>.png

Every size is from chapter 5 (``alloy_models``: the E8 subsize bar, the 170 mm plate) or assumed (supports, cradles).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import alloy_models as M  # noqa: E402

OUT = HERE / "out"
E = M.E8_SUB
R_PL, T_PL = M.PLATE["r"], M.PLATE["t"]
BAR = (0.60, 0.61, 0.62)
C_XY, C_Z, C_45 = (0.10, 0.58, 0.64), (0.93, 0.60, 0.10), (0.80, 0.22, 0.55)   # one colour per orientation (legend)
SUP = (0.86, 0.80, 0.62)
FIX = (0.30, 0.31, 0.33)
PLATE_C = (0.78, 0.79, 0.81)
WIRE = (0.86, 0.68, 0.28)
CUT = (0.95, 0.35, 0.10)
W_Y = -1.2                              # the cut plane: 1.2 mm off the plate's face (through the flat bars' ribs)


def _box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def bar_long_y() -> pv.PolyData:
    """The E8 subsize bar, long axis along -y from its foot at y = 0 to y = -100, 10 mm (grip) across x, 6 mm thick
    along z, centred on its axis."""
    return M.bar_mesh().translate((0.0, -E["L"] / 2, -E["T"] / 2), inplace=False)


def plate_on_edge(cx=0.0, cz=0.0) -> pv.PolyData:
    return pv.Cylinder(center=(cx, T_PL / 2, cz), direction=(0, 1, 0), radius=R_PL, height=T_PL,
                       resolution=96).triangulate()


def fixture(cx=0.0, cz=0.0) -> pv.PolyData:
    """The zero-point receiver behind the plate, the angle plate and its foot on the table (as chapter 5's)."""
    rec = pv.Cylinder(center=(cx, T_PL + 15, cz), direction=(0, 1, 0), radius=48, height=30).triangulate()
    ang = _box(cx - 140, cx + 140, T_PL + 30, T_PL + 60, cz - 150, cz + 120)
    foot = _box(cx - 180, cx + 180, T_PL + 30, T_PL + 120, cz - 170, cz - 150)
    table = _box(cx - 260, cx + 260, -260, 200, cz - 190, cz - 170)
    return rec.merge(ang).merge(foot).merge(table)


def wire_head(x, cz=0.0):
    up = _box(x - 40, x + 40, W_Y - 40, W_Y + 40, cz + 135, cz + 260)
    lo = _box(x - 30, x + 30, W_Y - 30, W_Y + 30, cz - 168, cz - 135)
    wire = pv.Cylinder(center=(x, W_Y, cz), direction=(0, 0, 1), radius=0.9, height=270.0).triangulate()
    return up.merge(lo), wire


# ------------------------------------------------------------------------------------------------ the three kinds
def flat_bar(x, cz=0.0, s=2.5):
    """A flat (XY) bar on its support ribs, plate on edge: long axis vertical (z), 6 mm out from y = -s to -s - 6."""
    bar = M.bar_mesh().translate((0.0, 0.0, 0.0), inplace=False)       # long along y, z 0..6
    bar.rotate_x(90.0, inplace=True)                                    # long along z, thickness along y (-6..0)
    bar.translate((x, -s, cz), inplace=True)
    ribs = None
    for z in np.arange(-48.0, 48.1, 4.0):
        r = _box(x - 4.0, x + 4.0, -s, 0.0, cz + z - 0.4, cz + z + 0.4)
        ribs = r if ribs is None else ribs.merge(r)
    return bar, ribs


def z_bar(x, z, cz=0.0):
    """A vertical (Z) bar standing out of the plate's face, level, its foot at y = 0."""
    return bar_long_y().translate((x, 0.0, cz + z), inplace=False)


def bar45(x, z, cz=0.0):
    """A bar printed at 45 deg, standing out forward and up from its foot at the plate's face, hung from support walls
    above it (the side that faced the plate in the printer); -> (bar, supports)."""
    b = M.bar_mesh().translate((0.0, -E["L"] / 2 - 6.0, -E["T"] / 2), inplace=False)   # foot 6 mm inside the plate
    b.rotate_x(-45.0, point=(0, 0, 0), inplace=True)                  # -y -> forward and up
    b.translate((x, 0.0, cz + z), inplace=True)
    d = np.array([0.0, -math.cos(math.radians(45)), math.sin(math.radians(45))])
    up = np.array([0.0, math.sin(math.radians(45)), math.cos(math.radians(45))])     # the bar's upper face's normal
    sup = None
    for t in np.arange(8.0, 96.0, 6.0):
        p = np.array([x, 0.0, cz + z]) + d * t + up * (E["T"] / 2)                 # on the bar's upper face
        y_face = 0.0
        if p[1] >= y_face:
            continue
        w = _box(x - 4.0, x + 4.0, p[1], y_face, p[2] - 0.35, p[2] + 0.35)            # a wall back to the plate
        sup = w if sup is None else sup.merge(w)
    return b, sup


def trough(x, z, cz=0.0, reach=102.0):
    """A U trough under a level bar (Z): floor 0.5 mm under it."""
    top = cz + z - E["T"] / 2 - 0.5
    return _box(x - 8, x + 8, -reach, -6.0, top - 4, top).merge(_box(x - 8, x - 6, -reach, -6.0, top, top + 4)).merge(
        _box(x + 6, x + 8, -reach, -6.0, top, top + 4))


def cradle45(x, z, cz=0.0):
    """A cradle at 45 deg under a 45 deg bar: a channel 0.5 mm under its lower face, with an end stop near the plate."""
    c = _box(-8, 8, -98.0, -10.0, -4.0, 0.0).merge(_box(-8, -6, -98.0, -10.0, 0.0, 4.0)).merge(
        _box(6, 8, -98.0, -10.0, 0.0, 4.0)).merge(_box(-8, 8, -12.0, -10.0, 0.0, 9.0))
    c.translate((0.0, 0.0, -E["T"] / 2 - 0.5), inplace=True)
    c.rotate_x(-45.0, point=(0, 0, 0), inplace=True)
    return c.translate((x, 0.0, cz + z), inplace=False)


def comb(xs, cz=0.0):
    """A comb under flat bars standing on end (chapter 5's catch_comb, simplified): a slot for each, walled in front."""
    zf = cz - E["L"] / 2 - 0.5
    xa, xb = min(xs) - 18, max(xs) + 18
    body = _box(xa, xb, -16, -1.4, zf - 10, zf).merge(_box(xa, xb, -21, -16, zf - 10, zf + 75))
    for a, b in zip([xa] + [x + 6.5 for x in sorted(xs)], [x - 6.5 for x in sorted(xs)] + [xb]):
        body = body.merge(_box(a, b, -16, -1.4, zf, zf + 75))
    return body


# ------------------------------------------------------------------------------------------------ the panels
def render(parts, cam, path, size=(1280, 720)):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background((0.97, 0.97, 0.96))
    for mesh, col, op in parts:
        if mesh is None or mesh.n_points == 0:
            continue
        pl.add_mesh(mesh, color=col, opacity=op, smooth_shading=False, specular=0.25)
    pl.enable_anti_aliasing("ssaa")
    pl.camera_position = cam
    pl.camera.view_angle = 30.0
    img = pl.screenshot(None, return_img=True)
    pl.close()
    im = Image.fromarray(img)
    im.save(path)
    return im


def common(parts, x_wire=-40.0, cz=0.0):
    head, wire = wire_head(x_wire, cz)
    parts += [(plate_on_edge(0, cz), PLATE_C, 1.0), (fixture(0, cz), FIX, 1.0), (head, (0.86, 0.87, 0.86), 1.0),
              (wire, WIRE, 1.0)]
    return parts


CAM = [(-360.0, -500.0, 190.0), (-5.0, -45.0, -15.0), (0.0, 0.0, 1.0)]


def panel_flat():
    xs = (-45.0, -15.0, 15.0, 45.0)
    parts = []
    for x in xs:
        b, r = flat_bar(x)
        parts += [(b, C_XY, 1.0), (r, SUP, 1.0)]
    parts.append((comb(xs), FIX, 1.0))
    return common(parts, x_wire=-28.0)


def panel_z():
    parts = []
    for x, z in ((-45.0, 30.0), (-15.0, -30.0), (15.0, 30.0), (45.0, -30.0)):
        parts += [(z_bar(x, z), C_Z, 1.0), (trough(x, z, reach=102.0 if z < 0 else 60.0), FIX, 1.0)]
    return common(parts, x_wire=-28.0)


def panel_45():
    parts = []
    for x in (-45.0, -15.0, 15.0, 45.0):
        b, s = bar45(x, -55.0)
        parts += [(b, C_45, 1.0), (s, SUP, 1.0), (cradle45(x, -55.0), FIX, 1.0)]
    return common(parts, x_wire=-28.0)


def panel_mixed():
    parts = []
    for x in (-50.0, -30.0):                                        # two flat ones
        b, r = flat_bar(x, s=2.5)
        parts += [(b, C_XY, 1.0), (r, SUP, 1.0)]
    parts.append((comb((-50.0, -30.0)), FIX, 1.0))
    for x, z in ((0.0, 40.0), (0.0, -10.0)):                        # two vertical ones (the upper trough short)
        parts += [(z_bar(x, z), C_Z, 1.0), (trough(x, z, reach=60.0 if z > 0 else 102.0), FIX, 1.0)]
    for x in (35.0, 58.0):                                          # two at 45 deg
        b, s = bar45(x, -62.0)
        parts += [(b, C_45, 1.0), (s, SUP, 1.0), (cradle45(x, -62.0), FIX, 1.0)]
    return common(parts, x_wire=-62.0)


def panel_section():
    """The plate flat on the table, the wire cutting it into strips (one orientation per strip) before each strip
    goes on edge."""
    plate = pv.Cylinder(center=(0, 0, -T_PL / 2), direction=(0, 0, 1), radius=R_PL, height=T_PL,
                        resolution=96).triangulate()
    parts = [(plate, PLATE_C, 1.0)]
    for x in (-50.0, -30.0):
        b = M.bar_mesh().translate((x, 0.0, 2.5), inplace=False)
        parts.append((b, C_XY, 1.0))
    for x, y in ((0.0, 25.0), (0.0, -25.0)):
        parts.append((z_bar(0, 0).rotate_x(-90.0, inplace=False).translate((x, y, 0.0), inplace=False), C_Z, 1.0))
    table = _box(-260, 260, -200, 200, -T_PL - 40, -T_PL - 20)
    rails = _box(-200, 200, -95, -75, -T_PL - 20, -T_PL).merge(_box(-200, 200, 75, 95, -T_PL - 20, -T_PL))
    parts += [(table, FIX, 1.0), (rails, (0.42, 0.44, 0.47), 1.0)]
    for xc in (-16.0, 20.0):                                        # the two strip cuts, through the plate
        parts.append((_box(xc - 0.4, xc + 0.4, -R_PL - 2, R_PL + 2, -T_PL - 0.5, 0.5), CUT, 1.0))
    wire = pv.Cylinder(center=(20.0, 40.0, 40.0), direction=(0, 0, 1), radius=0.9, height=180.0).triangulate()
    up = _box(-20, 60, 0, 80, 130, 200)
    parts += [(wire, WIRE, 1.0), (up, (0.86, 0.87, 0.86), 1.0)]
    cam = [(-300.0, -400.0, 380.0), (0.0, 0.0, 10.0), (0.0, 0.0, 1.0)]
    return parts, cam


TITLES = [("1  Flat (XY), on 2.5 mm of ribs", "plate on edge; the wire runs through the ribs along each bar; a comb "
           "catches them standing on end"),
          ("2  Vertical (Z)", "plate on edge; the bars stand out level; the wire cuts each 10 x 6 mm foot; a trough "
           "catches each"),
          ("3  45 deg, on support walls", "plate on edge; bar and supports come off together onto a 45 deg cradle; "
           "the supports are taken off later"),
          ("4  All three on one plate", "one pass on edge: the wire meets them in order of x; each kind has its own "
           "catch, each bar its own slot"),
          ("5  Or section the plate first", "flat on the table, the wire cuts it into strips, one orientation per "
           "strip; each strip then goes on edge")]


def font(size):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def label(im, title, sub):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, im.width, 74), fill=(255, 255, 255))
    d.text((18, 8), title, fill=(20, 20, 20), font=font(30))
    d.text((18, 44), sub, fill=(70, 70, 70), font=font(19))
    return im


def main():
    OUT.mkdir(exist_ok=True)
    ims = []
    for i, (f, (t, sub)) in enumerate(zip((panel_flat, panel_z, panel_45, panel_mixed), TITLES)):
        im = render(f(), CAM, OUT / f"edm_orientations_{i + 1}.png")
        ims.append(label(im, t, sub))
        ims[-1].save(OUT / f"edm_orientations_{i + 1}.png", optimize=True)
    parts, cam = panel_section()
    im = label(render(parts, cam, OUT / "edm_orientations_5.png"), *TITLES[4])
    im.save(OUT / "edm_orientations_5.png", optimize=True)
    ims.append(im)
    w, h = 640, 360
    sheet = Image.new("RGB", (w * 2, h * 3), "white")
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((w, h), Image.LANCZOS), ((i % 2) * w, (i // 2) * h))
    d = ImageDraw.Draw(sheet)
    d.text((w + 18, 2 * h + 40), "Tensile bars at three build orientations", fill=(20, 20, 20), font=font(26))
    d.text((w + 18, 2 * h + 80), "on a vertical-wire EDM (FANUC ROBOCUT class):", fill=(60, 60, 60), font=font(20))
    d.text((w + 18, 2 * h + 108), "the plate stands on edge for every kind,", fill=(60, 60, 60), font=font(20))
    d.text((w + 18, 2 * h + 136), "since the wire cuts in a plane that holds it.", fill=(60, 60, 60), font=font(20))
    for k, (c, t) in enumerate(((C_XY, "flat (XY)"), (C_Z, "vertical (Z)"), (C_45, "45 deg"), (SUP, "supports"))):
        x0 = w + 18 + k * 150
        d.rectangle((x0, 2 * h + 236, x0 + 22, 2 * h + 254), fill=tuple(int(255 * v) for v in c))
        d.text((x0 + 28, 2 * h + 234), t, fill=(40, 40, 40), font=font(17))
    d.text((w + 18, 2 * h + 176), "notes/edm_orientations.md: limits, cut times,", fill=(60, 60, 60), font=font(18))
    d.text((w + 18, 2 * h + 200), "properties, sources. Sizes from chapter 5 or assumed.", fill=(60, 60, 60),
           font=font(18))
    sheet.save(OUT / "edm_orientations.png", optimize=True)
    print("wrote", OUT / "edm_orientations.png", flush=True)


if __name__ == "__main__":
    main()
