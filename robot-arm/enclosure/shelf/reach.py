"""Where the PiPER can comfortably pick from a shelf (#229): the reach band, the parked pose, J1's dead wedge.

    python reach.py           # reach-results.json, reach-map.npz

The arm is planar when J4 = 0 (the fingertip sits 1.4 mm off the plane), so a 1 degree grid over
J2 x J3, with J5 solved for each gripper pitch, covers every way of reaching a point in the arm's
plane. J1 then swings that plane around the base, and J6 only rolls the gripper.

"Comfortable" means every joint stays at least MARGIN from its URDF limit while the gripper can
come in at any pitch from 30 to 60 degrees below horizontal: a 45 degree approach, with 15 degrees
of slack either way. Heights are the fingertip's, measured from the plate the arm stands on.
"""

import json
import sys
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from piper_fk import Piper, fk_points  # noqa: E402

MARGIN = np.radians(15)
PITCHES = np.arange(-90, 31, 5)          # gripper pitch, degrees, 0 = horizontal, -90 = straight down
APPROACH = (-60, -30)                    # the 45 degree approach cone the shelf is sized for
R_BINS = np.arange(-0.70, 0.801, 0.01)   # signed radius in the arm's plane: + in front of J1, - behind
Z_BINS = np.arange(-0.10, 0.501, 0.01)


def plane_solutions(piper, step_deg=1.0):
    """Every (J2, J3) on the grid, with J1 = J4 = J6 = 0."""
    L = piper.limits
    d = np.radians(step_deg)
    j2 = np.arange(L["joint2"][0], L["joint2"][1] + 1e-9, d)
    j3 = np.arange(L["joint3"][0], L["joint3"][1] + 1e-9, d)
    g2, g3 = np.meshgrid(j2, j3, indexing="ij")
    Q = np.zeros((g2.size, 6))
    Q[:, 1], Q[:, 2] = g2.ravel(), g3.ravel()
    return Q


def pitch_map(piper, margin=MARGIN):
    """feasible[p, i, k]: pitch PITCHES[p] reaches cell (R_BINS[i], Z_BINS[k]) with every joint >= margin
    inside its limits."""
    L = piper.limits
    Q = plane_solutions(piper)
    o = fk_points(piper, Q)
    tool = o["tip"] - o["flange"]
    a0 = np.arctan2(tool[:, 2], tool[:, 0])          # pitch with J5 = 0; J5 adds to it with sign -1
    nr, nz = len(R_BINS) - 1, len(Z_BINS) - 1
    feas = np.zeros((len(PITCHES), nr, nz), bool)
    for p, deg in enumerate(PITCHES):
        for out in (np.radians(deg), np.pi - np.radians(deg)):      # pointing away from J1, in front or behind
            j5 = -np.angle(np.exp(1j * (out - a0)))
            Qs = Q[np.abs(j5) <= L["joint5"][1] - margin].copy()
            Qs[:, 4] = j5[np.abs(j5) <= L["joint5"][1] - margin]
            m = np.minimum.reduce([np.minimum(Qs[:, i] - L[f"joint{i + 1}"][0], L[f"joint{i + 1}"][1] - Qs[:, i])
                                   for i in (1, 2)])
            Qs = Qs[m >= margin]
            tip = fk_points(piper, Qs)["tip"]
            r, z = tip[:, 0], tip[:, 2]
            behind = out > np.pi / 2
            keep = (r < 0) if behind else (r > 0)
            i = np.digitize(r[keep], R_BINS) - 1
            k = np.digitize(z[keep], Z_BINS) - 1
            ok = (i >= 0) & (i < nr) & (k >= 0) & (k < nz)
            feas[p, i[ok], k[ok]] = True
    return feas


def comfortable(feas):
    """Cells where every pitch in the approach cone works."""
    sel = (PITCHES >= APPROACH[0]) & (PITCHES <= APPROACH[1])
    return feas[sel].all(axis=0)


def band(comf, z_lo, z_hi):
    """Radii (front side) that are comfortable at every fingertip height from z_lo to z_hi."""
    zc = (Z_BINS[:-1] + Z_BINS[1:]) / 2
    rc = (R_BINS[:-1] + R_BINS[1:]) / 2
    rows = comf[:, (zc >= z_lo - 0.005) & (zc <= z_hi + 0.005)].all(axis=1) & (rc > 0)
    rr = rc[rows]
    # the longest unbroken run
    if not len(rr):
        return None
    runs = np.split(rr, np.where(np.diff(rr) > 0.011)[0] + 1)
    best = max(runs, key=len)
    return float(best.min() - 0.005), float(best.max() + 0.005)


# Items are gripped low: fingertips from 10 mm above the shelf (a short item) to 60 mm (a tall one).
GRIP_ABOVE_SHELF = (0.010, 0.060)
SHELF_HEIGHTS = (0.050, 0.075, 0.100, 0.125, 0.150)


def rest_pose(piper):
    """How far the parked arm reaches behind J1, the radius it sweeps if J1 turns while parked,
    and the height of its underside back there. From the meshes, not the joint origins."""
    P = piper.fk(np.zeros(6))
    V = []
    for name, path in piper.meshes.items():
        scene = trimesh.load(path, force="scene")
        for node in scene.graph.nodes_geometry:
            Tn, g = scene.graph[node]
            m = scene.geometry[g]
            if len(m.faces) < 10:
                continue
            v = trimesh.transform_points(m.vertices, P[name] @ piper.visual_origin[name] @ Tn)
            V.append(v)
    V = np.vstack(V)
    arm = V[V[:, 2] > 0.06]                       # above the foot
    r = np.hypot(arm[:, 0], arm[:, 1])
    back = arm[arm[:, 0] < -0.15]
    return dict(
        elbow_joint_m=[round(float(v), 4) for v in P["link3"][:3, 3][[0, 2]]],
        behind_m=round(float(-arm[:, 0].min()), 4),
        swept_radius_m=round(float(r.max()), 4),
        underside_behind_m=round(float(back[:, 2].min()), 4),
        top_behind_m=round(float(back[:, 2].max()), 4),
    )


def main():
    piper = Piper()
    feas = pitch_map(piper)
    comf = comfortable(feas)
    j1 = np.degrees(piper.limits["joint1"][1])
    zc = (Z_BINS[:-1] + Z_BINS[1:]) / 2
    bands = {}
    for z in (0.0, 0.05, 0.10, 0.15, 0.20, 0.25):
        b = band(comf, z, z)
        bands[f"{z:.2f}"] = [round(v, 3) for v in b] if b else None
    shelf = {}
    for h in SHELF_HEIGHTS:
        b = band(comf, h + GRIP_ABOVE_SHELF[0], h + GRIP_ABOVE_SHELF[1])
        shelf[f"{h:.3f}"] = [round(v, 3) for v in b] if b else None
    rc = (R_BINS[:-1] + R_BINS[1:]) / 2
    behind = feas[:, rc < -0.05, :]
    behind_pitches = PITCHES[behind.any(axis=(1, 2))]
    res = dict(
        margin_deg=round(float(np.degrees(MARGIN)), 1),
        approach_pitch_deg=list(APPROACH),
        j1_limit_deg=round(float(j1), 1),
        j1_dead_wedge_deg=round(float(360 - 2 * j1), 1),
        j1_dead_wedge_with_margin_deg=round(float(360 - 2 * (j1 - np.degrees(MARGIN))), 1),
        behind_comfortable=bool(comf[rc < -0.05].any()),
        behind_pitches_deg=[int(behind_pitches.min()), int(behind_pitches.max())] if len(behind_pitches) else None,
        straight_down_max_tip_height_m=round(float(zc[feas[PITCHES == -90][0].any(axis=0)].max() + 0.005), 3)
        if feas[PITCHES == -90][0].any() else None,
        comfortable_band_by_tip_height_m=bands,
        grip_above_shelf_m=list(GRIP_ABOVE_SHELF),
        comfortable_band_by_shelf_height_m=shelf,
        rest_pose=rest_pose(piper),
    )
    (HERE / "reach-results.json").write_text(json.dumps(res, indent=1) + "\n")
    np.savez_compressed(HERE / "reach-map.npz", feas=feas, r_bins=R_BINS, z_bins=Z_BINS, pitches=PITCHES)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
