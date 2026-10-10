<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/powder-doser    Assignee: swcharles
-->

**Presenter:** Sam Charles (GitHub `swcharles`)
**TMS 2027 abstract:** [A Programmable Powder Doser with 15+ Reservoirs and Automated Auger Swapping for AI-Enabled Alloy-Development Workflows](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/B6383C9897FAF23585258E280014B8D5?OpenDocument)
**Slot:** Talk, Mon Mar 15, 9:40 AM, Washington. AI-Enabled Materials Processing: Integrating Accelerated Experimental Workflows and Processing-Aware Machine Learning; session "Autonomous Laboratories, Digital Twins, and Process Intelligence".
**Authors on the abstract:** Sam Charles, Will Mulberry, Luke Winters, Sterling G. Baird (BYU Vertical Cloud Lab).
**Where the work is:** [powder-doser](https://github.com/vertical-cloud-lab/powder-doser): the multi-doser ([#128](https://github.com/vertical-cloud-lab/powder-doser/issues/128)); the base manuscript ([#96](https://github.com/vertical-cloud-lab/powder-doser/issues/96), [PR #97](https://github.com/vertical-cloud-lab/powder-doser/pull/97)).
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). The repos name Digital Discovery for the *base* doser paper, which Sam leads ([#96](https://github.com/vertical-cloud-lab/powder-doser/issues/96)): "This first (base) manuscript will include only the base design and the relevant exploration of ai--the other topics will be published separately later", and the modular multi-powder design this abstract presents is one of those other topics. That paper targets a collection due Nov 13 (frozen draft Oct 30, submission Nov 11; [PR #97](https://github.com/vertical-cloud-lab/powder-doser/pull/97)).
**Results freeze (G2):** [DATE]
**Data that exist now:** For the base paper: `paper/figures/data/*.csv` on branch `copilot/draft-base-manuscript`, the #116 protocol tests (99 valid doses), the PR #173 versatility figure (13 powders). For the 15+ reservoir system itself: no dosing data yet.

**To decide at G1:**
- Which paper does this tracker follow: the multi-powder paper (journal and freeze date open), or the Digital Discovery base paper (then title it "TMS 2027 to Digital Discovery: tracker" and use its Oct 30 / Nov 11 dates)?
- If the multi-powder paper: what has to run on the 15+ reservoir system by G2, and is that feasible by the freeze date?

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
