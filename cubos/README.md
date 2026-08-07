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

## Notes

- The gantry enumerates as `/dev/ttyUSB0` on the Pi; the original config's
  `serial_port: COM6` is Windows-specific and was the only edit needed.
- The potentiostat instrument is configured `offline: true`, so the base
  `cubos` install suffices — no vendor SDK extra needed for motion-only runs.
- The Pi's OT-2 overhead camera stream (port 8000) kept running throughout;
  CubOS's API port 8742 remains free for the Operator UI later.
