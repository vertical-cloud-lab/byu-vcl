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
**upside down**: the camera is mounted inverted on the gantry, so slot 1 lands
top-right and the trash in slot 12 lands bottom-left. ``--rotate`` (default)
turns it 180 degrees, which puts slot 1 front-left and the trash back-right --
the deck as you stand at the machine.

Getting this wrong is not cosmetic. On 2026-09-10 an upside-down frame was read
as "the vials are on the deck" when they were in fact off it, on the bench to
the right.

Two mistakes were live between 2026-09-09 and 2026-09-10 and both are fixed
here. The rotation was a quarter turn rather than a half turn; and when Pillow
was missing the correction silently did *nothing* and still reported success.
Pillow is not installed on the stream-cam Pi, which is where this script runs,
so every frame committed before 2026-09-10 is raw and upside down. It now says
so, loudly, on stderr and in the exit status, rather than shipping an
unrotated frame that looks fine until somebody reads a slot number from it.
Use ``--fix FILE`` to correct an already-saved frame on a machine that does
have Pillow.

Must run on the machine with the USB-Ethernet link to the robot -- as of
2026-09-09 that is the Pi behind RPI_STREAM_CAM_HOSTNAME, not the one behind
OT2_STREAM_CAM_HOSTNAME.
"""

from __future__ import annotations

import argparse
import io
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


ROTATE_DEGREES = 180  # the camera is mounted inverted over the deck


def rotate(jpeg, degrees=ROTATE_DEGREES):
    """Turn the frame upright.

    Raises ``RuntimeError`` if Pillow is missing rather than returning the
    frame untouched. The silent version of this shipped upside-down deck
    photos for two days without a single warning, and an upside-down deck
    photo is worse than no deck photo: it is read, and it is believed.
    """
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - depends on the host
        raise RuntimeError(
            "Pillow is not installed, so the frame cannot be turned upright. "
            "The OT-2 camera is mounted inverted and its raw output is upside "
            "down. Either `pip install Pillow` here, or pass --no-rotate and "
            "correct it elsewhere with `deck_photo.py --fix FILE`."
        ) from exc
    out = io.BytesIO()
    Image.open(io.BytesIO(jpeg)).rotate(degrees, expand=True).save(
        out, "JPEG", quality=88)
    return out.getvalue()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-o", "--out", default="deck.jpg", help="where to write the JPEG")
    p.add_argument("--robot-ip", default=DEFAULT_ROBOT_IP)
    p.add_argument("--no-rotate", action="store_true",
                   help="keep the camera's native upside-down orientation")
    p.add_argument("--degrees", type=int, default=ROTATE_DEGREES,
                   help="rotation applied to the raw frame (default: 180)")
    p.add_argument("--fix", metavar="FILE",
                   help="rotate an already-saved frame instead of capturing a "
                        "new one; use this to correct a frame taken on a host "
                        "without Pillow")
    args = p.parse_args(argv)

    if args.fix:
        with open(args.fix, "rb") as fh:
            jpeg = fh.read()
    else:
        try:
            jpeg = capture(args.robot_ip)
        except requests.exceptions.RequestException as exc:
            print(f"could not reach the robot at {args.robot_ip}:31950 -- {exc}\n"
                  "Run this from the Pi that holds the USB-Ethernet link to the OT-2.",
                  file=sys.stderr)
            return 1

    if not args.no_rotate:
        try:
            jpeg = rotate(jpeg, args.degrees)
        except RuntimeError as exc:
            # Still write the frame -- losing a capture helps nobody -- but say
            # plainly that it is upside down and fail, so a caller that checks
            # the exit status cannot publish it by accident.
            with open(args.out, "wb") as fh:
                fh.write(jpeg)
            print(f"wrote {args.out} ({len(jpeg)} bytes) BUT IT IS UPSIDE DOWN: {exc}",
                  file=sys.stderr)
            return 3

    with open(args.out, "wb") as fh:
        fh.write(jpeg)
    print(f"wrote {args.out} ({len(jpeg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
