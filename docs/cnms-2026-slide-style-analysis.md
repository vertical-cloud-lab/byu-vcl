# CNMS 2026 — what the hand-made deck does that my generated slides didn't

Self-analysis written by the coding agent (PR #176 follow-up, 2026-08-13), comparing the
**as-presented** `cnms-2026.pptx` (downloaded post-talk: 46 slides — 28 visible/presented,
18 hidden) against the 14 quote slides I built via headless-browser co-authoring on
2026-08-12, all of which ended up **hidden and unpresented** in the final deck. This is
revision 2, rewritten after Edison critique iteration 1 (which demolished parts of
revision 1 — artifacts under `outputs/cnms-2026-slide-feedback/`), and grounded in
Jean-luc Doumont's materials (*Trees, Maps, and Theorems* summary; the Nature
Masterclass "John's slides"/"Marie's slides" example decks; the Stanford
"Creating effective slides" lecture).

## 1. What was actually presented (structure of the 28 visible slides)

| Slides | Section | Content |
|---|---|---|
| 1 | — | Title: talk title, speaker, logos, venue. ~20 words total. |
| 2–3 | — | "The Wizard of Claude" — full-bleed Wizard of Oz still, then the same image white-washed with a small Claude icon behind the curtain ("I am toto" in speaker notes). Personal hook, humor, recurring motif. |
| 4–8 | — | One vertical timeline, five eras (Line completions '21 → ChatGPT '22 → Chat '23 → CLI '24 → Cloud agents '25). **Same skeleton on every slide**; past nodes dim to gray, the current node is black, and the right half is a live screen-recording demo of that era's tool. Progressive disclosure via emphasis, not bullet builds. |
| 9–13 | — | Message headline as a full sentence — "In 2026+, workflows are increasingly **multi-agent** and **multi-tool**" — held constant across five slides while the visual under it changes: timeline recap → atomizer footage + printed part in hand → $200 doser CAD with labeled DOFs → glovebox video → tensegrity prints + drop rig. The sentence is the claim; each slide is one piece of evidence for it. |
| 14 | — | "Agents and LLMs are reshaping …" — the abstract's list, with emphasis dimming (list in gray, the items the case studies cover in black). |
| 15–17 | lit-search / hpc / optimization | One full-bleed screen recording per abstract claim: literature search on the private alloy repo; "@copilot submit to HPC… fetch and commit those results" with verified TOTP commits; the BO campaign prompt (tensegrity#35). |
| 18–26 | robotic-control | The "prompts → outcomes" beat, done with **native artifacts**: screen recordings/screenshots of the real GitHub threads ("are the lights on?", color-sensor pickup, "dose 1 g", lab-tour demo → MongoDB Atlas), intercut with **phone video of the physical outcome** (OT-2 moving, glovebox dosing) and the YouTube Studio live-streams page. A QR-code moment appears on slide 26, not only at the end. |
| 27–28 | robotic-control | Full-screen demo video; closing slide: lab logo + BYU + Taylor Sparks video thumbnail + QR code. |

Speaker notes are minimal and narrative ("I am toto…", "I'd like to show you what these
sessions can look like using three examples from my own research group") — the slides
carry images, the speaker carries the words. This deck is structurally close to
Doumont's exemplar ("Marie's slides"): sentence-message headlines, one message per
slide, constant skeletons with shifting emphasis, visuals developed rather than listed.

## 2. What I built (the 14 hidden quote slides)

Dark-gradient `2_Quote_Long` layout, repeated 14×: a verbatim quote in large type, a
small-type manually re-typed attribution block (`— author · date · repo#issue`), and a
multi-sentence "→ outcome" paragraph in ~12 pt. No images. No videos. Slide numbers
visible; an unfilled Footer placeholder; in the final deck's renderings, several slides
(34, 35, 45) show text-on-text collisions from autofit overflow.

## 3. Why the 14 slides were cut — ranked explanations (post-critique)

Revision 1 framed this as "my slides lost a style contest, one principle at a time."
The adversarial review correctly reranked the causes. In order of plausibility:

1. **The block was source material / a prototype section, not a committed talk
   section.** The slides sat in a trailing section (the deck's own `slide-graveyard`),
   appended after the closing slide. Generated slides entering a deck that way are
   alternates until the author promotes them.
2. **Redundancy: the talk already expressed the same beats natively.** "Are the lights
   on?" is presented slide 18; the color-sensor arc is 19; "dose 1 g" is 22; demo → 
   MongoDB is 23–24. Once the beats existed as native screenshots/recordings inside the
   narrative, a trailing quotation block re-stating them added duration without adding
   evidence. This — not aesthetics — is probably the dominant explanation for an
   **all-or-none block cut**.
3. **Several slides were not presentation-safe.** Text collisions, stray slide-number
   fragments, unfilled placeholders: release-blocking defects. Under time pressure, a
   homogeneous 14-slide block with defects gets hidden wholesale, not repaired.
4. **The template broke the deck's visual and narrative continuity** — a run of
   red-gradient text slides in a deck whose language is white-background evidence
   slides, placed after the narrative payoff.
5. **The talk was already full** (14 added beats ≈ +50% slide count) — plausible but
   undemonstrated without rehearsal timing.

What the comparison **cannot** show: that hand-made slides generically beat generated
ones (one deck, one editor, confounded authorship/timing/media access), or that the
corpus-mining work was wasted — the presented "prompts → outcomes" section uses the
same comments the mining surfaced and verified; the value landed as *research and
selection*, while the *rendering* was discarded.

## 4. The style gap that remains real

Even with causality reranked, the side-by-side stands:

1. **Native artifact vs. transcription.** The talk shows the actual GitHub comment —
   avatars, timestamps, the "Claude finished @user's task in 2m 3s" banner — then the
   physical world responding on video. I re-typed quotes into a text template. The
   screenshot carries provenance *natively* (who, when, where, how long) at zero reading
   cost; my slides re-typeset that provenance as competing text blocks. (Correction from
   iteration 1: provenance on-canvas is fine — the talk keeps it on-canvas everywhere;
   the failure mode is *manually typeset* provenance.)
2. **Missing visuals for inherently visual content.** "0.9956 g in a glovebox" has
   video; "are the lights on?" has the camera still; the 18/18 blind test has a photo of
   the handwritten key. My slides cited them as text.
3. **No rhythm or build.** The deck has a visual grammar (recurring timeline, constant
   headline over changing evidence, dim-the-past emphasis). My 14 slides are a flat loop
   of one template with no hierarchy between a milestone beat and a garnish beat.
4. **Document/talk conflation.** My slides were written to be read — they work in the
   repo, which is exactly why they compete with a speaker when projected. But the fix is
   not "less text" as dogma: several presented slides are text-dense *interfaces*; they
   work because the decisive line ("Yes — the lights are on ✅") is findable in seconds
   and the rest is context, not required reading. The operative quantity is required
   attention per second of dwell time, not word count.

## 5. Operating rules for my future slide generation (v2)

1. **Every slide gets one defined communicative job.** For an analytical claim: a
   sentence assertion + legible visual evidence (Doumont: "with each slide, convey one
   message (only) — state the message verbally, then develop it visually"). For a demo:
   a what-to-watch-for cue. For a hook or transition: neither may need a headline.
2. **Prefer faithful extraction of native artifacts** — crop to the decisive region,
   enlarge until the key line reads at ~24 pt equivalent, mask irrelevant chrome,
   annotate — over both (a) re-typing content into styled text and (b) pasting raw
   full-window screenshots.
3. **Manage reading load, not word count.** Required reading time ≲ half of planned
   dwell time while the speaker talks; count words inside screenshots too; one primary
   reading path per slide. Minimum effective text size ≈ 24 pt equivalent; contrast
   ≥ 4.5:1 normal / 3:1 large.
4. **One slide, one beat; build by emphasis.** Hold a skeleton constant across a
   sequence and shift emphasis (dim past, highlight current) — the deck's timeline
   slides and Doumont's Marie-deck builds both do exactly this.
5. **Time budget from rehearsal, not slide count.** Ask for the slot length; deliver
   beats ranked with an explicit cut priority so the speaker can triage from the bottom.
6. **Match the host deck's visual system; extend its motifs.** Sample type scale,
   colors, and recurring devices before adding anything; never introduce a new template
   mid-deck. Insert new slides *into* the narrative where they belong, not as a trailing
   block — an appended section reads as source material, and gets treated as such.
7. **Mechanical release gates, then human check.** No text/object overlap, no
   placeholder leftovers, no off-slide objects, safe margins, media plays; then re-render
   every slide to an image and *look at it*; then a five-second test (can a cold viewer
   name the topic and find the focal point?).
8. **Audit evidence quality on claim slides.** Distinguish direct measurement /
   independent validation / agent self-report / anecdote; when the claim is scientific,
   show comparator, n, and uncertainty. A Claude comment saying "success" is a report,
   not a validation — pair it with the scale reading, the video, the log.

## 6. Meaningful-suggestion mode (critiquing hand-made decks) — v2

Iteration 1 endorsed some of my suggestions for the presented deck, rejected others,
and added sharper ones I missed. The surviving, defensible set:

**Endorsed / kept:**
- Slides 15–17 (full-bleed app recordings) would benefit from a one-line statement of
  why the audience is watching each interface; slides 18/19/22 may not — the decisive
  outcome line is already in-frame; cropping/zooming it beats adding a headline.
- Timeline labels are categories ("Chat Interfaces"), not conclusions; one stable
  assertion governing the sequence ("AI moved from suggesting code to executing
  workflows") would make the argument explicit without per-slide headlines.
- Slide 14's list→case-study mapping is implicit; three markers/icons would close it.

**Rejected (my v1 suggestions that don't survive scrutiny):**
- "Trim all videos to 8–15 s with a timer overlay" — source-file duration ≠ played
  duration; a universal cap is unjustified; GitHub's native "finished in 2m 3s" line is
  stronger time evidence than a decorative timer.
- "Repeat QR codes on section closers" — factually weak (slide 26 already has a QR
  moment) and attention-fragmenting.

**Added by the critique (the sharpest items I failed to flag):**
- Slides 10–13's evidence (melt pool, printed part, CAD, glovebox) shows *outcomes* but
  does not visibly establish "multi-agent, multi-tool" — the assertion–evidence link is
  loose; one slide showing two agents/tools actually interoperating would close it.
- The deck shows activity more than research gain: no comparative performance evidence
  (vs. manual workflow; reliability; cost) appears on any slide.
- Agent self-report is repeatedly presented as outcome evidence; pairing it with
  external verification (scale readings, video, DB records, the blind test) would
  materially strengthen the scientific claim — and the corpus contains exactly those
  artifacts.
- Slide 11's "$200 vs $1500" has no visible basis (scope/BOM/comparison).
- Vertical phone videos on dark slides waste most of the canvas (20–21).
- Slide 26's Google homepage is noise around the QR; slide 27 projects as a black
  frame outside slideshow mode; slide 28's call-to-action (what does the QR open?) is
  ambiguous.
- Accessibility untested: small gray timeline labels, dense dark-mode screenshots,
  color-only emphasis, uncaptioned videos.
- For a talk about autonomous research: no visible boundary between what was
  autonomous, human-approved, or safety-interlocked — a disclosure the audience needs
  and the CLAUDE.md-guardrails story could carry.

*(All of section 6 remains hypothesis about a talk I didn't hear narrated.)*

## 7. Self-test checklist (mechanical, runnable before delivering slides)

- [ ] Geometry: no overlapping text boxes; no objects off-slide; no unfilled
      placeholders; ≥3% edge margins. (My slides 34–35 fail this today.)
- [ ] Legibility: decisive text ≥ ~24 pt equivalent after cropping/scaling; contrast
      4.5:1 / 3:1; slide readable at 25% zoom.
- [ ] Reading load: (visible words incl. inside screenshots) / 200 wpm ≲ 50% of dwell.
- [ ] Five-second test: cold viewer names topic + first-fixation target.
- [ ] Assertion–evidence audit per claim slide: claim / evidence type (measurement,
      validation, self-report, anecdote) / comparator / n / uncertainty.
- [ ] Media: first frame communicates; starts ≤1 s before the action; plays on the
      presentation machine; captions or viewing cue.
- [ ] Audio-on test (complements the spoken sentence?) and audio-off orientation test
      (topic identifiable without narration?). A leave-behind, if needed, is a separate
      annotated PDF — one artifact should not serve both jobs.
