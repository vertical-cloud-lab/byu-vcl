# The Opentrons P20 on the CubXL — setup and troubleshooting

Status as of **2026-09-23**. This is the map; the detail is in
[`opentrons-pipette-wiring.md`](./opentrons-pipette-wiring.md), which is the
durable technical record and is where new findings go.

The pipette is an **Opentrons P20 GEN2** single-channel, mounted on the CubXL
gantry beside the capper/decapper and driven by an **Adafruit 6121 TMC2209**
breakout off an **Arduino Uno R3**. CubOS speaks to that Arduino over
`/dev/ttyACM0`, which it shares with the capper's electromagnet and line-break
sensor. The gantry is a separate stepper system on `/dev/ttyUSB0` — see §15 of
the wiring doc, because conflating the two has cost real time.

## Where it stands

**The motion half works. The plunger has never physically turned — but as of
2026-09-23 the reason is known, and it is a cable.**

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
| the motor windings | ✅ **4.3 Ω / 3.7 Ω on direct wiring — healthy** |
| the ribbon harness | 🔴 **condemned — it carried the open coil path** |

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
  limit-switch gate            OPEN     retractions execute (via the ribbon)
  VM at the screw terminal     13 V     measured 2026-09-17
  EN at the driver pin         0 V      candidate B ELIMINATED, 2026-09-21
  coil grouping in terminals   CORRECT  1A+1B = one winding, 2A+2B = the other
  serial link to the Pi        HEALTHY  10/10 clean round-trips
  motor windings               HEALTHY  4.3 / 3.7 Ohm once the ribbon is bypassed
  ------------------------------------- everything above is ruled out
  the ribbon harness           FAULTY   it is the only thing that changed
  1A - 2A on direct wiring      ?       was 0 Ohm through the ribbon; re-measure
  TMC2209 DIAG                  ?       5 V, but the latch may be stale
  VREF pot                     MAXIMUM  dangerous for the first time — real load
```

On **2026-09-23** Ben bypassed the 10-pin ribbon and its FC-10P and wired the
pipette straight to the driver's screw terminals. `1A`–`1B` read **4.3 Ω** and
`2A`–`2B` **3.7 Ω** — real stepper windings, and the first ever measured on this
machine. Every earlier reading of the same two pairs was kΩ to MΩ. Nothing about
the motor changed; only the harness left the path. **The motor is healthy and
the coil fault was in the ribbon, its crimps, the FC-10P, or the machine-end
solder junction.** See §18 of the wiring doc.

> 🔴 **Turn the VREF pot down before the driver is powered up again.** Until now
> the load was open or shorted, so the pot could not do damage. With real ~4 Ω
> windings attached the chopper can finally deliver what it is asking for —
> ~3.3 A rms full scale into a motor Opentrons runs at 1.0 A peak.

### What to do next, cheapest first

The order below is a **safety** order. Steps 1–3 come before power for a reason.

1. **Re-measure the cross pairs on the direct wiring, power off** — `1A`–`2A`
   and `1B`–`2B` must both read **open**. They were 0 Ω through the ribbon
   (§17.2), which is what latched `DIAG`. Still 0 Ω with the ribbon gone ⇒ the
   short is on the driver board itself, and it is then the only remaining
   suspect. Ten seconds, and it decides that.
2. **Reconnect the limit switch** — pins **6** and **7** rode the same ribbon.
   Left unconnected, D9 idles HIGH through its pull-up, the firmware reads the
   switch as *asserted*, every retraction is refused in ~0.107 s and `HOME` fake-
   succeeds in ~0.52 s. That is the pre-2026-09-18 signature and it would look
   like a regression. Check with
   [`../tools/pipette_driver_probe.py`](../tools/pipette_driver_probe.py)
   `--switch`; `pipette_driver_measure.py` also refuses to run while it reads
   asserted, so the refusal is itself the answer.
3. 🔴 **Turn the VREF pot well down.** Target ≈ 0.55 V at the wiper for ~1.0 A
   peak; wind it below that for a first re-test and creep up. Fit the 1515 heat
   sink. The pot is still the only thing setting current — `RUN_CURRENT_PERCENT`
   does not apply until UART works (§16.7).
4. **Power-cycle the 12 V, then read `DIAG`.** The short-circuit protection
   *latches*, and clearing it needs either a UART write (unavailable) or `VM`
   removed and restored. A `DIAG` read without the power cycle may be reporting
   a latch set days ago. ≈ 0 V ⇒ the chip survived. Still 5 V after a clean
   power cycle into a good load ⇒ replace the board.
5. 🔑 **Run a bounded bench move** —
   [`../tools/pipette_driver_measure.py`](../tools/pipette_driver_measure.py)
   `--move`, 6 mm out and 6 mm back, no gantry motion. Watch for the shaft
   turning, holding torque at rest, the yellow `S` LED changing, and `INDEX`
   fluctuating mid-scale. **Measure the 6 mm with a ruler** — `setMicrostepsPerStep(16)`
   has never landed, so MS1/MS2 decide at 1/8 and a commanded millimetre may
   travel two.
6. **Watch which way `HOME` seeks.** Direct wiring may have reversed a pair, and
   `homePipette()` seeks with `DIR` LOW. If the tip ejector starts to engage,
   the direction is inverted — swap the two wires of one pair.
7. **Rebuild or repair the harness before the pipette goes back on the gantry.**
   The ribbon was also the flexible tether. Solid wire into screw terminals will
   not survive gantry motion, and a terminal pulled out mid-run recreates exactly
   the open circuit that cost the last three weeks.

**Retired:** the terminal-block swap that §16.3 led with (§17.1), and the
localisation sequence of §17.5 — the substitution answered it first.

### Two things queued behind the first real movement

- 🔴 **Flash the P20 GEN2 image before any `aspirate` — this is now blocking,
  not queued.** The board runs the 2026-09-15 image, proven by
  `avrdude -U flash:v:` against all three candidates. `MOVE_TO` is absolute, so
  `blowout` and `drop_tip` land where CubOS asks; **`aspirate` is computed inside
  the firmware** and drives down to `PRIME_POSITION` first. The running image
  carries the P300-derived **36.0**; a P20 GEN2's bottom is **28.0**. That cost
  nothing while the plunger was silent — with a turning motor it drives the
  plunger 8 mm past its mechanical bottom on every call. Flashing
  [`../firmware/panda_vcl_p20gen2_20260917.hex`](../firmware/panda_vcl_p20gen2_20260917.hex)
  closes it and carries `tmc2209-softwareserial-read.patch`, without which
  `DRV_STATUS` — and with it the specific cause behind `DIAG` — cannot be read at
  all. ⚠️ It does **not** lower the run current until UART works; only the pot
  does (§16.7).
- **Check the first successful move against a ruler**, as in step 5 above. The
  firmware already contradicts itself about this: `STEPS_PER_MM 1592.0` against
  a homing back-off commented `796; // this is equal to 1mm`.

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
