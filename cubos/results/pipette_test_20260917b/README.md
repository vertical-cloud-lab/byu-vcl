# Campaign 50 — 2026-09-17 23:42 UTC — the gantry is alive again; `decap vial_1` did not confirm

Trio as committed at `46e1419`, unchanged:

| | |
|---|---|
| gantry | `cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml` |
| deck | `cubos/configs/deck/ben_6vials_tiprack.yaml` |
| protocol | `cubos/configs/protocol/vcl/pipette_test.yaml` |
| CubOS | `496819c` + `tipped-hover-clamp-main`, `pipette-connect-tolerate-failed-home-main`, `p20-gen2-plunger-constants` |
| result | **failed at step 2 (`decap vial_1`)**, 0 steps completed |

## The headline: homing worked, first attempt

```
2026-09-17 17:43:32,729  Command sent: $H
2026-09-17 17:43:50,808  Homing completed          <- 18.1 s, first try
```

Compare campaign 46 four hours earlier: five `$H` attempts, every one failing, then
`Homing timed out`. The difference is that the gantry's stepper supply was switched on.

## Correction: there was never a limit-switch fault

Campaign 46's write-up claimed two independent faults — a Z limit switch that never
asserts, and an X switch stuck closed. **Both were artifacts of the gantry being
unpowered, and the reasoning that produced them was wrong.**

`WPos` is GRBL's *internal step counter*, not a measurement. With motor power absent the
controller emits every step and reports a plausible position while nothing physically
moves. Therefore:

| campaign 46 claim | actual |
|---|---|
| "Z moves perfectly. Its switch never asserts" | only the **counter** moved 124 -> 99 -> 124. Z never travelled, so `ALARM:9` after a 186 mm search was correct |
| "X's switch is stuck asserted — a second fault" | `Pn:X` was truthful *and* power-dependent. It is **absent** in every read now |
| "a single disturbance to the limit-switch harness; the drag chain is the common path" | nothing is wrong with the harness |

Six consecutive status reads today, before any motion:

```
<Alarm|WPos:409.000,309.000,124.000|FS:0,0|WCO:-409.000,-309.000,-124.000>
<Alarm|WPos:409.000,309.000,124.000|FS:0,0|Ov:100,100,100>
<Alarm|WPos:409.000,309.000,124.000|FS:0,0>                x4
```

No `Pn:` field at all.

It also re-explains **campaign 36** (2026-09-16), previously filed as a separate Y fault:
steps 0-10 ran with the capper's line-break sensor confirming a real cap capture — only
possible if the head was physically moving — and then the closing `home` failed 2.5
minutes later. Consistent with the motor supply dropping out around 2026-09-16 22:24 UTC.

**Lesson worth keeping: `?` reports the counter; only a limit pin or an instrument sensor
reports reality.** The `Pn:` field is driven by the switches, not the step generator, and
was available as a power-independent discriminator the whole time.

## Why the decap failed — the geometry is provably identical to a run that worked

Commanded sequence, real hardware window only (`mill_control.log`, which the mock gantry
does not write to):

```
campaign 36  2026-09-16, decap vial_1 SUCCEEDED first attempt
  $H  Z99.065  X206.0  Y25.0  Z124.0  Y27.0  Z99.065  Z54.065  Z99.065  Z124.0  X284.0 ...

campaign 50  2026-09-17, decap vial_1 FAILED 3x
  $H  Z99.065  X206.0  Y25.0  Z124.0  Y27.0  Z99.065  Z54.065  Z99.065  Z54.065  Z99.065  Z54.065  Z99.065
```

Byte-identical up to and including the first engage. Same X 206, same Y 27, same engage
plane gantry Z 54.065 (= deck Z 70.0 = rim 55 + `engage_depth_mm` 15). The two runs then
diverge only in that campaign 36 confirmed and moved on to the tip rack, while campaign 50
retried twice more and aborted.

So the commanded position is not the problem. Candidates, cheapest first:

1. **No vial or no cap in slot 1.** The campaign 46 frames showed the column looking
   sparse — "two capped glass vials plus a row of loose caps". Five seconds to check.
2. **The electromagnet has no coil power.** The Arduino acknowledges `CMD_EMAG_ON`
   whether or not the coil is energised — it is just a pin. If the magnet's supply is on a
   different switch from the gantry's, the symptom is exactly this: descend, "energise",
   read `cap_present=False`, retry, abort. Given one supply was already found switched
   off, this is worth ruling out explicitly.
3. **Cap too tight.** Ben's own 2026-08-03 observation: the one cap the capper failed to
   lift was on a vial slightly wider than the rest.

The interlock behaved correctly: 3 attempts, then abort with the tool retracted to
`safe_z`, before any pipette motion. No vial was opened and nothing entered a capped vial.

## Plunger

Only three commands reached the Arduino before the gantry step failed:

| command | dt | reply |
|---|---|---|
| `STATUS` | 0.008 s | `homed:0, pos:0.00, max_vol:20.00` |
| `HOME` | **26.331 s** | `ERR:{"error":"Failed to home pipette"}` |
| `HOME` retry | **26.337 s** | `ERR:{"error":"Failed to home pipette"}` |

26.3 s is the firmware running its full 50 000-step seek — the **D9-LOW** signature, i.e.
the pipette's limit-switch loop reads *clear*. (The 0.52 s fake success seen on
2026-09-15/16 was D9 HIGH, loop open.) `prime()` never ran, because the connect patch
raises before it, so **no plunger travel was commanded this session**.

`CMD 29` still reads `comm = 0`, which remains uninformative: the running image is the
2026-09-15 p20 build, which predates `tmc2209-softwareserial-read`, and that read cannot
succeed on an AVR without it whatever the wiring does.

## Offline gates — all green, on the Pi, from the committed tree

| gate | result |
|---|---|
| `validate_setup` | PASS, 12 steps |
| `run_protocol --mock` | 12/12 |
| `passive_shadow` | 0 interferences |
| `passive_shadow --tip-stuck` | 0 interferences |

## Machine state at the end of the session

| | |
|---|---|
| Protocol | failed at step 2; tool retracted to `safe_z` by the capper's own `_safe_retract` |
| Electromagnet | off — `CMD_EMAG_OFF` -> `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| GRBL | `Alarm`, **no `Pn:` field**. Normal: the board resets when the port closes |
| `$130/$131/$132` | 409.000 / 309.000 / 124.000 — matches the gantry file |
| `$20` / `$21` / `$22` / `$23` / `$5` | 1 / 0 / 1 / 0 / 0 |
| Plunger | `homed:0, pos:0.00, max_vol:20.00`; no travel commanded |
| Ports | `/dev/ttyUSB0`, `/dev/ttyACM0` — both free |

## Session notes

* The Pi **rebooted** at 23:35:23 UTC (`uptime -s`) and was off the tailnet from 23:23:47
  to 23:40:03. It shares power with whatever was switched, which is worth knowing before
  the next power event — a run in progress would be cut.
* `rpicam-still --camera 1` hung again and had to be killed; camera 0 captured in under a
  second. Same 1 GB-Pi buffer contention seen on 2026-09-15. Neither camera is aimed at
  the vial column, so the deck frame here does not show slot 1.
* The gates write to the same `command.log` as a hardware run, so any G-code comparison
  must use `mill_control.log` (which only the real driver writes) or a tight time window.

## Files

| file | what |
|---|---|
| `mill_control_thisrun.log` | real driver exchange, timestamped, from `$H` onward |
| `gantry_command_thisrun.log` | G-code |
| `plunger_trace.json` | the three plunger commands with timings |
| `validate.log`, `mock.log`, `shadow_nominal.log`, `shadow_tipstuck.log` | offline gates |
| `frames/deck_after_decap_fail_cam0.jpg` | deck after the abort, cropped to the machine |
| `campaign_50_20260917_234224/` | campaign CSVs, status `failed` |
