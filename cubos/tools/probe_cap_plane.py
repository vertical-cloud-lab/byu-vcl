"""Measure the capper's true cap-engage plane with the head's own line-break sensor.

Why this exists
---------------
``decap``/``cap`` descend to ``vial.location.z + engage_depth_mm`` and then ask
the line-break sensor whether a cap was captured. Both numbers that determine
where the head actually ends up are unverified on this machine:

* ``vial.location.z`` resolves to 57.0 from ``sterling_deck.yaml``
  (``vial_holder.location.z 39.0 + labware_seat_height_from_bottom 18.0``),
  which disagrees with the measured vial top of ~85 by ~28 mm.
* the capper's ``depth: -25.0`` -- how far the socket face sits ABOVE the
  gantry datum (the pipette nozzle) -- was never measured either. It enters
  the same sum: ``gantry_z = vial_z + engage_depth_mm + depth``.

Because the two errors add, guessing ``engage_depth_mm`` gropes for a plane
whose offset is unknown. This script measures the plane directly instead: it
steps the head down over one vial and polls the line-break sensor, which
breaks when a cap enters the head. The first Z at which the beam breaks IS
the engage plane, whatever ``depth`` really is.

Safety
------
* **Ask the machine's owner before running this.** It is deliberate
  contact-seeking motion, not a validated protocol.
* **It drags the pipette.** The two instruments share one head: with the
  capper at ``offset (0, 0), depth -25`` and the pipette at
  ``offset (+135, +20), depth 0``, commanding the capper's tool point to deck
  ``(x, y, z)`` puts the pipette nozzle at deck ``(x + 135, y + 20, z - 25)``.
  The nozzle is the lowest thing on the head and hangs a third of the bed away
  in +X, so this sweep pulls it down through a plane 25 mm below the capper's
  over whatever sits at deck X ≈ 297. On 2026-08-03 that dragged the nozzle
  along the X rail. ``--floor-gantry-z`` bounds the *capper*; check what the
  nozzle passes through at ``floor_gantry_z`` before starting. Note that a
  normal ``decap``/``cap`` sweeps the same shadow — see
  ``cubos/results/capper_decapper_test_20260803/README.md``.
* Descends in ``--step`` mm increments, sensor-polled at every step, and stops
  the instant the beam breaks.
* ``--floor-gantry-z`` bounds the descent. It defaults to 17.0, the lowest
  gantry Z this machine has already been driven to over a vial (the
  2026-08-03 ``engage_depth_mm: -15.0`` runs) -- so the default sweep stays
  inside territory the machine has already traversed without damage.
* The electromagnet is never energized: this measures geometry only.
* Retracts to ``safe_z`` in a ``finally``, on every exit path.

Usage
-----
    python -m cubos.tools.probe_cap_plane <gantry.yaml> <deck.yaml> <protocol.yaml> \
        --vial vial_holder.vial_2

The protocol YAML is only used to build a validated context; no protocol step
is executed.
"""

from __future__ import annotations

import argparse
import sys

import yaml

from cubos.gantry import Gantry
from cubos.protocol_engine.setup import setup_protocol


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gantry")
    parser.add_argument("deck")
    parser.add_argument("protocol")
    parser.add_argument("--vial", default="vial_holder.vial_2")
    parser.add_argument("--instrument", default="vial_capper_decapper")
    parser.add_argument(
        "--start-gantry-z", type=float, default=70.0,
        help="Gantry Z to begin the descent from (default 70.0).",
    )
    parser.add_argument(
        "--floor-gantry-z", type=float, default=17.0,
        help=(
            "Lowest gantry Z the probe may reach. Default 17.0 -- the lowest "
            "this machine has already been driven to over a vial."
        ),
    )
    parser.add_argument("--step", type=float, default=1.0)
    args = parser.parse_args(argv)

    with open(args.gantry) as handle:
        raw_config = yaml.safe_load(handle)
    gantry = Gantry(config=raw_config)

    _protocol, context = setup_protocol(
        args.gantry, args.deck, args.protocol, gantry=gantry,
    )
    mount = context.gantry
    capper = mount.instruments[args.instrument]
    depth = float(capper.depth)
    coord = context.deck.resolve_coordinate(args.vial)
    x, y, vial_z = coord.x, coord.y, coord.z

    print(f"vial {args.vial}: deck ({x}, {y}, {vial_z})")
    print(f"capper depth={depth} -> gantry_z = deck_z + ({depth})")
    print(f"sweep: gantry Z {args.start_gantry_z} -> {args.floor_gantry_z} "
          f"in {args.step} mm steps, magnet OFF")

    gantry.connect()
    gantry.prepare_for_protocol_run()
    mount.connect_instruments()
    break_gantry_z = None
    try:
        if not gantry.is_healthy():
            print("gantry health check failed; aborting", file=sys.stderr)
            return 2
        gantry.home()

        baseline = capper.read_cap_present()
        print(f"baseline sensor at home: cap_present={baseline}")
        if baseline:
            print(
                "beam is ALREADY broken with the head clear of the deck -- "
                "something is held at the head, or the sensor is stuck. "
                "Aborting before any descent.",
                file=sys.stderr,
            )
            return 3

        mount.move_to_labware(args.instrument, coord)

        gantry_z = args.start_gantry_z
        while gantry_z >= args.floor_gantry_z - 1e-9:
            deck_z = gantry_z - depth
            mount.move(args.instrument, (x, y, deck_z))
            present = capper.read_cap_present()
            print(f"  gantry Z {gantry_z:6.1f}  (capper deck Z {deck_z:6.1f})"
                  f"  cap_present={present}")
            if present:
                break_gantry_z = gantry_z
                break
            gantry_z -= args.step
    finally:
        try:
            mount.move(args.instrument, (x, y, mount.safe_z))
        finally:
            mount.disconnect_instruments()
            gantry.disconnect()

    print()
    if break_gantry_z is None:
        print(
            f"NO BEAM BREAK down to gantry Z {args.floor_gantry_z}. Either the "
            f"slot is empty, the head does not reach the cap within this "
            f"bound, or the sensor does not respond to an unheld cap."
        )
        return 1

    engage_deck_z = break_gantry_z - depth
    print(f"BEAM BROKE at gantry Z {break_gantry_z} "
          f"(capper deck Z {engage_deck_z}).")
    print(f"  engage_depth_mm = {engage_deck_z} - {vial_z} = "
          f"{engage_deck_z - vial_z}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
