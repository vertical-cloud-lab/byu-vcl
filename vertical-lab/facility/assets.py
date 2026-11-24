"""The facility render's assets: each machine as a few merged meshes in its own frame, drawn many times from one copy.

A whole-lab scene from ``setup_lab.build`` holds about 2,600 actors and peaks at 6.7-7.7 GB, so a facility of dozens
of Shuttles, atomizers and printers can't be built from it machine by machine. Here each kind of machine becomes an
``Asset``: its parts merged by colour into a handful of triangle meshes (normals split at the scene's 35 deg, as
``scene.Scene.add`` does), with a decimated copy for the far rows. ``Library`` gives every mesh one VTK mapper, and
every placed copy (``Placed``) is a set of actors sharing those mappers, so 40 printers cost one printer's memory.

Where the meshes come from:

* **The Shuttle, 35 ft:** ``vlm.py``'s own housing, opening, logo and tray, built with ``vlm.UNIT_H`` set to
  10,700 mm (35 ft 1 in, on Kardex's 100 mm grid). Only the outside is built (the cladding is drawn solid): the
  columns, extractor and drive are hidden behind it.
* **The machines of the pilot cell (PR #318's lab):** baked from ``setup_lab.build`` by ``bake.py``.
* **The MiR250 + UR12e units:** ``props.mir250()`` and the arm and gripper meshes from ``ur_arm.py`` (Universal
  Robots' and Robotiq's own descriptions), one rigid part per link, posed with ``ur_arm.fk``.
* **The gas atomizer:** ``gas_atomizer.py`` (ours, from published sizes; see its docstring).
"""
from __future__ import annotations

import math
import os
import pickle
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pyvista as pv
import vtk

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))
CACHE = HERE / ".cache"
FEATURE_ANGLE = 35.0

SHUTTLE_H_FT = 35
SHUTTLE_H = 10700.0          # mm: 35 ft is 10,668 mm; Kardex builds Shuttle heights on a 100 mm grid (vlm.py)


@dataclass
class Part:
    mesh: pv.PolyData
    color: tuple
    specular: float = 0.2
    ambient: float = 0.22
    role: str = "solid"           # "solid" (merged), or a name the animation drives on its own ("glow", "beacon", ...)
    rigid: str = "body"           # the sub-assembly it moves with (a tray, a shutter, an arm link)


@dataclass
class Asset:
    name: str
    parts: list[Part] = field(default_factory=list)

    def bounds(self):
        b = self.__dict__.get("_bounds")
        if b is None:
            pts = np.vstack([p.mesh.points for p in self.parts if p.mesh.n_points])
            b = self.__dict__["_bounds"] = (pts.min(0), pts.max(0))
        return b

    def n_tris(self) -> int:
        return int(sum(p.mesh.n_cells for p in self.parts))


# ------------------------------------------------------------------------------------------------ mesh helpers
def tri(mesh) -> pv.PolyData:
    """Triangles only, with no data arrays (a transformed or re-triangulated mesh can carry a stale normals array)."""
    m = mesh if isinstance(mesh, pv.PolyData) else mesh.extract_surface(algorithm="dataset_surface")
    m = m.copy(deep=False)
    m.clear_data()
    if not m.is_all_triangles:
        m = m.triangulate()
    return m


def with_normals(mesh: pv.PolyData) -> pv.PolyData:
    """Point normals split at FEATURE_ANGLE, as Scene.add's smooth shading with split_sharp_edges draws them."""
    m = tri(mesh)
    if m.n_cells == 0:
        return m
    m = m.compute_normals(split_vertices=True, feature_angle=FEATURE_ANGLE, auto_orient_normals=False,
                          consistent_normals=False, cell_normals=False)
    return m


def coloured(mesh: pv.PolyData, color) -> pv.PolyData:
    m = with_normals(mesh)
    rgb = np.clip(np.round(np.asarray(color, float)[:3] * 255.0), 0, 255).astype(np.uint8)
    m.point_data["rgb"] = np.tile(rgb, (m.n_points, 1))
    return m


def decimated(mesh: pv.PolyData, keep: float) -> pv.PolyData:
    """A copy with about `keep` of its triangles (quadric decimation, boundaries kept); small meshes as they are."""
    m = tri(mesh)
    if keep >= 0.999 or m.n_cells < 400:
        return m
    try:
        d = m.clean(tolerance=1e-6).decimate(1.0 - keep, volume_preservation=True)
        return d if d.n_cells else m
    except Exception:                                     # noqa: BLE001
        return m


def spec_class(s: float) -> int:
    return 0 if s < 0.25 else (1 if s < 0.5 else 2)


SPEC_OF_CLASS = {0: 0.15, 1: 0.35, 2: 0.6}


def merged(asset: Asset, keep: float = 1.0) -> list[tuple[str, str, pv.PolyData, float, float, tuple | None]]:
    """The asset as drawn: [(rigid, role, mesh, specular, ambient, colour or None)]. Solid parts of one rigid body and
    one specular class are merged into one vertex-coloured mesh; any other role stays a mesh of its own (with its
    colour, which the animation changes)."""
    groups: dict[tuple, list] = {}
    out = []
    for p in asset.parts:
        if not p.mesh.n_points:
            continue
        if p.role == "detail" and keep < 1.0:
            continue                       # thin rails and panel seams: sub-pixel lines that flicker at a distance
        m = decimated(p.mesh, keep) if keep < 1.0 else tri(p.mesh)
        if p.role not in ("solid", "detail"):
            out.append((p.rigid, p.role, with_normals(m), p.specular, p.ambient, tuple(p.color)))
            continue
        key = (p.rigid, spec_class(p.specular), round(p.ambient, 2))
        groups.setdefault(key, []).append(coloured(m, p.color))
    for (rigid, sc_, amb), ms in groups.items():
        mesh = pv.merge(ms, merge_points=False) if len(ms) > 1 else ms[0]
        out.append((rigid, "solid", mesh, SPEC_OF_CLASS[sc_], amb, None))
    return out


# ------------------------------------------------------------------------------------------------ the library
class Library:
    """One mapper per (asset, level of detail, mesh); actors placed from it share the mappers (and their geometry)."""

    LODS = {"near": 1.0, "far": float(os.environ.get("FAC_FAR_KEEP", "0.25"))}

    def __init__(self, renderer):
        self.ren = renderer
        self.assets: dict[str, Asset] = {}
        self.drawn: dict[tuple[str, str], list] = {}      # (asset, lod) -> [(rigid, role, mapper, spec, amb, col)]
        self.tris: dict[tuple[str, str], int] = {}

    def add(self, asset: Asset, lods=("near", "far"), keep: dict | None = None):
        """Draw `asset` at each level of detail: keep[lod] (default LODS) of its triangles."""
        self.assets[asset.name] = asset
        keep = {**self.LODS, **(keep or {})}
        for lod in lods:
            items = []
            n = 0
            for rigid, role, mesh, spec, amb, col in merged(asset, keep[lod]):
                mp = vtk.vtkPolyDataMapper()
                mp.SetInputData(mesh)
                if col is None:
                    mp.SetScalarModeToUsePointFieldData()
                    mp.SelectColorArray("rgb")
                    mp.SetColorModeToDirectScalars()
                    mp.ScalarVisibilityOn()
                else:
                    mp.ScalarVisibilityOff()
                mp.StaticOn()
                items.append((rigid, role, mp, spec, amb, col, mesh))
                n += mesh.n_cells
            self.drawn[(asset.name, lod)] = items
            self.tris[(asset.name, lod)] = n
        return self

    def place(self, asset: str, M=np.eye(4), lod="near", tag=None) -> "Placed":
        return Placed(self, asset, M, lod, tag)


def _prop(spec, amb, col=None) -> vtk.vtkProperty:
    pr = vtk.vtkProperty()
    pr.SetInterpolationToPhong()
    pr.SetAmbient(amb)
    pr.SetDiffuse(0.80 if amb < 0.8 else 0.3)
    s = min(max(float(spec), 0.0), 1.0)
    pr.SetSpecular(0.30 * s * s)
    pr.SetSpecularPower(12.0 + 68.0 * s)
    if col is not None:
        pr.SetColor(*col)
    return pr


def vmat(M: np.ndarray) -> vtk.vtkMatrix4x4:
    vm = vtk.vtkMatrix4x4()
    vm.DeepCopy(np.asarray(M, float).ravel().tolist())
    return vm


class Placed:
    """One copy of an asset in the scene: an actor per mesh of each level of detail, the rigid bodies posed by
    ``pose({rigid: 4x4 in the asset's frame})`` on top of the copy's placement ``M``."""

    _shared_props: dict = {}

    def __init__(self, lib: Library, asset: str, M, lod, tag):
        self.lib, self.asset, self.tag = lib, asset, tag
        self.M = np.asarray(M, float)
        self.local: dict[str, np.ndarray] = {}
        self.actors: dict[str, list] = {}          # lod -> [(rigid, role, actor)]
        self.lod = None
        self.visible = True
        self.roles: dict[str, list] = {}           # role -> [actor] (all lods)
        for lv in ("near", "far"):
            items = lib.drawn.get((asset, lv))
            if not items:
                continue
            acts = []
            for rigid, role, mp, spec, amb, col, _mesh in items:
                a = vtk.vtkActor()
                a.SetMapper(mp)
                if role == "solid":
                    key = (round(spec, 3), round(amb, 3))
                    pr = Placed._shared_props.get(key)
                    if pr is None:
                        pr = Placed._shared_props[key] = _prop(spec, amb)
                    a.SetProperty(pr)
                else:
                    a.SetProperty(_prop(spec, amb, col))
                    self.roles.setdefault(role, []).append(a)
                a.SetVisibility(False)
                lib.ren.AddActor(a)
                acts.append((rigid, role, a))
            self.actors[lv] = acts
        self._mats: dict[str, tuple] = {}
        self.set_lod(lod)
        self.update()

    def set_lod(self, lod):
        if lod not in self.actors:
            lod = "near" if "near" in self.actors else next(iter(self.actors))
        if lod == self.lod:
            return
        self.lod = lod
        for lv, acts in self.actors.items():
            for _r, _ro, a in acts:
                a.SetVisibility(self.visible and lv == lod)

    def show(self, on: bool):
        if on == self.visible:
            return
        self.visible = on
        for lv, acts in self.actors.items():
            for _r, _ro, a in acts:
                a.SetVisibility(on and lv == self.lod)

    def pose(self, local: dict):
        self.local.update(local)

    def update(self):
        """Every rigid body's world matrix onto its actors, only where it changed."""
        for lv, acts in self.actors.items():
            for rigid, _ro, a in acts:
                L = self.local.get(rigid)
                W = self.M if L is None else self.M @ L
                key = W.tobytes()
                prev = self._mats.get((lv, rigid, id(a)))
                if prev is not None and prev == key:
                    continue
                a.SetUserMatrix(vmat(W))
                self._mats[(lv, rigid, id(a))] = key

    def colour(self, role: str, col, ambient=None):
        for a in self.roles.get(role, []):
            pr = a.GetProperty()
            pr.SetColor(*col)
            if ambient is not None:
                pr.SetAmbient(ambient)

    def centre(self) -> np.ndarray:
        lo, hi = self.lib.assets[self.asset].bounds()
        c = (lo + hi) / 2
        return (self.M @ np.array([c[0], c[1], c[2], 1.0]))[:3]


# ------------------------------------------------------------------------------------------------ the 35 ft Shuttle
def _cq_parts(fn) -> dict:
    import lab
    import common as LM
    out = {}
    for name, (shape, mat, group) in fn().items():
        if isinstance(shape, LM.cq.Workplane):
            shape = shape.val() if len(shape.vals()) == 1 else LM.cq.Compound.makeCompound(shape.vals())
        tol = 0.5 if ("lamp" in name or "console" in name) else 2.0
        out[name] = (lab.to_mesh(shape, tol), mat, group)
    return out


def shuttle35() -> Asset:
    """Kardex Shuttle XP 500, 2450 x 864 mm trays, built 10,700 mm tall from vlm.py's own parts (cladding solid).
    Rigid bodies: "body", "shutter" (slides up to open), "tray" (the presented tray, with a load drawn on it by the
    animation's tray assets) and the "led" strips (role "led"), "lamp" (role "beacon": the status beacon on the roof)."""
    path = CACHE / f"shuttle35_{int(SHUTTLE_H)}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    import lab
    import vlm as V
    h0 = V.UNIT_H
    V.UNIT_H = SHUTTLE_H
    try:
        parts = {}
        parts.update(_cq_parts(V.housing))
        parts.update(_cq_parts(V.opening))
    finally:
        V.UNIT_H = h0
    a = Asset("shuttle35")
    mats = dict(lab.MATS)
    for name, (mesh, mat, group) in parts.items():
        if group in ("posts",) or "levelling" in name or name == "base frame":
            continue                     # inside the cladding (the frame shows through nowhere with solid panels)
        r, g, b, op, spec = mats["vlm_skin_solid"] if mat == "vlm_skin" else mats[mat]
        if mat == "vlm_seam":
            r, g, b = 0.66, 0.69, 0.68
        rigid = "shutter" if group == "shutter" else "body"
        role = "led" if mat == "vlm_led" else ("detail" if mat == "vlm_seam" else "solid")
        amb = 0.85 if mat == "vlm_led" else (0.30 if mat in ("vlm_skin", "vlm_seam") else 0.22)
        a.parts.append(Part(mesh, (r, g, b), spec, amb, role, rigid))
    for text, (x, y, z, hh) in V.logo().items():
        t = pv.Text3D(text, depth=0.12)
        bb = t.bounds
        t = t.translate((-bb[0], -bb[2], -bb[4]), inplace=False).scale(hh / (bb[3] - bb[2]), inplace=False)
        t = t.rotate_x(90, inplace=False).translate((x, y, z), inplace=False)
        r, g, b, _op, spec = mats["vlm_logo"]
        a.parts.append(Part(t.triangulate(), (r, g, b), spec))
    # the status beacon on the roof's front edge (ours, as the finale draws one over each Shuttle)
    top = SHUTTLE_H + V.SKIN
    pole = pv.Cylinder(center=(V.UNIT_W / 2 - 250, -V.UNIT_D / 2 + 150, top + 150), direction=(0, 0, 1), radius=22,
                       height=300, resolution=16)
    lens = pv.Cylinder(center=(V.UNIT_W / 2 - 250, -V.UNIT_D / 2 + 150, top + 400), direction=(0, 0, 1), radius=110,
                       height=200, resolution=28)
    a.parts.append(Part(pole, (0.25, 0.26, 0.28), 0.3))
    a.parts.append(Part(lens, (0.62, 0.64, 0.67), 0.0, 0.9, "beacon"))
    # the presented tray: vlm.tray's pan, its socket and strip (the load is a separate asset placed with it)
    tp = _cq_parts(lambda: V.tray("X"))
    for name, (mesh, mat, group) in tp.items():
        r, g, b, op, spec = mats[mat]
        a.parts.append(Part(mesh, (r, g, b), spec, 0.22, "solid", "tray"))
    CACHE.mkdir(exist_ok=True)
    path.write_bytes(pickle.dumps(a))
    return a


def shuttle_dims() -> dict:
    import vlm as V
    return dict(W=V.UNIT_W + 2 * V.SKIN, D=V.UNIT_D + 2 * V.SKIN, H=SHUTTLE_H + V.SKIN, y_front=-V.UNIT_D / 2 - V.SKIN,
                y_open=V.Y_OPEN, z_open=V.Z_OPEN, z_sill=V.Z_SILL, tray_d=V.TRAY_D, tray_w=V.TRAY_W,
                y_shutter=V.Y_SHUTTER, open_top=V.Z_OPEN_TOP, unit_w=V.UNIT_W, unit_d=V.UNIT_D)


# ------------------------------------------------------------------------------------------------ the units
UNIT_RIGIDS = ("mir", "arm_base", "shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3")


def unit_asset(keep_arm: float = 1.0) -> Asset:
    """A MiR250 + UR10e (UR12e) unit as setup_lab.Unit draws it: the MiR250 and its cabinet (with the Class D unit and
    the three base cameras), the UR control box, the arm's links and the gripper (folded into wrist3: drawn closed)."""
    import props as P
    import ur_arm
    import animate as A
    a = Asset("unit")
    for nm, (mesh, col) in P.mir250().items():
        role = "band" if "light band" in nm else "solid"
        amb = 0.8 if "light" in nm else 0.22
        a.parts.append(Part(tri(mesh), tuple(col), 0.3, amb, role, "mir"))
    H0 = P.MIR["H"]
    a.parts.append(Part(pv.Box(bounds=(-230, 230, -127, 127, H0 + 5, H0 + 5 + 449)).triangulate(), (0.60, 0.62, 0.64),
                        0.3, 0.22, "solid", "mir"))
    holder, _seat = P.buffer_holder()
    a.parts.append(Part(tri(holder.translate((*A.BUFFER_LOCAL, P.AMR_TOP - 20), inplace=False)), P.RACK_C, 0.3, 0.22,
                        "solid", "mir"))
    for link, lst in ur_arm.arm_meshes(A.ROBOT).items():
        for mesh, col, spec in lst:
            m = decimated(tri(mesh), keep_arm) if keep_arm < 1.0 else tri(mesh)
            a.parts.append(Part(m, tuple(col), spec, 0.22, "solid", "arm_base" if link == "base" else link))
    gfk = ur_arm.gripper_fk(0.0)
    for part, lst in ur_arm.gripper_meshes().items():
        for mesh, col, spec in lst:
            m = tri(mesh).transform(gfk[part], inplace=False)
            a.parts.append(Part(m, tuple(col), spec, 0.22, "solid", "wrist3"))
    return a


def unit_local(q, grip_close: float = 0.0) -> dict:
    """{rigid: 4x4} in the unit's frame for joint angles q (rad): the arm stands on the cabinet's plate."""
    import props as P
    import ur_arm
    import animate as A
    from scene import T
    base = T((*A.ARM_LOCAL, P.AMR_TOP))
    fk = ur_arm.fk(A.ROBOT, q)
    out = {"mir": np.eye(4), "arm_base": base @ fk["base"]}
    for link in ("shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3"):
        out[link] = base @ fk[link]
    return out


def arm_base_world(unit_M: np.ndarray) -> np.ndarray:
    import props as P
    import animate as A
    from scene import T
    return unit_M @ T((*A.ARM_LOCAL, P.AMR_TOP))
