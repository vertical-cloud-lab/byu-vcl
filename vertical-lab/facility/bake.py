"""Bake the pilot cell, PR #318's lab as built by ``setup_lab.build``, into the facility render's assets.

    VLAB_ONLY_TRAYS=CDEFKLM xvfb-run -a python3 facility/bake.py          # -> facility/.cache/baked.pkl

The lab is built once, as every whole-lab clip builds it, and every actor is read back with its group's world matrix,
colour, specular and ambient. Out of it come:

* ``pilot``: the lab's floor markings, its machines, target posts, docks, chargers and safety assets (#379's Class D
  units and signs, the showers, the O2 monitors), in world coordinates. Left out: the two Shuttles (the facility draws
  its own 35 ft ones in their place), the trays (inside the Shuttles; the presented ones are drawn by the film), the
  MiR250 units (the film drives its own), the overhead utilities of the lab's own 36 ft building (cable trays, drops,
  argon line, lights and roof steel: cut off at the cell's edge they hang in mid-air, and the 10.7 m Shuttles run into
  the lights), and the pallet racking round its walls (the warehouse layout's storage, not part of the cell).
* one asset per floor machine (``F.groups``: the rePowder with DAL PR 189's camera units, the Aconity MIDI, the wire
  EDM, the Instron frames, the EOS M 400-4, the Meltio cell, the sieving cell, the fume hood, the DED, the glovebox,
  the packaging station), each in its own frame: the middle of its footprint on the floor at the origin, its front
  (the side a MiR250 docks at) towards -y.
* one asset per loaded tray (``tray_<k>``: the pan, its load, UPS, cameras and dock plate), in the tray's own frame
  (vlm.tray: the middle of the pan's underside at the origin).

See-through parts (sashes, windows, the Shuttles' ghosted skins) are made opaque and tinted: nothing in the facility
film is see-through (a restyle in Higgsfield treats transparency badly; README.md).
"""
from __future__ import annotations

import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(HERE))
os.chdir(LAB)

from assets import Asset, Part, CACHE  # noqa: E402

DROP_Z = 9000.0            # util parts wholly above this (the lab building's lights and roof steel) are left out
SHUTTLE_GROUPS = ("base", "posts", "skin_", "col_", "lift", "drive", "belts", "bay", "console", "shutter", "rails",
                  "extractor", "support", "u2_", "wall")
UNIT_PREFIXES = ("unit0", "unit1", "unit2", "unit3")


def top_group(sc, g):
    while g in sc.parent:
        g = sc.parent[g]
    return g


def chain(sc, g):
    out = [g]
    while g in sc.parent:
        g = sc.parent[g]
        out.append(g)
    return out


def actor_part(sc, name, M=None):
    """The actor's mesh in world coordinates (or through M), with its look, as a Part; None if empty or hidden."""
    import pyvista as pv
    a = sc.actors[name]
    if not a.GetVisibility() or sc.alpha.get(name, 1.0) <= 0.02:
        return None
    m = a.GetMapper()
    poly = m.GetInput() if m is not None else None
    if poly is None or poly.GetNumberOfCells() == 0:
        return None
    mesh = pv.wrap(poly).copy()
    if not isinstance(mesh, pv.PolyData):
        mesh = mesh.extract_surface()
    W = sc.world(sc.group_of[name])
    if M is not None:
        W = M @ W
    mesh = mesh.transform(W, inplace=False)
    pr = a.GetProperty()
    col = tuple(float(c) for c in pr.GetColor())
    op = float(pr.GetOpacity()) * sc.alpha.get(name, 1.0)
    spec = sc.base_alpha.get(name, 1.0)   # placeholder, replaced below
    s = pr.GetSpecular()
    spec = float(min(1.0, (s / 0.30) ** 0.5)) if s > 0 else 0.0
    amb = float(pr.GetAmbient())
    if op < 0.95:                          # glass and ghosts: opaque, tinted towards a dark blue-grey
        k = 0.55
        col = tuple(c * (1 - k) + t * k for c, t in zip(col, (0.32, 0.38, 0.44)))
        spec = max(spec, 0.6)
    role = "glow" if amb >= 0.85 else "solid"
    return Part(mesh.triangulate(), col, spec, min(amb, 0.9), role)


def is_shuttle(g):
    return g.startswith(SHUTTLE_GROUPS) or g in ("logo",) or g.startswith("u2")


def main():
    t0 = time.time()
    import lab
    import setup_lab as SL
    import warehouse as W
    data = lab.meshes()
    idata = SL.load_all()
    sc, L, F, items, rigs, units, util, ulabel, vp = SL.build(data, idata, mp4=False, name="facility_bake")
    sc.apply()
    print(f"built in {time.time() - t0:.0f} s; {len(sc.actors)} actors", flush=True)
    machine_of = {}
    for key, names in F.groups.items():
        for n in names:
            machine_of[n] = key
    import safety
    import safety_other
    keep_util = {f"util/{k}" for k in safety.floor_meshes()} | {f"util/{k}" for k in safety_other.floor_meshes()}
    baked = {"pilot": Asset("pilot"), "machines": {}, "trays": {}, "meta": {}}
    trays = {}
    skipped = {}
    for name in sc.actors:
        g = sc.group_of[name]
        top = top_group(sc, g)
        ch = chain(sc, g)
        if any(c.startswith(UNIT_PREFIXES) for c in ch):
            continue
        tray = next((c for c in ch if c.startswith("tray_") and len(c) == 6), None)
        if tray is not None:
            trays.setdefault(tray, []).append(name)
            continue
        if is_shuttle(top) or top.startswith("beacon"):
            skipped[top] = skipped.get(top, 0) + 1
            continue
        if top in ("floor", "wfloor"):
            continue
        p = actor_part(sc, name)
        if p is None:
            continue
        if g == "util" or top == "util":
            if name not in keep_util or p.mesh.bounds[4] > DROP_Z:
                skipped["util"] = skipped.get("util", 0) + 1
                continue
        if machine_of.get(name) == "racking":
            skipped["racking"] = skipped.get("racking", 0) + 1
            continue
        baked["pilot"].parts.append(p)
        key = machine_of.get(name)
        if key and key not in ("tape", "docks", "chargers", "racking", "vlm2"):
            baked["machines"].setdefault(key, []).append(p)
    print("skipped:", skipped, flush=True)
    # each machine in its own frame: the footprint's middle at the origin, its front towards -y
    from scene import T, R
    for key, parts in list(baked["machines"].items()):
        pts = np.vstack([p.mesh.points for p in parts])
        lo, hi = pts.min(0), pts.max(0)
        row = W.STATIONS.get(key, SL.FLOOR_PLAN.get(key, (None, "N")))[1] if key in SL.FLOOR_PLAN else "N"
        c = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 0.0)
        M = T((-c[0], -c[1], -c[2]))
        if row == "S":
            M = R((0, 0, 1), 180.0) @ M
        a = Asset(key)
        for p in parts:
            a.parts.append(Part(p.mesh.transform(M, inplace=False), p.color, p.specular, p.ambient, p.role))
        lo2, hi2 = a.bounds()
        baked["machines"][key] = a
        baked["meta"][key] = dict(row=row, world_centre=[float(v) for v in c], size=[float(v) for v in hi2 - lo2],
                                  tris=a.n_tris())
        print(f"  machine {key}: row {row}, size {np.round(hi2 - lo2)}, {a.n_tris()} tris", flush=True)
    # each tray in its own frame
    for tray, names in trays.items():
        Mi = np.linalg.inv(sc.world(tray))
        a = Asset(tray)
        for n in names:
            p = actor_part(sc, n, Mi)
            if p is not None:
                a.parts.append(p)
        if a.parts:
            baked["trays"][tray] = a
            print(f"  {tray}: {a.n_tris()} tris", flush=True)
    lo, hi = baked["pilot"].bounds()
    baked["meta"]["pilot"] = dict(lo=[float(v) for v in lo], hi=[float(v) for v in hi], tris=baked["pilot"].n_tris())
    baked["meta"]["dock_n"] = float(W.DOCK_N)
    baked["meta"]["dock_s"] = float(W.DOCK_S)
    baked["meta"]["aisle"] = [float(v) for v in W.AISLE]
    baked["meta"]["chargers"] = [list(W.charger_pose(i)) for i in range(len(W.CHARGERS))]
    baked["meta"]["docks"] = {}
    for key in list(SL.FLOOR_PLAN):
        try:
            baked["meta"]["docks"][key] = list(W.dock_pose(key))
        except Exception:                        # noqa: BLE001
            pass
    baked["meta"]["unit_poses"] = [list(u.pose) for u in units]
    CACHE.mkdir(exist_ok=True)
    (CACHE / "baked.pkl").write_bytes(pickle.dumps(baked))
    print(f"pilot: {baked['pilot'].n_tris()} tris, bounds {np.round(lo)} {np.round(hi)}; "
          f"baked in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
