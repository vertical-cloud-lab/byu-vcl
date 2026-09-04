"""Find GPIO pins that are shorted to ground, without a multimeter.

Run this ON the Pico W when the AS7341 stops answering:

    mpremote connect id:e6647c15673a2438 run board_pin_short_scan.py

No credentials, no network, no imports from /lib -- a missing or broken library
is one of the things this is meant to rule out.

Why a "pull fight" rather than just reading the pin
---------------------------------------------------
A floating input reads whatever charge happens to be on it, so "GP4 reads HIGH"
proves nothing on its own. Instead each pin is read twice, once fighting it with
the RP2040's internal pull-down and once with its internal pull-up. Those are
weak (~50-80k), so whatever is attached wins:

    PULL_DOWN reads 1  ->  a strong external pull-up is out there.
                           On an I2C line that means the breakout is powered and
                           the cable is intact.
    PULL_UP   reads 0  ->  something is holding the line at ground. A few kohm or
                           less -- solder bridge, flux residue, or a slave stuck
                           mid-transaction.
    PULL_UP 1, PULL_DOWN 0 -> nothing attached (floating).

Both I2C lines idling HIGH is the healthy state. One line pulled up and the other
clamped low is the signature of a solder bridge to an adjacent ground pin, and it
stops the bus dead: with SCL held low the master can never clock, so i2c.scan()
comes back empty and every register access returns ETIMEDOUT.
"""

from machine import Pin
from time import sleep_ms

# GPIO -> Pico physical pin, so a fault can be found by eye on the board instead
# of in the datasheet. GP23/24/25 are omitted: on a Pico W they belong to the
# CYW43 radio, not to the header.
PHYS = {0: 1, 1: 2, 2: 4, 3: 5, 4: 6, 5: 7, 6: 9, 7: 10, 8: 11, 9: 12,
        10: 14, 11: 15, 12: 16, 13: 17, 14: 19, 15: 20, 16: 21, 17: 22,
        18: 24, 19: 25, 20: 26, 21: 27, 22: 29, 26: 31, 27: 32, 28: 34}

GND_PINS = (3, 8, 13, 18, 23, 28, 33, 38)

# What the reference wiring puts on which pin, so a hit is immediately meaningful.
ROLE = {4: "I2C0 SDA -> STEMMA QT", 5: "I2C0 SCL -> STEMMA QT"}

REPEATS = 5


def classify(gpio):
    """Return (verdict, pulldown_reads, pullup_reads) for one pin."""
    down, up = [], []
    for _ in range(REPEATS):
        p = Pin(gpio, Pin.IN, Pin.PULL_DOWN)
        sleep_ms(3)
        down.append(p.value())
        p = Pin(gpio, Pin.IN, Pin.PULL_UP)
        sleep_ms(3)
        up.append(p.value())
    Pin(gpio, Pin.IN, None)  # leave it high-impedance

    if all(up) and all(down):
        return "EXTERNAL PULL-UP", down, up
    if all(up) and not any(down):
        return "floating (open)", down, up
    if not any(up):
        return "*** SHORTED TO GND ***", down, up
    return "unstable", down, up


def main():
    print("=== GPIO pull-fight scan (%d reads per pin) ===" % REPEATS)
    print("%-6s %-9s %-24s %-13s %s" % ("GPIO", "phys pin", "verdict", "adj GND pin", "role"))

    shorted, pulled_up = [], []
    for gpio in sorted(PHYS):
        verdict, _, _ = classify(gpio)
        phys = PHYS[gpio]
        adj = ", ".join("%d" % g for g in GND_PINS if abs(g - phys) == 1)
        print("%-6s %-9s %-24s %-13s %s" % (
            "GP%d" % gpio, "pin %d" % phys, verdict, adj, ROLE.get(gpio, "")))
        if "SHORTED" in verdict:
            shorted.append((gpio, phys, adj))
        elif "PULL-UP" in verdict:
            pulled_up.append(gpio)

    print()
    if not shorted:
        print("No pin is shorted to ground.")
        if 4 in pulled_up and 5 in pulled_up:
            print("Both STEMMA QT lines idle HIGH -- the bus looks healthy;")
            print("if the sensor still does not answer, the fault is past the bus.")
        else:
            print("Neither STEMMA QT line shows an external pull-up, so the breakout")
            print("is unpowered or the cable is not seated. Reseat both JST-SH ends.")
        return

    for gpio, phys, adj in shorted:
        print("GP%d (physical pin %d) is held at ground." % (gpio, phys))
        if ROLE.get(gpio):
            print("  This is the %s line." % ROLE[gpio])
        if adj:
            print("  It sits next to physical pin %s, which is ground -- a solder" % adj)
            print("  bridge between those two pads produces exactly this reading.")
        print("  With power off, measure resistance from pin %d to pin %s." % (phys, adj or "GND"))
        print("  A few ohms confirms the bridge; reflow and clean the flux.")

    if 5 in [s[0] for s in shorted] and 4 in pulled_up:
        print()
        print("SDA is pulled up but SCL is clamped: the breakout has power and the")
        print("cable is fine, but the master can never clock. The sensor is not at")
        print("fault. Note that as7341_sensor.Sensor() raises at import time, so")
        print("main.py dies before connectWiFi() and the board never reaches the")
        print("broker either -- a dead I2C line also looks like a dead radio.")


main()
