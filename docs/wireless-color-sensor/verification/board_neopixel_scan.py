"""Hunt for a NeoPixel by driving each candidate pin and watching the sensor.

Run ON the Pico:  mpremote connect /dev/ttyACM0 run board_neopixel_scan.py

main.py imports NeoPixel but never instantiates one, and no pin is recorded
anywhere, so the only way to find out whether an illumination source is actually
wired is to drive every pin and see if the AS7341 notices.
"""
from machine import I2C, Pin
from neopixel import NeoPixel
from time import sleep
from as7341_sensor import Sensor

s = Sensor(gain=4, i2c=I2C(0, scl=Pin(5), sda=Pin(4)))
s.LED = False
sleep(0.5)
base = sum(s.all_channels)
print("baseline (all dark) total =", base)

CANDS = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
         16, 17, 18, 19, 20, 21, 22, 26, 27, 28]  # 4 and 5 are the I2C bus
hits = []
for p in CANDS:
    try:
        np = NeoPixel(Pin(p, Pin.OUT), 1)
        np[0] = (255, 0, 0)
        np.write()
        sleep(0.4)
        r = sum(s.all_channels)
        np[0] = (0, 0, 255)
        np.write()
        sleep(0.4)
        b = sum(s.all_channels)
        np[0] = (0, 0, 0)
        np.write()
        if r > base * 1.5 or b > base * 1.5:
            print("  GP%-3d red_tot=%-8d blue_tot=%-8d  <== RESPONDS" % (p, r, b))
            hits.append(p)
    except Exception:
        pass  # pin unusable for NeoPixel output; not a finding
print("candidate NeoPixel pins:", hits)
