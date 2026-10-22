"""Ben's CubXL idea (PR 274, 2026-10-16): the miniature doser lives in the back right corner of the deck and rides with
the gantry in Y, held to it by electromagnets, dosing into one row of vials while staying behind the tools.

A concept sketch, not a design. The doser is the one-servo variant (doser_cad.tilt_meshes), mirrored so its servo faces
the middle of the deck. A side frame on a shuttle carries it, the shuttle runs on a rail screwed along the deck's right
margin, and a steel tab on the gantry's right side plate tows it through two electromagnets. The deck is Cubware's
PandaDeck.step. The rest of the CubXL (frame, gantry, head, tools) is boxes and cylinders, now placed from Ben's
measurements of 2026-10-19 (MEASURED below) and his photo of the right Y rail. What he didn't measure is marked assumed.

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
DECK = (480.0, 490.0, 10.0)                             # PandaDeck.step's plate; no slots outboard of x = 458
TRAVEL = (388.0, 233.665)                               # working_volume x, y (cub_xl_ben_pipette_capper.yaml)
PIPETTE = np.array([54.0, 12.999])                      # the pipette's offset from the capper
# MEASURED by Ben (PR 274, 2026-10-19), with the backboard moved out of the way (and with it in place):
RAIL_GAP = 38.0                                         # x: the deck's right edge to the right Y rail
BEAM_AHEAD, HEAD_AHEAD = 115.0, 65.0                    # y: the capper's axis in front of the beam (of the backboard)
BEAM_UNDER, HEAD_UNDER = 148.0, 120.0                   # z: the beam's (the head block's) underside above the deck
# assumed:
BEAM_DEPTH, BEAM_TALL = 40.0, 80.0                      # the X beam: a 40 x 80 profile (SainSmart's V2 review)
REACH0 = np.array([46.0, 101.0])                        # CubOS (0, 0) on the plate: x centred, y so that at the back
                                                        #   of its travel the beam's back face is over the deck's edge
SIDE_PLATE = 10.0                                       # the gantry's inner side plate, in the gap, 4 mm off the rail
Y_RAILS = ((-RAIL_GAP - 60.0, -RAIL_GAP), (DECK[0] + RAIL_GAP, DECK[0] + RAIL_GAP + 60.0))
PLATE_X = ((-RAIL_GAP + 4.0, -RAIL_GAP + 4.0 + SIDE_PLATE), (DECK[0] + RAIL_GAP - 4.0 - SIDE_PLATE,
                                                               DECK[0] + RAIL_GAP - 4.0))
VIAL = (28.0, 57.0, 18.0, 33.0)                         # 20 mL VOA: diameter, height, bottom above the plate, row pitch

# The doser, on the shuttle. Its capillary points forwards (-y), its body trails behind, its servo faces the deck.
PARK, DOSE = D.TILT_PARK, D.TILT_DISPENSE               # deg: outlet up (-10) for moves, 35 to dose
TIP_GAP = 5.0                                           # the tip, dosing, behind the beam's front face
LANE_X = 395.0                                          # the auger's axis, so the row of vials, in x
RIM_GAP = 5.0                                           # the tip above the vial rims while dosing, at least
RIM_CLEAR, BEAM_CLEAR = 2.0, 4.0                        # what the doser keeps over the rims behind, and under the beam
RAIL_X, RAIL_Z = (463.0, 475.0), (0.0, 8.0)             # MGN12 rail on the deck's free right margin (x 458 to 480)
CARRIAGE = (27.0, 45.0, 13.0)                           # MGN12H: width, length, height over the deck
CARRIAGE_Y = -42.0                                      # its centre, from the hinge: so that docked it is on the deck
SHUTTLE_X = (LANE_X + 62.0, LANE_X + 69.0)              # the shuttle's side plate, just outside the hinge screw's head
SERVO_BAR_X = (LANE_X - 60.0, LANE_X - 55.0)            # the frame's other side: the servo's frame, mirrored
MAGNET_R, MAGNET_L = 12.5, 20.0                         # Adafruit 3873 (P25/20): 25 x 20 mm, 5 kg rated, 5 V 0.3 A

STEEL, ALU, BLUE, BLACK = (0.36, 0.37, 0.40), (0.80, 0.82, 0.85), (0.16, 0.33, 0.72), (0.10, 0.10, 0.11)
MAGNET_ON, MAGNET_OFF, GLASS = (0.86, 0.18, 0.16), (0.45, 0.42, 0.42), (0.70, 0.82, 0.90)
REACH_C, LANE_C, BOTH_C = (0.25, 0.50, 0.90), (0.95, 0.55, 0.15), (0.45, 0.70, 0.30)


def box(x, y, z):
    return pv.Box((x[0], x[1], y[0], y[1], z[0], z[1])).triangulate().compute_normals(split_vertices=True,
                                                                                       feature_angle=30.0)


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


def beam_front(ty):
    """The beam's front face (machine y) for a capper y in CubOS's frame."""
    return REACH0[1] + ty + BEAM_AHEAD


S = D.HINGE[1] - D.NOSE_TIP[1]                          # the hinge to the capillary's tip, 48 mm


def doser_pose(fy, deg):
    """The doser's meshes at tilt `deg`, coupled to a beam whose front face is at y = fy, and its hinge (machine).
    PR 176's top plate and -x arm are left off (they would be under the beam): the shuttle's side frame replaces them.
    The tip is furthest forwards at level, TIP_GAP behind the beam's front face; tilted, it moves back."""
    hinge = np.array([LANE_X, fy + TIP_GAP + S, HINGE_Z])
    out = {}
    for k, m in D.tilt_meshes(deg).items():
        if k == ("bracket", "alu"):                     # keep only the servo's frame (x > 0, under the web)
            m = m.clip_box((0.0, 1e3, -1e3, 1e3, -1e3, 53.0), invert=False).extract_surface(algorithm=None)
        m = D._mirror_x(m.triangulate())
        out[k] = m.translate(hinge - D.HINGE * np.array([-1.0, 1.0, 1.0]), inplace=False)
    return out, hinge


def _low(deg, y0, half):
    """The module's lowest point (doser frame) within `half` of the auger's axis in x and behind y0, at tilt deg."""
    return min(m.clip_box((-half, half, y0, 1e3, -1e3, 1e3), invert=False).points[:, 2].min(initial=1e3)
               for m in D.tilt_meshes(deg).values())


def _hinge_z():
    """The hinge's height. The body trails over the row, so at PARK nothing in the row's width may come lower than
    RIM_CLEAR over the rims; dosing, the tip is RIM_GAP over them and only the vial being dosed may be under the tip."""
    rim = VIAL[2] + VIAL[1]
    c = np.radians(DOSE)
    tip = D.HINGE + np.array([0.0, -S * np.cos(c), -S * np.sin(c)])
    row = VIAL[0] / 2 + 2.0                             # half the width of the row of vials, with 2 mm to spare
    need = [rim + RIM_GAP - tip[2], rim + RIM_CLEAR - _low(DOSE, tip[1] + VIAL[0] / 2 + 2.0, row),
            rim + RIM_CLEAR - _low(PARK, -1e3, row)]
    return D.HINGE[2] + max(need)


HINGE_Z = _hinge_z()


def shuttle_parts(hinge):
    """[(mesh, colour)]: the side frame, the shuttle, its carriage and the magnets' block, for a hinge at `hinge`."""
    hx, hy, hz = hinge
    cy = hy + CARRIAGE_Y
    rear = (hy + 84.0, hy + 92.0)                       # behind the module's sweep (its back end: hinge + 79)
    out = [(box(SHUTTLE_X, (hy - 20.0, hy + 40.0), (CARRIAGE[2] + 6.0, hz + 15.0)), ALU),   # side plate, hinge
           (box(SHUTTLE_X, (hy + 40.0, rear[1]), (hz - 10.0, hz + 25.0)), ALU),             # and back to the rear
           (box(SERVO_BAR_X, (hy + 39.6, rear[1]), (hz - 10.0, hz + 25.0)), ALU),          # the servo's side
           (box((SERVO_BAR_X[0], SHUTTLE_X[1]), rear, (hz - 10.0, hz + 25.0)), ALU),        # the rear cross-member
           (box((SHUTTLE_X[0], 501.0), (cy - CARRIAGE[1] / 2, hy + 40.0), (CARRIAGE[2], CARRIAGE[2] + 6.0)), ALU),
           (box((sum(RAIL_X) / 2 - CARRIAGE[0] / 2, sum(RAIL_X) / 2 + CARRIAGE[0] / 2),
                (cy - CARRIAGE[1] / 2, cy + CARRIAGE[1] / 2), (RAIL_Z[1] - 4.0, CARRIAGE[2])), STEEL)]
    return out


def scene(ty=TRAVEL[1], tx=150.0, deg=None, coupled=True, doser_ty=None, fade=(), hide=()):
    """[(mesh, colour, specular, opacity)]: the CubXL stand-in with the capper at CubOS (tx, ty) and the doser at tilt
    `deg`. doser_ty: where the doser was left, if it isn't coupled (default: with the gantry). fade, hide: groups to
    draw see-through, or not at all ("right": the right Y rail and the gantry's right side; "beam"; "gantry": the head
    and the left side; "shuttle")."""
    items = []
    group = [""]
    add = lambda m, c, s=0.3, o=1.0: None if group[0] in hide else items.append(
        (m, c, s, 0.22 if group[0] in fade or (group[0] == "beam" and "gantry" in fade) else o))
    deg = PARK if deg is None else deg
    fy = beam_front(ty)
    # the frame: the deck, the two Y rails with their lead screws, the front and back members, blue corner plates
    add(deck(), (0.86, 0.90, 0.94), 0.5, 0.55)
    for i, (x0, x1) in enumerate(Y_RAILS):
        group[0] = "right" if i else ""
        add(box((x0, x1), (-40, 530), (-50, -2)), ALU)
        add(cyl(((x0 + x1) / 2, 245, -10), (0, 1, 0), 6, 560), STEEL, 0.5)
        for y0 in (-50, 530):
            add(box((x0 - 5, x1 + 5), (y0, y0 + 10), (-55, 30)), BLUE)
    group[0] = ""
    for y0 in (-40, 490):
        add(box((-RAIL_GAP, DECK[0] + RAIL_GAP), (y0, y0 + 40), (-50, -10)), ALU)
    # the gantry: on each side an inner and an outer plate on three wheels, a blue upright; the beam; the head
    for i, ((p0, p1), (r0, r1)) in enumerate(zip(PLATE_X, Y_RAILS)):
        group[0] = "right" if i else "gantry"
        o0, o1 = (r0 - 14.0, r0 - 4.0) if i == 0 else (r1 + 4.0, r1 + 14.0)
        for q0, q1 in ((p0, p1), (o0, o1)):
            add(box((q0, q1), (fy - 35, fy + 75), (-35, 75)), ALU)
        lo, hi = min(p0, o0), max(p1, o1)
        for wy in (fy - 15, fy + 20, fy + 55):
            add(cyl(((r0 + r1) / 2, wy, 10), (1, 0, 0), 11, r1 - r0 - 4), BLACK, 0.2)
        add(box((lo, hi), (fy - 10, fy + 50), (75, BEAM_UNDER + BEAM_TALL)), BLUE)
    group[0] = "beam"
    add(box((PLATE_X[0][1], PLATE_X[1][0]), (fy, fy + BEAM_DEPTH), (BEAM_UNDER, BEAM_UNDER + BEAM_TALL)), ALU)
    group[0] = "gantry"
    cx = REACH0[0] + tx
    cy = fy - BEAM_AHEAD                                # the capper's axis
    bb = fy - (BEAM_AHEAD - HEAD_AHEAD)                 # the backboard's front face
    add(box((cx - 40, cx + 45), (bb + 12, fy), (HEAD_UNDER, BEAM_UNDER + BEAM_TALL + 30)), ALU)   # the block
    add(box((cx - 200, cx + 50), (bb, bb + 10), (150, 330)), BLACK, 0.1)                      # the backboard
    add(cyl((cx, cy, 140), (0, 0, 1), 24, 70), BLACK, 0.2)                                     # capper
    add(box((cx - 10, cx + 10), (cy + 20, bb), (150, 170)), BLACK, 0.1)                        # its mount
    px, py = cx + PIPETTE[0], cy + PIPETTE[1]
    add(box((px - 18, px + 18), (py - 15, bb), (150, 290)), (0.88, 0.88, 0.86))              # pipette body
    add(cyl((px, py, 135), (0, 0, 1), 6, 30), (0.88, 0.88, 0.86))
    add(pv.Cone(center=(px, py, 112), direction=(0, 0, -1), height=16, radius=3.5, resolution=24), (0.92, 0.92, 0.9))
    # the row of vials, in a strip holder
    group[0] = ""
    rows = lane_rows()
    add(box((LANE_X - 20, LANE_X + 20), (rows[0] - 22, rows[-1] + 22), (0, VIAL[2])), (0.93, 0.93, 0.95), 0.2)
    for y in rows:
        add(cyl((LANE_X, y, VIAL[2] + VIAL[1] / 2), (0, 0, 1), VIAL[0] / 2, VIAL[1]), GLASS, 0.6, 0.45)
    # the doser, its frame and shuttle
    dfy = fy if doser_ty is None else beam_front(doser_ty)
    meshes, hinge = doser_pose(dfy, deg)
    for (_, mat), m in meshes.items():
        color, spec = D.MATERIALS[mat]
        add(m, color, spec)
    group[0] = "shuttle"
    for m, c in shuttle_parts(hinge):
        add(m, c)
    # the coupling: two magnets on a block on the shuttle's foot, faces forwards; a steel tab on the gantry's plate
    face = dfy
    for z in (34.0, 62.0):
        add(cyl((490.0, face + MAGNET_L / 2, z), (0, 1, 0), MAGNET_R, MAGNET_L), MAGNET_ON if coupled else MAGNET_OFF,
            0.5)
    add(box((477.0, 503.0), (face + MAGNET_L, face + MAGNET_L + 6), (CARRIAGE[2] + 6.0, 78)), ALU)
    group[0] = ""
    add(box((477.0, PLATE_X[1][0]), (fy - 6.0, fy), (24, 78)), STEEL, 0.5)
    end = beam_front(TRAVEL[1]) + TIP_GAP + S + CARRIAGE_Y + CARRIAGE[1] / 2      # the carriage's back, docked
    add(box(RAIL_X, (beam_front(0.0) + TIP_GAP + S + CARRIAGE_Y - CARRIAGE[1] / 2 - 5.0, end + 1.0), RAIL_Z), STEEL)
    add(box(RAIL_X, (end + 1.0, end + 6.0), (0, 30)), (0.2, 0.2, 0.22))          # dock: stop and detent
    return items


def tip_y(ty, deg=None):
    """The capillary tip's y in CubOS's frame (capper y = ty) at tilt `deg` (default: dosing)."""
    return ty + BEAM_AHEAD + TIP_GAP + S * (1.0 - np.cos(np.radians(DOSE if deg is None else deg)))


def fit():
    """Clearances, in mm: under the beam and under the head's block (worst over PARK..DOSE), the tip over the rims,
    the doser's top, and the steepest tilt that still clears the beam by BEAM_CLEAR."""
    fy = beam_front(0.0)

    def tops(deg):
        meshes, _ = doser_pose(fy, deg)
        p = np.vstack([m.points for m in meshes.values()])
        under = p[(p[:, 1] >= fy) & (p[:, 1] <= fy + BEAM_DEPTH), 2].max(initial=-1e3)
        ahead = p[p[:, 1] < fy, 2].max(initial=-1e3)
        return under, ahead, p[:, 2].max()
    worst = [tops(a) for a in np.arange(PARK, DOSE + 0.1, 2.5)]
    steep = max((a for a in np.arange(PARK, D.TILT_MAX + 0.1, 0.5) if tops(a)[0] <= BEAM_UNDER - BEAM_CLEAR),
                default=PARK)
    rim = VIAL[2] + VIAL[1]
    return dict(beam=BEAM_UNDER - max(w[0] for w in worst), head=HEAD_UNDER - max(w[1] for w in worst),
                rim=HINGE_Z - S * np.sin(np.radians(DOSE)) - rim, top=max(w[2] for w in worst), steep=steep)


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


def render(items, w, h, scale, focus, view, up=(0.0, 0.0, 1.0), cut_x=None):
    """cut_x: draw only what lies to the right of x = cut_x (a section, for the side view)."""
    pl = pv.Plotter(off_screen=True, window_size=(w, h))
    pl.set_background("white")
    pl.enable_depth_peeling(8)
    for m, c, s, o in items:
        if cut_x is not None:
            m = m.clip(normal=(-1.0, 0.0, 0.0), origin=(cut_x, 0.0, 0.0))
            if not m.n_points:
                continue
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
    pose = dict(ty=mid, tx=110.0, deg=DOSE)
    fy = beam_front(mid)
    _, hinge = doser_pose(fy, DOSE)
    f = fit()
    iso = framed(render(scene(**pose, fade=("right", "beam")), w, h, 290.0, (240.0, 255.0, 90.0), ISO),
                 "On Ben's measurements",
                 [f"the doser rides under the beam, behind its front face; dosing at {DOSE:g}°",
                  "(beam, right Y rail and the gantry's right side see-through)"])
    close = framed(render(scene(**pose, fade=("right", "beam")), w, h, 120.0, np.array([440.0, fy + 45.0, 75.0]),
                          CLOSE),
                   "The shuttle and the coupling",
                   ["a rail on the deck's free right margin; magnets on the shuttle, faces",
                    "forwards, on a steel tab on the gantry's side plate"])
    # from above, with the zones drawn over the render
    k = (h / 2) / 300.0
    top = render(scene(**pose, fade=("gantry",)), w, h, 300.0, (250.0, 245.0, 0.0), (0.0, 0.0, 1.0), up=(0.0, 1.0, 0.0))
    to_px = lambda x, y: (w / 2 + (x - 250.0) * k, h / 2 - (y - 245.0) * k)
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
        fnt = font(18, bold=True)
        d.rounded_rectangle(d.textbbox((px, py), t, font=fnt, anchor=anchor), 4, fill=(255, 255, 255))
        d.text((px, py), t, font=fnt, fill=tuple(int(160 * v) for v in c), anchor=anchor)
    n_both = int(sum(by_[0] - 0.1 <= r <= by_[1] for r in rows))
    top = framed(top, "From above", [f"{len(rows)} vials at {VIAL[3]:.0f} mm pitch, {n_both} of them also in the "
                                     "capper's reach", "front of the machine at the bottom; beam and head see-through"])
    # from the right, with the measured heights drawn across
    sc, foc = 150.0, np.array([420.0, hinge[1] - 40.0, 120.0])
    side = render(scene(**dict(pose, tx=TRAVEL[0]), fade=("shuttle",), hide=("right",)), w, h, sc, foc,
                  (1.0, 0.0, 0.0), cut_x=300.0)
    d = ImageDraw.Draw(side)
    kz = (h / 2) / sc
    to_side = lambda y, z: (w / 2 + (y - foc[1]) * kz, h / 2 - (z - foc[2]) * kz)
    rim = VIAL[2] + VIAL[1]
    for z, t, c in ((BEAM_UNDER, f"beam's underside {BEAM_UNDER:.0f}", (200, 60, 40)),
                    (HEAD_UNDER, f"head's block {HEAD_UNDER:.0f}", (200, 60, 40)),
                    (rim, f"vial rims {rim:.0f} (assumed)", (90, 96, 106))):
        _, pz = to_side(0.0, z)
        for x0 in range(0, w, 14):
            d.line((x0, pz, x0 + 7, pz), fill=c, width=2)
        d.text((8, pz - 22), t, font=font(16, bold=True), fill=c)
    for y, t, anchor in ((fy, "beam's front face", "ra"), (fy + BEAM_DEPTH, "and back (40 × 80 profile)", "la")):
        px, _ = to_side(y, 0.0)
        d.line((px, 0, px, h), fill=(200, 60, 40), width=2)
        d.text((px + (6 if anchor == "la" else -6), 6), t, font=font(16, bold=True), fill=(200, 60, 40), anchor=anchor)
    side = framed(side, "From the right", [f"tip {tip_y(0.0):.0f} mm behind the capper, {f['rim']:.0f} mm over the "
                                           f"rims at {DOSE:g}°; {f['beam']:.0f} mm under the beam",
                                           "head at its right end; a section right of x = 300 mm, front on the left"])
    gap = 12
    sheet = Image.new("RGB", (2 * iso.width + 3 * gap, 2 * iso.height + 3 * gap), (232, 234, 238))
    for i, im in enumerate((iso, close, top, side)):
        sheet.paste(im, (gap + (i % 2) * (iso.width + gap), gap + (i // 2) * (iso.height + gap)))
    sheet.save(HERE / "cubxl_shuttle_views.png", optimize=True)
    print("cubxl_shuttle_views.png", sheet.size, "rows", np.round(rows - REACH0[1], 1), "hinge z", round(HINGE_Z, 1),
          "tip behind capper", round(tip_y(0.0), 1), "both", n_both, {k: round(float(v), 1) for k, v in f.items()})


def motion(w=600, h=420):
    """Couple at the dock, tow the doser down its row dosing every other vial, run the head to its right end, bring the
    doser back, let go, move on alone."""
    rows = lane_rows() - REACH0[1]
    at = lambda r: r - tip_y(0.0)                       # capper y that puts the tip over row y r (CubOS frame)
    ease = lambda a, b, n: [a + (b - a) * (1 - np.cos(np.pi * i / (n - 1))) / 2 for i in range(n)]
    home = TRAVEL[1]
    seq = [dict(ty=home, deg=PARK, coupled=False, note="docked, magnets off")] * 4
    seq += [dict(ty=home, deg=PARK, coupled=True, note="gantry home: magnets on, coupled")] * 5
    y = home
    for r in rows[::-2][1:4]:
        yy = min(at(r), home)
        seq += [dict(ty=t, deg=PARK, coupled=True, note="moving in Y, outlet up") for t in ease(y, yy, 10)]
        seq += [dict(ty=yy, deg=a, coupled=True, note=f"tilting to {DOSE:g}°") for a in ease(PARK, DOSE, 6)]
        seq += [dict(ty=yy, deg=DOSE, coupled=True, note="dosing")] * 5
        seq += [dict(ty=yy, deg=a, coupled=True, note="back to park, outlet up") for a in ease(DOSE, PARK, 5)]
        y = yy
    seq += [dict(ty=y, tx=t, deg=PARK, coupled=True, note="the head runs to its right end, in front of the doser")
            for t in ease(60.0, TRAVEL[0], 10) + ease(TRAVEL[0], 60.0, 8)]
    seq += [dict(ty=t, deg=PARK, coupled=True, note="back to the dock") for t in ease(y, home, 12)]
    seq += [dict(ty=home, deg=PARK, coupled=False, note="magnets off: released")] * 4
    seq += [dict(ty=t, deg=PARK, coupled=False, doser_ty=home, note="the gantry goes on without it")
            for t in ease(home, 40.0, 12)]
    seq += [dict(ty=40.0, deg=PARK, coupled=False, doser_ty=home, note="the gantry goes on without it")] * 4
    frames = []
    for s in seq:
        s = dict(s)
        note = s.pop("note")
        s.setdefault("tx", 60.0)
        im = render(scene(fade=("right", "beam"), **s), w, h, 210.0, (340.0, 330.0, 100.0), ISO)
        im = framed(im, "Towed doser, on Ben's measurements", [note], head=70)
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=96))
    frames[0].save(HERE / "cubxl_shuttle.gif", save_all=True, append_images=frames[1:], duration=120, loop=0,
                   optimize=True)
    print("cubxl_shuttle.gif", len(frames), "frames", (HERE / "cubxl_shuttle.gif").stat().st_size, "bytes")


if __name__ == "__main__":
    import sys
    if "--fit" in sys.argv:
        print("hinge z", round(HINGE_Z, 1), "tip behind capper", round(tip_y(0.0), 1),
              {k: round(float(v), 1) for k, v in fit().items()})
    else:
        views()
        motion()
