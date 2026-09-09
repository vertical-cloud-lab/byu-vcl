# pipette_test on the CubXL — 2026-09-01, campaign 54

**18/18 steps, `completed`, 18:17:41 → 18:23:31 UTC (5 m 50 s).** No capper
retries, no alarms, no warnings beyond the routine "GRBL is in Alarm state
after connect" pair.

Run at @benwhitney5463's request on PR #171 with the trio he attached that
day. All three files are committed exactly as run:

| | |
|---|---|
| gantry | [`cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml`](../../configs/gantry/cub_xl_ben_pipette_capper.yaml) — parsed-identical to the branch, no edit needed |
| deck | [`cubos/configs/deck/ben_6vials_tiprack.yaml`](../../configs/deck/ben_6vials_tiprack.yaml) — tip-rack anchor moved back to a1.x 336.0 |
| protocol | [`cubos/configs/protocol/vcl/pipette_test.yaml`](../../configs/protocol/vcl/pipette_test.yaml) — `pipette_park` Z and `travel_z` 100 → 87 |

---

## 1. The plunger: the one-way fault survived the rewiring

@benwhitney5463 redid the pipette wiring before this run. It did not change
the behaviour. Bench-checked before sending anything to the gantry
([`bench_move.log`](bench_move.log)):

```
  HOME (cold)              dt=   0.52s  pos=0.0 homed=1
  MOVE_TO 1.0 mm           dt=   0.68s  pos=1.0
  MOVE_TO 3.0 mm           dt=   1.35s  pos=3.0
  HOME (from 3.0)          dt=   0.52s  pos=0.0
  MOVE_TO 3.0 mm           dt=   2.02s  pos=3.0
  MOVE_TO 1.0 mm (back)    dt=   0.11s  pos=3.0    <- did not move
  MOVE_TO 0.0 mm (back)    dt=   0.11s  pos=3.0    <- did not move
```

Motion costs a very consistent **0.673 s/mm** (0.68/1, 1.35/2, 2.02/3), so a
round trip that does not scale with the commanded distance did not move the
plunger. Forward scales; backward is flat at ~0.11 s. Identical to the
2026-08-31 measurement.

`HOME` returning in 0.52 s from pos 3.0 is also unchanged: retracting 3 mm
cannot cost less than 2.0 s, so `HOME` is zeroing the counter, not seeking the
endstop. There is no recovery path in the command set.

### What that did to each protocol step

Every plunger command was timed during the run itself by wrapping
`OpentronsPipette._send_command` (pass-through, behaviour unchanged). Raw
records in [`plunger_trace.json`](plunger_trace.json); the `@@PLUNGER` lines
in [`run_hardware.log`](run_hardware.log) are the same data inline.

| step | command sent | dt | reply | moved? |
|---|---|---|---|---|
| `connect()` | `STATUS` | 0.007 s | `homed:0, pos:0.00, max_vol:300.00` | — |
| `connect()` | `HOME` | 0.520 s | `Pipette homed` | **no** — counter zeroed |
| `connect()` prime | `MOVE_TO 5.0` | 3.355 s | `v:[5.00]` | **yes** — 5 mm × 0.671 s/mm |
| `pick_up_tip` | `MOVE_TO 0.0` | 0.107 s | `Pipette moved` | **no** |
| `aspirate` | `ASPIRATE 0.5` | 5.963 s | `v:[0.50, 36.00]` | **yes** |
| `blowout` | `MOVE_TO 7.0` | 0.108 s | `v:[7.00]` | **no** |
| `drop_tip` | `MOVE_TO 10.0` | 0.109 s | `v:[10.00]` | **no** |
| `drop_tip` | `MOVE_TO 5.0` | 0.110 s | `v:[5.00]` | **no** |

Two motions in the whole run: the prime at connect and the aspirate in
vial_1. Everything else was a retraction, and retractions are no-ops.

The `v:[...]` echo proves the arguments are parsed and accepted — the firmware
*decides* not to move rather than failing to. Combined with `HOME`'s flat
0.52 s from any position, that points at the DIR line to the driver or a
`target > pos` guard / unsigned step count in the retract path, not at CubOS,
not at the serial link, and not at the shared `/dev/ttyACM0`.

### `ASPIRATE` does not honour its argument

`ASPIRATE 0.5` (= 20 µL × `mm_to_ul` 0.025) ran for 5.963 s ≈ **8.9 mm** of
travel and the firmware reported the plunger at **36.00**. Commanded 0.5,
delivered ~9, reported 36 — three different numbers. Reproduced identically on
2026-08-31 (also ~5.9 s, also 36.00).

Worth knowing when reading the older logs: the firmware's `speed` argument
changes the reported landing position. CubOS sends
`_FIRMWARE_DEFAULT_SPEED = 0.0`, and at 0.0 `ASPIRATE 0.5` reports 36.00. A
probe that sent `speed=50` instead ([`speed_arg_probe.log`](speed_arg_probe.log))
got 11.22 and ran ~18× slower — that log is included only to document the
argument's effect; it is **not** representative of what CubOS does.

### `max_vol: 300.00` vs. a p20

@benwhitney5463 confirmed the mounted pipette is a **p20**, so
`pipette_model: p20_single_gen2` in the gantry YAML is right. The Arduino
firmware still reports `max_vol: 300.00`, i.e. the firmware is configured for
a different pipette than the one on the head.

Separately, every p20 constant in
`instruments/pipette/models.py` is marked `# placeholder`
(`prime 5.0`, `blowout 7.0`, `drop_tip 10.0`, `mm_to_ul 0.025`), so
`volume_ul: 20.0` is 0.5 mm of commanded plunger travel, not 20 µL. Volumes
will not mean microlitres until both the firmware's pipette and those
constants are set from the real p20.

### Accumulated one-way travel — inspect the plunger

Because retraction never works, every forward command is cumulative and
nothing gives it back. Commanded forward travel this session, in order:

| pass | commands that moved | mm |
|---|---|---|
| bench direction test | `MOVE_TO 1.0` (+1), `MOVE_TO 3.0` (+2), `MOVE_TO 3.0` after a counter-zeroing `HOME` (+3) | **+6.0** |
| `speed=50` probe | `MOVE_TO 5.0` (+5), `ASPIRATE 0.5` → 11.22 (+6.22) | **+11.2** |
| the protocol run | prime `MOVE_TO 5.0` (+5), `ASPIRATE 0.5` at 5.963 s ÷ 0.673 s/mm (~+8.9) | **+13.9** |

≈ **31 mm of commanded forward travel**, against a `p20` plunger whose modeled
range is 0–10 mm. (Commanded, not necessarily physical: once the plunger is
against its stop the stepper skips steps rather than advancing, which is the
normal non-destructive failure — but it also means the true position is
unknown.)

The `speed=50` probe was my call and accounts for ~11 mm of that; the bench
test is bounded by design and the run is what was asked for. **The plunger and
its coupling are worth an inspection** before reading anything into the
mechanism.

---

## 2. The gantry: clean, and the geometry is confirmed by measurement

Distinct Z planes commanded, straight from the run's G-code
([`gantry_command.log`](gantry_command.log)):

```
 20 x  G01 Z99.065     capper transit / park   (safe_z 115 + depth -15.935)
 14 x  G01 Z124.0      tipped hover, CLAMPED by the hover-clamp patch
 10 x  G01 Z54.065     capper engage over a vial (rim 55 + engage_depth 15)
  2 x  G01 Z75.0       aspirate / blowout, tip end 15 mm into the vial
  1 x  G01 Z92.0       drop_tip (tip end to the rack's location.z 57)
  1 x  G01 Z84.065     step 1, capper park_position at travel_z 100
  1 x  G01 Z57.0       pick_up_tip
  1 x  G01 Z122.0      step 5, pipette_park at travel_z 87
  1 x  G01 Z115.0      bare-nozzle hover at safe_z
```

X takes only four values: 236 (capper park), 206 (vial column), 284 (tip
rack), 154 (pipette over the vial column, = 206 − `offset_x` 52).

### The tip-rack frame question is settled

`pick_up_tip` commanded gantry **(284.0, 25.5, 57.0)** — exactly
@benwhitney5463's measured jog point. So a1 `(336.0, 37.5)` is already in the
pipette's deck frame (336 = 284 + `offset_x` 52; 37.5 = 25.5 + `offset_y` 12)
and needs no further conversion. The 366 tried on 2026-08-31 would have
commanded gantry X 314.

`validate_setup` passes with either value — it only asks whether a coordinate
is reachable, never whether it is the right one — which is why this had to be
settled by reading the G-code rather than by a gate.

### `safe_z: 115` + `park_position: [236, 175]` is the first fully clean combination

```
passive_shadow                 0 interferences
passive_shadow --tip-stuck     0 interferences
```

Both zero. The `--tip-stuck` column is the one that changed: at `safe_z: 87`
it was 3. `drop_tip` calls `clear_attached_tip_extension()` unconditionally,
so every step after 9 is planned bare-nozzle regardless of what physically
happened — and since the tip demonstrably did **not** come off (the ejector
command was a no-op), that case is the real one, not the hypothetical one.
It collided with nothing.

The two reasons: the capper now transits at gantry 99.065 instead of 71.065,
so a stuck tip's end rides deck 64 instead of 36; and park X 236 is *greater*
than the column X 206, so with the pipette hanging at +52 in X the nozzle
sweeps deck X 288–336 during those legs and never crosses a vial.

### Controller

`$130/$131/$132` = **409.000 / 309.000 / 124.000**, matching the gantry YAML
exactly — the mismatch that would have aborted every run at connect is gone.
`$20=1` (soft limits on), `$21=0`, `$22=1`, `$23=0`. Full dump in
[`grbl_and_arduino_20260901.json`](grbl_and_arduino_20260901.json).

---

## Machine state, left clean

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF` (code 6), `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | all five returned to vials 1–5 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home before the next run. |
| Plunger | counter reset to 0 by the board reset; **physical position unknown** — see the accumulated-travel note |
| Ports | `/dev/ttyUSB0` → gantry · `/dev/ttyACM0` → capper + pipette; both free |
| `~/CubOS` | `cbc33dc` + all three local patches |

## Still open

- **The plunger only turns one way.** Until that is fixed, `blowout` and
  `drop_tip` cannot execute and no tip is ejected.
- **The tip is still on the nozzle** — pull it off by hand. (`passive_shadow
  --tip-stuck` says nothing collides if it is left on, but it will not seat a
  fresh tip.)
- **`pickup_z: 57` is unverified by eye.** The XY is now proven correct, so if
  a tip still does not seat, Z is the only remaining variable. `pick_up_tip`
  is a friction press with no sensor.
- **`drop_tip` still ejects a full tip-length above the slot** (gantry 92 vs.
  a seated tip's end at deck 22). Needs a `tip_disposal` deck entry and a
  measured `drop_tip_position`.
- **No camera on the CubXL deck** — every statement here comes from the
  machine's own sensors and its G-code, not from vision.

## Files

| | |
|---|---|
| [`run_hardware.log`](run_hardware.log) | the hardware run, with the `@@PLUNGER` trace inline |
| [`plunger_trace.json`](plunger_trace.json) | every plunger command, argument, timing and reply |
| [`gantry_command.log`](gantry_command.log) | every G-code line the run emitted |
| [`bench_move.log`](bench_move.log) | the direction test, run before the protocol |
| [`bench_readonly.log`](bench_readonly.log) | post-run plunger status |
| [`speed_arg_probe.log`](speed_arg_probe.log) | the `speed=50` probe — documents the argument's effect, not CubOS behaviour |
| [`validate_setup.log`](validate_setup.log) · [`shadow_nominal.log`](shadow_nominal.log) · [`shadow_tipstuck.log`](shadow_tipstuck.log) | offline gates |
| [`grbl_and_arduino_20260901.json`](grbl_and_arduino_20260901.json) | full `$$` dump + Arduino probes |
| [`../campaign_54_20260901_181741/`](../campaign_54_20260901_181741/) | campaign CSVs |
