#!/usr/bin/env python3
"""Live preview of the lid camera, over the whole sensor, for positioning the mount and focusing.

Run it on the Pi 5 that carries the HQ Camera, then open the printed address in a browser on
the lab's tailnet:

    python3 preview_server.py              # stops by itself after 30 min
    python3 preview_server.py --minutes 90

It is PR #84's preview_server.py (ot2-overhead-camera/preview_server.py, itself based on the
picamera2 mjpeg_server example, BSD-2, Raspberry Pi Ltd) with three changes:

  * It keeps the whole 4:3 field. Asked for a 16:9 stream (1536 x 864), libcamera picks the
    IMX477's 2028 x 1080 mode, ScalerCrop (108, 440, 3840, 2160): 95 % of the sensor's width and
    71 % of its height. At 8 mm from the middle of the deck that hides the front 52 mm of slots 1-3
    and the back 52 mm of slots 10-12, which a full-resolution still does show. This version
    forces the 2028 x 1520 binned mode, ScalerCrop (2, 0, 4052, 3040), and streams 1352 x 1014.
  * It listens on the Pi's tailnet address only, not on the campus Wi-Fi, and stops after
    --minutes, so that it doesn't hold the camera for other users.
  * The page draws a cross on the image centre (the lens axis), for centring the mount.

The live view is a third of full resolution (about 2.8 px/mm at 8 mm). Measure from
full-resolution stills: stop this first, since only one program can hold the camera.

A focus score (variance of the image Laplacian; higher is sharper) is printed once per second.
"""

import argparse
import io
import logging
import socketserver
import subprocess
import threading
from http import server
from threading import Condition, Thread
from time import sleep

import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

SENSOR_MODE = (2028, 1520)   # 2x2 binned, the whole 4056 x 3040 array
MAIN_SIZE = (1352, 1014)     # 4:3, a third of full resolution
LORES_SIZE = (640, 480)      # focus-score frames

PAGE = """\
<html>
<head><title>OT-2 lid camera: live preview</title>
<style>
  body {{ background:#222; color:#eee; font-family:sans-serif; text-align:center }}
  .frame {{ position:relative; display:inline-block; max-width:95vw }}
  .frame img {{ display:block; max-width:95vw; max-height:85vh }}
  .h, .v {{ position:absolute; background:rgba(255,80,40,.8) }}
  .h {{ left:47%; width:6%; top:50%; height:2px }}
  .v {{ top:47%; height:6%; left:50%; width:2px }}
</style></head>
<body>
<h2>OT-2 lid camera: live preview (whole sensor, 4:3)</h2>
<p>The cross marks the image centre. The focus score prints in the terminal once per second;
turn the focus ring until it peaks. This page stops by itself after {minutes} min.</p>
<div class="frame"><img src="stream.mjpg" /><div class="h"></div><div class="v"></div></div>
</body>
</html>
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("preview")


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


output = StreamingOutput()


class StreamingHandler(server.BaseHTTPRequestHandler):
    page = b""

    def do_GET(self):
        if self.path == "/":
            content = self.page
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", 0)
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception as e:
                logger.info("Client %s disconnected: %s", self.client_address, e)
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass  # keep the terminal clear for focus scores


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def focus_score(gray):
    """Variance of the 4-neighbour Laplacian. Higher = sharper."""
    g = gray.astype(np.float32)
    lap = (
        g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:]
        - 4.0 * g[1:-1, 1:-1]
    )
    return float(lap.var())


def focus_loop(picam2):
    w, h = LORES_SIZE
    while True:
        try:
            yuv = picam2.capture_array("lores")
            score = focus_score(yuv[:h, :w])  # Y plane of YUV420
            logger.info("focus score: %8.1f  (higher = sharper)", score)
        except Exception as e:
            logger.warning("focus score failed: %s", e)
        sleep(1)


def tailnet_ip():
    try:
        out = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=5)
        return out.stdout.split()[0]
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--minutes", type=float, default=30.0, help="stop after this long (default 30)")
    ap.add_argument("--host", help="address to listen on (default: this Pi's tailnet address)")
    args = ap.parse_args()
    host = args.host or tailnet_ip() or "127.0.0.1"

    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size": MAIN_SIZE},
        lores={"size": LORES_SIZE, "format": "YUV420"},
        sensor={"output_size": SENSOR_MODE, "bit_depth": 12},
    )
    picam2.configure(config)
    picam2.start_recording(JpegEncoder(), FileOutput(output))
    sleep(0.5)
    crop = picam2.capture_metadata().get("ScalerCrop")
    logger.info("sensor mode %s, ScalerCrop %s of %s", picam2.camera_configuration()["sensor"], crop,
                picam2.camera_properties["PixelArraySize"])

    Thread(target=focus_loop, args=(picam2,), daemon=True).start()
    StreamingHandler.page = PAGE.format(minutes=f"{args.minutes:g}").encode("utf-8")
    httpd = StreamingServer((host, args.port), StreamingHandler)
    stop = threading.Timer(args.minutes * 60, httpd.shutdown)
    stop.daemon = True
    stop.start()
    try:
        logger.info("Preview at http://%s:%d for %g min", host, args.port, args.minutes)
        httpd.serve_forever()
    finally:
        picam2.stop_recording()
        picam2.close()
        logger.info("stopped")


if __name__ == "__main__":
    main()
