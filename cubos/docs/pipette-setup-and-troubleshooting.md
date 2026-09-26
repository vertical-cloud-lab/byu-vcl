# The Opentrons P20 on the CubXL — setup and troubleshooting

Status as of **2026-09-26**. This is the map; the detail is in
[`opentrons-pipette-wiring.md`](./opentrons-pipette-wiring.md), which is the
durable technical record and is where new findings go.

The pipette is an **Opentrons P20 GEN2** single-channel, mounted on the CubXL
gantry beside the capper/decapper and driven by an **Adafruit 6121 TMC2209**
breakout off an **Arduino Uno R3**. CubOS speaks to that Arduino over
`/dev/ttyACM0`, which it shares with the capper's electromagnet and line-break
sensor. The gantry is a separate stepper system on `/dev/ttyUSB0` — see §15 of
the wiring doc, because conflating the two has cost real time.

## Where it stands

**The motion half works. The plunger has never physically turned — the cable
that caused it has been removed, and the driver board it damaged is now
condemned. Replace the Adafruit 6121.**

Every software and geometry problem between a protocol and the plunger is
solved and verified on hardware:

| | |
|---|---|
| tipped-pipette travel | **works** — the hover clamp lets `safe_z 115` coexist with a 35 mm tip on a machine whose Z tops out at 124 |
| `pick_up_tip` XY | **works** — commands the measured jog point to the millimetre, three runs running |
| `aspirate` / `blowout` / `drop_tip` | **execute**, reach the right planes, and the firmware emits the steps |
| volume conversion | **single conversion** — `mm_to_ul: 1.0` in CubOS, the calibration constant in the firmware |
| plunger retraction | **un-gated** — 14 mm of retraction ran at the commanded rate on the direct wiring, 2026-09-24 |
| firmware plunger planes | ✅ **P20 GEN2 image flashed and verified 2026-09-24** — prime 28.0 / blowout 32.5 / drop_tip 46.5, `UL_TO_MM` 1.34 |
| passive-instrument sweep | **0 interferences**, nominal and tip-stuck |
| the motor windings | ✅ **4.3 Ω / 3.7 Ω on direct wiring — healthy** |
| phase-to-phase isolation | ✅ **MΩ on direct wiring — the short left with the ribbon** |
| VREF at the trimmer wiper | ✅ **0.586 V ≈ 1.09 A peak — matched to `RUN_CURRENT_PERCENT 20`, so it no longer matters which one is in force** |
| the ribbon harness | 🔴 **condemned — it carried both the open coil path and the short** |
| **the Adafruit 6121 driver board** | 🔴 **condemned 2026-09-26 — `DIAG` survives a power-on reset *and* an `ENN` reset with a clean load. Replace it** |
| the TMC2209 UART readback | 🔴 **`comm = 0` with the read fix now live — the RX-side bridge resistor alone; move it during the swap** |
| the first bench move | ❓ **no movement seen — expected with the output stage off; re-run on the replacement** |
| the Pi | ✅ **back on the tailnet 2026-09-25 23:37 UTC, 5.13 V input, no under-voltage since boot** — ⚠️ keep its lead out of the gantry's reach (§21.7) |

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
  limit-switch gate            OPEN     retractions execute on the DIRECT wiring too
  VM at the screw terminal     13 V     measured 2026-09-17
  EN at the driver pin         0 V      candidate B ELIMINATED, 2026-09-21
  coil grouping in terminals   CORRECT  1A+1B = one winding, 2A+2B = the other
  serial link to the Pi        HEALTHY  10/10 clean round-trips
  motor windings               HEALTHY  4.3 / 3.7 Ohm once the ribbon is bypassed
  phase-to-phase isolation     HEALTHY  1A-2A and 1B-2B are megohms on direct wire
  the ribbon harness           FAULTY   it carried BOTH faults, and both left with it
  firmware aspirate planes     FIXED    GEN2 image flashed and verified 2026-09-24
  ------------------------------------- the whole coil side is now ruled out
  VREF at the trimmer wiper    0.586 V  the chip's 5 V regulator is alive
  DIAG pull-up                 NONE     0.5 MOhm; the schematic has nothing on DIAG
  outputs to GND / VM+         NO SHORT ~1.5 V in diode mode, all four alike
  header solder bridges        NONE
  ------------------------------------- everything outside the chip is ruled out
  ENN reset                    DONE     DIAG still high afterwards (4.2 V)
  power-on reset (2026-09-24)  DONE     DIAG still high afterwards (5 V)
  Adafruit 6121 / TMC2209      CONDEMNED  re-detects a fault on every enable
  UART readback              comm=0   read fix LIVE; only the RX-side bridge
                                      resistor is left. Move it during the swap.
```

On **2026-09-26** the last three outside causes came back clean — no pull-up on
`DIAG`, no output shorted to either rail, no solder bridges — and `DIAG` survived
the `ENN` reset, having already survived a power-on reset on 2026-09-24. The
TMC2209's short detection explains how that happens with nothing wrong outside:
it compares the voltage across each output MOSFET while it is switched on, so a
MOSFET or gate driver that no longer switches properly is, to the chip, a short
— re-detected about a microsecond after every enable, whatever is connected. A
meter from outside finds shorted MOSFETs, not weak ones. **The board is
condemned.** See §22 of the wiring doc, which pulls the TMC2209 datasheet and the
6121 schematic for the first time.

On **2026-09-23** Ben bypassed the 10-pin ribbon and its FC-10P and wired the
pipette straight to the driver's screw terminals. `1A`–`1B` read **4.3 Ω** and
`2A`–`2B` **3.7 Ω** — real stepper windings, and the first ever measured on this
machine. Every earlier reading of the same two pairs was kΩ to MΩ. Nothing about
the motor changed; only the harness left the path. **The motor is healthy and
the coil fault was in the ribbon, its crimps, the FC-10P, or the machine-end
solder junction.** See §18 of the wiring doc.

On **2026-09-24** the two cross pairs came back at **megohms** on the same
direct wiring. §17.2's `1A`–`2A` = 0 Ω was the other half of the fault, and it
has gone with the ribbon too. Two windings, correct resistance, properly
isolated — **the coil-side diagnosis is closed.** What that also does is make a
**damaged output stage the leading explanation for `DIAG`**: the ribbon
presented a phase-to-phase short at the driver's outputs, the pot had been at
full clockwise since 2026-09-17, and `EN` has been at 0 V, so the chip was
enabled and driving into that short across many sessions. That is a textbook way
to destroy a driver. See §19.

> ✅ **VREF is set: 0.586 V at the wiper (2026-09-26), ≈ 1.09 A peak.** Full
> clockwise on this board is ~1.5 A rms / 2.2 A peak — the trimmer is fed from
> `5VOUT` through 33 kΩ, so VREF tops out near 1.16 V, not the 2.5 V behind the
> "~3.3 A rms" quoted here until now (§22.5a). Still twice what a P20 GEN2 wants,
> so turning it down was right. Do not go below ~0.5 V: the datasheet calls that
> "not recommended" for current precision (§22.4).

### What to do next

> 🔴 **Changed 2026-09-26: replace the driver board.** The 2026-09-24 meter
> sequence is complete (§19.5 of the wiring doc, results in §22), and its last
> step's condition is met: `DIAG` still high after the `ENN` reset, with the coils
> connected and no rail short found — and it had already survived a power-on
> reset. Keep the old board, labelled; it is a known-bad reference.

> ✅ **The deck is intact.** The 2026-09-24 trio was cut when the gantry
> travelled far enough from the outlet to unplug the Pi; Ben E-stopped it above
> vial 1 with the capper **not yet engaged**, so no cap was captured and nothing
> was dropped (§21.8). The position reference is still gone — recover with `$H`,
> never `$X` + a jog — and re-check `$20` before the next protocol run.

> ⛔ **But the trio cannot run as committed.** A read-only check on 2026-09-26
> found the controller recalibrated since 2026-09-24 — `$130/$131/$132` now
> 410 / 281 / 125.003 against the committed 409 / 309 / 124 — and the camera shows
> the machine on a different bench. CubOS refuses at connect on the mismatch, and
> the deck's jog readings are in the old frame, so the deck needs **re-jogging,
> not converting**, before the gantry file is synced. See
> [`../results/pipette_test_20260926/`](../results/pipette_test_20260926/README.md).
> None of this touches the plunger work below, which needs no gantry motion.

> 🔴 **Keep the Pi's mains lead out of the gantry's reach.** Step 0 of every
> protocol drives to the far corner (409, 309), the extreme that pulled the plug
> on 2026-09-24. The Pi is back (2026-09-25 23:37 UTC, 5.13 V in, no
> under-voltage since boot), but whether the lead has been re-routed is not
> recorded. The durable fix is a supply of its own, ideally a small UPS (§21.7).

**Optional, before binning the old board** — neither changes the action (§22.7):

- **Holding torque.** Board powered, `EN` low, nothing commanded: gently push the
  plunger. Moves freely, as on 2026-09-17 ⇒ neither bridge is driving ⇒ bin it.
  Resists ⇒ say so before binning it.
- **Let the chip name its fault.** Do step 2 below first, then read `CMD 29`:
  `s2ga`/`s2gb`/`s2vsa`/`s2vsb`/`ot` name the failed bridge. It also proves the
  readback path on a board known to have flags, before the new board's "no
  flags" is trusted.

**Bringing up the replacement** (§22.8):

1. **Power off** — the 12 V *and* the Arduino's USB — whenever a motor or supply
   wire is touched. Same header wiring; same terminal colours (`1A` red, `1B`
   blue, `2A` green, `2B` black). Fit the 1515 heat sink now.
2. **Move the bridge resistor to the TX side**: `A1 —R— NODE`, with `A0` and
   `PDN_UART` directly on `NODE`. 1 kΩ is the library's recommendation; the
   10 kΩ already fitted works at 9600 baud. The GEN2 firmware carries the read
   fix, so `CMD 29` then reads the new chip from its first power-up.
3. **Strain-relieve the four bare motor leads.** A lead pulling out of its
   terminal under current is the textbook way to kill a stepper driver.
4. **First power-up with `EN` jumpered to 5 V**, so no coil current flows
   whatever the new trimmer is set to. Bring the 12 V up by switching the supply
   on, not by pushing a live lead into the terminal — the datasheet wants `VS`
   slopes below 1 V/µs or the charge-pump capacitor can pass destructive
   currents.
5. **Set VREF to 0.55–0.59 V** at the new trimmer's wiper.
6. 🔑 **Go/no-go: `DIAG` ≈ 0 V with `EN` at 5 V, and still ≈ 0 V after `EN` goes
   low.** The old board never passed this. 🔴 If `DIAG` jumps high the moment
   `EN` goes low, **power off and stop** — something external is tripping the
   new chip, and re-enabling into it is how the first one probably died.
7. **Holding torque** with `EN` low and nothing commanded — it should now resist.
8. **First motion: 1 mm down and back.** From the Pi,
   [`../tools/pipette_driver_measure.py`](../tools/pipette_driver_measure.py)
   `--move`; or from any laptop's Arduino Serial Monitor at 115200 baud with
   Newline endings, `16,1,1592,400` then `16,0,1592,400` — no CubOS, no Pi, no
   gantry (§22.9). Then 10 mm against a ruler: standalone `MS1`/`MS2` give 1/8
   stepping where the firmware assumes 1/16, so if the UART writes are not
   landing, a commanded millimetre travels two.
9. **Watch which way `HOME` seeks.** Direct wiring may have reversed a pair, and
   `homePipette()` seeks with `DIR` LOW. If the tip ejector starts to engage,
   the direction is inverted — swap the two wires of one pair.
10. **Rebuild or repair the harness before the pipette goes back on the
   gantry.** The ribbon was also the flexible tether. Solid wire into screw
   terminals will not survive gantry motion, and a terminal pulled out mid-run
   recreates exactly the open circuit that cost the last three weeks.

**Retired:** the terminal-block swap that §16.3 led with (§17.1); §17.5's
localisation sequence, which the substitution answered first; the whole
2026-09-24 meter sequence, now complete (§22.1); "cut both rails together",
because `VCC_IO` does not power the chip's logic and a `VM` cycle is a full reset
(§22.5c); `INDEX` during a driven leg, superseded by the verdict; and
reconnecting the limit switch, which reads clear on the direct wiring (§20.3).

### Queued behind the first real movement

- ✅ **The P20 GEN2 image is flashed and verified** (2026-09-24, §20.1), so
  `aspirate` descends to the P20's 28.0 rather than the P300's 36.0. Whether its
  `RUN_CURRENT_PERCENT 20` or the trimmer sets the coil current depends on
  whether the boot-time UART writes reach a powered chip; with VREF at 0.586 V
  the two agree, so it does not matter (§22.5b).
- **Check the first successful move against a ruler**, as in step 8 above. The
  firmware already contradicts itself about this: `STEPS_PER_MM 1592.0` against
  a homing back-off commented `796; // this is equal to 1mm`.
- **`UL_TO_MM` 1.34 is Opentrons' nominal figure**, not a calibration of this
  unit — a gravimetric check once liquid actually moves.

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
- **A test whose negative result is already predicted is not a test.** The first
  bench move was run with `DIAG` asserted — which disables the output bridges by
  definition — *and* with the VREF pot freshly turned down to an unrecorded
  value. It showed nothing, as it had to, and the risk was that "no movement"
  got read as "the board is dead" (§21). Before spending hardware time, ask what
  each outcome of the test would rule out; if one of them rules out nothing, fix
  the ordering first.
- **The Pi is the host, so losing its power loses the evidence.** The run log,
  the plunger trace and the camera frames are all written on the Pi, and the
  closing `home` and `CMD_EMAG_OFF` are commands *from* it. A gantry that can
  reach the Pi's mains lead is therefore a data-integrity and machine-state
  problem, not just an interrupted run (§21.7).
- **A clean short test from outside does not clear a driver.** The TMC2209
  detects a short by the voltage across a MOSFET it has switched on, so a MOSFET
  or gate driver that no longer switches properly *is* a short as far as the chip
  is concerned — re-detected a microsecond after every enable, whatever is
  connected. A meter finds shorted MOSFETs, not weak ones (§22.2).
- **Read the schematic and the datasheet before quoting a limit.** "~3.3 A rms
  full scale" was repeated for a week on the assumption that the trimmer could
  reach 2.5 V; the 6121 feeds it through 33 kΩ and it tops out near 1.16 V
  (§22.5a). Both documents were a download away the whole time.
