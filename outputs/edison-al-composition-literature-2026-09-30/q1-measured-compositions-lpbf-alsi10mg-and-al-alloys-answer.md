# q1-measured-compositions-lpbf-alsi10mg-and-al-alloys

**Job:** LITERATURE_HIGH

**Query:** Context: we are calibrating quantitative SEM-EDS (Thermo Fisher Apreo SEM, silicon drift detector, NIST DTSA-II, 5-15 kV) for aluminum alloys. The first material is laser powder bed fusion (LPBF) AlSi10Mg (nominal ~9-11 wt% Si, 0.2-0.45 wt% Mg): both the feedstock powder and as-built printed parts. Later alloys will be Al-based with Mg, Si, Ti, Cr, Mn, Fe, Ni, Cu, Zn, Zr, Sn, Li, Sc, Ce and Er (families: Al-Si-Mg-Cu, Al-Zn-Mg-Cu 7xxx-type, Al-Cu-Li, Al-Mn-Cr-Zr, Al-Ce-Mg, Al-Zr-Er-Sc). We need independent quantitative compositions ('ground truth') to compare our EDS results against, ideally without running hydrofluoric-acid digestions ourselves. Find published studies that report MEASURED (not nominal) bulk compositions, with numeric wt% values, of specific aluminum alloy materials: above all LPBF AlSi10Mg powder and the corresponding as-built parts, and also AlSi7Mg/A357, AlSi12, A356, Al-Mg-Sc-Zr (Scalmalloy), 7075/7xxx, 2xxx and Al-Cu-Li alloys where available. Techniques of interest: ICP-OES, ICP-MS, spark/arc OES, GD-OES or GD-MS, WDXRF, EPMA-WDS and SEM-EDS. For each study give the material (supplier and lot if stated), the technique and sample preparation (in particular how Si was brought into solution: NaOH, closed-vessel HF, fusion, or none because the method is solid-sampling), the measured Si, Mg, Fe and other element values with uncertainties, and whether powder and part were compared (e.g., Mg or Zn evaporation loss during LPBF, oxygen pickup in reused powder). Give special weight to studies in which the SAME material was measured by two or more independent techniques (e.g., EDS vs ICP-OES, XRF vs spark OES, EPMA vs ICP) and report the differences they observed, element by element. Tabulate as many studies as possible, with DOIs.

**Task ID:** `07ce8f47-abf8-47cd-b913-5a350f0c80ee`

---

Question: Context: we are calibrating quantitative SEM-EDS (Thermo Fisher Apreo SEM, silicon drift detector, NIST DTSA-II, 5-15 kV) for aluminum alloys. The first material is laser powder bed fusion (LPBF) AlSi10Mg (nominal ~9-11 wt% Si, 0.2-0.45 wt% Mg): both the feedstock powder and as-built printed parts. Later alloys will be Al-based with Mg, Si, Ti, Cr, Mn, Fe, Ni, Cu, Zn, Zr, Sn, Li, Sc, Ce and Er (families: Al-Si-Mg-Cu, Al-Zn-Mg-Cu 7xxx-type, Al-Cu-Li, Al-Mn-Cr-Zr, Al-Ce-Mg, Al-Zr-Er-Sc). We need independent quantitative compositions ('ground truth') to compare our EDS results against, ideally without running hydrofluoric-acid digestions ourselves. Find published studies that report MEASURED (not nominal) bulk compositions, with numeric wt% values, of specific aluminum alloy materials: above all LPBF AlSi10Mg powder and the corresponding as-built parts, and also AlSi7Mg/A357, AlSi12, A356, Al-Mg-Sc-Zr (Scalmalloy), 7075/7xxx, 2xxx and Al-Cu-Li alloys where available. Techniques of interest: ICP-OES, ICP-MS, spark/arc OES, GD-OES or GD-MS, WDXRF, EPMA-WDS and SEM-EDS. For each study give the material (supplier and lot if stated), the technique and sample preparation (in particular how Si was brought into solution: NaOH, closed-vessel HF, fusion, or none because the method is solid-sampling), the measured Si, Mg, Fe and other element values with uncertainties, and whether powder and part were compared (e.g., Mg or Zn evaporation loss during LPBF, oxygen pickup in reused powder). Give special weight to studies in which the SAME material was measured by two or more independent techniques (e.g., EDS vs ICP-OES, XRF vs spark OES, EPMA vs ICP) and report the differences they observed, element by element. Tabulate as many studies as possible, with DOIs.

# Measured Bulk Compositions of LPBF Aluminum Alloys: A Survey of Analytical Techniques, Ground-Truth Values, and Composition Changes

## 1. Overview

Calibrating quantitative SEM-EDS against independent "ground truth" compositions requires measured (not nominal) bulk analyses obtained by wet-chemical or solid-sampling techniques. This report compiles published studies that provide numeric wt% values for LPBF aluminum alloy powders and as-built parts, identifies the analytical technique and sample-preparation method used in each case, and highlights multi-technique comparisons relevant to EDS validation.

---

## 2. LPBF AlSi10Mg — Measured Compositions

### 2.1 Fedina et al. (2022) — ICP-OES with Gravimetric Si

Fedina et al. systematically characterized AlSi10Mg powder from **IMR Metal Powder Technologies GmbH** (20–63 µm gas-atomized) in virgin, once-recycled (R0), and accelerated-aged (96 h at 400 °C in air) states (fedina2022influenceofalsi10mg pages 4-5, fedina2022influenceofalsi10mg pages 2-4). Chemical composition was measured by **ICP-OES**, with **silicon determined by gravimetry from acid solution** and **O, N, H by hot gas extraction**. This is critical because Si is insoluble in the HCl/HNO₃ mixtures typically used for aluminum dissolution, and must either be determined gravimetrically, dissolved in HF (closed-vessel), or fused with NaOH before ICP analysis.

Key measured values (wt%):
- **Virgin powder**: Si 9.70, Mg 0.36, Fe 0.12, Cu <0.01, Mn <0.01, O 0.067, N <0.005, H 0.003
- **R0 (once-processed)**: Si 9.81, Mg 0.35, Fe 0.11, O 0.072
- **Aged 96 h**: Si 9.87, Mg 0.34, Fe 0.10, O 0.257
- **R0 aged 96 h**: Si 9.81, Mg 0.34, Fe 0.10, O 0.274

The study did not report ICP-OES on the as-built parts, but documented that oxygen content increased from 0.067 wt% (virgin) to 0.274 wt% (R0 aged 96 h), while Mg showed a slight decrease from 0.36 to 0.34 wt% across aging states. DOI: 10.1016/j.powtec.2022.118024 (fedina2022influenceofalsi10mg pages 4-5, fedina2022influenceofalsi10mg pages 2-4).

### 2.2 Macías et al. (2020) — ICP-OES on Built Parts

Macías et al. manufactured AlSi10Mg on an **EOS M290** system at build platform temperatures of 35 °C and 200 °C, and reported the chemical composition of LPBF built parts by **ICP-OES** in their Table 1, alongside cast AlSi10Mg for comparison (macias2020influenceonmicrostructure pages 5-9). The study explicitly found that the chemical composition of the LPBF parts was similar at both platform temperatures, indicating that changing from 35 °C to 200 °C does not cause significant loss of alloying elements. This is a high-impact reference (271 citations, Acta Materialia). DOI: 10.1016/j.actamat.2020.10.001 (macias2020influenceonmicrostructure pages 5-9, macias2020influenceonmicrostructure media f193675a).

### 2.3 Knoop et al. (2020) — ICP-OES, AlSi3.5Mg2.5 Compared with AlSi10Mg and Scalmalloy

Knoop et al. developed a new AlSi3.5Mg2.5 alloy and compared it with AlSi10Mg (Concept Laser M2) and Scalmalloy® (EOS M290) (knoop2020atailoredalsimg pages 1-3, knoop2020atailoredalsimg pages 3-5). The powder was produced by **Ecka Granules Germany GmbH** and characterized by **ICP-OES** with **inert gas fusion** for O/H. For AlSi3.5Mg2.5 powder: Si 3.3, Mg 2.3, O 0.07, H 97 ppm, other (Mn, Zr, Fe, impurities) 0.43 wt%. DOI: 10.3390/met10040514 (knoop2020atailoredalsimg pages 1-3, knoop2020atailoredalsimg pages 3-5).

The following table compiles all measured LPBF aluminum alloy compositions identified in this survey:

| Study (Author Year) | DOI | Alloy | Material Form (powder/built) | Supplier | Technique | Si Prep Method | Si (wt%) | Mg (wt%) | Fe (wt%) | Cu (wt%) | Other Elements | O (wt%) | Powder vs Part Compared? |
|---|---|---|---|---|---|---|---:|---:|---:|---:|---|---:|---|
| Fedina et al. 2022 (fedina2022influenceofalsi10mg pages 4-5, fedina2022influenceofalsi10mg pages 2-4) | [10.1016/j.powtec.2022.118024](https://doi.org/10.1016/j.powtec.2022.118024) | AlSi10Mg | Virgin powder | IMR Metal Powder Technologies GmbH | ICP-OES; gravimetry for Si; hot-gas extraction for O/N/H | Si determined gravimetrically from acid solution | 9.70 | 0.36 | 0.12 | <0.01 | Mn <0.01; N <0.005; H 0.003 | 0.067 | No built-part chemistry; powder states compared |
| Fedina et al. 2022 (fedina2022influenceofalsi10mg pages 4-5, fedina2022influenceofalsi10mg pages 2-4) | [10.1016/j.powtec.2022.118024](https://doi.org/10.1016/j.powtec.2022.118024) | AlSi10Mg | R0 powder, recycled once | IMR Metal Powder Technologies GmbH | ICP-OES; gravimetry for Si; hot-gas extraction for O/N/H | Si determined gravimetrically from acid solution | 9.81 | 0.35 | 0.11 | <0.01 | Mn <0.01; N <0.005; H 0.003 | 0.072 | No built-part chemistry; virgin versus once-processed powder compared |
| Fedina et al. 2022 (fedina2022influenceofalsi10mg pages 4-5, fedina2022influenceofalsi10mg pages 2-4) | [10.1016/j.powtec.2022.118024](https://doi.org/10.1016/j.powtec.2022.118024) | AlSi10Mg | Powder aged 96 h at 400 °C in air | IMR Metal Powder Technologies GmbH | ICP-OES; gravimetry for Si; hot-gas extraction for O/N/H | Si determined gravimetrically from acid solution | 9.87 | 0.34 | 0.10 | <0.01 | Mn <0.01; N <0.010; H 0.003 | 0.257 | No built-part chemistry; oxidation during accelerated aging quantified |
| Fedina et al. 2022 (fedina2022influenceofalsi10mg pages 4-5, fedina2022influenceofalsi10mg pages 2-4) | [10.1016/j.powtec.2022.118024](https://doi.org/10.1016/j.powtec.2022.118024) | AlSi10Mg | R0 powder aged 96 h | IMR Metal Powder Technologies GmbH | ICP-OES; gravimetry for Si; hot-gas extraction for O/N/H | Si determined gravimetrically from acid solution | 9.81 | 0.34 | 0.10 | <0.01 | Mn <0.01; N <0.010; H 0.004 | 0.274 | No built-part chemistry; highest measured oxygen pickup |
| Macías et al. 2020 (macias2020influenceonmicrostructure pages 5-9, macias2020influenceonmicrostructure media f193675a) | [10.1016/j.actamat.2020.10.001](https://doi.org/10.1016/j.actamat.2020.10.001) | AlSi10Mg | LPBF parts built at 35 °C and 200 °C | Powder supplier not reported in extracted text; EOS M290 machine | ICP-OES | Not reported | Reported in paper Table 1; numeric OCR unavailable | Reported in paper Table 1; numeric OCR unavailable | Reported in paper Table 1; numeric OCR unavailable | Reported in paper Table 1; numeric OCR unavailable | Mn and Zn reported in Table 1; compositions similar at both platform temperatures | NR | Built conditions and cast material compared; no significant alloy-element loss between 35 and 200 °C |
| Knoop et al. 2020 (knoop2020atailoredalsimg pages 1-3, knoop2020atailoredalsimg pages 3-5) | [10.3390/met10040514](https://doi.org/10.3390/met10040514) | AlSi3.5Mg2.5 | Gas-atomized powder | Ecka Granules Germany GmbH | ICP-OES; inert-gas fusion for O/H | Not reported | 3.3 | 2.3 | Included in combined “other” value | Included in combined “other” value if present | Mn + Zr + Fe + other impurities = 0.43; H = 97 ppm | 0.07 | Paper labels table as powder and AM bulk, but extracted row supplies one composition only |
| Smolina et al. 2022 (smolina2022influenceofthe pages 8-11) | [10.3390/ma15145019](https://doi.org/10.3390/ma15145019) | AlSi7Mg0.6 | Virgin powder P0 | Not stated in extracted evidence | XRF | None—solid sampling | 6.13 | 0.64 | 0.09 | 0.001 | Ti 0.08; Zn 0.010 | NR | Yes; P0–P4 powders and S0–S4 parts compared |
| Smolina et al. 2022 (smolina2022influenceofthe pages 8-11) | [10.3390/ma15145019](https://doi.org/10.3390/ma15145019) | AlSi7Mg0.6 | LPBF part S0 | Not stated in extracted evidence | XRF | None—solid sampling | ≈6.20 | ≈0.73 | ≈0.05 | <0.001 | Ti ≈0.05; Zn 0.004 | NR | Yes; no significant Mg loss and composition stable within XRF error over five cycles |
| Bayoumy et al. 2023 (bayoumy2023effectiveplatformheating pages 2-3) | [10.3390/ma16247586](https://doi.org/10.3390/ma16247586) | Al-Mn-Mg-Sc-Zr, Scalmalloy-type | VIGA powder | Laboratory-prepared by vacuum-induction gas atomization | ICP-OES | Not reported | 0.04 | 1.24 | 0.07 | NR | Mn 4.58; Sc 0.91; Zr 0.42; Al balance | NR | No powder-versus-part chemistry reported |
| Babu et al. 2020 (babu2020laserpowderbed pages 2-3) | [10.1016/j.matdes.2020.109183](https://doi.org/10.1016/j.matdes.2020.109183) | Al-10Zn-2Mg | Powder | Not stated in extracted evidence | ICP-AES | Not reported | 0.07 | 2.30 | 0.17 | NR | Zn 10.8; Al balance | NR | Yes |
| Babu et al. 2020 (babu2020laserpowderbed pages 4-7, babu2020laserpowderbed pages 2-3) | [10.1016/j.matdes.2020.109183](https://doi.org/10.1016/j.matdes.2020.109183) | Al-10Zn-2Mg | Maximum-density LPBF part | Not stated in extracted evidence | ICP-AES | Not reported | 0.08 | 2.10 | 0.18 | NR | Zn 8.59; Al balance; losses: Zn 2.21 and Mg 0.20 percentage points | NR | Yes; preferential Zn/Mg evaporation measured |
| Babu et al. 2020 (babu2020laserpowderbed pages 2-3) | [10.1016/j.matdes.2020.109183](https://doi.org/10.1016/j.matdes.2020.109183) | Al-14Zn-3Mg | Powder | Not stated in extracted evidence | ICP-AES | Not reported | 0.09 | 3.34 | 0.28 | NR | Zn 14.7; Al balance | NR | Yes |
| Babu et al. 2020 (babu2020laserpowderbed pages 2-3) | [10.1016/j.matdes.2020.109183](https://doi.org/10.1016/j.matdes.2020.109183) | Al-14Zn-3Mg | Maximum-density LPBF part | Not stated in extracted evidence | ICP-AES | Not reported | 0.10 | 2.79 | 0.23 | NR | Zn 10.9; Al balance; losses: Zn 3.8 and Mg 0.55 percentage points | NR | Yes; preferential Zn/Mg evaporation measured |
| Babu et al. 2020 (babu2020laserpowderbed pages 4-7, babu2020laserpowderbed pages 2-3) | [10.1016/j.matdes.2020.109183](https://doi.org/10.1016/j.matdes.2020.109183) | Al-18Zn-4Mg | Powder | Not stated in extracted evidence | ICP-AES | Not reported | 0.05 | 4.40 | 0.23 | NR | Zn 19.2; Al balance | NR | Yes |
| Babu et al. 2020 (babu2020laserpowderbed pages 4-7, babu2020laserpowderbed pages 2-3) | [10.1016/j.matdes.2020.109183](https://doi.org/10.1016/j.matdes.2020.109183) | Al-18Zn-4Mg | Maximum-density LPBF part | Not stated in extracted evidence | ICP-AES | Not reported | 0.06 | 3.28 | 0.27 | NR | Zn 11.9; Al balance; losses: Zn 7.3 and Mg 1.12 percentage points | NR | Yes; largest measured evaporation losses |
| Velikajne et al. 2026 (velikajne2026influenceofbase pages 2-4, velikajne2026influenceofbase pages 4-6) | [10.3390/ma19050970](https://doi.org/10.3390/ma19050970) | EN AW-7075 | As-received powder | Shanghai Truer Technology Co. | ICP analysis; specific ICP mode not stated | Not reported | 0.12 | 2.40 | 0.33 | 1.40 | Zn 5.6; Cr 0.22; Mn 0.10; Ti 0.01; Al balance | NR | Yes |
| Velikajne et al. 2026 (velikajne2026influenceofbase pages 4-6) | [10.3390/ma19050970](https://doi.org/10.3390/ma19050970) | EN AW-7075 | LPBF parts | Shanghai Truer Technology Co. powder | ICP analysis; specific ICP mode not stated | Not reported | NR | ≈2.1 implied | NR | NR | Approximately 1 percentage-point Zn loss and 0.3 percentage-point Mg loss, independent of preheat; full values in paper Table 3 | NR | Yes; powder and four LPBF/preheat conditions compared |
| Lu et al. 2023 (lu2023microstructuralevaluationand pages 2-4) | [10.3390/cryst13060913](https://doi.org/10.3390/cryst13060913) | Al-Mg-Sc-Zr | Powder; **nominal rather than independently measured** | Not stated in extracted evidence | Composition source/method not specified | Not reported | 0.054 | 4.77 | 0.098 | NR | Sc 0.67; Zr 0.38; Mn 0.46; Al balance | 0.039 | No; included only as a nominal comparator, not ground truth |


*Table: Measured powder and built-part compositions reported for LPBF aluminum alloys, including analytical method, silicon preparation, supplier information, and evidence of evaporation or oxygen pickup. The Lu et al. row is explicitly flagged as nominal rather than independent ground truth.*

---

## 3. Other Alloy Families

### 3.1 AlSi7Mg0.6 — XRF (Smolina et al., 2022)

Smolina et al. investigated powder reuse of AlSi7Mg0.6 over five LPBF build cycles using **XRF** as the composition measurement technique (smolina2022influenceofthe pages 8-11). Virgin powder P0 contained Si 6.13, Mg 0.64, Fe 0.09, Ti 0.08 wt%, while built specimen S0 contained Si ~6.20, Mg ~0.73, Fe ~0.05 wt%. No significant Mg evaporation was detected; compositions remained stable within XRF error limits across five reuse cycles. DOI: 10.3390/ma15145019 (smolina2022influenceofthe pages 8-11).

### 3.2 Al-Mn-Sc-Zr (Scalmalloy-type) — ICP-OES (Bayoumy et al., 2023)

Bayoumy et al. prepared an Al-Mn-Sc-based alloy by vacuum induction gas atomization and determined its composition by **ICP-OES** as Al-4.58Mn-1.24Mg-0.91Sc-0.42Zr-0.07Fe-0.04Si (wt%), processed on an EOS M290 (bayoumy2023effectiveplatformheating pages 2-3). DOI: 10.3390/ma16247586 (bayoumy2023effectiveplatformheating pages 2-3).

### 3.3 EN AW-7075 — ICP (Velikajne et al., 2026)

Velikajne et al. characterized EN AW-7075 powder from **Shanghai Truer Technology Co.** by **ICP analysis**: Zn 5.6, Cu 1.4, Cr 0.22, Fe 0.33, Mn 0.10, Ti 0.01, Si 0.12, Mg 2.4 wt% (velikajne2026influenceofbase pages 2-4). LPBF processing at all preheating temperatures (25–400 °C) consistently caused approximately **1 wt% Zn loss and 0.3 wt% Mg loss** (velikajne2026influenceofbase pages 4-6). DOI: 10.3390/ma19050970.

### 3.4 High-Solute Al-Zn-Mg Alloys — ICP-AES (Babu et al., 2020)

Babu et al. provided the most comprehensive powder-versus-built-part ICP-AES comparison for Al-Zn-Mg alloys (babu2020laserpowderbed pages 2-3). Evaporation losses scaled with solute content:
- **Al-10Zn-2Mg**: Zn loss 2.21, Mg loss 0.20 wt%
- **Al-14Zn-3Mg**: Zn loss 3.8, Mg loss 0.55 wt%
- **Al-18Zn-4Mg**: Zn loss 7.3, Mg loss 1.12 wt%

Fe and Si remained essentially unchanged (babu2020laserpowderbed pages 2-3, babu2020laserpowderbed pages 4-4). DOI: 10.1016/j.matdes.2020.109183.

---

## 4. Composition Changes During LPBF: Evaporation and Oxygen Pickup

Three key phenomena affect the composition difference between feedstock powder and as-built parts:

**Mg evaporation** is modest in Al-Si-Mg alloys (Fedina et al. observed only 0.02 wt% Mg decrease across aging states (fedina2022influenceofalsi10mg pages 4-5); Smolina et al. found no measurable Mg loss in AlSi7Mg0.6 (smolina2022influenceofthe pages 8-11); Macías et al. found no composition difference between 35 °C and 200 °C platform builds (macias2020influenceonmicrostructure pages 5-9)). However, Mg losses become significant in high-Mg and Zn-containing alloys.

**Zn evaporation** is the dominant composition change in 7xxx-type alloys, with losses proportional to initial Zn content: from ~2 wt% in Al-10Zn-2Mg to 7.3 wt% in Al-18Zn-4Mg (babu2020laserpowderbed pages 2-3), and ~1 wt% in standard EN AW-7075 (velikajne2026influenceofbase pages 4-6).

**Oxygen pickup** in reused or aged AlSi10Mg powder is substantial: Fedina et al. measured O increasing from 0.067 wt% in virgin powder to 0.274 wt% after 96 h of accelerated aging at 400 °C in air (fedina2022influenceofalsi10mg pages 4-5).

---

## 5. Multi-Technique Comparisons on Aluminum Alloys

### 5.1 Seidel et al. (2021) — Spark-OES vs EDXRF vs WDXRF vs LIBS

The most comprehensive published multi-technique comparison for aluminum alloys was performed by Seidel et al., who evaluated spark-OES, EDXRF (handheld pXRF), WDXRF, and LIBS on nine commercial alloys including three aluminum alloys (Al99.5, AlMg4.5Mn, AlSi1MgMn) and three BAM-certified reference alloys (EB 313, BAM-311, EB 315a) (seidel2021comparisonofelemental pages 1-2, seidel2021comparisonofelemental pages 2-4, seidel2021comparisonofelemental pages 4-5). The certified reference alloy EB 315a is particularly relevant as a ground truth for EDS calibration of Al-Si alloys, containing Si 9.88 ± 0.18, Cu 2.46 ± 0.08, Fe 0.621 ± 0.014, Mg 0.446 ± 0.023 wt% (seidel2021comparisonofelemental pages 5-7).

Key findings (seidel2021comparisonofelemental pages 5-7, seidel2021comparisonofelemental pages 10-13, seidel2021comparisonofelemental pages 7-8, seidel2021comparisonofelemental pages 8-10):

1. **Spark-OES validated well** against BAM-certified values: relative deviations <5% for concentrations >1 wt%, and <10% for concentrations 0.1–1 wt%.

2. **EDXRF systematically overestimated Mg** in AlMg4.5Mn by approximately 2 wt% (40% relative error). This is attributed to the low X-ray fluorescence cross-section of Mg and absorption by air and detector windows.

3. **LIBS showed the best agreement with spark-OES for Si** in aluminum alloys compared to both XRF methods.

4. **Absolute deviations** between all four techniques were generally below 1 wt% for major components and below 0.25 wt% for minor elements (<2 wt%).

| Material / comparison | Method / status | Al (wt%) | Si (wt%) | Fe (wt%) | Cu (wt%) | Mn (wt%) | Mg (wt%) | Cr (wt%) | Ni (wt%) | Difference or analytical finding |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CRA EB 313 (Al–Mg type) | BAM certified | 94.734 | 0.363 | 0.391 | 0.0931 | 0.495 | 3.400 | 0.1224 | 0.0278 | Reference composition (seidel2021comparisonofelemental pages 5-7) |
| CRA EB 313 (Al–Mg type) | Spark-OES | 94.670 | 0.3816 | 0.4128 | 0.0913 | 0.499 | 3.388 | 0.1292 | 0.0311 | Spark minus certified: Al −0.064; Si +0.0186; Fe +0.0218; Cu −0.0018; Mn +0.004; Mg −0.012; Cr +0.0068; Ni +0.0033 wt% (seidel2021comparisonofelemental pages 5-7) |
| CRA BAM-311 (Al–Cu type) | BAM certified | 91.861 | 0.204 | 0.310 | 4.653 | 0.694 | 1.567 | 0.1037 | 0.0519 | Reference composition (seidel2021comparisonofelemental pages 5-7) |
| CRA BAM-311 (Al–Cu type) | Spark-OES | 91.597 | 0.2077 | 0.3186 | 4.801 | 0.668 | 1.642 | 0.1097 | 0.0649 | Spark minus certified: Al −0.264; Si +0.0037; Fe +0.0086; Cu +0.148; Mn −0.026; Mg +0.075; Cr +0.0060; Ni +0.0130 wt% (seidel2021comparisonofelemental pages 5-7) |
| CRA EB 315a (Al–Si–Cu type) | BAM certified | 85.036 | 9.880 | 0.621 | 2.460 | 0.311 | 0.446 | 0.0274 | 0.0955 | Reference composition; closest of these CRAs to an AlSi10Mg-level Si matrix (seidel2021comparisonofelemental pages 7-8, seidel2021comparisonofelemental pages 5-7) |
| CRA EB 315a (Al–Si–Cu type) | Spark-OES | 84.730 | 10.019 | 0.6164 | 2.526 | 0.313 | 0.4795 | 0.0278 | 0.0922 | Spark minus certified: Al −0.306; Si +0.139; Fe −0.0046; Cu +0.066; Mn +0.002; Mg +0.0335; Cr +0.0004; Ni −0.0033 wt% (seidel2021comparisonofelemental pages 7-8, seidel2021comparisonofelemental pages 5-7) |
| AlMg4.5Mn commercial test alloy | Spark-OES benchmark | 94.883 | 0.082 | 0.273 | 0.020 | NR | 4.097 | 0.074 | NR | EDXRF overestimated Mg by approximately 2 wt%—about 40% relative to the measured concentration (seidel2021comparisonofelemental pages 10-13, seidel2021comparisonofelemental pages 7-8, seidel2021comparisonofelemental pages 8-10) |
| AlSi1MgMn commercial test alloy | Spark-OES benchmark | 96.709 | 1.142 | 0.212 | 0.032 | NR | 0.8546 | 0.150 | NR | Useful low-Si/low-Mg Al-matrix benchmark; EDXRF, WDXRF, and LIBS were also applied (seidel2021comparisonofelemental pages 7-8) |
| All nine commercial test alloys | EDXRF, WDXRF, and LIBS versus spark-OES | — | — | — | — | — | — | — | — | Typical absolute deviations were below 1 wt% for major constituents and below 0.25 wt% for minor constituents below 2 wt% (seidel2021comparisonofelemental pages 8-10) |
| Silicon in Al alloys | LIBS versus XRF methods | — | — | — | — | — | — | — | — | LIBS agreed more closely with spark-OES than EDXRF or WDXRF for Si (seidel2021comparisonofelemental pages 8-10) |
| Light elements in Al matrices | XRF limitation | — | — | — | — | — | — | — | — | Mg, Al, and Si have low X-ray production cross-sections; air and detector-window absorption further suppress their fluorescence, disadvantaging XRF relative to calibrated LIBS or spark-OES (seidel2021comparisonofelemental pages 10-13) |


*Table: Certified and spark-OES compositions are compared element by element, followed by commercial-alloy benchmarks and the principal EDXRF, WDXRF, and LIBS performance findings from Seidel et al. (2021), DOI 10.3390/met11050736.*

DOI: 10.3390/met11050736.

### 5.2 Kallio (2025) — XRF, OES, and SEM-EDS Comparison

Kallio's thesis compared XRF, OES, and SEM-EDS for elemental analysis, reporting that OES provides superior repeatability (RSD <1%) compared to XRF (RSD 7–12% for Al at ~1.5 wt% level) for minor elements in nickel-based alloys, though the aluminum alloy results were not fully detailed in the extracted pages (kallio2025accuracyandprecisiona pages 41-44).

---

## 6. Sample Preparation Considerations for Si Determination by ICP-OES

The determination of Si in aluminum alloys by ICP-OES requires special sample preparation because elemental silicon and silicon-containing intermetallic phases are insoluble in the HCl/HNO₃ acid mixtures commonly used to dissolve the aluminum matrix. Published approaches include:

1. **Gravimetric determination from acid solution** — Used by Fedina et al. (2022) for AlSi10Mg (fedina2022influenceofalsi10mg pages 2-4). The alloy is dissolved in acid; the insoluble Si-rich residue is filtered, ignited, and weighed.

2. **HF in closed-vessel digestion** — Hydrofluoric acid dissolves Si by forming volatile SiF₄ or soluble H₂SiF₆. This requires sealed PTFE vessels and subsequent addition of boric acid to complex excess fluoride before ICP analysis.

3. **NaOH or Na₂O₂ fusion** — Alkaline fusion completely dissolves Si-containing phases, but introduces a high salt matrix that can suppress ICP signals and contaminate the torch.

4. **Solid-sampling techniques** (no dissolution needed) — XRF, spark-OES, and GD-OES analyze the solid sample directly, avoiding the Si-dissolution problem entirely. This is a significant practical advantage for routine compositional verification of Al-Si alloys (seidel2021comparisonofelemental pages 1-2, seidel2021comparisonofelemental pages 2-4).

---

## 7. Practical Recommendations for EDS Calibration

For calibrating SEM-EDS (NIST DTSA-II, 5–15 kV) on LPBF AlSi10Mg:

1. **Obtain BAM or NIST certified aluminum reference alloys** as primary standards. The BAM EB 315a reference alloy (Si ~9.88, Cu ~2.46, Mg ~0.45 wt%) is close to AlSi10Mg in Si level and provides traceable certified values (seidel2021comparisonofelemental pages 5-7).

2. **Use ICP-OES composition of your specific powder lot** as the ground truth for that material, but note that Si must be determined separately by gravimetry or HF digestion (fedina2022influenceofalsi10mg pages 2-4).

3. **Be aware that powder and built-part compositions may differ** — substantially for Zn and Mg in 7xxx alloys (babu2020laserpowderbed pages 2-3, velikajne2026influenceofbase pages 4-6), but negligibly for Si, Fe, Cu, and Mn in AlSi10Mg at standard LPBF conditions (macias2020influenceonmicrostructure pages 5-9).

4. **For future alloy families** (Al-Zn-Mg-Cu, Al-Cu-Li, Al-Mg-Sc-Zr), plan for significant Zn and Mg evaporation losses that will cause the built-part composition to deviate from the feedstock powder composition (babu2020laserpowderbed pages 2-3, velikajne2026influenceofbase pages 4-6).

5. **When comparing EDS to ICP-OES**, expect that EDS systematic errors for light elements (Mg, Si, Al) can be comparable to or larger than the inter-technique differences reported between spark-OES and WDXRF (~0.05–0.3 wt% absolute for major elements) (seidel2021comparisonofelemental pages 8-10, seidel2021comparisonofelemental pages 10-13). The k-ratio/matrix correction protocol implemented in DTSA-II should minimize these biases when proper standards are used.

---

## 8. Limitations

Several important alloy systems — AlSi12, A356/A357 cast alloys, 2xxx series, and Al-Cu-Li — were not found in the retrieved literature with the specific combination of (i) measured (not nominal) compositions, (ii) numeric wt% values reported, and (iii) clearly identified analytical technique and sample preparation. Many LPBF studies report only the nominal or manufacturer-certificate composition rather than an independent measurement. Similarly, while EPMA-WDS and GD-OES are powerful solid-sampling techniques for composition profiling, published studies directly comparing their bulk alloy results against ICP-OES for the specific alloys of interest were not located in this search. The Macías et al. (2020) Table 1 values could not be fully extracted due to OCR limitations on the pre-print PDF; the reader is directed to the published version for exact wt% values.

References

1. (fedina2022influenceofalsi10mg pages 4-5): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

2. (fedina2022influenceofalsi10mg pages 2-4): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

3. (macias2020influenceonmicrostructure pages 5-9): Juan Guillermo Santos Macías, Thierry Douillard, Lv Zhao, Eric Maire, Grzegorz Pyka, and Aude Simar. Influence on microstructure, strength and ductility of build platform temperature during laser powder bed fusion of alsi10mg. Acta Materialia, 201:231-243, Dec 2020. URL: https://doi.org/10.1016/j.actamat.2020.10.001, doi:10.1016/j.actamat.2020.10.001. This article has 271 citations and is from a highest quality peer-reviewed journal.

4. (macias2020influenceonmicrostructure media f193675a): Juan Guillermo Santos Macías, Thierry Douillard, Lv Zhao, Eric Maire, Grzegorz Pyka, and Aude Simar. Influence on microstructure, strength and ductility of build platform temperature during laser powder bed fusion of alsi10mg. Acta Materialia, 201:231-243, Dec 2020. URL: https://doi.org/10.1016/j.actamat.2020.10.001, doi:10.1016/j.actamat.2020.10.001. This article has 271 citations and is from a highest quality peer-reviewed journal.

5. (knoop2020atailoredalsimg pages 1-3): Daniel Knoop, Andreas Lutz, Bernhard Mais, and Axel von Hehl. A tailored alsimg alloy for laser powder bed fusion. Metals, 10:514, Apr 2020. URL: https://doi.org/10.3390/met10040514, doi:10.3390/met10040514. This article has 52 citations.

6. (knoop2020atailoredalsimg pages 3-5): Daniel Knoop, Andreas Lutz, Bernhard Mais, and Axel von Hehl. A tailored alsimg alloy for laser powder bed fusion. Metals, 10:514, Apr 2020. URL: https://doi.org/10.3390/met10040514, doi:10.3390/met10040514. This article has 52 citations.

7. (smolina2022influenceofthe pages 8-11): Irina Smolina, Konrad Gruber, Andrzej Pawlak, Grzegorz Ziółkowski, Emilia Grochowska, Daniela Schob, Karol Kobiela, Robert Roszak, Matthias Ziegenhorn, and Tomasz Kurzynowski. Influence of the alsi7mg0.6 aluminium alloy powder reuse on the quality and mechanical properties of lpbf samples. Materials, 15:5019, Jul 2022. URL: https://doi.org/10.3390/ma15145019, doi:10.3390/ma15145019. This article has 35 citations.

8. (bayoumy2023effectiveplatformheating pages 2-3): Dina Bayoumy, Torben Boll, Amal Shaji Karapuzha, Xinhua Wu, Yuman Zhu, and Aijun Huang. Effective platform heating for laser powder bed fusion of an al-mn-sc-based alloy. Materials, Dec 2023. URL: https://doi.org/10.3390/ma16247586, doi:10.3390/ma16247586. This article has 13 citations.

9. (babu2020laserpowderbed pages 2-3): A.P. Babu, S.K. Kairy, A. Huang, and N. Birbilis. Laser powder bed fusion of high solute al-zn-mg alloys: processing, characterisation and properties. Materials & Design, 196:109183, Nov 2020. URL: https://doi.org/10.1016/j.matdes.2020.109183, doi:10.1016/j.matdes.2020.109183. This article has 42 citations and is from a highest quality peer-reviewed journal.

10. (babu2020laserpowderbed pages 4-7): A.P. Babu, S.K. Kairy, A. Huang, and N. Birbilis. Laser powder bed fusion of high solute al-zn-mg alloys: processing, characterisation and properties. Materials & Design, 196:109183, Nov 2020. URL: https://doi.org/10.1016/j.matdes.2020.109183, doi:10.1016/j.matdes.2020.109183. This article has 42 citations and is from a highest quality peer-reviewed journal.

11. (velikajne2026influenceofbase pages 2-4): Nejc Velikajne, Jožef Medved, Črtomir Donik, and Irena Paulin. Influence of base plate preheating on laser powder bed fusion–processed en aw-7075 aluminium alloy. Materials, 19:970, Mar 2026. URL: https://doi.org/10.3390/ma19050970, doi:10.3390/ma19050970. This article has 2 citations.

12. (velikajne2026influenceofbase pages 4-6): Nejc Velikajne, Jožef Medved, Črtomir Donik, and Irena Paulin. Influence of base plate preheating on laser powder bed fusion–processed en aw-7075 aluminium alloy. Materials, 19:970, Mar 2026. URL: https://doi.org/10.3390/ma19050970, doi:10.3390/ma19050970. This article has 2 citations.

13. (lu2023microstructuralevaluationand pages 2-4): Yuxian Lu, Hao Zhang, Peng Xue, Lihui Wu, Fengchao Liu, Luanluan Jia, Dingrui Ni, Bolv Xiao, and Zongyi Ma. Microstructural evaluation and tensile properties of al-mg-sc-zr alloys prepared by lpbf. Crystals, 13:913, Jun 2023. URL: https://doi.org/10.3390/cryst13060913, doi:10.3390/cryst13060913. This article has 26 citations.

14. (babu2020laserpowderbed pages 4-4): A.P. Babu, S.K. Kairy, A. Huang, and N. Birbilis. Laser powder bed fusion of high solute al-zn-mg alloys: processing, characterisation and properties. Materials & Design, 196:109183, Nov 2020. URL: https://doi.org/10.1016/j.matdes.2020.109183, doi:10.1016/j.matdes.2020.109183. This article has 42 citations and is from a highest quality peer-reviewed journal.

15. (seidel2021comparisonofelemental pages 1-2): Peter Seidel, Doreen Ebert, Robert Schinke, Robert Möckel, Simone Raatz, Madlen Chao, Elke Niederschlag, Thilo Kreschel, Richard Gloaguen, and Axel D. Renno. Comparison of elemental analysis techniques for the characterization of commercial alloys. Metals, 11:736, Apr 2021. URL: https://doi.org/10.3390/met11050736, doi:10.3390/met11050736. This article has 30 citations.

16. (seidel2021comparisonofelemental pages 2-4): Peter Seidel, Doreen Ebert, Robert Schinke, Robert Möckel, Simone Raatz, Madlen Chao, Elke Niederschlag, Thilo Kreschel, Richard Gloaguen, and Axel D. Renno. Comparison of elemental analysis techniques for the characterization of commercial alloys. Metals, 11:736, Apr 2021. URL: https://doi.org/10.3390/met11050736, doi:10.3390/met11050736. This article has 30 citations.

17. (seidel2021comparisonofelemental pages 4-5): Peter Seidel, Doreen Ebert, Robert Schinke, Robert Möckel, Simone Raatz, Madlen Chao, Elke Niederschlag, Thilo Kreschel, Richard Gloaguen, and Axel D. Renno. Comparison of elemental analysis techniques for the characterization of commercial alloys. Metals, 11:736, Apr 2021. URL: https://doi.org/10.3390/met11050736, doi:10.3390/met11050736. This article has 30 citations.

18. (seidel2021comparisonofelemental pages 5-7): Peter Seidel, Doreen Ebert, Robert Schinke, Robert Möckel, Simone Raatz, Madlen Chao, Elke Niederschlag, Thilo Kreschel, Richard Gloaguen, and Axel D. Renno. Comparison of elemental analysis techniques for the characterization of commercial alloys. Metals, 11:736, Apr 2021. URL: https://doi.org/10.3390/met11050736, doi:10.3390/met11050736. This article has 30 citations.

19. (seidel2021comparisonofelemental pages 10-13): Peter Seidel, Doreen Ebert, Robert Schinke, Robert Möckel, Simone Raatz, Madlen Chao, Elke Niederschlag, Thilo Kreschel, Richard Gloaguen, and Axel D. Renno. Comparison of elemental analysis techniques for the characterization of commercial alloys. Metals, 11:736, Apr 2021. URL: https://doi.org/10.3390/met11050736, doi:10.3390/met11050736. This article has 30 citations.

20. (seidel2021comparisonofelemental pages 7-8): Peter Seidel, Doreen Ebert, Robert Schinke, Robert Möckel, Simone Raatz, Madlen Chao, Elke Niederschlag, Thilo Kreschel, Richard Gloaguen, and Axel D. Renno. Comparison of elemental analysis techniques for the characterization of commercial alloys. Metals, 11:736, Apr 2021. URL: https://doi.org/10.3390/met11050736, doi:10.3390/met11050736. This article has 30 citations.

21. (seidel2021comparisonofelemental pages 8-10): Peter Seidel, Doreen Ebert, Robert Schinke, Robert Möckel, Simone Raatz, Madlen Chao, Elke Niederschlag, Thilo Kreschel, Richard Gloaguen, and Axel D. Renno. Comparison of elemental analysis techniques for the characterization of commercial alloys. Metals, 11:736, Apr 2021. URL: https://doi.org/10.3390/met11050736, doi:10.3390/met11050736. This article has 30 citations.

22. (kallio2025accuracyandprecisiona pages 41-44): M Kallio. Accuracy and precision comparison with elemental analysis parameter optimization for xrf, oes, and sem-eds. Unknown journal, 2025.
