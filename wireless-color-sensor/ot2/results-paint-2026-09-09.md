# Colour test with red / blue / yellow acrylic — 2026-09-09

Issue #197. Three vials of acrylic paint diluted in water, placed in slot 7;
the sensor enclosure picked up from its base in slot 10 and carried over them.

Two robot cycles were run, both at `--scan-slot 7 --read-z 128` (the height
confirmed on the previous run to clear the vial tops):

| run | positions | output |
| --- | --- | --- |
| paint run | 3, at 30 mm pitch (the standing recipe) | `xscan-slot7-paint-2026-09-09.json` |
| sweep | 9, at 10 mm pitch, x = 3.88 … 83.88 | `xscan-slot7-sweep-2026-09-09.json` |

The empty-slot run at the same pose, taken on the previous session and never
committed, is recovered here as `xscan-slot7-z128-2026-09-09.json` and is the
reference both runs are normalised against.

## Result: one vial measured, two missed

The AS7341 sees exactly one coloured object along the scan line, centred at
**x ≈ 29 mm**, about 20 mm wide, and its signature is unambiguously **yellow**:
440 nm falls from 4.8% of the total to 2.3% while 583/620 nm rise.

Every other position in the sweep has the same spectral shape as every other —
410 nm at 1.47–1.50%, 440 nm at 4.5–4.8%, 620 nm at 21.5–22.6% — which is the
bare deck under room light. **There is no blue signature and no red signature
anywhere in x = 3.88 … 83.88 mm.**

Sweep, each channel as a share of that position's own total (level removed):

| x (mm) | 410 | 440 | 470 | 510 | 550 | 583 | 620 | 670 | total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.88 | 1.50 | 5.47 | 5.84 | 12.98 | 18.72 | 21.77 | 21.69 | 12.02 | 6316 |
| 13.88 | 1.47 | 4.79 | 5.42 | 12.84 | 18.81 | 21.72 | 22.18 | 12.78 | 5429 |
| **23.88** | 1.38 | **2.27** | **3.38** | 11.66 | 19.86 | 23.41 | 24.14 | 13.89 | 4838 |
| **33.88** | 1.40 | **2.33** | **3.43** | 11.78 | 19.85 | 23.19 | 24.06 | 13.96 | 4572 |
| 43.88 | 1.49 | 4.54 | 5.36 | 12.58 | 18.36 | 21.37 | 22.61 | 13.70 | 5366 |
| 53.88 | 1.49 | 4.63 | 5.41 | 12.56 | 18.33 | 21.44 | 22.57 | 13.57 | 5636 |
| 63.88 | 1.48 | 4.72 | 5.45 | 12.52 | 18.31 | 21.49 | 22.55 | 13.47 | 5894 |
| 73.88 | 1.48 | 4.78 | 5.49 | 12.49 | 18.31 | 21.54 | 22.52 | 13.38 | 6146 |
| 83.88 | 1.49 | 4.83 | 5.52 | 12.45 | 18.27 | 21.58 | 22.52 | 13.34 | 6360 |

The 3-position paint run agrees independently. Ratio against the empty-slot
reading at the same X, same Z:

| position | 410 | 440 | 470 | 510 | 550 | 583 | 620 | 670 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| x = 33.88 | 1.12 | **0.75** | 0.90 | 1.11 | 1.24 | **1.26** | 1.19 | 1.14 |
| x = 63.88 | 0.99 | 0.97 | 0.97 | 0.99 | 0.97 | 0.98 | 1.00 | 1.00 |
| x = 93.88 | 0.93 | 0.93 | 0.93 | 0.96 | 0.95 | 0.92 | 0.92 | 0.92 |

Flat ratios at 63.88 and 93.88 = uniform scaling = nothing in view.

## Why the other two were missed: the rack runs along Y, the scan along X

A scan that varies only X, at fixed y = 225.0, crosses **one** row of the deck.
Finding exactly one vial — 20 mm wide, with 60 mm of bare deck either side —
means the three vials are not spread along X. They are in a line along **Y**,
so the X-scan clips the one that happens to sit at y ≈ 225 and passes in front
of or behind the other two.

To measure all three, either turn the rack 90° so the vials lie along X, or
scan Y instead:

```bash
# vials along X (rack turned): the sweep above already works
python3 run_xscan_test.py --scan-slot 7 --read-z 128 --scan-dx=-60,-50,-40,-30,-20,-10,0,10,20

# vials along Y (rack as it is now): fix X on the vial column, step --scan-dy
#   -- needs a --scan-dy sweep, which run_xscan_test.py does not yet accept
```

`--scan-dy` is currently a single float. Adding a Y sweep is the smaller change
of the two and is the honest next step.

## The module has no controllable illumination

The previous session recommended setting `--rgb` before the paint test. That is
not actionable: **the RGB command is inert.** Seven settings, read with the
module seated, all identical (`led-probe-2026-09-09.json`, `led_probe.py`):

```
R=  0 Y=  0 B=  0   total=439        R=255 Y=  0 B=  0   total=438
R= 32 Y= 32 B= 32   total=439        R=  0 Y=255 B=  0   total=438
R=128 Y=128 B=128   total=437        R=  0 Y=  0 B=255   total=439
R=255 Y=255 B=255   total=439
```

`sensor_read.py` publishes `{"command": {"R":r,"Y":y,"B":b}}` and the board
replies with a reading, so the message is understood — but nothing lights. So
every measurement here is **ambient room light reflected off the sample**, and
raw counts are only comparable against an empty reading at the same X, Y and Z.

## The module came off its base at the end of the sweep

The sweep's reseat confirmation read **15084** where it should have read ~440.
The deck photo taken straight afterwards shows the enclosure lying on the deck
in front of its base, face up in room light — which is what 15084 counts means.
It is intact and still answering over MQTT. The gantry homed clear of it.

The sweep's readings should be treated with suspicion for the same reason. At
x = 63.88 the sweep reads 5894 where the paint run and the empty run both read
~2400, and the deep minimum both of those show at slot centre is absent from
the sweep entirely. A change in the *shape* of the spatial profile, not just its
level, is what a module tilting on the nozzle looks like. The yellow detection
survives this — it is a within-run, level-independent comparison against the
neighbouring positions of the same sweep, and it reproduces the paint run's
independent measurement at the same X — but the sweep's absolute counts do not.

**No further motion should be commanded until the module is back on its base by
hand.** Re-seating it with the robot means pressing the nozzle down at a point
whose position and orientation are unknown.
