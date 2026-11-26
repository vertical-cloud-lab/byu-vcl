# Full cycle: pick up → carry → notebook sensor test mid-air → reseat — SUCCESS (2026-08-10)

Requested (again) by @timothy-commins in PR #60: *"pick up, move, run the
following google colab code, post here the results, and then return the
enclosure to its housing"* — the same request whose first attempt
([`../pickup-test-2026-08-10-sensor-read-midair/`](../pickup-test-2026-08-10-sensor-read-midair/))
was interrupted by the RPi-5 outage before the return leg. This session ran
the entire cycle end-to-end without interruption: **the module was picked up,
carried out to x = 205, the Colab notebook's MQTT sensor test ran while it
hung on the nozzle, and it was returned to its slot-8 base.** The
wire-attached recipe is now **8-for-8 on completed reseats.**

## Recipe (proven wire-attached recipe, unchanged)

| stage | value |
|---|---|
| Pickup XY | (169.05, 225.0) |
| Descent ladder | z 170 → 150 → 120 → 105 → 101 → 99 |
| Straight entry | z = 95 (5 mm/s) |
| Press | z = 90.5 (5 mm/s) |
| Lift test | z = 110 + 4 s dwell |
| High lift | z = 130 → 150 → 170 (15 mm/s) |
| Carry | x 169.05 → 205, 8.5 mm segments @ 10 mm/s |
| **Sensor test** | **mid-air at (205, 225, 170)** — notebook R=Y=B=50 + ambient |
| Return carry | x 205 → 163.05, 8.5 mm segments @ 10 mm/s |
| Drop-off XY | (163.05, 225.0) — anti-tilt −6 mm offset |
| Staged descent | z 130 → 110 → 108 → 101 → **95.5** |
| Eject | dropTipInPlace, then clear to z = 128, home |

Driven from the RPi-5 (`ssh` over tailnet → USB-Ethernet →
`http://169.254.51.252:31950` maintenance-run API), one command per step.
Frames were taken with `rpicam-still` this session — the port-8000 MJPEG
stream from earlier sessions was not running after the Pi's reboot, and
single stills avoid leaving a process behind. Same camera, same pose.

## Sensor readings (AS7341 counts, notebook MQTT round-trip)

The Colab notebook (`sensor_file/test_sensor.ipynb` in
AccelerationConsortium/wireless-color-sensor) publishes
`{"command": {"R": 50, "Y": 50, "B": 50}, "experiment_id": ...}` to
`command/picow/test/as7341/read` over HiveMQ and waits for the 8-channel
reply. Four round-trips were run; raw replies are the `sensor_reading_*.json`
files alongside this README.

| channel (nm) | seated baseline (R=Y=B=50) | mid-air carry (R=Y=B=50) | mid-air carry (ambient 0/0/0) | reseated (R=Y=B=50) |
|---|---|---|---|---|
| 410 | 9 | 64 | 75 | 8 |
| 440 | 9 | 230 | 273 | 6 |
| 470 | 17 | 251 | 296 | 14 |
| 510 | 180 | 591 | 671 | 175 |
| 550 | 194 | 834 | 945 | 184 |
| 583 | 73 | 916 | 1063 | 58 |
| 620 | 70 | 936 | 1084 | 51 |
| 670 | 64 | 526 | 610 | 50 |

Observations, consistent with the interrupted first attempt:

1. **Lifting the module ~4–15×'s the signal** — seated, the aperture is
   shaded by the base; at carry height it sees the lab lights directly.
   Counts at (205, 225, 170) are ~35–40 % higher than the first attempt's
   hold at (169.05, 225, 110) — higher and 36 mm further from the gantry
   shadow — reinforcing that **pose dominates raw counts** and any
   colorimetric protocol should fix the read position.
2. **The R/Y/B LED command still has no effect** — mid-air ambient actually
   read slightly *higher* than R=Y=B=50 (a few % — consistent with ambient
   drift between reads, not with an LED contribution). The mixing LED is
   either not fitted or not facing the aperture on this build.
3. **The reseated reading doubles as a reseat check**: counts returned to
   the seated-baseline level (within ~20 %), i.e. the aperture is back in
   its shaded seated pose.

## Reseat check, measured

Comparing `00_baseline_seated.jpg` with `11_final_homed.jpg` (same camera
pose; mean abs grey-level difference):

| region | diff |
|---|---|
| module | 3.9 |
| gantry pillar (static) | 0.9 |
| right panel (static) | 1.5 |
| deck front | 17.4 (the service-loop wire draped differently — visible in frame) |

Module-band vertical cross-correlation: **3 px ≈ 0.4 mm** — fully seated
(the prior successful run measured 0 px vertical with a 1.7 mm horizontal
lean-settle from the same anti-tilt drop offset).

## Frames

1. `00_baseline_seated.jpg` — module seated in slot 8, wire attached; matches the recovery session's end state.
2. `01_homed.jpg` — gantry homed, maintenance run open.
3. `02_z99_mouth.jpg` — descent ladder done, nozzle centred on the crown mouth.
4. `03_entry_z95.jpg` — straight entry.
5. `04_press_z90p5.jpg` — deep press.
6. `05_lifttest_z110_dwell.jpg` — grip confirmed, module hanging after the 4 s dwell.
7. `06_highlift_z170.jpg` — module held through the staged climb.
8. `07_carry_x205.jpg` — carried out; the sensor test ran in this pose.
9. `08_return_x163.jpg` — back over the drop-off column, still gripped.
10. `09_predrop_z95p5.jpg` — staged descent to the eject height.
11. `10_after_eject_z128.jpg` — released; module on its base, nozzle bare and clear.
12. `11_final_homed.jpg` — gantry homed, module reseated, run deleted.

## Robot end state

Clean: module reseated on its slot-8 base (confirmed by camera + the
reseated sensor reading), nozzle bare, gantry homed, maintenance run
deleted, no stale state on the robot.
