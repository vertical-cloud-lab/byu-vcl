# Measured compositions of aluminum alloys in the literature (2026-09-30)

Follow-up to [#110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110): find published,
quantitative composition data on specific Al alloys that could stand in for, or check, the
ICP-MS "ground truth" CALIBER needs for EDS on AlSi10Mg.

| Edison query (all `success`) | Job | Answer | Full trajectory |
| --- | --- | --- | --- |
| Measured compositions of LPBF AlSi10Mg and other Al alloys | LITERATURE_HIGH | [answer](q1-measured-compositions-lpbf-alsi10mg-and-al-alloys-answer.md) | [json](q1-measured-compositions-lpbf-alsi10mg-and-al-alloys.json) |
| Certified reference materials for Al alloys | LITERATURE | [answer](q2-certified-reference-materials-al-alloys-answer.md) | [json](q2-certified-reference-materials-al-alloys.json) |
| SEM-EDS accuracy on Al alloys | LITERATURE | [answer](q3-eds-accuracy-on-aluminum-alloys-answer.md) | [json](q3-eds-accuracy-on-aluminum-alloys.json) |

Queries and task IDs are in [`_task_ids.json`](_task_ids.json). Edison's CRM answer could not
read the NIST certificates, so the NIST values below were read from the certificates and the
NIST store directly. The literature numbers were checked against full text wherever it was open.

## 1. Certified solid discs: an EDS check with no dissolution

Polish one and measure it with the same recipe as the unknown. Its certified values are the
reference, so no digestion is needed.

| Material | Si | Mg | Other (wt%) | Form | Price, availability (read 2026-09-30) |
| --- | --- | --- | --- | --- | --- |
| **BAM ERM-EB315a**, AlSi9Cu3 | 9.88 ± 0.18 | 0.446 ± 0.023 | Cu 2.46 ± 0.08, Fe 0.621 ± 0.014, Mn 0.311 ± 0.009 | disc, 50 mm dia × 40 mm | [€364, 15 in stock](https://webshop.bam.de/webshop_en/reference-material/non-ferrous-metals-alloys/aluminium.html?___from_store=webshop_en&limit=5&p=5) |
| NIST SRM 1256b, alloy 380 | 9.362 ± 0.086 | 0.0637 ± 0.0040 | Cu 3.478 ± 0.074, Fe 0.865 ± 0.011, Zn 1.011 ± 0.030 | disc, ~6.3 cm × 1.9 cm | $1,076, available |
| ALSUI-422/03, alloy 4046 (LGC) | 9.41 | 0.346 | Fe 0.19, Mn 0.107, Ti 0.049 | chill-cast disc, 60 × 25 mm | not listed. Only confirmed in [LGC's 2017 catalogue](https://s3-eu-west-1.amazonaws.com/lgcstandards-assets/MediaGallery/catalogues/EA/LGC-Aluminium-Reference-Materials-2017.pdf), p. 16 |
| NIST SRM 1255b, alloy 356 | 7.298 ± 0.050 | 0.3822 ± 0.0051 | Fe 0.1170 ± 0.0068 | disc | discontinued |

- **ALSUI-422/03 is the only one that meets every AlSi10Mg limit.** It needs a quote and an availability check from LGC.
- **ERM-EB315a is the closest match that is in stock.** Its Si and Mg are right; its Cu and Fe are not.
- **Values are cited from:** the EB315a values as printed in [Seidel et al. 2021](https://doi.org/10.3390/met11050736); the NIST values from the certificates at `https://tsapps.nist.gov/srmext/certificates/<SRM>.pdf`.

**For later alloy families:**

| Material | Composition (wt%) | Price |
| --- | --- | --- |
| NIST SRM 1259, 7075 | Mg 2.48, Zn 5.44, Cu 1.60 | $653 |
| BAM ERM-EB317, AlZn6CuMgZr | — | €361 |
| NIST SRM 1258-I, 6011 modified | Mg 1.00, Si 0.80 | $583 |

**Caveat: these discs are certified for bulk analysis, not microanalysis.**
- **They are certified for bulk spark-OES and XRF use.** NIST's micro-XRF saw mm-scale hot spots of Ti, V, Mn, Fe, Cu, Zn and Ga in its Al discs. BAM's EB314a certificate excludes micro-analysis outright.
- **Measure them the same way every time.** Use large rasters over many fields, and report the field-to-field scatter as an uncertainty of its own.
- **No published EDS-vs-certified numbers for an Al CRM disc turned up.** [Lanzinger et al. 2024](https://doi.org/10.1016/j.microc.2024.111782) ran SEM-EDX on Al-alloy CRM *particles*, but the full text was not reachable.

## 2. Measured AlSi10Mg compositions

| Study | Material | Method | Si | Mg | Fe | O |
| --- | --- | --- | --- | --- | --- | --- |
| [Fedina 2022](https://doi.org/10.1016/j.powtec.2022.118024) | IMR powder, virgin | ICP-OES; "Silicon was determined by gravimetry from acid solution" | 9.70 | 0.36 | 0.12 | 0.067 |
| same | aged 96 h at 400 °C | same | 9.87 | 0.34 | 0.10 | 0.257 |
| [Di Egidio 2023](https://doi.org/10.3390/ma16052006) | LPBF parts | GD-OES | 9.74 ± 0.09 | 0.30 ± 0.03 | 0.13 ± 0.01 | — |
| [Lehmhus 2022](https://doi.org/10.3390/ma15207386) | LPBF parts from reused powder | spark OES, mean of 4 | 10.661 | 0.2769 | 0.118 | 0.0402 (by inert-gas fusion) |
| same | the virgin powder | supplier data, method not stated | 9.70 | 0.39 | 0.11 | — |
| [Hitzler 2020](https://doi.org/10.3390/ma13030720) | LPBF AlSi10Mg0.3 parts | spark OES | 12.483 ± 1.180 | 0.297 ± 0.122 | 0.205 ± 0.006 | — |
| [Pan 2022](https://doi.org/10.3390/ma15072528) | powder | Si by photometry, Mg by ICP-AES | 10.11 | 0.28 | — | 0.044 |
| [Guzmán-Nogales 2026](https://doi.org/10.3390/ma19071297) | powder (EDS) / part (XRF) | EDS / XRF | 11.30 / 10.82 | 1.10 / 1.09 | — / 0.17 | — |

**No paper measures AlSi10Mg powder and its printed part by the same bulk method.**
- **Lehmhus:** its 0.39 → 0.28 Mg drop mixes two methods with powder reuse, so it can't be read as evaporation loss.
- **Hitzler:** the Si above the spec and the ±41% Mg scatter show that spark OES on LPBF material is not automatically ground truth.
- **Guzmán-Nogales:** two techniques agree on an Mg level 2.5 times the spec limit. Agreement alone doesn't make a value right.

**What the composition does from powder to part:**

| Material | Method | Change |
| --- | --- | --- |
| AlSi7Mg0.6 ([Smolina 2022](https://doi.org/10.3390/ma15145019)) | XRF | "magnesium's evaporation was not detected" |
| Al-7Mg-2Si-1.2Zr ([Yang 2022](https://doi.org/10.3390/ma15155089)) | ICP-OES | Mg 6.73 → 6.17 (−8.3%) |
| EN AW-7075 ([Velikajne 2026](https://doi.org/10.3390/ma19050970)) | ICP | Zn −1, Mg −0.3 wt% at every preheat |
| Al-(10–18)Zn-(2–4)Mg ([Babu 2020](https://doi.org/10.1016/j.matdes.2020.109183)) | ICP-AES | Zn −2.2 to −7.3, Mg −0.20 to −1.12 wt% |

For the Zn-bearing families, a powder analysis will not stand in for the part.

## 3. Accuracy benchmarks

- **Spark OES on certified BAM Al discs** ([Seidel et al. 2021](https://doi.org/10.3390/met11050736)).
  - On EB315a: Si 10.019 vs 9.88 (+1.4% relative), Mg 0.4795 vs 0.446 (+7.5%).
  - The same paper found EDXRF over-read Mg by about 2 wt% (about 40% relative) on AlMg4.5Mn.
- **NIST, standards-based SDD-EDS with DTSA-II at low beam energy** ([Newbury & Ritchie 2024](https://doi.org/10.1007/s10853-024-10285-4)).
  - "Two-hundred sixty-three concentration measurements for 39 elements in 113 materials."
  - "more than 98% of the results were found to be captured within a range of ±5% RDEV, while 82% of the results fell in the range -2% to 2% RDEV."
- **NIST's accuracy by concentration** ([Newbury & Ritchie 2015](https://doi.org/10.1007/s10853-014-8685-2)): ±5% relative for major constituents (>10 wt%), ±10% for minor (1–10 wt%) and ±25% for trace (0.1–1 wt%). Mg at 0.2–0.45 wt% is in the trace band.
- **An interlaboratory EDS/WDS round robin** ([Jonnard et al. 2015](https://doi.org/10.48550/arxiv.1509.00261)) used a Ni-based glass, not Al.
  - At 5 kV, the mean errors grew. Fe, for example, came out −30%.

## 4. Gaps

- There is no CRM sold as AlSi10Mg or EN AC-43000.
- There is no same-method powder-vs-part analysis of AlSi10Mg.
- I found no open dataset of EDS spectra from Al alloys of known composition. Newbury & Ritchie 2024 mention a supporting database, but its location and whether it covers Al were not confirmed.
