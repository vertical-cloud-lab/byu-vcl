# stir_module_trial_20261105 (prepared, not run)

The first protocol with the stir module on the deck, asked for by @benwhitney5463 on PR #269
on 2026-11-05: uncap vial 2, pick up a tip, aspirate from vial 2, recap vial 2, uncap
vial 1, dispense into vial 1, recap vial 1, then stir vial 1. **The tip must never pass over
vial 1 while it is capped**: on the stir module vial 1 is too tall for a tipped pipette to
clear its cap.

- Protocol: [`stir_module_trial.yaml`](../../configs/protocol/vcl/stir_module_trial.yaml)
- Deck: [`stir_module_trial.yaml`](../../configs/deck/stir_module_trial.yaml), Ben's, verbatim
- Gantry: [`cub_xl_ben_3_instrument.yaml`](../../configs/gantry/cub_xl_ben_3_instrument.yaml)
- Check: [`capped_vial_keepout.py`](../../tools/capped_vial_keepout.py)

![tip path](tip_path_plan.png)

## Offline checks (runner, CubOS `496819c` + the CubXL's four patches)

| check | result |
|---|---|
| `validate_setup` | PASS ([log](checks/gate_validate.log)) |
| `run_protocol --mock` | 11/11 steps ([log](checks/gate_mock.log)) |
| `passive_shadow`, nominal and `--tip-stuck` | no interference ([nominal](checks/gate_shadow.log), [tip-stuck](checks/gate_shadow_tipstuck.log)) |
| `capped_vial_keepout.py` | closest the tip's axis comes to vial 1's axis while vial 1 is capped and a tip is or may be on: **45.3 mm** (step 4). Keep-out 24 mm: PASS ([output](checks/keepout.txt)) |
| `tip_clearance.py --tip-stuck` | every sideways move with the tip on at gantry Z 122 (tool Z 87) ([output](checks/tip_clearance_tipstuck.txt)) |

The deck file models only the two vials and the tip rack, so the spots where the tip goes
down beside the capper were checked by eye against the deck camera
([frame](frames/224414Z_deckcam_before.jpg), 22:44 UTC):

| step | tip end over deck | lowest tip-end Z |
|---|---|---|
| 5 cap vial_2 | (191.668, 100) | 20, 36 mm below vial 2's rim |
| 6 decap vial_1, 8 cap vial_1 | (181, 56) | 30, 36 mm below vial 1's rim |

Status: waiting for Ben's go on the PR. Nothing has moved.
