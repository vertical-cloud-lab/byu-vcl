"""Where on the PandaDeck should the OpenRAMAN go? Exhaustive search over poses.

Decision: rotation theta in {0, 90, 180, 270} deg and translation (tx, ty) on a 5 mm grid
(the adapter's keys are generated for whichever slots end up under it, so the pose need
not sit on the 25 x 45 mm slot pitch).

Hard constraints
  1. the spectrometer + adapter + dock footprint stays on the 480 x 490 mm deck (the
     gantry's side plates run just outside it);
  2. the pipette reaches the tip station and +-5 mm along the beam, for an autofocus scan;
  3. the capper, which hangs 17 mm below the nozzle and 54 mm to -x / 13 mm to -y of it,
     clears everything taller than 31 mm while the tip is in the dock (its bottom is then
     at 36 mm above the baseplate; KM100s, FMP1s, cage, camera, cover are all taller);
  4. Ben's current vial column and 2 x 15 tip rack stay where they are;
  5. at least four slots under the adapter, spanning two rows and two columns, for keys.
Objective
  pipette-reachable deck area the footprint takes away (cm^2), i.e. what is lost for
  labware; ties broken towards the footprint sitting farther from the reach centre.

    python optimize_layout.py /path/to/openraman/cad   ->  best_pose.json, layout_optimization.png
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from shapely import affinity
from shapely.geometry import MultiPoint, Point, Polygon, box as sbox
from shapely.ops import unary_union
from shapely.prepared import prep

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cad"))
import cubxl_parts as cx  # noqa: E402
import openraman_assembly as oa  # noqa: E402

THETAS = (0, 90, 180, 270)
STEP = 5.0
TALL_Z = cx.DOCK_TOP + 1.0          # 31 mm above the baseplate top (capper bottom 36 minus 5 margin)
SCAN = 5.0                          # autofocus travel either side of the focus, mm
RESERVED_CUBOS = {                  # Ben's deck today (cubos/configs/deck/ben_6vials_tiprack.yaml, sterling_6vials*.yaml)
    "vial column (6 x 20 mL)": (189.0 - 22.0, 6.0, 189.0 + 22.0, 213.0),
    "2 x 15 tip rack": (314.75 - 33.0, 105.2 - 69.0, 314.75 + 33.0, 105.2 + 69.0),
}


def footprints(openraman_cad):
    parts, _, _ = oa.build(openraman_cad)
    hulls, tall = [], []
    shapes = [p.shape for p in parts] + [cx.tip_dock()]
    for s in shapes:
        v, _ = s.tessellate(0.5, 0.5)
        P = np.array([(q.x, q.y, q.z) for q in v])
        h = MultiPoint(P[:, :2]).convex_hull
        hulls.append(h)
        if P[:, 2].max() > TALL_Z:
            tall.append(h)
    outline = Polygon(cx.adapter_outline())
    return unary_union(hulls + [outline]), unary_union(tall), outline


def to_deck(geom, theta, tx, ty):
    return affinity.translate(affinity.rotate(geom, theta, origin=(0, 0)), tx, ty)


def deck_rect():
    return sbox(0.0, -cx.DECK_D, cx.DECK_W, 0.0)


def reserved_deck():
    out = {}
    for k, (x0, y0, x1, y1) in RESERVED_CUBOS.items():
        X0, Y0 = cx.cubos_to_deck(x0, y0)
        X1, Y1 = cx.cubos_to_deck(x1, y1)
        out[k] = sbox(min(X0, X1), min(Y0, Y1), max(X0, X1), max(Y0, Y1))
    return out


def search(foot, tall, outline):
    """Every pose that is on the deck with the tip reachable, with each other constraint
    recorded separately so scenarios can be compared."""
    reach = Polygon(cx.reach_polygon_deck())
    reach_in = prep(reach.buffer(-2.0))
    deck = prep(deck_rect())
    reserved = unary_union(list(reserved_deck().values()))
    rc = np.array(reach.centroid.coords[0])
    focus = oa.SAMPLE_FOCUS[:2]
    out = []
    for th in THETAS:
        f0, t0 = affinity.rotate(foot, th, origin=(0, 0)), affinity.rotate(tall, th, origin=(0, 0))
        c, s_ = np.cos(np.radians(th)), np.sin(np.radians(th))
        Rm = np.array([[c, -s_], [s_, c]])
        f_xy, beam = Rm @ focus, Rm @ np.array([1.0, 0.0])
        bx0, by0, bx1, by1 = f0.bounds
        for tx in np.arange(-bx0, cx.DECK_W - bx1 + 1e-6, STEP):
            for ty in np.arange(-cx.DECK_D - by0, -by1 + 1e-6, STEP):
                tip = f_xy + (tx, ty)
                if not all(reach_in.contains(Point(*(tip + k * SCAN * beam))) for k in (-1, 0, 1)):
                    continue
                fD = affinity.translate(f0, tx, ty)
                if not deck.contains(fD):
                    continue
                cxy = tip + np.array([cx.CAPPER_FROM_PIPETTE[0], -cx.CAPPER_FROM_PIPETTE[1]])
                capper = sbox(cxy[0] - cx.CAPPER_BOX[0] / 2, cxy[1] - cx.CAPPER_BOX[1] / 2,
                              cxy[0] + cx.CAPPER_BOX[0] / 2, cxy[1] + cx.CAPPER_BOX[1] / 2).buffer(3.0)
                keys = cx.keys_for_pose(th, tx, ty)
                lost = fD.intersection(reach).area / 100.0
                spread = np.linalg.norm(np.array(fD.centroid.coords[0]) - rc)
                out.append(dict(theta=th, tx=float(tx), ty=float(ty), lost_cm2=round(lost, 1),
                                score=lost - 0.01 * spread, tip_deck=[round(float(v), 2) for v in tip],
                                tip_cubos=[round(float(v), 2) for v in cx.deck_to_cubos(*tip)],
                                capper_deck=[round(float(v), 2) for v in cxy], n_keys=len(keys), keys=keys,
                                capper_ok=not capper.intersects(affinity.translate(t0, tx, ty)),
                                labware_ok=not fD.intersects(reserved),
                                keys_ok=len(keys) >= 4 and len({k[0] for k in keys}) >= 2 and len({k[1] for k in keys}) >= 2))
    return out


SCENARIOS = {"keep Ben's labware": lambda r: r["capper_ok"] and r["keys_ok"] and r["labware_ok"],
             "labware can move": lambda r: r["capper_ok"] and r["keys_ok"]}


def plot(cands, best, foot, tall, outline, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly

    fig = plt.figure(figsize=(16, 8.6))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.35, 1, 1])
    ax = fig.add_subplot(gs[:, 0])
    ax.add_patch(MPoly(np.array(deck_rect().exterior.coords), fc="#e9eef2", ec="#7a8794", lw=1.2))
    for x in cx.SLOT_X:
        for y in cx.SLOT_Y:
            ax.add_patch(plt.Rectangle((x - 5, y - 12.5), 10, 25, fc="white", ec="#b8c2cc", lw=0.6))
    reach = Polygon(cx.reach_polygon_deck())
    ax.add_patch(MPoly(np.array(reach.exterior.coords), fc="#2a9d8f", alpha=0.12, ec="#2a9d8f", lw=1.5,
                       label="pipette reach (assumed CubOS↔deck map)"))
    for k, r in reserved_deck().items():
        ax.add_patch(MPoly(np.array(r.exterior.coords), fc="#e9c46a", alpha=0.55, ec="#b58b00", lw=1))
        ax.text(*r.centroid.coords[0], k, ha="center", va="center", fontsize=7.5, rotation=90)
    th, tx, ty = best["theta"], best["tx"], best["ty"]
    for g, kw in ((foot, dict(fc="#264653", alpha=0.35, ec="#264653", label="spectrometer + adapter + dock")),
                  (tall, dict(fc="#264653", alpha=0.55, ec="none", label="parts taller than 31 mm"))):
        gd = to_deck(g, th, tx, ty)
        for poly in getattr(gd, "geoms", [gd]):
            ax.add_patch(MPoly(np.array(poly.exterior.coords), **kw))
            kw.pop("label", None)
    for X, Y in best["keys"]:
        ax.add_patch(plt.Rectangle((X - 4.9, Y - 12.4), 9.8, 24.8, fc="#e76f51", ec="k", lw=0.6))
    tip, cap = best["tip_deck"], best["capper_deck"]
    bdir = np.array([np.cos(np.radians(th)), np.sin(np.radians(th))])
    ax.annotate("", xy=np.array(tip) + 30 * bdir, xytext=np.array(tip) - 70 * bdir,
                arrowprops=dict(arrowstyle="->", color="#00b050", lw=2))
    ax.plot(*tip, marker="*", ms=16, color="#00b050", mec="k", label="tip station (laser focus)")
    ax.add_patch(plt.Rectangle((cap[0] - 25, cap[1] - 16), 50, 32, fc="none", ec="#d62828", lw=1.5, ls="--",
                               label="capper while the tip is docked"))
    ax.set_xlim(-10, 490); ax.set_ylim(-500, 10); ax.set_aspect("equal")
    ax.set_xlabel("PandaDeck X (mm)"); ax.set_ylabel("PandaDeck Y (mm)  — back edge at 0")
    ax.set_title(f"Best pose: θ = {th}°, takes {best['lost_cm2']:.0f} cm² of reachable deck\n"
                 f"tip station at CubOS deck ({best['tip_cubos'][0]:.0f}, {best['tip_cubos'][1]:.0f}) mm", fontsize=11)
    ax.legend(loc="lower left", fontsize=7.5, framealpha=0.9)

    reach_area = reach.area / 100.0
    free = SCENARIOS["labware can move"]
    for i, t in enumerate(THETAS):
        a = fig.add_subplot(gs[i // 2, 1 + i % 2])
        C = [r for r in cands if r["theta"] == t]
        R = [r for r in C if free(r)]
        bad = [r for r in C if not r["capper_ok"]]
        a.add_patch(MPoly(np.array(deck_rect().exterior.coords), fc="#f4f4f4", ec="#999", lw=0.8))
        a.add_patch(MPoly(np.array(reach.exterior.coords), fc="none", ec="#2a9d8f", lw=1))
        if bad:
            P = np.array([r["tip_deck"] for r in bad])
            a.scatter(P[:, 0], P[:, 1], s=5, c="#d62828", alpha=0.5, label="tip positions where the capper collides")
        if R:
            P = np.array([r["tip_deck"] for r in R]); L = np.array([r["lost_cm2"] for r in R])
            sc = a.scatter(P[:, 0], P[:, 1], c=L, s=6, cmap="viridis_r", vmin=0, vmax=max(1.0, L.max()))
            b = min(R, key=lambda r: r["score"])
            a.plot(*b["tip_deck"], marker="*", ms=12, color="#00b050", mec="k")
            a.set_title(f"θ = {t}° (labware movable): {len(R)} of {len(C)} poses ok\n"
                        f"best loses {b['lost_cm2']:.0f} of {reach_area:.0f} cm² reachable", fontsize=9)
            fig.colorbar(sc, ax=a, fraction=0.046, pad=0.02, label="cm² of reach lost")
        elif C:
            a.set_title(f"θ = {t}°: none of {len(C)} on-deck, reachable poses ok:\n"
                        f"the capper lands on a KM100/FMP1/cage in {len(bad)}", fontsize=9)
        else:
            a.set_title(f"θ = {t}°: no pose has the tip in reach\nwith the spectrometer still on the deck", fontsize=9)
        if bad:
            a.legend(loc="lower right", fontsize=7, markerscale=3)
        a.set_xlim(-10, 490); a.set_ylim(-500, 10); a.set_aspect("equal"); a.tick_params(labelsize=7)
    fig.suptitle("OpenRAMAN on the CubXL PandaDeck: exhaustive pose search (5 mm grid, 4 rotations)", fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def main(openraman_cad):
    t = time.time()
    foot, tall, outline = footprints(openraman_cad)
    cands = search(foot, tall, outline)
    scen = {}
    for name, ok in SCENARIOS.items():
        R = [r for r in cands if ok(r)]
        scen[name] = dict(n_feasible=len(R),
                          by_theta={str(k): sum(r["theta"] == k for r in R) for k in THETAS},
                          best=(min(R, key=lambda r: r["score"]) if R else None))
    by_theta = {str(k): dict(on_deck_and_reachable=sum(r["theta"] == k for r in cands),
                             capper_collides=sum(r["theta"] == k and not r["capper_ok"] for r in cands),
                             overlaps_labware=sum(r["theta"] == k and not r["labware_ok"] for r in cands),
                             too_few_key_slots=sum(r["theta"] == k and not r["keys_ok"] for r in cands)) for k in THETAS}
    best = scen["keep Ben's labware"]["best"] or scen["labware can move"]["best"]
    summary = dict(best=best, scenarios=scen, constraint_counts_by_theta=by_theta,
                   footprint_cm2=round(foot.area / 100.0, 1),
                   reach_cm2=round(Polygon(cx.reach_polygon_deck()).area / 100.0, 1),
                   assumptions=dict(cubos_from_deck=cx.CUBOS_FROM_DECK, pipette_reach=cx.PIPETTE_REACH,
                                    capper_from_pipette=cx.CAPPER_FROM_PIPETTE, capper_box=cx.CAPPER_BOX,
                                    tall_threshold_mm=TALL_Z, reserved_cubos=RESERVED_CUBOS),
                   seconds=round(time.time() - t, 1))
    (HERE / "best_pose.json").write_text(json.dumps(summary, indent=2))
    plot(cands, best, foot, tall, outline, HERE / "layout_optimization.png")
    print(json.dumps(dict(best={k: best[k] for k in ("theta", "tx", "ty", "lost_cm2", "tip_cubos", "n_keys")},
                          scenarios={k: dict(n=v["n_feasible"], by_theta=v["by_theta"],
                                             best=None if v["best"] is None else {kk: v["best"][kk] for kk in ("theta", "tx", "ty", "lost_cm2", "tip_cubos")})
                                     for k, v in scen.items()}, constraints=by_theta, seconds=summary["seconds"]), indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ext/openraman-cad/cad")
