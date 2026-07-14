Question: Identify up to 100 distinct aluminum alloys (and aluminum-based feedstocks) that together span as wide a range of compositions as possible - i.e. collectively covering many different alloying elements (e.g. Si, Mg, Cu, Zn, Mn, Fe, Cr, Ni, Ti, Zr, Sc, V, Li, Ag, Sn, Pb, Bi, Ga, Ni, rare earths, etc.) across the major wrought (1xxx-8xxx) and cast (Axxx.x) families as well as additive-manufacturing and specialty alloys (e.g. AlSi10Mg, Scalmalloy, A356/A357, 6061, 7075, 2024, 5083, 4047, 1100). For each alloy give: its common designation/name, its family or class, and its nominal/typical elemental composition (weight-percent ranges for the main alloying elements, balance Al). Prioritize diversity of the alloying-element palette over near-duplicates. Return TWO things: (1) a readable markdown table of the alloys with their nominal compositions, and (2) at the very END of your answer, a single fenced code block labelled ```json containing a JSON array where each element is an object with keys "designation" (string), "family" (string), and "nominal_composition" (string, a concise human-readable composition such as 'Al-10Si-0.4Mg' or 'Al-5.5Zn-2.5Mg-1.5Cu'). Include every alloy from the table in the JSON array, up to 100 entries.

## Comprehensive Survey of 100 Aluminum Alloys Spanning Maximum Compositional Diversity

The following compilation identifies 100 distinct aluminum alloys and aluminum-based feedstocks selected to collectively span the widest possible range of alloying elements and alloy families. The list encompasses wrought alloys from all major series (1xxx through 8xxx), cast alloy families (2xx.x through 8xx.x), aluminum-lithium alloys, additive manufacturing feedstocks, and specialty/research compositions. The alloying elements represented include Si, Mg, Cu, Zn, Mn, Fe, Cr, Ni, Ti, Zr, Sc, V, Li, Ag, Sn, Pb, Bi, Be, Ce, and Er, ensuring broad compositional coverage.

Compositions were verified against multiple literature sources. The 2xxx series alloys (2024: Al-4.4Cu-1.5Mg-0.6Mn; 2219: Al-6.3Cu with V and Zr additions; 2618: Al-2.3Cu-1.6Mg-1.0Ni-1.1Fe) were confirmed from metallurgical handbooks (mann2011hotdeformationof pages 39-43, mann2011hotdeformationof pages 33-39). Al-Li alloy compositions (2090, 2091, 2195, 2099, 2050, 2060, 8090, 1420) were sourced from Ablakatov et al. (2022) (ablakatov2022aluminumlithiumalloystypes pages 2-4), with supplementary Cu-Li ranges from González (2023) (gonzalez2023developmentandproductiona pages 48-51, gonzalez2023developmentandproduction pages 48-51). Cast alloy compositions (A356.0, A357.0, A380.0, A319.0, A390.0) were obtained from Wang'ombe (2022) (wangombe2022developmentofrecycled pages 41-46). The Scalmalloy® composition (Al-4.2–5.1Mg-0.6–0.88Sc-0.2–0.5Zr-0.3–0.8Mn) was documented in Remor (remorUnknownyearexperimentalanalysisof pages 34-40, remorUnknownyearexperimentalanalysisof pages 40-45). The research Al-Ce-Er-Sc-Zr alloy (Al-9.3Ce-0.11Sc-0.04Er-0.22Zr) was reported by Adetan (2025) (adetan2025microstructuralandmechanical pages 66-72, adetan2025microstructuralandmechanical pages 60-66).

| No. | Designation | Family/Class | Nominal Composition (wt%, bal. Al) |
|---:|---|---|---|
| 1 | 1100 | 1xxx Wrought | Al-0.12Cu (≥99.0 Al) |
| 2 | 1050 | 1xxx Wrought | Al (≥99.5 Al) |
| 3 | 1350 | 1xxx Wrought | Al (≥99.5 Al) |
| 4 | 2024 | 2xxx Wrought | Al-4.4Cu-1.5Mg-0.6Mn (mann2011hotdeformationof pages 39-43) |
| 5 | 2014 | 2xxx Wrought | Al-4.4Cu-0.8Si-0.8Mg-0.8Mn |
| 6 | 2219 | 2xxx Wrought | Al-6.3Cu-0.3Mn-0.06Ti-0.10V-0.18Zr (mann2011hotdeformationof pages 39-43) |
| 7 | 2618 | 2xxx Wrought | Al-2.3Cu-1.6Mg-1.0Ni-1.1Fe-0.18Si (mann2011hotdeformationof pages 39-43) |
| 8 | 2011 | 2xxx Wrought | Al-5.5Cu-0.4Pb-0.4Bi |
| 9 | 2017 | 2xxx Wrought | Al-4.0Cu-0.7Mg-0.7Mn-0.5Si |
| 10 | 2124 | 2xxx Wrought | Al-4.4Cu-1.5Mg-0.6Mn |
| 11 | 2519 | 2xxx Wrought | Al-5.8Cu-0.25Mg-0.3Mn-0.15V-0.15Zr |
| 12 | 2090 | 2xxx Al-Li Wrought | Al-2.6Li-3.0Cu-0.3Mg-0.1Zr (ablakatov2022aluminumlithiumalloystypes pages 2-4) |
| 13 | 2091 | 2xxx Al-Li Wrought | Al-2.3Li-2.5Cu-1.9Mg-0.1Zr (ablakatov2022aluminumlithiumalloystypes pages 2-4) |
| 14 | 2195 | 2xxx Al-Li Wrought | Al-1.0Li-4.0Cu-0.4Mg-0.4Ag-0.11Zr (ablakatov2022aluminumlithiumalloystypes pages 2-4, gonzalez2023developmentandproductiona pages 48-51) |
| 15 | 2099 | 2xxx Al-Li Wrought | Al-1.8Li-2.7Cu-0.3Mg-0.09Zr-0.3Zn-0.3Mn (ablakatov2022aluminumlithiumalloystypes pages 2-4, gonzalez2023developmentandproduction pages 48-51) |
| 16 | 2050 | 2xxx Al-Li Wrought | Al-1.0Li-3.6Cu-0.4Mg-0.4Ag-0.11Zr (ablakatov2022aluminumlithiumalloystypes pages 2-4, gonzalez2023developmentandproductiona pages 48-51) |
| 17 | 2060 | 2xxx Al-Li Wrought | Al-0.7Li-3.9Cu-0.8Mg-0.2Ag-0.11Zr-0.3Mn-0.4Zn (ablakatov2022aluminumlithiumalloystypes pages 2-4, gonzalez2023developmentandproductiona pages 48-51) |
| 18 | 2196 | 2xxx Al-Li Wrought | Al-1.8Li-2.9Cu-0.5Mg-0.4Ag-0.11Zr |
| 19 | 3003 | 3xxx Wrought | Al-1.2Mn-0.12Cu |
| 20 | 3004 | 3xxx Wrought | Al-1.2Mn-1.0Mg |
| 21 | 3105 | 3xxx Wrought | Al-0.55Mn-0.5Mg |
| 22 | 4043 | 4xxx Wrought | Al-5.2Si |
| 23 | 4047 | 4xxx Wrought | Al-12.0Si |
| 24 | 4032 | 4xxx Wrought | Al-12.2Si-1.0Mg-0.9Cu-0.9Ni |
| 25 | 4045 | 4xxx Wrought | Al-10.0Si |
| 26 | 4343 | 4xxx Wrought | Al-7.5Si |
| 27 | 5052 | 5xxx Wrought | Al-2.5Mg-0.25Cr |
| 28 | 5083 | 5xxx Wrought | Al-4.4Mg-0.7Mn-0.15Cr |
| 29 | 5086 | 5xxx Wrought | Al-4.0Mg-0.45Mn-0.15Cr |
| 30 | 5182 | 5xxx Wrought | Al-4.5Mg-0.35Mn |
| 31 | 5454 | 5xxx Wrought | Al-2.7Mg-0.8Mn-0.12Cr |
| 32 | 5754 | 5xxx Wrought | Al-3.1Mg-0.5Mn |
| 33 | 5056 | 5xxx Wrought | Al-5.0Mg-0.12Mn-0.12Cr |
| 34 | 5154 | 5xxx Wrought | Al-3.5Mg-0.25Cr |
| 35 | 5356 | 5xxx Wrought / Filler Wire | Al-5.0Mg-0.12Mn-0.12Cr-0.12Ti |
| 36 | 5556 | 5xxx Wrought / Filler Wire | Al-5.1Mg-0.8Mn-0.12Cr-0.12Ti |
| 37 | 5005 | 5xxx Wrought | Al-0.8Mg |
| 38 | 6061 | 6xxx Wrought | Al-1.0Mg-0.6Si-0.28Cu-0.20Cr |
| 39 | 6063 | 6xxx Wrought | Al-0.7Mg-0.4Si |
| 40 | 6082 | 6xxx Wrought | Al-0.9Mg-1.0Si-0.7Mn |
| 41 | 6013 | 6xxx Wrought | Al-0.8Mg-0.8Si-0.9Cu-0.35Mn |
| 42 | 6201 | 6xxx Wrought | Al-0.7Mg-0.7Si |
| 43 | 6111 | 6xxx Wrought | Al-0.8Mg-0.9Si-0.7Cu-0.2Mn |
| 44 | 6060 | 6xxx Wrought | Al-0.5Mg-0.4Si |
| 45 | 6005 | 6xxx Wrought | Al-0.5Mg-0.7Si-0.15Mn |
| 46 | 6351 | 6xxx Wrought | Al-0.6Mg-1.0Si-0.6Mn |
| 47 | 6020 | 6xxx Wrought | Al-0.8Mg-0.8Si-0.35Sn |
| 48 | 7075 | 7xxx Wrought | Al-5.6Zn-2.5Mg-1.6Cu-0.23Cr |
| 49 | 7050 | 7xxx Wrought | Al-6.2Zn-2.25Mg-2.3Cu-0.12Zr |
| 50 | 7055 | 7xxx Wrought | Al-8.0Zn-2.05Mg-2.3Cu-0.12Zr |
| 51 | 7475 | 7xxx Wrought | Al-5.7Zn-2.25Mg-1.6Cu-0.21Cr |
| 52 | 7178 | 7xxx Wrought | Al-6.8Zn-2.7Mg-2.0Cu-0.26Cr |
| 53 | 7003 | 7xxx Wrought | Al-6.0Zn-0.8Mg |
| 54 | 7020 | 7xxx Wrought | Al-4.5Zn-1.2Mg-0.35Mn-0.15Cr-0.12Zr |
| 55 | 7072 | 7xxx Wrought / Cladding | Al-1.0Zn |
| 56 | 7085 | 7xxx Wrought | Al-7.5Zn-1.5Mg-1.65Cu-0.12Zr |
| 57 | 7A04 | 7xxx Wrought (Chinese) | Al-6.0Zn-2.2Mg-1.7Cu-0.15Mn |
| 58 | 8090 | 8xxx Wrought / Al-Li | Al-2.4Li-1.2Cu-0.8Mg-0.11Zr (ablakatov2022aluminumlithiumalloystypes pages 2-4) |
| 59 | 8011 | 8xxx Wrought | Al-0.7Fe-0.7Si |
| 60 | 8079 | 8xxx Wrought | Al-1.2Fe-0.1Si |
| 61 | 8176 | 8xxx Wrought | Al-0.5Fe-0.1Si |
| 62 | A356.0 | Cast 3xx.x | Al-7.0Si-0.35Mg (wangombe2022developmentofrecycled pages 41-46) |
| 63 | A357.0 | Cast 3xx.x | Al-7.0Si-0.55Mg-0.05Be (wangombe2022developmentofrecycled pages 41-46) |
| 64 | 356.0 | Cast 3xx.x | Al-7.0Si-0.35Mg |
| 65 | A380.0 | Cast 3xx.x | Al-8.5Si-3.5Cu-0.5Ni (wangombe2022developmentofrecycled pages 41-46) |
| 66 | A319.0 | Cast 3xx.x | Al-6.0Si-3.5Cu (wangombe2022developmentofrecycled pages 41-46) |
| 67 | A390.0 | Cast 3xx.x | Al-17Si-4.5Cu-0.55Mg (wangombe2022developmentofrecycled pages 41-46) |
| 68 | 360.0 | Cast 3xx.x | Al-9.5Si-0.5Mg |
| 69 | 332.0 | Cast 3xx.x | Al-9.5Si-3.0Cu-1.0Mg-0.5Ni |
| 70 | 336.0 | Cast 3xx.x | Al-12.0Si-1.0Cu-1.0Mg-2.5Ni |
| 71 | 355.0 | Cast 3xx.x | Al-5.0Si-1.25Cu-0.5Mg |
| 72 | 413.0 | Cast 4xx.x | Al-12.0Si |
| 73 | 443.0 | Cast 4xx.x | Al-5.2Si |
| 74 | 295.0 | Cast 2xx.x | Al-4.5Cu-1.1Si |
| 75 | 201.0 | Cast 2xx.x | Al-4.6Cu-0.35Mg-0.7Ag-0.25Ti |
| 76 | 242.0 | Cast 2xx.x | Al-4.0Cu-1.5Mg-2.0Ni |
| 77 | 206.0 | Cast 2xx.x | Al-4.6Cu-0.3Mg-0.3Mn-0.22Ti |
| 78 | 520.0 | Cast 5xx.x | Al-10.0Mg |
| 79 | 535.0 | Cast 5xx.x | Al-6.9Mg-0.18Mn-0.18Ti |
| 80 | 713.0 | Cast 7xx.x | Al-7.5Zn-0.35Mg-0.7Cu |
| 81 | 771.0 | Cast 7xx.x | Al-7.0Zn-0.9Mg-0.13Cr-0.12Ti |
| 82 | 850.0 | Cast 8xx.x | Al-6.2Sn-1.0Cu-1.0Ni |
| 83 | 851.0 | Cast 8xx.x | Al-5.5Sn-2.5Si-1.0Cu-0.5Ni |
| 84 | 1420 | Russian/Other Al-Li | Al-2.2Li-6.2Mg-0.1Zr (ablakatov2022aluminumlithiumalloystypes pages 2-4) |
| 85 | 1441 | Russian/Other Al-Li | Al-1.7Li-1.6Cu-0.9Mg-0.1Zr |
| 86 | AlSi10Mg | AM Specialty | Al-10Si-0.4Mg |
| 87 | Scalmalloy | AM Specialty | Al-4.6Mg-0.7Sc-0.35Zr-0.5Mn (remorUnknownyearexperimentalanalysisof pages 34-40) |
| 88 | AlSi7Mg (A357-AM) | AM Specialty | Al-7Si-0.6Mg |
| 89 | AlSi12 | AM Specialty | Al-12Si |
| 90 | AlSi3.5Mg2.5 | AM Specialty | Al-3.5Si-2.5Mg |
| 91 | Al-5Mg-2Si-0.7Mn-0.15Zr | AM Specialty | Al-5Mg-2Si-0.7Mn-0.15Zr |
| 92 | A20X (Aeromet) | AM Specialty | Al-4.5Cu-0.25Mg-TiC |
| 93 | 6061-RAM | AM Specialty | Al-1.0Mg-0.6Si-0.28Cu |
| 94 | 7A77 | AM Specialty | Al-7.7Zn-2.4Mg-1.5Cu-0.15Zr |
| 95 | Al-9.3Ce-0.11Sc-0.04Er-0.22Zr | Specialty / Research RE Alloy | Al-9.3Ce-0.11Sc-0.04Er-0.22Zr (adetan2025microstructuralandmechanical pages 66-72, adetan2025microstructuralandmechanical pages 60-66) |
| 96 | Al-8Ce-10Mg | Specialty / Research RE Alloy | Al-8Ce-10Mg |
| 97 | Al-3.5Cu-1.5Mg-0.5Ag | Specialty / Al-Cu-Mg-Ag | Al-3.5Cu-1.5Mg-0.5Ag |
| 98 | Al-5.5Mg-0.3Mn-0.15Sc-0.1Zr | Specialty / Sc-modified 5xxx | Al-5.5Mg-0.3Mn-0.15Sc-0.1Zr |
| 99 | Al-33Cu | Specialty / Brazing Eutectic | Al-33Cu |
| 100 | Al-5Mg-0.7Mn-0.15Sc-0.05Er-0.1Zr | Specialty / Multi-RE Alloy | Al-5Mg-0.7Mn-0.15Sc-0.05Er-0.1Zr |


*Table: This table compiles 100 distinct aluminum alloys and feedstocks spanning wrought, cast, additive-manufacturing, and specialty systems, emphasizing broad coverage of alloying elements. Literature-backed entries are cited where context IDs were available; remaining entries follow standard nominal AA-style compositions and common industry designations.*

The JSON array containing all 100 alloys follows below:

```json
[
  {"designation": "1100", "family": "1xxx Wrought", "nominal_composition": "Al-0.12Cu (≥99.0 Al)"},
  {"designation": "1050", "family": "1xxx Wrought", "nominal_composition": "Al (≥99.5 Al)"},
  {"designation": "1350", "family": "1xxx Wrought", "nominal_composition": "Al (≥99.5 Al, electrical)"},
  {"designation": "2024", "family": "2xxx Wrought", "nominal_composition": "Al-4.4Cu-1.5Mg-0.6Mn"},
  {"designation": "2014", "family": "2xxx Wrought", "nominal_composition": "Al-4.4Cu-0.8Si-0.8Mg-0.8Mn"},
  {"designation": "2219", "family": "2xxx Wrought", "nominal_composition": "Al-6.3Cu-0.3Mn-0.06Ti-0.10V-0.18Zr"},
  {"designation": "2618", "family": "2xxx Wrought", "nominal_composition": "Al-2.3Cu-1.6Mg-1.0Ni-1.1Fe-0.18Si"},
  {"designation": "2011", "family": "2xxx Wrought", "nominal_composition": "Al-5.5Cu-0.4Pb-0.4Bi"},
  {"designation": "2017", "family": "2xxx Wrought", "nominal_composition": "Al-4.0Cu-0.7Mg-0.7Mn-0.5Si"},
  {"designation": "2124", "family": "2xxx Wrought", "nominal_composition": "Al-4.4Cu-1.5Mg-0.6Mn"},
  {"designation": "2519", "family": "2xxx Wrought", "nominal_composition": "Al-5.8Cu-0.25Mg-0.3Mn-0.15V-0.15Zr"},
  {"designation": "2090", "family": "2xxx Al-Li Wrought", "nominal_composition": "Al-2.6Li-3.0Cu-0.3Mg-0.1Zr"},
  {"designation": "2091", "family": "2xxx Al-Li Wrought", "nominal_composition": "Al-2.3Li-2.5Cu-1.9Mg-0.1Zr"},
  {"designation": "2195", "family": "2xxx Al-Li Wrought", "nominal_composition": "Al-1.0Li-4.0Cu-0.4Mg-0.4Ag-0.11Zr"},
  {"designation": "2099", "family": "2xxx Al-Li Wrought", "nominal_composition": "Al-1.8Li-2.7Cu-0.3Mg-0.09Zr-0.3Zn-0.3Mn"},
  {"designation": "2050", "family": "2xxx Al-Li Wrought", "nominal_composition": "Al-1.0Li-3.6Cu-0.4Mg-0.4Ag-0.11Zr"},
  {"designation": "2060", "family": "2xxx Al-Li Wrought", "nominal_composition": "Al-0.7Li-3.9Cu-0.8Mg-0.2Ag-0.11Zr-0.3Mn-0.4Zn"},
  {"designation": "2196", "family": "2xxx Al-Li Wrought", "nominal_composition": "Al-1.8Li-2.9Cu-0.5Mg-0.4Ag-0.11Zr"},
  {"designation": "3003", "family": "3xxx Wrought", "nominal_composition": "Al-1.2Mn-0.12Cu"},
  {"designation": "3004", "family": "3xxx Wrought", "nominal_composition": "Al-1.2Mn-1.0Mg"},
  {"designation": "3105", "family": "3xxx Wrought", "nominal_composition": "Al-0.55Mn-0.5Mg"},
  {"designation": "4043", "family": "4xxx Wrought", "nominal_composition": "Al-5.2Si"},
  {"designation": "4047", "family": "4xxx Wrought", "nominal_composition": "Al-12.0Si"},
  {"designation": "4032", "family": "4xxx Wrought", "nominal_composition": "Al-12.2Si-1.0Mg-0.9Cu-0.9Ni"},
  {"designation": "4045", "family": "4xxx Wrought", "nominal_composition": "Al-10.0Si"},
  {"designation": "4343", "family": "4xxx Wrought", "nominal_composition": "Al-7.5Si"},
  {"designation": "5052", "family": "5xxx Wrought", "nominal_composition": "Al-2.5Mg-0.25Cr"},
  {"designation": "5083", "family": "5xxx Wrought", "nominal_composition": "Al-4.4Mg-0.7Mn-0.15Cr"},
  {"designation": "5086", "family": "5xxx Wrought", "nominal_composition": "Al-4.0Mg-0.45Mn-0.15Cr"},
  {"designation": "5182", "family": "5xxx Wrought", "nominal_composition": "Al-4.5Mg-0.35Mn"},
  {"designation": "5454", "family": "5xxx Wrought", "nominal_composition": "Al-2.7Mg-0.8Mn-0.12Cr"},
  {"designation": "5754", "family": "5xxx Wrought", "nominal_composition": "Al-3.1Mg-0.5Mn"},
  {"designation": "5056", "family": "5xxx Wrought", "nominal_composition": "Al-5.0Mg-0.12Mn-0.12Cr"},
  {"designation": "5154", "family": "5xxx Wrought", "nominal_composition": "Al-3.5Mg-0.25Cr"},
  {"designation": "5356", "family": "5xxx Wrought / Filler Wire", "nominal_composition": "Al-5.0Mg-0.12Mn-0.12Cr-0.12Ti"},
  {"designation": "5556", "family": "5xxx Wrought / Filler Wire", "nominal_composition": "Al-5.1Mg-0.8Mn-0.12Cr-0.12Ti"},
  {"designation": "5005", "family": "5xxx Wrought", "nominal_composition": "Al-0.8Mg"},
  {"designation": "6061", "family": "6xxx Wrought", "nominal_composition": "Al-1.0Mg-0.6Si-0.28Cu-0.20Cr"},
  {"designation": "6063", "family": "6xxx Wrought", "nominal_composition": "Al-0.7Mg-0.4Si"},
  {"designation": "6082", "family": "6xxx Wrought", "nominal_composition": "Al-0.9Mg-1.0Si-0.7Mn"},
  {"designation": "6013", "family": "6xxx Wrought", "nominal_composition": "Al-0.8Mg-0.8Si-0.9Cu-0.35Mn"},
  {"designation": "6201", "family": "6xxx Wrought", "nominal_composition": "Al-0.7Mg-0.7Si"},
  {"designation": "6111", "family": "6xxx Wrought", "nominal_composition": "Al-0.8Mg-0.9Si-0.7Cu-0.2Mn"},
  {"designation": "6060", "family": "6xxx Wrought", "nominal_composition": "Al-0.5Mg-0.4Si"},
  {"designation": "6005", "family": "6xxx Wrought", "nominal_composition": "Al-0.5Mg-0.7Si-0.15Mn"},
  {"designation": "6351", "family": "6xxx Wrought", "nominal_composition": "Al-0.6Mg-1.0Si-0.6Mn"},
  {"designation": "6020", "family": "6xxx Wrought", "nominal_composition": "Al-0.8Mg-0.8Si-0.35Sn"},
  {"designation": "7075", "family": "7xxx Wrought", "nominal_composition": "Al-5.6Zn-2.5Mg-1.6Cu-0.23Cr"},
  {"designation": "7050", "family": "7xxx Wrought", "nominal_composition": "Al-6.2Zn-2.25Mg-2.3Cu-0.12Zr"},
  {"designation": "7055", "family": "7xxx Wrought", "nominal_composition": "Al-8.0Zn-2.05Mg-2.3Cu-0.12Zr"},
  {"designation": "7475", "family": "7xxx Wrought", "nominal_composition": "Al-5.7Zn-2.25Mg-1.6Cu-0.21Cr"},
  {"designation": "7178", "family": "7xxx Wrought", "nominal_composition": "Al-6.8Zn-2.7Mg-2.0Cu-0.26Cr"},
  {"designation": "7003", "family": "7xxx Wrought", "nominal_composition": "Al-6.0Zn-0.8Mg"},
  {"designation": "7020", "family": "7xxx Wrought", "nominal_composition": "Al-4.5Zn-1.2Mg-0.35Mn-0.15Cr-0.12Zr"},
  {"designation": "7072", "family": "7xxx Wrought / Cladding", "nominal_composition": "Al-1.0Zn"},
  {"designation": "7085", "family": "7xxx Wrought", "nominal_composition": "Al-7.5Zn-1.5Mg-1.65Cu-0.12Zr"},
  {"designation": "7A04", "family": "7xxx Wrought (Chinese)", "nominal_composition": "Al-6.0Zn-2.2Mg-1.7Cu-0.15Mn"},
  {"designation": "8090", "family": "8xxx Wrought / Al-Li", "nominal_composition": "Al-2.4Li-1.2Cu-0.8Mg-0.11Zr"},
  {"designation": "8011", "family": "8xxx Wrought", "nominal_composition": "Al-0.7Fe-0.7Si"},
  {"designation": "8079", "family": "8xxx Wrought", "nominal_composition": "Al-1.2Fe-0.1Si"},
  {"designation": "8176", "family": "8xxx Wrought", "nominal_composition": "Al-0.5Fe-0.1Si"},
  {"designation": "A356.0", "family": "Cast 3xx.x", "nominal_composition": "Al-7.0Si-0.35Mg"},
  {"designation": "A357.0", "family": "Cast 3xx.x", "nominal_composition": "Al-7.0Si-0.55Mg-0.05Be"},
  {"designation": "356.0", "family": "Cast 3xx.x", "nominal_composition": "Al-7.0Si-0.35Mg"},
  {"designation": "A380.0", "family": "Cast 3xx.x", "nominal_composition": "Al-8.5Si-3.5Cu-0.5Ni"},
  {"designation": "A319.0", "family": "Cast 3xx.x", "nominal_composition": "Al-6.0Si-3.5Cu"},
  {"designation": "A390.0", "family": "Cast 3xx.x", "nominal_composition": "Al-17Si-4.5Cu-0.55Mg"},
  {"designation": "360.0", "family": "Cast 3xx.x", "nominal_composition": "Al-9.5Si-0.5Mg"},
  {"designation": "332.0", "family": "Cast 3xx.x", "nominal_composition": "Al-9.5Si-3.0Cu-1.0Mg-0.5Ni"},
  {"designation": "336.0", "family": "Cast 3xx.x", "nominal_composition": "Al-12.0Si-1.0Cu-1.0Mg-2.5Ni"},
  {"designation": "355.0", "family": "Cast 3xx.x", "nominal_composition": "Al-5.0Si-1.25Cu-0.5Mg"},
  {"designation": "413.0", "family": "Cast 4xx.x", "nominal_composition": "Al-12.0Si"},
  {"designation": "443.0", "family": "Cast 4xx.x", "nominal_composition": "Al-5.2Si"},
  {"designation": "295.0", "family": "Cast 2xx.x", "nominal_composition": "Al-4.5Cu-1.1Si"},
  {"designation": "201.0", "family": "Cast 2xx.x", "nominal_composition": "Al-4.6Cu-0.35Mg-0.7Ag-0.25Ti"},
  {"designation": "242.0", "family": "Cast 2xx.x", "nominal_composition": "Al-4.0Cu-1.5Mg-2.0Ni"},
  {"designation": "206.0", "family": "Cast 2xx.x", "nominal_composition": "Al-4.6Cu-0.3Mg-0.3Mn-0.22Ti"},
  {"designation": "520.0", "family": "Cast 5xx.x", "nominal_composition": "Al-10.0Mg"},
  {"designation": "535.0", "family": "Cast 5xx.x", "nominal_composition": "Al-6.9Mg-0.18Mn-0.18Ti"},
  {"designation": "713.0", "family": "Cast 7xx.x", "nominal_composition": "Al-7.5Zn-0.35Mg-0.7Cu"},
  {"designation": "771.0", "family": "Cast 7xx.x", "nominal_composition": "Al-7.0Zn-0.9Mg-0.13Cr-0.12Ti"},
  {"designation": "850.0", "family": "Cast 8xx.x", "nominal_composition": "Al-6.2Sn-1.0Cu-1.0Ni"},
  {"designation": "851.0", "family": "Cast 8xx.x", "nominal_composition": "Al-5.5Sn-2.5Si-1.0Cu-0.5Ni"},
  {"designation": "1420", "family": "Russian Al-Li", "nominal_composition": "Al-2.2Li-6.2Mg-0.1Zr"},
  {"designation": "1441", "family": "Russian Al-Li", "nominal_composition": "Al-1.7Li-1.6Cu-0.9Mg-0.1Zr"},
  {"designation": "AlSi10Mg", "family": "AM Specialty", "nominal_composition": "Al-10Si-0.4Mg"},
  {"designation": "Scalmalloy", "family": "AM Specialty", "nominal_composition": "Al-4.6Mg-0.7Sc-0.35Zr-0.5Mn"},
  {"designation": "AlSi7Mg (A357-AM)", "family": "AM Specialty", "nominal_composition": "Al-7Si-0.6Mg"},
  {"designation": "AlSi12", "family": "AM Specialty", "nominal_composition": "Al-12Si"},
  {"designation": "AlSi3.5Mg2.5", "family": "AM Specialty", "nominal_composition": "Al-3.5Si-2.5Mg"},
  {"designation": "Al-5Mg-2Si-0.7Mn-0.15Zr", "family": "AM Specialty", "nominal_composition": "Al-5Mg-2Si-0.7Mn-0.15Zr"},
  {"designation": "A20X (Aeromet)", "family": "AM Specialty", "nominal_composition": "Al-4.5Cu-0.25Mg-TiC"},
  {"designation": "6061-RAM", "family": "AM Specialty", "nominal_composition": "Al-1.0Mg-0.6Si-0.28Cu"},
  {"designation": "7A77", "family": "AM Specialty", "nominal_composition": "Al-7.7Zn-2.4Mg-1.5Cu-0.15Zr"},
  {"designation": "Al-9.3Ce-0.11Sc-0.04Er-0.22Zr", "family": "Specialty / Research RE Alloy", "nominal_composition": "Al-9.3Ce-0.11Sc-0.04Er-0.22Zr"},
  {"designation": "Al-8Ce-10Mg", "family": "Specialty / Research RE Alloy", "nominal_composition": "Al-8Ce-10Mg"},
  {"designation": "Al-3.5Cu-1.5Mg-0.5Ag", "family": "Specialty / Al-Cu-Mg-Ag", "nominal_composition": "Al-3.5Cu-1.5Mg-0.5Ag"},
  {"designation": "Al-5.5Mg-0.3Mn-0.15Sc-0.1Zr", "family": "Specialty / Sc-modified 5xxx", "nominal_composition": "Al-5.5Mg-0.3Mn-0.15Sc-0.1Zr"},
  {"designation": "Al-33Cu", "family": "Specialty / Brazing Eutectic", "nominal_composition": "Al-33Cu"},
  {"designation": "Al-5Mg-0.7Mn-0.15Sc-0.05Er-0.1Zr", "family": "Specialty / Multi-RE Alloy", "nominal_composition": "Al-5Mg-0.7Mn-0.15Sc-0.05Er-0.1Zr"}
]
```

References

1. (mann2011hotdeformationof pages 39-43): RED Mann. Hot deformation of aluminum-copper-magnesium powder metallurgy alloys. Unknown journal, 2011.

2. (mann2011hotdeformationof pages 33-39): RED Mann. Hot deformation of aluminum-copper-magnesium powder metallurgy alloys. Unknown journal, 2011.

3. (ablakatov2022aluminumlithiumalloystypes pages 2-4): I.K. Ablakatov, B.M. Baiserikov, M.B. Ismailov, and M.R. Nurgozhin. Aluminum-lithium alloys: types, properties, application, and production technologies. overview. Kompleksnoe Ispolʹzovanie Mineralʹnogo syrʹâ/Complex Use of Mineral Resources/Mineraldik Shikisattardy Keshendi Paidalanu, 323:5-14, May 2022. URL: https://doi.org/10.31643/2022/6445.34, doi:10.31643/2022/6445.34. This article has 14 citations.

4. (gonzalez2023developmentandproductiona pages 48-51): P Rodríguez González. Development and production of al-cu-li wires by powder metallurgy routes and their application in waam techniques. Unknown journal, 2023.

5. (gonzalez2023developmentandproduction pages 48-51): P Rodríguez González. Development and production of al-cu-li wires by powder metallurgy routes and their application in waam techniques. Unknown journal, 2023.

6. (wangombe2022developmentofrecycled pages 41-46): DN Wang'ombe. Development of recycled friendly aluminium alloys for automotive and structural applications. Unknown journal, 2022.

7. (remorUnknownyearexperimentalanalysisof pages 34-40): F Remor. Experimental analysis of fatigue behaviour and metallographic characterization of sc-al alloy coupons. Unknown journal, Unknown year.

8. (remorUnknownyearexperimentalanalysisof pages 40-45): F Remor. Experimental analysis of fatigue behaviour and metallographic characterization of sc-al alloy coupons. Unknown journal, Unknown year.

9. (adetan2025microstructuralandmechanical pages 66-72): O Adetan. Microstructural and mechanical evolution of an al-ce-er-sc-zr alloy at elevated temperatures. Unknown journal, 2025.

10. (adetan2025microstructuralandmechanical pages 60-66): O Adetan. Microstructural and mechanical evolution of an al-ce-er-sc-zr alloy at elevated temperatures. Unknown journal, 2025.