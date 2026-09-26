#!/usr/bin/env python3
"""Download Raspberry Pi's own Pi 5 and Camera Module 3 STEP models into .cache/ and mesh
them for render.py. They are not committed: the Pi 5 model is 77 MB (MIT licence, included in
its zip) and the Camera Module 3 zip carries no licence at all.

    python fetch_models.py
"""
from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path

import cadquery as cq

CACHE = Path(__file__).resolve().parent / ".cache"
MODELS = {
    "pi5.stl": ("https://datasheets.raspberrypi.com/rpi5/RaspberryPi5-step.zip", "rpi-5b_no_graphics.step"),
    "cm3_standard.stl": ("https://pip-assets.raspberrypi.com/categories/1207-design-files/documents/"
                         "RP-008154-DS-1-camera-module-3-step.zip", "Camera_module_3_std_model_simple.stp"),
}


def main() -> None:
    CACHE.mkdir(exist_ok=True)
    for stl, (url, member) in MODELS.items():
        out = CACHE / stl
        if out.exists():
            print(f"{stl}: already there")
            continue
        print(f"{stl}: downloading {url}")
        data = urllib.request.urlopen(url, timeout=300).read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            name = next(n for n in z.namelist() if n.endswith(member) and "__MACOSX" not in n)
            step = CACHE / member
            step.write_bytes(z.read(name))
        shape = cq.importers.importStep(str(step))
        cq.exporters.export(shape, str(out), tolerance=0.05, angularTolerance=0.3)
        step.unlink()
        print(f"{stl}: written")


if __name__ == "__main__":
    main()
