# Y −2 mm full cycle — SUCCESS with the mounted P300 (2026-07-28)

Requested by @timothy-commins in PR #60: *"no, this tip will work perfectly
with this tip. try again"* — overriding the immediately-prior session
(`../pickup-test-2026-07-28-y-minus-2-blocked/`), which refused to press
because it assumed the P300 nozzle could not engage the printed crown.

That refusal was wrong: the `repeat`, `full-cycle`, and `raised-heights`
sessions had **already proven the P300 grips and carries this module**. This
session stopped second-guessing that and ran the requested −2 mm-Y full cycle
end-to-end with the P300 actually gripping the crown. Driven over the tailnet
(runner → Tailscale → RPi-5 → USB-Ethernet → OT-2 HTTP API), camera frame
checked between every move.

## The −2 mm change

Pickup/eject XY moved from the raised-heights **(171.05, 227.0)** to
**(171.05, 225.0)** — Tim's "the pick-up spot is close but not perfect,
try −2 mm in Y". Everything else reused the raised-heights recipe.

## Result — full cycle succeeded

| stage | outcome |
|---|---|
| Descent ladder (171.05, **225.0**), z 150→120→105→101→99 | ✓ tip centred over the crown mouth (mouth ≈ 98.7) |
| Straight entry z=95 | ✓ clean insertion, **no housing displacement** |
| Press to mouth − 7 (z=91.5) | ✓ gripped — the eject-capable press |
| Lift test z=110 | ✓ module rose with the nozzle, off its base |
| High lift z=170 (+20 mm rule) | ✓ module hanging cleanly, clear of base |
| Carry x 171.05 → 205 → 171.05, 8.5 mm segments | ✓ **module aboard the whole round trip** |
| Descend z=101.5 (foot ~10 mm above seat) | ✓ hovering over the base pocket |
| Mid-air eject (`dropTipInPlace`) | ✓ **clean release**, module dropped into the pocket and seated upright |
| Home / cleanup | ✓ final state matches baseline; maintenance run deleted |

The pickup, grip, carry, and mid-air drop-in all reproduced at the −2 mm-Y
position exactly as they did at y=227.0 — the 2 mm shift did not degrade any
stage.

## One incident (recovered)

After the eject, a clearance move to deck **z=150** tripped a smoothie
`Hard limit +Z` alarm and failed. Cause: with the crown released, the
pipette's critical point jumps from the tip end back up to the bare nozzle, so
the same deck Z commands a higher gantry Z than it did tip-on — and z=150
over-travels the +Z limit for the bare P300. It was cleared immediately by
**homing** (no damage, module already reseated). Rule for next time: keep
post-eject bare-nozzle clearance moves at **deck z ≤ ~130**, or just home.

## Robot end state

Clean: gantry homed, maintenance run deleted, module seated on its base in
slot 8, crown up, nozzle bare, deck untouched. Status note updated in
`/tmp/OT2_STATUS_READ_ME_FIRST.txt` on the RPi-5.

## Frames

1. `00_baseline.jpg` — module seated, crown up, nozzle parked.
2. `01_above_z150.jpg` / `02_z120.jpg` / `03_z105.jpg` / `04_z101.jpg` /
   `05_z99_mouth.jpg` — descent ladder at the new y=225.0, tip closing on the mouth.
3. `06_entry_z95.jpg` — straight entry, no housing shift.
4. `07_press_z91p5.jpg` — press to mouth − 7 (eject-capable grip).
5. `08_lifttest_z110.jpg` — grip confirmed, module rises off the base.
6. `09_highlift_z170.jpg` — module hanging cleanly at the +20 mm carry height.
7. `10_carry_x188.jpg` / `11_carry_x205.jpg` — outbound segments, module aboard.
8. `12_return_x188.jpg` / `13_return_x171.jpg` — return segments, still aboard.
9. `14_predrop_z101p5.jpg` — hovering, foot ~10 mm above the seat.
10. `15_after_eject.jpg` — clean release: module dropped in, crown upright, nozzle bare.
11. `16_nozzle_clear_z150.jpg` — frame captured around the failed +Z clearance move.
12. `17_final_homed.jpg` — gantry homed, module seated, matches baseline.

The overhead camera is still mis-aimed from the 2026-07-28 bump (deck viewed
nearly side-on, crown region in the lower frame) — enough to verify every
stage in-image; a physical re-aim would restore the full deck view.
