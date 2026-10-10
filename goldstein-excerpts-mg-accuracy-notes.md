# Goldstein Excerpts (Ch. 3, 6, 8) — Notes for Improving Mg wt% Accuracy in AlSi10Mg EDS

**Source:** Excerpts from Goldstein, Newbury, Joy, Lyman, Echlin, Lifshin, Sawyer, Michael,
*Scanning Electron Microscopy and X-Ray Microanalysis*, 3rd ed. — the "72-page EML training reading"
(Ch. 2 end / Ch. 3 electron beam–specimen interactions, Ch. 6 X-ray generation, Ch. 8 Qualitative X-Ray Analysis).
PDF attached to PR #95 (comment from @ronnie-guymon, 2026-07-20).

**Context:** SEM-EDS on the FEI Apreo + EDAX TEAM reads Mg ≈ 1.4–1.6 wt% vs. nominal 0.20–0.45 wt%
in AlSi10Mg (PR #95, PR #93). Prior Edison work identified standardless eZAF Al-tail/background
extrapolation under Mg Kα as the leading root cause. These notes list what the Goldstein excerpts add.

Key energies: Mg Kα 1.254 keV · Mg K edge (E_c) 1.305 keV · Al Kα 1.487 keV · Al K edge 1.559 keV ·
Si Kα 1.740 keV · Si K edge 1.839 keV. Mg–Al Kα separation: 233 eV.

---

## 1. Calibrate the energy scale on pure Mg + pure Zn (§8.2.2.1 #3, §8.2.4, pp. 369, 375)

- Peak positions must be correct to **within 10 eV**; calibration should be re-checked regularly as
  part of a measurement-QA plan.
- §8.2.4 warns that unresolved families used as calibration peaks (e.g., Cu Lα/Lβ) sit ~10 eV off the
  tabulated line energy, propagating a low-energy calibration error. The book's explicit fix:
  **"calibrate the system on a low-energy and a high-energy K peak, for example, pure Mg and pure Zn."**
- For a fit extracting a small Mg Kα shoulder from the Al Kα tail, a 10-eV miscalibration at 1.25 keV
  materially changes the apportionment. TEAM's calibration routine should be run with pure Mg (not Cu L
  or Al alone), and the calibration date/values recorded in session metadata.

## 2. The Mg/Al overlap is in the book's "danger zone" for major/minor pairs (§8.2.4, pp. 374–375)

- General rule: peaks of substantially unequal intensity (>3:1) separated by <50 eV are essentially
  inseparable; always check for overlaps within 100 eV of a peak of interest. For a **minor peak next to
  a major peak, "overlaps may be significant even with 200-eV separation."** Mg (minor, ~0.4 wt%) next to
  Al (major, ~90 wt%) at 233 eV separation with an intensity ratio of order 100:1 sits right at this limit —
  textbook confirmation that the Mg number from a standardless fit is fragile.
- Partially resolved overlaps **shift both peak channels by 10–20 eV** from their true energies.
  Diagnostic: read the fitted Mg Kα centroid in TEAM — if it is pulled above 1.254 keV toward Al,
  the deconvolution is being distorted by the Al peak.

## 3. Manual peak-stripping test — the direct "is Mg really that big?" check (§8.2.5, Fig. 8.19, p. 379)

- The book's maraging-steel example (hidden Co Kα revealed by stripping the Fe K family) is the exact
  analog of our problem: strip the **Al K family scaled to Al Kα** from the spectrum and inspect the
  residual at 1.254 keV against the local background.
- In practice: use TEAM's HPD/deconvolution residual display, or export the MSA and do the fit in
  HyperSpy/eXSpy with Gaussian components (as planned earlier in PR #95). A genuine 1.4-wt%-scale Mg
  peak should leave a large, clean residual; a residual comparable to the background scatter means the
  eZAF fit is inflating Mg from the Al tail.
- Detection criterion for any peak claim (§8.2.2.1 #1): net peak counts **P > 3·√N_B** (N_B = background
  counts under the peak). Worth computing from the saved MSAs for the Mg window.

## 4. Acquisition settings for trace work (§8.2.2.1 #2, Fig. 8.11, pp. 367–369)

- Best energy resolution requires low throughput: classic guidance is input count rate ≲ 2500 cps /
  **dead time < 30%** at the *longest* amp (shaping) time. High dead time broadens peaks and shifts peak
  positions (Fig. 8.11) — worst possible failure mode for a shoulder-fit.
- This reinforces the earlier Edison finding: the polished-sample runs at amp time 0.96 µs (135.5 eV
  resolution) went the wrong direction vs. 1.92 µs (130.4 eV). For Mg quantification: **longest amp time
  TEAM offers, beam current reduced until dead time is modest**, and buy statistics with live time
  (>1M counts total spectrum for minor/trace confidence, §8.2.2.2 #6–7).

## 5. Artifact bookkeeping: Al sum peak at 2.97 keV (§8.2.2.2 #5, Fig. 8.14, pp. 370–371, 382)

- Al Kα + Al Kα coincidence gives a sum peak at 2.97 keV that automatic qualitative analysis famously
  misidentifies as **Ag Lα (2.98 keV) or Ar Kα (2.96 keV)** — the book's own worked example of auto-ID
  failure. If a spurious element enters the element list, standardless normalization redistributes wt%
  across everything, including Mg.
- Checks: (a) inspect our spectra at 2.97 keV; (b) confirm the TEAM element list contains only real
  constituents (Al, Si, Mg, ± C, O, Fe); (c) sum-peak test = re-acquire at substantially lower dead time —
  sum peaks vanish, real peaks stay. (Helpfully, Mg/Al/Si Kα all sit below the Si K edge, so there are
  **no Si-escape peaks** to worry about in this alloy.)
- §8.2.2.1: if TEAM permits excluding candidate lines from auto-ID consideration, that option should be
  defeated at session start (multi-user machine hygiene).

## 6. Beam-energy lever: 15 kV is a very high overvoltage for Mg K (§6.2.14, §8.2.2.1 #4, §6.3.1)

- Optimum overvoltage is U = 2–3; at 15 kV, U for Mg K is ≈ 11.5. The book states that for sub-2-keV
  photons at U > 10, **50–99% of the generated low-energy X-rays are absorbed in the specimen** — so the
  measured Mg (and Al) K intensities are dominated by the ZAF absorption correction, and any error in
  that correction lands directly on the Mg result.
- §8.2.2.1 #4 recommends repeating spectrum accumulation at **5–10 keV** for the low-energy region.
  Concrete experiment: acquire the same polished areas at ~7 kV and ~10 kV (U(Mg) ≈ 5.4 and 7.7;
  Si K still excited at U ≈ 3.8–5.4) and compare eZAF Mg wt% across 7/10/15 kV.
  A strongly kV-dependent Mg result fingerprints absorption/background-model error rather than real Mg.
- Sampling depth shrinks accordingly (Anderson–Hasler, Eq. 6.12): Mg Kα range in Al matrix ≈ 2.2 µm at
  15 kV → ≈ 0.6 µm at 7 kV. Caveat: shallower sampling weights any MgO-enriched powder/oxide surface
  more heavily — on the polished cross-section this is minor, but worth remembering for powder-on-tape.

## 7. Secondary fluorescence: Al Kα is nearly optimal at fluorescing Mg (§6.5.1–6.5.3, pp. 292–295)

- Characteristic fluorescence of B by A is strongest when E_A just exceeds E_c(B). **Al Kα (1.487 keV)
  exceeds the Mg K edge (1.305 keV) by only 0.18 keV — near the maximum-effect condition** — and Si Kα
  (1.740 keV) also fluoresces both Mg and Al. In a matrix that is ~90 wt% Al, a huge Al Kα photon
  population is available to pump Mg K emission.
- The fluorescence source volume is far larger than the electron interaction volume (§6.5.3: radius ~10×,
  volume ~1000×), so this signal is generated over many microns and is insensitive to which
  microstructural feature the beam sits on.
- Implication: the measured Mg K intensity contains a secondary-fluorescence component that the eZAF F
  correction must remove; with a source/analyte concentration ratio of order 200:1, even a modest error
  in F inflates the apparent Mg. This is an *additional* candidate mechanism (beyond the Al-tail/background
  issue) pushing Mg high — and another argument for standards-based or ICP verification rather than
  refining standardless numbers.

## 8. Quantification validity checks (§6.2 Duane–Hunt, §6.3.3 homogeneity)

- **Duane–Hunt limit**: the continuum background must extrapolate to zero at the set beam energy
  (15.0 keV). A lower endpoint means charging / reduced landing energy, which corrupts all overvoltage-
  dependent corrections. Cheap check on every saved spectrum.
- **Homogeneity requirement** (§6.3.3): conventional quantitative analysis assumes the specimen is
  homogeneous over the full sampling volume. At 15 kV the ~2-µm Mg Kα range spans several α-Al cells +
  eutectic Si walls, so each point is a local microstructural average — consistent with the earlier
  finding that point-to-point Mg scatter reflects real (Mg₂Si / cell-boundary) heterogeneity. Report
  means over ≥10 areas, never single points.

## 9. Escalation path the book prescribes for exactly this situation (§8.2.4, §8.3)

- "When a minor element is interfered with by a major-element X-ray peak, it is often very difficult to
  detect [or measure] the minor element" → the stated remedies are advanced spectral processing or
  **WDS**, whose <10 eV resolution and ~10× peak-to-background fully separate Mg Kα from Al Kα and push
  detection to 100 ppm. If the EML (or geology's electron microprobe) has WDS capability, one WDS session
  would settle the Mg question at the microanalysis level; otherwise this is precisely the role the
  Agilent 8900 ICP-MS/MS plan already fills at the bulk level.

---

## Quick action list (TEAM-specific)

1. Recalibrate TEAM energy scale using **pure Mg + pure Zn**; log calibration in session metadata.
2. Acquire Mg-quant spectra at the **longest amp time**, dead time <30% (reduce beam current, extend
   live time; ≥1M counts).
3. Check the fitted **Mg Kα centroid** (should be 1.254 keV, not pulled toward Al) and run the
   **Al-family strip / HPD residual** test; verify P > 3√N_B for Mg.
4. Audit the element list; check for the **2.97-keV Al sum peak**; re-acquire once at low dead time.
5. Run a **kV series (7 / 10 / 15 kV)** on the same areas; kV-dependent Mg wt% ⇒ correction-model error.
6. Verify the **Duane–Hunt endpoint** = 15.0 keV on saved spectra (charging check).
7. Treat any refined standardless number as provisional; WDS or ICP-MS/MS remains the arbiter.

*Not in this excerpt:* Chapter 9 (quantitative analysis — ZAF/φ(ρz) details, standards, detection-limit
formulas). If the full Ch. 9 scan becomes available it would directly cover the eZAF correction models
TEAM uses.
