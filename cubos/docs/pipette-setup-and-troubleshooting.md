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
  coil grouping in terminals   CORRECT  1A+1B = one winding, 2A+2B = the other
  serial link to the Pi        HEALTHY  10/10 clean round-trips
  ------------------------------------- everything above is ruled out
  coil path to the windings    OPEN     both pairs read kOhm-MOhm where a
                                        winding reads ohms
  1A - 2A                      0 Ohm    DEAD SHORT between the two bridges
  TMC2209 DIAG                 5 V      asserted — and the short explains it
  motor windings at the header  ?       the measurement that decides whether
                                        the motor itself is any good
```

As of 2026-09-22 the two symptoms collapse into **one mechanism**: `1A`–`2A`
measures 0 Ω, so the driver's two bridge outputs are shorted together, and that
is one of the exact conditions that latches `DIAG` high and turns the output
stage off. It is also how such an output stage is destroyed — the VREF pot has
been at maximum (~3.3 A rms full scale) and chopping into that short for every
session since. See §17 of the wiring doc.

> 🔴 **Do not power the driver again until the short is cleared and the pot is
> turned down.** A bridge-to-bridge short at a maxed current setting will take a
> brand new replacement board out within seconds.

### What to do next, cheapest first

The cross-pair measurements landed on 2026-09-22 and are worked through in §17
of the wiring doc. The order below is a **safety** order, not just a convenience
one — step 4 before step 1 destroys a replacement driver.

0. **Sanity-check the meter** — probes together should read the leads' own
   resistance, probes apart open. Five seconds, and it rules out a stuck range
   or continuity mode behind the flat `0`.
1. 🔑 **Find and clear the `1A`–`2A` short, power off throughout.** In order:
   **(a)** loosen only red and green, lift them clear of the block, re-measure
   red–green — clears ⇒ a stray strand or over-stripped insulation at the
   terminal; **(b)** unplug the FC-10P at the pipette and re-measure at the
   harness end — still 0 Ω ⇒ the short is in the ribbon, the crimps, the
   connector body, or the machine-end solder junction (§8.7's standing suspect);
   **(c)** clears ⇒ it is at the header or inside the motor.
   **Reseat the FC-10P before condemning anything** — the limit switch on pins
   6/7 works and sits in the rows *furthest* from the tip, while all four coil
   conductors sit in the two rows nearest it, so a lift or skew at the tip end
   fits every reading.
2. 🔑 **Measure the windings at the pipette's own 10-pin header, FC-10P off** —
   the single most valuable measurement remaining, because it removes every
   crimp, the ribbon and the connector and tests the motor alone. Coil A =
   pins **3–4**, coil B = pins **1–2**, each a few to a few tens of ohms;
   pins **1–3** open. Both in range ⇒ the motor is healthy and the whole fault
   is in the harness, which is what the evidence currently favours.
3. 🔴 **Turn the VREF pot well down before the driver is powered again.** Target
   ≈ 0.55 V at the wiper for ~1.0 A peak; wind it below that for a first
   re-test and creep up. Fit the 1515 heat sink.
4. **Then power up and re-check `DIAG`.** Clear, with a real load and sane
   current ⇒ the chip survived. Still 5 V ⇒ replace the board. This cannot be
   answered before step 1.
5. **`VREF` at the trimmer wiper**, once the pot has been set — healthy ⇒ the
   internal regulator is fine; ≈ 0 V ⇒ the chip is dead.
6. **`INDEX` during a driven leg.** The 0 V reading is not yet usable — it is
   not recorded whether steps were being consumed at the time.
   [`../tools/pipette_driver_measure.py`](../tools/pipette_driver_measure.py)
   opens a bounded, direction-labelled window for exactly this. It has dropped
   in importance now that §17.3 has a mechanism for `DIAG`.

**Retired:** the terminal-block swap that §16.3 led with. Ben's wire-to-terminal
map puts both ends of coil A in `1A`+`1B` and both ends of coil B in `2A`+`2B` —
correctly grouped, so there is no two-wire fix (§17.1).

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
