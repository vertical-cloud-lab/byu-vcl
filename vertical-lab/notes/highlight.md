# A 2-3 minute highlight of round 15's long-form

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

## Where it comes from

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

## The shots

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

## What the cut changes, and what it keeps

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

## Rebuilding it

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
