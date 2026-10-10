<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/byu-vcl    Assignee: [NEW OWNER]
-->

**Presenter:** Seth Leavitt (GitHub `seth-leavitt`), camera poster
**TMS 2027 abstract:** [Low-Cost Open-Source Camera Modules for Continuous Monitoring of Self-Driving Laboratories](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/DF0C2EB3DB75D5C385258E2800046C6E?OpenDocument)
**Slot:** Not yet in a published session; submitted as a student poster. AI-Enabled Materials Processing.
**Authors on the abstract:** Seth Leavitt (BYU), Yanghuang Liu, Jonathan Woo (Acceleration Consortium, University of Toronto), Sterling G. Baird.
**Where the work is:** [byu-vcl](https://github.com/vertical-cloud-lab/byu-vcl): [`tms-2027-abstract-equipment-monitoring.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/tms-2027-abstract-equipment-monitoring.md), [#143](https://github.com/vertical-cloud-lab/byu-vcl/issues/143), [PR #146](https://github.com/vertical-cloud-lab/byu-vcl/pull/146); uptime analysis in [streamingLambda #9](https://github.com/vertical-cloud-lab/streamingLambda/issues/9).
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). No target journal found.
**Results freeze (G2):** [DATE]
**Data that exist now:** streamingLambda branch `claude/issue-9-20260926-0901`, folder `uptime/`: 355 archived broadcasts, uptime 96.77% (OT-2) and 96.74% (powder doser), Jul 30 to Sep 25, from the timestamp overlay on every frame.

**To decide at G1:**
- **Presenter.** On 2026-10-10 Sterling wrote that Seth "has left the group and won't be participating" ([PR #193](https://github.com/vertical-cloud-lab/byu-vcl/pull/193#issuecomment-6101511534)); ProgramMaster still lists Seth as the on-site speaker. Who presents, and who owns the paper? (TMS asks no-shows to notify TMS and the organizer.)
- **The uptime claim.** The abstract says ">99% uptime"; the measured figure is 96.7%. The paper reports the measurement.
- Two co-authors are at the Acceleration Consortium: start the sign-off checklist at G1.

### Gates

- [ ] **G1 Outline, Fri Oct 23, 2026.** Journal chosen, with its preprint policy and licence checked ([checklist](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/preprint-and-license.md)); title; authors and order agreed; the claim in one sentence; the figure list (`figN_slug`: what it shows, which data file); a section outline in `paper/manuscript/`.
- [ ] **G2 Results freeze, [DATE].** Every figure is a script reading only `data/`; every data file has its README (units, n, provenance); `make figures check colorblind` is clean ([colour-blind check](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/colorblind.md)); every caption states n and its error bars. New data after this only by agreement, as a new snapshot noted here.
- [ ] **G3 Draft to co-authors, Fri Jan 29, 2027.** The whole draft, references with DOIs; `make credit pdf`; `git tag g3`; sent to every co-author with the commit hash; sign-off round 1 ([checklist](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/coauthor-signoff.md)).
- [ ] **G4 My review, [DATE, between Jan 29 and Feb 26].** First, `make rebuild-check` passes and a fresh clone builds ([clean rebuild](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/checklists/clean-rebuild.md)); then the `make todos` PDF and `make diff REV=g3` to me.
- [ ] **G5 Preprint and submission, Fri Feb 26, 2027.** Every author has approved this version (sign-off round 2); `make submission-check` passes; the Zenodo DOI is reserved and in the text; the AI paragraph sits where this publisher wants it ([generative AI](https://github.com/vertical-cloud-lab/byu-vcl/blob/main/paper-kit/boilerplate/generative-ai.md)); preprint posted under [LICENCE], and the paper submitted.
- [ ] **G6 Poster, Fri Mar 5, 2027.** Made from the paper's figures: a 4 ft × 4 ft board, figures readable from 2 m, a QR code to the preprint.
- [ ] **G7 Practice talk, [DATE, before TMS opens on Sun Mar 14].** Given to the group; feedback addressed.

### Thursday update (copy into a comment every Thursday)

```
Figure: [one figure: figures/out/figN_slug.png at commit abc1234, or the image]
Numbers: [the numbers behind it: n, value ± error, data/<file>]
Next week: [one thing]
Blocker: [one blocker, or none]
```
