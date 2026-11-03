"""Every model in the scene, tessellated once and cached: the VLM, the equipment on its trays and the atomizer.

Each entry of ``meshes()`` is one actor: {"mesh", "color", "opacity", "specular", "group"}.
Parts of one piece of equipment that share a material are merged into one mesh, so the
scene has a few dozen actors rather than a few hundred.

Where each model comes from:

* Kardex Shuttle XP 500: ``vlm.py``, built here from Kardex's figures and #53's (no vendor CAD exists).
* Opentrons OT-2: Opentrons' own reference STEP, fetched and hash-checked by ``lab_models/vendor.py``.
* Bambu Lab H2D and A1 mini, CubXL, Aconity MIDI: the lab's CadQuery models from #199 (``lab_models/``), built
  from vendor drawings, specs and photos. The CubXL comes in four pieces (frame, gantry, carriage, tools) so it can
  move, with its control box moved onto a shelf behind the frame so three fit side by side on one tray.
* Bambu Lab A2L: ``a2l.py``, built here the same way from Bambu's published envelope and build volume.
* AMAZEMET rePowder atomizer, beside the VLM: the CadQuery model behind the rePowder training
  animations (#124, ``atomizer-training/viz3d/model.py``), copied to ``repowder/model.py``.

Built elsewhere, with their own caches: the multi-doser (``carousel.py``, powder-doser PR #185's own CAD and
kinematics), the UR10e and its Robotiq 2F-85 (``ur_arm.py``, the makers' ROS 2 descriptions), and the vials,
rack and MiR250 base (``props.py``).
"""
from __future__ import annotations

import hashlib
import pickle
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
CACHE = HERE / ".cache"

import common as LM      # noqa: E402
import vlm               # noqa: E402

# the CubXL's moving parts (lab_models/equipment.py names); "frame" is everything else. Its rack's sixth vial is left
# out: that seat takes the vial the arm brings from the multi-doser
CUBXL_PIECES = {"frame": None,
                "gantry": ("gantry upright L", "gantry upright R", "gantry beam", "cable chain"),
                "carriage": ("z carriage", "tool plate", "controller"),
                "tools": ("pipette", "capper")}
CUBXL_FREE_SLOT = ("vial 6", "vial 6 cap")
# the CubXL's control box (and its e-stop) stands 300 mm out to the left of the frame in the lab (#199's model). Three
# of them side by side on one tray only fit with the box behind the frame instead: on a shelf on four legs, 50 mm up,
# clear of the tray's power strip. A layout choice for the tray, not how the lab's one is set up
CUBXL_BEHIND = ("control box", "e-stop")
CUBXL_BOX_MOVE = (370.0, 577.0, 50.0)
EQ_VERSION = "r3-1"      # bump when an equipment builder in this file changes (the caches are keyed on it)

MATS = dict(LM.MATERIALS)
MATS.update(vlm.MATERIALS)
MATS["led_off"] = (0.30, 0.32, 0.30, 1.0, 0.5)


def _hash_sources(*files) -> str:
    h = hashlib.sha256()
    for f in sorted(files):
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


# ------------------------------------------------------------------------------------------ build
def _vlm_entries() -> dict:
    out = {}
    for name, (shape, mat, group) in vlm.all_parts().items():
        if isinstance(shape, LM.cq.Workplane):
            shape = shape.val() if len(shape.vals()) == 1 else LM.cq.Compound.makeCompound(shape.vals())
        tol = 0.5 if "lamp" in name or "console" in name else 2.0
        out[name] = _entry(to_mesh(shape, tol), mat, group)
    # the header's lettering, as on Kardex's renders
    for text, (x, y, z, h) in vlm.logo().items():
        t = pv.Text3D(text, depth=0.12)
        b = t.bounds
        t = t.translate((-b[0], -b[2], -b[4]), inplace=False).scale(h / (b[3] - b[2]), inplace=False)
        t = t.rotate_x(90, inplace=False).translate((x, y, z), inplace=False)
        out[f"logo {text}"] = _entry(t.triangulate(), "vlm_logo", "bay")
    return out


def _bbox_entry(entries) -> tuple:
    pts = np.vstack([e["mesh"].points for e in entries.values() if e["mesh"].n_points])
    lo, hi = pts.min(0), pts.max(0)
    return entries, (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])


def _report(key, entries, bb):
    size = np.array([bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4]])
    print(f"  {key}: {len(entries)} meshes, {sum(e['mesh'].n_cells for e in entries.values())} tris, "
          f"bbox {np.round(size, 1)}", flush=True)


def _cubxl_pieces() -> dict:
    """The CubXL in four pieces so its gantry can move: the frame, the gantry (y), the carriage (x), the tools (z)."""
    import equipment
    cub = equipment.cubxl(0.5, 0.5, 0.5)
    move = LM.cq.Location(LM.cq.Vector(*CUBXL_BOX_MOVE))
    for p in cub.parts:
        if p.name in CUBXL_BEHIND:
            p.shape = p.shape.moved(move)
    # the shelf the control box stands on: a plate on four legs (x -300..-40, y 304.5..504.5 once moved)
    cub.add("control box shelf", LM.box(-305, 300, 44, -35, 505, 50), "aluminium")
    for x in (-290.0, -50.0):
        for y in (312.0, 440.0):
            cub.add(f"shelf leg {x:.0f} {y:.0f}", LM.cyl(12, 44, x=x, y=y), "aluminium")
    out = {}
    for piece, names in CUBXL_PIECES.items():
        sub = LM.Model(cub.key, cub.title)
        for p in cub.parts:
            if (p.name in names) if names else not any(p.name in v for v in CUBXL_PIECES.values() if v) \
                    and p.name not in CUBXL_FREE_SLOT:
                sub.parts.append(p)
        out[f"cubxl_{piece}"] = _bbox_entry(_model_entries(sub, f"eq_cubxl_{piece}", 0.6))
    return out


def _equipment_builders() -> dict:
    """{key: (build() -> {name: (entries, bbox)}, source files)}: each cached on its own sources."""
    import equipment
    import vendor
    import a2l
    lmd = HERE / "lab_models"
    lm = [lmd / "common.py", lmd / "equipment.py"]

    def one(name, model, tol):
        return lambda: {name: _bbox_entry(_model_entries(model(), f"eq_{name}", tol))}
    return {
        "ot2": (one("ot2", vendor.ot2, 0.6), [lmd / "common.py", lmd / "vendor.py"]),
        "cubxl": (_cubxl_pieces, lm),
        "h2d": (one("h2d", equipment.h2d, 0.6), lm),
        "a1mini": (one("a1mini", equipment.a1_mini, 0.4), lm),
        "a2l": (one("a2l", a2l.a2l, 0.5), [lmd / "common.py", HERE / "a2l.py"]),
        "aconity": (one("aconity", equipment.aconity_midi, 1.0), lm),
    }


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


def _cached(key, build, srcs, rebuild=False):
    path = CACHE / f"{key}_{_hash_sources(*srcs)}_{EQ_VERSION}.pkl"
    if path.exists() and not rebuild:
        return pickle.loads(path.read_bytes())
    print(f"tessellating {key} (cached afterwards in {path.name})", flush=True)
    data = build()
    path.write_bytes(pickle.dumps(data))
    return data


def meshes(rebuild: bool = False) -> dict:
    """{"vlm": {name: entry}, "equipment": {key: (entries, bbox)}, "repowder": {...}}. Each model is cached on its own
    sources, so changing the VLM doesn't re-tessellate the vendor CAD."""
    CACHE.mkdir(exist_ok=True)
    lmd = HERE / "lab_models"
    data = {"vlm": _cached("vlm", _vlm_entries, [HERE / "vlm.py", lmd / "common.py"], rebuild),
            "repowder": _cached("repowder", _repowder, [*(HERE / "repowder").glob("*.py")], rebuild),
            "equipment": {}}
    for key, (build, srcs) in _equipment_builders().items():
        part = _cached(f"eq_{key}", build, srcs, rebuild)
        for name, (entries, bb) in part.items():
            _report(name, entries, bb)
        data["equipment"].update(part)
    return data


if __name__ == "__main__":
    d = meshes(rebuild="--rebuild" in sys.argv)
    print(len(d["vlm"]), "VLM parts;", ", ".join(d["equipment"]))
