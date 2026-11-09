#!/usr/bin/env python3
"""The compact base before and after the 2026-11-04 change: img/compact_base_20261104.png.

The change, asked for by @benwhitney5463 on PR #269: no board stop, and the cable notch moved from
the -Y wall to the wall on its right when the base lies on its side with the old notch on top,
which is the -X wall. The top row draws the base that way, on its side and looking into it; the
bottom row from above the -X/-Y corner. Left is the base printed on 2026-10-28 and 2026-10-30
(stl/compact/base_compact.stl at commit b9f57f5, read with git), right is today's STL. Orange marks
the stop and the notch.

    xvfb-run -a python compact/render_base_change.py img/compact_base_20261104.png

Run from hardware/vial-stirrer-cubxl. Needs pyvista and pillow, and git for the earlier STL.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib
import numpy as np
import pyvista as pv
from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent.parent
PRINTED = "b9f57f5"                         # the commit the 10-28 and 10-30 prints were sliced from
GREY, HL, GROUND = (0.62, 0.64, 0.68), (1.0, 0.47, 0.0), (0.90, 0.90, 0.90)
FONT = Path(matplotlib.get_data_path()) / "fonts" / "ttf"     # DejaVu Sans, shipped with matplotlib

# The features, as boxes in the base's own frame (compact/build_compact.py): x0, x1, y0, y1, z0, z1
STOP = (-1.1, 0.1, -5.0, 5.0, 3.19, 6.2)
NOTCH_OLD = (-11.0, -3.0, -22.0, -19.9, 2.6, 19.0)      # -Y wall, x -11 to -3
NOTCH_NEW = (-24.5, -22.4, -6.5, 6.5, 2.6, 19.0)        # -X wall, y -6.5 to 6.5
# On its side, old notch on top, looking into the open side: base -Y -> up, base +Z -> toward the
# viewer (world -Y), so base -X -> the viewer's right (world +X).
ON_SIDE = np.array([[-1, 0, 0, 0], [0, 0, -1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], dtype=float)


def printed_base() -> pv.PolyData:
    data = subprocess.run(["git", "show", f"{PRINTED}:hardware/vial-stirrer-cubxl/stl/compact/base_compact.stl"],
                          cwd=HERE, check=True, capture_output=True).stdout
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        f.write(data)
    return pv.read(f.name)


def split(mesh: pv.PolyData, boxes) -> tuple[pv.PolyData, pv.PolyData]:
    """The mesh's faces that lie wholly inside any of the boxes (grown by 0.02 mm), and the rest."""
    pts = mesh.points
    faces = mesh.faces.reshape(-1, 4)[:, 1:]
    inside = np.zeros(len(faces), bool)
    for x0, x1, y0, y1, z0, z1 in boxes:
        e = 0.02
        ok = ((pts[:, 0] > x0 - e) & (pts[:, 0] < x1 + e) & (pts[:, 1] > y0 - e) & (pts[:, 1] < y1 + e)
              & (pts[:, 2] > z0 - e) & (pts[:, 2] < z1 + e))
        inside |= ok[faces].all(axis=1)
    return mesh.extract_cells(np.where(inside)[0]).extract_surface(), mesh.extract_cells(np.where(~inside)[0]).extract_surface()


def outline(box, on_side: bool) -> pv.PolyData:
    x0, x1, y0, y1, z0, z1 = box
    m = pv.Box((x0, x1, y0, y1, z0, z1)).extract_all_edges()
    return m.transform(ON_SIDE, inplace=False) if on_side else m


def render(base: pv.PolyData, marks, ghost, on_side: bool, size=(900, 760)) -> Image.Image:
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("white")
    hl, rest = split(base, marks)
    for m, col in ((rest, GREY), (hl, HL)):
        if m.n_cells:
            m = m.transform(ON_SIDE, inplace=False) if on_side else m
            p.add_mesh(m, color=col, smooth_shading=False, specular=0.15, ambient=0.3, diffuse=0.7)
    for box in ghost:      # what is no longer there: its outline, as an orange wire frame
        p.add_mesh(outline(box, on_side), color=HL, line_width=3, opacity=0.9)
    if on_side:
        p.add_mesh(pv.Plane(center=(0, -6, -22.05), direction=(0, 0, 1), i_size=76, j_size=44), color=GROUND,
                   ambient=0.6, diffuse=0.4)     # the bench, under the +Y wall
        p.camera_position = [(-45, -190, 55), (0, -9.5, 0), (0, 0, 1)]
        p.camera.zoom(1.25)
    else:
        p.camera_position = [(-120, -165, 150), (-2, -2, 8), (0, 0, 1)]
        p.camera.zoom(1.2)
    p.enable_anti_aliasing("ssaa")
    img = Image.fromarray(p.screenshot(return_img=True))
    p.close()
    box = ImageChops.difference(img.convert("RGB"), Image.new("RGB", img.size, "white")).getbbox()
    return img.crop((max(box[0] - 25, 0), max(box[1] - 25, 0), min(box[2] + 25, img.width), min(box[3] + 25, img.height)))


def main(out: str) -> None:
    old = printed_base()
    new = pv.read(str(HERE / "stl" / "compact" / "base_compact.stl"))
    tiles = [
        [("Printed 10-28 and 10-30: on its side, notch on top", render(old, [STOP, NOTCH_OLD], [], True)),
         ("New, 11-04: no stop, notch in the wall on the right", render(new, [NOTCH_NEW], [STOP], True))],
        [("Printed: the stop, and the notch in −Y", render(old, [STOP, NOTCH_OLD], [], False)),
         ("New: the notch in −X; the stop (outline) is gone", render(new, [NOTCH_NEW], [STOP], False))],
    ]
    w = max(t.width for row in tiles for _, t in row)
    h = [max(t.height for _, t in row) for row in tiles]
    f = ImageFont.truetype(str(FONT / "DejaVuSans-Bold.ttf"), 26)
    small = ImageFont.truetype(str(FONT / "DejaVuSans.ttf"), 21)
    pad, cap = 28, 44
    sheet = Image.new("RGB", (2 * w + 3 * pad, sum(h) + 2 * cap + 3 * pad + 64), "white")
    d = ImageDraw.Draw(sheet)
    y = pad
    for r, row in enumerate(tiles):
        for c, (text, t) in enumerate(row):
            x = pad + c * (w + pad)
            d.text((x, y), text, fill=(30, 30, 30), font=f)
            sheet.paste(t, (x + (w - t.width) // 2, y + cap + (h[r] - t.height) // 2))
        y += cap + h[r] + pad
    for k, line in enumerate(("Compact base, 49 × 44 × 19 mm. Orange: the board stop and the cable notch. Top row: lying on "
                              "its +Y wall with the open side toward you,",
                              "so the old notch is on top and the −X wall is on the right. Bottom row: from above the "
                              "−X/−Y corner. compact/render_base_change.py")):
        d.text((pad, y - 10 + 28 * k), line, fill=(70, 70, 70), font=small)
    sheet.save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1])
