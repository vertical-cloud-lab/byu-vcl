# PiPER enclosure

Figures and numbers behind the enclosure discussion in
[#229](https://github.com/vertical-cloud-lab/byu-vcl/issues/229).

| Figure | What it shows |
|---|---|
| `piper-reach.png` | The PiPER and gripper, rendered from AgileX's own URDF, and a side view of where the fingertip can reach |
| `enclosure-options.png` | The quarter, half and full domes as sketched, plus spot D with the arm centred, all at one scale |
| `cb154-arm-locations.png` | Spots D and E on [`cb154.pdf`](../../cb154.pdf), and the ceiling height available for a two-level setup |

To regenerate the figures, run `xvfb-run -a python render_figures.py`. The script clones
`agilexrobotics/piper_ros` at `ac41fcb` into `/tmp` for the URDF and meshes.

## PiPER numbers

These come from the [user manual](https://static.generation-robots.com/media/agilex-piper-user-manual.pdf).

| | Arm | Two-finger gripper |
|---|---|---|
| Reach / stroke | 626.75 mm working radius | 0–70 mm opening. There is also a 100 mm version, and the SDK has a 70/100 mm travel setting |
| Payload / force | 1.5 kg | 40 N rated, 50 N max |
| Mass | 4.2 kg | 0.5 kg |
| Repeatability | ±0.1 mm | ±0.5 mm |
| Power | 24 V (24–26 V), ≤120 W peak, ≤40 W typical | 24 V, ≤50 W |
| Interface | CAN (USB–CAN adapter included) | Through the arm |
| Mounting | Four M5 threaded holes, 70 mm spacing | Flange |
| Joint range | J1 ±154°, J2 0–195°, J3 −175–0°, J4 ±106°, J5 ±75°, J6 ±100° | |
| Joint speed | 180 / 195 / 180 / 225 / 225 / 225 °/s | |

The manual also asks for "a relatively open area" because the arm has no obstacle sensing.
It is rated IP22.

## Reach

These values are computed here from the URDF, with the fingertip taken as 140 mm past the flange.

- **Flange reach:** 0.63 m from the base axis, which matches the 626 mm spec.
- **Fingertip reach:** 0.77 m horizontally.
- **Fingertip height:** up to 0.89 m above the mounting surface. If the base sits at the edge of a deck, the fingertip can also reach 0.40 m below the mounting surface.
- **Rest pose:** the zero pose folds the elbow 0.28 m *behind* the base. A base pushed into a corner or against a wall hits that wall every time the arm parks.
- **Reach lost to the walls:** this is the share of the fingertip's reachable volume that falls outside the walls. It treats the workspace as a solid of revolution, since J1 plus flipping over the top covers every direction.

  | Option | Share outside the walls |
  |---|---|
  | Quarter dome as sketched | 68 % |
  | Half dome as sketched | 44 % |
  | Full dome | 0 % |
  | Spot D (1.29 × 1.36 m), arm centred | 7 % |

## Keeping it inside the enclosure

The PiPER SDK has three relevant settings. All are in `piper_sdk/interface/piper_interface_v2.py`.

- **`MotorAngleLimitMaxSpdSet`:** sets per-joint angle and speed limits, which are stored on the arm.
- **`CrashProtectionConfig`:** sets collision sensitivity per joint, from 0 (off) to 8.
- **`MotionCtrl_2(installation_pos=...)`:** sets the mounting orientation, either upright, left-side or right-side (firmware V1.5-2 and later). There is no inverted option.

The SDK has no Cartesian keep-in box. That check belongs in our motion code, or can be done
with walls in MoveIt's planning scene.

## Parts

Prices were checked on 2026-09-25, before tax. Home Depot and Walmart block automated page
fetches, from both a CI runner and the OT-2 stream-cam Pi's residential IP, so their prices
come from search results. Confirm them in the store.

| Item | Product | Price | Link |
|---|---|---|---|
| Pipe | Charlotte 3/4 in Sch 40 PVC, 10 ft | $9.31 | [Home Depot](https://www.homedepot.com/p/Charlotte-Pipe-3-4-in-x-10-ft-PVC-Schedule-40-Pressure-Plain-End-Pipe-PVC-04007-0600/100348472) |
| Pipe, 1.9 m build | JM Eagle 1 in Sch 40 PVC, 10 ft | $13.50 | [Home Depot](https://www.homedepot.com/p/JM-EAGLE-1-in-x-10-ft-White-PVC-Schedule-40-Pressure-Plain-End-Pipe-531194/202280936) |
| Corners | FORMUFIT 3/4 in 3-way elbow, 8-pack | $18.99 | [Home Depot](https://www.homedepot.com/p/Formufit-3-4-in-Furniture-Grade-PVC-3-Way-Elbow-in-White-8-Pack-F0343WE-WH-8/205749438) |
| Mid-side posts | FORMUFIT 3/4 in 4-way tee, 8-pack | $20.99 | [Home Depot](https://www.homedepot.com/p/Formufit-3-4-in-Furniture-Grade-PVC-4-Way-Tee-in-White-8-Pack-F0344WT-WH-8/205749450) |
| Sleek pipe | FORMUFIT furniture-grade, 3/4 in × 5 ft, 2-pack | $24.99 | [Home Depot](https://www.homedepot.com/p/Formufit-3-4-in-x-5-ft-White-Furniture-Grade-Schedule-40-PVC-Pipe-2-Pack-P034FGP-WH-5x2/312192325) |
| Cloth | Everbilt 8 oz canvas drop cloth, 9 × 12 ft | $34.98 | [Home Depot](https://www.homedepot.com/p/Everbilt-9-ft-x-12-ft-8-oz-Canvas-Drop-Cloth-BARI-DP8-9-12/308535004) |
| Cloth | Hyper Tough canvas drop cloth, 9 × 12 ft | $24.97 | [Walmart](https://www.walmart.com/ip/Hyper-Tough-Canvas-Drop-Cloth-9-x-12/864492745) |
| Cloth | Mainstays Yale white tablecloth, 60 × 102 in | from $10.96 | [Walmart](https://www.walmart.com/ip/Mainstays-Yale-Fabric-Tablecloth-White-60-W-x-102-L-Rectangle/993645679) |
| Base | Columbia PureBond 3/4 in birch plywood, 2 × 4 ft | $34.11 | [Home Depot](https://www.homedepot.com/p/Columbia-Forest-Products-3-4-in-x-2-ft-x-4-ft-PureBond-Birch-Plywood-Project-Panel-4391/311925836) |
| Arm screws | Everbilt M5 × 25 mm socket cap, 3-pack (buy 2) | $2.75 | [Home Depot](https://www.homedepot.com/p/Everbilt-M5-0-8-x-25-mm-Zinc-Plated-Steel-Socket-Cap-Recessed-Hex-Screws-3-per-Pack-803318/204281933) |
| Clamp to table | BESSEY CM40 4 in C-clamp (buy 4) | $6.56 | [Home Depot](https://www.homedepot.com/p/BESSEY-CM-Series-4-in-Capacity-Drop-Forged-C-Clamp-with-3-1-4-in-Throat-Depth-CM40/205512968) |
| Cloth to pipe | Snap clamps for 3/4 in PVC, 10-pack | $8.80 | [Johnny's](https://www.johnnyseeds.com/tools-supplies/greenhouse-and-tunnel-supplies/hardware-accessories/snap-clamps-for-3-4%22-pvc-or-1%22-emt-7036.html) |
| Rigid panels | Coroplast 4 mm white, 4 × 8 ft | $34.98 | [Home Depot](https://www.homedepot.com/p/Coroplast-48-in-x-96-in-x-0-157-in-White-Corrugated-Plastic-Sheet-CP4896S/205351385) |
| Frame alternative | 80/20 1010 extrusion, 72 in | $32.35 | [DigiKey](https://www.digikey.com/en/products/detail/80-20-llc/1010-72/21783470) |
| Opaque drape | NICETOWN blackout curtains, 2 × 52 × 84 in | $58.99 | [NICETOWN](https://nicetown.com/products/100-percent-blackout-grommet-curtains-home) |

Snap clamps are easy to buy in the wrong size. Clamps sold as "3/4 in" fit 3/4 in EMT, which
is the same size as 1/2 in PVC. For 3/4 in PVC, get the ones labelled "3/4 in PVC / 1 in EMT".

Rough totals for a 1.3 × 1.4 × 1.1 m box with four sides and a top:

| Build | Approx. cost |
|---|---|
| Plain PVC and drop cloth | $265 |
| Furniture-grade PVC and Coroplast | $430 |
| 80/20 frame | $750 |
