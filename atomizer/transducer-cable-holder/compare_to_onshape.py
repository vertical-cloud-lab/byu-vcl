#!/usr/bin/env python3
"""Compare the rebuilt STL with Onshape's own tessellation of the part (onshape/part_studio.gltf).

The glTF came from the Part Studio's glTF export once the link allowed export. Onshape writes
it in metres, in the Part Studio's own frame, so it needs scaling only. Each mesh is sampled
evenly and the distance from every sample to the other surface is measured.

    python compare_to_onshape.py     # adds "onshape_comparison" to rebuild_summary.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent


def main() -> dict:
    onshape = trimesh.load(HERE / "onshape" / "part_studio.gltf", force="scene").to_geometry()
    onshape.apply_scale(1000.0)  # metres -> mm
    onshape.merge_vertices(merge_tex=True, merge_norm=True)  # glTF splits vertices per face
    rebuild = trimesh.load(HERE / "transducer_cable_holder.stl")
    assert onshape.is_watertight and rebuild.is_watertight
    a, _ = trimesh.sample.sample_surface_even(onshape, 40000, seed=1)
    b, _ = trimesh.sample.sample_surface_even(rebuild, 40000, seed=2)
    d = np.concatenate([trimesh.proximity.closest_point(rebuild, a)[1], trimesh.proximity.closest_point(onshape, b)[1]])
    out = {
        "onshape_volume_mm3": round(onshape.volume, 3), "rebuild_mesh_volume_mm3": round(rebuild.volume, 3),
        "onshape_area_mm2": round(onshape.area, 3), "rebuild_mesh_area_mm2": round(rebuild.area, 3),
        "bbox_max_difference_mm": round(float(np.abs(onshape.bounds - rebuild.bounds).max()), 5),
        "surface_distance_mm": {"samples": len(d), "mean": round(float(d.mean()), 5),
                                "p99": round(float(np.percentile(d, 99)), 5), "max": round(float(d.max()), 5)},
    }
    summary = json.loads((HERE / "rebuild_summary.json").read_text())
    summary["onshape_comparison"] = out
    (HERE / "rebuild_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
