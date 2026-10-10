<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to ASME Journal of Mechanical Design: tracker
Open in: vertical-cloud-lab/tensegrity-optimization    Assignee: me-madsen
-->

**Presenter:** Marcus Madsen (GitHub `me-madsen`)
**TMS 2027 abstract:** [Closed-Loop Bayesian Optimization of Multi-Material 3D-Printed Tensegrity-Inspired Energy Absorbers](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/E59DA70A00DDE30685258E350063E8D5?OpenDocument)
**Slot:** Talk, Tue Mar 16, 4:45 PM, Washington. AI-Enabled Materials Processing; session "Robotic Experimentation and Uncertainty-Aware Design".
**Authors on the abstract:** Marcus Madsen, Audrey Christiansen, Jinkwan Han, Jeffrey Hill, Sterling G. Baird (BYU).
**Where the work is:** [tensegrity-optimization](https://github.com/vertical-cloud-lab/tensegrity-optimization): the manuscript ([PR #76](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/76), [#75](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/75)), the abstract ([PR #73](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/73)), and the latest review edits (PR #116).
**Target journal:** ASME Journal of Mechanical Design (`make pdf J=asme`). From the repo: the manuscript in [PR #76](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/76) targets the ASME Journal of Mechanical Design (backup in its README: Smart Materials and Structures).
**Results freeze (G2):** [DATE]
**Data that exist now:** `manuscript/data/*.csv` (PR #116's branch): drop results, predictions and print keys for rounds 1 to 4, round-3 repeatability, round-5 leave-one-group-out CV, and the front's evolution, snapshotted with provenance.

**To decide at G1:**
- **ASME's AI rule.** ASME "prohibits the use of generative AI in the creation of content for journal submissions" and allows AI only to edit text the authors wrote. The PR #76 manuscript was drafted largely by AI agents, so before G5 its text must be the authors' own, or the paper goes to a journal whose policy fits (boilerplate/generative-ai.md).
- Author order and the equal-contribution marks (three students listed as equal first authors in the draft).

### Gates

- [ ] **G1 Outline, Fri Oct 23, 2026.** Journal chosen, with its preprint policy and licence checked ([checklist](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/preprint-and-license.md)); title; authors and order agreed; the claim in one sentence; the figure list (`figN_slug`: what it shows, which data file); a section outline in `paper/manuscript/`.
- [ ] **G2 Results freeze, [DATE].** Every figure is a script reading only `data/`; every data file has its README (units, n, provenance); `make figures check colorblind` is clean ([colour-blind check](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/colorblind.md)); every caption states n and its error bars. New data after this only by agreement, as a new snapshot noted here.
- [ ] **G3 Draft to co-authors, Fri Jan 29, 2027.** The whole draft, references with DOIs; `make credit pdf`; `git tag g3`; sent to every co-author with the commit hash; sign-off round 1 ([checklist](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/coauthor-signoff.md)).
- [ ] **G4 My review, [DATE, between Jan 29 and Feb 26].** First, `make rebuild-check` passes and a fresh clone builds ([clean rebuild](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/clean-rebuild.md)); then the `make todos` PDF and `make diff REV=g3` to me.
- [ ] **G5 Preprint and submission, Fri Feb 26, 2027.** Every author has approved this version (sign-off round 2); `make submission-check` passes; the Zenodo DOI is reserved and in the text; the AI paragraph sits where this publisher wants it ([generative AI](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/boilerplate/generative-ai.md)); preprint posted under [LICENCE], and the paper submitted.
- [ ] **G6 Slides, Fri Mar 5, 2027.** Made from the paper's figures (`vs.use("slide")`): one message per slide, nothing under 24 pt; about 20 minutes with questions.
- [ ] **G7 Practice talk, [DATE, before TMS opens on Sun Mar 14].** Given to the group; feedback addressed.

### Thursday update (copy into a comment every Thursday)

```
Figure: [one figure: figures/out/figN_slug.png at commit abc1234, or the image]
Numbers: [the numbers behind it: n, value ± error, data/<file>]
Next week: [one thing]
Blocker: [one blocker, or none]
```
