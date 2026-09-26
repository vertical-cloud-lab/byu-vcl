# 2026-09-26 (b): new gantry and deck files. The tip rack is converted, and the gantry file matches the controller. The trio still fails validation, on two numbers that are not the tip rack

Asked for: *"here are the new gantry and deck files: please change the tip rack
position on the deck file. I measured these coordinates with the pipette tip
hovering over the a1 spot: x= 265.0 y = 32.665."*

**No motion was commanded**, and nothing was run on the machine. On the Pi the
session did two things:

- read-only checks over SSH: log timestamps, `dmesg` USB events, port holders;
- one GRBL read (`?`, `$$`, `$#`, `$I`). Nothing was written. Opening the port
  resets the board, so it sits in `Alarm` until the next `$H`, which is step 0
  of any protocol. Whether it was homed before the read is not known.

The Arduino was not opened. Every gate below ran on the runner, against CubOS
`496819c` plus the Pi's three patches, rebuilt from `cubos/patches/`. Its
`git diff --stat` is identical to the Pi's (9 files, +154/−22).

| | result |
|---|---|
| tip rack | ✅ a1 **(319.0, 45.664)**. `pick_up_tip` commands gantry **(265.000, 32.665, 57.000)**, the jog reading exactly (§1) |
| gantry file vs controller | ✅ **12 of 12** `grbl_settings` match the live board: 391 / 236.665 / 124, `$20=1` (§2) |
| `validate_setup`, committed trio | ⛔ **FAIL, 8 violations, 2 causes**: the pipette cannot reach vial_1, and step 5's `travel_z: 87` is above the new `z_max: 121` (§3) |
| the same trio with only those two fixed | ✅ PASS · `--mock` 12/12 · `passive_shadow` 0 nominal, 0 tip-stuck (§3.3) |

## 1. The tip rack

The jog display shows raw WPos, which is the capper's frame (offset 0/0). CubOS
commands `gantry = deck − instrument offset`. So a point read with the
**pipette** over it sits, in the deck frame, at *reading + pipette offset*. The
offset here is the new one from Ben's 2026-09-26 gantry file, (54.0, 12.999),
not the old (52, 12).

| | x | y |
|---|---|---|
| jog reading, pipette over A1 | 265.0 | 32.665 |
| + pipette offset | 54.0 | 12.999 |
| **`calibration.a1`** | **319.0** | **45.664** |
| `calibration.a2` (one 8.5 mm column in −X, as in every rev since 2026-08-24) | 310.5 | 45.664 |
| `location` (Ben's +0.5 mm X from a1, kept) | 319.5 | 45.664 |

This was checked through the CubOS loader rather than asserted
(`tiprack_only_trace.log`):

```
Moving OpentronsPipette to (319.000, 45.664, 57.000)  -> gantry (265.000, 32.665, 57.000)   pick_up_tip
Moving OpentronsPipette to (319.000, 45.664, 86.000)  -> gantry (265.000, 32.665, 121.000)  tipped hover, clamped
Moving OpentronsPipette to (319.000, 45.664, 57.000)  -> gantry (265.000, 32.665, 92.000)   drop_tip
```

The tip grid:

- rows advance +Y, so A1 to O1 runs deck y 45.664 to 164.664 (gantry y 32.665 to 151.665);
- column 2 is at gantry x 256.5.

All 30 tips are inside the working volume. Both `passive_shadow` passes on the
pickup/drop alone are clean.

The pickup XY reproduces the jog reading **whatever the offset is**: the offset
is added going in and subtracted coming out. The offset only matters for points
measured with the capper and then visited by the pipette, which here means the
vials.

Unchanged from before:

- `pickup_z: 57` is still unverified by eye.
- `drop_tip` still releases a full tip length above the slot (gantry 92).

## 2. The gantry file matches the controller

**The recalibration happened off the Pi.** The Pi's CubOS logs still end at the
cut run on 2026-09-24. `dmesg` shows the GRBL board's CH340 leaving the Pi's USB
at **00:53:37 UTC** and returning at **01:09:56 UTC**, a few minutes before
Ben's comment. That fits a calibration done from another computer.

Read at 01:17:25 UTC (`grbl_settings_20260926b.json`):

```
<Alarm|WPos:391.000,236.665,124.000|FS:0,0|WCO:-391.000,-236.665,-124.000>
$3=1 $10=0 $20=1 $21=0 $22=1 $23=0 $27=3.000 $100..$102=400.000
$110..$112=5000.000   $130=391.000 $131=236.665 $132=124.000
[G54:-391.000,-236.665,-124.000]
```

All twelve `grbl_settings` in the gantry file match this, checked with CubOS's
own `$`-code mapping (`cubos.gantry.grbl_settings`) at its 0.001 mm tolerance.
So `Gantry._validate_grbl_settings` will pass at connect. `$20=1`, so soft
limits are on. That is worth saying because an interrupted calibration has left
them off twice before.

Changes vs. the previous committed gantry file (2026-09-15; 409 / 309 / 124):

| | was | now |
|---|---|---|
| `max_travel` x / y / z | 409 / 309 / 124 | **391 / 236.665 / 124** |
| `working_volume` max x / y / z | 386.333 / 232 / 124 | **388 / 233.665 / 121** (max travel − the 3 mm pull-off, i.e. the homed pose) |
| capper `depth` | −15.935 | **−17.0** |
| pipette `offset_x` / `offset_y` | 52.0 / 12.0 | **54.0 / 12.999** |
| capper `park_position` | deleted 2026-09-15 | `[236, 25]` again (ignored with a warning at `496819c`; harmless) |
| `cnc.default_feed_rate_mm_min` | 2000.0 | absent from the attachment. **Kept at 2000.0** |

**Why the feed-rate line was kept.** Ben's file descends from his local copy,
not the branch's: it has `park_position` and none of the comments. So the
missing line is an artifact of which copy he edited, not a choice. Without it,
CubOS falls back to `DEFAULT_FEED_RATE = 3000` (`gantry_driver/driver.py`). That
is 1.5× every run to date, and `$110`–`$112` = 5000 would not cap it. To take
the speed-up on purpose, delete the line.

## 3. The trio fails validation, and neither cause is the tip rack

`validate.log`, the committed gantry + deck + `pipette_test.yaml`:

```
pipette -> vial_1.location.safe_z:     gantry (135.0, -12.334, 121.0) violates y_min=0.0
pipette -> vial_1.location.action_z:   gantry (135.0, -12.334, 54.0)  violates y_min=0.0
pipette -> pipette_park.location.target:   gantry (204.0, 12.001, 122.0) violates z_max=121.0
pipette -> pipette_park.location.travel_z: gantry (204.0, 12.001, 122.0) violates z_max=121.0
(+ the same four from the semantics pass)
RESULT: FAIL - 8 violation(s) found
```

### 3.1 vial_1 is outside the pipette's reach

The pipette sits +12.999 mm in Y from the capper. So the lowest deck Y it can
put its nozzle over is 12.999, which is gantry y 0. vial_1 at deck y 0.665 would
need gantry y **−12.334**.

The capper reaches vial_1 fine (gantry y 0.665), so `decap`/`cap vial_1` are
valid. `aspirate: vial_1` is not. vial_2 (gantry y 20.001) is fine.

This is a physical layout question, not a number to edit. Options, cheapest
first:

1. **Move both vials up one seat**, if the holder is still the six-seat one at a
   33 mm pitch. vial_1 is in its lowest-Y seat, near the Y limit, so the free
   seats are all in +Y. Seat 2 is the y 33.0 already measured for vial_2, so
   only seat 3 needs a new jog reading.
2. **Shift the holder at least 12.4 mm in +Y** (say 15 for margin) and re-jog
   both vials.
3. **Keep the layout and change the protocol** so the pipette works only in
   vial_2: aspirate and blow out there.

### 3.2 Step 5's `travel_z: 87` is above the new ceiling

`travel_z` resolves in the moving instrument's frame. With a 35 mm tip on, 87
names gantry 122, and `z_max` is now 121. The hover-clamp patch deliberately
does not rescue an explicit `travel_z`. The fix is **87 → 86** in two places:
`positions.pipette_park` z, and step 5's `travel_z`. 86 = 121 − 35, the same
plane the clamp picks for every tipped engage.

### 3.3 Those are the only two

Both fixes were applied to copies, not to the committed files:

- `whatif_deck_seats2and3.yaml`: option 1, with seat 3 **assumed** at y 66.0 from
  the pitch, not measured;
- `whatif_pipette_test_step5_86.yaml`: the two 86s.

Against the committed gantry file:

```
validate_setup               RESULT: PASS
run_protocol --mock          Protocol complete — 12 steps executed.
passive_shadow               22 poses, 32 deck obstacles: No interference.
passive_shadow --tip-stuck   22 poses, 32 deck obstacles: No interference.
```

`passive_shadow` was run with `--cap-height 15`, the current `engage_depth_mm`.
Its default of 13 dates from when that was 13. The tool itself is not on this
branch; it was taken from `claude/issue-165-20260730-2304`, where it last
changed at `217d175`.

## 4. What the next run would command (what-if trace, `whatif_trace.log`)

| move | gantry | |
|---|---|---|
| capper transit / hover | Z 98.0 | `safe_z` 115 + `depth` −17 |
| capper engage | Z **52.0** | rim 54 + `engage_depth_mm` 15 + `depth` −17 |
| `pick_up_tip` A1 | (265.0, 32.665, 57.0) | the jog reading |
| tipped hover, clamped | Z 121.0 | tip end at deck 86, 17 mm over the cap tops at 69 |
| `aspirate` / `blowout` | Z 54.0 | tip end at deck 19, nozzle level with the rim |
| step 5 `pipette_park` | (204.0, 12.001, 121.0) | with the 86 fix |
| `drop_tip` | Z 92.0 | tip end at `pickup_z` 57 |

**One number to watch on the first decap.** The capper engage is now gantry Z
52.0. Campaign 54 captured on the first attempt at 54.065, and `G54` Z is −124
in both frames. So if the Z switch has not moved, the head now goes **2.065 mm
lower** onto the caps.

That is fine if vial z 54 and `depth` −17 are fresh measurements. The capture
is sensed and retried, and it aborts with the tool retracted.

## Files

| file | what |
|---|---|
| `grbl_settings_20260926b.json` | the read-only controller snapshot: status, `$$`, `$#`, `$I` |
| `validate.log` | the committed trio: FAIL, 8 violations |
| `tiprack_only.yaml` + `tiprack_only_{validate,trace,shadow,shadow_tipstuck}.log` | the new anchor on its own: PASS, 4/4, 0 / 0 |
| `whatif_deck_seats2and3.yaml`, `whatif_pipette_test_step5_86.yaml` | **not configs**: the two fixes, applied to copies |
| `whatif_{validate,trace,shadow,shadow_tipstuck}.log` | PASS, 12/12, 0 / 0 |
| `trace_mock.py` | `run_protocol --mock` with CubOS's per-move trace logger switched on |
