# AI-in-the-lab highlights compilation (2026-08-19 meeting)

A 6:10 edited highlights video cut from the full 75:34 meeting recording — high-density
but breathable: 14 segments across six titled parts, with burned-in captions, source
timecode bugs, loudness-normalized audio (−16 LUFS), and title/end cards.

![Contact sheet: one frame per segment](preview.jpg)

## Where the video lives

Video files are deliberately **not** committed to git (see [`../README.md`](../README.md)).

- **Draft GitHub release** [`meeting-2026-08-19-recording`](https://github.com/vertical-cloud-lab/byu-vcl/releases):
  `ai-in-the-lab-highlights-20260819.mp4` (20.5 MB, 1920×1080@16fps) plus the sidecar
  captions and chapters.
- **Raspberry Pi** (stream-cam Pi): `~/vcl-meeting-recordings/2026-08-19/highlights/`.

## What's in the cut

Output chapters ([`highlights-chapters.txt`](highlights-chapters.txt), YouTube-description format):

```
0:00 Cold open: anyone can use AI (Carl)
0:25 The three questions
0:53 Exhibit A: @claude runs a sensor test
1:12 The e-bike problem
2:53 Jarvis, not autopilot
4:17 Meanwhile, online: Audrey & Carl
5:10 So what do we do?
6:05 Where to watch more
```

Segment sources (original 75:34 timeline — the on-screen timecode bug at the start of
each segment shows the same value):

| Output | Source | Segment |
|---|---|---|
| 0:00 | 45:06 | Cold open — Carl: "if that's all you use, you're useless, because anyone can use AI" |
| 0:28 | 16:43 | Sterling reads the three discussion questions (screen share) |
| 0:56 | 18:27 | Tim's `@claude` comment: pick up the enclosure, run the Colab sensor test, post results |
| 1:15 | 26:31 | The e-bike analogy: complacency vs. competency, e-bikes vs. mountain biking |
| 2:06 | 29:31 | The rebuttal: "it's not like we can choose to not buy the e-bike … I bought it for everybody" |
| 2:56 | 30:33 | Tony Stark: "Jarvis is a support to Tony Stark, not doing Tony Stark's work" |
| 3:31 | 31:50 | Writing the paper yourself vs. backtracking through AI output; "where does the balance sit" |
| 4:20 | 49:06 | Audrey: what is *actually* grunt work — months of generative CAD vs. "plenty of us enjoy CAD" |
| 4:51 | 50:03 | "It doesn't live in the 3D world with us" / "It's not there yet" |
| 4:56 | 56:55 | Carl: "I'm probably overusing it" / Audrey: "and probably under-using it, so we just need to…" |
| 5:13 | 1:02:16 | "We are about to get YouTube famous" (where the channel clips came from) |
| 5:25 | 1:04:57 | Audrey's action item: teach good AI patterns during onboarding |
| 5:45 | 1:05:47 | "We could make a reel of us — this is good, this is bad" (this video is that artifact) |
| 6:00 | 1:15:26 | "Thanks, Audrey, Carl. Thanks, everybody." |

## Files

| File | Description |
|---|---|
| [`edl.json`](edl.json) | Edit decision list: every cut boundary (source seconds), card copy, caption overrides, and a `why` per segment |
| [`make_highlights.py`](make_highlights.py) | Renders the whole thing with ffmpeg from the EDL + the Teams transcript |
| [`ai-in-the-lab-highlights-20260819.vtt`](ai-in-the-lab-highlights-20260819.vtt) | Sidecar captions on the compilation timeline (captions are also burned in) |
| [`highlights-chapters.txt`](highlights-chapters.txt) | Chapter markers on the compilation timeline |
| [`preview.jpg`](preview.jpg) | 4×4 contact sheet, one frame per segment/card |

## Reproducing

```bash
yt-dlp -f source -o original.mp4 "<SharePoint share link in ../README.md>"
python3 make_highlights.py --source original.mp4 --workdir /tmp/build
```

Needs `ffmpeg` (6.x) and the DejaVu fonts. Cut boundaries come from the Teams transcript
cue times (±0.25–0.45 s padding), snapped to the 16 fps frame grid; each segment is cut
with input-seek re-encode (frame-accurate), gets two-pass `loudnorm` (−16 LUFS), burned
captions from `../transcript.vtt` (speakers tagged via `../transcript.json`; in breakout
segments, room-mic crosstalk cues are dropped and Carl/Audrey get name prefixes), and the
segments are joined with the concat *filter* while padding/trimming each segment's audio
to exactly its video duration — a stream-copy concat of independently encoded MP4s
accumulates AAC frame padding into ~240 ms of audible A/V drift by mid-video.

## Known limitations

- Parts 03–04 (e-bike / Jarvis, ~2:00–4:15) sit on the static GitHub-discussion screen
  share, because that is what the recording shows while the room talks; the room is only
  visible in the small webcam sidebar.
- Cut boundaries were placed from transcript cue timings and QA'd on frames and loudness
  stats, not by ear — if a word clips at a junction, the fix is a one-line nudge in
  `edl.json`.
- Room-mic speech (`@3`) is captioned without speaker names; remote speakers are named.
  A diarized transcript (in progress on this PR) could improve the in-room attributions.
