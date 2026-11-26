#!/usr/bin/env python3
"""The waste in the lab, animated (#303, PR #318 round 16, from PR #371's check: "Nothing about waste handling is
animated"). About two minutes, in the whole lab as the set-up movie leaves it (setup_lab.build), from notes/waste.md:

1. **The bottle trip.** A MiR250 + UR12e (units[1]) brings a capped 1 L bottle of sieve-wash IPA in the PE spill
   tray on its deck to the ducted fume hood's dock. Under the raised sash its arm sets the bottle in the intake tray's
   empty nest, takes an empty 1 L bottle from the rack beside it into the spill tray, and parks. One class a trip; the
   arm never opens, pours or combines waste; the delivery is logged for the pickup request.
2. **The cabinets.** The hood's base with its doors drawn see-through for a few seconds: the solvent cabinet's and
   the acid cabinet's containers (waste_station.cabinet_contents), each named.
3. **The powder point** behind the rePowder's fire point (powder_point.py): the two 118EXPs (Al family, Cu family),
   one grounded pail per family, Risk Management's Solid Material bucket, the sand can for filters, the Class D units,
   the sign. A person seals and carries the liners; powder waste never rides a MiR.
4. **Where waste waits**, the two places on the floor from the aisle.

    python3 runner_guard.py slot --mem 6500 --label waste -- xvfb-run -a python3 waste_clip.py
        # -> out/mp4/waste_clip.mp4, out/waste_clip.gif, out/waste_clip.json, out/waste_clip_still.png
    ARM_AUDIT=1 ... python3 waste_clip.py        # every frame checked (collide.py) -> out/collisions/waste_clip.json
    PREVIEW=1 ... python3 waste_clip.py          # the last frame of each sub-step -> /tmp/preview_waste_clip.png
    VIZ3D_HD=1 VIZ3D_HD_DIR=r16 VIZ3D_AUDIT=1 ... python3 waste_clip.py     # out/r16/ with text, out/clean/ without

VLAB_ONLY_TRAYS="" is the default here: the Shuttles stay clad, so their trays aren't seen and aren't loaded (about
6 GB for the whole lab). Every arm move goes through robot.py (joint moves planned round what is in the way, line moves
solved every frame); the poses at the deck, the nest and the rack are searched here against the scene as it stands
(IK branches x approach directions, collide.Checker). What is ours: the spill tray and the 1 L bottles (typical
sizes), the bottles' labels, the log line, the powder point's layout (powder_point.py). Notes: notes/waste_clip.md.
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("VLAB_ONLY_TRAYS", "")

import scene                          # noqa: E402
from scene import AUDIT, PREVIEW, T  # noqa: E402

import animate as A                   # noqa: E402
import lab                            # noqa: E402
import props as P                     # noqa: E402
import robot as RB                    # noqa: E402
import ur_arm                         # noqa: E402
import waste_station as WS            # noqa: E402
import powder_point as PP             # noqa: E402

NAME = "waste_clip"
TITLE = "Vertical cloud lab: the waste, where it waits and how it moves"
UNIT = 1                              # units[1], on charger 1 (x -300); unit 3 (floor cleaning) stays on its charger
MIR_SPEED = 1200.0                    # mm/s at most, at the MiR250's 0.3 m/s^2 (props.ramp_secs), as the chapters
TURN_RATE = 60.0                      # deg/s, at 60 deg/s^2 (assumed, as alloy_workflow.Unit8.route)
AISLE_Y = -4900.0                     # the aisle's south lane, where the unit drives along
# ours: the PE spill tray on the cabinet's top (cabinet frame, mm): 180 x 180, 6 mm floor, 50 mm walls, a nest ring
# for one 1 L bottle; clear of the arm's base (0, 130), the vial holder (-300, -150) and the e-stop (290..330, -250..-210)
CARRIER_AT = (190.0, -110.0)
CARRIER = dict(w=180.0, d=180.0, floor=6.0, wall=6.0, h=50.0)
DECK_Z = P.MIR["H"] + P.CAB_H + 20.0  # 800: the cabinet's top (props.AMR_TOP)
BOTTLE = dict(r=45.0, h=190.0)        # a 1 L HDPE narrow-mouth bottle (typical), as waste_station draws it
CAP_TCP = 183.0                       # the grasp point over the bottle's base: the pads on its cap (171-190 mm)
GRIP = ur_arm.close_for(2 * BOTTLE["r"] * 0.45 + 0.3)     # closed on the 40.5 mm cap
OPEN = 0.25
IPA_C = WS.IPA_C
RED = WS.RED


# ================================================================================================= the parts
def bottle_parts(liquid, fill, band=None, text=None) -> list:
    """A capped 1 L bottle at the origin (its base on z = 0): waste_station.bottle, a coloured band and a label in
    words on its front (-y)."""
    out = [(nm, m, c, op) for nm, m, c, op in WS.bottle(0.0, 0.0, 0.0, BOTTLE["r"], BOTTLE["h"], liquid, fill=fill,
                                                     glass=WS.HDPE)]
    if band is not None:
        out.append(("band", WS.cyl(BOTTLE["r"] + 1.5, 26.0, 0.0, 0.0, BOTTLE["h"] * 0.60), band, 1.0))
    if text:
        for nm, m, c, op in PP.text_plate(text, 0.0, -BOTTLE["r"] - 2.2, BOTTLE["h"] * 0.36, 74.0, 46.0, depth=0.8):
            out.append((f"label {nm}", m, c, op))
    return out


def carrier_mesh():
    c = CARRIER
    x0, x1, y0, y1 = -c["w"] / 2, c["w"] / 2, -c["d"] / 2, c["d"] / 2
    m = WS.box(x0, y0, 0.0, x1, y1, c["floor"])
    for a0, a1, b0, b1 in ((x0, x1, y0, y0 + c["wall"]), (x0, x1, y1 - c["wall"], y1), (x0, x0 + c["wall"], y0, y1),
                           (x1 - c["wall"], x1, y0, y1)):
        m = m.merge(WS.box(a0, b0, 0.0, a1, b1, c["h"]))
    import pyvista as pv
    ring = pv.Disc(center=(0, 0, c["floor"] + 0.5), inner=48, outer=56, normal=(0, 0, 1), c_res=48).triangulate()
    return m, ring.extrude((0, 0, 14), capping=True).triangulate()


def add_parts(sc, parts, group, parent, M):
    names = []
    for nm, m, c, op in parts:
        n = f"{group}/{nm}"
        sc.add(n, m, c, group, opacity=op, specular=0.25)
        names.append(n)
    sc.parent[group] = parent
    sc.gmat[group] = M
    return names


# ================================================================================================= the scene
def build():
    scene.GIF_FPS = 3                  # a two-minute GIF well under 4.9 MB (the MP4 keeps every frame)
    scene.GIF_SIZE = (512, 288)
    import setup_lab as SL
    import warehouse as W
    data = lab.meshes()
    idata = SL.load_all()
    sc, L, F, items, rigs, units, util, ulabel, vp = SL.build(data, idata, name=NAME, title=TITLE)
    sc.gif = not (PREVIEW or AUDIT)
    sc.intro = 0.8
    L.skin(0.0)(1.0)                   # the cladding as built: the trays stay inside
    L.show_gauges = False
    L.extra_gauges = []
    if "fumehood" not in F.rigs or not sc.members("waste"):
        raise SystemExit("waste_clip: the lab has no fume hood or no waste station (VLAB_WASTE=0?)")
    if not sc.members("powder_point"):
        raise SystemExit("waste_clip: the lab has no powder point (VLAB_POWDER_POINT=0?)")
    u = units[UNIT]
    u.set(W.charger_pose(UNIT))
    L.apply_state()
    return sc, L, F, u, W


def restrict_collisions(sc, keep_xy, reach=2600.0, keep_groups=()):
    """As upkeep_clip.fast_collisions: the collision world is what stands within `reach` of the points keep_xy (the
    unit's route and the hood), plus keep_groups; everything else is left out of the checks (it can't be touched)."""
    import collide as CL
    pts = np.asarray(keep_xy, float)
    only, known = {}, set(sc.actors)
    keep = set()
    for g in keep_groups:
        keep |= CL._subtree(sc, g)

    def near(name, actor):
        g = sc.group_of.get(name)
        if g in keep:
            return True
        inp = actor.GetMapper().GetInput()
        if inp is None or inp.GetNumberOfPoints() == 0:
            return False
        b = np.array(inp.GetBounds()).reshape(3, 2)
        c = np.array([[b[0, i], b[1, j], b[2, k]] for i in (0, 1) for j in (0, 1) for k in (0, 1)])
        w = (sc.world(g) @ np.c_[c, np.ones(8)].T).T[:, :3]
        lo, hi = w.min(axis=0), w.max(axis=0)
        d = np.linalg.norm(np.maximum(np.maximum(lo[:2] - pts, pts - hi[:2]), 0.0), axis=1).min()
        return d < reach and lo[2] < 3200.0

    for name, actor in sc.actors.items():
        if near(name, actor):
            only[name] = actor

    class FastWorld(CL.World):
        def refresh(self):
            full = self.sc.actors
            if len(full) != len(known):
                for name in set(full) - known:
                    known.add(name)
                    if near(name, full[name]):
                        only[name] = full[name]
            self.sc.actors = only
            try:
                CL.World.refresh(self)
            finally:
                self.sc.actors = full

    sc._collide_world = FastWorld(sc)
    print(f"collision world: {len(only)} of {len(sc.actors)} actors", flush=True)


def movie():
    import collide
    sc, L, F, u, W = build()
    rb = u.robot
    cab = f"{u.name}_cab"
    sc.robots = [rb]                    # only this unit's arm moves (the others stay parked on their chargers)
    PARK = np.radians(A.PARK_DEG)
    rig = F.rigs["fumehood"]
    rig.v["sash"] = 1.0                 # the sash at its 18 in (457 mm) stop, the hood's working position
    rig.apply()
    Mh = sc.world("wh_fumehood:body")

    def hw(p):
        return (Mh @ np.r_[np.asarray(p, float)[:3], 1.0])[:3]

    d_in = Mh[:3, :3] @ np.array([0.0, 1.0, 0.0])          # into the hood, world
    # ---- the work surface, drawn here part by part (the lab merges it by colour, which can't move): hide the merged
    # copies, add the intake tray, the nests, the delivered bottle, the rack and the etch as fixtures, and the two
    # empties as parts the arm can take
    for n in sc.members("waste"):
        if "/surface " in n:
            sc.alpha[n] = 0.0
            sc.base_alpha[n] = 0.0
    ws, nests = WS.work_surface()
    fixed = [(nm, m, c, op) for nm, m, c, op in ws if not nm.startswith("empty ")]
    add_parts(sc, fixed, "wc_surface", "wh_fumehood:body", np.eye(4))
    empties = []
    for k, (ex, ey) in enumerate(WS.EMPTIES):
        g = f"wc_empty{k}"
        add_parts(sc, bottle_parts((1, 1, 1), 0.0), g, "wc_surface", T((ex, ey, WS.EMPTIES_Z)))
        empties.append(g)
    # ---- the spill tray on the unit's cabinet, and the bottle of sieve-wash IPA in it
    tray_m, ring_m = carrier_mesh()
    add_parts(sc, [("tray", tray_m, WS.TRAY, 1.0), ("nest", ring_m, (0.35, 0.37, 0.40), 1.0)], "wc_carrier", cab,
              T((*CARRIER_AT, DECK_Z)))
    ipa_label = ((("IPA + Al fines",), 1.0), (("no water, no acid",), 0.62))
    add_parts(sc, bottle_parts(IPA_C, 0.75, band=RED, text=ipa_label), "wc_ipa", "wc_carrier",
              T((0.0, 0.0, CARRIER["floor"])))
    # ---- the cabinets' contents and the see-through hood (part 2 only)
    contents = add_parts(sc, WS.cabinet_contents(), "wc_contents", "wh_fumehood:body", np.eye(4))
    ghost = add_parts(sc, [(nm, m, c, op) for nm, m, c, op in WS.hood() if nm not in ("collar", "duct")
                           and not nm.startswith(("sash", "airflow"))], "wc_ghost", "wh_fumehood:body", np.eye(4))
    ghost_op = {n: op for n, (nm, m, c, op) in zip(ghost, [p for p in WS.hood() if p[0] not in ("collar", "duct")
                                                           and not p[0].startswith(("sash", "airflow"))])}
    for n in contents + ghost:
        sc.alpha[n] = 0.0
    hood_body = [n for n in rig.names.get("body", [])]
    waste_doors = [n for n in sc.members("waste") if "/surface " not in n]
    sc.apply()

    # ---- collision checks: only this unit's arm; the world near its route and the hood
    route_xy = [(u.pose[0], u.pose[1]), (u.pose[0], AISLE_Y), (2500.0, AISLE_Y), (2500.0, -5868.0), (1500.0, -5868.0),
                (1500.0, -6700.0)]
    restrict_collisions(sc, route_xy, reach=1800.0)      # the audit itself: scene.py (ARM_AUDIT=1, VIZ3D_AUDIT=1)

    st = {"lbl": "", "cap": ""}

    def say(label, cap):
        st["lbl"], st["cap"] = label, cap

    def step(secs, update=None, hold=0.1, cam=None, labels=(), still=False, va=None):
        sc.step(st["lbl"], st["cap"], secs, update, hold=hold, cam_to=cam, labels=labels, still=still,
                view_angle_to=va)

    def gauges(**kv):
        sc.gauges = [(k.replace("_", " "), v) for k, v in kv.items() if v]

    # ---- the drive: off the charger backwards, along the aisle, round to the hood's dock line, in to the dock
    def route(pts, end_heading=None, reverse_first=False):
        segs = []
        x, y, hd = u.pose
        for i, (px, py) in enumerate(pts):
            dist = math.hypot(px - x, py - y)
            if dist < 1:
                continue
            want = math.degrees(math.atan2(py - y, px - x)) + (180.0 if reverse_first and i == 0 else 0.0)
            turn = (want - hd + 180.0) % 360.0 - 180.0
            if abs(turn) > 0.5:
                segs.append(("turn", (x, y, hd), (x, y, hd + turn), P.ramp_secs(turn, TURN_RATE, 60.0), turn))
                hd += turn
            segs.append(("drive", (x, y, hd), (px, py, hd), P.ramp_secs(dist, MIR_SPEED), dist))
            x, y = px, py
        if end_heading is not None:
            turn = (end_heading - hd + 180.0) % 360.0 - 180.0
            if abs(turn) > 0.5:
                segs.append(("turn", (x, y, hd), (x, y, hd + turn), P.ramp_secs(turn, TURN_RATE, 60.0), turn))
        total = sum(s_[3] for s_ in segs) or 1.0
        bounds = np.cumsum([0.0] + [s_[3] for s_ in segs])

        def up(v):
            t = P.unease(v) * total
            for k, (kind, a, b, secs, d) in enumerate(segs):
                if t <= bounds[k + 1] + 1e-9 or k == len(segs) - 1:
                    f = min(1.0, max(0.0, (t - bounds[k]) / max(secs, 1e-9)))
                    g = P.ramp_frac(f, d, MIR_SPEED if kind == "drive" else TURN_RATE,
                                    P.MIR_ACCEL if kind == "drive" else 60.0)
                    a_, b_ = np.array(a), np.array(b)
                    u.set(tuple(a_ + (b_ - a_) * g))
                    if rb.held is not None:
                        rb.set()
                    return
        return up, total

    # ---- pose search. A held bottle stays upright only if the tool keeps the pitch it was grasped at (turning about
    # the vertical is free), so each bottle has one pitch for its grasp and its place. find(): an approach (that pitch,
    # a yaw from `yaws`) and an IK branch whose pose at p is clear of everything but `allow`, and the poses `outs`
    # ((up, back): the TCP raised `up` mm and drawn `back` mm along -approach), each solved from the one before in the
    # same branch, are clear too (gripper open). -> (app, q) or None.
    def find(p, d0, pitch, yaws, allow, outs=(), close=GRIP):
        chk = rb.checker()
        world = chk.snapshot()
        Wi = np.linalg.inv(sc.world(rb.root))
        for app in apps_round(d0, yaws, (pitch,)):
            Tw = tcp(p, app)
            for q in collide.ik_all(rb.model, Wi @ Tw, rb.q) or []:
                if chk.collisions(q, close, world, allow=set(allow), first=True):
                    continue
                ok, qo = True, q
                for up_, back in outs:
                    off = np.array([0.0, 0.0, up_]) - app * back
                    try:
                        qn = rb.solve(tcp(np.asarray(p) + off, app), qo)
                    except ValueError:
                        ok = False
                        break
                    if np.abs(qn - qo).max() > np.radians(70) or chk.collisions(qn, OPEN, world, allow=set(allow),
                                                                                 first=True):
                        ok = False
                        break
                    qo = qn
                if ok:
                    return app, q
        return None

    def apps_round(d0, yaws, pitches):
        out = []
        h = np.array([d0[0], d0[1], 0.0])
        h /= np.linalg.norm(h)
        for p_ in pitches:
            for y_ in yaws:
                c, s_ = math.cos(math.radians(y_)), math.sin(math.radians(y_))
                hh = np.array([c * h[0] - s_ * h[1], s_ * h[0] + c * h[1], 0.0])
                out.append(hh * math.cos(math.radians(p_)) + np.array([0, 0, -math.sin(math.radians(p_))]))
        return out

    def tcp(p, app):
        return P.tcp_frame(tuple(np.asarray(p, float)), tuple(np.asarray(app, float)), 0.0)

    def world_of(group, local):
        return (sc.world(group) @ np.r_[np.asarray(local, float), 1.0])[:3]

    def arm_step(desc, secs, update, hold=0.05, **kw):
        if AUDIT:
            print(f"waste_clip step at frame {sc.n}: {desc}", flush=True)
        step(secs, update, hold=hold, **kw)
        if AUDIT and rb.plans:
            pl = rb.plans[-1]
            if pl.get("frame", -1) >= 0 and pl.get("label") == sc.label and pl.get("reason"):
                print(f"   plan: {pl}", flush=True)

    x_d, y_d, hd_d = W.dock_pose("fumehood")
    nest = np.array(nests[1], float)
    e0 = WS.EMPTIES[0]
    YAWS = (0, 15, -15, 30, -30, 45, -45, 60, -60, 90, -90, 120, -120, 150, -150, 180)
    YAWS_IN = (0, 10, -10, 20, -20, 30, -30, 40, -40)

    def plan_stop():
        """Where on the hood's dock line (or up to 300 mm further out) the unit stops, and every pose its arm goes
        through there: the first stop where all are clear (east first: the hood's target post stands west)."""
        home = tuple(u.pose)
        tried = []
        for dx in (0.0, 150.0, 300.0, 450.0):
            for dy in (0.0, 150.0, 300.0):
                u.set((x_d + dx, y_d + dy, hd_d))
                cap_deck = world_of("wc_carrier", (0.0, 0.0, CARRIER["floor"] + CAP_TCP))
                cap_nest = hw((nest[0], nest[1], nest[2] + CAP_TCP))
                cap_e = hw((e0[0], e0[1], WS.EMPTIES_Z + CAP_TCP))
                base = world_of(rb.root, (0, 0, 0))
                d_out = cap_deck - base
                for p1 in (0.0, 15.0, 25.0):
                    a = find(cap_deck, d_out, p1, YAWS, ("wc_ipa", "wc_carrier"), outs=((0.0, 110.0),))
                    if a is None:
                        tried.append((dx, dy, p1, "deck"))
                        continue
                    b = find(cap_nest, d_in, p1, YAWS_IN, ("wc_surface",), outs=((70.0, 0.0), (70.0, 330.0)))
                    if b is None:
                        tried.append((dx, dy, p1, "nest"))
                        continue
                    app_h = b[0]
                    for p2 in (p1, 0.0, 15.0, 25.0):
                        c = find(cap_e, d_in, p2, YAWS_IN, (empties[0], "wc_surface"), close=OPEN,
                                 outs=((0.0, 300.0), (40.0, 300.0)))
                        if c is None:
                            tried.append((dx, dy, p2, "empty"))
                            continue
                        dd = find(cap_deck, d_out, p2, YAWS, ("wc_carrier",), outs=((95.0, 0.0), (0.0, 110.0)))
                        if dd is None:
                            tried.append((dx, dy, p2, "deck again"))
                            continue
                        u.set(home)
                        return dict(stop=(x_d + dx, y_d + dy, hd_d), app_d=a[0], app_h=app_h, app_e=c[0],
                                    app_d2=dd[0], p1=p1, p2=p2)
        u.set(home)
        raise SystemExit(f"waste_clip: no stop at the hood where every arm pose is clear; tried {tried[-12:]}")

    plan = plan_stop()
    print(f"waste_clip: stop {np.round(plan['stop'], 0).tolist()}, pitches {plan['p1']} / {plan['p2']}", flush=True)
    x_s, y_s, _ = plan["stop"]

    # ================================================================== 1. the bottle trip
    CAM_CHARGER = [(1600.0, -3000.0, 2300.0), (-300.0, -5600.0, 800.0), (0, 0, 1)]
    CAM_ROUTE = [(3200.0, -1900.0, 4300.0), (900.0, -5700.0, 600.0), (0, 0, 1)]
    # the hood from the aisle's north-west: the unit's camera mast stands at its east end, so from the north-east it
    # stood in front of the intake tray
    CAM_HOOD = [(250.0, -3650.0, 2750.0), (1450.0, -6300.0, 900.0), (0, 0, 1)]
    CAM_HOOD_IN = [(600.0, -4650.0, 3150.0), (1350.0, -6450.0, 980.0), (0, 0, 1)]      # over the arm, through the sash
    sc.cam = list(CAM_CHARGER)
    sc.view_angle = 36.0
    gauges(Unit="MiR250 + UR10e, on its charger", Carrying="1 L sieve-wash IPA, capped")
    say("1/4 The bottle trip", "Liquid waste leaves a station only in the capped bottle it was made in. One class a trip: "
        "this unit carries a 1 L bottle of sieve-wash IPA, its fines kept wet, in the spill tray on its deck.")
    deck_pt = world_of("wc_carrier", (0, 0, 120.0))
    step(3.2, None, hold=1.0, labels=[("Spill tray on the deck: one capped 1 L bottle,\nsieve-wash IPA with Al fines "
                                       "(red band, labelled)", tuple(deck_pt), (0.06, 0.40))])
    pts = [(u.pose[0], AISLE_Y), (2500.0, AISLE_Y), (2500.0, y_s), (x_s, y_s)]
    f, secs = route(pts, end_heading=hd_d, reverse_first=True)
    gauges(Unit="MiR250 + UR10e, to the fume hood", Carrying="1 L sieve-wash IPA, capped")
    say("1/4 The bottle trip", "It drives to the ducted fume hood's dock. Never the IPA and the Weck's together, never "
        "the acid and the sulfide, never anything aqueous with powder waste: the unit's job list knows each bottle's class.")
    arm_step("drive to the hood", min(secs, 12.0), f, hold=0.3, cam=CAM_ROUTE)
    step(1.6, None, hold=0.2, cam=CAM_HOOD)

    # -- take the bottle off the deck
    gauges(Unit="MiR250 + UR10e, at the fume hood", Carrying="1 L sieve-wash IPA, capped")
    say("1/4 The bottle trip", "At the hood the arm takes the bottle out of the spill tray by its cap.")
    cap_deck = world_of("wc_carrier", (0.0, 0.0, CARRIER["floor"] + CAP_TCP))
    cap_nest = hw((nest[0], nest[1], nest[2] + CAP_TCP))
    cap_e = hw((e0[0], e0[1], WS.EMPTIES_Z + CAP_TCP))
    app_d, app_h, app_e, app_d2 = plan["app_d"], plan["app_h"], plan["app_e"], plan["app_d2"]
    T_deck = tcp(cap_deck, app_d)
    T_deck_back = tcp(cap_deck - app_d * 110.0, app_d)
    arm_step("to the deck bottle", 2.0, RB.both(rb.joint_to(Tw=T_deck_back), rb.grip_to(OPEN)), cam=CAM_HOOD_IN)
    arm_step("onto its cap", 1.0, rb.line_to(T_deck))
    arm_step("close", 0.5, rb.grip_to(GRIP))
    rb.grasp("wc_ipa")
    arm_step("lift", 0.9, rb.line_to(tcp(cap_deck + np.array([0, 0, 95.0]), app_d)))

    # -- into the hood under the sash, down into the intake tray's empty nest
    T_in = tcp(cap_nest + np.array([0, 0, 70.0]), app_h)
    T_stage = tcp(cap_nest + np.array([0, 0, 70.0]) - app_h * 330.0, app_h)
    T_nest = tcp(cap_nest, app_h)
    say("1/4 The bottle trip", "Under the raised sash (18 in), inside the hood's airflow, the arm sets it in the intake "
        "tray's empty nest: one nest per class, each in its own spill tray.")
    labels_hood = [("Intake tray: closed bottles only,\none nest per class", tuple(hw((150.0, -300.0, 1000.0))),
                    (0.06, 0.30)),
                   ("Sash raised to its 18 in stop", tuple(hw((-300.0, WS.YF + 35, 1430.0))), (0.06, 0.16)),
                   ("Solvent cabinet (yellow doors)", tuple(hw((-420.0, WS.YF + 30, 700.0))), (0.06, 0.72)),
                   ("Acid cabinet (blue doors)", tuple(hw((420.0, WS.YF + 30, 700.0))), (0.80, 0.72))]
    arm_step("to the stage outside the sash", 2.2, rb.joint_to(Tw=T_stage), labels=labels_hood)
    arm_step("in under the sash", 1.4, rb.line_to(T_in))
    arm_step("down into the nest", 1.0, rb.line_to(T_nest))
    arm_step("open", 0.5, rb.grip_to(OPEN), hold=0.1)
    rb.release("wc_surface")
    gauges(Unit="MiR250 + UR10e, at the fume hood", Carrying="nothing: the bottle is in the intake tray")
    arm_step("up off the cap", 0.5, rb.line_to(tcp(cap_nest + np.array([0, 0, 25.0]), app_h)))
    arm_step("out of the hood", 1.4, rb.line_to(tcp(cap_nest + np.array([0, 0, 25.0]) - app_h * 330.0, app_h)))

    # -- an empty from the rack beside it, out, into the spill tray
    T_e = tcp(cap_e, app_e)
    T_e_stage = tcp(cap_e - app_e * 300.0, app_e)
    say("1/4 The bottle trip", "It takes an empty 1 L bottle from the rack beside the tray. The arm never opens, pours or "
        "combines waste: a person consolidates, in the hood, on the day shift.")
    arm_step("to the stage in front of the empty", 1.8, rb.joint_to(Tw=T_e_stage),
             labels=[("Empty 1 L bottles, labelled\nwhen they go out", tuple(hw((e0[0], e0[1], WS.EMPTIES_Z + 120.0))),
                      (0.80, 0.30))])
    arm_step("in to its cap", 1.4, rb.line_to(T_e))
    arm_step("close", 0.5, rb.grip_to(GRIP))
    rb.grasp(empties[0])
    gauges(Unit="MiR250 + UR10e, at the fume hood", Carrying="an empty 1 L bottle")
    arm_step("lift", 0.6, rb.line_to(tcp(cap_e + np.array([0, 0, 40.0]), app_e)))
    arm_step("out of the hood", 1.4, rb.line_to(tcp(cap_e + np.array([0, 0, 40.0]) - app_e * 300.0, app_e)))
    T_deck2 = tcp(cap_deck, app_d2)
    arm_step("over the spill tray", 2.0, rb.joint_to(Tw=tcp(cap_deck + np.array([0, 0, 95.0]), app_d2)))
    arm_step("down into it", 0.9, rb.line_to(T_deck2))
    arm_step("open", 0.5, rb.grip_to(OPEN))
    rb.release("wc_carrier")
    arm_step("off the cap", 0.9, RB.both(rb.line_to(tcp(cap_deck - app_d2 * 110.0, app_d2)), rb.grip_to(0.0)))
    gauges(Unit="MiR250 + UR10e, at the fume hood", Carrying="an empty 1 L bottle",
           Logged="1 L sieve-wash IPA, sieve cell, 0.8 L")
    say("1/4 The bottle trip", "The arm parks. The delivery is logged (bottle, station, volume, time), so the pickup "
        "request to BYU Risk Management can be filled from the log.")
    arm_step("park", 2.0, rb.joint_to(PARK), hold=1.4, still=True)

    # -- the unit leaves for its next job
    f, secs = route([(2500.0, y_s), (2500.0, AISLE_Y), (3600.0, AISLE_Y)], end_heading=0.0, reverse_first=True)
    gauges(Unit="MiR250 + UR10e, to its next job", Carrying="an empty 1 L bottle")
    step(min(secs, 7.0), f, hold=0.1, cam=CAM_HOOD)

    # ================================================================== 2. the cabinets
    CAM_CAB = [(800.0, -4300.0, 1350.0), (1550.0, -6500.0, 520.0), (0, 0, 1)]     # the dock's post left of the doors
    gauges()

    def see_through(v):
        for n in hood_body:
            sc.alpha[n] = 1.0 - v
        for n in waste_doors:
            sc.alpha[n] = 1.0 - v
        for n in ghost:
            sc.alpha[n] = ghost_op[n] * v if v > 0 else 0.0
        for n in contents:
            sc.alpha[n] = v

    say("2/4 The cabinets", "The hood's base is two vented cabinets. A person moves each day's bottles into them, checks "
        "labels and dates, and files the pickup request.")
    step(2.6, None, hold=0.1, cam=CAM_CAB, va=40.0)
    lab_cab = [("Solvent cabinet: IPA with Al fines in a grounded can,\nrinse IPA, Form Wash IPA with resin, used BN cans",
                tuple(hw((-330.0, WS.YF + 40.0, 560.0))), (0.04, 0.24)),
               ("Acid cabinet: Acid Aqueous on one shelf, Weck's\n(base, oxidizer) on the other, each in its own tray",
                tuple(hw((330.0, WS.YF + 40.0, 300.0))), (0.96, 0.30))]
    say("2/4 The cabinets", "Solvent cabinet: the sieve-wash IPA with its Al fines in a grounded can, the rinse IPA, the "
        "Form Wash IPA with resin and the used BN cans. Acid cabinet: Acid Aqueous and Weck's a shelf apart, each in its "
        "own tray.")
    step(1.6, see_through, hold=4.8, labels=lab_cab)
    step(1.2, lambda v: see_through(1.0 - v), hold=0.1)

    # ================================================================== 3. the powder point
    # high, so the fire point's B570 post, its Super D pail and the sign in front don't hide the pails behind them
    pp_cam = [(-5250.0, -3050.0, 4300.0), (-5200.0, -650.0, 250.0), (0, 0, 1)]
    pp_cam2 = [(-6300.0, -2800.0, 3900.0), (-5150.0, -700.0, 250.0), (0, 0, 1)]
    an = PP.ANCHORS
    say("3/4 The powder point", "Powder waste stays where it is made: the powder point stands in the atomizer's area, "
        "behind the rePowder's fire point, with a vacuum, a pail and a lid for each alloy family.")
    step(5.0, None, hold=0.4, cam=pp_cam, va=34.0)
    lab_pp = [("118EXP, Al family (blue band),\non wall power, its wand in the holster", an["Al vac"], (0.05, 0.22)),
              ("118EXP, Cu family (orange band)", an["Cu vac"], (0.62, 0.15)),
              ("Pail per family for sealed liners:\nlid set on, not crimped; bonded", an["Al pail"], (0.80, 0.36)),
              ("Cu-family pail", an["Cu pail"], (0.84, 0.50))]
    say("3/4 The powder point", "Each family has its own 118EXP and its own grounded steel pail: Al and Cu residues never "
        "share a bin (aluminium with copper oxide is a thermite pair).")
    step(1.2, None, hold=4.4, labels=lab_pp)
    lab_pp2 = [("Solid Material bucket (Risk Management's),\nlined: waste powder and sweepings", an["bucket"],
                (0.78, 0.26)),
               ("Used filters, in dry sand,\nin a small grounded can", an["sand"], (0.05, 0.62)),
               ("Class D: B570 on its post,\nSuper D pail and scoop", an["class D"], (0.30, 0.80)),
               ("COMBUSTIBLE METAL POWDER IN USE", an["sign"], (0.70, 0.66))]
    say("3/4 The powder point", "A person seals each liner in place and lifts it into its family's pail; the arms don't. "
        "Powder waste never rides a MiR: it leaves the cell only with BYU Environmental Management.")
    step(4.0, None, hold=2.6, labels=lab_pp2, cam=pp_cam2)
    say("3/4 The powder point", "Loose powder and sweepings go in the Solid Material bucket, used filters straight into "
        "dry sand. When a pail is full, the pickup is requested from BYU Risk Management.")
    step(1.0, None, hold=3.4, labels=lab_pp2)

    # ================================================================== 4. where waste waits
    # high over the aisle (round 16, the lead: from y -7400 at 11 m, over the 10.97 m roof line, a cable-tray hanger
    # crossed the middle of the frame; from over the aisle's south lane both places show and nothing hangs in between)
    cam_wide = [(-1900.0, -5900.0, 10400.0), (-1750.0, -3300.0, 0.0), (0, 0, 1)]
    say("4/4 Where waste waits", "Two places on the floor: powder at the powder point by the atomizer, liquids under the "
        "fume hood across the aisle. Waste stays in the room it was made in, incompatible classes apart.")
    step(5.5, None, hold=3.6, cam=cam_wide, va=55.0,
         labels=[("Powder point: the 118EXPs, a pail per family,\nSolid Material bucket, filters in sand",
                  (-5200.0, -650.0, 900.0), (0.05, 0.20)),
                 ("Chemical waste station: the fume hood's\nsolvent and acid cabinets, the intake tray",
                  tuple(hw((0.0, WS.YF, 1000.0))), (0.70, 0.78))])
    print(f"{NAME}: {sc.n} frames, {sc.n / scene.FPS:.1f} s at {scene.FPS} fps", flush=True)
    sc.save()


if __name__ == "__main__":
    movie()
