"""Interference checks for the mock-up v2 parts (#266), by OCC booleans on the exported solids.

    python checks.py      # -> exports/checks.json

Everything is put together in the carrier frame (see parts.py): Cubware's PandaDeck, the two 0 plates
on their keys, the dowels, both dock blocks, the carrier halves and post, eight vials, and AgileX's
gripper with the finger inserts on its carriages. The gripper is posed as analysis.py's IK has it: tool
axis 45 degrees down along the carrier, pointing away from J1 (towards pocket 9), fingers closing across
the carrier.

Each pair reports the volume they share. Fits that touch by design (the vials in their tight pockets,
the silicone pads on the post or vial, the inserts on their carriages) are listed as such, with the
number, so a design change that turns a touch into a clash still shows.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import cadquery as cq
import numpy as np
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Ax3, gp_Dir, gp_Pnt, gp_Trsf

import parts as PT
import sources as S

HERE = Path(__file__).resolve().parent
P = PT.P
SQ2 = math.sqrt(2.0)
TOL = 0.05  # mm^3; booleans on tessellation-free B-reps leave numerical slivers far below this


def overlap(a, b):
    try:
        bba, bbb = a.BoundingBox(), b.BoundingBox()
        if (bba.xmax < bbb.xmin or bbb.xmax < bba.xmin or bba.ymax < bbb.ymin or bbb.ymax < bba.ymin
                or bba.zmax < bbb.zmin or bbb.zmax < bba.zmin):
            return 0.0
        return round(float(a.intersect(b).Volume()), 3)
    except Exception as e:  # noqa: BLE001
        return f"boolean failed: {e}"


def gap(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    return round(float(d.Value()), 3) if d.IsDone() else None


def xform(shape, R, t):
    """Rigid move: the shape's x, y, z axes go to R's columns, its origin to t."""
    R = np.asarray(R, float)
    to = gp_Ax3(gp_Pnt(*map(float, t)), gp_Dir(*R[:, 2]), gp_Dir(*R[:, 0]))
    tr = gp_Trsf()
    tr.SetDisplacement(gp_Ax3(), to)
    return shape.moved(cq.Location(tr))


# ------------------------------------------------------------------ the scene
def deck_strip():
    """PandaDeck under the dock: deck x along the carrier, the carrier's axis on slot row y = -225."""
    d = S.deck()
    cy = -225.0
    cx = 252.5
    assert cy in d["slot_y"] and cx in d["slot_x"], "carrier centre must sit on a slot"
    strip = d["solid"].intersect(PT.box(cx - 170, cx + 170, cy - 40, cy + 40, -1, 11))
    # deck (x, y, z) -> carrier (X, Y, Z) = (-(y - cy), x - cx, z - 22)
    R = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    t = [cy, -cx, -(P.plate_t + P.floor_t + d["thickness"])]
    return xform(strip, R, t)


def at_end(shape, end):
    """Place a part built in a dock block's frame at end A (+y) or end B (-y) of the carrier."""
    s = shape if end == "A" else shape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)
    return s.translate(cq.Vector(0, P.pin_y if end == "A" else -P.pin_y, 0))


def vial(i):
    h = S.holder()
    y = PT.slot_y(i)
    z0 = h["seat_z"]
    body = PT.cyl(P.vial_r, z0, z0 + 45.5, 0, y)
    capped = PT.fuse(body, PT.cyl(P.cap_r, z0 + 45.5, z0 + 64.2, 0, y))
    return capped


def scene(parts, plate=("plate_0", "plate_0")):
    ft = P.floor_t
    out = {"deck": deck_strip()}
    for end, pname in zip("AB", plate):
        pl = parts[pname].translate(cq.Vector(0, 0, -ft))
        out[f"plate {end} ({pname})"] = at_end(pl, end)
        holes, _ = PT.plate_dowels(*PLATE_KEY[pname])
        for k, (x, y) in enumerate(holes):
            out[f"dowel {end}{k + 1}"] = at_end(PT.cyl(P.dowel_d / 2, -P.dowel_depth_plate - ft + 0.2,
                                                      -ft + P.dowel_depth_block - 0.2, x, y), end)
        _, pin = PT.plate_dowels(*PLATE_KEY[pname])
        blk = parts["dock_block"].translate(cq.Vector(0, 0, -ft))
        dx, dy = pin
        theta = PLATE_KEY[pname][1] if PLATE_KEY[pname][0] == "r" else 0.0
        blk = blk.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), theta).translate(cq.Vector(dx, dy, 0))
        out[f"dock block {end}"] = at_end(blk, end)
    out["carrier half A"] = parts["carrier_half_a"]
    out["carrier half B"] = parts["carrier_half_b"]
    out["handle post"] = parts["handle_post"]
    for i in range(1, 10):
        if i != P.post_slot:
            out[f"vial {i}"] = vial(i)
    return out


PLATE_KEY = {PT.plate_name(k, v): (k, v) for k, v in PT.PLATES}


# ------------------------------------------------------------------ the gripper
def pads(z_apex, v_dir):
    """Silicone strips in an insert's recesses, in the insert's frame."""
    xt, ytcp = PT.tcp()[0], PT.tcp()[1]
    s0, s1 = P.pad_s
    strip = PT.box(s0 + 0.15, s1 - 0.15, -P.pad_v + 0.25, P.pad_v - 0.25, P.pad_recess - P.pad_t, P.pad_recess)
    strip = strip.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 45).translate(cq.Vector(0, 0, z_apex))
    both = strip.fuse(strip.mirror("YZ"))
    return both.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -45 * v_dir).translate(cq.Vector(xt, ytcp, 0))


def gripper_parts(parts, travel):
    """AgileX's gripper with the inserts, carriages moved `travel` mm each from where AgileX modelled them,
    in the STEP frame. The stock jaws and pads come off; the bearings move over to the inserts."""
    g = S.gripper()
    sol = g["solids"]
    xt, zt = g["tool_axis_xz"]
    z_apex, _ = PT.grip_states()
    up, dn = cq.Vector(0, 0, travel), cq.Vector(0, 0, -travel)

    def flip(s):  # 180 degrees about the tool axis
        return s.rotate(cq.Vector(xt, 0, zt), cq.Vector(xt, 1, zt), 180)

    out = {"motor housing": sol[0], "linear rail": sol[1], "finger plate": sol[2], "back cover": sol[3],
           # AgileX's flange solid reads as touching everything in OCC (#245): use a plain 57 mm disc
           "flange (proxy)": cq.Solid.makeCylinder(28.5, 10.5, cq.Vector(xt, 54.48, zt), cq.Vector(0, 1, 0)),
           "upper carriage": sol[5].translate(up), "upper bearing": sol[8].translate(up),
           "upper insert": parts["finger_insert_upper"].translate(up),
           "upper pads": pads(z_apex, +1).translate(up),
           "lower carriage": sol[9].translate(dn), "lower bearing": sol[12].translate(dn),
           "lower insert": flip(parts["finger_insert_lower"]).translate(dn),
           "lower pads": flip(pads(z_apex, -1)).translate(dn)}
    return out


def grasp_pose(point, back=0.0):
    """STEP frame -> carrier frame with the TCP on `point`, backed off `back` mm along the tool axis."""
    tcp = np.array(PT.tcp())
    R = np.array([[0, 0, -1], [-1 / SQ2, 1 / SQ2, 0], [1 / SQ2, 1 / SQ2, 0]])  # columns: x, y, z of the STEP
    a = np.array([0, -1, -1]) / SQ2                                            # approach, = -y of the STEP
    t = np.asarray(point, float) - R @ tcp - a * back
    return R.tolist(), t.tolist()


def posed(gp, R, t):
    return {k: xform(v, R, t) for k, v in gp.items()}


# ------------------------------------------------------------------ checks
DESIGNED = {  # pairs that touch by design, and why
    ("vial", "carrier half"): "tight-fit pocket: the fingers squeeze the vial (Cubware's design, 0.57 mm on radius)",
    ("upper insert", "upper carriage"): "insert's mating face on the carriage",
    ("lower insert", "lower carriage"): "insert's mating face on the carriage",
    ("upper insert", "upper bearing"): "bearing on its seat",
    ("lower insert", "lower bearing"): "bearing on its seat",
    ("upper pads", "upper insert"): "pad in its recess",
    ("lower pads", "lower insert"): "pad in its recess",
    ("pads", "handle post"): "silicone on the post",
    ("pads", "vial"): "silicone on the vial",
}


def designed(a, b):
    for (p, q), why in DESIGNED.items():
        if (p in a and q in b) or (p in b and q in a):
            return why
    return None


def pairs(group_a, group_b=None, skip_same=True):
    out = []
    items_a = list(group_a.items())
    items_b = list(group_b.items()) if group_b is not None else None
    for i, (na, sa) in enumerate(items_a):
        others = items_b if items_b is not None else items_a[i + 1:]
        for nb, sb in others:
            v = overlap(sa, sb)
            if isinstance(v, str) or v > TOL:
                out.append(dict(a=na, b=nb, overlap_mm3=v, designed=designed(na, nb)))
    return out


def summarise(found):
    clashes = [f for f in found if not f["designed"]]
    return dict(clashes=clashes, designed_contacts=[f for f in found if f["designed"]], ok=not clashes)


def main():
    t0 = time.time()
    parts, _ = PT.build()
    print(f"built in {time.time() - t0:.0f} s")
    sc = scene(parts)
    _, states = PT.grip_states()
    res = {"frame": "carrier frame of parts.py; gripper posed at 45 degrees along the carrier"}

    # 1. the parts at rest: deck, plates, dowels, dock, carrier, vials
    res["assembly"] = summarise(pairs(sc))
    print("assembly", res["assembly"]["ok"], time.time() - t0)

    # 2. every offset plate under both dock blocks, with the carrier still where it was (it has not been
    #    re-placed, so only the plate, dowels and block are checked against each other and the deck)
    res["offset_plates"] = {}
    for pname in PLATE_KEY:
        s2 = scene(parts, (pname, pname))
        sub = {k: v for k, v in s2.items() if k.startswith(("plate", "dowel", "dock", "deck"))}
        res["offset_plates"][pname] = summarise(pairs(sub))
    print("plates", all(v["ok"] for v in res["offset_plates"].values()), time.time() - t0)

    # 3. the gripper alone at each opening: inserts against the gripper and each other
    res["gripper"] = {}
    for st in ("open", "vial", "post"):
        gp = gripper_parts(parts, states[st]["carriage_travel"])
        res["gripper"][st] = summarise(pairs(gp))
    print("gripper", time.time() - t0)

    # 4. grasps: the gripper posed on the post and on vials, closed, and open on the way in
    res["grasps"] = {}
    zg = P.groove_z
    cases = [("post, closed", (0, 0, zg), "post", 0.0), ("post, open at the grasp", (0, 0, zg), "open", 0.0),
             ("post, open, 30 mm back", (0, 0, zg), "open", 30.0), ("post, open, 60 mm back", (0, 0, zg), "open", 60.0)]
    for i in (1, 4, 6, 9):
        cases += [(f"vial {i}, closed", (0, PT.slot_y(i), zg), "vial", 0.0),
                  (f"vial {i}, open, 30 mm back", (0, PT.slot_y(i), zg), "open", 30.0)]
    for name, pt, st, back in cases:
        R, t = grasp_pose(pt, back)
        gp = posed(gripper_parts(parts, states[st]["carriage_travel"]), R, t)
        found = pairs(gp, sc)
        res["grasps"][name] = summarise(found)
        # clearances that matter: rib to the post's groove floor and flanks, and to a vial
        if name == "post, closed":
            rib = {k: gap(gp[k], sc["handle post"]) for k in ("upper insert", "lower insert")}
            res["grasps"][name]["insert_to_post_gap_mm"] = rib
        if name.startswith("vial") and name.endswith("closed"):
            i = int(name.split()[1].rstrip(","))
            res["grasps"][name]["insert_to_vial_gap_mm"] = {k: gap(gp[k], sc[f"vial {i}"])
                                                            for k in ("upper insert", "lower insert")}
            nb = [j for j in (i - 1, i + 1) if 1 <= j <= 9 and j != P.post_slot]
            res["grasps"][name]["gripper_to_neighbour_vials_mm"] = {
                f"vial {j}": min(gap(gp[k], sc[f"vial {j}"]) for k in ("upper insert", "lower insert",
                                                                        "upper carriage", "lower carriage"))
                for j in nb}
        print(name, res["grasps"][name]["ok"], time.time() - t0)

    res["ok"] = (res["assembly"]["ok"] and all(v["ok"] for v in res["offset_plates"].values())
                 and all(v["ok"] for v in res["gripper"].values()) and all(v["ok"] for v in res["grasps"].values()))
    res["grip_states"] = states
    res["rib"] = PT.rib_numbers()
    (PT.OUT / "checks.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v.get("ok") if isinstance(v, dict) else v for k, v in res.items()
                      if k not in ("grip_states", "rib", "frame")}, indent=1))
    print(f"done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
