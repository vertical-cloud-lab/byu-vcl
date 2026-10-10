<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/tensegrity-optimization    Assignee: ctrhjk
-->

**Presenter:** Jinkwan Han (GitHub `ctrhjk`)
**TMS 2027 abstract:** [Closed-Loop Bayesian Optimization of Multi-Material 3D-Printed Tensegrity Crutch-Tip Impact Absorbers](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/4190282C54D62AD685258E270070DE50?OpenDocument)
**Slot:** Talk, Mon Mar 15, 10:50 AM, Crystal Ballroom A. Biomedical Materials and Devices: From Laboratory to Market; session "Monday AM".
**Authors on the abstract:** Jinkwan Han, Marcus Madsen, Audrey Christiansen, Sterling G. Baird, Jeffrey Hill (BYU).
**Where the work is:** [tensegrity-optimization](https://github.com/vertical-cloud-lab/tensegrity-optimization): the abstract ([PR #18](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/18)), the drop-tower protocol ([#115](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/115)), simulations on branch `copilot/explore-simulations-for-tensegrity`.
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). No target journal found. The Journal of Mechanical Design manuscript moved the crutch tip to future work, so this one needs its own venue (a biomedical-device or rehabilitation-engineering journal would match the symposium).
**Results freeze (G2):** [DATE]
**Data that exist now:** No experimental data yet: simulation outputs (`simulations/outputs/*crutch*.csv`) and literature results only.

**To decide at G1:**
- What experiment produces the paper's data by G2: the drop-tower protocol (#115) on crutch-tip prototypes?
- A device for people may need different statements (ethics, intended use); check the chosen journal at G1.

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
