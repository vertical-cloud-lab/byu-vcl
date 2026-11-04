"""Chapter 2 of the alloy route, atomize: the MiR250 brings the four charged 5N Al cups from the VLM to the rePowder,
the UR10e loads them into the crucible round the sealing rod, and the machine melts and atomizes them; the arm takes
the powder container off onto the MiR (#303, rounds 4 and 5). Clips and photos of the lab's own runs are cut in where
the animation reaches the same moment: the charge melting, the stream on the plate, the powder, the sieved powder.

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

The scene is ``line.py``'s layout, as ``alloy_workflow.py`` builds it (the VLM, the line's machines), except that the
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
from scene import FPS, OUT, PREVIEW, Scene, T, R, S, ease, mix, window  # noqa: E402

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
GRIP_KNOB = 0.52                      # the lid's knob, 41 mm across
GRIP_HANDLE = 0.86                    # the container's 12 mm handle bar
HOOD_OPEN = 110.0                     # degrees the lid swings up (#124's training animation)
MIR_SPEED = 1500.0                    # mm/s, as alloy_workflow.py
PARK = np.radians(A.PARK_DEG)
CARRIER_AT = (A.BUFFER_LOCAL[0], A.BUFFER_LOCAL[1], P.AMR_TOP - 20.0)    # where chapter 1 puts the cup carrier
CRADLE_AT = (280.0, 10.0, P.AMR_TOP - 20.0)                           # the container's cradle, beside the arm
CRADLE_H = 150.0
END_POSE = (A.REPOWDER_AT[0] + 288.0, -2230.0)     # the hand-off to chapter 3 (sieve, print): MiR250 centre, yaw 0,
                                                   # square to the container's axis, 41 mm off the view port's flange

RAW = OUT / "clean"                                # git-ignored: the 3-D render before the footage goes in
RAW_MP4, RAW_JSON, RAW_GIF = RAW / f"{NAME}_3d.mp4", RAW / f"{NAME}_3d.json", RAW / f"{NAME}_3d_gif"
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
        grp = g(m["group"])
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
    """A MiR250 with its cabinet and a UR10e (alloy_workflow.Mir), driving on (x, y, yaw), with chapter 1's cup
    carrier and a cradle for the powder container."""

    def __init__(self, sc):
        self.sc = sc
        for name, (mesh, col) in P.mir250().items():
            kw = dict(ambient=0.8) if "light" in name else {}
            sc.add(f"amr/{name}", mesh, col, "amr", **kw)
        carrier, seats = C.carrier()
        sc.add("amr/cup carrier", carrier.translate(CARRIER_AT, inplace=False), P.RACK_C, "amr")
        self.seats = [np.array(s, float) + CARRIER_AT for s in seats]
        cx, cy, cz = CRADLE_AT
        post = pv.Cylinder(center=(cx, cy, cz + CRADLE_H / 2), direction=(0, 0, 1), radius=16,
                           height=CRADLE_H).triangulate()
        foot = pv.Box(bounds=(cx - 50, cx + 50, cy - 50, cy + 50, cz, cz + 8)).triangulate()
        ring = C.lathe([(M.CONT_R + 1.0, 0), (M.CONT_R + 7.0, 0), (M.CONT_R + 7.0, 40), (M.CONT_R + 1.0, 40)],
                       res=64).translate((cx, cy, cz + CRADLE_H), inplace=False)
        floor = pv.Cylinder(center=(cx, cy, cz + CRADLE_H + 1.5), direction=(0, 0, 1), radius=M.CONT_R + 7.0,
                            height=3.0, resolution=64).triangulate()
        sc.add("amr/cradle", post.merge(foot).merge(ring).merge(floor), (0.30, 0.32, 0.36), "amr")
        self.cradle_seat = np.array([cx, cy, cz + CRADLE_H + 3.0])
        self.x, self.y, self.yaw = 0.0, 0.0, 0.0
        self.rb = RB.Robot(sc, A.ROBOT, "amr", T((*A.ARM_LOCAL, P.AMR_TOP)), q0=A.PARK_DEG)

    def set(self, x, y, yaw=0.0):
        self.x, self.y, self.yaw = x, y, yaw
        self.sc.gmat["amr"] = T((x, y, 0)) @ R((0, 0, 1), yaw)
        if self.rb.held is not None:
            self.rb.set()

    def drive(self, x1, y1):
        """Along a smoothstep S-curve to (x1, y1), its long axis on the tangent (it drives along its length)."""
        x0, y0 = self.x, self.y

        def up(u):
            x = x0 + (x1 - x0) * u
            y = y0 + (y1 - y0) * (3 * u * u - 2 * u ** 3)
            dydx = (y1 - y0) * (6 * u - 6 * u * u) / (x1 - x0) if abs(x1 - x0) > 1 else 0.0
            self.set(x, y, math.degrees(math.atan(dydx)))
        return up

    def secs(self, x1, y1=None):
        d = math.hypot(x1 - self.x, (y1 if y1 is not None else self.y) - self.y)
        return max(1.2, d / MIR_SPEED + 0.8)

    def world(self, p):
        return (self.sc.world("amr") @ np.r_[p, 1.0])[:3]


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


def tip_in_path(k):
    """Cup poses (model frame) from above the open furnace down past the rod's adapter into the bore (#222's tight
    spot: ~45 mm in, the top just under the adapter), then on its own to its seat. Returns (held, slide)."""
    rim, ad = M.RIM, M.RIM + M.ROD_ADAPTER_ABOVE_RIM
    held = [cup_pose(k, 30.0, rim + 150.0, 0.0),
            cup_pose(k, 22.0, rim + 40.0, 0.0),               # beside the adapter, above the bore
            cup_pose(k, 17.6, rim + 4.0, 4.0),                # foot into the bore by the rod, top leaning out
            cup_pose(k, 15.9, ad - C.SLUG_L * math.cos(math.radians(4.1)) - 0.3, 4.1)]   # the tight spot
    seat = cup_seat(k)
    slide = [held[-1], cup_pose(k, CUP_R, seat[2] + 14.0, 0.0), cup_pose(k, CUP_R, seat[2], 0.0)]
    return held, slide


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


# ------------------------------------------------------------------------------------------------ the movie
def build():
    data = lab.meshes()
    idata = tour.load(["glovebox"])
    sc = Scene(NAME, TITLE, mp4=False)
    if not PREVIEW:                         # the 3-D render goes to out/clean/ first; splice() writes the final MP4
        RAW.mkdir(parents=True, exist_ok=True)
        sc.mp4, sc.mp4_path = scene.encoder(RAW_MP4, sc.size, crf=17), RAW_MP4
    sc.slots = []                           # where the real footage goes: (beat, MP4 frame, GIF frame, step label)
    sc.intro = 0.8
    L = A.Lab(sc, data, robot=False)
    L.show_gauges = False
    L.skin(0.0)(1.0)
    L.apply_state()
    sc.add("line floor", pv.Plane(center=(1200, -900, -1.5), direction=(0, 0, 1), i_size=34000, j_size=18000),
           A.FLOOR_C, "floor", ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
    inst, ents = idata["glovebox"]
    tour.Rig(sc, inst, ents, "glovebox:", at=line.place_floor(inst.bbox(), line.LINE["glovebox"]))
    ents = line.aconity_entries()
    pts = np.vstack([e["mesh"].points for e in ents.values() if e["mesh"].n_points])
    lo, hi = pts.min(0), pts.max(0)
    for n, e in ents.items():
        sc.add(n, e["mesh"], e["color"], "aconity", opacity=e["opacity"])
    sc.gmat["aconity"] = line.place_floor((lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]), line.LINE["aconity"])
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
    add_cups(sc, mir)
    hood(sc, 0.0)
    flange_clamp(sc, 1.0)
    return sc, L, mir, pool, powder, spray, drops, vent


def fast_forward(sc, first: int):
    """Re-render only from sub-step `first` on: earlier frames are counted but not drawn (ATOMIZE_TAIL), so a changed
    ending can be spliced onto an earlier render (see the notes)."""
    snap = sc.snap

    def maybe(n=1):
        if len(sc.substeps) < first:
            sc.want_still = False
            sc.n += n
            return None
        return snap(n)
    sc.snap = maybe


def slot(sc, beat: str):
    """Mark where the real footage for `beat` goes: the frame the next sub-step would start on. The view at that
    moment is kept without its text, for footage shown beside the model."""
    if PREVIEW or len(sc.substeps) < TAIL:
        return
    png = RAW / f"{NAME}_slot_{beat}.png"
    Image.fromarray(sc.render_base()).save(png)
    sc.slots.append(dict(beat=beat, frame=sc.n, gif=len(sc.gif_frames), label=sc.label, model_png=str(png)))


def finish(sc):
    """Save the 3-D render to out/clean/ (its MP4, its GIF frames as PNGs, its JSON with the footage slots), then
    splice the footage in."""
    if PREVIEW:
        return sc.save()
    if RAW_GIF.exists():
        shutil.rmtree(RAW_GIF)
    RAW_GIF.mkdir(parents=True)
    for i, im in enumerate(sc.gif_frames):
        im.save(RAW_GIF / f"{i:05d}.png", compress_level=1)
    n_gif = len(sc.gif_frames)
    sc.gif_frames, sc.gif = [], False
    info = sc.save()                                   # the MP4 in RAW, the still and out/alloy_atomize.json
    meta = json.loads((OUT / f"{NAME}.json").read_text())
    meta.update(slots=sc.slots, gif_frames=n_gif, gif_fps=scene.GIF_FPS, gif_size=list(scene.GIF_SIZE))
    RAW_JSON.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(info, flush=True)
    return splice()


def movie():
    sc, L, mir, pool, powder, spray, drops, vent = build()
    if TAIL:
        fast_forward(sc, TAIL)
    rb = mir.rb
    n = 5
    m_cup = RUN["charge_g"]
    ps = powder_sums()
    four, full225, full400 = ps["charges"]
    st = dict(pf=0.0, pc=0.0, o2=None, t=24.0, us="off")

    def show_g(**kw):
        st.update(kw)
        rows = {"Arm": st.get("arm"), "MiR250": st.get("mir"), "Charge": st.get("charge"),
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
    CAM_WIDE = [(-1500, -9200, 4300), (-1900, -1500, 900), (0, 0, 1)]
    CAM_LOAD = cam((-1000, -2050, 2150), (-20, -300, 1200))
    CAM_TOP = cam((-480, -560, 1700), (0, 10, 1290))
    CAM_SEC = cam((-330, -820, 1430), (5, 0, 1262))
    CAM_POUR = cam((-620, -1720, 1140), (10, 0, 970))
    CAM_CHAMBER = cam((-900, -2200, 1000), (110, 0, 760))
    CAM_CONT = cam((1450, -1650, 1250), (250, -300, 520))
    CAM_CRADLE = cam((1900, -2500, 1750), (150, -560, 760))

    show_g(arm="UR10e on MiR250, parked", mir="at the VLM's opening",
           charge=f"{N_CUPS} × 5N Al cup, Si, {m_cup:.1f} g")
    sc.cam = list(CAM_WIDE)
    # ------------------------------------------------------------------ 1. drive over
    cap = (f"From the VLM to the atomizer: the MiR250 carries the four charged 5N Al cups, {m_cup:.1f} g of Al-10Si "
           f"(Si powder under each plug), to the AMAZEMET rePowder. Four charges is how the lab loads the crucible; "
           f"its own Al runs were 169-180 g (DAL #159).")
    lbl = [("AMAZEMET rePowder atomizer", tuple(W((250, 0, 1700))), (0.16, 0.24)),
           ("4 charged Al cups", tuple(mir.world((-300, -150, 1110))), (0.62, 0.30)),
           ("Kardex VLM", (0, -1700, 2700), (0.80, 0.16))]
    sc.step(f"1/{n}", cap, 1.0, None, hold=1.0, labels=lbl)
    show_g(mir="driving")
    sc.step(f"1/{n}", cap, mir.secs(x_load, y_park), mir.drive(x_load, y_park), hold=0.2, cam_to=CAM_LOAD,
            labels=[("AMAZEMET rePowder atomizer", tuple(W((250, 0, 1700))), (0.16, 0.24))])
    show_g(mir="at the rePowder")

    # ------------------------------------------------------------------ 2. lid open, cups in, lid shut
    knob = np.array([(90 + 131) / 2, -20.0, 1470.0])          # the lid's knob (model.py hood_knob), model frame
    grasp_k = P.tcp_frame(W(knob), (0, 1, 0), 0.0)            # level, from the front; fingers close along x
    pre_k = P.tcp_frame(W(knob + (0, -110, 0)), (0, 1, 0), 0.0)
    cap = ("The sealing rod is already fitted and its lever down over the adapter: rod first, then the metal (GU500 "
           "manual, #222). The arm takes the lid's knob and swings the lid up about its hinge, to the left.")
    show_g(arm="lid")
    sc.step(f"2/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=pre_k), rb.grip_to(0.0)), hold=0.05,
            labels=[("lid knob", tuple(W(knob + (0, 0, 30))), (0.70, 0.22)),
                    ("sealing-rod lever", tuple(W((80, 0, 1400))), (0.74, 0.46))])
    sc.step(f"2/{n}", cap, 0.8, rb.line_to(grasp_k), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_KNOB), hold=0.05)
    hinge_w = W(M.HINGE)
    arc = [R((0, 1, 0), -d, hinge_w) @ grasp_k for d in np.linspace(0, HOOD_OPEN, 12)]

    lid = follow(rb, arc)

    def lid_up(u):
        lid(u)
        hood(sc, HOOD_OPEN * u)
    sc.step(f"2/{n}", cap, 2.2, lid_up, hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    away = R((0, 1, 0), -HOOD_OPEN, hinge_w) @ pre_k
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(away), hold=0.05)

    for k in range(N_CUPS):
        held_w, slide_w = tip_in_path(k)
        seat_w = [T(RP) @ Mx for Mx in held_w]
        slide_world = [T(RP) @ Mx for Mx in slide_w]
        cup_w = sc.world(f"cup{k}")
        top = cup_w[:3, 3] + np.array([0, 0, C.SLUG_L - 13.0])
        spin = (90.0 - CUP_ANGLES[k] + 90.0) % 180.0 - 90.0     # fingers along the cup's tangent (either way round)
        g_pick = A.down(top, spin=spin)
        f = 1.0 if k == 0 else 0.7                               # the first one at full speed, the rest quicker
        if k == 0:
            cap = (f"Cup 1 of {N_CUPS} out of the carrier and over the open crucible. Past the rod's adapter a 3/4 in "
                   "cup only goes in tipped, foot by the rod and top leaning away: #222 finds -0.09 mm in the scaled "
                   "drawing, too close to call, so try one first. Let go below the adapter; it slides to the floor "
                   "cone, plug up.")
        else:
            cap = (f"Cup {k + 1} of {N_CUPS}, the same way, at #222's next place round the rod. The places are 75° "
                   f"apart and clear of the sealing-rod lever; neighbours stand {CUP_GAP:.1f} mm apart, and a cup "
                   f"has {RADIAL_ROOM:.1f} mm between the rod and the wall.")
        show_g(arm=f"cup {k + 1}: carrier to crucible")
        sc.step(f"2/{n}", cap, 1.4 * f, RB.both(rb.joint_to(Tw=A.down(top + (0, 0, 110), spin=spin)),
                                               rb.grip_to(0.0)), hold=0.05, cam_to=CAM_LOAD if k == 0 else None)
        sc.step(f"2/{n}", cap, 0.7 * f, rb.line_to(g_pick), hold=0.05)
        sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_CUP), hold=0.05)
        rb.grasp(f"cup{k}")
        _, off = rb.held
        tcp_of = [Mx @ inv(off) for Mx in seat_w]
        lift = T((0, 0, 140)) @ rb.tcp_world()
        sc.step(f"2/{n}", cap, 0.6 * f, rb.line_to(lift), hold=0.05)
        sc.step(f"2/{n}", cap, 1.4 * f, rb.joint_to(Tw=tcp_of[0]), hold=0.05, cam_to=CAM_TOP if k == 0 else None)
        go = follow(rb, tcp_of)
        sc.step(f"2/{n}", cap, 2.4 * f, go, hold=0.05,
                labels=[("rod adapter", tuple(W((0, 0, M.RIM + 40))), (0.10, 0.30)),
                        ("crucible, 57 mm bore", tuple(W((-26, 0, M.RIM - 6))), (0.10, 0.62))] if k == 0 else ())
        sc.step(f"2/{n}", cap, 0.3, rb.grip_to(0.0), hold=0.0)
        rb.release("rp")
        cup_g = f"cup{k}"

        def slide_down(u, cup_g=cup_g, slide_world=slide_world):
            sc.gmat[cup_g] = T(-RP) @ pose_path(slide_world, u)
        up_tcp = T((0, 0, 160)) @ rb.tcp_world()
        sc.step(f"2/{n}", cap, 0.6, RB.both(slide_down, rb.line_to(up_tcp)), hold=0.1)
        if DEBUG:
            print("cup", k, "world", np.round(sc.world(cup_g)[:3, 3] - RP, 1), "seat", np.round(cup_seat(k), 1),
                  "parent", sc.parent.get(cup_g), flush=True)
    cap = (f"All four cups stand round the rod, plug and vent up, {CUP_GAP:.1f} mm apart: {m_cup:.1f} g, about the "
           "size of the lab's own Al runs. The crucible could take far more metal than the cups bring.")
    show_g(arm="lid", charge=f"in the crucible, {m_cup:.1f} g")
    lid_open_grasp = R((0, 1, 0), -HOOD_OPEN, hinge_w) @ grasp_k
    sc.step(f"2/{n}", cap, 1.4, rb.joint_to(Tw=R((0, 1, 0), -HOOD_OPEN, hinge_w) @ pre_k), hold=0.05,
            cam_to=CAM_LOAD)
    CAM_DOWN = cam((-22, -80, 1610), (0, 2, 1262))            # down into the open crucible
    sc.step(f"2/{n}", cap, 1.3, None, hold=1.8, cam_to=CAM_DOWN,
            labels=[("4 cups round the sealing rod", tuple(W(cup_seat(2) + (0, 0, C.SLUG_L))), (0.70, 0.30)),
                    (f"cup tops {M.RIM - cup_seat(1)[2] - C.SLUG_L:.0f} mm under the rim",
                     tuple(W(cup_seat(1) + (0, 0, C.SLUG_L))), (0.70, 0.62))])
    slot(sc, "charge")
    cap = "The arm swings the lid shut, then the MiR backs off along the front so the window stays clear."
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(lid_open_grasp), hold=0.05, cam_to=CAM_LOAD)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_KNOB), hold=0.05)
    lid_dn = follow(rb, arc[::-1])

    def lid_down(u):
        lid_dn(u)
        hood(sc, HOOD_OPEN * (1 - u))
    sc.step(f"2/{n}", cap, 2.0, lid_down, hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    sc.step(f"2/{n}", cap, 0.6, rb.line_to(pre_k), hold=0.05)
    sc.step(f"2/{n}", cap, 1.2, rb.joint_to(PARK), hold=0.05)
    show_g(arm="parked", mir="waiting beside it")
    sc.step(f"2/{n}", cap, mir.secs(x_wait), mir.drive(x_wait, y_park), hold=0.1, cam_to=CAM_SEC)

    # ------------------------------------------------------------------ 3. gas wash, heat, melt
    back = [k for k in range(N_CUPS) if math.sin(math.radians(CUP_ANGLES[k])) > 0]
    cap = ("Cut open at the furnace axis; the two back cups are cut through their own axes. Three cycles of pumping "
           "down to 4×10⁻¹ mbar and back-filling with 5N argon take the oxygen under 50 ppm. On each "
           "pump-down the air under the plugs leaves through their 1/16 in vents (#104).")
    vents = [cup_seat(k) + (0, 0, C.SLUG_L - C.PLUG_SEAT + 1.0) for k in range(N_CUPS)]
    show_g(p_abs=1013.0, o2=2.1e5)

    def cut_open(u):
        set_cut(sc, window(u, 0.0, 0.6))
    k0 = back[0]
    sc.step(f"3/{n}", cap, 1.5, cut_open, hold=0.2,
            labels=[("vented plug, 5N Al", tuple(W(vents[k0]) + (0, 4, 1)), (0.08, 0.26)),
                    ("Si powder under it", tuple(W(cup_seat(k0) + (0, 3, 22))), (0.08, 0.56))])
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
        set_gas(sc, 0.8 * (1.0 - window(u, 0.0, 0.5)))
        flange_clamp(sc, 1.0 - window(u, 0.5, 1.0))
    sc.step(f"5/{n}", cap, 1.6, close_up, hold=0.1, cam_to=CAM_CONT)
    sc.step(f"5/{n}", cap, mir.secs(x_cont), mir.drive(x_cont, y_park), hold=0.1)
    show_g(mir="at the rePowder")
    handle = np.array([(284 + 373) / 2, -94.0, 275.0])           # model.py container_handle, model frame
    grasp_h = P.tcp_frame(W(handle), (0, 1, 0), 90.0)            # level, from the front; fingers close vertically
    pre_h = P.tcp_frame(W(handle + (0, -120, 0)), (0, 1, 0), 90.0)
    cap = ("The arm takes the container by its handle, lowers it off the outlet and carries it to the cradle on the "
           "MiR's cabinet. It goes next to the sieve shaker.")
    show_g(arm="container")
    sc.step(f"5/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=pre_h), rb.grip_to(0.0)), hold=0.05)
    sc.step(f"5/{n}", cap, 0.8, rb.line_to(grasp_h), hold=0.05)
    sc.step(f"5/{n}", cap, 0.4, rb.grip_to(GRIP_HANDLE), hold=0.05)
    rb.grasp(g("container"))
    sc.step(f"5/{n}", cap, 0.6, rb.line_to(T((0, 0, -20)) @ grasp_h), hold=0.05)
    sc.step(f"5/{n}", cap, 1.0, rb.line_to(T((0, -170, -20)) @ grasp_h), hold=0.05)
    _, off = rb.held
    seat_w = mir.world(mir.cradle_seat)
    # the container stands in the cradle, its base on the seat, turned half round so the handle faces the arm
    target = T(seat_w) @ R((0, 0, 1), 180.0) @ T(-np.array([M.CHUTE_X, 0.0, M.CONT_Z[0]]))
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
    slot(sc, "sieved")
    sc.step(f"5/{n}", "Done: the powder is on the MiR250, in front of the rePowder. Next: the AS 200 sieve shaker and "
            "the printer.", 0.4, None, hold=2.0)
    if DEBUG:
        print("end pose", round(mir.x, 1), round(mir.y, 1), round(mir.yaw, 2), flush=True)
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    return finish(sc)


# ------------------------------------------------------------------------------------------------ the real footage
# What goes in at each slot: the lab's own runs (DAL #159, #219; the BYU VCL channel). File names are those of the
# parent session's fetch (FOOTAGE/manifest.json); `window` is seconds inside that file, `seconds` a photo's time on
# screen. None of it is Al-10Si: the captions say what it is.
PLAN = [
    dict(beat="charge", file="nab_k7m2q9_four_rod_pieces_1079.886g.jpg", seconds=3.6,
         caption="The lab's own four charges, Oct 27 2026: four 630 bronze rod pieces, 1,079.886 g on the balance, "
                 "melted in one run (Gage Erickson, DAL #219). Bronze, not this chapter's Al-10Si."),
    dict(beat="melt", file="nab_melt1.mp4", window=(10.0, 15.0),
         caption="Real footage, Oct 27 2026, through the furnace port: the four bronze pieces stand round the sealing "
                 "rod and glow (youtu.be/2brsz-90seg, DAL #219). 630 bronze at 1300 °C, not Al-10Si."),
    dict(beat="melt", file="nab_melt2.mp4", window=(70.0, 77.0),
         caption="A few minutes on, the pieces sink into their own melt round the rod (2brsz-90seg, about 4:36; at "
                 "3:55 Gage says \"It's melting in right now\")."),
    dict(beat="melt", file="nab_melt3.mp4", window=(14.0, 18.5),
         caption="The charge fully molten, a bright pool round the sealing rod (2brsz-90seg, DAL #219)."),
    dict(beat="pour", file="nab_pour1.mp4", window=(15.0, 22.5),
         caption="Real footage, Oct 27 2026, through the view port: the bronze jet lands on the tip of the W-coated "
                 "carbon-fibre plate and atomizes (2brsz-90seg). 91 % of the 1,080 g became usable powder (DAL #219)."),
    dict(beat="pour", file="al_pour_oct08.mp4", window=(14.0, 20.0),
         caption="Real footage, Oct 8 2026: an Al 6063 stream on a carbon-fibre plate (youtu.be/dTyuZmqYxHA). That "
                 "day it dripped rather than atomized: a CF plate with the 1.5:1 booster (DAL #159, PR #176)."),
    dict(beat="powder", file="nab_k7m2q9_jar_of_powder.jpg", seconds=3.0,
         caption="Real photo: a jar of the Oct 27 bronze powder, lot k7m2q9 (DAL #219)."),
    dict(beat="powder", file="al4047_oct22_c3k0n5_bag_and_jar.jpg", seconds=3.0,
         caption="Real photo: the Oct 22 Al 4047 run, lot c3k0n5, 169 g in: a bag of splats and a jar of powder "
                 "(Ronnie Guymon, DAL #159)."),
    dict(beat="sieved", file="nab_k7m2q9_sieved_three_jars.jpg", seconds=4.2,
         caption="Real photo: the Oct 27 bronze sieved. Left, under 63 µm, the LPBF cut: 188 g from both bronze "
                 "runs; middle, 63-250 µm, 827 g; right, flakes over 250 µm (Gage Erickson, DAL #219)."),
]
BEATS = ("charge", "melt", "pour", "powder", "sieved")
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
    ns = SimpleNamespace(title=TITLE, label=label, gauges=[], labels=[], caption=" ".join(caption.split()))
    img = Scene.overlay(ns, img, scale, [])
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


def clearance() -> dict:
    """At each cup's release (its top just under the rod's adapter, tipped 4 deg), how close the 2F-85's fingers come
    to the cups already seated and to the crucible's bore. The same poses the movie uses, from the gripper's meshes
    (ur_arm). Written to out/alloy_atomize_clearance.json."""
    import ur_arm
    gfk = ur_arm.gripper_fk(GRIP_CUP)
    parts = ("left_finger_tip", "right_finger_tip", "left_finger", "right_finger", "left_inner_knuckle",
             "right_inner_knuckle", "left_knuckle", "right_knuckle")
    pts = {p: np.vstack([m.points for m, _, _ in lst]) for p, lst in ur_arm.gripper_meshes().items() if p in parts}
    top_seated = cup_seat(0)[2] + C.SLUG_L
    rows = []
    for k in range(N_CUPS):
        held, _ = tip_in_path(k)
        spin = (90.0 - CUP_ANGLES[k] + 90.0) % 180.0 - 90.0
        pick = A.down(np.array([0.0, 0.0, C.SLUG_L - 13.0]), spin=spin)     # the grasp, relative to the cup's base
        tool0 = held[-1] @ pick @ T((0, 0, -ur_arm.TCP_MM))
        Wp = np.vstack([(tool0 @ gfk[p] @ np.c_[P_, np.ones(len(P_))].T).T[:, :3] for p, P_ in pts.items()])
        r = np.hypot(Wp[:, 0], Wp[:, 1])
        below = Wp[:, 2] < M.RIM
        over = []
        for j in range(k):
            s = cup_seat(j)
            on = np.hypot(Wp[:, 0] - s[0], Wp[:, 1] - s[1]) < C.STOCK_D / 2
            if on.any():
                over.append(dict(cup=j + 1, gap_mm=round(float(Wp[on, 2].min() - top_seated), 1)))
        rows.append(dict(cup=k + 1, angle_deg=CUP_ANGLES[k], fingers_lowest_below_rim_mm=round(float(M.RIM - Wp[:, 2].min()), 1),
                         over_seated_cups=over,
                         into_crucible_wall_mm=round(float(max(0.0, (r[below] - M.CRUCIBLE_ID / 2).max())), 1)
                         if below.any() else 0.0))
    return dict(cups=rows, seated_cup_tops_below_rim_mm=round(float(M.RIM - top_seated), 1),
                note="2F-85 at closure GRIP_CUP, holding the cup 13 mm below its top as the movie does, at the "
                     "release pose (#222's tight spot under the rod's adapter). into_crucible_wall_mm: how far the "
                     "fingers' outer corners reach past the 57.1 mm bore while below the rim, i.e. into the graphite.")


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
                raw = _clip(e["path"], t0 - off, t1 - t0, fps)
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
            badge = " · ".join(x for x in ("REAL FOOTAGE" if video else "REAL PHOTO", _alloy(e), _date(e)) if x)
            k0 = len(frames)
            frames += [np.asarray(_dress(p, sl["label"], badge, item["caption"], 1.0, size)) for p in pics]
            gifs += [_dress(p, sl["label"], badge, item["caption"], gsize[0] / size[0], gsize).convert("RGB")
                     for p in pics[::gstep]]
            subs.append(dict(label=sl["label"], caption=" ".join(item["caption"].split()), start_frame=k0,
                             end_frame=len(frames) - 1,
                             footage=dict(file=item["file"], source=e.get("source"), date=e.get("date"),
                                          alloy=_alloy(e), window_s=item.get("window"))))
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
    elif arg == "keep":
        print("kept", keep_footage(), "files in", KEEP)
    elif arg == "clearance":
        cl = clearance()
        (OUT / f"{NAME}_clearance.json").write_text(json.dumps(cl, indent=1) + "\n")
        print(json.dumps(cl, indent=1))
    elif arg == "powder":
        print(json.dumps(sums, indent=1, ensure_ascii=False))
    else:
        movie()
