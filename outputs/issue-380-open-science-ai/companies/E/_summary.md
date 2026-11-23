# Group E: lab automation, cloud labs, AI-for-science (Nov 2026)

| Name | Openness | Origin | Founded | Outcome | Latest value (date) |
|---|---|---|---|---|---|
| Opentrons | 3→2 | founder (DIYbio) | 2014 | private; Series E | ~$170M est. (2026-10) |
| Emerald Cloud Lab | 0→1 | founder | 2010 | operating | n/a |
| Strateos (Transcriptic) | 1→1 | founder | 2012 | quit hosted lab 2023; status unclear | n/a |
| Benchling | 0→0 | founder (MIT/YC) | 2012 | private, no IPO | $6.1B (2021-11) |
| Chemspeed | 0→0 | n/a | ≤2001 | acquired by Bruker 2024 | undisclosed |
| Schrödinger | 0→1 | academic (Columbia) | 1990 | public 2020 | $1.83B cap (2026-11-23) |
| Citrine Informatics | 1→1 | founder | 2013 | private | n/a |
| Kebotix | 0→0 | n/a | n/a | no news since ~2022 | n/a |
| Periodic Labs | 0→0 | founder (OpenAI/DeepMind) | 2025 | private | n/a ($300M raised) |
| Lila Sciences | 0→0 | Flagship venture | 2023 | private | >$1.3B (2025-10) |
| Radical AI | 1→1 | founder | 2025 | private | n/a ($55M) |
| Orbital Industries (ex-Orbital Materials) | 2→2 | n/a | n/a | renamed, pivoting | n/a |
| CuspAI (UK) | 0→0 | founder | 2024 | private | n/a (>$650M) |
| Chemify (UK) | 0→0 | academic (Glasgow) | 2022 | private | n/a (≥$93M) |
| Atinary (CH) | 0→0 | founder | n/a | private | n/a |
| EvolutionaryScale | 1→2 | Meta FAIR spin-out | 2024 | absorbed into non-profit Biohub | n/a ($142M seed) |
| Isomorphic Labs (UK) | 0→1 | Alphabet spin-off | 2021 | private | n/a ($7.7B raised) |
| Recursion | 0→1 | n/a | 2013 | public 2021; bought Exscientia | $1.66B cap (2026-11-23) |

## Observations

1. **Open to enter, closed to scale.** Opentrons is the only lab-automation firm that started with open hardware: the OT-One's files are Apache-2.0. It closed the hardware with the OT-2 (2018) and kept Apache-2.0 software, which is why it dominates academic SDL builds. Elsewhere openness is confined to languages and standards: Autoprotocol (BSD) and ECL's SLL ("research use", licence unnamed).
2. **Opentrons' bust was COVID, not openness.** Its valuation went from $1.8B (2021, SoftBank) to about $162M (Series D, Nov 2025; Forge estimate), roughly −91%, after its testing lab closed with 185 jobs lost. It still has 11,000+ robots in 80+ countries.
3. **Hosted cloud labs struggled.** Strateos abandoned its hosted lab (Apr 2023) and its web presence has since gone stale. Kebotix's news stops in 2022. ECL survived a move and layoffs by anchoring on public money: CMU's $40M lab and the NSF GEMSTONE testbed ($20M grant, 2026).
4. **The 2025–26 boom is overwhelmingly closed.** Isomorphic ($7.7B), CuspAI (>$650M), Lila ($550M), Periodic ($300M), Radical ($55M) and Chemify (>$50M) together raised about $9.3B. Only Orbital (Apache-2.0 Orb models) and Radical (MIT TorchSim) release OSI-licensed artifacts, and both are peripheral to the product. Lila publishes only preprints; Periodic and CuspAI release nothing.
5. **Open public data in, restricted outputs out.** AlphaFold was trained on more than 170,000 PDB structures, yet AF3 weights are non-commercial and bar training similar models. Recursion's OpenPhenom (trained partly on public JUMP-CP data) is non-commercial, and its RxRx releases are under 1% of its data. CuspAI builds on licensed CCDC/ICSD data and Meta's open models. Orbital, which publishes weights trained on Meta's open OMol25, is the exception.
6. **"Open" is being redefined as API access or papers.** Examples: Opentrons' "open, API-driven" robots, SLL "for research use" and Lila's arXiv output.
7. **Non-profits relicense toward open.** EvolutionaryScale went from a non-commercial licence under VC ownership (2024) to MIT after joining Biohub, the group's only OSI relicensing.
8. **Closed incumbents persist.** Schrödinger ($256M revenue in 2025, closed for 35 years) lists open engines (OpenMM, OpenFF, GROMACS) only as competitors. Bruker bought Chemspeed (2024) and partnered with Atinary (2026), forming a closed end-to-end SDL stack.

*Caveat: the shared WebSearch budget ran out after 28 queries (Opentrons, ECL, Strateos). The other 15 profiles rely on direct fetches of primary pages and are mostly low confidence.*
