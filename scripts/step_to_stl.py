"""Tessellate STEP files into one STL per solid, for scripts/render_cad.py.

Needs CadQuery (pip install cadquery), which must live in a different environment from
PyVista: CadQuery's OCP wheel bundles an older VTK that PyVista refuses to import.

    python -I scripts/step_to_stl.py part.step out_dir/ [--tol 0.05]

Writes out_dir/<stem>_<n>.stl for each solid and prints the paths as a JSON list.
"""

import argparse
import json
from pathlib import Path

import cadquery as cq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", nargs="+")
    ap.add_argument("out")
    ap.add_argument("--tol", type=float, default=None, help="linear deflection (model units)")
    ap.add_argument("--max-solids", type=int, default=60)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for s in args.step:
        shape = cq.importers.importStep(s)
        solids = shape.solids().vals()
        if not solids or len(solids) > args.max_solids:
            solids = [shape.val()]
        bb = shape.val().BoundingBox()
        tol = args.tol or max(bb.DiagonalLength / 2000.0, 1e-3)
        for i, so in enumerate(solids):
            p = out / f"{Path(s).stem}_{i:02d}.stl"
            cq.exporters.export(cq.Workplane().add(so), str(p), tolerance=tol, angularTolerance=0.2)
            written.append(str(p))
    print(json.dumps(written))


if __name__ == "__main__":
    main()
