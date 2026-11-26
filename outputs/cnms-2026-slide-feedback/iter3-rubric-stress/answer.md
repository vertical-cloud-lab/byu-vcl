## Bottom line

The rubric is much stronger as a set of **default constraints**, but several rules are written as absolutes. That will make the agent optimize visible slide properties while missing the talk’s real objective: controlling what an expert audience infers, in sequence, under a fixed time budget.

The largest concrete problems are in the redesigns:

- **A mislabels the test as double-blind and does not visibly prove 18/18.** The specified evidence supports agent blinding and a favorable human verdict, but not double blinding, the denominator, or the scoring protocol.
- **B contains an unresolved numerical conflict.** The supplied GitHub crop reports **0.9972 g**, while the redesign specifies **0.9956 g**. Until provenance establishes that these are different trials, this is a release-blocking factual problem. A tolerance of ±5 mg is also an acceptance criterion, not measurement uncertainty.
- **C does not prove “drop-tested.”** The prompt, generated plate preview, and photograph establish a prompt-to-artifact chain. They do not establish that a valid Bayesian optimization campaign was completed or that the specimens were drop-tested.

## 1. Breaking rules 1–8

| Rule | Realistic counterexample in this talk | Why literal compliance makes the talk worse | Amendment |
|---|---|---|---|
| **1. One communicative job; assertion–evidence for analytic claims** | A decisive workflow slide must show prompt → physical action → independent check together. Splitting those into three “one-job” slides makes the audience retain the links across slide boundaries. | “One job” gets mistaken for “one content type.” The evidentiary chain is the job, and separating it can weaken the inference. A Wizard-of-Oz callback may also intentionally combine reveal and interpretation. | **One intended audience inference per slide or build**, with as many linked elements as that inference requires. Require assertion–evidence only when the assertion is meant to be accepted as true on that beat. Permit synthesis, comparison, reveal, and callback forms. |
| **2. Native artifacts; never retype** | A long GitHub comment contains one decisive sentence, but even a tight crop is too wide or low-resolution for the room. | Pixel fidelity defeats legibility. Iteration 2 already found that clarity and annotation, not perceived authenticity, are the defensible benefits. Screenshots can also preserve distracting usernames, timestamps, and inaccessible contrast. | Preserve **provenance and wording**, not necessarily pixels. Permit a verified verbatim transcription when the native crop cannot pass room-legibility checks. Pair it with a small source thumbnail, link, or source note; distinguish transcription from paraphrase. Never silently reconstruct plots or measurements. |
| **3. Target ≤20 projected words/minute** | An expert audience sees a persistent axis label, material name, and equation for 90 seconds while the PI explains a plot. Counting every visible token makes the slide fail despite low incremental reading demand. Conversely, a nearly wordless dense CAD or telemetry plot can pass while being impossible to parse. | Words per minute does not measure graphical decoding, and exposure duration is ambiguous for builds and persistent labels. It can reward deleting necessary scientific labels. | Compute **new, audience-directed readable words per exposure interval**, excluding clearly subordinate provenance and already-read persistent labels. Add a separate visual-complexity check: number of focal regions, unfamiliar encodings, and required comparisons. Treat 20 wpm as a rehearsal trigger, not a release threshold. |
| **4. Constant-skeleton emphasis builds** | Three duplicated glovebox slides dim two panels at a time, although experts can understand the three-step chain immediately. | The build consumes advances, lengthens dwell time, prevents backward comparison, and can look mechanically repetitive. Dimming may make contextual evidence unreadable. | Use a build only when order, suspense, or correspondence matters and rehearsal shows that simultaneous display overloads attention. Otherwise prefer a static annotated chain or small multiples. Preserve context at readable contrast; avoid automatic duplication when one reveal or pointer suffices. |
| **5. Rehearsal timing; never append new slides** | Backup methods, provenance, troubleshooting, and demo-failure slides belong after the closing slide. A late-breaking result may also be safest as an explicitly optional module at a section boundary. | “Never appended” incorrectly bans a useful appendix and encourages invasive restructuring shortly before delivery. Timing cannot be finalized before the narrative and delivery mode exist. | Classify every slide as **core, optional module, backup, or provenance**. Core additions must be placed at their causal/narrative location. Optional modules need defined insertion and cut points. Backup material may be appended after a clear end marker. Rehearse the core path and each optional path. |
| **6. Match the host visual system** | The host deck’s existing quote treatment is document-like or has undersized labels. Matching it exactly reproduces the defect. A safety warning or evidence-status distinction may require a new semantic color. | Style imitation can outrank legibility, accessibility, or meaning. Because the agent cannot edit masters, forced matching may also produce brittle approximations. | Match the host’s **stable tokens and semantic conventions**, not its mistakes. Allow bounded deviations for legibility, accessibility, new evidence states, and technical limitations. Record each new token and reuse it consistently; ask the PI before introducing a conspicuous motif. |
| **7. Mechanical and five-second release gates** | An off-slide object is intentionally staged for an animation, or a transition slide is deliberately ambiguous for two seconds before a reveal. A dense expert plot cannot communicate its conclusion in five seconds but works with a 45-second explanation. | The gate produces false failures and may delete intentional staging. A five-second topic/focal-point test is not a validated comprehension test and is unsuitable for every slide role. | Separate **technical integrity gates** from **role-specific rhetorical checks**. Permit declared off-canvas animation assets. Test a hook for orientation, a claim slide for claim and focal evidence, a demo for cue visibility, and an expert plot for entry point and encoding, not full comprehension. Also test on the actual presentation computer and web/offline fallback path. |
| **8. Evidence type, comparator, n, uncertainty on claim slides** | A singular workflow demonstration has no meaningful sample size or comparator. Putting “n=1, anecdote, no comparator” on every step consumes the slide and can falsely make a case study look like a statistical study. External verification may not yet exist for an exploratory result. | Uniform metadata burdens weak and strong claims alike. It confuses tolerance with uncertainty and absence of evidence with evidence of absence. | Use a **claim-dependent evidence schema**. Quantitative performance claims require unit, denominator, comparator where relevant, variability/uncertainty, and scoring method. Singular demonstrations require provenance, operator, observation versus inference, and replication status. If external verification is absent, narrow the claim and label it unverified; do not imply that every self-report can be paired. Put secondary detail in notes or a provenance appendix when it need not be read live. |

The general repair is: every rule should state its **purpose, default, exception condition, and test**. Otherwise the coding agent can satisfy the syntax while violating the purpose.

## 2. Order-of-operations audit

### Stage-gated pipeline

| Stage | Agent work and decision point | Binding rules | Required PI judgment |
|---|---|---|---|
| **0. Brief contract** | Record audience, outcome, through-line, duration, delivery mode, constraints, and canonical style source. Define what counts as success. | 5, 6; proposed cohesion rules | **Required.** Audience intent and the talk’s desired final inference cannot be recovered reliably from slide pixels. |
| **1. Evidence inventory** | Index comments, images, plots, videos, and existing slides. Record source, date, actor, measurement origin, and what each artifact does and does not establish. Flag conflicts such as 0.9972 versus 0.9956 g. | 2, 8 | PI or domain owner resolves factual conflicts, embargoes, authorship, and whether evidence is strong enough for public claims. |
| **2. Claim and beat selection** | Build a claim–evidence ledger. For each candidate beat: intended audience inference, evidence strength, novelty relative to the current deck, and cut priority. Reject redundant examples before layout. | 1, 3, 5, 8 | **Required.** PI chooses which scientific claims and examples represent the work, and which nuance cannot be cut. |
| **3. Narrative placement** | Place beats in the causal and rhetorical arc. Mark setup/payoff pairs, Wizard-of-Oz callbacks, transitions, optional modules, and backups. Generate a text storyboard before slides. | 1, 5 plus cohesion rules | **Required approval of the storyboard.** This is where authorship and delivery intent matter most. |
| **4. Form selection** | Choose claim slide, process chain, comparison, demo cue, hook, transition, or callback. Decide static versus build and what the speaker says that the slide does not. Estimate dwell time and new-word load. | 1, 3, 4, 8 | PI confirms delivery-dependent choices: silent reading interval, reveal timing, live demo versus recording, and narration. |
| **5. Artifact preparation** | Crop decisive regions, mask irrelevant chrome, annotate non-destructively, create verified transcriptions only when needed, and retain source mapping. | 2, 3, 8 | Spot approval only for sensitive redaction, ambiguous crops, or transcription/paraphrase choices. |
| **6. Layout and style extension** | Apply deck tokens, grids, motif semantics, type hierarchy, and room-legible sizing. Prefer native deck layouts when reliable; use offline generation where automation is more deterministic. | 3, 4, 6 | PI decides only conspicuous style deviations or new motifs. The agent should not ask about routine alignment. |
| **7. Render and technical QA** | Inspect rendered images, object bounds, font substitution, contrast, video playback, links, animations, aspect ratio, presenter notes, and fallback media. Test both PowerPoint-for-web and the actual delivery route when relevant. | 7 | PI is needed for acceptance of intentional exceptions and to confirm the delivery machine/path. |
| **8. Rehearsal and rhetorical QA** | Rehearse with timings. Check reading intervals, narration redundancy, transitions, expert-level detail, and whether each callback lands. Cut using the pre-ranked list. | 1, 3, 4, 5, 7 | **Required.** Timing and emphasis are properties of the performance, not the file. |
| **9. Packaging** | Produce core deck, backup section, media bundle, PDF fallback, source/provenance map, and change summary. Freeze a release candidate. | 5, 7, 8 | PI signs off on final claims, cut path, and public/private content. |

This pipeline needs two loops, not one: evidence conflicts return to stages 1–2; failed rehearsal returns to stages 2–6. Visual QA should not be used to patch a bad narrative.

### Minimal questions before generation

The agent should ask these as one compact brief, not a long interview:

1. **What should this audience believe, understand, or do when the talk ends, in one sentence?**
2. **Who is in the room, what can they already be assumed to know, and what skepticism should the talk answer?**
3. **What is the hard speaking time and delivery mode:** live demo, recording, builds, and offline fallback?
4. **Which existing beats are mandatory, expendable, confidential, or scientifically non-negotiable?**
5. **Which deck/version is the canonical visual and narrative reference, and how much deviation is acceptable?**
6. **What evidentiary wording is acceptable for case studies versus validated performance claims, and who resolves factual disputes?**

If the PI answers only three, require 1, 3, and 4. The agent can propose defaults for the rest, but should display them before committing to a storyboard.

## 3. Adversarial review of A, B, and C

The word counts below are **lower bounds** from the specified headline and key excerpts. They exclude usernames, interface chrome, evidence labels, annotations, and text incidentally visible in photographs. Projected rate is `visible words / exposure minutes`; actual audience demand could therefore be higher. The 20 wpm value is used as the rubric’s trigger, not as a validated pass/fail threshold.

### A. Blind test

**One message:** The agent’s classifications agreed perfectly with a human-held hidden key in one documented test.

**Does the evidence prove the assertion?** No, not as written.

- “The order … will be known to me and not to you” establishes that the **agent was blinded to the order**. It does not establish double blinding. The student appears to know or control the key, so “double-blind” is at best unproven and likely incorrect.
- The verdict “it seems Claude got the true key correct” supports agreement with the key, but the specified panels do not visibly establish **18/18**, what the 18 units were, how they relate to 90 drops, or whether a decision rule was preregistered.
- A photograph of a handwritten key is useful provenance only if the audience can connect it to the predictions and scoring. A key plus a favorable sentence is not itself a confusion matrix or auditable match.
- “Independent validation” is too strong unless the student was independent of development and the scoring process prevented post hoc changes. “Human-held blinded key” is the directly supported description.

**Reading load:** 35 core words. That is ~105 wpm at 20 seconds, 70 at 30 seconds, 47 at 45 seconds, and 35 at 60 seconds. It needs **105 seconds** to meet 20 wpm literally. UI text will increase those values. More important, two simultaneous evidence panels create competing reading paths.

**Predicted failure modes:** epistemic overclaim; audience confusion over 18 analyses versus 90 drops; illegible handwriting; the word “undergrad” becoming the rhetorical focus rather than the blinding protocol; spoken repetition of the visible quotes.

**Concrete improvement:** Replace the headline with **“With the drop order hidden, the agent matched the held-out key: 18/18.”** Show three linked objects: a very short setup excerpt, the time-stamped agent prediction record or hash if available, and a compact 18-row match strip/confusion table reconstructed directly from the records with a source note. Label it **“single blinded evaluation; human-held key.”** If the prediction record or denominator cannot be shown, remove 18/18 from the headline. Let the audience read the setup silently; narration should explain the safeguard and its limitation rather than repeat it.

### B. Glovebox milestone

**One message:** A short remote instruction initiated closed-loop physical dosing inside the glovebox and the measured dose landed within the stated tolerance.

That is stronger and more scientifically useful than “one GitHub comment dosed,” which assigns agency to a comment and foregrounds the interface rather than the remote-control capability.

**Does the evidence prove the assertion?** Not yet.

- The command and video still can show request and apparatus context, but a still does not prove that the reported measurement came from that run.
- The agent banner is an **agent self-report**. The collaborator’s “worked” verdict verifies successful operation at a broad level, not the exact mass.
- The supplied crop in `/workspace/crop-dose1g.png` reports **0.9972 g**, “within the ±0.005 g tolerance,” whereas this redesign specifies **0.9956 g (−4.4 mg)**. That 1.6 mg discrepancy must be traced to distinct run IDs/timestamps or corrected before use.
- “±5 mg” is a target tolerance, not instrument uncertainty. Evidence transparency requires scale resolution/calibration or uncertainty separately if a metrological claim is intended.
- The panels need explicit evidence that the apparatus is in the University of Utah glovebox if that location remains in the assertion.

**Reading load:** At least 35 core words if both setup and collaborator verdict are shown: the same lower-bound rates as A. Three separate builds reduce simultaneous load, but at 20 wpm each build still needs roughly three seconds per newly shown word. Duplicating the full slide three times is unnecessary if a single progressive reveal or pointer works.

**Predicted failure modes:** release-blocking number conflict; tolerance presented as uncertainty; self-report mistaken for measurement; location asserted but not evidenced; three-slide build feeling slow after related examples already establish remote action.

**Concrete improvement:** First reconcile the trial. Then use **“A remote command closed the loop on a 1 g glovebox dose.”** Show (1) the cropped command, (2) a still labeled with verified site and run timestamp, and (3) a large native scale/telemetry readout tied to the same run. Beneath the readout distinguish **target: 1.0000 g; observed: [verified value]; error: [derived value]; acceptance band: ±0.005 g; measurement uncertainty: not reported**. Put the human verdict in notes unless it validates that exact run.

### C. Bayesian optimization dictated in plain English

**One message:** Conversational constraints were converted into a generated build-plate plan and physical specimens.

**Does the evidence prove the assertion?** Only partially.

- The prompt proves that constraints were expressed conversationally.
- The preview proves that code produced a plate representation. It does **not by itself** prove that the Bayesian optimization logic was correct, that the selected candidates came from a fitted optimizer, or that the complete campaign ran.
- The plate photograph can prove printing if specimen identities and geometry match the preview.
- None of the specified evidence proves **drop-testing**. A drop-test photograph, telemetry plot, result table, or linked specimen ID is needed.
- “Campaign” may imply multiple iterative rounds. The quoted prompt explicitly says “single batch” and “one iteration,” so the headline risks inflating a constrained pilot into a campaign.

**Reading load:** At least 26 core words: ~78 wpm at 20 seconds, 52 at 30 seconds, 35 at 45 seconds, and 26 at 60 seconds. Literal 20 wpm requires ~78 seconds. This understates the load because the full GitHub comment shown in the existing deck is much longer. Three highlighted clauses inside a full comment still invite experts to read the surrounding text.

**Predicted failure modes:** claim outruns evidence; “Bayesian optimization” becomes an unverified label; full-comment crop recreates the document-slide problem; correspondence between preview and photo is visually ambiguous; expertise reversal if elementary workflow explanation crowds out the variables/objective experts want.

**Concrete improvement:** Narrow the assertion to **“Plain-language constraints became a build-plate plan, then printed specimens.”** Crop each requested clause separately or add three concise callouts without retaining the full comment. Use matching specimen numbers/colors on the generated preview and physical photograph. If “Bayesian optimization” is central, add a compact provenance line naming the selection method and objective. If “drop-tested” is retained, replace one panel or add a subsequent slide with a native drop-test result linked by specimen ID.

### Redesign ranking

1. **A has the highest potential** because blinding addresses a central credibility objection, but its current wording is epistemically unsafe.
2. **C has the clearest visual transformation** from instruction to physical artifact, but the assertion must stop at what the panels establish or add test evidence.
3. **B can be strong once reconciled**, but the number conflict blocks publication and the message currently overlaps other remote-action examples such as the lights-on and robot-pickup sequences visible in the supplied presented-slide sheet.

## 4. Critique-delivery protocol

The six steps are directionally good, but they optimize politeness and defensibility more than action. Missing elements:

1. **Correctness and release risk before aesthetics.** A wrong mass, unsupported claim, broken video, or unreadable key must outrank structural praise.
2. **A shared review scope.** Ask whether the PI wants a release audit, narrative review, visual polish, or exploratory alternatives. Otherwise useful comments may be out of phase with the deck.
3. **An acceptance test.** Each suggestion should say how to tell whether the fix worked: “At room-scale render, the observed mass and tolerance are distinguishable in five seconds,” not merely “enlarge the number.”
4. **A distinction between blocker, question, recommendation, and optional idea.** Code review succeeds partly because comments have action semantics.
5. **Dependency awareness.** One narrative change can invalidate five cosmetic comments. Review high-level structure before local layout.
6. **A closure mechanism.** Suggestions need owner/status: accept, decline, defer, or needs PI input. A menu without closure becomes a graveyard.
7. **Delivery context capture.** Link every narration-dependent comment to the notes or rehearsal timestamp. Do not leave “maybe the speaker explains this” unresolved.
8. **No mandatory praise preamble.** Accurate positive observations are useful because they identify patterns to preserve. Formulaic praise before a blocker wastes attention and can feel tactical.

### Actionable batching model

Use a PR-style review with one short executive block and attached mockups:

- **Release blockers, unlimited but rare:** factual conflict, unsupported public claim, privacy/licensing issue, broken media, or rendering failure. Each gets evidence, owner, and acceptance test.
- **High-impact changes, maximum three per review:** narrative placement, redundant example, missing claim–evidence link, or unreadable central artifact. Rank by expected audience benefit divided by rework cost.
- **Clarifying questions, maximum three:** only questions whose answers change the recommendation. Put them before dependent edits.
- **One proposed patch set:** a storyboard move, rewritten assertion, or one-slide mockup. Group mutually dependent changes together rather than scattering comments across slides.
- **Optional polish:** collapsed into a separate checklist; never mix it with blockers.
- **Preserve list:** name two or three deck patterns the agent will not disturb. This is more useful than generic praise.

Every item should have: **ID, slide(s), type, observation, consequence, proposed patch, effort estimate, confidence, delivery dependency, acceptance test, and status**. Review in two passes: first narrative/evidence, then visual/mechanical polish after structural decisions are accepted. A busy PI should be able to respond with `accept H1/H3, decline H2, answer Q1`.

## 5. Checkable deck-level cohesiveness rules

### C1. Write a deck contract

Before slide generation, record:

- one-sentence audience outcome;
- opening question or tension;
- 3–5 section functions;
- closing answer;
- the role of the Wizard-of-Oz frame.

**Self-test:** Every core slide maps to one section function and advances the outcome. Unmapped slides are cut, moved to backup, or explicitly justified as pacing/transition beats.

### C2. Maintain a claim–evidence–payoff ledger

For every example, track setup, claim, evidence, limitation, and later payoff/callback.

**Self-test:** No claim appears before the minimum setup needed to understand it; no evidence appears without a nearby statement of why it matters; no promised demonstration or callback remains unresolved by the closing section.

### C3. Give motifs stable semantics

A recurring motif must mean the same thing each time. For example, curtain imagery could mean concealed human work, a GitHub card could mean instruction/provenance, and a colored outline could mean external verification.

**Self-test:** Generate a motif inventory from slide thumbnails. Flag one-off decorative motifs, semantic reuse with conflicting meanings, and motifs absent for more than one full section without an intentional reintroduction. New motifs require a documented purpose.

### C4. Make repeated examples advance state

Remote lights, robot pickup, dosing, and blind testing cannot all mean merely “the agent controlled hardware.” Assign a progression such as **observe → act → close the measurement loop → withstand blinded evaluation**.

**Self-test:** Write the “new capability or inference” beside each example. If two adjacent examples have the same answer, combine one into a montage, cut one, or use the second to introduce a limitation rather than another success.

### C5. Use explicit bridges at section boundaries

Each boundary should close the previous question and open the next: “Remote action is possible; can we trust the result?”

**Self-test:** Read only the last assertion of each section and the first assertion of the next. They should form a coherent causal or argumentative chain without presenter improvisation.

### C6. Preserve entity and terminology identity

Use stable names and visual identifiers for the agent, collaborators, repositories, instruments, specimens, and metrics. Do not alternate among “Claude,” “agent,” “control agent,” and “bot” where the distinction matters.

**Self-test:** Run a terminology audit and an entity-color/icon audit. Every synonym is either normalized or intentionally defined; the same color is not used for unrelated actors or evidence states.

### C7. Plan callbacks as paired beats

For the Wizard-of-Oz arc, specify the opening expectation, each piece of contrary evidence, the reveal, and the final reinterpretation. A callback must change meaning, not merely repeat imagery.

**Self-test:** Every callback identifies its source slide and the new inference it adds. Reject callbacks that only reproduce the earlier motif. The close should answer the opening tension in one sentence visible in the storyboard.

### C8. Control pacing across the whole deck

Alternate dense analytic beats with demonstrations, images, transitions, or pauses. Do not place four screenshot-heavy slides consecutively merely because they share a source.

**Self-test:** Plot estimated dwell time, new readable words, visual complexity, and slide role across slide order. Flag sustained peaks, abrupt section-length imbalance, and long runs of the same slide form. Validate the flags in rehearsal rather than imposing universal thresholds.

### C9. Separate the live story from the document layer

The live deck should optimize projection and narration; detailed provenance can live in notes, linked repository documentation, or backup slides.

**Self-test:** Every visible detail must serve the live inference. Every public quantitative claim must still have traceable provenance somewhere in the package. Export both a presentation path and a browsable handout only if the PI needs both; do not force one file to perform both jobs.

### C10. Perform three global reviews

1. **Thumbnail review:** focal rhythm, motif recurrence, section boundaries, and style discontinuities.
2. **Assertion-only review:** read headlines in order; they must form the talk’s argument without body content.
3. **Evidence-only review:** hide assertions and ask whether the artifacts are traceable, nonredundant, and correctly matched to claims.

A fourth **notes-only rehearsal review** checks that narration extends rather than reads projected text.

## Limitations

This audit uses the supplied redesign specifications and five rendered workspace images, including the visible 0.9972 g GitHub crop and slide-contact sheets. I did not have the source PowerPoint, speaker notes, rehearsal timings, complete GitHub threads, exact A/C assets, or the referenced `docs/cnms-2026-slide-style-analysis.md` file. Therefore:

- reading-load values are lower-bound scenario calculations, not audience measurements;
- independence, preregistration, trial identity, scale calibration, and specimen correspondence could not be verified;
- narrative placement and redundancy judgments remain provisional until the full deck and delivery are reviewed.

## Discretionary analytical decisions

- Treated each rubric item as a defeasible default rather than assuming universal compliance was desirable.
- Used one intended **audience inference** as the operational definition of a slide’s communicative job.
- Counted only specified headline/excerpt words for reading-load estimates and excluded incidental interface text, making the estimates explicit lower bounds.
- Evaluated projected word rates at 20, 30, 45, and 60 seconds because no rehearsal dwell times were supplied.
- Treated the rubric’s 20 wpm target as a diagnostic trigger rather than a validated release cutoff.
- Ranked factual conflicts and unsupported claims above style and layout concerns.
- Recommended narrowing assertions when evidence was missing rather than assuming unavailable source material would validate them.
- Limited high-impact critique batches to three items to reduce review burden; this is a workflow judgment, not an empirically established threshold.
- Proposed role-specific cold-viewer checks rather than applying the same five-second criterion to every slide type.