"""Two stills of the colour code applied, kept sparing (colour_coding.py; notes/colour_coding.md).

    xvfb-run -a python3 colour_vignette.py        # out/colour/bench.png, out/colour/floor_bay.png

1. **The bench**: the sieving cell's bench with an Al set and a Cu set side by side, each dedicated to its family: two
   sieves and a pan (a band on each handling tab), the powder's funnel (its band), a brush (a band on its collar), two
   jars (a stripe on the label, the caps stay black), the family's powder-waste can (a band), and the HOLD bin with
   its red tag. The parts are the model's own (sieve_station, charge.funnel, atom_brush, props.jar_parts).
2. **The floor at the bay**: a MiR250 docked at Shuttle 1's opening on the floor marking: the yellow lane edge, the
   white dock outline, the black/yellow operating hazard zone 0.5 m round the docked MiR250, a red/white keep-clear
   square at an extinguisher and a green square at the spill kit (both illustrative until the safety-assets PR places
   them).
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

import colour_coding as CC
from scene import OUT, Scene

SIZE = (1600, 900)
BLUE, ORANGE = (CC._rgb1(CC.FAMILY["Al"]["rgb"]), CC._rgb1(CC.FAMILY["Cu"]["rgb"]))
STEEL, GREY, BENCH, BLACK = (0.72, 0.74, 0.77), (0.55, 0.57, 0.60), (0.86, 0.87, 0.88), (0.08, 0.08, 0.09)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def _ring(r_out, r_in, z0, z1, res=72):
    return pv.Cylinder(center=(0, 0, (z0 + z1) / 2), direction=(0, 0, 1), radius=r_out, height=z1 - z0,
                       resolution=res).triangulate().boolean_difference(
        pv.Cylinder(center=(0, 0, (z0 + z1) / 2), direction=(0, 0, 1), radius=r_in, height=z1 - z0 + 2,
                    resolution=res).triangulate()) if r_in > 0 else None


def _band(r, z0, z1, res=72):
    """A thin coloured band (tape) round a cylinder of radius r: an open tube 0.6 mm proud."""
    return pv.Cylinder(center=(0, 0, (z0 + z1) / 2), direction=(0, 0, 1), radius=r + 0.6, height=z1 - z0,
                       resolution=res, capping=False).triangulate()


def _px(sc, xyz):
    fx, fy = sc.project(xyz)
    return fx * sc.size[0], fy * sc.size[1]


def _diag_stripes(x0, x1, y0, y1, pitch, z1):
    """Diagonal stripes over the square [x0, x1] x [y0, y1]: (polygon mesh, even) pairs, each extruded to z1."""
    def clip(poly, keep):
        out = []
        for i in range(len(poly)):
            a, b = poly[i - 1], poly[i]
            ka, kb = keep(a), keep(b)
            if kb:
                if not ka:
                    out.append(_cut(a, b, keep))
                out.append(b)
            elif ka:
                out.append(_cut(a, b, keep))
        return out

    def _cut(a, b, keep):
        lo, hi = 0.0, 1.0
        for _ in range(40):
            m = (lo + hi) / 2
            p = (a[0] + (b[0] - a[0]) * m, a[1] + (b[1] - a[1]) * m)
            if keep(p) == keep(a):
                lo = m
            else:
                hi = m
        return (a[0] + (b[0] - a[0]) * lo, a[1] + (b[1] - a[1]) * lo)
    sq = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out, k = [], 0
    c = (x0 - y1)
    while c < x1 - y0:
        c0, c1 = c, c + pitch
        poly = clip(clip(sq, lambda p, c0=c0: p[0] - p[1] >= c0), lambda p, c1=c1: p[0] - p[1] <= c1)
        if len(poly) >= 3:
            pts = np.array([(px, py, 0.0) for px, py in poly])
            face = np.hstack([[len(pts)], np.arange(len(pts))])
            m = pv.PolyData(pts, face).extrude((0, 0, z1), capping=True).triangulate()
            out.append((m, k % 2 == 0))
        c += pitch
        k += 1
    return out


def _put(sc, name, mesh, colour, at, rot_z=0.0, **kw):
    m = mesh.copy()
    if rot_z:
        m.rotate_z(rot_z, inplace=True)
    m.translate(at, inplace=True)
    sc.add(name, m, colour, **kw)


def family_set(sc, fam: str, x0: float, y0: float, z0: float) -> dict:
    """One family's tools on the bench, from x0; returns label anchors."""
    import atom_brush as AB
    import charge as CH
    import props as P
    import sieve_station as SS
    c = BLUE if fam == "Al" else ORANGE
    anchors = {}
    # the sieves and the pan, nested on their stand, tab to the front, each tab with a 12 mm band (the tab is the model's)
    zz = z0
    for i, key in enumerate(("pan", "s325", "s230")):
        parts = SS.sieve_parts(key)
        for nm, (m, col, spec, op) in parts.items():
            if nm == "tag":
                continue
            colour = c if nm == "tab" else col
            _put(sc, f"{fam} {key} {nm}", m, colour, (x0, y0, zz), specular=spec, opacity=op)
        zz += 46.0
    anchors["sieves: a band on each handling tab"] = (x0, y0 - 140, zz)
    # the powder's funnel on a little stand: the band is the family's colour, and carries the powder's name
    f = CH.funnel()
    stand = _box(-24, 24, -24, 24, 0, 30)
    fx = x0 + 210
    _put(sc, f"{fam} funnel stand", stand, GREY, (fx, y0 - 40, z0))
    _put(sc, f"{fam} funnel", f["body"], (0.95, 0.95, 0.94), (fx, y0 - 40, z0 + 30))
    _put(sc, f"{fam} funnel band", f["label"], c, (fx, y0 - 40, z0 + 30))
    anchors["funnel: its band, and the powder's name"] = (fx, y0 - 40, z0 + 70)
    # the brush, lying on the bench, grip and collars neutral, a band on the shaft by the collar
    bm = AB.brush_meshes()
    allb = pv.merge([m for m, _ in bm.values()])
    lo = np.array(allb.bounds[::2])
    for nm, (m, col) in bm.items():
        colour = GREY if "grip" in nm else (STEEL if "collars" not in nm else (0.30, 0.31, 0.33))
        mm = m.copy().translate(-lo, inplace=False).rotate_z(-90, inplace=False)
        _put(sc, f"{fam} {nm}", mm, colour, (x0 + 290, y0 - 120, z0 + 2))
    cb = bm["atc brush collars"][0].copy().translate(-lo, inplace=False).rotate_z(-90, inplace=False)
    cx = (cb.bounds[0] + cb.bounds[1]) / 2 + x0 + 290
    band = pv.Cylinder(center=(0, 0, 0), direction=(1, 0, 0), radius=9.0, height=16, resolution=40).triangulate()
    _put(sc, f"{fam} brush band", band, c, (cx + 30, y0 - 120 + (cb.bounds[2] + cb.bounds[3]) / 2,
                                             z0 + 2 + (cb.bounds[4] + cb.bounds[5]) / 2))
    anchors["brush: a band by the collar"] = (cx + 30, y0 - 120, z0 + 20)
    # two 250 mL jars: clear glass, black cap, white label with a 4 mm stripe along its top edge
    d, h, lid = 70.0, 92.0, 18.0
    for j in range(2):
        pp = P.jar_parts(d, h, lid, fill=0.55, label=(0.24, 0.58))
        jx, jy = x0 + 470 + j * 85, y0 - 10
        for nm, (m, col, op) in pp.items():
            _put(sc, f"{fam} jar{j} {nm}", m, col, (jx, jy, z0), opacity=op)
        _put(sc, f"{fam} jar{j} stripe", _band(d / 2 + 0.5, 0.58 * h - 4.0, 0.58 * h), c, (jx, jy, z0))
    anchors["jars: a stripe on the label; caps stay black"] = (x0 + 512, y0 - 10, z0 + 120)
    # the family's powder-waste can: steel, black lid, a 25 mm band
    can = pv.Cylinder(center=(0, 0, 110), direction=(0, 0, 1), radius=90, height=220, resolution=72).triangulate()
    lidm = pv.Cylinder(center=(0, 0, 226), direction=(0, 0, 1), radius=93, height=12, resolution=72).triangulate()
    _put(sc, f"{fam} can", can, STEEL, (x0 + 760, y0 + 40, z0), specular=0.5)
    _put(sc, f"{fam} can lid", lidm, BLACK, (x0 + 760, y0 + 40, z0))
    _put(sc, f"{fam} can band", _band(90, 150, 175), c, (x0 + 760, y0 + 40, z0))
    anchors["powder waste: one can per family (never mixed)"] = (x0 + 760, y0 + 40, z0 + 250)
    return anchors


def bench() -> None:
    sc = Scene("colour_bench", "Colour code: the bench", size=SIZE, gif=False, mp4=False)
    z0 = 900.0
    sc.add("floor", _box(-1500, 1700, -900, 900, -10, 0), (0.80, 0.81, 0.82))
    sc.add("bench top", _box(-1250, 1450, -420, 420, z0 - 40, z0), BENCH, specular=0.1)
    sc.add("bench legs", _box(-1200, -1150, -380, 380, 0, z0 - 40).merge(_box(1350, 1400, -380, 380, 0, z0 - 40)),
           GREY)
    sc.add("backboard", _box(-1250, 1450, 380, 420, z0, z0 + 700), (0.93, 0.93, 0.94), specular=0.05)
    # shadow-board outlines on the backboard: each family's tools have their own outlined place
    an = family_set(sc, "Al", -1000.0, -60.0, z0)
    an_cu = family_set(sc, "Cu", 100.0, -60.0, z0)
    # the HOLD bin, neutral grey, with a red tag that says HOLD
    sc.add("hold bin", _box(1050, 1300, -200, 120, z0, z0 + 130), GREY)
    sc.add("hold tag", _box(1125, 1225, -203, -200, z0 + 40, z0 + 100), (0.78, 0.06, 0.18), specular=0.05)
    sc.cam = [(150, -2500, 1900), (150, 0, 960), (0, 0, 1)]
    sc.view_angle = 33.0
    img = Image.fromarray(sc.render_base())
    d = ImageDraw.Draw(img)
    fb, f = ImageFont.truetype(FONT_B, 30), ImageFont.truetype(FONT, 21)
    d.text((40, 28), "One bench, two families: colour only where it decides which tool touches which powder",
           font=fb, fill=(31, 35, 40))
    d.text((40, 70), "Al family blue, Cu family orange. Everything else stays white, grey, black, steel and glass.",
           font=f, fill=(75, 85, 99))
    fl = ImageFont.truetype(FONT, 17)
    n = len(an)
    for i, (text, xyz) in enumerate(an.items()):          # the rightmost item's label on the top row: no crossings
        x, y = _px(sc, xyz)
        ty = 668 + 34 * (n - 1 - i)
        d.line((x, y, x, ty - 4), fill=(140, 145, 153), width=2)
        d.text((x - 8, ty), text, font=fl, fill=(31, 35, 40), stroke_width=3, stroke_fill="white")
    for nm, anchor in (("Al family set", an), ("Cu family set", an_cu)):
        x, y = _px(sc, list(anchor.values())[0])
        d.text((x - 60, 128), nm, font=ImageFont.truetype(FONT_B, 26),
               fill=tuple(int(255 * v) for v in (BLUE if nm.startswith("Al") else ORANGE)))
    x, y = _px(sc, (1175, -205, z0 + 140))
    d.text((x - 90, y - 40), "HOLD bin: a red tag", font=fl, fill=(31, 35, 40), stroke_width=3,
           stroke_fill="white")
    img.save(OUT / "colour" / "bench.png", optimize=True)
    sc.pl.close()


def floor_bay() -> None:
    import props as P
    sc = Scene("colour_floor_bay", "Colour code: the floor at the bay", size=SIZE, gif=False, mp4=False)
    Y, K, W_, R, G = (0.95, 0.76, 0.0), (0.12, 0.12, 0.12), (0.98, 0.98, 0.98), (0.78, 0.06, 0.18), (0.0, 0.52, 0.24)
    sc.add("floor", _box(-4200, 4200, -6400, 300, -10, 0), (0.80, 0.81, 0.82), specular=0.05)
    # Shuttle 1's front, its opening at 854 mm (tray_plan.json slots.open.z), cladding light grey
    sc.add("vlm front", _box(-1415, -505, -40, 0, 0, 3600).merge(_box(505, 1415, -40, 0, 0, 3600))
           .merge(_box(-505, 505, -40, 0, 0, 854)).merge(_box(-505, 505, -40, 0, 1850, 3600)),
           (0.90, 0.91, 0.92), specular=0.05)
    sc.add("vlm opening", _box(-505, 505, -10, 0, 854, 1850), (0.35, 0.37, 0.40))
    # the docked MiR250 (props.mir250), its back to the opening, 1932 mm out (tray_plan.json floor.docks.vlm)
    dock_y = -1932.0
    for nm, (m, col) in P.mir250().items():
        mm = m.copy().rotate_z(90, inplace=False)
        _put(sc, f"mir {nm}", mm, col, (0.0, dock_y, 0.0))
    L, W = P.MIR["L"], P.MIR["W"]
    hx, hy = W / 2, L / 2                       # turned 90 deg: its long side along y
    t = 2.0                                     # tape thickness, mm
    # the white dock outline, 50 mm tape, just outside the MiR's footprint
    for (x0, x1, y0, y1) in ((-hx - 60, hx + 60, dock_y - hy - 60, dock_y - hy - 10),
                             (-hx - 60, hx + 60, dock_y + hy + 10, dock_y + hy + 60),
                             (-hx - 60, -hx - 10, dock_y - hy - 60, dock_y + hy + 60),
                             (hx + 10, hx + 60, dock_y - hy - 60, dock_y + hy + 60)):
        sc.add(f"dock tape {x0:.0f} {y0:.0f}", _box(x0, x1, y0, y1, 0, t), W_, specular=0.05)
    # the operating hazard zone: 1 m round the docked MiR (MiR250 User Guide v1.2, section 10.7), its edge in 100 mm
    # black/yellow tape, closed against the Shuttle's front
    zx0, zx1, zy0, zy1 = -hx - 1000, hx + 1000, dock_y - hy - 1000, -45.0
    k = 0
    for (a, b, horiz, fixed) in ((zx0, zx1, True, zy0), (zy0, zy1, False, zx0), (zy0, zy1, False, zx1)):
        n = int(abs(b - a) // 150)
        for i in range(n):
            s0, s1 = a + i * (b - a) / n, a + (i + 1) * (b - a) / n
            col = Y if i % 2 == 0 else K
            box = (_box(s0, s1, fixed - 50, fixed + 50, 0, t + 0.5) if horiz else
                   _box(fixed - 50, fixed + 50, s0, s1, 0, t + 0.5))
            sc.add(f"hazard {k}", box, col, specular=0.05)
            k += 1
    # the MiR lane's edge: 75 mm yellow, along the aisle (tray_plan.json floor.aisle_mm: y -2400)
    sc.add("lane edge", _box(-4200, 4200, -2437, -2363, 0, t), Y, specular=0.05)
    sc.add("lane edge 2", _box(-4200, 4200, -5437, -5363, 0, t), Y, specular=0.05)
    # an extinguisher on a stand with its red/white keep-clear square, and the spill kit on its green square
    ex, ey = -2350.0, -1150.0
    for i, (m, even) in enumerate(_diag_stripes(ex - 450, ex + 450, ey - 450, ey + 450, 150.0, t)):
        sc.add(f"keep {i}", m, R if even else W_, specular=0.05)
    sc.add("extinguisher", pv.Cylinder(center=(ex, ey, 380), direction=(0, 0, 1), radius=90, height=600,
                                       resolution=48).triangulate(), R, specular=0.3)
    sc.add("extinguisher head", _box(ex - 40, ex + 40, ey - 30, ey + 30, 680, 760), BLACK)
    sx, sy = 2350.0, -1150.0
    sc.add("spill square", _box(sx - 450, sx + 450, sy - 450, sy + 450, 0, t), G, specular=0.05)
    sc.add("spill kit", _box(sx - 250, sx + 250, sy - 200, sy + 200, t, 600), (0.90, 0.90, 0.88), specular=0.1)
    sc.cam = [(3600, -7200, 4300), (0, -1700, 400), (0, 0, 1)]
    sc.view_angle = 32.0
    img = Image.fromarray(sc.render_base())
    d = ImageDraw.Draw(img)
    fb, f, fs = ImageFont.truetype(FONT_B, 30), ImageFont.truetype(FONT, 21), ImageFont.truetype(FONT, 18)
    d.text((40, 28), "The floor at Shuttle 1's opening: five meanings, the rest bare floor", font=fb,
           fill=(31, 35, 40))
    d.text((40, 70), "The extinguisher and spill-kit spots are illustrative until the safety-assets PR places them.",
           font=f, fill=(75, 85, 99))
    for text, xyz in (("black/yellow: operating hazard zone, 1 m round the docked MiR250", (zx1, dock_y - 800, 0)),
                      ("white: where the robot docks", (hx + 60, dock_y + 300, 0)),
                      ("yellow: the lane's edge", (2600, -2400, 0)),
                      ("red/white: keep clear (extinguisher)", (ex, ey - 450, 0)),
                      ("green: safety equipment (spill kit)", (sx, sy - 450, 0))):
        x, y = _px(sc, xyz)
        left = x > 0.62 * sc.size[0]                     # near the right edge: the text goes to the left
        tx = x - 30 if left else x + 30
        d.line((x, y, tx, y + 40), fill=(60, 64, 70), width=2)
        w = d.textlength(text, font=fs)
        d.text((tx - w - 4 if left else tx + 4, y + 36), text, font=fs, fill=(31, 35, 40), stroke_width=3,
               stroke_fill="white")
    img.save(OUT / "colour" / "floor_bay.png", optimize=True)
    sc.pl.close()


if __name__ == "__main__":
    (OUT / "colour").mkdir(parents=True, exist_ok=True)
    bench()
    floor_bay()
    print("wrote out/colour/bench.png and out/colour/floor_bay.png")
