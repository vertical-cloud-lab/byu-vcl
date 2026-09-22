# Agent guide: generating and reviewing presentation slides for this lab

Synthesized 2026-08-13 (PR #176) from: the CNMS 2026 deck post-mortem
([cnms-2026-slide-style-analysis.md](cnms-2026-slide-style-analysis.md)), **five Edison
Scientific critique iterations** (queries, raw task JSON, and answers under
[`outputs/cnms-2026-slide-feedback/`](../outputs/cnms-2026-slide-feedback/)), and
Jean-luc Doumont's materials (three laws; "with each slide, convey one message — state
it verbally, develop it visually"; the Nature Masterclass exemplar decks; *Effective
oral presentations* summary). Iteration 5 refereed a draft of this guide; its required
changes are folded in below. This is the operating document future sessions should load
before touching a deck.

## 0. The one-paragraph lesson

For CNMS 2026 I generated 14 verbatim-quote text slides; all 14 were cut. The corpus
mining and curation were used — the PI presented the same beats as **native artifacts**
(screen recordings of the real GitHub threads, phone video of hardware responding) —
but my rendering failed: appended as a trailing block instead of placed in the
narrative, redundant with beats already integrated, text-collision defects, and
document-styled where the deck's language is evidence-styled. Slide generation is a
pipeline with human judgment gated in, not a rendering step at the end.

## 1. Authority and operating modes (read first)

Roles (one person may hold several — in this lab, usually the PI):
**presenter** (owns delivery/timing) · **claim owner** (attests scientific
interpretation) · **data owner** (resolves data/access questions) · **release
approver** (accepts confidentiality/licensing/public wording).

Modes:
- `APPROVED` — the relevant owner accepted the required decisions; only in this mode
  may the canonical deck be changed or content released publicly.
- `PROVISIONAL` — owner unavailable or silent: the agent may produce a **reversible,
  watermarked review artifact** (duplicate deck or branch, never the canonical file)
  under the conservative defaults in §2. **Silence never converts PROVISIONAL to
  APPROVED.**
- `BLOCKED` — evidence, access, confidentiality, or claim authority is missing; no
  release artifact is produced; say so and stop.

**No human approval converts unresolved contradictory evidence into resolved
evidence** (see the conflict rule in §3 stage 2).

## 2. Before generating anything: the brief

Ask (one compact message, not an interview). Minimum viable: #1, #3, #4.

1. What should this audience believe/do at the end, in one sentence?
2. Who is in the room; what skepticism should the talk answer? (Include language
   proficiency — see §8 accommodations.)
3. Hard speaking time (incl. Q&A allocation) and delivery mode (live demo? recording?
   offline fallback?).
4. Which beats are mandatory / expendable / confidential / non-negotiable?
5. Which deck is the canonical style reference; how much deviation is acceptable?
6. What evidentiary wording is acceptable (case study vs. validated performance claim)?

**If unanswered by work-start time**, create a visible `ASSUMPTIONS` block and default
to: mixed technical audience; internal-only draft; no new performance/priority/safety/
generality claims; no confidential material; prerecorded media + static fallback;
latest approved deck as style reference; all uncertain beats optional. Proceed only to
a watermarked review draft (`PROVISIONAL`).

## 3. The pipeline (stage → binding rules → judgment gate)

1. **Brief contract** (§2) — *gate: presenter/claim owner (PROVISIONAL path exists).*
2. **Evidence inventory** — index artifacts with source, date, actor, run ID, and what
   each does and does NOT establish. **Conflict rule:** for conflicting values, record
   path, commit, timestamp, run ID, unit, processing step; determine whether they
   describe the same run and metric. Same run and irreconcilable → mark `CONFLICTED`
   and exclude from the release deck. Different runs → label separately; combine only
   as an explicit, labeled cross-run comparison. **Never present artifacts from
   different runs as one coherent event** (the 0.9972 g / 0.9956 g trap from iter3).
   A human may supply context but may not erase a discrepancy by preference.
3. **Claim/beat selection** — claim–evidence ledger; reject beats redundant with the
   existing deck BEFORE layout; assign cut priority. *Gate: claim owner picks
   representative claims.*
4. **Narrative placement** — text storyboard; setup/payoff pairs; callbacks; optional
   modules with insertion/cut points. **Release test for every new core slide: name
   its causal predecessor and successor in the storyboard; if either is absent,
   reclassify as backup or reject** (the appended-block lesson as a check, not a
   memory). *Gate: presenter approves storyboard.*
5. **Form selection** — claim slide / process chain / comparison / demo cue / hook /
   transition / callback; static vs. build; what the speaker says that the slide
   doesn't. *Gate: presenter confirms delivery-dependent choices.*
6. **Artifact preparation** — form comparison per evidence item: native crop vs.
   faithful redraw vs. derived plot vs. concise verified transcription — choose the
   form that best exposes the decisive evidence while retaining provenance (a source
   pointer travels with every panel). Never silently reconstruct plots or
   measurements.
7. **Layout & style extension** — host deck's stable tokens and semantic conventions,
   not its defects; bounded deviations for legibility/accessibility; new tokens
   documented and reused.
8. **Render & technical QA** — gates in §6.
9. **Rehearsal & rhetorical QA** — §7. *Gate: presenter (timing is a property of the
   performance, not the file).*
10. **Packaging** — core deck + Q&A-mapped backups + media bundle + provenance map +
    change summary + per-slide PNG proofs (PR-style triage) + PDF/static fallback.

Two loops: evidence conflicts → back to 2–3; failed rehearsal → back to 3–6. Never
patch a bad narrative with visual QA.

## 4. Design rules (defeasible defaults: purpose · default · exception · test)

Evidence labels: **[E]** empirical audience-learning evidence (Mayer/CTML
meta-analyses, signaling d≈0.38, coherence d≈0.86, contiguity d≈1.1, redundancy
d≈0.86, segmenting d≈0.79; assertion–evidence studies incl. nulls — full mapping with
citations in `outputs/cnms-2026-slide-feedback/iter2-literature/answer.md`; boundary
conditions: mostly student-learning contexts; expertise-reversal risk with expert
audiences). **[P]** production/reliability requirement. **[C]** craft default.
**[L]** lab-specific lesson from the CNMS post-mortem.

1. **[E] One focal inference per exposure state; one parent inference per build.**
   Analytic claims get a sentence assertion + visual evidence; demos get a
   what-to-watch-for cue; hooks/transitions may need neither. *Test:* name the
   inference; if you can't, the slide isn't ready.
2. **[C→E via clarity] Choose the evidence form deliberately; preserve provenance and
   wording, not necessarily pixels.** Native crops win when the interface IS the
   evidence (this lab's GitHub-thread beats); the benefit runs through *clarity and
   annotation*, not authenticity per se (truthiness effect failed replication).
   Verified transcription is allowed when crops can't reach room legibility — label
   it, keep a source thumbnail/pointer.
3. **[E] Manage reading load, not word count.** Formula: exposure interval = one
   static state between advances; reading load = newly revealed audience-readable
   words ÷ rehearsed dwell (minutes). ≈20 wpm is a rehearsal trigger, not a release
   gate. Without rehearsed dwell, report the word count and mark rate `UNKNOWN`.
   Complexity check besides words: focal regions, unfamiliar encodings, required
   comparisons. Quote slides: project the key phrase, audience reads silently,
   speaker *extends* — never reads.
4. **[E] Build by emphasis only when order/suspense/correspondence matters.** Constant
   skeleton, dim past, highlight current; static annotated chain or small multiples
   when experts can parse at once; dimmed context stays readable.
5. **[C] Time from rehearsal; classify every slide** core / optional module / backup /
   provenance; cut from a pre-ranked list. Backups live after a clear end marker with
   searchable titles + an index slide.
6. **[C] Match the host's stable tokens and semantics — not its defects.** Ask before
   introducing a conspicuous new motif.
7. **[P gates + C tests] Release QA** — see §6.
8. **[L/C] Claim-dependent evidence schema.** Quantitative: unit, denominator,
   comparator, variability, scoring method — never confuse acceptance tolerance
   (±5 mg) with measurement uncertainty. Singular demos: provenance, operator,
   observation vs. inference, replication status. Agent self-report is a report —
   pair it with external verification (scale telemetry, video, human-held key) or
   narrow the claim and label it unverified. Reserve "multi-agent" for ≥2
   identifiable agents/roles; "multi-tool" otherwise.

## 5. Deck-level cohesiveness rules (checkable)

- **C1 Deck contract:** outcome sentence, opening tension, 3–5 section functions,
  closing answer, role of the framing device. Every core slide maps to a function.
- **C2 Claim–evidence–payoff ledger:** no claim before its setup; no evidence without
  its "so what"; no unresolved promise at the close.
- **C3 Motif semantics:** each recurring motif means one thing; audit thumbnails for
  one-off decorations and conflicting reuse.
- **C4 Repeated examples must advance state** (observe → act → close the loop →
  survive blinded evaluation); same-answer neighbors get merged, cut, or repurposed
  as a limitation.
- **C5 Section bridges:** last assertion of section N + first of N+1 must chain.
- **C6 Entity/terminology identity:** stable names/identifiers; audit synonym drift.
- **C7 Callbacks change meaning,** never just repeat imagery.
- **C8 Pacing:** plot dwell × new-words × complexity × role across the deck; flag
  peaks and monotone runs; validate in rehearsal.
- **C9 Separate the live layer from the document layer.** Handouts get their own
  contract: standalone title/context, expanded captions, readable references,
  definitions, links, version/date, accessibility — never print-slides-with-notes.
  Posters are **out of scope** for this guide (self-paced, spatial medium).
- **C10 Three global reviews:** thumbnails (rhythm/motifs); **assertions-only over
  claim slides** (their headlines must argue the talk; hooks/transitions/demos are
  represented by their function and the sequence must still cohere); evidence-only
  (artifacts traceable, non-redundant, matched to claims). Plus a notes-only
  rehearsal check that narration extends rather than reads.

## 6. Release gates (mechanical)

| Gate | Required record | Failure consequence |
|---|---|---|
| Geometry/rendering | no text/object overlap; no leftover placeholders; no off-slide objects (unless declared animation staging); ≥3% margins; render every slide to PNG and inspect at 100%, 25% thumbnail, and simulated back-row when room geometry is known; no unintended near-black frames (>95% pixels <10/255 luminance) | Repair before release |
| Legibility/accessibility | decisive text ≥ ~24 pt equivalent after crop/scale; contrast ≥4.5:1 / 3:1; PowerPoint Accessibility Checker; reading order + unique titles; alt text or decorative flag; no color-only encoding; captions for video; meaningful link text. If a human cold-viewer or room geometry is unavailable, record `UNVERIFIED` — absence is not a pass | Repair or document approved exception |
| Scientific provenance | every number/quote/verdict → source path, commit/version, run ID, processing; provenance class (instrument / collaborator-judged / independently-analyzed / agent-reported); redaction state (public / redact / internal-only); OCR audit for tokens, emails, private URLs | Block affected claim |
| Delivery & Q&A | timed rehearsal; opening and close deliverable without slide dependence; 5–10 anticipated skeptical questions each mapped to a verbal answer + evidence source + optional backup; navigation back to close rehearsed; no backup introduces an unreviewed public claim | Keep as review draft |
| Technical fallback | media plays from the delivered file on the target machine, offline; start/pause/resume/skip test; static evidence-bearing poster frame behind every video; local copies; PDF fallback; QR decodes from a back-of-room-equivalent screenshot and destination verified | No live-demo dependency |

Cold-viewer checks are role-specific (hook → orientation; claim → claim + focal
evidence; demo → cue visibility; expert plot → entry point), with the pass criterion
named before testing; the five-second/80% form is a smoke test, not a validated
instrument.

## 7. Delivery-adjacent checks (Doumont)

The agent doesn't deliver, but the package must support delivery: extemporaneous
speech from a memorized outline (not wording); filler words out, silences in; the
opening sequence (attention getter → need → task → main message → preview) and close
(review → conclusion → elegant close) stated in notes; the four-step question
procedure (listen fully → repeat/rephrase for the room → think → answer briefly to
the whole audience) in the Q&A prep sheet. Feedback to the presenter about delivery
follows the fact-based, future-oriented protocol (§9).

## 8. Audience accommodations [C]

When the audience includes non-native English speakers (or on request): shorter
sentences, concrete verbs, acronyms expanded on first use, stable terminology,
specialized terms defined before use, deliberate pacing with pauses after dense
claims, captions on recorded speech, idiom/wordplay/culture-bound analogy avoided or
explained, key names/numbers/equations shown visually.

## 9. Reviewing a hand-made deck ("meaningful suggestions" mode)

Two passes: **narrative/evidence first**, visual polish only after structural
decisions land. Doumont feedback norms: observations as facts about the artifact and
my experience of it ("at 25% zoom the labels are unreadable to me"), future-oriented
proposals, no reproaches ("you should have"), no intent-guessing. Scope the review
first: release audit, narrative review, visual polish, or exploratory alternatives.

Batching (PR-style; every item: ID, slide, type, observation, consequence, proposed
patch, effort, confidence, delivery dependency, acceptance test, status):

1. **Release blockers** (factual conflict, unsupported public claim, broken media,
   privacy/licensing) — unlimited but rare; these outrank all aesthetics.
2. **≤3 high-impact changes**, ranked by audience benefit ÷ rework cost (show the
   ranking for transparency).
3. **≤3 clarifying questions** — only ones whose answers change a recommendation.
4. **One coherent patch set** (storyboard move, rewritten assertion, one-slide
   mockup) — not scattered edits.
5. **Optional polish** — collapsed checklist, never mixed with blockers.
6. **Preserve list** — 2–3 patterns that must not be disturbed.

Closure semantics: the owner replies `accept H1/H3, decline H2, answer Q1`; declined
items record a reason and don't reopen without new evidence; deferred items get an
owner and a trigger. Delivery-dependent observations say so explicitly and are
labeled `NOT ASSESSED` when notes/timings are unavailable — never inferred from
pixels. The full worked example (CNMS 2026 deck review with acceptance tests) is in
`outputs/cnms-2026-slide-feedback/iter4-critique-mode/answer.md`; the compact
checklist below is the reusable core.

### Two-pass checklist (compact)

**Pass 1 — narrative & evidence:** map every abstract/title promise to a slide (flag
narration-only promises) → per-section audience question; conclusion headlines on
evidence slides; cut same-function repeats → per-claim chain (task; agents/tools;
handoffs/boundaries; external check; result + uncertainty; research benefit or
"not yet measured") → challenges: failure → guardrail → retest status + judgment
gates → ending: one audience, one action, one payoff.

**Pass 2 — visual & delivery:** role-specific five-second tests with pre-named pass
criteria → rendered-image audit (clipping, contrast, size, empty canvas, chrome,
black frames, focal region, poster frames) → terminology/provenance audit
(multi-agent, verified, safe, autonomous, measured, cheaper — scope + evidence each)
→ media/venue preflight from the delivered file, offline.

## 10. Candidate evidence library (what to build slides FROM)

~418 agent-committed media files across the three public repos: camera stills
(`byu-vcl/wireless-color-sensor/`, `ot2-overhead-camera/`), CAD renders
(`tensegrity-optimization/cad/`, `powder-doser/design/`), BO plate previews
(`tensegrity-optimization/bo/`), drop-test figures (`data/drop-tests/`), dose
telemetry (`powder-doser/data/pid-dose/`), prior slide previews
(`tensegrity-optimization/presentation/`) — plus the full comment corpus
(`data/cnms-2026-corpus/`) from which any comment card can be re-rendered at chosen
zoom, and 18 screen recordings embedded in the CNMS deck. These are *candidates*: the
form comparison in §3 stage 6 decides how each is used. Every evidence panel traces
to path + commit + (hardware runs) run ID; group artifacts by run before composing.

## 11. Known mechanical constraints (PowerPoint for the web via automation)

See [cnms-2026-onedrive-access.md](cnms-2026-onedrive-access.md) for the full recipe.
Highlights: clipboard paste bypasses autocorrect (mandatory for verbatim text);
numeric Shape ribbon fields for exact sizes; ≈92.3 px/in mapping for
drag-positioning; slide masters are NOT editable in the web editor (python-pptx +
REST upload when the file is closed, or desktop PowerPoint); co-authoring works while
the owner has the deck open; verify persistence against the re-downloaded blob, and
verify *renders*, not just text.
