# Design space, master alloys, and the minimum feedstock set (2026-10-07)

Answers the 2026-10-07 question in issue #161: whatever we do with master alloys, can we still
reach every composition in the optimization campaign's search space, and what is the minimum
set of materials (and, for a master alloy, the minimum non-Al weight fraction) that makes the
whole space reachable? Companion files:

- `design_space_reachability.py` — the exact calculation; every number below comes from it
  and re-runs in two seconds after editing the bounds or the feedstock scenarios.
- `design-space-reachability-data.json` — cached output.
- `master_alloy_liquidus.py` / `master-alloy-liquidus-data.json` — CALPHAD liquidus of each
  binary Al–M master versus its solute fraction, for the "can we make it ourselves" side.
- `supplier-links-2026-10.md` — every supplier link by element and form, verified from the
  Pi's residential IP on 2026-10-07.
- `edison-*-2026-10.md` — the two Edison literature reports (Cs/Ce; all-element bounds).

## 0. The element count

The issue lists aluminium plus **15** solutes: Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc, Li,
Er, Zn, Sn. Adding Cs would make 16 non-Al elements. The script takes the element list as an
editable table, so the count does not matter to the method; the tables below use the 15 on
record, and Cs is handled in §6.

## 1. What the search space is, exactly

The campaign varies each solute independently in wt.% with aluminium as the balance. That is
a **box** (one [L, U] interval per solute) cut by **one linear inequality**,
Σ xᵢ ≤ S, where S is the total-solute cap (Al ≥ 100 − S). Aluminium is not a 17th free
variable; it is whatever is left. So the "hypercube with an inequality slicing it" picture in
the question is the right one, and the slice is large:

| Cap S (wt.%) | Al ≥ | Share of the raw box that survives (exact) |
| ---: | ---: | ---: |
| 10 | 90 | 0.006 % |
| 15 | 85 | 0.43 % |
| **20** | **80** | **5.1 %** |
| 25 | 75 | 22 % |
| 30 | 70 | 52 % |

(Volume by inclusion–exclusion over the box corners, `box_slice_volume_fraction`; with the
bounds in §2 the uppers sum to 59.3 wt.%, so most of the raw box is not an aluminium alloy at
all.) **S is a campaign decision that nobody has written down.** Everything below uses
S = 20 wt.% and the sweep in §4 shows how the conclusions move with it.

### The bounds on record

No design space has been ratified. These are the numbers in the repo — the family maxima from
the 20-run purchase model (`purchase_quantity_model.py`) and the erbium analysis
(`erbium-bounds-and-lot-size.md`) — with L = 0 everywhere so every element keeps a true
zero-arm control. §6 says what the Edison literature pass changes.

| Element | L | U (wt.%) | Element | L | U (wt.%) | Element | L | U (wt.%) |
| --- | ---: | ---: | --- | ---: | ---: | --- | ---: | ---: |
| Mn | 0 | 5.0 | Cu | 0 | 4.0 | Sc | 0 | 0.8 |
| Cr | 0 | 2.0 | Ti | 0 | 0.5 | Li | 0 | 2.0 |
| Zr | 0 | 2.0 | Fe | 0 | 1.0 | Er | 0 | 3.0 |
| Mg | 0 | 6.0 | Ni | 0 | 2.0 | Zn | 0 | 8.0 |
| Si | 0 | 12.0 | Ce | 0 | 10.0 | Sn | 0 | 1.0 |

## 2. The exact answer

### 2.1 Mixing is convex, so reachability is a convex-hull question

A crucible charge is a non-negative mixture of feedstocks that sums to 100 g, so the alloy
composition is a convex combination of the feedstock compositions. **The set of alloys a
feedstock set can make is the convex hull of the feedstock composition vectors**, and the
design space is fully accessible iff the design polytope P lies inside that hull. No
brute force is needed: both sets are convex, and the containment reduces to linear programs.

### 2.2 With one source per element the hull has a closed form

Use pure Al plus one source per element, where the source of element *i* carries a non-Al
mass fraction yᵢ (yᵢ = 1 for an elemental powder, 0.02 for Al-2Sc, 0.50 for ESPI's Al-Zr50
pieces). Delivering xᵢ grams of element *i* per gram of batch takes xᵢ/yᵢ grams of its
source, and the sources plus the pure Al must sum to one gram, so the reachable set is

    R(y) = { x ≥ 0 : Σᵢ xᵢ / yᵢ ≤ 1 }.

This is the whole result in one line: **master alloys do not change the shape of the problem.
They add a second half-space with the same form as the compositional cap, but tilted — each
element's wt.% is weighted by 1/yᵢ instead of by 1.** Elemental powders (yᵢ = 1) sit on the
original cap; a 2 % master weights its element 50×.

The space is fully reachable iff

    V(y) := max over x in P of Σᵢ xᵢ / yᵢ  ≤ 1.

V is a linear function maximized over a box with one budget constraint, which the continuous
knapsack greedy solves **exactly**: start every element at its lower bound, hand the leftover
solute budget S − ΣL to elements in decreasing order of 1/yᵢ (least concentrated source
first), each up to its upper bound. The maximizing vertex is the worst recipe you will ever be
asked to weigh, and V is how many grams of sources it needs per 100 g batch. The script
cross-checks V against `scipy.optimize.linprog`; they agree to machine precision.

### 2.3 Three consequences that need no numbers

1. **The minimum number of feedstocks is n + 1** (15 sources + Al = 16; 17 with Cs). P is
   n-dimensional, so a hull that contains it needs at least n + 1 affinely independent points.
   And because 0 is inside every [Lᵢ, Uᵢ], the point "pure Al" is in P, and no mixture of
   solute-bearing feedstocks can have zero solute — so **pure Al must itself be one of the
   feedstocks**. One source per element is enough provided V(y) ≤ 1.
2. **Multi-element masters never reduce the count.** Each element must still vary
   independently, so a ternary Al-Sc-Zr master cannot replace Al-Sc and Al-Zr; it can only be
   an *extra* (n + 2nd) feedstock. It then helps exactly when it is more concentrated than the
   binaries it overlaps (Al-2Sc-10Zr is outside the hull of {Al, Al-2Sc, Al-10Zr}), which is
   the arc-melter route in §5.
3. **The per-element floor is closed-form.** With every other source elemental, element *i*
   needs
   yᵢ ≥ Uᵢ / (1 − Oᵢ), where Oᵢ is the most solute the other elements can carry alongside
   Uᵢ under the cap (= min(S − Uᵢ, Σⱼ≠ᵢ Uⱼ) with zero lower bounds). This is *necessary*; the
   joint condition V(y) ≤ 1 couples the elements, because every master spends batch mass on
   its own aluminium and the worst vertex stacks the least concentrated sources together.

## 3. Numbers for the bounds on record (S = 20 wt.%)

### 3.1 Necessary floor on each source's non-Al fraction (others elemental)

| Element | U | y floor | Element | U | y floor | Element | U | y floor |
| --- | ---: | ---: | --- | ---: | ---: | --- | ---: | ---: |
| Mn | 5.0 | 5.9 % | Cu | 4.0 | 4.8 % | Sc | 0.8 | **1.0 %** |
| Cr | 2.0 | 2.4 % | Ti | 0.5 | 0.6 % | Li | 2.0 | **2.4 %** |
| Zr | 2.0 | **2.4 %** | Fe | 1.0 | 1.2 % | Er | 3.0 | **3.6 %** |
| Mg | 6.0 | 7.0 % | Ni | 2.0 | 2.4 % | Zn | 8.0 | 9.1 % |
| Si | 12.0 | 13.0 % | Ce | 10.0 | **11.1 %** | Sn | 1.0 | 1.2 % |

Every commercial master clears its own floor (Al-2Sc 2 % > 1 %, Al-5Li > 2.4 %, Al-10Zr,
Al-10Er, Al-20Ce > 11.1 %, Al-50Mg). **Individually, none of them is a problem.**

### 3.2 Jointly, the commercial-master plans are not feasible

V = grams of sources needed per 100 g for the worst recipe; feasible iff ≤ 1. "Reachable
share" is the volume fraction of P the scenario can make (Monte Carlo, 2 × 10⁶ draws).

| Scenario | Sources that are masters (y) | V | Reachable share | Worst recipe |
| --- | --- | ---: | ---: | --- |
| A. all elemental | none | **0.20** | 100 % | any; 20 g solute + 80 g Al |
| B. 2026-08 shopping chart | Zr Al-10Zr, Ce Al-20Ce, Sc Al-2Sc, Er Al-10Er, Li Al-10Li | 1.62 | 95.2 % | Sc 0.8 + Li 2 + Zr 2 + Er 3 + Ce 10 (+ Mn 2.2) needs **162 g** of sources |
| C. every reactive element as a commercial master | + Li Al-5Li, Ti Al-10Ti, Mg Al-50Mg | 1.88 | 78.4 % | same corner, 188 g |
| **D. the 2026-09 plan** | Li Al-5Li, Zr Al-10Zr pieces, Ti Al-10Ti pieces; Sc chips, Er powder, Ce pieces, Mg pieces elemental | **0.81** | **100 %** | Li 2 + Zr 2 + Ti 0.5 + Mn 5 + Cr 2 + Mg 6 + Si 2.5 → 80.5 g sources + 19.5 g Al |
| F. plan D but Sc as Al-2Sc | + Sc Al-2Sc | 1.20 | 98.8 % | Sc + Li + Zr + Ti corner needs 120 g |
| G. all masters but Al-10Li | Li Al-10Li, Sc Al-2Sc, Zr Al-10Zr, Ti Al-10Ti, Er Al-10Er, Ce Al-20Ce | 1.67 | 93.7 % | Ce 50 g + Sc 40 g + Er 30 g alone |
| E. recommended set (§5) | Li Al-10Li, Zr Al-Zr50 crushed, Ti Al-10Ti; rest elemental | **0.45** | **100 %** | 44.5 g sources, 55.5 g Al |

Two things to read off this table.

**The reachable-share column is misleading on purpose.** Scenario B still "covers" 95 % of
the design space by volume, but the 5 % it loses is exactly the high-Sc/Li/Zr/Er/Ce corner
that the L1₂-precipitation and Al-Ce families exist to explore. Bayesian optimization walks to
corners; volume fractions describe the interior.

**The plan already agreed on 2026-09-08 reaches the whole space,** with 19.5 g of pure Al to
spare in its worst case, and it stays feasible up to S ≈ 30 wt.% (§4). What it cannot absorb
is swapping scandium back to Al-2Sc (scenario F: with Al-5Li and Al-10Zr also at their
maxima the corner needs 120 g). The contextual minima the script prints for scenario F say
what would fix it: either an Al-Sc master at ≥ 3.9 wt.% Sc, or lithium as Al-10Li (≥ 9.9 %)
instead of Al-5Li. Those are the trade-offs the "minimum non-Al fraction" question was really
asking about: the floors are coupled, and the coupling is through which elements are
*simultaneously* dilute.

### 3.3 Minimum y per master given the rest of the plan (the useful numbers)

For scenario D (what we are ordering), holding the other sources fixed:

| Master | In the plan | Minimum y that keeps the space reachable | Margin |
| --- | --- | ---: | --- |
| Al-Li | Al-5Li (y = 0.05) | **3.4 %** | 1.5× |
| Al-Zr | Al-10Zr pieces (0.10) | **5.1 %** | 2× |
| Al-Ti | Al-10Ti pieces (0.10) | **2.0 %** | 5× |

If, in addition, erbium were taken as Al-10Er and cerium as Al-20Ce (the "safe-handling"
instinct), the plan breaks (scenario G). The Ce master alone is 50 g per batch at the 10 wt.%
upper bound, which is why **cerium must be elemental pieces or a ≥ ~20 % master used only
below ~5 wt.% Ce, and erbium elemental**, unless the Ce ceiling is lowered.

### 3.4 Impurity tolerance as a second floor

Masters cast on 99.7 % aluminium import tramp with every gram of their Al. With a 4N Al
base, 3N solutes and a 2000 ppm tolerance (the Scalmalloy Fe limit, see
`al-ni-purity-and-industry-feedstock-2026-10.md`), the worst recipe delivers:

| Scenario | masters cast on 99.7 % Al | masters cast on 4N Al |
| --- | ---: | ---: |
| A (elemental) | 280 ppm | 280 ppm |
| D (2026-09 plan) | **2,034 ppm** | 280 ppm |
| F | 3,171 ppm | 280 ppm |
| E (recommended) | 991 ppm | 280 ppm |

Impurity-limited floors on y, masters on 99.7 % Al, element alone at its upper bound:
Sc 1.2 %, Li 3.0 %, Zr 3.0 %, Er 4.4 %, Ce 13.8 %, Mg 8.6 %, Ti 0.8 %. They are the same
order as the reachability floors, and plan D sits right at the tolerance because 40 g of
Al-5Li on commercial aluminium is 40 % of the batch. **Ask Belmont what aluminium the
Al-5Li is cast on**; a 4N-base master removes the issue entirely.

## 4. How the answer moves with the total-solute cap

V for each scenario versus S (feasible iff ≤ 1):

| S (wt.%) | A | B | C | D | F | G | E |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 0.10 | 1.21 | 1.44 | 0.70 | 1.09 | 1.29 | 0.34 |
| 15 | 0.15 | 1.46 | 1.68 | 0.76 | 1.16 | 1.49 | 0.39 |
| 20 | 0.20 | 1.62 | 1.88 | 0.81 | 1.20 | 1.67 | 0.45 |
| 25 | 0.25 | 1.67 | 1.98 | 0.85 | 1.23 | 1.73 | 0.50 |
| 30 | 0.30 | 1.72 | 2.03 | 0.91 | 1.26 | 1.77 | 0.55 |

The commercial-master plans fail even at S = 10 because the failure is the *per-element*
mass of the dilute masters, not the cap: Al-2Sc at 0.8 wt.% Sc is 40 g whatever S is. The cap
only decides how many of those 40-gram charges can be demanded at once.

## 5. Master alloys we could make ourselves, and the window for each

The reachability floor says how *concentrated* a master must be; the liquidus says how
concentrated a master we can *melt*. `master_alloy_liquidus.py` sweeps the binary liquidus
with pycalphad (COST507; Dupin 2001 for Ni; ±10 °C from the 20 K grid). The induction module
is rated to 1300 °C, so a master can be melted (and atomized into powder) in-house if its
liquidus is ≲ 1200 °C with 100 °C superheat; above that it is an arc-melter job (#223) and is
dosed as pieces.

| Master | Reachability floor (S = 20, others elemental) | Liquidus vs y (°C) | Highest y we can melt on induction | Commercial y | Crushable? (intermetallic ≳ 50 wt.%) |
| --- | ---: | --- | ---: | --- | --- |
| Al-Zr | 2.4 % | 2 %: 1000 · 5 %: 1140 · 10 %: 1260 · 15 %: 1360 · 50 %: 1620 | **≈ 6 %** | 5, 10 (ESPI pieces), 50 (ESPI pieces) | Al-10Zr no (19 % Al₃Zr); **Al-Zr50 yes** (94 %) |
| Al-Ti | 0.6 % | 2 %: 960 · 5 %: 1100 · 10 %: 1200 · 20 %: 1300 | **≈ 10 %** | 5 (rod), 10 (ESPI pieces) | No (27 % Al₃Ti at 10 %) |
| Al-Ce | 11.1 % | 10 %: 640 · 20 %: 780 · 30 %: 980 · 50 %: 1220 | **≈ 45 %** | 10, 20 | Al-20Ce no (34 %); ≥ 30 % yes |
| Al-Li | 2.4 % | all ≤ 720 (AlLi melts ≈ 700) | any (reactivity, not temperature, limits it) | 2, 5, 8, 10, 20 | No (AlLi is 25 % at 5 % Li) |
| Al-Mg | 7.0 % | all ≤ 660 (eutectic 450 at 35 %) | any | 20–75 | **Al-50Mg yes** (β/γ) |
| Al-Mn | 5.9 % | 10 %: 820 · 20 %: 920 · 50 %: 1120 | ≈ 50 % | 60 (Belmont) | Al-60Mn yes |
| Al-Cr | 2.4 % | 10 %: 940 · 20 %: 1020 · 33 %: ≈ 1150 · 50 %: 1320 | ≈ 40 % | 20 (Belmont), 33 (ESPI) | **Al-Cr33 yes** |
| Al-Fe | 1.2 % | 5 %: 780 · 10 %: 900 · 20 %: 1040 · 50 %: 1180 | ≈ 50 % | — | ≥ 40 % yes |
| Al-Ni | 2.4 % | 10 %: 700 · 20 %: 780 · 30 %: 860 · 50 %: 1380 | ≈ 40 % | 20 (Belmont) | ≥ 40 % yes |
| Al-Si | 13.0 % | 12 %: 577 (eutectic) · 30 %: 840 · 50 %: 1060 | any | 11 (ESPI), 4047 rod | ≥ 50 % yes |
| Al-Cu, Al-Zn, Al-Sn | 4.8 / 9.1 / 1.2 % | all ≤ 660 | any | 10/50, drops, 15 | Al-Cu50 yes |
| Al-Sc *(literature)* | 1.0 % | 0.6 %: 659 (eutectic) · 2 %: ≈ 800 · 36 %: 1320 (Al₃Sc) | ≈ 5–10 % (liquidus ≈ 900–1000, interpolated) | 2 | No below ~25 % |
| Al-Er *(literature)* | 3.6 % | 6 %: 655 (eutectic) · Al₃Er ≈ 1070 at 67 % | ≈ 20–30 % | 5, 10 | ≥ 35 % yes |

(Sc and Er are not in COST507; their rows are from the assessed diagrams — eutectic 0.6 wt.%
Sc / 659 °C and ≈ 800 °C liquidus at 2 wt.% Sc from the US L1₂ alloy patents citing the
Al-Sc diagram; eutectic 6 wt.% Er / 655 °C likewise — and should be treated as ±50 °C.)

What this means for making master-alloy *powder* in-house:

- **Zr is the only element where the reachability floor and the melting ceiling squeeze.**
  The floor is 2.4 % (5.1 % next to Al-5Li), induction tops out near 6 %, and the commercial
  10 % piece needs the arc melter. The clean answer is ESPI's **Al-Zr50 pieces, arc-made,
  brittle, crushed in the glovebox** to 150–300 µm: 4 g per batch at 2 wt.% Zr. Atomizing an
  Al-5Zr powder in-house is possible but buys nothing over crushed Al-Zr50 (and Al-5Zr sits at
  the floor with no margin once Li is a master).
- **Ti**: Al-10Ti pieces are at the induction limit; fine to dissolve, not to re-atomize.
- **Ce, Mn, Cr, Fe, Ni, Si, Cu, Zn, Sn, Mg, Li**: any master concentration we would want is
  inside the induction window, so an in-house **Al-50Mg**, **Al-30Ce** or **Al-Cr33** powder
  is a routine atomizer run, and the high-solute versions are brittle enough to crush instead.
- **Sc and Er**: a ≥ 4 % Al-Sc or ≥ 10 % Al-Er master is meltable, but at 0.8 g and 3 g of
  elemental metal per batch there is nothing to gain over chips and powder in the cup.

### The recommended set (scenario E) — 16 feedstocks, V = 0.45 at S = 20

| Element | Source | y | Why |
| --- | --- | ---: | --- |
| Al | 4N shot/rod machined into the cup | — | required (pure-Al vertex) |
| Li | **Al-10Li** if available (Belmont/KBM/SAM), else Al-5Li | 0.10 / 0.05 | Al-5Li is feasible but leaves the Sc choice constrained (scenario F) |
| Zr | **Al-Zr50 pieces, crushed** (ESPI Knd2756) | 0.50 | 2.4 % floor; arc-made, brittle |
| Ti | Al-10Ti pieces (ESPI Knc6829) or −325 mesh Ti powder | 0.10 / 1 | both clear the 0.6 % floor |
| Sc | **chips** (ESPI Knc6313) | 1 | Al-2Sc only fits if Li is Al-10Li; chips dissolve faster than the pellet |
| Er | powder (Thermo 044169.14) | 1 | Al-10Er is 30 g at the 3 % ceiling |
| Ce | ingot/pieces (Thermo 000065.18, ESPI) | 1 | Al-20Ce is 50 g at the 10 % ceiling |
| Mg | pieces (ESPI) or Al-50Mg crushed | 1 / 0.50 | either clears the 7 % floor |
| Mn Cr Si Cu Fe Ni Zn Sn | elemental powders as quoted | 1 | no floor to meet |

Every composition in the box-with-cap is reachable with this set, the worst recipe uses 44.5 g
of sources, and no master is more than 2× above its floor except where the element is
elemental anyway. Swap any row and re-run the script; it prints the new worst vertex.

## 6. Cs and the literature bounds (Edison)

See `edison-cesium-and-cerium-bounds-2026-10.md` and `edison-design-space-bounds-2026-10.md`
for the raw reports. Summary and consequences are in §6 of this file once the queries return
(both were still running when this file was first written; this section is updated in place).

## 7. What to decide

1. **Ratify the bounds and the cap.** The method is exact; the inputs are placeholders. S = 20
   is a guess; the uppers are family maxima from July. Put the agreed table into
   `DESIGN_SPACE` and `S_TOTAL` and commit it — the optimizer config should import from the
   same place.
2. **Keep Sc, Er and Ce elemental** (chips/powder/pieces into the cup). That single choice is
   what makes the whole space reachable; every all-master variant fails on the same corner.
3. **Buy Al-Zr50 pieces rather than, or alongside, Al-10Zr**, and crush them.
4. **Ask for Al-10Li.** With Al-5Li the plan works (V = 0.81) but loses the option of ever
   using Al-2Sc.
5. **Ask what aluminium each master is cast on** (Fe, Si of the base); plan D sits at the
   2000 ppm tolerance with 99.7 % bases.
