# q2-diamond-carbon-residue

**Query:** When soft metals such as aluminum alloys are metallographically polished with fine diamond suspensions (1, 0.25, 0.1 um; polycrystalline or monocrystalline; water- or glycol/oil-based carriers), how much diamond becomes embedded in the surface and how much carbon contamination remains after standard cleaning, as measured by SEM/EDS, EPMA, XPS, or Auger analysis? Please give quantitative values (e.g., embedded particle areal density, surface carbon atomic % or wt% by EDS at 5-15 kV). For comparison, what is the typical carbon signal on clean metal surfaces in SEM-EDS due to adventitious hydrocarbon and electron-beam-induced contamination, and how does it grow with dwell time? Does residual carbon of this magnitude bias quantitative EDS of Al, Si, Mg, or O (e.g., through absorption of soft X-rays), and how is it handled in quantification (excluding C from the fit, coating correction, plasma cleaning)?

**Task ID:** `0305fa08-3596-4b1c-9904-35fd7e2214fd`

---

Question: When soft metals such as aluminum alloys are metallographically polished with fine diamond suspensions (1, 0.25, 0.1 um; polycrystalline or monocrystalline; water- or glycol/oil-based carriers), how much diamond becomes embedded in the surface and how much carbon contamination remains after standard cleaning, as measured by SEM/EDS, EPMA, XPS, or Auger analysis? Please give quantitative values (e.g., embedded particle areal density, surface carbon atomic % or wt% by EDS at 5-15 kV). For comparison, what is the typical carbon signal on clean metal surfaces in SEM-EDS due to adventitious hydrocarbon and electron-beam-induced contamination, and how does it grow with dwell time? Does residual carbon of this magnitude bias quantitative EDS of Al, Si, Mg, or O (e.g., through absorption of soft X-rays), and how is it handled in quantification (excluding C from the fit, coating correction, plasma cleaning)?

# Diamond embedding and carbon contamination after polishing aluminum

## Bottom line

The literature retrieved does **not provide a defensible quantitative value** for either (i) embedded-diamond areal density or (ii) residual carbon by SEM-EDS, EPMA, XPS, or Auger after polishing aluminum with 1, 0.25, or 0.1 µm diamond suspensions and standard cleaning. In particular, no controlled study was found that separates polycrystalline from monocrystalline diamond or water-based from glycol/oil-based carrier. Thus, values such as “particles mm⁻²” or “C wt% at 5–15 kV” cannot presently be assigned from published evidence without making them up.

The closest aluminum preparation study used 3, 1, and 0.25 µm diamond paste with IPA lubrication. Typical final stages were 1 and 0.25 µm for 120–240 s at 5 N. Mechanical-only preparation left conspicuous scratches on pure Al; subsequent colloidal-silica polishing or brief electropolishing improved the surface. However, the study did not count retained diamond and did not report carbon in its EDS results. Its SEM imaging was mainly at 1 kV, not quantitative carbon EDS at 5–15 kV. (rychly2021pokročilémetodypřípravya pages 35-42, rychly2021pokročilémetodypřípravya pages 31-35, rychly2021pokročilémetodypřípravy pages 31-35, rychly2021pokročilémetodypřípravya pages 42-49)

This is an important negative result: reports that “abrasive may embed” and SEM images lacking obvious particles do not establish a numerical upper bound. Moreover, carbon detected after diamond polishing is not uniquely diamond—it can include carrier residue, mounting resin, fingerprints, pump hydrocarbons, ordinary adventitious carbon, and beam-deposited carbon.

The quantitative evidence that is available is summarized below.

| Evidence category | Material / conditions | Quantitative result | Evidence status and interpretation |
|---|---|---|---|
| Fine-diamond polishing of Al | Pure Al polished successively with 3, 1, and 0.25 µm diamond paste; representative final stages were 1 and 0.25 µm for 120–240 s at 5 N with IPA lubricant | **No embedded-diamond areal density and no post-cleaning C at% or wt% were reported.** Mechanical-only polishing still left visible scratches; subsequent colloidal-silica polishing or electropolishing improved the surface. No retrieved study supplied the requested values for 1, 0.25, or 0.1 µm mono/polycrystalline diamond or water/oil carriers. (rychly2021pokročilémetodypřípravya pages 31-35, rychly2021pokročilémetodypřípravy pages 31-35, rychly2021pokročilémetodypřípravya pages 42-49) | **Direct evidence gap.** These data establish relevant preparation conditions, not a numerical upper bound on embedded diamond. An EDS carbon percentage must not be inferred from the absence of reported particles or scratches. |
| Adventitious carbon on Al by XPS | Initially Ar-ion-cleaned Al with no detectable C 1s or O 1s; subsequent water-vapour and air exposure | Apparent carbon thickness was nearly zero through about 50 L exposure, approximately **0.3 nm at 10⁴ L**, remained near 0.3 nm through 10⁹ L water exposure and initially through 10¹² L air exposure, then ultimately reached about **1 nm**. (piao2002adventitiouscarbongrowth pages 1-2, piao2002adventitiouscarbongrowth pages 2-3) | **Direct XPS/model-derived film thickness.** Surface-sensitive XPS can show substantial C atomic percentage for a sub-nanometre overlayer, but the paper did not report a corresponding SEM-EDS wt%; the two quantities are not interchangeable. |
| X-ray-induced carbon growth in XPS | Al and Au–Al surfaces under Al Kα irradiation; approximately 6×10⁻⁶ Pa; 0–1200 min | Plotted apparent carbon thickness grew over a range of roughly **0–3 nm in 1200 min**; Au-rich Au–Al showed an approximately **fivefold higher** contamination rate than pure Al. Exact point-by-point values were not tabulated. (piao2002adventitiouscarbongrowth pages 4-4, piao2002adventitiouscarbongrowth pages 1-2) | **Direct trend with approximate graph-read range.** Demonstrates instrument- and surface-dependent irradiation growth, not a universal linear rate for SEM. |
| Electron-beam deposition | Uncleaned InAs/InGaAs in a 197 kV STEM, approximately 0.1 nA, generally 1 min exposures | Approximately **1–3×10⁸ C atoms deposited per minute**, equivalent to about **200 incident electrons per deposited C atom**; deposited amount per dose was approximately constant, so thickness increased more rapidly when the same dose was concentrated into a smaller scanned area. (griffiths2010quantificationofcarbon pages 4-5, griffiths2010quantificationofcarbon pages 1-4) | **Direct STEM measurement.** Useful dose-normalized benchmark, but not directly convertible to SEM-EDS C wt% without scan area, film geometry, accelerating voltage, detector response, and substrate interaction volume. |
| Plasma-cleaning effect on beam deposition | Ar/O₂ plasma cleaning before 197 kV STEM irradiation | **8 min** plasma cleaning reduced deposition by approximately **20×**, from about 200 to about **4,000 electrons per deposited C atom**. Removal followed exponential behavior, with fitted inverse time constants about **0.47 min⁻¹** for scanned films and **0.25 min⁻¹** for spot-grown pillars. (griffiths2010quantificationofcarbon pages 4-5, griffiths2010quantificationofcarbon pages 1-4) | **Direct measurement.** Supports plasma cleaning as mitigation, while showing that deposition is reduced rather than guaranteed to be zero. |
| FE-EPMA contamination growth and suppression | Pure Fe, 7 kV, 50 nA; 10 or 60 s point dwells; mapping at 20 ms/pixel for about 1300 s | With a liquid-N₂ trap alone, C–K intensity rose approximately linearly with cumulative irradiation. Heating to about **100 °C**, especially with plasma cleaning and trapping, kept C–K weak and nearly constant through approximately **1300 s**. Plasma cleaning improved carbon-analysis precision from roughly **0.1 to 0.01 mass% C**; this is analytical precision, not the surface’s residual C concentration. (yamashita2016noveltechniqueto pages 2-3, yamashita2016noveltechniqueto pages 6-6, yamashita2016noveltechniqueto pages 3-6, yamashita2016noveltechniqueto pages 1-2) | **Direct FE-EPMA behavior.** Confirms dwell-time-dependent contamination and effective suppression, but supplies no universal SEM-EDS baseline carbon wt%. |
| Carbon-film attenuation of Si Kα | Calculated transmission through carbon of density 2.7 g cm⁻³ | **10/20/40 nm C:** **99.903% / 99.807% / 99.615%** transmission. (donovan2014electronprobemicroanalysis pages 29-34) | **Calculated transmission.** Even 40 nm attenuates Si Kα by only about 0.385%; a 0.3–3 nm adventitious layer should therefore have negligible influence relative to ordinary EDS uncertainty. |
| Carbon-film attenuation of Al Kα | Same model | **10/20/40 nm C:** **99.849% / 99.699% / 99.400%** transmission. (donovan2014electronprobemicroanalysis pages 29-34) | **Calculated transmission.** Corresponding losses are about 0.151%, 0.301%, and 0.600%; nanometre-scale adventitious carbon should not materially bias routine bulk-Al EDS. |
| Carbon-film attenuation of Mg Kα | Same model | **10/20/40 nm C:** **99.756% / 99.512% / 99.027%** transmission. (donovan2014electronprobemicroanalysis pages 29-34) | **Calculated transmission.** Loss reaches about 0.973% at 40 nm but remains very small for a typical sub- to few-nanometre adventitious film. |
| Carbon-film attenuation of O Kα | Same model | **10/20/40 nm C:** **96.712% / 93.533% / 87.484%** transmission. (donovan2014electronprobemicroanalysis pages 29-34) | **Calculated transmission.** O Kα is much more sensitive: losses are about 3.29%, 6.47%, and 12.52%. By interpolation, a uniform 0.3–3 nm film implies roughly 0.1–1% O Kα attenuation, whereas thick beam-deposited spots or deliberate carbon coatings require matched coatings or an explicit coating/film correction. |


*Table: Quantitative evidence for adventitious and beam-induced carbon is contrasted with the unresolved lack of direct embedded-diamond measurements on polished aluminum. The table also shows why nanometre-scale carbon has little effect on Si, Al, or Mg K lines but can measurably attenuate O Kα.*

## What carbon signal should be expected on a nominally clean metal?

### Surface-sensitive XPS/Auger

A genuinely sputter-cleaned aluminum surface can have no detectable C 1s signal immediately after cleaning: approximately 5×10¹⁴ ions cm⁻² of 3-keV Ar ions removed both detectable C 1s and O 1s. Carbon then readsorbed. XPS modeling gave an apparent carbon overlayer of about 0.3 nm after 10⁴ L exposure and about 1 nm after sufficiently large air exposure. Under prolonged Al Kα irradiation, the plotted apparent carbon thickness extended over approximately 0–3 nm during 0–1200 min; an Au-rich Au–Al surface accumulated it approximately five times faster than pure Al. (piao2002adventitiouscarbongrowth pages 4-4, piao2002adventitiouscarbongrowth pages 1-2, piao2002adventitiouscarbongrowth pages 2-3)

These thicknesses are more transferable than a nominal XPS atomic percentage. Because XPS samples only the outer few nanometres, even a sub-nanometre hydrocarbon layer can constitute a large C atomic fraction in an XPS survey while representing a negligible fraction of the micrometre-scale SEM-EDS interaction volume. Consequently, an XPS C at% must not be compared directly with an EDS C wt%.

### SEM-EDS

There is **no universal “clean-metal carbon wt%” for SEM-EDS**. The apparent value depends strongly on accelerating voltage, take-off angle, detector window and low-energy efficiency, fitting model, interaction volume, whether carbon is included in normalization, analysis area, prior beam exposure, and contamination in the chamber. The retrieved literature did not support a robust numerical baseline such as “clean Al normally gives X wt% C at 10 kV.” Reporting such a number without a same-instrument blank would therefore be misleading.

For practical comparison, acquire a same-session spectrum from a freshly plasma-cleaned metal standard under identical voltage, current, geometry, live time, and scan area. Carbon that is spatially uniform and comparable with that blank is consistent with adventitious/chamber contamination; localized C-rich submicrometre features persisting under low-dose analysis are more consistent with particles or preparation residue. Raman, Auger, or carbon-bonding XPS is needed to identify diamond specifically—EDS detects elemental carbon but cannot distinguish diamond from hydrocarbon or amorphous carbon.

## Growth during electron irradiation

A quantitative high-vacuum STEM benchmark found approximately 1–3×10⁸ carbon atoms deposited in one minute at 197 kV and about 0.1 nA, equivalent to roughly 200 incident electrons per deposited carbon atom. The deposited volume per electron dose was approximately constant. Therefore, when the same dose was concentrated into a smaller scan area, the contamination became correspondingly thicker; the relevant independent variables are dose and irradiated area, not dwell time alone. Eight minutes of Ar/O₂ plasma cleaning reduced deposition approximately twentyfold, to about 4,000 electrons per deposited carbon atom. (griffiths2010quantificationofcarbon pages 4-5, griffiths2010quantificationofcarbon pages 1-4)

Those STEM rates should not be transferred numerically to an SEM because voltage, chamber condition, beam size, scan area, hydrocarbon supply, and specimen temperature differ. They do establish that beam-grown carbon can be substantial and approximately dose-dependent.

FE-EPMA gives a more microanalysis-specific result. On nominally carbon-free Fe at 7 kV and 50 nA, C-K intensity increased approximately linearly with cumulative irradiation using 10- or 60-s point dwells and a liquid-nitrogen trap. Heating the specimen to about 100 °C, especially together with plasma cleaning and cold trapping, kept C-K weak and nearly constant through approximately 1300 s. In mapping, 20-ms pixels still accumulated contamination over a roughly 1300-s total acquisition unless heating was used. (yamashita2016noveltechniqueto pages 2-3, yamashita2016noveltechniqueto pages 6-6)

Plasma cleaning improved FE-EPMA carbon-analysis precision from about 0.1 to 0.01 mass% C; that number is an analytical precision/detection-performance result, **not** a measured residual surface-carbon concentration. (yamashita2016noveltechniqueto pages 3-6, yamashita2016noveltechniqueto pages 1-2)

## Does this carbon bias Al, Si, Mg, or O quantification?

For ordinary adventitious films of approximately 0.3–3 nm, the effect on bulk Al, Si, and Mg K-line EDS at 5–15 kV is normally negligible compared with routine EDS uncertainty. Published transmissions through 10/20/40 nm of carbon are:

- Si Kα: 99.903/99.807/99.615%;
- Al Kα: 99.849/99.699/99.400%;
- Mg Kα: 99.756/99.512/99.027%;
- O Kα: 96.712/93.533/87.484%. (donovan2014electronprobemicroanalysis pages 29-34)

Thus, even 40 nm carbon suppresses Si, Al, and Mg Kα by only about 0.39%, 0.60%, and 0.97%, respectively. Scaling the thin-film attenuation to a uniform 0.3–3 nm adventitious layer implies losses much smaller than 0.1% for Si, roughly 0.005–0.05% for Al, and roughly 0.007–0.07% for Mg. These are approximate interpolations, not direct measurements.

O Kα is more vulnerable because of its much lower photon energy. The same interpolation gives approximately 0.1–1% attenuation for 0.3–3 nm carbon. A deliberate 10-nm carbon coating already reduces O Kα by about 3.3%, and 40 nm by about 12.5%. Thick, localized beam-deposited contamination can therefore bias oxygen appreciably even where Al, Si, and Mg remain nearly unaffected. (donovan2014electronprobemicroanalysis pages 29-34)

A second and often larger error occurs if non-bulk carbon is included as though it were a homogeneous constituent. Normalizing Al–Mg–Si–O–C to 100% then dilutes every genuine bulk constituent mathematically. For alloy analysis, a surface C signal should ordinarily be excluded from the bulk composition/normalization unless carbon is genuinely part of the material and is measured with appropriate standards and corrections. Excluding C removes this normalization artifact, but it does **not** undo physical absorption by a thick carbon film.

## Recommended analytical handling

1. **For Al–Si–Mg alloy composition:** fit the C peak if useful diagnostically, but exclude clearly extrinsic surface carbon from the reported bulk normalization. Report the raw or separately quantified C signal and the exclusion explicitly.
2. **For oxygen or low-voltage work:** avoid carbon coating if conductivity permits. If a coating is necessary, coat standards and unknowns together to the same measured thickness, or apply an explicit multilayer/coating absorption correction. EPMA guidance specifically emphasizes identical coating composition and thickness for standards and unknowns. (donovan2014electronprobemicroanalysis pages 29-34)
3. **Minimize beam deposition:** navigate and focus away from the analysis site; use rastered rather than prolonged stationary exposure; acquire low-dose spectra first; keep scan area, current, dwell, and acquisition order fixed when comparing specimens.
4. **Clean both specimen and chamber:** solvent/ultrasonic cleaning removes loose carrier residue but not necessarily embedded particles or strongly adsorbed hydrocarbons. Ar/O₂ plasma cleaning reduced measured beam deposition about twentyfold in one study. For trace-carbon EPMA, plasma cleaning plus a liquid-nitrogen trap and specimen heating near 100 °C was markedly more effective than a cold trap or short chamber-plasma treatment alone. (yamashita2016noveltechniqueto pages 2-3, griffiths2010quantificationofcarbon pages 4-5, griffiths2010quantificationofcarbon pages 1-4)
5. **Demonstrate diamond rather than merely carbon:** use correlated BSE/SE imaging and carbon mapping, followed by Raman or bonding-sensitive Auger/XPS at candidate particles. A useful reporting metric would be particle count per mm² with size bins, accompanied by blank-polished and plasma-cleaned controls. Bulk EDS alone cannot distinguish embedded diamond from carrier or beam contamination.

## Defensible conclusion

For the specified fine-diamond polishing conditions, published quantitative values for embedded diamond and post-cleaning carbon are presently **not established** in the retrieved literature. The best-supported comparison is that clean aluminum rapidly carries an adventitious carbon film on the order of approximately 0.3–1 nm, with irradiation-dependent growth potentially reaching a few nanometres; beam deposition is dose- and area-dependent and can be reduced by roughly twentyfold with plasma cleaning. Carbon films of this magnitude do not materially bias Al, Si, or Mg K-line EDS, but they can produce a small oxygen bias and become important when beam-grown or deliberately applied carbon reaches tens of nanometres. The main compositional danger in routine alloy EDS is often inappropriate inclusion of extrinsic C in the 100% normalization, rather than absorption of Al, Si, or Mg X-rays.

References

1. (rychly2021pokročilémetodypřípravya pages 35-42): D Rychlý. Pokročilé metody přípravy vzorků al a jeho slitin. Unknown journal, 2021.

2. (rychly2021pokročilémetodypřípravya pages 31-35): D Rychlý. Pokročilé metody přípravy vzorků al a jeho slitin. Unknown journal, 2021.

3. (rychly2021pokročilémetodypřípravy pages 31-35): D Rychlý. Pokročilé metody přípravy vzorků al a jeho slitin. Unknown journal, 2021.

4. (rychly2021pokročilémetodypřípravya pages 42-49): D Rychlý. Pokročilé metody přípravy vzorků al a jeho slitin. Unknown journal, 2021.

5. (piao2002adventitiouscarbongrowth pages 1-2): H. Piao and N. S. McIntyre. Adventitious carbon growth on aluminium and gold–aluminium alloy surfaces. Surface and Interface Analysis, 33:591-594, Jul 2002. URL: https://doi.org/10.1002/sia.1425, doi:10.1002/sia.1425. This article has 114 citations and is from a peer-reviewed journal.

6. (piao2002adventitiouscarbongrowth pages 2-3): H. Piao and N. S. McIntyre. Adventitious carbon growth on aluminium and gold–aluminium alloy surfaces. Surface and Interface Analysis, 33:591-594, Jul 2002. URL: https://doi.org/10.1002/sia.1425, doi:10.1002/sia.1425. This article has 114 citations and is from a peer-reviewed journal.

7. (piao2002adventitiouscarbongrowth pages 4-4): H. Piao and N. S. McIntyre. Adventitious carbon growth on aluminium and gold–aluminium alloy surfaces. Surface and Interface Analysis, 33:591-594, Jul 2002. URL: https://doi.org/10.1002/sia.1425, doi:10.1002/sia.1425. This article has 114 citations and is from a peer-reviewed journal.

8. (griffiths2010quantificationofcarbon pages 4-5): A J V Griffiths and T Walther. Quantification of carbon contamination under electron beam irradiation in a scanning transmission electron microscope and its suppression by plasma cleaning. ArXiv, 241:012017, Jul 2010. URL: https://doi.org/10.1088/1742-6596/241/1/012017, doi:10.1088/1742-6596/241/1/012017. This article has 88 citations.

9. (griffiths2010quantificationofcarbon pages 1-4): A J V Griffiths and T Walther. Quantification of carbon contamination under electron beam irradiation in a scanning transmission electron microscope and its suppression by plasma cleaning. ArXiv, 241:012017, Jul 2010. URL: https://doi.org/10.1088/1742-6596/241/1/012017, doi:10.1088/1742-6596/241/1/012017. This article has 88 citations.

10. (yamashita2016noveltechniqueto pages 2-3): Takako Yamashita, Yuji Tanaka, Masayasu Nagoshi, and Kiyohito Ishida. Novel technique to suppress hydrocarbon contamination for high accuracy determination of carbon content in steel by fe-epma. Scientific Reports, Jul 2016. URL: https://doi.org/10.1038/srep29825, doi:10.1038/srep29825. This article has 35 citations and is from a peer-reviewed journal.

11. (yamashita2016noveltechniqueto pages 6-6): Takako Yamashita, Yuji Tanaka, Masayasu Nagoshi, and Kiyohito Ishida. Novel technique to suppress hydrocarbon contamination for high accuracy determination of carbon content in steel by fe-epma. Scientific Reports, Jul 2016. URL: https://doi.org/10.1038/srep29825, doi:10.1038/srep29825. This article has 35 citations and is from a peer-reviewed journal.

12. (yamashita2016noveltechniqueto pages 3-6): Takako Yamashita, Yuji Tanaka, Masayasu Nagoshi, and Kiyohito Ishida. Novel technique to suppress hydrocarbon contamination for high accuracy determination of carbon content in steel by fe-epma. Scientific Reports, Jul 2016. URL: https://doi.org/10.1038/srep29825, doi:10.1038/srep29825. This article has 35 citations and is from a peer-reviewed journal.

13. (yamashita2016noveltechniqueto pages 1-2): Takako Yamashita, Yuji Tanaka, Masayasu Nagoshi, and Kiyohito Ishida. Novel technique to suppress hydrocarbon contamination for high accuracy determination of carbon content in steel by fe-epma. Scientific Reports, Jul 2016. URL: https://doi.org/10.1038/srep29825, doi:10.1038/srep29825. This article has 35 citations and is from a peer-reviewed journal.

14. (donovan2014electronprobemicroanalysis pages 29-34): J. Donovan, J. Goldstein, D. Newbury, P. Echlin, D. Joy, C. Fiori, and E. Lifshin. Electron probe microanalysis ( epma ). The IUPAC Compendium of Chemical Terminology, Feb 2014. URL: https://doi.org/10.1351/goldbook.e02006, doi:10.1351/goldbook.e02006. This article has 1 citations.
