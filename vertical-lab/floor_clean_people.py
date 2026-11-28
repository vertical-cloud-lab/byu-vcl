"""The person's part of a floor pass (#366, #303): a visible spill.

Unit 3 (option C in notes/floor_cleaning.md) finishes two lanes along the rePowder's front and checks the floor's
colour. Its camera then sees a visible layer of powder in the aisle by the sieving cell (a dropped cup: ours, an
illustration). That is a person's job, not the robot's. The lab's vacuum SOP, section 8: "For any visible layer on the
floor: restrict access, ventilate, and call EHS". So unit 3 lifts clear, stops its vacuum, keeps 1 m away and messages
the person. The person takes the bulk up with a natural-bristle broom and a conductive dustpan. NFPA 484 (2022)
11.5.1: "conductive, nonsparking scoops and soft brooms as well as brushes that have natural fiber bristles". It goes
into a conductive bag for the grounded pail. Unit 3 then takes the residue (11.5.2: vacuums "only for residual
amounts") and checks the colour again.

    python3 runner_guard.py slot --label fcppl --mem 5000 -- env VIZ3D_FPS=10 xvfb-run -a python3 floor_clean_people.py
    -> out/mp4/floor_clean_people.mp4, out/floor_clean_people.gif, out/floor_clean_people.json (the sub-steps),
       out/collisions/floor_clean_people.json (the arm, audited as it renders: collide.Auditor, the round-11 rules) and
       out/collisions/floor_clean_people_person.json (the person's clearance to unit 3 and the floor plan's machines)

Models: floor_clean_still.build (the area; unit 3, a MiR250 + UR10e + 2F-85, with the 118EXP's wand and our floor
squeegee; the 25 ft hose; the powder point (powder_point.py); the bonding lead and stud), people.Person (MakeHuman's CC0 body, skinned
and dressed). New here, ours: the push broom (a 12 in natural-bristle head on a 1.2 m handle), the lobby dustpan
(conductive, 300 mm wide, on a 0.8 m handle), the spill (a patch 330 x 250 mm and 12 mm deep), and where they are.
"""
from __future__ import annotations

import json
import math

import numpy as np
import pyvista as pv

import alloy_atomize as AA
import atom_nilfisk as N
import floor_cleaning as FC
import floor_clean_still as FS
from scene import AUDIT, OUT, PREVIEW, S, T, R

NAME = "floor_clean_people"
TITLE = "Vertical cloud lab: a visible spill is the person's, the residue unit 3's"
SPILL = np.array([-2300.0, -2660.0])           # ours: a dropped cup's powder in the aisle by the sieving cell
PILE = (165.0, 125.0, 12.0)                     # the patch's half-sizes and depth, mm (ours)
POWDER = (0.60, 0.61, 0.63)                     # Al-Si powder, matte grey
P_START = np.array([1500.0, -3850.0])           # the person comes in along the aisle from the east
P_TURN = np.array([-900.0, -3250.0])
P_WORK = np.array([-1660.0, -2700.0])           # where they stand to sweep, facing west
PAN_LIP = np.array([-2075.0, -2735.0])          # the dustpan's lip on the floor, its mouth to the west
BROOM_Y = -2675.0
BROOM_FROM, BROOM_TO = -2590.0, -2215.0         # the broom head's x at each end of a stroke (towards the pan)
HANDLE = np.array([600.0, 120.0, 985.0])        # the broom's handle, head to the right hand (1.16 m)
PAN_W, PAN_D, PAN_H = 300.0, 240.0, 70.0
WOOD, BRISTLE, PAN_C = (0.62, 0.45, 0.28), (0.80, 0.68, 0.45), (0.17, 0.17, 0.19)


def ell_patch(rx, ry, h) -> pv.PolyData:
    """A low patch of powder: an ellipsoid's cap, its edge feathered into the floor."""
    s = pv.ParametricEllipsoid(rx, ry, h, u_res=48, v_res=24, w_res=8).triangulate()
    return s.clip(normal=(0, 0, -1), origin=(0, 0, 0.5), invert=True).triangulate() if s.n_points else s


def broom_head() -> dict:
    """Ours: a 12 in push broom's head, its long side along local y, the bristles down on z 0; the handle is drawn
    each frame from the head's socket to the hand."""
    blk = FS.box(-32, 32, -152, 152, 38, 78)
    bristle = FS.box(-27, 27, -147, 147, 0.5, 38)
    sock = pv.Cylinder(center=(10, 0, 92), direction=(0.5, 0, 0.87), radius=17, height=36).triangulate()
    return {"broom block": (blk.merge(sock), WOOD), "broom bristles (natural)": (bristle, BRISTLE)}


def pan_meshes() -> dict:
    """Ours: a lobby dustpan, conductive plastic; the origin at the middle of its lip, local +x into the pan."""
    floor_ = FS.box(0, PAN_D, -PAN_W / 2, PAN_W / 2, 0.5, 3.5)
    back = FS.box(PAN_D - 4, PAN_D, -PAN_W / 2, PAN_W / 2, 0.5, PAN_H)
    sides = FS.box(30, PAN_D, -PAN_W / 2, -PAN_W / 2 + 4, 0.5, PAN_H * 0.8).merge(
        FS.box(30, PAN_D, PAN_W / 2 - 4, PAN_W / 2, 0.5, PAN_H * 0.8))
    lid = FS.box(PAN_D * 0.55, PAN_D, -PAN_W / 2, PAN_W / 2, PAN_H - 4, PAN_H)
    return {"dustpan": (floor_.merge(back).merge(sides).merge(lid), PAN_C)}


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def main():
    import collide
    import people
    sc, u1, u3, rb, info = FS.build(clip=True, name=NAME, title=TITLE)
    sc.frame_hooks.insert(0, sc.hose_hook)
    combined = not AUDIT and not PREVIEW
    if combined:
        sc.auditor = collide.Auditor(sc)
        sc.frame_hooks.append(sc.auditor)

    # ---- the spill, the pan's load, the broom and the pan
    sc.add("spill", ell_patch(*PILE), POWDER, "spill", specular=0.05)
    sc.gmat["spill"] = T((*SPILL, 0.0))
    sc.add("pan load", ell_patch(85.0, 95.0, 22.0), POWDER, "panload", specular=0.05)
    for nm, (mesh, col) in broom_head().items():
        sc.add(f"broom/{nm}", mesh, col, "broom", specular=0.2)
    for nm, (mesh, col) in pan_meshes().items():
        sc.add(f"pan/{nm}", mesh, col, "pan", specular=0.3)
    sc.parent["panload"] = "pan"
    sc.gmat["panload"] = T((PAN_D * 0.42, 0.0, 3.5)) @ S((0.02, 0.02, 0.02))
    sc.add("broom handle", N.tube_along(np.array([[0, 0, 0], [0, 0, 1000.0]]), 12.0, 14), WOOD, "static")
    sc.add("pan handle", N.tube_along(np.array([[0, 0, 0], [0, 0, 800.0]]), 11.0, 14), PAN_C, "static")
    for nm in ("spill", "pan load", "broom/broom bristles (natural)", "pan/dustpan"):
        sc.soft.add(nm)
    # the camera's view, shown when it looks (a see-through wedge from the gripper's camera)
    sc.add("camera view", pv.Pyramid([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0.5, 0.5, 1]]).extract_surface()
           .triangulate(),
           FS.ORANGE, "camview", opacity=0.30, shown=False, ambient=0.9, specular=0.0)
    sc.soft.add("camera view")

    person = people.Person(sc, "staff")
    hidden = person.names() + [n for n, g in sc.group_of.items() if g in ("broom", "pan", "panload")] + \
        ["broom handle", "pan handle"]
    for n in hidden:
        sc.alpha[n] = 0.0
    st = dict(p=P_START.copy(), hd=0.0, lean=0.0, phase=0.0, amp=0.0)

    def face(dvec):
        return math.degrees(math.atan2(dvec[1], dvec[0])) - 90.0

    def tools_carried(p, hd):
        """The broom upright in the right hand, the pan hanging from the left, as they walk."""
        a = math.radians(hd)
        fw, rt = np.array([-math.sin(a), math.cos(a)]), np.array([math.cos(a), math.sin(a)])
        hr = np.r_[p + rt * 265 + fw * 120, 830.0]
        hl = np.r_[p - rt * 265 + fw * 120, 830.0]
        head = np.r_[p + rt * 330 + fw * 330, 60.0]
        lip = np.r_[p - rt * 300 + fw * 300, 70.0]
        return hr, hl, head, lip, fw

    def pose_tools(hr, hl, head, head_yaw, lip, pan_yaw, pan_tilt=0.0):
        sc.gmat["broom"] = T(tuple(head)) @ R((0, 0, 1), head_yaw)
        sock = (sc.gmat["broom"] @ np.r_[10.0, 0.0, 92.0, 1.0])[:3]
        sc.set_mesh("broom handle", N.tube_along(np.array([sock, hr + (0, 0, 95.0)]), 12.0, 14))
        Mp = T(tuple(lip)) @ R((0, 0, 1), pan_yaw) @ R((0, 1, 0), -pan_tilt)
        sc.gmat["pan"] = Mp
        back = (Mp @ np.r_[PAN_D - 10.0, 0.0, PAN_H - 6.0, 1.0])[:3]
        sc.set_mesh("pan handle", N.tube_along(np.array([back, hl + (0, 0, 70.0)]), 11.0, 14))

    def set_person(p, hd, amp=0.0, phase=0.0, lean=0.0, hands=None, look=None):
        person.set(x=float(p[0]), y=float(p[1]), hd=hd, amp=amp, phase=phase, lean=lean,
                   hands=hands or {"l": None, "r": None}, look=look, grip={"l": 0.55, "r": 0.55})

    hd0 = face(P_TURN - P_START)
    hr, hl, head, lip, fw = tools_carried(P_START, hd0)
    set_person(P_START, hd0, hands={"l": tuple(hl), "r": tuple(hr)})
    pose_tools(hr, hl, head, hd0, lip, hd0 + 90.0)

    # ---- the person's clearance (what collide.Auditor doesn't see): every posed vertex against unit 3's and unit 1's
    # chassis and arms (their parts' world points), and the floor plan's machines and posts, in plan
    F = FC.Floor()
    obst = [(k, r) for k, r in F.rects.items()] + [(f"post {i}", (px - 150, px + 150, py - 150, py + 150))
                                                     for i, (px, py) in enumerate(F.posts)]
    robot_groups = [g for g in set(sc.group_of.values()) if g.startswith(("amrC", "urC", "amr", "ur"))
                    and not g.startswith("urCvac")]
    pclear = dict(min_mm=1e9, where=None, frames=0)

    def person_check(_sc):
        if PREVIEW:
            return
        pclear["frames"] += 1
        pts = []
        for nm, (P_, _f) in person.posed().items():
            pts.append(np.asarray(P_)[::7])
        pts = np.vstack(pts)
        xy = pts[:, :2]
        for k, (x0, x1, y0, y1) in obst:
            dx = np.maximum(np.maximum(x0 - xy[:, 0], xy[:, 0] - x1), 0)
            dy = np.maximum(np.maximum(y0 - xy[:, 1], xy[:, 1] - y1), 0)
            d = float(np.hypot(dx, dy).min())
            if d < pclear["min_mm"]:
                pclear.update(min_mm=d, where=k)
        for g in robot_groups:
            Wg = sc.world(g)
            for n in sc.members(g):
                inp = sc.actors[n].GetMapper().GetInput()
                if inp is None or not inp.GetNumberOfPoints():
                    continue
                q = np.asarray(inp.GetPoints().GetData())[::25]
                q = (Wg @ np.c_[q, np.ones(len(q))].T).T[:, :3]
                lo, hi = q.min(0), q.max(0)
                dd = np.maximum(np.maximum(lo[None, :] - pts, pts - hi[None, :]), 0)
                d = float(np.linalg.norm(dd, axis=1).min())
                if d < pclear["min_mm"]:
                    pclear.update(min_mm=d, where=n)
    sc.frame_hooks.append(person_check)

    # ---- cameras and labels
    wide = [(-700.0, -7600.0, 3900.0), (-2750.0, -2250.0, 380.0), (0, 0, 1)]
    close = [(-3400.0, -5200.0, 2300.0), (-2050.0, -2650.0, 420.0), (0, 0, 1)]
    sc.cam, sc.view_angle = list(wide), 42.0
    AA.status(sc, Unit_3="lanes along the rePowder's front", Bond="clipped to the floor stud, read",
              Vacuum="on (Al-family 118EXP)")
    sc.label = "Option C"
    t0 = rb.tcp_world()
    lane1_w, up1, over2, down2, lane2_e, lift = (T(tuple(p_)) @ t0 for p_ in FS.STROKES)
    lab0 = [("Unit 3 (powder): MiR250 + UR10e", (FS.UNIT3[0] + 250, FS.UNIT3[1] - 200, 850.0), (0.34, 0.80)),
            ("Bonding lead on a floor ground stud", (FS.STUD[0], FS.STUD[1], 30.0), (0.70, 0.86)),
            ("118EXP, Al family", (FS.VAC_AL[0], FS.VAC_AL[1], 1100.0), (0.07, 0.30))]

    def cam_view(target, a):
        """The wedge from the gripper's camera to a floor patch around `target`, at opacity a."""
        gc = sc.world(f"{rb.prefix}_gr_camera")[:3, 3]
        tx, ty = target
        base = [(tx - 420, ty - 300, 3.0), (tx + 420, ty - 300, 3.0), (tx + 420, ty + 300, 3.0), (tx - 420, ty + 300, 3.0)]
        sc.set_mesh("camera view", pv.Pyramid([*base, tuple(gc)]).extract_surface().triangulate())
        sc.alpha["camera view"] = float(np.clip(a, 0.0, 1.0))

    # 1. the lanes
    sc.step("1/6 Lanes", "Unit 3 works two lanes of the squeegee along the rePowder's front, bonded to the floor stud, "
            "on the hose of the Al-family 118EXP at the station.", 3.0, rb.line_to(lane1_w), labels=lab0, hold=0.2)
    cap = "Up 30 mm, 110 mm out, down, and back east along the second lane."
    sc.step("1/6 Lanes", cap, 0.7, rb.line_to(up1), hold=0.0)
    sc.step("1/6 Lanes", cap, 0.7, rb.line_to(over2), hold=0.0)
    sc.step("1/6 Lanes", cap, 0.6, rb.line_to(down2), hold=0.0)
    sc.step("1/6 Lanes", cap, 3.0, rb.line_to(lane2_e), hold=0.2)
    # 2. the colour check
    strip = (FS.SQ_AT[0] - 240.0, FS.SQ_AT[1] - 55.0)

    sc.step("2/6 Colour check", "Lift clear. The camera checks the strip's colour: NFPA 484 11.4.1 allows no metal dust "
            "that \"obscures the color of the surface beneath it\". Clear.", 1.2, rb.line_to(lift), labels=[], hold=0.0)
    sc.step("2/6 Colour check", "Lift clear. The camera checks the strip's colour: NFPA 484 11.4.1 allows no metal dust "
            "that \"obscures the color of the surface beneath it\". Clear.", 1.2, lambda u: cam_view(strip, u),
            labels=[("Colour check: clear", (strip[0], strip[1], 10.0), (0.42, 0.88))], hold=0.8)
    # 3. a visible spill
    AA.status(sc, Unit_3="stopped: a visible spill in reach of its next spot", Vacuum="off",
              Message="sent to the person and EHS")
    sc.step("3/6 A visible spill", "Its camera finds a visible layer in the aisle by the sieving cell (a dropped cup; "
            "ours, an illustration). That is a person's job (vacuum SOP 8): unit 3 stops its vacuum, keeps 1 m away "
            "and messages the person and EHS.", 1.4, lambda u: cam_view(SPILL, 1.0),
            labels=[("Visible layer: a person's job (SOP 8)", (SPILL[0], SPILL[1], 15.0), (0.80, 0.70))], hold=1.6)
    sc.step("3/6 A visible spill", "Its camera finds a visible layer in the aisle by the sieving cell (a dropped cup; "
            "ours, an illustration). That is a person's job (vacuum SOP 8): unit 3 stops its vacuum, keeps 1 m away "
            "and messages the person and EHS.", 0.6, lambda u: cam_view(SPILL, 1.0 - u), hold=0.2)
    # 4. the person walks in with the broom and the pan
    route = [P_START, P_TURN, P_WORK]
    seg = [float(np.linalg.norm(route[i + 1] - route[i])) for i in range(2)]
    L = sum(seg)

    def walk(u):
        for n in hidden:
            sc.alpha[n] = 1.0
        s = u * L
        if s <= seg[0]:
            p = route[0] + (route[1] - route[0]) * s / seg[0]
            d = route[1] - route[0]
        else:
            p = route[1] + (route[2] - route[1]) * (s - seg[0]) / seg[1]
            d = route[2] - route[1]
        hd_walk = face(d)
        hd_end = 90.0                                    # facing west at the spill
        k = max(0.0, (u - 0.85) / 0.15)
        hd = hd_walk + (((hd_end - hd_walk + 180) % 360) - 180) * k
        amp = min(1.0, 5.0 * min(u, 1.0 - u))
        hr, hl, head, lip, fw = tools_carried(p, hd)
        set_person(p, hd, amp=amp, phase=2 * math.pi * s / person.STRIDE, hands={"l": tuple(hl), "r": tuple(hr)},
                   look=(SPILL[0], SPILL[1], 0.0))
        pose_tools(hr, hl, head, hd, lip, hd + 90.0)
    AA.status(sc, Person="on the way, with a natural-bristle broom and a conductive dustpan")
    sc.step("4/6 The person", "The person comes with a natural-bristle push broom and a conductive lobby dustpan. SOP 8 "
            "also has them restrict access, ventilate and call EHS (not drawn).", 5.5, walk, cam_to=close, view_angle_to=40.0,
            labels=[("The person (the lab's one person on shift)", (P_WORK[0], P_WORK[1], 1850.0), (0.86, 0.22))],
            hold=0.2)

    # 5. the bulk: the pan down at the spill's east edge, three strokes of the broom towards it
    hd_w = 90.0
    hr0, hl0, head0, lip0, fw0 = tools_carried(P_WORK, hd_w)
    pan_hand = np.array([PAN_LIP[0] + 300.0, PAN_LIP[1] - 115.0, 860.0])

    def broom_at(xh, lift_mm=0.0):
        head = np.array([xh, BROOM_Y, lift_mm])
        hr = head + HANDLE
        return head, hr

    def set_down(u):
        lip = lip0 + (np.r_[PAN_LIP, 0.0] - lip0) * u
        hl = hl0 + (pan_hand - hl0) * u
        head_e, hr_e = broom_at(BROOM_FROM, 0.0)
        head = head0 + (head_e - head0) * u
        hr = hr0 + (hr_e - hr0) * u
        lean = 18.0 * u
        set_person(P_WORK, hd_w, lean=lean, hands={"l": tuple(hl), "r": tuple(hr)}, look=(SPILL[0], SPILL[1], 0.0))
        pose_tools(hr, hl, head, 0.0, lip, 0.0)
    AA.status(sc, Person="sweeping the bulk into the dustpan")
    cap5 = ("The bulk first, by hand: NFPA 484 11.5.1, \"conductive, nonsparking scoops and soft brooms as well as "
            "brushes that have natural fiber bristles\". The robot never sweeps a visible spill.")
    sc.step("5/6 The bulk", cap5, 1.4, set_down, labels=[("Natural-bristle push broom", (BROOM_FROM, BROOM_Y + 160, 60.0),
                                                           (0.18, 0.62)),
                                                          ("Conductive lobby dustpan", (PAN_LIP[0] + 120, PAN_LIP[1] - 150,
                                                                                        40.0), (0.62, 0.86))],
            hold=0.1)
    n_str = 3

    def stroke(k):
        def up(u):
            # forward along the floor (0 -> 0.62), then lifted back (0.62 -> 1)
            if u < 0.62:
                v = u / 0.62
                xh, lift_mm = BROOM_FROM + (BROOM_TO - BROOM_FROM) * v, 0.0
                frac = (k + v) / n_str
            else:
                v = (u - 0.62) / 0.38
                xh, lift_mm = BROOM_TO + (BROOM_FROM - BROOM_TO) * v, 45.0 * math.sin(math.pi * v)
                frac = (k + 1) / n_str
            head, hr = broom_at(xh, lift_mm)
            lean = 18.0 + 9.0 * (1.0 - (xh - BROOM_FROM) / (BROOM_TO - BROOM_FROM))
            set_person(P_WORK, hd_w, lean=lean, hands={"l": tuple(pan_hand), "r": tuple(hr)},
                       look=(xh + 120.0, BROOM_Y, 0.0))
            pose_tools(hr, pan_hand, head, 0.0, np.r_[PAN_LIP, 0.0], 0.0)
            # the pile: pushed east towards the lip and taken up, the pan's load grows
            c = SPILL + (np.array([PAN_LIP[0] - 40.0, PAN_LIP[1] + 40.0]) - SPILL) * min(1.0, frac * 1.15)
            sc.gmat["spill"] = T((*c, 0.0)) @ S((max(0.02, 1.0 - 0.95 * frac), max(0.02, 1.0 - 0.9 * frac),
                                                 max(0.05, 1.0 - 0.7 * frac)))
            sc.gmat["panload"] = T((PAN_D * 0.42, 0.0, 3.5)) @ S((max(0.02, frac),) * 3)
        return up
    for k in range(n_str):
        sc.step("5/6 The bulk", cap5, 1.7, stroke(k), labels=[], hold=0.0)
    sc.alpha["spill"] = 0.0

    # 6. the pan tipped back and lifted; the person steps back; the residue is unit 3's
    def lift_pan(u):
        tilt = 28.0 * u
        lip = np.r_[PAN_LIP, 0.0] + np.r_[0.0, 0.0, 90.0 * u]
        hl = pan_hand + np.r_[60.0 * u, 0.0, 40.0 * u]
        head, hr = broom_at(BROOM_FROM + 60.0 * u, 30.0 * u)
        set_person(P_WORK + np.array([140.0 * u, 0.0]), hd_w, lean=18.0 * (1 - u), hands={"l": tuple(hl), "r": tuple(hr)},
                   look=(PAN_LIP[0], PAN_LIP[1], 0.0))
        pose_tools(hr, hl, head, 0.0, lip, 0.0, pan_tilt=tilt)
    AA.status(sc, Person="bagging the powder: conductive bag, sealed, to the grounded pail",
              Unit_3="next: the residue at that spot")
    sc.step("6/6 The residue", "The pan tipped back and lifted: into a conductive bag, sealed, to the grounded pail "
            "(SOP 4.4), and logged. The residue is unit 3's: it parks there, bonds, squeegees and checks the colour "
            "(11.5.2: vacuums \"only for residual amounts\").", 1.6, lift_pan, cam_to=wide, view_angle_to=42.0,
            labels=[], hold=3.0)
    sc.save()
    if combined:
        sc.auditor.save()
    rep = dict(what="the person's clearance in plan to the floor plan's machines and posts, and in 3-D (axis-aligned "
                    "boxes of each part) to the robots' parts, every rendered frame; the tools they hold and the "
                    "person's own body against each other are not checked",
               min_clearance_mm=round(pclear["min_mm"], 1), nearest=pclear["where"], frames=pclear["frames"])
    if not PREVIEW:
        (OUT / "collisions").mkdir(parents=True, exist_ok=True)
        (OUT / "collisions" / f"{NAME}_person.json").write_text(json.dumps(rep, indent=1) + "\n")
    print("person clearance:", rep, flush=True)


if __name__ == "__main__":
    main()
