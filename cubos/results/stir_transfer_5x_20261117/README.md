# stir_transfer_5x_20261117: ready, not run yet

Asked for by @benwhitney5463 on PR #348 (2026-11-17): pick up a tip, uncap vial 2,
aspirate in vial 2, cap vial 2, uncap vial 1, blowout in vial 1, cap vial 1, five times,
stirring vial 1 while vial 2 is uncapped, aspirated from and recapped.

- Protocol: [`stir_transfer_5x.yaml`](../../configs/protocol/vcl/stir_transfer_5x.yaml), 45 steps
- Gantry: [`cub_xl_ben_3_instrument_stirrer.yaml`](../../configs/gantry/cub_xl_ben_3_instrument_stirrer.yaml)
  (Ben's 10-02 file plus `stirrer_1`)
- Deck: [`stir_module_trial_stirrer.yaml`](../../configs/deck/stir_module_trial_stirrer.yaml)
  (Ben's 11-05 deck plus the stir module's body as a wall)
- CubOS: `496819c` + the four earlier patches + [`stirrer-approach-1.patch`](../../patches/stirrer-approach-1.patch)

## Checks (all passed; nothing moved)

On the CubXL Pi, `cubxl_run.py --checks-only` at 22:39 UTC ([`checks/`](checks/)): ports
(the stirrer names exactly the capper's and pipette's `/dev/ttyACM0`), GRBL against the
gantry file, the Uno (`STATUS`, cap sensor 0, magnet off, and `31` answered), then the gates:

| gate | result |
|---|---|
| `validate_setup` | PASS |
| `run_protocol --mock` | 45/45 steps |
| `passive_shadow`, nominal and `--tip-stuck` | no interference |
| `capped_vial_keepout.py` (run separately on the Pi) | closest the tip's axis comes to vial 1's while vial 1 is capped and a tip is on: **45.3 mm** (the aspirates in vial 2); keep-out 24 mm: PASS |

The tip goes on before vial 2 is opened (11-05 opened it first), so each `decap vial_2`
puts the tip beside the capper at deck (191.668, 100), down to Z 20, as `cap vial_2` already
did on 11-05.

## Why it hasn't run

1. **The stir module didn't turn** in the stir-only CubOS run just before
   ([`stir_only_check_20261117`](../stir_only_check_20261117/)): 0 rpm, stalled, no Hall pulse
   at all.
2. **Vial 1 may have moved.** The deck camera ([`frames/`](frames/)) shows the tip rack and
   camera at the same pixels as on 11-05
   ([frame](../stir_module_trial_20261105/frames/224414Z_deckcam_before.jpg)), but the stir
   module about one plate slot (~25 mm) further +X. In the
   [zoom](frames/223537Z_deckcam_zoom_stir_module.jpg), vial 1's cap is now to the right of
   vial 2's. On 11-05 it was to the left, as the deck file's x 126 vs 136.668 says. If the
   module did move, the capper would come down well off vial 1's axis.

Once both are sorted (and the deck file updated if vial 1 moved), the run is one command on
the Pi, from `~/byu-vcl-stir5x` (a sparse checkout of this branch) with `HOLD` taken:

```bash
cd ~/byu-vcl-stir5x && git pull
~/CubOS/.venv/bin/python cubos/tools/cubxl_run.py --name stir_transfer_5x_20261117 \
  --gantry cubos/configs/gantry/cub_xl_ben_3_instrument_stirrer.yaml \
  --deck cubos/configs/deck/stir_module_trial_stirrer.yaml \
  --protocol cubos/configs/protocol/vcl/stir_transfer_5x.yaml \
  --no-tic --home-check --frames-at 2,4,5,6,8,9,10,42,43
```
