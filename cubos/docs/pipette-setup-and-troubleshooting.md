# The Opentrons P20 on the CubXL — setup and troubleshooting

Status as of **2026-09-21**. This is the map; the detail is in
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
  VM at the screw terminal     13 V     measured by Ben, 2026-09-17
  serial link to the Pi        HEALTHY  10/10 clean round-trips
  ------------------------------------- everything above is ruled out
  EN at the driver pin         ?        candidate B — output stage held off
  TMC2209 chip / regulator     ?        candidate C — dead
  coil path to the windings    ?        candidate A — crimp, screw, or ribbon
```

### The next four measurements

They need hands and a meter at the machine; none can be done remotely.
[`../tools/pipette_driver_measure.py`](../tools/pipette_driver_measure.py) opens a
bounded, direction-labelled stepping window (6 mm out, 6 mm back) so the first
three can be probed while the plunger is actually being driven. It refuses to
open the window if the limit switch reads asserted.

1. **`EN` at the driver's pin** — ~0 V expected. ~5 V means the output stage is off.
2. **`DIAG`** — ~0 V expected. High means the chip is reporting a fault.
3. **`INDEX` during a driven leg** — must change. This is the split: changing
   means the chip is alive and counting, so the fault is downstream in the coil
   path or current is set to zero; dead flat means the chip is not processing STEP.
4. **Coil resistance at the four screw terminals**, ribbon attached, power off:
   `1A`–`1B` and `2A`–`2B` a few to a few tens of ohms, `1A`–`2A` open. This tests
   the whole path including crimps and screw clamping.

`DIAG` and `INDEX` are the reason this no longer depends on the UART readback
working — they are pins, not registers.

### Two things queued behind the first real movement

- 🔴 **The board is running the 2026-09-15 image, not the P20 GEN2 one.** Proven
  by `avrdude -U flash:v:` against all three candidates. CubOS carries the
  Opentrons planes (prime 28.0 / blowout 32.5 / drop_tip 46.5) while the firmware
  still carries the P300-derived 36.0 / 44.0 / 55.0 and `UL_TO_MM 1.8`. `MOVE_TO`
  is absolute so `blowout` and `drop_tip` land where CubOS asks; **`aspirate` does
  not**, because it is computed inside the firmware. Flashing
  [`../firmware/panda_vcl_p20gen2_20260917.hex`](../firmware/panda_vcl_p20gen2_20260917.hex)
  closes that, and drops run current from ~2.3 A to ~1.02 A peak — Opentrons'
  own `plungerCurrent` — which matters for a motor rated 500 mA peak.
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
