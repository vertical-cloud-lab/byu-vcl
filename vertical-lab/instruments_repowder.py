"""The rePowder as a register.py instrument: its furnace body, lid, hinge, draw latch and bolt (#303, PR "refine the
rePowder model"). The lid and latch are rebuilt from the live parameter dict, the rest comes from repowder/model.py's
mesh cache, so ``python3 register.py solve repowder`` can fit the lid's dimensions to frames of the real machine.

    refs/repowder/<view>.jpg + .json     (see register.py; poses are {"lid": 0..1, "latch": 0..1, "bolt": 0..1})
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "repowder"))
import model as M  # noqa: E402
from instruments import Instrument, Joint  # noqa: E402

MATERIALS: dict = {}
ANCHORS: dict = {}
FREE: dict = {}
CHECKS: dict = {}
REGISTRY: dict = {}

PIECES = {"lid": M.LID_PARTS, "latch": ("latch_lever", "latch_loop"), "bolt": ("latch_bolt",)}
# what register.py needs to see: the furnace and everything on it, not the chamber's stack, frame and utilities
SHOWN_GROUPS = {"furnace", "hood", "latch_lever", "latch_bolt", "machine", "rod", "arm", "arm_base", "top_ins", "tc"}
LID_PARAMS = dict(M.LID)


def _transform(pt, joint_vals: dict, part_joint: str | None):
    if part_joint is None:
        return np.asarray(pt, float)
    m = M.joint_matrix(part_joint, joint_vals.get(part_joint, 0.0))
    return (m @ np.r_[np.asarray(pt, float), 1.0])[:3]


def anchors(p: dict, pose: dict | None = None) -> dict:
    v = pose or {}
    BT, h1, h2, r, r1, ext = M.BODY_TOP, p["h1"], p["h2"], p["r"], p["r1"], p["ext"]
    zt = BT + h1 + h2
    g = M.latch_geom(p)
    lx, yf, zf, L = g["x"], g["yface"], g["zf"], g["length"]
    inset = r - r1
    lid = lambda pt: _transform(pt, v, "lid")  # noqa: E731
    a = {
        "lid top front mid": lid((0, -r1, zt)), "lid top front right": lid((ext - inset, -r1, zt)),
        "lid top back right": lid((ext - inset, r1, zt)), "lid top left": lid((-r1, 0, zt)), 
        "lid shoulder front": lid((0, -r, BT + h1)), "lid shoulder left": lid((-r, 0, BT + h1)),
        "lid foot front right": lid((ext, -r, BT)), "lid foot front mid": lid((0, -r, BT)),
        "lid foot left": lid((-r, 0, BT)), "lid foot back right": lid((ext, r, BT)),
        "lid back top": lid((0, r1, zt)),
        "hinge barrel left": np.array([-75.0, r + p["hinge_off"], BT + 6.0]),
        "hinge barrel right": np.array([75.0, r + p["hinge_off"], BT + 6.0]),
        "viewport centre": tuple(M.VIEWPORT + M.VIEWPORT_N * 30.0),
        "door top back": np.array([M.CH_X[0], M.DOOR_OPEN_W / 2, M.DOOR_Z[1]]),
        "door top front": np.array([M.CH_X[0], -M.DOOR_OPEN_W / 2, M.DOOR_Z[1]]),
        "door bottom mid": np.array([M.CH_X[0], 0.0, M.DOOR_Z[0]]),
        "knob ball": lid(tuple(np.array(M.facet_plane(p, "front", 0.12)[0]) + np.array([-35.0, 0, 0])
                               + np.array([0.62, -0.15, 0.77]) / 0.99 * 40.0)),
        "hinge barrel mid": np.array([0.0, r + p["hinge_off"], BT + 6.0]),
        "latch foot": np.array([lx, yf - 14.0, zf - 36.0]),
        "latch lever top": _transform((lx, yf - 10.0, zf + L), v, "latch"),
        "latch lug": _transform((lx + 28.0, yf - 11.0, g["bolt_z"]), v, "latch"),
        "keeper top": lid((lx, -r - 4.0, g["keeper"][2] + 38.0)),
        "bolt cabinet": _transform((g["cabinet_x"] + 30.0, yf - 11.0, g["bolt_z"]), v, "bolt"),
        "deck front right": np.array([ext - 6.0, -M.BODY_R, M.BODY_TOP]),
        "base front left": np.array([-M.BODY_R * 0.7, -M.BODY_R * 0.7, M.Z_PLATFORM[1]]),
    }
    return {k: tuple(float(c) for c in pt) for k, pt in a.items()}


ANCHORS["repowder"] = (LID_PARAMS, anchors)
FREE["repowder"] = ["r1", "ext", "h1", "h2", "latch_x", "latch_len", "cabinet_x"]
CHECKS["repowder"] = lambda p: [p["r"] - p["r1"] - 10, p["h2"] - 40, p["h1"] - 20, p["ext"] - M.BODY_R - 20]


def repowder() -> Instrument:
    p = dict(ANCHORS["repowder"][0])
    full = M.meshes()
    live = {x.name: x for x in M.hood_parts(p)}
    where = {n: k for k, ns in PIECES.items() for n in ns}
    inst = Instrument("repowder", "Induction atomizer", "AMAZEMET rePowder", (1000.0, 800.0, 1600.0),
                      "AMAZEMET rePowder; the lid, hinge, latch and bolt from the lab's training video T4, notes/repowder_refine.md")
    inst.meshes = {"body": [], "lid": [], "latch": [], "bolt": []}
    for name, d in full.items():
        if name in live or d["group"] not in SHOWN_GROUPS or d["whole"] is None or not d["whole"].n_points:
            continue
        inst.meshes["body"].append((d["whole"], d["color"], 1.0))
    for name, part in live.items():
        inst.meshes[where.get(name, "body")].append((M.tess(part.shape, part.tol), part.color, 1.0))
    for k in ("lid", "latch", "bolt"):
        j = M.joints()[k]
        if j["kind"] == "hinge":
            inst.joints[k] = Joint("hinge", axis=tuple(j["axis"]), pivot=tuple(float(c) for c in M.hinge_point(p) if True)
                                   if k == "lid" else tuple(float(c) for c in M.latch_geom(p)["pivot"]), deg=j["deg"])
        else:
            inst.joints[k] = Joint("slide", vec=tuple(j["vec"]))
    inst.anchors = anchors(p)
    return inst


REGISTRY["repowder"] = repowder
