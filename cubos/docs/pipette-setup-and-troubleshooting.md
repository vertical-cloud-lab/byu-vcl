# The Opentrons P20 on the CubXL — setup and troubleshooting

Status as of **2026-09-22**. This is the map; the detail is in
[`opentrons-pipette-wiring.md`](./opentrons-pipette-wiring.md), which is the
durable technical record and is where new findings go.

The pipette is an **Opentrons P20 GEN2** single-channel, mounted on the CubXL
gantry beside the capper/decapper and driven by an **Adafruit 6121 TMC2209**
breakout off an **Arduino Uno R3**. CubOS speaks to that Arduino over
`/dev/ttyACM0`, which it shares with the capper's electromagnet and line-break
sensor. The gantry is a separate stepper system on `/dev/ttyUSB0` — see §15 of
the wiring doc, because conflating the two has cost real time.

## Where it stands

**The motion half works. The plunger has never physically turned.**

Every software and geometry problem between a protocol and the plunger is
solved and verified on hardware:

| | |
|---|---|
| tipped-pipette travel | **works** — the hover clamp lets `safe_z 115` coexist with a 35 mm tip on a machine whose Z tops out at 124 |
| `pick_up_tip` XY | **works** — commands the measured jog point to the millimetre, three runs running |
| `aspirate` / `blowout` / `drop_tip` | **execute**, reach the right planes, and the firmware emits the steps |
| volume conversion | **single conversion** — `mm_to_ul: 1.0` in CubOS, the calibration constant in the firmware |
| plunger retraction | **un-gated** since 2026-09-18 — the limit-switch loop reads closed |
| passive-instrument sweep | **0 interferences**, nominal and tip-stuck |
| the plunger itself | 🔴 **silent. No coil current, no holding torque, no sound.** |

Campaign 54 (2026-09-18) is the high-water mark: 12/12 steps, and for the first
time every plunger command — including the two retractions — emitted its steps
at the commanded rate with the LEDs corroborating the serial trace
command-for-command.

### What is eliminated, and what is left

```
  Arduino STEP/DIR output      PROVEN   1592 steps at the commanded rate
  polarity and timing          PROVEN   B/F LEDs match the trace, per command
  Arduino pin map              FIXED    Cubware's diagram is shifted one pin
  10-pin pipette header        VERIFIED across three sources; 180 deg flip excluded
  limit-switch gate            OPEN     retractions execute
  VM at the screw terminal     13 V     measured 2026-09-17
  EN at the driver pin         0 V      candidate B ELIMINATED, 2026-09-21
  serial link to the Pi        HEALTHY  10/10 clean round-trips
  ------------------------------------- everything above is ruled out
  coil path to the windings    OPEN     candidate A CONFIRMED — both pairs read
                                        kOhms where a winding reads ohms
  TMC2209 DIAG                 5 V      candidate C LIVE — the chip is
                                        reporting a driver error
```

Two faults, and plausibly one story: an open coil path that the driver has been
chopping into at a VREF-pot setting worth ~3.3 A rms, for many sessions. See
§16 of the wiring doc.

### What to do next, cheapest first

The four measurements landed on 2026-09-21 and are worked through in §16 of the
wiring doc. What they leave:

1. 🔑 **Look at the colours in the two screw-terminal blocks.** No meter needed.
   **Blue and red belong together in one block; black and green in the other.**
   Blue+black in one and red+green in the other splits each coil *across* the
   blocks — the driver then sees an open circuit on both phases, the motor is
   silent with no buzzing, and both `1A`–`1B` and `2A`–`2B` read high. That is
   every symptom this pipette has, with nothing actually broken. Confirm with
   the meter, power off: if **`1A`–`2A`** or **`1B`–`2B`** reads a few to a few
   tens of ohms, swap two wires and it is fixed.
2. **If not that, take the ribbon out of the driver's terminals and re-measure.**
   In-circuit readings have the output stage in parallel and cannot localise a
   break. Blue–red and black–green at the loose ends; then at the pipette's own
   10-pin header (coil A = pins 3–4, coil B = pins 1–2) to split the ribbon from
   the motor. **Reseat the FC-10P first** — the limit switch on pins 6/7 works,
   and those sit in the two rows *furthest* from the tip while all four coil
   conductors sit in the two rows nearest it.
3. 🔴 **Turn the VREF pot down before the driver is powered again.** This is the
   step that protects a replacement. Target ≈ 0.55 V at the wiper for ~1.0 A
   peak; wind it well below that for a first re-test. Fit the 1515 heat sink.
4. **Then re-check `DIAG`.** Clear, with a real load and sane current ⇒ the chip
   survived. Still 5 V ⇒ replace the board.
5. **`VREF` at the trimmer wiper** — still unmeasured, and now the most valuable
   remaining probe. Healthy ⇒ the internal regulator is fine and `DIAG` is a
   latched output-stage fault. ≈ 0 V ⇒ the chip is dead.
6. **`INDEX` during a driven leg.** The 0 V reading is not yet usable — it is
   not recorded whether steps were being consumed at the time.
   [`../tools/pipette_driver_measure.py`](../tools/pipette_driver_measure.py)
   opens a bounded, direction-labelled window for exactly this.

### Two things queued behind the first real movement

- 🔴 **The board is running the 2026-09-15 image, not the P20 GEN2 one.** Proven
  by `avrdude -U flash:v:` against all three candidates. CubOS carries the
  Opentrons planes (prime 28.0 / blowout 32.5 / drop_tip 46.5) while the firmware
  still carries the P300-derived 36.0 / 44.0 / 55.0 and `UL_TO_MM 1.8`. `MOVE_TO`
  is absolute so `blowout` and `drop_tip` land where CubOS asks; **`aspirate` does
  not**, because it is computed inside the firmware. Flashing
  [`../firmware/panda_vcl_p20gen2_20260917.hex`](../firmware/panda_vcl_p20gen2_20260917.hex)
  closes that, and carries `tmc2209-softwareserial-read.patch`, without which
  `DRV_STATUS` — and with it the specific cause behind `DIAG` — cannot be read
  at all. ⚠️ **Correction:** this was previously described as also dropping run
  current from ~2.3 A to ~1.02 A peak. It does not, until UART works:
  `RUN_CURRENT_PERCENT` is applied by a UART register write and `comm = 0` means
  none has ever landed, so the VREF pot is still the only thing setting current.
  Turning the pot down is the action; see §16.7 of the wiring doc.
- **Check the first successful move against a ruler.** `setMicrostepsPerStep(16)`
  is a UART write that has never been confirmed to land, so the MS1/MS2 straps
  decide and their default is 1/8 — half what `STEPS_PER_MM 1592` assumes. The
  firmware already contradicts itself about this.

## What is in this PR

| | |
|---|---|
| [`opentrons-pipette-wiring.md`](./opentrons-pipette-wiring.md) | the technical record: pin maps, the source inventory, every measurement, and two retracted hypotheses kept visible |
| [`pipette-thread/`](./pipette-thread/README.md) | the discussion from PR #171, migrated verbatim with links back |
| [`../firmware/`](../firmware/README.md) | the VCL PANDA build, the stock backup, both hex images, and the patch against upstream |
| `../patches/p20-gen2-plunger-constants.patch` | CubOS `p20_single_gen2` from Opentrons' own specs, replacing placeholders |
| `../patches/tmc2209-softwareserial-read.patch` | makes the janelia TMC2209 read path work on an AVR at all |
| `../patches/tipped-hover-clamp*.patch` | lets a tipped pipette travel on a machine whose ceiling is below `safe_z + tip` |
| `../patches/pipette-connect-tolerate-failed-home*.patch` | the escape hatch for an unreferenced plunger — **not a bug fix**, remove once homing works |
| [`../tools/`](../tools/) | `pipette_driver_measure.py`, `pipette_driver_probe.py`, `pipette_bench_check.py`, `run_with_plunger_trace.py` |
| `../results/pipette_*` | 17 sessions of run logs, plunger traces, G-code, camera frames and `$$` dumps |

## Running it

CubOS lives on `rpi-5-des4` at `~/CubOS`; its install and patch state are in
[`SOP/raspberry-pi-cubos-setup.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/SOP/raspberry-pi-cubos-setup.md),
which is on [#171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171) and not in this PR. Run from a
foreground SSH session — a headless run logs *"Breakpoint skipped because stdin
is not interactive"* and continues.

```bash
C=~/byu-vcl/cubos/configs; PY=~/CubOS/.venv/bin/python
G=$C/gantry/cub_xl_ben_pipette_capper.yaml
D=$C/deck/ben_6vials_tiprack.yaml
P=$C/protocol/vcl/pipette_test.yaml

$PY -m cubos.tools.validate_setup      $G $D $P      # nothing moves
$PY -m cubos.tools.run_protocol --mock $G $D $P
$PY ~/byu-vcl/cubos/tools/passive_shadow.py $G $D $P --tip-stuck
$PY ~/byu-vcl/cubos/tools/run_with_plunger_trace.py  $G $D $P   # the real run, timed
```

Four gates pass offline and none of them models the *other* instrument on the
head, which is what `passive_shadow.py` is for. Re-home before every run: the
GRBL board resets when the port opens and comes up in `Alarm`.

## Things that cost a session each, so they are worth reading twice

- **`WPos` is GRBL's step counter, not a measurement.** With the stepper supply
  off the controller accepts every `G01`, emits the steps, and reports a
  plausible position while the machine stands still. `Pn:` is driven by the limit
  switches and *is* power-independent — that is the discriminator.
- **A round trip that scales with distance only proves the Arduino toggled STEP.**
  `stepMotor()` bit-bangs the pin and counts loop iterations; there is no
  encoder, no current sense, no feedback of any kind.
- **`offline: true` on an instrument does not mean "not attached."** It stubs the
  instrument into a simulator that agrees with itself while the gantry keeps
  moving for real. That is how a capper came to press onto six still-capped vials.
- **`validate_setup` asks whether a coordinate is reachable, never whether it is
  the right one.** A tip-rack anchor 52 mm out passes it.
