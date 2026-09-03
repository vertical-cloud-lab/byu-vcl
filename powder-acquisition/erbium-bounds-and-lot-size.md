# Erbium: campaign bounds and lot sizing

**Question (issue #161, @sgbaird, 2026-09-03):** *"What are our lower and upper bounds in our
optimization campaign for erbium? Worth it to get all 25 g?"*

Companion script: [`erbium_lot_sizing.py`](erbium_lot_sizing.py) reproduces every number below.

---

## 1. What is actually on record

**No optimization-campaign design space is defined anywhere in this repo.** The only Er number
committed is a *planning placeholder* I wrote in July inside
[`purchase_quantity_model.py`](purchase_quantity_model.py):

```python
("Al-Zr-Er-Sc", 4, {"Zr": 1.5, "Er": 1.0, "Sc": 0.8, "Ti": 0.5}),
```

i.e. **Er ∈ [0, 1.0] wt.%, in 4 of the 20 first-round runs**, and zero in the other 16. That
assumption is what produced the "campaign needs 5.0 g of Er" figure in
[`purchase-quantity-model.md`](purchase-quantity-model.md) §3, which in turn produced the
"strike the $800 ESPI Er line, buy 100 g of Al-10Er instead" recommendation in
[`quote-review-2026-08.md`](quote-review-2026-08.md) §1.2.

**Nobody ever ratified that 1.0 wt.% ceiling.** It was a placeholder chosen to size a purchase,
and the strike recommendation inherits all of its uncertainty. Section 2 below argues the
ceiling should be roughly 3× higher, which changes the purchase decision.

## 2. Where the bounds should sit

### 2.1 Physical anchors

| at.% Er | wt.% Er | Meaning |
| ---: | ---: | --- |
| 0.046 | **0.28** | Maximum **equilibrium** solid solubility of Er in Al (640 °C) — the ceiling for conventional cast-and-age practice |
| 0.4 | **2.33** | **Al-0.4Er-1Zr-1.33Ni** (= Al-2.33Er-3.19Zr-2.73Ni wt.%) — the optimum of a published ML alloy-design campaign, powder made by **ultrasonic atomization** |
| 1.02 | **6.0** | Al–Al₃Er **eutectic** (L → (Al) + Al₃Er, 655 °C); above this, coarse primary Al₃Er forms on solidification |
| 2.0 | **11.2** | Upper edge of the Er variable in that published design box |

Conversion for the binary: **1 at.% Er ≈ 5.9 wt.% Er** (Er is 6.2× heavier than Al, so at.% and
wt.% differ by nearly an order of magnitude — worth stating explicitly in the campaign config,
since most of the Al–Er literature is written in at.% and our shopping chart is in wt.%).

### 2.2 The regime that matters for us

Two distinct regimes exist, and rapid solidification is what separates them:

- **Dilute / equilibrium regime (≤0.28 wt.% Er).** Classic Northwestern-style creep-resistant
  Al-Sc-Zr-Er alloys. Er sits in solid solution after homogenization and precipitates as the
  **Er-rich core** of Al₃(Er,Sc,Zr) L1₂ core/double-shell precipitates — the shells form in
  diffusivity order, D(Er) > D(Sc) > D(Zr), and the slow Zr outer shell is what makes them
  coarsening-resistant to 400 °C. This is the regime where Er is a *partial, cheaper
  substitute for Sc*.
- **Rapid-solidification regime (0.3–6 wt.% Er).** Ultrasonic atomization and LPBF both quench
  fast enough to hold Er far past its equilibrium solubility. The closest published precedent —
  same alloy system, **same rePowder ultrasonic atomizer class** — runs **2.33 wt.% Er**, about
  **8× the equilibrium solubility**, and that composition was the *output* of an ML optimization
  over Er ∈ [0, 2] at.%.

### 2.3 Recommended box

| | wt.% Er | at.% Er | Rationale |
| --- | ---: | ---: | --- |
| **Lower bound** | **0** | 0 | Keep a true zero-Er arm — it is the control that tells you what Er is buying you. (If the doser cannot reliably deliver <0.05 wt.%, treat 0 as a separate categorical arm rather than a tiny continuous value.) |
| **Upper bound** | **3.0** | 0.51 | ~30% headroom above the published 2.33 wt.% optimum, so that optimum is **interior** to the box. Still below the 6 wt.% eutectic, so no primary Al₃Er. |
| *(optional stretch)* | 6.0 | 1.02 | Only if eutectic Al–Er networks are deliberately of interest; costs Er fast (see §3). |

The design-space rule that matters here: **if the literature optimum sits on or outside your
boundary, Bayesian optimization will just pin the variable to the boundary and you learn
nothing about the interior.** A 1.0 wt.% ceiling puts the known good composition *outside* the
box entirely.

Note that the Er range spans more than a decade of interesting physics (0.05 → 3 wt.%), so
log-spaced or two-stage sampling will resolve the dilute L1₂ regime better than a uniform
linear grid.

## 3. Budget arithmetic

Per 100 g batch, **1 wt.% Er = 1.0 g of Er**, so the sums are simple. Both tables carry the
same 1.25× contingency used in the purchase-quantity model. "Worst case" = every Er-bearing run
sits at the ceiling; "BO-mean" = Er sampled uniformly over [0, ceiling], mean = ceiling/2, which
is what an actual space-filling initial design consumes.

### 3.1 Forward — grams to buy

| Ceiling (wt.%) | 4 Er-runs | 8 Er-runs | 20 Er-runs |
| ---: | ---: | ---: | ---: |
| 0.50 | 2.5 / 1.2 g | 5.0 / 2.5 g | 12.5 / 6.2 g |
| 1.00 *(current placeholder)* | 5.0 / 2.5 g | 10.0 / 5.0 g | 25.0 / 12.5 g |
| 2.33 *(published optimum)* | 11.7 / 5.8 g | 23.3 / 11.7 g | 58.2 / 29.1 g |
| **3.00 *(recommended)*** | **15.0 / 7.5 g** | **30.0 / 15.0 g** | 75.0 / 37.5 g |
| 6.00 *(eutectic)* | 30.0 / 15.0 g | 60.0 / 30.0 g | 150.0 / 75.0 g |

*(worst case / BO-mean)*

### 3.2 Inverse — the ceiling a lot size buys you

This is the direction that matters at purchase time.

| Lot | 4 Er-runs | 8 Er-runs | 20 Er-runs |
| ---: | ---: | ---: | ---: |
| **5 g** (Thermo 044169.06) | 1.00 / 2.00 wt.% | 0.50 / 1.00 wt.% | 0.20 / 0.40 wt.% |
| 10 g | 2.00 / 4.00 wt.% | 1.00 / 2.00 wt.% | 0.40 / 0.80 wt.% |
| **25 g** (ESPI or Thermo 044169.14) | 5.00 / 10.00 wt.% | **2.50 / 5.00 wt.%** | 1.00 / 2.00 wt.% |

*(worst case / BO-mean ceiling, wt.%)*

**Read the 5 g row first.** A 5 g lot caps the campaign at ~1 wt.% Er over four runs — i.e. it
reproduces the placeholder bound and makes the published 2.33 wt.% optimum **unreachable**.
A 25 g lot supports a 2.5–3 wt.% ceiling across 8–10 Er-bearing runs, which brackets it.

## 4. Lot options and price sanity check

| Source | Spec | Lot | Price | $/g | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| ESPI Metals | Er powder, −40 mesh, 3N | 25 g | $800.00 | $32.00 | Quoted 2026-08; **3–5 week lead**; +$45 hazardous handling on the ESPI order |
| **Thermo/Alfa `044169.14`** | Er powder, −40 mesh, **99.9% (REO)**, packaged under argon | 25 g | **$770.65** (list $906) | **$30.83** | Verified on thermofisher.com 2026-09-03, available now; rides the Fisher PO already going out |
| Thermo/Alfa `044169.06` | same, 5 g | 5 g | $218.65 (list $243) | $43.73 | **25 g is not a minimum** — but the small lot costs 42% more per gram |

**$30–32/g is the real market rate for 3N Er powder in lab lots**, not an ESPI markup — two
independent houses land within 4% of each other. For scale, ESPI's elemental Sc is **$235/g**,
**7.3× more per gram**; at typical additions that is ~$46/run of Er versus ~$94/run of Sc.

⚠️ **Purity-basis caveat.** Alfa's "99.9% **(REO)**" means *rare-earth-oxide basis* — purity
measured against other rare earths only ("Total Rare Earth Oxide Impurities 0.1% max"). It says
nothing about Fe, Ta, or, critically, **oxygen**. ESPI's "3N" is normally a metals-basis figure.
These are not the same claim; ask both houses for a CoA reporting **O, Fe, Si** before choosing
on price. Oxygen is the impurity that actually threatens Al₃(Er,Zr) L1₂ nucleation.

## 5. Why elemental Er, not only the Al-10Er master

[`quote-review-2026-08.md`](quote-review-2026-08.md) §1.2 recommended replacing the elemental Er
line with 100 g of Al-10Er. Master alloys are still the right call at the *bottom* of the range
(dosing 0.1 wt.% Er means weighing 100 mg of elemental powder versus 1.0 g of Al-10Er — 10× the
mass for the same solute, so 10× better dose resolution). But dilute masters run into a hard
mass ceiling at the *top* of the range, because every gram of master is also a gram of the 100 g
batch:

| Target | Via | Master per 100 g batch |
| --- | --- | ---: |
| Zr 3.19 wt.% | Al-10Zr | 31.9 g |
| Er 2.33 wt.% | Al-10Er | 23.3 g |
| Sc 0.80 wt.% | Al-2Sc | **40.0 g** |
| | **total** | **95.2 g of a 100 g charge (95%)** |

At the published composition, an all-master recipe consumes **95% of the batch mass** before any
elemental Al, Ni, or Mn is added — the high-solute corner of the design space is essentially
unreachable. (Al-2Sc is the worst offender at 50 g of master per wt.% of Sc.) So the right
answer is **both forms, used at different ends of the range**: masters for the dilute runs,
elemental powder for the concentrated ones. That reverses the earlier "strike the elemental Er
line" call.

## 6. Verdict

**Yes — buy the 25 g, and treat it as the thing that sets the Er ceiling at 3 wt.%.**

1. It is the only lot size that lets the campaign bracket the one published, ultrasonically
   atomized Al-Zr-Er-Ni optimum (2.33 wt.%). The 5 g lot silently truncates the box to ~1 wt.%.
2. $771–800 is inside the ~$1k-per-rare-earth cap, and Er is the *affordable* rare earth here:
   the same $1k buys ~25 g of Er but only ~4 g of Sc. Under a rare-earth budget cap, **Er should
   be the primary L1₂-former lever in round one and Sc the rationed one** — which is exactly the
   substitution the Al-Sc-Zr-Er literature was built on.
3. Unused Er is not wasted. Er metal in a sealed can under Ar keeps indefinitely; the only cost
   of over-buying is tied-up capital, and at the recommended bounds round one consumes 15–30 g.
4. **Schedule risk argues for now, not later.** China's export-licence controls on Er are
   *suspended, not withdrawn*, and the suspension lapses **2026-11-10**. Both quoted lots are
   US-warehoused; the Thermo lot ships immediately, the ESPI lot has a 3–5 week lead that runs
   into that window.

**Buy from Thermo (`044169.14`, $770.65, in stock, packaged under argon) rather than ESPI**,
unless ESPI's CoA comes back with a better oxygen number — it is $29 cheaper, ships now instead
of in 3–5 weeks, avoids adding to ESPI's $45 hazardous-handling line, and consolidates onto a PO
that is already being placed.

**Keep the Al-10Er master quote alive anyway** (Kymera / Belmont / KBM) for the dilute end of
the range — but it is no longer the *substitute* for the elemental line, it is the complement.

### Open questions for the team

- **Ratify the box.** Er ∈ [0, 3] wt.% is a recommendation, not a decision. It needs @sgbaird's
  and @gage-erickson's sign-off, and it should be written down somewhere the optimizer config
  can point at — the same is true for all 15 solutes.
- **How many of the 20 runs carry Er?** Everything in §3 scales linearly with that number. The
  current model says 4; the tables assume 4–8 is the realistic range.
- **Handling:** −40 mesh Er has no bottom screen (0–425 µm), so it contains fines. Rare-earth
  metal fines are combustible; keep the can sealed and dose in the glovebox.

## Sources

- Ge, Wei, Taheri-Mousavi et al., *High-strength additively manufacturable Al-Zr-Er-Ni alloys
  with high as-built ductility and thermal stability*, npj Advanced Manufacturing (2025) —
  https://www.nature.com/articles/s44334-025-00048-7 ; open-access companion in
  Advanced Materials, https://pmc.ncbi.nlm.nih.gov/articles/PMC12810664/ (composition
  Al-0.4Er-1Zr-1.33Ni at.% = Al-2.33Er-3.19Zr-2.73Ni wt.%; ML design box
  {Er, Zr} = [0, 2] at.%, {Y, Yb} = [0, 1] at.%, Ni = [0, 4] at.%)
- van Dalen, Dunand, Seidman, *Erbium and ytterbium solubilities and diffusivities in aluminum*,
  Acta Materialia (2009) — https://www.sciencedirect.com/science/article/abs/pii/S1359645409003012
  (max Er solid solubility 0.046 at.% at 640 °C)
- *Evolution of nanoscale precipitates in Al microalloyed with Sc, Er and Zr*, Acta Materialia
  (2009) — https://www.sciencedirect.com/science/article/abs/pii/S1359645409002584 (Er-core /
  Sc-shell / Zr-outer-shell L1₂ structure; D(Er) > D(Sc) > D(Zr))
- Al–Er eutectic ~6 wt.% Er at 655 °C, L1₂ Al₃Er — as summarized in US Patent 7,811,395,
  https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7811395
- Thermo Scientific Chemicals (Alfa Aesar) Er powder −40 mesh 99.9% (REO):
  [25 g `044169.14`](https://www.thermofisher.com/order/catalog/product/044169.14) ·
  [5 g `044169.06`](https://www.thermofisher.com/order/catalog/product/044169.06) — prices
  fetched 2026-09-03
- China rare-earth export controls, Er suspension to 2026-11-10 —
  https://www.cirs-group.com/en/chemicals/china-temporarily-suspends-export-controls-on-key-raw-materials-including-rare-earths-lithium-batteries-and-diamond
  · https://www.mining-technology.com/news/china-rare-earth-export-pause-nears-expiry-amid-persistent-supply-concentration/
