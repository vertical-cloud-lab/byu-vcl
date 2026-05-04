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

## 1. Recommended system: ferricyanide / ferrocyanide in KCl

| Item | Value |
| --- | --- |
| Redox probe | 1–5 mM K₃[Fe(CN)₆] (potassium ferricyanide) |
| Supporting electrolyte | 0.1 M KCl in DI water |
| Formal potential E°′ | ≈ +0.23 V vs Ag/AgCl (3 M KCl) |
| Expected peak current (3 mm GC, 50 mV/s, 1 mM) | ≈ 10–30 µA |
| Reaction | [Fe(CN)₆]³⁻ + e⁻ ⇌ [Fe(CN)₆]⁴⁻ |

Why this system:

- It is the textbook "hello world" of electrochemistry — a fast,
  reversible, one-electron outer-sphere redox couple used worldwide to
  validate cell geometries, electrode preparation, and potentiostat
  setups. Peak shapes and ΔEₚ tell you immediately if anything is
  wrong (iR drop, reference drift, leaking joints, contamination).
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
   electrochemistry workflow
   ([vertical-cloud-lab #autonomous-electrochemistry](https://github.com/vertical-cloud-lab#autonomous-electrochemistry)),
   which is when concentrated KOH compatibility of Clear v5 becomes
   the open question to answer experimentally.

## 7. Next steps

- [ ] Confirm a potentiostat can be borrowed (and from whom).
- [ ] Confirm availability of a polished GC working electrode, a Pt
      (or graphite) counter, and an Ag/AgCl reference.
- [ ] Order or locate K₃[Fe(CN)₆] and KCl (both are typically already
      stocked in any general chemistry stockroom).
- [ ] Draft a one-page SOP from the template before running the test.
- [ ] Run the procedure in section 3 and post the CV + photos back to
      [issue #27](https://github.com/vertical-cloud-lab/byu-vcl/issues/27).
