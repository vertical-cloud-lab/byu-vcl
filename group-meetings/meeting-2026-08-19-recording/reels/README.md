# AI-in-the-lab reels (2026-08-19 meeting + breakouts)

Seven vertical (1080×1920) quote-driven cuts of the 2026-08-19 meeting and its breakout
pair discussions, in a **"next-episode preview" style** (the Frieren end-credits idea from
[PR #184](https://github.com/vertical-cloud-lab/byu-vcl/pull/184)): snippets of the actual
voices play while the quote text appears on screen **word-by-word in sync with the audio**,
on a black frame with a live waveform — or over the footage itself for the clips with real
framing (Xavier & Sam; the Gage & Ronnie Short) and the "Don't film me" cold open. Unlike
the long-form [highlights](../highlights/) (which keeps whole passages intact), these are
**"reels-style" micro-edited**: filler words (um/uh, stray *you know*s), false starts,
stutters, and dead air are removed with word-level cuts, so the density is high but every
word is still the speaker's own.

![Contact sheet](preview.jpg)

## The set

| Reel | Length | Sources |
|---|---|---|
| `ai-in-the-lab-reel-01-andrew-marcus` | 0:51 | [`VwOiijuXEP8`](https://youtu.be/VwOiijuXEP8), [`ndbG_nHQljc`](https://youtu.be/ndbG_nHQljc) — "Don't film me" · act-not-acted-upon · spatial reasoning · "AI is not our equal / No. It is our tool." · the mental check |
| `ai-in-the-lab-reel-02-gage-ronnie` | 0:50 | [`s5ptE--EVIk`](https://youtu.be/s5ptE--EVIk), [`bIONIUZDsMk`](https://youtu.be/bIONIUZDsMk) — learn-then-apply · explosive powders vs. aluminum alloys · pickleball · "have it critique your ideas" |
| `ai-in-the-lab-reel-03-ben-sterling` | 0:53 | [`I0jG2o6wthg`](https://youtu.be/I0jG2o6wthg), [`Ef0jl63-rLg`](https://youtu.be/Ef0jl63-rLg) — "I literally built the machine" · the next-cohort worry · "that didn't work, try again" · AI-first-draft idea · Xavier praise |
| `ai-in-the-lab-reel-04-xavier-sam` | 0:51 | [`rwoLhubyzZo`](https://youtu.be/rwoLhubyzZo) — BoTorch docs · Claude runs the powder doser · "I couldn't do it right now… that's scary" · the human element |
| `ai-in-the-lab-reel-05-audrey-carl` | 0:48 | meeting recording (their breakout happened inside the call) — grunt work & months of CAD · "it doesn't live in the 3D world with us" · overusing/under-using |
| `ai-in-the-lab-reel-06-group-discussion` | 1:27 | meeting recording — Carl's thesis · the e-bike problem & rebuttal · Jarvis, not autopilot · "YouTube famous" · "we could make a reel of us" · the close |
| `ai-in-the-lab-reel-07-everything` | 4:33 | everything above — the whole meeting end to end: cold open, the three questions, `@claude` runs a sensor test, e-bike, Jarvis, one bite per pair, what-do-we-do, the close (chapters sidecar included) |

Each breakout-session reel is **under 60 seconds** (Shorts-eligible). The group reel is
1:27; the everything reel runs 4:33 — past the 3-minute Shorts cap, which is a deliberate
trade (see *v2* below) and fine for Reels/TikTok and for a regular vertical YouTube upload.

## v4 (2026-08-29) — implementing the evidence review

[`../best-practices/`](../best-practices/) paired an Edison literature review with a
measured audit of these renders. This pass acts on the audit. **No quote, no cut boundary
and no word list changed** — the edit is the same edit; what changed is how it is
delivered.

### The reel opens on the quote (finding 2)

Every reel used to start with 2.4–3.0 s of silent branded title card — about 10 % of a
47-second reel, spent on branding, in exactly the window where a viewer decides whether to
stay. The card is gone as a *piece*: its kicker and title now fade in over the first bite,
top-left, and clear after 3.3 s. Frame 1 has a voice and a quote on it. The end card is
untouched — it comes after the content, where a "where to watch more" card belongs.

`title_card` is still in the EDL with its text; `"dur": 0.0` and
`"opened_over_first_bite": true` are what tell the renderer not to make a piece of it.

### The text stays out of the platform UI (finding 5)

| | v3 | v4 |
|---|---|---|
| Text measure | x = 78 … 1002 | **x = 78 … 846** |
| Quote block top | y = 1158 | **y = 940** |
| Lowest text across the set | y ≈ 1724 (4 lines @ 118 px) | **y = 1426** |
| Visual zone | y 372–938 | y 326–838 |

The right-hand like/comment/share column starts around x = 860–900 on Reels and TikTok, and
the caption/handle strip starts around y = 1600 (Shorts), 1490 (Reels), 1440 (TikTok). v3's
long lines ran under the buttons and a four-line quote ran under the captions. The measure
is now 768 px and the block is bounded at y = 1440, which is the lowest of the three.

Keeping the type large inside a smaller box took two changes: on-screen phrases are shorter
(38/50 characters instead of 54/72), and the visual zone gave up 54 px of height. Measured
across the whole set the quote now renders at **86–118 px, median 102 px** — v3's *base*
was 118 px but its auto-fit routinely dropped below that on long phrases. [`qa_layout.py`](qa_layout.py)
recomputes all of this from the EDL and the real font metrics, with no rendering:

```
$ python3 qa_layout.py
quote type sizes used: [118, 110, 102, 94, 86]  (median 102 px)
lines per phrase: max 4 (cap 4), mean 3.06
widest line  x=834px   vs action column 860px  ->  OK (+26px)
lowest text  y=1426px  vs TikTok       1440px  ->  OK (+14px)
safe areas: PASS
```

Platform overlay extents are published industry figures rather than device measurements —
worth confirming on a phone, and the constants are one edit away at the top of
`make_reels.py` if they turn out to be wrong.

### Quotes over footage are static blocks (finding 7)

The redundancy principle (verbatim text + identical speech hurts comprehension, *d* = 0.86)
has boundary conditions that our text-on-black bites sit comfortably inside: no competing
visual, short chunks, synchronized to speech. The v3 items that put the screen share on
screen do **not** — there the viewer is reading the screen share, reading a growing quote,
and listening at once, which is the split-attention case.

So footage and screen-share items now show the phrase as a **finished block** that fades in
at the first word and holds, with shorter phrases (30/40 characters) to keep it to one or
two lines. Word-by-word reveal — the Frieren look — survives everywhere it is safe, which
is every text-on-black bite, still the majority of the set.

### The sidecars are real caption tracks (findings 3 and 4)

The `.vtt` files were a transcript dump wearing a caption extension. In v3, **93 of 177 cues
(53 %) started before the previous cue ended**, lines ran to 81 characters, and no cue said
who was talking. All three are fixed in the writer, not by hand:

- each cue's end is clamped to the next cue's start (minus 80 ms) — no overlaps, at all;
- a cue may lead its audio by up to 0.35 s and hold up to 1.6 s past its last word, which
  is display time bought out of silence rather than out of the next line;
- text wraps to **≤ 42 characters** over at most two lines, balanced;
- every cue carries `<v Speaker>`, from the same diarized labels the burned render uses.

The captions and the burned text come from one function (`item_phrases`), so the sidecar
cannot drift from what is on screen.

### The redaction is gone

v3 blacked out ~3 s of the Colab notebook where MQTT broker credentials are on screen.
sgbaird confirms those are deliberately publicized test credentials, so the black box and
its `screen redacted` label are removed and the EDL records why.

### What did not change, and why

**Finding 6 — "reel 03 never shows a person"** — is not implementable from the sources.
Five of the seven pair clips are ceiling, wall or floor for their entire runtime; the pairs
set their phones face-up, which is the same fact the "Don't film me" cold open records.
[`../pair-clip-framing.jpg`](../pair-clip-framing.jpg) samples four frames across each of
the seven clips and shows it. The set already uses every second of real framing that
exists: Xavier & Sam's clip, the Gage & Ronnie Short, the "Don't film me" opening, Audrey's
Teams camera, the room camera at the close, and the screen share added in v3. The review's
own mitigation for audio-only material — a still photo of the speaker — would need photos
nobody has consented to yet, so it waits on [`../CONSENT.md`](../CONSENT.md).

**Finding 10 — disfluency removal** — the review's split is "aggressive in the reels,
conservative in the long-form". That is already the split: the reels micro-cut fillers, the
long-form keeps whole passages. The one thing missing was disclosure, which
[`../CONSENT.md`](../CONSENT.md) now carries.

## v3 (2026-08-27) — the screen share is on screen

Review question: *"wasn't I doing screen sharing for some of this?"* Yes — for **59 of the
75 minutes**. Classifying every second of the original recording (mean luma of the main
region, cross-checked on frames) gives:

| Original timeline | What the recording shows |
|---|---|
| 0:00 – 5:37 | avatars / black, people joining |
| 5:37 – **16:12** | the room camera, full frame |
| **16:12 – 1:15:22** | Sterling's screen share — GitHub discussion [#178](https://github.com/vertical-cloud-lab/byu-vcl/discussions/178), the three questions in a 500 %-zoom editor, then his Teams window through the online breakout — with brief returns to camera at 20:21 and 33:32 |
| 1:15:22 – 1:15:34 | the room camera again, for the closing lines |

v1 and v2 played **every** meeting bite as text on black, so none of that was ever visible
(the long-form [highlights](../highlights/) cut, which uses full-frame footage, always had
it). v3 puts the recording back on screen where it carries information, cropped to the part
of the 1920×1080 desktop being talked about — `"visual": "footage"` plus a `"crop"`
(source coordinates; a per-segment list where the shot changes mid-bite):

| Reel · item | What now plays instead of a waveform |
|---|---|
| 05 · `grunt-work` | **Audrey on camera** on the shared Teams stage, name plate and all, for her whole bite |
| 06 · `thanks` | the **room camera** — the recording cuts back to it at 1:15:22 |
| 07 · `three-questions` | the **three questions themselves**, in the editor, as he reads them |
| 07 · `claude-run` | Tim's comment, then **PR #60 and the `@claude` comment** reporting the 42-minute autonomous sensor test — the evidence the bite is describing |
| 07 · `thanks` | the shared Teams window, then the room camera |

Everything else stays a text card **on purpose**: during the e-bike / Jarvis stretch the
screen is a *static, unrelated* GitHub comment, and Carl was camera-off (a 900 px "CR"
avatar), so footage there would mislead or bore rather than inform.

### One redaction

The Colab notebook opened at 18:37 of the recording has **live MQTT broker credentials**
in the code cell and in its parameter form. Those ~3 s fall inside the `claude-run` bite,
so the EDL carries a `redact` entry — a timed black box in source coordinates, applied
before the crop — and the rendered reel shows `screen redacted` there instead. The rest of
that bite (the discussion thread, the PR, Claude's run report) is public and untouched.
**The credentials are still in the original recording and in the unlisted YouTube upload**;
worth rotating regardless of what the reels show.

### Nothing else moved

No cut boundary, word list, caption or chapter changed in v3 — only which pixels fill the
visual zone. Verified: the three re-rendered reels are the same length as the released v2
files to the frame (47.57 s / 87.40 s / 272.97 s), their `.vtt` and `.chapters.txt`
sidecars are byte-identical, and the decoded meeting audio cross-correlates with v2 at
**1.000000** (pair-clip audio, which had to be recovered again, at 0.9958 — one extra AAC
generation). So the v2 junction QA still stands and was not repeated.

## v2 (2026-08-26) — what changed and why

Review feedback on the first set was: the audio is noisy, the on-screen text keeps
re-wrapping, the role captions are more than is needed, the type could be bigger, black
would suit it better than navy, the corner timestamps are noise — and reel 07 was "better
but still fairly choppy and not very informative."

| Change | How |
|---|---|
| **Background-noise reduction** | The continuous source is denoised *before* the micro-cuts (so nothing re-adapts at a splice): 85 Hz high-pass → RNNoise (`arnndn`, `sh.rnnn`) → `afftdn` → 3 kHz presence bell → 12 kHz low-pass → gentle 2.5:1 compression. Measured on this recording: between-word level **−29.7 → −40.9 dBFS** in the room and **−25.6 → −40.5 dBFS** on the Teams side, with ASR word counts and confidence unchanged on normal speech (checked over three spans) |
| **No more reflowing line breaks** | Each phrase is wrapped **once**, up front, with PIL-measured advance widths; the reveal then emits those exact `\N` breaks with libass `WrapStyle: 2` (auto-wrap disabled) and left/top alignment. A word lands in its final position the moment it appears and never moves |
| **Bigger type** | Base 118 px (was 76), auto-fitting down through 110/102/94/86/79/72/66 until the phrase fits four lines in the 924 px measure. The size is chosen **per bite**, not per phrase, so the quote never resizes mid-thought |
| **Speaker labels** | A single grayed-out `Sterling Baird:` above the quote, replacing `STERLING · ON THE SCREEN SHARE`. For meeting items the label **follows the speaker within a bite**, derived from [`../whisper-diarized-transcript.json`](../whisper-diarized-transcript.json) (turns shorter than 1.3 s are absorbed so the name never flickers) |
| **Black canvas** | Pure black everywhere, replacing BYU navy |
| **No corner chrome** | The top-right source/timecode bug is gone |
| **Reel 07: less choppy** | The six hard-cut interstitial part cards are gone — a part title now fades in over the bite itself. That removes six full-frame interruptions and 9 s of dead cards |
| **Reel 07: more informative** | Every bite was re-authored to run to the **end of the thought** instead of stopping at a soundbite (Carl's thesis whole rather than its two ends; `@claude` demo with the "it can run 24-7" premise; the rebuttal carrying the question it sets up; the Jarvis analogy *plus* the learn-the-math-first argument it supports; Audrey's onboarding proposal with her examples). 14 bites, **2:45 → 4:33** |
| **Dead-air removal** | Inside every authored span, any inter-word silence longer than 1.2 s is cut back to 0.30 s either side — tightening pacing without ever cutting into a word (this alone took reel 07 from 5:03 to 4:33) |

Boundaries in reel 07 are authored as **phrase anchors** ("first words" → "last words")
resolved against faster-whisper word onsets, not hand-typed timestamps, so every cut sits
0.34 s before its opening word and 0.40 s after its closing word by construction, and can
never land inside a neighbouring word.

## Where the videos live

Video files are deliberately **not** committed to git (see [`../README.md`](../README.md)).

- **Draft GitHub release** [`meeting-2026-08-19-recording`](https://github.com/vertical-cloud-lab/byu-vcl/releases):
  all seven MP4s + caption sidecars.
- **Stream-cam Pi**: `~/vcl-meeting-recordings/2026-08-19/reels/` — *not refreshed for v2
  or v3*; neither runner had tailnet (see below). The release copies are current.

## Files here

| File | Description |
|---|---|
| [`reels-edl.json`](reels-edl.json) | The whole edit: per item, the audio keep-intervals (source seconds, fillers/false-starts/dead-air already cut), the kept words with their source-time onsets (drives the on-screen text), `speaker`/`speaker_spans`, card copy, and a `why` per item |
| [`make_reels.py`](make_reels.py) | Renders everything with ffmpeg + libass from the EDL: source-level denoise, micro-cut concat with 15 ms anti-click fades, per-item two-pass loudnorm (−14 LUFS), black frames with live waveform, pre-wrapped word-by-word ASS reveal, frame-exact joins |
| `*.vtt` | Sidecar captions per reel (phrase-level, output timeline) — the text is also burned in |
| `ai-in-the-lab-reel-07-everything.chapters.txt` | Chapter markers for the everything reel |
| [`asr_dump.py`](asr_dump.py) | Word-level ASR over padded windows of any source — regenerates the word-onset dumps the EDL was cut from |
| [`qa_reels.py`](qa_reels.py) | Junction QA: re-transcribes each rendered reel and checks every item's first/last words survive at the planned offsets, plus loudness and A/V duration parity |
| [`preview.jpg`](preview.jpg) | Contact sheet: one frame per segment of every reel |

## Re-rendering

Needs `ffmpeg` 6.x with libass, the Inter font family (`apt install fonts-inter`), and
`pip install faster-whisper pillow`. The RNNoise model is fetched once to
`/tmp/rnnoise-sh.rnnn`; without it the renderer falls back to FFT-only denoise and says so.

```bash
curl -Lo /tmp/rnnoise-sh.rnnn \
  https://raw.githubusercontent.com/GregorR/rnnoise-models/master/somnolent-hogwash-2018-09-01/sh.rnnn
# meeting recording (SharePoint share link in ../README.md)
yt-dlp -f source -o meeting.mp4 "<share link>"
# breakout clips: on the Pi under ~/vcl-ai-clips/media/ (YouTube blocks datacenter IPs)
python3 make_reels.py --source meeting.mp4 --clips-dir clips --workdir /tmp/reels-build
python3 qa_reels.py --dir /tmp/reels-build
```

To change a cut: edit the item's `segments`/`words` in `reels-edl.json` and re-run with
`--only <reel-id>`. Word-onset dumps for new spans: `python3 asr_dump.py spans.json out.json`.

### Rendering without the original pair clips

This runner had **no tailnet** (`tailscale` was not installed and no OAuth credentials were
present) and YouTube bot-gates the runner's datacenter IP on every player client, so the
seven pair clips were unreachable for v2 — and again for v3, which recovered reel 07's four
pair items from the **v2** release render the same way (timeline reproduced from the EDL to
0.000 frames against the released duration; `"denoise": "none"` in the manifest so the
already-denoised audio is not run through the chain twice). Instead, each pair item's media was recovered
**frame-exactly from the v1 renders** on the draft release, by replaying the v1 renderer's
offset arithmetic (validated: reconstructed reel durations matched the released files to
0.000 s, and predicted card boundaries matched `silencedetect` to ≤1 frame); item audio was
spot-checked against the EDL word lists by re-transcription. Footage items were recovered by
cropping the clean band of the v1 frame (the strip inset at y 430–1038, below the v1 header
and above the v1 burned quote). `make_reels.py --recovered <manifest.json>` takes such
pre-cut media, where the manifest maps `"<reel-id>__<item-id>"` to `{audio, video, dur}`.

**Consequence:** pair-clip audio in v2 carries one extra AAC generation and the v1 loudnorm,
and pair-clip footage one extra H.264 generation. Re-running with the Pi attached (or the
clips re-downloaded) will render those items from the originals with no change to the EDL.

## How this set measures up against the literature

[`../best-practices/`](../best-practices/) holds an evidence review of these formats and a
measured audit of these renders against it. In short: no background music, chapters on the
long cuts, speaker labels, a cut rate of 0.12–0.24 cuts/s (comfortably inside the studied
band), and text-on-black for audio-only bites all land on the right side of the evidence.
The findings worth acting on — the silent title card ahead of every hook, 53 % of sidecar
caption cues overlapping their predecessor, caption lines up to 81 characters, and a quote
block reaching into the platform UI zones — were implemented in **v4**, above.

## Known limitations

- The two voices within a pair are not name-distinguished (the label carries the pair);
  meeting-side attribution follows the ECAPA diarization, which cannot separate
  Andrew/Ronnie/Marcus on the shared room mic and labels them **In the room:**.
- RNNoise swallows Andrew's near-whispered "Don't film me" laugh-line, so that one item
  carries `"denoise": "gentle"` (FFT-only) in the EDL; verified restored by re-transcribing
  the rendered output. If another quiet aside sounds thin, the same one-key override fixes it.
- Some drawn-out fillers glued to the next word (e.g. a long "um" with no gap) were kept or
  only partially trimmed to avoid audible artifacts.
- Display text carries a few ASR patches ("clot" → "Claude", "Bow Torch" → "BoTorch"), all
  recorded in the EDL so display text stays auditable against the raw audio.
- Reel 07 at 4:33 is past the 3-minute YouTube Shorts cap. The five pair reels remain
  Shorts-eligible; a shorter everything-cut is a matter of dropping items from the EDL.
