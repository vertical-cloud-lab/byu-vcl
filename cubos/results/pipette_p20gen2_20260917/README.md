# 2026-09-17 — P20 GEN2 alignment landed; the trio could not run

Requested by @benwhitney5463 on PR #171: run the trio again (the homing
obstruction was fixed), address [Ursa's review][review], and "make values
match in all locations for the P20 GEN2". Ben also reported the bench result
that settles the driver question: **pulling the plunger by hand with the
driver plugged in and powered, it moves freely — no holding torque, so no
coil current.**

[review]: https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5719634392

**The trio did not run and the firmware was not flashed.** Both are blocked
by the same thing: `/dev/ttyACM0` — the capper + pipette Arduino — is
corrupting serial data in both directions. Everything that does not depend on
that link was completed.

## 🔴 The blocker: the Arduino's serial link drops bytes

`PawduinoLink.connect()` is the exact gate `run_protocol` hits, right after
validation and *before* the gantry port is opened. Run twice, read-only:

```
attempt 1: FAILED -> UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe1 in position 1
attempt 2: FAILED -> PawduinoLinkConnectionError: Pawduino on /dev/ttyACM0 did not
                     answer hello: Timed out (5.0s) waiting for response to command 0
```

So this is a hard block, not a judgement call — a run aborts at instrument
connect with zero steps and no motion commanded.

### The firmware is alive and is the right image

Replies *start* correctly and are cut off mid-stream:

```
badjson  OK:{"homed":0,"pos":0.00,"max_vol":2
badjson  OK:{"homed":0,"pos":0.00,"max_vol":2
```

`max_vol` starting with `2` confirms the 2026-09-15 p20 image is running
(stock BU firmware reports 300.00). Immediately after a USB-level reset one
probe got as far as `"Hello from Pawduino!"` and `20.00}`, mangled. So the
sketch runs and answers; the bytes are lost between the ATmega328P and the
Pi.

### Quantified

| measurement | result |
|---|---|
| `STATUS` (command 14) round-trips that parse | **0 of 25** |
| idle traffic with nothing sent | 10 bytes in 8 s — so the board is **not** babbling |
| `avrdude -n` sync, `-c arduino` at 115200 / 57600 / 19200, and `-c stk500v1` | fails at every one; `resp=` differs on every attempt |
| USBDEVFS_RESET (equivalent to a replug) | device re-enumerates, link still broken |

Two details worth keeping:

- **It is not line noise.** Separate runs produced *near-identical* byte
  sequences (`\x19\x01\x9b\x01\x9e\x01\x1f\x0c\xe1\xe1\xe1\xd2\x00\x00p...`
  differing in one byte), so what comes back is structured data, not random
  bits.
- **One early capture was the board's own USB serial-number string
  descriptor in UTF-16LE** — the `…3335351018130` of
  `03535343335351018130` with interleaved NULs — arriving on the *data*
  endpoint. That is pathological at the USB layer, not the sketch's output.

### This predates the session

`dmesg` shows the Arduino re-enumerating at kernel timestamp **510334**
against an uptime of 511786 s when first queried — about five minutes before
this session made any contact with the board. The first probe of the session
already found it broken. The USB serial number is unchanged
(`03535343335351018130`), so it is the same board, not a substitution.

### What to check, cheapest first

1. **Power-cycle the Arduino properly — unplug and replug the USB cable.** A
   `USBDEVFS_RESET` from the Pi is not a power cycle: neither the ATmega16U2
   nor the 328P loses state. Then one `STATUS` should return valid JSON.
2. **The 5 V rail.** The TMC2209's `VDD` is fed from the Arduino's 5 V, which
   comes from USB. If the rewiring added load, or there is a partial short,
   the rail sags and UART timing goes with it — which looks exactly like
   dropped bytes. A Pi 5 port plus a raised driver current is a plausible
   combination here.
3. **Anything the rewiring put on `D0`/`D1` or near `RESET`.** `D0`/`D1` are
   the hardware UART that both the sketch *and* the bootloader use — a wire
   there corrupts both, which is what is observed. A wire near `RESET` gives
   erratic resets, which would also explain avrdude never syncing.
4. **The USB cable itself**, swapped for a known-good one.

Until one `STATUS` parses, neither a protocol run nor a reflash is possible.

## ✅ P20 GEN2: the numbers now agree in all three places

Ben confirmed the model. Authority is Opentrons
`shared-data/pipette/definitions/1/pipetteModelSpecs.json`, keys
`p20_single_v2.0`/`2.1`/`2.2` (identical positions in all three). Opentrons
states plunger planes as signed offsets in a frame whose `top` is the home
reference; the firmware and CubOS both measure *downward* from home, so each
value is `top - <field>` with `top = 19.5`.

| | Opentrons | **P20 GEN2** | firmware was | CubOS was |
|---|---|---|---|---|
| `PRIME_POSITION` / `prime_position` | `bottom` −8.5 | **28.0** | 36.0 | 5.0 *(placeholder)* |
| `BLOWOUT_POSITION` / `blowout_position` | `blowout` −13 | **32.5** | 44.0 | 7.0 *(placeholder)* |
| `DROP_TIP_POSITION` / `drop_tip_position` | `dropTip` −27 | **46.5** | 55.0 | 10.0 *(placeholder)* |
| `UL_TO_MM` | `ulPerMm` → 0.746 µL/mm | **1.34** | 1.8 | — |
| `mm_to_ul` (CubOS) | — | **1.0** (pass-through) | — | 1.0 |
| `MAX_VOLUME` / `MIN_VOLUME` | 20 / 1 µL | **20.0 / 1.0** | 20.0 / 1.0 | 20.0 / 1.0 |

Two cross-checks that 1.34 is derived rather than guessed:

- `1 / 0.746 = 1.34`, and 0.746 µL/mm is the asymptote of Opentrons' own
  `ulPerMm` table for `p20_single_v2.1`. The same method on the P300 yields
  9.1 µL/mm — reproducing `UL_TO_MM 0.1098`, the one constant in this
  firmware that was independently calibrated.
- A full-scale 20 µL aspirate travels `20 × 1.34 = 26.8 mm` up from
  `PRIME 28.0`, landing the plunger at **1.2 mm**: inside the 28 mm
  top-to-bottom stroke with a small dead band, as Opentrons has it. The old
  1.8 was only `36.0 / 20`, i.e. read off a P300 plane.

**All three planes moved down, so every commanded plunger travel is shorter
than before** — the safe direction — and the ordering
`0 < prime < blowout < drop_tip`, which `aspirate`/`dispense`/`moveTo` rely
on, is preserved.

The CubOS placeholders were worse than a mis-scaling: they are sent as
**absolute `MOVE_TO` targets**, so `5/7/10` aimed 23–36 mm short of the
planes a P20 GEN2 plunger uses.

Verified end to end against the installed tree:

```
CubOS p20_single_gen2: zero=0.0 prime=28.0 blowout=32.5 drop_tip=46.5 mm_to_ul=1.0
20 uL aspirate -> ASPIRATE arg = 20.0 * 1.0 = 20.0 (microlitres, pass-through)
firmware applies UL_TO_MM 1.34 -> 26.8 mm from PRIME 28.0 -> lands at 1.2 mm
```

### Driver current, on the real sense resistor

Ursa read `R1`/`R2` = **0.05 Ω** off the Adafruit 6121 schematic; this repo
had assumed 0.11 Ω on 2026-09-09 and scaled every figure from it. With
`vsense = 0` and `CS = map(percent, 0, 100, 0, 31)`:

| percent | CS | I_rms | I_peak | |
|---|---|---|---|---|
| 50 | 15 | 1.64 A | 2.32 A | BU original — over the breakout's 2 A rating |
| 17 | 5 | 0.62 A | 0.87 A | VCL 2026-09-15 |
| **20** | **6** | **0.72 A** | **1.02 A** | **`RUN_CURRENT_PERCENT`, = Opentrons `plungerCurrent` 1.0 A** |
| **5** | **1** | **0.21 A** | **0.29 A** | **`HOLD_CURRENT_PERCENT`, = Opentrons `idleCurrent` 0.3 A** |

The 500 mA target used on 2026-09-09 was **science-jubilee's Duet choice,
not Opentrons'**. Opentrons' own `p20_single_v2.x` runs the plunger at 1.0 A
and idles at 0.3 A. ⚠️ **Fit the Adafruit 1515 heat sink before running at
this current.**

## ✅ The TMC2209 read path, and why `comm = 0` proved nothing

Retracted: this repo treated `comm = 0` as proof that no register write had
ever landed. A read over `SoftwareSerial` on an AVR **cannot** succeed with
this library regardless of wiring — `SoftwareSerial::write()` runs `cli()`, so
no echo is ever received, and `sendDatagramBidirectional()` then discards the
first four bytes of the driver's real reply as if they were that echo. Writes
need no echo and may have been landing all along.

`cubos/patches/tmc2209-softwareserial-read.patch` skips the echo
wait-and-discard when `software_serial_ptr_` is set. It is vendored into
`lib/TMC2209/` in the firmware project rather than patched in
`.pio/libdeps/`, so a `pio pkg` refresh cannot silently undo it — **proven**,
not assumed: inserting a sentinel `#error` into the `lib/` copy fails the
build.

⚠️ **The patch alone is not enough.** The bridge resistor must also move to
the TX side (`A1 -> 1k -> node`, with `A0` and `PDN_UART` directly on the
node). With `A1` wired straight to `PDN_UART`, the push-pull TX shorts out
the driver's reply.

## Gates — all green, against the installed tree

| gate | result |
|---|---|
| `pytest packages/core/tests` | **2544 passed, 17 skipped, 0 failed** |
| `validate_setup` | **PASS** |
| `run_protocol --mock` | **12/12 steps** |
| `passive_shadow` | **0 interferences** |
| `passive_shadow --tip-stuck` | **0 interferences** |

Firmware: builds clean, 17382 bytes (53.9% flash), 1429 bytes RAM (69.8%).
Both patches verified with `git apply --check` against fresh clones —
`PANDA_Arduino` @ `228615b` and the pristine TMC2209 10.1.1 — and the fresh
clone builds.

## Machine state — nothing was commanded

| | |
|---|---|
| Gantry motion | **none** — `/dev/ttyUSB0` opened read-only for `?` status and `$$` only |
| GRBL | `<Alarm\|WPos:409,309,124\|Pn:X>`; `$130/$131/$132` = 409.000 / 309.000 / 124.000, `$20=1` |
| Plunger | **not actuated** — no travel accumulated this session |
| Electromagnet | not energized; no capper command reached the board |
| Arduino flash | **unchanged** — avrdude never synced, so no erase or write occurred |
| `~/CubOS` | `496819c` + 3 patches (the p20 one now wider) |

`Alarm` with `Pn:X` is the expected resting state, not a leftover fault:
`$22=1` makes GRBL boot into Alarm until homed, and `Pn:X` is the carriage
parked on X's max switch with `$23=0` (home to max). Step 0 of the protocol
unlocks and homes.

## Files here

| | |
|---|---|
| `serial_link_diagnostics.txt` | the USB inventory, the `dmesg` timeline, the avrdude sweep, the 25× `STATUS` integrity test, the passive capture, and both `PawduinoLink.connect()` attempts |
| `pytest.log`, `validate.log`, `mock.log`, `shadow_nominal.log`, `shadow_tipstuck.log` | the five gates |
| `cubos_patches_applied.txt` | `git diff --stat` of the installed CubOS tree |

The built image is `cubos/firmware/panda_vcl_p20gen2_20260917.hex`. It has
**not** been programmed onto the board.
