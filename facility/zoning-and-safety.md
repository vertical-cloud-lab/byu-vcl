# Zoning, safety rules, safety systems, and what else a building needs

*If we were to build a facility like this* (the vertical cloud lab in the
[#303](https://github.com/vertical-cloud-lab/byu-vcl/issues/303) visualizations,
[PR #318](https://github.com/vertical-cloud-lab/byu-vcl/pull/318)):
- What zoning would it fall under in Utah?
- Which safety regulations apply, and which safety systems would we build in?
- Given about 20,000 ft² at 36 ft clear, what else should we look for in a building?

Gage asked these on [#343](https://github.com/vertical-cloud-lab/byu-vcl/issues/343). This builds on the codes in
[`README.md`](README.md#codes-that-decide-the-building) and the utilities in [`utilities.md`](utilities.md), and doesn't
repeat them.

Everything was read from public pages on 2026-11-12. **Nobody was contacted.** "(snippet)" marks a fact seen only in a
search result, and "mirror" a city code read on an unofficial copy. This is planning research, not legal or engineering
advice. For a real building, the city's building official and fire marshal, and a fire-protection engineer we'd hire,
would settle each point.

## Short answer

- **Zoning ([§1](#1-zoning-what-a-powder-lab-is-and-where-its-allowed)).**
  - **Utah leaves zoning to each city,** under Title 10 Chapter 20 of the Utah Code (Chapter 9a until November 2025).
  - **A lab like this is best described as research and development,** which is **permitted outright** in
    light-industrial, business-park and R&D zones in Lehi, Provo and Lindon. Spanish Fork, Saratoga Springs and Eagle
    Mountain list it too, though those were read only in search snippets or tables not fully checked.
  - **The risk is being read as manufacturing or foundry work**, which is conditional or heavy-industrial only, or
    running into a "no explosion hazard" performance standard, as in Provo. So ask the city for a written use
    determination before signing.
  - **In Utah a conditional use must be approved** if reasonable conditions can mitigate its effects.
  - **BYU would get no exemption** from city zoning.
- **Regulations ([§2](#2-safety-regulations-who-regulates-what)).**
  - **The city's building and fire codes do most of the work:** the occupancy (control areas or an H room), permits for
    dust, gases and hazardous materials with a management plan and inventory, and a dust hazard analysis.
  - **UOSH,** Utah's own OSHA plan: hazard communication, confined spaces, lockout, respirators, and OSHA's
    combustible-dust emphasis program.
  - **Utah DEQ:** probably no air permit; a hazardous-waste ID for spent IPA and powder waste; and Tier II reporting if
    the argon tank holds more than about 3,240 L, unless a research-lab exemption applies.
  - **The Labor Commission:** the compressed-air receiver, and perhaps the cryogenic tank, inspected every 48 months.
  - **CFATS** would cover 100 lb of aluminium powder, but it has lapsed since 2023.
- **Safety systems ([§3](#3-safety-systems-wed-build-in)).**
  - **For the powder:** a powder room on an exterior wall, inerted handling, dust collection outside, grounding, and
    Class D extinguishers and dry sand, never water.
  - **For the gases:** oxygen monitors, and the array's own gas suppression (argon rather than nitrogen where trays hold
    magnesium).
  - **For the rest:** robot guarding and emergency stops, standby power for exhaust and alarms, and remote alarms that
    put the lab in a safe state.
- **The ideal 20,000 ft², 36 ft building ([§4](#4-what-else-to-look-for-in-a-building)).**
  - **36 ft is enough:** 13 shorter Shuttles hold the same 352 trays.
  - **Then, roughly in order:** zoning that names R&D; **an end unit or a freestanding building** with a long exterior
    wall and a yard; **2,000-4,000 A at 480 V** already in; a **conventionally reinforced slab** we may cut, not a
    post-tensioned one; a **steel roof** that can carry fans; a documented ESFR system with fire flow to spare; a site
    **outside mapped fault and liquefaction zones**; a clean Phase I; and industrial neighbours.
  - **And a lease** that allows the hazardous materials, gives rights to the roof, slab and yard, allows round-the-clock
    operation, and offers the next 20,000 ft² first.

## 1. Zoning: what a powder lab is, and where it's allowed

**Utah has no state zoning category for a lab like this.** Each city zones its own land under the Municipal Land Use,
Development, and Management Act, which was renumbered in November 2025 from Title 10 Chapter 9a to **Title 10
Chapter 20** of the Utah Code ([crosswalk](https://le.utah.gov/lrgc/Recodification/Chapter_10_9a_Crosswalk.pdf?r=1)).
So the answer is city by city, and it turns on which *use* the city says we are.

### Which use we'd be

| How a city might read us | What the use tables call it | Where it's allowed | Does it fit? |
|---|---|---|---|
| **Research and development, or a laboratory** | "Research and development facilities and laboratories" (Lehi); "Research Services (including laboratories, scientific, medical, chemical, applied physics, mechanical…)" (Provo R&BP); "Research, Development, & Testing" (Lindon) | **Permitted** in light-industrial, business-park, R&D and technology zones | **The best fit.** The lab makes samples and data, not products for sale, and that is how to describe it |
| **Light manufacturing** | "Manufacturing, Processing, and Assembly" (Lehi); "Light manufacturing" (Provo R&BP) | Conditional or permitted in light-industrial zones | Possible, if a planner reads the atomizers and printers as production |
| **Foundry, smelting or metal processing** | "Nonferrous foundries… small item casting only" (Provo M1, conditional); smelting (Provo M2, conditional); "Metal & Minerals" (Lindon HI, conditional) | Heavy-industrial zones, often conditional | **The reading to head off.** Atomizing does melt metal, but about 100 g at a time ([the recorded mixture](../thermo-calc-100g-mixture-composition.md)), for research |
| **A use with an explosion hazard** | Not a use but a performance standard: Provo R&BP bars any use "dangerous… by reason of… fire, explosion", and Provo M1's purpose excludes uses with a "danger of explosion" | | Answer it with the fire code's controls (§3): control areas or an H room, inerted handling, a dust hazard analysis |

**So ask for a written use determination** for the exact address before signing, describing the lab plainly: research,
small batches, nothing made for sale, the powder quantities. Draft 3 asks Lehi; the same questions work for any city.

### What Utah law adds

- **A conditional use is a lower bar here than the name suggests.** Under
  [§10-20-506](https://le.utah.gov/xcode/Title10/Chapter20/C10-20-S506_2025110620251206.html) (formerly §10-9a-507),
  "a land use authority shall approve a conditional use if reasonable conditions are proposed, or can be imposed, to
  mitigate the reasonably anticipated detrimental effects", and mitigation "does not require elimination of the
  detrimental effects". It may deny only if the effects "cannot be substantially mitigated", and the decision is
  administrative, not a council vote. So a conditional use is a discussion about conditions: a screened gas pad,
  indoor work only, a hazardous-materials plan, night-time noise.
- **BYU would get no exemption.** [§10-20-304](https://le.utah.gov/xcode/Title10/Chapter20/C10-20-S304_2025110620251206.html)
  binds public bodies to city zoning, and [§10-20-305](https://le.utah.gov/xcode/Title10/Chapter20/C10-20-S305_2025110620251206.html)
  covers only land owned by the state or the United States. Nothing found exempts a private university, so the lab would
  follow city zoning whether BYU or a company ran it. (2025's SB 129 on higher-education development areas turned up
  and was not checked.)
- **Zoning doesn't regulate the hazard itself.** No Utah city was found that ties zoning to the building code's Group H
  or has a hazardous-materials overlay. The hazard is the building official's and the fire marshal's, under the codes
  in [§2](#2-safety-regulations-who-regulates-what). Some zones do add rules of their own, such as Provo M1's 25 ft
  setback for Class I flammable liquids.
- **Uses that aren't listed are not allowed** in Saratoga Springs, Orem and Vineyard (snippets). There the lab would need
  an unlisted-use ruling or a text amendment.

### City by city

Lehi is from the [README](README.md#zoning-what-lehi-allows). "Mirror" means read on zoneomics.com, an unofficial copy
of the city's code, because codepublishing.com and provo.municipal.codes returned HTTP 403. P is permitted, C is
conditional.

| City | Zones that fit | R&D or lab | Manufacturing | Watch for | Height | Source |
|---|---|---|---|---|---|---|
| **Lehi** | LI, BP, T-M, C-H; PC "Commercial, Flex" at Holbrook | **P** | C in LI, T-M and C-H | no row for hazardous materials or metal processing | LI 60 ft | [README](README.md#zoning-what-lehi-allows) (read) |
| **Provo** | R&BP Research & Business Park (ch. 14.44) | **P**: "Research Services", labs included | light manufacturing C; no "on-site milling, forging, or heavy grinding" | no use "dangerous… by reason of… fire, explosion"; noise 85 dBA by day, 55 dBA at night | 3 stories or 60 ft; 35 ft beside residential | [mirror](https://www.zoneomics.com/code/provo-UT/chapter_64) |
| Provo | M1 Light Manufacturing (ch. 14.27) | no R&D row; instrument manufacturing P | nonferrous foundries C, "small item casting only" | all work inside buildings; Class I flammables C, 25 ft from property lines; purpose excludes a "danger of explosion" | set by the IBC | [mirror](https://www.zoneomics.com/code/provo-UT/chapter_43) |
| **Lindon** | LI, R&B | **P** ("Research, Development, & Testing") | fabricated metal products C in LI, P in HI | industrial chemicals and explosives not allowed in any of these zones; "Metal & Minerals" C in HI only | not checked | [mirror](https://www.zoneomics.com/code/lindon-UT/chapter_10); which column is which zone not verified |
| Spanish Fork | I-1 Light, I-2 Medium | listed in I-1 and I-2 | I-1 covers "light manufacturing, assembling, warehousing" | a concrete plant needed a rezone from I-1 to I-2 | not verified | [ordinance](https://s3-us-west-2.amazonaws.com/municipalcodeonline.com-new/spanishfork/ordinances/documents/1762792970_EXE%20Ordinance%2017-2025%20to%20Amend%20Title%2015%20to%20Modify%20Regulations%20for%20Medical%20Cannabis%20Processing%20Facilities.pdf) (snippet) |
| Saratoga Springs | I, LI, BP and others (ch. 19.04) | P in 6 of 13 non-residential zones | light manufacturing P in 3 | LI is for manufacturing "predominantly from previously prepared materials"; unlisted uses not allowed | not found | [city PDF](https://www.saratogasprings-ut.gov/DocumentCenter/View/696/1904-Establishment-of-Land-Use-Zones-and-Official-Map) (read; which column is which zone not verified) |
| Eagle Mountain | Industrial (17.40); RTI overlay (17.48); Sweetwater Industrial overlay (17.53) | "Industrial (including research) Parks" P; R&D with light manufacturing P in both overlays | "clean advanced materials manufacturing" a special use in RTI | | RTI about 50 ft, more with approval ([README](README.md#land-for-a-purpose-built-building-with-a-high-bay)) | [17.40](https://codepublishing.com/UT/EagleMountain/html/EagleMountain17/EagleMountain1740.html), [17.48](https://www.codepublishing.com/UT/EagleMountain/html/EagleMountain17/EagleMountain1748.html) (snippet) |
| Orem | BP, M1, M2, CM | BP is "for scientific research, development and training", with manufacturing "incidental and accessory" | in Appendix A, not seen | unlisted uses not allowed | not verified | [mirror](https://www.zoneomics.com/code/orem-UT/chapter_9) (snippet) |
| Bluffdale | I-1 Light, I-2 Heavy | use table not seen | both cover "manufacturing, processing and warehousing" | | not verified | [ecode360](https://ecode360.com/50204794) (snippet) |
| American Fork | PI-1, I-1 | PI-1 described as for "office buildings, research…" (2024 minutes) | not verified | | not verified | [minutes](https://www.utah.gov/pmn/files/1160625.pdf) (snippet) |
| Springville | LIM, HIM | not seen | "Light Industry – Manufacturing Processes" row exists | | not verified | [code](https://www.codepublishing.com/UT/Springville/html/Springville11/Springville114.html) (snippet) |
| Herriman | M1 (Axia) | not checked | | | | [README](README.md#zoning-what-lehi-allows) |

**Not checked:** Draper (its code is on American Legal and was being updated in May 2026), Vineyard and Pleasant Grove,
and the use tables of American Fork, Springville, Orem and Bluffdale.

**The best fits so far** are zones that name research outright: Lehi's LI, BP and T-M and Holbrook's flex zone, Provo's
R&BP, Lindon's LI and R&B, and, from snippets, Spanish Fork's I-1 and Eagle Mountain's overlays. Provo's R&BP has the explosion standard and
a 55 dBA night limit, which matters for a lab that runs exhaust fans and chillers all night.

## 2. Safety regulations: who regulates what

Four public bodies set most of the rules: **the city** (building and fire codes, through permits), **UOSH** (workplace
safety), **Utah DEQ** (air, waste and chemical-inventory reporting) and **the Labor Commission's pressure-vessel
inspectors**. Consensus standards (NFPA, ANSI) come in through the codes, or as what inspectors measure against.

| Area | Who | The rule | What it means for this lab | Source |
|---|---|---|---|---|
| **Building and fire codes** | The city's building official and fire marshal | 2024 IBC and IFC with Utah amendments, and the 2023 NEC, from 2026-07-01 | A building permit for the fit-out. An occupancy decision: F-1/S-1 with control areas, or an H-2/H-3 room. IFC operational permits for combustible dust, compressed gases, cryogenic fluids and hazardous materials. A permit application includes a **Hazardous Materials Management Plan** and a **Hazardous Materials Inventory Statement** (IFC §5001.5.1-5001.5.2) | [README](README.md#codes-that-decide-the-building); [UpCodes](https://up.codes/viewer/utah/ifc-2024/chapter/50/hazardous-materials-general-provisions) |
| **Combustible metals** | The fire marshal, through the IFC | NFPA 484, which Utah's IFC still names; NFPA 660 replaced it in 2024 | **A dust hazard analysis**, done during design and before commissioning, "performed or led by a qualified person" (an outside firm is not required), and revalidated every 5 years | [README](README.md#codes-that-decide-the-building); [Processing](https://www.processingmagazine.com/material-handling-dry-wet/dust-control/article/55306953/nfpa-660-what-every-facility-needs-to-know-about-the-new-combustible-dust-standard) (snippet) |
| **Workplace safety** | **UOSH**, the Labor Commission's Occupational Safety and Health Division. Utah runs its own OSHA plan, so UOSH inspects, not federal OSHA | All of 29 CFR 1910, adopted by reference (R614-1-4) | The parts that matter are listed [below](#uosh-which-parts-of-29-cfr-1910-matter) | [OSHA](https://www.osha.gov/stateplans/ut); [R614-1-4](https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R614-1-4) |
| **Air** | Utah DEQ, Division of Air Quality | Small source exemption (R307-401-9): actual emissions under 5 tons a year each of PM10, VOC and the other criteria pollutants, and under 500 lb a year of any one hazardous air pollutant. Registration is optional | **Probably no air permit.** A filtered dust collector and modest IPA losses fit easily. Utah County is still a marginal nonattainment area for ozone, which would matter for IPA only near those limits. Ask DAQ how PM2.5 is counted, since the rule names PM10 | [R307-401-9](https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R307-401-9); [DAQ](https://deq.utah.gov/air-quality/new-source-review-exemptions-from-permitting-air-quality); [EPA Green Book](https://www3.epa.gov/airquality/greenbook/anayo_ut.html) |
| **Hazardous waste** | Utah DEQ, Division of Waste Management and Radiation Control | Generator size by monthly waste: up to 100 kg is a very small quantity generator, 100-1,000 kg small, over 1,000 kg large (40 CFR 262.13, adopted in R315-262). An EPA ID comes from Form 8700-12, filed online | **Spent IPA is D001** (ignitable). Waste fine powder and filter cake are probably D001 as well, and D003 (reactive) only if testing shows a violent reaction with water. The lab would likely be a very small or small generator | [DWMRC](https://deq.utah.gov/waste-management-and-radiation-control/hazardous-waste-management-program); [R315-262-18](https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R315-262-18) |
| **Wastewater** | The sewer district | Pretreatment rules for non-domestic wastewater | A survey with the business licence, perhaps a permit ([`utilities.md`](utilities.md#2-who-supplies-the-outside-utilities-by-city), draft 8) | |
| **Chemical inventory (EPCRA Tier II)** | Utah DEQ, with copies to the county's emergency planning committee and the fire department | 10,000 lb on site at any one time of any chemical OSHA calls hazardous. **Argon and nitrogen count** | **A bulk argon tank holding more than about 3,240 L of liquid (856 gal) crosses 10,000 lb.** A 6,000 L tank is about 18,500 lb; a full 3,000 L tank is about 9,260 lb, just under until two 230 L liquid cylinders join it. Liquid nitrogen crosses at about 5,600 L. Hundreds of pounds of powder is far below. Reports are due March 1 through Tier2 Submit, with no fee. **A possible exemption:** the law excludes any substance "to the extent it is used in a research laboratory" under "the direct supervision of a technically qualified individual" ([42 USC 11021(e)(4)](https://www.law.cornell.edu/uscode/text/42/11021)). Whether a bulk tank feeding an automated lab qualifies is DEQ's call; plan to report unless it says otherwise | [Utah DEQ](https://deq.utah.gov/environmental-response-and-remediation/cercla-comprehensive-environmental-response-compensation-and-liability-act/tier-2-chemical-inventory-program); [EPA](https://www.epa.gov/system/files/documents/2022-01/chapter-5-epcra-sections-311-and-312.pdf) |
| **Pressure vessels** | Utah Labor Commission's boiler and pressure vessel inspectors | Utah Code §34A-7-101 and R616-2: new vessels ASME-stamped and registered with the National Board, with a certificate of inspection; "all other pressure vessels" inspected externally every 48 months | **The compressed-air receiver** needs a certificate and the 48-month inspection. **A bulk cryogenic tank** looks in scope but isn't named, so ask the Division, and settle with the gas supplier who registers a tank it owns. DOT cylinders and dewars are exempt | [Compliance Manual rev. 15](https://laborcommission.utah.gov/wp-content/uploads/BLRCompManRev15Final-1.pdf); [R616-2-8](https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R616-2-8) |
| **Chemical security (CFATS)** | CISA | Aluminium powder is listed for theft, at 100 lb | **Nothing to file today:** the program lapsed on 2023-07-28 and no reauthorization was found (congress.gov not checked). If it returns, 100 lb or more of packaged powder means a Top-Screen within 60 days | [CISA](https://www.cisa.gov/resources-tools/programs/chemical-facility-anti-terrorism-standards-cfats); [CISA flyer](https://www.cisa.gov/sites/default/files/2023-05/flyer-cfats-aluminum-powder-508.pdf) (snippet) |
| **Shipping** | US DOT | Uncoated aluminium powder is UN1396, Division 4.3 (dangerous when wet). Hazmat employees are trained within 90 days of hire and every 3 years (49 CFR 172.704) | Anyone who packs or ships powder, or the hazardous waste, needs the training | [CAMEO](https://cameochemicals.noaa.gov/unna/1396) (snippet); [172.704](https://www.law.cornell.edu/cfr/text/49/172.704) |
| **Robots** | Consensus standards | ANSI/A3 R15.06-2025 (adopting ISO 10218-1/-2:2025) for robot cells; ANSI/A3 R15.08 parts 1-3 for industrial mobile robots | A risk assessment for every cell, fixed and mobile | [ANSI](https://blog.ansi.org/ansi/ansi-a3-r15-06-2025-robot-safety/); [A3](https://www.automate.org/store/products/ansi-a3-r15-08-american-national-standard-for-industrial-mobile-robots-imrs-imr-systems-and-imr-applications-safety-requirements-parts-1-2-and-3-pdf-download) (snippets) |
| **Lasers** | Consensus standard | ANSI Z136.1-2022 | The printers are Class 1 in normal use. Opening one for service exposes a Class 4 beam, which needs a laser safety officer and written procedures | [LIA](https://lia.org/node/29857) (snippet) |
| **If BYU runs it** | BYU Risk Management and Safety | BYU's lab safety plan and chemical hygiene plan, and the SOP and hazard-review forms used for CB 154 | The same review CB 154 went through, at a larger scale | [safety plan](../byu-engineering-lab-safety-plan-chemical-hygiene-plan-2024.pdf), [SOP template](../byu-engineering-sop-template.md), [hazard checklist](../byu-engineering-safety-and-health-hazard-checklist.pdf), [risk matrix](../byu-engineering-safety-and-health-risk-assessment-matrix-v2.pdf) |

### UOSH: which parts of 29 CFR 1910 matter

- **Hazard communication (1910.1200), not only the lab standard.** The lab standard (1910.1450) covers only "laboratory
  use": lab-scale containers, many chemicals, not part of or simulating a production process. Atomizing, printing, bulk
  powder and bulk gases fall under hazard communication: SDSs, labels and training. The etching and polishing bench may
  count as a laboratory, which needs a chemical hygiene plan, as CB 154 has
  ([1910.1450](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1450)).
- **Combustible dust:** OSHA's Combustible Dust National Emphasis Program (CPL 03-00-008, 2023-01-30) covers
  aluminium powder handling ([OSHA](https://www.osha.gov/combustible-dust/enforcement)). Housekeeping (1910.22) is
  where dust build-up is cited.
- **Confined spaces (1910.146):** a pit where argon can pool below 19.5 % oxygen is probably a permit-required confined
  space, needing a permit, an attendant and a rescue plan for every entry. Better to design it out.
- **Lockout/tagout (1910.147):** a written energy-control procedure for every robot, Shuttle, wire EDM, atomizer and
  printer.
- **Respirators (1910.134):** if anyone wears one for powder handling or filter changes, a written program, medical
  evaluation and fit testing.
- **Exposure limit:** aluminium metal dust, 15 mg/m³ total and 5 mg/m³ respirable, 8-hour average
  ([Table Z-1](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1000TABLEZ-1), snippet).

## 3. Safety systems we'd build in

A new warehouse shell comes with sprinklers, a fire alarm, exits and little else. Everything below would be ours to
build, and most of it is the same whichever building we pick. Where a line comes from the code it says so; the rest is
practice from the sources given. A fire-protection engineer would size all of it for a real building.

**What the powder is, by its own SDS.** The AlSi10Mg SDS in this repo
([PDF](../AlSi10Mg-sds-from-heegermaterials%20%5Bnot%20MSE%20supplies%5D.pdf)) classes the powder as a **flammable
solid (H228) that gives off flammable gas in contact with water (H261)**, storage class 4.3, and lists its 0.2-0.5 %
magnesium as pyrophoric in pure form. It says:
- fight fires with **Class D powder**, and *not* with water, CO₂ or Halon;
- clean up with an **explosion-proof vacuum with immersion filtration**, and never with compressed air;
- wear antistatic clothing, and keep eyewash stations and safety showers close.

GHS categories don't map one-to-one onto the fire code's classes (flammable solid, water-reactive Class 1-3), so the
fire marshal would class each powder from its SDS and any test data. The Aluminum Association's
[*Guidelines for Handling Aluminum Fines*](https://www.aluminum.org/sites/default/files/2021-11/Safe_Handling-Aluminum_Fine_Particles.pdf)
(F-1, 2008) is the industry's own short guide and is cited below as "AA F-1".

### Metal powder: fire and dust explosion

| Build in | Why, and the source |
|---|---|
| **A powder room on an exterior wall**, behind fire barriers. Below the quantity limits it is one of up to four control areas on the ground floor, with 1-hour barriers; above them it becomes a Group H-2 or H-3 room | IFC §5003.8.3 and Table 5003.8.3.2 ([UpCodes](https://up.codes/viewer/utah/ifc-2024/chapter/50/hazardous-materials-general-provisions)); H-room rules in [README](README.md#codes-that-decide-the-building). The figure already puts it on an outside wall |
| **Open powder only inside inerted enclosures** (gloveboxes, the atomizer's argon chamber) or under local exhaust | SDS: avoid dust clouds; IFC chapter 22 ([README](README.md#codes-that-decide-the-building)) |
| **Dust collectors outside the building**, or a listed wet-type collector indoors. Explosion venting or isolation on a dry collector. A wet collector interlocked so the process can't run without exhaust and water, and its sump vented for hydrogen when it stops | IFC chapter 22 ([README](README.md#codes-that-decide-the-building)); AA F-1 pp. 4-6 |
| **Housekeeping:** no more than 1/32 in of dust on any surface, cleaned with a vacuum built for combustible metal dust. Never compressed air, and never an ordinary shop vacuum | IFC chapter 22; SDS; AA F-1 p. 7 |
| **Ignition control:** every conductive part bonded and grounded, a static-dissipative floor and antistatic clothing, electrical gear rated for the area classification, non-sparking tools, hot-work permits | IFC chapter 22 and NFPA 70 ([README](README.md#codes-that-decide-the-building)); SDS; AA F-1 pp. 4, 6 |
| **Fire-fighting:** Class D extinguishers, and covered bins of dry sand (finer than 20 mesh) with long non-sparking shovels. No water, CO₂ or Halon on powder. NFPA 704 signs at the room, with the W symbol for water-reactive | IFC §906.3.4, which points to NFPA 10 ([UpCodes](https://up.codes/viewer/utah/ifc-2024/chapter/9/fire-protection-and-life-safety-systems)), and §5003.5 for NFPA 704 signs ([UpCodes](https://up.codes/viewer/utah/ifc-2024/chapter/50/hazardous-materials-general-provisions)); SDS; AA F-1 p. 7 |
| **A pre-plan with the fire department.** AA F-1 warns that outside firefighters "cannot be expected to be trained" for metal-dust fires, and a hose stream on powder raises a dust cloud and makes hydrogen | AA F-1 p. 7 |
| **Explosion control** (deflagration venting or prevention) for an H room, and **standby power** for its exhaust, alarms and detection | [README](README.md#codes-that-decide-the-building); IFC §5004.7, which points to §1203 |
| **A dust hazard analysis** before start-up | IFC chapter 22 requires one for a new facility ([README](README.md#codes-that-decide-the-building)); see [§2](#2-safety-regulations-who-regulates-what) |
| **A live inventory against the quantity limits.** The lab already tracks every jar ([`r8_store.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/cc31ddc/vertical-lab/r8_store.py): 204 feedstock jars and 377 atomized lots). Summing pounds by hazard class and control area gives the fire code's inventory statement, and can refuse a run that would push a room over its limit | IFC §5001.5.2 (HMIS); an idea, not a requirement |

### Water and aluminium make hydrogen

- **No water piping over powder,** and a room that keeps water out if water-reactive powder goes over its limit
  ([README](README.md#codes-that-decide-the-building)).
- **Sieves washed in IPA, not water,** in a closed, grounded vessel under extraction (DAL #234, as the
  [vertical-lab README](https://github.com/vertical-cloud-lab/byu-vcl/blob/cc31ddc/vertical-lab/README.md) records).
- **Wet sludge and polishing slurry** kept in vented containers and settled before anything reaches a drain
  ([`utilities.md`](utilities.md)).

### Argon and nitrogen: running out of oxygen

- **Oxygen monitors** wherever argon or nitrogen can collect: the powder room, the gloveboxes, the gas-pad entry and any
  pit. Argon is about 1.4 times as dense as air, so it pools low; put sensors and exhaust pick-ups near the floor. Have
  each monitor alarm locally and remotely and start the exhaust. Indoors the fire code asks for ventilation or gas
  detection, and accepts an oxygen-depletion alarm instead where approved (IFC §5307.2-5307.2.1,
  [README](README.md#codes-that-decide-the-building)).
- **A pit under the array would probably be a permit-required confined space** if a person ever had to go in
  ([§2](#2-safety-regulations-who-regulates-what)). Better not to have one, which is one more reason for the shorter
  units under 36 ft.
- **The bulk tank outside**, at the code's setbacks, with relief valves, an emergency shut-off where the line enters the
  building, labelled piping, and every cylinder chained (IFC §5303.5.3, [README](README.md#codes-that-decide-the-building)).
- **The array's own gas suppression** floods its units on a fire. It needs a pre-discharge alarm and a lockout for
  maintenance. Kardex's ENGEL system uses nitrogen. **Trays holding magnesium powder are an exception:** burning
  magnesium reacts with nitrogen and CO₂, and only argon makes an inert blanket
  ([arbeitssicherheit.de](https://www.arbeitssicherheit.de/schriften/dokument/0:9606814,18.html), snippet), so ask
  Kardex and Fike about argon (IG-01) for those units.

### Fire: the building and the array

- **The building's sprinklers,** extended into every lab room. See [§4](#4-what-else-to-look-for-in-a-building)
  on ESFR heads and obstructions.
- **The array:** its own suppression (above), aspirating smoke detection inside the units, and automatic shut-down on
  fire detection or sprinkler flow, plus a manual emergency stop (IFC §3209, [README](README.md#codes-that-decide-the-building)).
- **A fire alarm monitored round the clock,** reporting into the lab's own dashboard as well.

### Robots and machines

- **A risk assessment for every cell,** to the robot standards in [§2](#2-safety-regulations-who-regulates-what): guarding
  or area scanners for the fixed arms, power-and-force limits for the cobots, and speed and separation rules for the
  mobile robots.
- **One emergency-stop network across the floor,** with interlocked doors on every cell, and a lockout point for each
  machine and tray.
- **The Shuttles' own guarding** at their access openings, to the standards PR #331's
  [`build_our_own_vlm.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/685216e/vertical-lab/procurement/build_our_own_vlm.md)
  lists: EN 15095 for storage lifts, ISO 13849 for safety controls and NFPA 79 for machine wiring.

### Lasers, heat and molten metal

- **The printers are Class 1 enclosures** around Class 4 lasers. Servicing with the beam exposed needs a laser-controlled
  area and a laser safety officer ([§2](#2-safety-regulations-who-regulates-what)).
- **Furnaces and the atomizers' melts:** keep chilled-water lines and their fittings away from molten metal, with leak
  detection, since water under molten metal flashes to steam.

### Chemicals

- **Ducted fume hoods.** The lab already dropped Keller's reagent (it contains HF) for Weck's reagent, an HF-free tint
  etch ([vertical-lab README](https://github.com/vertical-cloud-lab/byu-vcl/blob/cc31ddc/vertical-lab/README.md)).
- **IPA in flammable-liquid cabinets,** well under its 120 gal limit per control area
  ([README](README.md#codes-that-decide-the-building)).
- **Eyewash stations and safety showers** (the SDS asks for them), spill kits, and a waste accumulation area.

### Electrical and seismic

- **An arc-flash study and labels** (NFPA 70E) once the switchboard is in, and ground-fault protection near water.
- **Everything tall anchored:** the Shuttles, racks, tanks and cylinders. The code requires shelving for hazardous
  materials to be braced and anchored to the IBC's seismic rules (IFC §5003.9.9), and the site is Seismic Design
  Category D ([README](README.md#codes-that-decide-the-building)).

### Running it remotely

A cloud lab's own safety rules, beyond the code:
- **Safety functions stay local and hard-wired.** A remote user can't override a stop, open an interlocked door, or
  restart after an alarm; that takes a local reset.
- **Alarms go to people on call** (oxygen, smoke, gas, dust collector, power) and to the lab's dashboard. The stream
  cameras let someone look before anyone walks in.
- **Every alarm drives a safe state:** stop atomizing, close the gas valves, park the robots, keep the exhaust running.
- **Someone reachable round the clock** when it runs lights-out, and a key box for the fire department.

## 4. What else to look for in a building

**36 ft clear is enough.** Gage's contact at Newmark Mountain West says 36 ft is usually the most these buildings
offer, which matches #344: nothing near BYU is listed taller. Under 36 ft the array becomes 13 Shuttles at 10.5 m
instead of 8 at 15.15 m, for the same 352 trays on about 1,700 ft² ([README](README.md#height)). And 20,000 ft² holds
the #318 floor, the array and the support rooms ([README](README.md#floor-area)). So height and area are settled, and
the rest decides between buildings.

Roughly in order of how hard each is to change later:

| Look for | Ideal | Why | How to check |
|---|---|---|---|
| **Zoning** | R&D or labs permitted outright, light manufacturing at least conditional, no homes next door | [§1](#1-zoning-what-a-powder-lab-is-and-where-its-allowed). Zones get stricter next to homes: Provo's R&BP drops from 60 ft to 35 ft beside residential, and limits noise to 55 dBA at night | the city's zoning map, then a written use determination |
| **Where the space sits** | **An end unit or a freestanding building**, with a long exterior wall and a yard beside it | An H room needs at least 25 % of its perimeter on an exterior wall, and an H-2 room over 1,000 ft² must be 30 ft from lot lines ([README](README.md#codes-that-decide-the-building)). Explosion vents, the dust collector, the gas pad, a generator and chillers all want an outside wall or yard. A middle bay has two shared walls | the site plan |
| **Power** | 2,000-4,000 A at 480 V already in, with room for another transformer | Switchgear and transformers take 30-80 weeks ([README](README.md#3-renovate-or-build), [`utilities.md`](utilities.md#4-rough-costs-and-lead-times-for-what-wed-build)) | the switchboard's nameplate |
| **The slab** | Conventionally reinforced, at least 6-7 in, and **not post-tensioned**, with the landlord's consent to cut it | We'd cut trenches for drains and conduit, and pour thicker footings under the Shuttles and the wire EDM. Post-tensioned tendons are stressed to 30,000 psi or more and a cut one "recoils violently"; ground-penetrating radar is the reliable way to find them ([GPRS](https://www.gp-radar.com/article/how-to-safely-saw-or-drill-into-concrete-in-post-tensioned-slabs)) | the structural drawings, warning stamps at the slab edge, a GPR scan |
| **The roof** | Steel joists and metal deck (Type IIB), able to carry exhaust fans and make-up air units, or ground space for them | Warehouse roofs usually can't carry heavy lab equipment, so new columns may be needed ([BD+C](https://www.bdcnetwork.com/3-key-considerations-when-converting-warehouse-laboratory)). A panelized wood roof (Type IIIB) is about 15 % cheaper to build and so common ([WoodWorks](https://www.woodworks.org/resources/why-consider-panelized-wood-roof-system-for-commercial-buildings/), snippet), and adds fuel overhead. It barely changes how big an H room may be: IBC Table 506.2 (the 2021 edition, as Washington prints it) allows 7,000 ft² of H-2 in either type, and 14,000 or 13,000 ft² of H-3 ([WAC 51-50-0506](https://lawfilesext.leg.wa.gov/law/WACArchive/2022/pdf/WAC%20%2051%20%20TITLE/WAC%20%2051%20-%2050%20%20CHAPTER/WAC%20%2051%20-%2050%20-0506.pdf), snippet) | the drawings; a structural engineer's roof check |
| **Sprinklers and water** | A documented ESFR system, enough fire flow at the street, and riser capacity for new branch lines | ESFR heads are sensitive to anything under them. Ducts and cable trays wider than 24 in in higher-hazard areas need sprinklers beneath (NFPA 13-2025 §14.2.10.3, per [MeyerFire](https://www.meyerfire.com/daily/sprinklers-reqd-for-large-ducts-gt31-below-esfr), a forum reading); open mezzanines over 4 ft wide need sprinklers below and a water shield ([PHC Pros](https://phcppros.com/articles/11344-are-esfr-sprinklers-ok-part-ii-obstructions)); and where ESFR meets ordinary sprinklers, a 2 ft draft curtain ([quick reference](https://a-us.storyblok.com/f/1014675/x/1550ab1ef8/obstructions-esfr-quick-reference-3.pdf), snippet). Lab rooms with their own ceilings will very likely need their own heads (not confirmed) | the sprinkler drawings and hydraulic placard; the fire flow from the city |
| **Geology** | Outside the mapped surface-fault-rupture and high-liquefaction areas, with a geotechnical report | Tall, heavy Shuttles on a slab. The Wasatch fault's Provo and Salt Lake City segments meet at Point of the Mountain (Bluffdale, Draper) in a network of surface traces ([Frontiers 2021](https://www.frontiersin.org/articles/10.3389/feart.2021.607018), snippet). Liquefaction is likeliest along rivers and the lake shore ([UGS PI-28](https://ugspub.nr.utah.gov/publications/public_information/pi-28.pdf), snippet). Draper and Provo have geologic-hazard ordinances (snippets) | the [UGS Geologic Hazards Portal](https://geology.utah.gov/apps/hazards/) at the address |
| **Environmental history** | A clean Phase I environmental site assessment | Under EPA's All Appropriate Inquiries rule (40 CFR 312) and ASTM E1527-21, a Phase I done before acquiring is what protects a buyer from an earlier owner's contamination under CERCLA ([EPA](https://www.epa.gov/brownfields/brownfields-all-appropriate-inquiries)). For a tenant it records the baseline, so we aren't blamed for it at the lease's end ([Mintz](https://www.mintz.com/insights-center/viewpoints/2016-02-life-sciences-lease-marathon-not-sprint), [Torys](https://www.torys.com/en/our-latest-thinking/publications/2022/07/strategies-for-life-science-leasing)) | a Phase I before signing |
| **Neighbours** | Industrial neighbours; no food, childcare or homes in the building | A lab wants protection from other tenants' materials ([Mintz](https://www.mintz.com/insights-center/viewpoints/2016-02-life-sciences-lease-marathon-not-sprint)), and neighbours are who complains about fans at night | the tour |
| **Columns, doors, docks** | 50 ft or more between columns; two dock-high doors and one grade-level door of at least 14 × 16 ft | Robot paths and the array's rows; the EOS and the Meltio cell arrive whole ([README](README.md#everything-else-a-building-has-to-provide)) | the listing |
| **Office and restrooms already built** | About 1,500-2,500 ft² (*estimate*) | Saves part of the fit-out | the tour |
| **Utilities an earlier tenant left** | A gas pad, compressed-air lines, a generator, exhaust fans | [`utilities.md`](utilities.md#5-what-to-look-for-on-a-tour) | the tour |
| **Location** | Within about 30 minutes of BYU, near I-15 and a FrontRunner station, with two fibre carriers | Students and staff commute; a cloud lab needs its network ([`utilities.md`](utilities.md)) | a map |

### Lease terms worth asking for

A tenant fit-out this large only makes sense with terms that protect it. From
[Mintz](https://www.mintz.com/insights-center/viewpoints/2016-02-life-sciences-lease-marathon-not-sprint) and
[Torys](https://www.torys.com/en/our-latest-thinking/publications/2022/07/strategies-for-life-science-leasing), on
life-science leases, plus what this lab needs:
- **The permitted use written into the lease:** research with the listed hazardous materials, under a management plan.
- **Restoration limited and listed up front.** It is "heavily negotiated"; spell out which equipment comes out at the
  end, so the gas piping and electrical service can stay.
- **Rights to the roof, the slab and the yard:** rooftop fans, saw-cutting, a gas pad and a dust collector outside.
- **Round-the-clock operation,** and access rules that don't need the landlord present.
- **A term long enough to pay off the fit-out** (7-10 years with renewal options, *estimate*), a TI allowance (Colliers
  puts it at $10-15/ft², [README](README.md#3-renovate-or-build)), a **right of first offer on the next 20,000 ft²**,
  and if possible an option to buy.
- **An exit report** by a licensed environmental professional, matched against the Phase I baseline (Torys).

The tour list in [`utilities.md`](utilities.md#5-what-to-look-for-on-a-tour) covers utilities. Add to it: the slab
(drawings and stamps), the roof structure, the sprinkler placard, whether the space is an end unit, and who the
neighbours are.

## 5. Who to ask, and what's not done

None of these has been contacted. Drafts 10 and 11 are new in [`drafts.md`](drafts.md).

| Who | For | Public contact | Draft |
|---|---|---|---|
| **City planning offices** (Lehi first, then Provo, Lindon, Spanish Fork and the rest) | a written use determination for an address | the cities' sites; Lehi's is in the [README contacts](README.md#contacts) | 3 |
| **A fire-protection engineer or code consultant**, for example: Resolut, a Utah engineering firm formed when VBFA and BNA merged in March 2025, which lists fire protection; Jensen Hughes, which offers code consulting and dust hazard analyses and was hiring to open a Salt Lake City office (snippet); Trinity Consultants, Salt Lake City, for air permits and combustible-dust risk | a code review of one building, and the dust hazard analysis | [Resolut](https://www.resolutgroup.com/) (+1 801 530 3148 on its site); [Jensen Hughes](https://jensenhughes.com/services/combustible-dust-safety); [Trinity](https://trinityconsultants.com/locations/north-america/united-states/utah/salt-lake-city) | 10 |
| **Gage's contact at Newmark Mountain West** | buildings that fit [§4](#4-what-else-to-look-for-in-a-building), on or off market | through Gage | 11 |
| **Utah DEQ:** Air Quality, Waste Management and Radiation Control, and the Tier II program | how PM2.5 counts toward the air exemption; generator status; whether the research-lab exemption covers a bulk tank | [deq.utah.gov](https://deq.utah.gov/) | none |
| **Labor Commission,** boiler and pressure vessel inspectors | whether a cryogenic tank needs a certificate, and who registers a supplier's tank | [Compliance Manual](https://laborcommission.utah.gov/wp-content/uploads/BLRCompManRev15Final-1.pdf) | none |
| **BYU Risk Management and Safety** | if BYU runs the lab | the CB 154 forms in this repo | none |

**Not done, or not verified:**
- **Zoning:**
  - not read: Draper, Vineyard and Pleasant Grove, and the use tables of American Fork, Springville, Orem and Bluffdale;
  - not verified: which column is which zone in Lindon's and Saratoga Springs' tables;
  - Provo's was read on a mirror, not the city's site, which returned HTTP 403.
- **Codes:**
  - NFPA 660's own text (the dust-hazard-analysis clause and any grace period) and NFPA 484's building chapter;
  - whether lab rooms under ESFR need their own sprinklers. Very likely, but not confirmed.
- **Site:**
  - liquefaction ratings city by city (UGS PI-28 is a scanned map);
  - how common post-tensioned slabs are in Utah tilt-ups.
- **Regulators:**
  - whether a cryogenic tank needs a Utah pressure-vessel certificate;
  - whether Tier II's research-lab exemption covers us;
  - whether a very small generator must notify in Utah.
- **CFATS:** its status was checked on CISA's page, not against congress.gov.

Add sites, contacts and numbers on [#343](https://github.com/vertical-cloud-lab/byu-vcl/issues/343).
