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
- **Stream-cam Pi**: `~/vcl-meeting-recordings/2026-08-19/reels/` — *not refreshed for v2*;
  this runner had no tailnet (see below).

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
seven pair clips were unreachable for v2. Instead, each pair item's media was recovered
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
