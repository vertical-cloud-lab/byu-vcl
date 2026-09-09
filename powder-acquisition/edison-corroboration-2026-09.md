# Edison Scientific corroboration of the issue #161 feedstock plan (2026-09-09)

Two Edison Scientific `paperqa3-high` literature queries were run to check the recommendations that
accumulated in [issue #161](https://github.com/vertical-cloud-lab/byu-vcl/issues/161), and to evaluate the
charging strategy raised on 2026-09-09: **dispense the non-Al elements into a sacrificial aluminium cup,
then set the loaded cup inside the atomizer's graphite crucible.**

| Query | Task ID | Raw report |
| --- | --- | --- |
| Sacrificial Al cup, powder incorporation into Al melts, graphite-crucible chemistry | `0d720f18-c588-448a-a8f4-14211be959ba` | [edison-crucible-and-charging-2026-09.md](edison-crucible-and-charging-2026-09.md) |
| Claim-by-claim corroboration of the purity / PSD / master-alloy / melt-window recommendations | `376e52f5-05e7-48f5-92e7-3d3d8e4178e4` | [edison-elements-and-master-alloys-2026-09.md](edison-elements-and-master-alloys-2026-09.md) |

Full trajectories (query, answer, contexts, tool history, citations) are committed under
[`outputs/issue-161-edison/`](../outputs/issue-161-edison/).

---

## 0. Verdict table

| # | Claim from the thread | Edison verdict | Action |
| --- | --- | --- | --- |
| A | 3N enough for Mn/Cr/Si/Cu/Zn/Ti/Ni/Fe/Sn/Ce; 4N for Al base + Zr/Sc/Er | **Plausible, no documented threshold** | Keep the plan; stop presenting it as literature-backed |
| B | Feedstock oxygen beats metallic impurity; coarse 99.7 % Al is cleaner than fine 99.99 % | **Supported**, numbers match | Keep; ask for O on every CoA |
| C | Buy the coarsest cut that feeds (150–300 µm) | **Partially supported** — right for the Al base, *wrong* for refractory solutes | **Split the rule by element** (§2) |
| D | Al-Li mandatory; masters preferred for Zr/Sc/Er/Ce/Ti | **Supported** | Keep |
| E | Ti dissolves, doesn't melt; liquidus 791/868/954 °C at 0.5/1/2 wt.% Ti | **Supported in principle; values not independently verified** | Keep the CALPHAD table; see §5 on superheat |
| F | Over-charge Mg/Zn/Li 5–15 %; Mn loss is dross, not vapour | **Supported qualitatively; Mn contradicted** for atomization specifically | **Revise: Mn *does* evaporate in UA** (§4) |
| G | Er design box [0, 3] wt.% | **Partially contradicted** — published LPBF Al-Er runs to 10 wt.% | Box is fine for the *precipitation* family; near-eutectic is a separate family the 25 g lot cannot feed (§6) |
| H | Sonotrode erosion contaminates the powder | **Strongly supported** — 2.6 wt.% Mo measured | Keep; plan a powder chemistry check |
| — | **Sacrificial Al cup inside the graphite crucible** | **No direct precedent, but every component of it is supported** | **Proceed, with the three conditions in §1** |

---

## 1. The aluminium-cup charging strategy — the answer to the 2026-09-09 question

**Short version: the literature has never tested this exact configuration, but it has tested every piece of
it, and each piece comes out in favour. Two conditions are non-negotiable and one is a design detail.**

### 1.1 What the cup actually is: an Al-clad compact, and those measurably outperform loose additions

The nearest published work is Najafabadi's McGill thesis on dissolving high-melting-point elements in molten
Al, which studied exactly two geometries: **powder wrapped in aluminium foil and plunged**, and **briquettes
of alloying powder mixed with aluminium powder**. Findings:

- Inside a briquette the **aluminium melts first**, then exothermic reaction with the solute particles drives
  the briquette **above bath temperature**, accelerating intermetallic formation and dissolution.
- Briquettes disintegrated in **25–35 s at 720 °C**; complete dissolution took **~420 s for Mn, ~330 s for Fe**.
- Loose fine powder added to an open melt has a documented failure mode: it **lacks the kinetic energy to
  penetrate the gas–liquid interface**, gets **trapped in dross, burns, and gives low recovery**; coarse powder
  penetrates but settles as sludge. The stated optimum for Mn additions is **40–140 mesh (100–400 µm)** —
  which independently lands on @gage-erickson's 150–300 µm target.

Razaz & Carlberg (2019) put a number on the compact advantage: in molten Al at 750 °C, **pure Mn flakes reached
only ~0.4 wt.% Mn after 9 minutes, while 80 % Mn compacts (i.e. Mn with aluminium interleaved) reached
1.5 wt.% in the same time** — nearly 4× the assimilation, for the same element, because the internal aluminium
supplies reaction area. A cup loaded with solute powder and melted from the outside in is the same geometry.

Separately, the Mg literature says ~**1 % of the aluminium oxidises per minute** while dross sits exposed, and
raising Mg from 0 → 2.5 wt.% increased melt loss by **4–8 %**; the standard mitigation is to **submerge the
addition below the melt surface**. The cup does that by construction.

**So the cup is not a workaround — it is the good-practice geometry, and it happens to be the one that a
robot can load.**

### 1.2 The oxide arithmetic strongly favours it

Native Al₂O₃ on aluminium is **2–4 nm** (Edison, citing Sun et al. 2006). Oxygen delivered by the aluminium
base of an 85 g/100 g charge, computed in [`charge_oxide_budget.py`](charge_oxide_budget.py):

| How the aluminium base arrives | ppm O in the Al | ppm O in the 100 g batch |
| --- | ---: | ---: |
| LPBF-grade powder, 30 µm | 413 | 351 |
| −100 mesh powder, ~60 µm | 207 | 176 |
| AEE AL-111, −50+100 mesh, ~212 µm | 59 | 50 |
| 4N shot, 9.5 mm | 1.3 | 1.1 |
| **Machined Al cup (~75 g, 6 mm wall)** | **0.7** | **0.5** |

Two things follow. The cup is **~100× cleaner than even the coarse AL-111 powder** and ~700× cleaner than
LPBF-grade Al powder — and Edison's independent estimate for 30 µm Al powder (0.04–0.07 wt.% O) matches the
measured 0.067 wt.% O of virgin AlSi10Mg powder, so the model is calibrated. But note that **4N shot is
already at ~1 ppm**: the cup's oxide advantage over shot is marginal. The cup's real wins are submersion,
the compact effect, and procurement (§1.5) — not oxide.

For scale, the solute powders' own oxide is small in the batch even at −325 mesh: Cr contributes ~11 ppm O,
Ti ~4 ppm, Mg ~3 ppm, Mn ~2 ppm. **The aluminium base was, and is, the whole oxygen story.**

### 1.3 Condition 1 (non-negotiable): the graphite crucible still needs a barrier — and Ti/Zr make it worse

The cup **delays** contact between molten Al and graphite; it does not prevent it. Once the cup melts, the
melt is on graphite, and Al₄C₃ formation is thermodynamically favourable (**ΔG° ≈ −35.1 kcal/mol at 970 °C**).
In a soak test, a TiB₂-painted graphite cube in molten Al at ~970 °C under argon had its coating cracked and
penetrated, and **no unreacted graphite remained** — Al₄C₃ forms with a **3.8:1 volume expansion** that
destroys the coating from inside. That test ran four weeks, so a several-minute hold is not the same
exposure; but this is a **20-run campaign in one crucible**, and carbide build-up and run-to-run carryover
accumulate.

The worse finding for us: **with Ti or Zr in the melt, TiC and ZrC are thermodynamically preferred over
Al₄C₃**. That means a graphite crucible does not merely dirty the melt — it **eats the very solutes the
Al₃(Sc,Zr,Ti) chemistry depends on**, and silently biases the composition low on exactly the alloy family
(Al-Zr-Er-Sc) where the budget is being spent.

**Recommendation: boron-nitride wash the graphite crucible bore, and re-apply between runs.** BN is the
consistently recommended barrier — molten Al wets it at a contact angle of **~160 ° up to 900 °C**, and it is
stable under reducing conditions far above our range. Keeping the graphite (rather than swapping to alumina)
is probably also necessary for a different reason: in an induction furnace the graphite is the **susceptor**,
so removing it changes the heating physics.

> ⚠️ **Caveat on BN that Edison did not raise and we should not ignore.** Molten Al does react slowly with
> BN: the reaction is self-limiting, forming an AlN skin, but **the boron goes into solution in the aluminium**
> ([Reactions between molten aluminum and pyrolytic boron nitride crucibles, *J. Vac. Sci. Technol. B* 11, 1032
> (1993)](https://pubs.aip.org/avs/jvb/article/11/3/1032/1046234/Reactions-between-molten-aluminum-and-pyrolytic)).
> Dissolved B plus our Ti gives **TiB₂** — an unplanned grain refiner and a Ti sink. It is probably a ppm-level
> effect at short holds, but it is a reason to (a) use a thin wash rather than a thick BN sleeve, and (b) put
> B and C on the ICP list for the first Ti-bearing powder.

### 1.4 Condition 2 (non-negotiable): budget dissolution time, and know that Ti poisons Mn kinetics

Two numbers to design around:

- **~7 minutes** for complete dissolution of an Mn briquette at 720 °C (Najafabadi); Fe ~5.5 min.
- **Adding just 0.12 wt.% Ti to the melt halved the Mn dissolution rate** and halved the intermetallic layer
  thickness (Razaz & Carlberg). Our Al-Mn-Cr-Zr family has Ti in it. Dissolution times measured on binaries
  are therefore **optimistic** for our chemistries.

Elemental dissolution is intermetallic-mediated in every case (MnAl₄/Al₁₁Mn₄ for Mn, Fe₂Al₅ for Fe, Al₃Ti for
Ti, Al₃Zr for Zr), and those layers grow parabolically and act as diffusion barriers unless stirring strips
them. The rePOWDER gives **electromagnetic stirring only, no mechanical stirrer**, so the melt practice
already in [`al-ti-melt-window.md`](al-ti-melt-window.md) — 950–1000 °C, 20–30 min stirred hold on the first
Ti run, then verify by ICP or by sectioning a button — is the right call and is now independently supported.

**Scandium is the outlier and it changes a purchase.** Edison: **direct dissolution of metallic Sc in Al at
800 °C takes more than one hour for gram-size pellets**, which is why commercial practice makes Al-Sc by
aluminothermic reduction (~90 % Sc recovery) and then adds the master at ~900 °C **with a 30 min superheat to
1150 °C**. The 2026-09-03 recommendation to buy the Thermo **5 g arc-cast Sc pellet** (`045118.KF`) is
therefore the *worst* elemental form for dissolution — a single monolithic gram-scale pellet is exactly the
geometry the literature says is slow.
**Amended: if Sc is bought elemental, buy chips or −40 mesh powder, not a pellet** (ESPI lists Sc chips
`Knc6313` and −40 mesh powder `Knd1178`, sold by the gram), **or make an Al-2Sc master in one dedicated melt
and dose that thereafter.** The cup helps here too — a pellet sitting in an Al cup is at least submerged and
in intimate contact with aluminium from the start.

### 1.5 The design detail: the cup's own oxide skin becomes a bag

When the cup melts at 660 °C its oxide skin does not vanish — it detaches and floats as film-like inclusions,
and Edison flags the specific risk that a **closed cup geometry forms a transient "oxide bag" that traps the
powder charge** until it ruptures, analogous to the oxide envelopes that stop scrap pieces coalescing. This is
also the bifilm mechanism: entrained double oxide films behave as internal cracks, and are the classic source
of scatter in Al castings.

Practical mitigations, in order of cheapness:

1. **Score or perforate the cup wall** (a few slits or drilled holes near the base) so the envelope ruptures
   at a predictable point instead of ballooning.
2. **Thin walls, wide base** — a squat cup ruptures earlier and has less oxide area than a tall thin one.
3. **Don't seal it.** An open cup, or a loose crimped foil lid, is better than a welded capsule.
4. **Hold and stir after the cup collapses**, which you are doing anyway for Ti/Zr.
5. Consider a **degas/skim step** if bifilms show up as porosity in the atomized powder.

### 1.6 Two consequences for procurement that follow directly from adopting the cup

- **The "4N Al in 150–300 µm doesn't exist off the shelf" problem disappears.** The cup is machined from
  solid, so the base can be bought as **4N rod, bar or ingot** — the form 4N aluminium is actually sold in.
  That removes the compromise recorded in [`quote-review-2026-08.md`](quote-review-2026-08.md) §1 (99.7 %
  AL-111 powder contributing 87 % of the impurity budget, ~2× the Scalmalloy Fe limit) at a stroke. It also
  means the AEE **AL-111 5 lb order is no longer load-bearing** — keep it as commissioning stock, but the
  campaign base should be 4N bar.
- **Weigh each cup.** Aluminium is the balance of the alloy, so a cup weighed to 0.01 g lets the solute doses
  be computed *against the actual cup mass* — which is strictly more accurate than dosing ~85 g of Al powder
  through an auger. The batch size becomes whatever the cup is, and that is fine.

### 1.7 What nobody has published

Edison was explicit about the gaps, and they should be treated as our own experiments, not as unknowns to be
argued about: no study evaluates a machined Al cup as a sacrificial charge container for small-batch
atomization; no element-specific recovery percentages exist for Al-wrapped Zr, Sc, Er, Ce or Li; Al₄C₃
formation rate as a function of temperature and time between 700–1100 °C is not quantified; and the effect of
carbide inclusions on Al₃(Sc,Zr,Er) L1₂ precipitation is unmeasured. **A single instrumented first run — cup,
BN-washed crucible, ICP on the powder for Ti/Zr/Sc/B/C/O — would produce data that the literature does not
have.**

---

## 2. Claim C is now split by element — this is the one recommendation that changes

The thread has been applying one rule ("buy the coarsest cut that feeds") to all sixteen elements. Edison
supports it for the aluminium base and **contradicts it for the refractory solutes**: dissolution in molten Al
is mass-transfer controlled through an intermetallic layer, so it scales with surface area, and coarse pieces
dissolve much more slowly. Razaz & Carlberg measured **Mn flakes dissolving only ~90 µm in 8 minutes at
750 °C**.

| Feedstock | Rule | Why |
| --- | --- | --- |
| **Al base** | as coarse as possible — **solid cup / bar / shot** | Oxide scales as 6δ/d and Al is 85 % of the charge; nothing to gain from powder |
| **Refractory solutes** — Ti, Zr, Cr, Fe, Ni, Mn | **fine end of what the doser tolerates**, 45–150 µm | Dissolution is the binding constraint, not oxide; their oxide contribution is ≤11 ppm of the batch |
| **Volatile / reactive** — Mg, Zn, Li | coarse (150–300 µm or lumps) | Oxidation and dust hazard dominate; they dissolve trivially |
| **Easy solutes** — Si, Cu, Sn | whatever is cheap and flows | Neither constraint binds |

This **retroactively vindicates the ESPI −325 mesh Cr and Ti lines** that [`quote-review-2026-08.md`](quote-review-2026-08.md)
called "won't feed" on flowability grounds. Metallurgically they are the *better* buy; the objection was
always about the auger, not the melt. Since Cr and Ti together are ~25 g for the whole campaign, pre-weighing
them into the cup by hand — inside the glovebox, where the −325 mesh Ti dust hazard is largely defused —
resolves the conflict without spending $425 on the Fisher Cr line. The dust-safety verdict on −325 mesh Ti
(UN 2546, MIE 3–30 mJ) is unchanged and still argues for keeping that lot small and handling it under argon.

---

## 3. Purity (Claims A and B): keep the plan, drop the confidence

Edison found **no published quantitative purity threshold** — nobody has shown that x ppm Fe in Zr feedstock
degrades Al₃Zr precipitation by a measurable amount. The physical argument survives and is arguably sharper
than we had it: Zr's equilibrium solubility in Al is ~0.08 at.%, and **the critical supersaturation to nucleate
Al₃Zr is only ~0.021 at.% Zr** (Knipling 2007), so there genuinely is very little margin for anything that
competes for or ties up the solute. But it is a mechanism argument, not a measured threshold, and the docs
should say so.

Claim B is supported with numbers: oxide film **2–4 nm**; virgin AlSi10Mg powder **0.067 wt.% O**, rising to
**0.257–0.274 wt.% after 96 h** of thermal aging; ~120 ppm O picked up over five LPBF re-use cycles. Two
operational consequences: **oxygen belongs on every CoA**, and **powder ages** — the drying step
(80 °C, ≥10 h) matters, but so does not leaving material open.

> **Unit-conversion warning on Edison's own numbers.** The report states Zr solubility as
> "~0.0008 mole fraction (~0.07 wt%)" and Er solubility as "~0.05 wt%". 0.0008 mole fraction of Zr in Al is
> **0.27 wt.%**, not 0.07 wt.%; and the widely cited Er figure is **0.046 at.% = 0.28 wt.%** (van Dalen 2009,
> already cited in [`erbium-bounds-and-lot-size.md`](erbium-bounds-and-lot-size.md)). Both of Edison's
> parentheticals look like at.% values wearing a wt.% label — the exact trap that doc warned about. **Our
> 0.28 wt.% Er stands; do not "correct" it to 0.05.**

---

## 4. Volatiles (Claim F): manganese needs re-classifying — for atomization, not for melting

[`al-ti-melt-window.md`](al-ti-melt-window.md) §5.1 argued that Mn's vapour pressure is four orders of
magnitude below Mg's, so Mn losses must be oxidation/dross rather than evaporation, and therefore need an
argon cover rather than an over-charge. **That reasoning is right about the melt and wrong about the
atomization step**, and three independent ultrasonic-atomization studies say so:

- Żrodowski et al. (2021), cold-crucible UA: "high Mn and Zn evaporation, **especially in the finest
  particles**".
- Bałasz et al. (2024), 316L by UA: **Mn measured from 1.08 to 3.88 wt.% across runs** — a 3.6× spread in a
  single nominal alloy.
- Goncharov et al. (2026), HEA by UA: **Mn 10 → 8.9 wt.%, Cu 10 → 8.8 wt.%** through processing.

The mechanism is the atomization itself: a fine droplet has enormous surface-to-volume ratio and flies through
hot gas, so the loss happens *after* the melt, where a crucible-surface argument does not apply — hence
"especially in the finest particles". **Mn belongs on the over-charge list with Mg and Zn**, and the
over-charge should be **calibrated against measured powder chemistry**, not assumed, because the size
dependence means it will vary with atomization frequency. Cu appearing in the Goncharov data is a mild
surprise and worth watching.

This also sharpens the volatile problem generally: our purchase model's flat 5–15 % over-charge is a
placeholder. One instrumented run with ICP on the powder (not the button) calibrates it for real.

---

## 5. Melt window (Claim E): the liquidus stands, but the superheat rule of thumb does not agree with us

Edison confirms the physics (Ti and Zr dissolve via peritectic reactions far below their melting points) and
could not independently verify the CALPHAD liquidus values, calling them "consistent with the steep liquidus
slopes characteristic of peritectic Al-Ti and Al-Zr systems". Our numbers were already validated three ways
against experiment in [`al-ti-melt-window.md`](al-ti-melt-window.md) §3, so they stand.

Two footnotes:

- **Edison's peritectic compositions are the solid-side numbers.** It reports "Al-Ti peritectic ~665 °C with
  ~1.0 wt.% Ti" and "Al-Zr peritectic ~660.5 °C with ~0.28 wt.% Zr". Those are the **maximum solid
  solubilities** (~1.3 wt.% Ti, 0.28 wt.% Zr), not the liquid compositions at the peritectic (~0.15 wt.% Ti,
  ~0.11 wt.% Zr). No change to our liquidus table.
- ⚠️ **The superheat rule of thumb conflicts with our setpoint.** Edison cites Bałasz et al. operating
  ultrasonic atomization at **1.3–1.5 × the absolute melting temperature**. For Al-1Ti (liquidus 868 °C =
  1141 K) that is **1210–1440 °C**, against the **968 °C** our liquidus + 100–150 °C rule gives. That is not a
  small discrepancy — 1.3 T_m would put us near the induction ceiling and would evaporate Mg and Zn
  catastrophically. The rule was derived on steels; whether it transfers to aluminium (much lower surface
  tension, much higher thermal conductivity, and volatile solutes) is exactly the question.
  **This is a direct question for AMAZEMET: what melt superheat do they run for Al alloys on the rePOWDER, and
  is the +100–150 °C figure sufficient for stable film formation on the sonotrode?** It should go in the same
  email as the crucible-material and Mg-atomization questions.

---

## 6. Erbium (Claim G): the box is right for the alloy family we chose, and wrong for the one we didn't

Edison calls [0, 3] wt.% Er "partially contradicted" because published LPBF Al-Er work runs to **Al-10Er**
(Li et al. 2026: Al-10Er, Al-10Er-5Mg-0.6Sc-0.3Zr, Al-10Er-5Mg-1.2Sc-0.8Zr). That is not really a
contradiction — it is a **different alloy family**: near-eutectic Al-Er "nano-skeleton" alloys strengthened by
a eutectic network, versus the L1₂-precipitation-strengthened Al-Zr-Er-(Sc,Ni) alloys the campaign is aimed
at, whose published optimum is **2.33 wt.% Er** and which [0, 3] brackets correctly with the optimum interior
to the box.

What *does* change is the purchasing consequence, and it is worth stating plainly for @sgbaird's
"$1 k per rare earth" cap:

- At the precipitation-family bounds, **25 g of Er is correctly sized** (15–30 g consumed in round one).
- At near-eutectic bounds, **10 wt.% Er = 10 g per 100 g run**, so 25 g is **2.5 runs**. The near-eutectic
  family is simply not affordable under the current cap and should be a deliberate, separately funded
  decision — not something to discover halfway through a campaign.

Other bounds Edison supplied, useful for the design-space file that still does not exist:
**Sc** 0.6–0.8 wt.% (Scalmalloy: Al-4.6Mg-0.66Sc-0.42Zr-0.49Mn), Al-Sc eutectic ~0.5 wt.%;
**Zr** 0.2–0.5 wt.% typical, up to ~4.4 wt.% explored;
**Ce** 6–16 wt.% in near-eutectic LPBF alloys, eutectic ~10 wt.%, DuAlumin-3D ~9 wt.%;
**Mn** 0.3–0.8 wt.% in Scalmalloy up to ~4.9 wt.% in Al-Mn LPBF alloys.
One discrepancy left open: the Al-Er eutectic is given as **~6 wt.%** by Lei (2023) and **~12.7 wt.%** by Li
(2026); the binary Al–Al₃Er value is the ~6 wt.% one.

---

## 7. Sonotrode contamination (Claim H): confirmed, with a units correction

Goncharov et al. (2026) measured **2.6 wt.% Mo** in ultrasonically atomized HEA powder from sonotrode erosion,
concentrated in interdendritic regions. Earlier notes in this thread said "~2.6 at.%" — it is **wt.%**.
Mitigations in the literature: inert/wear-resistant sonotrode material, improved sonotrode design, and
99.9999 % argon. Practical implication for us: **whatever the sonotrode is made of belongs on the ICP list**
for the first powder, alongside B and C from §1.3. If it is Ti, that is directly confounding for the Ti runs.

---

## 8. What to do next

1. **Adopt the cup**, with a BN-washed graphite crucible and scored/perforated cup walls (§1.3, §1.5).
2. **Re-spec the aluminium base as 4N bar or rod** rather than AL-111 powder (§1.6). This is the single
   biggest chemistry improvement available and it is now cheap.
3. **Amend the Sc form**: chips or −40 mesh, not a monolithic pellet — or make an Al-2Sc master once (§1.4).
4. **Split the particle-size rule by element** (§2), which un-rejects the cheap ESPI −325 mesh Cr and Ti.
5. **Move Mn onto the over-charge list** and calibrate all over-charges from measured powder chemistry (§4).
6. **Ask AMAZEMET** three things in one email: the superheat they run for Al alloys (§5), the crucible
   material and whether they endorse a BN wash, and the sonotrode alloy.
7. **Instrument run #1**: ICP the powder for Ti, Zr, Sc, Mn, Mg, Zn plus B, C, O and the sonotrode element.
   The gaps Edison identified in §1.7 are all answerable with that one run.

---

## Sources

Everything above is traceable to the two raw Edison reports
([crucible/charging](edison-crucible-and-charging-2026-09.md),
[elements/master alloys](edison-elements-and-master-alloys-2026-09.md)), which carry the full citation lists.
Key papers behind the verdicts: Najafabadi (1996) *The kinetics of dissolution of high melting point alloying
elements in molten aluminium*, McGill; Razaz & Carlberg (2019) *On the dissolution of Mn and Fe in molten Al*;
Knipling et al. (2007) on Al₃Zr nucleation; Fedina et al. (2022) on AlSi10Mg powder oxygen; Sun et al. (2006)
on Al native oxide thickness; Røyset (2005) and Mukhachov (2016) on Sc dissolution and Al-Sc master alloys;
Schilling (1988) on Al₄C₃ in graphite; Rudolph (2013) on BN release coatings; Campbell / Dispinar on bifilms;
Żrodowski (2021), Bałasz (2024) and Goncharov (2026) on ultrasonic atomization losses and sonotrode pickup;
Li et al. (2026) and Lei et al. (2023) on Al-Er LPBF alloys; Plotkowski (2024) on Al-Ce.

Non-Edison source used in §1.3: [Reactions between molten aluminum and pyrolytic boron nitride crucibles,
*J. Vac. Sci. Technol. B* 11, 1032 (1993)](https://pubs.aip.org/avs/jvb/article/11/3/1032/1046234/Reactions-between-molten-aluminum-and-pyrolytic).
