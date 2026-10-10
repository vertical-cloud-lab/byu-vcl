<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to Additive Manufacturing: tracker
Open in: vertical-cloud-lab/powder-doser    Assignee: williamulbz
-->

**Presenter:** Will Mulberry (GitHub `williamulbz`)
**TMS 2027 abstract:** [Auger-Based Powder Dosing as a Mechanistic Probe of Powder Flow Behavior: Multi-Task Bayesian Calibration and Physics-Based Property Inference](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/B309C32B4F06F84485258E2800150419?OpenDocument)
**Slot:** Talk, Mon Mar 15, 4:40 PM, Magnolia 18. Powder Materials Processing and Fundamental Understanding; session "Modeling for sintering and additive manufacturing".
**Authors on the abstract:** Will Mulberry, Sam Charles, Luke Winters, Sterling G. Baird (BYU Vertical Cloud Lab).
**Where the work is:** [powder-doser](https://github.com/vertical-cloud-lab/powder-doser): [#179](https://github.com/vertical-cloud-lab/powder-doser/issues/179), [#164](https://github.com/vertical-cloud-lab/powder-doser/issues/164), [PR #166](https://github.com/vertical-cloud-lab/powder-doser/pull/166).
**Target journal:** Additive Manufacturing (`make pdf J=elsevier`). From the repo: "This could also go into some kind of controls journal, but my preference would probably be Additive Manufacturing if we can swing it" (Sterling, [#179](https://github.com/vertical-cloud-lab/powder-doser/issues/179#issuecomment-6094172162)). Elsevier; check its preprint policy and licence at G1.
**Results freeze (G2):** [DATE]
**Data that exist now:** One 42-dose Bayesian-optimization campaign on salt (`data/opt/salt-20260929T014732Z/`, the paper kit's own example data), and production runs on AlSi10Mg and Al-4047. Per the [PR #166 gap analysis]({GH}powder-doser/pull/166#issuecomment-6094195351), the multi-task learning, the physics-based inference and the shear-cell or Hall-flow reference measurements have not started.

**To decide at G1:**
- The abstract promises multi-task calibration across powders and physics-based property inference: which of these can have data by G2, and what does the paper claim if only part does?
- The two figures in `docs/optimization/tms-2027/` are watermarked dummy data: replace them with scripts on real snapshots before anything is shown.

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
