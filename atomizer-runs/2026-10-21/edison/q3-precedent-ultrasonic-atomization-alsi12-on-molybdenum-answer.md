# q3-precedent-ultrasonic-atomization-alsi12-on-molybdenum

Edison Scientific `PRECEDENT` task `c7fbff8d-ea3b-4b92-8f50-9017f431a45b`, status `success`.

## Query

Has anyone reported ultrasonic atomization (sonotrode or vibrating-plate atomization, for example an AMAZEMET rePowder or 3D Lab ATO Lab) of the near-eutectic aluminium-silicon alloy AlSi12 (Al 4047) or of AlSi10Mg using a molybdenum sonotrode plate, and if so what melt temperature, superheat, overpressure, vibration amplitude and powder yield were used?

## Answer

Question: Has anyone reported ultrasonic atomization (sonotrode or vibrating-plate atomization, for example an AMAZEMET rePowder or 3D Lab ATO Lab) of the near-eutectic aluminium-silicon alloy AlSi12 (Al 4047) or of AlSi10Mg using a molybdenum sonotrode plate, and if so what melt temperature, superheat, overpressure, vibration amplitude and powder yield were used?

No. ## Finding

**AlSi12 has been ultrasonically atomized, but I found no report that establishes the full combination of AlSi12 (Al 4047) or AlSi10Mg *and* a molybdenum sonotrode plate with all five requested operating quantities.** Yankin and colleagues reported atomizing **AlSi12 wire** on a **3D Lab ATO Lab+ US35**: an electric arc melted the wire onto a vibrating platform, which dispersed the melt into powder. The paper does **not identify the platform material as molybdenum**. I did not verify a corresponding direct report for AlSi10Mg. (yankin2025effectofultrasonic pages 2-3)

For the **AlSi12 experiment**, the reported settings were **35 kHz**, **75% or 80% machine vibration-amplitude setting**, and **140 or 150 A** arc current. The authors state that approximately **75% of the powder was usable after sieving at 63 µm**. That is a *usable particle-size fraction*, not a demonstrated 75% conversion of starting alloy into collected powder. They do **not report a measured melt temperature, superheat above the liquidus, atomization-chamber overpressure, displacement amplitude in µm, or total feedstock-to-powder yield**. Consequently, none of those missing quantities can be assigned reliably to this AlSi12 run. (yankin2025effectofultrasonic pages 2-3)

The distinction from superficially similar reports matters:

| Study, alloy, and equipment | Molybdenum sonotrode specified? | Melt temperature / superheat | Pressure | Ultrasonic setting / amplitude | Powder yield or efficiency |
|---|---|---|---|---|---|
| **Yankin et al. (2025): AlSi12**, ATO Lab+ with US35 atomizer | **No.** The vibrating-platform/sonotrode material is not reported. | **Not reported; superheat not calculable.** | Chamber pressure or overpressure **not reported**. | **35 kHz; 75% or 80% machine amplitude setting** (not displacement in µm); arc current 140 or 150 A. | Approximately **75% passed the 63 µm sieve** and was deemed usable for the authors’ AM system. This is a usable-size fraction, **not a reported feed-to-powder conversion yield**. (yankin2025effectofultrasonic pages 2-3) |
| **Jedynak et al. (2024): AlSi9Mg–20 vol% SiC**—**not AlSi10Mg or AlSi12**; AMAZEMET rePowder for induction/plasma and 3D Lab ATO Lab+ for arc | **No.** Sonotrode/plate material is not specified in this paper. | Induction melting: **1100 °C in a graphite crucible**; superheat not stated. Arc/plasma melt temperatures not reported. These values are not transferable to AlSi12 or AlSi10Mg. | Induction-feed **pressure difference** of **300 or 500 mbar**, not identified as atomization-chamber overpressure. No pressure reported for arc/plasma. | Frequencies: **35 kHz arc, 40 kHz plasma, and 40 or 60 kHz induction**. Absolute or percentage amplitude is not reported in the primary paper. | Feedstock-to-collected-powder process efficiency: approximately **15% arc**, **41% plasma**, and **up to almost 50% induction**; individual induction conditions included approximately 19–38%. These are for the SiC composite, not either alloy asked about. (jedynak2024processabilityofaluminummatrix pages 1-3, jedynak2024processabilityofaluminummatrix pages 3-6) |
| **Goncharov et al. (2026): Co-free Al–Cr–Cu–Fe–Mn–Ni HEA**, AMAZEMET rePowder—**different alloy** | **Yes.** The rePowder platform is explicitly described as using a **molybdenum sonotrode**. This establishes that rePowder can use Mo, but does not prove that the AlSi12 experiment did. | Requested atomization temperature and superheat not reported in the cited methods. | Requested atomization overpressure not reported. | Requested amplitude not reported. | Requested powder yield not reported. (goncharov2026designofcobaltfree pages 2-4) |


*Table: Source-specific comparison separating the direct AlSi12 report from nonmatching AlSi9Mg–SiC and HEA studies. It prevents rePowder’s documented molybdenum sonotrode and the composite’s temperature, pressure, and efficiencies from being incorrectly attributed to AlSi12 or AlSi10Mg.*

In particular, **1100 °C** and **300–500 mbar** occur in Jedynak and colleagues’ *induction* experiments on **AlSi9Mg reinforced with 20 vol% SiC**, not on AlSi12 or AlSi10Mg; the pressure is a **feed pressure difference**, not a stated chamber overpressure. Their approximately **15% arc, 41% plasma, and nearly 50% maximum induction efficiencies** likewise belong to that composite. A separate rePowder publication explicitly documents a **molybdenum sonotrode**, but it atomizes an **Al–Cr–Cu–Fe–Mn–Ni high-entropy alloy**. Neither observation establishes the sonotrode material or operating conditions of the AlSi12 experiment. (jedynak2024processabilityofaluminummatrix pages 1-3, jedynak2024processabilityofaluminummatrix pages 3-6, goncharov2026designofcobaltfree pages 2-4, jedynak2024processabilityofaluminummatrix media 0d56dd6e)

References

1. (yankin2025effectofultrasonic pages 2-3): Andrei Yankin, Hussain Ali Murtaza, Boris Golman, Asma Perveen, and Didier Talamona. Effect of ultrasonic atomization parameters on alsi12 aluminum powder characteristics for additive manufacturing. Scientific Reports, Jul 2025. URL: https://doi.org/10.1038/s41598-025-06086-7, doi:10.1038/s41598-025-06086-7. This article has 5 citations and is from a peer-reviewed journal.

2. (jedynak2024processabilityofaluminummatrix pages 1-3): A JEDYNAK, S HÄRTEL, and R PIPPIG. Processability of aluminum-matrix composite (amc) by ultrasonic powder atomization. Materials Research Proceedings, 41:156-163, May 2024. URL: https://doi.org/10.21741/9781644903131-17, doi:10.21741/9781644903131-17. This article has 1 citations.

3. (jedynak2024processabilityofaluminummatrix pages 3-6): A JEDYNAK, S HÄRTEL, and R PIPPIG. Processability of aluminum-matrix composite (amc) by ultrasonic powder atomization. Materials Research Proceedings, 41:156-163, May 2024. URL: https://doi.org/10.21741/9781644903131-17, doi:10.21741/9781644903131-17. This article has 1 citations.

4. (goncharov2026designofcobaltfree pages 2-4): Ivan Goncharov, Vera Popovich, Marcel Sluiter, Anatoly Popovich, and Maurizio Vedani. Design of cobalt-free high-entropy alloy binder for wc-base cemented carbides. Metals, 16:318, Mar 2026. URL: https://doi.org/10.3390/met16030318, doi:10.3390/met16030318. This article has 1 citations.

5. (jedynak2024processabilityofaluminummatrix media 0d56dd6e): A JEDYNAK, S HÄRTEL, and R PIPPIG. Processability of aluminum-matrix composite (amc) by ultrasonic powder atomization. Materials Research Proceedings, 41:156-163, May 2024. URL: https://doi.org/10.21741/9781644903131-17, doi:10.21741/9781644903131-17. This article has 1 citations.
