# led_hold.py -- run from RAM with `mpremote run`: LED on at 4 mA for 20 s, then off.
import json
import time
from machine import I2C, Pin
from as7341_sensor import Sensor

sensor = Sensor(i2c=I2C(0, scl=Pin(5), sda=Pin(4)))
chip = sensor.sensor
try:
    chip.set_led_current(4)
    print(json.dumps({"event": "on", "mA": 4, "ms": time.ticks_ms()}))
    time.sleep(20)
finally:
    chip.set_led_current(0)
    print(json.dumps({"event": "off", "ms": time.ticks_ms()}))
