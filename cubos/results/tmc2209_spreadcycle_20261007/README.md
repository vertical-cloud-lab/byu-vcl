# tmc2209_spreadcycle_20261007: with fix B, the TMC2209 runs `pipette_test` 12/12 with everything plugged in

Issue #169, [PR #260](https://github.com/vertical-cloud-lab/byu-vcl/pull/260), 2026-10-07,
CubXL Pi. Ben: *"Try the probe test as is, and if it doesn't work, I want to try fix B so we
can leave everything plugged in when idle. flash the spreadCycle fix, and if the probe test
comes back successful, run the pipette test. I realized I unplugged EN from A4 instead of
UART. I just plugged EN back in to A4."*

**It worked.** With EN back on A4 and the UART wire on pin 9, the 10-01 firmware didn't move
the plunger, in two probes. Fix B (`disableStealthChop()`) did. `tmc2209_probe.py` passed, then
`pipette_test` ran 12/12 with no lost steps. Its plunger timings match the Tic's 10-06 run to
the hundredth of a second. Afterwards Ben confirmed that the board is an Adafruit 6121, and
found it at room temperature at idle. That is the sign that the firmware's hold current is in
force, not the trimmer's ([Ben's follow-ups](#bens-follow-ups)).

## Timeline (UTC)

| time | what | result |
|---|---|---|
| 18:33:10 | Both USB devices drop off the Pi and re-enumerate within 2 s, so the Arduino reset. Ben's *"I just plugged EN back in to A4"* came at 18:34:24 | |
| 18:40:05 | run 37667869310, on Ben's first version of the comment: the probe as is ([log](baseline_probe.log)) | no switch within 3 mm UP |
| 18:41:00 | that run is cancelled by the comment edit. It had written `HOLD`, and flashed nothing | |
| 18:49:52 | this run: the probe as is ([log](asis_probe.log)) | no switch within 3 mm UP |
| 18:51:48 | build ([script](build_spreadcycle.sh), [log](build.log)) | the unedited copy rebuilds to the 10-01 image byte-for-byte |
| 18:52:15 | flash ([script](flash_spreadcycle.sh), [log](flash.log)) | 10-01 image matched before, fix B matched after |
| 18:52:54 | the probe on fix B ([log](spread_probe.log)) | **exit 0** |
| 18:55:08–18:57:25 | [`pipette_test_20261007`](../pipette_test_20261007/SUMMARY.md) | **12/12** |

## The change

[`panda-arduino-spreadcycle.patch`](../../firmware/panda-arduino-spreadcycle.patch), one line
in `setupMotor()`:

```diff
-    stepperDriver.enableStealthChop();
+    stepperDriver.disableStealthChop(); // [VCL] spreadCycle: initialize() turns pwm_autoscale off, ...
```

The compiler inlines both calls, so the new image differs from
`panda_vcl_p20gen2_tic796_fastmove_20261001.hex` in 2 bytes, one instruction at 0x212E:
`andi r24, 0xFB` (clear GCONF bit 2, `en_SpreadCycle`) became `ori r24, 0x04` (set it). Same
size, 17,468 bytes. It was built in `~/panda_fw_vcl_tic796_fast_spread`, a copy of the 10-01
tree. Before the edit, a clean rebuild of the copy gave the 10-01 image (sha256 `6d2dc977…`),
so the toolchain and libraries hadn't drifted. The new image is
[`panda_vcl_p20gen2_tic796_fastmove_spread_20261007.hex`](../../firmware/panda_vcl_p20gen2_tic796_fastmove_spread_20261007.hex),
sha256 `e8ddfe3d…`. [`flash_before_20261007.hex`](flash_before_20261007.hex) is the whole
flash as read back before writing.

## The probe on fix B

Same script, same sha256 (`58cb6aab…`) as on 10-05, 10-06 and 10-07.

| step | fix B, today | 10-07 run, StealthChop image |
|---|---|---|
| UP search, 0.5 mm moves at 400/s | switch opened in move 3, **~1.05 mm** | ~1.65 mm |
| ladder: switch reopened after a 2 mm back-off, at 1,000 / 2,500 / 10,000 | ~2.05 / 2.10 / 2.12 mm | ~2.05 / 2.12 / 2.13 mm |
| time to the trip at 2,500/s | 0.770 s | 0.774 s |
| `HOME` from 2 mm below | `OK` in 1.347 s | `OK` in 1.348 s |

The plunger started ~1.05 mm below the switch. The 10-07 `HOME` had left it 1 mm below, so
nothing moved it in between, which fits a motor that never turned in the two as-is probes.

## `pipette_test_20261007`

`cubxl_run.py` with the 10-06 Tic run's arguments plus `--no-tic`: Ben's 10-02 files
(`cub_xl_ben_3_instrument.yaml`, `ben_2vials_tiprack.yaml`), `--home-check`, frames after steps
2, 3, 4, 8, 9 and 10. The Pi's checkout is still at byu-vcl `021ad70`. CubOS is at `496819c`
with the same 4 patches. All four gates passed.

| plunger command | TMC2209 + fix B, today | Tic, 10-06 |
|---|---:|---:|
| `HOME` on connect | 0.94 s | 0.94 s |
| `MOVE_TO 28.0` (prime) | 2.56 s | 2.56 s |
| `MOVE_TO 0.0` | 2.56 s | 2.56 s |
| `ASPIRATE 20` | 5.00 s | 5.00 s |
| `MOVE_TO 32.5` (blowout) | 2.86 s | 2.86 s |
| `MOVE_TO 46.5` (tip eject) | 4.65 s | 4.65 s |
| `MOVE_TO 28.0` | 1.70 s | 1.70 s |
| post-run `HOME` from 28.0 mm | 12.698 s ⇒ 28.04 mm (**+0.04 mm**) | 12.679 s ⇒ 28.00 mm |
| run | **12/12**, 137 s | 12/12, 141 s |

The firmware times the steps, so equal times only show that every command completed. The
post-run `HOME` is the check on lost steps: +0.04 mm is about 32 of its ~23,100 microsteps. No
USB lines in the kernel log during the run. The frames are top-down deck views and don't show the
tip clearly. The 10-06 Tic run isn't committed. It is on the Pi at
`~/cubxl_runs/pipette_test_20261006/`.

## What it settles

- **The firmware's StealthChop setup was the fault, and its UART writes land.** The as-is probe
  at 18:49:52Z and the fix B probe at 18:52:54Z were three minutes apart, with the same wiring
  and the same 12 V, and only one bit of GCONF different. One didn't move, and the other moved
  at every rate. That's what the 10-06 reading of the library predicted (wiring doc §24).
- **Everything can stay plugged in.** The chip now runs on the firmware's current, regulated:
  `IRUN` CS 6 while moving and `IHOLD` CS 1 at rest. On the 6121's 0.05 Ω (Ben has confirmed
  the board is one) that's 0.72 A rms and 0.21 A rms, Opentrons' 1.0 A peak `plungerCurrent`
  and 0.3 A `idleCurrent`. While the writes land, the trimmer sets nothing
  (`i_scale_analog = 0`).
- **The same image runs the Tic.** The Tic's STEP/DIR input ignores the UART writes, so swapping
  drivers needs no reflash, only `--no-tic` on `cubxl_run.py` while the TMC2209 is on.

## What doesn't fit: the 10-07 pass

The [10-07 record](../tmc2209_probe_20261007/README.md) says the UART wire was off. It was EN
that was off A4. With EN off and the UART wire on, the StealthChop image moved the plunger at
every rate. But EN is low either way: `setupPipette()` drives A4 low on every reset, and the
6121 pulls EN down with 20 kΩ. So pulling EN can't by itself change anything the chip sees.
For that run to move, the firmware's writes can't have reached the chip, which left it on its
standalone defaults: trimmer current, and StealthChop with automatic scaling. A UART wire that
wasn't making contact would do it, for example one loosened while EN was being pulled and
reseated at ~18:33Z, when both USB devices dropped off the Pi while Ben was at the header. That
is a guess, and nothing recorded can check it now.

In practice it doesn't matter while the writes land. If they ever don't, the chip falls back to
the trimmer, which also moves the plunger, as 10-07 showed. That makes VREF at 0.55–0.59 V the
backstop, so leave it there.

## Ben's follow-ups

- **18:53:47Z:** *"I felt vibrations on the first probe run (at least I think it was the first
  one.)"* Both probes before the flash were the 10-01 image, so whichever he counts as the
  first, it was one of them. That fits wiring doc §24: current in the coils and steps
  arriving, but too little current to turn the plunger. It is light evidence. He isn't sure of
  the run, and on 10-05 a 30 s buzz in what should have been the same state gave nothing he
  could feel.
- **21:10:37Z:** *"the new board is the Adafruit 6121."* So the current figures here stand, from
  its 0.05 Ω sense resistors: 0.72 A rms moving, 0.21 A rms at rest.
- **21:10:37Z:** *"I checked, and the board is at room temperature."* That is check 1 below, and
  it passed, assuming the 12 V was on. The chip is holding the firmware's `IHOLD`. On the
  trimmer it would hold ≈0.77 A rms at rest and turn warm, as it did on 10-07.

## Three things for Ben to know

1. **Idle temperature is the free check that the writes are landing.** After a run, with
   everything plugged in and the CubXL idle, the board and pipette should sit near room
   temperature, cooler than on 10-07. Warm like 10-07 means the trimmer is in charge again.
   *Done after this run: room temperature (above).*
2. **Power-up order.** If the 12 V comes on after the Arduino's last reset (the Pi booted first,
   say), the writes went to an unpowered chip. It then runs on the trimmer and holds full
   current at rest until a host opens the port. CubOS opens it at the start of every run, so
   runs always get the firmware's settings. Only idle time before the first run is affected.
   12 V first, then the Pi, avoids it.
3. **SpreadCycle is louder than StealthChop.** A faint hiss at rest and more buzz while moving
   are normal.

## State left

- **Firmware:** `panda_vcl_p20gen2_tic796_fastmove_spread_20261007.hex`, verified after the
  write.
- **Plunger:** homed by the post-run `HOME`, 1 mm below the switch. The next port open resets the
  Arduino and clears `homed`. CubOS re-homes on connect.
- **Gantry:** homed by the protocol's last step.
- **Electromagnet:** off, `EMAG_OFF` → `OK` after the run.
- **Driver:** TMC2209, UART mode, spreadCycle, holding `IHOLD` at rest. EN on A4, UART on pin 9,
  VREF 0.586 V, 12 V on.
- **`~/cubxl_runs/HOLD`:** run 37667869310's (18:40:52Z) was replaced with this run's at
  18:49:49Z, then removed at 18:59:21Z.
- **Pi:** up 21 h, `throttled=0x0`, EXT5V 5.13 V. No USB drops after the one at 18:33Z.
- **On the Pi:** `~/panda_fw_vcl_tic796_fast_spread/` (the build tree),
  `~/cubxl_runs/tmc2209_spreadcycle_20261007/` and `~/cubxl_runs/pipette_test_20261007/`.

## Going back

To put the 10-01 image back, close every handle on the Arduino's port first:

```bash
AVRDUDE=~/.platformio/packages/tool-avrdude/avrdude
CONF=$(find ~/.platformio -name avrdude.conf | head -1)
PORT=/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00
"$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P "$PORT" -b 115200 -D \
    -U flash:w:$HOME/cubxl_runs/tmc2209_spreadcycle_20261007/panda_vcl_p20gen2_tic796_fastmove_20261001.hex:i
```
