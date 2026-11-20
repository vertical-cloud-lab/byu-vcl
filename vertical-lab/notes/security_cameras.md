# Security cameras instead of the Pi HQ/Wide units (#303)

**Work in progress.** The candidates, the bill of materials and the figures are being filled in; the bay geometry
below is computed (`security_cams.py`).

Sterling (PR #318, 2026-11-20): "Considering a swap to mostly or all security cameras (with lots of adjustability in
terms of angle, resolution, night vision, onboard temperature/humidity logging, etc.) with a Pi 5 handling the
streaming and control (similar to borysgroup/aurora-cloud-infra PR 35, but doesn't have to be that brand, and I also
need an approximate cost here)".

## The bay, measured

- **A roof at the opening's clear height leaves 95.5 mm.** The presented tray's floor is at 857 mm; Kardex's goods
  envelope with its 20 mm clearance tops out at 1733.5 mm (the 996 mm opening's 856.5 mm product height is itself an
  estimate, `vlm.py`); the header's underside, where the bay's side walls and the LED light stop, is at 1829 mm. A
  camera hung from a roof there, anywhere over the tray, has 95.5 mm before it is in the way of the tallest goods.
- **The front strip is free of goods.** A tray slides in from the shaft and stops with its front edge at y = -1462 mm,
  so the 110 mm strip from there to the front of the LED light (y = -1572 mm) is never swept by anything on a tray. A
  taller camera (a PTZ) can hang there, limited only by the arm and the operator.
- **The UR10e's clearance** (`services.bay_arm_clearance`'s 320 poses, the arm as 75 mm capsules): a 180 mm-tall PTZ
  in the middle of the front strip comes within 17 mm of the arm (x = 0) or 31 mm (x = 170 mm), whose elbow rises to
  1.56-1.57 m reaching the tray's front half. At x = 450 / 650 mm a wide turret and a PTZ side by side keep 171 / 137 mm.
  A turret on the roof at the middle back keeps 281 mm, one over the tray's centre 236 mm.

## On the trays

- **Cameras set the slot height on seven of the twelve powered trays** (A, C, E, F, G, I, L: `setup_lab.py fit`,
  `out/tray_plan.json`). If every camera sat at or below its tray's tallest instrument, those slots could shrink by
  425 mm in all (A 50, C 75, F 50, G 125, I 25, L 100). A security camera on the same post at the same aim point
  must keep its top within each tray's headroom (2-25 mm on those seven) or the slot grows by a 25 mm step.
