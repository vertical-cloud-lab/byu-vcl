# The CubXL corrosion plan for copper: follow-up Edison queries

Written 2026-10-18 for [PR #278](https://github.com/vertical-cloud-lab/byu-vcl/pull/278). Sterling
asked for "a follow-up set of Edison scientific queries in the context of doing this for copper,
focused on naval applications, leveraging directed energy deposition, single stream
powder-based", cross-referencing
[digital-alloy-lab PR #117](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/117).

**Status: run, 2026-10-18.** All ten tasks succeeded: submitted 01:19–01:20 UTC, finished
between 01:39 and 01:53. An earlier attempt the same night (00:48–00:51 UTC) got `403 Forbidden`
from Edison's login. On the re-run, `EDISON_PLATFORM_API_KEY` passed Edison's credential check.
Nothing here records whether the secret was replaced in between or the fault was Edison's. The
[synthesis](#what-came-back) is below. Each answer is in [`batch1/`](batch1/) and each full trajectory in [`raw/`](raw/).

| File | What it is |
| --- | --- |
| [`queries.py`](queries.py) | The ten questions, with the shared context, "already established" and output blocks |
| [`edison_corrosion_cu.py`](edison_corrosion_cu.py) | Submit, wait, fetch and status, laid out like PR #117's `edison_cu_ded.py` |
| [`_task_ids.json`](_task_ids.json) | Task IDs, submit and fetch times |
| [`batch1/`](batch1/) | One file per question: the question, then Edison's answer with its reference list |
| [`raw/`](raw/) | The full verbose trajectory of each task, gzipped JSON |
| [`check_numbers.py`](check_numbers.py) → [`check_numbers.json`](check_numbers.json) | Arithmetic checks on Edison's numbers, and the numbers this README adds |

## What these ask, and why

PR #117's 53 queries (`edison-trajectories/cu-ded-2026-10/`) already cover the alloys, powder
making, DED process windows, film mechanisms, short against long tests, and corrosion metrology in
general. They don't cover the test this folder's parent plans: a 3–4 mm O-ring well holding about
150 µL on a polished cross-section, a low-cost potentiostat, and ICP of the used liquid. These
questions ask what that test becomes for Cu–Ni and NAB in naval service. Each one carries over a
named part of [the aluminum plan](../README.md).

The shared context fixes the target as single-stream blown-powder laser DED, meaning one
pre-alloyed powder feed, not in-situ blending, which is how PR #117 used the term. A block of
"already established" findings from PR #117 (films take months to mature, Tafel and assumed-B
pitfalls, natural seawater reversing rankings, DeCost 2022 being simulated, MAP-E) tells Edison
not to re-derive them.

| Name | Job | What it asks | Carries over |
| --- | --- | --- | --- |
| `c1-01-small-cell-artifacts-cu` | LITERATURE_HIGH | What goes wrong for copper alloys in an open 10–200 µL well: dissolved Cu redepositing, oxygen supply, evaporation, pH at the counter, crevice attack under the O-ring, area effects | §4 "Things that will bite". Copper's cathodic reaction is oxygen-diffusion-limited, and its dissolved metal plates back out, so the small well matters more than it does for Al |
| `c1-02-dc-sequence-for-cu` | LITERATURE | What replaces the G61-style cyclic polarization for alloys that corrode actively. Holds at cathodic-protection and galvanic-couple potentials. Current and potential ranges, to size the potentiostat | The protocol's sequence and §5's potentiostat spec. PR #117's b5-06 asked about measurement pitfalls and a one-hour protocol in general, not cyclic polarization, holds or current ranges |
| `c1-03-element-resolved-dissolution-cu` | LITERATURE_HIGH | AESEC, flow-cell ICP-MS and offline ICP of Cu–Ni and NAB: congruent or selective dissolution, faradaic balance, sodium matrix effects. Copper release rates, antifouling, and limits on copper discharge | §1.3, the chemistry link. For a naval copper alloy, its copper release rate is a property in its own right |
| `c1-04-zone-resolved-repair-electrochem` | LITERATURE | Deposit, fusion zone, HAZ and substrate compared by microcapillary cell, SDC, SVET, SECM and SKPFM; galvanic coupling; where to put wells on a repair cross-section | The repair coupons, and PR #117's open item 5 (masked zones plus a ZRA test) |
| `c1-05-specimen-prep-surface-state-cu` | LITERATURE | Final polish, delay and cleaning; as-deposited, machined or polished faces; build-plane orientation; pores acting as crevices | The polishing SOP (#258) and the XY/XZ comparison |
| `c1-06-electrolyte-series-naval` | LITERATURE | Which series mixed from stocks (chloride, sulfide, oxygen, pH, ammonia, ferrous dosing, temperature) gives each alloy a slope, and how to keep it stable in an open well | The 0.006–0.6 M chloride series |
| `c1-07-mini-jet-flow-cell-cu` | LITERATURE | Can a syringe- or peristaltic-fed micro-jet on a 3–4 mm spot screen erosion-corrosion, and what wall shear does it take to match 3–4 m/s pipe limits | New. Flow-driven attack is a well-known failure mode of Cu–Ni seawater piping, and the plan has no flow |
| `c1-08-precedent-automated-cu-corrosion` | PRECEDENT | Has anyone automated corrosion tests of copper alloys, especially printed or weld-repaired ones, or paired them with ICP of the electrolyte? | The novelty check of §2 and §7 |
| `c1-09-rapid-solidification-proxies-cu` | LITERATURE | Do laser-surface-melted, single-track, splat or arc-melted forms predict the corrosion of a multi-layer DED deposit? | §1.2, leftovers against the print, and the atomizer's splats and skull |
| `c1-10-coulometric-oxide-reduction-cu` | LITERATURE | Can cathodic reduction on the same potentiostat measure the oxide films on Cu–Ni and NAB, and the oxide on copper powder, compared with inert-gas fusion? | PR #117's "measure oxygen per lot by inert-gas fusion" (b3-10). It would be a second use of the potentiostat |

## What came back

These are Edison's answers, read and checked by Claude (2026-10-18). The primary papers were not
re-read here, so each number is as good as Edison's reading of its source. Each answer cites page
ranges for its claims, which makes spot-checking quick. Where a number below is computed rather
than quoted, it comes from [`check_numbers.py`](check_numbers.py).

### The short version

1. **Nobody seems to have done this yet, but the open space is narrow** (c1-08). Edison found no
   publication that combines robotic or gantry corrosion testing of additively made or weld-repaired copper alloys with
   element-resolved analysis of the used liquid. Each half has been done separately. A defensible
   claim is *automated, zone-resolved, chemistry-linked tests of single-feed copper-alloy DED
   deposits and repairs*. Automation, O-ring cells and copper-alloy jets are not new.
2. **Cyclic polarization should not be the headline result for copper alloys** (c1-02, c1-04,
   c1-09). Cu–Ni and NAB corrode actively under a film rather than pitting from a passive state.
   In the closest additive study (wire-arc NAB, Shahriari 2023), most samples showed no clear
   pitting range. Lead with OCP, the measured LPR slope, and holds at
   measured service potentials. Run cyclic polarization only on spare spots, labelled as a
   destructive test.
3. **ICP of the used liquid becomes the main metric, if the sample is handled right** (c1-03).
   Acidify each sample as soon as it is collected, or Cu(I) plates back out or precipitates. Use
   ICP-MS, not ICP-OES. Copper alloys dissolve non-congruently: Ni, Fe and Al stay behind in the
   film. So the liquid alone undercounts them, and the spot needs EDS or XRF too.
4. **The chloride series is not the right axis for copper.** For naval copper alloys, the useful
   axis is sulfide dose against exposure history, in a fixed seawater background (c1-06).
5. **A 3–4 mm well cannot isolate a heat-affected zone narrower than 1 mm** (c1-04, c1-05,
   c1-09). Repair coupons need wide pads, wells placed wholly inside a zone, and a separate
   two-piece galvanic test.
6. **Edison found no study that calibrates a small well against a bulk cell for Cu–Ni or NAB**
   (c1-01).
   That makes calibration against wrought C71500 and cast C95800 the first experiment, not an
   optional one.

### By question

**c1-01, small-cell artifacts.** Edison found no published Ecorr, Rp or breakdown data for
Cu–Ni, NAB, copper or brass across electrolyte volumes from 10 µL to over 100 mL. The artifacts are each
known separately, and together they are unquantified:

- **Reverse crevice corrosion.** On copper alloys, attack collects on the open surface just
  outside a crevice mouth, not inside it. On 70Cu–30Ni in seawater it took two months (Lu 2005,
  a thesis). So a ring of attack at the inner edge of the O-ring is expected, and should not be
  read as pitting or as a feature of the deposit.
- **Pt counter.** During an anodic scan the Pt counter is the cathode, so it can plate out
  dissolved copper and carry it to the next well. How much, in a microlitre seawater cell, has
  not been measured.
- **Counter pH.** Each mC passed through the counter makes 0.069 mM of base or acid in 150 µL.
- **Evaporation.** Losing 15 µL of the 150 µL raises chloride by 11%.

Its fixes: a humidified lid, weighing the clamp before and after, cleaning the Pt between wells,
calibrating at two or three O-ring sizes against a bulk cell, and keeping the counter away from
the metal.

**c1-02, the DC sequence.** Shahriari 2023 ran wire-arc AM NAB and reversed at 10 mA/cm². They
found no clear pitting range for most samples. Ding 2019 measured about 500 nm of β′ recession
on cast C95800 within 150 min near OCP. So selective phase attack can be seen within the length
of a test, by profilometry or SEM of the spot. No accessible study gives a cathodic-protection
potential that is shown to stop NAB selective phase corrosion, so that potential has to be
measured.

For sizing the potentiostat, the spot currents are:

| Condition | Whole-spot current |
| --- | --- |
| The Al plan's 1 mA/cm² reversal | 70–130 µA |
| Shahriari's 10 mA/cm² reversal | 0.7–1.3 mA |
| Luo 2026's NAB/duplex-steel galvanic couple at 1:50 area, 38 µA/cm² at the start | 2.7–4.9 µA |

So the range runs from nA to several mA, and compliance has to be checked on the assembled head.

**c1-03, element-resolved dissolution.** The closest AESEC work on a copper alloy is Sur 2025.
It used arc-melted Cu–Al and Cu–Al–Sn in sulfate at pH 4, not chloride, not NAB, and only two
compositions. Speck & Cherevko 2020, by flow-cell ICP-MS on Cu in alkaline and phosphate buffers,
saw 523 ng Cu/cm² dissolve per cyclic voltammogram (CV).

The naval number is Earley 2020's (*Biofouling*). The US Navy's "Dome" test takes one-hour
ICP-MS release measurements in natural San Diego Bay seawater:

- 90/10 Cu–Ni released about 100–200 µg Cu/cm²/day at first.
- Within about 30 days that fell to 1.4 µg/cm²/day for sheet and 3.9 µg/cm²/day for mesh.
- Materials releasing 1.4–6.9 µg/cm²/day delayed fouling; one below 0.5 fouled most.

So a one-hour test on a fresh spot measures the initial release, and copper release rate is a
property with its own naval meaning (antifouling). The answer's sample handling:

- Acidify at once with trace-metal HNO₃, to pH below 2.
- 150 µL of seawater-strength liquid suits ICP-MS with a collision cell after 5–10× dilution.
  ICP-OES would need about 2 mL, so wells would have to be pooled.
- Report the dissolution current from ICP, i = nF·m/(A·t), next to the charge passed. The gap
  between them is what stays on the surface.

**c1-04, repair zones.** Xing 2023 measured a TIG-welded 90–10 Cu–Ni with a Ni-rich filler. The
HAZ was anodic to the weld, at 4.43 µA/cm² coupled current at first in 5 m/s seawater, and its
pits reached 4–7 µm after 30 days. For NAB, Edison found no zone-by-zone map of a matched-alloy
laser DED repair, and no measured deposit-to-cast galvanic current. That is a gap the lab could
fill.

How to place the wells:

- Put each well wholly inside one zone, with clearance equal to the well's radius plus the
  positioning tolerance.
- Label any well that crosses the fusion line a "coupled mixed-area test".
- Measure galvanic coupling separately: two wired pieces in one bath, through a zero-resistance
  ammeter (ZRA), at area ratios of 1:1 and small anode to large cathode.
- Keep Pt-counter products and reference leakage out of the ICP sample.

**c1-05, specimen preparation.** Edison found no number for how much the finish (SiC, diamond or
colloidal silica) shifts Ecorr or Rp of C71500 or C95800. So the finish, and the delay
from polishing to immersion, become variables to test, not settled choices. Other points:

- Ding 2016 (wire-arc NAB on cast NAB) found reheated bands about 200 µm thick and a HAZ in the
  cast substrate under 1 mm wide.
- Song 2024 compared XY and YZ faces of wire-arc 70/30 Cu–Ni over 0.32 cm².
- Reject any footprint with pores, resin or adhered powder from the intrinsic-material set. Keep
  a separate, labelled set for pores.

**c1-06, the electrolyte series.** Keep the background fixed (ASTM D1141 or natural seawater) and
vary three things:

- **Sulfide dose:** 0, 0.01, 0.1, 1 and 10 mg/L.
- **Exposure history:** fresh, prefilmed in clean water then sulfided, and sulfided then clean.
- **Ferrous-sulfate prefilming:** as a conditioning step for condenser repair.

The measured effects of sulfide are large:

- **70/30 Cu–Ni** (Yuan 2007): icorr went from 8.44 to 87.39 µA/cm² at 10 ppm sulfide, fresh.
  After 10 days it was 18.44 µA/cm², against 1.01 µA/cm² in clean water.
- **Cast Cu–11Al–10Ni–2Fe bronze** (Nady 2017): at 2 mg/L sulfide, Ecorr fell from −464 to
  −609 mV SCE and icorr rose from 7.4 to 30 µA/cm².

These are Tafel fits, so read them as relative, not as rates.

An open well cannot hold an oxygen-poor series. Add Na₂S last, from a fresh capped stock. Measure
sulfide at the start and the end. Never mix sulfide and Fe²⁺ stocks.

**c1-07, a mini-jet flow cell.** Such a cell can screen how a fresh surface responds to flow. It
cannot give a pipe's critical velocity. Metikoš-Huković 2011 used a 1 mm submerged jet in 3.5%
NaCl at 2.7–8.3 m/s, which is 0.13–0.39 L/min:

- **Rp:** fell from 6–8 kΩ·cm² in still liquid to 0.4–1.3 kΩ·cm² under the jet.
- **Ranking:** flipped. The jet favoured Cu–10Ni; still liquid favoured Cu–30Ni.

It takes a sealed, pumped head, not an open well. Each run makes hundreds of mL of effluent,
which needs timed fractions for ICP. This is a separate module, after the static test works.

**c1-08, precedent.** Edison's answer to "has anyone done this?" is no, with these near misses.
It says itself that this is a search result, not proof.

| Work | What it did | What it did not do |
| --- | --- | --- |
| Schuppert 2014 | Scanning flow cell with online ICP-MS | Sputtered Pt–Cu film, in HClO₄ |
| DeCost 2022 | Autonomous droplet cell; deposited pure Cu and measured its dissolution in H₂SO₄ | Its Al–Ni–Ti corrosion optimization was simulated, which agrees with the correction in [the main README](../README.md) |
| MAP-E 2026 | Automated O-ring flat cells | 304 stainless steel |
| Joress et al. 2022 (NIST, [arXiv 2204.06094](https://doi.org/10.48550/arXiv.2204.06094)) | Automated millifluidic cell: a ~4.5 mm O-ring flow cell with syringe-pump mixing | Zn–Ni coating, not a copper alloy |
| Sur 2025 | AESEC on a copper alloy | Two Cu–Al(–Sn) compositions, in sulfate |
| Shahriari 2023, Zhang 2026 | Wire-arc NAB | Conventional single cells |

Joress 2022 is not in this plan's [references](../references.md) yet. It bears on the aluminum
plan's novelty statement too.

**c1-09, rapid-solidification stand-ins.** These are not yet shown to work. Edison found no
same-alloy study that compares laser surface melting (LSM) or a single track with a multilayer
blown-powder deposit.
The best direct evidence is Tang 2004, on cast Mn–Ni–Al bronze (C95700) in 3.5% NaCl:

| Surface | 12 h mass loss |
| --- | --- |
| Cast | 31.85 µg/cm²/h |
| Three LSM conditions | 16.59–28.67 µg/cm²/h |

So rapid melting helped, but the three LSM conditions disagree with each other by nearly a
factor of two. Validating the stand-ins should be the first block of the experimental design:
cast or wrought reference, LSM, single track and multilayer pad, all from the same powder.
Splats and skull are separate materials, not stand-ins for C71500 or C95800.

**c1-10, coulometric oxide reduction.** This works for copper oxides on the same potentiostat if
it has a galvanostatic mode. The method:

- Deaerated pH 8.4 borate, at 20–30 µA/cm², which is 1.4–3.9 µA per well.
- 1 nm of Cu₂O is 0.81 mC/cm², or 57–105 µC per well: 32 s per nm at 25 µA/cm².
- It needs deaerated liquid and an isolated counter, so it runs on a separate spot, not in the
  open corrosion well.

Edison found no calibration for Cu₂(OH)₃Cl or for Ni, Fe and Mn oxides, and Al₂O₃ does not
reduce in water at all. It found no measurement of powder oxide this way: the cavity-electrode
work it cites was on oxygen-reduction catalysts. So inert-gas fusion stays the oxygen assay for powder.

### Corrections to Edison

| Answer | Claim | Check |
| --- | --- | --- |
| c1-10 | 1 nm of CuO is 2.1 mC/cm² | **1.53 mC/cm²** (ρ 6.31 g/cm³, M 79.55, 2 e⁻). The Cu₂O figure, 0.81, is right |
| c1-01 | The 150 µL well's oxygen (37.5 nmol, 14.5 mC) "lasts roughly 25–50 min at typical Cu–Ni corrosion currents", so shorten OCP to 10–15 min | Its 5–10 µA are totals, which is 38–143 µA/cm² on these spots. At fresh Cu–Ni and NAB icorr, 1–11 µA/cm², the oxygen lasts **3 to 57 h**. What does limit oxygen is transport at the metal. In still liquid, the oxygen-limited current falls to about **14 µA/cm² after 5 min and 6 µA/cm² after 30 min**. In a bulk cell, where natural convection holds the depleted layer at 0.2–0.5 mm, it stays at about **40–100 µA/cm²**. So the well can shift Ecorr and the cathodic branch, but shortening OCP does not fix that: the bulk-cell calibration is the fix. The oxygen does run out within **2–3.5 min** at a 1 mA/cm² reversal current, after which the counter reduces water and the pH rises |
| c1-06 | Sulfide in aerated seawater has "a roughly 20-minute half-life", and "10 mg/L fell to 1.2 ± 0.2 mg/L in 1 day" | These cannot both hold for one solution: the second implies a half-life of about 8 h. Measure sulfide, don't assume either |
| c1-10 | Zhang 2026's WAAM NAB composition | Edison flagged this itself: the paper prints "Mg: Bal.", so the Cu balance can't be inferred from it |

### What changes in the plan for copper

In order. This list merges the ten answers' own top-5 lists.

1. **Calibrate the well first**, on wrought C71500 and cast C95800. Use two or three O-ring sizes
   against a 1 cm², 200 mL bulk cell, with a humidified lid and the clamp weighed before and
   after (c1-01, c1-02, c1-09).
2. **Make OCP, the LPR slope and potential holds the main sequence.** Run cyclic polarization only
   on spare spots, with its reversal rule stated. Measure the hold potentials (galvanic mixed
   potentials, propeller cathodic protection) rather than taking them from tables (c1-02, c1-04).
3. **Make ICP-MS of the used liquid plus one rinse the main metric.** Acidify on the deck, run
   stock, fixture and carryover blanks, and do EDS or XRF of the spot for what stays behind
   (c1-03, c1-04, c1-05). Acidifying at collection can be as simple as pre-loading each tube
   with a few µL of trace-metal HNO₃.
4. **Use sulfide against exposure history, in a seawater background, as the electrolyte series**
   (c1-06).
5. **Resolve the zones of a repair.** Use wide repair pads, wells placed wholly inside a zone,
   crossing wells labelled as coupled, and a separate two-piece ZRA galvanic test (c1-04, c1-05).
6. **Validate the stand-ins** (LSM, single track, splat) before they are used to rank powders
   (c1-09).
7. **Later modules:** a sealed jet head for flow (c1-07), and oxide coulometry on separate spots
   in deaerated borate (c1-10).

Most of this needs no new hardware beyond the aluminum plan's. The exceptions:

- **The potentiostat** needs a galvanostatic mode for item 7. Its current range has to reach
  several mA if the 10 mA/cm² reversals are copied.
- **Item 3's acidification** needs a few µL of trace-metal HNO₃ in each collection tube.
- **The ZRA test** needs either a potentiostat with a ZRA mode or a second channel.
- **The jet head** is new hardware.

## To run

Batch 1 has run. To re-run it or add a batch, from the repo root (needs `pip install edison-client`):

```bash
python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py submit 1
# one foreground call; PR #117 found every job, standard or high, takes about 30 min
python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py wait 1 45
python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py fetch
```

`submit` writes `_task_ids.json` as each task is created, so commit it straight away. `fetch` writes
`batch1/<name>.md` (the question, then Edison's answer) and `raw/<name>.json.gz` (the full verbose
trajectory). Commit both.
