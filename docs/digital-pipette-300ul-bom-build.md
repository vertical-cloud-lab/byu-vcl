# Digital Pipette (v2) redesigned down to 300 µL — BOM & build guide

A bill of materials and build guide for the Acceleration Consortium **Digital Pipette**, **rescaled
from its stock milliliter range down to a ~300 µL, disposable-tip, OT-2-P300-class head** for the
**CubXL** gantry.

> **Sources.** v1 (public CAD + firmware): [`ac-rad/digital-pipette`](https://github.com/ac-rad/digital-pipette)
> (CC-BY-4.0 hardware / MIT firmware), paper [10.1039/D3DD00115F](https://doi.org/10.1039/D3DD00115F).
> v2 (air-displacement + robotic tip exchange, ~$270, validated **0.2–10 mL** with BRAND 1–10 mL
> tips): [10.1039/D5DD00336A](https://doi.org/10.1039/D5DD00336A).
>
> **Important:** as published, **both versions are milliliter-scale.** The public repo CAD
> (`platform.stl`, `holder.stl`, `cover.stl`) is built around a **10 mL NORM-JECT syringe**. There
> is no released 300 µL variant — this document specifies the redesign, with the geometry math to
> pick the syringe and confirm resolution.

## Why it needs a redesign, in one paragraph

The Digital Pipette is a **linear actuator pushing a syringe plunger**. Volume per unit stroke is
fixed by the **syringe barrel cross-section**. The stock 10 mL syringe (~15.9 mm bore) moves ~0.5 µL
for every micron of stroke — far too coarse to meter 300 µL accurately. To hit 300 µL you **swap in
a much smaller syringe** (1 mL or 0.5 mL) and reprint the plunger holder + syringe cradle to that
smaller barrel. Everything else (actuator, controller, wiring) carries over. To get disposable-tip,
contamination-free operation like OT-2, run it as an **air-displacement** head (syringe = air
piston) driving a **standard 300 µL tip**, and add a **tip stripper**, which is the essence of the
v2 upgrade.

## The geometry: picking the syringe

Volume displaced `V = A · s`, where `A = π/4 · d²` (barrel bore area) and `s` = plunger stroke.
The actuator is an **Actuonix L16-100-63-6-R**: **100 mm** stroke, 6 V, ~50 N at the 63:1 ratio,
built-in position feedback. Assume a conservative **closed-loop positioning step of ~0.1 mm**.

| Syringe (NORM-JECT) | Bore d | Area A | Stroke for 300 µL | Full-scale volume at 100 mm | Resolution @ 0.1 mm step |
|---|---:|---:|---:|---:|---:|
| **1 mL** | ~4.7 mm | ~17.3 mm² | **~17 mm** | (barrel ≈ 58 mm travel = 1 mL) | ~**1.7 µL** (0.58% of 300 µL) |
| **0.5 mL** | ~3.3 mm | ~8.4 mm² | **~36 mm** | (barrel travel gives ~0.5 mL) | ~**0.84 µL** (0.28% of 300 µL) |
| 10 mL (stock) | ~15.9 mm | ~199 mm² | ~1.5 mm | 10 mL | ~20 µL (6.7%) — too coarse |

**Recommendation: a 1 mL syringe** as the default (300 µL uses a comfortable ~17 mm of the 100 mm
stroke, leaving room for an air gap and blow-out), or a **0.5 mL syringe** if you want finer
resolution and don't need >~450 µL. Both bring per-step resolution below 1% of 300 µL, in reach of
ISO-8655 accuracy after gravimetric calibration. Force is a non-issue: 300 µL air displacement needs
far less than the actuator's ~50 N.

## What changes vs. the stock (v1) design

| Aspect | Stock v1 | 300 µL redesign |
|---|---|---|
| Syringe | NORM-JECT 10 mL | **NORM-JECT 1 mL** (or 0.5 mL) |
| `holder.stl` (plunger holder) | 10 mL plunger tip | **Reprint** to grip the 1 mL plunger |
| `cover.stl` + `platform*.stl` | 10 mL barrel cradle | **Reprint/scale** to the 1 mL barrel OD & flange |
| Front end | Luer syringe, direct liquid | **Air-displacement**: printed nozzle/cone that a **300 µL disposable tip** press-fits onto, air-coupled to the syringe (short tubing or direct Luer) |
| Tip removal | none (v1) | **Fixed stripper collar** the nozzle retracts through (v2-style robotic tip exchange) |
| Calibration | steps↔mm↔mL for 10 mL | Re-derive steps↔µL for the new bore (see below) |

The Fusion 360 sources (`design/f3d/*.f3d`) are the right place to make these edits — the barrel
pocket in `platform`/`cover` and the plunger cup in `holder` are parametric to the syringe you drop
in.

## Bill of materials

### A. Actuation & control (carries over from v1)

| Item | Qty | Spec | ~Cost |
|---|---:|---|---:|
| **Actuonix L16-100-63-6-R** linear actuator | 1 | 100 mm stroke, 6 V, position feedback — [actuonix.com](https://www.actuonix.com/l16-100-63-6-r) | $70–100 |
| DC 6 V actuator power supply | 1 | Actuonix DC PSU or any 6 V supply | $15–25 |
| Microcontroller | 1 | Arduino Uno (stock) / Pi Pico / ESP32; runs `pipette.ino` | $10–25 |
| Breadboard/PCB, jumper + alligator wires, solder | set | Basic circuit build | $10 |
| M3 screws & nuts | 3× M3-10 mm, 1× M3-20 mm | Per v1 BOM | $3 |

> On the CubXL you can drive the actuator from your existing controller instead of a dedicated
> Arduino; the L16-R takes a simple position command (PWM/analog with the -R feedback line, or via
> the Actuonix control approach in `pipette.ino`).

### B. Metering front end (the 300 µL change)

| Item | Qty | Spec | ~Cost |
|---|---:|---|---:|
| **NORM-JECT 1 mL** Luer syringe (default) | 1+ | ~4.7 mm bore; 0.5 mL optional for finer resolution | ~$1 ea |
| Reprinted `holder.stl` (plunger cup, 1 mL) | 1 | Scaled to 1 mL plunger | filament |
| Reprinted `cover.stl` + `platform*.stl` (1 mL cradle) | set | Scaled to 1 mL barrel | filament |
| Printed **tip nozzle/cone** for 300 µL tips | 1 | Air-displacement front end; press-fit for universal 300 µL tips | filament |
| Silicone/PTFE tubing (if syringe is remote-mounted) | short | Air-couple syringe → nozzle | $3 |
| **300 µL disposable tips** + rack | 1 box | Universal-fit / Opentrons-style | $10–30 |

### C. Tip exchange (v2 capability)

| Item | Qty | Spec | ~Cost |
|---|---:|---|---:|
| Printed **fixed stripper plate/collar** | 1 | Bracket the nozzle retracts up through to shear off the used tip (North/N9-style, no extra motor) | filament |
| (Alt.) motorized ejector | 1 | Only if you want active eject instead of a passive stripper | $10–20 |

**Redesign total: ≈ $110–170** (actuator dominates), well inside the $100–300 target.

## Build steps

1. **Choose the syringe** (1 mL default) and **edit the CAD** (`design/f3d/holder.f3d`,
   `platform*.f3d`, `cover.f3d`) so the plunger cup and barrel cradle match its dimensions. Export
   new STLs.
2. **Print** the resized holder, platform, cover, plus the **tip nozzle** and the **stripper plate**
   (PETG/ABS for durability).
3. **Set the actuator zero.** Before assembly, use the microcontroller + `pipette.ino` to drive the
   L16 to a known reference and confirm the 100 mm stroke, exactly as in the v1 instructions.
4. **Assemble** per the v1 guide: plunger holder → actuator (short M3), actuator → platform (M3
   long + shipped brackets), syringe seated between platform and cover, plunger cup on the syringe
   plunger.
5. **Fit the front end.** Air-couple the syringe outlet to the printed nozzle (direct Luer or short
   tubing). Press a 300 µL tip onto the nozzle and verify a sealed air path.
6. **Mount to the CubXL carriage** and position the **stripper plate** at a fixed point so the
   nozzle can retract up through it to eject a tip; the tip rack goes within XY reach for pickup.
7. **Wire** the actuator to your controller (or the stock Arduino circuit — remember to tie
   Arduino GND and the 6 V supply GND together, per the v1 README).
8. **Calibrate gravimetrically.** Command increments of stroke, weigh dispensed water (ρ≈1 g/mL),
   and fit **steps→µL** for the new bore. Target ISO-8655-2 tolerances at 300 µL; expect ~1.7 µL
   theoretical resolution with a 1 mL syringe at 0.1 mm steps, better with 0.5 mL.
9. **Validate** across the working range (e.g. 50/150/300 µL): report systematic error and CV like
   the v2 paper (which reported −0.49% to −0.10% error / 0.10–0.58% CV at its mL scale).

## Open risks / notes

- **Resolution vs. accuracy.** The L16's real closed-loop repeatability may be coarser than the
  assumed 0.1 mm; if 300 µL accuracy misses ISO-8655, step down to the **0.5 mL** syringe or a
  higher-gear-ratio actuator (finer µm/step) at the cost of speed.
- **Air-displacement dead volume.** Keep the tubing between syringe and tip short and rigid;
  compliant/large air volumes degrade accuracy and add lag.
- **This is a redesign, not a reprint.** Unlike FINDUS (which uses a commercial pipette off the
  shelf), the accuracy here must be **re-established by your own calibration** — budget time for the
  gravimetric validation loop. The upside is a fully open, ~$150, Jubilee-ready head with disposable
  300 µL tips.

## Sources

- Digital Pipette v1 (CAD/firmware): [`ac-rad/digital-pipette`](https://github.com/ac-rad/digital-pipette);
  paper [10.1039/D3DD00115F](https://doi.org/10.1039/D3DD00115F)
- Digital Pipette v2 (air-displacement + tip exchange, ~$270): [10.1039/D5DD00336A](https://doi.org/10.1039/D5DD00336A)
- Actuator: [Actuonix L16-100-63-6-R](https://www.actuonix.com/l16-100-63-6-r)
- Syringe bore dimensions: NORM-JECT / Air-Tite Luer syringe datasheets
- Jubilee integration precedent: Pelkie et al. 2025, [10.26434/chemrxiv-2025-zhkrf](https://doi.org/10.26434/chemrxiv-2025-zhkrf)
