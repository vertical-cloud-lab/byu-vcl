#!/usr/bin/env python3
"""Run the protocol with BOTH camera capture and plunger command timing.

Thin composition of the two committed tools: it installs the plunger trace
hook from run_with_plunger_trace, then hands control to the camera harness.
Behaviour of neither is changed.
"""
import sys, os, time, json, datetime

TOOLS = os.path.expanduser("~/byu-vcl/cubos/tools")
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

import run_with_camera_capture as cam                       # noqa: E402

rc = 1
try:
    rc = cam.main()
finally:
    out = os.environ.get("PLUNGER_TRACE_OUT", "/tmp/plunger_trace.json")
    with open(out, "w") as fh:
        json.dump(TRACE, fh, indent=2)
    print(f"@@PLUNGER-TRACE {len(TRACE)} command(s) -> {out}", flush=True)
sys.exit(rc)
