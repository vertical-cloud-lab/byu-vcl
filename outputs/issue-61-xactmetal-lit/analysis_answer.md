## Findings

The public record is much thinner than vendor marketing suggests. I found **six academic institutions or collaborations with credible evidence of operating an Xact Metal printer**, concentrated on the XM200C and XM200G. I found **no verified academic installation or research paper for the XM200S or XM300/XM300C**.

Only two research programs clearly demonstrate changing core exposure parameters beyond a single factory recipe:

1. An AGH University of Krakow-led Polish collaboration using an **XM200C** varied laser power and scan speed.
2. The University of Southern Denmark using an **XM200G** varied laser power, scan speed, and layer thickness relative to Xact Metal’s recommended Inconel 625 settings.

“Not reported” below means that I did not find public evidence. It does not establish that the machine or institution lacks parameter access.

## Verified academic operators and uses

| Institution or group | Model | Application area | Representative output | Parameters beyond factory presets? |
|---|---|---|---|---|
| **University of Southern Denmark (SDU), Centre for Industrial Mechanics, Sønderborg** | **XM200C**, installed February 2022; later **XM200G** use is documented | Industry-facing design and prototyping; lightweight battery enclosure; aluminum printing; systematic Inconel 625 process–structure–property research | SDU–Zirocco battery-casing [case study](https://xactmetal.com/wp-content/uploads/2023/04/ZiroccoxSDU_v11.pdf). Yildiz, Gokcekaya & Malekan, “A holistic analysis of laser powder bed fusion process parameters for Inconel 625 superalloy,” *Progress in Additive Manufacturing* (online 2025), [DOI: 10.1007/s40964-025-01385-x](https://doi.org/10.1007/s40964-025-01385-x) | **Yes on XM200G.** The paper identifies Xact’s reference as 350 W, 1700 mm/s and then tests other combinations within machine limits, with volumetric energy density from 21.4 to 166.7 J/mm³. Layer thickness was also varied. Hatch spacing and rotation were held at 50 µm and 67°, respectively. For the XM200C case study, parameter changes were **not reported**. |
| **AGH University of Krakow-led collaboration**, with Rzeszów University of Technology and Warsaw University of Technology coauthors | **XM200C**; exact institutional host of the printer is not stated in the papers | M300 maraging-steel tooling, 316L microstructure and mechanical-property studies, build orientation, surface/volumetric treatment | Żaba et al., “Application of Powder-Bed Fusion…M300 Maraging Steel Tools,” *Materials* 17, 6185 (2024), [DOI: 10.3390/ma17246185](https://doi.org/10.3390/ma17246185). Żaba et al., “Effect of Build-Up Strategy and…Process Parameters…316L,” *Materials* 19, 26 (2026 issue; online 2025), [DOI: 10.3390/ma19010026](https://doi.org/10.3390/ma19010026). Żaba et al., M300 parameter/treatment study, [DOI: 10.30544/mmesee36](https://doi.org/10.30544/mmesee36) | **Yes.** The 316L study compares 50 W/150 mm·s⁻¹ with 100 W/300 mm·s⁻¹ while holding hatch distance at 0.024 mm and scan rotation at 67°. The 2024 M300 tooling paper instead used manufacturer-guideline settings: 50–80 W and 250–550 mm·s⁻¹, so that paper alone is **not** evidence of departing from presets. |
| **St. Mary’s University, San Antonio** | **XM200G** | Education and honors research; effect of build-plate position on 316L tensile properties and residual stress | Yareli Zelaya Pavón, “Influence of Build Plate Location on Tensile Properties and Residual Stresses in LPBF-Fabricated Stainless Steel 316 Components,” honors thesis (2025), [institutional record/PDF](https://commons.stmarytx.edu/cgi/viewcontent.cgi?article=1085&context=honorstheses) | **No, in the reported study.** The thesis says the specimens used standard settings and held laser power, speed, hatch spacing, and layer thickness constant to isolate build location. It reports a 200 W laser, 50 µm spot, and 30 µm layers. No DOI. |
| **Clarkson University, AIDFab, Mechanical and Aerospace Engineering** | **XM200C** | Hands-on metallic additive-manufacturing instruction, laboratory operation, and student fabrication | Clarkson’s public [XM200C operating documentation](https://bookstack.clarkson.edu/books/metallic-3d-printing-at-the-aidfab-in-the-mechanical-and-aerospace-engineering-department/page/xm200c-3d-printer-step-by-step-instructions) | **Not reported.** I found operating and safety documentation but no machine-specific research publication showing systematic changes to power, speed, hatch spacing, or rotation. |
| **University of Bolton, National Centre for Motorsport Engineering** | **XM200C** | Teaching metal additive manufacturing; motorsport components; stated interest in Scalmalloy parts | Installation announcement: [first UK Xact Metal machine at NCME](https://3dprinting.co.uk/news/xact-metal-ncme/); related [motorsport case study](https://3dprinting.co.uk/case-studies/motorsport-engineers-3d-printing/) | **Not reported.** Public material documents education and component production, not an exposure-parameter study. No representative peer-reviewed paper located. |
| **Pennsylvania State University student/Xact Metal collaboration** | Model described in the public account only as an Xact Metal printer; the university’s ownership of a specific production unit was not independently verified | Senior capstone parameter optimization and workforce training | [Capstone account](https://labmidwest.com/metal-3d-printing-mechanical-engineering-student/); background on the Penn State-founded company is in the university’s [startup announcement](https://www.psu.edu/news/academics/story/xact-metals-3d-printing-technology-launches) | **Yes, but weakly documented.** The capstone account says the student “optimized print parameters,” but does not publish the model, parameter ranges, design, or results. I would not treat it as peer-reviewed evidence. |

### Models for which no academic operator was verified

| Model | Search result |
|---|---|
| **XM200S** | I found product announcements and reseller material, but no credible university installation or machine-specific academic publication. |
| **XM300 / XM300C** | I found vendor specifications and reseller listings, but no verified academic operator or publication. The XM300C appears to have had little public academic uptake. |

## Comparison with other compact academic LPBF systems

### Published-research footprint

As a transparent discovery check, I queried OpenAlex by exact model name. The four Xact model searches returned **26 search records in total**, versus **574** for the eight comparator-name searches, a **22.1-fold difference**. Exact model-name matches in titles or indexed abstracts were 1 versus 35. These are **not formal bibliometric publication counts**: machine models are often mentioned only in full-text Methods sections, and names such as “SLM 125” can generate false positives. They do, however, agree with the manual literature search.

| System family | Relative academic footprint | Materials-development suitability | Assessment |
|---|---:|---|---|
| **Aconity MINI/MIDI** | **High and growing.** OpenAlex model-name searches returned 69 and 60 records. Representative work includes “Rapid Alloy Development of Extremely High-Alloyed Metals,” *Materials* 12, 1706 (2019), [DOI: 10.3390/ma12101706](https://doi.org/10.3390/ma12101706). | **Excellent.** These systems are commonly configured for open parameter control, small powder batches, monitoring, beam-profile experiments, and nonstandard atmospheres or modules. | Best fit among the listed systems for experimental alloy and process development, particularly where machine openness matters more than turnkey operation. |
| **SLM 125** | **Largest mature footprint in this search**: 231 OpenAlex search records. It appears frequently in theses, parameter-development studies, and alloy work. Example: “SLM 125 Single Track and Density Cube Characterization for 316L,” [DOI: 10.15368/theses.2019.47](https://doi.org/10.15368/theses.2019.47). | **Very good.** Small build volume and broad academic history make it suitable for process maps and new powders, especially with open-parameter access. | Stronger evidence base and cross-laboratory comparability than Xact Metal. Older installations may require more maintenance and powder than newer research-focused microsystems. |
| **TruPrint 1000** | **High**: 164 OpenAlex search records. Example: Ti–18Zr–14Nb process mapping, [DOI: 10.3390/met10121697](https://doi.org/10.3390/met10121697). | **Good to very good.** Demonstrated alloy/process mapping and industrially relevant control; typically more production-oriented and potentially less hackable than Aconity. | Better publication record and validation base than Xact, but generally a larger investment and less research-flexible than explicitly open platforms. |
| **EOS M 100** | **Moderate, established**: 33 OpenAlex search records, with many model mentions likely confined to full text. Example empirical parameter development: [DOI: 10.3390/ma13245793](https://doi.org/10.3390/ma13245793). | **Good for disciplined process development**, particularly established alloys and repeatability studies. EOS parameter access can be license/material dependent. | Strong turnkey operation and industrial relevance. Less attractive than Aconity when deep machine modification or unusual powders are central. |
| **Coherent/OR Laser Creator** | **Small**: 4–5 OpenAlex records under the two names. A representative IN738LC study is [DOI: 10.1115/1.4052404](https://doi.org/10.1115/1.4052404). | **Moderate.** Compact and comparatively accessible, but the published ecosystem and cross-lab validation are limited. | Similar publication-scale class to Xact, though with some credible superalloy research. Support continuity and platform lineage should be checked before purchase. |
| **2OneLab** | **Very small/emerging**: 8 OpenAlex search records, several of which are software or repository records rather than materials papers. TU Darmstadt documents research cooperation through its [DiSer project](https://www.ptw.tu-darmstadt.de/forschung_ptw/tec/aktuelle_projekte_tec/diser/index.en.jsp). | **Potentially excellent for low-powder, open experimentation**, but peer-reviewed validation is still sparse. | Interesting for education and rapid alloy screening. More platform risk and a weaker literature benchmark than Aconity, SLM, EOS, or TruPrint. |
| **Xact Metal XM200C/XM200G** | **Low but now demonstrably nonzero**. The strongest papers appeared in 2024–2025/2026. | **XM200G: good potential. XM200C: adequate but lower-power.** The SDU paper proves that at least one XM200G installation supports systematic variation of power and speed beyond recommended values. | Attractive where capital cost, compactness, and ease of use dominate. The evidence base for reproducible new-alloy development remains much thinner than for Aconity, SLM 125, or TruPrint 1000. |

## Practical assessment

For **materials-development research**, the important distinction is not simply compact versus full-size. It is whether the institution receives:

- unlocked control of contour and bulk laser power, scan speed, hatch spacing, scan rotation, layer thickness, and scan strategy;
- an efficient route for importing arbitrary parameter sets rather than only vendor material files;
- safe handling of small, nonqualified powder batches;
- access to machine logs and, ideally, melt-pool or layer-monitoring data;
- support for nonstandard alloys without voiding service arrangements.

The XM200G has crossed the minimum credibility threshold for process development: the SDU study varied power, speed, and layer thickness around a documented Xact reference condition and produced publishable process–microstructure–property results. The XM200C has also supported controlled power/speed experiments, although its 200 W laser and the small number of independent research groups limit the breadth of demonstrated alloy work.

If the primary goal is **teaching, prototyping, and occasional parameter studies**, Xact Metal is defensible. If the primary goal is **rapid new-alloy discovery, unusual scan strategies, beam shaping, custom monitoring, or extensive cross-institution comparison**, Aconity MINI/MIDI is the strongest research-oriented choice among those listed. SLM 125 and TruPrint 1000 offer the strongest mature publication precedents. EOS M 100 is a safer turnkey compromise. The Creator and 2OneLab platforms, like Xact, need a careful pre-purchase test of parameter openness and data export because their public research ecosystems remain small.

## Limitations

- This is a public-source survey, not a customer registry. Unannounced installations and papers that omit the machine model will be missed.
- Several installation sources are vendor or reseller case studies. I used them to establish equipment and application, not to validate scientific performance.
- Collaborative papers establish use of a machine but do not always identify which partner physically houses it. This is why the Polish XM200C work is listed as a collaboration rather than assigning ownership to one university.
- The St. Mary’s thesis is dated December 2025 and has no DOI; it is institutional grey literature.
- The OpenAlex numbers are discovery indicators, not statistically clean publication counts.

### Discretionary analytical decisions

- Required an explicit model name in a paper, thesis, university page, or installation announcement before classifying an institution as a verified operator.
- Treated vendor/reseller pages as acceptable evidence of installation but not as evidence of parameter capability unless they reported an actual study.
- Classified parameter modification as “yes” only when a source documented changing at least one requested core parameter or explicitly stated parameter optimization; fixed nonfactory values without a comparator were not enough.
- Kept collaborative publications under a joint institution label when the physical machine host was not stated.
- Used OpenAlex model-name searches only as a comparative discovery proxy and reported both broad search records and stricter title/abstract matches rather than presenting them as publication counts.
- Used a qualitative high/moderate/low publication-footprint scale because model mentions are inconsistently indexed and a formal bibliometric comparison would otherwise imply false precision.