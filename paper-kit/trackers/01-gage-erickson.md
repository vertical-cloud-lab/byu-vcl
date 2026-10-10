<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/byu-vcl    Assignee: gage-erickson
-->

**Presenter:** Gage Erickson (GitHub `gage-erickson`)
**TMS 2027 abstract:** [Optimizing Ultrasonic Atomization Parameters for Supply-Chain-Resilient Aluminum Powders in Laser Powder Bed Fusion](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/8C6E7050A962719685258E270075387D?OpenDocument)
**Slot:** Talk, Thu Mar 18, 10:40 AM, Magnolia 13. Atomization & Powder Metallurgy for Advanced Applications: An MPMD Symposium Honoring Iver Anderson; session "Ultrasonic Atomization".
**Authors on the abstract:** Gage Erickson, Ronnie Guymon, Carl Robison, Sterling G. Baird (BYU).
**Where the work is:** [byu-vcl](https://github.com/vertical-cloud-lab/byu-vcl) atomizer issues [#124](https://github.com/vertical-cloud-lab/byu-vcl/issues/124), [#126](https://github.com/vertical-cloud-lab/byu-vcl/issues/126), [#249](https://github.com/vertical-cloud-lab/byu-vcl/issues/249), [#261](https://github.com/vertical-cloud-lab/byu-vcl/issues/261), [#264](https://github.com/vertical-cloud-lab/byu-vcl/issues/264) and [PR #268](https://github.com/vertical-cloud-lab/byu-vcl/pull/268); per #264, drafting for the atomization article lives in `digital-alloy-lab-private`.
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). The repos point past these gates: on 2026-10-10 Sterling wrote that the atomization results are saved "for a large Advanced Materials collection article (due early 2028) instead of a standalone first paper in Powder Technology" ([#264](https://github.com/vertical-cloud-lab/byu-vcl/issues/264#issuecomment-6101511949)), and the runs plan on that issue's branch submits in early 2028.
**Results freeze (G2):** [DATE]
**Data that exist now:** Runs of Oct 2, 6 and 8 (PR #268's run record) and the run plan for the 4047-in-6063 spread; none of the three runs is yet a repeat, so there is no repeatability number.

**To decide at G1:**
- Does this talk become its own paper by Feb 26 (and in which journal), or does the tracker follow the early-2028 Advanced Materials article, with G3 to G5 moved to that schedule?
- The repeatability bar for a run to count (the plan sets one): it decides what n can be by G2.

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
