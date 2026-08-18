# Critical review of MAPS (Metal Additive manufacturing using Powder Sheets)

**Context.** Following the Addicoat / IMR outreach idea, this folder holds a set
of deliberately *critical* Edison Scientific (PaperQA3, `LITERATURE_HIGH`)
literature queries that interrogate the scientific underpinnings and commercial
viability of MAPS. MAPS is a powder-bed-fusion variant from Lupoi and
colleagues at Trinity College Dublin (TCD), now being commercialized by
**Addicoat**: metal powder is held in a thin polymer-binder sheet (e.g. ~80 µm
304 SS in polycaprolactone) that replaces loose-powder recoating, and a laser
fuses each sheet while the binder pyrolyzes off below ~500 °C.

- `queries.py` — dispatches and fetches the queries (key read from
  `EDISON_API_KEY`, never echoed); task IDs in `tasks.json`.
- `results/*.md` — full Edison answers with citations.
- `results/*.json` — raw task dumps.

## The five critical questions

| # | Question | File |
|---|----------|------|
| 1 | Is the >99% density / low-defect claim real and reproduced? | `results/01_densification_and_defects.md` |
| 2 | Does binder pyrolysis contaminate the part (C/O/N pickup)? | `results/02_binder_pyrolysis_contamination.md` |
| 3 | Can the sheet format actually *control grain morphology*? | `results/03_grain_morphology_control_claim.md` |
| 4 | Does 316L benchmarking against LPBF hold up? | `results/04_austenitic_steel_benchmark.md` |
| 5 | Is it commercially viable vs LPBF / DED / UAM? | `results/05_commercial_viability_vs_lpbf.md` |

## Bottom line — what science can we actually learn?

The honest verdict from the literature is that MAPS is a **conceptually
interesting, but evidentially thin, single-group technology** whose strongest
claims are largely unverified:

- **Density (Q1).** The headline 99.98% density rests on essentially *one*
  accessible paper (Lupoi et al., *CIRP Annals* 2022) using a tiny ~25 mm³,
  50-layer coupon, measured by micro-CT while the LPBF control was measured by
  Archimedes — a method mismatch and a 40× volume disparity, with no
  statistical replication. **No independent lab** has reproduced it.
- **Inter-sheet defects (Q1).** The most MAPS-specific risk — lack-of-fusion,
  delamination, and "kissing bonds" at sheet-to-sheet interfaces — has **never
  been systematically characterized** in the accessible literature.
- **Binder contamination (Q2).** TGA + EDX suggest the polycaprolactone binder
  fully decomposes, but there is **no quantitative interstitial chemistry
  (C, O, N by combustion / inert-gas fusion)**, no corrosion data, and no
  weldability data. Analogous binder processes (binder jetting, metal FFF)
  routinely leave 0.01–0.6 wt% residual carbon that can embrittle or distort
  parts — so the "no contamination" claim is plausible but unproven per-alloy.
- **Grain-morphology control (Q3).** This claim does **not** hold up: the one
  grain-size difference reported (29.2 vs 48.7 µm) is attributed *by the authors
  themselves* to sample-size/thermal-history differences, not to the feedstock.
  Solidification is governed by the same G, R, G/R physics as LPBF; there is no
  published mechanism by which the sheet format independently selects grain
  morphology. Treat "grain morphology selection" as **marketing overreach**,
  not established science.
- **316L benchmarking (Q4).** The MAPS-316L record rests on a single paper;
  **fatigue, anisotropy, and XCT defect data are absent**, and comparisons are
  against LPBF *literature values* rather than controlled side-by-side builds.

## Bottom line — commercial potential / viability (Q5)

The *genuine* advantages are **process/logistics, not metallurgy**:

- **Real value:** elimination of loose-powder handling/explosion/inhalation
  hazards; very fast material changeover (~10 min vs ~3 h); and genuinely
  simpler **multi-material / functionally-graded** printing by swapping sheets.
- **Likely overstated / unproven:** equivalence of part quality at production
  scale; build rate and sheet-manufacturing cost/yield (an extra coating step
  that consumes binder and solvent); achievable part size (demonstrated only at
  ~1 mm coupon scale, manual placement, no automated machine yet); and the net
  magnitude of the safety benefit once laser pyrolysis fumes are considered.
- **Competitive context:** the powder-handling-safety and multi-material pitch
  overlaps with incumbent sheet/foil routes — ultrasonic additive manufacturing
  (UAM) and laminated object manufacturing — and with wire-DED, which already
  avoid loose powder. MAPS must prove it beats these on cost *and* qualified
  mechanical performance, which the current evidence does not yet do.

**Implication for outreach to Addicoat / IMR.** The most useful, fundable
collaboration is precisely the evidence that is missing above: independent
replication, interstitial-chemistry/corrosion characterization, and statistically
powered fatigue/anisotropy benchmarking on production-scale builds — and, for the
lab's interest, exploiting the one defensible differentiator (multi-material /
functionally graded custom compositions) rather than the unsupported
grain-control narrative.

## Reproducing

```bash
python queries.py dispatch   # create the 5 LITERATURE_HIGH tasks (resumable)
python queries.py fetch      # poll and write results/*.md and results/*.json
```
