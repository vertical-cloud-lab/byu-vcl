"""The copper corrosion spot on the CubXL, start to finish, as a video. Writes cubxl-cu-spot.mp4
(1280 x 720, 30 fps), a shorter cubxl-cu-spot.gif preview (640 x 360) and stills.

What it shows, in order:
1. The real CubXL, empty: Ben's photo from #133 (2026-06-26).
2. The model of the same machine, seen from the photo's side, turning to the working view.
3. Every deck module, then every tool on the gantry head, placed one at a time with a short name.
4. What is made and done by hand before a night: stock alloys and DED pads, specimens,
   seawater and sulfide stocks, acid, tubes, the reference check (cards).
5. One spot, step by step. The head is rigid, so every tool goes down when one does; the tool
   that is doing the work is outlined in orange and lit in the panel at the top right, and its
   target on the deck is ringed.
6. After the night: ICP-MS of the tubes, SEM of the spots (a card), and an outro.

Where the geometry comes from:
- Exact models: the three STEP files in modules/electromagnetic-capper/cad/ (Ben's 9-position
  20 mL vial holder, the magnetic vial cap, the PAW-V2 electromagnet mount), meshed with gmsh,
  and the electrode cap, well lid and coupon tray from cad/ (CadQuery, this PR), when present.
- Exact numbers: deck positions, tool offsets (pipette +55, +11; camera -40, +10), tool hang
  (magnet face 16 mm below the carriage, 35 mm tip), working volume 361 x 278 x 122 and travel
  height from Ben's 2026-10-02 gantry and deck files, via deck_cu.py and ../plot_deck_layout.py.
- The well during the measurement: O2 and dissolved Cu fields from sim_well_hf.py when its
  fields file exists, else sim_well.py.
- Schematic, with the right proportions from the photos and the working volume: the
  PROVerXL 4030 V2 frame, gantry and Z carriage, the P20 body, the camera.

    xvfb-run -a python render_cubxl_cu.py                 # about 12 min on 4 cores
    xvfb-run -a python render_cubxl_cu.py --stills 2,9,40  # PNG stills at these seconds, no video
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CAD = REPO / "modules" / "electromagnetic-capper" / "cad"
CU_CAD = HERE / "cad"
PHOTO = HERE / "media" / "cubxl-empty-ben-2026-06-26.jpg"
sys.path.insert(0, str(HERE))
import deck_cu  # noqa: E402

base = deck_cu.base
W, H = 1280, 720
FPS = 30
GW, GH = 640, 360

# ------------------------------------------------------------------ geometry constants (mm)
FACE_Z, LID_TOP = base.TRAY["face_z"], base.TRAY["top"]  # 20, 26
TRAVEL = base.TRAVEL_Z  # 122
PIP = base.PIP_OFF  # (55, 11)
CAM_OFF = (-40.0, 10.0)
MAGNET_HANG = 16.0
TIP_LEN = 35.0
VIAL_RIM, VIAL_CAP_TOP = 56.0, 71.0
S_X, S_Y = base.STATION_X, base.STATION_Y
S1 = (S_X[0], S_Y)
A_SPOT, Z_STEP, R_BORE = 1.45, 1.6, 4.0  # AS568-006 ID / 2, throat, 8 mm bore
REF_TIP = 3.0  # cap B: reference tip 3.0 mm above the metal
CAP_PROTRUDE = 6.0 - REF_TIP  # electrodes below the skirt, which rests on the 6 mm lid
CAP_HANG = MAGNET_HANG + 16.0 + CAP_PROTRUDE  # 35.0
CUT0, CUT_SWEEP = -45.0, 270.0  # section views keep -45..225 deg; the front quadrant is cut away
PARK = (236.0, 25.0)  # the capper's park position in Ben's gantry file

# the machine frame (schematic; PROVerXL 4030 V2 proportions from the photos)
GANTRY_DY = 60.0  # the X beam's front face is 60 mm behind the capper axis
BEAM_X = (-120.0, 480.0)

ORANGE = (235, 104, 52)
NO_OUTLINE = ("tip0_", "tips1", "liq:", "vcap:", "pad", "oring", "cupliq:", "tubes", "slots", "pstat_face", "eyelets", "holdmag", "ecap:pogo", "ecap:coil", "ecap:holdsteel", "ecap:ref", "ecap:carrier")
ORANGE_HEX = "#eb6834"
C = {  # material colours
    "table": "#e9e7e1", "deck": "#e4ebee", "slot": "#c2ccd2", "alu": "#c3c6c9", "alu_dark": "#9fa4a8", "blue": "#2456a6",
    "black": "#2b2b2b", "petg": "#dedbd2", "petg_dark": "#c8c3b5",
    "tray": "#f4efe6", "lid": "#e9a47c", "glass": "#e8f1f6", "capbody": "#efe9e2", "steel": "#8d9196", "fkm": "#1d1d1d",
    "cuni": "#b89a8a", "nab": "#c39b55", "ded": "#c08a62", "ptfe": "#f7f7f5", "pt": "#c7c9cc",
    "agcl": "#e9e6df", "tip": "#f2f2ee", "tube": "#f4f4f0", "pip": "#1c1c1c", "pip_shaft": "#e7e7e3", "pip_top": "#4a4a4a",
    "brass": "#c9a64a", "pstat": "#2f4a6b", "asw": "#9cc7e8", "sulf": "#e6d58a", "acid": "#f3f0e6",
    "water": "#d9ecf7", "mount": "#9c9b97",
}


def step_mesh(name, size, curv):
    """Mesh a STEP file with gmsh (OpenCASCADE) and return it as PolyData. Cached in /tmp."""
    out = Path(tempfile.gettempdir()) / f"cubxl_cu_{name}_{size}_{curv}.stl"
    if not out.exists():
        import gmsh
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("Mesh.MeshSizeMax", size)
        gmsh.option.setNumber("Mesh.MeshSizeMin", size / 4)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", curv)
        gmsh.option.setNumber("Mesh.Algorithm", 6)
        gmsh.model.occ.importShapes(str(CAD / f"{name}.step"))
        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)
        gmsh.write(str(out))
        gmsh.finalize()
    return pv.read(out).clean()


def cad_parts():
    """cad/cad_parts.json, written by cad/cad_cu_cell.py: STL names and their frames."""
    f = CU_CAD / "cad_parts.json"
    return json.loads(f.read_text()) if f.exists() else {}


def cad_mesh(stem):
    f = CU_CAD / f"{stem}.stl"
    if not f.exists():
        return None
    m = pv.read(f).clean()
    return m.compute_normals(auto_orient_normals=False, split_vertices=True, feature_angle=35) if m.n_points else None


def revolve(profile_rz, sweep=360.0, start=0.0, res=None):
    """Revolve a closed (r, z) profile about the z axis. Returns PolyData with end caps."""
    pts = np.array([[r, 0.0, z] for r, z in profile_rz])
    poly = pv.PolyData(pts, faces=np.hstack([[len(pts)], np.arange(len(pts))]))
    res = res or max(8, int(sweep / 6))
    m = poly.extrude_rotate(resolution=res, angle=sweep, capping=sweep < 360, rotation_axis=(0, 0, 1))
    if start:
        m = m.rotate_z(start, inplace=False)
    return m.triangulate().clean().compute_normals(auto_orient_normals=True, split_vertices=True, feature_angle=40)


def box(x0, y0, z0, x1, y1, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1))


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------ the scene
class Scene:
    def __init__(self):
        pv.global_theme.allow_empty_mesh = True
        self.pl = pv.Plotter(off_screen=True, window_size=(W, H), lighting="light_kit")
        self.pl.set_background("#f6f5f1")
        self.pl.enable_anti_aliasing("fxaa")
        self.actors, self.meshes, self.colors = {}, {}, {}
        self.groups = {}  # group -> actor keys (placement, highlight)
        self.home = {}  # actor key -> its resting matrix for the frame (set each frame)
        self.sil = {}
        self.cad = cad_parts()
        self.build_frame()
        self.build_deck()
        self.build_head()
        self.build_ecap()
        self.load_field()
        self.build_marker()

    def add(self, key, mesh, group=None, **kw):
        kw.setdefault("smooth_shading", True)
        kw.setdefault("specular", 0.15)
        a = self.pl.add_mesh(mesh, **kw)
        self.actors[key] = a
        self.meshes[key] = mesh
        self.colors[key] = kw.get("color")
        if group:
            self.groups.setdefault(group, []).append(key)
        return a

    # ---- the machine: base, deck plate, gantry, carriage (schematic PROVerXL 4030 V2)
    def build_frame(self):
        add = self.add
        add("table", box(-400, -420, -62, 860, 700, -56), color=C["table"], smooth_shading=False, specular=0.0)
        for x0 in (-120.0, 440.0):  # Y rails
            add(f"yrail{x0}", box(x0, -95, -56, x0 + 40, 425, -10), color=C["alu"], smooth_shading=False, specular=0.4)
            for k in range(3):  # extrusion grooves
                add(f"ygroove{x0}{k}", box(x0 + 8 + 12 * k, -95.2, -50, x0 + 10 + 12 * k, 425.2, -16), color=C["alu_dark"], smooth_shading=False)
        for y0 in (-95.0, 385.0):  # front and back members
            add(f"xmem{y0}", box(-120, y0, -56, 480, y0 + 40, -14), color=C["alu"], smooth_shading=False, specular=0.4)
        for x0, x1 in ((-128, -120), (480, 488)):  # blue corner plates
            for y0, y1 in ((-100, -25), (350, 430)):
                add(f"corner{x0}{y0}", box(x0, y0, -62, x1, y1, 14), color=C["blue"], smooth_shading=False, specular=0.3)
        add("deckplate", box(-80, -55, -10, 440, 385, 0), color=C["deck"], smooth_shading=False, specular=0.5, opacity=0.95)
        slots = [box(x - 4, y - 11, -0.05, x + 4, y + 11, 0.25) for x in np.arange(-62, 430, 30.0) for y in np.arange(-38, 380, 30.0)]
        add("slots", pv.merge(slots), color=C["slot"], smooth_shading=False, specular=0.0)
        wv = box(0, 0, 0.3, 361, 278, 0.7)
        add("wv", wv.extract_feature_edges(), color="#8f8e88", line_width=1.2, smooth_shading=False)
        # gantry: moves in y with the head (y_axis_motion: head)
        g = []
        g.append(("gside_l", box(-134, GANTRY_DY - 8, -60, -122, GANTRY_DY + 52, 240), C["blue"]))
        g.append(("gside_r", box(482, GANTRY_DY - 8, -60, 494, GANTRY_DY + 52, 240), C["blue"]))
        g.append(("beam_lo", box(BEAM_X[0], GANTRY_DY, 165, BEAM_X[1], GANTRY_DY + 36, 200), C["alu"]))
        g.append(("beam_hi", box(BEAM_X[0], GANTRY_DY, 205, BEAM_X[1], GANTRY_DY + 36, 240), C["alu"]))
        for zg in (180, 220):
            g.append((f"beam_groove{zg}", box(BEAM_X[0], GANTRY_DY - 0.3, zg, BEAM_X[1], GANTRY_DY, zg + 3), C["alu_dark"]))
        g.append(("xmotor", box(-182, GANTRY_DY - 2, 190, -134, GANTRY_DY + 40, 232), C["black"]))
        g.append(("xlabel", box(-182.3, GANTRY_DY + 8, 206, -170, GANTRY_DY + 30, 216), "#e5c62e"))
        g.append(("chain", box(-60, GANTRY_DY + 6, 240, 420, GANTRY_DY + 30, 252), C["black"]))
        for k, m, col in g:
            add(f"gantry:{k}", m, color=col, smooth_shading=False, specular=0.35, group="gantry")
        # X carriage and Z axis body: move in x and y, not z
        add("xcar", box(-42, GANTRY_DY - 24, 150, 42, GANTRY_DY, 300), color=C["alu"], smooth_shading=False, specular=0.4, group="xcar")
        add("zmotor", box(-20, GANTRY_DY - 22, 300, 20, GANTRY_DY - 2, 342), color=C["black"], smooth_shading=False, group="xcar")

    # ---- the deck modules
    def build_deck(self):
        add = self.add
        # coupon tray (printed) with four stations: S1 C71500 Cu-Ni, S2 C95800 NAB, S3 DED pad, S4 PTFE blank
        x0, y0, x1, y1 = base.TRAY["rect"]
        materials = ["cuni", "nab", "ded", "ptfe"]
        self.cad_ok = cad_mesh("well_lid") is not None and cad_mesh("coupon_tray_minus_s1") is not None
        if self.cad_ok:
            W0 = lambda i: (S_X[i], S_Y, FACE_Z)  # noqa: E731  (well frame W -> deck)
            add("tray", cad_mesh("coupon_tray_minus_s1"), group="tray", color=C["tray"])
            add("tray_s1", cad_mesh("tray_station").translate(W0(0), inplace=False), group="tray", color=C["tray"])
            add("tray_s1_sec", cad_mesh("tray_station_section").translate(W0(0), inplace=False), group="tray", color=C["tray"])
            lid_parts = [("lid", "well_lid", C["lid"]), ("oring", "face_oring_006", C["fkm"]), ("pads", "lid_pads", "#c47a45"),
                         ("eyelets", "lid_eyelets", C["brass"]), ("holdmag", "lid_hold_magnets", "#9a9ea3")]
            for i in range(4):
                stem = "coupon_20x20x6" if i < 3 else "ptfe_blank"
                grp = "blank" if i == 3 else "coupons"
                for suffix in (("", "_section") if i == 0 else ("",)):
                    key = f"coupon{i}{suffix}"
                    add(key, cad_mesh(stem + suffix).translate(W0(i), inplace=False), group=grp, color=C[materials[i]],
                        specular=0.6 if i < 3 else 0.1, specular_power=30)
                for k, stem2, col in lid_parts:
                    for suffix in (("", "_section") if i == 0 else ("",)):
                        add(f"{k}{i}{suffix}", cad_mesh(stem2 + suffix).translate(W0(i), inplace=False), group="lids", color=col,
                            lighting=k != "oring", specular=0.6 if k in ("eyelets", "holdmag", "pads") else 0.15)
            self.sec_pairs = [("tray_s1", "tray_s1_sec"), ("coupon0", "coupon0_section")] + [(f"{k}0", f"{k}0_section") for k, _, _ in lid_parts]
        else:
            add("tray", box(x0, y0, 0, x1, y1, FACE_Z), group="tray", color=C["tray"], smooth_shading=False)
            lid_prof = [(A_SPOT, 1.42), (3.45, 1.42), (3.45, 0.0), (8.0, 0.0), (8.0, 6.0), (R_BORE, 6.0), (R_BORE, Z_STEP), (A_SPOT, Z_STEP)]
            oring = [(2.4 + 0.94 * math.cos(t), 0.71 + 0.70 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 28, endpoint=False)]
            coupon_prof = [(0.0, -3.0), (6.0, -3.0), (6.0, 0.0), (0.0, 0.0)]
            for i, sx in enumerate(S_X):
                sweep, start = (CUT_SWEEP, CUT0) if i == 0 else (360.0, 0.0)
                add(f"lid{i}", revolve(lid_prof, sweep, start).translate((sx, S_Y, FACE_Z), inplace=False), group="lids", color=C["lid"])
                add(f"oring{i}", revolve(oring, sweep, start).translate((sx, S_Y, FACE_Z), inplace=False), group="lids", color=C["fkm"], lighting=False)
                add(f"coupon{i}", revolve(coupon_prof, sweep, start).translate((sx, S_Y, FACE_Z + 0.01), inplace=False), group="blank" if i == 3 else "coupons",
                    color=C[materials[i]], specular=0.6 if i < 3 else 0.1, specular_power=30)
                for px in (sx - 11, sx + 11):  # reference / counter pads
                    add(f"pad{i}{px}", box(px - 1.5, S_Y - 3, LID_TOP - 0.01, px + 1.5, S_Y + 3, LID_TOP + 0.6), group="lids", color=C["brass"], specular=0.6)
            self.sec_pairs = []

        # Ben's 9-position holder (STEP), rotated so its positions run +Y from y 35
        holder = step_mesh("9VialHolder20mL_TightFit", 4.0, 8).rotate_z(180, inplace=False).translate((deck_cu.HOLDER_X, deck_cu.HOLDER_Y[0], 0), inplace=False)
        add("holder", holder, group="holder", color=C["petg_dark"], smooth_shading=False)
        self.vial_cap_mesh = step_mesh("VialCap16mm", 1.5, 12)
        liquids = {"1 M HNO3, trace metal": C["acid"], "ASW (D1141, no heavy metals)": C["asw"], "ASW + 10 mg/L S": C["sulf"],
                   "ASW + 0.1 mg/L S": "#ece2b4", "DI water": C["water"], "spare (FeSO4 nights only)": "#cfe0c8"}
        self.vials = {}
        for name, (vx, vy) in {**deck_cu.STOCKS, **deck_cu.SPARE}.items():
            add(f"vial:{name}", pv.Cylinder(center=(vx, vy, VIAL_RIM / 2), direction=(0, 0, 1), radius=13.75, height=VIAL_RIM, resolution=48, capping=True),
                group="vials", color=C["glass"], opacity=0.35, specular=0.6)
            add(f"liq:{name}", pv.Cylinder(center=(vx, vy, 19), direction=(0, 0, 1), radius=12.6, height=36, resolution=48), group="vials",
                color=liquids[name], opacity=0.85)
            add(f"vcap:{name}", self.vial_cap_mesh.translate((vx, vy, VIAL_CAP_TOP - 0.5), inplace=False), group="vials", color="#e3e1da")
            self.vials[name] = (vx, vy)

        # tip racks (panda_2x15) and tips: 20 uL tips as cones, top at 66, end 35 below the nozzle seat
        tip_prof = [(0.0, 0.0), (0.45, 0.0), (2.6, 30.0), (2.9, 37.0), (3.3, 39.0), (0.0, 39.0)]
        self.tip_mesh = revolve(tip_prof, 360, 0, res=24)
        for ri, rack in enumerate((base.TIP_RACK_1, base.TIP_RACK_2)):
            rx0, ry0, rx1, ry1 = base.rack_rect(rack)
            grp = f"rack{ri + 1}"
            add(f"rack{ri}", box(rx0, ry0, 0, rx1, ry1, 55), group=grp, color=C["petg_dark"] if ri == 0 else C["petg"], smooth_shading=False)
            tips = [self.tip_mesh.translate((tx, ty, 66.0 - 39.0), inplace=False) for (tx, ty) in base.rack_tips(rack)]
            if ri == 0:
                self.rack1_tips = list(base.rack_tips(rack))
                self.tip_actors = [add(f"tip{ri}_{j}", m, group=grp, color=C["tip"], specular=0.3) for j, m in enumerate(tips)]
            else:
                add(f"tips{ri}", pv.merge(tips), group=grp, color=C["tip"], specular=0.3)

        # tube rack: 2 x 8 open 0.5 mL PP tubes
        tx0, ty0, tx1, ty1 = base.TUBE_RACK["rect"]
        add("tuberack", box(tx0, ty0, 0, tx1, ty1, 20), group="tubes", color=C["petg"], smooth_shading=False)
        tube_prof = [(0.0, 0.0), (1.2, 0.0), (3.6, 12.0), (3.9, 32.0), (4.6, 32.0), (4.6, 30.5), (4.2, 30.5), (4.2, 12.2), (1.6, 0.6), (0.0, 0.6)]
        tube = revolve(tube_prof, 360, 0, res=32)
        self.tubes = [(x, y) for y in base.TUBE_Y for x in base.TUBE_X]
        add("tubes", pv.merge([tube.translate((x, y, 0), inplace=False) for x, y in self.tubes]), group="tubes", color=C["tube"], opacity=0.75, specular=0.4)
        add("tube1_liq", pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=3.4, height=1.0, resolution=24), color=C["asw"], opacity=0.9)

        # cups (4 mL vials): rinse 2 ASW, rinse 1 DI, park
        for name, (cx, cy) in deck_cu.CUPS.items():
            add(f"cup:{name}", pv.Cylinder(center=(cx, cy, 22.5), direction=(0, 0, 1), radius=7.5, height=45, resolution=40), group="cups",
                color=C["glass"], opacity=0.4, specular=0.6)
            add(f"cupliq:{name}", pv.Cylinder(center=(cx, cy, 22), direction=(0, 0, 1), radius=6.6, height=40, resolution=40), group="cups",
                color=C["asw"] if "ASW" in name else (C["water"] if "DI" in name else "#d8d2ea"), opacity=0.8)
        tw = deck_cu.TIP_WASTE
        add("tipwaste", pv.Cylinder(center=(*tw["c"], tw["top"] / 2), direction=(0, 0, 1), radius=tw["r"], height=tw["top"], resolution=48),
            group="tipwaste", color="#d4d3cd")
        px0, py0, px1, py1 = base.PSTAT_BOX["rect"]
        add("pstat", box(px0, py0, 0, px1, py1, 40), group="pstat", color=C["pstat"], smooth_shading=False)
        add("pstat_face", box(px0 + 6, py0 - 0.3, 8, px0 + 30, py0, 32), group="pstat", color="#1b2b3e", smooth_shading=False)
        cable = pv.Spline(np.array([[80, 310, 20], [120, 300, 12], [150, 275, 8], [172, 258, 10]]), 40).tube(radius=2.0)
        add("cable", cable, group="cable", color="#262626")

    # ---- the head: tool plate, capper (STEP mount + magnet), P20, camera
    def build_head(self):
        add = self.add
        mount = step_mesh("PAW-V2-ElectromagnetMount", 2.0, 16)
        mount = mount.rotate_x(180, inplace=False)  # open end down, toward the cap
        axis = (63.17, -6.53)  # bore axis of the STEP, fitted; after the flip y -> -y
        mount = mount.translate((-axis[0], -axis[1], -mount.bounds[4] - MAGNET_HANG), inplace=False)
        parts = [
            ("toolplate", box(-55, 25, 28, 82, 29, 168), "#45484c", "toolplate"),
            ("zplate", box(-36, 29, 40, 36, GANTRY_DY - 24, 165), C["alu"], "toolplate"),
            ("mount", mount, C["mount"], "capper"),
            ("magnet", pv.Cylinder(center=(0, 0, -MAGNET_HANG + 10.5), direction=(0, 0, 1), radius=12.5, height=20, resolution=48), C["steel"], "capper"),
            ("cap_arm", box(-8, 10, 0, 8, 25, 26), C["mount"], "capper"),
            ("pip_shaft", pv.Cylinder(center=(PIP[0], PIP[1], 22), direction=(0, 0, 1), radius=4.0, height=44, resolution=32), C["pip_shaft"], "pipette"),
            ("pip_body", box(PIP[0] - 17, PIP[1] - 13, 44, PIP[0] + 17, PIP[1] + 13, 150), C["pip"], "pipette"),
            ("pip_top", box(PIP[0] - 17, PIP[1] - 13, 150, PIP[0] + 17, PIP[1] + 13, 162), C["pip_top"], "pipette"),
            ("camera", box(CAM_OFF[0] - 11, CAM_OFF[1] - 11, 8, CAM_OFF[0] + 11, CAM_OFF[1] + 11, 34), "#3a3a3a", "camera"),
            ("lens", pv.Cylinder(center=(CAM_OFF[0], CAM_OFF[1], 6.5), direction=(0, 0, 1), radius=5.0, height=3.0, resolution=24), "#111111", "camera"),
            ("cam_arm", box(CAM_OFF[0] - 5, CAM_OFF[1] + 11, 20, CAM_OFF[0] + 5, 25, 34), "#3a3a3a", "camera"),
            ("uno", box(-52, 21.5, 104, -14, 25, 158), "#1f6fae", "driver"),
            ("tmc", box(-46, 19.5, 112, -24, 21.5, 138), "#8b1d2c", "driver"),
            ("shield", box(-50, 20.0, 142, -18, 21.5, 156), "#2e7d4f", "driver"),
        ]
        self.head_keys = []
        for k, m, col, grp in parts:
            add(f"head:{k}", m, group=grp, color=col, smooth_shading=k in ("mount", "magnet", "pip_shaft", "lens"), specular=0.3)
            self.head_keys.append(f"head:{k}")
        # the tip on the pipette (moves with the head)
        add("head_tip", self.tip_mesh.translate((PIP[0], PIP[1], -TIP_LEN), inplace=False), color=C["tip"], specular=0.3)
        add("head_tipliq", pv.Cylinder(center=(PIP[0], PIP[1], -TIP_LEN + 3), direction=(0, 0, 1), radius=0.9, height=5, resolution=16), color=C["asw"])
        # the vial cap carried on the magnet (shown only while a stock is open)
        add("carried_vcap", self.vial_cap_mesh, color="#e3e1da")

    # ---- the electrode cap. Local origin (CAD frame C): centre of the skirt's underside, z up.
    def build_ecap(self):
        names = [("body", "electrode_cap", C["capbody"]), ("disc", "steel_disc", C["steel"]), ("carrier", "electrode_carrier", "#d9d6cf"),
                 ("ref", "ag_agcl_ref", C["agcl"]), ("coil", "pt_coil", C["pt"]), ("pogo", "cap_pogo_pins", C["brass"]),
                 ("holdsteel", "cap_hold_steel", C["steel"])]
        if self.cad_ok and cad_mesh("electrode_cap") is not None:
            for k, stem, col in names:
                for suffix, grp in (("", "ecap"), ("_section", "ecap_sec")):
                    m = cad_mesh(stem + suffix)
                    if m is not None:
                        self.add(f"{grp}:{k}", m, group=grp, color=col, specular=0.5 if k in ("disc", "coil", "pogo", "holdsteel") else 0.15)
            return
        cap_prof = [(1.0, 0.0), (11.5, 0.0), (11.5, -0.01), (13.0, -0.01), (13.0, 4.0), (9.0, 4.0), (9.0, 14.8), (1.0, 14.8)]
        parts = {
            "body": (revolve(cap_prof, CUT_SWEEP, CUT0), C["capbody"]),
            "disc": (revolve([(0.0, 14.8), (6.0, 14.8), (6.0, 16.0), (0.0, 16.0)], CUT_SWEEP, CUT0), C["steel"]),
            "capillary": (revolve([(0.0, -CAP_PROTRUDE), (1.0, -CAP_PROTRUDE), (1.0, 14.8), (0.0, 14.8)], CUT_SWEEP, CUT0), C["agcl"]),
        }
        for k, (m, col) in parts.items():
            self.add(f"ecap:{k}", m, group="ecap", color=col, specular=0.15)
        self.groups["ecap_sec"] = []

    # ---- the liquid in S1's well: O2 on one cut face, dissolved Cu on the other
    def load_field(self):
        f = HERE / "sim_well_hf_fields.npz"
        self.field_src = "sim_well_hf.py" if f.exists() else "sim_well.py"
        d = np.load(f if f.exists() else HERE / "sim_well_fields.npz")
        self.f_times = d["times"]
        self.f_o2 = d["o2"]  # (nt, nr, nz), NaN outside the liquid
        self.f_cu = d["cu"]  # uM
        r = d["r"] * 10.0  # mm
        z = d["z"] * 10.0
        hcell = r[1] - r[0]
        self.f_z = z
        self.trace_t, self.trace_I, self.trace_E = d["trace_t"], d["trace_I"], d["trace_E"]
        re = np.r_[0.0, r + hcell / 2]
        ze = np.r_[0.0, z + hcell / 2]
        self.planes = []
        for th in (math.radians(CUT0), math.radians(CUT0 + CUT_SWEEP)):
            R_, Z_ = np.meshgrid(re, ze, indexing="ij")
            X = (R_ * math.cos(th))[:, :, None] + S1[0]
            Y = (R_ * math.sin(th))[:, :, None] + S1[1]
            Zg = Z_[:, :, None] + FACE_Z
            g = pv.StructuredGrid(X, Y, Zg)
            g.cell_data["v"] = np.ones(len(r) * len(z))
            self.planes.append(g)
        from matplotlib.colors import LinearSegmentedColormap
        self.cmap_o2 = LinearSegmentedColormap.from_list("o2", ["#0d366b", "#256abf", "#6da7ec", "#cde2fb"])
        self.cmap_cu = LinearSegmentedColormap.from_list("cu", ["#fbeee4", "#f0b48a", "#d4733f", "#8a3b16"])
        cu_max = float(np.nanmax(self.f_cu))
        self.cu_clim = (0.0, float(10 ** math.ceil(math.log10(max(cu_max, 1.0)))) if cu_max > 0 else 1.0)
        self.cu_clim = (0.0, max(cu_max, 1.0))
        self.add("field0", self.planes[0], scalars="v", cmap=self.cmap_o2, clim=(0, 1), nan_opacity=0.0, show_scalar_bar=False,
                 smooth_shading=False, lighting=False)
        self.add("field1", self.planes[1], scalars="v", cmap=self.cmap_cu, clim=self.cu_clim, nan_opacity=0.0, show_scalar_bar=False,
                 smooth_shading=False, lighting=False)
        self.surface = revolve([(1.0, 0.0), (R_BORE, 0.0), (R_BORE, 0.05), (1.0, 0.05)], CUT_SWEEP, CUT0)
        self.add("surface", self.surface, color=C["asw"], opacity=0.45)
        self.liquid_mask = ~np.isnan(self.f_o2[0])
        coil = d["coil"]
        self.coil_src = np.where(coil)
        self.coil_dst = (np.minimum(self.coil_src[0] + 6, coil.shape[0] - 1), self.coil_src[1])
        self.liquid_mask[coil] = True

    def field_at(self, arr, sim_t, fill):
        ts = self.f_times
        if sim_t <= ts[0]:
            f = np.where(np.isnan(arr[0]), np.nan, fill) if sim_t <= 0 else arr[0] * (sim_t / ts[0]) + fill * (1 - sim_t / ts[0])
        elif sim_t >= ts[-1]:
            f = arr[-1]
        else:
            j = int(np.searchsorted(ts, sim_t)) - 1
            u = (sim_t - ts[j]) / (ts[j + 1] - ts[j])
            f = (1 - u) * arr[j] + u * arr[j + 1]
        f = np.array(f)
        f[self.coil_src] = f[self.coil_dst]
        return np.where(self.liquid_mask, np.nan_to_num(f, nan=fill), np.nan)

    def set_field(self, sim_t, level_mm):
        zz = self.f_z[None, :] + 0 * self.liquid_mask
        for g, arr, fill in ((self.planes[0], self.f_o2, 1.0), (self.planes[1], self.f_cu, 0.0)):
            f = self.field_at(arr, sim_t, fill)
            f = np.where(zz <= level_mm, f, np.nan)
            g.cell_data["v"][:] = f.ravel(order="F")
            g.Modified()

    def build_marker(self):
        ring = pv.Disc(center=(0, 0, 0), inner=0.82, outer=1.0, normal=(0, 0, 1), r_res=1, c_res=72)
        self.add("marker", ring, color=ORANGE_HEX, lighting=False, opacity=0.95)

    # ---- outline for the tool or module in focus
    def silhouette(self, key):
        if key in self.sil:
            return self.sil[key]
        import vtk
        mesh = self.meshes[key]
        if not isinstance(mesh, pv.PolyData):
            mesh = mesh.extract_surface()
        alg = vtk.vtkPolyDataSilhouette()
        clean = mesh.triangulate()
        clean = pv.PolyData(clean.points.copy(), clean.faces.copy())
        self.sil_src = getattr(self, "sil_src", [])
        self.sil_src.append(clean)
        alg.SetInputData(clean)
        alg.SetCamera(self.pl.renderer.GetActiveCamera())
        alg.SetProp3D(self.actors[key])
        alg.SetEnableFeatureAngle(True)
        alg.SetFeatureAngle(70)
        alg.BorderEdgesOn()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(alg.GetOutputPort())
        mapper.SetResolveCoincidentTopologyToPolygonOffset()
        mapper.SetRelativeCoincidentTopologyLineOffsetParameters(0, -66000)
        act = vtk.vtkActor()
        act.SetMapper(mapper)
        p = act.GetProperty()
        p.SetColor(*[c / 255 for c in ORANGE])
        p.SetLineWidth(3.5)
        p.LightingOff()
        self.pl.renderer.AddActor(act)
        self.sil[key] = act
        return act

    # ---- per-frame state
    def set_state(self, st):
        hx, hy, hz = st["head"]
        Mh = T(hx, hy, hz)
        for k in self.head_keys:
            self.actors[k].user_matrix = Mh
            self.actors[k].visibility = True
        close = bool(st.get("closeup"))
        for k in self.groups["ecap"]:
            self.actors[k].visibility = not close
        for k in self.groups.get("ecap_sec", []):
            self.actors[k].visibility = close
        for k in self.groups["gantry"]:
            self.actors[k].user_matrix = T(0, hy, 0)
        for k in self.groups["xcar"]:
            self.actors[k].user_matrix = T(hx, hy, 0)
        self.actors["head_tip"].user_matrix = Mh
        self.actors["head_tip"].visibility = st["tip_on"]
        self.actors["head_tipliq"].user_matrix = Mh
        self.actors["head_tipliq"].visibility = st["tip_on"] and st["tip_liq"]
        for j, a in enumerate(self.tip_actors):
            a.visibility = j not in st["tips_taken"]
        # electrode cap
        where = st["ecap"]
        Mc = T(hx, hy, hz - CAP_HANG + CAP_PROTRUDE) if where == "head" else T(*where)
        for k in self.groups["ecap"] + self.groups.get("ecap_sec", []):
            self.actors[k].user_matrix = Mc
        for name in self.vials:
            self.actors[f"vcap:{name}"].visibility = st["open_vial"] != name
        self.actors["carried_vcap"].visibility = bool(st["open_vial"])
        self.actors["carried_vcap"].user_matrix = T(hx, hy, hz - MAGNET_HANG - 0.5)
        # well liquid
        lvl = st["level"]
        self.set_field(st["sim_t"], lvl)
        self.actors["surface"].user_matrix = T(S1[0], S1[1], FACE_Z + lvl)
        self.actors["surface"].visibility = lvl > 0.05
        for k in ("field0", "field1"):
            self.actors[k].visibility = lvl > 0.05
        tx, ty = self.tubes[0]
        h = st["tube_ul"] / 20.0
        self.actors["tube1_liq"].user_matrix = T(tx, ty, 12.5) @ np.diag([1, 1, max(h, 1e-3), 1])
        self.actors["tube1_liq"].visibility = st["tube_ul"] > 1
        # placement: hidden groups, drop offsets
        hidden, drops = st.get("hidden", set()), st.get("drop", {})
        for grp, keys in self.groups.items():
            if grp in ("gantry", "xcar"):
                continue
            for k in keys:
                a = self.actors[k]
                moving = k in self.head_keys or grp in ("ecap", "ecap_sec")
                keep = k in self.head_keys or grp in ("ecap", "ecap_sec") or k.startswith(("tip0_", "vcap:"))
                vis = True
                for full, sec in self.sec_pairs:
                    if k == full:
                        vis = not close
                    elif k == sec:
                        vis = close
                a.visibility = (a.visibility if keep else vis) and grp not in hidden and (grp != "ecap_sec" or "ecap" not in hidden)
                dz = drops.get(grp, 0.0)
                a.user_matrix = T(0, 0, dz) @ (np.array(a.user_matrix) if moving else np.eye(4))
        if "tubes" in hidden:
            self.actors["tube1_liq"].visibility = False
        # highlight
        lit = set(st.get("lit", ()))
        for grp, keys in self.groups.items():
            for k in keys:
                on = grp in lit and self.actors[k].visibility and not k.startswith(NO_OUTLINE) and not st.get("closeup")
                if on or k in self.sil:
                    s = self.silhouette(k)
                    s.SetVisibility(on)
                    s.SetUserMatrix(self.actors[k].GetUserMatrix())
                col = self.colors.get(k)
                if col is not None and isinstance(col, str) and grp in ("capper", "pipette", "camera", "pstat", "cable", "ecap"):
                    rgb = hex_rgb(col)
                    if on:
                        rgb = tuple(0.55 * c + 0.45 * o / 255 for c, o in zip(rgb, ORANGE))
                    self.actors[k].prop.color = rgb
        # target ring
        tgt = st.get("target")
        m = self.actors["marker"]
        if tgt is None:
            m.visibility = False
        else:
            x, y, z, r = tgt
            pulse = 1.0 + 0.12 * math.sin(st.get("t", 0.0) * 2 * math.pi * 1.4)
            m.visibility = True
            m.user_matrix = T(x, y, z + 0.4) @ np.diag([r * pulse, r * pulse, 1, 1])

    def set_camera(self, cam):
        pos, foc, up, angle = cam
        c = self.pl.camera
        c.position, c.focal_point, c.up = pos, foc, up
        c.view_angle = angle
        self.pl.renderer.ResetCameraClippingRange()

    def project(self, xyz):
        import vtk
        co = vtk.vtkCoordinate()
        co.SetCoordinateSystemToWorld()
        co.SetValue(*xyz)
        x, y = co.GetComputedDoubleDisplayValue(self.pl.renderer)
        return x, H - y

    def frame(self):
        self.pl.render()
        return self.pl.screenshot(return_img=True)


# ------------------------------------------------------------------ the run: one spot
def well_level(v_ul, capped):
    a2 = math.pi * A_SPOT ** 2
    throat = a2 * Z_STEP
    lvl = v_ul / a2 if v_ul <= throat else Z_STEP + (v_ul - throat) / (math.pi * R_BORE ** 2)
    if capped and lvl > REF_TIP:  # the capillary displaces liquid above its tip
        lvl = REF_TIP + (lvl - REF_TIP) * R_BORE ** 2 / (R_BORE ** 2 - 1.0)
    return lvl


TOOLS = {"capper": "Capper", "pipette": "P20 pipette", "camera": "Head camera", "pstat": "Potentiostat"}


class Story:
    """Keyframes for the head and the deck state; captions; camera; which tool works."""

    def __init__(self, t0=0.0, head=(PARK[0], PARK[1], TRAVEL)):
        self.t = t0
        self.head = head
        self.keys = [(t0, head)]
        self.events = []  # (t, dict of state changes)
        self.captions = []  # (t0, t1, text)
        self.cams = []  # (t, cam)
        self.travel_dur = 0.9

    def move(self, dur, x=None, y=None, z=None):
        hx, hy, hz = self.head
        self.head = (hx if x is None else x, hy if y is None else y, hz if z is None else z)
        self.t += dur
        self.keys.append((self.t, self.head))

    def travel(self, x, y, dur=None):
        dur = self.travel_dur if dur is None else dur
        if self.head[2] < TRAVEL - 1e-6:
            self.move(0.35, z=TRAVEL)
        self.move(dur, x=x, y=y)

    def wait(self, dur):
        self.move(dur)

    def ev(self, **kw):
        self.events.append((self.t, kw))

    def act(self, tool, target=None, what=""):
        """From now on, `tool` is the one working; target = (x, y, z, ring radius) on the deck."""
        self.ev(active=(tool, target, what))

    def caption(self, text, dur=None, t0=None):
        t0 = self.t if t0 is None else t0
        self.captions.append([t0, t0 + (dur or 0), text])

    def cam(self, t, pos, foc, up=(0, 0, 1), angle=30.0):
        self.cams.append((t, (np.array(pos, float), np.array(foc, float), np.array(up, float), angle)))

    def pip_to(self, x, y, z_end, tip=True, dur=None):
        self.travel(x - PIP[0], y - PIP[1], dur)
        self.move(0.45, z=z_end + (TIP_LEN if tip else 0.0))

    def capper_to(self, x, y, z_face, dur=None):
        self.travel(x, y, dur)
        self.move(0.45, z=z_face + MAGNET_HANG)

    def camera_to(self, x, y, dur=None):
        self.travel(x - CAM_OFF[0], y - CAM_OFF[1], dur)


OVERVIEW = ((990, -870, 810), (195, 145, 20))
RUN_WIDE = ((700, -520, 540), (225, 150, 30))
FRONT = ((182, -1400, 330), (182, 170, 60))
PLACE_HEAD = (361.0, 278.0, TRAVEL)


def build_story(t0):
    s = Story(t0, head=PLACE_HEAD)
    rack = list(base.rack_tips(base.TIP_RACK_1))
    asw, s10 = deck_cu.STOCKS["ASW (D1141, no heavy metals)"], deck_cu.STOCKS["ASW + 10 mg/L S"]
    acid = deck_cu.STOCKS["1 M HNO3, trace metal"]
    park, rinse1, rinse2 = deck_cu.CUPS["park cup"], deck_cu.CUPS["rinse 1 (DI)"], deck_cu.CUPS["rinse 2 (ASW)"]
    tube1 = (base.TUBE_X[0], base.TUBE_Y[0])
    tw = deck_cu.TIP_WASTE["c"]
    s.ev(tip_on=False, tip_liq=False, tips_taken=set(), ecap=(park[0], park[1], 45.0), open_vial=None,
         well_ul=0.0, sim_t=0.0, tube_ul=0.0, capped=False, active=None)
    wide = RUN_WIDE
    s.cam(s.t, *OVERVIEW, angle=30)
    s.cam(s.t + 1.2, *wide, angle=30)

    s.caption("1  Pick up a 20 µL tip from Ben's tip rack (unmoved)")
    s.act("pipette", (rack[0][0], rack[0][1], 66.0, 6.0), "picks up a tip")
    s.pip_to(rack[0][0], rack[0][1], 59.0, tip=False)
    s.ev(tip_on=True, tips_taken={0})
    s.wait(0.25)
    s.move(0.4, z=TRAVEL)

    s.caption("2  The capper lifts the seawater cap; the P20 builds the well from 135 µL of ASTM D1141 seawater (7 transfers)")
    s.act("capper", (asw[0], asw[1], VIAL_CAP_TOP, 17.0), "lifts the seawater (ASW) cap")
    s.capper_to(asw[0], asw[1], VIAL_CAP_TOP)
    s.ev(open_vial="ASW (D1141, no heavy metals)")
    s.wait(0.25)
    s.move(0.4, z=TRAVEL)
    s.act("pipette", (asw[0], asw[1], VIAL_RIM, 15.0), "aspirates 20 µL of ASW")
    s.pip_to(asw[0], asw[1], 35.0)
    s.ev(tip_liq=True)
    s.wait(0.3)
    s.cam(s.t + 0.8, (560, -330, 420), (240, 175, 35), angle=30)
    s.act("pipette", (S1[0], S1[1], LID_TOP, 6.0), "dispenses into well S1, above the meniscus")
    s.pip_to(S1[0], S1[1], FACE_Z + 2.0)
    t_fill = s.t
    s.fill_still = t_fill + 0.9
    s.wait(1.3)
    s.events.append((t_fill, {"well_ramp": (t_fill, s.t, 0.0, 135.0)}))
    s.ev(tip_liq=False)
    s.move(0.4, z=TRAVEL)
    s.act("capper", (asw[0], asw[1], VIAL_CAP_TOP, 17.0), "puts the ASW cap back")
    s.capper_to(asw[0], asw[1], VIAL_CAP_TOP)
    s.ev(open_vial=None)
    s.wait(0.25)
    s.move(0.35, z=TRAVEL)

    s.caption("3  Sulfide last: 15 µL of the 10 mg/L stock, made in the same seawater, gives 1 mg/L S")
    s.act("capper", (s10[0], s10[1], VIAL_CAP_TOP, 17.0), "lifts the sulfide-stock cap")
    s.capper_to(s10[0], s10[1], VIAL_CAP_TOP)
    s.ev(open_vial="ASW + 10 mg/L S")
    s.wait(0.25)
    s.move(0.35, z=TRAVEL)
    s.act("pipette", (s10[0], s10[1], VIAL_RIM, 15.0), "aspirates 15 µL of sulfide stock")
    s.pip_to(s10[0], s10[1], 35.0)
    s.ev(tip_liq=True)
    s.wait(0.25)
    s.act("pipette", (S1[0], S1[1], LID_TOP, 6.0), "adds it to S1")
    s.pip_to(S1[0], S1[1], FACE_Z + 4.0)
    t_s = s.t
    s.wait(0.7)
    s.events.append((t_s, {"well_ramp": (t_s, s.t, 135.0, 150.0)}))
    s.ev(tip_liq=False)
    s.move(0.35, z=TRAVEL)
    s.act("capper", (s10[0], s10[1], VIAL_CAP_TOP, 17.0), "recaps the sulfide stock")
    s.capper_to(s10[0], s10[1], VIAL_CAP_TOP)
    s.ev(open_vial=None)
    s.wait(0.25)
    s.move(0.35, z=TRAVEL)

    s.caption("4  Drop the tip, then the head camera checks for liquid outside the O-ring (2 min)")
    s.cam(s.t + 0.6, *wide, angle=30)
    s.act("pipette", (tw[0], tw[1], deck_cu.TIP_WASTE["top"], 15.0), "drops the tip")
    s.pip_to(tw[0], tw[1], 60.0)
    s.ev(tip_on=False)
    s.wait(0.3)
    s.move(0.35, z=TRAVEL)
    s.act("camera", (S1[0], S1[1], LID_TOP, 9.0), "leak check at S1")
    s.camera_to(S1[0], S1[1])
    s.wait(1.6)

    s.caption("5  The capper carries the electrode cap (leak-free Ag/AgCl, Pt coil) from its park cup and sets it over S1's boss: 0.12 mm clearance, no O-ring, two small lid magnets hold it")
    s.cam(s.t + 0.8, (430, -330, 400), (165, 215, 35), angle=30)
    s.act("capper", (park[0], park[1], 45.0, 9.0), "picks up the electrode cap")
    s.capper_to(park[0], park[1], 45.0 + 16.0)
    s.ev(ecap="head")
    s.wait(0.25)
    s.move(0.4, z=TRAVEL)
    s.act("capper", (S1[0], S1[1], LID_TOP, 9.0), "sets the cap over S1's boss")
    s.capper_to(S1[0], S1[1], LID_TOP + 16.0)
    s.ev(ecap=(S1[0], S1[1], LID_TOP), capped=True)
    s.wait(0.25)
    s.move(0.4, z=TRAVEL)

    t_meas0 = s.t + 1.6
    close_cam = ((S1[0] + 2.2, S1[1] - 20, FACE_Z + 7.5), (S1[0], S1[1], FACE_Z + 2.6))
    s.act("pstat", None, "OCP, LPR, hold: the head is free")
    s.cam(s.t + 1.6, *close_cam, angle=30)
    s.travel(PARK[0], PARK[1], 1.2)
    meas = 10.0
    s.caption("6  Measured with the cap on: OCP 30 min, LPR ±10 mV, rest 5 min, +50 mV hold 10 min, OCP 5 min. The head is free meanwhile", meas + 1.6)
    s.wait(t_meas0 + meas - s.t)
    fields = HERE / "sim_well_hf_fields.npz"
    t_last = float(np.load(fields if fields.exists() else HERE / "sim_well_fields.npz")["trace_t"][-1])
    s.events.append((t_meas0, {"sim_ramp": (t_meas0 + 0.6, t_meas0 + meas - 0.4, 0.0, t_last)}))
    s.cam(s.t + 0.2, *close_cam, angle=30)
    s.cam(s.t + 1.6, (480, -380, 430), (165, 160, 35), angle=30)
    s.measure = (t_meas0, t_meas0 + meas)

    s.travel_dur = 0.6
    s.caption("7  The magnet lifts the cap off S1 (about 2.4 N against the lid magnets); it is dipped in DI water, then seawater, and parked")
    s.act("capper", (S1[0], S1[1], LID_TOP, 9.0), "lifts the cap off S1")
    s.capper_to(S1[0], S1[1], LID_TOP + 16.0)
    s.ev(ecap="head", capped=False)
    s.wait(0.2)
    s.move(0.35, z=TRAVEL)
    for cup, what in ((rinse1, "dips the cap in DI water"), (rinse2, "dips the cap in seawater")):
        s.act("capper", (cup[0], cup[1], 45.0, 9.0), what)
        s.capper_to(cup[0], cup[1], 45.0 + 16.0)
        s.wait(0.3)
        s.move(0.35, z=TRAVEL)
    s.act("capper", (park[0], park[1], 45.0, 9.0), "parks the cap")
    s.capper_to(park[0], park[1], 45.0 + 16.0)
    s.ev(ecap=(park[0], park[1], 45.0))
    s.wait(0.2)
    s.move(0.35, z=TRAVEL)

    s.caption("8  A new tip moves the 150 µL, then a 150 µL DI rinse, into tube 1 for ICP-MS")
    s.act("pipette", (rack[1][0], rack[1][1], 66.0, 6.0), "picks up a new tip")
    s.pip_to(rack[1][0], rack[1][1], 59.0, tip=False)
    s.ev(tip_on=True, tips_taken={0, 1})
    s.move(0.35, z=TRAVEL)
    s.act("pipette", (S1[0], S1[1], LID_TOP, 6.0), "collects the well's liquid")
    s.pip_to(S1[0], S1[1], FACE_Z + 0.5)
    t_c = s.t
    s.ev(tip_liq=True)
    s.wait(0.6)
    s.events.append((t_c, {"well_ramp": (t_c, s.t, 150.0, 0.0)}))
    s.act("pipette", (tube1[0], tube1[1], 32.0, 6.0), "dispenses into tube 1")
    s.pip_to(tube1[0], tube1[1], 40.0)
    t_d = s.t
    s.ev(tip_liq=False)
    s.wait(0.45)
    s.events.append((t_d, {"tube_ramp": (t_d, s.t, 0.0, 300.0)}))
    s.move(0.3, z=TRAVEL)
    s.act("pipette", (tw[0], tw[1], deck_cu.TIP_WASTE["top"], 15.0), "drops the tip")
    s.pip_to(tw[0], tw[1], 60.0)
    s.ev(tip_on=False)
    s.move(0.3, z=TRAVEL)

    s.caption("9  Acidify at once: the capper opens the acid vial; the night's one acid tip adds 20 µL of 1 M HNO3 from above the tube rim")
    s.act("capper", (acid[0], acid[1], VIAL_CAP_TOP, 17.0), "lifts the acid-vial cap")
    s.capper_to(acid[0], acid[1], VIAL_CAP_TOP)
    s.ev(open_vial="1 M HNO3, trace metal")
    s.wait(0.2)
    s.move(0.3, z=TRAVEL)
    acid_tip = list(base.rack_tips(base.TIP_RACK_2))[0]
    s.act("pipette", (acid_tip[0], acid_tip[1], 66.0, 6.0), "takes the night's acid tip from rack 2")
    s.pip_to(acid_tip[0], acid_tip[1], 59.0, tip=False)
    s.ev(tip_on=True)
    s.move(0.3, z=TRAVEL)
    s.act("pipette", (acid[0], acid[1], VIAL_RIM, 15.0), "aspirates 20 µL of 1 M HNO3")
    s.pip_to(acid[0], acid[1], 35.0)
    s.ev(tip_liq=True)
    s.move(0.3, z=TRAVEL)
    s.act("pipette", (tube1[0], tube1[1], 32.0, 6.0), "adds the acid from above the rim")
    s.pip_to(tube1[0], tube1[1], 37.0)
    t_a = s.t
    s.wait(0.4)
    s.ev(tip_liq=False)
    s.events.append((t_a, {"tube_ramp": (t_a, s.t, 300.0, 320.0)}))
    s.move(0.3, z=TRAVEL)
    s.act("pipette", (acid_tip[0], acid_tip[1], 66.0, 6.0), "puts the acid tip back")
    s.pip_to(acid_tip[0], acid_tip[1], 62.0, tip=False)
    s.ev(tip_on=False)
    s.move(0.3, z=TRAVEL)
    s.act("capper", (acid[0], acid[1], VIAL_CAP_TOP, 17.0), "recaps the acid")
    s.capper_to(acid[0], acid[1], VIAL_CAP_TOP)
    s.ev(open_vial=None)
    s.wait(0.2)
    s.move(0.3, z=TRAVEL)

    s.caption("10  The head camera images the spot. Next spot: S2")
    s.act("camera", (S1[0], S1[1], LID_TOP, 9.0), "images the spot")
    s.camera_to(S1[0], S1[1])
    s.wait(1.2)
    s.act(None)
    s.travel(PARK[0], PARK[1], 0.9)
    s.cam(s.t, (480, -380, 430), (165, 160, 35), angle=30)
    s.cam(s.t + 1.5, *OVERVIEW, angle=30)
    s.wait(1.5)
    s.total = s.t
    return s


def run_state(s, t):
    st = {"t": t, "tip_on": False, "tip_liq": False, "tips_taken": set(), "open_vial": None, "capped": False,
          "ecap": (deck_cu.CUPS["park cup"][0], deck_cu.CUPS["park cup"][1], 45.0)}
    for te, kw in s.events:
        if te <= t + 1e-9:
            for k, v in kw.items():
                if not k.endswith("_ramp"):
                    st[k] = v
    st["well_ul"] = st["tube_ul"] = st["sim_t"] = 0.0
    for te, kw in s.events:
        for k, v in kw.items():
            if not k.endswith("_ramp") or te > t + 1e-9:
                continue
            a, b, v0, v1 = v
            st[{"well_ramp": "well_ul", "tube_ramp": "tube_ul", "sim_ramp": "sim_t"}[k]] = v0 + (v1 - v0) * min(max((t - a) / (b - a), 0.0), 1.0)
    if t > s.measure[1]:
        st["sim_t"] = 1e9
    keys = s.keys
    if t >= keys[-1][0]:
        st["head"] = keys[-1][1]
    elif t <= keys[0][0]:
        st["head"] = keys[0][1]
    else:
        j = max(i for i, (tk, _) in enumerate(keys) if tk <= t)
        (t0, p0), (t1, p1) = keys[j], keys[j + 1]
        u = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
        st["head"] = tuple(a + (b - a) * u for a, b in zip(p0, p1))
    st["level"] = well_level(st["well_ul"], st.get("capped", False))
    st.setdefault("tip_liq", False)
    act = st.get("active")
    if act and act[0]:
        tool, target, what = act
        st["lit"] = {"pstat": ("pstat", "cable", "ecap")}.get(tool, (tool,))
        st["target"] = target
        st["tool"], st["what"] = tool, what
    return st


def interp_cam(cams, t):
    if t <= cams[0][0]:
        return cams[0][1]
    if t >= cams[-1][0]:
        return cams[-1][1]
    j = max(i for i, (tk, _) in enumerate(cams) if tk <= t)
    (t0, c0), (t1, c1) = cams[j], cams[j + 1]
    u = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
    return tuple(c0[i] + (c1[i] - c0[i]) * u for i in range(4))


# ------------------------------------------------------------------ the placement chapter
DECK_MODULES = [  # group, label (1-5 words), anchor (deck xyz)
    ("tray", "Coupon tray, four stations", (222, 262, 24)),
    ("coupons", "Specimens: Cu–Ni, NAB, DED", (205, 228, 24)),
    ("blank", "PTFE blank on S4", (262, 228, 24)),
    ("lids", "Well lids, FKM O-rings", (222, 250, 30)),
    ("holder", "Stock vial holder", (318, 322, 40)),
    ("vials", "Stocks: seawater, sulfide, acid", (318, 215, 78)),
    ("rack1", "Tip rack 1 (Ben's)", (287, 80, 70)),
    ("rack2", "Tip rack 2", (104, 80, 70)),
    ("tubes", "ICP-MS sample tubes", (218, 18, 36)),
    ("cups", "Rinse and park cups", (55, 260, 50)),
    ("ecap", "Electrode cap, parked", (92, 240, 66)),
    ("tipwaste", "Tip waste", (385, 150, 54)),
    ("pstat", "Potentiostat, off the deck", (40, 335, 46)),
    ("cable", "Three-wire electrode bus", (128, 295, 16)),
]
HEAD_TOOLS = [  # group, label, anchor relative to the head origin
    ("capper", "Electromagnetic capper", (0, -16, -16)),
    ("pipette", "P20 pipette", (PIP[0] + 17, PIP[1] - 13, 100)),
    ("camera", "Head camera", (CAM_OFF[0] - 11, CAM_OFF[1] - 11, 20)),
    ("driver", "Arduino + TMC2209 driver", (-33, 19.5, 130)),
]
DROP, HOLD = 0.55, 1.15


class Placement:
    def __init__(self, t0):
        self.t0 = t0
        self.items = []
        t = t0 + 0.4
        for grp, lab, anc in DECK_MODULES:
            self.items.append((t, grp, lab, anc, False))
            t += DROP + HOLD
        t += 0.5
        self.t_tools = t
        for grp, lab, anc in HEAD_TOOLS:
            self.items.append((t, grp, lab, anc, True))
            t += DROP + HOLD
        self.t1 = t + 0.4
        self.head = PLACE_HEAD

    def state(self, t):
        st = {"t": t, "head": self.head, "tip_on": False, "tip_liq": False, "tips_taken": set(),
              "ecap": (deck_cu.CUPS["park cup"][0], deck_cu.CUPS["park cup"][1], 45.0), "open_vial": None,
              "sim_t": 0.0, "tube_ul": 0.0, "level": 0.0, "hidden": set(), "drop": {}, "lit": ()}
        for ts, grp, lab, anc, tool in self.items:
            if t < ts:
                st["hidden"].add(grp)
            elif t < ts + DROP:
                u = (t - ts) / DROP
                st["drop"][grp] = 140.0 * (1 - u) ** 2 if not tool else 60.0 * (1 - u) ** 2
                st["lit"] = (grp,)
                st["label"] = (lab, anc, tool, u)
            elif t < ts + DROP + HOLD:
                st["lit"] = (grp,)
                st["label"] = (lab, anc, tool, 1.0)
        return st

    def cams(self):
        hx, hy, hz = self.head
        up = np.array((0, 0, 1.0))
        P0, F0 = np.array(OVERVIEW[0], float), np.array(OVERVIEW[1], float)
        c = [(self.t0, (P0, F0, up, 30.0))]
        for ts, grp, lab, anc, tool in self.items:
            if tool:
                continue
            f = F0 + 0.4 * (np.array(anc, float) - F0)
            c.append((ts + 0.25, (f + 0.8 * (P0 - F0), f, up, 30.0)))
        tool_cam = ((hx - 270, hy - 560, 370), (hx + 10, hy, 135))
        c.append((self.t_tools - 0.2, (np.array(tool_cam[0], float), np.array(tool_cam[1], float), up, 30.0)))
        c.append((self.t1 - 0.3, (np.array(tool_cam[0], float) + (25, 0, 0), np.array(tool_cam[1], float), up, 30.0)))
        c.append((self.t1 + 0.9, (np.array(RUN_WIDE[0], float), np.array(RUN_WIDE[1], float), up, 30.0)))
        return c


# ------------------------------------------------------------------ 2D: fonts, cards, overlays
def font(size, bold=False):
    from matplotlib import font_manager
    path = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold" if bold else "normal"))
    return ImageFont.truetype(path, size)


INK, INK2, MUTED, RULE, PAPER = (11, 11, 11), (82, 81, 78), (137, 135, 129), (225, 224, 217), (246, 245, 241)


def wrap(d, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    return lines


def topbar(d, chapter):
    d.rectangle([0, 0, W, 36], fill=(252, 252, 251, 230))
    ft = font(19, True)
    title = "Copper corrosion on the CubXL"
    d.text((16, 8), title, font=ft, fill=INK)
    d.text((16 + d.textlength(title, font=ft) + 14, 11), "·  " + chapter, font=font(15), fill=INK2)
    d.text((W - 16, 11), "PR #278 · proposal, not built", font=font(13), fill=INK2, anchor="ra")


def caption_bar(d, text, size=17):
    f = font(size)
    lines = wrap(d, text, f, W - 40)
    hb = 14 + (size + 7) * len(lines)
    d.rectangle([0, H - hb, W, H], fill=(252, 252, 251, 232))
    for i, line in enumerate(lines):
        d.text((18, H - hb + 7 + (size + 7) * i), line, font=f, fill=INK)
    return hb


def label_at(d, xy, text, anchor_xy=None, size=16, color=INK, box=True):
    f = font(size, True)
    x, y = xy
    tw = d.textlength(text, font=f)
    if anchor_xy is not None:
        d.line([anchor_xy, (x, y)], fill=ORANGE + (255,), width=2)
        d.ellipse([anchor_xy[0] - 4, anchor_xy[1] - 4, anchor_xy[0] + 4, anchor_xy[1] + 4], fill=ORANGE + (255,))
    if box:
        d.rounded_rectangle([x - 8, y - size - 6, x + tw + 8, y + 6], radius=6, fill=(252, 252, 251, 235), outline=ORANGE + (255,), width=2)
    d.text((x, y - size - 1), text, font=f, fill=color)


def tool_panel(d, active):
    y = 46
    f = font(14, True)
    d.text((16, y + 5), "working now:", font=font(13), fill=INK2)
    y += 0
    for key in ("pstat", "camera", "pipette", "capper")[::-1]:
        pass
    widths = {k: d.textlength(v, font=f) + 26 for k, v in TOOLS.items()}
    xr = W - 16
    for key in ("capper", "pipette", "camera", "pstat"):
        pass
    order = ["capper", "pipette", "camera", "pstat"]
    xx = 16 + d.textlength("working now:", font=font(13)) + 10
    for k in order:
        on = k == active
        wpill = widths[k]
        d.rounded_rectangle([xx, y, xx + wpill, y + 26], radius=13, fill=ORANGE + (255,) if on else (252, 252, 251, 220),
                            outline=ORANGE + (255,) if on else (190, 188, 182, 255), width=2)
        d.text((xx + wpill / 2, y + 13), TOOLS[k], font=f, fill=(255, 255, 255) if on else MUTED, anchor="mm")
        xx += wpill + 8


PREP_CARDS = [
    ("1  Stock material", "the alloys",
     ["Wrought C71500 (70/30 Cu–Ni) and C70600 (90/10) bar, and cast C95800 NAB: the references the well is calibrated on",
      "DED pads and repairs from one pre-alloyed powder feed, by blown-powder laser DED",
      "Build wide pads: a well that sits in one zone needs at least 5 mm of sound deposit",
      "Log each piece: build plane (XY or XZ), build height, track centre or overlap",
      "Keep a sample of each powder lot for oxygen by inert-gas fusion"],
     "protocol.md §1, §7; c1-04, c1-05, c1-10", "ded"),
    ("2  Specimens", "cut, polish, clean, check",
     ["Cut 20 × 20 mm pieces, up to 6 mm thick, to fit the tray pocket (1 and 3 mm shims for thinner ones)",
      "Mount, grind and polish (SOP #258): SiC to P2400, 1 µm diamond, 0.04 µm colloidal silica; leave a bare metal back",
      "Clean: ethanol ultrasonic bath, ultrapure-water rinse, dry nitrogen",
      "EDS or XRF away from the wells; photograph each footprint, and a pore sends it to a separate set",
      "Into the tray 1 h ± 10 min after drying, kept in a desiccator"],
     "protocol.md §1; SOP PR #258; c1-05", "polish"),
    ("3  Solutions", "seawater, sulfide, acid",
     ["Seawater: ASTM D1141 salts without stock No. 3 (its heavy metals include copper), pH 8.2, filtered; an ICP-MS blank of every batch",
      "Sulfide master from Na₂S·9H₂O in deaerated water, in the fume hood",
      "10 and 0.1 mg/L S stocks in deaerated seawater, fresh each night, checked by methylene blue at the start and end",
      "1 M trace-metal HNO₃, diluted from the concentrated acid in the fume hood"],
     "protocol.md §3, §9; c1-06", "solutions"),
    ("4  Consumables and checks", "the evening before",
     ["Acid-leach the 0.5 mL PP tubes (2 % HNO₃ overnight), rinse, weigh empty on a 0.1 mg balance, label",
      "Check the working Ag/AgCl against the master reference in seawater and log the offset (e.g. ±5 mV)",
      "Fill the 20 mL stock vials, the DI and seawater rinse cups, and the park cup's storage solution",
      "Tips in both racks, tip waste empty; pieces in the tray, lids screwed down on the O-rings"],
     "protocol.md §3, §6; cubxl-setup.md §5", "tubes"),
]
AFTER_CARD = ("After the night", "the liquid and the spot",
              ["Cap the acidified tubes and weigh them: the recovered volume and the dilution",
               "Dilute 10× and run ICP-MS with a collision cell (read ⁶⁵Cu): Cu, Ni, Fe and Mn on every tube, Al on NAB",
               "Compare dissolved metal with the charge passed; the gap stayed in the film or replated",
               "Photograph each spot and take it to SEM/EDS. A ring of attack just inside the O-ring is reverse crevice attack, not pitting"],
              "protocol.md §4, §6", "icp")
CARD_DUR = 6.0


def icon(d, kind, x0, y0, s=1.0):
    """Small pictograms for the cards, drawn in the house palette."""
    def R(a, b, c, e, **kw):
        d.rectangle([x0 + a * s, y0 + b * s, x0 + c * s, y0 + e * s], **kw)

    def E(a, b, c, e, **kw):
        d.ellipse([x0 + a * s, y0 + b * s, x0 + c * s, y0 + e * s], **kw)

    def P(pts, **kw):
        d.polygon([(x0 + a * s, y0 + b * s) for a, b in pts], **kw)

    def L(pts, **kw):
        d.line([(x0 + a * s, y0 + b * s) for a, b in pts], **kw)
    if kind == "ded":
        P([(70, 0), (130, 0), (115, 70), (85, 70)], fill=(120, 120, 118), outline=INK2)
        rng = np.random.default_rng(3)
        for _ in range(70):
            u, v = rng.uniform(-1, 1), rng.uniform(0, 1)
            E(100 + u * 26 * (1 - v) - 2, 72 + v * 75 - 2, 100 + u * 26 * (1 - v) + 2, 72 + v * 75 + 2, fill=(184, 115, 51))
        R(10, 175, 230, 205, fill=(150, 150, 146))
        for k in range(4):
            E(30 + 40 * k, 150, 80 + 40 * k, 185, fill=(192, 138, 98), outline=(140, 90, 60))
        E(85, 140, 120, 165, fill=(255, 190, 90))
        for k, col in enumerate(((184, 154, 138), (190, 165, 150), (195, 155, 85))):
            R(20 + 72 * k, 225, 80 + 72 * k, 245, fill=col, outline=INK2)
        d.text((x0 + 10 * s, y0 + 252 * s), "C71500   C70600   C95800", font=font(int(13 * s)), fill=INK2)
    elif kind == "polish":
        E(10, 60, 230, 140, fill=(200, 205, 210), outline=INK2, width=2)
        E(40, 72, 200, 128, fill=(225, 228, 232), outline=MUTED)
        E(95, 50, 145, 90, fill=(184, 154, 138), outline=INK2, width=2)
        R(105, 0, 135, 55, fill=(90, 90, 90))
        for k in range(3):
            L([(170 + 18 * k, 175), (160 + 18 * k, 200), (178 + 18 * k, 225)], fill=(42, 120, 214), width=3)
        R(20, 175, 140, 250, outline=INK2, width=2)
        R(24, 200, 136, 246, fill=(205, 228, 245))
        d.text((x0 + 22 * s, y0 + 255 * s), "polish        ultrasonic clean", font=font(int(13 * s)), fill=INK2)
    elif kind == "solutions":
        for k, (col, lab) in enumerate((((156, 199, 232), "ASW"), ((230, 213, 138), "S²⁻"), ((243, 240, 230), "HNO₃"))):
            xx = 10 + 78 * k
            P([(xx + 10, 40), (xx + 55, 40), (xx + 65, 200), (xx, 200)], fill=(240, 244, 246), outline=INK2)
            P([(xx + 6, 110), (xx + 59, 110), (xx + 64, 196), (xx + 2, 196)], fill=col)
            d.text((x0 + (xx + 32) * s, y0 + 215 * s), lab, font=font(int(15 * s), True), fill=INK2, anchor="ma")
        for k in range(6):
            E(118 + 5 * (k % 2), 180 - 22 * k, 126 + 5 * (k % 2), 188 - 22 * k, outline=(42, 120, 214), width=2)
        d.text((x0 + 10 * s, y0 + 252 * s), "N₂ sparge, fume hood", font=font(int(13 * s)), fill=INK2)
    elif kind == "tubes":
        for k in range(6):
            xx = 20 + 34 * k
            P([(xx, 40), (xx + 22, 40), (xx + 18, 150), (xx + 11, 175), (xx + 4, 150)], fill=(244, 244, 240), outline=INK2)
        R(5, 120, 225, 135, fill=(200, 195, 181))
        R(40, 200, 200, 250, fill=(60, 60, 60))
        R(55, 190, 185, 200, fill=(140, 140, 140))
        d.text((x0 + 120 * s, y0 + 228 * s), "0.0000 g", font=font(int(16 * s), True), fill=(140, 230, 160), anchor="mm")
    elif kind == "icp":
        R(20, 40, 210, 200, fill=(90, 100, 110), outline=INK2, width=2)
        R(40, 60, 120, 110, fill=(30, 40, 50))
        L([(45, 100), (60, 90), (75, 95), (90, 70), (100, 85), (115, 75)], fill=(120, 220, 140), width=2)
        for k in range(5):
            E(135 + 14 * (k % 3), 70 + 30 * (k // 3), 147 + 14 * (k % 3), 82 + 30 * (k // 3), fill=(200, 200, 200))
        d.text((x0 + 115 * s, y0 + 215 * s), "ICP-MS   ·   SEM/EDS", font=font(int(14 * s), True), fill=INK2, anchor="ma")


def card_image(card, t_local, total=CARD_DUR, chapter="Before the night, off the deck"):
    title, sub, bullets, src, kind = card
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im, "RGBA")
    topbar(d, chapter)
    d.text((70, 78), title, font=font(34, True), fill=INK)
    d.text((72, 124), sub, font=font(18), fill=INK2)
    d.line([(70, 158), (W - 70, 158)], fill=RULE, width=2)
    icon(d, kind, 80, 200, 1.35)
    f = font(19)
    y = 190
    n = len(bullets)
    for i, b in enumerate(bullets):
        t_on = 0.5 + i * min(0.9, (total - 2.0) / max(n, 1))
        a = ease((t_local - t_on) / 0.35)
        if a <= 0:
            continue
        col = tuple(int(PAPER[j] + (INK[j] - PAPER[j]) * a) for j in range(3))
        lines = wrap(d, b, f, W - 470 - 70)
        d.ellipse([452, y + 9, 461, y + 18], fill=ORANGE + (int(255 * a),))
        for k, line in enumerate(lines):
            d.text((475, y + 27 * k), line, font=f, fill=col)
        y += 27 * len(lines) + 18
    d.text((70, H - 40), "Sources: " + src, font=font(13), fill=MUTED)
    return np.asarray(im)


def photo_card(t_local):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im, "RGBA")
    topbar(d, "the real machine")
    if PHOTO.exists():
        ph = Image.open(PHOTO).convert("RGB")
        z = 1.0 + 0.04 * min(t_local / 4.5, 1.0)  # slow push-in
        ph_h = int(600 * z)
        ph_w = int(ph.size[0] * ph_h / ph.size[1])
        ph = ph.resize((ph_w, ph_h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2, percent=60))
        box_w, box_h = int(600 * ph.size[0] / ph.size[1]), 600
        cx, cy = 76 + box_w // 2, 60 + box_h // 2
        crop = ph.crop(((ph_w - box_w) // 2, (ph_h - box_h) // 2, (ph_w + box_w) // 2, (ph_h + box_h) // 2))
        d.rectangle([cx - box_w // 2 - 10, cy - box_h // 2 - 10, cx + box_w // 2 + 10, cy + box_h // 2 + 10], fill=(255, 255, 255), outline=RULE)
        im.paste(crop, (cx - box_w // 2, cy - box_h // 2))
        x_text = cx + box_w // 2 + 60
    else:
        x_text = 80
    d = ImageDraw.Draw(im, "RGBA")
    d.text((x_text, 150), "The CubXL, empty", font=font(40, True), fill=INK)
    for i, line in enumerate(["Genmitsu PROVerXL 4030 V2 frame, Ursa Labs' CubOS",
                              "Working volume 361 × 278 × 122 mm (Ben's 2026-10-02 calibration)",
                              "Photo: Ben Whitney, issue #133, 2026-06-26",
                              "",
                              "Next: the same machine as a model, then every",
                              "module and tool a copper corrosion night needs"]):
        d.text((x_text, 220 + 32 * i), line, font=font(20), fill=INK2 if i < 3 else INK)
    return np.asarray(im)


def overlay_3d(img, scene, st, t, chapter, caption=None, label=None, closeup=None, active=None):
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im, "RGBA")
    topbar(d, chapter)
    if active is not None:
        tool_panel(d, active)
    if caption:
        caption_bar(d, caption)
    if label is not None:
        text, xyz, offset = label
        ax, ay = scene.project(xyz)
        if 0 < ax < W and 0 < ay < H:
            lx, ly = ax + offset[0], ay + offset[1]
            lx = min(max(lx, 20), W - 20 - font(16, True).getlength(text) - 16)
            ly = min(max(ly, 112), H - 70)
            label_at(d, (lx, ly), text, anchor_xy=(ax, ay))
    if closeup is not None:
        closeup(im, d)
    return np.asarray(im)


# ------------------------------------------------------------------ the timeline
class Video:
    def __init__(self):
        self.t_photo = (0.0, 4.6)
        self.t_dissolve = (4.6, 5.8)
        self.t_orbit = (5.8, 9.2)
        self.place = Placement(self.t_orbit[1])
        self.t_prep = (self.place.t1 + 0.9, self.place.t1 + 0.9 + CARD_DUR * len(PREP_CARDS))
        self.story = build_story(self.t_prep[1] + 0.3)
        self.t_run = (self.t_prep[1], self.story.total)
        self.t_after = (self.story.total, self.story.total + CARD_DUR)
        self.t_outro = (self.t_after[1], self.t_after[1] + 4.5)
        self.total = self.t_outro[1]
        self.cams = [(self.t_dissolve[0], self._c(FRONT, 26.0)), (self.t_orbit[0] + 0.2, self._c(FRONT, 26.0)),
                     (self.t_orbit[1], self._c(OVERVIEW, 30.0))]

    @staticmethod
    def _c(pf, ang):
        return (np.array(pf[0], float), np.array(pf[1], float), np.array((0, 0, 1.0)), ang)

    def kind(self, t):
        if t < self.t_dissolve[0]:
            return "photo"
        if t < self.t_orbit[1]:
            return "intro3d"
        if t < self.place.t1 + 0.9:
            return "place"
        if t < self.t_prep[1]:
            return "prep"
        if t < self.t_run[1]:
            return "run"
        if t < self.t_after[1]:
            return "after"
        return "outro"


def empty_state(t, hide_all=True):
    st = {"t": t, "head": PLACE_HEAD, "tip_on": False, "tip_liq": False, "tips_taken": set(),
          "ecap": (deck_cu.CUPS["park cup"][0], deck_cu.CUPS["park cup"][1], 45.0), "open_vial": None,
          "sim_t": 0.0, "tube_ul": 0.0, "level": 0.0, "lit": ()}
    st["hidden"] = {g for g, _, _ in DECK_MODULES} | {g for g, _, _ in HEAD_TOOLS} if hide_all else set()
    return st


def make_trace_inset(scene):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.2, 1.9), dpi=100, facecolor="#fcfcfb")
    t = scene.trace_t / 60
    ax.plot(t, scene.trace_I * 1e9, color="#2a78d6", lw=1.6)
    ax.set_yscale("symlog", linthresh=10)
    ax.set_xlim(0, t[-1])
    ax.set_ylim(min(-400, float(np.nanmin(scene.trace_I)) * 1.3e9), max(4000, float(np.nanmax(scene.trace_I)) * 1.3e9))
    ax.set_xlabel("minutes (simulated)", fontsize=8, color="#52514e")
    ax.set_ylabel("current, nA", fontsize=8, color="#52514e")
    ax.tick_params(labelsize=7, colors="#898781")
    for sp_ in ax.spines.values():
        sp_.set_color("#e1e0d9")
    ax.grid(True, color="#e1e0d9", lw=0.5)
    ax.set_title(f"current through the spot ({scene.field_src})", fontsize=8, color="#0b0b0b", loc="left")
    fig.tight_layout(pad=0.4)
    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy())
    h = img.size[1]
    y0, y1 = ax.get_ylim()

    def xpix(sim_s):
        disp = ax.transData.transform((sim_s / 60.0, 0))
        return disp[0], h - ax.transData.transform((0, y1))[1], h - ax.transData.transform((0, y0))[1]
    plt.close(fig)
    return img, xpix


def make_colorbar(cmap, lo, hi, label):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(2.6, 0.62), dpi=100, facecolor="#fcfcfb")
    cb = matplotlib.colorbar.ColorbarBase(ax, cmap=cmap, orientation="horizontal", norm=matplotlib.colors.Normalize(lo, hi))
    cb.set_label(label, fontsize=7.5, color="#52514e")
    cb.ax.tick_params(labelsize=7, colors="#898781")
    fig.tight_layout(pad=0.3)
    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy())
    plt.close(fig)
    return img


def phase_of(mins):
    return "OCP" if mins < 30 else "LPR" if mins < 32 else "rest" if mins < 37 else "+50 mV hold" if mins < 47 else "OCP"


class Renderer:
    def __init__(self):
        self.v = Video()
        self.scene = Scene()
        self.inset, self.xpix = make_trace_inset(self.scene)
        self.cb_o2 = make_colorbar(self.scene.cmap_o2, 0, 1, "O₂, fraction of air saturation (right face)")
        self.cb_cu = make_colorbar(self.scene.cmap_cu, *self.scene.cu_clim, "dissolved Cu, µM (left face)")
        self._front_frame = None

    def render3d(self, st, cam):
        self.scene.set_state(st)
        self.scene.set_camera(cam)
        return self.scene.frame()

    def frame(self, t):
        v, s = self.v, self.v.story
        k = v.kind(t)
        if k == "photo":
            return photo_card(t)
        if k == "intro3d":
            st = empty_state(t)
            raw = self.render3d(st, interp_cam(v.cams, t))
            img = overlay_3d(raw, self.scene, st, t, "the model", caption="The same machine as a model, in the CubOS deck frame: origin front-left, +Y away from you, working volume outlined")
            if t < v.t_dissolve[1]:
                a = ease((t - v.t_dissolve[0]) / (v.t_dissolve[1] - v.t_dissolve[0]))
                img = (photo_card(v.t_dissolve[0]) * (1 - a) + img * a).astype(np.uint8)
            return img
        if k == "place":
            p = v.place
            st = p.state(t)
            raw = self.render3d(st, interp_cam(p.cams(), t))
            label = None
            if "label" in st:
                lab, anc, tool, u = st["label"]
                xyz = tuple(np.add(st["head"], anc)) if tool else anc
                label = (lab, xyz, (40, -50))
            cap = "Deck modules, one at a time" if t < p.t_tools - 0.3 else "Tools on the gantry head: they move together, 55 mm apart"
            return overlay_3d(raw, self.scene, st, t, "placing the modules", caption=cap, label=label)
        if k == "prep":
            i = min(int((t - v.t_prep[0]) // CARD_DUR), len(PREP_CARDS) - 1)
            img = card_image(PREP_CARDS[i], t - v.t_prep[0] - i * CARD_DUR)
            if i == 0 and t - v.t_prep[0] < 0.5:
                a = ease((t - v.t_prep[0]) / 0.5)
                img = (img * a + 246 * (1 - a)).astype(np.uint8)
            return img
        if k == "run":
            st = run_state(s, t)
            m0, m1 = s.measure
            st["closeup"] = m0 + 0.8 <= t <= m1 + 0.1
            raw = self.render3d(st, interp_cam(s.cams, t))
            cap = [c for c in s.captions if c[0] <= t + 1e-9]
            caption = cap[-1][2] if cap else "One spot, start to finish"
            label = None
            tool = st.get("tool")
            if tool in ("capper", "pipette", "camera"):
                hx, hy, hz = st["head"]
                pt = {"capper": (hx, hy, hz - MAGNET_HANG), "pipette": (hx + PIP[0], hy + PIP[1], hz - (TIP_LEN if st["tip_on"] else 0) + 4),
                      "camera": (hx + CAM_OFF[0], hy + CAM_OFF[1], hz + 8)}[tool]
                label = (f"{TOOLS[tool]}: {st['what']}", pt, (60, -70))
            elif tool == "pstat":
                label = (f"{TOOLS[tool]}: {st['what']}", (40, 300, 40), (40, -60))
            close = None
            if st["closeup"]:
                label = None
                close = self.closeup_painter(st)
            return overlay_3d(raw, self.scene, st, t, "one spot", caption=caption, label=label, closeup=close, active=tool)
        if k == "after":
            img = card_image(AFTER_CARD, t - v.t_after[0], chapter="after the night")
            return img
        st = empty_state(t, hide_all=False)
        raw = self.render3d(st, (np.array((640, -380, 520), float), np.array((190, 175, 35), float), np.array((0, 0, 1.0)), 30.0))
        img = overlay_3d(raw, self.scene, st, t, "summary")
        im = Image.fromarray(img)
        d = ImageDraw.Draw(im, "RGBA")
        d.rectangle([40, 470, 760, 690], fill=(252, 252, 251, 238), outline=RULE)
        for i, line in enumerate(OUTRO_LINES):
            d.text((60, 486 + 30 * i), line, font=font(18, i == 0), fill=INK if i == 0 else INK2)
        return np.asarray(im)

    def closeup_painter(self, st):
        sc = self

        def paint(im, d):
            sim_t = st["sim_t"] if st["sim_t"] < 1e8 else float(sc.scene.trace_t[-1])
            iw, ih = sc.inset.size
            x0, y0 = W - iw - 16, H - 80 - ih - 12
            im.paste(sc.inset, (x0, y0))
            xp, ytop, ybot = sc.xpix(sim_t)
            d.line([x0 + xp, y0 + ytop, x0 + xp, y0 + ybot], fill=ORANGE + (255,), width=2)
            im.paste(sc.cb_cu, (16, H - 80 - sc.cb_cu.size[1] - 12))
            im.paste(sc.cb_o2, (16 + sc.cb_cu.size[0] + 10, H - 80 - sc.cb_o2.size[1] - 12))
            mins = sim_t / 60
            d.rectangle([14, 92, 420, 152], fill=(252, 252, 251, 215))
            d.text((24, 98), f"t = {mins:4.1f} min   {phase_of(mins)}", font=font(22, True), fill=INK)
            d.text((24, 128), "AS568-006 spot, 150 µL seawater, reference tip 3 mm up", font=font(12), fill=INK2)
            for text, xyz in (("2 mm Ag/AgCl capillary", (S1[0], S1[1], FACE_Z + 8)), ("Pt coil", (S1[0] - 2.6, S1[1] - 0.2, FACE_Z + 3.2)),
                              ("FKM O-ring, squeezed 21 %", (S1[0] + 2.3, S1[1] - 0.5, FACE_Z + 0.9)),
                              ("C71500, wetted to Ø4.0 mm (ID 2.90)", (S1[0] + 0.4, S1[1] - 1.3, FACE_Z + 0.15))):
                x, y = sc.scene.project(xyz)
                if 0 < x < W and 0 < y < H:
                    d.text((x + 6, y - 8), text, font=font(13), fill=INK, stroke_width=3, stroke_fill=(252, 252, 251))
            tool_panel(d, "pstat")
        return paint


OUTRO_LINES = [
    "One spot: about 67 min of deck time, 9 tubes and 17 tips a night",
    "Deck check with the CAD cap: 118 tool-down events, 0 collisions (deck_cu.py)",
    "CAD of the cap, lid and tray: alloy-corrosion/copper/cad/",
    "Well simulation: alloy-corrosion/copper/sim_well_hf.py",
    "github.com/vertical-cloud-lab/byu-vcl/pull/278",
]


# ------------------------------------------------------------------ main
def gif_frame(img):
    return Image.fromarray(img).resize((GW, GH), Image.LANCZOS)


def named_stills(v):
    s = v.story
    return {"photo": 3.0, "overview": v.place.t_tools - 0.4, "placement": v.place.items[3][0] + DROP + 0.5,
            "tools": v.place.items[-4][0] + DROP + 0.6, "prep": v.t_prep[0] + 2 * CARD_DUR + 5.0, "fill": s.fill_still,
            "closeup": s.measure[1] - 0.5, "acid": [c[0] for c in s.captions if c[2].startswith("9 ")][0] + 3.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="", help="comma-separated times in seconds to save as PNG stills, no video")
    ap.add_argument("--part", default="", help="i/n: render the i-th of n equal frame ranges to /tmp/cubxl_seg_i.mp4")
    ap.add_argument("--assemble", type=int, default=0, help="n: join /tmp/cubxl_seg_*.mp4 and build the GIF")
    args = ap.parse_args()
    v = Video()
    n = int(math.ceil(v.total * FPS))
    gif_ranges = [(v.t_run[0], v.t_run[1])]
    gif_dir = Path(tempfile.gettempdir()) / "cubxl_gif"
    if args.assemble:
        import subprocess
        import imageio_ffmpeg
        lst = Path(tempfile.gettempdir()) / "cubxl_segs.txt"
        lst.write_text("".join(f"file '{Path(tempfile.gettempdir()) / f'cubxl_seg_{i}.mp4'}'\n" for i in range(args.assemble)))
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", "-movflags", "+faststart", str(HERE / "cubxl-cu-spot.mp4")], check=True)
        frames = [Image.open(f).convert("RGB") for f in sorted(gif_dir.glob("*.png"))]
        if not frames:
            print("assembled; no GIF frames in this range", flush=True)
            return
        sheet = Image.new("RGB", (GW, GH * 6))
        for i, j in enumerate(np.linspace(0, len(frames) - 1, 6).astype(int)):
            sheet.paste(frames[j], (0, GH * i))
        pal = sheet.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        gq = [g.quantize(palette=pal, dither=Image.Dither.NONE) for g in frames]
        gq[0].save(HERE / "cubxl-cu-spot.gif", save_all=True, append_images=gq[1:], duration=100, loop=0, optimize=True)
        print("assembled", n, "frames;", len(frames), "GIF frames", flush=True)
        return
    r = Renderer()
    print(f"{v.total:.1f} s, {n} frames; run {v.t_run[0]:.1f}-{v.t_run[1]:.1f} s; field from {r.scene.field_src}", flush=True)
    stills = [float(x) for x in args.stills.split(",") if x.strip()]
    if stills:
        for t in stills:
            Image.fromarray(r.frame(t)).save(f"/tmp/cubxl_cu_still_{t:06.2f}.png")
            print("still", t, flush=True)
        return
    k0, k1, out = 0, n, HERE / "cubxl-cu-spot.mp4"
    if args.part:
        i, m = (int(x) for x in args.part.split("/"))
        k0, k1 = n * i // m, n * (i + 1) // m
        out = Path(tempfile.gettempdir()) / f"cubxl_seg_{i}.mp4"
    gif_dir.mkdir(exist_ok=True)
    import imageio.v2 as imageio
    writer = imageio.get_writer(out, fps=FPS, codec="libx264", quality=None, macro_block_size=8,
                                ffmpeg_params=["-crf", "21", "-preset", "slow", "-pix_fmt", "yuv420p", "-g", "60"])
    named = named_stills(v)
    for k in range(k0, k1):
        t = k / FPS
        img = r.frame(t)
        writer.append_data(img)
        for name, ts in named.items():
            if k == int(round(ts * FPS)):
                Image.fromarray(img).save(HERE / f"cubxl-cu-{name}.png", optimize=True)
        if k % 10 == 0 and any(a <= t < b for a, b in gif_ranges):
            gif_frame(img).save(gif_dir / f"{k:05d}.png")
        if (k - k0) % 150 == 0:
            print("frame", k, "of", n, flush=True)
    writer.close()
    print("done", k0, k1, flush=True)


if __name__ == "__main__":
    main()
