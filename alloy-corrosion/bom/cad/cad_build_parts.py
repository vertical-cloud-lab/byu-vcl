"""The printed parts the corrosion BOM needs that had no CAD yet. CadQuery 2.8.

Reuses the helpers, parameters and well-lid code of ../../copper/cad/cad_cu_cell.py, so the
cups and lids here share the cell's boss, bore and magnet layout exactly. Writes one STEP and
one STL per part into this folder, and build_parts.json (what each part is, where it goes,
its key numbers).

Parts:
- well_lid_v2_006 / _008 / _010: the well lid with a thicker counterbore ceiling (see below),
  for the AS568-006 main wells and the -008 / -010 calibration wells.
- cup_block_3: rinse 2 (ASW), rinse 1 (DI) and the park cup, each with the lid's 16 mm boss, so the
  electrode cap seats on a cup exactly as it seats on a well.
- tip_waste_cup, tube_rack_2x8, tip_rack_2x15.
- bench_cell_body / _clamp / _cover: the 0.92 cm2 bulk cell for the copper calibration.

Why a v2 lid. In ../../copper/cad/well_lid the O-ring's squeeze reaction (10-51 N, 23.6 N
nominal) bears on a 0.2 mm printed ledge between the counterbore (z 0-1.40) and the 8 mm bore
(from z 1.60). Treated as an annular plate clamped at r 3.8 and free at the 1.45 mm throat, that
ledge sees about 200 MPa at the nominal load (PETG yields near 50 MPa) and would lift 0.66 mm,
more than the ring's 0.38 mm squeeze. v2 adds a 0.4 mm step under the bore (a 4.0 mm hole from
z 1.60 to 2.00, the 8 mm bore from 2.00), so the ceiling is 0.6 mm thick from r 2.0 outward:
about 24 MPa nominal and 0.03 mm lift. At the worst-case 51 N (80 A rubber, a thick ring, a
shallow counterbore) it reaches PETG's yield. It clears the electrode carrier's legs (bottom at W z 2.2) by 0.2 mm and the coil by 0.28 mm. The liquid path to the
spot is now a 0.2 mm throat plus a 0.4 mm-long 4 mm neck, so ../../copper/sim_well_hf.py's
geometry no longer matches the lid exactly. ledge_check() below holds the numbers.

    python cad_build_parts.py      # about 30 s
"""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("cad_cu_cell", HERE.parents[1] / "copper" / "cad" / "cad_cu_cell.py")
cell = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cell)
cyl, boxs, rev, polar, union = cell.cyl, cell.boxs, cell.rev, cell.polar, cell.union
P = cell.P

CS = 1.78                                                      # AS568 dash 0xx cross-section
ORINGS = {"006": 2.90, "008": 4.47, "010": 6.07, "013": 10.82}  # IDs, mm
CBORE_CLEAR = round(P["cbore_d"] - (P["face_oring_id"] + 2 * CS), 3)  # 0.84: the -006 lid's diametral clearance
STEP_D, STEP_TOP = 4.0, 2.0                                    # v2: the neck under the bore

# Deck positions, CubOS frame of Ben's 2026-10-02 calibration (../../plot_deck_layout.py, ../../copper/deck_cu.py)
CUP_X, CUP_Y, CUP_SEAT_Z = (30.0, 60.0, 90.0), 245.0, 45.0
TUBE_X, TUBE_Y, TUBE_RECT = [176.0 + 12.0 * k for k in range(8)], (28.0, 46.0), (170.0, 20.0, 266.0, 54.0)
RACK2_A1, RACK2_A2, PITCH, ROWS = (108.0, 89.0), (99.5, 89.0), 8.5, 15

# Tube and tip fits. Measured values replace these; print the fit strips first.
# Eppendorf Safe-Lock 0.5 mL (technical data sheet): 7.8 mm OD under a 2 mm rim of about 9.6 mm, 30 mm rim top to tip.
# Plate top 30 puts the rims at 32, the tube-rack top the deck checks use; the tips clear the base by 0 to 1 mm.
TUBE = dict(body_d=7.8, hole_d=8.2, below_rim=28.0, plate_top=30.0)  # 0.5 mL PP tube hanging by its rim
# Opentrons 20 uL tip: 39.2 mm long, 3.27 mm ID at the top (labware definition); its OD and collar are not published.
TIP = dict(hole_d=5.0, plate_top=64.7)  # the collar rests on the plate; tip tops at about Ben's 66


# ------------------------------------------------------------------ parts
def well_lid_v2(dash):
    """W frame: the copper cell's well lid for AS568-<dash>, with the 0.4 mm step under the bore."""
    idd = ORINGS[dash]
    saved = dict(P)
    P.update(face_oring_id=idd, throat_d=idd, cbore_d=round(idd + 2 * CS + CBORE_CLEAR, 3))
    try:
        lid = cell.well_lid()
        cbore_d = P["cbore_d"]
    finally:
        P.clear()
        P.update(saved)
    neck = max(STEP_D, idd)
    step = cyl(P["bore_d"], P["throat_top"], STEP_TOP).cut(cyl(neck, P["throat_top"] - 1, STEP_TOP + 1))
    return lid.fuse(step).clean(), {"oring": f"AS568-{dash}", "oring_id": idd, "cbore_d": cbore_d, "cbore_h": P["cbore_h"],
                                    "throat_d": idd, "neck_d": neck, "neck_z": [P["throat_top"], STEP_TOP],
                                    "squeeze_pct": round(100 * (CS - P["cbore_h"]) / CS, 1),
                                    "nominal_area_cm2": round(math.pi / 4 * idd ** 2 / 100, 4)}


def boss_at(x, y, z):
    p = P
    b = rev([(0, -0.01), (p["boss_d"] / 2, -0.01), (p["boss_d"] / 2, p["boss_h"] - p["boss_chamfer"]),
             (p["boss_d"] / 2 - p["boss_chamfer"], p["boss_h"]), (0, p["boss_h"])])
    return b.translate(cq.Vector(x, y, z))


def cup_block():
    """D frame. Three towers on one base; each top is the well lid's seat plane, boss and magnet pockets."""
    p = P
    floor = 8.0
    body = union(boxs(CUP_X[0] - 16, CUP_Y - 14, 0, CUP_X[-1] + 16, CUP_Y + 14, 3.0),
                 *[cyl(26.0, 0, CUP_SEAT_Z, x, CUP_Y) for x in CUP_X],
                 *[boss_at(x, CUP_Y, CUP_SEAT_Z) for x in CUP_X])
    for x in CUP_X:
        body = body.cut(cyl(p["bore_d"], floor, CUP_SEAT_Z + p["boss_h"] + 1, x, CUP_Y))
        for ang in p["hold_angles"]:
            mx, my = polar(p["hold_r"], ang)
            z1 = CUP_SEAT_Z - p["hold_skin"]
            body = body.cut(cyl(p["hold_mag_d"] + 0.1, z1 - p["hold_mag_h"] - 0.1, z1, x + mx, CUP_Y + my))
    cap_floor = CUP_SEAT_Z - (p["lid_top"] - p["leg_bottom_w"])  # deck z of the carrier legs' bottom, cap seated
    fill_top = CUP_SEAT_Z + p["boss_h"] - 2.0
    meta = {"positions_xy": [[x, CUP_Y] for x in CUP_X], "roles": ["rinse 2 (ASW)", "rinse 1 (DI)", "park (reference storage)"],
            "seat_z": CUP_SEAT_Z, "boss_top_z": CUP_SEAT_Z + p["boss_h"], "reservoir": f"{p['bore_d']} mm bore from z {floor}",
            "fill_ul_to_2mm_below_boss_top": round(math.pi / 4 * p["bore_d"] ** 2 * (fill_top - floor)),
            "electrodes_lowest_z_seated": round(cap_floor, 2)}
    return body.clean(), meta


def tip_waste_cup(cx=385.0, cy=150.0):
    """D frame, at the copper deck's tip-waste position (the aluminium deck's is (335, 40))."""
    cup = union(cyl(30.0, 0, 50.0, cx, cy), cyl(44.0, 0, 2.5, cx, cy))
    return cup.cut(cyl(30.0 - 2 * 1.6, 3.0, 60.0, cx, cy)).clean()


def tube_rack():
    """D frame. 2 x 8 open 0.5 mL tubes hanging by their rims from a plate at z 31; open front and back
    so the hinged caps fold down over the edges (front row forward, back row back)."""
    x0, y0, x1, y1 = TUBE_RECT
    t = TUBE
    top0 = t["plate_top"] - 2.5
    body = union(boxs(x0, y0, 0, x1, y1, 2.0), boxs(x0, y0, top0, x1, y1, t["plate_top"]),
                 boxs(x0, y0, 0, x0 + 3, y1, t["plate_top"]), boxs(x1 - 3, y0, 0, x1, y1, t["plate_top"]),
                 boxs(217.0, y0 + 2, 0, 219.0, y1 - 2, t["plate_top"]))
    for x in TUBE_X:
        for y in TUBE_Y:
            body = body.cut(cyl(t["hole_d"], top0 - 1, t["plate_top"] + 1, x, y))
            body = body.cut(cyl(t["body_d"] - 3.0, 1.0, 3.0, x, y))  # clears the tube's tip if it bottoms out
    try:  # tube numbers, engraved 0.4 mm, between the rows
        for k, x in enumerate(TUBE_X):
            for n, y in ((k + 1, 34.2), (k + 9, 39.8)):
                txt = cq.Workplane("XY").workplane(offset=t["plate_top"] - 0.4).center(x, y).text(str(n), 3.2, 0.5, kind="bold").val()
                body = body.cut(txt)
        labels = True
    except Exception:  # no font on this machine: plain plate
        labels = False
    return body.clean(), {"tube_xy": [[x, y] for y in TUBE_Y for x in TUBE_X], "plate_top_z": t["plate_top"],
                          "hole_d": t["hole_d"], "labels": labels}


def tip_rack():
    """D frame. The second 2 x 15 rack at A1 (108, 89), A2 (99.5, 89), rows +y at 8.5 mm: 138 x 20 mm,
    as panda_2x15_tip_rack in Ben's deck file."""
    xs = (RACK2_A2[0], RACK2_A1[0])
    cx = sum(xs) / 2
    ya = RACK2_A1[1]
    y0, y1 = ya - (138.0 - (ROWS - 1) * PITCH) / 2, ya + (ROWS - 1) * PITCH + (138.0 - (ROWS - 1) * PITCH) / 2
    x0, x1 = cx - 10.0, cx + 10.0
    top = TIP["plate_top"]
    body = union(boxs(x0, y0, 0, x1, y1, 2.0), boxs(x0, y0, top - 3.0, x1, y1, top),
                 boxs(x0, y0, 0, x0 + 2.0, y1, top), boxs(x1 - 2.0, y0, 0, x1, y1, top),
                 boxs(x0, y0, 0, x1, y0 + 2.0, top), boxs(x0, y1 - 2.0, 0, x1, y1, top))
    for r in range(ROWS):
        for x in xs:
            body = body.cut(cyl(TIP["hole_d"], top - 4.0, top + 1.0, x, ya + r * PITCH))
    return body.clean(), {"rect": [x0, y0, x1, y1], "a1": list(RACK2_A1), "a2": list(RACK2_A2), "plate_top_z": top,
                          "hole_d": TIP["hole_d"]}


def fit_strip(kind):
    """A short strip of holes in 0.2 mm steps, to pick hole_d for the real tubes or tips before the full print."""
    ds = [7.8 + 0.2 * k for k in range(6)] if kind == "tube" else [4.2 + 0.2 * k for k in range(7)]
    pitch = 12.0 if kind == "tube" else 8.5
    strip = boxs(0, 0, 0, pitch * len(ds) + 4, 14.0, 3.0)
    for k, d in enumerate(ds):
        strip = strip.cut(cyl(d, -1, 4, 2 + pitch * (k + 0.5), 7.0))
    return strip.clean(), [round(d, 2) for d in ds]


def bench_cell():
    """Cell frame: z 0 is the coupon face (the body's underside). A 250 mL flat cell: the AS568-013 face seal
    in the floor's underside, a 0.6 mm throat, then a 45 degree cone so the 0.92 cm2 spot sees the bulk."""
    idd = ORINGS["013"]
    cbore_d, cbore_h = round(idd + 2 * CS + CBORE_CLEAR, 3), P["cbore_h"]
    r_in, r_out, h, floor = 30.0, 33.0, 90.0, 8.0
    body = cyl(2 * r_out, 0, h)
    body = body.cut(cyl(2 * r_in, floor, h + 1))
    body = body.cut(cyl(cbore_d, -1, cbore_h))
    rw = idd / 2
    body = body.cut(rev([(0, cbore_h - 0.01), (rw, cbore_h - 0.01), (rw, cbore_h + 0.6),
                         (rw + floor - cbore_h - 0.6 + 0.01, floor + 0.01), (0, floor + 0.01)]))
    screws = [(sx * 17.0, sy * 17.0) for sx in (-1, 1) for sy in (-1, 1)]
    for x, y in screws:
        body = body.cut(cyl(P["insert_d"], -1, 6.0, x, y))  # M3 heat-set inserts from below, 2 mm under the liquid
    # clamp plate: coupon pocket on top, WE spring pin through its floor, M3 x 8 from below in 5 mm counterbores
    plate = boxs(-23, -23, -8.0, 23, 23, 0)
    q = P["pocket"] / 2
    plate = plate.cut(boxs(-q, -q, -6.0, q, q, 1))
    for cx_, cy_ in ((-q, -q), (q, -q), (-q, q), (q, q)):
        plate = plate.cut(cyl(1.6, -6.0, 1, cx_, cy_))
    plate = plate.cut(boxs(2.0, q - 0.1, -5.0, 6.0, q + 2.0, 1))  # pry slot
    plate = plate.cut(cyl(P["we_pin_hole"], -9, -5.9))
    plate = plate.cut(boxs(-2.0, -2.0, -9, 2.0, 24, -8.0 + 3.0))  # wire channel out to the +y edge
    for x, y in screws:
        plate = plate.cut(cyl(3.4, -9, 1, x, y))
        plate = plate.cut(cyl(6.5, -9, -8.0 + 5.0, x, y))  # 3 mm under the head: an M3 x 8 engages 5 mm
    # loose cover: a 70 mm disc with a 4 mm skirt; holes for a 10 mm graphite counter, a 6 mm reference, a spare, a vent
    cover = cyl(70.0, h, h + 3.0).fuse(cyl(70.0, h - 4.0, h + 0.01).cut(cyl(2 * r_out + 0.8, h - 5, h + 1))).clean()
    for d, x, y in ((12.5, 0, 12.0), (6.5, -14.0, -6.0), (4.0, 14.0, -6.0), (2.0, 0, -20.0)):
        cover = cover.cut(cyl(d, h - 1, h + 4, x, y))
    vol_ml = math.pi * r_in ** 2 * (h - floor - 10.0) / 1000
    return body.clean(), plate.clean(), cover, {
        "oring": "AS568-013", "oring_id": idd, "cbore_d": cbore_d, "cbore_h": cbore_h,
        "squeeze_pct": round(100 * (CS - cbore_h) / CS, 1), "nominal_area_cm2": round(math.pi / 4 * idd ** 2 / 100, 3),
        "inner_d": 2 * r_in, "height": h, "floor": floor, "fill_ml_to_10mm_below_rim": round(vol_ml),
        "screws": "4 x M3 x 8 into heat-set inserts at (+/-17, +/-17)",
        "cover_holes": "12.5 mm: graphite counter (10 mm rod); 6.5 mm: reference (Ossila C2015B1 is 6 mm); 4.0 mm: spare; 2.0 mm: vent"}


# ------------------------------------------------------------------ the ledge check
def ledge_stress(a, b, r0, t, W, E=2.0e3, nu=0.38):
    """Annular plate, outer edge a clamped, inner edge b free, ring load W (N) at r0; mm, MPa.
    Returns the edge bending stress and the lift at r0 (Kirchhoff plate, closed form)."""
    D = E * t ** 3 / (12 * (1 - nu ** 2))
    k = W / (2 * math.pi * D)
    A = np.array([[a / 2, 1 / a, 0, 0],
                  [0, 0, (1 + nu) / 2, (nu - 1) / b ** 2],
                  [r0 / 2, 1 / r0, -r0 / 2, -1 / r0],
                  [(1 + nu) / 2, (nu - 1) / r0 ** 2, -(1 + nu) / 2, -(nu - 1) / r0 ** 2]])
    rhs = np.array([k * (a / 2 * math.log(a) - a / 4), 0, k * (r0 / 2 * math.log(r0) - r0 / 4),
                    k * ((0.5 * math.log(r0) + 0.25) + nu * (0.5 * math.log(r0) - 0.25))])
    C1, C2, C3, C4 = np.linalg.solve(A, rhs)
    th = lambda r: (-k * (r / 2 * math.log(r) - r / 4) + C1 * r / 2 + C2 / r) if r >= r0 else (C3 * r / 2 + C4 / r)
    dth_a = -k * (0.5 * math.log(a) + 0.25) + C1 / 2 - C2 / a ** 2
    Ma = -D * (dth_a + nu * th(a) / a)
    rs = np.linspace(a, r0, 400)
    lift = abs(np.trapezoid([th(r) for r in rs], rs))
    return 6 * abs(Ma) / t ** 2, lift


def ledge_check():
    loads = {"low": 10.0, "nominal": 23.6, "high": 51.0}  # ../../copper/cad/cad_check.json face seal, 70-80 A and tolerances
    r0 = P["face_oring_id"] / 2 + CS / 2
    out = {"model": "annular Kirchhoff plate, clamped at r 3.8 (between the 3.65 counterbore wall and the 4.0 bore), free at the "
                    "inner edge, the O-ring's reaction as a ring load at its centre radius 2.34; PETG E 2 GPa, nu 0.38; yield about 50 MPa",
           "squeeze_mm": round(CS - P["cbore_h"], 2)}
    for name, (t, b) in {"v1_0.2mm": (0.2, 1.45), "v2_0.6mm": (0.6, STEP_D / 2)}.items():
        out[name] = {k: dict(zip(("edge_stress_MPa", "lift_at_ring_mm"), [round(v, 3) for v in ledge_stress(3.8, b, r0, t, W)]))
                     for k, W in loads.items()}
    return out


# ------------------------------------------------------------------ export
def export(name, shape, what, place, tol=0.03, extra=None):
    cq.exporters.export(cq.Workplane().add(shape), str(HERE / f"{name}.step"))
    cq.exporters.export(cq.Workplane().add(shape), str(HERE / f"{name}.stl"), tolerance=tol, angularTolerance=0.25)
    bb = shape.BoundingBox()
    return {"step": f"{name}.step", "stl": f"{name}.stl", "what": what, "place": place,
            "bbox_mm": [round(v, 2) for v in (bb.xlen, bb.ylen, bb.zlen)], "volume_cm3": round(shape.Volume() / 1000, 2),
            **(extra or {})}


def main():
    parts = {}
    for dash in ("006", "008", "010"):
        lid, m = well_lid_v2(dash)
        parts[f"well_lid_v2_{dash}"] = export(f"well_lid_v2_{dash}", lid, f"well lid v2 for AS568-{dash}",
                                              "W frame: on the coupon face; deck = W + (station x, 240, 20)", 0.02, m)
    body, m = cup_block()
    parts["cup_block_3"] = export("cup_block_3", body, "rinse 2, rinse 1 and park cups with the lid's boss", "D frame, as is", 0.03, m)
    parts["tip_waste_cup"] = export("tip_waste_cup", tip_waste_cup(), "tip waste, 30 mm, top z 50",
                                    "D frame at the copper deck's (385, 150); the aluminium deck's is (335, 40)")
    body, m = tube_rack()
    parts["tube_rack_2x8"] = export("tube_rack_2x8", body, "2 x 8 rack for open 0.5 mL tubes", "D frame, as is", 0.03, m)
    body, m = tip_rack()
    parts["tip_rack_2x15"] = export("tip_rack_2x15", body, "second 2 x 15 tip rack (Ben's 138 x 20 footprint)", "D frame, as is", 0.03, m)
    for kind in ("tube", "tip"):
        s, ds = fit_strip(kind)
        parts[f"fit_strip_{kind}"] = export(f"fit_strip_{kind}", s, f"{kind} fit test: holes " + ", ".join(f"{d:.1f}" for d in ds) + " mm",
                                            "bench only", 0.02, {"hole_d": ds})
    body, plate, cover, m = bench_cell()
    parts["bench_cell_body"] = export("bench_cell_body", body, "250 mL flat cell, AS568-013 window in the floor", "bench", 0.03, m)
    parts["bench_cell_clamp"] = export("bench_cell_clamp", plate, "clamp plate: 20 x 20 coupon pocket, WE spring pin, 4 x M3 x 8", "bench")
    parts["bench_cell_cover"] = export("bench_cell_cover", cover, "loose cover: 10 mm counter and 6 mm reference holes, a spare, a vent", "bench")
    meta = {"units": "mm", "made_by": "cad_build_parts.py (CadQuery " + cq.__version__ + ")", "ledge_check": ledge_check(),
            "fits_to_measure": {"tube": TUBE, "tip": TIP}, "parts": parts}
    (HERE / "build_parts.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta["ledge_check"], indent=1))
    for k, v in parts.items():
        print(f"{k:22s} {v['bbox_mm']} {v['volume_cm3']} cm3")


if __name__ == "__main__":
    main()
