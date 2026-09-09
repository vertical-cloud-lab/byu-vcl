#!/usr/bin/env python3
"""Sweep the PASSIVE instrument through a protocol and report interferences.

CubOS's offline gates -- ``validate_setup`` and ``run_protocol --mock`` --
only ever check the instrument a command names. On a head that carries two
rigidly-coupled tools (the CubXL's capper + pipette) the *other* tool is
dragged through the deck on every move, and nothing upstream models it.
That blind spot has produced every near-miss on this machine so far: the
2026-08-03 X-rail drag, and the 2026-08-28 finding that ``cap vial_1``
shears an attached tip sideways out of the vial it is still inside.

This tool closes it. It mock-runs the protocol, records every commanded
gantry pose, expands each pose into the driver's real axis-by-axis
G-code segments (``gantry_driver/driver.py::_build_direct_move`` /
``_build_transit_move`` -- X, then Y, then Z; the mill never interpolates
a diagonal), then sweeps the passive instrument's tool point along each
segment and tests it against the deck's vials and tip racks.

Usage:
    python -m cubos.tools.passive_shadow GANTRY DECK PROTOCOL [options]

      --cap-height MM    height of a seated cap above the vial rim.
                         Default 13.0 = the capper's engage_depth_mm, which
                         is where the socket meets the cap.
      --tip-stuck        additionally model the case where a `drop_tip`
                         reported success but the tip is physically still
                         on the nozzle. `drop_tip` clears the modeled tip
                         extension unconditionally, so from that point on
                         CubOS plans in the bare-nozzle frame -- 35 mm
                         higher than reality.

Exit status is 1 when any interference is found, so it can gate a run.

NOTE this models *labware from the deck file only*. Vial holders, racks,
brackets, cabling and the machine's own structures are not in the deck
file and are not modeled here. A clean report is necessary, not
sufficient -- still eyeball the swept strips it prints.
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import math
import sys
from typing import Any

Seg = tuple[tuple[float, float, float], tuple[float, float, float]]


def axis_segments(
    start: tuple[float, float, float],
    target: tuple[float, float, float],
    travel_z: float | None,
) -> list[Seg]:
    """Expand one commanded pose into the driver's per-axis G-code moves.

    Mirrors ``_build_direct_move`` (X, Y, Z) and ``_build_transit_move``
    (lift to travel_z, X, Y, descend). Each axis is a separate G01, so a
    "move" is an L-shaped path, not a straight line to the target.
    """
    cx, cy, cz = start
    tx, ty, tz = target
    out: list[Seg] = []
    if travel_z is not None and cz != travel_z:
        out.append(((cx, cy, cz), (cx, cy, travel_z)))
        cz = travel_z
    if tx != cx:
        out.append(((cx, cy, cz), (tx, cy, cz)))
        cx = tx
    if ty != cy:
        out.append(((cx, cy, cz), (cx, ty, cz)))
        cy = ty
    if tz != cz:
        out.append(((cx, cy, cz), (cx, cy, tz)))
    return out


def horizontal_distance_to_axis(seg: Seg, cx: float, cy: float) -> float:
    """Closest approach of *seg* (in plan view) to the vertical line at (cx, cy)."""
    (ax, ay, _), (bx, by, _) = seg
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(ax - cx, ay - cy)
    t = max(0.0, min(1.0, ((cx - ax) * dx + (cy - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(ax + t * dx - cx, ay + t * dy - cy)


def record_moves(gantry_yaml: str, deck_yaml: str, protocol_yaml: str) -> list[dict]:
    """Mock-run the protocol, returning one record per commanded gantry pose."""
    import cubos.gantry.instrument_mount as instrument_mount

    events: list[dict] = []
    step = [-1, ""]
    original_move = instrument_mount.InstrumentedGantry.move

    def traced(self, instrument, position, travel_z=None):
        instr = self._resolve_instrument(instrument)
        x, y, z = self._resolve_position(position)
        depth = instr.effective_depth
        moving_key = next(
            (k for k, v in self.instruments.items() if v is instr), None
        )
        events.append(
            {
                "instrument": instr.name,
                "moving_key": moving_key,
                "gantry": [x - instr.offset_x, y - instr.offset_y, z + depth],
                "travel_z": (travel_z + depth) if travel_z is not None else None,
                "depths": {n: i.effective_depth for n, i in self.instruments.items()},
                "offsets": {n: [i.offset_x, i.offset_y] for n, i in self.instruments.items()},
                "step": step[0],
                "command": step[1],
            }
        )
        return original_move(self, instrument, position, travel_z)

    class StepTagger(logging.Handler):
        def emit(self, record):
            if record.msg == "Step %d: %s(%s)":
                step[0], step[1] = record.args[0], record.args[1]

    instrument_mount.InstrumentedGantry.move = traced
    logging.getLogger().addHandler(StepTagger())
    logging.getLogger().setLevel(logging.INFO)
    try:
        from cubos.tools import run_protocol

        argv, stdout = sys.argv, sys.stdout
        sys.argv = ["run_protocol", "--mock", gantry_yaml, deck_yaml, protocol_yaml]
        sys.stdout = io.StringIO()
        try:
            run_protocol.main()
        except SystemExit:
            pass
        finally:
            sys.argv, sys.stdout = argv, stdout
    finally:
        instrument_mount.InstrumentedGantry.move = original_move
    return events


def deck_obstacles(deck_yaml: str, cap_height: float) -> list[dict]:
    """Vial and tip-rack obstacles as (x, y, radius, top_z, label, kind)."""
    import yaml

    obstacles = []
    labware = (yaml.safe_load(open(deck_yaml)) or {}).get("labware", {}) or {}
    for key, entry in labware.items():
        if not isinstance(entry, dict):
            continue
        kind = entry.get("type")
        location = entry.get("location") or {}
        if kind == "vial":
            obstacles.append(
                {
                    "x": float(location["x"]),
                    "y": float(location["y"]),
                    "r": float(entry.get("diameter", 28.0)) / 2.0,
                    "rim": float(location["z"]),
                    "cap_top": float(location["z"]) + cap_height,
                    "label": key,
                    "kind": "vial",
                }
            )
        elif kind == "tip_rack":
            calibration = entry.get("calibration") or {}
            a1 = calibration.get("a1") or location
            a2 = calibration.get("a2") or {}
            x1 = float(a1["x"])
            y1 = float(a1["y"])
            x2 = float(a2.get("x", x1 - float(entry.get("x_offset", 8.5))))
            pitch_y = float(entry.get("y_offset", 8.5))
            top = float(entry.get("pickup_z", a1.get("z", 0.0)))
            for column, x in enumerate([x1, x2]):
                for row in range(int(entry.get("rows", 1))):
                    obstacles.append(
                        {
                            "x": x,
                            "y": y1 + pitch_y * row,
                            "r": 4.0,
                            "rim": top,
                            "cap_top": top,
                            "label": f"{key}.{chr(ord('A') + row)}{column + 1}",
                            "kind": "tip",
                        }
                    )
    return obstacles


def analyse(events, obstacles, *, tip_stuck: bool) -> list[dict]:
    open_vials: set[str] = set()
    findings = []
    pose = None
    for event in events:
        target = tuple(event["gantry"])
        if pose is None:
            pose = target
        moving = event["instrument"]
        # The passive instruments are every mounted tool this move does not
        # name -- resolved by identity when the trace was taken, so it does
        # not depend on class names matching config keys.
        for passive in [k for k in event["offsets"] if k != event["moving_key"]]:
            _sweep(event, pose, passive, obstacles, open_vials, findings,
                   tip_stuck=tip_stuck, moving=moving)
        pose = target
        command = (event["command"] or "").lower()
        if command == "decap":
            open_vials |= _vials_at(obstacles, target)
        elif command == "cap":
            open_vials -= _vials_at(obstacles, target)
    return findings


def _vials_at(obstacles, pose) -> set:
    return {o["label"] for o in obstacles if o["kind"] == "vial"
            and abs(o["x"] - pose[0]) < 1e-6 and abs(o["y"] - pose[1]) < 1e-6}


def _sweep(event, pose, passive, obstacles, open_vials, findings, *, tip_stuck, moving):
    offset_x, offset_y = event["offsets"][passive]
    depth = event["depths"][passive]
    if tip_stuck and passive == "pipette":
        depth = max(depth, 35.0)

    target = tuple(event["gantry"])
    for seg in axis_segments(pose, target, event["travel_z"]):
        (ax, ay, az), (bx, by, bz) = seg
        tool = (
            (ax + offset_x, ay + offset_y, az - depth),
            (bx + offset_x, by + offset_y, bz - depth),
        )
        vertical = tool[0][:2] == tool[1][:2]
        low = min(tool[0][2], tool[1][2])
        for obstacle in obstacles:
            gap = horizontal_distance_to_axis(tool, obstacle["x"], obstacle["y"])
            if gap >= obstacle["r"]:
                continue
            top = obstacle["rim"] if obstacle["label"] in open_vials else obstacle["cap_top"]
            if low >= top:
                continue
            # A purely vertical move down the axis of an OPEN vial is the
            # intended insertion, not an interference.
            if vertical and obstacle["label"] in open_vials:
                continue
            findings.append(
                {
                    "step": event["step"],
                    "command": event["command"],
                    "moving": moving,
                    "passive": passive,
                    "obstacle": obstacle["label"],
                    "gap_mm": round(gap, 2),
                    "tool_low_z": round(low, 3),
                    "obstacle_top_z": round(top, 3),
                    "tip_attached": depth > 0.5,
                    "segment": [tuple(round(v, 2) for v in tool[0]),
                                tuple(round(v, 2) for v in tool[1])],
                }
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("gantry")
    parser.add_argument("deck")
    parser.add_argument("protocol")
    parser.add_argument("--cap-height", type=float, default=13.0)
    parser.add_argument("--tip-stuck", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    logging.getLogger().setLevel(logging.CRITICAL)
    events = record_moves(args.gantry, args.deck, args.protocol)
    obstacles = deck_obstacles(args.deck, args.cap_height)
    findings = analyse(events, obstacles, tip_stuck=args.tip_stuck)

    if args.json:
        json.dump(findings, sys.stdout, indent=2)
        return 1 if findings else 0

    mode = "tip stuck on nozzle" if args.tip_stuck else "nominal"
    print(f"passive-instrument sweep [{mode}]: {len(events)} commanded poses, "
          f"{len(obstacles)} deck obstacles")
    if not findings:
        print("\nNo interference. (Deck labware only -- holders, brackets and "
              "cabling are not in the deck file and are not modeled.)")
        return 0
    print(f"\n{len(findings)} INTERFERENCE(S):\n")
    for f in findings:
        print(f"  step {f['step']:>2} {f['command']:<9} moving={f['moving']:<16} "
              f"passive={f['passive']} (tip={'on' if f['tip_attached'] else 'off'})")
        print(f"       -> {f['obstacle']}: {f['gap_mm']} mm from its axis, tool point "
              f"down to Z {f['tool_low_z']} vs obstacle top {f['obstacle_top_z']}")
        print(f"       {f['segment'][0]} -> {f['segment'][1]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
