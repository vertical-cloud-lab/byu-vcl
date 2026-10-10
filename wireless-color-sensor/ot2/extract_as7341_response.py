#!/usr/bin/env python3
"""Pull the AS7341's measured spectral response out of its datasheet, exactly.

Every comparison with published pigment spectra up to 2026-10-10 modelled each
channel as a Gaussian at the datasheet's typical centre and FWHM. That leaves
out the part of a real filter's response that lies outside its band. DS000504
v3-00 Figure 19 ("Measured Spectral Responsivity Relative to F8", page 17) is
the measured version, taken with a diffuser on the package. It is drawn as
vector paths, not a picture, so it can be read back without digitising by eye:
each curve is one polyline of 351 points at 2 nm steps from 350 to 1050 nm.

The axes are calibrated from the figure's own gridlines (verticals every
100 nm, horizontals every 0.2), and each curve is named from the legend swatch
next to its label. On v3-00 the fit residuals are 0.035 pt in x and 0.031 pt
in y, i.e. about 0.06 nm and 0.0003 in response.

The datasheet is not committed; fetch it, then::

    curl -L -o DS000504.pdf https://look.ams-osram.com/m/24266a3e584de4db/original/AS7341-DS000504.pdf
    python3 extract_as7341_response.py DS000504.pdf    # writes as7341-response-fig19.csv

v3-00 (2020-06-25) had sha256 6036d333...a23f0 on 2026-10-10. Values are
relative to F8's peak. F1-F8 were measured at 256x, Clear at 512x, NIR and
Flicker at 64x, as the legend says, so Clear/NIR/Flicker are not on the same
gain as F1-F8.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

import numpy as np
import pymupdf

HERE = Path(__file__).resolve().parent
PAGE = 16                       # 0-based: printed page 16, PDF page 17
BAND = (470.0, 715.0)           # y range (pt) of Figure 19 on that page
GRID_GREY = 0.851               # stroke colour of the gridlines
ORDER = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "Clear", "NIR", "Flicker"]
V3_SHA256 = "6036d333ca526e1a28dc47401cf8350d47156c2a9614e5620c617a8bf39a23f0"


def points(path):
    out = []
    for item in path["items"]:
        if item[0] != "l":
            raise SystemExit(f"unexpected path item {item[0]!r}: is this DS000504 v3-00?")
        out += [(p.x, p.y) for p in item[1:]]
    return out


def extract(pdf):
    page = pymupdf.open(pdf)[PAGE]
    paths = [d for d in page.get_drawings() if d["rect"].y0 >= BAND[0] and d["rect"].y1 <= BAND[1]]

    gx, gy = set(), set()
    for d in paths:
        if d.get("color") and abs(d["color"][0] - GRID_GREY) < 0.01:
            for _, a, b in (it for it in d["items"] if it[0] == "l"):
                if abs(a.x - b.x) < 1e-3:
                    gx.add(round(a.x, 3))
                if abs(a.y - b.y) < 1e-3:
                    gy.add(round(a.y, 3))
    gx, gy = sorted(gx), sorted(gy)
    if len(gx) != 8 or len(gy) != 7:
        raise SystemExit(f"expected 8 x and 7 y gridlines, found {len(gx)} and {len(gy)}")
    nm_grid = np.arange(350, 1051, 100)
    val_grid = np.round(np.arange(1.2, -0.01, -0.2), 1)
    kx = np.polyfit(nm_grid, gx, 1)
    ky = np.polyfit(val_grid, gy, 1)
    resid = (float(np.abs(np.polyval(kx, nm_grid) - gx).max()),
             float(np.abs(np.polyval(ky, val_grid) - gy).max()))

    spans = [s for b in page.get_text("dict")["blocks"] for line in b.get("lines", [])
             for s in line["spans"] if BAND[0] <= s["bbox"][1] <= BAND[1] and "_" in s["text"]]
    labels = {s["text"].replace(" ", "").split("_")[0]: s["bbox"] for s in spans}

    swatch, curve = {}, {}
    for d in paths:
        if not d.get("color"):
            continue
        colour = tuple(round(c, 3) for c in d["color"])
        pts = points(d)
        if len(pts) <= 3:                       # legend swatch: label sits just right of it
            cy, x1 = (d["rect"].y0 + d["rect"].y1) / 2, d["rect"].x1
            for name, bb in labels.items():
                if abs((bb[1] + bb[3]) / 2 - cy) < 3 and 0 <= bb[0] - x1 < 10:
                    swatch[colour] = name
        elif len(pts) > 20:
            curve.setdefault(colour, set()).update(pts)

    nm = np.arange(350, 1051, 2)
    table = {}
    for colour, pts in curve.items():
        pts = sorted(pts)
        x = (np.array([p[0] for p in pts]) - kx[1]) / kx[0]
        y = (np.array([p[1] for p in pts]) - ky[1]) / ky[0]
        if len(x) != len(nm) or np.abs(x - nm).max() > 0.2:
            raise SystemExit(f"{swatch.get(colour)}: points are not on the 2 nm grid")
        table[swatch[colour]] = np.clip(y, 0.0, None)
    missing = set(ORDER) - set(table)
    if missing:
        raise SystemExit(f"curves not found: {sorted(missing)}")
    return nm, table, resid


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=HERE / "as7341-response-fig19.csv")
    args = ap.parse_args()
    sha = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
    if sha != V3_SHA256:
        print(f"note: sha256 {sha[:12]}... is not the v3-00 file this was written against")
    nm, table, resid = extract(args.pdf)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["nm"] + ORDER)
        for i, wl in enumerate(nm):
            w.writerow([int(wl)] + [f"{table[k][i]:.4f}" for k in ORDER])
    print(f"wrote {args.out.name}: {len(nm)} wavelengths x {len(ORDER)} channels; "
          f"gridline residuals {resid[0]:.3f} pt (x), {resid[1]:.3f} pt (y)")
    for k in ORDER:
        i = int(np.argmax(table[k]))
        print(f"  {k:>7}: peak {table[k][i]:.3f} at {nm[i]} nm")


if __name__ == "__main__":
    main()
