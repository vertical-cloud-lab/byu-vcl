"""AgileX's own jaws at the same 45 degree grasps, for comparison with the inserts.

    python stock_jaws_check.py    # -> exports/checks_stock_jaws.json
"""
import json
import cadquery as cq
import numpy as np
import checks as C
import parts as PT
import sources as S

g = S.gripper()
sol = g["solids"]
xt, zt = g["tool_axis_xz"]
parts, _ = PT.build()
sc = C.scene(parts)
R = np.array([[0, 0, -1], [-1 / 2 ** 0.5, 1 / 2 ** 0.5, 0], [1 / 2 ** 0.5, 1 / 2 ** 0.5, 0]])
out = {}
for name, y, r in (("handle post (dia 16)", 0.0, PT.P.post_r), ("vial 4", PT.slot_y(4), PT.P.vial_r),
                   ("vial 6", PT.slot_y(6), PT.P.vial_r)):
    d = (zt + r) - g["pad_face_z"]
    up, dn = cq.Vector(0, 0, d), cq.Vector(0, 0, -d)
    gp = {"motor housing": sol[0], "linear rail": sol[1], "finger plate": sol[2], "back cover": sol[3],
          "upper jaw": sol[7].translate(up), "upper pad": sol[6].translate(up), "upper carriage": sol[5].translate(up),
          "lower jaw": sol[11].translate(dn), "lower pad": sol[10].translate(dn), "lower carriage": sol[9].translate(dn)}
    t = np.array([0, y, PT.P.groove_z]) - R @ np.array(g["tcp"])
    gp = {k: C.xform(v, R.tolist(), t.tolist()) for k, v in gp.items()}
    found = C.pairs(gp, sc)
    out[name] = [(f["a"], f["b"], f["overlap_mm3"]) for f in found]
    print(name, out[name], flush=True)
(PT.OUT / "checks_stock_jaws.json").write_text(json.dumps(out, indent=1) + "\n")
