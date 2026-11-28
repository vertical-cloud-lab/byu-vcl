"""The under-deck frame as printed on 2026-11-20: frame.stl without its four 0.5 mm corner pads.

Why: the frame prints bosses up, fan face down. Drawn with pads, its 1632 mm2 fan face sits 0.5 mm
above the bed on four corner pads (146 mm2), and that face is the 0.5 mm clearance over the fan's
rotor. Supports there would leave marks that eat into the clearance (BUILD.md says the same about
the vial holder's recess), and an unsupported 0.5 mm gap prints as a sagging bridge. Flipped, the
counterbores, the Hall pocket and the bosses all face the bed. So the pads come off and four 0.5 mm
M3 washers go in their place, as in the compact build, which sits on four such washers. The stack
heights don't change: washer 0.5 mm = pad 0.5 mm.

The cut is at the frame plate's underside, z = -12.83 in build_under_deck.py's deck frame
(Z_PLATE0 = -DECK_T - (Z_RECESS - Z_WALL)). Nothing else on the part is below it.

    python print/2026-11-20-under-deck/make_print_stls.py     # from hardware/vial-stirrer-cubxl
"""
import sys
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
Z_PLATE0 = -12.83


def to_manifold(m: trimesh.Trimesh) -> mf.Manifold:
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                               tri_verts=np.asarray(m.faces, np.uint32)))


def to_trimesh(man: mf.Manifold) -> trimesh.Trimesh:
    mesh = man.to_mesh()
    return trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts, process=True)


def main() -> int:
    src = trimesh.load(ROOT / "stl" / "under-deck" / "frame.stl")
    lo, hi = src.bounds
    keep = mf.Manifold.cube([200.0, 200.0, hi[2] - Z_PLATE0 + 10.0]).translate([-100.0, -100.0, Z_PLATE0])
    cut = to_trimesh(to_manifold(src) ^ keep)
    out = OUT / "frame_no_pads.stl"
    cut.export(out)
    pads = src.volume - cut.volume
    print(f"frame.stl        bounds z {lo[2]:.2f} .. {hi[2]:.2f}, volume {src.volume:.1f} mm3")
    print(f"frame_no_pads    bounds z {cut.bounds[0][2]:.2f} .. {cut.bounds[1][2]:.2f}, volume {cut.volume:.1f} mm3, "
          f"watertight {cut.is_watertight}, bodies {len(cut.split())}")
    print(f"removed: {pads:.1f} mm3 = {pads / 0.5:.0f} mm2 of pads x 0.5 mm")
    n, zc, a = cut.face_normals, cut.triangles_center[:, 2], cut.area_faces
    over = (n[:, 2] < -0.707) & (zc > cut.bounds[0][2] + 0.01)
    flat = (n[:, 2] < -0.99) & (zc < cut.bounds[0][2] + 0.01)
    print(f"on the bed: {a[flat].sum():.0f} mm2; overhang steeper than 45 deg above the bed: {a[over].sum():.1f} mm2")
    return 0 if cut.is_watertight and len(cut.split()) == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
