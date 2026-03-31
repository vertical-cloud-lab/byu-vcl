# Glovebox Options

Research for inert atmosphere glovebox procurement for the BYU Vertical Cloud Lab alloy discovery workflow. See [GitHub Issue #75](https://github.com/vertical-cloud-lab/byu-vcl/issues/75) and related [Issue #29](https://github.com/vertical-cloud-lab/byu-vcl/issues/29).

## Use Case

- Keeping flammable metal powders (Aluminum, Magnesium) and other powders (Silicon) very dry
- Mixing powders prior to transfer to an ultrasonic atomizer
- Potential battery-related work (electrolyte handling, electrode assembly)
- Inert atmosphere (N₂ or Ar) with low O₂ and H₂O levels required

## Requirements

| Requirement | Target |
|---|---|
| Atmosphere | Inert (N₂ or Ar), <1 ppm O₂ and H₂O preferred |
| Glove ports | 2-port minimum; 4-port preferred |
| Antechambers | Large and small |
| Gas purifier | Yes (with solvent removal for battery solvents) |
| O₂/H₂O analyzers | Yes |
| Electrical outlets | Inside the box (for powder trickler, etc.) |
| Feedthroughs | Banana plugs (5–10) for battery cycling (nice-to-have) |
| Solvent compatibility | LiPF₆, EC, ethers, and similar battery electrolytes |
| Form factor | On legs (floor standing) |

## LC Technologies (Primary Vendor — Quotes Received)

Recommended by Dr. Jason Porter and Dr. Devin Rappleye (BYU faculty). LC Technologies is a US-based manufacturer known for competitive pricing and good service. All systems achieve <1 ppm O₂ and H₂O with the RGP-1 gas purification system.

- **Website**: [lctechinc.com](https://lctechinc.com/)
- **Contact**: Quotes requested and received (see below)
- **Academic discount**: 25% included in all quotes
- **Warranty**: 2 years
- **Installation & training**: Free (included)

### Quotes Summary

All three glovebox quotes include the glovebox, large and small antechamber, gas purifier (with solvent removal), O₂/H₂O analyzers, and binding posts (electrical feedthroughs).

| Quote # | Model | Ports | Description | Estimated Price (w/ 25% academic discount) |
|---|---|---|---|---|
| LCT-26-0202 | LC-100 | 2-port | Single user, single sided | ~$34K |
| LCT-26-0224 | LC-180 | 4-port | Dual user, slightly longer | ~$47K–$50K |
| LCT-26-0225 | LC-200 | 4-port | Dual user, double length | ~$50K–$54K |

> **Price range: $34K–$54K** depending on model (see attached PDFs in [issue #75](https://github.com/vertical-cloud-lab/byu-vcl/issues/75) comments).

### Optional Accessories (Quote LCT-26-0203)

| Accessory | Description | Notes |
|---|---|---|
| AC-601 Automatic Antechamber Control | One-button full antechamber cycle (3 evac + 3 refill) | Reduces user error; good for multi-user labs |
| AN-710 Solvent Sensor | Detects solvent breakthrough in carbon column | Alerts when activated carbon needs replacement |
| Dry Pump Upgrade | Edwards nXDS10i dry scroll pump (replaces standard Edwards RV12 oil pump) | Cleaner, no oil maintenance |

### LC Technologies Model Comparison

| Feature | LC-100 | LC-180 | LC-200 |
|---|---|---|---|
| Glove ports | 2 | 4 | 4 |
| Users | 1 | 2 | 2 |
| Relative size | Standard | Longer | Double length |
| Atmosphere | <1 ppm O₂/H₂O | <1 ppm O₂/H₂O | <1 ppm O₂/H₂O |
| Material | Stainless steel | Stainless steel | Stainless steel |
| Made in USA | Yes | Yes | Yes |

> **Current preference**: LC-180 (slight lean per PI), but cost-dependent.

## Used and Refurbished Options

Used/refurbished gloveboxes can offer significant savings. Key marketplaces:

- [LabX](https://www.labx.com/categories/glove-boxes)
- [UsedGlovebox.com](https://usedglovebox.com/gloveboxes)
- [Machinio](https://www.machinio.com/)
- [Surplus Record](https://surplusrecord.com/machinery-equipment/glove-boxes/)
- [Federal Equipment](https://fedequip.com/inventory/glove-boxes)
- [eBay](https://www.ebay.com/sch/i.html?_nkw=vacuum+atmosphere+glove+box)
- [American Laboratory Trading](https://americanlaboratorytrading.com/)
- [BidService](https://bidservice.com/) (auction site — previously attempted)

### Used Market Price Ranges

| Brand | Basic/Older Unit | Full System (multi-port, purifier) | Notes |
|---|---|---|---|
| MBraun | $6K–$15K | $10K–$20K+ | Common in used market; Labmaster series popular |
| VAC (Vacuum Atmospheres Co.) | $4K–$10K | $10K–$15K+ | NEXUS DRI-TRAN models available |
| Innovative Technology | $5K–$15K | $10K–$20K+ | Often priced on request |
| LC Technology (used) | $10K–$17K | $15K–$25K+ | LC-200 seen at ~$17K used |

> **Note**: Used units may need new gloves, seals, purifier regeneration, or vacuum pump servicing. Budget an additional $2K–$5K for refurbishment and consumables. Confirm what is included (purifier, analyzers, pump, gloves) before purchasing.

### Previously Attempted Auction

A glovebox from [BidSpotter](https://www.bidspotter.com/en-us/auction-catalogues/bscbiditup/catalogue-id-bscbiditup10039/lot-7335ded1-8cfe-4927-ac47-b3ea012159f9) was identified but the bid was unsuccessful.

## Budget / Interim Options

For near-term use while awaiting a full glovebox, lower-cost acrylic options exist. These are **not** suitable for battery-grade (<1 ppm) work but can maintain 300–400 ppm O₂/H₂O.

### MSE Supplies Acrylic Gloveboxes

- **Website**: [msesupplies.com](https://www.msesupplies.com/collections/mse-pro-glove-boxes/acrylic-glovebox)

| Model | Airlock | Price | Notes |
|---|---|---|---|
| [Economy Compact 2-Port (with airlock)](https://www.msesupplies.com/products/mse-pro-economy-compact-laboratory-two-port-acrylic-glove-box-with-airlock-chamber-1) | Yes | ~$3,200 | Acrylic; 300–400 ppm O₂/H₂O minimum |
| [Compact 2-Port (without airlock)](https://www.msesupplies.com/products/mse-pro-compact-laboratory-two-port-acrylic-glove-box-without-airlock-chamber) | No | ~$1,400 | Just the chamber; needs pump, sensors |

> **Limitations**: Not suitable for corrosive organic reagents. Minimum achievable water and oxygen levels are 300–400 ppm. Requires separate vacuum pump, sensors, etc. Unclear if internal power outlet is available.

### Other Budget Vendors

| Vendor | Model | Price Range | Notes |
|---|---|---|---|
| [Cleatech](https://www.cleatech.com/product/laboratory-glove-box/) | S-2500 series (compact) | $1,100–$3,500 | Acrylic or PVC; N₂ purge capable; customizable |
| [Terra Universal](https://www.terrauniversal.com/glove-boxes-isolators.php) | ValuLine Portable | $1,250–$5,000+ | Plastic; N₂ positive pressure; optional airlocks |
| [Plas-Labs](https://www.thomassci.com/equipment/glove-boxes) | Basic Glove Box | $2,000–$5,000 (new) | Available used for $500–$2,000; N₂/Ar purge capable |

## Vendor Comparison Summary

| Category | Vendor/Option | Price Range | O₂/H₂O Level | Suitability |
|---|---|---|---|---|
| **New (professional)** | LC Technologies LC-100 | ~$34K | <1 ppm | ✅ Full workflow + battery |
| **New (professional)** | LC Technologies LC-180 | ~$47K–$50K | <1 ppm | ✅ Full workflow + battery |
| **New (professional)** | LC Technologies LC-200 | ~$50K–$54K | <1 ppm | ✅ Full workflow + battery |
| **Used (professional)** | MBraun / VAC / IT (used) | $4K–$20K+ | <1 ppm (with purifier) | ✅ If in good condition |
| **Budget (interim)** | MSE Supplies (with airlock) | ~$3,200 | 300–400 ppm | ⚠️ Powder storage only |
| **Budget (interim)** | Cleatech / Terra / Plas-Labs | $1,100–$5,000 | 100–500 ppm | ⚠️ Powder storage only |

## Safety Considerations

Handling flammable metal powders (Al, Mg) in a glovebox requires:

- **Inert gas**: N₂ or Ar atmosphere to prevent oxidation and ignition
- **Grounding/antistatic**: Static discharge can ignite metal powders; ensure glovebox and equipment are properly grounded
- **Class D fire extinguisher**: Must be accessible near the glovebox; standard (water, CO₂, ABC) extinguishers must NOT be used on metal fires
- **NFPA 652/484 compliance**: Combustible dust hazard analysis required
- **Proper PPE**: Flame-resistant lab coat; avoid synthetic clothing that generates static
- **HEPA filtration**: Consider for powder containment during handling
- **Ventilation**: Lab should have adequate air changes in case of glovebox breach

## Next Steps

- [ ] Schedule Teams call with LC Technologies to discuss final configuration
- [ ] Decide between LC-100 (2-port, ~$34K) and LC-180 (4-port, ~$47K–$50K)
- [ ] Determine whether optional accessories (auto antechamber, solvent sensor, dry pump) fit the budget
- [ ] Continue monitoring used glovebox market (LabX, Machinio, eBay) for potential deals
- [ ] Evaluate whether an interim budget glovebox (~$1K–$3K) is worth purchasing for near-term powder storage
- [ ] Coordinate with Barry Holman / Dave Laws regarding lab installation requirements (ventilation, electrical, etc.)
- [ ] Discuss with Gage Erickson on meeting setup per [Issue #29 comment](https://github.com/vertical-cloud-lab/byu-vcl/issues/29#issuecomment-4041885734)
