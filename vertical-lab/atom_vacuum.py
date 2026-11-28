"""The arm vacuums the inside of the rePowder's chamber with the lab's explosion-proof vacuum (PR #353, #303).

Procedure: byu-vcl PR 80's vacuum operating SOP (sections 1-4: continuity before every use, the equalization touch,
vacuum on before the powder, slow passes close to the surface, brush-and-capture, run-on in clean air, off, wait 60 s,
liner check) and DAL's atomizer SOP ("Powder Collection and Cleaning" step 7: "Vacuum with the ATEX vacuum, then wipe.
Never compressed air."; 178_sop.md "Cleaning and maintenance": vacuum first, then wipe; the crevices are the pump port and
the view port). The state at the start: after a run, cold, vented, the door open, the powder already brushed into the
container and the container taken off. Models: atom_nilfisk.py. Notes: notes/atom_vacuum.md.

    python3 runner_guard.py slot --label vac --mem 3000 -- xvfb-run -a python3 atom_vacuum.py
"""
from __future__ import annotations

import json
import math
import os

import numpy as np

import atom_base as AB
import atom_ground as G
import atom_nilfisk as N
import alloy_atomize as AA
import ur_arm
from scene import AUDIT, OUT, PREVIEW, T, R

COMBINED = not AUDIT and not PREVIEW      # the final render also audits every frame (one pass: render queue)

NAME = "atom_vacuum"
M = AB.M
VAC_AT = np.array([-1060.0, -250.0])          # the vacuum's bin axis, model frame (ours: layout)
STN_AT = np.array([-520.0, -200.0])           # our station's post
VAC_YAW = 90.0                                # the vacuum turned so its inlet faces back (+y), away from the station
MIR_PARK = (-520.0, -1150.0, 0.0)             # MiR250 2 in front of the station, the arm's base at y -1020
MIR_START = (900.0, -2300.0, 0.0)
PAIL_AT = np.array([-1140.0, -760.0])
EXT_AT = np.array([-1150.0, -1150.0])
SIGN_AT = np.array([-1210.0, -1560.0])
GROUND_BAR = np.array([-1000.0, 60.0])        # the building ground point the area's bonds go to (assumed place)
GRIP_FIN = ur_arm.close_for(N.FIN_T + 0.3)
OPEN = 0.25
CUT = [AB.g("chamber"), AB.g("bowl")]
CAM_IN_EYE, CAM_IN_AT = (60.0, -1700.0, 1100.0), (60.0, 0.0, 760.0)   # straight into the cut chamber


def place(sc, meshes, group, Mx, parent="static"):
    for name, (mesh, col) in meshes.items():
        sc.add(f"{group}/{name}", mesh, col, group, specular=0.5)
    sc.gmat[group] = Mx
    if parent:
        sc.parent[group] = parent


def vac_pt(name):
    """A named point on the vacuum (atom_nilfisk.vacuum_local), in the model frame."""
    a = math.radians(VAC_YAW)
    x, y, z = N.vacuum_local(name)
    return np.array([VAC_AT[0] + x * math.cos(a) - y * math.sin(a), VAC_AT[1] + x * math.sin(a) + y * math.cos(a), z])


def W2(p):
    return AB.W(p)


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


# ------------------------------------------------------------------------------------------------ the wand's poses
class Wand:
    """The wand assembly's pose from where its tool tip is and which way it points, and the TCP that holds it."""

    def __init__(self, sc):
        self.sc = sc
        self.tool = "crevice"

    def frame(self, tip, d, hint) -> np.ndarray:
        """World 4x4 of the wand frame with the tool's tip at model point `tip`, pointing along d (model), the fin
        towards `hint` (model direction), as near as it can be square to the wand."""
        z = -unit(d)
        h = np.asarray(hint, float) - (np.asarray(hint, float) @ z) * z
        f = unit(h)
        y = -f
        x = np.cross(y, z)
        Mx = np.eye(4)
        Mx[:3, 0], Mx[:3, 1], Mx[:3, 2] = x, y, z
        Mx[:3, 3] = np.asarray(tip, float) + (N.WAND_L + N.tool_reach(self.tool)) * z
        return AB.WT(Mx)

    def tcp(self, tip, d, hint) -> np.ndarray:
        return self.frame(tip, d, hint) @ N.grasp_local((0, -1, 0))

    def hanging(self, top_pt) -> np.ndarray:
        """The wand hanging nose down with its collar's underside at model point top_pt, the fin to -y."""
        Mx = np.eye(4)
        Mx[:3, 3] = np.asarray(top_pt, float) + np.array([0, 0, N.COLLAR_AT + N.COLLAR_L / 2])
        return AB.WT(Mx)


def refresh_held(sc, rb):
    """What the arm holds changed under the same group (a tool on or off the wand): drop the checkers' caches."""
    chks = [rb._checker] if rb._checker is not None else []
    if sc.auditor is not None:
        chks += list(getattr(sc.auditor, "checkers", {}).values())
    for c in chks:
        c.held_group = None


def hose_check(sc, log):
    """The hose against everything but its own two fittings (the wand and its tools, the vacuum's inlet) and the floor
    and its tape (the hose lies on them): FCL on the drawn tube every audited frame. The arm audit leaves the hose out
    (it is a soft part, joined to the held wand), so this is its own check."""
    import fcl
    import collide
    w = getattr(sc, "_collide_world", None)
    if w is None:
        return
    w.refresh()
    m = sc.actors["vac hose"].GetMapper().GetInput()
    tri = collide._tris(m)
    if tri is None:
        return
    v, f = tri
    bvh = fcl.BVHModel()
    bvh.beginModel(len(v), len(f))
    bvh.addSubModel(v, f)
    bvh.endModel()
    hose_obj = fcl.CollisionObject(bvh, fcl.Transform())
    hb = collide.Body("vac hose", "static", v, f)
    hb.src = (v, f)
    hb.place(np.eye(4))
    lo, hi = v.min(0), v.max(0)
    skip = {"vac:wand", "vac:crevice", "vac:brush"}
    snap = w.current(skip)
    log["frames_checked"] += 1
    hit_now = []
    for b, blo, bhi, Mx in snap.items:
        if b.name in ("vac hose", "vac:body/vac inlet") or bhi[2] <= 6.0 or b.name.startswith("vac ground cable"):
            continue
        if (blo > hi).any() or (bhi < lo).any():
            continue
        if b.pending is not None:
            b.ensure()
            b.place(Mx)
        if collide._hit(hose_obj, b.obj):
            hit_now.append((b.name, collide.depth(hb, b, upto=3.0)))
    if hit_now:
        log["frames_with_contact"] += 1
        if any(d > 3.0 for _, d in hit_now):
            log["frames_through"] = log.get("frames_through", 0) + 1
        for nm, d in hit_now:
            log["hits"].setdefault(nm, []).append((sc.n, d))


def tcp_of(wand_world) -> np.ndarray:
    return wand_world @ N.grasp_local((0, -1, 0))


def main():
    sc, ma, mb = AB.build(NAME, "Vertical cloud lab: the explosion-proof vacuum, and the arm vacuuming the chamber")
    AB.set_joints(sc, door=1.0, clamp0=1.0, clamp1=1.0)
    for grp in ("container", "splash"):
        sc.show(sc.members(AB.g(grp)), 0.0)
    AB.mir_at(ma, "right")
    AB.mir_at(mb, MIR_START)
    rb = mb.rb
    sc.soft = set(getattr(sc, "soft", set()))
    # ---- ground within reach (atom_ground.py, notes/atom_vacuum.md "Ground within reach"): a bonded floor plate at each
    # spot a MiR250 works, its leads in a floor channel to the ground bar; two sprung shoes and a bond lamp on each MiR250.
    # MiR250 1 has been parked at the right since before the clip: its shoes are down and its lamp green.
    rects = G.plate_rects(["vacuum", "right"])
    for name, (mesh, col) in {**G.plate_meshes(rects), **G.channel_meshes(rects)}.items():
        sc.add(name, mesh.translate(AB.RP, inplace=False), col, "static", specular=0.35)
    G.add_shoes(sc, ma, down=1.0)
    G.add_lamp(sc, ma, "green")
    G.add_shoes(sc, mb, down=0.0)
    G.add_lamp(sc, mb, "amber")
    shoes_b = G.shoe_points(MIR_PARK)
    plate_b = next(r for r in rects if r[0] <= shoes_b[0][0] <= r[1] and r[2] <= shoes_b[0][1] <= r[3])

    # ---- the area: vacuum, pail, extinguisher, sign, station, ground bonds
    place(sc, N.vacuum_meshes(), "vac:body", AB.WT(T((*VAC_AT, 0)) @ R((0, 0, 1), VAC_YAW)))
    place(sc, N.pail_meshes(), "vac:pail", AB.WT(T((*PAIL_AT, 0))))
    place(sc, N.extinguisher_meshes(), "vac:ext", AB.WT(T((*EXT_AT, 0)) @ R((0, 0, 1), 90)))
    place(sc, N.sign_meshes(), "vac:sign", AB.WT(T((*SIGN_AT, 0))))
    stn = N.station_meshes()
    place(sc, stn, "vac:station", AB.WT(T((*STN_AT, 0))))
    for nm in N.SOFT:
        if f"vac:station/{nm}" in sc.actors:
            sc.soft.add(f"vac:station/{nm}")
    sp = {k: v + np.r_[STN_AT, 0] for k, v in N.station_points().items()}
    lug = vac_pt("ground_lug")
    gb = np.r_[GROUND_BAR, 0.0]
    sc.add("vac ground bar", N._box(gb[0] - 60, gb[0] + 60, gb[1] - 15, gb[1] + 15, 0, 40).translate(AB.RP, inplace=False),
           (0.55, 0.45, 0.25), "static")
    cables = [[lug, lug + (60, -20, -95), np.array([-790.0, -480.0, 8.0]), np.array([-790.0, 30.0, 8.0]),
               gb + (60, 0, 8), gb + (0, -16, 25)],
              [np.r_[STN_AT, 0] + (0, 40, 40), np.r_[STN_AT, 0] + (-120, 120, 6), gb + (60, -60, 6), gb + (40, -16, 25)],
              [np.r_[PAIL_AT, 0] + (90, 100, 300), np.r_[PAIL_AT, 0] + (140, 160, 6), gb + (-120, -200, 6),
               gb + (-40, -16, 25)]]
    for k, pts in enumerate(cables):
        pts = np.array(pts, float)
        pts[:, 2] = np.maximum(pts[:, 2], 4.0)
        sc.add(f"vac ground cable {k}", N.tube_along(pts + AB.RP, 4.0, 10), N.GRN_YEL, "static")

    # ---- the wand and the two tools
    wand = Wand(sc)
    place(sc, N.wand_meshes(), "vac:wand", wand.hanging(sp["holster"]), parent=None)
    crev, brush = N.crevice_meshes(), N.brush_meshes()
    fit = T((0, 0, -N.WAND_L - N.SEAT_GAP + N.TOOL_COLLAR[0]))
    place(sc, crev, "vac:crevice", fit @ R((0, 0, 1), 90), parent="vac:wand")   # the slot's wide side along y_w
    place(sc, brush, "vac:brush", AB.WT(T(sp["pocket_b"]) @ R((0, 0, 1), 90)), parent=None)
    sc.soft.add("vac:brush/dust brush bristles")
    # the probe column beside the pad, its probes at the joints of the wand standing on the pad with the crevice tool
    reach = N.WAND_L + N.tool_reach("crevice")
    z0 = sp["pad"][2] + 1.0
    joints = [(z0 + N.tool_reach("crevice") + 14, N.WAND_OD / 2),          # the wand just above the tool joint
              (z0 + reach - N.COLLAR_AT - N.COLLAR_L / 2 - 25, N.WAND_OD / 2),   # the wand under our collar
              (z0 + reach + 30, N.CUFF_OD / 2)]                             # the cuff
    bar, probes = N.probe_column(joints)
    sc.add("vac:station/probe column", bar, N.OURS, "vac:station")
    sc.add("vac:station/stn spring probes", probes, N.BRASS, "vac:station")
    sc.soft.add("vac:station/stn spring probes")

    # ---- the hose: from the vacuum's inlet to the wand's cuff, relaxed every frame
    inlet = vac_pt("inlet")
    t_in = (0.0, 1.0, 0.0)

    def cuff_end():
        Wd = sc.world("vac:wand")
        return (Wd @ np.r_[0, 0, N.CUFF_L - 20.0, 1.0])[:3] - AB.RP, Wd[:3, 2]

    b0, tb0 = cuff_end()
    guide = [inlet, inlet + (0, 130, -40), np.array([-1050.0, 140.0, 26.0]), np.array([-900.0, 70.0, 26.0]),
             np.array([-600.0, 60.0, 26.0]), np.array([-420.0, 40.0, 26.0]), np.array([-400.0, -60.0, 600.0]),
             np.array([-400.0, -110.0, 1180.0]), np.array([-400.0, -200.0, 1320.0]), np.array([-400.0, -300.0, 1330.0]),
             b0 + (0, 0, 87.0), b0]
    hose = N.Hose(inlet, t_in, b0, tb0, guide=guide)

    def obstacles():
        x, y = mb.x - AB.RP[0], mb.y - AB.RP[1]
        boxes = [(x - 400, x + 400, y - 290, y + 290, 0, 800),                      # MiR250 2 + cabinet
                 (VAC_AT[0] - 230, VAC_AT[0] + 230, VAC_AT[1] - 300, VAC_AT[1] + 230, 0, 1150),
                 (STN_AT[0] - 30, STN_AT[0] + 30, STN_AT[1] - 30, STN_AT[1] + 30, 0, 1090),
                 (STN_AT[0] - 300, STN_AT[0] + 300, STN_AT[1] - 200, STN_AT[1] + 120, 0, 14),
                 (STN_AT[0] - 215, STN_AT[0] - 30, STN_AT[1] - 155, STN_AT[1] - 30, 0, 205),     # fixture
                 (STN_AT[0] + 135, STN_AT[0] + 270, STN_AT[1] - 205, STN_AT[1] - 90, 0, 285),    # meter
                 (GROUND_BAR[0] - 60, GROUND_BAR[0] + 60, GROUND_BAR[1] - 15, GROUND_BAR[1] + 15, 0, 40),
                 (STN_AT[0] - 260, STN_AT[0] - 195, STN_AT[1] - 75, STN_AT[1] - 45, 150, 1010),  # probe column
                 (STN_AT[0] - 55, STN_AT[0] + 55, STN_AT[1] - 190, STN_AT[1] - 30, 955, 1000),   # holster
                 (STN_AT[0] + 30, STN_AT[0] + 290, STN_AT[1] - 105, STN_AT[1] - 15, 585, 630),   # tool rack
                 (-115, 346, -128, 128, 300, 1150), (-401, -128, -8, 390, 600, 1115),
                 (-880, -420, 120, 340, 0, 260), (PAIL_AT[0] - 150, PAIL_AT[0] + 150, PAIL_AT[1] - 150, PAIL_AT[1] + 150,
                                                  0, 360)]
        caps = []
        for grp, a_, b_, r_ in link_caps:                  # each arm link as a capsule along its own mesh's long axis
            Wl = sc.world(grp)
            caps.append(((Wl @ np.r_[a_, 1.0])[:3] - AB.RP, (Wl @ np.r_[b_, 1.0])[:3] - AB.RP, r_))
        Wd = sc.world("vac:wand")
        top = Wd[:3, 3] - AB.RP
        caps.append((top - Wd[:3, 2] * 30, top - Wd[:3, 2] * (N.WAND_L + 200), 26.0))
        return boxes, caps

    def hose_hook(_sc):
        b, tb = cuff_end()
        hose.set_ends(inlet, t_in, b, tb)
        hose.boxes, hose.caps = obstacles()
        hose.relax(18)
        sc.set_mesh("vac hose", hose.mesh().translate(AB.RP, inplace=False))

    link_caps = []
    # (round 14 tried the 2F-85's knuckles and fingers as capsules too: the hose then lay in the gripper's left finger
    # for 41 frames instead of 50 of 1836, but in the rePowder's vacuum pump for 140 instead of 16; left out)
    for l in ("shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3", "gr_base", "gr_camera"):
        grp = f"{rb.prefix}_{l}"
        pts = [np.asarray(sc.actors[n].GetMapper().GetInput().GetPoints().GetData()) for n in sc.members(grp)
               if sc.actors[n].GetMapper().GetInput() is not None and sc.actors[n].GetMapper().GetInput().GetNumberOfPoints()]
        if not pts:
            continue
        pts = np.vstack(pts)
        c0 = pts.mean(0)
        ax = np.linalg.svd(pts - c0, full_matrices=False)[2][0]
        t = (pts - c0) @ ax
        rad = np.linalg.norm((pts - c0) - np.outer(t, ax), axis=1)
        link_caps.append((grp, c0 + ax * t.min(), c0 + ax * t.max(), float(np.percentile(rad, 95))))
    hose.boxes, hose.caps = obstacles()
    hose.relax(300)
    sc.add("vac hose", hose.mesh().translate(AB.RP, inplace=False), N.BLACK, "static", specular=0.2)
    sc.soft.add("vac hose")
    sc.frame_hooks.insert(0, hose_hook)
    hose_log = {"frames_checked": 0, "frames_with_contact": 0, "hits": {}}
    if COMBINED:
        import collide
        sc.auditor = collide.Auditor(sc)
        sc.frame_hooks.append(sc.auditor)
    if AUDIT or COMBINED:
        sc.frame_hooks.append(lambda _sc: hose_check(sc, hose_log))

    def gauges(**kv):
        AB.status(sc, **kv)

    gauges(Vacuum="off", Joints="not checked", Liner="3 % (from the last session's log)", Timer="",
           Bond="MiR250 1 bonded (0.1 ohm); MiR250 2 not parked")
    eye0, at0 = (600, -3200, 2400), (-760, -500, 450)

    # ============================================================================ 1. the area
    sc.step("1/10 Area", "The vacuum station by the atomizer: the Nilfisk 118EXP grounded to the building's ground "
            "bar, a grounded steel pail with its lid set on, a 30 lb Class D extinguisher and the sign at the tape. "
            "Where a MiR250 parks to work, a bonded steel plate is set flush in the floor (ours).",
            4.0, cam_to=AB.cam(eye0, at0), hold=1.6,
            labels=[("Nilfisk CFM 118EXP (lab has)", W2((VAC_AT[0], VAC_AT[1], 980)), (0.10, 0.30)),
                    ("Ground cable to the ground bar", W2((gb[0] - 40, gb[1] - 60, 30)), (0.30, 0.18)),
                    ("Uline S-7344 pail, lid set on, not crimped", W2((PAIL_AT[0], PAIL_AT[1], 380)), (0.05, 0.55)),
                    ("Class D, 30 lb NaCl (Amerex B570)", W2((EXT_AT[0], EXT_AT[1], 800)), (0.12, 0.72)),
                    ("Our station: holster, tool rack, continuity fixture", W2((STN_AT[0], STN_AT[1] - 150, 1040)),
                     (0.55, 0.22)),
                    ("Bonded floor plate (ours)", W2(((plate_b[0] + plate_b[1]) / 2, plate_b[2] + 40, 2)),
                     (0.55, 0.80))])
    sc.step("1/10 Area", "Sign: COMBUSTIBLE METAL POWDER IN USE. Authorized personnel only. NO water, NO compressed "
            "air (vacuum SOP 2.3). Every loose metal object in the zone is bonded or removed.", 2.4,
            cam_to=AB.cam((-850, -2700, 1100), (-1210, -1560, 650)), hold=1.2)
    # ============================================================================ 2. the chamber
    AA.set_cut(sc, 0.0, CUT)
    sc.step("2/10 The chamber", "After a run: cold, vented, door open. The powder was already brushed into the "
            "container and the container taken off (DAL SOP steps 2-3), so it is not drawn.", 3.0,
            cam_to=AB.cam((200, -1900, 1500), (-150, 50, 850)), hold=1.6,
            labels=[("Open door with the stack", W2((-270, 120, 1110)), (0.30, 0.20)),
                    ("Container removed", W2((M.CHUTE_X, 0, 300)), (0.70, 0.70))])
    # ============================================================================ 3. MiR250 2 parks
    up, secs = AB.mir_drive(mb, MIR_PARK)
    gauges(Bond="MiR250 1 bonded (0.1 ohm); MiR250 2 driving, its shoes up")
    sc.step("3/10 MiR250 2", "MiR250 2 drives in and parks in front of the station, clear of the hose and the "
            "vacuum, its two ground shoes lifted while it drives.", secs, up,
            cam_to=AB.cam((1100, -3300, 2300), (-400, -1300, 500)), hold=0.6)
    # ---- bonded before the arm moves (atom_ground.py; notes/atom_vacuum.md, "Ground within reach")
    shoe_c = (shoes_b[0] + shoes_b[1]) / 2
    lamp_w = mb.world(G.LAMP_AT)
    CAM_SHOE = AB.cam((shoe_c[0] + 1550, shoe_c[1] - 1750, 1000), (shoe_c[0] - 170, shoe_c[1] - 170, 330))
    gauges(Bond="MiR250 2: shoes coming down")
    sc.step("3/10 Bond", "It lowers its two sprung copper-graphite shoes onto the floor plate (ours). Every spot where "
            "a MiR250 works at the atomizer has such a plate, its leads run in a floor channel to the area's ground "
            "bar, so nobody clips a lead on and nothing trails across the floor.", 1.6, G.shoes_anim(sc, mb, 0.0, 1.0),
            cam_to=CAM_SHOE, hold=0.6,
            labels=[("Two sprung shoes, copper-graphite (ours)", W2(shoe_c + (0, -60, 30)), (0.10, 0.70)),
                    ("Bonded floor plate, leads to the ground bar", W2((shoe_c[0] + 100, plate_b[2] + 30, 2)),
                     (0.52, 0.86)),
                    ("Bond lamp", tuple(lamp_w), (0.70, 0.24))])
    gauges(Bond="MiR250 2: shoe-plate-shoe 0.12 ohm, plate-bar 0.05 ohm (each <= 1): BONDED")

    def bonded(u):
        G.lamp(sc, mb, "green" if u > 0.25 else "amber")
    sc.step("3/10 Bond", "Two readings before the arm may move: the MiR's meter, shoe to shoe through the plate (both "
            "shoes on metal), and the station's monitor, the plate through its two leads to the bar. Both under 1 "
            "ohm (ours; NFPA 77 finds under 10 ohm usual for a sound bond): the lamp turns green. Readings "
            "illustrative.", 1.2, bonded, hold=2.6,
            labels=[("Bond lamp: green", tuple(lamp_w), (0.70, 0.24))])
    # ============================================================================ 4. take the wand
    W0 = sc.world("vac:wand")
    g_tcp = tcp_of(W0)
    pre = g_tcp @ T((0, 0, -90))
    sc.step("4/10 Take the wand", "The arm reaches for the wand in our holster: the 2F-85 closes on the flats of our "
            "clamp-on fin. Nothing is drilled into the Nilfisk wand.", 3.0, rb.joint_to(Tw=pre),
            cam_to=AB.cam((350, -1350, 1450), (-560, -420, 950)), hold=0.3)
    sc.step("4/10 Take the wand", "In onto the fin.", 1.2, rb.line_to(g_tcp), hold=0.2)
    sc.step("4/10 Take the wand", "Grip.", 0.8, rb.grip_to(GRIP_FIN), hold=0.2)
    rb.grasp("vac:wand")
    lift = T((0, 0, 70)) @ g_tcp
    sc.step("4/10 Take the wand", "Lift: the locating pin comes out of the holster's hole, the collar off the fork.",
            1.4, rb.line_to(lift), hold=0.2)
    out_ = T((0, -140, 20)) @ lift
    sc.step("4/10 Take the wand", "Out of the fork, towards the arm.", 1.4, rb.line_to(out_), hold=0.2)
    # ============================================================================ 5. continuity check
    pad = sp["pad"] + np.array([0, 0, 1.0])
    Wpad = AB.WT(T(pad + np.array([0, 0, N.WAND_L + N.tool_reach("crevice")])))
    pre_pad = T((0, 0, 60)) @ tcp_of(Wpad)
    sc.step("5/10 Continuity", "To the continuity fixture (ours): the tool tip goes onto the bonded spring pad, "
            "spring probes touch each joint, a relay box switches the milliohm meter between them.", 3.2,
            rb.joint_to(Tw=pre_pad), cam_to=AB.cam((250, -1000, 850), (-650, -250, 500)), hold=0.2)
    sc.step("5/10 Continuity", "Down onto the pad.", 1.6, rb.line_to(T((0, 0, -3)) @ tcp_of(Wpad)), hold=0.2,
            labels=[("EXTECH 380560 class milliohm meter", W2(sp["meter"]), (0.12, 0.62)),
                    ("Spring pad, bonded", W2(sp["pad"]), (0.30, 0.82))])
    readings = dict(tool_to_wand="0.04", wand_to_coupling="0.02", coupling_to_cuff="0.03", hose="4.1",
                    body_to_ground="0.2")
    gauges(Joints="tool-wand 0.04, wand-coupling 0.02, coupling-cuff 0.03 ohm (each <= 0.1); hose 4.1 ohm "
                      "(<= 10^4); body-ground 0.2 ohm (< 1)")
    sc.step("5/10 Continuity", "Each joint must read 0.1 ohm or less (the OEM manual, UL 1213 par. 22), or the run "
            "stops. Readings shown are illustrative: the lab's crevice tool read open on 2026-08-19.", 0.6, hold=3.4)
    sc.step("5/10 Continuity", "Lift off the pad.", 1.0, rb.line_to(T((0, 0, 70)) @ tcp_of(Wpad)), hold=0.1)
    # ============================================================================ 6. equalization touch, vacuum on
    btn = sp["button"] + np.array([0, 0, 1.0])
    Wbtn = AB.WT(T(btn + np.array([0, 0, N.WAND_L + N.tool_reach("crevice")])))
    gauges(Joints="passed, logged")
    sc.step("6/10 Equalize", "Equalization touch: the tool tip on the bonded ground button beside the pad, away from "
            "the powder (vacuum SOP 3.1).", 1.6, rb.line_to(T((0, 0, 60)) @ tcp_of(Wbtn)), hold=0.1)
    sc.step("6/10 Equalize", "Touch.", 1.2, rb.line_to(T((0, 0, -3)) @ tcp_of(Wbtn)), hold=0.4)
    sc.step("6/10 Equalize", "Clear.", 0.8, rb.line_to(T((0, 0, 90)) @ tcp_of(Wbtn)), hold=0.1)
    gauges(Vacuum="ON (130 CFM, 69 in water lift)")
    sc.step("6/10 Vacuum on", "Vacuum ON before the tool goes near the powder (SOP 3.2). The SOP's switch is on the "
            "motor head: a relay on its supply is ours, to be cleared with Nilfisk and EHS.", 0.5, hold=1.6,
            labels=[("ON", W2(vac_pt("switch")), (0.18, 0.40))])
    # ============================================================================ 7. passes inside the chamber
    AA.set_cut(sc, 0.0, CUT)
    hint = (0.0, -1.0, 0.0)

    def pass_(label, caption, pts, d_of, seconds, cam=None, hint_=hint, hold=0.3, labels=()):
        poses = [wand.tcp(p, d_of(p), hint_) for p in pts]
        first = poses[0]
        sc.step(label, caption, max(2.0, seconds * 0.35), rb.joint_to(Tw=T((0, 0, 0)) @ first), cam_to=cam,
                hold=0.1, labels=labels)
        sc.step(label, caption, seconds, AA.follow(rb, poses), hold=hold)

    def door_dir(p, pivot=(-170.0, -30.0, 965.0)):
        return unit(np.asarray(p, float) - np.asarray(pivot, float))

    cut_on = AA.set_cut
    CAM_IN = AB.cam(CAM_IN_EYE, CAM_IN_AT)
    sc.step("7/10 Into the chamber", "The chamber is drawn see-through so the passes inside can be seen. The arm stays "
            "outside: only the wand and its tool go through the door.", 1.6, lambda u: cut_on(sc, 0.6 * u, CUT),
            cam_to=AB.cam((-30, -950, 1150), (-40, -100, 1030)), hold=0.4)
    # the view port: round its inside, the tool along the front wall, its tip 9 mm off the wall
    vp = M.VIEWPORT
    ring = [np.array([vp[0] + 34 * math.cos(t), -96.0, 1030.0 + 34 * math.sin(t)])
            for t in np.linspace(math.pi, 3 * math.pi, 25)]
    pass_("7/10 View port", "Round the inside of the view port (one of the two crevices: DAL 178 SOP, T4 6:51), "
          "slowly, the nozzle close to the wall (SOP 3.3-3.4).", ring,
          lambda p: unit((1.0, -0.33, 0.06)), 8.0, cam=AB.cam((-30, -950, 1150), (-40, -100, 1030)),
          hint_=(0.0, -0.15, 1.0))
    # the sloped floor down towards the outlet (the cone the powder runs down), two lanes, 8 mm off the floor
    lanes = []
    for y in (-50.0, 20.0):
        for x in np.linspace(-30.0, 212.0, 9):
            lanes.append(np.array([x, y, M.chamber_floor(x) + 16.0]))
    lane0, lane1 = lanes[:9], lanes[9:][::-1]
    sc.step("7/10 Sloped floor", "Now the chamber is shown cut open at its middle.", 1.0,
            lambda u: cut_on(sc, 0.6 + 0.4 * u, CUT), cam_to=CAM_IN, hold=0.2)
    pass_("7/10 Sloped floor", "Down the 45 deg floor towards the outlet, a lane at a time, at about 30 mm/s, the nozzle 11 mm off.",
          lane0, door_dir, 7.0, cam=CAM_IN)
    pass_("7/10 Sloped floor", "Back up the next lane. The catch bowl, 290 mm past the door at the floor's foot, is out "
          "of the wand's reach with the arm outside: a person vacuums it, and the cone from below.", lane1, door_dir, 7.0)
    # the front-bottom corner along the slope
    corner = [np.array([x, -86.0, M.chamber_floor(x) + 18.0]) for x in np.linspace(40.0, 170.0, 7)]
    pass_("7/10 Corners", "Along the front corner, where the sloped floor meets the front wall.", corner, door_dir, 5.0)
    # ============================================================================ 8. tool change
    pa, pb = sp["pocket_a"], sp["pocket_b"]

    def hang_at(tool_top, dy=0.0, dz=0.0):
        """The wand upright with its fitted tool's spigot top at tool_top (+ offsets)."""
        return AB.WT(T(tool_top + np.array([0, dy, dz + N.WAND_L - N.TOOL_COLLAR[0] + N.SEAT_GAP])))

    # round 14: by way of a pose high and well out in front of the rack. Straight to the pose over pocket A, the joint
    # move took the crevice tool past the station 1.5 mm deep for a frame (round 13's audit, frame 1358)
    sc.step("8/10 Tool change", "Out of the chamber and over to our tool rack, the wand upright.", 3.0,
            rb.joint_to(Tw=tcp_of(hang_at(pa, -260, 330))), cam_to=AB.cam((150, -1050, 900), (-330, -270, 650)),
            hold=0.0)
    sc.step("8/10 Tool change", "Out of the chamber and over to our tool rack, the wand upright.", 1.2,
            rb.line_to(tcp_of(hang_at(pa, -110, 150))), hold=0.1)
    sc.step("8/10 Tool change", "The crevice tool goes into pocket A from the front: its collar slides between our "
            "two slotted plates.", 1.4, rb.line_to(tcp_of(hang_at(pa, -110, 0))), hold=0.1)
    sc.step("8/10 Tool change", "In.", 1.6, rb.line_to(tcp_of(hang_at(pa, 0, 0))), hold=0.2)
    rb.reparent("vac:crevice", "vac:station")          # the tool stays in pocket A, where the wand left it
    refresh_held(sc, rb)
    sc.step("8/10 Tool change", "The arm pulls the wand straight up off the tool's spigot; the upper plate holds the "
            "tool down.", 1.6, rb.line_to(T((0, 0, 80)) @ tcp_of(hang_at(pa, 0, 0))), hold=0.2)
    wand.tool = "brush"
    sc.step("8/10 Tool change", "Over the dust brush in pocket B.", 1.8, rb.line_to(T((0, 0, 80)) @ tcp_of(hang_at(pb, 0, 0))),
            hold=0.1)
    sc.step("8/10 Tool change", "Down onto its spigot (a push fit; about 30 N, assumed).", 1.6,
            rb.line_to(tcp_of(hang_at(pb, 0, 0))), hold=0.2)
    rb.reparent("vac:brush", "vac:wand")
    sc.gmat["vac:brush"] = fit @ R((0, 0, 1), 90)
    refresh_held(sc, rb)
    sc.step("8/10 Tool change", "Out of the pocket to the front, with the brush.", 1.6,
            rb.line_to(tcp_of(hang_at(pb, -110, 0))), hold=0.3)
    # ============================================================================ 9. brush and capture
    pl = M.PLATE_C
    Dm = M.joint_matrix("door", 1.0)
    plc = (Dm @ np.r_[pl, 1.0])[:3]
    nrm = Dm[:3, :3] @ M.STACK_DIR
    along_ = Dm[:3, :3] @ M.PLATE_ALONG                 # from the plate's fixed end (the upper sonotrode) to its free end
    strokes = [plc - nrm * 3.0 + along_ * s for s in np.linspace(14.0, 46.0, 5)]
    pass_("9/10 Brush", "The dust brush on the plate: brush-and-capture, the bristles just kissing it while the "
          "airflow takes what they lift (SOP 3).", strokes, lambda p: -nrm, 5.0,
          cam=AB.cam((250, -900, 1250), (-280, 40, 900)), hint_=(0.0, -1.0, 0.3),
          labels=[("Plate, on the open door", W2(plc), (0.55, 0.25))])
    n_in = Dm[:3, :3] @ np.array([1.0, 0, 0])          # the door's inner face, open: it looks to the front
    band = [np.array([-115.0, -112.0, z]) for z in np.linspace(930.0, 1100.0, 5)] + \
        [np.array([-115.0, y, 1109.0]) for y in np.linspace(-95.0, 60.0, 5)]
    dface = unit(-n_in + np.array([0, 0, -0.25]))
    seal = [(Dm @ np.r_[p, 1.0])[:3] + dface * 3.0 for p in band]
    pass_("9/10 Brush", "Then the door's sealing face, where its seal lands: along the free edge and the top. The "
          "brush cannot meet the 45 deg floor square from the door, so the floor had the crevice tool.", seal,
          lambda p: dface, 6.0, cam=AB.cam((250, -900, 1300), (-260, 120, 980)), hint_=(0.0, -1.0, 0.5))
    # ============================================================================ 10. clear, run-on, off, settle, liner, holster
    clear = T((0, -140, 300)) @ tcp_of(wand.hanging(sp["holster"]))
    sc.step("10/10 Shut down", "Lift the tool clear of the powder, into clean air.", 2.4,
            AB.both(rb.joint_to(Tw=clear), lambda u: cut_on(sc, 1.0 - u, CUT)),
            cam_to=AB.cam((500, -1700, 1500), (-560, -380, 800)), hold=0.2)

    def timer(label, total, unit_):
        def up(u):
            gauges(Timer=f"{label} {u * total:4.0f} / {total:.0f} {unit_}")
        return up

    sc.step("10/10 Shut down", "Run-on in clean air for 20 s to clear the bores (SOP 4.1); time-lapse.", 2.4,
            timer("run-on", 20, "s"), hold=0.3)
    gauges(Vacuum="off")
    sc.step("10/10 Shut down", "OFF, then wait at least 60 s for the dust to settle before anything is opened (SOP "
            "4.2); time-lapse.", 3.0, timer("settle", 60, "s"), hold=0.3)
    gauges(Timer="", Liner="4 % by weight (an assumed load cell, ours): under 25 %, the liner stays")
    sc.step("10/10 Liner", "Liner check: 25 % at most (SOP 4.3). Sealing the liner (gooseneck, 2-3 turns, ESD tape) "
            "and lifting it into the pail stay a person's job.", 0.5, hold=3.6)
    Wh = wand.hanging(sp["holster"])
    # over the holster from 200 mm up, not 90: at 90 the nearest IK branches fold the upper arm onto the wrist, and the
    # one the planner took then swung the upper arm and forearm into the vacuum on the way into the fork
    sc.step("10/10 Holster", "The wand goes back in its holster, its tool hanging down, the pin in the hole.", 3.0,
            rb.joint_to(Tw=T((0, -140, 200)) @ tcp_of(Wh)), cam_to=AB.cam((350, -1350, 1450), (-560, -420, 950)),
            hold=0.1)
    sc.step("10/10 Holster", "Into the fork.", 1.4, rb.line_to(T((0, 0, 70)) @ tcp_of(Wh)), hold=0.1)
    sc.step("10/10 Holster", "Down onto it.", 1.2, rb.line_to(tcp_of(Wh)), hold=0.1)
    rb.release(None)
    sc.step("10/10 Holster", "Let go and back off. Wiping (dry, then a barely damp 70 % IPA wipe) and the log follow.",
            1.4, AB.both(rb.grip_to(OPEN), lambda u: None), hold=0.2)
    # 60 mm off the fin, then up: straight back 120 mm folded the upper arm onto the arm's own wrist 2
    sc.step("10/10 Holster", "", 0.8, rb.line_to(tcp_of(Wh) @ T((0, 0, -60))), hold=0.0)
    sc.step("10/10 Holster", "", 1.0, rb.line_to(T((0, 0, 120)) @ tcp_of(Wh) @ T((0, 0, -60))), hold=1.5)
    meta = dict(readings_illustrative=readings, hose_length_mm=round(hose.length(), 1), grip_close=GRIP_FIN)
    if AUDIT or COMBINED:
        hits = {k: dict(frames=len(v), first=v[0][0], last=v[-1][0], deeper_than_3mm=sum(1 for _, d in v if d > 3.0),
                        max_depth_mm=max(d for _, d in v)) for k, v in hose_log["hits"].items()}
        (OUT / "collisions").mkdir(parents=True, exist_ok=True)
        (OUT / "collisions" / f"{NAME}_hose.json").write_text(json.dumps(dict(
            what="the hose (a relaxed chain, re-meshed every frame) against everything but the wand, its tools, the "
                 "vacuum's inlet and the floor's markings", frames_checked=hose_log["frames_checked"],
            frames_with_contact=hose_log["frames_with_contact"], frames_through=hose_log.get("frames_through", 0),
            depth_note="collide.depth, sampled: 1.5 or 3 = resting against it (touching), more = through it", hits=hits),
            indent=1) + "\n")
        print("hose check:", hose_log["frames_with_contact"], "of", hose_log["frames_checked"], "frames touching,",
              hose_log.get("frames_through", 0), "through;", {k: (v["frames"], v["deeper_than_3mm"], v["max_depth_mm"]) for k, v in hits.items()})
    (OUT / "atom").mkdir(parents=True, exist_ok=True)
    (OUT / "atom" / f"{NAME}_meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    AB.finish(sc)
    if COMBINED:
        sc.auditor.save()


if __name__ == "__main__":
    main()
