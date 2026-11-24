# Group I: AI-for-science models and datasets (Nov 2026)

19 entries; WebFetch only (2026-11-23). Score = initial→current on a 0–4 scale over code, weights and data:

- 0: no weights
- 1: non-commercial (NC) or gated weights
- 2: open core
- 3: OSI or CC BY code and weights
- 4: level 3 plus open training data, or a publicly stewarded open database

n.s. = not stated on fetched pages.

| Name | Developer | First release | Code / weights / data | Score | Trained on |
|---|---|---|---|---|---|
| AlphaFold 2 + AFDB | Google DeepMind, EMBL-EBI | 2021 | Apache-2.0 / CC BY-NC→CC BY (2022) / CC BY | 1→4 | PDB, UniRef, BFD |
| AlphaFold 3 | Google DeepMind, Isomorphic | 2024 | none→CC BY-NC-SA→Apache-2.0 (2026) / gated NC / n.a. | 0→1 | PDB |
| OpenFold, OpenFold3 | Columbia, OpenFold consortium | 2021 | Apache-2.0 / released / CC BY | 3→4 | OpenProteinSet (PDB) |
| Boltz-1, Boltz-2 | academic, then Boltz PBC | 2024 | MIT / MIT, newest proprietary / downloadable | 4→2 | PDB, OpenFold distillation |
| Chai-1 | Chai Discovery | 2024 | NC→Apache-2.0 (2024) / same / n.s. | 1→2 | n.s. |
| RoseTTAFold, RFdiffusion | UW Institute for Protein Design | 2021 | MIT, BSD / NC→BSD (2023) / n.s. | 1→3 | n.s. |
| ESM, ESM3 | Meta → EvolutionaryScale → Biohub | 2019 | MIT / MIT→NC→MIT (2026) / Atlas CC BY | 3→2 | UniRef |
| Evo 2 | Arc Institute | 2025 | Apache-2.0 / Apache-2.0 / Apache-2.0 | 4→4 | OpenGenome2 |
| GNoME | Google DeepMind | 2023 | Apache-2.0 / none / CC BY-NC | 1→1 | Materials Project (2018) |
| MatterGen | Microsoft | 2025 | MIT / MIT / released | 4→4 | MP, Alexandria |
| MatterSim | Microsoft | 2024 | MIT / MIT (small only) / closed | 2→2 | in-house DFT |
| FAIR Chemistry (OC20 to UMA) | Meta FAIR | 2020 | MIT / custom, gated / CC BY | 3→2 | OC20, OMat24, OMol25, ODAC, OMC25 |
| MACE-MP | Csányi group | 2023 | MIT / MIT + ASL (NC) / open | 4→2 | MPtrj, sAlex, OMat24, OMol25 |
| CHGNet | Ceder group, LBNL | 2023 | BSD / in repo / MPtrj | 4→4 | MPtrj |
| M3GNet, MatGL | Materials Virtual Lab, Intel Labs | 2022 | BSD-3 / in repo / figshare | 4→4 | MP relaxations |
| Orb | Orbital Materials | 2024 | Apache-2.0 / Apache-2.0 / public | 3→3 | OMol25 (others n.s.) |
| SevenNet | MDIL-SNU | 2023 | GPL-3.0→MIT (2025) / repo / public | 4→4 | MPtrj, sAlex, OMat24 |
| BioNeMo, ALCHEMI | NVIDIA | 2024 | Apache-2.0 / upstream / n.a. | 2→2 | hosts others' models |
| Matbench (+ Discovery) | Materials Project (LBNL) | 2020 | MIT / n.a. / n.s. | 4→4 | benchmark |

## Observations

1. **More open than frontier LLMs.** The mean current score is 2.8 (median 3), and 10 of 19 score 3–4. Group C's eight frontier-LLM companies average 1.6 (company-level scores, so indicative).
2. **Corporate labs split by business model.** Meta publishes CC BY data (OMat24 and OMol25, 200M+ DFT calculations) but gates its custom-licensed weights. Microsoft released MatterGen fully open but keeps MatterSim's best versions in Azure. DeepMind restricts: AF3 weights are gated NC, and GNoME has no weights and NC data. NVIDIA opens frameworks to sell GPUs.
3. **Open clones followed the restriction.** AF3 launched on 2024-05-08 with "Code is not provided". Boltz-1 (MIT, Nov 2024), Chai-1 (Apache-2.0, 2024-11-27) and OpenFold3 (Apache-2.0, 2025) followed. Google later opened the code (Apache-2.0 on 2026-06-09) but never the weights.
4. **Openness tracks owner incentives.** ESM went from MIT at Meta to NC at VC-backed EvolutionaryScale (2024), then back to MIT under non-profit Biohub (2026-05-27). Boltz added proprietary models and announced a $110M Series A on 2026-11-18. Of 18 recorded licensing events, 11 were openings and 7 closings.
5. **Non-corporate developers are more open** (3.4 against 2.3 for corporate). Baker's lab moved weights from NC to BSD (2023) and SevenNet from GPL to MIT (2025), but MACE's newest models are NC despite CC BY training data.
6. **Everything rests on public data.** 14 of 17 models are confirmed trained on public datasets (PDB, Materials Project/MPtrj, Alexandria, UniRef, OMat24/OMol25, OpenGenome2); only MatterSim uses unreleased in-house data. GNoME put NC records back into the CC BY Materials Project.
7. **Permissive releases see more use** (age confounds this). ESM-2 650M (MIT) had 3.02M Hugging Face downloads a month against 2,268 for ESM3-open.
