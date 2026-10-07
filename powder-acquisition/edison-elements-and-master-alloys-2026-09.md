# Edison Scientific — Claim-by-Claim Corroboration of the Issue #161 Feedstock Recommendations

> Edison Scientific `job-futurehouse-paperqa3-high` (PaperQA, high effort). Task ID `376e52f5-05e7-48f5-92e7-3d3d8e4178e4`. Retrieved 2026-09-09. 37 sources cited of 98 contexts retrieved.
>
> This is the **raw, unedited** Edison output. The distilled verdicts live in [`edison-corroboration-2026-09.md`](edison-corroboration-2026-09.md).

<details>
<summary>Query as submitted</summary>

```
We are purchasing elemental and master-alloy feedstock to make ~100 g experimental aluminium alloys
by ULTRASONIC ATOMIZATION (induction melting under argon, melt dripped onto a vibrating sonotrode) to make
LPBF powder. Base is aluminium; additions are Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc, Li, Er, Zn, Sn,
each up to a few wt.%. Please CORROBORATE OR REFUTE the following specific claims, one by one, with
citations and quantitative evidence, and flag any that the literature contradicts:

CLAIM A (purity). For feedstock that is fully remelted before atomization, 99.9 % (3N) purity is
sufficient for Mn, Cr, Si, Cu, Zn, Ti, Ni, Fe, Sn and Ce, whereas the aluminium base and the L1_2-forming
microalloying elements Zr, Sc and Er justify higher purity (99.99 %), because oxide and tramp impurities
in those specifically degrade Al3(Sc,Zr,Er) precipitation. Is there quantitative evidence for a purity
threshold? Which impurities actually matter in Al LPBF alloys (Fe, Si, O, H, N, C), and at what levels do
they measurably degrade LPBF properties (porosity, hot cracking, strength)?

CLAIM B (oxygen dominates). The oxygen carried in on the feedstock's native surface oxide (which scales
roughly as 6*delta/d for particle diameter d) is a more important contaminant than the metallic impurity
level, so a coarse 99.7 % aluminium feedstock delivers a cleaner melt than a fine 99.99 % aluminium
powder. What oxygen levels are actually measured on Al powders of different size cuts, and what oxygen
content is specified/acceptable for LPBF Al powder? What is the oxide-film thickness on Al powder?

CLAIM C (coarse feedstock). Since everything is remelted, feedstock should be as coarse as practical
(150-300 um, granules or shot), not LPBF-grade 15-45 um, to reduce surface oxide, adsorbed moisture,
hydrogen porosity and dust-explosion risk. Any counter-evidence (e.g. dissolution kinetics or segregation
favouring finer feedstock)?

CLAIM D (master alloys). Li must be added as an Al-Li master alloy, and Zr, Sc, Er, Ce and Ti are better
added as Al-based master alloys (Al-10Zr, Al-2Sc, Al-5/10Er, Al-10/20Ce, Al-5Ti-1B or Al-10Ti) than as
elemental powder, for reasons of oxidation, dissolution kinetics and safety. Quantify: dissolution times
and temperatures for elemental Ti, Zr, Cr, Fe, Ni powders versus the corresponding master alloys in a
molten Al bath; recovery/assimilation yields; oxide inclusion content. Is there evidence that master-alloy
addition gives better recovery or finer/more uniform Al3X dispersoids than elemental addition?

CLAIM E (dissolution, not melting). Titanium does not need to be melted; it dissolves into liquid Al far
below its 1668 C melting point, and the binding temperature is the ALLOY LIQUIDUS: approximately 791 C at
0.5 wt.% Ti, 868 C at 1 wt.%, 954 C at 2 wt.% Ti, with atomization run at liquidus + 100-150 C superheat.
Corroborate these liquidus values and the recommended superheat for ultrasonic atomization of Al alloys.
Same question for Zr (reported 815 / 894 / 986 C at 0.5 / 1 / 2 wt.% Zr) and for Cr, Fe, Ni additions.
How long, and at what temperature and stirring, must an Al melt be held to fully dissolve elemental Ti or
Zr powder, and what happens to undissolved dense Al3Ti / Al3Zr particles (settling, atomization defects)?

CLAIM F (volatile losses). Mg, Zn and Li evaporate significantly from Al melts at 900-1100 C and should be
over-charged by 5-15 %, whereas Mn losses are oxidation/dross losses rather than evaporation. Quantify
measured evaporation losses of Mg, Zn and Li from small Al melts under argon versus temperature and hold
time, and the recommended over-charge. Is the recommendation to keep Zn out of Ti-bearing compositions
(because Zn boils at 907 C, below the liquidus of Al-1.3 wt.% Ti) supported?

CLAIM G (erbium bounds). For an Al-Zr-Er(-Sc/Ni) LPBF alloy design campaign, a useful Er composition range
is 0 to about 3 wt.% Er, given that the equilibrium solid solubility of Er in Al is only ~0.28 wt.%
(0.046 at.%), the Al-Al3Er eutectic is at ~6 wt.% Er, and rapid solidification allows large supersaturation.
What Er (and Sc, Zr) contents are actually used in the published additively manufactured Al-Er alloys, and
what is the optimum? Do the same for Sc, Zr, Ce and Mn upper bounds in LPBF Al alloys.

CLAIM H (contamination from the process). Ultrasonic atomization sonotrode erosion contaminates the powder
(Ti or Mo pickup has been reported); and hydrogen pickup rises with melt temperature. Quantify sonotrode
contamination levels reported for ultrasonically atomized Al alloys and any recommended mitigation.

Please be explicit about which claims the literature supports, which are unsupported but plausible, and
which are contradicted.
```

</details>

---

Question: We are purchasing elemental and master-alloy feedstock to make ~100 g experimental aluminium alloys
by ULTRASONIC ATOMIZATION (induction melting under argon, melt dripped onto a vibrating sonotrode) to make
LPBF powder. Base is aluminium; additions are Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc, Li, Er, Zn, Sn,
each up to a few wt.%. Please CORROBORATE OR REFUTE the following specific claims, one by one, with
citations and quantitative evidence, and flag any that the literature contradicts:

CLAIM A (purity). For feedstock that is fully remelted before atomization, 99.9 % (3N) purity is
sufficient for Mn, Cr, Si, Cu, Zn, Ti, Ni, Fe, Sn and Ce, whereas the aluminium base and the L1_2-forming
microalloying elements Zr, Sc and Er justify higher purity (99.99 %), because oxide and tramp impurities
in those specifically degrade Al3(Sc,Zr,Er) precipitation. Is there quantitative evidence for a purity
threshold? Which impurities actually matter in Al LPBF alloys (Fe, Si, O, H, N, C), and at what levels do
they measurably degrade LPBF properties (porosity, hot cracking, strength)?

CLAIM B (oxygen dominates). The oxygen carried in on the feedstock's native surface oxide (which scales
roughly as 6*delta/d for particle diameter d) is a more important contaminant than the metallic impurity
level, so a coarse 99.7 % aluminium feedstock delivers a cleaner melt than a fine 99.99 % aluminium
powder. What oxygen levels are actually measured on Al powders of different size cuts, and what oxygen
content is specified/acceptable for LPBF Al powder? What is the oxide-film thickness on Al powder?

CLAIM C (coarse feedstock). Since everything is remelted, feedstock should be as coarse as practical
(150-300 um, granules or shot), not LPBF-grade 15-45 um, to reduce surface oxide, adsorbed moisture,
hydrogen porosity and dust-explosion risk. Any counter-evidence (e.g. dissolution kinetics or segregation
favouring finer feedstock)?

CLAIM D (master alloys). Li must be added as an Al-Li master alloy, and Zr, Sc, Er, Ce and Ti are better
added as Al-based master alloys (Al-10Zr, Al-2Sc, Al-5/10Er, Al-10/20Ce, Al-5Ti-1B or Al-10Ti) than as
elemental powder, for reasons of oxidation, dissolution kinetics and safety. Quantify: dissolution times
and temperatures for elemental Ti, Zr, Cr, Fe, Ni powders versus the corresponding master alloys in a
molten Al bath; recovery/assimilation yields; oxide inclusion content. Is there evidence that master-alloy
addition gives better recovery or finer/more uniform Al3X dispersoids than elemental addition?

CLAIM E (dissolution, not melting). Titanium does not need to be melted; it dissolves into liquid Al far
below its 1668 C melting point, and the binding temperature is the ALLOY LIQUIDUS: approximately 791 C at
0.5 wt.% Ti, 868 C at 1 wt.%, 954 C at 2 wt.% Ti, with atomization run at liquidus + 100-150 C superheat.
Corroborate these liquidus values and the recommended superheat for ultrasonic atomization of Al alloys.
Same question for Zr (reported 815 / 894 / 986 C at 0.5 / 1 / 2 wt.% Zr) and for Cr, Fe, Ni additions.
How long, and at what temperature and stirring, must an Al melt be held to fully dissolve elemental Ti or
Zr powder, and what happens to undissolved dense Al3Ti / Al3Zr particles (settling, atomization defects)?

CLAIM F (volatile losses). Mg, Zn and Li evaporate significantly from Al melts at 900-1100 C and should be
over-charged by 5-15 %, whereas Mn losses are oxidation/dross losses rather than evaporation. Quantify
measured evaporation losses of Mg, Zn and Li from small Al melts under argon versus temperature and hold
time, and the recommended over-charge. Is the recommendation to keep Zn out of Ti-bearing compositions
(because Zn boils at 907 C, below the liquidus of Al-1.3 wt.% Ti) supported?

CLAIM G (erbium bounds). For an Al-Zr-Er(-Sc/Ni) LPBF alloy design campaign, a useful Er composition range
is 0 to about 3 wt.% Er, given that the equilibrium solid solubility of Er in Al is only ~0.28 wt.%
(0.046 at.%), the Al-Al3Er eutectic is at ~6 wt.% Er, and rapid solidification allows large supersaturation.
What Er (and Sc, Zr) contents are actually used in the published additively manufactured Al-Er alloys, and
what is the optimum? Do the same for Sc, Zr, Ce and Mn upper bounds in LPBF Al alloys.

CLAIM H (contamination from the process). Ultrasonic atomization sonotrode erosion contaminates the powder
(Ti or Mo pickup has been reported); and hydrogen pickup rises with melt temperature. Quantify sonotrode
contamination levels reported for ultrasonically atomized Al alloys and any recommended mitigation.

Please be explicit about which claims the literature supports, which are unsupported but plausible, and
which are contradicted.

## Corroboration and Refutation of Claims A–H: Feedstock Selection for Ultrasonic Atomization of Al LPBF Alloys

### CLAIM A — Purity (3N vs 4N for L1₂-forming elements)

**Verdict: Plausible but not quantitatively supported by a documented purity threshold in the literature.**

The claim that 99.9% (3N) purity suffices for Mn, Cr, Si, Cu, Zn, Ti, Ni, Fe, Sn, and Ce, while 99.99% (4N) is justified for the Al base and L1₂-forming microalloying elements Zr, Sc, and Er, is physically reasonable but lacks direct experimental documentation of a purity-grade threshold. The equilibrium solid solubility of Zr in Al is approximately 0.0008 mole fraction (~0.07 wt%) (sajjad2018grainrefinementofa pages 31-38, sajjad2018grainrefinementof pages 31-38), while Er solubility is only ~0.05 wt% (lei2023grainrefinementof pages 9-12). At such low solubility levels, even small amounts of tramp impurities (Fe, Si) could compete for solute or form unwanted phases that consume Zr/Sc/Er or poison nucleation of Al₃(Sc,Zr,Er). Knipling et al. showed that the critical supersaturation for Al₃Zr nucleation requires only ~0.021 at.% Zr, so impurities at even modest levels could interfere with precipitation (knipling2007nucleationandprecipitation pages 9-10). However, no retrieved publication establishes a specific quantitative purity threshold (e.g., that 0.1% Fe in Zr feedstock degrades Al₃Zr precipitation by a measurable amount). The claim regarding impurities that matter in LPBF (Fe, Si, O, H) is well supported: oxygen content in virgin AlSi10Mg powder is ~0.067 wt% and rises to ~0.257 wt% after 96 h thermal aging, correlating with increased porosity and melt-pool instabilities (fedina2022influenceofalsi10mg pages 4-5, fedina2022influenceofalsi10mg pages 5-6). Oxygen pickup of ~120 ppm over five LPBF production cycles has also been reported (sargioti2025physicochemicalandtoxicological pages 2-4).

### CLAIM B — Oxygen Dominates Over Metallic Impurity

**Verdict: SUPPORTED in principle; quantitative data partially corroborate.**

The native oxide film on aluminium powder particles is approximately 2–4 nm thick (sun2006dependenceofsize pages 2-3, sun2006dependenceofsize pages 1-2). For a spherical particle with oxide thickness δ and diameter d, the oxygen mass fraction scales as ~6δρ_oxide/(dρ_Al). For LPBF-grade powder (d ~ 30 µm, δ ~ 3 nm), this gives ~0.04–0.07 wt% O, consistent with the measured 0.067 wt% O for virgin AlSi10Mg powder (fedina2022influenceofalsi10mg pages 4-5). For a coarse 300 µm particle, the oxygen contribution from surface oxide drops by ~10×, to ~0.004–0.007 wt% O. Thus, the claim that a coarse 99.7% Al feedstock delivers a cleaner melt (in terms of oxygen) than fine 99.99% powder is quantitatively plausible: the 0.3% metallic impurity of 99.7% Al is comparable to or less than the ~0.07% oxygen penalty from fine powder. Extended aging further increases oxygen dramatically — from 0.067% to 0.274% after 96 h exposure (fedina2022influenceofalsi10mg pages 5-6). No explicit oxygen specification for LPBF Al powder was found in the retrieved literature, but values below ~0.1 wt% O appear to be the practical norm for acceptable virgin powder.

### CLAIM C — Coarse Feedstock (150–300 µm) Preferred for Remelting

**Verdict: PARTIALLY SUPPORTED, with important counter-evidence on dissolution kinetics.**

The oxide-reduction, moisture-reduction, and dust-safety arguments for coarse feedstock are sound based on the surface-area scaling described above. However, dissolution kinetics provide significant counter-evidence. Razaz and Carlberg (2019) showed that the dissolution of Mn and Fe in molten Al at ~750°C is mass-transfer-controlled and strongly dependent on the surface area and shape of the additive (razaz2019onthedissolution pages 11-13, razaz2019onthedissolution pages 8-11, razaz2019onthedissolution pages 5-8). Mn flakes dissolved only ~90 µm in 8 minutes, and pure Mn flakes reached only ~0.4 wt% Mn after 9 minutes, whereas 80% Mn compacts (with more surface area from internal Al) reached 1.5 wt% Mn in the same time (razaz2019onthedissolution pages 2-3). Coarser feedstock pieces therefore dissolve substantially more slowly. For high-melting-point additions (Ti, Zr, Cr), which dissolve through intermediate intermetallic layers (Al₃Ti, Al₅Fe₂, Al₁₁Mn₄), dissolution time increases with particle size. Oxide films on the feedstock surface can also delay or prevent local reaction (razaz2019onthedissolution pages 13-14). Thus, while coarse feedstock is correct for the Al base metal, for refractory additions a compromise is needed — fine enough to dissolve in reasonable time, but not so fine as to introduce excessive oxide.

### CLAIM D — Master Alloys Preferred for Li, Zr, Sc, Er, Ce, Ti

**Verdict: SUPPORTED by dissolution kinetics evidence and standard foundry practice.**

The dissolution of elemental Mn in molten Al at 750°C proceeds through three intermediate intermetallic phases (γ₂, Al₁₁Mn₄, and µ), with the γ₂ layer acting as the principal diffusion barrier (razaz2019onthedissolution pages 13-14, razaz2019onthedissolution pages 3-5). Fe dissolution proceeds through Al₅Fe₂ and Al₃Fe phases (razaz2019onthedissolution pages 1-2, razaz2019onthedissolution pages 5-8). Critically, the addition of only 0.12 wt% Ti to the melt reduced the Mn dissolution rate by approximately 50% and decreased the total intermetallic layer thickness by about half (razaz2019onthedissolution pages 14-15, razaz2019onthedissolution pages 2-3). This demonstrates that in multicomponent alloys, dissolution interactions can severely retard elemental addition assimilation.

For Ti specifically, elemental Ti reacts with molten Al to form Al₃Ti (TiAl₃) as a thick brittle intermetallic layer during dissolution (shapiro2007brazingoftitanium pages 11-14, mackowiak1958astudyof pages 26-32). Pure molten Al reacts "very actively" with Ti and can cause substantial base-metal erosion during brazing (shapiro2007brazingoftitanium pages 9-11), but the dissolution is through intermetallic intermediates rather than direct alloying. Master alloys such as Al-5Ti-1B or Al-10Ti have Ti pre-dissolved, bypassing the slow intermetallic-mediated dissolution step. The claim that Li must be added as Al-Li master alloy is universally accepted in foundry practice due to Li's extreme reactivity with moisture and atmospheric gases.

### CLAIM E — Dissolution, Not Melting; Liquidus Values

**Verdict: SUPPORTED in principle. Specific liquidus values could not be independently verified from retrieved papers but are consistent with established phase diagrams.**

The fundamental claim that Ti (m.p. 1668°C) and Zr (m.p. 1855°C) dissolve into liquid Al far below their melting points is firmly established. Knipling et al. confirmed that both Al₃Ti and Al₃Zr form via peritectic reactions in the Al-rich corner of their respective phase diagrams (knipling2007nucleationandprecipitation pages 9-10, knipling2007nucleationandprecipitation pages 8-9). The Al-Ti peritectic occurs at ~665°C with ~1.0 wt% Ti, and the Al-Zr peritectic at ~660.5°C with ~0.28 wt% Zr — both only slightly above the Al melting point (660°C). Mackowiak's (1958) thesis on Ti dissolution kinetics in molten Al confirmed that dissolution proceeds via solid-liquid interaction with intermediate intermetallic formation, well below Ti's melting point (mackowiak1958astudyof pages 32-39, mackowiak1958astudyof pages 1-9). The claimed liquidus values (Al-0.5Ti: ~791°C, Al-1Ti: ~868°C, Al-2Ti: ~954°C; Al-0.5Zr: ~815°C, Al-1Zr: ~894°C, Al-2Zr: ~986°C) were not directly verified in the retrieved texts but are consistent with the steep liquidus slopes characteristic of peritectic Al-Ti and Al-Zr systems. The superheat recommendation of liquidus + 100–150°C is consistent with ultrasonic atomization practice: Bałasz et al. reported operating at approximately 1.3–1.5 times the absolute melting temperature for ultrasonic atomization (scientific2023comparisonofultrasonic pages 2-4).

### CLAIM F — Volatile Losses of Mg, Zn, Li

**Verdict: SUPPORTED qualitatively; quantitative evaporation rates not obtained from retrieved literature.**

The Żrodowski et al. (2021) cold crucible ultrasonic atomization study explicitly observed "high Mn and Zn evaporation, especially in the finest particles" during powder production. Bałasz et al. (2024) confirmed that Mn is the element expected to evaporate first from 316L stainless steel during ultrasonic atomization due to its lower boiling temperature, with measured Mn content varying from 1.08 to 3.88 wt% across different atomization runs (bałasz2024aninvestigationof pages 7-9). The Goncharov et al. (2026) study of HEA ultrasonic atomization showed Mn decreased from 10 to 8.9 wt% and Cu from 10 to 8.8 wt% during processing (goncharov2026designofcobaltfree pages 10-13). The claim that Zn (b.p. 907°C) is incompatible with high-Ti alloys (where the liquidus exceeds 907°C for >~1.3 wt% Ti) is thermodynamically sound but was not explicitly documented in the retrieved literature. The recommended 5–15% overcharge for Mg, Zn, and Li is standard foundry practice for Al casting but specific quantitative loss rates under argon at 900–1100°C were not found in the retrieved papers.

### CLAIM G — Erbium Composition Range (0–3 wt% Er)

**Verdict: PARTIALLY CONTRADICTED — the claimed upper bound of ~3 wt% Er is conservative; published LPBF alloys extend to 10 wt% Er.**

The equilibrium solid solubility of Er in Al is ~0.05 wt% (lei2023grainrefinementof pages 9-12), which is lower than the claimed ~0.28 wt% (0.046 at.%). The Al-Er eutectic composition has been reported at two values: ~6 wt% Er in the binary phase diagram according to Lei et al. (lei2023grainrefinementof pages 9-12), and ~12.7 wt% Er according to Li et al. (2026) who used it for near-eutectic alloy design (li2026strong3dprintedaluminium pages 5-10). The discrepancy likely reflects a difference between binary Al-Al₃Er eutectic (~6 wt% Er) and a broader compositional reference. Published LPBF Al-Er alloys extend well beyond 3 wt% Er: Li et al. (2026) processed Al-10Er (wt%) as a near-eutectic composition, and designed alloys Al-10Er-5Mg-0.6Sc-0.3Zr and Al-10Er-5Mg-1.2Sc-0.8Zr (li2026strong3dprintedaluminium pages 10-16). Thus, for an Al-Zr-Er alloy design campaign, 0–3 wt% Er is a useful microalloying range for precipitation strengthening, but the literature shows that substantially higher Er contents (up to ~10 wt%) are viable and advantageous for near-eutectic nano-skeleton approaches.

For the other elements in LPBF Al alloys: **Sc** is typically 0.6–0.8 wt% in Scalmalloy® (Al-4.6Mg-0.66Sc-0.42Zr-0.49Mn) (janus2025microstructureandmechanical pages 1-3), with the Al-Sc eutectic at ~0.5 wt% Sc (li2026strong3dprintedaluminium pages 5-10). **Zr** is typically 0.2–0.5 wt% in Scalmalloy-type alloys, with higher values (up to ~4.4 wt%) explored in some LPBF compositions (yang2025themicrostructureregulation pages 3-4). **Ce** is used at 6–16 wt% in LPBF near-eutectic alloys, with the Al-Ce eutectic at ~10 wt% Ce (plotkowski2024highstrengthaluminum pages 9-12, ajantiwalay2022influenceofmicrostructural pages 1-2); DuAlumin-3D uses ~9 wt% Ce (plotkowski2024highstrengthaluminum pages 1-9). **Mn** ranges from 0.3–0.8 wt% in Scalmalloy to ~4.9 wt% in some LPBF Al-Mn alloys (yang2025themicrostructureregulation pages 3-4, janus2025microstructureandmechanical pages 1-3).

### CLAIM H — Sonotrode Erosion Contamination

**Verdict: STRONGLY SUPPORTED by quantitative evidence.**

Goncharov et al. (2026) directly documented molybdenum contamination from sonotrode erosion during ultrasonic atomization of a high-entropy alloy powder. Mo was concentrated mainly in interdendritic regions of the atomized particles, with an average Mo content of 2.6 wt% in the modified powder composition — a substantial and unintended contamination level (goncharov2026designofcobaltfree pages 10-13). Sojoodi et al. (2025) described sonotrode attrition as a known contamination pathway in ultrasonic plasma atomization, noting that high-frequency oscillation degrades the sonotrode and can introduce metallic impurities into the melt (sojoodi2025integrationofcircular pages 27-28). Recommended mitigations include selecting chemically inert and wear-resistant sonotrode materials, improved sonotrode designs, and using ultra-high-purity argon (99.9999%) to minimize atmospheric contamination (sojoodi2025integrationofcircular pages 27-28). The claim about hydrogen pickup increasing with melt temperature is well established in aluminium foundry metallurgy, though specific quantitative data for ultrasonic atomization were not found in the retrieved papers. For Al alloys specifically, the Żrodowski et al. (2021) study observed significant evaporation of Mn and Zn in the finest atomized fractions, confirming that compositional changes during ultrasonic atomization are a real concern beyond just sonotrode contamination.

---

### Summary Assessment

| Claim | Topic | Verdict |
|-------|-------|---------|
| A | Purity 3N vs 4N | **Plausible but unsupported** by a documented quantitative threshold |
| B | Oxygen dominates | **Supported** — oxide film ~2–4 nm; ~0.067 wt% O for 30 µm powder |
| C | Coarse feedstock | **Partially supported** — correct for Al base, but dissolution kinetics counter for refractory additions |
| D | Master alloys | **Supported** — dissolution of elemental Mn/Fe/Ti is slow, intermetallic-mediated |
| E | Dissolution not melting | **Supported** — Ti/Zr dissolve far below their melting points via peritectic reactions |
| F | Volatile losses | **Supported qualitatively** — Mn/Zn evaporation confirmed; specific rates not quantified |
| G | Er bounds 0–3 wt% | **Partially contradicted** — literature extends to 10 wt% Er; Er solubility is 0.05 wt%, not 0.28 wt% |
| H | Sonotrode contamination | **Strongly supported** — Mo pickup of 2.6 wt% documented |


References

1. (sajjad2018grainrefinementofa pages 31-38): A Sajjad. Grain refinement of al4cuti alloy with zirconium, scandium and erbium. Unknown journal, 2018.

2. (sajjad2018grainrefinementof pages 31-38): A Sajjad. Grain refinement of al4cuti alloy with zirconium, scandium and erbium. Unknown journal, 2018.

3. (lei2023grainrefinementof pages 9-12): Zhiguo Lei, Shengping Wen, Hui Huang, Wu Wei, and Zuoren Nie. Grain refinement of aluminum and aluminum alloys by sc and zr. Metals, 13:751, Apr 2023. URL: https://doi.org/10.3390/met13040751, doi:10.3390/met13040751. This article has 74 citations.

4. (knipling2007nucleationandprecipitation pages 9-10): Keith E. Knipling, David C. Dunand, and David N. Seidman. Nucleation and precipitation strengthening in dilute al-ti and al-zr alloys. Metallurgical and Materials Transactions A, 38:2552-2563, Sep 2007. URL: https://doi.org/10.1007/s11661-007-9283-6, doi:10.1007/s11661-007-9283-6. This article has 281 citations.

5. (fedina2022influenceofalsi10mg pages 4-5): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

6. (fedina2022influenceofalsi10mg pages 5-6): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

7. (sargioti2025physicochemicalandtoxicological pages 2-4): Nikoletta Sargioti, Leonidas Karavias, Leonidas Gargalis, Anna Karatza, Elias P. Koumoulos, and Evangelia K. Karaxi. Physicochemical and toxicological properties of particles emitted from scalmalloy during the lpbf process. Toxics, 13:398, May 2025. URL: https://doi.org/10.3390/toxics13050398, doi:10.3390/toxics13050398. This article has 5 citations.

8. (sun2006dependenceofsize pages 2-3): Juan Sun, Michelle L. Pantoya, and Sindee L. Simon. Dependence of size and size distribution on reactivity of aluminum nanoparticles in reactions with oxygen and moo3. Thermochimica Acta, 444:117-127, May 2006. URL: https://doi.org/10.1016/j.tca.2006.03.001, doi:10.1016/j.tca.2006.03.001. This article has 220 citations and is from a peer-reviewed journal.

9. (sun2006dependenceofsize pages 1-2): Juan Sun, Michelle L. Pantoya, and Sindee L. Simon. Dependence of size and size distribution on reactivity of aluminum nanoparticles in reactions with oxygen and moo3. Thermochimica Acta, 444:117-127, May 2006. URL: https://doi.org/10.1016/j.tca.2006.03.001, doi:10.1016/j.tca.2006.03.001. This article has 220 citations and is from a peer-reviewed journal.

10. (razaz2019onthedissolution pages 11-13): Ghadir Razaz and Torbjörn Carlberg. On the dissolution process of manganese and iron in molten aluminum. Metallurgical and Materials Transactions A, 50:1873-1887, Jan 2019. URL: https://doi.org/10.1007/s11661-019-05120-4, doi:10.1007/s11661-019-05120-4. This article has 11 citations.

11. (razaz2019onthedissolution pages 8-11): Ghadir Razaz and Torbjörn Carlberg. On the dissolution process of manganese and iron in molten aluminum. Metallurgical and Materials Transactions A, 50:1873-1887, Jan 2019. URL: https://doi.org/10.1007/s11661-019-05120-4, doi:10.1007/s11661-019-05120-4. This article has 11 citations.

12. (razaz2019onthedissolution pages 5-8): Ghadir Razaz and Torbjörn Carlberg. On the dissolution process of manganese and iron in molten aluminum. Metallurgical and Materials Transactions A, 50:1873-1887, Jan 2019. URL: https://doi.org/10.1007/s11661-019-05120-4, doi:10.1007/s11661-019-05120-4. This article has 11 citations.

13. (razaz2019onthedissolution pages 2-3): Ghadir Razaz and Torbjörn Carlberg. On the dissolution process of manganese and iron in molten aluminum. Metallurgical and Materials Transactions A, 50:1873-1887, Jan 2019. URL: https://doi.org/10.1007/s11661-019-05120-4, doi:10.1007/s11661-019-05120-4. This article has 11 citations.

14. (razaz2019onthedissolution pages 13-14): Ghadir Razaz and Torbjörn Carlberg. On the dissolution process of manganese and iron in molten aluminum. Metallurgical and Materials Transactions A, 50:1873-1887, Jan 2019. URL: https://doi.org/10.1007/s11661-019-05120-4, doi:10.1007/s11661-019-05120-4. This article has 11 citations.

15. (razaz2019onthedissolution pages 3-5): Ghadir Razaz and Torbjörn Carlberg. On the dissolution process of manganese and iron in molten aluminum. Metallurgical and Materials Transactions A, 50:1873-1887, Jan 2019. URL: https://doi.org/10.1007/s11661-019-05120-4, doi:10.1007/s11661-019-05120-4. This article has 11 citations.

16. (razaz2019onthedissolution pages 1-2): Ghadir Razaz and Torbjörn Carlberg. On the dissolution process of manganese and iron in molten aluminum. Metallurgical and Materials Transactions A, 50:1873-1887, Jan 2019. URL: https://doi.org/10.1007/s11661-019-05120-4, doi:10.1007/s11661-019-05120-4. This article has 11 citations.

17. (razaz2019onthedissolution pages 14-15): Ghadir Razaz and Torbjörn Carlberg. On the dissolution process of manganese and iron in molten aluminum. Metallurgical and Materials Transactions A, 50:1873-1887, Jan 2019. URL: https://doi.org/10.1007/s11661-019-05120-4, doi:10.1007/s11661-019-05120-4. This article has 11 citations.

18. (shapiro2007brazingoftitanium pages 11-14): AE Shapiro and YA Flom. Brazing of titanium at temperatures below 800^ oc: review and prospective applications. Unknown journal, 2007.

19. (mackowiak1958astudyof pages 26-32): J MacKowiak. A study of the kinetics of dissolution of titanium solid in molten aluminium. Unknown journal, 1958.

20. (shapiro2007brazingoftitanium pages 9-11): AE Shapiro and YA Flom. Brazing of titanium at temperatures below 800^ oc: review and prospective applications. Unknown journal, 2007.

21. (knipling2007nucleationandprecipitation pages 8-9): Keith E. Knipling, David C. Dunand, and David N. Seidman. Nucleation and precipitation strengthening in dilute al-ti and al-zr alloys. Metallurgical and Materials Transactions A, 38:2552-2563, Sep 2007. URL: https://doi.org/10.1007/s11661-007-9283-6, doi:10.1007/s11661-007-9283-6. This article has 281 citations.

22. (mackowiak1958astudyof pages 32-39): J MacKowiak. A study of the kinetics of dissolution of titanium solid in molten aluminium. Unknown journal, 1958.

23. (mackowiak1958astudyof pages 1-9): J MacKowiak. A study of the kinetics of dissolution of titanium solid in molten aluminium. Unknown journal, 1958.

24. (scientific2023comparisonofultrasonic pages 2-4): International Scientific, B. Bałasz, M. Bielecki, W. Gulbiński, and Ł. Słoboda. Comparison of ultrasonic and other atomization methods in metal powder production. Journal of Achievements in Materials and Manufacturing Engineering, 116:11-24, Jan 2023. URL: https://doi.org/10.5604/01.3001.0016.3393, doi:10.5604/01.3001.0016.3393. This article has 37 citations.

25. (bałasz2024aninvestigationof pages 7-9): Błażej Bałasz, Łukasz Żurawski, Dorota Laskowska, Nataliya Muts, and Andriana Ivanushko. An investigation of the metal powder ultrasound atomisation process of 316l stainless steel. Materials, 17:5642, Nov 2024. URL: https://doi.org/10.3390/ma17225642, doi:10.3390/ma17225642. This article has 11 citations.

26. (goncharov2026designofcobaltfree pages 10-13): Ivan Goncharov, Vera Popovich, Marcel Sluiter, Anatoly Popovich, and Maurizio Vedani. Design of cobalt-free high-entropy alloy binder for wc-base cemented carbides. Metals, 16:318, Mar 2026. URL: https://doi.org/10.3390/met16030318, doi:10.3390/met16030318. This article has 1 citations.

27. (li2026strong3dprintedaluminium pages 5-10): Yang Li, Tingting Chen, Shengyi Zhong, Haixing Fang, Pucong Sheng, Siming Ma, Han Chen, Yuchi Cui, Gang Ji, Yihao Wang, Yirui Chang, Lei Hu, Mingliang Wang, Shixin Nie, Haowei Wang, and Zhe Chen. Strong 3d-printed aluminium reinforced with ductile-transformable eutectic nano-skeleton. Nature Communications, Apr 2026. URL: https://doi.org/10.1038/s41467-026-72256-4, doi:10.1038/s41467-026-72256-4. This article has 0 citations and is from a highest quality peer-reviewed journal.

28. (li2026strong3dprintedaluminium pages 10-16): Yang Li, Tingting Chen, Shengyi Zhong, Haixing Fang, Pucong Sheng, Siming Ma, Han Chen, Yuchi Cui, Gang Ji, Yihao Wang, Yirui Chang, Lei Hu, Mingliang Wang, Shixin Nie, Haowei Wang, and Zhe Chen. Strong 3d-printed aluminium reinforced with ductile-transformable eutectic nano-skeleton. Nature Communications, Apr 2026. URL: https://doi.org/10.1038/s41467-026-72256-4, doi:10.1038/s41467-026-72256-4. This article has 0 citations and is from a highest quality peer-reviewed journal.

29. (janus2025microstructureandmechanical pages 1-3): K. Janus, A. Jarzębska, A. Wójcik, A. Garbacz-Klempka, J. Piekło, S. Terlicka, M. Piękoś, J. J. Sobczak, O. Krasa, and Ł. Krawczyk. Microstructure and mechanical properties of scalmalloy® produced by selective laser melting in term of long-term applications. Archives of Civil and Mechanical Engineering, May 2025. URL: https://doi.org/10.1007/s43452-025-01242-2, doi:10.1007/s43452-025-01242-2. This article has 4 citations.

30. (yang2025themicrostructureregulation pages 3-4): Wen-Bo Yang, Lei Zhan, Lin Liu, Fan-Xu Meng, Run Zhang, Kadiredan Tuerxun, Xing-Rui Zhao, Bai-Xin Dong, Shi-Li Shu, Tian-Shu Liu, Hong-Yu Yang, Feng Qiu, and Qi-Chuan Jiang. The microstructure regulation mechanism and future application of aluminum alloys manipulated by nanocrystalline structures formed by in situ amorphous crystallization. Sep 2025. URL: https://doi.org/10.3390/ma18174206, doi:10.3390/ma18174206. This article has 5 citations.

31. (plotkowski2024highstrengthaluminum pages 9-12): Alex Plotkowski, Ryan Dehoff, and Russ Cochran. High strength aluminum additive manufacturing. ArXiv, Feb 2024. URL: https://doi.org/10.2172/2301648, doi:10.2172/2301648. This article has 1 citations.

32. (ajantiwalay2022influenceofmicrostructural pages 1-2): Tanvi Ajantiwalay, Richard Michi, Christian Roach, Amit Shyam, Alex Plotkowski, and Arun Devaraj. Influence of microstructural heterogeneities on small-scale mechanical properties of an additively manufactured al-ce-ni-mn alloy. Dec 2022. URL: https://doi.org/10.1016/j.addlet.2022.100092, doi:10.1016/j.addlet.2022.100092. This article has 11 citations and is from a peer-reviewed journal.

33. (plotkowski2024highstrengthaluminum pages 1-9): Alex Plotkowski, Ryan Dehoff, and Russ Cochran. High strength aluminum additive manufacturing. ArXiv, Feb 2024. URL: https://doi.org/10.2172/2301648, doi:10.2172/2301648. This article has 1 citations.

34. (sojoodi2025integrationofcircular pages 27-28): Mahyar Sojoodi, Alireza Behvar, Harsh Bajaj, Shiva Mohajerani, Saeedeh Vanaei, Nasrin Taheri Andani, Anwar Algamal, Fatemeh Ghasemibojd, Mahsa Beyk Khorasani, Ahu Celebi, and Mohammad Elahinia. Integration of circular economy into metal additive manufacturing: a review of ultrasonic plasma atomization for producing virgin and recycled niti powder. Shape Memory and Superelasticity, 12:5-45, Oct 2026. URL: https://doi.org/10.1007/s40830-025-00589-y, doi:10.1007/s40830-025-00589-y. This article has 6 citations.
