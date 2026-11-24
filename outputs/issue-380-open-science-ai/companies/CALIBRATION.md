# Inter-rater calibration of the openness scores (issue #380)

An independent second scoring of `openness_initial` and `openness_current` for all 143 case
files in `companies/{A..G}/`, compared against the scores the original group agents
assigned. Per-file scores and notes are in [`calibration_scores.csv`](calibration_scores.csv).
Prepared 2026-11-24.

## Method

A Python script loaded each case JSON, **deleted `openness_initial` and `openness_current`
from the in-memory copy** (and asserted they were gone), and printed only identifying metadata
(name, slug, category, subcategory, origin, founded_year, ownership_status, used to pick the
rubric column and the starting date) plus the evidence fields `flagship_projects`,
`business_model`, `openness_notes`, `license_history`, `relicensing_events`,
`openness_effect_assessment` and `key_takeaway`. The files were read group by group in 21
batches of 5 to 9, and each was scored against the [SCHEMA.md](SCHEMA.md) rubric, applied
literally. The hardware column was used for the 37 `hardware` files and the two
hardware-standards foundations (Open Compute Project, RISC-V International). The software/AI
column was used for everything else, including big-tech files that declare they are scored on
their AI and developer-platform strategy. Level 4 was given to open foundations, government
open-data and science infrastructure, and non-profit or public stewards whose whole output is
openly licensed. Single-company, single-lab or single-maintainer projects without formal
governance were given 3. "Initial" was taken as the earliest state the file's evidence
describes for the scope it scores, usually the founding year or the first public release of
the flagship. All 143 rescored pairs were written to `calibration_scores.csv` first. Only then
did a second script join the original values from the JSONs and compute the statistics:
exact agreement, agreement within one level, Spearman's ρ (scipy, average ranks for ties) and
quadratic-weighted Cohen's κ over the fixed categories 0–4. `pine64` has a null original
`openness_initial`, so the initial statistics use n = 142. No case JSON was modified, and no
web access or git was used.

**The re-score was blind to the score fields, but not to the original scorers' reasoning.**
In 118 of the 143 files (83%), the evidence text itself states a numeric level: usually
`openness_notes`, with phrases such as "Initial 3 … Current 2", "scored 3 rather than 4" or
"level 1". By group, that is A 17/18, B 13/23, C 17/18, D 22/22, E 13/18, F 15/23 and G 21/21.
Many other files use the rubric's level names ("open core", "source-available", "only
peripheral parts open"). The figures below are therefore an upper bound on true inter-rater
reliability. As a partial check, the 25 files whose evidence states no number agreed exactly
in 24 of 25 cases (96%) for both measures. That is similar to the flagged files (initial 92%,
current 96%), but the unflagged set is mostly unambiguous cases: closed incumbents,
foundations and plain open core. Of the 12 files with a real disagreement (`pine64` aside),
9 have a rescored value that departs from a number written in that file's own notes.

## Agreement statistics

### `openness_initial`

| Subset | n | Exact % | Within-1 % | Spearman ρ | QW kappa | Mean orig | Mean rescored | Mean (rescored − orig) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **All** | 142 | 93.0 | 99.3 | 0.96 | 0.97 | 1.89 | 1.89 | +0.00 |
| A | 18 | 100.0 | 100.0 | 1.00 | 1.00 | 2.72 | 2.72 | +0.00 |
| B | 23 | 95.7 | 100.0 | 1.00 | 0.97 | 2.30 | 2.26 | -0.04 |
| C | 18 | 83.3 | 100.0 | 0.96 | 0.96 | 1.56 | 1.39 | -0.17 |
| D | 21 | 90.5 | 100.0 | 0.96 | 0.97 | 2.38 | 2.29 | -0.10 |
| E | 18 | 100.0 | 100.0 | 1.00 | 1.00 | 0.50 | 0.50 | +0.00 |
| F | 23 | 82.6 | 95.7 | 0.87 | 0.87 | 2.52 | 2.78 | +0.26 |
| G | 21 | 100.0 | 100.0 | 1.00 | 1.00 | 1.05 | 1.05 | +0.00 |

### `openness_current`

| Subset | n | Exact % | Within-1 % | Spearman ρ | QW kappa | Mean orig | Mean rescored | Mean (rescored − orig) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **All** | 143 | 95.8 | 100.0 | 0.99 | 0.99 | 1.81 | 1.81 | +0.00 |
| A | 18 | 100.0 | 100.0 | 1.00 | 1.00 | 1.67 | 1.67 | +0.00 |
| B | 23 | 100.0 | 100.0 | 1.00 | 1.00 | 2.17 | 2.17 | +0.00 |
| C | 18 | 88.9 | 100.0 | 0.88 | 0.94 | 1.83 | 1.72 | -0.11 |
| D | 22 | 95.5 | 100.0 | 0.97 | 0.98 | 2.18 | 2.14 | -0.05 |
| E | 18 | 100.0 | 100.0 | 1.00 | 1.00 | 0.72 | 0.72 | +0.00 |
| F | 23 | 87.0 | 100.0 | 0.90 | 0.97 | 2.70 | 2.83 | +0.13 |
| G | 21 | 100.0 | 100.0 | 1.00 | 1.00 | 1.10 | 1.10 | +0.00 |

Confusion matrices (rows: original level, columns: rescored level):

| `initial` | 0 | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| **0** | 38 | 0 | 0 | 1 | 0 |
| **1** | 2 | 15 | 0 | 0 | 0 |
| **2** | 0 | 0 | 21 | 0 | 0 |
| **3** | 0 | 0 | 4 | 43 | 3 |
| **4** | 0 | 0 | 0 | 0 | 15 |

| `current` | 0 | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| **0** | 27 | 0 | 0 | 0 | 0 |
| **1** | 0 | 31 | 0 | 0 | 0 |
| **2** | 0 | 2 | 43 | 0 | 0 |
| **3** | 0 | 0 | 1 | 18 | 3 |
| **4** | 0 | 0 | 0 | 0 | 18 |

## Files differing by 2 or more levels

| Group | File | Original (initial → current) | Rescored | Δ initial | Δ current | Reasoning (≤ 25 words) |
| --- | --- | --- | --- | ---: | ---: | --- |
| F | `openfoam` | 0 → 4 | 3 → 4 | +3 | 0 | Scored from the 2004 GPL release that founded OpenFOAM; the original appears to score proprietary pre-2004 FOAM (Nabla Ltd). |

For context, these are the files differing by exactly one level, plus the null case:

| Group | File | Original | Rescored | Reasoning |
| --- | --- | --- | --- | --- |
| B | `github` | 1 → 1 | 0 → 1 | 2008 evidence is proprietary SaaS only; the open tools (Linguist, Electron, Atom, CLI) came later. |
| C | `alphabet-google` | 3 → 2 | 2 → 2 | Open TensorFlow and Kubernetes beside closed search, ads and services is open core, not whole-product open source. |
| C | `amazon-aws` | 1 → 2 | 0 → 1 | Evidence shows no AWS source releases at first; Firecracker and the foundation forks are peripheral to closed AWS services and Nova. |
| C | `google-deepmind-science` | 4 → 2 | 4 → 1 | The current flagship (AF3) has non-commercial weights, level 1 like the Llama licence; Isomorphic's newer models are proprietary. |
| C | `meta` | 3 → 1 | 2 → 1 | Permissive React and PyTorch beside a closed advertising core is open core (2), not level 3. |
| D | `seeed-studio` | 3 → 3 | 2 → 2 | Flagship KiCad files are published without any licence, and reCamera Pro is withheld, so it fails the "open licence" test for 3. |
| D | `sofar-ocean-openrov` | 3 → 1 | 2 → 1 | OpenROV CAD is CC BY-NC-SA, which is not an open licence; the same file group scored Ultimaker's CC BY-NC designs 2. |
| F | `doe-code` | 3 → 3 | 4 → 4 | A government registry, built as open source with public metadata; the brief treats government open infrastructure as 4. |
| F | `hdf-group` | 3 → 3 | 4 → 4 | A wholly BSD-like data format and library stewarded by a non-profit: fully open science data infrastructure. |
| F | `lammps` | 1 → 3 | 1 → 4 | GPL code run by a government lab with a multi-institution core team: open science infrastructure. |
| F | `quantum-espresso` | 3 → 4 | 4 → 4 | GPL from inception as a multi-group distribution from a national centre, so open governance from the start. |
| D | `pine64` | null → 2 | 2 → 2 | The original initial is null; nothing in the evidence suggests it differed from the current level. |

## Systematic biases

No group's original scorer is consistently more lenient or strict by a meaningful margin. The
per-group mean of (rescored − original) ranges only from −0.17 (C, initial) to +0.26 (F,
initial). Groups A, E and G match the rescore in every cell, and B differs in one. Where
differences occur, they are directional and tied to particular rubric boundaries rather than
random.

- **Group C was more generous to big tech.** It counted open developer platforms (TensorFlow,
  Kubernetes, React, PyTorch) as level 3 even though the money-making core stayed closed:
  Google 3 and Meta 3 initial, Amazon 1/2. It also gave DeepMind science a current 2, while
  group E scored the same AlphaFold 3 non-commercial weights as 1 in `isomorphic-labs`.
- **Group F was stricter at the 3/4 boundary for non-profit and government stewards that lack
  a formal neutral foundation.** It scored HDF Group, DOE CODE, LAMMPS (current) and Quantum
  ESPRESSO (initial) at 3. Group G gave 4 to comparable non-profit infrastructure (arXiv,
  COS/OSF, OurResearch), so this is a between-scorer inconsistency on one boundary.
- **Group D was lenient at the hardware 2/3 boundary for design files that are published
  without an open licence.** It scored Seeed (no licence) and OpenROV (CC BY-NC-SA) at 3, yet
  Ultimaker's CC BY-NC designs at 2.
- **The one large disagreement (OpenFOAM initial, 0 vs 3) is about the date "initial" refers
  to,** not about the rubric. The same ambiguity, founding versus first open release versus
  start of the AI era, sits under the Google, Meta, Amazon and GitHub differences.

The large differences between group means (E about 0.5–0.7, F about 2.5–2.8) are reproduced
by the rescore, so they reflect which cases each group holds, not scorer leniency. Three
additions to SCHEMA.md would remove most of the remaining disagreement:

- define "initial" as the state at `founded_year`, or at the flagship's first public release;
- say whether non-profit or government stewards without a foundation qualify for 4;
- say how non-commercial or unlicensed hardware files map onto the hardware column.

<details>
<summary>Scripts used (run from <code>/tmp</code>; not committed)</summary>

Evidence printer (scores removed before anything is printed):

```python
import json, glob, os
BASE = "outputs/issue-380-open-science-ai/companies"
META = ["name", "slug", "category", "subcategory", "origin", "founded_year", "ownership_status"]
EVID = ["flagship_projects", "business_model", "openness_notes", "license_history",
        "relicensing_events", "openness_effect_assessment", "key_takeaway"]
for p in sorted(glob.glob(os.path.join(BASE, GROUP, "*.json")))[START:END]:
    d = json.load(open(p))
    d.pop("openness_initial", None); d.pop("openness_current", None)
    assert "openness_initial" not in d and "openness_current" not in d
    print({k: d.get(k) for k in META + EVID})
```

Agreement statistics (run only after every rescored value was in the CSV):

```python
import numpy as np
from scipy.stats import spearmanr

def qwk(a, b, k=5):  # quadratic-weighted Cohen's kappa over fixed categories 0..k-1
    a, b = np.asarray(a), np.asarray(b)
    O = np.zeros((k, k))
    for x, y in zip(a, b): O[x, y] += 1
    E = np.outer(np.bincount(a, minlength=k), np.bincount(b, minlength=k)) / len(a)
    W = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)]) / (k - 1) ** 2
    return 1 - (W * O).sum() / (W * E).sum()

# for each measure in (initial, current) and each subset (all, A..G), skipping null originals:
#   exact = mean(o == s); within1 = mean(|o - s| <= 1)
#   rho = spearmanr(o, s).statistic; kappa = qwk(o, s)
```

</details>
