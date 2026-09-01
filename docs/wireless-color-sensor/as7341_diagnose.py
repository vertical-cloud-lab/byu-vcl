"""Standalone AS7341 diagnostic for the wireless color sensor (MicroPython, Pico W).

Answers "why is the sensor not reading color?" by walking the chain one link at a
time and printing PASS/FAIL plus the specific remedy for whichever link broke.

Deliberately self-contained: it talks raw I2C to the AS7341 and imports nothing
from ``lib/``. A missing or half-copied ``as7341*.py`` is itself one of the faults
this is meant to find, so depending on those files would hide it.

Run it on the Pico, not on your laptop::

    >>> import as7341_diagnose

If you see ``ImportError: no module named 'machine'`` you are in desktop Python --
the board is not connected and the editor fell back to the local interpreter.

Registers and SMUX sequences follow Rob Hamerling's MicroPython AS7341 driver
(MIT), https://gitlab.com/robhamerling/micropython-as7341, which is what the
reference firmware wraps.
"""

import sys
import time

# --------------------------------------------------------------------------
# Wiring candidates. The Adafruit Proto Under Plate PiCowBell (PID 5905) hard
# wires its STEMMA QT connector to GP4 (SDA) / GP5 (SCL) = I2C bus 0, which is
# what the reference firmware uses. GP26/GP27 is the *default argument* of the
# Sensor class and is a common accidental pick -- see NOTES at the bottom.
# --------------------------------------------------------------------------
I2C_CANDIDATES = [
    (0, 4, 5, "STEMMA QT on the Proto Under Plate (what main.py expects)"),
    (1, 26, 27, "default arg of Sensor() -- header pins AD0/AD1"),
    (1, 2, 3, "alternate I2C1"),
    (0, 8, 9, "alternate I2C0"),
    (1, 6, 7, "alternate I2C1"),
    (0, 16, 17, "alternate I2C0"),
    (1, 18, 19, "alternate I2C1"),
    (0, 20, 21, "alternate I2C0"),
]

ADDR = 0x39
ID_VALUE = 0x24

ENABLE, ATIME, ASTEP, CFG_0, CFG_1, CFG_6 = 0x80, 0x81, 0xCA, 0xA9, 0xAA, 0xAF
STATUS_2, ASTATUS, ID_REG = 0xA3, 0x94, 0x92
CONFIG, LED_REG = 0x70, 0x74  # bank 1

PON, SP_EN, SMUXEN = 0x01, 0x02, 0x10
LOW_POWER, REG_BANK = 0x20, 0x10
AVALID, ASAT = 0x40, 0x80
LED_ACT, LED_SEL = 0x80, 0x08

SMUX = {
    "F1F4CN": b"\x30\x01\x00\x00\x00\x42\x00\x00\x50\x00\x00\x00\x20\x04\x00\x30\x01\x50\x00\x06",
    "F5F8CN": b"\x00\x00\x00\x40\x02\x00\x10\x03\x50\x10\x03\x00\x00\x00\x24\x00\x00\x50\x00\x06",
}
NAMES = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]

# Integration settings matching the reference firmware (~281 ms per half-read).
ATIME_VAL, ASTEP_VAL, GAIN_CODE = 200, 999, 8  # gain code 8 == x128

_fail = []


def _hdr(n, title):
    print()
    print("-" * 68)
    print("STAGE %s -- %s" % (n, title))
    print("-" * 68)


def _pass(msg):
    print("  PASS  " + msg)


def _fail_(stage, msg, remedy):
    """remedy is a list of short lines; each is printed as its own bullet."""
    print("  FAIL  " + msg)
    for line in remedy:
        print(("     -> " + line) if line else "")
    _fail.append(stage)


# --------------------------------------------------------------------------


class Chip:
    """Minimal raw-I2C AS7341 driver, only what the diagnostic needs."""

    def __init__(self, bus):
        self.bus = bus

    def rd(self, reg, n=1):
        return self.bus.readfrom_mem(ADDR, reg, n)

    def wr(self, reg, val):
        self.bus.writeto_mem(ADDR, reg, bytes([val]))
        time.sleep_ms(5)

    def modify(self, reg, mask, on):
        v = self.rd(reg)[0]
        v = (v | mask) if on else (v & ~mask & 0xFF)
        self.wr(reg, v)

    def bank(self, one):
        self.modify(CFG_0, REG_BANK, one)

    def configure(self):
        self.wr(ENABLE, PON)
        time.sleep_ms(50)
        self.wr(ATIME, ATIME_VAL)
        self.bus.writeto_mem(ADDR, ASTEP, bytes([ASTEP_VAL & 0xFF, (ASTEP_VAL >> 8) & 0xFF]))
        time.sleep_ms(20)
        self.wr(CFG_1, GAIN_CODE)

    def led(self, milliamps):
        """Onboard white LED on the Adafruit AS7341 breakout. 0 = off, else 4..20 mA."""
        self.bank(True)
        if 4 <= milliamps <= 20:
            self.modify(CONFIG, LED_SEL, True)
            self.wr(LED_REG, LED_ACT + ((milliamps - 4) // 2))
        else:
            self.modify(CONFIG, LED_SEL, False)
            self.wr(LED_REG, 0)
        self.bank(False)
        time.sleep_ms(150)

    def measure(self, selection, timeout_ms=4000):
        self.modify(CFG_0, LOW_POWER, False)
        self.modify(ENABLE, SP_EN, False)
        self.wr(CFG_6, 0x10)  # SMUX write mode
        self.bus.writeto_mem(ADDR, 0x00, SMUX[selection])
        time.sleep_ms(20)
        self.modify(ENABLE, SMUXEN, True)
        self.modify(ENABLE, SP_EN, True)
        start = time.ticks_ms()
        while not (self.rd(STATUS_2)[0] & AVALID):
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                raise OSError("measurement never completed (AVALID never set)")
            time.sleep_ms(50)
        buf = self.rd(ASTATUS, 13)
        saturated = bool(buf[0] & ASAT)
        vals = [buf[1 + 2 * i] | (buf[2 + 2 * i] << 8) for i in range(6)]
        return vals, saturated

    def all_channels(self):
        a, sat_a = self.measure("F1F4CN")
        b, sat_b = self.measure("F5F8CN")
        return a[:4] + b[:4], (sat_a or sat_b)


# --------------------------------------------------------------------------


def stage0_board():
    _hdr(0, "board identity and firmware variant")
    try:
        import os

        machine_str = os.uname().machine
        release = os.uname().release
    except Exception:
        machine_str, release = "<unknown>", "<unknown>"
    print("  machine : %s" % machine_str)
    print("  release : %s" % release)

    is_w = " W " in (" %s " % machine_str) or "Pico W" in machine_str
    have_net = True
    try:
        import network  # noqa: F401
    except ImportError:
        have_net = False
    have_ssl = True
    try:
        import ssl  # noqa: F401
    except ImportError:
        have_ssl = False

    print("  network module: %s   ssl module: %s" % (have_net, have_ssl))

    if is_w and have_net and have_ssl:
        _pass("Pico W firmware (RPI_PICO_W) -- WiFi and TLS available")
    else:
        _fail_(
            0,
            "this is NOT the Pico W build of MicroPython (banner says '%s')" % machine_str,
            [
                "The non-W build has no network stack and no ssl/tls module -- exactly",
                "the \"ImportError: no module named 'ssl'\" reported in this issue.",
                "Reflash with the RPI_PICO_W .uf2: https://micropython.org/download/RPI_PICO_W/",
                "Hold BOOTSEL, plug in USB, drop the .uf2 onto the RPI-RP2 drive.",
                "If RPI-RP2 never appears, try a different USB cable first -- many",
                "micro-USB cables are charge-only and carry no data lines.",
            ],
        )
    # Colour reads work fine on either build, so keep going regardless.


def stage1_bus():
    _hdr(1, "find the AS7341 on the I2C bus")
    from machine import I2C, Pin

    found = []
    for bus_id, sda, scl, note in I2C_CANDIDATES:
        try:
            bus = I2C(bus_id, scl=Pin(scl), sda=Pin(sda))
            devices = bus.scan()
        except Exception as err:
            print("  I2C(%d) GP%-2d/GP%-2d  -- unusable (%s)" % (bus_id, sda, scl, err))
            continue
        addrs = " ".join("0x%02X" % d for d in devices) or "(nothing)"
        mark = "  <== AS7341" if ADDR in devices else ""
        print("  I2C(%d) SDA=GP%-2d SCL=GP%-2d  %s%s" % (bus_id, sda, scl, addrs, mark))
        if ADDR in devices:
            found.append((bus, bus_id, sda, scl, note))

    if not found:
        _fail_(
            1,
            "no device answered at 0x39 on any candidate pin pair",
            [
                "Nothing is talking on I2C at all. In order of likelihood:",
                "1. The Qwiic/STEMMA QT cable is unplugged at one end.",
                "2. The cable is damaged. These JST-SH cables fail at the crimp and it is",
                "   invisible from outside -- swap in a known-good one. A faulty cable was",
                "   already reported in this thread, so this is not hypothetical.",
                "3. The AS7341 has no 3V3. Measure 3.3 V across its 3V3 and GND pads.",
                "4. SDA/SCL swapped -- only possible if the cable was hand-soldered rather",
                "   than plugged into the under-plate connector.",
                "Nothing below this line can run until 0x39 appears.",
            ],
        )
        return None

    bus, bus_id, sda, scl, note = found[0]
    _pass("AS7341 found at 0x39 on I2C(%d) SDA=GP%d SCL=GP%d" % (bus_id, sda, scl))
    print("        (%s)" % note)
    if (bus_id, sda, scl) != (0, 4, 5):
        print()
        print("  NOTE  main.py hardcodes I2C(0, scl=Pin(5), sda=Pin(4)). Your sensor")
        print("        is on a different bus, so main.py will not find it. Either")
        print("        rewire to the under-plate STEMMA QT connector or change main.py.")
    return bus


def stage2_id(chip):
    _hdr(2, "confirm the chip is really an AS7341")
    try:
        raw = chip.rd(ID_REG)[0]
    except Exception as err:
        _fail_(2, "could not read the ID register: %s" % err, [
            "The device ACKs its address but will not return data. Suspect a marginal",
            "cable or a brown-out -- retry on USB power rather than battery.",
        ])
        return False
    print("  ID register 0x92 = 0x%02X (part number in bits 7..2)" % raw)
    if (raw & ~0x03) & 0xFF == ID_VALUE:
        _pass("part number 0x24 -- genuine AS7341")
        return True
    _fail_(2, "expected 0x24, got 0x%02X" % ((raw & ~0x03) & 0xFF), [
        "Either something else is at 0x39, or the read is corrupted by bus noise.",
        "Try the shorter Qwiic cable -- 200 mm is long for I2C without extra pull-ups.",
    ])
    return False


def stage3_dark(chip):
    _hdr(3, "read all 8 channels in the dark (LED off)")
    chip.configure()
    chip.led(0)
    try:
        vals, saturated = chip.all_channels()
    except Exception as err:
        _fail_(3, "measurement failed: %s" % err, [
            "AVALID never went high -- the chip is powered but never finished a",
            "conversion. Power-cycle the Pico and re-run.",
        ])
        return None
    print("  " + "  ".join("%s=%d" % (n, v) for n, v in zip(NAMES, vals)))
    print("  saturated: %s" % saturated)
    _pass("read completed -- these are your dark/ambient counts")
    return vals


def stage4_lit(chip, dark):
    _hdr(4, "read again with the sensor's own white LED on")
    results = {}
    for milliamps in (4, 10):
        chip.led(milliamps)
        try:
            vals, saturated = chip.all_channels()
        except Exception as err:
            _fail_(4, "measurement at %d mA failed: %s" % (milliamps, err),
                   ["Same cause as a stage 3 failure -- see above."])
            chip.led(0)
            return
        results[milliamps] = (vals, saturated)
        print("  %2d mA: %s%s" % (milliamps,
                                  "  ".join("%s=%d" % (n, v) for n, v in zip(NAMES, vals)),
                                  "   [SATURATED]" if saturated else ""))
    chip.led(0)

    lit = results[10][0]
    if dark is None:
        return
    d_sum, l_sum = sum(dark), sum(lit)
    print()
    print("  total counts: dark=%d  lit=%d" % (d_sum, l_sum))

    if results[10][1] or results[4][1]:
        _fail_(4, "the sensor saturates with the LED on", [
            "Not really a fault -- just too much gain for this much light.",
            "Drop GAIN_CODE at the top of this file from 8 (x128) to 4 or 5 (x8/x16).",
            "Saturated channels are pinned at 65535, which looks a lot like",
            "'not reading color' if you only glance at the numbers.",
        ])
    elif l_sum > d_sum * 3 and l_sum > 500:
        _pass("the sensor responds strongly to light -- the HARDWARE IS FINE")
        print()
        print("  If your own test still shows flat or near-zero numbers, the sensor")
        print("  is working and the problem is that nothing is illuminating the")
        print("  sample. In the reference main.py BOTH light sources are commented")
        print("  out: 'sensor.LED = True' in read_sensor_data() and 'set_color(...)'")
        print("  in run_color_experiment(). Sealed inside the 3D-printed housing")
        print("  there is nothing left to measure. See NOTES at the bottom.")
    elif l_sum <= d_sum * 1.2:
        _fail_(4, "turning the LED on changed nothing", [
            "The chip reads and answers, but sees no light either way.",
            "1. Look at the breakout in a dark room. The white LED is bright and",
            "   obvious -- if it never lights, its trace or the LDR jumper is damaged.",
            "2. Check the housing aperture lines up with the sensor window, and that",
            "   no tape or film is covering it.",
            "3. Take the board OUT of the enclosure and re-run in room light. If the",
            "   counts jump, the enclosure is what is blocking the light.",
        ])
    else:
        _fail_(4, "the LED changes the reading, but only weakly (dark=%d lit=%d)"
               % (d_sum, l_sum), [
                   "Marginal light path. Usually the sensor window is partly occluded by",
                   "the housing, or the LED is dim because the battery is low.",
                   "Re-run on USB power and with the board out of the enclosure.",
               ])


def stage5_ambient(chip):
    _hdr(5, "manual check -- does it discriminate color?")
    print("  Point the sensor at something bright and colored (a phone screen showing")
    print("  full red, then full blue works well) and watch which channels move.")
    print("  Taking 3 samples, 3 seconds apart, LED off:")
    print()
    for i in range(3):
        try:
            vals, _ = chip.all_channels()
        except Exception as err:
            print("  sample %d failed: %s" % (i + 1, err))
            continue
        blue = vals[0] + vals[1]      # ch410 + ch440
        red = vals[6] + vals[7]       # ch620 + ch670
        print("  sample %d: %s" % (i + 1, "  ".join("%s=%d" % (n, v) for n, v in zip(NAMES, vals))))
        print("            blue-ish(410+440)=%d   red-ish(620+670)=%d" % (blue, red))
        time.sleep(3)
    print()
    print("  Red light should lift ch620/ch670; blue light should lift ch410/ch440.")
    print("  If every channel moves together but the ratios never change, the sensor")
    print("  is responding to brightness but not to hue -- that is a different fault")
    print("  from 'no reading at all', and worth reporting as such.")


def main():
    print("=" * 68)
    print("AS7341 wireless color sensor -- diagnostic")
    print("=" * 68)

    stage0_board()

    bus = stage1_bus()
    if bus is None:
        _summary()
        return

    chip = Chip(bus)
    if not stage2_id(chip):
        _summary()
        return

    dark = stage3_dark(chip)
    stage4_lit(chip, dark)
    stage5_ambient(chip)
    _summary()


def _summary():
    print()
    print("=" * 68)
    if _fail:
        print("RESULT: %d stage(s) failed: %s" % (len(_fail), sorted(set(_fail))))
        print("Copy this entire output into the GitHub issue.")
    else:
        print("RESULT: all stages passed -- the sensor reads color correctly.")
        print("If the pipeline still misbehaves, the fault is downstream")
        print("(WiFi / MQTT / database), not in the sensor.")
    print("=" * 68)


main()

# --------------------------------------------------------------------------
# NOTES -- things that look like "the sensor is broken" but are not
#
# 1. NOTHING TURNS THE LIGHT ON. In sensor_file/main.py of the reference repo,
#    read_sensor_data() has `# sensor.LED = True` commented out, and
#    run_color_experiment() has `# set_color(R, Y, B)` commented out. The
#    NeoPixel is only ever driven in response to an MQTT command, and even that
#    call is disabled. Run it standing alone, inside the enclosure, and every
#    channel reads near zero -- correctly, because it is dark in there.
#
# 2. Sensor() DEFAULTS TO THE WRONG PINS. The signature is
#        def __init__(self, atime=200, astep=999, gain=128,
#                     i2c=I2C(1, scl=Pin(27), sda=Pin(26)))
#    so a bare `Sensor()` talks to GP26/GP27, not the GP4/GP5 that the Proto
#    Under Plate's STEMMA QT connector is wired to. It fails with
#    "ExternalDeviceNotFound: Failed to contact AS7341". Always pass the bus:
#        Sensor(i2c=I2C(0, scl=Pin(5), sda=Pin(4)))
#    Worse, that default is evaluated at import time, so merely importing the
#    module claims GP26/GP27 as I2C1 whether you use it or not.
#
# 3. sensor.LED RAISES BEFORE IT IS EVER SET. Sensor.__init__ never assigns
#    self._led_state, so *reading* sensor.LED before writing it raises
#    AttributeError. Assign it first (`sensor.LED = False`) or patch __init__.
#
# 4. MISSING lib/ FILES. as7341.py does `from as7341_smux_select import *`.
#    All of as7341.py, as7341_sensor.py and as7341_smux_select.py must be in
#    /lib on the board or the import fails in a way that looks like a dead sensor.
#
# 5. WRONG FIRMWARE. See stage 0. A banner reading "Raspberry Pi Pico with
#    RP2040" (no W) means the non-W .uf2 is flashed: no network, no ssl.
# --------------------------------------------------------------------------
