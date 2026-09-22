# Iteration 4 of 5: produce the calibrated, deliverable critique of the PI's presented deck

## Where we are in the loop
Iterations 1–3 (adversarial critique → literature grounding → rubric stress-test) have
produced: defeasible design rules with purpose/default/exception/test structure; a
stage-gated generation pipeline with PI-judgment gates; evidence-tier gradings; and a
PR-style critique-batching model (release blockers unlimited-but-rare → max 3
high-impact changes → max 3 clarifying questions → one proposed patch set → collapsed
optional-polish checklist → a preserve list; every item with observation, consequence,
proposed patch, acceptance test, and action semantics: blocker/question/recommendation/
optional).

## Task
Apply that batching model to the ACTUAL presented deck (28 slides, attached as contact
sheets `presented-sheet-00..06.png`, plus `video-sample-frames.png` showing frames from
the embedded screen recordings). Produce the review exactly as it should be delivered to
the PI — this both (a) gives the PI immediately usable feedback on the talk he just
gave, for the next time he gives it, and (b) serves as the calibration example for my
future critique mode.

Context you should use:
- Talk: "Agentic Lifestyles in the Era of AI: Autonomous Research Workflows and Insights
  from the Vertical Cloud Lab" (CNMS 2026, already delivered; the review targets future
  re-delivery, e.g., other conferences/seminars).
- Abstract promises: successes AND challenges; three applications (alloy SDL, powder
  doser, tensegrity SDL); GitHub-integrated multi-agent workflows; Edison Scientific and
  cloud compute as securely-accessed external resources.
- Deck structure: 1 title; 2–3 Wizard-of-Claude hook ("I am toto" framing); 4–8 vertical
  timeline eras w/ per-era demo recordings; 9–13 constant headline "In 2026+, workflows
  are increasingly multi-agent and multi-tool" over changing evidence (timeline recap /
  atomizer + printed part / $200 doser CAD / glovebox video / tensegrity prints);
  14 abstract-list w/ dimmed emphasis; 15–17 full-bleed recordings (lit-search repo, HPC
  2FA/TOTP Copilot run, BO prompt thread); 18–26 robotic-control: native GitHub threads
  (lights-on 2m3s; color-sensor pickup 39m46s; dose 1g 0.9972g; lab-tour demo →
  MongoDB Atlas; YouTube Studio livestreams; QR moment at 26); 27 full-screen video;
  28 close (logos + collaborator video thumbnail + QR).
- Known facts from earlier iterations you may rely on: slides 10–13's evidence shows
  outcomes but not visibly "multi-agent/multi-tool"; the deck shows activity more than
  measured research gain; agent self-reports often stand in for verification even
  though the corpus contains external verification artifacts (blind-test key photo,
  scale telemetry, collaborator verdicts); $200-vs-$1500 on slide 11 lacks visible
  basis; slides 20–21 are portrait videos on mostly-empty dark canvases; slide 26
  wraps a QR in a Google homepage; slide 27 projects black outside slideshow; slide 28's
  call-to-action is ambiguous; timeline labels are categories not conclusions;
  "challenges" promised in the abstract have no dedicated beat (the corpus has strong
  failure→guardrail material: 'kind of scary… scraped the pipette' → CLAUDE.md rules).
- Doumont feedback norms: state observations as facts about the artifact/experience,
  future-oriented suggestions, no reproaches, no interpretations of intent.

## Requirements
1. Full review in the exact deliverable format (executive block ≤120 words; then the
   batched items with all fields; then the preserve list).
2. Respect the max-3 high-impact cap — choosing WHICH three matters; show your ranking
   rationale (audience benefit ÷ rework cost) for the top 6 candidates and why three
   lost.
3. Write acceptance tests that are actually checkable by the agent (rendered-image
   checks, five-second tests with named pass criteria, terminology audits).
4. Flag anything in my 'known facts' list above that you REJECT as a review item (too
   speculative, wrong altitude, or delivery-dependent) — the calibration value is as
   much in what a good reviewer leaves OUT.
5. End with a transferable one-page 'how to review a hand-made deck' checklist the
   agent can reuse, including the two-pass order (narrative/evidence before visual
   polish) and the closure mechanism (accept/decline/defer semantics).
