#!/usr/bin/env python3
"""What the A1 mini's own SD card says it has printed, over LAN through a Pi. Read-only (LIST and RETR).

Each cloud print leaves three files in /cache: `<job>.3mf` (the sliced project, with the plate's
G-code and thumbnails), `<job>_plate_N.gcode`, and `N_<job>.bbl`, a small JSON of the send options.
/ipcam holds the camera's recording of each print in ~8 min segments, which shows when the printer
actually ran. File dates are the printer's local clock, which has been on both UTC-6 and UTC+8, so
take times from the cloud history (cloud_history.py) instead.

Uses bambu_lan.py from PR #234 (`bambu/`, branch claude/ot2-lid-camera-mount-20260925): point
BAMBU_DIR at that folder. It tunnels through the Pi with ssh -W, so the access code never reaches the Pi.

    BAMBU_DIR=../../../bambu python sd_card.py ls  > sd_card.json      # every folder, with dates
    BAMBU_DIR=../../../bambu python sd_card.py get out/ "/cache/1_RaspberryPiCameraMount(NEW).bbl"
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.environ.get("BAMBU_DIR", os.path.join(os.path.dirname(__file__), "../../../bambu")))
import bambu_lan as bl  # noqa: E402


def tree(f, root: str = "/", depth: int = 3) -> dict[str, list[str]]:
    out, todo = {}, [root]
    while todo:
        path = todo.pop(0)
        lines: list[str] = []
        f.retrlines(f"LIST {path}", lines.append)
        out[path] = lines
        for line in lines:
            parts = line.split(None, 8)
            if len(parts) == 9 and line.startswith("d") and parts[8] not in (".", "..") and path.count("/") < depth:
                todo.append(path.rstrip("/") + "/" + parts[8])
    return out


def main() -> int:
    printer = bl.Printer(os.environ.get("PRINTER", "A1_MINI"))
    via = os.environ.get("VIA", "CUBXL_PI")
    with bl.ftps(printer, via) as f:
        if sys.argv[1] == "ls":
            print(json.dumps(printer.redact(tree(f)), indent=1))
            return 0
        dest = sys.argv[2]
        os.makedirs(dest, exist_ok=True)
        for path in sys.argv[3:]:
            out = os.path.join(dest, path.strip("/").replace("/", "__"))
            with open(out, "wb") as fh:
                f.retrbinary(f"RETR {path}", fh.write, blocksize=32768)
            print(f"{os.path.getsize(out):>9} B  {path}", flush=True)
            time.sleep(0.5)   # the printer and the Pi's Wi-Fi are shared; go gently
    return 0


if __name__ == "__main__":
    sys.exit(main())
