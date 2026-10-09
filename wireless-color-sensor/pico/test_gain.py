#!/usr/bin/env python3
"""Test the gain-only main.py without the board.

    python3 test_gain.py

1. main.py.gain.patch turns the board's own main.py (board-2026-10-09/main.py,
   copied off the board before the change) into main.py, byte for byte.
2. Both main.py files are run under CPython with the MicroPython modules
   stubbed and a fake AS7341 that behaves like the board's lib/as7341.py
   (set_again() ignores codes outside 0-10; ASTATUS read straight after a
   reading gives its gain code, while the driver's own bulk-read copy shows
   8, as measured on the board on 2026-10-09). Their message handlers are
   driven with fake MQTT messages: plain reads, gains 512 / 0.5 / {}, bad
   settings, a failed read, a failed status read.

Needs no network. Exits non-zero on any failure.
"""
import asyncio
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
import types

HERE = os.path.dirname(os.path.abspath(__file__))
BEFORE = os.path.join(HERE, "board-2026-10-09", "main.py")
AFTER = os.path.join(HERE, "main.py")
GAINS = (0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512)
failures = 0


def check(name, ok, detail=""):
    global failures
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))
    if not ok:
        failures += 1


class FakeChip:
    """The parts of lib/as7341.AS7341 that main.py and Sensor touch."""

    def __init__(self, light=1000.0):
        self.again, self.atime, self.astep = 9, 0, 999       # power-on defaults
        self.light, self.fail_next, self.status_fails = light, 0, 0
        self.astatus = 0
        self.measured = []                                   # (selection, again, atime, astep)
        self.timing_writes = []
        setattr(self, "__buffer13", bytearray(13))           # MicroPython does not mangle

    def set_measure_mode(self, mode):
        pass

    def set_again(self, code):
        if 0 <= code <= 10:                                  # as7341.py ignores the rest
            self.again = code

    def set_atime(self, v):
        self.atime = v
        self.timing_writes.append(("atime", v))

    def set_astep(self, v):
        if 0 <= v <= 65534:
            self.astep = v
        self.timing_writes.append(("astep", v))

    def start_measure(self, selection):
        if self.fail_next:
            self.fail_next -= 1
            raise OSError(5, "EIO")
        self.measured.append((selection, self.again, self.atime, self.astep))

    def get_spectral_data(self):
        scale = GAINS[self.again] * (self.atime + 1) * (self.astep + 1) / (128 * 101 * 1000)
        raw = [int(self.light * (k + 1) * scale) for k in range(6)]
        sat = any(v > 65535 for v in raw)
        getattr(self, "__buffer13")[0] = 8                   # the board's stale copy
        self.astatus = self.again | (0x80 if sat else 0)
        return [min(v, 65535) for v in raw]

    def readfrom_mem(self, addr, reg, n):                    # Sensor.i2c, ASTATUS only
        assert (addr, reg, n) == (0x39, 0x94, 1)
        if self.status_fails:
            self.status_fails -= 1
            raise OSError(5, "EIO")
        return bytes([self.astatus])


def stub_modules(chip):
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

    class Sensor:            # the board's lib/as7341_sensor.Sensor, reduced
        def __init__(self, atime=100, astep=999, gain=8, i2c=None):
            self.sensor = chip
            self.i2c = chip
            chip.set_measure_mode(None)
            chip.set_atime(atime)
            chip.set_astep(astep)
            chip.set_again(gain)

        @property
        def all_channels(self):
            self.sensor.start_measure("F1F4CN")
            f1, f2, f3, f4, clr, nir = self.sensor.get_spectral_data()
            self.sensor.start_measure("F5F8CN")
            f5, f6, f7, f8, clr, nir = self.sensor.get_spectral_data()
            return [f1, f2, f3, f4, f5, f6, f7, f8]

    mods = {
        "machine": machine,
        "neopixel": types.SimpleNamespace(NeoPixel=object),
        "netman": types.SimpleNamespace(connectWiFi=lambda *a, **k: None),
        "ntptime": types.SimpleNamespace(settime=lambda: None, timeout=0, host=""),
        "mqtt_as": types.SimpleNamespace(MQTTClient=object, config={}),
        "my_secrets": types.SimpleNamespace(SSID="s", PASSWORD="p", HIVEMQ_HOST="h",
                                            HIVEMQ_PASSWORD="p", HIVEMQ_USERNAME="u",
                                            COURSE_ID="c", PICO_ID="pico"),
        "uio": types.SimpleNamespace(StringIO=io.StringIO),
        "as7341_sensor": types.SimpleNamespace(Sensor=Sensor),
    }
    sys.modules.update(mods)


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


def boot(path, chip):
    """Run a main.py up to (not including) asyncio.run(main()); return its globals."""
    code = open(path).read()
    code = code[:code.index('config["queue_len"]')]
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "hivemq-com-chain.der"), "wb") as fh:
        fh.write(b"x")
    stub_modules(chip)
    sys.print_exception = lambda e, f: traceback.print_exception(e, file=f)
    g = {"__name__": "board_main"}
    cwd, real = os.getcwd(), sys.stdout
    os.chdir(tmp)
    sys.stdout = io.StringIO()
    try:
        exec(compile(code, path, "exec"), g)
    finally:
        sys.stdout = real
        os.chdir(cwd)
        shutil.rmtree(tmp)
    return g


def drive(g, msgs):
    client = FakeClient([(g["command_topic"], m) for m in msgs])
    real, sys.stdout = sys.stdout, io.StringIO()
    try:
        asyncio.run(g["messages"](client))
    finally:
        sys.stdout = real
    return {p["experiment_id"]: p for t, p in client.published if t == g["sensor_data_topic"]}, client


def patch_applies():
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(BEFORE, os.path.join(tmp, "main.py"))
        r = subprocess.run(["patch", "-p1", "--quiet", "-i", os.path.join(HERE, "main.py.gain.patch")],
                           cwd=tmp, capture_output=True, text=True)
        same = r.returncode == 0 and open(os.path.join(tmp, "main.py"), "rb").read() == open(AFTER, "rb").read()
        check("main.py.gain.patch turns the board's main.py into main.py", same, (r.stdout + r.stderr).strip())


def unit():
    g = boot(AFTER, FakeChip())
    gc = g["gain_code"]
    check("no settings -> code 8 (128x)", gc(None) == 8)
    check("empty settings -> code 8", gc({}) == 8)
    check("every gain maps to its code", [gc({"gain": x}) for x in GAINS] == list(range(11)))
    check("512.0 is accepted as 512", gc({"gain": 512.0}) == 10)
    for bad in ({"gain": 3}, {"gain": 1024}, {"gain": True}, {"gain": "512"}, {"gain": None},
                {"atime": 50}, {"gain": 512, "astep": 10}, {"led": 4}, [512], "x", 512):
        try:
            gc(bad)
            check(f"refuses {bad!r}", False)
        except ValueError:
            check(f"refuses {bad!r}", True)


def integration():
    cmd = {"command": {"R": 0, "Y": 0, "B": 0}}

    old_chip = FakeChip()
    old = boot(BEFORE, old_chip)
    old_reply, _ = drive(old, [{**cmd, "experiment_id": "plain"}])

    chip = FakeChip()
    g = boot(AFTER, chip)
    check("start-up leaves the chip at 128x, ATIME 100, ASTEP 999, as before",
          (chip.again, chip.atime, chip.astep) == (8, 100, 999) == (old_chip.again, old_chip.atime, old_chip.astep))
    chip.measured.clear()
    writes_at_boot = list(chip.timing_writes)
    ids = ["plain", "g512", "g05", "empty", "bad-gain", "bad-key", "bad-bool", "bad-type", "after"]
    msgs = [{**cmd, "experiment_id": "plain"},
            {**cmd, "experiment_id": "g512", "settings": {"gain": 512}},
            {**cmd, "experiment_id": "g05", "settings": {"gain": 0.5}},
            {**cmd, "experiment_id": "empty", "settings": {}},
            {**cmd, "experiment_id": "bad-gain", "settings": {"gain": 300}},
            {**cmd, "experiment_id": "bad-key", "settings": {"atime": 50}},
            {**cmd, "experiment_id": "bad-bool", "settings": {"gain": True}},
            {**cmd, "experiment_id": "bad-type", "settings": "512"},
            {**cmd, "experiment_id": "after"}]
    got, client = drive(g, msgs)
    check("one reply per command", len(client.published) == len(msgs) and set(got) == set(ids),
          [p["experiment_id"] for _, p in client.published])
    halves = [m[1] for m in chip.measured]
    check("each reading at its own gain: 8, 10, 0, 8, 8 (two halves each)",
          halves == [8, 8, 10, 10, 0, 0, 8, 8, 8, 8], halves)
    check("integration time never touched: no ATIME/ASTEP writes after start-up",
          chip.timing_writes == writes_at_boot and all(m[2:] == (100, 999) for m in chip.measured))
    check("default gain is back after the run", chip.again == 8)
    for k, gain, code in (("plain", 128, 8), ("g512", 512, 10), ("g05", 0.5, 0), ("empty", 128, 8), ("after", 128, 8)):
        s = got.get(k, {}).get("sensor_settings")
        check(f"{k}: reply says gain {gain}, chip's own ASTATUS code {code}",
              s == {"gain": gain, "again_code": code, "analog_saturated": False}, s)
    check("512x reads 4x the 128x counts",
          all(got["g512"]["sensor_data"][c] == 4 * got["plain"]["sensor_data"][c]
              for c in got["plain"]["sensor_data"] if got["plain"]["sensor_data"][c] < 16000))
    for k in ("bad-gain", "bad-key", "bad-bool", "bad-type"):
        p = got.get(k, {})
        check(f"{k}: error reply, no reading", "error" in p and "sensor_data" not in p, p.get("error"))
    check("bad settings took no reading", len(chip.measured) == 10)
    plain, after = got["plain"], got["after"]
    check("plain reads are identical before and after the gain changes",
          plain["sensor_data"] == after["sensor_data"])
    check("a plain read matches the old main.py's counts exactly",
          plain["sensor_data"] == old_reply["plain"]["sensor_data"])
    check("the only new reply field is sensor_settings",
          set(plain) - set(old_reply["plain"]) == {"sensor_settings"}
          and all(plain[k] == old_reply["plain"][k] for k in old_reply["plain"]))

    drive(g, [{**cmd, "experiment_id": "alone", "settings": {"gain": 512}}])
    check("128x is put back straight after a 512x reading", chip.again == 8, chip.again)

    chip.fail_next = 1
    got, _ = drive(g, [{**cmd, "experiment_id": "boom", "settings": {"gain": 1}}])
    check("a failed read gets no reply and still puts 128x back", not got and chip.again == 8, chip.again)
    chip.fail_next = 1
    got, client = drive(g, [{**cmd, "experiment_id": "boom2", "settings": {"gain": 1}},
                            {**cmd, "experiment_id": "next"}])
    check("the board carries on after a failed read: the next command is answered at 128x",
          set(got) == {"next"} and got["next"]["sensor_settings"]["again_code"] == 8, list(got))

    chip.status_fails = 1
    got, _ = drive(g, [{**cmd, "experiment_id": "nostatus", "settings": {"gain": 256}}])
    s = got.get("nostatus", {})
    check("a failed status read still sends the reading, with the code unknown",
          len(s.get("sensor_data", {})) == 8
          and s.get("sensor_settings") == {"gain": 256, "again_code": None, "analog_saturated": None}
          and chip.again == 8, s.get("sensor_settings"))

    hot = FakeChip(light=40000)
    gh = boot(AFTER, hot)
    got, _ = drive(gh, [{**cmd, "experiment_id": "hot", "settings": {"gain": 512}}])
    check("analog saturation is reported", got["hot"]["sensor_settings"]["analog_saturated"] is True)


if __name__ == "__main__":
    patch_applies()
    unit()
    integration()
    print("all passed" if not failures else f"{failures} FAILED")
    sys.exit(1 if failures else 0)
