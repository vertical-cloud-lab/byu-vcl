"""Powder, dosed to the mark: a scoop tips powder into a vial on a load cell and stops at a target mass (Alloy, CPU).

Alloy's demo "Water, poured to the line" tilts a jug of water over a cup. This is the same with powder, closed loop.
A scoop (a kinematic open box, 30 mm inside) holds 13.7 g of powder and tips about its front lip over a 20 mL vial
(25 mm bore). A simulated load cell under the vial reads the powder that has landed in it, each control period
(10 ms). The controller:

1. tips the scoop at 60 deg/s to 95 deg, past where sand starts to run;
2. tips on at 8 deg/s while powder pours;
3. tips back at 120 deg/s as soon as the reading reaches the target minus an allowance for the powder that will
   still land: `--allow` g plus `--allow-rate` s times the flow over the last 0.1 s. Both are 0 by default, so the
   first runs show the overshoot to cover; a second pass uses the allowance fitted to the first (README);
4. then waits 1 s for the last of it to land, and reports the dose against the target.

The powder is Alloy's dry silica sand card on Newton's implicit MPM solver, the same stand-in as doser_funnel.py.
Alloy fills grains at 0.59 x 2,650 kg/m^3; at its 3 mm voxel (1.5 mm particles) one particle is 5.28 mg.

    python doser_pour.py --target 4 [--allow 0.43 --allow-rate 0.10] [--render]    # out/doser_pour_t4_*.json
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "out"
INNER, WALL = 0.030, 0.003                      # the scoop: 30 mm cube inside, 3 mm walls
HX, HZ = -0.020, 0.070                          # its floor's centre x, and the bottom of its floor
LIP_X, LIP_Z = HX + INNER / 2 + WALL, HZ + WALL + INNER    # the front lip, top outer edge: the pivot
POWDER = (0.028, 0.028, 0.012)                  # m: 9.4 cm^3 of powder in the scoop
VX, VR, VD, VWALL = LIP_X + 0.006, 0.0125, 0.050, 0.003     # the vial, 6 mm past the lip; eight wall slabs
RIM = VWALL + VD
FAST, SLOW, BACK = math.radians(60), math.radians(8), math.radians(-120)
TIP_TO, TIP_MAX = math.radians(95), math.radians(150)


def build():
    import alloy

    scene = alloy.Scene(dt=0.01)
    scene.add_ground()
    scene.add_open_box("scoop", inner=(INNER, INNER, INNER), wall=WALL, pos=(HX, 0, HZ), kinematic=True)
    scene.add_box("powder", size=POWDER, pos=(HX, 0, HZ + WALL + POWDER[2] / 2 + 0.0005), material="sand_silica_dry")
    scene.add_open_cylinder("vial", inner_radius=VR, depth=VD, wall=VWALL, pos=(VX, 0, 0), segments=8,
                            material="glass_soda_lime")
    return alloy, alloy.build(scene, device="cpu")


def run(args) -> None:
    alloy, sim = build()
    pts = sim.state(world=0)["powder.points"]
    n = len(pts)
    voxel = float(sim.built.report.decisions["powder"].numbers["voxel"])
    m_p = 0.59 * 2650.0 * (voxel / 2) ** 3 * 1000          # g per particle (Alloy's GRAIN_MPM fill)
    print(f"{n} particles, voxel {voxel * 1000:.1f} mm, {m_p * 1000:.2f} mg each, {n * m_p:.2f} g", flush=True)
    sim.settle(0.1)
    target, allow, allow_rate = args.target, args.allow, args.allow_rate
    theta, phase, t_stop, log, frames = 0.0, "tip", None, [], []
    t0 = time.perf_counter()
    omega = FAST
    sim.drive("scoop", angular_velocity=(0, omega, 0), pivot=(LIP_X, 0, LIP_Z))
    k = 0
    while True:
        p = sim.state(world=0)["powder.points"]
        r = np.hypot(p[:, 0] - VX, p[:, 1])
        in_vial = (r < VR) & (p[:, 2] < RIM) & (p[:, 2] > VWALL - 0.002)
        grams = float(in_vial.sum() * m_p)
        spilled = float(((p[:, 2] < 0.01) & ~in_vial).sum() * m_p)
        log.append({"t": round(k * 0.01, 2), "theta_deg": round(math.degrees(theta), 2), "phase": phase,
                    "grams": round(grams, 4), "spilled_g": round(spilled, 4)})
        if args.render and k % args.every == 0:
            img = sim.render(width=400, height=380, look_at=((0.055, -0.175, 0.125), (0.0, 0.0, 0.07)), spp=8)
            frames.append((np.asarray(img), dict(log[-1])))
        # the controller: one decision per control period, on the load cell's reading
        new = omega
        if phase == "tip" and theta >= TIP_TO:
            phase, new = "pour", SLOW
        rate = (grams - log[-11]["grams"]) / 0.1 if len(log) > 10 else 0.0       # g/s over the last 0.1 s
        if phase in ("tip", "pour") and grams >= target - (allow + allow_rate * max(rate, 0.0)):
            phase, new, t_stop = "back", BACK, k * 0.01
        if phase == "pour" and theta >= TIP_MAX:
            phase, new, t_stop = "back", BACK, k * 0.01       # empty, or stuck: give up
        if phase == "back" and theta + BACK * 0.01 <= 0:
            phase, new = "settle", 0.0
            sim.stop_drives()
        if phase == "settle" and k * 0.01 - t_stop > args.settle + abs(TIP_MAX / BACK):
            break
        if phase == "settle" and all(e["phase"] == "settle" for e in log[-int(args.settle * 100):]) and \
                len(log) > args.settle * 100:
            break
        if new != omega and phase != "settle":
            sim.drive("scoop", angular_velocity=(0, new, 0), pivot=(LIP_X, 0, LIP_Z))
        omega = new if phase != "settle" else 0.0
        sim.step(1)
        theta = max(0.0, theta + omega * 0.01) if phase != "settle" else 0.0
        k += 1
        if k % 25 == 0:
            print(json.dumps(log[-1]), round(time.perf_counter() - t0, 1), flush=True)
        if k > 1000:
            break
    final = log[-1]["grams"]
    res = {"target_g": target, "allow_g": allow, "allow_rate_s": allow_rate, "final_g": final, "error_g": round(final - target, 4),
           "stop_reading_g": next((e["grams"] for e in log if e["phase"] == "back"), None), "t_stop": t_stop,
           "particles": n, "gram_per_particle": m_p, "powder_g": n * m_p, "health_ok": bool(sim.check()["ok"]),
           "wall_s": round(time.perf_counter() - t0, 1), "alloy_version": alloy.__version__, "log": log}
    OUT.mkdir(exist_ok=True)
    stem = f"doser_pour_t{target:g}_a{allow:g}" + (f"_r{allow_rate:g}" if allow_rate else "")
    (OUT / f"{stem}.json").write_text(json.dumps(res, indent=1))
    if frames:
        np.save(OUT / f"{stem}_frames.npy", np.stack([f for f, _ in frames]))
        (OUT / f"{stem}_frames.json").write_text(json.dumps([m for _, m in frames]))
    print(f"target {target} g, allowance {allow} g: stopped at reading {res['stop_reading_g']} g, landed {final:.3f} g "
          f"({final - target:+.3f} g), health {res['health_ok']}, wall {res['wall_s']} s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=float, default=4.0, help="g")
    ap.add_argument("--allow", type=float, default=0.0, help="g allowed for powder that lands after the stop")
    ap.add_argument("--allow-rate", type=float, default=0.0, help="s: plus this many seconds of the current flow")
    ap.add_argument("--settle", type=float, default=1.0, help="s to wait after the scoop is back")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--every", type=int, default=5)
    run(ap.parse_args())
