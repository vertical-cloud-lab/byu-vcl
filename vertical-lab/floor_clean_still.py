"""Stills of the floor-cleaning option to try first (#366, #303): a third MiR250 + UR10e, "unit 3: powder", vacuums
the floor along the rePowder's front with a floor squeegee on the 118EXP's wand. The wand's 25 ft conductive hose runs
to the Al-family vacuum at the atomizer's vacuum station (PR #353's two 118EXPs, Al and Cu, here on the lab's floor
plan, west of the machine and behind the dock line). The unit's bonding lead is clipped to a ground stud in the floor.
Unit 1 carries on with transfers at Shuttle 1's opening.

    python3 runner_guard.py slot --label fcstill --mem 4500 -- xvfb-run -a python3 floor_clean_still.py
    -> out/floor_cleaning_still.png (the area), out/floor_cleaning_still_close.png (the squeegee),
       out/collisions/floor_cleaning_still.json (the posed arm and what it holds, checked by collide.Checker)

Models, all the lab's own: atom_base / alloy_atomize (the rePowder; a MiR250 + cabinet + UR10e + 2F-85, as units 1 and
2 are), atom_nilfisk (the 118EXP, the wand with our clamp collar and fin, the hose's position-based dynamics, the
station, pail, extinguisher and sign), sieve_station (the sieving cell's downdraft enclosure), vlm via lab (Shuttle 1).
New here, ours: the floor squeegee (a 14 in head: the 118EXP accessory sheet's floor squeegee 01768800 publishes no
size, and the Ruwac kit's floor tool is 14 in), the 25 ft hose (Ruwac EXP151525CB's length; the lab's is 10 ft), the
bonding lead and its stud, unit 3's orange band, and the layout of the station on the floor plan
(floor_cleaning.VAC_STATION). Notes: notes/floor_cleaning.md.
"""
from __future__ import annotations

import json
import math
import os

import numpy as np
import pyvista as pv

import atom_base as AB
import alloy_atomize as AA
import atom_nilfisk as N
import floor_cleaning as FC
import props as P
import ur_arm
from scene import OUT, R, Scene, T

NAME = "floor_cleaning_still"
CLIP = "floor_cleaning_clip"
TITLE = "Vertical cloud lab: unit 3 vacuums the floor round the atomizer"
FLOOR_C = (0.93, 0.93, 0.92)
TAPE_Y = (0.95, 0.78, 0.10)
ORANGE = (0.93, 0.47, 0.13)
HOSE_LEN = 15 * 12 * N.IN                        # 4572 mm: 15 ft is enough for the atomizer's zone (the far
#                                                  zones need 25 ft, Ruwac EXP151525CB's; floor_cleaning.POU)
SQ_W, SQ_D, SQ_H = 14 * N.IN, 70.0, 42.0         # the squeegee head: 356 mm wide (assumed 14 in), depth and height ours
BLADE_H = 14.0

# the station on the floor plan (floor_cleaning.VAC_STATION's x range; the vacuums at its front, the post behind)
VAC_AL = np.array([-5480.0, -1265.0])            # the Al-family 118EXP's bin axis (world)
VAC_CU = np.array([-4990.0, -1265.0])            # the Cu-family one
VAC_YAW = -90.0                                  # inlets (the vacuum's +x) to the south, towards the floor they serve
STN_AT = np.array([-5230.0, -560.0])             # our station's post (holster, rack, fixture), behind the vacuums
PAIL_AL, PAIL_CU = np.array([-5640.0, -560.0]), np.array([-4850.0, -560.0])
EXT_AT = np.array([-5700.0, -1800.0])            # the Class D extinguisher at the station's front corner
STUD = np.array([-3020.0, -2380.0])              # ours: the floor ground stud the unit's bonding lead clips to

UNIT3 = (-3950.0, -2860.0, 0.0)                  # x, y, heading: in the aisle's north lane, its left (arm) side north
SQ_AT = np.array([-3270.0, -2090.0])             # the squeegee head's centre: its end 13 mm off the rePowder's
#                                                  front (out/tray_plan.json's y -1899)
WAND_DIR = np.array([-0.40, 0.40, -0.82])        # the wand's axis, hose end to tool end: down towards the machine and
#                                                  west, so its hose end stays east of unit 3's cabinet in both lanes
# the clip's strokes, as world translations of the grasp from the still's pose: lane 1 west along the machine's base,
# up, out to lane 2, down, back east, lift clear. Lane 2 is 110 mm out (the 356 mm head overlaps lane 1 by 246 mm)
STROKES = [(-480.0, 0.0, 0.0), (-480.0, 0.0, 30.0), (-480.0, -110.0, 30.0), (-480.0, -110.0, 0.0),
           (0.0, -110.0, 0.0), (0.0, -110.0, 150.0)]


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def place(sc, meshes, group, Mx):
    for name, (mesh, col) in meshes.items():
        sc.add(f"{group}/{name}", mesh, col, group, specular=0.5)
    sc.gmat[group] = Mx


def vac_pt(at, name):
    a = math.radians(VAC_YAW)
    x, y, z = N.vacuum_local(name)
    return np.array([at[0] + x * math.cos(a) - y * math.sin(a), at[1] + x * math.sin(a) + y * math.cos(a), z])


def box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def squeegee(tool_end: np.ndarray, d: np.ndarray) -> dict:
    """Ours: a 14 in floor squeegee for the 1.5 in wand, in the world. The head lies on the floor at SQ_AT, its blade
    across the stroke (the head's long side along y, square to the machine's front, so a stroke along x cleans a 356 mm
    band beside the machine); a neck from the head's inlet up to the wand's tool end, with a swivel ball."""
    cx, cy = SQ_AT
    head = box(cx - SQ_D / 2, cx + SQ_D / 2, cy - SQ_W / 2, cy + SQ_W / 2, BLADE_H, BLADE_H + SQ_H)
    blades = box(cx - SQ_D / 2 + 4, cx - SQ_D / 2 + 10, cy - SQ_W / 2, cy + SQ_W / 2, 0.5, BLADE_H).merge(
        box(cx + SQ_D / 2 - 10, cx + SQ_D / 2 - 4, cy - SQ_W / 2, cy + SQ_W / 2, 0.5, BLADE_H))
    inlet = np.array([cx, cy, BLADE_H + SQ_H])
    ball = pv.Sphere(radius=24, center=inlet + (0, 0, 14)).triangulate()
    neck = N.tube_along(np.array([inlet + (0, 0, 14), tool_end]), 19.0, 20)
    spigot = N.tube_along(np.array([tool_end - d * 2.0, tool_end - d * 45.0]), N.SPIGOT_R, 20)
    return {"squeegee head": (head.merge(ball), N.ALU), "squeegee blades": (blades, (0.10, 0.10, 0.11)),
            "squeegee neck": (neck.merge(spigot), N.ALU)}


def build(clip: bool = False, name: str | None = None, title: str | None = None):
    """The scene (floor_clean_people.py builds its clip on it, under its own name)."""
    sc = Scene(name or (CLIP if clip else NAME), title or TITLE, gif=clip, mp4=clip)
    sc.soft = set()
    # ---- the floor, the aisle's tape (warehouse.Floor._tape: 3 in lines on the aisle's edges, a dashed centre line)
    sc.add("lab floor", pv.Plane(center=(-3000, -3200, -1.5), direction=(0, 0, 1), i_size=14000, j_size=9000),
           FLOOR_C, "floor", ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
    lines = [box(-10200, 10200, y - 37.5, y + 37.5, -1.0, 0.5) for y in (-2400.0, -5400.0)]
    sc.add("aisle tape", lines[0].merge(lines[1]), TAPE_Y, "floor", ambient=0.9, diffuse=0.2, specular=0.0)
    dashes = None
    for x in np.arange(-10200 + 300, 3000, 1200):
        b = box(x, x + 600, -3925, -3875, -1.0, 0.5)
        dashes = b if dashes is None else dashes.merge(b)
    sc.add("aisle dashes", dashes, (0.97, 0.97, 0.95), "floor", ambient=0.5, specular=0.0)
    # the powder zone round the rePowder (floor_cleaning.ZONES_SPEC: its footprint grown by 600 mm), in red-and-white
    # tape where it isn't the aisle's own line
    zx0, zx1, zy0, zy1 = FC.Floor().zones["atomizer"]["rect"]
    zy0 = max(zy0, -2400.0 + 40.0)
    zt = [box(zx0, zx1, zy0 - 25, zy0 + 25, -0.9, 0.6), box(zx0 - 25, zx0 + 25, zy0, zy1, -0.9, 0.6),
          box(zx1 - 25, zx1 + 25, zy0, zy1, -0.9, 0.6)]
    sc.add("zone tape", zt[0].merge(zt[1]).merge(zt[2]), (0.86, 0.18, 0.14), "floor", ambient=0.9, specular=0.0)

    # ---- the rePowder (atom_base.build's own steps, without its clip-only floor and tape)
    for k in range(4):
        sc.parent.setdefault(AB.g(f"slug{k}"), "rp")
    AA.load_rp(sc, ghost={"stack_cover": 0.35})
    for k in range(4):
        sc.show(sc.members(AB.g(f"slug{k}")), 0.0)
    AB.set_joints(sc)
    AA.flange_clamp(sc, 1.0)

    # ---- the sieving cell's bench and downdraft enclosure (setup_lab.SIEVE_BENCH, sieve_station.enclosure_parts)
    import setup_lab as SL
    import sieve_station as SS
    sb = SL.SIEVE_BENCH
    bx, bw, bd, bh = sb["x"], sb["w"], sb["d"], sb["h"]
    by0 = -1577.0                                         # out/tray_plan.json: the sieving cell's front
    byc = by0 + bd / 2
    sc.add("sieve bench top", box(bx - bw / 2, bx + bw / 2, by0, by0 + bd, bh - 40, bh), (0.62, 0.64, 0.67), "sieve")
    legs = None
    for lx in (bx - bw / 2 + 40, bx + bw / 2 - 40):
        for ly in (by0 + 40, by0 + bd - 40):
            leg = box(lx - 25, lx + 25, ly - 25, ly + 25, 0, bh - 40)
            legs = leg if legs is None else legs.merge(leg)
    sc.add("sieve bench legs", legs, (0.35, 0.36, 0.38), "sieve")
    for nm, (mesh, col, spec, op) in SS.enclosure_parts(bw, bd, sb["encl_h"]).items():
        sc.add(f"sieve encl {nm}", mesh.translate((bx, byc, bh), inplace=False), col, "sieve", opacity=op,
               specular=spec)

    # ---- Shuttle 1 (vlm.py via lab.py), in the background
    try:
        import lab
        for nm, e in lab._vlm_entries().items():
            sc.add(f"vlm/{nm}", e["mesh"], e["color"], "vlm", opacity=e["opacity"], specular=e["specular"])
    except Exception as ex:                               # noqa: BLE001  (the still is about the floor, not the lift)
        print("Shuttle 1 left out:", ex, flush=True)

    # ---- the vacuum station: two 118EXPs, our post, two pails, the extinguisher, the sign, the ground bar
    for key, at in (("al", VAC_AL), ("cu", VAC_CU)):
        place(sc, N.vacuum_meshes(), f"vac{key}:body", T((*at, 0)) @ R((0, 0, 1), VAC_YAW))
    place(sc, N.station_meshes(), "vac:station", T((*STN_AT, 0)) @ R((0, 0, 1), 180))
    for nm in N.SOFT:
        if f"vac:station/{nm}" in sc.actors:
            sc.soft.add(f"vac:station/{nm}")
    place(sc, N.pail_meshes(), "vac:pail_al", T((*PAIL_AL, 0)))
    place(sc, N.pail_meshes(), "vac:pail_cu", T((*PAIL_CU, 0)))
    place(sc, N.extinguisher_meshes(), "vac:ext", T((*EXT_AT, 0)) @ R((0, 0, 1), 90))
    place(sc, N.sign_meshes(), "vac:sign", T((-5850.0, -1700.0, 0)) @ R((0, 0, 1), 90))
    for key, at in (("al", VAC_AL), ("cu", VAC_CU)):          # a label plate on each lid: which family's it is
        sc.add(f"vac{key} plate", box(at[0] - 90, at[0] + 90, at[1] - 182, at[1] - 178, 760, 860),
               (0.20, 0.42, 0.75) if key == "al" else (0.72, 0.38, 0.16), "static")

    # ---- unit 1 at Shuttle 1's opening (setup_lab: the VLM's dock, x 0, y -1932), arm parked
    u1 = AA.Mir(sc, g="amr", prefix="ur", cargo=True)
    u1.set(0.0, -1932.0, 0.0)

    # ---- unit 3: a MiR250 + cabinet + UR10e + 2F-85 like the others, with an orange band and a bonding lead
    x3, y3, h3 = UNIT3
    u3 = AA.Mir(sc, g="amrC", prefix="urC", cargo=False)
    u3.set(x3, y3, h3)
    Lc, Wc = P.MIR["L"] - 80, P.MIR["W"] - 60
    band = box(-Lc / 2 - 1, Lc / 2 + 1, -Wc / 2 - 1, Wc / 2 + 1, P.MIR["H"] + P.CAB_H - 90, P.MIR["H"] + P.CAB_H - 40)
    sc.add("amrC/unit 3 band", band, ORANGE, "amrC")
    lead_from = np.array([x3 + 330, y3 + 290, 120.0])
    stud = np.r_[STUD, 0.0]
    lead = np.array([lead_from, lead_from + (60, 40, -80), lead_from + (200, 170, -112), stud + (-60, -30, 8),
                     stud + (0, 0, 40)])
    lead[:, 2] = np.maximum(lead[:, 2], 4.0)
    sc.add("amrC bonding lead", N.tube_along(lead, 4.0, 10), N.GRN_YEL, "static")
    sc.add("ground stud", pv.Cylinder(center=(*STUD, 20), direction=(0, 0, 1), radius=9, height=40).triangulate()
           .merge(box(STUD[0] - 45, STUD[0] + 45, STUD[1] - 45, STUD[1] + 45, 0, 6)), N.BRASS, "static")
    sc.soft.add("amrC bonding lead")

    # ---- the wand with the squeegee, held by unit 3's arm
    d = unit(WAND_DIR)
    tool_end = np.array([SQ_AT[0], SQ_AT[1], BLADE_H + SQ_H + 14.0]) - d * 120.0
    z = -d
    hint = unit(np.array([x3 + 0.0, y3 + 130.0, 1500.0]) - tool_end)     # the fin towards the arm's base, up
    h = hint - (hint @ z) * z
    f = unit(h)
    y_ = -f
    x_ = np.cross(y_, z)
    Mw = np.eye(4)
    Mw[:3, 0], Mw[:3, 1], Mw[:3, 2] = x_, y_, z
    Mw[:3, 3] = tool_end + N.WAND_L * z                   # the wand frame's origin is its hose end
    place(sc, N.wand_meshes(), "vac:wand", Mw)
    # the squeegee goes in the wand's own group (in the wand's frame), so the audit sees it as part of what the arm
    # holds; it moves with the wand, and the strokes only translate it, so the head stays flat on the floor
    Mi = np.linalg.inv(Mw)
    for nm, (mesh, col) in squeegee(tool_end, d).items():
        sc.add(f"vac:wand/{nm}", mesh.transform(Mi, inplace=False), col, "vac:wand", specular=0.5)
    sc.soft.add("vac:wand/squeegee blades")
    head_local = (Mi @ np.r_[SQ_AT, BLADE_H + SQ_H / 2, 1.0])[:3]
    grasp = Mw @ N.grasp_local((0, -1, 0))
    rb = u3.rb
    rb.grasp("vac:wand")
    # every closed-form solution for the grasp (ur_arm._ik_analytic), polished, each checked with collide.Checker on
    # this pose; the first with nothing touching is kept (the nearest to the parked pose first). The wand is held
    # (its offset from the TCP fixed by the first solution's grasp), so each solution carries it to the same place.
    import collide
    close = ur_arm.close_for(N.FIN_T + 0.3)
    Tb = np.linalg.inv(sc.world(rb.root)) @ grasp
    off = np.eye(4)
    off[2, 3] = -ur_arm.TCP_MM
    T06 = Tb @ off
    seed = np.radians(np.asarray((-90.0, -150.0, 135.0, -75.0, -90.0, 180.0)))
    sols = []
    for q6 in np.linspace(-math.pi, math.pi, 13):
        for sol in ur_arm._ik_analytic("ur10e", T06, q6_free=float(q6)):
            qq = ur_arm._polish("ur10e", ur_arm._wrap_near(sol, seed), T06)
            e = ur_arm._pose_err(ur_arm.fk("ur10e", qq)["tool0"], T06)
            if np.linalg.norm(e[:3]) < 1e-3 and np.linalg.norm(e[3:]) < 1e-6:
                sols.append(ur_arm._wrap_near(qq, seed))
    if not sols:
        raise RuntimeError("unit 3's arm can't reach the wand's fin from there")
    sols.sort(key=lambda qq: float(np.sum((qq - seed) ** 2)))
    held_off = None
    best = None

    def path_cost(q0) -> tuple[int, float]:
        """(hits, worst joint step) along the clip's strokes from q0: each segment in 24 steps, IK seeded from the
        last, collide.Checker every third step and at each end (the hose and the floor's blades are soft)."""
        rb.set(q0, close=close)
        G0 = rb.tcp_world()
        qq_, hits, worst = q0.copy(), 0, 0.0
        prev = np.zeros(3)
        for dx, dy, dz in STROKES:
            for k in range(1, 25):
                p_ = prev + (np.array([dx, dy, dz]) - prev) * k / 24
                M = T(tuple(p_)) @ G0
                try:
                    qn = rb.solve(M, qq_)
                except ValueError:
                    return 99, 999.0
                worst = max(worst, float(np.abs(qn - qq_).max()))
                qq_ = qn
                if k % 4 == 0:
                    rb.set(qq_)
                    rb._checker = None
                    hits += len(collide.Checker(rb).collisions(depths=False, first=True))
                    if hits:
                        return hits, worst                  # one hit is enough to reject this branch
            prev = np.array([dx, dy, dz])
        return hits, worst

    for qq in sols:
        rb.set(qq, close=close)
        if held_off is None:
            held_off = np.linalg.inv(rb.tcp_world()) @ Mw
        rb.held = ("vac:wand", held_off)
        rb.set()
        rb._checker = None
        n_hit = len(collide.Checker(rb).collisions(depths=False))
        if n_hit:
            continue
        ph, worst = path_cost(qq)
        score = (ph, worst > math.radians(20), worst)
        if best is None or score < best[1]:
            best = (qq, score)
        if ph == 0 and worst <= math.radians(20):
            break
    if best is None:
        raise RuntimeError("no IK solution for the wand's grasp is clear of everything")
    q = best[0]
    rb.set(q, close=close)
    rb._checker = None
    print(f"unit 3: {len(sols)} IK solutions; kept one clear in the still's pose, with {best[1][0]} hits along the "
          f"strokes and a worst joint step of {math.degrees(best[1][2]):.1f} deg", flush=True)

    # ---- the hose: 25 ft from the Al vacuum's inlet to the wand's cuff, relaxed on the floor (atom_nilfisk.Hose)
    inlet = vac_pt(VAC_AL, "inlet")
    t_in = np.array([math.cos(math.radians(VAC_YAW)), math.sin(math.radians(VAC_YAW)), 0.0])
    Wd = sc.world("vac:wand")
    cuff = (Wd @ np.r_[0, 0, N.CUFF_L - 20.0, 1.0])[:3]
    t_cuff = Wd[:3, 2]
    # the guide: down from the inlet to the floor, east along the zone's front strip, a bulge towards the aisle (its
    # depth set so the guide is 97 % of the hose's length, so the hose lies in a gentle curve), up to the cuff
    def guide_for(depth):
        return [inlet, inlet + t_in * 160 + (0, 0, -330), np.array([-5250.0, -1950.0, 26.0]),
                np.array([-4800.0, -2250.0, 26.0]), np.array([-4300.0, -2300.0 - depth * 0.6, 26.0]),
                np.array([-3850.0, -2350.0 - depth * 0.4, 26.0]), np.array([-3600.0, -2420.0, 26.0]),
                cuff + t_cuff * 420 + (0, 0, -420), cuff + t_cuff * 60, cuff]

    def glen(depth):
        gg = np.asarray(guide_for(depth), float)
        return float(np.linalg.norm(np.diff(gg, axis=0), axis=1).sum())
    lo_, hi_ = 0.0, 3000.0
    for _ in range(40):
        mid = (lo_ + hi_) / 2
        lo_, hi_ = (mid, hi_) if glen(mid) < 0.97 * HOSE_LEN else (lo_, mid)
    guide = guide_for(lo_)
    hose = N.Hose.__new__(N.Hose)
    hose.n = 120
    hose.seg = HOSE_LEN / (hose.n - 1)
    hose.boxes, hose.caps = [], []
    hose.set_ends(inlet, t_in, cuff, t_cuff)
    g = np.asarray(guide, float)
    dd = np.r_[0, np.cumsum(np.linalg.norm(np.diff(g, axis=0), axis=1))]
    s = np.linspace(0, dd[-1], hose.n)
    hose.p = np.c_[[np.interp(s, dd, g[:, k]) for k in range(3)]].T
    link_caps = []                                 # each arm link as a capsule in its own frame (atom_vacuum's way)
    for l in ("shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3", "gr_base", "gr_camera"):
        grp = f"{rb.prefix}_{l}"
        pts = [np.asarray(sc.actors[n].GetMapper().GetInput().GetPoints().GetData()) for n in sc.members(grp)
               if sc.actors[n].GetMapper().GetInput() is not None
               and sc.actors[n].GetMapper().GetInput().GetNumberOfPoints()]
        if not pts:
            continue
        pts = np.vstack(pts)
        c0 = pts.mean(0)
        ax = np.linalg.svd(pts - c0, full_matrices=False)[2][0]
        tt = (pts - c0) @ ax
        rad = np.linalg.norm((pts - c0) - np.outer(tt, ax), axis=1)
        link_caps.append((grp, c0 + ax * tt.min(), c0 + ax * tt.max(), float(np.percentile(rad, 95))))
    rpx0, rpx1, rpy0, rpy1 = FC.Floor().rects["repowder"]
    fixed_boxes = [(x3 - 400, x3 + 400, y3 - 290, y3 + 290, 0, 800),                   # unit 3 and its cabinet
                   (VAC_AL[0] - 310, VAC_AL[0] + 310, VAC_AL[1] - 260, VAC_AL[1] + 260, 0, 1150),
                   (VAC_CU[0] - 310, VAC_CU[0] + 310, VAC_CU[1] - 260, VAC_CU[1] + 260, 0, 1150),
                   (rpx0, rpx1, rpy0, rpy1, 0, 2000),
                   (EXT_AT[0] - 110, EXT_AT[0] + 110, EXT_AT[1] - 170, EXT_AT[1] + 170, 0, 900),
                   (STUD[0] - 45, STUD[0] + 45, STUD[1] - 45, STUD[1] + 45, 0, 40)]

    def obstacles():
        Wd_ = sc.world("vac:wand")
        hc = (Wd_ @ np.r_[head_local, 1.0])[:3]
        boxes = fixed_boxes + [(hc[0] - SQ_D / 2, hc[0] + SQ_D / 2, hc[1] - SQ_W / 2, hc[1] + SQ_W / 2, 0,
                                BLADE_H + SQ_H)]
        caps = []
        for grp, a_, b_, r_ in link_caps:
            Wl = sc.world(grp)
            caps.append(((Wl @ np.r_[a_, 1.0])[:3], (Wl @ np.r_[b_, 1.0])[:3], r_))
        top = Wd_[:3, 3]
        caps.append((top - Wd_[:3, 2] * 30, top - Wd_[:3, 2] * (N.WAND_L + 200), 26.0))
        return boxes, caps

    def cuff_end():
        Wd_ = sc.world("vac:wand")
        return (Wd_ @ np.r_[0, 0, N.CUFF_L - 20.0, 1.0])[:3], Wd_[:3, 2]

    def hose_hook(_sc):
        b, tb = cuff_end()
        hose.set_ends(inlet, t_in, b, tb)
        hose.boxes, hose.caps = obstacles()
        hose.relax(18)
        sc.set_mesh("vac hose", hose.mesh())

    hose.boxes, hose.caps = obstacles()
    hose.relax(500)
    sc.add("vac hose", hose.mesh(), N.BLACK, "static", specular=0.2)
    sc.soft.add("vac hose")
    sc.hose_hook, sc.hose = hose_hook, hose
    info = dict(hose_drawn_mm=round(hose.length(), 0), hose_mm=HOSE_LEN, q_deg=[round(math.degrees(v), 2) for v in q],
                grasp_world=[round(v, 1) for v in grasp[:3, 3]], unit3=UNIT3, squeegee=list(SQ_AT))
    return sc, u1, u3, rb, info


def check(sc, rb) -> dict:
    """The posed arm, gripper and held wand (with the squeegee) against everything else: collide.Checker, as the clip
    audits do (soft parts: the blades on the floor, the hose, the bonding lead, the station's spring parts)."""
    import collide
    chk = collide.Checker(rb)
    hits = [dict(kind=k, part=a, other=b, group=g_, depth_mm=None if dd is None else round(float(dd), 2))
            for k, a, b, g_, dd in chk.collisions(depths=True)]
    return dict(rules="collide.Checker on the still's pose (the round-11 rules' pair list, one frame)",
                hits=hits, n=len(hits))


def labels_area(sc, u3, rb):
    W = np.array
    return [("Unit 3 (powder): MiR250 + UR10e, its own", W([UNIT3[0] + 250, UNIT3[1] - 200, 850]), (0.66, 0.80)),
            ("Floor squeegee, 14 in, on the 118EXP's wand", W([SQ_AT[0], SQ_AT[1] - 100, 40]), (0.36, 0.88)),
            ("15 ft conductive hose", W([-4300.0, -2450.0, 30]), (0.10, 0.86)),
            ("118EXP, Al family (in use)", W([VAC_AL[0], VAC_AL[1], 1100]), (0.06, 0.30)),
            ("118EXP, Cu family", W([VAC_CU[0], VAC_CU[1], 1100]), (0.27, 0.22)),
            ("Bonding lead to a floor ground stud", W([STUD[0], STUD[1], 30]), (0.86, 0.63)),
            ("Powder zone: 600 mm round the rePowder", W([-2300.0, -2360.0, 5]), (0.80, 0.47)),
            ("Unit 1 keeps on with transfers", W([0.0, -1932.0, 1000]), (0.86, 0.22))]


def main():
    sc, u1, u3, rb, info = build()
    rep = check(sc, rb)
    rep.update(info)
    (OUT / "collisions").mkdir(parents=True, exist_ok=True)
    (OUT / "collisions" / f"{NAME}.json").write_text(json.dumps(rep, indent=1) + "\n")
    print("collisions in the still's pose:", rep["n"], [(h["part"], h["other"], h["depth_mm"]) for h in rep["hits"]][:12],
          flush=True)
    AA.status(sc, Unit_3="vacuuming the atomizer's zone after a run", Hose="15 ft, Al-family 118EXP",
              Bond="clipped to the floor stud")
    sc.label = "Option C"
    sc.caption = ("A third MiR250 + UR10e owns the powder floor: after each run, sieving and depowdering it takes the "
                  "wand of that family's 118EXP at the station, checks continuity, and works the zone's floor, edges "
                  "and corners with a squeegee; units 1 and 2 never touch the powder.")
    views = {"": [(-600.0, -6900.0, 3900.0), (-3650.0, -1750.0, 300.0), (0, 0, 1)],
             "_close": [(-2250.0, -3700.0, 1250.0), (-3350.0, -2150.0, 220.0), (0, 0, 1)]}
    for suffix, cam in views.items():
        sc.cam = cam
        sc.view_angle = 40.0 if suffix == "" else 36.0
        if suffix == "":
            sc.labels = [(t, tuple(p), at, 1.0) for t, p, at in labels_area(sc, u3, rb)]
        else:                                              # the close view: its own label places, nothing stacked
            Wd = sc.world("vac:wand")
            sc.labels = [("Floor squeegee, 14 in (ours: a 14 in head assumed)", (SQ_AT[0], SQ_AT[1], 50.0),
                          (0.70, 0.83)),
                         ("Our clamp collar and fin, as at the atomizer", tuple((Wd @ np.r_[0, 0, -N.COLLAR_AT, 1])[:3]),
                          (0.30, 0.18)),
                         ("Bonding lead to a floor ground stud", (STUD[0], STUD[1], 30.0), (0.86, 0.66)),
                         ("Unit 3's cabinet, orange band", (UNIT3[0] + 350, UNIT3[1] + 290, 700.0), (0.10, 0.30))]
            sc.labels = [(t, tuple(float(v) for v in p), at, 1.0) for t, p, at in sc.labels]
        img = sc.snap()
        path = OUT / f"{NAME}{suffix}.png"
        img.convert("RGB").save(path, optimize=True)
        print("wrote", path, flush=True)
    sc.pl.close()


def clip():
    """The clip (about 20 s): unit 3 works two lanes of the squeegee along the rePowder's front, the hose following
    (relaxed every frame), and lifts clear. Audited as it renders (collide.Auditor, the round-11 rules, as
    atom_vacuum.py does) -> out/collisions/floor_cleaning_clip.json; ARM_AUDIT=1 audits without rendering.

        python3 runner_guard.py slot --label fcclip --mem 4500 -- env VIZ3D_FPS=10 xvfb-run -a python3 \
            floor_clean_still.py clip
    """
    from scene import AUDIT, PREVIEW
    import collide
    sc, u1, u3, rb, info = build(clip=True)
    sc.frame_hooks.insert(0, sc.hose_hook)
    combined = not AUDIT and not PREVIEW
    if combined:
        sc.auditor = collide.Auditor(sc)
        sc.frame_hooks.append(sc.auditor)
    AA.status(sc, Unit_3="the atomizer's zone, after a run", Hose="15 ft, Al-family 118EXP",
              Bond="clipped to the floor stud")
    sc.label = "Option C"
    wide = [(-600.0, -6900.0, 3900.0), (-3650.0, -1750.0, 300.0), (0, 0, 1)]
    # the lanes seen along their length: from the strip's east end (in front of the sieving bench), looking west
    close = [(-2250.0, -2750.0, 1350.0), (-3600.0, -2120.0, 120.0), (0, 0, 1)]
    sc.cam, sc.view_angle = list(wide), 40.0
    t0 = rb.tcp_world()
    lane1_w, up1, over2, down2, lane2_e, lift = (T(tuple(p_)) @ t0 for p_ in STROKES)
    lab_w = [(t, tuple(float(v) for v in p_), at) for t, p_, at in labels_area(sc, u3, rb)]
    sc.step("1/4 After a run", "After a run: unit 3 has the Al-family wand, continuity checked on the station's "
            "fixture (as in atom_vacuum), its bonding lead on the floor stud.", 2.5, cam_to=wide, labels=lab_w,
            hold=1.5)
    sc.step("2/4 Lane 1", "Along the machine's base, the blade on the floor: 480 mm at 0.15 m/s (assumed), slow "
            "for fine powder. The 14 in squeegee head is ours (assumed size).", 3.2, rb.line_to(lane1_w), cam_to=close,
            labels=[], hold=0.4)
    cap2 = "Up 30 mm, 110 mm out, down: the 356 mm head overlaps the first lane by 246 mm."
    sc.step("3/4 Lane 2", cap2, 1.0, rb.line_to(up1), hold=0.0)
    sc.step("3/4 Lane 2", cap2, 1.0, rb.line_to(over2), hold=0.0)
    sc.step("3/4 Lane 2", cap2, 0.8, rb.line_to(down2), hold=0.2)
    sc.step("3/4 Lane 2", "Back east along the second lane, then the next 480 mm of the zone.", 3.2,
            rb.line_to(lane2_e), hold=0.4)
    sc.step("4/4 Lift clear", "Lift clear: 20 s of run-on in clean air (vacuum SOP 4.1), then the next zone. A "
            "visible spill is not the robot's: it stops and calls the person (SOP 8).", 1.5, rb.line_to(lift),
            hold=2.5)
    sc.save()
    if combined:
        sc.auditor.save()
    if AUDIT:
        pass                                                # Scene.save() wrote the audit (ARM_AUDIT=1)
    (OUT / "collisions").mkdir(parents=True, exist_ok=True)
    meta = dict(info, hose_length_end_mm=round(sc.hose.length(), 1))
    (OUT / f"{CLIP}_meta.json").write_text(json.dumps(meta, indent=1) + "\n")


if __name__ == "__main__":
    import sys
    clip() if (len(sys.argv) > 1 and sys.argv[1] == "clip") else main()
