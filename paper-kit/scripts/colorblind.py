"""make colorblind: how every figure looks to readers with colour-vision deficiency.

For each figures/out/*.png this writes figures/out/cvd/<slug>.png, a sheet of
the figure as drawn and as simulated for deuteranopia, protanopia and
tritanopia (Machado, Oliveira and Fernandes 2009, severity 1), plus greyscale
for black-and-white printing.  It also finds the figure's series colours (the
saturated colours that cover a visible area) and reports any two that are
distinct as drawn but within dE 10 (CIELAB) of each other under a
simulation: those series need a second cue, such as marker shape, line
style or a direct label.

The sheets are for looking at; the checklist (checklists/colorblind.md) says
what to look for.
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

KIT = Path(__file__).resolve().parents[1]
OUT = KIT / "figures" / "out"
CVD = OUT / "cvd"

# Machado et al. (2009), doi:10.1109/TVCG.2009.113, severity 1.0, for linear RGB
MACHADO = {
    "deuteranopia": np.array([[0.367322, 0.860646, -0.227968],
                              [0.280085, 0.672501, 0.047413],
                              [-0.011820, 0.042940, 0.968881]]),
    "protanopia": np.array([[0.152286, 1.052583, -0.204868],
                            [0.114503, 0.786281, 0.099216],
                            [-0.003882, -0.048116, 1.051998]]),
    "tritanopia": np.array([[1.255528, -0.076749, -0.178779],
                            [-0.078411, 0.930809, 0.147602],
                            [0.004733, 0.691367, 0.303900]]),
}
DE_MIN = 10.0
SHEET_DPI = 150


def to_linear(srgb):
    s = np.asarray(srgb, dtype=float) / 255
    return np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)


def to_srgb(lin):
    lin = np.clip(lin, 0, 1)
    s = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)
    return np.round(s * 255).astype(np.uint8)


def simulate(rgb, kind):
    """rgb: (..., 3) uint8 -> the same as seen with the deficiency (or greyscale)."""
    lin = to_linear(rgb)
    if kind == "greyscale":
        y = lin @ np.array([0.2126, 0.7152, 0.0722])
        return to_srgb(np.repeat(y[..., None], 3, axis=-1))
    return to_srgb(lin @ MACHADO[kind].T)


def to_lab(rgb):
    lin = to_linear(rgb)
    xyz = lin @ np.array([[0.4124, 0.3576, 0.1805],
                          [0.2126, 0.7152, 0.0722],
                          [0.0193, 0.1192, 0.9505]]).T
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], axis=-1)


def series_colours(rgb, min_share=2e-4, min_chroma=40):
    """The saturated colours covering at least min_share of the pixels, most
    common first, with near-duplicates (dE < 3) merged."""
    px = rgb.reshape(-1, 3).astype(np.int32)
    packed = (px[:, 0] << 16) | (px[:, 1] << 8) | px[:, 2]
    vals, counts = np.unique(packed, return_counts=True)
    cols = np.stack([(vals >> 16) & 255, (vals >> 8) & 255, vals & 255], 1)
    keep = (counts >= min_share * packed.size) & ((cols.max(1) - cols.min(1)) >= min_chroma)
    cols, counts = cols[keep], counts[keep]
    merged = []
    for c in cols[np.argsort(-counts)].astype(np.uint8):
        if all(np.linalg.norm(to_lab(c) - to_lab(m)) >= 3 for m in merged):
            merged.append(c)
    return merged


def sheet(rgb, path):
    kinds = ["as drawn", "deuteranopia", "protanopia", "tritanopia", "greyscale"]
    tiles = [rgb] + [simulate(rgb, k) for k in kinds[1:]]
    h, w = rgb.shape[:2]
    pad = 40
    canvas = Image.new("RGB", (w, (h + pad) * len(tiles)), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 24)
    except OSError:
        font = ImageFont.load_default()
    for i, (k, t) in enumerate(zip(kinds, tiles)):
        y = i * (h + pad)
        draw.text((8, y + 6), k, fill="black", font=font)
        canvas.paste(Image.fromarray(t), (0, y + pad))
    canvas.save(path)


def main() -> int:
    pngs = sorted(OUT.glob("*.png"))
    if not pngs:
        print("no figures in figures/out/: run make figures first")
        return 1
    CVD.mkdir(parents=True, exist_ok=True)
    flagged = 0
    for png in pngs:
        with Image.open(png) as im:
            full = np.asarray(im.convert("RGB"))
            scale = SHEET_DPI / im.info.get("dpi", (600, 600))[0]
            small = np.asarray(im.convert("RGB").resize(
                (round(im.width * scale), round(im.height * scale)), Image.LANCZOS))
        sheet(small, CVD / png.name)
        cols = series_colours(full)
        notes = []
        for kind in ("deuteranopia", "protanopia", "tritanopia", "greyscale"):
            for a, b in combinations(cols, 2):
                de0 = np.linalg.norm(to_lab(a) - to_lab(b))
                de = np.linalg.norm(to_lab(simulate(a, kind)) - to_lab(simulate(b, kind)))
                if de0 >= DE_MIN and de < DE_MIN:
                    notes.append(f"{kind}: #{a[0]:02X}{a[1]:02X}{a[2]:02X} and "
                                 f"#{b[0]:02X}{b[1]:02X}{b[2]:02X} differ by dE {de:.1f}")
        hexes = ", ".join(f"#{c[0]:02X}{c[1]:02X}{c[2]:02X}" for c in cols) or "none"
        print(f"{png.stem}: series colours {hexes}")
        for n in notes:
            print(f"  LOOK: {n}; give these series a second cue (marker, line style, label)")
        flagged += bool(notes)
    print(f"\nsheets in {CVD.relative_to(KIT)}/; {flagged} of {len(pngs)} figures have colour "
          "pairs to look at (greyscale pairs matter only if the figure may be printed in black "
          "and white)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
