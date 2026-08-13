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
