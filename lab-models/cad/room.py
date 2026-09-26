"""CB154, roughly: the room shell from BYU Facilities Planning's plan (cb154.pdf and the
annotated copy, 1" = 25'-0"), with the equipment placed where the lab's photos and threads put it.

Frame: the plan as printed (north is to the page's left). x runs left to right across the page,
y runs up the page, both from the inside corner at the page's bottom left; z is up from the floor.
Room 154 is 25.78 x 31.38 ft (7.858 x 9.565 m) inside, as dimensioned on the annotated plan. Door,
pillar and inner-room positions were read off the plan at ~27.7 mm/px and are good to +-0.1 m.
The usable ceiling is ~103 in (2.62 m, #7). Placements marked PLACED below are where the
equipment is (photos or threads); GUESS marks a plausible spot that nobody has confirmed.
"""
from __future__ import annotations

import cadquery as cq

from common import Model, box, cyl, rbox

W, D, H = 7858.0, 9565.0, 2620.0     # room 154, inside
T = 150.0                            # wall thickness (assumed)

# (wall, start, end) of each opening, mm along the wall from the page-left / page-bottom corner
DOORS = {
    "entrance": ("bottom", 3000.0, 4180.0),    # 3.86 ft leaf, swings in
    "154-1": ("left", 4950.0, 5850.0),         # locked (#229)
    "154-2": ("top", 6000.0, 6950.0),
    "to 154A": ("right", 5100.0, 6000.0),
}
PILLAR = (1490.0, 6060.0, 1950.0, 6520.0)      # x0, y0, x1, y1
ROOM_158 = (0.0, 0.0, 2600.0, 4100.0)          # 8.53 ft wide, in the page-bottom-left corner
CLEAN_ROOM = (0.0, D - 3140.0, 4270.0, D)      # atomizer clean room, 14 x 10.29 ft from the top-left corner (#31)
SPOT_D = (1250.0, 4370.0, 2540.0, 5730.0)      # 1.29 x 1.36 m, arm centred (#229)
SPOT_E = (3330.0, 2530.0, 4690.0, 3820.0)      # 1.36 x 1.29 m (#229)
BENCH_H = 900.0


def _wall(x0, y0, x1, y1, openings=(), axis="x") -> cq.Workplane:
    w = box(x0, y0, 0, x1, y1, H)
    for a, b, top in openings:
        if axis == "x":
            w = w.cut(box(a, y0 - 1, 0, b, y1 + 1, top))
        else:
            w = w.cut(box(x0 - 1, a, 0, x1 + 1, b, top))
    return w


def shell() -> Model:
    m = Model("cb154_shell", "CB154 room shell", source="BYU Facilities Planning plan (cb154.pdf)")
    m.add("floor", box(-T, -T, -20, W + T, D + T, 0), "floor")
    op = {k: [] for k in ("bottom", "top", "left", "right")}
    for wall, a, b in DOORS.values():
        op[wall].append((a, b, 2100.0))
    m.add("wall bottom", _wall(-T, -T, W + T, 0, op["bottom"], "x"), "wall")
    m.add("wall top", _wall(-T, D, W + T, D + T, op["top"], "x"), "wall")
    m.add("wall left", _wall(-T, 0, 0, D, op["left"], "y"), "wall")
    m.add("wall right", _wall(W, 0, W + T, D, op["right"], "y"), "wall")
    x0, y0, x1, y1 = ROOM_158
    m.add("room 158 walls", box(x1, y0, 0, x1 + T, y1 + T, H).union(box(x0, y1, 0, x1 + T, y1 + T, H)), "wall")
    x0, y0, x1, y1 = PILLAR
    m.add("pillar", box(x0, y0, 0, x1, y1, H), "wall")
    for name, (wall, a, b) in DOORS.items():       # door leaves, shown shut
        if wall in ("bottom", "top"):
            yy = -T / 2 if wall == "bottom" else D + T / 2
            m.add(f"door {name}", box(a, yy - 20, 0, b, yy + 20, 2100), "door")
        else:
            xx = -T / 2 if wall == "left" else W + T / 2
            m.add(f"door {name}", box(xx - 20, a, 0, xx + 20, b, 2100), "door")
    return m


def clean_room() -> Model:
    """The atomizer's softwall enclosure (#31): a frame with curtain walls, open at the front."""
    x0, y0, x1, y1 = CLEAN_ROOM
    m = Model("atomizer_clean_room", "Atomizer clean-room enclosure, 14 x 10 ft (#31)", source="#31 / #229 plan position")
    hh = 2400.0
    frame = []
    for x in (x0 + 30, x1 - 30):
        for y in (y0 + 30, y1 - 30):
            frame.append(box(x - 25, y - 25, 0, x + 25, y + 25, hh))
    frame.append(box(x0, y0, hh - 50, x1, y0 + 50, hh))
    frame.append(box(x1 - 50, y0, hh - 50, x1, y1, hh))
    m.add("frame", cq.Workplane("XY").add(cq.Compound.makeCompound([f.val() for f in frame])), "extrusion")
    m.add("curtain front", box(x0 + 60, y0, 300, x1 - 900, y0 + 6, hh - 50), "acrylic")
    m.add("curtain right", box(x1 - 6, y0 + 60, 300, x1, y1 - 60, hh - 50), "acrylic")
    return m


def bench(x0, y0, x1, y1, name="bench", h=BENCH_H) -> Model:
    m = Model(name, name, source="assumed")
    m.add("top", box(x0, y0, h - 30, x1, y1, h), "benchtop")
    m.add("base cabinets", box(x0 + 20, y0 + 40, 0, x1 - 20, y1 - 20, h - 30), "wood")
    return m


def table(x0, y0, x1, y1, name="table", h=BENCH_H) -> Model:
    m = Model(name, name, source="assumed")
    m.add("top", box(x0, y0, h - 25, x1, y1, h), "wood")
    for x in (x0 + 30, x1 - 70):
        for y in (y0 + 30, y1 - 70):
            m.add(f"leg {x:.0f} {y:.0f}", box(x, y, 0, x + 40, y + 40, h - 25), "extrusion")
    return m


def _window(x0: float, x1: float) -> Model:
    """The pass-through window in the top wall, its roll-down shutter shut."""
    m = Model("window", "pass-through window", source="#7 photos")
    m.add("shutter", box(x0, D - 5.0, 1000.0, x1, D, 1900.0), "paint_white")
    m.add("coil hood", box(x0 - 40, D - 160.0, 1900.0, x1 + 40, D, 2080.0), "paint_white")
    return m


def island(x0, y0, x1, y1, h=BENCH_H) -> Model:
    m = Model("island", "black epoxy island", source="#7 photos")
    m.add("top", box(x0, y0, h - 25, x1, y1, h), "benchtop")
    m.add("cabinets", box(x0 + 30, y0 + 30, 0, x1 - 30, y1 - 30, h - 25), "wood")
    return m


def glovebox() -> Model:
    """A benchtop glove box (the doser's Shadow box, #30), about 900 x 600 x 650 mm (assumed)."""
    m = Model("glovebox", "glove box", source="assumed")
    shell = rbox(900.0, 600.0, 650.0, 20.0).faces(">Z").shell(-8.0)
    for x in (-200.0, 200.0):
        shell = shell.cut(cq.Workplane("XZ").circle(100.0).extrude(-30).translate((x, -300.0 - 5, 330.0)))
    m.add("box", shell, "acrylic")
    m.add("base", rbox(920.0, 620.0, 40.0, 20.0, z=-5.0), "printer_grey")
    for x in (-200.0, 200.0):
        m.add(f"glove port {x:+.0f}", cq.Workplane("XZ").circle(110.0).circle(95.0).extrude(40.0).translate((x, -300.0 + 10, 330.0)), "printer_black")
    return m


def envelope(key: str, title: str, dims, x, y, z=0.0, rz=0.0, material="printer_white") -> Model:
    """A labelled box standing in for vendor geometry that stays out of the repo (OT-2, PiPER)."""
    m = Model(key, title, source="envelope of the vendor STEP")
    m.add(title, rbox(dims[0], dims[1], dims[2], 20.0), material)
    return m.moved(x, y, z, rz)


def cb154(eq: dict[str, Model], vendor_models: dict[str, Model] | None = None) -> Model:
    """The room with its equipment. vendor_models (OT-2, PiPER) are used when given, otherwise
    envelopes, so the committed STEP holds no vendor geometry."""
    m = Model("cb154_room", "CB154 with equipment (rough)", source="plan + photos; see room.py")
    parts: list[tuple[str, Model]] = [("shell", shell()), ("clean room", clean_room())]
    # PLACED: the atomizer stands against a painted cinderblock wall inside its softwall clean room
    # in the page-top-left corner (#31, #124, the 2026-09-03 "Placing the Atomizer" short).
    parts.append(("atomizer", eq["amazemet_repowder"].moved(2100.0, D - 480.0, 0.0, 0.0)))
    # PLACED: a wood-grain counter runs along the top wall under the pass-through window, and the
    # OT-2 sits at its right end with door 154-2 immediately to its right and cinderblock behind it
    # (#7 photos; the OT-2 livestream after the 2026-09-10 move).
    parts.append(("counter top wall", bench(4400.0, D - 760.0, 5990.0, D, "counter, top wall")))
    parts.append(("pass-through window", _window(4600.0, 5500.0)))
    if vendor_models and "opentrons_ot2" in vendor_models:
        parts.append(("ot2", vendor_models["opentrons_ot2"].moved(5640.0, D - 330.0, BENCH_H, 180.0)))
    else:
        parts.append(("ot2", envelope("ot2_env", "OT-2 (envelope)", (624, 567, 662), 5640.0, D - 330.0, BENCH_H, 180.0)))
    # GUESS: the CubXL on the same counter, left of the OT-2 (it moved into CB154, #133; the photo
    # shows a dark wood bench like this one)
    parts.append(("cubxl", eq["cubxl"].moved(4800.0, D - 400.0, BENCH_H, 180.0)))
    # PLACED (position approximate): the black epoxy island with the glove box on it (#7 photos,
    # the 2026-08-26 multi-doser pitch)
    parts.append(("island", island(2950.0, 3900.0, 4150.0, 6250.0)))
    parts.append(("glovebox", glovebox().moved(3550.0, 5050.0, BENCH_H, 90.0)))
    # spot D: the PiPER sandbox table (#229)
    x0, y0, x1, y1 = SPOT_D
    parts.append(("spot D table", table(x0, y0, x1, y1, "spot D table")))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if vendor_models and "agilex_piper" in vendor_models:
        parts.append(("piper", vendor_models["agilex_piper"].moved(cx, cy, BENCH_H, 0.0)))
    else:
        parts.append(("piper", envelope("piper_env", "PiPER (envelope)", (145, 550, 466), cx, cy + 180.0, BENCH_H)))
    # GUESS: white tables along the right wall (#7 photos show them with blue bins), printers on them
    parts.append(("bench right", table(W - 760.0, 700.0, W, 4900.0, "tables, right wall")))
    parts.append(("h2d", eq["bambu_h2d"].moved(W - 380.0, 1400.0, BENCH_H, -90.0)))
    parts.append(("a1 mini", eq["bambu_a1_mini"].moved(W - 380.0, 2200.0, BENCH_H, -90.0)))
    # the drop tower is used by the tensegrity project in another lab (#27, #28): modelled, not placed
    for label, model in parts:
        for p in model.parts:
            m.add(f"{label} - {p.name}", p.shape, p.material)
    m.notes = {"room_inside_mm": [W, D, H], "north": "page left (-x)"}
    return m


def render_room(model: Model) -> None:
    """Cutaway renders: the ceiling is open and the near walls are dropped for the views."""
    import numpy as np
    import pyvista as pv

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
        "cb154_iso": (("wall bottom", "wall right", "door entrance", "door to 154A"), (0.8, -1.0, 1.25), 1.3,
                      "CB154, rough model (cutaway from the entrance corner)"),
        "cb154_top": ((), (0, 0, 1), 1.15, "CB154 from above (north is to the left)"),
    }
    labels = {                                  # where each thing is, for the captions on the renders
        "atomizer (clean room)": (2100.0, D - 700.0, 1700.0), "OT-2": (5640.0, D - 330.0, 1650.0),
        "CubXL": (4800.0, D - 400.0, 1500.0), "island + glove box": (3550.0, 5050.0, 1650.0),
        "spot D: PiPER sandbox": ((SPOT_D[0] + SPOT_D[2]) / 2, (SPOT_D[1] + SPOT_D[3]) / 2, 1500.0),
        "H2D": (W - 380.0, 1400.0, 1650.0), "A1 mini": (W - 380.0, 2200.0, 1400.0),
        "room 158": (1300.0, 2000.0, 2800.0), "pillar": (1720.0, 6290.0, 2800.0),
        "entrance": (3590.0, 0.0, 2300.0), "154-2": (6475.0, D, 2300.0),
    }
    for name, (hide, direction, zoom, title) in views.items():
        pl = plotter((1800, 1400))
        draw(pl, hide)
        pl.add_point_labels(np.array(list(labels.values())), list(labels), font_size=18, point_size=1,
                            shape_opacity=0.75, shape_color="white", text_color="black", always_visible=True,
                            show_points=False, margin=4)
        c = np.array([W / 2, D / 2, 600.0])
        d = np.array(direction, float)
        d /= np.linalg.norm(d)
        pl.camera_position = [tuple(c + d * 20000), tuple(c), (0, 1, 0) if name == "cb154_top" else (0, 0, 1)]
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
        caption(out, title, "Shell from BYU Facilities' plan; equipment from photos and threads, positions partly guessed "
                            "(see lab-models/README.md)")
