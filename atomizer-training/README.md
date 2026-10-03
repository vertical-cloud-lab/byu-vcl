# Atomizer installation and training: videos, SOP, and compilations

Our own documentation of the AMAZEMET rePowder ultrasonic atomizer, synthesized from the 26 atomizer-related videos on
the BYU VCL YouTube channel: the installation clips (Sep 2026), the two training days with Bartosz Kalicki of AMAZEMET
(Sep 29–30 2026), the custom-charge and dosing sessions, and the team's first unsupervised run (Oct 2 2026). Issue #124,
with the training detail from #222 and the powder bags from #249.

| What | Where |
| --- | --- |
| **The procedure**: before / during / after a run, safety, utilities, cleaning, troubleshooting, known runs, open questions, with every step linked to the moment of video it comes from | [`sop.md`](sop.md) |
| **Timestamp log**: every substantive moment in every video, one row each, links open the player **paused** at that second (no autoplay) | [`timestamps.md`](timestamps.md) |
| Per-video indexes: summary, timestamp table, procedural steps, parameters, quotes, open questions (what the SOP was built from) | [`notes/`](notes/) |
| Transcripts: YouTube auto-captions for 20 videos, Whisper large-v3-turbo transcripts for the videos done so far | [`transcripts/`](transcripts/) |
| Keyframes: a contact sheet per video, and one frame for every moment the SOP cites | [`keyframes/`](keyframes/README.md), [`keyframes/sop-frames.md`](keyframes/sop-frames.md) |
| Step visualizations: eight schematic GIFs of the run, plus the semi-transparent-operator test | [`viz/`](viz/README.md) |
| Narrated tutorials: scripts, build pipeline, upload log | [`tutorials/`](tutorials/README.md) |
| Inventory of the videos (id, title, date, duration, privacy) | [`videos.json`](videos.json) |
| The scripts that made all of this | [`tools/`](tools/) |

## How it was made

1. **Inventory** ([`tools/list_channel.py`](tools/list_channel.py)): the channel's uploads playlist through the YouTube Data API with
   the repo's upload/read token, filtered to the atomizer titles ([`tools/video_ids.txt`](tools/video_ids.txt)).
2. **Download** ([`tools/dl.sh`](tools/dl.sh)): YouTube refuses the player to a GitHub Actions runner ("sign in to confirm you're not a
   bot", as `CLAUDE.md` records), so the Pi 5 stream cam fetched the auto-captions, the audio (m4a) and a 360p video copy with
   `yt-dlp` at ≤3 MB/s, and the runner pulled them over Tailscale with `rsync --bwlimit`. 1.7 GB, nothing left on the Pi except
   `~/atomizer-dl/`, which can be deleted.
3. **Transcription** ([`tools/transcribe.py`](tools/transcribe.py)): `faster-whisper` **large-v3-turbo**, int8, batched with VAD, which is the
   largest Whisper model this 4-core, no-GPU runner handles at a useful speed (about 4× realtime when it has the machine to
   itself, 2× when sharing). The 26 videos total 11.2 hours, so one session cannot transcribe all of them; the queue runs videos
   without YouTube captions first, then the training videos. YouTube's auto-captions ([`tools/vtt2txt.py`](tools/vtt2txt.py)) stand in
   for the rest and are labelled as such in [`timestamps.md`](timestamps.md). Finished files land in
   [`transcripts/whisper/`](transcripts/whisper/); re-run the script to continue the queue.
4. **Indexing**: four reading agents turned the caption text into the per-video tables in [`notes/`](notes/), keeping the
   caption start time of every row so that each becomes a link. [`tools/make_timestamps.py`](tools/make_timestamps.py) assembles
   [`timestamps.md`](timestamps.md) from those tables.
5. **Keyframes** ([`tools/keyframes.py`](tools/keyframes.py), [`tools/sop_frames.py`](tools/sop_frames.py)): scene-change detection plus a frame
   every two minutes for the contact sheets; a frame at the exact cited second for every SOP reference.
6. **SOP**: drafted from the indexes with a fixed outline and the link convention, then reviewed. Where the captions disagree or
   are garbled, the SOP says so and lists the item under *Open questions*; the videos stay the authority.
7. **Visualizations** ([`viz/atomizer_steps.py`](viz/atomizer_steps.py)): a state-driven schematic rendered by matplotlib into one GIF
   per step, the same GIF-per-step idea as the assembly and machining clips in #245 and #232.
8. **Tutorials** ([`tutorials/build_tutorials.py`](tutorials/build_tutorials.py)): title cards and the step GIFs narrated with Microsoft Edge TTS
   `en-US-SteffanNeural` at 1×, interleaved with clips of the trainer's own explanations cut from the training videos (human
   narration wherever it exists), concatenated to 720p and uploaded unlisted with [`../youtube/yt_service.py`](../youtube/yt_service.py).

## Link convention

`https://www.youtube.com/embed/<id>?start=<seconds>` opens YouTube's embed player at that second **without autoplay**
(embeds only autoplay with `autoplay=1`); `https://www.youtube.com/watch?v=<id>&t=<seconds>s` is the same moment on the
normal watch page, which does autoplay. Unlisted videos open with either. Times are caption start times, so a link lands a
second or two before the words.

## Status and follow-ups

- Whisper transcripts exist for the videos listed in [`transcripts/whisper/`](transcripts/whisper/); the rest of the queue is a
  follow-up ping away (`python atomizer-training/tools/transcribe.py` after re-fetching audio from the Pi, or from the YouTube
  originals). The `notes/` and `timestamps.md` rows were made from auto-captions and should be re-checked against the Whisper
  text where it changes a number.
- *The expert cleaning the atomizer, pov* has sound but Whisper's voice-activity filter found no speech in it; it is probably
  machine noise, but re-run it with `vad_filter=False` to be sure.
- The `graining`/`draining` HMI label, the torque units, the Oct 2 "17" pressure reading and which plate ran on Oct 2 are the
  open questions in the SOP that only someone at the machine can close.
