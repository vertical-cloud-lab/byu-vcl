# Local CubOS patches applied on the lab Raspberry Pi

These are changes made to the **upstream CubOS clone** at `~/CubOS` on the lab Pi
(`Ursa-Laboratories/CubOS`, currently `main` @ `cbc33dc`). They do not live in that
repo, so they are recorded here to keep the Pi reproducible and to give us something
to upstream.

Apply with:

```bash
cd ~/CubOS
git apply /path/to/byu-vcl/cubos/patches/<name>.patch
```

Check what is currently applied with `cd ~/CubOS && git diff --stat`.

---

## `pawduino-connect-boot-banner.patch`

**Applied 2026-08-03.** Required to run `capper_decapper_test.yaml` on the CubXL at all.

### Symptom

Every `run_protocol` with `offline: false` on the capper died before step 0:

```
ERROR during execution: Arduino did not respond after connect:
  No 'value1' field in line-break sensor response 'OK:Ready'.
```

### Cause

Two independent problems in
`packages/core/src/cubos/instruments/capper/vendors/pawduino.py`:

1. `PawduinoCapper.connect()` opens the serial port, which toggles DTR and **resets
   the Arduino**. The board runs its bootloader and then prints an `OK:Ready` boot
   banner. `connect()` waits a fixed `_ARDUINO_SETTLE_TIME = 2.0` s — but on this Pi
   the banner does not arrive until **3.76 s** after open (measured, reproducible
   across trials on an `2341:0043` Arduino Uno R3).
2. `_send_command()` returns the *first* line beginning with `OK:`. So even when the
   banner does arrive inside the settle window it is still sitting in the input
   buffer, and it gets consumed as the reply to the first real command. `connect()`
   immediately issues `read_cap_present()` (command `7`), reads back `OK:Ready`
   instead of `OK:{"value1":0}`, and raises.

Reproduced directly against the board — the first command gets the banner, the
second gets the real reading:

```
cmd 7 -> 'OK:Ready'
cmd 7 -> 'OK:{"value1":0}'
```

### Fix

Wait for the banner explicitly (up to a new `_ARDUINO_BOOT_TIMEOUT = 10.0` s,
accepting `OK:` or `ERR:`), then `reset_input_buffer()` before the first real
command. Bumping the sleep alone is not sufficient — the buffer still has to be
drained.

### Upstream

Worth sending to `Ursa-Laboratories/CubOS`. Not filed yet.

---

## `cap-release-confirm-after-retract.patch`

**Applied 2026-08-03.** Required for `cap` to ever succeed on this head. With it,
`capper_decapper_test.yaml` completed all 27 steps on the CubXL.

### Symptom

`decap` worked, the pipette entered the open vial, and then `cap` aborted every time:

```
ERROR during execution: cap failed for 'vial_holder.vial_2':
  CapperError: cap: sensor did not confirm cap release after 3 attempt(s)
  (last reading: cap_present=True, expected False).
```

The cap was in fact placed back on the vial correctly. Reading the sensor by hand
right after the abort, with the head parked at `safe_z`, returned `cap_present=False`
— nothing was stuck to the head. The release worked; only the confirmation failed.

### Cause

`_run_capper_sequence()` in `packages/core/src/cubos/protocol_engine/commands/capper.py`
confirms **at the engage plane, before retracting**, for both directions:

```python
context.gantry.move(instrument, (x, y, engage_z))  # engage
_confirm_capture_or_release(capper, capturing=capturing, ...)
...
context.gantry.move(instrument, (x, y, context.gantry.safe_z))  # retract
```

For a capture that is right — the cap must be at the head. For a release it can
never pass: the line-break sensor reports a cap anywhere in the beam, held or not,
so the cap that was just set down is still sitting in the beam directly under the
head. Measured with [`cubos/tools/probe_cap_plane.py`](../tools/probe_cap_plane.py) —
descending onto a cap that was merely *resting* on a vial, magnet off, flipped the
sensor to `True` at exactly the engage plane.

This also contradicts the vendor driver's own docstring in
`instruments/capper/vendors/pawduino.py`: *"capping de-energizes the electromagnet
before retracting, so success is confirmed by the sensor reporting no cap present"*
— i.e. the source protocol confirmed **after** the retract.

### Fix

Split the two directions: capture confirms in place as before; release calls
`release_cap()`, retracts to `safe_z`, and only then runs the sense-and-retry loop.
The later "retract" move is then a no-op for the release path.

### Upstream

Worth sending to `Ursa-Laboratories/CubOS` alongside the boot-banner fix. Not filed yet.

---

## Known upstream bugs found but *not* patched

Recorded here so they are not rediscovered. Both were observed in the same run.

### 1. Failure-retract passes an instrument object where a name is expected

`_best_effort_retract_to_safe_z()` in
`packages/core/src/cubos/protocol_engine/setup.py:360` pulls
`pose["instrument"]` — an instrument **object** — and hands it to
`context.gantry.move()`, which does a name lookup. It always raises:

```
Failure retract to safe_z failed; manual hardware check required:
  "Unknown instrument 'PawduinoCapper'. Available: pipette, vial_capper_decapper"
```

**Impact is limited**, because this is the outer, redundant retract. The inner
`_safe_retract()` in `commands/capper.py:245` is passed the instrument *name* and
does work, so the tool is genuinely lifted to `safe_z` after a capper failure. The
scary-looking "manual hardware check required" line is the second retract failing
after the first already succeeded.

### 2. A failed capture leaves the electromagnet energized

`_confirm_capture_or_release()` in `commands/capper.py:120` calls `capture_cap()`
(`CMD_EMAG_ON`), and on a failed confirmation raises without ever calling
`release_cap()` (`CMD_EMAG_OFF`). `disconnect()` only closes the port.

In practice the coil does get de-energized, because closing the port resets the
Arduino and the sketch brings the pin low — so a `run_protocol` that exits is safe.
It would **not** be safe for a long-lived process that holds the port open across a
failure (e.g. the API server). De-energize explicitly if you hit this:

```bash
~/CubOS/.venv/bin/python - <<'EOF'
import serial, time
s = serial.Serial("/dev/ttyACM0", 115200, timeout=6.0)
s.readline(); s.reset_input_buffer()          # drop the boot banner
s.write(b"6\n"); s.flush(); print(s.readline())   # 6 = CMD_EMAG_OFF
s.close()
EOF
```
