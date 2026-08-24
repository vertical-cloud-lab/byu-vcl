# AI-in-the-lab highlights compilation (2026-08-19 meeting)

A 9:57 edited highlights video cut from the full 75:34 meeting recording **and the seven
break-off pair-discussion clips** from the channel — high-density but breathable: 23
segments across seven titled parts, with burned-in captions, source bugs (meeting
timecode or youtu.be link), loudness-normalized audio (−16 LUFS), and title/end cards.
Cut boundaries are word-aligned to faster-whisper word onsets (re-cut 2026-08-24 after
the first version, placed from Teams cue times, clipped the start of most segments'
opening sentence; the breakout bites were word-aligned from the start).

![Contact sheet: one frame per segment](preview.jpg)

## Where the video lives

Video files are deliberately **not** committed to git (see [`../README.md`](../README.md)).

- **Draft GitHub release** [`meeting-2026-08-19-recording`](https://github.com/vertical-cloud-lab/byu-vcl/releases):
  `ai-in-the-lab-highlights-20260819.mp4` (85 MB, 1920×1080@16fps) plus the sidecar
  captions and chapters.
- **Raspberry Pi** (stream-cam Pi): `~/vcl-meeting-recordings/2026-08-19/highlights/`;
  the seven downloaded breakout clips also live there under `~/vcl-ai-clips/`.

## What's in the cut

Output chapters ([`highlights-chapters.txt`](highlights-chapters.txt), YouTube-description format):

```
0:00 Cold open: anyone can use AI (Carl)
0:27 AI in the lab
0:31 The three questions
1:01 Exhibit A: @claude runs a sensor test
1:23 The e-bike problem
3:05 Jarvis, not autopilot
4:33 The breakouts: four more pairs
7:49 Meanwhile, online: Audrey & Carl
8:53 So what do we do?
9:51 Where to watch more
```

Segment sources — meeting segments cite the original 75:34 timeline (the on-screen
timecode bug at the start of each segment shows the same value); breakout segments cite
their clip (the bug shows the youtu.be link):

| Output | Source | Segment |
|---|---|---|
| 0:00 | 45:01 | Cold open — Carl: "the biggest thing is just recognizing that we're going to have AI forever" → "if that's all you use, you're useless, because anyone can use AI" |
| 0:33 | 16:41 | Sterling reads the three discussion questions (screen share) |
| 1:04 | 18:25 | Tim's `@claude` comment: pick up the enclosure, run the Colab sensor test, post results |
| 1:25 | 26:29 | The e-bike analogy: complacency vs. competency, e-bikes vs. mountain biking |
| 2:16 | 29:29 | The rebuttal: "it's not like we can choose to not buy the e-bike … I bought it for everybody" |
| 3:08 | 30:31 | Tony Stark: "Jarvis is a support to Tony Stark, not doing Tony Stark's work" |
| 3:44 | 31:44 | Writing the paper yourself vs. backtracking through AI output; "where does the balance sit" |
| 4:36 | [`VwOiijuXEP8`](https://youtu.be/VwOiijuXEP8) | Breakouts open — Andrew & Marcus: "Lab culture. Death and destruction." … "Don't film me" (after which their phone lies face-up: hence the audio-cards below) |
| 4:47 | [`VwOiijuXEP8`](https://youtu.be/VwOiijuXEP8) | Andrew & Marcus (audio): "things that act and not to be acted upon — if we start using AI too much, AI starts using us" |
| 5:07 | [`ndbG_nHQljc`](https://youtu.be/ndbG_nHQljc) | Andrew & Marcus (audio): "it's funny how bad AI's spatial reasoning is — no concept of 3D space at all" |
| 5:17 | [`s5ptE--EVIk`](https://youtu.be/s5ptE--EVIk) | Gage & Ronnie (on camera): what AI taught them about explosive elemental powders and safer aluminum alloys |
| 5:41 | [`bIONIUZDsMk`](https://youtu.be/bIONIUZDsMk) | Gage & Ronnie (audio): "have it critique your ideas … that'll help you think as well while you're using AI" |
| 6:04 | [`I0jG2o6wthg`](https://youtu.be/I0jG2o6wthg) | Ben & Sterling (audio): "I started from the ground up … people coming in when things have been built never got the chance to learn any of this" |
| 6:35 | [`rwoLhubyzZo`](https://youtu.be/rwoLhubyzZo) | Xavier & Sam (on camera): Claude runs the powder doser end to end — "if you asked me to do it myself, I couldn't do it right now … that's scary" |
| 7:03 | [`Ef0jl63-rLg`](https://youtu.be/Ef0jl63-rLg) | Ben & Sterling (audio): "I could tell that Xavier really understood — he wasn't just using AI to do the learning" |
| 7:24 | [`rwoLhubyzZo`](https://youtu.be/rwoLhubyzZo) | Xavier & Sam (on camera): "if Claude is doing research, then anybody can push the button — my research should have aspects of me in it" |
| 7:51 | 49:04 | Audrey: what is *actually* grunt work — months of generative CAD vs. "plenty of us enjoy CAD" |
| 8:24 | 49:57 | Carl: "it's not there yet" / Audrey: "it doesn't live in the 3D world with us. It's all just code and stuff" |
| 8:35 | 56:51 | Carl: "I'm probably overusing it" / Audrey: "and probably under-using it, so we just need to…" |
| 8:55 | 1:02:15 | "We are about to get YouTube famous" (where the channel clips came from) |
| 9:08 | 1:04:55 | Audrey's action item: teach good AI patterns during onboarding |
| 9:28 | 1:05:45 | "We could make a reel of us — this is good, this is bad" (this video is that artifact) |
| 9:45 | 1:15:22 | "Okay, we'll probably call it good there. Thanks, Audrey, Carl. Thanks, everybody." |

## Files

| File | Description |
|---|---|
| [`edl.json`](edl.json) | Edit decision list: every cut boundary (source seconds), card copy, caption overrides, breakout source registry, and a `why` per segment |
| [`make_highlights.py`](make_highlights.py) | Renders the whole thing with ffmpeg from the EDL + the Teams transcript + the per-clip whisper captions |
| [`sources/*.vtt`](sources/) | faster-whisper (`distil-large-v3`) captions for each breakout clip, on that clip's own timeline — used for the burned breakout captions |
| [`ai-in-the-lab-highlights-20260819.vtt`](ai-in-the-lab-highlights-20260819.vtt) | Sidecar captions on the compilation timeline (captions are also burned in) |
| [`highlights-chapters.txt`](highlights-chapters.txt) | Chapter markers on the compilation timeline |
| [`preview.jpg`](preview.jpg) | 5×5 contact sheet: one frame per segment plus the title and end cards |

## Reproducing

```bash
# meeting recording (SharePoint share link in ../README.md)
yt-dlp -f source -o original.mp4 "<share link>"
# breakout clips (YouTube blocks datacenter IPs -- run on a residential
# connection, e.g. the stream-cam Pi, where they are already downloaded
# under ~/vcl-ai-clips/media/ as separate video+audio streams)
for id in VwOiijuXEP8 ndbG_nHQljc bIONIUZDsMk s5ptE--EVIk Ef0jl63-rLg I0jG2o6wthg rwoLhubyzZo; do
  yt-dlp -f "bv[height<=1440][vcodec^=avc1]/bv[height<=1440]" -o "$id.video.%(ext)s" "https://www.youtube.com/watch?v=$id"
  yt-dlp -f "ba[ext=m4a]/ba" -o "$id.audio.%(ext)s" "https://www.youtube.com/watch?v=$id"
  ffmpeg -i "$id".video.* -i "$id".audio.* -c copy clips/"$id".mp4
done
python3 make_highlights.py --source original.mp4 --clips-dir clips --workdir /tmp/build
```

Needs `ffmpeg` (6.x) and the DejaVu fonts. Cut boundaries in `edl.json` are word-aligned:
each piece opens ≥0.3–0.5 s before its first word's faster-whisper onset and closes ≥0.3 s
after its last word ends, with cuts placed inside real speech gaps and snapped to the
16 fps frame grid. (The first cut used the Teams cue times ±0.25–0.45 s instead — those
timestamps lag the audio by ~0.5–1.2 s, which clipped the start of most opening
sentences.) Each segment is cut with input-seek re-encode (frame-accurate), gets two-pass
`loudnorm` (−16 LUFS), and burned captions — meeting segments from `../transcript.vtt`
(speakers tagged via `../transcript.json`; in online-breakout segments, room-mic
crosstalk cues are dropped and Carl/Audrey get name prefixes), breakout segments from
`sources/<id>.vtt`. Breakout footage is normalized to the 1920×1080 canvas (portrait
phone video pillarboxed on the card navy). The segments are joined with the concat
*filter* while padding/trimming each segment's audio to exactly its video duration — a
stream-copy concat of independently encoded MP4s accumulates AAC frame padding into
~240 ms of audible A/V drift by mid-video.

**Audio-cards.** Five of the eight breakout bites render as navy cards (pair names,
topic, live waveform, captions) instead of footage: those pairs set their phone
face-up while recording — VwOiijuXEP8 says "Don't film me" out loud at 0:11, and
VwOiijuXEP8 (after 0:14), ndbG_nHQljc, bIONIUZDsMk, I0jG2o6wthg, and Ef0jl63-rLg show
only the ceiling for essentially their whole runtime. The cards present that honestly
rather than airing 25-second ceiling shots; the two clips with real framing
(rwoLhubyzZo, s5ptE--EVIk) appear as footage.

## Known limitations

- Parts 03–04 (e-bike / Jarvis, ~2:00–4:30) sit on the static GitHub-discussion screen
  share, because that is what the recording shows while the room talks; the room is only
  visible in the small webcam sidebar.
- Every junction (including all breakout bites) was QA'd by re-transcribing each rendered
  segment and checking the expected opening/closing words survive intact. If a boundary
  still sounds off, the fix remains a one-line nudge in `edl.json` (meeting word onsets
  are in `../whisper-diarized-transcript.json`; breakout word onsets can be regenerated
  with faster-whisper, or read from the cue times in `sources/<id>.vtt`).
- Within the breakout bites the two voices of a pair are not name-distinguished in the
  captions (the section labels/cards identify the pair); Whisper occasionally mishears a
  word in the noisy phone recordings — the obvious cases are patched via
  `caption_text_fixes` in the EDL.
- The Gage & Ronnie Short (`s5ptE--EVIk`) frames its speaker at the edge of a propped
  phone shot; kept anyway because it is one of only two breakout clips with real footage.
- Room-mic speech (`@3`) in meeting segments is captioned without speaker names; remote
  speakers are named. The diarized transcript in `../` could improve in-room attributions.
