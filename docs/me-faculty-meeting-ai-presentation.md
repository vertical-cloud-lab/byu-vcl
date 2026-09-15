# AI in the Vertical Cloud Lab — 15 minutes for the ME faculty meeting

Prepared for a 15-minute slot in a BYU Mechanical Engineering department faculty meeting.
Source material: the public `vertical-cloud-lab` GitHub org (plus `sparks-baird`,
`AC-BO-Hackathon`, and `borysgroup` repos), Elder Gerrit W. Gong's August 2026 counsel to
BYU faculty, and Anthropic's model-selection guidance.

**Audience assumptions.** Mixed AI experience. Essentially everyone has access to the CES
ChatGPT enterprise workspace; a minority hold personal Claude/ChatGPT subscriptions; a few
are already running agents. Nobody needs to be sold on "AI is coming." What they need is a
principled frame, evidence it works in a real lab, and one concrete thing to do on Monday.

> **Verify before presenting:** the Elder Gong quotations below were gathered from the
> Herald Extra report and the speeches.byu.edu transcript. Check each against the official
> transcript, and confirm the CES workspace's data-handling terms with CES/OIT rather than
> relying on this document, before repeating either from the podium.

---

## The argument in one sentence

The most valuable thing AI did in this lab was not write code — it **manufactured human
conversations that would not otherwise have happened**, and the lab's job has been to keep
the humans, not the artifacts, at the center.

That is Elder Gong's thesis, arrived at independently from the direction of a machine shop.

---

## Timing plan (15:00)

| # | Segment | Time | Running |
|---|---|---|---|
| 1 | Cold open: the number, and why it's the wrong number | 1:00 | 1:00 |
| 2 | Elder Gong's frame — the rubric for everything after | 1:30 | 2:30 |
| 3 | **Thread 1: AI that produces human contact** (3 worked examples) | 4:00 | 6:30 |
| 4 | **Thread 2: outputs vs. outcomes** — provenance as pedagogy | 2:30 | 9:00 |
| 5 | **Thread 3: model choice, effort, and what it costs** | 3:30 | 12:30 |
| 6 | Three invitations | 1:30 | 14:00 |
| 7 | Close | 1:00 | 15:00 |

Q&A assumed to be outside the 15 minutes; see the backup section for the questions that
will actually come.

---

## 1. Cold open (1:00)

One slide, four numbers, from the public repos:

- **~1,340** human `@claude` pings across five public lab repos
- **20+** distinct human contributors — nearly all undergraduate and graduate research students
- **526** agentic sessions on the tensegrity project alone
- **$2,736** of API-list-equivalent AI work on that project, of which **~$410** was actually paid

Then take the number away:

> "I could stand here and tell you we got $2,700 of work for $410. That's true, and it's the
> least interesting thing I learned. The interesting thing is what the students did with the
> time it gave back — which turned out to be *talking to people*."

Cite: [`tensegrity-optimization#103`](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/103)
— a full audit, priced per-run at time of expenditure from CI logs, not an extrapolation.

---

## 2. Elder Gong's frame (1:30)

At [BYU University Conference, 24 August 2026](https://www.heraldextra.com/news/2026/aug/26/we-can-embrace-this-opportunity-elder-gong-counsels-professors-on-ai-use-at-byu/),
Elder Gong called AI one of the "greatest opportunities" for BYU and CES — and gave faculty
a rubric rather than a rule.

**The permission.**
> "To me, it is hard to completely ban AI from our classrooms" — and still expect students to
> learn to use it responsibly.

**The charge.**
> "We can embrace this opportunity. It gives us an opportunity to reexamine, reimagine and
> reaffirm our educational principles."

**His four framing questions** — worth putting on the slide verbatim, because they scale from
a single assignment to the university:
1. How should AI influence students and faculty — literacy, policies, preparation?
2. How should AI influence courses, disciplines, and degrees?
3. How should AI influence BYU's principles, curriculum, pedagogy, assessment, career prep?
4. How can BYU contribute to the conversation on human identity, dignity, and flourishing?

**The two lines to hang the rest of the talk on** (from
[*Becoming BYU in an Age of Artificial Intelligence*](https://speeches.byu.edu/talks/gerrit-w-gong/becoming-byu-in-an-age-of-artificial-intelligence/)):

- **Outputs vs. outcomes.** When the final artifact stops being a reliable indicator of
  learning, "the journey of development takes on greater significance." Guard against
  "metacognitive laziness" and "cognitive offloading."
- **Human relationships are at their core.** Elder Gong's own illustration is a list of BYU
  faculty who blessed him by name. His institutional phrase: **"No one sits alone."**

> Transition line: "I want to show you three times an AI agent's actual output was a *list of
> people to go talk to* — and what happened when students went and talked to them."

---

## 3. Thread 1 — AI that produces human contact (4:00)

This is the heart of the talk. Three examples, each a complete loop: **prompt → shortlist →
a student's own email → a real human reply → a judgment only the student could make.**

### Example A — "Who should Ronnie reach out to?"

**The prompt** ([`caliber#10`](https://github.com/vertical-cloud-lab/caliber/issues/10), 19 Aug 2026):

> "Would be good to get a short-list of folks for Ronnie to reach out to early on."

The agent read ~140 issues and PRs across a *different* repo and returned a ranked table:
who, why they're relevant, and — the column that matters — **"Warm intro?"** It found that
Mike Standing in the BYU Electron Microscopy Facility had already trained the team and had
already been flagged for a collaboration letter; that Kevin Rey in Geology had run the XRF
tests and "responds quickly to emails"; that Prof. Devin Rappleye in ChemE was already a
student's relative. It closed with **"Suggested top 3 for Ronnie this week."**

**Why this is the Gong point, not a productivity point:** the agent's deliverable was not an
answer. It was *an introduction it could not itself make*. Every row ends at a conversation
between two people. It also honestly flagged what it couldn't verify — two contacts known
only by first name, a surname spelled two ways — and said: confirm before formal outreach.

### Example B — The reply that saved a year

**The prompt** ([`byu-vcl#106`](https://github.com/vertical-cloud-lab/byu-vcl/issues/106), 3 Jul 2026)
— note that this one is addressed to a *student*, not to the agent:

> "@gage-erickson could you reach out to the SEM folks to get some more info on how they're
> running the SEMs as a cost recovery center / user facility from BYU's perspective? … For
> subject line, could use 'Equipment cost recovery / external user fees.'"

**The outcome, four days later, in Gage's words:** the SEM lab director explained that
university-wide, cost-recovery centers are *highly discouraged* — the SEM lab is grandfathered
in. The reasons are institutional and non-obvious: how the federal government perceives a
university using granted money in ways that undercut industry; BYU policy that the machine's
primary purpose is student learning. He was told they'd have to deliberately charge *more*
than industry to prove they weren't competing.

**Make this the emotional center of the talk.** No model, no web search, and no amount of
context would have produced that answer. It existed only inside one administrator's head, and
the only retrieval mechanism was a 20-year-old technology: a student walking down the hall to
ask. What the AI-saturated workflow did was *free up the student's week so he could*.

### Example C — The student who volunteered

[`byu-vcl#135`](https://github.com/vertical-cloud-lab/byu-vcl/issues/135) — need Archimedes
density measurements on 5 mm cubes. Seth Leavitt searched BYU's ScholarsArchive, found a
dissertation describing exactly such a device, and wrote:

> "If you'd like I can reach out and see if it's a physical device we could use or if they
> just have a design that we could use."

One line, easy to skip. It is what a healthy lab culture sounds like: a student's instinct on
encountering a gap is *to find the person*. Worth saying plainly that AI didn't do this — but
the lab norm of "the next step is a named human" is what AI use was trained around.

### The pattern, stated for the audience

| The agent does | The human does |
|---|---|
| Read 140 issues nobody has time to re-read | Send the email in their own voice |
| Rank by relevance and by *warmth of existing tie* | Sustain the relationship afterward |
| Say honestly what it could not verify | Exercise the judgment call |
| Draft, so a blank page never blocks outreach | Own the words and the consequences |

**Net effect: more human contact, not less.** And a governing norm worth stealing, from
[`byu-vcl#137`](https://github.com/vertical-cloud-lab/byu-vcl/issues/137) — when a student
reported an external collaborator's reply, the follow-up was immediate:

> "For provenance, could you include what your query was?"

The student posted his exact query. That thread now contains both sides of a real scholarly
correspondence with Trinity College Dublin, including the student's own conclusion that the
technology was too early-stage to help — **a negative result, reasoned to by a human, written
down.** That is an outcome, not an output.

---

## 4. Thread 2 — outputs vs. outcomes (2:30)

Elder Gong's warning is that artifacts stop certifying learning. The lab's answer has been to
make the *process* the artifact.

**Provenance is not bureaucracy; it's the assessment instrument.** Every agent run in these
repos posts its own todo list, links its CI job log, its branch, and its measured cost. Every
outreach thread records the query, not just the reply. A reader six months later can
reconstruct who decided what, on what evidence, and where the reasoning was thin. That
transcript is far more diagnostic of a student's thinking than a polished final report.

**Onboarding is now a first-class artifact.**
[`powder-doser#160`](https://github.com/vertical-cloud-lab/powder-doser/issues/160) —
"Provide an orientation to a new research student" — produced an orientation document mined
from the project's own history: a two-era narrative, a **"who leads what"** section naming
seven students and what each owns, and a first-week checklist. Two things to say about it:

- It names *people*, so a new student's map of the project is a map of colleagues. "No one
  sits alone," implemented as documentation.
- It credits the agents as part of the methodology (~460 Copilot commits, ~240 Claude) rather
  than hiding them. Honesty about authorship is the integrity move.

**Students in their own words.** If there's a projector, 30–60 seconds of one clip beats any
claim you can make. From the lab's channel (all 19 Aug 2026):
[AI and lab culture — Andrew & Marcus](https://www.youtube.com/watch?v=VwOiijuXEP8) ·
[Positive AI experiences — Andrew & Marcus](https://www.youtube.com/watch?v=ndbG_nHQljc) ·
[AI lab culture — Gage & Ronnie](https://www.youtube.com/watch?v=bIONIUZDsMk) ·
[When AI has helped enhance learning — Ben Whitney](https://www.youtube.com/watch?v=I0jG2o6wthg).
Pedagogy angle: [20 parallel agents re-designing a mechanical engineering course](https://www.youtube.com/watch?v=AIwn68hZQRE).

**The honest caveat — do not skip this slide.** Faculty trust is earned by naming the failure
mode. The orientation doc itself warns that `main` holds only a fraction of the work: **130+
branches and 35+ open PRs**, with real calibration data stranded on agent branches. Across
the org, agents authored the large majority of pull requests. Unreviewed agent output is not
progress; it is debt with good grammar. The bottleneck moved from *producing* to *curating*,
and curating is irreducibly human. Say it out loud:

> "If I've learned one hard lesson, it's that an agent can generate work faster than a lab can
> absorb it. The scarce resource is now human attention, and I've spent some of mine badly."

---

## 5. Thread 3 — model choice, effort, and what it costs (3:30)

Shift register here: this is the section faculty will take notes on.

### The four axes

Anthropic's own [model-selection guidance](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model)
frames the choice as **capability, speed, cost, and effort**. Most people know the first
three and have never heard of the fourth.

> **Effort is the underused dial.** "Tuning effort is often a better lever than switching
> models." Same model, dialed from low to high, trades intelligence against latency and cost.
> Before you conclude a model can't do your task, raise the effort.

### Two legitimate starting strategies

| Strategy | Start with | When it's right |
|---|---|---|
| **Efficiency-first** | Haiku 4.5, upgrade only on a demonstrated gap | Prototyping, high-volume, latency-sensitive, cost-sensitive |
| **Capability-first** | Opus 5, then optimize down (lower effort, cheaper model) | Complex reasoning, scientific work, long-horizon agentic work |

Current lineup, list prices per million tokens (in / out): **Fable 5.1** $10/$50 ·
**Opus 5** $5/$25 · **Sonnet 5** $2/$10 · **Haiku 4.5** $1/$5. Batch requests are 50% off;
cache reads cost a fraction of base input. The academic-relevant note: a 1M-token context
window is roughly 555k words — an entire thesis plus its references, in one prompt.

### What it actually cost us — measured, not modeled

From the [`tensegrity-optimization#103`](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/103) audit:

| Model | Runs | Total | Avg/run |
|---|---|---|---|
| Fable 5 | 170 | $1,270 | $7.47 |
| Opus 5 | 54 | $289 | $5.35 |
| Opus 4.8 | 35 | $89 | $2.54 |
| Sonnet 5 | 7 | $15 | $2.17 |

Four lessons on one slide:

1. **The distribution is heavy-tailed.** Median run $3.59, mean $6.25 — and the single most
   expensive run was **$118.98** (320 turns, on a journal paper). Budget for the tail.
2. **The premium model was 76% of spend** for 64% of runs — it costs more per token *and*
   runs longer. Defaulting to the best model is a compounding decision, not a linear one.
3. **The instrument matters more than the model.** ~$2,736 at list prices; **~$410 actually
   paid** — because the work ran on flat-rate subscriptions rather than metered API. A ~6.7×
   difference driven purely by billing structure.
4. **Pricing regimes move under you.** The same Copilot usage that cost ~$10 under legacy
   per-request billing would cost ~$1,000 under usage-based credits — roughly 100×. Don't
   build a research plan on this year's price sheet.

### What this means for *this* room

- **The CES ChatGPT enterprise workspace is the floor everyone already has.** It's the right
  default for drafting, summarizing, and coursework help, and the enterprise agreement is the
  reason to prefer it over a personal account for anything touching student data. Confirm the
  specific terms with CES/OIT — don't take my word for it, and don't assume a personal
  subscription carries the same protections.
- **Agentic coding is where a personal subscription still buys something distinct.** Everything
  in this talk ran through agents with repository access and tool use — a different product
  category from a chat window. If you want to try that, a flat-rate subscription is the sane
  instrument.
- **Do not put a metered API key on a personal card without a spend alarm.** One 320-turn run
  was $119. The failure mode is real, and it is silent.
- **Don't model-shop; build a two-case eval.** Anthropic's own advice is that a good
  evaluation set "is the most important step." Two real tasks you can grade in five minutes
  will outperform any benchmark table for your discipline.
- **Match the model to the stakes, not to the prestige.** Sonnet or Haiku for bulk
  summarizing and triage; frontier models for genuinely long-horizon reasoning. The
  multi-model pattern — cheap worker, expensive advisor — is standard practice, not a hack.

---

## 6. Three invitations (1:30)

Frame them as Elder Gong's, not yours.

1. **Write the policy — one line is enough.** His words: *"Have an AI policy in your class. It
   may be as direct as 'Do your own work.'"* The failure is silence, which students correctly
   read as either prohibition or permission depending on what they wanted to hear.
2. **Get first-hand familiarity, on one real task, this month.** Not a demo. Something you
   actually owe someone — a review, a reconciliation, a literature scan. You cannot supervise
   a tool you have never driven, and our students are already driving it.
3. **Keep the provenance.** Ask for the prompt alongside the result, the way we ask for a
   method alongside a measurement. It costs one sentence and it converts an ungradeable output
   into a legible outcome.

And a fourth, if you want the lab-specific ask: **the "who should I reach out to" prompt is
free, and it works.** Point an assistant at your own last two years of notes, proposals, and
email and ask who you've under-followed-up with. The output is a list of people. The value is
entirely in whether you call them.

---

## 7. Close (1:00)

Return to the opening number, then refuse it:

> Elder Gong reminded us that **"AI is not human. AI is mathematical algorithms, and
> mathematical algorithms are not alive."** Everything I showed you today was algorithms. The
> parts that mattered were all people: a student emailing Dublin and reasoning his way to a
> negative result. An administrator explaining why cost recovery would jeopardize federal
> funding. A student volunteering to go find a device someone built here a decade ago.
>
> The agents didn't replace a single one of those conversations. They *scheduled* them.
>
> Elder Gong's invitation was to define ourselves "not by what AI is or isn't but by what we
> as children of God are uniquely meant to be and become." In a lab, the practical form of
> that is almost embarrassingly simple: **when the machine hands you a list of names, go talk
> to them.**

---

## Backup — the questions that will actually come

**"How do you know the students are learning and not just prompting?"**
You read the transcript, not the artifact. The provenance norm — prompt recorded next to
result — is what makes the difference visible. Example B is the proof case: the agent produced
no part of that insight; a student's conversation did, and the thread shows it.

**"Isn't this just outsourcing your literature review?"**
Sometimes, and it must be checked. In [`byu-vcl#199`](https://github.com/vertical-cloud-lab/byu-vcl/issues/199)
a follow-up pass verified AI-generated literature claims against full article text and found
material errors — a dataset's trajectories were simulation-injected rather than real, a
repository described as closed was actually BSD-3-licensed. Verification is not optional, and
budgeting for it is part of the method.

**"What about student data, FERPA, confidentiality?"**
Use the enterprise workspace for anything involving student work, and confirm the terms with
CES/OIT. Separately: assume anything in a prompt may be logged. This lab treats credentials as
a hard boundary — [`byu-vcl#196`](https://github.com/vertical-cloud-lab/byu-vcl/issues/196)
documents an explicit allowlist so an agent cannot enumerate or read secrets it wasn't
granted, and it fails closed. Design the boundary before you need it.

**"What did this cost you in time, not dollars?"**
Real, and worth conceding. 130+ branches and 35+ open PRs of partially-absorbed work. The
bottleneck moved to human review, and review capacity did not grow.

**"Which should I use — ChatGPT or Claude?"**
For chat, the one your institution already licenses. For agentic work against a repository,
the tooling matters more than the model; that's a different product, and worth a separate
conversation over lunch.

**"Won't this widen the gap between students who pay and those who don't?"**
The most acute equity issue in the room. Everything shown here ran on public repositories with
free CI, which is precisely why it's reproducible by a student with no subscription. If you
assign AI-dependent work, assign it on infrastructure the department provides.

---

## Sources

- Elder Gerrit W. Gong, [*Becoming BYU in an Age of Artificial Intelligence*](https://speeches.byu.edu/talks/gerrit-w-gong/becoming-byu-in-an-age-of-artificial-intelligence/), BYU University Conference, 24 Aug 2026
- Herald Extra, [*"We can embrace this opportunity": Elder Gong counsels professors on AI use at BYU*](https://www.heraldextra.com/news/2026/aug/26/we-can-embrace-this-opportunity-elder-gong-counsels-professors-on-ai-use-at-byu/), 26 Aug 2026
- Anthropic, [Choosing the right model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model) and [Models overview](https://platform.claude.com/docs/en/models/overview)
- [`tensegrity-optimization#103`](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/103) — AI cost audit
- [`caliber#10`](https://github.com/vertical-cloud-lab/caliber/issues/10) — reviewer/collaborator shortlist
- [`byu-vcl#106`](https://github.com/vertical-cloud-lab/byu-vcl/issues/106) — cost-recovery outreach
- [`byu-vcl#135`](https://github.com/vertical-cloud-lab/byu-vcl/issues/135) · [`byu-vcl#137`](https://github.com/vertical-cloud-lab/byu-vcl/issues/137) · [`byu-vcl#196`](https://github.com/vertical-cloud-lab/byu-vcl/issues/196) · [`byu-vcl#199`](https://github.com/vertical-cloud-lab/byu-vcl/issues/199) · [`powder-doser#160`](https://github.com/vertical-cloud-lab/powder-doser/issues/160)
