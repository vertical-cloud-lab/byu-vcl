# Storing the atomizer feedstock powders without a glovebox

Answers issue [#230](https://github.com/vertical-cloud-lab/byu-vcl/issues/230): *will silica
oxide (desiccant) contaminate our powders?* — plus the other measures worth taking until the
glovebox arrives.

Backed by two Edison Scientific `paperqa3-high` literature runs; raw trajectories and full
cited answers are in [`outputs/issue-230-desiccant/`](../outputs/issue-230-desiccant).

| | |
| --- | --- |
| Powders in scope | The #161 feedstock list: elemental Al, Mg, Si, Mn, Cr, Ti, Fe, Ni, Cu, Zn, Sn at a 150–300 µm cut, plus crushed Al-Zr / Al-Sc / Al-Er / Al-Ce / Al-Li master-alloy granules. Also the existing 15–45 µm AlSi10Mg, which is the most exposure-sensitive thing in the cabinet. |
| Storage horizon | Months, room temperature, CB154 with the enclosure dehumidifier running (#42). |
| Verdict | Silica gel is chemically safe. Keep using it — but **outside** the powder jar, and **never** the blue indicating kind. |

## The short answer

**Silica gel will not chemically attack the powders at room temperature.** The reactions
people worry about are real but need heat that room-temperature storage never supplies:

- `4Al + 3SiO₂ → 2Al₂O₃ + 3Si` is strongly favourable thermodynamically (≈ −941 kJ at
  800 °C) but needs **≥ ~650 °C** to proceed measurably, and runs readily only once the Al is
  molten ([Islam et al. 2022](https://doi.org/10.3389/fmats.2022.977869)).
- `4Mg + SiO₂ → Mg₂Si + 2MgO` is likewise favourable at 923 K and likewise needs the heat
  ([Kondoh & Luangvaranunt 2003](https://doi.org/10.2320/matertrans.44.2468)).

At 20–25 °C the native passive oxide on each particle plus the solid-state diffusion barrier
means there is no credible solid-state or vapour-mediated reaction with *any* powder on the
list — Al, Mg, and the master alloys included. So the premise of the plan is sound.

**Three real risks remain, and all three are avoidable.**

### 1. Physical silica dust — the actual contamination route

Silica gel beads are friable. Shipping vibration, handling, and thermal cycling abrade them,
and the fines migrate through sachet fabric. That dust is inert in the jar and only becomes a
problem in the crucible, where it is exactly the reaction above: SiO₂ reduced by the melt,
producing **Si that shifts your composition off-spec** and **hard Al₂O₃ inclusions** that
survive atomization. Those inclusions ride into the atomized droplets and become lack-of-fusion
initiation sites in the eventual LPBF part, on top of being a nozzle-clogging risk.

For Mg-bearing melts the products are MgO and Mg₂Si instead — and note that even *colloidal*
silica binders cause severe mold-metal reaction in Mg investment casting
([Jafari et al. 2013](https://doi.org/10.1080/10426914.2013.811729)), which is a good measure
of how little silica it takes to matter.

**Fix:** never put desiccant loose in with the powder. Nest the containment instead (below).

### 2. Blue indicating gel — the one genuinely bad choice

Cobalt-chloride indicating gel carries **0.05–4.5 wt% CoCl₂**, and a meaningful fraction is
water-soluble and *mobile* — it demonstrably redistributes across the silica surface as
humidity cycles ([Balköse et al. 1999](https://doi.org/10.1016/s0169-4332%2899%2900088-4)). That
is a direct chloride transport path onto the powder, and chloride is the single worst
contaminant for aluminium: Cl⁻ adsorbs on the passive Al₂O₃ film, penetrates it, and
destabilises it into pitting ([Natishan & O'Grady 2014](https://doi.org/10.1149/2.1011409jes),
404 citations). Atmospheric Al corrosion starts around **70% RH once chloride is present**
([Graedel 1989](https://doi.org/10.1149/1.2096869)). Cobalt is also a ppm-level trace
contaminant in Al alloys in its own right.

Orange methyl-violet gel avoids the cobalt and chloride but adds an organic dye that
decomposes on melting — better, still not ideal.

**Fix:** use **non-indicating** desiccant only. Check the McMaster packets we already have and
set aside any that are blue. Put a cobalt-free humidity indicator card in the *outer* box if
you want a visual check.

### 3. Silica gel's humidity floor over months

Fresh activated silica gel can pull a tight enclosure below 4% RH, but it has a Type II/IV
isotherm — it does **not** hold a fixed setpoint. As it loads, container RH climbs; and because
water is bound weakly (heat of adsorption ~18 kJ/mol on 60 Å silica gel vs ~50–58 kJ/mol on
zeolite, [Wynnyk et al. 2019](https://doi.org/10.1021/acs.jced.9b00233)), **warming the
container makes it give the water back**.

The target to beat: Al powder showed no significant mass change, active-metal loss, or
hydroxide growth at **< 10% RH** over 14 days at 333 K, while at ~80% RH a 30 µm Al powder lost
active metal from ~99% to ~87%
([Paravan et al. 2019](https://doi.org/10.1016/j.actaastro.2018.08.001)). MgO surfaces start
building hydrated layers above **33% RH** ([Bracco et al. 2024](https://doi.org/10.1021/acsami.3c14823)).

**Fix:** generous, freshly regenerated, non-indicating desiccant; or step up to molecular
sieve 3A for the multi-month lots. Keep the cabinet away from heat sources so it is not
thermally cycled.

### Desiccant ranking

| Desiccant | Practical floor at 20–25 °C | Usable capacity | Verdict for our powders |
| --- | --- | --- | --- |
| **Molecular sieve 3A / 4A**, non-indicating | sub-1% RH | ~18–22 wt% | **Preferred** for months-long storage. Holds water tenaciously at low RH, resists thermal desorption. Regenerate at ~200–300 °C. 3A is the more water-selective. |
| **Silica gel**, non-indicating | < 4% fresh, rising as it loads | ~20–35 wt% | **Fine as-is** for the outer enclosure. What we already own; adequate if generously sized and kept out of the jar. |
| Activated alumina | ~1–10% RH | ~10–20 wt% | Acceptable second choice. Attrition fines are Al₂O₃ — less foreign to an Al melt than silica, but still an inclusion. |
| Drierite (CaSO₄), non-indicating | low single-digit RH | ~6.6 wt% | Clean but low capacity, so frequent replacement. Indicating grades may contain cobalt. |
| CaO (quicklime) | very low while unreacted | 32.1 wt% theoretical | **Avoid.** Caustic dust, swells on hydration (can rupture the packet), takes up CO₂. |
| CaCl₂ | low initially, then deliquesces | >100 wt% | **Avoid outright.** Ends as a chloride brine — the worst case for Al pitting. |
| P₂O₅ | extremely low | 38 wt% theoretical | **Avoid.** Violent hydration to phosphoric acid. |

### Nested containment — the actual storage recipe

1. Powder stays in its **original, tightly closed supplier container**. This is explicit NIST
   AM.SOP.2 guidance ([Moylan et al. 2013](https://doi.org/10.6028/nist.tn.1801)); ASTM F3303
   wants a moisture-impermeable container.
2. That sealed jar goes **inside a larger airtight box that holds the desiccant**. The
   desiccant then conditions the air *around* the jar, cutting seal ingress, and can never
   shed dust into the powder.
3. Desiccant travels in **sealed low-shedding sachets** (Tyvek/non-woven), not loose beads —
   and not resting on the powder even inside the jar.
4. Cobalt-free humidity indicator card or a small RH/T logger in the outer box, so desiccant
   exhaustion and seal failure are visible rather than inferred.
5. Outer box in a cool, dry, ventilated metal cabinet, away from heat.

## Three more things to do without a glovebox

Ranked by payoff. All four measures are cheap next to the ~$4–5k glovebox.

### A. Argon purge-and-seal into foil barrier bags — biggest single win

Purge the container headspace with dry Ar (three or more purge–vent cycles), fill as full as
practical to minimise headspace, and overbag rigid containers in heat-sealed
aluminium-foil/metallised barrier pouches, specifying the lowest certified OTR/WVTR available.

Powders held under high-purity Ar (<0.5 ppm O₂/H₂O) showed **no gas desorption** on later
vacuum heating, while humid-air-exposed powder gave off substantial hydrogen and water
([Yamasaki & Kawamura 2004](https://doi.org/10.2320/matertrans.45.1335)). A workable field
target is **O₂ < 100 ppm, H₂O < 10 ppm** — the operational limit used for genuinely reactive
powders ([Towndrow 2007](https://doi.org/10.1016/j.powtec.2006.10.018)). Argon-filled sealed
steel drums are the standard long-term form for metal powders
(Benson 2012, *Safety considerations when handling metal powders*).

Be honest about the limit: purge-and-seal is **not** a glovebox. Loading in open air traps some
air and moisture, and film permeates slowly. It is still far better than ambient.

**Do not** use iron-based oxygen absorber sachets. They need moisture to activate, which is
exactly what we are excluding, so they are inert in a dry package — plus rupture and Fe
contamination risk ([Gupta 2024](https://doi.org/10.1007/s13197-023-05681-8)).

### B. Single-run aliquots, so a jar is opened once

Subdivide each lot on arrival into portions sized for one atomizer run and seal each under Ar;
a published protocol used **50 g in borosilicate vials**
([Grubbs et al. 2022](https://doi.org/10.3390/met12040603)). Each aliquot is opened once,
immediately before use, which eliminates the cumulative exposure that a repeatedly-reopened
bulk jar accrues. It also gives per-aliquot traceability and confines any contamination.

Containers: **grounded gasketed metal cans** are best (impermeable, groundable, fire-resistant);
borosilicate glass is a fine barrier for small aliquots but cannot be grounded, so static
control has to come from elsewhere; **HDPE is not suitable** for long-term reactive storage
unless overbagged in a metallised pouch. Bond and ground drums, scoops, and funnels during
transfer — metal powders hold charge, and the cheap humidity-raising trick for dissipating it
is unavailable to us here (Ebadat 2010, *Electrostatic hazards associated with liquid and
powder processing*).

### C. Humidity/temperature control and monitoring, with condensation discipline

Published metal-powder guidance is 15–25 °C and <55% RH; for reactive Al, aim lower —
**≤30% RH in the room**, which the enclosure dehumidifier (#42) should already deliver, and
**≤30% RH during any open handling**. Experimental 17–29% RH preserved AlSi10Mg flow far
better than humid exposure ([Peres et al. 2024](https://doi.org/10.1590/1980-5373-mr-2023-0490));
at 80% RH the powder formed agglomerates that would not disperse even after shaking
([Weiss et al. 2022](https://doi.org/10.1016/j.procir.2022.08.102)).

The operational trap: **let a cold sealed container reach room temperature before opening it.**
Opening cold glass in a warm room condenses water directly onto the powder — worse in one
minute than months of good storage bought. Stable temperature matters more than low
temperature. The AirGradient going into the enclosure (#219) covers the room; add an indicator
card or small logger inside the outer boxes.

### D. Pre-melt vacuum drying — reconditioning, not a substitute

Worth having in the SOP because it recovers powder that has already seen some air.
Conservative schedule: **80–120 °C for 2–8 h under dynamic vacuum**, cool under vacuum or dry
Ar, keep sealed until charged. Validate by mass loss.

Respect the ceilings, which are alloy-dependent
([Yamasaki & Kawamura 2004](https://doi.org/10.2320/matertrans.45.1335)):

| Temperature | What happens |
| --- | --- |
| ~400 K (127 °C) | water desorption rises sharply — this is the useful window |
| ~390 K (117 °C) | fresh oxide growth begins on *highly hydrated* Al-Zn-Mg-Cu-Ag |
| ~450 K (177 °C) | fresh oxide growth begins on less-hydrated Al-Ti-Fe-Cr |
| ~473 K (200 °C) | Al–water reaction evolves hydrogen; avoid for unknown Al-Mg, Al-Li, or precipitation-sensitive powder |

Drying cannot undo hydroxide that already formed, and the benefit is process-specific: one
study cut hydrogen in the finished part by up to 25%
([Kramer et al. 2026](https://doi.org/10.1007/s00170-025-17198-9)), another found little
porosity benefit because the machine's vacuum pre-cycle had already done the work
(Van Cauwenbergh 2019). Treat the schedule as something to qualify, not inherit.

For transfers specifically, an **inflatable argon-purged glovebag** (tens to low hundreds of
dollars) is the honest stopgap: much better than open air, less reliable than a rigid
recirculating box because bags leak and have no continuous purification. Use **Ar, not N₂**,
wherever Li or Mg is involved — Li forms Li₃N (and powdered Li has ignited in flowing N₂ at
388–410 °C, [Jeppson et al. 1978](https://doi.org/10.2172/6885395)), and Mg forms Mg₃N₂ when
heated. N₂ is acceptable for Al, Si, Cu, Fe, Ni, Sn, Mn, Cr, Ti, Zn at room temperature, but
one gas for everything is simpler and safer.

## Shelf life to expect

Sealed under Ar with desiccant at <30% RH and 15–25 °C, micron-scale Al and Al-alloy powder
should hold specification for **several months to about a year**. Recheck oxygen, moisture, and
flow at **six months**; treat Mg, Li-, Zn-, and Sc-bearing material as more sensitive and
recheck every **2–3 months**.

Benchmarks for what degradation looks like:

| Study | Material | Condition | Result |
| --- | --- | --- | --- |
| [Fedina 2022](https://doi.org/10.1016/j.powtec.2022.118024) | AlSi10Mg | 96 h accelerated ambient aging | O: 0.067 → 0.257 wt% (~3.8×); printed porosity 3.16% → 6.5% |
| [Ferreira 2025](https://doi.org/10.1007/s00170-025-16619-z) | AlSi10Mg | 21 LPBF reuse builds | O: ~0.08 → ~0.19 wt%, ≈0.005 pp/build |
| [Raza 2021](https://doi.org/10.1016/j.matdes.2020.109358) | AlSi10Mg | ~30 months reuse | surface oxide 4 nm → 38 nm; up to 3% heavily oxidised spatter |
| [Paravan 2019](https://doi.org/10.1016/j.actaastro.2018.08.001) | ~30 µm Al | 14 d, 333 K | <10% RH: no marked change. ~80% RH: ~13% active Al lost |

One caveat on reading those numbers across to our inventory, which is our inference rather than
something the literature runs measured: every figure above is for LPBF-grade powder in the
15–45 µm range, and moisture/oxide pickup scales with specific surface area, i.e. roughly as
1/diameter. Our **150–300 µm cut therefore has on the order of one-seventh the surface area per
gram** of a 30 µm powder and should degrade proportionally more slowly — the coarse-cut decision
from #161 is doing real preservation work here. The exception is the existing **15–45 µm
AlSi10Mg**, which *is* the fine grade these studies measured, so treat that jar as the
sensitive one and give it the Ar backfill first.

## What this changes

Nothing about the plan in #230 is wrong. Concretely:

- ✅ Airtight containers + silica gel for several months: **keep doing this.**
- ⚠️ Sort the McMaster packets and use **non-indicating only** — discard/quarantine blue ones.
- ⚠️ Move the desiccant **out of the powder jar** into a nested outer box.
- ➕ Argon purge-and-seal the aliquots, especially the fine AlSi10Mg and anything Mg/Li-bearing.
- ➕ Aliquot to single-run portions on arrival; keep unopened supplier jars unopened.
- ➕ Indicator card or logger in each outer box; equilibrate to room temperature before opening.
- 🔜 Molecular sieve 3A is the upgrade if anything has to sit past ~6 months.

## Provenance

Two Edison Scientific `job-futurehouse-paperqa3-high` runs, 22 September 2026:

| Task | ID | Artifacts |
| --- | --- | --- |
| Silica gel contamination | `74d48c32-93d1-4b78-8af1-6528dccc68eb` | [`silica-gel-contamination.*`](../outputs/issue-230-desiccant) |
| Glovebox-free preservation | `b44fa395-5d25-4e4e-975e-aeec456eb3c4` | [`no-glovebox-preservation.*`](../outputs/issue-230-desiccant) |

Each has `.query.txt` (prompt), `.answer.md` and `.formatted_answer.md` (full cited answer),
`.references.md` (bibliography), and `.trajectory.json` (complete run). Re-fetch or extend with
[`scripts/edison_wait_fetch.py`](../scripts/edison_wait_fetch.py).
