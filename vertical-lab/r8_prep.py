"""Round 8, the prep stream (#303, PR #318): the sample-prep machines of chapter 6 (``alloy_prep.py``) and their tour
clips. ``tour.load()`` lets this module's REGISTRY replace the older builders' keys, so these are the models in every
scene that loads them.

    xvfb-run --server-num=11 -a python3 tour.py mount_press polisher cnc

* **mount_press, the lab's LECO MX400** (new). Modelled from the lab's own video, "Making Bakelite Polishing Puck"
  (https://www.youtube.com/watch?v=9m_hdgmu2Jw): a slim light-grey cabinet, LECO's "8 inch wide profile"; the
  touchscreen low on the front with "MX400" under it; the LECO badge and a vent grille on the sloped upper front; on
  top, the 1.5 in mold (its screen reads "Mold Size 1.50\"" at 6:20) under a stainless swing-arm closure with a knob at
  each end, and the stopper that goes in on top of the compound ("ALWAYS PLACE STOPPER ON TOP GREEN MARBLE END UP" on
  the label beside the mold). The clip follows the video: closure off (0:44), ram up, the specimen face down on the
  ram, ram down, the compound poured in (5:00-5:15), the stopper on, the closure swung back (5:20-5:30), the cycle
  with the screen's values (300, 4.2, 100 and a 10:00 timer: "Heating", 5:40-5:59; "Cooling", 6:04; "Complete",
  6:09), closure off, ram up, the mount out (6:24-6:55). Depth and height are not published: 460 x 480 mm is read off
  the video against the 8 in width (an estimate).
* **polisher, the LECO PX500**, refitted for an arm (``instruments.polisher()`` copied here and changed): 1.5 in
  mounts (``r8_specimens.MOUNT_D``) in the 6-position holder; a magnetic platen; six steel discs, each pre-loaded with
  its SiC paper (320, 400, 600, 800, 1200) or its cloth (for 1 um alumina) **and its own retaining ring**, so the arm
  changes disc, abrasive and ring as one piece by a handle on the ring; a six-shelf magazine for them beside the
  bottle holder; and a head that lifts higher for a disc change (our assumption, as alloy_characterize assumed a lift
  for loading). Why whole discs: peeling a worn paper, laying a new one flat and pressing a retaining ring back on is
  the manual job nobody has automated (notes/edison_r8.md); the one documented automatic route changes whole
  pre-loaded discs (BAM's RASI cell: a QATM QPOL 250 Bot with a magazine of 16).
* **cnc, the Makera Carvera** (``instruments_r7.cnc()`` copied and changed): the job is now the route's own part, the
  wire-EDM slice of the printed AlSi10Mg build (10 x 10 x 6 mm), faced flat and parallel on both sides to 5.6 mm for
  the steel mount (``r8_specimens.steel_mount``). Round 7's job was a generic printed blank.

Frame as in ``instruments.py``: x to the right, y away from you facing the front, z up, origin at the centre of the
footprint, millimetres. Sources and estimates: notes/alloy_prep.md.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments as I
import instruments_r7 as R7
import r8_specimens as SP
from instruments import Instrument, Joint, _piece, _xcyl, _ycyl
from instruments_lab import Timeline, Track, Turn

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import box, cyl, hose, rbox, tube  # noqa: E402

MATERIALS = dict(SP.MATERIALS)
MATERIALS.update({
    "r8p_granules": (0.13, 0.13, 0.14, 1.0, 0.05),     # loose conductive phenolic, before pressing
    "r8p_green": (0.16, 0.55, 0.32, 1.0, 0.45),        # the stopper's green marble end
    "r8p_magnet": (0.24, 0.25, 0.27, 1.0, 0.45),       # the magnetic platen's face
    "r8p_disc": (0.55, 0.56, 0.59, 1.0, 0.55),         # a steel disc's edge
    "r8p_ring": (0.70, 0.71, 0.74, 1.0, 0.55),         # a retaining ring
    "r8p_frame": (0.36, 0.38, 0.42, 1.0, 0.35),        # the magazine's frame
    "r8p_tag320": (0.80, 0.18, 0.15, 1.0, 0.3),        # each grit's handle in its own colour
    "r8p_tag400": (0.95, 0.52, 0.12, 1.0, 0.3),
    "r8p_tag600": (0.95, 0.80, 0.15, 1.0, 0.3),
    "r8p_tag800": (0.25, 0.62, 0.30, 1.0, 0.3),
    "r8p_tag1200": (0.20, 0.42, 0.80, 1.0, 0.3),
    "r8p_tagcloth": (0.92, 0.92, 0.90, 1.0, 0.3),
    "r8p_slice": (0.47, 0.48, 0.50, 1.0, 0.15),        # the slice as cut on the wire EDM
    "r8p_faced": (0.80, 0.81, 0.83, 1.0, 0.8),         # its faces after the CNC
})


def _dummy(at=(0.0, 0.0, 0.0)):
    """An invisible speck, so a piece that only carries a joint (and children) has a group in tour.Rig."""
    return [(pv.Sphere(radius=0.5, center=at, theta_resolution=4, phi_resolution=4), (1.0, 1.0, 1.0), 0.0)]


def _slope(sy, sz):
    L = math.hypot(sy, sz)
    up = np.array([0.0, sy / L, sz / L])
    return up, -math.degrees(math.atan2(up[1], up[2]))


# ===================================================================================================== a. MX400
# LECO MX400 (LECO: "a slim, 8-inch wide profile"; 1.25 in, 1.5 in, 30, 40 and 50 mm molds; 90-200 C; 1200-4300 psi;
# curing 0-30 min (DirectIndustry's copy of LECO's MX400 sheet)). 203 mm wide; 460 deep and 480 to the deck are read
# off the lab's video against that width (estimates). The mold: 1.5 in, the lab's (its screen, 6:20).
MX = dict(W=203.0, D=460.0, H=480.0, slope_z0=300.0, slope_d=110.0, mold=(-25.0, -40.0), post=(40.0, 120.0),
          bore=38.6, depth=75.0, bar_w=56.0, bar_h=36.0, bar_z=486.0, knob_d=50.0, knob_h=24.0, stopper_h=25.0,
          charge=55.0, press=35.0)
RAM_PRESSED = MX["press"] / MX["depth"]          # the ram's joint value once the compound is pressed (rises 35 mm)
# the compound doser (ours): its hopper's post on the deck behind and left of the mold, 74 mm off the closure's line;
# the chute 60 mm over the deck; parked, it points to the back of the deck, out of the closure's swing and the arm's way
DOSER = dict(at=(-60.0, 70.0), z=MX["H"] + 60.0, park_deg=162.0)


def mx_geometry() -> dict:
    p = MX
    mx, my = p["mold"]
    face0 = p["H"] - p["depth"]                    # the ram's face at rest, ram down
    return dict(mx=mx, my=my, face0=face0, top=p["H"], charge_top=face0 + p["charge"],
                stopper_z=face0 + p["charge"])


def mount_press() -> Instrument:
    p = MX
    g = mx_geometry()
    W, D, H = p["W"], p["D"], p["H"]
    mx, my, face0 = g["mx"], g["my"], g["face0"]
    inst = Instrument("mount_press", "Hot mounting press", "LECO MX400", (W, D, H + p["knob_h"] + p["bar_h"] + 6),
                      "the lab's video 'Making Bakelite Polishing Puck' (youtu.be/9m_hdgmu2Jw); LECO: 8 in wide, "
                      "1.25/1.5 in, 30/40/50 mm molds; depth and height read off the video (estimates)")
    body = _piece(inst, "body")
    yf = -D / 2
    cab = box(-W / 2, yf, 0, W / 2, D / 2, H).edges("|Z").fillet(14)
    pts = [(yf - 1, p["slope_z0"]), (yf - 1, H + 1), (yf + p["slope_d"], H + 1)]
    cab = cab.cut(cq.Workplane("YZ").polyline(pts).close().extrude(W + 2).translate((-W / 2 - 1, 0, 0)))
    cab = cab.cut(cyl(p["bore"] + 0.4, p["depth"] + 2, x=mx, y=my, z=face0 - 1))
    body.add("cabinet", cab, "px_grey")
    body.add("mold sleeve", tube(p["bore"] + 14, p["bore"] + 0.4, p["depth"] - 1, x=mx, y=my, z=face0), "stainless")
    body.add("mold ring", tube(72, p["bore"] + 0.6, 1.2, x=mx, y=my, z=H), "inst_black")
    body.add("pivot boss", cyl(48, p["bar_z"] - H, x=p["post"][0], y=p["post"][1], z=H), "stainless")
    # the screen on the vertical front, low; MX400 under it; the warning plate beside the mold
    sz0, sz1 = 115.0, 235.0
    body.add("bezel", box(-82, yf - 2, sz0 - 8, 82, yf, sz1 + 8), "inst_black")
    body.add("touchscreen", box(-72, yf - 3, sz0, 72, yf - 2, sz1), "px_screen")
    ui = box(-64, yf - 3.6, sz0 + 70, -14, yf - 3.0, sz0 + 74)
    for k in (1, 2):
        ui = ui.union(box(-64, yf - 3.6, sz0 + 70 - 24 * k, -14, yf - 3.0, sz0 + 74 - 24 * k))
    body.add("screen rows", ui, "px_ui")
    body.add("screen dial", cq.Workplane("XZ").circle(30).circle(27).extrude(0.6).translate((34, yf - 3.0, sz0 + 58)),
             "px_ui")
    body.add("MX400 label", box(30, yf - 1.2, sz0 - 30, 70, yf - 0.5, sz0 - 20), "inst_dark")
    up, tilt = _slope(p["slope_d"], H - p["slope_z0"])
    base = np.array([0.0, yf, p["slope_z0"]])
    L = math.hypot(p["slope_d"], H - p["slope_z0"])
    logo = box(-62, -1.0, -9, 10, -0.2, 9)
    vent = box(-4, -1.0, -16, 4, -0.2, 16)
    vents = vent.translate((-45, 0, 0))
    for k in range(1, 6):
        vents = vents.union(vent.translate((-45 + 14 * k, 0, 0)))
    for nm, solid, s, mat in (("LECO badge", logo, 0.72, "inst_dark"), ("vent grille", vents, 0.35, "inst_dark")):
        at = base + up * (s * L)
        body.add(nm, solid.rotate((0, 0, 0), (1, 0, 0), tilt).translate(tuple(at)), mat)
    body.add("label plate", box(mx + 30, my - 75, H, mx + 100, my - 45, H + 0.8), "inst_white")
    # the closure: a stainless bar from the pivot post to the mold, a knob at each end; it swings about the post
    px_, py_ = p["post"]
    ang = math.degrees(math.atan2(my - py_, mx - px_))
    Lb = math.hypot(mx - px_, my - py_)
    clo = _piece(inst, "closure")
    bar = rbox(Lb + p["bar_w"], p["bar_w"], p["bar_h"], p["bar_w"] / 2 - 2).translate((Lb / 2, 0, 0))
    clo.add("closure bar", bar.rotate((0, 0, 0), (0, 0, 1), ang).translate((px_, py_, p["bar_z"])), "stainless")
    clo.add("closure knob", cyl(p["knob_d"], p["knob_h"], x=mx, y=my, z=p["bar_z"] + p["bar_h"]).edges(">Z").fillet(4),
            "stainless")
    clo.add("pivot knob", cyl(p["knob_d"] - 6, p["knob_h"] - 4, x=px_, y=py_, z=p["bar_z"] + p["bar_h"])
            .edges(">Z").fillet(4), "stainless")
    # the ram: its face at the bottom of the mold, ram down
    ram = _piece(inst, "ram")
    ram.add("ram", cyl(p["bore"] - 0.2, 70, x=mx, y=my, z=face0 - 70), "chrome")
    # the coupon, face down on the ram (rides on it), placed from above
    spec = _piece(inst, "specimen")
    cx, cy, cz = SP.HOT["coupon"]
    spec.add("coupon", box(mx - cx / 2, my - cy / 2, face0, mx + cx / 2, my + cy / 2, face0 + cz), "r8s_edm")
    # the compound, loose; the pressed mount (the phenolic: the coupon is the specimen piece)
    charge = _piece(inst, "charge")
    charge.add("loose compound", cyl(p["bore"] - 0.4, p["charge"] - 0.5, x=mx, y=my, z=face0 + 0.2).cut(
        box(mx - cx / 2 - 0.3, my - cy / 2 - 0.3, face0, mx + cx / 2 + 0.3, my + cy / 2 + 0.3, face0 + cz + 0.3)),
        "r8p_granules")
    mount = _piece(inst, "mount")
    ph = SP.hot_mount_solids("ground")["phenolic"][0]
    mount.add("pressed mount", ph.rotate((0, 0, 0), (1, 0, 0), 180).translate((mx, my, face0 + SP.FACE_Z)),
              "r8s_phenolic")
    # the stopper: on the compound in the bore, green end up
    stop = _piece(inst, "stopper")
    zs = g["stopper_z"]
    stop.add("stopper", cyl(p["bore"] - 0.6, p["stopper_h"] - 2, x=mx, y=my, z=zs), "stainless")
    stop.add("green end", cyl(p["bore"] - 0.6, 2, x=mx, y=my, z=zs + p["stopper_h"] - 2), "r8p_green")
    heat = _piece(inst, "glow")
    heat.add("heater", tube(64, p["bore"] + 1.0, 0.6, x=mx, y=my, z=H + 1.2), "glow")
    # the compound doser (ours, for the arm; Struers sells one for its own presses, the CitoDoser): a hopper on a
    # post at the deck's back left, its chute swinging over the mold to pour the SOP's 3/4 scoop, then back
    dx_, dy_ = DOSER["at"]
    body.add("doser post", cyl(26, DOSER["z"] - H, x=dx_, y=dy_, z=H), "stainless")
    body.add("doser hopper", cyl(70, 95, x=dx_, y=dy_, z=DOSER["z"] + 25).union(
        cq.Workplane("XY").circle(35).workplane(offset=-25).circle(9).loft().translate((dx_, dy_, DOSER["z"] + 25))),
        "inst_white")
    body.add("doser lid", cyl(74, 6, x=dx_, y=dy_, z=DOSER["z"] + 120), "inst_dark")
    dos = _piece(inst, "doser")
    L_ = math.hypot(mx - dx_, my - dy_)
    a_ = math.degrees(math.atan2(my - dy_, mx - dx_))
    chute = box(0, -9, -6, L_ + 8, 9, 6).translate((0, 0, DOSER["z"] + 6))
    dos.add("doser chute", chute.rotate((0, 0, 0), (0, 0, 1), a_).translate((dx_, dy_, 0)), "stainless")
    dos.add("chute spout", cyl(16, 22, x=mx, y=my, z=DOSER["z"] - 12), "stainless")
    pour = _piece(inst, "pour")
    pour.add("compound falling", cyl(7, DOSER["z"] - 12 - (H - p["depth"] + p["charge"]), x=mx, y=my,
                                     z=H - p["depth"] + p["charge"]), "r8p_granules")
    inst.joints = {
        "closure": Joint("hinge", axis=(0, 0, 1), pivot=(px_, py_, 0), deg=95.0),
        "ram": Joint("slide", vec=(0, 0, p["depth"])),
        "specimen": Joint("path", parent="ram", path=((150, -240, 170), (0, 0, 40), (0, 0, 0))),
        "charge": Joint("fade", parent="ram"),
        "mount": Joint("fade", parent="ram"),
        "stopper": Joint("path", path=((150, -200, 150), (0, 0, 60), (0, 0, 0))),
        "glow": Joint("fade"),
        "doser": Joint("hinge", axis=(0, 0, 1), pivot=(DOSER["at"][0], DOSER["at"][1], 0), deg=DOSER["park_deg"],
                       v0=1.0),
        "pour": Joint("fade", parent="doser"),
    }
    inst.actions = [
        ("The lab's LECO MX400 hot mounting press, as in its video 'Making Bakelite Polishing Puck': 8 in wide, a 1.5 in "
         "mold under a swing-arm closure.", 1.8, {}),
        ("Swing the closure off the mold (0:44 in the video).", 1.4, {"closure": (0.0, 1.0)}),
        ("Ram up: its face rises flush with the top of the mold.", 1.4, {"ram": (0.0, 1.0)}),
        ("The coupon goes on the ram face down: the face to be polished.", 1.8, {"specimen": (0.0, 1.0)}),
        ("Ram down, 75 mm, taking the coupon into the mold.", 1.4, {"ram": (1.0, 0.0)}),
        ("Conductive phenolic (carbon-filled), the SOP's 3/4 scoop, poured in on top from a doser (ours) "
         "(5:00-5:15 in the video, by hand).", 2.4,
         {"doser": (1.0, 0.0), "pour": (0.0, 1.0), "charge": (0.0, 1.0)}),
        ("The doser swings back.", 1.0, {"doser": (0.0, 1.0), "pour": (1.0, 0.0)}),
        ("The stopper on top, green end up, as the label says; the closure swung back and locked (5:20-5:30).", 2.2,
         {"stopper": (0.0, 1.0), "closure": (1.0, 0.0)}),
        ("Heating under pressure, the lab's settings on the screen: 300, 4.2, 100, 10:00 (5:40-5:59). The ram presses "
         "the loose compound into a solid mount.", 3.4,
         {"glow": (0.0, 1.0), "ram": (0.0, RAM_PRESSED), "charge": (1.0, 0.0), "mount": (0.0, 1.0)}),
        ("Cooling, then Complete (6:04-6:09).", 1.6, {"glow": (1.0, 0.0)}),
        ("Closure off, stopper out; the ram rises and pushes the mount out of the mold (6:24-6:42).", 2.6,
         {"closure": (0.0, 1.0), "stopper": (1.0, 0.0), "ram": (RAM_PRESSED, 1.0)}),
        ("A 1.5 in conductive mount, the coupon's face in its underside, ready for the papers.", 1.6, {}),
    ]
    inst.labels = [("1.5 in mold", (mx, my - 20, H), (0.12, 0.30)),
                   ("swing-arm closure", (px_, py_, p["bar_z"] + p["bar_h"] + p["knob_h"]), (0.86, 0.22)),
                   ("touchscreen", (72, yf, 180), (0.86, 0.62))]
    inst.cam = (0.9, -1.5, 1.1)
    inst.framing = (1.0, 0.62)
    near = ((mx, my, H), 650.0)
    inst.zoom = {1: near, 10: "out"}
    inst.props = ("specimen", "charge", "mount", "stopper", "glow", "pour")
    return inst


# ===================================================================================================== b. PX500
# What changes from instruments.polisher(): MOUNT_D (1.5 in), the platen (magnetic, under a removable disc), the
# discs and their magazine, the head's extra lift for a change. The rest is the same model, fitted to the SOP frames.
P5 = dict(I.POLISHER)
MOUNT_D = SP.MOUNT_D
DISC = dict(d=300.0, t=2.0, paper=0.6, cloth=1.4, ring_od=312.0, ring_id=294.0, ring_h=6.0, foot=(150.0, 172.0),
            riser=(164.0, 172.0), grip=(164.0, 215.0), grip_z=(78.0, 92.0), grip_w=20.0)
GRITS = ("320", "400", "600", "800", "1200", "cloth")
MAG = dict(dx=-235.0, w=340.0, d=340.0, z0=22.0, pitch=100.0, rail=14.0, back=12.0)
LIFT = 120.0                     # the head's extra lift for a disc change (ours)
GRIP_HANDLE = 0.70 + (28.0 - DISC["grip_w"]) / 90.0     # 2F-85 closure on a handle's 20 mm grip bar


def px_geometry() -> dict:
    """Where the platen, the disc stack and the magazine are (PX500 frame)."""
    p = P5
    g = I._px500(p)
    pz = p["deck"] + p["platen_z"]                # the abrasive's top (paper), as in instruments.polisher
    disc_z = pz - DISC["t"] - DISC["paper"]       # a disc's underside on the platen
    rx = -g["W"] / 2 - 38                          # the bottle holder's centre (instruments.polisher)
    mag_x = rx - 34 - 12 - MAG["w"] / 2
    shelves = [MAG["z0"] + MAG["pitch"] * i for i in range(len(GRITS))]   # a disc's underside on each shelf
    return dict(bx=g["bx"], by=g["by"], pz=pz, disc_z=disc_z, mag=(mag_x, g["by"]), shelves=shelves,
                hx=g["hx"], hy=g["hy"], g=g)


def disc_solids(kind: str) -> dict:
    """One pre-loaded disc in its own frame (the disc's underside centre; the handle towards -y): {part: (solid, mat)}.
    A steel disc for the magnetic platen, its paper or cloth on top, and the retaining ring over the abrasive's edge
    with a handle (foot, riser, grip bar) in the grit's colour."""
    p = DISC
    top = p["t"] + (p["cloth"] if kind == "cloth" else p["paper"])
    out = {"disc": (cyl(p["d"], p["t"]), "r8p_disc"),
           "abrasive": (cyl(p["d"] - 2, top - p["t"], z=p["t"]), "cloth_white" if kind == "cloth" else "sic_paper")}
    ring = tube(p["ring_od"], p["d"] + 1.0, top, z=0.0).union(
        tube(p["ring_od"], p["ring_id"], p["ring_h"] - top, z=top))
    f0, f1 = p["foot"]
    w = p["grip_w"]
    ring = ring.union(box(-w / 2, -f1, 0, w / 2, -f0 + 4, p["ring_h"]))
    r0, r1 = p["riser"]
    ring = ring.union(box(-w / 2, -r1, p["ring_h"] - 1, w / 2, -r0, p["grip_z"][1]))
    out["ring"] = (ring, "r8p_ring")
    g0, g1 = p["grip"]
    out["handle"] = (box(-w / 2, -g1, p["grip_z"][0], w / 2, -g0, p["grip_z"][1]).edges("|Y").fillet(3),
                     f"r8p_tag{kind}")
    return out


def handle_tcp() -> np.ndarray:
    """The grasp on a disc's handle, in the disc's frame: pointing at the disc's centre (+y), level, the fingers closing
    across the 20 mm grip bar (along x)."""
    M = np.eye(4)
    M[:3, 0] = (1, 0, 0)
    M[:3, 2] = (0, 1, 0)
    M[:3, 1] = np.cross(M[:3, 2], M[:3, 0])
    M[:3, 3] = (0.0, -(DISC["grip"][1] - 22.0), sum(DISC["grip_z"]) / 2)
    return M


def magazine_solids() -> cq.Workplane:
    """The six-shelf magazine (ours), in the PX500's frame: two side walls with a rail per shelf, a back, a top."""
    g = px_geometry()
    m = MAG
    x0, y0 = g["mag"]
    hw, hd = m["w"] / 2, m["d"] / 2
    H = g["shelves"][-1] + DISC["grip_z"][1] + 16
    fr = box(x0 - hw - 8, y0 - hd, 0, x0 - hw, y0 + hd, H).union(box(x0 + hw, y0 - hd, 0, x0 + hw + 8, y0 + hd, H))
    fr = fr.union(box(x0 - hw - 8, y0 + hd, 0, x0 + hw + 8, y0 + hd + m["back"], H))
    fr = fr.union(box(x0 - hw - 8, y0 - hd, H, x0 + hw + 8, y0 + hd + m["back"], H + 8))
    fr = fr.union(box(x0 - hw - 8, y0 - hd, 0, x0 + hw + 8, y0 + hd + m["back"], 6))
    for z in g["shelves"]:
        for s in (-1, 1):
            xa, xb = (x0 - hw, x0 - hw + m["rail"]) if s < 0 else (x0 + hw - m["rail"], x0 + hw)
            fr = fr.union(box(xa, y0 - hd + 10, z - 5, xb, y0 + hd, z))
    return fr


def disc_home(i: int) -> np.ndarray:
    """A disc's frame on shelf i of the magazine, in the PX500's frame."""
    g = px_geometry()
    return I._T((g["mag"][0], g["mag"][1], g["shelves"][i]))


def disc_on_platen() -> np.ndarray:
    g = px_geometry()
    return I._T((g["bx"], g["by"], g["disc_z"]))


def polisher() -> Instrument:
    p = P5
    g = I._px500(p)
    G = px_geometry()
    W, D, yf, bx, by, hx, hy, dk = g["W"], g["D"], g["yf"], g["bx"], g["by"], g["hx"], g["hy"], p["deck"]
    H = dk + p["head_up"] + p["head_h"]
    inst = Instrument("polisher", "Metallographic grinder-polisher, its discs changed by the arm",
                      "LECO PX500 + disc magazine", (W + 2 * 38 + 34 + 12 + MAG["w"] + 16, D, round(H)),
                      "the lab's SOP videos (BYU Vertical Cloud Lab channel), fitted with register.py; LECO's PX400/"
                      "PX500 brochure (form 209-254); the magnetic platen, the pre-loaded discs, their magazine and "
                      "the head's extra lift are ours")
    body = _piece(inst, "body")
    R = p["drum_r"]
    base = (cyl(2 * R, dk, x=bx, y=by)
            .union(box(-W / 2, by, 0, W / 2, D / 2, dk).edges("|Z and >Y").fillet(25))
            .union(box(g["xb"], yf, 0, W / 2, by + 1, dk).edges("|Z and <Y and >X").fillet(14)))
    pts = [(yf - 1, p["slope_z0"]), (yf + p["slope_d"], dk + 1), (yf - 1, dk + 1)]
    cut = cq.Workplane("YZ").polyline(pts).close().extrude(W / 2 - g["xb"] + 2).translate((g["xb"] - 1, 0, 0))
    base = base.cut(cut)
    bowl_floor = dk - 120.0
    rim_r, bowl_r = g["rim_r"], g["bowl_r"]
    base = base.cut(cyl(2 * bowl_r, dk - bowl_floor + 1, x=bx, y=by, z=bowl_floor))
    body.add("base", base, "px_grey")
    body.add("bowl", cyl(2 * bowl_r + 2, 4, x=bx, y=by, z=bowl_floor).union(
        tube(2 * bowl_r + 2, 2 * bowl_r - 6, dk - bowl_floor, x=bx, y=by, z=bowl_floor)), "inst_grey")
    body.add("bowl lip", tube(2 * rim_r, 2 * bowl_r, p["rim_h"], x=bx, y=by, z=dk).edges(">Z").fillet(5), "inst_light")
    up = g["up"]
    tilt = -math.degrees(math.atan2(up[1], up[2]))
    sc = g["sc"]
    S = I.SCREEN
    bez = box(-S[0] / 2 - 12, -3, -S[1] / 2 - 6, S[0] / 2 + 12, 0, S[1] / 2 + 8)
    scr = box(-S[0] / 2, -4, -S[1] / 2, S[0] / 2, -3, S[1] / 2)
    lab = box(S[0] / 2 - 50, -1.2, S[1] / 2 + 20, S[0] / 2, -0.5, S[1] / 2 + 30)
    ui = box(-S[0] / 2 + 8, -4.6, -S[1] / 2 + 12, -S[0] / 2 + 70, -4.0, -S[1] / 2 + 14)
    for k in (1, 2):
        ui = ui.union(box(-S[0] / 2 + 8, -4.6, -S[1] / 2 + 12 + 22 * k, -S[0] / 2 + 70, -4.0, -S[1] / 2 + 14 + 22 * k))
    dial = cq.Workplane("XZ").circle(24).circle(21).extrude(0.6).translate((S[0] / 2 - 42, -4.0, 2))
    for nm, solid, mat in (("bezel", bez, "inst_black"), ("touchscreen", scr, "px_screen"), ("screen rows", ui, "px_ui"),
                           ("screen dial", dial, "px_ui"), ("PX500 label", lab, "inst_dark")):
        body.add(nm, solid.rotate((0, 0, 0), (1, 0, 0), tilt).translate(tuple(sc)), mat)
    ex, ez = p["estop_x"], p["estop_z"]
    body.add("e-stop collar", _ycyl(54, 6, x=ex, y=yf - 6, z=ez), "inst_yellow")
    body.add("e-stop", _ycyl(38, 14, x=ex, y=yf - 18, z=ez).union(_ycyl(26, 8, x=ex, y=yf - 6, z=ez)), "inst_red")
    body.add("deck mat", box(-W / 2 + 15, by + p["drum_r"] * 0.55, dk, W / 2 - 15, D / 2 - 15, dk + 3)
             .cut(cyl(2 * rim_r + 4, 10, x=bx, y=by, z=dk - 1)), "inst_dark")
    cy = hy + p["head_back"] - 40
    body.add("column", rbox(110, 80, p["head_up"] + 55, 12, x=hx, y=cy, z=dk + 5), "inst_grey")
    rx = -W / 2 - 38
    body.add("bottle rack", box(rx - 34, by - 150, 12, rx + 34, by + 150, 18).union(
        box(-W / 2 - 2, by - 150, 12, -W / 2, by + 150, 90)), "steel")
    for i in range(5):
        y = by - 120 + 60 * i
        body.add(f"bottle {i + 1}", cyl(52, 150, x=rx, y=y, z=18).edges(">Z").fillet(10)
                 .union(cyl(20, 14, x=rx, y=y, z=168)), "inst_white")
    _piece(inst, "magazine").add("disc magazine", magazine_solids(), "r8p_frame")   # a prop: on a tray it is its own
    # the head
    head = _piece(inst, "head")
    hz = dk + p["head_up"]
    hcy = g["hcy"]
    housing = rbox(p["head_w"], p["head_d"], p["head_h"], 0.42 * p["head_w"], x=hx, y=hcy, z=hz).edges(">Z").fillet(30)
    head.add("housing", housing.edges("<Z").fillet(8), "px_grey")
    head.add("housing skirt", rbox(p["head_w"] - 70, p["head_d"] - 70, 18, 0.35 * p["head_w"], x=hx, y=hcy, z=hz - 18),
             "inst_dark")
    head.add("lit ring", cyl(118, 34, x=hx, y=hy, z=hz - 52), "led_blue")
    head.add("hub", cyl(70, 26, x=hx, y=hy, z=hz - 78), "inst_dark")
    head.add("spindle", cyl(34, 30, x=hx, y=hy, z=hz - 108), "chrome")
    sx = hx + p["head_w"] / 2
    spout_end = (bx + 105, by + 20, dk + 62)
    hh = p["head_h"]
    head.add("spigot fitting", _xcyl(26, 34, x=sx - 20, y=hy, z=hz + 0.78 * hh), "inst_white")
    head.add("spigot", hose([(sx + 10, hy, hz + 0.78 * hh), (sx + 34, hy - 4, hz + 0.70 * hh),
                             (sx + 44, hy - 8, hz + 0.40 * hh), (sx + 38, hy - 12, hz + 0.05 * hh),
                             (spout_end[0] + 18, spout_end[1], dk + 110), spout_end], 10), "chrome")
    for i in range(2):
        head.add(f"dispenser nozzle {i + 1}", cyl(7, 40, x=hx + 70 + 14 * i, y=hy - 70, z=hz - 40), "steel")
    holder = _piece(inst, "holder")
    hz_h = hz - 120.0
    flower = cyl(p["hold_d"], 12, x=hx, y=hy, z=hz_h)
    for i in range(6):
        a_ = math.radians(30 + 60 * i)
        flower = flower.cut(cyl(MOUNT_D + 1, 14, x=hx + 52 * math.cos(a_), y=hy + 52 * math.sin(a_), z=hz_h - 1))
    holder.add("6-position holder", flower, "stainless")
    for i in range(6):
        a_ = math.radians(30 + 60 * i)
        holder.add(f"mount {i + 1}", cyl(MOUNT_D, SP.FACE_Z, x=hx + 52 * math.cos(a_), y=hy + 52 * math.sin(a_),
                                         z=hz_h - 13), "r8s_phenolic" if i % 3 else "r8s_steel")
    pz = G["pz"]
    platen = _piece(inst, "platen")
    platen.add("magnetic platen", cyl(p["platen_d"], 16, x=bx, y=by, z=G["disc_z"] - 16), "r8p_magnet")
    platen.add("platen hub", cyl(90, G["disc_z"] - 16 - bowl_floor, x=bx, y=by, z=bowl_floor), "steel")
    # the six pre-loaded discs: in the magazine, their handles to the front; the tour moves three of them
    for i, kind in enumerate(GRITS):
        pc = _piece(inst, f"disc_{kind}")
        M = disc_on_platen() if kind in ("320", "400", "cloth") else disc_home(i)
        for nm, (solid, mat) in disc_solids(kind).items():
            v = M[:3, 3]
            pc.add(f"{kind} {nm}", solid.translate(tuple(v)), mat)
    drop = hz_h - 13 - pz
    water = _piece(inst, "water")
    ls = spout_end[2] - drop - pz
    water.add("water", cyl(5, ls, x=spout_end[0], y=spout_end[1], z=spout_end[2] - ls), "water")
    stream = _piece(inst, "powder")
    ls = hz - 40 - drop - pz - 1.4
    stream.add("alumina stream", cyl(4, ls, x=hx + 70, y=hy - 70, z=hz - 40 - ls), "alumina")
    film = _piece(inst, "alumina")
    film.add("alumina on the cloth", tube(250, 90, 0.5, x=bx, y=by, z=pz + 0.8 + DISC["cloth"] - DISC["paper"]),
             "alumina")

    def disc_path(i):
        """Offsets from the disc on the platen: its shelf, out of the magazine, round the front, over the platen."""
        home = disc_home(i)[:3, 3] - disc_on_platen()[:3, 3]
        out_y = -(MAG["d"] + 10.0)
        lift = (dk + p["rim_h"] + 8.0) - G["disc_z"]
        return (tuple(home), tuple(home + (0, 0, 8)), tuple(home + (0, out_y, 8)), (home[0], out_y, lift),
                (0.0, out_y, lift), (0.0, 0.0, lift), (0.0, 0.0, 0.0))
    inst.joints = {
        "head": Joint("slide", vec=(0, 0, -drop)),
        "holder": Joint("spin", parent="head", axis=(0, 0, 1), pivot=(hx, hy, 0), deg=-150.0),
        "platen": Joint("spin", axis=(0, 0, 1), pivot=(bx, by, 0), deg=-720.0),
        "disc_320": Joint("path", parent="platen", path=disc_path(GRITS.index("320"))),
        "disc_400": Joint("path", parent="platen", path=disc_path(GRITS.index("400"))),
        "disc_cloth": Joint("path", parent="platen", path=disc_path(GRITS.index("cloth"))),
        "water": Joint("fade", parent="head"),
        "powder": Joint("fade", parent="head"),
        "alumina": Joint("fade", parent="disc_cloth"),
    }
    up_ = -LIFT / drop                      # the head's joint value with the extra lift
    inst.actions = [
        ("The lab's LECO PX500, refitted for the arm: a magnetic platen, and six steel discs in a magazine, each "
         "pre-loaded with its paper or cloth under its own retaining ring.", 2.4, {}),
        ("The head lifts clear (our extra lift). The arm changes disc, paper and ring as one piece, by the handle on "
         "the ring.", 1.4, {"head": (0.0, up_)}),
        ("320 grit: out of the magazine and onto the magnetic platen, which holds the steel disc flat.", 3.0,
         {"disc_320": (0.0, 1.0)}),
        ("Head down, water on. The SOP's grinding step: head 35 rpm, force 30, platen 150 rpm, 30 s.", 3.4,
         {"head": (up_, 1.0), "platen": (0.0, 1.0), "holder": (0.0, 1.0), "water": (0.0, 1.0)}),
        ("Head up. The 320 disc goes back to its shelf and the 400 comes out: no paper peeled, no ring pried off.",
         3.6, {"head": (1.0, up_), "water": (1.0, 0.0), "disc_320": (1.0, 0.0), "disc_400": (0.0, 1.0)}),
        ("400 grit, then 600, 800 and 1200 the same way (30 s each).", 3.0,
         {"head": (up_, 1.0), "platen": (1.0, 2.0), "holder": (1.0, 2.0), "water": (0.0, 1.0)}),
        ("The cloth disc for the final polish, 1 um alumina from a dispenser: force 3-5, 150 rpm, 3 min.", 3.6,
         {"head": (1.0, up_), "water": (1.0, 0.0), "disc_400": (1.0, 0.0), "disc_cloth": (0.0, 1.0)}),
        ("Head down, suspension on.", 3.0, {"head": (up_, 1.0), "platen": (2.0, 3.0), "holder": (2.0, 3.0),
                                           "powder": (0.0, 1.0), "alumina": (0.0, 1.0)}),
        ("Done. A person re-papers the five SiC discs between batches, off the machine: one fresh paper per grit per "
         "holder load (Buehler's note for its fully automatic VANGUARD: change SiC paper after each holder).", 2.6,
         {"head": (1.0, 0.0), "powder": (1.0, 0.0)}),
    ]
    inst.labels = [("power head", (hx - p["head_w"] / 2, hcy, hz + p["head_h"] * 0.7), (0.30, 0.12)),
                   ("magazine: 320 to 1200 SiC, cloth", (G["mag"][0], G["mag"][1] - MAG["d"] / 2,
                                                         G["shelves"][-1] + 60), (0.10, 0.24)),
                   ("magnetic platen", (bx + 150, by, G["disc_z"]), (0.88, 0.50)),
                   ("6-position holder, 1.5 in mounts", (hx - p["hold_d"] / 2, hy, hz_h), (0.86, 0.20))]
    inst.anchors = I.polisher_anchors(p)
    inst.cam = (0.55, -1.7, 0.9)
    inst.framing = (0.95, 0.40)
    near = ((bx - 120, by - 60, dk), 1500.0)
    inst.zoom = {2: near, 4: near, 8: "out"}
    inst.props = ("holder", "water", "powder", "alumina", "magazine", *[f"disc_{k}" for k in GRITS])
    return inst


def disc_magazine() -> Instrument:
    """The magazine on its own (on tray F it stands apart from the PX500, right of the furnace), its six discs in
    their shelves; frame: its footprint's centre. The tour clip of the PX500 shows it beside the machine instead."""
    G = px_geometry()
    mx, my = G["mag"]
    inst = Instrument("disc_magazine", "Magazine of pre-loaded polishing discs", "six-shelf disc magazine (ours)",
                      (MAG["w"] + 16, MAG["d"] + MAG["back"], round(G["shelves"][-1] + DISC["grip_z"][1] + 24)),
                      "our design: six 300 mm steel discs, each with its paper or cloth and retaining ring")
    body = _piece(inst, "body")
    body.add("frame", magazine_solids().translate((-mx, -my, 0)), "r8p_frame")
    for i, kind in enumerate(GRITS):
        pc = _piece(inst, f"disc_{kind}")
        v = disc_home(i)[:3, 3] - np.array([mx, my, 0.0])
        for nm, (solid, mat) in disc_solids(kind).items():
            pc.add(f"{kind} {nm}", solid.translate(tuple(v)), mat)
    inst.joints = {}
    inst.actions = [("Six steel discs, each pre-loaded with its paper or cloth under its own retaining ring.", 2.0, {})]
    inst.props = tuple(f"disc_{k}" for k in GRITS)
    inst.cam = (0.6, -1.6, 0.9)
    return inst


# ===================================================================================================== c. Carvera
# instruments_r7.cnc(), its job now the route's: the steel mount (r8_specimens.steel_mount) with the wire-EDM slice
# of the printed AlSi10Mg build just seated in its pocket, 0.4 mm proud (6.0 mm as cut in a 5.6 mm pocket). The
# Carvera faces the slice flush with the puck's top: the EDM's recast layer (a few to ~20 um) and the cut's waviness
# come off, and the face ends up parallel to the puck's base, which is what nanoindentation and PIP need. A 6 mm end
# mill, three passes. The puck sits on two short parallels in a small pneumatic vise (ours) whose jaws close across
# it (along y), so the arm's fingers, closing along x, never meet them.
CV = dict(R7.CV)
PUCK = dict(x=60.0, y=0.0, base=12.0, par_h=8.0, par_w=6.0, par_dy=9.0, jaw_h=14.0, jaw_t=14.0, jaw_open=20.0)


def cnc_puck_geometry() -> dict:
    """Where the steel mount sits in the Carvera's vise (Carvera frame): its base, its top (= the faced slice), the
    slice's top as seated."""
    p = CV
    z_base = p["bed_z"] + PUCK["base"] + PUCK["par_h"]
    top = z_base + SP.STEEL["h"]
    return dict(x=PUCK["x"], y=PUCK["y"], z_base=z_base, top=top, seated=top + SP.STEEL["proud"])


def cnc() -> Instrument:
    p = CV
    W, D, H = R7.FOOTPRINTS["cnc"][:3]
    inst = Instrument("cnc", "Desktop CNC mill with a tool changer, facing the steel mount's slice", "Makera Carvera",
                      (W, D, H), "Makera's Carvera spec (580 x 520 x 540 mm, 50 kg, 840 mm lid open, 360 x 240 x "
                      "140 mm, 6-tool changer, 200 W); lid actuator and pneumatic vise ours; layout from photos")
    w, d, h = p["W"], p["D"], p["H"]
    bz = p["bed_z"]
    hy, hz = p["hinge"]
    body = _piece(inst, "body")
    body.add("base", box(-w / 2, -d / 2, 0, w / 2, d / 2, bz - 15).edges("|Z").fillet(20), "r7_carvera")
    body.add("front panel", box(-120, -d / 2 - 1, 90, 120, -d / 2, 170), "inst_dark")
    body.add("front screen", box(-60, -d / 2 - 1.5, 110, 20, -d / 2 - 1, 150), "screen_on")
    body.add("back wall", box(-w / 2, hy, bz - 15, w / 2, d / 2, h).edges("|Z").fillet(10), "r7_carvera")
    for x0 in (-w / 2, w / 2 - 10):
        body.add(f"sill {x0:.0f}", box(x0, -d / 2 + 10, bz - 15, x0 + 10, hy, 300), "r7_carvera")
    for x0 in (-275.0, 255.0):
        body.add(f"rail {x0:.0f}", box(x0, -240, 290, x0 + 20, hy, 300), "steel")
    body.add("bed", box(-200, -150, bz - 15, 200, 150, bz), "aluminium")
    for k in range(5):
        y = -120 + 60 * k
        body.add(f"T-slot {k}", box(-200, y - 4, bz - 0.4, 200, y + 4, bz + 0.2), "inst_dark")
    body.add("tool rack", box(-200, -125, 280, -170, 125, 290).cut(
        cq.Workplane("XY").pushPoints(list(p["slots"])).circle(4.5).extrude(12).translate((0, 0, 279))), "inst_dark")
    body.add("rack post", box(-200, -125, bz, -190, 125, 280), "inst_dark")
    for i, (x, y) in enumerate(p["slots"][2:]):
        col, sh = R7._tool(x, y, p["tool_top"])
        body.add(f"tool {i + 2} collar", col, "steel")
        body.add(f"tool {i + 2}", sh, "r7_carbide")
    # the vise for a 1.5 in mount (ours): a base plate, two short parallels under the puck, jaws across it along y
    G = cnc_puck_geometry()
    sx_, sy_, zb = G["x"], G["y"], G["z_base"]
    R_ = SP.STEEL["d"] / 2
    pz0 = bz + PUCK["base"]
    jz1 = zb + PUCK["jaw_h"]
    body.add("vise base", box(sx_ - 45, sy_ - 52, bz, sx_ + 45, sy_ + 52, pz0), "steel")
    for s_ in (-1, 1):
        yc = sy_ + s_ * PUCK["par_dy"]
        body.add(f"parallel {s_}", box(sx_ - 12, yc - PUCK["par_w"] / 2, pz0, sx_ + 12, yc + PUCK["par_w"] / 2, zb),
                 "steel")
    body.add("fixed jaw", box(sx_ - 30, sy_ + R_ + 0.05, pz0, sx_ + 30, sy_ + R_ + 0.05 + PUCK["jaw_t"], jz1), "steel")
    body.add("air cylinder", box(sx_ - 30, sy_ - 80, bz, sx_ + 30, sy_ - R_ - PUCK["jaw_t"] - PUCK["jaw_open"] - 2,
                                 pz0 + 16), "inst_blue")
    body.add("lid actuator", cyl(30, 220, x=w / 2 + 15, y=hy + 20, z=300), "inst_dark")
    body.add("actuator mount", box(w / 2, hy + 5, 300, w / 2 + 30, hy + 35, 315), "inst_dark")
    jaw = _piece(inst, "jaw")
    jaw.add("moving jaw", box(sx_ - 30, sy_ - R_ - 0.05 - PUCK["jaw_t"], pz0, sx_ + 30, sy_ - R_ - 0.05, jz1), "steel")
    lid = _piece(inst, "lid")
    lid.add("lid top", box(-w / 2, -d / 2, h - 10, w / 2, hy, h), "r7_carvera_lid")
    lid.add("lid front", box(-w / 2, -d / 2, bz - 15, w / 2, -d / 2 + 10, h - 10), "r7_carvera_lid")
    for s in (-1, 1):
        x0 = w / 2 - 10 if s > 0 else -w / 2
        lid.add(f"lid side {s}", box(x0, -d / 2 + 10, 300, x0 + 10, hy, h - 10), "r7_carvera_lid")
    lid.add("lid handle", box(-80, -d / 2 - 14, h - 60, 80, -d / 2, h - 40), "inst_dark")
    lid.add("lid arm", box(w / 2, hy - 50, h - 40, w / 2 + 10, hy - 5, h - 10), "inst_dark")
    gan = _piece(inst, "gantry")
    gan.add("beam", box(-262, -20, 440, 262, 20, 490), "inst_dark")
    for s in (-1, 1):
        x0 = 255 if s > 0 else -275
        gan.add(f"upright {s}", box(x0, -25, 300, x0 + 20, 25, 440), "inst_dark")
    car = _piece(inst, "carriage")
    car.add("carriage", box(-40, -50, 420, 40, -20.5, 500), "r7_carvera")
    spn = _piece(inst, "spindle")
    sy = p["sp_y"]
    spn.add("spindle", cyl(52, 120, x=0, y=sy, z=p["nose"] + 20), "steel")
    spn.add("spindle cap", cyl(54, 10, x=0, y=sy, z=p["nose"] + 120), "inst_dark")
    spn.add("nose", cyl(22, 20, x=0, y=sy, z=p["nose"]), "chrome")
    tools = {}
    for nm, (x, y) in (("tool_a", p["slots"][0]), ("tool_b", p["slots"][1])):
        col, sh = R7._tool(x, y, p["tool_top"])
        tp = _piece(inst, nm)
        tp.add(nm + " collar", col, "steel")
        tp.add(nm, sh, "r7_carbide")
        tools[nm] = (x, y)
    # the steel mount: carried in (carrier: path); the slice's 0.4 mm proud skin ("stock") goes under the end mill
    inst.meshes["carrier"] = _dummy((sx_, sy_, zb + 10))
    sol = SP.steel_mount_solids("polished")
    part = _piece(inst, "part")
    part.add("steel puck", sol["puck"][0].translate((sx_, sy_, zb)), "r8s_steel")
    part.add("ball plunger", sol["screw"][0].translate((sx_, sy_, zb)), "r8s_screw")
    part.add("slice, faced", sol["slice"][0].translate((sx_, sy_, zb)), "r8p_faced")
    a2 = SP.STEEL["slice"][0] / 2
    st1 = _piece(inst, "stock")
    st1.add("slice as cut, 0.4 mm proud", box(sx_ - a2, sy_ - a2, G["top"], sx_ + a2, sy_ + a2, G["seated"]),
            "r8p_slice")
    # one timeline: gantry y, carriage x, spindle z, which tool rides the spindle
    tl = Timeline(dict(gy=120.0, cx=150.0, sz=20.0, a="rack", b="rack"))
    ga = tools["tool_a"][1] - sy
    grab = p["tool_top"] - p["nose"]
    cut_z = G["top"] - p["nose"] + 1.0 + 12.0          # the end mill's tip at the puck's top (tool stick-out ~12 mm)
    tl.go(1.4, cx=tools["tool_a"][0], gy=ga).go(0.8, sz=grab).go(0.3, a="sp").go(0.8, sz=20.0).mark("tool_a")
    tl.go(1.0, cx=sx_ - 12.0, gy=sy_ - 4.0 - sy).go(0.5, sz=cut_z)
    for k, yy in enumerate((-4.0, 0.0, 4.0)):
        if k:
            tl.go(0.25, gy=sy_ + yy - sy)
        tl.go(0.9, cx=sx_ + 12.0 if k % 2 == 0 else sx_ - 12.0)
    tl.go(0.5, sz=20.0).mark("faced")
    tl.go(1.4, cx=tools["tool_a"][0], gy=ga).go(0.8, sz=grab).go(0.3, a="rack").go(0.8, sz=20.0)
    tl.go(1.4, cx=150.0, gy=120.0).mark("park")

    def tool_off(name, key):
        tx, ty = tools[name]

        def f(s):
            if s[key] == "rack":
                return (0.0, 0.0, 0.0)
            return (s["cx"] - tx, sy + s["gy"] - ty, p["nose"] + s["sz"] - p["tool_top"])
        return f
    inst.joints = {
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(0, hy, hz), deg=p["lid_deg"]),
        "jaw": Joint("slide", vec=(0, -PUCK["jaw_open"], 0), v0=1.0),
        "carrier": Joint("path", path=((0, -420, 220), (0, -160, 140), (0, 0, 40), (0, 0, 0))),
        "part": Joint("fade", parent="carrier", v0=1.0),
        "stock": Joint("fade", parent="carrier", v0=1.0),
        "gantry": Track(knots=tl.knots(lambda s: (0.0, s["gy"], 0.0))),
        "carriage": Track(knots=tl.knots(lambda s: (s["cx"], 0.0, 0.0)), parent="gantry"),
        "spindle": Track(knots=tl.knots(lambda s: (0.0, 0.0, s["sz"])), parent="carriage"),
        "tool_a": Track(knots=tl.knots(tool_off("tool_a", "a"))),
        "tool_b": Track(knots=tl.knots(tool_off("tool_b", "b"))),
    }
    V = tl.v
    tv = lambda a, b: {k: (a, b) for k in ("gantry", "carriage", "spindle", "tool_a", "tool_b")}  # noqa: E731
    inst.actions = [
        ("Chapter 6's job for the Carvera: the steel mount, the wire-EDM slice of the printed AlSi10Mg build seated "
         "in its pocket, 0.4 mm proud. The lid opens.", 2.2, {"lid": (0.0, 1.0)}),
        ("The arm sets the mount on the parallels in a small vise (ours).", 2.2, {"carrier": (0.0, 1.0)}),
        ("The vise clamps it; the lid closes. A 6 mm end mill from the tool changer.", 3.0,
         {"jaw": (1.0, 0.0), "lid": (1.0, 0.0), **tv(0.0, V("tool_a"))}),
        ("The slice faced flush with the puck: the EDM's recast layer off, the face parallel to the puck's base.", 5.0,
         {**tv(V("tool_a"), V("faced")), "stock": (1.0, 0.0)}),
        ("The end mill back in the rack; the lid opens and the vise lets go. Next: grinding and polishing.", 3.0,
         {**tv(V("faced"), 1.0), "lid": (0.0, 1.0), "jaw": (0.0, 1.0)}),
    ]
    inst.zoom = {1: ((sx_, sy_, G["top"]), 520.0), 3: ((sx_, sy_, G["top"]), 420.0), 4: "out"}
    inst.labels = [("6-tool changer", (-185, -125, 290), (0.10, 0.30)),
                   ("vise for 1.5 in mounts (ours)", (sx_, sy_ - 52, pz0), (0.20, 0.80)),
                   ("lid actuator (ours)", (w / 2 + 15, hy + 20, 480), (0.88, 0.22)),
                   ("200 W spindle", (0, sy - 26, p["nose"] + 80), (0.62, 0.12))]
    inst.cam = (0.8, -1.7, 1.0)
    inst.props = ("carrier", "part", "stock")
    return inst


REGISTRY = {"mount_press": mount_press, "polisher": polisher, "cnc": cnc, "disc_magazine": disc_magazine}

# tray F (polishing and heat treatment), set by its camera posts (services.TRAY_CAMS["F"]): the press at the back
# left, behind camera F0's post; the disc magazine at the front right, right of camera F1's post, in front of the UPS
# and the dock plate; the PX500 and the furnace where they were (line.TRAY_LOADS)
TRAY_PLACEMENT = {
    "mount_press": dict(tray="F", x=-1095.0, y=125.0, turn=0.0),
    "disc_magazine": dict(tray="F", x=1022.0, y=-190.0, turn=0.0),
}


if __name__ == "__main__":
    for key, fn in REGISTRY.items():
        inst = fn()
        print(key, [round(v) for v in inst.bbox()], {k: len(m.parts) for k, m in inst.pieces.items()})
