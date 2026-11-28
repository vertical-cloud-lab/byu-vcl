---
name: stream-cams
description: Lab livestream cameras and the YouTube archive - BYU VCL Hardware Streams channel and playlist IDs, the picam-ot2 atomizer camera (144p, pixelation, overlay --flush patch), and reading archived streams back (yt-dlp is bot-blocked on Actions runners, the archive timeline is not wall clock, OCR the burned-in clock). Use for stream camera, YouTube livestream or archive-frame tasks.
---

# Stream cameras and the livestream archive

The rules in the root `CLAUDE.md` apply throughout: never print a credential, hostname or IP, and treat every Pi as a live production device.

**YouTube.** Channel `UCZ5KNGkEEqDsRVn0Nlfn0IA` ("BYU VCL Hardware Streams"), OT-2 playlist
`PLdKz1vXA-rfQ` ("OT-2 Livestreams Playlist"). Both are stored as Space *variables*, not
secrets, since they are public identifiers. `YT_FALLBACK_VIDEO_ID` is the embed shown when
the API is unavailable. Note the playlist ID is unusually short — that is genuine, not a
truncation.

**The `picam-ot2` camera now shows the atomizer room, not the OT-2.** As of 2026-10-01 that
camera (the Pi behind `OT2_STREAM_CAM_HOSTNAME`) streams 144p at 2 fps under workflow
`atomizer`. Since 19:55 MDT it is also pixelated on the Pi (`PIXELATE_BLOCKS` in its
`my_secrets.py`, another local `device.py` patch), so that it shows activity rather than
detail: 32×18 solid blocks at first, 128×72 (2×2 px at 144p) since 22:59 MDT. The overlay is
drawn afterwards and stays sharp. Its broadcasts
are titled *atomizer stream picam-ot2, …* and go into the *atomizer Livestreams Playlist*
(`PLeosQpHvsjiY`), not the OT-2 playlist above. Its settings, change log
and the archive tooling's 720p assumptions are in [`docs/stream-cams.md`](../../../docs/stream-cams.md),
along with how the Lambda matches a workflow name to playlists. The match is by substring,
which matters before renaming one.

**On that camera, the overlay is only a clock from 2026-10-01 18:52 MDT.** Without
`rpicam-vid --flush`, ffmpeg received frames in 4 KB batches. At 240p and 2 fps the overlay
stood still for 3–4 s, then jumped, and a third of the frames were copies. The Pi's
`device.py` now has `--flush` and `-flags low_delay`, a local patch like `SENSOR_MODE`,
which leaves the overlay about one frame behind capture. Any picam at a low resolution or
frame rate needs the same patch, and it is worth upstreaming to `ac-training-lab`.

**Reading the livestream archive back.** Two things cost a session to find, both in
`wireless-color-sensor/ot2/`:

- **YouTube will not do player extraction from a GitHub Actions runner.** `yt-dlp` on a
  runner returns *"Sign in to confirm you're not a bot"* for `--dump-json`, `-g` and any
  download, with or without a JS runtime. The channel/playlist *listing* works fine from
  anywhere — only the player is blocked. Run the fetching half from a stream-cam Pi's
  residential IP (it was the OT-2 lid camera Pi, gone since 2026-11-10; `grab.py` is
  preserved in digital-wetlab, so set it up again on whichever Pi replaces it): `~/.venvs/ytframes/bin/yt-dlp --js-runtimes node` (node is present; deno
  is not), with a static ffmpeg in `~/ytframes/bin`. That ffmpeg **cannot resolve DNS** —
  statically linked glibc has no NSS — so fetch HLS segments with urllib/curl and only ever
  hand ffmpeg a local file. `~/ytframes/grab.py` does exactly that and is the thing to
  reuse.
- **The archive timeline is not wall clock.** `release_timestamp` is where video offset 0
  sits at the very start, but for `bQDrYpT3vaE` everything from the third hour onward is
  **67 s later** than `release + offset` — a step, not a drift, i.e. an archive
  concatenated across a stall. At ~18 s per scan position that is more than one
  measurement, so a link computed from the metadata alone points at the wrong reading.
  Verify instead: the stream burns `%Y-%m-%d_%H-%M-%S` in **lab local time (UTC−6)** into
  the top-left of every frame, so `frames_from_stream.py` grabs, OCRs the overlay
  (`tesseract --psm 7`), and re-grabs shifted by the error. Treat that overlay as the
  clock, not the metadata.
