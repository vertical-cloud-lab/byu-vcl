# Firmware, P20 GEN2 constants, and the TMC2209 that answers nothing

*2026-09-15 → 2026-09-18 — 22 comments, migrated verbatim from [PR #171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171).*

Every comment below is reproduced exactly as posted, with its author and a link back to the original. `@`-mentions carry a zero-width space so that re-reading this file cannot notify anyone or re-trigger CI.

---

## @benwhitney5463 — 2026-09-15 21:45:43 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5688524600)

@claude I connected a 10 kilo-ohm resistor between A0 and A1. Run the trio, then report back. Feel free to delete the pipette_park_position. link the updated protocol below.  Next RUN_CURRENT_PERCENT to ~17, but hold off on running the trio until I tell you.  Set MAX_VOLUME/MIN_VOLUME for a p20, UL_TO_MM gravimetrically (~1.8 mm/µL to start), and mm_to_ul: 1.0 on the CubOS side so volume_ul stops being converted twice. I kept the cameras where they were. Take a few pictures during the run, and flip any photose vertically that came from the camera pointed at the room.

---

## @claude[bot] — 2026-09-15 21:46:04 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5688528247)

**Claude finished @benwhitney5463's task in 29m 34s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35027419556)

---
### Ran it — **12/12, campaign 26**. Then taught the firmware to use your resistor, and got the first straight answer out of the TMC2209: **it isn't communicating at all**

- [x] Reach the Pi, confirm CubOS state and ports
- [x] Delete the dead capper `park_position`
- [x] Add `--vflip`/`--hflip` to the camera harness, test-shot both cameras
- [x] Offline gates: `validate_setup` PASS · `--mock` 12/12 · `passive_shadow` **0 nominal, 0 tip-stuck**
- [x] **Hardware run — 12/12, `completed`**, every plunger command timed live
- [x] Firmware: `RUN_CURRENT_PERCENT` 17, p20 `MAX_VOLUME`/`MIN_VOLUME`, `UL_TO_MM` 1.8 — **flashed and verified**
- [x] CubOS side: `mm_to_ul: 1.0`
- [x] Commit configs, firmware, logs, frames ([`127e8f9`](https://github.com/vertical-cloud-lab/byu-vcl/commit/127e8f9))

```
Protocol complete — 12 steps executed.
```

Campaign 26, `21:51:38 → 21:56:41` UTC. Decapped vial_1, pressed onto A1, aspirated, parked, recapped vial_1, decapped vial_2, blew out, dropped the tip, capped vial_2, home. No capper retries, no alarms.

**No plunger motion was commanded after the reflash** — you said hold off, so the new constants are in and untested on the motor.

---

### The resistor is right, and it was inert. Here's the proof, and the fix

Campaign 26's plunger trace is **byte-for-byte campaigns 77 and 83** — `HOME` back in 0.520 s, the two downward commands stepping, all four upward ones refused in ~0.107 s. Nothing changed.

That's expected rather than disappointing. `setupMotor()` only ever *writes* TMC2209 registers and checks none of them, and no command in `Interface.cpp` exposed driver state. **The readback path your bridge creates had nothing asking it a question.** 10 kΩ is electrically fine, by the way — the driver sinks 0.5 mA to pull the line down, and at 9600 baud the RC isn't close to mattering.

So in the same reflash you asked for, I added `CMD_PIPETTE_DRIVER_STATUS = 29`. Five consecutive reads, immediately after flashing:

```
OK:{"msg":"Driver status","v":[0.00,0.00,-1.00]}
      comm = 0      flags = 0      current_scaling = -1 (unread)
```

### 🔴 `comm = 0` means the driver returned nothing at all

Not "replied but unconfigured" — the library's chain is `isCommunicating() → getVersion() == VERSION`, so 0 means no valid version byte came back. Two consequences, and the second one **retracts a hypothesis I gave you on 2026-09-08**:

- **None of `setupMotor()`'s six register writes has ever landed** — not on any run, ever. `setRunCurrent`, `setHoldCurrent`, `setMicrostepsPerStep`, `enableStealthChop`, `enableCoolStep`, `enable`. The chip has been on power-on defaults throughout.
- **So `setOperationModeToSerial()` never landed either**, which means `i_scale_analog` is still 1 and **the VREF pot is still in circuit**. My §4 worry — that correcting the UART pin would strand the driver at minimum current with its output stage off — is dead. That isn't what's happening.

Also worth knowing: `setMicrostepsPerStep(16)` never landing means MS1/MS2 straps decide, and their default is 1/8 — half what `STEPS_PER_MM 1592.0` assumes. The firmware already contradicts itself about this (`int backOffSteps = 796; // this is equal to 1mm`). **Check the first successful move against a ruler.**

### The two-minute discriminator

With the driver idle and powered, grab the plunger and try to turn it by hand.

| holding torque | reading | what to check |
|---|---|---|
| **none** | no coil current at all | **VM at the driver's screw terminal** (12 V — VDD from the Arduino is logic only, and the board enumerates and acks everything happily with VM absent), then the VREF pot, then coil continuity |
| **present** | driver is powered and energised, so `comm = 0` is the UART path alone | that PDN_UART really lands on **A1**, and the bridge itself |

The new `flags` word reports `open_load_a`/`open_load_b` — the coil-continuity answer without a meter — but those bits arrive *in a reply*, so they only mean anything once `comm` is non-zero. Fix `comm` first, then re-read 29 and it'll tell you about the coils directly.

```python
from cubos.instruments.controllers.pawduino import PawduinoLink
link = PawduinoLink.acquire("/dev/ttyACM0", 115200); link.connect()
print(link.send_command(29, timeout=15))
```

---

### The firmware — backed up first, and the backup proved the provenance

Before writing anything I read the flash off the board. Parsed and compared byte-for-byte, its **16 308 program bytes are identical to a local build of upstream `228615b`**. So the board really was running stock upstream, and the VCL image is a *provably* minimal delta — not a leap onto an unknown tree. Backup committed at [`cubos/firmware/flash_20260915T220346Z.hex`](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/firmware/flash_20260915T220346Z.hex), with a one-command restore in the [README](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/firmware/README.md).

🔴 **Upstream `main` does not compile.** `228615b` gives `mixInPlace`'s `dwell_ms` a default argument in both the header *and* the definition, which is a hard C++ error. The patch carries the one-line fix; worth sending upstream, since as it stands nobody can build `main`.

| constant | was | now | why |
|---|---|---|---|
| `MAX_VOLUME` | 300.0 | **20.0** | `STATUS` now reads `max_vol: 20.00` — that's the confirmation the new image is live |
| `MIN_VOLUME` | 5.0 | **1.0** | this clamp is why `ASPIRATE 0.5` always landed at 35.45: 0.5 clamped up to 5 |
| `UL_TO_MM` | 0.1098 | **1.8** | your number. = `PRIME_POSITION` 36.0 / 20 µL, so full scale lands the plunger at 0.0. **Starting estimate, not a calibration** |
| `RUN_CURRENT_PERCENT` | 50 | **17** | ~1.25 A peak vs the 500 mA peak science-jubilee specs for a Gen2 OT-2 motor |
| `HOLD_CURRENT_PERCENT` | 30 | **10** | ⚠️ **one change beyond your ask, and it's forced** |

That last row: the TMC2209 library maps hold `0-100 → IHOLD 0-31` **independently** of run current, not as a percentage *of* it. Leaving hold at 30 against a run of 17 would draw more current standing still than moving. 10 keeps your original 0.6 hold/run ratio. Say the word if you'd rather it were something else.

**Left alone deliberately:** `PRIME_POSITION` 36.0, `BLOWOUT_POSITION` 44.0, `DROP_TIP_POSITION` 55.0. They're mechanical plunger positions, and `UL_TO_MM` 1.8 is *derived* from `PRIME_POSITION` — moving one means re-deriving the other. They may still be P300 figures; a p20's usable travel is shorter, and `DROP_TIP_POSITION` 55.0 is worth checking against the real plunger before anything relies on the ejector.

Toolchain went into a user venv (`~/.venvs/pio`, toolchain under `~/.platformio`) — no sudo, nothing system-wide, same philosophy as the mpremote venv on the other Pi.

### CubOS: `mm_to_ul` 0.025 → 1.0

Checked before changing it: `mm_to_ul` is read in exactly three places, all `volume_ul * mm_to_ul` in `aspirate`/`dispense`/`mix`, and nowhere else. So 1.0 is a clean pass-through and the single conversion stays in the firmware where the calibration constant lives. The chain now closes:

```
protocol volume_ul  20.0
  x mm_to_ul 1.0    -> ASPIRATE 20.0        (CubOS)
  x UL_TO_MM 1.8    -> 36.0 mm of plunger   (firmware)
                    = PRIME_POSITION, i.e. exactly full scale
```

`2544 passed, 17 skipped, 0 failed`, and all four offline gates still green.

⚠️ **One thing that's still wrong and I didn't touch:** `prime_position: 5.0`, `blowout_position: 7.0`, `drop_tip_position: 10.0` in the same CubOS entry are still `# placeholder`, and unlike `mm_to_ul` they're sent to the firmware as **absolute** `MOVE_TO` targets. The firmware's planes are 36 / 44 / 55 — which is precisely what CubOS's `p300_single_gen2` carries, marked "calibrated from PANDA-BEAR". So a `blowout` asks for 7.0 while the blowout plane is 44.0. Matching them is the obvious next step, but it changes real motion and you didn't ask, so it's flagged rather than done.

---

### The park position — I deleted the gantry one, not the protocol one

Worth being explicit, because the names collide. I removed **`vial_capper_decapper.park_position`** from the gantry file: that's the one CubOS `main` ignores and warns about (`decap/cap no longer park; delete this key`), and the one I said on 2026-09-15 was "deliberately kept, your call". The warning is now gone from the validate output.

I left the protocol's `positions: park_position:` and `pipette_park:` alone — those are named protocol positions used by steps 1 and 5, and deleting either removes real motion from the run. If you meant one of those, say which and I'll do it.

One rollback cost, recorded inline: `PawduinoCapper.__init__` at `cbc33dc` takes `park_position` as a **required** argument, so going back to `cbc33dc` now means putting it back first — the fallback is the `[-10, -10]` placeholder, outside the working volume.

**Updated protocol:** [`cubos/configs/protocol/vcl/pipette_test.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/configs/protocol/vcl/pipette_test.yaml) — unchanged in body; the edit was in [`cub_xl_ben_pipette_capper.yaml`](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml).

---

### Cameras — 7 of 12 frames, and the vflip works

`--vflip cam1_csi1` is in the harness now, applied by `rpicam-still` at capture time so the file on disk is already the right way up. `cam0_csi0` got all six; `cam1_csi1` timed out at the 20 s limit on five of six, then succeeded on the last.

Not the flag — the same flag worked in the pre-run test shot (0.57 s) and on the final in-run capture (0.58 s). Most likely buffer contention on a **1 GB** Pi 5 driving two 4608×2592 sensors with CubOS resident. The harness's hard rule held: no camera failure touched the protocol, and the run completed 12/12. But each timeout cost 20 s of stationary wall clock, which is why this run took 5m 04s against campaign 77's 4m 03s. Worth a lower capture resolution or one camera at a time next run.

**step 4, `aspirate` — `cam0_csi0`:**

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/results/pipette_test_20260915/frames/step04_aspirate__cam0_csi0.jpg?raw=true)

**step 9, `drop_tip` — `cam1_csi1`, flipped:**

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/results/pipette_test_20260915/frames/step09_drop_tip__cam1_csi1.jpg?raw=true)

I **cropped the `cam1_csi1` frames** to the machine before committing — the left third of that camera's field is the room, with a lab member at a desk in it, and this repo is public. Nothing you need is in the discarded part, and the uncropped originals are still on the Pi in `/tmp/run_frames` if you want them.

---

### ✅ Machine state

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | both returned to vials 1–2 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home before the next run. |
| `$130/$131/$132` · `$20` | 409.000 / 309.000 / 124.000 · `1` — matches the gantry file |
| Plunger | `max_vol: 20.00` — new firmware live. **No motion commanded after the flash.** |
| Capper path | re-verified after the reflash: hello, sensor and magnet all answer |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |

~19 mm of one-way plunger travel was commanded during the run itself (prime + aspirate); retraction is still refused, so none came back. Worth an eyeball at the plunger and its coupling.

### Committed — [`127e8f9`](https://github.com/vertical-cloud-lab/byu-vcl/commit/127e8f9)

- [`cubos/firmware/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/127e8f9/cubos/firmware) — the [README](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/firmware/README.md), the [patch](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/firmware/panda-arduino-p20-and-driver-status.patch) (verified to apply clean to a fresh clone of `228615b` and build), the flashed hex, and the pre-change backup
- [`cubos/patches/p20-mm-to-ul-passthrough.patch`](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/patches/p20-mm-to-ul-passthrough.patch) + a [README entry](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/patches/README.md)
- [`cubos/results/pipette_test_20260915/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/127e8f9/cubos/results/pipette_test_20260915) — [write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/results/pipette_test_20260915/README.md), hardware log, plunger trace, gates, all seven frames; campaign CSVs in [`campaign_26_20260915_215138/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/127e8f9/cubos/results/campaign_26_20260915_215138)
- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/127e8f9/cubos/docs/opentrons-pipette-wiring.md) — new §9, including the retraction of the §4 hypothesis

The committed files were pulled back onto the Pi and all four gates re-run from them — PASS, 12/12, 0 interferences both ways. What's on the branch is what's on the machine.

### Not done

No plunger motion since the reflash, and no protocol run since — you said hold off, so the p20 constants and the current change are untested against the motor. `UL_TO_MM 1.8` is an estimate awaiting a gravimetric calibration; the CubOS `prime`/`blowout`/`drop_tip` positions are still placeholders. The heat sink isn't fitted. No wiring touched. Still no camera clearly on the tip rack, so whether a tip seated at A1 and where the undropped tip went need your eyes.

Nothing upstreamed: the `mixInPlace` compile error to BU-KABlab, the Cubware pin-diagram shift to Ursa, the hover clamp to Ursa, and the `P20_config.json` `mm_to_ul` finding to machineagency are all still unfiled. Say the word on any and I'll write them up.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-16 22:16:45 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5705358341)

@claude run the trio again this time with the current percent at 17

---

## @claude[bot] — 2026-09-16 22:17:09 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5705362338)

**Claude finished @benwhitney5463's task in 19m 51s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35156870574)

---
### Ran it — **11 of 12 steps, campaign 36**. Then the closing `home` failed, and the machine is parked in `Alarm`. Separately: `RUN_CURRENT_PERCENT 17` is in the flashed image but never reaches the chip

- [x] Reach the Pi — CubOS `496819c` + 3 patches, both ports free
- [x] Confirm the p20 firmware is live — `max_vol: 20.00` ✅
- [x] Re-read the TMC2209 over your A0↔A1 bridge — **`comm = 0`**, five consecutive reads
- [x] Offline gates: `validate_setup` PASS · `--mock` 12/12 · `passive_shadow` **0 nominal, 0 tip-stuck**
- [x] GRBL settings read live — all ten critical values match the gantry file
- [x] **Hardware run — steps 0–10 executed**, 10/10 camera frames, every plunger command timed
- [x] Root-cause the homing failure from the controller's own pin state
- [x] Leave the machine safe, commit logs + frames ([`b7da50c`](https://github.com/vertical-cloud-lab/byu-vcl/commit/b7da50c))

Campaign 36, `22:21:14 → 22:26:12` UTC. Decapped vial_1, pressed onto A1, aspirated, parked, recapped vial_1, decapped vial_2, blew out, dropped the tip, capped vial_2 — all clean, no capper retries, no alarms. Then step 11.

---

### 🔴 The closing `home` failed. Machine left in `Alarm` on purpose — please don't re-home until you've looked at Y

```
ERROR during execution: Homing timed out after 90 seconds
```

**What the controller says now**, six samples over 3 s, identical every time:

```
<Alarm|WPos:409.000,309.000,124.000|FS:0,0|Pn:X|WCO:-409.000,-309.000,-124.000>
```

`Pn:X` is GRBL's pin-state field — **the X limit switch is currently asserted.** And this is a clean before/after: the same read taken *before* the run carried **no `Pn:` field at all**. (`WPos` isn't a real position — the board resets when the port opens and reports `−max_travel` on every axis.)

**The attempts**, from the driver's own log:

```
16:24:13.626  $H
16:24:55.412  Homing failed, trying again...      (41.8 s)   <- GRBL in Alarm
16:24:55.412  $H
16:25:07.467  Homing failed, trying again...      (12.1 s)
16:25:07.467  $H
16:25:47.934  Homing failed, trying again...      (40.5 s)
16:25:47.934  $H
16:25:59.995  Homing failed, trying again...      (12.1 s)
16:25:59.995  $H
16:26:10.505  Homing timed out
```

### Reading: Z homed, X found its switch, **Y did not**

Stock GRBL homes Z first, then X and Y together. Settings read live: `$23=0` (home toward max), `$27=3.0` (pull-off), `$25=1000` (seek), `$131=309`.

- **Z reached its switch** — or X would never have moved. It reads clear now because the cycle pulls off 3 mm at the end.
- **X reached its switch** — `Pn:X`, still holding it.
- **Y did not** — no `Pn:Y`. GRBL aborts once an axis exceeds `1.5 × $131` = 463 mm without triggering, ~28 s at `$25`. That fits the ~41 s attempts (Z cycle first, then X+Y).

One thing that looks alarming and isn't: `Pn:Z` appears all through the run log. Every `travel_z: 124` pose sits exactly on Z's max switch. That's normal, not a fault.

### 🔑 This is the first homing failure ever recorded on this Pi — and the *opening* home of the same run worked

The gantry log covers the whole life of this Pi's install:

| when | result |
|---|---|
| 2026-09-15 15:52:15 | Homing completed ✅ (campaign 26, step 0) |
| 2026-09-15 15:56:39 | Homing completed ✅ (campaign 26, step 11) |
| **2026-09-16 16:21:51** | **Homing completed ✅ (this run, step 0)** |
| 16:24:13 → 16:26:10 | 4 retries, then timeout ❌ (this run, step 11) |

2.5 minutes apart. And here's why that isn't a contradiction: **the protocol only ever visits deck x 154–284, y 13–60. `home` is the only command that drives to the far corner (409, 309)** — so 11 steps of normal motion can pass and the closing home still fail.

### Two candidates, both photographed

I have cameras now, so this isn't inference from nothing. Both were inside the envelope during the run:

**The p20 is on the bench, tethered into the moving head by its FC-10P ribbon.** Its body is legible as `P20 GEN2` at the bottom right. A tether sized for the protocol's working area doesn't have to reach (409, 309):

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/results/pipette_test_20260916/frames/step10_cap__cam0_csi0.jpg?raw=true)

**A hand was in the work area** — expected, you said you'd be watching and holding the pipette, but it's a candidate obstruction and belongs in the record:

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/results/pipette_test_20260916/frames/step09_drop_tip__cam0_csi0.jpg?raw=true)

Those are hypotheses. What's *measured* is: Y didn't reach its switch, X is sitting on its own, and nothing like this has happened on this machine before.

### Why I stopped rather than retrying

`Alarm` is the safe state — GRBL refuses motion in it. Re-homing drives Y into whatever stopped it for ~28 s per attempt, and that's already happened five times. Clearing it needs eyes on the machine.

**To recover**, in this order:

1. **Look at Y's path to Y 309** — the ribbon tether, a dropped tip, anything on the far rail. Clear it.
2. Re-home **watching the machine, ready to cut power**:
   ```bash
   cd ~/CubOS && .venv/bin/python -c "
   from cubos.gantry.gantry_driver.driver import GrblCncMill
   m = GrblCncMill('/dev/ttyUSB0'); m.connect(); m.unlock(); m.home()"
   ```
3. **If it fails again**, the question becomes whether X's switch is genuinely stuck rather than just occupied. Jog X away from max and re-read: `Pn:X` clearing means the carriage was simply parked on it (normal); `Pn:X` persisting with the carriage moved means the switch or its wiring is the fault.

---

### On the current percent — 17 is in the image, and the chip never receives it

The flashed firmware *is* the VCL p20 build: `STATUS` returns `max_vol: 20.00` against the stock 300.0, and the patch sets `RUN_CURRENT_PERCENT 17`. But read five times before the run and again after:

```
OK:{"msg":"Driver status","v":[0.00,0.00,-1.00]}
      comm = 0      flags = 0      current_scaling = -1
```

`comm = 0` is the firmware's *"no reply at all"* case. `setRunCurrent(17)` is a UART register write — it never landed. **The chip is on power-on defaults with the VREF pot setting current, exactly as it was at 50**, so this run is electrically identical to campaign 26. The 17 can't be evaluated until `comm` is non-zero.

⚠️ **Don't read `flags = 0` as "no faults."** `getDriverDiagnostics()` only reads the status register when `comm > 0`; `current_scaling = -1` is the explicit unread sentinel and `flags` carries no information either. The `open_load_a`/`open_load_b` coil bits — the continuity answer without a meter — only mean something once the driver replies.

The two-minute discriminator is unchanged: **with the driver idle and powered, try to turn the plunger by hand.** No holding torque at all ⇒ no coil current ⇒ check VM at the driver's screw terminal (12 V; the Arduino's VDD is logic only), then the VREF pot, then coil continuity. Holding torque present ⇒ the fault is the UART path alone ⇒ check that PDN_UART really lands on **A1**, and the bridge itself.

### The plunger feedback

| step | command | dt | stepped? |
|---|---|---|---|
| `connect()` | `STATUS` | 0.008 s | — |
| `connect()` | `HOME` | 0.520 s | no — back-off only, switch asserted |
| `connect()` prime | `MOVE_TO 5.0` | **3.355 s** | **yes** |
| `pick_up_tip` | `MOVE_TO 0.0` | 0.109 s | no — refused (upward) |
| `aspirate` | `ASPIRATE 20.0` | **5.962 s** | **yes** → reports 36.00 |
| `blowout` | `MOVE_TO 7.0` | 0.107 s | no — refused |
| `drop_tip` | `MOVE_TO 10.0` | 0.109 s | no — refused |
| `drop_tip` | `MOVE_TO 5.0` | 0.107 s | no — refused |

Same shape as campaigns 77, 83 and 26. **The two moments to have watched: ~3.4 s at startup before the gantry homed, and ~6 s down in vial_1.** (Timing proves the Arduino toggled STEP — not that the motor turned.)

### ✅ One thing that did change: the volume chain now carries real microlitres

This is what `mm_to_ul: 1.0` + `UL_TO_MM 1.8` + `MIN_VOLUME 1.0` were for:

```
protocol volume_ul  20.0
  x mm_to_ul 1.0    -> ASPIRATE 20.0      (was ASPIRATE 0.5)
                       reply v:[20.00, 36.00]
```

Every earlier trace sent `0.5`, had it clamped up to the P300's `MIN_VOLUME 5.0`, and landed at 35.45. Now 20.0 goes through un-clamped and comes back as 20.00.

The 36.00 landing is `PRIME_POSITION`, and it's the limit switch again, not a conversion error: `aspirate()` drives *down* to 36.0 first, then *up* to `36.0 − 20 × 1.8` = 0.0. The upward leg is refused. Fix the plunger switch and that becomes a real 20 µL draw.

### ✅ Cameras: 10 of 10, all under 0.7 s

Against 7 of 12 with five 20 s timeouts last time. Captured after `pick_up_tip`, `aspirate`, `blowout`, `drop_tip` and `cap vial_2`, plus a pair after the homing failure.

**`cam1_csi1` frames are committed cropped** — that camera looks across the bench into the room and a lab member is in frame on the left of every shot, and this repo is public. Uncropped originals are on the Pi in `/tmp/run_frames`. `cam0_csi0` is committed as captured. Neither camera is aimed at the tip rack, so whether a tip seated at A1 and where the undropped tip went are still open.

### ✅ Machine state

| | |
|---|---|
| GRBL | **`Alarm`, `Pn:X`** — left deliberately, see above. Re-home only after checking Y. |
| Caps | **both returned** — steps 6 and 10 (`cap vial_1`, `cap vial_2`) both completed |
| Electromagnet | off — `CMD_EMAG_OFF` → `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| `$20` soft limits | `1` · `$130/$131/$132` = 409.000 / 309.000 / 124.000, matching the gantry file |
| Plunger | `max_vol: 20.00`, `homed: 0`; ~19 mm of one-way travel commanded, none returned |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |

### One incidental find worth upstreaming

The failure path exposed that `_best_effort_retract_to_safe_z()` still raises `KeyError: "Unknown instrument 'PawduinoCapper'"` at `496819c` — it hands an instrument *object* to a function expecting a *name*, so the outer safety retract is dead code upstream. It didn't matter here (the failing step was `home`, which commands no tool-relative motion), but it's a real bug in Ursa's abort path.

### Committed — [`b7da50c`](https://github.com/vertical-cloud-lab/byu-vcl/commit/b7da50c)

- [`cubos/results/pipette_test_20260916/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/b7da50c/cubos/results/pipette_test_20260916) — the [write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/results/pipette_test_20260916/README.md), the [hardware log](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/results/pipette_test_20260916/run_hardware.log), the [GRBL exchange with timestamps](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/results/pipette_test_20260916/mill_control_thisrun.log), the [G-code](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/results/pipette_test_20260916/gantry_command_thisrun.log), the [plunger trace](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/results/pipette_test_20260916/plunger_trace.json), the [`$$` + Arduino snapshot](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/results/pipette_test_20260916/grbl_and_arduino_20260916.json), all four gate logs and the [12 frames](https://github.com/vertical-cloud-lab/byu-vcl/tree/b7da50c/cubos/results/pipette_test_20260916/frames); campaign CSVs in [`campaign_36_20260916_222114/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/b7da50c/cubos/results/campaign_36_20260916_222114)
- [`cubos/tools/run_with_camera_and_plunger_trace.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/tools/run_with_camera_and_plunger_trace.py) — thin composition of the two existing tools so a run gets frames *and* plunger timing in one pass
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/README.md) — status section

**Your three config files needed no edit at all** — the trio ran exactly as committed at `127e8f9`. The branch is round-tripped back onto the Pi, so what's there is what ran.

### Not done

**The machine is not recovered** — it's in `Alarm` with `Pn:X`, and clearing that needs someone to look at Y's path first. I didn't retry homing and didn't jog.

The trio's 12th step never ran, so the gantry is not at a known position. No wiring was touched, no firmware flashed, no config changed. `drop_tip` still releases 35 mm above the slot pending a `tip_disposal` deck entry; the CubOS `prime`/`blowout`/`drop_tip` positions are still placeholders (5/7/10 against the firmware's 36/44/55). Nothing is upstreamed: the `mixInPlace` compile error to BU-KABlab, the Cubware pin-diagram shift and the hover clamp to Ursa, the `P20_config.json` finding to machineagency, and now the `_best_effort_retract_to_safe_z` bug. Say the word on any and I'll write them up.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-17 14:47:42 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5716350545)

@claude summarize the troubleshooting we've already done on the pipette (be brief) an give potential next steps.

---

## @claude[bot] — 2026-09-17 14:48:08 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5716356734)

**Claude finished @benwhitney5463's task in 2m 27s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35235974761)

---
### Pipette: where we are, and what I'd do next

- [x] Re-read the durable record ([`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/docs/opentrons-pipette-wiring.md), [firmware README](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/firmware/README.md), the run write-ups)
- [x] Summarize
- [x] Rank the next steps

**No hardware access this session** — you asked for a summary, so nothing was run, connected to, or changed.

---

### The one-line version

**The plunger has never physically turned.** Everything *above* the motor is proven working; the motor circuit itself has never been confirmed alive. Two independent faults, not one.

### Ruled out — measured, not assumed

| | how |
|---|---|
| CubOS, the serial link, the shared `/dev/ttyACM0` | the Arduino answers every command; the capper shares the port cleanly |
| Arduino STEP output | raw-step probe emitted **1592 steps at exactly the commanded rate** ([`pipette_driver_probe.py --motor-test`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/tools/pipette_driver_probe.py)) |
| Arduino pin map | Cubware's diagram was off by one (UART→A1, STEP→A2, DIR→A3, EN→A4) — you fixed it |
| 10-pin pipette header layout | agrees across three sources; a 180° connector flip is excluded by the switch history |
| coil *pairing* | a mis-paired coil buzzes and vibrates. Total silence ⇒ no coil current at all |
| ~~"correcting the UART pin stranded the driver at min current"~~ | **retracted** — `comm = 0` means `setOperationModeToSerial()` never landed, so the VREF pot is still in circuit |
| ~~"the DIR line is one-way"~~ (my 08-31 claim) | **retracted** — it was the limit switch gating the *up* direction |

### Confirmed broken — two separate things

1. **No coil current.** No buzzing, no motion, on any run.
2. **The limit-switch loop is open** (D9 reads asserted). `stepMotor()` gates the *up* direction on D9, so every retract is refused in ~0.11 s and `HOME` fake-succeeds in 0.52 s without moving. This is a pin 6↔7 continuity question and is **independent of #1** — fixing the motor won't fix it.

### Done, and so far inert

Your 10 kΩ A0↔A1 bridge ✅ · firmware taught to read the driver (`CMD 29`) ✅ → **`comm = 0`, five consecutive reads.** The TMC2209 returns nothing, so *none* of `setupMotor()`'s six register writes has ever landed. `RUN_CURRENT_PERCENT 17` is in the flashed image but never reaches the chip — campaign 36 was electrically identical to campaign 26. (⚠️ `flags = 0` is **not** "no faults" — it's unread, and `current_scaling = -1` is the sentinel saying so.)

---

### Next steps, cheapest first

**1. The two-minute discriminator — holding torque.** Driver idle and powered, try to turn the plunger by hand. **No resistance at all** ⇒ no coil current ⇒ go to 2. **Resistance present** ⇒ the driver is energised and `comm = 0` is the UART path alone ⇒ skip to 4.

**2. 🔑 Measure 12 V at the driver's VM screw terminal — not at the brick.** This is the hypothesis I'd test first now, because it's the only one that explains **both** symptoms with one cause. A TMC2209 takes its internal logic supply from the *motor* rail through its own regulator; the 5 V logic pin powers only the pin drivers. A driver with no VM will happily accept STEP/DIR, ack everything, drive no coils, **and answer nothing on UART** — exactly `comm = 0` plus silence. Check the terminal screws are actually clamping wire and not insulation.

**3. The VREF pot.** Since serial mode never engaged, the pot is *the only thing setting current*. Fully counter-clockwise = no torque, no sound. Turn it up (then back down once UART works and `RUN_CURRENT_PERCENT 17` takes over), and fit the Adafruit 1515 heat sink.

**4. If VM and torque are both fine, it's the UART path.** Three things to check, in order: EN measured at **0 V at the driver pin** (not the Arduino header); PDN_UART genuinely landing on **A1**; and the **MS1/MS2 straps**, which select the driver's UART *address* — the firmware calls `setup()` with the default address 0, so MS1 and MS2 must both be low or the chip will never answer. Dropping the bridge from 10 kΩ to the 1 kΩ the library's README specifies is a cheap variation if all three check out.

**5. Then re-read `CMD 29`.** Once `comm > 0`, `open_load_a`/`open_load_b` answer the coil-continuity question directly — no meter needed:
```python
from cubos.instruments.controllers.pawduino import PawduinoLink
link = PawduinoLink.acquire("/dev/ttyACM0", 115200); link.connect()
print(link.send_command(29, timeout=15))
```

**6. The limit switch, separately.** Continuity pin 6 → Arduino GND and pin 7 → D9, and confirm the contact is **normally closed** (LOW at rest). Until D9 reads LOW the plunger is a one-way ratchet — `blowout` and both `drop_tip` legs can't execute regardless of the motor.

### Queued behind the first real movement

- **Check it against a ruler.** `setMicrostepsPerStep(16)` never landed, so MS1/MS2 decide and their default is 1/8 — half what `STEPS_PER_MM 1592` assumes. Expect a possible 2× error.
- **CubOS `prime`/`blowout`/`drop_tip` are still `5.0 / 7.0 / 10.0` placeholders** against the firmware's real planes of **36 / 44 / 55**. They're sent as absolute targets, so they're wrong today — an easy fix, but it changes real motion so I've left it.
- **`UL_TO_MM 1.8` is an estimate**, not a calibration — gravimetric check once liquid actually moves.
- `drop_tip` still ejects 35 mm above the slot, pending a `tip_disposal` deck entry.

### ⚠️ Unrelated but blocking a run

The machine is still in **`Alarm` with `Pn:X`** from campaign 36's failed closing `home` — Y didn't reach its switch. Please look at Y's path to (409, 309) before re-homing; details and the recovery sequence are in the [campaign 36 write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7da50c/cubos/results/pipette_test_20260916/README.md).

**Not done:** nothing was run, measured, wired or committed this session — summary only. Say the word when you want any of the above executed on the machine.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-17 21:55:51 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5721762440)

@claude Try the trio again. I fixed the error from the last run, so the machine should be able to home. When I pull the plunger manually, it moves freely when plugged in and on, so there is no current going through. address https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5719634392 and make values match in all locations for the P20 GEN2

---

## @claude[bot] — 2026-09-17 21:56:12 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5721765761)

**Claude finished @benwhitney5463's task in 31m 33s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35279358592)

---
### I couldn't run it — the Arduino's serial link is corrupting data, so `run_protocol` aborts at instrument connect. The P20 GEN2 alignment is done, and your hand test plus Alex's review pin the driver fault on one measurement

- [x] Read [Alex's review](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5719634392) — **two of my conclusions don't survive it**
- [x] Reach the Pi; confirm CubOS `496819c` + 3 patches, both ports free
- [x] Pull the authoritative P20 GEN2 numbers from **Opentrons `pipetteModelSpecs.json`**
- [x] Align every location: firmware, CubOS `p20_single_gen2`, docs
- [x] Fix the TMC2209 read path + vendor the library so a rebuild can't lose it
- [x] Offline gates — `pytest` 2544/0, `validate_setup` PASS, `--mock` 12/12, `passive_shadow` 0 + 0
- [x] Commit ([`2fdea46`](https://github.com/vertical-cloud-lab/byu-vcl/commit/2fdea46), [`b7e0130`](https://github.com/vertical-cloud-lab/byu-vcl/commit/b7e0130))
- [ ] **Hardware run and reflash — both blocked on the same fault**

**No motion was commanded.** The gantry port was opened read-only for `?`/`$$`, the plunger was never actuated, and the Arduino's flash is unchanged — `avrdude` never synced, so no erase or write happened.

---

### 🔴 The blocker: `/dev/ttyACM0` is dropping bytes in both directions

`PawduinoLink.connect()` is the exact gate `run_protocol` hits — right after validation, **before** the gantry port is opened. Read-only, twice:

```
attempt 1: FAILED -> UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe1 in position 1
attempt 2: FAILED -> PawduinoLinkConnectionError: Pawduino on /dev/ttyACM0 did not
                     answer hello: Timed out (5.0s) waiting for response to command 0
```

So this is a hard block, not my judgement call — a run aborts with zero steps.

**The firmware is alive and is the right image.** Replies start correctly and get cut off:

```
badjson  OK:{"homed":0,"pos":0.00,"max_vol":2
badjson  OK:{"homed":0,"pos":0.00,"max_vol":2
```

`max_vol` starting with `2` confirms the 2026-09-15 p20 image is running (stock reports 300.00), and one probe got as far as `"Hello from Pawduino!"`. The sketch runs and answers; the bytes are lost between the ATmega328P and the Pi.

| measurement | result |
|---|---|
| `STATUS` (cmd 14) round-trips that parse | **0 of 25** |
| idle traffic, nothing sent | 10 bytes in 8 s — so the board is **not** babbling |
| `avrdude -n`, `-c arduino` @ 115200/57600/19200 and `-c stk500v1` | fails at every one, `resp=` different each attempt |
| `USBDEVFS_RESET` | re-enumerates, link still broken |

Two details worth keeping: it's **not line noise** — separate runs returned near-identical byte sequences, so it's structured data; and one early capture was the board's own **USB serial-number string descriptor in UTF-16LE** (`…3335351018130` with interleaved NULs) arriving on the *data* endpoint, which is pathological at the USB layer rather than sketch output.

**This predates my session.** `dmesg` shows the board re-enumerating at kernel timestamp 510334 against an uptime of 511786 s when I first queried — about five minutes before I made contact. Same board: USB serial `03535343335351018130`, unchanged.

### ⚠️ And it's intermittent, which makes it worse

A final check at the end of the session got further:

```
PawduinoLink.connect(): OK
  cmd 7   capper line-break sensor   -> OK:Ready
  cmd 14  pipette STATUS             -> RAISED UnicodeDecodeError: 0x8d at position 13
```

`connect()` succeeded — but `cmd 7` returned **`OK:Ready`**, the stale boot banner, not `OK:{"value1":0}`. The stream is running a reply behind itself.

That's the real reason not to attempt the trio. A clean refusal every time would be safe; an intermittent link can get **past** connect and then mis-read the cap sensor — and that interlock is exactly what has kept the pipette out of a capped vial since 2026-08-03. A sensor read that returns the wrong string is worse than one that raises.

#### What to check, cheapest first

1. **Unplug and replug the Arduino's USB cable.** A `USBDEVFS_RESET` from the Pi is *not* a power cycle — neither the 16U2 nor the 328P loses state. Then one `STATUS` should return valid JSON.
2. **The 5 V rail.** The TMC2209's `VDD` comes from the Arduino's 5 V, which comes from USB. Added load or a partial short makes the rail sag, and sagging 5 V looks exactly like dropped UART bytes.
3. **Anything the rewiring put on `D0`/`D1`, or near `RESET`.** `D0`/`D1` are the hardware UART that both the sketch *and* the bootloader use — a wire there corrupts both, which is what I'm seeing. A wire near `RESET` gives erratic resets, which would also explain avrdude never syncing.
4. **Swap the USB cable** for a known-good one.

---

### ✅ P20 GEN2: the numbers now agree in all three places

Not derived this time — read from **Opentrons `shared-data/pipette/definitions/1/pipetteModelSpecs.json`**, keys `p20_single_v2.0`/`2.1`/`2.2` (identical positions in all three). Opentrons states plunger planes as signed offsets in a frame whose `top` is the home reference; the firmware and CubOS both measure *downward* from home, so each value is `top − <field>` with `top = 19.5`.

| | Opentrons | **P20 GEN2** | firmware was | CubOS was |
|---|---|---|---|---|
| prime / bottom | `bottom` −8.5 | **28.0** | 36.0 | 5.0 *(placeholder)* |
| blowout | `blowout` −13 | **32.5** | 44.0 | 7.0 *(placeholder)* |
| drop tip | `dropTip` −27 | **46.5** | 55.0 | 10.0 *(placeholder)* |
| mm per µL | `ulPerMm` → 0.746 µL/mm | **1.34** | 1.8 | — |
| max / min volume | | 20 / 1 µL | 20.0 / 1.0 ✅ | 20.0 / 1.0 ✅ |

**The CubOS placeholders were worse than a mis-scaling.** `prime 5.0` / `blowout 7.0` / `drop_tip 10.0` are sent to the firmware as **absolute `MOVE_TO` targets**, so they didn't mis-scale a move — they named the wrong destination, 23–36 mm short of the planes a P20 GEN2 plunger actually uses.

Two cross-checks that `1.34` is derived rather than guessed:

- `1 / 0.746 = 1.34`, and 0.746 µL/mm is the asymptote of Opentrons' own `ulPerMm` table. **The same method on the P300 gives 9.1 µL/mm — reproducing `UL_TO_MM 0.1098`**, the one constant in this firmware that was independently calibrated. So the method is validated against a known-good value.
- A full-scale 20 µL aspirate travels `20 × 1.34 = 26.8 mm` up from `PRIME 28.0`, landing at **1.2 mm** — inside the 28 mm stroke with a small dead band, as Opentrons has it. The old 1.8 was only `36.0 / 20`, i.e. read off a P300 plane.

**Every plane moved down, so every commanded plunger travel is now shorter than before** — the safe direction — and the ordering `0 < prime < blowout < drop_tip` that `aspirate`/`dispense`/`moveTo` rely on is preserved. Verified end to end against the installed tree:

```
CubOS p20_single_gen2: zero=0.0 prime=28.0 blowout=32.5 drop_tip=46.5 mm_to_ul=1.0
20 uL aspirate -> ASPIRATE arg = 20.0 * 1.0 = 20.0   (microlitres, pass-through)
firmware applies UL_TO_MM 1.34 -> 26.8 mm from PRIME 28.0 -> lands at 1.2 mm
```

⚠️ **Nominal, not calibrated** — Opentrons' figures for the model, not a measurement of this unit. `UL_TO_MM` still needs a gravimetric check.

#### Current: the sense resistor is 0.05 Ω, and my 500 mA target wasn't Opentrons'

| percent | CS | I_rms | I_peak | |
|---|---|---|---|---|
| 50 | 15 | 1.64 A | **2.32 A** | stock — over the **breakout's** 2 A rating, not just the motor's |
| 17 | 5 | 0.62 A | 0.87 A | what I set on 2026-09-15 |
| **20** | **6** | **0.72 A** | **1.02 A** | **`RUN_CURRENT_PERCENT`** = Opentrons `plungerCurrent` 1.0 A |
| **5** | **1** | **0.21 A** | **0.29 A** | **`HOLD_CURRENT_PERCENT`** = Opentrons `idleCurrent` 0.3 A |

Hold is mapped to IHOLD *independently* of run current by this library, not as a percentage of it, so the two have to be chosen together. ⚠️ **Fit the Adafruit 1515 heat sink before running at this current.**

---

### 🔴 Two things I got wrong, corrected in place

**`comm = 0` was never evidence of anything.** I read it as proof that none of `setupMotor()`'s register writes had ever landed, and retracted an earlier hypothesis on that basis. A read over `SoftwareSerial` on an AVR **cannot** succeed with the janelia library whatever the wiring: `write()` runs `cli()` so the Arduino never hears its own transmission, and `sendDatagramBidirectional()` then discards the first four bytes of the driver's *real* reply as if they were that echo — `readReply()` waits for eight more, times out, retries 5×, done. I confirmed the code does exactly this. **So the writes may have been landing all along**, and the earlier hypothesis is back in play. A diagnostic whose success path is unreachable isn't a diagnostic; I should have checked that before trusting it.

**The sense resistor is 0.05 Ω, not the 0.11 Ω I assumed** — so every current figure I gave on 2026-09-09 was off, and the stock 50 was worse than I said.

`cubos/patches/tmc2209-softwareserial-read.patch` fixes the read path, vendored into `lib/TMC2209/` so a `pio pkg` refresh can't silently drop it. **Proven, not assumed:** a sentinel `#error` in the `lib/` copy fails the build, so that copy is provably what compiles. ⚠️ **Not sufficient alone** — the bridge resistor has to move to the **TX side** (`A1 → 1 kΩ → node`, with `A0` and `PDN_UART` directly on the node), or the push-pull TX shorts out the driver's reply.

### 🔑 Your hand test is the decisive one, and it points at `VM`

> *pulling the plunger manually, it moves freely when plugged in and on*

No holding torque ⇒ no coil current. And from the 6121 schematic: **the VREF pot is fed from the chip's own `5VOUT`, which is generated from `VM` alone** — `VCCIO` doesn't power the analogue side. So a missing `VM` gives zero VREF, zero coil current, no UART reply, and every `STEP`/`DIR` still accepted and acked. One cause, every symptom, including `comm = 0`.

**Measure 12 V at the driver's `VM` screw terminal, not at the brick** — and check the screws are clamping wire rather than insulation. Two related notes from the same schematic: `EN` has a 20 kΩ pull-down, so the driver is enabled even with the `EN` wire absent; and `MS1`/`MS2` pull down internally to **1/8 microstepping and UART address 0**, so addressing was never the problem — but a commanded millimetre will travel two if the microstep write doesn't land. **Check the first real move against a ruler.**

---

### ✅ Gates — all green, against the installed tree

| gate | result |
|---|---|
| `pytest packages/core/tests` | **2544 passed, 17 skipped, 0 failed** |
| `validate_setup` | **PASS** |
| `run_protocol --mock` | **12/12 steps** |
| `passive_shadow` | **0 interferences** |
| `passive_shadow --tip-stuck` | **0 interferences** |

Firmware builds clean (17 382 bytes, 53.9% flash). Both patches verified with `git apply --check` against fresh clones — `PANDA_Arduino` @ `228615b` and pristine TMC2209 10.1.1 — and the fresh clone builds. I also found that the patch previously documented as "four files" was missing a `platformio.ini` change; regenerated, it's five files, +161/−12.

### ✅ Machine state — untouched

| | |
|---|---|
| Gantry motion | **none** — `/dev/ttyUSB0` opened read-only for `?` and `$$` |
| GRBL | `<Alarm\|WPos:409,309,124\|Pn:X>` · `$130/$131/$132` = 409.000 / 309.000 / 124.000 · `$20=1` |
| Plunger | **not actuated** — no travel accumulated this session |
| Electromagnet | not energized; no capper command reached the board |
| Arduino flash | **unchanged** |
| Ports | both free |

On the homing fix — thanks, and `Alarm` with `Pn:X` is the *expected* resting state rather than a leftover fault: `$22=1` boots GRBL into Alarm until homed, and `Pn:X` is just the carriage parked on X's max switch with `$23=0`. Step 0 unlocks and homes, so we'll find out whether Y is clear on the next run.

### Committed — [`2fdea46`](https://github.com/vertical-cloud-lab/byu-vcl/commit/2fdea46) · [`b7e0130`](https://github.com/vertical-cloud-lab/byu-vcl/commit/b7e0130)

- [`cubos/patches/p20-gen2-plunger-constants.patch`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/patches/p20-gen2-plunger-constants.patch) — replaces `p20-mm-to-ul-passthrough.patch`, keeping its `mm_to_ul = 1.0`
- [`cubos/patches/tmc2209-softwareserial-read.patch`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/patches/tmc2209-softwareserial-read.patch) — the read-path fix
- [`cubos/firmware/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/b7e0130/cubos/firmware) — regenerated [patch](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/firmware/panda-arduino-p20-and-driver-status.patch), the built-but-unflashed [`panda_vcl_p20gen2_20260917.hex`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/firmware/panda_vcl_p20gen2_20260917.hex), and a [README](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/firmware/README.md) with the full constants table
- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/docs/opentrons-pipette-wiring.md) — new **§10**: both retractions, the Opentrons table, and what's now closed
- [`cubos/results/pipette_p20gen2_20260917/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/b7e0130/cubos/results/pipette_p20gen2_20260917) — the [write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/results/pipette_p20gen2_20260917/README.md), [`serial_link_diagnostics.txt`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/results/pipette_p20gen2_20260917/serial_link_diagnostics.txt), and all five gate logs
- [`cubos/patches/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/patches/README.md) and [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b7e0130/cubos/README.md)

The committed tree was pulled back onto the Pi, the applied `models.py` delta verified **byte-identical** to the committed patch, and all four gates re-run from it — PASS, 12/12, 0 interferences both ways. What's on the branch is what's on the machine.

### Not done

**The trio, and the reflash** — both blocked on the serial link. Replug the Arduino and confirm one `STATUS` parses, and I'll flash the P20 GEN2 image and run it in one pass.

I didn't touch any wiring, and the three bench items are still yours: `VM` at the screw terminal, the bridge resistor moved to the TX side, and the limit-switch loop (pin 6 → GND, pin 7 → D9, normally closed) — that last one is independent, and until D9 reads LOW the plunger can't retract whatever the motor does.

⚠️ One P20 GEN2 number I deliberately **didn't** propagate: Opentrons implies a **22.9 mm** tip extension (`tipLength 31.15` − `tipOverlap 8.25`) against the **35.0 mm** you measured on 2026-08-06. Every piece of validated tipped Z geometry on this branch depends on the 35 — the hover clamp's 89/124 planes, the `height: -35.0` insert, `travel_z: 87`. A caliper check is worth doing, but if it comes out 22.9 that's a re-derivation, not a one-line edit.

Alex also asked for PRs so our three CubOS branches don't drift, and nothing is upstreamed yet — the hover clamp and `_best_effort_retract_to_safe_z` to Ursa, the `mixInPlace` compile error to BU-KABlab, the SoftwareSerial guard to janelia. Say the word and I'll write them up.

`CLAUDE.md` shows as modified in the working tree only because the action synced `main`'s copy in; it's byte-identical to `origin/main`, so I left it uncommitted.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-17 22:43:53 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722205565)

@claude the driver current pot is turned completely clockwise to allow 2A. Should I change that? What is the best way to measure 12V at the screw terminal? While you were running the last command, the F light on the Driver board was blinking between bright green and less-bright green.

---

## @claude[bot] — 2026-09-17 22:44:25 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722210120)

**Claude finished @benwhitney5463's task in 8m 7s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35283486794)

---
### `F` is *Forward*, not *Fault* — and your two facts together make `VM` the answer

- [x] Look up what the `F` LED on the Adafruit 6121 actually is — **it's a direction indicator**
- [x] Answer the pot question — **leave it alone, and here's why that matters**
- [x] Write the 12 V measurement procedure
- [x] Check read-only whether the Arduino link recovered — **it did, 8/8 clean**
- [x] Record it all in the wiring doc ([`8670faf`](https://github.com/vertical-cloud-lab/byu-vcl/commit/8670faf))

**No motion was commanded** — you asked questions, so this was the Adafruit documentation plus a read-only probe. The only hardware actuated was an explicit `CMD_EMAG_OFF` at the end.

---

### 3️⃣ The `F` light — good news and bad news

**It's not a fault light.** Adafruit's guide lists exactly three LEDs on the 6121, and all three sit on logic pins *the Arduino drives*:

| silk | colour | tied to | lit when |
|---|---|---|---|
| **`F`** | green | **`DIR`** | *"the motor is being driven counterclockwise when the DIR pin is low"* |
| **`B`** | red | **`DIR`** | *"the motor is being driven clockwise when the DIR pin is high"* |
| **`S`** | yellow | **`STEP`** | *"the motor driver is being moved"* |

`F` = Forward, `B` = Backward. **`DIAG`** — the pin that *would* report a short, an open load or a thermal shutdown — is on header pin 7 with **no LED and no wire**. So this board can't show you a driver fault at all; the only route to one is still the UART readback, which needs the library patch **and** the resistor moved to the TX side.

#### Why it was blinking bright/dim — almost certainly me

Green `F` lights by the Arduino **sinking** the `DIR` net, so its brightness tracks pin `A3`:

| `A3` | green `F` |
|---|---|
| driven LOW by the running sketch | **bright** |
| high-impedance — during reset, and while the bootloader runs | **dim** (leakage only) |
| driven HIGH | off, red `B` lit instead |

You saw it during the session that spent several minutes running `avrdude` at four baud rates. **Every `avrdude` attempt toggles DTR, which resets the ATmega328P**, and the bootloader doesn't touch `A3` — so the pin floats (dim) until `setupPipette()` runs `pinMode(DIR_PIN, OUTPUT)` and drives it LOW (bright). One reset = one dim/bright transition. No plunger motion was commanded in that session at all, so nothing else could have moved `DIR`.

Benign. The one alternative worth ruling out is a `VDD` rail sagging under load and modulating the LED, and the test is free: **watch `F` while nothing is being sent to the board.** Steady = rail is fine.

#### 🔑 The useful part: the LEDs are a free direction readout

The firmware sets `DIR` once per move and holds it, so:

| firmware action | `DIR` | LED |
|---|---|---|
| `HOME` seek (upward) | LOW | **green `F`** |
| `HOME` back-off (796 steps) | HIGH | red `B` |
| `MOVE_TO` / `ASPIRATE` descending | HIGH | red `B` |
| `MOVE_TO` retracting | LOW | **green `F`** |

That answers a question that's been open since 2026-09-01 — *does `HOME` seek toward the limit switch or away from it?* — **by eye, no meter.** Run a `HOME`: it runs for 26 s, green `F` should be lit the whole time, and you can watch which way the shaft is being urged. And `S` flickering is a second confirmation that `STEP` pulses arrive, alongside the raw-step probe.

---

### 1️⃣ The pot at full clockwise — **don't change it yet**, and it's not what's wrong

Adafruit: *"when all the way to the right we can get to up to 2A max."* So yes, full CW is the maximum, and yes, that's roughly **2× the P20 GEN2's `plungerCurrent: 1.0 A`**.

But combined with your hand test, the two facts are far more informative than either alone — and they point away from the pot:

> `i_scale_analog` is still `1` (no UART write has ever been confirmed to land), so **the pot is the only thing setting coil current** — and it's at maximum. At maximum VREF this motor should have obvious holding torque. **It has none.** VREF is fed from the chip's own `5VOUT`, and `5VOUT` is generated from **`VM` alone**. So zero torque at maximum pot ⇒ VREF is zero ⇒ `5VOUT` is dead ⇒ **`VM` is missing** (or the chip is dead).

The pot is eliminated by being at the wrong end of its range to explain anything, and it's currently the setting *most* likely to reveal torque — turning it down can only muddy the measurement.

**Two caveats for once there is torque:**

- **In standalone mode, back it off before any sustained move.** Full scale on this board's real **0.05 Ω** sense resistors is ~3.3 A rms — past the breakout's own 2 A rating, never mind the motor's. Set it by measuring, not by counting turns: **VREF ≈ 0.55 V gives ~1.0 A peak** (`I_rms = (VREF / 2.5) × 3.283 A` → 0.72 A rms = 1.02 A peak, the same current `RUN_CURRENT_PERCENT 20` asks for). ⚠️ VREF isn't broken out on the 10-pin header, so that means probing the trimmer's wiper. **If full clockwise measures below 0.55 V, the pot can't over-current the motor and the question is moot.**
- **Once UART works the pot stops mattering entirely.** The first register write is `setOperationModeToSerial()`, which clears `i_scale_analog` and takes the pot out of circuit; `RUN_CURRENT_PERCENT` governs from then on.

⚠️ Fit the Adafruit 1515 heat sink before running at any of these currents — *"higher the currents will heat up both the motor driver and stepper so you may need to add heatsinking."*

---

### 2️⃣ How to measure the 12 V

Any multimeter on DC volts (`V⎓`), 20 V range or autoranging. Leave everything powered.

1. **Black probe on `−`, red probe on `+`** of the two-pin motor-supply screw block.
2. **Probe the screw heads, or the bare wire clamped under them** — not the insulation, not the barrel jack, and *not* the brick's own output. The whole point is finding out whether 12 V survives the journey.
3. Expect **11.4 – 12.6 V**.

| reading | meaning |
|---|---|
| **~12 V** | `VM` is present. Fault is downstream — VREF, or the coils. |
| **0 V** | nothing reaching the board: supply off, broken wire, or a screw clamped on insulation rather than copper |
| **~−12 V** | polarity reversed |
| **a few volts, or collapses when a move is commanded** | bad joint, or a supply that can't hold up under step load |

Four checks that cost nothing while the meter is out:

- **Tug each wire in the terminal block.** A screw tightened onto insulation is the single most common cause of a 0 V reading, and it looks perfectly installed.
- **Continuity** (Ω or the beeper) from the supply's output conductor to the matching screw terminal — under ~1 Ω.
- **Measure again while a bounded move is commanded**, to catch a rail that reads 12 V idle and collapses under load.
- **Same tug test on the four coil terminals** (`1A/1B/2A/2B`). If `VM` is good and there's still no torque, an insulation-clamped coil screw does exactly that — then the coil check applies: blue–red and black–green a few to a few tens of ohms, blue–black open.

Safety: 12 V is no shock hazard, but don't let the probe tips bridge `+` to `−` or to an adjacent pad — that's a dead short through the supply. **No meter to hand?** Crude substitute: put a known 12 V load (a fan, an LED strip) on the same leads and see if it runs. Tests the supply and the wiring, but not the terminal block itself.

---

### ✅ Unasked-for but important: the serial link came back

Both ports re-enumerated at **16:45 lab-local**, and a read-only probe straight afterwards:

```
banner: b'OK:Ready\r\n'
  [0..7] OK  dt=0.01s  OK:{"homed":0,"pos":0.00,"max_vol":20.00}

STATUS round-trips: 8 clean / 8 attempted      (was 0 of 25 earlier today)
```

So the first of the four candidates — *replug the USB cable; a `USBDEVFS_RESET` from the Pi is not a power cycle* — was the fix. **The P20 GEN2 reflash and the trio are both unblocked.**

I didn't do either. The reflash moves the `prime`/`blowout`/`drop_tip` planes by 8–9 mm and those are sent as **absolute** targets, so it's a real motion change — and you'd said to hold off. **Say "flash and run" and I'll do both in one pass.**

`CMD 29` still reads `comm = 0`, exactly as expected and still uninformative: the running image (`max_vol: 20.00` = the 09-15 build) predates the SoftwareSerial read fix, so that read can't succeed whatever the wiring does.

### ✅ Machine state — untouched

| | |
|---|---|
| Motion | **none commanded** — no homing, no G-code, no plunger command |
| GRBL | `<Alarm\|WPos:409,309,124\|Pn:X>` — the expected resting state (`$22=1` boots into Alarm until homed; `Pn:X` is the carriage parked on X's max switch with `$23=0`) |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Electromagnet | off — `CMD_EMAG_OFF` confirmed |
| Plunger | `homed: 0`, `pos: 0.00` — no travel accumulated this session |
| Ports | both free before and after |
| Firmware | the 2026-09-15 p20 image — **unchanged** |

### Order I'd go in

1. **Measure `VM` at the screw terminals.** One measurement, and it's the prime suspect for all of it.
2. **`VM` good but no torque** → tug the coil terminals, then the coil resistance check.
3. **`VM` good and coils good** → it's the UART path: move the bridge resistor to the **TX side** (`A1 → 1 kΩ → node`, `A0` and `PDN_UART` direct on the node), reflash, then `CMD 29` will tell you about the coils directly via `open_load_a/b`.
4. **Separately, the limit-switch loop** — pin 6 → GND, pin 7 → D9, normally closed. Independent fault; until D9 reads LOW the plunger can't retract whatever the motor does.
5. Then check the first real move **against a ruler** — `setMicrostepsPerStep(16)` never landing means MS1/MS2 decide, and their default is 1/8, so a commanded millimetre may travel two.

### Committed — [`8670faf`](https://github.com/vertical-cloud-lab/byu-vcl/commit/8670faf)

- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/8670faf/cubos/docs/opentrons-pipette-wiring.md) — new **§11**: the LED table, the reset explanation, the pot analysis with the VREF target, the `VM` procedure, and the link recovery. §10.5's status table updated.
- [`cubos/results/pipette_p20gen2_20260917/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/8670faf/cubos/results/pipette_p20gen2_20260917/README.md) + [`serial_link_recovered.log`](https://github.com/vertical-cloud-lab/byu-vcl/blob/8670faf/cubos/results/pipette_p20gen2_20260917/serial_link_recovered.log) — the addendum and the raw probe
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/8670faf/cubos/README.md) — status section

### Not done

No hardware run, no reflash, no wiring touched, no config file changed. I can't measure `VM`, VREF or coil resistance remotely — those three need the meter and your hands, and they're the whole critical path now.

Nothing is upstreamed yet: the `mixInPlace` compile error to BU-KABlab, the hover clamp and the `_best_effort_retract_to_safe_z` bug to Ursa, the Cubware pin-diagram shift, the SoftwareSerial guard to janelia, and Alex's ask for PRs so the CubOS branches don't drift. Say the word on any and I'll write them up.

Sources: [Adafruit 6121 product page](https://www.adafruit.com/product/6121) · [Adafruit TMC2209 breakout — Pinouts](https://learn.adafruit.com/adafruit-tmc2209-stepper-motor-driver-breakout-board/pinouts)
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-17 23:06:07 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722394735)

@claude try running the trio again

---

## @claude[bot] — 2026-09-17 23:06:32 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722398630)

**Claude finished @benwhitney5463's task in 16m 43s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35285264009)

---
### It didn't run — `home` (step 0) failed, **0 steps executed**. The cause is `ALARM:9` on **Z**, and there's a second, separate fault on **X**

- [x] Reach the Pi — Arduino link **healthy again**, 20/20 clean round-trips
- [x] Offline gates: `validate_setup` PASS · `--mock` 12/12 · `passive_shadow` **0 nominal, 0 tip-stuck**
- [x] Hardware run → **failed at step 0**, no deck motion, no vial approached
- [x] Capture the raw alarm code, then isolate the axis
- [x] Test Z's motion and both limit switches directly
- [x] Leave the machine safe; commit logs, frames, campaign CSVs ([`46e1419`](https://github.com/vertical-cloud-lab/byu-vcl/commit/46e1419))

```
ERROR during execution: Homing timed out after 90 seconds
Protocol did not complete — 0 steps executed before exit.
```

Campaign 46, `23:10:46 → 23:13:40` UTC, status `failed`. Nothing was commanded to the deck — no capper motion, no pipette motion, no vial approached. The gates were all green first, so the configs are not at fault.

---

### 🔴 `ALARM:9` on Z — and two numbers identify the axis

The driver's retry loop hid the real error, so I sent one instrumented `$H` and captured the raw serial stream:

```
before $H: <Idle|WPos:409.000,309.000,124.000|FS:0,0|Pn:X|...>
  t+11.46s  ALARM:9
  t+12.46s  <Alarm|WPos:409.000,309.000,310.000|...>
```

`ALARM:9` is *"could not find limit switch within search distance."* Which axis:

- **The Z counter ran 124 → 310 — exactly +186 mm, which is `1.5 × $132`**, GRBL's Z search distance.
- **It failed at t+11.46 s.** 186 mm at `$25 = 1000` mm/min is 11.2 s.

GRBL homes Z first, so the cycle never reached X or Y. **This is not campaign 36's failure** — that was Y, on the *closing* home, with 41.8 s attempts. This is Z, on the opening home, failing fast and identically every time (8 attempts, ~11.3 s / ~12.1 s alternating).

### Z moves perfectly. Its switch never asserts

Jogged Z ±25 mm, polling the pin state throughout:

```
jog Z-25 ->  124.000 -> 99.000    smooth, at commanded feed    Pn:X
jog Z+25 ->   99.000 -> 124.000   smooth                       Pn:X
jog Z+10 ->  error:15             soft limit at GRBL's Z ceiling
```

**`Pn:Z` never appeared** — not at Z 124, not anywhere, and not immediately after homing had driven Z 186 mm upward into its physical top. The axis is mechanically fine. `$5 = 0`, so a limit pin reads *not triggered* when its circuit is **open**.

Visible in the frames — the head between the two jog positions:

| Z at 99 | Z back at 124 |
|---|---|
| ![](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/results/pipette_test_20260917/frames/02_z_down__cam1.jpg?raw=true) | ![](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/results/pipette_test_20260917/frames/03_z_up__cam1.jpg?raw=true) |

### 🔴 And X's switch is stuck asserted — this is a *second* fault

```
at rest (carriage parked at X max):   Pn:X
$J=G91 X-10  ->  WPos X 409 -> 399    Pn:X
$J=G91 X-10  ->  WPos X 399 -> 389    Pn:X
```

The carriage moved **20 mm away from its switch and `Pn:X` never cleared.** That's a stuck-closed switch or a signal line shorted to ground — not a carriage parked on a switch, which is how I read it last session.

**This changes the fix.** It blocks nothing today (`$21 = 0`, hard limits off — which is why campaign 36's 11 steps ran fine), but homing *does* read the limit pins. Once Z is repaired, X will pull off `$27 = 3` mm, find its switch still triggered, and raise **`ALARM:8`**. So **both have to be fixed before homing can succeed** — repairing Z alone just changes the alarm code.

### Both broke during campaign 36

| when | Z switch | X switch |
|---|---|---|
| 2026-09-16 16:21:51 — campaign 36 step 0 | ✅ homing completed | no `Pn:` field at all |
| 2026-09-16 16:24:13 — campaign 36 step 11 | ❌ homing failed | — |
| since | ❌ | `Pn:X` asserted continuously |
| 2026-09-17 23:11 — this run | ❌ `ALARM:9` | `Pn:X`, stuck 20 mm off |

Two-and-a-half minutes between a successful home and a failed one, with both switches changing state in that window. A single disturbance to the limit-switch harness would account for both, and **the drag chain is the obvious common path** — it's the only thing that was moving.

---

### ✅ Genuinely good news: the *pipette* limit switch flipped back to CLEAR

Three plunger commands reached the Arduino before the gantry failed:

| command | dt | reply |
|---|---|---|
| `STATUS` | 0.008 s | `homed:0, pos:0.00, max_vol:20.00` |
| `HOME` | **26.345 s** | `ERR:{"error":"Failed to home pipette"}` |
| `HOME` retry | **26.345 s** | `ERR:{"error":"Failed to home pipette"}` |

Every session since 2026-09-01 saw `HOME` return in **0.520 s** with a fake success — the D9-HIGH signature (loop open, reads "asserted"). **26.345 s is the firmware running its full 50 000-step budget, which is the D9-LOW signature.** So the pipette's switch loop now reads clear, which un-gates the upward direction in `stepMotor()`: `blowout` and both `drop_tip` legs would execute for the first time, as far as the firmware is concerned.

Whether the *motor* turns is still separate — `CMD 29` reads `comm = 0`, expected since the running image predates the SoftwareSerial read fix. **`VM` at the driver's screw terminals is still the measurement to take.**

`prime()` never ran (the connect patch raises before it), so **no plunger travel was commanded this session** — the first time that's been true in a while.

### ✅ The serial link stayed healthy

The corruption that blocked 09-17's session is gone: **20/20 clean `STATUS` round-trips** across two probes, cap sensor and electromagnet both answering. The USB replug was the fix.

---

### ✅ Machine state

| | |
|---|---|
| Protocol | failed at step 0 — **0 steps, no deck motion** |
| GRBL | `<Alarm\|WPos:409.000,309.000,124.000\|FS:0,0\|Pn:X>` — Alarm refuses motion |
| Position | X ~20 mm off its max switch (from the jog test); Y unmoved; Z at/near its top |
| `$5`/`$20`/`$21`/`$22`/`$23`/`$27` | 0 / 1 / 0 / 1 / 0 / 3.000 |
| `$130`/`$131`/`$132` | 409.000 / 309.000 / 124.000 — matches the gantry file |
| Electromagnet | off — `CMD_EMAG_OFF` → `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Plunger | `homed:0, pos:0.00, max_vol:20.00`; **no travel commanded** |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |

⚠️ **Z was driven upward against its top for ~11 s per homing attempt** — 8 from the protocol, plus 1 diagnostic, on top of campaign 36's 4. A stepper against a hard stop skips steps rather than breaking, but the Z coupling and belt are worth an eyeball. I stopped after one diagnostic attempt rather than retrying.

### What to check

1. **The Z limit switch and its wiring** — continuity across the switch with Z at its top, and back to the controller's Z limit pin. With `$5 = 0`, an open circuit reads *not triggered*, which is exactly what GRBL sees.
2. **The X limit switch and its wiring** — it reads triggered with the carriage 20 mm away, so look for a shorted or pinched signal line.
3. **The drag chain**, as the path both run through and the only thing moving when they changed state.
4. Free confirmation once you're at the machine: **press each switch by hand and watch GRBL's `Pn:` field**, which names every asserted limit pin:

```bash
cd ~/CubOS && .venv/bin/python -c "
from cubos.gantry.gantry_driver.driver import Mill
import time
m = Mill('/dev/ttyUSB0'); m.connect()
for _ in range(40): print(m.query_raw_status()); time.sleep(1)
m.disconnect()"
```

One thing from the deck frame worth your eyes: the vial column looks like it holds **two capped glass vials plus a row of loose caps**, rather than six capped vials. The protocol targets `vial_1` and `vial_2`, so it may be fine — but it never got there, so I couldn't check it with the capper's own sensor.

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/results/pipette_test_20260917/frames/01_before__cam1.jpg?raw=true)

### Committed — [`46e1419`](https://github.com/vertical-cloud-lab/byu-vcl/commit/46e1419)

- [`cubos/results/pipette_test_20260917/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/46e1419/cubos/results/pipette_test_20260917) — the [write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/results/pipette_test_20260917/README.md), the [hardware log](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/results/pipette_test_20260917/run_hardware.log), the [GRBL exchange with timestamps](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/results/pipette_test_20260917/mill_control_thisrun.log), the [plunger trace](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/results/pipette_test_20260917/plunger_trace.json), the [end-of-session state](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/results/pipette_test_20260917/final_state.json), all four gate logs and the [8 frames](https://github.com/vertical-cloud-lab/byu-vcl/tree/46e1419/cubos/results/pipette_test_20260917/frames); campaign CSVs in [`campaign_46_20260917_231046/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/46e1419/cubos/results/pipette_test_20260917/campaign_46_20260917_231046)
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/README.md) — status section

**Your three config files needed no edit at all.** The `cam1` frames are committed cropped to the deck strip — that camera looks across the bench into the room and a lab member is in frame; uncropped originals are on the Pi in `/tmp/zdiag`.

### Not done

**The trio itself** — it's blocked on the two limit switches, and that needs hands on the machine. I didn't retry homing beyond the one diagnostic attempt, and I didn't jog Z away from its top (the top is the safest place for it).

I also didn't flash the P20 GEN2 firmware image: you asked for a run, not a flash, and it moves the `prime`/`blowout`/`drop_tip` planes by 8–9 mm as absolute targets. It's built and waiting at [`cubos/firmware/panda_vcl_p20gen2_20260917.hex`](https://github.com/vertical-cloud-lab/byu-vcl/blob/46e1419/cubos/firmware/panda_vcl_p20gen2_20260917.hex) — say "flash and run" once the switches are fixed and I'll do both in one pass.

Still open and untouched: `VM` at the driver screw terminals (the one measurement that would explain the silent plunger), the bridge resistor moved to the TX side, `drop_tip` ejecting 35 mm above the slot pending a `tip_disposal` deck entry, and nothing upstreamed — the `mixInPlace` compile error to BU-KABlab, the hover clamp and `_best_effort_retract_to_safe_z` to Ursa, the Cubware pin-diagram shift, and the SoftwareSerial guard to janelia.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-17 23:28:17 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722607151)

@claude, the gantry wasn't on... that is my bad. It is on now. Try the trio again.

---

## @claude[bot] — 2026-09-17 23:28:37 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722611202)

**Claude finished @benwhitney5463's task in 28m 50s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35286987416)

---
### Ran it — **the gantry homed on the first attempt, 18.1 s.** Then `decap vial_1` didn't confirm, and the interlock stopped it at step 2. Separately: I owe you a retraction — there was never a limit-switch fault

- [x] Reach the tailnet (joined automatically) and the Pi — it had **rebooted**, back at 23:40:03 UTC
- [x] Read GRBL live — **`Pn:X` is gone**
- [x] Offline gates: `validate_setup` PASS (12 steps) · `--mock` 12/12 · `passive_shadow` **0** · `--tip-stuck` **0**
- [x] Arduino link — **10/10 clean**, `max_vol: 20.00` (p20 image live)
- [x] **Hardware run — homed, moved to vial_1, attempted a real decap**
- [x] Prove the failure isn't geometry — compared the G-code against a run that worked
- [x] Leave the machine safe, commit logs + deck frame + campaign CSVs ([`0c02c84`](https://github.com/vertical-cloud-lab/byu-vcl/commit/0c02c84))
- [ ] **The remaining 11 steps — blocked on why the cap didn't lift**

```
2026-09-17 17:43:32,729  Command sent: $H
2026-09-17 17:43:50,808  Homing completed          <- first try, 18.1 s
```

Campaign 50, `23:42:24 → 23:44:35` UTC. Four hours earlier the same command failed five times and timed out. Your one sentence was the whole fix.

---

### 🔴 The retraction: I diagnosed two limit-switch faults that don't exist

`WPos` is GRBL's **internal step counter, not a measurement.** With the stepper supply off, the controller accepts every `G01`, emits the steps, and reports a perfectly plausible position while the machine stands still. Everything I built on top of that was wrong:

| what I told you | what it actually was |
|---|---|
| *"Z moves perfectly. Its switch never asserts"* | I saw the **counter** run 124 → 99 → 124. That was 50 mm of counter and 0 mm of carriage — so `ALARM:9` after a 186 mm search was correct and honest |
| *"X's switch is stuck asserted — a **second** fault"* | the carriage never left the switch, so `Pn:X` was truthful. It is **absent from every status read** now that the supply is on |
| *"a single disturbance to the limit-switch harness; the drag chain is the common path"* | nothing is wrong with the harness |

Six consecutive reads today, before any motion — no `Pn:` field at all:

```
<Alarm|WPos:409.000,309.000,124.000|FS:0,0|WCO:-409.000,-309.000,-124.000>
<Alarm|WPos:409.000,309.000,124.000|FS:0,0|Ov:100,100,100>
<Alarm|WPos:409.000,309.000,124.000|FS:0,0>          x4
```

It also re-explains **campaign 36**, which I'd filed as a separate Y fault: steps 0–10 ran with the capper's line-break sensor confirming a real cap capture — only possible if the head was physically moving — and then the closing `home` failed 2½ minutes later. That's the supply dropping out around 2026-09-16 22:24 UTC, not a Y switch.

**`?` reports the counter; only a limit pin or an instrument sensor reports reality.** `Pn:` is driven by the switches rather than the step generator, so it was a free power-independent check available the whole time, and I read it as the fault instead of as the discriminator. That's written into [`SOP/raspberry-pi-cubos-setup.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0c02c84/SOP/raspberry-pi-cubos-setup.md) so it doesn't cost a third session.

---

### 🔴 Why it stopped: `decap vial_1`, three attempts, no cap

```
ERROR during execution: decap failed for 'vial_1':
  sensor did not confirm cap capture after 3 attempt(s)
  (last reading: cap_present=False, expected True)
```

The interlock did exactly what it's for — 3 tries, then abort with the tool retracted to `safe_z`, before any pipette motion. No vial was opened and nothing entered a capped vial.

### 🔑 And it is **not** geometry — the G-code is byte-identical to a run that worked

Real hardware window only (from `mill_control.log`, which the mock gantry doesn't write to):

```
campaign 36   2026-09-16, decap vial_1 SUCCEEDED first attempt
  $H  Z99.065  X206.0  Y25.0  Z124.0  Y27.0  Z99.065  Z54.065  Z99.065  Z124.0  X284.0 ...

campaign 50   2026-09-17, decap vial_1 FAILED 3x
  $H  Z99.065  X206.0  Y25.0  Z124.0  Y27.0  Z99.065  Z54.065  Z99.065  Z54.065  Z99.065  Z54.065  Z99.065
```

Same X 206, same Y 27, same engage plane gantry Z 54.065 (= deck Z 70 = rim 55 + `engage_depth_mm` 15). They diverge only in that campaign 36 confirmed and went on to the tip rack, while today it retried twice and gave up. **The head went to the right place.** Candidates, cheapest first:

1. **Is there a vial and a cap in slot 1?** I flagged from campaign 46's frames that the column looked like *two capped vials plus a row of loose caps*. Five seconds to check, and it's my leading guess.
2. **🔑 Does the electromagnet have coil power?** The Arduino acks `CMD_EMAG_ON` whether or not the coil is energised — it's just a pin. If the magnet's supply is on a *different* switch from the gantry's, the symptom is precisely this: descend, "energise", read `cap_present=False`, retry, abort. Given a supply was already found switched off, this one deserves an explicit look rather than an assumption.
3. **Cap too tight** — your own 2026-08-03 observation, that the one cap the capper couldn't lift was on a vial slightly wider than the rest.

I can't settle #1 from here: neither camera is aimed at the vial column. This is cam0 after the abort — the deck strip, the tip rack, the capper head at right, and no view of slot 1:

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/0c02c84/cubos/results/pipette_test_20260917b/frames/deck_after_decap_fail_cam0.jpg?raw=true)

---

### ✅ The pipette limit switch is still reading CLEAR

Three plunger commands got through before the gantry step failed:

| command | dt | reply |
|---|---|---|
| `STATUS` | 0.008 s | `homed:0, pos:0.00, max_vol:20.00` |
| `HOME` | **26.331 s** | `ERR:{"error":"Failed to home pipette"}` |
| `HOME` retry | **26.337 s** | `ERR:{"error":"Failed to home pipette"}` |

26.3 s is the firmware running its full 50 000-step seek — the **D9-LOW** signature, loop closed. (The 0.52 s fake success on 09-15/16 was D9 HIGH, loop open.) `prime()` never ran, because the connect patch raises before it, so **no plunger travel was commanded this session.**

`CMD 29` still reads `comm = 0`, and that remains uninformative — the running image is the 09-15 p20 build, which predates `tmc2209-softwareserial-read`, and that read cannot succeed on an AVR without it whatever the wiring does. **`VM` at the driver's screw terminals is still the measurement to take**, and it's still worth knowing whether the driver's 12 V is on the same switch you just flipped.

### ✅ Machine state

| | |
|---|---|
| Protocol | failed at step 2; tool retracted to `safe_z` by the capper's own retract |
| Electromagnet | off — `CMD_EMAG_OFF` → `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | none were moved — vial_1 is still capped |
| GRBL | `Alarm`, **no `Pn:` field**. Normal: the board resets when the port closes. Re-home before the next run |
| `$130/$131/$132` · `$20` | 409.000 / 309.000 / 124.000 · `1` — matches the gantry file |
| Plunger | `homed:0, pos:0.00, max_vol:20.00`; no travel commanded |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |

**Your three config files needed no edit at all** — the trio ran exactly as committed at `46e1419`.

### Two session notes

- **The Pi shares power with the gantry.** It rebooted at 23:35:23 UTC and was off the tailnet 23:23:47 → 23:40:03, which is why I couldn't reach it for the first ten minutes. Worth knowing: a power cycle mid-run would cut the run.
- `rpicam-still --camera 1` hung again and had to be killed; camera 0 captured in under a second. Same 1 GB-Pi contention as 09-15.

### Committed — [`0c02c84`](https://github.com/vertical-cloud-lab/byu-vcl/commit/0c02c84)

- [`cubos/results/pipette_test_20260917b/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/0c02c84/cubos/results/pipette_test_20260917b) — the [write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/0c02c84/cubos/results/pipette_test_20260917b/README.md), the [timestamped driver exchange](https://github.com/vertical-cloud-lab/byu-vcl/blob/0c02c84/cubos/results/pipette_test_20260917b/mill_control_thisrun.log), the [G-code](https://github.com/vertical-cloud-lab/byu-vcl/blob/0c02c84/cubos/results/pipette_test_20260917b/gantry_command_thisrun.log), the [plunger trace](https://github.com/vertical-cloud-lab/byu-vcl/blob/0c02c84/cubos/results/pipette_test_20260917b/plunger_trace.json), all four gate logs and the deck frame; campaign CSVs in [`campaign_50_20260917_234224/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/0c02c84/cubos/results/pipette_test_20260917b/campaign_50_20260917_234224)
- [`SOP/raspberry-pi-cubos-setup.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0c02c84/SOP/raspberry-pi-cubos-setup.md) — a new appendix on checking the stepper supply before diagnosing a motion fault, and the shared-power warning
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0c02c84/cubos/README.md) — the campaign 46 section marked **RETRACTED** in place, with the corrected section after it

### Not done

**Steps 2–11 never ran** — no tip pickup, no aspirate, no blowout, no tip drop. Check slot 1 and the magnet's power and I'll re-run immediately; if you'd rather I probe it, say so and I can energise the magnet on command while you hold a cap to the head, which separates "no vial" from "no field" without any gantry motion.

I didn't touch wiring, flash firmware, or change any config file. Still open: `VM` at the driver's screw terminals, the bridge resistor moved to the TX side, the P20 GEN2 image built but unflashed at [`panda_vcl_p20gen2_20260917.hex`](https://github.com/vertical-cloud-lab/byu-vcl/blob/0c02c84/cubos/firmware/panda_vcl_p20gen2_20260917.hex), `drop_tip` ejecting 35 mm above the slot, and neither camera aimed at the vial column. Nothing is upstreamed — the `mixInPlace` compile error to BU-KABlab, the hover clamp and `_best_effort_retract_to_safe_z` to Ursa, the Cubware pin-diagram shift, and the SoftwareSerial guard to janelia.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-18 00:00:33 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722877699)

@claude run the trio again. That time, the capper/decapper never actually went down in the z-direction. Any ideas why?

---

## @claude[bot] — 2026-09-18 00:00:54 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722881065)

### Running the trio, and instrumenting Z specifically

- [x] Reach the Pi, read GRBL state and settings
- [ ] Offline gates
- [ ] **Prove whether Z physically moves** — `Pn:Z` assert/clear + a feed-rate sweep + camera A/B
- [ ] Hardware run
- [ ] Report + commit

<img src="https://github.com/user-attachments/assets/5ac382c7-e004-429b-8e35-7feb3e8f9c6f" width="14px" height="14px" style="vertical-align: middle; margin-left: 4px;" /> Campaign 50's homing cycle finished in **7.0 s for all three axes** — too fast to have travelled far, so it proves much less about Z than it looks. Testing Z directly against its own limit switch now.

[View job run](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35289317552) · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-18 00:10:39 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722983477)

@claude I measured the voltage on the screw heads of the Stepper motor driver, and it read at 13V. I stopped the run because you tried to push past the y-limit. I am manually resetting the machine.

---

## @claude[bot] — 2026-09-18 00:11:03 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722987717)

**Claude finished @benwhitney5463's task in 8m 45s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35290073753)

---
### The Y overrun was mine — a relative jog computed against a counter that was 282 mm wrong. And 13 V at `VM` retires the hypothesis I'd put at the top of the list

- [x] Stop — no motion commanded this session, nothing sent to the gantry
- [x] Find what drove Y past its limit — read-only forensics on the Pi
- [x] Work out what 13 V at `VM` rules in and rules out
- [x] Write the rule down so it can't recur, and commit ([`d96e5e5`](https://github.com/vertical-cloud-lab/byu-vcl/commit/d96e5e5))

Thank you for stopping it. **No machine fault is involved** — not a limit switch, not the drag chain. It was a diagnostic script I wrote and ran, and the arithmetic is unambiguous.

---

### 🔴 What happened

GRBL's board resets whenever the serial port opens or closes, and the counter re-initialises to the **homed corner** regardless of where the carriage actually is. Campaign 50 left the head at (206, 27, 99.065) and then closed the port:

| moment | counter says | carriage actually at |
|---|---|---|
| 17:44:33, campaign 50's last move | (206, 27, 99.065) | (206, 27, 99.065) — agreeing |
| 17:44:35, port closed → board reset | **(409, 309, 124)** | (206, 27, 99.065) |
| 18:05, `$H` → `ALARM:9` on Z | (409, 309, 310) | (206, 27, ~124) — X/Y never homed |
| 18:08, soft reset | **(409, 309, 124)** | (206, 27, ~124) |

So the counter was **203 mm high on X and 282 mm high on Y**. Then my script did this:

```python
raw("$X")                 # unlock — clears Alarm, permits motion on an UNHOMED machine
raw("G91")                # RELATIVE mode
raw("G01 X-60 F1000")     # counter 409 -> 349 ; carriage 206 -> 146   safe, by luck
raw("G01 X60  F1000")     # counter 349 -> 409 ; carriage 146 -> 206
raw("G01 Y-60 F1000")     # counter 309 -> 249 ; carriage  27 -> -33   <-- 33 mm PAST Y MIN
```

`WCO` on Y is −309, so work-frame Y runs [0, 309] and **Y 0 is the physical minimum**. The target was −33.

**Both frames confirm the motion was real** — the deck plate is visibly displaced between the start of the test and the end of the Y move:

| before the test | after `G01 Y-60` |
|---|---|
| ![](https://github.com/vertical-cloud-lab/byu-vcl/blob/d96e5e5/cubos/results/y_overrun_20260918/frame_A_before_cam0.jpg?raw=true) | ![](https://github.com/vertical-cloud-lab/byu-vcl/blob/d96e5e5/cubos/results/y_overrun_20260918/frame_D_after_y_minus60_cam0.jpg?raw=true) |

### Why nothing caught it

- **`$20=1` validated the wrong number.** GRBL checks the target against its own machine position: −309 + 249 = −60, inside [−309, 0], accepted. Soft limits only mean something *after a successful `$H`* — on an unhomed machine they check a fiction.
- **`$X` is not a substitute for `$H`.** Unlock clears `Alarm` and lets motion through while leaving the position reference wrong. It's for recovering a machine you're about to home, not for jogging.
- **`$21=0`** — hard limits off, so the physical Y switch in the path couldn't stop it either.
- **X survived by coincidence.** 206 − 60 = 146 happens to be in bounds. Parked below X 60, the same script would have crashed X instead.

### The rule, now written into the SOP

> **After a failed `$H`, the machine's position is unknown. Recover by hand — never `$X` and jog.** If a diagnostic genuinely needs motion on an unhomed machine, jog only *toward* the homed corner: that's the one direction guaranteed to have travel available however wrong the counter is.

This is the second half of the lesson from 09-16/17. That one was about **reading** `WPos` as a position; this is about **commanding against** it, and I didn't draw it at the time — I wrote the retraction and then made the same mistake from the other side a day later. It's in [`SOP/raspberry-pi-cubos-setup.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/d96e5e5/SOP/raspberry-pi-cubos-setup.md) now, not just in a comment.

**Worth your call separately:** `$21=1` would add a real backstop — GRBL halts on a limit switch regardless of what the counter believes. The cost is that it also alarms on electrical noise. A genuine trade-off, and yours; I haven't changed it.

---

### ✅ The 13 V answer: that's the end of my leading hypothesis

The TMC2209 makes its own internal logic and reference supplies from `VM` through an on-chip regulator — `VCC_IO` (the Arduino's 5 V) powers only the pin drivers. On the Adafruit 6121 the VREF trimmer is fed from that internal `5VOUT`, so **everything analogue on the chip hangs off `VM`**. Missing `VM` was the one fault that explained silence, no holding torque and `comm = 0` all at once. 13 V ends it.

Which sharpens the problem, because three things should now all be true: `5VOUT` up, VREF live and near maximum with your pot fully clockwise, and — since `i_scale_analog` is still at its power-on default — VREF *is* what sets coil current. A healthy TMC2209 in that state also carries a default hold current (`IHOLD 16`, `IRUN 31`, `toff 3` = output stage enabled). **It should hold the plunger firmly, and it doesn't.**

⚠️ Two caveats on the reading: confirm it was the **2-pin motor supply block** and not a coil pair; and 13 V with no current flowing confirms the supply is *present*, not that it can *hold up* — but that can't be tested until current flows, so it isn't worth chasing now.

### What's left — three candidates, all multimeter-settleable

**A — the coil path is open.** *Power off*, probe the driver's **own** coil terminals so the measurement covers driver → ribbon → motor:

```
1A – 1B     a few to a few tens of ohms     coil A
2A – 2B     a few to a few tens of ohms     coil B
1A – 2A     open                            the coils are isolated
```

Both pairs open ⇒ the connector or the crimps, not the pinout. Tug each wire in the terminal block while you're there — a screw tightened onto insulation looks perfectly installed. This is the candidate with the most independent support: silence with **no buzzing** is open coils, whereas mis-*paired* coils buzz and vibrate.

**B — `EN` is held high.** *Power on, sketch running*, measure `EN` **at the driver pin**, not the Arduino header — must be ≈ 0 V. And confirm the wire lands on **A4**. Cubware's diagram puts `EN` on A3, which is the `DIR` pin: wired that way the driver is energised for one direction and dead for the other. The board's 20 kΩ pull-down makes an *absent* `EN` wire harmless; a *wrong* one is not.

**C — the driver chip is dead.** *Power on*, measure **VREF at the trimmer wiper**. With `VM` = 13 V and the pot fully clockwise it should be well above zero. **VREF ≈ 0 V means the internal `5VOUT` isn't being generated and the chip should be replaced.** Weak corroboration: a TMC2209 with `VM` applied draws a little even idle, so a chip that's stone cold after minutes powered fits a dead regulator.

**Order: A, then B, then C.** A is power-off and needs no live probing.

### And the software half is now worth doing on its own merits

Candidate A can be answered *by the chip*, no meter — `open_load_a`/`open_load_b` in the driver status register, which `CMD 29` already returns. It needs two things done **together**:

1. **Flash [`panda_vcl_p20gen2_20260917.hex`](https://github.com/vertical-cloud-lab/byu-vcl/blob/d96e5e5/cubos/firmware/panda_vcl_p20gen2_20260917.hex)** — it carries the SoftwareSerial read fix, without which a read on an AVR is structurally impossible. That's why `comm = 0` has been uninformative every single time I've reported it.
2. **Move the bridge resistor to the TX side** — `A1 → 1 kΩ → node`, with `A0` and `PDN_UART` directly on the node. On the RX side the Arduino's push-pull TX shorts out the driver's reply.

I can do #1 remotely whenever you want; #2 is yours.

---

### Machine state, as I found it read-only

| | |
|---|---|
| Motion commanded this session | **none** — the gantry port was never opened |
| GRBL controller (CH340) | **absent from the USB bus** — `/dev/ttyUSB0` doesn't exist. Consistent with your reset |
| Capper/pipette Arduino | present on `/dev/ttyACM0`, free; I didn't open it |
| CubOS logs | nothing written since 17:44:35 lab-local — no protocol ran |
| Pi | up since 17:35 lab-local (it shares power with the gantry) |

⚠️ **Z was driven against its upper stop for ~161 mm of steps during the 18:05 `ALARM:9` homing attempt** — the fifth such event across 09-16/17. A stepper against a hard stop skips rather than breaks, but the Z coupling and belt are worth an eyeball while you're in there.

### One thing I'm deliberately *not* claiming

Homing **succeeded** at 17:43:32 (campaign 50, `ok` in 7.0 s) and **failed** with `ALARM:9` at 18:05 from a similar starting position. I don't have enough to say why — and the 7.0 s figure is itself hard to square with an X axis that had 203 mm to cover at `$25 = 1000 mm/min` (12.2 s minimum). Both observations are in the write-up; neither is explained. Please don't treat either as a diagnosis, and if homing misbehaves again that's the open question.

### Committed — [`d96e5e5`](https://github.com/vertical-cloud-lab/byu-vcl/commit/d96e5e5)

- [`cubos/results/y_overrun_20260918/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/d96e5e5/cubos/results/y_overrun_20260918) — the [forensics](https://github.com/vertical-cloud-lab/byu-vcl/blob/d96e5e5/cubos/results/y_overrun_20260918/README.md), [`motiontest.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/d96e5e5/cubos/results/y_overrun_20260918/motiontest.py) exactly as executed, the two Z/axis diagnostic logs, and both frames
- [`SOP/raspberry-pi-cubos-setup.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/d96e5e5/SOP/raspberry-pi-cubos-setup.md) — the recovery rule, and why `$20`/`$21` don't cover it
- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/d96e5e5/cubos/docs/opentrons-pipette-wiring.md) — new §12 with the three candidates, expected readings, and a status table of what's measured vs. still open
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/d96e5e5/cubos/README.md) — status section

### Not done

Nothing was run on the CubXL and no wiring, firmware or config was touched. The three measurements above need your meter and your hands — I can't take any of them remotely. Once the machine is back and homing cleanly, say the word and I'll flash the P20 GEN2 image and re-run the trio in one pass.

Still open and untouched: `drop_tip` ejects 35 mm above the slot pending a `tip_disposal` deck entry; neither camera is aimed at the vial column, so whether slot 1 has a vial and cap in it — my leading candidate for campaign 50's decap failure — is still an eyeball question. And nothing is upstreamed: the `mixInPlace` compile error to BU-KABlab, the hover clamp and `_best_effort_retract_to_safe_z` to Ursa, the Cubware pin-diagram shift, and the SoftwareSerial guard to janelia.

`CLAUDE.md` shows as modified in the working tree only because the action synced `main`'s copy in; it's byte-identical to `origin/main`, so I left it uncommitted.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-18 00:34:00 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5723187035)

@claude try the trio again. The machine is homed right now.

---

## @claude[bot] — 2026-09-18 00:34:23 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5723190142)

**Claude finished @benwhitney5463's task in 19m 2s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35291734056)

---
### Ran it — **12/12 steps, campaign 54**. And for the first time the plunger **retracts**: every command emitted steps, in both directions

- [x] Reach the Pi — rebooted, both boards back, Arduino link **10/10 clean**
- [x] 🔴 Found **`$20=0`** on the controller — soft limits switched off. Restored and verified
- [x] Offline gates: `validate_setup` PASS · `--mock` 12/12 · `passive_shadow` **0 nominal, 0 tip-stuck**
- [x] **Hardware run — 12/12, `completed`**, every plunger command timed live
- [x] Work out what the timings do and don't prove
- [x] Fix a bug in the camera harness that was starving the second camera
- [x] Leave the machine safe, commit logs + frames + campaign CSVs ([`7975d5e`](https://github.com/vertical-cloud-lab/byu-vcl/commit/7975d5e))

```
Protocol complete — 12 steps executed.
```

Campaign 54, `00:38:28 → 00:44:49` UTC. Homed, parked, decapped vial_1, pressed onto A1, aspirated, parked, recapped vial_1, decapped vial_2, blew out, dropped the tip, capped vial_2, homed. **No capper retries, no alarms.** Both homing cycles succeeded on the first attempt — 18.1 s and 23.6 s.

Only the protocol was sent to the machine this time. No `$X`, no jogs, no ad-hoc motion script.

---

### 🔑 The plunger retracted — and three commands agree to 0.01 mm

Every command timed through a pass-through wrapper. Motion costs **0.663 s/mm** on this firmware, so a round trip that scales with the commanded distance means steps were emitted:

| step | command | dt | commanded distance | implied rate |
|---|---|---|---|---|
| `connect()` | `HOME` ×2 | 26.346 / 26.348 s | full 31.4 mm seek | switch never found |
| `pick_up_tip` | `MOVE_TO 0.0` | 0.006 s | 0 mm (already there) | correct no-op |
| `aspirate` | `ASPIRATE 20.0` | 13.131 s | down 36 + **up 36** | — |
| `blowout` | `MOVE_TO 32.5` | 21.546 s | **+32.5 mm** | 0.663 |
| `drop_tip` | `MOVE_TO 46.5` | 9.288 s | **+14.0 mm** | 0.663 |
| `drop_tip` | `MOVE_TO 28.0` | 12.267 s | **−18.5 mm** | 0.663 |

That last row is the one that has never happened. Since 2026-09-15, *every* retraction returned a flat ~0.107 s having emitted nothing at all.

`ASPIRATE` confirms it independently, without relying on the rate. `aspirate()` descends to `PRIME_POSITION` and then ascends by `volume × UL_TO_MM` — and the ascent is the gated leg. Campaigns 26 and 36 measured **5.962 s** (descent only). This run measured **13.131 s** — both legs. Which is also why `MOVE_TO 32.5` measured exactly 32.5 mm of travel: the aspirate landed back at 0.0, as the arithmetic says it should.

**What this proves and what it doesn't.** `stepMotor()` bit-bangs STEP and counts loop iterations — no encoder, no current sense, no feedback. So this proves the **Arduino emitted the steps**, not that the motor turned. The three multimeter checks are unchanged and still the critical path: coil continuity at the driver's terminals, `EN` at the driver pin, VREF at the wiper.

What *has* changed is the firmware gate. `stepMotor()` aborts the up direction when D9 reads HIGH; D9 now reads **LOW**, which un-gates it. **Did you see the plunger move?** The moments to have watched are `00:41:49` (~13 s, down in vial_1) and `00:43:13` (~22 s, over vial_2) — that second one is the longest single plunger command ever sent to this machine.

### 🔑 `HOME` is now a test of the motor, not of the switch

Two attempts, **26.346 s and 26.348 s** — identical to the centisecond, which is a seek that exhausts its 50 000-step (≈31.4 mm) budget rather than one that stops on a switch. With the gate open, a turning motor should cross the switch inside 31 mm. It doesn't.

So one observed `HOME` now separates the last two possibilities, by eye, in 26 seconds: the `F`/`B` LEDs are a direction readout (green `F` = DIR LOW = the homing direction). **Motor visibly turning and not stopping** → the switch or its reachability. **Nothing moving** → still the coil circuit, and the meter checks stand.

### 🔴 Now that both legs run, the firmware's own aspirate constants matter

`MOVE_TO` targets come from CubOS — 28.0 / 32.5 / 46.5 are the P20 GEN2 values from `p20-gen2-plunger-constants`, and all three appear verbatim in the trace. But **`ASPIRATE` is computed inside the firmware**, and the running 2026-09-15 image still carries `PRIME_POSITION 36.0` (a P300 plane) and `UL_TO_MM 1.8` (an estimate). A P20 GEN2's bottom is **28.0**.

This was harmless while the up-leg was refused — the plunger never came back, so only the descent existed. Now both legs run, and if the motor is turning, `aspirate` drives 8 mm past the bottom every call. [`panda_vcl_p20gen2_20260917.hex`](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/firmware/panda_vcl_p20gen2_20260917.hex) is built and fixes exactly this (`PRIME 28.0`, `UL_TO_MM 1.34`, plus `RUN_CURRENT_PERCENT 20` / `HOLD 5` for the Gen2's 1.0 A `plungerCurrent`). **Not flashed** — you asked for a run, and it moves real motion planes. Say "flash it" and I will.

---

### 🔴 `$20=0` — soft limits were switched off

Read live before anything else:

```
$20=0   $21=0   $22=1   $23=0   $132=124.000
<Alarm|WPos:409.000,309.000,124.000|FS:0,0>      (no Pn: field -- nothing asserted)
```

So the machine had **neither soft (`$20`) nor hard (`$21`) limit protection** — the exact condition under which last night's Y move ran past its stop with nothing to catch it. It also meant no run could have started: `$20` is in CubOS's critical settings set.

Restored to `$20=1`, verified directly and again in the run's own connect dump, and it persists. Cause is known and has bitten once before (2026-08-27): `configure_soft_limits_from_spans` writes `$20=0` → travels → `$20=1`, and an interruption anywhere in between leaves it off. **Worth checking after any interrupted calibration, E-stop or manual reset** — the check is now a one-command snippet in [`SOP/raspberry-pi-cubos-setup.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/SOP/raspberry-pi-cubos-setup.md).

### ✅ And the campaign-50 decap failure is explained by elimination

`decap vial_1` captured on the **first attempt** today, at coordinates byte-identical to the ones it failed at yesterday (X 206, Y 27, engage gantry Z 54.065), with the configs unchanged. So it wasn't geometry — and the pre-run frame closes the cheapest of the other candidates: **two capped glass vials in the first two seats**, the remaining four empty, tip rack behind. Exactly what this protocol needs.

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/results/pipette_test_20260918/frames/prerun_deck__cam1_csi1_cropped.jpg?raw=true)

The difference between the two runs was the machine's power state, not the deck.

And here is the capper mid-run, after `drop_tip` — a cap held on the electromagnet face above an open vial:

![](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/results/pipette_test_20260918/frames/step09_drop_tip__cam0_csi0.jpg?raw=true)

### ✅ Gantry geometry, from this run's own G-code

```
Z99.065   capper transit / park      (safe_z 115 + depth -15.935)
Z124.0    tipped hover, CLAMPED      (hover-clamp patch; = z_max)
Z54.065   capper engage              (rim 55 + engage_depth 15)
Z55.0     aspirate / blowout         (tip end deck 20, 35 mm in)
Z115.0    bare-nozzle hover at safe_z
Z122.0    step 5 pipette_park at travel_z 87
Z92.0     drop_tip        Z57.0  pick_up_tip

X 154 (vial column, pipette frame) · 206 (capper over vials) · 284 (tip rack)
```

X 284 is your measured jog point, reproduced to the millimetre for the fifth run running.

### Fixed: the second camera was being starved by a plumbing bug

4 of 8 frames. `cam0_csi0` captured all four in under 0.8 s; `cam1_csi1` timed out at 20 s on all four — after capturing a pre-run test shot in **0.59 s**.

Not the camera. `run_with_camera_capture.py:174` called `capture()` without forwarding `width`/`height`, so the in-run path always used 1920×1080 however the flags were set, while `--test-shot` honoured them. On a 1 GB Pi 5 with two 4608×2592 sensors and CubOS resident, that's what starves. Both call sites now forward the size — verified by stubbing the capture backend and reading the command it builds:

```
IN-RUN CMD: rpicam-still --camera 1 --width 1536 --height 864 --nopreview --immediate --vflip -o ...
DEFAULT   : rpicam-still --camera 1 --width 1920 --height 1080 --nopreview --immediate -o ...
```

The harness's hard rule held regardless: no camera failure touched the protocol.

### ✅ Machine state

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF` → `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | both returned to vials 1–2 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home before the next run. |
| `$20` / `$21` | **`1`** (restored) / `0` · `$130/$131/$132` = 409.000 / 309.000 / 124.000, matching the gantry file |
| Plunger | counter reset by the port-open board reset; physical position unknown |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |

**Your three config files needed no edit at all** — the trio ran exactly as committed at `d96e5e5`.

### Committed — [`7975d5e`](https://github.com/vertical-cloud-lab/byu-vcl/commit/7975d5e)

- [`cubos/results/pipette_test_20260918/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/7975d5e/cubos/results/pipette_test_20260918) — the [write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/results/pipette_test_20260918/README.md), the [hardware log](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/results/pipette_test_20260918/run_hardware.log), the [plunger trace](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/results/pipette_test_20260918/plunger_trace.json), [this run's G-code](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/results/pipette_test_20260918/gcode_thisrun.log), the [timestamped GRBL exchange](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/results/pipette_test_20260918/mill_control_thisrun.log), [machine state](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/results/pipette_test_20260918/machine_state.json), all four gate logs and the frames; campaign CSVs in [`campaign_54_20260918_003828/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/7975d5e/cubos/results/pipette_test_20260918/campaign_54_20260918_003828)
- [`cubos/tools/run_with_camera_capture.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/tools/run_with_camera_capture.py) — the width/height fix
- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/docs/opentrons-pipette-wiring.md) — new §13 with the retraction arithmetic and the status table updated
- [`SOP/raspberry-pi-cubos-setup.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/SOP/raspberry-pi-cubos-setup.md) and [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/7975d5e/cubos/README.md)

The committed tree was pulled back onto the Pi and all four gates re-run from it — PASS, 12/12, 0 interferences both ways. **What's on the branch is what ran.**

### Next, in order

1. **Watch one `HOME`** (26 s, green `F` lit). Motor turning → the switch; nothing moving → the meter checks below.
2. **Coil continuity** at the driver's own terminals, power off: blue–red and black–green a few to a few tens of ohms, blue–black open.
3. **`EN` at 0 V measured at the driver pin** (and confirm it lands on A4, not A3), then **VREF at the trimmer wiper**.
4. Then say the word and I'll flash the P20 GEN2 image and re-run.

### Not done

No firmware flashed, no wiring touched, no config file changed. I have no way to tell whether the motor physically turned — that's the one thing this run can't answer and your eyes can.

`drop_tip` still releases 35 mm above the slot pending a `tip_disposal` deck entry. Neither camera is aimed at the vial column or the tip rack, so whether a tip seated at A1 and where the undropped tip went still need looking at. Nothing is upstreamed: the `mixInPlace` compile error to BU-KABlab, the hover clamp and `_best_effort_retract_to_safe_z` to Ursa, the Cubware pin-diagram shift, the SoftwareSerial guard to janelia, and Alex's ask for PRs so the CubOS branches don't drift.

`CLAUDE.md` shows as modified in the working tree only because the action synced `main`'s copy in; it's byte-identical to `origin/main`, so I left it uncommitted.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---

## @benwhitney5463 — 2026-09-18 00:45:30 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5723280806)

@claude still no physical actuation on the P20. The LEDs on the Motor Driver were as such: B red for the majority while the Pipette was running commands, then F green after the drop tip.

---

## @claude[bot] — 2026-09-18 00:45:50 UTC

[original](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5723283674)

**Claude finished @benwhitney5463's task in 15m 20s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/35292524122)

---
### Your LED reading matches the trace command-for-command — which means everything upstream of the driver chip is now proven good, and the fault is inside one short segment

- [x] Read what the last session committed (`d96e5e5`, `7975d5e`)
- [x] Reach the Pi, read machine + Arduino state
- [x] **Found campaign 54** — a clean 12/12 run that was never reported back to you
- [x] Identify which firmware is actually on the board (`avrdude` verify)
- [x] Lay the DIR timeline against your `B`/`F` observation
- [x] Find a way to interrogate the driver that doesn't need the UART
- [x] Commit ([`803e008`](https://github.com/vertical-cloud-lab/byu-vcl/commit/803e008))

**No motion was commanded** — you reported an observation rather than asking for a run. The gantry port was opened read-only for a status query, the Arduino was read, and the electromagnet was explicitly de-energized afterwards.

---

### First: campaign 54 ran 12/12 and nobody told you

The session you interrupted at 00:10 recovered, ran the trio at **00:38:28 → 00:44:49 UTC**, completed **12/12 steps**, and pushed its artifacts — then hit the job limit before it could post. So the result has been sitting on the branch unannounced. It's the run you were watching.

🔑 **It is the first run in which no plunger command was refused.** Every retract since 2026-09-01 came back in a flat ~0.107 s having emitted nothing. This one:

| UTC | step | command | from → to | distance | dt | s/mm |
|---|---|---|---|---|---|---|
| 00:41:48 | 4 `aspirate` | `ASPIRATE 20.0` | 0 → 36 → 0 | 72 mm | 13.131 s | — |
| 00:43:13 | 8 `blowout` | `MOVE_TO 32.5` | 0 → 32.5 | **+32.5 mm** | 21.546 s | 0.663 |
| 00:43:34 | 9 `drop_tip` | `MOVE_TO 46.5` | 32.5 → 46.5 | **+14.0 mm** | 9.288 s | 0.663 |
| 00:43:47 | 9 `drop_tip` | `MOVE_TO 28.0` | 46.5 → 28.0 | **−18.5 mm** | 12.267 s | 0.663 |

**137 mm commanded**, the three `MOVE_TO` legs fitting one rate to ~1%. That fit only closes if `aspirate` left the counter at exactly 0.0 — which is `PRIME 36.0 − 20 µL × UL_TO_MM 1.8`. So the aspirate ran both of its legs too.

### Your LEDs confirm it, independently and to the command

> *"B red for the majority while the Pipette was running commands, then F green after the drop tip."*

`B` and `F` are both on the **DIR** net, and `moveTo()` latches DIR at the start of a move and holds it. Against the table above:

| UTC | what's running | direction | DIR | LED |
|---|---|---|---|---|
| 00:43:13 → 00:43:34 | `blowout`, 32.5 mm | down | HIGH | **`B` red** |
| 00:43:34 → 00:43:44 | `drop_tip` leg 1, 14.0 mm | down | HIGH | **`B` red** |
| **00:43:47 → 00:43:59** | **`drop_tip` leg 2, 18.5 mm** | **up** | **LOW** | **`F` green** — latched to the end |

Red spans 30.8 s of the last 47 s of plunger activity; green starts at `drop_tip`'s **second** leg, the only upward `MOVE_TO` in the whole protocol. Your eyes and the serial trace agree exactly, including which command flipped the pin.

**But be precise about what that proves.** Both LEDs are driven by the *Arduino's* pins. They establish that STEP and DIR arrive at the board's input pins with the right polarity and timing. Nothing on the chip's side of those pins drives them — so they say nothing about whether the TMC2209 itself is alive.

### So here's the state of the diagnosis

| | how it was eliminated |
|---|---|
| the limit-switch gate | an 18.5 mm **retract** ran for 12.267 s |
| STEP / DIR not reaching the board | your LEDs follow them, right order, right times |
| missing `VM` | **your 13 V measurement** |
| CubOS, the serial link, the firmware | 137 mm commanded, each leg timed to ~1% of its distance, landing exactly where the constants predict |

Everything that's left is between **the TMC2209's input pins and the motor windings**. That's a very short list, and I found two pins on your board that read it directly.

---

### 🔑 `DIAG` and `INDEX` — both broken out on the 6121, neither needs the UART

Straight from [Adafruit's pinout page](https://learn.adafruit.com/adafruit-tmc2209-stepper-motor-driver-breakout-board/pinouts). Neither has an LED, and neither of us has ever looked at them:

- **`DIAG`** — *"driven high if there is a problem causing the motor driver to not be able to work properly."* A fault flag the chip raises on its own.
- **`INDEX`** — *"driven high when the microstep counter is in it's zero position."* So it **pulses as the chip consumes STEP pulses**, whether or not any current reaches the coils.

`INDEX` is exactly the discriminator we've been trying to get out of the UART:

| STEP arriving | `INDEX` | what it means |
|---|---|---|
| yes | **changing** | the chip is alive and counting → the fault is downstream: the coil path, or current set to zero |
| yes | **dead flat** | the chip isn't processing STEP at all → dead, disabled, or STEP not landing on its pin |

### The measurements, in order

1. **`EN` at the driver's own pin** (not the Arduino header) — expect **~0 V**. Adafruit: *"Pull this pin high to disable the output to the motors."* ~5 V = the output stage is off.
2. **`DIAG`** — expect **~0 V**. High means the chip is telling you it has a fault.
3. **`INDEX` while a leg is running** — it must **change**. On a DMM that reads as a fluctuating mid-scale value; a rock-steady 0 V or 5 V across a 20 s move means the counter isn't running.
4. **Coil resistance at the four screw terminals**, ribbon attached, power off: `1A`–`1B` and `2A`–`2B` a few to a few tens of ohms, `1A`–`2A` open. This tests the *whole* path including crimps and whether a screw is clamping copper or insulation — the same trap that hid the gantry supply.
5. **The yellow `S` LED**, free while you're there — you didn't mention it. At 2500 steps/s it reads as a steady dim glow rather than a flicker, but it has to look *different* during a move. If it never changes, STEP isn't reaching the board and it's one wire.

To hold the plunger stepping long enough to probe, I committed [`cubos/tools/pipette_driver_measure.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/tools/pipette_driver_measure.py) — 6 mm out, 6 mm back at 200 steps/s, ~48 s per leg, timestamped at each direction change, always returning to where it started. It refuses to open the window if the limit switch reads asserted, since the return leg would be refused and the plunger would ratchet outward. **Say the word and I'll run it while you hold the meter** — or run it yourself:

```bash
~/CubOS/.venv/bin/python ~/byu-vcl/cubos/tools/pipette_driver_measure.py --move
```

### One free test you can do with the LEDs alone

`HOME` is now a live motor test. It seeks **upward for 26 s** — green `F` lit the whole time — over a 31.4 mm budget on a ~55 mm plunger. If the motor were turning it would reach the switch. Watch which way the shaft is being urged during those 26 s: toward the switch and not stopping is one fault, away from it is a different one. It's the cheapest information available and it needs nothing but your eyes.

---

### ⚠️ The board isn't running the firmware we think it is

`avrdude -U flash:v:` against all three candidate images, read-only:

| image | verify |
|---|---|
| `panda_vcl_p20_20260915.hex` | ✅ **17370 bytes of flash verified** |
| `flash_20260915T220346Z.hex` (stock backup) | ❌ mismatch at byte `0x0e` |
| `panda_vcl_p20gen2_20260917.hex` | ❌ mismatch at byte `0x0e` |

So the P20 GEN2 build was never flashed. CubOS *is* patched with the Opentrons planes and sends them as absolute targets (`prime 28.0`, `blowout 32.5`, `drop_tip 46.5`), while the firmware's own planes are still `36.0 / 44.0 / 55.0` and its `PRIME_POSITION` is a P300 number. **If the motor were turning, `aspirate` would drive the plunger 8 mm past its bottom on every call.** Harmless while the up-leg was refused; not harmless now that both legs run.

Flashing [`panda_vcl_p20gen2_20260917.hex`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/firmware/panda_vcl_p20gen2_20260917.hex) closes that *and* brings the SoftwareSerial read fix. I didn't do it — you haven't asked, and it changes real motion planes. Say so and it's a two-minute job.

### And `comm = 0` is still not evidence — now for two independent reasons

Read three more times today: `OK:{"msg":"Driver status","v":[0.00,0.00,-1.00]}`.

1. **The running image predates the read fix.** Without `tmc2209-softwareserial-read.patch` the janelia library's read path *cannot* succeed on an AVR: `write()` runs `cli()` so the Arduino never hears its own transmission, and `sendDatagramBidirectional()` then discards the first four bytes of the driver's real reply as if they were that echo.
2. **The 10 kΩ bridge is on the wrong side.** `SoftwareSerial::begin()` leaves TX a **push-pull output idling HIGH**, so with `PDN_UART` on A1 the driver can't pull the node down to reply. It has to be `A1 —1 kΩ— NODE`, with `A0` **and** `PDN_UART` both directly on `NODE`.

Both need fixing before `comm > 0` is even possible — which is why `DIAG`/`INDEX` are the better route right now.

### ✅ Machine state — untouched

| | |
|---|---|
| Motion | **none commanded** — no homing, no G-code, no plunger command |
| GRBL | `<Alarm\|WPos:409.000,309.000,124.000\|FS:0,0>` — **no `Pn:` field**, so no limit pin is asserted. Normal resting state; re-home before the next run |
| Electromagnet | off — `CMD_EMAG_OFF` → `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Plunger | `homed:0, pos:0.00, max_vol:20.00` — **no travel commanded this session** |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |
| Pi | rebooted with the machine at 00:35 UTC; CubOS `496819c` + 3 patches |

### Committed — [`803e008`](https://github.com/vertical-cloud-lab/byu-vcl/commit/803e008)

- [`cubos/docs/opentrons-pipette-wiring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/docs/opentrons-pipette-wiring.md) — new **§14**: the LED/trace correlation table, the flash verification, the `DIAG`/`INDEX` discriminator and the measurement order
- [`cubos/tools/pipette_driver_measure.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/tools/pipette_driver_measure.py) — the bounded probing window
- [`cubos/results/pipette_test_20260918/driver_probe_and_flash_verify.txt`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/results/pipette_test_20260918/driver_probe_and_flash_verify.txt) — the raw `CMD 29` reads and the three `avrdude` verifies
- [`cubos/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/803e008/cubos/README.md) — status section

Campaign 54's own logs, trace, frames and write-up were already on the branch at [`7975d5e`](https://github.com/vertical-cloud-lab/byu-vcl/commit/7975d5e) — [`cubos/results/pipette_test_20260918/`](https://github.com/vertical-cloud-lab/byu-vcl/tree/803e008/cubos/results/pipette_test_20260918).

### Not done

I can't take any of the five measurements above — they need the meter and your hands, and they are the entire critical path now. No wiring touched, no firmware flashed, no config changed, no protocol run.

Still open and unchanged: the bridge resistor on the TX side, `drop_tip` ejecting 35 mm above the slot pending a `tip_disposal` deck entry, and nothing upstreamed — the `mixInPlace` compile error to BU-KABlab, the hover clamp and `_best_effort_retract_to_safe_z` to Ursa, the Cubware pin-diagram shift, and the SoftwareSerial guard to janelia.
 · [`claude/issue-165-20260730-2304`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-165-20260730-2304)

---
