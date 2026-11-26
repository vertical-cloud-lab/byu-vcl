# Referee report

## Verdict

**Not yet ready as the lab’s standing instruction.** The guide has the right architecture and preserves most of the hard-won lessons, but it still fails under ordinary autonomy constraints. Its main defect is not slide design. It is authority handling: several “PI required” gates have no timeout, substitute approver, provisional mode, or stop rule.

A second release issue is provenance. The guide links to source files and iteration artifacts that are absent from `/workspace`, so I could not verify the synthesis against the original iterations. I audited it against the supplied iteration 1–4 summary and the text itself. A standing guide must not depend on broken or unavailable links.

Minimum changes for a **yes**:

1. Replace absolute PI gates with an authority/escalation matrix and a safe provisional mode.
2. Replace “PI resolves factual disputes” with an evidence-based conflict rule. No person may resolve incompatible records by preference.
3. Operationalize the brief defaults, reading-load test, and cold-viewer QA.
4. Correct the cross-run prohibition so labeled comparisons remain possible.
5. Reconcile assertion-only review with hooks, transitions, and demo cues.
6. Add mandatory accessibility, delivery, Q&A, backup-slide, and offline-fallback checks.
7. Restore the referenced source artifacts and attach a real bibliography supporting every T1/T2 assignment.

## 1. Consistency audit

### A. Required approval conflicts with the default mechanism

> “**Brief contract** (above) — *PI required.*”

but also:

> “Propose defaults for unanswered items and display them before storyboarding.”

Displayed defaults are not an approved brief. As written, the agent must either stop at stage 1 or silently treat non-response as consent. Scenario (c) exposes this directly.

**Patch:** distinguish `approved`, `provisional`, and `blocked` decisions. Define which low-risk decisions the agent may make provisionally and which require an accountable human before release.

### B. Human authority is allowed to override evidence

> “Flag conflicts … *PI resolves factual disputes.*”

A PI can identify missing context, select the intended run, or narrow the claim. A PI cannot resolve conflicting measurements merely by choosing one. This wording weakens the provenance lesson from iteration 3.

**Patch:** “The claim owner supplies missing context. The agent resolves the record only from traceable source evidence. If the conflict remains, preserve both values with their run IDs, narrow the claim, or block release.”

### C. The cross-run rule is too absolute

> “0.9972 g vs 0.9956 g are different runs — never mix artifacts across runs on one slide.”

This prevents a legitimate, explicitly labeled run comparison, replication panel, or longitudinal result. The actual failure was presenting artifacts from different runs as one coherent event.

**Patch:** “Never combine artifacts from different runs as if they describe the same event. Cross-run comparisons are allowed only when each run is labeled and the comparison is the slide’s stated purpose.”

### D. Assertions-only review conflicts with allowed slide roles

Rule 1 says:

> “demos get a what-to-watch-for cue; hooks/transitions may need neither.”

C10 then requires:

> “assertions-only (headlines must argue the talk by themselves)”

Hooks, transitions, and some demo cues will fail that audit by design.

**Patch:** run the assertions-only audit on **claim slides**. In the full sequence, represent hooks, transitions, and demos by their intended rhetorical function or cue, then test whether the sequence still argues the talk.

### E. Native artifacts remain slightly overprivileged

> “Prefer faithful extraction of native artifacts…”

and:

> “The native-artifact library (what to build slides FROM)”

The guide correctly denies an authenticity-based truthiness benefit, but the library heading turns a defeasible preference back into a near-mandate. The CNMS lesson was that native artifacts worked **in that deck because they supplied integrated, inspectable evidence**, not that screenshots and recordings are generally the best visual form.

**Patch:** rename the section “Candidate evidence library.” Require a form comparison: native crop, faithful redraw, derived plot, or concise transcription. Choose the form that best exposes the relevant evidence while retaining provenance.

### F. Evidence-tier labels overstate auditability

> “**[T1]** = replicated experimental support (Mayer/CTML effect sizes d≈0.4–1.2; assertion–evidence studies)”

No study-level bibliography, outcome definition, population, or mapping from each rule to evidence is included. A range such as `d≈0.4–1.2` is not enough to support several heterogeneous rules. Mechanical QA requirements also appear under “T1 gates” even though they are engineering release criteria, not necessarily experimentally validated learning effects.

**Patch:** separate:

- `E`: empirical audience-learning evidence, with citations and boundary conditions;
- `P`: production/reliability requirement;
- `C`: craft default;
- `L`: lab-specific lesson from the CNMS post-mortem.

### G. “One message” changes unit mid-rule

> “One intended audience inference per slide/build.”

A build can contain several exposure states. The phrase can mean one inference per final slide, per animation state, or per complete sequence. Those lead to different authoring decisions.

**Patch:** “Each exposure state must have one current focal inference; the complete build must support one parent inference.”

## 2. Actionability audit

### Worst offender 1: missing-answer defaults

**Current:**

> “Propose defaults for unanswered items and display them before storyboarding.”

The guide gives neither defaults nor a rule for when silence counts as permission.

**Executable rewrite:**

> If no answer arrives by the agreed work-start time, create a visible `ASSUMPTIONS` block. Default to: mixed technical audience; internal-only draft; no new performance, priority, safety, or generality claim; no confidential material; prerecorded media plus static fallback; latest approved deck as style reference; all uncertain beats optional. Continue only to a watermarked review draft. Do not publish, overwrite the canonical deck, or present disputed evidence until an authorized reviewer accepts the assumptions.

### Worst offender 2: factual-conflict resolution

**Current:**

> “*PI resolves factual disputes.*”

This is both non-executable during PI absence and scientifically unsafe.

**Executable rewrite:**

> For each conflicting value, record file path, commit, timestamp, run ID, unit, and processing step. Test whether the records concern the same run and metric. If yes and the discrepancy cannot be reconciled from source data, mark the claim `CONFLICTED` and exclude it from the release deck. If they concern different runs, label them separately and use them together only for an explicit cross-run comparison. A human may supply context but may not erase an unresolved discrepancy.

### Worst offender 3: cold-viewer and room-legibility QA

**Current:**

> “decisive text ≥ ~24 pt equivalent”

and:

> “then role-specific cold-viewer checks…”

The agent may not know the room, projection geometry, viewer acuity, display scaling, or have access to a cold viewer. “24 pt equivalent” is not a reproducible room-legibility test.

**Executable rewrite:**

> Before release, render every slide at the target aspect ratio and inspect it at 100%, at a 25% thumbnail, and in a simulated back-row view based on known room/display dimensions. Run automated checks for overlap, clipping, missing fonts/media, contrast, and minimum text size. Then obtain one human cold-viewer result using a fixed prompt: after five seconds, state the slide’s role-specific target without coaching. Record `pass`, `fail`, or `not tested`. If room geometry or a human viewer is unavailable, label legibility `UNVERIFIED`; do not convert that absence into a pass.

The reading-load rule also needs a formula. Define an exposure interval as one static state between advances, count newly revealed audience-readable words, and divide by rehearsed dwell time. Without rehearsed dwell time, report word count and mark the rate unknown.

## 3. Omission audit

### Material from iterations 1–4 that is incompletely captured

Most supplied conclusions survived: appended-block failure, redundancy screening before layout, native evidence, provenance, stage gates, deck-level cohesion, PR-style batching, acceptance tests, and preserve lists.

Three parts remain incomplete:

1. **The reusable two-pass checklist is named, not actually supplied.** Section 5 describes ordering, but a future agent has no compact pass/fail checklist or completion record.
2. **“Appended-prototype status” is recorded as history but not made a release test.** Add: “For every new core slide, name its causal predecessor and successor. If either is absent, classify it as backup or reject it.”
3. **The provenance trap is overcorrected.** The lesson should prohibit false same-run continuity, not all cross-run slides.

### Delivery guidance is substantially missing

Doumont’s delivery guidance covers extemporaneous speech, rehearsal to fluency, purposeful silence instead of filler words, vocal modulation, stable stance, deliberate gesture, eye contact, and a four-step question procedure: listen, repeat/rephrase if needed, think, then answer briefly to the whole audience. The guide currently reduces rhetorical QA mostly to timing and “narration extends rather than reads.” Add a delivery rehearsal gate containing those checks. [Doumont, *Effective oral presentations*, pp. 1–4](https://www.cs.tufts.edu/~nr/cs257/archive/jean-luc-doumont/oral.pdf)

The guide also lacks an explicit opening/closing performance test. Doumont distinguishes the attention getter, need, task, main message, preview, review, conclusion, and close. C1 contains some structural analogues, but it does not test whether the speaker can deliver the opening and close cleanly without slide dependence. [Doumont, pp. 2–4](https://www.cs.tufts.edu/~nr/cs257/archive/jean-luc-doumont/oral.pdf)

### Q&A and backup strategy are missing

Backups are classified and packaged, but not designed around anticipated questions. Add:

- list the 5–10 most probable skeptical questions;
- map each to a concise verbal answer, evidence source, and optional backup slide;
- place backups after the end marker with searchable titles and a contents/index slide;
- include limitations, methods, sensitivity analyses, provenance, and definitions;
- rehearse navigation back to the closing slide;
- never let a backup introduce an unreviewed public claim.

Nature’s scientific-presentation guidance explicitly recommends selectivity in the talk, leaving time for Q&A, and anticipating likely questions. MIT’s Communication Lab likewise recommends preparing technical backup slides and repeating a question before answering. [Nature Scitable](https://www.nature.com/scitable/topicpage/oral-presentation-structure-13900387/) and [MIT NSE Communication Lab](https://mitcommlab.mit.edu/nse/commkit/slideshow/)

### Accessibility is not an executable release gate

“Bounded deviations for legibility/accessibility” is too vague. Add required checks for:

- PowerPoint Accessibility Checker;
- logical reading order and unique slide titles;
- alternative text or marked-decorative status for non-evidentiary images;
- adequate color contrast and no color-only encoding;
- captions/subtitles for video, transcripts where appropriate, and accessible controls;
- readable fonts and sufficient size;
- meaningful link text;
- screen-reader test for the distributed deck or handout;
- verbal description of decisive visual evidence during delivery.

These are supported by Microsoft’s PowerPoint accessibility guidance and W3C media guidance. [Microsoft Support](https://support.microsoft.com/en-US/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities) and [W3C WAI](https://www.w3.org/WAI/media/av/av-content/)

### Non-native-English and mixed-language audiences

Add a brief field for audience language proficiency and accommodations. Defaults should be shorter sentences, concrete verbs, expanded acronyms on first use, stable terminology, advance definition of specialized terms, deliberate pacing, pauses after dense claims, captions for recorded speech, and avoidance or explanation of idiom, wordplay, culture-bound analogy, and unexplained metaphor. Supply key names, numbers, equations, and terms visually. This is useful for everyone and especially important when the speaker or audience is operating in an additional language.

This should be labeled a craft/accessibility default unless the guide adds a properly scoped evidence review.

### Handouts and posters need separate contracts

> “Export a handout separately if needed.”

That does not specify what the handout is. Add a handout contract: standalone title and context, expanded captions, readable references, definitions, links, version/date, accessibility, and no reliance on animation or narration. Do not generate it by merely printing live slides with notes.

Posters should be declared **out of scope** or get a separate guide. A poster is self-paced, spatial, and often supports conversation; the slide rules about imposed sequence, builds, and speaker-controlled dwell do not transfer directly.

### Venue and failure recovery

The brief asks about delivery mode, but packaging needs an explicit run-of-show test: target machine, fonts, aspect ratio, clicker, audio, internet, adapters, media codec, presenter view, recording permissions, static demo fallback, local copy, PDF fallback, and a clean-deck recovery point. Doumont also recommends investigating time, room, and setup in advance. [Doumont, p. 1](https://www.cs.tufts.edu/~nr/cs257/archive/jean-luc-doumont/oral.pdf)

### Scope and identity

“PI” is too lab-specific and too narrow. The accountable person may be the presenter, project lead, data owner, or communications approver. Define roles separately:

- **presenter:** owns delivery and timing;
- **claim owner:** attests to scientific interpretation;
- **data owner:** resolves metadata and access questions;
- **release approver:** accepts confidentiality, licensing, and public wording.

One person may hold several roles.

## 4. Failure-mode simulation

### (a) “Make me 5 slides for a 10-min department seminar next week from the powder-doser repo”

**Where it breaks**

- The requested slide count arrives before the outcome, audience skepticism, mandatory beats, confidentiality, and allowed claim strength.
- “Time from rehearsal, not slide count” conflicts with a hard five-slide deliverable unless five means exactly five core slides.
- The native-artifact inventory does not identify which files belong to one coherent run.
- Multiple PI gates turn a one-week job into a serial approval queue.
- No rehearsal or Q&A allocation is specified within the ten minutes.

**Safe execution under a repaired guide**

1. Ask one compact brief message covering outcome, audience, ten-minute allocation including Q&A, mandatory beat, confidentiality, and claim level.
2. In parallel, inventory the repository without making performance claims.
3. Treat five as an upper bound on projected core states unless the requester confirms exactly five.
4. Draft a five-beat storyboard: need, method, observed result, verification/limitation, takeaway.
5. Use one internally consistent run or an explicitly labeled comparison.
6. Produce a watermarked review draft, static media fallbacks, and anticipated-question backups.
7. Release only after claim-owner and presenter checks.

The current guide can start this task but cannot finish it autonomously because its approval semantics are undefined.

### (b) “Review my draft deck for the TMS 2027 talk,” involving CALPHAD work in a private repo

**Where it breaks**

- The agent has neither the deck nor authorized private-repository access.
- The guide assumes evidence can be traced to a known native-artifact library; this library is irrelevant to CALPHAD work.
- A visual review alone cannot validate thermodynamic databases, phase labels, model versions, fit/validation separation, or public-release permissions.
- “PI resolves factual disputes” is unsafe where model outputs or database versions conflict.
- Notes and delivery context may be absent, making delivery-dependent criticism indeterminate.

**Required input**

The deck or rendered slides, speaker notes, speaking time, audience description, repository or a claim-evidence export, database/model/version metadata, confidentiality rules, and intended public wording.

Without those materials, the agent may review only visible structure and rendering and must label scientific provenance, completeness, and delivery findings `NOT ASSESSED`. It must not infer hidden CALPHAD validity from polished figures.

### (c) “Add two slides on last month’s results … while I’m at a conference,” with no PI available

**Where it breaks**

- Stage 1 is explicitly “PI required.”
- Stages 2–5 also reserve factual, representative-claim, storyboard, and delivery choices for the PI.
- The guide has no asynchronous approval path, substitute authority, or expiry time.
- “Propose defaults” does not authorize modification of the canonical deck.

**Safe provisional mode**

The agent may:

- duplicate rather than overwrite the canonical deck;
- insert two clearly marked optional slides at the causal location;
- use only already approved wording and traceable results from a single labeled run;
- avoid new generality, causality, safety, priority, or validated-performance claims;
- add source path, commit, run ID, and uncertainty in notes;
- generate PNG proofs and a short decision log;
- supply a static fallback and a one-command/reversible removal path.

The agent may not release the revised deck publicly or treat it as canonical until an authorized reviewer accepts it. If the results are conflicting, confidential, or scientifically novel, it must stop rather than improvise.

## 5. Proposed standing-guide patch set

Add a short section immediately before the pipeline:

### Authority and operating modes

- `APPROVED`: required decisions accepted by the relevant owner.
- `PROVISIONAL`: agent may create a reversible, watermarked review artifact under stated conservative defaults.
- `BLOCKED`: no release artifact may be produced because evidence, access, confidentiality, or claim authority is missing.
- Human silence never changes `PROVISIONAL` to `APPROVED`.
- No human approval converts unresolved contradictory evidence into resolved evidence.
- The canonical deck is changed only in `APPROVED` mode; provisional work goes to a branch or duplicate.

Add four release-gate rows:

| Gate | Required record | Failure consequence |
|---|---|---|
| Scientific provenance | claim → source → commit/version → run ID → processing | Block affected claim |
| Accessibility | checker, reading order, contrast, media alternatives, distributed-file test | Repair or document approved exception |
| Delivery and Q&A | timed rehearsal, opening/close, likely questions, backup map | Keep as review draft |
| Technical fallback | target-path media test, local/static/PDF fallback | No live-demo dependency |

Finally, convert every qualitative instruction into one of four forms: a measurable test, a named human judgment, a conservative default, or an explicit stop condition. That would make the guide usable by an autonomous agent rather than merely intelligible to one.

## Limitations

- The post-mortem, PR artifacts, task IDs, and OneDrive recipe cited by the guide were not available in `/workspace`. I therefore could not verify whether any iteration finding was omitted beyond the summary supplied in the prompt.
- This was a procedural referee audit, not an empirical experiment. No statistical test was appropriate.
- The external presentation sources support the omitted practices, but I did not treat all expert guidance as replicated causal evidence. The revised guide should preserve that distinction.

## Discretionary analytical decisions

- Treated “PI” as an overloaded authority role and recommended separating presenter, claim owner, data owner, and release approver.
- Ranked the three actionability failures by their ability to block autonomous execution or compromise scientific integrity, rather than by frequency.
- Treated native artifacts as one evidence representation among several, not as an unconditional design preference.
- Allowed explicitly labeled cross-run comparisons while prohibiting false same-run continuity.
- Used external expert and platform guidance to identify omissions, but did not upgrade those recommendations to the guide’s T1 category without a scoped evidence review.