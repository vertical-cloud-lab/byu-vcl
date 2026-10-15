# Protocol: one corrosion spot on the CubXL

The per-spot procedure behind the [README](README.md). It is a first proposal: settings marked
*choose* are to be fixed on the reference coupon before any comparison is run, then held. Every
computed number comes from [`corrosion_numbers.py`](corrosion_numbers.py).

## 1. Specimen

Use Ronnie's polishing SOP ([PR #258](https://github.com/vertical-cloud-lab/byu-vcl/blob/157ab1e/SOP/sem-eds-polishing-sop.md))
unchanged up to the cut-out, so one prepared piece serves both SEM/EDS and corrosion.

1. **Section** a piece about 1 cm across (SOP step 1). Where pieces come from is in the
   [README](README.md#3-specimens-we-already-have-or-will-have).
2. **Mount, grind and polish** to the 0.1 µm diamond film (SOP steps 2–8).
3. **Cut it out of the Bakelite** with a bare metal back (SOP step 9). The SOP does this so the
   piece conducts to an SEM stub. It is also the working-electrode contact this cell needs.
4. **Age it the same way every time.** Record when polishing ended, store the piece in the vacuum
   jar (SOP step 11), and test after a fixed time (*choose*: e.g. 24 ± 2 h). The air-formed oxide
   keeps growing after polishing, and on LPBF AlSi10Mg it grows faster than on the cast alloy
   ([Revilla et al. 2022](https://doi.org/10.1016/j.corsci.2022.110352)).
5. **Keep silicone off the face.** Use FKM (Viton) O-rings, not silicone, and no silicone grease.
   The SOP already bans silicone grease because it shows up as Si in EDS, and Si is the element the
   composition spread varies.
6. **Measure the piece's own composition** by EDS on the same face, away from where the wells
   will sit, before any corrosion test. Don't assume the charge composition: remelted metal loses
   some Mg and picks up oxide ([runs so far](https://github.com/vertical-cloud-lab/byu-vcl/blob/cad4e6d/atomizer-runs/plan-adv-mater/runs-so-far.md#earlier-for-context)).
7. **Photograph the face** with the CubXL camera, with the clamp in place, so each well's spot can
   be found again in the SEM.

## 2. Cell

| Part | What | Why |
| --- | --- | --- |
| Clamp | Printed tray. The piece sits face up on a spring contact (pogo pin) that touches its bare back. A lid with 2–4 stepped wells presses one FKM O-ring onto the face per well. | The O-ring sets the area. 2–4 wells per piece means one polish gives several spots. |
| Well | O-ring ID 3 mm (0.071 cm²) or 4 mm (0.126 cm²). Above it a wider bore, 8 mm across, holds about 150 µL (50 µL per mm of height). | A stepped bore keeps the area small and still leaves room for two electrodes and a pipette tip. |
| Reference | A **leak-free** Ag/AgCl mini-electrode, ≤ 2 mm across | See the two notes below |
| Counter | Pt wire, coiled, with several times the sample's exposed area | So the counter never limits the current. PANDA-film coils Pt wire around its reference capillary ([Quinn et al. 2026](https://arxiv.org/abs/2601.07043)) |
| Mount | Reference and counter on the CubXL head beside the pipette, as in PANDA-film. The holder doubles as a lid over the well. | A lid keeps evaporation from concentrating the chloride during a run of up to ~2 h |

**Not an Ag-wire pseudo-reference.** PANDA-film's Ag pseudo-reference is fine for deposition, but in
NaCl an Ag/AgCl wire's potential follows the electrolyte's own chloride, by about 59 mV per decade
(Nernst, 25 °C). A chloride series exists to measure how the pitting potential moves with
chloride, and the reference would move with it.

**Leak-free, because the well is small.** One microlitre of a standard 3 M KCl filling leaking into
150 µL adds 20 mM chloride. That is 3 % on top of 0.6 M NaCl, but it doubles a 0.02 M electrolyte
and quadruples a 0.006 M one ([`corrosion_numbers.json`](corrosion_numbers.json), `kcl_leak`).

Between spots, rinse the reference and counter in a water vial and park the reference in its
storage solution. Before each night, check the reference against a master reference kept for
nothing else (*choose* a limit, e.g. ±5 mV), and log the offset.

## 3. Electrolyte

- **Baseline: 0.6 M NaCl** (3.5 wt%), reagent-grade NaCl in DI water, open to air, at room
  temperature (log it). It is a common corrosion-test concentration and has been used on LPBF
  AlSi10Mg ([Wu et al. 2022](https://doi.org/10.3390/ma15248786)). The other common choice, 0.1 M
  ([Tiwari et al. 2023](https://doi.org/10.3390/coatings13020225)), is inside the series below.
- **Chloride series.** Mix each well's liquid in the well, from three stocks (0.6, 0.06 and
  0.006 M), so no step needs less than 2 µL. That is 8–9 P20 transfers per well.

  | Target, M | From |
  | --- | --- |
  | 0.006 | 150 µL of 0.006 M |
  | 0.01 | 11.1 µL of 0.06 M + 138.9 µL of 0.006 M |
  | 0.02 | 38.9 µL of 0.06 M + 111.1 µL of 0.006 M |
  | 0.06 | 150 µL of 0.06 M |
  | 0.1 | 23.7 µL of 0.6 M + 126.3 µL of 0.006 M |
  | 0.2 | 49.0 µL of 0.6 M + 101.0 µL of 0.006 M |
  | 0.6 | 150 µL of 0.6 M |

- **Check the stocks, not the wells.** A dip probe doesn't fit a 150 µL well, so check each stock
  batch with the conductivity probe from the Porter thread on #213 (or a borrowed meter) against
  NaCl standards, and with the pH probe (#148). Mixing accuracy in the well is a pipette question,
  checked once by weighing.
- Make fresh stocks on a fixed schedule (*choose*), and give every batch an ID.

## 4. Sequence

| # | Step | Settings | Output | Valid if |
| --- | --- | --- | --- | --- |
| 1 | Fill | 150 µL, mixed in the well; image the well | — | no liquid outside the O-ring after 2 min (camera) |
| 2 | OCP | 30 min, ≥ 1 point/s | E_corr (mean of the last 60 s) and its drift | drift over the last 5 min below a limit (*choose*) |
| 3 | LPR (after ASTM G59) | −10 → +10 mV about OCP at 0.167 mV/s (0.6 V/h), 2 min | R_p in Ω·cm², from the slope at zero current | the fit is linear (*choose* an R² limit) |
| 4 | Rest | OCP, 5 min | — | back within 5 mV of E_corr |
| 5 | Cyclic polarization (G61-style) | Start 50 mV below OCP. Sweep up at 0.167 mV/s (G61's 0.6 V/h) or 1 mV/s for screening. Reverse at 1 mA/cm². Stop back at E_corr. | E_pit at 10 and at 100 µA/cm²; E_rp, where the reverse scan falls back below 10 µA/cm²; anodic charge | no attack at the O-ring edge (camera now, SEM later) |
| 6 | Collect | Pipette the liquid plus one 150 µL water rinse into a capped polypropylene tube | tube ID, for ICP | — |
| 7 | Image | Camera image of the spot | — | — |

Notes:

- **"G61-style", not G61.** ASTM G61 is written for iron-, nickel- and cobalt-based alloys. MAP-E
  describes its own test the same way.
- **The reversal is lower than G61's.** G61 reverses at 5 mA/cm². In a 150 µL well, 1 mA/cm² keeps
  the pit and the dissolved Al small: 10 mC of charge dissolves 0.93 µg of Al, 6.2 mg/L in the
  cell.
- **The counter electrode makes OH⁻ while the sample is anodic**: 0.69 mM in 150 µL per 10 mC, if
  nothing neutralised it. The Al³⁺ coming off the sample largely does, but not near the counter, so
  mount the counter high in the well.
- **One spot takes 107 min at the G61 rate, or 44 min at 1 mV/s.** That is 6 or 16 spots in a
  12 h night (assumed ranges: 300 mV up, 400 mV back). Check the 1 mV/s values against the G61
  rate on the reference coupon before screening at 1 mV/s, since E_pit depends on scan rate.
- **Report R_p, not a corrosion rate.** Converting R_p into a current needs Tafel slopes (ASTM G102).
  Assuming them adds a number nobody measured.
- **Threshold definitions** (10 and 100 µA/cm²) make E_pit automatic and repeatable. Report both,
  so a reader can see how much the choice matters.
- **Polypropylene, not glass, for the ICP tubes.** Glass is a silicon source, and Si is one of the
  elements we want.

## 5. Repeatability first

Before comparing materials, run **at least 8 spots over at least 2 nights** on one reference
coupon: the high-purity Al rod from #222, or a slice of the 6063 bar lot used for Block A.

- Report mean, SD and spread of E_corr, log R_p, E_pit and E_rp, as the atomizer plan does for its
  metrics. With n = 8, the 95 % CI on σ is 0.66–2.04× the measured SD
  ([`plan_numbers.json`](https://github.com/vertical-cloud-lab/byu-vcl/blob/cad4e6d/atomizer-runs/plan-adv-mater/plan_numbers.json)).
- Size the comparisons from that SD with the plan's table. Detecting a difference of 2σ takes
  6 spots per material, 3σ takes 4, and 1σ takes 17.
- Pitting potentials scatter by nature. For reference, MAP-E measured E_pit = 392 ± 75 mV over
  32 automated measurements (4 runs × 8 cells, 1 cm² each) on 304 stainless steel
  ([Persaud et al. 2026](https://doi.org/10.1038/s41529-026-00822-8)).
- E_pit also depends on the area tested, so never compare spots from wells of different sizes
  ([Frankel 1998](https://doi.org/10.1149/1.1838615)).

## 6. Safety

- NaCl solutions are low hazard. The later pH series uses dilute HCl and NaOH, and anodizing (if it
  happens) uses sulfuric acid. Each needs its own SOP entry before it goes on the deck.
- No unattended night runs until the potentiostat's firmware has a safety timeout and the cell is
  switched off at the end of every spot. #231 flagged the timeout for the MYSTAT.
- Collected tubes hold NaCl with µg of dissolved metal. Label them and store them for ICP. They are
  not a disposal problem.
