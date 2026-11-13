"""Measure the bright and dark spots in Ronnie's two SE images of the first
diamond-polished AlSi10Mg sample (Apreo, ETD, 5 kV, 2026-11-06), and draw the
annotated figure for PR 258.

    pip install pillow numpy scipy scikit-image matplotlib
    python docs/sem-first-sample-2026-11-06/measure_spots.py

The two originals (6144 x 4376 JPEG, data bar included) are fetched from the
PR comment's attachments into /tmp/sem-dl/ if they are not already there.
"""
import os
import urllib.request

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure, morphology
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from matplotlib.patches import Rectangle

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = {
    # name: (attachment id, horizontal field width in um from the data bar)
    "5kx": ("793eb0e4-57bd-4c62-9d80-fafde80afa6e", 82.9),
    "35kx": ("98e04b8f-0dbe-491b-9067-528b064a5bf0", 11.8),
}


def load(name):
    aid, hfw = SRC[name]
    path = f"/tmp/sem-dl/{aid}.jpg"
    if not os.path.exists(path):
        os.makedirs("/tmp/sem-dl", exist_ok=True)
        urllib.request.urlretrieve(f"https://github.com/user-attachments/assets/{aid}", path)
    a = np.asarray(Image.open(path)).astype(float)[:4096]  # drop the data bar
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    text = ((g - np.maximum(r, b)) > 25) | (np.abs(r - b) > 25)  # green labels, yellow cross
    text = ndi.binary_dilation(text, structure=morphology.disk(6))
    return a.mean(axis=2), ~text, hfw * 1000 / a.shape[1]


def spots(gray, valid, px, sigma, min_d_nm):
    """Features brighter / darker than the local background by `sigma` robust SDs."""
    sm = ndi.gaussian_filter(gray, 2)
    bg = ndi.uniform_filter(ndi.median_filter(gray[::8, ::8], size=25), 9)
    bg = np.kron(bg, np.ones((8, 8)))[: gray.shape[0], : gray.shape[1]]
    d = sm - bg
    med = np.median(d[valid])
    mad = 1.4826 * np.median(np.abs(d[valid] - med))
    out = {}
    for kind in ("bright", "dark"):
        m = (d > med + sigma * mad) if kind == "bright" else (d < med - sigma * mad)
        m = ndi.binary_opening(m & valid, structure=morphology.disk(2))
        lab = measure.label(m)
        props = [p for p in measure.regionprops(lab) if p.equivalent_diameter_area * px >= min_d_nm]
        dia = np.array([p.equivalent_diameter_area * px for p in props])
        area = sum(p.area for p in props)
        out[kind] = dict(props=props, dia=dia, frac=area / valid.sum(),
                         dens=len(props) / (valid.sum() * (px / 1000) ** 2))
    return out


def summary(tag, res):
    for kind, r in res.items():
        q = np.percentile(r["dia"], [10, 50, 90]) if len(r["dia"]) else [np.nan] * 3
        print(f"{tag} {kind:6s} n={len(r['dia']):4d}  {r['dens']:.3f}/um2  "
              f"area {100 * r['frac']:.2f}%  d10/d50/d90 = {q[0]:.0f}/{q[1]:.0f}/{q[2]:.0f} nm")


def scalebar(ax, px_nm, length_um, label, x0=0.04, y0=0.06):
    w = length_um * 1000 / px_nm
    x1, x2 = ax.get_xlim(); y1, y2 = ax.get_ylim()
    X = x1 + x0 * (x2 - x1)
    Y = max(y1, y2) - y0 * abs(y2 - y1)  # image axes: y grows downward
    ax.plot([X, X + w], [Y, Y], color="white", lw=4, solid_capstyle="butt",
            path_effects=[pe.Stroke(linewidth=6, foreground="black"), pe.Normal()])
    ax.text(X + w / 2, Y - 0.025 * abs(y2 - y1), label, color="white", ha="center", va="bottom",
            fontsize=11, path_effects=[pe.withStroke(linewidth=3, foreground="black")])


def note(ax, x, y, s, **kw):
    ax.annotate(s, (x, y), color="#ffd166", fontsize=10.5, ha=kw.pop("ha", "left"),
                path_effects=[pe.withStroke(linewidth=3, foreground="black")], **kw)


def main():
    g1, v1, px1 = load("5kx")
    g2, v2, px2 = load("35kx")
    r1 = spots(g1, v1, px1, sigma=4, min_d_nm=300)
    r2 = spots(g2, v2, px2, sigma=3, min_d_nm=60)
    summary("5kx ", r1)
    summary("35kx", r2)

    fig, axs = plt.subplots(2, 2, figsize=(13, 9.4), dpi=110)
    lo, hi = 25, 120
    # (a) whole 5,000x field, counted bright features circled
    ax = axs[0, 0]
    ax.imshow(g1, cmap="gray", vmin=lo, vmax=hi)
    for p in r1["bright"]["props"]:
        y, x = p.centroid
        ax.add_patch(plt.Circle((x, y), 55, fill=False, ec="#ffd166", lw=0.8))
    zb = (2100, 1800, 3300, 2600)
    ax.add_patch(Rectangle((zb[0], zb[1]), zb[2] - zb[0], zb[3] - zb[1], fill=False, ec="#06d6a0", lw=1.5))
    ax.set_xlim(0, g1.shape[1]); ax.set_ylim(g1.shape[0], 0)
    scalebar(ax, px1, 10, "10 µm")
    ax.set_title(f"(a) 5,000x, ETD (SE), 5 kV: {len(r1['bright']['dia'])} bright features ≥0.3 µm circled", fontsize=11)
    # (b) zoom on bright particles
    ax = axs[0, 1]
    ax.imshow(g1[zb[1]:zb[3], zb[0]:zb[2]], cmap="gray", vmin=lo, vmax=hi)
    ax.set_xlim(0, zb[2] - zb[0]); ax.set_ylim(zb[3] - zb[1], 0)
    note(ax, 120, 700, "angular, mottled, flat-topped\nbright particles, 0.5-1.5 µm")
    note(ax, 905, 470, "pit: dark inside,\nbright rim", ha="left")
    note(ax, 760, 60, "brighter box: scanned\nearlier at higher mag.", ha="left")
    scalebar(ax, px1, 2, "2 µm")
    ax.set_title("(b) green box in (a), full resolution", fontsize=11)
    # (c) 35,000x
    ax = axs[1, 0]
    ax.imshow(g2, cmap="gray", vmin=30, vmax=95)
    ax.set_xlim(0, g2.shape[1]); ax.set_ylim(g2.shape[0], 0)
    zc = (2200, 1500, 3800, 2600)
    ax.add_patch(Rectangle((zc[0], zc[1]), zc[2] - zc[0], zc[3] - zc[1], fill=False, ec="#06d6a0", lw=1.5))
    scalebar(ax, px2, 2, "2 µm")
    ax.set_title("(c) 35,000x, same settings: wavy bright lines ~0.5-0.8 µm apart", fontsize=11)
    # (d) zoom on dark spots
    ax = axs[1, 1]
    ax.imshow(g2[zc[1]:zc[3], zc[0]:zc[2]], cmap="gray", vmin=30, vmax=95)
    ax.set_xlim(0, zc[2] - zc[0]); ax.set_ylim(zc[3] - zc[1], 0)
    note(ax, 40, 1040, "dark spots: soft edges, no bright rim;\nmost are 0.07-0.14 µm across")
    scalebar(ax, px2, 0.5, "500 nm", x0=0.70)
    ax.set_title("(d) green box in (c), full resolution", fontsize=11)
    for ax in axs.flat:
        ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    out = os.path.join(HERE, "etd-bright-and-dark-spots.png")
    fig.savefig(out, dpi=110)
    print("wrote", out)


if __name__ == "__main__":
    main()
