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
