#!/usr/bin/env python3
"""Hand a step-by-step driver one command and wait until it is waiting again.

For ``enclosure_height_cal.py``, ``tip_cal.py`` and ``paint_transfer.py``, which
all read one command at a time from ``cmd`` in their working directory and log
``WAIT (...)`` when they are ready for the next. Copy this into the same folder.

    python3 drive.py <command words...>     e.g.  python3 drive.py z 118
    python3 drive.py --status               last log lines and state, no command

Writes the command atomically (cmd.tmp -> cmd), then prints every log line the
step produced. Returns once the script logs its next WAIT, exits, or errors.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "log.txt")


def lines():
    with open(LOG) as fh:
        return fh.read().splitlines()


if sys.argv[1:] == ["--status"]:
    print("\n".join(lines()[-12:]))
    with open(os.path.join(HERE, "state.json")) as fh:
        s = json.load(fh)
    print({k: s.get(k) for k in ("phase", "aboard", "tip", "pos", "floor", "target",
                                 "aspirated", "waiting_for", "note", "updated_local")
           if k in s})
    sys.exit(0)

cmd = " ".join(sys.argv[1:])
n0 = len(lines())
tmp = os.path.join(HERE, "cmd.tmp")
with open(tmp, "w") as fh:
    fh.write(cmd + "\n")
os.replace(tmp, os.path.join(HERE, "cmd"))
t0 = time.time()
while time.time() - t0 < 900:
    time.sleep(0.5)
    new = lines()[n0:]
    seen = False
    done = False
    for ln in new:
        if "CMD:" in ln:
            seen = True
        elif seen and ("WAIT (" in ln or "exiting" in ln or "ERROR" in ln):
            done = True
    if done:
        break
print("\n".join(lines()[n0:]))
