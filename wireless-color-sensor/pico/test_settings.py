#!/usr/bin/env python3
"""Test the per-reading settings in main.py (gain, ATIME, ASTEP, LED) without the board.

    python3 test_settings.py

1. main.py.settings.patch turns the gain-only main.py that was on the board on
   2026-10-10 (board-2026-10-10/main.py) into main.py, byte for byte.
2. read_settings() accepts every valid gain, ATIME, ASTEP and LED current and
   refuses everything else.
3. main.py is run under CPython with the MicroPython modules stubbed (the same
   harness as test_gain.py) and a fake AS7341 that also has the board driver's
   set_led_current(): 4-20 mA turns the LED on, anything else turns it off, and
   counts scale with gain, integration time and LED current. Its message
   handler is driven with fake MQTT messages, and the chip records the gain,
   timing and LED state of every half-reading, so the checks can see that each
   setting applied to its own reading only and that the defaults came back
   after it -- including after a failed read with the LED on.

Needs no network. Exits non-zero on any failure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_gain as tg  # noqa: E402  (the stubs, fake MQTT client and check())

GAIN_ONLY = os.path.join(HERE, "board-2026-10-10", "main.py")
AFTER = os.path.join(HERE, "main.py")
PATCH = os.path.join(HERE, "main.py.settings.patch")
check = tg.check


class LedChip(tg.FakeChip):
    """FakeChip plus lib/as7341.AS7341.set_led_current(), as the board's driver has it."""

    def __init__(self, light=1000.0, led_light=3000.0):
        super().__init__(light)
        self.led, self.led_light, self.led_calls = 0, led_light, []

    def set_led_current(self, current):
        self.led = current if 4 <= current <= 20 else 0       # the driver: else LED off
        self.led_calls.append(current)

    def start_measure(self, selection):
        super().start_measure(selection)
        self.measured[-1] = self.measured[-1] + (self.led,)

    def get_spectral_data(self):
        light = self.light
        self.light = light + self.led_light * self.led / 4
        try:
            return super().get_spectral_data()
        finally:
            self.light = light


def patch_applies():
    import shutil
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(GAIN_ONLY, os.path.join(tmp, "main.py"))
        r = subprocess.run(["patch", "-p1", "--quiet", "-i", PATCH], cwd=tmp, capture_output=True, text=True)
        same = r.returncode == 0 and open(os.path.join(tmp, "main.py"), "rb").read() == open(AFTER, "rb").read()
        check("main.py.settings.patch turns the board's gain-only main.py into main.py", same,
              (r.stdout + r.stderr).strip())


def unit():
    rs = tg.boot(AFTER, LedChip())["read_settings"]
    check("no settings -> 128x, ATIME 100, ASTEP 999, LED off", rs(None) == (8, 100, 999, 0))
    check("empty settings -> the same", rs({}) == (8, 100, 999, 0))
    check("every gain maps to its code", [rs({"gain": x})[0] for x in tg.GAINS] == list(range(11)))
    check("ATIME 0 and 255, ASTEP 0 and 4999 accepted",
          rs({"atime": 0})[1] == 0 and rs({"atime": 255, "astep": 999})[1:3] == (255, 999)
          and rs({"astep": 0})[2] == 0 and rs({"atime": 100, "astep": 4999})[2] == 4999)
    check("every even LED current from 4 to 20 mA, and 0, accepted",
          [rs({"led_ma": m})[3] for m in (0, 4, 6, 8, 10, 12, 14, 16, 18, 20)] == [0, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    check("all four at once", rs({"gain": 4, "atime": 29, "astep": 599, "led_ma": 20}) == (3, 29, 599, 20))
    for bad in ({"gain": 3}, {"gain": True}, {"atime": 256}, {"atime": -1}, {"atime": 50.0},
                {"atime": True}, {"atime": "100"}, {"astep": 65535}, {"astep": None},
                {"atime": 255, "astep": 5999},                 # 4.3 s per half
                {"atime": 100, "astep": 5342},                 # 1500.4 ms, just over
                {"led_ma": 2}, {"led_ma": 3}, {"led_ma": 5}, {"led_ma": 22}, {"led_ma": 258},
                {"led_ma": True}, {"led_ma": 4.0}, {"led": 4}, {"az": 1}, [512], "x", 512):
        try:
            rs(bad)
            check(f"refuses {bad!r}", False)
        except ValueError:
            check(f"refuses {bad!r}", True)


def integration():
    cmd = {"command": {"R": 0, "Y": 0, "B": 0}}

    ref_chip = LedChip()
    ref = tg.boot(GAIN_ONLY, ref_chip)
    ref_reply, _ = tg.drive(ref, [{**cmd, "experiment_id": "plain"},
                                  {**cmd, "experiment_id": "g512", "settings": {"gain": 512}}])

    chip = LedChip()
    g = tg.boot(AFTER, chip)
    check("start-up leaves the chip at 128x, ATIME 100, ASTEP 999, LED never touched",
          (chip.again, chip.atime, chip.astep, chip.led, chip.led_calls) == (8, 100, 999, 0, []))
    writes_at_boot = list(chip.timing_writes)
    chip.measured.clear()
    msgs = [{**cmd, "experiment_id": "plain"},
            {**cmd, "experiment_id": "g512", "settings": {"gain": 512}},
            {**cmd, "experiment_id": "at50", "settings": {"atime": 50}},
            {**cmd, "experiment_id": "as499", "settings": {"astep": 499}},
            {**cmd, "experiment_id": "led10", "settings": {"led_ma": 10}},
            {**cmd, "experiment_id": "all", "settings": {"gain": 4, "atime": 29, "astep": 599, "led_ma": 20}},
            {**cmd, "experiment_id": "led0", "settings": {"led_ma": 0}},
            {**cmd, "experiment_id": "bad-led", "settings": {"led_ma": 30}},
            {**cmd, "experiment_id": "bad-key", "settings": {"led": 4}},
            {**cmd, "experiment_id": "bad-long", "settings": {"atime": 255, "astep": 65534}},
            {**cmd, "experiment_id": "after"}]
    got, client = tg.drive(g, msgs)
    check("one reply per command", len(client.published) == len(msgs), [p["experiment_id"] for _, p in client.published])
    halves = [m[1:] for m in chip.measured]
    want = [(8, 100, 999, 0)] * 2 + [(10, 100, 999, 0)] * 2 + [(8, 50, 999, 0)] * 2 + [(8, 100, 499, 0)] * 2 \
        + [(8, 100, 999, 10)] * 2 + [(3, 29, 599, 20)] * 2 + [(8, 100, 999, 0)] * 2 + [(8, 100, 999, 0)] * 2
    check("each reading at its own gain, ATIME, ASTEP and LED, both halves", halves == want, halves)
    check("the LED was on only during the readings that asked for it, and is off now",
          chip.led == 0 and chip.led_calls == [10, 0, 20, 0], chip.led_calls)
    check("defaults are back after the run", (chip.again, chip.atime, chip.astep) == (8, 100, 999))
    timing = chip.timing_writes[len(writes_at_boot):]
    check("timing is written only for readings that change it, and put back each time",
          timing == [("atime", 50), ("astep", 999), ("atime", 100), ("astep", 999),
                     ("atime", 100), ("astep", 499), ("atime", 100), ("astep", 999),
                     ("atime", 29), ("astep", 599), ("atime", 100), ("astep", 999)], timing)

    plain = got["plain"]
    check("a plain read gives exactly the gain-only main.py's counts",
          plain["sensor_data"] == ref_reply["plain"]["sensor_data"]
          and got["g512"]["sensor_data"] == ref_reply["g512"]["sensor_data"])
    check("a plain read's settings say 128x, 280.8 ms, LED off",
          plain["sensor_settings"] == {"gain": 128, "again_code": 8, "analog_saturated": False, "atime": 100,
                                       "astep": 999, "integration_ms": 280.8, "full_scale": 65535, "led_ma": 0},
          plain["sensor_settings"])
    old = ref_reply["plain"]
    check("replies keep every field the gain-only firmware sent; the only new field is sensor_extra",
          set(plain) - set(old) == {"sensor_extra"}
          and all(plain[k] == old[k] for k in old if k != "sensor_settings")
          and all(plain["sensor_settings"][k] == v for k, v in old["sensor_settings"].items()))
    check("sensor_extra has both halves' Clear and NIR",
          set(plain["sensor_extra"]) == {"clear", "nir"} and all(len(v) == 2 for v in plain["sensor_extra"].values()),
          plain["sensor_extra"])
    s = got["all"]["sensor_settings"]
    check("the combined reading reports what it used",
          (s["gain"], s["again_code"], s["atime"], s["astep"], s["led_ma"], s["full_scale"]) == (4, 3, 29, 599, 20, 18000)
          and s["integration_ms"] == 50.0, s)
    check("half the ATIME (51 steps) reads about half the counts",
          all(abs(got["at50"]["sensor_data"][c] - plain["sensor_data"][c] * 51 / 101) <= 1 for c in plain["sensor_data"]))
    check("LED at 10 mA adds light; LED 0 reads like a plain read",
          all(got["led10"]["sensor_data"][c] > plain["sensor_data"][c] for c in plain["sensor_data"])
          and got["led0"]["sensor_data"] == plain["sensor_data"])
    for k in ("bad-led", "bad-key", "bad-long"):
        p = got.get(k, {})
        check(f"{k}: error reply, no reading", "error" in p and "sensor_data" not in p, p.get("error"))
    check("plain reads are identical before and after", plain["sensor_data"] == got["after"]["sensor_data"])

    chip.fail_next = 1
    got, _ = tg.drive(g, [{**cmd, "experiment_id": "boom", "settings": {"led_ma": 20, "atime": 10, "gain": 1}},
                          {**cmd, "experiment_id": "next"}])
    check("a failed read with the LED on: no reply, then LED off and 128x/100/999 back",
          "boom" not in got and chip.led == 0 and (chip.again, chip.atime, chip.astep) == (8, 100, 999), list(got))
    check("and the next command is answered normally",
          got.get("next", {}).get("sensor_settings", {}).get("again_code") == 8)

    chip.status_fails = 1
    got, _ = tg.drive(g, [{**cmd, "experiment_id": "nostatus", "settings": {"gain": 256}}])
    s = got.get("nostatus", {}).get("sensor_settings", {})
    check("a failed status read still sends the reading, with code and saturation unknown",
          len(got.get("nostatus", {}).get("sensor_data", {})) == 8
          and s.get("again_code") is None and s.get("analog_saturated") is None and chip.again == 8, s)

    hot = LedChip(light=20000)
    gh = tg.boot(AFTER, hot)
    got, _ = tg.drive(gh, [{**cmd, "experiment_id": "hot", "settings": {"gain": 512}},
                           {**cmd, "experiment_id": "short", "settings": {"atime": 0, "astep": 9}}])
    check("analog saturation is reported", got["hot"]["sensor_settings"]["analog_saturated"] is True)
    check("full_scale follows the integration: (0+1) x (9+1) = 10 counts",
          got["short"]["sensor_settings"]["full_scale"] == 10)


if __name__ == "__main__":
    patch_applies()
    unit()
    integration()
    print("all passed" if not tg.failures else f"{tg.failures} FAILED")
    sys.exit(1 if tg.failures else 0)
