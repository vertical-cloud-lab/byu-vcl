# Question

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
