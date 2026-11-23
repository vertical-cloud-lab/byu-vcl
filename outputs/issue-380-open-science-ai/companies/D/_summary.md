# Group D: open hardware, maker and device companies (with closed comparators)

There are 22 files; SiFive and RISC-V International are split in two. Openness uses the hardware column (0-4). Values are USD. "n/d" means not disclosed or not found.

| Name | Openness | Origin | Founded | Outcome | Latest value (date) |
|---|---|---|---|---|---|
| Arduino | 3→3 | academic, IT | 2005 | Qualcomm deal announced 2025-10; closing unconfirmed | n/d (price undisclosed) |
| Raspberry Pi | 1→2 | nonprofit, UK | 2012 | LSE IPO 2024 | $1.19B market cap (2026-11-23) |
| Adafruit | 3→3 | founder, US | 2005 | bootstrapped, operating | n/d; revenue $45M (2016) |
| SparkFun | 3→3 | founder, US | 2003 | private, operating | n/d |
| Seeed Studio | 3→3 | founder, CN | 2008 | private, operating | n/d |
| Prusa Research | 3→2 | founder, CZ | 2012 | bootstrapped; first layoffs 2026 | n/d; revenue ~$157M (2024) |
| MakerBot | 3→0 | founder, US | 2009 | Stratasys 2013; merged into UltiMaker 2022 | $403M acquisition (2013-06) |
| UltiMaker | 2→1 | founder, NL | 2011 | private-equity majority after 2022 merger | n/d |
| LulzBot / Aleph Objects | 3→3 | founder, US | 2011 | 2019 collapse; assets to FAME 3D | n/d |
| RepRap | 4→4 | academic, UK | 2005 | community; RepRapPro closed 2016 | n/a |
| Bambu Lab | 1→1 | founder, CN | 2020 | VC-backed; 2025 authorization firmware | n/d |
| Formlabs | 0→0 | academic, US | 2011 | VC-backed; revenue >$250M (2025) | $2B private (2021-05) |
| Creality | 0→2 | founder, CN | 2014 | HKEX listing 2026 (company page only) | n/d |
| SiFive | 3→2 | academic, US | 2015 | VC; Intel's reported ~$2B offer (2021) came to nothing | $3.65B private (2026-04) |
| RISC-V International | 4→4 | academic, CH | 2015 | Swiss nonprofit since 2020 | n/a; revenue $8.6M (2024) |
| Open Compute Project | 4→4 | corporate, US | 2011 | foundation | n/a |
| Oxide Computer | 2→2 | founder, US | 2019 | VC, $834M raised; profitable 2026 | n/d |
| Framework | 1→2 | founder, US | 2020 | VC, ~$45M raised | n/d |
| System76 | 1→2 | founder, US | 2005 | private, operating | n/d |
| Pine64 | ?→2 | founder, HK | 2015 | operating; PinePhone Pro discontinued 2025 | n/d |
| OpenBCI | 3→2* | founder, US | 2013 | private, operating | n/d |
| Sofar Ocean / OpenROV | 3→1 | founder, US | 2011 | 2019 merger; VC | n/d |

\*Inferred, low confidence.

## Observations

1. **Open-hardware firms stay small and private.** Adafruit ($45M revenue in 2016), SparkFun (~140 staff in 2018) and Prusa (~$157M in 2024) have no disclosed valuation. The largest values belong to closed or closing firms: Formlabs ($2B), SiFive ($3.65B, which archived its open RTL in 2021) and Raspberry Pi ($1.19B, with closed boards).
2. **Closing didn't save MakerBot.** It closed the Replicator 2 in 2012, nine months before Stratasys paid $403M. By the end of 2015 Stratasys had written off all of MakerBot's goodwill.
3. **Clone risk is real but uneven.** Arduino sells about one genuine board for every 5-6 clones (2023). Prusa withheld its MK4 PCB layouts (2023) and put the CORE One under a non-commercial licence (2025), citing clones and Chinese patents; Hackaday disputes how many clones there are. Creality is more often the accused copier, with GPL violations from 2018 to 2022.
4. **Open software, closed hardware wins share.** Bambu Lab (level 1) built its slicer on AGPL-licensed PrusaSlicer, then gated printer control behind authorization firmware in 2025. Raspberry Pi passed 75M units on closed Broadcom silicon. Oxide, Framework and System76 open their firmware, not their boards.
5. **Bootstrapped firms last.** Adafruit has run 21 years without outside funding and SparkFun 23 years with no patents, neither with an exit. Prusa grew to ~1,144 staff without venture capital but cut jobs in 2026 under pressure from closed rivals.
6. **Consolidation.** The pattern is Arduino to Qualcomm, MakerBot to Stratasys to private-equity-owned UltiMaker, and LulzBot to FAME 3D. Arduino revised its terms on 2025-10-29 to bar reverse-engineering of its platform. Open designs outlive their owners: FAME 3D still publishes GPL source.
7. **Openness lasts best in foundations.** RISC-V (CC BY 4.0 spec, Swiss nonprofit) and OCP stay at level 4 and created markets, while their members sell closed products: SiFive, and an IDC estimate of ~$154B in OCP-recognized spending in 2025.
8. **Non-commercial licences are a halfway house.** OpenROV (CC BY-NC-SA), Ultimaker (CC BY-NC) and Prusa (OCL) all used them. None meets the OSHW definition, and each preceded or accompanied closing.
9. **OSHWA certification is concentrated** (through 2020): Adafruit ~413, SparkFun ~264, Aleph Objects ~25. None was found for Arduino, Raspberry Pi or Seeed.

**Caveat:** WebSearch's shared budget ran out after 32 group D searches, so 16 files rely on WebFetch alone (see `search_tool`). Financials are thin for Seeed, OpenBCI, Sofar, Pine64, SparkFun and Bambu.
