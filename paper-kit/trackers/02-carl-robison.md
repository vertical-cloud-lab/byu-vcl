<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/[REPO]    Assignee: carl-robison
-->

**Presenter:** Carl Robison (GitHub `carl-robison`)
**TMS 2027 abstract:** [An ICME Loop for Composition-Aware LPBF Parameter Qualification: CALPHAD-Predicted Printability, Bayesian Optimization, and Cross-Section Feedback to the Thermo-Calc AM Module](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/30908CDE388B906E85258E34004DF864?OpenDocument)
**Slot:** Talk, Mon Mar 15, 4:05 PM, San Antonio. Artificial Intelligence Applications in Integrated Computational Materials Engineering (AI-ICME); session "AI-ICME-2: AI-Guided Alloy, Process & Generative Materials Design".
**Authors on the abstract:** Carl Robison, Ronnie Guymon, Xavier Zaitzeff, Gage Erickson (BYU); Alik Nielsen, Ashley Spear (University of Utah); Sterling G. Baird (BYU); Paul Mason, Adam Hope (Thermo-Calc Software).
**Where the work is:** No abstract or plan found in the repositories this search could read (the alloy work is likely in `digital-alloy-lab-private`, which it could not). Related public work: LPBF printer quotes and parameter openness (byu-vcl #61, PR #62), the Utah Aconity print (#77).
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). No target journal found in the readable repositories.
**Results freeze (G2):** [DATE]
**Data that exist now:** None found in readable repositories.

**To decide at G1:**
- Four co-authors are outside BYU, two of them at a company: start the sign-off checklist at G1, and ask the Thermo-Calc authors whether their employer must clear the manuscript, and how long that takes.
- ProgramMaster lists the affiliation as "Brigham young University"; fix it in the TMS system if it can still be edited.

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
