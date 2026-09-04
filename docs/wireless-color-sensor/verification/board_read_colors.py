# Read the AS7341 dark, then under its own LED, then dark again.
# Single I2C init on purpose: re-muxing I2C0 latches the bus so that scan()
# keeps ACKing while every register read returns OSError(5).
import time
from machine import Pin, I2C
from as7341_sensor import Sensor

CHAN = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
print("i2c scan:", [hex(a) for a in i2c.scan()])

def row(label, vals):
    print("%-14s %s  total=%d" % (label, " ".join("%6d" % v for v in vals), sum(vals)))

print("\n%-14s %s" % ("", " ".join("%6s" % c[2:] for c in CHAN)))
for gain in (4,):
    s = Sensor(i2c=i2c, gain=gain)
    s.LED = False
    time.sleep(0.5)
    dark = list(s.all_channels)
    row("dark g%d" % gain, dark)
    s.LED = True
    time.sleep(1.0)
    lit = list(s.all_channels)
    row("LED-ON g%d" % gain, lit)
    s.LED = False
    time.sleep(0.5)
    dark2 = list(s.all_channels)
    row("dark again", dark2)
    sat = sum(1 for v in lit if v >= 65535)
    print("\nratio lit/dark = %.1fx    saturated channels = %d/8" % (
        (sum(lit) + 1) / (sum(dark) + 1), sat))
