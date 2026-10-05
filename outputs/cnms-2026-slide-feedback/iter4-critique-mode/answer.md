# Review for future delivery

## Executive block

The deck has a strong live-demo identity and a credible GitHub-to-hardware arc. Keep that character, but make the argument easier to verify. The main gap is a visible chain from claim to workflow to independently checked result to research benefit. Add one challenge-to-guardrail beat, convert the three applications into compact evidence cards, and end with one explicit audience action. Also preflight the media path: the captured slide 27 is entirely black. These changes preserve the talk’s energy while fulfilling the abstract’s promises of successes, challenges, three applications, multi-agent workflows, and securely accessed external resources. Broad restyling is not the next priority; the current visual language is serviceable once the evidence and ending are clear.

## Release blocker

### B1. Make slide 27 fail safely

- **Action semantics:** **Blocker**. Resolve before the deck is presented again.
- **Observation:** In the presented-deck capture, slide 27 is a completely black 16:9 frame. The contact sheets do not establish whether this came from projection mode, a video handoff, or the media itself.
- **Consequence:** A media-path failure immediately before the close creates an uncontrolled pause and can make the final demonstration look absent. The diagnosis is delivery-dependent; the visible failure state is not.
- **Proposed patch:** Either embed the video in the slide with a deliberate poster frame and local fallback, or remove slide 27 and launch the clip only from a tested local file. Put a static “what this demonstrates” frame behind the video so failure still leaves evidence on screen. Do not depend on a browser or network connection for this beat.
- **Acceptance test:**
  1. **Rendered-image check:** export all slides to PNG. Fail if any non-allowlisted slide has more than 95% of pixels at luminance below 10/255. Slide 27 must show a recognizable poster frame, a claim headline, and a fallback label.
  2. **Media preflight:** open the delivered file on the presentation machine with networking disabled; start, pause, resume, and advance from slide 27 three times. Pass only if all three runs show the first meaningful frame within two seconds and advancing reaches slide 28 without exposing the desktop or a browser.
  3. **Fallback test:** rename or temporarily remove the video asset. Pass only if slide 27 still communicates the intended result rather than displaying black or an error dialog.

## Three high-impact changes

### H1. Turn the three applications into claim-to-verification evidence cards

- **Action semantics:** **Recommendation**. Highest narrative/evidence priority.
- **Observation:** Slides 10–13 show the alloy, powder-doser, and tensegrity outcomes under the repeated claim “workflows are increasingly multi-agent and multi-tool,” but the images do not themselves identify the agents, tools, handoffs, or checks. Slides 15–25 later show GitHub threads, high-performance computing access, remote hardware, scale output, and MongoDB, but these artifacts are distributed across many screens. Several visible conclusions are agent-authored status reports. The available corpus also contains stronger external checks, including scale telemetry, a blind-test key photo, and collaborator verdicts.
- **Consequence:** A viewer can see that substantial activity occurred but cannot quickly reconstruct which system did what, what was independently checked, or what research gain followed. This weakens the deck’s central multi-agent claim even though relevant evidence exists.
- **Proposed patch:** Give each application one compact card using the same five-part grammar:
  1. **Research task**
  2. **Agents and tools**
  3. **Handoffs and secure resource access**
  4. **External check**
  5. **Measured result or bounded outcome**

  Use arrows only for documented handoffs. For example, the powder card can connect the native GitHub request, Claude, Tailscale/secure shell, controller, scale telemetry, and MongoDB, ending at the shown 0.9972 g result for a 1 g target. For alloy and tensegrity, use the blind-test key, collaborator verdict, or other external artifact only where its provenance and interpretation can be shown. If a research-gain metric was not collected, write “research gain not yet measured” rather than substituting task completion.
- **Acceptance test:**
  1. **Rendered-image check:** each of the three application cards must visibly contain all five labels above; each label must have at least one application-specific value. No card may use an agent’s prose as its only item under **External check**.
  2. **Five-second test, named pass criterion:** show each card for five seconds to a fresh reviewer who has not seen the talk, then hide it. Pass if the reviewer can name (a) the task, (b) at least two distinct agents/tools or one agent plus one external resource, and (c) the external check. Require all three answers on at least two of three cards.
  3. **Evidence audit:** for every number and verdict, record source, date/run identifier, and whether it is agent-reported, instrument-recorded, collaborator-judged, or independently analyzed. Pass only when every result has exactly one provenance class and a retrievable artifact.
  4. **Terminology audit:** reserve **multi-agent** for workflows with at least two identifiable agents or agent roles. Use **multi-tool** when only one agent is shown crossing tools. The headline and cards must not imply multi-agent operation where the artifact demonstrates only multi-tool use.

### H2. Add one explicit failure → guardrail → retest beat

- **Action semantics:** **Recommendation**.
- **Observation:** The abstract promises successes and challenges, while the presented sequence is dominated by successful outputs and completed tasks. There is no dedicated challenge beat. The source corpus contains a concrete failure account, “kind of scary… scraped the pipette,” followed by rules added to `CLAUDE.md`.
- **Consequence:** Without one bounded failure case, the talk leaves the audience without a usable model for supervising agents around physical systems. It also leaves an explicit abstract promise unfulfilled.
- **Proposed patch:** Replace one lower-information demo beat, preferably one of the portrait-video transitions, with a single three-column slide:
  - **Observed failure:** exact artifact and quote, with date/run context.
  - **Guardrail added:** the specific `CLAUDE.md` rules or control constraints.
  - **Retest status:** passed, failed, or not yet tested, supported by an artifact.

  Add one sentence defining the human judgment gate: which actions require approval before hardware motion, and which can proceed autonomously. Keep the claim narrow. A documented rule is a process guardrail, not proof that the system is safe.
- **Acceptance test:**
  1. **Rendered-image check:** the slide must visibly include the labels **Failure**, **Guardrail**, and **Retest**, plus the source identifiers for the failure and rule change.
  2. **Five-second test, named pass criterion:** after five seconds, a fresh reviewer must be able to state what went wrong and what changed. Pass only if both answers are concrete actions, not “the agent made a mistake” and “more oversight.”
  3. **Traceability test:** every quoted word must match the source artifact; every guardrail must map to a visible line or summarized rule in `CLAUDE.md`; the retest cell must not say “passed” without a post-change run artifact.
  4. **Terminology audit:** search slide text and notes for **safe**, **secure**, **verified**, and **autonomous**. Each occurrence must specify scope. Replace unbounded forms such as “safe autonomous control” with the tested condition, resource boundary, and human gate.

### H3. End on one audience action, not a destination puzzle

- **Action semantics:** **Recommendation**.
- **Observation:** Slide 26 places a QR code over a Google homepage. Slide 28 combines institutional logos, a collaborator-video thumbnail, and another QR code without a visible instruction stating what the audience should do or what opens after scanning.
- **Consequence:** The final seconds divide attention among branding, video, and QR interpretation. Interested viewers must infer both the destination and the requested action.
- **Proposed patch:** Make slide 28 the sole call to action. Use this syntax: **verb + object + payoff**, for example, “Watch the 7-minute lab walkthrough to see the complete GitHub-to-hardware run.” Put that line above one QR code, add the destination name and a short typed URL, and retain the two institutional logos at reduced visual weight. Remove the Google-homepage wrapper from slide 26; use slide 26 for the final evidence beat or delete it.
- **Acceptance test:**
  1. **Rendered-image check:** the closing slide must contain exactly one QR code, one imperative sentence, one destination label, and one human-readable fallback URL. No browser chrome may appear.
  2. **Five-second test, named pass criterion:** after five seconds, a fresh reviewer must answer “What should I do?” and “What will I get?” using words present on the slide. Both answers are required.
  3. **QR test:** decode the QR from (a) the exported slide image, (b) a 1920×1080 screenshot, and (c) a perspective-distorted screenshot occupying 25% of frame height. Pass only if all three decode to the same HTTPS destination and the fallback URL resolves to that destination.
  4. **Terminology audit:** the CTA verb must appear once and the destination name must be identical in the headline, QR target metadata, and fallback URL label.

## Clarifying questions

### Q1. What is the documented basis for “$200” versus “$1500 (scale)” on slide 11?

- **Action semantics:** **Question**. Answer before retaining the comparison.
- **Observation:** The slide presents `$200` and a struck-through `$1500 (scale)` without a visible bill of materials, vendor/model, date, or statement of whether labor, electronics, enclosure, and calibration are included.
- **Consequence:** The comparison is memorable but not reproducible from the deck.
- **Proposed patch:** If the basis exists, add a six-word qualifier and a footnote or QR-accessible bill of materials, such as “parts-only prototype cost, Aug 2026.” If the bases are not comparable, show the prototype cost alone and describe the commercial device functionally rather than numerically.
- **Acceptance test:** A reviewer must be able to answer “cost of what, on what basis, as of when?” from the slide and linked source. The two figures must use the same inclusion rules and currency.

### Q2. Which external-verification artifacts may be shown publicly?

- **Action semantics:** **Question**. Needed to implement H1 without exposing private repositories or collaborator information.
- **Observation:** The review corpus identifies a blind-test key photo, scale telemetry, and collaborator verdicts, while several deck screenshots expose repository and user-interface details.
- **Consequence:** The strongest evidence cannot be selected or redacted correctly until its presentation permissions are known.
- **Proposed patch:** Mark each candidate artifact **public**, **redact**, or **internal only**. For redacted artifacts, preserve the measurement, date/run identifier, and evaluator role while removing names, tokens, repository paths, and unrelated interface content.
- **Acceptance test:** Every artifact on an evidence card has a recorded permission state; an automated image/text audit finds no access tokens, private URLs, email addresses, or unnecessary participant identifiers.

### Q3. What single action should the closing QR request?

- **Action semantics:** **Question**. Needed to finalize H3.
- **Observation:** The current close could plausibly direct viewers to the collaborator video, a laboratory page, a repository, or a live-stream channel.
- **Consequence:** Choosing the wrong destination would make a visually clear close strategically unhelpful.
- **Proposed patch:** Select one primary audience and one next action for this version of the talk. Put all other links on the landing page reached by the primary QR.
- **Acceptance test:** Complete this sentence without “and”: “After the talk, I want [audience] to [one action] because [one payoff].” The final slide must implement that sentence.

## Proposed patch set

One coherent revision, not three unrelated edits:

1. **Keep slides 1–9 substantially intact.** The Wizard-of-Claude hook and progressive timeline establish the change in interaction style.
2. **Rebuild slides 10–13 as the three application evidence sequence.** Keep the strongest physical images, but replace the repeated generic headline with application-specific conclusions. Use the common five-part evidence grammar from H1. If the cost basis survives Q1, retain it as a qualified annotation rather than the main claim.
3. **Keep slide 14 as the roadmap into detailed workflows,** but emphasize the three abstract-promised applications and the two enabling resources rather than presenting seven equal topics.
4. **Use slides 15–17 as drill-down evidence.** Crop to the task, handoff, verification, and result; do not ask the audience to read entire GitHub threads.
5. **Use slides 18–19 for one robotic-control success, then make slide 20 the failure→guardrail→retest case.** This pairs capability with supervision while the hardware-control context is active.
6. **Use slides 21–25 for the powder-dosing chain:** hardware, target, instrument result, logged record, and resource boundary. Label which access is through Tailscale/secure shell and which service is external cloud compute or storage.
7. **Replace slide 26 with the final synthesis:** “Agents can cross software and hardware boundaries when handoffs, checks, and approval gates are explicit.” Show the three applications beneath it with one checked result each.
8. **Repair or remove slide 27 under B1.** It must have a static evidence-bearing fallback.
9. **Make slide 28 the single-action close** after Q3 is answered.

**Patch-set acceptance test:** Export the revised deck and run a slide-level audit. Pass if the abstract’s six promised elements can each be mapped to at least one slide: successes, challenges, alloy self-driving laboratory, powder doser, tensegrity self-driving laboratory, and GitHub-integrated multi-agent workflows with securely accessed external resources. No element may be supported only by speaker narration.

## Why these three: top-six ranking

The blocker is excluded from this ranking because reliable playback is a release condition, not a discretionary improvement. Scores use **audience benefit** and **rework cost** on 1–5 ordinal scales; the ratio is a prioritization aid, not a measured quantity.

| Rank | Candidate | Benefit | Cost | Benefit ÷ cost | Decision |
|---:|---|---:|---:|---:|---|
| 1 | Make the close one explicit action | 4 | 1 | 4.00 | **Selected as H3** |
| 2 | Add failure → guardrail → retest | 5 | 2 | 2.50 | **Selected as H2** |
| 3 | Build three claim-to-verification cards | 5 | 3 | 1.67 | **Selected as H1** |
| 4 | Add a separate multi-agent/tool topology diagram | 3 | 2 | 1.50 | Not selected; the evidence cards can expose the same roles and handoffs without adding another abstraction layer. Reconsider only if the cards fail the five-second test. |
| 5 | Rewrite the timeline labels as takeaway sentences | 2 | 2 | 1.00 | Not selected; the timeline already performs its orienting function, and changing it would not repair the missing verification or challenge evidence. |
| 6 | Reformat every portrait recording and browser capture | 1 | 2 | 0.50 | Not selected; useful polish, but the audience benefit is smaller than fixing the argument and close. Apply only to media retained after the narrative edit. |

The three selected changes also cover distinct jobs: **H1 proves the central claim, H2 calibrates trust, and H3 converts interest into action.** Candidate 4 overlaps H1; candidates 5 and 6 work at a lower-impact layer.

## Collapsed optional-polish checklist

### O1. Polish only the media that survives the narrative edit

- **Action semantics:** **Optional**. Defer until B1 and H1–H3 are accepted.
- **Observation:** Slides 20–21 place portrait recordings on mostly empty black canvases; slides 15–25 contain browser chrome and dense interface regions; slide 14 uses dimming to indicate emphasis but still presents a long list.
- **Consequence:** These choices reduce projected-image efficiency and can make the focal evidence harder to locate, but they do not create the deck’s main argumentative gap.
- **Proposed patch:** For retained media, crop to the evidence region; place portrait clips in a labeled two-column frame with a still/result beside them; remove browser chrome and unrelated account details; standardize headline position, source line, and result annotation; use one emphasis mechanism per slide.
- **Acceptance test:**
  - At 1920×1080, the focal evidence occupies at least 40% of slide area unless a deliberate comparison requires otherwise.
  - No essential text is below an equivalent 24-point size.
  - A fresh reviewer can point to the intended focal region within five seconds.
  - An OCR audit finds no emails, tokens, private URLs, or unrelated account labels.
  - Slides remain interpretable as static frames when animations and video are unavailable.

## Known-fact triage: what belongs in the review and what stays out

### Accepted or folded into the three changes

- **Slides 10–13 do not visibly establish multi-agent/multi-tool operation:** accepted and addressed in H1.
- **The deck shows activity more clearly than measured research gain:** accepted and addressed in H1, without demanding a gain metric that was never collected.
- **Agent self-reports sometimes stand in for verification despite stronger artifacts:** accepted and addressed in H1.
- **The `$200` versus `$1500` basis is not visible:** accepted as Q1, not promoted to a high-impact recommendation until its basis is known.
- **Challenges lack a dedicated beat:** accepted and addressed in H2.
- **The final call to action is ambiguous:** accepted and addressed in H3.
- **The captured slide 27 is black:** accepted as B1.

### Rejected as standalone review items

- **“Slide 27 projects black outside slideshow”: rejected as a causal diagnosis.** The capture proves a black frame, not why it occurred. B1 addresses the observable failure and requires testing both delivery paths.
- **“Slides 20–21 are portrait videos on mostly-empty dark canvases”: rejected as a top-level change.** This is valid visual polish but lower altitude than evidence and narrative; it is retained only in O1.
- **“Slide 26 wraps a QR in a Google homepage”: rejected as an independent item.** It is a symptom of the ambiguous closing action and is better fixed once under H3.
- **“Timeline labels are categories, not conclusions”: rejected for this revision.** Categories are appropriate for an orienting chronology. Rewriting them would add work without resolving a stated abstract promise.
- **Any claim that the talk’s live pacing, narration, or audience interaction failed:** rejected as unsupported. Contact sheets and sampled frames do not contain delivery audio, timings, or audience-response evidence.

## Preserve list

- Preserve the Wizard-of-Claude opening and “I am toto” framing; it gives the audience a concrete mental model before technical detail.
- Preserve the progressive timeline reveal on slides 4–9; it makes the interface evolution easy to follow.
- Preserve real GitHub issue threads as the native control surface. They are more credible than a redrawn fictional interface.
- Preserve the cross-boundary arc from repository to high-performance computing, secure remote access, hardware, telemetry, and database logging.
- Preserve the 1 g target and 0.9972 g scale result, with provenance and tolerance stated.
- Preserve physical outcomes: alloy processing, the powder doser, and tensegrity prints. They give the talk material stakes.
- Preserve collaborator presence and institutional identity, but subordinate them to the final audience action.
- Preserve the talk’s demo-forward character. The recommendation is to add verification structure around the demonstrations, not replace them with diagrams.

## Discretionary analytical decisions

- Treated the all-black slide 27 as a release blocker while withholding a diagnosis of its cause.
- Limited high-impact recommendations to evidence architecture, challenge/guardrail disclosure, and closing action; visual cleanup was deferred as optional.
- Used an ordinal 1–5 benefit/cost rubric to make prioritization explicit; the ratios are comparative judgments, not empirical measurements.
- Recommended provenance classes rather than a formal evidence-tier score on-slide to reduce audience decoding burden.
- Used a five-second recall test for claim clarity and required static fallbacks for all media.
- Treated “multi-agent” and “multi-tool” as distinct terms and required visible role/tool support for each.

# One-page checklist: how to review a hand-made deck

## Pass 1: narrative and evidence before visual polish

### 1. Contract

- Write the talk’s promise in one sentence.
- Extract every promised case, result, challenge, and resource from the title and abstract.
- Map each promise to a slide. Flag any promise supported only by narration.

### 2. Throughline

- For each section, identify the audience question it answers.
- Check that headlines state conclusions where evidence is being presented; use category labels only for navigation or chronology.
- Remove examples that repeat a function without advancing the argument.

### 3. Evidence chain

For every central claim, locate:

- the task or question;
- the responsible agent(s), person, and tools;
- the handoffs and resource boundaries;
- the external check;
- the result, uncertainty/tolerance, and source;
- the research benefit, or an explicit statement that it was not measured.

Do not treat an agent’s success message as independent verification. Do not infer research gain from activity.

### 4. Challenge and judgment gates

- Include at least one representative failure when challenges are promised.
- Show **failure → guardrail → retest status**.
- Identify which actions require principal-investigator or operator approval.
- Distinguish a written rule from demonstrated risk reduction.

### 5. Ending

- Choose one audience, one action, and one payoff.
- Use one QR code plus a typed fallback URL.
- Make the closing slide understandable without narration.

## Pass 2: visual and delivery polish

### 6. Five-second test

Show each key slide for five seconds, hide it, and ask:

- What was the claim?
- What evidence supported it?
- What should the audience remember or do?

Define the required answers before testing. Revise only when the named pass criterion fails.

### 7. Rendered-image audit

- Export every slide to an image.
- Check clipping, contrast, font size, empty canvas, browser chrome, and accidental black frames.
- Confirm that each slide has one obvious focal region.
- Verify that animations and video have meaningful static poster frames.

### 8. Terminology and provenance audit

- Search titles and notes for high-stakes terms: **multi-agent**, **verified**, **safe**, **secure**, **autonomous**, **measured**, and **cheaper**.
- Require scope and evidence for every occurrence.
- Trace every number, quote, comparison, and verdict to a retrievable artifact.
- Redact private repositories, identities, tokens, and URLs without removing provenance.

### 9. Media and venue preflight

- Test on the actual presentation machine, offline.
- Start, pause, resume, and skip every clip.
- Confirm audio routing and fallback behavior.
- Scan every QR from the back-of-room equivalent and verify its destination.
- Run once from the delivered file, not the authoring environment.

## Close the review

For every item, record exactly one state:

- **Accept:** implement the proposed patch and run its acceptance test.
- **Decline:** retain the current design and record the reason; do not reopen without new evidence.
- **Defer:** assign an owner and trigger, such as “after narrative lock” or “when the cost basis is documented.”

Release blockers remain open until their tests pass. Batch the rest as: at most three high-impact changes, at most three clarifying questions, one coherent patch set, one collapsed optional-polish list, and a preserve list.