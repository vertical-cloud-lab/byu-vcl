# Powder Purity & Particle-Size Recommendations for Atomizer Feedstock Acquisition

**Context:** [Issue #161 — Atomizer Powder Acquisition](https://github.com/vertical-cloud-lab/byu-vcl/issues/161). This note distills the [Edison Scientific literature report](edison-lpbf-feedstock-purity-report.md) into actionable purchasing guidance, and reconciles it with the shopping list drafted in [digital-alloy-lab-private PR #88](https://github.com/vertical-cloud-lab/digital-alloy-lab-private/pull/88).

Workflow assumed: blend elemental feedstocks → melt → ultrasonic atomization (~100 g batches, Amazemet rePowder-type) → LPBF-usable Al-alloy powder. The base is Al with additions drawn from Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc, Li, Er, Zn, Sn.

## 1. Recommended purity per element

| Element | Buy this purity | Preferred form | Notes |
| --- | --- | --- | --- |
| Al (base) | **99.9–99.99% (4N preferred)** | Granules/shot/ingot; coarse powder acceptable | >85 wt.% of every alloy — impurities here dominate total contamination. 4N mainly buys lower Fe/Si. |
| Mn | ≥99.7% (99.9% electrolytic is fine) | Granules/lumps or coarse powder | 99.7% used successfully in published Al-Mn-Ce EIGA work. Volatile — over-charge 5–15%. |
| Cr | **99.9%** | Coarse powder or granules | 99.5% (shopping-list item) is marginal; 99.9% is the literature-backed level. 99.99% is *not required* — see §4. |
| Zr | 99.9% min; 99.95% if Zr is a key microalloy | **Al-Zr master alloy (Al-10Zr) preferred**; else granules/coarse powder | Elemental Zr powder is DG class 4.2 (ships water-wet, hazmat fees) — master alloy avoids that entirely. |
| Mg | ≥99.9% | **Al-Mg master alloy (e.g., Al-50Mg)** or coarse granules/turnings; avoid fine powder | Fire hazard as fine powder; high vapor pressure — over-charge 5–15%. |
| Si | 99.9% | Lump/granule or coarse powder | Limits Fe-bearing brittle phases; 99.5% coarse Si (shopping list) is acceptable for first campaigns. |
| Cu | 99.9% | Granules/lumps or coarse powder | Cu losses observed during remelt/atomization — clean feedstock aids composition control. |
| Ti | 99.9% | **Al-Ti or Al-5Ti-1B master alloy preferred** | Standard grain-refiner practice; avoids undissolved Ti at 100 g melt scale. |
| Fe | 99.9% (only if intentional addition) | Granules/coarse powder | Otherwise Fe is the impurity to *avoid* — Scalmalloy spec holds Fe ≈ 0.068 wt.%. |
| Ni | 99.9–99.99% | Granules preferred | 99.99% granulate precedent in ultrasonic-atomization literature. |
| Ce | >99% min; 99.5–99.9% preferred | **Al-10Ce/Al-20Ce master alloy** or clean lumps | Cheapest rare earth; >99% Ce demonstrated in Al-Mn-Ce LPBF work. |
| Sc | 99.5% min; 99.9% if affordable | **Al-2Sc master alloy strongly preferred** | Elemental Sc is ~$3,000–15,000/kg and oxidizes readily; Al-2Sc is industry standard. |
| Li | Master alloy only | **Al-5Li/Al-10Li master alloy — do not buy elemental Li powder** | Elemental Li powder is pyrophoric and a severe safety hazard; handle master alloy under Ar. |
| Er | 99.9% min; 99.95% if primary strengthener | **Al-5Er/Al-10Er master alloy** or granules | 99.9% Er granulate precedent in ultrasonic-atomization literature. |
| Zn | 99.9–99.99% | Lump/granule or master alloy | Volatile — over-charge 5–15%. |
| Sn | 99.9% | Lump/granule | Keep Pb/Bi/Sb tramp low (segregation/cracking risk). |

## 2. Particle size: buy coarse, not fine

The 15–45 µm LPBF size window **does not apply to melt feedstock** — everything gets fully melted before atomization, so dissolution kinetics are irrelevant. Coarser is strictly better:

- **Less oxide carried into the melt** — oxide burden scales with specific surface area, and surface oxide films are the top driver of lack-of-fusion porosity in Al LPBF.
- **Less adsorbed moisture → less hydrogen porosity.**
- **Safer** — fine Al/Mg/Li powders are dust-explosion and pyrophoricity hazards; coarse forms often also ship cheaper (fewer DG surcharges).

**Buy:** granules/shot/lumps (1–5 mm) for Al, Cu, Zn, Ni, Si, Sn; coarse powder (45–150 µm / –100 mesh) or small granules for the high-melting elements (Cr, Mn, Ti, Zr, Fe); master-alloy pieces/chips for Sc, Er, Ce, Li (and ideally Zr, Ti, Mg).

## 3. Handling requirements (budget for these)

- Dry all feedstock at **80 °C for ≥10 h** before melting (removes adsorbed moisture → hydrogen).
- Weigh/blend reactive feedstocks (Li master alloy, Mg, fine Al) under **Ar** (glovebox or blanket).
- Purge the atomization chamber to low O₂ (published ultrasonic-atomization work ran at 23–50 ppm O₂).
- **Over-charge volatile elements (Mg, Zn, Li, Mn) by 5–15%** to compensate evaporation losses.
- Expect possible **sonotrode contamination** (≈2.6 at.% Mo pickup reported with Mo sonotrodes on rePowder-type systems) — plan ICP/EDS checks of atomized powder.

## 4. Reconciliation with the PR #88 shopping list

The core-five list (Al 4N ≤45 µm, Mn 99.9%, Cr 99.5%, Zr 99.5% water-wet, Si 99.5%) is workable, with these adjustments suggested by the literature:

1. **Al:** 99.99% is right, but prefer **shot/granules over ≤45 µm powder** — fine 4N Al powder maximizes the oxide/moisture surface you paid a premium to avoid, and adds a dust hazard. If powder is the only stocked form, take the coarsest cut offered.
2. **Cr (re: the 99.5% vs 99.99% question):** literature support lands at **99.9%** — used directly in a blended → remelted → ultrasonically atomized workflow. 99.99% does no harm and is fine if the price delta is small, but it is not required; Cr is not one of the impurity-critical elements. The elements that genuinely justify premium purity are **Al (the base) and the microalloying additions Zr, Er, Sc**, where oxide inclusions poison the L1₂ precipitation these alloys depend on.
3. **Zr:** consider **Al-10Zr master alloy instead of water-wet elemental Zr** — same metallurgical result, no class 4.2 dangerous-goods shipping (~$100–300 hazmat saved), better dissolution uniformity.
4. **Si:** 99.5% coarse Si is acceptable to start; move to 99.9% if Fe-bearing intermetallics show up in characterization.
5. **Second-wave elements (Mg, Cu, Zn, Sn, Ni, Ti, Fe, Ce, Sc, Li, Er):** buy per the table in §1, favoring master alloys for Li (mandatory), Sc, Er, Ce, Zr, Ti.

## 5. Which elements to buy as Al master alloys — safety/handling rationale

Beyond Li (mandatory — elemental Li powder is pyrophoric), the elements below have a genuine safety or handling case for the master-alloy route, ranked by strength of case:

| Element | Master alloy | Why |
| --- | --- | --- |
| **Zr** | Al-10Zr | **Safety + cost:** elemental Zr powder is pyrophoric (DG class 4.2), ships water-wet with $100–300 hazmat surcharges, and must be dried before an Al melt — a hazardous step in itself. The master alloy is a benign solid. |
| **Ce** | Al-10Ce / Al-20Ce | **Safety:** finely divided Ce metal is pyrophoric (mischmetal is literally lighter-flint material) and Ce lumps tarnish/oxidize rapidly in air, carrying oxide into the melt. |
| **Ti** | Al-5Ti-1B rod | **Safety + metallurgy:** fine Ti powder is combustible; Ti melts at 1668 °C and dissolves slowly in a 100 g Al melt — undissolved Ti particles become LPBF defects. Grain-refiner rod is the cheap, standard solution. |
| **Sc** | Al-2Sc | **Cost + oxidation:** elemental Sc oxidizes readily (oxide poisons the Al₃Sc L1₂ chemistry) and costs thousands per kg. Al-2Sc is the industry standard; there is no good elemental route. |
| **Er** | Al-5Er / Al-10Er | **Oxidation + cost:** rare-earth surface oxidation, same L1₂ argument as Sc. |
| **Mg** | optional (Al-50Mg) | **Judgment call:** fine Mg powder is a dust-explosion hazard — never buy it — but coarse 99.99% Mg granules/turnings are safe, cheap, and easier to certify at 4N than a master alloy. Prefer elemental granules unless a 4N-basis Al-Mg master is quoted cheaply. |

Elements with **no safety case for master alloys** — buy elemental in coarse form (granules/shot/lumps): Mn, Cr, Si, Cu, Zn, Ni, Fe, Sn. (Al-Mn/Al-Cr/Al-Fe/Al-Ni waffle masters exist as a dissolution convenience if melt temperature is capped ≤ ~850 °C, but they add cost and another certificate of analysis to chase.)

**Purity caveat for the 4N-list elements (Zr, Er, Sc) bought as masters:** a single "99.99%" label doesn't apply to a two-component master alloy. What protects the precipitation chemistry is (1) a **4N Al base** in the master and (2) **low oxygen** — request certificates of analysis reporting O, Fe, and Si. A master made from 4N Al with 99.9%+ solute is metallurgically equivalent to, and lower-oxide than, blending 4N elemental powders, because the solute's surface oxide is already gone.

## Sources

- [Edison Scientific full report with 26 literature citations](edison-lpbf-feedstock-purity-report.md) (task `a0bdf588-4bb1-4f75-8950-b069ac7bd154`, PaperQA high-effort, 2026-07-15)
- [digital-alloy-lab-private PR #88 shopping list](https://github.com/vertical-cloud-lab/digital-alloy-lab-private/pull/88)
- [`thermo-calc-100g-mixture-composition.md`](../thermo-calc-100g-mixture-composition.md) — the measured 100 g batch this workflow scales from
