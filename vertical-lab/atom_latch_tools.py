"""Tools for the latch and container clips (atom_latch.py, atom_container.py; PR #353, #303). No scene is built here.

**Why the latch is redrawn in the clip.** repowder/model.py's third-pass latch (``latch_geom``, ``hood_parts``) puts the
lever's pivot at its top and the loop on its own joint, as the footage shows (T4 5:29.5-5:41). Its parts cannot move as
drawn, though. FCL on the model's meshes (``python3 atom_latch_tools.py``) finds, with the bolt back:

* the lever reaching 14 mm above its pivot: opened past ~30 deg that end swings into the base plate, 48 mm deep at 90
  deg, 30 mm at 150 deg;
* the loop's legs at x = +-21.5 mm, inside the lever's flanges and on top of the base's side flanges (x +-19.5..22): they
  run through the base's flanges and graze the pivot pin even shut;
* the keeper's ledge drawn *above* the cross bar (``hook`` is 2 mm under it), so the loop would pull the bar away from
  it: a draw latch pulls the lid down only if the bar bears on a ledge *under* it.

So the clip hides those four meshes (lever, loop, keeper, pin) and draws them again here on the model's own joints (the
same pivots, ``M.joint_matrix``): the lever ends at its pivot in a rounded knuckle, the loop's legs run *outside* the
lever's flanges (x +-30.5) with their pins through the flanges, the keeper's ledge is under the bar with a 3 mm lip in
front, the pin is 53 mm long, and the lever's flanges have holes for the bolt's rod. Ours; model.py should take them.

**What the loop does** (worked out here, it is not in the footage frame by frame): taut, the bar sits on the keeper's
ledge. As the lever opens, its pivot first draws away from the hook (dead centre, ``M.latch_toggle``: 18 deg, +0.60 mm),
then comes back towards it; once the pivot-to-hook distance is less than the loop's length the loop is slack and its bar
rides up the keeper's plate (a rigid loop cannot keep its bar on the hook). Lifted off and let go, the loop falls onto
the lever's web, which faces the lid while the lever stands up, and lies over the lever when it is folded down: "it
dangles, hanging down over the lever" (T4 5:08, 5:29.5).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _model():
    if "repowder_model" in sys.modules:
        return sys.modules["repowder_model"]
    import importlib.util
    spec = importlib.util.spec_from_file_location("repowder_model", HERE / "repowder" / "model.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["repowder_model"] = mod
    spec.loader.exec_module(mod)
    return mod


M = _model()
# Everything here is worked out in the lid assembly's own frame (the latch on its front face, y = -135, as the third
# pass drew it) and carried onto the machine with M.LID_TURN_T: since commit e3b1428 the lid assembly is turned 90 deg
# about the furnace axis (hinged on the left, the latch on the housing's right face, the bolt running back into the
# cabinet). M.joint_matrix / joint_world answer in the turned frame; JL / JO below are the same joints in the lid's.
TURN = np.asarray(M.LID_TURN_T, float)
TURN_INV = np.linalg.inv(TURN)
G = M.latch_geom(turned=False)
LX = float(G["x"])
YF = float(G["yface"])                      # the housing's flat, y = -135
PIV = np.asarray(G["pivot"], float)         # the lever's pivot (72, -150, 1330)
Q0 = np.asarray(G["loop_pivot"], float)     # the loop's pivot on the lever, shut (72, -146, 1314)
HOOK = np.asarray(G["hook"], float)         # the bar's seat on the keeper (72, -147, 1369)
LOOP_L = float(np.linalg.norm(HOOK - Q0))   # 55.0 mm, pivot to bar
BAR_R, LEG_R = 2.4, 2.2
LEG_X = 30.5                                # the legs, either side of the lever's centre (outside its flanges, 26)
BAR_HALF = 33.0
PLATE_Y = -143.0                            # the keeper plate's face (model: k[1] - 3)
LEVER_Z0 = 1194.0                           # the lever's free end (the toe), 2 mm over the hold-down foot (z 1192)
TOE_Z = LEVER_Z0 + 3.0
TOE_ARM = float(PIV[2] - TOE_Z)             # 133 mm from the pivot to where it is pulled
WEB_Y = (-157.0, -154.5)
FL_Y = (-157.0, -141.0)
FL_X = (23.5, 26.0)
BOLT_Y, BOLT_Z = YF - 11.0, float(G["bolt_z"])
WEB_TOP_DROP = 12.0                         # the web ends this far under the pivot: higher, it swings into the base's
                                            # flanges past ~80 deg (FCL)
PRELOAD = 0.30                              # mm the loop is set short of the shut pivot-to-hook distance (ours,
                                            # assumed: the adjuster's "just tight enough to seal", 178_sop Furnace 9)


# ---------------------------------------------------------------------------------------------- meshes
def _cq():
    import cadquery as cq
    return cq


def _box(x0, x1, y0, y1, z0, z1):
    cq = _cq()
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _cylx(x0, x1, y, z, r):
    cq = _cq()
    return cq.Solid.makeCylinder(r, x1 - x0, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))


def _cyl(p0, d, r, h):
    cq = _cq()
    d = np.asarray(d, float) / np.linalg.norm(d)
    return cq.Solid.makeCylinder(r, h, cq.Vector(*map(float, p0)), cq.Vector(*map(float, d)))


def _tess(shape, tol=0.12):
    return M.tess(shape, tol)


def latch_meshes() -> dict:
    """{name: (pv mesh, rgb, model group)} of the redrawn latch, model frame, shut (joint values 0)."""
    lx = LX
    py, pz = float(PIV[1]), float(PIV[2])
    # the lever: a channel, web outside, flanges wrapping the base's side flanges; it ends at the pivot in a knuckle
    lev = _box(lx - FL_X[1], lx + FL_X[1], WEB_Y[0], WEB_Y[1], LEVER_Z0, pz - WEB_TOP_DROP)   # the web stops short of
    for s in (-1, 1):
        a, b = sorted((lx + s * FL_X[0], lx + s * FL_X[1]))
        lev = lev.fuse(_box(a, b, FL_Y[0], FL_Y[1], LEVER_Z0 + 3.0, pz)).fuse(_cylx(a, b, py, pz, 8.0))
    lev = lev.fuse(_box(lx - FL_X[1], lx + FL_X[1], WEB_Y[0] - 8.0, WEB_Y[1], LEVER_Z0, LEVER_Z0 + 6.0))   # the toe
    lev = lev.cut(_cylx(lx - 40, lx + 40, py, pz, 3.3))                       # the pivot pin's holes
    lev = lev.cut(_cylx(lx - 40, lx + 40, float(Q0[1]), float(Q0[2]), 2.3))  # the loop's pins
    lev = lev.cut(_cylx(lx - 40, lx + 40, BOLT_Y, BOLT_Z, 3.5))              # the bolt's rod (shut: it locks the lever)
    lev = lev.clean()
    # the loop: legs outside the flanges, pins into them, the cross bar, and the adjuster's lock nuts (ours)
    u = (HOOK - Q0) / LOOP_L
    parts = []
    for s in (-1, 1):
        x = lx + s * LEG_X
        p0 = np.array([x, Q0[1], Q0[2]])
        parts.append(_cyl(p0, u, LEG_R, LOOP_L))
        parts.append(_cylx(min(x, lx + s * 23.6), max(x, lx + s * 23.6), float(Q0[1]), float(Q0[2]), 2.0))  # pin
        parts.append(_cylx(x - 2.5, x + 2.5, float(Q0[1]), float(Q0[2]), 3.6))                             # eye
        parts.append(_cyl(p0 + u * (LOOP_L - 12.0), u, 3.4, 4.5))                                       # lock nut
    parts.append(_cylx(lx - BAR_HALF, lx + BAR_HALF, float(HOOK[1]), float(HOOK[2]), BAR_R))
    loop = parts[0]
    for p in parts[1:]:
        loop = loop.fuse(p)
    loop = loop.clean()
    # the keeper on the lid: the model's plate and screws, with the bar's ledge under the bar and a lip in front
    zb = float(HOOK[2]) - BAR_R
    kp = _box(lx - 26, lx + 26, PLATE_Y, -140.0, 1363.0, 1409.0)
    kp = kp.fuse(_box(lx - 24, lx + 24, -153.0, PLATE_Y, zb - 5.0, zb))
    kp = kp.fuse(_box(lx - 24, lx + 24, -153.0, -150.6, zb, zb + 3.4))
    for s in (-1, 1):
        kp = kp.fuse(_cyl((lx + s * 19, PLATE_Y, 1400.0), (0, -1, 0), 3.5, 2.0))
    kp = kp.clean()
    pin = _cylx(lx - 26.5, lx + 26.5, py, pz, 3.0).fuse(_cylx(lx - 27.5, lx - 26.5, py, pz, 4.5)) \
        .fuse(_cylx(lx + 26.5, lx + 27.5, py, pz, 4.5))
    out = {"latch_lever": (_tess(lev), M.STEEL, "latch_lever"),
           "latch_loop": (_tess(loop), M.STEEL_DK, "latch_loop"),
           "latch_keeper": (_tess(kp), M.STEEL, "hood"),
           "latch_pin": (_tess(pin), M.STEEL_DK, "furnace")}
    return {k: (m.transform(TURN, inplace=False), c, g) for k, (m, c, g) in out.items()}   # onto the machine


# ---------------------------------------------------------------------------------------------- the loop's motion
def lever_deg(v: float) -> float:
    return float(v) * M.LATCH_OPEN_DEG


def JL(v: float) -> np.ndarray:
    """The lever's joint in the lid's own frame (about -x through its pivot), v = 0..1 of 150 deg."""
    return M._hinge_m(PIV, (-1.0, 0.0, 0.0), M.LATCH_OPEN_DEG * float(v))


def JO(t: float) -> np.ndarray:
    """The loop's joint in the lever's frame, lid's own frame, t = 0..1 of 180 deg (any sign)."""
    return M._hinge_m(Q0, (-1.0, 0.0, 0.0), M.LOOP_OPEN_DEG * float(t))


def turn(p) -> np.ndarray:
    """A lid-frame point -> the model frame."""
    return (TURN @ np.r_[np.asarray(p, float)[:3], 1.0])[:3]


def loop_pivot(v: float) -> np.ndarray:
    """The loop's pivot (lid frame) with the lever at v (0..1 of its 150 deg)."""
    return (JL(v) @ np.r_[Q0, 1.0])[:3]


def _loop_value_for(v: float, bar: np.ndarray) -> float:
    """The 'loop' joint value (0..1 of 180 deg, any sign) that puts the bar's centre at `bar` (same distance as the
    loop) with the lever at v."""
    Ml = JL(v)
    Q = (Ml @ np.r_[Q0, 1.0])[:3]
    d_rest = HOOK - Q0
    d_now = np.linalg.inv(Ml[:3, :3]) @ (bar - Q)
    a0 = math.atan2(d_rest[2], d_rest[1])
    a1 = math.atan2(d_now[2], d_now[1])
    deg = math.degrees(a0 - a1)
    return deg / M.LOOP_OPEN_DEG


def loop_free_len() -> float:
    return LOOP_L - PRELOAD


def ride(v: float) -> tuple[float, float]:
    """(loop value, draw mm) with the loop hooked or riding the keeper: taut on the ledge while the pivot-to-hook
    distance is at least the loop's set length (the draw is how far past it: the seal's extra squeeze, or the loop's
    stretch), else slack, the bar slid up the keeper's plate (y = HOOK y) to where the loop reaches."""
    Q = loop_pivot(v)
    d = float(np.linalg.norm(HOOK - Q))
    Lf = loop_free_len()
    if d >= Lf - 1e-9:
        return _loop_value_for(v, HOOK), d - Lf
    dy = HOOK[1] - Q[1]
    z = Q[2] + math.sqrt(max(Lf * Lf - dy * dy, 0.0))
    bar = np.array([HOOK[0], HOOK[1], max(z, HOOK[2])])
    bar = Q + (bar - Q) / np.linalg.norm(bar - Q) * LOOP_L
    return _loop_value_for(v, bar), 0.0


def draw_mm(v: float) -> float:
    """Pivot-to-hook distance less the shut one: + draws the lid down (the over-centre curve)."""
    return float(np.linalg.norm(HOOK - loop_pivot(v)) - np.linalg.norm(HOOK - Q0))


ON_WEB_DEG = -162.0                         # the loop lying over the lever's web (loop joint, deg): the bar 2.7 mm off it


def on_web() -> float:
    return ON_WEB_DEG / M.LOOP_OPEN_DEG


def theta_taut() -> float:
    """The lever angle (deg) below which the loop is taut on the keeper (closing: where it first bears)."""
    Lf = loop_free_len()
    for d in np.linspace(M.LATCH_OPEN_DEG, 0.0, 3001):
        if np.linalg.norm(HOOK - loop_pivot(d / M.LATCH_OPEN_DEG)) >= Lf:
            return float(d)
    return 0.0


def toggle_curve(n: int = 151) -> list[tuple[float, float]]:
    return [(float(d), draw_mm(d / M.LATCH_OPEN_DEG)) for d in np.linspace(0.0, M.LATCH_OPEN_DEG, n)]


# ---------------------------------------------------------------------------------------------- grasps (model frame)
def lever_grasp(alpha_deg: float = 35.0, z_c: float = 1216.0, y_c: float = -155.0) -> np.ndarray:
    """The 2F-85 across the lever's flanges near its free end (pads on their outer faces, x = 46 / 98), approaching
    in and up at alpha from level; model frame, lever shut. Fingers close along x."""
    a = math.radians(alpha_deg)
    z = np.array([0.0, math.cos(a), math.sin(a)])
    x = np.array([1.0, 0.0, 0.0])
    y = np.cross(z, x)
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2], Mx[:3, 3] = x, y, z, (LX, y_c, z_c)
    return Mx


def legs_grasp(s: float = 26.0, back: float = 15.5, alpha_deg: float = -40.0) -> np.ndarray:
    """The 2F-85 across the loop's two legs from outside (x = LX +- 32.7), s mm up them from the pivot, approaching
    along +y (loop shut frame), the TCP `back` mm in front of the legs; model frame, loop as built. Fingers along x."""
    u = (HOOK - Q0) / LOOP_L
    p = Q0 + u * s
    a = math.radians(alpha_deg)                # in and down: the hand stands out and above the face, clear of the
    z = np.array([0.0, math.cos(a), math.sin(a)])   # chamber's top under the latch (the lid assembly turned)
    x = np.array([1.0, 0.0, 0.0])
    y = np.cross(z, x)
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2], Mx[:3, 3] = x, y, z, p - z * back
    return Mx


def close_for_gap(gap_mm: float) -> float:
    """The 2F-85 closure (0..1) whose pads stand gap_mm apart."""
    import ur_arm
    lo, hi = 0.0, 1.0
    for _ in range(40):
        c = (lo + hi) / 2
        Gf = ur_arm.gripper_fk(c)
        l = Gf["left_finger_tip"] @ np.array([-ur_arm._PAD[0], 0, ur_arm._PAD[1], 1.0])
        r = Gf["right_finger_tip"] @ np.array([ur_arm._PAD[0], 0, ur_arm._PAD[1], 1.0])
        if l[0] - r[0] > gap_mm:
            lo = c
        else:
            hi = c
    return (lo + hi) / 2


# ---------------------------------------------------------------------------------------------- the inset
def inset(img, deg: float, draw: float, squeeze: float, taut: bool, scale: float = 1.0, title="Over centre"):
    """Draw, on a PIL image, the over-centre curve (draw vs lever angle) with the lever's angle marked, and a section
    of the lid's seam with the O-ring squeezed by `squeeze` mm (schematic). Bottom right, above the caption."""
    from PIL import ImageDraw
    from scene import font
    W, H = img.size
    s = max(scale, 0.8)
    d = ImageDraw.Draw(img, "RGBA")
    bw, bh = 336 * s, 150 * s
    x0, y0 = W - bw - 14 * s, H - bh - 120 * s
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 6 * s, fill=(255, 255, 255, 228), outline=(150, 156, 164, 255))
    f = font(11.5 * s)
    fb = font(12 * s, bold=True)
    # the curve
    px0, py0, pw, ph = x0 + 32 * s, y0 + 24 * s, 150 * s, 92 * s
    d.text((x0 + 8 * s, y0 + 5 * s), title, font=fb, fill=(20, 20, 24))
    cur = toggle_curve(76)
    lo, hi = -1.0, 0.8
    def P(a, b):
        return px0 + a / M.LATCH_OPEN_DEG * pw, py0 + ph - (b - lo) / (hi - lo) * ph
    d.line([P(0, 0), P(M.LATCH_OPEN_DEG, 0)], fill=(170, 170, 176, 255), width=1)
    pts = [P(a, max(lo, b)) for a, b in cur]
    d.line(pts, fill=(30, 60, 140, 255), width=max(1, int(2 * s)))
    dc = max(cur, key=lambda t: t[1])
    d.text((P(dc[0], dc[1])[0] + 3 * s, P(dc[0], dc[1])[1] - 13 * s), f"dead centre {dc[0]:.0f} deg", font=f,
           fill=(30, 60, 140))
    mx, my = P(min(deg, M.LATCH_OPEN_DEG), max(lo, min(hi, draw_mm(deg / M.LATCH_OPEN_DEG))))
    r = 4.5 * s
    d.ellipse((mx - r, my - r, mx + r, my + r), fill=(200, 40, 30, 255))
    d.text((px0, py0 + ph + 3 * s), "0", font=f, fill=(90, 90, 96))
    d.text((px0 + pw - 22 * s, py0 + ph + 3 * s), "150 deg", font=f, fill=(90, 90, 96))
    d.text((x0 + 6 * s, py0 - 2 * s), "+0.8", font=f, fill=(90, 90, 96))
    d.text((x0 + 6 * s, py0 + ph - 12 * s), "-1.0", font=f, fill=(90, 90, 96))
    d.text((px0 + 2 * s, py0 + ph + 15 * s), "loop pull, mm vs shut", font=f, fill=(90, 90, 96))
    # the seam section: lid flange above, body flange below, the O-ring between (schematic, not to scale)
    sx0, sy0 = x0 + 222 * s, y0 + 26 * s
    d.text((sx0 - 4 * s, y0 + 5 * s), "Seam (schematic)", font=fb, fill=(20, 20, 24))
    k = 9.0 * s                         # px per mm in the section
    dia = 5.0                           # O-ring cross-section, mm (assumed)
    sq = max(0.0, min(squeeze, 1.6))
    hgt = (dia - sq) * k
    wid = dia * k * (dia / max(dia - sq, 1e-3)) ** 0.5
    cx, cy = sx0 + 40 * s, sy0 + 58 * s
    groove = (cx - 30 * s, cy, cx + 34 * s, cy + 26 * s)
    d.rectangle(groove, fill=(165, 168, 174, 255))
    d.rectangle((cx - 30 * s, cy - hgt - 26 * s, cx + 34 * s, cy - hgt), fill=(205, 207, 212, 255))
    d.ellipse((cx - wid / 2, cy - hgt, cx + wid / 2, cy + 0.0 * s), fill=(40, 100, 210, 255))
    d.text((cx + 36 * s, cy - hgt - 22 * s), "lid", font=f, fill=(60, 60, 66))
    d.text((cx + 36 * s, cy + 6 * s), "body", font=f, fill=(60, 60, 66))
    col = (20, 120, 40) if taut else (110, 110, 116)
    d.text((sx0 - 4 * s, y0 + bh - 18 * s), f"squeeze {squeeze:+.2f} mm" if taut else "seal free", font=f, fill=col)
    return img


if __name__ == "__main__":                  # the interference check of the model's latch and of this one
    import fcl

    def obj(mesh):
        m = mesh.triangulate()
        f = np.asarray(m.faces).reshape(-1, 4)[:, 1:].astype(np.int32)
        v = np.asarray(m.points, float)
        b = fcl.BVHModel()
        b.beginModel(len(v), len(f))
        b.addSubModel(v, f)
        b.endModel()
        return fcl.CollisionObject(b, fcl.Transform())

    def hit(a, b):
        return fcl.collide(a, b, fcl.CollisionRequest(), fcl.CollisionResult()) > 0

    ms = M.meshes()
    mine = latch_meshes()
    fixed = {n: obj(ms[n]["whole"]) for n in ("latch_base", "furnace_ext", "latch_foot", "bolt_housing", "hood")}
    fixed["latch_pin"] = obj(mine["latch_pin"][0])
    fixed["latch_keeper"] = obj(mine["latch_keeper"][0])
    lev, loop, bolt = obj(mine["latch_lever"][0]), obj(mine["latch_loop"][0]), obj(ms["latch_bolt"]["whole"])
    print("taut below", round(theta_taut(), 1), "deg; draw at dead centre",
          round(max(t[1] for t in toggle_curve()), 3), "mm; toe arm", TOE_ARM)

    def check(v, lv, b=1.0, tag=""):
        Ml = M.joint_matrix("latch", v)
        Mo = Ml @ M.joint_matrix("loop", lv)
        for o, Mx in ((lev, Ml), (loop, Mo), (bolt, M.joint_matrix("bolt", b))):
            o.setTransform(fcl.Transform(Mx[:3, :3], Mx[:3, 3]))
        bad = [f"lever-{n}" for n, o in fixed.items() if hit(lev, o)] + \
              [f"loop-{n}" for n, o in fixed.items() if hit(loop, o)] + (["loop-lever"] if hit(loop, lev) else []) + \
              (["bolt-lever"] if hit(bolt, lev) else []) + (["bolt-loop"] if hit(bolt, loop) else [])
        print(f"{tag:8s} lever {v * 150:5.1f} loop {lv * 180:7.1f}: {', '.join(bad) or 'clear'}")
    for d in np.linspace(0, 150, 16):
        v = d / 150
        check(v, ride(v)[0], tag="ride")
    for d in np.linspace(0, 150, 7):
        check(d / 150, on_web(), tag="on web")
    check(0.0, 0.0, b=0.0, tag="locked")
