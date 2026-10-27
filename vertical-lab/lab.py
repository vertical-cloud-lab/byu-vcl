"""Every model in the scene, tessellated once and cached: the VLM and the equipment on its trays.

Each entry of ``meshes()`` is one actor: {"mesh", "color", "opacity", "specular", "group"}.
Parts of one piece of equipment that share a material are merged into one mesh, so the
scene has a few dozen actors rather than a few hundred.

Where each model comes from:

* Kardex Shuttle XP 500: ``vlm.py``, built here from Kardex's and #53's figures (no vendor CAD exists).
* Opentrons OT-2 and AgileX PiPER: the vendors' own STEP files, fetched and hash-checked by
  ``lab_models/vendor.py`` (Opentrons' reference model; AgileX's arm-plus-gripper STEP).
* Powder doser: the lab's own assembly, ``full_assembly.glb`` from powder-doser's
  ``cad/full-assembly`` (Fusion 360 parts and datasheet-based purchased parts), fetched at a pinned commit.
* A&D HR-100A balance with the AutoTrickler V4 panel, Bambu Lab H2D and A1 mini, CubXL:
  the lab's CadQuery models from #199 (``lab_models/``), built from vendor drawings and specs.
* AMAZEMET rePowder atomizer, beside the VLM: the CadQuery model behind the rePowder training
  animations (#124, ``atomizer-training/viz3d/model.py``), copied to ``repowder/model.py``.
"""
from __future__ import annotations

import hashlib
import io
import pickle
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
CACHE = HERE / ".cache"

import common as LM      # noqa: E402
import vlm               # noqa: E402

DOSER = dict(
    url="https://raw.githubusercontent.com/vertical-cloud-lab/powder-doser/"
        "{sha}/cad/full-assembly/assembly/full_assembly.glb",
    sha="a3bb2a92ee78b09cfdc63ce837d1d05ddf46a5da",      # powder-doser PR #170 (#165), 2026-10-02
    sha256="954e0988a088186d392e6d71860c3483911e7ce2c5b21126bee594074d8dbc63",
)

MATS = dict(LM.MATERIALS)
MATS.update(vlm.MATERIALS)
MATS["led_off"] = (0.30, 0.32, 0.30, 1.0, 0.5)


def _hash_sources() -> str:
    h = hashlib.sha256()
    for f in sorted([HERE / "vlm.py", HERE / "lab.py", *(HERE / "lab_models").glob("*.py"),
                     *(HERE / "repowder").glob("*.py")]):
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def to_mesh(shape, tol: float) -> pv.PolyData:
    verts, tris = shape.tessellate(tol, 0.3)
    if not tris:
        return pv.PolyData()
    pts = np.array([(v.x, v.y, v.z) for v in verts], float)
    faces = np.hstack([[3, *t] for t in tris])
    return pv.PolyData(pts, faces)


def _merge(meshes: list[pv.PolyData]) -> pv.PolyData:
    meshes = [m for m in meshes if m.n_points]
    if not meshes:
        return pv.PolyData()
    out = meshes[0].merge(meshes[1:]) if len(meshes) > 1 else meshes[0]
    return out.clean(tolerance=1e-6)


def _entry(mesh, mat, group, **kw):
    r, g, b, a, spec = MATS[mat]
    e = dict(mesh=mesh, color=(r, g, b), opacity=a, specular=spec, group=group, material=mat)
    e.update(kw)
    return e


def _model_entries(model, group: str, tol: float) -> dict:
    """A lab_models Model -> one merged mesh per material."""
    by_mat: dict[str, list] = {}
    for p in model.parts:
        by_mat.setdefault(p.material, []).append(to_mesh(p.shape, tol))
    return {f"{group}:{mat}": _entry(_merge(ms), mat, group) for mat, ms in by_mat.items()}


def _glb_entries(path: Path, group: str) -> dict:
    """The doser's GLB: trimesh scene -> one mesh per base colour, in mm, z up."""
    import trimesh
    sc = trimesh.load(str(path))
    by_col: dict[tuple, list] = {}
    for node in sc.graph.nodes_geometry:
        tf, gname = sc.graph[node]
        g = sc.geometry[gname].copy()
        g.apply_transform(tf)
        col = (0.7, 0.7, 0.7)
        try:
            c = g.visual.material.baseColorFactor
            col = tuple(round(float(x) / (255.0 if max(c[:3]) > 1 else 1.0), 2) for x in c[:3])
        except Exception:
            try:
                c = g.visual.face_colors[0]
                col = tuple(round(float(x) / 255.0, 2) for x in c[:3])
            except Exception:
                pass
        faces = np.hstack([np.full((len(g.faces), 1), 3), g.faces]).ravel()
        by_col.setdefault(col, []).append(pv.PolyData(np.asarray(g.vertices, float), faces))
    out = {}
    for i, (col, ms) in enumerate(sorted(by_col.items())):
        out[f"{group}:c{i}"] = dict(mesh=_merge(ms), color=col, opacity=1.0, specular=0.3, group=group,
                                    material="glb")
    return out


def fetch_doser() -> Path:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / "powder_doser_full_assembly.glb"
    if not path.exists():
        url = DOSER["url"].format(sha=DOSER["sha"])
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        path.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    if DOSER["sha256"]:
        d = hashlib.sha256(path.read_bytes()).hexdigest()
        if d != DOSER["sha256"]:
            print(f"warning: {path.name} has sha256 {d}, built against {DOSER['sha256']}")
    return path


# ------------------------------------------------------------------------------------------ build
def _vlm_entries() -> dict:
    out = {}
    for name, (shape, mat, group) in vlm.all_parts().items():
        if isinstance(shape, LM.cq.Workplane):
            shape = shape.val() if len(shape.vals()) == 1 else LM.cq.Compound.makeCompound(shape.vals())
        tol = 0.5 if "lamp" in name or "console" in name else 2.0
        out[name] = _entry(to_mesh(shape, tol), mat, group)
    return out


def _equipment() -> dict:
    """{key: (entries, bbox (xmin, xmax, ymin, ymax, zmin, zmax))} for every equipment model, each in its own frame."""
    import equipment
    import labware
    import vendor
    eq = {}

    def add(key, entries):
        pts = np.vstack([e["mesh"].points for e in entries.values() if e["mesh"].n_points])
        lo, hi = pts.min(0), pts.max(0)
        eq[key] = (entries, (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
        print(f"  {key}: {len(entries)} meshes, {sum(e['mesh'].n_cells for e in entries.values())} tris, "
              f"bbox {np.round(hi - lo, 1)}", flush=True)

    add("ot2", _model_entries(vendor.ot2(), "eq_ot2", 0.6))
    add("cubxl", _model_entries(equipment.cubxl(), "eq_cubxl", 0.6))
    add("h2d", _model_entries(equipment.h2d(), "eq_h2d", 0.6))
    add("a1mini", _model_entries(equipment.a1_mini(), "eq_a1mini", 0.4))
    add("balance", _model_entries(labware.balance("autotrickler"), "eq_balance", 0.3))
    add("doser", _glb_entries(fetch_doser(), "eq_doser"))
    add("piper", _model_entries(vendor.piper(), "eq_piper", 0.4))
    return eq


def _repowder() -> dict:
    """The rePowder and its utilities, one mesh per colour, in the model's own frame (front towards -y)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("repowder_model", HERE / "repowder" / "model.py")
    rp = importlib.util.module_from_spec(spec)
    sys.modules["repowder_model"] = rp            # its dataclasses look themselves up there
    spec.loader.exec_module(rp)
    by: dict[tuple, list] = {}
    for p in rp.parts():
        if p.name == "floor":                     # the training scene's own floor
            continue
        m = rp.tess(p.shape, max(p.tol, 0.5))
        if m is not None:
            by.setdefault((tuple(round(c, 3) for c in p.color), p.opacity), []).append(m)
    for name, r in rp.pipe_routes().items():
        tube = pv.Spline(np.array(r["pts"], float), 120).tube(radius=r["r"], n_sides=14).triangulate()
        by.setdefault((tuple(round(c, 3) for c in r["color"]), 1.0), []).append(tube)
    out = {}
    for i, ((col, op), ms) in enumerate(sorted(by.items())):
        mesh = pv.merge(ms, merge_points=False) if len(ms) > 1 else ms[0]
        out[f"repowder:c{i}"] = dict(mesh=mesh, color=col, opacity=op, specular=0.3, group="repowder", material="rp")
    return out


def meshes(rebuild: bool = False) -> dict:
    """{"vlm": {name: entry}, "equipment": {key: (entries, bbox)}}, from the cache when the sources are unchanged."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"meshes_{_hash_sources()}.pkl"
    if path.exists() and not rebuild:
        return pickle.loads(path.read_bytes())
    print("tessellating (cached afterwards in", path.name + ")", flush=True)
    data = {"vlm": _vlm_entries(), "equipment": _equipment(), "repowder": _repowder()}
    path.write_bytes(pickle.dumps(data))
    return data


if __name__ == "__main__":
    d = meshes(rebuild="--rebuild" in sys.argv)
    print(len(d["vlm"]), "VLM parts;", ", ".join(d["equipment"]))
