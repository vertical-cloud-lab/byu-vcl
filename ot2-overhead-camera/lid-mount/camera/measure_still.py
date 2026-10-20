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

and from those, how far to slide and turn the mount. Writes ../exports/lid_camera_setup.json
and ../renders/lid_camera_now.jpg (the still, with the deck's slots drawn where the fit puts
them).

    python measure_still.py frames/2026-10-20/still_0358Z_lit.jpg

The search windows come from the previous fit in lid_camera_setup.json, widened by --search
pixels, so after a small move (up to ~20 mm) it finds the rails again. After a bigger one, pass
--guess X,Y (mm, where the picture's centre now is relative to the deck centre) and --focal.
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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("still")
    ap.add_argument("--guess", help="X,Y mm: the picture centre relative to the deck centre (+X right, +Y back)")
    ap.add_argument("--focal", type=float, help="guessed focal length, mm")
    ap.add_argument("--rotation", type=float, default=0.0, help="guessed rotation, degrees")
    ap.add_argument("--search", type=int, default=200, help="search half-width around each predicted rail, px")
    ap.add_argument("--out", default=str(EXPORTS / "lid_camera_setup.json"))
    ap.add_argument("--render", default=str(RENDERS / "lid_camera_now.jpg"))
    args = ap.parse_args()

    img = cv2.imread(args.still)
    if img is None or img.shape[1::-1] != PX:
        raise SystemExit(f"{args.still}: need a {PX[0]} x {PX[1]} still")
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
    wide = (SENSOR[0] * PUPIL_ABOVE_DECK / 8.0, SENSOR[1] * PUPIL_ABOVE_DECK / 8.0)
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
        "target_focal_mm": 8.0,
        "field_at_8mm_mm": [round(wide[0], 1), round(wide[1], 1)],
        "deck_span_mm": list(DECK_SPAN),
        "to_do": {
            "slide_mount_mm": {"toward_door": round(off[1], 1), "to_the_right": round(-off[0], 1)},
            "turn_mount_deg": {"clockwise_seen_from_above": round(rot, 2)},
            "front_back_margin_at_8mm_mm": round((wide[1] - DECK_SPAN[1]) / 2, 1),
        },
        "still_to_deck": None,
    }
    m = np.linalg.inv(np.array([[A, B], [B, -A]]))
    t = m @ np.array([-DECK_C[0] - C, -DECK_C[1] - F])
    out["still_to_deck"] = [[float(m[0, 0]), float(m[0, 1]), float(t[0])], [float(m[1, 0]), float(m[1, 1]), float(t[1])]]
    out["still_to_deck_note"] = "2 x 3 affine from deck mm (x right, y back, slot 1's front-left corner at 0,0) to still pixels"
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n")

    # The still with the slots drawn where the fit puts them, the picture centre and the deck centre.
    vis = img.copy()
    for n, (cx, cy) in SLOTS.items():
        corners = [to_px(fit, cx + dx, cy + dy) for dx, dy in ((-64, -43), (64, -43), (64, 43), (-64, 43))]
        cv2.polylines(vis, [np.array(corners, np.int32)], True, (171, 92, 28), 6)
        u, v = to_px(fit, cx, cy)
        cv2.putText(vis, str(n), (int(u) - 60, int(v) + 40), cv2.FONT_HERSHEY_SIMPLEX, 4, (171, 92, 28), 10)
    du, dv = to_px(fit, *DECK_C)
    for (x, y), col in (((uc, vc), (42, 98, 212)), ((du, dv), (171, 92, 28))):
        cv2.line(vis, (int(x) - 120, int(y)), (int(x) + 120, int(y)), col, 10)
        cv2.line(vis, (int(x), int(y) - 120), (int(x), int(y) + 120), col, 10)
    cv2.arrowedLine(vis, (int(uc), int(vc)), (int(du), int(dv)), (42, 98, 212), 8, tipLength=0.25)
    text = (f"picture centre (orange) is {abs(off[1]):.0f} mm {'behind' if off[1] > 0 else 'in front of'} and "
            f"{abs(off[0]):.0f} mm {'left' if off[0] < 0 else 'right'} of the deck centre (blue); "
            f"turned {rot:+.1f} deg; zoom about {focal:.2f} mm")
    band = vis[PX[1] - 150:, :].astype(np.float32)
    vis[PX[1] - 150:, :] = (band * 0.35).astype(np.uint8)
    cv2.putText(vis, text, (40, PX[1] - 50), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 5, cv2.LINE_AA)
    small = cv2.resize(vis, (PX[0] // 2, PX[1] // 2), interpolation=cv2.INTER_AREA)
    cv2.imwrite(args.render, small, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(json.dumps({k: out[k] for k in ("rails_used", "px_per_mm_at_deck", "field_at_deck_mm", "focal_mm",
                                          "rotation_deg", "axis_offset_mm", "slots_in_view", "to_do")}, indent=1))
    print(f"fit rms {fit['rms_mm']:.2f} mm, max {fit['max_mm']:.2f} mm")


if __name__ == "__main__":
    main()
