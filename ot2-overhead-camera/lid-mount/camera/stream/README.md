# The lid camera's YouTube live stream

Set up 2026-10-18 ([#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234)). The HQ Camera
on the lid mount streams to the *BYU VCL Hardware Streams* channel, into the
[OT-2 Livestreams Playlist](https://www.youtube.com/playlist?list=PLdKz1vXA-rfQ) (`PLdKz1vXA-rfQ`),
the playlist the OT-2-LCM Hugging Face Space embeds. Each broadcast is titled
*OT-2 stream hqcam-ot2-lid, <date> UTC <time>*; the playlist is the stable link, since every
restart makes a new video.

It runs the same client as the other stream cams, the Acceleration Consortium
[picam `device.py`](https://ac-training-lab.readthedocs.io/en/latest/devices/picam.html)
(`rpicam-vid` piped into `ffmpeg`, which pushes RTMP to a broadcast the lab's
[streaming Lambda](https://github.com/vertical-cloud-lab/streamingLambda) creates), with the same
watchdog. What differs is the Pi: this is the Pi 5 behind `RPI_STREAM_CAM_HOSTNAME`, which also
runs CubOS and the OT-2's wired link, so it is not rebooted and the stream is niced. The general
notes on the stream cams are in `docs/stream-cams.md` on `main`.

## Files here

| File | Goes to | What |
| --- | --- | --- |
| `device.py` | `~/ac-training-lab/src/ac_training_lab/picam/device.py` | The atomizer cam's patched `device.py` (upstream `87a3ccb` plus `SENSOR_MODE`, `--flush`, `-r`, pixelation) plus three optional settings for this Pi: `RESOLUTION = "WIDTHxHEIGHT"`, `CAMERA_CODEC`, `BITRATE`. See [What changed in `device.py`](#what-changed-in-devicepy) |
| `my_secrets_example.py` | `…/picam/my_secrets.py`, mode 600 | Every setting, with the Lambda URL left blank |
| `device.service.in` | `/etc/systemd/system/device.service` | The service, with `Nice=5` added. `install.sh` fills in the user and home |
| `stream-watchdog.sh`, `.service`, `.timer` | `/usr/local/bin`, `/etc/systemd/system` | The same watchdog as the other stream cams: restarts the service after 3 minutes with no RTMP bytes acknowledged, or when systemd has given up, at most 6 times in 24 h |
| `stream-rotate.service`, `.timer` | `/etc/systemd/system` | Restarts `device.service` at 05:00, 13:00 and 21:00 local, so no broadcast runs past YouTube's 12 h archive limit. The other stream cams reboot for this; this Pi must not |
| `no-ipv4-acd.conf`, `wifi-powersave-off.conf` | `/etc/NetworkManager/conf.d/` | The two fixes the other stream cams carry. This Pi had logged 21 campus ARP conflicts (`conflict detected … with host 00:00:00:00:00:00`), the start of the outage described in [streamingLambda#9](https://github.com/vertical-cloud-lab/streamingLambda/issues/9) |
| `install.sh` | | Does all of the above on a fresh Pi, with the sudo password on stdin |

## Settings

| Setting | Value | Why |
| --- | --- | --- |
| `CAM_NAME` | `"hqcam-ot2-lid"` | `picam-ot2` is the Zero 2 W that now watches the atomizer room |
| `WORKFLOW_NAME` | `"OT-2"` | Files into the existing OT-2 playlist. The Lambda matches it as a case-insensitive substring of titles, so `end` leaves the atomizer cam's *atomizer stream picam-ot2* broadcasts alone (`ot2` is not `ot-2`), and the atomizer cam's restarts leave this one alone |
| `PRIVACY_STATUS` | `"public"` | As asked in #234 |
| `RESOLUTION` | `"1536x1152"` | 4:3, the sensor's shape. Read from the camera on 2026-10-18: this output uses `ScalerCrop (2, 0)/4052x3040`, the whole sensor; `1280x720` uses `(0, 380)/4056x2280`, which at 8 mm zoom cuts off the front and back rows of slots (the crop [`preview_server.py`](../preview_server.py) also avoids). 1536 is a multiple of 64, which the raw-frame path needs |
| `FRAME_RATE` | `10` | What the OT-2 cam ran at 720p. Plenty for a deck view, and keeps the upload near 2–4 Mbit/s |
| `SENSOR_MODE` | `"2028:1520"` | The IMX477's full-field binned mode |
| `CAMERA_CODEC` | `"yuv420"` | The Pi 5 has no hardware H.264 encoder: `--codec h264` goes through libav in software, so the stream would be encoded twice (once at the camera's bit rate, once by ffmpeg for the overlay). Raw frames to ffmpeg mean one encode and no intermediate bit rate. 1536×1152 at 10 fps is 26 MB/s through the pipe, nothing for a Pi 5 |
| `TIMESTAMP_OVERLAY` | `True` | Lab local time top left, as on the other cams; it is the clock for reading archives back |
| `CAMERA_VFLIP` / `HFLIP` / `ROTATION` | `False` / `False` / `0` | Not yet checked against the deck. If the picture is upside down, set both flips `True` (free, in the sensor) and restart once |
| `PIXELATE_BLOCKS` | `None` | Sharp. The camera looks straight down at the deck through the window |
| `BITRATE` | `4000000` | Only used with `CAMERA_CODEC = "h264"` |

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

**Stop it for a while.** `systemctl stop device.service` is enough; also
`systemctl stop stream-rotate.timer` if the stop should outlast the next 8 h mark, or the
timer will start it again.

**Playlist.** The Lambda adds each broadcast to the first playlist whose title contains
`OT-2`. If that playlist is ever renamed, the Lambda creates *OT-2 Livestreams Playlist* afresh.

## What changed in `device.py`

Three optional settings, each backward compatible (a `my_secrets.py` without them behaves as
before), on top of the atomizer cam's version:

- `RESOLUTION` accepts `"WIDTHxHEIGHT"` as well as the 16:9 presets. Even numbers, at least 64.
- `CAMERA_CODEC = "yuv420"` sends raw frames and gives ffmpeg `-f rawvideo -pix_fmt yuv420p
  -video_size WxH -framerate N` for the pipe. ffmpeg then always encodes, even with no
  filters. The width must be a multiple of 64; otherwise the frames carry stride padding that
  ffmpeg cannot see (checked: at 1536 wide the frames are exactly 1536 × 1152 × 1.5 bytes).
- With `CAMERA_CODEC = "h264"` on a Pi without `/dev/video11` (no hardware encoder), it adds
  `--libav-format h264` and writes to `pipe:1`, because rpicam-vid's libav path does not
  understand `-o -` and otherwise writes nothing. `BITRATE` sets that encoder's bit rate (the
  1 Mbit/s default is too low for a 1152-line picture).

Both paths were tried on this Pi on 2026-10-18; the raw one is in use. The patch is worth
upstreaming to `ac-training-lab` with the rest of the lab's changes.

## Set-up record, 2026-10-18

Done from a `@claude` session on #234, over Tailscale SSH. `ffmpeg` was installed with apt (the
only package added); `~/ac-training-lab` is an upstream sparse checkout with `device.py` replaced
by this one; `requests` is in `…/picam/venv`. The Lambda URL was copied from the atomizer cam's
`my_secrets.py` straight into this Pi's over SSH, so it never passed through the session's
output. Nothing else on the Pi was changed; CubOS kept running throughout.
