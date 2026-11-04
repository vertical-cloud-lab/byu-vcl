# The Kardex opening height, and what a taller one would allow

[`kardex_tall.py`](../kardex_tall.py), byu-vcl #303. Sterling's question on PR #318 (2026-11-04): "I'm pretty sure there
are bay sizes that are close to 1000 mm, as a Kardex option ... Assuming a taller option, what would be enabled? E.g.,
MX-Lab? (Maybe too heavy)". The checks are in [`out/tall_opening.json`](../out/tall_opening.json). The scene is
[`out/vlm_tall_opening_still.png`](../out/vlm_tall_opening_still.png), with a
[GIF](../out/vlm_tall_opening.gif) and an [MP4](../out/mp4/vlm_tall_opening.mp4).

## What Kardex publishes: 727.5 mm

- **Kardex's order sheets give 727.5 mm.** The "Kardex Shuttle POF" for the XP 500 at 2450 × 864 mm gives "Maximum
  Product Height: 727.5 mm / 28.64 in. Depends on Tray Type selection", with "Clearance Required Above Product:
  20 mm". The sheet for 3050 × 864 mm gives 727 mm. Both have the access table at 833 mm.
- **Kardex's own pages say about the same.** Its blog gives VLM trays "a max product height of just over 28 inches".
  The brochures don't give a product or opening height at all: the Shuttle XP brochure (US and the German 2017
  edition), the Shuttle factsheet (8103-US-2112), the product page, the heavy-goods product guide and buyer's guide.
- **ac-dev-lab has nothing on opening height.**
  - #372 records the AC's XP-500 quote: 49.21 × 24 in trays, 992 lb per tray, and a floor-to-tray height of 32.8 in,
    "standard on all shuttles. They can change this height if necessary but would need to know before ordering".
    That is the delivery height, not the opening's.
  - #471, #370, #371, #373 and #216 give no opening height. #216 does hold the VLM vibration data: Johnstone's
    `VBA01001.XLS` and `organized_data.csv`, and Pranshu's runs at Johnstone and CMTS.

## Why a taller opening is plausible: all indirect

- **The Shuttle 1000 stores mesh boxes.** Kardex: "Use a forklift to stack and store EURO pallets and mesh boxes on
  special trays". The XP brochure lists "special trays for pallet storage" and "tray extraction for forklift
  operation". A Euro mesh box (UIC 435-3, formerly DIN 15155) is 1240 × 835 × 970 mm outside. So those trays must pass
  about 1 m. This is an inference: Kardex gives no figure for them.
- **Kardex makes other sizes.** The factsheet says "other sizes possible on request".
- **One used XP 500 has a taller opening.** It was built in 2005/2006, with 3050 × 864 mm trays, and is listed with
  "Bedienöffnung frontseitig auf 833 mm, Höhe 996 mm": a front opening 996 mm tall over the usual 833 mm table.
  - In `vlm.py` the header sits 867 mm over the table for 727.5 mm of goods. That spacing is from Kardex's renders, not
    published.
  - At the same spacing, a 996 mm opening takes about **856 mm** of goods. That figure is an estimate.
- **The TowerMat isn't the answer.** It is Kardex's lift for heavy, oversized goods and pallets, with 3–5 t carriers up
  to 12.2 × 2.1 m. It publishes no goods height, and it is a different machine.

**So "close to 1000 mm" is plausible, most likely on the Shuttle 1000's pallet trays, but no published figure confirms
it.** Four heights are checked:
- 727.5 mm, today;
- about 856 mm, the 996 mm opening (estimated);
- 970 mm, a mesh box;
- 1000 mm, Sterling's figure.

## What each tray carries

Kardex rates a tray as a whole and per area: the POF gives lb/sq ft, a distributed load. A machine on a small
footprint can be under the tray's total and still over its rating per area.

| Tray | kg per tray | kg/m² over the tray | Source |
|---|---|---|---|
| XP 500, 2450 × 864, Strong | 500 (the #53 quote: 490) | 236 | POF option 1; #53 |
| XP 500, 2450 × 864, 66-1-Medium-100 | 525 | 248 | POF option 1 |
| XP 500, 3050 × 864, Strong | 265 | 101 | POF option 6 |
| XP 500, 3050 × 864, 75-3-Medium-100 | 505 | 192 | POF option 6 |
| XP 700 | up to 725 | 342 at 2450 × 864 | XP brochure, factsheet |
| XP 1000, 2450 wide | 900 (1,000 at 1250, 800 at 4050); Kardex's page now says 825 | 425 at 2450 × 864 | XP brochure; kardex.com |

Trays are 610–1270 mm deep on the XP 250/500 and 700, and up to 1778 mm on the 1000.

## What about 1000 mm would let onto a tray

| Machine | W × D × H (mm) | kg | 727.5 | ~856 (est.) | 970 | 1000 | Per area against a strong XP 500 tray | Needs |
|---|---|---|---|---|---|---|---|---|
| InssTek MX-Lab (DED) | 680 × 684 × 835 | 250 | no | yes | yes | yes | 537 kg/m², 2.3× | argon (≤ 50 ppm O₂ option), powder carrier gas, 220 V 15(20) A, exhaust |
| MX-Lab base cabinet (estimated) | 900 × 760 × 1000 | ? | no | no | no | just | — | not published |
| Mastrex MX100 (LPBF) | 560 × 560 × 800 | 125 | no | yes | yes | yes | 399 kg/m², 1.7× | 120 V; nitrogen (Mastrex sells an NG150 generator) |
| Lasefinity Fusion X (LPBF) | 600 × 650 × 860 | not published | no | no (by 3.5 mm) | yes | yes | — | N₂ or Ar; filters on board |
| Sharebot MetalONE (LPBF) | 740 × 630 × 1000 | 150 | no | no | no | just | 322 kg/m², 1.4× | inert gas |
| Kings 3D DiMetal-100 (LPBF) | 690 × 720 × 1000 | 140 | no | no | no | just | 282 kg/m², 1.2× | inert gas, 220 V 50 Hz |
| Parker Balston UHPN2-1100 | 305 × 406 × 889 | 50 | no | no | yes | yes | (50 kg) | compressed air, 120 V |
| Formlabs Form 4, cover open | 407 × 478 × 844 | 18.3 | no | yes | yes | yes | — | power; resin and IPA are open EHS questions |

Still too tall at 1000 mm:
- Meltio M450, 1400 mm;
- Instron 68SC-2, 1410 mm. The shortest single column, the 68SC-05, is 1020 mm.
- One Click Metal MPRINT, 1900 mm;
- Kobelco O2-Dr.HIP, 1300 mm. At 1100 kg it is also over every Shuttle tray's rating.
- the rePowder, 1600 mm;
- the glovebox, 1794 mm;
- the Aconity MIDI, 2320 mm and 1450 kg.

## Is the MX-Lab too heavy?

**Not by the tray's total, but by its rating per area.**
- **By the total:** 250 kg is half a strong XP 500 tray's 500 kg, and well under the 700's 725 or the 1000's 825–900.
- **Per area:** it stands on 0.47 m², which makes 537 kg/m², 2.3 times the strong tray's 236 kg/m².
- **What would carry it:**
  - a spreader plate the width of the tray;
  - a Shuttle 1000 pallet tray, which is built for concentrated loads. A Euro pallet at 825 kg is about 860 kg/m².

  The Shuttle 1000 is also the model whose mesh-box trays imply about 1 m. So it is the one to ask Kardex about.

Other things come with it:
- **Its base cabinet.** InssTek's 835 mm is "without accessories", and what the cabinet holds is not published. If it
  holds the laser source, it rides on the same tray, because a process fibre can't go through a dock. InssTek's 2024
  brochure draws the laser generator inside the machine itself, which would leave the cabinet off the tray, but it
  doesn't say so (instruments_lab.md). On our estimate
  the cabinet is itself 1000 mm tall.
- **Argon and exhaust go through the dock.** That means a gas line in the CombiTac and an extraction duct, which the
  dock doesn't have yet.
- **More heat inside the VLM.** Its laser goes up to 500 W, and `notes/services.md` already counts about 7 kW.

## Other things to know

- **Tall trays use up the columns.** Each tray in storage takes its goods' height plus the 20 mm clearance, in 25 mm
  steps on the XP 500 and 50 mm on the 700 and 1000. One 1000 mm tray takes about 275 mm more of the columns than a
  727.5 mm one, and the unit is 3950 mm tall (under 13 ft, #53).
- **The arm's reach to the top of a 1000 mm machine isn't checked.** At the opening, the tray floor is about 857 mm
  up, so the top of such a machine is about 1857 mm up.
- **Kardex's ratings are per tray type and per width.** The wider the tray, the less it carries per tray at the same
  type (265 kg at 3050 mm against 500 kg at 2450 for the Strong). The special tray types carry more, but their heights
  are not given.

## Ask Kardex

1. The tallest product height through the opening on the Shuttle 700 and 1000, standard and as a special. Also on the
   XP 500: the used unit's 996 mm opening.
2. The product height of the Shuttle 1000's pallet and mesh-box trays, and their rating for a concentrated load, for
   example 250 kg on 0.47 m².
3. Whether a tall opening changes the 833 mm delivery height or the unit height.

## Sources

- Kardex Shuttle POF (order sheets) for the XP 500:
  - [2450 × 864](https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/VLM-Option-1-96x34-Light-Specification-Sheet.pdf)
  - [3050 × 864](https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/VLM-Option-6-120x34Medium-Specification-Sheet.pdf)
- Kardex Remstar Shuttle XP brochure:
  - [US, via SupplyCore](https://www.supplycore.com/wp-content/uploads/2022/01/Shuttle-XP-Vertical-Lift-Module-1108-1.pdf)
  - [German, 2017](https://wtp.hoechsmann.com/lexikon/pdf/kad_shuttlexp_2017_de.pdf)
- [Kardex Shuttle factsheet](https://info.southwestsolutions.com/hubfs/Brochures/SSG-Brochures/KAR-198/Shuttle.pdf)
  (8103-US-2112)
- Kardex's own pages:
  - [Shuttle product page](https://www.kardex.com/en-us/products/vertical-lift-module/kardex-shuttle)
  - [heavy-duty units](https://www.kardex.com/en/products/heavy-duty-units)
  - [TowerMat](https://www.kardex.com/en-us/products/vertical-lift-module/towermat)
  - [blog, VLMs vs vertical carousels](https://www.kardex.com/en-us/blog/vertical-lift-modules-vs-vertical-carousels)
- [The used XP 500 with a 996 mm opening](https://www.lagersysteme-paternoster.de/gebrauchte-lagertechnik/kardex-shuttle-xp500-3050x864-pos-89/)
  (lagersysteme-paternoster.de, Pos. 89)
- [Euro mesh box, 1240 × 835 × 970 mm](https://www.hellopro.fr//documentation/pdf_prod/3/0/9/88526_697b113fadeb2d9921786be336dce08a.pdf)
- ac-dev-lab:
  - [#372](https://github.com/AccelerationConsortium/ac-dev-lab/issues/372)
  - [#471](https://github.com/AccelerationConsortium/ac-dev-lab/issues/471)
  - [#216](https://github.com/AccelerationConsortium/ac-dev-lab/issues/216)
- The machines:
  - [Tech-Labs, Mastrex MX-100](https://tech-labs.com/products/mastrex-mx-100-metal-3d-printer)
  - [TCT Magazine, Lasefinity Fusion X](https://tctmagazine.com/lasefinity-fusionx-compact-desktop-metal-3d-printer-launches-at-tct-3sixty)
  - [All3DP, Kings 3D DiMetal-100](https://all3dp.com/4/kings-3ds-140-kg-dimetal-100-proves-desktop-sized-isnt-always-desktop-friendly/)
  - the rest from this repo's notes: [`instruments_lab.md`](instruments_lab.md) (MX-Lab),
    [`services.md`](services.md) (N₂ generator), and `out/fabrication.json` and `out/instruments.json`.

## Assumed or not checked

- **The ~856 mm figure is an estimate.** It assumes the used unit's header is as far over its goods as on the order
  sheet's unit. vlm.py draws that spacing from renders.
- **The 1000 mm itself is not a published figure.** It is Sterling's recollection, close to the mesh box's 970 mm.
- **Some machines are boxes in the scene.** The MX100, Fusion X and N₂ generator are drawn as boxes at their published
  size, and the MX-Lab's cabinet as a box at its estimated size. The MX-Lab is `instruments_lab.ded()` with the cabinet,
  shelf, balance and exhaust duct taken off.
- **Point-load ratings aren't published,** so the per-area comparison only shows where to ask. It doesn't show that a
  tray would fail.
