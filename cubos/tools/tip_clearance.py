#!/usr/bin/env python3
"""Vertical clearance of the CubXL's pipette tip end (and capper) over each vial.

Written 2026-11-04 for PR #269 (is there room to seat a stirred vial higher?). Run it with
CubOS importable, as for passive_shadow.py. Its answer for Ben's 10-02 deck is in
hardware/vial-stirrer-cubxl/analysis/deck_clearance_output.txt.

passive_shadow.py only reports collisions, and only for the PASSIVE tool. This
wrapper imports it unmodified (record_moves, deck_obstacles, axis_segments,
horizontal_distance_to_axis, _vials_at, analyse) and reports margins for both
the moving and the passive instrument.

Recording. passive_shadow.record_moves() is used as is. Underneath its tracer, a
second wrapper on InstrumentedGantry.move captures the travel Z CubOS actually
computed for each move (last_commanded_pose["travel_z"], gantry frame).
record_moves logs only the travel_z argument, which differs when a raw move
changes XY with no travel_z. The script asserts the two agree wherever an
argument was given, and counts the moves where they differ.

Geometry, the same as passive_shadow's: a vial is a cylinder of radius
diameter/2 = 14 mm, topped by its rim when open or by rim + cap_height (13) when
capped. Open/capped tracking is passive_shadow's (decap opens the vial at the
target XY, cap closes it). The tool is a point:
    tool = gantry + (offset_x, offset_y, -effective_depth)
For the pipette that point is the tip end, or the bare nozzle when no tip is on.
Every commanded pose is expanded into the driver's X, Y, Z segments.

Classification of each (segment, vial) pair whose plan distance is < r:
  insertion  pipette moves vertically along an OPEN vial: the intended entry
             or exit. passive_shadow exempts it too.
  engage     capper moves vertically onto its own target vial (approach
             hover, engage, retract)
  inside     pipette moves laterally inside an OPEN vial, below its rim, with
             both ends inside r (the stir). Reported separately with wall and
             nozzle-depth figures.
  over       everything else. clearance = lowest tool Z on the segment - top.

--tip-stuck matches passive_shadow: the passive pipette always carries the
35 mm tip. The moving pipette also carries it once it has had a tip, so after
drop_tip CubOS plans bare while the tip is still physically on.

The start pose is the homed pose (361, 278, 122), so the move out of the homed
corner is swept too (passive_shadow starts from the first target).
--start-first mimics passive_shadow for cross-checking.

Capper settle sleeps (capture_settle_s) are skipped in this process. They only
wait and do not affect motion.

Usage:
  tip_clearance.py GANTRY DECK PROTOCOL [--cap-height 13] [--tip-stuck] [--json OUT]
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import logging
import math
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import passive_shadow as ps  # noqa: E402  (this directory's, unmodified)

TIP_LEN = 35.0
HOMED = (361.0, 278.0, 122.0)    # working_volume x/y/z max = the homed pose
VIAL_ID = 21.0                   # Ben, PR #269 2026-10-12: inner diameter 21 mm


def record(gantry, deck, protocol):
    import cubos.gantry.instrument_mount as im
    import cubos.protocol_engine.commands.capper as capper_cmd

    real_move = im.InstrumentedGantry.move
    actual = []

    def capture(self, instrument, position, travel_z=None):
        out = real_move(self, instrument, position, travel_z)
        lp = self.last_commanded_pose
        actual.append({"gantry": list(lp["gantry_position"]), "travel_z": lp["travel_z"]})
        return out

    class _NoSleep:
        @staticmethod
        def sleep(_s):
            return None

        def __getattr__(self, k):
            import time
            return getattr(time, k)

    real_time = capper_cmd.time
    im.InstrumentedGantry.move = capture
    capper_cmd.time = _NoSleep()
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            events = ps.record_moves(gantry, deck, protocol)
    finally:
        im.InstrumentedGantry.move = real_move
        capper_cmd.time = real_time
        logging.getLogger().setLevel(logging.CRITICAL)
    assert len(actual) == len(events), (len(actual), len(events))
    n_diff = 0
    for e, a in zip(events, actual):
        assert all(abs(p - q) < 1e-9 for p, q in zip(e["gantry"], a["gantry"])), (e, a)
        if e["travel_z"] is not None:
            assert abs(e["travel_z"] - a["travel_z"]) < 1e-9, (e, a)
        elif a["travel_z"] is not None:
            n_diff += 1
        e["travel_z_actual"] = a["travel_z"]
    return events, n_diff, err.getvalue()


def analyse(events, obstacles, *, tip_stuck, start=HOMED):
    vials = [o for o in obstacles if o["kind"] == "vial"]
    open_vials: set[str] = set()
    pose = tuple(start) if start is not None else None
    had_tip = False
    rows, planes = [], []
    for ev in events:
        target = tuple(ev["gantry"])
        if pose is None:
            pose = target
        segs = ps.axis_segments(pose, target, ev["travel_z_actual"])
        if ev["depths"]["pipette"] >= TIP_LEN - 1e-9:
            had_tip = True
        for inst in ("pipette", "vial_capper_decapper"):
            role = "moving" if inst == ev["moving_key"] else "passive"
            ox, oy = ev["offsets"][inst]
            depth = ev["depths"][inst]
            if inst == "pipette" and tip_stuck and (role == "passive" or had_tip):
                depth = max(depth, TIP_LEN)
            for seg in segs:
                (ax, ay, az), (bx, by, bz) = seg
                a = (ax + ox, ay + oy, az - depth)
                b = (bx + ox, by + oy, bz - depth)
                vertical = a[:2] == b[:2]
                low, high = min(a[2], b[2]), max(a[2], b[2])
                if not vertical and inst == "pipette":
                    planes.append({"step": ev["step"], "command": ev["command"], "role": role,
                                   "gantry_z": round(az, 3), "tool_z": round(a[2], 3),
                                   "pipette_depth": depth})
                for v in vials:
                    gap = ps.horizontal_distance_to_axis((a, b), v["x"], v["y"])
                    if gap >= v["r"]:
                        continue
                    is_open = v["label"] in open_vials
                    top = v["rim"] if is_open else v["cap_top"]
                    da = math.hypot(a[0] - v["x"], a[1] - v["y"])
                    db = math.hypot(b[0] - v["x"], b[1] - v["y"])
                    at_target = (abs(target[0] + ox - v["x"]) < 1e-6
                                 and abs(target[1] + oy - v["y"]) < 1e-6)
                    if inst == "pipette" and vertical and is_open:
                        kind = "insertion"
                    elif inst != "pipette" and vertical and at_target:
                        kind = "engage"
                    elif (inst == "pipette" and is_open and high < v["rim"]
                          and da < v["r"] and db < v["r"]):
                        kind = "inside"
                    else:
                        kind = "over"
                    rows.append({
                        "step": ev["step"], "command": ev["command"], "instrument": inst,
                        "role": role, "depth": depth, "tip_on": inst == "pipette" and depth > 0.5,
                        "vial": v["label"], "open": is_open, "top": round(top, 3),
                        "rim": v["rim"], "low": round(low, 3), "high": round(high, 3),
                        "clearance": round(low - top, 3), "kind": kind, "gap": round(gap, 2),
                        "max_off_axis": round(max(da, db), 3),
                        "seg": [[round(c, 3) for c in a], [round(c, 3) for c in b]],
                        "axis": "Z" if vertical else ("X" if a[1] == b[1] else "Y"),
                    })
        pose = target
        cmd = (ev["command"] or "").lower()
        if cmd == "decap":
            open_vials |= ps._vials_at(obstacles, target)
        elif cmd == "cap":
            open_vials -= ps._vials_at(obstacles, target)
    return rows, planes


def summarise(rows, planes):
    def best(sel):
        sel = list(sel)
        return min(sel, key=lambda r: r["clearance"]) if sel else None

    over = [r for r in rows if r["kind"] == "over"]
    pip = [r for r in over if r["instrument"] == "pipette"]
    s = {
        "pipette_min": best(pip),
        "pipette_tip_on_min": best(r for r in pip if r["tip_on"]),
        "pipette_moving_min": best(r for r in pip if r["role"] == "moving"),
        "pipette_passive_min": best(r for r in pip if r["role"] == "passive"),
        "pipette_min_by_vial": {v: best(r for r in pip if r["vial"] == v)
                                for v in sorted({r["vial"] for r in rows})},
        "capper_lateral_min": best(r for r in over if r["instrument"] != "pipette"),
    }
    inside = [r for r in rows if r["kind"] == "inside"]
    if inside:
        s["inside"] = {
            "steps": [min(r["step"] for r in inside), max(r["step"] for r in inside)],
            "vial": sorted({r["vial"] for r in inside}),
            "tip_end_z": sorted({r["low"] for r in inside}),
            "tip_end_below_rim_max": round(max(r["rim"] - r["low"] for r in inside), 3),
            "nozzle_below_rim_max": round(max(r["rim"] - (r["low"] + r["depth"]) for r in inside), 3),
            "max_off_axis": max(r["max_off_axis"] for r in inside),
            "wall_clearance_from_axis_at_ID21": round(VIAL_ID / 2 - max(r["max_off_axis"] for r in inside), 3),
        }
    pl = {}
    for p in planes:
        key = (p["gantry_z"], p["pipette_depth"])
        pl.setdefault(key, set()).add(f"{p['step']}:{p['command']}:{p['role']}")
    s["pipette_lateral_planes"] = [
        {"gantry_z": gz, "pipette_depth": d, "tool_z": round(gz - d, 3),
         "steps": _compress(sorted(v, key=lambda t: int(t.split(":")[0])))}
        for (gz, d), v in sorted(pl.items(), key=lambda kv: (-kv[0][0], kv[0][1]))
    ]
    return s


def _compress(tags):
    """'9:move:moving', '10:move:moving', ... -> '9-69:move:moving'."""
    out, run = [], []
    for t in tags + ["-1::"]:
        n, rest = t.split(":", 1)
        if run and rest == run[-1][1] and int(n) == run[-1][0] + 1:
            run.append((int(n), rest))
            continue
        if run:
            a, b = run[0][0], run[-1][0]
            out.append(f"{a}{'-' + str(b) if b != a else ''}:{run[0][1]}")
        run = [(int(n), rest)]
    return out


def fmt(r):
    if r is None:
        return "none (never within a vial radius)"
    return (f"{r['clearance']:+.3f} mm  step {r['step']} {r['command']} ({r['role']} "
            f"{r['instrument']}, tip {'on' if r['tip_on'] else 'off'}) over {r['vial']} "
            f"[{'open' if r['open'] else 'capped'}, top {r['top']}], {r['axis']} move at tool Z "
            f"{r['low']}, {r['gap']} mm from axis; seg {r['seg'][0]} -> {r['seg'][1]}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("gantry")
    ap.add_argument("deck")
    ap.add_argument("protocol")
    ap.add_argument("--cap-height", type=float, default=13.0)
    ap.add_argument("--tip-stuck", action="store_true")
    ap.add_argument("--start-first", action="store_true",
                    help="start from the first target, as passive_shadow does")
    ap.add_argument("--json")
    ap.add_argument("--rows", action="store_true", help="print every 'over' row")
    a = ap.parse_args(argv)

    events, n_diff, _ = record(a.gantry, a.deck, a.protocol)
    obstacles = ps.deck_obstacles(a.deck, a.cap_height)
    rows, planes = analyse(events, obstacles, tip_stuck=a.tip_stuck,
                           start=None if a.start_first else HOMED)
    # cross-check against passive_shadow's own analysis (same start convention)
    ps_find = ps.analyse(events, obstacles, tip_stuck=a.tip_stuck)
    rows_ps, _ = analyse(events, obstacles, tip_stuck=a.tip_stuck, start=None)
    mine = sorted((r["step"], r["vial"]) for r in rows_ps
                  if r["role"] == "passive" and r["kind"] == "over" and r["clearance"] < 0)
    theirs = sorted((f["step"], f["obstacle"]) for f in ps_find if not f["obstacle"].startswith("tip_rack"))
    s = summarise(rows, planes)
    s.update(n_events=len(events), n_travel_z_computed_not_logged=n_diff,
             passive_shadow_vial_findings=len(theirs),
             crosscheck_passive_hits_match=(mine == theirs),
             tip_stuck=a.tip_stuck, cap_height=a.cap_height)
    mode = "tip-stuck" if a.tip_stuck else "nominal"
    print(f"== {a.protocol.rsplit('/', 1)[-1]} | {a.deck.rsplit('/', 1)[-1]} | {mode} | "
          f"{len(events)} poses | travel_z computed-not-logged: {n_diff} | passive_shadow vial "
          f"hits {len(theirs)} (cross-check {'OK' if mine == theirs else 'MISMATCH'})")
    print("  pipette min         :", fmt(s["pipette_min"]))
    print("  pipette moving min  :", fmt(s["pipette_moving_min"]))
    print("  pipette passive min :", fmt(s["pipette_passive_min"]))
    for v, r in s["pipette_min_by_vial"].items():
        print(f"  {v:<8} min        :", fmt(r))
    print("  capper lateral min  :", fmt(s["capper_lateral_min"]))
    if "inside" in s:
        print("  inside (stir)       :", json.dumps(s["inside"]))
    for p in s["pipette_lateral_planes"]:
        print(f"  pipette lateral at gantry Z {p['gantry_z']:>7} depth {p['pipette_depth']:>4} "
              f"-> tool Z {p['tool_z']:>7}  steps {', '.join(p['steps'])}")
    if a.rows:
        for r in rows:
            if r["kind"] == "over" and r["instrument"] == "pipette":
                print("   ", fmt(r))
    if a.json:
        json.dump({"summary": s, "rows": rows}, open(a.json, "w"), indent=1, default=list)
    return s


if __name__ == "__main__":
    main()
