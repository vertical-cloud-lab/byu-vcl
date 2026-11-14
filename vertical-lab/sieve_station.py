"""The sieving cell of the alloy route's chapter 3 (#303, round 5): what lets the UR10e do the whole sieving job.

Asked for in PR #318: no person taking the stack apart. The cell is on the bench between the rePowder and the VLM, in
a downdraft enclosure (open at the front for the arm, extraction through the roof, every metal part bonded to a
ground bar: Al powder under 63 um is among the most ignitable metal dusts). Four things make it work:

* **A handling tab on every sieve and on the pan**, a 12 mm stainless tab at the front of the frame, gripped like the
  build plate's lug. The 2F-85's fingers close on it vertically, so the arm can lift one sieve off a nested stack.
* **The Al set's own stand**, beside the shaker, where the set waits nested in the reverse order: No. 60 at the
  bottom, the pan on top. Taken off one at a time from the top, they go onto the AS 200 pan first, No. 60 last; taken
  off the AS 200 after the run, top first, they go back onto the stand in storage order, ready for the next run. One
  set per alloy family, as DAL #234's Edison answer advises: the Cu-alloy set lives on its own stand.
* **A tipper over a funnel**: a C-shaped cradle on a horizontal shaft clamps the sieve by its frame, turns it over the
  funnel, and a pneumatic knocker taps the frame, not the cloth (DAL #234: tap the frame; no brush on 63 um or finer,
  no compressed air on any cloth). What falls goes down the funnel into one of five labelled jars on a turntable,
  which turns one place for each sieve. The No. 325 and the pan share the LPBF jar: together they are the < 63 um cut.
* **The lid parked on the tipper's roof**, from where the arm takes it to the stack and back.

The lab does all of this by hand now (Gage Erickson's three videos of 29 Oct 2026, unlisted on the lab's channel):
the stack shaken by hand, each sieve tipped over a white plastic funnel into a glass jar, the jars labelled on a
P-touch, the sieves brushed and wiped. No shaker found is sold for robot loading (instruments_char's note), so the
tab, the stand, the tipper and the enclosure are this model's design; sizes are assumed except the sieves' own
(DAL's 8 in, 2 in deep, 304 stainless stack, McMaster, DAL PR #175).
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

import charge
import instruments_char as IC

# ------------------------------------------------------------------------------------------------- the sieves
T_, RW, LIP, DEPTH, SKIRT_H = IC.T_SHEET, IC.RW, IC.LIP, IC.DEPTH, IC.SKIRT_H
RIM_H = SKIRT_H + DEPTH - 2 * T_                  # a sieve's frame from its skirt's foot to its rim
ORDER = [k for k, *_ in IC.STACK]                 # bottom to top on the shaker: pan, s325, s230, s140, s100, s60
TAB_OUT = 40.0                                    # how far the tab stands out from the lip
TAB_T = 12.0                                      # its thickness (z): gripped like the 12 mm lug
STEEL = (0.80, 0.81, 0.83)
TAB_C = (0.70, 0.71, 0.74)


def _shell(line_pts, t=T_, res=72):
    inner = [(max(r - t, 0.0), z + (t if i == 0 else 0.0)) for i, (r, z) in enumerate(line_pts)]
    return charge.lathe(list(line_pts) + list(reversed(inner)), res=res)


def tab_z(key: str) -> float:
    """The tab's centre height in the sieve's own frame (z = 0 at its foot: the skirt's, or the pan's bottom)."""
    return DEPTH / 2 if key == "pan" else SKIRT_H + 20.0


def grasp_local(key: str) -> np.ndarray:
    """Where the gripper's TCP holds the tab, in the sieve's frame: the tab's middle, at the front (-y)."""
    # round 11: the pan's tab, held by its sides, 5 mm further out than a sieve's (the left fingertip's end reached
    # 2-3 mm into the pan's frame at the tab's root)
    return np.array([0.0, -(RW + LIP) - TAB_OUT / 2 - (5.0 if key == "pan" else 0.0), tab_z(key)])


def sieve_parts(key: str) -> dict:
    """{name: (mesh, colour, specular, opacity)} for one sieve (or the pan), in its own frame."""
    out = {}
    if key == "pan":
        out["frame"] = (_shell(IC.PAN_LINE, T_), STEEL, 0.55, 1.0)
    else:
        out["frame"] = (_shell(IC.SIEVE_LINE, T_), STEEL, 0.55, 1.0)
        cloth = pv.Cylinder(center=(0, 0, IC.MESH_DZ), direction=(0, 0, 1), radius=IC.MESH_R, height=0.5,
                            resolution=72).triangulate()
        out["cloth"] = (cloth, (0.45, 0.47, 0.51), 0.4, 0.55)
        out["tag"] = (pv.Box(bounds=(-18, 18, -RW - LIP - 1.2, -RW - LIP + 0.2, SKIRT_H + 34, SKIRT_H + 46))
                      .triangulate(), (0.78, 0.62, 0.30), 0.4, 1.0)
    tz = tab_z(key)
    out["tab"] = (pv.Box(bounds=(-14, 14, -(RW + LIP) - TAB_OUT, -RW + 1.0, tz - TAB_T / 2, tz + TAB_T / 2))
                  .triangulate(), TAB_C, 0.5, 1.0)
    return out


def powder_disc(key: str) -> pv.PolyData:
    """The fraction a sieve keeps, a flat heap on its cloth (or the pan's floor), in the sieve's frame."""
    z0 = 2 * T_ + 0.3 if key == "pan" else IC.MESH_DZ + 0.4
    heap = charge.lathe([(0, z0), (IC.MESH_R - 6, z0), (IC.MESH_R - 14, z0 + 3.0), (40, z0 + 5.0), (0, z0 + 6.0)],
                        res=48)
    return heap


def stack_seat(i: int) -> float:
    """The foot of the i-th piece from the bottom of a stack on the shaker, above the sieve plate's top (pan = 0)."""
    return 0.0 if i == 0 else i * DEPTH - (SKIRT_H - T_)


def stand_seat(i: int) -> float:
    """The foot of the i-th piece from the bottom of the stand's storage stack (No. 60 at the bottom, the pan on top),
    above the stand's top."""
    if i < 5:
        return i * DEPTH
    return 4 * DEPTH + RIM_H                          # the pan sits on the No. 325's rim


STORAGE = list(reversed(ORDER))                   # s60 at the bottom of the stand, the pan on top

# ------------------------------------------------------------------------------------------------- the tipper
TIP = dict(W=300.0, D=280.0, zc=405.0, top=560.0, ring_r=(106.0, 124.0), funnel=(120.0, 13.0, 300.0, 120.0),
           table_r=150.0, table_dy=110.0, jar_r=35.0, jar_h=124.0)
TIP["seat"] = TIP["zc"] - 33.0                    # a sieve's foot when it sits in the cradle (cradle upright)
JARS = [("s60", "> 250 um"), ("s100", "150-250 um"), ("s140", "106-150 um"), ("s230", "63-106 um"),
        ("lpbf", "< 63 um: LPBF")]
JAR_OF = {"s60": 0, "s100": 1, "s140": 2, "s230": 3, "s325": 4, "pan": 4}


def _box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def _cyl(r, p0, p1, res=32):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    return pv.Cylinder(center=(p0 + p1) / 2, direction=d, radius=r, height=float(np.linalg.norm(d)),
                       resolution=res).triangulate()


def tipper_parts() -> dict:
    """{piece: {name: (mesh, colour, specular, opacity)}} in the tipper's frame (its base's centre on the bench, the
    shaft along x at z = zc): 'body' (base, posts, roof, funnel, actuator), 'cradle' (turns about the shaft), 'clamps'
    (the cradle's pads, child of 'cradle'), 'knocker' (its rod, child of 'cradle'), 'table' (the jar turntable)."""
    p = TIP
    hw, zc = p["W"] / 2, p["zc"]
    dark, alu = (0.24, 0.25, 0.27), (0.70, 0.72, 0.75)
    body = {"base": (_box(-hw, hw, -110, p["D"] - 110, 0, 10), dark, 0.2, 1.0)}
    posts = None
    for sx in (-1, 1):
        post = _box(sx * hw - (30 if sx > 0 else 0), sx * hw + (0 if sx > 0 else 30), -15, 15, 10, p["top"])
        posts = post if posts is None else posts.merge(post)
    body["posts"] = (posts, alu, 0.4, 1.0)
    body["roof"] = (_box(-hw, hw, -60, 60, p["top"], p["top"] + 12), alu, 0.4, 1.0)
    body["actuator"] = (_box(-hw - 70, -hw, -40, 40, zc - 40, zc + 40), (0.12, 0.40, 0.75), 0.3, 1.0)
    rt, rb_, zt, h = p["funnel"]
    funnel = charge.lathe([(rb_ - 2, zt - h - 25), (rb_, zt - h - 25), (rb_, zt - h), (rt, zt), (rt + 6, zt),
                           (rt + 6, zt + 4), (rt - 2, zt + 4), (rb_ - 2, zt - h + 2)], res=64)
    body["funnel"] = (funnel, (0.93, 0.94, 0.95), 0.3, 1.0)
    arm = _box(-hw + 30, -rt, -10, 10, zt - 10, zt) .merge(_box(rt, hw - 30, -10, 10, zt - 10, zt))
    body["funnel arms"] = (arm, alu, 0.4, 1.0)
    # the cradle: a C-ring open at the front (the tab and the fingers pass there), on the shaft
    r0, r1 = p["ring_r"]
    segs = None
    for a0 in np.linspace(-60, 240, 26, endpoint=False):
        a1 = a0 + 300 / 26
        ca = [(r0 * math.cos(math.radians(a)), r0 * math.sin(math.radians(a))) for a in (a0, a1)]
        cb = [(r1 * math.cos(math.radians(a)), r1 * math.sin(math.radians(a))) for a in (a0, a1)]
        pts = np.array([[*ca[0], 0], [*ca[1], 0], [*cb[1], 0], [*cb[0], 0]], float)
        quad = pv.PolyData(pts, faces=[4, 0, 1, 2, 3]).extrude((0, 0, 22), capping=True).triangulate()
        segs = quad if segs is None else segs.merge(quad)
    ring = segs.translate((0, 0, p["seat"] + 26.0), inplace=False)
    # round 11: two stub trunnions from the posts into the cradle's lugs; one shaft from post to post ran through the
    # middle of every sieve set in the cradle (the stricter audit: the sieve 25-50 mm into the cradle)
    shaft = _cyl(13, (-hw, 0, zc), (-r0 + 2, 0, zc), 32).merge(_cyl(13, (r0 - 2, 0, zc), (hw, 0, zc), 32))
    lugs = _box(-r1 - 6, -r0 + 2, -9, 9, zc - 22, p["seat"] + 48).merge(_box(r0 - 2, r1 + 6, -9, 9, zc - 22,
                                                                             p["seat"] + 48))
    cradle = {"ring": (ring.merge(lugs), (0.30, 0.32, 0.36), 0.4, 1.0), "shaft": (shaft, alu, 0.6, 1.0),
              "knocker body": (_cyl(14, (r1 + 4, 40, p["seat"] + 37), (r1 + 50, 40, p["seat"] + 37), 24),
                               (0.85, 0.42, 0.10), 0.3, 1.0)}
    clamps = None
    for a in (0.0, 180.0, 90.0):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        pad = _box(-8, 8, -8, 8, p["seat"] + 26, p["seat"] + 48).translate((113.0 * c, 113.0 * s, 0), inplace=False)
        clamps = pad if clamps is None else clamps.merge(pad)
    knock = _cyl(5, (RW + LIP + 2, 40, p["seat"] + 37), (r1 + 6, 40, p["seat"] + 37), 16)
    table = {"table": (_cyl(p["table_r"], (0, p["table_dy"], 10), (0, p["table_dy"], 22), 72), dark, 0.2, 1.0)}
    return {"body": body, "cradle": cradle, "clamps": {"pads": (clamps, (0.12, 0.40, 0.75), 0.3, 1.0)},
            "knocker": {"rod": (knock, (0.62, 0.63, 0.66), 0.6, 1.0)}, "table": table}


def jar_xy(j: int, table_deg: float = 0.0) -> np.ndarray:
    """Jar j's centre on the turntable (tipper frame), with the table turned table_deg about its own centre."""
    a = math.radians(-90.0 + 72.0 * j + table_deg)
    return np.array([TIP["table_dy"] * math.cos(a), TIP["table_dy"] + TIP["table_dy"] * math.sin(a)])


def jar_parts() -> dict:
    """A 250 mL wide-mouth jar in the lab-wide style (round 9, props.jar_parts: clear glass, white label), lid off while
    it is filled under the funnel: {name: (mesh, colour, specular, opacity)}. The powder is drawn separately (jar_powder),
    so it can grow; the black lid (props.JAR_LID) is on the jar when it is not under the funnel, and not drawn here."""
    import props as P
    r, h = TIP["jar_r"], TIP["jar_h"]
    pp = P.jar_parts(2 * r, h, 14.0, fill=0.0, label=(0.24, 0.58))
    return {"body": (pp["glass"][0], pp["glass"][1], 0.35, pp["glass"][2]),
            "label": (pp["label"][0], pp["label"][1], 0.1, 1.0), "print": (pp["print"][0], pp["print"][1], 0.1, 1.0)}


def jar_lid() -> tuple:
    """The jar's black lid (props.JAR_LID), base at z = h, for the jar on the MiR: (mesh, colour)."""
    import props as P
    return P.jar_meshes(2 * TIP["jar_r"], TIP["jar_h"], 14.0)["lid"], P.JAR_LID


def jar_powder() -> pv.PolyData:
    return pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=TIP["jar_r"] - 2.5, height=1.0,
                       resolution=40).triangulate()


# ------------------------------------------------------------------------------------------------- stand, enclosure
STAND = dict(r=118.0, h=120.0)                    # a pedestal: on a 20 mm plate the No. 60's tab was so low that the
                                                  # gripper's lower knuckle reached into the bench


def stand_parts() -> dict:
    base = _cyl(STAND["r"], (0, 0, 0), (0, 0, STAND["h"]), 64)
    lip = charge.lathe([(IC.RS + 1.0, STAND["h"]), (IC.RS + 6.0, STAND["h"]), (IC.RS + 6.0, STAND["h"] + 8),
                        (IC.RS + 1.0, STAND["h"] + 8)], res=64)
    return {"stand": (base.merge(lip), (0.10, 0.55, 0.30), 0.25, 1.0)}


def enclosure_parts(w: float, d: float, h: float) -> dict:
    """A downdraft enclosure over a bench w x d, h tall over its top, open at the front: frame, panels, duct, ground
    bar and straps. Frame: the bench top's centre, the front edge at y = -d/2."""
    hw, hd = w / 2, d / 2
    frame = None
    for (x, y) in ((-hw, -hd), (hw, -hd), (-hw, hd), (hw, hd)):
        post = _box(x - 15, x + 15, y - 15, y + 15, 0, h)
        frame = post if frame is None else frame.merge(post)
    frame = frame.merge(_box(-hw - 15, hw + 15, -hd - 15, -hd + 15, h - 30, h)).merge(
        _box(-hw - 15, hw + 15, hd - 15, hd + 15, h - 30, h))
    panels = _box(-hw, hw, hd - 4, hd, 0, h).merge(_box(-hw - 4, -hw, -hd + 15, hd, 0, h)).merge(
        _box(hw, hw + 4, -hd + 15, hd, 0, h)).merge(_box(-hw, hw, -hd + 15, hd, h, h + 4))
    hood = charge.lathe([(0, h + 4), (220, h + 4), (90, h + 120), (90, h + 520), (84, h + 520), (84, h + 125),
                         (0, h + 125)], res=48).translate((0, hd - 260, 0), inplace=False)
    bar = _box(-hw + 40, hw - 40, hd - 30, hd - 6, 4, 22)
    return {"frame": (frame, (0.62, 0.63, 0.66), 0.4, 1.0), "panels": (panels, (0.78, 0.86, 0.92), 0.4, 0.16),
            "duct": (hood, (0.80, 0.81, 0.83), 0.4, 1.0), "ground bar": (bar, (0.80, 0.55, 0.20), 0.5, 1.0)}


def strap(p0, p1, r=3.0) -> pv.PolyData:
    """A ground strap (green-yellow), drooping between two points."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    mid = (p0 + p1) / 2 + (0, 0, -25.0)
    s = np.linspace(0, 1, 16)[:, None]
    pts = (1 - s) ** 2 * p0 + 2 * (1 - s) * s * mid + s ** 2 * p1
    return pv.Spline(pts, 24).tube(radius=r, n_sides=8).triangulate()


# ------------------------------------------------------------------------------------------------- the wash module
# Round 9 (Sterling, PR #318: "automation for cleaning the sieve stack? ... the depowdering module with ultrasonic IPA
# rinses?"). Three stages, no person: (1) the tipper turns the empty sieve over its funnel and a vibrator shakes the
# powder out of the cloth (a scaled-down version of what a Solukon SFM-AT200 does to a plate); (2) an ultrasonic IPA
# bath: the sieve sits on a basket ring that a lift lowers into the tank; (3) it rises into a warm-air knife (a slot
# nozzle above and one below, travelling along the cloth, air at no more than 60 C: Retsch's limit is 80 C). It is on
# its own stand, under its own extracted hood. Sizes are assumed; notes/alloy_print.md.
# Round 11: round 9 stood it on a 450 mm extension of the bench, left of the tipper, which was inside the rePowder's
# utility cabinet (repowder:c34, 900 mm tall, x -3095..-2615); the stricter audit's movers check found the basket and
# the sieve going through it. It now stands on its own stand in front of that cabinet (alloy_print.WASH_Y), between it
# and the MiR's lane, and is 60 mm shallower to fit there: the tank 290 mm deep (was 350; the basket's ring, r 113, and
# the sieve's tab, 143 mm forward of the axis, still clear its walls), the hood's posts flush with the tank's front and
# 32 mm behind the mast (were 10 mm in front and 40 mm behind): 350 mm front to back, was 438
WASH = dict(hw=165.0, y0=-150.0, y1=140.0, wall=6.0, tank_h=150.0, liq_h=118.0, z_top=260.0, z_bot=24.0, hb=330.0,
            hood_h=760.0, mast_y=162.0, knife_low=210.0)
# knife_low (round 11): the knife waits at the back (y1 - 12) at this height while the basket goes down and up, between
# the tank's rim (150) and the basket's arm to the mast (346 at its lowest), and rises to z_top only for its sweep. At
# z_top the arm passed through its upper nozzle as the basket went down; parked at the front it was in the gripper's way
WASH_POST_FRONT = 12.0                            # the front posts' centres, behind the tank's front face (y0)
WASH_BACK = 32.0                                  # the back panel, behind the mast's front face (mast_y): 4 mm behind the basket's carriage
LIQ_C = (0.72, 0.86, 0.96)


def wash_parts() -> dict:
    """{piece: {name: (mesh, colour, specular, opacity)}} in the module's frame (the sieve's axis at the origin, on the
    bench top): 'body' (tank, transducer, hood, mast), 'basket' (ring, hangers, beam, carriage; origin at the sieve's
    foot seat), 'knife' (the two slot nozzles at the origin, travelling along y), 'liquid', 'air' (the jets, with the
    knife)."""
    p = WASH
    hw, y0, y1, w, th = p["hw"], p["y0"], p["y1"], p["wall"], p["tank_h"]
    steel, dark = (0.80, 0.81, 0.83), (0.24, 0.25, 0.27)
    tank = _box(-hw, hw, y0, y1, 0, 8)
    for b in (_box(-hw, -hw + w, y0, y1, 0, th), _box(hw - w, hw, y0, y1, 0, th), _box(-hw, hw, y0, y0 + w, 0, th),
              _box(-hw, hw, y1 - w, y1, 0, th)):
        tank = tank.merge(b)
    body = {"tank": (tank, steel, 0.55, 1.0),
            "transducer": (_box(-hw + 20, hw - 20, y0 + 20, y1 - 20, -2, 0.1).merge(
                _box(-hw, hw, y0, y1, -2, 0)), (0.12, 0.40, 0.75), 0.3, 1.0)}
    hh = p["hood_h"]
    posts = None
    yp, ym = y0 + WASH_POST_FRONT, p["mast_y"] + WASH_BACK
    for (x, y) in ((-hw - 12, yp), (hw + 12, yp), (-hw - 12, ym), (hw + 12, ym)):
        post = _box(x - 12, x + 12, y - 12, y + 12, 0, hh)
        posts = post if posts is None else posts.merge(post)
    body["posts"] = (posts, (0.62, 0.63, 0.66), 0.4, 1.0)
    body["panels"] = (_box(-hw - 24, hw + 24, ym, ym + 4, 0, hh).merge(_box(-hw - 28, -hw - 24, y0, ym, 0, hh)).merge(
        _box(hw + 24, hw + 28, y0, ym, 0, hh)).merge(_box(-hw - 28, hw + 28, y0, ym + 4, hh, hh + 4)),
        (0.78, 0.86, 0.92), 0.4, 0.16)
    body["duct"] = (_cyl(70, (0, ym - 80, hh + 4), (0, ym - 80, hh + 420), 40), (0.80, 0.81, 0.83), 0.4, 1.0)
    body["mast"] = (_box(-14, 14, p["mast_y"], p["mast_y"] + 24, 0, hh - 40), (0.45, 0.47, 0.52), 0.5, 1.0)
    # the basket: a ring under the sieve's skirt, two hangers either side of it, a beam over them, an arm back to the
    # carriage on the mast (origin: the sieve's foot seat)
    rs = IC.RS
    ring = charge.lathe([(70.0, -6.0), (rs + 14.0, -6.0), (rs + 14.0, 0.0), (rs + 6.0, 0.0), (rs + 6.0, 8.0),
                         (rs + 1.0, 8.0), (rs + 1.0, 0.0), (70.0, 0.0)], res=64)
    hb = p["hb"]
    hang = _box(rs + 14, rs + 22, -9, 9, -6, hb).merge(_box(-rs - 22, -rs - 14, -9, 9, -6, hb))
    beam = _box(-rs - 22, rs + 22, -9, 9, hb - 8, hb).merge(_box(-9, 9, 0, p["mast_y"] + 24, hb - 8, hb)).merge(
        _box(-24, 24, p["mast_y"] - 4, p["mast_y"] + 28, hb - 40, hb + 30))
    basket = {"ring": (ring, steel, 0.6, 1.0), "hangers": (hang.merge(beam), (0.55, 0.57, 0.62), 0.5, 1.0)}
    # the knife: a slot nozzle above the rim and one below the ring, each 200 mm long, with its jet
    bar_up = _box(-100, 100, -9, 9, 100, 118)
    bar_dn = _box(-100, 100, -9, 9, -44, -26)
    knife = {"nozzles": (bar_up.merge(bar_dn), (0.85, 0.42, 0.10), 0.4, 1.0)}
    jet = _box(-100, 100, -6, 6, 52, 100).merge(_box(-100, 100, -6, 6, -26, 30))
    air = {"jets": (jet, (0.98, 0.66, 0.32), 0.1, 1.0)}
    liquid = {"ipa": (_box(-hw + w, hw - w, y0 + w, y1 - w, 8, p["liq_h"]), LIQ_C, 0.1, 1.0)}
    return {"body": body, "basket": basket, "knife": knife, "air": air, "liquid": liquid}
