"""The atomizer charge that the alloy workflow carries instead of a vial: the lab's charge cup, vented plug and press
sleeve, turned from high-purity Al or Cu bar, as PyVista meshes. A fixture rack, the doser's cup adapter, a press for
the plug, the AMR's cup carrier and the run's recipe go with them.

Geometry is #222's ``atomizer-charge/cad/charge_cad.py`` (branch ``claude/issue-222-20260925-0343``, commit
2a608d6), the parametric CAD behind the lab's STEP files, shop drawing and process sheets. The profiles below are
copied from it, dimension for dimension:

* **Cup (P2):** 3/4 in bar, 2.5 in long, a 1/2 in bore 1.875 in deep with a 118° drill point, 0.5 mm edge breaks.
* **Plug (P3):** 1/2 in press fit, 3/8 in long, a 15° lead-in, a 1/16 in vent through its axis (#104: the chamber is
  pumped down before melting, so the air under the plug has to have somewhere to go).
* **Press sleeve (F1):** 1018 steel, 1.25 in round, bored to the cup's OD + .0005 in, as long as the cup, so the
  cup's wall can't bulge when the plug goes in and the press bottoms out flush.

**The cups come in two metals** (byu-vcl #303): high-purity Al (5N, the Ø20 mm rod of DAL #152; the trial cups are
6063) and high-purity Cu (oxygen-free C10100, "dimensions similar to the aluminum rods so that we can insert them
into the atomizer", DAL #162). Each takes a plug of its own metal.

Every lathe part can also be built cut in half (``cut=True``, the front half removed), so a close-up shows the
bore, the powder and the plug going in. ``lathe()`` revolves a closed (r, z) profile about z.

    python3 charge.py      # prints the recipe -> out/alloy_recipe.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
IN = 25.4

# ------------------------------------------------------------------ #222 charge_cad.py, verbatim
STOCK_D = 0.750 * IN
SLUG_L = 2.500 * IN
EDGE_CHAMFER = 0.5
CUP_BORE_D = 0.500 * IN
CUP_BORE_DEPTH = 1.875 * IN
DRILL_POINT_DEG = 118.0
RIM_CHAMFER = 0.015 * IN
PLUG_L = 0.375 * IN
PLUG_LEADIN_DEG = 15.0
PLUG_LEADIN_L = 0.060 * IN
PLUG_LEADIN_R = PLUG_LEADIN_L * math.tan(math.radians(PLUG_LEADIN_DEG))
PLUG_TOP_CHAMFER = 0.015 * IN
VENT_D = 1 / 16 * IN
SLEEVE_OD = 1.250 * IN
SLEEVE_BORE_D = STOCK_D + 0.0005 * IN
SLEEVE_L = SLUG_L
PLUG_SEAT = 0.0          # plug top flush with the rim: F1 is as long as the cup, so the ram bottoms out on it (#222)

# ------------------------------------------------------------------ colours
AL_5N = (0.84, 0.85, 0.87)
CU = (0.80, 0.46, 0.28)
STEEL = (0.42, 0.43, 0.47)
PRINT = (0.10, 0.55, 0.55)          # PETG teal, as lab_models' printed holders
POWDERS = {                         # name: (colour, tapped density g/cm3, source of the density)
    "Ni": ((0.47, 0.48, 0.47), 4.9, "assumed: 55 % of 8.91, a gas-atomized spherical powder tapped"),
    "Fe": ((0.30, 0.29, 0.29), 4.3, "assumed: 55 % of 7.87"),
    "Cu": ((0.66, 0.36, 0.22), 4.9, "assumed: 55 % of 8.96"),
    "Al": ((0.62, 0.63, 0.66), 1.60, "#222: AlSi10Mg tapped by hand, 1.60"),
    "Si": ((0.36, 0.37, 0.42), 1.10, "#222: irregular Si tapped, 1.10"),
}
RHO = {"Al": 2.699, "Cu": 8.94}     # 5N Al; C10100


def drill_point_h(d: float) -> float:
    return (d / 2) / math.tan(math.radians(DRILL_POINT_DEG / 2))


def cup_profile(d=STOCK_D, length=SLUG_L, bore=CUP_BORE_D, depth=CUP_BORE_DEPTH):
    r, rb, c = d / 2, bore / 2, EDGE_CHAMFER
    floor = length - depth
    return [(0, 0), (r - c, 0), (r, c), (r, length - c), (r - c, length), (rb + RIM_CHAMFER, length),
            (rb, length - RIM_CHAMFER), (rb, floor), (0, floor - drill_point_h(bore))]


def plug_profile(d=CUP_BORE_D, length=PLUG_L):
    r, rv = d / 2, VENT_D / 2
    return [(rv, 0), (r - PLUG_LEADIN_R, 0), (r, PLUG_LEADIN_L), (r, length - PLUG_TOP_CHAMFER),
            (r - PLUG_TOP_CHAMFER, length), (rv, length)]


def sleeve_profile():
    ro, rb, c = SLEEVE_OD / 2, SLEEVE_BORE_D / 2, 1.0
    return [(rb + 0.5, 0), (ro - c, 0), (ro, c), (ro, SLEEVE_L - c), (ro - c, SLEEVE_L), (rb + 0.5, SLEEVE_L),
            (rb, SLEEVE_L - 0.5), (rb, 0.5)]


FLOOR_Z = SLUG_L - CUP_BORE_DEPTH                       # where the straight bore ends, cup frame
PLUG_HOME_Z = SLUG_L - PLUG_SEAT - PLUG_L               # plug bottom when pressed home
FILL_TOP = PLUG_HOME_Z                                  # "tapped to the plug line" (#222, E1/E3/E5/E6)


def powder_profile(top: float, bore=CUP_BORE_D):
    """The powder column from the drill point up to `top` (cup frame)."""
    rb = bore / 2 - 0.05
    return [(0, FLOOR_Z - drill_point_h(bore) + 0.05), (rb, FLOOR_Z + 0.05), (rb, top), (0, top)]


# ------------------------------------------------------------------ meshes
def lathe(profile, cut: bool = False, res: int = 72) -> pv.PolyData:
    """Revolve a closed (r, z) profile about z. cut=True keeps only the back half (y >= 0), with the cut faces
    capped, so a camera in front sees the whole section, as #124's atomizer cutaways do."""
    pts = np.array([(r, 0.0, z) for r, z in profile], float)
    n = len(pts)
    face = pv.PolyData(pts, faces=np.r_[n, np.arange(n)])
    m = face.extrude_rotate(resolution=res // 2 if cut else res, angle=180.0 if cut else 360.0, capping=cut,
                            rotation_axis=(0, 0, 1))
    m = m.triangulate().clean()
    try:
        m = m.compute_normals(split_vertices=True, feature_angle=50.0, auto_orient_normals=cut)
    except Exception:       # noqa: BLE001  (an open seam: keep the mesh's own normals)
        m = m.compute_normals(split_vertices=True, feature_angle=50.0)
    return m


def cup(cut=False):
    return lathe(cup_profile(), cut)


def plug(cut=False):
    return lathe(plug_profile(), cut)


def sleeve(cut=False):
    return lathe(sleeve_profile(), cut)


def powder(top: float, cut=False):
    return lathe(powder_profile(top), cut)


def unit_powder(cut=False):
    """A powder column of unit height from the bore floor, for an animation to scale in z (the drill point is left
    out: it is filled first, in the first few frames)."""
    rb = CUP_BORE_D / 2 - 0.05
    return lathe([(0, 0), (rb, 0), (rb, 1.0), (0, 1.0)], cut, res=48)


def drill_point_fill(cut=False):
    """The powder in the 118° drill point under the straight bore, cup frame."""
    rb = CUP_BORE_D / 2 - 0.05
    return lathe([(0, FLOOR_Z - drill_point_h(CUP_BORE_D) + 0.05), (rb, FLOOR_Z + 0.05), (0, FLOOR_Z + 0.05)], cut,
                 res=48)


def _box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def _cylz(r, z0, z1, x=0.0, y=0.0, res=48):
    return pv.Cylinder(center=(x, y, (z0 + z1) / 2), direction=(0, 0, 1), radius=r, height=z1 - z0,
                       resolution=res).triangulate()


def _ring(ro, ri, z0, z1, x=0.0, y=0.0):
    return lathe([(ri, z0), (ro, z0), (ro, z1), (ri, z1)], res=48).translate((x, y, 0), inplace=False)


# ------------------------------------------------------------------ fixtures
RACK_COLS = 8               # four cups a run, two runs (Al and Cu) made up together
RACK_PITCH = 40.0
RACK_H = 30.0
CUP_POCKET = 22.0           # the cup stands 22 mm deep in the rack
PLUG_POCKET = 5.0
RACK_Y = {"cup": -20.0, "plug": 16.0}   # cups in the front row, where a level gripper reaches them from the front


def rack(cols: int = RACK_COLS):
    """A printed charge rack (#222's holder_charge, as two rows of eight): cups in the front row, so a level gripper
    takes them from the front; their plugs behind, in shallow pockets, taken from above. Returns the block, its pocket
    rims and the seats: {"cup": [(x, y, z)], "plug": [...]}, base centres in the rack's frame."""
    RACK_COLS = cols        # noqa: N806
    w = RACK_COLS * RACK_PITCH + 16
    d = 80.0
    body = _box(-w / 2, w / 2, -d / 2, d / 2, 0, RACK_H)
    xs = [-w / 2 + 8 + RACK_PITCH * (i + 0.5) for i in range(RACK_COLS)]
    seats = {"cup": [(x, RACK_Y["cup"], RACK_H - CUP_POCKET) for x in xs],
             "plug": [(x, RACK_Y["plug"], RACK_H - PLUG_POCKET) for x in xs]}
    rims = None
    for x in xs:       # pocket rims, so the pockets read from a distance
        for (y, ro, ri) in ((RACK_Y["cup"], STOCK_D / 2 + 3.0, STOCK_D / 2 + 0.6),
                            (RACK_Y["plug"], CUP_BORE_D / 2 + 2.5, CUP_BORE_D / 2 + 0.5)):
            r = _ring(ro, ri, RACK_H - 0.4, RACK_H + 0.6, x, y)
            rims = r if rims is None else rims.merge(r)
    return body, rims, seats


def doser_adapter():
    """A printed holder that stands a cup in the multi-doser's 28 mm vial cup (assumed): 27.7 mm across, bored for
    the 3/4 in cup."""
    return lathe([(STOCK_D / 2 + 0.3, 0.0), (27.7 / 2, 0.0), (27.7 / 2, 14.0), (STOCK_D / 2 + 0.3, 14.0)], res=48)


# ------------------------------------------------------------------ one funnel per powder (byu-vcl PR #318)
# The doser itself has no funnel. Charging cups by hand, the lab used paper funnels, and one funnel only ever sees one
# powder (cross-contamination). So each powder has its own funnel, labelled with its colour, and it is only used for
# that powder: a stem under 11 mm that points into the cup's 12.7 mm bore without touching it, a flange that rests in a
# fork, and a band to grip by. Frame: z = 0 at the stem's tip, the funnel's axis on z. Our design, not measured.
FUNNEL = dict(stem_od=9.0, stem_id=6.0, stem_l=12.0, flange_d=28.0, flange_t=2.0, cone_r=20.0, cone_h=22.0, wall=1.4,
              band_d=42.0, band_h=6.0, gap=4.0)
FUNNEL["h"] = FUNNEL["stem_l"] + FUNNEL["flange_t"] + FUNNEL["cone_h"]       # 36 mm, stem tip to rim
FUNNEL["grasp"] = FUNNEL["h"] - FUNNEL["band_h"] / 2                          # the band's middle
FUNNEL_LABEL = {"Si": (0.95, 0.75, 0.10), "Ni": (0.20, 0.62, 0.30), "Fe": (0.80, 0.25, 0.20), "Cu": (0.85, 0.45, 0.20),
                "Al": (0.25, 0.45, 0.85)}


def funnel(cut: bool = False):
    """{part: mesh} of a powder funnel (printed PP, white), plus its label ring ("label"); cut=True: the back half."""
    f = FUNNEL
    s0, s1 = f["stem_l"], f["stem_l"] + f["flange_t"]
    ro, ri, w = f["stem_od"] / 2, f["stem_id"] / 2, f["wall"]
    top = f["h"]
    body = lathe([(ri, 0.0), (ro, 0.0), (ro, s0), (f["flange_d"] / 2, s0), (f["flange_d"] / 2, s1),
                  (ro + w, s1), (f["cone_r"] + w, top - f["band_h"]), (f["band_d"] / 2, top - f["band_h"]),
                  (f["band_d"] / 2, top), (f["cone_r"], top), (ri, s1)], cut=cut, res=56)
    label = _ring(f["band_d"] / 2 + 0.4, f["band_d"] / 2 - 0.2, top - f["band_h"] + 1.0, top - 1.0)
    return {"body": body, "label": label}


def funnel_stand(n: int = 2, pitch: float = 64.0):
    """A printed stand that holds the funnels by their flanges in forks open to the front (-y), so a level gripper
    takes one from the front: the block, and the seats (stem-tip points, stand frame)."""
    f = FUNNEL
    w = n * pitch + 12.0
    plate_z = 34.0                                                   # the forks' top: the flanges rest here
    base = _box(-w / 2, w / 2, 0.0, 40.0, 0.0, plate_z)              # the block, behind the forks
    plate = _box(-w / 2, w / 2, -40.0, 0.0, plate_z - 5.0, plate_z)  # the fork plate, over the stems
    foot = _box(-w / 2, w / 2, -40.0, 40.0, 0.0, 4.0)
    xs = [-w / 2 + 6 + pitch * (i + 0.5) for i in range(n)]
    seats = [(x, -22.0, plate_z - f["stem_l"]) for x in xs]
    m = base.merge(plate).merge(foot)
    for x in xs:                                                     # the slots, drawn as dark strips on the plate
        m = m.merge(_box(x - 5.5, x + 5.5, -40.0, -22.0, plate_z - 0.2, plate_z + 0.4))
    return m, seats


# ------------------------------------------------------------------ the doser's cup station, rebuilt for cups
# The rig's 100 g load cell, its vial cup, the vial post and the shared catch funnel come out. In their place: a 2020
# post on the same base rail, a cradle (a C open to the front, so the arm slides the cup in level) and above it a
# fork for the powder's own funnel, its stem 4 mm over the cup's rim. Rig frame (multidoser/layout.py), mm. Our
# design: the rig's docking actuator stands 6 mm behind the auger's outlet, so nothing as big as a balance's pan fits
# under the outlet as the rig is built; the cups are weighed on the HR-202i beside it instead.
STATION = dict(cup_base_z=194.0, post_xy=(18.33, -110.0), post_top=282.0, cradle_t=6.0, cradle_wall=8.0)


def station_fittings(axis_xy=(18.33, 4.76)):
    """{name: (mesh, colour)} of the post, cradle and funnel fork, rig frame; and the seats: the cup's base and the
    funnel's stem tip."""
    st, f = STATION, FUNNEL
    ax, ay = axis_xy
    px, py = st["post_xy"]
    zc = st["cup_base_z"]
    alu, printed = (0.70, 0.71, 0.73), PRINT
    post = _box(px - 10, px + 10, py - 10, py + 10, 35.0, st["post_top"])
    # cradle: a plate under the cup and a C wall round its back half, on an arm from the post
    plate = _box(ax - 17, ax + 17, ay - 17, ay + 17, zc - st["cradle_t"], zc)
    arm1 = _box(ax - 8, ax + 8, py + 10, ay - 17, zc - st["cradle_t"], zc)
    # the back half only (+x, away from the arm), so the cup slides in from -x: lathe(cut) keeps y >= 0; turn it
    wall = lathe([(STOCK_D / 2 + 0.6, zc), (STOCK_D / 2 + 3.6, zc), (STOCK_D / 2 + 3.6, zc + st["cradle_wall"]),
                  (STOCK_D / 2 + 0.6, zc + st["cradle_wall"])], cut=True, res=48)
    wall = wall.rotate_z(-90.0, inplace=False).translate((ax, ay, 0), inplace=False)
    # funnel fork: its top 4 mm + stem length over the rim; a slot open to the front (-x) for the stem
    tip = zc + SLUG_L + f["gap"]
    top = tip + f["stem_l"]
    fork = _box(ax + 5.5, ax + 20, ay - 20, ay + 20, top - 4, top).merge(
        _box(ax - 20, ax + 5.5, ay + 5.5, ay + 20, top - 4, top)).merge(
        _box(ax - 20, ax + 5.5, ay - 20, ay - 5.5, top - 4, top))
    arm2 = _box(ax - 8, ax + 8, py + 10, ay - 20, top - 4, top)
    parts = {"post": (post, alu), "cradle": (plate.merge(arm1).merge(wall), printed),
             "fork": (fork.merge(arm2), printed)}
    return parts, {"cup": (ax, ay, zc), "funnel": (ax, ay, tip)}


# The plug press (assumed: a benchtop electric press with a shuttle nest; the lab's own press-fit station is a 1 t
# arbor press, #222 E4, and F1 is #222's sleeve). Press frame: base centre on the tray floor, the column at the back
# (+y). The nest slides on a rail from OUT (in front, open above, where the arm loads it) to IN (under the ram).
PR = dict(base_y=(-175.0, 150.0), base_x=130.0, base_h=40.0, rail_h=6.0, nest_h=14.0, ram_y=-10.0, out_y=-125.0,
          ram_r=15.0, z_head=245.0, z_top=385.0, motor_h=125.0, eject=40.0)
PR["nest_top"] = PR["base_h"] + PR["rail_h"] + PR["nest_h"]          # the sleeve's (and an ejected-down cup's) base
PR["sleeve_top"] = PR["nest_top"] + SLEEVE_L
PR["ram_up"] = PR["sleeve_top"] + 100.0                               # the ram's face, retracted


def press_parts():
    """{"fixed": {name: (mesh, colour)}, "nest": ..., "ram": ..., "ejector": ...}. The nest's meshes are in its own
    frame (its centre at the origin, z from the tray floor); the ram's face is at z = 0; the ejector's top at z = 0."""
    bx, (y0, y1), bh = PR["base_x"], PR["base_y"], PR["base_h"]
    ry, zh, zt = PR["ram_y"], PR["z_head"], PR["z_top"]
    blue = (0.20, 0.36, 0.62)
    fixed = {
        "frame": (_box(-bx, bx, y0, y1, 0, bh).merge(_box(-55, 55, 60, y1, bh, zt))
                  .merge(_box(-70, 70, ry - 62, y1, zh, zt)), blue),
        "rail": (_box(-24, 24, PR["out_y"] - 40, ry + 40, bh, bh + PR["rail_h"]), STEEL),
        "motor": (_cylz(46.0, zt, zt + PR["motor_h"], 0.0, ry), (0.13, 0.13, 0.14)),
        "guide": (_cylz(PR["ram_r"] + 8, zh - 18, zh, 0.0, ry), STEEL),
    }
    z0 = bh + PR["rail_h"]
    nest = {"nest": (_box(-34, 34, -34, 34, z0, PR["nest_top"]), (0.62, 0.63, 0.66)),
            "sleeve": (sleeve().translate((0, 0, PR["nest_top"]), inplace=False), STEEL)}
    ram_m = _cylz(PR["ram_r"], 0.0, zh - PR["ram_up"] + 40.0)
    ej = _cylz(4.5, -PR["eject"] - 4.0, 0.0)
    return {"fixed": fixed, "nest": nest, "ram": (ram_m, (0.72, 0.73, 0.76)), "ejector": (ej, (0.72, 0.73, 0.76))}


def press():
    """The press assembled, nest in, for static scenes: {name: (mesh, colour)}."""
    p = press_parts()
    out = dict(p["fixed"])
    for k, (m, c) in p["nest"].items():
        out[k] = (m.translate((0, PR["ram_y"], 0), inplace=False), c)
    out["ram"] = (p["ram"][0].translate((0, PR["ram_y"], PR["ram_up"]), inplace=False), p["ram"][1])
    return out


def carrier(n=4, pitch=34.0):
    """A four-cup carrier on the AMR's cabinet top, where the charged cups ride to the atomizer: a block on a
    post (props.buffer_holder's post), its pockets in a row along x. Returns the mesh and the seats (cup base
    centres) in its own frame."""
    import props as P
    post = _cylz(16.0, 0.0, P.HOLDER_H)
    foot = _box(-45, 45, -45, 45, 0, 8)
    w = n * pitch + 16
    blk = _box(-w / 2, w / 2, -24, 24, P.HOLDER_H, P.HOLDER_H + 30.0)
    seats = [(-w / 2 + 8 + pitch * (i + 0.5), 0.0, P.HOLDER_H + 30.0 - CUP_POCKET) for i in range(n)]
    return post.merge(foot).merge(blk), seats


# ------------------------------------------------------------------ the run
def volumes() -> dict:
    """Solid and cavity volumes, cm3, from the profiles (Pappus: V = 2 pi * area * centroid radius)."""
    def vol(profile):
        p = np.array(profile + [profile[0]], float)
        r, z = p[:, 0], p[:, 1]
        a = r[:-1] * z[1:] - r[1:] * z[:-1]
        area = a.sum() / 2
        cr = ((r[:-1] + r[1:]) * a).sum() / (6 * area)
        return float(abs(2 * math.pi * area * cr) / 1000.0)
    return {"cup": vol(cup_profile()), "plug": vol(plug_profile()), "cavity": vol(powder_profile(FILL_TOP)),
            "slug": math.pi / 4 * STOCK_D ** 2 * SLUG_L / 1000.0}


# The cups the workflow charges: four 5N Al cups with Si for this run's Al-10Si (the Si of the AlSi10Mg the line prints),
# and four OFE Cu cups with Ni for the next run's 90/10 Cu-Ni (the Navy's seawater alloy, C70600 less its 1-1.8 % Fe;
# DAL's Cu work, #162, #219). Four charges a crucible is how the lab loads the rePowder (byu-vcl PR #318; the Oct 27
# 630 bronze run, DAL #219/#230, went in as 4 rod pieces, 1,080 g); #222 has four places round the sealing rod. The
# doser fills each bore with one powder; the fraction of the cavity under the plug that it fills sets the composition.
RUNS = {"Al-10Si": ("Al", "Si", 10.0, 4), "Cu-10Ni": ("Cu", "Ni", 10.0, 4)}   # cup metal, powder, powder wt%, cups


def fill_fraction(metal: str, pw: str, wt: float) -> float:
    """The fraction of the cavity under the plug that `pw` must fill for `wt` wt% of it in a cup + plug of `metal`."""
    v = volumes()
    m_metal = (v["cup"] + v["plug"]) * RHO[metal]
    return m_metal * wt / (100.0 - wt) / (v["cavity"] * POWDERS[pw][1])


def recipe() -> dict:
    v = volumes()
    runs = {}
    for name, (metal, pw, wt, n) in RUNS.items():
        cups, total = [], {}
        frac = fill_fraction(metal, pw, wt)
        for _ in range(n):
            m_cup = v["cup"] * RHO[metal]
            m_plug = v["plug"] * RHO[metal]
            m_pw = v["cavity"] * POWDERS[pw][1] * frac
            for el, m in ((metal, m_cup + m_plug), (pw, m_pw)):
                total[el] = total.get(el, 0.0) + m
            cups.append(dict(cup=f"{'5N Al' if metal == 'Al' else 'OFE Cu (C10100)'} cup + plug", powder=pw,
                             cup_g=round(m_cup, 2), plug_g=round(m_plug, 2), powder_g=round(m_pw, 2),
                             fill_mm=round((FILL_TOP - FLOOR_Z) * frac, 1),
                             headspace_mm=round((FILL_TOP - FLOOR_Z) * (1 - frac), 1)))
        mass = sum(total.values())
        runs[name] = dict(cups=cups, charge_g=round(float(mass), 1),
                          designed_wt_pct={k: round(float(100 * m / mass), 2) for k, m in total.items()})
    return dict(volumes_cm3={k: round(x, 3) for k, x in v.items()}, runs=runs,
                densities={k: dict(tapped_g_cm3=d, source=s) for k, (_, d, s) in POWDERS.items()},
                note="Designed composition: what the charge gives if every gram dissolves and none is lost; ICP/EDS "
                     "on the powder measures recovery (#222). Cup and plug volumes are #222's CAD. The Ni tapped "
                     "density is assumed. Powder below the plug line leaves headspace under the plug, as #222's E5 "
                     "does; the plug's vent lets that air out when the chamber is pumped down.")


if __name__ == "__main__":
    r = recipe()
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "alloy_recipe.json").write_text(json.dumps(r, indent=1) + "\n")
    print(json.dumps(r, indent=1))
