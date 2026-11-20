"""The safety assets' checks, figures and clip (safety.py has the models; notes/safety.md the write-up).

    python3 safety.py                    # report: NFPA 10 heights, the walk to every unit, the MiR250 with its unit
                                         #   (payload, tipping edges, footprint, the docks again), the BoM -> out/safety.json
    python3 safety.py plan               # out/safety_plan.png
    xvfb-run -a python3 safety.py sheet  # out/safety_assets.png
    xvfb-run -a python3 safety.py photo  # out/safety_b570_vs_amerex.png (Amerex's render is fetched, not committed)
    xvfb-run -a python3 safety.py clip   # out/mp4/safety.mp4, out/safety.gif (VIZ3D_HD=1: out/hd/safety.mp4)
"""
from __future__ import annotations

import heapq
import json
import math
import os
from pathlib import Path

import numpy as np

import safety as S

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
YEL = "#e8c20e"
MARGIN = 30.0                  # setup_lab.check_floor's margin round a MiR250, mm


# ================================================================================================ the floor
# the rePowder as a machine: `fit`'s rectangle for it takes in the bonded floor plates round it (atom_ground), which
# are flush and walked on; the model's own parts, placed at animate.REPOWDER_AT, measured off lab.meshes()'s cache
REPOWDER_RECT = (-4835.0, -2615.0, -2055.0, -700.0)
# chapter 2's two MiR250 spots are on those plates: nothing of ours stands on them
REPOWDER_PLATES = (-4795.0, -2045.0, -3160.0, -1620.0)
RACKING = {"rack W": (-12900.0, -11833.0, -9200.0, 4515.0), "rack E": (11833.0, 12900.0, -9200.0, 4515.0),
           "rack N": (-11000.0, 10944.0, 2800.0, 3867.0)}        # warehouse.RACKS


def floor() -> dict:
    """setup_lab's floor as `fit` last measured it (out/tray_plan.json): machines' plan rectangles, docks, the aisle;
    the rePowder's rectangle cut to the machine (REPOWDER_RECT)."""
    fl = json.loads((OUT / "tray_plan.json").read_text())["floor"]
    fl["machines"]["repowder"] = list(REPOWDER_RECT)
    return fl


def _rect_hit(a, b, m=0.0) -> bool:
    return a[0] < b[1] + m and b[0] < a[1] + m and a[2] < b[3] + m and b[2] < a[3] + m


def _rect_circle(rect, c, r) -> bool:
    x = min(max(c[0], rect[0]), rect[1])
    y = min(max(c[1], rect[2]), rect[3])
    return math.hypot(x - c[0], y - c[1]) < r


def _to_world(local_rect, x, y, hd):
    """A MiR-local rectangle -> world, for a MiR at (x, y) heading hd (0 or 180, as every dock is)."""
    x0, x1, y0, y1 = local_rect
    if abs(hd) < 1:
        return (x + x0, x + x1, y + y0, y + y1)
    return (x - x1, x - x0, y - y1, y - y0)


def place_rects(kind, x, y, face) -> dict:
    """World plan rectangles of a fixed unit: what stands on the floor ("solid") and the keep-clear square ("clear")."""
    if kind == "b570":
        R = S.B570["d"] / 2
        s = S.POST["s"]
        lo, hi = -(s / 2 + 10.0 + 2 * R + 25.0), S.POST["base"] / 2         # the unit's front, the base's back
        k, kw = S.NFPA10["keep_clear"], S.NFPA10["keep_clear_w"]
        sol = (x - 160.0, x + 160.0, y + (lo if face < 0 else -hi), y + (hi if face < 0 else -lo))
        cl = (x - kw / 2, x + kw / 2, y - s / 2 - k, y - s / 2) if face < 0 else (x - kw / 2, x + kw / 2, y + s / 2,
                                                                                  y + s / 2 + k)
        return dict(solid=sol, clear=cl)
    if kind == "680r":
        w = S.W680
        return dict(solid=(x - w["W"] / 2 - 25, x + w["W"] / 2 + 25,
                           *((y - 282.0, y + 632.0) if face < 0 else (y - 632.0, y + 282.0))))
    return dict(solid=(x - 170.0, x + 170.0, y - 160.0, y + 160.0))


def mir_rects(fp) -> list:
    """The MiR250's own outline and its unit's, MiR-local."""
    return [fp["mir"], fp["unit"]]


def dock_check(fl, fp) -> dict:
    """setup_lab.check_floor again, with the unit on the MiR: the docked outline, the approach lane along the dock line
    to the nearest clear pivot spot, and the pivot circle (the new turning radius), against the machines' rectangles
    and the target posts' feet. -> per dock: the pivot then and now, and anything hit."""
    rects = {k: tuple(v) for k, v in fl["machines"].items()}
    feet = {k: (d["target_post"][0] - 150, d["target_post"][0] + 150, d["target_post"][1] - 150,
                d["target_post"][1] + 150) for k, d in fl["docks"].items()}
    r_new = fp["r_turn"]
    out = {}
    for key, d in fl["docks"].items():
        x, y, hd = d["dock"]
        fwd = 1.0 if abs(hd) < 1 else -1.0
        open_dir = fwd if d["backs_in"] else -fwd
        docked = [_to_world(r, x, y, hd) for r in mir_rects(fp)]
        hits = []
        for i, dr in enumerate(docked):
            hits += [f"{'unit' if i else 'MiR'} docked: {k}" for k, rr in rects.items() if _rect_hit(dr, rr, MARGIN)
                     and not (k == key and not i and d["ok"]) and k not in ("vlm", "vlm2") or
                     (k in ("vlm", "vlm2") and _rect_hit(dr, rr, 0.0))]
            hits += [f"{'unit' if i else 'MiR'} docked: post {k}" for k, ff in feet.items() if _rect_hit(dr, ff, 0.0)]
        piv = None
        for dd in np.arange(400.0 + 50.0, 4000.0, 25.0):
            c = (x + open_dir * dd, y)
            if not any(_rect_circle(rr, c, r_new + MARGIN) for rr in rects.values()) and \
                    not any(_rect_circle(ff, c, r_new + MARGIN) for ff in feet.values()):
                piv = c
                break
        if piv is None:
            hits.append("no pivot spot within 4 m")
        else:
            for r in mir_rects(fp):                      # the lane: every position from the dock to the pivot
                a, b = _to_world(r, x, y, hd), _to_world(r, piv[0], piv[1], hd)
                lane = (min(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), max(a[3], b[3]))
                hits += [f"lane: {k}" for k, rr in rects.items() if k != key and _rect_hit(lane, rr, MARGIN)]
                hits += [f"lane: post {k}" for k, ff in feet.items() if k != key and _rect_hit(lane, ff, 0.0)]
        was = set(d["hits"])
        new = sorted({h for h in hits if not any(w in h for w in was)})
        out[key] = dict(dock=d["dock"], backs_in=d["backs_in"], pivot_was=d["pivot"], approach_was=d["approach_mm"],
                        pivot_now=None if piv is None else [round(piv[0]), round(piv[1])],
                        approach_now=None if piv is None else round(abs(piv[0] - x)), hits_before=sorted(was),
                        new_hits=new, ok=not new)
    return out


def places_check(fl, fp) -> list:
    """Each fixed unit against everything it must keep clear of (spot_hits), the other units included."""
    ob = obstacles(fl, fp)
    sols = [place_rects(k, x, y, f)["solid"] for _, k, x, y, f, _ in S.PLACES]
    out = []
    for i, (station, kind, x, y, face, what) in enumerate(S.PLACES):
        others = [s for j, s in enumerate(sols) if j != i]
        hits = spot_hits(kind, x, y, face, ob, others)
        sol = sols[i]
        nearest = min((math.hypot(max(rr[0] - sol[1], 0, sol[0] - rr[1]), max(rr[2] - sol[3], 0, sol[2] - rr[3])), k)
                      for k, rr in ob["rects"].items())
        out.append(dict(station=station, kind=kind, at=[x, y], face=face, covers=what, solid=[round(v) for v in sol],
                        nearest_machine=[round(nearest[0]), nearest[1]], hits=hits, ok=not hits))
    return out


# --------------------------------------------------------------------------------------------- where each goes
def obstacles(fl, fp) -> dict:
    """What a fixed unit must keep clear of, world plan: machines and racking (rects, 50 mm), every docked MiR250 with
    its unit, every approach lane (rects, 30 mm), every pivot circle (centre, r), the target posts' feet (rects, 30 mm),
    and the rePowder's floor plates, where chapter 2's MiR250s park."""
    dk = dock_check(fl, fp)
    rects = {k: tuple(v) for k, v in fl["machines"].items() if not k.startswith("charger")}
    rects.update(RACKING)
    mirs, lanes, circles = {}, {}, {}
    for key, d in dk.items():
        xd, yd, hd = d["dock"]
        for i, r in enumerate(mir_rects(fp)):
            mirs[f"{key}{'+unit' if i else ''}"] = _to_world(r, xd, yd, hd)
            piv = d["pivot_now"] or d["pivot_was"]
            if piv:
                a, b = _to_world(r, xd, yd, hd), _to_world(r, piv[0], piv[1], hd)
                lanes[f"{key}{'+unit' if i else ''}"] = (min(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]),
                                                         max(a[3], b[3]))
        piv = d["pivot_now"] or d["pivot_was"]
        if piv:
            circles[key] = (tuple(piv), fp["r_turn"])
    for i, x in enumerate((-1500.0, -300.0)):             # the chargers: a MiR250 parks on each, its front to the wall
        mirs[f"charger{i}"] = (x - 290.0 - 182.0, x + 290.0, -6238.0 + 20.0, -6238.0 + 820.0)
    feet = {k: (d["target_post"][0] - 150, d["target_post"][0] + 150, d["target_post"][1] - 150,
                d["target_post"][1] + 150) for k, d in fl["docks"].items()}
    # the aisle (MiR250s pass there) and the floor in front of each Shuttle's opening, where Kardex's tray extraction
    # table and its cart go (notes/maintenance.md): kept free, for the unit and its keep-clear area alike
    keep = {"aisle": tuple(fl["aisle_mm"][:2]) + (fl["aisle_mm"][2], fl["aisle_mm"][3])}
    for k, xc in (("Shuttle 1's front", 0.0), ("Shuttle 2's front", 3630.0)):
        keep[k] = (xc - 1225.0, xc + 1225.0, -1562.0 - 1200.0, -1562.0)
    return dict(rects=rects, mirs=mirs, lanes=lanes, circles=circles, feet=feet, plates=REPOWDER_PLATES, keep=keep)


def spot_hits(kind, x, y, face, ob, placed=()) -> list:
    """What a unit at (x, y) facing `face` hits (empty: the spot is good)."""
    pr = place_rects(kind, x, y, face)
    sol, cl = pr["solid"], pr.get("clear")
    h = [f"machine {k}" for k, rr in ob["rects"].items() if _rect_hit(sol, rr, 50.0)]
    h += [f"docked MiR {k}" for k, rr in ob["mirs"].items() if _rect_hit(sol, rr, MARGIN)]
    h += [f"lane {k}" for k, rr in ob["lanes"].items() if _rect_hit(sol, rr, MARGIN)]
    h += [f"pivot {k}" for k, (c, r) in ob["circles"].items() if _rect_circle(sol, c, r + MARGIN)]
    h += [f"post {k}" for k, rr in ob["feet"].items() if _rect_hit(sol, rr, MARGIN)]
    if _rect_hit(sol, ob["plates"], 0.0):
        h.append("the rePowder's floor plates")
    h += [f"{k}" for k, rr in ob["keep"].items() if _rect_hit(sol, rr, 0.0)]
    h += [f"unit {i}" for i, rr in enumerate(placed) if _rect_hit(sol, rr, 50.0)]
    if cl is not None:
        h += [f"keep-clear area: machine {k}" for k, rr in ob["rects"].items() if _rect_hit(cl, rr, 0.0)]
        h += [f"keep-clear area: docked MiR {k}" for k, rr in ob["mirs"].items() if _rect_hit(cl, rr, 0.0)]
        h += [f"keep-clear area: post {k}" for k, rr in ob["feet"].items() if _rect_hit(cl, rr, 0.0)]
        h += [f"keep-clear area: unit {i}" for i, rr in enumerate(placed) if _rect_hit(cl, rr, 0.0)]
        h += [f"keep-clear area: {k}" for k, rr in ob["keep"].items() if _rect_hit(cl, rr, 0.0)]
        if _rect_hit(cl, ob["plates"], 0.0):
            h.append("keep-clear area: the rePowder's floor plates")
    return h


def place_search(station, kind, face, near, box, ob, placed=(), step=50.0):
    """The spot nearest `near` (a station's hazard) inside `box` (x0, x1, y0, y1) where a unit hits nothing."""
    best = None
    for x in np.arange(box[0], box[1] + 1, step):
        for y in np.arange(box[2], box[3] + 1, step):
            d = math.hypot(x - near[0], y - near[1])
            if best is not None and d >= best[0]:
                continue
            if not spot_hits(kind, x, y, face, ob, placed):
                best = (d, float(x), float(y))
    return best


# --------------------------------------------------------------------------------------------- the walk
GRID_MM = 100.0
BOUNDS = (-12500.0, 12500.0, -13000.0, 2500.0)
BODY = 250.0                   # a person's clearance off machines, mm


def walk_field(fl):
    """Walking distance (mm) from the nearest fixed Class D unit to every cell of a 100 mm grid of the floor, round the
    machines (grown by 250 mm for a body). Dijkstra on 8 neighbours. -> (dist, x0, y0)."""
    x0, x1, y0, y1 = BOUNDS
    nx, ny = int((x1 - x0) / GRID_MM) + 1, int((y1 - y0) / GRID_MM) + 1
    xs, ys = x0 + np.arange(nx) * GRID_MM, y0 + np.arange(ny) * GRID_MM
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    block = np.zeros((nx, ny), bool)
    for k, (a, b, c, d) in fl["machines"].items():
        if k.startswith("charger"):
            continue
        block |= (X > a - BODY) & (X < b + BODY) & (Y > c - BODY) & (Y < d + BODY)
    dist = np.full((nx, ny), np.inf)
    pq = []
    for station, kind, x, y, face, _ in S.PLACES:
        if kind == "pail":
            continue
        sx, sy = x, y + face * (450.0 if kind == "b570" else 750.0)          # where a person takes it from
        i, j = int(round((sx - x0) / GRID_MM)), int(round((sy - y0) / GRID_MM))
        dist[i, j] = 0.0
        block[i, j] = False
        heapq.heappush(pq, (0.0, i, j))
    nb = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142),
          (-1, -1, 1.4142)]
    while pq:
        dd, i, j = heapq.heappop(pq)
        if dd > dist[i, j]:
            continue
        for di, dj, w in nb:
            a, b = i + di, j + dj
            if 0 <= a < nx and 0 <= b < ny and not block[a, b]:
                nd = dd + w * GRID_MM
                if nd < dist[a, b]:
                    dist[a, b] = nd
                    heapq.heappush(pq, (nd, a, b))
    return dist, x0, y0, block


def walks(fl) -> dict:
    """Each hazard's walk to the nearest fixed unit, in m and ft, against NFPA 10's 75 ft and the lab's 25 ft."""
    dist, x0, y0, block = walk_field(fl)
    out = {}
    for k, (x, y) in S.HAZARDS.items():
        i, j = int(round((x - x0) / GRID_MM)), int(round((y - y0) / GRID_MM))
        d = dist[i, j]
        if not np.isfinite(d):                    # inside a grown machine: the nearest free cell round it
            best = np.inf
            for di in range(-8, 9):
                for dj in range(-8, 9):
                    a, b = i + di, j + dj
                    if 0 <= a < dist.shape[0] and 0 <= b < dist.shape[1] and np.isfinite(dist[a, b]):
                        best = min(best, dist[a, b] + math.hypot(di, dj) * GRID_MM)
            d = best
        out[k] = dict(m=round(float(d) / 1000, 2), ft=round(float(d) / 304.8, 1),
                      nfpa10_75ft=bool(d <= S.NFPA10["travel_max"]), sop_25ft=bool(d <= S.NFPA10["travel_ideal"]))
    return out


# --------------------------------------------------------------------------------------------- the MiR250
def mir_load(fp) -> dict:
    """The top module's mass with and without the unit against the MiR250's 250 kg, and what the unit does to the
    moment that holds the robot down about each edge of its support (alloy_atomize's model: MASS, BALLAST, WHEELS)."""
    import alloy_atomize as AA
    m = AA.MASS
    before = dict(ur=m["ur10e"], control_box=m["control_box"], cabinet=m["cabinet"], gripper=m["gripper"],
                  on_top=m["on_top"], ballast=round(AA.BALLAST_KG, 1))
    unit = dict(b570=round(S.B570["gross_lb"] * S.LB, 1), bracket_811=round(S.B811["kg"], 1),
                adapter_plate=S.MIR_MOUNT["plate_kg"])
    held = 12.5                                       # the arm's rated payload, the most it could be holding
    s0, s1 = sum(before.values()), sum(before.values()) + sum(unit.values())
    # the unit's centre of mass, MiR-local: each part's mesh centre, weighted
    parts = S.mir_parts()

    def centre(names):
        pts = np.vstack([parts[n][0].points for n in names if n in parts])
        lo, hi = pts.min(0), pts.max(0)
        return (lo + hi) / 2
    c_b = centre([n for n in parts if n.startswith("B570")])
    c_b[2] = S.MIR_MOUNT["z_foot"] + S.B811["t"] + 260.0          # a full shell's centre of mass: low, about 10 in up
    c_k = centre(["811 bracket", "811 strap", "811 latch"])
    c_p = centre(["class D adapter plate"])
    mu = [(unit["b570"], c_b), (unit["bracket_811"], c_k), (unit["adapter_plate"], c_p)]
    mtot = sum(a for a, _ in mu)
    cog = sum(a * c for a, c in mu) / mtot
    ax, ay = AA.WHEELS
    g = 9.81
    edges = {"+x": (ax, (1, 0)), "-x": (-ax, (-1, 0)), "+y": (ay, (0, 1)), "-y": (-ay, (0, -1))}
    dM = {}
    for name, (a, u) in edges.items():
        coord = cog[0] if u[0] else cog[1]
        inward = (a - coord) * (1 if a > 0 else -1)            # mm inside the edge (> 0 holds the robot down)
        dM[name] = round(mtot * g * inward / 1000.0, 1)
    whole = 97.0 + s1
    return dict(payload_kg=dict(before=round(s0, 1), unit=round(sum(unit.values()), 1), after=round(s1, 1),
                                with_held_part=round(s1 + held, 1), limit=AA.MIR250_PAYLOAD,
                                margin_with_held_part=round(AA.MIR250_PAYLOAD - s1 - held, 1)),
                items=dict(before=before, unit=unit), unit_cog_mm=[round(float(v)) for v in cog],
                restoring_moment_change_Nm=dM, whole_robot_kg=round(whole, 1),
                note="restoring moment about each edge of the support rectangle (alloy_atomize.WHEELS, +-325 x "
                     "+-225 mm, an estimate) the unit adds (> 0) or takes away (< 0); the unit hangs 130 mm outside the "
                     "-x (back) edge, so it is the one edge it weakens")


# --------------------------------------------------------------------------------------------- heights, BoM, report
def heights() -> dict:
    """Where the top and bottom of each unit end up, against NFPA 10 (gross weight over 40 lb: top <= 42 in, bottom
    >= 4 in). The B570's 'top' read two ways: the squeeze lever (the highest rigid point) and the hose's loop."""
    b = S.B570
    hang = S.HANG_BOTTOM
    mir_b = S.MIR_MOUNT["z_foot"] + S.B811["t"]
    rows = {}
    for where, z0 in (("on its hook (post or wall)", hang), ("on a MiR250, in the 811", mir_b)):
        rows[where] = dict(bottom_mm=round(z0), lever_top_mm=round(z0 + b["z_lever"]),
                           hose_top_mm=round(z0 + b["z_hose"]),
                           bottom_ok=z0 >= S.NFPA10["bottom_min"],
                           lever_ok=z0 + b["z_lever"] <= S.NFPA10["top_max"],
                           hose_ok=z0 + b["z_hose"] <= S.NFPA10["top_max"])
    return rows


def bom() -> dict:
    n_fixed = sum(1 for p in S.PLACES if p[1] == "b570")
    n_mir = 2
    n_w = sum(1 for p in S.PLACES if p[1] == "680r")
    n_pail = sum(1 for p in S.PLACES if p[1] == "pail")
    rows = [
        ("Amerex B570, 30 lb Class D (Super D), with its wall hook", n_fixed + n_mir, S.B570["price_usd"],
         "Grainger 8C249 (DAL #126)"),
        ("Amerex 811 heavy-duty vehicle bracket (Buckeye 700229)", n_mir, S.B811["price_usd"],
         "Fire Supply Depot (4+: $69.95)"),
        ("Adapter plate for the 811 on the MiR's cabinet, 6 mm 6061, 250 x 470 mm, with 4 x M10 (ours)", n_mir, 60.0,
         "estimate"),
        ("Amerex 680R, 150 lb Class D (Super D) wheeled, argon, 36 in wheels", n_w, S.W680["price_usd"],
         "Tiger Medical sale price (list $16,589.79)"),
        ("Super D Class D powder, 50 lb pail (Brooks 50DPAIL)", n_pail, S.PAIL["price_usd"], "absupply.net"),
        ("Metal scoop for the pail", n_pail, None, "safetyemporium.com 09461, price not found"),
        ("Floor post: 1-5/8 in strut, 2.15 m, post base, 4 wedge anchors, red (ours)", n_fixed, 150.0, "estimate"),
        ("CLASS D sign, 7 x 10 in rigid plastic", n_fixed, 20.0, "estimate (DAL's parts list)"),
        ("Double-sided CLASS D flag sign and its aluminium flag bracket (DAL's)", n_fixed, 35.0, "estimate"),
        ("2 in yellow/black floor tape for the 36 x 36 in keep-clear squares, 108 ft roll", 1, 30.0, "estimate"),
    ]
    total = sum((q * p) for _, q, p, _ in rows if p)
    return dict(rows=[dict(item=i, qty=q, unit_usd=p, source=s) for i, q, p, s in rows], total_usd=round(total, 2),
                annual=("Annual service by a contractor (BYU Risk Management doesn't service Class D; the College's "
                        "industrial hygienist suggested Associated Fire Protection, Salt Lake City); 6-year "
                        "maintenance and 12-year hydrostatic test for dry powder; recharge after any use (B570 manual, "
                        "DAL's mounting study)"))


def report() -> dict:
    fl = floor()
    fp = S.mir_footprint()
    env = S.b570_envelope()
    rep = dict(
        b570=dict(model=S.B570["model"], part_no=S.B570["part_no"], envelope_mm=env,
                  overall_in=[round((env["z"][1] - env["z"][0]) / S.IN, 1), round((env["x"][1] - env["x"][0]) / S.IN, 1),
                              round((env["y"][1] - env["y"][0]) / S.IN, 1)],
                  datasheet_in=[35, 13, 8], cylinder_in=round(S.B570["d"] / S.IN, 2), source=S.B570["source"]),
        heights=heights(), nfpa10=S.NFPA10,
        mir=dict(footprint=fp, load=mir_load(fp)),
        docks=dock_check(fl, fp),
        places=places_check(fl, fp),
        walks=walks(fl),
        bom=bom(),
    )
    rep["docks_ok"] = all(d["ok"] for d in rep["docks"].values())
    rep["places_ok"] = all(p["ok"] for p in rep["places"])
    rep["walks_ok"] = all(w["nfpa10_75ft"] for w in rep["walks"].values())
    path = OUT / "safety.json"
    path.write_text(json.dumps(rep, indent=1, default=float) + "\n")
    print(json.dumps(dict(heights=rep["heights"], footprint=fp, load=rep["mir"]["load"]["payload_kg"],
                          dM=rep["mir"]["load"]["restoring_moment_change_Nm"],
                          docks={k: (d["approach_was"], d["approach_now"], d["new_hits"]) for k, d in rep["docks"].items()},
                          places=[(p["station"], p["kind"], p["hits"], p["nearest_machine"])
                                  for p in rep["places"]],
                          walks=rep["walks"], bom=rep["bom"]["total_usd"]), indent=1, default=float))
    print("->", path.relative_to(HERE))
    return rep


# ================================================================================================ the floor plan
def plan() -> str:
    """out/safety_plan.png: the floor from above, every fixed unit and what it covers, the MiR250s at two docks with
    their units, and the walk to the nearest unit as a field (shaded to 7.6 m, the lab's 25 ft)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, Polygon
    fl = floor()
    fp = S.mir_footprint()
    rep = json.loads((OUT / "safety.json").read_text()) if (OUT / "safety.json").exists() else report()
    dist, x0, y0, block = walk_field(fl)
    fig, ax = plt.subplots(figsize=(19.2, 12.0), dpi=100)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    d = np.where(np.isfinite(dist), dist, np.nan).T / 1000.0
    im = ax.imshow(d, origin="lower", extent=(x0 - 50, x0 + dist.shape[0] * 100 - 50, y0 - 50,
                                              y0 + dist.shape[1] * 100 - 50),
                   cmap="YlOrBr_r", vmin=0, vmax=7.62, alpha=0.38, interpolation="nearest")
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("walk to the nearest fixed Class D unit, m (scale ends at 7.6 m, the lab's 25 ft; NFPA 10 allows "
                 "22.9 m, 75 ft)", fontsize=11, color=INK2)
    names = {"glovebox": "glovebox", "repowder": "rePowder", "sieve_cell": "sieving", "vlm": "Shuttle 1",
             "vlm2": "Shuttle 2", "aconity": "Aconity MIDI", "packaging": "packaging", "instron_floor": "68FM-100",
             "instron_small": "68SC-2", "fumehood": "fume hood", "ded": "MX-Lab DED", "wire_edm": "wire EDM",
             "eos_m400": "EOS M 400-4", "meltio_cell": "Meltio cell"}
    for k, (a, b, c, e) in fl["machines"].items():
        hz = k in S.HAZARDS
        ax.add_patch(Rectangle((a, c), b - a, e - c, facecolor="#d9d7d2" if not hz else "#efe3b0",
                               edgecolor=INK2 if not hz else "#8a6d00", lw=1.0))
        if not k.startswith("charger"):
            ax.text((a + b) / 2, (c + e) / 2, names.get(k, k), ha="center", va="center", fontsize=10, color=INK)
    a0, a1, b0, b1 = fl["aisle_mm"]
    ax.add_patch(Rectangle((a0, b0), a1 - a0, b1 - b0, facecolor="none", edgecolor="#9bb5d6", lw=1.0, ls="--"))
    ax.text(a0 + 200, (b0 + b1) / 2, "aisle, 3.0 m", color="#5a7aa6", fontsize=10, va="center")
    for key, d_ in rep["docks"].items():                           # each dock's MiR250 outline, with its unit
        xd, yd, hd = d_["dock"]
        for i, r in enumerate([fp["mir"], fp["unit"]]):
            w = _to_world(r, xd, yd, hd)
            ax.add_patch(Rectangle((w[0], w[2]), w[1] - w[0], w[3] - w[2], facecolor="none",
                                   edgecolor="#2f6db5" if not i else "#c79a00", lw=0.8, ls=":" if not i else "-"))
        if d_["pivot_now"]:
            ax.add_patch(Circle(d_["pivot_now"], fp["r_turn"], facecolor="none", edgecolor="#2f6db5", lw=0.5,
                                ls=":", alpha=0.6))
    mk = {"b570": dict(marker="o", s=170, c=YEL, edgecolors=INK, zorder=6),
          "680r": dict(marker="s", s=230, c="#f2a900", edgecolors=INK, zorder=6),
          "pail": dict(marker="h", s=150, c="#ffffff", edgecolors="#8a6d00", zorder=6)}
    seen = set()
    for (station, kind, x, y, face, what), pc in zip(S.PLACES, rep["places"]):
        lab = {"b570": "B570 on a post, CLASS D signs, keep-clear square",
               "680r": "680R, 150 lb wheeled", "pail": "Super D pail and scoop"}[kind]
        ax.scatter([x], [y], label=None if kind in seen else lab, **mk[kind])
        seen.add(kind)
        if pc["clear"] if "clear" in pc else False:
            pass
        if kind == "b570":
            cl = place_rects(kind, x, y, face)["clear"]
            ax.add_patch(Rectangle((cl[0], cl[2]), cl[1] - cl[0], cl[3] - cl[2], facecolor="none", edgecolor="#b08a00",
                                   lw=0.8, hatch="////", alpha=0.6))
    for k, (x, y) in S.HAZARDS.items():
        w = rep["walks"][k]
        ax.plot([x], [y], marker="x", color="#b3261e", ms=9, mew=2, zorder=7)
        ax.text(x, y - 330 if y > -5000 else y + 230, f"{w['m']:.1f} m", color="#b3261e", fontsize=10, ha="center",
                zorder=7, fontweight="bold")
    ax.scatter([], [], marker="x", c="#b3261e", label="where the hazard is, and the walk to the nearest unit")
    ax.plot([], [], color="#c79a00", lw=1.2, label="a docked MiR250's B570 in its 811 bracket (behind the MiR)")
    ax.plot([], [], color="#2f6db5", lw=0.8, ls=":", label="docked MiR250s; their turning circles with the unit "
                                                           f"({fp['r_turn']:.0f} mm, was {fp['r_turn_mir']:.0f})")
    ax.set_xlim(-12300, 12300)
    ax.set_ylim(-12900, 2300)
    ax.set_aspect("equal")
    ax.set_xticks(np.arange(-12000, 12001, 2000))
    ax.set_yticks(np.arange(-12000, 2001, 2000))
    ax.tick_params(labelsize=9, colors=INK2)
    ax.grid(color=GRID, lw=0.6)
    for s_ in ax.spines.values():
        s_.set_color(GRID)
    ax.set_xlabel("x, mm (along the aisle)", color=INK2)
    ax.set_ylabel("y, mm", color=INK2)
    worst = max(rep["walks"].values(), key=lambda w: w["m"])
    ax.set_title(f"Class D on the floor: {sum(1 for p in S.PLACES if p[1] == 'b570')} B570s on posts, "
                 f"{sum(1 for p in S.PLACES if p[1] == '680r')} 680Rs, 2 pails, and one B570 on each MiR250. "
                 f"Longest walk from a powder station to a fixed unit: {worst['m']:.1f} m ({worst['ft']:.0f} ft)",
                 fontsize=15, color=INK, loc="left")
    ax.legend(loc="lower right", fontsize=10, frameon=True, facecolor="white", edgecolor=GRID)
    path = OUT / "safety_plan.png"
    fig.savefig(path, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)
    print("->", path.relative_to(HERE))
    return str(path)


# ================================================================================================ 3-D: shots
def _studio(name, size=(1600, 1200)):
    from scene import Scene
    import tour
    sc = Scene(name, name, size=size, gif=False, mp4=False)
    tour.studio(sc, size=60000.0)
    return sc


def add_parts(sc, parts: dict, group: str, M=None, prefix=""):
    """Add {name: (PolyData, material)} to a Scene under `group`, merged by material."""
    by: dict = {}
    for name, (mesh, mat) in parts.items():
        by.setdefault(mat, []).append(mesh if M is None else mesh.transform(M, inplace=False))
    names = []
    for mat, ms in by.items():
        r, g, b, a, spec = S.MATS[mat]
        n = f"{prefix}{group}/{mat}"
        sc.add(n, S._merge(ms), (r, g, b), group, opacity=a, specular=spec)
        names.append(n)
    return names


def _bb(parts, M=None):
    pts = np.vstack([(m if M is None else m.transform(M, inplace=False)).points for m, _ in parts.values()])
    lo, hi = pts.min(0), pts.max(0)
    return (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])


def shot(parts, direction, size=(900, 1200), pad=0.62, look_z=0.45, va=30.0, name="safety_shot", extra=None):
    import tour
    from PIL import Image
    sc = _studio(name, size)
    add_parts(sc, parts, "asset")
    bb = _bb(parts)
    tour.contact_shadow(sc, bb)
    if extra:
        extra(sc)
    sc.cam = tour.frame_cam(bb, direction, pad=pad, look_z=look_z)
    sc.view_angle = va
    img = Image.fromarray(sc.render_base())
    sc.pl.close()
    return img


def sheet() -> str:
    """out/safety_assets.png: the B570 (front and the valve close up), on its post with its signs, the 811 bracket
    empty and holding a B570, the 680R and the pail, each with its figures."""
    from PIL import Image, ImageDraw
    from scene import font, T
    b = S.b570_parts()
    tiles = []
    tiles.append((shot(b, (-0.55, -1.6, 0.35), pad=0.56), "Amerex B570, 30 lb Super D",
                  ["the lab's own Class D unit (DAL #126)", "35 x 13 x 8 in, 50 lb charged, 195 psig",
                   "soft-flow applicator, 3-6 ft, 24 s"]))
    import tour
    valve = {k: v for k, v in b.items()}
    from PIL import Image as _I
    sc = _studio("safety_valve", (900, 1200))
    add_parts(sc, valve, "asset")
    sc.cam = [(-260.0, -520.0, 820.0), (20.0, 0.0, 660.0), (0, 0, 1)]
    sc.view_angle = 30.0
    tiles.append((_I.fromarray(sc.render_base()), "Its valve, close up",
                   ["chrome-plated brass, gauge in the green", "large-loop stainless pin, red tamper seal",
                    "squeeze lever over the carry handle"]))
    sc.pl.close()
    post = S.post_parts()
    tiles.append((shot(post, (-0.9, -1.6, 0.5), pad=0.60, look_z=0.47), "On its post at a station",
                  ["hung from its own hook: lever 826 mm,", "hose loop 1047 mm, bottom 140 mm (NFPA 10)",
                   "CLASS D sign at 60 in, flag at 80 in"]))
    br = S.bracket811_parts(closed=0.0)
    tiles.append((shot(br, (-0.7, -1.6, 0.7), pad=0.70, look_z=0.5), "Amerex 811 vehicle bracket",
                  ["heavy duty, box type, for 30 lb Class D", "17.5 x 8.125 x 8.125 in, 9 lb, rubber-lined",
                   "quick-release strap (shown open)"]))
    held = dict(S.bracket811_parts(closed=1.0))
    Mb = S.b570_in_811()
    for k, (m, mat) in b.items():
        held[k] = (m.transform(Mb, inplace=False), mat)
    tiles.append((shot(held, (-0.8, -1.6, 0.45), pad=0.58), "A B570 in the 811",
                  ["as it rides on each MiR250's back", "strap over the lower band, clear of the label",
                   "standing on the foot plate"]))
    tiles.append((shot(S.w680r_parts(), (-0.9, -1.5, 0.45), pad=0.62), "Amerex 680R, 150 lb wheeled",
                  ["Super D, argon-regulated to 125 psi", "36 in non-sparking wheels, 25 ft hose",
                   "at the rePowder and the EOS"]))
    tiles.append((shot(S.pail_parts(), (-0.8, -1.6, 0.7), pad=0.75, look_z=0.45), "Super D, 50 lb pail",
                  ["the same agent, with a scoop", "for a small spill or a hot spot", "at the rePowder and the MIDI"]))
    W, H = 3600, 2460
    cols = 4
    tw, th = W // cols, 1060
    sheet = Image.new("RGB", (W, H), SURF)
    d = ImageDraw.Draw(sheet)
    d.text((40, 24), "Safety assets: Class D extinguishers, built part by part from Amerex's datasheets and the lab's "
                     "own B570", font=font(54, bold=True), fill=INK)
    for i, (img, title, lines) in enumerate(tiles):
        r, c = divmod(i, cols)
        x, y = c * tw, 110 + r * (th + 120)
        im = img.copy()
        im.thumbnail((tw - 20, th - 20))
        sheet.paste(im, (x + (tw - im.size[0]) // 2, y))
        d.text((x + 30, y + th - 20), title, font=font(36, bold=True), fill=INK)
        for j, t in enumerate(lines):
            d.text((x + 30, y + th + 26 + j * 34), t, font=font(28), fill=INK2)
    # the last tile: the MiR250 view is its own figure (mir_figure); the plan is safety_plan.png
    path = OUT / "safety_assets.png"
    sheet.save(path, optimize=True)
    print("->", path.relative_to(HERE))
    return str(path)


def mir_figure() -> str:
    """out/safety_mir.png: a MiR250 + UR arm with its B570 at the back, from behind and from the side, with its numbers."""
    from PIL import Image, ImageDraw
    import tour
    import warehouse as W
    from scene import font
    rep = json.loads((OUT / "safety.json").read_text())
    shots = []
    for direction, look in (((-1.5, -0.9, 0.55), (-250.0, -60.0, 650.0)), ((0.2, -1.6, 0.45), (-150.0, 0.0, 700.0))):
        sc = _studio("safety_mir", (1400, 1100))
        u = W.Amr(sc, "amr", (0.0, 0.0, 0.0))
        bb = (-600.0, 400.0, -300.0, 300.0, 0.0, 1500.0)
        tour.contact_shadow(sc, bb)
        d_ = np.asarray(direction, float)
        d_ /= np.linalg.norm(d_)
        sc.cam = [tuple(np.asarray(look) + d_ * 3300.0), look, (0, 0, 1)]
        sc.view_angle = 30.0
        shots.append(Image.fromarray(sc.render_base()))
        sc.pl.close()
    fp = rep["mir"]["footprint"]
    ld = rep["mir"]["load"]
    W_, H_ = 2800, 1360
    img = Image.new("RGB", (W_, H_), SURF)
    dr = ImageDraw.Draw(img)
    dr.text((40, 20), "A B570 rides on each MiR250: an 811 bracket on the cabinet's back end, under the arm",
            font=font(48, bold=True), fill=INK)
    for i, s in enumerate(shots):
        img.paste(s, (i * 1400, 90))
    lines = [f"Hangs {fp['behind_mm']:.0f} mm behind the MiR, between y {fp['side'][0]:.0f} and {fp['side'][1]:.0f} mm; "
             f"turning circle {fp['r_turn']:.0f} mm (was {fp['r_turn_mir']:.0f}); its bottom {fp['bottom_mm']:.0f} mm "
             f"up, above the rear scanner",
             f"Payload: {ld['payload_kg']['before']:.0f} kg before, {ld['payload_kg']['after']:.0f} kg with the unit "
             f"({ld['payload_kg']['with_held_part']:.0f} kg holding 12.5 kg) of the MiR250's {ld['payload_kg']['limit']:.0f}",
             "Restoring moment it adds about each edge, N m: " +
             ", ".join(f"{k} {v:+.0f}" for k, v in ld["restoring_moment_change_Nm"].items())]
    for j, t in enumerate(lines):
        dr.text((40, 1200 + j * 44), t, font=font(30), fill=INK2)
    path = OUT / "safety_mir.png"
    img.save(path, optimize=True)
    print("->", path.relative_to(HERE))
    return str(path)


# ================================================================================================ against Amerex's render
AMEREX_PDF = "https://amerex-fire.com/upl/downloads/library/class-d-extinguishers.pdf"


def _amerex_render():
    """Amerex's B570 render and its alpha mask, from the datasheet (fetched to /tmp, not committed)."""
    import subprocess
    from PIL import Image
    d = Path("/tmp/safety_amerex")
    d.mkdir(exist_ok=True)
    pdf = d / "class-d-extinguishers.pdf"
    if not pdf.exists():
        subprocess.run(["curl", "-sSL", "-A", "Mozilla/5.0", "-o", str(pdf), AMEREX_PDF], check=True)
    if not (d / "img-000.png").exists():
        subprocess.run(["pdfimages", "-png", str(pdf), str(d / "img")], check=True)
    return Image.open(d / "img-000.png").convert("RGB"), Image.open(d / "img-001.png").convert("L")


def photo() -> str:
    """out/safety_b570_vs_amerex.png: Amerex's render, the model drawn from the front at the same scale (an
    orthographic camera, the cylinder 272 px across as in the render), and the two silhouettes over each other, with
    their overlap (intersection over union) and where they differ."""
    from PIL import Image, ImageDraw, ImageChops
    from scene import font
    ref, mask = _amerex_render()
    Wr, Hr = ref.size
    s = 272.0 / S.B570["d"]                          # px per mm in the render
    yb = 1272                                        # the cylinder's bottom in the render, px
    xa = 224.5                                       # its axis, px
    sc = _studio("safety_photo", (Wr * 2, Hr * 2))
    add_parts(sc, S.b570_parts(), "asset")
    sc.pl.enable_parallel_projection()
    cz = (yb - Hr / 2) / s                           # the image centre, in mm from the bottom
    cx = (Wr / 2 - xa) / s
    sc.cam = [(cx, -5000.0, cz), (cx, 0.0, cz), (0, 0, 1)]
    sc._set_camera()
    sc.pl.camera.parallel_scale = Hr / 2 / s
    sc.pl.camera.parallel_projection = True
    img = Image.fromarray(sc.render_base()).resize((Wr, Hr), Image.LANCZOS)
    sc.pl.close()
    # the model's silhouette: everything not the studio's white floor/background
    a = np.asarray(img).astype(int)
    mod = (np.abs(a - 255).sum(2) > 40)
    ref_m = np.asarray(mask) > 128
    inter, union = (mod & ref_m).sum(), (mod | ref_m).sum()
    iou = inter / max(union, 1)
    over = np.zeros((Hr, Wr, 3), np.uint8) + 255
    over[ref_m & ~mod] = (220, 60, 50)              # Amerex's only: red
    over[mod & ~ref_m] = (40, 110, 220)             # the model's only: blue
    over[mod & ref_m] = (150, 150, 150)
    W_, H_ = Wr * 3 + 160, Hr + 260
    out = Image.new("RGB", (W_, H_), SURF)
    dr = ImageDraw.Draw(out)
    dr.text((30, 20), "The B570 against Amerex's own render, front view, same scale", font=font(40, bold=True), fill=INK)
    bg = Image.new("RGB", ref.size, (255, 255, 255))
    bg.paste(ref, mask=mask)
    for i, (im, cap) in enumerate(((bg, "Amerex's render (datasheet)"), (img, "the model"),
                                   (Image.fromarray(over), f"overlap {iou:.0%}: red Amerex only, blue model only"))):
        out.paste(im, (40 + i * (Wr + 40), 90))
        dr.text((40 + i * (Wr + 40), 100 + Hr), cap, font=font(24, bold=i == 2), fill=INK)
    dr.text((40, Hr + 150), "Scaled so the cylinder is 7.75 in across (272 px); the render then spans 35.7 x 12.7 in, "
                            "the datasheet 35 x 13 x 8 in. The hose's loop is flexible; the rest is the shape to match.",
            font=font(22), fill=INK2)
    dr.text((40, Hr + 185), f"Source: {AMEREX_PDF} (fetched at run time, not committed)", font=font(20), fill=INK2)
    path = OUT / "safety_b570_vs_amerex.png"
    out.save(path, optimize=True)
    print(f"-> {path.relative_to(HERE)}  IoU {iou:.3f}")
    (OUT / "safety_photo.json").write_text(json.dumps(dict(iou=round(float(iou), 3), px_per_mm=s), indent=1) + "\n")
    return str(path)


# ================================================================================================ the clip
def clip() -> str:
    """A short clip: the B570 turned round with its parts named, its valve, on its post, the 811 taking it, a MiR250
    with its unit and the strap let go, the 680R, the pail."""
    import tour
    import warehouse as W
    from scene import Scene, T, R, FPS
    sc = Scene("safety", "Safety assets: Class D extinguishers, at the stations and on the MiR250s")
    tour.studio(sc, size=60000.0)
    sc.intro = 0.6
    b = S.b570_parts()
    R_ = S.B570["d"] / 2
    # 1. the B570 alone, at the origin
    names_b = add_parts(sc, b, "b570")
    sc.gmat["b570"] = T((0.0, 0.0, 0.0))
    bb = _bb(b)
    tour.contact_shadow(sc, bb, name="shadow b570")
    cam0 = tour.frame_cam(bb, (-0.55, -1.6, 0.35), pad=0.60)
    sc.cam = cam0

    def turn(u):
        sc.gmat["b570"] = R((0, 0, 1), 360.0 * u)
    sc.step("Amerex B570", "The lab's own Class D extinguisher: 30 lb of Super D, a sodium-chloride powder that crusts "
            "over burning metal. Built from Amerex's datasheet and render.", 7.0, turn, hold=0.6,
            labels=[("squeeze lever, pin, gauge", (40.0, -10.0, 690.0), (0.62, 0.20)),
                    ("hose", (-140.0, 0.0, 800.0), (0.18, 0.18)),
                    ("soft-flow applicator", (S.B570["wand_x"], 0.0, 300.0), (0.72, 0.55)),
                    ("lattice bands hold it", (0.0, -R_ - 3.0, 290.0), (0.20, 0.62))])
    sc.step("The valve", "Chrome-plated brass. The gauge reads in the green; a large-loop stainless pin and a red "
            "tamper seal hold the lever.", 3.5, None, hold=1.6,
            cam_to=[(-230.0, -470.0, 800.0), (20.0, 0.0, 660.0), (0, 0, 1)])
    sc.step("The applicator", "Its soft-flow cup lays the powder on gently, so it never blasts burning metal "
            "into the air; it comes off for a straight stream.", 3.5, None, hold=1.6,
            cam_to=[(380.0, -420.0, 260.0), (100.0, 0.0, 110.0), (0, 0, 1)])
    # 2. on its post
    post = S.post_parts(with_unit=True)
    xp = 1600.0
    names_p = add_parts(sc, post, "post")
    sc.gmat["post"] = T((xp, 0.0, 0.0))
    for n in names_p:
        sc.alpha[n] = 0.0
    pb = _bb(post, T((xp, 0.0, 0.0)))
    cam_p = tour.frame_cam(pb, (-0.9, -1.6, 0.5), pad=0.62, look_z=0.47)

    def show_post(u):
        for n in names_p:
            sc.alpha[n] = u
    sc.step("On a post at each station", "Hung from its own hook so its lever is at 826 mm and its hose at "
            "1047 mm: NFPA 10's 42 in for a unit over 40 lb. CLASS D signs at 60 and 80 in, a keep-clear square.",
            4.5, show_post, cam_to=cam_p, hold=1.8)
    # 3. the 811, the strap open, then a B570 set in and strapped
    xb = 3200.0
    states = {}
    for k_, cl in enumerate((0.0, 0.5, 1.0)):
        states[cl] = add_parts(sc, S.bracket811_parts(closed=cl), f"b811_{k_}")
        sc.gmat[f"b811_{k_}"] = T((xb, 0.0, 0.0))
        for n in states[cl]:
            sc.alpha[n] = 0.0
    held = add_parts(sc, b, "b570_811")
    Mb = S.b570_in_811()
    for n in held:
        sc.alpha[n] = 0.0
    cam_b = tour.frame_cam((xb - 200, xb + 200, -260, 60, 0, 950), (-0.8, -1.6, 0.5), pad=0.75, look_z=0.42)

    def bracket_in(u):
        for n in states[0.0]:
            sc.alpha[n] = min(1.0, u * 3)
    sc.step("Amerex 811 vehicle bracket", "Heavy duty, box type, sold for 30 lb Class D units: 17.5 in tall, "
            "rubber-lined, with a quick-release strap.", 3.0, bracket_in, cam_to=cam_b, hold=0.8)

    def set_in(u):
        for n in held:
            sc.alpha[n] = 1.0
        sc.gmat["b570_811"] = T((xb, 0.0, 0.0)) @ T((0.0, -260.0 * (1 - u), 120.0 * (1 - u))) @ Mb
        cl = 0.0 if u < 0.75 else (0.5 if u < 0.88 else 1.0)
        for k_, ns in states.items():
            for n in ns:
                sc.alpha[n] = 1.0 if k_ == cl else 0.0
    sc.step("Strapped in", "It stands on the foot plate, its back on the bushings; the strap goes round above the "
            "lower band, clear of the label, and latches over centre.", 4.0, set_in, hold=1.2)
    # 4. the MiR250 with its unit (props.mir250 carries it); the strap let go and the unit lifted out
    xm = 5400.0
    u_ = W.Amr(sc, "amr", (xm, 0.0, 0.0))
    for n in u_.names():
        if "class D" in n:
            pass
    mir_cam = [(xm - 2900.0, -2300.0, 1700.0), (xm - 250.0, -80.0, 700.0), (0, 0, 1)]
    sc.step("On every MiR250", "Each MiR250 carries one in an 811 on its cabinet's back end, under the arm and above "
            "its rear scanner, wherever the robot works.", 4.5, None, cam_to=mir_cam, hold=1.4,
            labels=[("B570 in its 811", (xm - 470.0, -110.0, 700.0), (0.30, 0.30))])
    mir_unit = [n for n in sc.actors if n.startswith("amr/amr class D ") and any(
        t in n for t in ("cd_yellow", "chrome", "rubber", "black_plastic", "handle", "gauge", "label", "print", "star",
                         "seal", "steel"))]
    # only the B570's own materials lift out (the 811's black and the adapter's aluminium stay): split by group
    lift_names = []
    for n in mir_unit:
        lift_names.append(n)
    sc.step("Available for use", "Anyone near the robot takes it: throw the strap's latch, lift it off the foot plate "
            "and go. It is 50 lb, so it hangs low.", 3.5, None, hold=1.0,
            cam_to=[(xm - 1700.0, -1300.0, 1150.0), (xm - 470.0, -110.0, 650.0), (0, 0, 1)])
    # 5. the 680R and the pail
    xw = 7600.0
    w = S.w680r_parts()
    names_w = add_parts(sc, w, "w680")
    sc.gmat["w680"] = T((xw, 0.0, 0.0))
    for n in names_w:
        sc.alpha[n] = 0.0
    wb = _bb(w, T((xw, 0.0, 0.0)))
    tour.contact_shadow(sc, wb, name="shadow 680")
    pa = S.pail_parts()
    names_pa = add_parts(sc, pa, "pail")
    sc.gmat["pail"] = T((xw + 750.0, -200.0, 0.0))
    for n in names_pa:
        sc.alpha[n] = 0.0
    cam_w = tour.frame_cam((wb[0], wb[1] + 900.0, wb[2], wb[3], wb[4], wb[5]), (-0.9, -1.6, 0.45), pad=0.66)

    def show_w(u):
        for n in names_w + names_pa:
            sc.alpha[n] = min(1.0, u * 2)
    sc.step("Where the most powder is", "An Amerex 680R: 150 lb of the same agent, argon-regulated to 125 psi, on "
            "36 in non-sparking wheels, at the rePowder and the EOS. A 50 lb pail of it with a scoop beside.",
            5.0, show_w, cam_to=cam_w, hold=2.0)
    sc.step("", "", 1.0, None, hold=0.5)
    sc.save()
    return str(OUT / "mp4" / "safety.mp4")


def main(what: str):
    if what == "report":
        report()
    elif what == "plan":
        plan()
    elif what == "sheet":
        sheet()
    elif what == "mir":
        mir_figure()
    elif what == "photo":
        photo()
    elif what == "clip":
        clip()
    elif what == "all":
        report()
        plan()
        sheet()
        photo()
        mir_figure()
    else:
        raise SystemExit(f"unknown: {what}")
