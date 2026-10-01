# Narrowing to the driver: the LEDs, `DIAG`/`INDEX`, and two separate stepper systems

*2026-09-21 — 6 comments, migrated verbatim from [PR #171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171).*

Every comment below is reproduced exactly as posted, with its author and a link back to the original. `@`-mentions carry a zero-width space so that re-reading this file cannot notify anyone or re-trigger CI.

---

## @jarrettshupe — 2026-09-21 17:20:19 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5764603386)

@claude summarize everything that ben has done since you listed the "next steps" for troubleshooting.

---

## @claude[bot] — 2026-09-21 17:20:41 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5764608218)

**Claude finished @jarrettshupe's task in 2m 19s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35631374651)

---
### What Ben has done since the 2026-09-17 next-steps list

- [x] Locate the cut-off — my summary comment, 2026-09-17 14:48 UTC
- [x] Walk the thread forward from there
- [x] Pull in the three sessions whose commits landed after the last comment visible here ([`d96e5e5`](https://github.com/vertical-cloud-lab/byu-vcl/commit/d96e5e5), [`7975d5e`](https://github.com/vertical-cloud-lab/byu-vcl/commit/7975d5e), [`803e008`](https://github.com/vertical-cloud-lab/byu-vcl/commit/803e008))
- [x] Summarize, mapped against the next-steps list

**Nothing was run, connected to, or changed this session** — you asked for a summary, and Ben's standing rule is that runs need an explicit ask.

Short version: **Ben closed four of the six next-steps items, two of them decisively — and in the process the trio ran end-to-end for the first time since 2026-09-01, with the plunger retracting for the first time ever.** The motor is still silent, but the fault is now boxed into one short stretch of the circuit.

---

### Chronologically

**1. The hand test → no holding torque** *(2026-09-17 21:55)*
> *"When I pull the plunger manually, it moves freely when plugged in and on, so there is no current going through."*

Step 1 of the list, and the most load-bearing single result at that point: no torque ⇒ no coil current.

**2. The pot is at full clockwise** *(22:43)*
Which made #1 much stronger rather than merely adding a detail. No UART write has ever been confirmed to land, so `i_scale_analog` is still 1 and **the pot is the only thing setting current — and it was at maximum.** Maximum commanded current, zero torque.

He also reported the `F` LED blinking bright/dim, which turned out to be benign — `F` is *Forward*, a direction indicator on the `DIR` net, not a fault light, and it was tracking my `avrdude` resets. **This board can't show a driver fault at all**; `DIAG` has no LED and no wire.

**3. Replugged the Arduino's USB** *(between sessions)*
The serial link had been corrupting bytes — 0 of 25 `STATUS` round-trips parsed, blocking the run entirely. After the replug: 20/20 clean. A `USBDEVFS_RESET` from the Pi had not been enough.

**4. 🔑 "the gantry wasn't on... that is my bad"** *(23:28)*
Worth calling out, because it retired a diagnosis of mine rather than confirming one. With the stepper supply off, GRBL accepts every `G01`, emits the steps, and reports a plausible `WPos` while the machine stands still. I had read that as **two limit-switch faults** (Z open, X stuck) and blamed the drag chain. All of it was wrong, and campaign 36's failed closing `home` re-explains the same way. One sentence from Ben undid several hours of misdiagnosis.

Campaign 50 then homed on the first try in 18.1 s — and incidentally showed the **pipette limit switch now reads CLEAR** (`HOME` running its full 26.3 s seek instead of a 0.52 s fake success). That's step 6 of the list, closed by Ben's earlier rewiring.

**5. 🔑 `VM` = 13 V at the driver's screw heads** *(2026-09-18 00:10)*
Step 2, and it **killed the leading hypothesis**. Missing `VM` was the one fault that explained silence, no torque and `comm = 0` all at once — the TMC2209 makes its own logic and reference supplies from `VM`, and the 6121's VREF trimmer hangs off that internal rail. 13 V means the chip is powered and VREF should be live and near maximum. It still won't hold the plunger.

**6. Stopped the run when Y overran, and reset by hand** *(00:10)*
Correct call. **The overrun was my diagnostic script's fault, not the machine's** — `$X` + relative `G91` jogs against a counter that had reset to the homed corner while the carriage stood at Y 27, so `G01 Y-60` passed the soft-limit check and physically commanded Y −33. Soft limits only mean anything after a *successful* `$H`. Written up in [`cubos/results/y_overrun_20260918/`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/results/y_overrun_20260918/README.md) and the rule is now in the SOP. No machine fault; the limit switches and drag chain are not implicated.

**7. Homed the machine and asked for the run → campaign 54: 12/12** *(00:38)*

```
Protocol complete — 12 steps executed.
```

First complete run since 2026-09-01. Both homing cycles first try, no capper retries, no alarms, configs unchanged. `decap vial_1` captured on the **first attempt at the exact coordinates campaign 50 had failed at three times** — so that failure was the power state, not the deck or the geometry. The pre-run frame also closes the "is there a vial in slot 1" question outright:

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/results/pipette_test_20260918/frames/prerun_deck__cam1_csi1_cropped.jpg?raw=true)

**And the plunger retracted for the first time.** `MOVE_TO 28.0` from 46.5 = **−18.5 mm in 12.267 s**, at the firmware's own 0.663 s/mm. Every command in the run scaled with its commanded distance, in both directions. Since 2026-09-15 every retraction had returned a flat ~0.107 s having emitted no steps.

⚠️ Proves the **Arduino emitted the steps** — not that the motor turned. `stepMotor()` bit-bangs STEP and counts loop iterations; there's no feedback of any kind.

**8. Watched the driver board during that run**
> *"B red for the majority while the Pipette was running commands, then F green after the drop tip."*

This matches the serial trace **command-for-command**: red spans `blowout` and `drop_tip`'s first leg (00:43:13 → 00:43:44), green begins at 00:43:47 — `drop_tip`'s second leg, the only upward `MOVE_TO` in the protocol — and latches to the end. An independent, human-eye confirmation of the trace, down to which command flipped the pin.

Both LEDs are driven by the *Arduino's* pins, so they confirm that side only. **Combined with `VM` = 13 V, the fault is now confined to the segment between the TMC2209's input pins and the motor windings.**

---

### Against the list

| next step | status |
|---|---|
| 1. Hand test — holding torque | ✅ **done** — none |
| 2. Measure `VM` at the screw terminal | ✅ **done — 13 V.** Leading hypothesis dead |
| 3. VREF pot | ⚠️ reported at full CW; VREF itself still unmeasured at the wiper |
| 4. `EN` at the driver pin · PDN_UART on A1 · MS1/MS2 | ❌ not done |
| 5. Re-read `CMD 29` for `open_load_a/b` | ⛔ still `comm = 0`, and now known to be **impossible** until both the bridge topology and the flashed image change |
| 6. Limit-switch loop (pin 6 → GND, 7 → D9, NC) | ✅ **fixed** — D9 LOW, retractions execute |
| — ruler check on the first real move | ❌ blocked on the motor turning |
| — CubOS `prime`/`blowout`/`drop_tip` placeholders | ✅ **done** — P20 GEN2 planes 28.0 / 32.5 / 46.5 from Opentrons, live in campaign 54's trace |
| — `UL_TO_MM` gravimetric | ❌ still an estimate; the corrected 1.34 is built but unflashed |
| — the `Alarm` / `Pn:X` "blocking a run" | ✅ resolved — it was the supply, not a fault |

Two things I got wrong in that window and have corrected in place: the **two limit-switch faults** (§4 above) and **`comm = 0` as evidence** — a read over `SoftwareSerial` on an AVR can't succeed with the stock janelia library whatever the wiring does, so it never meant what I read into it.

---

### What's left, and it's a short list

`avrdude -U flash:v:` **proved** the board is running the 2026-09-15 p20 image — the P20 GEN2 build with the Opentrons planes *and* the SoftwareSerial read fix is built and waiting at [`panda_vcl_p20gen2_20260917.hex`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/firmware/panda_vcl_p20gen2_20260917.hex), unflashed.

🔑 **The new opening: `DIAG` and `INDEX`.** Both are broken out on the 6121, neither has an LED, neither has ever been looked at — and **neither needs UART**. `INDEX` pulses as the chip consumes STEP pulses, *independently of whether any current reaches the coils*, so it is exactly the discriminator the UART readback was wanted for:

| STEP arriving | `INDEX` | reading |
|---|---|---|
| yes | **changing** | chip is alive and counting → fault is downstream: coil path, or current at zero |
| yes | **dead flat** | chip isn't processing STEP → dead, disabled, or STEP not landing on its pin |

Bench order — all multimeter work, none of it needs the machine running:

1. **`EN` at the driver's pin** (not the Arduino header) — ~0 V expected; ~5 V means the output stage is off
2. **`DIAG`** — ~0 V expected; high means the chip is reporting a fault
3. **`INDEX` during a driven leg** — must change. [`pipette_driver_measure.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/tools/pipette_driver_measure.py) opens a bounded, direction-labelled ±6 mm stepping window for exactly this, and refuses to run if the limit switch reads asserted
4. **Coil resistance at the four screw terminals**, ribbon on, power off: `1A`–`1B` and `2A`–`2B` a few to a few tens of ohms, `1A`–`2A` open. Tests the whole path including crimps and screw clamping
5. **The yellow `S` LED**, free while you're there — it must look *different* during a move

Full detail in [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/docs/opentrons-pipette-wiring.md) §12–14; campaign 54 in [`cubos/results/pipette_test_20260918/`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/results/pipette_test_20260918/README.md).

**Also still open, unrelated to the plunger:** `$20` was found at `0` again before campaign 54 (soft limits off — restored and verified, and it's the same condition that let the Y overrun happen, so **re-check it after any E-stop or manual reset**); `drop_tip` still ejects 35 mm above the slot pending a `tip_disposal` deck entry; `cam1_csi1` still looks across the bench into the room rather than at the vial column.

**Not done:** nothing was measured, run, wired or committed this session — summary only. Say the word when you want any of the above executed on the machine, or the P20 GEN2 image flashed.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @jarrettshupe — 2026-09-21 17:36:47 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5764821653)

Could the stepper driver have anything to do with the issues above? @claude

---

## @claude[bot] — 2026-09-21 17:37:10 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5764827888)

**Claude finished @jarrettshupe's task in 3m 28s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35633131823)

---
### Short answer: not for the gantry, and yes for the plunger — where it's now one of only two things left

- [x] Read the branch state — **three sessions landed after the last comment in this thread**
- [x] Separate the two stepper systems and check it against the configs
- [x] Answer for each symptom: Y overrun, Z not descending, failed decap, silent plunger
- [x] Write the distinction into the wiring doc so it doesn't have to be re-derived
- [x] Commit ([`0561306`](https://github.com/vertical-cloud-lab/byu-vcl/commit/0561306))

**No hardware access this session** — you asked a question, and opening the gantry port resets the GRBL board and throws away any homing reference, which isn't worth doing to answer one. Nothing was run, connected to, or changed on the machine.

---

### There are two stepper systems, and they share no signal path

This is the whole answer, and it isn't obvious from the outside — "the stepper driver" could reasonably mean either.

| | gantry X / Y / Z | pipette plunger |
|---|---|---|
| commanded by | GRBL controller board | Arduino Uno R3 `2341:0043` |
| serial port | `/dev/ttyUSB0` (CH340) | `/dev/ttyACM0` |
| stepper drivers | **on the GRBL board**, one per axis | **Adafruit 6121 TMC2209 breakout**, one |
| step generation | GRBL firmware | `stepMotor()` bit-banging `STEP` (A2) / `DIR` (A3) |
| scaling | `$100`–`$102` = 400 steps/mm | `STEPS_PER_MM 1592` |
| limits | `$130`–`$132`, switches visible on `Pn:` | one switch on D9 |

Both ports sit side by side in [`cub_xl_ben_pipette_capper.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml), which is what makes them look like one system. **The TMC2209 has no electrical connection to any gantry axis** — it can't move an axis, block one, overshoot a limit, or mask a switch.

### So for the gantry symptoms: no. And each one already has its own cause

| symptom | cause |
|---|---|
| campaign 46 — `ALARM:9`, capper never went down in Z | **the gantry's stepper supply was off.** `WPos` is GRBL's step counter, not a measurement, so an unpowered machine reports plausible positions — which I misdiagnosed as two limit-switch faults before Ben found the switch |
| campaign 50 — `decap vial_1` failed 3× | same power state. Campaign 54 captured on the **first attempt at byte-identical coordinates** |
| **Y driven 33 mm past its stop** | my diagnostic script did `$X` + a `G91` relative jog against a counter **282 mm stale**. Soft limits validated the target against that fiction and passed it; `$21=0` meant the physical switch wasn't being watched. [Write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/cubos/results/y_overrun_20260918/README.md) — no machine fault, and the rule now in the SOP is *after a failed `$H`, recover by hand; don't `$X` and jog* |
| campaign 36 — closing `home` failed | same supply dropout |
| 2026-09-18 — no run could start | `$20=0` found on the controller. Restored |

### For the plunger: yes — and as of campaign 54 the driver is one of two candidates

Three sessions landed on the branch after this thread's last comment, and between them they closed out everything upstream of the driver:

```
  Arduino STEP/DIR output     PROVEN   1592 steps at the commanded rate
  polarity and timing         PROVEN   your own B-red / F-green observation matches
                                       the serial trace command-for-command
  limit-switch gate           OPEN     campaign 54 — retractions emit steps for
                                       the first time since 2026-09-15
  VM at the screw terminal    13 V     Ben measured it; kills the leading hypothesis
  ------------------------------------ everything above is eliminated
  TMC2209 chip / EN / VREF    ?        <- the driver itself
  coil path to the windings   ?
```

The fault is now confined to **the segment between the TMC2209's input pins and the motor windings**, and only two of the three remaining candidates are the driver proper:

- **B — `EN` held high.** Output stage off regardless of `VM` and VREF. Measure ~0 V **at the driver's pin**, not the Arduino header, and confirm the wire lands on **A4** — Cubware's diagram puts it on A3, which is `DIR`.
- **C — dead chip, or dead internal regulator.** With `VM` at 13 V the chip's own `5VOUT` should be up and VREF live; the pot is at full clockwise, so VREF should read near maximum. **VREF ≈ 0 V ⇒ replace the board.**
- (A — the coil path out of its terminals is open. Not the driver, but the same symptom, and still the hypothesis with the most independent support: silence with *no buzzing* is open coils; mis-*paired* coils buzz and vibrate.)

🔑 **`DIAG` and `INDEX` split B+C from A, and need no UART.** Both are broken out on the 6121 and neither has ever been looked at. `INDEX` pulses as the chip consumes STEP pulses *regardless of whether current reaches the coils* — so during a driven leg, **changing** means the chip is alive and the fault is downstream; **dead flat** means the chip isn't processing STEP. That's exactly the discriminator the broken UART readback was wanted for. [`pipette_driver_measure.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/cubos/tools/pipette_driver_measure.py) opens a bounded stepping window to probe them. Order and expected readings: [§14.5](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/cubos/docs/opentrons-pipette-wiring.md).

### ⚠️ One way the driver *could* touch the gantry — power, not signals

The Pi already shares power with the gantry (switching the gantry supply reboots it, seen 2026-09-17). **If the driver's 12 V comes off that same brick or strip**, a short or latched fault there could brown out the gantry and look like a motion fault — which is the one mechanism your question would be right about.

I can't check this remotely and it isn't recorded anywhere, so **it's worth 30 seconds of tracing the driver's supply leads.** Two things argue against it mattering today: the terminal read a healthy 13 V, and campaign 54 ran 12/12 clean with the driver connected.

### Committed — [`0561306`](https://github.com/vertical-cloud-lab/byu-vcl/commit/0561306)

- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/cubos/docs/opentrons-pipette-wiring.md) — new **§15**: the two-system table, the symptom-to-cause mapping, the elimination ladder, and the shared-power caveat
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/cubos/README.md) — a short pointer so this is findable from the top

**Not done:** no hardware measurement, no motion, no port opened, no wiring touched. The four measurements that would settle the plunger — `EN`, `DIAG`, `INDEX`, coil resistance — all need the meter and hands on the machine. The P20 GEN2 firmware image is still built-but-unflashed, and the bridge resistor still needs moving to the TX side before `comm > 0` is even possible.

`CLAUDE.md` shows as modified in the working tree only because the action synced `main`'s copy in; I verified it's byte-identical to `origin/main`, so I left it uncommitted.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-21 21:50:35 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5768010367)

@claude check https://github.com/Ursa-Laboratories/Cubware/blob/main/documentation/opentrons-pipette-setup.md is everything in the "before running pipette commands" list good to go? exclude the 5th point.

---

## @claude[bot] — 2026-09-21 21:50:58 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5768014434)

**Claude finished @benwhitney5463's task in 3m 31s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35659481889)

---
### Checked all four — **1–4 are good to go**, with one caveat on #1 that's worth fixing before the next run: the flashed image isn't the P20 GEN2 one

- [x] Fetch the Cubware doc and extract the checklist
- [x] Check each item (excluding #5) against the machine's verified state
- [x] Try a live re-check on the Pi — **it's off the tailnet**, see the end
- [x] Report

**Nothing was run** — you asked a question, so this is the repo record plus a reachability probe. No motion, no port opened, no config changed.

The list from [`opentrons-pipette-setup.md`](https://github.com/Ursa-Laboratories/Cubware/blob/main/documentation/opentrons-pipette-setup.md):

| # | item | status |
|---|---|---|
| 1 | Flash the PAW Arduino firmware that supports the pipette command set | ✅ **but see below** |
| 2 | Connect the Arduino to the CubOS host | ✅ last verified |
| 3 | Identify the serial port | ✅ |
| 4 | Confirm no other process has the serial port open | ✅ last verified |
| 5 | *(excluded per your ask)* | — |

---

### 1. Firmware — satisfied as worded, but it's the 09-15 image, not the GEN2 one

Strictly, ✅: the board runs a PANDA-derived image implementing the full command set (`HOME` 10, `MOVE_TO` 11, `ASPIRATE` 12, `DISPENSE` 13, `STATUS` 14, `MOVE_RELATIVE` 16, plus our `DRIVER_STATUS` 29). Proven rather than assumed — `avrdude -U flash:v:` against every candidate on 2026-09-18:

```
panda_vcl_p20_20260915.hex       17370 bytes of flash verified      <- this is what is running
flash_20260915T220346Z.hex       verification error at byte 0x000e  (stock backup)
panda_vcl_p20gen2_20260917.hex   verification error at byte 0x000e  (NOT flashed)
```

🔴 **The consequence: CubOS and the firmware now disagree about the plunger.** The `p20-gen2-plunger-constants` patch is applied on the Pi's CubOS (prime **28.0** / blowout **32.5** / drop_tip **46.5**, `mm_to_ul 1.0`), and its own comment says those "agree with `include/Pipette.h` in the VCL PANDA firmware" — they agree with the **GEN2 build**, which isn't on the board. The running image still carries `PRIME_POSITION 36.0`, `BLOWOUT 44.0`, `DROP_TIP 55.0`, `UL_TO_MM 1.8`.

`MOVE_TO` is absolute millimetres, so `blowout` and `drop_tip` land exactly where CubOS asks. **`aspirate` does not** — it's computed inside the firmware. Campaign 54's trace proves it, and the arithmetic closes three independent ways at the firmware's own 0.663 s/mm:

```
MOVE_TO 32.5  21.546 s / 32.5 mm = 0.663   <- so the plunger was at 0.0 when blowout started
MOVE_TO 46.5   9.288 s / 14.0 mm = 0.663
MOVE_TO 28.0  12.267 s / 18.5 mm = 0.663
```

Landing at 0.0 after `ASPIRATE 20.0` is exactly `PRIME 36.0 − 20 × 1.8`. With the GEN2 image it would be `28.0 − 20 × 1.34 =` **1.2**. So a "20 µL" aspirate is still running on the P300-derived scale.

The GEN2 build also carries `tmc2209-softwareserial-read`, without which `CMD 29` can only ever return `comm = 0` — which is why the driver diagnostic is still blind, and why `open_load_a/b` (the coil-continuity answer, no meter needed) is unavailable. **Say "flash it" and I'll flash [`panda_vcl_p20gen2_20260917.hex`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/cubos/firmware/panda_vcl_p20gen2_20260917.hex) next session** — it also drops run current from 50 to 20 (≈1.02 A peak, Opentrons' `plungerCurrent`), which matters given the board's been sitting at a ~2.3 A setting.

### 2. Arduino connected — ✅, last verified

`PawduinoLink.connect()` 3.77 s OK via the `CMD_HELLO` handshake, **10/10 clean `STATUS` round-trips**, and campaign 54 ran 12/12 on it. `STATUS` returns `max_vol: 20.00`, so the p20 image is live and answering.

⚠️ One history note: this link corrupted badly on 2026-09-17 (0 of 25 round-trips parsed) and the fix was a **physical USB replug** — a `USBDEVFS_RESET` from the Pi is not a power cycle and didn't clear it. If commands start returning truncated JSON, replug the cable rather than resetting in software.

### 3. Serial port identified — ✅

| device | port | USB ID |
|---|---|---|
| capper + pipette Arduino | `/dev/ttyACM0` | `2341:0043` Uno R3 |
| GRBL gantry | `/dev/ttyUSB0` | `1a86:7523` CH340 |

Both match `cub_xl_ben_pipette_capper.yaml`. Safer to name the stable paths, since `ttyACM0`/`ttyUSB0` swap on replug:

```
/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00   # capper + pipette
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0                                # gantry
```

Worth knowing beyond what the checklist asks: this is a **shared** port — capper *and* pipette both go through it — and upstream `PawduinoLink` arbitrates that, which is on the installed CubOS `496819c`. That was an unarbitrated hazard on the old pinned tree; it isn't now.

### 4. Nothing else holding the port — ✅, and structurally safe

Both ports were free before and after campaign 54. And this Pi was deliberately provisioned with **no systemd unit, no cron entry, no API server** — `sshd` is the only thing listening on a tailnet-facing address — so nothing grabs the port on boot or between runs. The only realistic contender is a second interactive session or a leftover Python process.

---

### ⚠️ The one thing I couldn't re-verify: the Pi is offline

```
rpi-5-des4   Online: false   LastSeen 2026-09-21T21:04:45Z
tailscale ping -> no reply (3x)    ssh -> connection timed out
```

Given the Pi shares a supply with the gantry, this may just be the machine switched off after your manual reset. So items 2 and 4 above are "as last verified on 2026-09-18", not "as of right now". Two commands settle both once it's back up:

```bash
ls -l /dev/serial/by-id/                       # 3 - both devices present?
sudo fuser -v /dev/ttyACM0 /dev/ttyUSB0        # 4 - silence means free
~/CubOS/.venv/bin/python -c "
from cubos.instruments.controllers.pawduino import PawduinoLink
l = PawduinoLink.acquire('/dev/ttyACM0', 115200); l.connect()
print(l.send_command(14))"                     # 2 - expect max_vol: 20.00
```

### The honest bottom line

All four gate items are satisfied — **pipette commands will be accepted and executed**, and campaign 54 showed every one of them producing a distance-scaling round trip including the first retraction. But that proves the *Arduino emitted the steps*, not that the motor turned, and it still doesn't. With your 13 V at the screw terminals retiring the missing-`VM` hypothesis, the fault is now confined to the segment between the TMC2209's input pins and the motor windings — **coil continuity, `EN` measured at the driver pin, or the chip itself.** Flashing the GEN2 image is the cheapest way to get the chip to answer that question directly (`DIAG`/`INDEX` and `open_load_a/b`); the rest of the plan is in [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0561306/cubos/docs/opentrons-pipette-wiring.md).

### Not done

No hardware access this session — the Pi is unreachable, and you asked a question rather than for a run. Nothing flashed, no wiring touched, no config or commit. Point 5 excluded as you asked.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---
