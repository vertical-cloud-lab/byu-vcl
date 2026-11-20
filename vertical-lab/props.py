"""Small things the workflow handles, and the robot's mobile base. PyVista primitives, millimetres, z up.

* The vial is the multi-doser's own: a 20 mL vial, 28 mm across and 61 mm tall (powder-doser
  ``cad/chain-carousel-v2/params.py``), with a powder fill and a liquid fill that the animation sets.
* The vial rack is a printed block like the CubXL's six-vial rack (``lab_models/equipment.py``), sized for 28 mm vials.
* The MiR's intermediary storage is a low block on its cabinet top, beside the arm's mounting plate, with bored and
  chamfered pockets (``pocket_block``, ``buffer_holder``; ``charge.carrier`` for the charge cups): no post.
* The mobile base is a **MiR250** (Mobile Industrial Robots, the AMR sold with UR arms): 800 x 580 x 300 mm
  (MiR250 data sheet), with a top cabinet that holds the UR control box (e-Series control box 460 x 449 x 254 mm,
  UR data sheet), so the arm's base sits at ``AMR_TOP``. The cabinet's height is a layout choice: it puts the
  arm's base 80 mm under the opening's counter, so the arm reaches over the counter and down onto the tray.
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

VIAL_R, VIAL_H = 14.0, 61.0                  # 20 mL vial (powder-doser chain-carousel-v2 params: 28 x 61 mm)
VIAL_WALL, VIAL_FLOOR = 1.2, 2.5
GLASS = (0.62, 0.78, 0.90)
POWDER = (0.33, 0.33, 0.36)                  # a grey metal powder (Al 4047, Si: the alloy lab's powders)
LIQUID = (0.25, 0.50, 0.85)
RACK_C = (0.94, 0.94, 0.92)

MIR = dict(L=800.0, W=580.0, H=300.0)        # MiR250: 800 x 580 x 300 mm
CAB_H = 480.0                                # top cabinet with the UR control box (layout choice, see above)
AMR_TOP = MIR["H"] + CAB_H + 20.0            # arm base height above the floor (20 mm mounting plate)
MIR_ACCEL = 300.0                            # mm/s^2: the MiR250 speeds up and slows down at 0.3 m/s^2 at full
#                                              payload; its top speed is 2.0 m/s (MiR250 spec sheet, Hartfiel's copy)


# ------------------------------------------------------------------------------------------------- the drives
# From PR #321 (claude/issue-303-r5-fixes, a34367a), brought over in round 8. A MiR250 drive from rest to rest: up to
# speed at MIR_ACCEL, on at vmax, down again. A trapezoid in speed, or a triangle when the drive is too short to reach
# vmax: at 0.3 m/s^2 it takes 7.5 m to reach 1.5 m/s and stop again, so along the line it never does. Scene.step eases
# its u; drive with ramp_frac(unease(u), ...) to keep this profile instead.
def unease(e: float) -> float:
    """The inverse of scene.ease: the step's own time (0-1) for the eased u that Scene.step passes, for a motion that
    keeps a profile of its own (a MiR250's drive, ramp_frac). (#321 put this in scene.py.)"""
    e = min(max(e, 0.0), 1.0)
    return 0.5 - math.sin(math.asin(1.0 - 2.0 * e) / 3.0)


def ramp_secs(dist: float, vmax: float, accel: float = MIR_ACCEL) -> float:
    """Seconds for a drive of `dist` (mm, or deg with a deg/s^2 accel) from rest to rest."""
    d = abs(dist)
    if d * accel <= vmax * vmax:
        return 2.0 * math.sqrt(d / accel)
    return d / vmax + vmax / accel


def ramp_peak(dist: float, vmax: float, accel: float = MIR_ACCEL) -> float:
    """The top speed that drive reaches: vmax, or less on a short one."""
    return min(vmax, math.sqrt(abs(dist) * accel))


def ramp_frac(u: float, dist: float, vmax: float, accel: float = MIR_ACCEL) -> float:
    """The share of that drive covered at u (0-1) of its time; spread over a longer step, it is slower all through."""
    d = abs(dist)
    if d < 1e-9:
        return 1.0
    T = ramp_secs(d, vmax, accel)
    t = min(max(u, 0.0), 1.0) * T
    v = ramp_peak(d, vmax, accel)
    ta = v / accel                                  # time to reach the top speed
    if t <= ta:
        s = 0.5 * accel * t * t
    elif t >= T - ta:
        s = d - 0.5 * accel * (T - t) ** 2
    else:
        s = 0.5 * accel * ta * ta + v * (t - ta)
    return min(1.0, max(0.0, s / d))


def s_curve(x0, y0, x1, y1, n=201):
    """A MiR250's drive from (x0, y0) to (x1, y1) that also changes lanes: x even in p, y on a smoothstep, its long axis
    on the tangent (it is differential drive, so it can't slide sideways). Returns (at, ps, s): at(p) -> (x, y, heading
    in degrees) and the path's length s at each of ps, to drive it with ramp_frac by length."""
    def at(p):
        x = x0 + (x1 - x0) * p
        y = y0 + (y1 - y0) * (3 * p * p - 2 * p ** 3)
        dydx = (y1 - y0) * (6 * p - 6 * p * p) / (x1 - x0) if abs(x1 - x0) > 1 else 0.0
        return x, y, math.degrees(math.atan(dydx))
    ps = np.linspace(0.0, 1.0, n)
    xy = np.array([at(q)[:2] for q in ps])
    return at, ps, np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]


def _cyl(r, h, z0=0.0, x=0.0, y=0.0, res=40):
    return pv.Cylinder(center=(x, y, z0 + h / 2), direction=(0, 0, 1), radius=r, height=h, resolution=res).triangulate()


def vial_glass() -> pv.PolyData:
    """Open 20 mL vial, base centre at the origin: a thin wall and floor, the neck's thread band."""
    outer = _cyl(VIAL_R, VIAL_H)
    neck = pv.Cylinder(center=(0, 0, VIAL_H - 5), direction=(0, 0, 1), radius=VIAL_R + 0.6, height=8,
                       resolution=40).triangulate()
    return outer.merge(neck)


def fill(level_mm: float, r: float = VIAL_R - VIAL_WALL) -> pv.PolyData:
    """A fill of unit height (the animation scales z), from the vial's floor."""
    return _cyl(r, 1.0, 0.0, res=32)


def vial_rack(n: int = 6, pitch: float = 34.0) -> tuple[pv.PolyData, list[tuple[float, float, float]]]:
    """A printed rack: n holes in a row along x, 32 mm deep. Returns the mesh and the vial seats (base centres)."""
    w = n * pitch + 16
    block = pv.Box(bounds=(-w / 2, w / 2, -26, 26, 0, 40)).triangulate()
    seats = [(-w / 2 + 8 + pitch * (i + 0.5), 0.0, 8.0) for i in range(n)]
    return block, seats


def mir250() -> dict[str, tuple[pv.PolyData, tuple]]:
    """MiR250 body, its status-light band, the top cabinet and the arm's mounting plate; origin on the floor at the
    centre of the footprint, long side along x, the arm mounted over the front (-y) half."""
    L, W, H = MIR["L"], MIR["W"], MIR["H"]
    body = pv.Box(bounds=(-L / 2, L / 2, -W / 2, W / 2, 30, H - 20)).triangulate()
    cover = pv.Box(bounds=(-L / 2 + 10, L / 2 - 10, -W / 2 + 10, W / 2 - 10, H - 20, H)).triangulate()
    band = pv.Box(bounds=(-L / 2 - 2, L / 2 + 2, -W / 2 - 2, W / 2 + 2, 60, 78)).triangulate()
    skirt = pv.Box(bounds=(-L / 2 + 20, L / 2 - 20, -W / 2 + 20, W / 2 - 20, 0, 30)).triangulate()
    cab = pv.Box(bounds=(-L / 2 + 40, L / 2 - 40, -W / 2 + 30, W / 2 - 30, H, H + CAB_H)).triangulate()
    plate = pv.Box(bounds=(-170, 170, -W / 2 + 30, W / 2 - 30, H + CAB_H, AMR_TOP)).triangulate()
    door = pv.Box(bounds=(-L / 2 + 70, L / 2 - 70, -W / 2 + 28, -W / 2 + 30, H + 40, H + CAB_H - 40)).triangulate()
    estop = pv.Cylinder(center=(L / 2 - 90, -W / 2 + 60, AMR_TOP + 15), direction=(0, 0, 1), radius=20,
                        height=30).triangulate()
    return {
        "amr body": (body.merge(skirt), (0.22, 0.23, 0.25)),
        "amr cover": (cover, (0.80, 0.81, 0.83)),
        "amr light band": (band, (0.55, 0.85, 1.00)),
        "amr cabinet": (cab.merge(plate), (0.86, 0.87, 0.88)),
        "amr cabinet door": (door, (0.70, 0.72, 0.75)),
        "amr e-stop": (estop, (0.85, 0.12, 0.10)),
    }


# The MiR's intermediary storage (byu-vcl PR #318, round 7). Sterling: "There's no insertion gap for the
# intermediary storage on the MiR250. They would just fall off. Also, it's positioned rather high ... Should probably be
# much lower / flush with the base." So it is a low block standing on the cabinet top beside the arm's mounting plate,
# no post, with real bored pockets: about 1 mm radial clearance, a 45 deg lead-in at the mouth, and deep enough (over
# 40 % of a vial's or a cup's height) that nothing tips out while the MiR drives. A printed or machined block; the
# sizes are layout choices, not a product.
DECK_H = 30.0                # the pocket block's height over the cabinet top, 10 mm over the mounting plate
DECK_FLOOR = 4.0             # under the pockets: the seats are this high in the block
DECK_DEPTH = DECK_H - DECK_FLOOR      # 26 mm: 43 % of the 61 mm vial, 41 % of the 63.5 mm charge cup
POCKET_CLEAR = 1.0           # radial clearance in a pocket
POCKET_LEAD = 3.0            # 45 deg chamfer at a pocket's mouth: the lead-in that guides a part in
HOLDER_H = DECK_H            # was the vial holder's 260 mm post; kept as a name for older callers


def _cq_mesh(shape, tol: float = 0.2) -> pv.PolyData:
    verts, tris = shape.tessellate(tol, 0.25)
    pts = np.array([(v.x, v.y, v.z) for v in verts], float)
    faces = np.hstack([np.full((len(tris), 1), 3), np.asarray(tris, int)]).ravel()
    return pv.PolyData(pts, faces).clean().compute_normals(split_vertices=True, feature_angle=35.0,
                                                           auto_orient_normals=True)


_BLOCKS: dict = {}


def pocket_block(x0, x1, y0, y1, holes, h: float = DECK_H, floor: float = DECK_FLOOR,
                 lead: float = POCKET_LEAD) -> pv.PolyData:
    """A block, its bottom face at z = 0, with flat-bottomed bores [(x, y, r)] from its top down to `floor`, each with a
    45 deg chamfer `lead` deep at its mouth. CadQuery, tessellated once per shape."""
    key = (x0, x1, y0, y1, tuple(holes), h, floor, lead)
    if key not in _BLOCKS:
        import cadquery as cq
        b = cq.Workplane("XY").box(x1 - x0, y1 - y0, h, centered=False).translate((x0, y0, 0))
        for x, y, r in holes:
            bore = cq.Workplane("XY").circle(r).extrude(h - floor + 1.0).translate((x, y, floor))
            cone = cq.Solid.makeCone(r, r + lead + 0.5, lead + 0.5, pnt=cq.Vector(x, y, h - lead),
                                     dir=cq.Vector(0, 0, 1))
            b = b.cut(bore).cut(cq.Workplane("XY").add(cone))
        _BLOCKS[key] = _cq_mesh(b.val())
    return _BLOCKS[key].copy()


def buffer_holder() -> tuple[pv.PolyData, tuple[float, float, float]]:
    """A one-vial block on the cabinet top, beside the arm's mounting plate: where the vial waits while the VLM swaps
    trays. Its frame's origin is on the cabinet top; returns the mesh and the seat (the vial's base centre): a 30 mm
    bore for the 28 mm vial, 26 mm deep, with a lead-in. The gripper takes the vial 50 mm up, so its fingertips stay
    about 5 mm over the block."""
    mesh = pocket_block(-32.0, 32.0, -32.0, 32.0, [(0.0, 0.0, VIAL_R + POCKET_CLEAR)])
    return mesh, (0.0, 0.0, DECK_FLOOR)


def tcp_frame(p, approach=(0, 0, -1), spin_deg: float = 0.0) -> np.ndarray:
    """A 4x4 tool pose at point p with the tool's z along `approach` (unit vector) and its x picked by `spin_deg`.

    For an approach within 60 deg of level, spin 0 always has the tool's y pointing down (round 7). Until then it
    pointed down or up depending on the heading. That rolled the gripper 180 deg between headings, which put the wrist
    camera (ur_arm.camera_meshes, on tool0's -y side) under the gripper for some of them, and turned a part held level
    upside down between two headings. Straight-down and steep approaches are as before."""
    z = np.asarray(approach, float)
    z /= np.linalg.norm(z)
    ref = np.array([1.0, 0.0, 0.0]) if abs(z[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    x = ref - z * (ref @ z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    if y[2] > 0.5:                     # level-ish with y up: roll 180 deg about z, so y points down
        x, y = -x, -y
    a = np.radians(spin_deg)
    x, y = x * np.cos(a) + y * np.sin(a), -x * np.sin(a) + y * np.cos(a)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, p
    return M


# ------------------------------------------------------------------------------------------- powder jars (round 9)
# Sterling (PR #318, 2026-11-05 22:56): "What's with the technicolor jars? Keep them all a normal black lid with
# transparent glass, but if you want to point out something that's unique about them, use a legend and a color change
# that then reverts once the legend has been shown for a bit of time." So every powder jar in the lab is drawn the same
# way: clear glass (light grey-blue, about 35 % opaque, so the powder shows), a matte black cap, a white label. To point
# something out (which lot, which size cut, which powder), tint only those jars or their powder for a few seconds while
# a legend says what the tint means, then fade back. The helpers, for any stream's scenes:
#   jar_style()                    the colours and opacities, as a dict
#   jar_meshes(d, h, lid_h)        one jar's parts as PolyData, base centre at the origin, the label facing -y
#   jar_parts(d, h, lid_h)         the same as {part: (mesh, rgb, opacity)}, for Instrument.meshes or sc.add
#   tint_sleeve(d, h)              a tinted see-through sleeve just outside a jar's glass: fade it in to tint the jar
#   TINT, tinted(rgb, tint, k)     the highlight colours; a colour k of the way from rgb to a tint (sc.color[name])
#   pulse(t, t_on, t_off, ramp)    0 -> 1 -> 0: a tint's strength at time t, with smooth ramps
#   use_legend(sc)                 a Scene then draws sc.legend = dict(title=, items=[(rgb, text)], alpha=0-1)
#   draw_legend(img, title, items, alpha, s)   the legend box itself (PIL), top right under the step label
#   piece_legend(key, legends)     for a tour clip (tour.py): a legend shown while a fade piece of the instrument shows
JAR_GLASS = (0.76, 0.83, 0.90)               # clear glass, drawn light grey-blue so it reads on a white floor
JAR_GLASS_OPACITY = 0.35
JAR_LID = (0.07, 0.07, 0.08)                 # matte black cap (phenolic or PP; PTFE-lined: notes/lab_r8.md, "Which containers for powder")
JAR_LABEL = (0.97, 0.97, 0.95)               # a white paper label
JAR_PRINT = (0.10, 0.10, 0.11)               # the ID printed on it
JAR_POWDER = POWDER                          # grey metal powder
JAR_WALL = 2.0                               # glass wall, mm (drawn: the powder's radius is the jar's less this)
# highlight tints, one meaning each per clip; always shown with a legend, then back to the plain jar
TINT = {"amber": (0.97, 0.60, 0.08), "teal": (0.00, 0.62, 0.66), "magenta": (0.84, 0.20, 0.58),
        "blue": (0.15, 0.42, 0.92), "green": (0.30, 0.70, 0.25)}
TINT_OPACITY = 0.72                          # a tint sleeve's opacity when fully on


def jar_style() -> dict:
    """The lab-wide powder jar: {"glass": rgb, "glass_opacity": a, "lid": rgb, "label": rgb, "print": rgb,
    "powder": rgb, "wall": mm}."""
    return dict(glass=JAR_GLASS, glass_opacity=JAR_GLASS_OPACITY, lid=JAR_LID, label=JAR_LABEL, print=JAR_PRINT,
                powder=JAR_POWDER, wall=JAR_WALL)


def _arc_band(r: float, z0: float, z1: float, deg: float, res: int = 18, facing: float = -90.0) -> pv.PolyData:
    """A thin curved strip on a cylinder of radius r from z0 to z1, `deg` wide and centred on the direction `facing`
    (degrees from +x; -90 is the front, -y): a label stuck on one side of a jar."""
    th = np.radians(np.linspace(facing - deg / 2, facing + deg / 2, res + 1))
    pts = np.array([(r * np.cos(t), r * np.sin(t), z) for t in th for z in (z0, z1)], float)
    faces = []
    for i in range(res):
        a, b, c, d = 2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2
        faces += [4, a, d, c, b]
    return pv.PolyData(pts, np.array(faces)).triangulate().compute_normals(auto_orient_normals=False)


def jar_meshes(d: float, h: float, lid_h: float, fill: float = 0.62, label=(0.14, 0.52), label_deg: float = 110.0,
               res: int = 28) -> dict:
    """One powder jar, base centre at the origin, z up, its label facing -y: {"glass", "powder", "label", "print",
    "lid"} as PolyData. d and h are the glass body's outside diameter and height; the cap (lid_h tall, 2 mm wider)
    sits on top. `fill` is the powder's height as a share of the inside; `label` its band as shares of h."""
    r = d / 2
    glass = _cyl(r, h, 0.0, res=res)
    z_floor = 2.5
    powder = _cyl(r - JAR_WALL, max(0.5, fill * (h - z_floor - 4.0)), z_floor, res=res)
    lab = _arc_band(r + 0.4, label[0] * h, label[1] * h, label_deg)
    zm = (label[0] + label[1]) / 2 * h
    prt = _arc_band(r + 0.7, zm - 0.10 * h, zm + 0.02 * h, label_deg * 0.45)
    lid = _cyl(r + 1.0, lid_h, h, res=res)
    return dict(glass=glass, powder=powder, label=lab, print=prt, lid=lid)


def jar_parts(d: float, h: float, lid_h: float, **kw) -> dict:
    """jar_meshes() with the lab-wide look: {part: (mesh, rgb, opacity)}."""
    m = jar_meshes(d, h, lid_h, **kw)
    return {"glass": (m["glass"], JAR_GLASS, JAR_GLASS_OPACITY), "powder": (m["powder"], JAR_POWDER, 1.0),
            "label": (m["label"], JAR_LABEL, 1.0), "print": (m["print"], JAR_PRINT, 1.0),
            "lid": (m["lid"], JAR_LID, 1.0)}


def tint_sleeve(d: float, h: float, res: int = 28) -> pv.PolyData:
    """A see-through sleeve 1.2 mm outside a jar's glass (label included), base at z = 0: drawn in a tint at
    TINT_OPACITY and faded in, it tints the whole jar body while the cap stays black."""
    return _cyl(d / 2 + 1.2, h - 0.5, 0.25, res=res)


def tinted(rgb, tint, k: float) -> tuple:
    """A colour k (0-1) of the way from rgb to tint: for sc.color[name] in a step's update."""
    k = min(max(float(k), 0.0), 1.0)
    return tuple(float(a + (b - a) * k) for a, b in zip(rgb, tint))


def pulse(t: float, t_on: float, t_off: float, ramp: float = 0.5) -> float:
    """0 before t_on, up to 1 over `ramp` s, 1 until t_off - ramp, back to 0 at t_off (smoothstep ramps): a tint's
    and its legend's strength at time t."""
    if t <= t_on or t >= t_off:
        return 0.0
    k = min(1.0, (t - t_on) / ramp, (t_off - t) / ramp)
    return k * k * (3.0 - 2.0 * k)


def draw_legend(img, title: str, items, alpha: float = 1.0, s: float = 1.0, corner: str = "tr", top: float = 46.0):
    """A legend box on a PIL image: a bold title, then a colour swatch and a line of text per item [(rgb, text)].
    corner "tr" puts it top right under the step label, "tl" top left under the title; `top` is its top edge in
    720p pixels (scaled by s). Returns the image."""
    if alpha <= 0.02 or not items:
        return img
    from PIL import ImageDraw
    from scene import font
    d = ImageDraw.Draw(img, "RGBA")
    W, _ = img.size
    al = int(255 * min(alpha, 1.0))
    ft, fi = font(14.5 * s, bold=True), font(13.5 * s)
    pad, sw, lh = 9 * s, 15 * s, 21 * s
    tw = max([d.textlength(title, font=ft)] + [d.textlength(t, font=fi) + sw + 9 * s for _, t in items])
    w = tw + 2 * pad
    h = 2 * pad + (21 * s if title else 0) + len(items) * lh - 4 * s
    x0 = W - 10 * s - w if corner == "tr" else 10 * s
    y0 = top * s
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 6 * s, fill=(255, 255, 255, int(238 * min(alpha, 1.0))),
                        outline=(120, 124, 130, al))
    y = y0 + pad
    if title:
        d.text((x0 + pad, y - 1 * s), title, font=ft, fill=(20, 20, 24, al))
        y += 21 * s
    for rgb, text in items:
        c = tuple(int(round(255 * v)) for v in rgb[:3])
        d.rounded_rectangle((x0 + pad, y + 1.5 * s, x0 + pad + sw, y + 1.5 * s + sw), 3 * s, fill=c + (al,),
                            outline=(60, 60, 66, al))
        d.text((x0 + pad + sw + 9 * s, y), text, font=fi, fill=(20, 20, 24, al))
        y += lh
    return img


def use_legend(sc) -> None:
    """Let a Scene draw a legend: in a step's update set sc.legend = dict(title=..., items=[(rgb, text)], alpha=0-1,
    corner="tr") (None for none), and every frame shows it over the usual text. Wraps this scene's overlay only;
    calling it twice is harmless; no legend with VIZ3D_CLEAN. A tint and its legend, in a chapter script:

        P.use_legend(sc)
        def up(u):                                   # inside a step of `secs` seconds
            k = P.pulse(u * secs, 0.0, secs, ramp=0.6)
            sc.color[name] = P.tinted(P.JAR_POWDER, P.TINT["amber"], k)
            sc.legend = dict(title="Tinted for now", items=[(P.TINT["amber"], "the LPBF cut, < 63 um")], alpha=k)
    """
    if getattr(sc, "_legend_on", False):
        return
    import scene as S
    base = sc.overlay
    sc.legend = None

    def overlay(img, scale, anchors):
        img = base(img, scale, anchors)
        lg = getattr(sc, "legend", None)
        if lg and not S.CLEAN:
            draw_legend(img, lg.get("title", ""), lg.get("items", ()), lg.get("alpha", 1.0), max(scale, 0.80),
                        lg.get("corner", "tr"), lg.get("top", 46.0))
        return img
    sc.overlay = overlay
    sc._legend_on = True


def piece_legend(key: str, legends: dict, then=None, corner: str = "tr", top: float = 46.0):
    """For a tour clip (tour.py plays an Instrument): a draw(sc, img, s) for instruments_lab.PLOTS[f"instruments/{key}"]
    that shows legends[piece] = (title, [(rgb, text)]) while that piece shows, at its fade joint's value (the tint
    sleeves are such a piece: Joint("fade"), v0 = 0, faded in and out by the actions). `then`: a drawer that already
    sits in PLOTS for that clip, called first."""
    def draw(sc, img, s):
        if then is not None:
            then(sc, img, s)
        for piece, (title, items) in legends.items():
            g = f"{key}:{piece}"
            a = max((sc.alpha.get(n, 0.0) for n, gg in sc.group_of.items() if gg == g), default=0.0)
            if a > 0.02:
                draw_legend(img, title, items, min(1.0, a), s, corner, top)
    return draw
