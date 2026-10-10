<!--
DRAFT, not posted. For Sterling's review before anything goes to a student.
Issue title: TMS 2027 to [JOURNAL]: tracker
Open in: vertical-cloud-lab/powder-doser    Assignee: lbwinters
-->

**Presenter:** Luke Winters (GitHub `lbwinters`)
**TMS 2027 abstract:** [Agentic Systems Design of an Open-Source Powder Doser for L-PBF Feedstock Research: CAD, PCB, and Firmware](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/2711856F2A84241585258E2800155BBF?OpenDocument)
**Slot:** Not yet in a published session (probably a poster). Accelerating Innovation in Materials and Manufacturing.
**Authors on the abstract:** Sam Charles, Will Mulberry, Luke Winters, Sterling G. Baird.
**Where the work is:** [powder-doser](https://github.com/vertical-cloud-lab/powder-doser): PCB automation, UI and digital twin ([#87](https://github.com/vertical-cloud-lab/powder-doser/issues/87), [#94](https://github.com/vertical-cloud-lab/powder-doser/issues/94), [#95](https://github.com/vertical-cloud-lab/powder-doser/issues/95), [#122](https://github.com/vertical-cloud-lab/powder-doser/issues/122), [#158](https://github.com/vertical-cloud-lab/powder-doser/issues/158)); PR #91's venue analysis.
**Target journal:** [JOURNAL] (`make pdf J=[TEMPLATE]`). No journal for this abstract on its own. The AI-assisted design work is part of the Digital Discovery base paper, where Luke is third author ([#96](https://github.com/vertical-cloud-lab/powder-doser/issues/96)); PR #91's venue analysis names the International Journal of Advanced Manufacturing Technology "if the LLM/code-CAD workflow becomes a major contribution".
**Results freeze (G2):** [DATE]
**Data that exist now:** `paper/figures/data/ai_tools_timeline.csv`, `ai_usage_weekly.csv`, `design_log_cad.csv`; PCB tool evaluations on branch `copilot/literature-search-generative-pcb-design`.

**To decide at G1:**
- Own paper, or the AI-design section of the Digital Discovery base paper? If own paper, how it differs from that one.
- An AI-tools paper is exactly where the generative-AI disclosure is hardest: read boilerplate/generative-ai.md before choosing a journal (ASME prohibits AI-drafted text).

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
