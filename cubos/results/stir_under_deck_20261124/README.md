# stir_under_deck_20261124: the under-deck stir module runs once it turns, but doesn't start from rest on its own

Asked for by @benwhitney5463 on PR #348 (2026-11-24, 23:05 UTC): "run a stir test. I have the
under-the-deck stir module all set up". This is the first run of the
[under-deck module](../../../hardware/vial-stirrer-cubxl/under-deck/README.md): the two parts
printed on 11-20, with the compact stirrer's fan, magnet carrier, Hall sensor and board hung under
the deck, and vial 1 standing on the deck in the collar. All times are UTC (the lab is on MST,
UTC−7).

- **Direct to the Uno:** 11-05's [`stir_trial.py`](uno/stir_trial.py), copied unchanged
  (sha256 `9d16a6936063`). It sends `30,<rpm>,<s>` for each step, reads `31` every second until
  4 s after the step's timer ends, and saves a deck frame every 2 s. Each step starts from rest.
  The gantry does not move. Two sequences: [`ud`](uno/ud_console.txt) and
  [`rest600`](uno/rest600_console.txt), with the data in [`ud.jsonl`](uno/ud.jsonl) and
  [`rest600.jsonl`](uno/rest600.jsonl).
- **Through CubOS:** `cubxl_run.py` with [`stir_only_check.yaml`](../../configs/protocol/vcl/stir_only_check.yaml),
  with the same arguments as [11-19](../stir_only_check_20261119/README.md). It homes, then
  `stir` 600 rpm for 20 s (blocking), `stir` 600 rpm with a 60 s limit and `wait: false`, a 15 s
  `pause`, and `stir` rpm 0. The record is in [`run/`](run/) ([`SUMMARY.md`](run/SUMMARY.md),
  [`stir_trace.json`](run/stir_trace.json)). Deck frames were taken every 2 s alongside by
  [`deck_snaps.py`](deck_snaps.py), as on 11-19.
- **Code:** byu-vcl `87e97d5`, and CubOS `496819c` + the four earlier patches +
  [`stirrer-approach-1`](../../patches/stirrer-approach-1.patch). The Uno's stirrer firmware
  (`30`/`31`) answered as on 11-19.

## Before anything moved

- **The Pi:** up 20 days, `throttled=0x0`, no `HOLD`. The Uno and the GRBL board's CH340 were on
  their usual `by-id` paths, and nothing held either port.
- **No USB over-current since 11-19:** the kernel log has no USB line after 2026-11-19 23:50.
  Over-currents were logged on 11-18 and 11-19 before Ben rebuilt the wiring.
- **Deck frame at 23:07:00** ([`230700Z_deckcam_before.jpg`](frames/230700Z_deckcam_before.jpg)):
  the module's cable no longer crosses the deck. Vial 1 (pink liquid, black cap) stands in the
  white collar, about where the on-deck module stood on 11-19
  ([11-19 and today, side by side](frames/module_20261119_vs_20261124.jpg)). The head is
  parked at its homed corner. Camera 1, on the head, can't see vial 1 from there, so only the
  overhead deck camera was used.
- **Between 23:07:00 and the first frame of the test (23:09:40), someone put a second white
  holder,** with a red-capped vial in it, on the deck just −X of the collar, about 60 mm from
  vial 1. At 23:12:00 it was moved about two slot columns further −X, where it stayed
  ([its position over time](frames/second_holder_230700-232153Z.jpg)). It is in view in every
  frame below.

## The runs

The firmware reports `rpm` as 30 × the Hall falling edges in the last 2 s, so one edge in a window
reads as 30 rpm. It starts every run with a 0.5 s kick at full power, then runs at duty 0.30. When
a 2 s window has no edge, it pauses the fan 0.75 s and kicks it again. If the window after five
such kicks is still empty, about 12 s after the start, it stops the fan and sets `stalled`.

| # | `30` sent | how | rpm, s | near the module (deck camera) | Hall `rpm` | ended |
|---:|---|---|---|---|---|---|
| 1 | 23:09:42.60 | Uno | 600, 60 | nobody | **0 throughout** | stall, 12.2 s |
| 2 | 23:10:47.39 | Uno | 600, 15 | nobody | **0** | stall, 12.1 s |
| 3 | 23:11:06.61 | Uno | 600, 15 | nobody | **0** | stall, 12.1 s |
| 4 | 23:11:25.84 | Uno | 600, 15 | nobody | **0** | stall, 12.1 s |
| 5 | 23:11:45.07 | Uno | 600, 15 | nobody | **0** | stall, 12.2 s |
| 6 | 23:12:04.32 | Uno | 300, 20 | someone moves the second holder (23:12:00), then **lifts vial 1 out** (~23:12:11 to ~23:12:22) and puts a finger in the empty collar twice | one edge in the 2 s up to 23:12:16.5, else 0 | its timer |
| 7 | 23:12:28.61 | Uno | 900, 20 | vial 1 back in; fingers by vial 1, probably under the clear deck | first edges by 4.0 s; 180 → 870 rpm at duty 0.68 | its timer |
| 8 | 23:12:52.90 | Uno | 1200, 20 | the same | 330 rpm by 2.0 s; 990 at duty 0.82, then 1080 as it stopped | its timer |
| 9 | 23:18:56.04 | **CubOS** `stir` | 600, 20 | nobody at the start; fingers by vial 1 at 23:19:08, seen through the clear deck or reflected in it | 150 rpm by 2.0 s; **600–630 from 14 s, at duty 0.54–0.55** | its timer |
| 10 | 23:19:16.29 | **CubOS** `stir`, no wait | 600, 60 | nobody | 630 → 480 → 120 → **0** at 6 s; restarted on the next kick, 180 → 450 at duty 0.57 | `stir` rpm 0 at 15 s |
| 11 | 23:21:55.39 | Uno | 600, 20 | nobody | 240 rpm by 2.0 s (the kick turned it about 8 times), 30, then 0 | stall, 16.2 s |
| 12 | 23:22:19.70 | Uno | 600, 20 | nobody | **0** | stall, 12.2 s |
| 13 | 23:22:44.03 | Uno | 600, 20 | nobody | **0** | stall, 12.1 s |
| 14 | 23:23:08.34 | Uno | 600, 60 | nobody | **0** | stall, 12.2 s |

Deck frames: [every 4 s through 1–8](frames/ud_every4s_230940-231317Z.jpg);
[vial 1 lifted out and put back](frames/vial1_lifted_out_231158-231233Z.jpg);
[the hand by vial 1 in 7–8](frames/hand_by_vial1_231156-231317Z.jpg);
[the start of 9](frames/cubos_window1_start_231850-231904Z.jpg) and
[the hand at 23:19:08](frames/cubos_window1_231904-231910Z.jpg);
[every 4 s through 11–14](frames/rest600_every4s_232153-232409Z.jpg). For part of the time someone
stood at the front of the machine; their reflection is in the deck. No hand was in view during
1–5, 10 or 11–14.

**CubOS:** 5/5 steps, rc 0, 70.5 s. The stage 1 checks and all four gates passed, with no alarms
and no USB kernel lines. Teardown sent `30,0`. As on 11-19, the CubOS side worked as designed.

**Kernel:** no USB or over-current lines from 23:05 to 23:36, so none during any of the runs.

## What it says

1. **Hands-off, it doesn't start from rest: 1 partial start in 9.** Of the nine hands-off starts
   at 600 rpm (1–5, 11–14), eight never counted a single Hall edge, through six full-power kicks
   each. In 11 the first kick turned it about 8 times, but at duty 0.31–0.39 it stopped again
   within 4 s, and the next five kicks didn't move it. That is what the old module did on 11-19
   on the 4.6 mm spacer.
2. **Even with vial 1 out, it barely moved.** From about 23:12:11 to 23:12:22, the vial was out
   of the collar during three or four kicks, and the Uno counted one edge. On 11-04, with the
   compact holder and no vial, the same fan started on the first kick at both 300 and 1200 rpm
   ([`stirrer_spin_20261104`](../stirrer_spin_20261104/README.md)). So something besides the
   bar seems to be holding the drive. The vial was only out for about 11 s, with fingers in the
   collar, so this needs repeating: see the checks below.
3. **Once it turns, the drive and the Hall sensor work.** It reached 870 rpm at duty 0.68 and
   990–1080 at 0.82 (7–8), and held 600–630 at 0.54–0.55 through CubOS (9). The Hall count rose
   and fell with the speed, with no spurious counts. But it needs more duty for the same speed
   than the same fan with no vial on 11-04, which held 1260 rpm at 0.62–0.65 and 300 at
   0.28–0.31. The bar and the liquid account for some of that.
4. **It stops at duties the firmware treats as enough.** In 10 the duty fell to 0.26–0.34 and
   the fan stopped from 480 rpm. In 11 it stopped at 0.31–0.39. The firmware starts every run
   at 0.30 after the kick, and between stall kicks it runs at about 0.31: below what keeps this
   module turning.
5. **The starts that worked all came after the module had been handled**: 7–8 with a hand by
   the vial, probably under the deck, and 9 about six minutes after the vial was re-seated. By
   11–14, with nobody touching it, it was back to not starting.

## Checks on the module, in this order

1. **With vial 1 out, turn the drive by hand from below.** It should spin freely and coast to a
   stop. If it catches or stops dead, something rubs. It could be the magnet carrier on the
   frame's Ø20.6 bore or on the deck's underside (drawn with a 1.1 mm gap), or the fan's blades
   on its housing. The housing can twist if the two fan screws, on one diagonal, are tight and
   the two loose 0.5 mm washers aren't under the other two corners.
2. **Are any screws near the magnets steel?** The two clamp screws and the two fan screws are
   20–23 mm from the axis. [BOM item 12](../../../hardware/vial-stirrer-cubxl/BOM.md) asks for
   stainless or brass. Magnets near steel give a detent that the fan has to break from rest.
3. **Then a hands-off stir with vial 1 out** (about a minute). If it starts on the first kick
   and holds 300–600 rpm at about duty 0.3, as on 11-04, the drive is free and the bar's pull is
   what is left. If it doesn't, the cause is in the drive itself. This was offered on the PR from
   23:25 to 23:36, but vial 1 stayed in the collar, so it wasn't run.

**On the firmware side, two changes would make starts more robust.** Neither frees a drive that
full-power kicks can't turn, as in 1–5 and 12–14.

- **A higher start duty.** Start at about 0.45 instead of 0.30, or use a longer kick (1 s
  instead of 0.5 s).
- **Don't restart from 0.30 while it is still coasting.** In 10, CubOS started the second
  window 0.01 s after the first one's timer ended, with the fan still at 630 rpm. The firmware
  treats any start after a stop as from rest: duty 0.30 and setpoint 100. The P loop then cut
  the duty to 0.26 and the fan stopped. Starting from the measured speed, or skipping the reset
  while edges are still coming in, avoids that.

Neither is made here. Both would go in `cubos/firmware/panda-arduino-stirrer.patch`
(`STIR_DC_START`, `STIR_KICK_MS` and `setStirrer()`).

## The CubOS files are not updated for the under-deck module

The run used the same gantry and deck files as on 11-19. The deck file,
[`stir_module_trial_stirrer.yaml`](../../configs/deck/stir_module_trial_stirrer.yaml), still has
vial_1 at x 151, y 45, rim z 66, and the on-deck module's body as a `wall` at z −16 to 26. This
protocol only homes and stirs, so neither entry is used. But both are wrong for the under-deck
module: the vial's rim is now about 30 mm lower (deck Z ≈ 38 by the
[design](../../../hardware/vial-stirrer-cubxl/under-deck/README.md#heights)), and nothing stands
on the deck but the 17 mm collar. **Teach vial 1 again before any protocol moves to it.**

## Changed on the Pi

- `~/byu-vcl-stir5x` fast-forwarded from `2b93a20` to `87e97d5`.
- New in `~/cubxl_runs/`: `stir_under_deck_20261124/` (the copies of `stir_trial.py` and
  `deck_snaps.py`, the logs, a camera 1 still, and 259 deck frames in `frames_ud/`,
  `frames_cubos/` and `frames_rest600/`); `stir_only_check_20261124/` and its `.console`.
- `~/cubxl_runs/HOLD` was set at 23:09:02 and removed at 23:36:10.
- Nothing else. `~/CubOS` was not touched.

`*.log` files are committed as `*.log.txt`, because the repo ignores `*.log`.
