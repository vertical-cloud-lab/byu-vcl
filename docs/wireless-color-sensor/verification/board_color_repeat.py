"""Repeated AS7341 read: dark / LED-lit / dark again, three trials.

Run ON the Pico:  mpremote connect /dev/ttyACM0 run board_color_repeat.py

Needs no credentials and no network, so it works on a bench. Reading the same
value back after the LED goes off is the point -- it separates a real optical
response from a drifting baseline.
"""
from machine import I2C, Pin
from time import sleep
from as7341_sensor import Sensor

NAMES = ["415", "445", "480", "515", "555", "590", "630", "680"]

# gain=4 keeps every channel off the 65535 rail while the LED is on.
# The driver default (gain=8) saturates -- see board_gain_sweep.py.
s = Sensor(gain=4, i2c=I2C(0, scl=Pin(5), sda=Pin(4)))


def row(tag, v):
    print("%-11s" % tag + "".join("%7d" % x for x in v) + "   tot=%d" % sum(v))


print("%-11s" % "chan" + "".join("%7s" % n for n in NAMES))
for trial in range(3):
    print("--- trial %d ---" % (trial + 1))
    s.LED = False
    sleep(1)
    row("dark", s.all_channels)
    s.LED = True
    sleep(1)
    row("led_on", s.all_channels)
    s.LED = False
    sleep(1)
    row("dark_again", s.all_channels)
print("DONE")
