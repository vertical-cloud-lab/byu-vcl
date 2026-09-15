# Edison Scientific: state of the art and future directions for CubXL-style closed-loop workflows

Run 2026-09-15 for [#213](https://github.com/vertical-cloud-lab/byu-vcl/issues/213), at Sterling
Baird's request. Five `paperqa3-high` (`LITERATURE_HIGH`) queries about where automated
dosing + conductivity + spectroscopy sits in the self-driving-lab literature, followed by an
independent verification pass that fetched the actual articles.

Trajectories, answers, reference blocks and the agent's own artifacts are in
[`outputs/edison-sdl-futures/`](../outputs/edison-sdl-futures). Task IDs are in `_task_ids.json`,
so a later session can re-fetch any of them.

| Query | Topic |
|---|---|
| `q1_sota_electrolyte_sdl` | SDLs that close the loop on **ionic conductivity** for liquid electrolyte formulation |
| `q2_inline_spectroscopy_sensor_fusion` | In-line ATR-FTIR / Raman / NIR as a composition sensor; **spectroscopy + conductivity on the same sample**; nonlinear spectral unmixing |
| `q3_future_directions_open_problems` | Open problems and roadmap items for SDLs, 2023–2026 |
| `q4_low_cost_open_hardware_sdl` | Low-cost, open, modular SDL hardware; precedent for a "one platform, many instruments" claim |
| `q5_active_learning_formulation_data_efficiency` | Active learning / BO for multicomponent formulation, including spectra as the observable |

## How the references were verified

Two levels, deliberately separated.

**Existence and metadata** — every DOI Edison cited was resolved against Crossref, and anything
Crossref missed was retried against DataCite and the arXiv API. This matters because Crossref does
not mint arXiv DOIs: nine `10.48550/arXiv.*` references and one TU Delft thesis DOI look like
fabrications if you stop at Crossref, and are real.

**Content** — open-access full text was fetched and the specific numeric claims were searched for
in it, so a claim counts as verified only if the number appears in the paper.

Both halves run from the stream-cam Pi, via
[`scripts/refcheck_pi.py`](../scripts/refcheck_pi.py) (stdlib only, nothing installed on the Pi).
PDFs are copied back to the runner rate-capped and the text extraction happens there.

### Publisher access, measured 2026-09-15

| Source | Actions runner | Pi (residential) |
|---|---|---|
| Crossref, OpenAlex, Unpaywall, Semantic Scholar, DataCite | yes | yes |
| Europe PMC `fullTextXML`, arXiv PDF, nature.com PDF | mixed | yes |
| RSC, Wiley, ACS, ScienceDirect, ChemRxiv | **403** | **403** |

The RSC/Wiley/ACS/Elsevier block is **bot fingerprinting, not datacentre IP** — the residential
address does not help. CLAUDE.md previously recorded "RSC 403s both the runner and the Pi" for one
article; this generalises, and it is the reason `refcheck_pi.py` falls back to open-access mirrors
(Europe PMC, arXiv, repository copies), which recovers most but not all of them.

## Verification result

| | |
|---|---|
| Unique DOIs cited across the five answers | **80** |
| Resolved via Crossref | 70 |
| Resolved via DataCite / arXiv | 10 |
| **Unresolved — i.e. possibly fabricated** | **0** |
| Full text retrieved and searched | 39 |

Full texts that could not be retrieved are concentrated in RSC (10), ACS (9) and Wiley (4), and are
paywall/bot-block failures rather than reference problems — metadata for all of them checks out.

### Claims checked against full text

Twenty specific numeric claims from the four platform descriptions that matter most for #213.
Nineteen appear verbatim in the papers.

**Dave et al. 2022, Clio/Dragonfly ([10.1038/s41467-022-32938-1](https://doi.org/10.1038/s41467-022-32938-1))** — confirmed:
42 experiments in two work-days; six-fold acceleration versus random search on the same robot;
optimum 13.7 mS/cm at EC:DMC 40:60 by mass, 0.9 m LiPF₆, 26–28 °C; PalmSens4 EIS at five
frequencies between 14 and 800 kHz; <10 ppm H₂O; 120-sample triplicate repeatability study at
±1.3%; >1000-point grid over 10–12 levels per axis.

Not confirmed: the claim that Dragonfly used **Thompson sampling / top-two EI / UCB** acquisitions
does not appear in the retrieved text — plausibly true of the Dragonfly package, and possibly in
the supplementary information, but it is not in the article body. Likewise the "**~3× workflow
efficiency versus an 8 h/day human**" figure. Treat both as unsourced.

**Whitacre et al. 2019, CMU test stand ([10.1149/2.0521916jes](https://doi.org/10.1149/2.0521916jes))** — all confirmed:
Topac K = 1.0 four-pole glass/Pt probe in a custom PTFE flow-through housing; Consort C3410
analyser; 7 mL binary blends in 1 mL steps; ~7 minutes per point; the 800-test campaign row;
20 °C reference with 0.5 mS/cm standard error.

**Rahmanian et al. 2023, Helmholtz Münster ([10.1038/s41597-023-01936-3](https://doi.org/10.1038/s41597-023-01936-3))** — all confirmed:
96 formulations in 8 h by gravimetric dosing of **solids and liquids**; nitrogen atmosphere;
EIS from −30 to 60 °C in 10 °C steps after 2 h equilibration; 40 mV AC, 20 kHz–50 Hz; MADAP;
504 JSON files; 5035 measurements.

**Noh et al. 2024, PNNL ([10.1038/s41467-024-47070-5](https://doi.org/10.1038/s41467-024-47070-5))** — confirmed:
22 solvent candidates plus 2079 binary combinations at 9 volume fractions; fewer than 10% of
candidates measured. Not confirmed: the ">13× throughput advantage" figure.

## What the answers say, in brief

**Closed-loop conductivity optimisation is rare.** Only **Clio/Dragonfly** (Dave 2022) closes the
full loop of dose → measure ionic conductivity → choose the next composition, and it does so in a
dry-argon glovebox on non-aqueous carbonates. Whitacre 2019 is the aqueous, ambient-condition
precursor and used a **four-pole flow-through probe**, which is the same electrode arrangement
Porter's group had 3D-printed at CU Boulder. Rahmanian 2023 dose**s powders and liquids**
gravimetrically under N₂ and measures conductivity by EIS, but had no online optimiser.

**Nobody in the retrieved literature closes the loop on conductivity *and* spectroscopy at once.**
Simultaneous spectroscopy-plus-conductivity measurement exists — Kachko 2015 fused NIR with
conductivity, density, pH, sound velocity and refractive index on a CO₂-capture pilot plant — but
as *process monitoring*, not as feedback selecting the next formulation. That gap is exactly
Porter's proposition, and it supports his read that the dosing-plus-prediction loop is established
while adding spectroscopy is what would be new.

**The nonlinear-unmixing problem Porter described is real and acknowledged.** Angulo 2022 found
linear models beat an ANN for four-component mixtures (R² 0.955–0.986) — but under near-additive
mixing, so it is not evidence about ion pairing. Maggioni 2019 showed MCR-ALS producing misleading
components precisely when Beer–Lambert superposition fails. The rule of thumb across the retrieved
work: linear models need ~25–50 samples for 3–6 components; nonlinear models need substantially
more, which is consistent with Porter's undergraduates generating training data by hand.

**Held-out validation is the recognised weak point**, matching Porter's "enough data to train it
and not enough to test it." The better-practice examples use Kennard–Stone partitioning plus an
independent challenge sample (Zavala-Ortiz 2022: 168 spectra split 135/33, then an independent
medium as a blind test).

**Open problems** (q3): interoperability standards, FAIR capture, cross-lab reproducibility,
missing negative results, closing the loop on **multiple orthogonal modalities** rather than one
scalar objective, multi-fidelity and multi-objective optimisation, transfer learning, error
recovery, and cost. Edison's read is that all of them remain open as of 2026.

## Caveat

These are literature-agent outputs. The verification above establishes that the references exist
and that the specific numbers quoted appear in the papers. It does not establish that Edison's
*interpretation* of each paper is correct, and it could not check the ~40 articles behind
publisher bot-blocks at all.
