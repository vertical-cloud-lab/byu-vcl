"""Build the CubXL parts for the pose chosen by ../layout/optimize_layout.py.

    python build_cad.py /path/to/openraman/cad /path/to/PandaDeck.step

Writes export/: the two printed parts (STEP + STL, frame S) and the whole installation
as one STEP in the PandaDeck frame, and refreshes printed_parts.json for ../bom.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cubxl_parts as cx  # noqa: E402
import openraman_assembly as oa  # noqa: E402

EXPORT = HERE / "export"


def installation(openraman_cad, deck_step=None, pose=None):
    """Everything in the PandaDeck frame: list of (name, shape, colour, opacity, group, step)."""
    pose = pose or json.loads((HERE.parent / "layout" / "best_pose.json").read_text())["best"]
    th, tx, ty, keys = pose["theta"], pose["tx"], pose["ty"], [tuple(k) for k in pose["keys"]]
    R, t = cx.pose_matrix(th, tx, ty)
    parts, dock_lens, beams = oa.build(openraman_cad)
    adapter = cx.deck_adapter(th, tx, ty, keys)
    dock = cx.tip_dock()
    return dict(parts=parts, dock_lens=dock_lens, beams=beams, adapter=adapter, dock=dock, R=R, t=t, pose=pose,
                deck=cx.panda_deck(deck_step), keys=keys)


def main(openraman_cad, deck_step=None):
    EXPORT.mkdir(exist_ok=True)
    inst = installation(openraman_cad, deck_step)
    R, t = inst["R"], inst["t"]
    for name, shape in (("cubxl_deck_adapter", inst["adapter"]), ("cubxl_tip_dock", inst["dock"])):
        cq.exporters.export(shape, str(EXPORT / f"{name}.step"))
        cq.exporters.export(shape, str(EXPORT / f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
    pp = json.loads((HERE / "printed_parts.json").read_text())
    pp["CUBXL_DECK_ADAPTER"] = dict(volume_cm3=round(inst["adapter"].Volume() / 1000.0, 1),
                                    source="cad/export/cubxl_deck_adapter.step (this repo)")
    pp["CUBXL_TIP_DOCK"] = dict(volume_cm3=round(inst["dock"].Volume() / 1000.0, 1),
                                source="cad/export/cubxl_tip_dock.step (this repo)")
    (HERE / "printed_parts.json").write_text(json.dumps(pp, indent=2) + "\n")

    # whole installation, PandaDeck frame
    to_d = lambda s: oa.place(s, R, t)
    shapes = [to_d(p.shape) for p in inst["parts"]] + [to_d(s) for s in inst["dock_lens"]]
    shapes += [to_d(inst["adapter"]), to_d(inst["dock"])]   # PandaDeck itself: Cubware
    cq.exporters.export(cq.Compound.makeCompound(shapes), str(EXPORT / "openraman_on_pandadeck.step"))
    print(json.dumps({k: pp[k] for k in ("CUBXL_DECK_ADAPTER", "CUBXL_TIP_DOCK")}, indent=1))
    for f in sorted(EXPORT.iterdir()):
        print(f"{f.name:40s} {f.stat().st_size / 1e3:8.1f} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ext/openraman-cad/cad",
         sys.argv[2] if len(sys.argv) > 2 else None)
