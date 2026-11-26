# Iteration 3 of 5: stress-test a slide-generation rubric + adversarial review of three concrete slide redesigns

## Where we are in the loop
Iteration 1 (adversarial critique) reranked why my 14 generated quote slides were cut from
a materials-science PI's CNMS 2026 talk (redundancy with natively-integrated examples +
appended-prototype-block status + rendering defects, with document-like styling
contributory). Iteration 2 (literature review) graded my revised rules: Tier-1
evidence-backed = reading-load management (projected words/minute, not word caps),
assertion–evidence for analytic claims, progressive-emphasis builds, mechanical QA gates;
Tier-2 craft = native-artifact extraction (works via clarity/annotation, NOT authenticity
per se — truthiness effect failed replication), evidence-type transparency, visual-system
matching, rehearsal-based timing. Key added nuances: expertise-reversal risk for expert
audiences; for verbatim-quote slides, project the key phrase, let the audience read it
silently, then speak commentary that EXTENDS rather than reads it; stakeholders often
resist assertion–evidence because they want slides to double as documents.

## The rubric as it now stands (v3, post-literature)
1. One communicative job per slide; analytic claims get a sentence assertion + visual
   evidence; demos get what-to-watch-for cues; hooks/transitions may need neither.
2. Faithful extraction of native artifacts: crop to decisive region, enlarge key line to
   ≥24 pt equivalent, mask chrome, annotate — never re-type into styled text, never paste
   raw full-window screenshots.
3. Manage projected-words-per-minute (target ≲20 wpm incl. words inside screenshots);
   short keywords/labels over duplicated prose; one primary reading path.
4. Build sequences by holding a skeleton constant and shifting emphasis (dim past,
   highlight current); no added clutter/motion.
5. Time budget from rehearsal; deliver beats ranked with explicit cut priority; new
   slides go INTO the narrative where they belong, never as an appended trailing block.
6. Match the host deck's type scale, colors, motifs; extend motifs, don't add templates.
7. Release gates: no overlap, no leftover placeholders, no off-slide objects, margins,
   media plays, then rendered-image visual check, then five-second cold-viewer test
   (topic + focal point) — labeled as craft, not validated.
8. Evidence transparency on claim slides: type (measurement / independent validation /
   agent self-report / anecdote), comparator, n, uncertainty; pair agent self-reports
   with external verification.

## Additional operating context you should stress-test against
- The generator is an AI coding agent driving PowerPoint-for-the-web via headless
  browser automation (clipboard paste bypasses autocorrect; can set numeric sizes;
  CANNOT edit slide masters; layout gallery clickable; can also build decks offline via
  python-pptx and render-verify via LibreOffice).
- The corpus of native artifacts available: ~418 agent-committed media files across
  three public GitHub repos (camera stills, CAD renders, BO plate previews, drop-test
  figures, dose-telemetry plots, screenshots), plus full JSONL of every issue/PR comment
  (so any comment card can be re-rendered/screenshotted at chosen zoom), plus 18
  screen-recording videos already embedded in the PI's deck.
- Audience: expert scientific conference (materials science + AI-workflow curious).
- The PI's standing goals: (a) agent generates slides of his quality/style/cohesiveness
  for future talks; (b) agent makes meaningful improvement suggestions even on decks he
  makes by hand.

## The three concrete redesign specs to adversarially review

# Three concrete slide redesigns (applying the v2 rules)

Each redesign rebuilds one of my cut quote slides as an assertion–evidence slide made
from **native artifacts already in the corpus**, per the v2 operating rules
(`docs/cnms-2026-slide-style-analysis.md` §5). These are specs I could execute today
with the headless co-authoring pipeline + Pillow cropping; they are the concrete test
objects for Edison iteration 4.

## A. The blind test (was hidden slide 35 — the strongest beat the talk never used)

- **Assertion headline (≤12 words):** "An undergrad ran a double-blind test on the agent: 18/18"
- **Evidence panel 1 (left, ~45%):** crop of me-madsen's actual comment card
  (tensegrity#86, comment 5172717335), zoomed so "The order of these will be known to
  me and not to you" reads at ≥24 pt equivalent; GitHub chrome outside the card masked.
- **Evidence panel 2 (right, ~45%):** the photo of the handwritten key from the verdict
  comment (5209909579), with the student's line "By my review, it seems Claude got the
  true key correct." as the only added text.
- **Evidence-type note:** independent validation (human-held key), not agent self-report
  — the strongest epistemic artifact in the corpus.
- **What is dropped from my v1 slide:** the 60-word outcome paragraph, typed
  attribution block, date, comment ID (all live in the linked repo doc / notes).

## B. Glovebox milestone (was hidden slide 37)

- **Assertion:** "One GitHub comment dosed 0.9956 g inside a U. Utah glovebox"
- **Evidence:** three-beat left→right chain, all native: (1) crop of lbwinters's
  comment "weve loaded salt into the auger and we are ready…" (typo kept, in the real
  UI); (2) video still of the doser inside the glovebox (from the presented deck's own
  footage — media5); (3) crop of the agent reply banner + the "0.9956 g (−4.4 mg,
  inside ±5 mg)" line.
- **Emphasis build option:** same slide duplicated ×3, dimming all but the active beat.
- **Self-report pairing:** the number comes from the scale feedback in the agent log
  AND the collaborator's human verdict ("using Claude as the control agent worked!") —
  quote the human, not the bot, if one must be chosen.

## C. BO dictated in plain English (was hidden slide 39)

- **Assertion:** "A Bayesian optimization campaign, specified conversationally, became
  printed, drop-tested specimens"
- **Evidence:** (1) crop of the tensegrity#35 prompt with three clauses highlighted
  ("single batch", "human-in-the-loop, one iteration", "fit as many as you can onto the
  single build plate"); (2) the plate-preview PNG the generated script itself produced
  (bo/t3_prism_sobol_batch.py output — a native artifact of the code); (3) photo of the
  printed specimens on the plate (tensegrity#35 thread).
- **Why this beats my v1:** the middle artifact *is the generated code's output* — it
  proves code ran, not just that code was described.

## Critique-delivery protocol (for making suggestions on the PI's hand-made decks)

Derived from Doumont's feedback rules (Teaching-is-not-Learning lecture: facts, not
reproaches; future-oriented; no interpretations) + iteration-1's calibration:

1. **Lead with what the deck does well structurally** (it earns the trust that makes
   critique receivable — and identifies motifs to extend rather than replace).
2. **State observations as facts about my experience of the artifact**, never "you
   should have": "At 25% zoom the timeline labels are unreadable to me" not "labels are
   too small".
3. **Tie each suggestion to a named principle** (signal-to-noise, assertion–evidence
   link, redundancy) so it's checkable, not taste.
4. **Offer a concrete candidate fix** (a cropped image, a rewritten headline, a
   one-slide mockup) the author can accept/reject cheaply — the same way I hand PRs.
5. **Rank by expected impact and label confidence**, flagging which suggestions depend
   on delivery choices I can't observe (narration, dwell time).
6. **Respect authorship:** suggestions are a menu, not a diff to merge; a hand-made
   deck encodes intent I may not see (as the graveyard incident proves).


## Your tasks
1. **Break the rubric.** For each rule 1–8, construct at least one realistic scenario
   from THIS lab's context (conference talk about agentic materials-research workflows)
   where following the rule produces a worse slide or worse talk, and state how the rule
   should be amended to survive the counterexample.
2. **Order-of-operations audit:** the rubric is a list, but generation is a pipeline
   (content selection → narrative placement → layout → rendering → QA → delivery
   packaging). Propose the pipeline with decision points, and identify which rubric
   rules bind at which stage. Where does the PI's judgment HAVE to enter, and what is
   the minimal set of questions the agent should ask the PI before generating anything?
3. **Adversarially review redesigns A, B, C** against the rubric AND against the
   iteration-2 evidence: predicted failure modes, what each slide's ONE message is,
   whether the evidence shown actually proves the assertion stated, reading-load
   estimate, and one concrete improvement each.
4. **Critique-delivery protocol:** review the 6-step protocol at the end of the specs
   document. What's missing for the 'meaningful suggestions on hand-made decks' goal?
   How should suggestions be batched/prioritized so a busy PI acts on them (think: how
   code-review feedback gets actioned vs ignored)?
5. **The cohesiveness gap:** quality and style are covered by rules 1–8; COHESIVENESS
   (the through-line of a whole deck: motif recurrence, callback structure, narrative
   arcs like this talk's Wizard-of-Oz frame) is not. Propose concrete, checkable
   deck-level rules for cohesiveness that an agent could apply and self-test.
