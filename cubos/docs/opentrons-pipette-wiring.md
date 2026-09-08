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

**The motor supply is separate from VDD.** The Arduino's 5 V on `VDD` powers the
driver's logic only. With no voltage on the `+`/`-` terminal the board still
accepts STEP/DIR and acknowledges everything, with zero coil current and total
silence — indistinguishable at the serial port from a healthy run.

## 6. Consequences that outlive the wiring fix

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
