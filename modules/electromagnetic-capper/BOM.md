# Bill of Materials — Electromagnetic Vial Capper/Decapper

Scoped to the capper/decapper module only (not the full PANDA-film platform).
Sources: [arXiv:2601.07043](https://arxiv.org/abs/2601.07043) §2 and the
[PANDA-BEAR BOM](https://github.com/BU-KABlab/PANDA-BEAR/blob/main/documentation/documents/bom.md) /
[Construction Guide](https://github.com/BU-KABlab/PANDA-BEAR/blob/main/documentation/Construction.md).
Prices are the PANDA-BEAR listed values (USD, mid-2026) — verify at order time.

## 1. Parts to procure (ME order)

| # | Item | Role | Part # | Vendor / Link | Qty | Est. Cost (USD) |
|---|------|------|--------|---------------|-----|-----------------|
| 1 | Electromagnet, 5 V 50 N (uxcell) | Cap pickup | 604267002199 | [Amazon B01N5OPUEC](https://www.amazon.com/dp/B01N5OPUEC) | 1 | 9.89 |
| 2 | IR break-beam sensor, 5 mm LEDs | Cap pickup/replace detection | 2168 | [Adafruit 2168](https://www.adafruit.com/product/2168) | 1 | 5.99 |
| 3 | Arduino Uno SMD R3 | Module control | A000073 | [DigiKey](https://www.digikey.com/en/products/detail/arduino/A000073/3476357) | 1 | 26.30 |
| 4 | Adafruit Proto Shield v5 | Driver circuitry | 2077 | [Adafruit 2077](https://www.adafruit.com/product/2077) | 1 | 9.95 |
| 5 | IRLZ44 logic-level MOSFET (kit) | Electromagnet switch | IRLZ44 | [Amazon B0CBKH4XGL](https://www.amazon.com/dp/B0CBKH4XGL) | 1 kit | 9.99 |
| 6 | 1N5819 Schottky flyback diode (kit) | Coil flyback protection | 1N5819 | [Amazon B079KG1TN2](https://www.amazon.com/dp/B079KG1TN2) | 1 kit | 7.99 |
| 7 | Resistor assortment (needs 200 Ω, 1 kΩ, 3 kΩ, 10 kΩ) | Gate/pull-down/sensor circuit | — | any (e.g., McMaster/Amazon assortment) | 1 kit | ~10 |
| 8 | 5 V DC power supply (≥2 A recommended) | Electromagnet power | — | any (e.g., [Adafruit 276](https://www.adafruit.com/product/276)) | 1 | ~8 |
| 9 | Jumper wires F–F, 200 mm ×40 | Wiring | 4447 | [Adafruit 4447](https://www.adafruit.com/product/4447) | 1 | 9.95 |
| 10 | Jumper wires M–M, 200 mm ×40 | Wiring | 4482 | [Adafruit 4482](https://www.adafruit.com/product/4482) | 1 | 9.95 |
| 11 | 20 mL clear VOA vials w/ septa caps | Stock vials the module services | 12-100-112 | [Fisher Sci](https://www.fishersci.com/shop/products/clear-voa-glass-vials-0-125in-septa/12-100-112) | 1 case | ~80 (case) |
| 12 | Sylgard 184 PDMS kit (base + crosslinker) | Cap interior fill, 10:1 ratio | Sylgard 184 | [Electron Microscopy Sciences 24236-10](https://www.emsdiasum.com/sylgard-184-silicone-elastomer-kit) | 1 kit (1.1 lb) | ~60 |
| 13 | Steel discs (magnetic mild steel; size to the recessed cap top — verify dia./thickness against `cad/VialCap16mm.step`) | Magnetic pickup target on each cap | — | McMaster-Carr (e.g., low-carbon steel discs) | 1 per cap + spares | ~10 |
| 14 | 3M double-sided adhesive (e.g., 3M VHB tape or 3M 468MP) | Affix steel disc to cap | — | McMaster/Amazon | 1 roll | ~15 |
| 15 | M3–M6 bolt kit | Mount electromagnet holder to gantry head | — | [Amazon B0CLZC8SQ5](https://www.amazon.com/gp/product/B0CLZC8SQ5/) | 1 kit | 23.99 |
| 16 | PLA filament | Caps, mount, vial rack | — | any (Bambu, Prusament, etc.) | 1 kg | ~25 |

**Estimated module subtotal: ~$320** (items 3–5, 7, 9–10, 15–16 are shared/stocked shop
items — actual incremental cost is lower if the lab already stocks Arduinos, resistor
kits, jumper wires, bolts, and filament).

Notes:

- The paper specifies the exact electromagnet as "5V 50N, uxcell" and the sensor as
  "2168, Adafruit" (arXiv:2601.07043, §2, PAW module 2).
- Resistor values: the PANDA-BEAR BOM lists 10 kΩ + 200 Ω for the electromagnet circuit
  while the Construction Guide checklist lists 1 kΩ / 200 Ω / 3 kΩ for the full PAW —
  an assortment kit covers both readings; confirm against the
  [wiring diagram](https://github.com/BU-KABlab/PANDA-BEAR/blob/main/documentation/Arduino-Wiring.md)
  and [PANDA_Arduino firmware](https://github.com/BU-KABlab/PANDA_Arduino) pinout when wiring.
- If integrating with an existing gantry (CNC/Jubilee/Opentrons), the Arduino + shield
  can be replaced by any spare 5 V-tolerant GPIO + MOSFET driver you already have.

## 2. Parts to 3D print (in-house, PLA)

| File (committed in [`cad/`](cad/)) | Part | Qty |
|------|------|-----|
| `VialCap16mm.step` | Custom magnetic vial cap body | 1 per stock vial (print ≥10; validated across independently printed caps) |
| `PAW-V2-ElectromagnetMount.step` | Electromagnet + IR sensor mount for gantry head | 1 |
| `9VialHolder20mL_TightFit.step` | 9-position 20 mL vial rack (deck) | 1 |

Optional deck-mounting parts (PANDA-specific "pill" mounts) are in
[PANDA-BEAR/documentation/3D-prints/DeckAccessories](https://github.com/BU-KABlab/PANDA-BEAR/tree/main/documentation/3D-prints/DeckAccessories);
skip or adapt these if mounting the rack to a different deck.

## 3. Cap fabrication steps (per paper §3.1)

1. Print cap bodies in PLA.
2. Mix Sylgard 184 at 10:1 base:crosslinker; fill the cap interior; cure.
3. Cut/punch steel discs to fit the recessed region on the cap top; attach with 3M adhesive.
4. Validate: run decap/recap cycles over a range of approach heights — expect ~3 mm
   vertical tolerance (paper Figure 2C).
