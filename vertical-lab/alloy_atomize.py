"""Chapter 2 of the alloy route, atomize: the MiR250 brings the four charged 5N Al cups from the VLM to the rePowder,
the UR10e undoes the lid's draw latch, opens the lid, and sets the cups on the crucible's floor round the sealing rod
with a loading tong; the machine melts and atomizes them; the arm takes the powder container off onto the MiR (#303,
rounds 4 to 6). Clips and photos of the lab's own runs are cut in where the animation reaches the same moment: the
charge melting (at 2x), the stream on the plate, the powder as it comes out, not yet sieved (round 8: the sieved jars
are chapter 3's, after its sieving). Round 6 also sums the MiR's tipping
and sliding for the pull on the latch (``stability``), the tong's clearances down the bore (``tong_clearance``), and
stops on the crucible stack, the part that is hardest to automate (notes/crucible_automation.md).

    xvfb-run -a python3 alloy_atomize.py            # render, then splice -> out/alloy_atomize.gif, out/mp4/alloy_atomize.mp4,
                                                    #   .json, _still.png
    python3 alloy_atomize.py splice                 # only cut the real footage into the last render (seconds)
    python3 alloy_atomize.py powder                 # the powder sums -> out/alloy_atomize_powder.json
    PREVIEW=1 xvfb-run -a python3 alloy_atomize.py  # the last frame of each sub-step -> /tmp/preview_alloy_atomize.png

The render and the footage are kept apart. The render writes the 3-D chapter, with a marker wherever footage goes, to
``out/clean/`` (git-ignored): ``alloy_atomize_3d.mp4``, its GIF frames and its JSON. ``splice`` then reads the clips
and photos listed in ``FOOTAGE/manifest.json`` (default ``/tmp/footage``), fits each one to the frame, draws the same
title, step label and caption on it, and writes the final MP4, GIF and JSON with the footage in. So new or better
footage needs no re-render.

Hand-offs: it starts where chapter 1 (the VLM charge) ends, the MiR250 at the VLM's opening (``animate.AMR_XY``) with
the four Al cups in ``charge.carrier()``'s four pockets on its cabinet, and it ends with the MiR parked in front of
the rePowder holding the powder container in a cradle, the arm parked, where chapter 3 (sieve and print) picks up.

The scene is setup_lab.py's two-Shuttle floor (round 8, ``alloy_atomize_floor.py``: the second Shuttle at x = 3630, the
Aconity at 6950, the glovebox at -7300), except that the
rePowder is loaded part by part from ``repowder/model.py`` (the merged copy ``animate.Lab`` adds is hidden), so its lid,
sealing rod, crucible and container can move and its furnace and chamber can be cut open at the furnace axis.

The melt, the stream, the vibrating plate, the droplets and the powder are ported, credited, from the rePowder
training animations (#124, ``atomizer-training/viz3d/steps.py`` on ``claude/issue-124-20261003-0335``: ``Pool``,
``Powder``, ``Particles``, ``stream``, ``film``, ``shake``, ``heat``, ``gas_meshes``) and its ``load_machine`` /
``set_cut``. The process numbers are #222's (``atomizer-charge/README.md`` on ``claude/issue-222-20260925-0343``),
see notes/alloy_atomize.md.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from scipy.spatial.transform import Rotation, Slerp

import scene
scene.GIF_FPS = 5                     # a ~90 s GIF under 4.9 MB: 5 fps at 640 x 360 (the MP4 keeps every frame)
scene.GIF_SIZE = (640, 360)
from scene import AUDIT, FPS, OUT, PREVIEW, Scene, T, R, S, ease, mix, window  # noqa: E402
_OVERLAY = Scene.overlay              # scene's own: instruments_char and instruments_lab patch Scene.overlay later

import alloy_atomize_floor as FL     # noqa: E402
import animate as A                   # noqa: E402
import charge as C                    # noqa: E402
import lab                            # noqa: E402
import line                           # noqa: E402
import props as P                     # noqa: E402
import robot as RB                    # noqa: E402
import tour                           # noqa: E402

HERE = Path(__file__).resolve().parent
NAME = "alloy_atomize"
DEBUG = bool(__import__("os").environ.get("ATOMIZE_DEBUG"))
TAIL = int(__import__("os").environ.get("ATOMIZE_TAIL", "0"))
# ATOMIZE_PART=a:b draws only sub-steps a..b-1 (every frame is still counted), into out/clean/*_part<a>*; run the parts
# side by side, then `python3 alloy_atomize.py merge` joins them and splices the footage in
PART = tuple(int(x) for x in __import__("os").environ["ATOMIZE_PART"].split(":")) \
    if __import__("os").environ.get("ATOMIZE_PART") else None
TITLE = "Vertical cloud lab: the charge cups into the atomizer"

_spec = importlib.util.spec_from_file_location("repowder_model", HERE / "repowder" / "model.py")
M = importlib.util.module_from_spec(_spec)
sys.modules["repowder_model"] = M     # its dataclasses look themselves up there
_spec.loader.exec_module(M)

RP = np.array(A.REPOWDER_AT, float)   # the rePowder model's origin (the furnace axis on the floor) in the world
RUN = json.loads((OUT / "alloy_recipe.json").read_text())["runs"]["Al-10Si"] if (OUT / "alloy_recipe.json").exists() \
    else C.recipe()["runs"]["Al-10Si"]

# ------------------------------------------------------------------------------------------------ the #124 port
FURNACE_CUT = ("crucible", "holder", "nozzle", "furnace", "side_ins", "top_ins", "bottom_ins", "coil", "hood", "tc")
CHAMBER_CUT = ("chamber", "door", "bowl", "splash", "container", "flange_clamp", "flange_clamp_b")
MELT = (1.0, 0.45, 0.10)
ARGON = (0.45, 0.72, 1.0)
PER_FRAME = 15 / FPS
# Four cups a run (byu-vcl PR #318: "we load multiple charges into the crucible (4)"), at #222's four places round the
# rod: the model's SLUG_ANGLES, 75 deg apart and clear of the sealing-rod lever, which lies over the crucible along +x.
# Loaded back pair first. The two at the back (y > 0) stay in the cutaway and are drawn cut through their own axes (a
# stepped section), so it shows their powder, plug and vent; the two at the front go with the half that is cut away.
CUP_ANGLES = (145.0, 70.0, 220.0, 295.0)
N_CUPS = len(CUP_ANGLES)
CUP_R = (M.SEALING_ROD_D / 2 + M.CRUCIBLE_ID / 2) / 2      # #222 SLUG_CIRCLE_R: halfway between the rod and the wall
CUP_GAP = 2 * CUP_R * math.sin(math.radians(75.0 / 2)) - C.STOCK_D      # between neighbours: 2.17 mm
RADIAL_ROOM = M.CRUCIBLE_ID / 2 - M.SEALING_ROD_D / 2 - C.STOCK_D        # rod to wall, less a cup: 3.20 mm
GRIP_CUP = 0.80                       # 2F-85 closure for the 19.05 mm cup (ur_arm.gripper_fk: 0.78 -> 21 mm)
GRIP_LET_GO = 0.70                    # let go of a cup by opening only this far (the pads 4.5 mm off it): wider, the
                                      # fingers swing out into the filling cone
GRIP_AT = 8.0                         # the pads' centre this far under the cup's top (round 5: 13), so the fingertips
                                      # stay 5 mm higher; they still overlap 27 mm of the cup
TIP_DEG = 4.1                         # #222's best tilt past the rod's adapter: foot by the rod, top leaning out
GRIP_KNOB = 0.70                      # the lid's knob, a 28 mm ball (model.py hood_knob): the pads on it
GRIP_HANDLE = 0.86                    # the container's 12 mm handle bar
GRIP_LEVER = 0.875                    # the sealing-rod lever's 12 mm bar
LEVER_AT = 40.0                       # where the arm takes the lever: mm along it from the rod
HOOD_OPEN = 110.0                     # degrees the lid swings up (#124's training animation)
MIR_SPEED = 1500.0                    # mm/s at most, at 0.3 m/s^2 (props.ramp_secs), as PR #321
PARK = np.radians(A.PARK_DEG)
CARRIER_AT = (A.BUFFER_LOCAL[0], A.BUFFER_LOCAL[1], P.AMR_TOP - 20.0)    # where chapter 1 puts the cup carrier
CRADLE_AT = (280.0, 10.0, P.AMR_TOP - 20.0)                           # the container's cradle, beside the arm
CRADLE_TURN = float(os.environ.get("CRADLE_TURN", "0"))   # the container's turn in the cradle (round 7: 180, handle
                                      # to the arm; round 8: 0, handle to the front, as chapter 3 takes it)
CRADLE_H = 12.0                       # a low ring on the cabinet top (was a ring on a 150 mm post: the upper arm
                                      # crossed it on two joint moves, PR #318 round 5)
END_POSE = (A.REPOWDER_AT[0] + 288.0, -2230.0)     # the hand-off to chapter 3 (sieve, print): MiR250 centre, yaw 0,
                                                   # square to the container's axis, 41 mm off the view port's flange
# Round 9 (Sterling, PR #318, 2026-11-05 22:56: "You're probably going to need both mobile robots (i.e., both arms) to
# be able to do the chamber opening and such on the atomizer"): the second MiR250 + UR10e waits in the aisle west of
# the rePowder and comes in for the lid. It stands left of the first (100 mm between their bodies), 200 mm nearer the
# machine: its arm holds the lid down while the first arm works the latch, and swings the lid open and shut.
B_HOME = (A.REPOWDER_AT[0] - 1500.0, -2450.0)       # in the aisle, west of the first's spot
B_AT = (A.REPOWDER_AT[0] - 760.0, -2190.0)       # its body 60 mm off the chamber's front, 100 mm off the first's
LITE = bool(os.environ.get("ATOMIZE_LITE"))       # development only: the rePowder and the MiRs, no lab floor

RAW = OUT / "clean"                                # git-ignored: the 3-D render before the footage goes in
RAW_MP4, RAW_JSON, RAW_GIF = RAW / f"{NAME}_3d.mp4", RAW / f"{NAME}_3d.json", RAW / f"{NAME}_3d_gif"


def part_paths(a: int):
    return RAW / f"{NAME}_3d_part{a:03d}.mp4", RAW / f"{NAME}_3d_part{a:03d}.json", RAW / f"{NAME}_3d_part{a:03d}_gif"
FOOTAGE = Path(os.environ.get("FOOTAGE", "/tmp/footage"))


# ------------------------------------------------------------------------------------------------ how much powder
AL_LIQUID = 2.37         # g/cm3: liquid Al near 700-750 C; taken for Al-10Si too (assumed)
AL_SOLID = 2.70          # g/cm3: 5N Al and 6063
NAB_SOLID = 7.58         # g/cm3: C63000, 0.274 lb/in3 (National Bronze's C63000 sheet, the one DAL #219 links)
POWDER_BULK = 1.40       # g/cm3: loose Al-Si powder in the container (assumed; #222's AlSi10Mg tapped by hand is 1.60)
BED_BULK = 1.50          # g/cm3: powder in the MIDI's bed, as notes/alloy_print.md
# The lab's best run so far, k7m2q9: 630 bronze on Oct 27 2026 (DAL #219, PR #230). Gage sieved both bronze runs
# together and put 97 % of the usable powder down to the first (#219, comments 6509252104 and 6509485831).
K7M2Q9 = dict(charge_g=1079.886, pieces=4, fines_g=187.973, mid_g=827.063, run1_share=0.97,
              source="DAL #219 (Gage, Oct 27-29 2026): 1,079.886 g in 4 rod pieces; both runs sieved: <63 um "
                     "187.973 g, 64-250 um 827.063 g, >251 um 181.903 g, left in the crucible 732.034 g; 97 % of "
                     "the usable powder from the first run")
MIDI_BUILDS = {"the lab's planning figure": (440.0, "powder-doser design/brainstorming.md, section 3: \"Aconity MIDI "
                                                    "~440 g/build\", from Sterling's PR-thread comment"),
               "a 30 mm build in the full 170 mm cylinder": (math.pi / 4 * 170.0 ** 2 * 30.0 / 1000.0 * BED_BULK,
                                                             "notes/alloy_print.md: pi/4 x 170^2 x 30 mm at 1.5 g/cm3")}
CRUCIBLES = {"225 cm3": 225.0, "400 cm3": 400.0}   # DAL #219 comment 6475748437 (the ONR YIP plan); the model: 225.2


def _pappus(pts) -> float:
    """cm3 of a closed (r, z) profile, mm, turned about z."""
    p = np.array(list(pts) + [pts[0]], float)
    r, z = p[:, 0], p[:, 1]
    a = r[:-1] * z[1:] - r[1:] * z[:-1]
    area = a.sum() / 2
    return float(abs(2 * math.pi * area * ((r[:-1] + r[1:]) * a).sum() / (6 * area)) / 1000.0)


def pool_volume(level: float) -> float:
    """cm3 of the drawn melt (model.pool_solid's profile) standing `level` mm above Z_CR."""
    rr = M.SEALING_ROD_D / 2 + 0.4
    level = max(level, M.floor_z(rr) + 0.5)
    if level >= 0:
        pts = [(rr, M.floor_z(rr)), (M.CRUCIBLE_ID / 2 - 0.3, -0.3), (M.CRUCIBLE_ID / 2 - 0.3, level), (rr, level)]
    else:
        pts = [(rr, M.floor_z(rr)), (M.CRUCIBLE_ID / 2 * (1 + level / M.FLOOR_CONE_H) - 0.3, level), (rr, level)]
    return _pappus(pts)


def powder_volume(level: float) -> float:
    """cm3 of the drawn heap (model.powder_solid's profile), `level` mm deep at the container's wall."""
    level, r = max(level, 2.0), M.CONT_R - 5
    pts = [(0, 4), (r - 14, 4), (r, 18), (r, level), (0, level + min(18.0, level * 0.3))]
    if level < 18:
        pts = [(0, 4), (r - 14, 4), (r - 14 + level * 0.7, level), (0, level + 3)]
    return _pappus(pts)


def level_for(volume_fn, cm3: float, lo: float, hi: float) -> float:
    for lv in np.linspace(lo, hi, int((hi - lo) * 10) + 1):
        if volume_fn(lv) >= cm3:
            return float(lv)
    return hi


def powder_sums() -> dict:
    """Powder per run for four cups, a full 225 cm3 crucible and the 400 cm3 one, at k7m2q9's yields, and runs per
    MIDI build. Written to out/alloy_atomize_powder.json."""
    k = K7M2Q9
    usable = (k["fines_g"] + k["mid_g"]) * k["run1_share"] / k["charge_g"]
    fines = k["fines_g"] * k["run1_share"] / k["charge_g"]
    metal_cm3 = k["charge_g"] / NAB_SOLID
    fill = metal_cm3 / CRUCIBLES["225 cm3"]
    charges = {"4 cups (this chapter)": (RUN["charge_g"], "out/alloy_recipe.json: 4 x 5N Al cup + plug + 3.92 g Si"),
               "225 cm3 crucible, filled as on Oct 27": (metal_cm3 * AL_SOLID,
                                                          f"{metal_cm3:.1f} cm3 of metal ({100 * fill:.0f} % of 225 "
                                                          f"cm3), the volume of k7m2q9's bronze, in Al at 2.70"),
               "400 cm3 crucible, the same fill": (fill * CRUCIBLES["400 cm3"] * AL_SOLID,
                                                   f"{100 * fill:.0f} % of 400 cm3 in Al at 2.70 (assumed: the "
                                                   f"same fill as Oct 27)")}
    rows = []
    for name, (g_in, how) in charges.items():
        row = dict(charge=name, al_g=round(g_in, 1), how=how, usable_g=round(g_in * usable, 1),
                   under_63um_g=round(g_in * fines, 1))
        row["runs_per_build"] = {b: math.ceil(m / (g_in * fines)) for b, (m, _) in MIDI_BUILDS.items()}
        rows.append(row)
    bed_440 = MIDI_BUILDS["the lab's planning figure"][0] / BED_BULK * 1000.0 / (math.pi / 4 * 170.0 ** 2)
    return dict(
        yields=dict(usable_under_250um=round(usable, 4), under_63um=round(fines, 4), source=k["source"]),
        charges=rows,
        midi_builds={b: dict(g=round(m), source=s) for b, (m, s) in MIDI_BUILDS.items()},
        reconcile=f"440 g of bed powder at {BED_BULK} g/cm3 is {440 / BED_BULK:.0f} cm3: a {bed_440:.1f} mm layer "
                  "of the 170 mm cylinder, i.e. a short build (or a smaller cylinder), where chapter 3's 30 mm build "
                  "in the full cylinder takes about 1 kg. Both are the bed alone; the supply's excess is on top.",
        caveats=["k7m2q9 is 630 bronze. Al atomizes coarser at the same 40 kHz (the capillary wavelength goes as "
                 "(surface tension / density)^(1/3), about 1.3x for Al against Cu alloys), so its share under 63 um "
                 "is an upper estimate for Al. The lab's Al 4047 powders looked coarse under the SEM (DAL #159).",
                 "The 63-250 um and >250 um powder can be remelted in a later run (more oxygen each time), so little "
                 "metal is lost; it doesn't cut the number of runs, since each run still makes the same share of "
                 "fines.",
                 "A cup charge is limited by the cups, not the crucible: four 2.5 in cups hold 59 cm3 of metal, a quarter of the 225. "
                 "The Oct 27 rod pieces were about 125 mm long (270 g each of 3/4 in rod), so cups that long would "
                 "about double the charge."],
        model=dict(pool_level_mm=round(POOL_LEVEL, 1), powder_level_mm=round(POWDER_END, 1),
                   melt_density=AL_LIQUID, powder_bulk=POWDER_BULK, cup_gap_mm=round(CUP_GAP, 2),
                   rod_to_wall_less_cup_mm=round(RADIAL_ROOM, 2)))


POOL_LEVEL = level_for(pool_volume, RUN["charge_g"] / AL_LIQUID, -14.0, 37.0)     # 21.6 mm for 156.7 g
POWDER_END = level_for(powder_volume, RUN["charge_g"] * 0.912 / POWDER_BULK, 3.0, 70.0)   # 15 mm: 143 g


def lighter(c, k=0.45):
    return tuple(x + (1 - x) * k for x in c)


def temp_color(t: float, cold=C.AL_5N) -> tuple:
    """#124 scene.temp_color: grey below ~450 C, then dull red, orange, yellow-orange."""
    stops = [(20, cold), (450, cold), (560, (0.45, 0.16, 0.12)), (680, (0.78, 0.18, 0.06)),
             (800, (1.00, 0.42, 0.08)), (1000, (1.00, 0.68, 0.25))]
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            return mix(c0, c1, (max(t, t0) - t0) / (t1 - t0))
    return stops[-1][1]


def g(name: str) -> str:
    """The scene group of a rePowder part group."""
    return f"rp:{name}"


def load_rp(sc: Scene, ghost: dict | None = None) -> dict:
    """#124's load_machine(defer=True), every group prefixed rp: and riding on "rp", the model placed at RP. Parts
    whose group is in FURNACE_CUT or CHAMBER_CUT are added whole and halved at y = 0; set_cut() blends them."""
    ms = M.meshes()
    ghost = ghost or {}
    cut = FURNACE_CUT + CHAMBER_CUT
    for name, m in ms.items():
        if name == "floor":
            continue
        grp = g("knob") if name == "hood_knob" else g(m["group"])    # its own group, so a grasp of it is just that
        wants = m["group"] in cut
        if wants and m.get("gone"):
            sc.add("w:" + name, m["whole"], m["color"], grp, opacity=m["opacity"])
            sc.cutrole["w:" + name] = "whole"
            sc.cut_f[grp] = 0.0
            continue
        op = ghost.get(name, m["opacity"])
        if wants and m["half"] is not None:
            sc.add(name, m["half"], m["color"], grp, opacity=op)
            if m["half_cut"] is not None:
                sc.add(name + "#cut", m["half_cut"], lighter(m["color"]), grp, opacity=op, smooth_shading=False,
                       ambient=0.55, diffuse=0.5, specular=0.0)
            sc.add("w:" + name, m["whole"], m["color"], grp, opacity=m["opacity"])
            sc.cutrole.update({name: "half", name + "#cut": "half", "w:" + name: "whole"})
            sc.cut_f[grp] = 0.0
        elif name in ghost:
            sc.add(name, m["whole"], m["color"], grp, opacity=1.0)
            sc.ghost_of[name] = op
            sc.cut_f.setdefault(grp, 0.0)
        else:
            sc.add(name, m["whole"], m["color"], grp, opacity=op)
    for name, p in M.pipe_routes().items():
        sc.add("rp pipe " + name, pv.Spline(np.array(p["pts"], float), 120).tube(radius=p["r"], n_sides=14),
               p["color"], g("pipes"))
    for a in ("connector", "sonotrode", "booster", "transducer"):
        sc.parent[g(a)] = g("stack")
    sc.parent[g("stack")] = g("door")
    sc.parent[g("cover")] = g("door")
    sc.parent[g("plate")] = g("connector")
    sc.parent[g("upper")] = g("connector")
    sc.parent[g("arm")] = g("arm_base")
    sc.parent[g("rod")] = g("arm_base")
    sc.parent[g("nozzle")] = g("crucible")
    sc.parent[g("holder")] = g("crucible")
    sc.parent[g("splash")] = g("container")
    sc.parent[g("knob")] = g("hood")
    for grp in set(sc.group_of.values()):
        if grp.startswith("rp:") and grp not in sc.parent:
            sc.parent[grp] = "rp"
    sc.gmat["rp"] = T(RP)
    return ms


def set_cut(sc: Scene, f: float, groups=None):
    for k in list(sc.cut_f):
        if groups is None or k in groups:
            sc.cut_f[k] = f


FUR_G = [g(x) for x in FURNACE_CUT]
CH_G = [g(x) for x in CHAMBER_CUT]


class Pool:
    """The melt in the crucible (#124 steps.Pool), from model.variant_meshes() at a series of levels, cut open."""

    def __init__(self, sc, level=-30):
        self.sc = sc
        v = M.variant_meshes()
        self.levels = v["pool_levels"]
        self.meshes = v["pool_half"]
        body, cut = self.meshes[0]
        sc.add("pool", body, MELT, g("crucible"), ambient=0.75, diffuse=0.45, specular=0.5)
        sc.add("pool#cut", cut, lighter(MELT, 0.3), g("crucible"), ambient=0.85, diffuse=0.3, specular=0.0,
               smooth_shading=False)
        self.set(level)

    def set(self, level, color=MELT):
        on = level > self.levels[0] - 0.5
        i = int(np.argmin(np.abs(self.levels - level)))
        body, cut = self.meshes[i]
        self.sc.set_mesh("pool", body)
        self.sc.set_mesh("pool#cut", cut)
        for n, c in (("pool", color), ("pool#cut", lighter(color, 0.3))):
            self.sc.alpha[n] = 1.0 if on else 0.0
            self.sc.color[n] = c


class Powder:
    """The powder heap in the container (#124 steps.Powder), cut open; it rides with the container."""

    def __init__(self, sc, level=0):
        self.sc = sc
        v = M.variant_meshes()
        self.levels = v["powder_levels"]
        self.meshes = v["powder_half"]
        col = C.POWDERS["Al"][0]
        sc.add("powder", self.meshes[0][0], col, g("container"), specular=0.05, ambient=0.3)
        sc.add("powder#cut", self.meshes[0][1], lighter(col, 0.25), g("container"), smooth_shading=False, ambient=0.6,
               specular=0.0)
        self.set(level)

    def set(self, level):
        on = level >= self.levels[0]
        i = int(np.argmin(np.abs(self.levels - level)))
        body, cut = self.meshes[i]
        self.sc.set_mesh("powder", body)
        self.sc.set_mesh("powder#cut", cut)
        self.sc.alpha["powder"] = self.sc.alpha["powder#cut"] = 1.0 if on else 0.0


STREAM_TOP = M.NOZZLE_EXIT_Z


def add_stream(sc, radius=1.4):
    h = STREAM_TOP - M.IMPACT[2]
    cyl = pv.Cylinder(center=(0, 0, M.IMPACT[2] + h / 2), direction=(0, 0, 1), radius=radius, height=h, resolution=16)
    sc.add("stream", cyl, MELT, g("stream"), ambient=0.85, diffuse=0.4, shown=False)
    disc = pv.Cylinder(center=tuple(M.IMPACT + M.STACK_DIR * 0.4), direction=tuple(M.STACK_DIR), radius=7.0,
                       height=0.8, resolution=32)
    sc.add("film", disc, MELT, g("film"), ambient=0.85, diffuse=0.4, shown=False)
    sc.parent[g("film")] = g("plate")
    sc.parent[g("stream")] = "rp"


def stream(sc, on, thick=1.0, frac=1.0):
    sc.alpha["stream"] = 1.0 if on > 0.02 else 0.0
    sc.gmat[g("stream")] = S((thick, thick, max(frac, 0.01)), (0, 0, STREAM_TOP))


def film(sc, on):
    sc.alpha["film"] = 1.0 if on else 0.0


def shake(sc, on):
    """The plate's vibration, exaggerated (1.2 mm along the axis, every other frame at 15 fps) so it shows."""
    sc.gmat[g("connector")] = T(M.STACK_DIR * (1.2 if (on and (sc.n * 15 // FPS) % 2) else 0.0))


FLYING, SLIDING, DROPPING = 0, 1, 2
DROP_R = 9.0
SLIDE_V, DROP_V = 900.0, 1200.0
CHUTE_C = np.array([M.CHUTE_X, 0.0])
OUTLET_R = 52.0 - DROP_R - 6.0
UPPER_BASE = M.TIP + M.STACK_DIR * M.PLATE_T


def floor_at(x):
    return np.maximum(M.CH_BOTTOM + DROP_R, M.SLOPE_C + DROP_R * math.sqrt(2) - np.asarray(x, float))


def chute_r(z):
    return np.interp(z, [M.CONT_Z[1] - 40, 340.0, 410.0, M.CH_BOTTOM + 20], [30.0, 30.0, 44.0, 44.0])


class Particles:
    """Droplets and powder as points drawn as spheres: #124's tiny ballistic model in slow motion, in the model's
    frame (the actor rides on "rp"). free=True: no chamber walls, just fall (the vent bubbles here)."""

    def __init__(self, sc, name, color, size=6.0, slowmo=0.22, seed=1, free=False, gravity=1.0):
        self.sc, self.name, self.slowmo, self.free, self.gravity = sc, name, slowmo, free, gravity
        self.rng = np.random.default_rng(seed)
        self.p = np.zeros((0, 3))
        self.v = np.zeros((0, 3))
        self.s = np.zeros(0, int)
        self.landed = 0
        sc.add(name, pv.PolyData(np.array([[0.0, 0.0, -500.0]])), color, g("fx"), render_points_as_spheres=True,
               point_size=size, ambient=0.4, smooth_shading=False)
        sc.parent[g("fx")] = "rp"
        sc.alpha[name] = 0.0

    def emit_spray(self, n, spread=1.0):
        if n <= 0:
            return
        r = self.rng
        sp = r.uniform(600, 1900, n) * spread
        d = (M.STACK_DIR[None, :] * r.uniform(0.35, 1.0, n)[:, None]
             + M.PLATE_UP[None, :] * r.uniform(-0.55, 0.9, n)[:, None]
             + np.array([0, 1.0, 0])[None, :] * r.uniform(0.05, 1.0, n)[:, None])
        d /= np.linalg.norm(d, axis=1)[:, None]
        p = M.IMPACT[None, :] + r.normal(0, 2.5, (n, 3))
        p[:, 1] = np.abs(p[:, 1]) + 1.0
        self.add(p, d * sp[:, None])

    def emit_drops(self, n, pos, vel):
        if n > 0:
            self.add(np.repeat(np.asarray(pos, float)[None, :], n, 0),
                     np.asarray(vel, float)[None, :] + self.rng.normal(0, 60, (n, 3)))

    def add(self, p, v, state=0):
        self.p = np.vstack([self.p, p])
        self.v = np.vstack([self.v, v])
        self.s = np.concatenate([self.s, np.full(len(p), state, int)])

    def clear(self):
        self.p, self.v, self.s = self.p[:0], self.v[:0], self.s[:0]
        self.step()

    def step(self, dt=None):
        if len(self.p):
            h = (dt or 1 / FPS) * self.slowmo
            self.v[:, 2] -= 9810 * h * self.gravity
            self.v *= (1 - 1.8 * h)
            self.p += self.v * h
            if self.free:
                keep = (self.p[:, 2] > 300) & (self.p[:, 2] < M.RIM + 38)
                self.p, self.v, self.s = self.p[keep], self.v[keep], self.s[keep]
            else:
                self._walls(h)
        pts = self.p if len(self.p) else np.array([[0.0, 0.0, -500.0]])
        self.sc.set_mesh(self.name, pv.PolyData(pts.copy()))
        self.sc.alpha[self.name] = 1.0 if len(self.p) else 0.0

    def _walls(self, h):
        p, v = self.p, self.v
        fly = self.s == FLYING
        x0, xc, rr = M.CH_X[0] + DROP_R, M.CH_X[1], M.CH_Y[1] - DROP_R
        for ax, lo, hi in ((0, x0, None), (1, 1.0, rr), (2, None, M.CH_TOP - DROP_R)):
            if lo is not None:
                hit = fly & (p[:, ax] < lo)
                p[hit, ax] = lo
                v[hit, ax] = np.abs(v[hit, ax]) * 0.15
            if hi is not None:
                hit = fly & (p[:, ax] > hi)
                p[hit, ax] = hi
                v[hit, ax] = -np.abs(v[hit, ax]) * 0.15
        dx = p[:, 0] - xc
        d = np.hypot(dx, p[:, 1]) + 1e-9
        hit = fly & (dx > 0) & (d > rr)
        if hit.any():
            n = np.column_stack([dx[hit] / d[hit], p[hit, 1] / d[hit]])
            p[hit, 0], p[hit, 1] = xc + n[:, 0] * rr, n[:, 1] * rr
            vn = (v[hit, :2] * n).sum(1)
            v[hit, :2] -= (1.15 * np.maximum(vn, 0.0))[:, None] * n
        q = p - UPPER_BASE
        t = q @ M.STACK_DIR
        rv = q - t[:, None] * M.STACK_DIR
        rad = np.linalg.norm(rv, axis=1) + 1e-9
        hit = fly & (t > -DROP_R) & (t < M.UPPER_L + DROP_R) & (rad < M.UPPER_R + DROP_R)
        if hit.any():
            n = rv[hit] / rad[hit, None]
            p[hit] = UPPER_BASE + t[hit, None] * M.STACK_DIR + n * (M.UPPER_R + DROP_R)
            vn = (v[hit] * n).sum(1)
            v[hit] -= (1.15 * np.minimum(vn, 0.0))[:, None] * n
        land = fly & (p[:, 2] <= floor_at(p[:, 0]))
        self.s[land] = SLIDING
        slide = self.s == SLIDING
        if slide.any():
            ps = p[slide]
            on_slope = ps[:, 0] < xc
            to = np.column_stack([CHUTE_C[0] - ps[:, 0], CHUTE_C[1] - ps[:, 1]])
            dist = np.linalg.norm(to, axis=1) + 1e-9
            vel = np.zeros_like(ps)
            vel[on_slope] = np.array([1.0, 0.0, 0.0]) * SLIDE_V
            vel[~on_slope, :2] = to[~on_slope] / dist[~on_slope, None] * SLIDE_V
            ps += vel * h
            ps[:, 2] = floor_at(ps[:, 0])
            v[slide] = 0.0
            p[slide] = ps
            at_outlet = np.hypot(ps[:, 0] - CHUTE_C[0], ps[:, 1] - CHUTE_C[1]) < OUTLET_R
            self.s[np.flatnonzero(slide)[at_outlet]] = DROPPING
        drop = self.s == DROPPING
        if drop.any():
            pd = p[drop]
            pd[:, 2] -= DROP_V * h
            off = pd[:, :2] - CHUTE_C[None, :]
            r = np.linalg.norm(off, axis=1) + 1e-9
            k = np.minimum(1.0, chute_r(pd[:, 2]) / r)
            pd[:, :2] = CHUTE_C[None, :] + off * k[:, None]
            p[drop] = pd
            v[drop] = 0.0
        gone = p[:, 2] < M.CONT_Z[1] - 20
        self.landed += int(gone.sum())
        self.p, self.v, self.s = p[~gone], v[~gone], self.s[~gone]


def add_gas(sc):
    """#124 gas_meshes(half=True): argon in the furnace and in the chamber, as a faint blue."""
    fur = pv.Cylinder(center=(0, 0, 1251), direction=(0, 0, 1), radius=128, height=186, resolution=72).merge(
        pv.Cylinder(center=(0, 0, 1412), direction=(0, 0, 1), radius=112, height=130, resolution=6))
    ch = M.tess(M.chamber_solid(M.CH_WALL + 1.0), 1.0).triangulate()
    ch = ch.merge(pv.Cylinder(center=(M.CHUTE_X, 0, (M.CONT_Z[0] + M.CH_BOTTOM) / 2), direction=(0, 0, 1),
                              radius=M.CONT_R - 6, height=M.CH_BOTTOM - M.CONT_Z[0] - 8, resolution=48).triangulate())
    fur = fur.clip(normal=(0, -1, 0), origin=(0, 0.5, 0))
    ch = ch.clip(normal=(0, -1, 0), origin=(0, 0.5, 0))
    sc.add("gas furnace", fur, ARGON, g("gas"), opacity=0.30, smooth_shading=False, specular=0.0, ambient=0.6)
    sc.add("gas chamber", ch, ARGON, g("gas"), opacity=0.22, smooth_shading=False, specular=0.0, ambient=0.6)
    sc.parent[g("gas")] = "rp"
    sc.alpha["gas furnace"] = sc.alpha["gas chamber"] = 0.0


def set_gas(sc, a):
    sc.alpha["gas furnace"] = sc.alpha["gas chamber"] = a


def hood(sc, deg):
    sc.gmat[g("hood")] = R((0, 1, 0), -deg, M.HINGE)


def rod_lift(sc, mm):
    sc.gmat[g("arm_base")] = T((0, 0, mm))


def flange_clamp(sc, f):
    """f = 1 closed round the joint, 0 open: the two halves 40 mm apart, front and back (#124)."""
    sc.gmat[g("flange_clamp")] = T((0, -40 * (1 - f), 0))
    sc.gmat[g("flange_clamp_b")] = T((0, 40 * (1 - f), 0))


def coil_glow(sc, on):
    for n in ("coil", "coil#cut", "w:coil"):
        if n in sc.actors:
            sc.color[n] = mix(M.COPPER, (1.0, 0.62, 0.30), on)
            sc.ambient[n] = 0.18 + 0.45 * on


# ------------------------------------------------------------------------------------------------ the MiR
class Mir:
    """A MiR250 with its cabinet and a UR10e (alloy_workflow.Mir), driving on (x, y, yaw). The first (group "amr",
    arm "ur") carries chapter 1's cup carrier and a cradle for the powder container; round 9's second unit (group
    "amrB", arm "urB", ``cargo=False``) comes for the lid. Both stand on a ballast plate (``BALLAST``)."""

    def __init__(self, sc, g: str = "amr", prefix: str = "ur", cargo: bool = True):
        self.sc, self.g, self.cargo = sc, g, cargo
        for name, (mesh, col) in P.mir250().items():
            kw = dict(ambient=0.8) if "light" in name else {}
            sc.add(f"{g}/{name}", mesh, col, g, **kw)
        if cargo:
            carrier, seats = C.carrier()
            sc.add(f"{g}/cup carrier", carrier.translate(CARRIER_AT, inplace=False), P.RACK_C, g)
            self.seats = [np.array(s, float) + CARRIER_AT for s in seats]
            cx, cy, cz = CRADLE_AT
            ring = C.lathe([(M.CONT_R + 1.0, 0), (M.CONT_R + 7.0, 0), (M.CONT_R + 7.0, CRADLE_H + 25.0),
                            (M.CONT_R + 1.0, CRADLE_H + 25.0)], res=64).translate((cx, cy, cz), inplace=False)
            floor = pv.Cylinder(center=(cx, cy, cz + 1.5), direction=(0, 0, 1), radius=M.CONT_R + 7.0,
                                height=3.0, resolution=64).triangulate()
            sc.add(f"{g}/cradle", ring.merge(floor), (0.30, 0.32, 0.36), g)
            self.cradle_seat = np.array([cx, cy, cz + 3.0])
        # round 9: the ballast plate, as low as a top module goes (on the MiR250's deck, under the cabinet), and
        # proud of the cabinet all round so it reads as a plate: dark steel with a yellow edge stripe (stability())
        for name, (mesh, col) in ballast_meshes().items():
            sc.add(f"{g}/{name}", mesh, col, g, specular=0.25)
        self.x, self.y, self.yaw = 0.0, 0.0, 0.0
        self.rb = RB.Robot(sc, A.ROBOT, g, T((*A.ARM_LOCAL, P.AMR_TOP)), q0=A.PARK_DEG, prefix=prefix)

    def set(self, x, y, yaw=0.0):
        self.x, self.y, self.yaw = x, y, yaw
        self.sc.gmat[self.g] = T((x, y, 0)) @ R((0, 0, 1), yaw)
        if self.rb.held is not None:
            self.rb.set()

    def drive(self, x1, y1):
        """Along a smoothstep S-curve to (x1, y1), its long axis on the tangent (it drives along its length), from rest
        to rest at the MiR250's 0.3 m/s^2 along the curve (props.s_curve, props.ramp_frac), over the step's time.
        Round 8: PR #321's ramped drive, brought over (it had the MiR at about twice its published acceleration)."""
        at, ps, s = P.s_curve(self.x, self.y, x1, y1)

        def up(u):
            f = P.ramp_frac(P.unease(u), s[-1], MIR_SPEED)
            self.set(*at(float(np.interp(f * s[-1], s, ps))))
        return up

    def secs(self, x1, y1=None):
        s = P.s_curve(self.x, self.y, x1, self.y if y1 is None else y1)[2]
        return max(1.2, P.ramp_secs(s[-1], MIR_SPEED))

    def world(self, p):
        return (self.sc.world(self.g) @ np.r_[p, 1.0])[:3]


def follow(rb, poses, max_jump=25.0):
    """A move of the grasp point through a list of 4x4 poses (piecewise, orientation slerped between them), IK solved
    now along the whole path so an impossible move fails before anything renders. Returns update(u)."""
    dense = []
    for A0, A1 in zip(poses[:-1], poses[1:]):
        sl = Slerp([0.0, 1.0], Rotation.from_matrix(np.stack([A0[:3, :3], A1[:3, :3]])))
        n = max(4, int(np.linalg.norm(A1[:3, 3] - A0[:3, 3]) / 6.0))
        for s in np.linspace(0, 1, n, endpoint=False):
            Mx = np.eye(4)
            Mx[:3, :3] = sl([s]).as_matrix()[0]
            Mx[:3, 3] = A0[:3, 3] + (A1[:3, 3] - A0[:3, 3]) * s
            dense.append(Mx)
    dense.append(poses[-1])
    q, path = rb.q.copy(), []
    for Mx in dense:
        q = rb.solve(Mx, q)
        path.append(q)
    path = np.array(path)
    jump = np.degrees(np.abs(np.diff(path, axis=0)).max()) if len(path) > 1 else 0.0
    if jump > max_jump:
        raise ValueError(f"path would flip the arm ({jump:.0f} deg in one step)")
    n = len(path) - 1

    def up(u):
        f = u * n
        i = min(int(f), n - 1)
        rb.set(path[i] + (path[i + 1] - path[i]) * (f - i))
    return up


def status(sc, **kv):
    rows = dict(getattr(sc, "_rows", {}))
    rows.update({k.replace("_", " "): v for k, v in kv.items()})
    sc._rows = rows
    sc.gauges = [(k, v) for k, v in rows.items() if v]


def W(p) -> np.ndarray:
    """A point in the rePowder model's frame -> the world."""
    return np.asarray(p, float) + RP


def cam(eye, at) -> list:
    """A camera given in the rePowder's frame."""
    return [tuple(W(eye)), tuple(W(at)), (0, 0, 1)]


# ------------------------------------------------------------------------------------------------ the cups
def add_cups(sc, mir):
    """The four charged Al cups (cup, Si powder to 73 % of the cavity, plug pressed home), standing in the carrier's
    four pockets on the MiR. Each is a group cup0..cup3, its frame at the cup's base centre. The cups that end up at
    the back of the crucible (y > 0) get a copy halved through their own axis for the cutaway, and those at the front
    go with the half that is cut away."""
    top = C.FLOOR_Z + (C.FILL_TOP - C.FLOOR_Z) * C.fill_fraction("Al", "Si", 10.0)
    for k in range(N_CUPS):
        grp = f"cup{k}"
        sc.add(f"{grp}/cup", C.cup(), C.AL_5N, grp, specular=0.6)
        sc.add(f"{grp}/plug", C.plug().translate((0, 0, C.PLUG_HOME_Z), inplace=False), C.AL_5N, grp, specular=0.6)
        sc.add(f"{grp}/powder", C.powder(top), C.POWDERS["Si"][0], grp, specular=0.05)
        sc.parent[grp] = "amr"
        sc.gmat[grp] = T(mir.seats[k])
        if math.sin(math.radians(CUP_ANGLES[k])) > 0:       # at the back: halved through its axis (y >= 0 kept)
            for part, prof, col in (("cup", C.cup_profile(), C.AL_5N),
                                    ("plug", [(r, z + C.PLUG_HOME_Z) for r, z in C.plug_profile()], C.AL_5N),
                                    ("powder", C.powder_profile(top), C.POWDERS["Si"][0])):
                sc.add(f"{grp}/{part}#h", half_lathe(prof), col, grp, specular=0.4 if part != "powder" else 0.05)
                sc.cutrole[f"{grp}/{part}#h"] = "half"
                sc.cutrole[f"{grp}/{part}"] = "whole"
        else:                                               # at the front: in the half the cutaway removes
            for part in ("cup", "plug", "powder"):
                sc.cutrole[f"{grp}/{part}"] = "whole"
        sc.cut_f[grp] = 0.0


def half_lathe(profile, res: int = 40) -> pv.PolyData:
    """The half of a lathe part with y >= 0 (the half the cutaway keeps), its cut faces capped."""
    pts = np.array([(r, 0.0, z) for r, z in profile], float)
    face = pv.PolyData(pts, faces=np.r_[len(pts), np.arange(len(pts))])
    return face.extrude_rotate(resolution=res, angle=180.0, capping=True, rotation_axis=(0, 0, 1)).triangulate().clean()


def heat_cups(sc, temp):
    c = temp_color(temp)
    amb = 0.18 + 0.55 * max(0.0, min(1.0, (temp - 450) / 400))
    for k in range(N_CUPS):
        for part in ("cup", "plug", "cup#h", "plug#h"):
            if f"cup{k}/{part}" in sc.actors:
                sc.color[f"cup{k}/{part}"] = c
                sc.ambient[f"cup{k}/{part}"] = amb


def cup_seat(k) -> np.ndarray:
    """The cup's base centre standing in the crucible, model frame: #222's slug_base_z, on the floor cone's rise."""
    a = math.radians(CUP_ANGLES[k])
    r_out = CUP_R + C.STOCK_D / 2 - C.EDGE_CHAMFER
    z = M.Z_CR + M.floor_z(r_out) + 0.05
    return np.array([CUP_R * math.cos(a), CUP_R * math.sin(a), z])


def cup_pose(k, r_b, z_b, tilt) -> np.ndarray:
    """The cup's frame (model): its base centre r_b from the axis on its radial line, z_b high, tipped `tilt` deg
    with its top leaning away from the axis (#222: "foot against the rod and its top leaning away from the adapter")."""
    a = math.radians(CUP_ANGLES[k])
    e = np.array([math.cos(a), math.sin(a), 0.0])
    t = np.array([-math.sin(a), math.cos(a), 0.0])
    Mx = R(t, tilt)
    Mx[:3, 3] = e * r_b + np.array([0, 0, z_b])
    return Mx


# The line the cup's axis follows down the bore, tipped TIP_DEG: its outer side 0.3 mm inside the bore at the rim (the
# meshes' facets stand up to 0.2 mm proud of the drawn circles). On it the cup's inner side meets the rod's adapter by
# about 0.3 mm in the model, #222's -0.09 mm (-2.1 to +0.5) "too close to call" squeeze, and its foot clears the rod.
LINE_R = M.CRUCIBLE_ID / 2 - 0.3 - C.STOCK_D / 2 / math.cos(math.radians(TIP_DEG))


def line_pose(k, depth):
    """The cup on LINE_R, its foot `depth` mm under the rim."""
    return cup_pose(k, LINE_R - depth * math.tan(math.radians(TIP_DEG)), M.RIM - depth, TIP_DEG)


def descent(k) -> list:
    """Cup poses (model frame) down into the crucible: beside the rod's adapter, over the bore; tipped, the foot over
    the bore's lip and clear of everything; the foot at the rim by the rod; and on down LINE_R to #222's tight spot,
    the cup's top just under the adapter."""
    d_tight = C.SLUG_L * math.cos(math.radians(TIP_DEG)) - M.ROD_ADAPTER_ABOVE_RIM + 0.3
    return [cup_pose(k, 22.0, M.RIM + 40.0, 0.0), cup_pose(k, LINE_R + 1.15, M.RIM + 8.0, TIP_DEG),
            line_pose(k, 0.0), line_pose(k, d_tight)]


def tip_in_path(k, release=0.78):
    """The held path and the slide (model frame). The arm carries the cup down `descent` to the fraction `release`
    of it and lets go there: as low as the 2F-85 can go (release_at). Lower, its fingertips would reach the filling
    cone and the bore, whose 57.1 mm the fingers' corners don't fit, or the wall thermocouple standing in the cone.
    The cup slides the rest of the way on its own, past the adapter, and down onto the floor cone. Returns (held,
    slide)."""
    d = descent(k)
    n = len(d) - 1
    at = pose_path(d, release)
    i = min(int(release * n), n - 1)
    held = [cup_pose(k, 30.0, M.RIM + 150.0, 0.0)] + d[:i + 1] + [at]
    seat = cup_seat(k)
    slide = [at] + d[i + 1:] + [cup_pose(k, CUP_R, seat[2] + 14.0, 0.0), cup_pose(k, CUP_R, seat[2], 0.0)]
    return held, slide


TONG_LINE_OUT = 0.0                   # mm the tong's line runs further out than LINE_R (see tong_clearance)


def tong_path(k) -> list:
    """Cup k's poses (model frame) as the tong carries it, all the way: over the crucible; #222's descent (beside the
    adapter, tipped 4.1 deg with the foot over the bore's lip, the foot at the rim by the rod, down the line to where
    the top passes under the adapter); then upright and in to its place, and down onto the floor cone."""
    seat = cup_seat(k)
    d = [cup_pose(k, 26.0, M.RIM + 70.0, 0.0)] + descent(k)
    if TONG_LINE_OUT:                                  # the two poses on the line, moved out along the radius
        a = math.radians(CUP_ANGLES[k])
        d = d[:3] + [T(np.array([math.cos(a), math.sin(a), 0.0]) * TONG_LINE_OUT) @ Mx for Mx in d[3:]]
    # under the adapter the top is free: stand the cup up as it goes on down, its outer side 0.3 mm inside the bore
    # at the rim all the way (line_pose for a tilt going from TIP_DEG to 0), then in to its place and down
    d_tight = C.SLUG_L * math.cos(math.radians(TIP_DEG)) - M.ROD_ADAPTER_ABOVE_RIM + 0.3
    up = []
    for s_ in (0.35, 0.7, 1.0):
        th = TIP_DEG * (1 - s_)
        dep = d_tight + (66.0 - d_tight) * s_
        lr = M.CRUCIBLE_ID / 2 - 0.3 - C.STOCK_D / 2 / math.cos(math.radians(th)) + TONG_LINE_OUT
        up.append(cup_pose(k, lr - dep * math.tan(math.radians(th)), M.RIM - dep, th))
    return d + up + [cup_pose(k, CUP_R, seat[2] + 5.0, 0.0), cup_pose(k, CUP_R, seat[2], 0.0)]


def _fcl_obj(mesh, Mx=None):
    import fcl
    m = mesh.triangulate()
    f = np.asarray(m.faces).reshape(-1, 4)[:, 1:].astype(np.int32)
    v = np.asarray(m.points, float)
    bvh = fcl.BVHModel()
    bvh.beginModel(len(v), len(f))
    bvh.addSubModel(v, f)
    bvh.endModel()
    o = fcl.CollisionObject(bvh, fcl.Transform())
    if Mx is not None:
        o.setTransform(fcl.Transform(Mx[:3, :3], Mx[:3, 3]))
    return o


def _dist(a, b) -> float:
    """Least distance between two FCL objects, mm; negative (the depth, roughly) when they overlap."""
    import fcl
    if fcl.collide(a, b, fcl.CollisionRequest(), fcl.CollisionResult()):
        res = fcl.CollisionResult()
        fcl.collide(a, b, fcl.CollisionRequest(num_max_contacts=50, enable_contact=True), res)
        return -max((c.penetration_depth for c in res.contacts), default=0.0)
    return float(fcl.distance(a, b, fcl.DistanceRequest(), fcl.DistanceResult()))


def tong_clearance(n_per_seg: int = 14) -> dict:
    """Along each cup's tong path: the least clearance of the tong (jaws, bridge, stem), and of the cup it carries,
    to the sealing rod, its adapter, the crucible, the filling cone, the wall thermocouple and the cups already in;
    and the gripper's lowest point over the rim. Model frame, the rod seated and the lever up. Written to
    out/alloy_atomize_clearance.json."""
    ms = M.meshes()
    fixed = {"sealing rod": "sealing_rod", "rod adapter": "rod_adapter", "crucible": "crucible",
             "filling cone (top insulation)": "top_insulation", "thermocouple": "thermocouple"}
    obj = {k: _fcl_obj(ms[v]["whole"]) for k, v in fixed.items()}
    tm = tong_meshes()
    tong_parts = {"jaws": tm["tong_a jaw"][0].merge(tm["tong_b jaw"][0]), "stem and bridge": tm["tong stem"][0]}
    cup_mesh = C.cup().merge(C.plug().translate((0, 0, C.PLUG_HOME_Z), inplace=False))
    rows = []
    for k in range(N_CUPS):
        path = tong_path(k)
        dense = [pose_path(path, f) for f in np.linspace(0, 1, n_per_seg * (len(path) - 1) + 1)]
        seated = {f"cup {j + 1}": _fcl_obj(cup_mesh, T(cup_seat(j))) for j in range(k)}
        best = {}
        for Mx in dense:
            F = tong_frame_for(k, Mx)
            movers = {"cup": _fcl_obj(cup_mesh, Mx)}
            movers.update({p: _fcl_obj(mesh, F) for p, mesh in tong_parts.items()})
            for who, o in movers.items():
                for what, w in list(obj.items()) + list(seated.items()):
                    if who == "cup" and what == "crucible" and Mx is dense[-1]:
                        continue                               # standing on its floor
                    d = _dist(o, w)
                    key = (who, what)
                    if key not in best or d < best[key][0]:
                        best[key] = (d, float(M.RIM - Mx[2, 3]))
        rows.append(dict(cup=k + 1, angle_deg=CUP_ANGLES[k],
                         least_clearance_mm={f"{a} to {b}": round(d, 2) for (a, b), (d, _) in sorted(best.items())},
                         where_foot_under_rim_mm={f"{a} to {b}": round(z, 1) for (a, b), (_, z) in
                                                  sorted(best.items())}))
    top_seated = cup_seat(0)[2] + C.SLUG_L
    return dict(cups=rows, seated_cup_tops_below_rim_mm=round(float(M.RIM - top_seated), 1),
                gripper_lowest_over_rim_mm=round(float(top_seated + TONG_GRASP - 30.0 - M.RIM), 1),
                note="The loading tong (tong_meshes): jaws 1.2 mm spring steel, 8 mm wide, 12 mm down the cup's top "
                     "on the two sides square to the crucible's radius; a 6 x 8 mm stem; the 2F-85 on its handle "
                     f"{TONG_GRASP:.0f} mm up. Distances by FCL on the meshes (the model's facets stand up to 0.2 mm "
                     "proud of the drawn circles), each the least along that cup's whole path (tong_path), with the "
                     "foot's depth under the rim where it happens; negative is an overlap. The cup's own squeeze past "
                     "the adapter is #222's -0.09 mm for a 3/4 in cup, which no tool changes.")


def release_at(rb, k, grip_of, steps: int = 90) -> tuple[float, np.ndarray]:
    """How far down `descent` (0..1) the arm can carry cup k, as it holds it now, with the gripper and the arm clear
    of everything (the filling cone, the crucible, the adapter, the thermocouple, the cups already in) and the cup
    touching nothing but the rod's adapter: #222's squeeze. Tried from each IK branch over the crucible; returns the
    deepest (the nearest branch of those that go as deep) and its joints at the pose over the crucible.
    `grip_of(Mx)`: the TCP pose for a cup pose Mx (model frame). Without the checker, 0.78 (the foot about 15 mm in
    the bore) and the nearest branch."""
    import collide
    above = grip_of(tip_in_path(k)[0][0])
    if RB.NO_PLAN or collide is None:
        return 0.78, rb.solve(above)
    chk = rb.checker()
    world = chk.snapshot()
    d = descent(k)

    def ok(q):                                       # holding it, and opening to let go
        return not any([h for h in chk.collisions(q, c, world) if h[0] != "held" or h[3] != g("rod")]
                       for c in (GRIP_CUP, (GRIP_CUP + GRIP_LET_GO) / 2, GRIP_LET_GO))
    cands = collide.ik_all(rb.model, inv(sc_world(rb)) @ above, rb.q) or [rb.solve(above)]
    fs = np.linspace(0.0, 0.85, steps + 1)               # no deeper than the foot ~25 mm in the bore
    depth = []
    for q0 in cands:
        got = -1
        if ok(q0):
            q = q0.copy()
            try:
                for i, f in enumerate(fs):
                    q2 = rb.solve(grip_of(pose_path(d, f)), q)
                    if np.abs(q2 - q).max() > math.radians(25) or not ok(q2):
                        break
                    q, got = q2, i
            except ValueError:
                pass
        depth.append(got)
    # the nearest branch that goes nearly as deep as the deepest (the nearer, the easier the move to it), and two
    # steps short of where it first touches anything
    top = max(depth)
    j = next(i for i, dd in enumerate(depth) if dd >= top - 3)
    return float(fs[max(0, depth[j] - 2)]) if depth[j] >= 0 else 0.0, cands[j]


def sc_world(rb) -> np.ndarray:
    return rb.sc.world(rb.root)


def pose_path(poses, f):
    """Piecewise-linear through 4x4 poses (positions lerped, rotations slerped), f in 0..1."""
    n = len(poses) - 1
    i = min(int(f * n), n - 1)
    s = f * n - i
    A0, A1 = poses[i], poses[i + 1]
    sl = Slerp([0.0, 1.0], Rotation.from_matrix(np.stack([A0[:3, :3], A1[:3, :3]])))
    Mx = np.eye(4)
    Mx[:3, :3] = sl([s]).as_matrix()[0]
    Mx[:3, 3] = A0[:3, 3] + (A1[:3, 3] - A0[:3, 3]) * s
    return Mx


def inv(Mx):
    Mi = np.eye(4)
    Mi[:3, :3] = Mx[:3, :3].T
    Mi[:3, 3] = -Mx[:3, :3].T @ Mx[:3, 3]
    return Mi


# ------------------------------------------------------------------------------------------------ the lid's knob
def knob_grasp() -> np.ndarray:
    """The grasp of the lid's knob, world frame. The knob is a 28 mm ball on a stalk on the hood's front-right
    face, its centre 12.7 mm off the face, so a level grasp from the front put the right finger through the hood.
    The pads go either side of the ball along the face, the fingers pointing down its slope and their width square
    to it: 3 mm out from the ball's centre, every part of the gripper is clear of the face."""
    c = np.array([M.HOOD_R0 * 0.62, -20.0, M.HOOD_Z0 + M.HOOD_H1 + 30.0]) + np.array([0.6, 0.0, 0.8]) * 38.0
    a0, a1 = M.HOOD_R0 * math.cos(math.pi / 6), M.HOOD_R1 * math.cos(math.pi / 6)
    n = np.array([math.cos(math.radians(-30.0)), math.sin(math.radians(-30.0)), (a0 - a1) / M.HOOD_H2])
    n /= np.linalg.norm(n)                                     # the face's outward normal (hexframe: a vertex on +x)
    t1 = np.cross(n, (0.0, 0.0, 1.0))
    t1 /= np.linalg.norm(t1)
    a = np.cross(n, t1)                                        # down the face's slope
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2], Mx[:3, 3] = np.cross(n, a), n, a, W(c + n * 3.0)
    return Mx


HOOD_TOP = M.HOOD_Z0 + M.HOOD_H1 + M.HOOD_H2        # the lid's flat top, 1510 mm
PRESS_AT = (-25.0, -15.0)              # where arm 2 presses on the lid's top, model x, y (round 9): 139 mm from the
                                       # hinge, 0.47 of the latch's 293; 190 mm from arm 1's tool axis at the tab
PRESS_TILT = 25.0                      # degrees: the press leans away from arm 2's base, so the wrist stays in reach
PRESS_F = 100.0                        # N, arm 2's press (estimate): under the 111 N its 12.5 kg rated payload, less the
                                       # 1.2 kg gripper, would weigh
GRIP_PRESS = 1.0                       # the 2F-85 shut: its fingertips together make the pusher


def gripper_low(Tw: np.ndarray, close: float) -> float:
    """The lowest world z of the 2F-85 (fingers, coupling, wrist camera) with its grasp point at the pose Tw."""
    import ur_arm
    G = ur_arm.gripper_fk(close)
    F = Tw @ T((0.0, 0.0, -ur_arm.TCP_MM))
    low = 1e9
    for part, lst in ur_arm.gripper_meshes().items():
        for mesh, _, _ in lst:
            pts = np.c_[np.asarray(mesh.points, float), np.ones(mesh.n_points)] @ (F @ G[part]).T
            low = min(low, float(pts[:, 2].min()))
    return low


def press_pose(gap: float = 0.8) -> np.ndarray:
    """Arm 2's tool pose pressing down on the lid's top with its shut fingertips, the lowest of them `gap` mm over it
    (world). The tool leans PRESS_TILT away from arm 2's base (a straight-down press 1.5 m up is past its reach from
    the left of the first MiR250), with the wrist camera (tool0's -y) to the side."""
    base = np.array([B_AT[0] + A.ARM_LOCAL[0], B_AT[1] + A.ARM_LOCAL[1]])
    p = W((PRESS_AT[0], PRESS_AT[1], HOOD_TOP + 40.0))
    h = p[:2] - base
    h /= np.linalg.norm(h)
    a = math.radians(PRESS_TILT)
    Tw = P.tcp_frame(p, (h[0] * math.sin(a), h[1] * math.sin(a), -math.cos(a)), 90.0)
    Tw[2, 3] += HOOD_TOP + gap - gripper_low(Tw, GRIP_PRESS)
    return Tw


def arc_branch(rb, sc, grasp, pose_at, move, close, skip, n: int = 23, back: float = 110.0) -> np.ndarray:
    """The IK solution at `grasp` from which the arm can follow pose_at(u), u 0..1, while move(u) swings the part it
    holds (the lid, the lever), touching nothing but the actors named in `skip` (what it holds), and from which it
    can back off `back` mm clear too; the nearest such one. Falls back to the nearest solution."""
    import collide
    if RB.NO_PLAN or collide is None:
        return rb.solve(grasp)
    chk = rb.checker()
    Tb = inv(sc.world(rb.root)) @ grasp
    cands = collide.ik_all(rb.model, Tb, rb.q) or [rb.solve(grasp)]
    for q in cands:
        ok, qq = True, q.copy()
        for u in np.linspace(0.0, 1.0, n):
            move(u)
            try:
                q_new = rb.solve(pose_at(u), qq)
            except ValueError:
                ok = False
                break
            if np.abs(q_new - qq).max() > math.radians(20):     # a wrist or elbow flip on the way: follow() can't
                ok = False
                break
            qq = q_new
            if any(not any(k in h[2] for k in skip) for h in chk.collisions(qq, close, chk.snapshot())):
                ok = False
                break
        move(0.0)
        if not ok:
            continue
        try:
            q_back = rb.solve(grasp @ T((0, 0, -back)), q)
        except ValueError:
            continue
        if not chk.collisions(q_back, 0.0, chk.snapshot()):
            return q
    return cands[0]


def lever(sc, deg):
    """The sealing-rod lever swung up `deg` about its pivot on the post (model.py LEVER_AXIS, PIVOT)."""
    sc.gmat[g("arm")] = R(tuple(M.LEVER_AXIS), deg, tuple(M.PIVOT))


# ------------------------------------------------------------------------------------------------ the lid's latch
# How the furnace lid really shuts (PR #318 round 6, from the lab's own training video T4, youtu.be/1F9_4ccwhss at
# 5:08, 5:17 and 5:23): one stainless over-centre draw latch (a toggle latch) on a flat on the furnace body's front
# right, its keeper (a plate with a lip, two screws) on the lid above it. The operator presses the lid down with one
# hand and closes the latch's lever with the other. The SOP: "close the furnace lid and secure the latch just tight
# enough to seal; if it hisses, loosen, adjust the latch and retighten" (T4 5:17, T8 9:09), so its loop is threaded
# to set the draw. Beside it a horizontal bolt comes out of the machine: "once you close the furnace and you change the
# pressure in the furnace, it automatically locks; there is like a bolt coming and locking the furnace" (Bartosz
# Kalicki, AMAZEMET, rePowder-BYU-Installation-Details.txt, 22:04-22:11). Drawn here in the chapter (the model's
# cache stays as it is): the latch's base on the body, its lever, its loop, the keeper on the lid, and the bolt on a
# bracket in front of the lever. The lever gets a pull tab for the robot (the real one has a plain end with a hole).
LATCH_AZ = -30.0                      # the hood's front-right face (model.py hexframe: a vertex on +x)
LATCH_PIVOT_R = M.BODY_R + 14.0       # the lever's pivot: 14 mm off the body
LATCH_Z = M.BODY_TOP - 74.0           # and 74 mm under the deck
LATCH_OPEN = 105.0                    # degrees the lever swings out and down to let the loop off the keeper
TAB = np.array([25.0, 0.0, 60.0])     # the pull tab's grasp point, latch frame (x out, y along the face, z up)
GRIP_TAB = 0.79                       # the 2F-85 on the 20 mm tab
GRIP_TAB_OPEN = 0.72                  # and open only so far round it: wide open, a finger meets the bolt's cylinder
BOLT_TRAVEL = 55.0                    # the locking bolt: out in front of the lever, or back clear of it


def latch_frame() -> np.ndarray:
    """The latch's frame in the model's: x out of the body at LATCH_AZ, y along the face, z up, origin the pivot."""
    a = math.radians(LATCH_AZ)
    n = np.array([math.cos(a), math.sin(a), 0.0])
    t = np.cross((0.0, 0.0, 1.0), n)
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2], Mx[:3, 3] = n, t, (0, 0, 1), n * LATCH_PIVOT_R + np.array([0, 0, LATCH_Z])
    return Mx


def _bx(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def _cy(c, d, r, h, res=24):
    return pv.Cylinder(center=c, direction=d, radius=r, height=h, resolution=res).triangulate()


def latch_meshes() -> dict:
    """{part: (mesh, colour, group)} in the latch frame. Groups: latch_base (on the body), latch_lever (turns about
    the frame's y axis), latch_loop (on the lever, turns about its pin), keeper (on the lid), lockbolt (slides on y)."""
    st, dk = (0.82, 0.83, 0.85), (0.55, 0.57, 0.60)
    dk2 = (0.36, 0.38, 0.41)              # round 8: the base and keeper darker, so the bright lever and loop read
    #                                       against them (all light grey, the latch vanished into the furnace body)
    base = _bx(-18, -2, -23, 23, -10, 62).merge(_bx(-4, 6, -19, -15, -6, 6)).merge(_bx(-4, 6, 15, 19, -6, 6))
    # the pull tab ends in a T: the 2F-85's pads sit inside its head, so the pull is taken by shape, not friction
    lever_ = _bx(0, 4, -15, 15, -4, 62).merge(_bx(4, 46, -10, 10, 56, 64)).merge(_bx(46, 50, -17, 17, 54, 66)).merge(
        _cy((0, 0, 0), (0, 1, 0), 4, 34))
    loop = None
    for y in (-10.0, 10.0):                       # the U-loop: two rods from the lever's pin up over the keeper's lip
        a, b = np.array([6.0, y, 30.0]), np.array([-4.0, y, 102.5])
        rod = pv.Line(a, b).tube(radius=2.2, n_sides=12).triangulate()
        loop = rod if loop is None else loop.merge(rod)
    loop = loop.merge(_cy((-4.0, 0, 102.5), (0, 1, 0), 2.2, 22, res=12))
    keeper = _bx(-17.4, -7.4, -17, 17, 76, 100).merge(_bx(-7.4, -1.5, -17, 17, 95, 100))
    for y in (-10, 10):
        keeper = keeper.merge(_cy((-7.0, y, 86), (1, 0, 0), 3.0, 1.5, res=16))
    body = _cy((10, 65, 48), (0, 1, 0), 10, 50).merge(_bx(-33, 2, 53, 77, 42, 54))
    bolt = _cy((10, 8.5, 48), (0, 1, 0), 4, 53, res=16)       # out: from the cylinder to past the lever's far edge
    return {"latch base": (base, dk2, "latch_base"), "latch lever": (lever_, st, "latch_lever"),
            "latch loop": (loop, st, "latch_loop"), "latch keeper": (keeper, dk2, "keeper"),
            "lock cylinder": (body, dk, "latch_base"), "lock bolt": (bolt, (0.70, 0.71, 0.73), "lockbolt")}


def add_latch(sc):
    Lf = latch_frame()
    for name, (mesh, col, grp) in latch_meshes().items():
        sc.add(f"rp {name}", mesh, col, g(grp), specular=0.6)
    for grp in ("latch_base", "latch_lever", "lockbolt"):
        sc.parent[g(grp)] = "rp"
    sc.parent[g("latch_loop")] = g("latch_lever")
    sc.parent[g("keeper")] = g("hood")
    sc.gmat[g("latch_base")] = sc.gmat[g("keeper")] = Lf
    latch(sc, 0.0)
    lock_bolt(sc, 0.0)                    # back: the furnace is at atmosphere


LATCH_NAMES = ("rp latch base", "rp latch lever", "rp latch loop", "rp latch keeper", "rp lock cylinder",
               "rp lock bolt")


def latch(sc, deg):
    """The lever swung out `deg` about its pivot; the loop with it, turned back a little so it lifts off the lip."""
    Lf = latch_frame()
    sc.gmat[g("latch_lever")] = Lf @ R((0, 1, 0), deg, (0, 0, 0))
    pin = (6.0, 0.0, 30.0)
    sc.gmat[g("latch_loop")] = R((0, 1, 0), -0.35 * deg, pin)


def lock_bolt(sc, f):
    """f = 1: the bolt out in front of the lever (the furnace under pressure); 0: back, clear of it."""
    sc.gmat[g("lockbolt")] = latch_frame() @ T((0, BOLT_TRAVEL * (1 - f), 0))


def latch_fade(sc, a):
    """The latch is on the half the cutaway removes: it fades with it."""
    for n in LATCH_NAMES:
        sc.alpha[n] = a


def tab_grasp(deg=0.0) -> np.ndarray:
    """The 2F-85 on the pull tab from above, fingers along the face, with the lever out `deg`; world frame."""
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2], Mx[:3, 3] = (0, -1, 0), (-1, 0, 0), (0, 0, -1), TAB   # the wrist camera (tool0 -y) outboard
    return T(RP) @ latch_frame() @ R((0, 1, 0), deg, (0, 0, 0)) @ Mx


# ------------------------------------------------------------------------------------------------ the loading tong
# Sterling (PR #318): "some interference between the gripper and the sealing rod when adding the charges ... I also
# don't like that it's just getting dropped inside from a high height. This also seems like something where a custom
# end effector might help." So the 2F-85 now loads the cups with a tong: two spring-steel jaws on a slim stem, which
# take a cup by its plug end, its top 12 mm, on the two sides square to the crucible's radius. Everything below the
# handle stays inside a 6 x 8 mm stem and the cup's own outline, so the tong goes down the bore with the cup, sets it
# on the floor cone, opens and comes straight up. The 2F-85's fingers clamp the handle's two halves (custom fingertip
# blocks, pinned): closing it the last 3 mm shuts the jaws, opening it 3 mm opens them, opening it fully lets the
# tong go in its holder on the MiR. Steel throughout; the jaws' faces lined with a ceramic paper, so they don't weld
# to hot Al (assumed design, not built).
TONG_JAW_T, TONG_JAW_W, TONG_JAW_L = 1.2, 8.0, 12.0
TONG_STEM = (6.0, 8.0)                # x (square to the radius, the jaws' closing line) and y (along the radius)
TONG_GRASP = 185.0                    # the handle's centre, mm over the jaws' top (the cup's top)
TONG_OPEN = 1.6                       # mm each jaw opens
GRIP_TONG, GRIP_TONG_OPEN = 0.80, 0.77
CUP_RAD = C.STOCK_D / 2
TONG_AT = (-381.0, 0.0)               # its holder, a sleeve hung on the cabinet's -x end, MiR-local


def tong_meshes() -> dict:
    """{part: (mesh, colour, group)} in the tong's frame: origin the cup's top centre, z up its axis, x the jaws'
    closing line. Groups: tong (stem, bridge, handle), tong_a / tong_b (a jaw each, they slide on x)."""
    sx, sy = TONG_STEM
    xj = CUP_RAD + TONG_JAW_T / 2
    stem = _bx(-sx / 2, sx / 2, -sy / 2, sy / 2, 9.0, TONG_GRASP - 18)
    bridge = _bx(-xj - TONG_JAW_T / 2 - 1.0, xj + TONG_JAW_T / 2 + 1.0, -TONG_JAW_W / 2, TONG_JAW_W / 2, 4.0, 9.0)
    # the handle: two halves, 19 mm across where the 2F-85's pads clamp them, joined above by a flexure block
    handle = _bx(-9.5, 9.5, -15, 15, TONG_GRASP - 18, TONG_GRASP + 18).merge(
        _bx(-12, 12, -15, 15, TONG_GRASP + 18, TONG_GRASP + 26))
    steel, dark = (0.66, 0.68, 0.71), (0.20, 0.21, 0.24)
    out = {"tong stem": (stem.merge(bridge), steel, "tong"), "tong handle": (handle, dark, "tong")}
    for s, grp in ((-1, "tong_a"), (1, "tong_b")):
        jaw = _bx(s * xj - TONG_JAW_T / 2, s * xj + TONG_JAW_T / 2, -TONG_JAW_W / 2, TONG_JAW_W / 2, -TONG_JAW_L,
                  4.0)
        out[f"{grp} jaw"] = (jaw, steel, grp)
    return out


def add_tong(sc, mir):
    """The tong standing in its holder (a sleeve) on the MiR's cabinet top."""
    for name, (mesh, col, grp) in tong_meshes().items():
        sc.add(name, mesh, col, grp, specular=0.6)
    sc.parent["tong_a"] = sc.parent["tong_b"] = "tong"
    tong_jaws(sc, 0.0)
    top = P.MIR["H"] + P.CAB_H
    z0 = top - 140.0                      # the sleeve hangs on the cabinet's end, its rim level with the cabinet top
    x, y = TONG_AT
    sleeve = C.lathe([(0.0, 0), (18.0, 0), (18.0, 140.0), (14.0, 140.0), (14.0, 6.0), (0.0, 6.0)], res=40).translate(
        (x, y, z0), inplace=False).merge(_bx(x, -P.MIR["L"] / 2 + 40, y - 22, y + 22, z0 + 60, z0 + 76))
    sc.add("amr/tong holder", sleeve, (0.30, 0.32, 0.36), "amr")
    sc.parent["tong"] = "amr"
    sc.gmat["tong"] = T((x, y, z0 + 6.0 + TONG_JAW_L + 1.0)) @ R((0, 0, 1), 90.0)
    return sc.gmat["tong"].copy()


def tong_jaws(sc, f):
    """f = 1: the jaws open TONG_OPEN each; 0: shut on a cup."""
    sc.gmat["tong_a"] = T((-TONG_OPEN * f, 0, 0))
    sc.gmat["tong_b"] = T((TONG_OPEN * f, 0, 0))


def tong_frame_for(k, Mx) -> np.ndarray:
    """The tong's frame (model) holding cup k whose frame is Mx: at the cup's top centre, along its axis, the jaws
    square to the crucible's radius at the cup's place."""
    a = math.radians(CUP_ANGLES[k])
    t = np.array([-math.sin(a), math.cos(a), 0.0])
    z = Mx[:3, 2] / np.linalg.norm(Mx[:3, 2])
    x = t - z * (t @ z)
    x /= np.linalg.norm(x)
    F = np.eye(4)
    F[:3, 0], F[:3, 1], F[:3, 2] = x, np.cross(z, x), z
    F[:3, 3] = (Mx @ np.r_[0.0, 0.0, C.SLUG_L, 1.0])[:3]
    return F


# ------------------------------------------------------------------------------------------------ will the MiR tip?
# Sterling (PR #318): "whether the base is heavy enough to compensate for a lot of load from being exerted via the
# arm". The sums for the arm pulling the latch open and pressing the lid shut, at the pose the chapter uses.
MASS = dict(mir250=97.0,                      # MiR250 spec sheet
            ur10e=33.3,                       # UR10e datasheet (its links below, UR's dynamics parameters)
            control_box=12.0,                 # UR e-Series control box (UR spec sheet: 12 kg)
            cabinet=25.0,                     # the top cabinet's frame and panels: estimate
            gripper=1.2,                      # 2F-85 0.925 kg + wrist camera and adapter: estimate
            on_top=3.0)                       # carrier, cups, tong, cradle: estimate
UR10E_LINKS = (7.369, 13.051, 3.989, 2.1, 1.98, 0.615)   # kg, shoulder .. wrist 3 (UR's DH/dynamics page); base: rest
# Round 9 (Sterling, PR #318, 2026-11-05 22:56: "the mobile bases will need to be heavy enough (and the center of
# gravity low enough)"): each MiR250 stands on a 40 mm steel plate, 760 x 550 mm, on its deck under the cabinet: the
# lowest place a top module can carry weight (the MiR250 itself is a closed chassis). Ours, not a product; it doubles
# as the top module's base plate. Round 6-8: 32 mm, 724 x 524, 95 kg, flush with the cabinet (a dark band at its foot)
BALLAST = dict(L=760.0, W=550.0, T=40.0)      # mm
BALLAST_T = BALLAST["T"]
BALLAST_KG = 7.85e-6 * BALLAST["L"] * BALLAST["W"] * BALLAST["T"]          # 131 kg of steel
MIR250_PAYLOAD = 250.0                        # kg (MiR250 spec sheet)


def ballast_meshes() -> dict:
    """The ballast plate, MiR-local: dark steel on the deck, a yellow band round its top edge."""
    L, Wd, H, t = BALLAST["L"], BALLAST["W"], P.MIR["H"], BALLAST["T"]
    plate = pv.Box(bounds=(-L / 2, L / 2, -Wd / 2, Wd / 2, H, H + t - 7)).triangulate()
    band = pv.Box(bounds=(-L / 2, L / 2, -Wd / 2, Wd / 2, H + t - 7, H + t)).triangulate()
    return {"ballast plate": (plate, (0.17, 0.18, 0.20)), "ballast edge": (band, (0.93, 0.74, 0.10))}
WHEELS = (325.0, 225.0)                       # the support rectangle, +-x, +-y, MiR-local: the corner casters (estimate)
DRIVE_SHARE = 0.5                             # share of the weight on the two drive wheels (estimate)
MU = 0.6                                      # drive wheel on the floor: the low end of the 0.6-0.8 MiR asks of a
                                              # floor (MiR250 user guide, section 16)
LATCH_F = dict(expected=100.0, design=200.0)  # N at the lever: Kipp's K0080 cover latches take 100 / 150 / 200 N of
                                              # hand force for 2 / 4 / 7 kN held (notes/alloy_atomize.md)
LID_KG = 10.0                                 # the lid (estimate): the model's hood is 810 cm3 of 5 mm steel, 6.4 kg,
                                              # with its CoG 166 mm from the hinge; a real one is lined: call it 10
LID_KNOB_N = round(LID_KG * 9.81 * 166.0 / 281.0)   # its weight on the knob, 281 mm from the hinge, as it starts up: 58 N


def stability(mir, q, P_tool, F_dir, ballast: bool) -> dict:
    """Tipping and sliding of the MiR250 with the UR10e at joints q, a force F_dir (unit, world, on the robot) at
    P_tool. Returns the force that would tip it about its weakest edge, the force that would slide it, and the CoG."""
    import ur_arm
    W0 = mir.sc.world(mir.g)
    inv0 = inv(W0)
    fk = ur_arm.fk(A.ROBOT, q)
    root = inv0 @ mir.sc.world(mir.rb.root)
    pos = {k: (root @ fk[k])[:3, 3] for k in ("base", "shoulder", "upper_arm", "forearm", "wrist1", "wrist2",
                                              "wrist3", "tool0")}
    H = P.MIR["H"]
    items = [(MASS["mir250"], (0.0, 0.0, 120.0)), (MASS["control_box"], (0.0, 0.0, H + 150.0)),
             (MASS["cabinet"], (0.0, 0.0, H + P.CAB_H / 2)),
             (MASS["on_top"] if mir.cargo else 0.0, (-100.0, 0.0, H + P.CAB_H + 40.0)),
             (MASS["ur10e"] - sum(UR10E_LINKS), pos["base"]), (UR10E_LINKS[0], pos["shoulder"]),
             (UR10E_LINKS[1], (pos["upper_arm"] + pos["forearm"]) / 2),
             (UR10E_LINKS[2], (pos["forearm"] + pos["wrist1"]) / 2), (UR10E_LINKS[3], pos["wrist1"]),
             (UR10E_LINKS[4], pos["wrist2"]), (UR10E_LINKS[5], pos["wrist3"]), (MASS["gripper"], pos["tool0"])]
    if ballast:
        items.append((BALLAST_KG, (0.0, 0.0, H + BALLAST_T / 2)))
    m = sum(k for k, _ in items)
    G = sum(k * np.asarray(p, float) for k, p in items) / m
    Wt = m * 9.81
    Pl = (inv0 @ np.r_[P_tool, 1.0])[:3]
    Fl = inv0[:3, :3] @ np.asarray(F_dir, float)
    ax, ay = WHEELS
    edges = {"+x": ((ax, -ay), (1, 0)), "-x": ((-ax, ay), (-1, 0)), "+y": ((ax, ay), (0, 1)), "-y": ((-ax, -ay), (0, -1))}
    tip = {}
    for name, (a, u) in edges.items():
        A_ = np.array([a[0], a[1], 0.0])
        u = np.array([u[0], u[1], 0.0])
        e = np.cross((0, 0, 1.0), u)
        arm_F = float(np.cross(Pl - A_, Fl) @ e)               # N mm per N of force: > 0 overturns
        keep = Wt * float(-(G - A_) @ u)                       # N mm the weight holds it down with
        tip[name] = dict(restoring_Nm=round(keep / 1000, 1), lever_mm=round(arm_F, 1),
                         tips_at_N=round(keep / arm_F, 0) if arm_F > 1e-6 else None)
    worst = min((v["tips_at_N"], k) for k, v in tip.items() if v["tips_at_N"] is not None)
    h = float(np.hypot(Fl[0], Fl[1]))
    slide = MU * DRIVE_SHARE * Wt / h if h > 1e-6 else None
    return dict(mass_kg=round(m, 1), cog_mm=[round(float(x)) for x in G], force_point_mm=[round(float(x)) for x in Pl],
                force_dir=[round(float(x), 3) for x in Fl], edges=tip, tips_at_N=worst[0], tips_about=worst[1],
                slides_at_N=round(slide, 0) if slide else None)


def ur_arm_tcp() -> float:
    import ur_arm
    return float(ur_arm.TCP_MM)


def tong_tcp(F) -> np.ndarray:
    """The 2F-85's grasp of the tong whose frame is F: on the handle, pointing down the tong, fingers on its x."""
    G = np.eye(4)
    G[:3, 0], G[:3, 1], G[:3, 2] = F[:3, 0], -F[:3, 1], -F[:3, 2]
    G[:3, 3] = F[:3, 3] + F[:3, 2] * TONG_GRASP
    return G


# ------------------------------------------------------------------------------------------------ the movie
def build():
    data = None if LITE else lab.meshes()
    idata = None if LITE else tour.load(["glovebox"])
    sc = Scene(NAME, TITLE, mp4=False)
    if not (PREVIEW or AUDIT):              # the 3-D render goes to out/clean/ first; splice() writes the final MP4
        RAW.mkdir(parents=True, exist_ok=True)
        # fragmented, so a render that is cut off still leaves a playable file; fast, since splice() re-encodes it
        mp4 = part_paths(PART[0])[0] if PART else RAW_MP4
        sc.mp4 = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{sc.size[0]}x{sc.size[1]}",
             "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-movflags", "+frag_keyframe+empty_moov", str(mp4)], stdin=subprocess.PIPE)
        sc.mp4_path = mp4
    if os.environ.get("ARM_AUDIT_RENDER") and not (PREVIEW or AUDIT):
        import collide                      # the audit of ARM_AUDIT=1, run alongside the render: one pass for both
        sc.auditor = collide.Auditor(sc)
        sc.frame_hooks.append(sc.auditor)
    sc.slots = []                           # where the real footage goes: (beat, MP4 frame, GIF frame, step label)
    sc.intro = 0.8
    L = None
    if not LITE:
        with FL.two_shuttle():              # round 8: setup_lab's floor, the second Shuttle at x = 3630
            L = A.Lab(sc, data, robot=False)
        L.show_gauges = False
        L.skin(0.0)(1.0)
        L.apply_state()
    sc.add("line floor", pv.Plane(center=(1200, -900, -1.5), direction=(0, 0, 1), i_size=34000, j_size=18000),
           A.FLOOR_C, "floor", ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
    if not LITE:
        inst, ents = idata["glovebox"]
        tour.Rig(sc, inst, ents, "glovebox:", at=FL.floor_at("glovebox", inst.bbox()))
        ents = line.aconity_entries()
        pts = np.vstack([e["mesh"].points for e in ents.values() if e["mesh"].n_points])
        lo, hi = pts.min(0), pts.max(0)
        for n, e in ents.items():
            sc.add(n, e["mesh"], e["color"], "aconity", opacity=e["opacity"])
        sc.gmat["aconity"] = FL.floor_at("aconity", (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))     # x = 6950
    for n in list(sc.actors):                   # the merged rePowder: replaced by its parts
        if n.startswith("repowder:"):
            sc.alpha[n] = 0.0
    load_rp(sc, ghost={"stack_cover": 0.35})
    for k in range(4):
        sc.show(sc.members(g(f"slug{k}")), 0.0)
    pool = Pool(sc, level=-30)
    powder = Powder(sc, level=0)
    add_stream(sc)
    add_gas(sc)
    spray = Particles(sc, "spray", (0.40, 0.41, 0.46), size=5.5)
    drops = Particles(sc, "drops", MELT, size=7.0, slowmo=0.35, seed=2)
    vent = Particles(sc, "vent", (0.80, 0.86, 0.92), size=4.5, slowmo=0.6, seed=3, free=True, gravity=-0.02)
    mir = Mir(sc)
    mir.set(*A.AMR_XY, 0.0)
    mir_b = Mir(sc, g="amrB", prefix="urB", cargo=False)      # round 9: the second unit, for the lid
    mir_b.set(*B_HOME, 0.0)
    add_cups(sc, mir)
    add_latch(sc)
    sc.tong_home = add_tong(sc, mir)
    hood(sc, 0.0)
    flange_clamp(sc, 1.0)
    return sc, L, mir, pool, powder, spray, drops, vent, mir_b


def fast_forward(sc, first: int, last: int | None = None):
    """Draw only sub-steps first..last-1: the others' frames are counted but not drawn (ATOMIZE_TAIL, ATOMIZE_PART),
    so a changed ending can be spliced onto an earlier render (see the notes), or the parts rendered side by side."""
    snap = sc.snap

    def maybe(n=1):
        if len(sc.substeps) < first or (last is not None and len(sc.substeps) >= last):
            sc.want_still = False
            sc.n += n
            return None
        return snap(n)
    sc.snap = maybe


def slot(sc, beat: str):
    """Mark where the real footage for `beat` goes: the frame the next sub-step would start on. The view at that
    moment is kept without its text, for footage shown beside the model."""
    if PREVIEW or AUDIT or len(sc.substeps) < TAIL or (PART and not PART[0] <= len(sc.substeps) < PART[1]):
        return
    png = RAW / f"{NAME}_slot_{beat}.png"
    Image.fromarray(sc.render_base()).save(png)
    sc.slots.append(dict(beat=beat, frame=sc.n, gif=len(sc.gif_frames), label=sc.label, model_png=str(png)))


def finish(sc):
    """Save the 3-D render to out/clean/ (its MP4, its GIF frames as PNGs, its JSON with the footage slots), then
    splice the footage in. ARM_AUDIT=1 renders nothing: it only writes out/collisions/alloy_atomize.json."""
    if PREVIEW or AUDIT:
        return sc.save()
    raw_json, raw_gif = (part_paths(PART[0])[1:] if PART else (RAW_JSON, RAW_GIF))
    if raw_gif.exists():
        shutil.rmtree(raw_gif)
    raw_gif.mkdir(parents=True)
    for i, im in enumerate(sc.gif_frames):
        im.save(raw_gif / f"{i:05d}.png", compress_level=1)
    n_gif = len(sc.gif_frames)
    sc.gif_frames, sc.gif = [], False
    info = sc.save()                                   # the MP4 in RAW, the still and out/alloy_atomize.json
    if sc.auditor is not None:                         # ARM_AUDIT_RENDER=1
        sc.auditor.save()
    meta = json.loads((OUT / f"{NAME}.json").read_text())
    meta.update(slots=sc.slots, gif_frames=n_gif, gif_fps=scene.GIF_FPS, gif_size=list(scene.GIF_SIZE))
    if PART:
        meta.update(part=list(PART))
    raw_json.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(info, flush=True)
    return None if PART else splice()


def merge() -> str:
    """Join the parts of a render made with ATOMIZE_PART (in sub-step order) into out/clean/'s single render, then
    splice the footage in."""
    metas = sorted((json.loads(p.read_text()) for p in RAW.glob(f"{NAME}_3d_part*.json")), key=lambda m: m["part"][0])
    lst = RAW / "parts.txt"
    lst.write_text("".join(f"file '{part_paths(m['part'][0])[0].name}'\n" for m in metas))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(RAW_MP4)], check=True)
    if RAW_GIF.exists():
        shutil.rmtree(RAW_GIF)
    RAW_GIF.mkdir(parents=True)
    k, slots = 0, []
    for m in metas:
        for sl in m["slots"]:
            slots.append(dict(sl, gif=sl["gif"] + k))
        for pth in sorted(part_paths(m["part"][0])[2].glob("*.png")):
            shutil.copy(pth, RAW_GIF / f"{k:05d}.png")
            k += 1
    meta = dict(metas[-1])
    meta.pop("part", None)
    meta.update(slots=slots, gif_frames=k)
    RAW_JSON.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(f"merged {len(metas)} parts: {k} GIF frames, {len(slots)} slots", flush=True)
    return splice()


def movie():
    sc, L, mir, pool, powder, spray, drops, vent, mir_b = build()
    if TAIL or PART:
        fast_forward(sc, *(PART or (TAIL,)))
    rb = mir.rb
    n = 5
    m_cup = RUN["charge_g"]
    ps = powder_sums()
    four, full225, full400 = ps["charges"]
    st = dict(pf=0.0, pc=0.0, o2=None, t=24.0, us="off")

    def show_g(**kw):
        st.update(kw)
        rows = {"Arm 1": st.get("arm"), "MiR250 1": st.get("mir"), "Arm 2": st.get("armB"),
                "MiR250 2": st.get("mirB"), "Charge": st.get("charge"),
                "Pressure": f"{st['p_abs']:.1f} mbar" if st.get("p_abs") is not None else None,
                "Furnace": f"{st['pf']:+.0f} mbar" if st.get("p_on") else None,
                "Chamber": f"{st['pc']:+.0f} mbar" if st.get("p_on") else None,
                "O₂": f"{st['o2']:.0f} ppm" if st.get("o2") is not None else None,
                "T (wall)": f"{st['t']:.0f} °C" if st.get("t_on") else None,
                "US": st.get("us") if st.get("us_on") else None,
                "Container": st.get("cont")}
        sc._rows = {}
        status(sc, **{k: v for k, v in rows.items() if v})

    # ---------------------------------------------------------------- places
    y_park = -2450.0                                  # the MiR broadside, 260 mm clear of the view port: the arm needs room
    x_load = RP[0] + 150.0                            # arm base 150 mm right of the furnace axis: the lid opens left
    x_wait = RP[0] + 1150.0                           # out of the cutaway's line of sight, in front of the HX
    x_cont = RP[0] + M.CHUTE_X - 320.0                # arm base 320 mm left of the container: room to reach in
    y_cont = -2650.0                                  # and 200 mm further out than for the lid: closer, the forearm
                                                      # comes down through the MiR's own cabinet to the low handle
    CAM_WIDE = [(-1500, -9200, 4300), (-1900, -1500, 900), (0, 0, 1)]
    CAM_LOAD = cam((-1000, -2050, 2150), (-20, -300, 1200))
    CAM_TOP = cam((-480, -560, 1700), (0, 10, 1290))
    CAM_SEC = cam((-330, -820, 1430), (5, 0, 1262))
    CAM_POUR = cam((-620, -1720, 1140), (10, 0, 970))
    CAM_CHAMBER = cam((-900, -2200, 1000), (110, 0, 760))
    CAM_CONT = cam((1450, -1650, 1250), (250, -300, 520))
    CAM_CRADLE = cam((1900, -2500, 1750), (150, -560, 760))
    CAM_PAIR = cam((-800, -4300, 1500), (-280, -600, 520))   # round 9: both units from the front, their ballast plates
    CAM_TWO = cam((640, -1000, 1700), (40, -90, 1390))       # round 9: both arms at the lid and the latch, front right
    CAM_LATCH2 = cam((760, 40, 1520), (100, -60, 1400))      # round 9: the latch from the right, arm 2's hand above it
                                                             # (from the front, arm 1's forearm hides the latch)
    rbB = mir_b.rb

    show_g(arm="parked", mir="at the VLM's opening", armB="parked", mirB="waiting in the aisle",
           charge=f"{N_CUPS} × 5N Al cup, Si, {m_cup:.1f} g")
    sc.cam = list(CAM_WIDE)
    # ------------------------------------------------------------------ 1. drive over
    cap = (f"From the VLM to the atomizer: MiR250 1 carries the four charged 5N Al cups, {m_cup:.1f} g of Al-10Si "
           f"(Si powder under each plug), to the AMAZEMET rePowder. Four charges is how the lab loads the crucible; "
           f"its own Al runs were 169-180 g (DAL #159). MiR250 2 comes over from the aisle for the lid.")
    lbl = [("AMAZEMET rePowder atomizer", tuple(W((250, 0, 1700))), (0.16, 0.24)),
           ("4 charged Al cups", tuple(mir.world((-300, -150, 1110))), (0.62, 0.30)),
           ("Kardex VLM", (0, -1700, 2700), (0.80, 0.16))]
    sc.step(f"1/{n}", cap, 1.0, None, hold=1.0, labels=lbl)
    show_g(mir="driving", mirB="driving")
    t_drive = max(mir.secs(x_load, y_park), mir_b.secs(*B_AT))
    sc.step(f"1/{n}", cap, t_drive, RB.both(mir.drive(x_load, y_park), mir_b.drive(*B_AT)), hold=0.2, cam_to=CAM_PAIR,
            labels=[("AMAZEMET rePowder atomizer", tuple(W((250, 0, 1700))), (0.16, 0.24))])
    show_g(mir="at the rePowder", mirB="at the rePowder")
    H_bal = P.MIR["H"] + BALLAST_T / 2
    cap = (f"Two MiR250 + UR10e units: opening and shutting the lid takes two hands. Each MiR250 carries a "
           f"{BALLAST_KG:.0f} kg steel plate, {BALLAST['T']:.0f} mm thick, on its deck under the cabinet: the weight as "
           f"low as a top module can carry it, so an arm can pull or press on the machine without tipping its base "
           f"(sums in notes/alloy_atomize.md).")
    sc.step(f"1/{n}", cap, 0.8, None, hold=2.6,
            labels=[("MiR250 2: the lid", tuple(mir_b.world((0, 0, 1000))), (0.06, 0.22)),
                    ("MiR250 1: the cups", tuple(mir.world((-250, -100, 1000))), (0.72, 0.22)),
                    (f"ballast plate, {BALLAST_KG:.0f} kg steel", tuple(mir_b.world((-150, -BALLAST['W'] / 2, H_bal))),
                     (0.04, 0.74)),
                    ("the same under MiR250 1", tuple(mir.world((200, -BALLAST['W'] / 2, H_bal))), (0.72, 0.74))])

    # ------------------------------------------------------------------ 2. lid open, cups in, lid shut
    # round 9: two arms, as a person does it with two hands (T4 5:23): arm 2 holds the lid down by its top while arm 1
    # pulls the latch's lever (the lid can't jump when the loop lets go), then arm 2 swings the lid up by its knob
    CAM_LATCH = cam((420, -330, 1360), (120, -75, 1300))     # from the right, so the arm (from the front) is clear
    Lw = T(RP) @ latch_frame()
    press = press_pose()
    pre_press = press @ T((0, 0, -120))
    cap = ("Arm 2 holds the lid down by its top while arm 1 works the latch, as a person does it with two hands (the "
           "lab's training video T4, 5:23), so the lid can't jump when the latch lets go. The latch is one over-centre "
           "draw latch on the furnace's front right, its keeper on the lid; the machine's own locking bolt beside it is "
           "back: the furnace is at atmosphere.")
    show_g(arm="lid latch", armB="holding the lid down")
    sc.step(f"2/{n}", cap, 1.8, RB.both(rbB.joint_to(Tw=pre_press), rbB.grip_to(GRIP_PRESS)), hold=0.05,
            cam_to=CAM_TWO,
            labels=[("draw latch", tuple((Lw @ np.r_[2.0, -16.0, 20.0, 1.0])[:3]), (0.74, 0.62)),
                    ("keeper, on the lid", tuple((Lw @ np.r_[-8.0, -14.0, 92.0, 1.0])[:3]), (0.74, 0.40)),
                    ("arm 2", tuple(press[:3, 3] + (0.0, 0.0, 260.0)), (0.12, 0.20))])
    sc.step(f"2/{n}", cap, 0.7, rbB.line_to(press), hold=0.1,
            labels=[("draw latch", tuple((Lw @ np.r_[2.0, -16.0, 20.0, 1.0])[:3]), (0.74, 0.62)),
                    ("keeper, on the lid", tuple((Lw @ np.r_[-8.0, -14.0, 92.0, 1.0])[:3]), (0.74, 0.40)),
                    (f"arm 2 presses the lid down, ~{PRESS_F:.0f} N", tuple(W((PRESS_AT[0], PRESS_AT[1], HOOD_TOP))),
                     (0.12, 0.20))])
    rbB.events.append((sc.n, "grasp", g("hood"), None))           # its fingertips on the lid's top
    q_press = rbB.q.copy()
    # the latch: arm 1 takes the lever's pull tab from above and swings it out and down (the IK branch is picked now,
    # with arm 2 on the lid, so arm 1's wrist stays clear of it)
    g_tab = tab_grasp(0.0)
    q_tab = arc_branch(rb, sc, g_tab, lambda u: tab_grasp(LATCH_OPEN * u), lambda u: latch(sc, LATCH_OPEN * u),
                       GRIP_TAB, ("latch lever", "latch loop"), back=110.0)
    n_out = Lw[:3, 0]
    stab = {}
    for key, ball in (("as_drawn_with_ballast", True), ("without_ballast", False)):
        stab[key] = dict(latch_pull=stability(mir, q_tab, g_tab[:3, 3], -n_out, ball),
                         latch_push=stability(mir, q_tab, g_tab[:3, 3], n_out, ball),
                         arm2_press=stability(mir_b, q_press, press[:3, 3], -press[:3, 2], ball))   # the lid pushes
                                                                       # back up the tilted tool's axis
    sp, sb = stab["without_ballast"]["latch_pull"], stab["as_drawn_with_ballast"]["latch_pull"]
    show_g(arm="lid latch")
    pre_tab = g_tab @ T((0, 0, -110))
    sc.step(f"2/{n}", cap, 1.6, RB.both(rb.joint_to(q1=rb.solve(pre_tab, q_tab)), rb.grip_to(GRIP_TAB_OPEN)), hold=0.05,
            labels=[(f"arm 2 presses the lid down, ~{PRESS_F:.0f} N", tuple(W((PRESS_AT[0], PRESS_AT[1], HOOD_TOP))),
                     (0.12, 0.20)),
                    ("arm 1", tuple(pre_tab[:3, 3] + (0.0, -60.0, 120.0)), (0.80, 0.20)),
                    ("locking bolt, back", tuple((Lw @ np.r_[10.0, 65.0, 58.0, 1.0])[:3]), (0.74, 0.62))])
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(g_tab), hold=0.05, cam_to=CAM_LATCH2)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_TAB), hold=0.05)
    rb.events.append((sc.n, "grasp", g("latch_lever"), g("latch_loop")))
    tab_out = follow(rb, [tab_grasp(d) for d in np.linspace(0.0, LATCH_OPEN, 12)])

    def latch_open(u):
        tab_out(u)
        latch(sc, LATCH_OPEN * u)
    cap = (f"Pulled out over centre, the lever lets the loop off the keeper. Not measured: about "
           f"{LATCH_F['expected']:.0f} N, {LATCH_F['design']:.0f} N for a stiff one (cover latches of this kind). "
           f"MiR250 1 with its {BALLAST_KG:.0f} kg plate would tip at {sb['tips_at_N']:.0f} N and slide at "
           f"{sb['slides_at_N']:.0f} N ({sp['tips_at_N']:.0f} and {sp['slides_at_N']:.0f} N without the plate).")
    sc.step(f"2/{n}", cap, 1.6, latch_open, hold=0.6, labels=[])
    sc.step(f"2/{n}", cap, 0.3, rb.grip_to(GRIP_TAB_OPEN), hold=0.05)
    rb.events.append((sc.n, "release", g("latch_lever"), g("latch_loop")))
    q_tab_open = rb.q.copy()
    sc.step(f"2/{n}", cap, 0.6, rb.line_to(tab_grasp(LATCH_OPEN) @ T((0, 0, -110))), hold=0.05, cam_to=CAM_TWO)
    # arm 2 lets go of the top and opens the lid by its knob
    knob = np.array([(90 + 131) / 2, -20.0, 1470.0])          # the lid's knob (model.py hood_knob), model frame
    grasp_k = knob_grasp()
    pre_k = grasp_k @ T((0, 0, -110))
    cap = ("Arm 2 lets go of the top, takes the lid's knob and swings the lid up about its hinge, to the left. The "
           "sealing rod is already fitted and seated: rod first, then the metal (GU500 manual, #222).")
    show_g(arm="waiting", armB="lid")
    sc.step(f"2/{n}", cap, 0.6, rbB.line_to(pre_press), hold=0.05)
    rbB.events.append((sc.n, "release", g("hood"), None))
    hinge_w = W(M.HINGE)
    arc = [R((0, 1, 0), -d, hinge_w) @ grasp_k for d in np.linspace(0, HOOD_OPEN, 12)]
    q_knob = arc_branch(rbB, sc, grasp_k, lambda u: R((0, 1, 0), -HOOD_OPEN * u, hinge_w) @ grasp_k,
                        lambda u: hood(sc, HOOD_OPEN * u), GRIP_KNOB, ("hood_knob",))   # clear all the way up
    sc.step(f"2/{n}", cap, 1.6, RB.both(rbB.joint_to(q1=rbB.solve(pre_k, q_knob)), rbB.grip_to(0.0)), hold=0.05,
            cam_to=CAM_LOAD,
            labels=[("lid knob", tuple(W(knob + (0, 0, 30))), (0.70, 0.22)),
                    ("sealing-rod lever", tuple(W((80, 0, 1400))), (0.74, 0.46))])
    sc.step(f"2/{n}", cap, 0.8, rbB.line_to(grasp_k), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rbB.grip_to(GRIP_KNOB), hold=0.05)
    rbB.events.append((sc.n, "grasp", g("knob"), None))          # the audit: the pads may touch the knob
    q_kb = rbB.q.copy()
    for key, ball in (("as_drawn_with_ballast", True), ("without_ballast", False)):
        stab[key]["arm2_lid"] = stability(mir_b, q_kb, grasp_k[:3, 3], (0.0, 0.0, -1.0), ball)
    stab.update(loads=dict(latch_N=LATCH_F, arm2_press_N=PRESS_F, arm2_lid_N=LID_KNOB_N),
                masses_kg=dict(MASS, ballast=round(BALLAST_KG, 1), ballast_plate_mm=BALLAST),
                payload_kg={k: round(sum(MASS[m] for m in ("cabinet", "control_box", "ur10e", "gripper"))
                                     + (MASS["on_top"] if c else 0.0) + BALLAST_KG, 1)
                            for k, c in (("mir250_1", True), ("mir250_2", False))},
                payload_limit_kg=MIR250_PAYLOAD, wheels_mm=WHEELS, drive_share=DRIVE_SHARE, mu=MU,
                note="tips_at_N: the force at the tool, in that direction, that would lift that MiR250 off its "
                     "weakest edge (the support rectangle WHEELS); slides_at_N: the horizontal force the drive wheels "
                     "hold by friction (MU x DRIVE_SHARE x weight). latch_pull / latch_push: MiR250 1, arm 1 at the "
                     "latch's pull tab (the IK branch the chapter uses), the lever pulling the arm toward the furnace "
                     "/ closing it, the other way. arm2_press: MiR250 2, arm 2 pressing straight down on the lid's "
                     "top, the tool leaning PRESS_TILT (the lid pushes back up its axis). arm2_lid: arm 2 at the lid's knob as it starts the swing (the "
                     "lid's weight pulls the arm down). Round 9: two units, a 131 kg plate (was 95 kg).")
    if not PREVIEW:
        (OUT / f"{NAME}_stability.json").write_text(json.dumps(stab, indent=1) + "\n")
    print("stability:", {k: {c: (v[c]["tips_at_N"], v[c]["slides_at_N"]) for c in v}
                         for k, v in stab.items() if isinstance(v, dict) and "latch_pull" in v}, flush=True)
    lid = follow(rbB, arc)

    def lid_up(u):
        lid(u)
        hood(sc, HOOD_OPEN * u)
    sc.step(f"2/{n}", cap, 2.2, lid_up, hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rbB.grip_to(0.0), hold=0.05)
    rbB.events.append((sc.n, "release", g("knob"), None))
    # straight up off the knob: backed off along the fingers, as arm 1 did, arm 2's forearm folds into its wrist
    away = T((0, 0, 100)) @ R((0, 1, 0), -HOOD_OPEN, hinge_w) @ grasp_k
    sc.step(f"2/{n}", cap, 0.7, rbB.line_to(away), hold=0.05)
    q_away = rbB.q.copy()
    show_g(armB="parked")
    sc.step(f"2/{n}", cap, 1.3, rbB.joint_to(PARK), hold=0.05)
    # the lever up off the adapter, out of the opening, as the machine is loaded by hand (training T4): down, its bar
    # lies over the places of the two cups nearest it, and the 2F-85's fingers would straddle it
    cap = ("Arm 1 lifts the sealing-rod lever off the rod's adapter and swings it up on its pivot, out of the "
           "opening, as the machine is loaded by hand. Down, it lies over the places of two of the cups. The rod "
           "stays seated.")
    lev_g = P.tcp_frame(W((LEVER_AT, 0.0, M.Z_ARM)), (0, 0, -1), 90.0)   # from above, fingers across the bar
    piv_w = tuple(W(M.PIVOT))

    def lev_pose(u):
        return R(tuple(M.LEVER_AXIS), M.ARM_RAISED * u, piv_w) @ lev_g
    q_lev = arc_branch(rb, sc, lev_g, lev_pose, lambda u: lever(sc, M.ARM_RAISED * u), GRIP_LEVER,
                       ("holder_arm",), back=100.0)
    show_g(arm="sealing-rod lever")
    sc.step(f"2/{n}", cap, 1.2, RB.both(rb.joint_to(q1=rb.solve(lev_g @ T((0, 0, -100)), q_lev)), rb.grip_to(0.0)),
            hold=0.05, labels=[("sealing-rod lever", tuple(W((60, 0, M.Z_ARM + 20))), (0.74, 0.40))])
    sc.step(f"2/{n}", cap, 0.6, rb.line_to(lev_g), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_LEVER), hold=0.05)
    rb.events.append((sc.n, "grasp", g("arm"), None))
    lev_arc = [lev_pose(u) for u in np.linspace(0.0, 1.0, 12)]
    lev_up = follow(rb, lev_arc)

    def lever_up(u):
        lev_up(u)
        lever(sc, M.ARM_RAISED * u)
    sc.step(f"2/{n}", cap, 1.6, lever_up, hold=0.05)
    sc.step(f"2/{n}", cap, 0.3, rb.grip_to(0.0), hold=0.05)
    rb.events.append((sc.n, "release", g("arm"), None))
    lev_off = lev_arc[-1] @ T((0, 0, -100))
    q_lev_off = rb.solve(lev_off, rb.q)
    sc.step(f"2/{n}", cap, 0.5, rb.line_to(lev_off), hold=0.05)

    # the loading tong out of its holder on the MiR's cabinet
    cap = ("The cups go in with a loading tong, a tool the 2F-85 holds: two thin spring-steel jaws on a slim stem. "
           "The gripper clamps its handle; closing the last 3 mm shuts the jaws, opening 3 mm opens them. Its "
           "wrist camera looks down past the tong.")
    show_g(arm="loading tong")
    home_w = sc.world("tong")
    g_home = tong_tcp(home_w)
    hw = home_w[:3, 3]
    CAM_TONG = [tuple(hw + (-420.0, -640.0, 520.0)), tuple(hw + (0.0, 0.0, 230.0)), (0, 0, 1)]
    sc.step(f"2/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=T((0, 0, 130)) @ g_home), rb.grip_to(0.0)), hold=0.05,
            cam_to=CAM_TONG, labels=[("loading tong", tuple(hw + (0.0, 0.0, 120.0)), (0.70, 0.30))])
    sc.step(f"2/{n}", cap, 0.8, rb.line_to(g_home), hold=0.05)
    cam_at = (g_home @ T((0.0, -67.0, 24.0 - ur_arm_tcp())) @ np.r_[0.0, 0.0, 0.0, 1.0])[:3]
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_TONG), hold=0.9,
            labels=[("loading tong", tuple(hw + (0.0, 0.0, 120.0)), (0.70, 0.30)),
                    ("wrist camera (RealSense D405)", tuple(cam_at), (0.08, 0.26))])
    rb.grasp("tong")
    sc.step(f"2/{n}", cap, 0.9, rb.line_to(T((0, 0, 210)) @ rb.tcp_world()), hold=0.05)

    def hold_cup(cg):
        """The tong has shut on the cup: the arm holds the cup now, the tong riding on it (the audit's bookkeeping:
        a held part may touch where it came from and where it goes)."""
        tw, cw = sc.world("tong"), sc.world(cg)
        rb.events.append((sc.n, "release", "tong", None))
        sc.parent.pop(cg, None)
        sc.gmat[cg] = cw
        rb.held = (cg, inv(rb.tcp_world()) @ cw)
        rb.events.append((sc.n, "grasp", cg, "amr"))
        sc.parent["tong"] = cg
        sc.gmat["tong"] = inv(cw) @ tw

    def hold_tong(cg):
        """The arm holds the tong again, the cup still in its jaws (or, after cup_down, standing on its own)."""
        tw, cw = sc.world("tong"), sc.world(cg)
        sc.parent.pop("tong", None)
        sc.gmat["tong"] = tw
        if sc.parent.get(cg) is None:
            sc.parent[cg] = "tong"
            sc.gmat[cg] = inv(tw) @ cw
        rb.events.append((sc.n, "release", cg, None))
        rb.held = ("tong", inv(rb.tcp_world()) @ tw)
        rb.events.append((sc.n, "grasp", "tong", None))

    def cup_down(k, cg):
        """The jaws open: the cup stays, standing on the floor cone at its place."""
        sc.parent[cg] = g("crucible")
        sc.gmat[cg] = inv(sc.world(g("crucible"))) @ T(RP) @ cup_pose(k, CUP_R, cup_seat(k)[2], 0.0)
        rb.events.append((sc.n, "release", cg, g("crucible")))
        for chk in [rb._checker] + list(getattr(sc.auditor, "checkers", {}).values()):
            if chk is not None:                      # what the arm holds changed under the same name: re-read it
                chk.held_group = None

    def jaws(f0, f1):
        def up(u):
            tong_jaws(sc, f0 + (f1 - f0) * u)
        return up
    xm = sc.world("amr")[:3, 0]
    for k in range(N_CUPS):
        cg = f"cup{k}"
        top = (sc.world(cg) @ np.r_[0.0, 0.0, C.SLUG_L, 1.0])[:3]
        F_pick = np.eye(4)
        F_pick[:3, 0], F_pick[:3, 1], F_pick[:3, 2], F_pick[:3, 3] = xm, np.cross((0, 0, 1.0), xm), (0, 0, 1), top
        g_pick = tong_tcp(F_pick)
        f = 1.0 if k == 0 else 0.7                               # the first one at full speed, the rest quicker
        if k == 0:
            g_low = cup_seat(0)[2] + C.SLUG_L + TONG_GRASP - 30.0 - M.RIM
            cap = ("Cup 1 of 4. The jaws take the cup's top 12 mm, on the two sides square to the crucible's radius, "
                   "so below the gripper nothing is wider than the cup and a 6 x 8 mm stem. The tong carries it down "
                   "#222's path: tipped 4.1° past the rod's adapter, then upright, and sets it on the floor cone. The "
                   f"gripper stays {g_low:.0f} mm over the rim.")
        else:
            cap = (f"Cup {k + 1} of {N_CUPS}, the same way, at #222's next place round the rod. Nothing is dropped: "
                   f"the jaws open only with the cup standing. Neighbours stand {CUP_GAP:.1f} mm apart; the jaws pass "
                   f"them with 1.3 mm to spare.")
        show_g(arm=f"cup {k + 1}: carrier to crucible")
        sc.step(f"2/{n}", cap, 1.4 * f, RB.both(rb.joint_to(Tw=T((0, 0, 90)) @ g_pick), rb.grip_to(GRIP_TONG_OPEN),
                                               jaws(0.0, 1.0)), hold=0.05)
        sc.step(f"2/{n}", cap, 0.7 * f, rb.line_to(g_pick), hold=0.05)
        sc.step(f"2/{n}", cap, 0.4, RB.both(rb.grip_to(GRIP_TONG), jaws(1.0, 0.0)), hold=0.05)
        hold_cup(cg)
        sc.step(f"2/{n}", cap, 0.6 * f, rb.line_to(T((0, 0, 150)) @ rb.tcp_world()), hold=0.05)
        path = tong_path(k)
        grips = [tong_tcp(T(RP) @ tong_frame_for(k, Mx)) for Mx in path]
        # by way of a pose in front of the furnace, right of the open lid: swung straight over, the tong's handle
        # grazed the lid's edge (one frame at 1.5 deg planning steps, the tong 0.2 m out from the wrist)
        stage = grips[0].copy()
        stage[0, 3], stage[1, 3] = RP[0] + 60.0, RP[1] - 200.0
        sc.step(f"2/{n}", cap, 1.3 * f, rb.joint_to(Tw=stage), hold=0.0, cam_to=CAM_TOP if k == 0 else None)
        sc.step(f"2/{n}", cap, 0.6 * f, rb.line_to(grips[0]), hold=0.05)
        # down the bore in three legs: to the foot at the rim, to the tight spot under the adapter, to the floor. At
        # each joint the arm's "held" part swaps between the cup and the tong (one riding on the other), so for the
        # audit each leg is its own episode, and the cup may touch what it touches where the leg starts and ends:
        # the bore's rim, the adapter and the rod at #222's squeeze, the floor cone. Nothing else changes.
        sc.step(f"2/{n}", cap, 1.2 * f, follow(rb, grips[:4]), hold=0.0,
                labels=[("rod adapter", tuple(W((0, 0, M.RIM + 40))), (0.10, 0.30)),
                        ("crucible, 57 mm bore", tuple(W((-26, 0, M.RIM - 6))), (0.10, 0.62))] if k == 0 else ())
        hold_tong(cg)
        sc.step(f"2/{n}", cap, 0.8 * f, follow(rb, grips[3:5]), hold=0.0)
        hold_cup(cg)
        sc.step(f"2/{n}", cap, 1.4 * f, follow(rb, grips[4:]), hold=0.05)
        hold_tong(cg)
        sc.step(f"2/{n}", cap, 0.4, RB.both(rb.grip_to(GRIP_TONG_OPEN), jaws(0.0, 1.0)), hold=0.05)
        cup_down(k, cg)
        sc.step(f"2/{n}", cap, 0.8 * f, rb.line_to(T((0, 0, 170)) @ rb.tcp_world()), hold=0.05)
        if DEBUG:
            print("cup", k, "world", np.round(sc.world(cg)[:3, 3] - RP, 1), "seat", np.round(cup_seat(k), 1),
                  flush=True)
    if not PREVIEW:
        cl = tong_clearance()
        (OUT / f"{NAME}_clearance.json").write_text(json.dumps(cl, indent=1) + "\n")
    cap = "The tong goes back in its holder on the MiR."
    show_g(arm="loading tong")
    home_w = sc.world("amr") @ sc.tong_home
    g_home = tong_tcp(home_w)
    sc.step(f"2/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=T((0, 0, 220)) @ g_home), rb.grip_to(GRIP_TONG),
                                       jaws(1.0, 0.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.9, rb.line_to(g_home), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("amr")
    sc.step(f"2/{n}", cap, 0.6, rb.line_to(T((0, 0, 120)) @ rb.tcp_world()), hold=0.05)
    cap = (f"All four cups stand round the rod, plug and vent up, {CUP_GAP:.1f} mm apart: {m_cup:.1f} g, about the "
           "size of the lab's own Al runs. The crucible could take far more metal than the cups bring.")
    show_g(arm="clear of the opening", charge=f"in the crucible, {m_cup:.1f} g")
    lid_open_grasp = R((0, 1, 0), -HOOD_OPEN, hinge_w) @ grasp_k
    # round 9: arm 1 waits off the raised lever, right of the opening (round 8: over the open lid, where arm 2 works)
    sc.step(f"2/{n}", cap, 1.4, RB.both(rb.joint_to(q1=q_lev_off), rb.grip_to(0.0)), hold=0.05, cam_to=CAM_LOAD)
    CAM_DOWN = cam((-22, -80, 1610), (0, 2, 1262))            # down into the open crucible
    sc.step(f"2/{n}", cap, 1.3, None, hold=1.8, cam_to=CAM_DOWN,
            labels=[("4 cups round the sealing rod", tuple(W(cup_seat(2) + (0, 0, C.SLUG_L))), (0.70, 0.30)),
                    (f"cup tops {M.RIM - cup_seat(1)[2] - C.SLUG_L:.0f} mm under the rim",
                     tuple(W(cup_seat(1) + (0, 0, C.SLUG_L))), (0.70, 0.62))])
    slot(sc, "charge")
    cap = ("Arm 1 lays the lever back down over the adapter. Then arm 2 swings the lid shut and holds it down on its "
           "seal while arm 1 closes the latch, and both MiR250s back off so the window stays clear.")
    show_g(arm="sealing-rod lever")
    sc.step(f"2/{n}", cap, 1.2, None, hold=0.05, cam_to=CAM_TOP)
    sc.step(f"2/{n}", cap, 0.5, rb.line_to(lev_arc[-1]), hold=0.05)
    sc.step(f"2/{n}", cap, 0.3, rb.grip_to(GRIP_LEVER), hold=0.05)
    rb.events.append((sc.n, "grasp", g("arm"), None))
    lev_dn = follow(rb, lev_arc[::-1])

    def lever_down(u):
        lev_dn(u)
        lever(sc, M.ARM_RAISED * (1 - u))
    sc.step(f"2/{n}", cap, 1.4, lever_down, hold=0.05)
    sc.step(f"2/{n}", cap, 0.3, rb.grip_to(0.0), hold=0.05)
    rb.events.append((sc.n, "release", g("arm"), None))
    sc.step(f"2/{n}", cap, 0.5, rb.line_to(lev_g @ T((0, 0, -100))), hold=0.05)
    # round 9: the lid shut by arm 2, held down on its seal by arm 2 while arm 1 closes the latch (T4 5:23)
    g_tab_o = tab_grasp(LATCH_OPEN)
    show_g(arm="lid latch", armB="lid")
    sc.step(f"2/{n}", cap, 1.4, RB.both(rb.joint_to(q1=rb.solve(g_tab_o @ T((0, 0, -110)), q_tab_open)),
                                       rb.grip_to(GRIP_TAB_OPEN)), hold=0.05, cam_to=CAM_LOAD)
    sc.step(f"2/{n}", cap, 1.4, rbB.joint_to(q1=q_away), hold=0.05)
    sc.step(f"2/{n}", cap, 0.7, rbB.line_to(lid_open_grasp), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rbB.grip_to(GRIP_KNOB), hold=0.05)
    rbB.events.append((sc.n, "grasp", g("knob"), None))
    lid_dn = follow(rbB, arc[::-1])

    def lid_down(u):
        lid_dn(u)
        hood(sc, HOOD_OPEN * (1 - u))
    sc.step(f"2/{n}", cap, 2.0, lid_down, hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rbB.grip_to(0.0), hold=0.05)
    rbB.events.append((sc.n, "release", g("knob"), None))
    sc.step(f"2/{n}", cap, 0.6, rbB.line_to(pre_k), hold=0.05)
    show_g(armB="holding the lid down")
    sc.step(f"2/{n}", cap, 1.2, RB.both(rbB.joint_to(Tw=pre_press), rbB.grip_to(GRIP_PRESS)), hold=0.05,
            cam_to=CAM_TWO)
    sc.step(f"2/{n}", cap, 0.6, rbB.line_to(press), hold=0.1,
            labels=[(f"arm 2 holds the lid on its seal, ~{PRESS_F:.0f} N",
                     tuple(W((PRESS_AT[0], PRESS_AT[1], HOOD_TOP))), (0.12, 0.20))])
    rbB.events.append((sc.n, "grasp", g("hood"), None))
    cap = ("Then the latch, with the lid held down: arm 1 swings the lever back up, the loop goes over the keeper's lip "
           "and the lever goes over centre, drawing the lid down onto its seal. A person does this, and the opening, "
           "in a few seconds with two hands; it is the one place an arm pushes hard on the machine.")
    show_g(arm="lid latch")
    sc.step(f"2/{n}", cap, 0.6, rb.line_to(g_tab_o), hold=0.05, cam_to=CAM_LATCH2)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_TAB), hold=0.05)
    rb.events.append((sc.n, "grasp", g("latch_lever"), g("latch_loop")))
    tab_in = follow(rb, [tab_grasp(d) for d in np.linspace(LATCH_OPEN, 0.0, 12)])

    def latch_shut(u):
        tab_in(u)
        latch(sc, LATCH_OPEN * (1 - u))
    sc.step(f"2/{n}", cap, 1.6, latch_shut, hold=0.2)
    sc.step(f"2/{n}", cap, 0.3, rb.grip_to(GRIP_TAB_OPEN), hold=0.05)
    rb.events.append((sc.n, "release", g("latch_lever"), g("latch_loop")))
    sc.step(f"2/{n}", cap, 0.6, rb.line_to(pre_tab), hold=0.05, cam_to=CAM_TWO)
    sc.step(f"2/{n}", cap, 0.5, rbB.line_to(pre_press), hold=0.05)
    rbB.events.append((sc.n, "release", g("hood"), None))
    sc.step(f"2/{n}", cap, 1.2, rb.joint_to(PARK), hold=0.05)
    sc.step(f"2/{n}", cap, 1.3, rbB.joint_to(PARK), hold=0.05)
    show_g(arm="parked", mir="waiting beside it", armB="parked", mirB="back to the aisle")
    sc.step(f"2/{n}", cap, max(mir.secs(x_wait), mir_b.secs(*B_HOME)),
            RB.both(mir.drive(x_wait, y_park), mir_b.drive(*B_HOME)), hold=0.1, cam_to=CAM_SEC)
    show_g(armB=None, mirB=None)

    # ------------------------------------------------------------------ 3. gas wash, heat, melt
    back = [k for k in range(N_CUPS) if math.sin(math.radians(CUP_ANGLES[k])) > 0]
    cap = ("Cut open at the furnace axis; the two back cups are cut through their own axes. Three cycles of pumping "
           "down to 4×10⁻¹ mbar and back-filling with 5N argon take the oxygen under 50 ppm. On each "
           "pump-down the air under the plugs leaves through their 1/16 in vents (#104).")
    vents = [cup_seat(k) + (0, 0, C.SLUG_L - C.PLUG_SEAT + 1.0) for k in range(N_CUPS)]
    show_g(p_abs=1013.0, o2=2.1e5)

    def bolt_out(u):
        lock_bolt(sc, u)
    sc.step(f"3/{n}", "The first pump-down starts. As the furnace leaves atmosphere, the machine's bolt comes out in "
            "front of the latch's lever: the lid can't be opened under vacuum or pressure (AMAZEMET, install call).",
            1.0, bolt_out, hold=0.9, cam_to=CAM_LATCH,
            labels=[("locking bolt, out", tuple((Lw @ np.r_[12.0, 10.0, 48.0, 1.0])[:3]), (0.08, 0.30))])

    def cut_open(u):
        set_cut(sc, window(u, 0.0, 0.6))
        latch_fade(sc, 1.0 - window(u, 0.0, 0.5))
    k0 = back[0]
    sc.step(f"3/{n}", cap, 1.5, cut_open, hold=0.2, cam_to=CAM_SEC,
            labels=[("vented plug, 5N Al", tuple(W(vents[k0]) + (0, 4, 1)), (0.08, 0.26)),
                    ("Si powder under it", tuple(W(cup_seat(k0) + (0, 3, 22))), (0.08, 0.56))])
    # an aside: building this stack is still by hand, and why it is the hard part to automate
    CAM_STACK = cam((-250, -470, 1240), (0, 0, 1150))
    cap = ("Still by hand: building this stack. The graphite crucible's threaded shank runs down into the chamber, "
           "where a thin graphite nut goes on from below, through the chamber's door, while someone holds the "
           "crucible still at the top: \"snug but never forced\" (the lab's SOP). A robot would need a tool at each "
           "end and fine force sensing: the UR10e's own is good to ±5.5 N and ±0.5 N·m; a wrist sensor resolves "
           "0.1 N and 0.005 N·m (Robotiq FT 300-S) or 1/16 N and 1/752 N·m (ATI Mini45). notes/crucible_automation.md")

    def nut_turn(u):
        sc.gmat[g("nut")] = R((0, 0, 1), 540.0 * u, (0, 0, 0))
    sc.step(f"3/{n}", cap, 4.0, nut_turn, hold=3.0, cam_to=CAM_STACK,
            labels=[("crucible, graphite", tuple(W((-31, 0, M.Z_CR + 30))), (0.08, 0.24)),
                    ("threaded shank", tuple(W((-M.SHANK_R, 0, M.Z_PLATFORM[0] - 2))), (0.08, 0.52)),
                    ("graphite nut, from below", tuple(W((-M.NUT_R + 2, 0, sum(M.NUT_Z) / 2))), (0.08, 0.76)),
                    ("graphite seal", tuple(W((M.NUT_R - 6, 0, M.NUT_Z[1] + 3))), (0.70, 0.70))])
    sc.step(f"3/{n}", cap, 1.2, None, hold=0.0, cam_to=CAM_SEC)
    o2s = [2.1e5, 3000.0, 300.0, 45.0]

    def wash(u):
        c = min(2, int(u * 3))
        v = u * 3 - c
        down_, up_ = window(v, 0.0, 0.45), window(v, 0.55, 1.0)
        p = 1013.0 * (1 - down_) + 0.4 * down_ if v < 0.5 else 0.4 + 1012.6 * up_
        o2 = o2s[c] + (o2s[c + 1] - o2s[c]) * up_
        set_gas(sc, 0.0 if v < 0.5 else 0.8 * up_)
        if 0.05 < v < 0.45 and sc.n % 2 == 0:
            for kk in back:
                vent.add(np.array([vents[kk]]) + vent.rng.normal(0, 0.8, (1, 3)),
                         np.array([[vent.rng.normal(0, 40), vent.rng.normal(0, 40), 260.0]]))
        vent.step()
        show_g(p_abs=p, o2=o2)
    sc.step(f"3/{n}", cap, 6.0, wash, hold=0.4, cam_to=CAM_TOP, live=False)
    vent.clear()
    cap = ("The 10 kW, 7 kHz coil heats the graphite and the graphite the charge. The Type N thermocouple sits in the "
           "crucible wall, so the metal lags its reading. The cups glow, then slump into a pool round the rod "
           "(Al-10Si is liquid above about 595 °C; a 750 °C hold is assumed).")
    show_g(t_on=True, t=24.0, p_abs=None, p_on=True, pf=150.0, pc=150.0)

    def heat_up(u):
        tt = 24 + (700 - 24) * u
        heat_cups(sc, tt)
        coil_glow(sc, min(1.0, u * 4))
        show_g(t=tt)
    sc.step(f"3/{n}", cap, 3.0, heat_up, hold=0.1, cam_to=CAM_SEC,
            labels=[("coil on (10 kW, 7 kHz)", tuple(W((-47, 0, M.Z_CR - 28 + 31))), (0.08, 0.62)),
                    ("Type N thermocouple, wall", tuple(W((40, 50, M.Z_CR + 60))), (0.74, 0.28))])

    seats = [cup_seat(k) for k in range(N_CUPS)]

    def slump(u):
        tt = 700 + 50 * u
        for k in range(N_CUPS):
            f = 1 - 0.95 * window(u, 0.05 + 0.06 * k, 0.72 + 0.05 * k)
            s = seats[k]
            sc.gmat[f"cup{k}"] = T(s) @ S((1 + 0.12 * (1 - f), 1 + 0.12 * (1 - f), f))
            for part in ("cup", "plug", "powder", "cup#h", "plug#h", "powder#h"):
                if f"cup{k}/{part}" in sc.actors:
                    sc.alpha[f"cup{k}/{part}"] = 1.0 if f > 0.07 else 0.0
        pool.set(-14 + (POOL_LEVEL + 14) * window(u, 0.05, 0.95))
        heat_cups(sc, max(tt, 680))
        rod_lift(sc, -1.5 * u)
        show_g(t=tt)
    sc.step(f"3/{n}", cap, 4.0, slump, hold=0.6,
            labels=[(f"melt pool, Al-10Si, {m_cup:.0f} g", tuple(W((-14, 0, M.Z_CR + POOL_LEVEL - 4))),
                     (0.08, 0.40))])
    slot(sc, "melt")
    # ------------------------------------------------------------------ 4. pour and atomize
    cap = ("Vibration on, then 200 mbar of argon over-pressure on the furnace: the pour runs on the pressure, not the "
           "melt's weight (#222). Sealing rod up: the stream falls through the nozzle onto the vibrating plate.")
    st_lv = dict(level=POOL_LEVEL)
    drain = (POOL_LEVEL + 4.0) / (11.0 * FPS)          # mm a frame: near the floor cone by the end of the pour
    show_g(us_on=True, us="40 kHz")

    def rod_up(u):
        rod_lift(sc, -1.5 + 13.5 * window(u, 0.2, 0.45))
        show_g(pf=150.0 + 200.0 * window(u, 0.0, 0.2), pc=150.0)
        stream(sc, 1.0 if u > 0.45 else 0.0, 1.0, window(u, 0.45, 0.7))
        film(sc, u > 0.7)
        if u > 0.7 and sc.n % max(1, 3 * FPS // 15) == 0:
            drops.emit_drops(2, M.IMPACT + np.array([0, 0, 3]), M.PLATE_UP * 250 + M.STACK_DIR * 500)
        drops.step()
        shake(sc, True)
    sc.step(f"4/{n}", cap, 3.0, rod_up, hold=0.4, live=True, cam_to=CAM_POUR,
            labels=[("sealing rod up", tuple(W((0, -6, M.Z_CR + 60))), (0.70, 0.22)),
                    ("melt stream", tuple(W((0, 0, 1060))), (0.70, 0.44)),
                    ("vibrating plate", tuple(W(M.PLATE_C + M.PLATE_ALONG * 20)), (0.08, 0.70))])

    def atomize(u, rate=26):
        stream(sc, 1.0, 1.0)
        spray.emit_spray(int(round(rate * PER_FRAME)))
        spray.step()
        drops.step()
        st_lv["level"] = max(-12.0, st_lv["level"] - drain)
        pool.set(st_lv["level"])
        powder.set(3 + (POWDER_END - 3) * min(1.0, spray.landed / 3800))
        shake(sc, True)
        show_g(pf=350.0, pc=150.0)
    cap = ("Droplets fly off the plate, freeze in the argon and run down the cone into the container. AMAZEMET's "
           "training fits a 0.7 mm nozzle for Al alloys (0.5 mm standard); which one our unit has is not known (#222).")
    sc.step(f"4/{n}", cap, 6.0, atomize, hold=0.6, live=True, still=True,
            labels=[("droplets freeze into powder", tuple(W(M.IMPACT + np.array([90, 0, -40]))), (0.70, 0.62))])
    slot(sc, "pour")
    cap = (f"The powder collects in the container under the chamber's valve, still under argon. At the Oct 27 bronze "
           f"run's yield, 91 % usable (DAL #219), the four cups make about {four['usable_g']:.0f} g of powder.")
    sc.step(f"4/{n}", cap, 4.0, atomize, hold=0.6, live=True, cam_to=CAM_CHAMBER,
            labels=[("powder container", tuple(W((M.CHUTE_X + M.CONT_R - 2, 0, 200))), (0.70, 0.74))])

    def tail(u):
        st_lv["level"] = max(-12.0, st_lv["level"] - 3 * drain)
        pool.set(st_lv["level"] if u < 0.8 else -30)
        stream(sc, 1.0 if u < 0.6 else 0.0, 1.0 - 0.6 * u)
        film(sc, u < 0.7)
        if u < 0.6:
            spray.emit_spray(int(round(20 * (1 - u) * PER_FRAME)))
        spray.step()
        drops.step()
        powder.set(3 + (POWDER_END - 3) * min(1.0, spray.landed / 3800))
        coil_glow(sc, 1.0 - u)
        shake(sc, u < 0.7)
        show_g(us="off" if u > 0.7 else "40 kHz", t=750 - 200 * u)
    cap = "The crucible runs empty; vibration and the coil off, the sealing rod down."
    sc.step(f"4/{n}", cap, 3.0, tail, hold=0.3, live=True)
    spray.clear()
    drops.clear()
    rod_lift(sc, 0.0)
    slot(sc, "powder")

    # ------------------------------------------------------------------ 5. the container onto the MiR
    cap = ("Closed again. The chamber's valve and the container's own valve are shut, so the powder comes off under "
           "argon; the flange clamp opens and the MiR comes back to the container.")
    show_g(us_on=False, t_on=False, p_on=False, o2=None, charge=None, cont="full, valves shut",
           arm="parked", mir="driving")

    def close_up(u):
        set_cut(sc, 1.0 - window(u, 0.0, 0.5))
        latch_fade(sc, window(u, 0.0, 0.5))
        lock_bolt(sc, 1.0 - window(u, 0.5, 1.0))             # vented: the bolt goes back
        set_gas(sc, 0.8 * (1.0 - window(u, 0.0, 0.5)))
        flange_clamp(sc, 1.0 - window(u, 0.5, 1.0))
    sc.step(f"5/{n}", cap, 1.6, close_up, hold=0.1, cam_to=CAM_CONT)
    sc.step(f"5/{n}", cap, mir.secs(x_cont, y_cont), mir.drive(x_cont, y_cont), hold=0.1)
    show_g(mir="at the rePowder")
    # model.py container_handle, model frame: taken at its outer end, clear of the open flange clamp's front half
    # (over the handle's inner 40 mm), level from the front and a little from the right; fingers close vertically
    handle = np.array([356.0, -94.0, 275.0])
    a_h = np.array([math.sin(math.radians(-15.0)), math.cos(math.radians(-15.0)), 0.0])
    grasp_h = P.tcp_frame(W(handle), a_h, 90.0)
    pre_h = grasp_h @ T((0, 0, -120))
    cap = ("The arm takes the container by its handle, lowers it off the outlet and carries it to the cradle on the "
           "MiR's cabinet. It goes next to the sieve shaker.")
    show_g(arm="container")
    # the fingers only open to 19 mm for the 12 mm bar: open wide, the upper one reaches the chamber valve's handle,
    # 27 mm over this one
    sc.step(f"5/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=pre_h), rb.grip_to(GRIP_CUP)), hold=0.05)
    sc.step(f"5/{n}", cap, 0.8, rb.line_to(grasp_h), hold=0.05)
    sc.step(f"5/{n}", cap, 0.4, rb.grip_to(GRIP_HANDLE), hold=0.05)
    rb.grasp(g("container"))
    sc.step(f"5/{n}", cap, 0.6, rb.line_to(T((0, 0, -20)) @ grasp_h), hold=0.05)
    sc.step(f"5/{n}", cap, 1.0, rb.line_to(T((0, -230, -20)) @ grasp_h), hold=0.05)
    _, off = rb.held
    seat_w = mir.world(mir.cradle_seat)
    # the container stands in the cradle, its base on the seat, its handle to the front, as it came out of the
    # rePowder: chapter 3 (alloy_print.py) takes it from there by the handle, level, from the front
    target = T(seat_w) @ R((0, 0, 1), CRADLE_TURN) @ T(-np.array([M.CHUTE_X, 0.0, M.CONT_Z[0]]))
    t_place = target @ inv(off)
    up_w = T((0, 0, 380)) @ rb.tcp_world()
    sc.step(f"5/{n}", cap, 1.0, rb.line_to(up_w), hold=0.05)
    sc.step(f"5/{n}", cap, 1.8, rb.joint_to(Tw=T((0, 0, 150)) @ t_place), hold=0.05, cam_to=CAM_CRADLE)
    sc.step(f"5/{n}", cap, 0.8, rb.line_to(t_place), hold=0.05,
            labels=[("powder container, under argon", tuple(seat_w + (0, 0, 260)), (0.70, 0.30))])
    sc.step(f"5/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("amr")
    sc.step(f"5/{n}", cap, 0.7, rb.line_to(t_place @ T((0, 0, -110))), hold=0.05)
    show_g(arm="parked", cont="on the MiR250, under argon")
    cap = "The arm parks, and the MiR250 lines up in front of the rePowder for the next leg: the AS 200 sieve shaker."
    sc.step(f"5/{n}", cap, 1.3, rb.joint_to(PARK), hold=0.2)
    show_g(mir="lining up")
    x_back = END_POSE[0] - 613.0                      # back off along the front, then an S-curve onto the hand-off spot
    sc.step(f"5/{n}", cap, mir.secs(x_back, y_park), mir.drive(x_back, y_park), hold=0.0)
    sc.step(f"5/{n}", cap, mir.secs(*END_POSE) + 0.6, mir.drive(*END_POSE), hold=0.2)
    show_g(mir="at the rePowder")
    b440 = next(iter(MIDI_BUILDS))
    cap = (f"How much powder: the four cups make about {four['under_63um_g']:.0f} g of the MIDI's 20-63 um cut, at "
           f"the Oct 27 run's 17 % under 63 um (DAL #219). The crucible takes much more: filled as on Oct 27, about "
           f"{full225['al_g']:.0f} g of Al ({full225['under_63um_g']:.0f} g of the cut), and the 400 cm³ one about "
           f"{full400['al_g']:.0f} g ({full400['under_63um_g']:.0f} g). A 440 g MIDI build then takes "
           f"{four['runs_per_build'][b440]}, {full225['runs_per_build'][b440]} or "
           f"{full400['runs_per_build'][b440]} runs.")
    sc.step(f"5/{n}", cap, 0.4, None, hold=6.5)
    sc.step(f"5/{n}", "Done: the powder, not yet sieved, is on the MiR250 in front of the rePowder. Next: the "
            "sieving cell and the printer.", 0.4, None, hold=2.0)
    if DEBUG:
        print("end pose", round(mir.x, 1), round(mir.y, 1), round(mir.yaw, 2), flush=True)
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    return finish(sc)


# ------------------------------------------------------------------------------------------------ the real footage
# What goes in at each slot: the lab's own runs (DAL #159, #219; the BYU VCL channel). File names are those of the
# parent session's fetch (FOOTAGE/manifest.json); `window` is seconds inside that file, `seconds` a photo's time on
# screen. None of it is Al-10Si: the captions say what it is.
MELT_SPEED = 2.0                  # the melt excerpts run at twice real time (Sterling, PR #318: "sped up a bit")
PLAN = [
    dict(beat="charge", file="nab_k7m2q9_four_rod_pieces_1079.886g.jpg", seconds=3.6,
         caption="The lab's own four charges, Oct 27 2026: four 630 bronze rod pieces, 1,079.886 g on the balance, "
                 "melted in one run (Gage Erickson, DAL #219). Bronze, not this chapter's Al-10Si."),
    dict(beat="melt", file="nab_melt1.mp4", window=(10.0, 15.0), speed=MELT_SPEED,
         caption="Real footage, Oct 27 2026, through the furnace port: the four bronze pieces stand round the sealing "
                 "rod and glow (youtu.be/2brsz-90seg, DAL #219). 630 bronze at 1300 °C, not Al-10Si."),
    dict(beat="melt", file="nab_melt2.mp4", window=(70.0, 77.0), speed=MELT_SPEED,
         caption="A few minutes on, the pieces sink into their own melt round the rod (2brsz-90seg, about 4:36; at "
                 "3:55 Gage says \"It's melting in right now\")."),
    dict(beat="melt", file="nab_melt3.mp4", window=(14.0, 18.5), speed=MELT_SPEED,
         caption="The charge fully molten, a bright pool round the sealing rod (2brsz-90seg, DAL #219)."),
    dict(beat="pour", file="mst2026_stream.mp4", window=(4.0, 11.0), crop=(0.283, 0.0, 0.818, 1.0),
         tag="Sterling Baird's MS&T 2026 talk",
         caption="Real footage, from Sterling Baird's MS&T 2026 talk (youtu.be/YmvaeqOQAU4, 4:58): a melt stream, a "
                 "line of drops, falls onto the tip of the vibrating plate and breaks up into a spray of droplets. The "
                 "talk doesn't name the alloy or the run."),
    dict(beat="pour", file="nab_pour1.mp4", window=(15.0, 22.5),
         caption="Real footage, Oct 27 2026, through the view port: the bronze jet lands on the tip of the W-coated "
                 "carbon-fibre plate and atomizes (2brsz-90seg). 91 % of the 1,080 g became usable powder (DAL #219)."),
    dict(beat="powder", file="nab_k7m2q9_jar_of_powder.jpg", seconds=3.0,
         caption="Real photo: the Oct 27 bronze powder as it came out of the atomizer, not yet sieved: lot k7m2q9 "
                 "(DAL #219). It is sieved in chapter 3."),
    dict(beat="powder", file="al4047_oct22_c3k0n5_bag_and_jar.jpg", seconds=3.0,
         caption="Real photo: the Oct 22 Al 4047 run, lot c3k0n5, 169 g in, as collected that day: a bag of "
                 "splats and a jar of powder (Ronnie Guymon, DAL #159)."),
]
BEATS = ("charge", "melt", "pour", "powder")       # round 8: the sieved jars moved to chapter 3, after the sieving
BADGE = (178, 34, 34)
KEEP = OUT / "footage"            # the excerpts and photos used, small, committed: splice() reads these when present


def manifest(root: Path) -> dict:
    """{file name: entry} from root/manifest.json ("clips" and "photos", or a plain list)."""
    path = root / "manifest.json"
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    items = raw if isinstance(raw, list) else [e for k in ("clips", "photos", "items", "files")
                                                for e in raw.get(k, []) if isinstance(e, dict)]
    out = {}
    for e in items:
        f = e.get("file") or e.get("path")
        if not f:
            continue
        p = Path(f) if Path(f).is_absolute() else root / f
        if p.exists():
            out[p.name] = dict(e, path=p)
    return out


def _date(e: dict) -> str:
    d = str(e.get("date", ""))
    try:
        y, m, dd = d.split("-")
        return f"{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(m) - 1]} " \
               f"{int(dd)} {y}"
    except (ValueError, IndexError):
        return d


def _alloy(e: dict) -> str:
    a = str(e.get("alloy", "")).lower()
    name = e["path"].name.lower()
    if "bronze" in a or name.startswith("nab"):
        return "630 bronze (NAB)"
    if "4047" in a or "4047" in name:
        return "Al 4047"
    if "6063" in a or "6063" in name or name.startswith("al"):
        return "Al 6063"
    return e.get("alloy", "")


def _fit(img: Image.Image, size) -> Image.Image:
    """`img` inside `size`, on a blurred, darkened copy of itself that fills the frame."""
    bg = ImageOps.fit(img, size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    fg = ImageOps.contain(img, size, Image.LANCZOS)
    bg.paste(fg, ((size[0] - fg.width) // 2, (size[1] - fg.height) // 2))
    return bg


def _side(real: Image.Image, model: Image.Image, size) -> Image.Image:
    """A portrait picture beside the model at the same moment: the model on the left, the real one on the right."""
    W_, H_ = size
    canvas = Image.new("RGB", size, (22, 24, 28))
    r = ImageOps.contain(real, (W_, H_), Image.LANCZOS)
    m = ImageOps.contain(model, (W_ - r.width - 30, H_), Image.LANCZOS)
    canvas.paste(m, (10, (H_ - m.height) // 2 - 20))
    canvas.paste(r, (W_ - r.width, (H_ - r.height) // 2))
    d = ImageDraw.Draw(canvas, "RGBA")
    f = scene.font(15 * H_ / 720, bold=True)
    for text, x, y in (("the model", 18, (H_ - m.height) // 2 - 20 + m.height - 34 * H_ / 720),
                       ("the lab", W_ - r.width + 10, 84 * H_ / 720)):
        w = d.textlength(text, font=f)
        d.rounded_rectangle((x, y, x + w + 16, y + 26 * H_ / 720), 5, fill=(255, 255, 255, 220))
        d.text((x + 8, y + 4 * H_ / 720), text, font=f, fill=(20, 20, 24))
    return canvas


def _clip(path: Path, t0: float, span: float, fps: int) -> list[Image.Image]:
    """Frames of a clip from t0 for span seconds at fps, as decoded (rotation applied, size kept)."""
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height:stream_side_data=rotation:format=duration", "-of", "json", str(path)],
                           capture_output=True, text=True).stdout
    info = json.loads(probe or "{}")
    st = (info.get("streams") or [{}])[0]
    w, h = int(st.get("width", 1280)), int(st.get("height", 720))
    rot = next((abs(int(float(sd.get("rotation", 0)))) for sd in st.get("side_data_list", []) if "rotation" in sd), 0)
    if rot in (90, 270):
        w, h = h, w
    dur = float(info.get("format", {}).get("duration", t0 + span))
    t0 = min(t0, max(0.0, dur - span))
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.2f}", "-t", f"{span:.2f}", "-i", str(path), "-an", "-vf",
           f"fps={fps},format=rgb24", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    buf = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(buf) // (w * h * 3)
    frames = [Image.frombuffer("RGB", (w, h), buf[i * w * h * 3:(i + 1) * w * h * 3], "raw", "RGB", 0, 1)
              for i in range(n)]
    return frames[:n - n % 3] if n > 3 else frames


def _photo(path: Path) -> Image.Image:
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def _push_in(img: Image.Image, n: int, k: float = 0.05) -> list[Image.Image]:
    """n frames of a slow push-in on img (k: how far)."""
    out = []
    for i in range(n):
        z = 1.0 - k * i / max(1, n - 1)
        w, h = img.width * z, img.height * z
        box = ((img.width - w) / 2, (img.height - h) / 2, (img.width + w) / 2, (img.height + h) / 2)
        out.append(img.resize(img.size, Image.BILINEAR, box=box))
    return out


def _dress(img: Image.Image, label: str, badge: str, caption: str, scale: float, size) -> Image.Image:
    """The chapter's title, step label and caption on a footage frame, plus a badge saying it is real."""
    img = img.convert("RGB")
    if img.size != tuple(size):
        img = img.resize(size, Image.LANCZOS)
    ns = SimpleNamespace(name=NAME, title=TITLE, label=label, gauges=[], labels=[], caption=" ".join(caption.split()))
    img = _OVERLAY(ns, img, scale, [])
    if scene.CLEAN:
        return img
    d = ImageDraw.Draw(img, "RGBA")
    s = max(scale, 0.80)
    fb = scene.font(15 * s, bold=True)
    w = d.textlength(badge, font=fb)
    d.rounded_rectangle((10 * s, 44 * s, 10 * s + w + 20 * s, 44 * s + 28 * s), 6 * s, fill=(*BADGE, 235))
    d.text((20 * s, 49 * s), badge, font=fb, fill=(255, 255, 255))
    return img


def _model_frame(frame: int, size) -> Image.Image:
    """Frame `frame` of the 3-D render."""
    buf = subprocess.run(["ffmpeg", "-v", "error", "-i", str(RAW_MP4), "-vf", f"select=eq(n\\,{max(0, frame)})",
                          "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return Image.frombuffer("RGB", size, buf[:size[0] * size[1] * 3], "raw", "RGB", 0, 1)


def clearance(rels=None) -> dict:
    """At each cup's release, where the 2F-85's fingers are: over the rim, in the filling cone, against the crucible's
    bore and the cups already seated. The movie's poses (`rels`: release_at's fractions of `descent`, as the movie
    found them), from the gripper's meshes (ur_arm). Written to out/alloy_atomize_clearance.json."""
    import ur_arm
    gfk = ur_arm.gripper_fk(GRIP_CUP)
    parts = ("left_finger_tip", "right_finger_tip", "left_finger", "right_finger", "left_inner_knuckle",
             "right_inner_knuckle", "left_knuckle", "right_knuckle")
    pts = {p: np.vstack([m.points for m, _, _ in lst]) for p, lst in ur_arm.gripper_meshes().items() if p in parts}
    top_seated = cup_seat(0)[2] + C.SLUG_L
    cone_top = M.BODY_TOP - 4.0

    def cone_r(z):                                  # the top insulation's bore: the lip, then the filling cone
        return np.where(z < M.RIM + 12.0, M.CRUCIBLE_ID / 2 + (z - M.RIM) / 6.0,
                        M.CRUCIBLE_ID / 2 + 2.0 + (z - M.RIM - 12.0) * (50.0 - M.CRUCIBLE_ID / 2 - 2.0)
                        / (cone_top - M.RIM - 12.0))
    rows = []
    for k in range(N_CUPS):
        rel = 0.78 if rels is None else rels[k]
        at = pose_path(descent(k), rel)
        spin = (90.0 - CUP_ANGLES[k] + 90.0) % 180.0 - 90.0
        pick = A.down(np.array([0.0, 0.0, C.SLUG_L - GRIP_AT]), spin=spin)      # the grasp, in the cup's frame
        tool0 = at @ pick @ T((0, 0, -ur_arm.TCP_MM))
        Wp = np.vstack([(tool0 @ gfk[p] @ np.c_[P_, np.ones(len(P_))].T).T[:, :3] for p, P_ in pts.items()])
        r = np.hypot(Wp[:, 0], Wp[:, 1])
        below = Wp[:, 2] < M.RIM
        in_cone = (Wp[:, 2] >= M.RIM) & (Wp[:, 2] < cone_top)
        over = []
        for j in range(k):
            s_ = cup_seat(j)
            on = np.hypot(Wp[:, 0] - s_[0], Wp[:, 1] - s_[1]) < C.STOCK_D / 2
            if on.any():
                over.append(dict(cup=j + 1, gap_mm=round(float(Wp[on, 2].min() - top_seated), 1)))
        rows.append(dict(cup=k + 1, angle_deg=CUP_ANGLES[k], descent_fraction=round(float(rel), 3),
                         foot_under_rim_mm=round(float(M.RIM - at[2, 3]), 1),
                         fingers_lowest_above_rim_mm=round(float(Wp[:, 2].min() - M.RIM), 1),
                         into_crucible_wall_mm=round(float(max(0.0, (r[below] - M.CRUCIBLE_ID / 2).max())), 1)
                         if below.any() else 0.0,
                         closest_to_filling_cone_mm=round(float((cone_r(Wp[in_cone, 2]) - r[in_cone]).min()), 1)
                         if in_cone.any() else None,
                         over_seated_cups=over))
    return dict(cups=rows, seated_cup_tops_below_rim_mm=round(float(M.RIM - top_seated), 1),
                note="2F-85 at closure GRIP_CUP, holding the cup GRIP_AT = 8 mm under its top, at the pose where the "
                     "movie lets go: as far down `descent` as the collision checker finds the gripper clear "
                     "(release_at). Below the rim the fingers' outer corners don't fit the 57.1 mm bore, so the arm "
                     "lets go with them over it and the cup slides the rest of the way. "
                     "closest_to_filling_cone_mm: the fingers' least clearance to the top insulation's bore (negative: "
                     "into it); into_crucible_wall_mm: how far any finger point under the rim reaches past the bore.")


def keep_footage(src: Path = FOOTAGE) -> int:
    """Copy what PLAN uses from `src` into out/footage/, small: each clip cut to its window (720 px tall, CRF 28, no
    sound), each photo at 1600 px, plus a manifest with the credits. Returns the number of files."""
    have = manifest(src)
    if not have:
        return 0
    KEEP.mkdir(parents=True, exist_ok=True)
    kept = []
    for item in PLAN:
        e = have.get(item["file"])
        if e is None:
            print("footage missing:", item["file"], flush=True)
            continue
        dst = KEEP / item["file"]
        entry = {k: v for k, v in e.items() if k != "path"}
        entry["file"] = dst.name
        if "window" in item:
            t0, t1 = item["window"]
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t0:.2f}", "-t", f"{t1 - t0:.2f}", "-i",
                            str(e["path"]), "-an", "-vf", "scale=-2:'min(720,ih)'", "-c:v", "libx264", "-crf", "28",
                            "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)], check=True)
            entry.update(excerpt_of=e["path"].name, excerpt_window_s=[t0, t1])
        else:
            im = _photo(e["path"])
            im.thumbnail((1600, 1600), Image.LANCZOS)
            im.save(dst, quality=84, optimize=True)
        kept.append(entry)
    (KEEP / "manifest.json").write_text(json.dumps(dict(
        note="The excerpts and photos alloy_atomize.py cuts into chapter 2, kept small: clips cut to the window "
             "used (excerpt_window_s, seconds in the parent's fetch), 720 px tall, no sound; photos at 1600 px. "
             "All the lab's own (BYU VCL channel, DAL #159 and #219); credits per file.",
        files=kept), indent=1, ensure_ascii=False) + "\n")
    return len(kept)


def splice() -> str:
    """Cut the footage in PLAN into the last 3-D render at its slots, and write the final MP4, GIF and JSON. Reads
    out/footage/ (the kept excerpts) if it has them, else FOOTAGE; with neither, writes the render out as it is."""
    meta = json.loads(RAW_JSON.read_text())
    size, fps = tuple(meta["size"]), meta["fps"]
    gsize = tuple(meta.get("gif_size", scene.GIF_SIZE))
    gstep = max(1, round(fps / meta.get("gif_fps", scene.GIF_FPS)))
    kept = KEEP / "manifest.json"
    if kept.exists():
        have = {}
        for e in json.loads(kept.read_text())["files"]:
            if (KEEP / e["file"]).exists():
                have[e["file"]] = dict(e, path=KEEP / e["file"], window_offset=e.get("excerpt_window_s", [0, 0])[0])
    else:
        have = manifest(FOOTAGE)
    inserts = []                                    # (slot, MP4 frames, GIF frames, sub-steps)
    for sl in meta.get("slots", []):
        frames, gifs, subs = [], [], []
        model = None
        for item in (it for it in PLAN if it["beat"] == sl["beat"]):
            e = have.get(item["file"])
            if e is None:
                continue
            video = "window" in item
            if video:
                t0, t1 = item["window"]
                off = e.get("window_offset", 0.0)
                raw = _clip(e["path"], t0 - off, t1 - t0, max(1, int(round(fps / item.get("speed", 1.0)))))
                if item.get("crop"):                # (x0, y0, x1, y1), fractions: a talk's black bar and webcam inset
                    cx0, cy0, cx1, cy1 = item["crop"]
                    raw = [f.crop((round(cx0 * f.width), round(cy0 * f.height), round(cx1 * f.width),
                                   round(cy1 * f.height))) for f in raw]
            else:
                pic = _photo(e["path"])
                raw = None
            portrait = (raw[0].height > raw[0].width) if video and raw else (not video and pic.height > pic.width)
            if portrait and model is None:
                png = Path(sl.get("model_png", ""))
                model = (Image.open(png).convert("RGB") if sl.get("model_png") and png.exists()
                         else _model_frame(sl["frame"] - 1, size))
            if video:
                pics = [(_side(f, model, size) if portrait else _fit(f, size)) for f in raw]
            else:
                still = _side(pic, model, size) if portrait else _fit(pic, size)
                pics = _push_in(still, int(round(item["seconds"] * fps / 3)) * 3, 0.04)
            if not pics:
                continue
            sp_ = item.get("speed", 1.0)
            badge = " · ".join(x for x in ("REAL FOOTAGE" if video else "REAL PHOTO",
                                            *((item["tag"],) if item.get("tag") else (_alloy(e), _date(e))),
                                            f"{sp_:g}× SPEED" if sp_ != 1.0 else "") if x)
            k0 = len(frames)
            frames += [np.asarray(_dress(p, sl["label"], badge, item["caption"], 1.0, size)) for p in pics]
            gifs += [_dress(p, sl["label"], badge, item["caption"], gsize[0] / size[0], gsize).convert("RGB")
                     for p in pics[::gstep]]
            subs.append(dict(label=sl["label"], caption=" ".join(item["caption"].split()), start_frame=k0,
                             end_frame=len(frames) - 1,
                             footage=dict(file=item["file"], source=e.get("source"), date=e.get("date"),
                                          alloy=_alloy(e), window_s=item.get("window"), speed=item.get("speed", 1.0))))
        if frames:
            inserts.append((sl, frames, gifs, subs))
    # the MP4: the render's frames, with the footage at each slot
    enc = scene.encoder(OUT / "mp4" / f"{NAME}.mp4", size, crf=21)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(RAW_MP4), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    nbytes = size[0] * size[1] * 3
    pending = {sl["frame"]: (frames, subs) for sl, frames, _, subs in inserts}
    placed, k, written = [], 0, 0

    def put(frames, subs):
        nonlocal written
        for f in frames:
            enc.stdin.write(np.ascontiguousarray(f).tobytes())
        placed.extend(dict(s_, start_frame=s_["start_frame"] + written, end_frame=s_["end_frame"] + written)
                      for s_ in subs)
        written += len(frames)
    while True:
        if k in pending:
            put(*pending.pop(k))
        buf = dec.stdout.read(nbytes)
        if len(buf) < nbytes:
            break
        enc.stdin.write(buf)
        written += 1
        k += 1
    for f_at in sorted(pending):                    # slots past the render's last frame
        put(*pending[f_at])
    enc.stdin.close()
    enc.wait()
    dec.wait()
    # the JSON: each 3-D sub-step moved on by the footage before it; the footage's own sub-steps in between
    ins = sorted((sl["frame"], len(fr)) for sl, fr, _, _ in inserts)
    out_subs = []
    for sub in meta["substeps"]:
        sh = sum(nf for f0, nf in ins if f0 <= sub["start_frame"])
        out_subs.append(dict(sub, start_frame=sub["start_frame"] + sh, end_frame=sub["end_frame"] + sh))
    out_subs = sorted(out_subs + placed, key=lambda s_: s_["start_frame"])
    meta_out = {k_: v for k_, v in meta.items() if k_ not in ("slots", "gif_frames", "gif_fps", "gif_size")}
    meta_out.update(n_frames=written, substeps=out_subs,
                    footage=[dict(beat=sl["beat"], seconds=round(len(fr) / fps, 1),
                                  files=[s_["footage"]["file"] for s_ in subs]) for sl, fr, _, subs in inserts])
    (OUT / f"{NAME}.json").write_text(json.dumps(meta_out, indent=1, ensure_ascii=False, default=str) + "\n")
    # the GIF: the render's frames, with the footage's at each slot
    gat = {}
    for sl, _, gifs, _ in inserts:
        gat.setdefault(sl["gif"], []).extend(gifs)
    gframes = []
    for i, pth in enumerate(sorted(RAW_GIF.glob("*.png"))):
        gframes += gat.pop(i, [])
        gframes.append(Image.open(pth).convert("RGB"))
    for i in sorted(gat):
        gframes += gat[i]
    gif = OUT / f"{NAME}.gif"
    if gframes:
        scene.write_gif(gframes, gif)
        # the footage is noisy, real video: if the GIF is still over 5 MB, drop to 4 fps (every fifth frame out),
        # then to 560 x 315
        fps0 = scene.GIF_FPS
        for shrink in (False, True):
            if gif.stat().st_size <= 5.0e6:
                break
            scene.GIF_FPS = 4
            frames2 = [f for i, f in enumerate(gframes) if i % 5 != 4]
            if shrink:
                frames2 = [f.resize((560, 315), Image.LANCZOS) for f in frames2]
            scene.write_gif(frames2, gif)
        scene.GIF_FPS = fps0
    n_ft = sum(len(fr) for _, fr, _, _ in inserts)
    info = (f"{NAME}: {written} frames, {written / fps:.1f} s, {n_ft / fps:.1f} s of it the lab's footage "
            f"({sum(len(s_) for *_, s_ in inserts)} pieces); gif {len(gframes)} frames "
            f"{gif.stat().st_size / 1e6 if gif.exists() else 0:.2f} MB")
    print(info, flush=True)
    return info


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    sums = powder_sums()
    (OUT / f"{NAME}_powder.json").write_text(json.dumps(sums, indent=1, ensure_ascii=False) + "\n")
    if arg == "splice":
        splice()
    elif arg == "merge":
        merge()
    elif arg == "keep":
        print("kept", keep_footage(), "files in", KEEP)
    elif arg == "tongclear":
        cl = tong_clearance(int(os.environ.get("TONG_N", "14")))
        (OUT / f"{NAME}_clearance.json").write_text(json.dumps(cl, indent=1) + "\n")
        print(json.dumps(cl, indent=1))
    elif arg == "clearance":
        cl = clearance()
        (OUT / f"{NAME}_clearance.json").write_text(json.dumps(cl, indent=1) + "\n")
        print(json.dumps(cl, indent=1))
    elif arg == "powder":
        print(json.dumps(sums, indent=1, ensure_ascii=False))
    else:
        movie()
