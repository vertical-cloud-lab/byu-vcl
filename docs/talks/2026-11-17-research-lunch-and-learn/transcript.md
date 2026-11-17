# Voice memo: planning the lightning talk, 2026-11-17

- **Recorded:** Tuesday 2026-11-17, 09:55 MST (5 min 27 s): `Nov 17 at 9-55 AM.m4a` on
  [OneDrive](https://1drv.ms/u/c/5c9b7864c8b38792/IQAo-MNpzi6XS7EPPHmWn1g2AUa8gMK3xc6V-A5jtUvb6p0),
  sha256 `6de26e05…38084fde`. The audio itself is not in the repo.
- **Transcribed with:** Whisper large-v3 (faster-whisper 1.2.1, int8, beam 5, VAD on) on the
  runner, using [`scripts/transcribe_whisper.py`](../../../scripts/transcribe_whisper.py),
  twice:
  - [Pass 1](whisper/pass1.md) uses the default setting, conditioned on previous text.
    It fell into a loop, writing "Yeah." ten times at one-second intervals at 03:29–03:38,
    and lost its punctuation after 04:06.
  - [Pass 2](whisper/pass2.md) adds `--no-condition-on-previous-text`. It has no loop, but
    it drops punctuation in places and heard "generative pad" for "generative CAD".
- **Below:** the two passes reconciled and lightly cleaned for intent. Restarts and fillers
  are dropped. Timestamps come from whichever pass starts a segment there, and are good to
  about ±10 s. Every change to a word is listed in the table
  at the end, so it can be checked against the raw passes.

---

**[00:02]** Giving a six-minute lightning talk today on doing research with AI agents.

**[00:10]** I think it'd still be good for me to start out talking about the progression from line
completion to cloud agents, and now these multi-agent workflows: multi-tool, multi-agent. I
think maybe showing that slide of the different ways in which AI agents can be used, or that I
have used them: with education, like course content; administrative work; literature search
and review; writing; coding; and even experiment planning and execution of experiments.
That's kind of the full stack there, I think.

**[01:05]** Trying to think of what would make the most sense to focus on in terms of the
audience. What would be most actionable. A couple things that could be done.

**[01:21]** Maybe I could show the use of the setup I have with Codex, and invite people to scan
a QR code to set up a time with myself or a TA, to show them how to do this integration on
GitHub with the CES subscription. So that would be one option. Pretty actionable; it could be a
big lift, but it could also mean that we get some more action actually being performed, more
impact from that, I think.

**[02:11]** What else? Research with AI agents. I think showing… oh yeah, that's right, I was
thinking about showing an example, like all the generative CAD that I've done related to this.
It might be good to talk about potential pitfalls.

**[02:40]** Probably I'll go find Taylor Sparks's LinkedIn post about agents, and how it's just
sort of like spinning up one agent after another. It's kind of the new modus operandi.

**[03:16]** Also, just really getting across this idea of context and tools. You know, it could
be interesting to maybe show one of the pings from the atomizer workflow. Perhaps some examples
of good and not-so-good prompts.

**[03:38]** Yeah, I was planning on going over the idea of human connection, transparency,
visibility, and provenance.

**[03:59]** And so I think it would also be good for me to point out maybe the number of
meetings that have resulted directly from these searches and reaching out to people, maybe
including the MRS conference. Let's see, what else?

**[04:45]** Oh, I mean, frankly, that's probably enough. It's maybe more about how to convey
those core points effectively, and within a six-minute time frame. So it'd be good for me to
practice in advance as well.

---

## Changes from the raw passes

| Raw | Here | Basis |
| --- | --- | --- |
| "with education, like, of course, content" (pass 1) | "with education, like course content" | Pass 2. It also fits the list: education → course content. |
| "all generative pad" (pass 2) | "all the generative CAD" | Pass 1 |
| "the new mode of operandum" (both) | "the new modus operandi" | Mis-heard Latin |
| "Yeah." ×10, 03:29–03:38 (pass 1) | dropped | A decoding loop; pass 2 has nothing there |
| "maybe so one of the pings" (pass 2) | "maybe show one of the pings" | Pass 1 |
| "I'll go to go find Taylor's LinkedIn post about, Taylor Sparks' LinkedIn post" | "I'll go find Taylor Sparks's LinkedIn post" | Restart dropped |
| "the the MRS MRS conference" | "the MRS conference" | Repetition dropped |
| "CES subscription" (both) | unchanged | Both passes agree. Confirm the name before it goes on a slide. |
