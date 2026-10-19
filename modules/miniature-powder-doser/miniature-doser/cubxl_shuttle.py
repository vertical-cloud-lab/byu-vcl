"""Ben's CubXL idea (PR 274, 2026-10-16): the miniature doser lives in the back right corner of the deck and rides with
the gantry in Y, held to it by electromagnets, dosing into one row of vials while staying behind the tools.

A concept sketch, not a design. The doser is the one-servo variant (doser_cad.tilt_meshes), mirrored so its servo faces
the middle of the deck. It hangs from a shuttle on its own short rail, and a steel tab on the gantry's right upright
tows it through two electromagnets. The deck is Cubware's PandaDeck.step. Everything else about the CubXL (frame,
gantry, head, tools) is a box-and-cylinder stand-in sized from Ben's photo, SainSmart's PROVerXL 4030 travel and the
gantry config, so its positions are estimates to within a few cm.

Needs what module_views.py needs (its docstring has the checkout and install commands), and the deck:
    gh api "repos/Ursa-Laboratories/Cubware/contents/cubxl_plus/deck/polycarbonate_deck/PandaDeck.step?ref=352aa95" \
        -H "Accept: application/vnd.github.raw" > /tmp/PandaDeck.step
    POWDER_DOSER=/tmp/powder-doser/cad/text-to-cad PANDA_DECK=/tmp/PandaDeck.step \
        xvfb-run -a -s "-screen 0 1920x1080x24" python cubxl_shuttle.py
Writes cubxl_shuttle_views.png and cubxl_shuttle.gif next to this file. Without PANDA_DECK it draws a plain plate.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw

from module_views import D, HERE, INK, MUTED, font

# Machine frame for this sketch: x to the right, y to the back, z up, origin at the deck plate's front-left top corner.
# CubOS's frame (deck_origin) is the capper's position, homed to the back right (+x, +y, +z, $23=0).
DECK_STEP = Path(os.environ.get("PANDA_DECK", "/tmp/PandaDeck.step"))
DECK = (480.0, 490.0, 10.0)                             # PandaDeck.step's plate
TRAVEL = (388.0, 233.665)                               # working_volume x, y (cub_xl_ben_pipette_capper.yaml)
REACH0 = np.array([46.0, 100.0])                        # CubOS (0, 0) on the plate: assumed (centred in x)
PIPETTE = np.array([54.0, 12.999])                      # the pipette's offset from the capper
TOOL_AHEAD = 110.0                                      # assumed: the capper's axis in front of the beam's centre
BEAM = (60.0, 200.0, 290.0)                             # depth, underside, top: assumed
UPRIGHT_X = ((-35.0, -15.0), (495.0, 515.0))            # the gantry's sides, on the rails of the two Y beams
Y_BEAMS = ((-45.0, -5.0), (485.0, 525.0))
VIAL = (28.0, 57.0, 18.0, 33.0)                         # 20 mL VOA: diameter, height, bottom above the plate, row pitch

# The doser, on the shuttle. Its capillary points forwards (-y), its body trails behind, its servo faces the deck.
TIP_GAP = 5.0                                           # the tip, at level, behind the beam's front face
LANE_X = 395.0                                          # the auger's axis, so the row of vials, in x
RIM_GAP = 5.0                                           # the tip above the vial rims while dosing
SHUTTLE_X = (455.0, 463.0)                              # the shuttle's upright plate
RAIL_X, RAIL_Z = (477.0, 485.0), (12.0, 24.0)           # a 12 mm miniature rail on the right Y beam's inner face
MAGNET_R, MAGNET_L = 12.5, 20.0                         # Adafruit 3873 (P25/20): 25 x 20 mm, 5 kg rated, 5 V 0.3 A

STEEL, ALU, BLUE, BLACK = (0.36, 0.37, 0.40), (0.80, 0.82, 0.85), (0.16, 0.33, 0.72), (0.10, 0.10, 0.11)
MAGNET_ON, MAGNET_OFF, GLASS = (0.86, 0.18, 0.16), (0.45, 0.42, 0.42), (0.70, 0.82, 0.90)
REACH_C, LANE_C, BOTH_C = (0.25, 0.50, 0.90), (0.95, 0.55, 0.15), (0.45, 0.70, 0.30)


def box(x, y, z):
    return pv.Box((x[0], x[1], y[0], y[1], z[0], z[1]))


def cyl(c, d, r, h, res=40):
    return pv.Cylinder(center=c, direction=d, radius=r, height=h, resolution=res)


def deck():
    """PandaDeck.step, tessellated (cached beside the doser's meshes), or a plain plate if the STEP isn't there."""
    if not DECK_STEP.exists():
        return box((0, DECK[0]), (0, DECK[1]), (-DECK[2], 0))
    cache = D.CACHE / "panda_deck.vtp"
    if not cache.exists():
        from OCP.STEPControl import STEPControl_Reader
        r = STEPControl_Reader()
        r.ReadFile(str(DECK_STEP))
        r.TransferRoots()
        p, t = D._tess(r.OneShape(), tol=0.3)
        D.CACHE.mkdir(exist_ok=True)
        D._poly(p, t).save(cache)
    return pv.read(cache).translate((0.0, DECK[1], -DECK[2]), inplace=False)   # the STEP spans y -490..0, z 0..10


def gantry_y(ty):
    """The beam's centre for a capper y in CubOS's frame."""
    return REACH0[1] + ty + TOOL_AHEAD


def doser_pose(by, deg):
    """The doser's meshes at tilt `deg`, coupled to a beam at y = by, and the machine position of its hinge."""
    hinge = np.array([LANE_X, by - BEAM[0] / 2 + TIP_GAP + (D.HINGE[1] - D.NOSE_TIP[1]), HINGE_Z])
    out = {}
    for k, m in D.tilt_meshes(deg).items():
        m = D._mirror_x(m.triangulate())
        out[k] = m.translate(hinge - D.HINGE * np.array([-1.0, 1.0, 1.0]), inplace=False)
    return out, hinge


def _hinge_z():
    """Set the hinge's height. The body trails over the row, so parked (and level) nothing may come lower than 2 mm
    over the rims; at 35 deg the tip is RIM_GAP over the rims, and only the vial being dosed may be under the tip."""
    rim = VIAL[2] + VIAL[1]
    c, s = np.radians(D.TILT_DISPENSE), D.HINGE[1] - D.NOSE_TIP[1]
    tip = D.HINGE + np.array([0.0, -s * np.cos(c), -s * np.sin(c)])
    row = VIAL[0] / 2 + 2.0                             # half the width of the row of vials, with 2 mm to spare
    low = lambda deg, y0: min(m.clip_box((-row, row, y0, 1e3, -1e3, 1e3), invert=False).points[:, 2].min(initial=1e3)
                              for m in D.tilt_meshes(deg).values())
    need = [rim + RIM_GAP - tip[2], rim + 2.0 - low(D.TILT_DISPENSE, tip[1] + VIAL[0] / 2 + 2.0)]
    need += [rim + 2.0 - low(deg, -1e3) for deg in (D.TILT_PARK, D.TILT_LEVEL)]
    return D.HINGE[2] + max(need)


HINGE_Z = _hinge_z()


def scene(ty=TRAVEL[1], tx=150.0, deg=D.TILT_PARK, coupled=True, doser_ty=None, fade=()):
    """[(mesh, colour, specular, opacity)]: the CubXL stand-in with the capper at CubOS (tx, ty) and the doser at tilt
    `deg`. doser_ty: where the doser was left, if it isn't coupled (default: with the gantry). fade: groups to draw
    see-through ("right": the right Y beam and upright; "gantry": the beam and the head; "shuttle")."""
    items = []
    group = [""]
    add = lambda m, c, s=0.3, o=1.0: items.append((m, c, s, 0.22 if group[0] in fade else o))
    by = gantry_y(ty)
    # the frame: the deck, two Y beams with their rails, the front and back members, blue corner plates
    add(deck(), (0.86, 0.90, 0.94), 0.5, 0.55)
    for i, (x0, x1) in enumerate(Y_BEAMS):
        group[0] = "right" if i else ""
        add(box((x0, x1), (-40, 530), (-50, 40)), ALU)
        add(box((x0 + 14, x1 - 14), (-40, 530), (40, 52)), STEEL)
        for y0 in (-50, 530):
            add(box((x0 - 5, x1 + 5), (y0, y0 + 10), (-55, 70)), BLUE)
    group[0] = ""
    for y0 in (-40, 490):
        add(box((-5, 485), (y0, y0 + 40), (-50, -10)), ALU)
    # the gantry: its two sides, the beam, the X carriage, the Z axis, the backboard and the two tools
    for i, (x0, x1) in enumerate(UPRIGHT_X):
        group[0] = "right" if i else "gantry"
        add(box((x0, x1), (by - 55, by + 55), (52, BEAM[2])), ALU)
    group[0] = "gantry"
    add(box((-35, 515), (by - BEAM[0] / 2, by + BEAM[0] / 2), BEAM[1:]), ALU)
    cx = REACH0[0] + tx
    cy = by - TOOL_AHEAD                                # the head and tools: still the "gantry" group
    add(box((cx - 50, cx + 50), (by - 42, by - 30), (185, 300)), ALU)
    add(box((cx - 35, cx + 35), (by - 80, by - 42), (120, 320)), (0.25, 0.26, 0.29))
    add(box((cx - 115, cx + 105), (by - 88, by - 80), (95, 255)), BLACK, 0.1)
    add(cyl((cx, cy, 140), (0, 0, 1), 24, 70), BLACK, 0.2)                      # capper
    px, py = cx + PIPETTE[0], cy + PIPETTE[1]
    add(box((px - 18, px + 18), (py - 15, by - 88), (150, 290)), (0.88, 0.88, 0.86))   # pipette body
    add(cyl((px, py, 135), (0, 0, 1), 6, 30), (0.88, 0.88, 0.86))
    add(pv.Cone(center=(px, py, 112), direction=(0, 0, -1), height=16, radius=3.5, resolution=24), (0.92, 0.92, 0.9))
    # the row of vials, in a strip holder
    group[0] = ""
    rows = lane_rows()
    add(box((LANE_X - 20, LANE_X + 20), (rows[0] - 22, rows[-1] + 22), (0, VIAL[2])), (0.93, 0.93, 0.95), 0.2)
    for y in rows:
        add(cyl((LANE_X, y, VIAL[2] + VIAL[1] / 2), (0, 0, 1), VIAL[0] / 2, VIAL[1]), GLASS, 0.6, 0.45)
    # the doser and its shuttle
    dby = by if doser_ty is None else gantry_y(doser_ty)
    meshes, hinge = doser_pose(dby, deg)
    for (_, mat), m in meshes.items():
        color, spec = D.MATERIALS[mat]
        add(m, color, spec)
    group[0] = "shuttle"
    top = hinge[2] + 82.0 - D.HINGE[2]                  # the bracket's top plate, the doser's mounting face
    ay = (hinge[1] - (D.HINGE[1] - 20.0), hinge[1] - (D.HINGE[1] - 42.0))
    add(box((LANE_X - 45, SHUTTLE_X[1]), ay, (top, top + 8)), ALU)               # arm over the top plate
    add(box(SHUTTLE_X, ay, (30, top + 8)), ALU)                                   # upright plate
    add(box((SHUTTLE_X[0], RAIL_X[0] - 2), ay, (22, 30)), ALU)                    # foot
    add(box((RAIL_X[0] - 12, RAIL_X[0]), (sum(ay) / 2 - 22, sum(ay) / 2 + 22), (6, 30)), STEEL)   # rail carriage
    group[0] = ""
    lo, hi = gantry_y(0.0) - 40, gantry_y(TRAVEL[1]) + 40
    add(box(RAIL_X, (lo, hi), RAIL_Z), STEEL)                                     # the rail
    add(box((RAIL_X[0] - 14, RAIL_X[0]), (hi - 10, hi), (0, 40)), (0.2, 0.2, 0.22))   # dock: stop and detent
    # the coupling: two magnets on the shuttle, faces forwards; a steel tab on the right upright, in front of them
    face = ay[0]
    group[0] = "shuttle"
    for z in (top - 34, top - 6):
        add(cyl(((SHUTTLE_X[1] + 492) / 2, face + MAGNET_L / 2, z), (0, 1, 0), MAGNET_R, MAGNET_L),
            MAGNET_ON if coupled else MAGNET_OFF, 0.5)
    add(box((SHUTTLE_X[1], 492), (face + MAGNET_L, face + MAGNET_L + 6), (top - 50, top + 8)), ALU)
    group[0] = ""
    tab_y = by - BEAM[0] / 2 + TIP_GAP + (D.HINGE[1] - D.NOSE_TIP[1]) - (D.HINGE[1] - 20.0)
    add(box((SHUTTLE_X[1] + 2, UPRIGHT_X[1][0]), (tab_y - 6, tab_y), (top - 50, top + 8)), STEEL, 0.5)
    return items


def tip_y(ty, deg=D.TILT_DISPENSE):
    """The capillary tip's y in CubOS's frame (capper y = ty) at tilt `deg`."""
    s = D.HINGE[1] - D.NOSE_TIP[1]
    return ty + TOOL_AHEAD - BEAM[0] / 2 + TIP_GAP + s * (1 - np.cos(np.radians(deg)))


def lane_rows():
    """Vial centres (machine y) at VIAL pitch, from the doser's front-most dosing spot to its back-most."""
    y0, y1 = REACH0[1] + tip_y(0.0), REACH0[1] + tip_y(TRAVEL[1])
    return y0 + VIAL[3] * np.arange(int((y1 - y0) // VIAL[3]) + 1)


def zone_boxes():
    """The capper's reach, the doser's row, and the stretch of the row the tools can also reach (machine x, y)."""
    rx, ry = (REACH0[0], REACH0[0] + TRAVEL[0]), (REACH0[1], REACH0[1] + TRAVEL[1])
    ly = (REACH0[1] + tip_y(0.0), REACH0[1] + tip_y(TRAVEL[1]))
    lx = (LANE_X - 17, LANE_X + 17)
    return [(rx, ry, REACH_C), (lx, ly, LANE_C), (lx, (ly[0], ry[1]), BOTH_C)]


def render(items, w, h, scale, focus, view, up=(0.0, 0.0, 1.0)):
    pl = pv.Plotter(off_screen=True, window_size=(w, h))
    pl.set_background("white")
    pl.enable_depth_peeling(8)
    for m, c, s, o in items:
        pl.add_mesh(m, color=c, specular=s, specular_power=20, smooth_shading=True, opacity=o)
    v = np.asarray(view, float)
    pl.camera.focal_point = focus
    pl.camera.position = np.asarray(focus) + 1500.0 * v / np.linalg.norm(v)
    pl.camera.up = up
    pl.enable_parallel_projection()
    pl.camera.parallel_scale = scale
    pl.enable_anti_aliasing("ssaa")
    img = Image.fromarray(pl.screenshot(return_img=True))
    pl.close()
    return img


def framed(img, title, lines, head=92):
    """The render under a white header carrying its title and notes."""
    out = Image.new("RGB", (img.width, img.height + head), (255, 255, 255))
    out.paste(img, (0, head))
    d = ImageDraw.Draw(out)
    d.text((16, 10), title, font=font(24, bold=True), fill=INK)
    for i, t in enumerate(lines):
        d.text((16, 44 + 23 * i), t, font=font(17), fill=MUTED)
    return out


ISO = np.array([1.0, -0.85, 0.75])                      # front right, above
CLOSE = np.array([0.9, -1.0, 0.55])


def views():
    w, h = 760, 560
    rows = lane_rows()
    mid = rows[len(rows) // 2] - REACH0[1] - tip_y(0.0)  # capper y that puts the tip on a middle vial
    pose = dict(ty=mid, tx=110.0, deg=D.TILT_DISPENSE)
    _, hinge = doser_pose(gantry_y(mid), D.TILT_DISPENSE)
    rim_gap = HINGE_Z - (D.HINGE[1] - D.NOSE_TIP[1]) * np.sin(np.radians(D.TILT_DISPENSE)) - VIAL[2] - VIAL[1]
    iso = framed(render(scene(**pose, fade=("right",)), w, h, 290.0, (240.0, 255.0, 90.0), ISO),
                 "The idea on a CubXL stand-in", ["the doser lives in the back right corner; towed in Y by the gantry,",
                                                  "it doses one row of vials (right Y beam and upright see-through)"])
    close = framed(render(scene(**pose, fade=("right",)), w, h, 105.0, hinge + np.array([10.0, 0.0, 10.0]), CLOSE),
                   "The coupling", ["two 5 V pot magnets (Adafruit 3873) on the shuttle, faces forwards,",
                                    "pull on a steel tab on the right upright; the shuttle runs on its own rail"])
    # from above, with the zones drawn over the render
    k = (h / 2) / 300.0
    top = render(scene(**pose, fade=("gantry",)), w, h, 300.0, (240.0, 245.0, 0.0), (0.0, 0.0, 1.0), up=(0.0, 1.0, 0.0))
    to_px = lambda x, y: (w / 2 + (x - 240.0) * k, h / 2 - (y - 245.0) * k)
    layer = Image.new("RGBA", top.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    zb = zone_boxes()
    for (x0, x1), (y0, y1), c in zb:
        (px0, py1), (px1, py0) = to_px(x0, y0), to_px(x1, y1)
        rgb = tuple(int(255 * v) for v in c)
        d.rectangle((px0, py0, px1, py1), fill=rgb + (50,), outline=rgb + (255,), width=3)
    top = Image.alpha_composite(top.convert("RGBA"), layer).convert("RGB")
    d = ImageDraw.Draw(top)
    (rx, ry, _), (lx, ly, _), (_, by_, _) = zb
    for (x, y), t, c, anchor in (((rx[0] + 6, ry[0] + 6), "capper's reach, 388 × 234 mm", REACH_C, "lb"),
                                 ((lx[0] - 8, ly[1] - 4), f"doser's row, {ly[1] - ly[0]:.0f} mm", LANE_C, "rt"),
                                 ((lx[0] - 8, by_[0] + 4), f"tools reach it too: {by_[1] - by_[0]:.0f} mm", BOTH_C,
                                  "rb")):
        px, py = to_px(x, y)
        f = font(18, bold=True)
        d.rounded_rectangle(d.textbbox((px, py), t, font=f, anchor=anchor), 4, fill=(255, 255, 255))
        d.text((px, py), t, font=f, fill=tuple(int(160 * v) for v in c), anchor=anchor)
    n_both = int(sum(by_[0] - 0.1 <= r <= by_[1] for r in rows))
    top = framed(top, "From above", [f"{len(rows)} vials at {VIAL[3]:.0f} mm pitch, {n_both} of them also in the "
                                     "capper's reach", "front of the machine at the bottom; beam and head see-through"])
    side = framed(render(scene(**pose, fade=("right", "shuttle")), w, h, 150.0,
                         np.array([420.0, hinge[1] - 30.0, 120.0]), (1.0, 0.0, 0.0)),
                  "From the right", [f"tip {tip_y(0.0):.0f} mm behind the capper, {rim_gap:.0f} mm over the rims at 35°",
                                     "(right Y beam, upright and shuttle see-through)"])
    gap = 12
    sheet = Image.new("RGB", (2 * iso.width + 3 * gap, 2 * iso.height + 3 * gap), (232, 234, 238))
    for i, im in enumerate((iso, close, top, side)):
        sheet.paste(im, (gap + (i % 2) * (iso.width + gap), gap + (i // 2) * (iso.height + gap)))
    sheet.save(HERE / "cubxl_shuttle_views.png", optimize=True)
    print("cubxl_shuttle_views.png", sheet.size, "rows", np.round(rows - REACH0[1], 1), "hinge z", round(HINGE_Z, 1),
          "tip behind capper at 35 deg", round(tip_y(0.0), 1), "both", n_both)


def motion(w=600, h=420):
    """Couple at the dock, tow the doser down its row dosing every other vial, bring it back, let go, move on alone."""
    rows = lane_rows() - REACH0[1]
    at = lambda r: r - tip_y(0.0)                       # capper y that puts the tip over row y r (CubOS frame)
    ease = lambda a, b, n: [a + (b - a) * (1 - np.cos(np.pi * i / (n - 1))) / 2 for i in range(n)]
    home = TRAVEL[1]
    seq = [dict(ty=home, deg=D.TILT_PARK, coupled=False, note="docked, magnets off")] * 4
    seq += [dict(ty=home, deg=D.TILT_PARK, coupled=True, note="gantry home: magnets on, coupled")] * 5
    y = home
    for r in rows[::-2][1:4]:
        yy = min(at(r), home)
        seq += [dict(ty=t, deg=D.TILT_PARK, coupled=True, note="moving in Y, outlet up") for t in ease(y, yy, 10)]
        seq += [dict(ty=yy, deg=a, coupled=True, note="tilting to 35°") for a in ease(D.TILT_PARK, 35.0, 6)]
        seq += [dict(ty=yy, deg=35.0, coupled=True, note="dosing")] * 5
        seq += [dict(ty=yy, deg=a, coupled=True, note="back to park") for a in ease(35.0, D.TILT_PARK, 5)]
        y = yy
    seq += [dict(ty=t, deg=D.TILT_PARK, coupled=True, note="back to the dock") for t in ease(y, home, 12)]
    seq += [dict(ty=home, deg=D.TILT_PARK, coupled=False, note="magnets off: released")] * 4
    seq += [dict(ty=t, deg=D.TILT_PARK, coupled=False, doser_ty=home, note="the gantry goes on without it")
            for t in ease(home, 40.0, 12)]
    seq += [dict(ty=40.0, deg=D.TILT_PARK, coupled=False, doser_ty=home, note="the gantry goes on without it")] * 4
    frames = []
    for s in seq:
        s = dict(s)
        note = s.pop("note")
        im = render(scene(tx=60.0, fade=("right",), **s), w, h, 210.0, (340.0, 330.0, 100.0), ISO)
        im = framed(im, "Doser towed by the gantry (concept)", [note], head=70)
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=96))
    frames[0].save(HERE / "cubxl_shuttle.gif", save_all=True, append_images=frames[1:], duration=120, loop=0,
                   optimize=True)
    print("cubxl_shuttle.gif", len(frames), "frames", (HERE / "cubxl_shuttle.gif").stat().st_size, "bytes")


if __name__ == "__main__":
    views()
    motion()
