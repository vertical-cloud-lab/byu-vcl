# Narrated tutorials

Four tutorial videos assembled from the material in this folder, uploaded **unlisted** to the BYU Vertical Cloud Lab
channel for review. Draft 2 replaces draft 1 after Sterling's review on PR #255; both sets are listed below, since the
upload token cannot delete videos.

## How each tutorial is put together

Every tutorial has the same shape, so the four read as one series:

1. **Title** over the 3D render of the machine.
2. **Outline**: a draw.io diagram of the tutorial's steps ([`diagrams/`](diagrams/README.md)), built up like a
   PowerPoint slide: the step boxes first, then each step's details appear, with no fade, as the narration names it.
3. **For each step**:
   - the outline again, with that step highlighted;
   - the **3D animation** of the step ([`../viz3d/`](../viz3d/README.md)), narrated by Microsoft Edge TTS
     `en-US-AndrewMultilingualNeural` at 1×, with each sentence timed to the sub-step it describes;
   - **Bartosz Kalicki (AMAZEMET) explaining it in his own words**, cut from the training videos.
4. A closing card pointing to the next tutorial.

Segments are joined with 0.4 s crossfades, except into and out of the outline build, which are hard cuts like slide
changes.

**The clips:**

- **Source.** The picture comes from 720p windows of the training videos (portrait 720×1280 for the phone video), fetched
  as HLS segments by [`../tools/hls_sections.py`](../tools/hls_sections.py). The sound comes from the full-length audio
  track. Each window is decoded from its start and cut by timestamp, so the cut is frame-exact. The window's `t0` is the video
  time of its first frame. This was checked against the 360p copy: the matching frame is the same one, not one frame off
  as the `.ts` timestamps would suggest.
- **Cuts.** Every cut starts at the beginning of a sentence and ends at the end of one. [`clip_words.py`](clip_words.py) runs
  word-timed Whisper (large-v3-turbo) on a window around each clip and moves the cut to the nearest boundaries. The words are
  cached in [`clip_words/`](clip_words/).
- **Subtitles.** The same words are burned in as subtitles.
- **Stabilisation.** Clips are stabilised with ffmpeg's two-pass `vidstab`. It crops rather than show moving edges: each
  clip is zoomed in by the fixed amount its corrections need. The corrections are capped, so the zoom never passes 10 %
  (9 % of each dimension, 4.5 % a side); a jolt beyond the cap stays partly in the picture. Smoothing is over about 1 s.
  The label bar and the subtitles are drawn after the stabilisation, so they are never cropped.
- **Audio.** Clip audio is loudness-matched to the narration, after a light high-pass and denoise.
- **Portrait phone video** gets a blurred fill instead of black bars.
- **Label.** A top bar names the speaker, the video and the time, so each moment can be found in [`../timestamps.md`](../timestamps.md).

## Uploads

| Tutorial | Draft 2 | Draft 1 (superseded) |
| --- | --- | --- |
| 0 · The machine and how it works | [5:16](https://www.youtube.com/watch?v=uVVeTokW3Us) | [3:31](https://www.youtube.com/watch?v=p6jlgTJEOw4) |
| 1 · Before a run: utilities, stack, furnace, chamber | [8:45](https://www.youtube.com/watch?v=qiBB0lIXUDM) | [6:04](https://www.youtube.com/watch?v=eKH7y4JgJD8) |
| 2 · During a run: gas wash, melt, pour, end of pour | [7:38](https://www.youtube.com/watch?v=sagBBb78pVQ) | [8:08](https://www.youtube.com/watch?v=cGxBFZyFmCY) |
| 3 · After a run: shutdown, cool-down, powder, cleaning | [5:54](https://www.youtube.com/watch?v=50j8N8YyDxU) | [6:42](https://www.youtube.com/watch?v=wPzP6I3jT5w) |

Draft 1 can be deleted in YouTube Studio once draft 2 is accepted (the upload token cannot delete).

**Playlist.** Creating a playlist needs the channel's full token (`playlists.insert` requires the `youtube` scope), which
only an `@claude-youtube` run has. [`../../youtube/make_playlist.py`](../../youtube/make_playlist.py) is ready for it:

```bash
python youtube/make_playlist.py --title "rePowder atomizer tutorials (draft 2)" --privacy unlisted --ids uVVeTokW3Us qiBB0lIXUDM sagBBb78pVQ 50j8N8YyDxU
```

## Files

- [`scripts.py`](scripts.py): the narration text and the segment list of every tutorial. Edit the words here.
- [`build_tutorials.py`](build_tutorials.py): renders the cards, times the narration against the animations, cuts and
  stabilises the clips, normalises everything to 1280×720 h264/aac and crossfades the segments together. It needs:
  - `ffmpeg` with `vidstab` and `libass` (Ubuntu's build has both), `edge-tts`, Pillow and `faster-whisper`;
  - the full-length audio copies, `<id>.m4a` (`ATOMIZER_DL`, default `/tmp/work/dl`; see [`../tools/dl.sh`](../tools/dl.sh));
  - the 720p windows, `<id>_<start>.ts` with their `.json` (`ATOMIZER_HLS`, default `/tmp/work/hls`; see
    [`../tools/hls_sections.py`](../tools/hls_sections.py)). A clip that no window covers falls back to the 360p copy
    `<id>.v360.mp4` in `ATOMIZER_DL`, with a warning;
  - the MP4s from `../viz3d/steps.py` and the PNGs from `diagrams/make_diagrams.py`.

  On a shared machine, `ATOMIZER_THREADS=2 nice -n 10 python build_tutorials.py` caps every ffmpeg call at two threads.
- [`clip_words.py`](clip_words.py): word-timed Whisper for the clip windows, cached in `clip_words/`.
- [`upload.py`](upload.py): uploads `out/*.mp4` unlisted with the upload-only token. It records ids per draft in
  [`uploads.json`](uploads.json).
- The rendered `out/*.mp4` are not committed (tens of MB each); the uploads are the deliverable, and the build is
  reproducible.

## Known limitations

- The clips are 720p, the best HLS stream `hls_sections.py` found for these videos. HMI screens filmed from a distance
  stay hard to read.
- The narration reads the SOP as written on 2026-10-03. When the SOP's open questions get answered, update `scripts.py` and
  rebuild.
- The 3D model is plausible rather than measured: proportions come from the keyframes and the vendor documents. See
  [`../viz3d/README.md`](../viz3d/README.md).
