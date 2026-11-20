"""The corrosion CubXL (``instruments_lab.cubxl_corrosion``, DAL PR #180's copper deck) on tray A of ``animate.py``'s
scenes, in place of round 2's liquid-handling CubXL, with its head driven by an ``instruments_lab`` timeline: round 2's
workflow uses it for DAL's powder reactivity test (``instruments_lab.powder_test``).

It goes where ``setup_lab.ROUND4_TRAY`` puts it: its bounding box centred at (-300, -114.5) on tray A. The tour's
meshes come from ``tour.load`` (cached in ``.cache/`` on instruments_lab.py's hash), so the deck is the same one the
corrosion tour shows, piece for piece.
"""
from __future__ import annotations

import numpy as np

import instruments_lab as IL
import r9_cubxl
import vlm as V
from scene import T

CUB_AT = (-300.0, -114.5)          # setup_lab.ROUND4_TRAY["A"]
PREFIX = "cub:"


def state_at(tl, v: float) -> dict:
    """A timeline's state at v (0-1): numbers interpolated, everything else held from the waypoint before."""
    ts = np.array(tl.t) / tl.t[-1]
    i = int(np.clip(np.searchsorted(ts, v, side="right") - 1, 0, len(ts) - 2))
    f = 0.0 if ts[i + 1] <= ts[i] else min(1.0, max(0.0, (v - ts[i]) / (ts[i + 1] - ts[i])))
    a, b = tl.states[i], tl.states[i + 1]
    out = {}
    for k, va in a.items():
        vb = b[k]
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
            out[k] = va + (vb - va) * f
        else:
            out[k] = vb if f >= 0.999 else va
    return out


class CubRig:
    """The corrosion CubXL as a ``tour.Rig`` on tray A; ``pose(state)`` puts its head, caps, tips and liquids where an
    instruments_lab timeline state says."""

    def __init__(self, L, hide_round2: bool = True, spare: bool = False):
        import tour
        self.L, self.sc = L, L.sc
        inst, ents = tour.load(["cubxl_corrosion"])["cubxl_corrosion"]
        x0, x1, y0, y1, z0, _ = inst.bbox()
        at = T((CUB_AT[0] - (x0 + x1) / 2, CUB_AT[1] - (y0 + y1) / 2, V.T_FLOOR - z0))
        self.inst = inst
        self.rig = tour.Rig(self.sc, inst, ents, PREFIX, at=at, parent="tray_A")
        self.body = f"{PREFIX}body"
        if hide_round2:                       # round 2's CubXL goes: the corrosion set-up replaces it, as in setup_lab
            for g in L.eq_groups["A"]:
                if L.eq_key[g] == "cubxl":
                    for n in L.eq_names(g):
                        self.sc.alpha[n] = 0.0
        if not spare:                         # the spare seat (y 35) is free: no FeSO4 vial tonight
            for n in self.rig.names.get("spare", []):
                self.sc.alpha[n] = 0.0
        self.state = None

    def deck_world(self, x, y, z) -> np.ndarray:
        """A CubOS deck point in world coordinates, where tray A is now."""
        return (self.sc.world(self.body) @ np.r_[IL._cx(x), IL._cy(y), IL._cz(z), 1.0])[:3]

    def pose(self, s: dict):
        self.state = s
        sc = self.sc
        for k, d in r9_cubxl.corr_offsets(s).items():
            sc.gmat[f"{PREFIX}{k}"] = T(d)
        for k, h in IL.corr_levels(s).items():
            z0, h0, _ = IL.LEVEL_AT[k]
            sc.gmat[f"{PREFIX}{k}"] = IL.Level(knots=((0.0, h), (1.0, h)), z0=z0, h0=h0).matrix(0.0)

    def play(self, tl, a: str, b: str, on_state=None):
        """An update(u) for Scene.step: the timeline from mark a to mark b; on_state(state) after each pose."""
        va, vb = tl.v(a), tl.v(b)

        def up(u):
            s = state_at(tl, va + (vb - va) * u)
            self.pose(s)
            if on_state is not None:
                on_state(s)
        return up
