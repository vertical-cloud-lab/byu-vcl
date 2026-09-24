# Opentrons pipette → TMC2209 → Arduino wiring, checked against the firmware

Written 2026-09-01 while diagnosing "nothing happens on the pipette — no buzzing,
the plunger never moves" on the CubXL. Revised 2026-09-08: §3 corrected (pin 6 →
GND *is* on the Cubware diagram) and extended with the connector-orientation
check, and §4 added.

**Where the Ursa documentation lives.** There is exactly one Ursa-authored
pipette wiring source —
[`Cubware/documentation/opentrons-pipette-setup.md`](https://github.com/Ursa-Laboratories/Cubware/blob/main/documentation/opentrons-pipette-setup.md)
and its `images/PipetteControl.png`. (`images/ArduinoCircuitDiagram_v3.png` in the
same folder is the capper/lights circuit, referenced from
`vial-capper-decapper-build.md`; it has nothing to do with the pipette. Nothing in
CubOS, PANDA-CUB, Zoo or BU-Configs documents this wiring.) That page delegates
onward: *"The legacy PANDA-BEAR wiring docs point to the external
BU-KABlab/PANDA_Arduino repository for firmware source, pin assignments, and
installation instructions."* `PANDA_Arduino` in turn carries a vendored copy of
the science-jubilee OT2 pipette tool doc at `src/pipette_tool.md`, and *that*
project is where the authoritative 10-pin material actually is.

The wiring diagram in Cubware
([`documentation/opentrons-pipette-setup.md`](https://github.com/Ursa-Laboratories/Cubware/blob/main/documentation/opentrons-pipette-setup.md)
→ `images/PipetteControl.png`) does **not** match the pin map in the firmware that
Arduino is running. The pipette side of the diagram is right; the Arduino side is
shifted by one analog pin on all four driver-control lines, and the pin the
firmware actually drives as ENABLE is not connected to anything.

Everything below is read out of source, not inferred from behaviour. Sources:

| what | where |
|---|---|
| firmware pin map + constants | [`BU-KABlab/PANDA_Arduino` `include/Pipette.h`](https://github.com/BU-KABlab/PANDA_Arduino/blob/main/include/Pipette.h) |
| firmware step/home/aspirate logic | [`src/Pipette.cpp`](https://github.com/BU-KABlab/PANDA_Arduino/blob/main/src/Pipette.cpp) |
| driver library | [`janelia-arduino/TMC2209`](https://github.com/janelia-arduino/TMC2209) `@^10.1.0`, pinned in `platformio.ini` |
| OT-2 10-pin ribbon pinout | the Jubilee OT2 pipette tool doc, [`src/pipette_tool.md`](https://github.com/BU-KABlab/PANDA_Arduino/blob/main/src/pipette_tool.md) §"Wiring Harness Assembly" |
| **which physical hole is pin 1** | [`science-jubilee` `tool_library/OT2_pipette/assembly_docs/OT2_Wiring_Diagram.pdf`](https://github.com/machineagency/science-jubilee/blob/main/tool_library/OT2_pipette/assembly_docs/OT2_Wiring_Diagram.pdf) — a photograph of the pipette's own header with each wire on its hole |
| ribbon conductor numbering | [`_static/ribbon_to_hookup_wiring.png`](https://github.com/machineagency/science-jubilee/blob/main/docs/building/_static/ribbon_to_hookup_wiring.png) |
| breakout | [Adafruit 6121](https://www.adafruit.com/product/6121) — motor supply 5–29 VDC, VDD 3–5 V, **current set by an onboard potentiometer** |

Cubware's own text flags the whole page as provisional: *"the OT2 pipette hardware
path has not yet been validated on the physical machine in this checkout. Treat
every position, model constant, and serial command as a commissioning value."*

## 1. The firmware's pin map

```c
// include/Pipette.h
#define PIPETTE_LIMIT_PIN 9 // Limit switch for homing
#define RX_PIN 14           // SoftwareSerial RX pin (not connected but required)
#define TX_PIN 15           // SoftwareSerial TX pin to TMC2209 RX
#define STEP_PIN 16         // Step pin
#define DIR_PIN 17          // Direction pin
#define ENABLE_PIN 18       // Enable pin (optional)
```

On an Arduino Uno the analog pins carry digital numbers 14–19, so
`A0=14, A1=15, A2=16, A3=17, A4=18, A5=19`. Substituting:

| firmware symbol | value | Uno pin | goes to |
|---|---|---|---|
| `RX_PIN` | 14 | **A0** | nothing — SoftwareSerial RX, "not connected but required" |
| `TX_PIN` | 15 | **A1** | TMC2209 **UART** (PDN_UART) |
| `STEP_PIN` | 16 | **A2** | TMC2209 **STEP** |
| `DIR_PIN` | 17 | **A3** | TMC2209 **DIR** |
| `ENABLE_PIN` | 18 | **A4** | TMC2209 **EN** |
| `PIPETTE_LIMIT_PIN` | 9 | **D9** | pipette limit switch |

No other module in the firmware claims any of these — the capper/lights use
D3 (`NEOPIXEL_RING_PIN`), D4 (`LINEBREAK_SENSOR_PIN`), D5 and D6. There is no pin
conflict.

## 2. The diagram vs. the firmware

| signal | **firmware wants** | **diagram shows** | |
|---|---|---|---|
| TMC2209 `UART` | **A1** | A0 | ❌ A0 is the SoftwareSerial **RX** — the firmware never transmits on it |
| TMC2209 `STEP` | **A2** | A1 | ❌ A1 is the UART **TX** |
| TMC2209 `DIR` | **A3** | A2 | ❌ A2 is **STEP** |
| TMC2209 `EN` | **A4** | A3 | ❌ A3 is **DIR** |
| TMC2209 `GND` | GND | GND | ✅ |
| TMC2209 `VDD` | 5 V | 5 V | ✅ |
| limit switch signal | **D9** | D9 | ✅ |

Every driver-control line is one analog pin low, and **A4 appears nowhere in the
diagram**. What each one does if you build it as drawn:

**`EN` on A3 ⇒ the direction bit switches the driver on and off.** TMC2209 `EN`
is active-low. `moveTo()` does `digitalWrite(DIR_PIN, isMovingDown ? HIGH : LOW)`,
so the driver would be energised for one direction of travel and completely dead
for the other.

> **Correction, 2026-09-01.** Earlier revisions of this document, and the PR
> comments of 2026-08-31 and 2026-09-01, offered this as the explanation for the
> plunger only moving one way. **It is not.** The one-way behaviour is a
> *firmware* gate on the limit-switch reading — see §3 below, which quotes the
> line — and it is visible at the serial port as a flat ~0.11 s refusal, which an
> `EN` fault could never produce (the firmware does not read `EN` back). `EN` on
> A3 is still wrong and still needs moving to A4; it just is not what caused the
> one-way symptom.

**`UART` on A0 ⇒ the driver is never configured.** The firmware's
`setupMotor()` calls `setRunCurrent(50)`, `setHoldCurrent(30)`,
`setMicrostepsPerStep(16)`, `enableStealthChop()`, `enableCoolStep()` and
`enable()` — all of which are UART register writes. It never calls
`setHardwareEnablePin()`, so in the library `enable()` is UART-only:

```cpp
void TMC2209::enable() {
  if (hardware_enable_pin_ >= 0) { digitalWrite(hardware_enable_pin_, LOW); }  // never: default -1
  chopper_config_.toff = toff_;
  writeStoredChopperConfig();                                                  // UART
}
```

With UART on the wrong pin none of that lands, and the chip runs on its power-on
defaults: microstepping from the MS1/MS2 straps and **current from the VREF
potentiometer only**.

**`STEP` on A1 and `DIR` on A2 ⇒ they are swapped in effect.** The driver's STEP
input sees UART frames (edges only while the firmware transmits, i.e. at boot),
and its DIR input sees the step pulse train.

### Corrected Arduino ↔ TMC2209 wiring

```
TMC2209 EN    -> Arduino A4      (was A3)
TMC2209 UART  -> Arduino A1      (was A0)
TMC2209 STEP  -> Arduino A2      (was A1)
TMC2209 DIR   -> Arduino A3      (was A2)
TMC2209 GND   -> Arduino GND     (unchanged)
TMC2209 VDD   -> Arduino 5V      (unchanged)
Arduino A0    -> leave unconnected
```

## 3. The 10 pins on the pipette — this half of the diagram is correct

The OT-2 pipette's FC-10P connector, per the Jubilee tool doc's ribbon table and
the JST housing order `[Blue/4, Red/3, Green/1, Black/2]` (so coil 1 = ribbon 3+4,
coil 2 = ribbon 1+2):

| pipette pin | function | diagram | verdict |
|---|---|---|---|
| 1 | stepper coil B | → TMC `2B` | ✅ |
| 2 | stepper coil B | → TMC `2A` | ✅ |
| 3 | stepper coil A | → TMC `1B` | ✅ |
| 4 | stepper coil A | → TMC `1A` | ✅ |
| 5 | unused | — | ✅ |
| 6 | limit switch **return (GND)** | labelled `Limit switch GND` | ✅ |
| 7 | limit switch signal | → Arduino D9 | ✅ |
| 8, 9, 10 | unused | — | ✅ |

The coil grouping matters and it is right: 3+4 together and 1+2 together. Swapping
the two wires *within* a pair only reverses the direction of travel; **mixing the
pairs** (e.g. 1 with 3) makes the motor buzz and vibrate without turning. Since
there is no buzzing at all, the coil wiring is not the current fault.

### Which physical hole is pin 1 — the thing neither Ursa source states

Both Ursa-side sources give the *logical* pinout and neither says which end of
the connector is pin 1. The only source that does is science-jubilee's
[`OT2_Wiring_Diagram.pdf`](https://github.com/machineagency/science-jubilee/blob/main/tool_library/OT2_pipette/assembly_docs/OT2_Wiring_Diagram.pdf),
which is a **photograph of the pipette's own 10-pin header** with a coloured dot
on each populated hole. Read off it:

- the **top row of the header (9, 10) is empty**, and the two motor coils occupy
  the **bottom two rows** — `1|2` bottom, `3|4` above it;
- each coil is a **left-right pair within one row** (blue+red on `3|4`,
  black+green on `1|2`), matching the JST housing order `[Blue/4, Red/3,
  Green/1, Black/2]`;
- the limit-switch pair is **7 and 6 — diagonal**, one hole in each of two
  adjacent rows, not a same-row pair. Wiring it to 7+8 or 5+6 is the easy
  mistake.

If the populated rows are at the *other* end of the connector, the FC-10P is
crimped 180° out and every pin maps `n → 11 − n`: all four coil wires land on
unused pins 7–10 (silent motor, no buzzing) and the limit-switch pair lands on
pin 4 (a coil) and pin 5 (no connect). That case is testable without a
multimeter — see the D9 table below — and it is *excluded* on this machine,
because D9 has read LOW (loop closed) in three of the five wiring passes, which
a rotated connector could never produce.

Two-minute meter check, ribbon off the driver's screw terminals, everything
powered down: **blue–red** and **black–green** should each read a few to a few
tens of ohms; **blue–black** should read open, because the two coils of a
bipolar stepper are isolated. If both pairs read open, the fault is in the
crimps or the solder joints, not in the pinout.

### The limit-switch return, pin 6 → Arduino GND

`setupPipette()` does `pinMode(PIPETTE_LIMIT_PIN, INPUT_PULLUP)`, and D9 **HIGH
means "at the limit"** — so an open switch circuit reads *asserted*.

**This one pin explains both plunger symptoms.** `stepMotor()` gates the upward
direction on it:

```c
// Check for limit switch when moving UP (DIR_PIN is LOW for UP)
if (digitalRead(PIPETTE_LIMIT_PIN) == HIGH && digitalRead(DIR_PIN) == LOW)
{
    delay(DEBOUNCE_TIME);
    if (digitalRead(PIPETTE_LIMIT_PIN) == HIGH) { errorOccurred = true; break; }
}
```

and `homePipette()` checks it *before* its first step, so an asserted switch is
an instant "success" that runs only the 796-step back-off:

```c
digitalWrite(DIR_PIN, LOW);            // seek upward
while (!homingSuccessful && ...) {
    if (digitalRead(PIPETTE_LIMIT_PIN) == HIGH) { ... homingSuccessful = true; break; }
    ... step ...
    if (stepsCount > 50000) return false;      // ~26 s of seek
}
digitalWrite(DIR_PIN, HIGH);           // back off 796 steps @ 510 us = 0.406 s
```

| D9 reads | `HOME` | UP / retract moves | DOWN / forward moves |
|---|---|---|---|
| **HIGH (asserted)** | "success" in **0.52 s** — back-off only, no seek | aborted after 1 step + 100 ms debounce → **~0.11 s** | unaffected |
| **LOW (clear)** | full 50000-step budget, then `false` → **26.35 s** ERR | normal, scales with distance | unaffected |

Both constants are exact: 796 × 510 µs + `DEBOUNCE_TIME 100` = **0.506 s** vs.
0.52 s measured; 1 step + 100 ms = **~0.1 s** vs. 0.11 s measured.

Consequences for the wiring:

- **Pin 6 must reach Arduino GND**, which is what the diagram's
  `Limit switch GND` label means. Anywhere that loop is open — pin 6, pin 7, the
  switch itself, a crimp — D9 idles HIGH through the pull-up and you get the
  whole "HIGH" row above: a fake home *and* a plunger that refuses to retract.
- The contact must be **normally closed**: LOW (closed to GND) at rest, opening
  as the plunger reaches the limit. A normally-open contact gives the HIGH row.

Observed history on this machine, all four rewiring passes:

| date / pass | `HOME` | backward | ⇒ D9 |
|---|---|---|---|
| 2026-08-31, before any rewiring | 0.52 s | refused | HIGH |
| 2026-09-01 18:33, rewire #1 | 26.35 s ERR | moves | LOW |
| 2026-09-01 18:56, rewire #2 | 26.35 s ERR | moves | LOW |
| 2026-09-01 19:13, rewire #3 | 26.35 s ERR | moves | LOW |
| 2026-09-01 19:46, rewire #4 | 0.52 s | refused | HIGH |
| 2026-09-08, rewire #5 (Arduino pins corrected) | not measurable — hardware off the Pi | — | — |

Nothing else in the plunger's behaviour changed across those passes. Treat this
pin as the first thing to measure whenever the plunger misbehaves.

## 4. Fixing the UART pin opens a new way for the driver to be switched off

Added 2026-09-08, after the Arduino-side pins were corrected and the plunger
still did not move. This is a *software* failure mode, and it was not reachable
while UART was on the wrong pin.

`setupPipette()` → `setupMotor()` → `stepperDriver.setup(softSerial)` →
[`TMC2209::initialize()`](https://github.com/janelia-arduino/TMC2209/blob/main/src/TMC2209/TMC2209.cpp):

```cpp
void TMC2209::initialize(long serial_baud_rate, SerialAddress serial_address)
{
  serial_baud_rate_ = serial_baud_rate;
  setOperationModeToSerial(serial_address);   // i_scale_analog = 0  <- VREF pot out of circuit
                                              // pdn_disable = 1, mstep_reg_select = 1
  setRegistersToDefaults();
  clearDriveError();
  minimizeMotorCurrent();                     // IRUN / IHOLD -> minimum
  disable();                                  // CHOPCONF.toff = 0 -> output stage OFF
  disableAutomaticCurrentScaling();
  disableAutomaticGradientAdaptation();
}
```

`setupMotor()` then calls `setRunCurrent(50)`, `setHoldCurrent(30)`,
`setMicrostepsPerStep(16)`, `enableStealthChop()`, `enableCoolStep()` and
`enable()` to undo the last two lines.

**Every one of those is a UART write, and the link is write-only.**
`SoftwareSerial softSerial(RX_PIN, TX_PIN)` is `(A0, A1)`, and `Pipette.h` says of
A0: *"SoftwareSerial RX pin (not connected but required)"*. The TMC2209's UART is
single-wire half-duplex (PDN_UART); with only TX attached the Arduino can never
read the driver back, and `setupMotor()` never calls
`stepperDriver.isSetupAndCommunicating()`. Nothing anywhere verifies that a
single register write landed.

So the two wiring states behave very differently:

| UART wire on | what the driver does |
|---|---|
| **A0** (the RX pin — the Cubware diagram) | nothing is ever transmitted. Chip stays in **standalone mode**: VREF pot sets current, MS1/MS2 straps set 1/8 microstepping, `CHOPCONF.toff` at its power-on default of 3 → **output stage enabled** |
| **A1** (the TX pin — correct) | the first thing that lands is `i_scale_analog = 0`, **taking the current pot out of the circuit**, followed by `minimizeMotorCurrent()` and `disable()`. If any later write is dropped or garbled, the driver sits at **minimum current with its output stage off** — silent, no holding torque — while the Arduino happily bit-bangs STEP into it |

### Two ways this could have failed that are now ruled out

Measured against the pinned library on 2026-09-08 rather than assumed:

- **SoftwareSerial baud is not marginal.** The `setup(SoftwareSerial &)` overload
  defaults to **9600** (`TMC2209.h:67`), not the 115200 the `HardwareSerial`
  overloads use. `setupMotor()` passes no baud, so 9600 is what runs — comfortable
  on a 16 MHz ATmega328P.
- **`enable()` does not write another zero.** `toff_` is initialised to
  `TOFF_DEFAULT = 3` (`TMC2209.h:508-510`), so `enable()` restores a live chopper
  config.

So the UART path only strands the driver if the register writes **partially**
land — `setOperationModeToSerial` + `minimizeMotorCurrent` + `disable` arriving
while the later `setRunCurrent`/`enable` do not. That is a narrower failure than
"UART is misrouted", and it needs a marginal connection rather than a wrong one.
Worth keeping on the list, no longer at the top of it.

### The bisect: pull the UART wire off A1

Nothing else changes. With the wire off, `setup()`'s writes go nowhere, the chip
never enters serial mode, and it runs on its power-on defaults with the pot back
in charge of current.

- **Plunger moves** → the fault is in the UART configuration path. (Distances will
  come out 2× — standalone MS1/MS2 default to 1/8, not the 1/16 the firmware
  assumes; see §6.)
- **Plunger still silent** → it is power, current, or the coil circuit. §5 and the
  meter check in §3.

Either way, turn the VREF pot up before running the test.

If you would rather instrument than unplug: tie A0 to the same PDN_UART line
through a 1 kΩ resistor — that is how the janelia library's single-wire mode is
meant to be wired — and then `isSetupAndCommunicating()` becomes meaningful and
can be checked after `setup()`.

### ⚠️ Turn the run current down before it works

`RUN_CURRENT_PERCENT 50` maps to `IRUN = 15` of 31, with `CHOPPER_CONFIG_DEFAULT
= 0x10000053` leaving `vsense = 0` (the high-current range) and the firmware never
calling `enableVSense()`. On a breakout Adafruit rates to 2 A that is on the order
of **0.9 A RMS / 1.2 A peak**.

The same science-jubilee source this harness comes from specifies **350 mA peak
for a gen1 OT-2 pipette motor and 500 mA for a gen2** (`M906 V350` / `M906 V500`).
So the firmware asks for roughly 2–3× the motor's rating — and *that only starts
mattering once the UART wire works*, because until then the pot was in charge.
Drop `RUN_CURRENT_PERCENT` to ~20 and `HOLD_CURRENT_PERCENT` to ~10 before the
first successful move, and fit the Adafruit `1515` heat sink to the driver
(Cubware's setup page has a section on it).

## 5. Two more things on that page

**"120V/2A Power Supply" is a typo for 12 V.** The Adafruit 6121 breakout takes
5–29 VDC on the motor terminal. Do not connect mains.

**12 V at 2 A into the driver's VM terminal is the right supply, and 2 A is a
ceiling rather than a setting.** A stepper driver is a current source: the coil
current is whatever IRUN/VREF asks for, and the supply's amp rating only has to
be at least that. It is the driver's *current setting* that needs to come down to
the motor's 350–500 mA, not the supply. Two things to keep in mind: the supply
must land on the driver's VM/GND screw terminal, not on VDD (VDD is logic only,
and the board enumerates and acks every command happily with VM absent — silently);
and 12 V into a 350 mA motor is a lot of headroom, so fit the heat sink and keep
the current setting low.

**The motor supply is separate from VDD.** The Arduino's 5 V on `VDD` powers the
driver's logic only. With no voltage on the `+`/`-` terminal the board still
accepts STEP/DIR and acknowledges everything, with zero coil current and total
silence — indistinguishable at the serial port from a healthy run.

## 6. What the 2026-09-08 measurements narrowed it to

Both readings came from `cubos/tools/pipette_driver_probe.py`, which drives the
firmware's `CMD_MOVE_RELATIVE` (code 16) in raw steps. That command reports an
aborted move **explicitly** (`ERR:{"error":"Failed to move relative"}`) instead of
leaving it to be inferred from a round-trip time, and its DOWN direction is not
gated by the limit switch at all.

```
limit switch   ASSERTED (D9 HIGH, loop OPEN)   dt=0.11s  ERR:{"error":"Failed to move relative"}
motor          DOWN 1.0 mm at 400 steps/s      dt=4.04s  expected 4.00s  OK
```

### The Arduino is not the problem

1592 steps at exactly the commanded rate, deliberately slow so the motor makes
its most torque and most noise. Everything upstream of the STEP pin works. The
fault is between the Arduino header and the motor windings.

### The one hypothesis that explains both symptoms at once

D9 reading HIGH means the **switch loop is open**, and total silence with no
buzzing means **no coil current** (a swapped coil *pair* buzzes and vibrates;
open coils are silent). Both the switch loop and both coils arrive on the same
FC-10P connector at the pipette. A connector that is not fully seated, or a bad
crimp row, opens all of them together.

The switch reading has also flipped between passes — asserted before 2026-09-01,
clear for three passes on 2026-09-01, asserted again since — while the Arduino
end was being rewired. An intermittent contact behaves exactly like that; a wrong
pinout does not.

So the meter check in §3 is now the first thing to do, not the last:

```
ribbon unplugged from the driver terminals, everything powered down

blue–red     a few to a few tens of ohms      coil A
black–green  a few to a few tens of ohms      coil B
blue–black   open                             the coils are isolated from each other
pin 6–pin 7  CLOSED at rest                   the limit switch, normally-closed
```

Both coil pairs open ⇒ the connector or the crimps, not the pinout. Pin 6–7 open
at rest ⇒ the same loop, or a normally-*open* switch, which the firmware cannot
use.

### Holding torque is the test that ignores the mechanical stop

`--motor-test` cannot tell "no coil current" from "the plunger is already against
its stop" — and the plunger *is* being ratcheted outward, see below. Holding
torque can: with the driver idle and powered, grab the plunger and try to turn or
push it. Energized coils resist noticeably (`HOLD_CURRENT_PERCENT 30`). No
resistance at all means no coil current, whatever position it is in.

### ⚠️ While the switch reads asserted, the plunger only travels one way

Every upward command is refused by the gate in `stepMotor()`, `HOME` only zeroes
the counter, and there is no other retract path in the command set. So each run
that reaches `aspirate` drives the plunger further out and nothing brings it
back. Fixing the switch loop is what restores the ability to retract at all — it
is not only a homing problem.

### `ASPIRATE`'s reported positions, explained

`aspirate()` clamps to `MIN_VOLUME 5.0`, moves **down to `PRIME_POSITION 36.0`
first**, then up to `36.0 - volume * UL_TO_MM`. The second leg is upward, so the
gate applies:

- switch clear → both legs run → reports 35.45
- switch asserted → second leg refused → reports 36.00

Every value seen in the logs is one of those two. It also means aspirate is never
a small move: it drives to 36.0 whatever volume is asked for. (`dispense()`
ignores its volume argument entirely and moves to `BLOWOUT_POSITION 44.0`.)

### Where 0.673 s/mm comes from

`stepMotor()` sets `stepDelay = 1000000 / velocity` clamped to [100, 10000] µs.
At `MOVEMENT_VELOCITY = 2500` steps/s that is 400 µs, plus ~23 µs of
`digitalWrite`/`digitalRead`/loop overhead → ~423 µs per step, and at
`STEPS_PER_MM 1592` that is **0.673 s/mm**. Arithmetic, not a fit — which is why
a round trip that fails to scale with distance is conclusive.

## 7. Consequences that outlive the wiring fix

**Microstepping is almost certainly 1/8, not the 1/16 the firmware assumes.**
`setMicrostepsPerStep(16)` is a UART write, so with UART unconfigured the chip
uses its MS1/MS2 straps, which default to 1/8. The firmware's own numbers admit
it: `STEPS_PER_MM 1592.0`, but the homing back-off says
`int backOffSteps = 796; // this is equal to 1mm` — exactly half. Same factor in
`if (stepsCount > 50000) // About 62mm of travel`: 50000 steps is 31 mm at 1592
steps/mm and 62 mm at 796. **Expect commanded millimetres to come out 2× on the
plunger** until either the UART wire is fixed or MS1/MS2 are strapped for 1/16.
Check it with a ruler on the first successful move.

**Volumes are double-converted, then clamped.** CubOS computes
`mm_travel = volume_ul * mm_to_ul` and sends that as the `ASPIRATE` argument, but
the firmware's `aspirate(float volume, ...)` takes **microlitres** and does its own
`volume * UL_TO_MM` internally. It also clamps to `MIN_VOLUME 5.0` /
`MAX_VOLUME 300.0` first. So a protocol asking for 20 µL sends `ASPIRATE 0.5`, the
firmware clamps 0.5 → 5 µL, and the plunger targets
`PRIME_POSITION 36.0 − 5×0.1098 = 35.45` — the exact value in every trace. To pass
real microlitres through, `mm_to_ul` would have to be **1.0**.

**`aspirate` always primes first.** `aspirate()` runs `moveTo(PRIME_POSITION)`
before anything else, so the plunger travels to 36.0 mm regardless of the
requested volume. `dispense()` ignores its volume argument entirely and just moves
to `BLOWOUT_POSITION 44.0`.

**The firmware is built for a P300.** `MAX_VOLUME 300.0`, `UL_TO_MM 0.1098`,
`PRIME 36.0`, `BLOWOUT 44.0`, `DROP_TIP 55.0`, and a `P300.json` beside it. That is
why `STATUS` reports `max_vol: 300.00` with a p20 on the head. CubOS's
`p20_single_gen2` entry in `instruments/pipette/models.py` is all
`# placeholder` values and does not correspond to this firmware at all.

**Timing at the serial port cannot see the motor.** `stepMotor()` bit-bangs STEP
and counts loop iterations; there is no encoder, no current sense, no feedback.
A move that takes the expected `0.673 s/mm` proves the *Arduino* stepped and
nothing more. (0.673 s/mm is itself just the firmware's arithmetic:
`MOVEMENT_VELOCITY 2500` → 400 µs/step, × `STEPS_PER_MM 1592` ≈ 0.67 s/mm.)
Likewise `HOME` failing after 26.35 s is the 50000-step budget in
`homePipette()`, not the 60 s timeout.

---

## 8. The science-jubilee prior art

`machineagency/science-jubilee` is the upstream of this whole pipette harness —
`BU-KABlab/PANDA_Arduino` vendors a copy of its tool doc at `src/pipette_tool.md`,
and Ursa's `Cubware/documentation/opentrons-pipette-setup.md` delegates to PANDA.
It drives the same OT-2 pipette from a **Duet 3 / RepRapFirmware** V axis instead of
an Arduino + TMC2209, so it is an independent implementation of the same mechanism —
which makes it usable as a cross-check on every constant PANDA carries.

Sources (MIT licensed):

| what | where |
| --- | --- |
| Duet `config.g` recipe | [`tool_library/OT2_pipette/duet_configs/OT2_Pipette_Configuration.md`](https://github.com/machineagency/science-jubilee/blob/main/tool_library/OT2_pipette/duet_configs/OT2_Pipette_Configuration.md) |
| Python driver | [`src/science_jubilee/tools/Pipette.py`](https://github.com/machineagency/science-jubilee/blob/main/src/science_jubilee/tools/Pipette.py) |
| Per-model constants | [`src/science_jubilee/tools/configs/P20_config.json`](https://github.com/machineagency/science-jubilee/blob/main/src/science_jubilee/tools/configs/P20_config.json) (also P300, P1000) |
| Header photo | [`tool_library/OT2_pipette/assembly_docs/OT2_Wiring_Diagram.pdf`](https://github.com/machineagency/science-jubilee/blob/main/tool_library/OT2_pipette/assembly_docs/OT2_Wiring_Diagram.pdf) |
| Tip-sensor holders | `tool_library/OT2_pipette/designs/3D_only/PipetteTool_Holder_{Mechanical,Dust-Proof}_Limit_Switch.stl` |

### 8.1 The two systems agree on the pipette, and that validates PANDA's numbers

RRF sets steps per axis unit with `M92`; the doc gives **48 (Gen1) / 200 (Gen2)** at
`M350 V16 I1`. PANDA uses `STEPS_PER_MM 1592.0`, also at 16x. Those are not the same
unit — the ratio is `1592 / 200 = 7.96`.

Which one is a millimetre falls out of the motor arithmetic. At 16x on a 200-step
motor:

```
PANDA  1592 / 16 =  99.5 full steps per unit  ->  2.01 mm of lead per revolution
SJ      200 / 16 =  12.5 full steps per unit  ->  16.0 mm of lead per revolution
```

2 mm is an ordinary leadscrew lead; 16 mm is not. **PANDA's "mm" are real
millimetres and science-jubilee's V units are ~7.96 mm each** — their `M92 V200`
is steps-per-V-unit, and nothing in their stack ever needs it to be a millimetre
because every position and volume constant is calibrated in those same units.

That in turn makes PANDA's plunger constants physically sensible: `PRIME 36.0`,
`BLOWOUT 44.0`, `DROP_TIP 55.0` mm, with `homePipette()`'s 50000-step budget being
31.4 mm — i.e. a ~55 mm plunger stroke, which is what an OT-2 pipette has.

The volume calibration cross-checks too. Converted to steps per microlitre — a
property of the piston alone, independent of how either project mounts the tool:

```
science-jubilee P300:  0.91   units/uL x  200 steps/unit = 182.0 steps/uL
PANDA           P300:  0.1098 mm/uL    x 1592 steps/mm   = 174.8 steps/uL
                                                    agree to within 4%
```

Two independent projects, two different controllers, same answer. **PANDA's
`UL_TO_MM 0.1098` is a real P300 calibration, not a placeholder.**

### 8.2 ...which is exactly why the P20 numbers are not trustworthy on either side

Upstream ships a `P20_config.json` for a "P20 Gen 2". Running the same consistency
check on all three of their configs — full-scale volume against the axis travel that
`zero_position` makes available:

| model | `zero_position` | `mm_to_ul` | full-scale stroke | % of available travel |
| --- | ---: | ---: | ---: | ---: |
| P1000 | 310 | 0.31 | 310.0 | **100%** |
| P300 | 310 | 0.91 | 273.0 | **88%** |
| **P20** | 250 | **0.8531** | **17.1** | **6.8%** |

P1000's value is exactly `zero_position / max_volume`; P300's sits 12% under it, which
is what a gravimetric trim looks like. P20's is neither — a P20 whose full 20 µL used
under 7% of the plunger travel would be a pipette that is 93% dead band. `0.8531` is
within 6% of the P300's `0.91`, which is what a copied line looks like, not a
calibration.

Self-consistent values, for anyone picking this up:

```
science-jubilee units:   mm_to_ul ~ 250 / 20 = 12.5   (vs the shipped 0.8531)
PANDA millimetres:       UL_TO_MM ~  36 / 20 =  1.8   (vs P300's 0.1098)
CubOS p20_single_gen2:   mm_to_ul   0.025 is ~72x too small
```

All three are estimates from "full volume uses the full stroke" and need a
gravimetric calibration before any number is a microlitre. The point is only that
the shipped values are wrong by one to two orders of magnitude, not by a few percent.

Also from that table: **`MIN_VOLUME`/`MAX_VOLUME` in the firmware are P300 values**
(`5.0` / `300.0`); upstream's P20 entry is `min_volume: 1, max_volume: 20`. The
firmware's `constrain(volume, MIN_VOLUME, MAX_VOLUME)` is why `ASPIRATE 0.5` has
always landed at 35.45 — 0.5 clamps up to 5, and `36.0 - 5 x 0.1098 = 35.451`.

### 8.3 Gen1 and Gen2 are 4.17x apart, and PANDA hardcodes one number

`M92 V48` vs `M92 V200` — the two generations do not share a drive ratio. `M906`
differs too: **350 mA peak for Gen1, 500 mA for Gen2**. PANDA has a single
`STEPS_PER_MM` and a single current, so the generation printed on the pipette body
(the diagram's own pipette reads `P300 GEN2`) has to be checked before any of these
constants mean anything.

### 8.4 Run current: PANDA asks for roughly 2.5x the motor's rating

`M906 V500` is the Gen2 spec. `RUN_CURRENT_PERCENT 50` in the janelia library maps
to `IRUN ~ 15/31`, and with `CHOPPER_CONFIG_DEFAULT = 0x10000053` leaving `vsense = 0`
(and `enableVSense()` never called):

```
I_rms = ((CS+1)/32) x (0.325 / (R_sense + 0.02)) / sqrt(2)
CS=15, R_sense=0.11:  884 mA rms = 1.25 A peak     vs. the 500 mA peak spec
```

Working backwards for the spec values (same assumptions):

| target | CS | `RUN_CURRENT_PERCENT` |
| --- | ---: | ---: |
| 350 mA peak (Gen1) | ~4 | **~11** |
| 500 mA peak (Gen2) | ~5 | **~17** |

Scale if the Adafruit 6121's sense resistor is not 0.11 Ω, and prefer
`enableVSense()` (0.18 V full scale) for usable resolution down here. Fit the
Adafruit 1515 heat sink either way.

### 8.5 The Duet can see why a driver isn't driving. This port cannot

RRF reports `open_load_a/b`, `short_to_ground_a/b` and over-temperature per driver
through `M122`. The same flags are on the TMC2209 and the janelia library exposes
them — `getStatus()` returns a struct with `open_load_a`, `open_load_b`,
`short_to_ground_a`, `short_to_ground_b`, `over_temperature_shutdown`, plus
`isSetupAndCommunicating()`.

**None of it is reachable here, because PANDA wires the UART one-way.**
`SoftwareSerial softSerial(RX_PIN, TX_PIN)` with `RX_PIN 14` documented as
"not connected but required". So the driver cannot report a fault, and
`setupMotor()` never asks whether a single register write landed.

The library's README gives the fix directly: *"the simplest way to connect the
single TMC2209 serial signal to both the microcontroller TX pin and RX pin is to use
a 1k resistor between the TX pin and the RX pin to separate them."* One resistor
between **A0 and A1** turns the link bidirectional.

That is worth doing before any more wiring passes. `open_load_a` / `open_load_b`
answer "are the coils actually connected to the driver" without a meter, and
`over_temperature_shutdown` and `short_to_ground_*` are both latching states that
present as a silent motor and are invisible today.

### 8.6 The header photo, and the check it supports

![OT-2 pipette 10-pin header](_static/ot2-pipette-header-pinout.png)

*Crop of `OT2_Wiring_Diagram.pdf`, machineagency/science-jubilee, MIT. Coloured dots
mark the populated holes; tan and purple are the limit switch, blue/red/green/black
are the motor.*

This is the only source anywhere that shows which physical hole is which. Reading it
against the ribbon table (`1` Green, `2` Black, `3` Red, `4` Blue on the motor;
`6` Black, `7` Red on the switch; `5`, `8`, `9`, `10` unused) resolves the numbering
completely and self-consistently:

| row, from the pipette-tip end | left column | right column |
| --- | --- | --- |
| 1 (closest to the tip) | **2** black, coil B | **1** green, coil B |
| 2 | **4** blue, coil A | **3** red, coil A |
| 3 | **6** black, switch return | 5 — empty |
| 4 | 8 — empty | **7** red, switch signal |
| 5 (farthest from the tip) | 10 — empty | 9 — empty |

Odd pins in one column, even in the other, pin 1 at the tip end. The
viewing-independent form, which is what to check by eye:

> **The two fully-populated rows are the two nearest the pipette tip. The four empty
> holes are the far row plus one hole in each of the two rows next to it.**

### 8.7 What a 180-degree connector flip would actually look like

Worth writing down precisely, because the mapping is not intuitive. Under a flipped
FC-10P, conductor `c` lands on header pin `11 - c`:

```
conductor 1 (green, coil B) -> header pin 10   unused inside the pipette
conductor 2 (black, coil B) -> header pin  9   unused
conductor 3 (red,   coil A) -> header pin  8   unused
conductor 4 (blue,  coil A) -> header pin  7   the switch SIGNAL
conductor 6 (switch return) -> header pin  5   unused
conductor 7 (switch signal) -> header pin  4   one end of coil A
```

Both coils end up with at least one terminal on an unused pin, so **no coil current
and no buzzing**. And D9 lands on coil A, whose other end is header pin 3, fed by
conductor 8 — which is unconnected at the machine end. So D9 dead-ends and floats,
and the pullup makes it **read asserted, permanently**.

That "permanently" is the discriminator. A flip cannot produce the 2026-09-01
sessions where `HOME` ran its full 26.35 s budget and retractions worked — those
require D9 LOW. So a flip only explains the record if the FC-10P has been
re-terminated since, which it has not. The **machine-end junction**, where four
motor wires and two switch wires are soldered onto ten ribbon conductors, remains
the better suspect: it is the one place a persistent coil fault and a
rework-sensitive switch fault can coexist, and it is the least keyed, least
documented joint in the chain.

### 8.8 Two things upstream does that would close open items here

**Homing has a direction check with a named failure mode.** `homev.g` is a coarse
seek, a back-off, then a slow re-seek:

```gcode
G91
G1 V-200 F800 H1   ; coarse seek toward the endstop
G1 V1    F600      ; back off
G1 V-10  F600 H1   ; slow re-seek
G90
G1 V0.5  F600
```

and the doc says to watch the drive shaft the first time: it must move *toward* the
endstop, and **"if you notice the pipette tip ejector starts to engage"** the
direction is inverted — stop it by pressing the endstop by hand (twice, once per
seek) and flip `M569 S`. On this machine the equivalent knob is `DIR_PIN` polarity in
`homePipette()`, which currently seeks with DIR LOW. The endstop convention matches
PANDA's exactly: `M574 V1 S1 P"^pin"` enables the pullup and treats HIGH as
triggered, so both projects expect a **normally-closed** switch to ground.

**Tip pickup is sensed, not a friction press.** Upstream fits a *second*, external
limit switch that trips when the nozzle seats into a tip, wires it as the machine's
Z endstop, and picks up tips with `G1 ... H4` — move until the endstop trips, no
error:

```python
self._machine.move_to(z=z, s=800, param="H4")
```

That is the open item on this branch: `pick_up_tip` here is an unsensed press, so
`pickup_z` cannot be verified in software and a missed tip is silent. Printable
holders for the switch are in `designs/3D_only/`
(`PipetteTool_Holder_Mechanical_Limit_Switch.stl`, and a dust-proof variant), plus
`endstop_attachment.STL` in the laser-cut set.

### 8.9 The command semantics are the same, which is reassuring

`Pipette.py` orders the plunger `aspirate < zero_position < blowout_position <
drop_tip_position`, with `_aspirate` moving negative from `prime()` and `blowout()`
returning to prime afterwards. PANDA is the same scheme (`ZERO 0 < PRIME 36 <
BLOWOUT 44 < DROP_TIP 55`, `aspirate()` subtracting from `PRIME_POSITION`), so the
port is faithful. Two divergences worth knowing:

- PANDA's `dispense(float /*volume*/, ...)` **ignores its volume argument** and moves
  to `BLOWOUT_POSITION`. Upstream's `_dispense` is a true relative move of
  `vol * mm_to_ul`. PANDA does have relative equivalents — `aspirateRelative`,
  `dispenseRelative`, `plungerMoveRelative` — which CubOS never calls.
- CubOS's `drop_tip_position` for the p300 is `60.0`; the firmware's is `55.0`.
  The firmware sets `maxPosition = DROP_TIP_POSITION` and `moveTo()` runs
  `constrain(positionMM, minPosition, maxPosition)`, so a commanded `60.0` is
  silently clamped to `55.0`. It lands on the real eject stop, but the CubOS
  constant is fiction.
- CubOS's `p300_single_gen2` carries `max_volume=200.0`. A P300 is 300 µL, and the
  firmware agrees (`MAX_VOLUME 300.0`). Upstream's P300 config also says 300.

### 8.10 Order of operations, given all of the above

1. **The 1k resistor from A0 to A1**, and read `getStatus()`. `open_load_a/b` answers
   the coil question without a meter, and `over_temperature_shutdown` /
   `short_to_ground_*` are latching failures that look exactly like this one.
2. **Check the generation** printed on the pipette body. Gen1 and Gen2 differ 4.17x
   in steps per unit and 350 vs 500 mA in current.
3. **Drop `RUN_CURRENT_PERCENT` to ~17** (Gen2) or ~11 (Gen1) before the first
   successful move, and fit the heat sink.
4. **Then** the volume constants: `MAX_VOLUME`/`MIN_VOLUME` for a p20 (20 / 1),
   `UL_TO_MM` from a gravimetric calibration (~1.8 mm/µL as a starting estimate),
   and `mm_to_ul: 1.0` on the CubOS side so `volume_ul` passes through as
   microlitres instead of being converted twice.
5. **The sensed tip pickup** (§8.8) whenever the tip-seating question comes back.

---

## 9. 2026-09-15: the resistor went in, the firmware was taught to listen, and the driver said nothing

Ben fitted a **10 kΩ** bridge between A0 (`RX_PIN`) and A1 (`TX_PIN`) — the
single-wire UART arrangement §8.10 step 1 asked for. 10 kΩ rather than 1 kΩ is
electrically fine: the driver has to pull the line low against the Arduino's
idle-high push-pull output, which is 0.5 mA at 5 V, and at 9600 baud
(104 µs/bit) the RC of 10 kΩ against tens of picofarads is not close to
mattering.

### 9.1 The resistor alone changes nothing, and campaign 26 proved it

The trio ran that day with the bridge in place and produced a plunger trace
**byte-for-byte identical** to campaigns 77 and 83: `HOME` back in 0.520 s
(back-off only), the two downward commands stepping, all four upward commands
refused in ~0.107 s.

That is expected rather than disappointing. `setupMotor()` only ever *writes*
TMC2209 registers and checks none of them, and no command in `Interface.cpp`
exposed driver state — so the readback path the bridge creates had nothing
asking it a question. **The bridge is necessary and was not sufficient.**

### 9.2 So the firmware was taught to ask

`CMD_PIPETTE_DRIVER_STATUS = 29`, added in the same reflash as the p20
constants (see [`../firmware/README.md`](../firmware/README.md)), returns
`comm` / `flags` / `current_scaling`. Five consecutive reads, immediately after
the flash:

```
OK:{"msg":"Driver status","v":[0.00,0.00,-1.00]}
```

`comm = 0` is unambiguous — the library's `isCommunicating()` is
`getVersion() == VERSION`, so 0 means the driver did not return a valid version
byte. Not "replied but unconfigured"; **no reply at all**.

### 9.3 What that rules in and out

Every register write `setupMotor()` makes has therefore never landed, on any
run since this rig was built. The driver has been running on power-on defaults
throughout. Two consequences, pulling in opposite directions:

* **`setOperationModeToSerial()` never landed either**, so `i_scale_analog` is
  still 1 and the **VREF potentiometer is in circuit**. The §4 worry — that
  correcting the UART pin would strand the driver at minimum current with its
  output stage off — is therefore *not* what is happening. That hypothesis is
  now dead.
* `setMicrostepsPerStep(16)` never landed, so MS1/MS2 straps decide. Their
  default is 1/8, which is half of what `STEPS_PER_MM 1592.0` assumes — the
  same 2× the firmware already contradicts itself about in
  `int backOffSteps = 796; // this is equal to 1mm`. **Check the first
  successful move against a ruler.**

### 9.4 The discriminator, and it takes two minutes

With the driver idle and powered, try to turn the plunger by hand.

| holding torque | reading | next |
| --- | --- | --- |
| **none** | no coil current at all | VM at the driver's screw terminal (12 V; VDD from the Arduino is logic only and the board enumerates happily without VM), then the VREF pot, then coil continuity |
| **present** | the driver is powered and energised, so `comm = 0` is the UART path alone | confirm PDN_UART really lands on **A1**, and the bridge |

The new `flags` word reports `open_load_a`/`open_load_b` directly, which would
settle the coil question without a meter — but those bits come back *in a
reply*, so they only mean anything once `comm` is non-zero. Fix `comm` first.

### 9.5 What is now closed

| §8.10 step | state |
| --- | --- |
| 1. bridge + `getStatus()` | **done** — bridge fitted, firmware reads it, answer is `comm = 0` |
| 2. generation | **done** — `P20 GEN2`, off the body in `../results/pi5_des4_provision_20260914/pipette_label_p20_gen2.jpg` |
| 3. `RUN_CURRENT_PERCENT` → 17 | **done** (and `HOLD_CURRENT_PERCENT` → 10, which is forced: the library maps hold independently of run, so 30 against 17 would draw more standing still than moving). Heat sink still to fit. |
| 4. volume constants | **done** — `MAX_VOLUME` 20, `MIN_VOLUME` 1, `UL_TO_MM` 1.8 in firmware; `mm_to_ul: 1.0` in CubOS. `UL_TO_MM` is a starting estimate awaiting a gravimetric calibration. |
| 5. sensed tip pickup | still open |

One more thing settled in passing: the P300-shaped `ASPIRATE` behaviour is
gone. `MIN_VOLUME` 5.0 was why `ASPIRATE 0.5` always landed at 35.45
(0.5 clamped up to 5, then `36.0 − 5 × 0.1098`). With the p20 constants a
commanded 20 µL is `ASPIRATE 20.0` → 36.0 mm → plunger at 0.0, full scale.

---

## 10. 2026-09-17: Ursa's review, two retractions, and the P20 GEN2 numbers

Alex Carlson reviewed sections 1–9 against Cubware, `PANDA_Arduino`, the
janelia TMC2209 source, CubOS `origin/main`, Opentrons `shared-data`, the
Opentrons OT-2 open-hardware schematics and the Adafruit 6121 schematic
([byu-vcl issue #133, 2026-09-17][ursa-review]). Two of the conclusions in
this document do not survive that review. Both are corrected in place below
rather than edited out, because the reasoning that produced them is the
reasoning to avoid repeating.

[ursa-review]: https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5719634392

### 10.1 🔴 RETRACTED: `comm = 0` was never evidence of anything

Sections 9.2–9.5 treated `CMD_PIPETTE_DRIVER_STATUS` returning `comm = 0` as
proof that *none of `setupMotor()`'s register writes had ever landed*, and
built on that to retract the section-4 hypothesis. **That inference is
unsound.** A read over `SoftwareSerial` on an AVR cannot succeed with this
library at all, whatever the wiring:

- AVR `SoftwareSerial::write()` runs `cli()` for the duration of each
  transmitted byte, so the Arduino never receives its own transmission back.
  The janelia README says software serial "should only be used for
  unidirectional communication" for exactly this reason.
- `TMC2209::sendDatagramBidirectional()` waits up to
  `ECHO_DELAY_MAX_MICROSECONDS` (4000) for `datagram_size` bytes and then
  **discards them as echo**. With no echo, the bytes that arrive in that
  window are the driver's 8-byte reply: the first 4 are thrown away,
  `readReply()` then waits for 8 more, times out, retries 5x, and
  `isCommunicating()` — which is `getVersion() == 0x21` — reports false.

So `comm = 0` is the *structural* outcome on an Uno. It says nothing about
whether the driver is powered, configured, or wired. **Writes need no echo
and may have been landing the whole time**, which means
`RUN_CURRENT_PERCENT`, `setMicrostepsPerStep(16)` and `enable()` may all
have been in effect, and the section-4 hypothesis is *not* excluded after
all.

The lesson worth keeping: a diagnostic that cannot return a positive result
is not a diagnostic. `getDriverDiagnostics()` was added in good faith and
then trusted without first asking whether its success path was reachable.

Two changes are needed before that reading means anything:

1. **`tmc2209-softwareserial-read.patch`** (in `cubos/patches/`) — skips the
   echo wait-and-discard block when `software_serial_ptr_` is set. Written and
   built; see §10.4 for why it is not yet on the board.
2. **The bridge resistor has to move to the TX side.** Per TMC2209 datasheet
   §4.3 fig 4.1 and the janelia "coupled" wiring diagram: `A1 -> 1k -> node`,
   with `A0` and `PDN_UART` connected *directly* to the node. With `A1` wired
   straight to `PDN_UART` and the resistor only on the `A0` leg, the
   Arduino's push-pull TX shorts out the driver's reply. **This is a bench
   change, and the library patch alone will not produce a valid read without
   it.**

### 10.2 🔴 CORRECTED: the sense resistor is 0.05 Ω, not 0.11 Ω

§8.4 assumed 0.11 Ω "the common value" and scaled every current figure from
it. Ursa read the actual value off the Adafruit 6121 schematic: `R1`, `R2` =
**0.05 Ω / 0.25 W**. Recomputing, with `vsense = 0` (`enableVSense()` is
never called) and the library's `CS = map(percent, 0, 100, 0, 31)`:

```
I_rms = ((CS+1)/32) * (0.325 / (0.05 + 0.02)) / sqrt(2) = ((CS+1)/32) * 3.283 A
```

| `RUN_CURRENT_PERCENT` | CS | I_rms | I_peak | |
|---|---|---|---|---|
| 50 | 15 | 1.64 A | **2.32 A** | BU original — over the board's 2 A rating |
| 17 | 5 | 0.62 A | 0.87 A | VCL 2026-09-15 |
| **20** | **6** | **0.72 A** | **1.02 A** | **matches Opentrons `plungerCurrent` 1.0 A** |
| 5 | 1 | 0.21 A | 0.29 A | matches Opentrons `idleCurrent` 0.3 A |

So the 50 that shipped from BU was worse than §8.4 said — over the
*breakout's* rating, not merely over the motor's. And the 500 mA peak figure
§8.4 used as the target is **science-jubilee's Duet choice, not Opentrons'**.
Opentrons' own `p20_single_v2.x` definition runs the plunger at
`plungerCurrent: 1.0 A` and idles at `idleCurrent: 0.3 A`. Those are the
numbers to match for this pipette, and 17 was conservative rather than
correct.

### 10.3 Other facts from the 6121 schematic worth recording

- Header order: `1 VDD, 2 GND, 3 DIR, 4 STEP, 5 MS1, 6 MS2, 7 DIAG, 8 INDEX,
  9 UART, 10 EN`.
- **`EN` has a 20 kΩ pull-down**, so the driver is enabled even with the `EN`
  wire absent. Moving `EN` from A3 to A4 was still right, but §3's claim that
  a mis-landed `EN` would leave the driver dead does not hold for this board.
- `MS1`/`MS2` have no board pulls and the chip pulls them down internally →
  **1/8 microstepping and UART address 0**. Address 0 matches the library
  default, so addressing was never the problem. 1/8 does mean a commanded
  millimetre travels two, if the microstep write never lands — the open
  question of §7.
- **The VREF pot is fed from the chip's own `5VOUT` through 33 kΩ, and
  `5VOUT` is generated from `VM` only.** `VCCIO` does not power the analogue
  side.

That last point is the important one, and it is why **`VM` remains the first
thing to measure**. With `VM` absent: `5VOUT` is dead, so VREF is zero, so
coil current is zero; the driver cannot reply on UART; and every `STEP`/`DIR`
command is still accepted and acked by the Arduino. One cause, every symptom
— including Ben's 2026-09-17 bench result that **the plunger moves freely by
hand with the driver powered and idle**, i.e. no holding torque, i.e. no coil
current.

### 10.4 The pipette is a P20 GEN2, and the numbers now agree in all three places

Ben confirmed the model on 2026-09-17 (and the label is legible in campaign
36's `cam0_csi0` frame). Ursa's records said P300 GEN2, and the flashed
2026-09-15 image was a hybrid — P300 plunger planes with P20 volume limits.
Resolved in favour of the P20 GEN2.

Authority is Opentrons `shared-data/pipette/definitions/1/pipetteModelSpecs.json`,
keys `p20_single_v2.0`/`2.1`/`2.2` (all three carry identical positions).
Opentrons states plunger planes as signed offsets in a frame whose `top` is
the home reference; both CubOS and the PANDA firmware measure distance
*downward* from home, so each value is `top - <field>` with `top = 19.5`:

| | Opentrons field | P20 GEN2 | → firmware / CubOS | was (a P300 value) |
|---|---|---|---|---|
| prime / bottom | `bottom` −8.5 | | **28.0** | 36.0 firmware, 5.0 CubOS |
| blowout | `blowout` −13 | | **32.5** | 44.0 firmware, 7.0 CubOS |
| drop tip | `dropTip` −27 | | **46.5** | 55.0 firmware, 10.0 CubOS |
| mm per µL | `ulPerMm` → 0.746 µL/mm | | **1.34** | 1.8 firmware |
| max / min volume | | 20 / 1 µL | **20.0 / 1.0** | 300 / 5 before 2026-09-15 |

Two cross-checks that the 1.34 is real rather than assumed:

- `1 / 0.746 = 1.34`, and 0.746 µL/mm is the asymptote of Opentrons' own
  `ulPerMm` table for `p20_single_v2.1`. The same arithmetic on the P300 gives
  9.1 µL/mm, which is where the old `UL_TO_MM 0.1098` came from — so the
  method reproduces the one number in this file that was independently
  calibrated.
- A full-scale 20 µL aspirate travels `20 * 1.34 = 26.8 mm` up from
  `PRIME_POSITION 28.0`, landing the plunger at **1.2 mm** — inside the 28 mm
  top-to-bottom stroke with a small dead band, which is how Opentrons has it.
  The old 1.8 was just `36.0 / 20`, i.e. derived from a P300 plane.

**Every one of the three planes moved down, so every commanded plunger travel
is now shorter than before** — the safe direction — and the ordering
`0 < prime < blowout < drop_tip` that `aspirate`, `dispense` and `moveTo`
rely on is preserved.

The CubOS-side placeholders mattered more than a mis-scaling: `prime 5.0`,
`blowout 7.0` and `drop_tip 10.0` are sent to the firmware as **absolute
`MOVE_TO` targets**, so they were aiming 23–36 mm short of the planes a P20
GEN2 plunger actually uses. Those are corrected in
`cubos/patches/p20-gen2-plunger-constants.patch` (which replaces
`p20-mm-to-ul-passthrough.patch` and keeps its `mm_to_ul = 1.0`
pass-through), and the firmware side in
`cubos/firmware/panda-arduino-p20-and-driver-status.patch`. The two now carry
the same three numbers.

⚠️ **Still nominal, not calibrated.** These are Opentrons' figures for the
model, not a measurement of this unit. `UL_TO_MM` needs a gravimetric check
once liquid actually moves.

⚠️ **One P20 GEN2 number was deliberately *not* propagated.** Opentrons gives
`tipLength: 31.15` and `tipOverlap: 8.25`, i.e. a **22.9 mm** tip extension
below the nozzle for their 10/20 µL tips — against the **35.0 mm** in
`ben_6vials_tiprack.yaml`, which Ben measured on the tip actually in the rack
on 2026-08-06. The 35 is a measurement of a possibly different tip and every
piece of validated tipped geometry on this branch depends on it (the hover
clamp's 89/124 planes, the `height: -35.0` insert, `travel_z: 87`). It was
left alone. If a caliper check ever says 22.9, all of that Z geometry has to
be re-derived — it is not a one-line change.

### 10.5 What is now closed, and what is not

| | |
|---|---|
| ✅ Pipette identity | P20 GEN2, confirmed by Ben and by the label in campaign 36's frame |
| ✅ Plunger planes | agree in the firmware and in CubOS, both from Opentrons |
| ✅ Volume conversion | single conversion, in the firmware; `mm_to_ul = 1.0` on the CubOS side |
| ✅ Run/hold current | set to Opentrons' `plungerCurrent` / `idleCurrent`, on the real 0.05 Ω |
| ✅ `comm = 0` | explained, and no longer read as evidence |
| ✅ Limit-switch convention | Opentrons `pipette-endstop.sch` shows an Omron D2F-L-A wired COM→signal, NC→GND, so the firmware's `INPUT_PULLUP` + `HIGH == triggered` is right and **D9 reading HIGH really does mean the loop is open** |
| ✅ 10-pin coil pairing | corroborated by Opentrons `pipette-main.sch`. Ribbon pin 5 is the EEPROM's 5 V input — leave it unconnected |
| 🔴 No coil current | Ben's hand test on 2026-09-17: the plunger moves freely with the driver powered. **Measure 12 V at the `VM` screw terminal first** — §10.3 explains why that one fault produces every symptom |
| 🔴 UART readback | needs the library patch *and* the resistor moved to the TX side |
| 🔴 Limit-switch loop | independent fault. Until D9 reads LOW the plunger cannot retract, whatever the motor does |
| ✅ Serial link to the Arduino | was blocking; **recovered on a USB replug**, 8/8 clean round-trips — see §11.5 |
| ✅ The `F` light | a *direction* indicator, not a fault light. There is no fault LED on this board — see §11.1 |
| ✅ The current pot | eliminated: it is at maximum and there is still no torque, which is what makes `VM` the prime suspect — see §11.3 |

---

## 11. 2026-09-17 (later): the `F` light is not a fault light, and the pot is not the problem

Three bench observations from Ben, and they move the diagnosis forward more
than anything since the hand test.

### 11.1 🔴 `F` on the 6121 means *Forward*, not *Fault*

There is **no fault LED on this board.** Adafruit's guide lists exactly three,
and all three are on logic pins the Arduino drives:

| silk | colour | tied to | lit when |
|---|---|---|---|
| **`F`** | green | **`DIR`** | "the motor is being driven counterclockwise when the DIR pin is low" |
| **`B`** | red | **`DIR`** | "the motor is being driven clockwise when the DIR pin is high" |
| **`S`** | yellow | **`STEP`** | "the motor driver is being moved" |

`DIAG` — the pin that *would* report a short, an open load or an
over-temperature shutdown — is broken out on header pin 7 and has **no LED**
and no wire. So the only way to see a driver fault on this build remains the
UART readback of §10.1, which needs both the library patch and the resistor
moved to the TX side.

**What the LEDs do give, for free, is the commanded direction.** The firmware
sets `DIR` once per move and holds it:

| firmware action | `DIR` | LED |
|---|---|---|
| `homePipette()` seek (upward) | LOW | **green `F`** |
| `homePipette()` back-off (796 steps) | HIGH | red `B` |
| `moveTo()` / `aspirate()` descending | HIGH | red `B` |
| `moveTo()` retracting | LOW | **green `F`** |

That turns the 2026-09-01 open question — *does `HOME` seek toward the switch
or away from it?* — into something answerable by eye without a meter, and it
gives a second confirmation that `STEP` pulses arrive (`S` flickers) to sit
alongside the raw-step probe of §6.

### 11.2 The green `F` blinking bright/dim was almost certainly the reflash attempts

Green `F` is lit by the Arduino **sinking** the `DIR` net, so its brightness
tracks the state of pin `A3`:

| `A3` | green `F` |
|---|---|
| driven LOW by the running sketch | **bright** |
| high-impedance — during reset, and while the bootloader runs | **dim** (leakage only) |
| driven HIGH | off, red `B` lit instead |

The observation was made during the session that spent several minutes
running `avrdude` at four different baud rates. Every `avrdude` attempt
toggles `DTR`, which **resets the ATmega328P**; the bootloader does not touch
`A3`, so the pin floats until `setupPipette()` runs `pinMode(DIR_PIN, OUTPUT)`
and drives it LOW. One reset cycle = one dim/bright transition. No plunger
motion was commanded in that session at all, so `DIR` was never deliberately
changed — the resets are the only mechanism available.

Benign, and not a fault report. The alternative reading — a `VDD` rail sagging
under load and modulating the LED — is worth ruling out, and the test is
trivial: **watch `F` while nothing is being sent to the board.** Steady
brightness means the rail is fine.

### 11.3 The pot is at maximum, and that makes the no-torque result much stronger

Ben reports the trimmer turned fully clockwise, which Adafruit describes as
*"when all the way to the right we can get to up to 2A max."*

Combined with the hand test, the two facts are far more informative than
either alone. `i_scale_analog` is still 1 (no UART write has ever been
confirmed to land), so **the pot is the only thing setting coil current** —
and it is at its maximum. At maximum VREF this motor should have obvious
holding torque. It has none. Since VREF is fed from the chip's own `5VOUT`,
and `5VOUT` is generated from `VM` alone (§10.3), zero torque at maximum pot
means **VREF is zero, which means `5VOUT` is dead, which means `VM` is
missing** — or the chip is dead. The pot has been eliminated as a suspect by
being at the wrong end of its range to explain anything.

**So: do not change it yet.** It is currently the setting most likely to
reveal torque, and turning it down can only muddy the measurement. Two
caveats for once there *is* torque:

- **In standalone mode, back it off before any sustained move.** Full scale on
  this board's real 0.05 Ω sense resistors is ~3.3 A rms, well past both the
  breakout's 2 A rating and the P20 GEN2's `plungerCurrent: 1.0 A`. Set it by
  measuring, not by counting turns: **VREF ≈ 0.55 V gives ~1.0 A peak**
  (`I_rms = (VREF / 2.5) x 3.283 A`, so 0.72 A rms = 1.02 A peak — the same
  current `RUN_CURRENT_PERCENT 20` asks for). Note `VREF` is not broken out on
  the 10-pin header, so this means probing the trimmer's wiper. If full
  clockwise measures below 0.55 V, the pot cannot over-current the motor and
  the question is moot.
- **Once UART works the pot stops mattering entirely.** The first register
  write is `setOperationModeToSerial()`, which clears `i_scale_analog` and
  takes the pot out of circuit; `RUN_CURRENT_PERCENT` governs from then on.

⚠️ Fit the Adafruit 1515 heat sink before running at any of these currents.

### 11.4 How to measure `VM` — the one measurement that settles it

Any multimeter, DC volts (`V⎓`), 20 V range or autoranging. The driver and the
Pi stay powered.

1. **Black probe on the `−` screw terminal, red probe on the `+` screw
   terminal** of the two-pin motor-supply block. Probe the **screw heads or
   the bare wire clamped under them** — not the insulation, not the barrel
   jack, and not the brick's own output, because the whole point is to find out
   whether 12 V survives the journey.
2. Expect **11.4–12.6 V**.

| reading | meaning |
|---|---|
| ~12 V | `VM` present. The fault is downstream — VREF, or the coils. |
| **0 V** | nothing reaching the board: supply off, broken wire, or a screw clamped on insulation rather than copper |
| ~−12 V | polarity reversed |
| a few volts, or collapses when a move is commanded | bad joint, or a supply that cannot hold up under step load |

Three checks that cost nothing while the meter is out:

- **Tug each wire in the terminal block.** A screw tightened onto insulation
  is the single most common cause of a 0 V reading, and it looks perfectly
  installed.
- **Continuity** (Ω or the beeper) from the supply's output conductor to the
  matching screw terminal: under ~1 Ω.
- **Measure again while a bounded move is commanded**, to catch a rail that
  reads 12 V at idle and collapses under load.
- **The same tug test on the four coil terminals** (`1A/1B/2A/2B`). If `VM` is
  good and there is still no torque, an insulation-clamped coil screw does
  exactly that. Then the coil resistance check of §8.6 applies: blue–red and
  black–green a few to a few tens of ohms, blue–black open.

Safety: 12 V is not a shock hazard, but do not let the probe tips bridge `+`
to `−` or to an adjacent pad — that is a dead short through the supply. With
no meter to hand, the crude substitute is to put a known 12 V load (a fan, an
LED strip) on the same leads and see whether it runs; that tests the supply
and the wiring but not the terminal block itself.

### 11.5 The Arduino serial link recovered on a replug

The corruption recorded in `cubos/results/pipette_p20gen2_20260917/` is gone.
Both `/dev/ttyACM0` and `/dev/ttyUSB0` re-enumerated at 2026-09-17 16:45
lab-local, and a read-only probe immediately afterwards returned **8 clean
`STATUS` round-trips out of 8**, against 0 of 25 earlier the same day:

```
banner: b'OK:Ready\r\n'
  [0..7] OK  dt=0.01s  OK:{"homed":0,"pos":0.00,"max_vol":20.00}
```

So of the four candidate causes listed at the time, the first — *unplug and
replug the USB cable; a `USBDEVFS_RESET` from the Pi is not a power cycle* —
was the fix. `max_vol: 20.00` confirms the 2026-09-15 p20 image is still what
is running; the P20 GEN2 image of §10.4 was never flashed, because `avrdude`
could not sync while the link was broken. **That reflash is now unblocked.**

`CMD 29` still reports `comm = 0`, exactly as §10.1 predicts: the running
image does not carry the SoftwareSerial read fix, so the read cannot succeed
regardless of the wiring. It stays uninformative until the reflash *and* the
resistor move are both done.

## 12. 2026-09-18: `VM` measures 13 V — the leading hypothesis is dead

Ben measured the stepper driver's motor-supply screw heads: **13 V**. That
retires the hypothesis §11.3 put at the top of the list, and it is the single
most useful measurement taken on this problem so far, because of what it
combines with.

### 12.1 What it rules out

The TMC2209 generates its own internal logic and reference supplies from `VM`
through an on-chip regulator; `VCC_IO` (the Arduino's 5 V) powers only the pin
drivers. On the Adafruit 6121 the VREF trimmer is fed from that internal
`5VOUT`, so **everything analogue on the chip hangs off `VM`**. A missing `VM`
was the one fault that explained silence, no holding torque and `comm = 0`
simultaneously.

13 V at the terminal means that story is finished. Three of its consequences
should now be true, and can be checked:

- the chip's internal `5VOUT` should be up,
- VREF should be live, and with the pot at **full clockwise** it should be near
  its maximum,
- with `i_scale_analog` still `1` (power-on default — no UART write has been
  confirmed to land) VREF *is* what sets coil current, so it should be high.

A healthy TMC2209 in that state also has a default hold current: power-on
`IHOLD = 16`, `IRUN = 31`, `toff = 3` (output stage enabled). It should hold
the plunger noticeably.

**It does not.** Ben's hand test on 2026-09-17 — *"pulling the plunger
manually, it moves freely when plugged in and on"* — still stands. So something
between the powered chip and the motor windings is broken.

⚠️ Two caveats on the reading itself. First, confirm it was the **2-pin motor
supply block**, not a coil pair. Second, 13 V measured with no current flowing
confirms the supply is *present*, not that it can *hold up* — but that cannot
be tested until current actually flows, so it is not worth chasing now.

### 12.2 What is left, and how to tell them apart

Three candidates remain. All three are settled with a multimeter; none needs
the machine running.

**A — the coil path is open.** Terminal screws clamped on insulation, a bad
crimp at the pipette's FC-10P, or a broken ribbon conductor. This has been the
standing suspicion since §6 and the §8 review supports it (silence with *no*
buzzing is open coils; mis-*paired* coils buzz and vibrate).

> **Power off.** Probe the driver's own coil terminals, so the measurement
> covers the whole path driver → ribbon → pipette motor:
> ```
> 1A – 1B      a few to a few tens of ohms      coil A
> 2A – 2B      a few to a few tens of ohms      coil B
> 1A – 2A      open                             the coils are isolated
> ```
> Both pairs open ⇒ the connector or the crimps, not the pinout. One pair open
> ⇒ that pair's path. Tug each wire in the terminal block while you are there;
> a screw tightened onto insulation looks perfectly installed.

**B — `EN` is held high.** The output stage is off whenever `EN` is high,
whatever `VM` and VREF do.

> **Power on, sketch running.** Measure `EN` **at the driver pin**, not at the
> Arduino header — it must be ≈ 0 V. And confirm the wire lands on **A4**.
> §2 found Cubware's diagram puts `EN` on A3, which is the `DIR` pin: wired
> that way the driver is energised for one direction of travel and dead for
> the other. The board's 20 kΩ pull-down means an *absent* `EN` wire is
> harmless; a *wrong* one is not.

**C — the driver chip is dead.** Its internal regulator, or the output stage.

> **Power on.** Measure **VREF at the trimmer wiper**. With `VM` = 13 V it
> should be well above zero and near maximum with the pot fully clockwise. If
> VREF reads ≈ 0 V, the internal `5VOUT` is not being generated and the chip
> should be replaced. A weak corroborating check: a TMC2209 with `VM` applied
> draws a little even idle, so a chip that is stone cold after minutes powered
> is consistent with a dead regulator.

Order: **A, then B, then C** — A is power-off and needs no live probing, and it
is the hypothesis with the most independent support.

### 12.3 The software half is now worth doing for its own sake

Candidate A can be answered *without the meter*, by the chip itself. The
janelia library exposes `open_load_a` / `open_load_b` in the driver status
register, and `CMD_PIPETTE_DRIVER_STATUS` (29) already returns them — but the
read cannot succeed until two things are done together:

1. **Flash the P20 GEN2 image** at `cubos/firmware/panda_vcl_p20gen2_20260917.hex`,
   which carries `tmc2209-softwareserial-read.patch`. Without it a
   `SoftwareSerial` read on an AVR is structurally impossible (§10.1), which
   is why `comm = 0` has been uninformative every time it has been reported.
2. **Move the bridge resistor to the TX side** — `A1 → 1 kΩ → node`, with `A0`
   and `PDN_UART` directly on the node. On the RX side the Arduino's push-pull
   TX shorts out the driver's reply.

With both done, `comm > 0` becomes meaningful and `flags` answers A directly.
Until then neither number carries information.

### 12.4 Status after this measurement

| | |
|---|---|
| Arduino STEP output | ✅ proven — 1592 steps at the commanded rate (§6) |
| Arduino pin map | ✅ corrected 2026-09-01 (§2); `EN` on A4 **still unverified electrically** |
| 10-pin header layout | ✅ agrees across three sources (§3, §8) |
| `VM` at the driver | ✅ **13 V, measured 2026-09-18** |
| VREF / `5VOUT` | ❓ unmeasured — §12.2 C |
| `EN` at the driver pin | ❓ unmeasured — §12.2 B |
| coil continuity | ❓ unmeasured — §12.2 A |
| coil current | 🔴 none — no holding torque, no buzzing |
| TMC2209 UART readback | 🔴 `comm = 0`, uninformative until §12.3 |
| pipette limit switch | ✅ reading **clear** — confirmed twice over (26.3 s seek, and retractions now execute; §13) |
| up-direction gate | ✅ **open** as of campaign 54 — `MOVE_TO` retractions emit steps (§13) |
| firmware aspirate constants | 🔴 still the 2026-09-15 image (`PRIME 36.0`, `UL_TO_MM 1.8`); P20 GEN2 hex built, not flashed (§13.3) |

---

## 13. 2026-09-18 (campaign 54): the up-direction gate is open — retractions execute

First run in which **every** plunger command produced a distance-scaling round
trip, including a retraction. Full trace in
[`cubos/results/pipette_test_20260918/`](../results/pipette_test_20260918/README.md).

### 13.1 The measurement

| command | dt | commanded distance | implied rate |
|---|---|---|---|
| `MOVE_TO 0.0` (from 0.0) | 0.006 s | 0 mm | correct no-op |
| `ASPIRATE 20.0` | 13.131 s | down 36 + **up 36** | — |
| `MOVE_TO 32.5` | 21.546 s | **+32.5 mm** | 0.663 s/mm |
| `MOVE_TO 46.5` | 9.288 s | **+14.0 mm** | 0.663 s/mm |
| `MOVE_TO 28.0` | 12.267 s | **−18.5 mm** | 0.663 s/mm |

The three `MOVE_TO` commands reproduce their commanded distances to within
0.01 mm at one consistent rate, and the last of them is a **retraction**. In
every run from 2026-09-15 to 2026-09-17 a retraction returned a flat ~0.107 s
having emitted no steps — the `stepMotor()` up-direction gate firing on
`digitalRead(PIPETTE_LIMIT_PIN) == HIGH`.

`ASPIRATE` corroborates independently: `aspirate()` descends to
`PRIME_POSITION` and then ascends by `volume × UL_TO_MM`, and the ascent is the
gated leg. Campaigns 26 and 36 measured **5.962 s** (descent only); campaign 54
measured **13.131 s** — both legs. Which is also why `MOVE_TO 32.5` measured
exactly 32.5 mm of travel: the aspirate landed back at 0.0 as the arithmetic
says it should.

### 13.2 What it proves, and what it does not

`stepMotor()` bit-bangs STEP and counts loop iterations. No encoder, no current
sense, **no feedback**. A distance-scaling round trip proves the **Arduino
emitted the steps**; it says nothing about whether the motor turned. §12's three
multimeter checks — coil continuity, `EN` at the driver pin, VREF at the wiper —
are unchanged and are still the critical path.

What *has* changed is the firmware gate, and therefore the diagnostic value of
`HOME`. D9 reads **LOW** (loop closed): retractions are no longer refused, and
`HOME` runs its full 50 000-step (≈31.4 mm) budget — 26.346 s and 26.348 s on
two attempts, identical to the centisecond, which is a seek that exhausts its
budget rather than one that terminates on a switch.

**So `HOME` is now a live test of the motor.** If the motor is turning, a 31 mm
seek should reach the switch; it does not. The `F`/`B` LEDs give the direction
for free (§11: green `F` = DIR LOW = the homing direction) and `HOME` runs for
26 s, so one observed `HOME` distinguishes *motor not turning* from *seeking
away from the switch*.

### 13.3 🔴 The firmware's aspirate constants are now the weak link

`MOVE_TO` targets come from CubOS — `p20-gen2-plunger-constants` supplies prime
28.0, blowout 32.5, drop_tip 46.5, and all three appear verbatim in the trace.
But `ASPIRATE` is computed **inside the firmware**, and the running 2026-09-15
image still has `PRIME_POSITION 36.0` (a P300 plane) and `UL_TO_MM 1.8` (an
estimate). A P20 GEN2's bottom is 28.0.

So *if* the motor is turning, `aspirate` drives the plunger 8 mm past its
bottom on every call. `cubos/firmware/panda_vcl_p20gen2_20260917.hex` is built
and fixes exactly this (`PRIME_POSITION 28.0`, `UL_TO_MM 1.34`,
`RUN_CURRENT_PERCENT 20`, `HOLD_CURRENT_PERCENT 5`). It is **not flashed**.

This was harmless while the up-leg was refused — the plunger never came back, so
the descent was the only motion. Now that both legs run, it matters.

---

## 14. 2026-09-18: the LEDs corroborate the trace, and `DIAG`/`INDEX` are the way in

Ben watched the driver board during campaign 54:

> *"B red for the majority while the Pipette was running commands, then F green
> after the drop tip."*

### 14.1 That matches the trace command-for-command

`B` and `F` are both on the **DIR** net (§11.1), and `moveTo()` latches DIR at the
start of a move and holds it until the next one. Against campaign 54's timings:

| UTC | protocol step | command | direction | DIR | LED |
|---|---|---|---|---|---|
| 00:39:08 / 00:39:35 | connect | `HOME` ×2, 26.3 s each | up (seek) | LOW | `F` green |
| 00:41:21 | 3 `pick_up_tip` | `MOVE_TO 0.0`, 0 mm | none | unchanged | unchanged |
| 00:41:48 | 4 `aspirate` | `ASPIRATE 20.0`, 36 down then 36 up | both | HIGH→LOW | red → green |
| 00:43:13 | 8 `blowout` | `MOVE_TO 32.5`, **+32.5 mm** | down | HIGH | **`B` red** |
| 00:43:34 | 9 `drop_tip` | `MOVE_TO 46.5`, **+14.0 mm** | down | HIGH | **`B` red** |
| 00:43:47 | 9 `drop_tip` | `MOVE_TO 28.0`, **−18.5 mm** | **up** | **LOW** | **`F` green** |

Red spans `blowout` and `drop_tip`'s first leg — 00:43:13 → 00:43:44, 30.8 s of the
last 47 s of plunger activity. Green begins at 00:43:47, `drop_tip`'s **second**
leg, the only upward `MOVE_TO` in the protocol, and latches to the end of the run.

So the observation is an independent, human-eye confirmation of the serial trace,
down to which command flipped the pin.

**But be precise about what it proves.** Both LEDs are driven by the *Arduino's*
pins. They establish that STEP and DIR arrive at the board's input pins with the
right polarity and timing. Nothing on the chip's side of those pins drives them,
so they say nothing about whether the TMC2209 is alive.

### 14.2 The running image, now proven rather than inferred

`avrdude -U flash:v:` against all three candidates, 2026-09-18:

| image | verify |
|---|---|
| `panda_vcl_p20_20260915.hex` | ✅ **17370 bytes of flash verified** |
| `flash_20260915T220346Z.hex` (stock backup) | ❌ mismatch at byte `0x0e` |
| `panda_vcl_p20gen2_20260917.hex` | ❌ mismatch at byte `0x0e` |

§13.3's reading was right: the P20 GEN2 image is not flashed, so the firmware's
`PRIME_POSITION 36.0` / `UL_TO_MM 1.8` are still live while CubOS sends the
Opentrons planes as absolute targets.

### 14.3 🔑 `DIAG` and `INDEX` answer this without UART

Both are broken out on the [Adafruit 6121](https://learn.adafruit.com/adafruit-tmc2209-stepper-motor-driver-breakout-board/pinouts),
neither has an LED, and neither has ever been looked at:

- **`DIAG`** — *"driven high if there is a problem causing the motor driver to not
  be able to work properly."* A fault flag the chip raises on its own.
- **`INDEX`** — *"driven high when the microstep counter is in it's zero
  position."* It therefore **pulses as the chip consumes STEP pulses**,
  independently of whether any current reaches the coils.

`INDEX` is precisely the discriminator the UART readback was wanted for:

| STEP arriving | `INDEX` | reading |
|---|---|---|
| yes | **changing** | the chip is alive and counting → the fault is downstream: the coil path, or current set to zero |
| yes | **dead flat** | the chip is not processing STEP → dead, disabled, or STEP not landing on its pin |

`EN` is broken out too — *"Pull this pin high to disable the output to the
motors"* — and should measure ~0 V at the **driver's** pin, not at the Arduino
header. §12.2 B has wanted that measurement since 2026-09-18 morning; it is
unchanged, and these two join it.

[`cubos/tools/pipette_driver_measure.py`](../tools/pipette_driver_measure.py) opens
a bounded, direction-labelled stepping window — 6 mm out and 6 mm back at 200
steps/s, ~48 s per leg — so all three can be probed while the plunger is actually
being driven. It refuses to open the window if the limit switch reads asserted,
since the return leg would be refused and the plunger would ratchet outward.

### 14.4 `comm = 0`, read three more times

```
cmd 29 DRIVER_STATUS  dt=0.209s  OK:{"msg":"Driver status","v":[0.00,0.00,-1.00]}   (×3)
```

Still carries no information, and §14.2 supplies the second independent reason
why: the running image predates `tmc2209-softwareserial-read.patch`, and without
it the janelia library's read path cannot succeed on an AVR at all — `write()`
runs `cli()` so the Arduino never hears its own transmission, and
`sendDatagramBidirectional()` then discards the first four bytes of the driver's
*real* reply as if they were that echo. The bridge-resistor topology (§12.3) is
the first reason. Both have to be fixed before `comm > 0` is even possible.

### 14.5 Order to work in

1. **`EN` at the driver pin** — ~0 V expected; ~5 V means the output stage is off.
2. **`DIAG`** — ~0 V expected; high means the chip has a fault it is reporting.
3. **`INDEX` during a driven leg** — must change. This is the split in §14.3.
4. **Coil resistance at the four screw terminals**, ribbon attached, power off:
   `1A`–`1B` and `2A`–`2B` a few to a few tens of ohms, `1A`–`2A` open. This tests
   the whole path including crimps and screw clamping.
5. **The yellow `S` LED**, free while the rest is happening: at 2500 steps/s it
   reads as a steady dim glow rather than a flicker, but it must look *different*
   during a move. If it never changes, STEP is not reaching the board and the
   fault is one wire.

---

## 15. Which stepper driver? The gantry and the plunger are separate systems

Asked on 2026-09-21 ([#171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171)):
*could the stepper driver have anything to do with the issues above?* The
answer depends on which motion is meant, because this machine has **two
independent stepper systems that share no signal path**.

| | gantry X / Y / Z | pipette plunger |
|---|---|---|
| commanded by | GRBL controller board | Arduino Uno R3 `2341:0043` |
| serial port | `/dev/ttyUSB0` (CH340 `1a86:7523`) | `/dev/ttyACM0` |
| stepper drivers | on the GRBL board, one per axis | **Adafruit 6121 TMC2209 breakout**, one |
| step generation | GRBL firmware | `stepMotor()` bit-banging `STEP` (A2) / `DIR` (A3) |
| scaling | `$100`–`$102` = 400 steps/mm | `STEPS_PER_MM 1592` |
| limits | `$130`–`$132` = 409 / 309 / 124, switches on `Pn:` | one switch on D9 |
| config | `serial_port:` + `grbl_settings:` | `instruments.pipette.port:` |

Both ports are listed side by side in
[`cub_xl_ben_pipette_capper.yaml`](../configs/gantry/cub_xl_ben_pipette_capper.yaml);
`/dev/ttyACM0` also carries the capper's electromagnet and line-break sensor.

**The TMC2209 has no electrical connection to any gantry axis.** It cannot make
an axis move, refuse to move, overshoot a limit, or miss a switch. So for the
gantry symptoms the answer is no, and in each case the cause is already
established and is something else:

| symptom | cause | written up in |
|---|---|---|
| campaign 46 — `ALARM:9`, capper never descended | gantry stepper supply switched off | §appendix of the [SOP](../../SOP/raspberry-pi-cubos-setup.md) |
| campaign 50 — `decap vial_1` failed 3× | same power state; campaign 54 captured first try at byte-identical coordinates | [`pipette_test_20260917b/`](../results/pipette_test_20260917b/README.md) |
| Y driven 33 mm past its stop | `$X` + `G91` jog against a counter 282 mm stale | [`y_overrun_20260918/`](../results/y_overrun_20260918/README.md) |
| campaign 36 — closing `home` failed | same supply dropout | [`pipette_test_20260916/`](../results/pipette_test_20260916/README.md) |
| no run could start (2026-09-18) | `$20=0` on the controller | [`pipette_test_20260918/`](../results/pipette_test_20260918/README.md) |

### 15.1 For the plunger the answer is yes, and it is now one of two things

Campaign 54 (§13) and the LED observation (§14) closed out everything upstream
of the driver's input pins, and Ben's 13 V measurement (§12) closed out its
supply. What remains, in full:

```
  Arduino STEP/DIR output    PROVEN  1592 steps at the commanded rate (§6)
  polarity and timing        PROVEN  B/F LEDs match the trace command-for-command (§14.1)
  limit-switch gate          OPEN    retractions emit steps (§13)
  VM at the screw terminal   13 V    (§12)
  ---------------------------------- everything above this line is eliminated
  TMC2209 chip / EN / VREF   ?       candidates B and C
  coil path to the windings  ?       candidate A
```

Only candidates **B** (`EN` held high, output stage off) and **C** (dead chip or
dead internal regulator) are the driver itself; **A** is the wiring downstream
of its output terminals. §14.5 is the order to work in, and `DIAG` / `INDEX` on
the 6121 split B+C from A without needing the UART readback to work.

### 15.2 The one way the driver could touch the gantry: shared power

Not through signals — through the supply. `rpi-5-des4` already shares power
with the gantry (switching the gantry supply reboots the Pi, observed
2026-09-17), so if the driver's 12 V comes off that same brick or strip, a
short or a latched fault at the driver could brown out the gantry and present
as a motion fault.

**Unverified, and worth confirming**: whether the TMC2209's motor supply is the
same source as the gantry's. Two things argue against it mattering today — the
terminal read a healthy 13 V, and campaign 54 ran 12/12 clean with the driver
connected — but a supply shared with a suspect board is worth knowing about
before the next fault is diagnosed.

---

## 16. 2026-09-21: the four measurements land — the coils are open and the chip is flagging a fault

Ben took the §14.5 measurements. All four, verbatim:

```
EN     = 0 V
INDEX  = 0 V
DIAG   = 5 V

1A-1B = 4.5 kOhm    2A-2B = 7.6 kOhm     driver connected, Arduino not powering it
                                          (unchanged when the Arduino is connected)
1A-1B = 0.55 kOhm   2A-2B = 5 kOhm       nothing powered
```

Plus an LED observation: *"While only plugged into the Arduino, F is bright
green. While only plugged into the wall, F is dimmer."*

Two of these settle things. Taken together they move the diagnosis from
"one of three candidates" to "**A is confirmed and C is now live**."

### 16.1 ✅ `EN` = 0 V — candidate B is eliminated

The output stage is not being held off. §12.2 B is closed.

One thing it does **not** prove: §10.3 found `EN` carries a **20 kΩ pull-down on
the board**, so 0 V is what an *absent* `EN` wire reads too. The measurement
rules out "held high"; it does not confirm the wire landed on A4. That
distinction does not matter while the pin reads 0 V, and it is recorded so
nobody re-derives it.

### 16.2 🔴 The resistance readings are not coil readings — and that is conclusive

Every value is in the hundreds of ohms to kilohms. **A stepper coil is a few
ohms to a few tens of ohms.** The lowest reading here, 550 Ω, is still one to
two orders of magnitude too high.

The reason that is conclusive rather than merely suspicious is the direction of
the in-circuit error. Probing at the driver's own terminals leaves the
TMC2209's output stage permanently in parallel with whatever the coil path
contributes, and **parallel paths can only pull a reading down, never up**:

```
measured = R_coil_path  ||  R_everything_else   <=  min(R_coil_path, R_everything_else)
```

So a measured 550 Ω puts a **floor** of 550 Ω on the real path. A 10–30 Ω
winding across those terminals would have dragged the reading to 10–30 Ω no
matter what else was in parallel. **There is no coil across either terminal
pair.**

Two corroborating details in the same data:

- **The readings move with power state** — 1A–1B goes 0.55 kΩ → 4.5 kΩ when the
  supply is on. A copper winding does not change resistance by 8× because a
  power supply was switched on. What is being measured is semiconductor
  junctions and leakage on the driver board, not a motor.
- **Therefore only the unpowered readings are even valid.** An ohmmeter injects
  a known current and measures the resulting voltage; an external supply
  corrupts that outright. Use 0.55 kΩ and 5 kΩ, and they are still both far too
  high.

⚠️ **The §12.2 A / §14.5 instruction was imprecise and this is where it shows.**
"Probe the driver's own coil terminals, ribbon attached" was written to cover
the whole path in one measurement, and it does — but only in the *open*
direction. Had it read low, the reading could have been the driver's own output
stage rather than the coil, and it would have proved nothing. It also cannot
localise the break. §16.4 has the corrected procedure.

### 16.3 🔑 The cheapest explanation is a terminal-block swap, and it is free to check

Before assuming anything is broken: **coil pairs split across the two terminal
blocks produce exactly this measurement, with a perfectly healthy motor.**

If the wires landed as `1A`/`2A` = coil A's two ends and `1B`/`2B` = coil B's,
then the driver's phase-1 output sees one end of coil A and one end of coil B
with nothing between them — an open circuit — and phase 2 sees the same. Both
`1A`–`1B` and `2A`–`2B` read high; the motor is fine; and the machine is
**silent with no buzzing**, which is the signature this pipette has had all
along. §8 noted that mis-*paired* coils buzz and vibrate — that is true of
coils swapped *within* the driver's view, and it is a different fault from a
pair split *across* the blocks, which the driver simply cannot energise.

Two ways to check, neither needing the machine:

**By grouping — the form of the check that does not depend on wire colour.**
Only one thing has to be true:

> **Both ends of one winding land in `1A`+`1B`, and both ends of the other
> land in `2A`+`2B`.**

Which winding goes to which block, and which way round within a block, change
only the direction the plunger travels. **Splitting one winding across the two
blocks is the fault**, and it is what produces an open circuit on both phases.

Trace by **pipette header pin**, which §8.6 fixes unambiguously: pins **3 and
4** are one winding, pins **1 and 2** are the other. The two wires coming from
3 and 4 must sit in the same block as each other. On the Adafruit 6121 the
positions are silkscreened `1A`, `1B`, `2A`, `2B` — however many physical
blocks that is on the board, the labels are what matter.

⚠️ **Colour is a hint, not the test.** `blue`+`red` = coil A and `black`+`green`
= coil B is the JST housing order of the OT-2 motor's **own four leads inside
the pipette**, recorded by science-jubilee's photograph (§8.6). Cubware's page
gives pin numbers only and **names no wire colours at all**. So those colours
appear at the driver's terminals only if the harness happens to carry them end
to end; across a rainbow ribbon, a re-crimped FC-10P or a re-terminated run
they mean nothing. When the colours are not traceable, go straight to the
meter row below — it is a 30-second check and it is the authoritative one.

**With the meter, power off.** Measure the two cross pairs, which §12.2 asked
for and this round did not report:

| pair | if it reads a few to a few tens of ohms |
|---|---|
| `1A`–`2A` | the pairs are split across the blocks — **swap two wires and it is fixed** |
| `1B`–`2B` | same conclusion |
| both high, and `1A`–`1B` / `2A`–`2B` high | the break is upstream: ribbon, crimps, FC-10P, or the motor → §16.4 |

### 16.4 If it is not the terminal block: where the break is, narrowed

**Take the ribbon out of the driver's screw terminals first.** That removes the
output stage from the measurement and makes the numbers mean what they say.
Then, power off:

1. **At the loose ribbon ends** — covers ribbon + FC-10P + motor. Blue–red and
   black–green each a few to a few tens of ohms.
2. **If (1) is open, at the pipette's own 10-pin header** — splits "the ribbon
   and its crimps" from "the motor". Per §8.6's map, coil A is header pins
   **3–4** and coil B is pins **1–2**. Header good + ribbon ends open ⇒ the
   ribbon, its crimps or the FC-10P. Header open ⇒ the motor or its internal
   connection.

🔑 **One narrowing the existing data already supplies for free.** The limit
switch shares the same FC-10P and the same ribbon, and it currently reads
**closed** — D9 is LOW, confirmed twice over by the 26.3 s full-budget seek and
by campaign 54's retractions executing (§13). So the connector is **not** wholly
unseated; at least two conductors are making contact. And those two are pins 6
and 7, which §8.6 places in rows 3 and 4, while all four coil conductors are in
**rows 1 and 2, the two nearest the pipette tip**. A connector lifted or
mis-seated at the tip end reproduces precisely this split. **Reseat the FC-10P
and re-measure** before condemning anything.

### 16.5 🔴 `DIAG` = 5 V — the chip is reporting a fault

Expected ~0 V. Adafruit's own description of the pin: *"driven high if there is
a problem causing the motor driver to not be able to work properly."* On the
TMC2209 `DIAG` is the driver-error output, asserted by the same conditions that
shut the output stage down — overtemperature, a short to ground or to supply on
either phase, or charge-pump undervoltage. Note that **open load is not one of
them**: `ola`/`olb` are informational bits in `DRV_STATUS` and do not drive
`DIAG`. So this is saying something beyond §16.2's open coils.

`INDEX` = 0 V supports reading it as a real assertion rather than a floating
pin: `DIAG` and `INDEX` are adjacent outputs of the same chip, and two pins
sitting at **opposite rails** is what driven outputs look like. A floating pair
would not reliably split that way.

Which specific error bit it is cannot be read without the UART path working —
that is exactly what `DRV_STATUS` would say, and it needs both the P20 GEN2
flash and the bridge resistor moved to the TX side (§12.3). But the flag alone
promotes candidate **C** from theoretical to live.

### 16.6 The two findings are plausibly one story, and it sets the repair order

The board has been running with the VREF pot **fully clockwise** since at least
2026-09-17, and in standalone mode — which it has always been in, because no
UART write has ever landed — the pot is the only thing setting current. §11.3
puts full scale on this board's 0.05 Ω sense resistors at **~3.3 A rms**, past
the breakout's own 2 A rating.

Chopping at that current into an **open** load, repeatedly, across many
sessions, is a well-known way to damage a stepper driver's output stage: the
chopper drives toward a current it can never reach, the outputs swing to the
rails, and flyback energy has nowhere to go. So the likely sequence is **open
coil path first, damaged driver as a consequence** — which makes the order
matter:

1. **Fix the coil path** (§16.3, then §16.4). Confirm with the meter, ribbon out
   of the terminals.
2. **Turn the VREF pot down before powering the driver again.** See §16.7 —
   this is the step that protects a *replacement* driver.
3. **Re-check `DIAG`.** Clear, with a real load and sane current ⇒ the chip
   survived. Still high ⇒ replace the board.
4. **Do not do 3 before 1.** Powering a suspect driver back into an open load is
   how the replacement gets destroyed too.

### 16.7 🔴 CORRECTION: flashing the P20 GEN2 image does *not* lower the run current

This has been stated as a benefit of the flash in the firmware README, in
[`pipette-setup-and-troubleshooting.md`](./pipette-setup-and-troubleshooting.md)
and in PR #228's description: *"drops run current from ~2.3 A to ~1.02 A peak."*

**That only holds once UART works.** `RUN_CURRENT_PERCENT` reaches the chip
through `setRunCurrent()`, which is a UART register write, and `comm = 0` means
no register write has ever been confirmed to land. `i_scale_analog` is still at
its power-on default of 1, so **the VREF trimmer is the only thing setting coil
current** — and it is at maximum.

So the action that actually reduces the current is **turning the pot down**, not
flashing. §11.3 has the target: **VREF ≈ 0.55 V at the wiper gives ~1.0 A
peak**, matching Opentrons' `plungerCurrent`. For a first re-test after a repair
there is no reason to start there — wind it well down, confirm the motor turns
at all, and creep up. ⚠️ Fit the Adafruit 1515 heat sink before any sustained
move.

The flash is still worth doing, for the two reasons it was always worth doing:
the firmware's `aspirate` constants are still P300-derived (§13.3), and it
carries `tmc2209-softwareserial-read.patch` without which `DRV_STATUS` — and
with it the specific `DIAG` cause — cannot be read at all.

### 16.8 `INDEX` = 0 V, and what it is still missing

§14.3 made `INDEX` the discriminator, on the basis that it pulses as the chip
consumes STEP pulses regardless of coil current. The reading as reported is
**not yet usable**, because it is not recorded whether it was taken *during a
driven leg*. At rest, 0 V is the expected and uninformative value — the
microstep counter simply is not at its zero position.

[`../tools/pipette_driver_measure.py`](../tools/pipette_driver_measure.py) exists
for this: it opens a bounded, direction-labelled stepping window so the pin can
be watched while steps are being consumed. On a DMM a changing `INDEX` reads as
a fluctuating mid-scale value rather than a clean 0 or 5 V.

It has also dropped in importance. It was the way to split "chip alive, fault
downstream" from "chip not processing STEP" — and §16.2 has now answered the
downstream half directly, while §16.5 has the chip telling us about itself.

### 16.9 The `F` LED observation is benign, and mildly informative

*"Only plugged into the Arduino, F is bright green. Only plugged into the wall,
F is dimmer."*

Consistent with §11.1: `F` sits on the `DIR` net and lights when the Arduino
**sinks** A3 low. Arduino connected with the sketch running ⇒ A3 actively driven
LOW ⇒ bright. Arduino absent ⇒ `DIR` floats ⇒ leakage only ⇒ dim. Nothing
anomalous.

The mildly useful part: the LED glows *at all* on wall power alone, which
requires a live rail on its anode side. If that rail is derived from the chip's
own `5VOUT` — generated from `VM`, per §10.3 — then the internal regulator is
working and the chip is not stone dead, which would favour "alive but in a
latched error state" over "completely dead." ⚠️ **Weak evidence**: the 6121's
LED supply source is not established here, and a dim LED is a poor instrument.
**VREF at the trimmer wiper** (§12.2 C) is the measurement that settles it, and
it is now the most valuable one still outstanding: healthy VREF ⇒ the regulator
is fine and `DIAG` is flagging a latched output-stage fault; VREF ≈ 0 ⇒ replace
the board.

### 16.10 Status after these four measurements

| | |
|---|---|
| Arduino STEP/DIR output | ✅ proven (§6), polarity corroborated by the LEDs (§14.1) |
| `VM` at the driver | ✅ 13 V (§12) |
| `EN` at the driver pin | ✅ **0 V — candidate B eliminated** |
| coil path to the windings | 🔴 **OPEN, both pairs — candidate A confirmed** (§16.2) |
| ↳ split across terminal blocks? | ❓ **check first** — `1A`–`2A` / `1B`–`2B` unmeasured (§16.3) |
| ↳ ribbon / crimps / FC-10P / motor | ❓ needs the ribbon out of the terminals (§16.4) |
| TMC2209 `DIAG` | 🔴 **asserted — the chip is reporting a driver error** (§16.5) |
| VREF / `5VOUT` | ❓ still unmeasured — now the most valuable remaining probe (§16.9) |
| `INDEX` | ❓ 0 V, but not known to have been taken during a driven leg (§16.8) |
| VREF pot | 🔴 **at maximum, ~3.3 A rms full scale.** Turn it down before re-powering (§16.7) |
| TMC2209 UART readback | 🔴 `comm = 0`; needs the GEN2 flash **and** the TX-side bridge (§12.3) |
| limit-switch loop | ✅ closed — and it proves the FC-10P is not wholly unseated (§16.4) |

## 17. 2026-09-22: the cross pairs land — one short explains `DIAG`, and the terminal-block hypothesis is dead

Reported by Ben, with the wire-to-terminal map §16.3 asked for:

```
1B <- Blue      1A - 1B    2.7  kOhm
1A <- Red       2A - 2B    2.7  MOhm
2A <- Green     1A - 2A    0    Ohm      <-- dead short
2B <- Black     1B - 2B    3.6  MOhm
```

Two findings, and the second is the first measurement in this whole hunt that
*explains* a previously unexplained one.

### 17.1 ✅ The grouping is correct — §16.3's leading hypothesis is eliminated

Against §8.6's header map — coil A = pins 3 (red) + 4 (blue), coil B = pins 1
(green) + 2 (black):

| driver terminal | wire | header pin | winding | lands in |
| --- | --- | --- | --- | --- |
| `1A` | red | 3 | A | block 1 |
| `1B` | blue | 4 | A | block 1 |
| `2A` | green | 1 | B | block 2 |
| `2B` | black | 2 | B | block 2 |

Both ends of coil A are in `1A`+`1B`; both ends of coil B are in `2A`+`2B`.
That is exactly the rule §16.3 set out, so **the coil pairs are *not* split
across the two blocks** and the cheap "swap two wires" fix does not apply. The
hypothesis §16.3 led with is retired on Ben's own colour map, without needing
the meter to settle it.

### 17.2 🔴 `1A`–`2A` = 0 Ω is a dead short between the two driver bridges

`1A` and `2A` are outputs of two independent DMOS bridges driving two isolated
windings. §12.2 predicted them **open**. Zero ohms means red (header pin 3) and
green (header pin 1) are joined by a near-zero-resistance path — one end of
coil A tied to one end of coil B, which the driver sees as `OA1` shorted to
`OA2`.

**All four readings are self-consistent with exactly that one topology.** Taking
red ≡ green:

| pair | predicted if red ≡ green | measured |
| --- | --- | --- |
| red–blue (`1A`–`1B`) | whatever the blue path is | 2.7 kΩ |
| green–black (`2A`–`2B`) | whatever the black path is | 2.7 MΩ |
| blue–black (`1B`–`2B`) | blue–red + red–black ≈ 2.7 k + 2.7 M ≈ 2.7 MΩ | 3.6 MΩ |
| red–green (`1A`–`2A`) | ≈ 0 | **0 Ω** |

The blue–black row closing to the right order of magnitude is the check that
matters; megohm readings on a DMM are range-dependent and noisy, so 2.7 M vs
3.6 M is agreement, not a discrepancy.

**And no winding appears in any measurement.** A stepper coil is a few to a few
tens of ohms. The lowest reading here is 2.7 kΩ — two orders of magnitude out —
so §16.2's conclusion stands: the coil path is open *as well as* shorted.

⚠️ **Do not read the specific kΩ/MΩ values as resistances.** `2A`–`2B` was
5 kΩ on 2026-09-21 and 2.7 MΩ now; `1A`–`1B` went 0.55 kΩ → 2.7 kΩ. Copper does
not change by 540× between sessions. Those numbers are leakage and semiconductor
junction paths on the driver board, and the only information in them is "far too
high to be a winding."

### 17.3 🔑 The short explains `DIAG` = 5 V

§16.5 established that `DIAG` is asserted by overtemperature, a short to ground
or to supply on either phase, or charge-pump undervoltage — and explicitly *not*
by open load. It had no candidate cause. It does now.

With `OA1` shorted to `OA2`, the instant bridge 1 pulls its output toward `VM`
while bridge 2 pulls its output toward GND, `VM` is connected to ground through
two conducting MOSFETs and nothing else. That is the short-circuit condition the
TMC2209's protection exists to catch: it latches the output stage off and raises
`DIAG`, and the latch holds until the driver is reset.

So the two symptoms collapse into one mechanism. **This also means `DIAG` may
clear once the short is gone** — which is why the repair order below puts the
wiring before any verdict on the chip.

### 17.4 🔴 It is also how the output stage dies — so the order is now a safety matter

The VREF pot has been at full clockwise since at least 2026-09-17, and in
standalone mode (which this board has always been in, §16.7) the pot is the only
thing setting current — full scale on the 6121's 0.05 Ω sense resistors is
~3.3 A rms. The chopper has been driving into a phase-to-phase short at that
setting, repeatedly, across every session since.

> 🔴 **Do not power the driver again until the short is cleared and the pot is
> turned down.** A bridge-to-bridge short with a maxed current setting is the
> textbook way to destroy a stepper driver's output stage — including a brand
> new replacement, within seconds of powering it up.

**Repair order:**

1. **Find and clear the short** (§17.5). Power off throughout.
2. **Confirm both windings read a few to a few tens of ohms.**
3. **Turn the VREF pot well down** — below the ≈ 0.55 V wiper target for ~1.0 A
   peak for a first re-test, then creep up. Fit the 1515 heat sink.
4. **Then power up and re-check `DIAG`.** Clear ⇒ the chip survived the abuse.
   Still 5 V ⇒ replace the board.

Doing 4 before 1 is how the replacement joins the first one.

### 17.5 Where the short is, cheapest first

**0. Sanity-check the meter.** Probes touched together should read the leads'
own resistance (typically 0.1–0.5 Ω, or 0.0 on a meter that zeroes them);
probes apart should read open. This takes five seconds and it matters, because
a flat `0` through a length of harness is suspiciously perfect — an accidental
bridge normally shows a fraction of an ohm, and a meter left in continuity mode
or with a stuck range reads 0 everywhere. `1B`–`2B` reading 3.6 MΩ argues the
meter is fine, so this is a formality rather than a doubt.

**1. The screw terminals.** Loosen *only* red and green, lift them clear of the
block so they cannot touch anything, and re-measure red–green at the wire ends.

- **Clears** ⇒ the short was at the block: a stray strand, over-stripped
  insulation, or the two wires touching above the terminal. Re-strip, re-seat,
  done.
- **Still 0 Ω** ⇒ downstream of the block. Go to 2.

**2. Unplug the FC-10P at the pipette** and measure red–green at the harness
end (connector body included on the harness side).

- **Still 0 Ω** ⇒ the short is in the harness — ribbon, crimps, the connector
  body, or the machine-end junction. §8.7 already nominates that junction, where
  four motor wires and two switch wires are soldered onto ten ribbon conductors,
  as the least keyed and least documented joint in the chain; a solder bridge
  there between the red and green conductors is exactly this reading.
- **Clears** ⇒ the short is at the pipette's header or inside the motor. Go to 3.

**3. 🔑 Measure at the pipette's own 10-pin header, FC-10P off.** This is the
single most valuable measurement remaining, because it removes every crimp, the
ribbon and the connector from the picture and tests the motor alone. Per §8.6:

| pins | expect |
| --- | --- |
| **3 – 4** (coil A) | a few to a few tens of ohms |
| **1 – 2** (coil B) | a few to a few tens of ohms |
| **1 – 3** | open |

Both windings in range and 1–3 open ⇒ **the motor is healthy and the entire
fault is in the harness**, which is the good outcome and the one the evidence
currently favours (see §17.6).

### 17.6 A single mechanical cause is available, and the motor is probably fine

A winding-to-winding short *inside* the motor is a poor fit for this data: it
would show low resistances across the shorted pair, not megohms. What fits is an
external fault, and there is a coherent single-cause story for both the short
and the opens.

§8.6 puts the odd pins in one column of the header and the even pins in the
other, with pin 1 at the tip end. So **green (1) and red (3) are adjacent
contacts in one column, and black (2) and blue (4) are adjacent contacts in the
other** — and all four sit in the two rows nearest the pipette tip. A connector
mis-seated or skewed at that end can bridge two adjacent contacts in one column
while the other column makes no contact at all: green–red shorted, black–blue
open. Equally, one bad rework at the machine-end solder junction gives a red–green
bridge alongside cold joints on blue and black.

🔑 **And the limit switch is the reason to suspect the tip end specifically.** It
shares the same ribbon and the same FC-10P, and it reads **closed** (D9 LOW,
confirmed by the 26.3 s full-budget seek and by campaign 54's retractions
executing, §13). Its two conductors are pins 6 and 7, which §8.6 places in rows
3 and 4 — the rows *furthest* from the tip. So the connector is making good
contact at one end and failing at the other, which is precisely what a lift or
skew at the tip end looks like. **Reseat the FC-10P before condemning anything.**

### 17.7 Status after the cross pairs

| | |
|---|---|
| Arduino STEP/DIR output | ✅ proven (§6), polarity corroborated by the LEDs (§14.1) |
| `VM` at the driver | ✅ 13 V (§12) |
| `EN` at the driver pin | ✅ 0 V — candidate B eliminated (§16.1) |
| coil grouping in the terminals | ✅ **correct — §16.3's hypothesis retired** (§17.1) |
| coil path to the windings | 🔴 **OPEN, both pairs** (§16.2, §17.2) |
| `1A`–`2A` | 🔴 **0 Ω — dead short between the two bridges** (§17.2) |
| TMC2209 `DIAG` | 🔴 asserted — **now explained by the short** (§17.3) |
| motor windings at the header | ❓ **the measurement to take next** (§17.5 step 3) |
| where the short is | ❓ block → harness → header, in that order (§17.5) |
| VREF / `5VOUT` | ❓ still unmeasured (§16.9) — but the pot must come **down** first (§17.4) |
| `INDEX` | ❓ 0 V, not known to have been taken during a driven leg (§16.8) |
| TMC2209 UART readback | 🔴 `comm = 0`; needs the GEN2 flash **and** the TX-side bridge (§12.3) |
| whether the chip survived | ❓ unanswerable until the short is cleared (§17.4) |

## 18. 2026-09-23: the ribbon comes out and the windings appear — the motor is fine

Reported by Ben. The pipette had always reached the driver board through a
10-pin ribbon and its FC-10P connector. He bypassed that entirely and wired the
pipette to the driver's screw terminals **directly**:

```
1A - 1B    4.3 Ohm
2A - 2B    3.7 Ohm
```

### 18.1 🔑 Those are real stepper windings, and they are the first ever measured

§17.5 step 3 set the expected band as *"a few to a few tens of ohms"* for a
healthy winding. Both readings land in it. Every previous measurement of the
same two pairs was kΩ to MΩ — two to five orders of magnitude out — and that is
what "the coil path is open" meant.

Nothing about the motor changed between the two sets of readings. The only thing
that changed is that the harness is no longer in the path. So:

> **The motor is healthy. The entire coil fault was in the ribbon harness —
> the ribbon, its crimps, the FC-10P, or the machine-end solder junction.**

That is §17.6's favoured outcome, reached by substitution rather than by the
localisation sequence of §17.5. It is the good ending: no motor to replace, and
the suspect is a part that can be rebuilt.

**The in-circuit caveat now argues for the reading rather than against it.**
§16.2 made the point that probing at the driver's own terminals leaves the
TMC2209's output stage permanently in parallel with the coil path, and that
parallel paths can only pull a reading *down*, never up — which is why a high
reading was conclusive and a low one would not have been. A 4.3 Ω reading with
the driver still attached is exactly what a real winding looks like through that
parallel path: the winding dominates, as it must.

The 0.6 Ω spread between the two pairs is not a concern. A DMM's own leads are
typically 0.1–0.5 Ω, and contact resistance at a screw terminal varies by more
than that between probings; low-ohms accuracy near zero is the worst part of a
handheld meter's range. If a precise figure is ever wanted, zero the leads (or
subtract a probes-touched reading) and measure at the pipette's header.

### 18.2 ❓ The one reading still missing: is the short gone too?

§17.2's `1A`–`2A` = 0 Ω is the other half of the fault, and the new set does not
speak to it. **Both cross pairs need re-measuring on the direct wiring, power
off:**

| pair | expect | if it instead reads ≈ 0 Ω |
| --- | --- | --- |
| `1A` – `2A` | **open** | the short is not in the harness — it is on the driver board itself |
| `1B` – `2B` | **open** | same |

The short was almost certainly in the harness and has left with it — a
phase-to-phase bridge inside a motor would have shown as a low resistance across
the shorted pair rather than the megohms §17.2 recorded. But this is the
measurement that decides whether the driver board is still a suspect or is now
the *only* suspect, and it costs ten seconds.

### 18.3 🔴 The VREF pot is dangerous now in a way it has never been before

Until today the driver's load was either open or shorted. A chopper driving an
open load delivers no current no matter what VREF asks for, and a shorted one
latches the protection off. **With ~4 Ω windings actually attached, the chopper
can finally deliver the current the pot is asking for**, and the pot has been at
full clockwise since at least 2026-09-17 — ~3.3 A rms full scale on this board's
0.05 Ω sense resistors (§11.3), into a motor Opentrons runs at
`plungerCurrent: 1.0 A` peak and whose breakout is rated 2 A.

> 🔴 **Turn the pot down before the driver is powered up again.** This is no
> longer a tidiness item. It is the first power-up at which the setting can do
> damage, and the thing it would damage is the motor that has just been proven
> good.

§11.3 has the target: **VREF ≈ 0.55 V at the wiper gives ~1.0 A peak**
(`I_rms = (VREF / 2.5) × 3.283 A`). For a first re-test wind it well below
that — enough to confirm the shaft turns at all — then creep up. Fit the
Adafruit 1515 heat sink. The pot remains the only thing setting current until
UART works (§16.7); `RUN_CURRENT_PERCENT` in the firmware does not apply.

### 18.4 🔴 Power-cycle `VM` before reading `DIAG`, or the verdict will be wrong

The TMC2209's short-circuit protection **latches** the output stage off; it is
cleared by disabling and re-enabling the driver — a `CHOPCONF.toff` write over
UART, which is unavailable here (§12.3) — or by removing and restoring `VM`.

So a `DIAG` read taken without a full 12 V power cycle may be reporting a latch
set days ago by a short that no longer exists. That would read as "the chip is
dead" when the chip is fine.

**Order:**

1. Confirm both cross pairs are open (§18.2). Power off.
2. Turn the VREF pot well down (§18.3).
3. **Fully power-cycle the 12 V** — off, a few seconds, on.
4. *Then* read `DIAG`. ≈ 0 V ⇒ the chip survived. Still 5 V ⇒ replace the board.

### 18.5 ⚠️ The limit switch probably went out with the ribbon

Pins **6 and 7** — the switch return and its signal — rode the same ribbon and
the same FC-10P as the four coil conductors (§8.6). If only the coil wires were
direct-wired, D9 is now unconnected, and `setupPipette()` configures it
`INPUT_PULLUP` with **HIGH meaning triggered** (§1, §6.2). An unconnected pin
idles HIGH, so the firmware will read the switch as **asserted**, and:

- `stepMotor()`'s gate closes on the **up** direction — every retraction is
  refused in ~0.107 s having emitted no steps
- `HOME` returns a fake success in ~0.52 s, running only its 796-step back-off

That is the pre-2026-09-18 signature, and it would look like a regression rather
than a wiring consequence. It is checkable in seconds:

```bash
~/CubOS/.venv/bin/python ~/byu-vcl/cubos/tools/pipette_driver_probe.py /dev/ttyACM0 --switch
```

`pipette_driver_measure.py` also refuses to open its stepping window while the
switch reads asserted — by design, since the return leg would be refused and the
plunger would ratchet outward — so that refusal is itself the answer.

**Reconnecting pins 6 and 7 is part of the direct-wire job**, not an optional
extra: without them the plunger is a one-way ratchet again.

### 18.6 ⚠️ Direction may have inverted, and homing is how it shows

Swapping the two ends *within* a pair reverses which way the plunger travels.
Mechanically that is harmless and `DIR` handles it — but `homePipette()` seeks
with `DIR` LOW (green `F` lit, §11.1), and if that direction is now *away* from
the switch, `HOME` can never reach it however many 26 s legs it runs.

science-jubilee's own homing instructions give the tell, and it is a visual one:
watch the drive shaft during the seek, and **if the tip ejector starts to
engage, the direction is inverted** (§8.9). The fix is to swap the two wires of
one pair — either pair, not both.

### 18.7 🔴 Flash the P20 GEN2 image before any `aspirate` — this just became blocking

§10.4's reflash has been queued behind "the first real movement" since
2026-09-17. A turning motor makes it a prerequisite rather than a nicety.

`MOVE_TO` targets come from CubOS, which already carries the Opentrons P20 GEN2
planes, so `blowout` and `drop_tip` land where CubOS asks. **`aspirate` does
not** — it is computed inside the firmware, and `aspirate()` drives *down* to
`PRIME_POSITION` before its metered ascent. The running 2026-09-15 image still
carries the P300-derived `PRIME_POSITION 36.0`; a P20 GEN2's bottom is **28.0**.

While the plunger was silent that discrepancy cost nothing. With a motor that
turns, **every `aspirate` call drives the plunger 8 mm past its mechanical
bottom**, stalling against the stop for the rest of the move.

So: no protocol `aspirate` on the current image. Flashing
`cubos/firmware/panda_vcl_p20gen2_20260917.hex` closes it and also carries
`tmc2209-softwareserial-read.patch`, without which `DRV_STATUS` — and the
specific bit behind `DIAG` — cannot be read at all. ⚠️ It does **not** lower the
run current while UART is down; only the pot does (§16.7).

### 18.8 The first-movement test, and what it finally unlocks

A bounded bench move is the right first test — no gantry motion, no protocol,
nothing that needs the pipette mounted:

```bash
~/CubOS/.venv/bin/python ~/byu-vcl/cubos/tools/pipette_driver_measure.py --move
```

6 mm out, 6 mm back at 200 steps/s, direction-labelled, always returning to
where it started. What to watch for, in order of how much each one settles:

| observation | meaning |
| --- | --- |
| **the shaft turns** | the hunt is over — everything from §1 onward was correct and the harness was the fault |
| **holding torque at rest** | coil current is flowing; the two-minute discriminator of §11.2 finally passes |
| yellow `S` LED changes during the move | STEP pulses reaching the board (free confirmation) |
| `INDEX` fluctuating mid-scale on a DMM | the microstep counter is running — §16.8's reading becomes usable at last |
| **measure the 6 mm with a ruler** | 🔑 `setMicrostepsPerStep(16)` is a UART write that has never landed, so MS1/MS2 decide and their default is 1/8 — **half** what `STEPS_PER_MM 1592` assumes. Expect a possible 2× error, and this is the moment to catch it |

⚠️ **The direct wiring is a bench configuration, not a machine one.** The ribbon
was also the flexible tether that let the pipette ride the moving head. Solid
wire into screw terminals will not survive gantry motion, and pulling a terminal
out mid-run recreates exactly the open circuit that has cost the last three
weeks. Bench-test on the direct wiring; rebuild or repair the harness before the
pipette goes back on the gantry.

### 18.9 Status after the direct-wire measurement

| | |
|---|---|
| Arduino STEP/DIR output | ✅ proven (§6), polarity corroborated by the LEDs (§14.1) |
| `VM` at the driver | ✅ 13 V (§12) |
| `EN` at the driver pin | ✅ 0 V (§16.1) |
| coil grouping in the terminals | ✅ correct (§17.1) |
| **the motor windings** | ✅ **4.3 Ω / 3.7 Ω — HEALTHY (§18.1)** |
| **the ribbon harness** | 🔴 **condemned — it carried the open coil path** |
| `1A`–`2A` / `1B`–`2B` on the direct wiring | ❓ **the next measurement (§18.2)** |
| VREF pot | 🔴 at maximum, and now into a real load — **turn it down first** (§18.3) |
| TMC2209 `DIAG` | ❓ 5 V, but **power-cycle `VM` before believing it** (§18.4) |
| limit switch / D9 | ⚠️ likely unconnected with the ribbon out (§18.5) |
| plunger direction | ⚠️ may have inverted; homing is the tell (§18.6) |
| firmware `aspirate` planes | 🔴 **flash the GEN2 image before any aspirate** (§18.7) |
| microstepping vs. `STEPS_PER_MM` | ❓ ruler check, available for the first time (§18.8) |
| TMC2209 UART readback | 🔴 `comm = 0`; needs the GEN2 flash **and** the TX-side bridge (§12.3) |

## 19. 2026-09-24: the coil path is clean — and `DIAG` survives a power cycle

Reported by Ben, on the direct wiring of §18:

```
1A - 2A    megohms          <- was 0 Ohm through the ribbon (S17.2)
1B - 2B    megohms
pot        turned down
DIAG       5 V, still, after cutting the power and plugging it back in
```

### 19.1 ✅ The short left with the ribbon — the driver board is exonerated as its source

§18.2 asked for exactly these two readings and set the criterion: open means
the short was in the harness, ≈ 0 Ω means it is on the driver board and the
board becomes the only suspect. **They are open.**

Put beside §18.1's 4.3 Ω and 3.7 Ω windings, the coil side is now completely
healthy for the first time since this began:

| pair | through the ribbon | direct |
| --- | --- | --- |
| `1A` – `1B` | 0.55 kΩ → 2.7 kΩ | **4.3 Ω** ✅ winding |
| `2A` – `2B` | 5 kΩ → 2.7 MΩ | **3.7 Ω** ✅ winding |
| `1A` – `2A` | **0 Ω** 🔴 | **MΩ** ✅ isolated |
| `1B` – `2B` | 3.6 MΩ | **MΩ** ✅ isolated |

Two windings, correct resistance, properly isolated from each other. The
ribbon harness carried **both** faults — the open coil path *and* the
phase-to-phase short — and both left with it. §17's localisation sequence and
§16.3's terminal-block hypothesis are now fully retired; the substitution
answered everything they were built to find.

> The entire coil-side diagnosis is closed. The motor is good, the terminals
> are good, and the harness is condemned.

### 19.2 🔴 And that makes a damaged output stage the *leading* explanation for `DIAG`

§16.6 offered "open coil path first, damaged driver as a consequence" as a
plausible story. §17.2's 0 Ω made it a concrete mechanism, and §19.1 now
confirms that mechanism was real and present for weeks:

- the ribbon presented a **phase-to-phase short** at the driver's outputs
- the VREF pot has been at **full clockwise** since at least 2026-09-17 —
  ~3.3 A rms full scale on this board's 0.05 Ω sense resistors (§11.3)
- `EN` has been at 0 V (§16.1), so the chip was **enabled** and chopping into
  that short every time the board was powered
- across many sessions

Driving a chopper into a bridge-to-bridge short at a maxed current setting is a
textbook way to destroy a stepper driver's output stage. This is no longer a
long shot; it is the hypothesis the evidence most supports. **A replacement
Adafruit 6121 is worth ordering now regardless of how the tests below come
out** — every remaining question about this pipette needs a known-good driver
to answer, and the part is inexpensive next to another week of sessions.

### 19.3 ❓ But five things can hold `DIAG` high that are not a dead chip

§18.4 said "still 5 V after a clean power cycle ⇒ replace the board." That is
still the destination, but the criterion was written loosely and the power
cycle Ben performed does not yet satisfy all of it. Five candidates, each cheap
to eliminate, roughly in order of how likely they are to be the answer.

#### (a) 🔑 The documented reset is `ENN`, not power

The TMC2209's `DIAG` is the driver-error output, and the datasheet's stated
recovery is **the error condition is reset by `ENN` = high** — not by a supply
interruption. Here `EN` is driven LOW continuously by the Arduino on A4
(§2, §16.1), so if the Arduino stayed powered across the 12 V cycle, **the
chip's enable input never went high and the prescribed reset never happened.**

To perform it: lift the `EN` wire off A4 and jumper it to **5 V** for about a
second, then remove the jumper. The breakout's 20 kΩ pull-down re-enables the
driver on its own (§12.4), so the wire can go back to A4 afterwards or be left
off for the test. Re-read `DIAG` immediately after.

#### (b) The power cycle may have been partial

Two rails feed this chip: `VM` (12 V, to the screw terminals) and `VCC_IO`
(5 V, from the Arduino). Cutting only `VM` leaves the digital side partly
powered from USB. **Cut both together** — unplug the Arduino's USB *and* the
12 V, wait ten seconds, restore. Combined with (a), this is the most likely
reason a genuine latch would have survived.

#### (c) 🔑 A short type never measured: output to ground, output to supply

The TMC2209 protects against three distinct short conditions, and only one of
them is phase-to-phase. `s2ga`/`s2gb` (short to **ground**) and
`s2vsa`/`s2vsb` (short to **supply**) are separate flags, and **neither has
ever been measured on this machine.** Power off, probe each of `1A`, `1B`,
`2A`, `2B` against `GND` and against `VM+`:

⚠️ Do not expect a clean "open." The driver's internal body diodes conduct in
one polarity, so an ohmmeter will read *something* on every one of these. The
tell is a hard near-zero in **both** probe polarities. Cleaner still: use the
meter's **diode-test** mode and look for ≈ 0.00 V rather than a normal
0.3–0.7 V drop.

And there is an obvious mechanical candidate now that the ribbon is gone: **is
the pipette's metal body tied to supply ground, and is a bare direct-wire lead
resting against it?** The ribbon insulated the whole run; four bare wires
draped from screw terminals to a metal pipette body with no strain relief are
exactly how a coil-to-chassis short appears. Look before probing.

#### (d) Overtemperature, which is self-holding

`ot` shutdown asserts `DIAG` and holds it until the chip cools **and** is
reset. With `EN` low and real ~4 Ω windings now attached, the chip holds
`IHOLD` current in both coils continuously at rest — at a pot near maximum
that is real standing dissipation with no heat sink fitted.

**Touch the chip with the board powered and nothing commanded.** Warm is
expected; too hot to keep a finger on means it is dissipating heavily at
standstill, which is both a cause of `DIAG` and a reason to turn the pot down
before anything else. ⚠️ It could be hot enough to burn — approach briefly.
Then leave it unpowered for several minutes before attempting (a) or (b).

#### (e) The cheapest check of all: is `DIAG` even being driven?

§16.5 argued that `DIAG` at 5 V beside `INDEX` at 0 V looks like two driven
outputs, because a floating pair would not reliably split to opposite rails.
That is a reasonable inference and it has never been checked. It can be
replaced with a fact in thirty seconds:

> **Everything unpowered, measure the resistance from `DIAG` to the 5 V /
> `VCC_IO` pin on the header.**
>
> - A few kΩ to tens of kΩ ⇒ there is a pull-up on the breakout, and 5 V on
>   that pin may mean nothing at all. Every `DIAG` reading in this document
>   would need re-reading.
> - Open / megohms ⇒ nothing is holding it high, the chip really is driving
>   it, and §16.5's inference was right.

### 19.4 How to measure VREF with a multimeter

Ben's direct question. `VREF` is **not** broken out on the 10-pin header
(§11.3), so this means probing the trimmer itself.

#### Step 1 — find the wiper, power off

A three-terminal trimmer has two ends of a resistive track and one wiper. On
this board the track ends go to the chip's internal `5VOUT` and to `GND`, and
the wiper goes to the chip's `VREF` pin. The unambiguous way to tell them
apart, with the board **unpowered**:

> Put the black probe on board `GND` and touch each of the three terminals in
> turn while turning the pot. **The wiper is the terminal whose resistance to
> `GND` changes as you turn it.** One of the other two reads a constant ~0 Ω
> (that is the track end tied to `GND`); the third reads a constant full-track
> value.

An equivalent check without moving to `GND`: measure all three pairs among the
terminals. The pair whose reading does *not* change as you turn the pot is the
two track ends; the remaining terminal is the wiper.

Faster but less certain: on many trimmers the **metal adjustment screw is
electrically the wiper**, so touching a probe to the screw head works. Worth
trying first — but confirm it against the resistance test before trusting a
number from it, and do not press hard or you will turn the pot while measuring.

#### Step 2 — 🔴 turn the pot fully counter-clockwise *before* powering up

Measuring `VREF` requires `VM` present, which means the chip will be energising
real windings the moment power is applied — at whatever the pot currently says.
Adafruit: fully clockwise is maximum. So wind it fully **counter-clockwise**
first, so the first powered moment with a real load is at minimum current, then
bring it up while watching the meter.

#### Step 3 — measure

| | |
| --- | --- |
| meter | **DC volts**, 2 V range or autoranging |
| black probe | board `GND` — the header `GND` pin, or the `−` of the motor supply block |
| red probe | the trimmer's **wiper** |
| power | **12 V must be on.** `VREF` is derived from the chip's internal `5VOUT`, which is generated from `VM` alone (§10.3) — with `VM` off it reads 0 V whatever the pot says |
| expect | somewhere in 0 – ~2.5 V, stable, unaffected by whether the motor is stepping |

**The target is `VREF` ≈ 0.55 V for ~1.0 A peak** — the P20 GEN2's
`plungerCurrent`. From §11.3, `I_rms = (VREF / 2.5) × 3.283 A`, so 0.55 V gives
0.72 A rms = 1.02 A peak. For a first movement test wind it well below that;
enough to confirm the shaft turns is enough.

⚠️ Use a fine-tipped probe, or solder a short wire to the wiper and clip onto
it. 12 V is no shock hazard, but a probe that slips and bridges the wiper to an
adjacent pad while powered will destroy the chip.

#### 🔑 Step 4 — the reading is itself a verdict on the chip

This is why `VREF` has been the most valuable outstanding measurement since
§16.9, and it now reads as a clean binary. With `VM` = 13 V and the pot turned
**up**:

| `VREF` | meaning |
| --- | --- |
| clearly non-zero, rising toward ~2.5 V as the pot turns up | the internal `5VOUT` regulator is **alive** — the chip is not wholly dead, and `DIAG` is reporting a latched or live fault in the output stage. §19.3's resets are worth trying |
| ≈ 0 V at full clockwise | `5VOUT` is **dead** — the chip's internal regulator has failed. **Replace the board**; nothing else needs testing |

If the board breaks out `5VOUT` anywhere, measuring it directly (≈ 5 V to
`GND`, `VM` on) answers the same question one step earlier.

#### If the wiper turns out to be unreachable

Two ways to set the current without ever measuring `VREF`, both entirely
adequate here:

- **Empirical.** Pot fully counter-clockwise, then creep up until the plunger
  moves reliably, then give it a small margin. On a ~4 Ω motor spec'd at 1.0 A
  peak, "just moves reliably" sits well below anything harmful. This is how
  drivers without a `VREF` pad get set routinely.
- **Supply current as a bound.** Meter in DC amps (10 A jack) in series with
  the 12 V `+` lead, motor at rest and holding. It is not the coil current, but
  it answers "is this 0.1 A or 1.5 A" directly. ⚠️ Never leave a meter in amps
  mode across a voltage.
- **Temperature as a proxy.** With the current set sanely and the motor idle,
  the driver should be warm at most. Too hot to hold a finger on is too much.

### 19.5 The order, and what it is blocked on

The plunger cannot turn while `DIAG` is asserted — the output stage is latched
off — so §18.8's first-movement test waits on this.

1. **Look** for a bare direct-wire lead touching the pipette body (§19.3c).
2. **Power off:** `DIAG`-to-5 V resistance (§19.3e), then each coil terminal to
   `GND` and to `VM+` in diode mode (§19.3c).
3. **Power off:** identify the trimmer wiper, and wind the pot fully
   counter-clockwise (§19.4 steps 1–2).
4. **Cut both rails together** — 12 V and the Arduino's USB — wait, let the
   chip cool, restore (§19.3b, §19.3d).
5. **Measure `VREF`**, turning the pot up from minimum (§19.4 step 3). ≈ 0 V at
   full clockwise ⇒ replace the board and stop here.
6. **Toggle `ENN` high for a second, then low** (§19.3a). Re-read `DIAG`.
7. **If `DIAG` is still 5 V** after all of the above, with the coils connected
   and no rail short found — **replace the driver board.**
8. Only then: set `VREF` to ~0.55 V, fit the 1515 heat sink, reconnect the
   limit switch (§18.5), and run the bench move (§18.8).

### 19.6 Status after the cross-pair measurement

| | |
|---|---|
| Arduino STEP/DIR output | ✅ proven (§6), polarity corroborated by the LEDs (§14.1) |
| `VM` at the driver | ✅ 13 V (§12) |
| `EN` at the driver pin | ✅ 0 V (§16.1) |
| coil grouping in the terminals | ✅ correct (§17.1) |
| motor windings | ✅ 4.3 Ω / 3.7 Ω (§18.1) |
| **phase-to-phase isolation** | ✅ **MΩ on the direct wiring — the short left with the ribbon (§19.1)** |
| the ribbon harness | 🔴 condemned — it carried **both** faults |
| **TMC2209 `DIAG`** | 🔴 **5 V, survives a `VM` cycle. A damaged output stage is now the leading explanation (§19.2)** |
| `ENN` reset attempted | ❓ **not yet — this is the documented recovery, not a power cycle (§19.3a)** |
| both rails cycled together | ❓ not yet (§19.3b) |
| coil terminal → `GND` / `VM+` | ❓ **never measured — a short type we have not looked for (§19.3c)** |
| `DIAG` → 5 V pull-up check | ❓ never measured; decides whether the pin is driven at all (§19.3e) |
| VREF at the wiper | ❓ **the binary verdict on the chip's internal regulator (§19.4)** |
| limit switch / D9 | ⚠️ likely unconnected with the ribbon out (§18.5) |
| plunger direction | ⚠️ may have inverted; homing is the tell (§18.6) |
| firmware `aspirate` planes | 🔴 flash the GEN2 image before any aspirate (§18.7) |
| TMC2209 UART readback | 🔴 `comm = 0`; needs the GEN2 flash **and** the TX-side bridge (§12.3) |

---

## 20. 2026-09-24: the GEN2 image goes on the board, and `comm = 0` becomes a one-line diagnosis

Ben asked for the trio now that the coils measure healthy. The firmware
prerequisite from §18.7 was done first; the protocol run itself was cut about a
minute in by a power loss.

### 20.1 The flash

`avrdude -U flash:v:` against all three candidate images, read-only, before
anything else:

```
panda_vcl_p20_20260915     : MATCH  17370 bytes of flash verified
flash_20260915T220346Z     : no     flash verification mismatch
panda_vcl_p20gen2_20260917 : no     flash verification mismatch
```

So the board was still on the 2026-09-15 image, as §14.3 found. `sha256` of the
GEN2 hex agreed between the repo and the Pi before writing it. After:

```
panda_vcl_p20gen2_20260917 : MATCH  17382 bytes of flash verified
panda_vcl_p20_20260915     : no
flash_20260915T220346Z     : no
```

Both instrument paths were re-checked on the reflashed board — the capper
shares this Arduino — and both answer: `OK:{"homed":0,"pos":0.00,"max_vol":20.00}`
and `OK:{"value1":0}`.

**Why it had to come before the trio.** `MOVE_TO` is absolute millimetres, so
CubOS's patched `blowout` (32.5) and `drop_tip` (46.5) land where CubOS asks on
either image. **`aspirate` does not** — it is computed inside the firmware and
descends to `PRIME_POSITION` before its metered ascent. The 09-15 image carries
`PRIME_POSITION 36.0`, a P300 plane; a P20 GEN2's bottom is **28.0**. With the
coils open that cost nothing. With windings that now measure 4.3 Ω and 3.7 Ω it
would drive the plunger **8 mm past its mechanical bottom on every call**.

### 20.2 🔑 `comm = 0` with the read fix live isolates the bridge

The GEN2 image carries `tmc2209-softwareserial-read.patch`, without which a
TMC2209 read over `SoftwareSerial` on an AVR is structurally impossible (§10.2).
Five consecutive reads immediately after flashing:

```
OK:{"msg":"Driver status","v":[0.00,0.00,-1.00]}      x5
      comm = 0      flags = 0      current_scaling = -1 (unread)
```

That is not a disappointment — it is the isolation. §12.3 listed two
independent reasons `comm = 0` could not be trusted. **One of them is now
gone.** The remaining one is the hardware bridge: the 10 kΩ resistor is still
on the **RX** side, so `SoftwareSerial::begin()` leaves the Arduino's TX a
push-pull output idling HIGH on the shared node and the driver cannot pull it
down to reply. It has to be:

```
A1 --[1 kOhm]-- NODE        with A0 and PDN_UART both directly on NODE
```

**One resistor now stands between this machine and `DRV_STATUS`** — which
reports `open_load_a/b`, `s2ga`/`s2gb`, `s2vsa`/`s2vsb` and `ot` directly, i.e.
the specific bit behind §19.2's `DIAG` = 5 V. That makes it the single
highest-value bench job outstanding, ahead of the meter work in §19.3, because
it answers several of those questions at once and without probing a live board.

### 20.3 The limit switch reads CLEAR on the direct wiring

§18.5 warned that pins 6 and 7 rode the ribbon that came out, and that with D9
floating the firmware would read the switch as asserted and refuse every
retraction. **It does not.** 14 mm of retraction — the gated direction — ran to
completion at the commanded rate without being refused, which is the D9-LOW
signature. So the switch loop survived the rewiring.

### 20.4 🔴 `CMD_MOVE_RELATIVE` takes three varargs, and getting that wrong is silent

`CMD_MOVE_RELATIVE` (16) takes **`direction, steps, velocity`**, and
`PawduinoLink.send_command(code, *args)` is **varargs, not a list**. Passing
`[d, steps, rate]` as one argument serialises the list's `repr` onto the wire;
the firmware's comma tokenizer then reads `atof("[0") == 0`, so **`direction`
parses as 0 whatever you asked for**. The reply echoes `v[0] = 0.00` in both
cases, which is the tell — and the only one, because a wrong direction still
returns a well-formed `OK`.

Measured semantics, with the correct call form:

| `direction` | counter | travel | LED |
|---|---|---|---|
| **0** | decreases | retract / up — **the direction gated by D9** | green `F` |
| **1** | increases | advance / down — ungated | red `B` |

These agree with `pipette_driver_probe.py`'s `DIR_UP = 0` / `DIR_DOWN = 1`,
which was written against the raw serial port in §6 and had it right all along.
`pipette_driver_measure.py` sent two arguments instead of three and is fixed.

### 20.5 The bench window

Plunger only — `/dev/ttyUSB0` was never opened, so no gantry motion was
commanded.

```
  direction=0  1.00 mm at 800 steps/s   dt= 2.031s  (commanded 1.99s)
  direction=1  1.00 mm at 800 steps/s   dt= 2.032s  (commanded 1.99s)
  advance     14.00 mm at 800 steps/s   dt=28.339s  (commanded 27.9s)
  ADVANCE      4.00 mm at 200 steps/s   dt=32.121s  (commanded 31.8s)
  RETRACT      4.00 mm at 200 steps/s   dt=32.118s  (commanded 31.8s)
```

Every leg ran at the commanded rate in **both** directions, to about 1%. Net
commanded travel for the session is **zero** — the 14 mm the mis-formed call
walked was restored, and the ±4 mm window balances.

⚠️ As always (§6.1): this proves the **Arduino emitted the steps**.
`stepMotor()` bit-bangs `STEP` and counts loop iterations, with no encoder, no
current sense and no feedback of any kind. Whether the motor turned needs eyes
on the machine, and `DIAG` = 5 V says the output stage is latched off, so the
prior is that it did not.

### 20.6 🔴 The run was cut, and the machine state is unknown

The protocol started at about 22:19 UTC. The Pi dropped off the tailnet at
**22:20:00 UTC**. The Pi shares power with the gantry (§13 session notes), so a
supply interruption takes both — the run was cut at an arbitrary point with no
closing `home` and no `CMD_EMAG_OFF`.

**Check by eye before the next run:**

- **Is the capper holding a cap, and is a vial open?** Step 2 is
  `decap vial_1`; anything between there and `cap vial_1` leaves a cap either
  on the electromagnet or dropped where the coil de-energised.
- **Where is the head?** GRBL's counter resets to the homed corner on port open
  regardless of where the carriage is, so `WPos` after a power cut is fiction
  (§15). Recover by hand or by a successful `$H` — do **not** `$X` and jog.
- **Re-check `$20`.** It read `1` before this run, but an interrupted
  calibration leaves it at `0`, and it has been found off twice (2026-08-27,
  2026-09-18).

### 20.7 Status

| | |
|---|---|
| Arduino STEP/DIR output | ✅ proven (§6), LEDs corroborate (§14.1) |
| `VM` at the driver | ✅ 13 V (§12) |
| `EN` at the driver pin | ✅ 0 V (§16.1) |
| coil grouping / windings / isolation | ✅ correct, 4.3 Ω / 3.7 Ω, MΩ (§17.1, §18.1, §19.1) |
| limit switch / D9 | ✅ **CLEAR on the direct wiring (§20.3)** — §18.5's warning did not bite |
| firmware `aspirate` planes | ✅ **GEN2 image flashed and verified (§20.1)** |
| the ribbon harness | 🔴 condemned — it carried **both** faults |
| **TMC2209 `DIAG`** | 🔴 **5 V, survives a `VM` cycle (§19.2)** |
| **TMC2209 UART readback** | 🔴 **`comm = 0` with the read fix live — now the TX-side bridge alone (§20.2)** |
| `ENN` reset attempted | ❓ not yet — the documented recovery, not a power cycle (§19.3a) |
| both rails cycled together | ❓ not yet (§19.3b) |
| coil terminal → `GND` / `VM+` | ❓ never measured (§19.3c) |
| `DIAG` → 5 V pull-up check | ❓ never measured (§19.3e) |
| VREF at the wiper | ❓ the binary verdict on the internal regulator (§19.4) |
| machine state after the cut | ⚠️ **unknown — needs eyes (§20.6)** |
