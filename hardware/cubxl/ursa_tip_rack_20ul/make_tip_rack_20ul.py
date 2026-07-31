#!/usr/bin/env python3
"""Derive a small-tip variant of the Ursa Cub-XL tip rack.

The upstream part is ``labware/ursa_tip_rack/TipRack.stl`` in
`Ursa-Laboratories/Cubware <https://github.com/Ursa-Laboratories/Cubware>`_.
Its 30 bores are a 300 uL tip seat: a Ohm6.980 -> Ohm6.424 taper over 16 mm
(~1.0 deg half-angle) followed by a Ohm4.32 through-bore for the last 2 mm.
20 uL tips rattle around in that, so this script re-bores the top plate to a
straight, user-specified diameter (5.0 mm by default).

Only the top plate is touched.  The script unions a solid box over the plate
region -- which fills the 30 old seats exactly, because the plate is solid
apart from those bores -- and then subtracts the new straight cylinders.  The
side walls, end gussets, bottom rail and the deck key pockets that lock the
rack to the PANDA-BEAR / Cub-XL deck all pass through unmodified.

Two files are written:

``TipRack20uL.stl``
    Original ``TipRack.stl`` coordinate frame, so it is a drop-in geometric
    replacement wherever CubOS/Cubware reference the stock mesh.
``TipRack20uL.3mf``
    Same solid, rotated into the recommended print orientation: open bottom on
    the bed, bores vertical, part in the positive octant (21 x 138 x 66 mm).

Usage::

    pip install trimesh manifold3d numpy
    python make_tip_rack_20ul.py                 # 5.0 mm bores
    python make_tip_rack_20ul.py --diameter 5.2  # printer-compensated
"""

from __future__ import annotations

import argparse
import math
import urllib.request
from pathlib import Path

import manifold3d as m3
import numpy as np
import trimesh

SOURCE_URL = (
    "https://raw.githubusercontent.com/Ursa-Laboratories/Cubware/main/"
    "labware/ursa_tip_rack/TipRack.stl"
)

# --- geometry measured off the upstream TipRack.stl (see module docstring) ---
ENVELOPE = (21.0, 66.0, 138.0)  # x, y (height, +y is up), z
PLATE_TOP_Y = 0.0  # top face of the tip plate
PLATE_BOTTOM_Y = -18.0  # underside of the tip plate / roof of the cavity
COLUMN_X = (6.25, 14.75)  # 2 columns, 8.5 mm apart, centred on x = 10.5
ROW_Z = tuple(-5.0 - 8.5 * i for i in range(15))  # 15 rows, 8.5 mm pitch
SEGMENTS = 96  # facets per bore

HERE = Path(__file__).resolve().parent


def load_source(path: Path) -> m3.Manifold:
    """Load the upstream STL as a Manifold, downloading it if needed."""
    if not path.exists():
        print(f"downloading {SOURCE_URL}")
        urllib.request.urlretrieve(SOURCE_URL, path)
    mesh = trimesh.load(path, force="mesh")
    # The STL is closed and consistently wound but has edges shared by four
    # faces where the bore walls meet the plate faces; merging coincident
    # vertices is enough for manifold3d to accept it.
    mesh.merge_vertices(digits_vertex=4)
    solid = m3.Manifold(
        m3.Mesh(
            vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
            tri_verts=np.asarray(mesh.faces, dtype=np.uint32),
        )
    )
    if solid.status() != m3.Error.NoError:
        raise RuntimeError(f"source mesh rejected by manifold3d: {solid.status()}")
    return solid


def box(x0, x1, y0, y1, z0, z1) -> m3.Manifold:
    return m3.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def rebore(solid: m3.Manifold, diameter: float) -> m3.Manifold:
    """Fill the stock 300 uL seats and cut straight bores of ``diameter``."""
    plate = box(0.0, ENVELOPE[0], PLATE_BOTTOM_Y, PLATE_TOP_Y, -ENVELOPE[2], 0.0)

    holes = (plate - solid).volume()
    filled = solid + plate
    if not math.isclose(filled.volume(), solid.volume() + holes, rel_tol=1e-6):
        raise RuntimeError("plate fill added material outside the stock bores")

    # Circumscribe the facet polygon so the *minimum* bore is exactly nominal.
    radius = 0.5 * diameter / math.cos(math.pi / SEGMENTS)
    # Overshoot 1 mm past both plate faces so the cut leaves no coincident
    # faces; the cavity under every bore is empty, so this removes nothing else.
    height = (PLATE_TOP_Y - PLATE_BOTTOM_Y) + 2.0
    cutter = m3.Manifold.cylinder(
        height, radius, radius, circular_segments=SEGMENTS
    ).translate([0.0, 0.0, PLATE_BOTTOM_Y - 1.0])
    # cylinder() is built along +z; rotate it onto the +y bore axis.
    cutter = cutter.rotate([-90.0, 0.0, 0.0])

    result = filled
    for x in COLUMN_X:
        for z in ROW_Z:
            result = result - cutter.translate([x, 0.0, z])
    if result.status() != m3.Error.NoError:
        raise RuntimeError(f"boolean failed: {result.status()}")
    return result


def to_trimesh(solid: m3.Manifold) -> trimesh.Trimesh:
    mesh = solid.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(mesh.vert_properties)[:, :3],
        faces=np.asarray(mesh.tri_verts),
        process=False,
    )


def print_orientation(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Rotate deck frame -> print frame: bottom slab on the bed, bores facing up.

    The bores then print vertically (round, no support) and their seating rims
    print last, clear of first-layer elephant's foot.  The only overhang is the
    plate underside bridging the 17 mm cavity.
    """
    out = mesh.copy()
    # (x, y, z) -> (x, -z, y); right-handed (det = +1).
    transform = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, -1.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    out.apply_transform(transform)
    out.apply_translation(-out.bounds[0])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--diameter",
        type=float,
        default=5.0,
        help="bore diameter in mm (default: 5.0, sized for 20 uL tips)",
    )
    ap.add_argument("--source", type=Path, default=HERE / "TipRack.stl")
    ap.add_argument("--stem", default="TipRack20uL")
    args = ap.parse_args()

    solid = load_source(args.source)
    print(f"source: volume {solid.volume():.1f} mm^3, genus {solid.genus()}")

    result = rebore(solid, args.diameter)
    mesh = to_trimesh(result)
    print(
        f"result: volume {mesh.volume:.1f} mm^3, genus {result.genus()}, "
        f"watertight={mesh.is_watertight}, winding={mesh.is_winding_consistent}"
    )
    if not mesh.is_watertight or result.genus() != 31:
        raise RuntimeError("result is not a clean 30-bore solid")

    stl_path = HERE / f"{args.stem}.stl"
    mesh.export(stl_path)
    print(f"wrote {stl_path.name} (deck frame, extents {mesh.extents.round(2)})")

    printable = print_orientation(mesh)
    tmf_path = HERE / f"{args.stem}.3mf"
    printable.export(tmf_path)
    print(f"wrote {tmf_path.name} (print frame, extents {printable.extents.round(2)})")


if __name__ == "__main__":
    main()
