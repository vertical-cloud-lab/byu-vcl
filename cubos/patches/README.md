# Local CubOS patches applied on the lab Raspberry Pi

These are changes made to the **upstream CubOS clone** at `~/CubOS` on the lab Pi
(`Ursa-Laboratories/CubOS`). They do not live in that repo, so they are recorded
here to keep the Pi reproducible and to give us something to upstream.

Apply with:

```bash
cd ~/CubOS
git apply /path/to/byu-vcl/cubos/patches/<name>.patch
```

Check what is currently applied with `cd ~/CubOS && git diff --stat`, or per file:

```bash
for p in ~/byu-vcl/cubos/patches/*.patch; do
  git apply --reverse --check "$p" 2>/dev/null && echo "APPLIED: $(basename $p)"
done
```

## What is on the Pi right now

**`rpi-5-des4`, `~/CubOS` detached at `496819c` (upstream `main`), two patches
applied** — migrated 2026-09-15, record in
[`results/cubos_migration_20260915/`](../results/cubos_migration_20260915/README.md).

| patch | state | why |
|---|---|---|
| `p20-gen2-plunger-constants.patch` | **APPLIED** 2026-09-17 | the `p20_single_gen2` plunger planes and volume conversion, from Opentrons' own P20 GEN2 definition. Replaces `p20-mm-to-ul-passthrough.patch`, whose `mm_to_ul = 1.0` it keeps. See below. |
| `tipped-hover-clamp-main.patch` | **APPLIED** | load-bearing. Without it Ben's trio fails validation with 6 violations; a 35 mm tip would need carriage Z 150 on a machine whose Z tops out at 124. |
| `pipette-connect-tolerate-failed-home-main.patch` | **APPLIED** | workaround, not a fix. Revert the moment the plunger limit switch works. |
| `pawduino-connect-boot-banner.patch` | superseded | fixed upstream by `88bf226` (`PawduinoLink`), and **verified against this board**: `connect()` handles the 3.76 s banner in 3.77 s. |
| `cap-release-confirm-after-retract.patch` | superseded | fixed upstream by `3a7f4ab`, and better — upstream re-engages on each retry; ours did not. |
| `tipped-hover-clamp-and-ceiling-travel.patch` | split | upstream took the ceiling-travel half (`0cc5028`/`b39988b`); the clamp is re-ported as `tipped-hover-clamp-main.patch`. |
| `pipette-connect-tolerate-failed-home.patch` | rebased | the `cbc33dc` form, kept only for rollback. |

`tmc2209-softwareserial-read.patch` is the odd one out in this directory: it
patches the **janelia TMC2209 Arduino library**, not CubOS, and belongs to the
firmware build on `~/panda_fw_vcl`. It is filed here because it is a local
third-party patch like the rest. See below.

The four files **without** a `-main` suffix are written against `cbc33dc` and are
only needed to roll back. The migration record has the rollback recipe; note it
also requires removing `cnc.default_feed_rate_mm_min` from the gantry file, which
`CncYaml` at `cbc33dc` rejects.

---

## `p20-gen2-plunger-constants.patch`

The `p20_single_gen2` entry of `instruments/pipette/models.py`: four numbers,
from Opentrons' own definition of the pipette that is physically on the head.
Supersedes `p20-mm-to-ul-passthrough.patch` (2026-09-15), which changed only
`mm_to_ul` and is kept verbatim inside this one.

### Symptom

Two, with different causes. Commanded volumes were not microlitres by a factor
nobody could name; and `blowout`/`drop_tip` aimed the plunger at planes 23–36 mm
away from the ones a P20 GEN2 actually uses.

### Cause 1 — both ends converted

`OpentronsPipette.aspirate`/`dispense`/`mix` each do

```python
mm_travel = volume_ul * self._config.mm_to_ul
```

and send `mm_travel` as the `ASPIRATE` argument — but the PANDA firmware's
`aspirate(float volume, ...)` takes **microlitres** and applies its own
`UL_TO_MM` internally. So `volume_ul: 20.0` became `20 × 0.025 = 0.5`, which the
firmware then clamped up to `MIN_VOLUME` and converted again.

`mm_to_ul` is read in exactly those three places and nowhere else, so `1.0`
makes this side a pass-through and leaves the single conversion in the firmware,
where the calibration constant belongs.

### Cause 2 — the plunger planes were placeholders, and they are absolute

`prime_position: 5.0`, `blowout_position: 7.0` and `drop_tip_position: 10.0`
were all marked `# placeholder`, and unlike `mm_to_ul` they are sent to the
firmware as **absolute `MOVE_TO` targets**. So they did not mis-scale a move —
they named the wrong destination.

The fix is Opentrons
`shared-data/pipette/definitions/1/pipetteModelSpecs.json`, keys
`p20_single_v2.0`/`2.1`/`2.2` (identical positions in all three). Opentrons
states plunger planes as signed offsets in a frame whose `top` is the home
reference; CubOS and the firmware both measure *downward* from home, so each
value is `top - <field>` with `top = 19.5`:

| | Opentrons field | P20 GEN2 | was |
|---|---|---|---|
| `prime_position` | `bottom` −8.5 | **28.0** | 5.0 |
| `blowout_position` | `blowout` −13 | **32.5** | 7.0 |
| `drop_tip_position` | `dropTip` −27 | **46.5** | 10.0 |
| `mm_to_ul` | — | **1.0** (pass-through) | 0.025 |

`max_volume` 20.0, `min_volume` 1.0 and `zero_position` 0.0 were already right.

All three planes moved **down**, so every commanded plunger travel is shorter
than before, and the ordering `0 < prime < blowout < drop_tip` that
`aspirate`/`dispense`/`moveTo` rely on is preserved.

### Chain, end to end

```
protocol volume_ul  20.0
  x mm_to_ul 1.0     -> ASPIRATE 20.0            (CubOS, this patch)
  x UL_TO_MM 1.34    -> 26.8 mm of plunger       (firmware, ../firmware/)
                        from PRIME 28.0, landing at 1.2 mm -- inside the
                        28 mm stroke with a small dead band, as Opentrons
                        has it
```

The firmware side carries the same three planes; the two files agree by
construction. See [`../firmware/README.md`](../firmware/README.md) and
§10.4 of [`../docs/opentrons-pipette-wiring.md`](../docs/opentrons-pipette-wiring.md).

### Still not calibrated

These are Opentrons' figures for the **model**, not a measurement of this unit.
`UL_TO_MM` needs a gravimetric check once liquid actually moves. Until then a
commanded microlitre is nominal, not verified.

### Upstream

Not filed. Worth sending: upstream's `p20_single_gen2` entry is entirely
placeholders, and these four numbers come from Opentrons rather than from this
machine, so they are correct for anyone with a P20 GEN2 — not VCL-specific.
The same is true of the `p300_single_gen2` entry, which carries 36.0 / 46.0 /
60.0 against Opentrons' 34.0 / 38.5 / 56.5. That one was **left alone**: it is
not the pipette on this machine, and changing an unused model adds risk without
being asked for.

---

## `tmc2209-softwareserial-read.patch`

**Not a CubOS patch.** It patches the janelia TMC2209 Arduino library, vendored
into `~/panda_fw_vcl/lib/TMC2209/` for the firmware build.

### Symptom

`CMD_PIPETTE_DRIVER_STATUS` (command 29, added 2026-09-15) always returned
`comm = 0`, which this repo read as proof that no TMC2209 register write had
ever landed. **That conclusion was wrong** — see §10.1 of
[`../docs/opentrons-pipette-wiring.md`](../docs/opentrons-pipette-wiring.md).

### Cause

A read over `SoftwareSerial` on an AVR cannot succeed with this library at all,
whatever the wiring. `SoftwareSerial::write()` runs `cli()` for the duration of
each transmitted byte, so the Arduino never receives its own transmission back
on the shared single-wire link. But `sendDatagramBidirectional()` waits for
`datagram_size` bytes and then **discards them as echo** — and with no echo, the
bytes that arrive in that window are the driver's 8-byte reply. The first four
are thrown away, `readReply()` waits for eight more, times out, retries 5×, and
`isCommunicating()` reports false.

Diagnosed by Ursa (Alex Carlson), byu-vcl issue #133, 2026-09-17. The janelia
README says software serial "should only be used for unidirectional
communication" for exactly this reason.

### Fix

Skip the echo wait-and-discard block when `software_serial_ptr_` is set. Writes
are unaffected either way — they need no echo — so this changes only the read
path.

### ⚠️ Not sufficient on its own

The bridge resistor must also move to the **TX side**: `A1 -> 1k -> node`, with
`A0` and `PDN_UART` connected directly to the node, per TMC2209 datasheet §4.3
fig 4.1 and the janelia "coupled" diagram. With `A1` wired straight to
`PDN_UART` and the resistor only on the `A0` leg, the Arduino's push-pull TX
shorts out the driver's reply. **That is a bench change.**

### Why it is vendored rather than applied in `.pio/libdeps/`

`.pio/libdeps/` is PlatformIO's dependency cache and can be re-resolved at any
time, which would silently drop the patch. `lib/` is the project-local private
library directory and takes precedence. **Verified rather than assumed:**
inserting a sentinel `#error` into the `lib/` copy fails the build, so that copy
is provably the one being compiled.

```bash
# how it was created, and how to recreate it after a library bump
cd ~/panda_fw_vcl
cp -r .pio/libdeps/uno/TMC2209 lib/
git apply --directory=lib/TMC2209 ~/byu-vcl/cubos/patches/tmc2209-softwareserial-read.patch
```

### Upstream

Not filed. Worth sending to `janelia-arduino/TMC2209` — the library already
documents that reads do not work over software serial, so the honest fix is
either this guard or a compile-time error.

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

**Written and offline-validated 2026-08-25. APPLIED to the Pi on 2026-08-31**, at
@benwhitney5463's request on PR #171, after the campaign-33 video showed the head
travelling ~16 mm lower than the jogged `safe_z` and knocking caps off the
electromagnet. Unlike the two patches above it changes motion planning for *every*
protocol, which is why it sat unapplied for six days.

It is what makes `cnc.safe_z: 115.0` possible on this machine. Without it a tipped
pipette must hover at `safe_z + 35`, so `safe_z` is capped at `z_max - 35 = 89`, and
the capper — which shares `safe_z` — is dragged down with it. The clamp decouples
them: capper legs ride at gantry 99.065 while the tipped hover clamps to gantry 124.

Confirmed live in the rev-2 trio's mock trace, once per tipped engage:

```
OpentronsPipette cannot reach safe_z 115.000 (tool point rides 35.000 below the
carriage; ceiling 124.000). Hovering/traveling at 89.000 instead — confirm this
plane clears all deck contents.
```

**⚠️ If this patch is ever reverted (`git apply -R`), `cnc.safe_z` in
`configs/gantry/cub_xl_ben_pipette_capper.yaml` must go back to ≤ 89.0** or nothing
with a tip attached will validate. The two numbers are coupled.

It does *not* clamp an explicit `move` target or `travel_z` you wrote by hand — those
stay hard requirements, deliberately. See the rev-2 `pipette_test.yaml` header for the
one place that bites.

Liquid still needs the pipette's plunger fixed independently: bench-tested 2026-08-31,
the stepper only turns one way (`results/pipette_bench_20260831/`).

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

---

## `pipette-connect-tolerate-failed-home.patch`

**Written 2026-09-01. APPLIED to the Pi 2026-09-01 19:01 UTC** so the shortened
`pipette_test.yaml` could run after the rewiring left homing still broken
(campaign 69, `cubos/results/pipette_test_20260901c/`). **Revert it the moment
the limit switch works** — it is the one patch here that is not a bug fix.

### Symptom

Every `run_protocol` with the pipette live (`offline: false`) aborts at instrument
connect, before the gantry is homed and before any G-code is sent:

```
CONNECT FAILED in 56.5s: PipetteConnectionError(
  'Plunger home/prime after connect failed: Command 10 failed:
   ERR:{"error":"Failed to home pipette"}')
```

### Cause

`OpentronsPipette.connect()` sees the firmware's `homed: 0` after the port-open
reset and calls `home()`, which already retries once — its own comment explains
why: *"Firmware gives up after ~31 mm of upward travel per attempt, but full
plunger travel is 55 mm: a plunger parked low needs a second leg to reach the
limit switch."* On the CubXL **both** legs run their full budget, 26.35 s each,
so ~62 mm is swept against a 55 mm range and the switch is never seen. Measured
four times on 2026-09-01, identical to the centisecond and independent of the
starting position — see `cubos/results/pipette_test_20260901b/README.md`.

Upstream's refusal is **correct**: without a home the firmware's position counter
is meaningless, so absolute `MOVE_TO` targets land somewhere unknown and a
commanded volume is not a volume.

### What the patch does

Turns the refusal into a `logger.warning` and continues with `_is_homed = False`,
so motion testing can proceed while the limit switch is being fixed. It does not
make volumes real, and it should be reverted the moment homing works.

This is the one patch here that is **not** a bug fix — the other three correct
upstream defects. Apply it only for a deliberate motion test:

```bash
cd ~/CubOS && git apply ~/byu-vcl/cubos/patches/pipette-connect-tolerate-failed-home.patch
# revert with: git apply -R ~/byu-vcl/cubos/patches/pipette-connect-tolerate-failed-home.patch
```

Verified with `git apply --check` against the Pi's tree (`cbc33dc` + the three
applied patches) on 2026-09-01, then applied the same day.

### What it looked like in practice (campaign 69, 2026-09-01)

The run reached all 12 steps and every plunger command actuated. One side effect
worth knowing: the exception is raised inside `self.home()`, **before**
`self.prime()`, so `prime` never runs while this patch is carrying a failed home
— the plunger starts the protocol at firmware counter 0 rather than 5.0.


---

# Rebased onto upstream `main` — prepared, **not applied**

Both apply cleanly to `496819c` and together produce **2544 passed, 0 failed** on
`packages/core/tests` — the same count as pristine `main`, because each patch
rewrites the upstream tests whose behaviour it changes. Full evidence and the
migration recipe: [`cubos/results/cubos_update_audit_20260915/`](../results/cubos_update_audit_20260915/README.md).

## `tipped-hover-clamp-main.patch`

The `main` port of `tipped-hover-clamp-and-ceiling-travel.patch`, and much smaller
than it, because upstream took the ceiling-travel half at `b39988b` (2026-09-02):
`InstrumentedGantry.move()` now lifts to `multi_tool_safe_travel_z` before any XY
change without an explicit `travel_z`, and `decap`/`cap` no longer park at all.

What upstream did **not** take is the hover clamp, and without it Ben's committed
trio fails on `main` with six violations:

```
- pipette -> tip_rack.A1.safe_z: gantry (284.0, 25.5, 150.0) violates z_max=124.0
- step 4 (aspirate): safe_z gantry z=150.0 is outside working volume [0.0, 124.0]
```

`move_to_labware` still ends at `safe_z` measured *at the tool point*, so a 35 mm
tip needs the carriage at `115 + 35 = 150` on a machine whose Z tops out at 124.
`multi_tool_safe_travel_z` cannot help — it is a `max()`, so it never clamps down.

The patch adds `GantryConfig.hover_z(instrument, tip_extension=...)`, clamps the
hover target in `move_to_labware` (logging a WARNING each time), mirrors the clamp
at four call sites in `validation/bounds.py` and three in
`validation/protocol_semantics.py`, and seeds the mock controller's working volume
from the loaded config so dry runs plan the same motion as hardware.

## `pipette-connect-tolerate-failed-home-main.patch`

The `main` port of `pipette-connect-tolerate-failed-home.patch`, rebased onto the
new `PawduinoLink` connect path (`self._release_link()` replaced
`self._close_serial()`). Upstream's refusal is unchanged at `main`, so the escape
hatch is still needed while the plunger limit switch does not assert.

**Still the one patch here that is not a bug fix.** Revert it the moment the switch
works; it is inert whenever `home()` succeeds.

## Two patches that `main` makes unnecessary

- **`pawduino-connect-boot-banner.patch`** — superseded by `PawduinoLink`
  (`88bf226`, 2026-08-20), which drains the port and then does a `CMD_HELLO`
  round-trip with `expect="Hello"` that skips stale lines. That is a resync rather
  than a longer sleep, so it is robust to our measured 3.76 s banner. Verified that
  `CMD_HELLO = 0` exists in the firmware this machine runs (`BU-KABlab/PANDA_Arduino`,
  `src/Interface.cpp:143` → `"Hello from Pawduino!"`). `PawduinoLink` also fixes the
  unarbitrated shared `/dev/ttyACM0` flagged on 2026-08-26.
- **`cap-release-confirm-after-retract.patch`** — fixed upstream at `3a7f4ab`
  (2026-08-28), and better than ours: it re-engages before re-actuating on each
  retry, which ours did not.

## Why the Operator UI's Update button will not work here

`deploy/pi/update.sh` runs `git checkout --detach <target>` against the live tree.
Any applied patch makes git refuse, and the abort happens before `ROLLBACK_READY=1`,
so it fails clean and leaves the machine where it was — but it can never succeed
while a patch is applied. Independently, this Pi has no `cubos_api` install, no API
server, no `cubos` systemd service and no `npm`, so the button does not exist on it
yet. A gitops updater and a locally patched appliance are mutually exclusive; the
durable fix is upstreaming the clamp so we carry no patches at all.
