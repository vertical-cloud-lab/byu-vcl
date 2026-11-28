# stir_transfer_5x_20261118: 45/45 again after the fan-ground fix, and still 0 rpm

Asked for by @benwhitney5463 on PR #348 (2026-11-18, 23:23 UTC): "the ground on the fan was
disconnected, so I soldered it together. Try that protocol again." It is the
[11-17 run](../stir_transfer_5x_20261117/README.md) repeated after that repair: same protocol,
gantry, deck and CubOS. Only the wiring changed.

- Protocol: [`stir_transfer_5x.yaml`](../../configs/protocol/vcl/stir_transfer_5x.yaml), 45 steps
- Gantry: [`cub_xl_ben_3_instrument_stirrer.yaml`](../../configs/gantry/cub_xl_ben_3_instrument_stirrer.yaml)
- Deck: [`stir_module_trial_stirrer.yaml`](../../configs/deck/stir_module_trial_stirrer.yaml), vial_1 at x 151
- The three files hash the same as on 11-17 (`13b6f8f746e3`, `ebb87d59fd94`, `550b2503e8da`)
- Code: byu-vcl `6cdc7eb`. CubOS `496819c` + the four earlier patches + [`stirrer-approach-1.patch`](../../patches/stirrer-approach-1.patch)
- Record: [`run/`](run/) from `cubxl_run.py` ([`SUMMARY.md`](run/SUMMARY.md), [`stir_trace.json`](run/stir_trace.json),
  [`plunger_trace.json`](run/plunger_trace.json), frames after steps 2, 4, 5, 6, 8, 9, 10, 42 and 43
  in [`run/frames/`](run/frames/), the console in [`run/console.txt`](run/console.txt))

## Before it ran

- **Deck camera at 23:25:58** ([frame](frames/232558Z_deckcam_before.jpg)), before anything
  moved. Vials, stir module and tip rack are where they were on 11-17
  ([11-17 frame](../stir_transfer_5x_20261117/frames/223418Z_deckcam_before.jpg)). Two things
  changed. Vial 1 now holds pink liquid, which is the red from vial 2 that 11-17 transferred.
  The stir module's cable now runs straight down the right side of the vial column, where on
  11-17 it crossed the open deck diagonally. It lies flat on the deck, and nothing in the
  protocol goes below deck Z 20 outside a vial, so the route doesn't matter to the run.
- **A stir-only check first** ([`stir_only_check_20261118`](../stir_only_check_20261118/README.md),
  23:28): CubOS 5/5, and the stirrer read 0 rpm and stalled in both windows.
- The run's own stage 1 checks and all four gates passed (ports, GRBL against the gantry file,
  the Uno answering `31`, `validate_setup`, `--mock`, both shadow checks).

## The run (23:32:58 → 23:38:06 UTC, 308 s)

**45/45 steps, protocol complete.** 172 `G01` moves, no alarms, 0 USB kernel lines. Every step
took the same time as on 11-17 to within 0.1 s. The tip came from A1 and went back into A1.
Plunger HOME check after the run: the firmware said 28.0 mm, and HOME took 12.678 s, which
implies 28.00 mm, so **no lost steps**.

**Stirring: commanded at the right moments, and again it never turned.**

| stir | `stir` step | started (UTC) | stopped by | s | `31` reads | rpm max | stalled |
|---:|---:|---|---|---:|---:|---:|---|
| 1 | 3 | 23:33:49.986 | firmware (stall) | 12.1 | 12 | 0 | yes |
| 2 | 11 | 23:34:42.902 | firmware (stall) | 11.1 | 11 | 0 | yes |
| 3 | 19 | 23:35:24.566 | firmware (stall) | 11.1 | 11 | 0 | yes |
| 4 | 27 | 23:36:06.291 | firmware (stall) | 11.1 | 11 | 0 | yes |
| 5 | 35 | 23:36:47.959 | firmware (stall) | 11.1 | 11 | 0 | yes |

The firmware's replies follow the same sequence as on 11-17: the setpoint ramps from 100 to
600 rpm, and the duty creeps from 0.300 to 0.315. That is the stall branch: each 2 s update
with no pulse pauses 0.75 s, then kicks at full power for 0.5 s. After five such updates it
stops the fan and sets `stalled`. Across this run and the stir-only check, that is seven
windows and about 40 full-power kicks, and D2 saw **not one falling edge**.

The plunger did the same as on 11-17 too. Aspirate 1 started from 0.0 mm (5.00 s); aspirates
2-5 started from the blowout plane, 32.5 mm (2.86 s each), so by plunger travel they drew about
23 µL rather than 20. That is CubOS's pipette, not the stirrer (see the 11-17 README).

## Hand-turn Hall check

[`hand_turn_watch/`](hand_turn_watch/): from 23:40:15 the Uno's `31` was read once a second
with the fan off ([`hall_watch.py`](../stirrer_first_spins_20261103/hall_watch.py) from 11-03,
run for 540 s), and the PR comment asked Ben to turn the fan by hand. Nothing was commanded.

- **310 reads, 23:40:16 → 23:45:28.** Two of them, at 23:43:33 and 23:43:34, show `rpm` 60:
  two falling edges in one 2 s window. Every other read is 0.
- **Those two edges coincide with a USB event.** At 23:43:32 the kernel logged the GRBL
  board's CH340 dropping off USB and coming straight back
  ([`kernel_2340_2350Z.log.txt`](hand_turn_watch/kernel_2340_2350Z.log.txt)). So they may be
  noise from someone handling cables rather than a hand turn. Only Ben can say which.
- **At 23:45:28 the Pi logged USB over-current on every port.** The Uno and the CH340 both
  disconnected, which ended the watch (`write failed: [Errno 5]`). Both came back at 23:45:55,
  dropped again at 23:46:52 and were back at 23:46:55; they are on their usual `by-id` paths.
  A Realtek USB Ethernet adapter (`eth1`, usb 4-1) came up at 23:45:57 with carrier, failed
  at 23:46:53, and the kernel gave up on it (`r8152 failed probe after 3 tries`). The fan was
  off and nothing else was commanded. The stir module runs from the Uno's 5 V, which comes from the Pi's
  USB, so a short in its wiring is one way to get this. Plugging something in is another.

**Ben's own observation** (PR #348, 23:39 UTC): "The stirring worked (it was pulsing) on the stir
only test, then it worked after the first 2 pipette blowouts into it, but after that, I saw no
mixing."

## What the zero says

The code isn't the suspect. The same firmware read 240 rpm two seconds after a start on 11-05
([`trial_stir.jsonl`](../stir_module_trial_20261105/stir/trial_stir.jsonl)), and on 11-03
the Hall input counted while the fan was turned by hand
([11-03](../stirrer_first_spins_20261103/README.md#hand-turn-hall-check-the-sensor-works)).
The wiring is in
[`hardware/vial-stirrer-cubxl`](../../../hardware/vial-stirrer-cubxl/README.md#driving-it-from-the-cubxls-arduino-uno):
5 V to the fan's + and the US1881's VDD; the fan's − to the IRLZ44N's drain; the source and
the US1881's GND to the Uno's GND; D10 through 100 Ω to the gate; the US1881's OUT to D2.

**Ben saw vial 1 stirred in pulses, so the fan now gets power: the repair worked.** The "pulsing" is what the
firmware does when it counts no Hall edges: each 2 s update, 0.75 s off, then 0.5 s at full
power. After five updates it stops the fan, about 11 s in. The firmware's replies were the
same in all five windows, so whatever made windows 4 and 5 look different to Ben (or 3 to 5,
depending on how the windows are counted) came from the module, not from the commands. A bar
thrown off by the full-power kicks would do it. So would an intermittent joint.

Zero edges with the fan moving leaves two explanations:

1. **The Hall signal doesn't reach D2.** The US1881's VDD, GND or OUT lead is open, or the
   sensor has come loose from beside the magnets. Check this first: its leads run in the
   same cable as the fan's, and one of those had already come off.
2. **The holder only twitches and never completes a turn,** so the latch never sees the next
   pole. On 11-03 the fan, turned by hand, "moves jerkily, as if the magnets were catching
   on something", and a kick that rocks the bar would look like pulsed mixing too.

Watching the magnet holder during a stir tells them apart: full turns mean 1, twitches
mean 2. So does turning it by hand through a few full turns while `31` is read; each turn
should count one edge.

## Changed on the Pi

- `~/byu-vcl-stir5x` fast-forwarded from `013f6a4` to `6cdc7eb` (results only, no config or tool changes).
- New in `~/cubxl_runs/`: `stir_only_check_20261118/`, `stir_transfer_5x_20261118/`, their
  `.console` files, `stir_rerun_20261118_frames/` (the deck frame) and `hall_watch_20261118/`.
- `~/cubxl_runs/HOLD` was set at 23:25:57 and removed at 23:51:45, after the USB event.
- Nothing else. `~/CubOS` was not touched.

The "lab" times in [`run/SUMMARY.md`](run/SUMMARY.md) (17:32:58–17:38:06) are an hour late.
`cubxl_run.py` added a fixed −6 h, but Utah has been on MST (UTC−7) since 2026-11-01. The
kernel log's own timestamps (`-07:00`) show the right local time. The 11-17 records have the
same error. `cubxl_run.py` now uses the `America/Denver` zone.

`*.log` files are committed as `*.log.txt`, because the repo ignores `*.log`. The Pi's
hostname is redacted in `kernel_during_run.log.txt` and `hand_turn_watch/kernel_2340_2350Z.log.txt`.
