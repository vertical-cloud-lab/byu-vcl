<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/caliber    Assignee: ronnie-guymon
-->

**Presenter:** Ronnie Guymon (GitHub `ronnie-guymon`)
**TMS 2027 abstract:** [CALIBER: A Retrieval-Augmented, Uncertainty-Aware Platform for Selecting High-Fidelity Characterization Parameters for Novel Alloys](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/62FB3D040E8FD6C085258E340053D059?OpenDocument)
**Slot:** Talk, Mon Mar 15, 3:10 PM, Anaheim. AI/ML/Data Informatics for Materials Discovery: Bridging Experiment, Theory, and Modeling; session "Data Informatics, Knowledge Infrastructure, and AI-Enabled Characterization".
**Authors on the abstract:** Ronnie Guymon, Gage Erickson, Carl Robison, Xavier Zaitzeff, Sterling G. Baird (BYU).
**Where the work is:** [caliber](https://github.com/vertical-cloud-lab/caliber) (its README is the abstract); [PR #14](https://github.com/vertical-cloud-lab/caliber/pull/14) for the scholarship and proposal deadlines.
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). No journal named. The MSA scholarship draft in caliber plans an M&M 2027 abstract in Jan to Feb 2027 and the "Journal manuscript and open data release" in Sep to Dec 2027, later than these gates.
**Results freeze (G2):** [DATE]
**Data that exist now:** `scripts/AlSi10Mg_EDS_Map_1.csv`, `eds_voltage_predictions.csv`, EBSD `example/area2-results/*stats.json`, and notes on EDS and EBSD parameters: thin for a results freeze so far.

**To decide at G1:**
- Paper by Feb 26, or on the Sep to Dec 2027 timeline the scholarship draft gives?
- Sterling presents a related abstract, "Patterns First: ... High-Fidelity EBSD Acquisition ...", with the same authors: one paper or two?
- Nearer deadlines that compete for the same weeks: the MSA proposal (due Nov 1) and the scholarship (due Dec 1).

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
