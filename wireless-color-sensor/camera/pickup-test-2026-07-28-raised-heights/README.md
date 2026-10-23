# Full cycle with raised heights — 2026-07-28 (pickup ✓, +20 mm carry ✓, 10 mm drop-in ✓)

Requested by @timothy-commins in PR #60: *"stop, put it back. when lifting the
housing unit, you must lift it at least 20mm higher. also when setting it down
drop it from 10 mm higher than where you are currently dropping it. continue"*

State at session start: the robot was **idle** (nothing to stop) and the module
was already **back on its base** — the immediately prior session (see
`/tmp/OT2_STATUS_READ_ME_FIRST.txt` history on the RPi-5, run 30401047053) had
completed a full cycle after Tim's manual reseat and ended with the module
seated and the nozzle bare. This session then re-ran the full cycle with both
new height rules applied. Driven over the tailnet (runner → Tailscale → RPi-5 →
USB-Ethernet → OT-2 HTTP API), camera frame checked between moves.

## Result

| stage | outcome |
|---|---|
| Straight entry at (171.05, 227.0), mouth Z 98.7, entry z=95 | ✓ clean insertion, no housing displacement |
| Press to mouth − 7 (z=91.5) **at pickup** | ✓ gripped — done up front because the new mid-air eject needs ≥ 7 mm hang engagement |
| Lift test z=110 | ✓ module follows the nozzle |
| **High lift z=170** (was 150 → **+20 mm rule**) | ✓ module hanging cleanly |
| Carry x=171→205→171 @ 10 mm/s, 8.5 mm segments | ✓ module aboard the whole round trip at the new height |
| **Eject at z=101.5** (foot ~10 mm above seat → **+10 mm drop rule**; previous sessions ejected while seated) | ✓ `dropTipInPlace` succeeded mid-air; module **dropped ~10 mm into the base pocket and seated upright** |
| Nozzle clear + final | ✓ bare nozzle at z=130; homed; module position matches baseline |

## The two new rules, made permanent

1. **Carry height: z=170** (nozzle) with the module aboard — 20 mm above the
   previous z=150. No detach at 10 mm/s segmented; the prior detach was a
   30 mm/s unsegmented carry at z=150, so speed/segmentation — not the extra
   height — remains the guard that matters.
2. **Set-down: eject with the foot ~10 mm above the seat** (nozzle z=101.5
   here) instead of seating + re-pressing + ejecting. The base's registration
   pocket guides the fall and the module lands upright. **Precondition:** press
   to **mouth − 7** at pickup — the prior session showed `dropTipInPlace`
   fails at 6 mm engagement, and with a mid-air eject there is no seated
   re-press to fall back on, so the hang engagement itself must be ≥ 7 mm.

`protocol_cyclic_housing.py` was updated to match (`TRANSPORT_DZ` 20 → 40,
`DROP_RELEASE_Z` 2 → 12, `tipOverlap` 6 → 7).

## Frames

1. `s2_01_after_home.jpg` — baseline: module seated, crown up, nozzle parked.
2. `s2_02_above_z120.jpg` / `s2_03_z105.jpg` / `s2_04_z101.jpg` — approach
   ladder; tip centred over the crown mouth.
3. `s2_05_entry_z95.jpg` — straight entry, crown rim visible both sides.
4. `s2_06_press_z91p5_mouth_minus_7.jpg` — the eject-capable press.
5. `s2_07_lifttest_z110.jpg` — module rises with the nozzle.
6. `s2_08_highlift_z170.jpg` — hanging at the new +20 mm carry height.
7. `s2_09_carry_x179/188/196/205.jpg` — outbound segments, module aboard.
8. `s2_10_return_x196/188/179/171.jpg` — return segments, module aboard.
9. `s2_11_predrop_z101p5_foot_10mm_up.jpg` — hovering, foot ~10 mm above seat.
10. `s2_12_after_eject.jpg` — separated; module dropped in, crown upright
    under the nozzle.
11. `s2_13_nozzle_clear_z130.jpg` — bare nozzle, module seated below.
12. `s2_14_reseat_check.jpg` / `s2_15_final_homed.jpg` — final state matches
    baseline; gantry homed, maintenance run deleted.

Robot left clean: gantry homed, maintenance run deleted, module seated on its
base in slot 8, nozzle bare. Camera is still mis-aimed from the 2026-07-28
bump (crown region at frame bottom was sufficient for verification) — a
re-aim would restore the full deck view.
