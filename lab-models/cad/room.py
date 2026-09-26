"""CB154, roughly: the room shell and what is in it, in compass coordinates.

Frame (the one in sources/cb154_room.json): origin at the inside south-west corner at floor level,
+x east along the long walls (0 -> 9601 mm), +y north (0 -> 7874 mm), +z up. The plan's north arrow
points to the page's left, so on cb154.pdf page-top is east.

Sources, cross-checked in sources/cb154_room.json:
  - BYU Facilities Planning's plan (cb154.pdf, 1" = 25'-0", and the annotated copy: 25.78 x 31.38 ft);
  - Gage's tape-measured sketch in #7 (310 x 378 in), which is used for the size;
  - the #229 render and photos (counters, spot D), #31 (outlets, clean room), and room photos.
Each placement below says how sure it is. The usable ceiling is 103 in (2616 mm) to the ducts.
"""
from __future__ import annotations

import cadquery as cq

from common import Model, box, rbox

W, D, H = 9601.0, 7874.0, 2616.0     # inside, x (E-W) by y (N-S), to the lowest ducts
T = 190.0                            # 8 in concrete block
COUNTER_H = 910.0

# doors: (wall, centre along the wall, width, head height)
DOORS = {
    "entrance": ("W", 4060.0, 1150.0, 2080.0),      # from corridor 101, swings in
    "154-2": ("E", 1340.0, 914.0, 2080.0),          # to room 123
    "154-1": ("N", 4820.0, 1220.0, 2080.0),         # to the neighbouring lab, kept sealed
    "to 154A": ("S", 5525.0, 914.0, 2080.0),        # swings out into 154A
}
WINDOW = ("W", 1350.0, 1200.0, 950.0, 2150.0)       # roll-up steel shutter to corridor 101: sill, top
ROOM_158 = (0.0, 5274.0, 4090.0, D)                 # a separate room cut into the NW corner
PILLAR = (6245.0, 6100.0, 490.0)                    # centre x, y and side (19 in square)
CLEAN_ROOM = (6550.0, 3607.0, W, D, 2743.0)         # hard steel walls, 14 x 10 x 9 ft, NE corner
SPOT_D = (4981.0, 6052.0, 1360.0, 1290.0)           # centre x, y; E-W and N-S size (#229)


def _wall_with_openings(x0, y0, x1, y1, openings, along: str) -> cq.Workplane:
    w = box(x0, y0, 0, x1, y1, H)
    for c, width, z0, z1 in openings:
        a, b = c - width / 2, c + width / 2
        w = w.cut(box(a, y0 - 1, z0, b, y1 + 1, z1) if along == "x" else box(x0 - 1, a, z0, x1 + 1, b, z1))
    return w


def shell() -> Model:
    m = Model("cb154_shell", "CB154 room shell", source="plan + #7 tape measurements")
    m.add("floor", box(-T, -T, -20, W + T, D + T, 0), "floor")
    op = {"W": [], "E": [], "N": [], "S": []}
    for wall, c, width, head in DOORS.values():
        op[wall].append((c, width, 0.0, head))
    wall, c, width, sill, top = WINDOW
    op[wall].append((c, width, sill, top))
    m.add("wall S", _wall_with_openings(-T, -T, W + T, 0, op["S"], "x"), "wall")
    m.add("wall N", _wall_with_openings(-T, D, W + T, D + T, op["N"], "x"), "wall")
    m.add("wall W", _wall_with_openings(-T, 0, 0, D, op["W"], "y"), "wall")
    m.add("wall E", _wall_with_openings(W, 0, W + T, D, op["E"], "y"), "wall")
    x0, y0, x1, y1 = ROOM_158
    m.add("room 158 walls", box(x1 - T, y0, 0, x1, y1, H).union(box(x0, y0, 0, x1, y0 + T, H)), "wall")
    px, py, s = PILLAR
    m.add("pillar", box(px - s / 2, py - s / 2, 0, px + s / 2, py + s / 2, H), "wall")
    m.add("pilaster", box(6233 - 250, 0, 0, 6233 + 250, 320, H), "wall")
    m.add("corner column", box(0, 0, 0, 370, 300, H), "wall")
    for name, (wall, c, width, head) in DOORS.items():       # leaves, shown shut
        a, b = c - width / 2, c + width / 2
        if wall in ("N", "S"):
            yy = -T / 2 if wall == "S" else D + T / 2
            m.add(f"door {name}", box(a, yy - 20, 0, b, yy + 20, head), "door")
        else:
            xx = -T / 2 if wall == "W" else W + T / 2
            m.add(f"door {name}", box(xx - 20, a, 0, xx + 20, b, head), "door")
    wall, c, width, sill, top = WINDOW
    m.add("window shutter", box(-T / 2 - 10, c - width / 2, sill, -T / 2 + 10, c + width / 2, top), "paint_white")
    return m


def clean_room() -> Model:
    """The atomizer's hard-wall enclosure, with strip-curtain doorways on its west and south faces."""
    x0, y0, x1, y1, h = CLEAN_ROOM
    m = Model("atomizer_clean_room", "Atomizer clean room, 14 x 10 x 9 ft, steel walls (#31)", source="#31 / #124 photos")
    t = 60.0
    west = box(x0, y0, 0, x0 + t, y1, h).cut(box(x0 - 1, 4350 - 600, 0, x0 + t + 1, 4350 + 600, 2100))
    south = box(x0, y0, 0, x1, y0 + t, h).cut(box(7300 - 600, y0 - 1, 0, 7300 + 600, y0 + t + 1, 2100))
    m.add("steel walls", west.union(south), "paint_grey")
    m.add("curtain, west doorway", box(x0 + t / 2 - 3, 4350 - 600, 0, x0 + t / 2 + 3, 4350 + 600, 2100), "acrylic")
    m.add("curtain, south doorway", box(7300 - 600, y0 + t / 2 - 3, 0, 7300 + 600, y0 + t / 2 + 3, 2100), "acrylic")
    m.add("roof", box(x0, y0, h - 40, x1, y1, h), "paint_grey")
    return m


def counter(x0, y0, x1, y1, name, top="wood", h=COUNTER_H, wall_hung=True) -> Model:
    m = Model(name, name, source="#229 / #7")
    m.add("top", box(x0, y0, h - 40, x1, y1, h), top)
    if not wall_hung:
        m.add("cabinets", box(x0 + 20, y0 + 20, 0, x1 - 20, y1 - 20, h - 40), "wood")
    return m


def table(cx, cy, w, d, name, h=COUNTER_H, top="wood") -> Model:
    m = Model(name, name, source="assumed")
    x0, y0, x1, y1 = cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2
    m.add("top", box(x0, y0, h - 25, x1, y1, h), top)
    for x in (x0 + 20, x1 - 60):
        for y in (y0 + 20, y1 - 60):
            m.add(f"leg {x:.0f} {y:.0f}", box(x, y, 0, x + 40, y + 40, h - 25), "extrusion")
    return m


def envelope(key: str, title: str, dims, x, y, z=0.0, rz=0.0, material="printer_white") -> Model:
    """A box standing in for vendor geometry that stays out of the repo (OT-2, PiPER)."""
    m = Model(key, title, source="envelope of the vendor STEP")
    m.add(title, rbox(dims[0], dims[1], dims[2], 20.0), material)
    return m.moved(x, y, z, rz)


def cb154(eq: dict[str, Model], vendor_models: dict[str, Model] | None = None) -> Model:
    """The room with what is in it. vendor_models (OT-2) are used when given, otherwise
    envelopes, so the committed STEP holds no vendor geometry."""
    vendor_models = vendor_models or {}
    m = Model("cb154_room", "CB154 with equipment (rough)", source="see room.py and sources/cb154_room.json")
    parts: list[tuple[str, Model]] = [("shell", shell()), ("clean room", clean_room())]
    # SURE (plan, #7 tape, #229): the wall-hung L-counter in the SW corner, 800 deep, top ~910;
    # west leg B under the roll-up window, south leg A with black shelves above it
    parts.append(("counter B (west)", counter(0, 0, 800, 3251, "counter B, west leg")))
    parts.append(("counter A (south)", counter(800, 0, 2781, 800, "counter A, south leg")))
    shelves = Model("shelves", "black shelves over counter A", source="#229 photo")
    shelves.add("shelves", box(300, 0, 1500, 2500, 330, 2150), "printer_black")
    parts.append(("shelves over A", shelves))
    # SURE (Jul-Aug 2026 photos): sink + eyewash casework, SE corner to the pilaster, wood upper over it
    parts.append(("sink casework", counter(6560, 0, W, 745, "sink casework", top="benchtop", wall_hung=False)))
    upper = Model("upper", "upper cabinet over the sink", source="2026-08-19 photo")
    upper.add("cabinet", box(6600, 0, 1450, 7500, 330, 2150), "wood")
    parts.append(("upper cabinet", upper))
    # PLACED (livestream, #229): the OT-2 at the north end of counter B, facing east, the
    # entrance door just north of it
    if "opentrons_ot2" in vendor_models:
        parts.append(("ot2", vendor_models["opentrons_ot2"].moved(330.0, 2790.0, COUNTER_H, 90.0)))
    else:
        parts.append(("ot2", envelope("ot2_env", "OT-2 (envelope)", (624, 567, 662), 330.0, 2790.0, COUNTER_H, 90.0)))
    # PLACED (moved in 2026-09-22): the CubXL on counter A, facing north, controller to its east
    parts.append(("cubxl", eq["cubxl"].moved(1900.0, 420.0, COUNTER_H, 180.0)))
    # PLACED (#229): spot D, the PiPER tables against room 158's east wall; the arm is planned
    cx, cy, w, d = SPOT_D
    parts.append(("spot D", table(cx, cy, w, d, "spot D tables")))
    if "agilex_piper" in vendor_models:
        parts.append(("piper", vendor_models["agilex_piper"].moved(cx, cy, COUNTER_H, 0.0)))
    else:
        parts.append(("piper", envelope("piper_env", "PiPER (envelope)", (145, 550, 466), cx, cy + 180.0, COUNTER_H)))
    # APPROXIMATE (+-500, #229 render and Feb photos): island E, mobile black-top benches
    parts.append(("island", counter(3050 - 750, 3900 - 750, 3050 + 750, 3900 + 750, "island E", top="benchtop",
                                    wall_hung=False)))
    # GUESS: the atomizer is still crated; AMAZEMET places it on install day (2026-09-28)
    parts.append(("atomizer", eq["amazemet_repowder"].moved(8700.0, D - 520.0, 0.0, 0.0)))
    # LOW CONFIDENCE (photos): gray storage cabinet by 158's SE corner, whiteboard on the south wall,
    # the transformer north of the pillar (size assumed)
    cab = Model("cabinet", "gray storage cabinet", source="Feb photos")
    cab.add("cabinet", box(3850 - 450, 5050 - 225, 0, 3850 + 450, 5050 + 225, 1980), "paint_grey")
    parts.append(("gray cabinet", cab))
    wb = Model("whiteboard", "whiteboard", source="photos")
    wb.add("board", box(2900, 0, 900, 4500, 20, 2100), "paint_white")
    parts.append(("whiteboard", wb))
    tr = Model("transformer", "transformer", source="#229 description, size assumed")
    tr.add("transformer", box(6000 - 350, 7450 - 275, 0, 6000 + 350, 7450 + 275, 900), "paint_grey")
    parts.append(("transformer", tr))
    # not in CB154: the drop tower (tensegrity, another lab), the printers, and the glove box (not bought yet)
    for label, model in parts:
        for p in model.parts:
            m.add(f"{label} - {p.name}", p.shape, p.material)
    m.notes = {"room_inside_mm": [W, D, H], "frame": "origin inside SW corner, +x east, +y north"}
    return m


LABELS = {
    "atomizer (crated; spot TBD)": (8700.0, D - 520.0, 1750.0), "clean room": (7300.0, 3700.0, 2900.0),
    "OT-2": (330.0, 2790.0, 1650.0), "CubXL": (1900.0, 420.0, 1500.0), "counter B": (400.0, 1400.0, 1000.0),
    "spot D: PiPER sandbox": (SPOT_D[0], SPOT_D[1], 1500.0), "island E": (3050.0, 3900.0, 1100.0),
    "room 158": (2000.0, 6600.0, 2800.0), "pillar": (6245.0, 6100.0, 2800.0), "sink": (8080.0, 372.0, 1200.0),
    "entrance": (0.0, 4060.0, 2300.0), "154-2": (W, 1340.0, 2300.0), "154-1": (4820.0, D, 2300.0),
    "to 154A": (5525.0, 0.0, 2300.0), "window": (0.0, 1350.0, 2300.0),
}


def render_room(model: Model) -> None:
    """Cutaway renders: no ceiling, and the near walls dropped for the 3D view."""
    import numpy as np

    from common import MATERIALS, RENDERS
    from render import caption, plotter, to_mesh

    def draw(pl, hide=()):
        for p in model.parts:
            if any(h in p.name for h in hide):
                continue
            mesh = to_mesh(p.shape, 3.0)
            if mesh.n_points == 0:
                continue
            r, g, b, a, spec = MATERIALS[p.material]
            pl.add_mesh(mesh, color=(r, g, b), opacity=a, specular=spec, smooth_shading=True, split_sharp_edges=True)

    views = {
        "cb154_iso": (("wall S", "wall W", "door entrance", "door to 154A", "window shutter", "shelves",
                       "whiteboard", "clean room - roof"), (-0.8, -1.0, 1.25), (0, 0, 1), 1.3,
                      "CB154, rough model (cutaway from the south-west corner)"),
        "cb154_top": (("clean room - roof",), (0, 0, 1), (0, 1, 0), 1.15, "CB154 from above (north up)"),
    }
    for name, (hide, direction, up, zoom, title) in views.items():
        pl = plotter((1800, 1400))
        draw(pl, hide)
        pl.add_point_labels(np.array(list(LABELS.values())), list(LABELS), font_size=18, point_size=1,
                            shape_opacity=0.75, shape_color="white", text_color="black", always_visible=True,
                            show_points=False, margin=4)
        c = np.array([W / 2, D / 2, 600.0])
        d = np.array(direction, float)
        d /= np.linalg.norm(d)
        pl.camera_position = [tuple(c + d * 20000), tuple(c), up]
        pl.camera.view_angle = 30
        if name == "cb154_top":
            pl.enable_parallel_projection()
        pl.reset_camera(bounds=(-200, W + 200, -200, D + 200, 0, H))
        pl.camera.zoom(zoom)
        pl.enable_ssao(radius=300, bias=5, kernel_size=64)
        pl.enable_anti_aliasing("ssaa")
        out = RENDERS / f"{name}.png"
        pl.screenshot(str(out))
        pl.close()
        caption(out, title, "Shell: BYU's plan + Gage's tape (#7). Contents: #229, #31, photos. "
                            "Atomizer spot is a guess (install 2026-09-28)")
