# Deep-press pickup — 2026-07-28 second session ("pick it up much more")

Follow-up to the morning session after @timothy-commins, watching live, posted
"stop. you need to pick it up much more. then continue." Driven over the
tailnet (RPi-5 → USB-Ethernet → OT-2 HTTP API) with side-view camera frames
between every move.

## What was wrong

The prior session (maintenance run started 19:42 UTC) pressed to z = 90.5 —
the "full press" depth from the earlier 2026-07-28 test — but the camera
showed the P300 nozzle **hanging in mid-air above the crown, never touching
it** (`00_stalled_session_nozzle_never_inserted.jpg`). Its lift/carry moved a
bare nozzle. The Z frame had shifted versus the morning numbers (fresh
calibration below puts the crown mouth at ≈ 97.5, and a real grip needed
z = 86, i.e. ~4.5 mm *below* the old "full press"), so the old absolute
Z was no longer meaningful. Lesson repeated from the addendum: **verify
insertion on camera before trusting any press depth.**

## What this session did

Took over the robot (the stale run was already gone), homed for a clean Z
reference, re-calibrated image scale with a known 20 mm move (≈ 4.35 px/mm),
then camera-stepped the descent at (x = 171, y = 227):

| step | z (mm) | observation |
|---|---|---|
| approach | 120 → 100 | tip closes on crown; mouth measured at ≈ 97.5 |
| insert | 95 | tip disappears into bore, white rim both sides |
| press | 88 → **86** | **~11.5 mm engagement**, housing never shifts |
| lift | 110 | **grip confirmed** — upper module rises off its base |
| high lift | **170** | housing dangles mid-air, ~84 mm above the seat |
| carry | x 205 → 171 | ±34 mm X travel, still gripped |
| reseat | 95 → 86.5 | module lands back on its base |
| eject | `dropTipInPlace` | clean release, bare nozzle on lift to 150 |
| home | — | deck restored |

## Working numbers (this session's frame, left-mount P300, no offset cal)

| quantity | value |
|---|---|
| Crown axis X / Y | 171.0 / 227.0 mm |
| Crown mouth Z | ≈ 97.5 mm |
| Deep-press Z | **86.0 mm (~11.5 mm engagement)** |
| High-lift Z | 170.0 mm |
| Eject | `dropTipInPlace` at z = 86.5, worked at 11.5 mm engagement |

Notably, **ejection still works at ~11.5 mm engagement** (deeper than the
9 mm previously thought to be near the safe limit), so the deeper press both
grips reliably and remains robot-releasable.

## Frames

1. `00_stalled_session_nozzle_never_inserted.jpg` — the state Tim saw: nozzle
   hovering above the crown at the stale "press" height.
2. `01_rehomed_above_crown_z120.jpg` — after takeover + home.
3. `02_scale_cal_z100_tip_at_mouth.jpg` — scale calibration; tip ~2 mm above mouth.
4. `03_inserted_z95.jpg` — insertion verified (tip swallowed, rim both sides).
5. `04_press_z88.jpg` / `05_deep_press_z86_11p5mm.jpg` — the deep press.
6. `06_grip_confirmed_lift_z110.jpg` — module rises off its base.
7. `07_high_lift_z170_midair.jpg` — **confirmation shot**, housing high in mid-air.
8. `08_carry_x205_still_gripped.jpg` — sideways carry.
9. `09_reseated_z86p5.jpg` — reseated on its base.
10. `10_ejected_bare_nozzle_z150.jpg` — after eject, housing back in slot 8.
11. `11_homed.jpg` — final state.
