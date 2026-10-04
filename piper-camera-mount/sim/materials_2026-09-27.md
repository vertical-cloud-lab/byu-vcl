# Filament options for the PiPER wrist camera mount on a Bambu Lab H2D

Compiled 2026-09-27 (web research only). Every number carries its source.

- bambulab.com, wiki.bambulab.com and us.store.bambulab.com refuse automated fetches (HTTP 403/402). Values from those pages come through a mirror or a search snippet, and each is labelled as such.
- The Bambu datasheet (TDS) values below were read straight from the PDFs on Bambu's own CDN (`store.bblcdn.com` / `store.bblcdn.eu`), or from retailer copies of the same Bambu PDF.
- Prices come from the US store's Shopify product JSON (`bambulab-us.myshopify.com/products/<handle>.js`), fetched 2026-09-27.
- "X-Y" means the specimen was printed flat and loaded along the layers. "Z" means it was loaded across the layers, i.e. layer adhesion.

## 1. What the H2D can print

| Item | Value | Source |
|---|---|---|
| Max nozzle temperature | 350 °C | [3DPI spec reproduction](https://3dprintingindustry.com/news/bambu-labs-new-h2d-3d-printer-technical-specifications-and-pricing-237763/) (official [tech-specs page](https://bambulab.com/en/h2d/tech-specs) blocks fetches) |
| Chamber | **Active heating, max 65 °C** | same 3DPI page |
| Bed max | 120 °C | same 3DPI page |
| Nozzle as shipped | **Hardened steel**, 0.4 mm; 0.2/0.6/0.8 mm supported | same 3DPI page. A community post says the optional 0.2 mm is *not* hardened ([forum](https://forum.bambulab.com/t/does-the-h2d-come-with-hardened-steel-nozzles-or-not/183783), unverified). Check the installed nozzles' markings. |
| Filaments listed as supported | "PLA, PETG, TPU, PVA, BVOH, ABS, ASA, PC, PA, PET, Carbon/Glass Fiber Reinforced PLA, PETG, PA, PET, PC, ABS, ASA, **PPA-CF/GF, PPS, PPS-CF/GF**" | same 3DPI page. All ten materials in the table below are covered. PPS-CF is supported, but I did not retrieve its TDS (unverified). |
| AMS 2 Pro drying | Max **65 °C**, and "only achievable when the ambient temperature is ≥25 °C" | Bambu wiki [drying guide](https://wiki.bambulab.com/en/ams-2-pro/manual/drying-function) (search snippet only; page blocks fetches) |
| AMS HT drying | Max **85 °C**, 170 W heater, holds temperature at 10–25 °C ambient. "Some filaments require a drying temperature higher than 85 °C and may not be completely dried, such as PPS and PPA." | [3DPI](https://3dprintingindustry.com/news/bambu-labs-new-h2d-3d-printer-technical-specifications-and-pricing-237763/); [wiki drying guide](https://wiki.bambulab.com/en/ams-2-pro/manual/drying-function) (snippet) |

What this means for drying the nylons:
- PA6-CF, PA6-GF, PAHT-CF and PET-CF all ask for **80 °C, 8–12 h** (TDS links in the table). The AMS HT can do that. The AMS 2 Pro, capped at 65 °C, cannot.
- PPA-CF asks for **100–140 °C, 8–12 h** in a blast oven, or 110–120 °C for 12 h on a heatbed ([PPA-CF TDS](https://store.bblcdn.eu/s8/default/f592e57fe69c40289897513bdd2b61bc/Bambus_PPA-CF_Technical_Data_Sheet_2ab26420-79f5-4692-888e-090006814050.pdf)). No AMS reaches that, so it needs an oven, or the heatbed method on the H2D's 120 °C bed.
- Every engineering TDS says to print and store at **< 20 % RH**, sealed with desiccant.
- The nylon parts also re-absorb water after printing: saturated uptake is 0.88–2.56 % at 25 °C / 55 % RH (table below). Bambu gives no uptake-rate curve (unverified).

## 2. Comparison table (Bambu TDS values)

Moduli and strengths are in MPa and HDT is in °C. "a/b" means X-Y / Z. Standards used by Bambu:
- tensile: ISO 527
- flexural: ISO 178
- HDT: ISO 75, given as 1.8 MPa / 0.45 MPa
- water absorption: saturated at 25 °C, 55 % RH

The "Specimen state" column matters most for the nylons. Only PAHT-CF and PET-CF label their tables "Dry state". No sheet gives conditioned (wet) values.

| Material (TDS ver.) | Density g/cm³ | Tensile modulus X-Y / Z | Tensile strength X-Y / Z | Flex modulus X-Y / Z | Flex strength X-Y / Z | HDT 1.8 / 0.45 MPa | Tg (DSC) | Water abs. | Nozzle / bed / chamber °C | Drying | Specimen state | US price | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **PLA Basic** (V3.0) | 1.24 | 2580 / 2060 | 35 / 31 | 2750 / 2370 | 76 / 59 | **54 / 57** | 60 | 0.43 % | 190–230 / 35–45 / 25–45 | 50 °C, 8 h | annealed + dried 55 °C 8 h | $19.99 refill, $22.99 w/ spool per kg ([json](https://bambulab-us.myshopify.com/products/pla-basic-filament.js)). A [16 Sep 2026 forum post](https://forum.bambulab.com/t/filament-prices-drop-across-all-regions/259832) says the refill is now $15.99, which conflicts. | [TDS](https://store.bblcdn.com/s1/default/58b85d0f3db94878854a28fdb8a0006e/Bambu_PLA_Basic_Technical_Data_Sheet.pdf) |
| **PETG HF** (V1.0) | 1.28 | 1810 / 1540 | 34 / 23 | 2050 / 1810 | 64 / 48 | 62 / 69 | 66 | 0.40 % | 230–260 / 65–75 / 35–50 | 65 °C, 8 h | annealed + dried 75 °C 8 h | unverified (store handle not found). PETG *Basic* refill $13.99 per [forum 16 Sep 2026](https://forum.bambulab.com/t/filament-prices-drop-across-all-regions/259832) | [TDS](https://store.bblcdn.com/ce12d65176a94f1086e6aefa238e62e2.pdf) |
| **PETG-CF** (V3.0) | 1.25 | **2460 / 1340** | 35 / 29 | 2910 / 1560 | 70 / 48 | 68 / 74 | 68 | 0.30 % | 240–270 / 65–75 / 35–50 | 65 °C, 8 h | annealed + dried 65 °C 8 h | $34.99 w/ spool, $31.99 refill /kg ([json](https://bambulab-us.myshopify.com/products/petg-cf.js)) | [TDS (retailer copy of Bambu PDF)](https://3d.nice-cdn.com/upload/file/Bambu_PETG-CF_Technical_Data_Sheet_V2.pdf) |
| **PET-CF** (V3.0) | 1.29 | **4730 / 2160** | 74 / 35 | 5320 / 2210 | 131 / 49 | **182 / 205** | 75 | 0.37 % | 260–290 / 80–100 / 45–60 | 80 °C, 8–12 h | "Dry state"; annealed + dried 80 °C 12 h | $44.99 / 0.5 kg; **$84.99 / kg** ([json](https://bambulab-us.myshopify.com/products/pet-cf.js)) | [TDS (retailer copy)](https://cdn03.plentyone.com/ioseuwg7moqp/propertyItems/4493344/pet-cf%20tds.pdf); original on [wiki](https://wiki.bambulab.com/filament-acc/petcf-ppacf/07689de83afd4cc480f136c7697e6de3.pdf) |
| **PAHT-CF** (V2.0) | 1.06 | 3860 / **2180** | 88 / **64** | 4120 / 1680 | 140 / 68 | 170 / 194 | 70 | 0.88 % | 260–290 / 80–100 / 45–60 | 80 °C, 8–12 h | "Dry state"; annealed + dried 80 °C 12 h. Base is "PA 12 and other long-chain PA". V3.0 may add wet values; its wiki copy blocks fetches (unverified). | $49.99 / 0.5 kg; **$94.99 / kg** ([json](https://bambulab-us.myshopify.com/products/paht-cf.js)) | [TDS V2.0 (retailer copy)](https://www.machines-3d.com/images/Image/File/Fiches%20techniques/CONSOMMABLES/FILAMENTS%20BAMBU%20LAB/Bambu_PAHT-CF_Technical_Data_Sheet.pdf); V3.0 on [wiki](https://wiki.bambulab.com/filament-acc/asacf-pahtcf/65f1b18a6d6142d794a1a6a00f1496ef.pdf) |
| **PA6-CF** (V3.0) | 1.09 | 4430 / 2170 | 102 / 48 | 5460 / 2240 | 151 / 80 | 164 / 186 | 68 | **2.35 %** | 260–290 / 80–100 / 45–60 | 80 °C, 8–12 h | annealed + dried 80 °C 12 h, so these are dry values. A search snippet of Bambu's store page gives a wet X-Y flexural modulus of **3560 MPa**, 35 % below dry (unverified). | $42.99 / 0.5 kg; **$79.99 / kg** ([json](https://bambulab-us.myshopify.com/products/pa6-cf.js)) | [TDS](https://store.bblcdn.eu/s8/default/a64af9edb0f64095ad18bc4ad4faf1ec/Bambu_PA6-CF_Technical_Data_Sheet-v2.pdf) |
| **PA6-GF** (V1.0) | 1.14 | 2850 / 1950 | 75 / 27 | 3670 / 2300 | 120 / 51 | 158 / 182 | 67 | **2.56 %** | 260–290 / 80–100 / 45–60 | 80 °C, 8–12 h | annealed + dried 80 °C 12 h (dry) | **$59.99 / kg** ([json](https://bambulab-us.myshopify.com/products/pa6-gf.js)) | [TDS](https://store.bblcdn.com/s5/default/f0317db8b3f44d0486553c1e214cff9d.pdf) |
| **PPA-CF** (V1.0) | 1.25 | **11800 / 4300** | 168 / 57 | 9860 / 3240 | 208 / 63 | **196 / 227** | **85** | 1.30 % | 280–310 / 100–120 / **50–80** | **100–140 °C, 8–12 h** | **Not annealed**; printed on an X1C at a 52 °C chamber. Dry/wet state not stated. TDS: a 70–80 °C chamber gives "higher mechanical properties … especially the Z-direction's". Z elongation at break is only 0.9 %. | **$149.99 / 0.75 kg (= $199.99 / kg)** ([json](https://bambulab-us.myshopify.com/products/ppa-cf.js)) | [TDS](https://store.bblcdn.eu/s8/default/f592e57fe69c40289897513bdd2b61bc/Bambus_PPA-CF_Technical_Data_Sheet_2ab26420-79f5-4692-888e-090006814050.pdf) |
| **ASA** (V3.0) | 1.05 | 2450 / 2120 | 37 / 31 | 1920 / 1650 | 65 / 40 | 92 / 100 | n/a (Vicat 106) | 0.45 % | 240–270 / 80–100 / 45–60 | 80 °C, 8 h | annealed + dried 80 °C 12 h | **$29.99 / kg** ([json](https://bambulab-us.myshopify.com/products/asa-filament.js)) | [TDS](https://store.bblcdn.eu/s8/default/cad72d633f104a1aa80dc6c5937cb642/Bambu_ASA_Technical_Data_Sheet.pdf) |
| **PC** (V3.0) | 1.20 | 2110 / 1450 | 55 / 34 | 2310 / 1620 | 108 / 55 | 117 / 112 (as printed in the TDS, i.e. inverted, probably a typo) | **145** | 0.25 % | 260–280 / 90–110 / 45–60 | 80 °C, 8 h | annealed + dried 80 °C 12 h | **$39.99 / kg** ([json](https://bambulab-us.myshopify.com/products/pc-filament.js)) | [TDS](https://store.bblcdn.eu/s8/default/ab03007d58814bc28a08145719b552de/Bambu_PC_Technical_Data_Sheet.pdf) |

Annealing recipes from the same TDSs:

| Material | Recipe | Notes |
|---|---|---|
| PLA Basic | 50–60 °C, 6–12 h | |
| PETG HF | "not recommended" (75–80 °C, 4–8 h if you must) | |
| PETG-CF | 55–60 °C, 65–70 h | |
| PET-CF | 80–140 °C, 6–12 h | |
| PAHT-CF | 80–130 °C, 5–12 h | |
| PA6-CF / PA6-GF | 80–130 °C, 6–12 h | |
| PPA-CF | 120–140 °C, 6–12 h | "may deform, warp and get decreased in toughness" |
| ASA | 80–90 °C, 6–12 h | |
| PC | 85–100 °C, 6–12 h | |

Almost all of these carry the same warning: "some prints may deform and warp after annealing".

**Derived numbers** (my arithmetic from the table, not sourced). Stiffness ratio to PLA Basic, tensile modulus X-Y / Z:

| Material | X-Y / Z vs PLA Basic |
|---|---|
| PETG HF | 0.70 / 0.75 |
| PETG-CF | **0.95 / 0.65** |
| PET-CF | 1.83 / 1.05 |
| PAHT-CF | 1.50 / 1.06 |
| PA6-CF (dry) | 1.72 / 1.05 |
| PA6-GF | 1.10 / 0.95 |
| PPA-CF | **4.57 / 2.09** |
| ASA | 0.95 / 1.03 |
| PC | 0.82 / 0.70 |

Material cost for the ~70 cm³ print (density × $/kg):

| Material | Cost |
|---|---|
| PLA | ≈ $1.7 |
| ASA | ≈ $2.2 |
| PETG-CF | ≈ $3.1 |
| PC | ≈ $3.4 |
| PA6-GF | ≈ $4.8 |
| PA6-CF | ≈ $6.1 |
| PAHT-CF | ≈ $7.1 |
| PET-CF | ≈ $7.7 |
| PPA-CF | ≈ $17.5 |

Takeaways:
- **PETG-CF is not stiffer than PLA Basic.** It is about 5 % lower in X-Y and 35 % lower in Z, and its HDT is only 68 °C. It is a PETG, not an upgrade for pointing stability.
- **Across layers (Z), PET-CF, PAHT-CF and PA6-CF are only about 5 % stiffer than PLA** (2160–2180 vs 2060 MPa). The carbon fibre helps only where the load runs along the layers, so print orientation matters as much as the material.
- **PPA-CF is the only candidate that doubles the Z stiffness.**
- HDT at 1.8 MPa: PLA 54 °C, PETG HF 62 °C, PETG-CF 68 °C, ASA 92 °C, PC 117 °C, PA/PET-CF 164–182 °C, PPA-CF 196 °C.
- The high HDTs of PET-CF and the PA-CFs were measured on annealed-and-dried specimens (80 °C, 12 h). PPA-CF's were measured without annealing.
- PET-CF is semi-crystalline (crystallisation peak 130 °C, Tg 75 °C per its TDS). I infer, but have not verified, that an as-printed, un-annealed PET-CF part will sit much closer to its 75 °C Tg than to the 182 °C HDT.

## 3. Creep and preload relaxation data

**Bolted joints and inserts versus nut traps**

- **CNC Kitchen, M3 in PETG** (4 perimeters, 100 % infill, n = 3) ([blog](https://www.cnckitchen.com/blog/helicoils-threaded-insets-and-embedded-nuts-in-3d-prints-strength-amp-strength-assessment)). This is short-term strength only; nothing here depends on time.
  - Torque until the thread strips:

    | Method | Torque |
    |---|---|
    | Screw straight into plastic | 1 Nm |
    | Helicoil | 1 Nm |
    | Nut trap | **2 Nm** (the PETG crushes) |
    | **Heat-set insert** | **3 Nm** |

  - Pull-out force:

    | Method | Pull-out |
    |---|---|
    | Screw straight into plastic | 118 kg |
    | Insert | 119 kg |
    | Helicoil | 120 kg |
    | Nut in a side pocket | 86 kg |
    | **Nut in a bottom pocket** | **166 kg** |

  - Per that post, 1 Nm on an M3 already gives more than 1500 N of preload.
- **CNC Kitchen, PA6-CF vs PA12-CF, bolted joint over one week** (temperature not stated) ([blog](https://www.cnckitchen.com/blog/carbon-fiber-nylon-in-3d-printing-pa6-vs-pa12-tested)). This is the closest thing found to a preload-creep test on printed parts. It counts how often the bolts had to be re-tightened; it does not measure force.

  | Material | Re-tightening needed over one week |
  |---|---|
  | Unannealed PA6-CF | "almost every day" |
  | PA6-CF annealed 8 h at 110 °C | "slightly twice" |
  | **PA12-CF** | **once, after about half a week** |

  - Wet PA6 took up about 3 % water, kept 56 % of its dry strength, and bent about 3x as far (0.7 mm to about 2 mm).
  - PA12 took up about 0.7 %, lost 15 % of its strength, and its stiffness was essentially unchanged.
  - Bambu PAHT-CF is "PA 12 and other long-chain PA" ([TDS](https://www.machines-3d.com/images/Image/File/Fiches%20techniques/CONSOMMABLES/FILAMENTS%20BAMBU%20LAB/Bambu_PAHT-CF_Technical_Data_Sheet.pdf)), so it belongs to the better-behaved family.
- **Printed M12 bolts under temperature cycling (10 to 40 °C and 10 to 80 °C, preload on a load cell):** ABS held preload well and PLA poorly ([Eraliev et al. 2022, Appl. Sci. 12:3001](https://doi.org/10.3390/app12063001), abstract). The claim that "ABS loosened 2.5x less than PLA" is unverified.
- **Transverse vibration:** clamp force of printed bolted joints dropped by 10 % to more than 40 % after 200 cycles ([MATEC 2018](https://www.matec-conferences.org/articles/matecconf/abs/2018/44/matecconf_icpmmt2018_00029/matecconf_icpmmt2018_00029.html); unverified, page blocks fetches). This is a loosening mechanism for a moving robot wrist, not static creep.
- **MyTechFun creep and screw-joint test** (PLA, PETG, ASA, nylon; 2.5 Nm, checked from 10 h out to 6 days) ([link](https://www.mytechfun.com/video/143)). The numbers are only in a spreadsheet that could not be opened (unverified).
- A widely repeated claim of "3 % clamp-force loss for PLA and 11.5 % for PETG over 7 days" could not be traced to any primary source. Do not use it.

**Material creep and stress-relaxation studies**

| Study | Material(s) | Finding |
|---|---|---|
| [Bertocco et al. 2022, *Materials* 15:3509](https://doi.org/10.3390/ma15103509) | PLA | Room temperature, 500 s hold: modulus fell ≈ 13 / 11 / 13 % for 0° / 45° / 90° rasters. Thermal pre-treatment made the decay larger. |
| [Doğan 2022, SV-JME 68:451](https://doi.org/10.5545/sv-jme.2022.191) | ABS, CPE, PLA, tough PLA, PC, nylon | Tested at 25 / 40 / 60 °C and 10 / 20 MPa. The abstract says material, temperature and stress all matter significantly. The ranking (PC best, PLA worst) comes from a secondary summary (unverified). |
| [Dimitrellou et al. 2024, JMEP](https://doi.org/10.1007/s11665-024-09144-9) | PAHT-CF, PC, PLA | Per the abstract: **PAHT-CF > PC > PLA** in steady-state creep resistance. The abstract gives no numbers. |
| [Valvez, Silva & Reis 2022, *Aerospace* 9:124](https://doi.org/10.3390/aerospace9030124) | PETG vs PETG-CF, compression at 25 / 50 / 75 % of yield | Carbon fibre lowered compressive yield 9.9 % and raised compressive modulus 12.4 %, but **increased** stress relaxation and creep displacement compared with plain PETG. Carbon fibre in PETG does not help through-thickness clamp creep. |
| [Gebrehiwot et al. 2024, Composites Part C](https://www.sciencedirect.com/science/article/pii/S2666682024000999) | FFF CF-PET | Creep depends strongly on raster orientation (unverified, page blocks fetches). |

**Tg margins.** How much headroom each material has above a 25–40 °C service temperature (Tg is where creep takes off):

| Material | Tg | Source |
|---|---|---|
| PLA Basic | 60 °C | Bambu TDS |
| PETG HF | 66 °C | Bambu TDS |
| PETG-CF | 68 °C | Bambu TDS |
| PA6-CF | 68 °C, **dry** | Bambu TDS |
| PAHT-CF | 70 °C | Bambu TDS |
| PET-CF | 75 °C | Bambu TDS |
| PPA-CF | 85 °C | Bambu TDS |
| PC | 145 °C | Bambu TDS |
| Nylon 6, moisture-conditioned | ≈ 10 °C (vs ≈ 50 °C dry) | weak secondary source (unverified). [Reimschuessel 1978](https://doi.org/10.1002/pol.1978.170160606) documents the decline. |

Conditioned nylon 6 therefore sits *above* its Tg at room temperature, which fits CNC Kitchen's observation that wet PA6 lost about 2/3 of its stiffness.

**Rough stress under the screw head** (arithmetic, not sourced):

| Contact area | Bearing stress at 1500 N preload |
|---|---|
| M3 head, ≈ 5.5 mm OD on a 3.2 mm hole (≈ 16 mm²) | ≈ **95 MPa** |
| 7 mm washer (≈ 30 mm²) | ≈ **50 MPa** |

Both are well above the 10–20 MPa used in the creep studies and near the compressive yield of printed plastics. Whatever the material, preload will fade unless the design allows for it:
- use large washers;
- tighten to well under 1 Nm;
- re-torque after 1–2 days;
- or add spring (Belleville) washers so the joint tolerates some relaxation.

With PETG, the heat-set-insert and bottom-pocket nut results beat side-pocket nuts.

## 4. Practical notes: CF nylon and PET on Bambu machines

- **Chamber and warping.** Bambu's recommended chamber temperatures (TDS links in the table):

  | Material | Chamber |
  |---|---|
  | PETG-CF | 35–50 °C |
  | PET-CF, PA6-CF, PA6-GF, PAHT-CF, ASA, PC | 45–60 °C |
  | PPA-CF | 50–80 °C |

  - All of these fall within the H2D's 65 °C active chamber, except the top of PPA-CF's range.
  - Bambu's warp claims are only qualitative: PET-CF "maintain[s] the low warping and shrinkage of ordinary PET"; PAHT-CF has "a high-degree of dimensional stability"; PETG-CF "minimizes the risk of warping". I found no shrinkage percentages on any Bambu or Prusa page I could open (unverified). **Size the M3 nut traps and the 57 mm bore from a test coupon printed on the H2D in the chosen material.**
- **Anisotropy and layer adhesion.** Z tensile strength as a share of X-Y (TDS):

  | Material | Z / X-Y tensile strength |
  |---|---|
  | PLA Basic | 89 % |
  | ASA | 84 % |
  | PETG-CF | 83 % |
  | **PAHT-CF** | **73 %** (64 MPa, the highest absolute Z strength of any candidate) |
  | PC | 62 % |
  | PET-CF | 47 % |
  | PA6-CF | 47 % |
  | PA6-GF | 36 % |
  | PPA-CF | 34 % |

  Z elongation at break is 0.9 % for PPA-CF and 2.4 % for PET-CF, so both are brittle across layers. Keep clamp hoop stress and nut-trap wedging loads along the layers.
- **Supports.** Every engineering TDS gives a max overhang of about 70° and bridging of about 30–40 mm; PLA Basic is 55°. A 45° seat is inside that.
- **Annealing.** The recipes are in §2. No Bambu sheet quantifies the before/after change in HDT, strength or dimensions (unverified). All sheets warn that parts may deform. They require a forced-air (blast) oven, "a micro-wave oven or kitchen oven is not compatible". If you anneal, re-check the bore and nut traps afterwards.
- **Abrasion.** Bambu's CF/GF TDSs recommend a 0.6 mm nozzle (0.4 and 0.8 mm allowed) but do not name the nozzle material. Prusa states its PETG Carbon Fiber "requires a hardened nozzle" ([Prusament](https://prusament.com/materials/prusament-petg-carbon-fiber/)). The H2D ships with hardened steel ([3DPI](https://3dprintingindustry.com/news/bambu-labs-new-h2d-3d-printer-technical-specifications-and-pricing-237763/)). Treat every CF/GF option as hardened-nozzle only, and keep the A1 mini's stock nozzle away from them.
- **Moisture.**
  - Nylons: saturated uptake is PA6-CF 2.35 %, PA6-GF 2.56 %, PPA-CF 1.30 %, PAHT-CF 0.88 %.
  - Polyesters and PC: PET-CF 0.37 %, PETG-CF 0.30 %, PC 0.25 %.
  - Bambu says PAHT-CF is "optimized to retain excellent mechanical properties when wet", and calls PA6-CF ideal for parts "used in dry environments" (TDS text).
  - The only dry-vs-wet number for a Bambu grade is PA6-CF's flexural modulus, 5460 dry vs 3560 MPa wet (search snippet, unverified).
  - Independently, CNC Kitchen measured a conditioned PA6-CF at about 3 % water: it kept 56 % of its strength and about 1/3 of its stiffness. A PA12-CF at about 0.7 % water lost 15 % of its strength and kept its stiffness ([CNC Kitchen](https://www.cnckitchen.com/blog/carbon-fiber-nylon-in-3d-printing-pa6-vs-pa12-tested)).

## 5. Is carbon-fibre-filled plastic conductive enough to matter next to a Pi 5?

- Bambu's TDSs for PET-CF, PETG-CF, PAHT-CF, PA6-CF and PPA-CF give **no electrical data**. Neither does the Prusament PETG CF page.
- The one measured value for a comparable chopped-CF nylon: 3DXTech CarbonX CF Nylon (Gen3) has a **surface resistivity of 1E9 Ω** (IEC 62631-3-2) ([Material Data Center](https://www.materialdatacenter.com/ms/en/CarbonX/3DXTech/CarbonX%E2%84%A2+Carbon+Fiber+Nylon+(Gen3)/866b0ff6/7489)).
- An older 3DXTech catalogue lists >10^10 Ω/sq for CarbonX nylon and PETG ([DirectIndustry](https://pdf.directindustry.com/pdf/3dxtech/carbonx-carbon-fiber-reinforced-nylon-3d-filament/196785-750048.html); snippet only, unverified).
- For scale:
  - Markforged's ESD datasheet puts conductive below 10^4 Ω, static-dissipative at 10^4–10^11 Ω, and insulative above 10^11 Ω.
  - Its purpose-made **Onyx ESD** CF-nylon measures 10^5–10^9 Ω ([Markforged Onyx ESD datasheet](https://www-objects.markforged.com/craft/materials/Onyx_ESD_Supplemental_Datasheet.pdf)).
  - Purpose-made ESD PLA targets 10^4–10^9 Ω ([3DXSTAT ESD-PLA](https://www.3dxtech.com/products/3dxstat-esd-pla-1)).
- I found no forum or blog reports of chopped-CF prints shorting a board (unverified either way).
- My inference, not sourced: at about 10^9 Ω, 5 V drives only nanoamps, so a hard short is unlikely. Fibres are, however, exposed at cut surfaces and supported faces, and no Bambu grade has been measured. Keep the Pi on its M2.5 standoffs with the plate clear of the board, as the design already does. Or print the Pi plate in an unfilled material (PC, ASA or PETG) if you want zero doubt.

## 6. Shortlist (my synthesis from the sources above)

**(a) Clamp collar (bracket and carrier).** The deciding factors are sustained preload, nut traps, layer adhesion and warm air.

1. **PAHT-CF**
   - Best layer adhesion of the set: Z tensile 64 MPa (73 % of X-Y), Z modulus 2180 MPa.
   - HDT 170 °C (dry).
   - Water 0.88 %. It is PA12-based, and CNC Kitchen's PA12-CF needed only one re-tightening in a week, against daily for PA6-CF.
   - Ranked above PC and PLA for steady-state creep (Dimitrellou 2024).
   - $94.99/kg.
2. **PET-CF**
   - E 4730 / 2160 MPa (X-Y / Z).
   - HDT 182 °C (annealed specimen); Tg 75 °C.
   - Lowest water uptake of the CF options, 0.37 %.
   - $84.99/kg.
   - Weak across layers (Z tensile 35 MPa, 2.4 % elongation). Orient so hoop stress runs along the layers, and consider annealing at 80–140 °C.
3. **PPA-CF**
   - E 11800 / 4300 MPa.
   - HDT 196 °C unannealed; Tg 85 °C; water 1.30 %.
   - $199.99/kg.
   - Z elongation of only 0.9 % makes cracked nut traps a real risk. It also needs 100–140 °C drying (beyond the AMS HT) and a 50–80 °C chamber (the H2D maxes at 65 °C).
   - Non-CF budget alternative: **PC** (Tg 145 °C, water 0.25 %, $39.99/kg). It is no stiffer than PLA (2110 MPa), but has 85 °C more Tg margin.

**(b) Camera pod (45° seat).** The deciding factors are arc-minute pointing stiffness and warmth from the Pi.

1. **PPA-CF**
   - The only material that doubles PLA's stiffness in Z as well: E 11800 / 4300 MPa, i.e. 4.6x / 2.1x PLA.
   - Flex modulus 9860 MPa; HDT 196 °C.
   - The pod alone uses little filament, so the $199.99/kg matters less here.
2. **PET-CF**
   - E 4730 MPa X-Y (1.8x PLA), flex 5320 MPa.
   - HDT 182 °C.
   - Water 0.37 %, so its stiffness does not drift with humidity.
   - $84.99/kg.
3. **PAHT-CF**
   - E 3860 / 2180 MPa (1.5x / 1.06x PLA).
   - HDT 170 °C.
   - Holds its properties when wet.

**Avoid:**
- **PETG-CF** for stiffness. E_xy is 2460 MPa, below PLA's 2580, and HDT is 68 °C.
- **PA6-CF / PA6-GF** in an unconditioned lab. Water uptake is 2.35–2.56 %, wet PA6 loses about 2/3 of its stiffness (CNC Kitchen), and unannealed PA6-CF needed its bolts re-tightened daily.
- **CF on the Pi plate** unless it stays on standoffs (§5).
