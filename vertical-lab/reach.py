"""Which UR arm: UR3e, UR7e or UR10e, parked on its MiR250 in front of the Kardex opening (animate.py's layout).

For each arm, with its base where the animation puts it:

* the seats the workflow uses: the vial rack and the multi-doser's vessel shuttle (v5, round 9) on tray B, the holder
  on the arm's own base, the free seat in the CubXL's vial holder on tray A (each with the gripper pointing the way the
  animation grips there);
* coverage: the share of the presented tray (50 mm grid) the gripper reaches pointing straight down, 100 mm and 250 mm
  over the tray floor;
* overhead clearance: for every reachable grid point, the lowest gap between the arm (elbow, forearm, wrists) and the
  opening's header, and whether any of it has to go above the header to get there.

    python3 reach.py            # -> out/reach.json, and a table on stdout
"""
from __future__ import annotations

import json
import sys

import numpy as np

import animate as A
import props as P
import ur_arm
import vlm as V
from scene import T

ARMS = ("ur3e", "ur7e", "ur10e")
FRONT = -V.UNIT_D / 2 - V.SKIN                 # outer face of the front panel


def base_world() -> np.ndarray:
    return T((A.AMR_XY[0] + A.ARM_LOCAL[0], A.AMR_XY[1] + A.ARM_LOCAL[1], P.AMR_TOP))


def solve(model, Tw, seeds):
    Bi = np.linalg.inv(base_world())
    best = None
    for s in seeds:
        try:
            q = ur_arm.ik(model, Bi @ Tw, s)
        except ValueError:
            continue
        fk = ur_arm.fk(model, q)
        tcp = base_world() @ fk["tool0"] @ T((0, 0, ur_arm.TCP_MM))
        if np.linalg.norm(tcp[:3, 3] - Tw[:3, 3]) > 1.0:
            continue
        pts = [(base_world() @ fk[k])[:3, 3] for k in ("upper_arm", "forearm", "wrist1", "wrist2", "wrist3")]
        top = max(p[2] for p in pts)
        if best is None or top < best[1]:
            best = (q, top, pts)
    return best


def header_gap(pts) -> float:
    """Smallest gap below the header (Z_OPEN_TOP) of the arm's joints that are inside the bay or within 150 mm of
    its face (positive: clear)."""
    gaps = [V.Z_OPEN_TOP - p[2] for p in pts if p[1] > FRONT - 150.0]
    return min(gaps) if gaps else float("inf")


def seats() -> dict[str, np.ndarray]:
    """The workflow's grip poses, world frame (the trays at the opening)."""
    import carousel as C
    out = {}
    block, rs = P.vial_rack()
    rack_xy = A.LOADS["B"][0][1:]
    s = np.array(rs[A.RACK_SEAT]) + (*rack_xy, V.T_FLOOR)
    out["vial rack (tray B)"] = A.down(A.tray_world("B", s + (0, 0, 50.0)))
    # round 10: the multi-doser is v5 (round 9, carousel.py), unturned at animate.LOADS's place. No gripper reaches its
    # balance's pan, so the arm stands the vial upright on the fork of our vessel shuttle, 71 mm outside the port in
    # its -y panel, gripping it 50 mm up from above (animate.workflow, step 2). Round 8's seat was the v2 doser's cup,
    # gripped level, on a rig turned 90 degrees
    car_xy = next((x, y) for k, x, y in A.LOADS["B"] if k == "carousel")
    hand = C.vessel_at("vial", 1.0, 0.0) + (*car_xy, V.T_FLOOR)
    out["multi-doser shuttle fork (tray B)"] = A.down(A.tray_world("B", hand + (0, 0, 50.0)), spin=180.0)
    _, seat = P.buffer_holder()
    b = A.AMR_XY[0] + A.BUFFER_LOCAL[0], A.AMR_XY[1] + A.BUFFER_LOCAL[1], P.AMR_TOP - 20 + seat[2] + 50.0
    out["holder on the arm's base"] = A.down(np.array(b))
    # the CubXL's free seat on tray A. Round 10: the corrosion set-up (cubxl_rig.CubRig at CUB_AT, x -300), the seat the
    # 9:09 clip stands the vial in (instruments_lab.POWDER_TEST["seat"], gripped 50 mm up, spin 0). Round 8 used round
    # 2's CubXL rack at x -112, which the corrosion set-up replaced
    try:
        import cubxl_rig as CR
        import instruments_lab as IL
        import tour
        inst, _ = tour.load(["cubxl_corrosion"])["cubxl_corrosion"]
        x0, x1, y0, y1, z0, _ = inst.bbox()
        at = T((CR.CUB_AT[0] - (x0 + x1) / 2, CR.CUB_AT[1] - (y0 + y1) / 2, V.T_FLOOR - z0))
        sx, sy = IL.POWDER_TEST["seat"]
        p = (at @ np.array([IL._cx(sx), IL._cy(sy), IL._cz(0.0), 1.0]))[:3]
        out["CubXL holder seat (tray A)"] = A.down(A.tray_world("A", p + (0, 0, 50.0)), spin=0.0)
    except Exception as e:                       # noqa: BLE001  (the corrosion model isn't cached: round 2's rack)
        print(f"reach: CubXL seat from round 2's rack ({type(e).__name__}: {e})", flush=True)
        import lab
        _, bb = lab.meshes()["equipment"]["cubxl_frame"]
        cx, cy = (bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2
        x, y = A.LOADS["A"][0][1:]
        p = np.array(A.CUB_SLOT) + (x - cx, y - cy, V.T_FLOOR - bb[4])
        out["CubXL rack seat (tray A, round 2's)"] = A.down(A.tray_world("A", p + (0, 0, 50.0 - 8.0)))
    return out


def main():
    res = {}
    seeds = [np.radians(q) for q in ((-90, -100, 120, -110, -90, 0), (-90, -60, 90, -120, -90, 0),
                                     (-60, -80, 100, -110, -90, 0), (-120, -80, 100, -110, -90, 0),
                                     (-90, -120, 60, -30, 90, 0), (-90, -45, 45, -90, -90, 0))]
    grid = [(x, y) for x in np.arange(-V.TRAY_W / 2 + 50, V.TRAY_W / 2 - 49, 50.0)
            for y in np.arange(-V.TRAY_D / 2 + 50, V.TRAY_D / 2 - 49, 50.0)]
    for m in ARMS:
        r = dict(reach_mm=ur_arm.MODELS[m]["reach_mm"], payload_kg=ur_arm.MODELS[m]["payload_kg"], seats={})
        for name, Tw in seats().items():
            b = solve(m, Tw, seeds)
            g = None if b is None else header_gap(b[2])
            r["seats"][name] = None if b is None else dict(highest_joint_mm=round(b[1]),
                                                           header_gap_mm=None if g == float("inf") else round(g))
        for h in (100.0, 250.0):
            ok = gaps = 0
            worst = float("inf")
            depth = []
            for x, y in grid:
                b = solve(m, A.down(A.tray_world("B", (x, y, V.T_FLOOR + h))), seeds)
                if b is None:
                    continue
                g = header_gap(b[2])
                if g < 0:
                    gaps += 1
                    continue
                ok += 1
                worst = min(worst, g)
                depth.append(y + V.TRAY_D / 2)
            r[f"tray_cover_{int(h)}mm"] = dict(share=round(ok / len(grid), 3), reachable_only_over_header=gaps,
                                               min_header_gap_mm=None if worst == float("inf") else round(worst),
                                               deepest_mm=None if not depth else round(max(depth)))
        res[m] = r
        print(m, json.dumps(r), flush=True)
    import scene
    (scene.OUT / "reach.json").write_text(json.dumps(dict(
        base_mm=[round(v, 1) for v in base_world()[:3, 3]], header_mm=V.Z_OPEN_TOP, table_mm=V.Z_SILL,
        tray_presented_floor_mm=V.Z_OPEN + V.T_FLOOR, arms=res), indent=1) + "\n")


if __name__ == "__main__":
    sys.exit(main())
