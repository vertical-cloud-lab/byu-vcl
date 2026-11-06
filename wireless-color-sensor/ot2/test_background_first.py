#!/usr/bin/env python3
"""Tests for "every well is read empty before paint goes in" (PR #202, 2026-10-18).

No robot, no camera, no sensor, no network: the drivers run with --simulate in
a scratch folder, against a stand-in ``sensor_read.py`` that answers like the
board. Run from anywhere:

    python3 test_background_first.py

Checks:
  * deck.well_xy is what tip_cal.well_xy always computed, and deck.well_at
    inverts it, only within its tolerance;
  * enclosure_height_cal.py's ``background`` records the well from the
    nozzle's position, marks the rows, and refuses between wells;
  * paint_transfer.backgrounds() counts only rows over the right well of a
    plate in the right slot, meant as a background, and recent;
  * paint_transfer.py will not start without --backgrounds or
    --skip-background-check, dispenses into a well that was read empty, and
    refuses (before moving) to carry paint into one that was not.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILS = []
PASSES = []


def check(name, ok, detail=""):
    (PASSES if ok else FAILS).append(name)
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail and not ok else ""))


# A board that answers the way the AS7341 does: ~440 counts closed on its
# base (and after a release), thousands once off it.
FAKE_SENSOR = '''
import time
CHANNELS = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")
class SensorError(RuntimeError):
    pass
def _iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + ".000Z"
class SensorLink:
    def connect(self):
        return self
    def close(self):
        pass
    def read(self, label="", settings=None, **kw):
        low = any(k in label for k in ("seated", "after_release", "after-release", "homed"))
        ch = dict(zip(CHANNELS, [5, 5, 12, 165, 174, 41, 24, 22] if low
                      else [60, 250, 270, 570, 760, 760, 800, 560]))
        t = time.time()
        out = {"experiment_id": label, "channels": ch, "total": sum(ch.values()),
               "t_request_utc": _iso(t), "t_response_utc": _iso(t)}
        if settings:
            out["sensor_settings"] = dict(settings)
            out["sensor_extra"] = {}
        return out
'''

SCRIPTS = ("enclosure_height_cal.py", "paint_transfer.py", "tip_cal.py", "deck.py",
           "run_xscan_test.py", "live_frame.py", "drive.py")


def scratch(root, name):
    d = os.path.join(root, name)
    os.makedirs(d)
    for s in SCRIPTS:
        shutil.copy(os.path.join(HERE, s), d)
    with open(os.path.join(d, "sensor_read.py"), "w") as fh:
        fh.write(FAKE_SENSOR)
    return d


def drive(d, proc, words, timeout=60):
    """Send one command the way drive.py does and wait for the next WAIT (or exit)."""
    log = os.path.join(d, "log.txt")
    n0 = len(open(log).read().splitlines())
    with open(os.path.join(d, "cmd.tmp"), "w") as fh:
        fh.write(words + "\n")
    os.replace(os.path.join(d, "cmd.tmp"), os.path.join(d, "cmd"))
    t0 = time.time()
    while time.time() - t0 < timeout:
        new = open(log).read().splitlines()[n0:]
        seen = any("CMD:" in ln for ln in new)
        if seen and (any("WAIT (" in ln for ln in new[1:]) or proc.poll() is not None):
            return new
        time.sleep(0.1)
    raise TimeoutError(f"no WAIT after {words!r}")


def wait_ready(d, proc, timeout=60):
    log = os.path.join(d, "log.txt")
    t0 = time.time()
    while time.time() - t0 < timeout:
        if os.path.exists(log) and "WAIT (" in open(log).read():
            return
        if proc.poll() is not None:
            raise RuntimeError(open(log).read() if os.path.exists(log) else "exited")
        time.sleep(0.1)
    raise TimeoutError("driver never waited for a command")


# -- 1. geometry -------------------------------------------------------------
def test_geometry():
    import deck
    import tip_cal
    rows = "ABCDEFGH"
    same = all(abs(tip_cal.well_xy(s, f"{r}{c}")[i]
                   - deck.in_slot(s, 14.38 + 9.0 * (c - 1), 74.24 - 9.0 * rows.index(r))[i]) < 1e-9
               for s in (1, 6, 7) for r in rows for c in range(1, 13) for i in (0, 1))
    check("well_xy unchanged (288 wells, slots 1/6/7)", same)
    inverse = all(deck.well_at(7, *deck.well_xy(7, f"{r}{c}")) == f"{r}{c}"
                  for r in rows for c in range(1, 13))
    check("well_at inverts well_xy (slot 7)", inverse)
    x, y = deck.well_xy(7, "F3")
    check("well_at: 0.6 mm off centre is no well", deck.well_at(7, x + 0.6, y) is None
          and deck.well_at(7, x, y - 0.6) is None)
    check("well_at: tol=3 accepts a tip 2.9 mm off centre", deck.well_at(7, x + 2.9, y, tol=3.0) == "F3")
    check("well_at: the base's socket is no plate well", deck.well_at(7, 92.8, 316.5) is None)
    bad = []
    for name in ("Z1", "A0", "A13", "I1", "", "A", "Ax"):
        try:
            deck.well_xy(7, name)
            bad.append(name)
        except ValueError:
            pass
    check("well_xy refuses names that aren't wells", not bad, f"accepted {bad}")


# -- 2. backgrounds() filter -------------------------------------------------
def test_filter(root):
    import paint_transfer as pt
    now = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)

    def row(**kw):
        t = kw.pop("t", now - timedelta(minutes=30))
        r = {"label": "empty-F3", "well": "F3", "plate_slot": 7, "role": "background",
             "pos": [32.38, 210.24, 92.0], "total": 4000,
             "t_response_utc": t.strftime("%Y-%m-%dT%H:%M:%S.000Z")}
        r.update(kw)
        return json.dumps(r)
    path = os.path.join(root, "filter.jsonl")
    with open(path, "w") as fh:
        fh.write("\n".join([
            row(),                                                   # counts (F3)
            row(role=None, label="empty-F6", well="F6"),             # 10-14 style tag: counts
            row(role=None, label="z92", well="F9"),                  # an ordinary step read: no
            row(well="F12", plate_slot=1),                           # another slot: no
            row(well="H7", t=now - timedelta(hours=13)),             # 13 h old: no
            row(well=None, label="empty-F5"),                        # not over a well: no
            row(role=None, label="empty-F3", well="F4"),             # tag and position disagree: no
            "not json",
        ]) + "\n")
    got = pt.backgrounds([path, os.path.join(root, "missing.jsonl")], 7, 12.0, now=now)
    check("backgrounds(): only F3 and F6 count", sorted(got) == ["F3", "F6"], sorted(got))
    check("backgrounds(): z comes from the nozzle position", got.get("F3", [{}])[0].get("z") == 92.0)


# -- 3. the enclosure trip: background rows ------------------------------------
def test_enclosure(root):
    d = scratch(root, "enc")
    proc = subprocess.Popen(
        [sys.executable, "enclosure_height_cal.py", "--simulate", "--no-live", "--plate-slot", "7",
         "--target-x", "86.38", "--target-y", "210.24", "--press-z", "89.0", "--floor", "91",
         "--clear-z", "90", "--timeout", "120"],
        cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    try:
        wait_ready(d, proc)
        for w in ("pickup", "down 97", "down 95", "down 93", "down 91", "down 89", "lift",
                  "carry", "z 92"):
            drive(d, proc, w)
        out = drive(d, proc, "background")                     # over F9
        check("background over F9 is taken", any("background F9 at z 92" in ln for ln in out),
              out[-3:])
        drive(d, proc, "z 125")
        drive(d, proc, "xy 59.38 210.24")                     # F6
        drive(d, proc, "z 92")
        drive(d, proc, "background 2 gain=4")
        drive(d, proc, "read 2 plain")
        drive(d, proc, "z 125")
        drive(d, proc, "xy 64.0 210.24")                      # between F6 and F7
        drive(d, proc, "z 92")
        out = drive(d, proc, "background")
        check("background between wells is refused",
              any("REFUSED: background only centred over a plate well" in ln for ln in out), out[-3:])
        drive(d, proc, "z 125")
        drive(d, proc, "return")            # sets it down, homes and exits by itself
        proc.wait(timeout=60)
        check("the trip ends seated and closed", "maintenance run closed; exiting"
              in open(os.path.join(d, "log.txt")).read())
    finally:
        if proc.poll() is None:
            proc.terminate()
    rows = [json.loads(ln) for ln in open(os.path.join(d, "readings.jsonl"))]
    bg = [r for r in rows if r.get("role") == "background"]
    check("4 + 2 background rows", len(bg) == 6, len(bg))
    check("background rows: well from position, tag empty-<well>, plate slot 7",
          sorted({(r["well"], r["label"], r["plate_slot"]) for r in bg})
          == [("F6", "empty-F6", 7), ("F9", "empty-F9", 7)])
    check("background rows keep their settings", all(r.get("settings") == {"gain": 4}
                                                      for r in bg if r["well"] == "F6"))
    plain = [r for r in rows if r["label"] == "plain"]
    check("an ordinary read over F6 gets well F6 and no role",
          len(plain) == 2 and all(r["well"] == "F6" and "role" not in r for r in plain))
    seated = [r for r in rows if r["label"] == "seated"]
    check("readings off the plate get well None", seated and all(r["well"] is None for r in seated))
    return os.path.join(d, "readings.jsonl")


# -- 4. paint_transfer.py: the guard ----------------------------------------
def test_transfer(root, readings):
    d = scratch(root, "paint")
    base = [sys.executable, "paint_transfer.py", "--simulate", "--plate-slot", "7", "--timeout", "120"]
    r = subprocess.run(base, cwd=d, capture_output=True, text=True)
    check("paint_transfer.py won't start without --backgrounds or --skip-background-check",
          r.returncode == 2 and "read empty first" in r.stderr, r.stderr[-200:])
    r = subprocess.run(base + ["--backgrounds", "nope.jsonl"], cwd=d, capture_output=True, text=True)
    check("a missing --backgrounds file is an error", r.returncode == 2 and "no such file" in r.stderr)

    proc = subprocess.Popen(base + ["--backgrounds", readings], cwd=d,
                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    vial = "326.4 39.4"
    load = ["pickup", f"tip {vial} 80", "prep", f"tip {vial} 70", f"tip {vial} 60",
            f"tip {vial} 50", f"tip {vial} 40", f"tip {vial} 30"]
    try:
        wait_ready(d, proc)
        log = open(os.path.join(d, "log.txt")).read()
        check("start-up lists the wells read empty", "F6 (2)" in log and "F9 (4)" in log)
        drive(d, proc, "tiphover A1 10")
        for w in load + ["aspirate 200", "up"]:
            drive(d, proc, w)
        out = drive(d, proc, "well F6 10")
        check("loaded tip into F6 (read empty): allowed, background logged",
              any("F6: 2 empty-well background reading(s)" in ln for ln in out)
              and not any("REFUSED" in ln for ln in out), out[-3:])
        for h in ("5", "0", "-4", "-8"):
            drive(d, proc, f"well F6 {h}")
        out = drive(d, proc, "dispense")
        check("dispense into F6", any("dispensed 200 uL at 30 uL/s into F6" in ln for ln in out), out[-3:])
        for w in ("blowout", "up", "trash"):
            drive(d, proc, w)
        drive(d, proc, "tiphover B1 10")
        for w in load + ["aspirate 100", "up"]:
            drive(d, proc, w)
        out = drive(d, proc, "well F3 10")
        st = json.load(open(os.path.join(d, "state.json")))
        check("loaded tip into F3 (never read empty): refused before moving",
              any("REFUSED: F3 has no empty-well background" in ln for ln in out)
              and st["pos"][2] >= 109.9, (out[-2:], st["pos"]))
        drive(d, proc, "trash")
        drive(d, proc, "quit")
        proc.wait(timeout=60)
    finally:
        if proc.poll() is None:
            proc.terminate()

    # dispense itself checks the well under the tip, however the tip got there
    import argparse
    import paint_transfer as pt
    args = argparse.Namespace(rack_slot=6, plate_slot=7, travel_z=110.0, rim_z=61.0, nudge_z=70.0,
                              max_down=10.0, vial_floor=20.0, timeout=5.0, simulate=True,
                              backgrounds=[readings], background_max_age_h=12.0,
                              skip_background_check=False, well="A1")
    # tip_cal keeps its log and state beside itself; point them at the scratch folder
    pt.tip_cal.LOGFILE = os.path.join(d, "log.txt")
    pt.tip_cal.STATE = os.path.join(d, "state.json")
    cwd = os.getcwd()
    os.chdir(d)
    try:
        tr = pt.Transfer(args)
        tr.robot.pipette_id = "simulated-pipette"
        x, y = pt.tip_cal.deck.well_xy(7, "F12")
        tr.tip, tr.aspirated, tr.pos = True, 100.0, [x, y, 6.22]
        try:
            tr.dispense_all(30.0)
            check("dispense_all refuses a well never read empty (F12)", False, "dispensed")
        except ValueError as exc:
            check("dispense_all refuses a well never read empty (F12)", "F12 has no" in str(exc))
        tr.pos = [x + 4.5, y, 6.22]                          # between F12 and the plate edge
        try:
            tr.dispense_all(30.0)
            check("dispense_all refuses between wells", False, "dispensed")
        except ValueError as exc:
            check("dispense_all refuses between wells", "inside a plate well" in str(exc))
        args.skip_background_check = True
        tr.pos = [x, y, 6.22]
        tr.dispense_all(30.0)
        check("--skip-background-check dispenses, and says so",
              "no empty-well background check" in open("log.txt").read())
    finally:
        os.chdir(cwd)


def main():
    root = tempfile.mkdtemp(prefix="bgfirst-")
    try:
        test_geometry()
        test_filter(root)
        readings = test_enclosure(root)
        test_transfer(root, readings)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"\n{len(PASSES)} passed, {len(FAILS)} failed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
