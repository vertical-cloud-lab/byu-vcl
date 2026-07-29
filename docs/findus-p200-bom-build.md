# FINDUS P200 pipette subassembly — BOM & build guide

A practical bill of materials and build guide for extracting the **FINDUS pipette arm** (the
motorized "robot thumb" that drives a standard manual **P200 / 20–200 µL** pipette) and mounting it
as a tool on the **CubXL** custom Cartesian gantry.

> **Source of truth.** FINDUS = Barthels et al., *SLAS Technology* 2020, 25(2) 190–199,
> [10.1177/2472630319877374](https://doi.org/10.1177/2472630319877374). All CAD (FreeCAD `.FCStd`
> + meshed `.stl`), firmware, and the Python driver are in
> [`FBarthels/FINDUS`](https://github.com/FBarthels/FINDUS) (GPL-3.0). Numbers below are read
> directly out of that repo — e.g. `source code/findus.py` documents **200 µL = 16 mm plunger
> travel** and the GT2/pulley step math.

## What the subassembly actually is

FINDUS does **not** contain a custom air-displacement head. It holds an **off-the-shelf manual
single-channel pipette** (a P200-class pipette, 20–200 µL) in a printed casing and presses its
plunger button with a **stepper-driven rack-and-pinion "thumb."** That means:

- **Accuracy/precision come from the commercial pipette itself** (< 0.3% relative error reported),
  and you use **standard 200 µL disposable tips** — exactly the OT-2-like behavior we want.
- The only things you build are the **motorized thumb**, the **pipette-holding casing**, and a
  passive **tip-changer (ejector) station**.
- Volume is set by driving the plunger a calibrated distance: **≈ 0.08 mm/µL** for a P200
  (16 mm of travel = 200 µL), vs 0.02 mm/µL for a P1000.

This is the cleanest open-source path to "P300-class disposable-tip pipetting on our own gantry":
adopt the arm, drop the FINDUS XYZ frame (the CubXL replaces it).

## Files to print (from `3D-models/pipette-arm/`)

| Printed part (STL) | Role |
|---|---|
| `Thumb_Casing (Meshed).stl` | Clamps the pipette body; the whole tool carrier |
| `Adapter (Meshed).stl` | Adapts the casing to the specific pipette body/collar (P200) |
| `Gear (Meshed).stl` + `Pinion (Meshed).stl` | Reduction gear + pinion driven by the stepper |
| `Gear_rack(Meshed).stl` + `Gear_Rack_Nut (Meshed).stl` | The linear "thumb" that presses the plunger |
| `Gear_Cover (Meshed).stl` | Gear guard |
| `Sliding_Bearing.FCStd` | Printed linear guide for the rack (export STL from FreeCAD) |

Reference-only (open in FreeCAD to check fit, not printed as-is):
`Assembly_Thumb.FCStd`, `Step_Motor.FCStd`, and the exploded view `expl.png`.
The **`P1000_Adapter` / `P1000_Bolt` / `P1000_Bottom`** parts are the **alternate** set for a P1000
pipette — **skip them for the P200 build**.

Tip-eject station (from `3D-models/racks/`): `tip-changer-top/bottom`, `tip-changer-bolt`,
`tip-changer-shaft-fixer`, and `Tip-changer-mount.png` for placement. Tip/well racks
(`tip-rack`, `96-well-rack`, `eppi-rack`) are optional if you use your own labware.

## Bill of materials

### A. The pipette (the "consumable" spec target)

| Item | Qty | Spec / example | ~Cost |
|---|---:|---|---:|
| Manual single-channel pipette, **20–200 µL (P200)** | 1 | Eppendorf Research plus, Gilson PIPETMAN P200, or generic; plunger travel ≈ 16 mm | $30–150 |
| 200 µL disposable tips + tip rack | 1 box | Standard universal-fit tips | $10–30 |

Pick the pipette **first** and confirm the printed `Adapter`/`Thumb_Casing` fits its body diameter
and plunger geometry — FINDUS's casings were modeled around a specific pipette and usually need a
small scale/offset tweak in FreeCAD for a different brand.

### B. Actuation (the motorized thumb)

| Item | Qty | Spec | ~Cost |
|---|---:|---|---:|
| **NEMA 11 stepper**, 1.8°/200-step, ~**6 N·cm** holding torque | 1 | Drives the pinion → rack → plunger | $15–20 |
| **DRV8825** stepper driver (Pololu breakout) | 1 | Per FINDUS schematic `findus.sch`; 32× microstepping | $3–6 |
| Printed pinion, gear, gear-rack, rack-nut, sliding bearing | set | From `pipette-arm/` STLs | filament ~$3 |
| Steel shaft/rod for the sliding bearing + pinion axle | 1–2 | ~3–5 mm rod, cut to length | $3 |
| M3 screws/nuts + heat-set inserts | ~10 | Assembly hardware | $5 |

### C. Control electronics

| Item | Qty | Spec | ~Cost |
|---|---:|---|---:|
| Microcontroller | 1 | Stock FINDUS uses an **ESP8266 (ESP-12)** running `findus.ino` (Wi-Fi AP + HTTP API). **On the CubXL**, drive the pipette axis from your existing motion controller instead (e.g. a Duet/RRF **E-axis**, or an extra DRV8825 on your MCU). | $0–10 |
| 12 V PSU for the driver | 1 | Sized for the stepper; shareable with the gantry supply | $0–15 |
| Endstop / limit switch for plunger home | 1 | To home the thumb to a repeatable zero | $2 |

### D. Tip ejection

| Item | Qty | Spec | ~Cost |
|---|---:|---|---:|
| Printed **tip-changer station** | 1 | `racks/tip-changer-*` — a fixed fixture the pipette pushes into to strip the used tip (see `remTip()` in `findus.py`) | filament ~$2 |

**Subassembly total (excluding the pipette): ≈ $35–70** plus the pipette ($30–150) and tips.
The full FINDUS workstation is "< $400"; the pipette arm alone is a small fraction of that.

## Calibration constants (straight from `findus.py`)

- **P200:** `200 µL ≈ 16 mm plunger travel` → **0.08 mm/µL** (≈ 43 steps/µL at the pipette axis).
- **P1000:** `1000 µL ≈ 19.9 mm` → 0.02 mm/µL (for reference).
- **XYZ belt axes** (not the pipette): GT2 belt (2 mm pitch) + 20-tooth pulley = 40 mm/rev;
  200 steps × 32 microsteps ÷ 40 mm = **160 steps/mm**. Reuse this only if you belt-drive an axis.
- Tip pick/eject positions are table-driven (`tip200`, `tip1000`, `tipbin` in `findus.py`) — retune
  the Z heights for the CubXL bed and your tip rack.

## Build steps

1. **Print** the `pipette-arm` set (Thumb_Casing, Adapter, Gear, Pinion, Gear_rack, Gear_Rack_Nut,
   Gear_Cover) and the `tip-changer` station. PETG/ABS recommended for the load-bearing thumb.
2. **Fit-check the casing** to your chosen P200 in FreeCAD; scale/offset the `Adapter` if needed so
   the pipette seats firmly and the rack lands square on the plunger button.
3. **Assemble the drive:** press the pinion onto the NEMA 11 shaft, mesh it with the printed gear,
   engage the gear on the rack, and slide the rack into the printed sliding bearing. The rack tip
   should contact the plunger button with a few mm of pre-travel headroom.
4. **Mount the pipette** in the Thumb_Casing/Adapter and bolt the stepper so the thumb's stroke
   covers the full 16 mm (P200) plunger travel plus the tip-eject over-stroke.
5. **Wire the stepper** to a DRV8825 (32× microstep) and to your controller — on the CubXL, add it
   as an extra stepper axis on your existing board (Duet E-axis or a spare DRV8825 on your MCU).
   You do **not** need the ESP8266 unless you want FINDUS's standalone Wi-Fi controller.
6. **Mount the tip-changer station** at a fixed, reachable spot on the CubXL bed (see
   `Tip-changer-mount.png`). Tip pickup = press the pipette onto a tip in the rack; ejection =
   drive into the tip-changer and retract (`getTip`/`remTip`).
7. **Home & calibrate:** set the plunger-home endstop as zero, then verify **16 mm = 200 µL**
   gravimetrically (weigh dispensed water, ρ≈1 g/mL) and adjust steps/µL to hit ISO-8655 tolerance.
8. **Drive it** from your gantry firmware, or adapt the FINDUS `findus.ino` + `findus.py` API if you
   keep the ESP8266.

## CubXL integration notes

- **Reuse the arm, drop the frame.** The CubXL is the XYZ system; you only need the `pipette-arm`
  (+ tip-changer). Mount the Thumb_Casing to your carriage/tool plate.
- **One extra motor axis.** The plunger is just another stepper — simplest is to run it as an
  E-axis on a Duet/RRF board (matches the Jubilee tool-changer path used elsewhere in this repo).
- **Volume class:** P200 tops out at 200 µL. For a true 300 µL, fit a **P300-class** manual pipette
  and re-derive mm/µL (the mechanism is identical; only the casing/adapter fit and calibration
  change). This is the smallest change to reach the 300 µL target with a commercial pipette's
  accuracy.

## Sources

- FINDUS paper: [10.1177/2472630319877374](https://doi.org/10.1177/2472630319877374)
- Repo (CAD, firmware, driver): [`FBarthels/FINDUS`](https://github.com/FBarthels/FINDUS) — GPL-3.0
- Calibration/step math: `source code/findus.py`; firmware: `source code/findus/findus.ino`;
  schematic: `findus.sch` (DRV8825 × 4, ESP-12)
