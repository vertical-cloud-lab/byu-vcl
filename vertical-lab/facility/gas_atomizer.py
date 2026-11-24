"""A lab/pilot-scale close-coupled vacuum induction-melting inert-gas atomizer, drawn for the facility render.

**Ours, sized after one published plant, not a vendor's CAD.** The only lab/pilot close-coupled atomizer we found with
a published data sheet and a dimensioned drawing is Phoenix Scientific Industries' HERMIGA 100/10 VI: 6.0 x 5.1 x 5.7 m
overall, 5 t, a 1.5 L crucible (about 10 kg of steel) atomized at 2-4 kg/min, 100 kVA, argon up to 6 kg/min at 20 bar
or more, about 70 L/min of cooling water; PSI sells the series for 10-25 kg of powder a run. Read off its drawing
(about +-10 %): the upper deck at about 3.5 m, a horizontal melt chamber about 1.3-1.4 m across on it with a side door
and its top at about 5.3 m, the tower about 1.1 m wide with a 1.75 m cylindrical section and a cone below, a cyclone
beside it, the powder in cans at floor level, a control cabinet about 1.45 m wide on the deck. Everything else here
(the stair, the rails, the pump stand, the induction power supply on the floor, the argon bundle rack, the filter and
the stack) is drawn to the class, not to that drawing. README.md has the sources.

Rigid bodies: all "body". Roles the animation drives: "glow_melt" (the chamber's view-ports), "glow_spray" (the
tower's) and "beacon" (the stack light on the deck rail). Thin rails are role "detail" (left out at a distance).
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

from assets import Asset, Part

SIZE = dict(
    deck_z=3500.0, deck_w=4600.0, deck_d=3500.0, deck_t=150.0,       # the upper deck (x, y), top at deck_z
    chamber_d=1350.0, chamber_l=1800.0,                              # horizontal melt chamber on the deck, axis along x
    tower_d=1100.0, tower_cyl=1750.0, cone_bottom=650.0,             # atomization tower under the deck
    can_d=460.0, can_h=560.0,                                        # powder cans on the floor
    cyclone_d=760.0, cyclone_top=3000.0, cyclone_cyl=1100.0, cyclone_cone_bottom=900.0,
    filter=(1200.0, 1000.0, 2500.0),                                 # cartridge filter: w, d, h
    cabinet=(1450.0, 600.0, 1900.0),                                 # control cabinet on the deck (HERMIGA drawing)
    psu=(1200.0, 800.0, 1900.0),                                     # medium-frequency induction supply, on the floor
)

WHITE = (0.88, 0.89, 0.90)
STEEL = (0.70, 0.72, 0.75)
BLUE = (0.18, 0.33, 0.55)
DECK = (0.30, 0.31, 0.33)
YELLOW = (0.95, 0.76, 0.10)
DARK = (0.16, 0.17, 0.19)
GLASS_OFF = (0.20, 0.22, 0.25)


def _box(x0, y0, z0, x1, y1, z1):
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))).triangulate()


def _cyl(c, d, r, h, res=48):
    return pv.Cylinder(center=c, direction=d, radius=r, height=h, resolution=res, capping=True).triangulate()


def _cone(top_c, r_top, r_bot, h, res=48):
    """A frustum from r_top at top_c down to r_bot, h below."""
    x, y, z = top_c
    th = np.linspace(0, 2 * math.pi, res, endpoint=False)
    top = np.c_[x + r_top * np.cos(th), y + r_top * np.sin(th), np.full(res, z)]
    bot = np.c_[x + r_bot * np.cos(th), y + r_bot * np.sin(th), np.full(res, z - h)]
    pts = np.vstack([top, bot, [[x, y, z]], [[x, y, z - h]]])
    faces = []
    for i in range(res):
        j = (i + 1) % res
        faces += [3, i, j, res + j, 3, i, res + j, res + i]
        faces += [3, 2 * res, j, i, 3, 2 * res + 1, res + i, res + j]
    return pv.PolyData(pts, np.array(faces)).triangulate()


def _tube(pts, r, res=20):
    return pv.Spline(np.asarray(pts, float), 60).tube(radius=r, n_sides=res, capping=True).triangulate()


def _rail(x0, y0, x1, y1, z, h=1100.0, r=24.0):
    """A handrail along a deck edge: top and knee rails, posts about every 1.5 m (48 mm tube)."""
    out = []
    L = math.hypot(x1 - x0, y1 - y0)
    d = np.array([x1 - x0, y1 - y0, 0.0]) / max(L, 1e-6)
    mid = np.array([(x0 + x1) / 2, (y0 + y1) / 2, 0.0])
    for zz in (z + h, z + h / 2):
        out.append(_cyl(tuple(mid + [0, 0, zz]), tuple(d), r, L, 12))
    n = max(2, int(L // 1500) + 1)
    for i in range(n):
        p = np.array([x0, y0, 0.0]) + d * L * i / (n - 1)
        out.append(_cyl((p[0], p[1], z + h / 2), (0, 0, 1), r, h, 12))
    return out


def _dish(c, axis, r, depth, res=48):
    """A dished head (a flattened half sphere) of radius r and depth `depth`, its rim at c, bulging along `axis`."""
    s = pv.Sphere(radius=r, center=(0, 0, 0), theta_resolution=res, phi_resolution=res // 2, end_phi=90)
    s = s.scale((1.0, 1.0, depth / r), inplace=False)
    a = np.asarray(axis, float)
    a /= np.linalg.norm(a)
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(z, a)
    if np.linalg.norm(v) > 1e-9:
        ang = math.degrees(math.acos(float(np.clip(np.dot(z, a), -1, 1))))
        s = s.rotate_vector(v, ang, inplace=False)
    elif a[2] < 0:
        s = s.rotate_x(180, inplace=False)
    return s.translate(c, inplace=False).triangulate()


def gas_atomizer() -> Asset:
    s = SIZE
    a = Asset("gas_atomizer")
    add = lambda m, c, spec=0.25, amb=0.22, role="solid", rigid="body": a.parts.append(  # noqa: E731
        Part(m, c, spec, amb, role, rigid))
    zt, W, D, dt = s["deck_z"], s["deck_w"], s["deck_d"], s["deck_t"]
    # --- the deck on six columns, its beams, rails and a stair up its west side
    for x in (-W / 2 + 120, 0.0, W / 2 - 120):
        for y in (-D / 2 + 120, D / 2 - 120):
            add(_box(x - 100, y - 100, 0, x + 100, y + 100, zt - dt), BLUE, 0.3)
    for y in (-D / 2 + 120, D / 2 - 120):
        add(_box(-W / 2, y - 100, zt - dt - 300, W / 2, y + 100, zt - dt), BLUE, 0.3)
    for x in (-W / 2 + 120, W / 2 - 120):
        add(_box(x - 100, -D / 2, zt - dt - 300, x + 100, D / 2, zt - dt), BLUE, 0.3)
    add(_box(-W / 2, -D / 2, zt - dt, W / 2, D / 2, zt), DECK, 0.15)
    for seg in [(-W / 2, D / 2, W / 2, D / 2), (W / 2, -D / 2, W / 2, D / 2), (-W / 2, -D / 2, W / 2, -D / 2),
                (-W / 2, -D / 2, -W / 2, -D / 2 + 900)]:
        for m in _rail(*seg, zt):
            add(m, YELLOW, 0.2, role="detail")
    sx0, sx1 = -W / 2 - 1000, -W / 2 - 100
    run_y0, run_y1 = D / 2 + 2700, -D / 2 + 1200
    n = int(zt // 220)
    for k in range(1, n + 1):
        z = k * zt / n
        y = run_y0 + (run_y1 - run_y0) * k / n
        add(_box(sx0, y - 130, z - 40, sx1, y + 130, z), DECK, 0.15)
    for x in (sx0 - 30, sx1 + 30):
        add(_tube([(x, run_y0, 120), (x, run_y1, zt - 100)], 40, 8), BLUE, 0.3)
        add(_tube([(x, run_y0, 1100), (x, run_y1, zt + 1000)], 24, 8), YELLOW, 0.2, role="detail")
    add(_box(sx0, run_y1 - 500, zt - dt, -W / 2, run_y1 + 130, zt), DECK, 0.15)
    # --- the melt chamber: a horizontal vessel on two saddles, its door (a dished head) at the west end
    R, L = s["chamber_d"] / 2, s["chamber_l"]
    zc = zt + 280 + R
    for x in (-L / 3, L / 3):
        add(_box(x - 120, -R * 0.8, zt, x + 120, R * 0.8, zc - R * 0.55), BLUE, 0.3)
    add(_cyl((0, 0, zc), (1, 0, 0), R, L, 72), WHITE, 0.35)
    add(_dish((L / 2, 0, zc), (1, 0, 0), R, 320), WHITE, 0.35)
    for x in (-L / 2 + 30, L / 2 - 30):
        add(_cyl((x, 0, zc), (1, 0, 0), R + 60, 90, 72), STEEL, 0.5)
    add(_dish((-L / 2 - 60, 0, zc), (-1, 0, 0), R + 40, 300), STEEL, 0.45)        # the door
    add(_cyl((-L / 2 - 380, 0, zc), (1, 0, 0), 110, 60, 32), DARK, 0.3)            # its hand wheel
    for z in (zc - R * 0.6, zc + R * 0.6):
        add(_box(-L / 2 - 120, R * 0.55, z - 50, -L / 2 + 40, R * 0.85, z + 50), STEEL, 0.5)   # hinges
    for xv in (-L * 0.18, L * 0.18):                                                # view-ports, front (-y)
        add(_cyl((xv, -R - 40, zc + R * 0.25), (0, 1, 0), 105, 110, 32), STEEL, 0.5)
        add(_cyl((xv, -R - 100, zc + R * 0.25), (0, 1, 0), 72, 10, 32), GLASS_OFF, 0.0, 0.9, "glow_melt")
    add(_cyl((0, 0, zc + R + 160), (0, 0, 1), 160, 320, 32), STEEL, 0.5)            # the top port (charging)
    # the control cabinet on the deck (HERMIGA's drawing: about 1.45 m wide), its screen to the stair
    cw, cd, ch = s["cabinet"]
    add(_box(-W / 2 + 250, D / 2 - 250 - cd, zt, -W / 2 + 250 + cw, D / 2 - 250, zt + ch), (0.86, 0.87, 0.88), 0.2)
    add(_box(-W / 2 + 450, D / 2 - 250 - cd - 4, zt + ch - 700, -W / 2 + 1000, D / 2 - 250 - cd, zt + ch - 300),
        DARK, 0.6)
    # vacuum line down to the pump stand on the floor, east
    add(_tube([(L / 2 + 250, R * 0.3, zc), (W / 2 + 400, R * 0.3, zc), (W / 2 + 900, D / 2 - 600, 1300)], 95, 24),
        STEEL, 0.5)
    add(_box(W / 2 + 400, D / 2 - 1300, 0, W / 2 + 1500, D / 2, 900), (0.34, 0.45, 0.60), 0.3)
    add(_cyl((W / 2 + 950, D / 2 - 650, 1150), (1, 0, 0), 200, 900, 32), (0.34, 0.45, 0.60), 0.3)
    # --- the atomization tower under the deck, its cone, valve and can
    rt = s["tower_d"] / 2
    z_top = zt - dt - 40
    z_cyl = z_top - s["tower_cyl"]
    add(_cyl((0, 0, (z_top + z_cyl) / 2), (0, 0, 1), rt, s["tower_cyl"], 72), WHITE, 0.35)
    add(_cone((0, 0, z_cyl), rt, 140, z_cyl - s["cone_bottom"]), WHITE, 0.35)
    for zz in (z_cyl + 40, z_top - 50):
        add(_cyl((0, 0, zz), (0, 0, 1), rt + 55, 90, 72), STEEL, 0.5)
    add(_cyl((0, 0, s["cone_bottom"] - 70), (0, 0, 1), 130, 140, 32), STEEL, 0.5)
    add(_cyl((0, 0, s["can_h"] / 2 + 20), (0, 0, 1), s["can_d"] / 2, s["can_h"] - 40, 48), STEEL, 0.55)
    add(_box(-360, -360, 0, 360, 360, 50), DARK, 0.2)
    t = math.radians(-70)
    c = (rt * math.cos(t), rt * math.sin(t), z_cyl + 1000)
    d = (math.cos(t), math.sin(t), 0.0)
    add(_cyl(tuple(np.add(c, np.multiply(d, 50))), d, 120, 100, 32), STEEL, 0.5)
    add(_cyl(tuple(np.add(c, np.multiply(d, 105))), d, 82, 10, 32), GLASS_OFF, 0.0, 0.9, "glow_spray")
    # --- the cyclone (east of the tower, under the deck's edge) with its can, the duct, the filter and the stack
    cx, cy = rt + 1150, -D / 2 + 650
    rc = s["cyclone_d"] / 2
    zc0 = s["cyclone_top"] - s["cyclone_cyl"]
    add(_cyl((cx, cy, (s["cyclone_top"] + zc0) / 2), (0, 0, 1), rc, s["cyclone_cyl"], 48), WHITE, 0.35)
    add(_cone((cx, cy, zc0), rc, 110, zc0 - s["cyclone_cone_bottom"]), WHITE, 0.35)
    add(_cyl((cx, cy, s["cyclone_cone_bottom"] - 150), (0, 0, 1), 140, 300, 32), STEEL, 0.55)
    add(_cyl((cx, cy, 280), (0, 0, 1), 230, 480, 32), STEEL, 0.55)
    add(_tube([(rt * 0.6, -rt * 0.6, z_cyl + 250), (cx - rc - 250, cy, z_cyl + 500),
               (cx - rc, cy, s["cyclone_top"] - 300)], 120, 24), STEEL, 0.5)
    fw, fd, fh = s["filter"]
    fx, fy = W / 2 + 1150, -D / 2 + 300
    add(_box(fx - fw / 2, fy - fd / 2, 0, fx + fw / 2, fy + fd / 2, fh), (0.80, 0.82, 0.84), 0.25)
    add(_tube([(cx, cy, s["cyclone_top"]), (cx, cy, s["cyclone_top"] + 400), (fx, fy, fh + 350), (fx, fy, fh)], 110,
              24), STEEL, 0.5)
    add(_cyl((fx + fw / 2 - 220, fy, fh + 1500), (0, 0, 1), 140, 3000, 32), STEEL, 0.5)    # exhaust stack
    # --- on the floor: the induction power supply, the argon bundle rack and the gas train
    px, py, ph = s["psu"]
    add(_box(-W / 2 + 200, -D / 2 - 300 - py, 0, -W / 2 + 200 + px, -D / 2 - 300, ph), (0.85, 0.86, 0.87), 0.2)
    add(_box(-W / 2 + 350, -D / 2 - 300 - py - 4, ph - 650, -W / 2 + 800, -D / 2 - 300 - py, ph - 300), DARK, 0.6)
    add(_tube([(-W / 2 + 200 + px / 2, -D / 2 - 300, ph - 200), (-W / 2 + 900, -D / 2 + 200, zt + 100),
               (-L / 4, -R * 0.4, zc - R * 0.6)], 60, 16), (0.60, 0.25, 0.15), 0.3)    # the coil leads (copper)
    gx, gy = 300.0, -D / 2 - 1300
    add(_box(gx, gy - 450, 0, gx + 2200, gy + 450, 110), DARK, 0.2)
    for i in range(5):
        for j in range(2):
            add(_cyl((gx + 230 + i * 420, gy - 200 + j * 400, 110 + 850), (0, 0, 1), 112, 1700, 24),
                (0.25, 0.45, 0.30), 0.35)
    for x in (gx, gx + 2200):
        add(_box(x - 30, gy - 470, 0, x + 30, gy + 470, 2000), BLUE, 0.3)
    add(_tube([(gx + 2200, gy, 1500), (rt + 200, -rt - 100, 1500), (rt * 0.5, -rt * 0.5, z_cyl + 600)], 28, 12),
        STEEL, 0.6)
    # --- the stack light on the deck's front rail
    add(_cyl((W / 2 - 300, -D / 2 + 70, zt + 1350), (0, 0, 1), 25, 500, 12), DARK, 0.3)
    add(_cyl((W / 2 - 300, -D / 2 + 70, zt + 1700), (0, 0, 1), 100, 240, 24), (0.62, 0.64, 0.67), 0.0, 0.9, "beacon")
    return a


def footprint() -> tuple[float, float, float, float]:
    """x0, x1, y0, y1 of everything on the floor, model frame (the tower's axis at the origin)."""
    s = SIZE
    return (-s["deck_w"] / 2 - 1100, s["deck_w"] / 2 + 1800, -s["deck_d"] / 2 - 1800, s["deck_d"] / 2 + 2800)
