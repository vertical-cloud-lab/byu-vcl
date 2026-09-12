"""Run a protocol on hardware, grabbing frames from one or more cameras.

Why this exists: every hardware session on this branch has ended with "no
visual confirmation -- there is no camera on the CubXL deck, so whether a
tip seated, where the dropped tip went, and whether the caps are straight
need your eyes."  With cameras on the CubXL Pi, that gap closes -- but only
if the frames are taken at *known* moments.

So capture is keyed to protocol steps, not to wall clock.  Frames are taken
at step boundaries, where the gantry is stationary and its pose is known, and
each file is named with the step index and command that had just finished.
A frame labelled `step04_aspirate` is evidence about the aspirate; a frame
labelled `t+38s` is not.

Two hard rules, both about not making a camera into a hazard:

  * A camera failure NEVER aborts the protocol.  Every capture is wrapped;
    a failure is logged and the run continues.  Losing a picture is cheap.
    Aborting mid-run can leave a tool down inside a vial.
  * Captures happen only *between* steps.  Nothing here touches the gantry,
    the capper or the plunger, and no capture is issued while an instrument
    command is in flight.

Usage:
    # See what cameras the Pi has, and grab one test frame from each
    python run_with_camera_capture.py --list
    python run_with_camera_capture.py --test-shot --outdir /tmp/camtest

    # Run the protocol, 4 frames per camera at the default step boundaries
    python run_with_camera_capture.py --outdir /tmp/run_frames -- \
        <gantry.yaml> <deck.yaml> <protocol.yaml>

    # Choose the moments yourself (indices are validate_setup's step numbers)
    python run_with_camera_capture.py --at 2,4,9,10 --outdir ... -- <trio>

Backends are detected, not assumed: CSI ribbon cameras via rpicam-still /
libcamera-still, USB UVC devices via ffmpeg on /dev/videoN.  `--list` prints
exactly what was found and which backend each will use.
"""
import argparse
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

CAPTURE_TIMEOUT_S = 20


# --------------------------------------------------------------------------
# camera discovery
# --------------------------------------------------------------------------
def _rpicam_binary():
    for name in ("rpicam-still", "libcamera-still"):
        path = shutil.which(name)
        if path:
            return path
    return None


def _discover_csi():
    """CSI/ribbon cameras, as reported by rpicam-still --list-cameras."""
    binary = _rpicam_binary()
    if not binary:
        return []
    try:
        out = subprocess.run([binary, "--list-cameras"], capture_output=True,
                             text=True, timeout=20).stdout
    except Exception:
        return []
    cams = []
    # lines look like: "0 : imx708 [4608x2592 10-bit RGGB] (/base/axi/...)"
    for m in re.finditer(r"^\s*(\d+)\s*:\s*(\S+)", out, re.M):
        cams.append({"kind": "csi", "index": int(m.group(1)),
                     "name": m.group(2), "binary": binary})
    return cams


def _discover_uvc():
    """USB webcams: /dev/videoN nodes that actually support capture."""
    if not shutil.which("ffmpeg"):
        return []
    cams = []
    for node in sorted(glob.glob("/dev/video*"),
                       key=lambda p: int(re.sub(r"\D", "", p) or 0)):
        name = node
        # A UVC device exposes several /dev/video nodes; only some capture.
        if shutil.which("v4l2-ctl"):
            try:
                caps = subprocess.run(["v4l2-ctl", "-d", node, "--all"],
                                      capture_output=True, text=True,
                                      timeout=10).stdout
                if "Video Capture" not in caps:
                    continue
                m = re.search(r"Card type\s*:\s*(.+)", caps)
                if m:
                    name = m.group(1).strip()
            except Exception:
                continue
        cams.append({"kind": "uvc", "device": node, "name": name})
    return cams


def discover_cameras():
    return _discover_csi() + _discover_uvc()


def _label(cam, i):
    if cam["kind"] == "csi":
        return f"cam{i}_csi{cam['index']}"
    return f"cam{i}_{os.path.basename(cam['device'])}"


# --------------------------------------------------------------------------
# capture
# --------------------------------------------------------------------------
def capture(cam, path, width=1920, height=1080):
    """Grab one frame. Returns None on success, or an error string.

    Never raises: the caller is a protocol run and must not be interrupted
    by a camera.
    """
    try:
        if cam["kind"] == "csi":
            cmd = [cam["binary"], "--camera", str(cam["index"]),
                   "--width", str(width), "--height", str(height),
                   "--nopreview", "--immediate", "-o", path]
        else:
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                   "-f", "v4l2", "-video_size", f"{width}x{height}",
                   "-i", cam["device"], "-frames:v", "1", path]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=CAPTURE_TIMEOUT_S)
        if proc.returncode != 0:
            return (proc.stderr or proc.stdout or "non-zero exit").strip()[:300]
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return "no file written"
        return None
    except Exception as exc:                       # timeout, missing binary...
        return repr(exc)


def capture_all(cams, outdir, tag, manifest):
    for i, cam in enumerate(cams):
        name = f"{tag}__{_label(cam, i)}.jpg"
        path = os.path.join(outdir, name)
        t0 = time.time()
        err = capture(cam, path)
        rec = {"tag": tag, "camera": _label(cam, i), "name": cam["name"],
               "file": name, "dt_s": round(time.time() - t0, 2),
               "t": datetime.datetime.now().isoformat(timespec="seconds"),
               "error": err}
        manifest.append(rec)
        status = "OK " if err is None else "ERR"
        print(f"@@CAM {status} {name}  ({rec['dt_s']}s)"
              + (f"  {err}" if err else ""), flush=True)


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Run a CubOS protocol on hardware, capturing camera "
                    "frames at protocol step boundaries.")
    ap.add_argument("--list", action="store_true",
                    help="List detected cameras and exit (no protocol, no motion)")
    ap.add_argument("--test-shot", action="store_true",
                    help="Grab one frame per camera and exit (no protocol, no motion)")
    ap.add_argument("--outdir", default="/tmp/cubos_frames")
    ap.add_argument("--at", default=None,
                    help="Comma-separated step indices to capture AFTER. "
                         "Default: 4 boundaries spread across the protocol.")
    ap.add_argument("--shots", type=int, default=4,
                    help="How many frames per camera when --at is not given")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("rest", nargs=argparse.REMAINDER,
                    help="-- <gantry.yaml> <deck.yaml> <protocol.yaml> [run_protocol args]")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    cams = discover_cameras()

    if not cams:
        print("No cameras detected (looked for rpicam-still/libcamera-still "
              "CSI devices and ffmpeg-capable /dev/video* nodes).")
    for i, cam in enumerate(cams):
        where = cam.get("device", f"csi index {cam.get('index')}")
        print(f"  {_label(cam, i)}: {cam['name']}  [{cam['kind']}]  {where}")

    if args.list:
        return 0

    manifest = []
    if args.test_shot:
        capture_all(cams, args.outdir, "testshot", manifest)
        with open(os.path.join(args.outdir, "frames.json"), "w") as fh:
            json.dump(manifest, fh, indent=2)
        return 0 if all(r["error"] is None for r in manifest) else 1

    rest = args.rest[1:] if args.rest and args.rest[0] == "--" else args.rest
    if len(rest) < 3:
        ap.error("need -- <gantry.yaml> <deck.yaml> <protocol.yaml>")

    # Hook the step boundary. Imported here so --list works without CubOS.
    from cubos.protocol_engine import runtime as _rt
    from cubos.protocol_engine import protocol as _proto

    wanted = None
    if args.at:
        wanted = {int(x) for x in args.at.split(",") if x.strip() != ""}

    state = {"points": set(), "total": 0}

    # Protocol.execute is the only place that knows the real step count.
    # ProtocolContext does not carry a reference back to its protocol.
    _orig_run = _proto.Protocol.execute

    def protocol_execute(self, context):
        total = len(self._steps)
        state["total"] = total
        if wanted is not None:
            state["points"] = {i for i in wanted if 0 <= i < total}
            dropped = sorted(wanted - state["points"])
            if dropped:
                print(f"@@CAM ignoring out-of-range step(s) {dropped}; "
                      f"protocol has {total}", flush=True)
        elif total:
            # Spread over the interior boundaries: step 0 is `home` and the
            # last step is usually `home`, neither worth a picture.
            n = max(1, args.shots)
            state["points"] = {
                max(0, min(total - 1, round((k + 1) * (total - 1) / (n + 1))))
                for k in range(n)}
        print(f"@@CAM capture after steps {sorted(state['points'])} "
              f"of {total}", flush=True)
        return _orig_run(self, context)

    _proto.Protocol.execute = protocol_execute

    _orig_execute = _rt.ProtocolStep.execute

    def execute(self, context):
        result = _orig_execute(self, context)
        if self.index in state["points"]:
            tag = f"step{self.index:02d}_{self.command_name}"
            capture_all(cams, args.outdir, tag, manifest)
        return result

    _rt.ProtocolStep.execute = execute

    sys.argv = ["run_protocol"] + rest
    from cubos.tools.run_protocol import main as run_main
    try:
        rc = run_main()
    finally:
        with open(os.path.join(args.outdir, "frames.json"), "w") as fh:
            json.dump(manifest, fh, indent=2)
        ok = sum(1 for r in manifest if r["error"] is None)
        print(f"@@CAM {ok}/{len(manifest)} frame(s) captured -> {args.outdir}",
              flush=True)
    return rc or 0


if __name__ == "__main__":
    sys.exit(main())
