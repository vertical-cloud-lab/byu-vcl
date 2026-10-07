# Atomizer installation and training: videos, SOP, and compilations

Our own documentation of the AMAZEMET rePowder ultrasonic atomizer, synthesized from the 26 atomizer-related videos on
the BYU VCL YouTube channel: the installation clips (Sep 2026), the two training days with Bartosz Kalicki of AMAZEMET
(Sep 29–30 2026), the custom-charge and dosing sessions, and the team's first unsupervised run (Oct 2 2026). Issue #124,
with the training detail from #222 and the powder bags from #249.

| What | Where |
| --- | --- |
| **The procedure**: before / during / after a run, safety, utilities, cleaning, troubleshooting, known runs, open questions, with every step linked to the moment of video it comes from | [`sop.md`](sop.md) |
| **Daily run SOP** (Gage Erickson, Oct 6): who does what on a run day, Gage, Ronnie and Paul, copied from #126 | [`daily-sop.md`](daily-sop.md) |
| **Runs, checked against the footage**: Oct 6, Gage's three videos placed on the clock of the pixelated room stream, then the daily SOP and the #261 parameters checked step by step; what to check or replace after it, and what to expect in its powder (`4yghtr`) | [`runs/2026-10-06.md`](runs/2026-10-06.md) |
| **Timestamp log**: every substantive moment in every video, one row each, links open the player **paused** at that second (no autoplay) | [`timestamps.md`](timestamps.md) |
| Per-video indexes: summary, timestamp table, procedural steps, parameters, quotes, open questions (what the SOP was built from) | [`notes/`](notes/) |
| Transcripts: YouTube auto-captions for 20 videos, Whisper large-v3-turbo transcripts for all 26, and for Gage's three Oct 6 videos (word-timed for all nine training videos and every longer video), and word-level re-runs of the clips where the two still disagreed | [`transcripts/`](transcripts/) |
| **Start-to-finish stitch**: every logged moment of all 26 videos in the order of a run, one raw cut in two parts, with the clip list and chapter times | [`stitch/`](stitch/README.md) |
| Keyframes: a contact sheet per video, and one frame for every moment the SOP cites | [`keyframes/`](keyframes/README.md), [`keyframes/sop-frames.md`](keyframes/sop-frames.md) |
| **3D step animations**: a CadQuery model of the machine, rendered with PyVista into one GIF per step of the run (the assembly-GIF style of #239 and #234), plus a labelled overview and a cutaway. Every animation is checked frame by frame so that no part passes through another ([`viz3d/out/collisions.md`](viz3d/out/collisions.md)) | [`viz3d/`](viz3d/README.md) |
| **Narrated tutorials**: four videos built from the 3D animations, draw.io outlines and the trainer's own explanations; scripts, diagrams, build pipeline, upload log; [`real-footage.md`](tutorials/real-footage.md), the cut list of real action footage for draft 5 | [`tutorials/`](tutorials/README.md) |
| **Slide clips** for PowerPoint, 1080p MP4s with at most 6 words on screen at a time, each caption up at least 4 s, and one short narrated line per caption. The whole run in 44 s, condensed with the fasteners sped up, including the coil stirring the melt: [summary](https://www.youtube.com/watch?v=j9QcpcG8EVI). Furnace loading, the ultrasonic stack and the pour, at the animations' own speed. All ten step animations as 1080p30 MP4s too, with the GIFs' text and without | [`ppt/`](ppt/README.md) |
| **The playlists**: every atomizer video on the channel in one unlisted playlist, tutorials first, then the recordings in the order they were made; each renamed, with a summary, chapters and links back here. *Atomizer Runs*, named by the daily SOP, holds the team's own runs | [playlist](https://www.youtube.com/playlist?list=PLB8wxmcPAjLM), [Atomizer Runs](https://www.youtube.com/playlist?list=PLZQwIo89me4c), [`playlist/`](playlist/README.md) |
| Inventory of the videos (id, title as on YouTube, original title, date, duration, privacy) | [`videos.json`](videos.json) |
| The scripts that made all of this | [`tools/`](tools/) |

## How it was made

1. **Inventory** ([`tools/list_channel.py`](tools/list_channel.py)): the channel's uploads playlist through the YouTube Data API with
   the repo's upload/read token, filtered to the atomizer titles ([`tools/video_ids.txt`](tools/video_ids.txt)).
2. **Download** ([`tools/dl.sh`](tools/dl.sh)): YouTube refuses the player to a GitHub Actions runner ("sign in to confirm you're not a
   bot", as `CLAUDE.md` records), so the Pi 5 stream cam fetched the auto-captions, the audio (m4a) and a 360p video copy with
   `yt-dlp` at ≤3 MB/s, and the runner pulled them over Tailscale with `rsync --bwlimit`. 1.7 GB, nothing left on the Pi except
   `~/atomizer-dl/`, which can be deleted. For the tutorial clips and the measurement frames,
   [`tools/hls_sections.py`](tools/hls_sections.py) fetches only the HLS segments of the windows needed, at the best
   resolution YouTube has (720p for these videos, 1080p for some phone clips), into `~/atomizer-hls/` on the Pi.
3. **Transcription** ([`tools/transcribe.py`](tools/transcribe.py)): `faster-whisper` **large-v3-turbo**, int8, batched with VAD, which is the
   largest Whisper model this 4-core, no-GPU runner handles at a useful speed (about 4× realtime when it has the machine to
   itself, 2× or less when sharing it with renders). Every run now uses word timestamps: segments are re-cut at sentence ends
   (or every ~12 s of speech) and the JSON keeps each word as `[start, end, word, probability]`. All nine training videos and every other video longer than a few minutes have word-timed transcripts in [`transcripts/whisper/`](transcripts/whisper/) (the two machine-noise videos were run without the voice filter); the remaining short clips (the installation and dosing clips, the lathe and vacuum-test clips) keep the first pass's segments until `python tools/transcribe.py` (no arguments) re-runs them. YouTube's auto-captions ([`tools/vtt2txt.py`](tools/vtt2txt.py)) are kept next to them for the 20 videos that have them. Clips where the captions
   and the batched transcript still disagreed on a number, name or label were re-decoded word by word with
   [`tools/recheck_clips.py`](tools/recheck_clips.py) ([`recheck-clips.json`](transcripts/whisper/recheck-clips.json)), which also records the speech check of the
   silent videos.
4. **Indexing**: four reading agents turned the caption text into the per-video tables in [`notes/`](notes/), keeping the
   caption start time of every row so that each becomes a link. Every captioned video was then re-checked line by line
   against its Whisper transcript, with each correction marked in the row ("Whisper: …") and listed in the section's
   *Unclear* list; the six uncaptioned videos were indexed from Whisper, or from frames of the footage where there is no speech.
   [`tools/make_timestamps.py`](tools/make_timestamps.py) assembles [`timestamps.md`](timestamps.md) from those tables and labels each
   video's source.
5. **Keyframes** ([`tools/keyframes.py`](tools/keyframes.py), [`tools/sop_frames.py`](tools/sop_frames.py)): scene-change detection plus a frame
   every two minutes for the contact sheets; a frame at the exact cited second for every SOP reference. Every tile carries the
   true time of its frame: a scene change keeps ffmpeg's own timestamp, and the every-two-minute frames are taken with an
   accurate seek at exactly 00:00, 02:00, 04:00, …
6. **SOP**: drafted from the indexes with a fixed outline and the link convention, then reviewed. Where the captions disagree or
   are garbled, the SOP says so and lists the item under *Open questions*; the videos stay the authority.
7. **3D animations** ([`viz3d/`](viz3d/README.md)): a CadQuery model of the module (furnace, crucible stack, chamber, ultrasonic
   stack, cone and container, frame and utilities), measured from 720p frames and AMAZEMET's renders and scaled to the documented
   envelope, rendered off-screen
   with PyVista into one animation per step. Each animation's sub-steps are written to a JSON file so the narration can follow
   them. Draft 1's matplotlib schematics and stick-figure operator were dropped after review. Since draft 4,
   [`viz3d/collide.py`](viz3d/collide.py) replays every animation without rendering and fails any pair of parts that
   pass through each other. Fixing what it found also put the steps in the order of a real run: the furnace, the
   chamber, and the stack into the door last.
8. **Tutorials** ([`tutorials/`](tutorials/README.md)). Each tutorial runs: a draw.io outline of its steps that builds up with the
   narration (step boxes first, then each step's details as it is named), then for each step:
   - the outline with that step highlighted;
   - its 3D animation, narrated sentence by sentence by Microsoft Edge TTS `en-US-AndrewMultilingualNeural` at 1×;
   - the trainer's own explanation, cut from the training videos.

   Clips are cut from the 720p sources on sentence boundaries found by word-timed Whisper, stabilised with `vidstab` (zooming
   up to 10 % instead of showing borders) and subtitled. Segments are crossfaded, rendered at 720p, and uploaded unlisted with
   [`../youtube/yt_service.py`](../youtube/yt_service.py).

## Link convention

`https://www.youtube.com/embed/<id>?start=<seconds>` opens YouTube's embed player at that second **without autoplay**
(embeds only autoplay with `autoplay=1`); `https://www.youtube.com/watch?v=<id>&t=<seconds>s` is the same moment on the
normal watch page, which does autoplay. Unlisted videos open with either. Times are caption start times (Whisper segment
starts for the uncaptioned videos), so a link lands a second or two before the words.

## Status and follow-ups

- The transcription queue is finished: Whisper transcripts exist for all 26 videos, and all 20 captioned indexes have been
  re-checked against them (Oct 3). 799 rows across all 26 videos in [`timestamps.md`](timestamps.md): 20 videos indexed from
  auto-captions and re-checked, 3 from Whisper alone, 3 from keyframes.
- Values the re-check changed, each also corrected in [`sop.md`](sop.md): the Oct 2 pour pressure was said as ".17 bar"
  (0.17 bar, as #249 records; the captions heard "17.17") and the Oct 2 plate was "pure molybdenum" (captions: "pure
  aluminum"); the coolant flow at commissioning read about 3 L/min against the 2 L/min needed (captions: "10"); Video 4's
  "sealing block" is the sealing rod being lowered before loading; earlier passes settled the ~1000 °C Video 2 setpoint and
  the spoken N·m torque unit. The per-video *Unclear* lists in [`notes/`](notes/) record every
  correction and the lines that remain disputed.
- No usable speech in three videos. *The expert cleaning the atomizer, pov* and *Dosing Al 4047 powder*, re-run without the
  voice filter, give only hallucinated filler ("So, let's go.", "Thank you.", "We'll be right back.") at the edges of
  Whisper's 30 s windows, and a sensitive VAD pass finds 1 s and 0 s of speech in them; the *nzyjn0 AlSi10Mg-Al6063 dosing
  session* has a few words in its first 19 s and nothing after. All three are indexed from frames of the footage only, so
  their steps have to be read from the footage.
- Word-timed Whisper re-run: done for all nine training videos (Videos 9, 3, 7 and 2 on Oct 3, session 4: 3.5 h of audio in 54 min, sharing the runner with the stitch build) and for every other video longer than a few minutes. Seven short clips (the two installation clips, the vacuum test, the dehumidifier clip, the lathe clip, and the two *Claude ping* dosing videos) still carry the first pass's coarse segments; `python tools/transcribe.py` with no arguments picks exactly those up. The training videos' index rows keep caption times, which are within a second or two of the words.
- **Start-to-finish stitch** ([`stitch/`](stitch/README.md)): every logged moment of all 26 videos, reorganised into the order of a run and joined end to end (254 clips, 6.8 h, two unlisted uploads), with the clip list in [`stitch/edl.md`](stitch/edl.md).
- Open questions only someone at the machine can close: the `graining`/`draining` HMI label; whether the HMI's pour
  pressure is absolute or relative to the chamber (0.17 bar was "definitely too high" against a 150 mbar chamber); the
  Video 8 nozzle Gage machined, said as "0.05" (0.5 mm inferred); whether the Sep 30 plate was Mo or tungsten–nickel–iron;
  and the safety-valve rating and thermocouple type from Video 1 (0.8 bar and "M" per Whisper, "8 bar" and N per the captions).
