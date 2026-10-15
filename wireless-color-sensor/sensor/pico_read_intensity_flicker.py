"""MicroPython script for the wireless-color-sensor Pico W: intensity + flicker.

Copy this file to the Pico W (alongside the existing ``lib/`` folder from
AccelerationConsortium/wireless-color-sensor ``sensor_file/``) and run it. It
needs **no WiFi and no MQTT** -- it talks to the AS7341 over I2C and prints the
result as JSON on the USB serial REPL, so it works with the Pico tethered to a
laptop (Thonny) or to the RPi-5 (``collect_over_serial.py``).

Why this exists instead of ``as7341_test.py``: the upstream ``Sensor`` wrapper
(``lib/as7341_sensor.py``) returns only the 8 spectral channels and throws away
everything else. This script drives ``lib/as7341.py`` directly so you also get:

* **Clear** (unfiltered, the closest thing the AS7341 has to a broadband
  "light intensity" reading) and **NIR**,
* **flicker frequency** -- ``AS7341.get_flicker_frequency()`` returns 100, 120
  or 0 Hz. This is a mains-flicker detector, not a general frequency counter:
  100 Hz = 50 Hz mains (Europe), 120 Hz = 60 Hz mains (North America, i.e. what
  BYU lab lighting should read), 0 = no flicker detected (DC/daylight/LED
  driven above the detector's band, or too dim to call),
* **basic counts** -- raw counts normalised by gain and integration time, which
  is what you must compare across readings if gain/atime/astep ever change,
* a **saturation flag**, so an over-range reading is not silently reported.

Usage on the Pico::

    >>> import pico_read_intensity_flicker as r
    >>> r.measure()                      # one reading, ambient light
    >>> r.measure(led_ma=8)              # with the onboard LED at 8 mA
    >>> r.run(n=10, period_s=1.0)        # 10 readings, 1 s apart, JSON per line

Each reading prints one line of the form::

    #WCS# {"ch410": 99, ..., "clear": 5231, "nir": 812, "flicker_hz": 120, ...}

The ``#WCS#`` prefix lets a host parse readings out of the REPL chatter without
guessing which lines are data.
"""

import json

from machine import I2C, Pin

from as7341 import AS7341, AS7341_MODE_SPM

# I2C wiring used by the sensor package (same as upstream main.py):
# AS7341 on I2C0, SCL = GP5, SDA = GP4.
I2C_ID = 0
SCL_PIN = 5
SDA_PIN = 4

# Integration/gain defaults, matching lib/as7341_sensor.py so numbers taken
# with this script are directly comparable to the existing demo firmware.
ATIME = 200
ASTEP = 999
GAIN = 128  # ADC gain multiplier (0.5 .. 512)

# The 8 spectral channels, by their nominal centre wavelength in nm.
CHANNEL_NAMES = (
    "ch410",
    "ch440",
    "ch470",
    "ch510",
    "ch550",
    "ch583",
    "ch620",
    "ch670",
)

PREFIX = "#WCS#"  # marker so the host can find data lines in REPL output

_sensor = None


def _gain_code(gain):
    """AGAIN register code for a gain factor (0.5 -> 0 ... 512 -> 10)."""
    code = 0
    value = 0.5
    while value < gain and code < 10:
        value *= 2
        code += 1
    return code


def get_sensor(atime=ATIME, astep=ASTEP, gain=GAIN):
    """Return a configured low-level AS7341 (created once, then reused)."""
    global _sensor
    if _sensor is None:
        i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
        found = " ".join("0x{:02X}".format(x) for x in i2c.scan())
        print("I2C devices:", found)
        sensor = AS7341(i2c)
        if not sensor.isconnected():
            raise OSError("AS7341 not responding on I2C -- check wiring/power")
        sensor.set_measure_mode(AS7341_MODE_SPM)
        sensor.set_atime(atime)
        sensor.set_astep(astep)
        sensor.set_again(_gain_code(gain))
        _sensor = sensor
    return _sensor


def integration_time_ms(atime=ATIME, astep=ASTEP):
    """Integration time in ms: (ATIME + 1) * (ASTEP + 1) * 2.78 us."""
    return (atime + 1) * (astep + 1) * 2.78 / 1000.0


def measure(led_ma=0, atime=ATIME, astep=ASTEP, gain=GAIN, quiet=False):
    """Take one full reading and return it as a dict.

    Parameters
    ----------
    led_ma : int
        Onboard LED drive current in mA. 0 leaves the LED off (ambient-light
        reading). The driver only accepts even values in 4..20; anything else
        is treated as off.
    quiet : bool
        If True, return the dict without printing the ``#WCS#`` line.

    Returns
    -------
    dict
        Channel counts, ``clear``, ``nir``, ``flicker_hz``, normalised
        ``basic_counts``, and the settings the reading was taken with.
    """
    sensor = get_sensor(atime=atime, astep=astep, gain=gain)

    if led_ma:
        sensor.set_led_current(led_ma)

    try:
        # The AS7341 has 6 ADCs, so the 8 spectral channels + clear + NIR are
        # read in two SMUX passes. Clear/NIR appear in both; keep the second.
        sensor.start_measure("F1F4CN")
        f1, f2, f3, f4, clear_a, nir_a = sensor.get_spectral_data()
        sensor.start_measure("F5F8CN")
        f5, f6, f7, f8, clear, nir = sensor.get_spectral_data()

        # Flicker detection reconfigures the SMUX, so run it after the
        # spectral passes.
        flicker_hz = sensor.get_flicker_frequency()
    finally:
        if led_ma:
            sensor.set_led_current(0)

    counts = (f1, f2, f3, f4, f5, f6, f7, f8)
    reading = dict(zip(CHANNEL_NAMES, counts))

    t_ms = integration_time_ms(atime, astep)
    # "Basic counts": raw / (gain x integration time). Required for comparing
    # readings taken at different gain/integration settings.
    norm = float(gain) * t_ms
    reading["clear"] = clear
    reading["nir"] = nir
    reading["clear_first_pass"] = clear_a
    reading["nir_first_pass"] = nir_a
    reading["flicker_hz"] = flicker_hz
    reading["basic_counts"] = {
        name: round(value / norm, 6) for name, value in zip(CHANNEL_NAMES, counts)
    }
    reading["basic_counts"]["clear"] = round(clear / norm, 6)
    # 16-bit ADC: a channel pinned at 65535 means the reading is over-range and
    # the numbers below it are not trustworthy.
    reading["saturated"] = max(list(counts) + [clear, nir]) >= 65535
    reading["settings"] = {
        "atime": atime,
        "astep": astep,
        "gain": gain,
        "integration_time_ms": round(t_ms, 3),
        "led_ma": led_ma,
    }

    if not quiet:
        print(PREFIX, json.dumps(reading))
    return reading


def run(n=1, period_s=1.0, led_ma=0, **kwargs):
    """Take ``n`` readings ``period_s`` apart, printing one JSON line each."""
    from time import sleep

    out = []
    for i in range(n):
        reading = measure(led_ma=led_ma, **kwargs)
        reading["index"] = i
        out.append(reading)
        if i < n - 1:
            sleep(period_s)
    return out


if __name__ == "__main__":
    run(n=1)
