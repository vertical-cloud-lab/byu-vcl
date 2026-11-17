# Doing research with AI agents: a six-minute lightning talk

Outline for the research lunch and learn on 2026-11-17 ([#350](https://github.com/vertical-cloud-lab/byu-vcl/issues/350)).
It is built from the [voice memo](transcript.md) and follows Jean-luc Doumont's design
template component by component; the [method notes](doumont-method.md) cite his PDFs.
The talk is modelled on Doumont's own six-minute talk, whose opening and closing he
annotated for teaching.

The [follow-ups](follow-ups.md) fill most of the bracketed gaps below: the CAD renders, the
[five system animations](systems/README.md) for slide 4, the meeting count, real prompt pairs and pings, and what the literature says.

Draft wording, in italics, is a starting point. Doumont says to learn only the first and last
few sentences by heart, and otherwise to "memorize your outline but not your wording". Items in
**[brackets]** are facts only you can fill in.

## The template, filled in

| Component | Doumont: "…" | This talk |
| --- | --- | --- |
| **Attention getter** | "A way to lead the audience to the need efficiently" | A show of hands: who used AI this week, and for whom did it finish a whole task? |
| **Need** | "A difference between actual and desired situations" | AI went from completing a line of code to teams of agents with tools, but most of us still use it as a chat box, one question at a time. |
| **Task** | "What I decided/was asked to do to address the need" | You've handed agents work across the whole research stack, and you'll show what works. |
| **Main message** | "The one sentence I want my audience to remember" | **Agents can do real research work if we give them context and tools and keep their work in the open.** |
| **Preview** | "A map of the body (ideally three points, max. five)" | 1. the whole stack · 2. context and tools · 3. in the open |
| Point 1 | | Agents now reach across the whole research stack. |
| Point 2 | | Context and tools decide whether they help. |
| Point 3 | | Working in the open keeps agents accountable and brings people together. |
| **Review** | "A recap of the body, leading into the conclusion" | "So what to remember?" and the three points, one line each |
| **Conclusion** | "What the above means to the audience in the end" | You don't have to set this up alone: scan the QR code, book 30 minutes, and leave with your first agent running. |
| **Close** | "A way to end the presentation clearly and elegantly" | Back to the show of hands |

## Planning: Doumont's five questions

- **Why (purpose):** get people to *act*, not just listen. You said so in the memo: "what
  would be most actionable". Success means bookings through the QR code after lunch.
- **Who (audience):** researchers from mixed groups, many of whom use chat assistants and few
  of whom use agents. Doumont's first law, "Adapt to your audience", means less on how the
  agents work and more on what they would do for these listeners.
- **What (content):** three points, each with one example. Everything else from the memo is
  either in those three points or cut (see the [traceability table](#where-each-idea-from-the-memo-went)).
- **When (time):** six minutes, so about 900 spoken words. Suggested budget:

  | 0:00–0:50 | 0:50–2:05 | 2:05–3:20 | 3:20–4:35 | 4:35–5:45 | 5:45–6:00 |
  | --- | --- | --- | --- | --- | --- |
  | Opening | Point 1 | Point 2 | Point 3 | Review, conclusion (QR up), close | Slack |

- **Where (space):** a lunch room. People will be eating and holding phones, so the QR code
  needs to be large and stay on screen for the last minute and through the questions.

## Opening (about 50 s)

**Attention getter.** Doumont's own six-minute talk starts by addressing the audience
directly ("You are scientists…"). Three options, the first recommended:

- **A. A question (recommended).** *"Quick show of hands: who used an AI tool this week?
  … Keep your hand up if it finished a whole task for you while you were busy with something
  else. Say, eating lunch."* It's short, about the audience, and set in the room, and it lets
  the close come back to it.
- **B. A quotation.** Taylor Sparks's LinkedIn post about spinning up one agent after
  another as the new way of working. **[Find the post; quote it exactly, with its date.** A web
  search didn't find it, since LinkedIn posts aren't indexed; see the
  [follow-ups](follow-ups.md#taylor-sparkss-post).**]** A
  professor at the U is someone this audience may well know, which is what an attention getter
  needs: a link to something familiar. If you use A, B fits in the need instead.
- **C. A picture.** A ping from the atomizer workflow on a phone screen (see point 3). It's
  vivid but about you rather than them, so it works better as evidence than as an opener.

**Need: the actual situation versus the one we could have.** *"A few years ago, AI finished the
line of code you were typing. Then it answered questions in a chat window. Now you can hand an
agent a task, like 'find the papers on this' or 'design this part', and it comes back with the
finished work. And people are running several at once [B: Taylor's post]. Yet most of us still
use it as a chat box, one question at a time."*

**Task: now introduce yourself.** Doumont: "Wait until the task to talk about yourself." *"For
the past [year], I've given agents work across my whole research group, from teaching to
running instruments. Here's what works."*

**Main message: one sentence, said before the preview.**
*"Agents can do real research work if we give them context and tools and keep their work in
the open."*
Alternative in the form of Doumont's own six-minute talk ("TeX is powerful. TeX is flexible.
TeX is reliable."): *"Agents are capable. Agents are steerable. Agents are accountable."*,
which maps one-to-one onto the three points.

**Preview: collective *we*, and show the logic.** *"Let's first see how much of the research stack
agents can already cover. Then, what separates the attempts that work from the ones that don't:
context and tools. And finally, why doing all of it in the open keeps agents honest and, to
my surprise, brings people together."*
Transition: *"So: how much of our work can agents take on?"*

## Body (about 75 s per point)

### 1. Agents now reach across the whole research stack

- **The stack, as one picture** (the slide you mentioned): education (course content),
  administrative work, literature search and review, writing, coding, experiment planning,
  experiment execution. That's seven boxes in a row, from desk to lab. Say the message, then
  let the picture carry the list; don't read it out.
- **One example, shown rather than told:** five whole systems the agents designed and animated,
  in a 74 s [showreel](systems/showreel.mp4) ([what's in it](systems/README.md)). They are the
  PiPER wrist camera mount, the OT-2 overhead camera, the PiPER swapping the powder doser's auger,
  the CubXL copper corrosion screen and the vertical lab. Lead with the one that exists: the OT-2
  camera went from a comment on 25 Sep, through prints the agent sent itself, to a live stream on
  18 Oct. Then let the reel run while you say *"and it didn't stop at one part"*. Be straight that
  one is built, one is printed and three are designs or proposals.
  - If you want a number, there are **111 distinct agent-made designs** since April
    ([`cad/`](cad/README.md)). Say it, but don't show the grid: the systems carry the point better.
- **Many agents at once:** spinning up one agent after another, as in Taylor's post, if you
  didn't use it in the opening.
- Transition, creating the need for point 2: *"But for every task that worked, I've had one
  that didn't, and the difference was almost never the model."*

### 2. Context and tools decide whether they help

- **A good and a not-so-good prompt, side by side.** The not-so-good one is a single line with
  no files and no definition of done. The good one gives the goal, the sources to use, the
  constraints, what "done" looks like, and how to check it. Best real pair
  ([Pair B](prompts-and-pings.md#pair-b-tools-give-it-a-checker-atomizer-charge-cup-design-dal-152)):
  a long request for atomizer cup CAD came back verbose and with a stress check done wrong. The
  16-word follow-up *"double check this with Edison, and also make sure that the sizes are
  something standard"* caught four real errors. A good prompt names a tool and a check, and it
  doesn't have to be long. One candidate for the good side is the dictated request behind this outline
  ([#350](https://github.com/vertical-cloud-lab/byu-vcl/issues/350)). It is garbled ("jealous
  Dumont"), yet it names the source of truth ("look up the actual PDF") and a tool ("use the
  Raspberry Pi"), and that was enough.
- **Tools change what an agent can do.** An agent that can run the code, open the CAD file,
  query the database or look through the camera can check its own work. One that can only
  chat has to guess.
- **Pitfalls, with two real cases** (choose one or two; this lab's `CLAUDE.md` records both):
  - *Guessing instead of reading.* On [#197](https://github.com/vertical-cloud-lab/byu-vcl/issues/197),
    three facts about the sensor firmware were guessed wrong before anyone read its source.
  - *Missing context means repeating known work.* The same thread re-derived a calibration fix
    over several sessions, although upstream had already published it.
  - *Anything physical gets a human gate.* A print goes to the printer only after a person
    approves the run.
- Transition: *"And once agents can act on their own, the question becomes: how do we know
  what they did?"*

### 3. Working in the open keeps agents accountable and brings people together

This is your strongest point; Doumont puts the strongest arguments first and last.

- **Transparency, visibility, provenance.** Every request is an issue and every result is a
  commit or a comment, linked to its sources and to the run that produced it. Anyone can see
  what the agent did and why.
- **Show a ping from the atomizer workflow.** After the rePowder install call, an agent turned
  the transcript into follow-ups that pinged the right people, each linking back to the
  transcript ([the queued posts](../../meetings/2026-09-17-repowder-install/posts/)). Recommended
  ping: [DAL #153](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/153), where the
  transcript became an issue asking Gage to e-mail about an arc melter, and he replied "Email
  sent." **[Screenshot it.]** Alternatives are in [`prompts-and-pings.md`](prompts-and-pings.md#2-atomizer-pings-working-in-the-open).
- **Human connection.** About **seven** meetings with outside people came from agent-built contact
  lists and agent-drafted e-mails: professors in Lisbon, Berkeley and Michigan, and BYU's research
  VP. That's 4 confirmed and 3 likely, from about 27 people contacted
  ([evidence](meetings.md)). Most came through Copilot's coding agent running Claude, so say
  "agents". None trace back to MRS yet, since MRS is Nov 29 to Dec 4. Agents do the searching,
  and people do the meeting.

## Closing (about 70 s)

**Review.** Doumont's own words in his six-minute talk were "So what to remember?":
*"Agents now reach across the whole research stack. Context and tools decide whether they help.
And doing it in the open keeps them accountable and brings people together."*

**Conclusion: what it means for them, made actionable.** This mirrors Doumont's TeX
conclusion: it's free, so right after this talk you can go back to your office and install it.
*"And you don't have to set this up alone. Scan this code and book 30 minutes with me or one
of our TAs. We'll connect Codex to your GitHub through the CES ChatGPT Edu subscription, and you'll
leave with your first agent working on one of your own tasks."* The QR code goes up here and
stays up. **[Check first whether students get CES ChatGPT Edu licences: BYU-Idaho's page says they
don't ([details](follow-ups.md#the-ces-subscription)).]** The teaching literature backs this
format, a short introduction followed by guided practice on the person's own task. It also
suggests adding a recurring drop-in and a check-in after about three months
([Edison](follow-ups.md#teaching-researchers-to-use-ai--the-conclusion-and-the-qr-code)).

**Close: link back to the attention getter.** *"So next time someone asks for a show of hands,
keep yours up. Let an agent finish a whole task for you while you're at lunch."*

- Optional, riskier version: start an agent on a real task just before you speak, and open
  the close with *"While we were at lunch, this is what it finished."* Have a screenshot ready
  in case it hasn't.
- Avoid, per Doumont: "So, that's all I had", "Thank you for your attention", and "Happy to
  take questions". Let the applause come, then invite questions.

## Slides

One message per slide. Each title is the *so what*, as a full sentence of 12 words or fewer.
Seven slides is plenty for six minutes; "Do your slides right… or don't do slides at all."

| # | Title (the message) | Visual |
| --- | --- | --- |
| 1 | *Doing research with AI agents* | Title only, or blank during the show of hands |
| 2 | AI went from finishing our lines of code to running agent teams | Timeline: line completion → chat → cloud agents → multi-agent, multi-tool |
| 3 | *Doing research with AI agents* (structure slide, named after the talk, not "Outline") | Three short labels: the whole stack · context and tools · in the open. Show it again at each transition with the current point highlighted. |
| 4 | Agents now reach across the whole research stack | Seven boxes from teaching to running experiments, then the [five-system showreel](systems/showreel.mp4) (74 s; trim to the OT-2 clip if short on time) |
| 5 | The same agent succeeds or fails on context and tools | Not-so-good and good prompt side by side |
| 6 | Working in the open keeps agents accountable and connects people | The atomizer ping ([DAL #153](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/153)), plus "~7 meetings" as one large number |
| 7 | Book 30 minutes and leave with your first agent running | A large QR code; no "Thank you" or "Questions?" slide |

## Rehearsal

You ended the memo with "it'd be good for me to practice in advance". Doumont's advice for
that:

- Learn the first two and last two sentences word for word. Everything else, learn as an outline.
- Time two full run-throughs aloud against the budget above. If you run long, cut subpoints,
  not the review: Doumont warns against rushing and "sacrific[ing] the review".
- Start straight with the show of hands: no "Well, um, so" and no thanking the organizers first.

## Where each idea from the memo went

| In the memo | In the talk |
| --- | --- |
| The progression from line completion to cloud agents to multi-agent, multi-tool workflows | Need, slide 2 |
| The slide of ways you've used agents: education, admin, literature, writing, coding, planning and running experiments | Point 1, slide 4 |
| "What would be most actionable" for this audience | Planning (why), conclusion |
| Your Codex setup, the QR code to book you or a TA, the GitHub integration, the "CES subscription" | Conclusion, slide 7 |
| Generative CAD example | Point 1 |
| Potential pitfalls | Point 2 |
| Taylor Sparks's post on spinning up one agent after another | Attention-getter option B, or the need |
| Context and tools | Point 2, main message |
| A ping from the atomizer workflow | Point 3, slide 6 |
| Good and not-so-good prompts | Point 2, slide 5 |
| Human connection, transparency, visibility, provenance | Point 3, main message |
| Meetings that came from agent searches and outreach, maybe MRS | Point 3 |
| Practise in advance | Rehearsal |

Nothing from the memo was dropped. Showing the Codex setup itself was folded into the booked
session, since a live demo would take most of the six minutes.
