# Press 1 mm deeper (z 91.5 → 90.5) — full cycle SUCCEEDS with the wire attached (2026-07-31)

Requested by @timothy-commins in PR #60: *"move -1mm in the z axis. since the
tip fell off I want try and go down enough for it to not fall off"*.

Result: **the full cycle completed, wire attached.** The module was picked up,
survived the high lift to z = 170 that dropped it last time, was carried out to
x = 205 and back, and was released back onto its base. Nozzle bare at the end,
gantry homed, maintenance run deleted.

Two things changed relative to the failed run in
[`pickup-test-2026-07-31-wire-attached`](../pickup-test-2026-07-31-wire-attached/README.md):
the requested **−1 mm on the press**, and — visible in the frames — the **wire
has been re-routed** so it now arcs up and over the gantry and travels with the
head instead of being anchored at deck level. Both changes are in this run, so
this session on its own does not separate their contributions (see "Caveat").

## Recipe (only the two Z values changed)

| stage | this run | previous run |
|---|---|---|
| Pickup XY | (169.05, 225.0) | same |
| Descent ladder | z 150 → 120 → 105 → 101 → 99 | same |
| Straight entry | z = 95 | same |
| **Press** | **z = 90.5** (mouth − 8.2) | z = 91.5 |
| Lift test + 4 s dwell | z = 110 | same |
| High lift / carry height | z = 170 (via 130, 150) | z = 170 (single move) |
| Carry | x 169.05 → 205 → 163.05, 8.5 mm segments @ 10 mm/s | same |
| Drop-off XY | (163.05, 225.0) — the −5 mm anti-tilt offset | same |
| **Drop-off (eject) Z** | **z = 95.5** | z = 96.5 |

The eject Z was lowered by the same 1 mm: with the nozzle 1 mm further into the
socket, the module hangs 1 mm higher on the nozzle, so the nozzle has to descend
1 mm further for the module's foot to reach its base.

## Result — every stage passed

| stage | outcome |
|---|---|
| Descent ladder | ✓ tip centred on the crown mouth (`01_z99_mouth.jpg`) |
| Straight entry z = 95 | ✓ clean insertion, housing not displaced |
| Press to z = 90.5 | ✓ gripped |
| Lift test z = 110 | ✓ module off its base, hanging (`04_lifttest_z110.jpg`) |
| 4 s dwell | ✓ no slip (`05_dwell.jpg`) |
| **High lift z = 110 → 130 → 150 → 170** | ✓ **held — this is the move that failed last time** (`08_highlift_z170.jpg`) |
| Carry x → 205 | ✓ still gripped (`09_carry_x205.jpg`) |
| Return x → 163.05 | ✓ still gripped (`10_return_x163.jpg`) |
| Staged descent to z = 95.5 | ✓ module lowered onto its base (`13_predrop_z95p5.jpg`) |
| Eject | ✓ released cleanly, nozzle bare (`14_after_eject.jpg`, `15_clear_z128.jpg`) |
| **Reseat** | ✓ **module back on its base in slot 8** (`16_final_homed.jpg`) |

## Reseat check, measured

Comparing the pre-run baseline (`00_baseline_homed.jpg`) with the post-cycle
homed frame (`16_final_homed.jpg`), both taken from the same camera pose:

| region | mean abs grey-level difference |
|---|---|
| module | 15.1 |
| gantry pillar (static) | 2.8 |
| right panel (static) | 1.6 |
| base front (static) | 2.2 |

Cross-correlating the module band between the two frames:

* **vertical shift = 0 px** — the module sits at exactly its pre-run height,
  i.e. fully down on its base rather than perched on a lip.
* **horizontal shift = −13 px ≈ 1.7 mm** at the measured image scale
  (≈ 7.75 px/mm from the module's 60 mm side-on span). That is the expected
  lean-and-settle from the −5 mm drop-off offset, the same behaviour recorded
  in the `drop-xminus5` run; the residual module-region difference is mostly
  that offset plus the wire draping differently.

## Caveat — two variables changed, not one

The wire is now routed up and over the gantry with a service loop, so it travels
with the head instead of tethering the module to the deck. That is exactly
suggestion 2 from the previous session's write-up, and it removes the failure
mechanism identified there (a taut tether stripping the module off during the
climb). The press also went 1 mm deeper, which does add engagement.

Both are in this run, so **this session cannot attribute the fix to the −1 mm
alone.** The previous failure was a lateral/moment load from the tether, not an
axial pull-off — the socket had already held the loaded module through a 4 s
static hang at the shallower press — so the wire routing is the more likely
cause of the improvement. If it matters which one did it, re-running at
z = 91.5 with the wire still routed overhead would separate them in one cycle.

## Note on going deeper still

z = 90.5 is 8.2 mm into a nominally 8 mm socket, so the nozzle is at or slightly
past the bottom of the bore. Earlier sessions went as deep as z = 86 (11.5 mm)
and still ejected, so there is headroom, but past the bore bottom extra depth
buys shoulder contact rather than more grip — and every extra millimetre makes
ejection harder, which the FEA already flags as the binding constraint at this
bore size. If more retention is needed, a tighter bore or a strain-relieved wire
anchor is a better lever than more press depth.

## Frames

1. `00_baseline_homed.jpg` — before any motion; module seated on its base in slot 8, electronics aboard, wire attached.
2. `01_z99_mouth.jpg` — end of the descent ladder, tip centred on the crown mouth.
3. `02_entry_z95.jpg` — straight entry.
4. `03_press_z90p5.jpg` — the deeper press (−1 mm).
5. `04_lifttest_z110.jpg` — grip confirmed, module off its base.
6. `05_dwell.jpg` — after the 4 s hang: still gripped.
7. `06_lift_z130.jpg`, `07_lift_z150.jpg`, `08_highlift_z170.jpg` — the staged climb through the height that failed last time; module held at every step.
8. `09_carry_x205.jpg` — outbound carry, module aboard.
9. `10_return_x163.jpg` — back at the drop-off column, still gripped.
10. `11_predrop_z108.jpg`, `12_z101.jpg`, `13_predrop_z95p5.jpg` — staged descent to the 1 mm-lower seat.
11. `14_after_eject.jpg` — released.
12. `15_clear_z128.jpg` — nozzle clear and bare, module on its base.
13. `16_final_homed.jpg` — gantry homed.
14. `17_seated_before_after.png` — side-by-side of the pre-run and post-cycle seated module.

Frames are committed raw from the RPi-5 side-view MJPEG stream
(`http://<rpi-5>:8000/stream.mjpg`); the camera was not moved during the session
(static regions match to < 3 grey levels across the whole run).
