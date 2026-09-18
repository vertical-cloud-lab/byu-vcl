# Full cycle with drop-off x −5 mm (anti-tip) — SUCCESS (2026-07-31)

Requested by @timothy-commins in PR #60: *"note that when dropping the
package in comparison to the last run, drop it -5mm in the x axis. whats
happening is that the enclosure is being tipped when picked up (does not
remain perfectly vertical) and is hitting the base when trying to set it
down."*

Full pick-up → carry → put-back cycle with the **fully loaded module**
(housing + Pico W, sensor board, LiPo + shim — the electronics are visible on
the housing's left face in every frame). The proven 6-for-6 recipe was reused
with **one change**: the drop-off x moved from 168.05 to **163.05 mm**
(−5 mm), per Tim's observation that the module hangs tilted and its foot
strikes the base on set-down.

Driven over the tailnet (runner → Tailscale → RPi-5 → USB-Ethernet → OT-2
HTTP API) in a single maintenance run, with a camera frame checked at every
stage.

## Recipe (only the drop-off x changed)

| stage | coordinates / z |
|---|---|
| Pickup XY | (169.05, 225.0) |
| Descent ladder | z 150 → 120 → 105 → 101 → 99 |
| Straight entry | z = 95 |
| Press (eject-capable) | z = 91.5 (mouth − 7) |
| Lift test | z = 110, + 4 s dwell slip check |
| High lift / carry height | z = 170 |
| Carry | x 169.05 → 205 → **163.05**, 8.5 mm segments @ 10 mm/s |
| **Drop-off XY** | **(163.05, 225.0)** ← was (168.05, 225.0), **−5 mm in x** |
| Pre-drop check stops (new) | z = 108, 101 (frames inspected before committing) |
| Drop-off (eject) Z | 96.5 |
| Post-eject clearance | z = 128 (bare-P300 +Z rule) |

## Result — the module reseated in its pocket

| stage | outcome |
|---|---|
| Descent ladder at (169.05, 225.0) | ✓ tip centred on the crown mouth |
| Straight entry z=95 | ✓ clean insertion, no housing displacement |
| Press to z=91.5 | ✓ gripped |
| Lift test z=110 | ✓ loaded module off its base |
| 4 s dwell | ✓ no slip under full electronics mass |
| High lift z=170 | ✓ hanging — **tilt clearly visible, confirming Tim's diagnosis** |
| Carry x 169.05 → 205 → 163.05 | ✓ module aboard the whole way |
| Staged descent z 108 → 101 → 96.5 at x=163.05 | ✓ no contact with the base at any stop |
| Mid-air eject (`dropTipInPlace`) | ✓ clean release |
| Reseat | ✓ **module standing upright on its base, crown up** |
| Clearance z=128 → home | ✓ no +Z alarm |

### Quantitative check on the landing

Edge positions of the module in the side-on camera, measured on the same
camera pose before and after the cycle (column-gradient peaks in the module's
y-band, px):

| frame | module edges (px) |
|---|---|
| `01_z99_mouth.jpg` (seated, start of run) | 495, 533, 546, 555, 638, 648 |
| `14_final_homed.jpg` (seated, after the cycle) | 496, 533, 547, 557, 639, 649 |

Every feature matches to **1–2 px**, i.e. the module landed back in
essentially its original seated position — see
`15_seated_before_after.png` (left = before, right = after; visually
identical). Static background features (base/gantry edges at 759/783/940 →
760/785/942) confirm the camera did not move between those two frames, so
the match is real and not a camera artefact.

**The −5 mm drop-off offset works.** The tilt Tim described is real and
visible in `06_highlift_z170.jpg` / `07_carry_x205.jpg` — the module does not
hang plumb — and shifting the release point −5 mm in x compensated for it,
so the foot cleared the base and dropped into the pocket instead of catching
its rim.

## Frames

1. `00_camera_bumped_topdown.jpg` — the very first frame of the session: the
   camera was pointing down at the deck (slots 4/5/7), module not in view.
2. `00b_baseline_seated.jpg` — after homing, the camera had settled back to
   the usual side-on pose; module seated, electronics aboard.
3. `01_z99_mouth.jpg` — end of descent ladder, nozzle centred on the crown.
4. `02_entry_z95.jpg` — straight entry.
5. `03_press_z91p5.jpg` — eject-capable press (mouth − 7).
6. `04_lifttest_z110.jpg` — grip confirmed, module off its base, **tilted**.
7. `05_dwell.jpg` — after 4 s hang: no slip.
8. `06_highlift_z170.jpg` — hanging at carry height, tilt visible.
9. `07_carry_x205.jpg` — outbound end of carry, module aboard.
10. `08_return_x163.jpg` — returned over the **new** drop-off x=163.05.
11. `09_predrop_check_z108.jpg` — safety stop 12 mm high, alignment checked.
12. `10_z101.jpg` — second staged stop.
13. `11_predrop_z96p5.jpg` — at the release height, no contact with the base.
14. `12_after_eject.jpg` — released; module settling onto its base.
15. `13_clear_z128.jpg` — bare nozzle clear, module upright on the base.
16. `14_final_homed.jpg` — gantry homed, module seated, crown up.
17. `15_seated_before_after.png` — before/after crop comparison.

## Camera caveat — the mount is being knocked

The camera moved **twice** during this session without anyone touching it:
it started pointing down at the deck (`00_camera_bumped_topdown.jpg`,
inverted and aimed at slots 4/5/7), returned to the side-on pose after the
first home (`00b_baseline_seated.jpg`), and shifted/zoomed once more between
that frame and the descent ladder. From `01_z99_mouth.jpg` onward it stayed
put, which is what makes the before/after edge comparison above valid.

Frames from this session are committed **raw** (no 180° rotation needed —
unlike the 2026-07-30 session, the sensor is currently upright). Anyone using
the live stream at `http://rpi-5-stream-cam-2wp0:8000/stream.mjpg` should
check the orientation before trusting it, and the mount should be secured —
it appears to be within reach of the gantry.

## Robot end state

Clean: gantry homed, maintenance run deleted, module (with electronics)
seated on its base in slot 8, crown up, nozzle bare.

## Suggested next step

The recipe is now **7-for-7** and the drop-off offset is calibrated. The
remaining unknown is whether the −5 mm offset is a *constant* correction or
whether the tilt varies run to run: the module hangs from a socket whose axis
is offset from the body's centre of mass, so the lean direction should be
repeatable, but only repeated cycles will confirm it. This is the change that
unblocks unattended cyclic testing — worth folding the −5 mm into
`protocol_cyclic_housing.py`'s drop coordinates and running a short
multi-cycle batch to check that every cycle reseats.
