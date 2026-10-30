#!/usr/bin/env python3
"""Which side of focus is the lid camera on? Fit the iris-shaped blur spot in the stills.

    python focus_side.py               # fit (about 3 min) and draw
    python focus_side.py --plot-only   # redraw from focus_side.json

A defocused point spreads into a copy of the iris opening, a rounded triangle on this lens when the
iris is partly closed. While the picture still forms behind the sensor, the copy is upright. Once
it forms in front of the sensor the rays have crossed, and the copy is turned 180 degrees. So the
way the triangle points says whether the lens needs more room from the sensor or less.

Each paint-filled well is a uniform disc, so its image is that disc convolved with the blur spot.
For each well this fits the disc radius, spot size, extra Gaussian softness, centre, contrast and
background three times: spot apex up, apex down, and a round spot of the same area. The 18:08 UTC
still (knurled ring screwed fully in, focus thumbscrew at NEAR, so the picture forms behind the
sensor) calibrates which way is which: there the spot is a large upright triangle.

Reads the half-resolution stills in frames/2026-10-23/ and writes focus_side.json and
focus_side.png there. Coordinates in WELLS are full-resolution (4056 x 3040) pixels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Rectangle
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import least_squares
from scipy.signal import fftconvolve

HERE = Path(__file__).resolve().parent
OUT = HERE / "frames/2026-10-23"
STILLS = {
    "18:08": ("still_1808Z_focus_at_near.jpg", "ring screwed fully in, focus thumbscrew at NEAR"),
    "18:54": ("still_1854Z_ring_all_the_way_out.jpg", "knurled ring all the way out"),
    "19:04": ("still_1904Z_ring_all_the_way_out.jpg", "the same, after the Pi's 13:00 MDT reboot"),
}
WELLS = {  # (paint, x, y), full-resolution px
    "18:08": [("yellow", 907, 1867), ("red", 1779, 1856), ("yellow", 621, 2437), ("red", 1207, 2437)],
    "18:54": [("yellow", 629, 2013), ("red", 1697, 2002), ("red", 1001, 2717), ("yellow", 293, 2716)],
    "19:04": [("yellow", 629, 2013), ("red", 1697, 2002), ("red", 1001, 2717), ("yellow", 293, 2716)],
}
FULL_PER_FILE = 2   # the committed stills are half resolution
DS = 2              # fit on a further 2x downsampled crop, for speed
SHAPES = ("up", "down", "round")


def paint(rgb: np.ndarray, kind: str) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(float) for i in range(3))
    return (r + g) / 2 - b if kind == "yellow" else r - (g + b) / 2


def spot(side: float, shape: str, soft: float, n: int) -> np.ndarray:
    """Blur spot of the given triangle side (px). 'up': apex towards the top of the picture."""
    yy, xx = np.mgrid[-(n // 2):n // 2 + 1, -(n // 2):n // 2 + 1].astype(float)
    if shape == "round":
        k = (np.hypot(xx, yy) <= side * np.sqrt(np.sqrt(3) / (4 * np.pi))).astype(float)
    else:
        h = side * np.sqrt(3) / 2
        y = yy if shape == "up" else -yy
        k = ((y <= h / 3) & (y >= -2 * h / 3) & (np.abs(xx) <= (y + 2 * h / 3) / max(h, 1e-6) * side / 2)).astype(float)
    if k.sum() == 0:
        k[n // 2, n // 2] = 1
    if soft > 0.3:
        k = ndi.gaussian_filter(k, soft)
    return k / k.sum()


def model(p: np.ndarray, shape: str, hw: tuple[int, int]) -> np.ndarray:
    cx, cy, R, s, soft, A, B = p
    yy, xx = np.mgrid[0:hw[0], 0:hw[1]]
    disc = np.clip(R - np.hypot(xx - cx, yy - cy) + 0.5, 0, 1)
    n = int(max(s, 3) * 1.2 + 6 * max(soft, 0.5)) // 2 * 2 + 1
    return B + A * fftconvolve(disc, spot(s, shape, soft, n), mode="same")


def fit_well(img: np.ndarray, kind: str, x: float, y: float) -> dict:
    """Fit one well; returns, per spot shape, rms residual and parameters in full-resolution px."""
    f = FULL_PER_FILE * DS
    half = 300 // FULL_PER_FILE
    xf, yf = int(x / FULL_PER_FILE), int(y / FULL_PER_FILE)
    crop = paint(img[max(0, yf - half):yf + half, max(0, xf - half):xf + half], kind)
    c = ndi.zoom(ndi.gaussian_filter(crop, DS / 2), 1 / DS, order=1)
    lo, hi = np.percentile(c, 3), np.percentile(c, 99.7)
    out = {}
    for shape in SHAPES:
        best = None
        for s0 in (40, 120, 250):
            p0 = [c.shape[1] / 2, c.shape[0] / 2, 130 / f, s0 / f, 1.0, hi - lo, lo]
            lb = [0, 0, 20 / f, 1, 0, 0, lo - abs(hi)]
            ub = [c.shape[1], c.shape[0], 400 / f, 700 / f, 80 / f, 3 * (hi - lo) + 1, hi]
            r = least_squares(lambda p: (model(p, shape, c.shape) - c).ravel(), p0, bounds=(lb, ub),
                              x_scale="jac", max_nfev=400)
            if best is None or r.cost < best.cost:
                best = r
        p = best.x
        side, soft = p[3] * f, p[4] * f
        out[shape] = {"rms": round(float(np.sqrt(2 * best.cost / c.size)), 3),
                      "disc_radius_px": round(float(p[2] * f), 1), "spot_side_px": round(float(side), 1),
                      "extra_softness_sigma_px": round(float(soft), 1),
                      # rms radius of the whole spot: triangle s^2/12 plus 2 sigma^2 for the softness
                      "spot_rms_radius_px": round(float(np.sqrt(side ** 2 / 12 + 2 * soft ** 2)), 1)}
    return out


def triangle(ax, cx: float, cy: float, side: float, up: bool, **kw) -> None:
    h = side * np.sqrt(3) / 2
    sgn = -1 if up else 1   # image y points down
    pts = [(cx, cy + sgn * 2 * h / 3), (cx - side / 2, cy - sgn * h / 3), (cx + side / 2, cy - sgn * h / 3)]
    ax.add_patch(Polygon(pts, closed=True, fill=False, **kw))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plot-only", action="store_true", help="redraw the figure from focus_side.json")
    args = ap.parse_args()
    if args.plot_only:
        saved = json.loads((OUT / "focus_side.json").read_text())
        plot(saved["stills"], saved["summary"])
        return
    res = {}
    for t, (name, what) in STILLS.items():
        img = np.asarray(Image.open(OUT / name).convert("RGB"))
        wells = []
        for kind, x, y in WELLS[t]:
            fits = fit_well(img, kind, x, y)
            best = min(fits, key=lambda k: fits[k]["rms"])
            wells.append({"paint": kind, "x": x, "y": y, "best": best, "fits": fits})
            print(t, kind, (x, y), " | ".join(f"{k} {v['rms']:.3f}" for k, v in fits.items()), "->", best)
        res[t] = {"still": name, "state": what, "wells": wells}

    summary = {}
    for t, r in res.items():
        votes = {s: sum(w["best"] == s for w in r["wells"]) for s in SHAPES}
        margin = [round(w["fits"]["up"]["rms"] / w["fits"]["down"]["rms"], 3) for w in r["wells"]]
        win = max(votes, key=votes.get)
        size = float(np.median([w["fits"][win]["spot_rms_radius_px"] for w in r["wells"]]))
        summary[t] = {"votes": votes, "rms_up_over_down": margin, "spot_rms_radius_px_median": round(size, 1)}
    (OUT / "focus_side.json").write_text(json.dumps({"summary": summary, "stills": res}, indent=1) + "\n")
    plot(res, summary)


def plot(res: dict, summary: dict) -> None:
    # Figure: each still's red well, same full-resolution window, with the fitted spot drawn to scale.
    fig, axs = plt.subplots(1, 2, figsize=(11, 5.9))
    for ax, t in zip(axs, ("18:08", "18:54")):
        img = Image.open(OUT / STILLS[t][0]).convert("RGB")
        w = res[t]["wells"][1]                       # the upper red well
        best = summary[t]["votes"]
        win = max(best, key=best.get)
        f = w["fits"][win]
        half = 420
        box = tuple(int(v / FULL_PER_FILE) for v in (w["x"] - half, w["y"] - half, w["x"] + half, w["y"] + half))
        ax.imshow(img.crop(box), extent=(-half, half, half, -half))
        s = f["spot_side_px"]
        cx, cy = half - 0.62 * s - 20, -half + 0.62 * s + 20
        triangle(ax, cx, cy, s, win == "up", ec="white", lw=2.2)
        triangle(ax, cx, cy, s, win == "up", ec="#ff7800", lw=1.2)
        ax.text(cx, cy + 0.75 * s + 25, "fitted blur spot", color="white", ha="center", va="center", fontsize=9)
        ratios = summary[t]["rms_up_over_down"]
        worse = [max(r, 1 / r) for r in ratios]
        lean = f"fits {min(worse) - 1:.0%}-{max(worse) - 1:.0%} better than the other way up"
        side = "picture behind the sensor" if win == "up" else "probably just past focus (picture in front of the sensor)"
        ax.set_title(f"{t} UTC: {STILLS[t][1]}\nspot apex {win} ({summary[t]['votes'][win]}/{len(res[t]['wells'])} wells, "
                     f"{lean}):\n{side}; spot rms radius {summary[t]['spot_rms_radius_px_median']:.0f} px", fontsize=9.5)
        ax.add_patch(Rectangle((-half, half - 40), 200, 14, color="white"))
        ax.text(-half + 100, half - 55, "200 px", color="white", ha="center", fontsize=9)
        ax.set_xticks([]), ax.set_yticks([])
    fig.suptitle("Lid camera: the same red well before and after the knurled ring went all the way out "
                 "(full-resolution pixels)", fontsize=11, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / "focus_side.png", dpi=110)
    print("wrote", OUT / "focus_side.json", "and", OUT / "focus_side.png")


if __name__ == "__main__":
    main()
