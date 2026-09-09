#!/usr/bin/env python3
"""Photograph the OT-2 deck through the robot's own camera.

The X-scan test presses the nozzle down at slot 10 and only finds out whether
anything was there from the grip check, several moves later. This answers the
same question first, in one HTTP call, with no motion at all::

    python3 deck_photo.py -o deck.jpg

Run it before ``run_xscan_test.py`` whenever you are not standing next to the
robot. On 2026-09-09 it was the check that caught an empty deck before a run
that would otherwise have pressed an empty slot 10.

The endpoint is ``POST /camera/picture`` -- a GET returns 405, which reads like
"no camera" if you are not expecting it. The image comes back 640x480 and
rotated a quarter turn, because the camera is mounted on its side above the
deck; ``--rotate`` (default) corrects that when Pillow is available and is a
no-op otherwise, so the script keeps working on a bare Pi.

Must run on the machine with the USB-Ethernet link to the robot -- as of
2026-09-09 that is the Pi behind RPI_STREAM_CAM_HOSTNAME, not the one behind
OT2_STREAM_CAM_HOSTNAME.
"""

from __future__ import annotations

import argparse
import sys

import requests

DEFAULT_ROBOT_IP = "169.254.51.252"
HEADERS = {"Opentrons-Version": "3"}


def capture(ip=DEFAULT_ROBOT_IP, timeout=30):
    """Return the raw JPEG bytes of the current deck view."""
    r = requests.post(f"http://{ip}:31950/camera/picture", headers=HEADERS,
                      timeout=timeout)
    r.raise_for_status()
    if not r.content.startswith(b"\xff\xd8"):
        raise RuntimeError(
            f"the robot answered {r.status_code} but did not return a JPEG: "
            f"{r.content[:200]!r}"
        )
    return r.content


def rotate(jpeg):
    """Turn the frame upright. Returns it unchanged if Pillow is not installed."""
    try:
        import io

        from PIL import Image
    except ImportError:
        return jpeg
    out = io.BytesIO()
    Image.open(io.BytesIO(jpeg)).rotate(-90, expand=True).save(out, "JPEG", quality=88)
    return out.getvalue()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-o", "--out", default="deck.jpg", help="where to write the JPEG")
    p.add_argument("--robot-ip", default=DEFAULT_ROBOT_IP)
    p.add_argument("--no-rotate", action="store_true",
                   help="keep the camera's native sideways orientation")
    args = p.parse_args(argv)

    try:
        jpeg = capture(args.robot_ip)
    except requests.exceptions.RequestException as exc:
        print(f"could not reach the robot at {args.robot_ip}:31950 -- {exc}\n"
              "Run this from the Pi that holds the USB-Ethernet link to the OT-2.",
              file=sys.stderr)
        return 1

    if not args.no_rotate:
        jpeg = rotate(jpeg)
    with open(args.out, "wb") as fh:
        fh.write(jpeg)
    print(f"wrote {args.out} ({len(jpeg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
