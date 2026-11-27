# Sign-off package for the resubmission

Everything a co-author needs in order to approve the revised Perspective, plus the list of what still stands between it and submission. Prepared on 27 November 2026. Nothing here has been sent to anyone.

## What to send

| File | For whom | What it is |
| --- | --- | --- |
| [`summary-of-changes.md`](summary-of-changes.md) ([.docx](summary-of-changes.docx), [.pdf](summary-of-changes.pdf)) | everyone | One page: what changed since the decision letter of 9 January 2025 |
| [`per-author-checklist.md`](per-author-checklist.md) ([.docx](per-author-checklist.docx), [.pdf](per-author-checklist.pdf)) | everyone, each reading their own section | Each author's contribution as worded in the manuscript, the files and public records that back it, and the items they confirm |
| [`review-copies/manuscript-v3.pdf`](review-copies/manuscript-v3.pdf) | everyone | The manuscript as it would be submitted |
| [`review-copies/manuscript-v3-for-review.docx`](review-copies/manuscript-v3-for-review.docx) | anyone who wants to edit | The same text in Word, with line numbers and every sign-off anchor shown inline as **[[ID]]**, so each person can search for their own IDs |
| [`review-copies/esi.pdf`](review-copies/esi.pdf) | project teams | Supplementary information: Note S1 has each project as contributed, and Note S3 has the evidence for each team's Table 5 row |
| [`review-copies/response-to-decision-letter.pdf`](review-copies/response-to-decision-letter.pdf), [`review-copies/cover-letter.pdf`](review-copies/cover-letter.pdf) | senior authors | The point-by-point response and the cover letter |
| [`messages.md`](messages.md) | Sterling | Draft notes to each team, ready to paste, each with that team's specific asks |

The markdown files one level up are the source of truth. The Word and PDF copies are generated from them by [`../tools/build_review_copies.py`](../tools/build_review_copies.py) and should be regenerated after any edit.

## How people sign off

Reply to the e-mail or on [PR #193](https://github.com/vertical-cloud-lab/byu-vcl/pull/193) with "confirmed", or a correction, for each ID in your section. Corrections to the text are welcome as tracked changes in the Word review copy. Please do not soften Table 5. If a team cannot accept its row, it can ask for the row to be removed, and the caption will say so.

Silence is not consent: RSC requires the corresponding author to attest that every author agreed to the submission.

## Who still has to do what

State on 27 November 2026. No co-author has confirmed anything yet: no reply has reached the PR thread or the repository since the v3 package went up on 10 October.

### Blocking: it cannot be submitted without these

| # | What | Who | ID |
| --- | --- | --- | --- |
| 1 | A public work-in-progress repository for **P3, the rolling ball viscometer**: CAD, BOM, code as it stands, licence, and a README saying "pre-release". Otherwise P3 comes out of the paper; the replacement text and numbers are drafted in [`../revision-notes-v3.md`](../revision-notes-v3.md) §5(b) | DTU team: Louie Lucas Bisgaard Nyeland, Jin Hyun Chang, Kshitij Gambhir, Rógvi Ziskason; escalation Tejs Vegge. Dropping P3 is Sterling's and Tejs's decision | TV-1 |
| 2 | Confirmation that `loppe35/PowderDispensing_and_Weighing_Module` is **P1** | DTU team | TV-1 |
| 3 | Confirmation that the two forks are **P7**'s files, ideally consolidated into one repository | Yang Cao, Ethan Rajkumar; escalation Jason E. Hein | P7-1 |
| 4 | A clean **Figure 8**, exported by the team from its own file without AI tools: no logos, no proofing marks, at least 1960 px wide | P7 team | P7-2 |
| 5 | The **survey ethics statement** for §2: the committee and its number, or a plain statement of how responses were collected | Brenden Pelkie, Lilo D. Pozzo | BP-3, LDP-1 |
| 6 | Consent to each team's **Table 5 row** and to the **§6 deposit commitment** | every project team | TV-4/6, OM-3/5, TB-3/4, BP-8/9, P7-4/5, SGB-10/11, JEH-2/3 |
| 7 | **Authorship**: Seth Leavitt's consent; whether Basita Das and Ilya Yakavets are added | Seth Leavitt; Tonio Buonassisi with Basita Das; the P7 team with Ilya Yakavets; Sterling | SL-1, TB-2, P7-3, SGB-5 |
| 8 | **Approval from all 28 authors**, with affiliation, CRediT role, conflicts, funding and ORCID | everyone | ALL-1 to ALL-7 |
| 9 | At submission: merge PR #193, tag the commit and put the tag in the Data availability statement; fill the ScholarOne fields | Sterling | SGB-4, SGB-12 |

### Needed for the text as written, but not blocking on their own

- Brenden Pelkie: the selection criterion (BP-1), the survey instrument and responses (BP-2; a fallback sentence is ready), whether the ChemRxiv text is what the editor read (BP-4), the "manifesto" (BP-5, with Lilo D. Pozzo).
- Nadya Peek: the keynote paraphrase (NP-1); Sonya Vasquez's affiliation (NP-2).
- Funding lines: Sterling for the AC and BYU authors (SGB-6), Tonio Buonassisi (TB-5), Brenden Pelkie and Nadya Peek for UW (BP-10, NP-3).
- Sterling: the AI statement (SGB-3), the author order (SGB-2), and whether the two co-organizers are content to be thanked (SGB-14).

### Fixes the teams could make that would improve the paper

None of these blocks submission. Each one fixed before submission is recorded in ESI Note S3, and §6 keeps its past tense ("we found").

- **P1 (DTU):** the merge-conflict markers in 11 firmware files, the empty folders in the Zenodo deposit, the 16 wrong file names in the build guide, and the inconsistent licences.
- **P2 (Melville):** a licence; the README's function names.
- **P4 (DTU):** a licence file.
- **P6 (Pelkie):** a release with the Zenodo integration.
- **P8 (Baird, Hattrick):** move the parts list into the repository, credit the CC BY 4.0 Digital Pipette, and tag a release.
- **P9 (Baird, Aspuru-Takata):** the microscope-side code; a running public interface.
- **P10 (Hein):** archive later releases; align the deposit's licence with the repository's.

### At revision, after review (nothing needed now)

- Figures as separate TIFF files at 600 dpi or more. Figure 4 (DTU original photograph) and Figure 8 (clean export) need new files; Figure 1 can be re-rendered from the script, and Figure 9 taken from the TIFF in `figures/source/`. Figure 7's Documentation panel shows a YouTube player logo, which the journal discourages.
- A table-of-contents graphic drawn by a co-author (SGB-15).
- The response to the referees.
- At acceptance: the Zenodo DOIs for the analysis code (SGB-4) and the archival deposits the teams committed to in §6.

## Suggested timeline

Nothing outside the authors' control sets the date: the AI4X collection has closed, and a regular Perspective has no deadline. The people listed above set it, and so do the December holidays at all seven institutions.

| When | Step |
| --- | --- |
| Mon 30 Nov 2026 | Send the package, using the drafts in [`messages.md`](messages.md), with replies due **Mon 14 Dec**. Send the two blocking asks first: DTU (P3 repository) and P7 (file confirmation and a clean Figure 8). |
| Mon 7 Dec | Nudge the DTU and P7 teams if their items have not arrived. |
| Mon 14 – Thu 17 Dec | Fold in corrections; rebuild the review copies; circulate the final PDF for explicit approval. |
| **Fri 18 Dec (best case)** | Submit, if every blocking item and all 28 approvals are in. |
| Mon 4 – Fri 8 Jan 2027 | Chase the remaining approvals. **Fri 8 Jan: decide on P3.** If its repository has not appeared, drop it, using the text and numbers in [`../revision-notes-v3.md`](../revision-notes-v3.md) §5(b). |
| **Fri 15 Jan 2027 (realistic)** | Submit with P3. Without P3, allow one more week to re-run the analysis and recirculate: **Fri 22 Jan**. |

The APC is £2,200 for 2026 submissions, and no 2027 price has been published. If the price follows the submission date, December is slightly cheaper. That is an inference, and not a reason to rush the approvals.
