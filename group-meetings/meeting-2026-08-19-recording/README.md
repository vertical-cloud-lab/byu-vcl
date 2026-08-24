# VCL weekly group meeting — 2026-08-19 — recording artifacts

Recording of the weekly group meeting on high-level thoughts about the use of AI in the lab
([issue #183](https://github.com/vertical-cloud-lab/byu-vcl/issues/183); compilation in
[`../ai-in-the-lab.md`](../ai-in-the-lab.md)).

## Source

- **Original recording**: `VCL weekly group meeting-20260819_160112UTC-Meeting Recording.mp4`
  on Sterling's BYU OneDrive —
  [SharePoint/Stream share link](https://byu-my.sharepoint.com/:v:/g/personal/sbaird9_byu_edu/IQAhCotWVHEJQ4FQHXVHsz1VASzsf4iyN8yh_-5Clg94V58?e=au0TVR).
  75:34 (4534.7 s), 1920×1080 H.264 @ 16 fps, 16 kHz mono AAC, 453.7 MiB.
  Recorded 2026-08-19 16:01–17:16 UTC.
- **YouTube upload (unlisted)**:
  [VCL weekly group meeting - High-level thoughts about use of AI in the lab](https://youtu.be/f5_cQvuNKnA)
  — 62:01, published 2026-08-20 on the BYU Vertical Cloud Lab channel. It is ~13.5 min
  shorter than the original, so chapter times below (original timeline) shift accordingly.

The share link is anonymously accessible (verified 2026-08-20 from a GitHub Actions
runner — no BYU sign-in or residential IP needed). To re-download the original file:
`yt-dlp -f source "<share link>"` (the `source` format is the pristine MP4).

## Files in this directory

| File | Description |
|---|---|
| `transcript.vtt` | Teams meeting transcript, WebVTT as served by Stream |
| `transcript.json` | Same transcript, structured entries with speaker IDs and confidences |
| `transcript.txt` | Readable rendering, one line per utterance (`[HH:MM:SS] @speaker: text`) |
| `chapters.txt` | Derived chapter markers in YouTube-description format (original 75:34 timeline) |
| `audrey-carl-clip.vtt` | Captions re-timed for the extracted Audrey & Carl discussion clip |
| [`highlights/`](highlights/) | Edited 6:10 highlights compilation — EDL, render script, captions, chapters, contact-sheet preview (the MP4 itself is on the draft release and the Pi) |

Stream has **no auto-generated chapters** for this video (`tableOfContentsVisibility: none`),
so `chapters.txt` was derived by hand from the transcript.

Speaker names come through anonymized (`@1`–`@4`) when the transcript is fetched via the
anonymous share link. Mapping, from on-screen name labels in the video and dialog context:

| ID | Person | Evidence |
|---|---|---|
| `@1` | Gage (inferred) | Online only until ~00:15 ("I'm pulling up at BYU right now"); Sterling lists the online trio as "Audrey, Gage, Carl" |
| `@2` | Carl Robison | On-screen participant label; answers "Carl, can you hear me?" |
| `@3` | Sterling Baird + in-room speakers | Recording ran on Sterling's account; the room mic attributes all in-person speech to this one channel |
| `@4` | Audrey Christiansen | On-screen participant label |

## Extracted clip: Audrey & Carl discussion

The eighth pair discussion from this meeting (the other seven were uploaded to the channel
on 2026-08-19 — see the compilation). Audrey and Carl joined remotely, so their breakout
happened inside the meeting itself; Sterling notes at 1:01:24 of the recording that their
discussion "is already recorded" and just needs uploading to the channel.

- **Boundaries**: 00:40:40.8 → 01:01:06.6 of the original recording (duration 20:25.8).
  Opens on the screen-shared prompt ("What is an experience where the use of AI has helped
  you learn in the lab or enhance productivity?"); the second question (what lab culture do
  we want around AI) starts at clip time ~10:28; ends as Audrey finishes "…make sure,
  whatever you use it for, you're comfortable declaring to the professor."
- **Encoding**: frame-accurate re-encode, H.264 CRF 20 at source resolution/frame rate,
  63.6 MB.
- **Suggested title** (matches the channel's naming convention):
  *Discussion between Audrey Christiansen and Carl Robison about experiences with AI in the lab*
- **Captions**: upload `audrey-carl-clip.vtt` alongside it.

## Where the large artifacts live

Video files are deliberately **not** committed to git.

- **Raspberry Pi** (the stream-cam Pi whose Tailscale hostname is injected as
  `$RPI_STREAM_CAM_HOSTNAME` in the coding-agent workflow): `~/vcl-meeting-recordings/2026-08-19/`
  holds the full original MP4, the extracted clip, and copies of all transcript/chapter
  files (placed 2026-08-20; ~515 MB total, ~21.6 GB free on the card afterwards).
- **Draft GitHub release** [`meeting-2026-08-19-recording`](https://github.com/vertical-cloud-lab/byu-vcl/releases)
  (visible to repo collaborators only while a draft): the extracted clip, its captions, and
  the chapters file — downloadable without touching the Pi.
- The full recording can always be re-fetched from the share link above.

## Transcript API recipe (for future sessions)

The Stream watch page (`stream.aspx`, reached by following the share-link redirect) embeds a
`g_fileInfo` JSON containing `.spItemUrl` and `.driveAccessTokenV21`. With those:

- List transcripts: `GET {spItemUrl, with /_api/v2.0/ → /_api/v2.1/}/media/transcripts`
  with header `Authorization: Bearer {.driveAccessTokenV21}`
- Download: the `temporaryDownloadUrl` from the listing (send `Accept: */*`; returns VTT), or
  `…/media/transcripts/{id}/streamContent?format=json` for the structured version with
  speaker IDs (`format=docx` also works)

Tokens are short-lived but re-derivable from the share link at any time.
