# Narrated tutorials

Four tutorial videos assembled from the material in this folder, uploaded **unlisted** to the BYU Vertical Cloud Lab
channel for review. Draft 2 replaces draft 1 after Sterling's review on PR #255; both sets are listed below, since the
upload token cannot delete videos.

## How each tutorial is put together

Every tutorial has the same shape, so the four read as one series:

1. **Title** over the 3D render of the machine.
2. **Outline**: a draw.io diagram of the tutorial's steps ([`diagrams/`](diagrams/README.md)).
3. **For each step**:
   - the outline again, with that step highlighted;
   - the **3D animation** of the step ([`../viz3d/`](../viz3d/README.md)), narrated by Microsoft Edge TTS
     `en-US-AndrewMultilingualNeural` at 1×, with each sentence timed to the sub-step it describes;
   - **Bartosz Kalicki (AMAZEMET) explaining it in his own words**, cut from the training videos.
4. A closing card pointing to the next tutorial.

Segments are joined with 0.4 s crossfades.

**The clips:**

- **Cuts.** Every cut starts at the beginning of a sentence and ends at the end of one. [`clip_words.py`](clip_words.py) runs
  word-timed Whisper (large-v3-turbo) on a window around each clip and moves the cut to the nearest boundaries. The words are
  cached in [`clip_words/`](clip_words/).
- **Subtitles.** The same words are burned in as subtitles.
- **Stabilisation.** Clips are stabilised with ffmpeg's two-pass `vidstab`.
- **Audio.** Clip audio is loudness-matched to the narration, after a light high-pass and denoise.
- **Portrait phone video** gets a blurred fill instead of black bars.
- **Label.** A top bar names the speaker, the video and the time, so each moment can be found in [`../timestamps.md`](../timestamps.md).

## Uploads

| Tutorial | Draft 2 | Draft 1 (superseded) |
| --- | --- | --- |
| 0 · The machine and how it works | _see [`uploads.json`](uploads.json)_ | https://www.youtube.com/watch?v=p6jlgTJEOw4 |
| 1 · Before a run | | https://www.youtube.com/watch?v=eKH7y4JgJD8 |
| 2 · During a run | | https://www.youtube.com/watch?v=cGxBFZyFmCY |
| 3 · After a run | | https://www.youtube.com/watch?v=wPzP6I3jT5w |

**Playlist.** Creating a playlist needs the channel's full token (`playlists.insert` requires the `youtube` scope), which
only an `@claude-youtube` run has. [`../../youtube/make_playlist.py`](../../youtube/make_playlist.py) is ready for it (see the
command at the end of this file).

## Files

- [`scripts.py`](scripts.py): the narration text and the segment list of every tutorial. Edit the words here.
- [`build_tutorials.py`](build_tutorials.py): renders the cards, times the narration against the animations, cuts and
  stabilises the clips, normalises everything to 1280×720 h264/aac and crossfades the segments together. It needs:
  - `ffmpeg` with `vidstab` and `libass` (Ubuntu's build has both), `edge-tts`, Pillow and `faster-whisper`;
  - the local video and audio copies (`ATOMIZER_DL`, default `/tmp/work/dl`; see [`../tools/dl.sh`](../tools/dl.sh));
  - the MP4s from `../viz3d/steps.py` and the PNGs from `diagrams/make_diagrams.py`.
- [`clip_words.py`](clip_words.py): word-timed Whisper for the clip windows, cached in `clip_words/`.
- [`upload.py`](upload.py): uploads `out/*.mp4` unlisted with the upload-only token. It records ids per draft in
  [`uploads.json`](uploads.json).
- The rendered `out/*.mp4` are not committed (tens of MB each); the uploads are the deliverable, and the build is
  reproducible.

## Known limitations

- Clips come from the 360p copies, so HMI screens are not readable in them. Re-run with 720p sources for that.
- The narration reads the SOP as written on 2026-10-03. When the SOP's open questions get answered, update `scripts.py` and
  rebuild.
- The 3D model is plausible rather than measured: proportions come from the keyframes and the vendor documents. See
  [`../viz3d/README.md`](../viz3d/README.md).
