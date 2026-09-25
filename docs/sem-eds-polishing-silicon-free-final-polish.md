# Silicon-free final polish for AlSi10Mg: VibroMet 2 options, residue numbers, prices

Written for Ronnie's [2026-09-25 questions in #110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110):

- Can the VibroMet 2 give the same finish as the 5 h colloidal-silica step without leaving silicon?
- Would diamond work, what does it cost, and how much carbon does it leave?
- Is there any fine polish that leaves no residue?
- Would 0.04 µm alumina work without inflating Al?
- What does carbon tape for the stubs cost?

> Prices are US list prices read from the live product pages on 2026-09-25, before shipping and
> tax. The literature checks are in [`outputs/edison-final-polish-2026-09-25/`](../outputs/edison-final-polish-2026-09-25/)
> (three Edison queries, answers, full trajectories). The residue numbers come from
> [`sem-eds-polishing-residue-estimate.py`](sem-eds-polishing-residue-estimate.py).

## Short answers

| Question | Answer |
| --- | --- |
| Silicon-free medium for the VibroMet 2 | **0.05 µm polycrystalline or sol-gel alumina**, the only drop-in swap. On Al–Si it comes close to silica but doesn't match it: "quite acceptable … Fine polishing scratches could be observed at high magnification. Colloidal silica, however, is clearly superior" ([Buehler Tech-Notes 3(2)](https://www.buehler.com/assets/solutions/technotes/vol3_issue2.pdf)). |
| 0.04 µm alumina | **Not sold as a suspension.** 0.04 µm is the size of the ProPrep 2 *silica* in the order. The standard finest alumina is 0.05 µm. |
| Would alumina inflate Al? | **Barely**, because Al is already ~90% of the alloy. Even with residue as heavy as the May silica layer, Al rises by only 0.75 wt% at 5 kV. The real side effects are that Si and Mg get diluted by ~6–7% relative and O goes up (§2). |
| Is diamond expensive? | **No.** 0.25 µm polycrystalline diamond is $40 for 8 oz ([OnPoint](https://onpointabrasives.com/products/diabrasive-premium-polycrystalline-diamond-suspension)). That is ~$15–25 per VibroMet charge, against ~$13 for alumina. |
| Is diamond a good match? | **For EDS chemistry, yes; as a VibroMet finish, no.** NIST microanalysts prefer diamond because "embedded diamond … does not interfere with most analytical jobs." But fine diamond suspensions embed in aluminum, and diamond doesn't remove the deformed layer. Buehler, Struers and PACE all end their aluminum methods with an oxide step after diamond (§3). |
| How much carbon | No published measurement exists. Bracketed: under 1 wt% C at 5 kV unless the surface is visibly peppered with particles. Your Aug 5 kV spectrum already had 1.99 wt% C from contamination, and C is excluded from the alloy quant anyway. |
| Residue-free | **Yes: argon ion polishing. The BYU EMF has a JEOL broad-beam ion polisher at $15 per 2 h**, and a BYU paper by Fullwood, Miles et al. used a JEOL ion polisher on aluminum (§4). Electropolishing is abrasive-free but a poor fit for Al–Si. |
| Carbon tape | **Ted Pella `16084-1`, 12 mm tabs, $17.00 per 100.** It is not quote-only (§5). |

## 1. Silicon-free media for the VibroMet 2

### Alumina is the only drop-in swap

- **Buehler lists it for vibratory polishing.** "… running samples on a vibratory polisher, for at least half an hour using alumina or silica suspension. … The most commonly used suspension is silica" ([Buehler Tech-Note](https://www.buehler.com/assets/solutions/technotes/How_to_Select_and_Use_Final_Polishing_Oxide_Media.pdf)).
- **Buehler rates the right kind highly for aluminum.** "MasterPrep alumina suspension has been found to be highly effective as a final polishing abrasive for aluminum alloys, however, the standard alumina abrasives made by the calcination process are unsuitable for aluminum" ([Buehler aluminum guide](https://www.buehler.com/blog/aluminum-metallographic-specimen-preparation-and-testing/)). **So buy sol-gel or polycrystalline alumina, not generic calcined alumina.**
- **PACE's house method for aluminum ends on alumina, not silica.** It uses "a final 0.05 µm Nanometer alumina polish that preserves second-phase particles at their true position." Its reasoning: "Final-polishing on alumina (rather than colloidal silica) avoids the slight chemical attack that can lift oxide inclusions out of the matrix" ([PACE aluminum guide](https://www.metallographic.com/guides/aluminum-sample-preparation)).
- **Why it is slower.** Silica works chemo-mechanically: "due to its high pH, the suspension does surface dissolution." Alumina "removes material through [a] mechanical, abrasive process" (Buehler Tech-Note). Equal particle size does not mean equal damage removal. Plan on the same run time or longer, not shorter.
- **The one direct Al–Si comparison is qualitative.** 0.05 µm gamma alumina (MasterPrep) gave "quite acceptable" surfaces with fine scratches at high magnification, and silica was "clearly superior" ([Tech-Notes 3(2)](https://www.buehler.com/assets/solutions/technotes/vol3_issue2.pdf)).
- **No one has published EBSD hit rates for alumina vs silica on aluminum.** Edison found no such study ([q1](../outputs/edison-final-polish-2026-09-25/q1-alumina-vs-silica-final-polish-al-answer.md)), and neither did a separate web search. Whether alumina is good enough for EBSD has to be tested (§6).

### "0.04 µm alumina" doesn't exist as a suspension

- The only 0.04 µm alumina found is a Kemet gamma-alumina **powder** (1 kg, quote-only; [Kemet](https://www.kemet-international.com/us/products/metallography/alumina-colloidal-silica-polishing-suspensions)).
- 0.04 µm is a *silica* size. The OnPoint cart lists ProPrep 2 as "Colloidal Silica – Low Crystallizing – 0.04 micron", and Struers OP-U is 0.04 µm silica too.
- The finest alumina suspension listed is Allied's 0.03 µm colloidal alumina ([pH 3.5, quote only](https://consumables.alliedhightech.com/Colloidal-Alumina-Suspension-p/collal03.htm)). 0.05 µm is the standard.

### 0.05 µm alumina, priced

| Product | Type, pH | Stays wet over a long run? | 32 oz | Other sizes |
| --- | --- | --- | ---: | --- |
| **[OnPoint AlumaPro `APA-32`](https://onpointabrasives.com/collections/polycrystalline-alumina)** | polycrystalline, pH 8.5–10.5 | **"does not recrystallize, making it an ideal choice for … EBSD"** | **$80** | 16 oz $80, 64 oz $130, 1 gal $205 |
| [PACE NA-1020](https://shop.metallographic.com/products/na-1020) | polycrystalline, **pH 4** | not stated | $95 | 16 oz $60, ½ gal $160, 1 gal $290 |
| [Buehler MasterPrep, via JH Technologies](https://shop.jhtechnologies.com/products/b406377032) | sol-gel, pH ~8.5 | **"will crystallise"** (Buehler Tech-Note) | $108 | — |
| [OnPoint Alumabrasive `ALSF-32005`](https://onpointabrasives.com/collections/alumina-suspension) | type not stated (possibly calcined) | not stated | $72 | 16 oz $38, 1 gal $199 |
| [Allied de-agglomerated 0.05 µm](https://consumables.alliedhightech.com/Alumina-Polishing-Suspension-p/alum01.htm) | — | not stated | quote | 16 / 128 oz |

**Buy AlumaPro.** It is polycrystalline, the kind Buehler says works on aluminum. A 4–5 h run in an open bowl is exactly where crystallization bites, and it is the only alumina here sold as non-recrystallizing. It is also the same vendor as the grit/alumina/silica order. **[That order with AlumaPro added comes to $404](https://onpointabrasives.com/cart/41449145958532:1,41449146024068:1,41449146089604:1,41449146155140:1,41449146220676:1,40893902127236:1,41614944600196:1,40732536930436:1)**, eight items. The link was tested today, and nothing is bought until someone enters payment. Keep the $38 silica in the order: it is the comparison arm of the trial (§6), and it stays the best EBSD finish if alumina falls short.

If AlumaPro's alkaline pH etches the matrix or raises relief around the Si, switch to PACE NA-1020 (pH 4). PACE's own troubleshooting for "Etching (Alumina)" is "Use lower pH alumina" ([PACE](https://www.metallographic.com/metallographic-consumables/final-polishing)).

The manual asks for enough suspension to cover the cloth. A comparable vibratory study on AlSi10Mg used 150 mL ([Maleki et al. 2023](https://re.public.polimi.it/bitstream/11311/1232085/2/MALEA01-23.pdf)). At $80 per 946 mL, a charge costs **about $10–13**.

### What changes on the machine

- **Use a fresh cloth dedicated to alumina.** If the bowl has had silica in it, rinse it out first. Mixing the two defeats the purpose.
- Keep the run time you use now (4–5 h) for the first trial. Adjust it after the SEM comparison.
- Buehler's end-of-run rule applies to alumina too: "Both MasterMet and MasterPrep will crystallise … clean immediately after polishing" (Tech-Note). §4 covers cleaning.
- The VibroMet 2 is [discontinued](https://www.buehler.com/products/grinding-and-polishing/vibratory-polishers/vibromet-2-vibratory-polisher/) (replaced by the VibroMet 3). This only matters if the machine ever needs parts.

## 2. How much each residue shifts the EDS result

This uses the same first-order model as the [silica estimate on 09-25](https://github.com/vertical-cloud-lab/byu-vcl/issues/110), now run for each X-ray line.

- AlSi10Mg is taken as Al 89.65 / Si 10.00 / Mg 0.35, with Mg at the middle of the spec.
- The X-ray generation depth is about 0.3 µm at 5 kV and 2.2 µm at 15 kV.
- The alloy columns exclude O and C and renormalize Al + Si + Mg to 100, which is how the alloy would be reported.
- Surface weighting would make every residue effect ~20–50% larger, so treat these numbers as lower bounds.

**Residue as heavy as Gage's May 22 silica layer** (≈ 25 nm of solid, one close-packed layer of ~42 nm spheres):

| Residue | kV | Al | Si | Mg | O added | C added |
| --- | :-: | ---: | ---: | ---: | ---: | ---: |
| none | — | 89.65 | 10.00 | 0.350 | — | — |
| colloidal silica | 5 | 86.62 | **13.05 (+31%)** | 0.339 (−3%) | 3.1 | — |
| alumina | 5 | 90.40 | 9.27 (−7%) | 0.329 (−6%) | 4.9 | — |
| diamond | 5 | 89.71 | 9.94 (−1%) | 0.352 (+1%) | — | 9.3 |
| colloidal silica | 15 | 89.26 | 10.40 (+4%) | 0.348 | 0.5 | — |
| alumina | 15 | 89.74 | 9.91 (−1%) | 0.347 (−1%) | 0.8 | — |
| diamond | 15 | 89.65 | 10.00 | 0.350 | — | 1.5 |

**Ten times cleaner** (≈ 2.5 nm), at 5 kV:

| Residue | Si | Mg | O added | C added |
| --- | ---: | ---: | ---: | ---: |
| silica | 10.30 (+3.0%) | 0.349 | 0.3 | — |
| alumina | 9.93 (−0.7%) | 0.348 (−0.6%) | 0.5 | — |
| diamond | 9.99 | 0.350 | — | 0.9 |

What the tables say:

1. **Alumina doesn't inflate Al in any way that matters.** Al goes up 0.75 wt% at worst, and 0.1 wt% at 15 kV. What alumina does instead is *dilute* the minor elements. Mg reads 6% low at 5 kV under a May-level layer, and 0.6% low under a realistic one. O also rises, which matters only because you want a small O peak. For scale, the native oxide alone accounts for ~0.4–1.1 wt% O at 5 kV.
2. **Silica is ~4× worse for Si than alumina, and in the opposite direction.**
3. **Diamond moves Al, Si and Mg by ≤1% even under a full layer.** The ±1% in the table comes from the model's per-line depth difference. Physically, carbon only absorbs. Under 25 nm of it, Mg Kα loses 1.8%, Al 1.1% and Si 0.7%, but O Kα loses 17%.
4. **The campaign makes silica worse than AlSi10Mg suggests.** Five of the six planned alloy families contain no Si. On those, the May layer would read **3.3 wt% Si that isn't there** at 5 kV. Even a surface ten times cleaner reads 0.33 wt%, above EDS's ~0.1 wt% detection limit.

**A rule of thumb for an aluminum-alloy lab:** the only abrasives whose residue can't be mistaken for an alloying element are **alumina** (Al is always the base) and **diamond** (C is never an analyte). Every other oxide abrasive adds one of the campaign's 16 elements:

| Oxide abrasive | Element it adds |
| --- | --- |
| silica | Si |
| ceria | Ce |
| zirconia | Zr |
| chromia | Cr |
| iron oxide / rouge | Fe |
| MgO, the traditional Al final polish | Mg |

NIST's microprobe lab uses the same logic: "We prefer not to use CrO₂, SiO₂, CeO₂, or Al₂O₃ since they easily embed themselves into the sample. In addition, many of the samples we analyze contain Cr and Al" ([Geller & Engle 2002](https://doi.org/10.6028/jres.107.051)). They avoid alumina as well, because Al is a minor element in their samples. In an aluminum alloy Al is the base, so embedded alumina costs you only its O.

The SiC grinding papers count too. "SiC particles can become embedded in aluminum alloys … usually arises with the finer grit size papers" ([Tech-Notes 3(2)](https://www.buehler.com/assets/solutions/technotes/vol3_issue2.pdf)). The 1 µm alumina step has to take the surface below that damage. PACE's aluminum method goes further and grinds on aluminum-oxide papers, "to avoid SiC embedding" ([PACE](https://www.metallographic.com/guides/aluminum-sample-preparation)). That is worth considering once the campaign alloys arrive, but not for this order.

## 3. Diamond: cheap and EDS-friendly, but it embeds in aluminum

**Price is not the obstacle.** At ~150 mL per VibroMet charge, diamond costs $15–40 per charge from OnPoint or PACE (~$90 as Buehler MetaDi), against ~$13 for AlumaPro.

| Product | 0.25 µm | 0.05 µm |
| --- | --- | --- |
| **[OnPoint Diabrasive Premium](https://onpointabrasives.com/products/diabrasive-premium-polycrystalline-diamond-suspension)** (polycrystalline, water-soluble) | **8 oz $40**, 32 oz $120, 1 gal $395 | — |
| [PACE DIAMAT WPC](https://shop.metallographic.com/products/wpc-0125) (polycrystalline, water-based) | 250 mL $65, 1 gal $525 | [250 mL $90](https://shop.metallographic.com/products/wpc-0105), 1 gal $570 |
| Buehler MetaDi Supreme, via [JH Technologies](https://shop.jhtechnologies.com/products/b406629) | 8 oz $146 | [8 oz $156](https://shop.jhtechnologies.com/products/b406627) |

**Carbon is harmless to the quant.** C is not one of the 16 campaign elements, so it is excluded from the alloy quant. You exclude it already: the Aug 5 kV run had 1.99 wt% C from contamination.

- **NIST:** "Embedded diamond in a sample is relatively easy to recognize and does not interfere with most analytical jobs" ([Geller & Engle](https://doi.org/10.6028/jres.107.051)).
- **No published number exists for how much carbon a diamond polish leaves on aluminum.** Edison found none ([q2](../outputs/edison-final-polish-2026-09-25/q2-diamond-carbon-residue-answer.md)). It did find that clean Al carries 0.3–1 nm of adventitious carbon ([Piao & McIntyre 2002](https://doi.org/10.1002/sia.1425)).
- **Edison's main warning** is that leaving C *in* the normalization dilutes every real element.
- **The model brackets it:**

  | Diamond left behind | C at 5 kV |
  | --- | ---: |
  | 2.5 nm equivalent (≈ 30 quarter-micron diamonds in every 10 × 10 µm field, which you would see) | ~0.9 wt% |
  | a full May-style layer | ~9 wt% |

- **Embedded diamonds are easy to count:** they show up as dark specks in BSE.

**Embedding and deformation are the obstacles:**

- **Buehler:** "Pure aluminum and some alloys are susceptible to embedment of fine diamond abrasive particles, especially when suspensions are used. If this occurs, switch to diamond in paste form" ([aluminum guide](https://www.buehler.com/blog/aluminum-metallographic-specimen-preparation-and-testing/)).
  - In their Al–Si trials with diamond suspensions, "the specimen surfaces were heavily embedded with diamond abrasive."
  - They concluded that "embedment is mainly a problem with fine diamond particles" ([Tech-Notes 3(2)](https://www.buehler.com/assets/solutions/technotes/vol3_issue2.pdf)). So going finer, 0.25 → 0.05 µm, makes embedding worse, not better.
- **Struers:** "A very thorough final polishing with silicon dioxide suspension is necessary to ensure that embedded diamond particles are completely removed" ([Struers, aluminum](https://www.struers.com/en/Knowledge/Materials/Aluminum)).
- **No deformation removal:** diamond is purely mechanical, so it doesn't remove the deformed layer that EBSD sees. Edison's summary calls fine diamond "a higher-risk compromise" as a final step on Al.

**Verdict:**

- **For the VibroMet step, use alumina, not diamond.** Diamond is not the analog of 5 h of silica.
- **Diamond still has a place on EDS-only samples,** as NIST uses it: **paste, not suspension**, on the rotary polisher. Analyze between any dark specks.
- **This refines my [caliber PR #11 advice](https://github.com/vertical-cloud-lab/caliber/pull/11#issuecomment-5374057757)** to finish with 1 → 0.25 µm diamond. The chemistry argument stands. But it should have said *paste*, and a sample that also needs EBSD needs an oxide or ion-polish step after it.

## 4. Is there a residue-free polish?

| Route | Leaves behind | Available | Catch |
| --- | --- | --- | --- |
| **Broad-beam Ar ion polishing** | no abrasive; a few nm of Ar-damaged surface | **BYU EMF, $15 per 2 h** | ~2 mm polished area; Al and Si sputter at different rates, so some relief |
| Electropolishing | no abrasive | not listed at the EMF. Fullwood's group electropolished AA7021 (perchloric/methanol), so ask them | perchloric-acid electrolytes; the Si network is left standing |
| 2 min water polish after the VibroMet | much less residue, not none | yes, on the rotary polisher | cheapest fix, and works with any abrasive |
| 4 s Keller's etch after the VibroMet | best EBSD in the one AlSi10Mg study | chemistry | contains HF, and it etches, so it's wrong for EDS quant |

### Ion polishing at the EMF

- **The tool.** The Electron Microscopy Facility's "JEOL Broad Beam Ion Mill/Polisher" does "final surface polishing of a flat sample … Polishing can be targeted to approximately a 2mm area" ([EMF equipment](https://web.archive.org/web/20260413235110/https://microscopy.byu.edu/ancillary-equipment)).
- **The price.** "Broad Beam (for 2 hours) $15.00" ([EMF pricing](https://web.archive.org/web/20260520190335/https://microscopy.byu.edu/services)). Both pages are Wayback copies from April–May 2026, because the live site blocks the runner, so confirm with the EMF.
- **Local precedent.** Sarkar et al. (Fullwood, Miles and co-authors) prepared AA7021 for HR-EBSD on "a JEOL ion-beam cross-section polisher": "coarsely milled at 5 kV … for 20 min," then "4 kV … for 5 min" ([Crystals 2026](https://doi.org/10.3390/cryst16030199)).
- **Why it matters for CALIBER.** It is the one route that removes abrasive residue *and* the deformed layer. That makes it the natural last step for the EDS standards: the AlSi10Mg piece and the Al pellet.
- **Caveats for AlSi10Mg:**
  - Al and Si sputter at different rates, so expect some relief.
  - Only ~2 mm gets polished, which is plenty for EDS spots and an EBSD map.
  - The native oxide grows back within seconds in air. Load the sample soon after milling, or store it under vacuum.

### Electropolishing

It is abrasive-free, but the wrong tool for AlSi10Mg composition work:

- **Struers:** "Due to the many different phases in cast alloys, they are not suited for electrolytic polishing" ([Struers aluminium note](https://web.archive.org/web/20220121011152/https://www.struers.com/-/media/Library/Brochures/English/Application-Note-Aluminium.pdf?lm=20200211T153417Z)).
- **Edison's literature check:** one Al–Si study vibratory-polished for 12 h instead, because the hard Si was unaffected by electropolishing.
- **Safety:** the standard electrolytes are perchloric-acid based.

### The water polish (do this regardless)

[Maleki et al. 2023](https://re.public.polimi.it/bitstream/11311/1232085/2/MALEA01-23.pdf) is the closest study to your process: LPBF AlSi10Mg, 0.05 µm colloidal silica, 150 mL, 90 min on a vibratory polisher. They found the silica "mostly located inside the pores" and named it the main source of contamination. EBSD hit rates:

| Finish after the vibratory step | Hit rate |
| --- | ---: |
| none | 51.26% |
| **2 min on a soft pad with distilled water, 40 rpm** | **81.12%** |
| 4 s perchloric/acetic electropolish | 87.23% |
| 4 s Keller's etch | 95.41% |

The water polish is two minutes on the machine you already use. Do it straight after the puck leaves the VibroMet, before Gage's solvent sequence, whichever abrasive is in the bowl. Then:

- Mike's Luminox → DI → IPA ultrasonic sequence.
- Cold water only. Edison's sources warn that hot water hardens silica residue.

**What doesn't work:**

- Nothing dissolves silica without attacking aluminum. NaOH and HF both etch Al.
- Plasma cleaning removes carbon, not silica or alumina ([q3](../outputs/edison-final-polish-2026-09-25/q3-silica-alumina-residue-removal-eds-answer.md)).

## 5. Carbon tape for the 12.7 mm pin stubs

A 12 mm tab on a 12.7 mm stub leaves no adhesive past the edge.

| Product | Pack | Price | Per tab |
| --- | --- | ---: | ---: |
| **[Ted Pella `16084-1`](https://www.tedpella.com/SEMmisc_html/SEMadhes.aspx) PELCO Tabs, 12 mm** | 100 | **$17.00** | $0.17 |
| [EMS `77825-12`](https://www.emsdiasum.com/conductive-carbon-adhesive-tabs) standard carbon tabs, 12 mm | 100 | $18.00 | $0.18 |
| Ted Pella `16084-20` PELCO Image Tabs, 12 mm | 100 | $18.50 | $0.19 |
| Ted Pella `16084-4` Spectro Tabs, 12 mm (higher purity) | 120 | $44.40 | $0.37 |
| Ted Pella `16073-1` carbon tape roll, 12 mm × 20 m, cut your own | 1 | $69.10 | ~$0.04 |
| EMS `77825-12`, resold by [Fisher (`5025105`)](https://www.fishersci.com/shop/products/carbon-adhesive-tabs-1/5025105) | 100 | $33.15 | $0.33 |

- **Buy `16084-1` from Ted Pella**, on the same order as the stubs and silver paint. The earlier BOM listed it as quote-only; the page shows $17.00.
- **Skip Fisher.** It charges 1.8× for the identical EMS part.
- **Skip generic Amazon tape.** It comes with no impurity spectrum or outgassing data.
- **Standard tabs, not Image Tabs.** Ted Pella lists:

  | | PELCO Tabs | Image Tabs |
  | --- | --- | --- |
  | Adhesive strength | 38 oz/in | 20 oz/in |
  | Through-thickness resistance | 50–200 kΩ | 1,000–3,500 kΩ |
  | Impurities | "very small impurities of Al and Si" | "Ni, Cu, Si, Sb, S, Na, P and … Fe and Mg" (campaign elements) |

  A 1 cm polished piece covers the whole tab, so the smoother surface buys nothing.
- **Carbon, not aluminum or copper tape.** Aluminum-backed tape adds Al next to an Al alloy, and copper adds Cu, a campaign element.
- **Either way, keep the beam off the tab.**

## 6. Suggested next run

1. **Order** the OnPoint cart above ($404, with AlumaPro added) and the Ted Pella tabs ($17).
2. **Prepare two pucks from the same build**, and run the pure Al pellet alongside puck B. Take all of them through the SOP to 1 µm alumina, then:

   | Puck | VibroMet (4–5 h) | Then |
   | --- | --- | --- |
   | A | silica, as now | 2 min water polish |
   | B + Al pellet | AlumaPro, on a fresh cloth | 2 min water polish |

   Clean both identically. The pellet is a built-in blank: pure Al has no Si, so any Si it shows is contamination from the papers or the bowl.
3. **Compare on the SEM in the same session:**
   - SE at ≥ 50,000× for residue.
   - EDS at 5 kV for Si/Al, O and C.
   - EBSD hit rate with Gage's [AlSi10Mg parameters](https://github.com/vertical-cloud-lab/byu-vcl/issues/77#issuecomment-4908212699).
4. **Ion-polish one puck at the EMF** ($15), and repeat step 3 on the milled area. That is the residue-free reference the other two are judged against.
5. **Decide:**
   - If B's EBSD is close to A's, use alumina for everything.
   - If it isn't, keep silica + water polish for EBSD-only samples.
   - Either way, finish the CALIBER standards with alumina or ion polishing.

## Sources

- Buehler, [*Tech-Notes* 3(2): preparation of cast Al–Si alloys](https://www.buehler.com/assets/solutions/technotes/vol3_issue2.pdf) (Vander Voort): MasterPrep vs silica, diamond and SiC embedding
- Buehler, [*How to Select and Use Final Polishing Oxide Media*](https://www.buehler.com/assets/solutions/technotes/How_to_Select_and_Use_Final_Polishing_Oxide_Media.pdf) and [aluminum preparation guide](https://www.buehler.com/blog/aluminum-metallographic-specimen-preparation-and-testing/)
- PACE Technologies, [*Aluminum sample preparation*](https://www.metallographic.com/guides/aluminum-sample-preparation): alumina final polish, aluminum-oxide grinding papers
- Struers, [*Application Note: Aluminium*](https://web.archive.org/web/20220121011152/https://www.struers.com/-/media/Library/Brochures/English/Application-Note-Aluminium.pdf?lm=20200211T153417Z) and [aluminum knowledge page](https://www.struers.com/en/Knowledge/Materials/Aluminum)
- Geller & Engle, "Sample Preparation for Electron Probe Microanalysis—Pushing the Limits," *J. Res. NIST* 107 (2002) 627, [doi:10.6028/jres.107.051](https://doi.org/10.6028/jres.107.051)
- Maleki et al., *Additive Manufacturing Letters* 5 (2023) 100122, [doi:10.1016/j.addlet.2023.100122](https://doi.org/10.1016/j.addlet.2023.100122) ([open-access PDF](https://re.public.polimi.it/bitstream/11311/1232085/2/MALEA01-23.pdf))
- Sarkar et al., *Crystals* 16 (2026) 199, [doi:10.3390/cryst16030199](https://doi.org/10.3390/cryst16030199): BYU JEOL ion polishing of AA7021
- BYU EMF [equipment](https://web.archive.org/web/20260413235110/https://microscopy.byu.edu/ancillary-equipment) and [pricing](https://web.archive.org/web/20260520190335/https://microscopy.byu.edu/services) (Wayback, 2026)
- Edison literature queries, [`outputs/edison-final-polish-2026-09-25/`](../outputs/edison-final-polish-2026-09-25/): q1 alumina vs silica on Al–Si, q2 diamond carbon, q3 residue removal
