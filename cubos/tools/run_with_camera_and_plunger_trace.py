#!/usr/bin/env python3
"""Run the protocol with camera capture, plunger command timing and step timing.

Thin composition of the two committed tools: it installs the plunger trace
hook from run_with_plunger_trace, then hands control to the camera harness.
Behaviour of neither is changed.

Also records when each protocol step starts and how long it takes, as
``@@STEP`` lines and a JSON list at $STEP_TRACE_OUT. The wrapper sits under
the camera harness's own hook, so a step's time excludes any frame captured
after it. With CUBXL_NO_CAMERA=1 the protocol runs without the camera harness.
Used by cubxl_run.py; runnable on its own exactly as before.
"""
import sys, os, time, json, datetime

TOOLS = os.path.dirname(os.path.abspath(__file__))   # was ~/byu-vcl/cubos/tools; any checkout now
sys.path.insert(0, TOOLS)

from cubos.instruments.pipette.vendors import opentrons as _ot

TRACE = []
_orig = _ot.OpentronsPipette._send_command


def traced(self, code, *args, **kwargs):
    t0 = time.time()
    exc = None
    try:
        reply = _orig(self, code, *args, **kwargs)
    except Exception as e:                       # noqa: BLE001
        exc, reply = repr(e), None
        raise
    finally:
        rec = {"t": datetime.datetime.now(datetime.timezone.utc)
                        .isoformat(timespec="milliseconds"),
               "code": code, "args": [repr(a) for a in args],
               "dt_s": round(time.time() - t0, 3),
               "reply": reply, "error": exc}
        TRACE.append(rec)
        print(f"@@PLUNGER {json.dumps(rec)}", flush=True)
    return reply


_ot.OpentronsPipette._send_command = traced

# Step timing. Installed before the camera harness wraps the same method, so
# the harness's capture runs after this wrapper has returned.
from cubos.protocol_engine import runtime as _rt                # noqa: E402

STEPS = []
_orig_step = _rt.ProtocolStep.execute


def timed_step(self, context):
    t_wall = datetime.datetime.now(datetime.timezone.utc)
    t0 = time.monotonic()
    ok = False
    try:
        result = _orig_step(self, context)
        ok = True
        return result
    finally:
        rec = {"index": self.index, "command": self.command_name,
               "t": t_wall.isoformat(timespec="milliseconds"),
               "dt_s": round(time.monotonic() - t0, 3), "ok": ok}
        STEPS.append(rec)
        print(f"@@STEP {json.dumps(rec)}", flush=True)


_rt.ProtocolStep.execute = timed_step

rc = 1
try:
    if os.environ.get("CUBXL_NO_CAMERA") == "1":
        from cubos.tools.run_protocol import main as run_main      # noqa: E402
        rest = sys.argv[1:]
        rc = run_main(rest[1:] if rest[:1] == ["--"] else rest) or 0
    else:
        import run_with_camera_capture as cam                   # noqa: E402
        rc = cam.main()
finally:
    out = os.environ.get("PLUNGER_TRACE_OUT", "/tmp/plunger_trace.json")
    with open(out, "w") as fh:
        json.dump(TRACE, fh, indent=2)
    print(f"@@PLUNGER-TRACE {len(TRACE)} command(s) -> {out}", flush=True)
    out = os.environ.get("STEP_TRACE_OUT", "/tmp/step_trace.json")
    with open(out, "w") as fh:
        json.dump(STEPS, fh, indent=2)
    print(f"@@STEP-TRACE {len(STEPS)} step(s) -> {out}", flush=True)
sys.exit(rc)
