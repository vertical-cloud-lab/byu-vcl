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

## `tipped-hover-clamp-and-ceiling-travel.patch`

**Written and offline-validated 2026-08-25. NOT applied to the Pi** — unlike the two
patches above it changes motion planning for *every* protocol, so applying it is a
deliberate decision, not a bug fix to slip in. Apply it when you want literal
`mix:` / `aspirate:` / `transfer:` / `drop_tip:` commands runnable with a tip on
(they also need the pipette brought online — `offline: false` + a real port — before
any liquid actually moves).

### Symptom

Every engage-based pipette command is rejected on this machine as soon as a 35 mm
tip is attached, no matter what the protocol says:

```
step (mix): mix 'vial_1' safe_z gantry z=149.0 is outside working
  volume [0.0, 122.0] for instrument 'pipette'.
```

The required gantry Z is always **`safe_z + tip_length`** (149 at safe_z 114; 160 if
safe_z is raised to 125), because engage commands hover at `safe_z` measured **at the
tool point** — the tip end, 35 mm below the nozzle — and take no `travel_z`. Raising
`safe_z` therefore makes the number *worse*, 1:1. The machine itself can carry the
tip end across the whole deck at gantry 122 (tip end at deck 87) with clearance;
CubOS just has no way to be told to travel there.

### Fix (three parts, one patch)

1. **Backport upstream `0cc5028`** (*"Travel XY at the working-volume ceiling, not
   the safe_z plane"*, merged upstream 2026-08-24, after the Pi's `cbc33dc`):
   `move_to_labware` XY-travel rides `working_volume.z_max` so every tool on the
   head clears the deck; `safe_z` stays the hover/retract plane.
2. **Hover clamp** (the new part, `instrument_mount.py`): when an instrument's tool
   point is so deep that hovering at `safe_z` needs gantry Z above `z_max` — exactly
   the tipped-pipette case — hover at the highest carriage-reachable plane
   (`z_max − depth − tip`) instead of commanding an impossible Z. A WARNING is
   logged each time. With the current configs: tip end hovers at **87**, carriage at
   **122**, instead of refusing at 149.
3. **Keep offline checks equal to hardware**: `GantryConfig.hover_z()` mirrors the
   clamp in both validators (`validation/bounds.py`, `validation/protocol_semantics.py`),
   and `instrument_loader.py` seeds the working volume into the offline `Gantry`
   (mock runs previously constructed `Gantry(offline=True)` with **no config**, so
   dry-run travel planes silently diverged from hardware). Two upstream tests that
   asserted the old refuse-to-run behavior are updated to the new clamp behavior.

### What changes on the machine when applied

- Capper XY transits ride at gantry **122** instead of 98.065 (24 mm higher than
  the proven 2026-08-03 runs — safer over the deck, slightly slower per hop).
  Capper hover/engage/retract/park planes are unchanged.
- A tipped pipette hovers between labware with the tip end at **87** (gantry 122):
  19 mm above the cap tops (~68), which matches Ben's visual check that the gantry
  at Z 122 clears everything with a tip on. Bare-nozzle behavior is unchanged.
- Explicit `move` + `travel_z` steps are unchanged.

### Caveat that must outlive this patch

The clamp plane is `z_max − tip_length`. With the 35 mm tips that is deck 87 —
plenty. **If the lab ever switches to longer tips** (the `ursa_tip_rack` definition
default is 59.3 mm), the clamped plane becomes 122 − 59.3 ≈ **63 — below the cap
tops**, and the offline validators cannot catch that (they model the machine's fixed
structures, not labware heights; the WARNING log is the only tell). Re-check
`z_max − tip_length` against the tallest deck item whenever tips change.

### Validation

Against `cbc33dc` with both patches above applied: upstream suite 2020 passed /
3 pre-existing failures (two caused by the behavior the earlier patches deliberately
changed, one cwd-sensitive `.gitignore` test — verified identical without this
patch). A literal-`mix` probe protocol with the **unchanged** committed configs:
`validate_setup` PASS, `--mock` 5/5, runtime trace shows
`Moving OpentronsPipette to (187, 26, 87) -> gantry (135, 14, 122)` where unpatched
code commands gantry 149. The committed `pipette_test.yaml` still validates PASS and
mock-runs 27/27 unchanged.

### Upstream

Current CubOS `main` (`5b3376c`) already contains part 1 (`0cc5028`) and still
rejects the tipped hover (verified: same 149/160 failure). Parts 2–3 are the piece
to send to `Ursa-Laboratories/CubOS`. Not filed yet.

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
