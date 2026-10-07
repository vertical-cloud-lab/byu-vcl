Question: What published data exist on run-to-run (heat-to-heat, batch-to-batch or lot-to-lot) repeatability of gas atomization of metal powders (VIGA, EIGA, close-coupled or free-fall gas atomization; also plasma atomization) at nominally fixed settings? Report, with numbers and citations, the spread (standard deviation or coefficient of variation, and the number of runs or lots) in D10/D50/D90 or span, yield into the additive-manufacturing cut (15-45 um or 15-53 um), sphericity/morphology, oxygen and nitrogen content, flowability (Hall, Carney, rheometer) and apparent density. Include industrial lot-to-lot variability for AM powders (AlSi10Mg, Ti-6Al-4V, 316L, IN718), powder-variability studies for qualification (e.g. NIST, NASA, ASTM interlaboratory studies), and how many lots or runs those studies used. Also report any published guidance on how many replicate runs are needed to establish a process baseline before optimization.

# Run-to-Run Repeatability of Gas Atomization of Metal Powders for Additive Manufacturing: A Review of Published Data

## 1. Introduction and Scope

Published data on the true run-to-run (heat-to-heat, batch-to-batch, or lot-to-lot) repeatability of gas atomization at nominally fixed settings are remarkably scarce. Most studies in the literature either (i) compare containers or sub-samples drawn from a single production heat lot, (ii) compare powder states before and after reuse, or (iii) survey powders from different suppliers using different atomization equipment and settings. Each of these study designs conflates different sources of variability. The following sections synthesize the quantitative data that are available, organized by property category.

---

## 2. Particle Size Distribution (D10/D50/D90, Span)

### 2.1 Within-heat-lot (container-to-container) variability

The most rigorous published PSD-uniformity data come from a NIST study that examined containers of gas-atomized powder drawn from the same production heat lot. For **17-4 stainless steel** (4 containers), D10 = 24.4 ± 0.6 µm (CV ≈ 2.5%), D50 = 36.5 ± 0.2 µm (CV ≈ 0.55%), and D90 = 54.5 ± 0.8 µm (CV ≈ 1.5%), where uncertainties are one standard deviation across the four samples (slotwinski2014characterizationofmetal pages 8-12, slotwinski2014characterizationofmetal pages 6-8). For **CoCr** (15 containers from one heat lot, distributed for a NIST-managed AM round robin), D10 = 8.9 ± 0.4 µm (CV ≈ 4.5%), D50 = 23.0 ± 1.0 µm (CV ≈ 4.2%), and D90 = 44.7 ± 1.5 µm (CV ≈ 3.4%) (slotwinski2014characterizationofmetal pages 8-12). These values establish that container-to-container PSD variability within a single heat lot is typically below 5% CV for D50.

### 2.2 Between-sample variability (handling/storage studies)

Grubbs et al. (2022) characterized 19 numbered powder samples (Lots #0–#18) of **Al 5056** and **Ta** for AM. Across the 19 samples, Al 5056 showed D10 = 21.73 ± 0.29 µm (CV 1.3%), D50 = 37.46 ± 0.52 µm (CV 1.4%), D90 = 63.3 ± 2.82 µm (CV 4.5%), and span = 1.109 ± 0.065 (CV 5.9%). For Ta, the spread was markedly larger: D10 = 11.42 ± 0.72 µm (CV 6.3%), D50 = 26.36 ± 1.42 µm (CV 5.4%), D90 = 53.90 ± 8.34 µm (CV 15.5%), and span = 1.616 ± 0.261 (CV 16.2%) (grubbs2022explorationofthe pages 11-13). The large D90 and span CV for Ta indicates that the coarse tail of the distribution is the most variable parameter, a pattern also seen in other datasets.

### 2.3 Multi-supplier lot surveys (IN718)

A NASA study by Smith and Sudbrack (2017) characterized 19 powder lots of **IN718** sourced from 13+ commercial suppliers plus large-volume and recycled variants. D50 ranged from approximately 12.8 to 25.4 µm across the population (smith2017relationshipofpowder pages 1-7, smith2017relationshipofpowder pages 7-15). This range reflects the combined effect of different suppliers, atomization equipment, atomizing gas (Ar vs. N₂), and sieving practices, rather than fixed-setting atomizer repeatability. Ellis and Sudbrack (2019) used principal component analysis on 18 IN718 powders and found that powder size and shape descriptors captured approximately half the total variability in the dataset (ellis2019…feedstockvariability pages 6-10).

### 2.4 Powder reuse campaigns (Ti-6Al-4V ELI)

Cordova et al. (2023) studied Ti-6Al-4V ELI powder before and after approximately 10 PBF-LB build cycles across 6 consecutive build jobs. Virgin powder had D10 = 18.33 µm, D50 = 28.46 µm, D90 = 46.02 µm; after reuse, these shifted to D10 = 15.96 µm, D50 = 30.39 µm, D90 = 49.32 µm (cordova2023impactofpowder pages 4-7). Gibbons and van der Merwe (2026) reported a 175-cycle reuse campaign for Ti-6Al-4V ELI in a certified medical device facility, with PSD changes of no more than 2.1% net change over the campaign (gibbons2026alongitudinalstudy pages 3-5).

The detailed quantitative data are consolidated in the table below:

| Study/Reference | Material | Atomization Method | Number of Lots/Containers | Property | Mean Value | Standard Deviation | CV (%) | Notes |
|---|---|---:|---:|---|---:|---:|---:|---|
| Slotwinski et al. (2014), NIST (slotwinski2014characterizationofmetal pages 8-12, slotwinski2014characterizationofmetal pages 6-8) | 17-4 SS | Gas atomized | 4 containers; one production heat lot | D10 | 24.4 µm | 0.6 µm | 2.5 | Container-to-container SD reported by authors. |
| Slotwinski et al. (2014), NIST (slotwinski2014characterizationofmetal pages 8-12, slotwinski2014characterizationofmetal pages 6-8) | 17-4 SS | Gas atomized | 4 containers; one production heat lot | D50 | 36.5 µm | 0.2 µm | 0.55 | Container-to-container SD reported by authors. |
| Slotwinski et al. (2014), NIST (slotwinski2014characterizationofmetal pages 8-12, slotwinski2014characterizationofmetal pages 6-8) | 17-4 SS | Gas atomized | 4 containers; one production heat lot | D90 | 54.5 µm | 0.8 µm | 1.5 | Container-to-container SD reported by authors. |
| Slotwinski et al. (2014), NIST (slotwinski2014characterizationofmetal pages 6-8) | 17-4 SS | Gas atomized | 2 of 4 containers measured for density | Skeletal density | ≈7.877 g/cm³ | Measurement uncertainty ±0.005 g/cm³ | ≈0.064 | Individual results 7.878 and 7.875 g/cm³; helium-pycnometer density, not apparent density. |
| Slotwinski et al. (2014), NIST (slotwinski2014characterizationofmetal pages 8-12, slotwinski2014characterizationofmetal pages 6-8) | CoCr | Gas atomized | 15 containers; one production heat lot | D10 | 8.9 µm | 0.40 µm | 4.5 | Material was distributed for a NIST-managed AM round robin; variability is within one heat lot. |
| Slotwinski et al. (2014), NIST (slotwinski2014characterizationofmetal pages 8-12, slotwinski2014characterizationofmetal pages 6-8) | CoCr | Gas atomized | 15 containers; one production heat lot | D50 | 23.0 µm | 0.96 µm | 4.2 | Author summary rounded SD to 1.0 µm. |
| Slotwinski et al. (2014), NIST (slotwinski2014characterizationofmetal pages 8-12, slotwinski2014characterizationofmetal pages 6-8) | CoCr | Gas atomized | 15 containers; one production heat lot | D90 | 44.7 µm | 1.5 µm | 3.4 | Container-to-container SD reported by authors. |
| Slotwinski et al. (2014), NIST (slotwinski2014characterizationofmetal pages 6-8) | CoCr | Gas atomized | 3 of 15 containers measured for density | Skeletal density | ≈8.303 g/cm³ | Measurement uncertainty ±0.005 g/cm³ | ≈0.060 | Individual results 8.305, 8.301, and 8.304 g/cm³; not apparent density. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Al 5056 | Atomization route not established in cited extract | 19 numbered samples/lots | D10 | 21.726 µm | 0.286 µm | 1.3 | Pooled statistics for samples numbered 0–18; independence as production atomization lots was not established. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Al 5056 | Atomization route not established in cited extract | 19 numbered samples/lots | D50 | 37.457 µm | 0.519 µm | 1.4 | Same qualification caveat as above. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Al 5056 | Atomization route not established in cited extract | 19 numbered samples/lots | D90 | 63.3 µm | 2.824 µm | 4.5 | Upper-tail PSD varied more than D10 or D50. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Al 5056 | Atomization route not established in cited extract | 19 numbered samples/lots | Span | 1.109 | 0.065 | 5.9 | Span definition follows the source dataset. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Al 5056 | Atomization route not established in cited extract | 19 numbered samples/lots | Median sphericity | 0.965 | 0.000 | ≈0 | Reported precision indicates no resolved spread. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Ta | Atomization route not established in cited extract | 19 numbered samples/lots | D10 | 11.418 µm | 0.721 µm | 6.3 | Pooled statistics for samples numbered 0–18. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Ta | Atomization route not established in cited extract | 19 numbered samples/lots | D50 | 26.356 µm | 1.416 µm | 5.4 | Sample independence as atomization lots was not established. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Ta | Atomization route not established in cited extract | 19 numbered samples/lots | D90 | 53.902 µm | 8.343 µm | 15.5 | Large variation concentrated in the coarse tail. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Ta | Atomization route not established in cited extract | 19 numbered samples/lots | Span | 1.616 | 0.261 | 16.2 | Largest reported relative spread in this dataset. |
| Grubbs et al. (2022) (grubbs2022explorationofthe pages 11-13) | Ta | Atomization route not established in cited extract | 19 numbered samples/lots | Median sphericity | 0.931 | 0.001 | 0.11 | Very small morphology spread despite wider PSD variation. |
| Cordova et al. (2023) (cordova2023impactofpowder pages 4-7, cordova2023impactofpowder pages 3-4) | Ti-6Al-4V ELI | Atomized; specific route not stated in cited text | 2 powder states; virgin and composite reused after ≈10 cycles; 6 builds | D10 | Virgin 18.33; reused 15.96 µm | Not reported | Not reported | Reuse comparison, not independent atomization-lot repeatability. |
| Cordova et al. (2023) (cordova2023impactofpowder pages 4-7, cordova2023impactofpowder pages 3-4) | Ti-6Al-4V ELI | Atomized; specific route not stated in cited text | 2 powder states; 6 builds | D50 | Virgin 28.46; reused 30.39 µm | Not reported | Not reported | D50 increased 6.8% after reuse. |
| Cordova et al. (2023) (cordova2023impactofpowder pages 4-7, cordova2023impactofpowder pages 3-4) | Ti-6Al-4V ELI | Atomized; specific route not stated in cited text | 2 powder states; 6 builds | D90 | Virgin 46.02; reused 49.32 µm | Not reported | Not reported | D90 increased 7.2% after reuse. |
| Cordova et al. (2023) (cordova2023impactofpowder pages 4-7) | Ti-6Al-4V ELI | Atomized; specific route not stated in cited text | Virgin state | Oxygen | 0.110 wt.% | 0.004 wt.% | 3.6 | SD is analytical/sample repeatability, not between-lot SD. |
| Cordova et al. (2023) (cordova2023impactofpowder pages 4-7) | Ti-6Al-4V ELI | Atomized; specific route not stated in cited text | Reused state | Oxygen | 0.120 wt.% | 0.001 wt.% | 0.83 | Oxygen rose by 0.010 wt.% after reuse. |
| Cordova et al. (2023) (cordova2023impactofpowder pages 4-7) | Ti-6Al-4V ELI | Atomized; specific route not stated in cited text | Virgin state | Hall flow | 37 s | 3 s | 8.1 | Reused powder did not flow through the Hall funnel. |
| Cordova et al. (2023) (cordova2023impactofpowder pages 4-7) | Ti-6Al-4V ELI | Atomized; specific route not stated in cited text | Virgin state | Carney flow | 6.8 s | 0.4 s | 5.9 | Measurement SD, not atomization-run SD. |
| Cordova et al. (2023) (cordova2023impactofpowder pages 4-7) | Ti-6Al-4V ELI | Atomized; specific route not stated in cited text | Reused state | Carney flow | 12.0 s | 0.5 s | 4.2 | Longer discharge time than virgin powder. |
| Cordova et al. (2023) (cordova2023impactofpowder pages 4-7) | Ti-6Al-4V ELI | Atomized; specific route not stated in cited text | 2 powder states | Apparent density | 2.49 g/cm³ in both states | 0.01 g/cm³ each | 0.40 | No resolved change after reuse. |
| Smith & Sudbrack (2017), NASA (smith2017relationshipofpowder pages 1-7) | IN718 | Commercial gas atomization; Ar and N₂ atomized lots | 19 samples: 13 commercial, 3 large-volume, 3 recycled | D50 | Range ≈12.8–25.4 µm | Not reported | Not reported | Supplier/lot survey, not nominally fixed-settings atomizer repeatability. |
| Smith & Sudbrack (2017), NASA (smith2017relationshipofpowder pages 1-7) | IN718 | Commercial gas atomization; Ar and N₂ atomized lots | Unrecycled commercial and large-volume lots | Oxygen | Range 109–331 ppm | Not reported | Not reported | Chemistry varied among suppliers/lots. |
| Smith & Sudbrack (2017), NASA (smith2017relationshipofpowder pages 1-7) | IN718 | Commercial gas atomization; Ar and N₂ atomized lots | Unrecycled commercial and large-volume lots | Nitrogen | Range 25–1,395 ppm | Not reported | Not reported | N₂-atomized powders drove the upper values; V3/R3 reached 2,770 ppm in the extended set. |
| Ellis & Sudbrack (2019), NASA (ellis2019…feedstockvariability pages 6-10) | IN718 | Primarily commercial Ar gas atomization | 18 powders | Nitrogen | Mostly 100–200 ppm | Not reported | ≈10 stated variation | Source reports approximate variation, not a complete lot-level table or formal CV. |
| Anderson & Terpstra (2002) (anderson2002progresstowardgas pages 4-5) | 316L | High-pressure close-coupled gas atomization nozzle study | 2 replicate gas-flow measurements per selected condition | Gas mass-flow repeatability | — | — | Not reported | Spread from average: 10.05% for HPGA-IIIb ensemble nozzle, 2.65% for HPGA-I single jet, and 4.25% for HPGA-IIIb single jet; these are spreads, not CVs or powder-property repeatability. |
| Zhang et al. (2025) review (zhang2025researchprogresson pages 10-11, zhang2025researchprogresson pages 4-6) | Various alloys | VIGA | Number of runs not reported | Yield below 53 µm | ≈70% | Not reported | Not reported | Process-level literature value; includes particles below 15 µm and is not a 15–53 µm cut or run-to-run statistic. |
| Zhang et al. (2025) review (zhang2025researchprogresson pages 10-11) | Various alloys | EIGA | Number of runs not reported | Yield below 53 µm | 30–45% | Not reported | Not reported | Literature range across unspecified conditions, not fixed-setting repeatability. |
| Zhang et al. (2025) review (zhang2025researchprogresson pages 10-11) | Various alloys | Plasma atomization | Number of runs not reported | Yield below 53 µm | 32–40% | Not reported | Not reported | Literature range across unspecified conditions, not fixed-setting repeatability. |


*Table: Quantitative powder-property variability reported across production containers, lots, powder states, or replicate atomizer-flow measurements. Notes distinguish genuine between-unit variation from analytical repeatability, reuse studies, supplier surveys, and process-level yield ranges.*

---

## 3. Sphericity and Morphology

Quantitative lot-to-lot sphericity data are extremely limited. Grubbs et al. (2022) reported median sphericity of 0.965 ± 0.000 for Al 5056 and 0.931 ± 0.001 for Ta across 19 samples, indicating negligible resolved variability in this descriptor (grubbs2022explorationofthe pages 11-13). Gibbons and van der Merwe (2026) reported that particle elongation decreased by 2.9% over 175 reuse cycles and the form factor distribution narrowed around its unchanged mean (gibbons2026alongitudinalstudy pages 3-5). The Cordova et al. (2023) study noted by SEM observation that few morphological differences were apparent between virgin and reused Ti-6Al-4V ELI powder after 10 build cycles, with satellite particles being slightly less frequent in reused powder (cordova2023impactofpowder pages 4-7, cordova2023impactofpowder pages 3-4).

## 4. Oxygen and Nitrogen Content

### 4.1 Within-lot analytical repeatability

Cordova et al. (2023) reported virgin Ti-6Al-4V ELI oxygen at 0.110 ± 0.004 wt.% and nitrogen at 0.0020 ± 0.0002 wt.%, where the standard deviations are analytical measurement repeatability on a single batch (cordova2023impactofpowder pages 4-7). After approximately 10 build-reuse cycles, oxygen rose modestly to 0.120 ± 0.001 wt.%, remaining within the ASTM F3001 specification limit of 0.13 wt.% (cordova2023impactofpowder pages 4-7). Gibbons and van der Merwe (2026) found an 8.2% increase in powder oxygen concentration and a 25.1% increase in produced-material oxygen over 175 reuse cycles (gibbons2026alongitudinalstudy pages 3-5).

### 4.2 Multi-lot chemistry variability (IN718)

The NASA lot survey by Smith and Sudbrack (2017) found oxygen ranging from 109 to 331 ppm and nitrogen from 25 to 1,395 ppm across 19 IN718 powder lots, with the highest nitrogen values attributable to N₂-atomized powders (smith2017relationshipofpowder pages 1-7). Ellis and Sudbrack (2019) noted that most of 18 IN718 powders contained 100–200 ppm nitrogen with approximately 10% variation (ellis2019…feedstockvariability pages 6-10).

### 4.3 Multi-lot chemistry variability (Ti-6Al-4V)

Brika et al. (2020) compared three Ti-6Al-4V lots (one gas-atomized, two plasma-atomized) and found oxygen contents of 0.11, 0.12, and 0.11 wt.%, and nitrogen of 0.020, 0.004, and 0.020 wt.% (brika2020influenceofparticle pages 5-8). The nitrogen difference between gas-atomized and plasma-atomized lots was substantial.

## 5. Flowability (Hall, Carney, Rheometer) and Apparent Density

Cordova et al. (2023) reported Hall flow rate of 37 ± 3 s/50 g for virgin Ti-6Al-4V ELI powder (CV ≈ 8.1%), while the reused powder did not flow through the Hall funnel. Carney funnel flow was 6.8 ± 0.4 s for virgin (CV ≈ 5.9%) and 12 ± 0.5 s for reused powder (CV ≈ 4.2%). Apparent density was 2.49 ± 0.01 g/cm³ for both states (CV ≈ 0.4%), and tap density was 2.86 ± 0.05 g/cm³ (virgin) and 2.88 ± 0.02 g/cm³ (reused). The Hausner ratio was 1.15 in both states (cordova2023impactofpowder pages 4-7). These standard deviations represent analytical measurement repeatability on a given powder state, not atomization run-to-run variability.

Gibbons and van der Merwe (2026) found that over 175 reuse cycles, Hall flow rate decreased by 5.4% (improved) and apparent density increased by 0.8% (gibbons2026alongitudinalstudy pages 3-5).

NASA MSFC has invested in powder characterization for lot-to-lot comparison using Hall and Carney funnels per ASTM B212/B213/B417/B964 (mcelderry2022ampowderflowability pages 1-13), but the numerical lot-to-lot variability datasets from those programs have not been published in the open literature.

## 6. Yield into the AM-Grade Size Cut

Published yield data for the fine AM-grade fraction are reported at the process level rather than as batch-to-batch variability statistics. A review by Zhang et al. (2025) tabulated the following nominal yields for powder below 53 µm: **VIGA** ≈ 70%, **EIGA** ≈ 30–45%, and **plasma atomization** ≈ 32–40% (zhang2025researchprogresson pages 10-11). Close-coupled gas atomization (CCGA) generally provides higher yields of fine powder in the AM-relevant size range compared to free-fall gas atomization (FFGA) (pennacchio2026…stainlesssteel pages 44-47). No published study was found that reports the run-to-run standard deviation or CV of AM-cut yield at fixed atomization settings.

## 7. NIST, NASA, and ASTM Qualification Studies

The following table summarizes the key qualification-oriented powder variability studies identified:

| Study | Organization | Alloy | Number of Lots/Samples | Study Type | Key Findings |
|---|---|---|---:|---|---|
| Slotwinski et al. (2014) | NIST | 17-4 SS; CoCr | 4 containers of 17-4 SS; 15 containers of CoCr, each material from one heat lot | Powder-uniformity assessment and preparation for a NIST-managed AM round robin | Laser-diffraction PSD curves were indistinguishable within estimated measurement uncertainty of <1%. D50 was 36.5 ± 0.2 µm for 17-4 SS (CV 0.55%) and 23.0 ± 0.96 µm for CoCr (CV 4.2%). This measures container-to-container uniformity within a heat—not heat-to-heat repeatability. (slotwinski2014characterizationofmetal pages 8-12, slotwinski2014characterizationofmetal pages 6-8) |
| Smith & Sudbrack (2017) | NASA Glenn Research Center | IN718 | 19 powder samples: 13 commercial, 3 large-volume virgin, and 3 once-recycled | Industry lot-to-lot feedstock comparison supporting SLS/SLM Alloy 718 qualification research | Feedstock varied widely: plotted D50 values extended from about 12.8 to 25.4 µm; unrecycled-powder O ranged 109–331 ppm and N 25–1,395 ppm. After building and thermal processing, mean grain diameter ranged 19.5–90.3 µm and hardness 426–471 HV across powders. The population combines suppliers, atomization gases, volumes, and recycled states, so it is not a fixed-setting atomizer repeatability test. (smith2017relationshipofpowder pages 1-7, smith2017relationshipofpowder pages 7-15, smith2017relationshipofpowder pages 15-19) |
| Ellis & Sudbrack (2019) | NASA | IN718 | 18 powders | Principal-component analysis of feedstock variability | Size, shape, rheology, and packing descriptors showed broad variability; the leading PCA structure captured roughly half of dataset variability. Most powders contained about 100–200 ppm N, with approximately 10% variation reported. Nominal sieve ranges differed, so this is a sourced-powder qualification survey rather than replicate production at fixed settings. (ellis2019…feedstockvariability pages 6-10) |
| Cordova et al. (2023) | Additive Industries / Universidad Carlos III de Madrid | Ti-6Al-4V ELI | 2 powder states—virgin and composite reused after about 10 cycles—and 6 consecutive builds | Industrial batch repeatability during powder reuse | Relative density remained 99.6–100% over six builds, while dimensional deviations were generally within about 2%. Powder O increased from 0.110 ± 0.004 to 0.120 ± 0.001 wt.%; apparent density remained 2.49 ± 0.01 g/cm³. This is reuse/build repeatability, not independent atomization-lot repeatability. (cordova2023impactofpowder pages 7-9, cordova2023impactofpowder pages 4-7, cordova2023impactofpowder pages 3-4) |
| Grubbs et al. (2022) | Worcester Polytechnic Institute | Al 5056; Ta | 19 numbered samples per material (0–18) | Effects of repeated handling and environmental exposure on AM powder | Across the numbered samples, Al 5056 D50 was 37.457 ± 0.519 µm (CV 1.4%) and D90 63.3 ± 2.824 µm (CV 4.5%); Ta D50 was 26.356 ± 1.416 µm (CV 5.4%) and D90 53.902 ± 8.343 µm (CV 15.5%). These are pooled exposure/sample statistics; the source does not establish 19 independent atomization lots. (grubbs2022explorationofthe pages 11-13) |
| Brika et al. (2020) | ÉTS Montréal | Ti-6Al-4V | 3 lots: 1 gas-atomized and 2 plasma-atomized | Comparison of morphology/PSD effects on powder rheology and LPBF manufacturability | O values were 0.11, 0.12, and 0.11 wt.%; N values were 0.020, 0.004, and 0.020 wt.%. Because only one lot was gas-atomized and atomization routes differed, the inter-lot range cannot be interpreted as gas-atomizer run-to-run repeatability. (brika2020influenceofparticle pages 5-8) |
| ASTM F3049-14 / AM Standardization Roadmap (2017) | ASTM International / ANSI–America Makes | Various metal powders | No required lot count stated | Standard guide and standards-gap assessment | ASTM F3049 references established powder-metallurgy sampling practice, including ASTM B215. The roadmap emphasizes representative sampling, sampling frequency, batch-size considerations, and special treatment of reused/blended powder, but gives no minimum number of independent atomization heats or lots for qualification. (makes2017standardizationroadmapfor pages 100-103) |
| MSFC-STD-3716 framework / Glendening and Russell (2020) | NASA | Various AM metals | No minimum powder-lot count stated in the cited public presentation | AM process and hardware qualification framework | Requires a qualified material process, material-property suite, process-control reference distribution, witness testing, and statistical process control. The public framework does not prescribe a universal minimum number of powder lots or atomization runs for establishing the feedstock baseline. (glendening2020nasasplansfor pages 19-31) |
| McElderry & Boothe (2022) | NASA Marshall Space Flight Center | Various AM powders | Not reported | Powder acceptance, lot-to-lot comparison, and ASTM proficiency-testing capability | MSFC supports powder acceptance and lot comparison using PSD, morphology, flow, and density measurements and participates in ASTM proficiency testing. The presentation describes five laser-diffraction scans per sample but does not report a qualification lot count or production-level variability dataset. (mcelderry2022ampowderflowability pages 1-13) |


*Table: Published qualification-oriented studies vary from within-heat container checks to multi-supplier lot surveys and powder-reuse campaigns. The table separates their sample counts and quantitative findings from standards that require representative sampling or SPC but prescribe no universal minimum number of atomization lots.*

### 7.1 NIST studies

The landmark NIST study by Slotwinski et al. (2014) systematically characterized 15 containers of CoCr powder from one heat lot as preparation material for an interlaboratory AM round robin study, alongside 4 containers of 17-4 stainless steel (slotwinski2014characterizationofmetal pages 8-12, slotwinski2014characterizationofmetal pages 6-8). The NIST report by Cooke and Slotwinski (2012) reviewed the state of the art in metal-powder property testing for AM, establishing measurement methods and identifying gaps, but did not provide lot-to-lot production variability data (cooke2012propertiesofmetal pages 1-7).

### 7.2 NASA IN718 powder variability program

The most comprehensive published lot-to-lot comparison for a single AM alloy is the NASA program on SLM IN718, reported by Smith, Kloesel, and Sudbrack (2017) and Ellis and Sudbrack (2019). This program procured and characterized 19 powder lots from 13+ commercial suppliers (plus large-volume and recycled variants), built SLM test articles from each, and characterized microstructure (grain size 19.5–90.3 µm), porosity (void area fraction 0.011–0.276% after HIP/heat treatment), and hardness (426–471 HV, mostly 43–46 HRC) (smith2017relationshipofpowder pages 1-7, smith2017relationshipofpowder pages 7-15, smith2017relationshipofpowder pages 15-19). This represents a supplier-variability survey rather than a fixed-settings atomizer repeatability test.

### 7.3 NASA MSFC-STD-3716 and MSFC-SPEC-3717

NASA's AM qualification framework (MSFC-STD-3716) requires a Qualified Material Process (QMP), material property suite with process control reference distributions (PCRD), statistical process control (SPC), and witness testing for build-to-build equivalence (glendening2020nasasplansfor pages 19-31). The framework treats each AM machine as a foundry and requires SPC to sustain certification rationale. However, the public documentation does not prescribe a universal minimum number of powder lots or atomization heats for establishing the feedstock baseline (glendening2020nasasplansfor pages 19-31). NASA MSFC has developed powder acceptance and lot-to-lot comparison capabilities using PSD, morphology, flow, and density measurements (mcelderry2022ampowderflowability pages 1-13).

### 7.4 ASTM standards

ASTM F3049-14 ("Standard Guide for Characterizing Properties of Metal Powders Used for Additive Manufacturing Processes") references established powder-metallurgy sampling practices including ASTM B215 and MPIF Standard 01, but does not specify a required number of lots or heats for qualification (makes2017standardizationroadmapfor pages 100-103). The 2017 AM Standardization Roadmap identified the need for dedicated AM powder-sampling standards as a high-priority gap (makes2017standardizationroadmapfor pages 100-103).

## 8. Guidance on Number of Replicate Runs for Process Baseline

**No published standard or guideline was found that specifies a minimum number of replicate gas-atomization runs (heats, lots, or batches) needed to establish a process baseline before optimization.** This is a significant gap in the literature. The available evidence includes:

- Anderson and Terpstra (2002) performed 2 replicate gas mass-flow measurements at selected supply pressures for close-coupled HPGA nozzles and found spread from the average of 2.65% (single HPGA-I jet), 4.25% (single HPGA-IIIb C-D jet), and 10.05% (HPGA-IIIb ensemble nozzle at 6.9 MPa) (anderson2002progresstowardgas pages 4-5, anderson2002progresstowardgas pages 5-6). These are gas-only flow repeatability checks, not powder-property baselines.

- Marinucci (2023) used 4 initial atomization runs during process development for AlSi10Mg to investigate parameters, yield, crucible effects, and an unexpected pressure transient (marinucci2023developmentofalsi10mg pages 70-73). This was exploratory and not framed as a statistically justified baseline.

- The NASA MSFC SPC framework (glendening2020nasasplansfor pages 19-31) and ASTM F3049 (makes2017standardizationroadmapfor pages 100-103) both implicitly require sufficient data to construct process control reference distributions, but neither prescribes a specific sample size.

From a practical standpoint, the observed CVs in the literature suggest that D50 variability within a single heat lot is typically <5%, while between different suppliers or atomization settings it can exceed 50%. This implies that even a modest number of replicate heats (e.g., 5–10) at truly fixed settings should be sufficient to characterize D50 to useful precision, but no published study has validated this experimentally with a controlled atomization campaign.

## 9. Summary of Key Findings

1. **Container-to-container PSD uniformity** within a single gas-atomization heat lot is excellent: CV <5% for D10, D50, D90 (NIST data, n = 4 for 17-4SS, n = 15 for CoCr) (slotwinski2014characterizationofmetal pages 8-12).

2. **Between-sample PSD variability** (19 samples) ranges from CV 1.3–4.5% for spherical Al 5056 to CV 5.4–16.2% for angular Ta, with D90 and span being the most variable descriptors (grubbs2022explorationofthe pages 11-13).

3. **Multi-supplier lot-to-lot variability** for IN718 is very large: D50 ranges from ~13 to ~25 µm, oxygen from 109 to 331 ppm, nitrogen from 25 to 1,395 ppm across 19 lots from different commercial sources and atomization gases (smith2017relationshipofpowder pages 1-7).

4. **Oxygen pickup during powder reuse** is consistently reported: +0.01 wt.% over 10 cycles for Ti-6Al-4V ELI (cordova2023impactofpowder pages 4-7), +8.2% over 175 cycles (gibbons2026alongitudinalstudy pages 3-5), remaining within specification limits when managed properly.

5. **Flowability** (Hall, Carney) analytical repeatability CVs are 4–8% within a powder state (cordova2023impactofpowder pages 4-7); apparent density is very stable (CV ≈ 0.4%).

6. **Sphericity** shows negligible lot-to-lot variability when powder morphology is consistent (CV ≈ 0–0.1%) (grubbs2022explorationofthe pages 11-13).

7. **AM-grade yield** (<53 µm) is approximately 70% for VIGA, 30–45% for EIGA, and 32–40% for plasma atomization, but no run-to-run yield variability statistics have been published (zhang2025researchprogresson pages 10-11).

8. **No published standard** (ASTM F3049, NASA MSFC-STD-3716, or otherwise) specifies a minimum number of atomization heats or lots for process qualification (makes2017standardizationroadmapfor pages 100-103, glendening2020nasasplansfor pages 19-31). This is an identified standards gap.

9. The **absence of true fixed-settings, multi-heat atomization repeatability studies** in the open literature is itself a significant finding. Nearly all available data represent either within-lot uniformity, reuse campaigns, or multi-supplier surveys, none of which isolate atomizer run-to-run variability at constant settings.

References

1. (slotwinski2014characterizationofmetal pages 8-12): J. A. Slotwinski, E. J. Garboczi, P. E. Stutzman, C. F. Ferraris, S. S. Watson, and M. A. Peltz. Characterization of metal powders used for additive manufacturing. Journal of Research of the National Institute of Standards and Technology, 119:460, Oct 2014. URL: https://doi.org/10.6028/jres.119.018, doi:10.6028/jres.119.018. This article has 703 citations and is from a peer-reviewed journal.

2. (slotwinski2014characterizationofmetal pages 6-8): J. A. Slotwinski, E. J. Garboczi, P. E. Stutzman, C. F. Ferraris, S. S. Watson, and M. A. Peltz. Characterization of metal powders used for additive manufacturing. Journal of Research of the National Institute of Standards and Technology, 119:460, Oct 2014. URL: https://doi.org/10.6028/jres.119.018, doi:10.6028/jres.119.018. This article has 703 citations and is from a peer-reviewed journal.

3. (grubbs2022explorationofthe pages 11-13): Jack Grubbs, Bryer C. Sousa, and Danielle Cote. Exploration of the effects of metallic powder handling and storage conditions on flowability and moisture content for additive manufacturing applications. Metals, 12:603, Mar 2022. URL: https://doi.org/10.3390/met12040603, doi:10.3390/met12040603. This article has 34 citations.

4. (smith2017relationshipofpowder pages 1-7): TM Smith, MF Kloesel, and CK Sudbrack. Relationship of powder feedstock variability to microstructure and defects in selective laser melted alloy 718. Unknown journal, 2017.

5. (smith2017relationshipofpowder pages 7-15): TM Smith, MF Kloesel, and CK Sudbrack. Relationship of powder feedstock variability to microstructure and defects in selective laser melted alloy 718. Unknown journal, 2017.

6. (ellis2019…feedstockvariability pages 6-10): D Ellis and C Sudbrack. … feedstock variability on structure, property, and performance of selective laser melted alloy 718: a principal component analysis (pca) of feedstock variability. Unknown journal, 2019.

7. (cordova2023impactofpowder pages 4-7): Laura Cordova, Cindy Sithole, Eric Macía Rodríguez, Ian Gibson, and Mónica Campos. Impact of powder reusability on batch repeatability of ti6al4v eli for pbf-lb industrial production. Powder Metallurgy, 66:129-138, Oct 2023. URL: https://doi.org/10.1080/00325899.2022.2133357, doi:10.1080/00325899.2022.2133357. This article has 17 citations and is from a peer-reviewed journal.

8. (gibbons2026alongitudinalstudy pages 3-5): Duncan W. Gibbons and Andre F. van der Merwe. A longitudinal study of ti-6al-4v eli powder reuse for laser powder bed fusion in a certified medical device manufacturing facility. The International Journal of Advanced Manufacturing Technology, Sep 2026. URL: https://doi.org/10.1007/s00170-026-19064-8, doi:10.1007/s00170-026-19064-8. This article has 0 citations.

9. (cordova2023impactofpowder pages 3-4): Laura Cordova, Cindy Sithole, Eric Macía Rodríguez, Ian Gibson, and Mónica Campos. Impact of powder reusability on batch repeatability of ti6al4v eli for pbf-lb industrial production. Powder Metallurgy, 66:129-138, Oct 2023. URL: https://doi.org/10.1080/00325899.2022.2133357, doi:10.1080/00325899.2022.2133357. This article has 17 citations and is from a peer-reviewed journal.

10. (anderson2002progresstowardgas pages 4-5): Iver E Anderson and Robert L Terpstra. Progress toward gas atomization processing with increased uniformity and control. Materials Science and Engineering A-structural Materials Properties Microstructure and Processing, 326:101-109, Mar 2002. URL: https://doi.org/10.1016/s0921-5093(01)01427-7, doi:10.1016/s0921-5093(01)01427-7. This article has 154 citations.

11. (zhang2025researchprogresson pages 10-11): Sen Zhang, K. Guo, Yongquan Qing, and Changsheng Liu. Research progress on the preparation technology of spherical alloy powders for laser additive manufacturing. Materials, Jul 2025. URL: https://doi.org/10.3390/ma18143385, doi:10.3390/ma18143385. This article has 14 citations.

12. (zhang2025researchprogresson pages 4-6): Sen Zhang, K. Guo, Yongquan Qing, and Changsheng Liu. Research progress on the preparation technology of spherical alloy powders for laser additive manufacturing. Materials, Jul 2025. URL: https://doi.org/10.3390/ma18143385, doi:10.3390/ma18143385. This article has 14 citations.

13. (brika2020influenceofparticle pages 5-8): Salah Eddine Brika, Morgan Letenneur, Christopher Alex Dion, and Vladimir Brailovski. Influence of particle morphology and size distribution on the powder flowability and laser powder bed fusion manufacturability of ti-6al-4v alloy. Additive manufacturing, 31:100929, Jan 2020. URL: https://doi.org/10.1016/j.addma.2019.100929, doi:10.1016/j.addma.2019.100929. This article has 600 citations and is from a highest quality peer-reviewed journal.

14. (mcelderry2022ampowderflowability pages 1-13): J McElderry and R Boothe. Am powder flowability capabilities at nasa marshall space flight center (msfc). Unknown journal, 2022.

15. (pennacchio2026…stainlesssteel pages 44-47): A Pennacchio. … stainless steel powders and their properties after pbf-lb/m processing. from waste-derived powder production to pbf-lb/m components: gas atomization …. Unknown journal, 2026.

16. (smith2017relationshipofpowder pages 15-19): TM Smith, MF Kloesel, and CK Sudbrack. Relationship of powder feedstock variability to microstructure and defects in selective laser melted alloy 718. Unknown journal, 2017.

17. (cordova2023impactofpowder pages 7-9): Laura Cordova, Cindy Sithole, Eric Macía Rodríguez, Ian Gibson, and Mónica Campos. Impact of powder reusability on batch repeatability of ti6al4v eli for pbf-lb industrial production. Powder Metallurgy, 66:129-138, Oct 2023. URL: https://doi.org/10.1080/00325899.2022.2133357, doi:10.1080/00325899.2022.2133357. This article has 17 citations and is from a peer-reviewed journal.

18. (makes2017standardizationroadmapfor pages 100-103): A Makes and AAMS Collaborative. Standardization roadmap for additive manufacturing. Unknown journal, 2017.

19. (glendening2020nasasplansfor pages 19-31): A Glendening and R Russell. Nasa's plans for development of standards for additive manufactured components. Unknown journal, 2020.

20. (cooke2012propertiesofmetal pages 1-7): April Cooke and John Slotwinski. Properties of metal powders for additive manufacturing: a review of the state of the art of metal powder property testing. ArXiv, Aug 2012. URL: https://doi.org/10.6028/nist.ir.7873, doi:10.6028/nist.ir.7873. This article has 137 citations.

21. (anderson2002progresstowardgas pages 5-6): Iver E Anderson and Robert L Terpstra. Progress toward gas atomization processing with increased uniformity and control. Materials Science and Engineering A-structural Materials Properties Microstructure and Processing, 326:101-109, Mar 2002. URL: https://doi.org/10.1016/s0921-5093(01)01427-7, doi:10.1016/s0921-5093(01)01427-7. This article has 154 citations.

22. (marinucci2023developmentofalsi10mg pages 70-73): F Marinucci. Development of alsi10mg based alloys for additive manufacturing processes. Unknown journal, 2023.