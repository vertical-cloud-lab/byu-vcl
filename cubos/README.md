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

## Capper/decapper test protocol (not yet run on hardware)

`configs/protocol/vcl/capper_decapper_test.yaml` walks vial_1 → vial_6 doing
decap → pipette insertion → cap on each, against
`configs/gantry/cub_xl_ben_pipette_capper.yaml` +
`configs/deck/sterling_deck.yaml` (both as attached to
[PR #171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171), the gantry
file with two documented safety edits). It passes `validate_setup` and a
`run_protocol --mock` dry run for vials 2–6; **vial_1 currently fails bounds
validation** because the pipette's `offset_y: 20.0` puts the required gantry Y
at −15.0. See the protocol file's header for the fix options. Do not run on
hardware until vial_1 is resolved and the capper's `park_position` is
confirmed against the physical cap-staging area.

## Notes

- The gantry enumerates as `/dev/ttyUSB0` on the Pi; the original config's
  `serial_port: COM6` is Windows-specific and was the only edit needed.
- The potentiostat instrument is configured `offline: true`, so the base
  `cubos` install suffices — no vendor SDK extra needed for motion-only runs.
- The Pi's OT-2 overhead camera stream (port 8000) kept running throughout;
  CubOS's API port 8742 remains free for the Operator UI later.
