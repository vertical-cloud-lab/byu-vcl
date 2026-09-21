# 2026-09-17 — trio run attempt: blocked at step 0 by a gantry limit-switch fault

Ben asked for the trio to be run again. It did not run: **`home` (step 0) failed
and the protocol executed 0 steps.** Nothing was commanded to the deck — no
capper motion, no pipette motion, no vial was approached.

The homing failure is not the one from campaign 36. That one was Y failing to
reach its switch on the *closing* home; this one is **Z**, on the *opening*
home, and the evidence below identifies it precisely.

Configs are the branch's committed trio, unchanged:

| | |
|---|---|
| gantry | `cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml` |
| deck | `cubos/configs/deck/ben_6vials_tiprack.yaml` |
| protocol | `cubos/configs/protocol/vcl/pipette_test.yaml` |
| CubOS | `496819c` + 3 patches (`tipped-hover-clamp-main`, `pipette-connect-tolerate-failed-home-main`, `p20-gen2-plunger-constants`) |
| firmware | the 2026-09-15 p20 image (`max_vol: 20.00`) — the P20 GEN2 image is built but **not** flashed |
| campaign | 46, `2026-09-17T23:10:46Z` → `23:13:40Z`, status `failed` |

## Offline gates — all green

Run before any motion, against the installed tree:

```
validate_setup              PASS
run_protocol --mock         12/12 steps
passive_shadow              0 interferences (22 poses, 36 deck obstacles)
passive_shadow --tip-stuck  0 interferences
```

So the configs are not the problem.

## The failure

```
ERROR during execution: Homing timed out after 90 seconds
Protocol did not complete — 0 steps executed before exit.
```

`Mill.home()` polls status and re-sends `$H` whenever it sees `Alarm`. Eight
attempts in 107 s, alternating ~11.3 s and ~12.1 s — a *fast, repeatable*
failure, quite unlike campaign 36's 41.8 s / 12.1 s pattern.

### The alarm code: `ALARM:9`, and the axis is Z

One instrumented `$H` with the raw serial stream captured:

```
before $H: <Idle|WPos:409.000,309.000,124.000|FS:0,0|Pn:X|...>
  t+11.46s  ALARM:9
  t+12.46s  <Alarm|WPos:409.000,309.000,310.000|FS:0,0|Pn:X|WCO:-409.000,-309.000,-124.000>
```

`ALARM:9` is *"Homing fail. Could not find limit switch within search
distance."* Two numbers identify the axis:

- **The Z counter ran from 124 to 310 — exactly +186 mm, which is `1.5 × $132`
  (1.5 × 124)**, GRBL's search distance for Z.
- **It failed at t+11.46 s.** 186 mm at `$25 = 1000` mm/min is 11.2 s.

GRBL homes Z first, so the cycle never reached X or Y. Z searched its entire
budget upward and its switch never asserted.

## Two independent limit-switch faults, both measured

### Z — moves fine, switch never asserts

Jogged Z ±25 mm and polled the pin state throughout:

```
jog Z-25 -> 124.000 -> 99.000   (smooth, at commanded feed)   Pn:X
jog Z+25 ->  99.000 -> 124.000  (smooth)                      Pn:X
jog Z+10 -> error:15   (soft limit; GRBL's assumed Z ceiling is 124)
```

`Pn:Z` never appeared — not at Z 124, not anywhere, and not immediately after
the homing attempt had driven Z 186 mm upward into its physical top. The Z
axis is mechanically fine; the switch or its wiring is not being seen.
`$5 = 0`, so a limit pin reads *not triggered* when its circuit is **open**.

### X — switch stuck asserted, 20 mm off the switch

```
at rest (carriage parked at X max):   Pn:X
$J=G91 X-10  ->  WPos X 409 -> 399    Pn:X
$J=G91 X-10  ->  WPos X 399 -> 389    Pn:X
```

The carriage moved 20 mm away from its switch and **`Pn:X` never cleared.**
That is a stuck-closed switch or a signal line shorted to ground — not a
carriage parked on a switch, which is what it had been read as.

**This matters for the fix:** it does not block anything today (`$21 = 0`, hard
limits off, which is why campaign 36's 11 steps ran fine), but homing *does*
read the limit pins. Once Z is repaired, X's homing will pull off `$27 = 3` mm,
find the switch still triggered, and raise **`ALARM:8`**. So **both have to be
fixed before homing can succeed** — fixing Z alone will just change the alarm
code.

### Timeline

| when | Z switch | X switch |
|---|---|---|
| 2026-09-16 16:21:51 — campaign 36 step 0 | ✅ homing completed | no `Pn:` field at all |
| 2026-09-16 16:24:13 — campaign 36 step 11 | ❌ homing failed | — |
| 2026-09-16 onward | ❌ | `Pn:X` asserted continuously |
| 2026-09-17 23:11 — this run | ❌ `ALARM:9` | `Pn:X`, stuck 20 mm off |

Both changed state **during campaign 36**, in the 2.5 minutes between a
successful home and a failed one. A single disturbance to the limit-switch
harness — the drag chain is the obvious common path — would account for both.

## Plunger: the limit switch flipped back to CLEAR

Three commands reached the Arduino before the gantry failure:

| command | dt | reply |
|---|---|---|
| `STATUS` (14) | 0.008 s | `homed:0, pos:0.00, max_vol:20.00` |
| `HOME` (10) | **26.345 s** | `ERR:{"error":"Failed to home pipette"}` |
| `HOME` (10) retry | **26.345 s** | `ERR:{"error":"Failed to home pipette"}` |

Campaign 36 and every session since 2026-09-01 saw `HOME` return in **0.520 s**
with a fake success — the signature of D9 reading HIGH (loop open, switch
"asserted"). 26.345 s is the firmware running its full 50 000-step budget,
which is the **D9-LOW** signature.

So the pipette's limit-switch loop now reads **clear**, which un-gates the
upward direction in `stepMotor()`. `blowout` and both `drop_tip` legs would
execute for the first time — as far as the firmware is concerned. Whether the
motor turns is still a separate question: `CMD 29` reads `comm = 0` (expected,
the running image predates `tmc2209-softwareserial-read`).

`prime()` never ran: `pipette-connect-tolerate-failed-home` raises before it, so
**no plunger travel was commanded this session.**

## Machine state

| | |
|---|---|
| Protocol | failed at step 0; **0 steps executed**, no deck motion |
| GRBL | `<Alarm\|WPos:409.000,309.000,124.000\|FS:0,0\|Pn:X>` — Alarm refuses motion |
| Position | X ~20 mm off its max switch (from the jog test); Y unmoved; Z at/near its top |
| `$5` / `$20` / `$21` / `$22` / `$23` / `$27` | 0 / 1 / 0 / 1 / 0 / 3.000 |
| `$130` / `$131` / `$132` | 409.000 / 309.000 / 124.000 — matches the gantry file |
| Electromagnet | off — `CMD_EMAG_OFF` → `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Plunger | `homed:0, pos:0.00, max_vol:20.00`; **no travel commanded** |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free, link healthy (20/20 clean round-trips) |

⚠️ Z was driven upward against its top for ~11 s per homing attempt — 8 from the
protocol plus 1 diagnostic, on top of campaign 36's 4. A stepper against a hard
stop skips steps rather than breaking, but the Z coupling and belt are worth an
eyeball.

## What to check

1. **The Z limit switch and its wiring** — continuity across the switch with Z
   at its top, and back to the controller's Z limit pin. With `$5 = 0` an open
   circuit reads *not triggered*, which is exactly what GRBL sees.
2. **The X limit switch and its wiring** — it reads triggered with the carriage
   20 mm away, so look for a shorted or pinched signal line.
3. **The drag chain**, as the common path both run through, and as the only
   thing that was moving when both changed state.
4. A free confirmation once you are at the machine: press each switch by hand
   and watch GRBL's `Pn:` field — it names every asserted limit pin.

```bash
cd ~/CubOS && .venv/bin/python -c "
from cubos.gantry.gantry_driver.driver import Mill
m = Mill('/dev/ttyUSB0'); m.connect()
import time
for _ in range(40):
    print(m.query_raw_status()); time.sleep(1)
m.disconnect()"
```

## Files

- `run_hardware.log` — the full run, including the four offline gates
- `mill_control_thisrun.log` — the GRBL exchange with timestamps
- `plunger_trace.json` — the three plunger commands and their timings
- `final_state.json` — GRBL status and settings, Arduino replies, after the session
- `validate_setup.log`, `mock.log`, `shadow_nominal.log`, `shadow_tipstuck.log`
- `frames/` — cam0 and cam1 at each stage of the Z jog test. cam1 frames are
  cropped to the deck strip: that camera looks across the bench into the room
  and a lab member is in frame, and this repository is public. Uncropped
  originals are on the Pi in `/tmp/zdiag`.
- `campaign_46_20260917_231046/` — the campaign CSVs (`status: failed`)
