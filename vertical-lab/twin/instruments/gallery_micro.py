"""Figures of the microscopy, diffraction and chemistry simulators: one PNG per instrument showing the raw data and
what the analysis extracted, for AlSi10Mg, Scalmalloy and an uninoculated 7075 (FLAIME) and 70-30 Cu-Ni and NAB (ONR),
each made through the truth the way ``truth_al.reference_table()`` / ``truth_cu.reference_table()`` make them
(``micro.gallery_samples``); and 512x512 transparent icons for the video's DAG.

    python -m twin.instruments.gallery_micro            # out/twin2/instruments/*.png, out/twin2/thumbs/*.png
"""
from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "twin2" / "instruments"
THUMBS = ROOT / "out" / "twin2" / "thumbs"

FIGURES = [("xrd", "gallery"), ("sem", "gallery"), ("eds", "gallery"), ("ebsd", "gallery"), ("xrf", "gallery"),
           ("icpms", "gallery")]
ICONS = [("sem", "thumbnail_powder", "sem_powder"), ("sem", "thumbnail_section", "sem_section"),
         ("eds", "thumbnail", "eds"), ("ebsd", "thumbnail_map", "ebsd"), ("ebsd", "thumbnail_kikuchi", "kikuchi"),
         ("xrd", "thumbnail", "xrd"), ("xrf", "thumbnail", "xrf")]


def main(only=None):
    from twin.instruments import micro
    OUT.mkdir(parents=True, exist_ok=True)
    THUMBS.mkdir(parents=True, exist_ok=True)
    samples = micro.gallery_samples()
    for mod, fn in FIGURES:
        if only and mod not in only:
            continue
        t0 = time.time()
        getattr(importlib.import_module(f"twin.instruments.{mod}"), fn)(OUT, samples)
        print(f"{mod}.{fn}: {time.time() - t0:.1f} s", flush=True)
    for mod, fn, name in ICONS:
        if only and mod not in only:
            continue
        getattr(importlib.import_module(f"twin.instruments.{mod}"), fn)(THUMBS / f"{name}.png", samples)
        print(f"thumb {name}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
