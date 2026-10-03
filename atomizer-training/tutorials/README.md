# Narrated tutorials

Four draft tutorial videos assembled from the material in this folder, uploaded **unlisted** to the BYU Vertical Cloud Lab
channel for review. Each one alternates two kinds of narration:

- **Human**: Bartosz Kalicki (AMAZEMET) explaining a step in his own words, cut straight from the training videos (360p copy,
  upscaled, with a lower-third naming the speaker, video and time so the moment can be found in
  [`../timestamps.md`](../timestamps.md)).
- **Synthetic**: Microsoft Edge TTS voice `en-US-SteffanNeural` at 1×, reading a summary of the SOP over the step animations
  from [`../viz/`](../viz/README.md) and over title cards.

| Tutorial | Length | Unlisted link |
| --- | --- | --- |
| 0 · Installation and training overview | | see [`uploads.json`](uploads.json) |
| 1 · Before a run (utilities, stack, furnace, loading) | 6:04 | https://www.youtube.com/watch?v=eKH7y4JgJD8 |
| 2 · During a run (gas wash, heating, pour) | | see [`uploads.json`](uploads.json) |
| 3 · After a run (shutdown, cooldown, powder, cleaning) | | see [`uploads.json`](uploads.json) |

**Playlist.** Creating a playlist needs the channel's full token (`playlists.insert` requires the `youtube` scope), which
only an `@claude-youtube` run has. [`../../youtube/make_playlist.py`](../../youtube/make_playlist.py) is ready for it:

```bash
python youtube/make_playlist.py --title "rePowder atomizer tutorials (draft)" --privacy unlisted --ids <ids from uploads.json in order 00 01 02 03>
```

## Files

- [`scripts.py`](scripts.py): the narration text and the segment list of every tutorial. Edit the words here.
- [`build_tutorials.py`](build_tutorials.py): renders cards, animates the GIFs to the narration length, cuts the clips, normalises
  everything to 1280×720 h264/aac and concatenates. Needs `ffmpeg`, `edge-tts`, Pillow, and the local video/audio copies
  (`ATOMIZER_DL`, default `/tmp/work/dl`).
- [`upload.py`](upload.py): uploads `out/*.mp4` unlisted with the upload-only token and records ids in [`uploads.json`](uploads.json).
- The rendered `out/*.mp4` are not committed (40–60 MB each); the uploads are the deliverable, and the build is reproducible.

## Known limitations of this draft

- Clips are from the 360p copies, so the HMI screens are not readable in them; the build can be re-run with 720p sources.
- Clip boundaries come from caption start times (±2 s), so a few clips begin mid-sentence.
- The synthetic narration reads the SOP as written on 2026-10-03; where the SOP's open questions get answered, update
  `scripts.py` and rebuild.
- Nothing is cut from the three uncaptioned videos (expert cleaning POV, cartridge cleaning, drill press); they can be added
  once their Whisper transcripts are indexed.
