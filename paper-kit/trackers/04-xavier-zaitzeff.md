<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/partial_kgfn    Assignee: XZaitzeff
-->

**Presenter:** Xavier Zaitzeff (GitHub `XZaitzeff`)
**TMS 2027 abstract:** [Implementation of Bayesian Optimization over Function Networks with Partial Evaluations for Cost-Aware AI Guided Material Discovery of Critical Mineral Lean Aluminum Alloys](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/1701C81A5B7A265E85258E27006D39F9?OpenDocument)
**Slot:** Talk (25-minute slot), Wed Mar 17, 10:55 AM, Los Angeles. Algorithms Development in Materials Science and Engineering; session "Algorithms and Methods for Material Processing and Manufacturing".
**Authors on the abstract:** Xavier Zaitzeff, Sterling G. Baird (BYU).
**Where the work is:** [partial_kgfn](https://github.com/vertical-cloud-lab/partial_kgfn) ([#4](https://github.com/vertical-cloud-lab/partial_kgfn/issues/4)); Thermo-Calc on the HPC (byu-vcl #123).
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). No target journal found.
**Results freeze (G2):** [DATE]
**Data that exist now:** None found as data files; the method code is in partial_kgfn.

**To decide at G1:**
- Sterling's talk "Cost-aware Bayesian optimization across a CALPHAD-atomization-LPBF function network ..." covers the same function network: where does this paper stop and that one start?
- Method paper (benchmarks only) or applied (alloy results)? It decides what G2 freezes.

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
