#!/usr/bin/env python3
"""Pick the sensor enclosure up from its home slot and read colour at three X positions.

Requested by @timothy-commins on issue #33: *"make the color sensor pick up
the enclosure from well 10, and then place it into 3 different places in the
x direction on well 8. the test will then test the color at each of the 3
places in well 8."*

What it does, in order::

    seated baseline read  ->  pick up from slot 10  ->  grip check
    ->  carry to slot 8                                  x = centre - 30
        descend, settle, read N times                    x = centre
        lift, carry, repeat                              x = centre + 30
    ->  carry back to slot 10  ->  reseat  ->  reseat-confirm read  ->  home

Only X changes between the three read positions. Y and Z are identical at all
three, because the 2026-08-10 session measured that raw counts are dominated
by pose (seated vs lifted changed them ~15x) -- so a scan that varied height
or Y would measure the pose, not the sample.

Where to run it
---------------
On the **OT-2 stream-cam Pi**. It is the only machine that can reach both
ends: the robot answers on the link-local address ``169.254.51.252:31950``
over its direct USB-Ethernet link to that Pi, and the Pi has the internet
access needed for HiveMQ and MongoDB Atlas.

    export MQTT_BROKER=... MQTT_PORT=8883 MQTT_USERNAME=... MQTT_PASSWORD=...
    export PICO_ID=... MONGODB_URI=... MONGODB_DATABASE=digital-wetlab

    python3 run_xscan_test.py --align      # 1. confirm the pickup coordinate
    python3 run_xscan_test.py --dry-run    # 2. sensor + database, no robot motion
    python3 run_xscan_test.py              # 3. the real test

Run ``--align`` first whenever the base has been moved. It homes, hovers the
bare nozzle 30 mm above the computed pickup point, and stops -- so the base
can be slid under the nozzle before anything presses down on it.

Motion recipe
-------------
Coordinates and speeds are the recipe that completed 9 of 9 pick-and-reseat
cycles in July/August 2026 (``../camera/pickup-test-2026-08-10-*``), with the
pickup translated by the OT-2 slot pitch from slot 8 to slot 10. Nothing about
the pickup, press, lift, carry or eject has been re-tuned; only the start slot
and the read positions are new.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck  # noqa: E402
from sensor_read import CHANNELS, SensorError, SensorLink  # noqa: E402

# --- proven motion recipe (do not re-tune without a camera-checked session) --
DESCENT_LADDER = [170.0, 150.0, 120.0, 105.0, 101.0, 99.0]
ENTRY_Z, ENTRY_SPEED = 95.0, 5.0          # straight entry into the socket mouth
PRESS_Z, PRESS_SPEED = 90.5, 5.0          # deep press; >=7 mm engagement so eject works
LIFT_Z, LIFT_DWELL_S = 110.0, 4.0         # grip check height + slip dwell
HIGH_LIFT = [130.0, 150.0, 170.0]
HIGH_LIFT_SPEED = 15.0
CARRY_Z = 170.0                           # travel height with the module aboard
CARRY_SEGMENT_MM, CARRY_SPEED = 8.5, 10.0  # segmented carry, proven not to shed the module
DROP_DX = -6.0                            # anti-tilt offset applied to the drop-off X only
DROP_DESCENT = [130.0, 110.0, 108.0, 101.0, 95.5]
CLEAR_Z = 128.0                           # straight-up retreat after release
DESCENT_SPEED = 10.0

# --- test layout defaults ---------------------------------------------------
HOME_SLOT = 10                 # where the enclosure's base stands ("well 10")
SCAN_SLOT = 8                  # where the three readings are taken ("well 8")
BASE_DX, BASE_DY = 36.55, 44.0  # socket position within its slot, from PR #60
SCAN_DX = (-30.0, 0.0, 30.0)   # X offsets from the scan slot's centre
SCAN_DY = 44.0                 # same within-slot Y as the base, = y 225.0 in slot 8
READ_Z = 120.0                 # nozzle Z at every read -> aperture ~29.5 mm off the deck
SETTLE_S = 1.5                 # pause after arriving, before the first read
READS_PER_POSITION = 3
GRIP_RATIO = 2.0               # lifted total counts must exceed seated x this

PIPETTE = {"pipetteName": "p300_single_gen2", "mount": "left"}
DEFAULT_ROBOT_IP = "169.254.51.252"
HEADERS = {"Opentrons-Version": "3"}
MONGO_COLLECTION = "sensor-data"


def utcnow():
    return datetime.now(timezone.utc)


def stamp():
    return utcnow().strftime("%H:%M:%S")


def log(msg):
    print(f"[{stamp()}] {msg}", flush=True)


class Robot:
    """Thin wrapper over the OT-2 maintenance-run API.

    Maintenance runs are used rather than an uploaded protocol because the
    colour reads happen between moves, from this host -- the robot itself is
    on a link-local network with no route to the broker, so it cannot take
    the readings itself.
    """

    def __init__(self, ip, simulate=False):
        self.base = f"http://{ip}:31950"
        self.simulate = simulate
        self.run_id = None
        self.pipette_id = None
        self.moves = []
        self._sim_pos = None   # simulate mode tracks its own nozzle position

    def health(self):
        if self.simulate:
            return {"name": "simulated", "robot_model": "OT-2 Standard", "api_version": "-"}
        r = requests.get(f"{self.base}/health", headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()

    def command(self, command_type, params, timeout=120):
        if self.simulate:
            return {}
        r = requests.post(
            f"{self.base}/maintenance_runs/{self.run_id}/commands",
            headers={**HEADERS, "Content-Type": "application/json"},
            params={"waitUntilComplete": "true"},
            json={"data": {"commandType": command_type, "params": params}},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()["data"]
        if data["status"] != "succeeded":
            raise RuntimeError(f"{command_type} failed: {data.get('error')}")
        return data.get("result") or {}

    def open(self):
        if self.simulate:
            self.run_id, self.pipette_id = "simulated-run", "simulated-pipette"
            return
        r = requests.post(f"{self.base}/maintenance_runs", headers=HEADERS,
                          json={"data": {}}, timeout=10)
        r.raise_for_status()
        self.run_id = r.json()["data"]["id"]
        log(f"maintenance run {self.run_id}")
        self.pipette_id = self.command("loadPipette", PIPETTE)["pipetteId"]

    def close(self):
        if self.simulate or self.run_id is None:
            return
        try:
            requests.delete(f"{self.base}/maintenance_runs/{self.run_id}",
                            headers=HEADERS, timeout=10)
            log("maintenance run deleted")
        except requests.RequestException as exc:
            log(f"WARNING: could not delete the maintenance run: {exc}")

    # -- motion ------------------------------------------------------------
    def home(self):
        log("homing")
        self.command("home", {}, timeout=180)

    def position(self):
        if self.simulate:
            return self._sim_pos
        return self.command("savePosition", {"pipetteId": self.pipette_id})["position"]

    def move(self, x, y, z, speed):
        self.command("moveToCoordinates", {
            "pipetteId": self.pipette_id,
            "coordinates": {"x": x, "y": y, "z": z},
            "speed": speed,
            "forceDirect": True,
        })
        self.moves.append({"x": round(x, 2), "y": round(y, 2), "z": round(z, 2),
                           "speed": speed})
        self._sim_pos = {"x": x, "y": y, "z": z}
        log(f"  at ({x:7.2f}, {y:7.2f}, {z:6.2f})  {speed:g} mm/s")

    def carry_to(self, x, y, z, speed=CARRY_SPEED, segment=CARRY_SEGMENT_MM):
        """Move laterally in short segments -- the module sheds on long fast moves."""
        here = self.position()
        x0 = here["x"] if here else x
        y0 = here["y"] if here else y
        span = max(abs(x - x0), abs(y - y0))
        steps = max(1, int(span / segment + 0.999))
        for i in range(1, steps + 1):
            self.move(x0 + (x - x0) * i / steps, y0 + (y - y0) * i / steps, z, speed)

    def drop_tip_in_place(self):
        log("  releasing (dropTipInPlace)")
        self.command("dropTipInPlace", {"pipetteId": self.pipette_id})


def high_lift_stages(carry_z):
    """Staged climb from the lift-test height to the carry height.

    The module has come off the nozzle during a single long Z move before
    (2026-07-31, wire attached), so the climb is broken into rungs.
    """
    return [z for z in HIGH_LIFT if z < carry_z] + [carry_z]


def summarise(reading):
    ch = reading["channels"]
    body = "  ".join(f"{c[2:]}={ch[c]:>5}" for c in CHANNELS)
    return f"{body}  total={reading['total']:>6}"


def take_reads(link, label, n, rgb, records, position):
    out = []
    for i in range(1, n + 1):
        reading = link.read(label=f"{label}-{i}", rgb=rgb)
        reading["position"] = position
        reading["stage"] = label
        records.append(reading)
        out.append(reading)
        log(f"  read {i}/{n}  {summarise(reading)}")
    return out


def mean_total(readings):
    return sum(r["total"] for r in readings) / float(len(readings))


def store_in_mongodb(records, run_meta, uri, database):
    from pymongo import MongoClient

    client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    try:
        client.admin.command("ping")
        docs = []
        for r in records:
            docs.append({
                "timestamp": utcnow(),
                "source": "ot2-xscan-test",
                "run": run_meta,
                "stage": r["stage"],
                "position": r.get("position"),
                "experiment_id": r["experiment_id"],
                "command": r["command"],
                "channels": r["channels"],
                "total": r["total"],
                "latency_s": r["latency_s"],
            })
        result = client[database][MONGO_COLLECTION].insert_many(docs)
        log(f"stored {len(result.inserted_ids)} document(s) in {database}.{MONGO_COLLECTION}")
        return [str(i) for i in result.inserted_ids]
    finally:
        client.close()


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--robot-ip", default=os.environ.get("OT2_IP", DEFAULT_ROBOT_IP))
    p.add_argument("--home-slot", type=int, default=HOME_SLOT,
                   help="slot the enclosure's base stands in (default: %(default)s)")
    p.add_argument("--scan-slot", type=int, default=SCAN_SLOT,
                   help="slot the three readings are taken over (default: %(default)s)")
    p.add_argument("--base-dx", type=float, default=BASE_DX)
    p.add_argument("--base-dy", type=float, default=BASE_DY)
    p.add_argument("--scan-dx", default=",".join(str(v) for v in SCAN_DX),
                   help="comma-separated X offsets from the scan slot centre")
    p.add_argument("--scan-dy", type=float, default=SCAN_DY)
    p.add_argument("--carry-z", type=float, default=CARRY_Z,
                   help="travel height with the module aboard (default: %(default)s)")
    p.add_argument("--read-z", type=float, default=READ_Z,
                   help="nozzle Z at each read; aperture sits ~%(default)s-90.5 mm off the deck")
    p.add_argument("--reads", type=int, default=READS_PER_POSITION)
    p.add_argument("--rgb", default="0,0,0", help="R,Y,B sent with each read command")
    p.add_argument("--settle", type=float, default=SETTLE_S)
    p.add_argument("--grip-ratio", type=float, default=GRIP_RATIO)
    p.add_argument("--align", action="store_true",
                   help="home, hover 30 mm above the pickup point, and stop")
    p.add_argument("--dry-run", action="store_true",
                   help="exercise the sensor and database only; the robot never moves")
    p.add_argument("--simulate", action="store_true",
                   help="print the motion plan without a robot or a sensor")
    p.add_argument("--no-mongo", action="store_true")
    p.add_argument("--skip-grip-check", action="store_true",
                   help="do not abort when the lifted counts fail to rise")
    p.add_argument("--out", default=None, help="write the full result JSON here")
    return p.parse_args(argv)


def build_plan(args):
    """Resolve the deck geometry and fail loudly on anything off-slot."""
    pickup_x, pickup_y = deck.in_slot(args.home_slot, args.base_dx, args.base_dy)
    scan_cx, _ = deck.slot_center(args.scan_slot)
    scan_ox, scan_oy = deck.slot_origin(args.scan_slot)
    scan_y = scan_oy + args.scan_dy
    offsets = [float(v) for v in args.scan_dx.split(",") if v.strip()]
    positions = [{"index": i + 1, "dx": dx, "x": round(scan_cx + dx, 2),
                  "y": round(scan_y, 2), "z": args.read_z}
                 for i, dx in enumerate(offsets)]

    margin = deck.slot_margin(args.home_slot, pickup_x, pickup_y)
    if margin < 0:
        raise SystemExit(
            f"pickup ({pickup_x:.2f}, {pickup_y:.2f}) is outside slot {args.home_slot}"
        )
    for pos in positions:
        m = deck.slot_margin(args.scan_slot, pos["x"], pos["y"])
        if m < 0:
            raise SystemExit(
                f"read position {pos['index']} ({pos['x']}, {pos['y']}) is "
                f"{-m:.1f} mm outside slot {args.scan_slot} -- narrow --scan-dx"
            )
        pos["slot_margin_mm"] = round(m, 2)
    if args.read_z <= PRESS_Z:
        raise SystemExit(
            f"--read-z {args.read_z} is at or below the press depth {PRESS_Z}; "
            "the module's foot would be driven into the deck"
        )
    return {
        "pickup": {"x": round(pickup_x, 2), "y": round(pickup_y, 2),
                   "slot": args.home_slot, "slot_margin_mm": round(margin, 2)},
        "drop_off": {"x": round(pickup_x + DROP_DX, 2), "y": round(pickup_y, 2)},
        "positions": positions,
        "aperture_height_mm": round(args.read_z - PRESS_Z, 2),
    }


def print_plan(plan, args):
    print("\n  deck plan")
    print(f"    pick up from slot {args.home_slot} at "
          f"({plan['pickup']['x']}, {plan['pickup']['y']})  "
          f"[{plan['pickup']['slot_margin_mm']} mm inside the slot]")
    for pos in plan["positions"]:
        print(f"    read {pos['index']}: x={pos['x']:>7.2f}  y={pos['y']:.2f}  "
              f"z={pos['z']:.1f}   dx={pos['dx']:+.1f} mm from the slot "
              f"{args.scan_slot} centre  [{pos['slot_margin_mm']} mm inside]")
    print(f"    aperture sits ~{plan['aperture_height_mm']} mm above the deck at each read")
    print(f"    reseat at ({plan['drop_off']['x']}, {plan['drop_off']['y']}) "
          f"-- {abs(DROP_DX):g} mm anti-tilt offset\n")


def pick_up(robot, plan):
    x, y = plan["pickup"]["x"], plan["pickup"]["y"]
    log(f"descent ladder over the socket at ({x}, {y})")
    for z in DESCENT_LADDER:
        robot.move(x, y, z, speed=DESCENT_SPEED if z <= 105 else 25.0)
    log("straight entry")
    robot.move(x, y, ENTRY_Z, speed=ENTRY_SPEED)
    log("press")
    robot.move(x, y, PRESS_Z, speed=PRESS_SPEED)
    log(f"lift test to z={LIFT_Z} + {LIFT_DWELL_S:g} s dwell")
    robot.move(x, y, LIFT_Z, speed=DESCENT_SPEED)
    time.sleep(LIFT_DWELL_S)


def reseat(robot, plan, carry_z=CARRY_Z):
    x, y = plan["drop_off"]["x"], plan["drop_off"]["y"]
    log(f"returning to the drop-off column x={x}")
    robot.carry_to(x, y, carry_z)
    log("staged descent")
    for z in [z for z in DROP_DESCENT if z < carry_z]:
        robot.move(x, y, z, speed=DESCENT_SPEED)
        time.sleep(0.4)
    robot.drop_tip_in_place()
    robot.move(x, y, CLEAR_Z, speed=20.0)


def main(argv=None):
    args = parse_args(argv)
    rgb = tuple(int(v) for v in args.rgb.split(","))
    plan = build_plan(args)
    started = utcnow()
    records = []

    print(f"\n=== OT-2 colour X-scan: slot {args.home_slot} -> slot {args.scan_slot} "
          f"({len(plan['positions'])} positions x {args.reads} reads) ===")
    print_plan(plan, args)

    if args.simulate:
        robot = Robot(args.robot_ip, simulate=True)
        robot.open()
        pick_up(robot, plan)
        for z in high_lift_stages(args.carry_z):
            robot.move(plan["pickup"]["x"], plan["pickup"]["y"], z, HIGH_LIFT_SPEED)
        for pos in plan["positions"]:
            robot.carry_to(pos["x"], pos["y"], args.carry_z)
            robot.move(pos["x"], pos["y"], pos["z"], DESCENT_SPEED)
            robot.move(pos["x"], pos["y"], args.carry_z, DESCENT_SPEED)
        reseat(robot, plan, args.carry_z)
        print(f"\n  {len(robot.moves)} moves planned, no hardware touched.")
        return 0

    # -- preflight ---------------------------------------------------------
    log("preflight: sensor link")
    link = SensorLink().connect()
    link.check_delivery()
    log("  broker delivers to us: PASS")

    mongo_uri = None if args.no_mongo else os.environ.get("MONGODB_URI")
    database = os.environ.get("MONGODB_DATABASE", "digital-wetlab")

    try:
        log("seated baseline read (module on its base)")
        seated = take_reads(link, "seated-baseline", max(2, args.reads // 2), rgb,
                            records, None)
        seated_total = mean_total(seated)

        if args.dry_run:
            log("--dry-run: stopping before any robot motion")
        else:
            robot = Robot(args.robot_ip)
            health = robot.health()
            log(f"robot: {health['name']} ({health.get('robot_model')})")
            robot.open()
            try:
                robot.home()
                if args.align:
                    x, y = plan["pickup"]["x"], plan["pickup"]["y"]
                    robot.move(x, y, PRESS_Z + 30.0, speed=40.0)
                    print(f"\n  ALIGN: the bare nozzle is hovering 30 mm above "
                          f"({x}, {y}).\n  Slide the base so the socket is centred "
                          f"directly under it, then re-run without --align.\n")
                    return 0

                pick_up(robot, plan)
                log("grip check via the sensor itself")
                lifted = take_reads(link, "grip-check", 2, rgb, records,
                                    {"x": plan["pickup"]["x"], "y": plan["pickup"]["y"],
                                     "z": LIFT_Z})
                ratio = mean_total(lifted) / max(seated_total, 1.0)
                log(f"  seated {seated_total:.0f} -> lifted {mean_total(lifted):.0f} "
                    f"= {ratio:.1f}x")
                if ratio < args.grip_ratio and not args.skip_grip_check:
                    raise RuntimeError(
                        f"grip check FAILED: lifting raised the counts only {ratio:.1f}x "
                        f"(expected >= {args.grip_ratio}x). The module is probably still "
                        "on its base and the nozzle came up empty -- aborting before the "
                        "carry so nothing is dropped."
                    )
                log("  grip confirmed")

                log("high lift to carry height")
                for z in high_lift_stages(args.carry_z):
                    robot.move(plan["pickup"]["x"], plan["pickup"]["y"], z,
                               HIGH_LIFT_SPEED)

                for pos in plan["positions"]:
                    label = f"pos{pos['index']}-dx{pos['dx']:+g}"
                    log(f"--- position {pos['index']} of {len(plan['positions'])}: "
                        f"x={pos['x']} (dx {pos['dx']:+g} mm) ---")
                    robot.carry_to(pos["x"], pos["y"], args.carry_z)
                    robot.move(pos["x"], pos["y"], pos["z"], speed=DESCENT_SPEED)
                    time.sleep(args.settle)
                    take_reads(link, label, args.reads, rgb, records, pos)
                    robot.move(pos["x"], pos["y"], args.carry_z, speed=DESCENT_SPEED)

                reseat(robot, plan, args.carry_z)
                robot.home()
            except Exception:
                log("ERROR during the run -- attempting to reseat before exiting")
                try:
                    reseat(robot, plan, args.carry_z)
                    robot.home()
                except Exception as exc:  # noqa: BLE001 - report, do not mask
                    log(f"reseat also failed ({exc}); the module may still be on the "
                        "nozzle. Run cad/recover_reseat.py once you have looked inside.")
                raise
            finally:
                robot.close()

            log("reseat confirmation read (counts should fall back to the seated level)")
            after = take_reads(link, "reseat-confirm", 2, rgb, records, None)
            log(f"  seated {seated_total:.0f} -> after reseat {mean_total(after):.0f}")
    finally:
        link.close()

    # -- report ------------------------------------------------------------
    run_meta = {
        "started": started.isoformat(),
        "home_slot": args.home_slot,
        "scan_slot": args.scan_slot,
        "plan": plan,
        "rgb": {"R": rgb[0], "Y": rgb[1], "B": rgb[2]},
        "reads_per_position": args.reads,
        "dry_run": bool(args.dry_run),
    }

    print("\n  results by position")
    header = "  " + "".join(f"{c[2:]:>7}" for c in CHANNELS) + f"{'total':>9}"
    print(header)
    for pos in plan["positions"]:
        rows = [r for r in records
                if isinstance(r.get("position"), dict)
                and r["position"].get("index") == pos["index"]]
        if not rows:
            continue
        means = {c: sum(r["channels"][c] for r in rows) / len(rows) for c in CHANNELS}
        line = "  " + "".join(f"{means[c]:>7.0f}" for c in CHANNELS)
        print(f"{line}{mean_total(rows):>9.0f}   x={pos['x']} (dx {pos['dx']:+g})")

    if mongo_uri and not args.no_mongo:
        try:
            run_meta["mongodb_ids"] = store_in_mongodb(records, run_meta, mongo_uri,
                                                       database)
        except Exception as exc:  # noqa: BLE001 - the readings still matter
            log(f"WARNING: MongoDB write failed ({exc}); the JSON below still has "
                "every reading")
    elif not args.no_mongo:
        log("MONGODB_URI is not set; skipping the database write")

    payload = {"run": run_meta, "readings": records}
    out = args.out or f"xscan-{started.strftime('%Y%m%dT%H%M%SZ')}.json"
    with open(out, "w") as fh:
        json.dump(payload, fh, indent=2, default=str)
    log(f"wrote {out}  ({len(records)} readings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
