# Group F: scientific software and open-science infrastructure

Openness is initial→current on the 0–4 scale. Five entries used WebSearch (26 queries). The other 18 used direct WebFetch after the shared search budget ran out (see `fetched_urls`).

| Name | Open | Origin | Founded | Funding model | Scale (date) |
|---|---|---|---|---|---|
| Materials Project | 4→4 | Gov (LBNL) | 2011 | DOE grants | 650k users, 32k citations (2026-01) |
| RCSB PDB / wwPDB | 4→4 | Gov (BNL) | 1971 | NSF/NIH/DOE | 247,287 structures; 4.7B downloads (2025) |
| LAMMPS | 1→3 | Gov (Sandia CRADA) | ~1995 | DOE | 430+ contributors (2025-05) |
| Quantum ESPRESSO | 3→4 | Academic (IT) | 2002 | EU grants | ~28k citations (undated) |
| VASP | 0→0 | Academic (AT) | 1989 | Licences | >1,400 groups (undated) |
| Gaussian | 1→0 | Academic (CMU) | 1987 | Licences | $2.5–6k academic licence (2023) |
| Ansys | 0→0 | Startup | 1970 | Proprietary | $35B sale (2025-07) |
| COMSOL | 0→0 | Startup (SE) | 1986 | Licences | 700+ staff (2026) |
| OpenFOAM | 0→4 | Academic | 2004 | Maintenance plans | €250k/yr, 5 maintainers (2025-11) |
| Kitware | 3→3 | Startup | 1998 | Services | >$39M revenue (undated) |
| Enthought | 2→1 | Startup | 2001 | Consulting | not found |
| RDKit | 3→3 | Unconfirmed | 2006 | Support services | 6.9M PyPI downloads/month (2026-11) |
| OpenFlexure | 3→3 | Academic (UK) | 2016 | Grants | 50+ countries, 12 vendors |
| PyLabRobot | 3→3 | Academic (MIT) | 2022 | Community | 80+ devices (2026-11) |
| Jubilee | 3→3 | Academic (UW) | 2019 | Grants | 630 stars; ~$1,350/unit |
| Project Jupyter | 3→4 | Academic | 2014 | Philanthropy, then LF | ~10M GitHub notebooks (2021-01) |
| NumFOCUS | 4→4 | Community | 2012 | Grants, sponsors | $8.4M revenue (2024) |
| Linux Foundation | 4→4 | Corporate | 2007 | Memberships | $220.7M revenue (2024) |
| Apache SF | 4→4 | Community | 1999 | Donations | $2.2M revenue (FY to 2025-04) |
| HDF Group | 3→3 | Academic (NCSA) | 2006 | Services | $3.0M revenue, 17 staff (2025) |
| Globus | 3→1 | Academic (UChicago) | 2010 | Freemium SaaS | 1 EB moved, 150k users (2020) |
| Zenodo | 4→4 | Gov (CERN/EU) | 2013 | EC grants + CERN | >1 PB (2021) |
| DOE CODE | 3→3 | Gov (OSTI) | 2017 | Appropriations | 5,879 releases, 94% open (2025-04) |

## Observations

1. **Longevity alone does not separate open from closed; control does.** The PDB (1971) survived a 1998 change of host and is CC0 data replicated on three continents. Closed codes also last decades (Gaussian, Ansys, VASP), but users cannot fork them. Ansys's 2025 sale put it under a chip-design company.
2. **Value capture is asymmetric.** Ansys sold for $35B, while OpenFOAM's maintainers ask for €500k a year on €250k. The PDB's $49.4M five-year award compares with RCSB's >$27B estimate of the cost to replace the archive.
3. **Open data became AI training data.** PDB structures trained AlphaFold2 (2024 Nobel). Materials Project data trained GNoME, MatterGen and MPtrj-based potentials. The GNoME data DeepMind added back to MP carries non-commercial terms.
4. **What stays closed, and why.** VASP and Gaussian fund dedicated teams through licences. Gaussian bars competing developers, and VASP's June 2026 rules forbid feeding its source to public AI models or training on it. Yet the open Materials Project runs its DFT on VASP.
5. **Sustainability models.** Grants carry the most-used data infrastructure (MP, PDB, Zenodo). Services sustain Kitware but are shrinking at the HDF Group ($4.7M to $3.0M). Globus traded open code for freemium SaaS.
6. **Foundations are consolidating.** The Linux Foundation ($221M) now hosts Jupyter (2024) and the Agentic AI Foundation (2025). NumFOCUS's 2023–24 deficits halved its net assets, and the ASF runs on $2.2M.
7. **Government open-source output is measurable.** 94% of DOE's 5,879 inventoried releases are open source, mostly under permissive licences. New records fell from 839–1,051 a year (2020–22) to 446–588 (2023–24).
8. **Academic open lab tooling is thinly funded.** OpenFlexure, Jubilee and PyLabRobot spread through independent vendors rather than spin-outs. RDKit is downloaded 6.9M times a month with no visible institutional funding.
