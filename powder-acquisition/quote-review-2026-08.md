# Quote Review — ESPI Metals, Thermo Fisher #M6449, Atlantic Equipment Engineers (2026-08-26)

> **Update 2026-09-03 — the Er verdict in §1.2 is superseded.** That section's "campaign needs
> 5.0 g of Er, so buy 100 g of Al-10Er instead" rests on a *placeholder* 1.0 wt.% Er ceiling that
> nobody ratified. Against the published Al-Zr-Er-Ni optimum (2.33 wt.% Er, made by ultrasonic
> atomization), a 25 g lot is correctly sized and the 5 g alternative would truncate the design
> space below the known-good composition. See
> [erbium-bounds-and-lot-size.md](erbium-bounds-and-lot-size.md). The Sc verdict in §1.2 stands.

**Context:** [Issue #161 — Atomizer Powder Acquisition](https://github.com/vertical-cloud-lab/byu-vcl/issues/161).
Three quotes came back against the [shopping chart](https://github.com/vertical-cloud-lab/byu-vcl/issues/161#issuecomment-5417186399)
and the [RFQ emails](rfq-emails-2026-08.md). This document answers the two questions asked:
**(1) are the quoted purities good enough**, and **(2) are the quoted particle sizes a problem
for auger dosing and for dust-explosion safety.**

Every number below is reproducible with [`quote_analysis.py`](quote_analysis.py)
(`python powder-acquisition/quote_analysis.py`); the alloy composition ranges come from
[`purchase-quantity-model.md`](purchase-quantity-model.md).

---

## 0. Bottom line

| Question | Answer |
| --- | --- |
| **Purity** | Good enough on **every line except the aluminium base**. Al is >85 wt.% of every alloy, so 99.7% Al alone contributes **2,715 ppm** of tramp — 87% of the entire feedstock impurity budget, and ~2× the Scalmalloy Fe limit. Everything else lands at ≤120 ppm and is fine. |
| **Particle size** | **Four lines are genuinely unworkable** as auger feedstock (ESPI Cr, ESPI Ti, ESPI Sn 3N — all −325 mesh — and ESPI's Mg, which is ½″ ingot, not powder). Several more are "fine but tolerable". Only **one quoted line hits the 150–300 µm target: AEE AL-111.** |
| **Dust explosion** | One line is a real hazard escalation: **ESPI's −325 mesh titanium** (MIE 3–30 mJ, ships UN 2546 Class 4.2 spontaneously combustible). The rest are manageable inside the argon glovebox. |
| **Money** | The three quotes total **$9,399.55**. About **$8,600 of that should not be bought** — most of it a single elemental-scandium line — leaving **~$780 of items worth ordering today**, plus master alloys and Mg still to source. |

---

## 1. Three things to fix before any PO goes out

### 1.1 Fisher line `000102-22` is **dysprosium**, not aluminium — do not order it ($368)

The RFQ asked for Fisher SKU `AA0001022` = *Aluminum powder, −40+325 mesh, 99.8%, 100 g*
(list ≈ $29). Fisher's quote desk re-keyed it into Alfa catalog format as **`000102-22`**, which
is a different product line: [**Dysprosium ingot, 99.8% (REO), 100 g**](https://www.thermofisher.com/order/catalog/product/000102.22).
That is why an element not on our list appears in the quote at **$368**.

Root cause is the Alfa→Fisher SKU convention (Fisher drops one leading zero): Alfa **000010** →
Fisher `AA0001022` is the aluminium; Alfa **000102** → Fisher `AA0010222` is the dysprosium.

**Action:** strike the line. If the small Al commissioning pack is still wanted, re-order it by
*full description plus both numbers* — "Alfa **000010-22** / Fisher **AA0001022**, Aluminum
powder, −40+325 mesh, 99.8%, 100 g". Note it ships UN 1396 Class 4.3 (dangerous when wet), so it
carries a hazmat fee; since AEE is supplying the real 2 kg base, the simplest move is to drop it.

### 1.2 Do not buy elemental scandium at $5,875 — this is 76% of the ESPI quote

ESPI quoted 25 g of −40 mesh 3N Sc at **$235/g = $5,875**. Two problems:

1. **Quantity.** The 20-run campaign needs **4.0 g of Sc**. The quote is for 6.25× the
   requirement, so the cost per gram actually consumed is ~$1,470/g.
2. **Form.** Elemental Sc is exactly what the [Edison literature report](edison-lpbf-feedstock-purity-report.md)
   says to avoid: its surface oxide is the thing that poisons Al₃(Sc,Zr) L1₂ precipitation, and a
   −40 mesh powder has a lot of surface. **250 g of Al-2Sc delivers the same 5 g of Sc** with the
   solute already dissolved and its oxide skin gone.

~~The same argument applies with less force to **Er** ($800 for 25 g, campaign needs 5.0 g) — 100 g
of Al-10Er covers it.~~ **Superseded 2026-09-03:** the 5.0 g figure came from an unratified
1.0 wt.% Er ceiling. At the published 2.33 wt.% Er composition the 25 g lot is right-sized, and
elemental Er is needed for the high-solute corner that dilute masters cannot reach —
see [erbium-bounds-and-lot-size.md](erbium-bounds-and-lot-size.md).

**Action:** hold both lines pending the Kymera/Reading master-alloy quote. Keep the ESPI lines as a
*named fallback* — they are US-warehoused material, which has real option value given
[China's export licensing on Sc (April 2025) and Er (suspended only to 2026-11-10)](supplier-search-2026-08.md).
If you keep the fallback alive, also ask ESPI what a **5 g** Sc lot costs, since 25 g is oversized.

### 1.3 Reject ESPI's −325 mesh titanium on safety grounds, not just flow

See §3.2. This is the one line where the particle size is a category change in risk, not a
convenience issue.

---

## 2. Purity verdict — line by line

### 2.1 The governing principle

A feedstock's purity only matters in proportion to how much of it ends up in the alloy. The
figure of merit is `max wt.% × (1 − purity)` = **ppm of tramp element delivered to the finished
alloy at that element's maximum planned addition**:

| Element | Supplier / quoted purity | Max wt.% | **ppm to alloy** | Verdict |
| --- | --- | ---: | ---: | --- |
| **Al** | AEE AL-111, **99.7%** | 90.5 | **2,715** | ⚠️ **the only real purity problem** |
| Mg | Fisher, 99.8% *(no source)* | 6.0 | 120 | fine |
| Si | Fisher, 99.9% | 12.0 | 120 | fine |
| *Al* | *AEE AL-130, 99.99% (alt.)* | *90.5* | *91* | *the fix* |
| Zn | Fisher, 99.9% | 8.0 | 80 | fine (ESPI's 4N is better: 8 ppm) |
| Ni | Fisher, 99.7% | 2.0 | 60 | fine — below the 99.9% ask, doesn't matter |
| Mg | ESPI pieces, 99.9% | 6.0 | 60 | fine on purity, wrong on form |
| Mn | ESPI, 99.9% *(no CoA)* | 5.0 | 50 | fine on purity — see §2.3 |
| Cu | Fisher, 99.9% | 4.0 | 40 | fine |
| Ti | Fisher, 99.5% *(no source)* | 0.5 | 25 | fine |
| Cr | ESPI, 99.9% | 2.0 | 20 | fine |
| Sn | Fisher, 99.85% | 1.0 | 15 | fine — below the 99.9% ask, doesn't matter |
| Ti | ESPI, 99.7% | 0.5 | 15 | fine on purity, fails on size |
| Fe | Fisher, 99.9% | 1.0 | 10 | fine |
| Er | ESPI, 99.9% | 1.0 | 10 | fine |
| Sn | ESPI 3N | 1.0 | 10 | fine |
| Sc | ESPI, 99.9% | 0.8 | 8 | fine on purity; wrong form and price |
| Zn | ESPI, 99.99% | 8.0 | 8 | fine |
| Cr | Fisher, 99.97% | 2.0 | 6 | fine, but 13× ESPI's $/g for no benefit |
| Sn | ESPI 5N | 1.0 | 0.1 | 5N is pointless here — see §2.4 |

**Worst-case stack with a 99.7% Al base: 3,131 ppm, of which aluminium is 2,715 ppm (87%).**
Swap to a 99.99% base and the whole budget drops to **507 ppm — 6.2× cleaner** — without changing
a single other line. That is the entire purity conversation in one number.

Two chart items relax with no consequence: the **Ti 99.99%** on the chart is unbuyable as a
stocked product and unnecessary (0.5 wt.% Ti at 99.5% = 25 ppm), and the **Mg 99.99%** likewise —
4N Mg simply is not sold as powder.

### 2.2 The aluminium decision — the one place to spend money

AEE's catalogue makes the trade-off unusually explicit, because they stock both ends of it:

| AEE item | Purity | Size | Auger-ready? |
| --- | --- | --- | --- |
| **AL-111** | 99.7% | **−50+100 mesh (150–300 µm)** | ✅ exactly the target |
| **AL-130** | **99.99%** | ¼″–½″ pellets | ❌ hand-charge only |
| AL-110 | 99.7% | 20–50 mesh (300–850 µm) | too coarse |
| AL-103-S | 99.8% | −100 mesh | too fine |

You can have 4N **or** sand-sized, not both. Quantitatively, if AL-111's 0.3% impurity has the
typical commercial split (~0.15% Fe / 0.10% Si / 0.05% other), the base alone puts
**~1,360 ppm Fe = 0.136 wt.% Fe** into the alloy. That is:

- **2.0× the Scalmalloy Fe limit** (0.068 wt.%) — a real problem for the Al-Zr-Er-Sc family, where
  Fe forms coarse Al-Fe-Si intermetallics that blunt exactly the ductility those alloys are for;
- **0.54× the AlSi10Mg limit** (0.25 wt.%) — a non-problem for the Al-Si-Mg-Cu, Al-Zn-Mg-Cu,
  and Al-Ce-Mg families.

**Recommendation — buy both:**

1. **AL-111, 5 lb, $97.45** as the workhorse base for the Si / Cu / Zn / Ce / Mn / Cr families and
   all commissioning melts. **Request the certificate of analysis first** — if the actual Fe comes
   in near 0.05–0.08% rather than 0.15%, most of this concern evaporates.
2. **AL-130 4N pellets, ~500 g (quote it)** reserved for the Al-Zr-Er-Sc runs. Hand-charging the
   base is not a real loss of automation: aluminium is one constant ~90 g addition per batch that
   carries no combinatorial information, whereas the augers earn their keep on the *solutes*.
   Weighing three pellets is not harder than dosing 90 g through a screw feeder.

Either way, **report the measured Fe** with the alloy data — for a comparative screening campaign a
known, constant Fe background is a systematic offset rather than a confound between compositions.

### 2.3 The manganese lot with no certificate of analysis

ESPI's $0.35/g Mn is roughly an order of magnitude below normal lab pricing, and they are explicit
about why: no CoA. Assessment:

- **Composition risk is low.** Even if the lot is really 99.5% rather than 99.9%, Mn at 5 wt.%
  contributes 250 ppm — still inside the impurity budget above.
- **Verification is cheap and you already have the capability.** ICP-OES/ICP-MS on a dissolved
  sub-sample will confirm the metallic assay.
- **But ICP will not see the thing that matters most.** "Metals basis" purity — on *every* line in
  all three quotes — excludes O, C, N and H. Oxygen needs inert-gas fusion (LECO), which is a
  different instrument. See §2.5.

**Recommendation:** buy the uncertified lot, and ask ESPI for the CoA-bearing lot's price in the
same email so the delta is visible. Run ICP on receipt and record it. If BYU has no IGF/LECO
access, note that as an open gap rather than assuming the CoA would have covered it — most
"metals basis" certificates do not report oxygen either.

### 2.4 Where the quotes over-buy purity

- **ESPI Sn 5N at $450** vs **Sn 3N at $40**. At 1 wt.% Sn the purity difference is 10 ppm vs
  0.1 ppm of the finished alloy. The $410 premium buys nothing measurable. *(The 5N lot is the
  coarser cut at −40 mesh, but the campaign only consumes 2.5 g of Sn total — hand-weigh it.)*
- **Fisher Cr 99.97% at $425/50 g** vs **ESPI Cr 99.9% at $65/100 g**. 13× the $/g for 14 ppm.
  The Fisher lot is the better *size* (45–150 µm vs <45 µm), which is the only argument for it.
- **Fisher Zn at $219/100 g, 46-day lead** vs **ESPI Zn 4N at $45/100 g in stock**. ESPI wins on
  price, purity and lead time. Strike the Fisher Zn line.

### 2.5 The impurity nobody quoted: surface oxide

This is the point that connects the two questions, and it is the reason the "coarse like sand"
instinct is metallurgically correct and not just a handling preference.

A passivated metal powder carries a native oxide film (~2–10 nm). Its mass fraction scales as
`6δ/d`, so it grows as particles get finer — and it is **not** covered by a metals-basis assay.
For the aluminium base in a 100 g charge:

| Al feedstock | d_char | O in the Al | O contributed to the 100 g batch |
| --- | ---: | ---: | ---: |
| **AEE AL-111, −50+100 mesh** | 212 µm | 97 ppm | **88 ppm** |
| a −100 mesh Al powder | 60 µm | 344 ppm | 312 ppm |
| LPBF-grade 15–45 µm Al | 30 µm | 689 ppm | 623 ppm |
| a −325 mesh Al powder | 18 µm | 1,148 ppm | **1,039 ppm** |

Gas-atomised AM aluminium powder is typically specified at **400–1,200 ppm O total**. Charging fine
Al powder would consume the entire oxygen budget *before atomisation starts*; the AL-111 cut lands
roughly an order of magnitude below it. **A 99.7% coarse aluminium is a cleaner melt than a 99.99%
fine one.**

The same table also shows why fine cuts are acceptable for the *minor* additions — oxide scaled by
how much of the element is in the alloy:

| Feedstock | O in the feedstock | O it puts in the 100 g batch |
| --- | ---: | ---: |
| Al, AEE AL-111 (150–300 µm) | 97 ppm | **88.1 ppm** |
| Si, Fisher −100 mesh | 121 ppm | 14.5 ppm |
| Zn, ESPI −100 mesh | 124 ppm | 9.9 ppm |
| Mn, ESPI −100 mesh | 95 ppm | 4.7 ppm |
| Cr, ESPI −325 mesh | 229 ppm | 4.6 ppm |
| **Ti, ESPI −325 mesh** | **626 ppm** | **3.1 ppm** |
| Fe, Fisher −20 mesh | 14 ppm | 0.1 ppm |

Titanium at −325 mesh is the dirtiest feedstock per gram on the list by a wide margin — and it
still only adds 3 ppm of oxygen to the batch, because there is only half a gram of it. **Fine
powder is a metallurgical problem for the base metal and a rounding error for the trace additions.**
The reason to reject the −325 mesh Ti is safety and dosing, not chemistry.

---

## 3. Particle-size verdict — auger handling and dust-explosion safety

Mesh → micron for the cuts quoted: 20 mesh = 850 µm · 40 = 425 · 50 = **300** · 60 = 250 ·
100 = **150** · 140 = 106 · 170 = 90 · 325 = 45. **Target band: 150–300 µm = −50+100 mesh.**

### 3.1 Every quoted line against the target

"Cohesion" = (250 µm / d_char)², the ratio of van der Waals to gravitational force relative to a
particle at the middle of the target band. Above ~10× a powder bridges and rat-holes in a small
screw feeder instead of flowing.

| Element | Supplier / cut | µm | Cohesion | In band? | Can sieving rescue it? |
| --- | --- | --- | ---: | --- | --- |
| **Al** | **AEE AL-111, −50+100** | **150–300** | **1.4×** | ✅ **yes** | not needed |
| Ti | Fisher −60+100 *(no source)* | 150–250 | 1.7× | ✅ yes | not needed |
| Mg | Fisher −20+100 *(no source)* | 150–850 | 0.5× | partial | ✅ top screen only, high yield |
| Fe | Fisher −20 mesh | 0–850 | 0.5× | partial | ✅ screen both ends, moderate yield |
| Sc | ESPI −40 mesh | 0–425 | 2.2× | partial | ✅ screen both ends |
| Er | ESPI −40 mesh | 0–425 | 2.2× | partial | ✅ screen both ends |
| Sn | ESPI 5N −40 mesh | 0–425 | 2.2× | partial | ✅ screen both ends |
| Ni | Fisher −60+170 | 90–250 | 2.8× | partial | ✅ bottom screen at +100 mesh |
| Cu | Fisher −100+325 **spherical** | 45–150 | 9.3× | ❌ | ❌ — but spherical, so it flows anyway |
| Cr | Fisher −100+325 | 45–150 | 9.3× | ❌ | ❌ no coarse fraction exists |
| Zn | Fisher −140+325 | 45–106 | 13× | ❌ | ❌ |
| Mn | ESPI −100 mesh | 0–150 | 17× | ❌ | ❌ |
| Zn | ESPI −100 mesh | 0–150 | 17× | ❌ | ❌ |
| Si | Fisher −100 mesh | 0–150 | 17× | ❌ | ❌ |
| Sn | Fisher −100 mesh | 0–150 | 17× | ❌ | ❌ |
| **Cr** | **ESPI −325 mesh** | **0–45** | **193×** | ❌ | ❌ |
| **Sn** | **ESPI 3N −325** | **0–45** | **193×** | ❌ | ❌ |
| **Ti** | **ESPI −325 mesh** | **0–45** | **193×** | ❌ | ❌ |
| **Mg** | **ESPI ½″ and down** | ingot | — | ❌ not powder | ❌ |

**The critical structural point: you cannot sieve coarse particles out of a powder that has none.**
For anything sold as "−325 mesh", every particle is already below 45 µm — screening on receipt
removes nothing and yields nothing. Sieving only rescues lots that were quoted with a *coarse top
end* (Fisher's −20 mesh Fe and −20+100 Mg, ESPI's −40 mesh Sc/Er/Sn). Note the irony that the two
lines which hit the target band perfectly — Fisher's Mg −20+100 and Ti −60+100 — are exactly the
two that came back **"No source."**

### 3.2 Dust-explosion assessment

[NFPA 484](https://www.nfpa.org/codes-and-standards/nfpa-484-standard-development/484) treats metal
particulate below ~420 µm (40 mesh) as combustible metal dust; severity climbs steeply as the
fraction below 150 µm grows, and steeply again below 75 µm.

| Tier | Lines | Assessment |
| --- | --- | --- |
| 🚨 **Escalation** | **ESPI Ti, −325 mesh, 200 g** | Titanium dust MIE is [3–30 mJ](https://www.metal-am.com/articles/titanium-powder-pyrophoricity-passivation-and-handling-for-safe-production-and-processing/) — *below the ~10–30 mJ a person can discharge as static*. Explosion severity [rises as Ti size falls from −100 mesh and plateaus at −325 mesh](https://www.sciencedirect.com/science/article/abs/pii/S0950423013001290), i.e. this cut sits at maximum severity. Dry Ti powder ships [UN 2546, Class 4.2 "spontaneously combustible"](https://cameochemicals.noaa.gov/chemical/7989). **Reject.** |
| ⚠️ **Watch** | ESPI Zn −100, Fisher Zn −140+325 | Zinc dust is [UN 1436, Class 4.3](https://en.wikipedia.org/wiki/List_of_UN_numbers_1401_to_1500) — water-reactive as well as combustible. Keep dry and under Ar; never wet a Zn spill. |
| ⚠️ **Watch** | ESPI Cr −325, Fisher Si −100, Fisher Fe −20 | Ordinary combustible metal dusts (St-1 class). Manageable, but the Cr is fine enough to become airborne easily and Fe fines self-heat. |
| ✅ **Low** | AEE Al −50+100, Fisher Cu/Ni/Sn, ESPI Mn/Sc/Er | Aluminium is a St-3 dust in fine form, but the AL-111 cut is bottom-screened at 150 µm with essentially no fines — this is the safest way to buy 2 kg of aluminium. Cu is not an explosion hazard. Ni is chemically benign here but is a **respiratory carcinogen** — glovebox handling is the right control regardless of size. |
| ✅ **Safest** | ESPI Mg ½″ pieces | Bulk Mg cannot form a dust cloud. It is the safest Mg on offer and the least automatable. |

**What the argon glovebox does and does not buy you.** A dust explosion needs an oxidiser; at
glovebox O₂ levels there is no explosion pentagon, so *inside* the box the fine powders are far
less dangerous than their datasheets suggest. Two caveats that matter for this specific list:

1. **Argon is the right choice and nitrogen would not be.** Mg and Ti both burn in N₂ (forming
   nitrides) and in CO₂. This also means a Class D extinguisher is the only correct one —
   **water and CO₂ are actively wrong** on a Mg or Ti fire.
2. **The risk concentrates at the transfers**, exactly the "occasional air exposure" already
   identified. Opening a jar of −325 mesh Ti in room air, or a glovebox breach with fines
   suspended, are the credible scenarios. Grounded/bonded scoops and containers, sealed transfer
   vessels, and antistatic tooling are the controls; buying coarse in the first place removes the
   need to rely on them.

### 3.3 Why flow matters more than it might seem

With a screw feeder, cohesive powder does not simply flow slower — it bridges, then avalanches, so
dose *scatter* rises. At a realistic ±20% scatter for a cohesive lot:

| Element | Target in a 100 g batch | ±20% scatter = | Composition error |
| --- | ---: | ---: | --- |
| Ti | 0.50 g | ±0.100 g | ±0.100 wt.% on a 0.5 wt.% target |
| Sc | 0.80 g | ±0.160 g | ±0.160 wt.% on a 0.8 wt.% target |
| Cr | 2.00 g | ±0.400 g | ±0.40 wt.% |
| Mn | 5.00 g | ±1.000 g | ±1.0 wt.% |

For the microalloyed elements those errors are the same size as the composition *steps* the
campaign is trying to resolve, which would make the resulting dataset much harder to interpret.
This is the strongest argument for holding the line on particle size — stronger than the safety
argument, which the glovebox already largely handles.

### 3.4 …but only for the elements you actually use a lot of

Ranked by grams consumed across all 20 runs:

| Item | g for 20 runs | Dosing |
| --- | ---: | --- |
| Al | 1,428 | **auger — size/flow really matters** |
| Al-10Zr / Al-2Sc / Al-20Ce | 275 / 200 / 188 | **auger — specify the crushed cut in the RFQ** |
| Al-5Li, Mn, Al-10Er, Mg, Si, Zn, Cr, Cu | 58 → 20 | auger if the cut allows, else pre-weigh |
| **Ti, Ni, Fe, Sn** | **7.5 / 5.0 / 2.5 / 2.5** | **pre-weigh into capsules — the auger buys nothing** |

Those last four total **17.5 g across the entire campaign** — less than one Fisher pack. Insisting
on a 150–300 µm cut for them is not worth a supply-chain fight. Pre-weighing 20 tiny charges into
capsules inside the glovebox is a one-afternoon job and gives *better* accuracy than a screw feeder
would. This reframes the whole size problem: **the 150–300 µm requirement is binding for Al and
the four master alloys, negotiable for the mid-tier, and irrelevant for Ti/Ni/Fe/Sn.**

---

## 4. The magnesium gap

Neither house can supply Mg powder: Fisher lists it "No source", ESPI offers ½″ ingot pieces.
That is not a coincidence — Mg powder ships [UN 1418, Class 4.3 with a 4.2 subsidiary](https://adrdangerousgoods.com/eng/substances/0000790/un1418-magnesium-powder-or-magnesium-alloys-powder/)
(water-reactive *and* spontaneously combustible), so general lab-chemical distributors increasingly
decline to stock it. The material exists; it is sold by specialist metal-powder houses, not
catalogue distributors.

**Three routes, in preference order:**

1. **Buy coarse atomised Mg from a specialist.** Both of these are US producers, which also
   sidesteps the import-restriction problem that killed the MSE route:
   - **[Luxfer Magtech](https://luxfermagtech.com/products/magnesium-products/)** (Cincinnati OH) —
     inert-gas-atomised Mg from **20–1000 µm (16–635 mesh)**, explicitly including the −50+100
     mesh band, with lot-to-lot PSD control. **(800) 503-4483.**
   - **[Coogee USA](https://coogee.com/magnesium-powder/)** (Ottawa IL) — newer atomised-Mg plant,
     ISO 9001, flexible PSDs, and they also run **titanium powder** — so one call can potentially
     close both the Mg and the coarse-Ti gaps.
   - Also worth an email: **Kymera International / ECKA Granules**, who are already being asked to
     quote the master alloys and produce atomised Mg granules — one PO instead of two.
2. **Take ESPI's ½″ pieces and hand-charge Mg.** $230/100 g is a high price for magnesium, but the
   campaign only needs 36 g, the material is the safest form on the list, and Mg is present in
   only ~6 of the 20 planned runs. Cutting/filing ingot introduces fresh unpassivated surface, so
   do it under Ar shortly before melting.
3. **Atomise it yourselves — not first, and not as pure Mg.** The instinct is sound, but pure Mg
   is the worst possible commissioning material for a new atomiser: it melts at 650 °C, ignites in
   air, burns in N₂ and CO₂, and reacts with any moisture in the chamber or crucible. If you do go
   this way, atomise an **Al-Mg master alloy** (e.g. Al-50Mg) rather than pure Mg — dramatically
   less reactive, still gives a dosable Mg-bearing powder, and it is a far more forgiving first
   experiment. Treat this as a later capability, after the atomiser has runs on Al alloys behind
   it. *(Caveat: this is a hazard judgement, not a machine-capability judgement — the atomiser's
   own limits on Mg should be confirmed with Amazemet before planning it.)*

Also worth flagging: Mg is the element with the largest evaporation loss in the melt (the model
already carries a 15% over-charge), so a 5–10 g weighing convenience is not the binding constraint
here — sourcing is.

---

## 5. The titanium gap

Fisher's −60+100 mesh Ti (the perfect cut) is "No source", and ESPI's substitute is −325 mesh,
which §3.2 rejects. Alternatives, best first:

1. **[AEE / Micron Metals TI-109](https://micronmetals.com/product/titanium-metal-powder-2/)** —
   99.7% HDH Ti, −100 mesh, **$70.26/lb at 1–2 lb**, 1 lb minimum. Already the aluminium supplier,
   so it rides the same PO and freight. **Ask them to screen it to −60+100 mesh** — they are a
   powder house and custom cuts are routine; expect a yield-based surcharge and a smaller net
   weight. Even unscreened, −100 mesh is 3.3× coarser than ESPI's −325 mesh and is not a Class 4.2
   shipment.
2. **Coogee USA** (see §4) — atomised Ti; a spherical coarse cut would flow better than any HDH
   powder and one call covers Mg too.
3. **Buy 25 g, not 200 g.** The campaign needs 7.5 g of Ti. The 200 g on the chart was sized when
   Ti was going to arrive as Al-5Ti-1B rod at 5% Ti. As elemental powder, 25–50 g is plenty, and a
   smaller pack of a hazardous material is easier to buy, ship, store and dispose of.
4. If nothing coarse can be found, **elemental Ti is the most droppable element on the list** for
   round one — it is a grain refiner rather than a strengthening solute in these chemistries, and
   deferring it costs the campaign one variable out of sixteen.

---

## 6. Revised order

### Order now — ~$780

| Supplier | Lines | $ |
| --- | --- | ---: |
| **Fisher #M6449** | Si `000311-22` $106 · Fe `047355-30` $122 · Ni `010579-22` $68.90 · Cu `042623-22` $57.80 · Sn `000941-22` $68 | **$422.70** |
| **ESPI** | Mn −100 3N $35 · Cr −325 3N+ $65 · Zn −100 4N $45 · hazardous handling $45 | **$190.00** |
| **AEE** | AL-111 aluminium 5 lb @ $19.49/lb | **$97.45** |
| **AEE** | TI-109 titanium 1 lb @ $70.26 *(request −60+100 screen)* | **$70.26** |
| | | **≈ $780 + freight/hazmat** |

*Note the ESPI Cr is kept at −325 mesh deliberately: at $65 vs Fisher's $425 for half as much, and
with only 20 g consumed all campaign, it is worth taking the cheap lot and pre-weighing it rather
than augering it. If Cr must be auto-dosed, switch to the Fisher line and accept the $360 delta.*

### Strike from the quotes — ~$8,620

| Line | $ | Why |
| --- | ---: | --- |
| Fisher Dy ingot `000102-22` | 368.00 | wrong product — SKU transcription error (§1.1) |
| ESPI Sc, 25 g elemental | 5,875.00 | buy as Al-2Sc; 6× oversized (§1.2) |
| ESPI Er, 25 g elemental | 800.00 | buy as Al-10Er (§1.2) |
| ESPI Ti −325 mesh | 130.00 | Class 4.2, MIE 3–30 mJ, won't feed (§3.2) |
| ESPI Sn 5N −40 mesh | 450.00 | 5N buys 10 ppm; use Fisher's $68 line (§2.4) |
| ESPI Mg ½″ pieces | 230.00 | keep as fallback; try Luxfer/Coogee first (§4) |
| Fisher Cr 99.97% | 425.00 | ESPI's is 13× cheaper per gram (§2.4) |
| Fisher Zn | 219.00 | ESPI's 4N is cheaper, purer, in stock (§2.4) |
| Fisher Mg / Fisher Ti | 152.40 | quoted "No source" — nothing to buy |

Quoted total **$9,399.55** → **≈ $780 orderable**, with master alloys and Mg still to price.

### Still open

| Item | Status |
| --- | --- |
| Al-10Zr 300 g, Al-2Sc 250 g, Al-20Ce 250 g (binary, **not** mischmetal), Al-10Er 100 g, Al-5Li 200 g — **all crushed/screened to 150–300 µm** | Kymera/Reading quote outstanding. Sophisticated Alloys is out (no powders). Add **Belmont Metals** (stocks 30–60 mesh granular masters, small lots, has Al-5Li) and **KBM Affilips** (only non-China Al-Er producer). **This is now the critical path.** |
| Mg, 150–300 µm | Luxfer Magtech / Coogee / Kymera-ECKA (§4) |
| Ti, 150–300 µm | AEE TI-109 screened, or Coogee (§5) |
| AL-130 4N Al pellets, ~500 g | Ask AEE to add to the AL-111 quote (§2.2) |
| **Er timing** | China's Er export-licence suspension lapses **2026-11-10**; masters have 3–5 week lead times. Place the Al-10Er order by early October or keep the ESPI elemental line alive as insurance. |

### Two questions to put in the next email round

1. **To ESPI:** price of the same Mn with a certificate of analysis; a 5 g Sc lot; and whether they
   will custom-screen the −40 mesh Sc/Er to −50+100 mesh.
2. **To AEE:** AL-111 certificate of analysis (Fe, Si, **O**); AL-130 4N pellet pricing; and
   whether TI-109 can be screened to −60+100 mesh.

Ask for **oxygen on every certificate of analysis** — as §2.5 shows, it is the largest single
impurity in most of these lots and no "metals basis" number covers it.

---

## Sources

- Quotes as posted in [issue #161 on 2026-08-26](https://github.com/vertical-cloud-lab/byu-vcl/issues/161)
  (ESPI Metals; Thermo Fisher quote #M6449, 2026-08-24, valid to 2026-09-23; Atlantic Equipment Engineers)
- [`quote_analysis.py`](quote_analysis.py) — all calculations in this document
- [`edison-lpbf-feedstock-purity-report.md`](edison-lpbf-feedstock-purity-report.md) — 26-citation literature basis
- [`purchase-quantity-model.md`](purchase-quantity-model.md) — the 20-run composition and mass model
- [`supplier-search-2026-08.md`](supplier-search-2026-08.md) — supplier directory and import-restriction analysis
- [Thermo Scientific 000102.22 — Dysprosium ingot, 99.8% (REO), 100 g](https://www.thermofisher.com/order/catalog/product/000102.22)
  and [Fisher AA0001022 — Aluminum powder, −40+325 mesh, 99.8%, 100 g](https://www.fishersci.com/shop/products/aluminum-powder-40-325-mesh-99-8-metals-basis-alfa-aesar-3/AA0001022)
- [AEE aluminium products](https://micronmetals.com/product/aluminum-metal-powder/) · [AEE titanium products](https://micronmetals.com/product/titanium-metal-powder-2/) · [AEE chromium products](https://micronmetals.com/product/chromium-metal-powder/)
- [Luxfer Magtech magnesium powders (20–1000 µm)](https://luxfermagtech.com/products/magnesium-products/) · [Coogee USA magnesium powder](https://coogee.com/magnesium-powder/)
- [Boilard et al., *Explosibility of micron- and nano-size titanium powders*, J. Loss Prev. Proc. Ind.](https://www.sciencedirect.com/science/article/abs/pii/S0950423013001290)
- [Metal AM — titanium powder pyrophoricity, passivation and handling](https://www.metal-am.com/articles/titanium-powder-pyrophoricity-passivation-and-handling-for-safe-production-and-processing/)
- [CAMEO Chemicals — Titanium powder, dry (UN 2546, Class 4.2)](https://cameochemicals.noaa.gov/chemical/7989) · [UN 1418 magnesium powder, Class 4.3 (4.2)](https://adrdangerousgoods.com/eng/substances/0000790/un1418-magnesium-powder-or-magnesium-alloys-powder/)
