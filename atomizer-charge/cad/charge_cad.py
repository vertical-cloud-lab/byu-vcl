"""Parametric CAD for the first rePowder atomizer charges (issue #222).

Every machined part is a lathe part, so each one is defined the way the
prototyping lab will make it: a half-profile (r, z) revolved about Z.  The same
profile drives the STEP/STL exports, the renders (``render.py``) and the
dimensioned shop drawing (``drawings.py``).

Parts that get machined (6063-T52, McMaster 1640T16, 3/4" bar on hand):

* ``solid_slug``   - E2, the solid-rod control
* ``std_cup``      - 3/4" x 2.5" cup, 1/2" bore to 3/4 of the length (Gage's spec)
* ``std_plug``     - 1/2" press-fit plug, vented, same bar
* ``thin_cup``     - short thin-wall cup for the small-batch trials (E7)
* ``thin_plug``    - 5/8" plug for it
* ``support_sleeve`` - steel sleeve that stops the cup wall bulging when the plug
  is pressed hydraulically (E4 only)

Concept only (not for machining, answers the "annulus over the piston" idea):

* ``ring_cup`` / ``ring_plug``

Context only (for the renders and the loading check): the graphite crucible,
the sealing rod with its adapter and holder arm, the insulating filling cone on
the rim, and the induction coil.  See ``../README.md`` for what is documented
and what is scaled or inferred.

Run:  python charge_cad.py      (writes step/, stl/, parts.json, experiments.json)
"""

from __future__ import annotations

import json
import math
import pathlib

from build123d import (
    Align,
    Axis,
    Box,
    Circle,
    Compound,
    Cylinder,
    Helix,
    Plane,
    Polyline,
    Pos,
    Rot,
    Sphere,
    export_step,
    export_stl,
    make_face,
    revolve,
    sweep,
)

HERE = pathlib.Path(__file__).resolve().parent
STEP_DIR = HERE / "step"
STL_DIR = HERE / "stl"

IN = 25.4  # mm per inch

# ---------------------------------------------------------------------------
# rePowder induction crucible - context geometry, NOT for machining.
#
# Documented (vendor documents, ../repowder-reference/README.md):
#   * one graphite crucible, 225 cm^3 (AMAZEMET's quote); the melt leaves
#     through a pour hole in the floor, sealed by the sealing rod, and is pushed
#     out by argon over-pressure
#   * the rod is fitted and seated BEFORE the metal goes in, and the metal is
#     filled around it (Indutherm GU500 manual pp. 47-51).  Never run without it
# Verbal (Bartosz, 9/17 call): ~20 mm rod to wall, 10-11 cm deep, and a charge
# may stand to ~12 cm.
# Nothing dimensions the crucible, but Indutherm's section of the same furnace
# (GU500 Fig. 61) is a CAD drawing, so its proportions scale.  Scaled to the
# quoted 225 cm^3 it also lands on all three of Bartosz's numbers (a 22 mm gap,
# 102 mm deep, 120 mm to the top of the insulation), so that is the scaling used
# here; repowder-reference/crucible_proportions.py has the working.  The floor is
# a ~36 deg cone, not flat, which is why the old flat-floor inference (225 ml at
# 105 mm deep) came out at 52 mm.  Measure.
#
# z = 0 is where the straight bore ends and the floor cone begins.
# ---------------------------------------------------------------------------
CRUCIBLE_ID = 57.1
BORE_STRAIGHT = 81.1  # rim down to the floor cone
FLOOR_CONE_H = 20.5  # floor cone, down to its apex on the axis: 101.6 rim to apex
CRUCIBLE_WALL = 9.1
CRUCIBLE_BOTTOM = 13.7  # graphite below the apex
POUR_HOLE_D = 6.9  # the nozzle screws in below; ours is not yet identified
SEALING_ROD_D = 12.6  # ball-tipped, seated on the floor cone round the pour hole
FILLING_CONE_H = 18.8  # insulating "filling cone" (C020) on the rim
FILLING_CONE_OD = 120.0  # schematic, as is the shape of its mouth
CRUCIBLE_MAX_FILL = BORE_STRAIGHT + FILLING_CONE_H  # a charge may stand up into the filling cone
# The rod hangs from an adapter (C018) pinned to a holder arm (C017) that reaches in
# from one side.  Both stay over the crucible while it is filled, so a charge has to
# get past them: see loading_margin().  The adapter's size is the least certain
# number in the drawing, which shows only its width along the arm.
ROD_ADAPTER_D = 21.7
ROD_ADAPTER_ABOVE_RIM = 18.3  # its lower end, about level with the top of the filling cone
ARM_ABOVE_RIM = 46.8  # underside of the holder arm
ARM_D, ARM_L, ARM_ANGLE = 16.0, 75.0, 45.0  # schematic; the arm comes in from the back right

COIL_RADIUS = 47.0  # centreline of the copper tube
COIL_TUBE_D = 8.0
COIL_PITCH = 12.5
COIL_Z0, COIL_Z1 = -28.0, 72.0

# ---------------------------------------------------------------------------
# Charge parts - 3/4" 6063-T52 bar (McMaster 1640T16, +/-0.014" on diameter)
# ---------------------------------------------------------------------------
STOCK_D = 0.750 * IN
SLUG_L = 2.500 * IN  # Gage: "cut it down to about 2.5 in"
EDGE_CHAMFER = 0.5

CUP_BORE_D = 0.500 * IN  # drill 31/64 (PILOT_DRILL_D), then bore or ream to 1/2"
PILOT_DRILL_D = 31 / 64 * IN  # leaves .0156" total stock - Machinery's Handbook for a 1/2" reamer
CUP_BORE_DEPTH = 1.875 * IN  # "to about 3/4 the length", full-diameter depth
DRILL_POINT_DEG = 118.0  # ASME B94.11M general-purpose point
RIM_CHAMFER = 0.015 * IN  # .015 break, the standard "break sharp edges" callout

PLUG_L = 0.375 * IN
PLUG_LEADIN_DEG = 15.0  # standard press-fit lead-in (ANSI B4.2 recommends 10-15 deg)
PLUG_LEADIN_L = 0.060 * IN
PLUG_LEADIN_R = PLUG_LEADIN_L * math.tan(math.radians(PLUG_LEADIN_DEG))
PLUG_TOP_CHAMFER = 0.015 * IN  # break on the parted face - deburr only, no part in the fit
VENT_D = 1 / 16 * IN  # through-vent: never seal gas in with the powder (#104, #134).
# 1/16" not 1 mm: fractional drills are in every US shop's index (ASME B94.11M), and at
# .375" deep a 1 mm bit is 9.5xD while 1/16" is 6xD.  #60 (.040") is the small alternate.

THIN_L = 1.250 * IN
THIN_BORE_D = 0.625 * IN
THIN_FLOOR = 0.125 * IN  # flat-bottom bore
THIN_PLUG_L = 0.1875 * IN
TALL_THIN_L = 100.0  # only for the ring comparison: a thin-wall cup standing full depth

SLEEVE_OD = 1.250 * IN  # 1018 CRS round, a stock size; .25" of steel is ~10x the cup wall
SLEEVE_BORE_D = STOCK_D + 0.0005 * IN  # bore to the measured cup OD +.0005 - see fit_check()
SLEEVE_L = SLUG_L  # same length as the cup, so the press bottoms out flush

# Annular "ring over the sealing rod" concept
RING_OD = 50.0  # from 2" bar
RING_ID = 16.0
RING_H = 60.0
RING_GROOVE_ID, RING_GROOVE_OD = 22.0, 42.0
RING_GROOVE_DEPTH = 45.0
RING_PLUG_L = 8.0

# Where the slugs stand in the crucible: centred in the rod-to-wall gap
SLUG_CIRCLE_R = (SEALING_ROD_D / 2 + CRUCIBLE_ID / 2) / 2

# ---------------------------------------------------------------------------
# Materials (g/cm^3) and nominal compositions (wt%)
# ---------------------------------------------------------------------------
RHO = {
    "6063": 2.69,
    "AlSi10Mg_tap": 1.60,  # gas-atomised, tapped by hand (~60 % dense)
    "AlSi10Mg_pressed": 2.00,  # ~75 % dense, E4 hydraulic press
    "Si_tap": 1.10,  # irregular Si powder, tapped (~47 % dense) - weigh it
    "Al_UA_tap": 1.65,  # re-atomised spherical 6063 powder (~61 %)
    "Al_liquid": 2.37,  # ~700 C, for melt-height estimates
    "steel": 7.85,
}
COMP = {  # (Si, Mg) wt%
    "6063": (0.40, 0.675),  # Si 0.20-0.60, Mg 0.45-0.90
    "AlSi10Mg": (10.0, 0.35),  # Si 9-11, Mg 0.20-0.45
    "Si": (100.0, 0.0),
    "Al_UA": (0.40, 0.675),  # powder made from the 6063 slugs (E2)
}


def turned(profile: list[tuple[float, float]]):
    """Revolve a closed half-profile of (r, z) points about Z - a lathe part."""
    return revolve(Plane.XZ * make_face(Polyline(*profile, close=True)), Axis.Z, 360)


def drill_point_h(d: float) -> float:
    return (d / 2) / math.tan(math.radians(DRILL_POINT_DEG / 2))


# ---------------------------------------------------------------------------
# Profiles (r, z), z = 0 at the part's base
# ---------------------------------------------------------------------------
def solid_slug_profile(d=STOCK_D, length=SLUG_L, c=EDGE_CHAMFER):
    r = d / 2
    return [(0, 0), (r - c, 0), (r, c), (r, length - c), (r - c, length), (0, length)]


def std_cup_profile(d=STOCK_D, length=SLUG_L, bore=CUP_BORE_D, depth=CUP_BORE_DEPTH):
    r, rb, c = d / 2, bore / 2, EDGE_CHAMFER
    floor = length - depth
    return [
        (0, 0),
        (r - c, 0),
        (r, c),
        (r, length - c),
        (r - c, length),
        (rb + RIM_CHAMFER, length),
        (rb, length - RIM_CHAMFER),
        (rb, floor),
        (0, floor - drill_point_h(bore)),
    ]


def plug_profile(d=CUP_BORE_D, length=PLUG_L):
    r, rv = d / 2, VENT_D / 2
    return [
        (rv, 0),
        (r - PLUG_LEADIN_R, 0),
        (r, PLUG_LEADIN_L),
        (r, length - PLUG_TOP_CHAMFER),
        (r - PLUG_TOP_CHAMFER, length),
        (rv, length),
    ]


def thin_cup_profile(d=STOCK_D, length=THIN_L, bore=THIN_BORE_D, floor=THIN_FLOOR):
    r, rb, c = d / 2, bore / 2, EDGE_CHAMFER
    return [
        (0, 0),
        (r - c, 0),
        (r, c),
        (r, length - c),
        (r - c, length),
        (rb + 0.2, length),
        (rb, length - 0.2),
        (rb, floor),
        (0, floor),
    ]


def sleeve_profile():
    ro, rb, c = SLEEVE_OD / 2, SLEEVE_BORE_D / 2, 1.0
    return [
        (rb + 0.5, 0),
        (ro - c, 0),
        (ro, c),
        (ro, SLEEVE_L - c),
        (ro - c, SLEEVE_L),
        (rb + 0.5, SLEEVE_L),
        (rb, SLEEVE_L - 0.5),
        (rb, 0.5),
    ]


def powder_profile(bore: float, z_bottom: float, z_top: float, point: bool):
    """Powder column in a bore; `point` adds the 118 deg drill-point cone."""
    rb = bore / 2
    base = [(0, z_bottom - drill_point_h(bore)), (rb, z_bottom)] if point else [(0, z_bottom), (rb, z_bottom)]
    return base + [(rb, z_top), (0, z_top)]


def ring_cup_profile():
    ri, ro = RING_ID / 2, RING_OD / 2
    gi, go = RING_GROOVE_ID / 2, RING_GROOVE_OD / 2
    zf = RING_H - RING_GROOVE_DEPTH
    c = EDGE_CHAMFER
    return [
        (ri + c, 0),
        (ro - c, 0),
        (ro, c),
        (ro, RING_H - c),
        (ro - c, RING_H),
        (go, RING_H),
        (go, zf),
        (gi, zf),
        (gi, RING_H),
        (ri + c, RING_H),
        (ri, RING_H - c),
        (ri, c),
    ]


def ring_plug_profile():
    gi, go = RING_GROOVE_ID / 2, RING_GROOVE_OD / 2
    return [(gi, 0), (go, 0), (go, RING_PLUG_L), (gi, RING_PLUG_L)]


def floor_z(r: float) -> float:
    """Height of the conical floor at radius r (z = 0 where the straight bore ends)."""
    return -(CRUCIBLE_ID / 2 - r) * FLOOR_CONE_H / (CRUCIBLE_ID / 2)


def rest_z(r_out: float, chamfer: float = 0.0) -> float:
    """Base height of a flat-bottomed part standing on the floor cone.

    The cone rises towards the wall, so the part sits on the outer edge of its base
    (radius r_out from the crucible axis, less the edge break).
    """
    return floor_z(r_out - chamfer) + 0.05


def slug_base_z(rc: float = SLUG_CIRCLE_R) -> float:
    """Where a 3/4" slug centred rc from the axis stands: a millimetre or so below z = 0."""
    return rest_z(rc + STOCK_D / 2, EDGE_CHAMFER)


def ring_base_z() -> float:
    return rest_z(RING_OD / 2, EDGE_CHAMFER)


def crucible_profile():
    ro, ri = CRUCIBLE_ID / 2 + CRUCIBLE_WALL, CRUCIBLE_ID / 2
    rh = POUR_HOLE_D / 2
    zb, zt = -FLOOR_CONE_H - CRUCIBLE_BOTTOM, BORE_STRAIGHT
    return [
        (rh, zb),
        (ro - 2, zb),
        (ro, zb + 2),
        (ro, zt - 2),
        (ro - 2, zt),
        (ri + 1, zt),
        (ri, zt - 1),
        (ri, 0),
        (rh, floor_z(rh)),
    ]


def filling_cone_profile():
    """Insulating ring on the rim; its mouth narrows down to the bore (proportions as drawn)."""
    ri, ro, z0 = CRUCIBLE_ID / 2, FILLING_CONE_OD / 2, BORE_STRAIGHT
    return [
        (ri, z0),
        (ro, z0),
        (ro, z0 + FILLING_CONE_H),
        (0.8 * CRUCIBLE_ID, z0 + FILLING_CONE_H),
        (ri, z0 + 0.1 * CRUCIBLE_ID),
    ]


def rod_ball_z() -> float:
    """Centre of the rod's ball tip, seated on the floor cone (0.05 mm proud)."""
    r = SEALING_ROD_D / 2
    half_angle = math.atan((CRUCIBLE_ID / 2) / FLOOR_CONE_H)  # cone half-angle, from the axis
    return -FLOOR_CONE_H + r / math.sin(half_angle) + 0.05


def sealing_rod():
    """Graphite rod with a ball tip, from its seat up to the adapter."""
    r, zc = SEALING_ROD_D / 2, rod_ball_z()
    top = BORE_STRAIGHT + ROD_ADAPTER_ABOVE_RIM
    shank = Cylinder(r, top - zc, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(0, 0, zc) * (Sphere(r) + shank)


def rod_holder():
    """The rod's adapter over the axis, and the arm it is pinned to (schematic)."""
    z_ad = BORE_STRAIGHT + ROD_ADAPTER_ABOVE_RIM
    z_arm = BORE_STRAIGHT + ARM_ABOVE_RIM + ARM_D / 2
    adapter = Pos(0, 0, z_ad) * Cylinder(
        ROD_ADAPTER_D / 2, z_arm + ARM_D / 2 + 4 - z_ad, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    arm = Pos(0, 0, z_arm) * Rot(0, 0, ARM_ANGLE) * Rot(0, 90, 0) * Cylinder(
        ARM_D / 2, ARM_L, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    return adapter + arm


# ---------------------------------------------------------------------------
# Solids
# ---------------------------------------------------------------------------
def ring_plug():
    """Washer plug for the ring concept, with three vents like the slug plugs."""
    plug = turned(ring_plug_profile())
    rv = (RING_GROOVE_ID + RING_GROOVE_OD) / 4
    for ang in (0, 120, 240):
        vent = Cylinder(VENT_D / 2, RING_PLUG_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
        plug -= Rot(0, 0, ang) * Pos(rv, 0, 0) * vent
    return plug


def coil():
    helix = Helix(COIL_PITCH, COIL_Z1 - COIL_Z0, COIL_RADIUS, center=(0, 0, COIL_Z0))
    start = helix @ 0
    tangent = helix % 0
    profile = Plane(origin=start, z_dir=tangent) * Circle(COIL_TUBE_D / 2)
    return sweep(profile, path=helix, is_frenet=True)


def build() -> dict:
    """All solids, keyed by name; z = 0 at each part's own base."""
    std_floor = SLUG_L - CUP_BORE_DEPTH
    std_top = SLUG_L - PLUG_L
    thin_top = THIN_L - THIN_PLUG_L
    ring_floor = RING_H - RING_GROOVE_DEPTH
    return {
        "solid_slug": turned(solid_slug_profile()),
        "std_cup": turned(std_cup_profile()),
        "std_plug": turned(plug_profile()),
        "std_powder": turned(powder_profile(CUP_BORE_D, std_floor, std_top, point=True)),
        "thin_cup": turned(thin_cup_profile()),
        "thin_plug": turned(plug_profile(THIN_BORE_D, THIN_PLUG_L)),
        "thin_powder": turned(powder_profile(THIN_BORE_D, THIN_FLOOR, thin_top, point=False)),
        "support_sleeve": turned(sleeve_profile()),
        "ring_cup": turned(ring_cup_profile()),
        "ring_plug": ring_plug(),
        "ring_powder": turned(
            [
                (RING_GROOVE_ID / 2, ring_floor),
                (RING_GROOVE_OD / 2, ring_floor),
                (RING_GROOVE_OD / 2, RING_H - RING_PLUG_L),
                (RING_GROOVE_ID / 2, RING_H - RING_PLUG_L),
            ]
        ),
        "crucible": turned(crucible_profile()),
        "filling_cone": turned(filling_cone_profile()),
        "sealing_rod": sealing_rod(),
        "rod_holder": rod_holder(),
        "coil": coil(),
    }


def powder_column(fill_mass_g: float, rho: float, bore: float, z_bottom: float, point: bool):
    """Powder solid of a given mass/density, filled up from the bottom of a bore."""
    rb = bore / 2
    area = math.pi * rb**2
    cone = area * drill_point_h(bore) / 3 if point else 0.0
    vol = fill_mass_g / rho * 1000
    height = (vol - cone) / area
    return turned(powder_profile(bore, z_bottom, z_bottom + height, point))


# ---------------------------------------------------------------------------
# Experiments (issue #222, 2026-09-24).  2 slugs per run by default (~80-100 g,
# the 100 g/run basis of the #161 purchase model).  Four fit however they lean,
# five only standing off the rod (packing()) - if they can get in at all
# (loading_margin()).
# ---------------------------------------------------------------------------
EXPERIMENTS = [
    {
        "id": "E1",
        "title": "AlSi10Mg powder in a cup, plug on top",
        "tier": "first",
        "cup": "std",
        "fill": "tap",
        "powder": {"AlSi10Mg": 1.0},
        "rho": "AlSi10Mg_tap",
    },
    {"id": "E2", "title": "Solid 6063 rod (control)", "tier": "first", "cup": "solid"},
    {
        "id": "E3",
        "title": "AlSi10Mg + Si powder, plug on top",
        "tier": "first",
        "cup": "std",
        "fill": "target_si",
        "target_si": 10.0,  # the whole charge lands at AlSi10Mg's 10 wt% Si
        "powder": {"Si": None, "AlSi10Mg": None},
    },
    {
        "id": "E4",
        "title": "AlSi10Mg, plug pressed hydraulically",
        "tier": "handy",
        "cup": "std",
        "fill": "full_bore",  # fill the whole bore, press the plug flush -> ~75 % dense
        "powder": {"AlSi10Mg": 1.0},
        "rho": "AlSi10Mg_tap",
        "fixture": "support_sleeve",
    },
    {
        "id": "E5",
        "title": "Si powder only",
        "tier": "handy",
        "cup": "std",
        "fill": "target_si",
        "target_si": 12.0,  # = the Al 4047 benchmark rods AMAZEMET supplied
        "powder": {"Si": 1.0},
    },
    {
        "id": "E6",
        "title": "Re-atomise our own 6063 powder (from E2)",
        "tier": "handy",
        "cup": "std",
        "fill": "tap",
        "powder": {"Al_UA": 1.0},
        "rho": "Al_UA_tap",
    },
    {
        "id": "E7",
        "title": "Small batch: short thin-wall cup",
        "tier": "later",
        "cup": "thin",
        "fill": "tap",
        "powder": {"AlSi10Mg": 1.0},
        "rho": "AlSi10Mg_tap",
    },
]
SLUGS_PER_RUN = 2
MAX_SLUGS = 4

# Bar consumed per piece: saw kerf + facing both ends (~3 mm)
CUT_ALLOWANCE = 3.0
BAR_ON_HAND = 24 * IN
CHUCK_REMNANT = 25.0


def cavity_volume_cm3(cup: str) -> float:
    if cup == "std":
        rb = CUP_BORE_D / 2
        h = CUP_BORE_DEPTH - PLUG_L
        return (math.pi * rb**2 * h + math.pi * rb**2 * drill_point_h(CUP_BORE_D) / 3) / 1000
    rb = THIN_BORE_D / 2
    return math.pi * rb**2 * (THIN_L - THIN_FLOOR - THIN_PLUG_L) / 1000


def full_bore_volume_cm3() -> float:
    rb = CUP_BORE_D / 2
    return (math.pi * rb**2 * CUP_BORE_DEPTH + math.pi * rb**2 * drill_point_h(CUP_BORE_D) / 3) / 1000


def charge(exp: dict, parts: dict) -> dict:
    """Per-slug masses (g) and the resulting composition for one experiment."""
    al = {
        "solid": parts["solid_slug"].volume,
        "std": parts["std_cup"].volume + parts["std_plug"].volume,
        "thin": parts["thin_cup"].volume + parts["thin_plug"].volume,
    }[exp["cup"]] / 1000 * RHO["6063"]
    powder: dict[str, float] = {}
    if exp["cup"] != "solid":
        cav = cavity_volume_cm3(exp["cup"])
        if exp["fill"] == "tap":
            (name,) = exp["powder"]
            powder[name] = cav * RHO[exp["rho"]]
        elif exp["fill"] == "full_bore":
            (name,) = exp["powder"]
            powder[name] = full_bore_volume_cm3() * RHO[exp["rho"]]
        elif exp["fill"] == "target_si":
            # Si needed so the whole slug hits the target; AlSi10Mg (if any) fills
            # the rest of the cavity and, at 10 % Si, leaves a 10 % target unchanged.
            x = exp["target_si"] / 100
            si_cup = COMP["6063"][0] / 100
            powder["Si"] = (x - si_cup) * al / (1 - x)
            if "AlSi10Mg" in exp["powder"]:
                free = cav - powder["Si"] / RHO["Si_tap"]
                a = free * RHO["AlSi10Mg_tap"]
                # re-solve with the AlSi10Mg in the charge (only matters if x != 10 %)
                si_a = COMP["AlSi10Mg"][0] / 100
                powder["Si"] = ((x - si_cup) * al + (x - si_a) * a) / (1 - x)
                powder["AlSi10Mg"] = a
    total = al + sum(powder.values())
    si = COMP["6063"][0] * al + sum(COMP[k][0] * m for k, m in powder.items())
    mg = COMP["6063"][1] * al + sum(COMP[k][1] * m for k, m in powder.items())
    return {
        "al_g": al,
        "powder_g": powder,
        "slug_g": total,
        "powder_frac": sum(powder.values()) / total,
        "si_wt": si / total,
        "mg_wt": mg / total,
    }


def pieces(exp: dict) -> dict[str, int]:
    per_slug = {"solid": {"solid_slug": 1}, "std": {"std_cup": 1, "std_plug": 1}, "thin": {"thin_cup": 1, "thin_plug": 1}}
    return {k: v * SLUGS_PER_RUN for k, v in per_slug[exp["cup"]].items()}


PIECE_LENGTH = {
    "solid_slug": SLUG_L,
    "std_cup": SLUG_L,
    "std_plug": PLUG_L,
    "thin_cup": THIN_L,
    "thin_plug": THIN_PLUG_L,
}


def annulus_area_mm2() -> float:
    return math.pi / 4 * (CRUCIBLE_ID**2 - SEALING_ROD_D**2)


def cavity_volume_crucible_cm3() -> float:
    """Straight bore plus floor cone, rod not subtracted: compare with the quoted 225 cm^3."""
    area = math.pi / 4 * CRUCIBLE_ID**2
    return (area * BORE_STRAIGHT + area * FLOOR_CONE_H / 3) / 1000


def melt_depth_mm(volume_cm3: float, dz: float = 0.01) -> float:
    """Height of a melt above the floor apex: it fills the floor cone round the rod's
    ball tip first, then the bore round the rod."""
    R, r = CRUCIBLE_ID / 2, SEALING_ROD_D / 2
    zc = rod_ball_z()
    half_angle = math.atan(R / FLOOR_CONE_H)
    z, vol = zc - r * math.sin(half_angle), 0.0  # start at the ring where the ball seals
    while vol < volume_cm3 * 1000:
        r_cav = R if z >= 0 else R * (z + FLOOR_CONE_H) / FLOOR_CONE_H
        r_rod = r if z >= zc else math.sqrt(max(r**2 - (z - zc) ** 2, 0.0))
        vol += math.pi * max(r_cav**2 - r_rod**2, 0.0) * dz
        z += dz
    return z + FLOOR_CONE_H


def head_mbar(depth_mm: float) -> float:
    return RHO["Al_liquid"] * 1000 * 9.80665 * depth_mm / 1000 / 100


# Liquid Al surface tension, N/m; the oxide skin, ignored here, only adds to it
GAMMA_AL = 0.87


def breakthrough_mbar(nozzle_d_mm: float) -> float:
    """Pressure to push liquid Al into a hole it doesn't wet: 2 gamma / r (Laplace)."""
    return 2 * GAMMA_AL / (nozzle_d_mm / 2 / 1000) / 100


def loading_margin(d: float, length: float, step: float = 0.1) -> dict:
    """Room (mm) for a round part to get past the rod adapter into the bore, the rod
    seated as documented.  Negative means it doesn't fit.

    Straight down, the part has to fit the band between the adapter and the bore
    wall.  Tipped in, its bottom rides against the rod and its top leans away from
    the adapter just enough to clear the adapter's lower end; at every depth until
    its top is below the adapter, it has to stay inside the bore at the rim.  The
    same model as repowder-reference/crucible_proportions.py.  It checks at the rim:
    if the filling cone's hole runs straight for a few mm above it, as drawn, the
    tipped-in figure is up to ~0.4 mm worse.
    """
    r_rod, r_bore, r_ad = SEALING_ROD_D / 2, CRUCIBLE_ID / 2, ROD_ADAPTER_D / 2
    h = ROD_ADAPTER_ABOVE_RIM
    worst = r_bore - r_rod - d  # a part shorter than h passes beside the adapter: just the gap
    if length > h:
        n = int((length - h) / step)
        for depth in [k * step for k in range(n + 1)] + [length - h]:
            tilt = (r_ad - r_rod) / (h + depth)  # tan of the least tilt that clears the adapter
            worst = min(worst, r_bore - (r_rod + d * math.hypot(1, tilt) + depth * tilt))
    return {"straight_down_mm": round(r_bore - r_ad - d, 2), "tipped_in_mm": round(worst, 2)}


def packing(n: int, d: float = STOCK_D, hot: bool = False, lean: str = "wall") -> float:
    """Gap (mm) between neighbouring slugs, n evenly spaced in the rod-to-wall gap.

    lean="wall" is the roomiest arrangement (all against the crucible wall),
    lean="rod" the tightest (all against the sealing rod).
    hot=True evaluates at ~600 C: Al grows ~1.45 %, graphite ~0.26 %.
    """
    grow = 1.0026 if hot else 1.0
    dd = d * (1.0145 if hot else 1.0)
    rc = CRUCIBLE_ID / 2 * grow - dd / 2 if lean == "wall" else SEALING_ROD_D / 2 * grow + dd / 2
    return 2 * rc * math.sin(math.pi / n) - dd


def summarise(parts: dict) -> tuple[dict, list]:
    part_info = {}
    for name, solid in parts.items():
        bb = solid.bounding_box()
        part_info[name] = {
            "volume_cm3": round(solid.volume / 1000, 3),
            "bbox_mm": [round(bb.size.X, 2), round(bb.size.Y, 2), round(bb.size.Z, 2)],
        }
    for name in ("solid_slug", "std_cup", "std_plug", "thin_cup", "thin_plug", "ring_cup", "ring_plug"):
        part_info[name]["mass_g_6063"] = round(parts[name].volume / 1000 * RHO["6063"], 2)
    part_info["support_sleeve"]["mass_g_steel"] = round(parts["support_sleeve"].volume / 1000 * RHO["steel"], 1)

    exps = []
    for e in EXPERIMENTS:
        c = charge(e, parts)
        run_g = c["slug_g"] * SLUGS_PER_RUN
        depth = melt_depth_mm(run_g / RHO["Al_liquid"])
        exps.append(
            {
                **{k: e[k] for k in ("id", "title", "tier", "cup")},
                "fixture": e.get("fixture"),
                "slugs_per_run": SLUGS_PER_RUN,
                "per_slug": {
                    "al_g": round(c["al_g"], 1),
                    "powder_g": {k: round(v, 2) for k, v in c["powder_g"].items()},
                    "total_g": round(c["slug_g"], 1),
                },
                "run_g": round(run_g, 1),
                "powder_frac_pct": round(100 * c["powder_frac"], 1),
                "si_wt_pct": round(c["si_wt"], 2),
                "mg_wt_pct": round(c["mg_wt"], 2),
                # over the pour hole, i.e. above the floor apex
                "melt_depth_mm": round(depth, 1),
                "head_mbar": round(head_mbar(depth), 1),
                "pieces": pieces(e),
            }
        )
    return part_info, exps


def bar_budget(exps: list, ids: list[str]) -> float:
    total = 0.0
    for e in exps:
        if e["id"] in ids:
            for piece, n in e["pieces"].items():
                total += n * (PIECE_LENGTH[piece] + CUT_ALLOWANCE)
    return total


# ---------------------------------------------------------------------------
# Press fit, from Lame's thick-walled-cylinder solution rather than asserted.
# Plug and cup are the same alloy, so E and nu cancel out of the ratio.
# ---------------------------------------------------------------------------
E_AL = 69000.0  # MPa
YIELD_6063_T52 = 110.0  # MPa, 16 ksi minimum per ASTM B221; ~145 MPa typical
MU_AL_AL = (1.05, 1.35)  # dry Al on Al, STATIC.  Edison's correction: 0.4 is the
# sliding value, and it is breakaway that sets the press you need to reserve.


def fit_check(bore: float, od: float, engage_l: float, interference_in: float) -> dict:
    """Interference fit of a solid plug in a cup: contact pressure, hoop stress, force."""
    r, b = bore / 2, od / 2
    k = (b**2 + r**2) / (b**2 - r**2)  # hoop-stress multiplier at the bore
    delta_r = interference_in * IN / 2
    # radial closure = hub growth + solid-plug compression = (p r / E)(k + nu) + (p r / E)(1 - nu)
    p = delta_r * E_AL / (r * (k + 1.0))
    area = math.pi * bore * engage_l
    # At the bore the stress state is (sigma_r, sigma_th, sigma_z) = (-p, p k, 0).
    # Yield is von Mises, not hoop alone - checking hoop against Sy understates it by
    # ~24 % here, which is Edison's correction and the reason the ceiling is .0008".
    vm = p * math.sqrt(k**2 + k + 1)
    return {
        "interference_in": interference_in,
        "contact_pressure_MPa": round(p, 1),
        "bore_hoop_stress_MPa": round(p * k, 1),
        "bore_von_mises_MPa": round(vm, 1),
        "frac_of_min_yield": round(vm / YIELD_6063_T52, 2),
        "press_force_t": [round(p * area * mu / 9806.65, 2) for mu in MU_AL_AL],
        "max_elastic_interference_in": round(
            interference_in * YIELD_6063_T52 / vm, 5
        ),
        # how far the cup OD grows before the bore yields - this is all the clearance
        # the E4 support sleeve is allowed, or it never takes any load
        "od_growth_at_yield_in": round(
            2 * (YIELD_6063_T52 / math.sqrt(k**2 + k + 1)) * r**2 * b
            / (E_AL * (b**2 - r**2)) * 2 / IN, 5
        ),
    }


def fits() -> dict:
    return {
        "std_cup_P2_P3": [fit_check(CUP_BORE_D, STOCK_D, PLUG_L, i) for i in (0.0005, 0.0008, 0.001, 0.002)],
        "thin_cup_P4_P5": [
            fit_check(THIN_BORE_D, STOCK_D, THIN_PLUG_L, i) for i in (0.0005, 0.001)
        ],
    }


def export(parts: dict) -> None:
    STEP_DIR.mkdir(exist_ok=True)
    STL_DIR.mkdir(exist_ok=True)
    machined = ["solid_slug", "std_cup", "std_plug", "thin_cup", "thin_plug", "support_sleeve", "ring_cup", "ring_plug"]
    for name in machined:
        export_step(parts[name], STEP_DIR / f"{name}.step")
        export_stl(parts[name], STL_DIR / f"{name}.stl", tolerance=0.01, angular_tolerance=0.1)

    # Context assembly: crucible + filling cone + sealing rod and holder + coil
    # + four standard cups with plugs + powder, standing on the floor cone
    cups = []
    for k in range(MAX_SLUGS):
        loc = Rot(0, 0, 90 * k) * Pos(SLUG_CIRCLE_R, 0, slug_base_z())
        cups += [
            loc * parts["std_cup"],
            loc * Pos(0, 0, SLUG_L - PLUG_L) * parts["std_plug"],
            loc * parts["std_powder"],
        ]
    context = [parts[k] for k in ("crucible", "filling_cone", "sealing_rod", "rod_holder", "coil")] + cups
    export_step(Compound(children=context), STEP_DIR / "crucible_context_4x_std_cup.step")
    # Same assembly cut through the axis, for GitHub's in-browser STL viewer
    front = Box(400, 200, 600, align=(Align.CENTER, Align.MAX, Align.CENTER))
    halves = [s - front for s in context]
    export_stl(Compound(halves), STL_DIR / "crucible_cutaway_4x_std_cup.stl", tolerance=0.1, angular_tolerance=0.35)


def main() -> None:
    parts = build()
    export(parts)
    part_info, exps = summarise(parts)

    budget = {
        "bar_on_hand_mm": round(BAR_ON_HAND, 1),
        "usable_mm": round(BAR_ON_HAND - CHUCK_REMNANT, 1),
        "E1-E3_mm": round(bar_budget(exps, ["E1", "E2", "E3"]), 1),
        "E4-E7_mm": round(bar_budget(exps, ["E4", "E5", "E6", "E7"]), 1),
        "one_spare_std_set_mm": round(SLUG_L + PLUG_L + 2 * CUT_ALLOWANCE, 1),
        # one slug per run instead of two: E1-E7 each get a single cup/slug
        "all_runs_one_slug_each_mm": round(bar_budget(exps, [e["id"] for e in exps]) / SLUGS_PER_RUN, 1),
    }
    geometry = {
        "crucible_bore_mm": CRUCIBLE_ID,
        "sealing_rod_mm": SEALING_ROD_D,
        "rod_to_wall_gap_mm": round((CRUCIBLE_ID - SEALING_ROD_D) / 2, 2),
        "floor_cone_deg": round(math.degrees(math.atan(FLOOR_CONE_H / (CRUCIBLE_ID / 2))), 1),
        "rim_to_floor_apex_mm": round(BORE_STRAIGHT + FLOOR_CONE_H, 1),
        "annulus_area_mm2": round(annulus_area_mm2(), 1),
        "annulus_volume_cm3": round(annulus_area_mm2() * BORE_STRAIGHT / 1000, 1),
        "cavity_volume_cm3_225ml_check": round(cavity_volume_crucible_cm3(), 1),
        "max_al_charge_g_to_rim": round(
            RHO["Al_liquid"] * (cavity_volume_crucible_cm3() - parts["sealing_rod"].volume / 1000), 0
        ),
        "slug_base_below_cone_top_mm": round(-slug_base_z(), 2),
        # the band beside the rod adapter, and how a part gets past it, rod seated
        "band_beside_rod_adapter_mm": round((CRUCIBLE_ID - ROD_ADAPTER_D) / 2, 2),
        "loading_margin_mm": {
            "P1_P2_3/4in_x_2.5in": loading_margin(STOCK_D, SLUG_L),
            "P1_P2_max_tol_bar_0.764in": loading_margin(0.764 * IN, SLUG_L),
            "P4_3/4in_x_1.25in": loading_margin(STOCK_D, THIN_L),
            "5/8in_x_2.5in": loading_margin(0.625 * IN, SLUG_L),
            "1/2in_x_2.5in": loading_margin(0.500 * IN, SLUG_L),
            "5N_20mm_x_2.5in": loading_margin(20.0, SLUG_L),
        },
        # Laplace pressure against the melt's head: the pour runs on over-pressure
        "breakthrough_mbar_by_nozzle_mm": {str(d): round(breakthrough_mbar(d), 1) for d in (0.5, 0.7, 1.0, 2.0)},
        "std_cavity_cm3": round(cavity_volume_cm3("std"), 3),
        "std_full_bore_cm3": round(full_bore_volume_cm3(), 3),
        "thin_cavity_cm3": round(cavity_volume_cm3("thin"), 3),
        "ring_powder_cm3": round(parts["ring_powder"].volume / 1000, 2),
        # same thin wall as E7 but standing the full 100 mm: what 4 slugs could hold
        "four_tall_thin_cups_powder_cm3": round(
            4 * math.pi / 4 * THIN_BORE_D**2 * (TALL_THIN_L - THIN_FLOOR - THIN_PLUG_L) / 1000, 1
        ),
        "std_cup_wall_mm": round((STOCK_D - CUP_BORE_D) / 2, 3),
        "thin_cup_wall_mm": round((STOCK_D - THIN_BORE_D) / 2, 3),
        "slug_clearance_to_rod_mm": round(SLUG_CIRCLE_R - STOCK_D / 2 - SEALING_ROD_D / 2, 2),
        "gap_between_slugs_mm": {
            f"{n}_{lean}_{state}": round(packing(n, hot=(state == "hot"), lean=lean), 2)
            for n in (4, 5, 6)
            for lean in ("wall", "rod")
            for state in ("cold", "hot")
        },
        "gap_5_slugs_max_tol_bar_cold_mm": round(packing(5, d=0.764 * IN), 2),
    }
    part_info["fits"] = fits()
    (HERE / "parts.json").write_text(json.dumps(part_info, indent=2) + "\n")
    (HERE / "experiments.json").write_text(
        json.dumps({"experiments": exps, "bar_budget": budget, "geometry": geometry}, indent=2) + "\n"
    )
    print(json.dumps(geometry, indent=2))
    print(json.dumps(fits(), indent=2))
    print(json.dumps(budget, indent=2))
    for e in exps:
        print(
            f'{e["id"]:3} {e["run_g"]:6.1f} g/run  per slug {e["per_slug"]}  '
            f'powder {e["powder_frac_pct"]:4.1f} %  Si {e["si_wt_pct"]:5.2f}  Mg {e["mg_wt_pct"]:4.2f}  '
            f'melt {e["melt_depth_mm"]} mm = {e["head_mbar"]} mbar'
        )


if __name__ == "__main__":
    main()
