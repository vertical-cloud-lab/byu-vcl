#!/usr/bin/env python3
"""Test sensor_settings.py and main.py.patch without the board.

    python3 test_sensor_settings.py

1. sensor_settings on its own, against a fake AS7341 that behaves like
   as7341.py: set_again() ignores codes outside 0-10, and the bulk read latches
   ASTATUS (gain code, saturation) beside the counts.
2. The real upstream main.py (AccelerationConsortium/wireless-color-sensor at a
   pinned commit), patched with main.py.patch, its message handler driven with
   fake MQTT messages: no settings, gain 512 with a shorter integration, bad
   settings, and a read that fails. Needs network for the one download.

Exits non-zero on the first failure.
"""
import asyncio
import io
import json
import os
import subprocess
import sys
import tempfile
import traceback
import types
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sensor_settings as ss  # noqa: E402

UPSTREAM_SHA = "07efedd7302bd1def93ef81ceadba38e1ae96853"
UPSTREAM = ("https://raw.githubusercontent.com/AccelerationConsortium/wireless-color-sensor/"
            f"{UPSTREAM_SHA}/sensor_file/main.py")
GAINS = ss.GAINS
failures = 0


def check(name, ok, detail=""):
    global failures
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))
    if not ok:
        failures += 1


class FakeChip:
    """The parts of as7341.AS7341 that main.py and sensor_settings touch."""

    def __init__(self, light=1000.0, fail=False):
        self.again, self.atime, self.astep = 9, 0, 999       # power-on: AGAIN 256x
        self.light, self.fail = light, fail
        self.measured = []                                   # (selection, again, atime, astep)
        self._AS7341__buffer13 = bytearray(13)               # CPython spelling of __buffer13

    def set_again(self, code):
        if 0 <= code <= 10:                                  # as7341.py: silently ignores the rest
            self.again = code

    def get_again(self):
        return self.again

    def set_atime(self, v):
        self.atime = v

    def set_astep(self, v):
        if 0 <= v <= 65534:
            self.astep = v

    def start_measure(self, selection):
        if self.fail:
            raise OSError(5, "EIO")
        self.measured.append((selection, self.again, self.atime, self.astep))

    def get_spectral_data(self):
        scale = GAINS[self.again] * (self.atime + 1) * (self.astep + 1) / (256 * 201 * 1000)
        top = min(65535, (self.atime + 1) * (self.astep + 1))
        raw = [int(self.light * (k + 1) * scale) for k in range(6)]
        sat = any(v > top for v in raw)
        self._AS7341__buffer13[0] = self.again | (0x80 if sat else 0)
        return [min(v, top) for v in raw]


def unit():
    check("parse(None) is the default", ss.parse(None) == ss.DEFAULT)
    check("default gain is the chip's own 256x", ss.DEFAULT["gain"] == 256 and ss.gain_code(256) == 9)
    check("a partial object keeps the other defaults",
          ss.parse({"gain": 512}) == {"gain": 512, "atime": 200, "astep": 999})
    check("gain 0.5 is code 0", ss.gain_code(0.5) == 0)
    for bad in ({"gain": 3}, {"gain": True}, {"atime": 256}, {"atime": 1.5}, {"astep": -1},
                {"astep": 65535}, {"led": 4}, [1, 2], "x"):
        try:
            ss.parse(bad)
            check(f"rejects {bad!r}", False)
        except ValueError:
            check(f"rejects {bad!r}", True)

    chip = FakeChip()
    ss.apply(chip, ss.parse({"gain": 64, "atime": 29, "astep": 599}))
    check("apply writes the code, not the factor", (chip.again, chip.atime, chip.astep) == (7, 29, 599))
    counts, st = ss.read(chip, ss.parse({"gain": 64, "atime": 29, "astep": 599}))
    check("read takes both SMUX halves in order", [m[0] for m in chip.measured] == list(ss.SMUX))
    check("read returns 8 counts", len(counts) == 8)
    check("status reads the gain back from ASTATUS",
          [h["again_code"] for h in st["halves"]] == [7, 7], st["halves"])
    check("integration time is (ATIME+1)(ASTEP+1) x 2.78 us", st["integration_ms"] == 50.04,
          st["integration_ms"])
    hot = FakeChip(light=200000)
    ss.apply(hot, ss.DEFAULT)
    _, st = ss.read(hot, ss.DEFAULT)
    check("saturation is reported", st["saturated"] is True)


def stub_modules(chip):
    m = {}
    machine = types.ModuleType("machine")

    class Pin:
        OUT = 1

        def __init__(self, *a, **k):
            self.v = 0

        def on(self):
            self.v = 1

        def toggle(self):
            self.v ^= 1

        def value(self):
            return self.v
    machine.Pin, machine.I2C, machine.SoftI2C = Pin, (lambda *a, **k: None), (lambda *a, **k: None)
    m["machine"] = machine
    m["neopixel"] = types.SimpleNamespace(NeoPixel=object)
    m["netman"] = types.SimpleNamespace(connectWiFi=lambda *a, **k: None)
    m["ntptime"] = types.SimpleNamespace(settime=lambda: None, timeout=0, host="")
    m["mqtt_as"] = types.SimpleNamespace(MQTTClient=object, config={})
    m["my_secrets"] = types.SimpleNamespace(SSID="s", PASSWORD="p", HIVEMQ_HOST="h",
                                            HIVEMQ_PASSWORD="p", HIVEMQ_USERNAME="u",
                                            COURSE_ID="c", PICO_ID="pico")
    m["uio"] = types.SimpleNamespace(StringIO=io.StringIO)

    class Sensor:            # as7341_sensor.Sensor, including its gain-factor bug
        def __init__(self, atime=200, astep=999, gain=128, i2c=None):
            self.sensor = chip
            chip.set_atime(atime)
            chip.set_astep(astep)
            chip.set_again(gain)

        @property
        def all_channels(self):
            self.sensor.start_measure("F1F4CN")
            a = self.sensor.get_spectral_data()
            self.sensor.start_measure("F5F8CN")
            b = self.sensor.get_spectral_data()
            return a[:4] + b[:4]
    m["as7341_sensor"] = types.SimpleNamespace(Sensor=Sensor)
    m["sensor_settings"] = ss
    for k, v in m.items():
        sys.modules[k] = v


class FakeClient:
    def __init__(self, messages):
        self.messages, self.published = messages, []

    @property
    def queue(self):
        async def gen():
            for t, msg in self.messages:
                yield t.encode(), json.dumps(msg).encode(), False
        return gen()

    async def publish(self, topic, payload):
        self.published.append((topic, json.loads(payload)))


def integration():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "sensor_file"))
        src = urllib.request.urlopen(UPSTREAM, timeout=30).read().replace(b"\r\n", b"\n")
        with open(os.path.join(tmp, "sensor_file", "main.py"), "wb") as fh:
            fh.write(src)
        r = subprocess.run(["patch", "-p1", "--quiet", "-i", os.path.join(HERE, "main.py.patch")],
                           cwd=tmp, capture_output=True, text=True)
        check("main.py.patch applies to upstream " + UPSTREAM_SHA[:7], r.returncode == 0,
              (r.stdout + r.stderr).strip())
        if r.returncode:
            return
        code = open(os.path.join(tmp, "sensor_file", "main.py")).read()
        code = code[:code.index('config["queue_len"]')]       # stop before asyncio.run(main())
        with open(os.path.join(tmp, "hivemq-com-chain.der"), "wb") as fh:
            fh.write(b"x")
        chip = FakeChip()
        stub_modules(chip)
        sys.print_exception = lambda e, f: traceback.print_exception(e, file=f)
        g = {"__name__": "board_main"}
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            out = io.StringIO()
            sys.stdout, real = out, sys.stdout
            try:
                exec(compile(code, "main.py", "exec"), g)
            finally:
                sys.stdout = real
        finally:
            os.chdir(cwd)
        check("after start-up the chip is at 256x, set explicitly", chip.again == 9)
        topic, data = g["command_topic"], g["sensor_data_topic"]
        cmd = {"command": {"R": 0, "Y": 0, "B": 0}}
        msgs = [(topic, {**cmd, "experiment_id": "plain"}),
                (topic, {**cmd, "experiment_id": "hi", "settings": {"gain": 512, "atime": 100}}),
                (topic, {**cmd, "experiment_id": "bad", "settings": {"gain": 300}}),
                (topic, {**cmd, "experiment_id": "after"})]
        client = FakeClient(msgs)
        chip.measured.clear()
        sys.stdout, real = io.StringIO(), sys.stdout
        try:
            asyncio.run(g["messages"](client))
        finally:
            sys.stdout = real
        got = {p["experiment_id"]: p for t, p in client.published if t == data}
        check("every command got exactly one reply", len(client.published) == 4 and set(got) ==
              {"plain", "hi", "bad", "after"}, [p["experiment_id"] for _, p in client.published])
        plain, hi, bad, after = (got.get(k, {}) for k in ("plain", "hi", "bad", "after"))
        check("plain command: 8 channels, read at 256x / 558.8 ms",
              len(plain.get("sensor_data", {})) == 8
              and plain["sensor_settings"]["gain"] == 256
              and plain["sensor_settings"]["integration_ms"] == 558.78
              and [h["again_code"] for h in plain["sensor_settings"]["halves"]] == [9, 9],
              plain.get("sensor_settings"))
        check("settings applied for that reading only: 512x, ATIME 100",
              chip.measured[2:4] == [("F1F4CN", 10, 100, 999), ("F5F8CN", 10, 100, 999)],
              chip.measured[2:4])
        check("reply proves it: ASTATUS gain code 10",
              [h["again_code"] for h in hi.get("sensor_settings", {}).get("halves", [])] == [10, 10])
        check("bad settings: an error reply and no reading",
              "error" in bad and "sensor_data" not in bad and len(chip.measured) == 6,
              bad.get("error"))
        check("the next plain command is back at the defaults",
              chip.measured[4:6] == [("F1F4CN", 9, 200, 999), ("F5F8CN", 9, 200, 999)]
              and plain["sensor_data"] == after.get("sensor_data"), chip.measured[4:6])
        check("old payload fields are kept", plain.get("command") == cmd["command"])

        chip.fail = True
        client = FakeClient([(topic, {**cmd, "experiment_id": "x", "settings": {"gain": 1}})])
        sys.stdout, real = io.StringIO(), sys.stdout
        try:
            asyncio.run(g["messages"](client))
        finally:
            sys.stdout = real
        check("a failed read still puts the defaults back", (chip.again, chip.atime) == (9, 200))


if __name__ == "__main__":
    unit()
    integration()
    print("all passed" if not failures else f"{failures} FAILED")
    sys.exit(1 if failures else 0)
