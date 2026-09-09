# `pipette_test.yaml` (shortened rev) — 2026-09-01, second session

Requested on PR #171: *"try it again with this shortened protocol."*

**Not run.** Every offline gate passes and the geometry is sound, but the
plunger cannot be homed, and `OpentronsPipette.connect()` refuses to connect
without a reference. `run_protocol` aborts before step 0, with **no gantry
motion at all**.

The plunger **direction** fault that has blocked `blowout` and `drop_tip`
since 2026-08-31 **is fixed** — see below. The limit switch is the new and
only blocker.

## Files

| file | what it is |
|---|---|
| `bench_readonly.log` | `pipette_bench_check.py`, query-only pass |
| `bench_move.log` | `pipette_bench_check.py --move` — the direction test |
| `connect_attempt.log` | `OpentronsPipette.connect()` driven directly, with per-command timing |
| `validate_setup.log` | PASS, 12 steps |
| `mock.log` | `run_protocol --mock`, 12/12 |
| `coords.log` | every commanded pose, deck-frame tool point |
| `shadow_nominal.log`, `shadow_tipstuck.log` | `passive_shadow`, 0 interferences both |
| `grbl_and_arduino_20260901b.json` | live `$$` dump + Arduino state, read before and after |

## 1. The plunger moves in both directions now

`bench_move.log`. Motion on this firmware costs a very consistent
**0.673 s/mm**, so a round trip that does not scale with the commanded
distance did not move.

```
  MOVE_TO 1.0 mm           dt=   0.67s  pos=1.0     <- forward, 1 mm
  MOVE_TO 3.0 mm           dt=   1.33s  pos=3.0     <- forward, 2 mm
  MOVE_TO 3.0 mm           dt=   0.01s  pos=3.0     <- 0 mm, correctly a no-op
  MOVE_TO 1.0 mm (back)    dt=   1.33s  pos=1.0     <- BACKWARD, 2 mm
  MOVE_TO 0.0 mm (back)    dt=   0.67s  pos=0.0     <- BACKWARD, 1 mm
```

Compare 2026-08-31, where every retraction returned in ~0.11 s with a
well-formed `v:[...]` echo and did not move:

```
  MOVE_TO 1.0 mm (back)    dt=   0.11s  pos=3.0     <- did not move
  MOVE_TO 0.0 mm (back)    dt=   0.11s  pos=3.0     <- did not move
```

Timing now scales with `|distance|` in both directions, and a zero-distance
request correctly costs 0.01 s. Ben's rewiring fixed it.

## 2. `HOME` now fails — the limit switch never asserts

Four attempts today, all identical:

```
  HOME (cold, from pos 0)   dt=  26.35s  reply=ERR:{"error":"Failed to home pipette"}
  HOME (from pos 3.0)       dt=  26.35s  reply=ERR:{"error":"Failed to home pipette"}
```

and through the driver's own path (`connect_attempt.log`), which retries:

```
@@CMD code=10 dt= 26.35s RAISED PipetteCommandError('... ERR:{"error":"Failed to home pipette"}')
INFO OpentronsPipette: Homing fell short of the limit switch; retrying
@@CMD code=10 dt= 26.35s RAISED PipetteCommandError('... ERR:{"error":"Failed to home pipette"}')

CONNECT FAILED in 56.5s: PipetteConnectionError('Plunger home/prime after connect failed: ...')
```

Three things make this specifically a **switch** finding rather than a
generic "homing didn't work":

1. **The driver already expects a short first leg and retries.**
   `opentrons.py` `home()`:

   > *Firmware gives up after ~31 mm of upward travel per attempt, but full
   > plunger travel is 55 mm: a plunger parked low needs a second leg to reach
   > the limit switch.*

   Both legs ran their full budget, so ~62 mm was swept against a 55 mm range.
   Wherever the plunger started, the switch should have been crossed.

2. **The duration does not depend on the starting position.** 26.35 s from
   pos 0 and 26.35 s from pos 3.0, to the centisecond, four times. A seek that
   terminates on a switch varies with distance; a seek that runs out its step
   budget does not.

3. **It inverted.** Before the rewiring `HOME` returned in 0.52 s with
   `OK:{"msg":"Pipette homed"}` from any position — the switch reading as
   *permanently asserted*. It now reads as *permanently un-asserted*. That is
   the signature of the switch input line, not of the motor drive.

Candidate causes, cheapest first:

1. **The limit-switch signal line** — continuity switch → MCU pin, the
   pull-up/pull-down, and NO vs. NC. Swapping normally-open for
   normally-closed inverts exactly this way.
2. **Homing direction.** If the rewiring flipped DIR polarity, `HOME` now
   seeks *away* from the switch and can never reach it, no matter how many
   legs. `MOVE_TO` would be unaffected — its position counter is
   self-consistent either way, which is what we measure. **Distinguishing
   these two needs eyes on the plunger**: `HOME` runs for 26 s, so watch which
   way it travels. Toward the switch and not stopping → cause 1. Away from it
   → cause 2.
3. **The switch is out of the plunger's reach** — if the carriage or coupling
   was reseated during the rewiring.

## 3. Where the protocol stops, and why there is no motion

`run_protocol` connects instruments immediately after validation and
**before** the protocol's own step 0 (`home()` of the gantry) — confirmed in
campaign 54's log, where the plunger `STATUS`/`HOME` lines precede any G-code.
So the failure costs 0 steps and commands nothing to the gantry.

There is no config-level way around it: the gate is
`if not status.is_homed:` on the firmware's own flag, and no gantry-YAML field
influences it.

## 4. The trio itself is clean

Run against the Pi's exact CubOS (`cbc33dc` + all three local patches):

```
validate_setup                PASS — 12 steps
run_protocol --mock           12/12
passive_shadow                0 interferences
passive_shadow --tip-stuck    0 interferences
```

Commanded geometry (`coords.log`, deck-frame tool point → gantry):

```
step 1 capper park, travel_z 100        gantry Z  84.065
capper transit / park at safe_z 115     gantry Z  99.065
capper engage (rim 55 + engage 15)      gantry Z  54.065
bare-nozzle hover at safe_z 115         gantry Z 115.0
pick_up_tip tip_rack.A1                 gantry   (284.0, 25.5, 57.0)
tipped hover, CLAMPED by the patch      gantry Z 124.0
aspirate vial_1 / blowout vial_2        gantry Z  55.0     <- tip end deck 20
step 5 pipette_park, travel_z 87        gantry Z 122.0
drop_tip tip_rack.A1                    gantry Z  92.0
```

### `height: -35.0` clears the vial floor

`height` is an offset from the vial **rim**, and the engage descends the
**tool point** — the tip end, with a tip attached:

```
vial rim (location.z)                deck Z  55.0
+ height                                   -35.0
= tip end                            deck Z  20.0   -> gantry Z 55.0
nozzle (tip end + tip_length 35)     deck Z  55.0   == the rim
```

CubOS documents a vial's `height` as the **outer** height, rim → underside
(`deck/labware/vial.py`), so `height: 83` with the rim at deck 55 puts the
underside at deck **−28**: the tip end has ~45 mm of clearance to the floor.
Gantry Z 55 is nonetheless the deepest pipette pose ever commanded here (the
`-15.0` rev commanded 75).

The number worth eyeballing is the **nozzle**, which ends up at exactly rim
height instead of ~20 mm above it. XY is proven (campaign 54's G-code put
`pick_up_tip` on the measured jog point to the millimetre), so this only
matters if the rim Z is off or a tip fails to seat.

### `park_position` Y 170 → 100

This is the protocol's own named position for step 1, not the capper's
`park_position` in the gantry file (unchanged at `[236, 175]`, which is what
`decap`/`cap` use). Deck (206, 100) is inside vial_3's footprint (centre Y 93,
diameter 28), but the capper tool point rides deck Z 100 there — 30 mm above
the cap tops at deck 70 — and the passive nozzle sits at deck (258, 112),
52 mm clear of the column in X.

## 5. Machine state — untouched

| | |
|---|---|
| Gantry motion | **none commanded** — no homing, no G-code |
| GRBL | `Alarm` (the board resets when the port opens) — re-home before any run |
| `$130/$131/$132` | 409.000 / 309.000 / 124.000 — matches the gantry file exactly |
| `$20` soft limits | `1` |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held |
| Plunger | `OK:{"homed":0,"pos":0.00,"max_vol":300.00}` |
| Ports | `/dev/ttyUSB0` → gantry · `/dev/ttyACM0` → capper + pipette; both free |
| `~/CubOS` | `cbc33dc` + the three existing patches; the new one **not** applied |

`/dev/ttyACM0` re-enumerated at **18:31 UTC**, ~5 minutes after the disconnect
noted at the end of the previous session — consistent with the Arduino being
unplugged for the rewiring and put back.

## 6. Plunger travel this session

Retraction works, so unlike previous sessions this is not cumulative: the
bench test walked +3 mm and gave it all back, ending at the same place. The
four `HOME` attempts each ran ~26 s of seek in the homing direction and are
the one thing worth an eyeball at the plunger and its coupling.

## 7. The escape hatch, written but NOT applied

`cubos/patches/pipette-connect-tolerate-failed-home.patch` turns the connect
refusal into a warning, so a run proceeds with an **unreferenced** plunger.
Verified to apply cleanly to the Pi's tree; deliberately not applied.

It is strictly second-best — the firmware's position counter is meaningless
without a home, so absolute `MOVE_TO` targets land somewhere unknown and
commanded volumes are not volumes. It exists only so motion testing can
continue while the switch is being fixed. What it *would* buy, now that
direction works, is that every plunger command in this protocol actuates
rather than silently no-opping:

| step | command | with the patch |
|---|---|---|
| connect prime | `MOVE_TO 5.0` | +5 mm |
| `pick_up_tip` | `MOVE_TO 0.0` | −5 mm (was a no-op) |
| `aspirate` | `ASPIRATE 0.5` | → firmware pos 36 |
| `blowout` | `MOVE_TO 7.0` | −29 mm (was a no-op) |
| `drop_tip` | `MOVE_TO 10.0`, `5.0` | +3, then −5 (both were no-ops) |

## 8. Unchanged, still open

- The firmware reports `max_vol: 300.00` while the pipette on the head is a
  **p20**. Every p20 constant in `instruments/pipette/models.py` is marked
  `# placeholder` (`prime 5.0`, `blowout 7.0`, `drop_tip 10.0`,
  `mm_to_ul 0.025`), so `volume_ul: 20.0` is 0.5 mm of commanded plunger, not
  20 µL. Volumes will not be microlitres until both are set from the real p20.
- `ASPIRATE 0.5` with CubOS's `speed = 0.0` drives to firmware position 36.00,
  not 0.5 — reproduced identically on 2026-08-31 and unexplained. Not re-tested
  today: it is the largest single plunger move available and the position
  semantics are uncertain, so it was not worth the travel while the plunger has
  no reference.
- `drop_tip` releases the tip 35 mm above the slot; the real fix is a
  `tip_disposal` deck entry plus a measured `drop_tip_position`.
- `pickup_z: 57` has still not been jog-verified.
