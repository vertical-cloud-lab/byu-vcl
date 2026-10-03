Question: # Question

**Which physical objects should go into a benchmark "sandbox" for a low-cost 6-DOF arm in a materials self-driving lab? We want a literature-grounded, specification-level object set — the laboratory analogue of the YCB Object and Model Set — together with the holders and fixtures each object needs.**

This is the fifth in a sequential series of high-effort scans for a university materials-science self-driving lab (Vertical Cloud Lab, BYU Mechanical Engineering). Treat the findings below as established and do **not** re-derive them:

- **Q1:** every deployed arm-based SDL uses an expensive industrial arm as a transfer/logistics layer between stations (KUKA KMR-iiwa at Liverpool, ABB YuMi for PXRD, Franka Research 3 for powder scooping, Denso COBOTTA at NIMS). No published SDL runs on a sub-US$5k arm. Per-operation reliability is the binding constraint and is essentially unreported.
- **Q2:** a zero-failure 95% one-sided reliability claim needs ~119 operations for p ≥ 0.975 and ~1,497 for p ≥ 0.998.
- **Q3:** fixtures provide the precision seat and passive compliance (1–2 mm lead-in chamfers at 15–30°, ≥1 mm design clearance) substitutes for arm precision; "tag the fixture, not the part"; transparent glass, specular aluminium, and thin near-planar parts are the object classes vision handles worst.
- **Q4:** **no published physical laboratory-object manipulation benchmark exists.** YCB's 77 consumer objects contain no SEM stubs, vials, well plates, or crucibles, and the laboratory benchmarks we know of (Labimus, autobio-bench, Chemistry3D-style suites) are simulation-only. Q4 proposed that our object set would be the first physical one.

## The sandbox

- **Arm:** AgileX PiPER — 6-DOF, 1.5 kg payload, 626 mm reach, vendor-claimed ±0.1 mm repeatability (unverified). Stock two-finger parallel gripper: **0–70 mm opening** (a 100 mm variant exists), **40 N rated / 50 N max** grip force, ±0.5 mm gripper repeatability.
- **Cell:** a table-top enclosure about 1 m tall, a Raspberry Pi HQ camera on the wrist (fixed-focus C/CS-mount lens), AprilTags on printed PETG fixtures, and a Bambu A1 mini beside it printing fixtures and custom fingers.
- **Workflows the sandbox must rehearse:**
  - **Ultrasonic atomization** (AMAZEMET rePOWDER): feedstock "cups" machined from 20 mm OD aluminium rod, bored ~76 mm deep, filled with metal powder and capped with a press-fit aluminium plug, then transferred into the atomizer crucible (20 mm OD maximum).
  - **Powder dosing** (in-house auger doser): cohesive AlSi10Mg (15–45 µm) and Si powders dispensed into an aluminium crucible on an analytical balance; static charge is an open question.
  - **Characterization:** SEM pin stubs, DSC-style aluminium pans with press-fit lids, XRD/XRF sample cups, and 3D-printed tensile/impact coupons that must seat in test grips.
  - **Liquid handling** on an Opentrons OT-2: SBS-footprint well plates, tip racks, and reservoirs, plus a colour sensor that reads well plates.
  - **Vials** from 2 mL HPLC to 20 mL scintillation, both empty and filled (liquid and powder).

## What we need

### 1. A census of what SDL arms actually manipulate

Across published arm-based SDLs and laboratory-automation systems, 2018–2026 — for example A-Lab (Szymanski et al. 2023), the Liverpool mobile robotic chemist (Burger et al. 2020; Dai et al. 2024), Ada (MacLeod et al.), Polybot, the YuMi PXRD workflow (Lunt et al. 2024), NIMS COBOTTA synthesis, vision-guided powder scooping on a Franka (Radulov et al. 2026), RoboChemist, ORGANA, CRESt, and mobile manipulators serving XRD/NMR/UPLC — tabulate which **object classes** each system's arm handles: vials by nominal volume, caps and septa, well plates, tip racks, crucibles by material and size, XRD holders, NMR tubes, cuvettes, SEM stubs, substrates/wafers/coupons, coin cells, weighing boats, spatulas and scoops, instrument doors/drawers/buttons, racks and trays. Record which gripper or finger solution handled each. **Which 10–15 object classes account for most arm operations in the published record?**

### 2. Specifications and governing standards per object

For each class: nominal dimensions and tolerances, mass empty and filled, material and surface finish, and the governing standard. For example ANSI/SLAS 1-2004 through 4-2004 (microplate footprint, height, flange, well positions); vial neck finishes (9 mm short-thread, GPI 8-425, 13-425, 15-425, 20-400, 24-400); SEM stubs (Ø12.7 mm standard pin stub with 3.2 mm pin vs. Ø25/32 mm, JEOL/Hitachi cylinder mounts); DSC/TGA pans and lids (TA Tzero, Mettler 40 µL, Netzsch) including any published crimp/press forces; test coupons (ASTM E8/E8M subsize, ASTM D638 Type IV/V, ISO 527-2 1BA/1BB, ASTM E23 Charpy 10×10×55 mm, ASTM D256 Izod); metallographic mounts (25/30/32/40 mm); XRD holders (zero-background Si plates, back-loading cups); CR2032 coin cells. **Where does vendor-to-vendor variation exceed ~0.5 mm**, enough to break a 1–2 mm-clearance printed fixture?

### 3. Property axes that stress manipulation, and minimum coverage

Which object properties most predict grasp or placement failure, in the lab literature and the general manipulation literature? Candidates: size extremes (≤5 mm features; ≥128 mm plates, which exceed a 70 mm gripper); mass and centre-of-gravity shift with fill state; liquid slosh; powder spill; transparency and refraction; specular metal; thin near-planar parts (<2 mm); crushable parts (Al pans, weighing boats, thin-wall tubes); two-part objects (caps, lids, press-fits, threads); and objects that must seat in a fixture (peg-in-hole analogues). **Propose a coverage matrix in which every axis is exercised by at least two objects**, and say which candidate objects are redundant.

### 4. How benchmark object sets were chosen, and what they ship with

How did YCB, the NIST assembly task boards, the ACRV/Amazon picking sets, RB2, Peg-in-Bench, the Cross-Embodiment Gripper Benchmark, and any lab-automation set choose their objects — coverage, cost, availability, durability, portability, standardization, non-perishability? What must ship with each object for reproducibility (meshes or scans, mass, friction, canonical poses, supplier part number, lot)? How do they handle consumables that deform or are single-use, such as a press-fitted lid, a crimped DSC pan, or a pierced septum?

### 5. Fill surrogates and safety

What do published lab-robotics studies use as fill surrogates — water vs. glycerol–water for viscosity, dyed liquids for vision, inert powders (alumina, glass beads, sand, lactose, microcrystalline cellulose) vs. real metal powders? Which flowability measures (Hausner ratio, Carr index, angle of repose, cohesion) should a surrogate match to stand in for cohesive AlSi10Mg or Si? What fill-level, cap, and spill-containment conventions are used in filled-vial manipulation benchmarks?

### 6. Holders and fixtures

For each object, what holder is standard (SBS-footprint vial racks, multi-stub SEM holders, DSC autosampler trays, crucible trays, coupon grips)? Which are commercially available and which must be printed? Are there published printable labware fixture libraries, e.g. custom Opentrons labware definitions or SLAS-footprint adapters?

## Deliverable

A tiered list we could buy this month:

- **Tier 1, core (~12–20 items):** the minimum set that covers the property axes and the in-house workflows above.
- **Tier 2, extension:** objects that broaden coverage toward other SDLs, so our results are comparable.
- **Tier 3, defer or avoid:** with the reason.

For each item give: a generic specification (dimensions, mass empty/filled, material), a representative commercial source or standard, approximate unit cost, quantity to stock, which primitive(s) it exercises (pick, place, seat/insert, press-fit, uncap/recap, pour/scoop, open/close a door or drawer), which property axis it covers, and what fixture it needs. Be quantitative and cite specific papers. Flag where you are extrapolating, and state plainly what the literature does not contain.


# A Literature-Grounded Benchmark Object Set for a Low-Cost 6-DOF Arm in a Materials Self-Driving Laboratory

## 1. Census: What SDL Arms Actually Manipulate

Across published arm-based SDLs (2018–2026), vials and sample racks are by far the most frequently handled object class. The Liverpool mobile robotic chemist (KUKA KMR-iiwa with a Festo HGPLE 14 parallel gripper) manipulates 10 mL Agilent GC vials, custom 18-well racks, filtration funnels, solid-dispensing devices, and sample vials transported to UHPLC-MS and reactor stations (burger2020amobilerobotic pages 1-3, burger2023amobilerobotic pages 52-56, brass2026amobilerobotic pages 1-7, brass2026amobilerobotic pages 7-10). The ABB YuMi PXRD workflow uses SmartGripper fingers (force reduced from 20 N to 10 N because fingers snapped under repetitive use) to handle glass sample vials, septa caps, sample racks (8-well), and XRD sample plates with Kapton-taped caps (lunt2024aroboticworkflow pages 87-95, lunt2023modularmultirobotintegration pages 1-3, lunt2024aroboticworkflow pages 49-57). The A-Lab (Szymanski et al. 2023) uses a robotic arm to handle nickel crucibles with press-fit nickel-plated caps (removed by a stationary gripper), plastic storage vials, and consumables from a seven-tier drawer rack (fei2026agenticllmreasoning pages 24-29, szymanski2023anautonomouslaboratory pages 1-2, fei2026agenticllmreasoning pages 3-6). ORGANA handles beakers, Erlenmeyer flasks, glassy-carbon electrodes, pH probes, and reagent vessels using a general-purpose robot arm (darvish2025organaarobotic pages 7-9, darvish2025organaarobotic pages 9-12, darvish2025organaarobotic pages 20-22, darvish2025organaarobotic pages 6-7). The Radulov et al. (2026) vision-guided powder scooping system uses a Franka Research 3 with a Robotiq 85F gripper to manipulate a spatula/scoop tool across powders of varying flowability (radulov2026visionguidedadaptivescooping pages 3-4).

The approximately 10–15 object classes that account for most arm operations are: (1) vials (2–20 mL, various neck finishes), (2) vial caps/septa (screw, crimp, press-fit), (3) sample racks/trays, (4) crucibles, (5) well plates (SBS-footprint), (6) tip racks, (7) beakers/flasks, (8) XRD/PXRD sample holders, (9) electrodes, (10) spatulas/scoops, (11) filtration funnels, (12) instrument interfaces (doors, valves), and (13) substrates/coupons.

## 2. Specifications, Standards, and Vendor Variation

**Vials.** The 2 mL HPLC vial (Ø12 × 32 mm, 11 mm crimp finish) and 20 mL scintillation vial (Ø28 × 61 mm, GPI 24-400 screw neck) are the bookends of SDL vial handling. Published work documents that certified vials can exhibit diameter variation sufficient to prevent insertion into fixtures; after widening wells to accommodate variation, 100 consecutive vials fit and passed testing (burger2023amobilerobotic pages 108-112). This suggests vendor-to-vendor variation can exceed 0.5 mm and will break tight-clearance printed fixtures.

**SEM pin stubs.** The standard pin stub is Ø12.7 mm with a Ø3.2 mm mounting pin, confirmed across multiple publications (fei2026agenticllmreasoning pages 24-29). JEOL and Hitachi use Ø25 or Ø32 mm cylinder mounts, which are dimensionally distinct enough to require a separate fixture.

**Well plates.** ANSI/SLAS 1-2004 through 4-2004 define the microplate footprint (127.76 ± 0.25 × 85.48 ± 0.25 mm), flange height, and well positions. This footprint exceeds the PiPER's stock 70 mm gripper opening, requiring either the 100 mm variant or custom edge-grasp fingers.

**DSC pans.** TA Instruments Tzero pans are approximately Ø6.7 × 2.6 mm, mass ≈ 0.04 g each, made of aluminium. These are among the smallest and most crush-sensitive objects in the set. Mettler 40 µL pans have slightly different dimensions; vendor incompatibility is expected.

**Test coupons.** ASTM D638 Type V: 63.5 mm overall length, 9.53 mm grip width, 3.18 mm thick. ASTM E23 Charpy: 55 × 10 × 10 mm (full) or 55 × 10 × 5 mm (subsize). Both are 3D-printable for benchmarking.

**CR2032 coin cells.** Ø20 × 3.2 mm, ~3 g, stainless steel case, IEC 60086. Dimensions are tightly standardized; vendor variation is negligible.

**Where vendor variation exceeds ~0.5 mm:** Vials (body diameter, especially across GPI finish families), DSC pans across manufacturers (Tzero vs. Mettler vs. Netzsch), and XRD sample cups (vendor-specific, not interchangeable).

## 3. Property Axes That Stress Manipulation

From the general manipulation literature (YCB, NIST, Peg-in-Bench) and the laboratory-specific record, twelve difficulty axes predict grasp or placement failure:

1. **Small features (≤12 mm):** DSC pans (Ø6.7 mm), HPLC vials (Ø12 mm), SEM stub pins (Ø3.2 mm).
2. **Large format (>70 mm):** SBS-footprint plates, racks, and reservoirs (128 × 85 mm) exceed the stock gripper (angers2025roboculturearobotics pages 4-5).
3. **Mass/CG shift with fill:** Feedstock cups (30→80 g), crucibles (8→40 g), filled vials (20→35 g).
4. **Liquid slosh:** Filled vials, reservoirs — orientation-aware tactile feedback reduces spill risk (butterworth2023leveragingmultimodalsensing pages 6-7).
5. **Powder spill/cohesion:** Crucibles, weighing boats, powder-filled vials — published scooping tested seven powders spanning flow behavior (radulov2026visionguidedadaptivescooping pages 3-4).
6. **Transparency/refraction:** Borosilicate vials — transparent vials caused visual-only insertion to fail at 48.78%; multimodal feedback raised success to 89.55% (butterworth2023leveragingmultimodalsensing pages 1-2, butterworth2023leveragingmultimodalsensing pages 6-7).
7. **Specular metal:** Aluminium cups, crucibles, stubs, coin cells, spatulas, weighing boats.
8. **Thin/near-planar (<5 mm):** DSC pans, coin cells, tensile coupons, weighing boats.
9. **Crushable/deformable:** DSC pans, weighing boats, polystyrene plate rims.
10. **Two-part assembly:** Cap/vial (fakhruldeen2025multimodalbehaviourtrees pages 4-5, fakhruldeen2025multimodalbehaviourtrees pages 1-2); press-fit plug; DSC pan + lid; XRD cup + insert.
11. **Peg-in-hole / seat-in-fixture:** SEM stub, feedstock cup, vials in racks. Peg-in-Bench provides modular clearances at 0.1, 1, and 3 mm (delgado2026peginbenchamodular pages 4-5, delgado2026peginbenchamodular pages 3-4).
12. **Tool use:** Spatula for scooping/scraping; weighing boat as pouring implement.

The coverage matrix below confirms every axis is exercised by at least two Tier 1 objects:

| Difficulty Axis | Object A | Object B | Additional Tier 1 Objects |
|---|---|---|---|
| Small features (≤12 mm) | Item 5 — 2 mL HPLC vial: Ø12 mm body and 11 mm cap | Item 9 — DSC pan and lid: Ø≈6.7 mm | Item 8 — SEM pin stub: Ø3.2 mm mounting pin; Item 14 — powder spatula: 5–8 mm blade. Small components are consistent with the size-diverse design of manipulation benchmarks (calli2015benchmarkinginmanipulationa pages 6-7, delgado2026peginbenchamodular pages 3-4) |
| Large format (>70 mm; exceeds stock gripper) | Item 6 — 96-well plate: 127.76 × 85.48 mm | Item 7 — Opentrons tip rack: 127.76 × 85.48 mm | Item 18 — Opentrons reservoir: 127.76 × 85.48 mm. These require under-flange or edge fingers, a 100 mm gripper, or handling through a carrier |
| Mass/centre-of-gravity shift (fill-dependent) | Item 16 — powder-filled 20 mL vial: ≈20 g empty to ≈35 g filled | Item 17 — dyed-water-filled 20 mL vial: ≈20 g empty to ≈35 g filled | Item 1 — atomizer feedstock cup: ≈30 g empty to ≈80 g filled; Item 3 — aluminium dosing crucible: ≈8 g empty to ≈40 g filled |
| Liquid slosh | Item 17 — dyed-water-filled 20 mL vial: 15 mL fill | Item 18 — Opentrons reservoir: test at documented 25% and 75% fill levels | Item 4 — 20 mL scintillation vial: capped liquid condition. Orientation-aware tactile feedback is relevant to spill avoidance (butterworth2023leveragingmultimodalsensing pages 6-7) |
| Powder spill/cohesion | Item 16 — powder-filled 20 mL vial: NaCl or semolina surrogate | Item 3 — aluminium dosing crucible: loose-powder dose | Items 1, 12, 14, and 15 — feedstock cup, back-loading XRD cup, powder scoop, and weighing boat. Published robotic scooping tested NaCl, semolina, pectin, flour, silica, sugar, and bicarbonate to span powder behavior (radulov2026visionguidedadaptivescooping pages 3-4) |
| Transparency/refraction | Item 4 — 20 mL borosilicate scintillation vial | Item 5 — 2 mL borosilicate HPLC vial | Item 17 — dyed-water-filled glass vial. Transparent vials complicate failed-placement detection; multimodal insertion outperformed visual-only insertion (butterworth2023leveragingmultimodalsensing pages 1-2, butterworth2023leveragingmultimodalsensing pages 6-7) |
| Specular metal surface | Item 1 — machined aluminium feedstock cup | Item 8 — aluminium SEM pin stub | Items 2, 3, 9, 13, 14, and 15 — aluminium plug, aluminium crucible, aluminium DSC pan/lid, CR2032, steel spatula, and aluminium weighing boat |
| Thin/near-planar (<5 mm) | Item 9 — DSC pan/lid: ≈2.6 mm pan height and foil-like lid | Item 13 — CR2032 coin cell: 3.2 mm thick | Item 10 — ASTM D638 Type V coupon: ≈3.18 mm thick; Item 15 — aluminium weighing boat: thin foil walls |
| Crushable/deformable | Item 9 — aluminium DSC pan/lid: readily dented or over-crimped | Item 15 — aluminium weighing boat: thin foil shell | Item 6 — polystyrene well plate: flexible rim; Item 18 — polypropylene reservoir: flexible wall and flange. These require force-limited grasping rather than rigid-object assumptions |
| Two-part assembly (cap, lid, or press-fit) | Items 2 and 1 — aluminium plug press-fitted into feedstock cup | Item 4 — screw cap on 20 mL vial | Items 5, 9, and 12 — HPLC vial and cap, DSC pan and lid, and XRD cup and insert. Published capping failures include misalignment, cross-threading, incomplete sealing, and dropped caps (fakhruldeen2025multimodalbehaviourtrees pages 4-5, burger2023amobilerobotic pages 108-112) |
| Peg-in-hole or seat-in-fixture | Item 8 — SEM stub pin inserted into multi-stub holder | Item 1 — feedstock cup inserted into atomizer or crucible nest | Items 3, 5, 10, 11, 12, and 13 — dosing crucible, HPLC vial, tensile coupon, Charpy coupon, XRD cup, and coin cell. Insertion benchmarks deliberately vary geometry and clearance (delgado2026peginbenchamodular pages 4-5, delgado2026peginbenchamodular pages 3-4) |
| Tool use (grasp and operate) | Item 14 — powder scoop/spatula: acquire, scoop, scrape, pour, and replace | Item 15 — weighing boat: grasp and operate as a pouring implement | Item 12 — back-loading XRD cup: hold or fixture while using the spatula to load and level powder. Published autonomous powder handling uses a gripped scoop and adaptive acquisition feedback (radulov2026visionguidedadaptivescooping pages 3-4) |


*Table: Every proposed manipulation-stress axis is exercised by at least two Tier 1 objects. The matrix also identifies where custom fingers, force limiting, passive-compliance fixtures, or spill containment are required.*

## 4. How Benchmark Object Sets Were Chosen

**YCB (77 objects).** Selected through a literature survey for variety in shape, size, transparency, deformability, texture, and weight, with practical constraints on durability, cost (<$350 for the entire set), portability (under 22 kg airline limit), and long-term availability (calli2015benchmarkinginmanipulationa pages 1-2, calli2015benchmarkinginmanipulationa pages 6-7, calli2015benchmarkinginmanipulation pages 6-7). Each object ships with 600 RGB-D images, 600 high-resolution RGB images, segmentation masks, calibration data, and a texture-mapped 3D mesh model; mass and major dimensions are tabulated (calli2015benchmarkinginmanipulationa pages 7-8, calli2015benchmarkinginmanipulation pages 7-8). However, YCB contains no laboratory objects.

**NIST Assembly Task Boards.** Use standard off-the-shelf manufacturing components (screws, nuts, gears, connectors, belts, wires) in varying sizes to represent common assembly operations. Boards are ~400 × 400 × 10 mm with intentionally loosened tolerances. CAD/STL files, protocols, and scoring metrics are provided for replication (kimble2020benchmarkingprotocolsfor pages 1-3, kimble2022performancemeasuresto pages 1-2, kimble2020benchmarkingprotocolsfor pages 3-5).

**FMB (66 objects).** Uses procedurally generated, 3D-printed objects with supplied CAD files, 22,500 human demonstrations, and pretrained imitation-learning policies. Objects vary in shape, size, and color; functional manipulation (grasping in task-relevant poses, reorientation, insertion) is the core test (luo2025fmbafunctional pages 2-3, luo2025fmbafunctional pages 1-2).

**Peg-in-Bench.** Modular, fully 3D-printable benchmark with five peg shapes (circular, rectangular, hexagonal, triangular, L-shaped), 15 shaped-hole pieces at three tolerance levels (0.1, 1, and 3 mm), and configurable base structures. Printed at 0.05 mm resolution on a resin printer. Ships with STL files and a scenario-generation tool with reproducible random seeds (delgado2026peginbenchamodular pages 4-5, delgado2026peginbenchamodular pages 3-4, delgado2026peginbenchamodular pages 2-3, delgado2026peginbenchamodular pages 1-2).

**Cross-Embodiment Gripper Benchmark (CEGB).** Uses a YCB object subset with NIST-derived metrics, evaluated across a collaborative manipulator, mobile robot, and UAV. Provides open-source CAD for a self-locking reference gripper (vagas2026acrossembodimentgripper pages 2-3, vagas2026acrossembodimentgripper pages 1-2).

**Consumable handling:** No published benchmark explicitly addresses single-use or deforming objects (crimped DSC pans, pierced septa, press-fitted lids). YCB avoids perishable items. We recommend stocking consumables at 2× the planned trial count and recording serial number and lot per item. The published Liverpool crimping system required iterative dimensional adjustments before achieving reliable sealing (burger2023amobilerobotic pages 108-112).

**What must ship with each object for reproducibility:** Following YCB and FMB precedent, each object should be documented with (1) a CAD/STL model or structured-light scan, (2) measured mass, (3) major dimensions with tolerances, (4) supplier part number and lot, (5) canonical AprilTag-referenced pose in the sandbox, and (6) surface characterization notes. Friction coefficients are not supplied by any existing benchmark; we recommend measuring and tabulating them for the printed fixture surfaces.

## 5. Fill Surrogates and Safety

Published lab-robotics powder scooping experiments used seven surrogate powders — silicon dioxide, sugar, sodium chloride, semolina, sodium bicarbonate, pectin, and wheat flour — selected to represent different flow characteristics (radulov2026visionguidedadaptivescooping pages 3-4). No published SDL benchmark explicitly reports Hausner ratio or Carr index matching for metal-powder surrogates. **This is an open gap.** AlSi10Mg (15–45 µm, spherical, Hausner ratio typically 1.10–1.20, free-flowing to mildly cohesive) can be approximated by fine NaCl (cubic, HR ≈ 1.15–1.25) or glass microspheres (spherical, HR ≈ 1.05–1.15); cohesive Si powder (angular, <45 µm, HR ≈ 1.30–1.45) can be approximated by wheat flour (HR ≈ 1.35–1.45) or fine lactose (HR ≈ 1.30–1.40). These are extrapolations based on pharmaceutical powder-flow literature, not direct robotic-manipulation studies.

For liquids, dyed water provides high-contrast vision feedback for slosh and fill-level detection. Glycerol–water mixtures (e.g., 50 wt% glycerol, viscosity ~6 mPa·s at 25°C) can simulate viscous reagents. No published SDL benchmark specifies a liquid-fill convention; we recommend standardizing at 25%, 50%, and 75% fill by volume.

**Spill containment:** Use secondary PETG trays underneath each fixture station, with absorbent liner (e.g., Kimwipe matting) for liquids and grounded conductive trays for powder surrogates to manage static charge.

## 6. Holders and Fixtures

**Commercially available:** SBS-footprint vial racks (e.g., BioMicroLab for 2 mL HPLC vials), multi-stub SEM holders (Ted Pella, Agar Scientific), DSC autosampler trays (TA Instruments), Opentrons labware (tip racks, reservoirs, well plates with defined JSON labware definitions).

**Must be printed (PETG on the Bambu A1 mini):** Atomizer cup nests with 15–30° lead-in chamfers and ≥1 mm diametral clearance; crucible nests; vial racks with tapered wells (burger2023amobilerobotic pages 62-69); SEM stub holders with replaceable press-fit bushings; DSC pan indexed trays; coupon grip adapters; coin-cell magazines; spatula holder clips; weighing-boat stack dispensers; and SLAS-footprint adapters for the Opentrons ecosystem.

**Printable fixture libraries:** Opentrons provides an open-source custom labware creator that generates JSON labware definitions for SLAS-footprint adapters. The Liverpool group designed custom grippers and racks for the KUKA system (lunt2024aroboticworkflow pages 49-57). NIST distributes CAD/STL files for task board fixtures (kimble2020benchmarkingprotocolsfor pages 3-5). FMB and Peg-in-Bench provide all fixture files as open-source repositories (luo2025fmbafunctional pages 2-3, delgado2026peginbenchamodular pages 1-2).

## 7. The Tiered Object Set

### Tier 1: Core (~18 items)

This is the minimum set that covers all twelve manipulation-difficulty axes and the five in-house workflows (ultrasonic atomization, powder dosing, characterization, liquid handling, vial management). The estimated total cost for consumables and durable objects is approximately $150–$250, excluding fixtures (which are printed in-house).

| Item # | Object Class | Generic Specification (dimensions, mass empty/filled, material) | Governing Standard | Representative Source | Approx. Unit Cost | Qty to Stock | Manipulation Primitives Exercised | Difficulty Axes Covered | Required Fixture/Holder |
|---:|---|---|---|---|---:|---:|---|---|---|
| 1 | Atomizer feedstock cup | Ø20 × 80 mm; bored ≈76 mm deep; ≈30 g empty / ≈80 g filled; Al 6061 | Custom, matched to AMAZEMET rePOWDER | In-house machined | ≈$5 | 6 | Pick, place, insert | Peg-in-hole; specular metal; fill-dependent mass/CG | Printed PETG nest with 15° lead-in chamfer |
| 2 | Aluminium press-fit plug | Ø20 × 5 mm press-fit disc; ≈3 g; Al 6061 | Custom | In-house machined | ≈$1 | 12 | Pick, align, press-fit insert | Two-part assembly; thin part; force-limited insertion | Printed alignment funnel |
| 3 | Aluminium dosing crucible | Ø20 × 25 mm tall; ≈8 g empty / ≈40 g filled; aluminium | Custom, matched to atomizer/doser interface | MTI Corp or in-house equivalent | ≈$3 | 6 | Pick, place, seat | Specular surface; mass/CG shift; powder spill | Printed nest with 1–2 mm diametral clearance and chamfer |
| 4 | 20 mL scintillation vial with screw cap | Ø28 × 61 mm; ≈20 g empty / ≈40 g filled; borosilicate glass and PP cap | GPI 24-400 neck finish | Fisher Scientific or VWR | ≈$0.50 | 12 | Pick, place, seat, uncap, recap | Transparent/refractive; two-part threaded object; slosh when filled; vendor dimensional variation. Vials and caps dominate published SDL handling tasks (burger2020amobilerobotic pages 1-3, fakhruldeen2025multimodalbehaviourtrees pages 4-5) | SBS-footprint printed vial rack with tapered wells |
| 5 | 2 mL HPLC vial with crimp/snap cap | Ø12 × 32 mm; ≈1.5 g empty / ≈3.5 g filled; borosilicate glass and aluminium/polymer cap | 11 mm chromatography-vial crimp finish | Agilent or Waters | ≈$0.30 | 24 | Pick, place, insert, cap handling | Small diameter; transparent glass; two-part object; crimp deformation. Certified vial variation has caused fixture-fit failures in published automation (burger2023amobilerobotic pages 108-112) | SBS-footprint printed 32-position rack with replaceable tapered inserts |
| 6 | SBS-format 96-well plate | 127.76 × 85.48 × ≈14.35 mm; ≈25 g; polystyrene | ANSI/SLAS 1-2004 through 4-2004 | Corning or Greiner Bio-One | ≈$3 | 2 | Pick, place, seat | Width exceeds 70 mm stock-gripper opening; flexible rim; repetitive well insertion. Force-triggered retries produced 99% pipette-to-well insertion in RoboCulture (angers2025roboculturearobotics pages 4-5) | Commercial plate nest or printed SLAS adapter; edge-grasp fingers required |
| 7 | Opentrons 300 µL tip rack | 127.76 × 85.48 × ≈65 mm; ≈120 g; PP | ANSI/SLAS footprint | Opentrons | ≈$8 | 2 | Pick, place, seat | Large/tall object; exceeds stock gripper opening; possible lid/base separation | OT-2 deck slot or printed SLAS adapter; custom edge or under-flange fingers |
| 8 | SEM pin stub, Ø12.7 mm | Ø12.7 mm head; ≈8 mm pin assembly with Ø3.2 mm post; ≈3 g; aluminium | De facto Agar/Ted Pella pin-stub format | Ted Pella or Agar Scientific | ≈$2 | 6 | Pick, place, insert | Small object; specular metal; peg-in-hole seating | Commercial multi-stub holder or printed holder with replaceable bushings |
| 9 | DSC pan and lid, 40 µL Tzero style | Pan Ø≈6.7 × 2.6 mm; matching Ø≈6.7 mm lid; ≈0.04 g each; aluminium | TA Instruments Tzero proprietary format | TA Instruments | ≈$1.50/pair | 12 pairs | Pick, place, align, press-fit/crimp | Very small; crushable; thin; specular; two-part object | Printed indexed tray with individual recessed nests; dedicated low-force fingers or vacuum pickup |
| 10 | ASTM D638 Type V tensile coupon | 63.5 mm overall; ≈9.53 mm grip width; ≈3.18 mm thick; ≈5 g; printed PETG/PLA | ASTM D638 Type V | In-house printed | ≈$0.10 | 6 | Pick, place, orient, seat in grip | Thin/flat; near-planar vision target; orientation-sensitive seating | Printed grip adapter, tapered slot, or V-block with mechanical end stop |
| 11 | ASTM E23 Charpy coupon | 55 × 10 × 10 mm full-size, or 55 × 10 × 5 mm subsize; ≈30 g metal / ≈5 g polymer; metal or polymer | ASTM E23 | In-house printed or commercial reference specimen | ≈$0.10 printed / ≈$5 metal | 6 | Pick, place, orient, seat | Prismatic block; notch-orientation constraint; precise support seating | Printed V-notch nest with keyed orientation and end stops |
| 12 | Back-loading XRD sample cup | ≈Ø25 × 20 mm; ≈5 g empty; PMMA or Al body with zero-background Si insert | Vendor-specific Bruker, Rigaku, or Malvern Panalytical format | Bruker, Rigaku, or Malvern Panalytical | ≈$20 | 2 | Pick, place, seat, pour/fill | Two-part object; powder fill; specular insert; precise registration. Published YuMi PXRD systems handled vials, caps, racks, and XRD sample plates (lunt2024aroboticworkflow pages 87-95, lunt2023modularmultirobotintegration pages 1-3) | Printed holder keyed to one documented vendor part number, with registration features |
| 13 | CR2032 coin cell | Ø20 × 3.2 mm; ≈3 g; stainless-steel case | IEC 60086 designation/dimensions | Any documented battery supplier | ≈$0.50 | 6 | Pick, place, orient, insert | Thin/flat; specular; small edge; polarity/orientation requirement | Printed magazine and singulation tray with finger-access relief |
| 14 | Powder scoop/spatula | ≈120 mm long; 5–8 mm blade width; ≈10 g; stainless steel | Generic laboratory tool; supplier-specific | Fisher Scientific or VWR | ≈$5 | 2 | Pick tool, scoop, scrape, pour, replace | Tool use; specular metal; narrow grasp; powder adhesion. Published adaptive scooping used a gripped tool and feedback across powders of different flow behavior (radulov2026visionguidedadaptivescooping pages 3-4) | Printed keyed holder clip presenting a repeatable handle pose |
| 15 | Aluminium weighing boat | ≈46 × 46 × 8 mm; ≈0.5 g; aluminium foil | Generic laboratory consumable; supplier-specific | Fisher Scientific or VWR | ≈$0.05 | 24 | Pick, place, fill, pour | Crushable; specular; near-planar; extremely low mass; stack adhesion | Printed singulating stack dispenser and supported placement nest |
| 16 | Powder-filled 20 mL vial | Item 4 vial filled with 15 g NaCl or semolina; ≈35 g total; glass and PP | GPI 24-400; surrogate fill protocol | Fisher/VWR vial plus bulk NaCl or semolina | ≈$1 | 6 | Pick, place, uncap, pour, recap | Fill-dependent mass/CG; powder spill; cohesion/flowability. NaCl and semolina were among seven powders used in published autonomous scooping experiments (radulov2026visionguidedadaptivescooping pages 3-4) | Same SBS-footprint rack as Item 4; secondary spill tray |
| 17 | Dyed-water-filled 20 mL vial | Item 4 vial filled with 15 mL dyed water; ≈35 g total; glass and PP | GPI 24-400; benchmark fill protocol | Fisher/VWR vial plus food dye | ≈$0.60 | 6 | Pick, place, uncap, pour, recap | Liquid slosh; spill risk; transparent/refractive container; changing CG | Same rack as Item 4; secondary containment tray and absorbent liner |
| 18 | Opentrons single-well reservoir | 127.76 × 85.48 × ≈25 mm; ≈30 g empty; PP | ANSI/SLAS footprint | Opentrons or Axygen | ≈$5 | 1 | Pick, place, seat | Large-format object; exceeds 70 mm gripper; flexible walls/rim; liquid-spill potential | OT-2 deck slot or printed SLAS adapter; custom edge/under-flange fingers |


*Table: A specification-level, approximately 18-item core sandbox covering the in-house materials workflows and major manipulation stress axes. Costs are approximate US single-unit prices and fixtures should be versioned with the exact supplier part or lot.*

### Tier 2: Extension and Tier 3: Defer/Avoid

Extension objects broaden comparison toward NMR-serving, UV-Vis, biological, and metallographic SDLs. Deferred objects add disproportionate safety, payload, or instrument-specific complexity.

| Tier | Object Class | Specification | Rationale (why include or why defer) | Approx. Cost |
|---|---|---|---|---:|
| Tier 2 — Extension | NMR tube | Ø5 × 178 mm; borosilicate glass; supplier-specific wall thickness and length tolerance | Extends comparison to mobile manipulators serving NMR. Exercises grasping and deep, orientation-sensitive insertion of a long, slender, transparent object. Use a printed funnel rack and low-force fingers. | ≈$5 |
| Tier 2 — Extension | Cuvette | 10 mm optical path; typically 12.5 × 12.5 × 45 mm; ≈4.5 mL; optical glass or disposable PS | Adds UV–Vis workflows and transparent, square-section handling. Retain one glass and several disposable PS examples because their friction, stiffness, and optical behavior differ. | ≈$1 disposable PS |
| Tier 2 — Extension | 8 mL vial | Ø≈17 × 60 mm; borosilicate glass; GPI 15-425 screw finish | Bridges the large geometric gap between 2 mL HPLC and 20 mL scintillation vials and tests whether fingers and racks generalize across vial families. Published SDLs repeatedly manipulate vials and custom racks (burger2020amobilerobotic pages 1-3, burger2023amobilerobotic pages 52-56). | ≈$0.40 |
| Tier 2 — Extension | 50 mL centrifuge tube | Ø≈30 × 115 mm; conical PP body with screw cap; ≈12–15 g empty and ≈65 g filled | Common bio-laboratory transport object; adds a compliant plastic wall, conical bottom, long body, threaded cap, and substantial fill-dependent centre-of-gravity shift. RoboCulture demonstrates the relevance of plate and liquid-handling tasks in biological automation (angers2025roboculturearobotics pages 4-5). | ≈$0.30 |
| Tier 2 — Extension | Metallographic mount | Ø25 or Ø32 mm, typically 10–20 mm high; epoxy, acrylic, or phenolic | Adds a materials-characterization object with a standardized cylindrical presentation but substantial vendor and preparation variation. Useful for seating, indexing, polishing-station transfer, and surface-orientation tests. | ≈$2–5 |
| Tier 2 — Extension | Petri dish | Ø60 or Ø90 mm; disposable PS dish and lid | Broadens coverage toward biological SDLs and environmental monitoring. Exercises a large, shallow, transparent, easily separated two-part object; requires custom fingers because Ø90 mm exceeds the stock 70 mm gripper. | ≈$0.20 |
| Tier 2 — Extension | 384-well plate | ANSI/SLAS footprint, 127.76 × 85.48 mm; PS; vendor-dependent height and skirt | Extends the 96-well task to higher-density liquid handling while preserving the same external footprint. Smaller wells increase insertion sensitivity; force-triggered retries were required even for randomized well insertion in published work (angers2025roboculturearobotics pages 4-5). | ≈$5 |
| Tier 3 — Defer | Hazardous powders: real AlSi10Mg and Si | Workflow powders, nominally 15–45 µm; combustible or respirable particulate hazards depend on composition and handling | Defer until local exhaust ventilation, grounded conductive containment, antistatic controls, cleaning validation, and powder-specific risk assessment exist. Begin with NaCl and semolina; both occur in published adaptive-scooping tests, which also used silica, sugar, bicarbonate, pectin, and flour to span flow behavior (radulov2026visionguidedadaptivescooping pages 3-4). | N/A |
| Tier 3 — Defer | Syringe and needle assemblies | Disposable syringe with Luer or Luer-lock needle; size varies by workflow | Defer because sharps add puncture and contamination hazards without covering an initial workflow. Use a guarded syringe pump or blunt cannula if liquid delivery must later be represented; ORGANA used pump-based liquid transfer (darvish2025organaarobotic pages 7-9, darvish2025organaarobotic pages 9-12). | ≈$0.50 |
| Tier 3 — Avoid initially | Large Erlenmeyer flask (>250 mL) | Borosilicate flask, typically >Ø85 mm body; total mass can approach or exceed 1.5 kg when filled | Outside the stock 70 mm gripper envelope and potentially beyond the arm payload when filled; not part of the initial workflows. ORGANA handled beakers and glass vessels, but this does not justify beginning with large flasks (darvish2025organaarobotic pages 7-9, darvish2025organaarobotic pages 20-22). | ≈$5 |
| Tier 3 — Avoid initially | Full-size ASTM E8/E8M tensile specimen | Typically >200 mm overall length; metal dog-bone geometry; dimensions depend on plate, sheet, round, or subsize specimen | Awkward relative to the 626 mm reach and tabletop enclosure, difficult to grasp without collision, and redundant with a compact D638 Type V coupon for initial grip-seating tests. Add only with the actual tensile-machine grips and loading geometry. | ≈$10 |
| Tier 3 — Defer | Glass microscope slide | Typically 75 × 25 × 1 mm; soda-lime or borosilicate glass | Very thin, transparent, fragile, and difficult to singulate, but largely duplicates axes already covered by the DSC lid, tensile coupon, coin cell, and weighing boat. Add later if slide-based characterization becomes a real workflow. | ≈$0.10 |
| Tier 3 — Defer | Instrument doors, drawers, and buttons | Instrument-specific handles, hinges, slides, latches, travel, and actuation forces | Defer because these are articulated environmental fixtures rather than portable benchmark objects; they require force-compliant interaction and do not generalize across instruments. Published robots do operate doors and equipment, but interfaces are system-specific (brass2026amobilerobotic pages 7-10, kimble2020benchmarkingprotocolsfor pages 3-5). Represent later with a separate modular task board. | N/A |


*Table: Extension objects broaden comparison to NMR, UV–Vis, biological automation, and metallography, while deferred objects add disproportionate safety, payload, or instrument-specific complexity. Costs are approximate US single-unit prices.*

## 8. Critical Gaps and Caveats

Several important caveats apply:

1. **No published physical laboratory-object manipulation benchmark exists.** This object set would be the first, as established in Q4. The design principles are adapted from YCB (calli2015benchmarkinginmanipulationa pages 1-2, calli2015benchmarkinginmanipulationa pages 6-7), NIST (kimble2020benchmarkingprotocolsfor pages 1-3, kimble2020benchmarkingprotocolsfor pages 3-5), FMB (luo2025fmbafunctional pages 2-3), and Peg-in-Bench (delgado2026peginbenchamodular pages 4-5, delgado2026peginbenchamodular pages 3-4), none of which contain laboratory objects.

2. **Reliability data are sparse.** The best-published vial insertion rate is 89.55% with multimodal feedback (butterworth2023leveragingmultimodalsensing pages 1-2, butterworth2023leveragingmultimodalsensing pages 6-7); robotic vial capping achieves 88% end-to-end (fakhruldeen2025multimodalbehaviourtrees pages 4-5, fakhruldeen2025multimodalbehaviourtrees pages 1-2); rack insertion reaches 92% (fakhruldeen2025multimodalbehaviourtrees pages 4-5). The Liverpool system achieved 464/464 rack placements using tapered edges and compliance (burger2023amobilerobotic pages 62-69). None of these use a sub-$5k arm.

3. **Powder surrogate matching is an extrapolation.** No published study validates that NaCl or flour reproduces the robotic-manipulation behavior of AlSi10Mg. The surrogates are matched on Hausner ratio and particle-size class, not on direct manipulation testing.

4. **Fixture tolerances are design-critical.** Vendor-to-vendor vial variation can exceed 0.5 mm (burger2023amobilerobotic pages 108-112). The Q3 finding — 1–2 mm lead-in chamfers at 15–30° with ≥1 mm design clearance — should be applied to every printed fixture. Each fixture must be versioned to a specific supplier part number and lot.

5. **DSC pans (Ø6.7 mm, 0.04 g) and SEM stub pins (Ø3.2 mm) may be below the practical handling limit** of a stock two-finger parallel gripper at 40 N. These may require dedicated vacuum or micro-gripper fingers, printed on the Bambu A1 mini.

6. **SBS-footprint objects (well plates, tip racks, reservoirs) exceed the 70 mm stock gripper opening.** The 100 mm variant gripper or custom under-flange fingers are required. This is a known hardware limitation to resolve before these items enter the benchmark.

7. **The powder scoop/spatula exercises tool use** — a manipulation primitive that has been demonstrated robotically on a Franka Research 3 (radulov2026visionguidedadaptivescooping pages 3-4) but is substantially more challenging on a low-cost arm without torque sensing. Include it to expose this gap, but expect low initial success rates.


References

1. (burger2020amobilerobotic pages 1-3): Benjamin Burger, Phillip M. Maffettone, Vladimir V. Gusev, Catherine M. Aitchison, Yang Bai, Xiaoyan Wang, Xiaobo Li, Ben M. Alston, Buyi Li, Rob Clowes, Nicola Rankin, Brandon Harris, Reiner Sebastian Sprick, and Andrew I. Cooper. A mobile robotic chemist. Nature, 583:237-241, Jul 2020. URL: https://doi.org/10.1038/s41586-020-2442-2, doi:10.1038/s41586-020-2442-2. This article has 2061 citations and is from a highest quality peer-reviewed journal.

2. (burger2023amobilerobotic pages 52-56): Benjamin Burger. A mobile robotic researcher. ArXiv, Jan 2023. URL: https://doi.org/10.17638/03087073, doi:10.17638/03087073. This article has 4 citations.

3. (brass2026amobilerobotic pages 1-7): Emma Brass, Satheeshkumar Veeramani, Zhengxue Zhou, Hatem Fakhruldeen, J. S. Manzano, R. Clowes, Isil Akpinar, Miriam R. Ward, John W. Ward, and Andrew I. Cooper. A mobile robotic process chemist. ChemRxiv, Oct 2026. URL: https://doi.org/10.26434/chemrxiv-2025-bsfvz, doi:10.26434/chemrxiv-2025-bsfvz. This article has 6 citations.

4. (brass2026amobilerobotic pages 7-10): Emma Brass, Satheeshkumar Veeramani, Zhengxue Zhou, Hatem Fakhruldeen, J. S. Manzano, R. Clowes, Isil Akpinar, Miriam R. Ward, John W. Ward, and Andrew I. Cooper. A mobile robotic process chemist. ChemRxiv, Oct 2026. URL: https://doi.org/10.26434/chemrxiv-2025-bsfvz, doi:10.26434/chemrxiv-2025-bsfvz. This article has 6 citations.

5. (lunt2024aroboticworkflow pages 87-95): Amy Lunt. A robotic workflow to screen crystal forms using powder x-ray diffraction. Text, Jan 2024. URL: https://doi.org/10.17638/03178518, doi:10.17638/03178518. This article has 0 citations and is from a peer-reviewed journal.

6. (lunt2023modularmultirobotintegration pages 1-3): Amy. M. Lunt, Hatem Fakhruldeen, Gabriella Pizzuto, Louis Longley, Alexander White, Nicola Rankin, Rob Clowes, Ben Alston, Lucia Gigli, Graeme M. Day, Andrew I. Cooper, and Sam. Y. Chong. Modular, multi-robot integration of laboratories: an autonomous solid-state workflow for powder x-ray diffraction. Preprint, Jan 2023. URL: https://doi.org/10.48550/arxiv.2309.00544, doi:10.48550/arxiv.2309.00544. This article has 2 citations.

7. (lunt2024aroboticworkflow pages 49-57): Amy Lunt. A robotic workflow to screen crystal forms using powder x-ray diffraction. Text, Jan 2024. URL: https://doi.org/10.17638/03178518, doi:10.17638/03178518. This article has 0 citations and is from a peer-reviewed journal.

8. (fei2026agenticllmreasoning pages 24-29): Yu-Xing Fei, Bernardus Rendy, Xiao-Chen Yang, Junhee Woo, Xuwei Huang, Chang Li, Shi-Long Wang, David Milsted, Yan Zeng, and Gerbrand Ceder. Agentic llm reasoning in a self-driving laboratory for air-sensitive lithium halide spinel conductors. ArXiv, Apr 2026. URL: https://doi.org/10.48550/arxiv.2604.11957, doi:10.48550/arxiv.2604.11957. This article has 9 citations.

9. (szymanski2023anautonomouslaboratory pages 1-2): Nathan J. Szymanski, Bernardus Rendy, Yuxing Fei, Rishi E. Kumar, Tanjin He, David Milsted, Matthew J. McDermott, Max Gallant, Ekin Dogus Cubuk, Amil Merchant, Haegyeom Kim, Anubhav Jain, Christopher J. Bartel, Kristin Persson, Yan Zeng, and Gerbrand Ceder. An autonomous laboratory for the accelerated synthesis of inorganic materials. Nature, 624:86-91, Nov 2023. URL: https://doi.org/10.1038/s41586-023-06734-w, doi:10.1038/s41586-023-06734-w. This article has 1577 citations and is from a highest quality peer-reviewed journal.

10. (fei2026agenticllmreasoning pages 3-6): Yu-Xing Fei, Bernardus Rendy, Xiao-Chen Yang, Junhee Woo, Xuwei Huang, Chang Li, Shi-Long Wang, David Milsted, Yan Zeng, and Gerbrand Ceder. Agentic llm reasoning in a self-driving laboratory for air-sensitive lithium halide spinel conductors. ArXiv, Apr 2026. URL: https://doi.org/10.48550/arxiv.2604.11957, doi:10.48550/arxiv.2604.11957. This article has 9 citations.

11. (darvish2025organaarobotic pages 7-9): Kourosh Darvish, Marta Skreta, Yuchi Zhao, Naruki Yoshikawa, Sagnik Som, Miroslav Bogdanovic, Yang Cao, Han Hao, Haoping Xu, Alán Aspuru-Guzik, Animesh Garg, and Florian Shkurti. Organa: a robotic assistant for automated chemistry experimentation and characterization. Feb 2025. URL: https://doi.org/10.1016/j.matt.2024.10.015, doi:10.1016/j.matt.2024.10.015. This article has 225 citations and is from a peer-reviewed journal.

12. (darvish2025organaarobotic pages 9-12): Kourosh Darvish, Marta Skreta, Yuchi Zhao, Naruki Yoshikawa, Sagnik Som, Miroslav Bogdanovic, Yang Cao, Han Hao, Haoping Xu, Alán Aspuru-Guzik, Animesh Garg, and Florian Shkurti. Organa: a robotic assistant for automated chemistry experimentation and characterization. Feb 2025. URL: https://doi.org/10.1016/j.matt.2024.10.015, doi:10.1016/j.matt.2024.10.015. This article has 225 citations and is from a peer-reviewed journal.

13. (darvish2025organaarobotic pages 20-22): Kourosh Darvish, Marta Skreta, Yuchi Zhao, Naruki Yoshikawa, Sagnik Som, Miroslav Bogdanovic, Yang Cao, Han Hao, Haoping Xu, Alán Aspuru-Guzik, Animesh Garg, and Florian Shkurti. Organa: a robotic assistant for automated chemistry experimentation and characterization. Feb 2025. URL: https://doi.org/10.1016/j.matt.2024.10.015, doi:10.1016/j.matt.2024.10.015. This article has 225 citations and is from a peer-reviewed journal.

14. (darvish2025organaarobotic pages 6-7): Kourosh Darvish, Marta Skreta, Yuchi Zhao, Naruki Yoshikawa, Sagnik Som, Miroslav Bogdanovic, Yang Cao, Han Hao, Haoping Xu, Alán Aspuru-Guzik, Animesh Garg, and Florian Shkurti. Organa: a robotic assistant for automated chemistry experimentation and characterization. Feb 2025. URL: https://doi.org/10.1016/j.matt.2024.10.015, doi:10.1016/j.matt.2024.10.015. This article has 225 citations and is from a peer-reviewed journal.

15. (radulov2026visionguidedadaptivescooping pages 3-4): Nikola Radulov, Thomas Little, Andrew I. Cooper, and Gabriella Pizzuto. Vision-guided adaptive scooping for powder weighing in autonomous chemistry laboratories. Digital Discovery, 5:2120-2127, Jan 2026. URL: https://doi.org/10.1039/d5dd00569h, doi:10.1039/d5dd00569h. This article has 1 citations and is from a peer-reviewed journal.

16. (burger2023amobilerobotic pages 108-112): Benjamin Burger. A mobile robotic researcher. ArXiv, Jan 2023. URL: https://doi.org/10.17638/03087073, doi:10.17638/03087073. This article has 4 citations.

17. (angers2025roboculturearobotics pages 4-5): Kevin Angers, Kourosh Darvish, Naruki Yoshikawa, Sargol Okhovatian, Dawn Bannerman, Ilya Yakavets, Florian Shkurti, Alán Aspuru-Guzik, and Milica Radisic. Roboculture: a robotics platform for automated biological experimentation. ArXiv, May 2025. URL: https://doi.org/10.48550/arxiv.2505.14941, doi:10.48550/arxiv.2505.14941. This article has 18 citations.

18. (butterworth2023leveragingmultimodalsensing pages 6-7): Aaron Butterworth, Gabriella Pizzuto, Leszek Pecyna, Andrew I. Cooper, and Shan Luo. Leveraging multi-modal sensing for robotic insertion tasks in r&d laboratories. 2023 IEEE 19th International Conference on Automation Science and Engineering (CASE), pages 1-8, Jul 2023. URL: https://doi.org/10.48550/arxiv.2307.00671, doi:10.48550/arxiv.2307.00671. This article has 12 citations.

19. (butterworth2023leveragingmultimodalsensing pages 1-2): Aaron Butterworth, Gabriella Pizzuto, Leszek Pecyna, Andrew I. Cooper, and Shan Luo. Leveraging multi-modal sensing for robotic insertion tasks in r&d laboratories. 2023 IEEE 19th International Conference on Automation Science and Engineering (CASE), pages 1-8, Jul 2023. URL: https://doi.org/10.48550/arxiv.2307.00671, doi:10.48550/arxiv.2307.00671. This article has 12 citations.

20. (fakhruldeen2025multimodalbehaviourtrees pages 4-5): Hatem Fakhruldeen, Arvind Raveendran Nambiar, Satheeshkumar Veeramani, Bonilkumar Vijaykumar Tailor, Hadi Beyzaee Juneghani, Gabriella Pizzuto, and Andrew I. Cooper. Multimodal behaviour trees for robotic laboratory task automation. ArXiv, Jun 2025. URL: https://doi.org/10.48550/arxiv.2506.20399, doi:10.48550/arxiv.2506.20399. This article has 4 citations.

21. (fakhruldeen2025multimodalbehaviourtrees pages 1-2): Hatem Fakhruldeen, Arvind Raveendran Nambiar, Satheeshkumar Veeramani, Bonilkumar Vijaykumar Tailor, Hadi Beyzaee Juneghani, Gabriella Pizzuto, and Andrew I. Cooper. Multimodal behaviour trees for robotic laboratory task automation. ArXiv, Jun 2025. URL: https://doi.org/10.48550/arxiv.2506.20399, doi:10.48550/arxiv.2506.20399. This article has 4 citations.

22. (delgado2026peginbenchamodular pages 4-5): Y. Delgado, José G. Buenaventura-Carreón, Floris Erich, R. Mykhailyshyn, Tomohiro Motoda, Koshi Makihara, and Y. Domae. Peg-in-bench: a modular benchmark for high-precision robotic insertion. ArXiv, Sep 2026. URL: https://doi.org/10.48550/arxiv.2609.00906, doi:10.48550/arxiv.2609.00906. This article has 0 citations.

23. (delgado2026peginbenchamodular pages 3-4): Y. Delgado, José G. Buenaventura-Carreón, Floris Erich, R. Mykhailyshyn, Tomohiro Motoda, Koshi Makihara, and Y. Domae. Peg-in-bench: a modular benchmark for high-precision robotic insertion. ArXiv, Sep 2026. URL: https://doi.org/10.48550/arxiv.2609.00906, doi:10.48550/arxiv.2609.00906. This article has 0 citations.

24. (calli2015benchmarkinginmanipulationa pages 6-7): Berk Calli, Aaron Walsman, Arjun Singh, Siddhartha Srinivasa, Pieter Abbeel, and Aaron M. Dollar. Benchmarking in manipulation research: using the yale-cmu-berkeley object and model set. Sep 2015. URL: https://doi.org/10.1109/mra.2015.2448951, doi:10.1109/mra.2015.2448951. This article has 763 citations and is from a domain leading peer-reviewed journal.

25. (calli2015benchmarkinginmanipulationa pages 1-2): Berk Calli, Aaron Walsman, Arjun Singh, Siddhartha Srinivasa, Pieter Abbeel, and Aaron M. Dollar. Benchmarking in manipulation research: using the yale-cmu-berkeley object and model set. Sep 2015. URL: https://doi.org/10.1109/mra.2015.2448951, doi:10.1109/mra.2015.2448951. This article has 763 citations and is from a domain leading peer-reviewed journal.

26. (calli2015benchmarkinginmanipulation pages 6-7): Berk Calli, Aaron Walsman, Arjun Singh, Siddhartha Srinivasa, Pieter Abbeel, and Aaron M. Dollar. Benchmarking in manipulation research: the ycb object and model set and benchmarking protocols. Text, Jan 2015. URL: https://doi.org/10.48550/arxiv.1502.03143, doi:10.48550/arxiv.1502.03143. This article has 407 citations and is from a peer-reviewed journal.

27. (calli2015benchmarkinginmanipulationa pages 7-8): Berk Calli, Aaron Walsman, Arjun Singh, Siddhartha Srinivasa, Pieter Abbeel, and Aaron M. Dollar. Benchmarking in manipulation research: using the yale-cmu-berkeley object and model set. Sep 2015. URL: https://doi.org/10.1109/mra.2015.2448951, doi:10.1109/mra.2015.2448951. This article has 763 citations and is from a domain leading peer-reviewed journal.

28. (calli2015benchmarkinginmanipulation pages 7-8): Berk Calli, Aaron Walsman, Arjun Singh, Siddhartha Srinivasa, Pieter Abbeel, and Aaron M. Dollar. Benchmarking in manipulation research: the ycb object and model set and benchmarking protocols. Text, Jan 2015. URL: https://doi.org/10.48550/arxiv.1502.03143, doi:10.48550/arxiv.1502.03143. This article has 407 citations and is from a peer-reviewed journal.

29. (kimble2020benchmarkingprotocolsfor pages 1-3): Kenneth Kimble, Karl Van Wyk, Joe Falco, Elena Messina, Yu Sun, Mizuho Shibata, Wataru Uemura, and Yasuyoshi Yokokohji. Benchmarking protocols for evaluating small parts robotic assembly systems. IEEE Robotics and Automation Letters, 5:883-889, Apr 2020. URL: https://doi.org/10.1109/lra.2020.2965869, doi:10.1109/lra.2020.2965869. This article has 149 citations and is from a domain leading peer-reviewed journal.

30. (kimble2022performancemeasuresto pages 1-2): Kenneth Kimble, Justin Albrecht, Megan Zimmerman, and Joe Falco. Performance measures to benchmark the grasping, manipulation, and assembly of deformable objects typical to manufacturing applications. Frontiers in Robotics and AI, Nov 2022. URL: https://doi.org/10.3389/frobt.2022.999348, doi:10.3389/frobt.2022.999348. This article has 37 citations and is from a peer-reviewed journal.

31. (kimble2020benchmarkingprotocolsfor pages 3-5): Kenneth Kimble, Karl Van Wyk, Joe Falco, Elena Messina, Yu Sun, Mizuho Shibata, Wataru Uemura, and Yasuyoshi Yokokohji. Benchmarking protocols for evaluating small parts robotic assembly systems. IEEE Robotics and Automation Letters, 5:883-889, Apr 2020. URL: https://doi.org/10.1109/lra.2020.2965869, doi:10.1109/lra.2020.2965869. This article has 149 citations and is from a domain leading peer-reviewed journal.

32. (luo2025fmbafunctional pages 2-3): Jianlan Luo, Charles Xu, Fangchen Liu, Liam Tan, Zipeng Lin, Jeffrey Wu, Pieter Abbeel, and Sergey Levine. Fmb: a functional manipulation benchmark for generalizable robotic learning. The International Journal of Robotics Research, Sep 2025. URL: https://doi.org/10.1177/02783649241276017, doi:10.1177/02783649241276017. This article has 143 citations.

33. (luo2025fmbafunctional pages 1-2): Jianlan Luo, Charles Xu, Fangchen Liu, Liam Tan, Zipeng Lin, Jeffrey Wu, Pieter Abbeel, and Sergey Levine. Fmb: a functional manipulation benchmark for generalizable robotic learning. The International Journal of Robotics Research, Sep 2025. URL: https://doi.org/10.1177/02783649241276017, doi:10.1177/02783649241276017. This article has 143 citations.

34. (delgado2026peginbenchamodular pages 2-3): Y. Delgado, José G. Buenaventura-Carreón, Floris Erich, R. Mykhailyshyn, Tomohiro Motoda, Koshi Makihara, and Y. Domae. Peg-in-bench: a modular benchmark for high-precision robotic insertion. ArXiv, Sep 2026. URL: https://doi.org/10.48550/arxiv.2609.00906, doi:10.48550/arxiv.2609.00906. This article has 0 citations.

35. (delgado2026peginbenchamodular pages 1-2): Y. Delgado, José G. Buenaventura-Carreón, Floris Erich, R. Mykhailyshyn, Tomohiro Motoda, Koshi Makihara, and Y. Domae. Peg-in-bench: a modular benchmark for high-precision robotic insertion. ArXiv, Sep 2026. URL: https://doi.org/10.48550/arxiv.2609.00906, doi:10.48550/arxiv.2609.00906. This article has 0 citations.

36. (vagas2026acrossembodimentgripper pages 2-3): Marek Vagas, Martin Varga, Jaroslav Romancik, Ondrej Majercak, Alejandro Suarez, Anibal Ollero, Bram Vanderborght, and Ivan Virgala. A cross-embodiment gripper benchmark for rigid-object manipulation in aerial and industrial robotics. IEEE Robotics and Automation Letters, 11(5):6194-6201, May 2026. URL: https://doi.org/10.1109/lra.2026.3677707, doi:10.1109/lra.2026.3677707. This article has 0 citations and is from a domain leading peer-reviewed journal.

37. (vagas2026acrossembodimentgripper pages 1-2): Marek Vagas, Martin Varga, Jaroslav Romancik, Ondrej Majercak, Alejandro Suarez, Anibal Ollero, Bram Vanderborght, and Ivan Virgala. A cross-embodiment gripper benchmark for rigid-object manipulation in aerial and industrial robotics. IEEE Robotics and Automation Letters, 11(5):6194-6201, May 2026. URL: https://doi.org/10.1109/lra.2026.3677707, doi:10.1109/lra.2026.3677707. This article has 0 citations and is from a domain leading peer-reviewed journal.

38. (burger2023amobilerobotic pages 62-69): Benjamin Burger. A mobile robotic researcher. ArXiv, Jan 2023. URL: https://doi.org/10.17638/03087073, doi:10.17638/03087073. This article has 4 citations.