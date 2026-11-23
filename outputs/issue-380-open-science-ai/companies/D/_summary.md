# Group D: open hardware, maker and device companies (with closed comparators)

There are 22 files; SiFive and RISC-V International are split. Openness uses the hardware scale (0-4). Values are USD; n/d = not disclosed or not found.

| Name | Openness | Origin | Founded | Outcome | Latest value (date) |
|---|---|---|---|---|---|
| Arduino | 3→3 | academic, IT | 2005 | Qualcomm deal (2025-10), closing unconfirmed | n/d |
| Raspberry Pi | 1→2 | nonprofit, UK | 2012 | LSE IPO 2024 | $1.19B market cap (2026-11-23) |
| Adafruit | 3→3 | founder, US | 2005 | bootstrapped | revenue $45M (2016) |
| SparkFun | 3→3 | founder, US | 2003 | private | n/d |
| Seeed Studio | 3→3 | founder, CN | 2008 | private | n/d |
| Prusa Research | 3→2 | founder, CZ | 2012 | bootstrapped; layoffs 2026 | revenue ~$157M (2024) |
| MakerBot | 3→0 | founder, US | 2009 | Stratasys 2013; UltiMaker 2022 | $403M acquisition (2013-06) |
| UltiMaker | 2→1 | founder, NL | 2011 | PE-owned since 2022 | n/d |
| LulzBot / Aleph Objects | 3→3 | founder, US | 2011 | 2019 collapse; FAME 3D | n/d |
| RepRap | 4→4 | academic, UK | 2005 | community project | n/a |
| Bambu Lab | 1→1 | founder, CN | 2020 | VC; 2025 firmware lock | n/d |
| Formlabs | 0→0 | academic, US | 2011 | VC; revenue >$250M (2025) | $2B private (2021-05) |
| Creality | 0→2 | founder, CN | 2014 | HKEX 2026 (unverified) | n/d |
| SiFive | 3→2 | academic, US | 2015 | VC; Intel's ~$2B offer (2021) fell through | $3.65B private (2026-04) |
| RISC-V International | 4→4 | academic, CH | 2015 | Swiss nonprofit | revenue $8.6M (2024) |
| Open Compute Project | 4→4 | corporate, US | 2011 | foundation | n/a |
| Oxide Computer | 2→2 | founder, US | 2019 | VC, $834M raised; profitable 2026 | n/d |
| Framework | 1→2 | founder, US | 2020 | VC, ~$45M raised | n/d |
| System76 | 1→2 | founder, US | 2005 | private | n/d |
| Pine64 | ?→2 | founder, HK | 2015 | PinePhone Pro ended 2025 | n/d |
| OpenBCI | 3→2* | founder, US | 2013 | private | n/d |
| Sofar Ocean / OpenROV | 3→1 | founder, US | 2011 | 2019 merger; VC | n/d |

\*Inferred, low confidence.

## Observations

1. **Open-hardware firms stay small and private.** Adafruit ($45M revenue, 2016), SparkFun (~140 staff) and Prusa (~$157M revenue) have no valuation. The top values are closed or closing firms: Formlabs ($2B), SiFive ($3.65B; open RTL archived 2021) and Raspberry Pi ($1.19B).
2. **Closing didn't save MakerBot.** The Replicator 2 closed in 2012, nine months before Stratasys paid $403M. All its goodwill was written off by end-2015.
3. **Clone risk is real but uneven.** Arduino sells one genuine board per 5-6 clones (2023). Prusa withheld MK4 PCB layouts (2023) and put the CORE One under a non-commercial licence (2025), citing clones and Chinese patents; Hackaday disputes the scale. Creality was itself accused of GPL violations (2018-2022).
4. **Open software, closed hardware wins share.** Bambu Lab built its slicer on PrusaSlicer (AGPL), then added authorization firmware (2025). Raspberry Pi passed 75M units on closed Broadcom silicon. Oxide and Framework open firmware, not boards.
5. **Bootstrapped firms last.** Adafruit (21 years, no outside funding) and SparkFun (23 years, no patents) have no recorded exits. Prusa (~1,144 staff, no VC) made its first layoffs in 2026.
6. **Consolidation.** Arduino went to Qualcomm, and its terms revised on 2025-10-29 bar reverse-engineering its platform. MakerBot went to Stratasys, then UltiMaker (PE-owned), and LulzBot to FAME 3D. The open designs outlive their owners: FAME 3D still publishes GPL source.
7. **Foundations keep openness.** RISC-V and OCP stay at level 4 and created markets for closed member products: SiFive, and ~$154B of OCP-recognized spending (IDC, 2025).
8. **Non-commercial licences are a halfway house.** OpenROV, Ultimaker and Prusa all used them. None meets the OSHW definition, and each preceded or accompanied closing.
9. **OSHWA certification is concentrated** (through 2020): Adafruit ~413, SparkFun ~264, Aleph Objects ~25; none for Arduino, Raspberry Pi or Seeed.

**Caveat:** WebSearch's shared budget ran out after 32 group D searches, so 16 files use WebFetch only (see `search_tool`).
