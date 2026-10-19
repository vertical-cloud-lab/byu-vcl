# The lid camera's YouTube live stream

Set up 2026-10-18 ([#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234)). The HQ Camera
on the lid mount streams to the *BYU VCL Hardware Streams* channel. Since 2026-10-19 it has its
own playlist, [OT2 overhead Livestreams Playlist](https://www.youtube.com/playlist?list=PLM4VC4X_7XKQ)
(`PLM4VC4X_7XKQ`), at 1920 × 1440 and 3 fps. Before that it went into the
[OT-2 Livestreams Playlist](https://www.youtube.com/playlist?list=PLdKz1vXA-rfQ) (`PLdKz1vXA-rfQ`),
the one the OT-2-LCM Hugging Face Space embeds, at 1536 × 1152 and 10 fps. Each broadcast is
titled *OT2 overhead stream hqcam-ot2-lid, <date> UTC <time>*; the playlist is the stable link,
since every restart makes a new video.

It runs the same client as the other stream cams, the Acceleration Consortium
[picam `device.py`](https://ac-training-lab.readthedocs.io/en/latest/devices/picam.html)
(`rpicam-vid` piped into `ffmpeg`, which pushes RTMP to a broadcast the lab's
[streaming Lambda](https://github.com/vertical-cloud-lab/streamingLambda) creates), with the same
watchdog. What differs is the Pi: this is the Pi 5 behind `RPI_STREAM_CAM_HOSTNAME`, which is
also the OT-2's only link and where jobs that drive the robot run. So the stream is niced, and the
Pi's scheduled reboot waits while the robot or the camera is in use ([Reboots](#reboots)). The
general notes on the stream cams are in `docs/stream-cams.md` on `main`.

## Files here

| File | Goes to | What |
| --- | --- | --- |
| `device.py` | `~/ac-training-lab/src/ac_training_lab/picam/device.py` | The atomizer cam's patched `device.py` (upstream `87a3ccb` plus `SENSOR_MODE`, `--flush`, `-r`, pixelation) plus optional settings for this Pi: `RESOLUTION = "WIDTHxHEIGHT"`, `CAMERA_CODEC`, `BITRATE`, `X264_PRESET`, `MAX_BITRATE`. See [What changed in `device.py`](#what-changed-in-devicepy) |
| `my_secrets_example.py` | `…/picam/my_secrets.py`, mode 600 | Every setting, with the Lambda URL left blank |
| `device.service.in` | `/etc/systemd/system/device.service` | The service, with `Nice=5` added. `install.sh` fills in the user and home |
| `stream-watchdog.sh`, `.service`, `.timer` | `/usr/local/bin`, `/etc/systemd/system` | The same watchdog as the other stream cams: restarts the service after 3 minutes with no RTMP bytes acknowledged, or when systemd has given up, at most 6 times in 24 h |
| `stream-reboot.sh`, `.service`, `.timer` | `/usr/local/bin`, `/etc/systemd/system` | Reboots the Pi at 05:00, 13:00 and 21:00 local, as the other stream cams do, so no broadcast runs past YouTube's 12 h archive limit. Waits while the OT-2 or the camera is in use; see [Reboots](#reboots). Until 2026-10-19 this was `stream-rotate`, which restarted only `device.service` |
| `stream-reboot-inhibit.rules` | `/etc/polkit-1/rules.d/50-stream-reboot-inhibit.rules` | Lets the Pi's user hold the reboot off for a long job with `systemd-inhibit`, over SSH and without sudo |
| `no-ipv4-acd.conf`, `wifi-powersave-off.conf` | `/etc/NetworkManager/conf.d/` | The two fixes the other stream cams carry. This Pi had logged 21 campus ARP conflicts (`conflict detected … with host 00:00:00:00:00:00`), the start of the outage described in [streamingLambda#9](https://github.com/vertical-cloud-lab/streamingLambda/issues/9) |
| `install.sh` | | Does all of the above on a fresh Pi, with the sudo password on stdin |

## Settings

| Setting | Value | Why |
| --- | --- | --- |
| `CAM_NAME` | `"hqcam-ot2-lid"` | `picam-ot2` is the Zero 2 W that now watches the atomizer room |
| `WORKFLOW_NAME` | `"OT2 overhead"` | Since 2026-10-19 (was `"OT-2"`). No playlist title contained it, so at the first start the Lambda created *OT2 overhead Livestreams Playlist* (`PLM4VC4X_7XKQ`, public), and it files every later broadcast there. The Lambda matches the name as a case-insensitive substring of titles, hence no hyphen: with `OT-2` in these titles, any camera started as `OT-2` would end this broadcast, and could file into this playlist. As it is, `end` leaves *atomizer stream picam-ot2* and *powder doser stream picam-d1pr* alone, and their restarts leave this one alone |
| `PRIVACY_STATUS` | `"public"` | As asked in #234 |
| `RESOLUTION` | `"1920x1440"` | Since 2026-10-19 (was `"1536x1152"`). 4:3, the sensor's shape, so the whole sensor: read from the camera on 2026-10-18, a 4:3 output uses `ScalerCrop (2, 0)/4052x3040`, while `1280x720` uses `(0, 380)/4056x2280`, which at 8 mm zoom cuts off the front and back rows of slots (the crop [`preview_server.py`](../preview_server.py) also avoids). 1440 lines is the most that comes back out of YouTube for this stream: the Lambda creates every broadcast at Low latency, which YouTube [does not offer at 4K](https://support.google.com/youtube/answer/7444635), and a 2880 × 2160 test stream was served live at 1440 × 1080 at most, with 1920 × 1440 at the top of its archive. See [the 2026-10-19 record](#change-record-2026-10-19) |
| `FRAME_RATE` | `3` | Since 2026-10-19 (was `10`). The deck changes slowly; 3 fps leaves room for the larger frame |
| `SENSOR_MODE` | `"2028:1520"` | The IMX477's full-field binned mode, `(0, 0)/4056x3040`, which the ISP scales to the output. Up to 2028 wide it is the one to use: binning halves the noise. A 2880 × 2160 output needs `"4056:3040"`, the full-resolution mode (up to 11.7 fps) |
| `CAMERA_CODEC` | `"yuv420"` | The Pi 5 has no hardware H.264 encoder: `--codec h264` goes through libav in software, so the stream would be encoded twice (once at the camera's bit rate, once by ffmpeg for the overlay). Raw frames to ffmpeg mean one encode and no intermediate bit rate. 1920×1440 at 3 fps is 12 MB/s through the pipe, nothing for a Pi 5. The raw path needed three fixes on 2026-10-19; see [What changed in `device.py`](#what-changed-in-devicepy) |
| `TIMESTAMP_OVERLAY` | `True` | Lab local time top left, as on the other cams; it is the clock for reading archives back |
| `CAMERA_VFLIP` / `HFLIP` / `ROTATION` | `False` / `False` / `0` | Not yet checked against the deck. If the picture is upside down, set both flips `True` (free, in the sensor) and restart once |
| `PIXELATE_BLOCKS` | `None` | Sharp. The camera looks straight down at the deck through the window |
| `BITRATE` | `4000000` | Only used with `CAMERA_CODEC = "h264"` |
| `X264_PRESET` | `"veryfast"` | New 2026-10-19. ffmpeg's libx264 preset; the default, and what every other picam runs, is `"ultrafast"`. On this Pi, on a detailed test scene at 2880 × 2160 and 3 fps, `veryfast` needed 7.9 Mbit/s where `ultrafast` needed 16.4, for 1.0 core instead of 0.7 |
| `MAX_BITRATE` | `4000000` | New 2026-10-19. Caps ffmpeg's encode at 4 Mbit/s (`-maxrate`, 2 s `-bufsize`). Uncapped, libx264 encodes at constant quality, and a dark picture at high gain is mostly noise, which it spends bits on |

## Operating it

All of this is over Tailscale SSH as `RPI_STREAM_CAM_USERNAME`; `sudo` wants
`RPI_STREAM_CAM_PASSWORD` on stdin.

**Read the state without printing the stream key.** `systemctl status` and the journal's
`Streaming to:` and `create` lines contain the RTMP URL with the key in it.

```bash
systemctl show device.service -p ActiveState -p SubState -p NRestarts -p ActiveEnterTimestamp
journalctl -u device.service -n 50 --no-pager | sed -E 's#rtmps?://[^ ]*#RTMP#g; s#live2/[A-Za-z0-9_-]+#live2/<key>#g'
ss -Htin state established '( dport = :1935 )' | grep -oE 'bytes_acked:[0-9]+'   # climbing = YouTube is receiving
journalctl -t stream-watchdog -n 20 --no-pager
```

**Change a setting.** Edit the line in `my_secrets.py`, then restart once. A restart ends the
broadcast and creates a new one with a new video ID; the stream is off the air for about
30 s. `device.service` allows 3 starts an hour (`systemctl reset-failed device.service` clears
the count).

```bash
cd ~/ac-training-lab/src/ac_training_lab/picam && sed -i 's/^CAMERA_VFLIP = .*/CAMERA_VFLIP = True/' my_secrets.py
sudo -S -p '' systemctl restart device.service <<< "$RPI_STREAM_CAM_PASSWORD"
```

**Take a full-resolution still.** The stream holds the camera, so stop it first, then start it
again (which makes a new broadcast). The watchdog leaves a stopped unit alone; it only acts on
a failed or stalled one.

```bash
sudo -S -p '' systemctl stop device.service <<< "$RPI_STREAM_CAM_PASSWORD"
rpicam-still -n -t 3000 -o still.jpg
sudo -S -p '' systemctl start device.service <<< "$RPI_STREAM_CAM_PASSWORD"
```

**Stop it for a while.** `systemctl stop device.service` stops it until the next reboot (05:00,
13:00 or 21:00 local), which starts it again. To keep it off through reboots, use
`systemctl disable --now device.service`, and `enable --now` to bring it back.

**Playlist.** The Lambda adds each broadcast to the first playlist whose title contains
`OT2 overhead`, now *OT2 overhead Livestreams Playlist*. If that playlist is renamed or deleted,
the Lambda creates a new one under the same name at the next start, with a new ID. The first
broadcast under a new name can miss its brand-new playlist: on 2026-10-19 the Lambda created it
and then got `HTTP 409 … SERVICE_UNAVAILABLE` adding the broadcast to it, so the service was
restarted once more. The journal's `create` response has `playlist_add_status`, `added` when
it worked.

**Moving the stream back into the OT-2 playlist** (for the Hugging Face Space, say) means
`WORKFLOW_NAME = "OT-2"` again, and ending the `OT2 overhead` broadcast by hand first, because
on start the device only ends broadcasts that match its new name:
`venv/bin/python -c "from device import call_lambda; call_lambda('end', 'hqcam-ot2-lid', 'OT2 overhead')"`.

## Reboots

`stream-reboot.timer` reboots the Pi at 05:00, 13:00 and 21:00 local time (America/Boise, so
11:00, 19:00 and 03:00 UTC while daylight saving lasts, an hour later in winter), the slots the
other stream cams reboot in. Every boot starts a fresh broadcast, so none runs past YouTube's
12 h archive limit, and the Pi starts clean. Each reboot takes the stream, the Pi's tailnet
connection and the OT-2's link down for under a minute: on the test reboot the Pi was back on
the tailnet and the OT-2 answering 31 s after the trigger, and YouTube was receiving the new
broadcast after 50 s ([record](#reboots-set-up-2026-10-19)).

Until 2026-10-19 this Pi only restarted the stream, to spare CubOS and the OT-2 link. Neither
reason holds now. The CubXL hardware is on its own Pi; `cubos.service` still runs here, with
nothing attached. The OT-2's USB-Ethernet adapter is in a black USB 2.0 port (`1-2`,
480 Mbit/s), not the USB 3 port where it failed to come up after the cold boot of 2026-09-25
([`wireless-color-sensor/ot2/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b31a75d/wireless-color-sensor/ot2/README.md?plain=1#L110-L147)
on `main`).

Jobs that drive the OT-2 run on this Pi, so `stream-reboot.sh` checks first, and waits while

| It waits while | Seen as |
| --- | --- |
| something here is moving the robot | the OT-2 has a maintenance run. `ot2ctl.py` and the scan scripts hold one from start to finish |
| a protocol is running on the robot | the robot's current run is anything but `idle`, `succeeded`, `failed` or `stopped` |
| someone is previewing or taking stills | `device.service` is stopped and something holds `/dev/media*` or `/dev/video*` |
| any other job asked it to | a `systemd-inhibit` shutdown lock is held |

It checks again every 10 min. After 3 h it gives up on that slot: it restarts only the stream,
which still starts a fresh broadcast, and leaves the reboot to the next slot. A robot that doesn't
answer is nothing to wait for. A slot less than an hour after boot is skipped. A Pi 5 without an
RTC battery boots with the clock it had at shutdown, so after a long power cut the first NTP
correction would otherwise make a slot that passed while it was off fire at once.

**Keep the Pi up through a long job** (a download, or anything else that doesn't hold a
maintenance run) by starting it under a lock. The lock goes when the job ends, however it ends:

```bash
systemd-inhibit --what=shutdown --why="atomizer archive download" python3 fetch.py
```

`stream-reboot-inhibit.rules` lets the Pi's user take that lock over SSH without sudo; polkit
otherwise answers `Interactive authentication required`. A reboot run by hand as root ignores it.

**See what it would do, and what it did:**

```bash
sudo /usr/local/bin/stream-reboot.sh --check   # would reboot now / would hold off: … / would skip this slot
systemctl list-timers stream-reboot.timer
journalctl -t stream-reboot -n 20 --no-pager      # this boot only
cat /var/lib/stream-reboot/history               # every decision, across reboots
```

journald on this Pi is volatile (Raspberry Pi OS's `40-rpi-volatile-storage.conf`), so a
reboot wipes the journal, including the line that announced it. Hence the history file, which
keeps the last 300 lines. `uptime -s` gives the time of the last boot.

**No reboots for a while:** `sudo systemctl stop stream-reboot.timer` lasts until the next boot,
`disable --now` until it is enabled again. Without reboots, something else has to start a new
broadcast at least every 12 h.

## What changed in `device.py`

Optional settings, each backward compatible (a `my_secrets.py` without them behaves as
before), on top of the atomizer cam's version:

- `RESOLUTION` accepts `"WIDTHxHEIGHT"` as well as the 16:9 presets. Even numbers, at least 64.
- `CAMERA_CODEC = "yuv420"` sends raw frames and gives ffmpeg `-f rawvideo -pix_fmt yuv420p
  -video_size WxH -framerate N` for the pipe. ffmpeg then always encodes, even with no
  filters. Three things about those frames, all found on 2026-10-19 and all invisible while
  the picture was black:
  - **rpicam-vid's log stays out of the pipe.** The original `device.py` merged the camera's
    stderr into its stdout, so libcamera's start-up log (2,038 bytes, measured) sat in the
    pipe ahead of the first frame. That is harmless for H.264, whose parser skips to the next
    start code, but raw frames have no markers: every frame ffmpeg read was shifted by 2,038
    bytes, i.e. wrapped 502 px sideways at 1536 wide, with the colour planes shifted by
    different amounts. The camera's stderr now goes to the journal.
  - **Rows are padded to a multiple of 128 pixels,** not 64: measured frame sizes give a
    stride of 1536 for 1536, 2048 for 1984 and 2944 for 2880, with zeros in the padding.
    `device.py` reads the padded width and crops it off, so any even width works. ([Read at
    2880](../frames/2026-10-19/raw_2880_read_without_stride.jpg), a 2880-wide frame shears
    diagonally, with green lines where the padding lands.)
  - **They are full-range.** libcamera configures the stream as `YUV420/sYCC`: BT.601 matrix,
    levels 0–255. ffmpeg had been passing them on unconverted, which a player reads as
    limited range, crushing shadows and clipping highlights; on a test photo 9.0 % of pixels
    came out at 0 or 255, against 0.4 % in the photo. `device.py` now converts to
    limited-range BT.709 (`scale=in_range=pc:out_range=tv:…`, 13 % of a core at 2880 × 2160)
    and tags the output so, which brings that to 0.9 %.
- With `CAMERA_CODEC = "h264"` on a Pi without `/dev/video11` (no hardware encoder), it adds
  `--libav-format h264` and writes to `pipe:1`, because rpicam-vid's libav path does not
  understand `-o -` and otherwise writes nothing. `BITRATE` sets that encoder's bit rate (the
  1 Mbit/s default is too low for a 1152-line picture).

- `X264_PRESET` and `MAX_BITRATE` (2026-10-19) set ffmpeg's libx264 preset (default
  `ultrafast`, as before) and an optional `-maxrate`, with a 2 s `-bufsize`.

Both paths were tried on this Pi on 2026-10-18; the raw one is in use. The patch is worth
upstreaming to `ac-training-lab` with the rest of the lab's changes; the stderr fix applies to
any picam.

## Set-up record, 2026-10-18

Done from a `@claude` session on #234, over Tailscale SSH. `ffmpeg` was installed with apt (the
only package added); `~/ac-training-lab` is an upstream sparse checkout with `device.py` replaced
by this one; `requests` is in `…/picam/venv`. The Lambda URL was copied from the atomizer cam's
`my_secrets.py` straight into this Pi's over SSH, so it never passed through the session's
output. Nothing else on the Pi was changed; CubOS kept running throughout.

| | |
| --- | --- |
| Started | 2026-10-18 04:32:24 UTC. The Lambda's `end` found nothing to end; `create` returned the broadcast within 10 s and filed it in `PLdKz1vXA-rfQ` (`playlist_add_status: added`) |
| First broadcast | [`VUPZWQcTFWg`](https://www.youtube.com/watch?v=VUPZWQcTFWg), *OT-2 stream hqcam-ot2-lid, 2026-10-18 UTC 04:32*, public |
| Pipeline | `rpicam-vid --codec yuv420 --mode 2028:1520 1536x1152 @ 10 fps` → `ffmpeg -f rawvideo … libx264 ultrafast, -r 10 -g 20` → RTMP. ffmpeg logged `Input #1, rawvideo … 1536x1152, 10 tbr` and `Output #0 … 1536x1152, 10 fps` |
| Cost on the Pi 5 | ffmpeg about 18 % of one core, rpicam-vid negligible; 45 °C, `throttled=0x0`, load 0.16 with CubOS idle |
| Upload | 4.5 MB acknowledged by YouTube in the first 40 s (about 0.9 Mbit/s with the lab dark; expect more with the lights on) |
| Watchdog | no entries; the 180 s start-up grace applied |
| Picture | Black, with the OT-2's rail lights on or off, while the robot's own camera saw a lit deck. The lens is covered or stopped down again (see [`../README.md`](../README.md#2026-10-18-streaming-to-youtube)); nothing on the Pi's side. The flips are untested until it clears |

## Change record, 2026-10-19

Asked on [#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-6271826588):
its own playlist, marked as overhead; 3 fps; the highest resolution within reason. Done from a
`@claude` session over Tailscale SSH. `device.py` and `my_secrets.py` were backed up first, to
`~/device.py.bak-2026-10-19` and `~/my_secrets.py.bak-2026-10-19` (mode 600). Nothing was
installed. CubOS stayed active throughout, and the atomizer and powder-doser streams were not
touched.

| UTC | |
| --- | --- |
| 16:24 | `device.service` stopped; the last `OT-2` broadcast, `EnyPX1dX38g`, ended by hand through the Lambda. A full-resolution still was black (mean level 1 of 255): the lens is still covered or stopped down, or the camera is not on the mount |
| 16:24–16:34 | Off-air tests on the Pi, which found the three raw-path problems in [What changed in `device.py`](#what-changed-in-devicepy) and gave the figures below |
| 16:34 | Live as `OT2 overhead`, 2880 × 2160 from `4056:3040`: [`fJ5g69i3HPM`](https://www.youtube.com/watch?v=fJ5g69i3HPM). The Lambda created *OT2 overhead Livestreams Playlist* (`PLM4VC4X_7XKQ`), then failed to add the broadcast to it (HTTP 409, `SERVICE_UNAVAILABLE`). YouTube showed it as upcoming for 4.5 min before it went live |
| 16:39 | One restart to fill the playlist: [`uf8urr9T1lg`](https://www.youtube.com/watch?v=uf8urr9T1lg), `playlist_add_status: added`, live within about a minute |
| 16:43 | 1920 × 1440 from `2028:1520` (below): [`_4GnZiE6pug`](https://www.youtube.com/watch?v=_4GnZiE6pug), added to the playlist. Current until the test reboot at 16:50, after which the same settings came back as [`A2SwVZgreMA`](https://www.youtube.com/watch?v=A2SwVZgreMA); see [Reboots set up, 2026-10-19](#reboots-set-up-2026-10-19) |

**Why 1920 × 1440 and not 2160 lines.** The Lambda creates every broadcast with
`latencyPreference: "Low"`, and YouTube's latency page says of Low and Ultra-low latency alike:
"This setting does not support 4K resolution" ([source](https://support.google.com/youtube/answer/7444635)).
Live renditions stopped at 1440 × 1080 (format `270`) for both sizes, so 2160 lines bought live
viewers nothing, for twice the CPU and nearly three times the upload. The archives get more:
`fJ5g69i3HPM`'s tops out at 1920 × 1440 (format `271`), which a 1440-line stream also gives.
Measured live, over 60 s each, with the dark picture:

| | 2880 × 2160 from `4056:3040` | 1920 × 1440 from `2028:1520` |
| --- | --- | --- |
| ffmpeg CPU | 1.39 cores | 0.65 of a core |
| ffmpeg memory (RSS) | 830 MB | 390 MB |
| Upload to YouTube | 4.0 Mbit/s, held at the cap | 1.5 Mbit/s |
| SoC temperature | 52 °C | 48 °C |
| YouTube, live | up to 1440 × 1080 | up to 1440 × 1080 |
| YouTube, archive | up to 1920 × 1440 | — |

For 2160 lines live, the Lambda would have to create this camera's broadcasts at Normal latency
(`create_broadcast_and_bind_stream` in
[streamingLambda](https://github.com/vertical-cloud-lab/streamingLambda/blob/f6a4a8a/chalicelib/ytb_api_utils.py#L123),
which sets it for every camera; a per-camera field in the payload would keep the others as they
are). Then `RESOLUTION = "2880x2160"` and `SENSOR_MODE = "4056:3040"` here, about 1.4 cores and
4 Mbit/s.

**Encoder settings, tested off-air** on a detailed, lit scene (a photo of the OT-2 from
above, scaled to 2880 × 2160, as full-range frames with σ ≈ 1.7 levels of fresh luma noise
per frame), 30 s at 3 fps, every run with the range conversion and the timestamp:

| x264 preset | Cap | Upload | ffmpeg CPU |
| --- | --- | --- | --- |
| `ultrafast` | none | 16.4 Mbit/s | 0.66 of a core |
| `superfast` | none | 11.8 Mbit/s | 0.88 |
| `veryfast` | none | 7.9 Mbit/s | 1.02 |
| `veryfast` | 6 Mbit/s | 5.3 Mbit/s | 0.95 |
| `veryfast` | 4 Mbit/s | 3.1 Mbit/s | 0.91 |

**This Pi's supply sags at full load.** The kernel logged `Undervoltage detected!` at 16:30:04
and 16:31:55 UTC, during two of those off-air runs, which ran ffmpeg flat out on all four cores;
`vcgencmd get_throttled` has read `0x50000` (under-voltage and throttling have occurred) ever
since, against `0x0` at 16:21. There have been none since the stream went live. `EXT5V` read
4.85 V with the 2160-line stream running and 4.96 V at 1440. The official 27 W supply holds
about 5.1 V; check what this Pi is plugged into before giving it more work, and don't benchmark
on it flat out.

## Reboots set up, 2026-10-19

Asked on [#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-6271876140):
reboot after all, accepting a short loss of the OT-2 connection, now that CubXL runs on its own
Pi. Done from a `@claude` session over Tailscale SSH, at the same time as the change record
above; this session left `device.service` and `my_secrets.py` alone and waited for that one to
finish before rebooting.

| UTC | |
| --- | --- |
| 16:24–16:33 | Read-only first. No root or user crontab. `cubos.service` active since boot (9 days), with no requests logged and no USB serial device attached; the CubXL Arduino and CH340 are on the CubXL Pi. The OT-2's adapter on `1-2` at 480 Mbit/s, the robot answering, no maintenance run, no protocol run since July |
| 16:35 | `stream-reboot.*` installed, `stream-rotate.*` disabled and deleted. Next slot 13:00 MDT (19:00 UTC) |
| 16:36–16:45 | Checks without rebooting, below. The polkit rule went in after the first lock test failed with `Interactive authentication required` |
| 16:50:15 | Test reboot through the timer's own path, `systemctl start stream-reboot.service`, after `--check` said *would reboot now* |
| +9 s | Pi off the tailnet |
| +31 s | Back, with a new boot ID. The OT-2 answered `/health` with 200 at the first try: `eth1` on `1-2` at 480 Mbit/s, `carrier on` 4 s after the kernel started, then 5 of 5 pings |
| +46 s | `device.service` started at boot with the settings above (1920 × 1440, 3 fps, `2028:1520`). The Lambda ended `_4GnZiE6pug` and created [`A2SwVZgreMA`](https://www.youtube.com/watch?v=A2SwVZgreMA), *OT2 overhead stream hqcam-ot2-lid, 2026-10-19 UTC 16:50*, in `PLM4VC4X_7XKQ` |
| +50 s | YouTube acknowledging RTMP bytes; the channel listed the broadcast live by 16:52 |
| After | `cubos.service`, `tailscaled` and NetworkManager active, no failed units. `stream-reboot.timer` next at 13:00 MDT. No campus ARP conflicts logged. `throttled=0x0`, `EXT5V` 4.89 V, no under-voltage during the boot. A frame pulled from the live broadcast on the Pi at 16:53:37 (`yt-dlp -g -f 270`, then `ffmpeg -live_start_index -1 -frames:v 1`) carried a timestamp 15 s old and was otherwise black ([frame](../frames/2026-10-19/stream_frame_1653Z_after_reboot.jpg)): the lens is still covered |

**Checks without rebooting**, `sudo stream-reboot.sh --check`:

| Situation | Answer |
| --- | --- |
| Nothing held | *would reboot now* |
| A `systemd-inhibit --what=shutdown` lock taken by the Pi's user over SSH | *would hold off: a shutdown inhibitor is held* |
| `device.service` stopped and `/dev/media0` held open | *would hold off: the camera is in use outside device.service* |
| Up less than an hour (just after the test reboot) | *would skip this slot* |
| A stand-in OT-2 server on the runner: a maintenance run, or a protocol run that is `running`, `paused`, `finishing` or `awaiting-recovery` | *would hold off* |
| The same: a protocol run that is `idle`, `succeeded`, `failed` or `stopped`, no current run, or no answer | *would reboot now* |

Against the stand-in, the whole script also held off at every re-check, then restarted only
`device.service` at its time limit, and wrote every decision to its history file.
