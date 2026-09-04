"""Sweep the gain and check that the spectral SHAPE holds while magnitude scales.

Run ON the Pico:  mpremote connect /dev/ttyACM0 run board_gain_sweep.py

This is the test that distinguishes a genuine spectral measurement from noise or
a railed ADC: normalised channel fractions should agree across gains. They stop
agreeing once channels clip, which is how you spot saturation without guessing.
"""
from machine import I2C, Pin
from time import sleep
from as7341_sensor import Sensor

NAMES = ["415", "445", "480", "515", "555", "590", "630", "680"]

print("%-6s" % "gain" + "".join("%7s" % n for n in NAMES) + "%9s" % "total")
shapes = {}
for g in [1, 2, 4, 8, 16]:
    s = Sensor(gain=g, i2c=I2C(0, scl=Pin(5), sda=Pin(4)))
    s.LED = True
    sleep(1.0)
    v = s.all_channels
    s.LED = False
    t = sum(v)
    print(
        "%-6d" % g
        + "".join("%7d" % x for x in v)
        + "%9d" % t
        + (" SATURATED" if max(v) >= 65535 else "")
    )
    shapes[g] = [x / t for x in v]
    sleep(0.3)

print("\nnormalised shape (fraction of total) -- should be near-identical:")
print("%-6s" % "gain" + "".join("%7s" % n for n in NAMES))
for g in [1, 2, 4, 8]:
    print("%-6d" % g + "".join("%7.3f" % x for x in shapes[g]))
print(
    "\nmax deviation of gain=8 shape vs gain=2 shape: %.4f"
    % max(abs(a - b) for a, b in zip(shapes[8], shapes[2]))
)
