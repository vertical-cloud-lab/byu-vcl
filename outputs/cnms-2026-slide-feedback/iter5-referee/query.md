# Iteration 5 of 5: referee the final synthesis — the agent's operating guide for slide generation and review

## The loop so far
Iter1 adversarial critique reranked why 14 generated quote slides were cut from a CNMS
2026 talk (appended-prototype status + redundancy with natively-integrated beats +
rendering defects > pure style). Iter2 graded the design rules against the multimedia-
learning / assertion–evidence literature. Iter3 stress-tested the rubric into defeasible
purpose/default/exception/test form, produced a stage-gated pipeline with PI-judgment
gates, exposed a provenance trap in a redesign (mixing artifacts from two different dose
runs) and 10 deck-level cohesiveness rules. Iter4 produced a calibrated PR-style review
of the presented deck (blocker → ≤3 high-impact → ≤3 questions → patch set → optional
polish → preserve list, all with acceptance tests) plus a reusable two-pass review
checklist.

## The synthesized guide (referee this)

# Agent guide: generating and reviewing presentation slides for this lab

Synthesized 2026-08-13 (PR #176) from: the CNMS 2026 deck post-mortem
([cnms-2026-slide-style-analysis.md](cnms-2026-slide-style-analysis.md)), five Edison
Scientific critique iterations (artifacts + task IDs in
[`outputs/cnms-2026-slide-feedback/`](../outputs/cnms-2026-slide-feedback/)), and
Jean-luc Doumont's materials (three laws; "with each slide, convey one message — state
it verbally, develop it visually"; the Nature Masterclass exemplar decks). This is the
operating document future sessions should load before touching a deck.

## 0. The one-paragraph lesson

For CNMS 2026 I generated 14 verbatim-quote text slides; all 14 were cut. The corpus
mining and curation were used — the PI presented the same beats as **native artifacts**
(screen recordings of the real GitHub threads, phone video of hardware responding) —
but my rendering failed: appended as a trailing block instead of placed in the
narrative, redundant with beats already integrated, text-collision defects, and
document-styled where the deck's language is evidence-styled. Slide generation is a
pipeline with the PI's judgment gated in, not a rendering step at the end.

## 1. Before generating anything: the brief

Ask (one compact message, not an interview). Minimum viable: #1, #3, #4.

1. What should this audience believe/do at the end, in one sentence?
2. Who is in the room; what skepticism should the talk answer?
3. Hard speaking time and delivery mode (live demo? recording? offline fallback?).
4. Which beats are mandatory / expendable / confidential / non-negotiable?
5. Which deck is the canonical style reference; how much deviation is acceptable?
6. What evidentiary wording is acceptable (case study vs. validated performance claim)?

Propose defaults for unanswered items and display them before storyboarding.

## 2. The pipeline (stage → binding rules → PI gate)

1. **Brief contract** (above) — *PI required.*
2. **Evidence inventory** — index artifacts with source, date, actor, run ID, and what
   each does and does NOT establish. Flag conflicts (e.g., 0.9972 g vs 0.9956 g are
   different runs — never mix artifacts across runs on one slide). *PI resolves factual
   disputes.*
3. **Claim/beat selection** — claim–evidence ledger; reject beats redundant with the
   existing deck BEFORE layout; assign cut priority. *PI picks representative claims.*
4. **Narrative placement** — text storyboard; setup/payoff pairs; callbacks; optional
   modules with insertion/cut points. Core additions go at their causal location;
   backups may be appended after a clear end marker; never dump core content as a
   trailing block. *PI approves storyboard.*
5. **Form selection** — claim slide / process chain / comparison / demo cue / hook /
   transition / callback; static vs. build; what the speaker says that the slide
   doesn't. *PI confirms delivery-dependent choices.*
6. **Artifact preparation** — crop decisive region, mask chrome, annotate
   non-destructively; verified transcription only when a native crop can't pass
   room-legibility, always with a source pointer; never silently reconstruct plots or
   measurements.
7. **Layout & style extension** — host deck's tokens and semantic conventions, not its
   mistakes; bounded deviations for legibility/accessibility; new tokens documented and
   reused. (PowerPoint web: clipboard paste bypasses autocorrect; numeric size fields;
   masters not editable — see [cnms-2026-onedrive-access.md](cnms-2026-onedrive-access.md).)
8. **Render & technical QA** — gates below.
9. **Rehearsal & rhetorical QA** — timing from rehearsal, not slide count. *PI required.*
10. **Packaging** — core deck + backups + media bundle + provenance map + change
    summary; per-slide PNG proofs so the PI can triage like a PR.

Two loops: evidence conflicts → back to 2–3; failed rehearsal → back to 3–6. Never
patch a bad narrative with visual QA.

## 3. Design rules (defeasible defaults: purpose · default · exception · test)

Evidence tiers from the literature pass (Edison iter2): **[T1]** = replicated
experimental support (Mayer/CTML effect sizes d≈0.4–1.2; assertion–evidence studies);
**[T2]** = consistent-with-theory craft knowledge.

1. **[T1] One intended audience inference per slide/build.** Not "one content type" —
   an evidentiary chain (prompt → action → check) can be one inference. Analytic claims
   get a sentence assertion + visual evidence; demos get a what-to-watch-for cue;
   hooks/transitions may need neither. *Test:* name the inference; if you can't, the
   slide isn't ready.
2. **[T2] Prefer faithful extraction of native artifacts; preserve provenance and
   wording, not necessarily pixels.** Crop/enlarge/mask/annotate the real thing. The
   benefit runs through *clarity and annotation*, not authenticity per se (truthiness
   effect failed replication). Verified transcription is allowed when crops can't reach
   room legibility — label it and keep a source thumbnail/pointer. *Test:* decisive
   text ≥ ~24 pt equivalent; provenance traceable from the notes.
3. **[T1] Manage reading load, not word count.** Metric: *new, audience-directed
   readable words per exposure interval* (persistent labels and subordinate provenance
   don't recount). ~20 projected wpm is a rehearsal trigger, not a release gate.
   Complexity check besides words: focal regions, unfamiliar encodings, required
   comparisons. Quote slides: project the key phrase, let the audience read silently,
   then narrate commentary that *extends* (never reads) it.
4. **[T1] Build by emphasis only when order/suspense/correspondence matters.** Hold a
   skeleton constant, dim the past, highlight the current — but a static annotated
   chain or small multiples beats a mechanical 3-step build when experts can parse it
   at once. Keep dimmed context readable.
5. **[T2] Time from rehearsal; classify every slide** core / optional module / backup /
   provenance. Cut from a pre-ranked list.
6. **[T2] Match the host's stable tokens and semantics — not its defects.** Ask before
   introducing a conspicuous new motif.
7. **[T1 gates + T2 tests] Release gates:** no text/object overlap; no leftover
   placeholders; no off-slide objects (unless declared animation staging); safe
   margins; media plays on the delivery path; then re-render each slide and *look*;
   then role-specific cold-viewer checks (hook → orientation; claim → claim + focal
   evidence; demo → cue visibility; expert plot → entry point). Five-second/80% is
   craft, not validated — treat as a smoke test.
8. **[T2] Claim-dependent evidence schema.** Quantitative claims: unit, denominator,
   comparator, variability, scoring method — and don't confuse acceptance tolerance
   (±5 mg) with measurement uncertainty. Singular demos: provenance, operator,
   observation vs. inference, replication status. Agent self-report is a report;
   pair it with external verification (scale telemetry, video, human-held key) or
   narrow the claim and label it unverified.

## 4. Deck-level cohesiveness rules (checkable)

- **C1 Deck contract:** outcome sentence, opening tension, 3–5 section functions,
  closing answer, role of the framing device (e.g., Wizard-of-Oz). Every core slide
  maps to a function.
- **C2 Claim–evidence–payoff ledger:** no claim before its setup; no evidence without
  its "so what"; no unresolved promise at the close.
- **C3 Motif semantics:** each recurring motif means one thing (curtain = concealed
  human work; GitHub card = instruction/provenance). Audit thumbnails for one-off
  decorations and conflicting reuse.
- **C4 Repeated examples must advance state** (observe → act → close the loop →
  survive blinded evaluation); two adjacent examples with the same "new capability"
  answer → merge, cut, or turn one into a limitation.
- **C5 Section bridges:** last assertion of section N + first of N+1 must chain
  ("Remote action works; can we trust the result?").
- **C6 Entity/terminology identity:** stable names and visual identifiers; audit for
  synonym drift (Claude/agent/bot).
- **C7 Callbacks change meaning,** never just repeat imagery.
- **C8 Pacing:** plot dwell × new-words × complexity × role across the deck; flag
  peaks and monotone runs; validate in rehearsal.
- **C9 Separate the live layer from the document layer** — notes/backup/repo docs
  carry provenance; the projection carries inference. Export a handout separately if
  needed.
- **C10 Three global reviews:** thumbnails (rhythm/motifs); assertions-only (headlines
  must argue the talk by themselves); evidence-only (artifacts traceable,
  non-redundant, matched to claims). Plus a notes-only rehearsal check that narration
  extends rather than reads.

## 5. Reviewing a hand-made deck ("meaningful suggestions" mode)

Two passes: **narrative/evidence first**, visual polish only after structural decisions
land. Doumont feedback norms: observations as facts about the artifact/experience
("at 25% zoom the labels are unreadable to me"), future-oriented, no reproaches, no
intent-guessing.

Batching (PR-style; every item: ID, slide, type, observation, consequence, proposed
patch, effort, confidence, delivery dependency, acceptance test, status):

1. **Release blockers** (factual conflict, unsupported public claim, broken media,
   privacy/licensing) — unlimited but rare; these outrank all aesthetics.
2. **≤3 high-impact changes**, ranked by audience benefit ÷ rework cost.
3. **≤3 clarifying questions** — only ones whose answers change a recommendation.
4. **One proposed patch set** (storyboard move, rewritten assertion, one-slide mockup).
5. **Optional polish** — collapsed checklist, never mixed with blockers.
6. **Preserve list** — 2–3 patterns that must not be disturbed (more useful than
   praise).

Closure semantics: the PI should be able to reply `accept H1/H3, decline H2, answer
Q1`. Delivery-dependent observations must say so and link to notes/rehearsal, not
stand as unconditional findings.

## 6. The native-artifact library (what to build slides FROM)

~418 agent-committed media files across the three public repos (inventory method in
`outputs/cnms-2026-slide-feedback/`): camera stills (`byu-vcl/wireless-color-sensor/`,
`ot2-overhead-camera/`), CAD renders (`tensegrity-optimization/cad/`,
`powder-doser/design/`), BO plate previews (`tensegrity-optimization/bo/`), drop-test
figures (`data/drop-tests/`), dose telemetry (`powder-doser/data/pid-dose/`), prior
slide previews (`tensegrity-optimization/presentation/`) — plus the full comment corpus
(`data/cnms-2026-corpus/`) from which any comment card can be re-rendered at chosen
zoom, and 18 screen-recordings already embedded in the CNMS deck. Rule: every evidence
panel on a slide traces to one of these by path + commit + (for hardware runs) run ID.

## 7. Known mechanical constraints (PowerPoint for the web via automation)

See [cnms-2026-onedrive-access.md](cnms-2026-onedrive-access.md) for the full recipe.
Highlights: clipboard paste bypasses autocorrect (mandatory for verbatim text); numeric
Shape ribbon fields for exact sizes; ≈92.3 px/in mapping for drag-positioning; slide
masters are NOT editable in the web editor (use python-pptx + REST upload when the file
is closed, or desktop PowerPoint); co-authoring works while the owner has the deck
open; verify persistence against the re-downloaded blob, and verify *renders*, not just
text.


## Referee tasks
1. **Consistency audit:** find contradictions between guide sections, or places where
   the guide waters down a harder-won conclusion from iterations 1–4 (as summarized
   above). Quote the offending lines.
2. **Actionability audit:** which instructions would an autonomous agent be UNABLE to
   execute as written (unmeasurable, circular, requiring information it can't get)?
   Rewrite the three worst offenders.
3. **Omission audit:** what did iterations 1–4 establish that the guide fails to
   capture? What do presentation experts know that the whole loop still missed —
   e.g., anything from Doumont's actual delivery guidance, poster/handout distinctions,
   Q&A/backup-slide strategy, accessibility, non-native-English audiences?
4. **Failure-mode simulation:** simulate the guide against three future scenarios and
   report where it breaks: (a) 'make me 5 slides for a 10-min department seminar next
   week from the powder-doser repo'; (b) 'review my draft deck for the TMS 2027 talk'
   (a deck the agent has never seen, on CALPHAD work in a private repo); (c) 'add two
   slides on last month's results to my existing group-meeting deck while I'm at a
   conference' (no PI availability — the brief-contract gate cannot be satisfied).
5. **Verdict:** is this guide ready to be the lab's standing instruction for
   agent-generated slides? State the minimum changes for a yes.
