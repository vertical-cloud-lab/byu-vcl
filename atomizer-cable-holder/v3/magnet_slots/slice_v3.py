#!/usr/bin/env python3
"""Slice an Onshape glTF of Atomizer Holder V3 for the A1 mini with Bambu Studio's CLI.

Stock presets as on 2026-10-06 (A1 mini 0.4, 0.20mm Standard @BBL A1M, Bambu PLA Basic, Textured
PEI), standing on the bottom of the hook. Optional process overrides as key=value.

    python slice_v3.py <bambu squashfs-root> <part_studio.gltf> <build dir> [key=value ...]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flatten_presets import PRESETS, flatten  # noqa: E402

bambu, gltf, build = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
overrides = dict(a.split("=", 1) for a in sys.argv[4:])
build.mkdir(parents=True, exist_ok=True)

mesh = trimesh.load(gltf, force="scene").to_geometry()
mesh.apply_scale(1000.0)
mesh.merge_vertices(merge_tex=True, merge_norm=True)
# Onshape -y (the bottom of the hook) becomes -z: (x, y, z) -> (x, -z, y)
mesh.apply_transform(np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float))
mesh.apply_translation(-mesh.bounds[0])
stl = build / "atomizer_holder_v3_print.stl"
mesh.export(stl)
lo, hi = mesh.bounds
print("print bounds mm:", np.round(hi - lo, 3).tolist(), "volume mm3:", round(mesh.volume, 1))

presets = {}
for kind, name in PRESETS.items():
    cfg = flatten(kind, name, bambu / "resources" / "profiles" / "BBL")
    if kind == "filament":
        cfg["filament_colour"] = ["#000000"]
    if kind == "process":
        cfg.update(overrides)
    presets[kind] = build / f"{kind}.json"
    presets[kind].write_text(json.dumps(cfg, indent=2) + "\n")

centre = np.array([90.0, 90.0])
pos = centre - (lo[:2] + hi[:2]) / 2
assemble = build / "assemble.json"
assemble.write_text(json.dumps({"plates": [{"plate_name": "V3", "need_arrange": False, "objects": [
    {"path": str(stl), "count": 1, "filaments": [1], "pos_x": [float(pos[0])], "pos_y": [float(pos[1])], "pos_z": [0]}]}]}))
json.dump({"stl_origin_on_bed": pos.tolist(), "overrides": overrides}, open(build / "placement.json", "w"))

cmd = [str(bambu / "AppRun"), "--debug", "2",
       "--load-settings", f"{presets['machine']};{presets['process']}",
       "--load-filaments", str(presets["filament"]),
       "--load-assemble-list", str(assemble),
       "--curr-bed-type", "Textured PEI Plate",
       "--slice", "0", "--outputdir", str(build), "--export-3mf", "v3.gcode.3mf"]
proc = subprocess.run(cmd, capture_output=True, text=True)
(build / "cli.log").write_text(proc.stdout + proc.stderr)
print("CLI exit:", proc.returncode)
res = json.loads((build / "result.json").read_text())
print("result:", res.get("return_code"), res.get("error_string"),
      [(p["id"], round(p["total_predication"])) for p in res.get("sliced_plates", [])])
