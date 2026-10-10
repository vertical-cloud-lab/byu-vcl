# inventory.py -- run from RAM with `mpremote run`; reads only, writes nothing.
# Every file on the board with its size and sha256, the MicroPython version, and the
# AS7341's timing, gain and LED registers read straight off the chip (no Sensor(), so
# nothing is reset or written).
import os, sys, json, hashlib, binascii
from machine import I2C, Pin

def walk(d):
    for name, kind, *_ in os.ilistdir(d):
        p = (d.rstrip("/") + "/" + name) if d != "/" else "/" + name
        if kind & 0x4000:
            yield from walk(p)
        else:
            yield p

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(1024)
            if not b:
                break
            h.update(b)
    return binascii.hexlify(h.digest()).decode()

print(json.dumps({"event": "version", "sys": sys.version, "impl": sys.implementation[0],
                  "uname": tuple(os.uname())}))
for p in sorted(walk("/")):
    print(json.dumps({"event": "file", "path": p, "size": os.stat(p)[6], "sha256": sha(p)}))
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
rd = lambda r, n=1: int.from_bytes(i2c.readfrom_mem(0x39, r, n), "little")
cfg0 = rd(0xA9)
i2c.writeto_mem(0x39, 0xA9, bytes([cfg0 | 0x10]))      # bank 1 for CONFIG/LED
try:
    config, led = rd(0x70), rd(0x74)
finally:
    i2c.writeto_mem(0x39, 0xA9, bytes([cfg0 & 0xEF]))
print(json.dumps({"event": "regs", "ID": rd(0x92), "CFG1_again": rd(0xAA), "ATIME": rd(0x81),
                  "ASTEP": rd(0xCA, 2), "CONFIG": config, "LED": led, "AZ_CONFIG": rd(0xD6),
                  "CFG0": cfg0}))
