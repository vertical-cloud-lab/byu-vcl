# Protocol: one copper-alloy corrosion spot on the CubXL

The per-spot procedure for naval Cu–Ni and nickel–aluminium bronze (NAB), as wrought or cast
references and as single-feed blown-powder laser DED deposits and repairs. It carries the
[aluminum protocol][al-protocol] over to copper, with what the ten Edison answers in
[`copper-ded-edison/`][edison] change. Each change cites its answer, c1-01 to c1-10.

It is a first proposal. Settings marked *choose* are fixed on the reference coupons (§5) before
any comparison is run, then held. Every computed number comes from
[`copper_numbers.py`](copper_numbers.py) → [`copper_numbers.json`](copper_numbers.json).
Positions are in the CubOS deck frame of Ben's 2026-10-02 calibration, as in
[`cubxl-setup.md`][setup]. Nothing here has been bought, built or run.

**What changes from aluminum, in one table**

| | Aluminum plan | Copper |
| --- | --- | --- |
| Headline result | E_pit and E_rp from cyclic polarization | OCP, R_p, the charge of a potential hold, and ICP-MS of the used liquid. Cyclic polarization only on spare spots ([c1-02], [c1-04], [c1-09]) |
| Main chemistry metric | ICP of the tubes in the 2027 batch | ICP-MS of every spot, acidified in the tube at once ([c1-03]) |
| Electrolyte axis | chloride, 0.006–0.6 M NaCl | sulfide dose against exposure history, in fixed substitute ocean water ([c1-06]) |
| Cell | open well, cap resting on the lid | the cap nearly seals the well: a 0.12 mm clearance skirt over the lid's boss, 1.6 µL of water lost an hour ([c1-01], [`cad/`](cad/README.md)) |
| Each piece's second well | a repeat | an OCP-only companion, for the free-corrosion release and an undisturbed film ([c1-06]) |
| First experiment | 8 spots on one reference coupon | the well against a bulk cell, on C71500 and C95800, at three O-ring sizes ([c1-01]) |

## 1. Specimen

Use Ronnie's polishing SOP ([PR #258](https://github.com/vertical-cloud-lab/byu-vcl/blob/157ab1e/SOP/sem-eds-polishing-sop.md))
up to the cut-out, as for aluminum, so one prepared piece serves EDS and corrosion. Where pieces
come from is in [`test-matrix.csv`](test-matrix.csv).

1. **Section** a piece at least 15 mm across for two -006 wells, or 20 mm for one -010 well.
   For a DED pad, cut so the face is a known build plane, and record it: XY (a layer) or XZ
   (contains the build direction), the face's build height, and whether the well sits on a track
   centre or an overlap ([c1-05]).
2. **Mount, grind and polish** with SOP steps 2–9, ending with a bare metal back. Final polish
   (*choose*; [c1-05]'s baseline): SiC to P2400, then 1 µm diamond, then 0.04–0.05 µm colloidal
   silica. Edison found no measured effect of the finish on E_corr or R_p of C71500 or C95800, so the finish is a
   variable to test (§5), not a settled choice. Never change the finish and the alloy at once.
3. **Clean** (*choose*): a short ethanol ultrasonic bath, an ultrapure-water rinse, and a dry
   nitrogen blow ([c1-05]). Check under the microscope for retained silica and, on NAB, for
   pulled-out κ particles.
4. **Time it.** Record when polishing ended, when the piece was dry, and the first fill, with the
   room's temperature and RH. Test after a short fixed delay (*choose*, for example 1 h ± 10 min in
   a desiccator), never after uncontrolled overnight storage. Deliberate air-ageing is a separate
   arm on the reference coupons ([c1-05]). This replaces the aluminum plan's 24 h vacuum-jar age.
5. **Measure the piece's composition** by EDS or XRF on the same face, away from the wells. For
   NAB, map the phases on an etched sister section, not on the test face: an etched face is a
   different surface ([c1-05]).
6. **Screen each well footprint before sealing.** Photograph it with the CubXL camera and under the
   microscope. A footprint with a visible pore, adhered powder, a scratch or resin goes into a
   separate, labelled pore set, not into the intrinsic-material set ([c1-05]). X-ray CT of
   representative deposits, when it is available, finds connected pores the face does not show.
7. **Photograph the face** with the clamp in place, so each spot can be found again in the SEM.

## 2. Cell

The printed tray and the magnetic electrode cap of [`cubxl-setup.md` §3][setup-head], with these
changes.

| Part | What | Why |
| --- | --- | --- |
| Tray | Stations S1–S3 at x 185 / 210 / 235, y 240 hold the pieces; S4 at x 260 holds a PTFE blank disk with the same lid. Coupon face at z 20, lid top at z 26 | S4 is the fixture and carry-over blank (§6) |
| Well | FKM O-ring AS568-006, ID 2.90 mm, cross-section 1.78 mm, squeezed 21 % in a 7.30 × 1.40 mm counterbore: **0.0661 cm² nominal, 0.101–0.126 cm² wetted**. An 8 mm bore above it holds 150 µL | The squeezed ring touches the metal only from r ≈ 1.8–2.0 mm, so the liquid wets 1.5–1.9 times the ID's area, including a thin crevice under the ring ([`cad/README.md`](cad/README.md)). Measure the real area from the attack ring after every test, and report current densities on that area. In [`sim_well_hf.py`](sim_well_hf.md) the crevice carries about 35 % of the anodic current at open circuit on Cu–Ni and 45 % on NAB |
| Calibration wells only | AS568-008 (ID 4.47 mm, 0.157 cm², 10 mm bore) and -010 (ID 6.07 mm, 0.289 cm², 12 mm bore), each in its own lid, same FKM compound as the -006 | Three sizes against a bulk cell (§5) |
| Cap seal | No O-ring. The cap's skirt slides over a Ø16 mm boss around each well with 0.12 mm radial clearance; two 4 × 2 mm magnets in the lid pull on two steel slugs in the skirt and hold it down at an estimated 1.6–2.3 N ([`cad/`](cad/README.md)) | This is the humidified lid c1-01 asks for: the headspace sits near 89 % RH, and water escapes through the gap at 1.6 µL/h, 1.1 % of the well in a 63 min spot (6.1 µL/h with no cap). The surface stays in contact with room air, so it stays air-saturated. A radial AS568-016 seal was the first design. Its pull-off force (2.3–85 N with tolerances and friction) is too close to what the electromagnet can pull on a 1 mm disc (about 23 N), so it is kept only as a fallback (`electrode_cap_oring`, which needs its 0.3 mm vent) |
| Reference | Leak-free Ag/AgCl, ≤ 2 mm, through the cap. Tip **3.0 mm above the metal, in the bore**, not 1.5 mm down in the O-ring's throat as in the aluminum cap | In [`sim_well.py`](sim_well.py) (cap B) the raised tip gives 22 % more O₂ at the spot after 30 min than the 1.5 mm tip, with the current density uniform within 1.4 %. Its uncompensated resistance is 60 Ω in seawater: 4 mV of iR at a 1 mA/cm² reversal, about 0.1 mV in LPR, and under 0.3 mV in the anodic hold. Check it against the master reference each night (*choose* a limit, e.g. ±5 mV) and log the offset |
| Counter | Pt coil around the reference, as for aluminum | During an anodic step the Pt is the cathode, and it can plate out dissolved copper and carry it to the next well ([c1-01]). The carry-over blank (§6) measures this |

Notes:

- **The gantry sets the cap down and the magnet lifts it off** against about 2.4 N (the hold-down
  magnets and two pogo pins of at most 0.4 N each): a margin of 9 at contact. The price is approach
  height: jog the decap height to the disc top within about ±0.15 mm, not PANDA-film's ±3 mm. The two
  hold-down magnets also clock the cap, but 180° is stable too and swaps the reference and counter
  pads, so set the index mark by hand at the park cup; the OCP window at step 3 catches a reversed
  cap. Measure the lift force, the magnet's pull on the real disc, and the water loss on the bench
  before the cap goes on the deck ([`cad/README.md`](cad/README.md), "Still needs a bench test").
- **Expect a ring of attack just inside the O-ring.** Copper alloys show reverse crevice corrosion:
  attack collects on the open surface at the crevice mouth, not inside it ([c1-01]). Photograph
  each spot before and after. A ring at the O-ring edge is not pitting, and not a feature of the
  deposit.
- **Clean or replace the Pt coil between alloys**, not between wells: off the deck, in the morning,
  with the reference protected from the acid ([c1-01]).
- **The cap's moves are the aluminum plan's:** `decap park_cup`, `cap S_k`, measure, `decap S_k`,
  then a dip in each rinse cup. Cap moves happen with no tip on the pipette.

Deck positions used below (all proposals, to be re-jogged):

| Item | Where (x, y) | Holds |
| --- | --- | --- |
| Ben's 9-position 20 mL holder ([`9VialHolder20mL_TightFit.step`](https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/modules/electromagnetic-capper/cad/9VialHolder20mL_TightFit.step), 33.0 mm pitch) | x 318, y 35 + 33k | y 35: spare (FeSO₄ conditioning, non-sulfide nights only). y 68: 1 M trace-metal HNO₃. y 101: ASW. y 134: ASW + 10 mg/L S. y 167: ASW + 0.1 mg/L S. y 200: DI water. **y 233 and 266 stay empty**: y 233 sits under the bare pipette while the capper sets the cap on S4 |
| Rinse cups and park cup (4 mL vials) | (30, 245), (60, 245), (90, 245) | rinse 2: ASW; rinse 1: DI water; park: the reference's storage solution |
| Tube rack, 2 × 8 open 0.5 mL tubes | x 176 + 12k, y 28 / 46 | one tube per well, plus the stock blanks |
| Tip racks | rack 1 Ben's, A1 (291.332, 89); rack 2 A1 (108, 89) | at least 17 tips a night |
| Tip waste | (385, 150) | moved, because the full holder now covers (335, 40) |

## 3. Electrolyte

- **Background: ASTM D1141 substitute ocean water without the heavy-metal stock**, at pH 8.2.
  D1141's optional heavy-metal stock (No. 3) includes copper nitrate. At the standard's dilution
  that is about 10 µg/L of Cu, or 1.6 ng in one well. That is about 40 % of what a mature
  90/10 film releases from a well in an hour (`d1141_heavy_metal_stock_copper` and `icp_ms` in
  [`copper_numbers.json`](copper_numbers.json)). Buy it ready-made without heavy metals, or make
  it from the salts. Filter it after the pH adjustment, and reject a turbid batch: Ca and Mg
  precipitate as carbonate or hydroxide if the pH overshoots ([c1-06]). Measure every batch by
  ICP-MS as its stock blank anyway (§6).
- **Natural seawater later, as its own condition.** It can reverse rankings made in substitute
  ocean water ([`queries.py`][queries], "already established").
- **The series: sulfide dose, in the same ASW, so the background never changes** ([c1-06]).
  Two sulfide stocks, 10 and 0.1 mg/L S as Na₂S, made up in deaerated ASW, with as little
  headspace as possible, and fresh each night (*choose* how long they last, from the start and end
  measurements). Make the 0.1 mg/L stock from the 10 mg/L one, not from solid. Mix each well from
  the stocks, ASW first and sulfide last ([c1-06]):

  | Target, mg/L S | From (µL, per 150 µL well) | P20 transfers | S in the well |
  | --- | --- | --- | --- |
  | 0 | 150 ASW | 8 | — |
  | 0.01 | 135 ASW + 15 of 0.1 mg/L | 8 | 1.5 ng |
  | 0.1 | 150 of 0.1 mg/L | 8 | 15 ng |
  | 1 | 135 ASW + 15 of 10 mg/L | 8 | 0.15 µg |
  | 10 | 150 of 10 mg/L | 8 | 1.5 µg |

  The smallest transfer is 15 µL, well above the P20's 2 µL floor.
- **Tip rules, so no stock is contaminated.** Dispense from above the meniscus, so a tip that has
  touched well liquid never goes back into a stock. A tip that has touched a sulfide stock never
  goes back into the ASW. With ASW first and sulfide last, one fill tip per well satisfies both.
- **Expect the still well to flatten the sulfide response.** The sulfide doses raise i_corr in
  bulk cells several times over (8.44 to 87.39 µA/cm² on 70/30 Cu–Ni at 10 ppm, Yuan 2007, via
  [c1-06]). The well cannot supply oxygen for that: [`sim_well.py`](sim_well.py) caps the
  oxygen-limited current near 6.6 µA/cm² after 30 min, and a metal at 20 µA/cm² in the bulk
  cell reads 0.31 of it in the well. So the dose-response at open circuit will be compressed at
  the top. Read the series from the anodic hold at a fixed potential, which oxygen does not limit,
  and from ICP-MS, and run the 1 and 10 mg/L doses in the bulk cell too.
- **Measure sulfide at the start and the end of the night**, on each stock ([c1-06]). Use
  methylene blue (the CHEMets K-9510 kit reads 0–1 and 1–10 mg/L, with a 0.05 mg/L detection
  limit) or a sulfide ISE. The kit comes with a 25 mL sample cup, so test the parent batch at the
  start and a capped witness vial of the same batch at the end, rather than the 20 mL deck vial.
  The 0.01 mg/L wells hold 1.5 ng of sulfur, below any check, so report them as nominal.
  Edison's two figures for how fast sulfide decays in aerated seawater disagree by more than ten
  times ([`../copper-ded-edison/README.md`][corrections], "Corrections to Edison"), so measure it
  rather than assume either.
- **Never put sulfide and Fe²⁺ on the deck the same night** ([c1-06]). Ferrous-sulfate
  prefilming is a conditioning step for condenser repair, kept for non-sulfide nights.
- **Exposure history is made off the deck**, in beakers, before the piece goes on the CubXL:
  fresh; prefilmed in clean ASW, then sulfided; or sulfided, then clean ([c1-06]). Record each
  step's duration and batch IDs. Durations are *choose*. Yuan 2007's ten days of clean exposure is
  the reference point ([c1-06]).
- **Air-equilibrated only.** An open or vented well cannot hold an oxygen-poor series; that needs a
  sealed, gas-controlled cell ([c1-06]). Log the liquid temperature. A temperature series needs a
  heated stage and is not in this plan.

## 4. Sequence

The main spot, on the first well of each piece:

| # | Step | Settings | Output | Valid if |
| --- | --- | --- | --- | --- |
| 1 | Fill | 150 µL, 8 P20 transfers, ASW first and sulfide last, dispensed from above the meniscus; image the well | — | — |
| 2 | Leak check | 2 min, head camera | — | no liquid outside the O-ring |
| 3 | Cap on | `decap park_cup` (or a rinse cup), `cap S_k`; tipless | — | OCP reads inside an expected window within 30 s (*choose*) |
| 4 | OCP | 30 min (*choose*; the simulated O₂ supply to the spot levels off by then, and E_corr drifts only about 2 mV more over the next 30 min: [`sim_well.json`](sim_well.json) `ocp_in_well`), ≥ 1 point/s | E_corr (mean of the last 60 s), drift | drift over the last 5 min below a limit (*choose*) |
| 5 | LPR (after ASTM G59) | −10 → +10 mV about OCP at 0.167 mV/s, 2 min | R_p in Ω·cm², from the slope at zero current | the fit is linear (*choose* an R² limit) |
| 6 | Rest | OCP, 5 min | — | back within 5 mV of E_corr |
| 7 | Anodic hold | E_corr + 50 mV for 10 min (*choose*), stopped early at 3 mC (*choose*) | i(t) and the charge | charge below the cap |
| 8 | OCP | 5 min | how far E_corr recovers | — |
| 9 | Cap off | `decap S_k`, dip in rinse 1 (DI), then in rinse 2 (ASW) | — | — |
| 10 | Collect | 150 µL plus one 150 µL DI rinse into a pre-weighed 0.5 mL PP tube | tube ID | recovered mass within *choose* % of what was dispensed (weighed in the morning) |
| 11 | Acidify | 20 µL of 1 M trace-metal HNO₃ from the capped acid vial (318, 68), dispensed from above the tube rim with the night's one acid tip, which never touches a sample | 62 mM HNO₃ in 320 µL, pH about 1.2 | — |
| 12 | Image | head camera | — | — |

A main spot is about 67 min of deck time and 63 min of liquid contact. Eight wells (three pieces
with two wells each, plus the two blanks on S4) take about 9 h, so they fit in a 12 h night.
That is 9 tubes with the stock blank, and at least 17 tips (`timing`).

Notes:

- **Report R_p, not a corrosion rate.** The cathodic branch is limited by oxygen transport, and an
  assumed Stern–Geary B is unreliable for these alloys ([c1-03], [`queries.py`][queries]). LPR
  currents span 13 nA (50 kΩ·cm²) to 1.7 µA (400 Ω·cm²) on a -006 well (`lpr`).
- **Set the hold potential against the reference, not against the well's own OCP**, once the
  bulk cell (§5) has given each reference alloy's E_corr. The well's own OCP is biased. In
  [`sim_well_hf.py`](sim_well_hf.md) it reads +4.0 and +7.9 mV from the bulk cell's on C70600 and
  C71500 (the copper that piles up near the metal outweighs the slower oxygen supply) and −28.1 mV on
  NAB, where the oxygen supply wins. The simulated "OCP + 50 mV" hold passes 0.30–0.53 of the
  bulk cell's current. At a fixed potential the current no longer depends on the oxygen supply,
  though in the still well it still depends on how fast dissolved copper diffuses away. Until the
  bulk-cell E_corr exists, OCP + 50 mV is the placeholder.
- **The anodic hold stands in for a galvanic couple** until the ZRA test (§7) measures a real
  couple potential, which then replaces the +50 mV. At the fresh-surface corrosion currents in
  the answers, 1–11 µA/cm², the 10 min hold passes 0.2–2.8 mC. That puts 1–12 mg/L of Cu into the
  well, if all of it leaves as Cu(I) (`anodic_hold`). The charge cap matters for NAB: Ocejo 2022
  measured final currents of 0.92, 2.06 and 82 µA/cm² on cast NAB held for 72 h at −200, −150 and
  −100 mV vs SCE, so 50 mV can multiply the current by 40 ([c1-05]).
- **Acidify at once.** Cu(I) replates or precipitates in near-neutral liquid, and copper sticks to
  polypropylene at neutral pH ([c1-03]). The acid makes the sample total recoverable metal, since
  any precipitate dissolves. A filtered fraction would need filtering before the acid, which the
  deck cannot do ([c1-06]).

**The companion well** (the second well on each piece): the same fill and 63 min of contact, OCP
only, collected and acidified the same way. It matters more than it looked: in
[`sim_well_hf.py`](sim_well_hf.md) the +50 mV hold acidifies the spot to pH 7.2–7.3 on Cu–Ni and 5.8 on NAB
(from Cu₂O formation and Al hydrolysis), against 8.3 at open circuit, so the OCP after the hold reads
a disturbed surface. It gives the free-corrosion release by ICP-MS, and an
unpolarized film for SEM or XPS ([c1-06]). The difference between the two tubes is what the
polarization did.

**Cathodic holds go on separate spots**, collected the same way, because a cathodic step replates
dissolved Cu(I) onto the spot: a −300 mV hold for 10 min after the anodic hold puts 18.5 % of the dissolved Cu back on C71500 in [`sim_well_hf.py`](sim_well_hf.md), and 51 % in the first-order [`sim_well.py`](sim_well.py), which kept all of it as Cu(I) at the metal. The cathodic-protection series holds NAB at
several potentials (*choose* a bracket around a measured in-service propeller potential; [c1-02])
for a fixed time, then measures Al, Cu, Ni, Fe and Mn in each tube. The potential at which Al
release stops is the one that stops NAB's selective-phase attack. Edison found no published value
for it ([c1-02]), and this series measures it directly. Keep the bracket above where the camera
shows hydrogen bubbles. In seawater a cathodic spot also grows calcareous deposits; that is real
cathodic-protection behaviour, so record it rather than avoid it.

**Cyclic polarization only on spare spots, labelled destructive.** Start 50 mV below OCP, sweep at
1 mV/s, reverse at **1 mA/cm², not 10**, and stop back at E_corr. The order-of-magnitude estimate in
`cyclic_polarization` gives the reason. At 1 mA/cm² one scan is about 3.4 mC, or 15 mg/L of Cu in
the well. At 10 mA/cm² it is about 34 mC: 150 mg/L of Cu, and 2.4 mM of OH⁻ from the counter,
as much as the ASW's whole alkalinity. The well's O₂ also runs out in about 3.5 min at 1 mA/cm²,
or 22 s at 10 mA/cm². The ohmic drop stays small: with the reference tip 3 mm up, [`sim_well.py`](sim_well.py) puts the uncompensated resistance at 60 Ω in seawater, about 4 mV at 1 mA/cm² and 40 mV at 10 mA/cm² on a -006 spot. Report the curve as an anodic response, not as E_pit and E_rp:
most wire-arc NAB samples showed no clear pitting range ([c1-02]). Run it last in the night, then
the carry-over blank.

## 5. Calibrate first

Edison found no published small-cell against bulk-cell data for Cu–Ni or NAB ([c1-01]), so this
calibration is the first experiment and a result in its own right.

- **Alloys:** wrought C71500 (70/30 Cu–Ni) and cast C95800 (NAB) first, then wrought C70600
  (90/10 Cu–Ni).
- **Conditions:** -006, -008 and -010 wells on the CubXL, 150 µL each (2.27, 0.96 and
  0.52 mL/cm²), against a 1 cm² bulk cell on the bench (200 mL, 200 mL/cm²). Use the same ASW batch,
  potentiostat, reference and sequence, open to air with a loose cover, unstirred.
- **Replicates:** at least 8 per condition over at least 2 nights. Report the mean and SD of
  E_corr, log R_p, the hold charge, and ICP-MS Cu per cm² per hour. On the bench cell the same
  release rates give 22–44 µg/L of Cu in 200 mL, measurable without dilution (`bulk_cell`).
- **What it decides:** whether the well's bias is small next to the spot-to-spot SD. If E_corr or
  R_p trend with O-ring size, the trend is the artifact and the bulk cell is the anchor.
  [`sim_well_hf.py`](sim_well_hf.md) gives the size to expect with copper's own chemistry. After 30 min the well's i_corr is 0.53, 0.61 and 0.31 of the bulk cell's for C70600, C71500 and C95800, E_corr reads +4.0, +7.9 and −28.1 mV from the bulk cell's, and R_p on the wetted area reads 1.22, 1.08 and 3.17 times the bulk cell's (0.67, 0.60 and 1.75 on the nominal area). The area matters more than the chemistry: report R_p on the wetted area, measured from the attack ring. The first-order [`sim_well.py`](sim_well.py), with oxygen supply as the only difference, had the well's i_corr at 0.93 down to 0.31 of the bulk cell's for bulk i_corr of 1 to 20 µA/cm². **In that model the O-ring sizes will not show the bias:** at 5 µA/cm² the -006, -008 and -010 wells give 0.71, 0.70 and 0.69, because the 4 mm column of liquid sets the oxygen supply, not the spot. A flat size trend does not clear the well. Only the bulk cell can.
- **The finish and delay arms** of §1 run on the same reference coupons, after the size series:
  a SiC-only arm and a diamond-only arm against the baseline, and timed air-ageing ([c1-05]).
- **Cost in deck time:** about 4 nights per alloy for 8 spots at each of the three sizes, plus 8
  bench runs.

## 6. ICP-MS: the sample and its blanks

- **Blanks every night:**
  - a **stock blank**: ASW straight into a tube, plus acid (one per stock used that night,
    *choose*);
  - a **fixture blank**: S4's first well, on the PTFE disk, with the same fill, cap and timing as a
    main spot but the cell off;
  - a **carry-over blank**: S4's second well, after the last anodic spot of the night.
- **Tubes.** Acid-leach the 0.5 mL polypropylene tubes before use (*choose*, e.g. overnight in 2 %
  HNO₃, then an ultrapure-water rinse). Weigh each tube empty and again after collection, on a
  0.1 mg balance, so the recovered volume and the dilution are known. O-ring compounds carry
  metal-oxide fillers, and the fixture blank measures what they add.
- **Analysis: ICP-MS with a collision cell, after a 10× dilution** in dilute HNO₃ ([c1-03]). The
  tube holds about 16 g/L of salts, and the dilution takes it to 1.6 g/L. ⁴⁰Ar²³Na⁺ sits on ⁶³Cu,
  so use the collision cell or read ⁶⁵Cu ([c1-03]). ICP-OES would need about 2 mL, which means
  pooling wells ([c1-03]). On campus this is the Agilent 8900 that #128 is training on
  ([README §1.3][al-readme-icp]). Measure Cu, Ni, Fe and Mn on every tube, Al on NAB, and Cr on
  Cr-modified Cu–Ni.
- **What to expect** in one -006 well after 63 min (`icp_ms`):

  | Release rate (Earley 2020, 90/10 Cu–Ni, via [c1-03]) | Cu per well | After the 10× dilution | Over the 0.13 µg/L detection limit |
  | --- | --- | --- | --- |
  | 100–200 µg/cm²/day, fresh surface | 290–580 ng | 90–180 µg/L | 700–1,400 times |
  | 1.4–3.9 µg/cm²/day, after about 30 days | 4–11 ng | 1.3–3.5 µg/L | 10–27 times |

  The fresh-surface rate is 1.8–3.5 µA/cm² of Cu(I). A one-hour test on a freshly polished spot
  measures the initial release, about 100 times the mature film's ([c1-03]).
- **Expect about half the copper in the tube.** In [`sim_well_hf.py`](sim_well_hf.md), 0.51–0.52 of the copper
  oxidised on Cu–Ni reaches the tube as Cu(I), Cu(II) or suspended Cu₂O; the rest stays on the metal
  as Cu₂O film. That split rests on an assumed film share (0.32–0.62 of it reaches the tube for 60 %
  and 10 %), so the measured split is a result, not a check.
- **Report the dissolution current from ICP-MS next to the charge passed**:
  i_M = n F m_M / (M_M A t). Here m_M is the mass of element M found, M_M its molar mass, n its charge, A
  the area and t the contact time. Edison found no published charge-to-dissolved-metal balance for
  Cu–Ni or NAB ([c1-03]). The gap is what stayed on the surface or replated. 1 mC is 0.66 µg of Cu
  as Cu(I), 0.33 µg as Cu(II), 0.30 µg of Ni or 0.093 µg of Al (`ug_per_mC`).
- **What stays behind:** Cu–Ni and NAB dissolve non-congruently, with Ni, Fe and Al held in the
  film ([c1-03]). EDS or XRF of each spot after the test covers what the liquid undercounts.
- **The naval meaning of the number:** in Earley 2020's Navy Dome test, 90/10 Cu–Ni releasing
  1.4–6.9 µg/cm²/day delayed fouling, while a coating below 0.5 fouled most ([c1-03]). Copper release
  rate is a property with its own naval use (antifouling), not only a corrosion rate.

## 7. Repair coupons and the galvanic test

- **Map the section first**, on an unetched polished face: melt boundary, layers, heat-affected
  zone (HAZ) and substrate ([c1-04]).
- **Each well sits wholly inside one zone**, with clearance equal to the well's wetted radius plus
  the placement tolerance ([c1-04]). With a ±0.5 mm placement tolerance (*choose* once measured),
  a zone must be 3.9 mm wide at a -006 well, 5.5 mm at -008 and 7.1 mm at -010 if the O-ring's ID
  sets the wetted edge (`wells`). The squeezed ring wets out to r ≈ 2.0 mm on a -006
  ([`cad/README.md`](cad/README.md)), which makes it 5.0 mm. So a repair coupon needs at least 5 mm
  of sound deposit in the section: wide pads.
- **A NAB HAZ under 1 mm wide** (Ding 2016, via [c1-05]) cannot be isolated by a 2.9 mm well.
  That needs a smaller capillary cell, validated separately ([c1-05]).
- **A well that crosses the fusion line** is labelled "coupled mixed-area" and is never reported as
  a zone result ([c1-04], [c1-05]).
- **The galvanic couple is a bench test, not a CubXL one.** Cut the deposit and the substrate
  apart, mask each to a known area, and put both in one 200 mL ASW bath, joined through a
  zero-resistance ammeter (ZRA), with a reference in the bath for the mixed potential ([c1-04]).
  - Area ratios: 1:1, and a small deposit against a large substrate, e.g. 1:50 as in Luo 2026
    ([c1-02]).
  - Measure each piece's uncoupled OCP first, and repeat after the films age.
  - A potentiostat in two-electrode mode held at 0 V between the pieces is a ZRA. The mixed
    potential then needs a second channel or a separate high-impedance voltmeter. The
    ESPICO-DK has two channels ([`bom.csv`][bom]).
  - Currents: Luo 2026's 38 µA/cm² at the start is 2.5 µA on a 0.0661 cm² anode. Xing 2023's
    4.43 µA/cm² between a 90/10 HAZ and its weld is 0.29 µA (`zra`), so the range is nA to µA.
  - The measured couple potential then replaces the +50 mV of the anodic hold (§4, step 7).

## 8. Later modules

- **A sealed micro-jet head for flow** ([c1-07]). It can screen how a fresh surface responds to
  flow, and in Metikoš-Huković 2011 it flipped the Cu–10Ni / Cu–30Ni ranking. It needs a sealed,
  pumped head, not an open well. Each run makes hundreds of mL of effluent, collected for ICP as
  timed fractions. It comes after the static test works.
- **Oxide coulometry** ([c1-10]). Reduce the film galvanostatically in deaerated pH 8.4 borate, at
  20–30 µA/cm², which is 1.3–2.0 µA on a -006 spot. 1 nm of Cu₂O is 54 µC on that spot, or 32 s at
  25 µA/cm². CuO is 101 µC, or 61 s (`coulometry`; the CuO figure is the corrected
  1.53 mC/cm², per [`../copper-ded-edison/check_numbers.py`][check]). It needs a galvanostatic
  mode, and deaerated liquid in a sealed cell, so it runs on separate spots and not on the open deck.

## 9. Safety

- **Sodium sulfide.** Na₂S·9H₂O is corrosive, and with acid it gives off H₂S. Make the master stock
  from the solid in a fume hood, in deaerated water. A deck stock holds at most 0.2 mg of sulfur
  (10 mg/L in 20 mL). An acidified sulfide tube can give off at most about 1.5 µg of sulfur as H₂S,
  which is trivial. Still, that is why the acid tip never touches a sulfide liquid. Sulfide needs
  its own SOP entry before it goes on the deck.
- **Nitric acid.** Only 1 M trace-metal HNO₃ goes on the deck, in a capped vial. Dilute it from the
  concentrated acid in the fume hood only, with gloves and eye protection.
- **Polishing** Cu–Ni and NAB is wet, as in the SOP, so no Ni-bearing dust is made.
- **No unattended nights** until the potentiostat has a firmware or host timeout that opens the
  cell, and the protocol switches the cell off before every cap move ([#231](https://github.com/vertical-cloud-lab/byu-vcl/issues/231)),
  as for aluminum.
- **Collected tubes** hold seawater with micrograms of metal in 62 mM HNO₃. Label them, cap them in
  the morning, and store them for ICP.

[al-protocol]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/protocol.md
[al-readme-icp]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/README.md#13-what-dissolves-the-chemistry-link
[setup]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/cubxl-setup.md
[setup-head]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/cubxl-setup.md#3-the-head-what-is-on-it-and-why-nothing-is-added
[setup-first]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/cubxl-setup.md#9-what-to-do-first
[bom]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/bom.csv
[edison]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/README.md
[corrections]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/README.md#corrections-to-edison
[check]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/check_numbers.py
[queries]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/queries.py
[c1-01]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/batch1/c1-01-small-cell-artifacts-cu.md
[c1-02]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/batch1/c1-02-dc-sequence-for-cu.md
[c1-03]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/batch1/c1-03-element-resolved-dissolution-cu.md
[c1-04]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/batch1/c1-04-zone-resolved-repair-electrochem.md
[c1-05]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/batch1/c1-05-specimen-prep-surface-state-cu.md
[c1-06]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/batch1/c1-06-electrolyte-series-naval.md
[c1-07]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/batch1/c1-07-mini-jet-flow-cell-cu.md
[c1-09]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/batch1/c1-09-rapid-solidification-proxies-cu.md
[c1-10]: https://github.com/vertical-cloud-lab/byu-vcl/blob/9e37bb1/alloy-corrosion/copper-ded-edison/batch1/c1-10-coulometric-oxide-reduction-cu.md
