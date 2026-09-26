# AlSi10Mg EDS cross-comparison — Edison results & integrated analysis

Response to https://github.com/vertical-cloud-lab/byu-vcl/pull/93#issuecomment-4523029351.

Six Edison tasks were submitted (1 ANALYSIS with file upload + 5 LITERATURE_HIGH parallel searches) on 2026-05-22 against three SEM-EDS measurement sets on the same nominal AlSi10Mg LPBF feedstock. All six tasks completed successfully; the ANALYSIS task required re-submission with the data bundle uploaded as a single collection (per the [Edison file-management docs](https://docs.edisonscientific.com/edison-client/file-management)) rather than as separate files.

Full per-query answers (workbook-style, with citations and tables) are saved in `eds-cross-comparison-edison-queries.md` task IDs. The verbatim answers ran ~7 k to ~25 k characters each; this document captures the integrated bottom line.

## TL;DR

| Topic | Verdict |
|---|---|
| **Are we on the right track?** | **Partial.** Si recovery (9.1–9.4 wt%) ✅ and elimination of O after polish ✅ are both genuine improvements. **Mg = 1.4–1.6 wt% is mostly an analytical artifact**, not real Mg enrichment. |
| **Best-guess true Mg** | **~0.7–1.0 wt%** (Edison Analysis crow re-fit of the raw MSA spectrum). Still above the 0.20–0.45 wt% spec but ~2× lower than what TEAM reports. The remaining gap is a mix of standardless k-factor bias for low-Z lines (~10–20%) and possibly a small real surface enrichment. |
| **Dominant root cause** | **Two compounding effects:** (1) TEAM's eZAF Smart Quant under-models the low-energy "incomplete-charge" tail of the large Al Kα peak and dumps the residual into the Mg Kα window; (2) the EDAX `BackgroundRegions` (2.14–2.42, 2.865–3.145, 4.865–5.145, 6.865–7.145, 10.865–11.145 keV) contain **no anchors below 2 keV**, so the bremsstrahlung under Mg Kα is being blindly extrapolated from above the Si peak. |
| **Microstructural contribution to Mg** | **Real but secondary.** STEM-EDX consistently measures ~1.7 wt% Mg in the intercellular eutectic Si network vs. ~0.5 wt% retained in α-Al cells (Cauwenbergh 2021). With a ~2 µm interaction volume at 15 kV, an SEM-EDS spot inevitably averages both, biasing high vs. ICP-OES bulk. SEM-EDS has been documented to overestimate Mg by 3–14× on AM AlSi10Mg surfaces depending on kV and surface state (Lynch 2019; Ho 2022). |
| **"Small spheres" on polish** | Most likely **colloidal-silica polishing residue** (sub-µm SiO₂ agglomerates from the 0.05 µm OPS final-polish step), not Mg-rich nodules. The Area 6/7 quant shows 0% O, which rules out gross MgO/MgAl₂O₄ surface scale but does **not** rule out a thin Si–O residue layer. **Spot-EDX on a sphere** (look for Si + O with little/no Al/Mg) and a vibratory-polish + DI/ethanol/plasma re-clean will diagnose. |
| **Missing fishscale in SEM** | Expected. Unetched, mirror-polished AlSi10Mg has minimal SE topographic contrast and insufficient Z-contrast in BSE. **Light Keller's-reagent etch (~60 s)** reveals the melt-pool fishscale and the cellular Si network. |

## Source tasks

Full task IDs (all status = success):
- `eb5e59c7-96c8-4c34-864f-8842d5c774d4` — ANALYSIS (first retry, fail-fast due to oversized bundle uploaded as separate files)
- `53f221ff-1bcb-4feb-a48b-e3d3c9cc6b95` — **ANALYSIS** (succeeded; bundle re-uploaded as a single zipped collection via `client.store_file_content(as_collection=True)`)
- `1c63284b-2f0a-415c-b51f-8c53fe6a4332` — LITERATURE_HIGH: eZAF / standardless Mg bias
- `21ba848f-8c6c-4db1-9830-35062b1d11a2` — LITERATURE_HIGH: where Mg resides in LPBF AlSi10Mg
- `afe8c121-9f8e-4444-abd2-31aa5c42c74e` — LITERATURE_HIGH: amp-time / SDD resolution & Mg-Al deconvolution
- `53ed54dd-a61c-4074-8858-6c0da3e0d7c9` — LITERATURE_HIGH: "small spheres" on polished cross-sections; fishscale invisibility
- `705df51f-975c-48fa-8387-3a7e07389f47` — LITERATURE_HIGH: concrete EDS SOP per ASTM E1508 / E1078

Slim data bundle uploaded for analysis (raw MSA/CSV/XML + README with all eZAF numbers extracted from the three PDFs, no PDFs): `data_entry:0bddb41a-235a-4b1c-ad37-b60d24f22163`. The original full bundle (with PDFs) is `data_entry:23c00fbb-a03b-42e3-bcac-d924e5db41cf`.

## 1. ANALYSIS crow — re-fit of the raw MSA spectrum

The Edison Analysis agent re-processed `EDS_NonFlat.msa` (non-flat sample, 460.8 s sum spectrum) directly. Constraining peak widths with the standard Fiori–Newbury relation (Fano = 0.12, noise FWHM 47 eV) and including a bounded Hypermet low-energy tail on Al Kα plus the Al Kβ line at 1.557 keV, the corrected net Mg Kα counts came out as follows:

| Fit | Net Mg Kα counts | Notes |
|---|---:|---|
| TEAM eZAF Smart Quant (reported in PDF, scaled to live time) | ~65,148 | Baseline — what we are getting today |
| Simple 3-Gaussian (Mg, Al, Si) + linear background | 38,328 | Even a naive fit halves the apparent Mg |
| Physically constrained (Al Kβ + bounded Hypermet tail) | **31,641** | ~2.06× lower than TEAM |
| Unbounded Al low-energy tail | 26,948 | ~2.4× lower than TEAM |

Linearly back-scaling 1.64 wt% by 31,641/65,148 gives a **corrected Mg ≈ 0.80 wt%**. The Analysis agent also flagged a small but visible Al+Al sum peak at 2.97 keV (~0.06 % of Al Kα) — evidence the input count rate is brushing pile-up territory for the chosen amp time.

The Analysis agent also pointed out a discrepancy worth resolving: the **non-flat MSA header records amp time = 3.84 µs**, while the **TEAM PDF table reports 1.92 µs**. One of those is wrong; please confirm with Gage which was actually used.

## 2. Why TEAM standardless eZAF inflates trace Mg in an Al matrix

Synthesis of `LIT_eZAF_Mg_bias` (Newbury & Ritchie 2013/2015/2024, Goldstein et al. 2018, Pinard 2020):

- **Standardless commercial routines have ~±25–30 % relative error for 95 % of analyses** — that alone explains ±0.1 wt% at 0.3 wt% Mg, but cannot explain a 3–7× overestimate.
- **A ~5× overestimate requires compounding error sources.** Five mechanisms add together for the Mg-in-Al case:
  1. Mg Kα (1.253) and Al Kα (1.486) are 233 eV apart vs. ~83–94 eV FWHM at this energy → the Mg peak sits on the dominant Al low-energy tail. Any error in the Al peak-shape/tail model assigns Al counts to Mg. At 0.3 wt% Mg vs. ~89 wt% Al, the Mg:Al peak ratio is ~1:300, so the fit is extremely sensitive to tail modeling.
  2. Mg Kα is strongly absorbed in Al (μ/ρ ≈ 4000 cm²/g); the absorption correction in φ(ρz)/ZAF is the largest matrix correction and propagates strongly from any error in MAC tables, take-off angle, or assumed depth.
  3. Standardless routines normalize to 100 %. Any missing constituent (e.g., undetected oxide) gets redistributed onto the remaining elements, amplifying minor-element error.
  4. Background under Mg Kα is **not** measured directly; with the EDAX `BackgroundRegions` set used here, the lowest anchor is 2.14 keV — well above the Mg/Al peaks. Bremsstrahlung shape at <2 keV is steep and is being extrapolated, not fit.
  5. Low-energy detector-window efficiency error biases the Mg k-ratio more than Al/Si.
- **The fix in the literature is unambiguous:** use a measured Mg standard (or MgO; NIST SRM 470 / K412 glass is the standard suggestion because it contains Mg+Al+Si in one homogeneous reference) and switch to a proper standards-based k-ratio fit — ideally NIST DTSA-II MLLS, which routinely achieves >98 % within ±5 % relative even on this overlap. WDS gets you ±2 %.

## 3. Where Mg actually lives in LPBF AlSi10Mg — and why even a perfect EDS quant will read > nominal

Synthesis of `LIT_Mg_segregation` (Cauwenbergh 2021, Qin 2020, Giovagnoli 2021, Raza 2021, Lynch 2019, Brice 2018):

- Mg has a low partition coefficient in Al (k₀ ≈ 0.195) and is **strongly rejected to the last liquid to solidify**. STEM-EDX maps directly show ~1.7 wt% Mg in the intercellular eutectic Si network vs. ~0.5 wt% retained in α-Al cells (Cauwenbergh 2021).
- Mg₂Si is **latent** in the as-built state — APT shows nanoscale Mg+Si clusters that act as nuclei for Mg₂Si precipitation only on subsequent reheating (DSC exotherm near 317 °C; Giovagnoli 2021).
- **MgAl₂O₄ spinel** forms preferentially over Al₂O₃ on AlSi10Mg powder/spatter surfaces (Raza 2021: virgin oxide ~4 nm thick growing to ~38 nm after 30 months of reuse; spatter shells 50–125 nm). On the as-built non-flat surface, the 8 wt% O we measured is dominated by Al₂O₃/MgAl₂O₄.
- **Mg evaporation losses in LPBF AlSi10Mg appear modest** under inert-gas shielding (XRF on AlSi7Mg0.6 finds no significant Mg loss). Unlike EB deposition in vacuum (30–80 % Mg loss reported), the ~750 mbar Ar atmosphere provides ~1000× evaporation suppression. So Mg loss is unlikely to drive the powder-to-print compositional offset.
- **Published cross-validation data:** Lynch (2019) measured Mg = 4.35 wt% at 5 kV and 1.01 wt% at 20 kV on the same AM AlSi10Mg surface (true bulk ~0.3–0.5 wt%) — i.e. SEM-EDS routinely overestimates Mg by **2–14×** on AM AlSi10Mg, primarily driven by surface oxide, microstructural sampling of the eutectic network, and standardless deconvolution error.

**Implication for our 1.4–1.6 wt% reading:** even with a perfect re-fit, true bulk Mg measured by SEM-EDS on a polished LPBF cross-section should be expected to read above ICP-OES bulk because the ~2 µm interaction volume preferentially samples the Mg-enriched intercellular network. The Edison Analysis agent's corrected ~0.8 wt% is consistent with this — and ICP-OES is the only way to know the true bulk to high precision.

## 4. Amp-time / resolution trade-off — does 1.92 → 0.96 µs matter for Mg?

Synthesis of `LIT_amp_time` (Goldstein 2018, Newbury & Ritchie 2014/2016, Nylese 2017):

- 233 eV separation vs. 82.8 eV FWHM at Mg Kα (130.4 eV res) → separation/FWHM = **2.81**. At 135.5 eV res, this drops to **2.57**. Both are comfortably resolvable by MLLS fitting (which Newbury has demonstrated separating peaks at 13 eV and even 3 eV separations).
- **So the 1.92 → 0.96 µs change is a ~9 % broadening, not a qualitative break.** The Edison literature task and the Analysis crow agree: amp time is a *contributing* factor (compounded with tail modeling), not the primary cause of the 3–7× Mg overestimate.
- However, **for trace Mg on a dominant Al peak, longer shaping = less tail = more reliable deconvolution**. Use the longest amp time consistent with maintaining ≤30 % dead time at your chosen beam current. Goldstein recommends 130–135 eV (Mn Kα) as an "excellent" practical setting; Newbury's standard SOP runs at ~470 ns (127.5 eV). Mike Standing's training session used 7.68 µs which is fine, just lower-throughput.

## 5. "Small spheres" and missing fishscale pattern

Synthesis of `LIT_spheres` (Rémond 2002, Vander Voort 2006/2011/2013, Qin 2020, Mueller 2017, Zejli 2026):

- **Most likely culprit: colloidal-silica polishing residue.** Sub-100 nm SiO₂ primary particles from the 0.05 µm OPS final-polish step agglomerate and crystallize on insufficiently-rinsed Al surfaces and appear as nanosphere clusters at 10 000–50 000×. Diagnostic: EDX point spectra on a sphere should show **Si + O with little/no Al/Mg**. The 0 wt% O in the Area 6/7 quant is a sum spectrum over a larger field; a point spectrum on a sphere would still light up O.
- **Other candidates to rule out:** pulled-out eutectic Si particles (Mueller 2017 — Al-Si alloys are prone to this); embedded SiC/diamond/alumina abrasives; chamber-environmental silica; spatter/PMP (these would be much larger, 1–40 µm); Mg₂Si or Al-Fe-Si intermetallics (real but tens of nm, not spheres covering the surface).
- **Fixes:** longer DI water + ethanol rinse, ≥20 min vibratory final polish on colloidal silica (Vander Voort 2011 reports >10 % EBSD band-contrast improvement), plasma clean before SEM, or a brief re-polish.
- **Why no fishscale:** unetched mirror-polished AlSi10Mg gives minimal SE topographic contrast (flat by design) and insufficient BSE Z-contrast (melt-pool boundary is a fine-to-coarse cellular morphology change of the same Al-Si composition, not a Z change). Optical microscopy is more sensitive to subtle reflectivity changes; SEM is not. **Light Keller's reagent etch (~60 s)** is the standard fix. 40 s is under-etched, 80 s pits.

## 6. Concrete recommendations for the next polished-sample run (with Mike Standing spot-checking)

Synthesizing `LIT_SOP` (ASTM E1508-12a(R19), Goldstein 2018, Newbury 2014/2015), the ANALYSIS crow output, and Mike Standing's prior training defaults:

| Parameter | Recommendation | Reasoning |
|---|---|---|
| **Beam energy** | **15 kV** (consider 10 kV repeat) | Overvoltage > 2 for Mg/Al/Si K; 10 kV cross-check reduces interaction volume and absorption-correction burden for Mg Kα. |
| **Beam current / spot size** | Tune empirically on a high-flux Al standard to hit **target dead time** | Don't guess; ASTM E1508 wants 20–30 %; Newbury & Ritchie recommend ~10 % for trace work to suppress sum peaks. |
| **Dead time target** | **10–20 %** (for trace Mg work; ≤30 % per ASTM E1508) | We saw a small Al+Al sum peak at 2.97 keV → was running too hot. |
| **Live time** | **≥200 s per point**, replicate ≥3 points per sample | Counting-statistics formula CDL = 3·√Nₘ/(Nₛ−Nₘ)·Cₛ wants high total counts to push the Mg detection limit below 0.1 wt%. |
| **Amp time** | **3.84 µs or 7.68 µs** | Mike Standing used 7.68 µs in training. **Do NOT use 0.96 µs.** Trace-on-major requires the narrowest peaks you can afford. |
| **Working distance** | **10 mm** (or whatever is the Apreo analytical WD) | Match the take-off angle assumed in the software; absorption correction for Mg is very sensitive to TOA. |
| **Take-off angle** | **35° or higher**, kept fixed across all spectra | Higher TOA = shorter absorption path; the 48.7° → 35° change between sessions is OK if standards and unknowns are at the same geometry. |
| **Magnification** | **500–1 000×** for bulk composition; spot for phase ID | Averages over multiple α-Al cells + Si network. |
| **Standards** | **Use standards.** Acquire MgO and pure Al (or NIST K412 glass which contains Mg+Al+Si) in the **same session, same kV, same TOA, same amp time** | Eliminates the unknown systematic offset in EDAX's remote-standards database for Mg. This is the single biggest accuracy improvement available. |
| **Spectrum analysis** | **Re-process raw MSAs in NIST DTSA-II or HyperSpy** with measured standards | DTSA-II MLLS handles the Mg/Al overlap robustly; >98 % within ±5 % relative is documented. Don't rely on TEAM Smart Quant for the report numbers. |
| **Background regions** | If staying in TEAM, **add a low-energy background anchor between Mg Kα and the noise floor** (e.g., ~0.7–0.9 keV); confirm with EDAX what's editable | Current `BackgroundRegions` start at 2.14 keV; bremsstrahlung under Mg/Al is being extrapolated. |
| **Sample prep** | Grind 320/600/1200/2400 SiC → diamond 6/3/1 µm → 0.05 µm OPS → **≥20 min vibratory final polish** → ultrasonic + DI water + ethanol rinse + immediate dry → plasma clean → optional ~10 nm carbon coat | Vander Voort 2011 method; minimizes colloidal-silica residue and Al smearing. |
| **Etching for microstructure imaging** | **Keller's reagent (2 mL HF + 3 mL HCl + 5 mL HNO₃ + 190 mL H₂O), ~60 s immersion** | Will reveal melt-pool fishscale and cellular Si network in SEM. (Etched sample is NOT used for quantitative EDS though — do EDS first, then etch.) |
| **# of areas / replicates** | ≥ 3 polished areas per sample, ≥ 3 point spectra per area (or large-area rasters), report mean ± std | Mg is heterogeneous (eutectic vs. matrix) — bulk composition needs averaging. |
| **Cross-validation** | **ICP-OES on a piece of the powder feedstock and a sample of the print** | Reasonable expectation: ±3–5 % relative at 0.2–0.45 wt% Mg. SEM-EDS alone cannot release the alloy chemistry. |
| **WDS option** | Only if the highest accuracy on Mg is required for the Genesis proposal narrative | WDS gives ~10 eV resolution, eliminates the overlap, ±2 % relative. BYU EML may or may not have WDS-capable EPMA; check. |

## 7. Clarifying questions for the team

Before we draw firmer conclusions in the proposal narrative, it would help to confirm:

1. **Amp time discrepancy on the non-flat run.** The MSA header (`SPCTRMAPID = AlSi10Mg_3d_1`) lists `TBEWIND = 3.84 µs`, but the TEAM PDF report lists 1.92 µs. Which was actually used? (This affects how we interpret the resolution and any future re-fit.)
2. **Dead time during each session.** Not in the PDF reports. Can Gage check the TEAM live-time / real-time / DT-meter logs? Important for assessing whether the small Al+Al sum peak indicates the count rate was too high.
3. **Polishing protocol details for the May 22 polished sample.** Did the workflow include the final ≥20 min vibratory colloidal-silica step + thorough DI/ethanol rinse + plasma clean? Was the final rinse fresh or recirculated? This is the primary determinant of whether the spheres are SiO₂ residue.
4. **Spot EDX on one of the spheres.** A single 60–120 s point spectrum on a sphere (vs. clean matrix nearby) will diagnose Si+O residue vs. real Mg-rich nodule vs. spatter inclusion in ~5 minutes of beam time.
5. **BSE image of the polished sample.** Was BSE imaging tried before/after the SEM-EDS run? Z-contrast often reveals Mg₂Si or Al-Fe-Si intermetallics that don't show in SE.
6. **ICP-OES on the powder.** Do we have ICP-OES or OES (e.g., from Carpenter / EOS / Linde / SLM Solutions / Renishaw feedstock COA) for this powder lot? Even a vendor COA would anchor "true bulk Mg" within ±0.02 wt%.
7. **Standards availability.** Does the BYU EML or Standing's lab have a pure Mg, MgO, pure Al, and NIST K412 (or equivalent) standard set? This is the cheapest accuracy upgrade available.
8. **Polished sample raw MSA file.** Only the PDF report is available for the polished Areas 6 and 7. Could Gage export the raw MSA/CSV from TEAM? Then we can do the same DTSA-II / HyperSpy re-fit on the polished spectra (not just the non-flat one).
9. **DTSA-II / HyperSpy access.** Is there interest in having one of us walk through the NIST DTSA-II standards-based workflow with Gage on the next run? Mike Standing's group may already have a SOP for this.

## Retrieval script

```python
import os, uuid, pathlib
from edison_client import EdisonClient
client = EdisonClient(api_key=os.environ["EDISON_API_KEY"])
TASK_IDS = {
    "ANALYSIS":            "53f221ff-1bcb-4feb-a48b-e3d3c9cc6b95",
    "LIT_eZAF_Mg_bias":    "1c63284b-2f0a-415c-b51f-8c53fe6a4332",
    "LIT_Mg_segregation":  "21ba848f-8c6c-4db1-9830-35062b1d11a2",
    "LIT_amp_time":        "afe8c121-9f8e-4444-abd2-31aa5c42c74e",
    "LIT_spheres":         "53ed54dd-a61c-4074-8858-6c0da3e0d7c9",
    "LIT_SOP":             "705df51f-975c-48fa-8387-3a7e07389f47",
}
out = pathlib.Path("edison_answers"); out.mkdir(exist_ok=True)
for name, tid in TASK_IDS.items():
    r = client.get_task(uuid.UUID(tid))
    (out / f"{name}.md").write_text(
        f"# {name}\nTask: {tid}\nStatus: {r.status}\n\n## Query\n\n{r.query}\n\n## Answer\n\n{r.answer}"
    )
```

To re-upload the slim bundle yourself (matters for Analysis crow — see API docs note below):

```python
resp = client.store_file_content(
    name="BYU-VCL_AlSi10Mg_EDS_slim",
    file_path="./eds-bundle-slim",      # raw MSA/CSV/XML + README
    description="Slim BYU VCL AlSi10Mg EDS bundle for Edison Analysis crow.",
    as_collection=True,                  # critical — zips dir as single entry
)
print(resp.data_storage.id)
```

## API note (for future sessions)

The ANALYSIS crow initially failed with status `fail` and no error message when the data bundle was uploaded as separate files via `upload_file` per-file. Per the [Edison file-management docs](https://docs.edisonscientific.com/edison-client/file-management), `Edison Analysis` expects directory inputs uploaded as a single zipped collection via `store_file_content(file_path=DIR, as_collection=True)`. Once re-uploaded that way, the crow ran for ~11 minutes and returned a full peak-deconvolution analysis of the raw MSA spectrum. Also note: removing the large PDFs (21 MB → 152 kB bundle) may have helped with the OOM / timeout — but the collection-vs-individual-files distinction was the actual blocker.
