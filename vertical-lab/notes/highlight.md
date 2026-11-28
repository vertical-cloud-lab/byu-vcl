# Highlights of the vertical lab

Two editions. The current one, asked for on PR #390 (2026-11-28,
https://github.com/vertical-cloud-lab/byu-vcl/pull/390): "can we get this updated with the most recent vertical lab
progress across all of this repo (see all issue and PR comments via gh API) and DAL (if applicable)? Re-uploaded to
YouTube. Public with notify subscribers." The first edition, round 15's alloy route in eight shots, is further down;
its script is [`highlight.py` at d349073](https://github.com/vertical-cloud-lab/byu-vcl/blob/d349073/vertical-lab/highlight.py)
and its outputs stay where they were, in [`out/highlight/`](../out/highlight/).

## The 2026-11-28 edition: the alloy route, the real atomizer, what's new, the twin

- The cut: [`out/highlight/2026-11-28/vertical_lab_highlight_2026-11-28.mp4`](../out/highlight/2026-11-28/vertical_lab_highlight_2026-11-28.mp4),
  3:37, 1280 × 720 at 30 fps, silent, 18 shots, a YouTube chapter for each. On YouTube, **public, subscribers
  notified**: [b3kamYpyCpo](https://www.youtube.com/watch?v=b3kamYpyCpo) (uploaded 2026-11-28 08:40 UTC, processed in
  HD). Its record (every part's times and source, the MP4's sha256, the upload) is
  [`highlight.json`](../out/highlight/2026-11-28/highlight.json), and the description as uploaded is
  [`youtube_description.txt`](../out/highlight/2026-11-28/youtube_description.txt). The first edition's unlisted
  upload (lnpVq8JvnJM) is untouched: the run's YouTube token can upload but not edit or delete.
- The stills: [`out/highlight/2026-11-28/stills/`](../out/highlight/2026-11-28/stills/), one 1280 × 720 PNG per shot,
  each the cut's own frame with its band; [`highlight_sheet.png`](../out/highlight/2026-11-28/highlight_sheet.png)
  puts them side by side.
- The script: [`highlight.py`](../highlight.py) (`fetch`, `sheets`, `bandscan`, `build`, `upload`).

### What "the most recent progress" was, and where it came from

All 271 issue and PR comments in this repo since 2026-11-18 were pulled through the API (every person's comment, each thread's
latest report and every video link in them), and DAL's since the same day.
What had happened since the first edition's round 15:

| Progress | Where | In the cut |
|---|---|---|
| Round 16's long-form, 1:31:05, 69 chapters: the alloy route's chapters 1, 2, 4, 5 and 7 re-rendered, and a person changing a vacuum liner (#371's check) | PR #318, [YWbplBXPC84](https://www.youtube.com/watch?v=YWbplBXPC84) (unlisted) | shots 1-7, 13, 18 |
| The PRs merged into #318 on 2026-11-20 and 11-23 and drawn in rounds 15-16: atomizer automation (#353), tray services and UPSs, Class D extinguishers (#379), floor cleaning (#369), the scale-up machines | PRs #353, #369, #379, #318 | shots 9-12, 14 |
| The atomizer's real runs: 10 logged from 2 Oct to 13 Nov, 5 aluminium and 5 630 bronze; Oct 27 and 28 sieved together, 1,015 g under 250 µm from 1,938 g charged | [DAL PR 286](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/286) | shot 8 |
| The digital twin, round 5 (488 runs, finished) and its two-year cut, with the floor-space comparison of PR #406 | PRs #405, #428, [Ty6njW-GF74](https://www.youtube.com/watch?v=Ty6njW-GF74) (unlisted preview) | shots 15-17 |
| Twin round 6 | PR #427, running on Actions | the end card only |
| Is the vertical lab worth it? | PR #410 (open) | the description only |

Left out: everything outside the vertical lab (the CubXL stir module, the deck keys, the toy drive, open science),
and twin rounds 3-4, which round 5 supersedes.

### The shots

| # | In the cut | Source | Caption |
|---|---|---|---|
| 1 | 0:00 | [round 16, 19:27](https://youtu.be/YWbplBXPC84?t=1167) | powder-doser's chain carousel v5 · A&D HR-202i balance · Specac Atlas Autotouch 15T vacuum press |
| 2 | 0:15 | [28:33](https://youtu.be/YWbplBXPC84?t=1713) | AMAZEMET rePowder ultrasonic atomizer, cut open for the pour |
| 3 | 0:27 | [47:41](https://youtu.be/YWbplBXPC84?t=2861) | Retsch AS 200 sieve shaker, in a downdraft enclosure |
| 4 | 0:39 | [52:27](https://youtu.be/YWbplBXPC84?t=3147) | Rigaku MiniFlex benchtop powder XRD, its housing drawn see-through |
| 5 | 0:52 | [1:00:08](https://youtu.be/YWbplBXPC84?t=3607) | Instron 68FM-100 · 3119-608 environmental chamber · AVE 2 video extensometer |
| 6 | 1:04 | [1:04:54](https://youtu.be/YWbplBXPC84?t=3894) | LECO PX500 grinder-polisher and its magazine of pre-loaded discs |
| 7 | 1:15 | [1:07:19](https://youtu.be/YWbplBXPC84?t=4039) | Hitachi TM4000PlusII tabletop SEM · Oxford Instruments AZtecOne EDS |
| 8 | 1:27 | [2brsz-90seg, 5:29 and 8:17](https://youtu.be/2brsz-90seg?t=497), real | The lab's own rePowder, 27 Oct 2026: 630 bronze molten, then atomizing; the sieved powder (DAL PR 286) |
| 9 | 1:37 | [37:44](https://youtu.be/YWbplBXPC84?t=2264) | The arm swaps the ultrasonic plate: the old one off its M8 stud, a W-coated plate on (#353) |
| 10 | 1:48 | [4:14](https://youtu.be/YWbplBXPC84?t=254) | Stäubli CombiTac dock: power, Ethernet, air, N2 and chilled water mate in a set order; each powered tray has a UPS |
| 11 | 1:59 | [9:00](https://youtu.be/YWbplBXPC84?t=539) | Amerex B570 Class D extinguishers, 30 lb of Super D: on every MiR250 in an 811 bracket, and at each powder station |
| 12 | 2:09 | [1:24:49](https://youtu.be/YWbplBXPC84?t=5089) | Unit 3 squeegees the floor on a Nilfisk CFM 118EXP explosion-proof vacuum's hose, then its camera checks the colour |
| 13 | 2:20 | [1:28:30](https://youtu.be/YWbplBXPC84?t=5310) | A person changes the 118EXP's liner: sealed in place, lifted out to the Al-family pail (round 16) |
| 14 | 2:31 | [1:18:56](https://youtu.be/YWbplBXPC84?t=4736) | EOS M 400-4: four lasers on one 400 x 400 mm build, two Sentinel-1 antenna brackets after RUAG's case study |
| 15 | 2:42 | [twin, 9:16](https://youtu.be/Ty6njW-GF74?t=556) | From day 161 the run's own bookings move the 3-D lab (seed 1 of 16) |
| 16 | 2:53 | [twin, 14:18](https://youtu.be/Ty6njW-GF74?t=858) | Copper 1.5-2.1x sooner in the automated lab with the funnel, 2x or more with BOFN or pKGFN; aluminium's first target a tie |
| 17 | 3:03 | [twin, 18:20](https://youtu.be/Ty6njW-GF74?t=1100) | The same 45 tray positions: 3,029 sq ft in the vertical lab against 6,192 laid out flat for robots |
| 18 | 3:14 | [1:30:36](https://youtu.be/YWbplBXPC84?t=5436) | The whole lab at speed, ending on the long-form's own "first year" card |

Shots 1-7 are the first edition's moments, found in round 16 through the two videos' `out/longform.json` (every clip
kept its length, so a moment's offset in its clip carries over), then trimmed to 11-13.5 s each so the update stays
near three and a half minutes. In and out points were checked against 1 fps contact sheets and ffmpeg's scene
detection: no shot starts or ends inside a cut or a dissolve.

### What it says, and what it doesn't

- **The real atomizer is real; nothing else is.** Shot 8 uses the excerpts of run k7m2q9 that round 16's chapter 2
  already cuts in (`out/footage/`, from [2brsz-90seg](https://youtu.be/2brsz-90seg)), and DAL's photo of its sieved
  powder. The figure is DAL's weighed one: the Oct 27 and 28 runs were sieved together, <63 µm 187.973 g and 64-250 µm
  827.063 g from 1,938.307 g charged ([DAL PR 286](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/286),
  `atomizer-runs/2026-10-27-nab-k7m2q9/provenance.md`). The video's own YouTube title says Cu70/Ni30; DAL's run table,
  the jars and the long-form say 630 bronze (C63000), and the cut follows DAL.
- **Not claimed:** that the lab's own powder has been printed, that the route has run end to end, that the atomizer is
  running now (no runs since the Nov 13 collection cup failure, DAL #269), or that the twin is calibrated on the lab's
  record. The description says the twin's atomizer rates are design targets against a record of 10 runs in 43 days.
- **The twin's numbers are round 5's own**, as its two-year cut shows them: like for like, 16 runs an arm, with the
  ties shown as ties. DAL PR 293's audit of the round-2 video (stocked against unstocked, different optimizers) is why
  the cut quotes like-for-like figures only.
- **The floor-space shot is a design layout,** and PR #410's answer to "is the vertical lab worth it?" (at the twin's
  load the robots are 1-2 % busy, so transport doesn't bind; floor is the gain) is in the description, so the 51 %
  isn't read as the whole case.
- **Two sources are unlisted on the channel:** round 16's long-form and the twin's two-year preview. The description
  links both, which makes them reachable from a public video.

### How the shots were made

- **Cut from YouTube,** as the first edition was, since no render outlives its runner: round 16's 720p HLS stream
  (itag 232) and the twin's 1080p one (itag 270), scaled to 720p once when its window is cut. Fetched through the CubXL
  Pi's network over an SSH SOCKS tunnel, capped at 1.2 MB/s, nothing installed or written on the Pi: 46 MB of segments
  in all. The 1080p stream's segments answer with a redirect, so `fetch` follows them (`curl -L`).
- **The twin's frames are fitted, not covered:** scaled whole to 1142 × 642 above the band, on their own background,
  since their panels run to the frame's edges. Round 16's shots keep the long-form's picture and cover only its caption
  band, as before (`bandscan` measured its height in each).
- **The real lab's shot is composed:** the upright excerpts (406 × 720) at the left, the photo at the right, each under
  a red badge, the band below.
- **Cards:** a title card naming the four parts and an end card with the two full videos, the code and DAL, both in the
  long-form's card style. No sound, as before.

### Rebuilding it

```bash
cd vertical-lab
ssh -D 127.0.0.1:1080 -N -f "$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME"   # or any lab Pi this run can reach
pip install "yt-dlp[default]"                                         # node is the JS runtime here
python3 highlight.py fetch --rate 1200K        # into $HIGHLIGHT_CACHE (default /tmp/vertical_lab_highlight)
python3 highlight.py sheets                    # 1 fps contact sheets of each window, to move in and out points
python3 highlight.py bandscan                  # round 16's shots: each band_top should cover the long-form's band
python3 highlight.py build                     # out/highlight/2026-11-28/
python3 highlight.py upload --privacy public --notify     # refuses a file already uploaded
```

A shot's times are its `t0`/`t1` in `SHOTS`, in seconds of its source; `still` picks its still.

## The first edition: round 15's alloy route (2026-11-25)

Asked for on PR #318 (2026-11-25, https://github.com/vertical-cloud-lab/byu-vcl/pull/318#issuecomment-7175729752):
"Cut a 2 to 3 minute highlight of round 15's long-form: one shot from each chapter of the alloy route (charge, atomize,
sieve and print, powder checks, machining and tensile, sample prep, characterization), then the whole lab at speed,
with short captions naming each instrument. Upload it unlisted, and commit 8 full-resolution stills, one per chapter,
as PNGs on the branch."

- The cut: [`out/highlight/vertical_lab_highlight_r15.mp4`](../out/highlight/vertical_lab_highlight_r15.mp4), 2:42,
  1280 × 720 at 30 fps, silent. On YouTube, unlisted: [lnpVq8JvnJM](https://www.youtube.com/watch?v=lnpVq8JvnJM),
  with a chapter per shot; the record is in [`out/highlight/highlight.json`](../out/highlight/highlight.json) and the
  description in [`youtube_description.txt`](../out/highlight/youtube_description.txt).
- The stills: [`out/highlight/stills/`](../out/highlight/stills/), 1280 × 720 PNGs, one per chapter plus the whole lab;
  [`highlight_sheet.png`](../out/highlight/highlight_sheet.png) puts them side by side.
- The script: [`highlight.py`](../highlight.py) (`fetch`, `build`, `upload`, and `bandscan` to check the captions).

### Where it comes from

Round 15's chapter renders went with its runner (`out/r15/` is git-ignored, and only chapter 2's 720p render was
committed), so the shots are cut from the long-form as YouTube serves it:
[79FL6mTFSsI](https://www.youtube.com/watch?v=79FL6mTFSsI), 1:28:55, public. Its source file is 1280 × 720, so that is
the full resolution here too.

- **The stream:** YouTube's 720p HLS stream (itag 232, H.264 at 30 fps). It has the highest bitrate YouTube offers for
  this video: 0.88 Mbit/s on average over the segments fetched (YouTube lists up to 2.5), against 0.64 and 0.43 Mbit/s
  for the 720p DASH streams (H.264 and AV1). The stills still carry YouTube's compression.
- **Fetched through a lab Pi:** YouTube refuses player requests from GitHub's runners, so the fetch went through the
  CubXL Pi's network over an SSH SOCKS tunnel, capped at 1.2 MB/s for its Wi-Fi. Nothing was installed or written on
  the Pi. In all, a 240p copy of the whole video (58 MB) was fetched to choose the shots, and then only the 5.3 s
  segments of the 720p stream that cover them (77 segments, 45 MB).
- **Frame-exact cuts:** the segments carry the long-form's own timestamps. Seeking inside a transport stream drops the
  frames up to the next keyframe, which on the first try cost some windows up to 5 s. So each window is decoded from its
  first segment and trimmed on those timestamps. Each shot's in and out points were then set from 1 fps contact sheets
  and ffmpeg's scene-cut detection, so that no shot starts or ends inside a dissolve or a cut to real footage.

### The shots

| # | In the cut | Long-form | Caption: the instruments named | What happens |
|---|---|---|---|---|
| 1 | 0:04 | [18:59-19:19](https://youtu.be/79FL6mTFSsI?t=1139) | powder-doser's chain carousel v5 · A&D HR-202i balance · Specac Atlas Autotouch 15T vacuum press | The arm takes a 5N Al cup from the rack to the doser's shuttle; module 6 docks, tilts and doses Si onto the balance, cut open. |
| 2 | 0:24 | [28:02-28:19](https://youtu.be/79FL6mTFSsI?t=1682) | AMAZEMET rePowder ultrasonic atomizer, cut open for the pour | Both arms take the knobs of the plate's landing stage; the melt pours onto the vibrating plate and atomizes. |
| 3 | 0:40 | [47:11-47:29](https://youtu.be/79FL6mTFSsI?t=2831) | Retsch AS 200 sieve shaker, in a downdraft enclosure | The arm clamps the lid; the stack sieves, drawn see-through; each fraction is tinted under a legend, then grey again. |
| 4 | 0:58 | [51:54-52:14](https://youtu.be/79FL6mTFSsI?t=3114) | Rigaku MiniFlex benchtop powder XRD, its housing drawn see-through | The arm loads the zero-background holder; the door shuts; the scan; the pattern, badged computed, not measured. |
| 5 | 1:18 | [59:35-59:55](https://youtu.be/79FL6mTFSsI?t=3575) | Instron 68FM-100 · 3119-608 environmental chamber · AVE 2 video extensometer | A bar into the lower grip; the chamber cut away; the pull, its curve labelled illustrative; broken. |
| 6 | 1:38 | [1:04:23-1:04:39](https://youtu.be/79FL6mTFSsI?t=3863) | LECO PX500 grinder-polisher and its magazine of pre-loaded discs | The arm takes the 320-grit disc from the magazine onto the magnetic platen; the pistons press the mounts down. |
| 7 | 1:53 | [1:06:46-1:07:04](https://youtu.be/79FL6mTFSsI?t=4006) | Hitachi TM4000PlusII tabletop SEM · Oxford Instruments AZtecOne EDS | The conductive mount goes into the SEM's grounded holder cup; pump-down; a BSE image, badged illustrative. |
| 8 | 2:10 | [1:28:17-1:28:43](https://youtu.be/79FL6mTFSsI?t=5297) | Two 30 ft Kardex Shuttle XP 500s with 19 trays, the floor machines and two UR12e arms on MiR250s | Week by week, then month by month, to the first year's totals, then the long-form's own "first year" card. |

The arm in shots 1 and 3-7 is a UR12e on a MiR250, named at the right of each caption. Shot 5 is the chapter Sterling
called "machining and tensile": the wire EDM's cut comes earlier in the same chapter (about 56:35 in the long-form).
Shot 3 shows the sieving; the Aconity MIDI is loaded and prints at 50:00-50:43.

### What the cut changes, and what it keeps

- **The picture is the long-form's**, with its title bar, status panel and step counter, at the speed it was played
  there. Shot 8 is the long-form's own time-lapse, so the speed it states on screen still holds.
- **The captions:** each shot covers the long-form's caption band with a band in the same style. It gives the chapter,
  the instruments in the shot and, at the right, the arm. The long-form's sentence would be cut off mid-step. That band
  is two to four lines tall, so `bandscan` measures the highest it reaches in each shot (6 frames a second), and the new
  band covers that height for the whole shot: 78 px in four shots, 102 px in three, 126 px in shot 2. It comes off for
  the "first year" card, which has no band.
- **No sound.** The narration's lines don't start and stop with the shots, so it is left out.
- **Joins:** 0.5 s dissolves. A title card and an end card in the long-form's card style (`longform.card_image`); the
  end card points to the full video and to PR #318.
- **The stills** are the cut's own frames with their caption band, taken from the near-lossless window rather than
  from the final MP4, so they are compressed once (by YouTube), not twice.

### Rebuilding it

With `highlight.py` as it was at d349073 (the file now builds the 2026-11-28 edition):

```bash
cd vertical-lab
ssh -D 127.0.0.1:1080 -N -f "$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME"   # or any lab Pi this run can reach
pip install "yt-dlp[default]"                                         # node is the JS runtime here
python3 highlight.py fetch                     # into $HIGHLIGHT_CACHE (default /tmp/vertical_lab_highlight)
python3 highlight.py bandscan                  # each shot's band_top should cover the long-form's band
python3 highlight.py build                     # out/highlight/
python3 highlight.py upload                    # unlisted; refuses a file already uploaded
```

A shot's times are its `t0`/`t1` in `SHOTS`, in long-form seconds; `still` picks its still.
