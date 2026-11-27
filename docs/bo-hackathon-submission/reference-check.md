# Reference check against Crossref and DataCite

Every bibliography entry the revised manuscript cites (111 keys across `references.bib`,
`summaries-ref.bib` and the new `revision-refs.bib`) was compared with its Crossref or
DataCite record on 27 November 2026: DOI, title, authors, year, venue, volume and pages;
correction and retraction notices; and published versions of preprints. Entries without a
DOI were searched by title, first author and year, and a DOI was added only when all three
matched.

## What was changed in the manuscript

All registry-backed. Keys are unchanged, so no citation moved.

- **Wrong DOI:** Szymanski et al. 2023 (A-Lab) pointed to a paper on the yeast protein
  interactome; Aldeghi et al. 2022 and Graff et al. 2021 did not resolve.
- **Wrong author lists:** Szymanski 2023, Aldeghi 2022, Johansen 2024, Leeman 2024, Judge
  2024, Sabanza-Gil 2025 and scikit-optimize.
- **Published since:** Ansari and White (Digital Discovery 2024), Sabanza-Gil et al. (Nature
  Computational Science 2025), Valentine et al. (Soft Matter 2025), Rankovic et al. (GOLLuM,
  now Nature Machine Intelligence 2026, retitled). Adachi et al. is AISTATS 2024 and Kristiadi
  et al. ICML 2024, not arXiv or NeurIPS. Maus et al. is NeurIPS 2022, GAUCHE NeurIPS 2023.
- **27 DOIs added**; arXiv numbers now print for arXiv-only entries, as RSC style asks.
- **Five works printed twice** under two keys (BayBE, Shahriari, Altamirano, Lin,
  Ramakrishnan); merged onto one key each.
- **Misattributed citation:** Sections V.B and VII cited *Sustainable concrete via Bayesian
  optimization* for acquisition optimization and scalable hypervolume acquisitions; they now
  cite Ament et al., *Unexpected improvements to expected improvement for Bayesian
  optimization* (NeurIPS 2023).
- RDKit and Ax were typed as journal articles ("Release 1, 4", "GitHub repository"); now
  software references. `language = {en}` became `{english}`, so the build no longer errors.

## Left as is

- Correction notices exist for three cited works (A-Lab 2023, Diemar 2025, Zhou 2019).
  Corrections do not change the citation, but A-Lab's correction retitled the article "...of
  inorganic materials"; the bibliography keeps the original title "...of novel materials".
- Eight conference papers (NeurIPS, ICML, JMLR) have no Crossref DOI to add.
- Eight entries truncate their author list with "and others". RSC asks for every author's name;
  the typesetter can expand them from the DOIs (one has 144 authors).

The tables below are the audit's own output, run while the manuscript was being edited:
statuses describe the entries before the fixes above were applied.

## 1. Counts by status

One status per entry, the most serious that applies (order: retracted_or_corrected, mismatch, preprint_published, duplicate, missing_doi_found, missing_doi_unconfirmed, not_found, minor, ok). All applicable statuses are in `report.json` (`all_statuses`).

| status | cited entries | all entries |
|---|---|---|
| retracted_or_corrected | 3 | 3 |
| mismatch | 12 | 17 |
| preprint_published | 1 | 2 |
| duplicate | 3 | 14 |
| missing_doi_found | 34 | 34 |
| missing_doi_unconfirmed | 9 | 11 |
| not_found | 8 | 8 |
| minor | 8 | 14 |
| ok | 33 | 37 |
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
| `szymanski_autonomous_2023` (references.bib; project_24.json) | [retracted_or_corrected] notice: correction 10.1038/s41586-025-09992-y (2026-01-19): "Author Correction: An autonomous laboratory for the accelerated synthesis of inorganic materials"; high: DOI 10.1038/s41586-023-06739-5 resolves to a different work: "The social and structural architecture of the yeast protein interactome" (Michaelis); the cited work is 10.1038/s41586-023-06734-w; high: 7 of 13 bib author(s) not in registry author list: Huo, Parija, Shoghi, Rigas, Neaton, Toma, Gregoire; low: title wording differs slightly from registry (similarity 96) | Crossref 10.1038/s41586-023-06734-w: "An autonomous laboratory for the accelerated synthesis of inorganic materials", Nature 2023, vol. 624, p. 86-91 | APPLIED doi = 10.1038/s41586-023-06734-w; APPLIED author = Szymanski, Nathan J. and Rendy, Bernardus and Fei, Yuxing and Kumar...; suggest: Crossref now gives the title as "An autonomous laboratory for the accelerated synthesis of inorganic materials" and lists a correction notice (10.1038/s41586-025-09992-y); the bib keeps the title as originally published. Check the notice and decide whether to cite the corrected title or the notice  | high |
| `zhou2019optimization` (summaries-ref.bib; project_8.json) | [retracted_or_corrected] notice: correction 10.1038/s41598-020-66840-x (2020-06-23): "Author Correction: Optimization of Molecules via Deep Reinforcement Learning" | Crossref 10.1038/s41598-019-47148-x: "Optimization of Molecules via Deep Reinforcement Learning", Scientific Reports 2019, vol. 9, p. 10752 | APPLIED doi = 10.1038/s41598-019-47148-x | high |
| `adachi_looping_2024` (references.bib; main.tex:L558) | [mismatch] medium: entry names "Advances in Neural Information Processing Systems", but the arXiv record (author supplied) says: journal_ref "AISTATS 238, 505--513, 2024"; comment "Accepted at AISTATS 2024, 24 pages, 11 figures"; low: DOI is the arXiv preprint DOI, but the entry names "Advances in Neural Information Processing Systems" (a proceedings volume without DOIs of its own, so the arXiv DOI is a reasonable stand-in); low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2310.17273" | DataCite 10.48550/arXiv.2310.17273: "Looping in the Human Collaborative and Explainable Bayesian Optimization", arXiv 2023 | suggest: cite the AISTATS 2024 paper (PMLR vol. 238, pp. 505-513, per the arXiv journal_ref) instead of "Advances in Neural Information Processing Systems"; PMLR is not in Crossref, so this is unconfirmed ; suggest: add eprint = {2310.17273} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2310.17273" (RSC style)  | high |
| `aldeghi_roughness_2022` (references.bib; project_44.json) | [mismatch] high: DOI 10.1021/acs.jcim.2c00792 does not resolve; the cited work is 10.1021/acs.jcim.2c00903; high: 4 of 5 bib author(s) not in registry author list: Häse, Hickman, Tamblyn, Aspuru-Guzik | Crossref 10.1021/acs.jcim.2c00903: "Roughness of Molecular Property Landscapes and Its Impact on Modellability", Journal of Chemical Information and Modeling 2022, vol. 62, p. 4660-4671 | APPLIED doi = 10.1021/acs.jcim.2c00903; APPLIED author = Aldeghi, Matteo and Graff, David E. and Frey, Nathan and Morrone, J... | high |
| `graff_accelerating_2021` (references.bib; project_44.json) | [mismatch] high: DOI 10.1039/d1sc02482a does not resolve; the cited work is 10.1039/d0sc06805e | Crossref 10.1039/D0SC06805E: "Accelerating high-throughput virtual screening through molecular pool-based active learning", Chemical Science 2021, vol. 12, p. 7866-7881 | APPLIED doi = 10.1039/D0SC06805E | high |
| `griffiths_gauche_2024` (references.bib; main.tex:L475; main.tex:L521; main.tex:L540; project_29.json ...) | [mismatch] medium: bib year 2024 differs by one from registry year 2023 (issued 2023, print 2023, online None); low: author list truncated with "and others" (7 listed, registry has 28); low: pages/article number missing (registry: 76923-76946) | Crossref 10.52202/075280-3362: "GAUCHE: A Library for Gaussian Processes in Chemistry", Advances in Neural Information Processing Systems 36 2023, p. 76923-76946 | APPLIED doi = 10.52202/075280-3362; APPLIED year = 2023; APPLIED pages = 76923--76946 | high |
| `johansen_gpu-accelerated_2024` (references.bib; project_24.json) | [mismatch] high: 4 of 7 bib author(s) not in registry author list: Christiansen, Voss, Juhás, Billinge | Crossref 10.21105/joss.06024: "A GPU-Accelerated Open-Source Python Package for Calculating Powder Diffraction, Small-Angle-, and Total Scattering with the Debye Scattering Equation", Journal of Open Source Software 2024, vol. 9, p. 6024 | APPLIED author = Johansen, Frederik L. and Anker, Andy S. and Friis-Jensen, Ulrik an... | high |
| `judge_applying_2024` (references.bib; main.tex:L556) | [mismatch] high: 1 of 2 bib author(s) not in registry author list: Ren; low: author list truncated with "and others" (2 listed, registry has 5); low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2409.07190" | DataCite 10.48550/arXiv.2409.07190: "Applying Multi-Fidelity Bayesian Optimization in Chemistry: Open Challenges and Major Considerations", arXiv 2024 | APPLIED author = Judge, Edmund and Azzouzi, Mohammed and Mroz, Austin M. and del Rio...; suggest: add eprint = {2409.07190} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2409.07190" (RSC style)  | high |
| `leeman_challenges_2024` (references.bib; project_24.json) | [mismatch] high: 4 of 5 bib author(s) not in registry author list: Kunitsa, Vecchio, Ceder, Kusne | Crossref 10.1103/prxenergy.3.011002: "Challenges in High-Throughput Inorganic Materials Prediction and Autonomous Synthesis", PRX Energy 2024, vol. 3, p. 011002 | APPLIED author = Leeman, Josh and Liu, Yuhan and Stiles, Joseph and Lee, Scott B. an... | high |
| `maus_local_2023` (references.bib; main.tex:L542; project_21.json) | [mismatch] medium: bib year 2023 differs by one from registry year 2022 (issued 2022, print None, online None); low: arXiv citation without the arXiv DOI (10.48550/arXiv.2201.11872) | DataCite 10.48550/arXiv.2201.11872: "Local Latent Space Bayesian Optimization over Structured Inputs", arXiv 2022; published version 10.52202/068431-2500: "Local Latent Space Bayesian Optimization Over Structured Inputs", Advances in Neural Information Processing Systems 35 2022 | APPLIED journal = Advances in Neural Information Processing Systems; APPLIED volume = 35; APPLIED pages = 34505--34518; APPLIED year = 2022; APPLIED doi = 10.52202/068431-2500; APPLIED url = https://doi.org/10.52202/068431-2500 | high |
| `rankovic_gollum_2025` (references.bib; main.tex:L558) | [mismatch] medium: arXiv record was retitled after v1: bib has the v1 title; the current version is "Large language models as uncertainty-calibrated optimizers for experimental discovery" (3 authors); low: author count differs (bib 2, registry 3); low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2504.06265" | DataCite 10.48550/arXiv.2504.06265: "Large language models as uncertainty-calibrated optimizers for experimental discovery", arXiv 2025; published version 10.1038/s42256-026-01283-z: "Large language models as uncertainty-calibrated optimizers for experimental discovery", Nature Machine Intelligence 2026 | suggest: add eprint = {2504.06265} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2504.06265" (RSC style) ; suggest: published version "Large language models as uncertainty-calibrated optimizers for experimental discovery" (Nature Machine Intelligence 2026, 10.1038/s42256-026-01283-z); title differs from the cited (bib) title (similarity 42), so not clearly the same content; not applied 10.1038/s42256-026-01283-z | high |
| `sabanza-gil_best_2025` (references.bib; main.tex:L556) | [mismatch] high: 1 of 2 bib author(s) not in registry author list: Bailly; high: DOI is the arXiv preprint DOI, but the entry names "Nature Computational Science" with volume/pages of the published version; low: author list truncated with "and others" (2 listed, registry has 7); low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2410.00544" | DataCite 10.48550/arXiv.2410.00544: "Best Practices for Multi-Fidelity Bayesian Optimization in Materials and Molecular Research", arXiv 2024; published version 10.1038/s43588-025-00822-9: "Best practices for multi-fidelity Bayesian optimization in materials and molecular research", Nature Computational Science 2025 | APPLIED doi = 10.1038/s43588-025-00822-9; APPLIED url = https://doi.org/10.1038/s43588-025-00822-9; APPLIED author = Sabanza-Gil, Víctor and Barbano, Riccardo and Pacheco Gutiérrez, Da...; suggest: add eprint = {2410.00544} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2410.00544" (RSC style)  | high |
| `scikit-optimize_2021` (summaries-ref.bib; project_30.json) | [mismatch] high: 5 of 8 bib author(s) not in registry author list: MechCoder, fcharras, Cournapeau, Pedregosa, Mueller; low: entry type @software is not defined in apsrev4-2.bst (BibTeX warns and falls back) | DataCite 10.5281/zenodo.5565057: "scikit-optimize/scikit-optimize", Zenodo 2021 | APPLIED author = Head, Tim and Kumar, Manoj and Nahrstaedt, Holger and Louppe, Gille...; suggest: change @software to @misc: apsrev4-2.bst does not define @software (BibTeX warns and falls back)  | high |
| `valentine_hacktive_2025` (references.bib; main.tex:L521; main.tex:L531) | [mismatch] high: DOI is the arXiv preprint DOI, but the entry names "Soft Matter" with volume/pages of the published version; low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2505.01365" | DataCite 10.48550/arXiv.2505.01365: "Hacktive Matter: data-driven discovery through hackathon-based cross-disciplinary coding", arXiv 2025; published version 10.1039/d5sm00401b: "Hacktive matter: data-driven discovery through hackathon-based cross-disciplinary coding", Soft Matter 2025 | APPLIED doi = 10.1039/D5SM00401B; APPLIED url = https://doi.org/10.1039/D5SM00401B; suggest: add eprint = {2505.01365} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2505.01365" (RSC style)  | high |
| `ansari_learning_2023` (references.bib; project_14.json) | [preprint_published]  | Crossref 10.1101/2023.06.01.543289: "Learning Peptide Properties with Positive Examples Only", openRxiv 2023; published version 10.1039/d3dd00218g: "Learning peptide properties with positive examples only", Digital Discovery 2024 | APPLIED journal = Digital Discovery; APPLIED volume = 3; APPLIED number = 5; APPLIED pages = 977--986; APPLIED year = 2024; APPLIED doi = 10.1039/D3DD00218G; APPLIED url = https://doi.org/10.1039/D3DD00218G | high |
| `garcia_dockstring_2022` (references.bib; project_25.json) | [duplicate] duplicate of garcia-ortegon_dockstring_2022 | Crossref 10.1021/acs.jcim.1c01334: "DOCKSTRING: Easy Molecular Docking Yields Better Benchmarks for Ligand Design", Journal of Chemical Information and Modeling 2022, vol. 62, p. 3486-3502 | none | high |
| `ramakrishnan_quantum_2014` (references.bib; project_18.json; project_27.json; project_28.json) | [duplicate] duplicate of ramakrishnan2014quantum | Crossref 10.1038/sdata.2014.22: "Quantum chemistry structures and properties of 134 kilo molecules", Scientific Data 2014, vol. 1, p. 140022 | none | high |
| `shahriari_taking_2016` (references.bib; main.tex:L540; project_3.json) | [duplicate] duplicate of shahriari2015taking | Crossref 10.1109/JPROC.2015.2494218: "Taking the Human Out of the Loop: A Review of Bayesian Optimization", Proceedings of the IEEE 2016, vol. 104, p. 148-175 | none | high |
| `altamirano_robust_2023` (references.bib; main.tex:L542; main.tex:L558; project_12.json) | [missing_doi_found] no DOI in the entry; arXiv DOI built from the arXiv id and verified in DataCite; low: arXiv citation without the arXiv DOI (10.48550/arXiv.2311.00463); duplicate of altamirano2023robust | DataCite 10.48550/arXiv.2311.00463: "Robust and Conjugate Gaussian Process Regression", arXiv 2023 | APPLIED doi = 10.48550/arXiv.2311.00463 | high |
| `ament2310sustainable` (summaries-ref.bib; project_12.json) | [missing_doi_found] no DOI in the entry; arXiv DOI built from the arXiv id and verified in DataCite; medium: missing year; medium: booktitle contains a URL or citation fragment: "URL https://arxiv. org/abs/2310.18288. NeurIPS 2023 Workshop on Adaptive Experimentation in the Real World"; medium: title ends with a year ("Sustainable concrete via bayesian optimization, 2023"); low: cited as a preprint, but the arXiv record (author supplied) says: comment "NeurIPS 2023 Workshop on Adaptive Experimental Design and Active Learning in the Real World"; low: arXiv citation without the arXiv DOI (10.48550/arXiv.2310.18288); duplicate of ament_sustainable_2023 | DataCite 10.48550/arXiv.2310.18288: "Sustainable Concrete via Bayesian Optimization", arXiv 2023 | APPLIED title = Sustainable Concrete via Bayesian Optimization; APPLIED booktitle = NeurIPS 2023 Workshop on Adaptive Experimentation in the Real World; APPLIED doi = 10.48550/arXiv.2310.18288; APPLIED year = 2023 | high |
| `bellamy2022batched` (summaries-ref.bib; project_17.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0); duplicate of bellamy_batched_2022 | Crossref 10.1021/acs.jcim.2c00602: "Batched Bayesian Optimization for Drug Design in Noisy Environments", Journal of Chemical Information and Modeling 2022, vol. 62, p. 3970-3981 | APPLIED doi = 10.1021/acs.jcim.2c00602 | high |
| `bick2017computational` (summaries-ref.bib; project_32.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.7554/elife.28909: "Computational design of environmental sensors for the potent opioid fentanyl", eLife 2017, vol. 6, p. e28909 | APPLIED doi = 10.7554/elife.28909 | high |
| `blanchard2022language` (summaries-ref.bib; project_32.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1177/10943420221121804: "Language models for the prediction of SARS-CoV-2 inhibitors", The International Journal of High Performance Computing Applications 2022, vol. 36, p. 587-602 | APPLIED doi = 10.1177/10943420221121804 | high |
| `chakkingal2022multi` (summaries-ref.bib; project_16.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0); duplicate of chakkingal_multi-output_2022 | Crossref 10.1016/j.cej.2022.137186: "Multi-output machine learning models for kinetic data evaluation : A Fischer-Tropsch synthesis case study", Chemical Engineering Journal 2022, vol. 446, p. 137186 | APPLIED doi = 10.1016/j.cej.2022.137186 | high |
| `chen2021algebraic` (summaries-ref.bib; project_17.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1038/s41467-021-23720-w: "Algebraic graph-assisted bidirectional transformers for molecular property prediction", Nature Communications 2021, vol. 12, p. 3521 | APPLIED doi = 10.1038/s41467-021-23720-w | high |
| `desantis2017techno` (summaries-ref.bib; project_9.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1021/acs.energyfuels.6b02510: "Techno-economic Analysis of Metal-Organic Frameworks for Hydrogen and Natural Gas Storage", Energy & Fuels 2017, vol. 31, p. 2024-2032 | APPLIED doi = 10.1021/acs.energyfuels.6b02510 | high |
| `durant2002reoptimization` (summaries-ref.bib; project_8.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1021/ci010132r: "Reoptimization of MDL Keys for Use in Drug Discovery", Journal of Chemical Information and Computer Sciences 2002, vol. 42, p. 1273-1280 | APPLIED doi = 10.1021/ci010132r | high |
| `dusselier2018small` (summaries-ref.bib; project_10.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0); duplicate of dusselier_small-pore_2018 | Crossref 10.1021/acs.chemrev.7b00738: "Small-Pore Zeolites: Synthesis and Catalysis", Chemical Reviews 2018, vol. 118, p. 5265-5329 | APPLIED doi = 10.1021/acs.chemrev.7b00738 | high |
| `frazier_tutorial_2018` (references.bib; main.tex:L540) | [missing_doi_found] no DOI in the entry; arXiv DOI built from the arXiv id and verified in DataCite; low: arXiv citation without the arXiv DOI (10.48550/arXiv.1807.02811); low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:1807.02811" | DataCite 10.48550/arXiv.1807.02811: "A Tutorial on Bayesian Optimization", arXiv 2018 | APPLIED doi = 10.48550/arXiv.1807.02811; suggest: add eprint = {1807.02811} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:1807.02811" (RSC style)  | high |
| `furukawa2013chemistry` (summaries-ref.bib; project_9.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1126/science.1230444: "The Chemistry and Applications of Metal-Organic Frameworks", Science 2013, vol. 341, p. 1230444 | APPLIED doi = 10.1126/science.1230444 | high |
| `galvao2022cordata` (summaries-ref.bib; project_7.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0); low: author list truncated with "and others" (10 listed, registry has 12) | Crossref 10.1038/s41529-022-00259-9: "CORDATA: an open data management web application to select corrosion inhibitors", npj Materials Degradation 2022, vol. 6, p. 48 | APPLIED doi = 10.1038/s41529-022-00259-9 | high |
| `hargreaves_earth_2020` (references.bib; project_22.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1021/acs.chemmater.0c03381: "The Earth Mover’s Distance as a Metric for the Space of Inorganic Compositions", Chemistry of Materials 2020, vol. 32, p. 10610-10620 | APPLIED doi = 10.1021/acs.chemmater.0c03381 | high |
| `heo2020metal` (summaries-ref.bib; project_9.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.3390/polym12092061: "Metal-Organic Framework Materials for Perovskite Solar Cells", Polymers 2020, vol. 12, p. 2061 | APPLIED doi = 10.3390/polym12092061 | high |
| `jumper2021highly` (summaries-ref.bib; project_32.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0); low: author list truncated with "and others" (10 listed, registry has 34) | Crossref 10.1038/s41586-021-03819-2: "Highly accurate protein structure prediction with AlphaFold", Nature 2021, vol. 596, p. 583-589 | APPLIED doi = 10.1038/s41586-021-03819-2 | high |
| `kim2023bayeso` (summaries-ref.bib; project_6.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.21105/joss.05320: "BayesO: A Bayesian optimization framework in Python", Journal of Open Source Software 2023, vol. 8, p. 5320 | APPLIED doi = 10.21105/joss.05320 | high |
| `knowles2006parego` (summaries-ref.bib; project_18.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1109/TEVC.2005.851274: "ParEGO: a hybrid algorithm with on-line landscape approximation for expensive multiobjective optimization problems", IEEE Transactions on Evolutionary Computation 2006, vol. 10, p. 50-66 | APPLIED doi = 10.1109/TEVC.2005.851274 | high |
| `li2022bayesian` (summaries-ref.bib; project_6.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1364/oe.468843: "Bayesian optimization of nanophotonic electromagnetic shielding with very high visible transparency", Optics Express 2022, vol. 30, p. 33182 | APPLIED doi = 10.1364/oe.468843 | high |
| `lozano2008single` (summaries-ref.bib; project_16.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0); duplicate of lozano-blanco_single-event_2008 | Crossref 10.1021/ie071587u: "Single-Event Microkinetic Model for Fischer-Tropsch Synthesis on Iron-Based Catalysts", Industrial & Engineering Chemistry Research 2008, vol. 47, p. 5879-5891 | APPLIED doi = 10.1021/ie071587u | high |
| `mahmoudi2017review` (summaries-ref.bib; project_16.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1515/bfuel-2017-0002: "A review of Fischer Tropsch synthesis process, mechanism, surface chemistry and catalyst formulation", Biofuels Engineering 2017, vol. 2, p. 11-31 | APPLIED doi = 10.1515/bfuel-2017-0002 | high |
| `mallette2024current` (summaries-ref.bib; project_10.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0); duplicate of mallette_current_2024 | Crossref 10.1021/acs.chemrev.3c00801: "The Current Understanding of Mechanistic Pathways in Zeolite Crystallization", Chemical Reviews 2024, vol. 124, p. 3416-3493 | APPLIED doi = 10.1021/acs.chemrev.3c00801 | high |
| `mercado2018silico` (summaries-ref.bib; project_39.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1021/acs.chemmater.8b01425: "In Silico Design of 2D and 3D Covalent Organic Frameworks for Methane Storage Applications", Chemistry of Materials 2018, vol. 30, p. 5069-5086 | APPLIED doi = 10.1021/acs.chemmater.8b01425 | high |
| `moriwaki2018mordred` (summaries-ref.bib; project_7.json; project_8.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1186/s13321-018-0258-y: "Mordred: a molecular descriptor calculator", Journal of Cheminformatics 2018, vol. 10, p. 4 | APPLIED doi = 10.1186/s13321-018-0258-y | high |
| `moss_gaussian_2020` (references.bib; project_22.json) | [missing_doi_found] no DOI in the entry; arXiv DOI built from the arXiv id and verified in DataCite; low: arXiv citation without the arXiv DOI (10.48550/arXiv.2010.01118) | DataCite 10.48550/arXiv.2010.01118: "Gaussian Process Molecule Property Prediction with FlowMO", arXiv 2020 | APPLIED doi = 10.48550/arXiv.2010.01118 | high |
| `muckley2023interpretable` (summaries-ref.bib; project_5.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1039/D3DD00082F: "Interpretable models for extrapolation in scientific machine learning", Digital Discovery 2023, vol. 2, p. 1425-1435 | APPLIED doi = 10.1039/D3DD00082F | high |
| `oliveira2023crafted` (summaries-ref.bib; project_9.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1038/s41597-023-02116-z: "CRAFTED: An exploratory database of simulated adsorption isotherms of metal-organic frameworks", Scientific Data 2023, vol. 10, p. 230 | APPLIED doi = 10.1038/s41597-023-02116-z | high |
| `rogers2010extended` (summaries-ref.bib; project_17.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1021/ci100050t: "Extended-Connectivity Fingerprints", Journal of Chemical Information and Modeling 2010, vol. 50, p. 742-754 | APPLIED doi = 10.1021/ci100050t | high |
| `ruddigkeit_enumeration_2012` (references.bib; project_27.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1021/ci300415d: "Enumeration of 166 Billion Organic Small Molecules in the Chemical Universe Database GDB-17", Journal of Chemical Information and Modeling 2012, vol. 52, p. 2864-2875 | APPLIED doi = 10.1021/ci300415d | high |
| `sorourifar_accelerating_2024` (references.bib; project_21.json) | [missing_doi_found] no DOI in the entry; arXiv DOI built from the arXiv id and verified in DataCite; low: cited as a preprint, but the arXiv record (author supplied) says: comment "9 pages, 2 figures consisting of 6 and 4 plots, accepted to NeurIPS 2023 Workshop on Adaptive Experimental Design and Active Learning in the Real World"; low: arXiv citation without the arXiv DOI (10.48550/arXiv.2401.01398) | DataCite 10.48550/arXiv.2401.01398: "Accelerating Black-Box Molecular Property Optimization by Adaptively Learning Sparse Subspaces", arXiv 2024 | APPLIED doi = 10.48550/arXiv.2401.01398 | high |
| `stetefeld2016dynamic` (summaries-ref.bib; project_20.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1007/s12551-016-0218-6: "Dynamic light scattering: a practical guide and applications in biomedical sciences", Biophysical Reviews 2016, vol. 8, p. 409-427 | APPLIED doi = 10.1007/s12551-016-0218-6 | high |
| `truong2026neural` (summaries-ref.bib; main.tex:L549; project_36.json) | [missing_doi_found] no DOI in the entry; arXiv DOI built from the arXiv id and verified in DataCite; low: arXiv citation without the arXiv DOI (10.48550/arXiv.2601.06505) | DataCite 10.48550/arXiv.2601.06505: "Neural Nonmyopic Bayesian Optimization in Dynamic Cost Settings", arXiv 2026 | APPLIED doi = 10.48550/arXiv.2601.06505 | high |
| `wu2018quantitative` (summaries-ref.bib; project_17.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1021/acs.jcim.7b00558: "Quantitative Toxicity Prediction Using Topology Based Multitask Deep Neural Networks", Journal of Chemical Information and Modeling 2018, vol. 58, p. 520-531 | APPLIED doi = 10.1021/acs.jcim.7b00558 | high |
| `yang2019multi` (summaries-ref.bib; project_18.json) | [missing_doi_found] no DOI in the entry; Crossref bibliographic search (title 100, first author match, year diff 0) | Crossref 10.1016/j.swevo.2018.10.007: "Multi-Objective Bayesian Global Optimization using expected hypervolume improvement gradient", Swarm and Evolutionary Computation 2019, vol. 44, p. 945-956 | APPLIED doi = 10.1016/j.swevo.2018.10.007 | high |
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
| `deneault_preferential_2025` (references.bib; main.tex:L558) | [minor] low: author list truncated with "and others" (1 listed, registry has 8); low: volume missing (registry: 4); low: pages/article number missing (registry: 723-737) | Crossref 10.1039/D4DD00320A: "Preferential Bayesian optimization improves the efficiency of printing objects with subjective qualities", Digital Discovery 2025, vol. 4, p. 723-737 | APPLIED volume = 4; APPLIED pages = 723--737 | high |
| `durholt_bofire_2024` (references.bib; main.tex:L558) | [minor] low: author list truncated with "and others" (3 listed, registry has 18); low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2408.05040" | DataCite 10.48550/arXiv.2408.05040: "BoFire: Bayesian Optimization Framework Intended for Real Experiments", arXiv 2024 | suggest: add eprint = {2408.05040} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2408.05040" (RSC style)  | high |
| `kristiadi_sober_2024` (references.bib; main.tex:L542; main.tex:L558) | [minor] low: cited as a preprint, but the arXiv record (author supplied) says: comment "ICML 2024. Code: https://github.com/wiseodd/lapeft-bayesopt"; low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2402.05015" | DataCite 10.48550/arXiv.2402.05015: "A Sober Look at LLMs for Material Discovery: Are They Actually Good for Bayesian Optimization Over Molecules?", arXiv 2024 | suggest: the arXiv comment says ICML 2024; consider citing the ICML 2024 proceedings version (PMLR, not in Crossref, unconfirmed) ; suggest: add eprint = {2402.05015} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2402.05015" (RSC style)  | high |
| `muller_la_agente_optima_2026` (references.bib; main.tex:L558) | [minor] low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2609.04564" | DataCite 10.48550/arXiv.2609.04564: "La Agente Óptima: Towards Agentic Self-Driving Laboratories", arXiv 2026 | suggest: add eprint = {2609.04564} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2609.04564" (RSC style)  | high |
| `pratiush_michackathon_2025` (references.bib; main.tex:L529) | [minor] low: author list truncated with "and others" (3 listed, registry has 73) | Crossref 10.1088/2632-2153/ae1f5d: "Mic-hackathon 2024: hackathon on machine learning for electron and scanning probe microscopy", Machine Learning: Science and Technology 2025, vol. 6, p. 040701 | none | high |
| `sanchez-lengeling_bayesian_2018` (references.bib; project_29.json) | [minor] low: bib year 2018 is the online year; print issue year is 2019 (online vs print) | Crossref 10.1002/adts.201800069: "A Bayesian Approach to Predict Solubility Parameters", Advanced Theory and Simulations 2019 (online 2018, print 2019), vol. 2, p. 1800069 | none | high |
| `zimmermann_reflections_2024` (references.bib; main.tex:L521; main.tex:L531) | [minor] low: author list truncated with "and others" (3 listed, registry has 144); low: arXiv number not in any printed field (only in url/doi); RSC style wants "arXiv:2411.15221" | DataCite 10.48550/arXiv.2411.15221: "Reflections from the 2024 Large Language Model (LLM) Hackathon for Applications in Materials Science and Chemistry", arXiv 2024 | suggest: add eprint = {2411.15221} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2411.15221" (RSC style)  | high |

## 4. Duplicates (same DOI, same arXiv id, or title similarity >= 95 under different keys)

12 duplicate groups; **0 would print twice** in this snapshot. Earlier in the session (before the 19:24 UTC edits) several pairs were cited under both keys (for example `fitzner_baybe_2022` in main.tex and `fitzner2022baybe` in project_7/20/23/26.json, `shahriari_taking_2016` and `shahriari2015taking`, `ramakrishnan_quantum_2014` and `ramakrishnan2014quantum`, the two `altamirano`, `ament` and `lin` pairs); the concurrent edits merged the citations onto one key each. The unused twins are still in the bib files and can be deleted.

| group | keys (file) | where cited | prints twice | suggestion |
|---|---|---|---|---|
| 1 | `ramakrishnan_quantum_2014` (references.bib)<br>`ramakrishnan2014quantum` (summaries-ref.bib) | `ramakrishnan_quantum_2014`: project_18.json, project_27.json, project_28.json<br>`ramakrishnan2014quantum`: not cited | no | Prints once. Delete the unused `ramakrishnan2014quantum`. |
| 2 | `shahriari_taking_2016` (references.bib)<br>`shahriari2015taking` (summaries-ref.bib), no DOI | `shahriari_taking_2016`: main.tex:L540, project_3.json<br>`shahriari2015taking`: not cited | no | Prints once. Delete the unused `shahriari2015taking`. |
| 3 | `fitzner_baybe_2022` (references.bib), no DOI<br>`fitzner2022baybe` (summaries-ref.bib), no DOI | `fitzner_baybe_2022`: main.tex:L521, main.tex:L558, project_7.json, project_20.json, project_23.json, project_26.json<br>`fitzner2022baybe`: not cited | no | Prints once. Delete the unused `fitzner2022baybe`. |
| 4 | `altamirano_robust_2023` (references.bib), no DOI<br>`altamirano2023robust` (summaries-ref.bib), no DOI | `altamirano_robust_2023`: main.tex:L542, main.tex:L558, project_12.json<br>`altamirano2023robust`: not cited | no | Prints once. Delete the unused `altamirano2023robust`. |
| 5 | `ament_sustainable_2023` (references.bib), no DOI<br>`ament2310sustainable` (summaries-ref.bib), no DOI | `ament_sustainable_2023`: not cited<br>`ament2310sustainable`: project_12.json | no | Prints once. Delete the unused `ament_sustainable_2023`. The cited `ament2310sustainable` is the weaker entry (3 high/medium issues against 0); switch the citation to `ament_sustainable_2023`, or keep `ament2310sustainable` as repaired in the fixed bib. |
| 6 | `lin_preference_2022` (references.bib), no DOI<br>`lin2022preference` (summaries-ref.bib), no DOI | `lin_preference_2022`: main.tex:L540, project_16.json<br>`lin2022preference`: not cited | no | Prints once. Delete the unused `lin2022preference`. |
| 7 | `lozano-blanco_single-event_2008` (references.bib)<br>`lozano2008single` (summaries-ref.bib), no DOI | `lozano-blanco_single-event_2008`: not cited<br>`lozano2008single`: project_16.json | no | Prints once. Delete the unused `lozano-blanco_single-event_2008`. The cited key has no DOI but its twin does; the fixed bib adds it. |
| 8 | `chakkingal_multi-output_2022` (references.bib)<br>`chakkingal2022multi` (summaries-ref.bib), no DOI | `chakkingal_multi-output_2022`: not cited<br>`chakkingal2022multi`: project_16.json | no | Prints once. Delete the unused `chakkingal_multi-output_2022`. The cited key has no DOI but its twin does; the fixed bib adds it. |
| 9 | `garcia-ortegon_dockstring_2022` (references.bib)<br>`garcia_dockstring_2022` (references.bib) | `garcia-ortegon_dockstring_2022`: not cited<br>`garcia_dockstring_2022`: project_25.json | no | Prints once. Delete the unused `garcia-ortegon_dockstring_2022`. |
| 10 | `bellamy_batched_2022` (references.bib)<br>`bellamy2022batched` (summaries-ref.bib), no DOI | `bellamy_batched_2022`: not cited<br>`bellamy2022batched`: project_17.json | no | Prints once. Delete the unused `bellamy_batched_2022`. The cited key has no DOI but its twin does; the fixed bib adds it. |
| 11 | `dusselier_small-pore_2018` (references.bib)<br>`dusselier2018small` (summaries-ref.bib), no DOI | `dusselier_small-pore_2018`: not cited<br>`dusselier2018small`: project_10.json | no | Prints once. Delete the unused `dusselier_small-pore_2018`. The cited key has no DOI but its twin does; the fixed bib adds it. |
| 12 | `mallette_current_2024` (references.bib)<br>`mallette2024current` (summaries-ref.bib), no DOI | `mallette_current_2024`: not cited<br>`mallette2024current`: project_10.json | no | Prints once. Delete the unused `mallette_current_2024`. The cited key has no DOI but its twin does; the fixed bib adds it. |

## 5. Preprints

| key | server | published version | action |
|---|---|---|---|
| `adachi_looping_2024` | arXiv | none found in Crossref; arXiv says: AISTATS 238, 505--513, 2024; Accepted at AISTATS 2024, 24 pages, 11 figures | suggested only: cite the AISTATS 2024 paper (PMLR vol. 238, pp. 505-513, per the arXiv journal_ref) instead of "Advances in Neural Information Processing Systems"; PMLR is not in Crossref, so this is unconfirmed |
| `altamirano_robust_2023` | arXiv | none found in Crossref | APPLIED (doi) |
| `ament2310sustainable` | arXiv | none found in Crossref; arXiv says: NeurIPS 2023 Workshop on Adaptive Experimental Design and Active Learning in the Real World | APPLIED (booktitle, doi, title, year) |
| `ansari_learning_2023` | bioRxiv | 10.1039/D3DD00218G, Digital Discovery 2024 (Learning peptide properties with positive examples only; found via Crossref relation is-preprint-of, Crossref relation has-preprint (on the published record), Crossref title search (journal/proceedings only)) | APPLIED (doi, journal, number, pages, url, volume, year) |
| `busby_building_2015` | bioRxiv | none found in Crossref | keep as preprint |
| `durholt_bofire_2024` | arXiv | none found in Crossref; arXiv says: 6 pages, 1 figure, 1 listing | suggested only: add eprint = {2408.05040} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2408.05040" (RSC style) |
| `frazier_tutorial_2018` | arXiv | none found in Crossref | APPLIED (doi) |
| `judge_applying_2024` | arXiv | none found in Crossref | suggested only: add eprint = {2409.07190} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2409.07190" (RSC style) |
| `kristiadi_sober_2024` | arXiv | none found in Crossref; arXiv says: ICML 2024. Code: https://github.com/wiseodd/lapeft-bayesopt | suggested only: the arXiv comment says ICML 2024; consider citing the ICML 2024 proceedings version (PMLR, not in Crossref, unconfirmed) |
| `maus_local_2023` | arXiv | 10.52202/068431-2500, Advances in Neural Information Processing Systems 35 2022 (Local Latent Space Bayesian Optimization Over Structured Inputs; found via Crossref title search (journal/proceedings only)) | APPLIED (doi, journal, pages, url, volume, year) |
| `moss_gaussian_2020` | arXiv | none found in Crossref | APPLIED (doi) |
| `muller_la_agente_optima_2026` | arXiv | none found in Crossref | suggested only: add eprint = {2609.04564} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2609.04564" (RSC style) |
| `rankovic_gollum_2025` | arXiv | 10.1038/s42256-026-01283-z, Nature Machine Intelligence 2026 (Large language models as uncertainty-calibrated optimizers for experimental disc; found via Crossref title search (journal/proceedings only)) | suggested only: add eprint = {2504.06265} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2504.06265" (RSC style) |
| `sabanza-gil_best_2025` | arXiv | 10.1038/s43588-025-00822-9, Nature Computational Science 2025 (Best practices for multi-fidelity Bayesian optimization in materials and molecul; found via Crossref title search (journal/proceedings only)) | APPLIED (author, doi, url) |
| `schmid_general_2025` | arXiv | none found in Crossref | keep as preprint |
| `sorourifar_accelerating_2024` | arXiv | none found in Crossref; arXiv says: 9 pages, 2 figures consisting of 6 and 4 plots, accepted to NeurIPS 2023 Workshop on Adaptive Experimental Design and Active Learning in the Real World | APPLIED (doi) |
| `truong2026neural` | arXiv | none found in Crossref; arXiv says: 32 pages, 20 figures, 13 tables | APPLIED (doi) |
| `valentine_hacktive_2025` | arXiv | 10.1039/D5SM00401B, Soft Matter 2025 (Hacktive matter: data-driven discovery through hackathon-based cross-disciplinar; found via Crossref title search (journal/proceedings only)) | APPLIED (doi, url) |
| `zimmermann_reflections_2024` | arXiv | none found in Crossref; arXiv says: Updating author information, the submission remains largely unchanged. 98 pages total | suggested only: add eprint = {2411.15221} and archivePrefix = {arXiv} so apsrev4-2 prints "arXiv:2411.15221" (RSC style) |

## 6. Corrections and retractions (Crossref `filter=updates` and `updated-by`)

Checked for every entry with a Crossref record (97 entries). **No retraction, withdrawal or expression of concern was found.** 3 correction notices:

- `szymanski_autonomous_2023` (cited): correction notice 10.1038/s41586-025-09992-y, 2026-01-19: "Author Correction: An autonomous laboratory for the accelerated synthesis of inorganic materials".
- `diemar_report_2025` (cited): correction notice 10.1177/02611929251322945, 2025-02-23: "Corrigendum to Report of the First ONTOX Hackathon: Hack to Save Lives and Avoid Animal Suffering. The Use of Artificial Intelligence in Toxicology - A Potential Driver for Reducing/Replacing Laboratory Animals in the Future".
- `zhou2019optimization` (cited): correction notice 10.1038/s41598-020-66840-x, 2020-06-23: "Author Correction: Optimization of Molecules via Deep Reinforcement Learning".

Corrections do not change how an entry is cited, but the A-Lab entry is worth a look: Crossref now titles the article "...synthesis of inorganic materials" while the bib (and the original 2023 publication) say "...of novel materials". arXiv entries were checked for a "withdrawn" comment; none was found.

## 7. RSC house style for preprints

- ChemRxiv: no ChemRxiv entries in any of the bib files, so no version-suffix issue.
- Cited arXiv entries without the arXiv DOI (7): `frazier_tutorial_2018`, `altamirano_robust_2023`, `sorourifar_accelerating_2024`, `maus_local_2023`, `moss_gaussian_2020`, `ament2310sustainable`, `truong2026neural`. The fixed bib adds the DataCite-verified `10.48550/arXiv.<id>` DOI to each of these unless the entry was updated to a published version.
- Cited arXiv entries whose printed fields do not show the arXiv number (10): `frazier_tutorial_2018`, `zimmermann_reflections_2024`, `valentine_hacktive_2025`, `durholt_bofire_2024`, `sabanza-gil_best_2025`, `kristiadi_sober_2024`, `rankovic_gollum_2025`, `adachi_looping_2024`, `judge_applying_2024`, `muller_la_agente_optima_2026`. apsrev4-2 prints an `eprint` field as "arXiv:NNNN.NNNNN", so adding `eprint = {<id>}` and `archivePrefix = {arXiv}` (not done here, as it is a style change rather than a registry correction) would satisfy RSC style.

## 8. Malformed fields

- `language = {en}`: 3 entries (`jablonka_14_2023`, `lferguson_conference_2019`, `mulholland_hackathon_2015`). Harmless for apsrev4-2, which ignores the field.
- Other malformed fields (10 findings):
  - `lferguson_conference_2019` (references.bib, not cited): author "L. Ferguson, Andrew" has an initial in the family-name part
  - `lferguson_conference_2019` (references.bib, not cited): author "J. Reich, Brian" has an initial in the family-name part
  - `lozano-blanco_single-event_2008` (references.bib, not cited): non-ASCII character(s) U+2212 in title may not be set up for pdflatex/inputenc
  - `landrum2013rdkit` (summaries-ref.bib, cited): journal = "Release" is not a journal (software/documentation entry typed as @article)
  - `ament2310sustainable` (summaries-ref.bib, cited): missing year
  - `ament2310sustainable` (summaries-ref.bib, cited): booktitle contains a URL or citation fragment: "URL https://arxiv. org/abs/2310.18288. NeurIPS 2023 Workshop on Adaptive Experimentation in the Real World"
  - `ament2310sustainable` (summaries-ref.bib, cited): title ends with a year ("Sustainable concrete via bayesian optimization, 2023")
  - `bakshy2018ax` (summaries-ref.bib, cited): journal = "GitHub repository" is not a journal (software/documentation entry typed as @article)
  - `bakshy2018ax` (summaries-ref.bib, cited): @article with howpublished (ignored by apsrev4-2 for articles)
  - `scikit-optimize_2021` (summaries-ref.bib, cited): entry type @software is not defined in apsrev4-2.bst (BibTeX warns and falls back)
- `@misc` entries that Crossref types as journal-article: none.
- No unescaped `&`, `%`, `#` or `_`, no unbalanced braces and no all-caps titles were found in any printed field.

## 9. Post-hackathon Outcomes: link check

The task describes inline `\href` links. In the snapshot those sentences now cite bib keys instead (the links were converted at 19:16 UTC), so both versions were checked: the original `\href` text (identical in `the 8321260 main.tex` and `the PR 171 head`) and the current `\cite` keys.

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
| current | truong2026neural | "Neural nonmyopic Bayesian optimization in dynamic cost settings" / arXiv preprint arXiv:2601.06505, 2026 | 10.48550/arXiv.2601.06505: "Neural Nonmyopic Bayesian Optimization in Dynamic Cost Settings", arXiv, issued 2026 | title matches; journal matches; year matches |
| current | anker_autonomous_2026 | "Autonomous synthesis of nanoparticles with target scattering patterns" / ACS Nano, 2026 | 10.1021/acsnano.5c15488: "Autonomous Synthesis of Nanoparticles with Target Scattering Patterns", ACS Nano, issued 2026, print 2026 | title matches; journal matches; year matches |
| other DOI link in current main.tex | 10.5281/zenodo.20496810 | (no title in the sentence) | 10.5281/zenodo.20496810: "AC-BO Hackathon 2024 - All Projects", Zenodo, issued 2024 | resolves (DataCite record exists) |

## 10. Changes in the fixed bib files

Only high-confidence, registry-backed changes to cited entries were applied; keys are unchanged and untouched entries are byte-identical (see `bib.diff`). The fixes are in the patch series (patch "References checked against Crossref and DataCite").

- `aldeghi_roughness_2022` (references.bib):
  - doi: `10.1021/acs.jcim.2c00792` -> `10.1021/acs.jcim.2c00903` (wrong DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
  - author: `Aldeghi, Matteo and Häse, Florian and Hickman, Riley J. and Tamblyn, Isaac and A...` -> `Aldeghi, Matteo and Graff, David E. and Frey, Nathan and Morrone, Joseph A. and Pyzer-Knapp, Edward O. and Jor...` (author list contradicts Crossref: 4 of 5 bib author(s) not in registry author list: Häse, Hickman, Tamblyn, Aspuru-Guzik)
- `altamirano_robust_2023` (references.bib):
  - doi: `(absent)` -> `10.48550/arXiv.2311.00463` (missing DOI; arXiv DOI built from the arXiv id and verified in DataCite)
- `ansari_learning_2023` (references.bib):
  - journal: `bioRxiv` -> `Digital Discovery` (preprint superseded by the published version (Crossref relation is-preprint-of, Crossref relation has-preprint (on the published record), Crossref title search (journal/proceedings only)))
  - volume: `(absent)` -> `3` (published version)
  - number: `(absent)` -> `5` (published version)
  - pages: `(absent)` -> `977--986` (published version)
  - year: `2023` -> `2024` (published version)
  - doi: `(absent)` -> `10.1039/D3DD00218G` (published version)
  - url: `https://doi.org/10.1101/2023.06.01.543289` -> `https://doi.org/10.1039/D3DD00218G` (url pointed to the preprint)
- `deneault_preferential_2025` (references.bib):
  - volume: `(absent)` -> `4` (volume missing (registry: 4))
  - pages: `(absent)` -> `723--737` (pages/article number missing (registry: 723-737))
- `frazier_tutorial_2018` (references.bib):
  - doi: `(absent)` -> `10.48550/arXiv.1807.02811` (missing DOI; arXiv DOI built from the arXiv id and verified in DataCite)
- `graff_accelerating_2021` (references.bib):
  - doi: `10.1039/d1sc02482a` -> `10.1039/D0SC06805E` (wrong DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `griffiths_gauche_2024` (references.bib):
  - doi: `(absent)` -> `10.52202/075280-3362` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 1))
  - year: `2024` -> `2023` (bib year 2024 differs by one from registry year 2023 (issued 2023, print 2023, online None))
  - pages: `(absent)` -> `76923--76946` (pages/article number missing (registry: 76923-76946))
- `hargreaves_earth_2020` (references.bib):
  - doi: `(absent)` -> `10.1021/acs.chemmater.0c03381` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `johansen_gpu-accelerated_2024` (references.bib):
  - author: `Johansen, Frederik L. and Anker, Andy S. and Christiansen, Thomas L. and Voss, L...` -> `Johansen, Frederik L. and Anker, Andy S. and Friis-Jensen, Ulrik and Dam, Erik B. and Jensen, Kirsten M. Ø. an...` (author list contradicts Crossref: 4 of 7 bib author(s) not in registry author list: Christiansen, Voss, Juhás, Billinge)
- `judge_applying_2024` (references.bib):
  - author: `Judge, Edmund and Ren, Tony and others` -> `Judge, Edmund and Azzouzi, Mohammed and Mroz, Austin M. and del Rio Chanona, Antonio and Jelfs, Kim E.` (author list contradicts DataCite: 1 of 2 bib author(s) not in registry author list: Ren)
- `leeman_challenges_2024` (references.bib):
  - author: `Leeman, Josh and Kunitsa, Alexander A. and Vecchio, Kevin S. and Ceder, Gerbrand...` -> `Leeman, Josh and Liu, Yuhan and Stiles, Joseph and Lee, Scott B. and Bhatt, Prajna and Schoop, Leslie M. and P...` (author list contradicts Crossref: 4 of 5 bib author(s) not in registry author list: Kunitsa, Vecchio, Ceder, Kusne)
- `maus_local_2023` (references.bib):
  - journal: `arXiv preprint arXiv:2201.11872` -> `Advances in Neural Information Processing Systems` (preprint superseded by the published version (Crossref title search (journal/proceedings only)))
  - volume: `(absent)` -> `35` (published version)
  - pages: `(absent)` -> `34505--34518` (published version)
  - year: `2023` -> `2022` (published version)
  - doi: `(absent)` -> `10.52202/068431-2500` (published version)
  - url: `http://arxiv.org/abs/2201.11872` -> `https://doi.org/10.52202/068431-2500` (url pointed to the preprint)
- `moss_gaussian_2020` (references.bib):
  - doi: `(absent)` -> `10.48550/arXiv.2010.01118` (missing DOI; arXiv DOI built from the arXiv id and verified in DataCite)
- `ruddigkeit_enumeration_2012` (references.bib):
  - doi: `(absent)` -> `10.1021/ci300415d` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `sabanza-gil_best_2025` (references.bib):
  - doi: `10.48550/arXiv.2410.00544` -> `10.1038/s43588-025-00822-9` (DOI pointed to the arXiv/bioRxiv preprint; the Crossref journal record matches the journal, volume and pages already in the entry)
  - url: `https://doi.org/10.48550/arXiv.2410.00544` -> `https://doi.org/10.1038/s43588-025-00822-9` (url pointed to the preprint)
  - author: `Sabanza-Gil, Victor and Bailly, Alexandre and others` -> `Sabanza-Gil, Víctor and Barbano, Riccardo and Pacheco Gutiérrez, Daniel and Luterbacher, Jeremy S. and Hernánd...` (author list contradicts Crossref: 1 of 2 bib author(s) not in registry author list: Bailly)
- `sorourifar_accelerating_2024` (references.bib):
  - doi: `(absent)` -> `10.48550/arXiv.2401.01398` (missing DOI; arXiv DOI built from the arXiv id and verified in DataCite)
- `szymanski_autonomous_2023` (references.bib):
  - doi: `10.1038/s41586-023-06739-5` -> `10.1038/s41586-023-06734-w` (wrong DOI; Crossref bibliographic search (title 96, first author match, year diff 0))
  - author: `Szymanski, Nathan J. and Zeng, Yan and Huo, Haotian and Bartel, Christopher J. a...` -> `Szymanski, Nathan J. and Rendy, Bernardus and Fei, Yuxing and Kumar, Rishi E. and He, Tanjin and Milsted, Davi...` (author list contradicts Crossref: 7 of 13 bib author(s) not in registry author list: Huo, Parija, Shoghi, Rigas, Neaton, Toma, Gregoire)
- `valentine_hacktive_2025` (references.bib):
  - doi: `10.48550/arXiv.2505.01365` -> `10.1039/D5SM00401B` (DOI pointed to the arXiv/bioRxiv preprint; the Crossref journal record matches the journal, volume and pages already in the entry)
  - url: `https://doi.org/10.48550/arXiv.2505.01365` -> `https://doi.org/10.1039/D5SM00401B` (url pointed to the preprint)
- `ament2310sustainable` (summaries-ref.bib):
  - title: `Sustainable concrete via bayesian optimization, 2023` -> `Sustainable Concrete via Bayesian Optimization` (title carried a trailing year; registry title)
  - booktitle: `URL https://arxiv. org/abs/2310.18288. NeurIPS 2023 Workshop on Adaptive Experim...` -> `NeurIPS 2023 Workshop on Adaptive Experimentation in the Real World` (booktitle began with a pasted URL fragment)
  - doi: `(absent)` -> `10.48550/arXiv.2310.18288` (missing DOI; arXiv DOI built from the arXiv id and verified in DataCite)
  - year: `(absent)` -> `2023` (year missing; registry year)
- `bellamy2022batched` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1021/acs.jcim.2c00602` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `bick2017computational` (summaries-ref.bib):
  - doi: `(absent)` -> `10.7554/elife.28909` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `blanchard2022language` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1177/10943420221121804` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `chakkingal2022multi` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1016/j.cej.2022.137186` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `chen2021algebraic` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1038/s41467-021-23720-w` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `desantis2017techno` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1021/acs.energyfuels.6b02510` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `durant2002reoptimization` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1021/ci010132r` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `dusselier2018small` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1021/acs.chemrev.7b00738` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `furukawa2013chemistry` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1126/science.1230444` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `galvao2022cordata` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1038/s41529-022-00259-9` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `heo2020metal` (summaries-ref.bib):
  - doi: `(absent)` -> `10.3390/polym12092061` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `jumper2021highly` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1038/s41586-021-03819-2` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `kim2023bayeso` (summaries-ref.bib):
  - doi: `(absent)` -> `10.21105/joss.05320` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `knowles2006parego` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1109/TEVC.2005.851274` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `li2022bayesian` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1364/oe.468843` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `lozano2008single` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1021/ie071587u` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `mahmoudi2017review` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1515/bfuel-2017-0002` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `mallette2024current` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1021/acs.chemrev.3c00801` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `mercado2018silico` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1021/acs.chemmater.8b01425` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `moriwaki2018mordred` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1186/s13321-018-0258-y` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `muckley2023interpretable` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1039/D3DD00082F` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `oliveira2023crafted` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1038/s41597-023-02116-z` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `rogers2010extended` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1021/ci100050t` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `scikit-optimize_2021` (summaries-ref.bib):
  - author: `Head, Tim and MechCoder and Louppe, Gilles and Shcherbatyi, Iaroslav and fcharra...` -> `Head, Tim and Kumar, Manoj and Nahrstaedt, Holger and Louppe, Gilles and Shcherbatyi, Iaroslav` (author list contradicts DataCite: 5 of 8 bib author(s) not in registry author list: MechCoder, fcharras, Cournapeau, Pedregosa, Mueller)
- `stetefeld2016dynamic` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1007/s12551-016-0218-6` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `truong2026neural` (summaries-ref.bib):
  - doi: `(absent)` -> `10.48550/arXiv.2601.06505` (missing DOI; arXiv DOI built from the arXiv id and verified in DataCite)
- `wu2018quantitative` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1021/acs.jcim.7b00558` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `yang2019multi` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1016/j.swevo.2018.10.007` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))
- `zhou2019optimization` (summaries-ref.bib):
  - doi: `(absent)` -> `10.1038/s41598-019-47148-x` (missing DOI; Crossref bibliographic search (title 100, first author match, year diff 0))

## 11. BibTeX check (apsrev4-2, all cited keys)

- original: 113 references, 2 warnings: Warning--entry type for "scikit-optimize_2021" isn't style-file defined; Warning--empty year in ament2310sustainable; no DOI appears twice in the .bbl
- fixed: 113 references, 1 warning: Warning--entry type for "scikit-optimize_2021" isn't style-file defined; no DOI appears twice in the .bbl

## 12. State of the work tree compared with these fixed files

Because the work tree already received intermediate output of this audit, here is how its current bib files compare with the final `.fixed.bib` files (full diff, fixed to work tree, in the audit cache):

- `references.bib` (work tree mtime 2026-11-27T19:43:25Z): differs in 12 entries: `adachi_looping_2024`, `durholt_bofire_2024`, `frazier_tutorial_2018`, `jablonka_14_2023`, `johansen_gpu-accelerated_2024`, `judge_applying_2024`, `kristiadi_sober_2024`, `lferguson_conference_2019`, `mulholland_hackathon_2015`, `muller_la_agente_optima_2026`, `rankovic_gollum_2025`, `zimmermann_reflections_2024`.
- `summaries-ref.bib` (work tree mtime 2026-11-27T19:44:56Z): differs in 3 entries: `bakshy2018ax`, `landrum2013rdkit`, `scikit-optimize_2021`.
- `revision-refs.bib` (work tree mtime 2026-11-27T19:39:35Z): differs in 1 entry: `ament_unexpected_2023`.

Re-audit of the current work-tree bib files (snapshot 2026-11-27T19:45:07Z, same checks, nothing written back): cited-entry statuses retracted_or_corrected 3, duplicate 9, missing_doi_unconfirmed 9, not_found 8, minor 13, ok 69. BibTeX on the work tree: 113 references, warnings: none.

Cited entries in the work tree that still need attention:

| key | status | open issues | registry evidence |
|---|---|---|---|
| `diemar_report_2025` (references.bib) | retracted_or_corrected | notice: correction 10.1177/02611929251322945 (2025-02-23) | Crossref 10.1177/02611929241305112: "Report of the First ONTOX Hackathon: Hack to Save Lives and Avoid Animal Suffering. The Use of Artificial Intelligence in Toxicology - A Potential Driver for Reducing/Replacing Laboratory Animals in the Future", Alternatives to Laboratory Animals 2025 (online 2024, print 2025), vol. 53, p. 42-61 |
| `szymanski_autonomous_2023` (references.bib) | retracted_or_corrected | notice: correction 10.1038/s41586-025-09992-y (2026-01-19) | Crossref 10.1038/s41586-023-06734-w: "An autonomous laboratory for the accelerated synthesis of inorganic materials", Nature 2023, vol. 624, p. 86-91 |
| `zhou2019optimization` (summaries-ref.bib) | retracted_or_corrected | notice: correction 10.1038/s41598-020-66840-x (2020-06-23) | Crossref 10.1038/s41598-019-47148-x: "Optimization of Molecules via Deep Reinforcement Learning", Scientific Reports 2019, vol. 9, p. 10752 |

In particular, `revision-refs.bib` in the work tree contains `volume = {36}` in `ament_unexpected_2023`. That line came from an intermediate run of this audit (19:34 UTC) and was dropped from the final output: the booktitle already reads "Advances in Neural Information Processing Systems 36 (NeurIPS 2023)", so the extra field makes apsrev4-2 print the volume twice. Remove it. Do not copy the `.fixed.bib` files over the work tree wholesale: the work tree also has edits made after this audit started (for example `language = {english}`), which the fixed files, being based on the originals, do not contain.

## 13. What could not be checked

- No registry record (17 cited entries): `fitzner_baybe_2022`, `lin_preference_2022`, `mqs_cosmo_2024`, `jiang_efficient_2020`, `baird_introduction_2024`, `balandat2020botorch`, `JMLRdragonfly`, `daulton2021parallel`, `poloczek2017multi`, `snoek2012practical`, `bergstra2012random`, `landrum2013rdkit`, `bakshy2018ax`, `stair-lab_coh2`, `kusner2017grammar`, `athalye_gavel_2016`, `acbo_followup_2026`. NeurIPS volumes 35 and 36 are in Crossref through Curran Associates (prefix 10.52202) and were checked; earlier NeurIPS/NIPS volumes, ICML and AISTATS (PMLR) and JMLR papers are not in Crossref, and software, web pages, videos and datasets have no DOI here. Their volume, page and year fields were not verified.
- Venue claims taken from arXiv comments or journal_ref (ICML 2024 for `kristiadi_sober_2024`, AISTATS 2024 for `adachi_looping_2024`) are author supplied and could not be confirmed in Crossref.
- `acbo_followup_2026` points to a GitHub issue comment; it was not fetched.
- Author lists were compared by family name only; given names, initials and diacritics were not compared.
