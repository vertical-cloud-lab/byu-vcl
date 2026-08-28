"""Hardware-free tests for the color-sensor read scripts.

Run with ``python test_sensor_scripts.py`` (no pytest needed). These stub out
the AS7341 driver and the serial port, so they check the parts that are easy to
get wrong without a board on the bench:

* the SMUX two-pass channel mapping and which pass's Clear/NIR is kept,
* gain -> AGAIN register code, integration time, basic-counts normalisation,
* that the LED is switched back off after a lit reading,
* the MicroPython raw-REPL framing in ``collect_over_serial.py`` (this caught a
  real bug: a single read often returns the whole ``OK...\\x04...\\x04>`` frame,
  so bytes past the first token must be carried over, not discarded),
* ``read_and_upload.py``'s validation (S5), colour derivation (S6) and
  document build -- the stages that decide whether a reply becomes a database
  record, and the ones a broken sensor exercises hardest.

The numbers here are synthetic. They prove the plumbing, not the optics.
"""

import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _install_micropython_stubs():
    """Fake ``machine`` and ``as7341`` so the Pico script imports on CPython."""
    machine = types.ModuleType("machine")

    class I2C:
        def __init__(self, *args, **kwargs):
            pass

        def scan(self):
            return [0x39]

    class Pin:
        def __init__(self, *args, **kwargs):
            pass

    machine.I2C, machine.Pin = I2C, Pin
    sys.modules["machine"] = machine

    calls = []
    as7341 = types.ModuleType("as7341")

    class AS7341:
        def __init__(self, i2c):
            self.selection = None

        def isconnected(self):
            return True

        def set_measure_mode(self, mode):
            calls.append(("mode", mode))

        def set_atime(self, value):
            calls.append(("atime", value))

        def set_astep(self, value):
            calls.append(("astep", value))

        def set_again(self, code):
            calls.append(("again_code", code))

        def set_led_current(self, milliamps):
            calls.append(("led", milliamps))

        def start_measure(self, selection):
            self.selection = selection
            calls.append(("measure", selection))

        def get_spectral_data(self):
            if self.selection == "F1F4CN":
                return (99, 294, 470, 756, 5231, 812)
            return (1172, 1507, 1548, 775, 5240, 815)

        def get_flicker_frequency(self):
            calls.append(("flicker",))
            return 120

    as7341.AS7341 = AS7341
    as7341.AS7341_MODE_SPM = 0
    sys.modules["as7341"] = as7341
    return calls


def test_pico_measure():
    calls = _install_micropython_stubs()
    import pico_read_intensity_flicker as pico

    assert pico._gain_code(0.5) == 0
    assert pico._gain_code(128) == 8  # 0.5 * 2**8
    assert pico._gain_code(512) == 10

    reading = pico.measure(led_ma=8, quiet=True)

    # F1-F4 come from the first SMUX pass, F5-F8 from the second.
    assert reading["ch410"] == 99 and reading["ch510"] == 756
    assert reading["ch550"] == 1172 and reading["ch670"] == 775
    # Clear/NIR appear in both passes; the second one is the reported value.
    assert reading["clear"] == 5240 and reading["nir"] == 815
    assert reading["clear_first_pass"] == 5231
    assert reading["flicker_hz"] == 120
    assert reading["saturated"] is False

    t_ms = pico.integration_time_ms()
    assert abs(t_ms - (201 * 1000 * 2.78 / 1000.0)) < 1e-6
    assert abs(reading["basic_counts"]["ch410"] - 99 / (128 * t_ms)) < 1e-6
    assert reading["settings"]["integration_time_ms"] == round(t_ms, 3)

    # The LED must not be left on after a lit reading.
    assert ("led", 8) in calls and ("led", 0) in calls
    staged = [c for c in calls if c[0] in ("measure", "flicker")]
    assert staged == [("measure", "F1F4CN"), ("measure", "F5F8CN"), ("flicker",)]
    print("[PASS] pico measure(): channels, clear/NIR, flicker, normalisation, LED")


def test_collect_over_serial():
    import serial

    readings = [
        {
            "ch410": 99, "ch440": 294, "ch470": 470, "ch510": 756,
            "ch550": 1172, "ch583": 1507, "ch620": 1548, "ch670": 775,
            "clear": 5231, "nir": 812, "flicker_hz": 120,
            "saturated": False, "index": 0,
        },
        {
            "ch410": 101, "ch440": 300, "ch470": 480, "ch510": 760,
            "ch550": 1180, "ch583": 1510, "ch620": 1550, "ch670": 780,
            "clear": 5300, "nir": 820, "flicker_hz": 120,
            "saturated": False, "index": 1,
        },
    ]

    class FakeSerial:
        """A MicroPython board in raw REPL, answering in whole frames."""

        def __init__(self, port, baud, timeout=5.0):
            self.buf = b""
            self.execs = 0

        def write(self, data):
            if b"\x01" in data:  # Ctrl-A
                self.buf += b"raw REPL; CTRL-B to exit\r\n>"
            elif data == b"\x04":  # Ctrl-D: run
                self.execs += 1
                out = b""
                if self.execs == 2:  # 1st exec defines the module, 2nd runs it
                    out = b"I2C devices: 0x39\r\n" + b"".join(
                        b"#WCS# " + json.dumps(r).encode() + b"\r\n"
                        for r in readings
                    )
                self.buf += b"OK" + out + b"\x04" + b"\x04" + b">"

        def read(self, n=1):
            chunk, self.buf = self.buf[:n], self.buf[n:]
            return chunk

        def reset_input_buffer(self):
            pass

        def close(self):
            pass

    serial.Serial = FakeSerial
    import collect_over_serial as collector

    parsed = collector.collect("/dev/fake", n=2, period=0.0, led_ma=0, timeout=10)
    assert len(parsed) == 2
    assert parsed[0]["flicker_hz"] == 120
    assert parsed[1]["clear"] == 5300
    print("[PASS] collect_over_serial(): raw-REPL framing and JSON parsing")




def test_validate_rejects_unusable_readings():
    """S5 is the gate between 'the Pico replied' and 'this is a reading'.

    The firmware publishes whatever the driver returned, so a wedged I2C bus
    produces a perfectly well-formed message full of zeros. Each of these
    cases has been reproduced against the real script; they must stay
    distinguishable so the runbook's failure table keeps meaning what it says.
    """
    import read_and_upload as rau

    good = {"sensor_data": {c: 100 + i for i, c in enumerate(rau.CHANNELS)}}
    counts, problems = rau.stage5_validate(good)
    assert counts is not None and not problems, problems
    assert len(counts) == 8

    zeros = {"sensor_data": {c: 0 for c in rau.CHANNELS}}
    counts, problems = rau.stage5_validate(zeros)
    assert counts is not None
    assert any("not answering on I2C" in p for p in problems), problems

    saturated = {"sensor_data": {c: 65535 for c in rau.CHANNELS}}
    _, problems = rau.stage5_validate(saturated)
    assert any("saturated" in p for p in problems), problems

    missing = {"sensor_data": {"ch410": 5}}
    _, problems = rau.stage5_validate(missing)
    assert any("missing channels" in p for p in problems), problems

    # No sensor_data at all -> hard failure (None), not a warning: there is
    # nothing to store.
    counts, problems = rau.stage5_validate({"error": "I2C read failed"})
    assert counts is None and problems

    print("[PASS] stage5_validate(): zeros, saturation, missing, no-data")


def test_color_separates_the_two_measured_poses():
    """S6 must tell the seated reading from the mid-air one.

    These are the real 2026-08-10 counts. Seated, the aperture is shaded by
    the base and the spectrum peaks at 550 nm; lifted, it sees the warm lab
    lighting and peaks at 620 nm. If the derivation cannot separate those two
    it cannot separate two dye wells either, so this is the cheapest possible
    end-to-end check that the colour maths is wired up correctly.
    """
    import read_and_upload as rau

    seated = {"ch410": 9, "ch440": 9, "ch470": 17, "ch510": 180,
              "ch550": 194, "ch583": 73, "ch620": 70, "ch670": 64}
    midair = {"ch410": 75, "ch440": 273, "ch470": 296, "ch510": 671,
              "ch550": 945, "ch583": 1063, "ch620": 1084, "ch670": 610}

    seated_color = rau.stage6_color(seated)
    midair_color = rau.stage6_color(midair)
    assert seated_color["valid"] and midair_color["valid"]
    assert seated_color["dominant_nm"] == 550
    assert midair_color["dominant_nm"] == 620
    # Lifting the module shifts it decisively toward red on the x chromaticity
    # axis; the exact numbers are uncalibrated, the ordering is not.
    assert midair_color["cie_x"] > seated_color["cie_x"]
    assert seated_color["srgb_hex"] != midair_color["srgb_hex"]

    dark = rau.stage6_color({c: 0 for c in rau.CHANNELS})
    assert dark["valid"] is False

    print("[PASS] stage6_color(): seated vs mid-air separate, dark is invalid")


def test_document_is_idempotent_per_reading():
    """The reading_uid is what makes re-uploading a backfill safe.

    Same reply -> same uid (so S9 updates in place); different counts -> a new
    uid (so a genuinely new reading is never silently overwritten).
    """
    import read_and_upload as rau

    cfg = {"PICO_ID": "test", "HIVEMQ_HOST": "broker.example"}
    counts = {c: 10 for c in rau.CHANNELS}
    trip = {"reply": {"experiment_id": "abc", "command": {"R": 0, "Y": 0, "B": 0}},
            "latency_s": 1.0, "sent_utc": None}

    first = rau.build_document(trip, counts, [], rau.stage6_color(counts),
                               cfg, "t", None)
    second = rau.build_document(trip, counts, [], rau.stage6_color(counts),
                                cfg, "t", None)
    assert first["reading_uid"] == second["reading_uid"]

    changed = dict(counts, ch550=999)
    third = rau.build_document(trip, changed, [], rau.stage6_color(changed),
                               cfg, "t", None)
    assert third["reading_uid"] != first["reading_uid"]

    # A document that failed validation must be flagged, not silently stored
    # as if it were good.
    flagged = rau.build_document(trip, counts, ["saturated"],
                                 rau.stage6_color(counts), cfg, "t", None)
    assert flagged["quality"]["ok"] is False

    print("[PASS] build_document(): stable uid, change-sensitive, flags quality")


if __name__ == "__main__":
    test_pico_measure()
    test_collect_over_serial()
    test_validate_rejects_unusable_readings()
    test_color_separates_the_two_measured_poses()
    test_document_is_idempotent_per_reading()
    print("all tests passed")
