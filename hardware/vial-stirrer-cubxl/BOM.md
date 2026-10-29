# Bill of materials: single-vial magnetic stirrer, driven by the CubXL's Arduino Uno

For one stirrer, as asked for by @benwhitney5463 on
[PR #269](https://github.com/vertical-cloud-lab/byu-vcl/pull/269). It is the design in
[`README.md`](README.md), with the vial cup copied from the 9-vial holder. The stirrer
is driven by the **Arduino Uno already on the CubXL**, the one that runs the capper and
the pipette, rather than by its own XIAO RP2040. See
[Driving it from the CubXL's Arduino Uno](README.md#driving-it-from-the-cubxls-arduino-uno)
for the wiring and the firmware.

**Status: designed, not built.** Nothing has been printed, wired, flashed or run.
Once the parts are in, [`BUILD.md`](BUILD.md) is the step-by-step build guide.

Prices and stock were checked from the CubXL Pi on **2026-10-19**. The raw results are in
[`vendor_lookup_20261019.json`](../../outputs/issue-169-magnetic-stirrer/vendor_lookup_20261019.json).
Amazon prices change, so check them again when you order.

Item 10 (the perfboard) was rechecked on **2026-10-29** in headed Chromium on the CubXL Pi,
with [`scripts/amazon_listing_pi.py`](../../scripts/amazon_listing_pi.py): the strips are 6 × 28 holes
(columns A–Z, A, B; rows 01–06), 80 × 20 × 1.6 mm, still $7.99, with 9 left in stock.

Item 13 (the 100 nF capacitor) was added on **2026-10-29**, at @benwhitney5463's request, and
checked the same way: MCIGICM's kit, $6.99, in stock, shipped by Amazon, with 20 each of 100 nF
(104M, Y5V, 50 V) and 10 nF (103K, X7R, 50 V) in 1206.

## 1. Parts to buy (ME order)

All thirteen can go in one Amazon cart. The notes column gives other vendors where they
are cheaper or carry the same part.

| # | Part | Per stirrer | Order | Pack | Price | Notes |
|---|---|---|---|---|---|---|
| 1 | Fan, Orion **OD4010-12HSS**, 40 × 40 × 10.5 mm, 12 V, 2-wire | 1 | [Amazon B00JJ402HY](https://www.amazon.com/dp/B00JJ402HY) | 1 | $7.43 | The Pioreactor's fan, run at 5 V. Orion rates it 0.07 A typical, 0.09 A max, at 12 V ([datasheet](https://assets.testequity.com/te1/Documents/pdf/orion/OrionFans_DCFan_OD4010-05HSS_Datasheet_0125.pdf)). **Only 4 left** on 2026-10-19; Digi-Key 1053-1205-ND is the same part |
| 2 | Magnet, N52 disc, **1/4 × 1/16 in** | 2 | [Amazon B0DGG2Y6F7](https://www.amazon.com/dp/B0DGG2Y6F7) | 200 | $23.99 | Or [K&J D41-N52](https://www.kjmagnetics.com/d41-n52-neodymium-disc-magnet), $0.32 each |
| 3 | Stir bar, PTFE, **15 × 6 mm** | 1 | [Amazon B074FX1XJ2](https://www.amazon.com/dp/B074FX1XJ2) | 10 | $14.99 | Or [Pioreactor SKU 2046](https://pioreactor.com/products/15x6mm-ptfe-stir-bar), $2.24, which has a pivot ring. **Not the Pioreactor 20 mL's bar:** its v1.5 parts list has a 3 × 12 mm bar ([SKU 2003](https://pioreactor.com/products/3-mm-ptfe-stir-bar), $1.68), the length the 9.8 mm magnet spacing suits. Worth adding a few for the coupling test |
| 4 | Hall latch, Melexis **US1881**, TO-92UA | 1 | [Amazon B0D2XX9HY7](https://www.amazon.com/dp/B0D2XX9HY7) | 20 | $9.99 | 3.5–24 V, trips at ≤ 9.5 mT ([datasheet](https://www.melexis.com/-/media/files/documents/datasheets/us1881-datasheet-melexis.pdf)) |
| 5 | N-MOSFET, **IRLZ44N**, TO-220 | 1 | [Amazon B0FPQC8SV8](https://www.amazon.com/dp/B0FPQC8SV8) | 12 | $6.99 | **Skip if the capper's IRLZ44 kit has spares** |
| 6 | Schottky diode, **1N5819**, DO-41 | 1 | [Amazon B079KG1TN2](https://www.amazon.com/dp/B079KG1TN2) | 100 | $7.99 | Flyback across the fan. **Skip if the capper's 1N5819 kit has spares** |
| 7 | Resistors, **100 Ω** ×1 and **10 kΩ** ×2, 1/4 W | 3 | [Amazon B08FD1XVL6](https://www.amazon.com/dp/B08FD1XVL6) | 1000 (25 values) | $9.99 | **Skip if the lab has them.** Gate resistor, gate pull-down, Hall pull-up. The capper's 200 Ω works as the gate resistor too, and halves the pin's charging peak ([README](README.md#current-draw-and-power)) |
| 8 | Cable, **22 AWG, 4 conductors**, stranded | ~1.5 m | [Amazon B0BVQ7ZNCQ](https://www.amazon.com/dp/B0BVQ7ZNCQ) | 10 ft | $7.99 | Stirrer to Uno. Measure the route clear of the gantry first; 10 ft is enough for two stirrers |
| 9 | Connector pair, **JST-XH 4-pin**, plug and socket with 10 cm leads | 1 pair | [Amazon B0DNT63PTW](https://www.amazon.com/dp/B0DNT63PTW) | 10 pairs | $8.99 | Inline, near the Uno, so the stirrer can come off the deck without unsoldering |
| 10 | Perfboard, 2.54 mm pitch, 6 holes wide: a piece **8 × 6 holes** (20.3 × 20 mm) | 1 | [Amazon B0FVFTDYYH](https://www.amazon.com/dp/B0FVFTDYYH) | 20 strips, 2 × 8 cm, 6 × 28 holes | $7.99 | The junction board that sits where the XIAO would; three pieces to a strip ([`BUILD.md`](BUILD.md#the-junction-board)). Optional: the resistors can be spliced in-line with heat shrink instead |
| 11 | Heat-set insert, **M3 × 5.7 mm** (ruthex RX-M3x5.7) | 8 | [Amazon B08BCRZZS3](https://www.amazon.com/dp/B08BCRZZS3) | 100 | $9.99 | Ø4.0 mm holes, 6.5 mm deep |
| 12 | Socket head screw kit, **M3, 304 stainless**, 6–30 mm | 4 × M3×16, 4 × M3×12 | [Amazon B0D4L6QRZB](https://www.amazon.com/dp/B0D4L6QRZB) | 540 pcs | $9.99 | Stainless, not steel: the magnets catch on steel screws |
| 13 | Capacitor, **100 nF, 1206 chip** (3.2 × 1.6 mm), from a 16-value kit | 1 | [Amazon B06XDHC93D](https://www.amazon.com/dp/B06XDHC93D) | 320 (20 of each value) | $6.99 | Across the Hall sensor's supply, as Melexis recommends. It is soldered on top across the pads of E5 and E6 ([`BUILD.md`](BUILD.md#the-junction-board)). A leaded 100 nF won't do there: its ~4 mm body, laid flat, rides up on R3's end, under the fan. The kit's 100 nF is Y5V, fine for decoupling. Its 10 nF is the optional one in section 3. One value, X7R: [B08XQXLJFD](https://www.amazon.com/dp/B08XQXLJFD), 100 for $7.14 |

**Cost.** All thirteen packs come to **$133.31**. That drops to **$108.34** if the
MOSFET, the diode and the resistors come from the capper's leftovers and lab stock.
Item 13 was added after ME order 13518 went in, so it needs an order of its own. Once
the packs are bought, each further stirrer costs about **$20**, of which the fan is $7.43
and 1.5 m of cable about $4. For more
stirrers, the fan (one each), the stir bars (ten to a pack) and the cable (10 ft covers
about two) run out first; the other packs last for ten or more.

## 2. Parts to 3D print

Print in PETG or better. The Pioreactor prints its own bottom holder in PC-CF, and its
forum reports PLA warping when the stirrer runs warm. The STEP files are Onshape's
B-rep. They carry their own units (Onshape writes metres), so CAD tools and slicers
import them at the right size, and each has the same volume as its STL. Both sets are
exported in assembly position, which is also the print orientation for all four parts,
so a slicer only has to drop them onto the bed.

| Part | STEP | STL | Qty | Volume | Print |
|---|---|---|---|---|---|
| Base | [`step/base.step`](step/base.step) | [`stl/base.stl`](stl/base.stl) | 1 | 23.8 cm³ | Floor down. The key pockets are on the bed face |
| Vial holder | [`step/vial_holder.step`](step/vial_holder.step) | [`stl/vial_holder.stl`](stl/vial_holder.stl) | 1 | 17.1 cm³ | Flange down, so the fingers print upright as in the 9-vial holder. The 1.2 mm floor bridges the Ø27 mm carrier pocket; support it if the bridge sags |
| Magnet carrier | [`step/magnet_carrier.step`](step/magnet_carrier.step) | [`stl/magnet_carrier.stl`](stl/magnet_carrier.stl) | 1 | 0.8 cm³ | Pockets up |
| Deck key | [`step/deck_key.step`](step/deck_key.step) | [`stl/deck_key.stl`](stl/deck_key.stl) | **2** | 2.3 cm³ each | Nub up. Fix elephant's foot first; Cubware says to. The nub presses into the base, 0.05 mm a side, the best fit of the [2026-10-22 fit test](print/2026-10-22-a1mini-keys/README.md). Keep printing this one. The 0.10 and 0.15 mm keys are in [`stl/key_fit_test/`](stl/key_fit_test), in case another printer or filament comes out loose |

[`step/vial_stirrer_assembly.step`](step/vial_stirrer_assembly.step) is the whole
stirrer as 39 solids: the printed parts, the bought parts modelled from their datasheet
dimensions, the screws and inserts, the vial and the stir bar. It is for checking the fit
on the deck in CAD, not for printing. It still shows the XIAO RP2040 in the controller
pocket, which is where the junction board (item 10) goes.

About 46 cm³ in all, under 60 g of PETG even at 100% infill.

For the coupling test in README risk 1, also print **spacer discs**, Ø27 mm × 1, 2
and 3 mm, to go under the vial. Any slicer can make these as a cylinder primitive.

## 3. Already on the CubXL or in lab stock

| Part | Use |
|---|---|
| Arduino Uno R3, running the PANDA firmware | Drives the stirrer, with [`panda-arduino-stirrer.patch`](../../cubos/firmware/panda-arduino-stirrer.patch) applied. Uses D2, D10, 5V and GND |
| Adafruit Proto Shield v5, if it is on the Uno ([capper BOM](../../modules/electromagnetic-capper/BOM.md) item 4) | Solder the JST-XH socket's leads to 5V, GND, D2 and D10 |
| Male–male jumper wires (capper BOM item 10, Adafruit 4482) | Instead of the proto shield: one pin each into the Uno's 5V, GND, D2 and D10 headers |
| CA glue, hot glue, heat shrink, 26 AWG hookup wire | Magnets, carrier, Hall sensor and its 60 mm leads. The keys press in; glue them only if they are loose |
| 10 nF ceramic capacitor | Only if the measured rpm reads above 0 with the fan off: D2 to GND at the Uno. Item 13's kit has 1206 ones; a leaded one is easier at the Uno's headers |
| Soldering iron | Wiring, and pressing in the heat-set inserts |

## 4. Not needed when the Uno drives it

These are only for the self-contained version, which has its own USB link to the Pi
([`firmware/main.py`](firmware/main.py)). The prices are from 2026-10-10.

| Part | Source | Price |
|---|---|---|
| Seeed XIAO RP2040 | [Amazon B09NNVNW7M](https://www.amazon.com/dp/B09NNVNW7M) | $9.99 |
| USB-A to USB-C cable, 1 ft | [Amazon B07F17X6CP](https://www.amazon.com/dp/B07F17X6CP) (2) | $3.99 |

The printed parts are the same for both versions.
