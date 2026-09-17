# CubOS on the VCL Raspberry Pi

Provenance for the first CubOS install and hardware protocol run on the lab's
Raspberry Pi 5 (the OT-2 / stream-camera Pi), performed 2026-07-27 via
[issue #165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165).

## What lives where on the Pi

- CubOS checkout: `~/CubOS` (clone of [Ursa-Laboratories/CubOS](https://github.com/Ursa-Laboratories/CubOS)), venv at `~/CubOS/.venv` with `packages/core` installed (`pip install -e packages/core`)
- Configs (copies of `configs/` here, with `serial_port` set to `/dev/ttyUSB0`):
  - `~/CubOS/packages/core/configs/gantry/cubxl_vcl_1_instrument.yaml`
  - `~/CubOS/packages/core/configs/deck/vcl_deck.example.yaml`
  - `~/CubOS/packages/core/configs/protocol/vcl/vial_scan.example.yaml`
- Run data store: `~/.cubos/panda_data.db`; result CSV exports under
  `~/CubOS/packages/core/src/cubos/data/results/`

## How the protocol was run

```bash
cd ~/CubOS
.venv/bin/python -m cubos.tools.validate_setup  <gantry> <deck> <protocol>  # offline check
.venv/bin/python -m cubos.tools.run_protocol --mock <gantry> <deck> <protocol>  # offline dry-run
.venv/bin/python -m cubos.tools.run_protocol        <gantry> <deck> <protocol>  # hardware
```

with the three config paths above. The hardware run (campaign 2) homed the
CubXL, visited all 8 vial scan positions at deck-frame Z 63 with travel Z 85,
parked, and re-homed: 12 steps, started 20:51:19 UTC, completed 20:53:43 UTC.
CSV exports for that campaign are in `results/campaign_2_20260727_205119/`
(motion-only protocol, so the experiment/measurement tables are empty).

## Capper/decapper test protocol (PASSED on hardware 2026-08-03)

`configs/protocol/vcl/capper_decapper_test.yaml` (vials 2–7: decap → pipette
insertion → cap) completed 27/27 steps on the CubXL on 2026-08-03 with the
re-measured `cub_xl_ben_pipette_capper.yaml` + `sterling_deck.yaml`. Full
attempt-by-attempt history in `results/capper_decapper_test_20260803/README.md`.

## Tip-pickup capper test protocol (written 2026-08-06, NOT run)

`configs/protocol/vcl/capper_decapper_tip_test.yaml` extends the above for the
re-measured 6-vial deck (`configs/deck/sterling_6vials.yaml`, which adds a
1×1 `tip_rack` at (255.5, 33.5), pickup Z 60, 35 mm tips): park → decap →
`pick_up_tip` → insert (tip modeled by CubOS) → cap, for vials 1–6.
**Currently blocked**: all six vials sit at deck X ≈ 113, but the pipette
(`offset_x: 135.0`) cannot reach below deck X 135, so the 12 insert/retract
moves fail `validate_setup` at gantry X −22. A +30 mm shift of every vial
`location.x` (plus the matching protocol positions) validates PASS and
mock-runs 28/28. See the protocol header for the full analysis, including the
tip-shadow corridor the offline validator cannot see.

## Tip-pickup capper test, j_config_1 deck (written 2026-08-08, NOT run)

`configs/protocol/vcl/capper_decapper_tip_test_j1.yaml` is the same
park → decap → `pick_up_tip` → insert → cap sequence retargeted at
@jarrettshupe's setup: the gantry was **re-calibrated and the pipette
physically remounted** (offset 135/13 → 51.97/12 — which fixes the X-reach
blocker above), and `configs/deck/j_config_1.yaml` uses a new measurement
convention where each vial's `location.z` is the raw jog-widget WPos at which
the capper engages the cap (paired with `engage_depth_mm: 17.248 = -depth` in
the gantry config). The tip position was measured in the capper's reference
frame and converted (+51.97, +12.0 in XY) in the deck's `tip_rack` entry.
`validate_setup` PASS, `--mock` 28/28. **The older sterling configs/protocols
no longer describe the machine** — their numbers predate the remount. See the
protocol header for the passive-pipette corridor that must be eyeballed
before any hardware run. **Superseded 2026-08-24:** the gantry was
re-calibrated again (next section), so the j_config_1 numbers in turn no
longer describe the machine.

## Sterling 6-vial + Ursa tip rack deck (added 2026-08-24, NOT run)

`configs/deck/sterling_6vials_tiprack.yaml` is @benwhitney5463's re-measured
6-vial column (deck X 187, Y 26–191, rim Z 55) plus the CubXL docs' standard
tip rack (`load_name: ursa_tip_rack`: 2 columns × 15 rows = 30 tips, 8.5 mm
pitch, body 66 × 138 × 22 mm), anchored by one measured point — the
bottom-right tip, jogged in the capper's reference frame to WPos (265, 1),
converted to the pipette deck frame (317, 13) = tip `A1`. The second
calibration point is derived from the docs' pitch, not measured (rack assumed
square to the axes; see the deck header for the mirrored-rack fallback).
`pickup_z: 60.0` is carried from Ben's 2026-08-06 measurement — confirm by
jog before the first hardware pickup.

The paired `configs/gantry/cub_xl_ben_pipette_capper.yaml` is Ben's
2026-08-24 re-calibration (working volume 386.333 × 232.0 × 122.0, capper
depth −15.935 / engage_depth 13, pipette offset 52.0 / 12.0, park [125, 50]),
committed byte-identical to the attachment — it already carried
`/dev/ttyUSB0`, so for the first time no port edit was needed. Offline
checks: `validate_setup` PASS and a 7-step `--mock` (corner-tip hovers +
`pick_up_tip: tip_rack.A1` + a tipped move) pass; commanding the pipette to
`tip_rack.A1` reproduces the measured WPos (265.0, 1.0) exactly.

## pipette_test protocol (shortened, 2026-09-01 rev 3) — RAN ON HARDWARE, 12/12

Campaign 73, `19:23:23 → 19:28:39` UTC (5 m 16 s), status `completed`. Same
trio as campaign 69, unchanged, run after another rewiring pass. Gantry and
capper clean; `validate_setup` PASS, `--mock` 12/12, `passive_shadow` 0
interferences nominal **and** tip-stuck.

**The plunger did not move, and made no sound** — reported by
@benwhitney5463 watching the machine. The trace is byte-for-byte the shape of
campaign 69's: both directions scaling at ~0.665 s/mm. That is the finding:
`stepMotor()` bit-bangs the STEP pin and counts, with **no feedback of any
kind**, so those timings prove the *Arduino emitted the steps* and nothing
about the motor. Everything upstream of STEP/DIR works; the TMC2209 is not
driving the coils, and total silence means no coil current at all.

Root cause found in the firmware source: the Cubware wiring diagram's four
Arduino→TMC2209 signal lines are each **shifted one analog pin** from the pin
map in [`BU-KABlab/PANDA_Arduino`](https://github.com/BU-KABlab/PANDA_Arduino),
and **A4 — the firmware's `ENABLE_PIN` — is connected to nothing**. Full
analysis, corrected wiring table, the pipette's 10-pin mapping, and the
knock-on effects on microstepping and volume units:
[`docs/opentrons-pipette-wiring.md`](docs/opentrons-pipette-wiring.md). Run
write-up: [`results/pipette_test_20260901d/README.md`](results/pipette_test_20260901d/README.md).

Reading the firmware also closed several open questions: `ASPIRATE 0.5` →
`35.45` is exact arithmetic (`aspirate()` primes to 36.0, clamps the argument
up to `MIN_VOLUME 5.0` µL, targets `36.0 − 5×0.1098`); 0.673 s/mm is
`MOVEMENT_VELOCITY 2500` × `STEPS_PER_MM 1592`; `HOME`'s 26.35 s is the
50 000-step budget in `homePipette()`, so the seek ran to completion and D9
never went HIGH; and `max_vol: 300.00` is `MAX_VOLUME 300.0` — the firmware is
built for a P300.

## pipette_test protocol (shortened, 2026-09-01 rev 2) — RAN ON HARDWARE, 12/12

Campaign 69, `19:01:52 → 19:07:08` UTC (5 m 16 s), status `completed`.
The first run in which every plunger command was **issued and stepped** rather
than declined — `blowout` and `drop_tip` had returned in a flat ~0.1 s on every
previous run. (Read at the time as "actuated". Campaign 73 showed that the
firmware stepping and the plunger moving are different things; see above.)

The trio is the one committed at `abd81d6`, run unchanged: @benwhitney5463's
shortened protocol (vials 3–5 commented out, 18 → 12 steps, `height` on
`aspirate`/`blowout` deepened from −15.0 to −35.0) with the deck and gantry
files untouched.

@benwhitney5463 rewired the pipette between the previous session's observed
`USB disconnect` (18:26 UTC) and `/dev/ttyACM0` re-enumerating (18:50 UTC). The
rewiring **kept** the direction fix and did **not** fix homing: `HOME` still
fails after 26.35 s, identically from pos 0.0 and pos 3.0, so the limit switch
never asserts anywhere in the plunger's travel.

To run it, `patches/pipette-connect-tolerate-failed-home.patch` was **applied**
to the Pi — it downgrades `OpentronsPipette.connect()`'s refusal to a warning
and continues with an unreferenced plunger. Revert it once the switch works.

Every plunger `MOVE_TO` in the run scaled at 0.663–0.666 s/mm, two of them
backwards in the firmware's counter (`blowout` 28.45 mm in 18.862 s;
`drop_tip`'s second leg 5.00 mm in 3.322 s). Offline gates on the Pi's exact
CubOS: `validate_setup` PASS (12 steps), `--mock` 12/12, `passive_shadow` 0
interferences nominal **and** tip-stuck.

The `ASPIRATE 0.5` → 35.45 reading, flagged here as unexplained, is resolved:
it is the firmware clamping the argument to `MIN_VOLUME 5.0` µL and priming to
`PRIME_POSITION 36.0` first. Full write-up:
[`results/pipette_test_20260901c/README.md`](results/pipette_test_20260901c/README.md).

## pipette_test protocol (shortened, 2026-09-01 rev 2) — offline analysis, before the run

`configs/protocol/vcl/pipette_test.yaml` is @benwhitney5463's shortened revision:
vials 3–5 commented out (18 → 12 steps) and `height` on `aspirate`/`blowout`
deepened from −15.0 to −35.0. The deck and gantry files are unchanged.

Every offline gate passes on the Pi's exact CubOS — `validate_setup` PASS (12
steps), `--mock` 12/12, `passive_shadow` 0 interferences nominal **and**
tip-stuck — and the deeper insert clears the vial floor by ~45 mm (CubOS
documents a vial's `height` as the outer rim→underside dimension, so
`height: 83` with the rim at deck 55 puts the underside at deck −28).

It did not run. **The plunger direction fault is fixed** — retractions move and
round-trip time scales with distance both ways — but `HOME` now fails after
26.35 s per attempt, identically on four attempts and independent of starting
position, and `OpentronsPipette.connect()` refuses to connect without a plunger
reference. That happens before the gantry is homed, so 0 steps ran and no motion
was commanded. The evidence points at the limit-switch **input** rather than the
motor drive: before the rewiring `HOME` returned 0.52 s claiming success (switch
reading permanently asserted); it now never asserts.

`patches/pipette-connect-tolerate-failed-home.patch` was written here and left
unapplied at the time; it was applied the same day for campaign 69 (above).
Full write-up:
[`results/pipette_test_20260901b/README.md`](results/pipette_test_20260901b/README.md).

## pipette_test protocol (revised 2026-09-01) — RAN ON HARDWARE, 18/18

`configs/protocol/vcl/pipette_test.yaml`, `configs/deck/ben_6vials_tiprack.yaml`
and `configs/gantry/cub_xl_ben_pipette_capper.yaml` hold @benwhitney5463's
2026-09-01 revision, run on the CubXL that day: **18/18 steps, 5m 50s,
campaign 54, status `completed`**, no capper retries and no alarms.

This is the first rev in which every offline gate is clean *including*
`passive_shadow --tip-stuck` (0 interferences) — `safe_z: 115` lifts capper
transits to gantry 99.065 and `park_position: [236, 175]` puts the passive
pipette's sweep at deck X 288–336, clear of the vial column. The
`travel_z` 100 → 87 fix on the tipped `move` is what made it validate:
`travel_z` resolves in the moving instrument's tool frame, so 100 with a
35 mm tip is gantry 135, past `z_max` 124.

Two things it also settled by measurement rather than by argument:

* **The tip-rack anchor is already in the pipette's deck frame.**
  `pick_up_tip` commanded gantry (284.0, 25.5, 57.0) — exactly the measured
  jog point — so a1 `(336.0, 37.5)` needs no further +52/+12 conversion.
  `validate_setup` passes either way, so only the G-code could tell.
* **The plunger's one-way fault survived the rewiring.** Every plunger
  command was timed during the run: forward moves scale at 0.673 s/mm,
  every retraction returns in ~0.11 s without moving. So `pick_up_tip`,
  `blowout` and both `drop_tip` legs were no-ops; only the connect-time
  prime and the `aspirate` actually turned the motor. The mounted pipette is
  a p20 (confirmed by @benwhitney5463) while the Arduino firmware still
  reports `max_vol: 300.00`.

Full write-up, including the accumulated one-way plunger travel that needs an
inspection:
[`results/pipette_test_20260901/README.md`](results/pipette_test_20260901/README.md).

`tools/run_with_plunger_trace.py` is the wrapper used to capture that trace —
it wraps `OpentronsPipette._send_command` to record (code, args, elapsed,
reply) and calls straight through, so run behaviour is unchanged.

## pipette_test protocol (revised 2026-08-31) — RAN ON HARDWARE, 18/18

`configs/protocol/vcl/pipette_test.yaml`, `configs/deck/ben_6vials_tiprack.yaml`
and `configs/gantry/cub_xl_ben_pipette_capper.yaml` hold @benwhitney5463's
2026-08-31 revision, run on the CubXL that day: **18/18 steps, 4m 39s, campaign
33, no retries.** First run in which the pipette's own `aspirate` / `blowout` /
`drop_tip` executed on hardware. The protocol is the corrected 2026-08-28 rev-2
with vial_6 removed; its body is verbatim, only the header was rewritten.

Two edits were needed to make it runnable, both documented inline:

* **Gantry** — `grbl_settings.max_travel_{x,y,z}` synced 389.333/235/125 →
  **409/309/124** to match the controller. Those three are in
  `Gantry._validate_grbl_settings`' critical set, so until they agreed every run
  aborted at connect with *"Critical GRBL settings mismatch"*. `working_volume`
  was deliberately left tighter.
* **Deck** — the tip-rack anchor converted from the reference instrument's frame
  into the pipette's deck frame, `(284, 25.5)` → **`(336.0, 37.5)`** (`+52/+12`).
  The measurement was taken with the pipette tip hovering, but the jog display
  reports the capper. Verified through the loader: `pick_up_tip: tip_rack.A1`
  then commands gantry (284.0, 25.5, 60.0), the measured point exactly. Note
  `validate_setup` passes either way — it checks reachability, not correctness.

This run also settled the deck-frame ambiguity flagged on 2026-08-28: `decap
vial_1` captured on the first attempt, so the vial column really is at
y 27..192 in the post-recalibration frame. Had it been stale the sensor
interlock would have aborted at step 2 over bare deck. Full write-up, the
verification matrix and what remains open (`drop_tip` releasing 35 mm above the
slot, unverified `pickup_z`, the `max_vol 300` vs `p20_single_gen2` mismatch) in
[`results/pipette_test_20260831/README.md`](results/pipette_test_20260831/README.md).

`safe_z: 87` with capper `park_position: [206, 50]` is what makes this work
without patching CubOS: the tipped hover lands on gantry 122 (= `z_max`) and
every capper leg is a pure-Y move that holds the passive pipette 52 mm clear of
the vial column. `cub_xl_ben_pipette_capper_tipsafe.yaml` plus
`patches/tipped-hover-clamp-and-ceiling-travel.patch` remain the alternative
route (0 interferences even with a stuck tip) but were not needed.

## Plunger + travel-height diagnosis (2026-08-31, read-only — nothing commanded)

`results/pipette_diagnosis_20260831/` answers three things Ben raised after
watching campaign 33 run.

**The head travels below the `safe_z` you jog to, by `depth`.** CubOS commands
`gantry_z = safe_z + depth`, and the jog widget shows raw WPos with no
instrument offset. At `safe_z: 87` with the capper's `depth: -15.935`, every
capper leg runs at gantry **71.065** — 15.935 mm lower than a jog to 87. The
bare nozzle (`depth: 0.0`) is the lowest thing on the head and rides at that
same deck Z. Held-cap clearance over neighbouring caps works out to
`safe_z − 81`, so **lowering `safe_z` makes both the rail proximity and the
cap knock-off worse**, not better.

**`working_volume.z_max` must stay ≤ 124.** The controller still reports
`$132 = 124.000` with `$20 = 1`; reachable deck-frame Z is `[0, 124]`. Unpatched,
the tipped hover pins `safe_z ≤ z_max − 35`, so 89 is the ceiling. Going higher
needs `patches/tipped-hover-clamp-and-ceiling-travel.patch`.

**The plunger's absolute moves are no-ops.** `aspirate` and `blowout` share an
identical preceding 47 mm descent; the aspirate step took 8.068 s and the
blowout 2.216 s. Command 12 (relative ASPIRATE) runs the stepper; command 11
(absolute MOVE_TO — which is what `blowout`, `drop_tip` and `pick_up_tip` all
use) returns in ~0.1 s for targets of 0, 5, 7 and 10 mm alike. The plunger was
also never homed: instrument connect took 12.4 s for both instruments against
a ~35 s homing pass, and `OpentronsPipette.home()` sets `_is_homed = True`
without re-reading the firmware. `tools/pipette_bench_check.py` isolates the
plunger from the protocol engine to separate wiring from firmware; it is
read-only unless given `--move`.

## pipette_test protocol (revised 2026-08-28, NOT run — do not run as attached)

`configs/protocol/vcl/pipette_test.yaml` and
`configs/deck/ben_6vials_tiprack.yaml` hold @benwhitney5463's 2026-08-28
revision (bodies exactly as attached to PR #171; parsed YAML verified
identical, headers rewritten). The deck follows a machine recalibration —
vials moved to x 206, y 27..192 — and supersedes
`sterling_6vials_tiprack.yaml`. The protocol adds a real `aspirate` in
vial_1, `cap` vial_1, `decap` vial_2, `blowout` in vial_2, then `drop_tip`.

It was **not** run: the Pi was off the tailnet all session (last seen
2026-08-28 00:26 UTC). Independently, **the trio as attached must not be
run.** It passes `validate_setup` and `--mock`, and it still shears the
attached tip sideways out of vial_1 on step 5 — both offline gates only
check the instrument a command names, never the other tool on the head.

Use `configs/gantry/cub_xl_ben_pipette_capper_tipsafe.yaml` (`safe_z: 122`,
capper `park_position: [206, 50]`) **together with**
`patches/tipped-hover-clamp-and-ceiling-travel.patch` applied on the Pi.
Verified 0 interferences, including the case where the tip never leaves the
nozzle. Neither half works without the other; the analysis, the geometric
reason no value of `safe_z` can fix it, and the `drop_z` answer are in
[`results/pipette_test_20260828/README.md`](results/pipette_test_20260828/README.md).

`tools/passive_shadow.py` was added for this: it mock-runs a protocol,
expands each pose into the driver's real per-axis G-code segments, and
sweeps the *passive* instrument through them against the deck's labware.
Run it alongside `validate_setup` on anything that mixes the capper and a
tipped pipette.

## pipette_test protocol (revised 2026-08-26, NOT run)

`configs/protocol/vcl/pipette_test.yaml` and
`configs/gantry/cub_xl_ben_pipette_capper.yaml` now hold @benwhitney5463's
2026-08-26 revision, committed exactly as attached to PR #171 (comments added,
no values changed). The revision swaps the `move`-stroke substitutions for
literal `mix:`/`drop_tip:`, drops `safe_z` 114 -> 87 to make those validate,
and brings the pipette online on the capper's `/dev/ttyACM0`.

It was **not** run: the runner lost tailnet access when the `Connect to
Tailscale` step was removed from `main`'s workflow. The offline audit —
validation matrix across three CubOS versions, the ~3 mm cap clearance that
`safe_z: 87` buys, the placeholder plunger constants, and the unarbitrated
shared serial port — is in
[`results/pipette_test_20260826/README.md`](results/pipette_test_20260826/README.md).

## pipette_test protocol, original revision (written 2026-08-25, NOT run)

`configs/protocol/vcl/pipette_test.yaml` retargets the capper test at the
2026-08-24 deck/gantry pair above: park → decap vial_1 → `pick_up_tip`
tip_rack.A1 → three tip-frame mix strokes inside vial_1 (40↔48) → tipped
move to the park position → `breakpoint` (tip comes off **by hand**; run
from a foreground terminal — headless runs skip the stop) → cap vial_1 →
decap+cap vials 2–6 → home. `validate_setup` PASS, `--mock` 27/27.

Two requested commands are deliberately absent, with the full analysis in
the protocol header: the literal `mix:` and `drop_tip:` commands travel at
safe_z **in the tip frame** (114 + 35 = gantry Z 149 on a 122 mm machine),
so `validate_setup` rejects them on this hardware and no protocol/deck edit
can route around it — that needs a CubOS change (engage commands have no
`travel_z`) plus an online pipette before the ejector/plunger are real. The
tip rack's `drop_z` is read by **no command** at this CubOS version
(`cbc33dc`); a runnable `drop_tip` targets a separate `tip_disposal` deck
entry and uses that entry's own `location.z`.

**Update 2026-08-25:** the CubOS change now exists as
`patches/tipped-hover-clamp-and-ceiling-travel.patch` — offline-validated
but **deliberately NOT applied to the Pi** (it changes motion planning for
every protocol; see the patch entry in `patches/README.md` for what moves
differently and the longer-tip caveat). With it applied, a tipped engage
hovers at tip-end Z 87 / gantry 122 instead of being rejected at 149.

## Notes

- The gantry enumerates as `/dev/ttyUSB0` on the Pi; the original config's
  `serial_port: COM6` is Windows-specific and was the only edit needed.
- The potentiostat instrument is configured `offline: true`, so the base
  `cubos` install suffices — no vendor SDK extra needed for motion-only runs.
- The Pi's OT-2 overhead camera stream (port 8000) kept running throughout;
  CubOS's API port 8742 remains free for the Operator UI later.

## 2026-08-31 (rev 2) — hover-clamp patch applied, plunger root-caused

`patches/tipped-hover-clamp-and-ceiling-travel.patch` is now **applied** to
`~/CubOS` on the Pi (all three local patches live). That is what lets
`cnc.safe_z` rise from 87 to **115**, which is the fix for both symptoms in
the campaign-33 video: the bare nozzle now rides at deck 99.065 during
capper legs instead of 71.065, and a gripped cap clears its neighbours by
30 mm instead of 6. `passive_shadow` reports **0** interferences nominally
*and* with `--tip-stuck` — the first time the tip-stuck case has been clean.

**The plunger only turns one way.** Bench-tested directly against the
Arduino: `MOVE_TO` executes only when the target is above the current
position, any retraction returns `OK` in 0.11 s without moving, and `HOME`
zeroes the counter rather than seeking the endstop. That is the complete
explanation for campaign 33's blowout and drop_tip doing nothing — `aspirate`
ran, left the plunger at pos 36, and every later command was a retraction.
It is a DIR-line/firmware fault, not CubOS, not the shared `/dev/ttyACM0`,
and no config change works around it. Full evidence and the command matrix:
`results/pipette_bench_20260831/README.md`.

The rev-2 trio fails validation on one number — a tipped `move` at
`travel_z: 100` resolves to gantry 135, past `z_max` 124. `travel_z: 89` in
the two places that name the pipette makes it PASS, 18 steps; the corrected
copy is in that same results directory. Not run: Ben asked for the bench
test only.

## 2026-09-01 (rev 3) — campaign 77, 12/12, and the plunger fault is ONE PIN

Ben's rev-3 protocol (`park_position [206, 25, 115]`, step 1 `travel_z: 115`)
ran on the CubXL as **campaign 77, 12/12 steps, 4m 3s, `completed`** — no
capper retries, no alarms. `validate_setup` PASS, `--mock` 12/12, and
`passive_shadow` **0 interferences nominal and 0 with the tip modeled as
stuck**. The `travel_z` change did what it was meant to: step 1's transit
rises from gantry 84.065 to **99.065**, the same plane every other capper leg
rides. All three config files ran exactly as committed.

**Correction to the 2026-08-31 and 2026-09-01 (b, c) write-ups: there is no
plunger "direction fault".** Both symptoms — `HOME` returning instantly, and
retractions being refused in ~0.11 s — come from a single reading of a single
input, and `BU-KABlab/PANDA_Arduino` `src/Pipette.cpp` says so outright:
`stepMotor()` aborts a move when `digitalRead(PIPETTE_LIMIT_PIN) == HIGH &&
digitalRead(DIR_PIN) == LOW`, i.e. any *up* move, after 1 step + the 100 ms
debounce; and `homePipette()` checks the same pin before its first step, so an
asserted switch makes homing a 0.52 s no-seek back-off. D9 is `INPUT_PULLUP`
and HIGH means "at the limit", so an **open switch circuit reads asserted**.

That single table reproduces all four rewiring passes exactly, including this
one, where the switch went back to asserted. The wire to check is pipette
**pin 6 → Arduino GND** (the Cubware diagram labels it but draws no wire),
then pin 7 → D9, then that the contact is normally *closed*.

`EN` on A3 instead of A4 is still wrong and still worth fixing — it just is
not what caused the one-way symptom, since the firmware never reads `EN` back.
Corrected analysis in
[`docs/opentrons-pipette-wiring.md`](docs/opentrons-pipette-wiring.md); run
write-up in
[`results/pipette_test_20260901e/README.md`](results/pipette_test_20260901e/README.md).

`tools/pipette_bench_check.py` now reports the limit-switch verdict instead of
the DIR-fault one (and no longer crashes with a `NameError` on that path).

## 2026-09-08 — no hardware access; the wiring question answered from source

Ben corrected the 2026-09-01 write-up: **pin 6 → GND is on the Cubware diagram
and is wired**, so the "the diagram forgets it" framing above is wrong. What the
diagram genuinely does not state — and neither does any other Ursa source — is
*which physical hole is pin 1*. That is settled by science-jubilee's
[`OT2_Wiring_Diagram.pdf`](https://github.com/machineagency/science-jubilee/blob/main/tool_library/OT2_pipette/assembly_docs/OT2_Wiring_Diagram.pdf),
a photograph of the pipette's own header: the top row (9, 10) is empty, the two
coils occupy the bottom two rows as left-right pairs, and the limit switch is
pins 7 and 6 — *diagonal*, not a same-row pair.

Source inventory, since the question keeps coming up: Cubware's
`documentation/opentrons-pipette-setup.md` + `images/PipetteControl.png` is the
only Ursa-authored pipette wiring page (`ArduinoCircuitDiagram_v3.png` beside it
is the capper/lights circuit); it delegates to `BU-KABlab/PANDA_Arduino`, which
vendors the science-jubilee tool doc at `src/pipette_tool.md`.

**New finding — correcting the UART pin opened a way for the driver to be left
switched off.** `TMC2209::initialize()` runs `setOperationModeToSerial()`
(`i_scale_analog = 0`, which takes the VREF pot out of circuit), then
`minimizeMotorCurrent()` and `disable()` (`CHOPCONF.toff = 0`), and relies on the
firmware's subsequent `setRunCurrent`/`enable()` writes to undo that. The link is
write-only — `SoftwareSerial` RX is A0, documented in `Pipette.h` as "not
connected" — and nothing calls `isSetupAndCommunicating()`. With UART on A0 the
chip stayed in standalone mode and was enabled by default; with UART on A1 it is
put into serial mode and disabled first. **Bisect: pull the UART wire off A1 and
retry.** Also, `RUN_CURRENT_PERCENT 50` is ~0.9 A RMS against a motor rated
350–500 mA peak, and that only became live when the UART wire started working.

Full derivation in [`docs/opentrons-pipette-wiring.md`](docs/opentrons-pipette-wiring.md)
§3 and §4.

**No hardware access this session.** Nothing is on the Pi's USB bus: the GRBL
CH340 last disconnected 2026-09-03 19:20 UTC and the capper/pipette Arduino
2026-09-01 18:31 UTC. No measurements were possible; nothing was run.

## 2026-09-08 (later) — CubXL replugged; campaign 83, 12/12, and the fault narrowed to the pipette connector

The CubXL came back on the Pi's USB bus. Ports enumerated on the **same names**
as before the unplug, so no config edit was needed: `/dev/ttyUSB0` (CH340 →
GRBL) and `/dev/ttyACM0` (Arduino Uno → capper + pipette). Their `by-id` paths
are in `results/pipette_test_20260908/README.md` and are the safer thing to
reference if a third serial device is ever added.

Ran the trio exactly as committed at `a0ccbb7`: `validate_setup` PASS, `--mock`
12/12, `passive_shadow` 0 nominal and 0 tip-stuck, then **12/12 on hardware in
4m 3s** (campaign 83, `21:22:52 → 21:26:55` UTC, status `completed`). Controller
read live beforehand: `$130/$131/$132` = 409.000 / 309.000 / 124.000 and
`$20=1`, matching the gantry file. Plunger trace byte-for-byte the shape of
campaign 77 — the two forward moves (prime, aspirate) emitted steps, the four
upward ones were refused.

**New tool: [`tools/pipette_driver_probe.py`](tools/pipette_driver_probe.py).**
It drives the firmware's `CMD_MOVE_RELATIVE` (code 16) in raw steps, which
reports an aborted move *explicitly* rather than leaving it to be inferred from a
round-trip time, and whose DOWN direction is not gated by the limit switch at
all. Two readings:

- limit switch **ASSERTED — the loop is open** (`ERR:{"error":"Failed to move relative"}`)
- motor: **1592 steps down in 4.04 s against 4.00 s commanded**, at a deliberately
  slow 400 steps/s. Everything upstream of the STEP pin works.

So the fault is between the Arduino header and the motor windings, and one
hypothesis covers both symptoms: the switch loop and both coils all arrive on the
same FC-10P connector at the pipette, so a seat/crimp fault opens them together.
Total silence (no buzz) means no coil current — a swapped coil *pair* buzzes
instead. The switch reading has also flipped between rewiring passes, which is
intermittent-contact behaviour, not a wrong pinout.

Two hypotheses were **ruled out** by reading the pinned `janelia-arduino/TMC2209`
v10.1.1 rather than assuming: the `SoftwareSerial` overload defaults to 9600 baud
(not 115200), and `toff_` initialises to `TOFF_DEFAULT = 3` so `enable()` writes
a live chopper config. The UART-disable path is still real but now needs
*partially* landing writes, which is a narrower failure than a misrouted pin.

Three firmware readings closed open questions: `aspirate()` moves down to
`PRIME_POSITION 36.0` **first** and only then up to the volume target, so the
36.00-vs-35.45 discrepancy is just that second (upward) leg being refused when
the switch is asserted; `0.673 s/mm` is `MOVEMENT_VELOCITY 2500` steps/s against
`STEPS_PER_MM 1592` plus loop overhead, arithmetic rather than a fit; and while
the switch reads asserted **the plunger is a one-way ratchet** — every upward
command is refused, `HOME` only zeroes the counter, and no other retract path
exists, so each run drives it further out.

On the supply: 12 V / 2 A into the driver's VM terminal is right, and the 2 A is
a ceiling, not a setting — a stepper driver is a current source, so what needs to
come down to the motor's 350–500 mA is `RUN_CURRENT_PERCENT`, not the supply.

Full write-up in [`results/pipette_test_20260908/README.md`](results/pipette_test_20260908/README.md);
wiring analysis updated in [`docs/opentrons-pipette-wiring.md`](docs/opentrons-pipette-wiring.md) §4, §5 and §6.

**Not flashed:** the §4 bisect was not run as a firmware change. The Pi has no
AVR toolchain (`avrdude`, `arduino-cli`, `pio` all absent), so it would mean an
apt install on a production device plus reflashing the Arduino that also drives
the capper. The meter check in `docs/opentrons-pipette-wiring.md` §6 settles the
same question faster and without touching the board.

## 2026-09-09 — the science-jubilee prior art, read against this build

No hardware run and no Pi connection this session. `machineagency/science-jubilee`
is the upstream of this pipette harness (PANDA vendors its tool doc; Ursa delegates
to PANDA), and it drives the same OT-2 pipette from a Duet instead of an
Arduino + TMC2209 — so it is an independent implementation to cross-check against.
Full analysis in [`docs/opentrons-pipette-wiring.md`](docs/opentrons-pipette-wiring.md) §8.

The load-bearing results:

- **PANDA's millimetres are real millimetres.** `STEPS_PER_MM 1592` at 16x is
  99.5 full steps/mm — a 2.01 mm leadscrew lead. science-jubilee's `M92 V200`
  works out to 16 mm/rev, so their V units are ~7.96 mm each, not millimetres.
  Constants cannot be ported between the two without that factor.
- **The P300 volume calibration is corroborated.** 0.91 units/µL × 200 steps/unit
  = 182 steps/µL upstream, against 0.1098 mm/µL × 1592 steps/mm = 174.8 here.
  Two controllers, 4% apart. `UL_TO_MM 0.1098` is real.
- **Upstream's `P20_config.json` is not.** Its `mm_to_ul` puts full-scale volume at
  6.8% of the plunger travel, where P1000 is at 100% and P300 at 88%. It reads as a
  copied P300 line. A self-consistent p20 starting estimate is ~1.8 mm/µL in PANDA
  units — against CubOS's placeholder `0.025`, which is ~72x too small.
- **The run current is ~2.5x the motor's rating.** `M906` upstream is 350 mA peak
  (Gen1) / 500 mA (Gen2); `RUN_CURRENT_PERCENT 50` here is ~1.25 A peak. Want ~11
  and ~17 respectively. Gen1 and Gen2 also differ 4.17x in steps per unit, and this
  firmware hardcodes one value.
- **A Duet reports driver faults; this port cannot.** `open_load_a/b`,
  `short_to_ground_*` and `over_temperature_shutdown` are all on the TMC2209 and
  exposed by the janelia library, but PANDA wires the UART one-way (`RX_PIN 14`,
  "not connected but required"). A 1 kΩ resistor between **A0 and A1** — the
  library's own documented single-wire hookup — makes them readable, and
  `open_load_a/b` answers the coil question without a meter.
- **The header photo resolves the pin numbering**, and it is now redrawn as a table
  plus a viewing-independent check (the two fully-populated rows are the two nearest
  the pipette tip). Working the 180° flip through in full gives a sharper result than
  before: it would leave D9 floating through a dead-ended coil and reading asserted
  *permanently*, which the 2026-09-01 sessions rule out. The machine-end
  ribbon-to-hookup junction remains the better suspect.
- **Upstream senses tip pickup**, with a second limit switch on the tool and RRF's
  `H4` stop-on-endstop move. That is the answer to this branch's long-standing
  unsensed `pick_up_tip`; printable switch holders ship in the same tool library.

## 2026-09-12 — the CubXL moved to a new Pi; cameras arrive, SSH does not

See [`results/pipette_test_20260912/`](results/pipette_test_20260912/README.md).

The CubXL was moved onto a new Raspberry Pi 5 with two cameras attached, and the
2026-09-08 trio was to be run through it. It was not run: the new Pi is online on
the tailnet but carries **`tag:pi-5-des4`** and no `tag:tailscale-ssh`, so
Tailscale SSH from a CI runner tagged `tag:stream-cam-test` is refused. Five
login names were refused identically, which rules out a `users`-field mismatch —
the policy has no `dst` covering that tag. The OAuth client cannot read or write
the policy (403 on both `/acl` and `/devices`), so this is an admin change.

The CubXL genuinely left the old Pi: no `/dev/ttyUSB*` or `/dev/ttyACM*` there
any more, and `lsusb` shows only an Ethernet adapter. There is no fallback host.

Everything offline was done instead. Against CubOS `cbc33dc` + all four patches,
the trio gives `validate_setup` PASS (12 steps), `--mock` 12/12, and
`passive_shadow` **0 interferences both nominal and tip-stuck**. The only change
in the trio is both park positions moving to the near-Y end of the deck; the
capper park is now off the vial column in X (236 vs the column's 192–220), which
holds the passive nozzle ≥ 38 mm clear of every cap and is what keeps the
tip-stuck column at zero.

New: [`tools/run_with_camera_capture.py`](tools/run_with_camera_capture.py) —
wraps `run_protocol` and grabs frames at **step boundaries**, where the gantry is
stationary and its pose is known, naming each file for the step it followed. Two
properties were tested rather than asserted: with both cameras stubbed to fail
the protocol still completed 12/12 and returned 0 (a camera cannot abort a run),
and the default capture points for this protocol come out as steps 2, 4, 7, 9 —
`decap vial_1`, `aspirate`, `decap vial_2`, `drop_tip`, which are precisely the
four questions that have needed eyes on this branch. CSI cameras are found via
`rpicam-still --list-cameras`, USB UVC via `ffmpeg` on capture-capable
`/dev/videoN` nodes.

## 2026-09-14 — CubOS installed on the new CubXL Pi; ready to run, not run

Full record and evidence:
[`results/pi5_des4_provision_20260914/`](results/pi5_des4_provision_20260914/).

SSH to `rpi-5-des4` works now (the tag fix in [`0d8173e`](https://github.com/vertical-cloud-lab/byu-vcl/commit/0d8173e)),
so the install that 2026-09-12 was blocked on is done. **The trio was deliberately not
run** — @jarrettshupe asked for the Pi to be made ready for someone else to run it.

`~/CubOS` is CubOS **`cbc33dc`** in a Python 3.13.5 venv with **all four** patches from
[`patches/`](patches/) applied cleanly (9 files, 173 insertions), and `~/byu-vcl` is this
branch. The only package that had to be installed on the Pi was **`git`** — `venv` already
bundles pip, and `patch`, `gcc`, `v4l2-ctl` and `rpicam-still` were present. `ffmpeg` is
absent and not needed, since both cameras are CSI. `apt upgrade` was deliberately not run.

Five gates, all against the committed trio, all on the Pi:

| gate | result |
| --- | --- |
| `validate_setup` | **PASS** |
| `run_protocol --mock` | **12/12** |
| `passive_shadow` | **0 interferences** |
| `passive_shadow --tip-stuck` | **0 interferences** |
| upstream test suite | **2020 passed, 3 failed, 17 skipped** |

The 3 failures are the upstream tests for the three patches that intentionally change
behaviour. That was proved, not assumed: the same three tests were run in a pristine
`cbc33dc` worktree with `PYTHONPATH` pointed at its own `src`, and all three pass there.

Hardware read read-only, nothing commanded. `$130/$131/$132` = 409.000 / 309.000 / 124.000
and `$20=1` match the gantry file exactly, so the next run will **not** abort at connect
with "Critical GRBL settings mismatch". The Arduino's boot banner lands at **3.76 s** —
the same figure as the old Pi, and well past the stock 2.0 s settle time, so
`pawduino-connect-boot-banner` is required here too. The capper sensor reads clear and the
electromagnet was explicitly de-energized afterwards.

Two findings for whoever runs it:

- 🔴 **The cameras need re-aiming.** Both capture fine, but `cam1_csi1` is mounted rotated
  90° and its frame is dominated by the machine's side panel and the room; neither test
  frame clearly shows the vial holder or the tip rack. As aimed today the eight run frames
  would not answer the questions the harness exists for.
- ✅ **The pipette is a `P20 GEN2`** — legible on the body in `cam0`'s test frame, closing
  the question left open on 2026-09-09. Gen2 means 500 mA peak and `M92 V200`, so PANDA's
  `RUN_CURRENT_PERCENT` should be ~17; it is currently **50**, about 2.5× the motor's
  rating.

Also worth knowing: campaign numbering restarts at 1 on this Pi (the old one ended at 83),
and mock runs consume numbers. No systemd unit, cron entry or API server was created —
nothing starts on boot, and `sshd` is still the only thing listening on a tailnet-facing
address, matching the `tcp:22`-only grant for `tag:rpi-5-des4`.

## 2026-09-15 — CubOS `main` update audited; migration prepared, deliberately not taken

Prompted by [Alex Chen's note on #200](https://github.com/vertical-cloud-lab/byu-vcl/issues/200#issuecomment-5666131265):
CubOS `main` now moves the CubXL faster, and the Operator UI carries an **Update** button.
Full write-up and evidence in
[`cubos/results/cubos_update_audit_20260915/`](results/cubos_update_audit_20260915/README.md).
Nothing on the Pi was changed and nothing was run on the CubXL.

`main` is **226 commits** ahead of the Pi's `cbc33dc`, and three of those commits matter
here.

**The speed change is real and silent for us.** `7ff4d7f` adds
`cnc.default_feed_rate_mm_min` and raises the module default 2000 → 3000 mm/min; every
`G01` previously hardcoded `F2000` regardless of `$110/$111/$112`. Upstream pinned all of
*its* configs to an explicit 3000. `cub_xl_ben_pipette_capper.yaml` is ours and carries no
such field, so it would inherit 3000 without anyone choosing it. Worth pinning to 2000 and
taking the speed as its own watched run — but the pin has to land **with** the update, not
before: `CncYaml` at `cbc33dc` is `extra="forbid"`, so adding the field today breaks
loading on the Pi as it stands.

**The capper park leg is gone, and that helps the cap-clearance problem.** `b39988b` makes
every XY move without an explicit `travel_z` lift to the multi-tool ceiling first, and drops
`decap`/`cap`'s trailing park entirely (`park_position` now loads with a warning and is
ignored). Concretely: a gripped cap used to be carried on the park leg at carriage Z 99.065
and is now carried on the next command's ceiling travel at Z 124 — about 9 mm more clearance
over neighbouring caps, which is the symptom Ben filmed on 2026-08-31.

**Two of our four patches are fixed upstream, better than ours** — `3a7f4ab` for the
cap-sensor confirm (it re-engages per retry, ours did not) and `88bf226`'s `PawduinoLink`
for the boot banner (a `CMD_HELLO` resync rather than a longer sleep; also fixes the
unarbitrated shared `/dev/ttyACM0`). The other two are re-ported as
`cubos/patches/*-main.patch`.

🔴 **As-is, `main` fails Ben's committed trio with 6 violations.** Upstream took the
ceiling-travel half of our hover patch but not the clamp, so a 35 mm tip still demands
carriage Z 150 against `z_max` 124. With both ports applied: `validate_setup` PASS,
`--mock` 12/12, `passive_shadow` 0 both ways, and `pytest` **2544 passed / 0 failed** —
identical to pristine `main`. Diffing commanded poses between the two revisions on the same
trio shows six removed poses (the four capper park legs plus two redundant retracts),
nothing added and nothing moved.

🔴 **The Update button cannot work on this Pi.** `deploy/pi/update.sh` runs
`git checkout --detach`, which any applied patch makes git refuse (it aborts cleanly, before
the rollback path arms). Independently, this Pi has no `cubos_api`, no API server, no
`cubos` systemd service and no `npm`, so the button does not exist on it yet. A gitops
updater and a locally patched appliance are mutually exclusive — the durable fix is
upstreaming the clamp so we carry no patches.

**Recommendation: hold.** The plunger fault Ben and Jarrett are chasing is entirely below
CubOS, so the update buys nothing for it and adds a variable; Ben's outstanding 2026-09-12
ask (run the trio, capture 8 frames) was validated against `cbc33dc` and should happen on
the known-good tree first. The migration recipe is written down and reversible whenever
they want it.

## 2026-09-15 (later) — migration executed: the Pi now runs upstream `main` + two patches

Ben asked for it, so the migration prepared in the audit above was executed on
`rpi-5-des4`. Full record, evidence and rollback recipe in
[`results/cubos_migration_20260915/`](results/cubos_migration_20260915/README.md).
**No protocol was run and no motion was commanded** — both ports were opened
read-only and the electromagnet was de-energized afterwards.

| | before | after |
|---|---|---|
| `~/CubOS` HEAD | `cbc33dc` | **`496819c`** (detached; `== origin/main`) |
| patches applied | 4 | **2** — `tipped-hover-clamp-main`, `pipette-connect-tolerate-failed-home-main` |
| local diff | 9 files, 173 insertions | 8 files, 125 insertions |
| `validate_setup` / `--mock` | PASS / 12·12 | **PASS / 12·12** |
| `passive_shadow` nominal / tip-stuck | 0 / 0, 28 poses | **0 / 0, 22 poses** |
| `pytest` | 2020 passed, **3 failed** | **2544 passed, 0 failed** |

`origin/main` was still exactly the audited `496819c`, so the verified recipe
applied verbatim and both ports went on clean.

**The one thing that needed hardware, not reasoning:** dropping
`pawduino-connect-boot-banner` hands the Arduino handshake to upstream's
`PawduinoLink` (`CMD_HELLO` round-trip with `expect="Hello"`, which skips stale
lines). Our patch existed because this board's boot banner lands at 3.76 s, past
the 2 s settle. Tested against the board: `connect()` returned **OK in 3.77 s**,
then the capper sensor, plunger status and electromagnet-off all answered
normally. A resync, not a longer sleep — and it works here.

**The commanded geometry is byte-identical to the audit**: 22 poses, down from
28. The six removed are the capper's park legs, which upstream `b39988b`
deleted; a gripped cap is now carried on the next command's ceiling travel at
carriage Z 124 instead of the park leg's 99.065 — about **9 mm more clearance**
over the caps it traverses, which is the symptom in Ben's 2026-08-31 video.

Two config decisions came with it, both in
[`configs/gantry/cub_xl_ben_pipette_capper.yaml`](configs/gantry/cub_xl_ben_pipette_capper.yaml):

- **`cnc.default_feed_rate_mm_min: 2000.0` added.** Upstream raised the module
  default 2000 → 3000, and our file carried no such field, so the migration would
  silently have made every move 1.5× faster. Pinned so the next run differs from
  campaign 83 in exactly one intended way. One line to `3000.0` takes the speed.
- **The capper's `park_position` kept, not deleted.** Upstream ignores it with a
  warning and says to delete it; `PawduinoCapper.__init__` at `cbc33dc` takes it
  as a *required* argument, so deleting it breaks rollback and the fallback is the
  out-of-bounds `[-10, -10]` placeholder. Note this is **not** the protocol's own
  `positions: park_position:`, which is still used.

All ten settings in the connect-time critical GRBL set match the controller
(`409 / 309 / 124`, `$20=1`), so a run will connect. Unchanged by any of this:
the plunger still will not actuate — that fault is below CubOS, in the
Arduino → TMC2209 → motor chain.

## 2026-09-15 (later still) — campaign 26, the p20 firmware, and the TMC2209 finally answers

Ben fitted a 10 kΩ bridge between A0 and A1, asked for the trio to be run, for
the dead park position to go, and for the p20 constants to be set — then for the
machine to be left alone until he says otherwise.

**Run:** campaign 26, `21:51:38 → 21:56:41` UTC, **12/12**, `validate_setup`
PASS, `--mock` 12/12, `passive_shadow` 0 interferences nominal and tip-stuck.
Full write-up in
[`results/pipette_test_20260915/`](results/pipette_test_20260915/README.md).

**The headline.** The bridge is the right hardware change and was inert on its
own — the firmware only ever wrote TMC2209 registers and never read one back, so
campaign 26's plunger trace is byte-for-byte campaigns 77 and 83. Adding
`CMD_PIPETTE_DRIVER_STATUS = 29` in the same reflash as the p20 constants got an
answer, stable over five reads:

```
OK:{"msg":"Driver status","v":[0.00,0.00,-1.00]}       comm = 0
```

**The driver returns nothing.** So none of `setupMotor()`'s six register writes
has ever landed, and the chip has been on power-on defaults throughout. That
kills the §4 hypothesis in
[`docs/opentrons-pipette-wiring.md`](docs/opentrons-pipette-wiring.md) — with
serial mode never entered, the VREF pot is still in circuit rather than bypassed.
The discriminator is holding torque by hand: none ⇒ no coil current (VM, VREF,
coils, in that order); present ⇒ the UART path alone.

**Firmware.** The board's flash was backed up first and proved byte-for-byte
identical to a local build of upstream `228615b`, so the VCL image is a provably
minimal delta; a rebuild elsewhere reproduces it bit-for-bit. `MAX_VOLUME` 300→20,
`MIN_VOLUME` 5→1, `UL_TO_MM` 0.1098→1.8, `RUN_CURRENT_PERCENT` 50→17,
`HOLD_CURRENT_PERCENT` 30→10, plus the new command. `STATUS` now reports
`max_vol: 20.00`. Patch, hex, backup and restore recipe in
[`firmware/`](firmware/README.md).

Upstream `main` **does not compile** — a duplicate default argument on
`mixInPlace`. The patch carries the one-line fix.

**CubOS.** `p20-mm-to-ul-passthrough.patch`: `mm_to_ul` 0.025 → 1.0, so
`volume_ul` stops being converted to mm on both sides. 2544 tests pass.
`prime_position` / `blowout_position` / `drop_tip_position` are still
placeholders (5/7/10 against the firmware's 36/44/55) and were deliberately left
alone — they change real motion and were not asked for.

**Config.** The capper's `park_position` is deleted; upstream `b39988b` ignores
it and the clearance it used to give moved upward, not away. Rolling CubOS back
to `cbc33dc` now needs it put back first.

**Cameras.** 7 of 12 frames. `cam0_csi0` got all six; `cam1_csi1` timed out on
five, most likely buffer contention on a 1 GB Pi 5 running two 4608×2592 sensors
alongside CubOS. No camera failure touched the protocol — that rule held.
`run_with_camera_capture.py` gained `--vflip`/`--hflip`.

## 2026-09-16 — campaign 36: 11 of 12 steps, then the closing `home` failed

Requested: run the trio again with `RUN_CURRENT_PERCENT` at 17. Full write-up in
[`results/pipette_test_20260916/`](results/pipette_test_20260916/README.md).

**The current change is inert.** The 17 is in the flashed image (`STATUS` returns
`max_vol: 20.00`, so the VCL p20 build is unambiguously live), but
`setRunCurrent()` is a UART register write and the driver still answers `comm = 0`
— no reply at all. The chip is on power-on defaults with the VREF pot in charge,
exactly as it was at 50, so this run is electrically identical to campaign 26.
Note `flags = 0` in that reply is **not** "no faults": `getDriverDiagnostics()`
only reads the status register when `comm > 0`, so the `open_load_a/b` coil bits
carry no information yet.

🔴 **The closing `home` (step 11) failed and the machine was left in `Alarm`.**
GRBL reports `Pn:X` — the X limit switch asserted — persistently, where the same
read before the run carried no `Pn:` field at all. Homing alarmed on all five
attempts. Reading it against `$23=0` (home to max) and stock GRBL's cycle order:
Z homed and pulled off 3 mm, X reached its switch and is still holding it, and
**Y never reached its own** — GRBL aborts once an axis exceeds `1.5 × $131` =
463 mm, ~28 s at `$25`, which fits the observed ~41 s attempts.

This is the first homing failure ever recorded on this Pi; the opening `home` of
the *same run* succeeded 2.5 minutes earlier. The protocol only visits deck
x 154–284, y 13–60 — `home` is the only command that drives to the far corner
(409, 309), which is why 11 steps of normal motion can pass and the closing home
still fail. Two candidate obstructions are in the camera frames and want ruling
out first: the p20 is **on the bench, tethered into the moving head by its
FC-10P ribbon** (its body reads `P20 GEN2` in `step10_cap__cam0_csi0.jpg`), and a
hand was in the work area. `Alarm` is the safe state, so it was left there rather
than driving Y into whatever stopped it a sixth time.

Everything else was left clean: both caps returned by the protocol's own `cap`
steps, electromagnet off, cap sensor clear, both ports free.

**The volume chain now carries real microlitres.** `mm_to_ul: 1.0` + `UL_TO_MM
1.8` + `MIN_VOLUME 1.0` mean CubOS sends `ASPIRATE 20.0` and the firmware echoes
`v:[20.00, 36.00]` — where every earlier trace sent `0.5`, had it clamped up to
the P300's `MIN_VOLUME 5.0`, and landed at 35.45. The 36.00 is `PRIME_POSITION`
and is the plunger limit switch, not a conversion error: `aspirate()` drives down
to 36.0 first, then *up* to 0.0, and upward strokes are still refused.

**Cameras: 10 of 10 frames, all under 0.7 s** — against 7 of 12 with five 20 s
timeouts last time. `cam1_csi1` frames are committed **cropped**: that camera
looks across the bench into the room and a lab member is in frame in every shot.

One incidental find: `_best_effort_retract_to_safe_z()` still raises
`KeyError: "Unknown instrument 'PawduinoCapper'"` at `496819c` — it passes an
instrument object where a name is expected, so the outer safety retract is dead
code upstream. It did not matter here (the failing step was `home`), but it is
worth filing.

## 2026-09-17 — P20 GEN2 alignment landed; the trio blocked by the Arduino's serial link

Ben asked for three things: run the trio again (the homing obstruction was
fixed), address [Ursa's review][ursa200], and make the values match in all
locations for the **P20 GEN2**. He also reported the bench result that settles
the driver question — *pulling the plunger by hand, with the driver plugged in
and on, it moves freely*, i.e. no holding torque, i.e. no coil current.

[ursa200]: https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5719634392

🔴 **The trio did not run and the firmware was not flashed.** Both are blocked
by the same fault: `/dev/ttyACM0` corrupts serial data in both directions.
`PawduinoLink.connect()` — the exact gate `run_protocol` hits, before the
gantry port is opened — fails. 0 of 25 `STATUS` round-trips parse; `avrdude`
will not sync at any baud or with either programmer; and replies arrive valid
but truncated (`OK:{"homed":0,"pos":0.00,"max_vol":2`). The board re-enumerated
five minutes before this session made contact, so the fault predates it, and
the USB serial number is unchanged — same board. Full evidence, and the bench
checks (power-cycle first, then the 5 V rail, then anything on `D0`/`D1` or
near `RESET`) in
[`results/pipette_p20gen2_20260917/`](results/pipette_p20gen2_20260917/README.md).

✅ **P20 GEN2 values now agree in all three places** — the firmware, CubOS's
`p20_single_gen2`, and the docs — taken from Opentrons
`shared-data/.../pipetteModelSpecs.json` rather than derived:

| | Opentrons | P20 GEN2 | firmware was | CubOS was |
|---|---|---|---|---|
| prime | `bottom` −8.5 | **28.0** | 36.0 | 5.0 *(placeholder)* |
| blowout | `blowout` −13 | **32.5** | 44.0 | 7.0 *(placeholder)* |
| drop tip | `dropTip` −27 | **46.5** | 55.0 | 10.0 *(placeholder)* |
| mm per µL | `ulPerMm` → 0.746 µL/mm | **1.34** | 1.8 | — |

The CubOS placeholders were worse than a mis-scaling: they are sent as
**absolute `MOVE_TO` targets**, so `5/7/10` aimed 23–36 mm short of the planes
a P20 GEN2 plunger uses. All three planes moved *down*, so every commanded
travel is now shorter — the safe direction. Run current went 17 → **20**
(CS 6, 1.02 A peak = Opentrons `plungerCurrent`) and hold 10 → **5** (0.29 A
peak = `idleCurrent`), recomputed on the **0.05 Ω** sense resistor Ursa read
off the Adafruit schematic; this repo had assumed 0.11 Ω.

🔴 **Two conclusions in `docs/opentrons-pipette-wiring.md` were retracted**,
in place, in a new §10:

- **`comm = 0` was never evidence.** A read over `SoftwareSerial` on an AVR
  cannot succeed with the janelia library whatever the wiring — `write()` runs
  `cli()` so no echo is received, and `sendDatagramBidirectional()` then
  discards the first four bytes of the driver's real reply as if they were
  that echo. So "none of `setupMotor()`'s writes ever landed" is unproven, and
  the §4 hypothesis is no longer excluded. A diagnostic whose success path is
  unreachable is not a diagnostic.
- **The sense resistor is 0.05 Ω**, so the stock `RUN_CURRENT_PERCENT 50` was
  2.32 A peak — over the *breakout's* 2 A rating, not merely the motor's.

`patches/tmc2209-softwareserial-read.patch` fixes the read path, vendored into
`lib/TMC2209/` so a `pio pkg` refresh cannot drop it — proven with a sentinel
`#error`, not assumed. ⚠️ It is **not sufficient alone**: the bridge resistor
has to move to the TX side (`A1 -> 1k -> node`, `A0` and `PDN_UART` on the
node), or the push-pull TX shorts out the driver's reply.

**`VM` is still the first thing to measure.** The VREF pot is fed from the
chip's `5VOUT`, which is generated from `VM` alone — so a missing `VM` gives
zero coil current, no UART reply, and every `STEP`/`DIR` still acked. One
cause, every symptom, including Ben's hand test.

Gates, all against the installed tree: `pytest` **2544 passed / 0 failed**,
`validate_setup` **PASS**, `--mock` **12/12**, `passive_shadow` **0
interferences** nominal and `--tip-stuck`. Firmware builds clean; both patches
verified with `git apply --check` against fresh clones.

One P20 GEN2 number was deliberately **not** propagated: Opentrons implies a
**22.9 mm** tip extension (`tipLength 31.15` − `tipOverlap 8.25`) against the
**35.0 mm** Ben measured and that every piece of validated tipped Z geometry on
this branch depends on. A caliper check is worth doing, but it is not a
one-line change.
