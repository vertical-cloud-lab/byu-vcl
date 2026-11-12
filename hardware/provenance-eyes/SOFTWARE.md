# Provenance Eyes: software build-out path

What the headset has to do ([#342](https://github.com/vertical-cloud-lab/byu-vcl/issues/342)):
press the button and it records what the wearer sees and hears. Press it again and the
recording stops and uploads to YouTube. Stopping also puts the transcript, an analysis of the
video and its conclusions on GitHub, with nobody touching a computer.

This is a plan, not code that has run. Every command below needs checking on the first bench
build (phase 0). Facts were checked on 2026-11-12 and are linked where they matter.

## The pipeline

```
 HEADSET (Pi Zero 2 W)                         GITHUB (private data repo)
 ─────────────────────                         ──────────────────────────
 button ─► recorder.service                    release "rec-<device>-<UTC>" published
            rpicam-vid + stereo I2S mics             │
            → <id>.mkv  + <id>.json sidecar          ▼
 button ─► stop, buzz twice                     provenance.yml (Actions)
            │                                    1. download audio + frames
            ▼                                    2. faster-whisper → transcript.vtt / .md
 uploader.service (when on Wi-Fi)                3. Claude: transcript + frames
   1. remux to MP4, SHA-256                         → analysis.md, conclusions.md
   2. YouTube upload (yt_service.py) ─► video ID  4. commit recordings/<date>/<id>/
   3. extract audio + keyframes                   5. release notes, issue comment,
   4. create GitHub release with the bundle  ──►     MongoDB metadata
```

Three design rules hold it together:

- **The original file is the record.** The Pi hashes it before anything else touches it, and the
  hash goes in every downstream file. YouTube re-encodes everything, so a YouTube copy is not
  the original.
- **Nothing downloads from YouTube on a runner.** GitHub's runners are refused YouTube's player
  ("Sign in to confirm you're not a bot"; see `CLAUDE.md`). So the headset sends the analysis
  its own copy of the audio and frames, a few MB, instead of a YouTube link.
- **Secrets live on GitHub, not on the head.** The headset holds only an upload-only YouTube token
  and a GitHub token for one private repo. A lost headset costs two revocations. The Claude
  credential stays in Actions.

## Phase 0: bench prototype (a day or two)

Get the parts working on a desk before anything is printed: the Zero 2 W, the camera, both mics,
the button and the PiSugar.

1. **Raspberry Pi OS Lite, 64-bit.** Join Wi-Fi and Tailscale with the device tag, as the other
   lab Pis are (see `CLAUDE.md`). SSH and `journalctl` over the tailnet are the "backdoor" for
   logs. Remember that the tailnet grants only `tcp:22`, so bind any service to `127.0.0.1`.
2. **Microphones.** Adafruit's current guide uses one overlay line in `/boot/firmware/config.txt`:
   `dtoverlay=googlevoicehat-soundcard`. Wire BCLK to GPIO18, LRCL to GPIO19 and DOUT to GPIO20,
   with one mic's SEL to ground and the other's to 3.3 V for stereo. The rate is fixed at 48 kHz
   ([guide](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-test)).
   Test with `arecord -D plughw:1 -c2 -r 48000 -f S32_LE -t wav -V stereo -v test.wav`. The guide
   names Bookworm and Bullseye; check it on Trixie.
3. **Camera and audio together.** `rpicam-vid` records audio itself when the libav backend is used
   ([docs](https://www.raspberrypi.com/documentation/computers/camera_software.html); `--audio-source`
   accepts `pulse` or `alsa`, per the [source](https://raw.githubusercontent.com/raspberrypi/rpicam-apps/main/core/video_options.hpp)):

   ```bash
   rpicam-vid -t 0 --width 1920 --height 1080 --framerate 30 \
     --codec libav --libav-audio \
     --audio-source alsa --audio-device <name from `arecord -L`> \
     --audio-channels 2 --audio-samplerate 48000 --audio-bitrate 128000 \
     --bitrate 8000000 --intra 150 --autofocus-mode continuous \
     -o test.mkv
   ```

   - **The encoder.** On the Zero 2 W, libav's default video codec is `h264_v4l2m2m`, the
     hardware encoder.
   - **The container.** The `.mkv` extension picks it (`--libav-format` overrides). Use MKV
     rather than MP4, so a flat battery doesn't lose the whole file.
     MP4 is unreadable until its index is written at the end; MKV is readable up to the last
     cluster.
   - **The bitrates.** `--audio-bitrate` defaults to 32 kb/s, which is too low for stereo, hence
     128000. `--intra 150` puts a keyframe every 5 s, which phase 2 uses.
4. **Measure, don't assume:**
   - CPU use, SoC temperature, and dropped frames at 1080p30. Drop to 720p30 if it can't keep up.
   - Lip sync, from a clap at the start. `--av-sync` adjusts it.
   - Current at the battery, which sets run time.
   - The temperature of the front enclosure where it touches the band.

## Phase 1: the recorder service

`recorder.py`, run by `systemd` with `Restart=on-failure`, logs to the journal.

| Gesture | Action | Feedback |
| --- | --- | --- |
| Single press | Start recording; press again to stop | LED on while recording; one buzz to start, two to stop |
| Double press | **Bookmark**: append `{t, utc}` to the sidecar | Short buzz |
| Hold 3 s | Stop if recording, then a clean `shutdown` | Long buzz |

- **Reading the button.** Use [`gpiozero`](https://gpiozero.readthedocs.io/) `Button`
  (`when_pressed`, `hold_time=3`); a small timer separates single presses from double ones. The
  record button is on a GPIO pin, not the PiSugar's own button. That one is at the back of the
  head and long-press on it is the hardware power-off.
- **Stopping cleanly.** Start `rpicam-vid` as a subprocess and stop it with `SIGINT`, so the
  container is closed properly.
- **The sidecar, `<id>.json`.** It records:
  - the device ID, the wearer (set per session), and the start and stop times in UTC
  - the bookmarks, and battery and temperature samples every 30 s
  - the software versions
  - the tail of `rpicam-vid`'s log

  The PiSugar's clock keeps the times right offline.
- **Naming.** Use `<device>-<UTC start, YYYYmmddTHHMMSSZ>`, so names sort and never collide.
- **A spoken tag.** Ask wearers to say the experiment or issue at the start, for example "this is
  for issue 231". Phase 4 picks it up from the transcript.

## Phase 2: upload when the clip ends

`uploader.py` runs as a second service. It takes finished recordings off a queue on disk, so it
survives reboots and no-Wi-Fi stretches. To spare the battery, it can wait until the headset is
charging; the PiSugar reports this over I2C.

1. **Remux and hash.** `ffmpeg -i <id>.mkv -c copy -movflags +faststart <id>.mp4` remuxes in
   seconds, with no re-encode. Then compute the SHA-256.
2. **YouTube.** Use the lab's existing helper with the upload-only token
   (`YOUTUBE_UPLOAD_TOKEN_PICKLE_B64`; [`youtube/README.md`](../../youtube/README.md)):

   ```python
   from youtube.yt_service import upload_video
   video_id = upload_video(mp4, title=f"Provenance {rec_id}",
                           description=f"sha256 {digest}\nsidecar: {sidecar_url}",
                           privacy="unlisted")
   ```

   **Always pass `privacy`.** Since 2 November 2026, uploads from unverified API projects are no
   longer forced to private, and an upload with no `privacyStatus` now defaults to **public**
   ([revision history](https://developers.google.com/youtube/v3/revision_history)). The helper
   already defaults to `private`. This also makes the line in `youtube/README.md` about uploads
   being "locked private anyway" out of date. Uploads now have their own quota, 100 a day by
   default ([quota](https://developers.google.com/youtube/v3/determine_quota_cost)).
3. **The analysis bundle**, a few MB:
   - **Audio:** `ffmpeg -i <id>.mkv -vn -ac 1 -ar 16000 -c:a flac audio.flac`.
   - **Keyframes:** `ffmpeg -skip_frame nokey -i <id>.mkv -fps_mode vfr -vf scale=768:-2 -q:v 4 frames/%05d.jpg`.
     This decodes only the keyframes, one every 5 s, which a Zero can afford.
   - **Add bookmarked frames** by seeking to each bookmark.
   - **The sidecar** with the `video_id` and hash added.
4. **The GitHub release.** Create it on a **private** data repo (suggested name
   `vertical-cloud-lab/provenance-eyes-data`; this repo is public). Tag it `rec-<id>` and attach
   the bundle as assets. Assets stay out of git history and can be up to 2 GB each.
   - The headset's token is a fine-grained PAT with *Contents: write* on that one repo only.
   - A release published with a PAT, unlike one made with `GITHUB_TOKEN`, starts workflows.
5. **Keep the original** on the card until it has been copied to lab storage. That could be a NAS
   share mounted from a lab Pi, or Box once a link exists. Then delete it.

## Phase 3: transcription on Actions

A workflow in the data repo, `on: release: types: [published]`:

```yaml
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions: { contents: write, issues: write, id-token: write }
    steps:
      - uses: actions/checkout@v4
      - run: gh release download "${{ github.event.release.tag_name }}" -D bundle
        env: { GH_TOKEN: "${{ github.token }}" }
      - run: pip install faster-whisper
      - run: python scripts/transcribe.py bundle/audio.flac --model small.en --out bundle/
      # step 4 (Claude) and step 5 (commit) follow
```

- **The script.** `transcribe.py` runs [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
  with `compute_type="int8"` and word timestamps.
- **The outputs.** It writes `transcript.vtt`, and `transcript.md` with one line per segment,
  each linked to `https://youtu.be/<id>?t=<seconds>`.
- **Speed.** The README times `small` on 13 minutes of audio at 1 min 42 s with int8, on an
  8-thread desktop CPU. A 4-vCPU runner is likely 2–4 times slower, so allow 3–7 minutes per
  13 minutes of audio; time it on the first run. Move up to `medium.en` if the lab vocabulary
  (reagent names, instrument names) needs it.

## Phase 4: analysis and conclusions with Claude

Two ways to run the same step:

- **`anthropics/claude-code-action@v1`, recommended to start.** It is the action this repo's
  `claude.yml` already uses, with the `CLAUDE_CODE_OAUTH_TOKEN` the lab already has, so it needs no
  new secret. Give it a fixed `prompt:`:
  - read `bundle/transcript.md`, the sidecar and the keyframes, which it can view as images
  - write `analysis.md`: a timeline with YouTube timestamp links, the materials and instruments
    seen, the steps as performed, deviations, safety observations, and open questions
  - write `conclusions.md`
  - find any issue number the wearer said, and comment there with a short summary and links

  It runs inside the job, so it can read the repo's own context as it works, such as earlier
  recordings and SOPs.
- **The Messages API, for a fixed, cheaper call.** Use the official `anthropic` Python SDK and
  `claude-opus-5-5`. Send one request with the transcript and the frames as image blocks, and get
  structured JSON back. It needs a new `ANTHROPIC_API_KEY` secret. The cost estimate is in
  [`BOM.md`](BOM.md#running-costs), about $0.25 per 30-minute recording.

Then commit to `recordings/YYYY/MM/DD/<id>/`:

| File | Content |
| --- | --- |
| `README.md` | Title, YouTube link, wearer, times, hash, bookmarks, a summary, and links to the rest |
| `transcript.vtt`, `transcript.md` | Timestamped transcript |
| `analysis.md`, `conclusions.md` | Claude's output, marked as machine-written |
| `sidecar.json` | The headset's metadata and log tail |

- **Release notes.** The workflow copies the summary into the release notes, so each recording
  has one page that links everything.
- **MongoDB.** It also writes one metadata document (ID, times, hash, `video_id`, paths and issue
  links) to `digital-wetlab`, in a new collection such as `provenance-recordings`. Metadata only:
  the free tier's 512 MB cap rules out video.

**Who adds the workflow:** the Claude GitHub App can't write `.github/workflows/`. Whoever creates
the data repo adds this file, along with the `CLAUDE_CODE_OAUTH_TOKEN` and `MONGODB_URI`
secrets.

## Phase 5: hardening

- **Uploads that can't lose data.** Retry with back-off, make every step resumable, and keep the
  queue state in the sidecar.
- **A health check.** The uploader can publish a small status (battery, free space, queue length,
  last error) to MQTT on `status/provenance-eyes/<device>`, following the lab's topic scheme. A
  dashboard can then show which headset needs charging.
- **Several headsets and wearers.** Give each headset a device ID. Set the wearer per session,
  with a QR code shown to the camera or a CLI over SSH.
- **Tests.** Simulate the button presses and the upload queue with a fake `rpicam-vid`, and run
  them in CI on the data repo.
- **Privacy.** Wearers tell people they are recording, and the LED is visible to others.
  Uploads are unlisted or private, and transcripts stay private. Get IRB guidance before
  recordings are used as research data about people.

## Phase 6: later

- **Live view.** Stream to YouTube while recording, through the stream cams' streamingLambda RTMP
  path ([`docs/stream-cams.md`](../../docs/stream-cams.md)). Keep the local recording as the
  record, since Wi-Fi drops while walking around.
- **Spoken bookmarks.** Run a small on-device keyword spotter for "mark", or find "mark" in the
  transcript afterwards.
- **Captions on YouTube.** `captions.insert` needs the `youtube.force-ssl` scope
  ([docs](https://developers.google.com/youtube/v3/docs/captions/insert)), which only the
  approval-gated full token has. So captions would be pushed by an `@claude-youtube` run, not by
  the headset.
- **Transcribing on the headset**, if the network is unreliable. That means a Pi 5 and its weight
  and heat; see [`BOM.md`](BOM.md#options).

## Order of work

| Phase | Gives you | Rough effort |
| --- | --- | --- |
| 0 | Proof that the parts record good stereo video together | 1–2 days |
| 1 | A button that records to the card | 1–2 days |
| 2 | Clips on YouTube, and the bundle on GitHub | 2–3 days |
| 3 + 4 | Transcript, analysis and conclusions committed automatically | 2–3 days |
| 5 | Something people can wear every day | ongoing |

Phases 2–4 don't need the headset: they can be built and tested with any MKV recorded on a desk.
