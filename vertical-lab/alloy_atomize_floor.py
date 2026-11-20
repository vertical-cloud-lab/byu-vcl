"""The two-Shuttle floor of ``setup_lab.py`` for the alloy route's chapters 2 and 3 (#303, round 8).

Round 7's chapters 2 (``alloy_atomize.py``) and 3 (``alloy_print.py``) stood on the old one-Shuttle line: the Aconity
MIDI at ``line.LINE["aconity"]`` (x = 3250), where the second Kardex Shuttle now stands (``setup_lab.X2`` = 3630). This
module puts them on ``setup_lab.FLOOR_PLAN`` instead, without editing any shared file: for the length of a build,
``animate.Lab`` is ``setup_lab.TwoLab`` (the second Shuttle's meshes at X2) and ``line.LINE["aconity"]`` is the floor
plan's x; ``floor_at`` gives a machine's pose on the plan (``warehouse.place``, the N row facing -y, the S row +y).
"""
from __future__ import annotations

import numpy as np

import animate as A
import line
import setup_lab as SL
import warehouse as WH

ACONITY_X = SL.FLOOR_PLAN["aconity"][0]          # 6950: east of the second Shuttle
X2 = SL.X2                                       # 3630: the second Shuttle's centre


class TwoLab(SL.TwoLab):
    """setup_lab.TwoLab, called the way animate.Lab is (``robot=False``)."""

    def __init__(self, sc, data, robot=False, highlight=None):
        super().__init__(sc, data, highlight=highlight)


class two_shuttle:
    """``with two_shuttle(): ...``: animate.Lab is TwoLab and the Aconity's x is the floor plan's while the scene is
    built. The Aconity keeps its new x afterwards (labels and cameras read line.LINE); animate.Lab is put back."""

    def __enter__(self):
        self._lab = A.Lab
        A.Lab = TwoLab
        line.LINE["aconity"] = ACONITY_X
        return self

    def __exit__(self, *exc):
        A.Lab = self._lab
        return False


def floor_at(key: str, bbox) -> np.ndarray:
    """A machine's own frame -> its place on setup_lab.FLOOR_PLAN (the glovebox set back, as warehouse.Floor does)."""
    cx, row, turn, _ = SL.FLOOR_PLAN[key]
    front = WH.Y_FACE_N if row == "N" else WH.Y_FACE_S
    front += WH.SETBACK.get(key, 0.0) * (1 if row == "N" else -1)
    return WH.place(bbox, cx, front, row, turn)
