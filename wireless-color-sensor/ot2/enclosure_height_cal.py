#!/usr/bin/env python3
"""Find how low the colour-sensor enclosure can sit over a 96-well plate.

**It has not done that yet.** Its one run with the enclosure aboard, on
2026-09-25, dropped it: the grip check passed at 10.7x, and the enclosure fell
~85 mm to the deck about 6 s into the carry. See
``results-enclosure-height-2026-09-25.md``. The grip check measures *light* --
that the enclosure has left its base -- not how tightly it is held, so a pass
here does not mean the carry is safe. Do not run ``carry`` unattended until
something that actually tests the grip has been added.

Runs ON the Pi that holds the robot link, under nohup, and is driven one step
at a time through a command file. It is built this way, rather than driven
move-by-move over SSH from a CI runner, for two reasons:

* A CI job can end at any moment -- it is torn down as soon as it posts its
  final comment. Anything it was driving would stop mid-sequence with the
  enclosure on the nozzle. This process outlives it.
* Every step waits for an explicit go-ahead, and silence means "stop": if no
  command arrives within --timeout seconds, the enclosure is carried back and
  set down on its base, and the gantry is homed.

Commands -- write one line to ``cmd`` in the working directory, atomically
(``echo 'z 110' > cmd.tmp && mv cmd.tmp cmd``); it is consumed when read:

    align <x> <y> <z>
                    bare nozzle only: hover over (x, y) at z >= 100 to line up
                    with the socket; the pickup then happens at that (x, y)
    pickup          descend to just above the socket mouth and STOP there
    down <z>        press further, at most 2 mm per step, never below --press-z
    lift            once pressed to within 1 mm of --press-z: lift, dwell, grip check
    back-out        after a pickup: rise 5 mm, eject, home (abandon the press)
    carry           high lift, then carry to the plate target at carry height
    z <mm>          move the nozzle to this Z over the target (bounded, stepped)
    xy <x> <y>      move the target, at the current Z, only when Z >= 125
    floor <mm>      change the lowest Z that ``z`` will accept
    read [n]        take n sensor readings where it is (default 3)
    photo           photograph again without moving
    return          lift, carry back, set the enclosure down, home
    retry-release [extra_mm]
                    the release did not let go: go back down and eject again,
                    optionally pressing extra_mm (0-1) deeper first
    park            it will not let go: hold it at its own release pose
    seated | aboard after a release with no sensor reading, say which it is
    home            lift and home WITHOUT a release (empty nozzle only)
    quit            close the maintenance run and exit (only when nothing is aboard)

Status is written to ``state.json`` after every step, and photos to
``NN_label_robot.jpg`` (robot camera, turned upright) and ``NN_label_live.jpg``
(newest livestream frame, taken once the stream has caught up with the move).
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
import live_frame  # noqa: E402
from run_xscan_test import (  # noqa: E402
    CARRY_SEGMENT_MM, CARRY_SPEED, CARRY_Z, CLEAR_Z, DESCENT_SPEED, DROP_DESCENT,
    ENTRY_SPEED, HEADERS, HIGH_LIFT_SPEED, LIFT_DWELL_S, LIFT_Z,
    PRESS_SPEED, PRESS_Z, Robot, high_lift_stages, robot_lights,
)
from sensor_read import SensorLink  # noqa: E402

ROBOT_IP = "169.254.51.252"
FFMPEG = os.path.expanduser("~/ytframes/bin/ffmpeg")
CMD = os.path.join(HERE, "cmd")
STATE = os.path.join(HERE, "state.json")
LOGFILE = os.path.join(HERE, "log.txt")

# Base in slot 10. Its LEFT socket (A1) is at the within-slot offset every run
# since PR #60 used. The RIGHT socket (A2), where the enclosure was found on
# 2026-09-25, took a full-depth press at A1 + (56.25, 1.0); the definition's
# A1 + (55.95, 0) jammed 2.3 mm in. Confirm by photo with `align` regardless.
SOCKET_A1 = deck.in_slot(10, 36.55, 44.0)              # (36.55, 315.5)
SOCKET_A2 = deck.in_slot(10, 36.55 + 56.25, 45.0)      # (92.8, 316.5)
ALIGN_MIN_Z = 100.0         # bare-nozzle hover floor over a socket (mouth ~97.5-99.5)
ALIGN_TRAVEL_Z = 120.0      # lateral moves near the base only at or above this
# run_xscan_test.pick_up's descent ladder, split so the bare nozzle stops 30 mm
# over the socket for an alignment photo before anything presses down.
ALIGN_LADDER = [170.0, 150.0, 120.0]
PICKUP_LADDER = [105.0, 101.0, 99.0]
SEATED_MAX = 800            # counts; above this the enclosure is not closed on its base
GRIP_RATIO = 2.0
SAFE_XY_Z = 125.0           # lateral moves over the plate only at or above this nozzle Z
MAX_RELEASE_RETRIES = 3


class Cal:
    def __init__(self, args):
        self.args = args
        self.robot = Robot(ROBOT_IP)
        self.link = None
        self.seq = 0
        self.phase = "start"
        self.aboard = False          # we believe the enclosure is on the nozzle
        self.pos = None              # last commanded [x, y, z]
        self.floor = args.floor
        self.target = [args.target_x, args.target_y]
        self.press_z = args.press_z
        self.release_z = round(DROP_DESCENT[-1] + (args.press_z - PRESS_Z), 2)
        self.socket = [args.socket_x, args.socket_y]
        self.drop_dx = args.drop_dx
        self.seated_total = None
        self.lights_before = None
        self.history = []
        self.last_note = ""
        self.release_tries = 0
        self.live_failures = 0

    # -- bookkeeping ---------------------------------------------------------
    def log(self, msg):
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        with open(LOGFILE, "a") as fh:
            fh.write(line + "\n")

    def save_state(self, waiting=None):
        state = {
            "updated_local": datetime.now().strftime("%H:%M:%S"),
            "phase": self.phase, "aboard": self.aboard, "pos": self.pos,
            "floor": self.floor, "target": self.target, "press_z": self.press_z,
            "release_z": self.release_z, "socket": self.socket,
            "drop": self.drop, "seq": self.seq,
            "seated_total": self.seated_total, "waiting_for": waiting,
            "timeout_s": self.args.timeout, "note": self.last_note,
            "history": self.history[-60:],
        }
        tmp = STATE + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(state, fh, indent=1)
        os.replace(tmp, STATE)

    # -- robot, with patience for a dropped link -------------------------------
    def _healthy(self):
        try:
            r = requests.get(f"http://{ROBOT_IP}:31950/health", headers=HEADERS, timeout=5)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def call(self, fn, *a, **kw):
        """Run a robot call; if the link drops, wait for it rather than give up.

        Everything routed through here is safe to repeat (absolute moves, home,
        an eject with nothing on the nozzle), so re-issuing after the link
        returns is correct.
        """
        deadline = time.time() + self.args.link_wait
        while True:
            try:
                return fn(*a, **kw)
            except (requests.ConnectionError, requests.Timeout) as exc:
                if time.time() > deadline:
                    raise
                self.log(f"LINK: {type(exc).__name__}; waiting for the robot to answer again")
                self.last_note = "robot link down -- waiting"
                self.save_state(waiting="link")
                while not self._healthy():
                    if time.time() > deadline:
                        raise
                    time.sleep(5)
                self.log("LINK: robot answers again; repeating the last call")

    def move(self, x, y, z, speed):
        self.call(self.robot.move, x, y, z, speed)
        self.pos = [round(x, 2), round(y, 2), round(z, 2)]

    def carry_to(self, x, y, z):
        """Short lateral segments: the enclosure sheds on long fast moves."""
        x0, y0 = self.pos[0], self.pos[1]
        span = max(abs(x - x0), abs(y - y0))
        steps = max(1, int(span / CARRY_SEGMENT_MM + 0.999))
        for i in range(1, steps + 1):
            self.move(x0 + (x - x0) * i / steps, y0 + (y - y0) * i / steps, z, CARRY_SPEED)

    # -- observations ------------------------------------------------------------
    def photos(self, label, reads=0):
        self.seq += 1
        base = os.path.join(HERE, f"{self.seq:02d}_{label}")
        t_move = time.time()
        out = {"seq": self.seq, "label": label, "pos": self.pos,
               "t_local": datetime.now().strftime("%H:%M:%S")}
        try:
            r = requests.post(f"http://{ROBOT_IP}:31950/camera/picture",
                              headers=HEADERS, timeout=30)
            r.raise_for_status()
            raw = base + "_robot_raw.jpg"
            with open(raw, "wb") as fh:
                fh.write(r.content)
            # The camera is mounted inverted; turn the frame upright.
            subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-i", raw,
                            "-vf", "hflip,vflip", "-q:v", "3", base + "_robot.jpg"],
                           check=True)
            os.remove(raw)
            out["robot"] = os.path.basename(base + "_robot.jpg")
        except Exception as exc:  # noqa: BLE001 - a photo must never stop the run
            out["robot_error"] = str(exc)[:200]
        if reads:
            out["reads"] = self.read(reads, label)
        # The livestream runs ~3 s behind; keep grabbing until its newest
        # segment ends after the move did, so the frame shows the new pose.
        if self.live_failures < 3:
            try:
                info = {}
                for _ in range(6):
                    time.sleep(3)
                    info = live_frame.grab(base + "_live.jpg")
                    if info.get("frame_epoch") and info["frame_epoch"] >= t_move + 1.0:
                        break
                out["live"] = os.path.basename(base + "_live.jpg")
                out["live_frame_local"] = info.get("frame_local")
                self.live_failures = 0
            except Exception as exc:  # noqa: BLE001
                out["live_error"] = str(exc)[:200]
                self.live_failures += 1
        self.history.append(out)
        self.log(f"photo {self.seq:02d} {label} at {self.pos}"
                 + (f"  reads={out.get('reads')}" if reads else ""))
        self.save_state()
        return out

    def read(self, n, label):
        totals = []
        try:
            if self.link is None:
                self.link = SensorLink().connect()
            for i in range(n):
                r = self.link.read(label=f"cal-{label}-{i + 1}")
                totals.append(r["total"])
        except Exception as exc:  # noqa: BLE001 - the sensor is a cross-check only
            self.log(f"sensor read failed: {exc}")
            try:
                if self.link:
                    self.link.close()
            except Exception:  # noqa: BLE001
                pass
            self.link = None
        return totals

    # -- waiting for a decision --------------------------------------------------
    def wait(self, what):
        self.last_note = f"waiting for: {what}"
        self.save_state(waiting=what)
        self.log(f"WAIT ({what}); timeout {self.args.timeout:.0f} s")
        t0 = time.time()
        while time.time() - t0 < self.args.timeout:
            if os.path.exists(CMD):
                with open(CMD) as fh:
                    text = fh.read().strip()
                # An empty file is a writer caught between create and write
                # (write cmd.tmp then mv it into place to avoid even that).
                if text:
                    os.remove(CMD)
                    self.log(f"CMD: {text}")
                    return text.split()
            time.sleep(0.5)
        self.log("TIMEOUT: no instruction; taking the safe way out")
        return ["timeout"]

    # -- the sequence --------------------------------------------------------------
    def preflight(self):
        self.phase = "preflight"
        h = self.call(self.robot.health)
        self.log(f"robot {h['name']} API {h.get('api_version')}")
        self.lights_before = robot_lights(ROBOT_IP)
        if self.args.lights != "leave":
            robot_lights(ROBOT_IP, on=self.args.lights == "on")
            time.sleep(2.0)
        totals = self.read(2, "seated")
        self.seated_total = sum(totals) / len(totals) if totals else None
        self.log(f"seated baseline {totals}")
        self.photos("before")
        self.call(self.robot.open)
        self.log(f"maintenance run {self.robot.run_id}")
        self.call(self.robot.home)
        self.pos = None

    @property
    def drop(self):
        return (round(self.socket[0] + self.drop_dx, 2), self.socket[1])

    def align(self):
        self.phase = "align"
        x, y = self.socket
        for z in ALIGN_LADDER:
            self.move(x, y, z, 25.0)
        self.photos("align_hover_z120")

    def realign(self, x, y, z):
        """Bare nozzle only: hover over (x, y) at z, travelling at a safe height."""
        if deck.slot_margin(10, x, y) < 5.0:
            raise ValueError(f"({x}, {y}) is not well inside slot 10")
        if not ALIGN_MIN_Z <= z <= CARRY_Z:
            raise ValueError(f"align z must be {ALIGN_MIN_Z}-{CARRY_Z}")
        if abs(x - self.pos[0]) > 0.01 or abs(y - self.pos[1]) > 0.01:
            if self.pos[2] < ALIGN_TRAVEL_Z:
                self.move(self.pos[0], self.pos[1], ALIGN_TRAVEL_Z, DESCENT_SPEED)
            self.move(x, y, self.pos[2], DESCENT_SPEED)
        self.move(x, y, z, DESCENT_SPEED)
        self.socket = [x, y]
        self.photos(f"align_x{x:g}_y{y:g}_z{z:g}")

    def pickup(self):
        """Descend to just above the socket mouth and STOP.

        On 2026-09-25 a continuous press into the right-hand socket stalled
        ~2.6 mm into the enclosure's top and the Z motor silently lost ~7 mm
        of steps. So the press is now fed in steps with ``down <z>``, each one
        photographed: the nozzle's shoulder stays visible above the enclosure,
        and a step that did not happen shows up as a shoulder that did not
        move. A jam is then one short stall, backed out at once.
        """
        self.phase = "press"
        x, y = self.socket
        if abs(x - self.pos[0]) > 0.01 or abs(y - self.pos[1]) > 0.01:
            raise ValueError("not hovering over the socket; align first")
        for z in [z for z in PICKUP_LADDER if z < self.pos[2]]:
            self.move(x, y, z, DESCENT_SPEED)
        self.photos(f"press_start_z{self.pos[2]:g}")

    def press_to(self, z):
        if not self.press_z - 1e-9 <= z < self.pos[2]:
            raise ValueError(f"down must go lower, to no less than {self.press_z}")
        if self.pos[2] - z > 2.0 + 1e-9:
            raise ValueError("at most 2 mm per step while pressing")
        x, y = self.socket
        self.move(x, y, z, ENTRY_SPEED)
        time.sleep(0.5)
        self.photos(f"press_z{z:g}")

    def lift(self):
        self.phase = "pickup"
        x, y = self.socket
        self.aboard = True                     # from here on, assume it is on
        self.move(x, y, LIFT_Z, DESCENT_SPEED)
        time.sleep(LIFT_DWELL_S)
        shot = self.photos("lifted_z110", reads=2)
        lifted = shot.get("reads") or []
        if lifted and self.seated_total:
            ratio = (sum(lifted) / len(lifted)) / max(self.seated_total, 1.0)
            shot["grip_ratio"] = round(ratio, 2)
            self.last_note = f"grip ratio {ratio:.1f}x (need {GRIP_RATIO})"
            self.log(self.last_note)
            if ratio < GRIP_RATIO:
                self.log("GRIP CHECK FAILED -- the enclosure is probably still on its base")
                self.aboard = False
        self.save_state()

    def back_out(self):
        """Abandon a press: rise 5 mm, eject, rise, home.

        If the nozzle did catch the enclosure, 5 mm up leaves its foot inside
        its own pocket, so the eject drops it straight back in. If it did not,
        the eject fires on an empty nozzle, which is harmless.
        """
        self.phase = "back-out"
        x, y = self.socket
        self.move(x, y, self.press_z + 5.0, PRESS_SPEED)
        self.log("backing out: eject in place over the pocket")
        self.call(self.robot.drop_tip_in_place)
        self.move(x, y, LIFT_Z, DESCENT_SPEED)
        shot = self.photos("backed_out", reads=2)
        self.aboard = False
        reads = shot.get("reads") or []
        if reads and sum(reads) / len(reads) > SEATED_MAX:
            self.aboard = True
            self.last_note = "backed out but the sensor says it is NOT seated -- look"
            self.log(self.last_note)
            self.phase = "release?"
            return
        self.call(self.robot.home)
        self.pos = None
        self.phase = "done"
        self.photos("homed", reads=2)

    def carry(self):
        self.phase = "carry"
        x, y = self.socket
        for z in high_lift_stages(CARRY_Z):
            self.move(x, y, z, HIGH_LIFT_SPEED)
        self.carry_to(self.target[0], self.target[1], CARRY_Z)
        self.photos(f"over_plate_z{CARRY_Z:g}", reads=2)

    @staticmethod
    def max_step(z):
        if z >= 130:
            return 40.0
        if z >= 118:
            return 12.0
        if z >= 110:
            return 4.0
        if z >= 104:
            return 2.0
        return 1.0

    def go_z(self, z):
        if z < self.floor:
            raise ValueError(f"z {z} is below the floor {self.floor}")
        if z > CARRY_Z:
            raise ValueError(f"z {z} is above the carry height {CARRY_Z}")
        here = self.pos[2]
        if z < here and here - z > self.max_step(z) + 1e-9:
            raise ValueError(f"step {here - z:.2f} mm down to {z} exceeds the "
                             f"{self.max_step(z)} mm allowed at that height")
        self.phase = "ladder"
        speed = 5.0 if z < 120 else DESCENT_SPEED
        self.move(self.target[0], self.target[1], z, speed)
        time.sleep(2.0)
        self.photos(f"z{z:g}", reads=2)

    def go_xy(self, x, y):
        if self.pos[2] < SAFE_XY_Z:
            raise ValueError(f"lateral moves need z >= {SAFE_XY_Z}; at {self.pos[2]}")
        if deck.slot_margin(1, x, y) < 0:
            raise ValueError(f"({x}, {y}) is outside slot 1")
        self.carry_to(x, y, self.pos[2])
        self.target = [x, y]
        self.photos(f"xy{x:g}_{y:g}", reads=2)

    def set_down(self):
        """From wherever the enclosure is: lift, go to the release column, release."""
        self.phase = "return"
        x, y = self.pos[0], self.pos[1]
        near_base = abs(x - self.socket[0]) < 15 and abs(y - self.socket[1]) < 15
        top = 130.0 if near_base else CARRY_Z
        for z in [z for z in (130.0, 150.0, CARRY_Z) if self.pos[2] < z <= top]:
            self.move(x, y, z, DESCENT_SPEED if z <= 130 else HIGH_LIFT_SPEED)
        self.carry_to(self.drop[0], self.drop[1], max(self.pos[2], top))
        self.release(extra=0.0)

    def release(self, extra):
        self.phase = "release"
        self.release_tries += 1
        x, y = self.drop
        rz = round(self.release_z - extra, 2)
        for z in [z for z in list(DROP_DESCENT[:-1]) + [rz] if z < self.pos[2]]:
            self.move(x, y, z, DESCENT_SPEED)
            time.sleep(0.4)
        self.photos(f"predrop_z{rz:g}")
        self.log("releasing (dropTipInPlace)")
        self.call(self.robot.drop_tip_in_place)
        self.move(x, y, CLEAR_Z, 20.0)
        shot = self.photos("after_release", reads=2)
        after = shot.get("reads") or self.read(2, "after-release-retry")
        if not after:
            # No sensor, so no way to tell seated from still-aboard. Do not
            # guess in either direction: a retry would press an empty nozzle
            # onto a seated enclosure, and homing would fly one that is still
            # on. Stay here and let someone look at the photo.
            self.phase = "release?"
            self.last_note = "after release: no sensor reading -- check the photo"
            self.log(self.last_note)
            self.save_state()
            return
        mean = sum(after) / len(after)
        self.aboard = mean > SEATED_MAX
        self.last_note = (f"after release {mean:.0f} counts -> "
                          + ("STILL ABOARD" if self.aboard else "seated on its base"))
        self.log(self.last_note)
        self.save_state()
        if not self.aboard:
            self.call(self.robot.home)
            self.pos = None
            self.phase = "done"
            self.photos("homed", reads=2)

    def park_over_base(self):
        """Last resort if it will not let go: hold it at its own release pose.

        That is the pose every successful release lets go from, so if the fit
        gives up later, it drops the way it always does -- into the pocket.
        """
        x, y = self.drop
        for z in [z for z in list(DROP_DESCENT[:-1]) + [self.release_z] if z < self.pos[2]]:
            self.move(x, y, z, DESCENT_SPEED)
            time.sleep(0.4)
        self.phase = "parked"
        self.last_note = ("enclosure would not release; parked at its release pose "
                          "over the base, so if it falls it falls into the pocket")
        self.log(self.last_note)
        self.photos("parked", reads=2)

    def home_empty(self):
        self.phase = "home"
        if self.pos:
            self.move(self.pos[0], self.pos[1], min(max(self.pos[2], 110.0), 128.0), 10.0)
        self.call(self.robot.home)
        self.pos = None
        self.phase = "done"
        self.photos("homed")

    def finish(self):
        try:
            self.call(self.robot.close)
        finally:
            if self.args.lights != "leave" and self.lights_before is not None:
                try:
                    robot_lights(ROBOT_IP, on=self.lights_before)
                except Exception:  # noqa: BLE001
                    pass
            if self.link:
                self.link.close()
            self.phase = "closed"
            self.save_state()
            self.log("maintenance run closed; exiting")

    def prompt(self):
        if self.phase == "pickup":
            return "carry | return | home" if self.aboard else "home"
        if self.phase in ("carry", "ladder"):
            return "z <mm> | xy <x> <y> | floor <mm> | read [n] | photo | return"
        if self.phase == "release":
            return "retry-release [mm] | park"
        if self.phase == "release?":
            return "seated | aboard | retry-release [mm]"
        return "quit"

    def run(self):
        self.preflight()
        self.align()
        while True:
            cmd = self.wait("align <x> <y> <z> | pickup | home")
            try:
                if cmd[0] == "align":
                    self.realign(float(cmd[1]), float(cmd[2]), float(cmd[3]))
                    continue
                if cmd[0] == "pickup":
                    self.pickup()
                    while True:
                        cmd = self.wait("down <z> | lift | back-out")
                        if cmd[0] == "down":
                            try:
                                self.press_to(float(cmd[1]))
                            except (ValueError, IndexError) as exc:
                                self.last_note = f"REFUSED: {exc}"
                                self.log(self.last_note)
                            continue
                        if cmd[0] == "lift" and self.pos[2] <= self.press_z + 1.0:
                            self.lift()
                        else:                  # back-out, timeout, or lift too shallow
                            self.back_out()
                        break
                    break
            except (ValueError, IndexError) as exc:
                self.last_note = f"REFUSED: {exc}"
                self.log(self.last_note)
                continue
            self.home_empty()
            return
        while self.phase not in ("done", "parked"):
            cmd = self.wait(self.prompt())
            op = cmd[0]
            try:
                if op == "timeout" and self.phase == "release?":
                    self.log("no instruction and no sensor: holding still, no motion")
                elif op == "timeout":
                    if self.phase == "release" and self.aboard:
                        if self.release_tries >= MAX_RELEASE_RETRIES:
                            self.park_over_base()
                        else:
                            self.move(self.drop[0], self.drop[1], 110.0, DESCENT_SPEED)
                            self.release(extra=0.5)
                    elif self.aboard:
                        self.set_down()
                    else:
                        self.home_empty()
                elif op == "carry" and self.phase == "pickup" and self.aboard:
                    self.carry()
                elif op == "z" and self.phase in ("carry", "ladder"):
                    self.go_z(float(cmd[1]))
                elif op == "xy" and self.phase in ("carry", "ladder"):
                    self.go_xy(float(cmd[1]), float(cmd[2]))
                elif op == "floor":
                    f = float(cmd[1])
                    if f < 60.0:
                        raise ValueError("floor below 60 refused")
                    self.floor = f
                    self.log(f"floor now {f}")
                elif op == "read":
                    n = int(cmd[1]) if len(cmd) > 1 else 3
                    self.history.append({"label": "read", "pos": self.pos,
                                         "reads": self.read(n, "extra")})
                elif op == "photo":
                    self.photos("again", reads=2)
                elif op == "return" and self.aboard and self.phase in ("pickup", "carry", "ladder"):
                    self.set_down()
                elif op == "seated" and self.phase == "release?":
                    self.aboard = False
                    self.call(self.robot.home)
                    self.pos = None
                    self.phase = "done"
                    self.photos("homed", reads=2)
                elif op == "aboard" and self.phase == "release?":
                    self.aboard = True
                    self.phase = "release"
                elif op == "park" and self.phase == "release" and self.aboard:
                    self.park_over_base()
                elif op == "retry-release" and self.phase in ("release", "release?"):
                    extra = float(cmd[1]) if len(cmd) > 1 else 0.0
                    if not 0.0 <= extra <= 1.0:
                        raise ValueError("extra press must be 0-1 mm")
                    if self.release_tries >= MAX_RELEASE_RETRIES + 2:
                        raise ValueError("too many release attempts; look first")
                    self.move(self.drop[0], self.drop[1], 110.0, DESCENT_SPEED)
                    self.release(extra=extra)
                elif op == "home" and not self.aboard and self.phase in ("pickup", "align"):
                    self.home_empty()
                elif op == "quit" and not self.aboard:
                    return
                else:
                    raise ValueError(f"'{' '.join(cmd)}' not allowed in phase {self.phase} "
                                     f"(aboard={self.aboard})")
            except (ValueError, IndexError) as exc:
                self.last_note = f"REFUSED: {exc}"
                self.log(self.last_note)
            self.save_state()


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--target-x", type=float, default=63.88,
                   help="nozzle X over the plate (default: centre of slot 1)")
    p.add_argument("--target-y", type=float, default=42.74)
    p.add_argument("--press-z", type=float, default=90.0,
                   help="pickup press depth; 90.0 is the tighter fit used since 2026-09-09")
    p.add_argument("--socket-x", type=float, default=SOCKET_A2[0])
    p.add_argument("--socket-y", type=float, default=SOCKET_A2[1])
    p.add_argument("--drop-dx", type=float, default=-6.0,
                   help="release column offset; -6.0 is what every September reseat used")
    p.add_argument("--floor", type=float, default=108.0,
                   help="lowest nozzle Z accepted until raised or lowered by command")
    p.add_argument("--timeout", type=float, default=600.0,
                   help="seconds of silence before it sets the enclosure down by itself")
    p.add_argument("--link-wait", type=float, default=2700.0)
    p.add_argument("--lights", choices=("on", "off", "leave"), default="on")
    args = p.parse_args()
    cal = Cal(args)
    cal.log(f"start: socket {cal.socket} target {cal.target} press {cal.press_z} "
            f"release {cal.release_z} drop {cal.drop} floor {cal.floor}")
    try:
        cal.run()
    except Exception:  # noqa: BLE001
        cal.log("ERROR:\n" + traceback.format_exc())
        cal.last_note = "ERROR -- see log.txt"
        cal.save_state()
        if cal.phase == "press" and cal.pos:
            cal.log("error while pressed into the socket: backing out")
            try:
                cal.back_out()
            except Exception:  # noqa: BLE001
                cal.log("back-out failed:\n" + traceback.format_exc())
        elif cal.aboard and cal.pos:
            cal.log("attempting to set the enclosure down after the error")
            try:
                if cal.phase in ("release", "release?"):
                    cal.log("error during the release: holding still")
                else:
                    cal.set_down()
            except Exception:  # noqa: BLE001
                cal.log("recovery failed:\n" + traceback.format_exc())
    finally:
        if not cal.aboard:
            cal.finish()
        else:
            cal.log("ENCLOSURE MAY STILL BE ON THE NOZZLE -- maintenance run left open")
            cal.save_state()
    return 0


if __name__ == "__main__":
    sys.exit(main())
