#!/usr/bin/env python3
"""Zero-motion check: does the module's own illumination respond to --rgb?

Every scan on record was taken with rgb=(0,0,0), i.e. LEDs off. Before the
paint run we need to know (a) that the LEDs light at all and (b) where they
saturate the AS7341, because a saturated channel is not a colour measurement.
The module is seated in its closed base, so ambient is ~440 counts and any
response is unambiguous.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/xscan"))
from sensor_read import SensorLink, CHANNELS

link = SensorLink(
    broker=os.environ["MQTT_BROKER"], port=int(os.environ["MQTT_PORT"]),
    username=os.environ["MQTT_USERNAME"], password=os.environ["MQTT_PASSWORD"],
    pico_id=os.environ["PICO_ID"],
)
link.connect()
link.check_delivery()

LEVELS = [(0,0,0), (32,32,32), (128,128,128), (255,255,255),
          (255,0,0), (0,255,0), (0,0,255)]
out = []
for rgb in LEVELS:
    rd = link.read(label=f"led-{rgb[0]}-{rgb[1]}-{rgb[2]}", rgb=rgb)
    ch = rd["channels"]
    out.append({"rgb": rgb, "channels": ch, "total": rd["total"]})
    print(f"R={rgb[0]:>3} Y={rgb[1]:>3} B={rgb[2]:>3}  " +
          "  ".join(f"{c}={ch[c]:>6}" for c in CHANNELS) +
          f"  total={rd['total']:>7}", flush=True)
link.close()
json.dump(out, open(os.path.expanduser("~/xscan/led-probe.json"), "w"), indent=1)
