# Echem Cell — Initial Low-Hazard, Low-Current Test Plan

This document proposes a first experiment for the newly-printed
3D-printed electrochemical cell (Formlabs Clear v5 resin) from
[AccelerationConsortium/echem-cell](https://github.com/AccelerationConsortium/echem-cell)
once a potentiostat can be borrowed. The goal is **not** to do science
yet — it is to confirm the cell, electrodes, wiring, and software work
together, using a system that is intrinsically safe and produces tiny
currents.

Context for the parts and printing decisions is in
[issue #27](https://github.com/vertical-cloud-lab/byu-vcl/issues/27).
A literature-grounded critical review of this plan (probe chemistry,
safety, sourcing, success criteria) generated with Edison Scientific
is archived at
[`echem-cell-initial-test-artifacts/edison-literature-review.md`](./echem-cell-initial-test-artifacts/edison-literature-review.md);
the corrections it surfaced have been folded back into this doc.

## 1. Recommended system: ferricyanide / ferrocyanide in KCl

| Item | Value |
| --- | --- |
| Redox probe | 1–5 mM K₃[Fe(CN)₆] (potassium ferricyanide) |
| Supporting electrolyte | 0.1 M KCl in DI water |
| Formal potential E°′ | ≈ +0.22 to +0.23 V vs Ag/AgCl (3 M KCl); ~5 mV more positive vs Ag/AgCl (3 M NaCl) |
| Expected peak current (3 mm GC, 50 mV/s) | ≈ 11 µA at 1 mM, ≈ 55 µA at 5 mM (Randles–Ševčík, D ≈ 7.2 × 10⁻⁶ cm² s⁻¹) |
| Reaction | [Fe(CN)₆]³⁻ + e⁻ ⇌ [Fe(CN)₆]⁴⁻ |

Why this system:

- It is the textbook "hello world" of electrochemistry — a fast,
  reversible, one-electron redox couple used worldwide to validate
  cell geometries, electrode preparation, and potentiostat setups.
  Peak shapes and ΔEₚ tell you immediately if anything is wrong
  (iR drop, reference drift, leaking joints, contamination). A 2023
  review ([Cassidy et al., *Electrochem* **4**, 313–349](https://doi.org/10.3390/electrochem4030022))
  argues hexacyanoferrate is better classified as "surface-sensitive"
  rather than strictly outer-sphere — its kinetics depend on surface
  chemistry, adsorbed films, cation identity, and double-layer
  structure. That makes it *more* sensitive to cell condition, which
  is exactly what we want for a shakedown test.
- Currents are in the **µA range**, far below anything that could
  electrolyze the cell wall, heat the resin, or out-gas appreciably.
- Both KCl and the ferri/ferrocyanide salts are low-hazard solids
  (see safety notes below).
- It does **not** put concentrated KOH into the Clear v5 cell. That
  matters because Clear v4.1 (not v5) is the resin with documented
  KOH tolerance — see the discussion in
  [issue #27](https://github.com/vertical-cloud-lab/byu-vcl/issues/27)
  about ordering v5 from Xometry. Saving caustic chemistry for later
  also gives time to evaluate long-term resin compatibility.

## 2. Suggested electrode set

| Role | Electrode | Notes |
| --- | --- | --- |
| Working (WE) | 3 mm glassy carbon disk | Polish with 0.05 µm alumina, rinse, sonicate in DI |
| Counter (CE) | Platinum wire or coil | Large area vs WE; no Pt? graphite rod is fine |
| Reference (RE) | Ag/AgCl (3 M KCl) | If unavailable, a clean Ag wire pseudo-reference is acceptable for a first check |

If we are borrowing a potentiostat from another group, ask whether
they can also lend a polished GC electrode and an Ag/AgCl reference —
those are the two parts most likely to be the limiting factor.

## 3. Procedure (first session, ~1 hour)

1. **Leak / fit check (no electrolyte).** Fill the assembled cell with
   DI water to the working level. Insert the lid, sample holder, cap,
   and epoxy plug. Watch for drips at the lid seal and around each
   port for ~10 minutes. Dry off and inspect for any softening or
   tackiness of the resin near the seals.
2. **Background scan.** Replace DI water with 0.1 M KCl only.
   Record a cyclic voltammogram from −0.2 V to +0.6 V vs Ag/AgCl at
   50 mV/s for 3 cycles. Expect a small, featureless box — this is
   the baseline for the cell + electrodes.
3. **Probe scan.** Spike in K₃[Fe(CN)₆] to ~1 mM. Repeat the same CV
   window and scan rate for 3 cycles. Expect a clearly reversible
   pair of peaks centered near +0.23 V, with ΔEₚ ≈ 60–90 mV and
   |iₚₐ / iₚc| ≈ 1.
4. **Scan-rate study (optional, same session).** Run CVs at 25, 50,
   100, 200 mV/s. Plot iₚ vs √v — a straight line through the
   origin confirms diffusion-limited, well-behaved behavior, which
   indirectly confirms cell geometry and electrode area are sane.
5. **Photo documentation.** Photograph the assembled cell with
   electrodes inserted, and save the CV plots into the issue thread
   for #27.

Total active electrochemistry time: ~30 minutes. Total charge passed
in step 3 (1 mM, ~20 µA peak, few cycles) is on the order of a few
millicoulombs — negligible.

## 4. Safety notes

- **Ferricyanide / ferrocyanide:** low acute toxicity as solids and in
  neutral solution. **Critical rule:** never mix with strong acid or
  heat strongly — under those conditions they can release HCN. We are
  using neutral KCl, so this is not a realistic risk in the planned
  procedure, but it is the one thing to flag in the SOP.
- **UV / sunlight:** hexacyanoferrate(II) slowly photodecomposes under
  UV light, releasing free cyanide. Store stock solutions in amber
  bottles or in a closed drawer, and do not leave waste in clear
  containers on a sunny bench. At mM scale and mL volumes the total
  cyanide inventory is sub-mg, but the rule is cheap to follow.
- **KCl:** non-hazardous, common lab salt.
- **Volumes:** keep total electrolyte volume to the minimum needed to
  cover the working electrode (tens of mL), so that any spill is
  trivial to clean up.
- **PPE:** safety glasses, nitrile gloves, lab coat — same as any
  aqueous bench work in the BYU engineering safety plan.
- **Waste:** ferri/ferrocyanide solutions go into aqueous heavy-metal
  / cyanide-complex waste, **not** down the drain, even though the
  cyanide is tightly bound. Label the bottle.
- A short SOP using
  [`byu-engineering-sop-template.md`](./byu-engineering-sop-template.md)
  should be written before the experiment is run.

## 5. What success looks like

After this first session we should be able to answer:

1. Does the printed cell hold aqueous electrolyte without leaking
   over the timescale of a CV experiment?
2. Do the electrode ports seat the WE/CE/RE at sensible spacing and
   depth?
3. Does the potentiostat + cell + electrodes reproduce the textbook
   ferricyanide CV (E°′ ≈ +0.23 V, ΔEₚ ≈ 60–90 mV, peak symmetry,
   iₚ ∝ √v)?
4. Is there any visible attack on the resin (haze, tackiness,
   discoloration) after ~1 hour of contact with neutral aqueous
   electrolyte?

## 6. Logical follow-on experiments (out of scope here)

Once the ferricyanide check passes, reasonable next steps — still
relatively benign — are, in roughly increasing severity:

1. Ru(NH₃)₆Cl₃ in KCl — another classic outer-sphere probe, useful
   cross-check.
2. Dilute (e.g. 0.1 M) Na₂SO₄ water-splitting onset scan, very low
   current cutoff, to characterize the solvent window.
3. Eventually: the actual target chemistry for the autonomous
   electrochemistry workflow tracked in
   [issue #27](https://github.com/vertical-cloud-lab/byu-vcl/issues/27),
   which is when concentrated KOH compatibility of Clear v5 becomes
   the open question to answer experimentally.

## 7. Shopping list (link-validated)

All product URLs below were checked and resolved to a live product page
at the time this doc was committed. BASi prices are gated behind a
free account (the listed prices are recent typical figures, not live
quotes — confirm at checkout). Fisher prices are the public web price
for the smallest size that comfortably covers this experiment.

### Reagents (Fisher Scientific)

| Item | Vendor / cat. | Size | Approx. price | Link |
| --- | --- | --- | --- | --- |
| Potassium ferricyanide(III), ≥99% (Thermo Scientific) | Fisher AC424125000 | 500 g | ~$70 | [fishersci.com](https://www.fishersci.com/shop/products/potassium-ferricyanide-iii-acros-organics-2/AC424125000) |
| Potassium chloride, crystalline, ACS (Fisher Chemical) | Fisher P217-500 | 500 g | ~$45 | [fishersci.com](https://www.fishersci.com/shop/products/potassium-chloride-crystalline-certified-acs-fisher-chemical-4/p217500) |

A 5 g bottle of ferricyanide (Fisher AC424120050) is plenty for this
experiment if the lab does not want to commit to 500 g — at 5 mM in
20 mL you use ~33 mg/run, so 5–25 g covers hundreds of CVs and keeps
the cyanide-complex waste inventory small. Edison's literature review
also flagged 500 g as overkill for this use case.

### Cheaper alternative: CH Instruments

CH Instruments (Austin, TX, [chinstruments.com](https://www.chinstruments.com/))
is the most common low-cost source for academic CV electrodes and was
the vendor used in the Petrovic (2000) undergraduate ferricyanide-CV
reference cited by Edison. A typical CHI equivalent set (3 mm GC WE,
Pt wire CE, Ag/AgCl 3 M KCl RE, alumina polish) usually totals
roughly **$200–270**, vs ~$595 from BASi for the same three
electrodes — a ~$300+ saving for a first-borrowed-potentiostat test.
Catalog numbers change occasionally, so confirm with a current CHI
quote before ordering; the part families are CHI104 (3 mm GC),
CHI115 (Pt wire), CHI111 (Ag/AgCl 3 M KCl). ALS Co. (Japan, US
distribution via BASi) is a similar mid-price option; Pine Research
is high-quality but typically priced between CHI and BASi.

### Electrodes & polishing (BASi — one-stop, all 3 electrodes)

| Item | Vendor / cat. | Notes | Approx. price | Link |
| --- | --- | --- | --- | --- |
| Glassy carbon working electrode, 3.0 mm dia. | BASi MF-2012 | Standard CV working electrode | ~$220 | [basinc.com](https://www.basinc.com/products/MF-2012) |
| Platinum auxiliary (counter) electrode, 0.5 mm × 7.5 cm | BASi MW-1032 | 99.95% Pt wire | ~$165 | [basinc.com](https://www.basinc.com/products/MW-1032) |
| Ag/AgCl reference electrode (3 M NaCl, RE-5B) | BASi MF-2052 | **Filled with 3 M NaCl, not 3 M KCl** — measured E°′ will sit ~5 mV more negative than the +0.23 V quoted vs Ag/AgCl (3 M KCl); record which reference you used. | ~$165 | [basinc.com](https://www.basinc.com/products/MF-2052) |
| 0.05 µm alumina polishing slurry, 7 mL | BASi CF-1050 | Minimum needed to polish the GC | ~$45 | [basinc.com](https://www.basinc.com/products/CF-1050) |

A more complete polishing setup (recommended if the lab does not
already own polishing pads + glass plate) is the **PK-4 Electrode
Polishing Kit, BASi MF-2060** (~$285,
[basinc.com](https://www.basinc.com/products/MF-2060)) — it bundles
the alumina suspension above with diamond polish, polishing pads, and
the glass plate. Buying the kit is usually cheaper than assembling the
pieces separately and is the right choice if BASi MF-2012 is your
first GC electrode.

### Optional / nice-to-have

| Item | Vendor / cat. | Why | Link |
| --- | --- | --- | --- |
| Polishing glass plate, individual | BASi MF-2128 | Only if not buying the PK-4 kit | [basinc.com](https://www.basinc.com/products/MF-2128) |
| Reference electrode storage vial | BASi MR-5275 | Keeps the Ag/AgCl from drying out between uses | [basinc.com](https://www.basinc.com/products/MR-5275) |
| Replacement CoralPor frit (reference) | BASi MF-2064 | Spare frit for the Ag/AgCl | [basinc.com](https://www.basinc.com/products/MF-2064) |

### Cost summary

| Scenario | What you buy | Approx. total (USD) |
| --- | --- | --- |
| **Bare minimum** (lab already has polishing supplies) | Fisher P217-500 + AC424120050 (5 g ferri) + BASi MF-2012 + MW-1032 + MF-2052 + CF-1050 | **~$525** |
| **Recommended** (first-time setup, full polishing kit) | Fisher P217-500 + AC424125000 + BASi MF-2012 + MW-1032 + MF-2052 + MF-2060 (kit replaces CF-1050) | **~$785** |

These figures exclude shipping and BYU procurement markups. A
borrowed potentiostat is assumed (per the issue thread); a new
benchtop research-grade potentiostat would dwarf this list.

### Notes on substitutions

- **No Pt counter on hand?** A 6 mm graphite rod from any pencil-lead
  or McMaster-Carr equivalent works fine for a ferricyanide CV — the
  counter-electrode reaction is not rate-limiting at these currents.
- **No commercial Ag/AgCl?** A clean Ag wire dipped directly in the
  test solution serves as a pseudo-reference for a first sanity
  check; report potentials vs the reference couple, not vs SHE.
- **Sigma-Aldrich equivalents** (if your group already has a Sigma
  account): potassium ferricyanide ACS is **244023**
  (`https://www.sigmaaldrich.com/US/en/product/sigald/244023`) and
  potassium chloride ACS is **P9333**
  (`https://www.sigmaaldrich.com/US/en/product/sigald/p9333`). These
  Sigma URLs follow the standard product-page pattern but were not
  reachable from the sandbox at commit time, so verify before
  ordering.

## 8. Next steps

- [ ] Confirm a potentiostat can be borrowed (and from whom).
- [ ] Confirm availability of a polished GC working electrode, a Pt
      (or graphite) counter, and an Ag/AgCl reference.
- [ ] Order or locate K₃[Fe(CN)₆] and KCl (both are typically already
      stocked in any general chemistry stockroom).
- [ ] Draft a one-page SOP from the template before running the test.
- [ ] Run the procedure in section 3 and post the CV + photos back to
      [issue #27](https://github.com/vertical-cloud-lab/byu-vcl/issues/27).
