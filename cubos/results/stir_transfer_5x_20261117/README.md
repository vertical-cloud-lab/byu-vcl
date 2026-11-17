# stir_transfer_5x_20261117: 45/45 on the CubXL, but the stirrer stalled every time

Asked for by @benwhitney5463 on PR #348 (2026-11-17): pick up a tip, uncap vial 2,
aspirate in vial 2, cap vial 2, uncap vial 1, blowout in vial 1, cap vial 1, five times,
stirring vial 1 while vial 2 is uncapped, aspirated from and recapped. It was the first
protocol to use CubOS's own `stir` command (approach 1 of #133).

- Protocol: [`stir_transfer_5x.yaml`](../../configs/protocol/vcl/stir_transfer_5x.yaml), 45 steps
- Gantry: [`cub_xl_ben_3_instrument_stirrer.yaml`](../../configs/gantry/cub_xl_ben_3_instrument_stirrer.yaml)
  (Ben's 10-02 file plus `stirrer_1`)
- Deck: [`stir_module_trial_stirrer.yaml`](../../configs/deck/stir_module_trial_stirrer.yaml)
  at `013f6a4`: Ben's 11-05 deck with **vial_1 at x 151** (it was 126), plus the stir
  module's body as a wall
- CubOS: `496819c` + the four earlier patches + [`stirrer-approach-1.patch`](../../patches/stirrer-approach-1.patch)
- Record: [`run/`](run/) ([`SUMMARY.md`](run/SUMMARY.md), [`stir_trace.json`](run/stir_trace.json),
  [`plunger_trace.json`](run/plunger_trace.json), frames after steps 2, 4, 5, 6, 8, 9, 10,
  42 and 43 in [`run/frames/`](run/frames/))

## Before it ran

- **Vial 1 had moved.** The deck camera ([`frames/`](frames/)) showed the stir module one plate
  slot further +X than on 11-05 ([11-05 frame](../stir_module_trial_20261105/frames/224414Z_deckcam_before.jpg)).
  Ben confirmed it at 22:41 UTC ("vial one moved one slot +X"), and the deck's slot columns
  are 25 mm apart, so `vial_1` went from x 126 to 151 and the wall moved with it.
- **Checks** (`--checks-only`, 22:39, [`checks/`](checks/), with the old x 126): ports, GRBL,
  the Uno answering `31`, and the four gates all passed. With x 151,
  `capped_vial_keepout.py` gives 42.1 mm as the closest the tip's axis comes to vial 1's
  while vial 1 is capped and a tip is on (keep-out 24 mm), and the run re-ran the four gates
  itself before moving (all PASS, [`run/`](run/)). With the capper on vial 1 the tip now waits
  over deck (206, 56), down to Z 30, where the deck file has nothing.
- **The stirrer had already failed** a stir-only CubOS run ten minutes earlier
  ([`stir_only_check_20261117`](../stir_only_check_20261117/)). That doesn't make the
  transfer unsafe, so the run went ahead to test the protocol, with the stirring expected to
  stall.

## The run (22:50:08 → 22:55:15 UTC, 307 s)

**45/45 steps, protocol complete.** 172 `G01` moves, no alarms, 0 USB kernel lines. Plunger
HOME check after the run: ended at 28.0 mm, HOME took 12.681 s, so **+0.00 mm**, no lost steps.
Tip from A1 and back into A1.

Each cycle took about 41 s (steps 3-10: stir on, decap vial 2, aspirate, cap vial 2, stir off,
decap vial 1, blowout, cap vial 1). Five `ASPIRATE 20`s, five blowouts to 32.5 mm.

**Stirring: commanded at the right moments, but the stirrer never turned.**

| stir | `stir` step | started (UTC) | stopped by | s | `31` reads | rpm max | stalled |
|---:|---:|---|---|---:|---:|---:|---|
| 1 | 3 | 22:51:00.012 | firmware (stall) | 12.1 | 12 | 0 | yes |
| 2 | 11 | 22:51:52.635 | firmware (stall) | 11.1 | 11 | 0 | yes |
| 3 | 19 | 22:52:34.356 | firmware (stall) | 11.1 | 11 | 0 | yes |
| 4 | 27 | 22:53:16.044 | firmware (stall) | 11.1 | 11 | 0 | yes |
| 5 | 35 | 22:53:57.716 | firmware (stall) | 11.1 | 11 | 0 | yes |

Each `stir` (600 rpm, 120 s limit, no wait) was sent just before vial 2 was decapped, and CubOS
read `31` once a second after it. With no Hall pulse at all, the firmware gave up after five
stall retries, about 11 s in, which was during the decap of vial 2 each time. The `stir` rpm 0
steps (7, 15, …) then stopped an already-stopped stirrer. The protocol carried on, as it
should: a non-blocking stir that stalls is logged, not fatal. So the CubOS side worked; the
module itself needs a look (leads to the Uno, the fan turning freely).

## Plunger: aspirates 2-5 started from the blowout plane

The firmware's `ASPIRATE` is one continuous move to an absolute target,
`PRIME_POSITION − µL × UL_TO_MM` = 28.0 − 20 × 1.34 = 1.2 mm, at about 11 mm/s
([firmware README](../../firmware/README.md)):

- **Aspirate 1** started at 0.0 mm, where `pick_up_tip` leaves the plunger. It travelled down
  28 mm and back up 26.8 mm (5.00 s), so with the tip in vial 2 it first pushed out the
  tip's air as bubbles. 11-05 did the same.
- **Aspirates 2-5** started at 32.5 mm, the blowout plane, where the previous `blowout` left
  it. They travelled 31.3 mm up (2.86 s), so by nominal plunger travel they drew about
  **23 µL, not 20**. CubOS's `aspirate` doesn't re-prime between a blowout and the next
  aspirate.

Neither is in the stirrer code. The fix belongs in CubOS's pipette: prime above the liquid
before an aspirate. Until then, a protocol that reuses a tip should expect it. Worth checking
the nozzle for liquid after this run.

`*.log` files are committed as `*.log.txt`, because the repo ignores `*.log`. The Pi's
hostname is redacted in `kernel_during_run.log.txt`.
