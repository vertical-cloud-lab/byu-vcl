"""Numbers behind the #266 review: the mock-up against the real deck, payload and grip, reach, tolerance.

    python analysis.py          # prints a summary and writes results.json
"""

import json

import numpy as np
from scipy.optimize import least_squares

import geometry as G
from piper_fk import Piper, _axis_angle_batch

PLA = 1.24e-3        # g/mm^3
G0 = 9.81


# ------------------------------------------------------------------ 1. the mock-up against the real CubXL+
def measure_parts():
    parts = G.mockup_parts()
    deck, holder, key, vial = parts["deck"], parts["holder"], parts["key"], parts["vial"]
    out = {"mockup_deck": G.slot_grid(deck), "real_deck": G.slot_grid(G.panda_deck())}
    out["mockup_deck"]["top_above_table_mm"] = round(float(deck.bounds[1][2] - deck.bounds[0][2]), 1)
    out["mockup_deck"]["solid_mass_g"] = round(float(deck.volume * PLA))

    # Holder: pocket fingers, seat, key sockets
    r_min = []
    for z in (18.5, 25.0, 30.0, 34.5):
        v = holder.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1]).vertices[:, :2]
        d = np.linalg.norm(v - [0, 0], axis=1)
        r_min.append((z, round(float(d[d < 20].min()), 2)))
    out["holder"] = dict(extents_mm=np.round(holder.extents, 1).tolist(), pockets=9, pitch_mm=G.VIAL_PITCH_MM,
                         seat_mm=18.0, finger_top_mm=35.0, finger_inner_radius_mm=r_min,
                         key_spacing_mm=225.0, solid_mass_g=round(float(holder.volume * PLA)))
    # Body radius of the dummy vial and the cap step
    zs = np.arange(0.5, vial.extents[2], 0.5)
    rad = [np.sqrt(sum(p.area for p in vial.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
                       .to_2D()[0].polygons_full) / np.pi) for z in zs]
    step = float(zs[np.argmax(np.diff(rad)) + 1])
    out["vial"] = dict(height_mm=round(float(vial.extents[2]), 1), body_d_mm=round(2 * rad[0], 1),
                       cap_d_mm=round(2 * rad[-1], 1), cap_starts_mm=step,
                       solid_mass_g=round(float(vial.volume * PLA), 1))
    interference = out["vial"]["body_d_mm"] / 2 - r_min[-1][1]
    out["holder"]["fit_at_top_mm"] = round(-interference, 2)   # negative = interference on radius
    out["key"] = dict(extents_mm=np.round(key.extents, 1).tolist(),
                      slot_clearance_mockup_mm=round(out["mockup_deck"]["slot_mm"][1] - key.extents[0], 2),
                      slot_clearance_real_mm=round(out["real_deck"]["slot_mm"][0] - key.extents[0], 2),
                      engagement_mm=10.0, chamfer_mm=0.0)
    return out


# ------------------------------------------------------------------ 2. what the gantry can reach
def tool_windows():
    out = {}
    for axis in "xy":
        lo, hi = G.tool_window(axis)
        out[axis] = dict(common_window_mm=[round(lo, 1), round(hi, 1)], span_mm=round(hi - lo, 1),
                         vials_at_33mm=G.vials_that_fit(axis))
    return out


# ------------------------------------------------------------------ 3. payload and grip
def payload():
    glass, cap, water = 20.0, 6.0, 20.0             # g; weigh yours (20 mL VOA vial, PANDA magnetic cap)
    vial_full = glass + cap + water
    holder_printed, holder_solid = 75.0, 202.0      # g; default 15 % infill vs 100 %
    fingers = 40.0
    full9 = [holder_printed + 9 * vial_full + fingers, holder_solid + 9 * vial_full + fingers]
    full8 = [holder_printed + 8 * vial_full + fingers + 15, holder_solid + 8 * vial_full + fingers + 15]
    grip = 40.0                                       # N, PiPER gripper rated (50 N max)
    mu = {"bare PLA/aluminium on glass": 0.25, "silicone pad on glass": 0.7}
    slip = {k: round(2 * m * grip, 1) for k, m in mu.items()}
    # Worst static tilt on a centre-gripped 8 + 1 carrier: four full vials on one side only
    side = np.array([-1, -2, -3, -4]) * G.VIAL_PITCH_MM / 1000
    m_holder = holder_printed / 1000
    m_v = vial_full / 1000
    cog = m_v * side.sum() / (m_holder + 4 * m_v)
    torque_partial = (m_holder + 4 * m_v) * G0 * abs(cog)
    # Friction torque two flat 20 x 20 mm pads can resist about the closing axis (mean radius 0.383 a)
    t_pad = {k: round(2 * m * grip * 0.383 * 0.020, 3) for k, m in mu.items()}
    # Cantilever if the carrier were held by one end instead
    torque_end = (holder_printed + 9 * vial_full) / 1000 * G0 * 0.155
    return dict(vial_full_g=vial_full, vial_dummy_solid_g=46.8,
                carrier_9_full_g=full9, carrier_8_plus_post_full_g=full8,
                payload_rating_kg=1.5, gripper_mass_kg=0.5,
                fraction_of_rating=[round(f / 1500, 2) for f in full9],
                fraction_if_gripper_counts=[round(f / 1000, 2) for f in full9],
                grip_force_N=grip, vertical_slip_force_N=slip,
                partial_load_cog_offset_mm=round(cog * 1000, 1),
                partial_load_torque_Nm=round(torque_partial, 3), pad_friction_torque_Nm=t_pad,
                end_grip_cantilever_torque_Nm=round(torque_end, 2))


# ------------------------------------------------------------------ 4. reach
TCP = 0.120  # pad centre, 120 mm past the flange (finger mesh ends at 140 mm)


def _pose(piper, q):
    T = piper.fk(q)["link6"]
    return T[:3, 3] + T[:3, 2] * TCP, T[:3, :3]


def ik(piper, target, approach, close, seeds=40, seed=0):
    """Full 6-DOF IK: pad centre on target, tool z along approach, fingers closing along close.
    Returns (q, smallest joint margin in degrees) for the most central solution, or None."""
    lims = np.array([piper.limits[f"joint{i}"] for i in range(1, 7)])
    a = np.asarray(approach, float) / np.linalg.norm(approach)
    c = np.asarray(close, float) / np.linalg.norm(close)
    rng = np.random.default_rng(seed)

    def res(q):
        t, R = _pose(piper, q)
        return np.r_[(t - target) * 10, R[:, 2] - a, 0.5 * (1 - abs(R[:, 1] @ c))]

    best = None
    for _ in range(seeds):
        s = least_squares(res, rng.uniform(lims[:, 0] * 0.9, lims[:, 1] * 0.9), bounds=(lims[:, 0], lims[:, 1]))
        if s.cost < 1e-8:
            m = float(np.degrees(np.min(np.minimum(s.x - lims[:, 0], lims[:, 1] - s.x))))
            if best is None or m > best[1]:
                best = (s.x, m)
    return best


def reach_bands(n=1_200_000):
    """Radius band where the pad centre can sit at each height for a given pitch below horizontal."""
    piper = Piper()
    lims = np.array([piper.limits[f"joint{i}"] for i in range(1, 7)])
    rng = np.random.default_rng(1)
    Q = np.column_stack([rng.uniform(lo, hi, n) for lo, hi in lims])
    Q[:, 0] = 0.0
    poses = {piper.joints[0]["parent"]: np.broadcast_to(np.eye(4), (n, 4, 4)).copy()}
    for j in piper.joints:
        T = poses[j["parent"]] @ j["T"]
        if j["type"] == "revolute" and j["name"] in {f"joint{i}" for i in range(1, 7)}:
            R = np.broadcast_to(np.eye(4), (n, 4, 4)).copy()
            R[:, :3, :3] = _axis_angle_batch(j["axis"], Q[:, int(j["name"][-1]) - 1])
            T = T @ R
        poses[j["child"]] = T
    F = poses["link6"]
    z = F[:, :3, 2]
    tip = F[:, :3, 3] + z * TCP
    pitch = np.degrees(np.arcsin(np.clip(-z[:, 2], -1, 1)))
    out = {}
    for margin in (0, 15):
        ok = np.all((Q[:, 1:] > lims[1:, 0] + np.radians(margin)) & (Q[:, 1:] < lims[1:, 1] - np.radians(margin)),
                    axis=1) & (np.abs(z[:, 1]) < 0.05)
        for want in (90, 60, 45):
            row = {}
            for h in (0.0, 0.05, 0.10, 0.15, 0.20, 0.25):
                s = ok & (np.abs(pitch - want) < 3) & (np.abs(tip[:, 2] - h) < 0.01) & (tip[:, 0] > 0.05)
                row[f"{h:.2f}"] = None if s.sum() < 5 else [round(float(tip[s, 0].min()), 2),
                                                            round(float(tip[s, 0].max()), 2)]
            out[f"pitch{want}_margin{margin}"] = row
    return out


def handoff_ik():
    piper = Piper()
    h = G.grasp_point()[2]
    cases = {
        "carrier radial, 45 deg along it (post)": (G.grasp_point(), [0, 1, -1], [1, 0, 0]),
        "carrier radial, 60 deg along it (post)": (G.grasp_point(), [0, 1, -np.sqrt(3)], [1, 0, 0]),
        "carrier tangential, 45 deg along it": (G.grasp_point(), [1, 0, -1], [0, 1, 0]),
        "top-down on the post": (G.grasp_point(), [0, 0, -1], [1, 0, 0]),
        "nearest vial (slot 1), 45 deg": (np.array([0, G.slot_y(1), h]), [0, 1, -1], [1, 0, 0]),
        "farthest vial (slot 9), 45 deg": (np.array([0, G.slot_y(9), h]), [0, 1, -1], [1, 0, 0]),
        "single-vial pocket, 45 deg": (np.array([*G.SINGLE_POCKETS[0], h]), [*G.SINGLE_POCKETS[0], -0.43], [1, 0, 0]),
        "far deck corner (direct reach-in), 45 deg": (np.array([0.40, 0.72, h]), [0.40, 0.72, -0.82], [0, 0, 1]),
    }
    out = {}
    for name, (tgt, appr, close) in cases.items():
        if name.startswith("single"):
            close = np.cross(appr, [0, 0, 1])
        if name.startswith("far deck"):
            close = np.cross(appr, [0, 0, 1])
        b = ik(piper, np.asarray(tgt, float), appr, close)
        out[name] = dict(radius_m=round(float(np.hypot(tgt[0], tgt[1])), 3), height_m=round(float(tgt[2]), 3),
                         reachable=b is not None,
                         min_margin_deg=None if b is None else round(b[1], 1),
                         q_deg=None if b is None else np.round(np.degrees(b[0]), 1).tolist())
    return out


# ------------------------------------------------------------------ 5. placement tolerance
def tolerance():
    arm = dict(repeatability=0.10, gripper=0.50, teach_and_registration=0.30, structure_and_humidity=0.25)
    rss = float(np.sqrt(sum(v ** 2 for v in arm.values())))
    worst = float(sum(arm.values()))
    capture = {"pill key into deck slot (no chamfer)": 0.2,
               "vial into tight-fit pocket (finger top)": 0.6,
               "carrier onto dock (3 mm lead-in + cone pins)": 3.0,
               "vial into loose chamfered single pocket": 2.5,
               "magnet onto cap (lateral)": 2.0}
    return dict(arm_error_mm=arm, rss_mm=round(rss, 2), worst_case_mm=round(worst, 2),
                capture_mm=capture, margin_vs_worst=
                {k: round(v / worst, 1) for k, v in capture.items()})


def main():
    res = dict(parts=measure_parts(), tool_windows=tool_windows(), payload=payload(),
               reach_bands=reach_bands(), handoff_ik=handoff_ik(), tolerance=tolerance(),
               grasp_point_m=np.round(G.grasp_point(), 4).tolist(),
               vial_grasp_band=dict(zip(("centre_m", "height_m"), np.round(G.vial_grasp_height(), 4).tolist())))
    (G.HERE / "results.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
