# Bibliography audit: DD-ART-06-2026-000353

"Bayesian Optimization Hackathon for Chemistry and Materials" (Digital Discovery revision). Generated 2026-11-27T19:40:23Z.

Checked against Crossref and DataCite, with the arXiv API as a supplementary source for arXiv comments, journal_ref and version titles. User-Agent "ref-audit/1.0 (python-requests)", no e-mail or personal data, at most 1 request/s for Crossref list queries and 3 requests/s otherwise, every response cached in `/tmp/refcheck/cache/`. This run: 46 network requests, 276 cache hits, 0 retries, 0 failures.

## 0. Inputs and a warning about concurrent edits

The source tree in `/tmp/acbo/work` was being edited by someone else while this audit ran: `main.tex` changed at 19:16, 19:25 and 19:30 UTC, `latex/revision-refs.bib` appeared at 19:16 and grew at 19:24, and nine project JSON summaries changed at 19:24 (duplicate keys were merged). The `\bibliography` line now reads `latex/references, latex/summaries-ref, latex/revision-refs`, so a third file is part of the build and was audited too. Everything below describes the snapshot taken at 2026-11-27T19:39:58Z (copies in `/tmp/refcheck/snapshot/`):

| file | sha256 (first 12) | size | mtime (UTC) |
|---|---|---|---|
| main.tex | 9b80c22dbc53 | 47361 | 2026-11-27T19:35:04Z |
| latex/references.bib | 39b0183abf33 | 43535 | 2026-11-27T19:39:35Z |
| latex/summaries-ref.bib | 6dd46e9cf59b | 18698 | 2026-11-27T19:39:26Z |
| latex/revision-refs.bib | 44a880f10e94 | 4187 | 2026-11-27T19:39:35Z |
| _projects/json_summaries/*.json | 45 files | | latest 2026-11-27T19:24:11Z |

**Inputs changed after the snapshot** (re-run `python3 -P /tmp/refcheck/scripts/audit.py`, which is cheap because of the cache):
- `latex/references.bib`: modified 2026-11-27T19:40:16Z

## 1. Counts by status

One status per entry, the most serious that applies (order: retracted_or_corrected, mismatch, preprint_published, duplicate, missing_doi_found, missing_doi_unconfirmed, not_found, minor, ok). All applicable statuses are in `report.json` (`all_statuses`).

| status | cited entries | all entries |
|---|---|---|
| retracted_or_corrected | 3 | 3 |
| mismatch | 2 | 7 |
| preprint_published | 0 | 1 |
| duplicate | 9 | 20 |
| missing_doi_found | 0 | 0 |
| missing_doi_unconfirmed | 9 | 11 |
| not_found | 8 | 8 |
| minor | 15 | 21 |
| ok | 65 | 69 |
| **total** | **111** | **140** |

## 2. Citation coverage

- 111 distinct keys are cited: 50 in `main.tex` (comments ignored) and 72 in the project JSON summaries (some in both).
- Cited but missing from every bib file: **none** in this snapshot (the nine keys added to `main.tex` at 19:16 are defined in `revision-refs.bib`).
- Never cited (29 entries; they do not print): `lferguson_conference_2019` (references.bib), `saarLowCostRobotScience2022` (references.bib), `mahjour_interactive_2023` (references.bib), `wallum_instrument_2023` (references.bib), `wurger_exploring_2021` (references.bib), `ozkan_laying_2024` (references.bib), `azam_pretraining_2024` (references.bib), `wang_bayesian_2022` (references.bib), `lewis_retrieval-augmented_2020` (references.bib), `ament_sustainable_2023` (references.bib), `lilienfeld_retrospective_2020` (references.bib), `lozano-blanco_single-event_2008` (references.bib), `chakkingal_multi-output_2022` (references.bib), `qin_large_2023` (references.bib), `garcia-ortegon_dockstring_2022` (references.bib), `angello_convergent_2022` (references.bib), `wang_autonomous_2024` (references.bib), `reker_active-learning_2015` (references.bib), `xu_high-throughput_2020` (references.bib), `krajina_dynamic_2017` (references.bib), `bellamy_batched_2022` (references.bib), `rube_prediction_2022` (references.bib), `dusselier_small-pore_2018` (references.bib), `mallette_current_2024` (references.bib), `shahriari2015taking` (summaries-ref.bib), `fitzner2022baybe` (summaries-ref.bib), `altamirano2023robust` (summaries-ref.bib), `lin2022preference` (summaries-ref.bib), `ramakrishnan2014quantum` (summaries-ref.bib).
- No key is defined in more than one file.

## 3. Cited entries that are not ok

Evidence is the registry record the entry was compared with (Crossref unless marked DataCite). "APPLIED" means the change is in the `.fixed.bib` files; "suggest" means it was not applied (lower confidence, or not a registry-backed change). En and em dashes inside quoted titles are shown as hyphens.

| key | issue | evidence (DOI, title, year) | suggested fix | confidence |
|---|---|---|---|---|
| `diemar_report_2025` (references.bib; main.tex:L535) | [retracted_or_corrected] notice: correction 10.1177/02611929251322945 (2025-02-23): "Corrigendum to Report of the First ONTOX Hackathon: Hack to Save Lives and Avoid Animal Suffering. The Use of "; low: bib title is a shortened form of the registry title (similarity 100 set, 58 sorted) | Crossref 10.1177/02611929241305112: "Report of the First ONTOX Hackathon: Hack to Save Lives and Avoid Animal Suffering. The Use of Artificial Intelligence in Toxicology - A Potential Driver for Reducing/Replacing Laboratory Animals in the Future", Alternatives to Laboratory Animals 2025 (online 2024, print 2025), vol. 53, p. 42-61 | suggest: use the full registry title: "Report of the First ONTOX Hackathon: Hack to Save Lives and Avoid Animal Suffering. The Use of Artificial Intelligence in Toxicology - A Potential Driver for Reducing/Replacing Laboratory Animals in the Future" ; suggest: Crossref now gives the title as "Report of the First ONTOX Hackathon: Hack to Save Lives and Avoid Animal Suffering. The Use of Artificial Intelligence in Toxicology - A Potential Driver for Reducing/Replacing Laboratory Animals in the Future" and lists a correction notice (10.1177/02611929251322945); the bib keeps the title as originally published. Check the notice and decide whether to cite the corrected title or the notice  | medium |
| `szymanski_autonomous_2023` (references.bib; project_24.json) | [retracted_or_corrected] notice: correction 10.1038/s41586-025-09992-y (2026-01-19): "Author Correction: An autonomous laboratory for the accelerated synthesis of inorganic materials"; low: title wording differs slightly from registry (similarity 96) | Crossref 10.1038/s41586-023-06734-w: "An autonomous laboratory for the accelerated synthesis of inorganic materials", Nature 2023, vol. 624, p. 86-91 | suggest: Crossref now gives the title as "An autonomous laboratory for the accelerated synthesis of inorganic materials" and lists a correction notice (10.1038/s41586-025-09992-y); the bib keeps the title as originally published. Check the notice and decide whether to cite the corrected title or the notice  | medium |
| `zhou2019optimization` (summaries-ref.bib; project_8.json) | [retracted_or_corrected] notice: correction 10.1038/s41598-020-66840-x (2020-06-23): "Author Correction: Optimization of Molecules via Deep Reinforcement Learning" | Crossref 10.1038/s41598-019-47148-x: "Optimization of Molecules via Deep Reinforcement Learning", Scientific Reports 2019, vol. 9, p. 10752 | none | high |
| `adachi_looping_2024` (references.bib; main.tex:L558) | [mismatch] high: DOI is the arXiv preprint DOI, but the entry names "Proceedings of the 27th International Conference on Artificial Intelligence and Statistics (AISTATS)" with volume/pages of the published version; medium: bib year 2024 differs by one from registry year 2023 (issued 2023, print None, online None); medium: arXiv record (author supplied) says: journal_ref "AISTATS 238, 505--513, 2024"; comment "Accepted at AISTATS 2024, 24 pages, 11 figures"; low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2310.17273" | DataCite 10.48550/arXiv.2310.17273: "Looping in the Human Collaborative and Explainable Bayesian Optimization", arXiv 2023 | suggest: cite the AISTATS 2024 paper (PMLR vol. 238, pp. 505-513, per the arXiv journal_ref) instead of "Advances in Neural Information Processing Systems"; PMLR is not in Crossref, so this is unconfirmed ; suggest: add eprint = {2310.17273} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2310.17273" (RSC style)  | high |
| `ament2310sustainable` (summaries-ref.bib; project_12.json) | [mismatch] medium: DOI is the arXiv preprint DOI, but the entry names "NeurIPS 2023 Workshop on Adaptive Experimentation in the Real World"; low: arXiv record (author supplied) says: comment "NeurIPS 2023 Workshop on Adaptive Experimental Design and Active Learning in the Real World"; low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2310.18288"; duplicate of ament_sustainable_2023 | DataCite 10.48550/arXiv.2310.18288: "Sustainable Concrete via Bayesian Optimization", arXiv 2023 | suggest: add eprint = {2310.18288} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2310.18288" (RSC style)  | high |
| `altamirano_robust_2023` (references.bib; main.tex:L542; main.tex:L558; project_12.json) | [duplicate] duplicate of altamirano2023robust | DataCite 10.48550/arXiv.2311.00463: "Robust and Conjugate Gaussian Process Regression", arXiv 2023 | none | high |
| `bellamy2022batched` (summaries-ref.bib; project_17.json) | [duplicate] duplicate of bellamy_batched_2022 | Crossref 10.1021/acs.jcim.2c00602: "Batched Bayesian Optimization for Drug Design in Noisy Environments", Journal of Chemical Information and Modeling 2022, vol. 62, p. 3970-3981 | none | high |
| `chakkingal2022multi` (summaries-ref.bib; project_16.json) | [duplicate] duplicate of chakkingal_multi-output_2022 | Crossref 10.1016/j.cej.2022.137186: "Multi-output machine learning models for kinetic data evaluation : A Fischer-Tropsch synthesis case study", Chemical Engineering Journal 2022, vol. 446, p. 137186 | none | high |
| `dusselier2018small` (summaries-ref.bib; project_10.json) | [duplicate] duplicate of dusselier_small-pore_2018 | Crossref 10.1021/acs.chemrev.7b00738: "Small-Pore Zeolites: Synthesis and Catalysis", Chemical Reviews 2018, vol. 118, p. 5265-5329 | none | high |
| `garcia_dockstring_2022` (references.bib; project_25.json) | [duplicate] duplicate of garcia-ortegon_dockstring_2022 | Crossref 10.1021/acs.jcim.1c01334: "DOCKSTRING: Easy Molecular Docking Yields Better Benchmarks for Ligand Design", Journal of Chemical Information and Modeling 2022, vol. 62, p. 3486-3502 | none | high |
| `lozano2008single` (summaries-ref.bib; project_16.json) | [duplicate] duplicate of lozano-blanco_single-event_2008 | Crossref 10.1021/ie071587u: "Single-Event Microkinetic Model for Fischer-Tropsch Synthesis on Iron-Based Catalysts", Industrial & Engineering Chemistry Research 2008, vol. 47, p. 5879-5891 | none | high |
| `mallette2024current` (summaries-ref.bib; project_10.json) | [duplicate] duplicate of mallette_current_2024 | Crossref 10.1021/acs.chemrev.3c00801: "The Current Understanding of Mechanistic Pathways in Zeolite Crystallization", Chemical Reviews 2024, vol. 124, p. 3416-3493 | none | high |
| `ramakrishnan_quantum_2014` (references.bib; project_18.json; project_27.json; project_28.json) | [duplicate] duplicate of ramakrishnan2014quantum | Crossref 10.1038/sdata.2014.22: "Quantum chemistry structures and properties of 134 kilo molecules", Scientific Data 2014, vol. 1, p. 140022 | none | high |
| `shahriari_taking_2016` (references.bib; main.tex:L540; project_3.json) | [duplicate] duplicate of shahriari2015taking | Crossref 10.1109/JPROC.2015.2494218: "Taking the Human Out of the Loop: A Review of Bayesian Optimization", Proceedings of the IEEE 2016, vol. 104, p. 148-175 | none | high |
| `balandat2020botorch` (summaries-ref.bib; project_1.json; project_23.json) | [missing_doi_unconfirmed] no Crossref match; venue/item type usually has no Crossref DOI (neural information processing) | no plausible Crossref record (best title similarity 74, different first author) | none | low |
| `bergstra2012random` (summaries-ref.bib; project_5.json) | [missing_doi_unconfirmed] no Crossref match; venue/item type usually has no Crossref DOI (machine learning research) | no plausible Crossref record (best title similarity 100, different first author) | none | low |
| `daulton2021parallel` (summaries-ref.bib; project_1.json) | [missing_doi_unconfirmed] no Crossref match; venue/item type usually has no Crossref DOI (neural information processing) | no plausible Crossref record (best title similarity 83, different first author) | none | low |
| `jiang_efficient_2020` (references.bib; project_36.json) | [missing_doi_unconfirmed] no Crossref match; venue/item type usually has no Crossref DOI (neural information processing) | no plausible Crossref record (best title similarity 72, different first author) | none | low |
| `JMLRdragonfly` (summaries-ref.bib; project_1.json) | [missing_doi_unconfirmed] no Crossref match; venue/item type usually has no Crossref DOI (machine learning research) | no plausible Crossref record (best title similarity 100, different first author) | none | low |
| `kusner2017grammar` (summaries-ref.bib; project_21.json) | [missing_doi_unconfirmed] no Crossref match; venue/item type usually has no Crossref DOI (international conference on machine learning) | no plausible Crossref record (best title similarity 100, different first author) | none | low |
| `lin_preference_2022` (references.bib; main.tex:L540; project_16.json) | [missing_doi_unconfirmed] duplicate of lin2022preference; no Crossref match; venue/item type usually has no Crossref DOI (pmlr, artificial intelligence and statistics) | no plausible Crossref record (best title similarity 75, different first author) | none | low |
| `poloczek2017multi` (summaries-ref.bib; project_2.json) | [missing_doi_unconfirmed] no Crossref match; venue/item type usually has no Crossref DOI (neural information processing) | no plausible Crossref record (best title similarity 100, different first author) | none | low |
| `snoek2012practical` (summaries-ref.bib; project_3.json; project_5.json) | [missing_doi_unconfirmed] no Crossref match; venue/item type usually has no Crossref DOI (neural information processing) | no plausible Crossref record (best title similarity 91, different first author) | none | low |
| `acbo_followup_2026` (revision-refs.bib; main.tex:L547) | [not_found]  | no plausible Crossref record (best title similarity 55, different first author) | none | low |
| `athalye_gavel_2016` (revision-refs.bib; main.tex:L321) | [not_found]  | no plausible Crossref record (best title similarity 100, different first author) | none | low |
| `baird_introduction_2024` (references.bib; main.tex:L477; main.tex:L529; main.tex:L531; main.tex:L533 ...) | [not_found]  | no plausible Crossref record (best title similarity 64, different first author); related paper 10.1017/s1049096515000347: "An Interview with Brian Baird", PS: Political Science & Politics 2015 | suggest: a peer-reviewed paper on this software exists: 10.1017/s1049096515000347, "An Interview with Brian Baird", PS: Political Science & Politics 2015; consider citing it (with or instead of the repository)  | medium |
| `bakshy2018ax` (summaries-ref.bib; project_31.json) | [not_found] medium: journal = "GitHub repository" is not a journal (software/documentation entry typed as @article); low: @article with howpublished (ignored by apsrev4-2 for articles) | no plausible Crossref record (best title similarity 80, different first author) | suggest: retype as @misc with howpublished/url (journal = "GitHub repository" prints as if it were a journal)  | high |
| `fitzner_baybe_2022` (references.bib; main.tex:L521; main.tex:L558; project_7.json; project_20.json ...) | [not_found] duplicate of fitzner2022baybe | no plausible Crossref record (best title similarity 78, different first author); related paper 10.1039/D5DD00050E: "BayBE: a Bayesian Back End for experimental planning in the low-to-no-data regime", Digital Discovery 2025 | suggest: a peer-reviewed paper on this software exists: 10.1039/D5DD00050E, "BayBE: a Bayesian Back End for experimental planning in the low-to-no-data regime", Digital Discovery 2025; consider citing it (with or instead of the repository)  | medium |
| `landrum2013rdkit` (summaries-ref.bib; project_8.json) | [not_found] medium: journal = "Release" is not a journal (software/documentation entry typed as @article) | no plausible Crossref record (best title similarity 42, different first author) | suggest: retype as @misc with howpublished/url (journal = "Release" prints as if it were a journal)  | high |
| `mqs_cosmo_2024` (references.bib; project_42.json) | [not_found]  | no plausible Crossref record (best title similarity 60, different first author) | none | low |
| `stair-lab_coh2` (summaries-ref.bib; project_33.json) | [not_found]  | no plausible Crossref record (best title similarity 76, different first author) | none | low |
| `busby_building_2015` (references.bib; main.tex:L521; main.tex:L531) | [minor] low: author list truncated with "and others" (3 listed, registry has 32) | Crossref 10.1101/018085: "Building Genomic Analysis Pipelines in a Hackathon Setting with Bioinformatician Teams: DNA-seq, Epigenomics, Metagenomics and RNA-seq", openRxiv 2015 | none | high |
| `deneault_preferential_2025` (references.bib; main.tex:L558) | [minor] low: author list truncated with "and others" (1 listed, registry has 8) | Crossref 10.1039/D4DD00320A: "Preferential Bayesian optimization improves the efficiency of printing objects with subjective qualities", Digital Discovery 2025, vol. 4, p. 723-737 | none | high |
| `durholt_bofire_2024` (references.bib; main.tex:L558) | [minor] low: author list truncated with "and others" (3 listed, registry has 18); low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2408.05040" | DataCite 10.48550/arXiv.2408.05040: "BoFire: Bayesian Optimization Framework Intended for Real Experiments", arXiv 2024 | suggest: add eprint = {2408.05040} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2408.05040" (RSC style)  | high |
| `frazier_tutorial_2018` (references.bib; main.tex:L540) | [minor] low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:1807.02811" | DataCite 10.48550/arXiv.1807.02811: "A Tutorial on Bayesian Optimization", arXiv 2018 | suggest: add eprint = {1807.02811} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:1807.02811" (RSC style)  | high |
| `galvao2022cordata` (summaries-ref.bib; project_7.json) | [minor] low: author list truncated with "and others" (10 listed, registry has 12) | Crossref 10.1038/s41529-022-00259-9: "CORDATA: an open data management web application to select corrosion inhibitors", npj Materials Degradation 2022, vol. 6, p. 48 | none | high |
| `griffiths_gauche_2024` (references.bib; main.tex:L475; main.tex:L521; main.tex:L540; project_29.json ...) | [minor] low: author list truncated with "and others" (7 listed, registry has 28) | Crossref 10.52202/075280-3362: "GAUCHE: A Library for Gaussian Processes in Chemistry", Advances in Neural Information Processing Systems 36 2023, p. 76923-76946 | none | high |
| `judge_applying_2024` (references.bib; main.tex:L556) | [minor] low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2409.07190" | DataCite 10.48550/arXiv.2409.07190: "Applying Multi-Fidelity Bayesian Optimization in Chemistry: Open Challenges and Major Considerations", arXiv 2024 | suggest: add eprint = {2409.07190} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2409.07190" (RSC style)  | high |
| `jumper2021highly` (summaries-ref.bib; project_32.json) | [minor] low: author list truncated with "and others" (10 listed, registry has 34) | Crossref 10.1038/s41586-021-03819-2: "Highly accurate protein structure prediction with AlphaFold", Nature 2021, vol. 596, p. 583-589 | none | high |
| `kristiadi_sober_2024` (references.bib; main.tex:L542; main.tex:L558) | [minor] low: arXiv record (author supplied) says: comment "ICML 2024. Code: https://github.com/wiseodd/lapeft-bayesopt"; low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2402.05015" | DataCite 10.48550/arXiv.2402.05015: "A Sober Look at LLMs for Material Discovery: Are They Actually Good for Bayesian Optimization Over Molecules?", arXiv 2024 | suggest: the arXiv comment says ICML 2024; consider citing the ICML 2024 proceedings version (PMLR, not in Crossref, unconfirmed) ; suggest: add eprint = {2402.05015} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2402.05015" (RSC style)  | high |
| `muller_la_agente_optima_2026` (references.bib; main.tex:L558) | [minor] low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2609.04564" | DataCite 10.48550/arXiv.2609.04564: "La Agente Óptima: Towards Agentic Self-Driving Laboratories", arXiv 2026 | suggest: add eprint = {2609.04564} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2609.04564" (RSC style)  | high |
| `pratiush_michackathon_2025` (references.bib; main.tex:L529) | [minor] low: author list truncated with "and others" (3 listed, registry has 73) | Crossref 10.1088/2632-2153/ae1f5d: "Mic-hackathon 2024: hackathon on machine learning for electron and scanning probe microscopy", Machine Learning: Science and Technology 2025, vol. 6, p. 040701 | none | high |
| `sanchez-lengeling_bayesian_2018` (references.bib; project_29.json) | [minor] low: bib year 2018 is the online year; print issue year is 2019 (online vs print) | Crossref 10.1002/adts.201800069: "A Bayesian Approach to Predict Solubility Parameters", Advanced Theory and Simulations 2019 (online 2018, print 2019), vol. 2, p. 1800069 | none | high |
| `scikit-optimize_2021` (summaries-ref.bib; project_30.json) | [minor] low: entry type @software is not defined in apsrev4-2.bst (BibTeX warns and falls back) | DataCite 10.5281/zenodo.5565057: "scikit-optimize/scikit-optimize", Zenodo 2021 | suggest: change @software to @misc: apsrev4-2.bst does not define @software (BibTeX warns and falls back)  | high |
| `sorourifar_accelerating_2024` (references.bib; project_21.json) | [minor] low: arXiv record (author supplied) says: comment "9 pages, 2 figures consisting of 6 and 4 plots, accepted to NeurIPS 2023 Workshop on Adaptive Experimental Design and Active Learning in the Real World" | DataCite 10.48550/arXiv.2401.01398: "Accelerating Black-Box Molecular Property Optimization by Adaptively Learning Sparse Subspaces", arXiv 2024 | none | high |
| `zimmermann_reflections_2024` (references.bib; main.tex:L521; main.tex:L531) | [minor] low: author list truncated with "and others" (3 listed, registry has 144); low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2411.15221" | DataCite 10.48550/arXiv.2411.15221: "Reflections from the 2024 Large Language Model (LLM) Hackathon for Applications in Materials Science and Chemistry", arXiv 2024 | suggest: add eprint = {2411.15221} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2411.15221" (RSC style)  | high |

## 4. Duplicates (same DOI, same arXiv id, or title similarity >= 95 under different keys)

12 duplicate groups; **0 would print twice** in this snapshot. Earlier in the session (before the 19:24 UTC edits) several pairs were cited under both keys (for example `fitzner_baybe_2022` in main.tex and `fitzner2022baybe` in project_7/20/23/26.json, `shahriari_taking_2016` and `shahriari2015taking`, `ramakrishnan_quantum_2014` and `ramakrishnan2014quantum`, the two `altamirano`, `ament` and `lin` pairs); the concurrent edits merged the citations onto one key each. The unused twins are still in the bib files and can be deleted.

| group | keys (file) | where cited | prints twice | suggestion |
|---|---|---|---|---|
| 1 | `ramakrishnan_quantum_2014` (references.bib)<br>`ramakrishnan2014quantum` (summaries-ref.bib) | `ramakrishnan_quantum_2014`: project_18.json, project_27.json, project_28.json<br>`ramakrishnan2014quantum`: not cited | no | Prints once. Delete the unused `ramakrishnan2014quantum`. |
| 2 | `shahriari_taking_2016` (references.bib)<br>`shahriari2015taking` (summaries-ref.bib), no DOI | `shahriari_taking_2016`: main.tex:L540, project_3.json<br>`shahriari2015taking`: not cited | no | Prints once. Delete the unused `shahriari2015taking`. |
| 3 | `fitzner_baybe_2022` (references.bib), no DOI<br>`fitzner2022baybe` (summaries-ref.bib), no DOI | `fitzner_baybe_2022`: main.tex:L521, main.tex:L558, project_7.json, project_20.json, project_23.json, project_26.json<br>`fitzner2022baybe`: not cited | no | Prints once. Delete the unused `fitzner2022baybe`. |
| 4 | `altamirano_robust_2023` (references.bib)<br>`altamirano2023robust` (summaries-ref.bib), no DOI | `altamirano_robust_2023`: main.tex:L542, main.tex:L558, project_12.json<br>`altamirano2023robust`: not cited | no | Prints once. Delete the unused `altamirano2023robust`. |
| 5 | `ament_sustainable_2023` (references.bib), no DOI<br>`ament2310sustainable` (summaries-ref.bib) | `ament_sustainable_2023`: not cited<br>`ament2310sustainable`: project_12.json | no | Prints once. Delete the unused `ament_sustainable_2023`. The cited `ament2310sustainable` is the weaker entry (1 high/medium issues against 0); switch the citation to `ament_sustainable_2023`, or keep `ament2310sustainable` as repaired in the fixed bib. |
| 6 | `lin_preference_2022` (references.bib), no DOI<br>`lin2022preference` (summaries-ref.bib), no DOI | `lin_preference_2022`: main.tex:L540, project_16.json<br>`lin2022preference`: not cited | no | Prints once. Delete the unused `lin2022preference`. |
| 7 | `lozano-blanco_single-event_2008` (references.bib)<br>`lozano2008single` (summaries-ref.bib) | `lozano-blanco_single-event_2008`: not cited<br>`lozano2008single`: project_16.json | no | Prints once. Delete the unused `lozano-blanco_single-event_2008`. |
| 8 | `chakkingal_multi-output_2022` (references.bib)<br>`chakkingal2022multi` (summaries-ref.bib) | `chakkingal_multi-output_2022`: not cited<br>`chakkingal2022multi`: project_16.json | no | Prints once. Delete the unused `chakkingal_multi-output_2022`. |
| 9 | `garcia-ortegon_dockstring_2022` (references.bib)<br>`garcia_dockstring_2022` (references.bib) | `garcia-ortegon_dockstring_2022`: not cited<br>`garcia_dockstring_2022`: project_25.json | no | Prints once. Delete the unused `garcia-ortegon_dockstring_2022`. |
| 10 | `bellamy_batched_2022` (references.bib)<br>`bellamy2022batched` (summaries-ref.bib) | `bellamy_batched_2022`: not cited<br>`bellamy2022batched`: project_17.json | no | Prints once. Delete the unused `bellamy_batched_2022`. |
| 11 | `dusselier_small-pore_2018` (references.bib)<br>`dusselier2018small` (summaries-ref.bib) | `dusselier_small-pore_2018`: not cited<br>`dusselier2018small`: project_10.json | no | Prints once. Delete the unused `dusselier_small-pore_2018`. |
| 12 | `mallette_current_2024` (references.bib)<br>`mallette2024current` (summaries-ref.bib) | `mallette_current_2024`: not cited<br>`mallette2024current`: project_10.json | no | Prints once. Delete the unused `mallette_current_2024`. |

## 5. Preprints

| key | server | published version | action |
|---|---|---|---|
| `adachi_looping_2024` | arXiv | none found in Crossref; arXiv says: AISTATS 238, 505--513, 2024; Accepted at AISTATS 2024, 24 pages, 11 figures | suggested only: cite the AISTATS 2024 paper (PMLR vol. 238, pp. 505-513, per the arXiv journal_ref) instead of "Advances in Neural Information Processing Systems"; PMLR is not in Crossref, so this is unconfirmed |
| `altamirano_robust_2023` | arXiv | none found in Crossref | keep as preprint |
| `ament2310sustainable` | arXiv | none found in Crossref; arXiv says: NeurIPS 2023 Workshop on Adaptive Experimental Design and Active Learning in the Real World | suggested only: add eprint = {2310.18288} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2310.18288" (RSC style) |
| `busby_building_2015` | bioRxiv | none found in Crossref | keep as preprint |
| `durholt_bofire_2024` | arXiv | none found in Crossref; arXiv says: 6 pages, 1 figure, 1 listing | suggested only: add eprint = {2408.05040} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2408.05040" (RSC style) |
| `frazier_tutorial_2018` | arXiv | none found in Crossref | suggested only: add eprint = {1807.02811} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:1807.02811" (RSC style) |
| `judge_applying_2024` | arXiv | none found in Crossref | suggested only: add eprint = {2409.07190} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2409.07190" (RSC style) |
| `kristiadi_sober_2024` | arXiv | none found in Crossref; arXiv says: ICML 2024. Code: https://github.com/wiseodd/lapeft-bayesopt | suggested only: the arXiv comment says ICML 2024; consider citing the ICML 2024 proceedings version (PMLR, not in Crossref, unconfirmed) |
| `moss_gaussian_2020` | arXiv | none found in Crossref | keep as preprint |
| `muller_la_agente_optima_2026` | arXiv | none found in Crossref | suggested only: add eprint = {2609.04564} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2609.04564" (RSC style) |
| `schmid_general_2025` | arXiv | none found in Crossref | keep as preprint |
| `sorourifar_accelerating_2024` | arXiv | none found in Crossref; arXiv says: 9 pages, 2 figures consisting of 6 and 4 plots, accepted to NeurIPS 2023 Workshop on Adaptive Experimental Design and Active Learning in the Real World | keep as preprint |
| `truong2026neural` | arXiv | none found in Crossref; arXiv says: 32 pages, 20 figures, 13 tables | keep as preprint |
| `zimmermann_reflections_2024` | arXiv | none found in Crossref; arXiv says: Updating author information, the submission remains largely unchanged. 98 pages total | suggested only: add eprint = {2411.15221} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2411.15221" (RSC style) |

## 6. Corrections and retractions (Crossref `filter=updates` and `updated-by`)

Checked for every entry with a Crossref record (101 entries). **No retraction, withdrawal or expression of concern was found.** 3 correction notices:

- `szymanski_autonomous_2023` (cited): correction notice 10.1038/s41586-025-09992-y, 2026-01-19: "Author Correction: An autonomous laboratory for the accelerated synthesis of inorganic materials".
- `diemar_report_2025` (cited): correction notice 10.1177/02611929251322945, 2025-02-23: "Corrigendum to Report of the First ONTOX Hackathon: Hack to Save Lives and Avoid Animal Suffering. The Use of Artificial Intelligence in Toxicology - A Potential Driver for Reducing/Replacing Laboratory Animals in the Future".
- `zhou2019optimization` (cited): correction notice 10.1038/s41598-020-66840-x, 2020-06-23: "Author Correction: Optimization of Molecules via Deep Reinforcement Learning".

Corrections do not change how an entry is cited, but the A-Lab entry is worth a look: Crossref now titles the article "...synthesis of inorganic materials" while the bib (and the original 2023 publication) say "...of novel materials". arXiv entries were checked for a "withdrawn" comment; none was found.

## 7. RSC house style for preprints

- ChemRxiv: no ChemRxiv entries in any of the bib files, so no version-suffix issue.
- Cited arXiv entries without the arXiv DOI (0): none. The fixed bib adds the DataCite-verified `10.48550/arXiv.<id>` DOI to each of these unless the entry was updated to a published version.
- Cited arXiv entries whose printed fields do not show the arXiv number (8): `frazier_tutorial_2018`, `zimmermann_reflections_2024`, `durholt_bofire_2024`, `kristiadi_sober_2024`, `adachi_looping_2024`, `judge_applying_2024`, `muller_la_agente_optima_2026`, `ament2310sustainable`. apsrev4-2 prints an `eprint` field as "arXiv:NNNN.NNNNN", so adding `eprint = {<id>}` and `archivePrefix = {arXiv}` (not done here, as it is a style change rather than a registry correction) would satisfy RSC style.

## 8. Malformed fields

- `language = {en}`: 0 entries (). Harmless for apsrev4-2, which ignores the field.
- Other malformed fields (7 findings):
  - `lferguson_conference_2019` (references.bib, not cited): author "L. Ferguson, Andrew" has an initial in the family-name part
  - `lferguson_conference_2019` (references.bib, not cited): author "J. Reich, Brian" has an initial in the family-name part
  - `lozano-blanco_single-event_2008` (references.bib, not cited): non-ASCII character(s) U+2212 in title may not be set up for pdflatex/inputenc
  - `landrum2013rdkit` (summaries-ref.bib, cited): journal = "Release" is not a journal (software/documentation entry typed as @article)
  - `bakshy2018ax` (summaries-ref.bib, cited): journal = "GitHub repository" is not a journal (software/documentation entry typed as @article)
  - `bakshy2018ax` (summaries-ref.bib, cited): @article with howpublished (ignored by apsrev4-2 for articles)
  - `scikit-optimize_2021` (summaries-ref.bib, cited): entry type @software is not defined in apsrev4-2.bst (BibTeX warns and falls back)
- `@misc` entries that Crossref types as journal-article: none.
- No unescaped `&`, `%`, `#` or `_`, no unbalanced braces and no all-caps titles were found in any printed field.

## 9. Post-hackathon Outcomes: link check

The task describes inline `\href` links. In the snapshot those sentences now cite bib keys instead (the links were converted at 19:16 UTC), so both versions were checked: the original `\href` text (identical in `/tmp/acbo/pristine/main.tex` and `/tmp/acbo/repo/main.tex`) and the current `\cite` keys.

| version | link or key | claimed title / journal, year | registry record | verdict |
|---|---|---|---|---|
| original | https://doi.org/10.1063/5.0272663 | "Ranking over regression for Bayesian optimization and molecule selection" / APL Machine Learning, 2025 | 10.1063/5.0272663: "Ranking over regression for Bayesian optimization and molecule selection", APL Machine Learning, issued 2025, print 2025 | title matches; journal matches; year matches |
| original | https://arxiv.org/abs/2502.18966 | "One Set to Rule Them All: How to Obtain General Chemical Conditions via Bayesian Optimization over Curried Functions" | 10.48550/arXiv.2502.18966: "Bayesian Optimization for General Reaction Conditions", arXiv, issued 2025 | TITLE DIFFERS (similarity 86); the claimed title is the arXiv v1 title "One Set to Rule Them All: How to Obtain General Chemical Conditions via Bayesian Optimization over Curried Functions" (similarity 100); the record was retitled; no journal version found in Crossref |
| original | https://doi.org/10.1039/D5DD00039D | "BoTier: multi-objective Bayesian optimization with tiered objective structures" / Digital Discovery, 2025 | 10.1039/D5DD00039D: "BoTier : multi-objective Bayesian optimization with tiered objective structures", Digital Discovery, issued 2025 | title matches; journal matches; year matches |
| original | https://doi.org/10.1039/D4DD00225C | "Cost-informed Bayesian reaction optimization" / Digital Discovery, 2024 | 10.1039/D4DD00225C: "Cost-informed Bayesian reaction optimization", Digital Discovery, issued 2024 | title matches; journal matches; year matches |
| original | https://doi.org/10.1039/D5DD00005J | "Machine-learning-guided design of electroanalytical pulse waveforms" / Digital Discovery, 2025 | 10.1039/D5DD00005J: "Machine-learning-guided design of electroanalytical pulse waveforms", Digital Discovery, issued 2025 | title matches; journal matches; year matches |
| original | https://arxiv.org/abs/2601.06505 | "Neural nonmyopic Bayesian optimization in dynamic cost settings" | 10.48550/arXiv.2601.06505: "Neural Nonmyopic Bayesian Optimization in Dynamic Cost Settings", arXiv, issued 2026 | title matches; no journal version found in Crossref |
| original | https://doi.org/10.1021/acsnano.5c15488 | "Autonomous synthesis of nanoparticles with target scattering patterns" / ACS Nano, 2026 | 10.1021/acsnano.5c15488: "Autonomous Synthesis of Nanoparticles with Target Scattering Patterns", ACS Nano, issued 2026, print 2026 | title matches; journal matches; year matches |
| current | acbo_followup_2026 | (no title in the sentence) / https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/issues/172#issuecomment-5348017006, 2026 | not a DOI or arXiv link; not checkable against a registry | not checked |
| current | tom_ranking_2025 | "Ranking over regression for Bayesian optimization and molecule selection" / APL Machine Learning, 2025 | 10.1063/5.0272663: "Ranking over regression for Bayesian optimization and molecule selection", APL Machine Learning, issued 2025, print 2025 | title matches; journal matches; year matches |
| current | schmid_general_2025 | (no title in the sentence) / arXiv preprint, arXiv:2502.18966, 2025 | 10.48550/arXiv.2502.18966: "Bayesian Optimization for General Reaction Conditions", arXiv, issued 2025 | title matches; year matches |
| current | haddadnia_botier_2025 | "BoTier: multi-objective Bayesian optimization with tiered objective structures" / Digital Discovery, 2025 | 10.1039/D5DD00039D: "BoTier : multi-objective Bayesian optimization with tiered objective structures", Digital Discovery, issued 2025 | title matches; journal matches; year matches |
| current | schoepfer_cost-informed_2024 | "Cost-informed Bayesian reaction optimization" / Digital Discovery, 2024 | 10.1039/D4DD00225C: "Cost-informed Bayesian reaction optimization", Digital Discovery, issued 2024 | title matches; journal matches; year matches |
| current | movassaghi_machine-learning-guided_2025 | "Machine-learning-guided design of electroanalytical pulse waveforms" / Digital Discovery, 2025 | 10.1039/D5DD00005J: "Machine-learning-guided design of electroanalytical pulse waveforms", Digital Discovery, issued 2025 | title matches; journal matches; year matches |
| current | truong2026neural | "Neural nonmyopic Bayesian optimization in dynamic cost settings" / arXiv preprint arXiv:2601.06505, 2026 | 10.48550/arXiv.2601.06505: "Neural Nonmyopic Bayesian Optimization in Dynamic Cost Settings", arXiv, issued 2026 | title matches; JOURNAL DIFFERS; year matches |
| current | anker_autonomous_2026 | "Autonomous synthesis of nanoparticles with target scattering patterns" / ACS Nano, 2026 | 10.1021/acsnano.5c15488: "Autonomous Synthesis of Nanoparticles with Target Scattering Patterns", ACS Nano, issued 2026, print 2026 | title matches; journal matches; year matches |
| other DOI link in current main.tex | 10.5281/zenodo.20496810 | (no title in the sentence) | 10.5281/zenodo.20496810: "AC-BO Hackathon 2024 - All Projects", Zenodo, issued 2024 |  |

## 10. Changes in the fixed bib files

Only high-confidence, registry-backed changes to cited entries were applied; keys are unchanged and untouched entries are byte-identical (see `bib.diff`). Outputs: `/tmp/refcheck/references.fixed.bib`, `/tmp/refcheck/summaries-ref.fixed.bib`.


## 11. BibTeX check (apsrev4-2, all cited keys)

- original: 113 references, 1 warnings: Warning--entry type for "scikit-optimize_2021" isn't style-file defined; no DOI appears twice in the .bbl
- fixed: 113 references, 1 warnings: Warning--entry type for "scikit-optimize_2021" isn't style-file defined; no DOI appears twice in the .bbl

## 12. What could not be checked

- No registry record (17 cited entries): `fitzner_baybe_2022`, `lin_preference_2022`, `mqs_cosmo_2024`, `jiang_efficient_2020`, `baird_introduction_2024`, `balandat2020botorch`, `JMLRdragonfly`, `daulton2021parallel`, `poloczek2017multi`, `snoek2012practical`, `bergstra2012random`, `landrum2013rdkit`, `bakshy2018ax`, `stair-lab_coh2`, `kusner2017grammar`, `athalye_gavel_2016`, `acbo_followup_2026`. NeurIPS volumes 35 and 36 are in Crossref through Curran Associates (prefix 10.52202) and were checked; earlier NeurIPS/NIPS volumes, ICML and AISTATS (PMLR) and JMLR papers are not in Crossref, and software, web pages, videos and datasets have no DOI here. Their volume, page and year fields were not verified.
- Venue claims taken from arXiv comments or journal_ref (ICML 2024 for `kristiadi_sober_2024`, AISTATS 2024 for `adachi_looping_2024`) are author supplied and could not be confirmed in Crossref.
- `acbo_followup_2026` points to a GitHub issue comment; it was not fetched.
- Author lists were compared by family name only; given names, initials and diacritics were not compared.
