"""Animate one copper corrosion spot on the CubXL deck, in 3D. Writes cubxl-cu-spot.mp4
(1280 x 720, 30 fps) and cubxl-cu-spot.gif (640 x 360, 10 fps).

Where the geometry comes from:
- Exact models: the three STEP files in modules/electromagnetic-capper/cad/ (Ben's 9-position
  20 mL vial holder, the 16 mm magnetic vial cap, the PAW-V2 electromagnet mount), meshed
  with gmsh as they are; the AS568-006 FKM O-ring (ID 2.90 mm, cross-section 1.78 mm).
- Exact numbers: every deck position, tool offset (pipette +55, +11; camera -40, +10), tool
  hang (magnet face 16 mm below the carriage, 35 mm tip), the working volume and travel
  height (z 122) from Ben's 2026-10-02 gantry and deck files, via deck_cu.py and
  ../plot_deck_layout.py; tip rack, vial and tube heights from the same files.
- The well's contents during the measurement: the O2 field computed by sim_well.py (cap B).
- Schematic, with the right footprint: the CubXL frame and beams, the P20 body, the camera,
  the printed coupon tray, and the electrode cap, which is a proposal (../cubxl-setup.md
  section 3, with the copper changes).

    xvfb-run -a python render_cubxl_cu.py            # about 6 min on 4 cores
    xvfb-run -a python render_cubxl_cu.py --frames 0,750,900   # stills only, for checking
"""

from __future__ import annotations

import argparse
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CAD = REPO / "modules" / "electromagnetic-capper" / "cad"
sys.path.insert(0, str(HERE))
import deck_cu  # noqa: E402

base = deck_cu.base
W, H = 1280, 720
FPS = 30

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

C = {  # material colours
    "deck": "#dcdbd5", "frame": "#3b3b3b", "rail": "#5a5a5a", "petg": "#dedbd2", "petg_dark": "#c8c3b5",
    "tray": "#f4efe6", "lid": "#e9a47c", "glass": "#e8f1f6", "capbody": "#efe9e2", "steel": "#8d9196", "fkm": "#1d1d1d",
    "cuni": "#b89a8a", "nab": "#c39b55", "ded": "#c08a62", "ptfe": "#f7f7f5", "pt": "#c7c9cc",
    "agcl": "#e9e6df", "tip": "#f2f2ee", "tube": "#f4f4f0", "pip": "#e7e7e3", "pip_top": "#2d2d2d",
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


def revolve(profile_rz, sweep=360.0, start=0.0, res=None):
    """Revolve a closed (r, z) profile about the z axis. Returns PolyData with end caps."""
    pts = np.array([[r, 0.0, z] for r, z in profile_rz])
    poly = pv.PolyData(pts, faces=np.hstack([[len(pts)], np.arange(len(pts))]))
    res = res or max(8, int(sweep / 6))
    m = poly.extrude_rotate(resolution=res, angle=sweep, capping=sweep < 360, rotation_axis=(0, 0, 1))
    if start:
        m = m.rotate_z(start, inplace=False)
    return m.triangulate().clean().compute_normals(auto_orient_normals=True, split_vertices=True, feature_angle=40)


def circle_profile(rc, zc, rad, n=24):
    return [(rc + rad * math.cos(t), zc + rad * math.sin(t)) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def box(x0, y0, z0, x1, y1, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1))


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ the scene
class Scene:
    def __init__(self):
        pv.global_theme.allow_empty_mesh = True
        self.pl = pv.Plotter(off_screen=True, window_size=(W, H), lighting="light_kit")
        self.pl.set_background("#eeede8", top="#fcfcfb")
        self.pl.enable_anti_aliasing("fxaa")
        self.actors = {}
        self.build_static()
        self.build_dynamic()

    def add(self, key, mesh, **kw):
        kw.setdefault("smooth_shading", True)
        kw.setdefault("specular", 0.15)
        a = self.pl.add_mesh(mesh, **kw)
        self.actors[key] = a
        return a

    # ---- static deck
    def build_static(self):
        add = self.add
        add("deck", box(-50, -45, -6, 430, 445, 0), color=C["deck"], smooth_shading=False)
        # the working volume the capper reaches (Ben's gantry file), as a faint outline
        wv = box(0, 0, 0, 361, 278, 0.4)
        add("wv", wv.extract_feature_edges(), color="#8f8e88", line_width=1.5, smooth_shading=False)

        # coupon tray (printed) with four stations: S1 C71500 Cu-Ni, S2 C95800 NAB, S3 DED pad, S4 PTFE blank
        x0, y0, x1, y1 = base.TRAY["rect"]
        add("tray", box(x0, y0, 0, x1, y1, FACE_Z), color=C["tray"], smooth_shading=False)
        lid_prof = [(A_SPOT, 1.42), (3.45, 1.42), (3.45, 0.0), (8.0, 0.0), (8.0, 6.0), (R_BORE, 6.0), (R_BORE, Z_STEP), (A_SPOT, Z_STEP)]
        oring = [(2.4 + 0.94 * math.cos(t), 0.71 + 0.70 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 28, endpoint=False)]
        coupon_prof = [(0.0, -3.0), (6.0, -3.0), (6.0, 0.0), (0.0, 0.0)]
        materials = ["cuni", "nab", "ded", "ptfe"]
        for i, sx in enumerate(S_X):
            cut = i == 0
            sweep, start = (CUT_SWEEP, CUT0) if cut else (360.0, 0.0)
            add(f"lid{i}", revolve(lid_prof, sweep, start).translate((sx, S_Y, FACE_Z), inplace=False), color=C["lid"])
            add(f"oring{i}", revolve(oring, sweep, start).translate((sx, S_Y, FACE_Z), inplace=False), color=C["fkm"], lighting=False)
            add(f"coupon{i}", revolve(coupon_prof, sweep, start).translate((sx, S_Y, FACE_Z + 0.01), inplace=False), color=C[materials[i]],
                specular=0.6 if i < 3 else 0.1, specular_power=30)
            for px in (sx - 11, sx + 11):  # reference / counter pads
                add(f"pad{i}{px}", box(px - 1.5, S_Y - 3, LID_TOP - 0.01, px + 1.5, S_Y + 3, LID_TOP + 0.6), color=C["brass"], specular=0.6)

        # Ben's 9-position holder (STEP), rotated so its positions run +Y from y 35
        holder = step_mesh("9VialHolder20mL_TightFit", 4.0, 8).rotate_z(180, inplace=False).translate((deck_cu.HOLDER_X, deck_cu.HOLDER_Y[0], 0), inplace=False)
        add("holder", holder, color=C["petg_dark"], smooth_shading=False)
        self.vial_cap_mesh = step_mesh("VialCap16mm", 1.5, 12)
        liquids = {"1 M HNO3, trace metal": C["acid"], "ASW (D1141, no heavy metals)": C["asw"], "ASW + 10 mg/L S": C["sulf"],
                   "ASW + 0.1 mg/L S": "#ece2b4", "DI water": C["water"], "spare (FeSO4 nights only)": "#cfe0c8"}
        self.vials = {}
        for name, (vx, vy) in {**deck_cu.STOCKS, **deck_cu.SPARE}.items():
            add(f"vial:{name}", pv.Cylinder(center=(vx, vy, VIAL_RIM / 2), direction=(0, 0, 1), radius=13.75, height=VIAL_RIM, resolution=48, capping=True),
                color=C["glass"], opacity=0.35, specular=0.6)
            add(f"liq:{name}", pv.Cylinder(center=(vx, vy, 19), direction=(0, 0, 1), radius=12.6, height=36, resolution=48), color=liquids[name], opacity=0.85)
            cap = self.vial_cap_mesh.translate((vx, vy, VIAL_CAP_TOP - 0.5), inplace=False)
            add(f"vcap:{name}", cap, color="#e3e1da")
            self.vials[name] = (vx, vy)

        # tip racks (panda_2x15) and tips: 20 uL tips as cones, top at 66, end 35 below the nozzle seat
        tip_prof = [(0.0, 0.0), (0.45, 0.0), (2.6, 30.0), (2.9, 37.0), (3.3, 39.0), (0.0, 39.0)]
        self.tip_mesh = revolve(tip_prof, 360, 0, res=24)
        for ri, rack in enumerate((base.TIP_RACK_1, base.TIP_RACK_2)):
            rx0, ry0, rx1, ry1 = base.rack_rect(rack)
            add(f"rack{ri}", box(rx0, ry0, 0, rx1, ry1, 55), color=C["petg_dark"] if ri == 0 else C["petg"], smooth_shading=False)
            tips = [self.tip_mesh.translate((tx, ty, 66.0 - 39.0), inplace=False) for (tx, ty) in base.rack_tips(rack)]
            if ri == 0:
                self.rack1_tips = list(base.rack_tips(rack))
                self.tip_actors = []
                for j, m in enumerate(tips):
                    self.tip_actors.append(add(f"tip{ri}_{j}", m, color=C["tip"], specular=0.3))
            else:
                add(f"tips{ri}", pv.merge(tips), color=C["tip"], specular=0.3)

        # tube rack: 2 x 8 open 0.5 mL PP tubes
        tx0, ty0, tx1, ty1 = base.TUBE_RACK["rect"]
        add("tuberack", box(tx0, ty0, 0, tx1, ty1, 20), color=C["petg"], smooth_shading=False)
        tube_prof = [(0.0, 0.0), (1.2, 0.0), (3.6, 12.0), (3.9, 32.0), (4.6, 32.0), (4.6, 30.5), (4.2, 30.5), (4.2, 12.2), (1.6, 0.6), (0.0, 0.6)]
        tube = revolve(tube_prof, 360, 0, res=32)
        self.tubes = [(x, y) for y in base.TUBE_Y for x in base.TUBE_X]
        add("tubes", pv.merge([tube.translate((x, y, 0), inplace=False) for x, y in self.tubes]), color=C["tube"], opacity=0.75, specular=0.4)

        # cups (4 mL vials): rinse 2 ASW, rinse 1 DI, park
        for name, (cx, cy) in deck_cu.CUPS.items():
            add(f"cup:{name}", pv.Cylinder(center=(cx, cy, 22.5), direction=(0, 0, 1), radius=7.5, height=45, resolution=40), color=C["glass"], opacity=0.4, specular=0.6)
            add(f"cupliq:{name}", pv.Cylinder(center=(cx, cy, 17), direction=(0, 0, 1), radius=6.6, height=32, resolution=40),
                color=C["asw"] if "ASW" in name else (C["water"] if "DI" in name else "#d8d2ea"), opacity=0.8)
        tw = deck_cu.TIP_WASTE
        add("tipwaste", pv.Cylinder(center=(*tw["c"], tw["top"] / 2), direction=(0, 0, 1), radius=tw["r"], height=tw["top"], resolution=48), color="#d4d3cd")
        px0, py0, px1, py1 = base.PSTAT_BOX["rect"]
        add("pstat", box(px0, py0, 0, px1, py1, 40), color=C["pstat"], smooth_shading=False)
        cable = pv.Spline(np.array([[80, 310, 20], [120, 300, 12], [150, 275, 8], [172, 258, 10]]), 40).tube(radius=2.0)
        add("cable", cable, color="#262626")

    # ---- moving things
    def build_dynamic(self):
        add = self.add
        # head: PAW-V2 electromagnet mount (STEP), its 25 mm electromagnet, P20 (schematic), camera_3, carriage
        mount = step_mesh("PAW-V2-ElectromagnetMount", 2.0, 16)
        mount = mount.rotate_x(180, inplace=False)  # open end down, toward the cap
        axis = (63.17, -6.53)  # bore axis of the STEP, fitted; after the flip y -> -y
        mount = mount.translate((-axis[0], -axis[1], -mount.bounds[4] - MAGNET_HANG), inplace=False)
        self.head_parts = {
            "mount": (mount, C["mount"]),
            "magnet": (pv.Cylinder(center=(0, 0, -MAGNET_HANG + 10.5), direction=(0, 0, 1), radius=12.5, height=20, resolution=48), C["steel"]),
            "plate": (box(-55, -14, 27, PIP[0] + 22, PIP[1] + 18, 33), C["rail"]),
            "pip_shaft": (pv.Cylinder(center=(PIP[0], PIP[1], 22), direction=(0, 0, 1), radius=4.0, height=44, resolution=32), C["pip"]),
            "pip_body": (box(PIP[0] - 17, PIP[1] - 13, 44, PIP[0] + 17, PIP[1] + 13, 150), C["pip"]),
            "pip_top": (box(PIP[0] - 17, PIP[1] - 13, 150, PIP[0] + 17, PIP[1] + 13, 162), C["pip_top"]),
            "camera": (box(CAM_OFF[0] - 11, CAM_OFF[1] - 11, 8, CAM_OFF[0] + 11, CAM_OFF[1] + 11, 34), "#3a3a3a"),
            "zslide": (box(-12, -14, 33, 12, -4, 92), C["rail"]),
        }
        for k, (m, col) in self.head_parts.items():
            add(f"head:{k}", m, color=col, smooth_shading=k in ("mount", "magnet", "pip_shaft"))
        add("xbeam", box(-55, -10, 0, 435, 10, 16), color="#7d7c77", smooth_shading=False, opacity=0.55)
        # the tip on the pipette (moves with the head)
        add("head_tip", self.tip_mesh.translate((PIP[0], PIP[1], -TIP_LEN), inplace=False), color=C["tip"], specular=0.3)
        add("head_tipliq", pv.Cylinder(center=(PIP[0], PIP[1], -TIP_LEN + 3), direction=(0, 0, 1), radius=0.9, height=5, resolution=16), color=C["asw"])
        # the electrode cap: skirt with FKM gasket, body, steel disc, 2 mm Ag/AgCl capillary, Pt coil, pogo pins.
        # Local origin: centre of the skirt's underside (rests on the lid top), z up.
        cap_prof = [(1.0, 0.0), (11.5, 0.0), (11.5, -0.01), (13.0, -0.01), (13.0, 4.0), (9.0, 4.0), (9.0, 14.8), (1.0, 14.8)]
        parts = {
            "body": (revolve(cap_prof, CUT_SWEEP, CUT0), C["capbody"]),
            "gasket": (revolve([(8.9, -0.35), (10.3, -0.35), (10.3, 0.0), (8.9, 0.0)], CUT_SWEEP, CUT0), "#3a3a3a"),
            "disc": (revolve([(0.0, 14.8), (6.0, 14.8), (6.0, 16.0), (0.0, 16.0)], CUT_SWEEP, CUT0), C["steel"]),
            "capillary": (revolve([(0.0, -CAP_PROTRUDE), (1.0, -CAP_PROTRUDE), (1.0, 14.8), (0.0, 14.8)], CUT_SWEEP, CUT0), C["agcl"]),
        }
        coil = []
        for turn in range(5):
            zc = 2.4 + 0.4 * turn - 6.0
            th = np.radians(np.linspace(CUT0 + 4, CUT0 + CUT_SWEEP - 4, 80))
            pts = np.c_[2.6 * np.cos(th), 2.6 * np.sin(th), np.full_like(th, zc)]
            coil.append(pv.Spline(pts, 120).tube(radius=0.125, n_sides=10))
        coil.append(pv.Line((2.6 * math.cos(math.radians(90)), 2.6 * math.sin(math.radians(90)), -3.6), (0, 2.6, 4.0)).tube(radius=0.125))
        for th in (CUT0, CUT0 + CUT_SWEEP):
            n_ = (-math.sin(math.radians(th)), math.cos(math.radians(th)), 0.0)
            for turn in range(5):
                zc = 2.4 + 0.4 * turn - 6.0
                coil.append(pv.Cylinder(center=(2.625 * math.cos(math.radians(th)), 2.625 * math.sin(math.radians(th)), zc),
                                        direction=n_, radius=0.14, height=0.06, resolution=16))
        parts["coil"] = (pv.merge(coil), C["pt"])
        parts["pogo"] = (pv.merge([pv.Cylinder(center=(sx, 0, 1.5), direction=(0, 0, 1), radius=0.5, height=4.2, resolution=12) for sx in (-11, 11)]), C["brass"])
        self.ecap_parts = parts
        for k, (m, col) in parts.items():
            add(f"ecap:{k}", m, color=col, specular=0.5 if k in ("disc", "coil", "pogo") else 0.15)
        # the vial cap carried on the magnet (shown only while a stock is open)
        add("carried_vcap", self.vial_cap_mesh, color="#e3e1da")
        # liquid in S1's well: a 270-degree section coloured by the simulated O2 field
        self.load_field()
        # liquid in tube 1
        add("tube1_liq", pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=3.4, height=1.0, resolution=24), color=C["asw"], opacity=0.9)

    def load_field(self):
        d = np.load(HERE / "sim_well_fields.npz")
        self.f_times = d["times"]
        self.f_o2 = d["o2"]  # (nt, nr, nz), NaN outside the liquid
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
            g.cell_data["O2"] = np.ones(len(r) * len(z))
            self.planes.append(g)
        from matplotlib.colors import LinearSegmentedColormap
        self.cmap = LinearSegmentedColormap.from_list("o2", ["#0d366b", "#256abf", "#6da7ec", "#cde2fb"])
        for i, g in enumerate(self.planes):
            self.add(f"field{i}", g, scalars="O2", cmap=self.cmap, clim=(0, 1), nan_opacity=0.0, show_scalar_bar=False,
                     smooth_shading=False, lighting=False)
        # liquid surface: a thin 270-degree annulus
        self.surface = revolve([(1.0, 0.0), (R_BORE, 0.0), (R_BORE, 0.05), (1.0, 0.05)], CUT_SWEEP, CUT0)
        self.add("surface", self.surface, color=C["asw"], opacity=0.45)
        self.liquid_mask = ~np.isnan(self.f_o2[0])
        coil = d["coil"]
        self.coil_src = np.where(coil)
        self.coil_dst = (np.minimum(self.coil_src[0] + 6, coil.shape[0] - 1), self.coil_src[1])
        self.liquid_mask[coil] = True

    def set_field(self, sim_t, level_mm, show_cap_capillary):
        """O2 fraction at sim_t (s), cut at the liquid level (mm above the metal)."""
        ts = self.f_times
        if sim_t <= ts[0]:
            f = np.ones_like(self.f_o2[0])
        elif sim_t >= ts[-1]:
            f = self.f_o2[-1]
        else:
            j = int(np.searchsorted(ts, sim_t)) - 1
            u = (sim_t - ts[j]) / (ts[j + 1] - ts[j])
            f = (1 - u) * self.f_o2[j] + u * self.f_o2[j + 1]
            if j == -1:
                f = self.f_o2[0]
        f = np.array(f)
        f[self.coil_src] = f[self.coil_dst]
        f = np.where(self.liquid_mask, np.nan_to_num(f, nan=1.0), np.nan)
        if not show_cap_capillary:  # before the cap is on, the capillary's cells are liquid too
            pass
        zz = self.f_z[None, :] + 0 * f
        f = np.where(zz <= level_mm, f, np.nan)
        for g in self.planes:
            g.cell_data["O2"][:] = f.ravel(order="F")
            g.Modified()

    # ---- per-frame state
    def set_state(self, st):
        hx, hy, hz = st["head"]
        Mh = T(hx, hy, hz)
        for k in self.head_parts:
            self.actors[f"head:{k}"].user_matrix = Mh if k != "zslide" else T(hx, hy, hz)
        self.actors["xbeam"].user_matrix = T(0, hy - 24, hz + 92)
        zs = self.head_parts["zslide"][0]
        self.actors["head:zslide"].user_matrix = T(hx, hy, hz)
        self.actors["head_tip"].user_matrix = Mh
        self.actors["head_tip"].visibility = st["tip_on"]
        self.actors["head_tipliq"].user_matrix = Mh
        self.actors["head_tipliq"].visibility = st["tip_on"] and st["tip_liq"]
        for j, a in enumerate(self.tip_actors):
            a.visibility = j not in st["tips_taken"]
        # electrode cap
        where = st["ecap"]
        if where == "head":
            Mc = T(hx, hy, hz - CAP_HANG + CAP_PROTRUDE)
        else:
            x, y, z = where
            Mc = T(x, y, z)
        for k in self.ecap_parts:
            self.actors[f"ecap:{k}"].user_matrix = Mc
        # stock caps
        for name, (vx, vy) in self.vials.items():
            self.actors[f"vcap:{name}"].visibility = st["open_vial"] != name
        if st["open_vial"]:
            self.actors["carried_vcap"].visibility = True
            self.actors["carried_vcap"].user_matrix = T(hx, hy, hz - MAGNET_HANG - 0.5)
        else:
            self.actors["carried_vcap"].visibility = False
        # well liquid
        lvl = st["level"]
        self.set_field(st["sim_t"], lvl, st["ecap"] != "head")
        self.actors["surface"].user_matrix = T(S1[0], S1[1], FACE_Z + lvl)
        self.actors["surface"].visibility = lvl > 0.05
        # tube 1
        tx, ty = self.tubes[0]
        h = st["tube_ul"] / 20.0
        self.actors["tube1_liq"].user_matrix = T(tx, ty, 12.5) @ np.diag([1, 1, max(h, 1e-3), 1])
        self.actors["tube1_liq"].visibility = st["tube_ul"] > 1

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


# ------------------------------------------------------------------ the story
def well_level(v_ul, capped):
    a2 = math.pi * A_SPOT ** 2
    throat = a2 * Z_STEP
    if v_ul <= throat:
        lvl = v_ul / a2
    else:
        lvl = Z_STEP + (v_ul - throat) / (math.pi * R_BORE ** 2)
    if capped and lvl > REF_TIP:
        # the capillary displaces liquid above its tip
        lvl = REF_TIP + (lvl - REF_TIP) * R_BORE ** 2 / (R_BORE ** 2 - 1.0)
    return lvl


class Story:
    """Keyframes for the head and the deck state; captions; camera."""

    def __init__(self):
        self.t = 0.0
        self.keys = []  # (t, head xyz)
        self.events = []  # (t, dict of state changes)
        self.captions = []  # (t0, t1, text)
        self.cams = []  # (t, cam)
        self.head = (236.0, 25.0, TRAVEL)
        self.keys.append((0.0, self.head))
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

    def caption(self, text, dur=None, t0=None):
        t0 = self.t if t0 is None else t0
        self.captions.append([t0, t0 + (dur or 0), text])

    def cam(self, t, pos, foc, up=(0, 0, 1), angle=30.0):
        self.cams.append((t, (np.array(pos, float), np.array(foc, float), np.array(up, float), angle)))

    # convenience: pipette tip end over deck xy at height z_end
    def pip_to(self, x, y, z_end, tip=True, dur=None):
        self.travel(x - PIP[0], y - PIP[1], dur)
        self.move(0.45, z=z_end + (TIP_LEN if tip else 0.0))

    def capper_to(self, x, y, z_face, dur=None):
        self.travel(x, y, dur)
        self.move(0.45, z=z_face + MAGNET_HANG)


def build_story():
    s = Story()
    rack = list(base.rack_tips(base.TIP_RACK_1))
    asw, s10 = deck_cu.STOCKS["ASW (D1141, no heavy metals)"], deck_cu.STOCKS["ASW + 10 mg/L S"]
    acid = deck_cu.STOCKS["1 M HNO3, trace metal"]
    park, rinse1 = deck_cu.CUPS["park cup"], deck_cu.CUPS["rinse 1 (DI)"]
    tube1 = (base.TUBE_X[0], base.TUBE_Y[0])
    s.ev(tip_on=False, tip_liq=False, tips_taken=set(), ecap=(park[0], park[1], 45.0 + CAP_PROTRUDE), open_vial=None,
         well_ul=0.0, sim_t=0.0, tube_ul=0.0, capped=False)

    overview = ((585, -300, 430), (205, 175, 35))
    s.cam(0.0, (610, -60, 360), (205, 175, 35), angle=32)
    s.cam(3.2, *overview, angle=32)
    s.caption("Copper corrosion spot on the CubXL: a proposal in the CubOS deck frame of Ben's 2026-10-02 calibration", 3.2)
    s.wait(3.2)

    # 1 tip
    s.caption("1  Pick up a 20 µL tip from Ben's tip rack (unmoved)", 3.0)
    s.cam(s.t + 1.0, (520, -200, 330), (250, 150, 40), angle=32)
    s.pip_to(rack[0][0], rack[0][1], 59.0, tip=False)
    s.ev(tip_on=True, tips_taken={0})
    s.wait(0.25)
    s.move(0.4, z=TRAVEL)

    # 2 fill with ASW: the capper opens the stock, the pipette moves 135 uL
    s.caption("2  The capper lifts the ASW cap; the P20 builds the well from 135 µL of ASTM D1141 seawater (7 transfers)", 6.2)
    s.capper_to(asw[0], asw[1], VIAL_CAP_TOP)
    s.ev(open_vial="ASW (D1141, no heavy metals)")
    s.wait(0.2)
    s.move(0.4, z=TRAVEL)
    s.pip_to(asw[0], asw[1], 35.0)
    s.ev(tip_liq=True)
    s.wait(0.25)
    s.cam(s.t + 0.8, (500, -170, 320), (245, 175, 40), angle=32)
    s.pip_to(S1[0], S1[1], FACE_Z + 1.0)
    t0 = s.t
    s.fill_still = t0 + 0.9
    s.wait(1.2)
    s.events.append((t0, {"well_ramp": (t0, s.t, 0.0, 135.0)}))
    s.ev(tip_liq=False)
    s.move(0.4, z=TRAVEL)
    s.capper_to(asw[0], asw[1], VIAL_CAP_TOP)
    s.ev(open_vial=None)
    s.wait(0.2)
    s.move(0.35, z=TRAVEL)

    # 3 sulfide last
    s.caption("3  Sulfide last: 15 µL of the 10 mg/L stock, made in the same seawater, gives 1 mg/L S (c1-06)", 5.0)
    s.capper_to(s10[0], s10[1], VIAL_CAP_TOP)
    s.ev(open_vial="ASW + 10 mg/L S")
    s.wait(0.2)
    s.move(0.35, z=TRAVEL)
    s.pip_to(s10[0], s10[1], 35.0)
    s.ev(tip_liq=True)
    s.wait(0.2)
    s.pip_to(S1[0], S1[1], FACE_Z + 1.0)
    t0 = s.t
    s.wait(0.6)
    s.events.append((t0, {"well_ramp": (t0, s.t, 135.0, 150.0)}))
    s.ev(tip_liq=False)
    s.move(0.35, z=TRAVEL)
    s.capper_to(s10[0], s10[1], VIAL_CAP_TOP)
    s.ev(open_vial=None)
    s.wait(0.2)
    s.move(0.35, z=TRAVEL)

    # 4 drop the tip
    s.caption("4  Drop the tip. The head camera checks for liquid outside the O-ring", 2.2)
    s.cam(s.t + 0.6, *overview, angle=32)
    s.pip_to(deck_cu.TIP_WASTE["c"][0], deck_cu.TIP_WASTE["c"][1], 60.0)
    s.ev(tip_on=False)
    s.wait(0.3)
    s.move(0.35, z=TRAVEL)

    # 5 electrode cap: park cup -> S1
    s.caption("5  The capper carries the electrode cap (leak-free Ag/AgCl, Pt coil) from its park cup to S1; an FKM gasket seals the headspace", 5.0)
    s.cam(s.t + 0.8, (360, -120, 300), (150, 220, 40), angle=32)
    s.capper_to(park[0], park[1], 45.0 + CAP_PROTRUDE + 16.0)
    s.ev(ecap="head")
    s.wait(0.2)
    s.move(0.4, z=TRAVEL)
    s.capper_to(S1[0], S1[1], LID_TOP + 16.0)
    s.ev(ecap=(S1[0], S1[1], LID_TOP), capped=True)
    s.wait(0.2)
    s.move(0.4, z=TRAVEL)

    # 6 the measurement, close up, O2 from sim_well.py
    t_meas0 = s.t + 1.6
    close_cam = ((S1[0] + 1.5, S1[1] - 27, FACE_Z + 8.5), (S1[0], S1[1], FACE_Z + 3.4))
    s.cam(s.t + 1.6, *close_cam, angle=30)
    s.travel(236.0, 25.0, 1.2)
    meas = 9.0
    s.caption("6  Measured with the cap on: OCP 30 min, LPR ±10 mV, rest, +50 mV hold 10 min, OCP 5 min. The head is free meanwhile", meas + 1.6)
    s.wait(t_meas0 + meas - s.t)
    s.events.append((t_meas0, {"sim_ramp": (t_meas0 + 0.6, t_meas0 + meas - 0.4, 0.0, float(np.load(HERE / "sim_well_fields.npz")["trace_t"][-1]))}))
    s.cam(s.t + 0.2, *close_cam, angle=30)
    s.cam(s.t + 1.6, (360, -120, 300), (150, 160, 40), angle=32)
    s.measure = (t_meas0, t_meas0 + meas)

    # 7 cap off and rinse, collect, acidify
    s.travel_dur = 0.6
    s.caption("7  Cap to the DI rinse and park; a new tip moves the 150 µL plus a 150 µL rinse into tube 1; the acid tip adds 20 µL 1 M HNO3", 7.6)
    s.capper_to(S1[0], S1[1], LID_TOP + 16.0)
    s.ev(ecap="head", capped=False)
    s.wait(0.15)
    s.move(0.35, z=TRAVEL)
    s.capper_to(rinse1[0], rinse1[1], 45.0 + CAP_PROTRUDE + 16.0 - 6.0)
    s.wait(0.25)
    s.move(0.35, z=TRAVEL)
    s.capper_to(park[0], park[1], 45.0 + CAP_PROTRUDE + 16.0)
    s.ev(ecap=(park[0], park[1], 45.0 + CAP_PROTRUDE))
    s.wait(0.15)
    s.move(0.35, z=TRAVEL)
    s.pip_to(rack[1][0], rack[1][1], 59.0, tip=False)
    s.ev(tip_on=True, tips_taken={0, 1})
    s.move(0.35, z=TRAVEL)
    s.pip_to(S1[0], S1[1], FACE_Z + 0.5)
    t0 = s.t
    s.ev(tip_liq=True)
    s.wait(0.5)
    s.events.append((t0, {"well_ramp": (t0, s.t, 150.0, 0.0)}))
    s.pip_to(tube1[0], tube1[1], 40.0)
    t0 = s.t
    s.ev(tip_liq=False)
    s.wait(0.4)
    s.events.append((t0, {"tube_ramp": (t0, s.t, 0.0, 300.0)}))
    s.move(0.3, z=TRAVEL)
    s.pip_to(deck_cu.TIP_WASTE["c"][0], deck_cu.TIP_WASTE["c"][1], 60.0)
    s.ev(tip_on=False)
    s.move(0.3, z=TRAVEL)
    s.pip_to(acid[0], acid[1], 35.0, tip=False)  # the acid tip, shown bare for brevity
    s.move(0.3, z=TRAVEL)
    s.pip_to(tube1[0], tube1[1], 37.0)
    t0 = s.t
    s.wait(0.4)
    s.events.append((t0, {"tube_ramp": (t0, s.t, 300.0, 320.0)}))
    s.move(0.3, z=TRAVEL)

    # 8 outro
    s.caption("8  Tube 1 goes to ICP-MS (Cu, Ni, Al, Fe, Mn). Next spot: S2. Deck check: 118 tool-down events, 0 collisions", 3.4)
    s.cam(s.t + 0.2, (360, -120, 300), (150, 160, 40), angle=32)
    s.travel(236.0, 25.0, 1.0)
    s.cam(s.t + 2.4, (640, -380, 520), (205, 175, 35), angle=32)
    s.wait(2.4)
    s.total = s.t
    return s


def state_at(s, t):
    st = {}
    for te, kw in s.events:
        if te <= t + 1e-9:
            for k, v in kw.items():
                if k.endswith("_ramp"):
                    continue
                st[k] = v
    st["well_ul"] = 0.0
    st["tube_ul"] = 0.0
    st["sim_t"] = 0.0
    for te, kw in s.events:
        for k, v in kw.items():
            if not k.endswith("_ramp") or te > t + 1e-9:
                continue
            a, b, v0, v1 = v
            val = v0 + (v1 - v0) * min(max((t - a) / (b - a), 0.0), 1.0)
            st[{"well_ramp": "well_ul", "tube_ramp": "tube_ul", "sim_ramp": "sim_t"}[k]] = val
    if t > s.measure[1]:
        st["sim_t"] = 1e9
    # head
    keys = s.keys
    if t >= keys[-1][0]:
        st["head"] = keys[-1][1]
    else:
        j = max(i for i, (tk, _) in enumerate(keys) if tk <= t)
        (t0, p0), (t1, p1) = keys[j], keys[j + 1]
        u = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
        st["head"] = tuple(a + (b - a) * u for a, b in zip(p0, p1))
    st["level"] = well_level(st["well_ul"], st.get("capped", False))
    # tip liquid only while it holds liquid
    st.setdefault("tip_liq", False)
    return st


def cam_at(s, t):
    cams = s.cams
    if t <= cams[0][0]:
        return cams[0][1]
    if t >= cams[-1][0]:
        return cams[-1][1]
    j = max(i for i, (tk, _) in enumerate(cams) if tk <= t)
    (t0, c0), (t1, c1) = cams[j], cams[j + 1]
    u = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
    pos = c0[0] + (c1[0] - c0[0]) * u
    foc = c0[1] + (c1[1] - c0[1]) * u
    up = c0[2] + (c1[2] - c0[2]) * u
    ang = c0[3] + (c1[3] - c0[3]) * u
    return pos, foc, up, ang


# ------------------------------------------------------------------ overlays
def font(size, bold=False):
    from matplotlib import font_manager
    path = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold" if bold else "normal"))
    return ImageFont.truetype(path, size)


def make_trace_inset(scene):
    """The simulated current through the spot, as an image, and a map from sim time to pixel x."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.2, 1.9), dpi=100, facecolor="#fcfcfb")
    t = scene.trace_t / 60
    ax.plot(t, scene.trace_I * 1e9, color="#2a78d6", lw=1.6)
    ax.set_yscale("symlog", linthresh=10)
    ax.set_xlim(0, t[-1]); ax.set_ylim(-400, 4000)
    ax.set_xlabel("minutes (simulated)", fontsize=8, color="#52514e")
    ax.set_ylabel("current, nA", fontsize=8, color="#52514e")
    ax.tick_params(labelsize=7, colors="#898781")
    for sp_ in ax.spines.values():
        sp_.set_color("#e1e0d9")
    ax.grid(True, color="#e1e0d9", lw=0.5)
    for x0, x1, lab in ((0, 30, "OCP"), (37, 47, "+50 mV")):
        ax.text((x0 + x1) / 2, 1500, lab, ha="center", fontsize=7, color="#52514e")
    ax.set_title("current through the spot (sim_well.py, cap B)", fontsize=8, color="#0b0b0b", loc="left")
    fig.tight_layout(pad=0.4)
    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy())
    h = img.size[1]

    def xpix(sim_s):
        disp = ax.transData.transform((sim_s / 60.0, 0))
        return disp[0], h - ax.transData.transform((0, 4000))[1], h - ax.transData.transform((0, -400))[1]
    plt.close(fig)
    return img, xpix


def make_colorbar():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("o2", ["#0d366b", "#256abf", "#6da7ec", "#cde2fb"])
    fig, ax = plt.subplots(figsize=(2.6, 0.62), dpi=100, facecolor="#fcfcfb")
    cb = matplotlib.colorbar.ColorbarBase(ax, cmap=cmap, orientation="horizontal", norm=matplotlib.colors.Normalize(0, 1))
    cb.set_label("O2, fraction of air saturation", fontsize=7.5, color="#52514e")
    cb.ax.tick_params(labelsize=7, colors="#898781")
    fig.tight_layout(pad=0.3)
    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy())
    plt.close(fig)
    return img


LABELS = [  # (text, deck xyz anchor) for the wide shots
    ("S1-S4: coupon tray", (222, 262, 30)),
    ("stocks in Ben's\n9-vial holder (STEP)", (318, 300, 60)),
    ("tip rack 1 (Ben's)", (287, 80, 70)),
    ("tip rack 2", (104, 80, 70)),
    ("tubes for ICP-MS", (220, 20, 36)),
    ("rinse / park cups", (60, 255, 50)),
    ("potentiostat", (40, 330, 45)),
    ("tip waste", (385, 150, 54)),
]


def overlay(img, scene, story, t, st, inset, xpix, cbar):
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im, "RGBA")
    f_title, f_cap, f_small, f_lab = font(19, True), font(17), font(12), font(13)
    d.rectangle([0, 0, W, 34], fill=(252, 252, 251, 225))
    d.text((14, 7), "Copper corrosion on the CubXL: one spot, proposal (not built)", font=f_title, fill=(11, 11, 11))
    d.text((W - 14, 10), "PR #278 · alloy-corrosion/copper", font=f_small, fill=(82, 81, 78), anchor="ra")
    cap = [c for c in story.captions if c[0] <= t + 1e-9]
    if cap:
        text = cap[-1][2]
        d.rectangle([0, H - 46, W, H], fill=(252, 252, 251, 230))
        d.text((14, H - 34), text, font=f_cap, fill=(11, 11, 11))
    d.text((14, 42), "Exact: deck/tool positions (CubOS, Ben 2026-10-02), STEP holder, vial caps, magnet mount, AS568-006 O-ring\n"
           "Schematic: frame, P20 body, camera, tray. Electrode cap: proposal, shown in section", font=f_small, fill=(82, 81, 78))
    m0, m1 = story.measure
    close = m0 + 0.8 <= t <= m1 + 0.1
    if close:
        sim_t = st["sim_t"]
        if sim_t > 1e8:
            sim_t = float(scene.trace_t[-1])
        iw, ih = inset.size
        x0, y0 = W - iw - 16, H - 46 - ih - 12
        im.paste(inset, (x0, y0))
        xp, ytop, ybot = xpix(sim_t)
        d.line([x0 + xp, y0 + ytop, x0 + xp, y0 + ybot], fill=(235, 104, 52, 255), width=2)
        im.paste(cbar, (16, H - 46 - cbar.size[1] - 12))
        mins = sim_t / 60
        phase = "OCP" if mins < 30 else "LPR" if mins < 32 else "rest" if mins < 37 else "+50 mV hold" if mins < 47 else "OCP"
        d.rectangle([14, 92, 380, 150], fill=(252, 252, 251, 215))
        d.text((24, 98), f"t = {mins:4.1f} min   {phase}", font=font(22, True), fill=(11, 11, 11))
        d.text((24, 128), "AS568-006 spot, 150 µL ASW, reference tip 3 mm up", font=f_small, fill=(82, 81, 78))
        # labels in the close-up
        for text, xyz in (("2 mm Ag/AgCl capillary", (S1[0], S1[1], FACE_Z + 8)), ("Pt coil", (S1[0] - 2.6, S1[1] - 0.2, FACE_Z + 3.2)),
                          ("FKM O-ring", (S1[0] + 2.3, S1[1] - 0.5, FACE_Z + 0.9)), ("2.90 mm spot (C71500)", (S1[0] + 0.4, S1[1] - 1.3, FACE_Z + 0.15))):
            x, y = scene.project(xyz)
            if 0 < x < W and 0 < y < H:
                d.text((x + 6, y - 8), text, font=f_lab, fill=(11, 11, 11), stroke_width=3, stroke_fill=(252, 252, 251))
    else:
        if t < 3.4 or t > story.total - 2.8:
            for text, xyz in LABELS:
                x, y = scene.project(xyz)
                if 0 < x < W and 70 < y < H - 50:
                    d.text((x, y), text, font=f_lab, fill=(11, 11, 11), anchor="ms", stroke_width=3, stroke_fill=(252, 252, 251))
    return np.asarray(im)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="", help="comma-separated frame numbers to save as PNG stills, no video")
    args = ap.parse_args()
    story = build_story()
    scene = Scene()
    inset, xpix = make_trace_inset(scene)
    cbar = make_colorbar()
    n = int(math.ceil(story.total * FPS))
    print(f"{story.total:.1f} s, {n} frames", flush=True)
    stills = [int(v) for v in args.frames.split(",") if v.strip()]
    if stills:
        for k in stills:
            t = k / FPS
            st = state_at(story, t)
            scene.set_state(st)
            scene.set_camera(cam_at(story, t))
            img = overlay(scene.frame(), scene, story, t, st, inset, xpix, cbar)
            Image.fromarray(img).save(f"/tmp/cubxl_cu_frame_{k:04d}.png")
            print("still", k, flush=True)
        return
    import imageio.v2 as imageio
    writer = imageio.get_writer(HERE / "cubxl-cu-spot.mp4", fps=FPS, codec="libx264", quality=None,
                                ffmpeg_params=["-crf", "23", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    gif_frames = []
    for k in range(n):
        t = k / FPS
        st = state_at(story, t)
        scene.set_state(st)
        scene.set_camera(cam_at(story, t))
        img = overlay(scene.frame(), scene, story, t, st, inset, xpix, cbar)
        writer.append_data(img)
        for name, ts in (("overview", 2.9), ("fill", story.fill_still), ("closeup", story.measure[1] - 0.5)):
            if k == int(round(ts * FPS)):
                Image.fromarray(img).save(HERE / f"cubxl-cu-{name}.png", optimize=True)
        if k % 3 == 0:
            gif_frames.append(Image.fromarray(img).resize((640, 360), Image.LANCZOS))
        if k % 100 == 0:
            print("frame", k, flush=True)
    writer.close()
    pal = gif_frames[len(gif_frames) // 2].quantize(colors=160, method=Image.Quantize.MEDIANCUT)
    gq = [g.quantize(palette=pal, dither=Image.Dither.NONE) for g in gif_frames]
    gq[0].save(HERE / "cubxl-cu-spot.gif", save_all=True, append_images=gq[1:], duration=100, loop=0, optimize=True)
    # one still per scene for the README
    print("done", flush=True)


if __name__ == "__main__":
    main()
