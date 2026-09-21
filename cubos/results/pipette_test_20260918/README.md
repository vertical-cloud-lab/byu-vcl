# 2026-09-18 — campaign 54: 12/12 on hardware, and the plunger retracts for the first time

Run requested by Ben ("try the trio again. The machine is homed right now").

| | |
|---|---|
| campaign | **54**, `2026-09-18T00:38:28Z` → `00:44:49Z` (lab local 18:38 → 18:44), status **`completed`** |
| trio | `cub_xl_ben_pipette_capper.yaml` + `ben_6vials_tiprack.yaml` + `pipette_test.yaml`, **exactly as committed at `d96e5e5`** |
| CubOS | `496819c` + `tipped-hover-clamp-main` + `pipette-connect-tolerate-failed-home-main` + `p20-gen2-plunger-constants` |
| firmware | the **2026-09-15** p20 image. Not reflashed this session. |
| result | **12/12 steps**, no capper retries, no alarms |

---

## 1. 🔴 `$20=0` — soft limits were switched off on the controller

Read live before anything else:

```
$20=0   $21=0   $22=1   $23=0   $27=3.000
$130=409.000  $131=309.000  $132=124.000
<Alarm|WPos:409.000,309.000,124.000|FS:0,0>        (no Pn: field)
```

Two consequences:

- **The machine had no limit protection of any kind.** `$21=0` (hard limits off)
  has been the standing configuration; with `$20=0` as well, nothing would have
  stopped an out-of-range target. That is exactly the condition under which the
  2026-09-17 late-session Y move ran 33 mm past its stop
  (`cubos/results/y_overrun_20260918/`).
- **No run could have started.** `$20` is in `Gantry._validate_grbl_settings`'
  critical set and the gantry file declares `soft_limits: true`, so
  `run_protocol` aborts at connect with *"Critical GRBL settings mismatch"*.

Restored to `$20=1` and verified, both immediately and in the run's own connect
dump (`mill_control_thisrun.log`, `_verify_connection`). It persists after the run.

The mechanism is known: `configure_soft_limits_from_spans`
(`gantry/gantry.py`) writes `$20=0`, then `$130/$131/$132`, then `$20=1`.
Interrupted between the first and last write it stays off. The same thing was
found and fixed on 2026-08-27. **Re-check `$20` after any interrupted
calibration, E-stop, or manual reset.**

## 2. The gantry

Both homing cycles succeeded on the first attempt:

```
18:39:37.113  $H  ->  18:39:55.203  Homing completed     (18.1 s)   step 0
18:44:23.434  $H  ->  18:44:47.078  Homing completed     (23.6 s)   step 11
```

Commanded Z planes, from this run's own G-code (`gcode_thisrun.log`):

| plane | what |
|---|---|
| `Z99.065` | capper transit / park — `safe_z` 115 + `depth` −15.935 |
| `Z124.0` | tipped-pipette hover, **clamped** by the hover-clamp patch (= `z_max`) |
| `Z54.065` | capper engage — rim 55 + `engage_depth_mm` 15 |
| `Z55.0` | aspirate / blowout — tip end at deck 20, 35 mm into the vial |
| `Z115.0` | bare-nozzle hover at `safe_z` |
| `Z122.0` | step 5 `pipette_park` at `travel_z` 87 |
| `Z92.0` | `drop_tip` |
| `Z57.0` | `pick_up_tip` |

Distinct X: `154.0` (vial column in the pipette frame), `206.0` (capper over the
vials), `284.0` (tip rack — the measured jog point, reproduced again).

`passive_shadow` reported **0 interferences nominal and 0 tip-stuck**.

## 3. 🔑 The plunger — every command produced distance-scaling motion, retractions included

Every command was timed live through a pass-through wrapper on
`OpentronsPipette._send_command` (`plunger_trace.json`).

| step | command | dt | commanded distance | implied rate |
|---|---|---|---|---|
| `connect()` | `STATUS` | 0.008 s | — | — |
| `connect()` | `HOME` | 26.346 s | full 50 000-step budget | — |
| `connect()` | `HOME` retry | 26.348 s | full budget again | — |
| `pick_up_tip` | `MOVE_TO 0.0` | 0.006 s | 0 mm (already at 0) | correct no-op |
| `aspirate` | `ASPIRATE 20.0` | 13.131 s | down 36 + **up 36** | see below |
| `blowout` | `MOVE_TO 32.5` | 21.546 s | +32.5 mm | **0.663 s/mm** |
| `drop_tip` | `MOVE_TO 46.5` | 9.288 s | +14.0 mm | **0.663 s/mm** |
| `drop_tip` | `MOVE_TO 28.0` | 12.267 s | **−18.5 mm** | **0.663 s/mm** |

The three `MOVE_TO` round trips reproduce their commanded distances to within
0.01 mm at a single consistent rate — and **one of them is a retraction**. In
every run since 2026-09-15 a retraction returned a flat ~0.107 s having emitted
no steps at all.

`ASPIRATE` corroborates it independently. `aspirate()` drives *down* to
`PRIME_POSITION` and then *up* by `volume × UL_TO_MM`; the up-leg is the gated
direction. On the running image (`PRIME_POSITION 36.0`, `UL_TO_MM 1.8`) a 20 µL
aspirate from 0.0 is 36 mm down then 36 mm back to 0.0. Campaigns 26/36 saw
**5.962 s** for the down-leg alone; this run saw **13.131 s**, i.e. both legs.
That also explains why `MOVE_TO 32.5` measured exactly 32.5 mm of travel: the
aspirate really did land back at 0.0.

### What this proves, and what it does not

`stepMotor()` bit-bangs the STEP pin and counts loop iterations — no encoder, no
current sense, **no feedback of any kind**. So a distance-scaling round trip
proves the **Arduino emitted the steps**. It does not prove the motor turned;
that still needs eyes on the plunger.

What *has* changed is the **firmware gate**: `stepMotor()` aborts the up
direction when `digitalRead(PIPETTE_LIMIT_PIN) == HIGH`, and `HOME` returns a
fake success in 0.52 s in the same state. Two independent readings say D9 is now
LOW (loop closed): the retractions are no longer refused, and `HOME` runs its
full 26.3 s budget instead of returning in 0.52 s.

### `HOME` still fails

`homePipette()` gives up after 50 000 steps ≈ 31.4 mm of upward seek. Two
attempts, 26.346 s and 26.348 s — identical, which is the signature of a seek
that runs out its budget rather than one that terminates on a switch. Either the
motor is not turning, the plunger starts further than 31 mm from the switch, or
the seek runs away from it. **The `F`/`B` LEDs on the driver breakout are a free
direction readout** (`F` green = DIR LOW = the homing direction), and `HOME` runs
for 26 s, so watching one `HOME` answers it by eye.

### 🔴 The firmware's own aspirate constants are now the weak link

`MOVE_TO` targets come from CubOS (`p20-gen2-plunger-constants`: prime 28.0,
blowout 32.5, drop_tip 46.5 — all three visible in the trace). But `ASPIRATE`
uses the **firmware's** `PRIME_POSITION` and `UL_TO_MM`, and the running image
still carries `36.0` / `1.8` — a P300 plane and an estimate. A P20 GEN2's bottom
is at 28.0, so if the motor is turning, `aspirate` is driving the plunger 8 mm
past it.

`cubos/firmware/panda_vcl_p20gen2_20260917.hex` is built and waiting and fixes
exactly this (`PRIME_POSITION 28.0`, `UL_TO_MM 1.34`, plus
`RUN_CURRENT_PERCENT 20` / `HOLD_CURRENT_PERCENT 5` for the Gen2's 1.0 A
`plungerCurrent`). It was not flashed this session — Ben asked for a run, not a
flash, and it moves real motion planes.

`CMD 29` still reads `comm = 0`, which remains uninformative: the running image
predates `tmc2209-softwareserial-read`, and that read cannot succeed on an AVR
without it whatever the wiring does.

## 4. The deck, and why `decap` worked this time

Campaign 50 (2026-09-17) aborted at step 2 with *"sensor did not confirm cap
capture after 3 attempt(s)"*. Campaign 54 captured on the **first** attempt, at
the same commanded coordinates (X 206, Y 27, engage gantry Z 54.065 — the G-code
is identical). Nothing in the configs changed between the two runs.

`frames/prerun_deck__cam1_csi1_cropped.jpg` shows why the "is there a vial in
slot 1" question is closed: **two capped glass vials in the first two seats**,
with the remaining four seats empty, and the tip rack behind them. That is
exactly what this protocol needs, and it rules out the cheapest of the three
campaign-50 candidates. The difference between the two runs was the machine's
power state, not the deck.

`frames/step02_decap__cam0_csi0.jpg` and `frames/step09_drop_tip__cam0_csi0.jpg`
both show a cap held on the electromagnet face above an open vial.

## 5. Cameras: 4 of 8, and a bug in the harness

`cam0_csi0` captured all four frames in under 0.8 s each. `cam1_csi1` timed out
at the 20 s limit on all four.

Not the camera: the same camera captured in **0.59 s** in the pre-run
`--test-shot`. The difference is a plumbing bug —
`run_with_camera_capture.py:174` called `capture()` without forwarding `width`
and `height`, so the in-run path always used the 1920×1080 defaults while
`--test-shot` honoured `--width`/`--height`. On a 1 GB Pi 5 driving two
4608×2592 sensors with CubOS resident, the full-resolution capture is what
starves. **Fixed** — both call sites now forward the requested size.

The harness's hard rule held throughout: no camera failure touched the protocol.

## 6. Machine state

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF` → `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | both returned to vials 1–2 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home before the next run. |
| `$20` | **`1`** (restored) · `$21=0` · `$130/$131/$132` = 409.000 / 309.000 / 124.000 |
| Plunger | counter reset by the port-open board reset; physical position unknown |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |

## Files

| file | what |
|---|---|
| `run_hardware.log` | the run, start to finish |
| `plunger_trace.json` | every plunger command, timed |
| `gcode_thisrun.log` | the G-code this run emitted |
| `mill_control_thisrun.log` | the timestamped GRBL exchange, including both homing cycles and the `$$` dump |
| `machine_state.json` | settings and instrument reads, before and after |
| `validate.log` `mock.log` `shadow.log` `shadow_ts.log` | the four offline gates |
| `campaign_54_20260918_003828/` | campaign CSVs |
| `frames/` | 4 in-run frames (cam0) + the cropped pre-run deck view (cam1) |

`cam1_csi1` looks across the bench into the room, so its frame is committed
cropped to the deck; the uncropped original is on the Pi in `/tmp/prerun`.
