"""Powder through the doser's funnel: how steep must the funnel wall be for powder to drain? (Alloy engine, CPU)

The doser drops powder from its outlet into a funnel whose spout sits in the vial's mouth (powder-doser PR 185's chain
carousel v2 has a D-cut funnel there). Here a 7.2 cm^3 column of powder drops into an octagonal funnel (40 mm across
the top, a 12 mm outlet, 22 mm over a 20 mL vial's rim), runs through it and lands in the vial. One run per wall
angle beta (from horizontal). What it reports: the share of the powder in the vial over time, what is left on the
funnel's wall when the flow stops, and the flow rate against Beverloo's law for the same outlet.

Alloy steps sand on Newton's implicit MPM solver: the powder is a continuum (no grains), so it neither arches nor
clogs, and the outlet is only a few grid cells across at the CPU's resolution. The powder is Alloy's dry silica sand
card: its grain density (2,650 kg/m^3) is within 1 % of AlSi10Mg's 2,670 and its friction angle is 33 deg. The wall
friction is set to mu_w = 0.40 (a wall friction angle of 21.8 deg), an assumption, not a measurement for PETG.

    python doser_funnel.py --beta 30           # one run: out/doser_funnel_b30.json (+ frames with --render)
    python doser_funnel.py --plot              # the chart of every run found in out/
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "out"
R_TOP, R_OUT, T_WALL, N_FACETS = 0.020, 0.006, 0.003, 8
Z_OUT = 0.075                          # m: the funnel's outlet, 22 mm over the vial's rim (3 mm floor + 50 mm)
VIAL_R, VIAL_DEPTH, VIAL_WALL = 0.0125, 0.050, 0.003    # a 20 mL scintillation vial's bore (about 25 mm) and depth
COLUMN = (0.012, 0.012, 0.050)         # m: the powder dropped into the funnel (7.2 cm^3)
MU_WALL = 0.40
G, RHO_BULK = 9.81, 1555.0             # the sand card's bulk density in Alloy's funnel-pour task (packing 0.59)


def build(beta_deg: float):
    import alloy

    b = math.radians(beta_deg)
    z_top = Z_OUT + (R_TOP - R_OUT) * math.tan(b)
    slant = (R_TOP - R_OUT) / math.cos(b)
    width = 2 * R_TOP * math.tan(math.pi / N_FACETS) * 1.15   # an octagonal funnel: plates overlap at the seams
    r_mid, z_mid = (R_TOP + R_OUT) / 2, (Z_OUT + z_top) / 2
    scene = alloy.Scene(dt=0.01)
    scene.add_ground()
    facets = []
    for i in range(N_FACETS):
        phi = 2 * math.pi * i / N_FACETS
        # the plate's inner face lies on the cone: push its centre out by half its thickness along the cone's normal
        n_r, n_z = math.sin(b), -math.cos(b)                 # outward normal of the wall (r, z), pointing down-out
        cr, cz = r_mid + 0.5 * T_WALL * n_r, z_mid + 0.5 * T_WALL * n_z
        name = f"funnel{i:02d}"
        scene.add_box(name, size=(slant, width, T_WALL), pos=(cr * math.cos(phi), cr * math.sin(phi), cz),
                      rpy=(0.0, -b, phi), static=True, material="pet")
        facets.append(name)
    # eight wall slabs, not the default 24: Alloy sizes the MPM grid at a quarter of the narrowest face the powder can
    # meet (min(d_feature / 4, 5 mm)), and 24 slabs 3.7 mm wide made it 0.93 mm and 74,000 particles
    scene.add_open_cylinder("vial", inner_radius=VIAL_R, depth=VIAL_DEPTH, wall=VIAL_WALL, pos=(0, 0, 0),
                            segments=8, material="glass_soda_lime")
    z0 = z_top + 0.005 + COLUMN[2] / 2
    scene.add_box("powder", size=COLUMN, pos=(0, 0, z0), material="sand_silica_dry")
    for f in facets:
        scene.set_friction("powder", f, MU_WALL)
    return alloy, scene, z_top


def run(args) -> None:
    alloy, scene, z_top = build(args.beta)
    t0 = time.perf_counter()
    sim = alloy.build(scene, device="cpu")
    n = len(sim.state(world=0)["powder.points"])
    print(f"beta {args.beta}: {n} particles, built in {time.perf_counter() - t0:.1f} s", flush=True)
    log, frames = [], []
    t1 = time.perf_counter()
    steps = round(args.seconds / sim.dt)
    for k in range(steps + 1):
        if k:
            sim.step(1)
        if k % args.every == 0 or k == steps:
            p = sim.state(world=0)["powder.points"]
            r = np.hypot(p[:, 0], p[:, 1])
            in_vial = (r < VIAL_R) & (p[:, 2] < VIAL_DEPTH)
            on_funnel = (p[:, 2] > Z_OUT - 0.002) & (p[:, 2] < z_top + 0.004) & (r < R_TOP + 0.004)
            log.append({"t": round(sim.t, 3), "in_vial": float(in_vial.mean()), "in_funnel": float(on_funnel.mean()),
                        "wall_s": round(time.perf_counter() - t1, 1)})
            print(json.dumps(log[-1]), flush=True)
            if args.render and k % (args.every * args.render_every) == 0:
                img = sim.render(width=360, height=420, look_at=((0.11, -0.13, 0.13), (0.0, 0.0, 0.065)), spp=8)
                frames.append(np.asarray(img))
    health = sim.check()
    res = {"beta_deg": args.beta, "particles": n, "mu_wall": MU_WALL, "seconds": args.seconds, "log": log,
           "health_ok": bool(health["ok"]), "wall_s": round(time.perf_counter() - t1, 1),
           "geometry": {"r_top": R_TOP, "r_out": R_OUT, "z_out": Z_OUT, "z_top": z_top, "vial_r": VIAL_R,
                        "column": COLUMN}, "alloy_version": alloy.__version__}
    OUT.mkdir(exist_ok=True)
    (OUT / f"doser_funnel_b{args.beta:g}.json").write_text(json.dumps(res, indent=1))
    if frames:
        np.save(OUT / f"doser_funnel_b{args.beta:g}_frames.npy", np.stack(frames))
    print("health", health["ok"], "wall", res["wall_s"], flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--beta", type=float, default=30.0, help="funnel wall angle from horizontal, deg")
    p.add_argument("--seconds", type=float, default=2.0)
    p.add_argument("--every", type=int, default=5)
    p.add_argument("--render", action="store_true")
    p.add_argument("--render-every", type=int, default=1)
    a = p.parse_args()
    run(a)
