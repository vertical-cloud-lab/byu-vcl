# BO Hackathon manuscript: Digital Discovery revision (DD-ART-06-2026-000353)

Prepared 27 November 2026 for [issue 185](https://github.com/vertical-cloud-lab/byu-vcl/issues/185).
This folder holds the complete revised upload set, built from
[AC-BO-Hackathon PR 171](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/pull/171)
at `8321260` plus the patches in [`patches/`](patches/). It replaces the 8 October set
(branch `claude/issue-185-20261008-2005`).

## Where it stands

**The revision has not been submitted**, as far as anything outside the portal shows:

- Gage had not submitted it as of 8 October
  ([PR 171](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/pull/171#issuecomment-6049867211)),
  and Sterling said on 13 October that he would take over the final submission. Nothing on
  PR 171, its branches, this issue or the hackathon repository has changed since.
- Crossref has no Digital Discovery record for the paper, and the ChemRxiv preprint
  (10.26434/chemrxiv-2025-dzh5z) is still version 1 with 125 authors.
- The editor's own decision letter, with the revision deadline, is not in any repository; only
  the four referee reports are (AC-BO issue 170). Gage could still see the revision's file list
  in the portal on 8 October. Whether the deadline has passed can only be checked in ScholarOne.

## Upload set

Every file below is in this folder. "Replaces" refers to the six files of the original
submission as listed in the portal on 8 October (screenshot in issue 185).

| File | Portal designation | Replaces | Notes |
| --- | --- | --- | --- |
| [`cover-letter/cover-letter.docx`](cover-letter/cover-letter.docx) ([PDF](cover-letter/cover-letter.pdf)) | Cover letter field, or a file | Letter_to_Referees_BYU_letterhead_signed_fullpage.docx | **Draft.** Put it on letterhead, fill in the editor's name and the date, sign. Declares the AI use and the authorship change, as RSC requires. |
| [`response/Response_to_Referees.pdf`](response/Response_to_Referees.pdf) | Response to Referees | (new for the revision) | Every page pointer checked against the PDF below. Also paste or attach in the "Response to Decision Letter" step. |
| [`manuscript/BO_Hackathon_Manuscript_Revised.pdf`](manuscript/BO_Hackathon_Manuscript_Revised.pdf) | Main Article | BO_Hackathon_Manuscript_Final.pdf | 27 pages, 0 unresolved references or citations. |
| [`manuscript/BO_Hackathon_Manuscript_Revised_marked_changes.pdf`](manuscript/BO_Hackathon_Manuscript_Revised_marked_changes.pdf) | Revised manuscript with changes marked | (new) | latexdiff against the submitted source (`6d2c616`). |
| [`manuscript/BO_Hackathon_Manuscript_Revised_LaTeX_source.zip`](manuscript/BO_Hackathon_Manuscript_Revised_LaTeX_source.zip) | LaTeX source files | (new) | Compiles without shell-escape: tested by unzipping into an empty folder. Needs TeX Live 2023 (see below). |
| [`figures/Fig1.tif`](figures/) to `Fig5.tif` | Figure | (new) | TIFF at 600 dpi or more at print width (8.3 cm for Fig. 1, 17.1 cm for the rest), transparency flattened onto white. Figs. 3 to 5 were upsampled to reach 600 dpi; Fig. 5's source screenshot is only 1660 px wide. |
| Original ESI + [`esi/ESI_Tables_S1_S2_addendum.pdf`](esi/ESI_Tables_S1_S2_addendum.pdf) | Supplementary Information | ESI_AC-BO-Hackathon-2024-All-Projects.pdf | **Merge needed**: the original ESI is not in any repository. `pdfunite ESI_AC-BO-Hackathon-2024-All-Projects.pdf ESI_Tables_S1_S2_addendum.pdf ESI_revised.pdf`. If the original already has a Table S1, renumber. |
| [`toc/TOC_entry.tif`](toc/TOC_entry.tif) + [`toc/TOC_entry.docx`](toc/TOC_entry.docx) | Table of Contents Entry | TOC_entry.pdf | 8.0 x 2.7 cm at 600 dpi (the journal's maximum is 8 x 4 cm). The 202-character text is a draft; keep the June text if you prefer it (250 characters maximum). |
| [`das/Data_Availability_Statement.docx`](das/Data_Availability_Statement.docx) | Data Availability Statement | Data_Availability_Statement.docx | The statement changed, so the old file is out of date. Same text as the manuscript. |
| Author contributions (CRediT) without Jiale Shi and Dandan Tang | Other | Author_Contributions_CRediT.pdf | **Not built**: its source is in no repository. See blockers. |

## What changed since the 8 October set

The 8 October set was `8321260` as it stood. These changes are in [`patches/`](patches/)
(apply on PR 171 with `git am --keep-cr`; `--keep-cr` because `process_spreadsheet.py` has
CRLF line endings), and every PDF above was rebuilt from them.

1. **Referee 4, point 3 (datasets).** The fix written for AC-BO issue 176 (`0258d7a`) sat on an
   unmerged branch, so the 8 October set still had the stopgap reply, which pointed to a
   "future work section" that does not say what the reply claimed. Ported: thirteen summaries
   name their data source, Section IV gains a data-provenance paragraph, and the reply now
   points to them.
2. **RSC's AI policy.** RSC requires generative-AI use to be declared in the cover letter and,
   with model names, in the Acknowledgements when there is no methods section
   ([author responsibilities](https://web.archive.org/web/20261013084246/https://www.rsc.org/publishing/journals/processes-and-policies/author-responsibilities)).
   Nothing declared it, although Claude and Copilot drafted much of the revision, Edison
   proposed the Table IV classification and Claude compiled the Section VI cohort review.
   Drafted in both places for Sterling to check.
3. **Numbers that changed with the author list.** Section VI said "126 paper co-authors";
   recounted for the 124 current authors from the same evidence file: 73 students, 94 with a
   visible output, 56 of the students (percentages unchanged: 59, 76, 77). Nine faculty moves
   became eight (Toledo was Jiale Shi's).
4. **References** (Crossref check, [`reference-check.md`](reference-check.md)). Three DOIs were wrong (Szymanski 2023 resolved to a paper on the yeast interactome; Aldeghi 2022 and Graff 2021 did not resolve), seven author lists were wrong, four preprints have since been published, 27 DOIs were missing, five works printed twice under two keys, and two sentences cited *Sustainable concrete via Bayesian optimization* for acquisition optimization where Ament et al.'s *Unexpected improvements to expected improvement* was meant. All fixed.
5. **Table III and Table V.** Table III linked project 15 to project 13's repository; links now
   come from the project pages. Project 22's repository was deleted after July, so Table V is
   now 19 MIT and 5 inaccessible, checked 27 November.
6. **ESI Table S2 (new):** license, README, dependency files and last push for every
   project's repository. This is the documentation, dependency and maintenance part of
   Referee 1's request that was still open, and it backs Referee 4's point 2.
7. **Presentation:** Data availability now sits after Conflicts of interest with full URLs
   (RSC's rule); the follow-up papers in Section VI are numbered references instead of opaque
   links (Referee 4, minor 11); Gavel and the Crowd-BT model it implements are cited; the
   summaries' generation date is given (January 2025); the abstract mentions the synthesis;
   accented names (Özkan, Šošić, Lála) now extract correctly, which the ligature fix alone had
   not done; Scientific lessons covers batch size and overhead, the two items on Referee 1's
   list it had skipped.

The full mapping from each referee point to the revision is in
[`point-by-point-check.md`](point-by-point-check.md).

## What Sterling or Gage has to do

In this order:

1. **Check the revision is still open (Sterling).** In ScholarOne (Digital Discovery Author
   Center), find DD-ART-06-2026-000353 under "Revised Manuscripts in Draft" or "Manuscripts
   with Decisions" and read the due date. Gage submitted the original, so the draft may be in
   **his** Author Center: either he submits, or the editorial office moves it to Sterling. If
   the deadline has passed, ask DigitalDiscovery-rsc@rsc.org to reopen it.
2. **Authorship change (Sterling).** Send the e-mail in
   [`authorship-change-email.md`](authorship-change-email.md) with the two authors' requests
   attached, before uploading. RSC requires every author, including those removed, to agree,
   and the office may send a form.
3. **CRediT statement (Gage).** Regenerate `Author_Contributions_CRediT.pdf` without Jiale Shi
   and Dandan Tang. Referee 4 reported mangled names in this file too ("Gri ths", "LÆla"), and
   the response letter now says it was regenerated, so export with embedded fonts and check
   that copying "Griffiths", "Özkan", "Šošić" and "Lála" out of the PDF works.
4. **Read and approve the AI statement (Sterling)** in the Acknowledgements and the cover
   letter. Confirm: the models (Claude Opus 5 and Fable 5 per the AC-BO workflow file, Claude
   Opus 5.5 for this round, the Copilot coding agent, Edison), whether anyone checked the
   Table IV assignments by hand (if
   so, add "and checked by the authors" to the Section IV and ESI wording), and what the
   ChatGPT share link in the abstract's source comment was for (the link is dead; if ChatGPT
   wrote text, add it to the statement).
5. **Apply the patches to PR 171 (Sterling)**, so the repository matches what is uploaded:
   `git am --keep-cr docs/bo-hackathon-submission/patches/*.patch` on
   `copilot/address-dd-reviewer-feedback` (tested: the 16 patches apply cleanly to `8321260`),
   or ask `@claude` on PR 171 to do it.
6. **Fix the participant spreadsheet before reviewers follow the new link (Sterling).**
   `AC-bo-hackathon-2024.csv` in the public AC-BO repository holds 131 participants' e-mail
   addresses and postal addresses, and the Data availability statement now sends reviewers
   to that repository. Table III only needs the project and link columns. Dropping the e-mail
   and address columns takes minutes; whether to purge them from the history is a separate
   call.
7. **Merge the ESI (Gage or Sterling):** original ESI followed by the S1/S2 addendum.
8. **Cover letter (Sterling):** letterhead, editor's name, date, signature. Do not mention the
   invitation in the letter; RSC wants that in the submission form only.
9. **Upload** the files in the table above, update the abstract in the form (it changed), remove
   the two authors in the author step if the system allows it, check ScholarOne's built PDF,
   and submit.

## Still open, with owners

| Item | Owner | Blocks submission? |
| --- | --- | --- |
| Revision still open in ScholarOne, and whose account holds it | Sterling (Gage if the draft is his) | yes |
| Editorial approval of the authorship change | Sterling; Jiale Shi and Dandan Tang may have to confirm | yes |
| New CRediT statement | Gage | yes |
| Approve the AI statement; ChatGPT link; who checked Table IV | Sterling | yes |
| Participant e-mails and addresses in the public CSV | Sterling | should be done first |
| Merge the original ESI with Tables S1 and S2 | Gage or Sterling | yes |
| The summarization prompt (and transcripts if kept), to archive with the raw outputs. The journal's LLM policy asks for input and output logs, and Referee 4 raised reproducibility. Without it, say in the letter that the prompt was not retained | Mehrad Ansari | no, but the data reviewer may come back on it |
| Fig. 1 is a DoE vs BO plot credited to ref. 1 (Baird and Sparks, STAR Protocols 2023, CC BY 4.0). If it is taken from that paper, add "Adapted from ref. 1 (CC BY 4.0)" to the caption | Sterling | no, but production will ask |
| Project 22: Jiale Shi deleted the repository and withdrew; decide whether its summary and Table III row stay as they are | Sterling | no |
| Zenodo snapshot of the AC-BO repository, DOI into Data availability | Sterling, at acceptance | no (journal requires it at acceptance) |
| Competing interests: authors employed by Merck KGaA, which develops BayBE (discussed in the paper). The submission declared none; RSC may ask | Sterling | no |

## Realistic submission date

**Friday 4 December 2026**, if ScholarOne still has the revision open and the editorial office
approves the authorship change by e-mail. That leaves Monday to Wednesday for Gage's CRediT
statement and the ESI merge and for Sterling to approve the AI statement and send the
authorship e-mail, and Thursday to upload. If the deadline has lapsed and has to be reopened,
add the office's turnaround: about **11 December**. If the office wants a signed form from all
124 authors, expect January 2027, since RSC's offices slow down over the holidays.

## How this was built

- Manuscript, latexdiff and ESI: `texlive/texlive:TL2023-historic` in Docker, the same TeX Live
  generation as every earlier build of this paper. TeX Live 2024 and 2025 cannot build it:
  `revtex4-2` (2022/06/05, still the current release) replaces internals of the `array`
  package that `array` v2.6 rewrote, so every table with array-style columns stops with
  "Extra \or" (checked in both). The zip's README says so; on Overleaf, pick TeX Live 2023.
- `latexmk -f` is still needed for the original 8321260 tree because three `.bib` entries carry
  `language = {en}`; the patches fix the entries, so the build now exits cleanly.
- Source zip: the two shell-escape pipes are replaced with their output; only the files the
  build reads are included, so no participant spreadsheet, no `edison_output/` and no unused
  `latex/authors.tex`. Unzipped into an empty folder and compiled with plain
  `pdflatex`/`bibtex`: same 27 pages and the same text as the manuscript PDF (one word breaks
  differently at a line end).
- Figures: lossless TIFF (Deflate), RGB, white background, resolution tag set to the print width.
- Response letter: `scripts/make_response_letter.sh` (pandoc), as before.
