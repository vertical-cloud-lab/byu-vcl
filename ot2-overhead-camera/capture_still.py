#!/usr/bin/env python3
"""Capture a full-resolution still from the RPi HQ Camera (IMX477).

Saves a timestamped 4056x3040 JPEG and prints capture metadata plus a focus
score (variance of the image Laplacian -- higher is sharper) so shots taken
at different zoom/focus/lighting settings can be compared numerically.

Usage:
    python3 capture_still.py                          # auto exposure
    python3 capture_still.py -o plate_28mm.jpg
    python3 capture_still.py --exposure 250 --gain 2  # manual, 250 ms
"""

import argparse
from datetime import datetime
from time import sleep

import numpy as np
from picamera2 import Picamera2


def focus_score(gray):
    g = gray.astype(np.float32)
    lap = (
        g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:]
        - 4.0 * g[1:-1, 1:-1]
    )
    return float(lap.var())


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-o", "--output", help="output filename (default: timestamped)")
parser.add_argument(
    "--exposure", type=float, help="manual exposure time in milliseconds "
    "(the plate is stationary, so long exposures like 100-500 are fine)"
)
parser.add_argument("--gain", type=float, help="manual analogue gain, e.g. 1.0-8.0")
parser.add_argument("--quality", type=int, default=93, help="JPEG quality (default 93)")
args = parser.parse_args()

output = args.output or datetime.now().strftime("ot2cam_%Y-%m-%d_%H-%M-%S.jpg")

picam2 = Picamera2()
picam2.options["quality"] = args.quality
picam2.configure(picam2.create_still_configuration())

controls = {}
if args.exposure is not None:
    controls["AeEnable"] = False
    controls["ExposureTime"] = int(args.exposure * 1000)  # ms -> us
    controls["AnalogueGain"] = args.gain if args.gain is not None else 1.0
if controls:
    picam2.set_controls(controls)

picam2.start()
sleep(2)  # let auto-exposure / auto-white-balance settle

request = picam2.capture_request()
try:
    request.save("main", output)
    rgb = request.make_array("main")
    metadata = request.get_metadata()
finally:
    request.release()
picam2.stop()

gray = rgb[..., :3].mean(axis=2)
print(f"saved:         {output}  ({rgb.shape[1]}x{rgb.shape[0]})")
print(f"focus score:   {focus_score(gray):.1f}  (higher = sharper)")
print(f"exposure time: {metadata.get('ExposureTime', 0) / 1000:.1f} ms")
print(f"analogue gain: {metadata.get('AnalogueGain', 0):.2f}")
print(f"lux estimate:  {metadata.get('Lux', float('nan')):.1f}")
