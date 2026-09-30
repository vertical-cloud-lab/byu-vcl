#!/usr/bin/env python3
"""Move paint from the loose vials in slot 3 into plate wells, one fresh tip per colour.

Asked on PR #202 (2026-09-30): "the color vials are on the ot-2 well 3, please
use a tip to take the liquid color and put them in their own slot on the
96-slot well plate. then please read the color with the color sensor". This
does the first half. The reading is ``enclosure_height_cal.py``'s job.

The vials are not in a rack. They are three open glass vials, about 20 mm
across, standing loose and touching at the back of slot 3, so the robot has no
labware for them. Every vial position here is an absolute deck coordinate,
measured from robot-camera photos of the bare nozzle (``look``) before any tip
goes near a vial, and a tip only ever goes into a vial straight down from above
its mouth.

Builds on ``tip_cal.py`` (the pick-up and the plate wells, tested 2026-09-29)
and runs the same way: ON the Pi that holds the robot link, under nohup, one
step at a time through a command file (``echo 'look 330 50 120' > cmd.tmp &&
mv cmd.tmp cmd``, or ``drive.py``). Silence for --timeout seconds means stop:
a tip goes straight up out of whatever it is in, then into the trash, and the
gantry homes.

    bare nozzle
      look <x> <y> <z>        nozzle end to (x, y, z), z >= LOOK_MIN_Z; sideways
                              only at z >= LOOK_TRAVEL_Z, and at most 10 mm down
                              per command below that
      tiphover <well> <h>     nozzle h mm over tip <well> of the rack (h >= 1)
      pickup                  Opentrons' own pickUpTip at the last tiphover
    with a tip on (every z is the tip's END)
      tip <x> <y> <z>         tip end to (x, y, z). Sideways at --travel-z, except
                              nudges of <= 3 mm at z >= --nudge-z. Below --nudge-z
                              at most --max-down mm down per command, and never
                              below --vial-floor
      prep                    plunger to the bottom, in air above --rim-z
      aspirate <uL> [uL/s]    in place, only below --rim-z; <= 250 uL per tip
      well <name> <h>         over plate well <name>, tip end h mm above its rim
                              (tip_cal.py: 5 mm steps down, 1 mm floor clearance)
      dispense [uL/s]         dispense everything held, in place
      blowout                 blow out in place
      wait <s>                hold still (the paint is viscous)
      up                      straight up to --travel-z, slowly out of a vial
      trash                   up, across to the fixed trash, eject, home
      return                  an unused tip back into its own rack position
    either
      photo | home | quit     (home and quit with an empty nozzle only)

``--simulate`` runs the command flow with no robot and no camera.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tip_cal  # noqa: E402
from tip_cal import (  # noqa: E402
    DESCENT_SPEED, FINE_SPEED, PLATE_TOP_Z, RACK_TOP_Z, TRAVEL_SPEED,
    TRAVEL_Z_BARE, TipCal, well_xy,
)

LOOK_MIN_Z = 70.0            # bare nozzle end; the vial rims are expected near z 61
LOOK_TRAVEL_Z = 100.0        # bare nozzle: sideways only at or above this
LOOK_MAX_DOWN = 10.0
MAX_TIP_VOLUME = 250.0
PAINT_SPEED = 40.0           # sideways with paint aboard
OUT_OF_LIQUID_SPEED = 3.0    # the first --rim-z clearance out of a vial
# The OT-2 fixed trash (opentrons_1_trash_1100ml_fixed): opening centred on
# (347.84, 351.5), top at z 82, 107 x 166 mm. Drop a little in front of centre.
TRASH_XY = (347.84, 340.0)
TRASH_TIP_Z = 110.0          # tip end over the trash: 28 mm above its top


def in_plate(x, y, slot):
    ox, oy = tip_cal.deck.slot_origin(slot)
    return ox <= x <= ox + 127.76 and oy <= y <= oy + 85.48


class Transfer(TipCal):
    def __init__(self, args):
        super().__init__(args)
        self.primed = False
        self.wet = False             # this tip has been in paint
        self.picked = []

    # -- helpers ---------------------------------------------------------------
    def refuse(self, msg):
        raise ValueError(msg)

    def same_xy(self, x, y, tol=0.01):
        return self.pos is not None and abs(self.pos[0] - x) <= tol and abs(self.pos[1] - y) <= tol

    # -- bare nozzle -------------------------------------------------------------
    def look(self, x, y, z):
        if self.tip:
            self.refuse("look is for the bare nozzle; use tip")
        if z < LOOK_MIN_Z:
            self.refuse(f"look z must be >= {LOOK_MIN_Z}")
        if not self.same_xy(x, y):
            if self.pos is not None and self.pos[2] < LOOK_TRAVEL_Z:
                self.move(self.pos[0], self.pos[1], LOOK_TRAVEL_Z, DESCENT_SPEED)
            here_z = self.pos[2] if self.pos else TRAVEL_Z_BARE
            self.move(x, y, max(here_z, LOOK_TRAVEL_Z), TRAVEL_SPEED)
        if z < self.pos[2] and z < LOOK_TRAVEL_Z and self.pos[2] - z > LOOK_MAX_DOWN + 1e-9:
            self.refuse(f"below z {LOOK_TRAVEL_Z}, at most {LOOK_MAX_DOWN} mm down per look")
        self.move(x, y, z, DESCENT_SPEED if z >= self.pos[2] or z >= LOOK_TRAVEL_Z else FINE_SPEED)
        self.phase = "bare"
        self.photo(f"look_x{x:g}_y{y:g}_z{z:g}")

    def tiphover(self, well, h):
        if self.tip:
            self.refuse("a tip is already on")
        if well in self.picked:
            self.refuse(f"tip {well} has been used already")
        well_xy(self.args.rack_slot, well)          # validates the name
        if self.args.well != well:
            self.args.well = well
            self.offset = [0.0, 0.0]
        self.hover(0.0, 0.0, h)

    def pickup_tip(self):
        self.pickup(0.0)
        self.picked.append(self.args.well)
        self.primed = False
        self.wet = False
        self.aspirated = 0.0

    # -- with a tip ----------------------------------------------------------------
    def tip_to(self, x, y, z):
        a = self.args
        if not self.tip:
            self.refuse("no tip on")
        if z > a.travel_z + 40:
            self.refuse("too high")
        floor = PLATE_TOP_Z + 1.0 if in_plate(x, y, a.plate_slot) else a.vial_floor
        if z < floor:
            self.refuse(f"z {z} is below the floor {floor} here")
        if not self.same_xy(x, y):
            dxy = max(abs(self.pos[0] - x), abs(self.pos[1] - y))
            if dxy <= 3.0 and self.pos[2] >= a.nudge_z and z >= a.nudge_z:
                self.move(x, y, self.pos[2], FINE_SPEED)          # a nudge, in air
            else:
                if self.pos[2] < a.travel_z:
                    self.rise(a.travel_z)
                self.move(x, y, self.pos[2], PAINT_SPEED if self.aspirated else TRAVEL_SPEED)
        if z < self.pos[2]:
            if z < a.nudge_z and self.pos[2] > a.nudge_z:
                # Arriving from above: straight down to the nudge height, and
                # stop there for a look if the rest is more than one step.
                self.move(x, y, a.nudge_z, DESCENT_SPEED)
                if a.nudge_z - z > a.max_down + 1e-9:
                    self.phase = "tip"
                    self.last_note = (f"stopped at z {a.nudge_z:g}: below it, at most "
                                      f"{a.max_down:g} mm down per command")
                    self.log(self.last_note)
                    self.photo(f"tip_x{x:g}_y{y:g}_z{a.nudge_z:g}")
                    return
            if z < a.nudge_z and self.pos[2] - z > a.max_down + 1e-9:
                self.refuse(f"at most {a.max_down:g} mm down per command below z {a.nudge_z:g}")
            self.move(x, y, z, DESCENT_SPEED if z >= a.nudge_z else FINE_SPEED)
        elif z > self.pos[2]:
            self.rise(z)
        self.phase = "tip"
        self.photo(f"tip_x{x:g}_y{y:g}_z{z:g}")

    def travel_to(self, x, y, z_travel):
        """tip_cal's travel, but out of a vial slowly and sideways gently with paint."""
        if self.pos is None:
            self.move(x, y, z_travel, TRAVEL_SPEED)
            return
        if self.pos[2] < z_travel - 0.01:
            self.rise(z_travel)
        self.move(x, y, max(self.pos[2], z_travel),
                  PAINT_SPEED if self.aspirated else TRAVEL_SPEED)

    def rise(self, z):
        """Straight up: slowly while the tip end may still be in a vial."""
        x, y, z0 = self.pos
        if self.tip and z0 < self.args.rim_z + 3.0 and not in_plate(x, y, self.args.plate_slot):
            top = min(z, self.args.rim_z + 3.0)
            self.move(x, y, top, OUT_OF_LIQUID_SPEED)
            if self.aspirated:
                time.sleep(2.0)                    # let a drop fall back into the vial
        if self.pos[2] < z:
            self.move(x, y, z, DESCENT_SPEED)

    def prep(self):
        if not self.tip:
            self.refuse("no tip on")
        if self.pos[2] <= self.args.rim_z + 2.0:
            self.refuse(f"prep only in air, tip end above z {self.args.rim_z + 2.0}")
        self.robot.command("prepareToAspirate", {"pipetteId": self.robot.pipette_id})
        self.primed = True
        self.log("plunger at the bottom, ready to aspirate")
        self.save_state()

    def aspirate(self, vol, rate):
        if not self.tip:
            self.refuse("no tip on")
        if not self.primed:
            self.refuse("prep first, in air")
        if self.pos[2] > self.args.rim_z - 3.0:
            self.refuse(f"aspirate only inside a vial, tip end below z {self.args.rim_z - 3.0}")
        if in_plate(self.pos[0], self.pos[1], self.args.plate_slot):
            self.refuse("not from the plate")
        if not 0 < vol <= MAX_TIP_VOLUME - self.aspirated or not 5.0 <= rate <= 92.86:
            self.refuse(f"0-{MAX_TIP_VOLUME - self.aspirated:g} uL at 5-92.86 uL/s")
        self.robot.command("aspirateInPlace", {"pipetteId": self.robot.pipette_id,
                                                "volume": vol, "flowRate": rate}, timeout=180)
        self.aspirated += vol
        self.wet = True
        self.log(f"aspirated {vol:g} uL at {rate:g} uL/s (holding {self.aspirated:g})")
        self.photo(f"aspirated{vol:g}")

    def dispense_all(self, rate):
        if not self.tip or self.aspirated <= 0:
            self.refuse("nothing to dispense")
        if not in_plate(self.pos[0], self.pos[1], self.args.plate_slot) \
                or self.pos[2] > PLATE_TOP_Z + 2.0:
            self.refuse("dispense only inside a plate well")
        vol = self.aspirated
        self.robot.command("dispenseInPlace", {"pipetteId": self.robot.pipette_id,
                                                "volume": vol, "flowRate": rate}, timeout=180)
        self.aspirated = 0.0
        self.log(f"dispensed {vol:g} uL at {rate:g} uL/s")
        self.photo(f"dispensed{vol:g}")

    def blowout(self):
        if not self.tip:
            self.refuse("no tip on")
        self.robot.command("blowOutInPlace", {"pipetteId": self.robot.pipette_id,
                                               "flowRate": 46.43})
        self.aspirated = 0.0
        self.primed = False
        self.log("blown out")
        self.photo("blown_out")

    def up_to_travel(self):
        if not self.tip:
            self.refuse("no tip on")
        if self.pos[2] < self.args.travel_z:
            self.rise(self.args.travel_z)
        self.photo("up")

    def trash(self):
        if not self.tip:
            self.refuse("no tip on")
        self.phase = "trash"
        if self.pos[2] < self.args.travel_z:
            self.rise(self.args.travel_z)
        self.move(TRASH_XY[0], TRASH_XY[1], max(self.pos[2], TRASH_TIP_Z),
                  PAINT_SPEED if self.aspirated else TRAVEL_SPEED)
        if self.pos[2] > TRASH_TIP_Z:
            self.move(TRASH_XY[0], TRASH_XY[1], TRASH_TIP_Z, DESCENT_SPEED)
        self.photo("over_trash")
        self.robot.command("dropTipInPlace", {"pipetteId": self.robot.pipette_id,
                                               "homeAfter": True}, timeout=180)
        self.tip = False
        self.aspirated = 0.0
        self.primed = False
        self.log(f"tip {self.args.well} dropped in the trash")
        self.pos = self.position()
        self.home()

    # -- the loop ------------------------------------------------------------------
    def prompt(self):
        if self.tip:
            return ("tip <x> <y> <z> | prep | aspirate <uL> [uL/s] | well <name> <h> | "
                    "dispense [uL/s] | blowout | wait <s> | up | trash | return | photo")
        return "look <x> <y> <z> | tiphover <well> <h> | pickup | photo | home | quit"

    def safe_exit(self):
        if self.tip:
            self.log("taking the safe way out: straight up, then the trash")
            self.trash()
        else:
            self.home()

    def run(self):
        self.preflight()
        while True:
            cmd = self.wait(self.prompt())
            op = cmd[0]
            try:
                if op == "timeout":
                    self.safe_exit()
                    return
                elif op == "look":
                    self.look(float(cmd[1]), float(cmd[2]), float(cmd[3]))
                elif op == "tiphover":
                    self.tiphover(cmd[1].upper(), float(cmd[2]))
                elif op == "pickup":
                    self.pickup_tip()
                elif op == "tip":
                    self.tip_to(float(cmd[1]), float(cmd[2]), float(cmd[3]))
                elif op == "prep":
                    self.prep()
                elif op == "aspirate":
                    self.aspirate(float(cmd[1]), float(cmd[2]) if len(cmd) > 2 else 30.0)
                elif op == "well":
                    self.well(cmd[1].upper(), float(cmd[2]))
                elif op == "dispense":
                    self.dispense_all(float(cmd[1]) if len(cmd) > 1 else 30.0)
                elif op == "blowout":
                    self.blowout()
                elif op == "wait":
                    s = float(cmd[1])
                    if not 0 < s <= 60:
                        self.refuse("wait 0-60 s")
                    time.sleep(s)
                    self.photo(f"waited{s:g}")
                elif op == "up":
                    self.up_to_travel()
                elif op == "trash":
                    self.trash()
                elif op == "return" and self.tip:
                    if self.wet:
                        self.refuse("this tip has held paint: trash it")
                    self.return_tip()
                elif op == "photo":
                    self.photo("again")
                elif op == "home" and not self.tip:
                    self.home()
                elif op == "quit" and not self.tip:
                    return
                else:
                    self.refuse(f"'{' '.join(cmd)}' not allowed (tip={self.tip})")
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
    p.add_argument("--rack-slot", type=int, default=6)
    p.add_argument("--plate-slot", type=int, default=1)
    p.add_argument("--travel-z", type=float, default=110.0,
                   help="tip end for every sideways move with a tip on (nozzle ~161)")
    p.add_argument("--rim-z", type=float, default=61.0,
                   help="the vials' rim height, measured from photos before a tip goes in")
    p.add_argument("--nudge-z", type=float, default=70.0,
                   help="sideways nudges of <= 3 mm allowed with the tip end at or above this")
    p.add_argument("--max-down", type=float, default=10.0,
                   help="largest single step down with the tip end below --nudge-z")
    p.add_argument("--vial-floor", type=float, default=20.0,
                   help="lowest tip end allowed outside the plate (vial floors are at z ~3)")
    p.add_argument("--timeout", type=float, default=900.0)
    p.add_argument("--simulate", action="store_true")
    args = p.parse_args()
    args.well = "A1"
    tr = Transfer(args)
    tr.log(f"start: rack slot {args.rack_slot}, plate slot {args.plate_slot}, travel z "
           f"{args.travel_z}, rim z {args.rim_z}, nudge z {args.nudge_z}, vial floor "
           f"{args.vial_floor}, rack top {RACK_TOP_Z:.2f}")
    try:
        tr.run()
    except Exception:  # noqa: BLE001
        tr.log("ERROR:\n" + traceback.format_exc())
        tr.last_note = "ERROR -- see log.txt; holding still"
        tr.save_state()
        return 1
    finally:
        if not tr.tip:
            tr.finish()
        else:
            tr.log("TIP MAY STILL BE ON THE NOZZLE -- maintenance run left open")
            tr.save_state()
    return 0


if __name__ == "__main__":
    sys.exit(main())
