"""Exact chain kinematics for the v2 loop (both chains identical and in step).

A positive shift runs the loop counter-clockwise in (y, z): bottom run toward
+y, up the +y side, top run toward -y, down the -y side. The machine runs the
other way (params.RUN_DIRECTION = -1), i.e. negative shifts. At home (shift 0) the 104 pins
sit where ``home_pins()`` puts them: pin 0 at the bottom-left tangent point,
12 links along the bottom, 8 round B+, 24 up the side, 8 round T+, 12 along
the top, 8 round T-, 24 down the side and 8 round B-.

All four 32T sprockets turn together by one tooth per link of travel. Pins
on a sprocket sit in its seats and turn with it; each free span runs
straight between the last pin seated on one sprocket and the first on the
next. Every span is a whole number of pitches and its two end pins sit at
the same tooth phase on equal sprockets, so the span just translates
(polygonal action: it rides up and down by R(1 - cos(pi/32)) = 0.23 mm and
surges by up to half a pitch). For a shift s, pin j takes home slot
j + round(s) and then moves g = s - round(s) of a link (g in [-1/2, 1/2)):
round its sprocket if the slot is seated, with its span if the slot is
free. At g = +-1/2 the two descriptions meet, so nothing jumps.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from params import LOOP_A, LOOP_B, LOOP_M, LOOP_N, N_LINKS, N_TEETH, P, R, Z_BOT

ALPHA = 2 * math.pi / N_TEETH
LOOP_Y = LOOP_B / 2
Z_TOP_ = Z_BOT + LOOP_A
CORNERS = {"B+": (LOOP_Y, Z_BOT), "T+": (LOOP_Y, Z_TOP_), "T-": (-LOOP_Y, Z_TOP_), "B-": (-LOOP_Y, Z_BOT)}


@lru_cache(None)
def home_pins() -> np.ndarray:
    """104 pin centres (y, z) at home, in loop order, from the bottom run's
    tangent point under the B- sprocket."""
    b = LOOP_B
    pts = []
    y0, z0 = -b / 2, Z_BOT - R
    pts += [(y0 + k * P, z0) for k in range(LOOP_M)]                                       # bottom straight
    pts += [(b / 2 + R * math.cos(-math.pi / 2 + j * ALPHA), Z_BOT + R * math.sin(-math.pi / 2 + j * ALPHA)) for j in range(8)]
    pts += [(b / 2 + R, Z_BOT + k * P) for k in range(LOOP_N)]                             # up the +y side
    pts += [(b / 2 + R * math.cos(j * ALPHA), Z_TOP_ + R * math.sin(j * ALPHA)) for j in range(8)]
    pts += [(b / 2 - k * P, Z_TOP_ + R) for k in range(LOOP_M)]                            # top straight
    pts += [(-b / 2 + R * math.cos(math.pi / 2 + j * ALPHA), Z_TOP_ + R * math.sin(math.pi / 2 + j * ALPHA)) for j in range(8)]
    pts += [(-b / 2 - R, Z_TOP_ - k * P) for k in range(LOOP_N)]                           # down the -y side
    pts += [(-b / 2 + R * math.cos(math.pi + j * ALPHA), Z_BOT + R * math.sin(math.pi + j * ALPHA)) for j in range(8)]
    pts = np.array(pts)
    gaps = np.linalg.norm(np.roll(pts, -1, axis=0) - pts, axis=1)
    assert len(pts) == N_LINKS and np.allclose(gaps, P, atol=1e-6), (len(pts), gaps.min(), gaps.max())
    return pts


@lru_cache(None)
def _slots():
    """For each home slot: ('seat', corner centre) or ('span', tangent point, its corner centre)."""
    m, n = LOOP_M, LOOP_N
    b0, b1 = 0, m                       # bottom: pin 0 (B- departure) .. pin 12 (B+ arrival)
    r0 = m + 8                          # 20: B+ departure
    t0 = r0 + n                         # 44: T+ arrival
    tp0 = t0 + 8                        # 52: T+ departure
    tm0 = tp0 + m                       # 64: T- arrival
    l0 = tm0 + 8                        # 72: T- departure
    bm0 = l0 + n                        # 96: B- arrival
    pins = home_pins()
    seats = {"B+": range(b1, r0 + 1), "T+": range(t0, tp0 + 1), "T-": range(tm0, l0 + 1), "B-": list(range(bm0, N_LINKS)) + [0]}
    spans = [(range(b0 + 1, b1), b0, "B-"), (range(r0 + 1, t0), r0, "B+"), (range(tp0 + 1, tm0), tp0, "T+"), (range(l0 + 1, bm0), l0, "T-")]
    out = [None] * N_LINKS
    for c, idx in seats.items():
        for k in idx:
            out[k] = ("seat", np.array(CORNERS[c]))
    for idx, tan, c in spans:
        for k in idx:
            out[k] = ("span", pins[tan].copy(), np.array(CORNERS[c]))
    assert all(o is not None for o in out)
    return out


def _rot(v: np.ndarray, a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def pins_at(shift: float) -> np.ndarray:
    """(104, 2) pin centres (y, z) after the chain has travelled `shift` links (forward = bottom run toward +y)."""
    n = math.floor(shift + 0.5)
    g = shift - n                                   # [-1/2, 1/2)
    phi = g * ALPHA
    home = home_pins()
    sl = _slots()
    out = np.zeros((N_LINKS, 2))
    for j in range(N_LINKS):
        k = (j + n) % N_LINKS
        s = sl[k]
        if s[0] == "seat":
            c = s[1]
            out[j] = c + _rot(home[k] - c, phi)
        else:
            t, c = s[1], s[2]
            out[j] = home[k] + (c + _rot(t - c, phi) - t)
    return out


def sprocket_angle(shift: float) -> float:
    """Rotation of every 32T sprocket (and its shaft) from home, rad, counter-clockwise in (y, z)."""
    return shift * ALPHA


if __name__ == "__main__":
    a = pins_at(0.0)
    assert np.allclose(a, home_pins())
    for s in (0.3, 0.5 - 1e-9, 0.5, 1.0, 7.77, -3.2):
        q = pins_at(s)
        gaps = np.linalg.norm(np.roll(q, -1, axis=0) - q, axis=1)
        print(f"shift {s:6.3f}: pitch {gaps.min():.6f}-{gaps.max():.6f}")
    q0, q1 = pins_at(0.5 - 1e-7), pins_at(0.5 + 1e-7)
    print("max jump at g = 1/2:", float(np.abs(q0 - q1).max()))
    assert np.allclose(pins_at(1.0), np.roll(home_pins(), -1, axis=0))
