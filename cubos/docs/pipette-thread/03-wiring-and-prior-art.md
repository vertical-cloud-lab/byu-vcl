# The wiring hunt: the Cubware pin shift, the raw-step probe, and the science-jubilee prior art

*2026-09-08 → 2026-09-09 — 7 comments, migrated verbatim from [PR #171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171).*

Every comment below is reproduced exactly as posted, with its author and a link back to the original. `@`-mentions carry a zero-width space so that re-reading this file cannot notify anyone or re-trigger CI.

---

## @benwhitney5463 — 2026-09-08 18:30:29 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5589942249)

@claude, the pipette still isn't actuating anything, and I am wondering if it is a hardware or a software issue, or maybe it's both. The Arduino pins are correct now, but I am worried the wiring layout of the 10 pins going to the pipette is incorrect. Your worries that Pin6 isn't connected to ground are wrong. The diagram does have pin6 to ground, and I have it connected there physically. Is there another source from URSA labs detailing the connecting between the stepper motor, arduino and pipette?

---

## @claude[bot] — 2026-09-08 18:30:46 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5589945967)

**Claude finished @benwhitney5463's task in 15m 2s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/34263447945)

---
### Both — and the software half is new: correcting the UART pin opened a path that leaves the driver switched **off**

- [x] Re-read the Cubware diagram — pin 6 noted, you're right
- [x] Find the other Ursa source (there is one, and it points somewhere better)
- [x] Verify the 10-pin layout against three independent sources
- [x] Re-read the PANDA firmware + the pinned TMC2209 library
- [x] Try to measure on the Pi — **nothing is plugged into it, see the end**
- [x] Commit the corrected wiring doc ([`a0ccbb7`](https://github.com/vertical-cloud-lab/byu-vcl/commit/a0ccbb7))

Pin 6 → GND is on the diagram and you have it wired — corrected in the doc, dropping it. Nothing was run and nothing on the machine was touched.

---

### 1. Yes — there's another source, and it's the one that actually answers your question

Ursa has exactly **one** pipette wiring page: [`Cubware/documentation/opentrons-pipette-setup.md`](https://github.com/Ursa-Laboratories/Cubware/blob/main/documentation/opentrons-pipette-setup.md) + `images/PipetteControl.png`. (`images/ArduinoCircuitDiagram_v3.png` sitting next to it is the **capper/lights** circuit from the decapper build guide — not the pipette. Nothing in CubOS, PANDA-CUB, Zoo or BU-Configs documents this wiring either; I checked all of them.)

But that page delegates: *"The legacy PANDA-BEAR wiring docs point to the external BU-KABlab/PANDA_Arduino repository for firmware source, pin assignments, and installation instructions."* And `PANDA_Arduino` vendors a copy of the **science-jubilee OT2 pipette tool doc** at [`src/pipette_tool.md`](https://github.com/BU-KABlab/PANDA_Arduino/blob/main/src/pipette_tool.md) — that project is the upstream of this whole harness, and it has two things Ursa doesn't:

- 🔑 [**`tool_library/OT2_pipette/assembly_docs/OT2_Wiring_Diagram.pdf`**](https://github.com/machineagency/science-jubilee/blob/main/tool_library/OT2_pipette/assembly_docs/OT2_Wiring_Diagram.pdf) — a **photograph of the pipette's own 10-pin header** with a coloured dot on each populated hole. This is the only source anywhere that says which physical hole is pin 1.
- [`_static/ribbon_to_hookup_wiring.png`](https://github.com/machineagency/science-jubilee/blob/main/docs/building/_static/ribbon_to_hookup_wiring.png) — the ribbon conductor numbering (conductor 1 = the red-striped edge).

### 2. Your 10-pin layout is right — three sources agree, and the machine's own history rules out a flip

| | Cubware diagram | science-jubilee ribbon table | the photo |
|---|---|---|---|
| coil A | 3 → `1B`, 4 → `1A` | Red (3), Blue (4) | one row, left+right |
| coil B | 1 → `2B`, 2 → `2A` | Green (1), Black (2) | the row below, left+right |
| limit switch | 7 signal, 6 GND | Red (7), Black (6) | one hole in each of two adjacent rows |
| unused | 5, 8, 9, 10 | 5, 8, 9, 10 | top row empty |

Three checks off the photo:

- **The top row (9, 10) is empty and the motor is on the bottom two rows.** If your populated rows are at the other end, the FC-10P is crimped 180° out and every pin maps `n → 11 − n` — all four coil wires land on unused pins 7–10, which is a silent motor with no buzzing.
- **Each coil is a left–right pair within one row.** Blue+Red together, Black+Green together.
- **The limit switch is 7 and 6 — *diagonal*, one hole in each of two rows.** Wiring it to 7+8 or 5+6 (same row) is the easy mistake.

**But the 180° case is already excluded on your machine.** Under that rotation the limit-switch pair lands on pin 4 (a motor coil) and pin 5 (no connect), so D9 could never read a closed loop — and D9 has read LOW in three of your five wiring passes. **Don't rewire the 10-pin end.** If you want it confirmed with a meter, ribbon off the driver terminals and everything powered down: blue–red and black–green should each read a few to a few tens of ohms, blue–black should read open (the two coils are isolated). Both pairs open ⇒ crimps, not pinout.

One more thing your symptom rules out: coils miswired *across* pairs makes a stepper buzz and vibrate without turning. **No buzzing at all means no coil current** — a different failure from a mis-paired coil.

---

### 3. 🔴 The software half: `TMC2209::initialize()` disables the driver, and nothing checks that it got re-enabled

This is what changed when you moved UART from A0 to A1, and it's the first thing I'd try because it costs nothing.

`setupPipette()` → `setupMotor()` → `stepperDriver.setup(softSerial)` → [`TMC2209::initialize()`](https://github.com/janelia-arduino/TMC2209/blob/main/src/TMC2209/TMC2209.cpp):

```cpp
setOperationModeToSerial(serial_address);   // i_scale_analog = 0  <- VREF POT OUT OF CIRCUIT
setRegistersToDefaults();
clearDriveError();
minimizeMotorCurrent();                     // IRUN / IHOLD -> minimum
disable();                                  // CHOPCONF.toff = 0 -> OUTPUT STAGE OFF
```

`setupMotor()` then calls `setRunCurrent(50)`, `setMicrostepsPerStep(16)`, `enableStealthChop()`, `enableCoolStep()`, `enable()` to undo those last two lines.

**Every one of those is a UART write, and the link is write-only.** `SoftwareSerial softSerial(RX_PIN, TX_PIN)` is `(A0, A1)`, and `Pipette.h` says of A0: *"SoftwareSerial RX pin (not connected but required)"*. The TMC2209's UART is single-wire half-duplex, so with only TX attached the Arduino can never read the driver back — and `setupMotor()` never calls `isSetupAndCommunicating()`. **Nothing anywhere verifies that a single register write landed.**

| UART wire on | what the driver actually does |
|---|---|
| **A0** (the diagram's pin — the RX pin, never transmitted on) | nothing is ever sent. Chip stays in **standalone mode**: VREF pot sets current, MS1/MS2 straps set 1/8 microstepping, `toff` at its power-on default of 3 → **enabled** |
| **A1** (correct) | first thing that lands is `i_scale_analog = 0`, **taking your current pot out of the circuit**, then `minimizeMotorCurrent()` + `disable()`. If any later write is dropped or garbled, the driver sits at **minimum current with its output stage off** — silent, no holding torque — while the Arduino happily bit-bangs STEP into it |

That second row is exactly your symptom, and it **was not reachable before you fixed the pin**.

#### 🔧 The 30-second bisect: pull the UART wire off A1 and try a move

Nothing else changes. With the wire off, the chip never enters serial mode and runs on its power-on defaults with the pot back in charge.

- **Plunger moves** → the fault is the UART configuration path. (Distances will come out 2× — standalone MS1/MS2 default to 1/8, not the 1/16 `STEPS_PER_MM 1592` assumes. The firmware disagrees with itself about this already: the homing back-off says `int backOffSteps = 796; // this is equal to 1mm`, exactly half.)
- **Still silent** → it's power, current, or the coil circuit → §4.

Turn the VREF pot up before running it either way. If you'd rather instrument than unplug: tie A0 to the same PDN_UART line through a 1 kΩ resistor — that's how the janelia library's single-wire mode is meant to be wired — and then `isSetupAndCommunicating()` becomes meaningful.

### 4. The hardware side, in order, for "no buzzing" specifically

1. **Motor supply on the driver's `+`/`−` screw terminals.** The Arduino's 5 V on `VDD` is *logic only*. With no motor voltage the board accepts STEP/DIR and acks everything with zero coil current and total silence — indistinguishable at the serial port from a healthy run. Measure at the terminals, not at the brick. (And the diagram's *"120V/2A Power Supply"* is a typo: the Adafruit 6121 takes **5–29 VDC** there.)
2. **EN actually at 0 V at the driver pin** while the firmware is running. Adafruit's pinout says "pull high to disable"; the firmware drives A4 LOW in `setupPipette()`. Measure at the driver, not the Arduino header.
3. **The VREF pot**, but only for the §3 bisect — in serial mode it's bypassed. Adafruit: *"when all the way to the right we can get up to 2A max"*; fully counter-clockwise is no torque and no sound.
4. **Coil continuity**, the meter check in §2.

### ⚠️ Turn the run current down before it works

`RUN_CURRENT_PERCENT 50` is about half of the 31-step scale, with `CHOPPER_CONFIG_DEFAULT = 0x10000053` leaving `vsense = 0` (the high-current range) and the firmware never calling `enableVSense()`. On a breakout Adafruit rates to 2 A that's roughly **0.7–0.9 A RMS**, depending on its sense resistor.

The same science-jubilee source this harness comes from specifies **350 mA peak for a gen1 OT-2 pipette motor, 500 mA for a gen2** (`M906 V350` / `V500`). So the firmware is asking for 2–3× the motor's rating — and, like everything else in §3, *that only became live when the UART wire started working*. I'd drop `RUN_CURRENT_PERCENT` to ~20 and `HOLD_CURRENT_PERCENT` to ~10 before the first successful move, and make sure the Adafruit `1515` heat sink is on the driver (Cubware has a section on fitting it).

---

### ⚠️ I couldn't measure anything — the CubXL is off the Pi

```
$ lsusb
Bus 001/002/003/004 Device 001: Linux Foundation root hub     # nothing else
```

| device | last seen on the Pi |
|---|---|
| GRBL controller (CH340, `/dev/ttyUSB0`) | **2026-09-03 19:20 UTC** — `ch341-uart converter now disconnected` |
| capper + pipette Arduino (2341:0043, `/dev/ttyACM0`) | **2026-09-01 18:31 UTC**, right after campaign 77 |

So I have no way to read D9's current state or time a move. Everything above is from source. The Pi itself is fine (up 12 days, `~/CubOS` at `cbc33dc` with all four patches). Plug the Arduino back in and say the word and I'll re-measure D9 and time a bounded ±1 mm move to tell you which of the two rows in §3's table you're in.

### Also worth settling once it moves

- **The firmware is built for a P300, not your p20.** `MAX_VOLUME 300.0`, `UL_TO_MM 0.1098`, `PRIME_POSITION 36.0`, and a `P300.json` beside it. CubOS's `p300_single_gen2` entry carries the *identical* constants marked "calibrated from PANDA-BEAR", while every `p20_single_gen2` value is `# placeholder`. Cubware's BOM specifies a P300 too. Volumes will be wrong on both sides until the firmware is reflashed *and* `models.py` gets real p20 numbers.
- **Check the first successful move against a ruler.** science-jubilee says 48 steps/mm (gen1) or 200 (gen2) at 16× microstepping; PANDA says 1592. Somebody is wrong.

### Committed — [`a0ccbb7`](https://github.com/vertical-cloud-lab/byu-vcl/commit/a0ccbb7)

- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/a0ccbb7/cubos/docs/opentrons-pipette-wiring.md) — pin-6 claim corrected, the source inventory, the connector-orientation check, and the new §4 on the driver-disable path
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/a0ccbb7/cubos/README.md) — summary section

### Not done

No hardware measurement, no motion, no port opened, no protocol run — the CubXL hasn't been on the Pi since 2026-09-03. I didn't touch any wiring. Nothing is upstreamed: the Cubware diagram's pin shift is still unfiled, and neither CubOS patch has gone to Ursa.

The Tailscale step is still missing from `.github/workflows/claude.yml` on `main` (removed in `429fe34`); I joined manually again, and I can't edit workflow files myself. [Fix this →](https://claude.ai/code?q=On%20the%20main%20branch%20of%20vertical-cloud-lab%2Fbyu-vcl%2C%20re-add%20the%20%22Connect%20to%20Tailscale%22%20step%20to%20.github%2Fworkflows%2Fclaude.yml%20that%20commit%20429fe34%20removed.%20It%20uses%20tailscale%2Fgithub-action%40v2%20with%20oauth-client-id%3A%20%24%7B%7B%20secrets.TS_OAUTH_CLIENT_ID%20%7D%7D%2C%20oauth-secret%3A%20%24%7B%7B%20secrets.TS_OAUTH_SECRET%20%7D%7D%2C%20tags%3A%20tag%3Astream-cam-test%2C%20and%20must%20run%20before%20the%20%22Run%20Claude%20Code%22%20step.&repo=vertical-cloud-lab/byu-vcl)
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-08 21:17:32 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5591994630)

@claude the Pi is plugged back in. Try running that trio again, and I will let you know if anything is actuated on the pipette. Note that some of the ports on the pi might have changed. Try running the software changes you mentioned as well, and I will let you know if anything changed physically. It should be noted that I am giving 12V and 2A from the stepper motor driver to the p20 pipette. Let me know if that should be changed.

---

## @claude[bot] — 2026-09-08 21:17:49 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5591997774)

**Claude finished @benwhitney5463's task in 18m 48s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/34279764348)

---
### Ran it — **12/12, campaign 83**. And the probe I built underneath the position counter says the switch loop is **open** while the Arduino's STEP output is **perfect**

- [x] Reach the Pi (tailnet step still missing on `main` — joined manually)
- [x] Re-detect the serial ports — **both back, same names, no config edit needed**
- [x] Bench-check the plunger before sending anything
- [x] Offline gates: `validate_setup` PASS · `--mock` 12/12 · `passive_shadow` **0 nominal, 0 tip-stuck**
- [x] **Hardware run — 12/12, `completed`**, every plunger command timed live
- [x] New probe: read the limit switch and the motor in raw steps, underneath the counter and the gate
- [x] Answer the 12 V / 2 A question
- [x] Commit tool + logs + campaign CSVs ([`72047a7`](https://github.com/vertical-cloud-lab/byu-vcl/commit/72047a7))
- [ ] Firmware bisect — **not flashed**, see the end

```
Protocol complete — 12 steps executed.
```

Campaign 83, `21:22:52 → 21:26:55` UTC, 4m 3s. Decapped vial_1, pressed onto A1, aspirated, parked, recapped vial_1, decapped vial_2, blew out, dropped the tip, capped vial_2, home. No capper retries, no alarms.

---

### ✅ The ports came back on the same names

| device | port | USB ID |
|---|---|---|
| GRBL gantry | `/dev/ttyUSB0` | `1a86:7523` CH340 |
| capper + pipette Arduino | `/dev/ttyACM0` | `2341:0043` Uno R3 |

Your three config files needed **no edit at all** — the trio ran exactly as committed at `a0ccbb7`. Their stable `by-id` paths are recorded in the [run README](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/results/pipette_test_20260908/README.md) and are the safer thing to name if a third serial device ever joins.

Controller read live before the run: `$130/$131/$132` = 409.000 / 309.000 / 124.000, `$20=1` — matches the gantry file exactly.

### The plunger feedback you asked for

| step | command | dt | firmware stepped? |
|---|---|---|---|
| `connect()` | `STATUS` | 0.007 s | — (`homed:0, pos:0.00, max_vol:300.00`) |
| `connect()` | `HOME` | 0.520 s | back-off only — switch asserted |
| `connect()` prime | `MOVE_TO 5.0` (down) | **3.354 s** | **yes** |
| `pick_up_tip` | `MOVE_TO 0.0` (up) | 0.106 s | no — refused |
| `aspirate` | `ASPIRATE 0.5` (down) | **5.961 s** | **yes** → pos 36.00 |
| `blowout` | `MOVE_TO 7.0` (up from 36) | 0.106 s | no — refused |
| `drop_tip` | `MOVE_TO 10.0` (up) | 0.109 s | no — refused |
| `drop_tip` | `MOVE_TO 5.0` (up) | 0.107 s | no — refused |

**The two moments to have watched: `21:23:12` UTC (~3.4 s, at startup before the gantry homed) and `21:24:47` UTC (~6 s, down in vial_1).** Nothing at the tip rack, nothing at the blow-out, nothing at the tip drop — those four were refused by the firmware, not by CubOS. Byte-for-byte the shape of campaign 77.

---

### 🔬 New tool: [`pipette_driver_probe.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/tools/pipette_driver_probe.py)

Everything I've measured so far has gone through `MOVE_TO`/`HOME`, which are filtered through the two things that keep breaking: the position counter and the switch gate. So I went underneath both, using the firmware's `CMD_MOVE_RELATIVE` (code 16). It takes **raw steps** and hands them to `moveSteps()`, and two properties make it the right instrument:

- `moveSteps()` returns `stepsCompleted == abs(steps)`, and a False becomes `ERR:{"error":"Failed to move relative"}` — an aborted move is reported **explicitly** instead of being inferred from a round trip.
- the gate in `stepMotor()` only fires when DIR is LOW (up), so **down is completely ungated** — it exercises the driver and motor with the switch out of the picture.

```
limit switch   ASSERTED (D9 HIGH, loop OPEN)   dt=0.11s  ERR:{"error":"Failed to move relative"}
motor          DOWN 1.0 mm at 400 steps/s      dt=4.04s  vs 4.00s commanded  OK
```

**1592 steps at exactly the commanded rate**, deliberately slow so the motor makes its maximum torque and noise. Everything upstream of the STEP pin works. The fault is between the Arduino header and the motor windings.

### 🔴 One hypothesis now covers both symptoms: the pipette's own connector

D9 HIGH means the **switch loop is open**. Silence with no buzzing means **no coil current** — a swapped coil *pair* buzzes and vibrates; open coils are silent. The switch loop and both coils all arrive on the **same FC-10P connector at the pipette**, and a connector that isn't fully seated, or a bad crimp row, opens them together.

The switch reading has also flipped between passes — asserted before 09-01, clear for three passes on 09-01, asserted again since. That's intermittent-contact behaviour; a wrong pinout doesn't come and go.

**So the meter check is now the first thing to do, not the last.** Ribbon off the driver terminals, everything powered down:

```
blue–red      a few to a few tens of ohms     coil A
black–green   a few to a few tens of ohms     coil B
blue–black    open                            the coils are isolated
pin 6–pin 7   CLOSED at rest                  limit switch, normally-closed
```

Both coil pairs open ⇒ the connector or the crimps, not the pinout.

**And one test that takes two seconds and ignores everything else: holding torque.** With the driver idle and powered, grab the plunger and try to move it. Energized coils resist noticeably (`HOLD_CURRENT_PERCENT 30`). No resistance at all means no coil current, whatever position the plunger is in — which matters because `--motor-test` *can't* tell "no current" from "already against the stop", and the plunger has been ratcheted outward for days (below).

### ⚠️ Two of my own hypotheses, retracted

I checked the pinned `janelia-arduino/TMC2209` v10.1.1 rather than assuming, and two things I'd have bet on are wrong:

- **`SoftwareSerial` baud is not marginal.** The `setup(SoftwareSerial &)` overload defaults to **9600**, not the 115200 the `HardwareSerial` overloads use. `setupMotor()` passes no baud, so 9600 is what runs — comfortable on a 16 MHz ATmega328P.
- **`enable()` doesn't write another zero.** `toff_` initialises to `TOFF_DEFAULT = 3`, so it restores a live chopper config.

So the UART-disable path from my last comment only strands the driver if the register writes **partially** land — `setOperationModeToSerial` + `minimizeMotorCurrent` + `disable` arriving while `setRunCurrent`/`enable` don't. That needs a marginal connection rather than a wrong one. Still on the list, no longer at the top of it.

---

### On 12 V and 2 A — the supply is right; it's the *driver's* current that's wrong

**12 V into the driver's VM/GND screw terminal is correct** (the Adafruit 6121 takes 5–29 V), and **2 A is a ceiling, not a setting.** A stepper driver is a current source: the coil current is whatever IRUN/VREF asks for, and the supply only has to be able to deliver it. So don't change the supply.

What does need to come down is `RUN_CURRENT_PERCENT 50` in the firmware. That maps to IRUN 15/31 with `vsense = 0`, on the order of **0.9 A RMS** — against an OT-2 pipette motor that science-jubilee specs at **350 mA peak (gen1) / 500 mA (gen2)**. Roughly 2–3× rated. Worth fixing before the first successful move, along with fitting the heat sink.

Two things to double-check while you're there: the 12 V must land on **VM**, not VDD — VDD is logic only, and the board enumerates and acks every command perfectly happily with VM absent, which is indistinguishable from a healthy run at the serial port. And confirm EN is actually at 0 V *at the driver pin*, not just at the Arduino header.

### Three firmware readings that close open questions

- **`ASPIRATE`'s odd landing positions are explained.** `aspirate()` clamps to `MIN_VOLUME 5.0`, moves **down to `PRIME_POSITION 36.0` first**, and only then up to `36.0 − volume × 0.1098`. That second leg is *upward*, so the gate applies: switch clear (campaign 69) → both legs run → reports 35.45; switch asserted (77, 83) → second leg refused → reports 36.00. Every value in the logs is one of those two. It also means aspirate is never a small move — it drives to 36.0 whatever volume you ask for.
- **`0.673 s/mm` is arithmetic, not a fit.** `MOVEMENT_VELOCITY 2500` steps/s → 400 µs/step, plus ~23 µs of `digitalWrite`/`digitalRead` overhead, at `STEPS_PER_MM 1592`. Which is why a round trip that fails to scale with distance is conclusive.
- 🔴 **While the switch reads asserted, the plunger is a one-way ratchet.** Every upward command is refused, `HOME` only zeroes the counter, and there's no other retract path in the command set. Each run that reaches `aspirate` drives it further out and nothing brings it back. This session commanded ~+21 mm total. Fixing the switch loop is what restores the ability to retract at all — it isn't only a homing problem.

### ✅ Machine state

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | both returned to vials 1–2 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home before the next run. |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |
| `~/CubOS` | `cbc33dc` + all four patches |

### On "run the software changes as well" — I didn't flash, and here's why

The software change I described was the §4 bisect: build the firmware without `stepperDriver.setup()`, so the TMC2209 stays in standalone mode with the pot and the MS1/MS2 straps in charge. That's a firmware reflash, and the Pi has **no AVR toolchain at all** — `avrdude`, `arduino-cli` and `pio` are all absent — so it means an apt install on a production device plus reflashing the Arduino that *also* drives the capper. I'd want a flash backup and your go-ahead before doing that to a board the capper depends on.

It's also no longer the cheapest way to the answer: the two hypotheses I retracted above were the strongest reasons to suspect the UART path, and the meter check settles the connector question in two minutes without touching the board. **Say the word and I'll do the flash bisect next session** — back up the flash first, build both variants, and restore afterwards.

### Committed — [`72047a7`](https://github.com/vertical-cloud-lab/byu-vcl/commit/72047a7)

- [`cubos/tools/pipette_driver_probe.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/tools/pipette_driver_probe.py) — the raw-step probe (`--switch`, `--switch-monitor N` to wiggle the connector and watch it flip, `--motor-test`)
- [`cubos/results/pipette_test_20260908/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/72047a7/cubos/results/pipette_test_20260908) — [README](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/results/pipette_test_20260908/README.md), the [hardware log](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/results/pipette_test_20260908/run_hardware.log), the [plunger trace](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/results/pipette_test_20260908/plunger_trace.json), [this run's G-code](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/results/pipette_test_20260908/gantry_command_thisrun.log), both [probe](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/results/pipette_test_20260908/probe_switch.log) [logs](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/results/pipette_test_20260908/probe_motor.log) and all offline gates; campaign CSVs in [`campaign_83_20260908_212252/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/72047a7/cubos/results/campaign_83_20260908_212252)
- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/docs/opentrons-pipette-wiring.md) — new §6 with the measurements, the retractions in §4, the supply answer in §5
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/72047a7/cubos/README.md) — status section

### Not done

No firmware was flashed and no config file was changed. Still no camera on the CubXL deck, so whether a tip seated at A1, where the undropped tip is, and whether both caps are straight need your eyes. `drop_tip` still releases 35 mm above the slot pending a `tip_disposal` deck entry. Neither CubOS patch is upstreamed to Ursa, and I haven't filed anything against the Cubware diagram.

The Tailscale step is still missing from `.github/workflows/claude.yml` on `main` (removed in `429fe34`); I joined manually again, and I can't edit workflow files myself. [Fix this →](https://claude.ai/code?q=On%20the%20main%20branch%20of%20vertical-cloud-lab%2Fbyu-vcl%2C%20re-add%20the%20%22Connect%20to%20Tailscale%22%20step%20to%20.github%2Fworkflows%2Fclaude.yml%20that%20commit%20429fe34%20removed.%20It%20uses%20tailscale%2Fgithub-action%40v2%20with%20oauth-client-id%3A%20%24%7B%7B%20secrets.TS_OAUTH_CLIENT_ID%20%7D%7D%2C%20oauth-secret%3A%20%24%7B%7B%20secrets.TS_OAUTH_SECRET%20%7D%7D%2C%20tags%3A%20tag%3Astream-cam-test%2C%20and%20must%20run%20before%20the%20%22Run%20Claude%20Code%22%20step.&repo=vertical-cloud-lab/byu-vcl)
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-08 21:35:13 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5592188010)

New Trio (shorter test, different park positions)
[pipette_test.yaml](https://github.com/user-attachments/files/31977985/pipette_test.yaml)
[cub_xl_ben_pipette_capper.yaml](https://github.com/user-attachments/files/31977992/cub_xl_ben_pipette_capper.yaml)
[ben_6vials_tiprack.yaml](https://github.com/user-attachments/files/31978222/ben_6vials_tiprack.yaml)

---

## @sgbaird — 2026-09-09 21:12:02 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5608815876)

@claude have a look at https://science-jubilee.readthedocs.io/en/latest/building/pipette_tool.html and the GitHub repository attached with that, since this is a case where custom integration with an opentrons pipette has happened before, noting though that you might have already looked at some of this

---

## @claude[bot] — 2026-09-09 21:12:21 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5608819470)

**Claude finished @sgbaird's task in 14m 8s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/34405565494)

---
### Read it properly this time — and it turns up the p20 constants, an independent check on the P300 calibration, a 2.5× current error, and one resistor that would make the driver say what's wrong

- [x] Read the science-jubilee `pipette_tool` docs page
- [x] Pull `machineagency/science-jubilee` and read `tool_library/OT2_pipette` end to end
- [x] Cross-reference against `BU-KABlab/PANDA_Arduino` and CubOS's `models.py`
- [x] Extract what's actionable for the silent motor
- [x] Commit ([`3335fb8`](https://github.com/vertical-cloud-lab/byu-vcl/commit/3335fb8))

You're right that I'd touched it — on 2026-09-08 I cited the wiring PDF and the 350/500 mA figure. What I hadn't read was the **Duet `config.g` recipe**, the **Python driver**, and the **per-model config JSONs**, and that's where the new material is. Nothing ran on hardware and I didn't connect to the Pi; you didn't ask for a run.

The useful thing about this source is that it drives the *same* OT-2 pipette from a **Duet 3 / RepRapFirmware V axis** instead of an Arduino + TMC2209. PANDA is a port of it (PANDA vendors science-jubilee's tool doc verbatim; Ursa's page delegates to PANDA). So it's an independent implementation of the same mechanism — which makes every constant checkable.

---

### 🔑 The one to do first: a 1 kΩ resistor from A0 to A1, and the driver will tell you what's wrong

A Duet reports `open_load_a/b`, `short_to_ground_a/b` and over-temperature per driver through `M122`. Those flags are **on the TMC2209**, and the janelia library already exposes them — `getStatus()` returns a struct with exactly those fields, plus `isSetupAndCommunicating()`.

None of it is reachable here, because PANDA wires the UART one-way: `SoftwareSerial softSerial(RX_PIN, TX_PIN)` with `RX_PIN 14` documented as *"not connected but required"*. The driver cannot report a fault, and `setupMotor()` never asks whether a single register write landed.

The library's own README gives the fix in one line:

> *"The simplest way to connect the single TMC2209 serial signal to both the microcontroller TX pin and RX pin is to use a **1k resistor** between the TX pin and the RX pin to separate them."*

One resistor between **A0 and A1**. Then:

| flag | what it answers |
|---|---|
| `open_load_a` / `open_load_b` | **are the coils actually connected to the driver** — the meter check, without the meter |
| `short_to_ground_a` / `_b` | a latching fault that presents as a silent motor |
| `over_temperature_shutdown` | ditto, and plausible at the current you're running (below) |
| `isSetupAndCommunicating()` | whether *any* of `setupMotor()`'s register writes landed |

Given four rewiring passes have each moved the symptom without resolving it, I'd rather have the driver answer than guess again. `open_load_a/b` alone would settle the connector question outright.

### 🔴 The run current is about 2.5× the motor's rating

The Duet recipe is explicit — `M906` **peak** current: **350 mA for Gen1, 500 mA for Gen2**. Here:

```
RUN_CURRENT_PERCENT 50  ->  IRUN ~15/31, vsense=0 (enableVSense() never called)
I_rms = ((CS+1)/32) x (0.325/(R_sense+0.02)) / sqrt(2)
      = 884 mA rms = 1.25 A peak        vs. the 500 mA peak spec
```

| target | `RUN_CURRENT_PERCENT` |
|---|---:|
| 350 mA peak (Gen1) | **~11** |
| 500 mA peak (Gen2) | **~17** |

Assumes the common 0.11 Ω sense resistor — scale if Adafruit's differs, and `enableVSense()` gives usable resolution down there. This won't cause silence on its own, but it's why `over_temperature_shutdown` is worth reading, and it's worth fixing before the first move that works. Fit the Adafruit 1515 heat sink.

### 🔴 Gen1 and Gen2 are 4.17× apart, and the firmware hardcodes one number

`M92 V48` (Gen1) vs `M92 V200` (Gen2), both at 16× microstepping. Different current, different steps per unit. PANDA has a single `STEPS_PER_MM 1592` and a single current. **Worth reading the generation off the pipette body** — the diagram's own pipette is stamped `P300 GEN2` — before trusting any constant.

---

### ✅ Good news: PANDA's millimetres really are millimetres

I flagged on 2026-09-01 that commanded distances might come out ~2× wrong. This settles the underlying question, and it's cleaner than I expected. At 16× on a 200-step motor:

```
PANDA  1592 / 16 =  99.5 full steps per unit  ->  2.01 mm of lead per revolution
SJ      200 / 16 =  12.5 full steps per unit  ->  16.0 mm of lead per revolution
```

2 mm is an ordinary leadscrew lead. 16 mm is not. So **PANDA's units are physical millimetres and science-jubilee's V units are ~7.96 mm each** — their `M92 V200` is steps-per-V-unit and nothing in their stack needs it to be a millimetre.

That makes PANDA's plunger constants physically sensible: `PRIME 36.0`, `BLOWOUT 44.0`, `DROP_TIP 55.0` mm, with `homePipette()`'s 50 000-step budget being 31.4 mm — a ~55 mm plunger stroke, which is what an OT-2 pipette has. (The 2× worry stands only if the microstep UART write doesn't land: standalone MS1/MS2 default to 1/8, and then a commanded 1 mm travels 2 mm. Another thing `isSetupAndCommunicating()` would settle.)

### ✅ And the P300 volume calibration is corroborated

Converted to steps per microlitre — a property of the piston alone, independent of how either project mounts the tool:

```
science-jubilee P300:  0.91   units/uL x  200 steps/unit = 182.0 steps/uL
PANDA           P300:  0.1098 mm/uL    x 1592 steps/mm   = 174.8 steps/uL
                                                   agree to within 4%
```

Two projects, two controllers, same answer. **`UL_TO_MM 0.1098` is a real calibration, not a placeholder.**

### 🔴 Upstream ships a `P20_config.json` — and its `mm_to_ul` is wrong

There *is* a p20 entry upstream, for a "P20 Gen 2". But running the same consistency check on all three of their configs — full-scale volume against the travel `zero_position` makes available:

| model | `zero_position` | `mm_to_ul` | full-scale stroke | % of travel |
|---|---:|---:|---:|---:|
| P1000 | 310 | 0.31 | 310.0 | **100%** |
| P300 | 310 | 0.91 | 273.0 | **88%** |
| **P20** | 250 | **0.8531** | **17.1** | **6.8%** |

P1000's value is exactly `zero_position / max_volume`. P300's sits 12% under it — what a gravimetric trim looks like. P20's is neither: a p20 whose full 20 µL used under 7% of the plunger travel would be 93% dead band. And `0.8531` is within 6% of the P300's `0.91`, which is what a copied line looks like.

Self-consistent starting estimates, all needing a gravimetric calibration before any of them is a microlitre:

```
science-jubilee units:   mm_to_ul ~ 250 / 20 = 12.5    (vs the shipped 0.8531)
PANDA millimetres:       UL_TO_MM ~  36 / 20 =  1.8    (vs P300's 0.1098)
CubOS p20_single_gen2:   mm_to_ul   0.025  is ~72x too small
```

Two smaller ones from the same comparison: upstream's p20 is `min_volume: 1, max_volume: 20` where the firmware clamps to the **P300's** `[5, 300]` — which is why `ASPIRATE 0.5` has always landed at 35.45 (0.5 clamps up to 5, and `36.0 − 5 × 0.1098 = 35.451`). And CubOS's `p300_single_gen2` carries `max_volume=200.0`; a P300 is 300 µL and the firmware agrees.

---

### The header photo, redrawn

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/3335fb8/cubos/docs/_static/ot2-pipette-header-pinout.png?raw=true)

*Crop of `OT2_Wiring_Diagram.pdf`, machineagency/science-jubilee, MIT.*

Reading the dots against the ribbon table resolves the numbering completely and self-consistently — odd pins in one column, even in the other, pin 1 at the tip end:

| row, from the pipette-tip end | left column | right column |
|---|---|---|
| 1 (closest to the tip) | **2** black, coil B | **1** green, coil B |
| 2 | **4** blue, coil A | **3** red, coil A |
| 3 | **6** black, switch return | 5 — empty |
| 4 | 8 — empty | **7** red, switch signal |
| 5 (farthest from the tip) | 10 — empty | 9 — empty |

The check that doesn't depend on which face you're looking at:

> **The two fully-populated rows are the two nearest the pipette tip.** The four empty holes are the far row plus one hole in each of the two rows next to it.

### On the 180° flip — I worked it through properly, and the earlier conclusion holds

I'd said it was excluded. It is, but my reasoning was loose, so here it is in full. Under a flipped FC-10P, conductor `c` lands on header pin `11 − c`:

```
conductor 1 (green, coil B) -> header pin 10   unused inside the pipette
conductor 2 (black, coil B) -> header pin  9   unused
conductor 3 (red,   coil A) -> header pin  8   unused
conductor 4 (blue,  coil A) -> header pin  7   the switch SIGNAL
conductor 6 (switch return) -> header pin  5   unused
conductor 7 (switch signal) -> header pin  4   one end of coil A
```

Both coils lose at least one terminal to an unused pin → **no coil current, no buzzing** ✅ matches. And D9 lands on coil A, whose other end is header pin 3, fed by conductor 8 — unconnected at the machine end. So D9 dead-ends and floats, and the pullup makes it read **asserted, permanently**.

That "permanently" is the discriminator: a flip cannot produce the 2026-09-01 sessions where `HOME` ran its full 26.35 s budget and retractions worked, which need D9 LOW. So it's only in play if the FC-10P has been re-terminated since, and it hasn't.

Which leaves the **machine-end junction** — where four motor wires and two switch wires are soldered onto ten ribbon conductors — as the better suspect. It's the one place a persistent coil fault and a switch fault that moves every time you rework the Arduino end can coexist, and it's the least keyed, least documented joint in the chain. (Note the D9 state has tracked *your* rewiring at the Arduino/Molex end across five passes, not anything done at the pipette.)

### Two things upstream does that would close open items here

**Homing has a direction check with a named failure mode.** `homev.g` is coarse seek → back off → slow re-seek, and the doc says to watch the drive shaft the first time: it must move *toward* the endstop, and **"if you notice the pipette tip ejector starts to engage"** the direction is inverted — stop it by pressing the endstop by hand (twice, once per seek) and flip `M569 S`. Here the equivalent is `DIR_PIN` polarity in `homePipette()`, which seeks with DIR LOW. Their endstop convention matches PANDA's exactly — `M574 V1 S1 P"^pin"` enables the pullup and treats HIGH as triggered — so **both projects independently expect a normally-closed switch to ground**, which confirms what I read off the firmware.

**Tip pickup is sensed, not a friction press.** Upstream fits a *second*, external limit switch on the tool that trips when the nozzle seats into a tip, wires it as the machine's Z endstop, and picks tips up with RRF's `H4` (move until the endstop trips, no error):

```python
self._machine.move_to(z=z, s=800, param="H4")
```

That's the answer to the item that's been open on this branch since 08-25 — `pick_up_tip` here is an unsensed press, so `pickup_z` can't be verified in software and a missed tip is silent. Printable holders ship in the same tool library (`PipetteTool_Holder_Mechanical_Limit_Switch.stl`, plus a dust-proof variant and `endstop_attachment.STL`), which fits the 3D-printing SOP already in this repo.

### Order I'd go in

1. **1 kΩ from A0 to A1**, read `getStatus()` → `open_load_a/b` settles the coil question.
2. **Check Gen1 vs Gen2** on the pipette body.
3. **`RUN_CURRENT_PERCENT` to ~17** (Gen2) or ~11 (Gen1), heat sink on.
4. **Then** the volume constants: `MAX_VOLUME`/`MIN_VOLUME` for a p20, `UL_TO_MM` gravimetrically (~1.8 mm/µL to start), and `mm_to_ul: 1.0` on the CubOS side so `volume_ul` stops being converted twice.
5. **The sensed tip pickup** whenever the tip-seating question comes back.

### Committed — [`3335fb8`](https://github.com/vertical-cloud-lab/byu-vcl/commit/3335fb8)

- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/3335fb8/cubos/docs/opentrons-pipette-wiring.md) — new **§8**, all of the above with every source cited and the arithmetic shown
- [`cubos/docs/_static/ot2-pipette-header-pinout.png`](https://github.com/vertical-cloud-lab/byu-vcl/blob/3335fb8/cubos/docs/_static/ot2-pipette-header-pinout.png) — the header crop, MIT, attributed
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/3335fb8/cubos/README.md) — summary section

### Not done

No hardware run, no Pi connection, no wiring touched, no firmware flashed, no config file changed. I haven't filed the `P20_config.json` finding upstream with machineagency, nor the Cubware pin shift with Ursa, nor either CubOS patch — say the word on any of those and I'll write them up.

Two things I couldn't check from the source: whether Adafruit's 6121 uses a 0.11 Ω sense resistor (the current numbers scale with it), and whether your pipette is Gen1 or Gen2 — that one's a label on the body.

The Tailscale step is still missing from `.github/workflows/claude.yml` on `main` (removed in `429fe34`); I didn't need the tailnet this session, but I can't edit workflow files myself. [Fix this →](https://claude.ai/code?q=On%20the%20main%20branch%20of%20vertical-cloud-lab%2Fbyu-vcl%2C%20re-add%20the%20%22Connect%20to%20Tailscale%22%20step%20to%20.github%2Fworkflows%2Fclaude.yml%20that%20commit%20429fe34%20removed.%20It%20uses%20tailscale%2Fgithub-action%40v2%20with%20oauth-client-id%3A%20%24%7B%7B%20secrets.TS_OAUTH_CLIENT_ID%20%7D%7D%2C%20oauth-secret%3A%20%24%7B%7B%20secrets.TS_OAUTH_SECRET%20%7D%7D%2C%20tags%3A%20tag%3Astream-cam-test%2C%20and%20must%20run%20before%20the%20%22Run%20Claude%20Code%22%20step.&repo=vertical-cloud-lab/byu-vcl)
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---
