#!/usr/bin/env python3
"""Pick up one 300 uL tip, take it into a well of the 96-well plate, put it back.

Asked on PR #202 (2026-09-29): "calibration test for the pipette plastic
tips" -- can the P300 pick up a tip from the 300 uL rack and place liquid in
the plate. There is no liquid on the deck, so the liquid step is the same
motion with air: aspirate above the plate, lower the tip into the well,
dispense and blow out there.

First run, 2026-09-29 19:03-19:09 MDT: the pick-up at the nominal position
worked first time, the tip went 8 mm into plate well A1 and back into its rack
position (``results-tip-pickup-2026-09-29.md``). The rack is in slot 6.

The robot has **no calibration for this pipette** (no tip length, no pipette
offset; ``calibration-state-2026-09-11.json``), and its deck calibration
predates the lab move. So nothing here trusts the nominal positions blindly:
the bare nozzle hovers over the tip first and is photographed, and the tip is
lowered into the well a step at a time.

Runs ON the Pi that holds the robot link, under nohup, one step at a time
through a command file, like ``enclosure_height_cal.py``: write one line to
``cmd`` in the working directory (``echo 'hover 0 0 10' > cmd.tmp && mv
cmd.tmp cmd``). Silence for --timeout seconds means "stop": a tip on the
nozzle is put back where it came from and the gantry is homed.

    hover <dx> <dy> <h>   bare nozzle over the tip at <well> + (dx, dy), h mm
                          above the tip tops (h >= 1). Travels at TRAVEL_Z.
    pickup [dz]           Opentrons' own pick-up (a 17 mm press at 0.125 A,
                          which stalls harmlessly on a misaligned tip, then a
                          Z re-home), from the last hover's (dx, dy)
    well <name> <h>       tip over plate well <name>, tip end h mm above the
                          well's top rim; descends at most 5 mm per step, and
                          never below 1 mm over the well's floor
    air <uL>              aspirate air, only with the tip above the plate
    dispense              dispense everything and blow out, in place
    up                    tip straight up to the travel height
    photo                 photograph again without moving
    return                put the tip back in its own rack position, home
    home | quit           (empty nozzle only)

``--simulate`` runs the command flow with no robot and no camera.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deck  # noqa: E402
from run_xscan_test import HEADERS, Robot, robot_lights  # noqa: E402

ROBOT_IP = "169.254.51.252"
FFMPEG = os.path.expanduser("~/ytframes/bin/ffmpeg")
CMD = os.path.join(HERE, "cmd")
STATE = os.path.join(HERE, "state.json")
LOGFILE = os.path.join(HERE, "log.txt")

# opentrons_96_tiprack_300ul/1 and corning_96_wellplate_360ul_flat/1, from
# opentrons-shared-data 8.8.1. Well x/y are from the labware's front-left
# corner; "top" is the tip's top rim / the well's rim above the deck.
RACK = {"loadName": "opentrons_96_tiprack_300ul", "namespace": "opentrons", "version": 1}
PLATE = {"loadName": "corning_96_wellplate_360ul_flat", "namespace": "opentrons", "version": 1}
RACK_TOP_Z = 5.39 + 59.3            # 64.69: the tips' top rims
TIP_LENGTH = 59.3 - 8.2             # 51.1 below the nozzle once on (8.2 mm overlap)
PLATE_TOP_Z = 3.55 + 10.67          # 14.22
PLATE_FLOOR_Z = 3.55
PITCH = 9.0

# Travel heights. The enclosure is lying on the deck in front of the base in
# slot 10 (back of slot 7) and the base's tower stands ~100 mm tall, so every
# lateral move is made at or above these.
TRAVEL_Z_BARE = 150.0               # nozzle
TRAVEL_Z_TIP = 110.0                # tip end (nozzle ~161)
TRAVEL_SPEED = 60.0
DESCENT_SPEED = 10.0
FINE_SPEED = 5.0
WELL_STEP = 5.0                     # at most this per `well` step, downwards
FLOW = 46.43                        # uL/s, the P300 GEN2's default at apiLevel 2.0-2.5


def well_xy(slot, name):
    """Nominal deck (x, y) of well <name> in a standard 96 layout in <slot>."""
    row = "ABCDEFGH".index(name[0].upper())
    col = int(name[1:]) - 1
    if not (0 <= row < 8 and 0 <= col < 12):
        raise ValueError(f"no well {name}")
    return deck.in_slot(slot, 14.38 + PITCH * col, 74.24 - PITCH * row)


class TipCal:
    def __init__(self, args):
        self.args = args
        self.robot = Robot(ROBOT_IP, simulate=args.simulate)
        self.seq = 0
        self.phase = "start"
        self.tip = False
        self.pos = None
        self.rack_id = None
        self.plate_id = None
        self.offset = [0.0, 0.0]         # last hover's (dx, dy) from the nominal tip
        self.aspirated = 0.0
        self.history = []
        self.last_note = ""
        self.lights_before = None

    # -- bookkeeping ---------------------------------------------------------
    def log(self, msg):
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        with open(LOGFILE, "a") as fh:
            fh.write(line + "\n")

    def save_state(self, waiting=None):
        state = {"updated_local": datetime.now().strftime("%H:%M:%S"),
                 "phase": self.phase, "tip": self.tip, "pos": self.pos,
                 "rack_slot": self.args.rack_slot, "well": self.args.well,
                 "offset": self.offset, "aspirated": self.aspirated,
                 "seq": self.seq, "waiting_for": waiting, "note": self.last_note,
                 "history": self.history[-60:]}
        with open(STATE + ".tmp", "w") as fh:
            json.dump(state, fh, indent=1)
        os.replace(STATE + ".tmp", STATE)

    def photo(self, label):
        self.seq += 1
        base = os.path.join(HERE, f"{self.seq:02d}_{label}")
        out = {"seq": self.seq, "label": label, "pos": self.pos, "tip": self.tip,
               "t_local": datetime.now().strftime("%H:%M:%S")}
        if not self.args.simulate:
            try:
                time.sleep(0.8)
                r = requests.post(f"http://{ROBOT_IP}:31950/camera/picture",
                                  headers=HEADERS, timeout=30)
                r.raise_for_status()
                with open(base + "_raw.jpg", "wb") as fh:
                    fh.write(r.content)
                # The camera is mounted inverted; turn the frame upright.
                subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-i", base + "_raw.jpg",
                                "-vf", "hflip,vflip", "-q:v", "3", base + ".jpg"], check=True)
                os.remove(base + "_raw.jpg")
                out["file"] = os.path.basename(base + ".jpg")
            except Exception as exc:  # noqa: BLE001 - a photo must never stop the run
                out["error"] = str(exc)[:200]
        self.history.append(out)
        self.log(f"photo {self.seq:02d} {label} at {self.pos}")
        self.save_state()
        return out

    # -- motion ----------------------------------------------------------------
    def move(self, x, y, z, speed):
        self.robot.move(x, y, z, speed)
        self.pos = [round(x, 2), round(y, 2), round(z, 2)]

    def travel_to(self, x, y, z_travel):
        """Up to the travel height where we are, across, and nothing else."""
        if self.pos is None or self.pos[2] < z_travel - 0.01:
            here = self.pos or [x, y, z_travel]
            self.move(here[0], here[1], z_travel, DESCENT_SPEED if self.pos else TRAVEL_SPEED)
        self.move(x, y, max(self.pos[2], z_travel), TRAVEL_SPEED)

    def descend(self, x, y, z):
        """Straight down, slowing for the last 10 mm."""
        if abs(self.pos[0] - x) > 0.01 or abs(self.pos[1] - y) > 0.01:
            raise ValueError("descend only straight down")
        if z < self.pos[2] - 10.0:
            self.move(x, y, z + 10.0, DESCENT_SPEED)
        self.move(x, y, z, FINE_SPEED if z < self.pos[2] else DESCENT_SPEED)

    # -- steps -------------------------------------------------------------------
    def preflight(self):
        self.phase = "preflight"
        h = self.robot.health()
        self.log(f"robot {h['name']} API {h.get('api_version')}")
        if not self.args.simulate:
            self.lights_before = robot_lights(ROBOT_IP)
            robot_lights(ROBOT_IP, on=True)
            time.sleep(1.5)
        self.photo("before")
        self.robot.open()
        self.log(f"maintenance run {self.robot.run_id}")
        self.robot.home()
        self.pos = None
        if not self.args.simulate:
            self.rack_id = self.robot.command("loadLabware", {
                "location": {"slotName": str(self.args.rack_slot)}, **RACK})["labwareId"]
            self.plate_id = self.robot.command("loadLabware", {
                "location": {"slotName": str(self.args.plate_slot)}, **PLATE})["labwareId"]
        self.log(f"rack {self.rack_id} in slot {self.args.rack_slot}, "
                 f"plate {self.plate_id} in slot {self.args.plate_slot}")
        self.phase = "bare"

    def hover(self, dx, dy, h):
        if self.tip:
            raise ValueError("hover is for the bare nozzle")
        if not 1.0 <= h <= TRAVEL_Z_BARE - RACK_TOP_Z:
            raise ValueError("h must be 1 mm or more above the tip tops")
        if max(abs(dx), abs(dy)) > 4.0:
            raise ValueError("offsets over 4 mm: the rack's position is in doubt, look first")
        x0, y0 = well_xy(self.args.rack_slot, self.args.well)
        x, y, z = x0 + dx, y0 + dy, RACK_TOP_Z + h
        if self.pos and abs(self.pos[0] - x) < 5.0 and abs(self.pos[1] - y) < 5.0 \
                and self.pos[2] >= RACK_TOP_Z + 1.0:
            # already over this tip: rise first if going sideways, never drag
            if abs(self.pos[0] - x) > 0.01 or abs(self.pos[1] - y) > 0.01:
                if self.pos[2] < RACK_TOP_Z + 5.0:
                    self.move(self.pos[0], self.pos[1], RACK_TOP_Z + 5.0, FINE_SPEED)
                self.move(x, y, self.pos[2], FINE_SPEED)
        else:
            self.travel_to(x, y, TRAVEL_Z_BARE)
        self.descend(x, y, z)
        self.offset = [dx, dy]
        self.photo(f"hover_dx{dx:g}_dy{dy:g}_h{h:g}")

    def pickup(self, dz):
        if self.tip:
            raise ValueError("a tip is already on")
        if not -2.0 <= dz <= 2.0:
            raise ValueError("dz within +-2 mm")
        x0, y0 = well_xy(self.args.rack_slot, self.args.well)
        x, y = x0 + self.offset[0], y0 + self.offset[1]
        if self.pos is None or abs(self.pos[0] - x) > 0.01 or abs(self.pos[1] - y) > 0.01:
            raise ValueError("hover over the tip first")
        self.phase = "pickup"
        self.log(f"pickUpTip {self.args.well} offset ({self.offset[0]}, {self.offset[1]}, {dz})")
        self.tip = True                   # from here on, assume it is on
        result = self.robot.command("pickUpTip", {
            "pipetteId": self.robot.pipette_id, "labwareId": self.rack_id,
            "wellName": self.args.well,
            "wellLocation": {"origin": "top",
                             "offset": {"x": self.offset[0], "y": self.offset[1], "z": dz}},
        }, timeout=180)
        self.log(f"pickUpTip result {result}")
        self.pos = self.position()
        self.phase = "tip"
        self.photo("picked_up")

    def position(self):
        if self.args.simulate:
            return self.pos
        p = self.robot.command("savePosition", {"pipetteId": self.robot.pipette_id})["position"]
        return [round(p["x"], 2), round(p["y"], 2), round(p["z"], 2)]

    def up(self):
        if self.pos[2] < TRAVEL_Z_TIP:
            self.move(self.pos[0], self.pos[1], TRAVEL_Z_TIP, DESCENT_SPEED)
        self.photo("up")

    def well(self, name, h):
        if not self.tip:
            raise ValueError("no tip on")
        x, y = well_xy(self.args.plate_slot, name)
        z = PLATE_TOP_Z + h
        if z < PLATE_FLOOR_Z + 1.0:
            raise ValueError(f"the floor is {PLATE_TOP_Z - PLATE_FLOOR_Z:.2f} mm down; "
                             f"h >= {PLATE_FLOOR_Z + 1.0 - PLATE_TOP_Z:.2f}")
        over = abs(self.pos[0] - x) < 0.01 and abs(self.pos[1] - y) < 0.01
        if not over:
            self.travel_to(x, y, TRAVEL_Z_TIP)
            if z < PLATE_TOP_Z + 10.0:
                raise ValueError("arrived over the well; come down to h >= 10 first")
            self.descend(x, y, z)
        else:
            if z < self.pos[2] - WELL_STEP - 1e-9:
                raise ValueError(f"at most {WELL_STEP} mm per step down")
            self.move(x, y, z, FINE_SPEED)
        self.phase = "well"
        self.photo(f"well_{name}_h{h:g}")

    def air(self, vol):
        if not self.tip:
            raise ValueError("no tip on")
        if self.pos[2] < PLATE_TOP_Z + 2.0:
            raise ValueError("aspirate air only above the plate")
        if not 0 < vol <= 200 or self.aspirated + vol > 250:
            raise ValueError("0-200 uL, 250 uL total")
        if self.aspirated == 0:
            # Plunger to the bottom first; a blow-out leaves it below that.
            self.robot.command("prepareToAspirate", {"pipetteId": self.robot.pipette_id})
        self.robot.command("aspirateInPlace", {"pipetteId": self.robot.pipette_id,
                                                "volume": vol, "flowRate": FLOW})
        self.aspirated += vol
        self.log(f"aspirated {vol} uL of air (holding {self.aspirated})")
        self.photo(f"air{vol:g}")

    def dispense(self):
        if not self.tip:
            raise ValueError("no tip on")
        if self.aspirated > 0:
            self.robot.command("dispenseInPlace", {"pipetteId": self.robot.pipette_id,
                                                    "volume": self.aspirated, "flowRate": FLOW})
            self.log(f"dispensed {self.aspirated} uL")
        self.robot.command("blowOutInPlace", {"pipetteId": self.robot.pipette_id,
                                               "flowRate": FLOW})
        self.aspirated = 0.0
        self.log("blown out")
        self.photo("dispensed")

    def return_tip(self):
        """Back into the rack position it came from, the way return_tip() does."""
        self.phase = "return"
        x0, y0 = well_xy(self.args.rack_slot, self.args.well)
        x, y = x0 + self.offset[0], y0 + self.offset[1]
        self.travel_to(x, y, TRAVEL_Z_TIP)
        self.photo("over_rack")
        self.robot.command("dropTip", {
            "pipetteId": self.robot.pipette_id, "labwareId": self.rack_id,
            "wellName": self.args.well,
            "wellLocation": {"origin": "default",
                             "offset": {"x": self.offset[0], "y": self.offset[1], "z": 0}},
            "homeAfter": True,
        }, timeout=180)
        self.tip = False
        self.log("tip returned to the rack")
        self.pos = self.position()
        self.photo("returned")
        self.home()

    def home(self):
        if self.tip:
            raise ValueError("home with a tip on: use return")
        if self.pos:
            self.move(self.pos[0], self.pos[1], max(self.pos[2], TRAVEL_Z_BARE), DESCENT_SPEED)
        self.robot.home()
        self.pos = None
        self.phase = "done"
        self.photo("homed")

    def finish(self):
        try:
            self.robot.close()
        finally:
            if self.lights_before is not None and not self.args.simulate:
                try:
                    robot_lights(ROBOT_IP, on=self.lights_before)
                except Exception:  # noqa: BLE001
                    pass
            self.phase = "closed"
            self.save_state()
            self.log("maintenance run closed; exiting")

    # -- the loop ------------------------------------------------------------------
    def wait(self, what):
        self.last_note = f"waiting for: {what}"
        self.save_state(waiting=what)
        self.log(f"WAIT ({what}); timeout {self.args.timeout:.0f} s")
        t0 = time.time()
        while time.time() - t0 < self.args.timeout:
            if os.path.exists(CMD):
                with open(CMD) as fh:
                    text = fh.read().strip()
                if text:
                    os.remove(CMD)
                    self.log(f"CMD: {text}")
                    return text.split()
            time.sleep(0.5)
        self.log("TIMEOUT: no instruction; taking the safe way out")
        return ["timeout"]

    def prompt(self):
        if self.tip:
            return "well <name> <h> | air <uL> | dispense | up | photo | return"
        return "hover <dx> <dy> <h> | pickup [dz] | photo | home | quit"

    def run(self):
        self.preflight()
        while self.phase not in ("done",):
            cmd = self.wait(self.prompt())
            op = cmd[0]
            try:
                if op == "timeout":
                    if self.tip:
                        self.return_tip()
                    else:
                        self.home()
                elif op == "hover":
                    self.hover(float(cmd[1]), float(cmd[2]), float(cmd[3]))
                elif op == "pickup":
                    self.pickup(float(cmd[1]) if len(cmd) > 1 else 0.0)
                elif op == "well":
                    self.well(cmd[1], float(cmd[2]))
                elif op == "air":
                    self.air(float(cmd[1]))
                elif op == "dispense":
                    self.dispense()
                elif op == "up":
                    self.up()
                elif op == "photo":
                    self.photo("again")
                elif op == "return" and self.tip:
                    self.return_tip()
                elif op == "home" and not self.tip:
                    self.home()
                elif op == "quit" and not self.tip:
                    return
                else:
                    raise ValueError(f"'{' '.join(cmd)}' not allowed (tip={self.tip})")
            except (ValueError, IndexError) as exc:
                self.last_note = f"REFUSED: {exc}"
                self.log(self.last_note)
            except RuntimeError as exc:
                # A command the robot rejected. Nothing moves by itself after
                # this: look at the photo and decide.
                self.last_note = f"ROBOT ERROR: {exc}"
                self.log(self.last_note)
                self.photo("after_error")
            self.save_state()


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--rack-slot", type=int, default=6,
                   help="slot 6 on this deck (2026-09-29); the AC protocol uses 9")
    p.add_argument("--plate-slot", type=int, default=1)
    p.add_argument("--well", default="A1", help="the tip to use, in the rack")
    p.add_argument("--timeout", type=float, default=900.0)
    p.add_argument("--simulate", action="store_true")
    args = p.parse_args()
    cal = TipCal(args)
    x, y = well_xy(args.rack_slot, args.well)
    cal.log(f"start: tip {args.well} in slot {args.rack_slot} at nominal ({x:.2f}, {y:.2f}), "
            f"top z {RACK_TOP_Z:.2f}; plate in slot {args.plate_slot}")
    try:
        cal.run()
    except Exception:  # noqa: BLE001
        cal.log("ERROR:\n" + traceback.format_exc())
        cal.last_note = "ERROR -- see log.txt; holding still"
        cal.save_state()
        return 1
    finally:
        if not cal.tip:
            cal.finish()
        else:
            cal.log("TIP MAY STILL BE ON THE NOZZLE -- maintenance run left open")
            cal.save_state()
    return 0


if __name__ == "__main__":
    sys.exit(main())
