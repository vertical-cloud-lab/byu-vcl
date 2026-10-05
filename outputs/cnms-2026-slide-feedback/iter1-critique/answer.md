# Hostile-referee verdict

Your analysis notices several real defects, but it overclaims why the slides were cut. The strongest fact is not that 14 individually bad slides lost 14 independent quality contests. It is that an entire contiguous, repeated-format block was hidden while some of its content was retained in another form. That pattern points first to **structural triage, redundancy, and integration failure**, with visual quality as a contributing factor.

You have converted one editorial decision into a comprehensive design doctrine. Some of that doctrine is useful. Some is retrospective storytelling.

## Evidence limits

The evidence consists of rendered slides and sampled video frames. There is no talk recording, rehearsal timing, edit history, original assignment wording, or statement from the PI explaining the cuts. Consequently:

- We can judge visible defects and content duplication.
- We can infer plausible editorial pressures.
- We cannot identify the PI’s actual causal reason for hiding the slides.
- We cannot assess video duration from source-file duration. A 733-second source can contain a 10-second embedded segment.
- We cannot establish that corpus mining caused the PI’s selections without timestamps or edit history showing that transfer.

## 1. Your eight gap diagnoses

| # | Diagnosis | Verdict | What the attachments actually support |
|---|---|---|---|
| 1 | Native artifact vs. transcription | **Strong, but overstated** | Slides 18, 19, 22, and 23 preserve authorship, interface context, task duration, and the agent response. Hidden slides 33–36 retype the exchange and discard those cues. But a screenshot is not automatically “self-authenticating”; it can still be cropped, staged, or illegible. It is rhetorically more credible, not proof by itself. |
| 2 | One message vs. one dataset | **The defect is real; your comparison is false** | Hidden slides 34–36 visibly collide and become unreadable. They contain competing quote, attribution, and outcome regions. But the hand-made deck does **not** average “well under 15 words” in any meaningful visual-density sense. Slides 8, 15–19, and 22–24 contain dense application interfaces; slide 17 is a wall of text. The real distinction is selective framing and recognizable hierarchy, not raw word count. |
| 3 | Provenance belongs off-canvas | **Mostly wrong** | The presented deck repeatedly keeps provenance on canvas because it is embedded in GitHub’s native interface: avatars, dates, account names, repository context, status, and elapsed time. That provenance helps establish who instructed what and what the system reported. The problem on your slides is not provenance itself. It is manually typeset metadata competing for space. |
| 4 | No visual for inherently visual content | **Strong** | The supplied video frames include physical hardware, printed parts, robot motion, camera confirmation, dosing results, and database records. Your sampled quote slides show none of them. This is the clearest medium-selection failure. However, your specific 18/18-transfer claim is unsupported by the presented contact sheets: the blind-classification example is not visible in slides 1–28. |
| 5 | Rhythm and build | **Strong for the presented deck; weak as a cause of cutting** | Slides 4–7 reuse a timeline with changing emphasis; slides 9–13 repeat a headline while changing imagery. Hidden slides 33–36 repeat a template without narrative progression. That establishes a stylistic gap. It does not establish that lack of rhythm caused the block to be cut rather than merely making the cut easier. |
| 6 | Time budget | **Plausible, not demonstrated** | Adding 14 slides to 28 would increase the visible count by 50%, so time pressure is credible. But “~1 slide/min ceiling” is not a defensible general rule. Slides 4–7 can pass quickly; one live demo can consume several minutes. Time must be estimated from rehearsed duration, not slide count. |
| 7 | Layout mechanics | **Decisively supported** | Slides 34 and 35 have severe text-on-text collisions. Slide 36 is crowded, and slide 33 shows stray stacked slide-number digits at lower right. The original PowerPoint screenshot also shows an unfilled “Footer” placeholder. These are release-blocking defects, not matters of taste. Your analysis oddly understates them by discussing 12-point text when the more basic problem is that the rendered objects overlap. |
| 8 | Slideument conflation | **Partly post-hoc** | Your quote slides require sustained reading and do compete with narration. But several presented slides are also document-like: slide 8 is a full GitHub issue; slides 15–19 and 22–24 are application screens; slide 17 contains a long prompt. The hand-made deck did not reject documents categorically. It used documents as *demonstration objects*. Your failure was turning source material into a generic text composition without making either the claim or the evidence easier to apprehend. |

### Two claims in “What transferred” need downgrading

1. **“The mining and curation were used”** is plausible for the exact “lights on” and color-sensor examples, because they appear on presented slides 18–19. It is not proven from the final deck alone, and it is not true for the whole shortlist. The 18/18 blinded experiment, for example, is absent from the supplied presented sheets.
2. The claim that the corpus-statistics slide “survives” is misleading if it remained hidden. Surviving in the file is not surviving in the talk.

## 2. Why all 14 were cut: ranked rival hypotheses

These hypotheses are not mutually exclusive.

### 1. The block was a source-material or prototype section, not a committed talk section

**High plausibility.** The original screenshot explicitly places the quote slide below a section labeled **“slide-graveyard.”** The final slides are also hidden as a contiguous trailing group. This is direct evidence that at least by the captured editing stage they were being treated as alternates or raw material. If the PI requested “slides,” that still does not mean every generated slide was intended to survive rehearsal.

This explanation is more parsimonious than “the PI evaluated all 14 and rejected each for violating Doumont.”

### 2. The presented deck already expressed the same beats, making the quote block redundant

**High plausibility.** The exact “@claude are the lights on?” exchange appears natively on slide 18; the color-sensor exchange appears on slide 19; remote dosing appears on slides 22–23. Once those examples were integrated into the main narrative, repeating them as quotations near the end would add duration without adding evidence.

This is probably the dominant explanation for an **all-or-none block cut**. Your analysis mentions redundancy only indirectly and instead narrates the event as a style competition.

### 3. The slides were not presentation-safe

**High plausibility for at least some slides.** Slides 34 and 35 contain catastrophic overlap. Stray numbers and an unfilled footer indicate inadequate visual quality control. A speaker doing last-minute, sunk-cost-free triage would reasonably hide the whole homogeneous block rather than repair 14 instances.

This is narrower and better supported than your broad “slideument” theory.

### 4. The quote template broke the deck’s narrative and visual continuity

**Moderate-to-high plausibility.** The main deck moves from historical setup to applications to demonstrations and closing. A late run of 14 red-gradient quotation slides would introduce a new visual language and repeat the demonstration material after its narrative payoff. The fact that they were appended matters more than the fact that they were quotations.

### 5. Rehearsal showed that the talk was already full

**Moderate plausibility.** Fourteen additional beats are expensive. Yet no slot length, rehearsal timing, or talk recording was supplied. Treat this as a hypothesis, not a finding.

### 6. The PI preferred live/native demonstration over summarized outcomes

**Moderate plausibility.** The final deck heavily favors interfaces and video. But this may reflect the content already available, the PI’s speaking style, or convenience, not a universal preference.

### 7. Every quote was intrinsically weak or poorly curated

**Low plausibility.** Some exact examples were retained in native form, which is evidence that selection was useful. The rendering and placement were rejected more clearly than the underlying stories.

### 8. The deck proves a general superiority of hand-made slides over generated slides

**Very low plausibility.** This is a one-deck, one-editor observational comparison with severe confounding: authorship, timing, access to media, narrative ownership, intended role, and integration stage all differ.

## 3. Operating rules: keep, revise, or delete

### Rule 1: “State the message, then prove it visually”

**Keep as a default, not a law.** Assertion–evidence structure is useful for scientific claims. But demos, section transitions, emotional hooks, and process reveals do not always need a sentence headline. A title can also consume scarce vertical space or redundantly narrate an obvious clip.

Revised rule: **Every slide needs a defined communicative job. For an analytical claim, use a concise assertion plus legible evidence. For a demo, make the audience know what to watch for.**

### Rule 2: “Prefer capture over re-creation”

**Revise substantially.** Native capture preserves context, but raw screenshots often fail projection. Slides 17 and 24 demonstrate the risk: much of the interface is too small or irrelevant. A scientific talk should prefer **faithful extraction**, not untouched capture: crop, enlarge the decisive region, mask irrelevant interface chrome, and annotate without changing the evidentiary content.

### Rule 3: “≤15 words of my own text”

**Delete the hard threshold.** It is neither derived from this comparison nor suitable across scientific talks. A 12-word vague headline can be worse than a 30-word precise explanation. Conversely, a plot may need axis labels, conditions, sample size, and uncertainty.

Use reading time, font size, hierarchy, and task relevance instead. Also, “my own text” is the wrong denominator: unreadable GitHub text burdens the audience regardless of authorship.

### Rule 4: “One slide, one beat; build by emphasis”

**Keep as a strong default.** Slides 4–7 support it. But “duplicated-slide overlays beat animation” is a tooling preference, not a lesson established by this deck. Duplication can bloat files and create synchronization errors.

### Rule 5: “Respect time budget; propose slide count”

**Keep the time-budget requirement; remove slide-count fetishism.** Propose a rehearsed time allocation by section and by demo. Count is secondary. A 20-second image and a three-minute live demonstration are not equivalent units.

### Rule 6: “Match the deck’s visual system”

**Keep.** The red-gradient block plainly looks imported. But matching style should not mean preserving defects in the host deck or forcing every scientific figure into a motif. Consistency serves comprehension, not imitation.

### Rule 7: “Re-render and look”

**Keep and strengthen.** This is directly supported by the collisions. Add automated bounding-box checks, minimum effective text-size checks, and media-playback validation. Human projection review remains mandatory because a parser cannot judge hierarchy or glance comprehension.

### Rule 8: “Deliver PNG proofs + map doc”

**Reasonable workflow, not derivable from the comparison.** It may improve review, but there is no evidence here that lack of PNG proofs caused the cuts. More artifacts can also increase review burden. Ask what the PI will actually inspect.

### Scientific-talk-specific correction

Your rules focus on aesthetics and narrative while neglecting scientific evidence. For each substantive scientific claim, ask:

- What was measured?
- Against what comparator or baseline?
- Under what conditions?
- With how many trials or samples?
- What uncertainty or failure rate was observed?
- Does the visual establish the claimed contribution, or merely show that software and hardware exist?

The presented deck is rich in workflow anecdotes but, from the supplied images, thin on comparative performance evidence. Your future slides should not imitate that weakness merely because those slides survived.

## 4. Your proposed critiques of the PI’s deck

### Adding sentence headlines to slides 4–8 and 15–26

**Endorse selectively; reject as a blanket edit.**

- Slides 15–17 would benefit from a statement of why the audience is seeing each interface.
- Slides 18, 19, and 22 already contain salient outcomes inside the interface: “Yes — the lights are on,” “Pickup test complete,” and “Dosed 1 g.” Cropping and emphasizing those lines may work better than adding another title.
- Full-screen videos need a viewing instruction or setup, but that can be spoken or briefly shown before playback.

Your suggested “A five-word comment operates the robot” is catchy but potentially imprecise. The visible evidence shows a comment initiating an agent workflow whose implementation and safeguards are hidden. “A GitHub comment initiated a remote robot check” is less theatrical and better supported.

### Timeline labels should state significance

**Endorse.** “Line Completions,” “Chat Interfaces,” and “Command Line” are categories, not conclusions. A short progression such as “AI moves from suggesting code to executing workflows” would make the argument explicit. But do not add a separate sentence to every timeline slide if one stable assertion can govern the sequence.

### Slide 14 should map the list to the cases

**Partly endorse.** The active/dim text already encodes selection, but the mapping is not self-evident. Color-coded case markers or three small icons could clarify it. Your statement that three cases cover “only three of eight items” is itself too literal: one case may demonstrate coding, adaptive experimentation, robotic control, and teaching simultaneously.

### Trim all videos to 8–15 seconds and add a clock

**Reject as stated.** The contact sheet gives source durations, not played durations. There is no evidence that the PI played 123, 177, or 733 seconds. Eight to fifteen seconds may be too short to establish autonomous physical action. Trim dead time and rehearse exact playback points; do not impose a universal duration.

A timer overlay is justified only when elapsed time is part of the claim and the timer’s provenance is clear. Otherwise it adds clutter and can look staged. GitHub’s native “finished … in 2m 3s” line may be stronger evidence.

### Repeat QR codes on section closers

**Reject absent audience testing.** Repetition consumes space, invites phones during the argument, and can fragment attention. One stable closing QR with a readable short URL is usually cleaner. Slide 26 already provides an earlier QR moment, so the claim that QR codes appear only on the final slide is factually wrong.

## Important problems you failed to flag

1. **The evidence often does not prove the headline.** Slides 10–13 repeat “workflows are increasingly multi-agent and multi-tool,” but a melt-pool video, a printed part, CAD, and hardware photographs do not visibly establish multiple agents or tools. The assertion–evidence link is weak.
2. **Raw interface screenshots are frequently too dense.** Slide 17 is unreadable at contact-sheet scale and likely difficult from the back of a room. Slides 15, 16, 22, 23, and 24 include substantial interface chrome. Native does not mean legible.
3. **The talk shows activity more clearly than research gain.** Screenshots demonstrate that commands were issued and outputs reported. They do not by themselves quantify acceleration, reliability, cost reduction, material performance, or comparison with a human/manual workflow.
4. **Agent self-report is treated as outcome evidence.** A Claude comment saying a task succeeded is not independent validation. Physical video, sensor logs, mass measurements, database records, and blinded checks are stronger. The deck should distinguish agent report from external verification.
5. **Slide 11’s cost comparison lacks visible basis.** “$200” and struck-through “$1500 (scale)” are memorable but unsupported on the slide: scope, bill of materials, and comparison basis are unclear.
6. **Slide 14’s abstraction level and terminology shift.** It moves from historical narrative to a taxonomy without an explicit transition or mapping to the three promised applications.
7. **Vertical and dark media waste the canvas.** Slides 20 and 21 use narrow portrait content with large black side fields. Cropping, framing, or a paired explanatory panel could improve use of projection area.
8. **Slide 24 shows a cluster overview, not clearly the claimed logged result.** The video sample includes a more relevant Data Explorer view with `dose_runs`; that would better support “logged to MongoDB.”
9. **Slide 26 is visually a Google homepage plus QR code.** The Google page is irrelevant noise. A clean branded QR slide with destination text would be stronger.
10. **Slide 27 is black.** It may be an intentional video endpoint or pause, but without playback context it is impossible to distinguish from a failure state. That should be tested in slideshow mode.
11. **The final call to action is ambiguous.** Slide 28 combines lab branding, a YouTube thumbnail, and a QR code without plainly stating what the code opens or what the audience should do.
12. **Accessibility is untested.** Small gray timeline labels, dense dark-mode screenshots, color-dependent emphasis, and video without visible captions may fail for distant viewers or viewers with impaired vision/hearing.
13. **No visible disclosure boundary.** For a talk about autonomous research, audiences need to know which actions were autonomous, which were human-approved, and where safety interlocks operated. That distinction is scientifically and ethically more important than another style refinement.

## 5. Mechanical and empirical self-tests

No purely mechanical rule can certify that a slide is presentable. Use automated gates to catch failures, followed by human comprehension testing.

### A. Release-blocking geometry checks

- No text or object overlap unless explicitly whitelisted.
- No object outside the slide bounds.
- No unresolved placeholders such as “Footer.”
- No stray slide-number fragments.
- At least 3–5% safe margin from the slide edge for essential content.
- All linked/embedded media plays in slideshow mode on the presentation machine.

Your slides 34–35 fail the first test immediately; the original screenshot fails the placeholder test.

### B. Effective legibility checks

- Body text created in PowerPoint: target at least 24–28 pt; larger for key messages.
- Screenshot text: crop and scale until the decisive text has approximately the same projected height as 24–28 pt slide text.
- Large text contrast: at least 3:1; normal-size text: at least 4.5:1 as a practical accessibility screen.
- Simulate distance by viewing the full slide at roughly 25% size on a laptop. If the required evidence cannot be read without zooming, recrop it.
- For each screenshot, calculate the proportion of pixels devoted to the decisive evidence versus browser/interface chrome. Treat less than ~50% evidence area as a review trigger, not an automatic failure.

### C. Reading-load checks

- Estimate silent reading time as displayed words divided by 200 words/minute, then add time for interpreting figures and interfaces.
- If required reading time approaches or exceeds planned dwell time, the slide is document-like for that delivery.
- Count all visible words that the audience must inspect, including words inside screenshots. Do not exempt “native” text.
- Highlight no more than one primary reading path and two supporting regions per slide.

A hard 15-word rule is inferior to this because the relevant quantity is **required attention per second**.

### D. Blinded five-second test

Show each slide for five seconds, without narration, to 3–5 lab members unfamiliar with it. Ask:

1. “What was this slide about?”
2. “Where did your eye go first?”
3. “What evidence did you notice?”

Pass criterion: at least 80% identify the intended topic, and the modal first-fixation region is the intended focal point. For an assertion slide, require at least 80% to paraphrase the same claim after ten seconds.

This is much more informative than asking whether they “like” the slide.

### E. Assertion–evidence audit

For every claim slide, record in a table:

- exact claim;
- visual evidence offered;
- whether the evidence is direct measurement, independent validation, agent self-report, anecdote, or decoration;
- comparator/baseline;
- sample size or repetition count;
- uncertainty/failure information;
- one sentence explaining how the evidence supports the claim.

If that last sentence requires facts not visible or spoken at that moment, revise the slide or narration.

### F. Audio-on and audio-off tests

A talk slide should not be judged solely as a leave-behind.

- **Audio-on test:** Does the slide complement the planned sentence, or make the audience read a competing paragraph?
- **Audio-off orientation test:** Can a viewer at least identify the topic and evidence type? It need not contain the whole argument.
- Produce a separate annotated PDF if a self-contained leave-behind is required. Do not force one artifact to serve incompatible jobs.

### G. Rehearsal-based timing

- Record actual dwell time per slide and playback time per video.
- Flag any slide whose required reading time exceeds ~50% of its dwell time while the speaker is also talking.
- Record cumulative section time and a cut priority for every optional beat.
- Test every demo’s fallback state and recovery time.

This replaces the unsupported “one slide per minute” rule.

### H. Media checks

- First visible frame communicates context; no blank/loading frame.
- Clip begins within one second of the relevant action.
- Remove dead time based on rehearsal, not a universal 8–15-second cap.
- Add captions or a concise viewing cue.
- If speed or autonomy is claimed, show an auditable timestamp or log rather than a decorative timer.
- Pair agent reports with external evidence when possible.

## The revision your analysis needs

Replace the thesis “my slides were cut because they violated eight presentation principles” with:

> The generated block had clear rendering failures and converted visually demonstrable events into generic text. However, the all-at-once cut is better explained by its role as an appended prototype/source section, duplication of examples already integrated into the main narrative, and time-efficient triage. The surviving native examples show that some curation was useful, but the available evidence does not isolate visual style as the cause of the editorial decision.

That version is harsher, less flattering, and better supported.

## Discretionary analytical decisions

- Ranked hypotheses qualitatively rather than assigning numerical probabilities because there is no direct PI rationale, edit history, rehearsal timing, or talk recording.
- Treated exact content recurrence across hidden and presented slides as evidence of redundancy, but not as proof that the corpus work caused the PI’s selection.
- Used practical accessibility thresholds of 3:1 for large text and 4.5:1 for normal text as review gates, not as guarantees of auditorium legibility.
- Proposed 24–28 pt as a practical minimum body-text range while requiring screenshot text to be judged by equivalent projected size.
- Proposed an 80% agreement threshold in small blinded comprehension tests as a workflow criterion, not a validated universal standard.
- Treated ~50% decisive-evidence area and reading time exceeding ~50% of dwell time as review triggers rather than hard rejection rules.