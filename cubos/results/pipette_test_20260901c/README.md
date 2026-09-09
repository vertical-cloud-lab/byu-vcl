# `pipette_test.yaml` on the CubXL — 2026-09-01, run C (campaign 69)

**Result: 12/12 steps, `completed`, 19:01:52 → 19:07:08 UTC (5 m 16 s).**
**First run in which every plunger command actuated — including `blowout` and
`drop_tip`, which had silently no-opped since 2026-08-31.**

Trio run: the files committed at `abd81d6`, unchanged.

| file | rev |
|---|---|
| `cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml` | `abd81d6`, unchanged |
| `cubos/configs/deck/ben_6vials_tiprack.yaml` | `abd81d6`, unchanged |
| `cubos/configs/protocol/vcl/pipette_test.yaml` | `abd81d6`, unchanged |

## What changed on the hardware

Ben rewired the pipette between 2026-09-01 18:26 UTC (the previous session's
observed `USB disconnect`) and 18:50 UTC (`/dev/ttyACM0` re-enumerated).

The rewiring **kept** the direction fix from the previous rev and did **not**
fix homing. Both measured before any protocol was sent:

```
  HOME (cold)              dt=  26.35s  ERR:{"error":"Failed to home pipette"}   pos=0.0 homed=0
  MOVE_TO 1.0 mm           dt=   0.67s  pos=1.0
  MOVE_TO 3.0 mm           dt=   1.33s  pos=3.0
  HOME (from 3.0)          dt=  26.35s  ERR:{"error":"Failed to home pipette"}   pos=3.0 homed=0
  MOVE_TO 3.0 mm           dt=   0.01s  pos=3.0     <- 0 mm, correct no-op
  MOVE_TO 1.0 mm (back)    dt=   1.33s  pos=1.0     <- BACKWARD, moved
  MOVE_TO 0.0 mm (back)    dt=   0.67s  pos=0.0     <- BACKWARD, moved
```

`HOME` returns the identical 26.35 s from both pos 0.0 and pos 3.0 — to the
centisecond, and identical to the four attempts measured on the previous rev.
A seek that terminates on a switch varies with starting distance; one that
runs out its step budget does not. The limit switch still never asserts
anywhere in the plunger's travel.

## Getting past the connect refusal

`OpentronsPipette.connect()` refuses to return when the plunger will not home,
so **every** protocol aborts at instrument connect, before any gantry motion.
To run the protocol as asked, `cubos/patches/pipette-connect-tolerate-failed-home.patch`
was applied to `~/CubOS` on the Pi (it was written and committed on the
previous rev but deliberately left unapplied). It downgrades the refusal to a
warning and continues with an unreferenced plunger.

Revert with:

```bash
cd ~/CubOS && git apply -R ~/byu-vcl/cubos/patches/pipette-connect-tolerate-failed-home.patch
```

The patch is inert once the switch works — it only fires on a failed home.

Side effect worth knowing: the exception is raised inside `self.home()`, before
`self.prime()`, so **`prime` never ran** this session. The plunger therefore
started the protocol at firmware counter 0 rather than the usual 5.0.

## The plunger trace

Every `OpentronsPipette._send_command` call was timed by
`cubos/tools/run_with_plunger_trace.py` (pass-through, behaviour unchanged).
Motion on this firmware costs a very consistent ~0.665 s/mm, so a round trip
that does not scale with the commanded distance did not move.

| step | command | counter move | dt | s/mm | moved? |
|---|---|---|---|---|---|
| `connect()` | `STATUS` | — | 0.007 s | — | — |
| `connect()` | `HOME` | — | 26.348 s | — | **no** (switch never asserts) |
| `connect()` | `HOME` (retry) | — | 26.346 s | — | **no** |
| `pick_up_tip` | `MOVE_TO 0.0` | 0.00 mm | 0.006 s | — | correct no-op (already at 0) |
| `aspirate` | `ASPIRATE 0.5` | 0 → 35.45 | 6.671 s | — | **YES** |
| `blowout` | `MOVE_TO 7.0` | 35.45 → 7.0, **−28.45 mm** | 18.862 s | 0.663 | **YES — a retraction** |
| `drop_tip` | `MOVE_TO 10.0` | 7.0 → 10.0, +3.00 mm | 1.997 s | 0.666 | **YES** |
| `drop_tip` | `MOVE_TO 5.0` | 10.0 → 5.0, **−5.00 mm** | 3.322 s | 0.664 | **YES — a retraction** |

All four `MOVE_TO` commands scaled at 0.663–0.666 s/mm, two of them backwards.
Compare the same two commands on the previous rev, which returned a flat
~0.11 s regardless of distance and did not move.

## Open: `ASPIRATE`'s counter is not `MOVE_TO`'s counter

`ASPIRATE 0.5` reported landing at **35.45** — 71× its argument, and the third
different value observed for the same command (36.00 twice on 2026-08-31 and
2026-09-01a, 11.22 with `speed=50`). `MOVE_TO` then treats 35.45 as the current
position and travels `|35.45 − 7.0| = 28.45 mm`, which the 18.862 s round trip
confirms it physically did at the `MOVE_TO` rate.

Whether that retraction is matched to the aspirate's real advance depends on
`ASPIRATE`'s travel rate, which is not the `MOVE_TO` rate and is not
characterised:

* if `ASPIRATE` advanced the full 35.45 mm in 6.671 s (0.19 s/mm), the blowout
  retraction is matched and the plunger ended near its start;
* if it advanced at the `MOVE_TO` rate, it moved ~10 mm and the blowout
  retracted ~18 mm **past** the starting point, into the retracted stop,
  skipping steps for the rest of that 18.9 s move.

This is now the largest unknown in the plunger path, and it only became
observable once retraction started working. Watching the plunger during a run
distinguishes the two directly.

## Gantry — commanded Z planes, from the run's own G-code

```
  8 x  Z99.065    capper transit / park       (safe_z 115 + depth -15.935)
  8 x  Z124.0     tipped hover, CLAMPED by the hover-clamp patch
  4 x  Z54.065    capper engage               (rim 55 + engage_depth 15)
  2 x  Z55.0      aspirate / blowout          (tip end deck 20, nozzle at rim)
  1 x  Z92.0      drop_tip
  1 x  Z84.065    step 1, capper park at travel_z 100
  1 x  Z57.0      pick_up_tip
  1 x  Z122.0     step 5, pipette_park at travel_z 87
  1 x  Z115.0     bare-nozzle hover at safe_z
```

Distinct X: 154.0 (vial column in the pipette frame, 206 − 52), 206.0 (capper
over the vials), 236.0 (capper park), 284.0 (tip rack). Exactly the predicted
geometry.

## Offline gates (the Pi's exact CubOS: `cbc33dc` + all four patches)

```
validate_setup                PASS — 12 steps
run_protocol --mock           12/12
passive_shadow                0 interferences  (28 poses, 36 obstacles)
passive_shadow --tip-stuck    0 interferences
```

Controller read live before the run — matches the gantry file exactly:

```
$20=1  $21=0  $22=1  $23=0  $27=3.000  $100=$101=$102=400.000
$130=409.000  $131=309.000  $132=124.000
<Alarm|WPos:409.000,309.000,124.000|WCO:-409.000,-309.000,-124.000>
```

## Machine state after the run

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | both returned to vials 1–2 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home before the next run. |
| Plunger | `OK:{"homed":0,"pos":0.00,...}` — counter reset by the port-open board reset; **physical position unknown** |
| `~/CubOS` | `cbc33dc` + all four patches (hover-clamp and connect-tolerate both applied) |

## Still open

* **The plunger limit switch never asserts.** Same 26.35 s failure from any
  starting position, unchanged by the rewiring. Until it works, the connect
  patch must stay applied and no commanded volume is a volume.
* The firmware reports `max_vol: 300.00` while the pipette on the head is a
  p20 — the firmware is configured for a different pipette. Every p20 constant
  in `instruments/pipette/models.py` is marked `# placeholder`, so
  `volume_ul: 20.0` is 0.5 mm of commanded plunger either way.
* `drop_tip` still releases the tip 35 mm above the slot: it descends the *tip
  end* to the rack's `location.z` 57, while a seated tip's end sits at deck 22.
  Needs a `tip_disposal` deck entry and a measured `drop_tip_position`.
* `pickup_z: 57` is still unverified by jog. XY is proven (the run commanded
  `pick_up_tip` to gantry (284.0, 25.5, 57.0), Ben's measured point).

## Files

| file | what |
|---|---|
| `run_hardware.log` | the full hardware run |
| `plunger_trace.json` | every plunger command with timings |
| `gantry_command.log` | this run's G-code block |
| `bench_move.log` | the pre-run bench check (direction + homing) |
| `validate.log`, `mock.log` | offline gates |
| `shadow_nominal.log`, `shadow_tipstuck.log` | passive-instrument sweeps |

Campaign CSVs: `cubos/results/campaign_69_20260901_190152/`.
