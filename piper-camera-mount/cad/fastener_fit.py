#!/usr/bin/env python3
"""Which screws fit each joint of the PiPER mount: lengths, heads, and room for the tool.

For each of the six joints (and the HQ Camera's once more with M2, the drawer having no M2.5) it
sweeps standard lengths. For each length it reports how far the tip gets past the far face of its
nut (for the tab screws, how far into the gripper's tab), what it runs into, whether it ends up
behind the J6 flange face or in either camera's picture, and the longest screw that runs into
nothing. Then it puts a socket head (ISO 4762) and three Phillips pan heads (ISO 7045, the older,
wider DIN 7985 that shop bins often hold, and McMaster's) on each screw, and measures the room
around each head and the straight run a driver has out to it.

It uses the same `Params`, parts and gripper model as `piper_mount.py`, so a change there flows
through. `ON_HAND` lists what the lab can get without ordering: the stainless Phillips pan heads
in the ME Prototyping Lab's drawer (photo on #234, 2026-10-02) and the black nylon COMRUN kits.

    python fastener_fit.py     # prints a summary, writes ../exports/fastener_fit.json

Nuts are taken at their thickest (ISO 4032 maximum), the worst case for reach. The HQ Camera's
board is taken as 2.0 mm, as measured on the lab's board for the OT-2 lid mount (#234), not the
1.4 mm on Raspberry Pi's drawing; the drawing's figure is reported alongside.
"""
from __future__ import annotations

import json

import cadquery as cq

import reference
from piper_mount import (CM3W_FOV, EXPORTS, Params, build, cm_holes, cm_place, hq_fov, hq_holes, hq_place,
                         optical_axes, pi_holes, pod_screw_axes, view_pyramid)

LENGTHS = {"M2": (6, 8, 10, 12, 14, 16, 18), "M2.5": (6, 8, 10, 12, 14, 16, 18),
           "M3": (6, 8, 10, 12, 14, 16, 18, 20, 25)}
ON_HAND = {"M2": (6, 12, 18, 25), "M3": (6, 10, 18, 25, 40),      # Prototyping Lab drawer, stainless
           "M2.5": (6, 8, 12)}                                      # COMRUN nylon kit
PITCH = {"M2": 0.4, "M2.5": 0.45, "M3": 0.5}
MAJOR = {"M2": 2.0, "M2.5": 2.5, "M3": 3.0}
NUT_M = {"M2": 1.6, "M2.5": 2.0, "M3": 2.4}                         # ISO 4032 nut height, max
HEADS = {                                                           # dk, k
    "socket (ISO 4762)": {"M2": (3.8, 2.0), "M2.5": (4.5, 2.5), "M3": (5.5, 3.0)},
    "Phillips pan (ISO 7045)": {"M2": (4.0, 1.6), "M2.5": (5.0, 1.75), "M3": (5.6, 2.4)},
    "Phillips pan (DIN 7985)": {"M2": (4.0, 1.6), "M2.5": (5.0, 2.0), "M3": (6.0, 2.4)},
    # McMaster's 18-8 pan heads, the fallback if the drawer runs out (92000A019, 92000A127 pages)
    "Phillips pan (McMaster 92000A)": {"M2": (4.0, 1.7), "M2.5": (5.0, 2.0), "M3": (6.0, 2.5)},
}
DRIVERS = {"#1 Phillips screwdriver (shaft 5 mm)": 5.0, "hex key (3 mm)": 3.0}
HQ_PCB_MEASURED = 2.0
TIGHT = 0.15          # radial room (mm) below which a head may not drop into a printed counterbore


def cylinder(d: float, start: cq.Vector, direction: cq.Vector, length: float) -> cq.Solid:
    return cq.Solid.makeCylinder(d / 2, length, start, direction.normalized())


def cam_axis(place, x: float, y: float, z: float) -> cq.Vector:
    """A point given in a camera's own frame (x, y on the board, z along the optical axis
    backwards), in the gripper frame."""
    v = place(cq.Workplane().add(cq.Vertex.makeVertex(x, y, z))).val()
    return cq.Vector(v.X, v.Y, v.Z)


def joints(p: Params, hq_pcb_t: float) -> dict[str, dict]:
    """Each joint: thread size, screw axes as (seat, unit direction of the shank), and where the
    thread it screws into starts and ends, as distances from the seat. For nuts, the nut is
    pulled up against the face of its trap nearest the head."""
    X, Y = cq.Vector(1, 0, 0), cq.Vector(0, 1, 0)
    out = {}
    # 1. Pad onto the gripper tab: heads on the pad's back face, into the tab's brass inserts.
    seat = p.collar_y0 + p.pad_t
    into = seat - p.plate_back_y
    out["tab: pad -> gripper tab inserts"] = dict(
        size="M3", axes=[(cq.Vector(x, seat, z), -Y) for x, z in p.tab_holes],
        engage=(into, into + p.tab_depth), thread="the tab's insert", counterbore=p.access_d,
        design=p.tab_screw_len)
    # 2. Collar clamp: heads on the carrier side, nuts in the bracket's ears. The model has the
    # split open; tightened, it closes and the carrier (with the heads) moves `shift` toward the nuts.
    seat_x = p.ax_x + p.clamp_head_seat
    floor = p.ax_x - p.ear_w + p.m3_nut_depth
    d0 = seat_x - floor - p.split_gap
    axes = [(cq.Vector(seat_x, y, p.ax_z + sz * p.clamp_r), -X) for sz in (-1, 1) for y in p.clamp_y]
    out["clamp: carrier -> nuts in the bracket's ears"] = dict(
        size="M3", axes=axes, engage=(d0, d0 + NUT_M["M3"]), thread="nut", shift=p.split_gap,
        counterbore=p.m3_head_cb_d, design=p.clamp_screw_len)
    # 3. Pod onto the seat: heads on the pod's back face, nuts in the seat's slots.
    face = p.pod_nut_y + p.m3_nut_depth / 2                    # slot face nearest the head (station y)
    d0 = -p.hq_standoff - face
    out["pod: pod -> nuts in the seat"] = dict(
        size="M3", axes=pod_screw_axes(p), engage=(d0, d0 + NUT_M["M3"]), thread="nut",
        counterbore=None, design=p.pod_screw_len)
    # 4. HQ Camera: heads in counterbores on the pod's front, nuts on the board's back.
    hq = hq_place(p)
    cb_floor = -(p.hq_standoff + p.pod_t) + 2.0                  # camera-frame z of the counterbore floor
    axes = []
    for x, y in hq_holes(p):
        a, b = cam_axis(hq, x, y, cb_floor), cam_axis(hq, x, y, cb_floor + 1.0)
        axes.append((a, (b - a).normalized()))
    out["HQ Camera: pod -> nuts on the camera"] = dict(
        size="M2.5", axes=axes, engage=(-cb_floor + hq_pcb_t, -cb_floor + hq_pcb_t + NUT_M["M2.5"]),
        thread="nut", counterbore=5.0, design=12.0)
    # The drawer has no M2.5, but its M2 pan heads and nuts pass through the HQ's M2.5 holes.
    out["HQ Camera with M2: pod -> nuts on the camera"] = dict(
        size="M2", axes=axes, engage=(-cb_floor + hq_pcb_t, -cb_floor + hq_pcb_t + NUT_M["M2"]),
        thread="nut", counterbore=5.0, design=12.0)
    # 5. Camera Module 3 Wide, the same way.
    cm = cm_place(p)
    cb_floor = -(p.cm_standoff + p.pod_t) + 2.0
    axes = []
    for x, y in cm_holes(p):
        a, b = cam_axis(cm, x, y, cb_floor), cam_axis(cm, x, y, cb_floor + 1.0)
        axes.append((a, (b - a).normalized()))
    out["Wide: pod -> nuts on the camera"] = dict(
        size="M2", axes=axes, engage=(-cb_floor + p.cm_pcb_t, -cb_floor + p.cm_pcb_t + NUT_M["M2"]),
        thread="nut", counterbore=4.2, design=10.0)
    # 6. Pi 5: heads on the board, through the printed spacers, nuts in the carrier's traps.
    top = p.pi_x + 1.6
    floor = p.carrier_x0 + p.m25_nut_h
    out["Pi 5: board -> spacers -> nuts in the carrier"] = dict(
        size="M2.5", axes=[(cq.Vector(top, y, z), -X) for y, z in pi_holes(p)],
        engage=(top - floor, top - floor + NUT_M["M2.5"]), thread="nut", counterbore=None, design=12.0)
    return out


def views(p: Params) -> dict[str, cq.Shape]:
    """Each camera's view, 250 mm deep, as run_checks() draws it for the printed parts."""
    axes = optical_axes(p)
    return {"HQ view": view_pyramid(*axes["hq"], *hq_fov(p), 250.0, aperture=6.0).val(),
            "Wide view": view_pyramid(*axes["cm3w"], *CM3W_FOV, 250.0, aperture=1.5).val()}


def obstacles(p: Params, parts: dict[str, cq.Workplane]) -> dict[str, cq.Shape]:
    names = ("bracket", "pod", "carrier", "pi_spacers", "pi5", "hq_pcb", "hq_mount", "hq_lens",
             "cm_pcb", "cm_module")
    obs = {n: parts[n].val() for n in names}
    obs["gripper body"] = reference.gripper()["body"].val()
    for opening, tag in ((0.0, "closed"), (100.0, "fully open")):
        obs[f"gripper fingers ({tag})"] = reference.gripper(opening)["fingers"].val()
    return obs


def touching(shape: cq.Shape, obs: dict[str, cq.Shape], skip=()) -> dict[str, float]:
    """Obstacles a shape runs into, with the shared volume (mm^3). A boolean, not BRepExtrema's
    distance: that measures between boundaries, so a driver wholly inside a part reads as clear.
    (The gripper's flange, which upsets booleans, is the plain proxy cylinder here.)"""
    found = {}
    a = shape.BoundingBox()
    for name, o in obs.items():
        if name in skip:
            continue
        b = o.BoundingBox()
        if (a.xmax < b.xmin or b.xmax < a.xmin or a.ymax < b.ymin or b.ymax < a.ymin
                or a.zmax < b.zmin or b.zmax < a.zmin):
            continue
        v = sum(s.Volume() for s in shape.intersect(o).Solids())
        if v > 1e-3:
            found[name] = round(v, 3)
    return found


def shank(size: str, seat: cq.Vector, d: cq.Vector, length: float, start: float = 0.0) -> cq.Solid:
    """The thread at its minor diameter (d3 = d - 1.2269 P), so it doesn't graze the clearance
    holes, or the M3 tapped holes AgileX models in the tab at about 2.5 mm."""
    return cylinder(MAJOR[size] - 1.2269 * PITCH[size], seat + d * start, d, length - start)


def longest(size, axes, obs, hi=45.0) -> float | None:
    """Longest screw (to 0.05 mm) whose shank runs into nothing on any of the joint's axes."""
    def clear(L):
        return all(not touching(shank(size, s, d, L, start=0.5), obs) for s, d in axes)
    if clear(hi):
        return None
    lo = 1.0
    while hi - lo > 0.05:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if clear(mid) else (lo, mid)
    return round(lo, 2)


def head_room(size, axes, obs, dk, k) -> dict:
    """Smallest gap from a head (sat 0.01 mm off its seat) to anything around it."""
    gaps = []
    hit = {}
    for s, d in axes:
        h = cylinder(dk, s - d * (k + 0.01), d, k)
        hit.update(touching(h, obs))
        gaps.append(min(h.distance(o) for o in obs.values()))
    return {"min_gap_mm": round(min(gaps), 3), "runs_into": hit}


def driver_reach(axes, obs, dia, k, hi=150.0) -> list[float]:
    """Straight run (mm) a driver of diameter `dia` has from the top of the head outward along
    the screw's axis before it meets anything, per screw (hi = nothing within hi)."""
    out = []
    for s, d in axes:
        start = s - d * (k + 0.05)
        def clear(L):
            return not touching(cylinder(dia, start - d * L, d, L), obs)
        if clear(hi):
            out.append(hi)
            continue
        lo, h = 0.0, hi
        while h - lo > 0.25:
            mid = (lo + h) / 2
            lo, h = (mid, h) if clear(mid) else (lo, mid)
        out.append(round(lo, 1))
    return out


def behind_flange(p: Params, axes, L) -> float:
    """How far (mm, along Y) the furthest tip sits behind the J6 flange face; negative = in front."""
    return round(max((s + d * L).y for s, d in axes) - p.flange_face_y, 2)


def sweep(p: Params, only: str | None = None) -> dict:
    parts = build(p)
    obs = obstacles(p, parts)
    cams = views(p)
    out = {"assumptions": {
        "nut heights (ISO 4032 max, mm)": NUT_M,
        "HQ board (mm)": f"{HQ_PCB_MEASURED} measured (lid mount, #234); drawing says {p.hq_pcb_t}",
        "clamp": "split closed (the tightened state); with it open, every clamp tip is 0.6 mm shorter",
        "on hand": {"Prototyping Lab drawer (stainless Phillips pan)": {k: ON_HAND[k] for k in ("M2", "M3")},
                    "COMRUN nylon kit (Phillips pan)": {"M2.5": ON_HAND["M2.5"]}},
    }, "joints": {}}
    for pcb_label, pcb in (("measured", HQ_PCB_MEASURED), ("drawing", p.hq_pcb_t)):
        for name, j in joints(p, pcb).items():
            if pcb_label == "drawing" and not name.startswith("HQ"):
                continue
            if only and only not in name:
                continue
            key = name if pcb_label == "measured" else f"{name} (board {p.hq_pcb_t} mm, drawing)"
            e0, e1 = j["engage"]
            sh = j.get("shift", 0.0)
            rows = []
            for L in LENGTHS[j["size"]] + tuple(x for x in ON_HAND[j["size"]] if x not in LENGTHS[j["size"]]):
                hits, seen = {}, {}
                for s, d in j["axes"]:
                    hits.update(touching(shank(j["size"], s + d * sh, d, L, start=0.5), obs))
                    seen.update(touching(shank(j["size"], s + d * sh, d, L, start=0.5), cams))
                rows.append({"length": L, "on_hand": L in ON_HAND[j["size"]],
                             "reaches_thread": L >= e0, "past_far_face": round(L - e1, 2),
                             "engaged": round(max(0.0, min(L, e1) - e0), 2),
                             "behind_flange_face": behind_flange(p, j["axes"], L + sh), "runs_into": hits,
                             "in_a_camera_view_mm3": seen})
            rows.sort(key=lambda r: r["length"])
            res = {"size": j["size"], "count": len(j["axes"]), "thread": j["thread"],
                   "design_length": j["design"], "thread_from_seat_mm": [round(e0, 2), round(e1, 2)],
                   "longest_clear_mm": longest(j["size"], [(s + d * sh, d) for s, d in j["axes"]], obs),
                   "lengths": rows}
            if pcb_label == "measured":
                heads = {}
                for kind, table in HEADS.items():
                    dk, k = table[j["size"]]
                    room = head_room(j["size"], j["axes"], obs, dk, k)
                    if j["counterbore"]:
                        room["radial_room_in_counterbore_mm"] = round((j["counterbore"] - dk) / 2, 2)
                        room["may_not_drop_in_as_printed"] = (j["counterbore"] - dk) / 2 < TIGHT
                    heads[kind] = room
                res["heads"] = heads
                k = max(t[j["size"]][1] for t in HEADS.values())
                res["driver_reach_mm"] = {n: driver_reach(j["axes"], obs, dia, k) for n, dia in DRIVERS.items()}
                # Where each screw's head sits, for the README (gripper frame, mm).
                res["seats"] = [[round(c, 2) for c in s.toTuple()] for s, _ in j["axes"]]
            out["joints"][key] = res
            print(f"{key}: thread {e0:.2f}-{e1:.2f} mm from the seat, longest clear {res['longest_clear_mm']}")
            for r in rows:
                print(f"   {r['length']:>4} {'*' if r['on_hand'] else ' '} past {r['past_far_face']:+6.2f}"
                      f"  engaged {r['engaged']:5.2f}  behind flange {r['behind_flange_face']:+6.2f}  {r['runs_into']}"
                      f"  {r['in_a_camera_view_mm3'] or ''}")
    return out


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="re-run only the joints whose name contains this; merges into the JSON")
    args = ap.parse_args()
    p = Params()
    res = sweep(p, args.only)
    path = EXPORTS / "fastener_fit.json"
    if args.only and path.exists():
        old = json.loads(path.read_text())
        old["joints"].update(res["joints"])
        old["assumptions"] = res["assumptions"]
        res = old
    path.write_text(json.dumps(res, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
