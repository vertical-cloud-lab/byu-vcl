"""The two OpenFlexure microscopes, both set up for reflection (epi-) illumination, from OpenFlexure's own CAD (#303).

* **OpenFlexure Microscope v7** (gitlab.com/openflexure/openflexure-microscope, tag ``v7.0.0-beta5``, commit
  ``4828ffa5``; CERN-OHL-S-2.0): the high-resolution build with the beamsplitter optics module, the filter cube and
  the reflection illuminator; stand, motors, Raspberry Pi and Sangaboard.
* **OpenFlexure Delta Stage** (gitlab.com/openflexure/openflexure-delta-stage, tag ``v1.2.3``, commit ``d882d18b``;
  CERN-OHL-1.2): the same reflection optics under the delta stage, on its electronics base.

Every part was exported from OpenFlexure's OpenSCAD source with OpenSCAD's manifold backend, in assembled positions:
the v7 through the repo's own assembly-rendering modules, the delta stage with its ``build.sh`` options and the
transforms in ``openflexure/manifest.json``. Neither repo renders the reflection set-up assembled, so the filter cube,
illuminator and LED are placed from the .scad sources (see the manifest's notes). The scripts are in
``openflexure/``; the meshes (about 60 MB of STL) are not committed, like the other vendor CAD: they live in
``.cache/openflexure/{v7,delta}/`` and are regenerated with those scripts.

Reflection mode is what metallography needs: the LED sits beside the optics module under the stage, the beamsplitter
turns its light up through the objective onto an opaque, polished sample, and the camera looks down through it.
"""
from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments as I
from common import box, cyl  # noqa: F401  (lab_models helpers, on the path via instruments)

HERE = Path(__file__).resolve().parent
SRC = HERE / ".cache" / "openflexure"
MANIFEST = json.loads((HERE / "openflexure" / "manifest.json").read_text())
MAX_TRIS = 25000            # per part, for the scene; the main bodies keep their detail


def _hex(c: str) -> tuple:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _load(key: str) -> dict:
    """{part: (PolyData, rgb)} for one microscope, decimated to MAX_TRIS."""
    parts = MANIFEST["instruments"][key]["parts"]
    out = {}
    for name, p in parts.items():
        if p.get("placeholder") and "slide" in name:          # the sample is ours (below)
            continue
        path = SRC / p["file"]
        if not path.exists():
            raise FileNotFoundError(f"{path}: build the OpenFlexure meshes first (openflexure/README.md)")
        m = pv.read(str(path)).triangulate().clean()
        if m.n_cells > MAX_TRIS:
            m = m.decimate(1.0 - MAX_TRIS / m.n_cells)
        m = m.compute_normals(split_vertices=True, feature_angle=35.0, auto_orient_normals=False)
        col = _hex(p["colour"])
        if name == "led_star_placeholder":
            col = (1.0, 0.85, 0.2)
        out[name] = (m, col, p.get("moves_with_stage", []))
    return out


def _sample(z: float) -> I.Model:
    """A glass slide with a small polished metal coupon on it: what reflection mode is for."""
    m = I.Model("ofm_sample", "slide and coupon")
    m.add("slide", box(-37.5, -12.5, 0, 37.5, 12.5, 1.0), "window")
    m.add("coupon", box(-6, -6, 1.0, 6, 6, 4.0), "sample")
    return m


def _build(key: str, title: str, model: str, source: str, stage_parts: tuple, optics_parts: tuple, z_stage: float,
           cam) -> I.Instrument:
    d = MANIFEST["instruments"][key]
    (x0, y0, z0), (x1, y1, z1) = d["overall_bbox_mm"]
    inst = I.Instrument(f"openflexure_{key}", title, model, (round(x1 - x0), round(y1 - y0), round(z1 - z0)), source)
    for name, (mesh, col, moves) in _load(key).items():
        piece = "stage" if name in stage_parts else "optics" if name in optics_parts else \
            "led" if name == "led_star_placeholder" else "body"
        inst.meshes.setdefault(piece, []).append((mesh, col, 1.0))
    inst.pieces["sample"] = _sample(z_stage)
    inst.meshes.setdefault("stage", [])
    return inst


def v7() -> I.Instrument:
    d = MANIFEST["instruments"]["v7"]
    zs = d["stage_top_surface_z"]
    inst = _build("v7", "Microscope, reflection", "OpenFlexure Microscope v7",
                  "OpenFlexure Microscope v7.0.0-beta5's OpenSCAD (commit 4828ffa5, CERN-OHL-S-2.0), exported "
                  "assembled with its own rendering modules; reflection optics placed from the .scad sources",
                  ("xy_stage", "sample_clips"),
                  ("optics_module_beamsplitter", "objective", "tube_lens", "picamera2_with_cover", "camera_ribbon_cable",
                   "fl_cube", "reflection_illuminator_holder", "reflection_led_condenser"), zs, None)
    inst.joints = {
        "sample": I.Joint("path", parent="stage", path=((0, -170, zs + 90), (0, -60, zs + 30), (0, 0, zs + 6),
                                                         (0, 0, zs))),
        "stage": I.Joint("slide", vec=(6.0, 4.0, 0)),
        "optics": I.Joint("slide", vec=(0, 0, 2.0)),
        "led": I.Joint("fade", v0=1.0),
    }
    inst.actions = [
        ("A polished coupon on a slide goes under the clips: reflection mode, for opaque metal samples.", 2.2,
         {"sample": (0.0, 1.0), "led": (1.0, 1.0)}),
        ("The LED beside the optics module lights the sample through the objective via the beamsplitter; the camera "
         "looks down through it. The flexure stage scans x/y (+-6 mm) and the optics focus.", 3.0,
         {"stage": (0.0, 1.0), "optics": (0.0, 1.0)}),
        ("Back to centre. Printed in PLA, about 170 mm across; several fit on one tray.", 1.8,
         {"stage": (1.0, 0.0), "optics": (1.0, 0.0)}),
    ]
    inst.labels = [("beamsplitter optics and reflection illuminator", (0, -20, 60), (0.12, 0.70)),
                   ("flexure XY stage", (20, -20, zs), (0.84, 0.25))]
    inst.cam = (0.9, -1.6, 0.9)
    return inst


def delta() -> I.Instrument:
    d = MANIFEST["instruments"]["delta"]
    zs = d["stage_top_surface_z"]
    inst = _build("delta", "Microscope, reflection", "OpenFlexure Delta Stage",
                  "OpenFlexure Delta Stage v1.2.3's OpenSCAD (commit d882d18b, CERN-OHL-1.2), exported with its "
                  "build.sh options for reflection illumination; assembled from the .scad sources",
                  ("moving_stage", "sample_clips"), (), zs, None)
    inst.joints = {
        "sample": I.Joint("path", parent="stage", path=((0, -170, zs + 90), (0, -60, zs + 30), (0, 0, zs + 6),
                                                         (0, 0, zs))),
        "stage": I.Joint("slide", vec=(5.0, -4.0, 3.0)),
        "led": I.Joint("fade", v0=1.0),
    }
    inst.actions = [
        ("The delta stage: three flexure legs move the stage in x, y and z. A polished coupon goes on.", 2.2,
         {"sample": (0.0, 1.0), "led": (1.0, 1.0)}),
        ("Same reflection optics underneath, fixed; the stage does the moving, focus included.", 3.0,
         {"stage": (0.0, 1.0)}),
        ("Back to centre.", 1.4, {"stage": (1.0, 0.0)}),
    ]
    inst.labels = [("moving stage", (0, 30, zs), (0.84, 0.25)),
                   ("electronics base (Pi, Sangaboard)", (60, -40, 40), (0.84, 0.72))]
    inst.cam = (0.9, -1.6, 0.9)
    return inst
