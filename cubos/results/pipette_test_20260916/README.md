# `pipette_test` on the CubXL — 2026-09-16, campaign 36

Requested by @benwhitney5463: *"run the trio again this time with the current
percent at 17"*.

**Outcome: steps 0–10 of 12 executed on hardware. The closing `home` (step 11)
failed, and the machine was left in GRBL `Alarm` deliberately.** The plunger
behaved exactly as in campaign 26 — because `RUN_CURRENT_PERCENT 17` never
reaches the TMC2209 (§2).

| | |
|---|---|
| Campaign | `campaign_36_20260916_222114` |
| Window (UTC) | 22:21:14 → 22:26:12 |
| Steps executed | 11 of 12 (`home` at step 11 failed) |
| Camera frames | 10 of 10 captured, no failures |
| CubOS | `496819c` + `tipped-hover-clamp-main`, `pipette-connect-tolerate-failed-home-main`, `p20-mm-to-ul-passthrough` |
| Firmware | VCL p20 image (`max_vol: 20.00` confirms it is live) |

Note the log timestamps are Pi local time (UTC−6); the campaign directory name
and the plunger trace are UTC.

---

## 1. The homing failure

### What the controller says

Read live after the run, six samples over 3 s, identical every time:

```
<Alarm|WPos:409.000,309.000,124.000|FS:0,0|Pn:X|WCO:-409.000,-309.000,-124.000>
```

`Pn:X` is GRBL's pin-state field: **the X limit switch is currently asserted.**
`Pn:Y` and `Pn:Z` are absent.

This is a clean before/after. The same read taken *before* the run carried **no
`Pn:` field at all**:

```
<Alarm|WPos:409.000,309.000,124.000|FS:0,0|WCO:-409.000,-309.000,-124.000>
```

`WPos` is not a real position — the board resets when the port opens, so it
reports `-max_travel` on every axis. The *physical* position is unknown.

### The homing attempts

From `mill_control_thisrun.log`. `driver.home()` polls status after `$H`; on
seeing `Alarm` it logs `Homing failed, trying again...`, clears buffers and
re-sends `$H`, until the 90 s timeout.

```
16:24:13.626  $H
16:24:55.412  Homing failed, trying again...      (41.8 s)
16:24:55.412  $H
16:25:07.467  Homing failed, trying again...      (12.1 s)
16:25:07.467  $H
16:25:47.934  Homing failed, trying again...      (40.5 s)
16:25:47.934  $H
16:25:59.995  Homing failed, trying again...      (12.1 s)
16:25:59.995  $H
16:26:10.505  Homing timed out
```

So GRBL entered `Alarm` on every attempt. The alternation between ~41 s and
~12 s is the driver re-issuing `$H` while GRBL is still locked out.

### First failure ever recorded on this Pi

`~/.cubos/logs/gantry/mill_control.log` covers 2026-09-15 15:51 → 2026-09-16
16:26 — the whole life of this Pi's CubOS install:

| when | result |
|---|---|
| 2026-09-15 15:52:15 | Homing completed ✅ (campaign 26, step 0) |
| 2026-09-15 15:56:39 | Homing completed ✅ (campaign 26, step 11) |
| **2026-09-16 16:21:51** | **Homing completed ✅ (this run, step 0)** |
| 2026-09-16 16:24:13 → 16:26:10 | 4 retries, then timeout ❌ (this run, step 11) |

Homing worked at the start of this run and failed 2.5 minutes later at the end
of it.

### Reading: Z homed, X found its switch, Y did not

Stock GRBL homes Z first (`HOMING_CYCLE_0`), then X and Y together
(`HOMING_CYCLE_1`). Settings read live: `$23=0` (home toward max on every
axis), `$27=3.000` (pull-off), `$25=1000` (seek), `$21=0` (hard limits off).

Chaining that against the pin state:

- **Z reached its switch**, or X would never have moved. It now reads clear
  because the cycle pulls off `$27` = 3 mm at the end.
- **X reached its switch** — `Pn:X`, and it is still holding it.
- **Y did not** — no `Pn:Y`. GRBL aborts a homing cycle once an axis exceeds
  `1.5 × $131` = 463 mm without triggering, which at `$25` = 1000 mm/min is
  ~28 s. That fits the observed ~41 s attempt (Z cycle first, then X+Y).

`Pn:Z` is *normal* mid-protocol, incidentally: every `travel_z: 124` pose in
this protocol sits exactly on Z's max switch, and the run log shows `Pn:Z` at
every Z 124 line. It is not a fault.

### What was in the machine

The protocol only ever visits deck x 154–284, y 13–60. **`home` is the only
command that drives to the far corner (409, 309)** — which is why 11 steps of
normal motion can succeed and the closing home still fail.

The camera frames show two things that were inside the envelope during the run
and are worth ruling out first:

- **The p20 is not on the gantry** — it is on the bench, tethered into the
  moving head by its FC-10P ribbon (`frames/step10_cap__cam0_csi0.jpg`, where
  the body is legible as `P20 GEN2`). A tether sized for the protocol's working
  area does not have to reach (409, 309).
- **A hand was in the work area** (`frames/step09_drop_tip__cam0_csi0.jpg`).
  Expected — Ben said he would be watching and holding the pipette — but it is
  a candidate obstruction and it belongs in the record.

Both are hypotheses. What is measured is: Y did not reach its switch, X is
sitting on its own, and nothing like it has happened on this machine before.

### Why the machine was left in `Alarm`

`Alarm` is the safe state — GRBL refuses motion in it. Re-homing would drive Y
into whatever stopped it, for ~28 s per attempt; that has already happened five
times. Clearing it needs eyes on the machine, so it was left alone.

Everything else is safe and confirmed by direct query after the run:

| | |
|---|---|
| Caps | **both returned** — steps 6 (`cap vial_1`) and 10 (`cap vial_2`) both completed |
| Electromagnet | off — `CMD_EMAG_OFF` → `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Ports | `/dev/ttyUSB0`, `/dev/ttyACM0` — both free |
| `$20` soft limits | `1` |

One unrelated thing the failure exposed: `_best_effort_retract_to_safe_z()` in
`protocol_engine/setup.py` still raises `KeyError: "Unknown instrument
'PawduinoCapper'"` — it passes an instrument *object* where a *name* is
expected. This is the long-standing upstream bug, still present at `496819c`,
and it means the outer safety retract is dead code. It did not matter here (the
failing step was `home`, which commands no tool-relative motion), but it is
worth upstreaming.

---

## 2. `RUN_CURRENT_PERCENT 17` is in the image and never reaches the chip

The flashed firmware is the VCL p20 image — `STATUS` returns `max_vol: 20.00`
against the stock 300.0, so it is unambiguously live, and
`panda-arduino-p20-and-driver-status.patch` sets `RUN_CURRENT_PERCENT 17`.

But `CMD_PIPETTE_DRIVER_STATUS` (29), read five times consecutively before the
run and again after:

```
OK:{"msg":"Driver status","v":[0.00,0.00,-1.00]}
      comm = 0      flags = 0      current_scaling = -1
```

`comm = 0` is the firmware's *"no reply at all"* case — `isCommunicating()`
resolves to `getVersion() == VERSION`, so zero means no valid version byte came
back over the A0↔A1 bridge.

**Consequences:**

- `setRunCurrent(17)` is a UART register write. It never landed. The chip is on
  power-on defaults with the VREF pot setting current, exactly as it was at 50.
- So this run is electrically identical to campaign 26. The current change
  cannot be evaluated until `comm` is non-zero.
- ⚠️ **`flags = 0` does not mean "no faults".** `getDriverDiagnostics()` only
  reads the status register when `comm > 0`; `current_scaling = -1` is the
  explicit unread sentinel and `flags` carries no information either. The
  `open_load_a` / `open_load_b` bits — the coil-continuity answer — are only
  meaningful once the driver replies.

The two-minute discriminator is unchanged: with the driver idle and powered,
try to turn the plunger by hand. No holding torque at all ⇒ no coil current ⇒
check VM at the driver's screw terminal (12 V; the Arduino's VDD is logic
only), then the VREF pot, then coil continuity. Holding torque present ⇒ the
fault is the UART path alone ⇒ check that PDN_UART really lands on A1, and the
bridge itself.

---

## 3. The plunger trace

Motion on this firmware costs ~0.673 s/mm, so a round trip that does not scale
with the commanded distance emitted no steps. (Timing proves the *Arduino*
toggled STEP — not that the motor turned.)

| step | command | dt | stepped? |
|---|---|---|---|
| `connect()` | `STATUS` | 0.008 s | — |
| `connect()` | `HOME` | 0.520 s | no — back-off only, limit switch asserted |
| `connect()` prime | `MOVE_TO 5.0` | 3.355 s | **yes** |
| `pick_up_tip` | `MOVE_TO 0.0` | 0.109 s | no — refused (upward) |
| `aspirate` | `ASPIRATE 20.0` | 5.962 s | **yes**, → reports 36.00 |
| `blowout` | `MOVE_TO 7.0` | 0.107 s | no — refused |
| `drop_tip` | `MOVE_TO 10.0` | 0.109 s | no — refused |
| `drop_tip` | `MOVE_TO 5.0` | 0.107 s | no — refused |

Same shape as campaigns 77, 83 and 26: the plunger limit switch still reads
asserted (`homed: 0`, `HOME` in 0.520 s), so `stepMotor()`'s gate refuses every
upward command after one step.

### The volume chain now carries real microlitres

This is the one thing that did change, and it is what `mm_to_ul: 1.0` +
`UL_TO_MM 1.8` + `MIN_VOLUME 1.0` were for:

```
protocol volume_ul  20.0
  x mm_to_ul 1.0    -> ASPIRATE 20.0      (CubOS; previously ASPIRATE 0.5)
                       reply v:[20.00, 36.00]
```

Previously CubOS sent `0.5`, the firmware clamped it up to the P300's
`MIN_VOLUME 5.0`, and every trace landed at 35.45. Now 20.0 goes through
un-clamped and is echoed back as 20.00.

The landing position of 36.00 is `PRIME_POSITION`, and is the limit switch
again, not a conversion error: `aspirate()` drives *down* to 36.0 first, then
*up* to `36.0 − 20 × 1.8` = 0.0. The second leg is upward, so it is refused and
the plunger stops at 36.0. Fix the limit switch and that stroke becomes a real
20 µL draw.

---

## 4. Offline gates (all green, before the run)

| gate | result |
|---|---|
| `validate_setup` | PASS |
| `run_protocol --mock` | 12/12 steps |
| `passive_shadow` | 0 interferences |
| `passive_shadow --tip-stuck` | 0 interferences |

All ten settings in `_validate_grbl_settings`' critical set matched the gantry
file: `$3`/`$20`/`$22`/`$23` = 1/1/1/0, `$100`–`$102` = 400.000,
`$130`/`$131`/`$132` = 409.000/309.000/124.000.

---

## 5. Cameras

10 of 10 frames captured, every one under 0.7 s — against campaign 26, where
cam1 timed out at 20 s on five of six. The difference is capture resolution
pressure on a 1 GB Pi; frames still land at 1920×1080.

Captured after steps 3 (`pick_up_tip`), 4 (`aspirate`), 8 (`blowout`),
9 (`drop_tip`) and 10 (`cap vial_2`), plus a pair taken after the homing
failure (`after_homing_failure__*`).

**`cam1_csi1` frames in this directory are cropped.** That camera looks across
the bench into the room and a lab member is in frame on the left of every shot;
this repository is public. The crop box is `(1120, 260) → (1920, 1080)`,
chosen to land well right of the furthest-right the person reaches in any
frame. Uncropped originals are on the Pi in `/tmp/run_frames`. `cam0_csi0`
frames are committed as captured — they look into the machine and contain no
faces.

Neither camera is aimed at the tip rack, so whether a tip seated at A1 and
where the undropped tip went are still open.

---

## Files

| file | what |
|---|---|
| `run_hardware.log` | full run output including the traceback |
| `mill_control_thisrun.log` | the driver's GRBL exchange, with timestamps |
| `gantry_command_thisrun.log` | every G-code line sent |
| `plunger_trace.json` | every plunger command with its round-trip time |
| `grbl_and_arduino_20260916.json` | `$$` dump, six post-failure status reports, Arduino state |
| `validate.log`, `mock.log`, `shadow_nom.log`, `shadow_stuck.log` | the four offline gates |
| `frames/`, `frames.json` | the 12 frames and their capture manifest |

Campaign CSVs: `../campaign_36_20260916_222114/`.
