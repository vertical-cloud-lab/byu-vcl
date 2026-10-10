#!/usr/bin/env python3
"""CalculiX FEA of the cable holder's snap clips: how hard the arms strain when a cable is pushed in.

Both versions of the part are modelled, from their Onshape feature lists:

    rebuild   onshape/features.json          the first version, which the rest of this folder rebuilds
    printed   onshape/features_printed.json  the 17:03 UTC revision that was printed in #256

The profiles come from ../rebuild_from_features.py, so they are the same sketch, regions and fillets.
Each clip is cut down to one arm, half its depth, and the half of the strip above it, with symmetry
on the clip's centre plane and the extrude's mid-plane, and the strip's top face held. The mesh is
the profile in quads, extruded into 20-node hexes (C3D20R). A cable of diameter D pushed through the
opening g spreads each lip by (D - g) / 2, so the narrowest point of the opening is moved outward by
that much, with nonlinear geometry, up to D = the bore.

With the lip's displacement prescribed, the strain field does not depend on Young's modulus, so one
run per clip serves every material: the strain is compared against each material's allowable strain,
and the force scales with E.

    python clip_fea.py     # writes results.json, clip_strain.png and clip_contours.png (needs ccx and gmsh)
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from multiprocessing import get_context
from pathlib import Path

import cadquery as cq
import gmsh
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import rebuild_from_features as R  # noqa: E402

WORK = HERE / "runs"  # meshes and CalculiX output, not committed
E_RUN, NU = 3500.0, 0.35  # MPa; PLA. Strains do not depend on E here, forces scale with it.
H_FINE, H_COARSE = 0.25, 1.0  # mm, element size in the arm and far up the strip (0.15 mm: see MESH_CHECK)

# The printed revision's sketch was redrawn, so its topology is written down here as the rebuild's
# is in rebuild_from_features.py, decoded from the features' queries the same way. Each bore is one
# arc over the top, tangent to the strip, so it is split at its top point into "<id>:a" (start to top)
# and "<id>:b" (top to end), one half per arm.
PRINTED_REGIONS = {
    "Extrude 1": [["aKihO2aJETPw.bottom", "aKihO2aJETPw.left", "aKihO2aJETPw.top", "aKihO2aJETPw.right"]],
    "Extrude 2": [
        ["vtf6jK1B5sUS.trimOffspring", "EO4ysWMsi3hF.2", "RVWZw1uEt7uM", "H7VmPe9f7fec", "29WyK9CfSpQ5:b"],
        ["EO4ysWMsi3hF.1", "EO4ysWMsi3hF.0", "f7HonitPCrIT", "q9G3ImMZdLYd0.MirrorCS", "29WyK9CfSpQ5:a"],
    ],
    "Extrude 3": [
        ["eteE2RSTmiyF.trimOffspring", "Mg7PK0DorgMO.2", "sgU9xQr9ezlC", "Mq8FDruIE0r0", "T1fcGOuyAf3p:b"],
        ["Mg7PK0DorgMO.1", "Mg7PK0DorgMO.0", "wMkQm6umFrAG", "sS4pTWjdfYFf0.MirrorCS", "T1fcGOuyAf3p:a"],
    ],
}
PRINTED_FILLETS = {
    "Fillet 1": [
        ("aKihO2aJETPw.bottom", "aKihO2aJETPw.right"), ("aKihO2aJETPw.top", "aKihO2aJETPw.right"),
        ("aKihO2aJETPw.bottom", "aKihO2aJETPw.left"), ("aKihO2aJETPw.top", "aKihO2aJETPw.left"),
        ("H7VmPe9f7fec", "RVWZw1uEt7uM"), ("q9G3ImMZdLYd0.MirrorCS", "f7HonitPCrIT"),
        ("Mq8FDruIE0r0", "sgU9xQr9ezlC"), ("sS4pTWjdfYFf0.MirrorCS", "wMkQm6umFrAG"),
    ],
}
VERSIONS = {
    "rebuild": ("features.json", R.REGIONS, R.FILLETS),
    "printed": ("features_printed.json", PRINTED_REGIONS, PRINTED_FILLETS),
}
CLIPS = {"large": "Extrude 2", "small": "Extrude 3"}

# Allowable bending strain for a snap fit. Rule-of-thumb design values for moulded parts, cut back
# for FDM printed along the extruded lines: single use, then repeated use at about 60 % of it.
MATERIALS = {  # name: (E in MPa, allowable strain once, repeatedly)
    "PLA": (3500, 0.020, 0.012),
    "PETG": (2000, 0.035, 0.020),
    "Nylon (PA12/PA6, unfilled)": (1500, 0.060, 0.035),
    "TPU 95A": (30, 0.30, 0.20),
}


def split_at_top(curves: dict, eid: str) -> None:
    """Replace the arc eid, which passes over its circle's top, with its two halves eid:a and eid:b."""
    s = curves.pop(eid)
    top = (s.c[0], s.c[1] + s.r)
    curves[eid + ":a"] = R.Seg("arc", s.p0, top, s.c, s.r, s.ccw)
    curves[eid + ":b"] = R.Seg("arc", top, s.p1, s.c, s.r, s.ccw)


def profiles(version: str) -> dict:
    """The version's 2D faces on the Front plane: {feature: {"depth", "faces", "bore", "centre"}}."""
    fname, regions, fillets = VERSIONS[version]
    doc = json.loads((HERE.parent / "onshape" / fname).read_text())
    assert {v["featureStatus"] for v in doc["featureStates"].values()} == {"OK"}
    feats = {f["name"]: f for f in doc["features"]}
    curves = R.sketch_curves(feats["Sketch 1"])
    for name, regs in regions.items():
        text = R.query_text(feats[name], "entities")
        for ent in sum(regs, []):
            assert ent.split(".")[0].split(":")[0] in text, (version, name, ent)
            if ent.endswith(":a") and ent[:-2] in curves:
                split_at_top(curves, ent[:-2])
    corners = {}
    for name, pairs in fillets.items():
        text = R.query_text(feats[name], "entities")
        assert text.count("SWEPT_EDGE") == len(pairs), (version, name)
        for a, b in pairs:
            v = next(p for p in (curves[a].p0, curves[a].p1) if R.close(p, curves[b].p0) or R.close(p, curves[b].p1))
            corners[v] = R.param(feats[name], "radius")
    out = {}
    for name, regs in regions.items():
        faces = [R.face(R.fillet(R.loop(curves, names), corners)) for names in regs]
        bores = [curves[n] for n in sum(regs, []) if curves[n].kind == "arc" and abs(curves[n].c[1] + curves[n].r + 5) < 1e-3]
        out[name] = {"depth": R.param(feats[name], "depth"), "faces": faces,
                     "bore": 2 * bores[0].r if bores else None, "centre": bores[0].c if bores else None}
    return out


def whole_part_volume(version: str, prof: dict) -> float:
    solids = [R.extrude_symmetric(f, p["depth"]) for p in prof.values() for f in p["faces"]]
    return solids[0].fuse(*solids[1:]).clean().Volume()


# --- one half-clip ----------------------------------------------------------------------------------

def opening(faces: list, centre) -> tuple[float, tuple]:
    """Narrowest gap between the two arms below the bore's centre, and the point on the first arm
    (the one the model keeps) where it occurs."""
    below = cq.Solid.makeBox(100, 100, 100, cq.Vector(-50, -50, centre[1] - 100))
    a, b = (f.intersect(below) for f in faces)
    d = R.BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    p = d.PointOnShape1(1)
    return d.Value(), (p.X(), p.Z())


def mesh_half_clip(arm: cq.Face, centre, half_depth: float, layers: int, tag: str) -> tuple[Path, float]:
    """Arm plus the strip above it, out to the part's end, extruded half the clip's depth. Returns the
    Abaqus-format mesh and the side the arm is on (-1 left of the clip's centre, +1 right)."""
    side = -1.0 if arm.Center().x < centre[0] else 1.0
    x0, x1 = sorted((centre[0], centre[0] + side * 12.5))
    strip = cq.Face.makeFromWires(cq.Wire.makePolygon(
        [cq.Vector(x0, 0, -5), cq.Vector(x1, 0, -5), cq.Vector(x1, 0, 5), cq.Vector(x0, 0, 5)], close=True))
    region = arm.fuse(strip).clean()
    assert len(region.Faces()) == 1, len(region.Faces())
    brep, inp = WORK / f"{tag}.brep", WORK / f"{tag}_mesh.inp"
    if inp.exists():  # meshed by an earlier run
        return inp, side
    region.Faces()[0].exportBrep(str(brep))

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add(tag)
    surf = gmsh.model.occ.importShapes(str(brep))
    gmsh.model.occ.synchronize()
    ext = gmsh.model.occ.extrude(surf, 0, half_depth, 0, numElements=[layers], recombine=True)
    gmsh.model.occ.synchronize()
    gmsh.model.addPhysicalGroup(3, [t for d, t in ext if d == 3], name="PART")
    box = gmsh.model.mesh.field.add("Box")
    for k, v in {"VIn": H_FINE, "VOut": H_COARSE, "XMin": -100, "XMax": 100, "YMin": -100, "YMax": 100,
                 "ZMin": -100, "ZMax": -3.0, "Thickness": 4.0}.items():
        gmsh.model.mesh.field.setNumber(box, k, v)
    gmsh.model.mesh.field.setAsBackgroundMesh(box)
    for k, v in {"Mesh.MeshSizeExtendFromBoundary": 0, "Mesh.MeshSizeFromPoints": 0, "Mesh.MeshSizeFromCurvature": 0,
                 "Mesh.Algorithm": 8, "Mesh.RecombineAll": 1, "Mesh.RecombinationAlgorithm": 1,
                 "Mesh.SecondOrderIncomplete": 1, "Mesh.ElementOrder": 2}.items():
        gmsh.option.setNumber(k, v)
    gmsh.model.mesh.generate(3)
    gmsh.write(str(inp))
    gmsh.finalize()
    text = inp.read_text().replace("type=C3D20,", "type=C3D20R,").replace("type=C3D15,", "type=C3D15,")
    inp.write_text(text)
    return inp, side


def read_inp_nodes(inp: Path) -> tuple[np.ndarray, np.ndarray]:
    ids, xyz, on = [], [], False
    for line in inp.read_text().splitlines():
        if line.startswith("*"):
            on = line.upper().startswith("*NODE")
            continue
        if on and line.strip():
            v = line.split(",")
            ids.append(int(v[0]))
            xyz.append([float(c) for c in v[1:4]])
    return np.array(ids), np.array(xyz)


def read_inp_elements(inp: Path) -> list[list[int]]:
    els, cur, on = [], [], False
    for line in inp.read_text().splitlines():
        if line.startswith("*"):
            on = line.upper().startswith("*ELEMENT")
            continue
        if on and line.strip():
            v = [int(c) for c in line.replace(",", " ").split()]
            cur += v
            if not line.rstrip().endswith(","):
                els.append(cur[1:])
                cur = []
    return els


def nset(name: str, ids) -> str:
    ids = list(map(int, ids))
    rows = [", ".join(map(str, ids[i:i + 12])) for i in range(0, len(ids), 12)]
    return f"*NSET, NSET={name}\n" + "\n".join(rows) + "\n"


def run_clip(version: str, clip: str, prof: dict) -> dict:
    p = prof[CLIPS[clip]]
    gap, lip = opening(p["faces"], p["centre"])
    arm = p["faces"][0]
    half_depth = p["depth"] / 2
    layers = max(2, round(half_depth / 0.9))
    tag = f"{version}_{clip}"
    inp, side = mesh_half_clip(arm, p["centre"], half_depth, layers, tag)
    ids, xyz = read_inp_nodes(inp)
    x, y, z = xyz.T
    tol = 1e-4
    fix = ids[np.abs(z - 5) < tol]
    symx = ids[np.abs(x - p["centre"][0]) < tol]
    symy = ids[np.abs(y) < tol]
    d_lip = np.hypot(x - lip[0], z - lip[1])
    lipn = ids[d_lip < d_lip.min() + 1e-6]  # the boundary node nearest the narrowest point, through the depth
    assert len(lipn) >= layers + 1, (tag, len(lipn))
    delta = (p["bore"] - gap) / 2
    (WORK / f"{tag}_sets.inp").write_text(nset("FIX", fix) + nset("SYMX", symx) + nset("SYMY", symy) + nset("LIP", lipn))
    deck = f"""*INCLUDE, INPUT={inp.name}
*INCLUDE, INPUT={tag}_sets.inp
*MATERIAL, NAME=MAT
*ELASTIC
{E_RUN}, {NU}
*SOLID SECTION, ELSET=PART, MATERIAL=MAT
*BOUNDARY
FIX, 1, 3
SYMX, 1, 1
SYMY, 2, 2
*STEP, NLGEOM, INC=1000
*STATIC
0.1, 1.0, 1e-6, 0.1
*BOUNDARY
LIP, 1, 1, {side * delta:.6f}
*NODE FILE
U
*EL FILE
E
*NODE PRINT, NSET=LIP, TOTALS=ONLY
RF
*END STEP
"""
    log, deck_file = WORK / f"{tag}.log", WORK / f"{tag}.inp"
    if not (log.exists() and "Job finished" in log.read_text() and deck_file.read_text() == deck):
        deck_file.write_text(deck)
        r = subprocess.run(["ccx", "-i", tag], cwd=WORK, capture_output=True, text=True)
        log.write_text(r.stdout + r.stderr)
        assert "Job finished" in r.stdout, r.stdout[-2000:]

    frd = parse_frd(WORK / f"{tag}.frd")
    forces = parse_totals(WORK / f"{tag}.dat")
    node_xyz = dict(zip(ids, xyz))
    order = np.array(sorted(frd["coords"]))
    far = np.hypot(np.array([node_xyz[n][0] for n in order]) - lip[0],
                   np.array([node_xyz[n][2] for n in order]) - lip[1]) > 1.0  # skip where the lip is pulled
    curve = []
    for t, inc in sorted(frd["increments"].items()):
        e = inc["E"]
        tens = np.array([[[e[n][0], e[n][3], e[n][5]], [e[n][3], e[n][1], e[n][4]], [e[n][5], e[n][4], e[n][2]]] for n in order])
        ev = np.linalg.eigvalsh(tens)
        i_max = int(np.argmax(np.where(far, ev[:, -1], -np.inf)))
        i_min = int(np.argmin(np.where(far, ev[:, 0], np.inf)))
        f = forces.get(round(t, 6), [np.nan] * 3)
        curve.append({"t": t, "D_mm": gap + 2 * t * delta, "lip_mm": t * delta,
                      "max_tensile_strain": float(ev[i_max, -1]), "at": [round(float(c), 2) for c in node_xyz[order[i_max]][[0, 2]]],
                      "max_compressive_strain": float(ev[i_min, 0]), "at_c": [round(float(c), 2) for c in node_xyz[order[i_min]][[0, 2]]],
                      "force_per_arm_N_PLA": abs(f[0]) * 2})  # x2: the model is half the depth
    last = frd["increments"][max(frd["increments"])]
    return {"version": version, "clip": clip, "bore_mm": round(p["bore"], 3), "depth_mm": p["depth"],
            "opening_mm": round(gap, 3), "opening_pct_of_bore": round(100 * gap / p["bore"], 1),
            "lip_spread_at_bore_mm": round(delta, 3), "nodes": len(ids), "layers": layers,
            "elements": len(read_inp_elements(inp)), "curve": curve,
            "_field": {"ids": order.tolist(), "xyz": [node_xyz[n].tolist() for n in order],
                       "U": [last["U"][n] for n in order], "E1": np.linalg.eigvalsh(np.array(
                           [[[last["E"][n][0], last["E"][n][3], last["E"][n][5]], [last["E"][n][3], last["E"][n][1], last["E"][n][4]],
                             [last["E"][n][5], last["E"][n][4], last["E"][n][2]]] for n in order]))[:, -1].tolist(),
                       "elements": read_inp_elements(inp), "lip": lip, "side": side}}


# --- reading CalculiX output ------------------------------------------------------------------------

def parse_frd(path: Path) -> dict:
    """Node coordinates and, per increment, displacements (U) and total strains (E: xx yy zz xy yz zx)."""
    coords, incs, block, t, cur = {}, {}, None, None, None
    for line in path.read_text().splitlines():
        if line.startswith("    2C"):
            block = "coords"
        elif line.startswith("  100C"):
            t = float(line[12:24])
            incs.setdefault(round(t, 6), {})
        elif line.startswith(" -4"):
            name = line.split()[1]
            block = {"DISP": "U", "TOSTRAIN": "E"}.get(name)
            if block:
                cur = incs[round(t, 6)].setdefault(block, {})
        elif line.startswith(" -3"):
            block = None
        elif line.startswith(" -1") and block:
            n = int(line[3:13])
            vals = [float(line[13 + 12 * i:25 + 12 * i]) for i in range((len(line) - 13) // 12)]
            if block == "coords":
                coords[n] = vals[:3]
            else:
                cur[n] = vals
    return {"coords": coords, "increments": {k: v for k, v in incs.items() if "E" in v}}


def parse_totals(path: Path) -> dict:
    out, t = {}, None
    lines = path.read_text().splitlines()
    for i, line in enumerate(lines):
        m = re.search(r"total force \(fx,fy,fz\) for set LIP and time\s+(\S+)", line)
        if m:
            t = round(float(m.group(1)), 6)
            nums = next(l for l in lines[i + 1:] if l.strip())
            out[t] = [float(v) for v in nums.split()]
    return out


def run_case(version: str, clip: str) -> dict:
    return run_clip(version, clip, profiles(version))


# The printed large clip run once at 0.15 mm in the arm and 0.05 increments (48,257 nodes, 11 min),
# against 0.25 mm and 0.1 increments in the runs above: peak tensile strain at D = bore, and the force.
MESH_CHECK = {"printed large, 0.15 mm mesh": {"max_tensile_strain": 0.02310, "at": [-15.98, -6.03],
                                             "max_compressive_strain": -0.03142, "force_per_arm_N_PLA": 8.03}}


def main() -> dict:
    WORK.mkdir(exist_ok=True)
    results = {"model": {"E_MPa_in_run": E_RUN, "poisson": NU, "element": "C3D20R (C3D15 where a quad would not form)",
                         "mesh_mm": {"arm": H_FINE, "strip": H_COARSE}, "nlgeom": True,
                         "boundary": "strip top face held; symmetry on the clip's centre plane and the extrude's mid-plane; "
                                     "the narrowest point of the opening moved outward by (D - opening)/2 through the depth"},
               "materials": {k: {"E_MPa": v[0], "allowable_once": v[1], "allowable_repeated": v[2]} for k, v in MATERIALS.items()},
               "versions": {}, "clips": []}
    for version in VERSIONS:
        results["versions"][version] = {"part_volume_mm3": round(whole_part_volume(version, profiles(version)), 2)}
    with get_context("spawn").Pool(4) as pool:  # one ccx per core; fork deadlocks once OCC has started threads
        runs = pool.starmap(run_case, [(v, c) for v in VERSIONS for c in CLIPS])
    results["mesh_check"] = MESH_CHECK
    fields = {}
    for res in runs:
        fields[(res["version"], res["clip"])] = res.pop("_field")
        results["clips"].append(res)
        end = res["curve"][-1]
        print(f"{res['version']:8s} {res['clip']:5s} bore {res['bore_mm']:.2f} opening {res['opening_mm']:.2f} "
              f"strain at D=bore {100 * end['max_tensile_strain']:.2f}% (at {end['at']}), "
              f"{100 * end['max_compressive_strain']:.2f}% (at {end['at_c']}), force/arm (PLA) {end['force_per_arm_N_PLA']:.1f} N")
    (HERE / "results.json").write_text(json.dumps(results, indent=1) + "\n")
    import plots
    plots.strain_curves(results, HERE / "clip_strain.png")
    plots.contours(results, fields, HERE / "clip_contours.png")
    return results


if __name__ == "__main__":
    main()
