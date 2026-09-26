# PANDA Arduino firmware — the VCL build

The Arduino Uno on `/dev/ttyACM0` runs **one** firmware that serves the
capper, the line-break sensor, the lights *and* the pipette plunger. Anything
flashed here affects the capper too, so nothing in this directory should be
applied casually.

Upstream: [`BU-KABlab/PANDA_Arduino`](https://github.com/BU-KABlab/PANDA_Arduino)
@ `228615b` ("fixed mixing function for pipette", 2025-08-27).

## ⚠️ 2026-09-17: a newer image is built and committed but **NOT flashed**

`panda_vcl_p20gen2_20260917.hex` corrects the plunger planes and the driver
current to Opentrons' own **P20 GEN2** figures (table below). It could not be
programmed: `avrdude` cannot sync with the board at any baud, because the
Arduino's serial link is corrupting data in both directions. Evidence and the
bench checks are in
[`../results/pipette_p20gen2_20260917/README.md`](../results/pipette_p20gen2_20260917/README.md).

**So the board still runs `panda_vcl_p20_20260915.hex`.** Once one `STATUS`
round-trip parses again, flash with:

```bash
cd ~/panda_fw_vcl && ~/.venvs/pio/bin/pio run -e uno -t upload --upload-port /dev/ttyACM0
```

`pio` is the way to do it — it drives the auto-reset correctly, where a bare
`avrdude` invocation on this Pi does not.

## What is on the board (2026-09-15)

| file | what it is |
| --- | --- |
| `flash_20260915T220346Z.hex` | **Backup of the flash as it was before this change.** Read with `avrdude -U flash:r:...:i` at 2026-09-15 22:03 UTC. Restores the board exactly. |
| `panda-arduino-p20-and-driver-status.patch` | The VCL delta against upstream `228615b`. **Regenerated 2026-09-17**: five files, +161/-12. Verified with `git apply --check` against a fresh clone at `228615b`, and the fresh clone builds. |
| `panda_vcl_p20_20260915.hex` | The image actually flashed on 2026-09-15, and **still what is on the board**. |
| `panda_vcl_p20gen2_20260917.hex` | The P20 GEN2 image. Built and verified, **not flashed** — see the warning above. 17 382 bytes, 53.9% flash, 1429 bytes RAM. |

The patch previously documented as "four files" also carries a
`platformio.ini` change (dropping `lib_extra_dirs = ~/Documents/Arduino/libraries`,
a path that does not exist on the Pi) that the earlier regeneration missed. It
is captured now.

**The backup proved the provenance.** Parsed and compared byte-for-byte, the
16 308 program bytes read off the board were **identical** to a local build of
upstream `228615b` — so the board really was running stock upstream, and the
VCL image is a provably minimal delta from it.

`panda_vcl_p20_20260915.hex` is the exact 17 370-byte image that was written and
verified by avrdude. A rebuild reproduced it bit-for-bit in one environment, but
**the build is not reproducible in general**: `platformio.ini` pins its library
dependencies with `^` ranges, so a clone that resolves a different minor version
builds a slightly different image (17 364 bytes in one such case). Flash the
committed hex if you want exactly what was on the board; rebuild from the patch
if you want the source of truth.

## Upstream `main` does not compile

`228615b` gives a default argument for `dwell_ms` in **both** the declaration
in `include/Pipette.h` and the definition in `src/Pipette.cpp`, which is a hard
C++ error:

```
src/Pipette.cpp:355:86: error: default argument given for parameter 4 of
  'bool mixInPlace(int, float, float, float)'
```

The patch drops the duplicate from the definition; the header keeps it, so the
default is unchanged. Worth sending upstream — as it stands nobody can build
`main`.

## What changed, and why

### Pipette constants — P20 GEN2, from Opentrons

The pipette on the head is a **P20 GEN2** — legible on the body in
`../results/pi5_des4_provision_20260914/pipette_label_p20_gen2.jpg` and in
campaign 36's `cam0_csi0` frame, and confirmed by Ben on 2026-09-17. Ursa's
records had said P300 GEN2, and the 2026-09-15 image was a hybrid: P300
plunger planes with P20 volume limits. Resolved in favour of the P20 GEN2.

Authority is Opentrons
`shared-data/pipette/definitions/1/pipetteModelSpecs.json`, keys
`p20_single_v2.0`/`2.1`/`2.2` (identical positions in all three). Opentrons
states plunger planes as signed offsets in a frame whose `top` is the home
reference; this firmware measures distance **downward** from home, so each
value is `top - <field>` with `top = 19.5`.

| constant | stock | 2026-09-15 | **2026-09-17** | why |
| --- | --- | --- | --- | --- |
| `MAX_VOLUME` | 300.0 | 20.0 | **20.0** | P20 GEN2. `STATUS` reported `max_vol: 300.00` for months. |
| `MIN_VOLUME` | 5.0 | 1.0 | **1.0** | P20 GEN2. The P300 clamp is why `ASPIRATE 0.5` always landed at 35.45: 0.5 clamped up to 5. |
| `PRIME_POSITION` | 36.0 | 36.0 | **28.0** | Opentrons `bottom` −8.5. 36.0 is the P300's plane. |
| `BLOWOUT_POSITION` | 44.0 | 44.0 | **32.5** | Opentrons `blowout` −13. |
| `DROP_TIP_POSITION` | 55.0 | 55.0 | **46.5** | Opentrons `dropTip` −27. Also the ceiling `moveTo` clamps at. |
| `UL_TO_MM` | 0.1098 | 1.8 | **1.34** | `1 / 0.746`, and 0.746 µL/mm is the asymptote of Opentrons' own `ulPerMm` table for `p20_single_v2.1`. The 1.8 was only `36.0 / 20`, i.e. read off a P300 plane. |
| `RUN_CURRENT_PERCENT` | 50 | 17 | **20** | → CS 6, **1.02 A peak** = Opentrons `plungerCurrent` 1.0 A. See the current note below. |
| `HOLD_CURRENT_PERCENT` | 30 | 10 | **5** | → CS 1, **0.29 A peak** = Opentrons `idleCurrent` 0.3 A. |

Two cross-checks that `UL_TO_MM 1.34` is derived rather than guessed:

- The same method applied to the P300 gives 9.1 µL/mm, reproducing
  `UL_TO_MM 0.1098` — the one constant in this firmware that was
  independently calibrated. So the method is validated against a known-good
  value.
- A full-scale 20 µL aspirate travels `20 × 1.34 = 26.8 mm` up from
  `PRIME_POSITION 28.0`, landing the plunger at **1.2 mm**: inside the 28 mm
  top-to-bottom stroke with a small dead band, which is how Opentrons has it.

**All three planes moved down, so every commanded plunger travel is shorter
than before** — the safe direction — and `0 < prime < blowout < drop_tip`,
which `aspirate`/`dispense`/`moveTo` rely on, still holds.

⚠️ **Nominal, not calibrated.** These are Opentrons' figures for the model,
not a measurement of this unit. `UL_TO_MM` needs a gravimetric check once
liquid actually moves.

These three planes now match CubOS's `p20_single_gen2` entry exactly; see
[`../patches/README.md`](../patches/README.md).

### Driver current — the sense resistor is 0.05 Ω, not 0.11 Ω

The 2026-09-15 value of 17 was scaled from an assumed 0.11 Ω sense resistor
and a 500 mA target taken from science-jubilee's Duet config. Both were wrong.
Ursa read `R1`/`R2` = **0.05 Ω** off the Adafruit 6121 schematic, and
Opentrons' own `p20_single_v2.x` runs the plunger at **1.0 A**, idling at
0.3 A. With `vsense = 0` (`enableVSense()` is never called) and the library's
`CS = map(percent, 0, 100, 0, 31)`:

```
I_rms = ((CS+1)/32) * (0.325 / (0.05 + 0.02)) / sqrt(2) = ((CS+1)/32) * 3.283 A
```

| percent | CS | I_rms | I_peak | |
| --- | --- | --- | --- | --- |
| 50 | 15 | 1.64 A | 2.32 A | stock — over the **breakout's** 2 A rating, not just the motor's |
| 17 | 5 | 0.62 A | 0.87 A | 2026-09-15 |
| **20** | **6** | **0.72 A** | **1.02 A** | Opentrons `plungerCurrent` |
| **5** | **1** | **0.21 A** | **0.29 A** | Opentrons `idleCurrent` |

Hold current is mapped to IHOLD **independently** of run current by this
library, not as a percentage *of* it — so the two rows have to be chosen
together. ⚠️ **Fit the Adafruit 1515 heat sink before running at this
current.**

⚠️ **Whether this table is in force depends on power-up order, and cannot be
read back yet.** `RUN_CURRENT_PERCENT` reaches the chip through
`setRunCurrent()`, a UART *write*. `UART` runs straight from A1 to `PDN_UART`,
writes need no reply, and SoftwareSerial's 9600 baud clears the datasheet's
9000 minimum — so whenever the Arduino boots with the 12 V already up (including
every time a host opens the port, which resets it), `setOperationModeToSerial()`
very probably lands, takes the VREF trimmer out of circuit, and this table
governs. If the Arduino boots before the 12 V, the writes reach an unpowered chip
and the trimmer governs until the next reset. So **keep the two matched**: VREF
at 0.55–0.59 V on the wiper gives 1.02–1.09 A peak, the same as the 20 row; it
has been at 0.586 V since 2026-09-26. Full clockwise on the Adafruit 6121 is
~1.5 A rms / 2.2 A peak — its 10 kΩ trimmer is fed from `5VOUT` through 33 kΩ —
not the ~3.3 A rms stated here until 2026-09-26. `IFCNT` will settle the
question once the bridge resistor is on the TX side. See §22.4–22.5 of
[`../docs/opentrons-pipette-wiring.md`](../docs/opentrons-pipette-wiring.md).

### The TMC2209 library is now vendored and patched

`lib/TMC2209/` in the firmware project holds a patched copy of the janelia
library: reads over `SoftwareSerial` cannot work unpatched, which is why
`CMD_PIPETTE_DRIVER_STATUS` always answered `comm = 0`. The patch is
[`../patches/tmc2209-softwareserial-read.patch`](../patches/tmc2209-softwareserial-read.patch);
it is **not** sufficient on its own — the bridge resistor also has to move to
the TX side. Vendoring into `lib/` rather than `.pio/libdeps/` is deliberate
and was verified, not assumed: a sentinel `#error` in the `lib/` copy fails
the build, so that copy is provably what compiles.


`PRIME_POSITION` 36.0, `BLOWOUT_POSITION` 44.0 and `DROP_TIP_POSITION` 55.0 are
**unchanged** — they are mechanical plunger positions, and `UL_TO_MM` 1.8 is
derived from `PRIME_POSITION`, so moving one means re-deriving the other.
They may still be P300 figures; a P20's usable travel is shorter, and
`DROP_TIP_POSITION` 55.0 in particular is worth checking against the real
plunger before anything relies on the ejector.

### New: `CMD_PIPETTE_DRIVER_STATUS = 29`

Ben bridged `RX_PIN` (A0) to `TX_PIN` (A1) with 10 kΩ on 2026-09-15, which is
what makes a TMC2209 read possible — PDN_UART is half duplex, so the driver
answers on the wire it was addressed on, and without the bridge the Arduino
could only ever talk.

Before this, `setupMotor()` wrote six registers and checked none of them, and
no command exposed driver state. A driver sitting at minimum current with its
output stage off was indistinguishable, at the serial port, from a healthy one.

```
OK:{"msg":"Driver status","v":[<comm>,<flags>,<current_scaling>]}
```

* `comm` — `0` no reply at all · `1` communicating but not set up (driver power
  was lost after `setup()`, so defaults reloaded) · `2` set up and communicating
* `flags` — bitmask, `DRVSTATUS_*` in `include/Pipette.h`: over-temperature
  warning/shutdown, short-to-ground A/B, low-side short A/B, **open-load A/B**,
  the 120/143/150/157 °C flags, stealthChop, standstill, hardware-disabled
* `current_scaling` — the driver's actual CS value, 0-31, or `-1` if unread

`open_load_a`/`open_load_b` answer the coil-continuity question without a
meter. Read it with CubOS's own link:

```python
from cubos.instruments.controllers.pawduino import PawduinoLink
link = PawduinoLink.acquire("/dev/ttyACM0", 115200); link.connect()
print(link.send_command(29, timeout=15))
```

## Rebuild / reflash / restore

PlatformIO lives in a user venv on the Pi (`~/.venvs/pio`), toolchain under
`~/.platformio` — no sudo, nothing system-wide.

```bash
git clone https://github.com/BU-KABlab/PANDA_Arduino.git ~/panda_fw_vcl
cd ~/panda_fw_vcl && git checkout 228615b
git apply ~/byu-vcl/cubos/firmware/panda-arduino-p20-and-driver-status.patch
~/.venvs/pio/bin/pio run -e uno -t upload --upload-port /dev/ttyACM0
```

To put the board back exactly as it was:

```bash
AVRDUDE=~/.platformio/packages/tool-avrdude/avrdude
CONF=$(find ~/.platformio -name avrdude.conf | head -1)
"$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P /dev/ttyACM0 -b 115200 -D \
    -U flash:w:~/byu-vcl/cubos/firmware/flash_20260915T220346Z.hex:i
```

Close every serial handle first — CubOS holds `/dev/ttyACM0` for the whole of a
run, and opening the port resets the board.
