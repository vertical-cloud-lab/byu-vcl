#!/usr/bin/env python3
"""The powder point on the lab floor (#303, PR #318 round 16, from PR #371's check): where the atomizer cell's powder
waste waits, as notes/waste.md ("The waste station: where waste waits", item 1, and "How it is kept") describes it.

    python3 powder_point.py        # its parts' plan rectangles and their clearances to their neighbours (no scene)

What stands here, all in world coordinates on setup_lab's floor:

* **The two Nilfisk CFM 118EXPs** (atom_nilfisk.vacuum_meshes, PR #353; notes/atom_vacuum.md "How many vacuums",
  items 1-2): the Al-family unit the lab has and the Cu-family second unit, each with its own hose, wand and crevice
  tool, on wall power (a twin outlet box on our station's post, fed from the north cable tray's drop above).
* **Our station post** (atom_nilfisk.station_meshes: the holster, the tool rack, the continuity fixture, the meter),
  with a second holster fork (ours, the first one turned round) so each family's wand has its own place.
* **One grounded steel pail per alloy family** for the sealed liners (atom_nilfisk.pail_meshes: Uline S-7344, its lid
  set on and not crimped), each labelled in words, each bonded to the area's ground bar.
* **Risk Management's lined, labelled Solid Material bucket** for waste powder and sweepings (a 5 gal HDPE pail with
  a liner over its rim and a lid: typical size, ours).
* **A small grounded steel can with dry sand for used filters** (about 2 gal: typical size, ours; notes/waste.md: "the
  smallest grounded can the filter fits, not a pail of sand").
* **The area sign** (atom_nilfisk.sign_meshes: the vacuum SOP's wording).

The Class D units are the safety PR's fixed ones (safety.PLACES): the B570 on its post and the Super D pail just
south of the point, and the 680R just west of it. They are not drawn here.

**Where, and why not where atom_vacuum.py puts it.** atom_vacuum's own floor stands the vacuum, the post and MiR250
2 in front of the rePowder's west end (model frame VAC_AT (-1060, -250), STN_AT (-520, -200), MIR_PARK (-520, -1150);
world = model + alloy_atomize.RP = (-3775, -1700)). On setup_lab's floor that puts the vacuum and the post in the
rePowder dock's approach lane (y -2520 to -1940 from the pivot at x -5362 to the dock at x -3487) and the pail,
extinguisher and sign in the aisle (y -2460 to -3260). floor_cleaning.VAC_STATION (x -5900 to -4710, y -1980 to -340)
stood west of the machine instead, but the safety PR's fire point (the B570 at (-5150, -1400), the Super D pail at
(-5650, -1475)) has since taken its front half. So the point stands behind the fire point: between the 680R
(x <= -5919) and the rePowder's back (x >= -4475), north of the B570's post (y >= -1273), clear of every dock, lane,
pivot and target post (``python3 powder_point.py`` prints the gaps; ``setup_lab.py fit`` checks the lanes and pivots
against ``RECT``). The arm side of atom_vacuum (MiR250 2 taking the wand from the holster) is atom_vacuum's own floor;
here a person takes the wand to the hose's reach, or unit 3 does (floor_clean_still.py), and a person seals and
carries the liners (PR 80; notes/atomizer_automation.md).

Everything not cited above is ours, at typical sizes, and says so.
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

import atom_nilfisk as N
import colour_coding as CC

# --------------------------------------------------------------------------------------------------- the layout
# world (x, y) in mm. Vacuums: the bin's axis, turned VAC_YAW so the inlets face south (the station side) and the push
# handles north. The post: turned POST_YAW, so its first holster (the station's own, model frame -y) faces east.
VAC = {"Al": (-5640.0, -340.0), "Cu": (-5120.0, -340.0)}
VAC_YAW = -90.0
POST = (-5510.0, -920.0)
POST_YAW = 90.0
PAIL = {"Al": (-5100.0, -810.0), "Cu": (-4770.0, -810.0)}
BUCKET = (-4700.0, -320.0)                     # Risk Management's Solid Material bucket
SAND = (-5750.0, -1110.0)                      # the filter can, with dry sand
SIGN = (-4740.0, -1160.0)                      # the A-frame sign, its face to the south (the aisle side)
BAR = (-4880.0, -610.0)                        # the area's ground bar (ours)
# which holster holds which family's wand: the west fork (the station's first holster turned round) the Al wand, nearest
# the Al vacuum; the east fork (the station's own) the Cu wand
FORK = {"Al": "west", "Cu": "east"}

BUCKET_D, BUCKET_H = 300.0, 370.0              # a 5 gal HDPE pail (typical)
SAND_D, SAND_H = 200.0, 280.0                  # a 2 gal steel can (typical)
WHITE = (0.95, 0.95, 0.93)
HDPE = (0.93, 0.93, 0.90)
LINER = (0.78, 0.80, 0.82)
INK = (0.06, 0.06, 0.07)
STEEL = (0.55, 0.57, 0.60)
LABEL = (0.98, 0.98, 0.96)
COPPER = (0.72, 0.45, 0.25)
CORD = (0.10, 0.10, 0.11)
BOX = (0.62, 0.64, 0.66)
# PR #377's family colours (colour_coding.FAMILY; Sterling, 2026-11-22: "blue and orange as mentioned are fine for
# now"): blue for the Al family, orange for the Cu family, always with the family's name in words beside the band
FAM = {k: tuple(int(CC.FAMILY[k]["rgb"][i:i + 2], 16) / 255.0 for i in (1, 3, 5)) for k in ("Al", "Cu")}
FAM_WORDS = {"Al": "Al family", "Cu": "Cu family"}


def _M(x, y, yaw=0.0, z=0.0) -> np.ndarray:
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    M = np.eye(4)
    M[:3, :3] = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    M[:3, 3] = (x, y, z)
    return M


def _box(x0, x1, y0, y1, z0, z1) -> pv.PolyData:
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))).triangulate()


def _cyl(x, y, z0, r, h, res=40) -> pv.PolyData:
    return pv.Cylinder(center=(x, y, z0 + h / 2), direction=(0, 0, 1), radius=r, height=h, resolution=res).triangulate()


def text_plate(blocks, x, y, z, w, h, depth=1.5) -> list:
    """A white label plate w x h (x across, z up) with black text fitted inside, its face to -y at y, centred on (x, z).
    blocks: ((lines, relative size), ...) as atom_nilfisk.fit_text takes them."""
    plate = _box(x - w / 2, x + w / 2, y, y + 2.0, z - h / 2, z + h / 2)
    txt, _ = N.fit_text(blocks, w * 0.88, h * 0.78, depth=depth)
    txt.translate((x, y, z), inplace=True)
    return [("label plate", plate, LABEL, 1.0), ("label text", txt, INK, 1.0)]


def vac_point(fam: str, name: str) -> np.ndarray:
    x, y, z = N.vacuum_local(name)
    p = _M(*VAC[fam], VAC_YAW) @ np.r_[x, y, z, 1.0]
    return p[:3]


def _post_M() -> np.ndarray:
    return _M(*POST, POST_YAW)


def holster_point(fork: str) -> np.ndarray:
    """World point where a wand's collar rests on a holster fork (the station's own: east; ours, turned round: west)."""
    hp = N.station_points()["holster"]
    if fork == "west":
        hp = np.array([-hp[0], -hp[1], hp[2]])
    return (_post_M() @ np.r_[hp, 1.0])[:3]


def wand_world(fork: str) -> np.ndarray:
    """The wand's frame (origin at its hose end, the wand down -z) hanging in a fork, as atom_vacuum.Wand.hanging, its
    fin out from the post as the station's own wand hangs."""
    yaw = POST_YAW + (180.0 if fork == "west" else 0.0)
    top = holster_point(fork) + np.array([0, 0, N.COLLAR_AT + N.COLLAR_L / 2])
    return _M(top[0], top[1], yaw, top[2])


def _tube(pts, r, sides=12, iters=3):
    """A tube along the polyline pts, its corners rounded by corner cutting (Chaikin), which never leaves the
    polyline's corners' hull: a spline through the same points overshot by up to 90 mm (into the B570's post)."""
    P = np.array(pts, float)
    for _ in range(iters):
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]):
            Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1])
        P = np.array(Q)
    P[:, 2] = np.maximum(P[:, 2], r + 1.0)
    return pv.lines_from_points(P).tube(radius=r, n_sides=sides).triangulate()


def parts_list() -> list:
    """[(name, mesh, rgb, opacity)], world coordinates, one entry per drawn piece (``parts`` merges them)."""
    out = []

    def put(prefix, meshes: dict, M):
        for nm, (mesh, col) in meshes.items():
            out.append((f"{prefix} {nm}", mesh.transform(M, inplace=False), col, 1.0))

    # ---- the vacuums, each with a family label plate on its motor head's south face
    for fam, (x, y) in VAC.items():
        put(f"{fam} vac", N.vacuum_meshes(), _M(x, y, VAC_YAW))
        # the family band round the bin, the collection vessel (notes/colour_coding.md: "a band on the nozzle, hose
        # cuff and collection vessel"), 40 mm, and the family's name on a plate on the motor head
        rb = N.BIN_ID / 2 + 4.0
        out.append((f"{fam} vac band", N.lathe([(rb, 250.0), (rb + 2.5, 250.0), (rb + 2.5, 290.0), (rb, 290.0)])
                    .translate((x, y, 0), inplace=False), FAM[fam], 1.0))
        for nm, m, c, op in text_plate((((FAM_WORDS[fam],), 1.0),), x, y - 196.0, 800.0, 200.0, 62.0):
            out.append((f"{fam} vac {nm}", m, c, op))
        out.append((f"{fam} vac label band", _box(x - 100, x + 100, y - 197.0, y - 195.0, 838.0, 852.0), FAM[fam], 1.0))
    # ---- our station post, and a second holster fork (the first one turned round, ours)
    Mp = _post_M()
    stn = N.station_meshes()
    put("station", stn, Mp)
    R180 = _M(0.0, 0.0, 180.0)
    for nm in ("stn holster (ours)", "stn holster hole"):
        mesh, col = stn[nm]
        out.append((f"station west {nm}", mesh.transform(Mp @ R180, inplace=False), col, 1.0))
    # the twin outlet box on the post's top (ours) and its conduit up to the north cable tray (setup_lab.utilities:
    # over the north row at y -862, z 4300)
    px, py = POST
    out.append(("outlet box", _box(px - 70, px + 70, py - 55, py + 55, N.POST_H, N.POST_H + 180), BOX, 1.0))
    out.append(("outlet faces", _box(px - 50, px + 50, py - 57, py - 55, N.POST_H + 40, N.POST_H + 150),
                (0.92, 0.92, 0.90), 1.0))
    out.append(("conduit", _cyl(px, py, N.POST_H + 180, 13.0, 4300.0 - N.POST_H - 180, 16), BOX, 1.0))
    # ---- each family's wand in its fork, the crevice tool on, and its hose to that family's vacuum
    for fam in ("Al", "Cu"):
        fork = FORK[fam]
        Mw = wand_world(fork)
        put(f"{fam} wand", N.wand_meshes(), Mw)
        cuff_band = N.lathe([(N.CUFF_OD / 2, 20.0), (N.CUFF_OD / 2 + 1.5, 20.0), (N.CUFF_OD / 2 + 1.5, 45.0),
                             (N.CUFF_OD / 2, 45.0)])
        out.append((f"{fam} wand cuff band", cuff_band.transform(Mw, inplace=False), FAM[fam], 1.0))
        fit = _M(0, 0, 90.0, -N.WAND_L - N.SEAT_GAP + N.TOOL_COLLAR[0])
        put(f"{fam} crevice", N.crevice_meshes(), Mw @ fit)
        cuff = (Mw @ np.r_[0, 0, N.CUFF_L - 20.0, 1.0])[:3]
        inlet = vac_point(fam, "inlet")
        # down from the vacuum's inlet to the floor, along it clear of the post's base and the pails, up beside the wand
        # and over into its cuff (drawn, not relaxed)
        if fork == "west":
            pts = [inlet, (inlet[0], inlet[1] - 26, 330.0), (inlet[0] - 12, inlet[1] - 40, 26.0), (-5662.0, -650.0, 26.0),
                   (-5662.0, -800.0, 26.0), (-5662.0, -800.0, 900.0), (-5662.0, -850.0, 1330.0),
                   (cuff[0], cuff[1] + 30, 1345.0), cuff + (0, 0, 150), cuff + (0, 0, 10)]
        else:
            pts = [inlet, (inlet[0], inlet[1] - 26, 330.0), (inlet[0] - 10, -620.0, 26.0), (inlet[0] - 20, -640.0, 26.0),
                   (-5300.0, -640.0, 26.0), (-5330.0, -660.0, 40.0), (-5330.0, -820.0, 40.0), (-5330.0, -820.0, 900.0),
                   (-5340.0, -880.0, 1330.0), (cuff[0], cuff[1] + 30, 1345.0), cuff + (0, 0, 150), cuff + (0, 0, 10)]
        out.append((f"{fam} hose", _tube(pts, N.HOSE_R), N.BLACK, 1.0))
        # its power cord: up from the cord point over the head and across to the outlet box
        cp = vac_point(fam, "cord")
        box_pt = np.array([px + (-40 if fam == "Al" else 40), py - 56, N.POST_H + 70])
        cord = [cp, cp + (0, 40, 220), ((cp[0] + box_pt[0]) / 2, (cp[1] + box_pt[1]) / 2, 1180.0),
                box_pt + (0, -20, 30), box_pt]
        out.append((f"{fam} cord", _tube(cord, 5.0, 8), CORD, 1.0))
    # ---- the pails, one per family: lid set on, not crimped; a label in words; a bonding lead
    for fam, (x, y) in PAIL.items():
        put(f"{fam} pail", N.pail_meshes(), _M(x, y))
        # the family's 25 mm band (notes/colour_coding.md, "Powder-waste cans"), just under the rim, and the words
        z0, z1 = N.PAIL_H - 70.0, N.PAIL_H - 45.0
        rr = lambda z: N.PAIL_OD_BOT / 2 + (N.PAIL_OD_TOP / 2 - N.PAIL_OD_BOT / 2) * z / N.PAIL_H + 1.0  # noqa: E731
        out.append((f"{fam} pail band", N.lathe([(rr(z0) - 1.5, z0), (rr(z0), z0), (rr(z1), z1), (rr(z1) - 1.5, z1)])
                    .translate((x, y, 0), inplace=False), FAM[fam], 1.0))
        for nm, m, c, op in text_plate((((FAM_WORDS[fam],), 1.0), (("sealed liners", "lid on, not crimped"), 0.55)),
                                       x, y - 147.0, 190.0, 200.0, 130.0):
            out.append((f"{fam} pail {nm}", m, c, op))
    # ---- Risk Management's Solid Material bucket: an HDPE pail, the liner folded over its rim, the lid on, labelled
    bx, by = BUCKET
    r0, r1, h = BUCKET_D / 2 - 12, BUCKET_D / 2, BUCKET_H
    out.append(("bucket", N.lathe([(0, 0), (r0, 0), (r1, h - 20), (r1, h), (r1 - 6, h), (r0 - 6, 8), (0, 8)])
                .translate((bx, by, 0), inplace=False), HDPE, 1.0))
    out.append(("bucket liner", N.lathe([(r1 - 1, h - 60), (r1 + 2, h - 60), (r1 + 2, h + 4), (r1 - 1, h + 4)])
                .translate((bx, by, 0), inplace=False), LINER, 1.0))
    out.append(("bucket lid", N.lathe([(0, h + 2), (r1 + 6, h + 2), (r1 + 6, h + 20), (0, h + 24)])
                .translate((bx, by, 0), inplace=False), HDPE, 1.0))
    for nm, m, c, op in text_plate(((("SOLID MATERIAL",), 1.0), (("waste powder, sweepings",), 0.62)), bx, by - r1 + 4.0,
                                   200.0, 230.0, 120.0):
        out.append((f"bucket {nm}", m, c, op))
    # ---- the filter can: steel, dry sand inside, the lid on, labelled, bonded
    sx, sy = SAND
    rs = SAND_D / 2
    out.append(("sand can", N.lathe([(0, 0), (rs, 0), (rs, SAND_H), (rs - 5, SAND_H), (rs - 5, 6), (0, 6)])
                .translate((sx, sy, 0), inplace=False), STEEL, 1.0))
    out.append(("sand can lid", N.lathe([(0, SAND_H - 2), (rs + 4, SAND_H - 2), (rs + 4, SAND_H + 14), (0, SAND_H + 16)])
                .translate((sx, sy, 0), inplace=False), (0.48, 0.50, 0.53), 1.0))
    for nm, m, c, op in text_plate(((("USED FILTERS",), 1.0), (("in dry sand",), 0.7)), sx, sy - rs - 1.0, 150.0,
                                   170.0, 100.0):
        out.append((f"sand can {nm}", m, c, op))
    # ---- the area sign, its face to the aisle
    put("sign", N.sign_meshes(), _M(*SIGN))
    # ---- the ground bar and the bonds: each pail, the can, each vacuum's lug and the post's lug
    gx, gy = BAR
    out.append(("ground bar", _box(gx - 60, gx + 60, gy - 15, gy + 15, 0, 40), COPPER, 1.0))
    leads = []
    for fam, (x, y) in PAIL.items():              # from a ring terminal under each pail's rim, east of its label
        lug = np.array([x + 140.0, y + 60.0, 300.0])
        leads.append([lug, lug + (20, 30, -150), (lug[0] + 30, gy - 40.0, 6.0), (gx + 40 * (1 if fam == "Cu" else -1),
                                                                                gy - 20.0, 6.0), (gx, gy, 45.0)])
    # the can's, each vacuum's and the post's: down to the floor, then in one corridor between the vacuums and the
    # pails (y -584 to -606) to the bar
    lug = np.array([sx, sy + rs, 200.0])
    leads.append([lug, (sx, sy + rs + 20, 60.0), (sx, sy + rs + 50, 6.0), (sx, -598.0, 6.0), (gx - 80, -598.0, 6.0),
                  (gx - 50, gy, 20.0), (gx - 30, gy, 45.0)])
    for fam, yc in (("Al", -584.0), ("Cu", -590.0)):
        lg = vac_point(fam, "ground_lug")
        leads.append([lg, (lg[0], lg[1] - 20, 15.0), (lg[0] - 5, yc, 6.0), (gx - 80, yc, 6.0), (gx - 40, gy + 5, 30.0),
                      (gx - 20, gy, 45.0)])
    plug = (Mp @ np.r_[0.0, 40.0, 40.0, 1.0])[:3]
    leads.append([plug, (plug[0], plug[1] + 20, 18.0), (plug[0], -616.0, 18.0), (plug[0], -606.0, 6.0),
                  (gx - 80, -606.0, 6.0), (gx - 45, gy - 8, 25.0), (gx - 25, gy, 45.0)])
    for k, pts in enumerate(leads):
        out.append((f"bond lead {k}", _tube(pts, 4.0, 8), N.GRN_YEL, 1.0))
    return out


def parts() -> dict:
    """{name: (mesh, rgb, opacity)}, world coordinates, merged by colour (setup_lab.Floor adds them as group
    "powder_point")."""
    by: dict = {}
    for _, m, c, op in parts_list():
        by.setdefault((tuple(round(float(v), 3) for v in c), float(op)), []).append(m)
    out = {}
    for i, ((c, op), ms) in enumerate(sorted(by.items())):
        m = ms[0].merge(ms[1:]) if len(ms) > 1 else ms[0]
        out[f"p{i}"] = (m.clean().triangulate(), c, op)
    return out


def item_rects() -> dict:
    """Each item's plan rectangle (x0, x1, y0, y1), from its meshes (wands, hoses, cords and leads left out: they lie
    on or hang over the others)."""
    by: dict = {}
    for nm, m, c, op in parts_list():
        if any(k in nm for k in ("wand", "crevice", "hose", "cord", "lead", "conduit")):
            continue
        key = nm.split(" ")[0] if nm.split(" ")[0] in ("Al", "Cu") else nm.split(" ")[0]
        key = " ".join(nm.split(" ")[:2]) if nm.split(" ")[0] in ("Al", "Cu") else key
        b = m.bounds
        r = by.get(key)
        by[key] = (b[0], b[1], b[2], b[3]) if r is None else (min(r[0], b[0]), max(r[1], b[1]), min(r[2], b[2]),
                                                               max(r[3], b[3]))
    return by


def _rect() -> tuple:
    rs = [m.bounds[:4] for nm, m, _, _ in parts_list() if "conduit" not in nm]
    return (min(r[0] for r in rs), max(r[1] for r in rs), min(r[2] for r in rs), max(r[3] for r in rs))


RECT = (-5868.0, -4505.0, -1222.0, -60.0)       # the whole point's plan rectangle, rounded out (``check`` confirms it)

# label anchors for the clips (world mm)
ANCHORS = {
    "Al vac": (VAC["Al"][0], VAC["Al"][1], 1150.0), "Cu vac": (VAC["Cu"][0], VAC["Cu"][1], 1150.0),
    "Al pail": (PAIL["Al"][0], PAIL["Al"][1] - 150.0, 300.0), "Cu pail": (PAIL["Cu"][0], PAIL["Cu"][1] - 150.0, 300.0),
    "bucket": (BUCKET[0], BUCKET[1] - 150.0, 330.0), "sand": (SAND[0], SAND[1] - 100.0, 250.0),
    "sign": (SIGN[0], SIGN[1] - 10.0, 750.0), "post": (POST[0], POST[1], 1150.0),
    "class D": (-5150.0, -1500.0, 700.0), "super D": (-5650.0, -1520.0, 400.0),
    "bar": (BAR[0], BAR[1], 40.0),
}


def neighbours() -> dict:
    """The plan rectangles round the point it must stay clear of (world mm): the safety PR's fixed units as drawn
    (safety.PLACES with the post, 680R and pail models' own bounds), the rePowder's back and pump (repowder/model.py
    as lab._repowder draws it, solid parts above the floor), the docks' lanes and pivot circles and the glovebox's
    target post (setup_lab fit, out/tray_plan.json, as boxes)."""
    return {
        "B570 post": (-5277.0, -5023.0, -1527.0, -1273.0),
        "B570 keep-clear": (-5404.0, -4896.0, -2335.0, -1421.0),
        "Super D pail": (-5806.0, -5485.0, -1626.0, -1325.0),
        "680R": (-6681.0, -5919.0, -1281.0, -368.0),
        "rePowder pump": (-4655.0, -4195.0, -1580.0, -1360.0),
        "rePowder west side": (-4475.0, -4175.0, -1577.0, -825.0),
        "rePowder ground bar": (-4835.0, -4715.0, -1655.0, -1625.0),
        "rePowder lane (+30)": (-5792.0, -3057.0, -2550.0, -1910.0),
        "rePowder pivot (box of its circle +30)": (-5886.0, -4838.0, -2754.0, -1706.0),
        "glovebox post foot": (-6800.0, -6500.0, -1862.0, -1562.0),
        "glovebox lane (+30)": (-8180.0, -6870.0, -2252.0, -1612.0),
        "atom_vacuum MIR_PARK": (-4695.0, -3895.0, -3140.0, -2560.0),
    }


def check() -> dict:
    """Every item's rectangle against every neighbour's: the smallest gap, mm (negative: they overlap)."""
    def gap(a, b):
        dx = max(a[0] - b[1], b[0] - a[1])
        dy = max(a[2] - b[3], b[2] - a[3])
        return max(dx, dy)
    items, nb = item_rects(), neighbours()
    out = {}
    for k, r in items.items():
        g = {n: round(gap(r, rr)) for n, rr in nb.items()}
        n = min(g, key=g.get)
        out[k] = dict(rect=[round(v) for v in r], nearest=n, gap_mm=g[n])
    keys = sorted(items)
    inner = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if not (a.split()[0] in ("station", "outlet") and b.split()[0] in ("station", "outlet")):
                inner.append((a, b, round(gap(items[a], items[b]))))
    rr = _rect()
    return dict(items=out, closest_pairs=sorted(inner, key=lambda t: t[2])[:6], rect=[round(v) for v in rr],
                rect_inside_RECT=bool(rr[0] >= RECT[0] and rr[1] <= RECT[1] and rr[2] >= RECT[2] and rr[3] <= RECT[3]),
                rect_vs_neighbours={n: round(gap(RECT, r)) for n, r in neighbours().items()})


if __name__ == "__main__":
    import json
    print(json.dumps(check(), indent=1))
