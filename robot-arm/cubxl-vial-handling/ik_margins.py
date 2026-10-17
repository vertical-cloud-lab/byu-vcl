"""IK margins for the finger inserts' grasp centre (162 mm past the flange) against AgileX's pad centre (120 mm).

    python ik_margins.py    # -> exports/ik_margins.json (uses analysis.py's IK and piper_fk.py)
"""
import json
import numpy as np

import analysis as A
import geometry as G
import parts as PT
from piper_fk import Piper

out = {}
piper = Piper()
for tcp_mm in (120.0, 120.0 + PT.P.reach_extension):
    A.TCP = tcp_mm / 1000
    h = G.grasp_point()[2]
    cases = {
        "handle post, 45 deg": (G.grasp_point(), [0, 1, -1], [1, 0, 0]),
        "nearest vial (slot 1), 45 deg": (np.array([0, G.slot_y(1), h]), [0, 1, -1], [1, 0, 0]),
        "farthest vial (slot 9), 45 deg": (np.array([0, G.slot_y(9), h]), [0, 1, -1], [1, 0, 0]),
    }
    res = {}
    for name, (tgt, appr, close) in cases.items():
        b = A.ik(piper, np.asarray(tgt, float), appr, close)
        res[name] = dict(radius_m=round(float(np.hypot(tgt[0], tgt[1])), 3), height_m=round(float(tgt[2]), 4),
                         reachable=b is not None, min_margin_deg=None if b is None else round(b[1], 1),
                         q_deg=None if b is None else np.round(np.degrees(b[0]), 1).tolist())
    out[f"tcp_{tcp_mm:g}mm"] = res
print(json.dumps(out, indent=1))
(PT.OUT / "ik_margins.json").write_text(json.dumps(out, indent=1) + "\n")
