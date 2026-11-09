#!/usr/bin/env python3
"""Write the plain Ø10 x 4.6 mm spacer STL and check both spacer STLs (2026-11-06).

Ben described the spacer on PR #269 as "a plain 10mm diameter, 4.6mm tall cylinder". His Onshape
document "Stir module spacer" (793acc919f1bebafa8462ee6, last changed 2026-11-05 23:02 UTC) holds a
Ø15 x 4.6 mm cylinder instead; stl/spacer/spacer_d15_h4.6_onshape.stl is that part as Onshape
exported it, byte for byte. Both are here so the print run can print whichever Ben names.

    python make_spacer.py        # needs numpy and trimesh

The Ø10 cylinder has 96 sides, so its sides sit at most 0.003 mm inside the true circle. It stands on
z = 0, centred on x = y = 0, which is the way up it prints.
"""
import hashlib
import math
import pathlib

import numpy as np
import trimesh

HERE = pathlib.Path(__file__).resolve().parent
STL = HERE.parents[1] / "stl" / "spacer"


def write_d10() -> pathlib.Path:
    m = trimesh.creation.cylinder(radius=5.0, height=4.6, sections=96)
    m.apply_translation([0, 0, 2.3])
    out = STL / "spacer_d10_h4.6.stl"
    m.export(out)
    return out


def check(path: pathlib.Path, d: float, h: float) -> None:
    m = trimesh.load(path)
    lo, hi = m.bounds
    r = np.hypot(m.vertices[:, 0], m.vertices[:, 1])
    ideal = math.pi * (d / 2) ** 2 * h
    assert m.is_watertight, path
    assert np.allclose(lo, [-d / 2, -d / 2, 0], atol=1e-3) and np.allclose(hi, [d / 2, d / 2, h], atol=1e-3), (lo, hi)
    assert set(np.round(r[r > 1e-6], 4)) == {d / 2}, "not a plain cylinder"
    assert set(np.round(m.vertices[:, 2], 4)) == {0.0, h}, "not a plain cylinder"
    print(f"{path.name}: Ø{hi[0] - lo[0]:.3f} x {hi[2] - lo[2]:.3f} mm, plain cylinder, "
          f"volume {m.volume:.1f} mm³ (exact cylinder {ideal:.1f}), {len(m.faces)} faces, "
          f"md5 {hashlib.md5(path.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    check(write_d10(), 10.0, 4.6)
    check(STL / "spacer_d15_h4.6_onshape.stl", 15.0, 4.6)
