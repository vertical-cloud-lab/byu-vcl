"""VLM tray: how hard can a tray accelerate before loose labware slides or tips over? (Alloy engine, CPU)

Every world carries two kinematic trays moving side by side: one bare galvanised steel (a Kardex tray's sheet) and
one covered by a nitrile mat. Each tray carries the same five loose items, standing free with no rack. Every world
gets its own acceleration a: the trays speed up at +a for T seconds, slow down at -a for T seconds, then stop. That
is one extraction or one MiR move, and both its start and its stop push on the load.

What it reports, per item, tray surface and acceleration: did the item stay put, slide on the tray, rock and settle
back, or fall over. Then it compares the onsets with the two textbook thresholds for a rigid block: it slides when
a > mu g, and it tips when a > g (D / H) (D its footprint along the motion, H its height, centre of mass at H / 2).
mu for each pair is the one Alloy uses: a pair card's mu_dynamic, else the harmonic mean of the two materials'
mu_dynamic (AGENTS.md, section 4), read from the cards that ship with Alloy.

    python vlm_tray.py sweep  [--worlds 24]        # every acceleration, no images: out/vlm_tray_sweep.json
    python vlm_tray.py render [--accels 0.3,2,5,9]  # a few worlds, rendered by Alloy's camera: out/vlm_tray_*.gif
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import yaml

import alloy

G = 9.81
OUT = Path(__file__).resolve().parent / "out"
LIB = Path(alloy.__file__).resolve().parent / "_data" / "library"

# Loose labware. Sizes: common catalogue dimensions (cap on). Masses are estimates; they do not enter either threshold.
ITEMS = [  # name, label, shape, size (m), material, mass (kg)
    ("vial_4ml", "4 mL vial", "cyl", (0.0147, 0.045), "glass_soda_lime", 0.006),
    ("vial_20ml", "20 mL scintillation vial", "cyl", (0.028, 0.061), "glass_soda_lime", 0.022),
    ("tube_50ml", "50 mL self-standing tube", "cyl", (0.029, 0.115), "pp_homopolymer", 0.013),
    ("bottle_250ml", "250 mL media bottle", "cyl", (0.070, 0.143), "glass_soda_lime", 0.45),
    ("plate_96", "96-well plate", "box", (0.1278, 0.0855, 0.0144), "polystyrene", 0.06),
]
SURFACES = [("steel", "bare galvanised steel", "steel_zinc_plated"), ("mat", "nitrile mat", "nitrile_70a")]
TRAY = (0.864, 0.80, 0.01)         # x (motion: the 864 mm tray depth) by y by thickness, m; no rim (README)
TRAY_TOP = 0.10                    # m above the ground
TRAY_Y = {"steel": -0.45, "mat": 0.45}
ITEM_Y = np.linspace(-0.30, 0.30, len(ITEMS))     # items in a row across the motion, so a falling one hits nothing
T_RAMP = 0.40                      # s at +a, then s at -a
T_HOLD = 0.60                      # s at rest after the stop
DT = 0.0025                        # control period: the drive's speed is a staircase of a * DT steps (see README)


def mu_dynamic(material: str) -> float:
    card = yaml.safe_load((LIB / "materials" / f"{material}.yaml").read_text())
    return float(card["surface"]["mu_dynamic"]["value"])


def pair_mu(a: str, b: str) -> tuple[float, str]:
    """Alloy's contact friction for two materials: a pair card if one ships, else the harmonic mean of mu_dynamic."""
    for x, y in ((a, b), (b, a)):
        p = LIB / "pairs" / f"{x}__{y}.yaml"
        if p.exists():
            card = yaml.safe_load(p.read_text())
            key = "mu_static" if card.get("single_mu") == "static" else "mu_dynamic"
            return float(card[key]["value"] if isinstance(card[key], dict) else card[key]), f"pair card {p.name}"
    ma, mb = mu_dynamic(a), mu_dynamic(b)
    return 2 * ma * mb / (ma + mb), f"harmonic mean of {a} {ma} and {b} {mb}"


def thresholds() -> dict:
    rows = {}
    for surf, _, smat in SURFACES:
        for name, label, shape, size, mat, _ in ITEMS:
            mu, why = pair_mu(mat, smat)
            d_over_h = size[0] / size[1] if shape == "cyl" else size[0] / size[2]
            rows[f"{surf}/{name}"] = {"mu": mu, "mu_source": why, "a_slide": mu * G, "a_tip": G * d_over_h,
                                      "first": "slide" if mu < d_over_h else "tip"}
    return rows


def build(accels: np.ndarray):
    W = len(accels)
    scene = alloy.Scene(worlds=W, dt=DT)
    scene.add_ground()
    for surf, _, smat in SURFACES:
        scene.add_box(f"tray_{surf}", size=TRAY, pos=(0.0, TRAY_Y[surf], TRAY_TOP - TRAY[2] / 2), material=smat,
                      kinematic=True, rigid=True)
        for (name, _, shape, size, mat, mass), y in zip(ITEMS, ITEM_Y):
            n = f"{surf}_{name}"
            if shape == "cyl":
                scene.add_cylinder(n, size[0] / 2, size[1], pos=(0.0, TRAY_Y[surf] + y, TRAY_TOP + size[1] / 2),
                                   material=mat, mass=mass, rigid=True)
            else:
                scene.add_box(n, size=size, pos=(0.0, TRAY_Y[surf] + y, TRAY_TOP + size[2] / 2), material=mat,
                              mass=mass, rigid=True)
    return alloy.build(scene, device="cpu", seed=0)


def tray_speed(a: np.ndarray, t: float) -> np.ndarray:
    """Speed at the middle of the control period starting at t: up at +a for T_RAMP, down at -a for T_RAMP, then 0."""
    tm = t + DT / 2
    if tm < T_RAMP:
        return a * tm
    if tm < 2 * T_RAMP:
        return a * (2 * T_RAMP - tm)
    return np.zeros_like(a)


def drive(sim, a: np.ndarray, t: float) -> None:
    v = np.zeros((len(a), 3))
    v[:, 0] = tray_speed(a, t)
    for surf, _, _ in SURFACES:
        sim.drive(f"tray_{surf}", velocity=v)


def tilt_deg(q_wxyz: np.ndarray) -> np.ndarray:
    x, y = q_wxyz[..., 1], q_wxyz[..., 2]
    return np.degrees(np.arccos(np.clip(1 - 2 * (x * x + y * y), -1, 1)))


def names() -> list[str]:
    return [f"{s}_{n}" for s, _, _ in SURFACES for n, *_ in ITEMS]


def sweep(args) -> None:
    accels = np.geomspace(args.amin, args.amax, args.worlds)
    t0 = time.perf_counter()
    sim = build(accels)
    t_build = time.perf_counter() - t0
    print({k: v["route"] for k, v in sim.routes().items()})
    sim.settle(0.2)
    keys = names()
    s0 = sim.state()
    start = {k: s0[f"{k}.pos"].copy() for k in keys}
    tray0 = {s: s0[f"tray_{s}.pos"].copy() for s, _, _ in SURFACES}
    n = round((2 * T_RAMP + T_HOLD) / DT)
    max_tilt = {k: np.zeros(len(accels)) for k in keys}
    max_slip = {k: np.zeros(len(accels)) for k in keys}
    t1 = time.perf_counter()
    for i in range(n):
        drive(sim, accels, i * DT)
        sim.step(1)
        if i % 4 == 3 or i == n - 1:
            s = sim.state()
            for k in keys:
                surf = k.split("_", 1)[0]
                rel = (s[f"{k}.pos"][:, 0] - s[f"tray_{surf}.pos"][:, 0]) - (start[k][:, 0] - tray0[surf][:, 0])
                max_tilt[k] = np.maximum(max_tilt[k], tilt_deg(s[f"{k}.quat_wxyz"]))
                max_slip[k] = np.maximum(max_slip[k], np.abs(rel))
    t_run = time.perf_counter() - t1
    s = sim.state()
    health = sim.check()
    th = thresholds()
    # Alloy's contacts are soft: an item that holds still lags the tray by about tau x its speed while the tray speeds
    # up, the same for every item, mass and material, and catches up as it slows down. Fit tau in the slowest world
    # (under every threshold) and count only the slip beyond it.
    v_max = accels * T_RAMP
    tau = float(np.median([max_slip[k][0] / v_max[0] for k in keys]))
    rows = []
    for k in keys:
        surf, item = k.split("_", 1)
        final_tilt = tilt_deg(s[f"{k}.quat_wxyz"])
        final_rel = np.abs((s[f"{k}.pos"][:, 0] - s[f"tray_{surf}.pos"][:, 0]) - (start[k][:, 0] - tray0[surf][:, 0]))
        size = dict((n, sz) for n, _, _, sz, _, _ in ITEMS)[item]
        on_tray = TRAY[0] / 2 - size[0] / 2
        for w, a in enumerate(accels):
            slip = max_slip[k][w] - tau * v_max[w]
            if max_slip[k][w] > on_tray:
                outcome = "off"
            elif final_tilt[w] > 45:
                outcome = "fell"
            elif max_tilt[k][w] > 5:
                outcome = "rocked"
            elif slip > 0.002:
                outcome = "slid"
            else:
                outcome = "held"
            rows.append({"surface": surf, "item": item, "accel": float(a), "outcome": outcome,
                         "max_tilt_deg": float(max_tilt[k][w]), "final_tilt_deg": float(final_tilt[w]),
                         "max_slip_mm": float(1000 * max_slip[k][w]), "slip_beyond_lag_mm": float(1000 * slip),
                         "final_offset_mm": float(1000 * final_rel[w])})
    out = {"alloy_version": alloy.__version__, "worlds": len(accels), "accels": accels.tolist(), "dt": DT,
           "t_ramp": T_RAMP, "t_hold": T_HOLD, "build_s": round(t_build, 1), "run_s": round(t_run, 1),
           "health_ok": bool(health["ok"]), "contact_lag_tau_s": tau, "items": [dict(zip(("name", "label", "shape", "size_m", "material",
                                                                  "mass_kg"), it)) for it in ITEMS],
           "surfaces": [dict(zip(("name", "label", "material"), s_)) for s_ in SURFACES], "thresholds": th,
           "rows": rows}
    OUT.mkdir(exist_ok=True)
    (OUT / "vlm_tray_sweep.json").write_text(json.dumps(out, indent=1))
    print(f"build {t_build:.1f} s, run {t_run:.1f} s, health ok {health['ok']}, contact lag tau {1000 * tau:.1f} ms")
    for k in keys:
        surf, item = k.split("_", 1)
        seq = "".join({"held": ".", "slid": "s", "rocked": "r", "fell": "X", "off": "o"}[r["outcome"]]
                      for r in rows if r["surface"] == surf and r["item"] == item)
        t = th[f"{surf}/{item}"]
        print(f"{surf:5s} {item:13s} {seq}  mu={t['mu']:.2f} slide>{t['a_slide']:.1f} tip>{t['a_tip']:.1f}")


def render(args) -> None:
    from PIL import Image, ImageDraw, ImageFont

    from alloy.camera.pose import look_at

    accels = np.array([float(x) for x in args.accels.split(",")])
    W = len(accels)
    sim = build(accels)
    sim.settle(0.2)
    cams = None
    n = round((2 * T_RAMP + T_HOLD) / DT)
    every = max(1, round(1 / (args.fps * DT)))
    frames = []
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 15)
        small = ImageFont.truetype("DejaVuSans.ttf", 12)
    except OSError:
        font = small = ImageFont.load_default()
    for i in range(n + 1):
        if i % every == 0:
            x = sim.state()["tray_steel.pos"][:, 0]
            poses = np.stack([look_at((xi + 1.25, -1.55, 0.95), (xi, 0.05, 0.10)) for xi in x])
            if cams is None:
                cams = alloy.Camera("follow", pose=poses, width=args.width, height=args.height, fov=50, spp=args.spp,
                                    denoise=args.denoise)
            else:
                cams.set_pose(pose=poses)
            imgs = np.asarray(sim.render(cams))
            tiles = []
            for w in range(W):
                im = Image.fromarray(imgs[w])
                d = ImageDraw.Draw(im)
                v = float(tray_speed(accels[w:w + 1], i * DT - DT / 2)[0]) if i else 0.0
                d.text((8, 6), f"a = {accels[w]:.1f} m/s²", fill=(20, 20, 20), font=font)
                d.text((8, 26), f"t = {i * DT:.2f} s   v = {v:.2f} m/s", fill=(60, 60, 60), font=small)
                d.text((8, args.height - 34), "front: bare steel tray", fill=(60, 60, 60), font=small)
                d.text((8, args.height - 18), "back: nitrile mat", fill=(60, 60, 60), font=small)
                tiles.append(im)
            cols = min(W, args.cols)
            rows_ = math.ceil(W / cols)
            sheet = Image.new("RGB", (cols * args.width, rows_ * args.height), "white")
            for w, im in enumerate(tiles):
                sheet.paste(im, ((w % cols) * args.width, (w // cols) * args.height))
            frames.append(sheet)
            print(f"frame {len(frames)} t={i * DT:.2f}", flush=True)
        if i < n:
            drive(sim, accels, i * DT)
            sim.step(1)
    OUT.mkdir(exist_ok=True)
    stem = OUT / "vlm_tray"
    frames[0].save(f"{stem}.gif", save_all=True, append_images=frames[1:] + [frames[-1]] * 8,
                   duration=int(1000 / args.fps * args.slow), loop=0)
    frames[len(frames) // 3].save(f"{stem}_frame.png")
    frames[-1].save(f"{stem}_final.png")
    print("health ok", sim.check()["ok"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sweep")
    s.add_argument("--worlds", type=int, default=24)
    s.add_argument("--amin", type=float, default=0.3)
    s.add_argument("--amax", type=float, default=10.0)
    r = sub.add_parser("render")
    r.add_argument("--accels", default="0.3,2,4,8")
    r.add_argument("--width", type=int, default=400)
    r.add_argument("--height", type=int, default=300)
    r.add_argument("--cols", type=int, default=2)
    r.add_argument("--spp", type=int, default=8)
    r.add_argument("--denoise", default=None)
    r.add_argument("--fps", type=float, default=25)
    r.add_argument("--slow", type=float, default=2.0, help="playback slow-down factor")
    a = p.parse_args()
    {"sweep": sweep, "render": render}[a.cmd](a)
