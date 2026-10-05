# Task: adversarial critique of an AI coding agent's self-analysis of presentation-slide quality

## Context

I am a coding agent embedded in a materials-research lab's GitHub workflow (BYU Vertical
Cloud Laboratory). The lab's PI presented a conference talk at CNMS 2026 titled:

**"Agentic Lifestyles in the Era of AI: Autonomous Research Workflows and Insights from the Vertical Cloud Lab"**

Abstract (verbatim): "Agents and LLMs are reshaping research workflows, whether for
literature search, topic exploration, teaching, learning, code development, manuscript and
proposal writing, administrative work, control of robotic systems, and direct usage within
materials optimization campaigns. We highlight our lab's use of these tools in three
materials research applications: (1) a self-driving lab for critical-mineral-lean,
3D-printable metal alloy powder for aerospace, (2) generative systems prototyping for a
low-cost, high-performance powder multi-dosing system, and (3) a self-driving lab for
mechanical performance optimization of tensegrity-inspired, multi-material structures for
planetary landers. Our workflows are tightly integrated with GitHub, combining GitHub
Copilot and Claude Code GitHub Actions with frontier models (e.g., Fable 5) with GitHub's
built-in project management features (issues and pull requests) triggering parallelized
multi-agent workflows that have secure access to external resources such as Edison
Scientific and cloud computing. As agentic lifestyles normalize in science, we are excited
to share our successes and challenges in accelerating materials discovery and
commercialization."

Before the talk, I generated 14 "quote slides" (verbatim GitHub prompts → outcomes) and
inserted them into the PI's deck. The PI hand-built the rest of the deck. In the final
as-presented version, ALL 14 of my slides were hidden (cut); the PI's hand-made 28 slides
were presented. The PI now asks me to analyze the quality/style gap so I can eventually
(a) generate presentation slides of comparable quality and (b) make meaningful
improvement suggestions on his hand-made slides.

Attached files:
- claude-quote-slide-original.png — one of my quote slides as built (my style)
- hidden-quote-slides-sheet.png — four of my quote slides as they ended up (hidden)
- presented-sheet-00..06.png — contact sheets of all 28 presented hand-made slides
- video-sample-frames.png — sample frames from the 18 embedded screen-recordings/videos

## My self-analysis (the object you should attack)

# CNMS 2026 — what the hand-made deck does that my generated slides didn't

Self-analysis written by the coding agent (PR #176 follow-up, 2026-08-13), comparing the
**as-presented** `cnms-2026.pptx` (downloaded post-talk: 46 slides — 28 visible/presented,
18 hidden) against the 14 quote slides I built via headless-browser co-authoring on
2026-08-12, all of which ended up **hidden and unpresented** in the final deck. Refined
through five Edison Scientific critique iterations (artifacts under
`outputs/cnms-2026-slide-feedback/`) and grounded in Jean-luc Doumont's principles
(*Trees, Maps, and Theorems*; "Creating effective slides").

## 1. What was actually presented (structure of the 28 visible slides)

| Slides | Section | Content |
|---|---|---|
| 1 | — | Title: talk title, speaker, logos, venue. ~20 words total. |
| 2–3 | — | "The Wizard of Claude" — full-bleed Wizard of Oz still, then the same image white-washed with a small Claude icon behind the curtain ("I am toto" in speaker notes). Personal hook, humor, recurring motif. |
| 4–8 | — | One vertical timeline, five eras (Line completions '21 → ChatGPT '22 → Chat '23 → CLI '24 → Cloud agents '25). **Same skeleton on every slide**; past nodes dim to gray, the current node is black, and the right half is a live screen-recording demo of that era's tool. Progressive disclosure via emphasis, not bullet builds. |
| 9–13 | — | Message headline as a full sentence — "In 2026+, workflows are increasingly **multi-agent** and **multi-tool**" — held constant across five slides while the visual under it changes: timeline recap → atomizer footage + printed part in hand → $200 doser CAD with labeled DOFs → glovebox video → tensegrity prints + drop rig. The sentence is the claim; each slide is one piece of evidence for it. |
| 14 | — | "Agents and LLMs are reshaping …" — the abstract's list, with emphasis dimming (the whole list in gray, items relevant to the three case studies in black). |
| 15–17 | lit-search / hpc / optimization | One full-bleed screen recording per abstract claim: Edison-adjacent literature search on the private alloy repo; "@copilot submit to HPC… fetch and commit those results" with verified TOTP commits; BO campaign prompt (tensegrity#35). |
| 18–26 | robotic-control | The "prompts → outcomes" beat, done with **native artifacts**: screen recordings/screenshots of the real GitHub threads ("are the lights on?", color-sensor pickup, "dose 1 g", lab-tour demo → MongoDB Atlas), intercut with **phone video of the physical outcome** (OT-2 moving, glovebox dosing) and the YouTube Studio live-streams page. |
| 27–28 | robotic-control | Full-screen demo video; closing slide: lab logo + BYU + Taylor Sparks video thumbnail + QR code. |

Speaker notes are minimal and narrative ("I am toto…", "I'd like to show you what these
sessions can look like using three examples from my own research group") — the slides
carry images, the speaker carries the words.

## 2. What I built (the 14 hidden quote slides)

Dark-gradient `2_Quote_Long` layout, repeated 14×: a verbatim quote in large type, a
small-type attribution block (`— author · date · repo#issue`), and a multi-sentence
"→ outcome" paragraph in ~12 pt. No images. No videos. Slide numbers visible. Appended
as a trailing section.

## 3. The gap, itemized

1. **Native artifact vs. transcription.** The talk shows the *actual* GitHub comment —
   avatars, timestamps, the green "Claude finished @user's task in 2m 3s" banner — and
   then the physical world responding on video. I re-typed the same quotes into a text
   template. The screenshot is self-authenticating evidence; my transcription is an
   assertion. For a talk whose thesis is "the lab runs by GitHub comment," the GitHub UI
   *is* the figure.
2. **One message per slide vs. one dataset per slide.** Each of my slides carried
   quote + context + outcome + provenance (four items); the outcome paragraphs ran
   40–60 words at ~12 pt. Doumont's signal-to-noise law: everything on the slide that
   the audience won't read is noise; everything they must read competes with the
   speaker. The hand-made slides average well under 15 words visible.
3. **Provenance belongs in the repo, not on the canvas.** Comment IDs, dates, and
   issue numbers are essential in `cnms-2026-quotes.md` (the archive) and useless
   projected for 40 seconds. I optimized for verifiability — a document virtue — on a
   projection medium.
4. **No visual when the content was inherently visual.** "0.9956 g in a glovebox" has
   video. "Are the lights on?" has the camera still. The 18/18 blind test has a photo
   of the handwritten key. My slides cited them as text.
5. **Rhythm and build.** The presented deck has a visual grammar: recurring timeline,
   constant headline with changing evidence, dim-to-gray for the past, motif callbacks
   (Wizard of Claude → "behind the curtain" → Taylor's video). My 14 slides are a flat
   loop of one template — no build, no hierarchy between the load-bearing beat (glovebox
   milestone) and a garnish beat (147-word abstract).
6. **Time budget.** 14 near-identical slides appended to a ~25-slide talk ignores the
   ~1 slide/min ceiling. The speaker solved it by cutting all 14 — the curation survived
   (the corpus stats intro, and the same comments I shortlisted appear as
   screenshots/recordings in slides 18–26), but the *rendering* was discarded.
7. **Layout mechanics.** The `2_Quote_Long` attribution placeholder autofits into
   overlap when fed 60-word outcome paragraphs (visible in re-rendered slides 34/35/45);
   white autofit text on a dark gradient, slide numbers left on, defaults unexamined.
8. **Document/talk conflation (the "slideument").** My slides read well *as a file* —
   which is exactly the failure: they were written to be read, not to be presented.
   Doumont: slides that work without the speaker compete with the speaker.

## 4. What transferred (worth keeping)

- **The mining and curation were used.** The presented "prompts → outcomes" section is
  drawn from the same comments my corpus pass surfaced and verified; the corpus stats
  slide (254 issues · 146 PRs · 3,417 comments · 616 triggers) survives verbatim in the
  hidden intro slide. My value was research, verification, and selection — the
  bottleneck was visual instantiation.
- **Verbatim discipline** (typos kept: "weve", "aghh..") matches the talk's authenticity
  aesthetic — it just belongs inside a screenshot rather than re-set in Aptos.
- The headless co-authoring pipeline itself (build slides in the live deck, verify
  against the stored blob) worked and persists as capability.

## 5. Operating rules for my future slide generation

Derived from the comparison + Doumont + five Edison critique rounds:

1. **State the message, then prove it visually.** Slide title = a full-sentence claim
   (assertion–evidence structure); body = one native artifact (screenshot, photo, video,
   plot). If I can't name the one message, the slide isn't ready.
2. **Prefer capture over re-creation.** For GitHub-thread content: render the real
   comment (screenshot at readable zoom, cropped to the comment card) rather than
   re-typing. Keep typography native to the source.
3. **≤ 15 words of my own text on a slide** (title + label); everything longer goes to
   speaker notes or the repo doc. Attribution: `user · repo#issue` at most; full
   provenance lives in the committed markdown, linked from notes.
4. **One slide, one beat; build sequences by emphasis.** Reuse a constant skeleton and
   shift emphasis (dim past, highlight current) instead of new layouts per slide.
   Duplicated-slide overlays beat animation in PowerPoint web.
5. **Respect the time budget.** Ask (or infer) the slot length; propose slide *count*
   before building; deliver the shortlist ranked so the speaker cuts from the bottom.
6. **Match the deck's visual system before adding to it** — sample the existing slides'
   type scale, colors, and motif vocabulary; extend motifs (the timeline, the curtain)
   rather than introducing a new template mid-deck.
7. **Verify like a presenter, not a parser**: after building, re-render each slide as an
   image and *look* at it (overflow, overlap, contrast, autofit) — the same way the
   stored-blob text check was done, but visual.
8. **Deliver as a reviewable artifact**: committed per-slide PNG proofs + a map doc, so
   the speaker can triage slides the way they triage PRs.

## 6. Meaningful-suggestion mode (critiquing hand-made decks)

What I'd flag in the presented deck, applying the same standards symmetrically — offered
as evidence I can critique constructively, not just imitate:

- Slides 4–8 and 15–26 rely wholly on narration for their message; as a leave-behind the
  deck is mute. A one-line message title on the evidence slides (e.g., "A five-word
  comment operates the robot") would make them self-supporting without competing with
  the speaker — Doumont explicitly prefers sentence headlines over label headlines.
- The timeline labels ("Line Completions June 2021…") are label-titles set small; the
  era's *significance* (what changed for the researcher) is only spoken.
- Slide 14's dimmed list is the abstract's taxonomy, but three case studies cover only
  three of eight items; the mapping item→case-study is implicit.
- The demo videos are long (123 s, 177 s, 733 s source files); trimmed 8–15 s excerpts
  with a visible clock/timer overlay would keep the "it happened in 2m 3s" claim tight.
- QR codes appear only on the final slide; the audience's phone moment passes fast —
  repeating the QR on section closers would raise capture rate.

*(Each of these is a hypothesis about a live talk I didn't hear narrated; the speaker's
delivery may already cover them.)*


## Excerpt of my curated quote corpus doc (so you can judge claim 4-"What transferred")

# CNMS 2026 — curated prompts & outcomes from the lab's GitHub corpus

Source material for the "slideshow of prompts and some of the resulting outcomes" slides
(issue #175). Built 2026-08-12 by fetching **every** issue, PR, and comment across
`byu-vcl`, `powder-doser`, and `tensegrity-optimization` (raw dump + index in
[`data/cnms-2026-corpus/`](../data/cnms-2026-corpus/INDEX.md)), mining each repo for
candidates, and verifying the headline quotes verbatim against the raw JSON.

All quotes are copied exactly, typos included ("weve", "aghh") — recommend keeping them;
they read as authentic. Elisions marked with "…".

## Headline numbers (for the opening / "It's hard to keep up" slide)

- **254 issues + 146 PRs** across the three repos, Jan 6 → Aug 12, 2026
- **3,417 human comments**, 1,181 bot comments, 464 inline review comments, 205 PR reviews
- **616 human `@claude` triggers** — **361 from Sterling** (3 accounts), **255 from students/others**
- Growth curve: **9 triggers in June → 514 in July** (Claude Code workflows landed late June; August is a partial month at 93)
- powder-doser: napkin sketch (Apr 23) → agent-driven glovebox dosing at U. Utah (Jul 24) in **13 weeks**
- byu-vcl PR #60 alone spans Feb→Aug 2026: from Copilot design chat to Claude physically driving the OT-2 — a one-PR embodiment of the talk's timeline
- ⚠️ **FLAIME caveat:** the FLAIME proposal lives in `vertical-cloud-lab/digital-alloy-lab-private`, *not* in these three repos (only one substantive mention here, [byu-vcl#95](https://github.com/vertical-cloud-lab/byu-vcl/pull/95#issuecomment-4566509175)). The "how many sessions / PRs / pings" counts need a separate pass over that repo.

---

## The shortlist — 17 slide-ready prompt → outcome pairs

Ordered to follow the talk narrative. Each works as one slide: the human prompt big, the outcome as the reveal.

### A. Students running the lab's agents (teaching narrative)

**1. Five words, one robot** — sgbaird, 2026-07-11 · [byu-vcl#84](https://github.com/vertical-cloud-lab/byu-vcl/issues/84#issuecomment-4948345446)
> @claude are the lights on?

**Outcome (2m 3s):** "Yes — the lights are on ✅ Captured a fresh full-res still from the OT-2 camera Pi just now (over Tailscale, no one had to touch the hardware)" — with a lux estimate and embedded photo. *Triage-from-anywhere in its purest form.*

**2. A student steers the OT-2 by comment** — timothy-commins (undergrad), 2026-07-28 · [byu-vcl#60](https://github.com/vertical-cloud-lab/byu-vcl/issues/60#issuecomment-5108531313)
> @claude the color sensor is in slot 8. I want you to run a test to pick up the wireless color sensor and to use the camera to confirm if it has been picked up or not

**Outcome (39m 46s):** "**Camera confirmation: housing hanging mid-air on the nozzle** ✔" — the agent detected an unannounced P20→P300 pipette swap and corrected coordinates. The arc continues: "it will break the ot-2." ([5108951888](https://github.com/vertical-cloud-lab/byu-vcl/issues/60#issuecomment-5108951888)) → "great job… try the same test again but -2mm in the y direction" ([5110062424](https://github.com/vertical-cloud-lab/byu-vcl/issues/60#issuecomment-5110062424), which the agent **refused** as unsafe after the pipette swap) → "this test seems perfect" ([5110478883](https://github.com/vertical-cloud-lab/byu-vcl/issues/60#issuecomment-5110478883)). *A 4-slide build showing iteration, safety, and convergence.*

**3. An undergrad runs a double-blind experiment on the AI** — me-madsen, 2026-08-03 · [tensegrity#86](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/86#issuecomment-5172717335)
> The second set of drops contains 20 drops. A random arrangement of sets of 5 drops… The order of these will be known to me and not to you. The data will be uploaded to you, and I will check to see if your analysis… matches the actual order of the drops

**Outcome:** Claude pre-registered its decision rule before seeing data, then blind-classified 90 accelerometer drops. Verdict three days later, with a photo of the handwritten key: "By my review, it seems Claude got the true key correct." ([5209909579](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/86#issuecomment-5209909579)) — **18/18 correct**. *A student spontaneously inventing blinded validation is the teaching narrative's peak; one-image slide.*

**4. The learning curve, honestly** — gage-erickson, 2026-06 · [byu-vcl#99](https://github.com/vertical-cloud-lab/byu-vcl/issues/99#issuecomment-4463300181)
> It regularly asks to run specific commands that I also don't really understand.

**Outcome:** Six weeks later the same cohort was steering robots and designing blind tests. Pairs with the onboarding policy comment ([4756431550](https://github.com/vertical-cloud-lab/byu-vcl/issues/99#issuecomment-4756431550)): "We can get you set up with being able to ping @claude on repos…"

### B. Powder doser Part I — generative system design

**5. Napkin sketch → parametric CAD, same day** — sgbaird, 2026-04-23 · [powder-doser#1](https://github.com/vertical-cloud-lab/powder-doser/issues/1)
> We're thinking of using a pure mechanical approach that can be connected to a gantry system… deep ladle/style to drop powder

**Outcome:** Within hours, Copilot opened PR #2 with a CadQuery parametric model plus an Edison literature review framed "roughly as the intro to a *Digital Discovery* manuscript." Follow-up prompt "@copilot+claude-opus-4.7 Include full assembly image from CAD" ([4309852263](https://github.com/vertical-cloud-lab/powder-doser/issues/2#issuecomment-4309852263)) returned an embedded assembly render **one minute later**.

**6. Honest engineering, AI edition** — swcharles (student), 2026-07-01 · [powder-doser#116](https://github.com/vertical-cloud-lab/powder-doser/issues/116#issuecomment-4858202063)
> Note: yes, the threading is terrible. It was AI, we're fixing it in the next few days. It should work for now.

**Outcome:** Posted with photos of 9 freshly pr

## Your task (iteration 1 of 5)

Act as a hostile referee on MY ANALYSIS (not on the PI's talk). Specifically:

1. Which of my eight "gap" diagnoses (section 3) are well-supported by the attached
   visual evidence, and which are confabulated, overfit, or post-hoc rationalization?
2. What important explanations for "all 14 slides were cut" am I MISSING? Consider
   rival hypotheses: time constraints, redundancy with existing slides, the PI never
   intending to present them (source material vs. slides), sunk-cost-free triage, etc.
   Rank rival hypotheses by plausibility given the evidence.
3. Are my "operating rules" (section 5) actually derivable from this comparison, or do
   some not follow from the evidence? Which rules are wrong or counterproductive for
   scientific conference talks specifically?
4. My "meaningful-suggestion mode" critiques of the PI's own deck (section 6): which
   would a presentation-design expert (e.g., in the tradition of Jean-luc Doumont's
   'Trees, Maps, and Theorems' and assertion-evidence slide design) endorse, which
   would they reject, and what did I fail to flag?
5. What measurable/checkable criteria could distinguish a "presentable" slide from a
   "document-like" slide, so I can self-test future output mechanically?

Be specific, cite evidence from the attachments where possible, and be harsh — I will
use your critique to revise the analysis before a follow-up query.
