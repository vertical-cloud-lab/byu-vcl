#!/usr/bin/env python3
"""BUILD.md stage 6 for the compact stirrer, as four renders on one sheet: img/compact_assembly.png.

The bought parts (fan, magnet carrier and magnets, inserts, MOSFET, Hall sensor) are the Onshape
model's, read with assembly_video.onshape_parts() (read-only, cached under .cache/). The base and
the vial holder are the compact STLs. The junction board, the cable, the four M3 washers and the
four M3 x 20 screws are drawn here, to BUILD.md's dimensions: the 8 x 6-hole board on the rails,
where the stop held it until 2026-11-04, with the cable in through the -X notch and its cores
straight into column A, and the MOSFET's legs straight into H2-H4.

    xvfb-run -a python compact/render_compact_steps.py img/compact_assembly.png

Run from hardware/vial-stirrer-cubxl. Needs pyvista, pillow and requests, and an Onshape key pair
that can read the document (ONSHAPE_ACCESS_KEY, ONSHAPE_SECRET_KEY).
"""

import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import assembly_video as av  # noqa: E402

HL, AMBER = (1.0, 0.47, 0.0), (1.0, 0.72, 0.10)        # what the step adds, and a second kind of part
STEEL, BRASS = (0.74, 0.75, 0.78), (0.80, 0.62, 0.25)
COL = {"base": (0.33, 0.35, 0.39), "holder": (0.10, 0.58, 0.60), "keys": (0.92, 0.92, 0.88),
       "carrier": (0.93, 0.92, 0.88), "mag_n": (0.85, 0.13, 0.13), "mag_s": (0.15, 0.30, 0.85),
       "fan": (0.16, 0.16, 0.18), "ins_fan": BRASS, "mosfet": (0.10, 0.10, 0.10), "mosfet_tab": STEEL,
       "hall": (0.15, 0.15, 0.15), "board": (0.13, 0.42, 0.24), "parts": (0.86, 0.76, 0.56),
       "cable": (0.60, 0.60, 0.62), "washers": STEEL, "screws": STEEL, "mosfet_legs": STEEL}
FP = 16.0                                   # fan screw positions, +-x +-y
Z_FAN0, Z_FAN1, Z_FLANGE = 9.0, 19.5, 20.0  # fan bottom and top, holder flange underside (on 0.5 mm washers)
BOARD = (-21.42, -1.1, -10.0, 10.0, 3.7, 5.3)   # the compact base's board on its rails, where the stop held it
COLS = [BOARD[0] + 1.27 + 2.54 * i for i in range(8)]   # A-H, -X to +X
ROWS = [6.35 - 2.54 * j for j in range(6)]              # 1-6, +Y to -Y


def onshape() -> dict[str, pv.PolyData]:
    parts, cdir = av.onshape_parts()
    out: dict[str, list] = {}
    for p in parts:
        m = pv.read(str(cdir / p["file"]))
        key = av.actor_key(p["name"], np.array(m.center))
        if key in ("ins_fan", "carrier", "mag_n", "mag_s", "fan", "mosfet", "mosfet_tab", "hall", "keys"):
            if key in ("mosfet", "mosfet_tab"):
                # the compact board is 0.5 mm further toward +X, and the legs go into H2-H4, centred on row 3
                m = m.translate((0.5, ROWS[2], 0), inplace=False)
            out.setdefault(key, []).append(m)
    return {k: pv.merge(v) for k, v in out.items()}


def drawn() -> dict[str, pv.PolyData]:
    """The parts drawn here: the board and its parts, the cable, the washers and the screws."""
    x0, x1, y0, y1, z0, zt = BOARD
    d = {"board": pv.Box((x0, x1, y0, y1, z0, zt))}
    flat = []
    for (c0, r0), (c1, r1), rad in (((1, 0), (5, 0), 1.15), ((6, 0), (6, 4), 1.15), ((2, 1), (2, 5), 1.15),
                                    ((5, 2), (5, 5), 1.3)):      # R1, R2, R3, D1, lying flat
        a, b = np.array((COLS[c0], ROWS[r0])), np.array((COLS[c1], ROWS[r1]))
        mid, axis = (a + b) / 2, np.append((b - a) / np.linalg.norm(b - a), 0)
        flat.append(pv.Cylinder(center=(*mid, zt + rad), direction=axis, radius=rad, height=5.6))
    flat.append(pv.Box((COLS[4] - 0.8, COLS[4] + 0.8, ROWS[5] - 0.3, ROWS[4] + 0.3, zt, zt + 1.0)))   # C1, 1206
    d["parts"] = pv.merge(flat)
    # The cable comes in through the -X wall's notch (y -6.5 to 6.5, floor at z 2.6) and its jacket
    # ends at the wall's inner face. The four cores fan out from there, up over the board's -X edge
    # and down into column A: A6 (5V), A5 (GND), A3 (Hall), A1 (PWM).
    r, zj = 0.7, 2.6 + 2.3
    cores = []
    for row, y0 in ((5, -1.2), (4, -0.4), (2, 0.4), (0, 1.2)):
        y = ROWS[row]
        pts = [(-24.0, y0, zj), (-22.9, y0 + 0.35 * (y - y0), zj + 0.3), (-21.9, y, zt + 1.0),
               (COLS[0] - 0.4, y, zt + 1.0), (COLS[0], y, zt + 0.2)]
        cores.append(pv.Spline(np.array(pts), 60).tube(radius=r, n_sides=12, capping=True))
    d["cores"] = cores
    d["cable"] = pv.Spline(np.array([(-23.0, 0.0, zj), (-29.0, 0.0, zj), (-37.0, 0.0, 2.6), (-62.0, 0.0, 2.3)]),
                           40).tube(radius=2.3, n_sides=28, capping=True)
    # The MOSFET's three legs, from its body (the Onshape model's leads stop at x 0) straight into
    # H2, H3 and H4: nothing stands between them now
    legs = []
    for row in (1, 2, 3):
        y = ROWS[row]
        legs.append(pv.Spline(np.array([(0.2, y, 5.05), (-1.2, y, 5.6), (COLS[7] + 0.4, y, 5.75), (COLS[7], y, 5.4),
                                        (COLS[7], y, 4.4)]), 40).tube(radius=0.32, n_sides=10, capping=True))
    d["mosfet_legs"] = pv.merge(legs)
    d["washers"] = pv.merge([pv.Disc(center=(sx * FP, sy * FP, Z_FAN1), inner=1.6, outer=3.5, c_res=48)
                             .extrude((0, 0, 0.5), capping=True) for sx in (-1, 1) for sy in (-1, 1)])
    screws = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            screws.append(pv.Cylinder(center=(sx * FP, sy * FP, 13.0), direction=(0, 0, 1), radius=1.45, height=20.0))
            screws.append(pv.Cylinder(center=(sx * FP, sy * FP, 24.5), direction=(0, 0, 1), radius=2.75, height=3.0))
    d["screws"] = pv.merge(screws)
    return d


CORE_COL = [(0.80, 0.10, 0.10), (0.10, 0.10, 0.10), (0.92, 0.92, 0.92), (0.10, 0.55, 0.20)]   # 5V, GND, Hall, PWM

STEPS = [   # caption, actors shown, actors highlighted (HL, AMBER), lift in mm for actors not yet in place
    ("2. Board on its rails, cable in through the −X notch, MOSFET at +X",
     ["keys", "base", "ins_fan", "board", "parts", "cores", "cable", "mosfet", "mosfet_tab", "mosfet_legs"],
     (["board", "parts", "mosfet", "mosfet_tab", "mosfet_legs"], ["cores", "cable"]), {}),
    ("3. Fan onto its four posts, the carrier already on its hub",
     ["keys", "base", "ins_fan", "board", "parts", "cores", "cable", "mosfet", "mosfet_tab", "mosfet_legs", "fan", "carrier",
      "mag_n", "mag_s"], (["fan"], ["carrier", "mag_n", "mag_s"]), {}),
    ("5–6. A washer on each of the fan's corners, then the holder, its groove over the notch (−X)",
     ["keys", "base", "ins_fan", "board", "parts", "cores", "cable", "mosfet", "mosfet_tab", "mosfet_legs", "fan", "carrier",
      "mag_n", "mag_s", "washers", "holder", "hall"], (["washers"], ["holder", "hall"]), {"holder": 22, "hall": 22}),
    ("7. Four M3 × 20 through the holder, the washers and the fan into the inserts",
     ["keys", "base", "ins_fan", "board", "parts", "cores", "cable", "mosfet", "mosfet_tab", "mosfet_legs", "fan", "carrier",
      "mag_n", "mag_s", "washers", "holder", "hall", "screws"], (["screws"], []), {"screws": 16}),
]


def render(meshes, step, size=(900, 780)) -> Image.Image:
    caption, shown, (hl, amber), lift = step
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("white")
    for key in shown:
        ms = meshes[key] if isinstance(meshes[key], list) else [meshes[key]]
        for i, m in enumerate(ms):
            col = HL if key in hl else AMBER if key in amber else COL.get(key, (0.6, 0.6, 0.6))
            if key == "cores" and key not in hl and key not in amber:
                col = CORE_COL[i]
            m = m.translate((0, 0, lift.get(key, 0)), inplace=False)
            p.add_mesh(m, color=col, smooth_shading=key in ("cores", "cable", "parts", "screws"), specular=0.2,
                       ambient=0.28, diffuse=0.75, opacity=0.35 if key == "base" and "fan" not in shown else 1.0)
    p.camera_position = [(-120, -165, 150), (-2, -4, 16), (0, 0, 1)]
    p.camera.zoom(1.05)
    p.add_axes(line_width=3, labels_off=False, viewport=(0, 0, 0.22, 0.22))
    p.enable_anti_aliasing("ssaa")
    img = Image.fromarray(p.screenshot(return_img=True))
    p.close()
    box = ImageChops.difference(img.convert("RGB"), Image.new("RGB", img.size, "white")).getbbox()
    img = img.crop((max(box[0] - 20, 0), max(box[1] - 20, 0), min(box[2] + 20, img.width), min(box[3] + 20, img.height)))
    return img


def main(out: str) -> None:
    meshes = {**onshape(), **drawn()}
    meshes["base"] = pv.read(str(HERE / "stl" / "compact" / "base_compact.stl"))
    meshes["holder"] = pv.read(str(HERE / "stl" / "compact" / "vial_holder_compact.stl"))
    tiles = [(s[0], render(meshes, s)) for s in STEPS]
    w = max(t.width for _, t in tiles)
    h = max(t.height for _, t in tiles)
    f = ImageFont.truetype(str(av.FONTS / "DejaVuSans-Bold.ttf"), 22)
    pad = 24
    caps = [av.wrap(text, f, w) for text, _ in tiles]
    cap = 30 * max(len(c) for c in caps) + 10
    sheet = Image.new("RGB", (2 * w + 3 * pad, 2 * (h + cap) + 3 * pad), "white")
    d = ImageDraw.Draw(sheet)
    for i, (text, t) in enumerate(tiles):
        x, y = pad + (i % 2) * (w + pad), pad + (i // 2) * (h + cap + pad)
        for k, line in enumerate(caps[i]):
            d.text((x, y + 30 * k), line, fill=(30, 30, 30), font=f)
        sheet.paste(t, (x + (w - t.width) // 2, y + cap + (h - t.height) // 2))
    sheet.save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1])
