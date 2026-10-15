# led_check.py -- run from RAM with `mpremote run`; writes nothing to flash.
# Turns the AS7341's LED driver (LDR pin) on at 4, 10 and 20 mA -- inside the
# 4-20 mA that lib/as7341.py itself allows -- and reads all channels with the
# LED off, on, and off again, at the board's own settings (Sensor() defaults:
# 128x, ATIME 100, ASTEP 999). Ends with the LED off whatever happens.
import json
import time
from machine import I2C, Pin
from as7341_sensor import Sensor

ADDR = 0x39
sensor = Sensor(i2c=I2C(0, scl=Pin(5), sda=Pin(4)))  # built exactly as main.py does
chip = sensor.sensor
i2c = sensor.i2c


def rd(reg, n=1):
    b = i2c.readfrom_mem(ADDR, reg, n)
    return b[0] if n == 1 else int.from_bytes(b, "little")


def bank1(regs):
    """Read registers in 0x60-0x74 (bank 1), then go back to bank 0."""
    cfg0 = rd(0xA9)
    i2c.writeto_mem(ADDR, 0xA9, bytes([cfg0 | 0x10]))
    try:
        return [rd(r) for r in regs]
    finally:
        i2c.writeto_mem(ADDR, 0xA9, bytes([cfg0 & 0xEF]))


def regs():
    config, led = bank1((0x70, 0x74))
    return {"CONFIG": config, "LED": led, "CFG1": rd(0xAA),
            "ATIME": rd(0x81), "ASTEP": rd(0xCA, 2)}


def reading():
    out, st = [], []
    for sel in ("F1F4CN", "F5F8CN"):  # the same two cycles as Sensor.all_channels
        chip.start_measure(sel)
        out.append(chip.get_spectral_data())
        st.append(rd(0x94))  # ASTATUS: bit 7 analog saturation, bits 3:0 gain code
    a, b = out
    return {"ch": list(a[:4]) + list(b[:4]), "clear": [a[4], b[4]],
            "nir": [a[5], b[5]], "astatus": st, "ms": time.ticks_ms()}


def saturated(r):
    return any(s & 0x80 for s in r["astatus"]) or max(r["ch"] + r["clear"]) >= 65535


def block(tag, n, ma):
    sat = False
    for _ in range(n):
        r = reading()
        r["tag"] = tag
        r["mA"] = ma
        sat = sat or saturated(r)
        print(json.dumps(r))
    return sat


print(json.dumps({"event": "start", "regs": regs()}))
try:
    block("off", 5, 0)
    for ma in (4, 10, 20):
        chip.set_led_current(ma)
        print(json.dumps({"event": "led", "mA": ma, "regs": regs()}))
        if block("on", 8, ma):
            # Too bright for 128x: repeat at 32x (code 6), then put 128x back.
            chip.set_again(6)
            try:
                block("on-32x", 3, ma)
            finally:
                chip.set_again(8)
finally:
    chip.set_led_current(0)
    print(json.dumps({"event": "off", "regs": regs()}))
block("off-after", 5, 0)
print(json.dumps({"event": "end", "regs": regs()}))
