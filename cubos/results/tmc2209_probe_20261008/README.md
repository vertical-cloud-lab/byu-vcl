# tmc2209_probe_20261008: after the recabling, the TMC2209 drives the plunger, and `HOME` works

Issue #165, 2026-10-08, CubXL Pi. Ben: *"we are no longer using the Tic t500. Instead the TMC
2209 is connected to the Arduino running the pipette. Check run the probe test to make sure the
pipette is working."* Earlier that afternoon he had unplugged everything and replaced some
cables. The gantry was switched off.

**It passed.** [`tmc2209_probe.py`](tmc2209_probe.py) exited 0. The plunger moved both ways at
every rate the firmware uses, the limit switch stopped it at the top, and the firmware `HOME`
returned `OK`. Every figure is within a few hundredths of a millimetre or a few milliseconds of
the [2026-10-07 pass](https://github.com/vertical-cloud-lab/byu-vcl/blob/2aa4c1a/cubos/results/tmc2209_spreadcycle_20261007/README.md)
on the same firmware.

## Before the probe

- **Pi:** up since 21:51Z (15:51 MDT), `throttled=0x0`. The Arduino and the gantry's CH340 were
  on their usual `by-id` paths, and nothing held either port. There was no Tic on USB.
- **Firmware:** `avrdude -U flash:v` ([log](firmware_verify.log)) reads the flash and writes
  nothing. It matched `panda_vcl_p20gen2_tic796_fastmove_spread_20261007.hex` (fix B,
  `disableStealthChop()`, sha256 `e8ddfe3d…`) and not the 10-01 image. That is the image flashed
  on 10-07, and the one that moves the plunger with the UART wire on pin 9. The hex is
  [committed on PR #260](https://github.com/vertical-cloud-lab/byu-vcl/blob/2aa4c1a/cubos/firmware/panda_vcl_p20gen2_tic796_fastmove_spread_20261007.hex).
- **Script:** the same `tmc2209_probe.py` as on 10-05, 10-06 and 10-07 (sha256 `58cb6aab…`).
  The copy here is because `main` doesn't have it yet; the original is on PR #260.
- **`~/cubxl_runs/HOLD`:** written at 22:36:48Z and removed at 22:37:56Z.
- **The 16:11 MDT systems check** ([`051a8bd`](https://github.com/vertical-cloud-lab/byu-vcl/blob/051a8bd/cubos/results/systems_check_20261008/README.md))
  reported the Tic missing as a fault. That check was written from `main`'s Tic setup, without
  the TMC2209 work on PR #260. With the Tic retired, its absence is expected.

## What the probe saw

22:37:01–22:37:28Z. Plunger only: the gantry's port was never opened. [Log](probe.log),
[rows](tmc2209_probe.json).

| step | today | 10-07, fix B |
|---|---|---|
| connect (resets the Arduino) | 3.77 s, `homed 0` | 3.77 s, `homed 0` |
| `CMD 29` | `comm = 0` | `comm = 0` |
| switch read at the start | closed (below the top) | closed |
| UP search, 0.5 mm moves at 400/s | switch opened in move 3, **~1.02 mm** | move 3, ~1.05 mm |
| ladder: switch reopened after a 2 mm back-off, at 1,000 / 2,500 / 10,000 | ~2.05 / 2.12 / 2.09 mm | ~2.05 / 2.10 / 2.12 mm |
| time to the trip at 2,500/s | 0.774 s | 0.770 s |
| each 2 mm back-off at 400/s | 4.034 s | 4.034–4.035 s |
| `HOME` from 2 mm below | `OK` in 1.348 s | `OK` in 1.347 s |
| after `HOME` | `homed 1`, `pos 0.00`, switch closed | same |
| end | `EMAG_OFF` → `OK` | same |

## What it shows

- **The driver turns the motor both ways.** UP opened the switch, and each 2 mm DOWN closed it
  again. So `STEP` and `DIR` reach the board, the driver is enabled, the 12 V is on, and both
  coils are connected.
- **DIR LOW is still up.** No coil pair was reversed in the recabling. The firmware's blind
  `HOME` seek, which CubOS runs on connect, still goes toward the switch.
- **No lost steps at any rate.** Each rung reopened the switch after the 2 mm it had backed off,
  including the 10,000 rung (~8,700 steps/s in practice), the rate `MOVE_TO` and `ASPIRATE` use.
- **The plunger hadn't moved since 10-07.** It started ~1.02 mm below the switch, where the
  post-run `HOME` on 10-07 left it (1 mm below).

## What it doesn't show

- **Whether the firmware's current settings reached the driver.** `CMD 29` reads `comm = 0`
  because the 10 kΩ bridge is still on the RX side, so nothing can be read back. With the UART
  wire on pin 9, the chip runs the firmware's 0.72 A rms moving and 0.21 A rms at rest. With the
  wire off or loose, it runs on the trimmer and can hold up to ~0.77 A rms at rest. The plunger moves
  either way (10-07), so the probe can't tell them apart.
- **The rest of the stroke and the tip handling.** The probe keeps the plunger within ~2 mm of
  the switch. Prime, aspirate, blowout and the tip-eject push are covered by `pipette_test`,
  which needs the gantry.

## Next

1. **Feel the driver board and the pipette after a few minutes.** Room temperature means the
   firmware's settings are in force. Warm, as on 10-07, means the UART wire on pin 9 came off or
   is loose after the recabling. The pipette still works that way, but it can hold up to ~0.77 A at rest.
2. **Run `pipette_test` once the gantry is on.** Use `cubxl_run.py --no-tic`, as on 10-07.
   Without `--no-tic` the runner looks for the Tic and refuses to start.
3. **Power-up order still matters.** The probe's port open sent the settings with the 12 V on.
   If the 12 V is switched off and on again, the driver forgets them until the next port open.
   Every CubOS run opens the port, so runs aren't affected, only idle time.

## State left

- **Plunger:** homed, 1 mm below the switch (`pos 0.00`). The next port open resets the Arduino
  and clears `homed`. CubOS re-homes on connect.
- **Electromagnet:** off.
- **Gantry:** not touched, and its port wasn't opened.
- **Driver:** TMC2209 on firmware fix B, 12 V on, holding at rest.
- **Pi:** `throttled=0x0`, EXT5V 5.14 V, and no USB events in the kernel log since boot
  ([post_state.txt](post_state.txt)).
- **On the Pi:** `~/cubxl_runs/tmc2209_probe_20261008/` holds these files and copies of both hex
  images.

To rerun:

```bash
cd ~/cubxl_runs/tmc2209_probe_20261008 && \
  PYTHONPATH=$HOME/CubOS/packages/core/src ~/CubOS/.venv/bin/python tmc2209_probe.py tmc2209_probe.json
```
