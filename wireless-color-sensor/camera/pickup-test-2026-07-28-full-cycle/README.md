# Full cycle COMPLETE — 2026-07-28 (pickup ✓, slow carry ✓, reseat ✓, eject ✓)

@timothy-commins reseated the module and asked (PR #60) to skip the blind
descent and reuse the previous session's Z data. This session ran the whole
pick-up → carry → put-back cycle end-to-end for the first time since the
carry-detach failure, driven over the tailnet (runner → Tailscale → RPi-5 →
USB-Ethernet → OT-2 HTTP API) with a camera frame checked between moves.

The overhead camera is still mis-aimed from the 2026-07-28 bump (it mostly
sees the enclosure glass), but the crown region of slot 8 sits in the bottom
of the frame — enough to verify every stage in-image.

## Result

| stage | outcome |
|---|---|
| Straight entry at stored (171.05, 227.0), entry z=95 | ✓ **0.0 px housing drag** (phase correlation) — stored coordinates and stored mouth Z (98.7) reproduced with no re-measurement |
| Press to mouth − 6 (z=92.7) | ✓ gripped |
| Lift test z=110 | ✓ crown + housing rose ~78 px (≈17.2 mm) matching the nozzle's +17.3 mm; base stayed |
| High lift z=140 | ✓ module hanging cleanly |
| Carry x 171.05 → 205 (+34 mm) | ✓ **module aboard the whole way** — 10 mm/s, 8.5 mm segments, frame check each segment |
| Return x 205 → 171.05 | ✓ still aboard |
| Reseat (slow descent to z=92.7) | ✓ module back on base, **0 px offset vs baseline** |
| Eject at 6 mm engagement (z=92.7) | ✗ **failed** — `dropTipInPlace` reported success but the module came back up with the nozzle |
| Re-press to mouth − 7 (z=91.5) + eject | ✓ **clean release**, bare nozzle verified on camera |
| Home / cleanup | ✓ maintenance run deleted, deck restored |

The slow segmented carry directly fixes the previous session's failure: the
same +34 mm leg at 30 mm/s detached the module
(`../pickup-test-2026-07-28-carry-detach/`); at 10 mm/s with the same
mouth − 6 press it survived both directions.

## New finding — minimum engagement for ejection

`dropTipInPlace` at **6 mm engagement did not release** the module (it stayed
wedged and lifted off its base with the nozzle), while the **same command
after re-pressing to 7 mm engagement released cleanly** while seated. Prior
successful ejections ran at ~9 and ~11.5 mm engagement. The P300's ejector
sleeve has a fixed stroke, so at shallow engagement the crown's top rim sits
too far down the nozzle for the sleeve to push it off.

Working rule going forward (updates the engagement-relative rules in
`../pickup-test-2026-07-28-repeat/README.md`):

- **Pick up / carry at mouth − 6 to − 7** (grips, survives a slow carry).
- **Before ejecting, be at ≥ mouth − 7** (7 mm engagement) — re-press onto
  the seated module if the cycle used less.
- Hard floor mouth − 9 unchanged.

Carry rules confirmed by this session: ≤ 10 mm/s laterally, short segments
with a frame between, grip-presence check (white crown at the black nozzle
tip) per segment.

## Session numbers (left-mount P300, uncalibrated, stored-frame Z)

| quantity | value |
|---|---|
| Bore axis X / Y | 171.05 / 227.0 mm (stored; reproduced with 0.0 px entry drag) |
| Mouth Z | 98.7 mm (stored from previous session, per Tim's instruction — not re-measured) |
| Entry / press / eject Z | 95 / 92.7 (mouth − 6) / **91.5 (mouth − 7, minimum that ejects)** |
| Carry | z=140, 10 mm/s, 4 × 8.5 mm segments each way, ±34 mm total |
| Reseat accuracy | 0 px (phase correlation vs pre-pickup baseline at z=105) |

## Frames

1. `01_baseline_before_motion.jpg` — module reseated by Tim, crown post up.
2. `02_above_slot8_z150.jpg` / `03_z120.jpg` / `04_z105.jpg` — descent ladder on stored coordinates.
3. `05_z101_2mm_above_mouth.jpg` — sanity check ~2.3 mm above the stored mouth Z.
4. `06_entry_z95.jpg` — straight entry, nozzle swallowed, 0.0 px housing drag.
5. `07_press_z92p7_mouth_minus_6.jpg` — carry-grade press.
6. `08_lifttest_z110.jpg` — grip confirmed (crown follows nozzle, base stays).
7. `09_highlift_z140.jpg` — module hanging clear of the base.
8. `10_carry_x179p5.jpg` … `13_carry_x205.jpg` — outbound slow carry, module aboard at every check.
9. `14_return_x188.jpg` / `15_return_x171_above_base.jpg` — return legs, still aboard.
10. `16_reseat_descent_z105.jpg` / `17_reseated_z92p7.jpg` — slow reseat onto the base.
11. `18_after_eject_z150.jpg` — **the failed eject**: module back on the nozzle at 6 mm engagement.
12. `19_repress_z91p5_mouth_minus_7.jpg` — recovery re-press while seated.
13. `20_eject_check_z105.jpg` — clean release; bare nozzle, module seated (0 px vs baseline).
14. `21_final_homed.jpg` — gantry homed, deck restored.

Robot left clean: gantry homed, maintenance run deleted, status note updated
in `/tmp/OT2_STATUS_READ_ME_FIRST.txt` on the RPi-5. The camera would still
benefit from a physical re-aim (slot 8 only clips the bottom of the frame).
