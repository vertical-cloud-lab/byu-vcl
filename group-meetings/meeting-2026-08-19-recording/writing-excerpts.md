# Every excerpt about **writing**, across the AI-in-the-lab videos

Pulled 2026-09-01 in response to a request on
[PR #184](https://github.com/vertical-cloud-lab/byu-vcl/pull/184): *"pull out all excerpts
from all the videos here … that discuss writing specifically."*

**Sources searched (complete):** the 75:34 meeting recording (Teams transcript +
the Whisper/ECAPA diarized transcript committed here), all seven break-off clips on the
channel (committed faster-whisper VTTs in `highlights/sources/`), the eighth pair
discussion (Audrey & Carl, recorded inside the meeting), and the YouTube auto-captions of
the rest of the channel grab catalogued in [`../ai-in-the-lab.md`](../ai-in-the-lab.md).
Search terms: `writ* / wrote / paper* / manuscript* / draft* / thesis / dissertation /
publish* / publication* / abstract / essay / prose / grammar / proofread* / journal /
article / author* / cite* / citation* / plagiar* / disclos* / declar* / proposal* /
grant* / document* / LaTeX / Overleaf`, then every hit read in context.

## Timestamps and links

The unlisted YouTube upload **`f5_cQvuNKnA` runs 1:15:35 and its timeline matches the
original recording second-for-second** (verified 2026-09-01 against its auto-captions:
first cue "Carl, can you hear me?" at 00:04:52.9 vs. 00:04:52.7 in the original; last cue
"…Thanks everybody." at 01:15:30). Earlier notes in this repo describe that upload as a
62:01 trim — that is not what is published now, so meeting timestamps below link straight
into it and `chapters.txt` applies as-is.

Quotes are ASR output, lightly cleaned. `[bracketed]` words are corrections where the
recogniser clearly mangled a word ("clot" → Claude, "Sparks Note" → SparkNotes) or where a
word is missing; `…` marks a trim. Anything genuinely unintelligible is marked
`[unintelligible]`.

## Attribution

- The Teams transcript separates only the four *call channels*: `@1` Gage (phone), `@2`
  Carl, `@3` **the entire room**, `@4` Audrey. Names for in-room speakers come from the
  committed ECAPA diarization, which cannot separate Andrew / Ronnie / Marcus.
- **The pair clips are not diarized at all** — within a clip the two voices are not
  distinguished, which is why the reels and the highlights cut label them by pair. Where a
  passage is unmistakably the PI's (grant deadlines, group policy), that inference is
  labelled as an inference.

---

# 1. Writing papers — the meeting

### 1.1 "If somebody asks you a question about your paper, you're expected to know everything"
**25:16–25:57 · in the room** (the diarization splits this between Xavier and the
Andrew/Ronnie/Marcus cluster) · [watch](https://youtu.be/f5_cQvuNKnA?t=1516)

> The workloads that we have are different than industry standards, whereas for research,
> if somebody asks you a question about your paper, you're expected to know everything
> about what you just researched. Like, you are considered the expert, and if there's some
> portion of your research that you're like, "oh, I don't know, I [offloaded] it
> [to Claude]" — whatever. In industry, they're like, "yeah, that's fine, as long as it's
> working, it's working." If you say that to another researcher, they're gonna be like,
> "why are you qualified?" … The purpose of a master's or a PhD or a bachelor's is to show
> that you have a certain level of competency.

The ownership premise the rest of the writing discussion rests on.

### 1.2 The balance: writing it yourself vs. backtracking through AI output
**31:30–32:52 · Gage** (ECAPA diarization; Teams has it on the shared room channel `@3`,
so treat the name as the diarization's best guess) ·
[watch](https://youtu.be/f5_cQvuNKnA?t=1890)

> …it's powerful in helping us learn, understand, and also build the ability to think. I
> think it comes to a point when — for example, some of these research papers we've been
> working on, it's all done by AI. And I know the difference of myself personally: like,
> when I write out [a] whole paper, I really understand everything. But when AI writes it
> for me, then I'm going, like, backtracking — okay, what does this mean? I don't know…
> there's so much going on here… It has so much output you're trying to go through, like,
> is this right? Is this right? There's so many assumptions in the stuff — if you construct
> it yourself… there's a vagueness to it. You don't know what the conclusions are coming
> from. And so, personally, I want to find a balance of learning the skills [versus] having
> it do it for me and then applying it to it after that, or with it. I just don't know
> where that balance sits — because people are going to write papers a lot faster than I
> will, if I don't use the AI [to] write the first draft, or whatever it is.

### 1.3 "Writing's been a pretty recurring theme"
**32:53 · Sterling Baird** · [watch](https://youtu.be/f5_cQvuNKnA?t=1973)

> Writing's been a pretty recurring theme. This might be a good segue to…

Said in the meeting itself — the observation this whole document is the receipt for.

### 1.4 "If you have AI do the research and write the paper, then we'd go to a conference to present that paper…"
**35:36–36:08 · in the room** (Andrew / Ronnie / Marcus cluster — not separable) ·
[watch](https://youtu.be/f5_cQvuNKnA?t=2136)

> …yes, if you have AI, like, do the research and write the paper about it, then we'd
> [go to a] conference to present that paper, and it's like — you [don't] know what that
> word means. That's where people get in trouble, and that's where we let it [do the]
> broad things for us. … Yeah — treating it like a TA. "Okay, I want to do this thing, help
> me do this" — especially if that context is for the paper, for … doing more research
> later on.

The clearest statement in the meeting of the failure mode: presenting a paper you cannot
answer questions about.

### 1.5 Audrey, mid-meeting
**39:50 · Audrey Christiansen** · [watch](https://youtu.be/f5_cQvuNKnA?t=2390)

> I don't know if Carl was saying anything, but I was just finishing typing up my essay
> that I wrote.

### 1.6 The abstract that got fed through AI
**43:06–43:35 · Audrey Christiansen** · [watch](https://youtu.be/f5_cQvuNKnA?t=2586) ·
(Audrey & Carl clip time **02:25**)

> Yeah, I'm really worried about the things where we've had a lot of AI generate a lot of
> what we're writing — to the point where, like, I spent a lot of time writing my abstract,
> and we ended up feeding it through AI. It added a bunch of sources and
> [unintelligible] me afterward, and I didn't [think] that was the way to go. I think we
> should have read [those] sources.

The most concrete writing incident anyone reports in the whole corpus: a
human-written abstract, AI-augmented, with citations nobody had read.

### 1.7 The technical-writing class, and declaring AI use
**59:59–1:01:00 · Carl Robison and Audrey Christiansen** ·
[watch](https://youtu.be/f5_cQvuNKnA?t=3599) · (Audrey & Carl clip time **19:18**)

> **Carl:** …the writing class.
> **Audrey:** Yeah, that one's just a lot of work.
> **Carl:** Is it fun, or is it just kind of busy work?
> **Audrey:** Parts of it are fun. I mean, assuming every class has the same kind of flow —
> like, the first project is, you're going to write a set of instructions for someone and
> you need to make it really pretty easy to follow, and stuff like that. And that's
> actually fun. And then you have, like, your assortment of papers that you have to do that
> are less fun, but you get them done and it's whatever.
> **Carl:** Yeah, I feel like that's a good use of AI — to use it to write instructions.
> Like, give it a bunch of data and processes and then have it write the instructions, and
> then just verify that it was good. I don't know… maybe not, though.
> **Audrey:** …you also have to — everything you submit, you have to say what you used AI
> for, and stuff like that. So just make sure, whatever you use it for, **you're comfortable
> declaring [it] to the professor.**

Audrey's closing line is the only disclosure standard anyone articulates in the corpus, and
it is a usable one: *would you be comfortable declaring it?*

### 1.8 "Lab culture involving reading the source manuscript material"
**1:09:01–1:09:33 · Sterling Baird** · [watch](https://youtu.be/f5_cQvuNKnA?t=4141)

> I think lab culture involving reading the source manuscript material and — I don't know
> how you feel about this, but maybe, like, spend time with the manuscripts. Maybe say it's
> still okay if you're, like, pinging [Claude] to help with things, but while you're
> waiting, it's like, keep reading… have the PDF of the manuscripts — the really core
> manuscripts that you want to understand — in front of you.

### 1.9 The summarisation loop, and the closing line
**1:10:34–1:11:13 · in the room** (Teams `@3`; the diarization splits it across room
voices) · [watch](https://youtu.be/f5_cQvuNKnA?t=4234)

> …this idea of summary is dangerous. If I do research and have AI write it in
> scienti[fic] language and get a paper, somebody takes that paper and has AI summarize it
> out of scien[tific language] — you know, it's like, why are we taking all these steps?
> You need to be able to read the stuff and get right there, right? — in both the writing
> and [the reading]. And if we let AI… AIs talking to different AIs about research, then
> that's a self-directed lab, that's not [our] research. We want to get to the point where
> we have [automated] the stuff that we don't [want to] be doing, **so that we can do
> research, read the papers, write the papers.**

The meeting's last word on writing, thirty seconds before the wrap-up — and the tidiest
statement of the thesis: automate what you don't want to do *so that* the writing stays
yours.

---

# 2. Writing papers — the break-off clips

## 2.1 Ben Whitney & Sterling Baird — lab culture with AI
[`Ef0jl63-rLg`](https://www.youtube.com/watch?v=Ef0jl63-rLg) · not diarized; speaker
inferences are marked

### "Where does AI play a role in that, and what's the culture around that?"
**2:00–2:25** · [watch](https://youtu.be/Ef0jl63-rLg?t=120)

> And I think a big thing that a lot of people in this lab are talking about — and I think
> is a really great point — is, when it comes to **writing papers** and preparing for
> presentations, doing things like that, where [does] AI play [a] role [in] that, and
> what's [the] culture around that? I think that's been the main topic of interest for most
> people that have been bringing this up.

*Almost certainly Sterling* (surveying what the lab is saying).

### The rush to get papers out — and the pressure behind it
**2:28–3:15** · [watch](https://youtu.be/Ef0jl63-rLg?t=148)

> And I think I've had a certain rush that I felt with the summer — with getting some early
> papers out, with graduation timelines for some people that are going to be applying to
> grad school. And **having a publication is a very big deal for grad school.** Like, it's
> not like you can't get into grad school without publications, but it can really set you
> apart. So some of these timelines are on my mind, and I think I felt a certain rush:
> like, okay, let's get these papers out. Let's write some grants based on those. So I
> think that it would also be too easy for me to just stay in that mindset — and be like,
> "well, that's just… let's just keep doing that."

*Almost certainly Sterling* — grant-writing and student graduation timelines are the PI's.
Notable as the only place anyone names the **incentive** that makes AI-written papers
tempting, and names it as their own.

### The concrete proposal: AI writes the first draft, you read it to find what you don't know
**4:21–4:50** · [watch](https://youtu.be/Ef0jl63-rLg?t=260) — *this is the bite used in
reel 03 (`first-draft`)*

> I wonder if there could be some form of, like — **AI could write the first draft of a
> paper that then we read and really understand.** And if there are things that we don't
> understand, either have [it] tell AI, like, "we don't need to talk about that," or really
> dig deep. Because I think AI could give us a map, and help us in that process of figuring
> out what we don't really understand and what we don't really [want to] talk about.

### Staged gates on the manuscript
**5:42–6:06** · [watch](https://youtu.be/Ef0jl63-rLg?t=342)

> I think maybe on the manuscript side, it could be that we have these kind of **staged
> gates** of: okay, yes, here's the first draft — go in and have your *learning* iteration.
> Like, "I'm not here to make revisions on the draft, I'm here to understand what's here,"
> to then be able to make better revisions [at] the second step.

The most actionable writing-process idea anywhere in the corpus: split the first pass into
a *comprehension* pass and a *revision* pass, and say out loud which one you're in.

## 2.2 Gage Erickson & Ronnie — AI lab culture
[`bIONIUZDsMk`](https://www.youtube.com/watch?v=bIONIUZDsMk) · not diarized

**1:41–2:35** · [watch](https://youtu.be/bIONIUZDsMk?t=98)

> …there's also a lot of specific use cases where it makes a lot of sense to use AI. Like,
> instead of doing a four-hour Google search session for gathering research and compiling
> it, you can have it [do that]. — Dude, that's a really powerful use of AI… there's a lot
> more benefit there than what it takes away — **versus other cases, like actually writing
> the paper.** — Yeah. **Maybe for a first draft**, but I think there's a lot more benefit
> for the… lab assistant to do that themselves, and then **have AI as an assistant to help
> facilitate writing**. And so I think you're totally right with that, and making that the
> lab culture — making that the understanding when people come [in]: this is how we use AI.
> — Yeah, and that helps you get the background to do [your] research, because it's giving
> you information, it's not doing the research for you. Like, **you're not going to be
> publishing on what already exists.**

The other independent arrival at "first draft, but you finish it" — reached by two
students, in a different room, from the one Ben & Sterling reached. Worth noting that the
two pairs converged.

## 2.3 Xavier Zaitzeff & Sam Charles
[`rwoLhubyzZo`](https://www.youtube.com/watch?v=rwoLhubyzZo) — see §3; their "writing" is
code, not prose.

## 2.4 Andrew & Marcus
[`VwOiijuXEP8`](https://www.youtube.com/watch?v=VwOiijuXEP8) (lab culture) and
[`ndbG_nHQljc`](https://www.youtube.com/watch?v=ndbG_nHQljc) (positive experiences), and the
Gage & Ronnie Short [`s5ptE--EVIk`](https://www.youtube.com/watch?v=s5ptE--EVIk): **no
discussion of writing.** The nearest is Andrew & Marcus asking Claude for source papers —
reading, not writing (§4.1).

---

# 3. "Writing" as in writing **code**

Same verb, different activity — separated out so it doesn't inflate the count above. The
argument is nevertheless the same one.

### Carl: generate the code, then go back and understand it
**44:32–44:59 · Carl Robison** · [watch](https://youtu.be/f5_cQvuNKnA?t=2672) · (Audrey &
Carl clip time **03:50**)

> I've also found it super useful to be able to write code and stuff with it — but when
> doing that, I think it's essential to go back and actually understand what the code is
> doing. So, like, I'll use AI and generate a ton of code, and then I'll go back through all
> of it and figure out what the heck it just did, and what I want to change or what I need
> to optimize. Because it doesn't usually get it quite right.

### Audrey: better to write it herself
**50:03–50:53 · Audrey Christiansen** · [watch](https://youtu.be/f5_cQvuNKnA?t=3003) ·
(clip time **10:02**)

> …it can be super helpful for code. I mean, I've been a little more careful with generating
> so much code at once, because often it'll come up with, like, a function or something that
> I haven't ever used before, and I'll be like, "hey, what's that?" And then it takes a
> little more time, but then you're still learning with it. But often it can feel a little
> like you're trying to catch up to where AI is at, and you're never going to get to that
> point — but you learn a lot. **But I think it's ultimately better writing my own code,
> because then I know exactly how it works and how I want it to be working.**

### Xavier & Sam: Claude writes the code that runs the experiments
**0:32–0:41 and 1:06–1:22** · [watch](https://youtu.be/rwoLhubyzZo?t=32) ·
[watch](https://youtu.be/rwoLhubyzZo?t=66)

> For the powder doser, it's been [Claude] controlling the whole thing — **writing the code
> that does the tests**, and running the tests.

> The scary part of that is that… even if I think I could probably figure out somewhat
> quickly how to run the powder doser myself and **write the code**, I have not done that,
> and I don't currently know. Like, if you asked me to do it myself, I couldn't do it right
> now. It would take me a couple of days, probably. …Yeah, that's scary.

### Ben & Sterling: learning to write the protocol files
**0:48–1:20** · [watch](https://youtu.be/I0jG2o6wthg?t=45)

> It'll help me understand what's been *written* already in Alex's whole GitHub repository
> of, like, Cubware, CubOS — and help me understand how to use that tool, to where now I
> understand the machinery of a gantry, which I didn't before… I understand the YAML files
> that go into the protocols that we do, **and how to write those myself**. And so when I
> ping Claude to do these things, I know exactly what it's doing.

---

# 4. Writing-adjacent, included because they came up in the same breath

### 4.1 Reading papers instead of a "SparkNotes education"
**1:07:16–1:09:00 · Xavier Zaitzeff** · [watch](https://youtu.be/f5_cQvuNKnA?t=4036)

> Something Sam and I talked about was making a bigger commitment to reading recent,
> relevant research papers. … I read them, I look at the code, and I'm like, "okay, I think
> I need to do this," and then I read them again and I'm like, "oh, I didn't read this
> closely enough" … and that has helped me understand exactly what the code is doing. And
> it avoids me having just a **summary education** of the topic — which is currently how we
> use AI: "give me the SparkNotes version." And so then you get a SparkNotes education of
> that. But then you read another paper that you'd still be expected to understand, and
> because you only have a SparkNotes version of that, you don't know the details… and so you
> ask for a SparkNotes education of *that*, and so you miss out on having a good-quality
> education of the topic broadly.

Reading, not writing — but it is the passage §1.9 immediately answers, and it sets up
"read the papers, write the papers."

Also Xavier's anecdote at **1:09:34** ([watch](https://youtu.be/f5_cQvuNKnA?t=4174)):
finishing his last *math paper*, he had Claude search for theorems of three specific types,
read the five results per type himself, and found the one that made the proof work — "it is
really good at finding relevant papers, but giving them out, it probably doesn't do as well
[a] job."

### 4.2 Andrew & Marcus: asking for source papers rather than for the answer
**0:34–1:06** · [watch](https://youtu.be/ndbG_nHQljc?t=34)

> So instead of just asking it what to do next, what we did was we asked, like, "how does
> this work? What are you doing with this? **Give us some source papers**" … And it provided
> back a lot of stuff that obviously I had to go through and, like, source-check. But the
> papers and stuff that it provided were pretty good, because I could go and find these
> papers and see how they relate. Are they good?

### 4.3 A workflow for giving feedback on a paper
**3:44–4:20 · Ben & Sterling** (*almost certainly Sterling*, describing his own pipeline) ·
[watch](https://youtu.be/I0jG2o6wthg?t=224)

> If you're doing, like, a feedback of a paper, or reviewing anything where there's a visual
> component and an auditory component — like your own feedback and then some visual thing —
> [it] just makes a whole spec document with screenshots and your timestamped comments, that
> it can then go and iterate through. And that feels like a freeing thing, because you can
> just talk and click and point, **and you don't have to write down everything that you're
> [saying]**.

### 4.4 Elsewhere on the channel

The rest of the grab was swept exhaustively: **all 164 catalogued video IDs** were run
through `yt-dlp` on the stream-cam Pi (YouTube bot-gates the runner's datacenter IP), which
returned **92 English auto-caption tracks** — the other 72 have no captions, being silent
equipment, print and powder-handling clips. Every caption track was run through the same
keyword search and every hit read in context. Beyond the AI-in-the-lab set, **five** videos
have real writing content; three of them substantially:

**[Are AI-generated scientific overview and workflow figures for manuscripts and proposals
any good?](https://www.youtube.com/watch?v=Gb3Yymp_TOM)** (2026-04-01, 2:40) — the whole
video is an answer, and the answer is "not really":

> I ended up saying, "okay, gave you this other chance — still no," [and] went back to just
> sort of drawing on pen and paper, trying to draft something out, and then I started
> converging on something that started to feel a little bit more natural for conveying this.
> ([0:26](https://youtu.be/Gb3Yymp_TOM?t=26))

> Figures [have] still a lot of room [to improve], especially for, like, manuscripts and
> proposals. At best they can kind of do, like, semi-decent Mermaid chart figures. There was
> one kind of similar that did make it into the final proposal… not amazing, but still…
> ([1:43](https://youtu.be/Gb3Yymp_TOM?t=103))

> It['s] easy to pick out when you've just used some, like, ChatGPT or DALL·E-3-generated
> image, and so I'd avoid using that very much, at least in manuscripts and proposals and
> the like. ([2:24](https://youtu.be/Gb3Yymp_TOM?t=144))

**[Agentic manuscript & Proposal development](https://www.youtube.com/watch?v=Ri81slJ6FQY)**
(2026-07-22, 1:22:00) — the only other video whose *subject* is writing, but it is a **live
build session, not a discussion about writing**: an experimental result is handed to a
Copilot agent through a GitHub issue, with Edison literature queries in parallel. The
writing-specific moments are procedural:

- **2:00** — designing the test honestly: *"it's a good test case because this is also a
  historical paper from ACS. So we're not going to tell [it] the paper… we'll probably do
  both. One where we tell [it] the paper, one where we don't."*
  ([watch](https://youtu.be/Ri81slJ6FQY?t=120))
- **13:20** — the manuscript PDF containing the answer gets uploaded by accident and is
  pulled back out so the test isn't contaminated. ([watch](https://youtu.be/Ri81slJ6FQY?t=800))
- **23:29** — *"to clarify: when you're making these proposals, for any sort of document,
  it's all living in this one repo?"* — the answer being one issue and one pull request per
  thread, each agent seeing its own thread's context.
  ([watch](https://youtu.be/Ri81slJ6FQY?t=1409))

**[Testing Generative AI in Zoo CAD software to design a simple
part](https://www.youtube.com/watch?v=DwFI1eQ_3bI)** (2026-06-09, 1:03:26) — the title is
about CAD, but the session drifts into publishing, and at **44:41–46:24** contains the
clearest explanation of peer review anywhere on the channel
([watch](https://youtu.be/DwFI1eQ_3bI?t=2681)):

> **Q:** Is it common, when submitting papers, that they find something, you send it back,
> you find something, you send it back…?
> **A:** …[reviewers] give technical feedback on it, and so that can happen a couple times.
> It can end with the manuscript… it could get rejected when you send it to the editor and
> they say "this is just out of scope," or "we all want to reject this"… if all three
> reviewers that were asked say "do not publish, just reject this," then the editor will
> just come back and say it's rejected. Or they might say "revise it, but do major
> revisions on it — here are the revisions that we want you to do." And then it goes back
> to the authors. The authors make revisions, they send it back. And that can technically go
> on as many times [as needed].

The same session also works through **who counts as an author** on a Zenodo record versus on
the paper (**46:24**, [watch](https://youtu.be/DwFI1eQ_3bI?t=2784)): *"not everybody that
was listed here became a co-author on the paper."*

Two more, from the two "featured" talks in the compilation rather than from the lab's own
equipment clips:

- **[So, you want to build a self-driving lab?](https://www.youtube.com/watch?v=hvY3WE0XEoY)**
  (46:04) names the tension every one of these builds sits in, at **34:00**
  ([watch](https://youtu.be/hvY3WE0XEoY?t=2035)): *"how do I manage the tension between what I
  build — that infrastructural output — versus **my actual scientific output when I'm writing
  publications**?"*
- **[Your GitHub Repo Is Now a Research Robot](https://www.youtube.com/watch?v=U5sB19DLnOk)**
  (Taylor Sparks, 37:14) touches writing only as plumbing: Asta's literature-grounded
  hypothesis generation *"which you could use for things like **proposal background
  research**, identifying prior work, or generating candidate research directions"*
  (**22:54**, [watch](https://youtu.be/U5sB19DLnOk?t=1374)); *"did you finish your lit review?
  Now provide me a summary and write it to somewhere"* (**18:53**); and Zenodo as
  *"agent-driven FAIR data publishing — it'll push datasets, it'll even mint new DOIs"*
  (**33:36**). Most of its `write`/`author` matches are **write access** and **OAuth**, not
  writing.

Everything else in the grab that matches the keywords matches them in a non-writing sense —
"writing a file" during calibration, MQTT "published" messages, "the steps [are already]
written" for a setup procedure, a Fusion "program that … Fusion has written." The 3:07
[Trying out zoo design studio](https://www.youtube.com/watch?v=6YsOMIsOfkY) working session
has passing mentions of a paper, authors and "so many manuscript[s]," but its auto-captions
are too garbled by overlapping conversation to quote responsibly.

---

# 5. What the current cuts do with all this

Of the excerpts above, **exactly two are in any released cut**:

| Excerpt | Where |
|---|---|
| §1.2 the balance (31:44–32:41) | `papers-balance`, in the 9:56 landscape highlights cut only |
| §2.1 AI writes the first draft (4:21–4:50) | `first-draft`, in reel 03 (Ben & Sterling) |

Everything else — Audrey's abstract, the declare-it-to-the-professor standard, the staged
gates, "you're not going to be publishing on what already exists," and the whole
"read the papers, write the papers" close — is **not in any Short or in the long-form cut**.
`papers-balance` was already flagged as the one highlights item the portrait set doesn't
cover; on this evidence there is enough material here for a self-contained Short about
writing, drawing on at least three of the eight pair discussions plus the meeting close.
