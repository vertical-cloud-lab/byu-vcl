<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/[REPO]    Assignee: timothy-commins
-->

**Presenter:** Tim Commins (GitHub `timothy-commins`)
**TMS 2027 abstract:** [FeS/PbS Precipitation Boundaries for Impurity Management in Concentrated Hydrometallurgical Process Waters](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/D2B181B3FF2CADCB85258E35005F8A0D?OpenDocument)
**Slot:** Not yet in a published session (probably a poster). From Mine to Refinery: An EPD Symposium Honoring Shijie Wang.
**Authors on the abstract:** Timothy Commins, Samuel Charles, Xavier Zaitzeff, Finn Albiston, Seth Leavitt, Sterling G. Baird.
**Where the work is:** No precipitation data or plan found in the readable repositories. Related: the OT-2 wireless colour sensor ([byu-vcl #33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33), [#197](https://github.com/vertical-cloud-lab/byu-vcl/issues/197), [PR #202](https://github.com/vertical-cloud-lab/byu-vcl/pull/202)).
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). No target journal found for the precipitation work. (The colour-sensor issue, #33, suggests HardwareX or the Journal of Open Hardware for the sensor itself, which is a different paper.)
**Results freeze (G2):** [DATE]
**Data that exist now:** None found for precipitation mapping; the colour-sensor results are in `wireless-color-sensor/ot2/` and on PR #202's branch.

**To decide at G1:**
- Is the precipitation-mapping platform the OT-2 with the colour sensor? If so, which paper comes first: the hardware, or the FeS/PbS boundaries?
- Seth Leavitt, a co-author, has left the group: keep him as an author for his part, and plan his sign-off by email.

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
