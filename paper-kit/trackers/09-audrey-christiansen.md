<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/tensegrity-optimization    Assignee: achris0520
-->

**Presenter:** Audrey Christiansen (GitHub `achris0520`)
**TMS 2027 abstract:** [Tensegrity-Inspired Lattices for Orientation-Invariant Impact Protection](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/8AA038D180FB1CAE85258E2800132DD4?OpenDocument)
**Slot:** Not yet in a published session (probably a poster). Accelerating Innovation in Materials and Manufacturing.
**Authors on the abstract:** Audrey Christiansen, Marcus Madsen, Jinkwan Han, Jeffrey Hill, Sterling G. Baird (BYU).
**Where the work is:** [tensegrity-optimization](https://github.com/vertical-cloud-lab/tensegrity-optimization): [#78](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/78) (the abstract is on branch `claude/issue-78-20260731-0505`; its PR was never opened).
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). No target journal found.
**Results freeze (G2):** [DATE]
**Data that exist now:** None yet for the lattice: the abstract describes a campaign of 100 experiments (25 batches of 4) that has not started.

**To decide at G1:**
- What can be printed and tested by G2? 25 batches of 4 between now and the freeze is the critical path.
- How this paper differs from the Journal of Mechanical Design manuscript (Marcus's tracker), so the two do not overlap.

### Gates

- [ ] **G1 Outline, Fri Oct 23, 2026.** Journal chosen, with its preprint policy and licence checked ([checklist](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/preprint-and-license.md)); title; authors and order agreed; the claim in one sentence; the figure list (`figN_slug`: what it shows, which data file); a section outline in `paper/manuscript/`.
- [ ] **G2 Results freeze, [DATE].** Every figure is a script reading only `data/`; every data file has its README (units, n, provenance); `make figures check colorblind` is clean ([colour-blind check](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/colorblind.md)); every caption states n and its error bars. New data after this only by agreement, as a new snapshot noted here.
- [ ] **G3 Draft to co-authors, Fri Jan 29, 2027.** The whole draft, references with DOIs; `make credit pdf`; `git tag g3`; sent to every co-author with the commit hash; sign-off round 1 ([checklist](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/coauthor-signoff.md)).
- [ ] **G4 My review, [DATE, between Jan 29 and Feb 26].** First, `make rebuild-check` passes and a fresh clone builds ([clean rebuild](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/clean-rebuild.md)); then the `make todos` PDF and `make diff REV=g3` to me.
- [ ] **G5 Preprint and submission, Fri Feb 26, 2027.** Every author has approved this version (sign-off round 2); `make submission-check` passes; the Zenodo DOI is reserved and in the text; the AI paragraph sits where this publisher wants it ([generative AI](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/boilerplate/generative-ai.md)); preprint posted under [LICENCE], and the paper submitted.
- [ ] **G6 Slides or poster, Fri Mar 5, 2027.** Made from the paper's figures; TMS confirms which in early January. Slides: `vs.use("slide")`, one message per slide, nothing under 24 pt, about 20 minutes with questions. Poster: a 4 ft × 4 ft board, figures readable from 2 m, a QR code to the preprint.
- [ ] **G7 Practice talk, [DATE, before TMS opens on Sun Mar 14].** Given to the group; feedback addressed.

### Thursday update (copy into a comment every Thursday)

```
Figure: [one figure: figures/out/figN_slug.png at commit abc1234, or the image]
Numbers: [the numbers behind it: n, value ± error, data/<file>]
Next week: [one thing]
Blocker: [one blocker, or none]
```
