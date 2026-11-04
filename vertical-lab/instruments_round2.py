"""Round 2's equipment doing its job, with the insides showing (#303, PR #320): the Opentrons OT-2's gantry and pipette
over its deck, the Bambu Lab H2D and A1 mini printing a part, the CubXL's pipette over its rack, and the multi-doser
dosing into a vial drawn in half section. ``tour.py`` plays each one, like the round-3 and round-4 instruments:

    xvfb-run -a python3 tour.py ot2 h2d a1_mini cubxl_lh multidoser   # -> out/instruments/<key>.gif, .png; out/mp4/...
    python3 tour.py still h2d                                            # the end of every action -> /tmp/still_h2d.png

Each is an ``instruments.Instrument``: named pieces (``body`` stays put), a ``Joint`` per moving piece and an
``actions`` script. What is around each process is drawn see-through while it runs (a piece's ``~`` value in the
actions, as ``alloy_workflow.py`` ghosts the depowdering box and the MIDI's shell), and liquid, powder and printed
parts grow with ``grow()``, a ``follow`` joint that stretches a piece upward from its base. A machine whose motion
isn't rigid pieces (the doser's chain) can name its own clip function in ``TOURS``; tour.py calls it instead of
``tour_one``.

The models are round 2's (``lab_models/equipment.py``, ``lab_models/vendor.py``, ``carousel.py``), split into the
pieces that move; nothing here changes how round 2's scenes draw them. Frame, as in ``instruments.py``: x to the
right and y away from you when you face the front, z up from the bench, origin at the centre of the footprint, mm.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

from instruments import Instrument, Joint, _piece, _xcyl, _ycyl  # noqa: F401

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import Model, box, cyl, hose, rbox, tube  # noqa: E402,F401

# files the builds read besides this one and tour.py's common sources: tour.load() re-tessellates when they change
SOURCES = ["lab_models/equipment.py", "lab_models/vendor.py", "lab_models/labware.py", "carousel.py",
           "multidoser/layout.py", "multidoser/parts.py", "multidoser/params.py", "multidoser/kinematics.py"]

# name: (r, g, b, opacity, specular), merged into tour.MATS
MATERIALS = {
    "r2_petg_blue": (0.16, 0.42, 0.80, 1.0, 0.35),      # the part printing on the H2D
    "r2_pla_orange": (0.95, 0.50, 0.12, 1.0, 0.30),     # the part printing on the A1 mini
    "r2_pla_green": (0.20, 0.62, 0.32, 1.0, 0.30),
    "r2_liquid": (0.30, 0.58, 0.92, 0.80, 0.6),         # the liquid in a half-section vial
    "r2_liquid_cut": (0.22, 0.48, 0.85, 1.0, 0.4),
    "r2_powder": (0.66, 0.66, 0.70, 1.0, 0.1),          # a grey metal powder
    "r2_glass_cut": (0.80, 0.90, 0.95, 0.45, 0.9),      # a vial's glass, cut in half
    "r2_tip": (0.90, 0.91, 0.88, 0.70, 0.4),            # a polypropylene pipette tip
    "r2_hot": (1.00, 0.42, 0.08, 1.0, 0.1),             # a hot nozzle tip
}


# ===================================================================================================== helpers
def split(model: Model, inst: Instrument, groups: dict, drop=()) -> None:
    """Hand a lab_models Model's parts to the instrument's pieces: groups = {piece: (part names)}; every other part
    goes to "body", and parts named in `drop` are left out."""
    owner = {n: piece for piece, names in groups.items() for n in names}
    for part in model.parts:
        if part.name in drop:
            continue
        _piece(inst, owner.get(part.name, "body")).parts.append(part)


def grow(z0: float, h0: float, h1: float, parent: str | None = None, v0: float = 0.0) -> Joint:
    """A follow joint that stretches a piece modelled from z0 to z0 + h0 so it reaches z0 + h1 at v = 1: a liquid
    level, a powder heap or a printed part (a prism, so stretching it is the same as adding layers). Below v = 0 it
    shrinks back, to zero height at v = -h0 / (h1 - h0)."""
    k = h1 / h0 - 1.0
    zero = [[0.0] * 4 for _ in range(3)]
    jz = [[0.0] * 4, [0.0] * 4, [0.0, 0.0, k, -k * z0]]
    return Joint("follow", vec=(0.0, 0.0, 1.0), jac=(zero, zero, jz), parent=parent, v0=v0)


def trace(path, axis: int, parent: str | None = None) -> Joint:
    """A follow joint that moves a piece along one axis (0 x, 1 y, 2 z) of a path's offsets, in step with a "path"
    joint on the same waypoints: a CoreXY gantry following its toolhead in y, a bed slinger's bed in y."""
    zero = [[0.0] * 4 for _ in range(3)]
    jac = [list(map(list, zero)) for _ in range(3)]
    jac[axis][axis][3] = 1.0
    return Joint("follow", path=tuple(tuple(p) for p in path), jac=tuple(tuple(map(tuple, j)) for j in jac),
                 parent=parent)


def loops(x0, x1, y0, y1, n: int, start=(0.0, 0.0), z=0.0) -> tuple:
    """Waypoints from `start` to the corner (x0, y0), n times round the rectangle, and back to `start`."""
    pts = [(start[0], start[1], z)]
    for _ in range(n):
        pts += [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    pts += [(x0, y0, z), (start[0], start[1], z)]
    return tuple(pts)


def half(shape, y: float = 0.0, keep_back: bool = True):
    """The back half (y >= `y`) of a CadQuery shape, so a camera in front sees its section."""
    big = 5000.0
    cutter = box(-big, y - big if keep_back else y, -big, big, y if keep_back else y + big, big)
    return shape.cut(cutter)


# ===================================================================================================== Opentrons OT-2
def ot2() -> Instrument:
    """The OT-2 from Opentrons' reference STEP (lab_models/vendor.py), its gantry and pipette split out by bounding
    box so they move over the deck."""
    raise FileNotFoundError("ot2: not built yet")


# ===================================================================================================== Bambu Lab H2D
def h2d() -> Instrument:
    raise FileNotFoundError("h2d: not built yet")


# ===================================================================================================== Bambu Lab A1 mini
def a1_mini() -> Instrument:
    raise FileNotFoundError("a1_mini: not built yet")


# ===================================================================================================== CubXL, liquid handling
def cubxl_lh() -> Instrument:
    raise FileNotFoundError("cubxl_lh: not built yet")


# ===================================================================================================== the multi-doser
def multidoser() -> Instrument:
    """The chain carousel v2 (carousel.py): its own layout.placements(State(...)), the dose in half section."""
    raise FileNotFoundError("multidoser: not built yet")


# {key: name of a function here, (inst, entries) -> str}: a clip tour.tour_one can't play; tour.py calls it instead
TOURS: dict[str, str] = {}

REGISTRY = {"ot2": ot2, "h2d": h2d, "a1_mini": a1_mini, "cubxl_lh": cubxl_lh, "multidoser": multidoser}
