#!/usr/bin/env python3
"""The stirrer's assembly, one part per step: a 1080p MP4 to pause on, a GIF and a contact sheet.

    xvfb-run -a -s "-screen 0 1920x1080x24" python assembly_video.py            # MP4, GIF and sheet
    xvfb-run -a -s "-screen 0 1920x1080x24" python assembly_video.py --stills   # held frames only

Writes img/assembly_steps.mp4 (1920 x 1080, 30 fps, a chapter per step), img/assembly_steps.gif
(960 x 540, 10 fps, the same steps with shorter holds) and img/assembly_steps_sheet.png, where
each step ends. The style is the lab's (docs/assembly-instruction-videos.md, after the OT-2 lid
mount's assembly_video.py on PR #234): each step first holds with its parts beside their places
and a dashed line from each to where it goes, then moves them in and holds again. Orange marks
what the step adds, amber a second kind of part, and the side panel repeats the step from
BUILD.md, the build of the version driven by the CubXL's Uno.

The parts come from the Onshape document in onshape/document.json, one STL per part in its
assembled place. That is read-only, and cached under .cache/ by the document's microversion; it
needs ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY, as build_onshape.py does. The Onshape model
still has the XIAO RP2040 version's controller in the pocket, so the XIAO and its diode are left
out here, and the junction board, its parts and the cable to the Uno are drawn instead, to
BUILD.md's dimensions. Where the parts sit on the board is indicative.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"
CACHE = HERE / ".cache" / "assembly_video"
TITLE = "Single-vial stirrer for the CubXL: assembly"
FONTS = Path("/usr/share/fonts/truetype/dejavu")
HL = (1.0, 0.47, 0.0)           # orange: the parts the current step adds
HL2 = (1.0, 0.76, 0.12)         # amber: a second kind of part in the same step
ORANGE = (255, 120, 0)
INK, GREY, PANEL = (30, 30, 32), (105, 105, 110), (244, 244, 241)
UP = np.array([0.0, 0.0, 1.0])
X = np.array([1.0, 0.0, 0.0])

# Heights and positions from onshape/vial_stirrer.fs, in mm; z = 0 is the deck's top face.
FLOOR_T, Z_FAN0, Z_FAN1, Z_WALL, FLANGE_T = 3.2, 9.0, 19.5, 20.0, 6.0
Z_CAR = Z_FAN1 + 3.23                 # carrier top
Z_RECESS = Z_CAR + 1.1                # the holder's pocket ceiling
Z_VIAL = Z_RECESS + 1.2               # vial bottom
Z_BAR = Z_VIAL + 1.6 + 3.0            # stir bar axis
FAN_PITCH, POST, KEY_X, MAG_X = 32.0, 23.5, 12.5, 4.9
HOLDER_MID = np.array([0.0, 0.0, 31.0])   # the holder turns over about this point

STEEL = (0.74, 0.75, 0.78)            # the BOM's screws are 304 stainless
REAL = {"fan_screws": STEEL, "holder_screws": STEEL,
        "carrier": (0.86, 0.86, 0.82)}   # the model's orange would read as "new" here


@dataclass
class Layout:
    W: int                            # canvas
    H: int
    VW: int                           # the 3D view, VW x H at the left; the panel takes the rest
    fps: int
    cam: int                          # frames for the camera move between steps
    staged: int                       # frames held with the parts beside their places
    move: float                       # times Step.frames, which are written for 30 fps
    hold: int                         # the finished step holds at least this many frames
    chapter: int                      # and the whole step at least this many
    label: float                      # label text, against the MP4's 25 and 20 px
    detail: bool                      # the labels' grey second line


# YouTube ignores chapters shorter than 10 s, hence 11 s a step in the MP4.
MP4 = Layout(1920, 1080, 1290, 30, 30, 75, 1.0, 150, 11 * 30, 1.0, True)
# The GIF's view is the MP4's at half size, so the framing and the label places carry over.
GIF = Layout(960, 540, 645, 10, 7, 9, 0.25, 15, 0, 0.62, False)


def font(size: float, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), round(size))


def wrap(text: str, f: ImageFont.FreeTypeFont, width: float) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}".strip()
            if f.getlength(trial) <= width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def ease(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


# --- what each part is: label, detail line ----------------------------------------------------

PARTS = {
    "deck": ("CubXL+ deck", "10 mm polycarbonate, pill slots 25 mm apart"),
    "keys": ("Deck key", "printed, nub up (Cubware's key)"),
    "base": ("Base", "printed PETG"),
    "inserts": ("M3 x 5.7 mm heat-set insert", "brass, ruthex (BOM 11)"),
    "magnets": ("N52 magnet, 1/4 x 1/16 in", "BOM 2"),
    "mag_n": ("Magnet, north up", "N52, 1/4 x 1/16 in (BOM 2)"),
    "mag_s": ("Magnet, south up", "N52, 1/4 x 1/16 in (BOM 2)"),
    "carrier": ("Magnet carrier", "printed, 100 % infill"),
    "board": ("Junction board", "perfboard, 3 resistors, 100 nF, 1N5819"),
    "cable": ("Cable to the Uno", "22 AWG, 4 cores; JST-XH at the Uno end"),
    "notch": ("Cable notch", "the wall without vents"),
    "mosfet": ("IRLZ44N MOSFET", "TO-220, flat, tab toward +X (BOM 5)"),
    "fan": ("Fan, Orion OD4010-12HSS", "40 x 40 x 10.5 mm, rotor side up (BOM 1)"),
    "fan_screws": ("M3 x 16 socket head", "304 stainless (BOM 12)"),
    "hall": ("US1881 Hall latch", "TO-92UA, marked face toward you (BOM 4)"),
    "groove": ("Groove", "for the sensor's leads"),
    "holder": ("Vial holder", "printed PETG, the 9-vial holder's cup"),
    "holder_screws": ("M3 x 12 socket head", "304 stainless (BOM 12)"),
    "bar": ("PTFE stir bar, 15 x 6 mm", "BOM 3"),
    "vial": ("20 mL vial", "~10 mL of sample; water for the first spins"),
    "perfboard": ("Perfboard, 8 x 7 holes", "BOM 10"),
    "passives": ("100 R and 2 x 10 k resistors, 1N5819", "BOM 6, 7"),
    "jst": ("JST-XH 4-pin plug and socket", "near the Uno (BOM 9)"),
    "cap": ("100 nF ceramic capacitor", "across the sensor's supply"),
    "glue": ("Gel CA, hot glue, heat shrink", "and 26 AWG wire, a small zip tie"),
}
SWATCH = {"inserts": (0.80, 0.62, 0.25), "magnets": (0.85, 0.13, 0.13), "board": (0.13, 0.42, 0.24),
          "cable": (0.60, 0.60, 0.62), "perfboard": (0.13, 0.42, 0.24), "passives": (0.85, 0.75, 0.55),
          "jst": (0.95, 0.95, 0.92), "cap": (0.35, 0.60, 0.85), "glue": (0.97, 0.97, 0.97)}


# --- the steps -----------------------------------------------------------------------------------

@dataclass
class Move:
    names: list[str]                  # actors, or "@group"
    vec: np.ndarray                   # where they start, relative to where they end up
    t0: float = 0.0                   # the part of the step they move in
    t1: float = 1.0
    guide: list[np.ndarray] | None = None   # for a group: points for the dashed lines


@dataclass
class Label:
    key: str                          # PARTS entry
    at: tuple[float, float]           # top-left of the box, as fractions of the 3D view
    targets: list[str] = field(default_factory=list)   # actors whose anchors it points at
    points: list[tuple] | None = None                   # or these points, moving with targets[0]
    qty: int = 0
    text: str | None = None


@dataclass
class Step:
    short: str                        # chapter title and progress list entry
    title: str
    body: str
    cam: list
    brief: str = ""                   # the GIF's one or two lines
    stage: str = ""                   # where it is in BUILD.md
    adds: list[tuple[int, str, int]] = field(default_factory=list)   # qty, part, which highlight
    moves: list[Move] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)
    highlight: list[str] = field(default_factory=list)
    highlight2: list[str] = field(default_factory=list)
    xray: dict[str, float] = field(default_factory=dict)
    hide: list[str] = field(default_factory=list)
    show: list[str] = field(default_factory=list)
    frames: int = 60
    setup: Callable[[], None] | None = None          # before the step, while what it changes is hidden
    pre: Callable[[float], None] | None = None       # during the camera move
    spin: list[str] = field(default_factory=list)    # turned about the vial axis during the last hold
    tool: str = ""
    number: int = 0


def view(az: float, el: float, dist: float, focal) -> list:
    """Camera from an azimuth (degrees from -Y toward +X), an elevation and a distance."""
    a, e = math.radians(az), math.radians(el)
    f = np.array(focal, float)
    d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    return [tuple(f + dist * d), tuple(f), (0.0, 0.0, 1.0)]


# --- the parts -----------------------------------------------------------------------------------

def onshape_parts() -> tuple[list[dict], Path]:
    """Every part of the Onshape model as an STL in its assembled place, cached by microversion."""
    sys.path.insert(0, str(HERE))
    from build_onshape import DOC_FILE, Onshape

    api = Onshape()
    doc = json.loads(DOC_FILE.read_text())
    did, wid, ps = doc["did"], doc["wid"], doc["partstudio"]
    mv = api.get(f"documents/d/{did}/w/{wid}/currentmicroversion").json()["microversion"]
    cdir = CACHE / mv
    index = cdir / "parts.json"
    if index.exists():
        return json.loads(index.read_text()), cdir
    feats = api.get(f"partstudios/d/{did}/w/{wid}/e/{ps}/features").json()["features"]
    state = {p["parameterId"]: p.get("value") for f in feats for p in f.get("parameters", [])}
    if state.get("step") or state.get("exploded") or state.get("section"):
        raise SystemExit(f"The Onshape feature is set to {state}. Set it back to step 0 first "
                         "(build_onshape.py leaves it there).")
    cdir.mkdir(parents=True, exist_ok=True)
    hdr = {"Accept": "application/vnd.onshape.v1+octet-stream"}
    out = []
    for p in api.get(f"parts/d/{did}/w/{wid}/e/{ps}").json():
        pid = urllib.parse.quote(p["partId"], safe="")
        r = api.get(f"parts/d/{did}/w/{wid}/e/{ps}/partid/{pid}/stl", headers=hdr, allow_redirects=False,
                    params={"mode": "binary", "units": "millimeter", "angleTolerance": 0.1,
                            "chordTolerance": 0.01})
        if r.status_code in (302, 307):
            r = api.get(r.headers["Location"], headers=hdr)
        r.raise_for_status()
        f = cdir / f"{len(out):02d}.stl"
        f.write_bytes(r.content)
        look = p.get("appearance", {})
        c = look.get("color", {})
        out.append({"name": p["name"], "file": f.name, "opacity": look.get("opacity", 255) / 255,
                    "color": [c.get("red", 128) / 255, c.get("green", 128) / 255, c.get("blue", 128) / 255]})
    index.write_text(json.dumps(out, indent=1) + "\n")
    print(f"fetched {len(out)} parts from Onshape into {cdir}")
    return out, cdir


def actor_key(name: str, centre) -> str | None:
    """Which actor an Onshape part belongs to; None for the XIAO version's controller."""
    table = [("CubXL+ deck", "deck"), ("Base", "base"), ("Deck key", "keys"), ("N-MOSFET", "mosfet"),
             ("IRLZ44N tab", "mosfet_tab"), ("Fan", "fan"), ("M3 x 16", "fan_screws"),
             ("M3 x 12", "holder_screws"), ("Magnet carrier", "carrier"), ("Vial holder", "holder"),
             ("Hall latch", "hall"), ("US1881 leads", "hall_leads"), ("Vial 20 mL", "vial"),
             ("Sample", "sample"), ("Stir bar", "bar")]
    if "XIAO" in name or name.startswith("Flyback diode"):
        return None
    if name.startswith("Heat-set insert"):
        return "ins_fan" if abs(abs(centre[0]) - FAN_PITCH / 2) < 1.0 else "ins_corner"
    if name.startswith("Magnet N52"):
        return "mag_n" if "N up" in name else "mag_s"
    for prefix, key in table:
        if name.startswith(prefix):
            return key
    raise SystemExit(f"unexpected part in the Onshape model: {name!r}")


def junction_board() -> dict[str, tuple[pv.PolyData, tuple]]:
    """The Uno version's junction board on the controller rails, its parts, and the cable.

    BUILD.md stage 5: perfboard cut to 8 x 7 holes (21 x 17.5 mm) on the rails at the -X end,
    everything on top under 3 mm, the cable's four cores at the -X (notch) end. The jacket is
    4.6 mm across and leaves through the notch, low, to stay clear of the fan.
    """
    z0, x0, x1, hy = FLOOR_T + 0.5, -22.6, -1.6, 8.75
    zt = z0 + 1.6
    cols = [x0 + 0.34 + 1.27 + 2.54 * i for i in range(8)]
    rows = [(j - 3) * 2.54 for j in range(7)]
    parts: dict[str, tuple[pv.PolyData, tuple]] = {}
    parts["jb_board"] = (pv.Box((x0, x1, -hy, hy, z0, zt)), (0.13, 0.42, 0.24))
    pads = [pv.Cylinder(center=(x, y, zt + 0.03), direction=(0, 0, 1), radius=0.8, height=0.06, resolution=14)
            for x in cols for y in rows]
    parts["jb_pads"] = (pv.merge(pads), (0.83, 0.80, 0.72))

    def axial(xa, xb, y, r, body, bands=()):
        """A part lying flat along X between the holes at xa and xb: body, lead and colour bands."""
        xc = (xa + xb) / 2
        zc = zt + r + 0.15
        lead = [pv.Cylinder(center=(xc, y, zc), direction=(1, 0, 0), radius=0.3, height=xb - xa, resolution=10)]
        for x in (xa, xb):
            lead.append(pv.Cylinder(center=(x, y, (zt + zc) / 2), direction=(0, 0, 1), radius=0.3,
                                    height=zc - zt, resolution=10))
        main = pv.Cylinder(center=(xc, y, zc), direction=(1, 0, 0), radius=r, height=body, resolution=28)
        rings = [(pv.Cylinder(center=(xc + dx, y, zc), direction=(1, 0, 0), radius=r + 0.03, height=0.55,
                              resolution=28), col) for dx, col in bands]
        return main, pv.merge(lead), rings

    brown, black, orange, gold = (0.45, 0.25, 0.10), (0.08, 0.08, 0.08), (0.95, 0.45, 0.05), (0.80, 0.65, 0.25)
    res, leads, ring_meshes = [], [], {}
    for y, third in ((rows[1], brown), (rows[2], orange), (rows[3], orange)):   # 100 R, then the two 10 k
        body, lead, rings = axial(cols[1], cols[4], y, 1.15, 6.0,
                                  ((-1.9, brown), (-1.1, black), (-0.3, third), (1.9, gold)))
        res.append(body)
        leads.append(lead)
        for m, col in rings:
            ring_meshes.setdefault(col, []).append(m)
    body, lead, rings = axial(cols[3], cols[6], rows[5], 1.35, 5.2, ((2.1, (0.85, 0.85, 0.85)),))
    leads.append(lead)
    for m, col in rings:
        ring_meshes.setdefault(col, []).append(m)
    parts["jb_res"] = (pv.merge(res), (0.86, 0.76, 0.56))
    parts["jb_diode"] = (body, (0.10, 0.10, 0.10))
    parts["jb_leads"] = (pv.merge(leads), (0.80, 0.80, 0.82))
    for i, (col, ms) in enumerate(ring_meshes.items()):
        parts[f"jb_band{i}"] = (pv.merge(ms), col)
    parts["jb_cap"] = (pv.Cylinder(center=(cols[6], rows[2] - 1.27, zt + 1.0), direction=(0, 0, 1), radius=2.2,
                                   height=2.0, resolution=32), (0.35, 0.60, 0.85))
    # Four cores from the jacket, inside the notch, up to the holes in the -X column
    zc = FLOOR_T - 0.6 + 2.3
    cores = {"jb_core_red": (rows[5], (0.80, 0.10, 0.10)), "jb_core_black": (rows[4], (0.10, 0.10, 0.10)),
             "jb_core_white": (rows[2], (0.92, 0.92, 0.92)), "jb_core_green": (rows[1], (0.10, 0.55, 0.20))}
    for k, (name, (y, col)) in enumerate(cores.items()):
        y0 = (k - 1.5) * 1.1
        path = pv.Spline(np.array([(-23.4, y0, zc), (-22.2, (y0 + y) / 2, zc + 0.3), (cols[0], y, zt + 0.7)]), 12)
        parts[name] = (path.tube(radius=0.7, n_sides=12, capping=True), col)
    route = np.array([(-23.0, 0, zc), (-28.5, 0, zc), (-34.0, 0, zc - 0.6), (-40.0, -3.0, 2.6), (-45.0, -12.0, 2.3),
                      (-47.0, -30.0, 2.3), (-47.0, -67.0, 2.3)])
    parts["cable"] = (pv.Spline(route, 60).tube(radius=2.3, n_sides=28, capping=True), (0.60, 0.60, 0.62))
    return parts


JB = None   # the junction board's actor names, set by scene()


def scene() -> tuple[dict[str, pv.PolyData], dict[str, tuple], dict[str, float], dict[str, np.ndarray]]:
    """Every actor as a mesh in its assembled place, its colour, its opacity, and anchor points."""
    global JB
    parts, cdir = onshape_parts()
    meshes: dict[str, list[pv.PolyData]] = {}
    colours, opacity, tops = {}, {}, {}
    for p in parts:
        m = pv.read(cdir / p["file"])
        key = actor_key(p["name"], m.center)
        if key is None:
            continue
        meshes.setdefault(key, []).append(m)
        colours[key] = REAL.get(key, tuple(p["color"]))
        opacity[key] = p["opacity"]
        b = m.bounds
        tops.setdefault(key, []).append(((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, b[5]))
    out = {k: (v[0] if len(v) == 1 else pv.merge(v)) for k, v in meshes.items()}
    jb = junction_board()
    JB = list(jb)
    for k, (m, c) in jb.items():
        out[k], colours[k], opacity[k] = m, c, 1.0
    # One point per copy for the many-copy parts (the top of each), set points for the rest
    anchors = {k: np.array(tops[k]) for k in ("keys", "ins_fan", "ins_corner", "fan_screws", "holder_screws")}
    holes = np.array([(sx * FAN_PITCH / 2, sy * FAN_PITCH / 2, Z_FAN1) for sx in (-1, 1) for sy in (-1, 1)])
    anchors.update({
        "base": np.array([(-KEY_X, 0, 0.0), (KEY_X, 0, 0.0)]),
        "jb_board": np.array([(-12.1, 0, FLOOR_T + 2.1)]),
        "mosfet": np.array([(10.6, 0, FLOOR_T + 4.5)]),
        "fan": holes,
        "mag_n": np.array([(-MAG_X, 0, Z_CAR - 0.1)]),
        "mag_s": np.array([(MAG_X, 0, Z_CAR - 0.1)]),
        "hall": np.array([(-11.8, 0, Z_RECESS - 1.6)]),
        "bar": np.array([(0, 0, Z_BAR)]),
    })
    return out, colours, opacity, anchors


GROUPS = {   # innermost first: a member's transforms apply in this order
    "car_sub": ["carrier", "mag_n", "mag_s"],
    "holder_sub": ["holder", "hall", "hall_leads"],
    "vial_sub": ["vial", "sample", "bar"],
}


# --- the video -----------------------------------------------------------------------------------

def rot_about(deg: float, axis, origin) -> np.ndarray:
    a = math.radians(deg)
    k = np.asarray(axis, float) / np.linalg.norm(axis)
    kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    r = np.eye(3) + math.sin(a) * kx + (1 - math.cos(a)) * kx @ kx
    m = np.eye(4)
    m[:3, :3] = r
    m[:3, 3] = np.asarray(origin, float) - r @ np.asarray(origin, float)
    return m


def shift(v) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = v
    return m


class Video:
    def __init__(self, lay: Layout, out: Path | None, stills: bool):
        self.L = lay
        self.pl = pv.Plotter(off_screen=True, window_size=(lay.VW, lay.H))
        self.pl.set_background("white")
        self.pl.enable_anti_aliasing("ssaa")
        self.pl.enable_depth_peeling()
        self.actors, self.color, self.pos, self.spin = {}, {}, {}, {}
        self.alpha, self.base_alpha, self.real_alpha = {}, {}, {}
        self.groups = {g: list(m) for g, m in GROUPS.items()}
        self.group_off = {g: np.zeros(3) for g in self.groups}
        self.group_rot = {g: 0.0 for g in self.groups}       # degrees about X through HOLDER_MID
        self.anchors: dict[str, np.ndarray] = {}
        self.cam = None
        self.frame_no = 0
        self.chapters: list[tuple[int, str]] = []
        self.stills: list[tuple[str, Image.Image]] = []
        self.only_stills = stills
        self.out = out
        self.ff = None
        if out is not None and not stills:
            self.tmp = out.with_suffix(".tmp.mp4")
            codec = (["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-g", str(lay.fps)]
                     if out.suffix == ".mp4" else ["-c:v", "libx264rgb", "-preset", "veryfast", "-qp", "0"])
            self.ff = subprocess.Popen(
                [ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                 "-s", f"{lay.W}x{lay.H}", "-r", str(lay.fps), "-i", "-", *codec, "-movflags", "+faststart",
                 str(self.tmp)], stdin=subprocess.PIPE)

    def add(self, name, poly, color, opacity=1.0, shown=True):
        self.actors[name] = self.pl.add_mesh(poly, color=color, opacity=opacity, smooth_shading=True,
                                             split_sharp_edges=True, specular=0.25)
        self.color[name] = color
        self.pos[name] = np.zeros(3)
        self.spin[name] = 0.0
        self.base_alpha[name] = self.real_alpha[name] = opacity
        self.alpha[name] = 1.0 if shown else 0.0

    def members(self, name: str) -> list[str]:
        if name.startswith("@"):
            g = name[1:]
            return [n for n in self.actors if n in self.groups[g]]
        return [name]

    def matrix(self, name: str, with_pos: bool = True) -> np.ndarray:
        m = rot_about(self.spin[name], UP, (0, 0, 0)) if self.spin[name] else np.eye(4)
        for g, members in self.groups.items():
            if name in members:
                if self.group_rot[g]:
                    m = rot_about(self.group_rot[g], X, HOLDER_MID) @ m
                m = shift(self.group_off[g]) @ m
        return shift(self.pos[name]) @ m if with_pos else m

    @staticmethod
    def apply_m(m: np.ndarray, pts) -> np.ndarray:
        pts = np.atleast_2d(np.asarray(pts, float))
        return pts @ m[:3, :3].T + m[:3, 3]

    def apply(self):
        for name, actor in self.actors.items():
            actor.SetUserMatrix(pv.vtkmatrix_from_array(self.matrix(name)))
            a = self.alpha[name]
            actor.SetVisibility(a > 0.02)
            actor.GetProperty().SetOpacity(self.base_alpha[name] * a)

    def project(self, pts) -> list[tuple[float, float]]:
        ren = self.pl.renderer
        out = []
        for x, y, z in pts:
            ren.SetWorldPoint(float(x), float(y), float(z), 1.0)
            ren.WorldToDisplay()
            dx, dy, _ = ren.GetDisplayPoint()
            out.append((dx, self.L.H - dy))
        return out

    # -- drawing -----------------------------------------------------------------------------------

    def render3d(self) -> Image.Image:
        self.apply()
        self.pl.camera_position = self.cam
        self.pl.render()
        return Image.fromarray(self.pl.screenshot(return_img=True))

    def label_points(self, lab: Label) -> np.ndarray:
        if lab.points is not None:
            return self.apply_m(self.matrix(lab.targets[0]), lab.points)
        pts = [self.apply_m(self.matrix(t), self.anchors[t]) for t in lab.targets]
        return np.vstack(pts)

    def overlay(self, labels: list[Label], guides: list[tuple]) -> Image.Image:
        L, ss = self.L, 2
        s = L.H / 1080                     # line widths and the like follow the view's size
        lay = Image.new("RGBA", (L.VW * ss, L.H * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for a, b in guides:
            (ax, ay), (bx, by) = self.project([a, b])
            dashed(d, (ax * ss, ay * ss), (bx * ss, by * ss), ORANGE + (235,), max(2, round(3 * s * ss)),
                   14 * s * ss, 9 * s * ss)
            r = 5 * s * ss
            d.ellipse([bx * ss - r, by * ss - r, bx * ss + r, by * ss + r], outline=ORANGE + (255,),
                      width=max(2, round(2 * s * ss)))
        f1, f2 = font(25 * L.label * ss, True), font(20 * L.label * ss)
        pad, lw = 14 * L.label * ss, max(2, round(2 * L.label * ss))
        for lab in labels:
            if lab.targets and self.alpha[lab.targets[0]] < 0.5:      # not on screen yet
                continue
            name, sub = PARTS[lab.key]
            head = lab.text or (f"{lab.qty} x {name}" if lab.qty else name)
            tw = (max(f1.getlength(head), f2.getlength(sub)) if L.detail else f1.getlength(head)) + 2 * pad
            th = (72 if L.detail else 42) * L.label * ss
            x0, y0 = lab.at[0] * L.VW * ss, lab.at[1] * L.H * ss
            x1, y1 = x0 + tw, y0 + th
            for px, py in self.project(self.label_points(lab)):
                px, py = px * ss, py * ss
                sx, sy = min(max(px, x0), x1), min(max(py, y0), y1)
                d.line([(sx, sy), (px, py)], fill=INK + (255,), width=lw)
                r = 4.5 * L.label * ss
                d.ellipse([px - r, py - r, px + r, py + r], fill=INK + (255,), outline=(255, 255, 255, 255),
                          width=lw)
            d.rounded_rectangle([x0, y0, x1, y1], radius=10 * L.label * ss, fill=(255, 255, 255, 240),
                                outline=INK + (255,), width=lw)
            d.text((x0 + pad, y0 + 9 * L.label * ss), head, font=f1, fill=INK + (255,))
            if L.detail:
                d.text((x0 + pad, y0 + 41 * L.label * ss), sub, font=f2, fill=GREY + (255,))
        return lay.resize((L.VW, L.H), Image.LANCZOS)

    def compose(self, view_img: Image.Image, pan: Image.Image, labels, guides) -> Image.Image:
        canvas = Image.new("RGB", (self.L.W, self.L.H), "white")
        if labels or guides:
            view_img = Image.alpha_composite(view_img.convert("RGBA"), self.overlay(labels, guides)).convert("RGB")
        canvas.paste(view_img, (0, 0))
        canvas.paste(pan, (self.L.VW, 0))
        return canvas

    def emit(self, img: Image.Image, n: int = 1):
        if self.ff is not None:
            data = img.tobytes()
            for _ in range(n):
                self.ff.stdin.write(data)
        self.frame_no += n

    def close(self):
        self.pl.close()
        if self.ff is None:
            return
        self.ff.stdin.close()
        self.ff.wait()
        out, L = self.out, self.L
        if out.suffix == ".mp4":
            meta = out.with_suffix(".chapters.txt")
            lines = [";FFMETADATA1", f"title={TITLE}"]
            bounds = [c[0] for c in self.chapters[1:]] + [self.frame_no]
            for (start, name), end in zip(self.chapters, bounds):
                lines += ["[CHAPTER]", f"TIMEBASE=1/{L.fps}", f"START={start}", f"END={end}", f"title={name}"]
            meta.write_text("\n".join(lines) + "\n")
            subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(self.tmp), "-i", str(meta), "-map", "0",
                            "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", "-movflags", "+faststart",
                            str(out)], check=True)
            meta.unlink()
        else:
            # One palette for the whole GIF, and only the changed rectangle of each frame
            pal = out.with_suffix(".palette.png")
            subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(self.tmp), "-vf",
                            "palettegen=max_colors=192:stats_mode=full", str(pal)], check=True)
            subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(self.tmp), "-i", str(pal), "-lavfi",
                            "paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle", "-loop", "0", str(out)],
                           check=True)
            pal.unlink()
        self.tmp.unlink()
        print(f"{out.name}: {self.frame_no} frames, {self.frame_no / L.fps:.1f} s, {out.stat().st_size / 1e6:.1f} MB")
        if out.suffix == ".mp4":
            for start, name in self.chapters:
                t = start // L.fps
                print(f"  {t // 60}:{t % 60:02d} {name}")


def ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def dashed(d: ImageDraw.ImageDraw, a, b, fill, width, dash, gap):
    a, b = np.array(a, float), np.array(b, float)
    length = np.linalg.norm(b - a)
    if length < 1:
        return
    u = (b - a) / length
    s = 0.0
    while s < length:
        e = min(s + dash, length)
        d.line([tuple(a + u * s), tuple(a + u * e)], fill=fill, width=width)
        s = e + gap


def swatch(key: str, colours: dict) -> tuple[int, int, int]:
    rgb = SWATCH.get(key) or colours.get(key) or (0.5, 0.5, 0.5)
    return tuple(int(255 * c) for c in rgb)


# --- the side panels -----------------------------------------------------------------------------

def panel(step: Step, steps: list[Step], colours: dict, parts_list=None) -> Image.Image:
    """The MP4's: the step, its parts, and every step with this one marked."""
    W, H, VW = MP4.W, MP4.H, MP4.VW
    img = Image.new("RGB", (W - VW, H), PANEL)
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (0, H)], fill=(205, 205, 200), width=2)
    x, width = 40, W - VW - 80
    y = 30
    d.text((x, y), TITLE, font=font(21), fill=GREY)
    y += 44
    n_steps = sum(1 for s in steps if s.number)
    if step.number:
        d.text((x, y), f"Step {step.number} of {n_steps}", font=font(24, True), fill=ORANGE)
        y += 38
    for line in wrap(step.title, font(33, True), width):
        d.text((x, y), line, font=font(33, True), fill=INK)
        y += 43
    y += 8
    for line in wrap(step.body, font(22), width):
        d.text((x, y), line, font=font(22), fill=INK)
        y += 30
    notes = [t for t in (f"Tool: {step.tool}" if step.tool else "", f"BUILD.md {step.stage}" if step.stage else "")
             if t]
    if notes:
        y += 6
        d.text((x, y), "   ·   ".join(notes), font=font(20, True), fill=GREY)
        y += 30
    if step.adds:
        y += 18
        d.text((x, y), "THIS STEP ADDS (coloured as in the view)", font=font(18, True), fill=GREY)
        y += 32
        y = part_rows(d, x, y, step.adds, colours)
    if parts_list:
        for heading, rows in parts_list:
            y += 14
            d.text((x, y), heading.upper(), font=font(18, True), fill=GREY)
            y += 29
            y = part_rows(d, x, y, rows, colours, compact=True)
    if step.number:
        top = H - 30 - 27 * n_steps
        if y > top - 8:
            print(f"warning: panel text runs into the step list on step {step.number} ({y} > {top - 8})")
        y = top
        for s in steps:
            if not s.number:
                continue
            here, done = s.number == step.number, s.number < step.number
            f = font(19, here)
            colour = INK if here else (GREY if done else (150, 150, 152))
            if here:
                d.rectangle([x - 14, y - 2, x - 8, y + 22], fill=ORANGE)
            d.text((x, y), f"{s.number:>2}", font=f, fill=colour)
            d.text((x + 38, y), s.short + ("  ✓" if done else ""), font=f, fill=colour)
            y += 27
    elif y > H - 20:
        print(f"warning: the parts list runs off the panel ({y} > {H - 20})")
    return img


def part_rows(d, x, y, rows, colours, compact=False) -> int:
    fq, fn, fs = font(21 if compact else 24, True), font(21 if compact else 24), font(19)
    for qty, key, *shade in rows:
        name, sub = PARTS[key]
        sz = 20 if compact else 25
        # A step's own parts get the colour they have in the view; the full list, their real one.
        fill = tuple(int(255 * c) for c in (HL, HL2)[shade[0] - 1]) if shade else swatch(key, colours)
        d.rounded_rectangle([x, y + 3, x + sz, y + 3 + sz], radius=5, fill=fill, outline=(90, 90, 90), width=1)
        tx = x + sz + 14
        q = f"{qty} x " if qty else ""
        d.text((tx, y), q, font=fq, fill=INK)
        d.text((tx + fq.getlength(q), y), name, font=fn, fill=INK)
        if compact:
            y += 28
        else:
            d.text((tx, y + 32), sub, font=fs, fill=GREY)
            y += 64
    return y


def gif_panel(step: Step, steps: list[Step], colours: dict, parts_list=None) -> Image.Image:
    """The GIF's: the step's title, a line or two, its parts, and a row of boxes for progress."""
    W, H, VW = GIF.W, GIF.H, GIF.VW
    img = Image.new("RGB", (W - VW, H), PANEL)
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (0, H)], fill=(205, 205, 200), width=1)
    x, width = 18, W - VW - 34
    y = 14
    for line in wrap("Single-vial stirrer for the CubXL", font(13), width):
        d.text((x, y), line, font=font(13), fill=GREY)
        y += 17
    y += 6
    n_steps = sum(1 for s in steps if s.number)
    if step.number:
        d.text((x, y), f"Step {step.number} of {n_steps}", font=font(15, True), fill=ORANGE)
        y += 22
    for line in wrap(step.title, font(19, True), width):
        d.text((x, y), line, font=font(19, True), fill=INK)
        y += 24
    y += 6
    for line in wrap(step.brief or step.body, font(14), width):
        d.text((x, y), line, font=font(14), fill=INK)
        y += 19
    if step.adds:
        y += 10
        for qty, key, shade in step.adds:
            fill = tuple(int(255 * c) for c in (HL, HL2)[shade - 1])
            d.rounded_rectangle([x, y + 2, x + 14, y + 16], radius=3, fill=fill, outline=(90, 90, 90), width=1)
            for line in wrap((f"{qty} x " if qty else "") + PARTS[key][0], font(14, True), width - 22):
                d.text((x + 22, y), line, font=font(14, True), fill=INK)
                y += 19
            y += 3
    if parts_list:
        for heading, rows in parts_list:
            y += 5
            d.text((x, y), heading.upper(), font=font(11, True), fill=GREY)
            y += 15
            for qty, key in rows:
                d.rounded_rectangle([x, y + 2, x + 10, y + 12], radius=2, fill=swatch(key, colours),
                                    outline=(90, 90, 90), width=1)
                d.text((x + 16, y), (f"{qty} x " if qty else "") + PARTS[key][0], font=font(12), fill=INK)
                y += 14
        if y > H - 8:
            print(f"warning: the GIF's parts list runs off the panel ({y} > {H - 8})")
    if step.number:
        size, gap = 14, 4
        y = H - 22 - size
        if step.stage:
            d.text((x, y - 22), f"BUILD.md {step.stage}", font=font(12, True), fill=GREY)
        for s in steps:
            if not s.number:
                continue
            bx = x + (s.number - 1) * (size + gap)
            here, done = s.number == step.number, s.number < step.number
            fill = ORANGE if here else ((150, 150, 152) if done else PANEL)
            d.rectangle([bx, y, bx + size, y + size], fill=fill, outline=(150, 150, 152))
    return img


# --- the assembly ----------------------------------------------------------------------------------

STIRRER = ["base", "keys", "ins_fan", "ins_corner", "mosfet", "mosfet_tab", "fan", "fan_screws", "carrier",
           "mag_n", "mag_s", "holder", "hall", "hall_leads", "holder_screws"]


def make_steps(v: Video) -> list[Step]:
    jb = JB
    board_bits = [n for n in jb if n != "cable"]
    corners = [np.array((sx * POST, sy * POST, Z_WALL)) for sx in (-1, 1) for sy in (-1, 1)]
    inside = ["ins_fan", "ins_corner"] + jb + ["mosfet", "mosfet_tab", "fan", "fan_screws"]

    def flip_back(u):
        v.group_rot["holder_sub"] = 180.0 * (1 - ease(u))

    def turn_over():
        v.group_off["holder_sub"] = UP * 35.0
        v.group_rot["holder_sub"] = 180.0

    def to_bench():
        v.group_off["car_sub"] = UP * 30.0

    def vial_up():
        v.group_off["vial_sub"] = UP * 60.0

    steps = [
        Step("Parts", "Parts for one stirrer",
             "Printed: the base, the vial holder, the magnet carrier and two deck keys. Bought: the "
             "fan, magnets, Hall sensor, MOSFET, the junction board's parts, the cable, inserts and "
             "stainless screws (BOM.md). Then a vial with a stir bar.",
             brief="Every part, grouped by where it comes from (BOM.md).",
             cam=view(35, 16, 600, (0, 0, 72)),
             labels=[Label("holder", (0.05, 0.30), ["holder"], points=[(-16.7, -2, 40)]),
                     Label("fan", (0.62, 0.50), ["fan"], points=[(18, -18, Z_FAN1)]),
                     Label("base", (0.05, 0.62), ["base"], points=[(-28, -10, 12)]),
                     Label("deck", (0.60, 0.84), ["deck"], points=[(60, -60, 0)]),
                     Label("vial", (0.62, 0.10), ["vial"], points=[(13.75, 0, 60)]),
                     Label("bar", (0.05, 0.06), ["bar"], points=[(-7.5, 0, Z_BAR)]),
                     Label("carrier", (0.05, 0.46), ["carrier"], points=[(-9.5, 0, Z_CAR - 1.6)]),
                     Label("board", (0.62, 0.66), ["jb_board"], points=[(-6, -8, FLOOR_T + 2.1)])]),
        Step("Deck keys into two slots", "Two deck keys into two slots",
             "Pick two adjacent slots in one row, 25 mm apart, where the stirrer will live. Drop a key "
             "into each, nub up, and turn each so its nub's single point faces the point of the "
             "triangular pocket under the base. Open slots: tape their undersides first.",
             brief="Two adjacent slots in one row, 25 mm apart. Nub up, its point toward the pocket's.",
             stage="stage 2", cam=view(35, 34, 290, (0, 0, 4)), adds=[(2, "keys", 1)],
             moves=[Move(["keys"], UP * 30)], highlight=["keys"],
             hide=[n for n in v.actors if n not in ("deck", "keys")],
             labels=[Label("keys", (0.05, 0.08), ["keys"], qty=2),
                     Label("deck", (0.55, 0.84), ["deck"], points=[(37.5, -32, 0)])]),
        Step("Base onto the keys", "Glue the base onto the keys",
             "Dry run first: the base sits flat on the nubs. Then a small drop of gel CA in each "
             "pocket, not on the nub. Lower the base straight down, press it flat for 30 s, wait a "
             "few minutes and lift it straight up: both keys come with it. Let it cure fully.",
             brief="Gel CA in each pocket, base straight down, 30 s; lift it off with the keys.",
             stage="stage 2", tool="gel CA", cam=view(35, 28, 280, (0, 0, 14)), adds=[(1, "base", 1)],
             moves=[Move(["base"], UP * 36)], highlight=["base"],
             labels=[Label("base", (0.05, 0.08), ["base"], points=[(-28, -20, 20)]),
                     Label("keys", (0.58, 0.82), ["keys"], qty=2)]),
        Step("Heat-set inserts", "Press in eight heat-set inserts",
             "Four in the short fan posts, four in the corner posts. Press each in straight with the "
             "iron at the insert maker's PETG temperature, until its top is level with the post or up "
             "to 0.2 mm below. When cool, run an M3 screw into each to check it goes in straight.",
             brief="Four in the fan posts, four in the corner posts: flush, or up to 0.2 mm below.",
             stage="stage 3", tool="soldering iron", cam=view(35, 42, 215, (0, 0, 8)),
             adds=[(8, "inserts", 1)], moves=[Move(["ins_fan", "ins_corner"], UP * 24)],
             highlight=["ins_fan", "ins_corner"], hide=["deck"],
             labels=[Label("inserts", (0.04, 0.07), ["ins_fan", "ins_corner"], qty=8)]),
        Step("Magnets into the carrier", "Glue the magnets into the carrier",
             "On the bench. Stack the two magnets, dot both outer faces, slide them apart. CA one "
             "into each pocket, dot up, flush or just below: that puts opposite poles up. Check with "
             "the spare magnet: it is pulled over one and pushed away over the other.",
             brief="Dot both outer faces of the stacked pair; glue both dot up = opposite poles up.",
             stage="stage 4", tool="CA glue, marker", cam=view(35, 44, 125, (0, 0, 50)),
             adds=[(1, "mag_n", 1), (1, "mag_s", 2)], setup=to_bench,
             moves=[Move(["mag_n", "mag_s"], UP * 16)], highlight=["mag_n"], highlight2=["mag_s"],
             show=["carrier"], hide=["base", "keys", "ins_fan", "ins_corner"],
             labels=[Label("mag_n", (0.04, 0.08), ["mag_n"]),
                     Label("mag_s", (0.58, 0.08), ["mag_s"]),
                     Label("carrier", (0.55, 0.82), ["carrier"], points=[(6.7, -6.7, Z_CAR)])]),
        Step("Junction board", "Junction board onto the rails",
             "Soldered and bench-checked first (stage 5). Slide it onto the two rails at the -X end, "
             "against the stop, with the cable out through the notch in the wall without vents. "
             "Zip-tie the jacket just inside the notch, so a tug pulls on the jacket, not the joints.",
             brief="Soldered and checked first (stage 5). On the rails, cable out through the notch.",
             stage="stages 5-6", tool="small zip tie", cam=view(-38, 40, 200, (-16, 0, 6)),
             adds=[(1, "board", 1), (1, "cable", 2)], moves=[Move(jb, UP * 28)],
             highlight=["jb_board"], highlight2=["cable"],
             show=["base", "keys", "ins_fan", "ins_corner"], hide=["carrier", "mag_n", "mag_s"],
             labels=[Label("board", (0.50, 0.07), ["jb_board"], points=[(-6, 6, FLOOR_T + 2.1)]),
                     Label("cable", (0.04, 0.74), ["cable"], points=[(-47, -40, 4.6)]),
                     Label("notch", (0.04, 0.07), ["base"], points=[(-27, -6.5, 14)])]),
        Step("MOSFET", "MOSFET flat at +X",
             "Lay it flat on the floor at +X, tab toward +X, with a dab of hot glue; the tab must touch "
             "nothing. Its three leads cross the stop to the board's +X end, joined with short wires.",
             brief="Flat on the floor at +X, tab toward +X, hot glue. Leads over the stop to the board.",
             stage="stages 5-6", tool="hot glue", cam=view(40, 44, 190, (8, 0, 6)),
             adds=[(1, "mosfet", 1)], moves=[Move(["mosfet", "mosfet_tab"], UP * 26)],
             highlight=["mosfet", "mosfet_tab"],
             labels=[Label("mosfet", (0.55, 0.08), ["mosfet"])]),
        Step("Fan", "Fan onto the posts, rotor side up",
             "Rotor side up: the side without the motor's struts, whose centre turns. Don't go by the "
             "sticker; many fans carry it on the strut side. Set it on the four short posts with its "
             "leads toward the board: red to 5V, black to Drain.",
             brief="Rotor side up: the side without the struts, not the sticker. Leads to the board.",
             stage="stage 6", cam=view(35, 32, 250, (0, 0, 12)), adds=[(1, "fan", 1)],
             moves=[Move(["fan"], UP * 34)], highlight=["fan"],
             labels=[Label("fan", (0.04, 0.07), ["fan"], points=[(-18, -18, Z_FAN1)])]),
        Step("M3 x 16 through the fan", "Four M3 x 16 through the fan",
             "Through the fan's corner holes into the post inserts. Snug only: the frame is plastic. "
             "Screwed down, the magnets can't lift the fan. Spin the blades by hand: nothing touches.",
             brief="Into the fan-post inserts, snug only: the frame is plastic.",
             stage="stage 6", tool="2.5 mm hex key", cam=view(35, 36, 250, (0, 0, 14)),
             adds=[(4, "fan_screws", 1)], moves=[Move(["fan_screws"], UP * 30)], highlight=["fan_screws"],
             labels=[Label("fan_screws", (0.04, 0.07), ["fan_screws"], qty=4)]),
        Step("Carrier onto the hub", "Glue the carrier onto the hub",
             "Hub more than 0.4 mm proud? Sand the carrier's underside first. Scuff the hub, then glue "
             "the carrier on, magnets up, centred to about 0.3 mm: measure to the frame's round "
             "opening at four points. Off centre, the bar walks round the vial.",
             brief="Magnets up, centred to ~0.3 mm on the hub, or the bar walks round the vial.",
             stage="stage 6", tool="gel CA or 5-min epoxy", cam=view(35, 38, 200, (0, 0, 22)),
             adds=[(1, "carrier", 1)], show=["carrier", "mag_n", "mag_s"],
             moves=[Move(["@car_sub"], UP * 30, guide=[np.array((0, 0, Z_CAR))])], highlight=["carrier"],
             labels=[Label("carrier", (0.04, 0.07), ["carrier"], points=[(6.7, -6.7, Z_CAR)])]),
        Step("Hall sensor into the holder", "Hall sensor into the holder",
             "Turn the holder upside down. Glue the sensor flat on the recess ceiling at the groove's "
             "mouth, marked face toward you, leads in the groove. Line its lead edge up with the "
             "recess edge; out along the groove, the signal gets weaker.",
             brief="Holder upside down. Flat on the recess ceiling at the groove's mouth, leads in the "
                   "groove.",
             stage="stage 6", tool="CA glue", cam=view(30, 34, 230, (-4, 0, 64)), setup=turn_over,
             adds=[(1, "hall", 1)], moves=[Move(["hall", "hall_leads"], UP * 22)],
             highlight=["hall"], show=["holder"],
             hide=["base", "keys", "carrier", "mag_n", "mag_s", *inside],
             labels=[Label("hall", (0.04, 0.07), ["hall"]),
                     Label("groove", (0.04, 0.82), ["holder"], points=[(-20, -2.6, Z_WALL)]),
                     Label("holder", (0.60, 0.82), ["holder"], points=[(20, -20, Z_WALL + 3)])]),
        Step("Holder onto the base", "Vial holder onto the base",
             "Right way up again. Only one of the four ways round is right: the groove goes over the "
             "cable notch. Fold the sensor's leads down inside that wall, and check the flange sits "
             "flat all round with no wire under it.",
             brief="The groove over the cable notch; no wire trapped under the flange.",
             stage="stage 6", cam=view(35, 30, 290, (0, 0, 32)), adds=[(1, "holder", 1)],
             show=["base", "keys", "carrier", "mag_n", "mag_s", *inside], pre=flip_back,
             moves=[Move(["@holder_sub"], UP * 35, guide=corners)], highlight=["holder"],
             labels=[Label("holder", (0.04, 0.07), ["holder"], points=[(-16.7, 0, 40)]),
                     Label("notch", (0.04, 0.82), ["base"], points=[(-28, -6.5, 12)])]),
        Step("M3 x 12 through the flange", "Four M3 x 12 through the flange",
             "Through the flange corners into the corner-post inserts. Then the three checks: spin the "
             "fan through a vent with a toothpick, the Hall output toggles once a turn, and the fan "
             "runs with no rubbing.",
             brief="Into the corner inserts. Then BUILD.md's spin, Hall and fan checks.",
             stage="stage 6", tool="2.5 mm hex key", cam=view(35, 38, 250, (0, 0, 22)),
             adds=[(4, "holder_screws", 1)], moves=[Move(["holder_screws"], UP * 30)],
             highlight=["holder_screws"],
             labels=[Label("holder_screws", (0.04, 0.07), ["holder_screws"], qty=4)]),
        Step("Onto the deck", "Set it on the deck",
             "After flashing the Uno (stage 7): the keys drop into the same two slots, a slip fit held "
             "by gravity. Run the cable clear of the gantry, flat on the deck or along its edge, "
             "taped, and plug in the JST.",
             brief="The keys into the same two slots. Cable clear of the gantry, then plug in the JST.",
             stage="stage 8", cam=view(35, 26, 380, (0, 0, 14)), show=["deck"],
             moves=[Move(["@stirrer"], UP * 45, guide=[np.array((sx * KEY_X, 0, -5.0)) for sx in (-1, 1)])],
             labels=[Label("deck", (0.55, 0.84), ["deck"], points=[(45, -45, 0)]),
                     Label("cable", (0.04, 0.80), ["cable"], points=[(-47, -40, 4.6)])]),
        Step("Stir bar into the vial", "Stir bar into the vial",
             "About 10 mL in the vial: water for the first spins, then the sample. Drop in the stir "
             "bar.",
             brief="About 10 mL: water for the first spins, then the sample.",
             stage="stage 8", cam=view(35, 30, 330, (0, 0, 92)), adds=[(1, "bar", 1)], setup=vial_up,
             show=["vial", "sample"], moves=[Move(["bar"], UP * 75)], highlight=["bar"],
             labels=[Label("bar", (0.60, 0.10), ["bar"], points=[(7.5, 0, Z_BAR)]),
                     Label("vial", (0.04, 0.10), ["vial"], points=[(-13.75, 0, 60)])]),
        Step("Vial into the cup", "Vial into the cup",
             "Push it down past the four fingers, all the way to the floor: they spring out about "
             "0.8 mm and grip it. For the coupling test, a 1, 2 or 3 mm spacer disc goes under it. "
             "The holder is see-through here.",
             brief="Down past the four fingers to the floor; they grip it.",
             stage="stage 8", cam=view(35, 22, 380, (0, 0, 62)), adds=[(1, "vial", 1)],
             moves=[Move(["@vial_sub"], UP * 60, guide=[np.array((0, 0, Z_VIAL))])], highlight=["vial"],
             xray={"holder": 0.35},
             labels=[Label("vial", (0.62, 0.12), ["vial"], points=[(13.75, 0, 70)]),
                     Label("holder", (0.04, 0.80), ["holder"], points=[(-16.7, -2, 34)])]),
        Step("Assembled", "Assembled",
             "On the deck, ready for its first spins (BUILD.md stage 8): no vial, then water, then the "
             "coupling test. The vial axis is midway between the two slot columns; its rim sits about "
             "7 mm higher than in the 9-vial holder (stage 9). The bar's turning here is only a sketch.",
             brief="Ready for its first spins (BUILD.md stage 8). The bar's turning is only a sketch.",
             cam=view(35, 22, 390, (0, 0, 34)), spin=["bar", "carrier", "mag_n", "mag_s"],
             labels=[Label("vial", (0.62, 0.10), ["vial"], points=[(13.75, 0, 70)]),
                     Label("holder", (0.04, 0.30), ["holder"], points=[(-16.7, -2, 40)]),
                     Label("base", (0.04, 0.56), ["base"], points=[(-28, -10, 12)]),
                     Label("cable", (0.04, 0.80), ["cable"], points=[(-47, -40, 4.6)]),
                     Label("deck", (0.55, 0.84), ["deck"], points=[(45, -45, 0)])]),
    ]
    for i, s in enumerate(steps[1:-1], 1):
        s.number = i
    return steps


EXPLODE = {"deck": -48, "keys": -20, "base": 0, "ins_fan": 16, "ins_corner": 16, "mosfet": 24, "mosfet_tab": 24,
           "fan": 32, "fan_screws": 52, "carrier": 58, "mag_n": 68, "mag_s": 68, "holder": 80, "hall": 80,
           "hall_leads": 80, "holder_screws": 100, "vial": 118, "sample": 118, "bar": 175}


def run(lay: Layout, out: Path, stills: bool, sheet_path: Path | None) -> None:
    v = Video(lay, out, stills)
    meshes, colours, opacity, anchors = scene()
    for name, m in meshes.items():
        v.add(name, m, colours[name], opacity=opacity[name])
    v.anchors = anchors
    v.groups["stirrer"] = STIRRER + JB
    v.group_off["stirrer"] = np.zeros(3)
    v.group_rot["stirrer"] = 0.0
    for n in v.actors:                                   # the first chapter: every part laid out
        v.pos[n] = UP * EXPLODE.get(n, 24 if n in JB else 0)

    steps = make_steps(v)
    full = [("Printed (PETG)", [(1, "base"), (1, "holder"), (1, "carrier"), (2, "keys")]),
            ("Bought (BOM.md, ME order 13518)", [(1, "fan"), (2, "magnets"), (1, "hall"), (1, "mosfet"),
                                                 (1, "passives"), (1, "perfboard"), (1, "cable"), (1, "jst"),
                                                 (8, "inserts"), (4, "fan_screws"), (4, "holder_screws"),
                                                 (1, "bar")]),
            ("Lab stock", [(1, "cap"), (0, "glue")]),
            ("On the CubXL", [(1, "deck"), (1, "vial")])]
    make_panel = panel if lay is MP4 else gif_panel
    v.cam = steps[0].cam
    lit: list[str] = []
    for k, st in enumerate(steps):
        start = v.frame_no
        v.chapters.append((start, f"{st.number}. {st.short}" if st.number else st.short))
        pan = make_panel(st, steps, colours, full if not st.number else None)
        for n in lit:                                    # last step's orange goes back to its colour
            v.actors[n].GetProperty().SetColor(*v.color[n])
        for n, a in st.xray.items():
            v.base_alpha[n] = a
        for n in st.highlight:
            v.actors[n].GetProperty().SetColor(*HL)
        for n in st.highlight2:
            v.actors[n].GetProperty().SetColor(*HL2)
        lit = st.highlight + st.highlight2
        if st.setup:
            st.setup()

        # Where this step's parts wait: hidden ones go straight there, visible ones are moved there
        movers = [n for m in st.moves for nm in m.names if not nm.startswith("@") for n in v.members(nm)]
        pos_from = {n: v.pos[n].copy() for n in v.actors}
        pos_to = dict(pos_from)
        if k == 1:                                       # out of the exploded view
            pos_to = {n: np.zeros(3) for n in v.actors}
        goff_from = {g: o.copy() for g, o in v.group_off.items()}
        goff_to = dict(goff_from)
        for m in st.moves:
            for nm in m.names:
                if nm.startswith("@"):
                    goff_to[nm[1:]] = np.asarray(m.vec, float)
                else:
                    for n in v.members(nm):
                        pos_to[n] = np.asarray(m.vec, float)
        for n in v.actors:
            if v.alpha[n] < 0.02:
                v.pos[n] = pos_from[n] = pos_to[n]
        fade_in = [n for n in movers + st.show if v.alpha[n] < 1.0]
        fade_out = [n for n in st.hide if v.alpha[n] > 0.0]

        # 1. Camera to this step's view, while its parts appear beside their places.
        cam_from = [np.array(c, float) for c in v.cam]
        cam_to = [np.array(c, float) for c in st.cam]
        moving = (any(np.linalg.norm(pos_to[n] - pos_from[n]) > 0.01 for n in v.actors)
                  or any(np.linalg.norm(goff_to[g] - goff_from[g]) > 0.01 for g in v.group_off))
        changes = (not all(np.allclose(a, b) for a, b in zip(cam_from, cam_to)) or moving or fade_in or fade_out
                   or st.pre)
        n_cam = 0 if k == 0 or not changes else (lay.cam * (2 if k == 1 else 1))
        for i in range(1, n_cam + 1):
            u = ease(i / n_cam)
            v.cam = [tuple(a + (b - a) * u) for a, b in zip(cam_from, cam_to)]
            for n in v.actors:
                v.pos[n] = pos_from[n] + (pos_to[n] - pos_from[n]) * u
            for g in v.group_off:
                v.group_off[g] = goff_from[g] + (goff_to[g] - goff_from[g]) * u
            if st.pre:
                st.pre(u)
            for n in fade_in:
                v.alpha[n] = u
            for n in fade_out:
                v.alpha[n] = 1 - u
            if not stills:
                v.emit(v.compose(v.render3d(), pan, [], []))
        v.cam = [tuple(c) for c in cam_to]
        for n in v.actors:
            v.pos[n] = pos_to[n]
        v.group_off.update({g: goff_to[g] for g in v.group_off})
        if st.pre:
            st.pre(1.0)
        for n in fade_in:
            v.alpha[n] = 1.0
        for n in fade_out:
            v.alpha[n] = 0.0

        def guides():
            out_ = []
            for m in st.moves:
                for nm in m.names:
                    if nm.startswith("@"):
                        off_now = v.group_off[nm[1:]]
                        out_ += [(g + off_now, g) for g in (m.guide or [])]
                    else:
                        for n in v.members(nm):
                            if n in v.anchors:
                                a = v.apply_m(v.matrix(n), v.anchors[n])
                                b = v.apply_m(v.matrix(n, with_pos=False), v.anchors[n])
                                out_ += list(zip(a, b))
            return [(a, b) for a, b in out_ if np.linalg.norm(a - b) > 1.0]

        # 2. Hold: the parts beside their places, with a dashed line to where each one goes.
        if st.moves:
            img = v.compose(v.render3d(), pan, st.labels, guides())
            v.stills.append((f"{st.number:02d}a", img))
            v.emit(img, lay.staged)

        # 3. Move them in.
        n_move = max(1, round(st.frames * lay.move))
        if not stills and st.moves:
            for i in range(1, n_move + 1):
                for m in st.moves:
                    loc = ease((i / n_move - m.t0) / (m.t1 - m.t0))
                    for nm in m.names:
                        if nm.startswith("@"):
                            v.group_off[nm[1:]] = np.asarray(m.vec, float) * (1 - loc)
                        else:
                            for n in v.members(nm):
                                v.pos[n] = np.asarray(m.vec, float) * (1 - loc)
                v.emit(v.compose(v.render3d(), pan, st.labels, guides()))
        for m in st.moves:
            for nm in m.names:
                if nm.startswith("@"):
                    v.group_off[nm[1:]] = np.zeros(3)
                else:
                    for n in v.members(nm):
                        v.pos[n] = np.zeros(3)

        # 4. Hold, in place; in the last chapter, with the bar turning.
        last = k == len(steps) - 1
        n_hold = max(lay.hold, (lay.chapter + 3 * lay.fps * last) - (v.frame_no - start))
        if k == 0 or last:                               # long enough to read the parts list
            n_hold = max(n_hold, 5 * lay.fps)
        img = v.compose(v.render3d(), pan, st.labels, [])
        v.stills.append((f"{st.number:02d}b" if st.number else st.short, img))
        if st.spin and not stills:
            for i in range(n_hold):
                for n in st.spin:
                    v.spin[n] = (360.0 * 0.8 * i / lay.fps) % 360.0      # 0.8 turns a second
                v.emit(v.compose(v.render3d(), pan, st.labels, []))
        else:
            v.emit(img, n_hold)
        for n in st.xray:                                # see-through only for its own step
            v.base_alpha[n] = v.real_alpha[n]

    v.close()
    if stills:
        d = Path("/tmp/assembly_video_stills" + ("" if lay is MP4 else "_gif"))
        d.mkdir(exist_ok=True)
        for name, img in v.stills:
            img.save(d / f"{name.replace(' ', '_')}.png")
        print("stills in", d)
    if sheet_path is not None:
        sheet(v.stills, sheet_path)


def sheet(stills: list[tuple[str, Image.Image]], path: Path) -> None:
    """Where each step ends, 4 across."""
    ends = [img for name, img in stills if not name.endswith("a")]
    tw, th = 480, 270
    cols = 4
    rows = (len(ends) + cols - 1) // cols
    out = Image.new("RGB", (tw * cols, th * rows), "white")
    for i, img in enumerate(ends):
        out.paste(img.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    out.save(path, optimize=True)
    print(f"{path.name}: {len(ends)} stills")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stills", action="store_true", help="render only the held frames, to /tmp")
    ap.add_argument("--only", choices=["mp4", "gif"], help="make just one of the two")
    a = ap.parse_args()
    if a.only != "gif":
        run(MP4, IMG / "assembly_steps.mp4", a.stills, IMG / "assembly_steps_sheet.png")
    if a.only != "mp4":
        run(GIF, IMG / "assembly_steps.gif", a.stills, None)
