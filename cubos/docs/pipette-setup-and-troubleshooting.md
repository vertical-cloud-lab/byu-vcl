# The Opentrons P20 on the CubXL — setup and troubleshooting

Status as of **2026-10-07**. This is the map; the detail is in
[`opentrons-pipette-wiring.md`](./opentrons-pipette-wiring.md), which is the
durable technical record and is where new findings go.

The pipette is an **Opentrons P20 GEN2** single-channel, mounted on the CubXL
gantry beside the capper/decapper and driven by an **Adafruit 6121 TMC2209**
breakout off an **Arduino Uno R3**. CubOS speaks to that Arduino over
`/dev/ttyACM0`, which it shares with the capper's electromagnet and line-break
sensor. The gantry is a separate stepper system on `/dev/ttyUSB0` — see §15 of
the wiring doc, because conflating the two has cost real time.

## Where it stands

> ✅ **2026-10-07, later: fix B is flashed, and `pipette_test` ran 12/12 on the TMC2209 with
> every wire on.** The wire pulled for the earlier entry was EN from A4, not UART. With EN back
> on, the 10-01 image didn't move the plunger in two probes. The firmware was rebuilt with
> `disableStealthChop()` in `setupMotor()`, which changes one instruction (GCONF
> `en_SpreadCycle`), and flashed. `tmc2209_probe.py` then passed, and `cubxl_run.py --no-tic`
> ran 12/12 with a post-run `HOME` of +0.04 mm. Its plunger timings match the Tic's 10-06 run.
> The chip now runs on the firmware's regulated current, 0.72 A rms moving and 0.21 A rms at
> rest on a 6121 (Ben has confirmed the new board is one), so everything can stay plugged in at
> idle. Ben found the board at room temperature at idle after the run, the sign that the
> firmware's settings are in force rather than the trimmer's. Run with `--no-tic` while the
> TMC2209 is on. Record:
> [`tmc2209_spreadcycle_20261007`](../results/tmc2209_spreadcycle_20261007/README.md), wiring
> doc §26, firmware in [`../firmware/README.md`](../firmware/README.md).
>
> ✅ **2026-10-07: with the UART wire off, the TMC2209 moves the plunger.** *(Corrected: the
> wire that was off was EN, not UART. See the entry above.)* The board was
> cold with the wire on pin 9 and turned warm with it off. `tmc2209_probe.py` then proved the
> direction (DIR LOW is up), passed the rate ladder up to the ~8,700 steps/s `MOVE_TO` rate,
> and homed, matching the Tic's 09-29 numbers. So the board is fine, and the firmware's UART
> writes were what stopped it (wiring doc §25). Next is `pipette_test` with the wire off and
> `cubxl_run.py --no-tic`. Long term, either leave the wire off with pin 9 tied to a level, or
> flash `disableStealthChop()` and put the wire back. Record:
> [`tmc2209_probe_20261007`](../results/tmc2209_probe_20261007/README.md).
>
> 🔑 **2026-10-06: the board checks out, and the firmware may be what starves it.**
> Ben's meter readings on the TMC2209 were healthy: VM 12.4 V, VDD 5 V, VREF 0.586 V,
> coils 3.4 Ω, and DIAG 0 V once enabled. `tmc2209_probe.py` and the down-probe still saw
> no motion either way. The janelia library's `initialize()` switches off StealthChop's
> automatic current scaling, and `setupMotor()` never switches it back on. In that mode
> `IRUN 6` scales a fixed PWM amplitude, 36 × 7/32 of 256, instead of setting a regulated
> current. That works out to ≈0.1 A in the coils against the 1 A intended (wiring doc
> §24). Two tests are in
> [`tmc2209_probe_20261006`](../results/tmc2209_probe_20261006/README.md#next-two-ways-to-test-it):
> pull the UART wire (standalone mode), or flash `disableStealthChop()`.
>
> 🔴 **2026-10-05: the TMC2209 board was tried again, and it doesn't drive the
> plunger.** Ben swapped the Tic out for it. With the board plugged in, limit-switch
> probes sent 9 mm of moves in both directions, and none reached the switch. They
> started where the 10-02 run's last `HOME` left the plunger. Ben stood at the
> pipette for a 30 s buzz at 100 full steps/s and felt nothing. `CMD 29` read
> `comm = 0`. `pipette_test` was not run, and the pipette is going back on the Tic.
> The record and a checklist for another try are in
> [`tmc2209_probe_20261005`](../results/tmc2209_probe_20261005/README.md). If the
> TMC2209 goes back in, run its `tmc2209_probe.py` before any protocol, and give
> the runner `--no-tic`.
>
> ⚡ **2026-10-01: the trio runs in about 2 minutes, and there is a runner.** All
> three speed changes are in (CubOS status polling, F3000, fast `MOVE_TO`):
> 12/12 in 124 s against 238 s on 09-30, with no plunger steps lost (see
> [Speed](#speed)). Runs now go through one command,
> [`cubos/tools/cubxl_run.py`](../tools/cubxl_run.py), which checks, gates, runs
> and writes a one-screen `SUMMARY.md`; see [Running it](#running-it). The scale
> check below is still open.
>
> ✅ **2026-09-30: the pipette handles liquid.** Ben watched campaign 68 and
> reports that it aspirated (almost filling the tip below the foam filter),
> dispensed, and dropped the tip. That is the first end-to-end confirmation.
> Still open: the scale. Weigh one 20 µL dispense of water: about 20 mg means
> 796 steps/mm is right, about 10 mg means it is 1592. `UL_TO_MM 1.34` is also
> still Opentrons' nominal figure. The run took 4 minutes, and 73 s of that was
> the CubOS driver waiting on a serial timeout; see [Speed](#speed) below.
>
> 🔑 **2026-09-30 (b): the trio ran 12/12 on the Tic, and every plunger command
> executed.** `pick_up_tip`, `aspirate` (both legs, landing at 1.2 mm),
> `blowout` and both `drop_tip` legs all returned `OK` at their commanded
> rates, and a `HOME` after the run took 12.680 s against 12.687 s before it
> from the same position, so no steps were lost over ~160,000 in both
> directions. Not yet shown: liquid actually moving (needs eyes or a balance),
> and the 796 steps/mm scale (the ruler check). Before the run the GRBL
> controller was found **factory-reset** (`G54` zeroed, travel 400/300/100,
> soft limits off); the calibrated frame was restored from the 09-26 record.
> See [`pipette_test_20260930b`](../results/pipette_test_20260930b/README.md).
>
> **2026-09-30:** the Arduino now runs the same firmware with
> `STEPS_PER_MM 796` for the Tic's 1/8 step, so the warning below is resolved
> (796 cannot overshoot whichever scale is right; the ruler check is still
> open). The first trio with the Tic in circuit stopped in `decap vial_1` when
> all of the Pi's USB ports tripped over-current at once; see
> [`pipette_test_20260930`](../results/pipette_test_20260930/README.md).

**🔑 2026-09-29: the plunger moves.** A Pololu Tic T500 has replaced the condemned
Adafruit 6121. Driven through the Arduino, the plunger went up to the limit
switch, back down, and up to it again at every firmware rate, and the
firmware's `HOME` succeeded for the first time
([record](../results/pipette_switch_search_20260929/README.md)). ⚠️ **Don't
connect CubOS yet.** The firmware still has `STEPS_PER_MM 1592`, written for
1/16 step, and the Tic runs 1/8. So CubOS's connect-time `prime` would drive
about 56 mm, into the end of travel. Confirm 796/mm and flash it first
([Tic doc](./tic-t500-pipette-setup.md), steps 6–7).

*Until 2026-09-29 this read:* **The motion half works. The plunger has never
physically turned — the cable that caused it has been removed, and the driver
board it damaged is now condemned. Replace the Adafruit 6121.**

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
| **the plunger, on the Tic T500** | ✅ **moves both ways, 2026-09-29.** The limit switch opens after ~28.7 mm up, closes 2 mm down, and reopens after 2 mm at 200–2,500 microsteps/s. `HOME` works. Polarity correct. Tic left de-energized; `ticcmd --energize` before use |
| firmware `STEPS_PER_MM` | 🔴 **still 1592 (1/16 step) against the Tic's 1/8.** Confirm 796 by ruler or weight, then flash, before CubOS connects |
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

> 🔀 **2026-09-29: if the replacement is a Pololu Tic T500** rather than another
> 6121, see [`tic-t500-pipette-setup.md`](./tic-t500-pipette-setup.md). It has the
> wiring diagram, the three Tic settings, the one firmware constant that changes
> (`STEPS_PER_MM` 1592 → 796) and the bring-up order. **Bring-up step 1 is
> done:** STEP/DIR, 1/8 step and 990 mA are in the Tic's memory and read back
> ([record](../results/tic_t500_settings_20260929/README.md)). **Steps 3 and 5
> were run later the same day:** wired and on 12 V, energized with no errors,
> coil current tracking the setting, and moves sent both through the Arduino and
> from the Tic itself. Whether the plunger turned is still to be confirmed by
> eye ([record](../results/tic_t500_first_moves_20260929/README.md)).
> ✅ **Confirmed at 18:05–18:10 by the limit switch,** which is the one sensor on
> the plunger. UP opened it after about 28.7 mm. DOWN 2 mm closed it, and UP
> reopened it after the same 2 mm at 200, 400, 800, 1,600 and 2,500
> microsteps/s. The firmware's `HOME` succeeded in 1.36 s
> ([record](../results/pipette_switch_search_20260929/README.md)). **Next:** step 6
> (confirm 796 microsteps/mm, by ruler or weight), then step 7 (flash it), and only
> then CubOS.

> ✅ **The deck is intact.** The 2026-09-24 trio was cut when the gantry
> travelled far enough from the outlet to unplug the Pi; Ben E-stopped it above
> vial 1 with the capper **not yet engaged**, so no cap was captured and nothing
> was dropped (§21.8). The position reference is still gone — recover with `$H`,
> never `$X` + a jog — and re-check `$20` before the next protocol run.

> ⛔ **The trio still does not validate, for two new reasons.** Ben
> recalibrated on the new bench (2026-09-26) and re-jogged the deck.
>
> - The gantry file now matches the controller: 391 / 236.665 / 124, `$20=1`.
> - The tip rack is converted from his A1 reading.
>
> What still fails:
>
> - The pipette cannot reach vial_1 at y 0.665. It sits +13 mm in Y from the
>   capper, which puts vial_1 12.3 mm past the Y limit.
> - Step 5's `travel_z: 87` is above the new `z_max: 121`.
>
> Fixing both gives PASS, 12/12, and 0 interferences. The options are in
> [`../results/pipette_test_20260926b/`](../results/pipette_test_20260926b/README.md).
> None of this touches the plunger work below, which needs no gantry motion.

> 🔴 **Keep the Pi's mains lead out of the gantry's reach.** Step 0 of every
> protocol drives to the far corner (now 391, 236.665), the extreme that pulled the plug
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
  unit. It needs a gravimetric check, which is now possible: liquid moves as of
  2026-09-30.

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
| `../patches/grbl-prompt-status-polling.patch` | the status-polling half of Alex's CubOS PR #351, backported to `496819c`; removes the 2 s wait after every G-code (see [Speed](#speed)). **Not applied to the Pi** |
| [`../tools/`](../tools/) | `pipette_driver_measure.py`, `pipette_driver_probe.py`, `pipette_bench_check.py`, `run_with_plunger_trace.py` |
| `../results/pipette_*` | 17 sessions of run logs, plunger traces, G-code, camera frames and `$$` dumps |

## Running it

CubOS lives on `rpi-5-des4` at `~/CubOS`; its install and patch state are in
[`SOP/raspberry-pi-cubos-setup.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/SOP/raspberry-pi-cubos-setup.md),
which is on [#171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171) and not in this PR.

### With the runner (since 2026-10-01)

This branch is checked out on the Pi as a worktree at `~/byu-vcl-pipette`
(`~/byu-vcl` itself stays on #171's branch). One command does the whole routine
and writes one folder:

```bash
git -C ~/byu-vcl-pipette pull --ff-only          # run the committed configs
setsid nohup ~/CubOS/.venv/bin/python ~/byu-vcl-pipette/cubos/tools/cubxl_run.py \
    --name pipette_test_YYYYMMDD > /tmp/cubxl_run.out 2>&1 < /dev/null &
cat ~/cubxl_runs/pipette_test_YYYYMMDD/SUMMARY.md   # when done
```

Results go to `~/cubxl_runs/<name>/`, outside the checkout so the `pull` never
conflicts; copy the folder into `cubos/results/` to commit it.

[`cubos/tools/cubxl_run.py`](../tools/cubxl_run.py) defaults to the trio below.
In order, and any refusal before the run means nothing moved:

1. **checks**: commits and which `cubos/patches` are applied; ports present, not
   held open, and named identically where shared; protocol step 0 is `home`
   (opening the GRBL port resets it, so anything else would move against a lost
   position); `$$` against the gantry file, `G54 == -max_travel` (catches a
   factory reset), feed within `$110`–`$112`; the Arduino answers and nothing is
   on the magnet; the Tic's settings equal [`tic_p20.txt`](tic_p20.txt), then
   it is energized. Protocols with a `breakpoint` are refused, because the run
   is headless.
2. **gates**: `validate_setup`, `run_protocol --mock`, `passive_shadow` nominal and
   `--tip-stuck`.
3. **run**: `run_with_camera_and_plunger_trace.py`, with the Tic polled and the
   GRBL logs sliced to the run.
4. **post-run**: magnet off, cap sensor, plunger `STATUS`; with `--home-check`, a
   plunger `HOME` whose duration says whether any steps were lost; Tic
   de-energized.
5. **summary**: `SUMMARY.md` (one screen) and `summary.json`; `--baseline <dir>`
   adds a comparison.

`--checks-only` stops after stage 2 (about 25 s, no motion). `setsid nohup` is
only so an SSH drop can't take the run with it; the runner also ignores SIGHUP.
Exit status 0 = completed, 1 = ran and failed, 2 = refused, 3 = runner error.

### By hand

Run from a foreground SSH session if the protocol has a `breakpoint` — a headless
run logs *"Breakpoint skipped because stdin is not interactive"* and continues.

```bash
C=~/byu-vcl-pipette/cubos/configs; PY=~/CubOS/.venv/bin/python
G=$C/gantry/cub_xl_ben_pipette_capper.yaml
D=$C/deck/ben_6vials_tiprack.yaml
P=$C/protocol/vcl/pipette_test.yaml

$PY -m cubos.tools.validate_setup      $G $D $P      # nothing moves
$PY -m cubos.tools.run_protocol --mock $G $D $P
$PY ~/byu-vcl-pipette/cubos/tools/passive_shadow.py $G $D $P --tip-stuck
$PY ~/byu-vcl-pipette/cubos/tools/run_with_plunger_trace.py  $G $D $P   # the real run, timed
```

Four gates pass offline and none of them models the *other* instrument on the
head, which is what `passive_shadow.py` is for. Re-home before every run: the
GRBL board resets when the port opens and comes up in `Alarm`.

## Speed

Measured from campaign 68 (2026-09-30), the 12-step trio: **238 s** from gantry
connect to disconnect ([logs](../results/pipette_test_20260930b/README.md)).

| part | time | waiting, not moving |
|---|---|---|
| 47 gantry moves (`G01`, one axis each) | 127.5 s | ~58 s; the moves themselves need ~69 s at F2000 |
| 2 homing cycles | 38.2 s | ~11 s, after the opening `$H` |
| 8 plunger commands (incl. connect) | 45.7 s | none; `MOVE_TO` runs at ~2,400 steps/s |
| connect, cameras, capper dwell, disconnect | ~27 s | ~4 s (`G90` and `F3000` at connect) |

**Every gantry command took a multiple of ~2.06 s, including 1 mm moves.** In
CubOS `496819c`, `Mill.current_status()` reads the port *before* sending `?`.
GRBL sends nothing unprompted (`$10=0`), so that read waits out the serial
timeout: 2 s normally, 10 s during `home`. Alex's CubOS
[PR #351](https://github.com/Ursa-Laboratories/CubOS/pull/351) (draft, not
merged) sends `?` first. Its `current_status()` hunk and its six tests are
backported here as `../patches/grbl-prompt-status-polling.patch`. Offline on the
Pi's exact tree (`496819c` + the three applied patches), the six tests fail
without it and pass with it, and the whole core suite passes (2550, 0 failed). A
real-time fake GRBL reproduces the log: a 1.5 s move returns after 2.05 s today
and 1.55 s patched. Nothing has been tested on hardware yet, here or upstream.
The G-code and feed rates are unchanged.

The levers, per run, measured against this log:

| change | saves | notes |
|---|---|---|
| apply `grbl-prompt-status-polling.patch` | ~70 s | same G-code; only the waiting goes |
| delete `default_feed_rate_mm_min: 2000.0` (CubOS default 3000; GRBL allows 5000) | ~19 s, with or without the patch | each move still ramps down to a stop at its target |
| firmware `MOVEMENT_VELOCITY` 2500 → 10000, keeping moves into the ejector zone (target > `BLOWOUT_POSITION`) at 2500 | ~25 s | 10000 hits the firmware's 100 µs step-delay floor, ~8,700 steps/s. That is the rate `ASPIRATE` already runs at, because CubOS sends speed 0 and `aspirate()` passes it through. It is ~11 mm/s, about Opentrons' 7.56 µL/s P20 GEN2 default flow. Opentrons ejects tips at 15 mm/s |
| end the protocol parked instead of homed | ~15 s | the closing `home` is the move to the far corner that pulled the Pi's cable on 09-24 |
| coordinated XY diagonals (the other half of PR #351) | ~5–10 s | depends on upstream's routing stack; wait for it to merge |

The first three together take a run from about 4 minutes to about 2.

**Measured 2026-10-01, all three applied** (campaign 75,
[`../results/pipette_test_20261001/`](../results/pipette_test_20261001/SUMMARY.md)):
the same 12 steps, same configs otherwise, 12/12.

| | campaign 68 (09-30) | **campaign 75 (10-01)** | saved |
|---|---:|---:|---:|
| whole run | 238 s, connect to disconnect | **124 s**, process start to end | 114 s |
| 47 `G01` moves | 127.5 s | **55.2 s** (median 0.91 s; 1 mm moves now 0.06 s) | 72 s |
| 2 `$H` cycles | 38.2 s | **28.6 s** (7.9 + 20.7) | 10 s |
| 8 plunger commands | 45.7 s | **20.3 s** | 25 s |

The prediction above was 70 + 19 + 25 = 114 s; the measurement is 114 s. The
ejector push (`MOVE_TO 46.5`) took 4.65 s on both days, as intended. **No
plunger steps were lost at the faster rate:** a plunger `HOME` after the run,
from the firmware's 28.0 mm, took 12.677 s against 12.680 s on 09-30, i.e.
27.99 mm (−0.01 mm). The Tic logged no errors (VIN 9.0–11.3 V), and the kernel
logged no USB events.

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
