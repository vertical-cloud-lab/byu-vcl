# Housing pickup test — 2026-07-27 (slot 8, camera-guided)

Remote camera-guided pickup attempt of the sensor housing with the P20 GEN2,
driven over the tailnet (RPi-5 → USB-Ethernet → OT-2 HTTP API) with frames
pulled from the RPi-5 overhead-camera MJPEG stream between every move.

## Result

The nozzle was located, aligned, and **fully inserted** into the swap-in
tip's socket (verified visually at three depths), but the mounted tip
**did not grip** — every lift came up bare, including after a
maximum-depth press with the nozzle body seated on the crown.

## Measured position (deck coordinates, left-mount P20 nozzle tip)

| quantity | value |
|---|---|
| Socket axis X | **171.0 mm** |
| Socket axis Y | **233.0 mm** |
| Socket mouth Z | **≈ 113 mm** |
| Full-press Z used | 103.5 mm (~9.5 mm engagement) |

Slot 8 local coordinates of the socket axis: x ≈ 38.5, y ≈ 52.0
(i.e. ~25 mm left and ~9 mm behind slot center — the post is not at the
slot center, so `protocol_cyclic_housing.py` needs `SOCKET_X = 38.5`,
`SOCKET_Y = 52.0`, and the mouth height above deck of ~113 mm, unless the
housing is repositioned with the post at slot center).

## Frames

1. `01_baseline_housing_slot8.jpg` — housing standing in slot 8, green-taped
   swap-in tip holder pointing up.
2. `02_nozzle_at_slot8_center.jpg` — nozzle at nominal slot-8 center
   (196.4, 223.7): visibly ~25 mm right of the post.
3. `03_probe_too_far_back.jpg` — mid-search probe; white crown occluding the
   black nozzle = nozzle behind the post (the occlusion cue used to bisect Y).
4. `04_tip_entering_socket_mouth.jpg` — tapered tip entering the socket mouth
   at z = 113.
5. `05_tip_inserted_7mm.jpg` — tip ~7 mm engaged, spring fingers around it.
6. `06_full_press_seated.jpg` — full press (z = 103.5), nozzle body seated
   against the crown.
7. `07_lift_no_grip.jpg` — lift to z = 150: nozzle bare, housing untouched.

## Interpretation

Insertion is clean with zero housing disturbance, so the failure is the
**press-fit itself**: the tip currently mounted in the holder does not
interference-fit the P20 nozzle (round-1 testing found only the 3.40 mm
slitted bore grips; larger bores slide off, and a worn/spread 3.40 behaves
the same). Swap in the round-1-winning 3.40 mm slitted tip (or a solid
3.40–3.50 mm) and rerun at the coordinates above.
