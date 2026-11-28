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
from scene import AUDIT, PREVIEW, R, T  # noqa: E402

import animate as A                   # noqa: E402
import lab                            # noqa: E402
import props as P                     # noqa: E402
import robot as RB                    # noqa: E402
import ur_arm                         # noqa: E402
import waste_station as WS            # noqa: E402
import powder_point as PP             # noqa: E402
import atom_nilfisk as N              # noqa: E402
from people import Person             # noqa: E402  (MakeHuman's CC0 body, skinned: floor_clean_people, upkeep_clip)

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


def sealed_liner() -> list:
    """Ours: the 118EXP's conductive liner as it comes out sealed (vacuum SOP 4.4: gathered, twisted into a gooseneck,
    folded and taped), with a little powder in it: 250 mm across, 325 mm tall, so it stands in a 5 gal pail under its
    lid. Its own frame: the bottom's centre at the origin."""
    body = N.lathe([(0, 0), (112, 0), (122, 30), (126, 180), (118, 225), (62, 262), (22, 288), (0, 290)])
    neck = N.lathe([(0, 286), (17, 286), (15, 325), (0, 325)])
    tape = N.lathe([(17.5, 296), (19.5, 296), (19.5, 309), (17.5, 309)])
    return [("liner", body.merge(neck), N.BLACK, 1.0), ("tape", tape, (0.76, 0.77, 0.80), 1.0)]


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
    if parent:
        sc.parent[group] = parent
    sc.gmat[group] = M
    return names


# ================================================================================================= the person's check
class PersonCheck:
    """What collide.Auditor doesn't see (as floor_clean_people.py checks its person): every audited frame, the
    person's posed body against boxes round the fire point's units, the pails, the vacuums (bin and trolley, the head
    where it is), the station post with its forks and the hanging Cu wand, the bucket, the sand can, the sign,
    the ground bars, the 680R and the glovebox. The hands and forearms (the body within 250 mm of a palm) are left out:
    they touch what they handle; so is the vacuum's push handle, which the person leans over to reach the bin.
    -> out/collisions/waste_clip_person.json"""

    def __init__(self, sc, worker):
        self.sc, self.worker = sc, worker
        self.min_mm, self.where, self.frames, self.inside = 1e9, None, 0, []
        vx, vy = PP.VAC["Al"]
        nb = PP.neighbours()
        ir = PP.item_rects()
        b = {"B570 post": (*nb["B570 post"], 0, 2150), "B570": (-5248.0, -5052.0, -1627.0, -1431.0, 0, 1044),
             "Super D pail": (*nb["Super D pail"], 0, 480), "680R": (*nb["680R"], 0, 1322),
             "glovebox": (-7702.0, -6898.0, -1162.0, 1143.0, 0, 2200),
             "Al vac bin": (vx - 223.0, vx + 223.0, vy - 240.0, vy + 220.0, 0, N.Z_BIN[1]),
             "Cu vac": (*ir["Cu vac"], 0, 1150), "post": (-5542.0, -5478.0, -952.0, -888.0, 0, 1090),
             "forks": (-5720.0, -5300.0, -965.0, -875.0, 955.0, 1005.0),
             "Cu wand": (-5390.0, -5330.0, -950.0, -890.0, 380.0, 1200.0),
             "bucket": (*ir["bucket"], 0, 400), "sand can": (*ir["sand"], 0, 300), "sign": (*ir["sign"], 0, 930),
             "station base": (-5630.0, -5310.0, -1220.0, -620.0, 0, 14)}
        for fam in ("Al", "Cu"):
            x, y = PP.PAIL[fam]
            b[f"{fam} pail"] = ("cyl", x, y, 153.0, 0, N.PAIL_H + 16.0)
        for nm_, (x, y) in (("ground bar", PP.BAR), ("ground bar north", PP.BAR_N)):
            b[nm_] = (x - 60.0, x + 60.0, y - 15.0, y + 15.0, 0, 40.0)
        self.boxes = b

    def head_box(self):
        vx, vy = PP.VAC["Al"]
        o = self.sc.gmat.get("wc_head", np.eye(4))[:3, 3]
        return ("cyl", vx + o[0], vy + o[1], 203.0, N.Z_BIN[1] + o[2], N.Z_HEPA[1] + o[2])

    def __call__(self, sc):
        if PREVIEW or sc.alpha.get(self.worker.names()[0], 0.0) <= 0.0:
            return
        self.frames += 1
        pts = np.vstack([np.asarray(P_)[::5] for part, (P_, _f) in self.worker.posed().items() if part != "glove"])
        hands = [self.worker.hand_point(s_) for s_ in ("l", "r")]
        keep = np.ones(len(pts), bool)
        for h in hands:
            keep &= np.linalg.norm(pts - h, axis=1) > 250.0
        pts = pts[keep]
        boxes = dict(self.boxes)
        heads = sc.members("wc_head")
        if heads and sc.alpha.get(heads[0], 1.0) > 0.0:     # set aside (hidden) while the liner is changed
            boxes["Al vac head"] = self.head_box()
        for k, bx in boxes.items():
            if bx[0] == "cyl":                       # a round part: (cx, cy, r, z0, z1)
                _, cx, cy, r, z0, z1 = bx
                rad = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) - r
                dz = np.maximum(z0 - pts[:, 2], pts[:, 2] - z1)
                d = np.maximum(rad, dz)
                out = np.hypot(np.maximum(rad, 0), np.maximum(dz, 0))
            else:
                x0, x1, y0, y1, z0, z1 = bx
                d = np.maximum.reduce([x0 - pts[:, 0], pts[:, 0] - x1, y0 - pts[:, 1], pts[:, 1] - y1,
                                       z0 - pts[:, 2], pts[:, 2] - z1])
                out = np.linalg.norm(np.c_[np.maximum(x0 - pts[:, 0], 0) + np.maximum(pts[:, 0] - x1, 0),
                                           np.maximum(y0 - pts[:, 1], 0) + np.maximum(pts[:, 1] - y1, 0),
                                           np.maximum(z0 - pts[:, 2], 0) + np.maximum(pts[:, 2] - z1, 0)], axis=1)
            dist = np.where(d > 0, out, d)            # negative: inside, by how much
            m = float(dist.min())
            if m < self.min_mm:
                self.min_mm, self.where = m, k
            if m < 0:
                self.inside.append((sc.n, k, round(m, 1)))

    def save(self):
        import json
        rep = dict(what=" ".join((PersonCheck.__doc__ or "").split()), frames=self.frames,
                   min_clearance_mm=round(self.min_mm, 1), nearest=self.where,
                   frames_inside=len({f for f, _, _ in self.inside}), inside=self.inside[:40])
        path = Path(__file__).resolve().parent / "out" / "collisions" / f"{NAME}_person.json"
        path.write_text(json.dumps(rep, indent=1) + "\n")
        print(f"{NAME}: person clearance {rep['min_clearance_mm']} mm (nearest {rep['nearest']}), "
              f"{rep['frames_inside']} of {rep['frames']} frames with the body inside a box", flush=True)


# ================================================================================================= the liner change
def liner_change(sc, worker, say, step, cam_from):
    """Part 3's person: in from the aisle round the glovebox and along the corridor behind the machines (clear of
    the 680R, the B570 and the Super D pail), the Al-family 118EXP unplugged and its head lifted off (then set aside,
    not drawn), the liner sealed in place (a gooseneck twist, taped), lifted out by its neck over the vacuum's handle,
    the Al-family pail's lid off, the liner in, the lid set back on (not crimped), a fresh liner and the head back on,
    plugged in, and out the way they came. PersonCheck checks the person's clearance every audited frame."""
    vx, vy = PP.VAC["Al"]
    px, py = PP.PAIL["Al"]
    P_W = np.array([-5620.0, 260.0])                  # where the person stands, at the vacuum's handle side
    route_in = [np.array(p_, float) for p_ in ((-8600.0, -2650.0), (-8600.0, 1650.0), (-5620.0, 1650.0), tuple(P_W))]
    z_bag = N.Z_BIN[0] + 20.0
    st = {"head": np.zeros(3), "bag": np.array([vx, vy, z_bag]), "lid": np.zeros(3)}
    HD_S, HD_W = 180.0, 90.0                          # facing south (the vacuum), west (the pail)
    head_names = sc.members("wc_head")

    def place_head(off):
        st["head"] = np.asarray(off, float)
        sc.gmat["wc_head"] = T(tuple(st["head"]))

    def place_bag(p_):
        st["bag"] = np.asarray(p_, float)
        sc.gmat["wc_bag"] = T(tuple(st["bag"]))

    def place_lid(off):
        st["lid"] = np.asarray(off, float)
        sc.gmat["wc_lid"] = T(tuple(st["lid"]))

    def pose(p_, hd, hands=None, lean=0.0, amp=0.0, phase=0.0, look=None):
        worker.set(x=float(p_[0]), y=float(p_[1]), hd=hd, amp=amp, phase=phase, lean=lean,
                   hands=hands or {"l": None, "r": None}, look=look, grip={"l": 0.55, "r": 0.55})

    def left_of(hd):
        a = math.radians(hd)
        return np.array([-math.cos(a), -math.sin(a), 0.0])

    def head_hands():
        """Both hands on the motor head's top rim, on the side towards the person (who faces south)."""
        top = np.array([vx, vy + 110.0, N.Z_MOTOR[1] - 10.0]) + st["head"]
        lv = left_of(HD_S)
        return {"l": tuple(top + lv * 140.0), "r": tuple(top - lv * 140.0)}

    def walk(path, hd_end=None):
        seg = [float(np.linalg.norm(path[i + 1] - path[i])) for i in range(len(path) - 1)]
        L = sum(seg)

        def up(u):
            d_ = u * L
            for i, sl in enumerate(seg):
                if d_ <= sl or i == len(seg) - 1:
                    f = min(1.0, d_ / max(sl, 1e-9))
                    p_ = path[i] + (path[i + 1] - path[i]) * f
                    dv = path[i + 1] - path[i]
                    break
                d_ -= sl
            hd = math.degrees(math.atan2(dv[1], dv[0])) - 90.0
            if hd_end is not None and u > 0.9:
                hd = hd + (((hd_end - hd + 180) % 360) - 180) * (u - 0.9) / 0.1
            pose(p_, hd, amp=min(1.0, 6.0 * min(u, 1.0 - u)), phase=2 * math.pi * u * L / Person.STRIDE)
        return up, L

    def path_pt(pts, u):
        seg = [float(np.linalg.norm(pts[i + 1] - pts[i])) for i in range(len(pts) - 1)]
        d_ = u * sum(seg)
        for i, sl in enumerate(seg):
            if d_ <= sl or i == len(seg) - 1:
                return pts[i] + (pts[i + 1] - pts[i]) * min(1.0, d_ / max(sl, 1e-9))
            d_ -= sl
        return pts[-1]

    for n in worker.names():
        sc.alpha[n] = 1.0
    pose(route_in[0], 0.0)
    f, L = walk(route_in, hd_end=HD_S)
    cam_pp = [(-4550.0, 2050.0, 2700.0), (-5750.0, -100.0, 650.0), (0, 0, 1)]
    say("3/4 The vacuum liners", "A person changes the liners; the arms don't. In from the aisle round the glovebox and "
        "along the corridor behind the machines, clear of the fire point, to the Al-family 118EXP.")
    step(6.0, f, hold=0.2, cam=cam_pp, va=40.0)
    # unplugged, the clamps opened, the head lifted off and set aside (not drawn)
    say("3/4 The vacuum liners", "Vacuum off and unplugged, after its run-on and 60 s settle (vacuum SOP 4). The two "
        "clamps open and the head comes off (set aside: not drawn).")
    for n in sc.members("wc_cord") + sc.members("wc_clamps"):
        sc.alpha[n] = 0.0
    step(0.8, lambda u: pose(P_W, HD_S, hands=head_hands(), lean=22.0 * u), hold=0.1)

    def head_off(u):
        place_head((0, 0, 200.0 * min(1.0, u / 0.6)))
        pose(P_W, HD_S, hands=head_hands(), lean=22.0 - 10.0 * min(1.0, u / 0.6))
        for n in head_names:
            sc.alpha[n] = 1.0 - max(0.0, (u - 0.6) / 0.4)
    step(1.6, head_off, hold=0.1)
    # the liner sealed in place: its mouth drawn up, twisted into a gooseneck, folded over and taped
    neck_at = np.array([vx, vy + 80.0, 700.0])
    say("3/4 The vacuum liners", "The liner is sealed where it is: its mouth drawn up, twisted into a gooseneck, folded "
        "over and taped (vacuum SOP 4.4). Dry: no water, no oil, nothing poured.")
    lv = left_of(HD_S)
    step(0.9, lambda u: pose(P_W, HD_S, hands={"l": tuple(neck_at + lv * 60.0), "r": tuple(neck_at - lv * 60.0)},
                             lean=12.0 + 23.0 * u), hold=0.05)
    raised = np.array([vx, vy + 30.0, neck_at[2] - 325.0])

    def seal(u):
        tw = math.radians(320.0 * u)
        lh = neck_at + lv * 60.0 * math.cos(tw) + np.array([0, 25.0 * math.sin(tw), 0])
        rh = neck_at - lv * 60.0 * math.cos(tw) - np.array([0, 25.0 * math.sin(tw), 0])
        pose(P_W, HD_S, hands={"l": tuple(lh), "r": tuple(rh)}, lean=35.0)
        if u > 0.45:
            for n in sc.members("wc_bag_open") + sc.members("wc_lip"):
                sc.alpha[n] = 0.0
            for n in sc.members("wc_bag"):
                sc.alpha[n] = 1.0
            place_bag(np.array([vx, vy, z_bag]) + (raised - np.array([vx, vy, z_bag])) * min(1.0, (u - 0.45) / 0.4))
    step(2.0, seal, hold=0.5, labels=[("Gooseneck: twisted, folded over, taped", tuple(neck_at), (0.72, 0.28))])

    def neck():
        return st["bag"] + (0, 0, 315.0)
    # out by its neck, high enough to pass over the vacuum's handle (its top at 1143 mm), round to the pail
    say("3/4 The vacuum liners", "The sealed liner comes out by its neck, over the vacuum's handle, to the Al-family pail "
        "beside it on the corridor side.")
    B = [raised, np.array([vx, vy + 30.0, 1165.0]), np.array([vx, -75.0, 1165.0]), np.array([-5990.0, -75.0, 1165.0]),
         np.array([-6010.0, py - 40.0, 1000.0])]
    step(1.2, lambda u: (place_bag(path_pt(B[:2], u)),
                         pose(P_W, HD_S, hands={"r": tuple(neck()), "l": None}, lean=35.0 - 30.0 * u)), hold=0.05)

    def over_and_west(u):
        place_bag(path_pt(B[1:], u))
        hd = HD_S - 90.0 * max(0.0, (u - 0.35) / 0.65)
        pose(P_W, hd, hands={"r": tuple(neck()), "l": None}, lean=5.0)
    step(2.0, over_and_west, hold=0.05)
    pail_top = np.array([px, py, N.PAIL_H + 10.0])
    lid_grip = np.array([px + 100.0, py - 70.0, N.PAIL_H + 12.0])     # the lid's rim towards the person's left hand
    bag4 = st["bag"].copy()
    over_pail = np.array([px, py, N.PAIL_H + 60.0])

    def lid_off(u):
        place_lid((40.0 * u, -340.0 * u, 180.0 * u))      # clear of the liner's way in (59 mm at the pail)
        place_bag(bag4 + (over_pail - bag4) * max(0.0, (u - 0.5) / 0.5))
        pose(P_W, HD_W, hands={"r": tuple(neck()), "l": tuple(lid_grip + st["lid"])}, lean=10.0 + 18.0 * min(1.0, u * 2))
    step(1.4, lid_off, hold=0.05, labels=[("Al-family pail: the lid off only while the liner goes in",
                                           tuple(pail_top), (0.06, 0.32))])
    bag5 = st["bag"].copy()
    inside = np.array([px, py, 10.0])

    def bag_in(u):
        place_bag(bag5 + (inside - bag5) * u)
        pose(P_W, HD_W, hands={"r": tuple(neck()), "l": tuple(lid_grip + st["lid"])}, lean=28.0 + 8.0 * u)
    step(1.2, bag_in, hold=0.1)
    say("3/4 The vacuum liners", "The lid goes back on, set on, not crimped: a crimped lid would hold in the trace "
        "hydrogen (Waste Management). The pail stays bonded to the ground bar.")
    lid1 = st["lid"].copy()
    right_grip = np.array([px + 100.0, py + 70.0, N.PAIL_H + 12.0])

    def lid_on(u):
        place_lid(lid1 * (1.0 - u))
        pose(P_W, HD_W, hands={"l": tuple(lid_grip + st["lid"]),
                               "r": tuple(right_grip + st["lid"]) if u > 0.25 else tuple(neck())},
             lean=36.0 - 16.0 * u)
    step(1.4, lid_on, hold=0.6, labels=[("Lid set on, not crimped", tuple(pail_top + (0, 0, 30.0)), (0.06, 0.32))])
    # a fresh liner, the head back on, plugged in
    say("3/4 The vacuum liners", "A fresh liner, seated on bare metal, the head back on and clamped, plugged in. Powder "
        "waste never rides a MiR: the full pail waits here for BYU Risk Management's pickup.")
    for n in sc.members("wc_bag_open") + sc.members("wc_lip"):
        sc.alpha[n] = 1.0
    step(1.0, lambda u: pose(P_W, HD_W + 90.0 * u, hands=head_hands() if u > 0.6 else None, lean=20.0 - 12.0 * u),
         hold=0.05)

    def head_on(u):
        for n in head_names:
            sc.alpha[n] = min(1.0, u / 0.4)
        place_head((0, 0, 200.0 * (1.0 - max(0.0, (u - 0.4) / 0.6))))
        pose(P_W, HD_S, hands=head_hands(), lean=8.0 + 8.0 * max(0.0, (u - 0.4) / 0.6))
    step(1.6, head_on, hold=0.1)
    place_head(np.zeros(3))
    for n in sc.members("wc_cord") + sc.members("wc_clamps"):
        sc.alpha[n] = 1.0
    f, L = walk([P_W, np.array([-5620.0, 1650.0]), np.array([-7400.0, 1650.0])])
    say("3/4 The vacuum liners", "And out the way they came. The liners, the bottles and the labels are booked in "
        "upkeep as the waste work: an hour a week at one alloy a day.")
    step(3.6, f, hold=0.2)
    for n in worker.names():
        sc.alpha[n] = 0.0


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
    # ---- the powder point drawn again part by part for part 3's person (the lab merges it by colour, which can't
    # move): the Al vacuum's head, its liner's lip, its cord and the Al pail's lid as groups of their own
    for n in sc.members("powder_point"):
        sc.alpha[n] = 0.0
        sc.base_alpha[n] = 0.0
    moving = {"wc_head": ("Al vac vac housing", "Al vac vac motor head", "Al vac vac hepa", "Al vac vac switch",
                          "Al vac label"),
              "wc_lip": ("Al vac vac liner lip",), "wc_cord": ("Al cord",), "wc_lid": ("Al pail pail lid",),
              "wc_clamps": ("Al vac vac clamps",), "wc_bail": ("Al pail pail bail",)}
    for nm, (mesh, col, op) in PP.parts(skip=tuple(q for qs in moving.values() for q in qs)).items():
        sc.add(f"wc_pp/{nm}", mesh, col, "wc_pp", opacity=op, specular=0.3)
    plist = PP.parts_list()
    for g, prefixes in moving.items():
        add_parts(sc, [(nm, m, c, op) for nm, m, c, op in plist if nm.startswith(prefixes)], g, None, np.eye(4))
    # the Al pail's bail laid down along its rim on the corridor side, out of the opening the liner goes through
    bx_, by_ = PP.PAIL["Al"]
    zb_ = N.PAIL_H - 40.0
    sc.gmat["wc_bail"] = T((bx_, by_, zb_)) @ R((1, 0, 0), -90.0) @ T((-bx_, -by_, -zb_))
    vx, vy = PP.VAC["Al"]
    z_bag = N.Z_BIN[0] + 20.0                         # the liner's bottom, on the bin's floor
    bag_open = N.lathe([(N.BIN_ID / 2 - 6, z_bag), (N.BIN_ID / 2 - 3, z_bag), (N.BIN_ID / 2 - 3, N.Z_BIN[1] - 6),
                        (N.BIN_ID / 2 - 6, N.Z_BIN[1] - 6)]).translate((vx, vy, 0), inplace=False)
    add_parts(sc, [("liner", bag_open, N.BLACK, 1.0)], "wc_bag_open", None, np.eye(4))
    add_parts(sc, sealed_liner(), "wc_bag", None, T((vx, vy, z_bag)))
    worker = Person(sc, "worker")
    for n in worker.names() + sc.members("wc_bag"):
        sc.alpha[n] = 0.0
    pcheck = PersonCheck(sc, worker) if AUDIT else None
    if pcheck is not None:
        sc.frame_hooks.append(pcheck)
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
    say("3/4 The powder point", "Loose powder and sweepings go in the Solid Material bucket, used filters straight into "
        "dry sand. When a pail is full, the pickup is requested from BYU Risk Management.")
    step(4.0, None, hold=3.0, labels=lab_pp2, cam=pp_cam2)
    liner_change(sc, worker, say, step, pp_cam2)

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
    if pcheck is not None:
        pcheck.save()
    sc.save()


if __name__ == "__main__":
    movie()
