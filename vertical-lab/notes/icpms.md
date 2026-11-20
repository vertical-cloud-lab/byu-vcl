# An ICP-MS station of the lab's own, its acids in a fume hood (round 13, run D)

Sterling on PR #318 (2026-11-20, on round 12's video):

> Do we have ICP-MS as a module? If not, we should. Also, an OT-2 probably doesn't have great compatibility with many
> of the solvents that would be required for ICP-MS and ICP-OES. And it would be very risky to try to put high-hazard
> chemicals on a tray. This would be better for a standalone fumehood, and probably with a liquid handler that's
> designed for those kinds of harsh solvents (maybe Hamilton? Really expensive, but we need good chemical
> compatibility..). On a similar note, we might need a similar kind of sleeve or protection for the UR arms.

**Was there one? No.** Until now the corrosion wells' samples were diluted by the OT-2 on tray A and sent to the BYU
Spectroscopic Facility (Agilent 8900; DAL's FLAIME proposal), and nothing in the lab digested a build for its
composition. The model is [`icpms.py`](../icpms.py): `xvfb-run -a python3 icpms.py` renders the clip,
`python3 icpms.py bom` writes [`out/icpms_bom.json`](../out/icpms_bom.json).

Provenance tags: **[M]** published by the maker; **[3P]** a dealer, distributor or other third party; **[E]** our
estimate or arithmetic. "(snippet)" means the figure came from a search extract because the page blocked fetching
(agilent.com returned 403 to the runner); check it before relying on it.

## What the station is

| Part | What | Size W x D x H, mass | Why this one |
|---|---|---|---|
| ICP-MS | **Agilent 7850** | 730 x 600 x 595 mm (655 with its duct collar), 100 kg [M, A1/A2] | Ultra-high-matrix aerosol dilution (UHMI) is standard: "up to 25% total dissolved solids" [M, A4 (snippet)], so the seawater electrolyte (3.5 % TDS) needs no big liquid dilution. Agilent is what BYU's facility runs (an 8900), so methods carry over |
| Autosampler | **Agilent SPS 4**, under its vented cover | 600 x 363 x 510 mm, 15 kg [M, A1] | Its cover is exhausted at 50-100 L/min through a 50 mm port "when corrosive liquids are loaded" [M, A1]. The cover's lid actuator is ours, so the arm can load from above |
| Chiller, forepump | Agilent G3292A chiller; the 7850's own forepump | 368 x 702 x 576 mm, 85 kg, 2900 W; DS402 (the 7800's): 164 x 541 x 242 mm, 35 kg [M, A1]. The 7850's pump wasn't confirmed | Under the bench, the pump on a drip pan |
| Argon | **180 L liquid argon dewar, 22 psi** | Ø 508 x 1635 mm, about 143 m³ of gas [3P, G1] | 20 L/min of plasma gas [M, A1]: about 119 h of plasma a dewar, three weeks of 8 h days less boil-off [E]; PerkinElmer: "expect a new dewar every 2-3 weeks" [M, P1]. A 47 L cylinder would last about 5 h [E] |
| Fume hood | **HEMCO UniFlow Trace Metals, 6 ft**, metal-free polypropylene, on a ventilated acid cabinet | 72 x 32 x 59 in = 1829 x 813 x 1499 mm [3P, F1]; base cabinet and work surface (900 + 32 mm) [E] | One-piece welded polypropylene chamber and baffle; four horizontal sliding sashes on two tracks, so at most half open [M, F2 (snippet)]. A perchloric hood isn't needed for HNO3/HCl [3P, F5, F6]; check with BYU EHS, since one university manual asks for special hoods for hot acid digestion [3P, F7] |
| Digestion | Graphite hot block (**SCP Science DigiPREP** class), 24 x 50 mL PP tubes | 500 x 400 x 280 mm [E, not published] | Up to 450 C [3P, D2]. HNO3 + HCl, aqua regia (3:1 HCl:HNO3) for the copper alloys; never sealed [3P, D6] |
| Acid-rated dilutor | **Questron (HORIBA) QPrep** class, with a decapping head (ours) | 840 x 550 x 700 mm [E: QPrep's size isn't published] | "All-plastic construction", a "Teflon-coated rigid graphite probe", "capable of handling HF solutions"; dilutes, spikes internal standard, makes up standards, fills racks [M, Q1]. PFA lines and syringe pumps: no metal or PEEK where the acid goes |
| Acids | HNO3, HCl, ultrapure water, in PFA bottles in a PP tray | 1 L bottles | Only here, inside the hood. **No HF anywhere** |
| Arm cover | **PTFE-laminate robot suit** for the UR12e (Roboworld Robosuit class) | to fit | "10-mil laminated Teflon" for "caustic chemical environments", zips or hook-and-loop; quote only; no maker publishes an IP rating [M, R1; 3P, R2]. The UR12e is IP54, and UR says where liquids are present "additional measures should be taken, such as utilizing a protective robot cover" [M, U1, U3] |
| Racks | 15 mL PP tubes, 4 x 6, with a central T handle for the 2F-85 (ours) | 190 x 176 x 178 mm | The arm carries the capped sample rack in and the open autosampler rack (2 % HNO3) out: never an open concentrated acid |

### Why not a Hamilton (or the OT-2)

| Handler | What the acid touches | What the maker says | Fit |
|---|---|---|---|
| Opentrons OT-2 / Flex | 100 % PP tips; pipettes of PC-ABS with NBR and silicone O-rings [M, O1] | "Keep corrosive materials, agents, or otherwise damaging materials away from the robot"; its HEPA module "doesn't provide operator protection like a fume hood" [M, O1, O2] | Fine for the electrolyte and buffers on tray A; not for the acids |
| Hamilton Microlab STARlet / STAR (CO-RE air displacement) | stainless 1.4305, EPDM, PEEK, ZrO2, PTFE [M, H1] | Its own resistance table rates the CO-RE head **3, "not recommended for continuous contact", for 5-10 % and for 70 % nitric acid**, PP 4 ("severe") for 70 % HNO3, and pitting on the steels with 20 % HCl; for corrosive liquids it asks for "an exhaust suction device to remove corrosive fumes away from the deck" [M, H1] | STARlet 1124 x 795 x 903 mm, 135 kg [M, H1]: most of a 6 ft hood. No price found |
| Hamilton Microlab 600 (syringe dilutor) | glass syringes, PTFE [M, H2 (snippet)] | Its compatibility FAQ lists conc. nitric acid as A/A/A-B/A-B (column headers not seen) [M, H2 (snippet)] | A bench dilutor, one sample at a time: a good fit if Hamilton is wanted |
| Gilson GX-271 ASPEC | FEP, PTFE, PEEK, glass, ceramics [M, G1] | Of PEEK: "Avoid concentrated sulfuric or nitric acids (over 10%)" [M, G1] | 597 x 541 x 571 mm, 22 kg |
| ESI prepFAST + SC-4 DX | fluoropolymer probe guide [M via distributor, E1] | inline 1-400x autodilution and internal standard [M via distributor, E1] | Beside the ICP-MS, after the hood: a cleaner alternative to the SPS 4 |
| Teledyne CETAC ASX-560 (+ ENC-560DC) | "chemically resistant materials" [M, C1] | enclosure with a 4 in exhaust at 12-15 cfm [M, C1] | 580 x 560 x 620 mm, 11.7 kg |

So the recommendation is the reverse of a general-purpose deck in a hood: an all-fluoropolymer dilutor (QPrep class)
for the concentrated acids, inside the hood, and the ICP-MS's own autosampler (or an ESI prepFAST) for the final
dilution, outside it. The arm only moves racks.

### ICP-MS or ICP-OES?

- **Percent-level composition of the Al and Cu alloys: ICP-OES.** ASTM E3061-24 (Al alloys) is an ICP-AES method [M
  (ASTM), D1]; the majors would need dilutions of 10⁴ or more on an ICP-MS [E]. An Agilent 5800 is 625 x 740 x 887 mm,
  about 90 kg, 16.7 L/min of argon [3P, X4; M, A6]; a Thermo iCAP PRO 615 x 690 x 933 mm, 80 kg [M, T3].
- **Trace metals leached into the corrosion electrolyte: ICP-MS**, with aerosol dilution for the salt.
- **This station** is an ICP-MS, because the corrosion screen is what sends samples today; an ICP-OES of about the same
  size could stand on the same bench, sharing the argon, chiller and hood. That is a choice for Sterling.

### Digesting the alloys without HF

- **Cu-10Ni and NAB (C63000):** HNO3 + HCl, or aqua regia, in the hot block [M, D4; M, D5 (snippet)]. Validate Al
  recovery from NAB against a reference material [E].
- **Al alloys:** HCl finished with HNO3 takes the matrix [E]. **Silicon over about 1 % won't dissolve without HF**
  [3P, D7 (snippet)]; alkaline (NaOH) dissolution works for Al-Si with 7.8-13.4 % Si [3P, D8 (snippet)] but is slow
  and adds sodium [3P, D9 (snippet)]. **So Si (and the majors, as a cross-check) comes from the XRF** in chapter 4;
  everything else from HF-free acid digests.

### The seawater samples

A tenfold liquid dilution of 3.5 % TDS electrolyte still leaves about 0.35 % TDS, above Thermo's 0.2 % rule of thumb
for plain ICP-MS [M, T2]. With UHMI (Agilent), AGD (Thermo) or AMS (PerkinElmer) the instrument dilutes the aerosol
instead [M, A4, T2, P2]. The clip's dilutor makes the tenfold dilution into 2 % HNO3 with an internal standard; the
7850 does the rest.

## Utilities, and what it costs

| | ICP-MS (7850) | The station |
|---|---|---|
| Power | 200-240 V single phase on a 30 A circuit, NEMA L6-30P [M, A1] | plus the chiller's 12.2 A, the hood's lights, the hot block (about 2 kW [E]) |
| Argon | 20 L/min at 500-700 kPa [M, A1] | a 180 L dewar, its regulator within 3 m [M, P1] |
| Exhaust | its own 150 mm drop, 5-7 m³/min [M, A1]; PerkinElmer asks for a dedicated vent [M, P1] | the SPS 4's cover (50 mm port, 50-100 L/min) and the hood's own duct (a 6 ft hood is about 690 cfm with the sash open: Labconco's figure for its XStream [M, F3]) |
| Cooling | up to 4.5 kW into the water and the duct [M, A1] | the G3292A chiller, 2.9 kW |
| Price | **$160-220k** for a 7850 (LabX's 2026 buyer's guide [3P, X1]); a 2017 Agilent quote: 7800 system $215,975 list, **$122,526 net**; a 7900 with UHMI $162,005 net; SPS 4 $12,305 list [M, A3]; refurbished 7850s at $100-120k [3P, X2, X3] | the hood, dilutor, hot block and arm cover are quote-only |

All of these go in #331's quote requests.

## Where it goes on the floor (for run A)

The station is 4.3 m along its wall (hood, bench, dewar) and 0.81 m deep, plus about 1 m in front for the MiR250. The
current floor (`setup_lab.FLOOR_PLAN`, [`out/tray_plan_floor.png`](../out/tray_plan_floor.png)) has no 4.3 m gap in
either row, so:

- **Suggested: the south row's east end, past the wire EDM**, where about 3.8 m of row front is free from x ≈ 7,850
  (the EDM ends at about 7,650) to 11,650, the fronts on the row line (y = −6,238) facing north. Turned to face north,
  the model's left and right swap: the bench with the ICP-MS at the west end (x ≈ 7,850-9,650), the hood at the east
  end (x ≈ 9,750-11,580), and the dewar behind the bench (y ≈ −7,500) instead of beside it, which saves 0.6 m. The
  MiR docks 60 mm off the hood's front with its centre 60 mm inside the hood's edge next to the bench (x ≈ 9,810), as
  in the clip: the hood's open half and the SPS 4 are both in reach from there. It stays 1.9 m clear of the Meltio
  cell (y < −9,000). In `FLOOR_PLAN` terms, roughly `"icpms": (9715, "S", 0.0, 9810)` without the dewar; check which
  way `setup_lab` mirrors a south-row machine.
- **Or a room of its own.** ICP-MS labs are usually separate: clean air for trace metals, the acids away from metal
  powder and the robots. If the building has a room off the floor with a door the MiR can open, that is the better
  place; the station and the clip are the same.

## How the arm works it, and what it is protected from

- The arm reaches into the hood through its open half, as a person does: four panels on two tracks, three slid behind
  the first. Only the gripper, the wrist and the rack pass the sash plane.
- It carries capped tubes in and an autosampler rack of dilute acid out. The concentrated acids never leave the hood;
  the dilutor's head (ours) unscrews each tube's cap, takes its aliquot, dilutes it into the autosampler rack and puts
  the cap back.
- Its cover is drawn as a loose skin about 6 mm off the shoulder, upper arm, forearm and wrists 1-2. The collision
  check works on the arm's own bodies (`collide.ArmBodies`), so the cover itself isn't checked; a real suit's bulk at
  the elbow and wrist is for a fitting.

## The clip (`icpms.py`)

Eight steps, about 85 s, collision-checked as it renders (`VIZ3D_AUDIT=1`, round 11's strict rules): the station; the
MiR250 + UR12e driving in at its published 0.3 m/s²; the sash; the capped rack into the hood; the dilutor's cycle on
tube 0 in full; the hot block; the autosampler rack to the SPS 4; the SPS 4 sampling, with the utilities and costs.

**Ours, at assumed sizes:** the station's layout, the racks and their handles, the MiR's rack carrier, the dilutor's
geometry and decapping head, the SPS 4 lid's actuator, the hot block's size, the base cabinet. **Not modelled:** the
waste carboy in the acid cabinet, the scrubber (Questron sells one rated over 90 % for HNO3 [M, Q2 (snippet)]), the
ICP-MS's cones and torch.

## Sources

**Agilent.** A1: 7800/7900 ICP-MS Site Preparation Checklist G8400-90020 rev B (2016), [Wayback copy](https://web.archive.org/web/20160615024950id_/http://www.agilent.com:80/cs/library/sitepreparationchecklists/G8400-90020_B.pdf).
A2: [the 2024 edition](https://www.agilent.com/cs/library/sitepreparationchecklists/G8400-90020_SitePrepChecklist7900EN.pdf), with a 7850 row (the Chinese edition G8400-97020, in search extracts: 59.5 x 73.0 x 60 cm, 100 kg).
A3: Agilent quotes 2290454 (7800) and 2290536 (7900), [West Virginia bid file, 2017](http://www.state.wv.us/admin/purchase/Bids/FY2017/B_1400_AGR1700000016_04.pdf).
A4: [7850 product page](https://agilent.com/en/product/atomic-spectroscopy/inductively-coupled-plasma-mass-spectrometry-icp-ms/icp-ms-instruments/7850-icp-ms).
A6: [5800/5900 ICP-OES user's guide](https://icp-oes.help.agilent.com/en/Manuals/Agilent_5800-5900_UG_EN.pdf).
**Thermo.** T2: [TN001705, argon gas dilution](https://documents.thermofisher.com/TFS-Assets/CMD/Technical-Notes/tn-001705-icp-ms-argon-gas-dilution-tn001705-en.pdf).
T3: [iCAP PRO operating manual](https://knowledge1.thermofisher.com/@api/deki/files/34809/iCAP_PRO_Series_OM.pdf?revision=1).
**PerkinElmer.** P1: [Preparing your lab for the NexION 1100/2200](https://perkinelmer.widen.net/content/w5wsbl6zpx/pdf/gde-nexion-1100-2200-icp-ms-prep-your-lab.pdf?u=mzx6xj).
P2: [NexION 2200 page](https://perkinelmer.com/product/nexion-2200-icp-ms-N8170012).
**Liquid handlers.** O1: [OT-2R user manual](https://insights.opentrons.com/hubfs/Products/OT-2/OT-2R%20User%20Manual.pdf); O2: [Flex manual](https://insights.opentrons.com/hubfs/Products/Flex/Opentrons%20Flex%20manual%20REV3.pdf);
H1: [Microlab STAR line operator's manual 627043_04](https://www.gmc.vu.lt/images/GMKC/Bioinzinerijos_lab/Microlab_STAR_Line_Operators_Manual_.pdf); H2: [Hamilton FAQ, Microlab 600 fluid path](https://www.hamiltoncompany.com/knowledge-base/faq/will-the-microlab-600-fluid-path-be-compatible-with-my-solvents);
G1: [Gilson GX-271 ASPEC user's guide](https://cdn.labwrench.com/eMan/manualNo/2927/gilson_gx_271_aspec_manual.pdf); E1: [ESI prepFAST (Thermo catalogue)](https://www.thermofisher.com/order/catalog/product/1378910);
C1: [Teledyne CETAC ASX-560 brochure](https://www.teledynelabs.com/en-us/resources/Documents/Brochures-Datasheets/ASX-560_family_brochure.pdf); Q1: [HORIBA/Questron QPrep](https://www.horiba.com/gbr/products/detail/action/show/Product/qprep-1897); Q2: [HORIBA/Questron Vulcan](https://horiba.com/usa/products/detail/action/show/Product/vulcan-by-questron-1896).
**Digestion.** D1: [ASTM E3061-24](https://store.astm.org/e3061-24.html); D2: [DigiPREP (SelectScience)](https://www.selectscience.net/product/digiprep-block-digestion-systems); D4: [Thermo AN43146](https://assets.thermofisher.com/TFS-Assets/CMD/Application-Notes/AN-43146-ICP-OES-Trace-Elements-Steels-Alloys-AN43146-EN.pdf);
D5: [Agilent 5991-8120EN](https://agilent.com/cs/library/applications/5991-8120EN_MP-AES%20Metals%20in%20ore.pdf); D6: [U. Waterloo ICP sample-prep SOP](https://uwaterloo.ca/chemical-engineering/sites/default/files/uploads/documents/che-sop-icp-sample-prep_1.docx);
D7: [Inorganic Ventures, silicon in metals](https://www.inorganicventures.com/advice/dissolution-silicon-metals); D8: [Al-Si alkaline dissolution (2025)](https://castjournals.cast.org.cn/joweb/qcgyycl/EN/PDF/10.19710/J.cnki.1003-8817.20250032); D9: [US 4151253](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4151253).
**Hoods.** F1: [HEMCO UniFlow Trace Metals (LabWrench)](https://www.labwrench.com/equipment/15490/hemco-corporation-uniflow-trace-metals-fume-hood); F2: [HEMCO Polypro trace-metal hoods](https://www.labmanager.com/polypro-trace-metal-fume-hoods-22651);
F3: [Labconco XStream datasheet](https://www.labconco.com/p/protector-xstream-laboratory-hoods/datasheet); F5: [WSU EHS, perchloric acid](https://ehs.wsu.edu/iii-c/iii-c-1/); F6: [CMU EHS, perchloric acid](https://www.cmu.edu/ehs/Laboratory-Safety/chemical-safety/documents/ehs-guideline---using-perchloric-acid.pdf);
F7: [UGA, fume hoods](https://research.uga.edu/docs/units/safety/manuals/ChemicalSafetyManual/Fume_Hoods_and_Other_Exhaust_Devices.pdf).
**UR and covers.** U1: [UR12e datasheet](https://www.universal-robots.com/manuals/latest/en/datasheets/ur12e/); U3: [UR, robot care in uncontrolled environments](https://www.universal-robots.com/articles/ur/robot-care-maintenance/removal-of-blue-lids-in-uncontrolled-environment/);
R1: [Roboworld on the UR+ marketplace](https://www.universal-robots.com/marketplace/products/01tP40000071NgUIAU); R2: [qviro, Roboworld UR10/UR10e Robosuit](https://qviro.com/product/roboworld/universal-robots-ur10-ur10e-robosuit/specifications).
**Prices.** X1: [LabX, best ICP-MS systems of 2026](https://www.labx.com/resources/the-best-icp-ms-systems-of-2026-a-buyers-guide-to-price-and-features/4945) (written with AI assistance, then reviewed); X2: [Quantum Analytics, refurbished 7850](https://store.lqa.com/product/3322-agilent-7850-icp-ms-w-chiller-sps-4-he-collision-software-pc/); X3: [EquipNet 7850](https://www.equipnet.com/agilent-technologies-7850-icp-ms-with-agilent-listid-1076567/); X4: [speciation.net, Agilent 5800](https://speciation.net/Appl/Techniques/technique.html?id=3354).
**Argon.** G1: [Airgas, 180 L argon at 22 psi](https://www.airgas.com/product/Gases/Argon/p/AR%20180LT22).

**Not found in the time:** the 7850's current site-prep sheet (blocked), its forepump model, list prices for the
NexION 2200, iCAP RQ, Hamilton STAR, ESI prepFAST and ADS 2, the sizes of the QPrep, Vulcan and DigiPREP, the CEM and
Milestone automated microwave digesters, the HEMCO hood's price, and the Roboworld suit's size and IP rating.
