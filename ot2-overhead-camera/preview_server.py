#!/usr/bin/env python3
"""Live MJPEG preview server for focusing the RPi HQ Camera over the network.

The HQ Camera (IMX477) has no autofocus, and the Pi runs headless (RPi OS
Lite), so this serves a live preview to any browser on the tailnet:

    python3 preview_server.py
    # then open http://<tailscale-ip>:8000 in a browser

While the stream is running, a focus score (variance of the image Laplacian
-- higher is sharper) is printed to the terminal once per second. Turn the
lens focus ring slowly until the score peaks, then lock the thumb screw.

Based on the picamera2 mjpeg_server example (BSD-2, Raspberry Pi Ltd) and the
a1_cam device in AccelerationConsortium/ac-dev-lab.
"""

import io
import logging
import socketserver
from http import server
from threading import Condition, Thread
from time import sleep

import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

PORT = 8000
LORES_SIZE = (640, 480)  # focus-score frames; preview stream is 1536x864

PAGE = """\
<html>
<head><title>OT-2 overhead camera preview</title></head>
<body style="background:#222;color:#eee;font-family:sans-serif;text-align:center">
<h2>OT-2 overhead camera &mdash; live preview</h2>
<p>Focus score prints in the SSH terminal once per second. Adjust the lens
focus ring until it peaks.</p>
<img src="stream.mjpg" style="max-width:95%%" />
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


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            content = PAGE.encode("utf-8")
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
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
            )
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


picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (1536, 864)},
    lores={"size": LORES_SIZE, "format": "YUV420"},
)
picam2.configure(config)
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

Thread(target=focus_loop, args=(picam2,), daemon=True).start()

try:
    logger.info("Preview at http://<this-pi's-tailscale-ip>:%d", PORT)
    StreamingServer(("", PORT), StreamingHandler).serve_forever()
finally:
    picam2.stop_recording()
