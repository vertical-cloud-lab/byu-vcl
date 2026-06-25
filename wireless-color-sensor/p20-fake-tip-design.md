# Press-Fit "Fake Tip" Design for Wireless Color Sensor — OT-2 P20 Pipette

> **CAD implementation:** parametric build123d models of the test array, deck
> plate, modular insert, and a drop-in mock sensor package are in
> [`cad/`](cad/README.md) (STL/STEP/renders + an OT-2 test protocol).
> Measuring the original P300 `Sensor package main enclosure.step` gives a bore
> taper half-angle of **1.78°**, which the CAD adopts for the P20 socket.

## Overview

This document specifies the design approach for a 3D-printed press-fit "fake tip" that allows the OT-2 P20 single-channel GEN2 pipette to pick up, carry, and drop off the wireless color sensor package. The fake tip replaces a real pipette tip with a rigid, reusable 3D-printed socket that friction-fits onto the pipette nozzle and is permanently attached (or integrated) into the top of the sensor package enclosure.

## Design Goals

1. **Reliable press fit** — the fake tip must grip the P20 nozzle firmly enough that the OT-2 can pick up the full sensor package (~30–50 g) without slipping during XY or Z moves.
2. **Repeatable pickup/drop-off** — the fit should allow the OT-2's tip-eject mechanism to reliably release the sensor package at the charging station or parking position.
3. **No air-seal required** — unlike a real tip, no airtight seal is needed; only mechanical retention matters.
4. **Printability** — the part should be printable on a standard FDM printer (e.g., Bambu Lab) in PLA or PETG without supports inside the socket bore.

## P20 GEN2 Nozzle Reference Dimensions

Opentrons does not publicly release precise nozzle drawings. The values below are compiled from third-party tip manufacturers, universal-fit guides, and community caliper measurements. **Verify with calipers on your own P20 GEN2 before finalizing the design.**

| Parameter | Estimated Value | Source |
|---|---|---|
| Nozzle shaft outer diameter (OD) | 3.6–3.8 mm | GenFollower tip specs, GMP Plastic fit guide |
| Nozzle taper (half-angle) | ~2–5° | Industry standard for air-displacement pipettes |
| Nozzle usable length (below plunger housing) | ~8–12 mm | Visual reference from Opentrons product images |
| O-ring present on nozzle | Yes (adds ~0.1–0.2 mm effective OD) | Opentrons GEN2 user guide |

Compatible OT-2 20 µL tip reference dimensions (mount end):

| Parameter | Value |
|---|---|
| Tip collar inner diameter | ~3.8 mm |
| Tip collar outer diameter | ~5.0 mm |
| Tip overall length | ~51 mm |

## Recommended Design Approach

### 1. Socket Geometry

The fake tip is a short, hollow cylinder (the "socket") that slides over the P20 nozzle. Key features:

```
        ┌─────────┐
        │         │  ← optional flange / shoulder
        │  ┌───┐  │     (sits against nozzle housing,
        │  │   │  │      acts as a depth stop)
        │  │   │  │
        │  │ ○ │  │  ← socket bore (tapered ID)
        │  │   │  │     grips the nozzle
        │  │   │  │
        │  └───┘  │
        │         │
        └────┬────┘
             │
     ┌───────┴───────┐
     │  sensor pkg   │  ← top of sensor package enclosure
     │  enclosure    │     (socket is integrated or glued here)
     └───────────────┘
```

- **Socket bore inner diameter (ID):** Start at the nominal nozzle OD and add printer-specific compensation. For a press/interference fit on an FDM printer, target the bore ID to be **0.05–0.15 mm smaller** than the measured nozzle OD.
- **Socket depth:** 8–10 mm — deep enough for a stable grip, shallow enough to allow the eject mechanism to push it off.
- **Slight internal taper:** Match the nozzle cone (~2–3° half-angle) so the socket self-centers and wedges onto the nozzle.
- **Wall thickness:** ≥1.2 mm (3 perimeters at 0.4 mm nozzle width) for structural integrity.
- **Entry chamfer:** 0.5 mm × 45° chamfer at the top of the bore for guided insertion.

### 2. Integration with Sensor Package

Two options, in order of preference:

| Option | Description | Pros | Cons |
|---|---|---|---|
| **A — Integrated** | Socket is part of the sensor package enclosure CAD (single print). | Simplest assembly; strongest bond. | Must reprint enclosure to change socket dimensions. |
| **B — Modular insert** | Socket is a separate small part that press-fits or screws into a recess on the enclosure top. | Easy to iterate socket dimensions without reprinting the whole enclosure. | Requires designing the recess interface; possible play between parts. |

**Recommendation for prototyping:** Use **Option B** so the socket can be iterated independently. Switch to Option A once the final dimensions are locked in.

For the modular insert, design a cylindrical recess (e.g., 8 mm ID × 5 mm deep) in the top of the sensor enclosure. The insert has a matching outer cylinder that press-fits or threads into this recess.

For Option A, the **actual** printed 7.5 mm enclosure (from [issue #33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33#issuecomment-4489837433)) has been recreated parametrically and re-bored with a P20 socket as `real_sensor_package_p20` (see `cad/`), giving a drop-in stand-in whose mass and envelope match the real part for pick/place testing.

### 3. Material Selection

The BYU ME Prototyping Lab (EB 117) has Prusa and Bambu Lab FDM printers and supports a range of filaments. Materials confirmed available at BYU include:

| Material | Available at BYU? | Notes |
|---|---|---|
| **PLA** | ✅ Yes (~$0.10/g) | Rigid, low shrinkage (~0.3%), good for precise interference fits. Good for initial prototyping. |
| **PETG** | ✅ Yes (~$0.10/g) | Slightly more flexible, better layer adhesion, more resistant to cracking from repeated insertion/removal. **Recommended for the fake tip** due to many insertion/removal cycles. |
| **TPU** | ✅ Yes (~$0.14/g) | Flexible; not suitable for a rigid press-fit socket. |
| **Nylon (PA)** | ✅ Yes (~$0.14/g) | High strength, good fatigue resistance, but harder to print accurately at small bore sizes. |
| **ABS/ASA** | ✅ Yes (check with lab) | More heat/impact resistant; needs enclosed printer. Viable alternative to PETG. |
| **Resin (SLA)** | ✅ Yes (Prusa SL1s) | Highest resolution for bore accuracy, but brittle — poor for repeated flex cycles. |

**Recommendation:** Print in **PETG** (black) for the best combination of dimensional accuracy, flex durability, and light-blocking. PLA is acceptable for the initial test array if PETG is not loaded on the printer at the time.

Sources: [BYU HBLL Makerspace](https://lib.byu.edu/services/3d-printers/), [ME Prototyping Lab](https://www.me.byu.edu/me-prototyping-lab), [BYU Prototyping Lab booking](https://byuprojectslab.simplybook.me/v2/)

### 4. Print Orientation and Settings

- **Print the socket vertically** (bore axis = Z axis) for best bore roundness.
- **Layer height:** 0.12–0.20 mm (use 0.12–0.16 mm if your printer supports it for a smoother bore surface; 0.20 mm is acceptable on most standard FDM printers with a 0.4 mm nozzle).
- **No supports** inside the bore.
- **100% infill** for the socket section (or at least 4+ perimeters).
- Enable **hole compensation** in slicer if available (Bambu Studio: "Hole compensation" → +0.1 mm).

## Test Array: Parametric Sizing Strategy

Because the nozzle OD is not precisely known and printer tolerances vary, **print an array of test sockets** with incremental bore IDs. This lets you physically test each one on the P20 and find the optimal fit.

### Recommended Test Matrix

The test pieces are simple cylinders: 8 mm tall, 6 mm OD, with a centered through-bore at the specified ID. Print all on the same plate in one batch.

| Test # | Bore ID (mm) | Expected Fit (if nozzle OD ≈ 3.70 mm) |
|---|---|---|
| 1 | 3.40 | Very tight — may not fit or may crack |
| 2 | 3.45 | Tight interference |
| 3 | 3.50 | Moderate interference |
| 4 | 3.55 | Light interference (likely ideal) |
| 5 | 3.60 | Snug / transition fit |
| 6 | 3.65 | Snug / slight clearance |
| 7 | 3.70 | Slide fit |
| 8 | 3.75 | Loose slide fit |
| 9 | 3.80 | Clearance fit |
| 10 | 3.85 | Loose |

The array spans 3.40–3.85 mm in 0.05 mm increments (10 pieces). This covers any nozzle OD in the 3.6–3.8 mm range plus printer tolerance.

### Evaluation Criteria

For each test piece, record:

1. **Can the socket be pushed onto the nozzle by hand?** (Yes/No)
2. **Does it stay on when the pipette is inverted?** (Yes/No — must be Yes)
3. **Can it hold a ~50 g weight hanging from it without slipping?** (Yes/No — must be Yes)
4. **Can the OT-2 tip-eject mechanism push it off?** (Yes/No — must be Yes)
5. **Does repeated insertion/removal (10+ cycles) cause visible wear or loosening?** (Note any degradation)

The ideal bore ID is the **largest ID that still passes criteria 2 and 3**, while also passing criterion 4.

### Second-Round Refinement

Once the best bore ID from round 1 is identified (e.g., 3.55 mm), print a second array at finer resolution around that value:

| Test # | Bore ID (mm) |
|---|---|
| A | best − 0.04 |
| B | best − 0.02 |
| C | best (repeat) |
| D | best + 0.02 |
| E | best + 0.04 |

Also vary the **wall thickness** (1.0, 1.2, 1.5, 2.0 mm) and **socket depth** (6, 8, 10 mm) to find the combination that gives the best grip without making the part too bulky or hard to eject.

### FEA-guided starting point

A CalculiX fit study over all 10 round-1 bore IDs (see `cad/fea_fit_study.py` and `cad/README.md`) — using a nominal Ø3.70 mm nozzle, the ~50 g package weight, friction retention (μ≈0.30, safety factor 3), an ejectability cap (~20 N grip), and a released-cycle endurance limit (~25 MPa) — recommends a **starting bore ID of ≈3.65 mm**. It is the *smallest* bore that still ejects and stays under the PETG endurance limit (11.5 MPa, unlimited cycles), so it grips hardest (≈2.4× the required pull-off) while remaining ejectable; bores ≤3.60 mm grip well but won't eject, and bores ≥3.70 mm don't grip at the nominal nozzle OD. The study models the as-built **6-finger** socket, which is stiffer overall (≈2× the total grip of a 3-finger socket), so the ejectability cap pushes the winner up one step from the earlier 3-finger estimate (3.60 mm). Center the round-2 sweep on **3.63–3.67 mm in 0.02 mm steps** and update the nozzle OD in the study once it is measured with calipers.

## Detailed Dimensions — Initial Prototype

Based on the research and a conservative starting point, the recommended initial prototype dimensions (to be refined with the test array) are:

```
                    ╔══════════════╗
                    ║   ← 0.5 mm  ║  entry chamfer (45°)
                    ║  ┌────────┐ ║
                    ║  │        │ ║  ← bore ID: 3.55 mm (nominal)
                    ║  │        │ ║     tapered at ~3° half-angle
                    ║  │        │ ║
                    ║  │        │ ║  ← socket depth: 8 mm
                    ║  │        │ ║
                    ║  └────────┘ ║
     ╔══════════════╩══════════════╩══════════════╗
     ║             shoulder/flange                ║
     ║          OD: 8 mm, height: 2 mm            ║
     ╠════════════════════════════════════════════╣
     ║       mounting peg (for enclosure)         ║
     ║  OD: 6 mm, length: 5 mm (press-fit into     ║
     ║  enclosure recess)                          ║
     ╚════════════════════════════════════════════╝
```

| Feature | Dimension |
|---|---|
| Socket bore ID (top, entry) | 3.60 mm |
| Socket bore ID (bottom, narrow end) | 3.50 mm |
| Socket bore taper | ~3° half-angle over 8 mm depth |
| Socket outer diameter | 6.0 mm |
| Socket depth | 8.0 mm |
| Entry chamfer | 0.5 mm × 45° |
| Flange/shoulder OD | 8.0 mm |
| Flange height | 2.0 mm |
| Mounting peg OD | 6.0 mm (to match enclosure recess) |
| Mounting peg length | 5.0 mm |
| Wall thickness (minimum) | 1.2 mm |
| Total height (socket + flange + peg) | 15.0 mm |

## Additional Considerations

### Light Shielding

Since the sensor needs to measure color without interference from ambient light, consider:

- Printing the fake tip and surrounding area in **black filament** to minimize light leakage.
- Adding a thin **skirt or collar** around the bottom of the sensor enclosure that matches the well plate slot geometry, blocking stray light from adjacent wells.

### Sensor Proximity

The original design positions the AS7341 sensor at the bottom of the enclosure. The fake tip geometry should be designed so the **sensor face is as close as possible** to the well plate surface when the pipette is at its lowest Z position. Account for:

- P20 nozzle-to-tip length budget
- OT-2 Z-axis travel limits
- Well plate top surface height on the OT-2 deck

### Vapor Protection

For liquid sensing applications, consider adding a thin, translucent glass or plastic cover slide over the sensor aperture to protect it from solvent vapors.

### Durability and Spring-Finger Slits (PETG)

Since the fake tip will undergo many insertion/removal cycles, PETG is recommended over PLA for its superior fatigue resistance. To further improve durability, add **6 axial spring-finger slits** spaced at 60° around the socket wall. These slits let each finger flex slightly outward during insertion rather than the full bore being forced to deform, dramatically reducing stress per cycle.

**Spring-finger slit dimensions (for PETG, ~6 mm OD socket):**

| Parameter | Value | Rationale |
|---|---|---|
| **Number of slits** | 6 | Evenly spaced at 60° for symmetric grip (one slit per finger) |
| **Slit width** | 0.5 mm | Minimum reliably printable gap on FDM; wide enough to allow flex without fusing shut during printing |
| **Slit depth (length)** | 6 mm | ~75% of the 8 mm socket depth — leaves a 2 mm solid ring at the base for structural integrity |
| **Fillet at slit base** | 0.3 mm radius | Prevents stress concentration / crack initiation at the bottom of each slit |
| **Finger radial wall thickness** | ~1.2 mm | (OD − ID)/2 = (6 − 3.55)/2 ≈ 1.2 mm radial wall — enough to grip without being too stiff; each of the 6 fingers also spans ~2.6 mm circumferentially (π × 6 mm OD / 6 − 0.5 mm slit) |

```
    Top view — socket with 6 spring-finger slits (PETG):

                 slit
                  ↓
            ┌──── │ ────┐
           ╱ f6   │   f1 ╲
     slit→ ┤ f5   ○   f2 ├ ←slit
           ╲ f4   │   f3 ╱
            └──── │ ────┘
                  ↑
                 slit
        (bore ~3.55 at centre ○)

    6 fingers, slits at 0°, 60°, 120°, 180°, 240°, 300°

    Side cross-section:

    ┌──────────┐  ← entry chamfer
    │ ╱      ╲ │
    │╱ finger ╲│  ← slit depth: 6 mm
    │╱        ╲│     (fingers can flex outward)
    │          │
    ├──────────┤  ← solid ring: 2 mm
    │  (base)  │     (no slits here — structural)
    └──────────┘
```

**Why these dimensions work for PETG:**
- **0.5 mm slit width** is the practical minimum for FDM at 0.12–0.20 mm layer heights — narrow enough to maintain grip force, wide enough to actually print as an open gap.
- **6 mm slit depth** gives each finger enough lever arm to flex ~0.1–0.2 mm outward during insertion without exceeding PETG's elastic limit (~3–4% elongation at yield). This keeps the fingers in the elastic regime over hundreds of cycles.
- The **2 mm solid ring** at the base prevents the slits from propagating into the flange/shoulder and keeps the socket structurally sound.
- **Fillets (0.3 mm)** at slit bases are critical — without them, sharp corners act as crack initiators under cyclic loading.

```
    Side cross-section of socket with spring-finger slits:

         ┌─────────┐
         │  ┌───┐  │  ← 0.5 mm entry chamfer
         │  │   │  │
         │  │ ┃ │  │  ← slit runs 6 mm deep
         │  │ ┃ │  │     (finger flexes here)
         │  │ ┃ │  │
         │  │ ╰─│  │  ← 0.3 mm fillet at slit base
         │  │   │  │
         │  └───┘  │  ← 2 mm solid ring (no slit)
         └────┬────┘
              │        ← flange / shoulder
```

## References

- [Acceleration Consortium — Wireless Color Sensor](https://accelerationconsortium.github.io/wireless-color-sensor/)
- [Original CAD files (STEP)](https://github.com/AccelerationConsortium/wireless-color-sensor/tree/main/CAD-File/STEP)
- [GenFollower 20 µL OT-2 compatible tips](https://www.genfollower.com/product/20ul-pipette-tip-for-opentrons/)
- [GMP Plastic — Universal Pipette Tip Fit Guide](https://gmpplastic.com/blogs/useful-articles-on-lab-supplies-faq-section/pipette-tip-fit-guide)
- [Opentrons GEN2 Pipette White Paper](https://opentrons-landing-img.s3.amazonaws.com/pipettes/Opentrons-Master-Pipette-White-Paper.pdf)
- [Opentrons GEN2 Single-Channel Manual](https://insights.opentrons.com/hubfs/Products/Pipettes/GEN2%20Pipette%20Single-Channel%20Manual.pdf)
- [3D Print Tolerance & Fit Guide (utils.com)](https://tolerance-fit-guide.utils.com/)
- [AON3D — Engineering Fits for 3D Printing](https://www.aon3d.com/applications/engineering-fits-how-to-design-for-3d-printed-assemblies/)
