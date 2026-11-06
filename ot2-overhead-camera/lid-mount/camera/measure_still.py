#!/usr/bin/env python3
"""Where is the lid camera looking? Fit the deck's rails in a full-resolution still.

Reads a 4056 x 3040 still (`curl -s localhost:8081/still` on the camera's Pi, see
stream/picam_source.py) and finds the metal rails in the 4.5 mm gaps between deck slots. Each
rail shows as two dark edges about 3.5 mm apart; its centre line is their midpoint. The rails
around the centre column sit at known deck coordinates (Opentrons' slot pitch, 132.5 x 90.5 mm),
so a least-squares fit of a similarity (scale, rotation, shift) gives

    px/mm at the deck, hence the field of view and the zoom (pinhole model of ../cad/coverage.py),
    the rotation of the picture against the deck,
    where the picture's centre is on the deck, relative to the deck centre (between slots 5 and 8),

and from those, how far to slide, turn and zoom the mount to look straight down at the plate in
--target-slot (default 7), centred, with --target-margin (default 5) mm of deck left and right of
it. Writes ../exports/lid_camera_setup.json and ../renders/lid_camera_now.jpg (the still, with the
deck's slots drawn where the fit puts them).

    python measure_still.py frames/2026-10-20/still_0358Z_lit.jpg

The search windows come from the previous fit in lid_camera_setup.json, widened by --search
pixels, so after a small move (up to ~20 mm) it finds the rails again. After a bigger one, pass
--guess X,Y (mm, where the picture's centre now is relative to the deck centre) and --focal.

Plate mode measures from one 96-well plate's own 12 x 8 well grid instead, for when the camera is
zoomed in on that plate and no rails are in view:

    python measure_still.py STILL --plate 7 [--deck-fit ../exports/lid_camera_setup.json] [--near U,V]

For a range of ring sizes it scores every point for being the centre of a circle that size, links
the high scores into square grids (measuring their pitch and angle) and takes each grid's 12 x 8
block of sites with the most score. Of the strong blocks it keeps the one nearest where the plate
should be (slot SLOT through --deck-fit, a rail-mode fit of the same camera state; else --near;
else the picture centre), so the tip rack next door is skipped. Then it centres each well on the
outer edge of its rim (a circle fitted to edge points on 120 rays; the well's bottom shows inside
it, shifted by parallax), least-squares fits a similarity from plate mm to pixels over the 96
wells, refits until that settles, and checks the block a column and a row either way, since the
plate's frame and row letters one pitch outside the wells can pass for a column of wells. It
reports px/mm, field and zoom at the plate's top, the rotation, where the picture's centre is from
the plate centre, the margins round the plate, and how to slide, turn and zoom so the plate sits
centred with --target-margin mm of deck left and right. Writes ../exports/lid_camera_plate.json
and ../renders/lid_camera_plate.jpg.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
RENDERS = HERE.parent / "renders"

PX = (4056, 3040)
PIXEL_MM = 0.00155                    # IMX477 pixel pitch
SENSOR = (PX[0] * PIXEL_MM, PX[1] * PIXEL_MM)
PUPIL_ABOVE_DECK = 590.2 + 11.5 + 20.0  # window top + lens front above it + pupil inside the lens (coverage.py)
SLOTS = {n: (((n - 1) % 3) * 132.5 + 64.0, ((n - 1) // 3) * 90.5 + 43.0) for n in range(1, 13)}
SLOT_SIZE = (128.0, 86.0)
DECK_C = (196.5, 178.75)              # midpoint of slots 5 and 8
DECK_SPAN = (393.0, 357.5)            # outer edges of the 12 slots
RAIL_W = 3.5                          # mm between a rail's two dark edges (measured: 33 px at 9.5 px/mm)
PLATE = (127.76, 85.48)               # SBS plate footprint, mm
PLATE_TOP = PUPIL_ABOVE_DECK - 14.35  # pupil above a plate's top (an SBS plate is 14.35 mm tall)
PITCH, WELL_R = 9.0, 6.86 / 2         # 96-well pitch and well opening radius, mm
# Well centres in plate mm, A1 first: origin at the grid's centre (= the plate's), x right toward column 12, y back toward row A.
WELLS = np.array([((c - 5.5) * PITCH, (3.5 - r) * PITCH) for r in range(8) for c in range(12)])

# Rails around the centre column: (name, "h"/"v", deck coordinate of the centre line, span along it in mm).
# Horizontal ones sit in the gaps between rows, vertical ones between columns.
RAILS = [
    ("11|8", "h", 269.25, (150.0, 245.0)),
    ("8|5", "h", 178.75, (150.0, 245.0)),
    ("5|2", "h", 88.75, (150.0, 245.0)),
    ("4|5", "v", 130.25, (95.0, 165.0)),
    ("8|9", "v", 262.75, (190.0, 255.0)),
]


def to_px(fit: dict, X: float, Y: float) -> tuple[float, float]:
    """Deck mm -> still pixels, by the fit's inverse."""
    A, B, C, F = fit["A"], fit["B"], fit["C"], fit["F"]
    m = np.linalg.inv(np.array([[A, B], [B, -A]]))
    u, v = m @ np.array([X - DECK_C[0] - C, Y - DECK_C[1] - F])
    return float(u), float(v)


def guess_fit(offset: tuple[float, float], focal: float, rotation: float) -> dict:
    """A fit dict from a guessed state: picture centre at `offset` mm from the deck centre."""
    s = focal / (PIXEL_MM * PUPIL_ABOVE_DECK)  # px per mm at the deck
    th = math.radians(rotation)
    A, B = math.cos(th) / s, math.sin(th) / s
    uc, vc = (PX[0] - 1) / 2, (PX[1] - 1) / 2
    return {"A": A, "B": B, "C": offset[0] - (A * uc + B * vc), "F": offset[1] - (B * uc - A * vc)}


def rail_centre(profile: np.ndarray, sep: float) -> float | None:
    """Midpoint of the deepest pair of dark minima about `sep` px apart, or None."""
    p = profile - np.median(profile)
    mins = [i for i in range(1, len(p) - 1) if p[i] <= p[i - 1] and p[i] <= p[i + 1] and p[i] < -3]
    best, where = 0.0, None
    for i in mins:
        for j in mins:
            if j > i and abs((j - i) - sep) <= 0.2 * sep + 2:
                depth = -(p[i] + p[j])
                if depth > best:
                    best, where = depth, (i + j) / 2
    return where


def measure(gray: np.ndarray, prior: dict, search: int) -> tuple[dict, list]:
    s0 = 1 / math.hypot(prior["A"], prior["B"])
    sep = RAIL_W * s0
    rows, rhs, found = [], [], []
    for name, o, mm, (a, b) in RAILS:
        pts = []
        for t in np.linspace(a, b, 16):
            X, Y = (t, mm) if o == "h" else (mm, t)
            u, v = (int(round(c)) for c in to_px(prior, X, Y))
            if o == "h":
                lo, hi = max(0, v - search), min(PX[1], v + search)
                if u < 25 or u > PX[0] - 25 or hi - lo < 50:
                    continue
                c = rail_centre(gray[lo:hi, u - 20:u + 20].mean(axis=1), sep)
                if c is not None:
                    pts.append((u, lo + c))
            else:
                lo, hi = max(0, u - search), min(PX[0], u + search)
                if v < 25 or v > PX[1] - 25 or hi - lo < 50:
                    continue
                c = rail_centre(gray[v - 20:v + 20, lo:hi].mean(axis=0), sep)
                if c is not None:
                    pts.append((lo + c, v))
        if len(pts) < 5:
            continue
        P = np.array(pts)
        # drop outliers from a straight line
        if o == "h":
            k, b0 = np.polyfit(P[:, 0], P[:, 1], 1)
            r = P[:, 1] - (k * P[:, 0] + b0)
        else:
            k, b0 = np.polyfit(P[:, 1], P[:, 0], 1)
            r = P[:, 0] - (k * P[:, 1] + b0)
        P = P[np.abs(r) <= max(2.0, 2.5 * np.median(np.abs(r)))]
        found.append({"rail": name, "points": len(P)})
        for u, v in P:
            if o == "h":
                rows.append([-v, u, 0, 1]); rhs.append(mm - DECK_C[1])
            else:
                rows.append([u, v, 1, 0]); rhs.append(mm - DECK_C[0])
    if len({f["rail"] for f in found} & {"11|8", "8|5", "5|2"}) < 2 or not {f["rail"] for f in found} & {"4|5", "8|9"}:
        raise SystemExit(f"Too few rails found ({found}); pass --guess and --focal closer to the truth")
    M, y = np.array(rows), np.array(rhs)
    (A, B, C, F), *_ = np.linalg.lstsq(M, y, rcond=None)
    res = M @ np.array([A, B, C, F]) - y
    return {"A": float(A), "B": float(B), "C": float(C), "F": float(F), "rms_mm": float(res.std()),
            "max_mm": float(np.abs(res).max())}, found


# --- plate mode: one 96-well plate's own well grid --------------------------------------------------
RING_PX = 8.0                             # ring radius, working px, while searching for the grid
UNIT = [(1, 0), (-1, 0), (0, 1), (0, -1)]
STEPS = UNIT + [(1, 1), (1, -1), (-1, 1), (-1, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]  # bridge a missed well


def ring_map(img: np.ndarray, f: float, r: float) -> tuple[np.ndarray, float, float]:
    """`img` shrunk about f times, scored for circles of radius r (full-res px): the mean, round a thin ring of
    that radius, of edge strength running along the ring less edge strength crossing it (colour gradients, so
    blue paint shows too). It peaks at the centres of circles, empty or paint-filled wells alike, and is ~0 on
    texture and where other wells' rims cross the ring. Returns the map and its pixel size (fx, fy) in
    full-res px; map pixel (x, y) is full-res ((x + .5) fx - .5, (y + .5) fy - .5)."""
    h, w = img.shape[:2]
    size = (max(8, round(w / f)), max(8, round(h / f)))
    small = cv2.GaussianBlur(cv2.resize(img, size, interpolation=cv2.INTER_AREA), (0, 0), 0.7).astype(np.float32)
    fx, fy = w / size[0], h / size[1]
    xx, yy, xy = (np.zeros(small.shape[:2], np.float32) for _ in range(3))
    for ch in cv2.split(small):
        gx, gy = cv2.Sobel(ch, cv2.CV_32F, 1, 0), cv2.Sobel(ch, cv2.CV_32F, 0, 1)
        xx, yy, xy = xx + gx * gx, yy + gy * gy, xy + gx * gy
    g = np.sqrt(xx + yy) + 1e-3            # |g| cos 2theta and |g| sin 2theta of the gradient's direction theta
    c2, s2 = (xx - yy) / g, 2 * xy / g
    rr = r / math.sqrt(fx * fy)
    n = int(rr + 4)
    y, x = np.mgrid[-n:n + 1, -n:n + 1]
    ring = np.exp(-0.5 * (np.hypot(x, y) - rr) ** 2)
    ring /= ring.sum()
    phi = np.arctan2(y, x)                 # |g| cos 2(theta - phi): +|g| for a radial gradient, -|g| for a tangential one
    return (cv2.filter2D(c2, -1, (ring * np.cos(2 * phi)).astype(np.float32))
            + cv2.filter2D(s2, -1, (ring * np.sin(2 * phi)).astype(np.float32))), fx, fy


def peaks(R: np.ndarray, rad: int, n: int = 800) -> tuple[np.ndarray, np.ndarray]:
    """The n strongest local maxima of R at least `rad` px apart and above its noise (median + 4 MAD)."""
    med = float(np.median(R))
    floor = med + 4 * 1.4826 * float(np.median(np.abs(R - med)))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * rad + 1, 2 * rad + 1))
    ys, xs = np.nonzero((R >= cv2.dilate(R, k)) & (R > floor))
    o = np.argsort(-R[ys, xs])[:n]
    return np.column_stack([xs[o], ys[o]]).astype(float), R[ys[o], xs[o]]


def grid_angle(P: np.ndarray, w: np.ndarray, pitch: float) -> float | None:
    """Angle of the grid's rows (mod 90 deg, picture px) from every pair of peaks about one pitch apart."""
    d = P[None] - P[:, None]
    L = np.hypot(d[..., 0], d[..., 1])
    m = (L > 0.85 * pitch) & (L < 1.15 * pitch)
    if m.sum() < 16:
        return None
    z = (np.minimum(w[:, None], w[None]) * np.exp(4j * np.arctan2(d[..., 1], d[..., 0])))[m].sum()
    return float(np.angle(z)) / 4


def neighbours(P: np.ndarray, shape: tuple, pitch: float, ang: float, steps: list) -> dict:
    """For each grid step (di, dj), the peak that far from each peak (within 0.22 pitch), or -1."""
    lab = np.full(shape, -1, np.int32)
    for k, (x, y) in enumerate(P):
        cv2.circle(lab, (int(round(x)), int(round(y))), max(1, int(0.22 * pitch)), int(k), -1)
    a1 = pitch * np.array([math.cos(ang), math.sin(ang)])   # +i: along the rows (right)
    a2 = np.array([-a1[1], a1[0]])                          # +j: down the columns (toward the door)
    nb = {}
    for di, dj in steps:
        q = np.round(P + di * a1 + dj * a2).astype(int)
        ok = (q[:, 0] >= 0) & (q[:, 0] < shape[1]) & (q[:, 1] >= 0) & (q[:, 1] < shape[0])
        nb[(di, dj)] = np.where(ok, lab[q[:, 1].clip(0, shape[0] - 1), q[:, 0].clip(0, shape[1] - 1)], -1)
    return nb


def grid_step(P: np.ndarray, nb: dict) -> tuple[float, float]:
    """Pitch and row angle measured from linked neighbours (median step; steps down the columns turned to match)."""
    turn = {(1, 0): lambda v: v, (-1, 0): lambda v: -v, (0, 1): lambda v: v @ [[0, -1], [1, 0]], (0, -1): lambda v: v @ [[0, 1], [-1, 0]]}
    v = np.vstack([turn[s](P[nb[s][nb[s] >= 0]] - P[nb[s] >= 0]) for s in UNIT])
    a1 = np.median(v, axis=0)
    return float(np.hypot(*a1)), float(math.atan2(a1[1], a1[0]))


def grids(nb: dict, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Peaks linked by grid steps, as components (label per peak) with integer site indices (i right, j down)."""
    comp, ij = np.full(n, -1), np.zeros((n, 2), int)
    for s in range(n):
        if comp[s] >= 0:
            continue
        comp[s], todo = s, [s]
        while todo:
            k = todo.pop()
            for (di, dj), m in nb.items():
                q = m[k]
                if q >= 0 and comp[q] < 0:
                    comp[q], ij[q] = s, ij[k] + (di, dj)
                    todo.append(q)
    return comp, ij


def fit_similarity(XY: np.ndarray, UV: np.ndarray, tol: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Least squares UV = [[a, b], [b, -a]] XY + t (plate mm, y back, to picture px, y down), dropping points
    more than max(tol, 3 robust sigmas) px off until none are. Returns the 2 x 3 affine, kept mask, residuals."""
    keep = np.ones(len(XY), bool)
    for _ in range(10):
        x, y = XY[keep].T
        M = np.zeros((2 * len(x), 4))
        M[0::2, 0], M[0::2, 1], M[0::2, 2] = x, y, 1
        M[1::2, 0], M[1::2, 1], M[1::2, 3] = -y, x, 1
        (a, b, tu, tv), *_ = np.linalg.lstsq(M, UV[keep].ravel(), rcond=None)
        T = np.array([[a, b, tu], [b, -a, tv]])
        res = np.hypot(*(XY @ T[:, :2].T + T[:, 2] - UV).T)
        new = res <= max(tol, 3 * 1.4826 * float(np.median(res[keep])))
        if (new == keep).all() or new.sum() < 6:
            break
        keep = new
    return T, keep, res


def apply(T: np.ndarray, XY) -> np.ndarray:
    return np.asarray(XY, float) @ T[:, :2].T + T[:, 2]


def sample(R: np.ndarray, uv: np.ndarray) -> np.ndarray:
    """R at (rounded) map positions, 0 off the map."""
    q = np.round(uv).astype(int)
    ok = (q[:, 0] >= 0) & (q[:, 0] < R.shape[1]) & (q[:, 1] >= 0) & (q[:, 1] < R.shape[0])
    return np.where(ok, R[q[:, 1].clip(0, R.shape[0] - 1), q[:, 0].clip(0, R.shape[1] - 1)], 0.0)


def blocks(R: np.ndarray, P: np.ndarray, w: np.ndarray, comp: np.ndarray, ij: np.ndarray, pitch: float) -> list[dict]:
    """For each linked grid, the 12 x 8 window of its sites with the most ring response, read off the map at
    every site: a well scores plus, an empty site (the plate's frame and labels sit one pitch outside the
    wells) minus, a site off the picture nothing, so a plate cut off by the frame is placed toward the cut.
    Returns each window's plate mm -> map px similarity, wells in it, on/off-site response ratio, and its mean
    response in units of the map's noise (z, comparable between ring sizes)."""
    h = max(1, round(0.08 * pitch))                    # take the best within a few px of each site
    Rm = cv2.dilate(R, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * h + 1, 2 * h + 1)))
    noise = 1.4826 * float(np.median(np.abs(R - np.median(R)))) + 1e-9
    out = []
    for c in np.unique(comp):
        k = comp == c
        if k.sum() < 12:
            continue
        T, keep, _ = fit_similarity(ij[k] * [1, -1], P[k], 0.15 * pitch)
        base = 0.5 * float(np.median(w[k][keep]))     # half a typical well's response
        lo, hi = ij[k][keep].min(0) - (11, 7), ij[k][keep].max(0) + (11, 7)
        I, J = np.meshgrid(np.arange(lo[0], hi[0] + 1), np.arange(lo[1], hi[1] + 1), indexing="ij")
        uv = apply(T, np.column_stack([I.ravel(), -J.ravel()]))
        inside = (uv[:, 0] > 0.3 * pitch) & (uv[:, 0] < R.shape[1] - 0.3 * pitch) & (uv[:, 1] > 0.3 * pitch) & (uv[:, 1] < R.shape[0] - 0.3 * pitch)
        val = sample(Rm, uv)
        score = np.where(inside, val - base, 0.0).reshape(I.shape)
        found = (inside & (val > base)).reshape(I.shape)
        best = max(((score[a:a + 12, b:b + 8].sum(), a, b) for a in range(I.shape[0] - 11) for b in range(I.shape[1] - 7)))
        _, a, b = best
        i0, j0 = lo[0] + a, lo[1] + b
        # The grid sites must out-respond the points half a pitch off them (else this is the gaps between wells).
        bi, bj = np.meshgrid(np.arange(i0, i0 + 12), np.arange(j0, j0 + 8), indexing="ij")
        on = sample(Rm, apply(T, np.column_stack([bi.ravel(), -bj.ravel()])))
        off = max(np.median(sample(Rm, apply(T, np.column_stack([bi.ravel() + di, -(bj.ravel() + dj)]))))
                  for di, dj in ((0.5, 0), (0, 0.5), (0.5, 0.5)))
        # plate mm -> map px: column c = i - i0, row r = j - j0, x = 9 (c - 5.5), y = 9 (3.5 - r)
        Tp = np.column_stack([T[:, :2] / PITCH, apply(T, [[i0 + 5.5, -(j0 + 3.5)]])[0]])
        z = float(np.where(inside.reshape(I.shape), val.reshape(I.shape), 0)[a:a + 12, b:b + 8].sum()) / 96 / noise
        on = float(np.median(on))
        out.append({"T": Tp, "wells": int(found[a:a + 12, b:b + 8].sum()),
                    "on_off": float(on / max(off, 0.1 * on)) if on > 0 else 0.0, "z": z})
    return out


def find_grid(img: np.ndarray, near: tuple[float, float], s_guess: float | None) -> tuple[np.ndarray, dict]:
    """A rough plate mm -> still px similarity. For each ring size: link the ring centres into square grids,
    measure their pitch and angle, and take each grid's best 12 x 8 block. Of the blocks that stand well above
    the map's noise (z; 96 sites at most, so fine texture can't win by sheer numbers), overlapping blocks are
    one grid: keep each grid's strongest, drop grids under 35 % of the best, and take the one nearest `near`
    (px), i.e. the plate in that slot and not the tip rack next door."""
    if s_guess:
        radii = WELL_R * s_guess * 1.1 ** np.arange(-2, 3)
    else:   # 6-60 mm lenses: 6.4-64 px/mm at the plate top
        radii = 20.0 * 1.12 ** np.arange(22)
    found = []
    for r in radii:
        f = max(1.0, r / RING_PX)
        R, fx, fy = ring_map(img, f, r)
        pitch = r / math.sqrt(fx * fy) * PITCH / WELL_R
        P, w = peaks(R, max(2, int(0.4 * pitch)))
        ang = grid_angle(P, w, pitch) if len(P) >= 12 else None
        if ang is None:
            continue
        for _ in range(2):                     # the ring size is a guess to ~6 %: link again at the measured pitch
            nb = neighbours(P, R.shape, pitch, ang, UNIT)
            if sum(int((m >= 0).sum()) for m in nb.values()) < 16:
                break
            pitch, ang = grid_step(P, nb)
        else:
            comp, ij = grids(neighbours(P, R.shape, pitch, ang, STEPS), len(P))
            D, o = np.diag([fx, fy]), np.array([0.5 * fx - 0.5, 0.5 * fy - 0.5])     # map px -> full-res px
            for c in blocks(R, P, w, comp, ij, pitch):
                if c["wells"] >= 24 and c["on_off"] > 1.3:
                    c["T"] = np.column_stack([D @ c["T"][:, :2], D @ c["T"][:, 2] + o])
                    c["ring_radius_px"], c["dist_px"] = float(r), float(math.dist(c["T"][:, 2], near))
                    found.append(c)
    if not found:
        raise SystemExit("No 12 x 8 well grid found; pass --focal (and --near) closer to the truth")
    # Blocks that overlap are one grid seen at several ring sizes (or misplaced at a poor one): keep the strongest.
    groups = []
    for c in sorted(found, key=lambda c: -c["z"]):
        p = PITCH * math.hypot(*c["T"][:, 0])
        if not any(abs(g["T"][0, 2] - c["T"][0, 2]) < 9 * p and abs(g["T"][1, 2] - c["T"][1, 2]) < 6 * p for g in groups):
            groups.append(c)
    good = [g for g in groups if g["z"] >= 0.35 * groups[0]["z"]]
    pick = min(good, key=lambda c: c["dist_px"])
    return pick["T"], {"grids_seen": len(good), "picked": {k: round(v, 2) if isinstance(v, float) else v for k, v in pick.items() if k != "T"}}


def rim_gradient(img: np.ndarray, s: float) -> tuple[np.ndarray, np.ndarray]:
    """Grey-level gradient (x, y) of the still, smoothed to the scale of a rim (s px/mm)."""
    g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), max(1.0, 0.12 * s))
    return cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1)


def rim_centres(grad: tuple, T: np.ndarray, r_rim: float | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Each well's centre from the outer edge of its rim: the outermost circle round a well, and the one feature
    certainly at the plate's top (the well's bottom shows inside it, shifted toward the picture centre by
    parallax, about 2 mm on the wide view). On 120 rays from where T puts the well, take the outermost strong
    edge between 0.8 and 1.36 opening radii; or, given the rim's radius r_rim (px, from a first pass), the
    strongest edge within 0.12 opening radii of the circle so far. Fit a circle (to a quarter px, dropping
    points off it), look again from it, and repeat until it settles, so the answer leans less on T.
    Returns centres and radii in full-res px (nan where a well is off the picture or no circle is found)."""
    s, (gx, gy) = math.hypot(T[0, 0], T[1, 0]), grad
    ang = np.linspace(0, 2 * math.pi, 120, endpoint=False)
    cs, sn = np.cos(ang)[:, None], np.sin(ang)[:, None]
    w = 0.12 * WELL_R * s
    uv, rad = np.full((96, 2), np.nan), np.full(96, np.nan)
    for n, c0 in enumerate(apply(T, WELLS)):
        (cx, cy), R = c0, r_rim
        for _ in range(3 if r_rim is None else 8):
            rs = np.arange(0.8 * WELL_R * s, 1.36 * WELL_R * s, 0.25) if r_rim is None else np.arange(R - w, R + w, 0.25)
            X, Y = (cx + cs * rs).astype(np.float32), (cy + sn * rs).astype(np.float32)
            if X.min() < 1 or Y.min() < 1 or X.max() > PX[0] - 2 or Y.max() > PX[1] - 2:
                R = None
                break
            e = np.abs(cv2.remap(gx, X, Y, cv2.INTER_LINEAR) * cs + cv2.remap(gy, X, Y, cv2.INTER_LINEAR) * sn)
            if r_rim is None:
                m = (e[:, 1:-1] >= e[:, :-2]) & (e[:, 1:-1] >= e[:, 2:]) & (e[:, 1:-1] > 0.4 * e.max(axis=1, keepdims=True))
                ok, i = m.any(axis=1), e.shape[1] - 2 - np.argmax(m[:, ::-1], axis=1)   # outermost such peak
            else:
                ok, i = np.ones(len(e), bool), np.argmax(e[:, 1:-1], axis=1) + 1       # strongest in the band
            a, b, c = (e[np.arange(len(e)), i + d] for d in (-1, 0, 1))
            r = rs[i] + 0.25 * np.clip(0.5 * (a - c) / np.minimum(a - 2 * b + c, -1e-6), -0.5, 0.5)
            P = np.column_stack([cx + r * cs[:, 0], cy + r * sn[:, 0]])[ok]
            for _ in range(4):                                         # algebraic circle fit, outliers dropped
                if len(P) < 40:
                    break
                (x0, y0, k), *_ = np.linalg.lstsq(np.column_stack([2 * P, np.ones(len(P))]), (P ** 2).sum(axis=1), rcond=None)
                Rf = math.sqrt(max(k + x0 * x0 + y0 * y0, 0.0))
                d = np.abs(np.hypot(P[:, 0] - x0, P[:, 1] - y0) - Rf)
                P = P[d <= max(0.3, 2.5 * float(np.median(d)))]
            if len(P) < 40 or math.dist((x0, y0), c0) > 0.15 * PITCH * s or not 0.8 * WELL_R * s < Rf < 1.4 * WELL_R * s:
                R = None
                break
            moved = math.dist((x0, y0), (cx, cy))
            (cx, cy), R = (x0, y0), Rf
            if r_rim is not None and moved < 0.05:
                break
        if R is not None:
            uv[n], rad[n] = (cx, cy), R
    return uv, rad


def fit_rims(grad: tuple, T: np.ndarray) -> tuple:
    """Centre the wells on their rims and refit the similarity, until the fit settles (each pass keeps some of
    the last pass's error, as a well can sit between its rim and the parallax-shifted circles inside it)."""
    r_rim = None
    for _ in range(15):
        uv, rad = rim_centres(grad, T, r_rim)
        ok = ~np.isnan(uv[:, 0])
        if ok.sum() < 12:
            raise SystemExit(f"Only {ok.sum()} wells' rims found; pass --near and --focal closer to the truth")
        T_old, (T, keep, res) = T, fit_similarity(WELLS[ok], uv[ok], 0.1 * math.hypot(T[0, 0], T[1, 0]))
        r_rim = float(np.median(rad[ok]))
        if np.abs(apply(T, WELLS) - apply(T_old, WELLS)).max() < 0.1:
            break
    return T, ok, keep, res[keep], r_rim


def rim_strength(grad: tuple, T: np.ndarray, r: float) -> float:
    """How much circle of radius r px there is round the wells T puts, summed over those in view: edge strength
    running along the circle less that crossing it (|g| cos 2(theta - phi), as in ring_map), so an edge-rich
    patch such as the plate's frame, letters and glare scores about nothing."""
    ang = np.linspace(0, 2 * math.pi, 120, endpoint=False)
    c = apply(T, WELLS)
    X, Y = (c[:, :1] + r * np.cos(ang)).astype(np.float32), (c[:, 1:] + r * np.sin(ang)).astype(np.float32)
    gx, gy = cv2.remap(grad[0], X, Y, cv2.INTER_LINEAR), cv2.remap(grad[1], X, Y, cv2.INTER_LINEAR)
    gr, gt = gx * np.cos(ang) + gy * np.sin(ang), gy * np.cos(ang) - gx * np.sin(ang)
    e = (gr * gr - gt * gt) / (np.hypot(gr, gt) + 1e-3)
    inside = (X.min(1) > 0) & (Y.min(1) > 0) & (X.max(1) < PX[0] - 1) & (Y.max(1) < PX[1] - 1)
    return float(e.mean(axis=1)[inside].sum())


def measure_plate(img: np.ndarray, args: argparse.Namespace) -> None:
    uc, vc = (PX[0] - 1) / 2, (PX[1] - 1) / 2
    near, s_guess, deck = (uc, vc), None, None
    k_top = PUPIL_ABOVE_DECK / PLATE_TOP      # the plate's top is nearer the lens: it looks this much bigger
    if args.focal:
        s_guess = args.focal / (PIXEL_MM * PLATE_TOP)
    if args.deck_fit:                         # deck mm -> px at deck height, then scaled about the picture centre
        deck = np.array(json.loads(Path(args.deck_fit).read_text())["still_to_deck"])
        u, v = apply(deck, [SLOTS[args.plate]])[0]
        near = (uc + k_top * (u - uc), vc + k_top * (v - vc))
        s_guess = s_guess or k_top * math.hypot(deck[0, 0], deck[1, 0])
    if args.near:
        near = tuple(float(c) for c in args.near.split(","))
    T, info = find_grid(img, near, s_guess)
    grad = rim_gradient(img, math.hypot(T[0, 0], T[1, 0]))
    T, ok, keep, res, r_rim = fit_rims(grad, T)
    # The plate's frame and row letters sit one pitch outside the wells and can ring nearly as well as a well:
    # step the block a column or a row while that puts more rim under the fitted circles (only the column or
    # row that changes counts: real rims against frame and letters).
    shifts = [(0, 0), (PITCH, 0), (-PITCH, 0), (0, PITCH), (0, -PITCH)]
    info["stepped_mm"] = [0.0, 0.0]
    for _ in range(3):
        cand = [np.column_stack([T[:, :2], apply(T, [d])[0]]) for d in shifts]
        k = int(np.argmax([rim_strength(grad, t, r_rim) for t in cand]))
        if k == 0:
            break
        info["stepped_mm"] = [info["stepped_mm"][0] + shifts[k][0], info["stepped_mm"][1] + shifts[k][1]]
        T, ok, keep, res, r_rim = fit_rims(grad, cand[k])
    info["rim_radius_mm"] = round(r_rim / math.hypot(T[0, 0], T[1, 0]), 2)

    a, b = T[0, 0], T[1, 0]
    s = math.hypot(a, b)
    rot = math.degrees(math.atan2(b, a))
    off = np.linalg.solve(T[:, :2], np.array([uc, vc]) - T[:, 2])        # the picture's centre in plate mm
    field = (PX[0] / s, PX[1] / s)
    focal = SENSOR[0] * PLATE_TOP / field[0]
    hw, hh = PLATE[0] / 2, PLATE[1] / 2
    corners = apply(T, [(-hw, hh), (hw, hh), (hw, -hh), (-hw, -hh)])
    margins = {"left": (corners[:, 0].min() + 0.5) / s, "right": (PX[0] - 0.5 - corners[:, 0].max()) / s,
               "back_top": (corners[:, 1].min() + 0.5) / s, "front_bottom": (PX[1] - 0.5 - corners[:, 1].max()) / s}
    t_field = PLATE[0] + 2 * args.target_margin
    t_focal = SENSOR[0] * PLATE_TOP / t_field
    fill = (PLATE[0] / t_field, PLATE[1] / (t_field * PX[1] / PX[0]))
    rms = math.sqrt(float(np.mean(res ** 2))) / s

    out = {
        "still": str(Path(args.still).name),
        "still_path": str(Path(args.still).resolve().relative_to(HERE.parent)) if Path(args.still).resolve().is_relative_to(HERE.parent) else str(args.still),
        "method": "96-well grid: circles fitted to the outer edges of the wells' rims, least-squares similarity to the 9 mm SBS grid",
        "slot": args.plate,
        "search": info,
        "wells_found": int(ok.sum()),
        "wells_used": int(keep.sum()),
        "fit_rms_mm": round(rms, 3),
        "fit_max_mm": round(float(res.max()) / s, 3),
        "px_per_mm_at_plate_top": round(s, 3),
        "field_at_plate_top_mm": [round(field[0], 1), round(field[1], 1)],
        "focal_mm": round(focal, 2),
        "focal_note": f"pinhole model, pupil {PLATE_TOP:.2f} mm above the plate's top ({PUPIL_ABOVE_DECK:.1f} above the deck, plate 14.35 tall); about +-2 %",
        "rotation_deg": round(rot, 2),
        "axis_offset_mm": [round(off[0], 2), round(off[1], 2)],
        "axis_offset_note": "where the picture's centre is, from the plate centre (the well grid's centre); +x right, +y back (seen from the door)",
        "margins_mm": {k: round(v, 1) for k, v in margins.items()},
        "margins_note": f"from the plate's outline ({PLATE[0]} x {PLATE[1]} mm) to the picture's edges, at the plate top; negative = plate cut off",
        "px_per_well": round(2 * WELL_R * s, 1),
        "target": {"margin_mm": args.target_margin, "field_w_mm": round(t_field, 2), "focal_mm": round(t_focal, 2),
                   "plate_fills": [round(fill[0], 3), round(fill[1], 3)]},
        "to_do": {
            "slide_mount_mm": {"toward_door": round(off[1], 1), "to_the_right": round(-off[0], 1)},
            "turn_mount_deg": {"clockwise_seen_from_above": round(rot, 2)},
            "zoom": {"zoom in" if t_focal > focal else "zoom out": f"from {focal:.2f} to {t_focal:.2f} mm",
                     "plate_fills_width": round(fill[0], 3)},
        },
        "plate_to_still": [[round(float(x), 6) for x in row] for row in T],
        "plate_to_still_note": "2 x 3 affine from plate mm (origin at the plate centre, x right toward column 12, y back toward row A) to still pixels",
    }
    if deck is not None:                      # the plate centre back at deck height, in deck mm, against its slot's centre
        u, v = T[:, 2]
        X = np.linalg.solve(deck[:, :2], np.array([uc + (u - uc) / k_top, vc + (v - vc) / k_top]) - deck[:, 2])
        out["plate_vs_slot_mm"] = [round(float(X[0] - SLOTS[args.plate][0]), 2), round(float(X[1] - SLOTS[args.plate][1]), 2)]
        out["plate_vs_slot_note"] = f"plate centre minus slot {args.plate}'s centre, deck mm through {Path(args.deck_fit).name} (axis assumed vertical)"
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n")

    # The still with the fitted wells and plate outline, the picture and plate centres, and the target box.
    vis = img.copy()
    blue, orange, green = (171, 92, 28), (42, 98, 212), (60, 160, 40)
    for u, v in apply(T, WELLS):
        cv2.circle(vis, (int(round(u)), int(round(v))), int(round(WELL_R * s)), blue, 3, cv2.LINE_AA)
    cv2.polylines(vis, [np.round(corners).astype(np.int32)], True, blue, 8, cv2.LINE_AA)
    bw, bh = fill[0] * PX[0] / 2, fill[1] * PX[1] / 2
    cv2.rectangle(vis, (int(uc - bw), int(vc - bh)), (int(uc + bw), int(vc + bh)), green, 8, cv2.LINE_AA)
    pu, pv = T[:, 2]
    for (x, y), col in (((uc, vc), orange), ((pu, pv), blue)):
        cv2.line(vis, (int(x) - 120, int(y)), (int(x) + 120, int(y)), col, 10)
        cv2.line(vis, (int(x), int(y) - 120), (int(x), int(y) + 120), col, 10)
    cv2.arrowedLine(vis, (int(uc), int(vc)), (int(pu), int(pv)), orange, 8, tipLength=0.25)
    text = (f"picture centre (orange) is {abs(off[1]):.1f} mm {'behind' if off[1] > 0 else 'in front of'} and "
            f"{abs(off[0]):.1f} mm {'left' if off[0] < 0 else 'right'} of the plate centre (blue); turned {rot:+.2f} deg; "
            f"{s:.2f} px/mm, zoom about {focal:.2f} mm; green = plate at {t_focal:.1f} mm; {keep.sum()} wells, rms {rms:.2f} mm")
    scale = min(2.0, 2.0 * (PX[0] - 140) / cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 5)[0][0])
    band = vis[PX[1] - 150:, :].astype(np.float32)
    vis[PX[1] - 150:, :] = (band * 0.35).astype(np.uint8)
    cv2.putText(vis, text, (40, PX[1] - 50), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 5, cv2.LINE_AA)
    small = cv2.resize(vis, (PX[0] // 2, PX[1] // 2), interpolation=cv2.INTER_AREA)
    cv2.imwrite(args.render, small, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(json.dumps({k: out[k] for k in ("search", "px_per_mm_at_plate_top", "field_at_plate_top_mm", "focal_mm", "rotation_deg",
                                          "axis_offset_mm", "margins_mm", "px_per_well", "target", "to_do")
                      + (("plate_vs_slot_mm",) if deck is not None else ())}, indent=1))
    print(f"fit rms {rms:.3f} mm over {keep.sum()} of 96 wells, max {out['fit_max_mm']:.3f} mm")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("still")
    ap.add_argument("--guess", help="X,Y mm: the picture centre relative to the deck centre (+X right, +Y back)")
    ap.add_argument("--focal", type=float, help="guessed focal length, mm")
    ap.add_argument("--rotation", type=float, default=0.0, help="guessed rotation, degrees")
    ap.add_argument("--search", type=int, default=200, help="search half-width around each predicted rail, px")
    ap.add_argument("--plate", type=int, choices=range(1, 13), metavar="SLOT",
                    help="plate mode: measure from the 96-well plate in this deck slot")
    ap.add_argument("--deck-fit", help="plate mode: a rail-mode JSON of the same camera state, to predict where the plate is")
    ap.add_argument("--near", help="plate mode: U,V px, roughly where the plate's centre is (default: the picture centre)")
    ap.add_argument("--target-slot", type=int, choices=range(1, 13), default=7, metavar="SLOT",
                    help="rail mode: the slot whose plate the camera is to look straight down at (default 7)")
    ap.add_argument("--target-margin", type=float, default=5.0,
                    help="deck to leave left and right of the plate at the target zoom, mm (default 5)")
    ap.add_argument("--out", help="default ../exports/lid_camera_setup.json (plate mode: lid_camera_plate.json)")
    ap.add_argument("--render", help="default ../renders/lid_camera_now.jpg (plate mode: lid_camera_plate.jpg)")
    args = ap.parse_args()
    args.out = args.out or str(EXPORTS / ("lid_camera_plate.json" if args.plate else "lid_camera_setup.json"))
    args.render = args.render or str(RENDERS / ("lid_camera_plate.jpg" if args.plate else "lid_camera_now.jpg"))

    img = cv2.imread(args.still)
    if img is None or img.shape[1::-1] != PX:
        raise SystemExit(f"{args.still}: need a {PX[0]} x {PX[1]} still")
    if args.plate:
        return measure_plate(img, args)
    gray = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.5)

    prev = json.loads(Path(args.out).read_text()) if Path(args.out).exists() else {}
    if args.guess or args.focal or "fit" not in prev:
        gx, gy = (float(v) for v in (args.guess or "0,0").split(","))
        prior = guess_fit((gx, gy), args.focal or 9.0, args.rotation)
    else:
        prior = prev["fit"]
    fit, found = measure(gray, prior, args.search)
    fit, found = measure(gray, fit, 60)          # second pass, tight windows around the first fit

    A, B, C, F = fit["A"], fit["B"], fit["C"], fit["F"]
    s = 1 / math.hypot(A, B)
    rot = math.degrees(math.atan2(B, A))
    uc, vc = (PX[0] - 1) / 2, (PX[1] - 1) / 2
    off = (A * uc + B * vc + C, B * uc - A * vc + F)
    field = (PX[0] / s, PX[1] / s)
    focal = SENSOR[0] * PUPIL_ABOVE_DECK / field[0]
    # The goal: straight down at the plate in --target-slot, centred, --target-margin mm of deck left and right of it.
    tx, ty = SLOTS[args.target_slot]
    to_slot = (DECK_C[0] + off[0] - tx, DECK_C[1] + off[1] - ty)      # the picture's centre from the slot's centre
    t_field = PLATE[0] + 2 * args.target_margin
    t_focal = SENSOR[0] * PLATE_TOP / t_field
    # Slots in view now: fraction of each slot's area inside the picture (sampled).
    in_view = {}
    for n, (cx, cy) in SLOTS.items():
        xs, ys = np.meshgrid(np.linspace(cx - 64, cx + 64, 33), np.linspace(cy - 43, cy + 43, 23))
        X, Y = xs.ravel() - DECK_C[0] - C, ys.ravel() - DECK_C[1] - F
        m = np.linalg.inv(np.array([[A, B], [B, -A]]))
        u, v = m @ np.vstack([X, Y])
        in_view[n] = round(float(np.mean((u >= 0) & (u < PX[0]) & (v >= 0) & (v < PX[1]))), 2)

    out = {
        "still": str(Path(args.still).name),
        "still_path": str(Path(args.still).resolve().relative_to(HERE.parent)) if Path(args.still).resolve().is_relative_to(HERE.parent) else str(args.still),
        "method": "rail centre lines (midpoints of their two dark edges), least-squares similarity to Opentrons' slot pitch",
        "rails_used": found,
        "fit": fit,
        "px_per_mm_at_deck": round(s, 3),
        "field_at_deck_mm": [round(field[0], 1), round(field[1], 1)],
        "focal_mm": round(focal, 2),
        "focal_note": f"pinhole model, pupil {PUPIL_ABOVE_DECK:.1f} mm above the deck (coverage.py); about +-2 %",
        "rotation_deg": round(rot, 2),
        "axis_offset_mm": [round(off[0], 1), round(off[1], 1)],
        "axis_offset_note": "where the picture's centre is on the deck, from the deck centre (midpoint of slots 5 and 8); +x right, +y back (seen from the door)",
        "slots_in_view": in_view,
        "target": {"slot": args.target_slot, "slot_centre_mm": [tx, ty], "margin_mm": args.target_margin,
                   "field_at_plate_top_mm": [round(t_field, 2), round(t_field * PX[1] / PX[0], 2)], "focal_mm": round(t_focal, 2),
                   "plate_fills": [round(PLATE[0] / t_field, 3), round(PLATE[1] / (t_field * PX[1] / PX[0]), 3)]},
        "target_note": f"looking straight down at the plate in slot {args.target_slot}, centred, with margin_mm of deck left and right of it at the plate's top (14.35 mm up)",
        "axis_offset_from_target_mm": [round(to_slot[0], 1), round(to_slot[1], 1)],
        "deck_span_mm": list(DECK_SPAN),
        "to_do": {
            "slide_mount_mm": {"toward_door": round(to_slot[1], 1), "to_the_right": round(-to_slot[0], 1)},
            "turn_mount_deg": {"clockwise_seen_from_above": round(rot, 2)},
            "zoom": {"zoom in" if t_focal > focal else "zoom out": f"from {focal:.2f} to {t_focal:.2f} mm"},
        },
        "still_to_deck": None,
    }
    m = np.linalg.inv(np.array([[A, B], [B, -A]]))
    t = m @ np.array([-DECK_C[0] - C, -DECK_C[1] - F])
    out["still_to_deck"] = [[float(m[0, 0]), float(m[0, 1]), float(t[0])], [float(m[1, 0]), float(m[1, 1]), float(t[1])]]
    out["still_to_deck_note"] = "2 x 3 affine from deck mm (x right, y back, slot 1's front-left corner at 0,0) to still pixels"
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n")

    # The still with the slots drawn where the fit puts them, the picture centre and the target slot's centre.
    vis = img.copy()
    for n, (cx, cy) in SLOTS.items():
        corners = [to_px(fit, cx + dx, cy + dy) for dx, dy in ((-64, -43), (64, -43), (64, 43), (-64, 43))]
        cv2.polylines(vis, [np.array(corners, np.int32)], True, (171, 92, 28), 6)
        u, v = to_px(fit, cx, cy)
        cv2.putText(vis, str(n), (int(u) - 60, int(v) + 40), cv2.FONT_HERSHEY_SIMPLEX, 4, (171, 92, 28), 10)
    du, dv = to_px(fit, tx, ty)
    for (x, y), col in (((uc, vc), (42, 98, 212)), ((du, dv), (171, 92, 28))):
        cv2.line(vis, (int(x) - 120, int(y)), (int(x) + 120, int(y)), col, 10)
        cv2.line(vis, (int(x), int(y) - 120), (int(x), int(y) + 120), col, 10)
    cv2.arrowedLine(vis, (int(uc), int(vc)), (int(du), int(dv)), (42, 98, 212), 8, tipLength=0.25)
    text = (f"picture centre (orange) is {abs(to_slot[0]):.0f} mm {'left' if to_slot[0] < 0 else 'right'} and "
            f"{abs(to_slot[1]):.0f} mm {'behind' if to_slot[1] > 0 else 'in front of'} slot {args.target_slot}'s centre (blue); "
            f"turned {rot:+.1f} deg; zoom about {focal:.2f} mm, target {t_focal:.1f} mm")
    band = vis[PX[1] - 150:, :].astype(np.float32)
    vis[PX[1] - 150:, :] = (band * 0.35).astype(np.uint8)
    cv2.putText(vis, text, (40, PX[1] - 50), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 5, cv2.LINE_AA)
    small = cv2.resize(vis, (PX[0] // 2, PX[1] // 2), interpolation=cv2.INTER_AREA)
    cv2.imwrite(args.render, small, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(json.dumps({k: out[k] for k in ("rails_used", "px_per_mm_at_deck", "field_at_deck_mm", "focal_mm", "rotation_deg",
                                          "axis_offset_mm", "slots_in_view", "target", "axis_offset_from_target_mm", "to_do")}, indent=1))
    print(f"fit rms {fit['rms_mm']:.2f} mm, max {fit['max_mm']:.2f} mm")


if __name__ == "__main__":
    main()
