# A highlight of round 15's long-form

Sterling, 2026-11-25 (PR #318): "Cut a 2 to 3 minute highlight of round 15's long-form: one shot from each chapter of
the alloy route (charge, atomize, sieve and print, powder checks, machining and tensile, sample prep,
characterization), then the whole lab at speed, with short captions naming each instrument. Upload it unlisted, and
commit 8 full-resolution stills, one per chapter, as PNGs on the branch."

- **The cut:** [Br2IlDjcysY](https://www.youtube.com/watch?v=Br2IlDjcysY), unlisted, 2:49, 1280 × 720 at 30 fps,
  silent, with YouTube chapters. The MP4 is `out/highlight/vertical_lab_highlight.mp4` (22.9 MB).
- **The stills:** `out/highlight/01_charge.png` to `08_whole_lab.png`, 1280 × 720, the long-form's own resolution.
  `out/highlight/sheet.jpg` puts them on one page.
- **The record:** `out/highlight/highlight.json`, every shot's place in the long-form, its band height, the still's
  frame, the MP4's sha256 and the upload.
- **The code:** `highlight.py` (`fetch`, build, `sheet`, `upload`).

## The shots

The title card, then one shot per chapter, 17 s each (16.6-17.6 s), then 37 s of the finale, then a card pointing
to the full video. Each shot is a continuous stretch of the long-form, cut clear of the clips' half-second dissolves.

| # | Chapter | In the long-form | Caption: the instruments in view |
|---|---|---|---|
| 1 | Charge | 19:26-19:43 | Multi-doser (powder-doser's chain carousel v5) over an A&D HR-202i; Specac Atlas Autotouch vacuum press. Tray B at the opening, the arm feeding the Al cups to the doser (shown faster in the clip) |
| 2 | Atomize | 28:13-28:30 | AMAZEMET rePowder ultrasonic atomizer, both MiR250 + UR12e units on the plate's landing stage (ours). The spray in cutaway, then the lab's own Oct 27 bronze jet beside the model (badged REAL FOOTAGE) |
| 3 | Sieve and print | 47:10-47:27 | Retsch AS 200 sieve shaker: the stack clamped and shaken, then what stays on each sieve |
| 4 | Powder checks | 53:14-53:31 | Malvern Mastersizer 3000 + Aero S, laser diffraction in cutaway, with the size distribution (SEM count of the lab's Al 4047 measured, the laser result computed) |
| 5 | Machining and tensile | 1:00:21-1:00:38 | Instron 68FM-100 with a 3119-608 chamber: a bar cut on the wire EDM and heat treated, pulled at 200 °C (illustrative curve) |
| 6 | Sample prep | 1:04:22-1:04:39 | LECO PX500: the arm sets a pre-loaded 320-grit disc from the magazine (ours) on the magnetic platen; the pistons press the mounts |
| 7 | Characterization | 1:06:55-1:07:12 | Hitachi TM4000PlusII SEM with Oxford AZtecOne EDS: BSE image and EDS maps (illustrative; the inset is the lab's own powder) |
| 8 | The whole lab at speed | 1:28:08-1:28:38, then 1:28:39-1:28:46 | Week by week and month by month, then the first year's card: 360 alloys atomized, 309 printed and fully tested, by the schedule model |

Chapter 5 is the pull rather than the wire EDM's cut (56:28 in the long-form): one shot per chapter allowed only one,
and the pull is the route's end. The caption says the bar was cut on the EDM. Chapter 3's shot is the sieving; the
MIDI's print (50:21) is a dark cutaway that reads poorly at this length.

## Where the frames come from

Round 15 drew its clips into `out/r15/`, which is git-ignored and went with that run's runner. Only chapter 2's 720p
MP4 was committed, and the 1:28:55 join never was (too big for git). So the one copy of round 15's frames is the
long-form on YouTube, [79FL6mTFSsI](https://www.youtube.com/watch?v=79FL6mTFSsI).

- **The stream:** its 720p H.264 HLS stream, itag 232, about 2.5 Mbit/s, the highest-rate 720p YouTube serves. Its
  5.333 s segments carry the long-form's own timestamps (plus one frame), so a shot is cut at the long-form's own times.
- **What was fetched:** only the 39 segments that cover the shots, 21 MB.
- **The route:** YouTube refuses to play to a GitHub runner (CLAUDE.md), so the fetch went through an SSH SOCKS
  tunnel to the CubXL Pi (exit network BYU), rate-capped at 3 MB/s. The Pi only relayed: nothing was installed or
  written on it.
- **Choosing the shots:** a 360p copy (97 MB) was fetched the same way, for contact sheets of every chapter. It isn't
  kept.

So each frame has been through two encodes: round 15's and YouTube's. At 2.5 Mbit/s for clean 3-D that shows as a
little softness on fine text, nothing worse. A sharper cut would need the shots re-rendered from round 15's code.

## The captions

- **The band:** each clip's own caption band (one to four lines, which a 17 s shot would cut mid-sentence) is covered
  by a band in the same style. It carries the chapter in a blue tab, the instruments in view in bold and one line of
  what they are doing.
- **Its height:** at least two lines (77 px), and taller wherever a clip's own band was taller somewhere in that shot.
  The script finds the clip's band by its 2 px blue top rule in a frame every 0.25 s, so none of the old text shows.
- **What isn't covered:** everything else is the long-form's own: the title bar, the status panel, the labels, the
  data panels and their REAL / COMPUTED / ILLUSTRATIVE badges.
- **The year card:** the finale's last piece is a full-frame card with its own text, so no band goes over it.
- **The stills:** each is the decoded frame under the same band, written once as PNG, so it has had no third encode.
- **Sound:** none. The long-form's narration is cut to its lines and wouldn't survive 17 s shots, so the cut is
  silent and the end card points to the narrated version.

## Rebuilding

```bash
cd vertical-lab
pip install yt-dlp pillow numpy            # and ffmpeg, curl, node (yt-dlp's JS runtime)
ssh -o ExitOnForwardFailure=yes -D 127.0.0.1:1080 -N -f "$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME"
HIGHLIGHT_PROXY=socks5://127.0.0.1:1080 python3 highlight.py fetch     # 39 segments into /tmp/highlight_hls
python3 highlight.py                      # the MP4, the 8 stills, highlight.json (about 1.5 min on 4 cores)
python3 highlight.py sheet                # out/highlight/sheet.jpg
python3 highlight.py upload               # unlisted; skipped if this MP4 is already up
```

To change a shot, edit its `t0`, `t1` or `still` in `SHOTS` (long-form seconds; `out/longform.json` has where each
clip starts) and run `fetch` again for any new segments.
