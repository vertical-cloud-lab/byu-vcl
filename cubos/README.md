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
