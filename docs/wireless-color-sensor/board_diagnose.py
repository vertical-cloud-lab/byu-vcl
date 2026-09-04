"""On-board AS7341 diagnostic for the wireless color sensor.

Run it from a host that drains the serial port, addressing the board by USB
serial so a co-resident Arduino/second Pico can never be opened by mistake:

    ~/.venvs/mpremote/bin/mpremote connect id:e6647c15673a2438 reset
    ~/.venvs/mpremote/bin/mpremote connect id:e6647c15673a2438 run board_diagnose.py

Reset first. Register access is fine from a clean boot, but if anything has
already re-muxed I2C0 onto other pins the bus latches up and every register
read returns OSError(5) while i2c.scan() still ACKs 0x39 -- which looks exactly
like a dead sensor. SoftI2C clears that state; so does a reset.

No credentials, no network, nothing from the cloud side.
"""

from machine import Pin, I2C
from time import sleep

ADDR = 0x39
BANDS = (415, 445, 480, 515, 555, 590, 630, 680)


def stage_1_bus():
    """Find the AS7341 and confirm it is really an AS7341."""
    i2c = I2C(0, scl=Pin(5), sda=Pin(4))  # STEMMA QT on the Proto Under Plate
    found = i2c.scan()
    print("stage 1  I2C0 GP4/GP5 ->", [hex(a) for a in found])
    if ADDR not in found:
        print("  FAIL  nothing at 0x39.")
        print("  -> the JST-SH cable fails at the crimp and it is invisible from")
        print("     outside; swap in a known-good one before suspecting the board.")
        return None
    part = i2c.readfrom_mem(ADDR, 0x92, 1)[0] & 0xFC
    print("  part number register 0x92 = 0x%02x (expect 0x24)" % part)
    print("  PASS" if part == 0x24 else "  FAIL  not an AS7341")
    return i2c if part == 0x24 else None


def stage_2_light(i2c):
    """Does it respond to light at all? This is the question that matters."""
    from as7341_sensor import Sensor

    s = Sensor(i2c=i2c, gain=4)
    s.LED = False  # write before reading: the property has no default
    sleep(0.4)
    dark = s.all_channels
    s.LED = True
    sleep(1.0)
    lit = s.all_channels
    s.LED = False

    print("stage 2  " + " ".join("%6d" % b for b in BANDS))
    print("  dark   " + " ".join("%6d" % c for c in dark) + "   total=%d" % sum(dark))
    print("  lit    " + " ".join("%6d" % c for c in lit) + "   total=%d" % sum(lit))
    ratio = (sum(lit) + 1) / (sum(dark) + 1)
    print("  lit/dark = %.0fx" % ratio)
    if ratio > 3:
        print("  PASS  the sensor reads light. If readings still look empty, the")
        print("        fault is upstream: nothing is illuminating the sample.")
    else:
        print("  FAIL  no response to its own LED.")
    return s


def stage_3_gain(i2c):
    """Pick an exposure. The stock gain=128 pins every channel at full scale."""
    from as7341_sensor import Sensor

    print("stage 3  gain sweep, LED on (full scale is 65535)")
    for g in (2, 4, 8, 16, 128):  # ints only: gain=0.5 hits a driver TypeError
        s = Sensor(i2c=i2c, gain=g)
        s.LED = False
        sleep(0.3)
        s.LED = True
        sleep(0.8)
        ch = s.all_channels
        s.LED = False
        flag = "  SATURATED" if max(ch) >= 65535 else ""
        print("  gain %-4s" % g + " ".join("%6d" % c for c in ch) + flag)
        sleep(0.2)


i2c = stage_1_bus()
if i2c:
    stage_2_light(i2c)
    stage_3_gain(i2c)
