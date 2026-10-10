# First electrochemistry use-cases for the CubXL

Written 2026-10-10 for [issue #213](https://github.com/vertical-cloud-lab/byu-vcl/issues/213). It answers three
questions:

- What should the CubXL's first conductivity / spectroscopy / electrochemistry experiments be?
- Is there an alloy-relevant one?
- How do we make use of what Dr. Jason Porter is working on?

Sources:

- the [Porter conversation notes](https://github.com/vertical-cloud-lab/byu-vcl/blob/f197035/docs/porter-electrochemistry-cubxl-2026-09-14.md)
  and [transcript](https://github.com/vertical-cloud-lab/byu-vcl/blob/f197035/docs/transcripts/RKp4XslErJo-porter-cubxl-electrochemistry.txt).
  Timestamps below point into [the video](https://youtu.be/RKp4XslErJo).
- the [Edison literature review](https://github.com/vertical-cloud-lab/byu-vcl/blob/4166146/docs/edison-sdl-state-of-the-art-2026-09-15.md)
- this repo
- primary sources fetched for this note

**Every DOI below was resolved on 2026-10-10.** Where a fact comes from code or a BOM rather than
from a paper, the text says so. Nothing here has been bought or built yet.

## Recommendation

| | **1 · Porter's speciation data** | **2 · Alloy films for water electrolysis** | **3 · AlSi10Mg corrosion** |
|---|---|---|---|
| What | make blind test sets for his spectrum → species model, then do active learning | electrodeposit Ni–Fe(–Co/–Mo) films, then test OER/HER in KOH | droplet-cell corrosion of our own AlSi10Mg vs. Valimet's |
| Alloy-relevant | no | **yes**: the films are alloys | **yes**: the atomizer program's alloy |
| Uses Porter's modalities | **all three** | UV-Vis + conductivity on the bath; Raman on the film | hardly |
| New hardware | phase 0: none. Phase 1: a ~$230 conductivity kit | potentiostat, electrode head, substrate plate, rinse station | the potentiostat from (2), plus a droplet cell |
| New as a self-driving lab? | spectroscopy in the loop: **yes** | bath monitoring: **probably** | in general **no**; for AlSi10Mg, **yes** |
| First thing that goes wrong | sample volume (§2.4) | Fe impurities in KOH (§3) | polishing coupons is manual |

1. **Start with use-case 1.** It is the only one where someone is already waiting for the result,
   and the gap is one a robot fills directly. Porter has enough data to train his model but not to
   test it. This semester three undergraduates are making his samples by hand (13:22–14:08). It runs
   in open air on aqueous solutions, as he proposed (04:10–04:25). **Phase 0 needs no new
   hardware:** the CubXL makes capped, blinded vials and his lab measures them on its own ATR-FTIR.
2. **Use-case 2 is the alloy one, and the right second step.** AMPERE-2 and CatBot already do
   this. PANDA-film, the system the CubXL's pipette firmware and capper come from, already shows the
   electrode head and well plate for it on a gantry. The new part would be Porter's contribution:
   check every plating bath by UV-Vis and conductivity before it is used. AMPERE-2's code measures
   nothing about the bath beyond what EIS sees, and the literature search found no automated setup
   that monitors a Ni/Fe/Co bath this way.
3. **Use-case 3 is the most directly alloy-relevant, but the least new**, and it needs polished
   coupons. Once use-case 2 has bought the potentiostat, it makes good TMS material. It would be a
   poor first demo.

Fuel-cell testing proper (ORR, membrane-electrode assemblies) needs a rotating disk electrode or a
cell test station, not a pipetting gantry. Half-cell OER/HER in use-case 2 is the way into water
electrolysis.

## 1. What Porter works on

### What he said on 2026-09-14

- **Conductivity plus one optical method.** IR is what he wants. Raman may be easier to
  fiber-couple, and UV-Vis is the easiest of all (01:07–02:13, 04:33–04:39).
- **His rig.**
  - Two syringes, one high-salt and one low-salt, sweep about 15 concentrations.
  - The liquid flows through a gasket, under a four-electrode conductivity cell 3D-printed by
    partners at CU Boulder, and over an ATR crystal.
  - It runs dose, measure, repeat, inside an argon glove box (07:33–11:51).
- **His model.** A Python model predicts every species from the spectrum. It is "a highly
  non-linear mixing problem", so traditional regression fails. He has enough data to train it but
  not to test it (13:22–14:08).
- **His chemistry.** Battery work with salt powders and solvents, in one sulfur and one non-sulfur
  glove box (10:36–10:50). Moisture and oxygen change the powders' conductivity and stability
  (06:19–06:42).
- **What he asked for.**
  - Handle powders as well as liquids, with stirring (12:12–12:23).
  - What he finds new is putting spectroscopy in the loop (03:14–03:38).
  - One test matrix costs about $1,000 in chemicals (02:42–03:07).

### What he publishes

He has been in BYU Mechanical Engineering since 2023, after 2010–2023 at Colorado School of Mines
(OpenAlex; ORCID [0000-0001-5992-8733](https://orcid.org/0000-0001-5992-8733)).

- **Quantitative IR of liquid battery electrolytes, mostly ATR-FTIR.** He measures Li⁺
  concentration, solvent and salt composition, and decomposition.
  - Operando ATR during fast charging: [JES 2021](https://doi.org/10.1149/1945-7111/ac1d7a), and
    [J. Power Sources 2025](https://doi.org/10.1016/j.jpowsour.2025.238058), which measured over 95%
    Li⁺ depletion at the back of the anode.
  - Carbonate decomposition: [JES 2018](https://doi.org/10.1149/2.1051816jes).
- **Machine learning on spectra.** PCA locates the solvation-shifted bands, and a CNN trained on
  spectra of known compositions predicts concentrations
  ([JES 2023](https://doi.org/10.1149/1945-7111/ad017e)). The "Python model" from the conversation is
  most likely this line of work (my inference).
- **Li–S polysulfide speciation** by FTIR, with Raman and DFT/MD alongside.
  - It started in 2017 ([Appl. Spectrosc.](https://doi.org/10.1177/0003702816684638)).
  - It now resolves individual Li₂Sₙ species in TEGDME and DMSO
    ([ECS 2025](https://doi.org/10.1149/ma2025-024721mtgabs),
    [ECS 2026](https://doi.org/10.1149/ma2026-013267mtgabs)).
  - This sits in a DOE consortium with co-authors from NREL and CU Boulder. The sulfur glove box
    fits this work.
- **Transport properties from IR.**
  - One project is an FTIR-ATR Li/Li cell "using small electrolyte volumes, for fast electrolyte
    screening" ([ECS 2022](https://doi.org/10.1149/ma2022-026625mtgabs)).
  - Another is FTIR imaging in a short-path transmission flow cell, with a CNN predicting LiPF₆/EC/EMC
    composition ([ECS 2025](https://doi.org/10.1149/ma2025-01173mtgabs)).
- **He already dissolves powders into liquids.** He measured the solubility of Li, Ni and Co oxides in ten
  deep eutectic solvents, for battery recycling ([J. Mol. Liq. 2025](https://doi.org/10.1016/j.molliq.2025.128875)).
- **No indexed abstract mentions ionic conductivity.** The four-electrode cell he showed is
  unpublished. Conductivity and IR measured on the same liquid is therefore open ground for a joint
  paper.

**In one line:** he uses machine learning to turn vibrational spectra of battery electrolytes into
species concentrations. What holds him back is making enough samples of known composition, and that
is exactly the job a dosing robot is for.

## 2. Use-case 1: a blind-test-set generator for his model

### 2.1 What the CubXL adds to his two-syringe rig

- **More of composition space.**
  - Mixing two stocks only reaches compositions on the line between them.
  - The current six-vial deck column can reach a five-dimensional simplex.
  - A blind test set needs points the training data never visited. The practice the Edison review
    found recommended is Kennard–Stone partitioning plus an independent challenge sample.
- **Blinding built in.** The robot draws compositions from a seed the modeller never sees. Porter
  predicts, and then we unblind. That is the "actual blind study" he asked for (13:52–14:08).
- **Capped samples.** The [electromagnetic capper](../modules/electromagnetic-capper/README.md) keeps
  vials from evaporating while they wait to be measured or are carried to his lab.
- **The loop.**
  - After a first batch, the robot picks the next compositions where his model is least certain.
    That is active learning on model error, not optimisation of a property.
  - It is his "what's the next mix you want to make" (02:20–02:32).
  - With spectroscopy in the loop, it is the part both he and the
    [Edison review](https://github.com/vertical-cloud-lab/byu-vcl/blob/4166146/docs/edison-sdl-state-of-the-art-2026-09-15.md)
    call new. Only Clio/Dragonfly ([Dave et al. 2022](https://doi.org/10.1038/s41467-022-32938-1))
    closes the loop on conductivity, and nothing the review retrieved closes it on conductivity
    *and* spectra.

### 2.2 Phases

| Phase | CubXL does | Measured where | New hardware | Done when |
|---|---|---|---|---|
| 0 | makes capped, blinded samples from 3–6 stocks, logging every dispense | Porter's ATR-FTIR and conductivity cell | none, if volumes fit (§2.4) | his model is scored on a set it never saw |
| 1 | phase 0, plus on-deck conductivity and a visible-absorbance reading | CubXL | conductivity kit; stirring; a fixed cuvette or flow holder for the AS7341 | conductivity matches KCl standards; absorbance is linear across a dye dilution series |
| 2 | closes the loop, picking the next compositions from model uncertainty | CubXL plus Raman, or CubXL feeding his flow cell | OpenRAMAN (separate thread on #213), or a transfer line into his cell | model error falls faster than with random picks |
| 3 | handles non-aqueous, moisture-sensitive chemistry (LiPF₆/carbonates, polysulfides) | in a glove box | glove-box integration ([PR #217 research](https://github.com/vertical-cloud-lab/byu-vcl/pull/217)) | — |

The AS7341 belongs in a **fixed transmission holder**, not on the gantry as a reflectance probe. The
OT-2 colour scans found its spread between positions over an *empty* slot was larger than the paint
signal ([`results-why-only-yellow-2026-09-09.md`](../wireless-color-sensor/ot2/results-why-only-yellow-2026-09-09.md)).

### 2.3 Model chemistries for Porter to choose from

All four candidates meet his first two criteria (04:10–04:25):

- not sensitive to moisture;
- a measurable change in conductivity.

Whether they meet the third, a spectral signature that correlates with conductivity, depends on
which instrument is looking.

| Chemistry | What the spectrum sees | Conductivity | Instrument | Notes |
|---|---|---|---|---|
| **Cu(II) in LiCl or CaCl₂** (optionally Co(II)) | visible colour shifts as chloro-complexes form ([Brugger et al. 2001](https://doi.org/10.1016/s0016-7037(01)00614-7); [Lacarbonara et al. 2023](https://doi.org/10.1016/j.electacta.2023.142514)) | changes with chloride content and pairing | **UV-Vis / AS7341**; the only coloured option | cheap, and Cu is the safer metal. Co speciation in choline chloride–water has been resolved from UV-Vis plus XAS by MCR ([Mannucci et al. 2026](https://doi.org/10.1021/acs.inorgchem.6c01344)), which is close to his solvent work |
| **MgSO₄** | Raman ν₁ ≈ 980 cm⁻¹, with a contact-ion-pair mode at 993 cm⁻¹ ([Rudolph et al. 2003](https://doi.org/10.1039/b308951g)); three kinds of ion pair coexist ([Buchner et al. 2004](https://doi.org/10.1021/jp034870p)) | association constants from conductivity ([Katayama 1973](https://doi.org/10.1246/bcsj.46.106)) | Raman | Epsom salt; the nonlinearity is real but subtle at 25 °C |
| **NaNO₃ / LiNO₃** | Raman and IR resolve ion-paired from solvated nitrate, in D₂O ([Riddell et al. 1972](https://doi.org/10.1139/v72-474)) | measured in the same paper; concentrated-solution data in [Isono 1984](https://doi.org/10.1021/je00035a016) | Raman or IR | cheap; alkali nitrates pair only weakly |
| **LiTFSI in water** ("water-in-salt", [Suo et al. 2015](https://doi.org/10.1126/science.aab1595)) | FTIR and X-ray show the water network breaking into small clusters by 20 m ([Zhang et al. 2021](https://doi.org/10.1021/acs.jpcb.1c02189)) | a full conductivity data set exists ([Ding & Xu 2018](https://doi.org/10.1021/acs.jpcc.8b05193)) | IR (his ATR) | closest to his battery work and to his own TFSI band assignments ([ECS 2022](https://doi.org/10.1149/ma2022-011113mtgabs)); expensive at ~21 m |

**Suggested pairing:**

- LiTFSI–water, or a nitrate, for phase 0, where his ATR is the instrument.
- Cu(II)–chloride for phase 1, where the AS7341 is.
- MgSO₄ once Raman arrives.

**On Ben's idea of doing Raman through the pipette tip.** Polypropylene has Raman bands at 809 and
841 cm⁻¹ ([Minogianni et al. 2005](https://doi.org/10.1366/0003702055012681)). Other PP bands
commonly quoted near 973 and 998 cm⁻¹ would sit on the sulfate band, but they were *not* verified
here. Either way, record an empty-tip blank first.

### 2.4 Sample volume will bite first

- **The pipette.** The P20 Gen2 moves 20 µL per transfer.
- **The vials.** The deck file's vials are 28 mm across
  ([`sterling_6vials.yaml`](../cubos/configs/deck/sterling_6vials.yaml)), so each mm of depth holds
  about 616 µL.
- **The arithmetic.** Covering a dip probe to **15 mm (an assumption: check the datasheet)** takes
  about 9.2 mL. That is about 460 P20 transfers per sample, which is not workable.
- **Fixes, cheapest first:**
  1. Narrower vessels. A tube with a 10 mm bore needs about 1.2 mL for the same depth: ~60 P20
     transfers, or 4 with a 300 µL head.
  2. The 300 µL head ([`digital-pipette-300ul-bom-build.md`](digital-pipette-300ul-bom-build.md)).
  3. A micro-volume flow or capillary cell. This is the geometry Porter already uses, and his 2022
     abstract aims at small-volume screening.

Smaller samples cut the chemical cost of each point, just as active learning cuts the number of
points. Both levers apply to his $1,000 matrix.

## 3. Use-case 2: alloy films for alkaline water electrolysis

### The template exists, in three published systems

- **PANDA-film** ([Quinn et al. 2026, arXiv:2601.07043](https://arxiv.org/abs/2601.07043); PDF in
  [`modules/electromagnetic-capper/paper/`](../modules/electromagnetic-capper/paper/README.md)).
  - It is the CubXL's closest relative: same electromagnetic capper, same Adafruit 6121 TMC2209
    pipette driver, also on a CNC gantry.
  - Electrochemistry runs on a PalmSens EmStat4S in a three-electrode configuration. A Pt-wire
    counter electrode is coiled around a glass capillary that holds an Ag pseudo-reference, all on
    the tool head.
  - The working electrode is the ITO-coated floor of each well in a custom 40-well
    PDMS-on-glass plate.
  - The control software, which drives the potentiostat, runs on a Raspberry Pi (paper §2.2, §2.4).
- **AMPERE-2** ([Fisker-Bødker et al. 2025](https://doi.org/10.1039/D5DD00180C)), for OER. The RSC
  full text blocks bots, so these details come from its
  [code and BOM](https://github.com/AccelerationConsortium/SDL1_OpenTron_electrodeposition) unless
  marked otherwise.
  - Hardware: an OT-2 plus an Arduino, with an Admiral Squidstat Plus.
  - Plate: 15 wells, each 20 mm across and holding 3.9 mL. The sample area is 0.2827 cm², and the well
    cartridge uses nickel tape.
  - Bath: chloride stocks of Ni, Fe, Co, Cr, Mn, Zn and Cu, plus NH₄OH and potassium citrate. The
    bath is mixed ultrasonically and the film deposited galvanostatically.
  - Tests: activation, then CV, EIS (500 kHz–1 Hz), and chronopotentiometry steps from 1 to
    100 mA/cm², all in KOH at 35 °C. The headline metric is the iR-corrected potential at
    10 mA/cm².
  - Cleaning: a flush tool and peristaltic pumps.
  - Throughput: 65 min per sample (abstract).
  - Cost: the minimum-viable BOM totals 5,029, *excluding* the robot and the potentiostat. The
    currency is not stated; the links are mostly amazon.ca.
- **CatBot** ([Freiesleben de Blasio et al. 2025](https://doi.org/10.1039/D5DD00403A);
  [code](https://github.com/Pele905/CatBot_public)), for HER.
  - It deposits onto roll-to-roll Ni wire, optimises Ni–Mo, and uses a Squidstat Plus.
  - Its example run tests in 30 wt% KOH at 80 °C.
  - Its sibling **FastCat** ([Fisker-Bødker et al. 2025](https://doi.org/10.1002/aidi.202500138))
    made over 500 Ni-based multi-element OER catalysts in a closed loop. It found Ni–Fe–Cr–Co
    reaching 20 mA cm⁻² at 231 mV overpotential (abstract).

So the CubXL would not be first to electrodeposit alloys for OER. It can add three things:

1. **Bath monitoring with Porter's modalities.**
   - Ni²⁺, Co²⁺, Cu²⁺ and Fe³⁺ are all coloured, and conductivity tracks ionic strength. Checking
     every bath by UV-Vis and conductivity before deposition makes bath composition a measured
     input rather than an assumed one.
   - A search on 2026-10-10 found no automated setup that does this. The nearest is smartphone
     colorimetry of an electroless Ni bath ([Albizu et al. 2024](https://doi.org/10.1016/j.microc.2024.110073)).
     A 2026 review finds industry still relying on titration and Hull cells
     ([Giurlani et al.](https://doi.org/10.1016/j.aca.2026.346032)).
   - Chloride, ammonia and citrate complexation change the colour too. That is Porter's speciation
     problem in a metals setting (my inference).
2. **Raman of the working film.** [Louie & Bell 2013](https://doi.org/10.1021/ja405351s) saw two
   NiOOH bands in situ in 0.1 M KOH, and their relative intensities shift with Fe content. The
   OpenRAMAN hardware from use-case 1 would serve the alloy work too.
3. **Measure film composition rather than assume it from the bath.** Use offline EDS or XRF, or
   strip the film and read it colorimetrically. Mapping bath to film is another nonlinear inverse
   problem of the kind Porter models.

**Pitfalls, verified:**

- **Fe in KOH activates Ni.** Rigorously Fe-free Ni(OH)₂ shows no significant OER below 400 mV
  overpotential ([Trotochaud et al. 2014](https://doi.org/10.1021/ja502379c), which also gives a way
  to purify KOH). A Ni–Fe campaign run in unpurified KOH partly measures its own contamination.
- **The benchmark is the overpotential at 10 mA cm⁻² of geometric area.** Every non-noble system
  that [McCrory et al. 2013](https://doi.org/10.1021/ja407115p) tested in alkaline solution landed
  at 0.35–0.43 V.
- **Substrate.** PANDA-film's ITO wells held polymer films deposited from an organic stock solution.
  AMPERE-2's well cartridge uses nickel tape. In KOH, follow AMPERE-2.

## 4. Use-case 3: corrosion of the lab's own AlSi10Mg

- **The material.**
  - The atomizer program plans to arc-melt a master alloy from AlSi10Mg powder, atomize it here,
    and compare the result with commercial Valimet AlSi10Mg
    ([`new-arc-melt-utah.md`](meetings/2026-09-17-repowder-install/posts/new-arc-melt-utah.md)).
  - The target is a 20–63 µm cut for laser powder-bed fusion (LPBF)
    ([PR #262](https://github.com/vertical-cloud-lab/byu-vcl/pull/262)).
- **Why corrosion would tell us something.**
  - Laser-melted AlSi10Mg was 2–3× more corrosion-resistant than cast in 0.1 M NaCl, by
    potentiodynamic polarisation and EIS ([Tiwari et al. 2023](https://doi.org/10.3390/coatings13020225)).
  - Its native oxide grows faster, and is more passive, than on the cast alloy
    ([Revilla et al. 2022](https://doi.org/10.1016/j.corsci.2022.110352)).
  - Si content controls how connected the Si network is, and that governs micro-cracking during
    corrosion ([Revilla et al. 2018](https://doi.org/10.1149/2.0101814jes)).
  - Recycled powder coarsened that network, although salt-spray behaviour was "almost the same"
    ([Barile et al. 2022](https://doi.org/10.1007/s43452-022-00375-y)).
  - Oxide on the powder particles grew from ~4 to ~38 nm over ~30 months of reuse
    ([Raza et al. 2020](https://doi.org/10.1016/j.matdes.2020.109358)).
  - So "our own powder vs. Valimet" and "fresh vs. reused" are real questions.
- **On the CubXL.**
  - A droplet or O-ring cell sits on a polished coupon: a cross-section of an arc-melted button, or
    a printed part.
  - In NaCl it runs OCP, EIS and LPR, then potentiodynamic polarisation. That gives the corrosion
    potential E_corr, the corrosion current i_corr and the pitting potential E_pit.
- **Automated precedents.**
  - MAP-E ([Persaud et al. 2026](https://doi.org/10.1038/s41529-026-00822-8)) measured pitting
    potential with a 75 mV standard deviation over 32 automated runs, and built pH–chloride maps for
    304 stainless steel on its own.
  - Scanning droplet cells have been run autonomously ([DeCost et al. 2022](https://doi.org/10.1007/s11837-022-05367-0))
    and used to screen passivation of complex alloys ([Sur et al. 2023](https://doi.org/10.1149/1945-7111/aceeb8)).
  - **No automated or droplet-cell study of AlSi10Mg turned up.** That would be the TMS-sized
    contribution.
- **Limits.**
  - It needs bulk coupons, not powder.
  - Polishing is manual.
  - It hardly uses Porter's modalities.
  - It shares the potentiostat with use-case 2, so it adds little cost once that exists.

## 5. Powder dosing in a smaller module (placeholder)

A candidate module is to be linked on #213. Why it matters here:

- Porter asked for powders as well as liquids (12:12), and his salts arrive as powders
  (10:41–10:50). His deep-eutectic-solvent work also dissolves oxide powders.
- Dosing the salt as a solid removes the ceiling that stock-solution concentration puts on every
  bath and electrolyte. AMPERE-2 and CatBot both work from stock solutions.
- The precedent is [Rahmanian et al. 2023](https://doi.org/10.1038/s41597-023-01936-3), which dosed
  solids and liquids gravimetrically under N₂ and made 96 formulations in 8 h (verified in the
  Edison review).

What to check a candidate against:

- mg-scale resolution when dosing salts;
- a balance in the loop, since gravimetric truth is what makes a blind set trustworthy;
- tolerance of hygroscopic salts (LiCl, LiTFSI, CaCl₂);
- a footprint that fits the deck;
- cleaning between powders.

## 6. Shared hardware, in buying order

| Item | Serves | Status |
|---|---|---|
| 300 µL pipette head | 1, 2 | in design ([`digital-pipette-300ul-bom-build.md`](digital-pipette-300ul-bom-build.md)). Phase 0 waits on it unless the vessels get narrower |
| Conductivity: [Atlas K 1.0 kit](https://atlas-scientific.com/kits/conductivity-k-1-0-kit/) or the [mini K 1.0 kit](https://atlas-scientific.com/kits/mini-conductivity-k-1-0-kit/) | 1, 2 | $229.99 for the K 1.0 kit, priced 2026-09-14 on #213 |
| Stirring | 1, 2 | Porter asked for it; Ben says the magnet capability is already there (12:23–12:38) |
| Potentiostat | 2, 3, Porter's four-electrode cell | not priced here. See below |
| Optics | 1, 2 | AS7341 on hand (fixed holder, §2.2); OpenRAMAN is a separate thread on #213; ATR-FTIR stays in Porter's lab |
| Electrode head, substrate plate, rinse station | 2 (and 3) | open designs from PANDA-film and AMPERE-2 |

**Which potentiostat:**

- **The platform matters.** PANDA-film drove its EmStat4S from software running on a Raspberry Pi.
  The CubXL is controlled from a Pi 5 (arm64).
- **The Squidstat would need a second computer.** AMPERE-2's README says its Squidstat setup "will
  only work on a Windows X86_64 platform". Admiral's current API ships Python wheels only for
  Windows, macOS and x86_64 Linux
  ([AdmiralSquidstatAPI](https://github.com/Admiral-Instruments/AdmiralSquidstatAPI/tree/main/SquidstatLibrary),
  checked 2026-10-10). Neither has an ARM build, so a Squidstat needs an x86 host beside the CubXL.
- **Ask Porter first.** He offered to show what his lab has (07:00–07:18). Ask whether a loan is
  possible before buying.

## 7. Questions to settle

**For Porter:**

1. Which chemistry should the first blind set use: one from §2.3, or whatever his current model is
   trained on, if that is stable in air?
2. Does his model take only IR, or would Raman or visible spectra of the same samples help?
3. How many blind samples does he need, and over what composition ranges? Is phase 0 (we make the
   vials, his lab measures them) useful now?
4. Will he share the four-electrode cell design and protocol he offered (07:18–07:28, 09:17–09:21)?

**For VCL:**

1. Should we borrow or buy a potentiostat, and is it the EmStat4S (Pi-friendly, PANDA-film code)
   or the Squidstat (AMPERE-2/CatBot code, needs an x86 host)?
2. How high a priority is the 300 µL head, given that phase 0 waits on it?
3. Will arc-melted AlSi10Mg buttons exist soon enough to make use-case 3 worth scheduling?
