"""Linear-elastic FEA (gmsh tet10 + CalculiX 2.21) of the three compliant/critical features.

  cup   one cup of the rack: radial displacement of the right pad's contact face
        (cylindrical system about the cup axis) -> pad force and peak strain.
  key   clip-in key: inward displacement of one barb (what the deck slot imposes
        while the key goes in) -> latch force and peak strain.
  bar   gantry bar: 50 N down (2x the ~25 N the magnet can pull) on the
        housing stop, prongs held where they bear on the backboard -> prong stress.

PLA, E = 2600 MPa (Bambu PLA Basic ~2.3-3.5 GPa; forces scale with E, strains don't),
nu = 0.35.  Run:  python run_fea.py  (needs cadquery, gmsh, numpy; ccx on PATH)
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cad")); sys.path.insert(0, HERE)
import cadquery as cq
import build as B
import ccxrun

E = 2600.0
OUT = os.path.join(HERE, "runs"); os.makedirs(OUT, exist_ok=True)
res = {"E_MPa": E, "nu": 0.35}

def cup_model():
    p = B.P
    body = cq.Workplane("XY").box(p["width"], p["pitch"], p["height"], centered=(True, True, False))
    cut, adds = B.cup_cuts_and_adds(p)
    body = body.cut(cut)
    for a in adds:
        body = body.union(a)
    # right half only (the loaded arm); the cut face at x=-2 is held fixed
    body = body.intersect(cq.Workplane("XY").box(30, 40, 40, centered=(False, True, False)).translate((-2, 0, -1)))
    f = os.path.join(OUT, "cup.step"); cq.exporters.export(body, f); return f

def key_model():
    f = os.path.join(OUT, "key.step"); cq.exporters.export(B.build_key(), f); return f

def bar_model():
    f = os.path.join(OUT, "bar.step"); cq.exporters.export(B.build_bar(), f); return f

which = sys.argv[1:] or ["cup", "key", "bar"]
p = B.P

if "cup" in which:
    step = cup_model()
    a0, a1 = p["pad_deg"]; rp = p["r_pad"]; z0, z1 = p["pad_z"]; d = p["r_arm_in"] + 0.05 - rp
    def on_pad(q):
        r = math.hypot(q[0], q[1]); ang = math.degrees(math.atan2(q[1], q[0]))
        return r <= rp + 0.03 and a0 + 1 <= ang <= a1 - 1 and z0 + d + 0.2 <= q[2] <= z1 - d - 0.2
    def fixed(q):
        r = math.hypot(q[0], q[1])
        return abs(q[1]) >= p["pitch"] / 2 - 0.02 or (q[2] <= 0.02 and r < 13.5) or q[0] <= -1.98
    out = {}
    for dlt in (1.0,):
        r = ccxrun.run(step, "cup", fixed, on_pad, disp=(dlt, None, None), E=E, size=1.1, workdir=OUT, cyl_axis=((0, 0, 0), (0, 0, 1)))
        Fr = None
        # radial reaction: project the global RF on the pad's mid direction
        am = math.radians((a0 + a1) / 2)
        if r["RF"]:
            Fr = r["RF"][0] * math.cos(am) + r["RF"][1] * math.sin(am)
        r["F_radial_N"] = Fr; out[f"delta_{dlt}"] = r
    res["cup"] = out
    print("cup", json.dumps(out, indent=1))

if "key" in which:
    step = key_model()
    hx = p["pill_w"] / 2; u = p["barb_u"]
    def on_barb(q):   # +x barb's outer flat, root-side 0.6 mm: where the slot wall touches first
        return q[0] >= hx + u - 0.03 and p["barb_y"][0] <= q[1] <= p["barb_y"][0] + 0.6
    def fixed(q):
        return q[2] >= p["rigid_bottom"] + 0.5
    need = u - (5.0 - hx)   # deflection to pass a 10.0 mm slot
    r = ccxrun.run(step, "key", fixed, on_barb, disp=(-need, None, None), E=E, size=0.5, workdir=OUT)
    r["deflection_mm"] = need
    res["key"] = r
    print("key", json.dumps(r, indent=1))

if "bar" in which:
    step = bar_model()
    pl, ht = p["prong_len"], p["hook_t"]
    Lb = p["bar_len"]
    def fixed(q):   # prong surfaces bearing on the board: stem bottoms inside the board, hooks' front faces
        return q[1] <= -0.3
    def on_stop(q):  # the channel's stop face (housing tongue rests here)
        return abs(q[2] - (-Lb + p["stop_t"])) < 0.02 and q[1] > p["bar_t"] - p["dt_depth"] - 0.2
    r = ccxrun.run(step, "bar", fixed, on_stop, force=(0, 0, -50.0), E=E, size=1.2, workdir=OUT,
                   extra_fixed=[((-10, -0.01, -Lb - 1, 30, 0.05, -Lb + 40), (2,))])
    res["bar_50N_down"] = r
    print("bar", json.dumps(r, indent=1))

json.dump(res, open(os.path.join(HERE, "fea_results.json"), "w"), indent=1)
