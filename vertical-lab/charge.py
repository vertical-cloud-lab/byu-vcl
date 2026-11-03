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

Every lathe part can also be built cut open (``cut=True``): a quarter removed, so a close-up shows the bore, the
powder and the plug going in. ``lathe()`` revolves a closed (r, z) profile about z.

    python3 charge.py      # prints the recipe -> out/alloy_charge.json
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
PLUG_SEAT = 0.8          # plug top below the cup's rim when pressed home (lab_models/labware.py charge_cup)

# ------------------------------------------------------------------ colours
AL_5N = (0.84, 0.85, 0.87)
CU = (0.80, 0.46, 0.28)
STEEL = (0.50, 0.51, 0.54)
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
    """Revolve a closed (r, z) profile about z. cut=True leaves out the quarter between -y and +x (the side a
    camera in front and to the right sees), with the cut faces capped."""
    pts = np.array([(r, 0.0, z) for r, z in profile], float)
    n = len(pts)
    face = pv.PolyData(pts, faces=np.r_[n, np.arange(n)])
    angle = 270.0 if cut else 360.0
    m = face.extrude_rotate(resolution=res * 3 // 4 if cut else res, angle=angle, capping=cut, rotation_axis=(0, 0, 1))
    m = m.triangulate().clean()
    if not cut:
        return m
    # extrude_rotate starts on +x and turns counter-clockwise: the missing quarter is x > 0, y < 0. Turn it so the
    # opening faces the front-right (-y, +x) of the part's own frame.
    return m.rotate_z(0.0, inplace=False)


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
RACK_COLS = 4
RACK_PITCH = 34.0
RACK_H = 30.0
CUP_POCKET = 22.0           # the cup stands 22 mm deep in the rack
PLUG_POCKET = 5.0


def rack():
    """A printed charge rack (#222's holder_charge, widened to two rows of four): cups at the back row, their
    plugs in shallow pockets at the front row. Returns the mesh and the seats: {"cup": [(x, y, z)], "plug": [...]},
    base centres in the rack's frame."""
    w = RACK_COLS * RACK_PITCH + 16
    d = 80.0
    body = _box(-w / 2, w / 2, -d / 2, d / 2, 0, RACK_H)
    xs = [-w / 2 + 8 + RACK_PITCH * (i + 0.5) for i in range(RACK_COLS)]
    seats = {"cup": [(x, 14.0, RACK_H - CUP_POCKET) for x in xs], "plug": [(x, -22.0, RACK_H - PLUG_POCKET) for x in xs]}
    rims = None
    for x in xs:       # pocket rims, so the pockets read from a distance
        for (y, ro, ri) in ((14.0, STOCK_D / 2 + 3.0, STOCK_D / 2 + 0.6), (-22.0, CUP_BORE_D / 2 + 2.5, CUP_BORE_D / 2 + 0.5)):
            r = _ring(ro, ri, RACK_H - 0.4, RACK_H + 0.6, x, y)
            rims = r if rims is None else rims.merge(r)
    return body, rims, seats


def doser_adapter():
    """A printed sleeve that stands a cup in the multi-doser's 28 mm vial cup: 27.7 mm across, bored for the 3/4 in
    cup, a 1.5 mm floor (assumed)."""
    return lathe([(STOCK_D / 2 + 0.3, 1.5), (27.7 / 2, 1.5), (27.7 / 2, 16.0), (STOCK_D / 2 + 0.3, 16.0)], res=48) \
        .merge(_cylz(27.7 / 2, 0.0, 1.5))


PRESS = dict(base=(260.0, 300.0, 40.0), col=(120.0, 90.0), throat=150.0, head_h=170.0, z_head=430.0, ram_d=30.0,
             stroke=150.0, nest_h=20.0)


def press():
    """A benchtop electric press for the plug (assumed: a 1 t servo press, C-frame, 150 mm stroke; the lab's own
    press-fit station is a 1 t arbor press, #222 E4). Frame: base centre at the origin, the ram over the nest at
    (0, -PRESS throat), the column at the back (+y). Returns {name: (mesh, colour)} and the nest's seat (the
    sleeve's base centre) and the ram's axis."""
    bw, bd, bh = PRESS["base"]
    cw, cd = PRESS["col"]
    zt = PRESS["z_head"] + PRESS["head_h"]
    ram_y = -30.0
    parts = {
        "frame": (_box(-bw / 2, bw / 2, -bd / 2, bd / 2, 0, bh)
                  .merge(_box(-cw / 2, cw / 2, bd / 2 - cd, bd / 2, bh, zt))
                  .merge(_box(-cw / 2 - 10, cw / 2 + 10, ram_y - 60, bd / 2, PRESS["z_head"], zt)), (0.20, 0.36, 0.62)),
        "motor": (_cylz(48.0, zt, zt + 150.0, 0.0, ram_y), (0.13, 0.13, 0.14)),
        "nest": (_ring(SLEEVE_OD / 2 + 6.0, SLEEVE_OD / 2 + 0.3, bh, bh + PRESS["nest_h"], 0.0, ram_y)
                 .merge(_cylz(SLEEVE_OD / 2 + 6.0, bh, bh + 2.0, 0.0, ram_y)), (0.62, 0.63, 0.66)),
        "guard": (_box(-bw / 2 + 10, -bw / 2 + 14, ram_y - 110, bd / 2 - cd, bh, PRESS["z_head"] - 10)
                  .merge(_box(bw / 2 - 14, bw / 2 - 10, ram_y - 110, bd / 2 - cd, bh, PRESS["z_head"] - 10)),
                  (0.85, 0.92, 0.95)),
    }
    seat = (0.0, ram_y, bh + 2.0)
    return parts, seat, ram_y


def ram(length=None):
    """The ram, its face at z = 0, going up (the animation moves it)."""
    L = length or PRESS["stroke"] + 60.0
    return _cylz(PRESS["ram_d"] / 2, 0.0, L).merge(_cylz(9.0, -6.0, 0.0))


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


# One run of nickel aluminium bronze, C63000 (82Cu-10Al-5Ni-3Fe, DAL #219's 630 bronze), built from high-purity
# elements: three Cu cups and one Al cup, four being the most that stand round the sealing rod (#222). The doser fills
# each cup's bore with one powder, tapped to the plug line.
RUN = [  # (cup metal, powder, fill fraction of the cavity)
    ("Cu", "Ni", 0.86),
    ("Cu", "Fe", 0.69),
    ("Cu", "Cu", 1.00),
    ("Al", "Al", 1.00),
]
C63000 = {"Cu": (78.0, 85.0), "Al": (9.0, 11.0), "Ni": (4.0, 5.5), "Fe": (2.0, 4.0)}   # wt%, ASTM B150


def recipe() -> dict:
    v = volumes()
    cups, total = [], {}
    for metal, pw, frac in RUN:
        m_cup = v["cup"] * RHO[metal]
        m_plug = v["plug"] * RHO[metal]
        m_pw = v["cavity"] * POWDERS[pw][1] * frac
        for el, m in ((metal, m_cup + m_plug), (pw, m_pw)):
            total[el] = total.get(el, 0.0) + m
        cups.append(dict(cup=f"{'5N Al' if metal == 'Al' else 'OFE Cu (C10100)'} cup + plug", powder=pw,
                         cup_g=round(m_cup, 2), plug_g=round(m_plug, 2), powder_g=round(m_pw, 2),
                         fill_mm=round((FILL_TOP - FLOOR_Z) * frac, 1)))
    mass = sum(total.values())
    comp = {k: round(float(100 * m / mass), 2) for k, m in total.items()}
    return dict(alloy="nickel aluminium bronze, C63000 (ASTM B150: Cu 78-85, Al 9-11, Ni 4-5.5, Fe 2-4 wt%)",
                volumes_cm3={k: round(x, 3) for k, x in v.items()}, cups=cups, charge_g=round(mass, 1),
                designed_wt_pct=comp, in_spec={k: bool(lo <= comp.get(k, 0) <= hi) for k, (lo, hi) in C63000.items()},
                densities={k: dict(tapped_g_cm3=d, source=s) for k, (_, d, s) in POWDERS.items()},
                note="Designed composition: what the charge gives if every gram dissolves and none is lost. Al and "
                     "Mg oxidise and evaporate in a vacuum furnace, so ICP/EDS on the powder measures recovery. "
                     "Cup and plug volumes are #222's CAD; tapped densities of Ni, Fe and Cu are assumed.")


if __name__ == "__main__":
    r = recipe()
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "alloy_charge.json").write_text(json.dumps(r, indent=1) + "\n")
    print(json.dumps(r, indent=1))
