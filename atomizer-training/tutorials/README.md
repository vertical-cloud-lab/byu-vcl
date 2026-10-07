# Narrated tutorials

Four tutorial videos assembled from the material in this folder, uploaded **unlisted** to the BYU Vertical Cloud Lab
channel for review. Draft 4 replaces draft 3 after Sterling's review on PR #255: no part of the 3D model passes through
another any more, tutorial 1 follows the order of a real run (utilities, furnace, chamber, then the ultrasonic stack before
the door closes), and the cleaning step takes the nut off from below before the crucible comes out. All four sets are listed
below, since the upload token cannot delete videos.

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

| Tutorial | Draft 4 | Draft 3 (superseded) | Draft 2 (superseded) | Draft 1 (superseded) |
| --- | --- | --- | --- | --- |
| 0 · The machine and how it works | [5:27](https://www.youtube.com/watch?v=-yxOIJfhs80) | [draft 3](https://www.youtube.com/watch?v=raIcdus1lI0) | [draft 2](https://www.youtube.com/watch?v=uVVeTokW3Us) | [draft 1](https://www.youtube.com/watch?v=p6jlgTJEOw4) |
| 1 · Before a run: utilities, furnace, chamber, stack | [11:03](https://www.youtube.com/watch?v=xpkbazHT_7M) | [draft 3](https://www.youtube.com/watch?v=KwY4KTY1UdI) | [draft 2](https://www.youtube.com/watch?v=qiBB0lIXUDM) | [draft 1](https://www.youtube.com/watch?v=eKH7y4JgJD8) |
| 2 · During a run: gas wash, melt, pour, end of pour | [7:43](https://www.youtube.com/watch?v=Jex6lDcERUM) | [draft 3](https://www.youtube.com/watch?v=79QQtmIm0JM) | [draft 2](https://www.youtube.com/watch?v=sagBBb78pVQ) | [draft 1](https://www.youtube.com/watch?v=cGxBFZyFmCY) |
| 3 · After a run: shutdown, cool-down, powder, cleaning | [6:20](https://www.youtube.com/watch?v=VWa33SEvFJw) | [draft 3](https://www.youtube.com/watch?v=TvaFwSyqaog) | [draft 2](https://www.youtube.com/watch?v=50j8N8YyDxU) | [draft 1](https://www.youtube.com/watch?v=wPzP6I3jT5w) |

Draft 4 went up already titled in the playlist's pattern (*Atomizer tutorial N: … (draft 4)*) and described from
[`../playlist/catalog.py`](../playlist/catalog.py): summary, chapters, the training-video moment behind every clip, and
links pinned at `6c5da5f`. Drafts 1 and 2 are titled `[superseded] …`. Deleting them is still to do: it needs the full token
and a go-ahead.

**Playlist.** The atomizer playlist, <https://www.youtube.com/playlist?list=PLB8wxmcPAjLM>, opens with the tutorials,
ahead of the cups tutorial, the stitch and the recordings. Draft 4 has been in positions 1–4 since 2026-10-07, without
"(draft 4)" in the titles, and draft 3 is labelled `[superseded] …`. See [`../playlist/README.md`](../playlist/README.md).

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
- [`upload.py`](upload.py): uploads `out/*.mp4` unlisted with the upload-only token, with the title from `scripts.py` and
  the description that `../playlist/catalog.py` gives the tutorial (`--ref <pushed sha>` pins its links). It records ids per
  draft in [`uploads.json`](uploads.json). For a new draft:
  1. build;
  2. `python build_tutorials.py --timeline` for the chapter times;
  3. update the catalog entries and push;
  4. upload;
  5. swap the ids in the catalog.
- The rendered `out/*.mp4` are not committed (tens of MB each); the uploads are the deliverable, and the build is
  reproducible.

## Known limitations

- The clips are 720p, the best HLS stream `hls_sections.py` found for these videos. HMI screens filmed from a distance
  stay hard to read.
- The narration reads the SOP as written on 2026-10-03. When the SOP's open questions get answered, update `scripts.py` and
  rebuild.
- The 3D model's proportions are measured from 720p frames and scaled to the documented envelope, but not yet checked
  with a tape measure. See [`../viz3d/README.md`](../viz3d/README.md).
