# Point-by-point check against the referee reports

DD-ART-06-2026-000353, first-round reports (copied in AC-BO issue 170). Each referee point is
mapped to what the revision does, where (pages refer to
[`manuscript/BO_Hackathon_Manuscript_Revised.pdf`](manuscript/BO_Hackathon_Manuscript_Revised.pdf),
26 pages), and whether it is finished. Every page below was read off the compiled PDF,
not the LaTeX source, and the response letter's pointers were checked against the same build.

Status: **done**; **partly** (answered, but a referee could reasonably ask for more);
**open** (needs a person; owner named).

## Referee 1

| Point | What the revision does | Where | Status |
| --- | --- | --- | --- |
| Organizational lessons: what worked, what did not, what to change | Section V.A, four paragraphs, grounded partly in the recorded interview; six changes for future events | V.A, pp. 19 to 20 | done |
| Scientific lessons: pros and cons of BO across projects (representation, kernels, warm start, noise, dimensionality, batch size, acquisition optimization, overhead, reproducibility) | Section V.B: strengths, now tied to the projects that showed them (inputs 8, 21, 27; multi-objective 1, 18, 37; multi-fidelity 2; contextual 26; batched 15; cost-aware 36; preference 16), then limitations. This revision adds batch size (15), overhead (37) and the noise test (23) | V.B, p. 20 | done |
| Future opportunities (autonomous labs, multi-fidelity, uncertainty-aware planning, foundation models, preference BO, multi-objective, noise-robust BO, benchmarks, domain tools) | Section VII covers every listed direction, plus the LLM note the referee's list prompted | VII, p. 21 | done |
| Systematic evaluation: categories; code availability, licensing, documentation, reproducibility, dependencies, maintenance | Table IV (categories), Table V (licenses, now rechecked: 19 MIT, 5 inaccessible), ESI Table S1 (per-project categories), **new ESI Table S2** (per-project README, dependency files, last push). Reproducibility and maintenance plans are not assessed beyond these proxies | IV, pp. 18 to 19; ESI | partly (reproducibility not tested) |
| Overall: synthesis, limitations, future directions | Sections IV to VII; the abstract now says so too | pp. 18 to 21 | done |

## Referee 2

| Point | What the revision does | Where | Status |
| --- | --- | --- | --- |
| Meta-analysis: commonalities and differences between teams | Last paragraph of Section IV | p. 19 | done |
| Does prior expertise affect outcomes? | Not measured. The text used to say mixed teams "appeared to be an asset"; it now cites other hackathons for that and says it was not measured here, matching the reply | p. 19 | done (as a stated limitation) |
| Follow-up studies, ultimate gain | Section VI: continuation trail for about 19 projects, cohort statistics recounted for the 124 current co-authors, career moves; now with numbered references | VI, p. 20 | done |
| Reflective component, lessons learned | Section V | pp. 19 to 20 | done |

## Referee 3

| Point | What the revision does | Where | Status |
| --- | --- | --- | --- |
| Listing ends abruptly | Sections IV to VII now follow the project listing | pp. 18 to 21 | done |
| 1. Frameworks for noisy vs less noisy data | One narrow observation, now stated in the text and the reply: in project 23 a noise-aware GP beat a fixed-noise one in 15 of 16 settings | V.B, p. 20 | done (narrow by necessity) |
| 2. Deployability in experimental settings | End of V.B (wet-lab caveat) and VII (GUI and web tools) | pp. 20, 21 | done |
| 3. Where BO helped and where it did not | V.B examples: helped (first paragraph, by project), little gain over random search (33 and 23; project 1 had been misread), acquisition effort (3); no generalization without a survey, which is committed for future events | pp. 20, 20 | done |

## Referee 4 (data review)

| Point | What the revision does | Where | Status |
| --- | --- | --- | --- |
| 1. Projects 14, 19, 23, 29, 34, 42 missing | All 45 summarized. Project 43 also had no video, so Section III now says seven, and all seven summaries carry the note it promises (19, 29, 42 and 43 did not) | III, pp. 8 to 18 | done |
| 1a. More on winners 23 and 34 | Full summaries noting the awards | pp. 13, 16 | done |
| 2. Missing module requirements | Aggregate in Section IV; per-repository dependency files now in ESI Table S2 (23 of 36 public repositories declare dependencies) | p. 19; ESI | done |
| 3. Datasets unclear (6, 15, 19 to 21, 29, 30, 31, 36, 37, 40, 42, 45) | **Was not in the 8 Oct set.** Ported from the unmerged AC-BO issue 176 branch: each summary names its data source or says none was used; data-provenance paragraph in Section IV | III and IV, p. 19 | done |
| 4. Judging rubric in the SI | No numeric rubric existed; Gavel's pairwise question is stated, now with citations for Gavel and the Crowd-BT model it uses | II, fifth paragraph, p. 3 | done |
| 5. Summarization workflow not reproducible; "objective" claim | Model, temperature and generation date (January 2025) stated; raw and edited summaries archived; claim withdrawn. **The prompt is not archived**, and the journal's LLM policy asks for input and output logs | III, p. 8 | partly: prompt needed from Mehrad Ansari |
| 6. Figure 2 label contrast | White outline on the labels | Fig. 2, p. 5 | done |
| 7. Table 1 empty second page | Table III breaks with entries on both pages | pp. 7 to 8 | done |
| 9. Figure 3 caption preprint policy | Caption states the reason for blurring | Fig. 3, p. 5 | done |
| 11. Table 2 footnote marker | Folded into the caption (now Table I) | p. 4 | done |
| 13. Consent for names in Figs 4 and 5 | The reply now answers the question: participants were not asked in advance, so names are pixelated (deterministic pixelation, no generative editing); the names left legible in Fig. 4 are co-authors' | p. 6 | done (Sterling to confirm the wording) |
| Minor 11. Opaque title hyperlinks | Headings are plain text; links stay in Table III, and **new ESI Table S3** prints the full URL behind every icon there. The Section VI paper links are now numbered references | III; VI, p. 20; ESI | done |
| Minor 13a/b. Project 40, 33 and 34 links | Fixed on the project pages and in Table III. This revision also fixes project 15, which Table III linked to project 13's repository | Table III, pp. 7 to 8 | done |
| Minor 13. Ligature-mangled names | PDF now carries glyph-to-Unicode maps and, since this round, T1 fonts, so accented letters are single glyphs (checked by extracting the text: Griffiths, Jeffrey, Özkan, Šošić, Lála all come out right). **The separate author contributions PDF has the same problem and has to be regenerated** | Acknowledgements, p. 21 | open: Gage |
| Checklist 1a. All data listed? | See point 3 | | done |
| Checklist 2a and 6a. Survey workflow and code | Scripts, raw AI outputs and agent logs listed in Data availability; Zenodo snapshot promised on acceptance | p. 21 | done (snapshot due at acceptance) |
