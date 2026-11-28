"""Round 14, the doser: a shorter fall into the vessel, our draft shield round it, a nest that holds it. Measured on v5's
own geometry, with our parts from ``carousel.py`` (STATION "r14").

Sterling on PR #318 (2026-11-20): "The dose is still going from way too high up. We probably need more of a custom
breeze break that extends higher up. Either way, that's way too long of a fall distance before it lands in the cup ...
Also seems like maybe you could reverse the orientation of the balance to free up space (again, with a custom breeze
break)"; and at 9:54: "when it's actually on the pedestal, it still looks relatively unsecure".

    python3 doser_shield.py            # measurements and FCL checks -> out/doser_shield.json
    python3 doser_shield.py figure     # the section, before and after -> out/doser_shield_section.png

Rig frame (v5's own): x along the augers (the outlet end and the balance's display at -x), y along the loop, z up from
the bench, mm. What is checked (python-fcl, mesh to mesh, on the meshes the animation draws):

* the room over the pan in every state of v5's electronics carriage (EC): parked, each 7 mm of its 28 mm rise, each
  10° of its tilt to 30°, and the chain shifting with the EC parked;
* our fixed parts (the roof plate, the dose post and its nest, the draft shield) against every v5 part in every one
  of those states;
* the vessel (the vial; a charge cup) and the fork, carried along the shuttle's whole travel and set on the nest, with
  the EC docked and tilted to 30° (the only state in which a vessel is on the post);
* the HR-202i turned round (180° about the pan's axis), against v5 parked and at the dose.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel as C        # noqa: E402

CL, CP = C.CL, C.CP
OUT = HERE / "out"
EXIT = np.asarray(CL.exit_point(C.TILT), float)
EXIT_Z = float(EXIT[2])
PX, PY = (float(v) for v in C.PAN_XY)
STREAM_D = 8.0                                  # v5's check_stream column
MOUTH = {"vial": 2 * (14.0 - 1.2), "cup": 12.7}  # the vial's mouth (props), the cup's bore (charge.CUP_BORE_D)
H = {"vial": C.VIAL_H, "cup": C.CUP_L}
REGION = (-120.0, 220.0, -480.0, 160.0, 240.0, 470.0)   # parts outside this box can't come near the dose zone


def states() -> dict:
    st = {"parked": CL.State(ext=0.0, beaker=False)}
    for e in (7.0, 14.0, 21.0):
        st[f"rising {e:.0f} mm"] = CL.State(ext=e, magnet_on=True, beaker=False)
    for t in (0.0, 10.0, 20.0, 30.0):
        st[f"docked, tilt {t:.0f}°"] = CL.State(ext=C.DOCK_EXT, tilt=t, magnet_on=True, beaker=False)
    for s in (2.0, 4.0, 6.0):
        st[f"chain shift {s:.0f} links"] = CL.State(shift=s, ext=0.0, beaker=False)
    return st


def _fcl_model(mesh):
    import fcl
    m = mesh.triangulate()
    f = m.faces.reshape(-1, 4)[:, 1:]
    bvh = fcl.BVHModel()
    bvh.beginModel(len(m.points), len(f))
    bvh.addSubModel(np.asarray(m.points, float), np.asarray(f, np.int64))
    bvh.endModel()
    return fcl.CollisionObject(bvh, fcl.Transform())


def v5_objects(st, parts, skip=("hr202i",)):
    """[(key, fcl object, bounds)] of v5's part instances near the dose zone in state `st` (world = rig frame)."""
    import pyvista as pv
    x0, x1, y0, y1, z0, z1 = REGION
    out = []
    for p in C.lowered(CL.placements(st)):
        if p.key in C.SKIP or p.key.startswith(skip) or p.key == "hr202i_top_door":
            continue
        m = parts[p.key]
        if not m.n_points:
            continue
        pts = m.points @ p.M[:3, :3].T + p.M[:3, 3]
        lo, hi = pts.min(0), pts.max(0)
        if hi[0] < x0 or lo[0] > x1 or hi[1] < y0 or lo[1] > y1 or hi[2] < z0 or lo[2] > z1:
            continue
        w = pv.PolyData(pts, m.faces)
        out.append((p.key, _fcl_model(w), (lo, hi)))
    return out


def min_dist(obj, objs, lo=None, hi=None, margin=60.0):
    """(distance, key) from fcl object `obj` to the nearest of `objs` (negative: they overlap)."""
    import fcl
    best = (1e9, "")
    for key, o, (a, b) in objs:
        if lo is not None and (np.any(a > hi + margin) or np.any(b < lo - margin)):
            continue
        req, res = fcl.DistanceRequest(enable_signed_distance=True), fcl.DistanceResult()
        d = fcl.distance(obj, o, req, res)
        if d <= 0:
            creq, cres = fcl.CollisionRequest(enable_contact=True, num_max_contacts=50), fcl.CollisionResult()
            fcl.collide(obj, o, creq, cres)
            d = -max([c.penetration_depth for c in cres.contacts], default=0.0) if cres.is_collision else d
        if d < best[0]:
            best = (float(d), key)
    return best


def vessel_mesh(kind):
    import charge
    import props
    return props.vial_glass() if kind == "vial" else charge.cup()


def measure() -> dict:
    import pyvista as pv
    C.STATION = "r14"
    parts = C.part_meshes(C.PORT_R14)
    sts = states()
    objs = {k: v5_objects(st, parts) for k, st in sts.items()}
    out = dict(source="powder-doser chain-carousel-v5 at 353dae7 (copied in multidoser/); our r14 parts in carousel.py",
               exit=[round(float(v), 2) for v in EXIT], pan_xy=[round(PX, 2), round(PY, 2)])
    # ---- the room over the pan: the lowest v5 part within r of the axis, per state (sampled surfaces, 1.5 mm)
    room = {}
    for k, st in sts.items():
        pts = _surface_points(st, parts, PX, PY, 45.0)
        rr = np.hypot(pts[:, 0] - PX, pts[:, 1] - PY)
        room[k] = {f"r{r}": round(float(pts[rr <= r, 2].min()), 1) if (rr <= r).any() else None
                   for r in (10, 14, 20, 25, 30, 40)}
    out["room_over_pan"] = room
    # ---- our fixed parts against every v5 part in every state
    fixed = {"roof plate": C.roof_mesh()}
    for kind in ("vial", "cup"):
        pm = C.post_meshes(kind)
        fixed[f"post with the {kind} nest"] = pm["nest"].merge(pm["tube"])
    sh = C.shield_meshes()
    fixed["draft shield"] = sh["panels"].merge(sh["frame"])
    fixed["draft shield door, shut"] = sh["door"]
    door_open = sh["door"].translate((-C.SHIELD_DOOR["slide"], 0, 0), inplace=False)
    fixed["draft shield door, open"] = door_open
    fx = {}
    for name, mesh in fixed.items():
        o = _fcl_model(mesh)
        lo, hi = np.asarray(mesh.bounds[::2]), np.asarray(mesh.bounds[1::2])
        worst = (1e9, "", "")
        for k, ob in objs.items():
            d, key = min_dist(o, ob, lo, hi)
            if d < worst[0]:
                worst = (d, key, k)
        fx[name] = dict(min_mm=round(worst[0], 1), part=worst[1], state=worst[2])
    out["fixed_parts_vs_v5"] = fx
    # the post against the roof plate's hole and the shield
    roof_o = _fcl_model(C.roof_mesh())
    for kind in ("vial", "cup"):
        pm = C.post_meshes(kind)
        d, _ = min_dist(_fcl_model(pm["tube"].merge(pm["nest"])), [("roof", roof_o, (np.full(3, -1e9), np.full(3, 1e9)))])
        out.setdefault("post_to_roof_plate_mm", {})[kind] = round(d, 2)
    # ---- the vessel and the fork at the dose (EC docked, tilted 30°), carried along the travel and set on the nest
    dose_objs = objs["docked, tilt 30°"] + [("draft shield", _fcl_model(sh["panels"].merge(sh["frame"])),
                                            (np.full(3, -1e9), np.full(3, 1e9))),
                                           ("shield door (open)", _fcl_model(door_open),
                                            (np.full(3, -1e9), np.full(3, 1e9)))]
    path = {}
    for kind in ("vial", "cup"):
        C.NEST = kind
        vm = vessel_mesh(kind)
        sm = C.shuttle_meshes_r14(kind)["moving"]
        pm = C.post_meshes(kind)
        nest_o = ("nest", _fcl_model(pm["nest"]), (np.full(3, -1e9), np.full(3, 1e9)))
        worst_v, worst_f, worst_v5 = (1e9, "", 0.0), (1e9, "", 0.0), (1e9, "", 0.0)
        for s in np.linspace(0.0, 1.0, 41):
            base = C.vessel_at(kind, float(s), 0.0)
            v = vm.translate(base, inplace=False)
            o = _fcl_model(v)
            lo, hi = np.asarray(v.bounds[::2]), np.asarray(v.bounds[1::2])
            d, key = min_dist(o, dose_objs + ([nest_o] if s > 1e-6 else []), lo, hi)
            if d < worst_v[0]:
                worst_v = (d, key, float(s))
            d, key = min_dist(o, objs["docked, tilt 30°"], lo, hi)
            if d < worst_v5[0]:
                worst_v5 = (d, key, float(s))
            f = sm.translate((0, -C.TRAVEL * s, 0), inplace=False)
            fo = _fcl_model(f)
            lo, hi = np.asarray(f.bounds[::2]), np.asarray(f.bounds[1::2])
            d, key = min_dist(fo, dose_objs + [nest_o], lo, hi)
            if d < worst_f[0]:
                worst_f = (d, key, float(s))
        seated = vm.translate(C.vessel_at(kind, 0.0, 1.0), inplace=False)
        d_seat, k_seat = min_dist(_fcl_model(seated), dose_objs)
        dropped = sm.translate((0, 0, -C.FORK_DROP), inplace=False)
        d_drop, k_drop = min_dist(_fcl_model(dropped), [nest_o], np.asarray(dropped.bounds[::2]),
                                  np.asarray(dropped.bounds[1::2]))
        d_vf, _ = min_dist(_fcl_model(seated), [("fork", _fcl_model(dropped), (np.full(3, -1e9), np.full(3, 1e9)))])
        rim = C.seat_z_of(kind, "r14") + H[kind]
        rim9 = C.SEAT_Z + H[kind]
        path[kind] = dict(seat_z=C.seat_z_of(kind, "r14"), rim_z=round(rim, 1), fall_mm=round(EXIT_Z - rim, 1),
                          fall_round9_mm=round(EXIT_Z - rim9, 1),
                          carried_min_mm=round(worst_v[0], 1), carried_nearest=worst_v[1], at_shuttle=worst_v[2],
                          carried_min_to_v5_mm=round(worst_v5[0], 1), carried_nearest_v5=worst_v5[1],
                          at_shuttle_v5=worst_v5[2],
                          fork_min_mm=round(worst_f[0], 1), fork_nearest=worst_f[1],
                          seated_min_mm=round(d_seat, 1), seated_nearest=k_seat,
                          fork_dropped_to_nest_mm=round(d_drop, 2), fork_dropped_to_vessel_mm=round(d_vf, 2),
                          ring_inner_d=round(2 * C.nest_ring_r(kind)[0], 2), ring_h=C.NEST_RING_H,
                          mouth_margin_each_side_mm=round((MOUTH[kind] - STREAM_D) / 2, 2),
                          post_top_under_parked_ec_mm=round(room["parked"]["r20"] - (C.seat_z_of(kind, "r14")
                                                                                   + C.NEST_RING_H), 1))
    C.NEST = "vial"
    out["vessel_at_the_dose"] = path
    out["stream"] = dict(exposed_before_mm=round(EXIT_Z - float(CP.HR2_H) - 2.0, 1),
                         note="round 9-13: the top door open, the stream fell from the exit (435.9) to the balance's "
                              "top (312) in the rig's open interior, then 31 mm inside the chamber; round 14: the shield's "
                              "roof is at SHIELD_TOP, the stream above it runs between the module's outlet door and the "
                              "EC's -x face")
    out["drift"] = drift(path)
    out["balance_turned_round"] = turned_round(parts, sts)
    return out


def _surface_points(st, parts, x, y, r, z0=250.0):
    """Points sampled every 1.5 mm or so on the surfaces of v5's parts (not the balance) within r of (x, y), above z0."""
    pts_all = []
    for p in C.lowered(CL.placements(st)):
        if p.key in C.SKIP or p.key.startswith("hr202i"):
            continue
        m = parts[p.key]
        if not m.n_points:
            continue
        P = m.points @ p.M[:3, :3].T + p.M[:3, 3]
        lo, hi = P.min(0), P.max(0)
        if hi[0] < x - r or lo[0] > x + r or hi[1] < y - r or lo[1] > y + r or hi[2] < z0:
            continue
        f = m.triangulate().faces.reshape(-1, 4)[:, 1:]
        a, b, c = P[f[:, 0]], P[f[:, 1]], P[f[:, 2]]
        e = np.maximum(np.linalg.norm(b - a, axis=1), np.maximum(np.linalg.norm(c - a, axis=1),
                                                                 np.linalg.norm(c - b, axis=1)))
        n = np.clip(np.ceil(e / 1.5).astype(int), 1, 80)
        S = [a, b, c]
        for k in np.unique(n):
            if k <= 1:
                continue
            sel = n == k
            A, B, Cc = a[sel], b[sel], c[sel]
            for i in range(k + 1):
                for j in range(k + 1 - i):
                    S.append(A + (i / k) * (B - A) + (j / k) * (Cc - A))
        S = np.vstack(S)
        S = S[(S[:, 2] > z0) & (np.hypot(S[:, 0] - x, S[:, 1] - y) <= r)]
        if len(S):
            pts_all.append(S)
    return np.vstack(pts_all) if pts_all else np.zeros((0, 3))


def drift(path) -> dict:
    """How far a draft carries grains over the fall, round 9-13 against round 14. A grain falling at its terminal speed
    v_t in still air while a cross draft u acts over an exposed height h lands about u h / v_t off the axis (Stokes;
    a dense stream falls faster than single grains, so this overstates it, the same way for both). u: 0.1 m/s, a typical
    draft at a bench (a balance in still air sees under 0.05). The particle sizes are the 20-63 µm cut's d10/d50/d90
    (k7m2q9, assumed for every powder) and the densities AlSi10Mg 2.67, Si 2.33, Ni 8.9, Cu 8.96 g/cm³."""
    mu, g, u = 1.81e-5, 9.81, 0.10
    sizes = {"d10": 25e-6, "d50": 40e-6, "d90": 60e-6}
    rho = {"Si": 2330.0, "AlSi10Mg": 2670.0, "Ni": 8900.0, "Cu": 8960.0}
    # exposed: round 9-13 (no shield; the top door open), the fall above the balance's top in the rig's interior; the
    # 31 mm inside the chamber, under its open top door, counted at half the draft. Round 14: inside the shield, the
    # fall below its roof counted at a tenth of the draft (the shield is open at its notch); above the roof, the stream
    # runs between the module's outlet door and the EC's face (counted at half)
    out = {}
    for kind in ("cup", "vial"):
        p = path[kind]
        rim9 = EXIT_Z - p["fall_round9_mm"]
        rim14 = p["rim_z"]
        roof9 = float(CP.HR2_H) + 2.0
        before = (EXIT_Z - roof9) * 1.0 + (roof9 - rim9) * 0.5
        after = (EXIT_Z - C.SHIELD_TOP) * 0.5 + (C.SHIELD_TOP - rim14) * 0.1
        row = dict(effective_exposed_mm=dict(before=round(before, 1), after=round(after, 1)),
                   fall_mm=dict(before=p["fall_round9_mm"], after=p["fall_mm"]))
        for pw, r in rho.items():
            for lab, d in sizes.items():
                vt = r * g * d * d / (18 * mu)
                row[f"{pw} {lab}"] = dict(v_t_m_s=round(vt, 3), drift_before_mm=round(u * before / vt, 1),
                                          drift_after_mm=round(u * after / vt, 1))
        out[kind] = row
    out["model"] = ("drift = u h_eff / v_t, Stokes terminal speed v_t = rho g d^2 / (18 mu); u = 0.1 m/s; h_eff weighs "
                    "each part of the fall by how open it is to the room (1 open, 0.5 under an open top door or "
                    "between the outlet door and the EC, 0.1 inside our shield); an estimate to compare the two "
                    "stations, not a prediction of strays (powder-doser's T8b would measure them)")
    return out


def turned_round(parts, sts) -> dict:
    """The HR-202i turned 180° about the pan's axis, against v5's parts parked and at the dose (its top door off)."""
    import pyvista as pv
    R = np.eye(4)
    R[:2, :2] = [[-1, 0], [0, -1]]
    M = np.eye(4)
    M[:2, 3] = C.PAN_XY
    Mi = np.eye(4)
    Mi[:2, 3] = -C.PAN_XY
    rot = M @ R @ Mi
    bal = []
    for p in CL.placements(CL.State(ext=0.0, beaker=False)):
        if p.key.startswith("hr202i") and p.key != "hr202i_top_door":
            m = parts[p.key]
            pts = m.points @ p.M[:3, :3].T + p.M[:3, 3]
            pts = pts @ rot[:3, :3].T + rot[:3, 3]
            bal.append(pv.PolyData(pts, m.faces))
    body = pv.merge(bal)
    o = _fcl_model(body)
    lo, hi = np.asarray(body.bounds[::2]), np.asarray(body.bounds[1::2])
    res = {"bounds_x": [round(float(lo[0]), 1), round(float(hi[0]), 1)]}
    for k in ("parked", "docked, tilt 30°"):
        ob = v5_objects(sts[k], parts, skip=("hr202i",))
        # every part, not just the dose zone's: the body reaches the frame's front
        import fcl
        hits = []
        for p in C.lowered(CL.placements(sts[k])):
            if p.key in C.SKIP or p.key.startswith("hr202i"):
                continue
            m = parts[p.key]
            if not m.n_points:
                continue
            pts = m.points @ p.M[:3, :3].T + p.M[:3, 3]
            a, b = pts.min(0), pts.max(0)
            if np.any(a > hi) or np.any(b < lo):
                continue
            q = _fcl_model(pv.PolyData(pts, m.faces))
            req, rs = fcl.CollisionRequest(), fcl.CollisionResult()
            if fcl.collide(o, q, req, rs) > 0:
                hits.append(p.key)
        res[k] = sorted(set(hits))
        del ob
    return res


def figure(m: dict, path: Path) -> None:
    """Two sections through the pan's axis (y = const), round 9-13 and round 14, with v5 at the dose."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pyvista as pv
    from matplotlib.patches import Rectangle
    parts = C.part_meshes(C.PORT_R14)
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 8.2), sharey=True)
    st_dose = CL.State(ext=C.DOCK_EXT, tilt=C.TILT, magnet_on=True, top_door=C.TOP_OPEN, beaker=False)
    st_park = CL.State(ext=0.0, beaker=False)

    def outline(ax, mesh, color, lw=0.7, alpha=1.0, ls="-"):
        try:
            sl = mesh.slice(normal=(0, 1, 0), origin=(PX, PY, 0))
        except Exception:                # noqa: BLE001
            return
        if sl.n_points == 0:
            return
        lines = sl.lines.reshape(-1, 3)[:, 1:] if sl.lines.size else []
        for a, b in lines:
            P = sl.points[[a, b]]
            ax.plot(P[:, 0], P[:, 2], color=color, lw=lw, alpha=alpha, ls=ls)

    for ax, st_name in zip(axes, ("r9", "r14")):
        for p in C.lowered(CL.placements(st_dose)):
            if p.key in C.SKIP or (st_name == "r14" and p.key == "hr202i_top_door"):
                continue
            mesh = parts[p.key]
            if not mesh.n_points:
                continue
            w = pv.PolyData(mesh.points @ p.M[:3, :3].T + p.M[:3, 3], mesh.faces)
            if w.bounds[0] > 330 or w.bounds[1] < -170 or w.bounds[4] > 560:
                continue
            col = "#c0392b" if p.key == "sam_electronics_carriage" else "#8a8f98"
            outline(ax, w, col, 0.7 if col != "#c0392b" else 1.2)
        # the parked EC, dotted
        for p in C.lowered(CL.placements(st_park)):
            if p.key == "sam_electronics_carriage":
                w = pv.PolyData(parts[p.key].points @ p.M[:3, :3].T + p.M[:3, 3], parts[p.key].faces)
                outline(ax, w, "#c0392b", 0.8, 0.6, ":")
        teal = "#1a8c8c"
        if st_name == "r9":
            seat = C.seat_mesh(seat_z=C.SEAT_Z)
            outline(ax, seat, teal, 1.2)
            kind_z = C.SEAT_Z
            ax.add_patch(Rectangle((PX - C.CUP_D / 2, kind_z), C.CUP_D, C.CUP_L, fill=False, ec="#b5651d", lw=1.4))
            rim = kind_z + C.CUP_L
            ttl = "Rounds 9-13: the cup on our pedestal, through the balance's side door"
            ax.annotate("", xy=(PX - 70, rim), xytext=(PX - 70, EXIT_Z), arrowprops=dict(arrowstyle="<->", lw=1.0))
            ax.text(PX - 75, (rim + EXIT_Z) / 2, f"{EXIT_Z - rim:.0f} mm\nfall", ha="right", va="center", fontsize=10)
            ax.text(-150, 318, "balance's top door slid back: the stream falls 124 mm\nin the rig's open interior, then "
                    "31 mm in the chamber", fontsize=8.5, color="#555")
        else:
            C.NEST = "cup"
            pm = C.post_meshes("cup")
            for k in ("foot", "tube", "nest"):
                outline(ax, pm[k], teal if k != "tube" else "#222", 1.2)
            outline(ax, C.roof_mesh(), "#5b8fb0", 1.2)
            sh = C.shield_meshes()
            outline(ax, sh["panels"], "#5b8fb0", 1.4)
            outline(ax, sh["frame"], teal, 1.0)
            s = C.seat_z_of("cup", "r14")
            ax.add_patch(Rectangle((PX - C.CUP_D / 2, s), C.CUP_D, C.CUP_L, fill=False, ec="#b5651d", lw=1.4))
            rim = s + C.CUP_L
            ttl = "Round 14: the cup on our dose post's nest, inside our draft shield"
            ax.annotate("", xy=(PX + 95, rim), xytext=(PX + 95, EXIT_Z), arrowprops=dict(arrowstyle="<->", lw=1.0))
            ax.text(PX + 100, rim - 12, f"{EXIT_Z - rim:.0f} mm fall", ha="left", va="center", fontsize=10)
            ax.text(-150, 250, "roof plate in the top door's rails;\nthe post passes its 21 mm hole untouched",
                    fontsize=8.5, color="#2c6e91")
            ax.text(-150, 440, f"draft shield (ours),\nup to {C.SHIELD_TOP:.0f} mm", fontsize=8.5, color="#2c6e91")
            C.NEST = "vial"
        ax.plot([PX, PX], [rim, EXIT_Z], color="#d9a520", lw=5, alpha=0.55, solid_capstyle="butt")
        ax.plot(EXIT[0], EXIT_Z, marker="v", color="#d9a520", ms=10, mec="k")
        ax.axhline(m["room_over_pan"]["parked"]["r20"], color="#c0392b", lw=0.8, ls=":")
        ax.text(160, m["room_over_pan"]["parked"]["r20"] + 3, "EC parked (dotted): its underside over the axis",
                fontsize=8, color="#c0392b")
        ax.text(160, 470, "EC docked and tilted 30° (red)", fontsize=8, color="#c0392b")
        ax.set_title(ttl, fontsize=11)
        ax.set_xlim(-160, 330)
        ax.set_ylim(0, 520)
        ax.set_aspect("equal")
        ax.set_xlabel("x along the augers, mm (rig frame; section through the pan's axis)")
    axes[0].set_ylabel("height over the bench, mm")
    fig.suptitle("Multi-doser v5 (powder-doser 353dae7) at the 30° dose: the fall into a charge cup, before and after",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    jp = OUT / "doser_shield.json"
    if len(sys.argv) > 1 and sys.argv[1] == "figure":
        figure(json.loads(jp.read_text()), OUT / "doser_shield_section.png")
        print("->", OUT / "doser_shield_section.png")
    else:
        m = measure()
        jp.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
        print(json.dumps({k: m[k] for k in ("room_over_pan", "fixed_parts_vs_v5", "vessel_at_the_dose",
                                            "post_to_roof_plate_mm", "balance_turned_round")}, indent=1,
                         ensure_ascii=False))
