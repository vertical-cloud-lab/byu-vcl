"""Hardware-free tests for the color-sensor read scripts.

Run with ``python test_sensor_scripts.py`` (no pytest needed). These stub out
the AS7341 driver and the serial port, so they check the parts that are easy to
get wrong without a board on the bench:

* the SMUX two-pass channel mapping and which pass's Clear/NIR is kept,
* gain -> AGAIN register code, integration time, basic-counts normalisation,
* that the LED is switched back off after a lit reading,
* the MicroPython raw-REPL framing in ``collect_over_serial.py`` (this caught a
  real bug: a single read often returns the whole ``OK...\\x04...\\x04>`` frame,
  so bytes past the first token must be carried over, not discarded).

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


if __name__ == "__main__":
    test_pico_measure()
    test_collect_over_serial()
    print("all tests passed")
