"""Run the protocol on hardware, recording every plunger command + timing.

Behaviour is unchanged: this wraps OpentronsPipette._send_command to log
(code, args, elapsed, reply) and calls straight through.

The firmware's stepMotor() bit-bangs the STEP pin at ~0.673 s/mm with no
feedback, so a round trip that does NOT scale with the commanded distance
proves the firmware emitted no steps.  The converse does not hold: a round
trip that does scale only proves the Arduino stepped, not that the motor
turned.  Whether the plunger physically moved needs a pair of eyes.
"""
import sys, time, json, datetime

from cubos.instruments.pipette.vendors import opentrons as _ot

TRACE = []
_orig = _ot.OpentronsPipette._send_command
NAMES = {10: "HOME", 11: "MOVE_TO", 12: "ASPIRATE", 13: "DISPENSE",
         14: "STATUS", 15: "MIX", 28: "DRIP_STOP"}


def traced(self, code, *args, **kwargs):
    t0 = time.time()
    err = None
    try:
        reply = _orig(self, code, *args, **kwargs)
    except Exception as exc:          # record then re-raise unchanged
        err, reply = repr(exc), None
        raise
    finally:
        rec = {
            "t": datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "cmd": NAMES.get(code, str(code)),
            "code": code,
            "args": [str(a) for a in args],
            "dt_s": round(time.time() - t0, 3),
            "reply": reply,
            "error": err,
        }
        TRACE.append(rec)
        print(f"@@PLUNGER {json.dumps(rec)}", flush=True)
    return reply


_ot.OpentronsPipette._send_command = traced

from cubos.tools.run_protocol import main  # noqa: E402

try:
    rc = main()
finally:
    with open("/tmp/plunger_trace.json", "w") as fh:
        json.dump(TRACE, fh, indent=2)
    print(f"@@PLUNGER-TRACE {len(TRACE)} command(s) -> /tmp/plunger_trace.json",
          flush=True)
sys.exit(rc or 0)
