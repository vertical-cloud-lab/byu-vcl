# Kardex Shuttle height: what Kardex publishes, and a unit near 30 ft

byu-vcl #303, PR #318. The model's Shuttle XP 500 is 3,950 mm tall ([`vlm.py`](../vlm.py) `UNIT_H`, the tallest under
#53's 13 ft). Sterling wants it "closer to 30 ft" (9,144 mm). Sources were read on 2026-11-20 and quotes are verbatim.

## Recommendation for the model

- **`UNIT_H = 9150.0`, 30 ft 0.2 in.** That is 2,550 mm plus 66 steps of 100 mm, so it is on Kardex's grid and well
  inside the Shuttle 250/500's 2,550-30,050 mm. If 30 ft is a cap rather than a target, use 9,050 mm (29 ft 8.3 in).
- **Keep the 260 mm drive bay at the top** (`Z_TOP_IN = UNIT_H - 260`, which gives 8,890 mm).
  - Kardex publishes no top-section height. The 260 mm is the model's own figure.
  - *Our inference:* the drive doesn't grow with the unit, and nothing stands above the cladding, since Kardex asks
    for only 20 mm of room over a unit.
- **What the building needs.**
  - A room at least 9,170 mm (30 ft 1 in) tall.
  - 31.5 ft to the sprinkler deflectors under NFPA 13's 18 in, or 33.0 ft under ESFR's 36 in (PR #344's clearances).
  - That fits PR #344's 36 ft buildings. A 32 ft building fits it only without ESFR: under ESFR its tallest unit is
    8,750 mm, and Holbrook Bldg 5 lists ESFR.
- **Code that assumes 3.95 m.** [`setup_lab.py`](../setup_lab.py) hangs the north cable tray at 4,300 mm ("above the
  VLM's 3950 mm roof"). Its dock supply risers are `4150.0 - V.UNIT_H` tall, which goes negative.

## What Kardex publishes

| | Shuttle 250/500 | Shuttle 700 | Shuttle 1000 |
|---|---|---|---|
| Unit height, in steps of | 2,550-30,050 mm, 100 mm | 2,550-20,050 mm, 100 mm | 2,550-20,050 mm, 100 mm |
| Load per tray | 560 kg (page, 2014 brochure); 555 kg (2024 factsheet) | 725 kg | 1,000 kg (900 kg at 2,450 mm wide) |
| Load per unit | "Maximum load 67/120 t" (2014); "TOTAL UNIT LOAD (Unit Capacity): 70000 kg" (2026 order sheet) | not given | "Max. total load 67/120 t" (2014) |

**Sources.**

- [Product page](https://www.kardex.com/en-us/products/shuttle-vertical-lift-modules): "Standard technical data,
  other sizes possible on request". The [global page](https://kardex.com/en/products/shuttle-vertical-lift-modules)
  adds "standard device heights extending up to 30 m".
- Factsheet 8103-US-2112, dated 2024-02-20
  ([dealer copy](https://info.southwestsolutions.com/hubfs/Brochures/SSG-Brochures/KAR-198/Shuttle.pdf); Abel Womack's
  `Factsheet_US_KardexShuttle.pdf` is a 404).
- Shuttle XP US brochure 1108C-2014-US-1301-MD, in identical dealer copies at
  [SupplyCore](https://www.supplycore.com/wp-content/uploads/2022/01/Shuttle-XP-Vertical-Lift-Module-1108-1.pdf) and
  [V&H](https://www.vhhdlg.com/wp-content/uploads/2022/08/VH_Kardex_Remstar-Shuttle_XP.pdf).
- **Taller than 30 m:** Kardex's [blog](https://www.kardex.com/en-us/blog/outdoor-vertical-lift-module-storage-system)
  says Shuttles "are TÜV-certified for safe, stable operation, even up to 41 meters high".
- **In service:** ENGEL runs a Shuttle 700 at "H: 14,950mm" ([case study](https://blog.kardex-remstar.com/case-studies/engel)).

## Raising a unit later

- **The 2014 brochure** calls the Shuttle "modular in its construction with the ability to change its height and
  number of access openings pre and post construction". It adds: "The height of the unit can be modified quickly and
  easily, and additional access openings can be retrofitted to meet future needs".
- **Kardex's product page now says less:** "It can be expanded or adapted at any time without disrupting ongoing
  operations".
- **A used-equipment dealer** writes "(height Kardex is adjustable to available height)"
  ([machineseeker](https://www.machineseeker.ie/kardex-shuttle+xp500/i-19235156)).
- **Not found:** "building higher at a later stage is feasible", or any procedure, cost or downtime for a raise.

## Weight, floor, seismic and clearance

- **Weight.** Kardex's order sheet ("Shuttle POF Version 16") for SHUTTLE-01-500-2450x864x6750 gives "Unit Weight
  without Trays: 2936 kg" ([StoreMoreStore option 1](https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/VLM-Option-1-96x34-Light-Specification-Sheet.pdf)).
  - Its 138 trays weigh 4,830, 6,486 or 8,004 kg (options 1,
    [2](https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/VLM-Option-2-96x34-Medium-Specification-Sheet.pdf)
    and [3](https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/VLM-Option-3-96x34-Strong-Specification-Sheet.pdf)).
  - That is 35, 47 or 58 kg each for light, medium or strong trays (*our division*). They are rated 230, 360 and
    500 kg.
- **Floor, our estimates.** Kardex publishes no floor pressure or slab specification.
  - A 9.15 m unit weighs about 4.0 t, scaling with height.
  - At the 70 t cap on the 2,780 × 3,073 mm footprint, that gives about 85 kN/m² (1,770 psf). PR #344 gets
    86-94 kN/m² at 15 m.
  - 24 strong trays (PR #344's count at 9.2 m) carrying #53's 490 kg each give about 20 kN/m² (410 psf).
- **Seismic.** Kardex lists "Vertical Lift Module Kardex Shuttles up to 15 meters in height" among standard solutions
  "designed for peak ground acceleration up to 0.5 g-force in accordance with Eurocode 8", with "Robust wall bracing
  and floor anchoring" ([earthquake page](https://www.kardex.com/solutions/controlled-environment/earthquake-resistant)).
  - Utah County is Seismic Design Category D (PR #344), so ask Kardex whether 0.5 g covers the site.
  - Units with "an additional seismic absorption structure" "can be installed directly next to each other" (product
    page).
  - The order sheet: "External supports are Only for stand-alone units (not for units positioned side by side)!".
- **Clearance.** The only published figure is the order sheet's: "The required room height (unit height + 20mm
  /0.79") is the absolute minimum measure. Possible floor / ceiling unevenness and slope must be considered therein."
  How the top modules go in with 20 mm to spare is a question for Kardex.

## What PR #344 says about height

[PR #344](https://github.com/vertical-cloud-lab/byu-vcl/pull/344) is open and covers facility locations (#343).

- **The array.** Its "50 ft array" is eight XP 500s at 15.15 m (`scale.py` @ 03801d8, 44 trays a unit). That needs
  51.2 ft clear, or 52.7 ft under ESFR.
- **The sites.** No building near BYU has more than 36 ft. So it offers a 3.4 m pit, a high bay, or shorter units: 15 ×
  9.2 m under 32 ft (24 trays each), or 13 × 10.5 m under 36 ft.
- **A rounding slip.** Its `tallest_under()` rounds to whole 100 mm, so those heights miss Kardex's grid by 50 mm. Under
  32 ft the grid allows 9,250 mm.
- **What it lists as unpublished:** self-weight, floor load, slab, levelness and the clearance over a unit. Its draft 2
  asks Kardex or Hoj for them. The order sheet above answers three: the weight at 6.75 m, the unit capacity and the room
  height.
- **The lab itself.** Its later `needs.md` finds that the #318 lab needs only 16-18 ft clear.

**Not found:** the drive-bay or top-section height, a slab specification, and Kardex's installation or maintenance
clearance.
