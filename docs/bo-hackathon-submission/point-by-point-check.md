# Point-by-point check against the referee reports

DD-ART-06-2026-000353, first-round reports (copied in AC-BO issue 170). Each referee point is
mapped to what the revision does, where (pages refer to
[`manuscript/BO_Hackathon_Manuscript_Revised.pdf`](manuscript/BO_Hackathon_Manuscript_Revised.pdf),
27 pages), and whether it is finished. Every page below was read off the compiled PDF,
not the LaTeX source, and the response letter's pointers were checked against the same build.

Status: **done**; **partly** (answered, but a referee could reasonably ask for more);
**open** (needs a person; owner named).

## Referee 1

| Point | What the revision does | Where | Status |
| --- | --- | --- | --- |
| Organizational lessons: what worked, what did not, what to change | Section V.A, four paragraphs, grounded partly in the recorded interview; six changes for future events | V.A, pp. 20 to 21 | done |
| Scientific lessons: pros and cons of BO across projects (representation, kernels, warm start, noise, dimensionality, batch size, acquisition optimization, overhead, reproducibility) | Section V.B: strengths, then limitations. This revision adds batch size (project 15) and computational overhead (project 37), the two items on the referee's list that were missing | V.B, p. 21 | done |
| Future opportunities (autonomous labs, multi-fidelity, uncertainty-aware planning, foundation models, preference BO, multi-objective, noise-robust BO, benchmarks, domain tools) | Section VII covers every listed direction, plus the LLM note the referee's list prompted | VII, p. 22 | done |
| Systematic evaluation: categories; code availability, licensing, documentation, reproducibility, dependencies, maintenance | Table IV (categories), Table V (licenses, now rechecked: 19 MIT, 5 inaccessible), ESI Table S1 (per-project categories), **new ESI Table S2** (per-project README, dependency files, last push). Reproducibility and maintenance plans are not assessed beyond these proxies | IV, pp. 19 to 20; ESI | partly (reproducibility not tested) |
| Overall: synthesis, limitations, future directions | Sections IV to VII; the abstract now says so too | pp. 19 to 22 | done |

## Referee 2

| Point | What the revision does | Where | Status |
| --- | --- | --- | --- |
| Meta-analysis: commonalities and differences between teams | Last paragraph of Section IV | p. 20 | done |
| Does prior expertise affect outcomes? | Not measured; the mix of backgrounds is described and the response says so | p. 20 | done (as a stated limitation) |
| Follow-up studies, ultimate gain | Section VI: continuation trail for about 19 projects, cohort statistics recounted for the 124 current co-authors, career moves; now with numbered references | VI, p. 21 | done |
| Reflective component, lessons learned | Section V | pp. 20 to 21 | done |

## Referee 3

| Point | What the revision does | Where | Status |
| --- | --- | --- | --- |
| Listing ends abruptly | Sections IV to VII now follow the project listing | pp. 19 to 22 | done |
| 1. Frameworks for noisy vs less noisy data | One narrow, project-anchored observation (noise-robust methods) | V.B, p. 21 | partly (the projects cannot support more) |
| 2. Deployability in experimental settings | End of V.B (wet-lab caveat) and VII (GUI and web tools) | pp. 21, 22 | done |
| 3. Where BO helped and where it did not | V.B examples (projects 1, 33, 3), no generalization without a survey; survey committed for future events | pp. 21, 21 | done |

## Referee 4 (data review)

| Point | What the revision does | Where | Status |
| --- | --- | --- | --- |
| 1. Projects 14, 19, 23, 29, 34, 42 missing | All 45 summarized; the six without a video are written from pages and artifacts and say so | III, pp. 9 to 9 | done |
| 1a. More on winners 23 and 34 | Full summaries noting the awards | pp. 14, 17 | done |
| 2. Missing module requirements | Aggregate in Section IV; per-repository dependency files now in ESI Table S2 (23 of 36 public repositories declare dependencies) | p. 20; ESI | done |
| 3. Datasets unclear (6, 15, 19 to 21, 29, 30, 31, 36, 37, 40, 42, 45) | **Was not in the 8 Oct set.** Ported from the unmerged AC-BO issue 176 branch: each summary names its data source or says none was used; data-provenance paragraph in Section IV | III and IV, p. 20 | done |
| 4. Judging rubric in the SI | No numeric rubric existed; Gavel's pairwise question is stated, now with citations for Gavel and the Crowd-BT model it uses | II, fifth paragraph, p. 3 | done |
| 5. Summarization workflow not reproducible; "objective" claim | Model, temperature and generation date (January 2025) stated; raw and edited summaries archived; claim withdrawn. **The prompt is not archived**, and the journal's LLM policy asks for input and output logs | III, p. 9 | partly: prompt needed from Mehrad Ansari |
| 6. Figure 2 label contrast | White outline on the labels | Fig. 2, p. 6 | done |
| 7. Table 1 empty second page | Table III breaks with entries on both pages | pp. 8 to 9 | done |
| 9. Figure 3 caption preprint policy | Caption states the reason for blurring | Fig. 3, p. 6 | done |
| 11. Table 2 footnote marker | Folded into the caption (now Table I) | p. 5 | done |
| 13. Consent for names in Figs 4 and 5 | Display names pixelated, captions say so (deterministic pixelation, no generative editing) | p. 7 | done |
| Minor 11. Opaque title hyperlinks | Headings are plain text; links stay in Table III. This revision also turns the Section VI paper links into numbered references | III; VI, p. 21 | done |
| Minor 13a/b. Project 40, 33 and 34 links | Fixed on the project pages and in Table III. This revision also fixes project 15, which Table III linked to project 13's repository | Table III, pp. 8 to 9 | done |
| Minor 13. Ligature-mangled names | PDF now carries glyph-to-Unicode maps (checked: the names extract correctly). **The separate author contributions PDF has the same problem and has to be regenerated** | Acknowledgements, p. 22 | open: Gage |
| Checklist 1a. All data listed? | See point 3 | | done |
| Checklist 2a and 6a. Survey workflow and code | Scripts, raw AI outputs and agent logs listed in Data availability; Zenodo snapshot promised on acceptance | p. 22 | done (snapshot due at acceptance) |
