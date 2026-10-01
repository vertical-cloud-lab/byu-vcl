# Stream cams

The lab's livestream cameras run the Acceleration Consortium
[picam client](https://ac-training-lab.readthedocs.io/en/latest/devices/picam.html)
(`device.py` from `AccelerationConsortium/ac-training-lab`), which pipes `rpicam-vid`
into `ffmpeg` and pushes RTMP to the *BYU VCL Hardware Streams* YouTube channel. Each
camera's settings live on its Pi, in a file that also holds a secret, so none of it is
in this repo. This page records what is set and what has been changed.

## `picam-ot2`: now pointed at the atomizer room

| | |
| --- | --- |
| Pi | Raspberry Pi Zero 2 W behind `OT2_STREAM_CAM_HOSTNAME` (user `OT2_STREAM_CAM_USERNAME`, sudo password `OT2_STREAM_CAM_PASSWORD`), Camera Module 3 (imx708), Debian 13 |
| Points at | the atomizer room, as of 2026-10-01, **not the OT-2**. It streams as `CAM_NAME = "picam-ot2"` and `WORKFLOW_NAME = "atomizer"`, so broadcasts are titled *atomizer stream picam-ot2, …* and go into the [*atomizer Livestreams Playlist*](https://www.youtube.com/playlist?list=PLeosQpHvsjiY) (`PLeosQpHvsjiY`). Until 2026-10-01 17:38 MDT the workflow was `OT-2`, whose broadcasts the Lambda files into the *OT-2 Livestreams Playlist* (`PLdKz1vXA-rfQ`). The robot itself is cabled to the Pi behind `RPI_STREAM_CAM_HOSTNAME` ([`wireless-color-sensor/ot2/README.md`](../wireless-color-sensor/ot2/README.md#run-it)) |
| Client | `~/ac-training-lab/src/ac_training_lab/picam/device.py`, upstream `87a3ccb` plus a local patch, run by `device.service`. The patch adds `SENSOR_MODE`, and on the libx264 path a 2 s keyframe interval and (since 2026-10-01) `-r FRAME_RATE`. The file as it was before the `-r` change is `~/device.py.bak-2026-10-01` |
| Settings | `my_secrets.py` in the same directory, mode `600`. It also holds the Lambda URL, so read individual lines rather than `cat` it |
| Watchdog | `stream-watchdog.timer` runs `/usr/local/bin/stream-watchdog.sh` every minute. It restarts `device.service` after 3 checks in a row with no RTMP bytes acknowledged, at most 6 times a day by default |
| Reboots | root crontab, `0 5,13,21 * * *`. Each boot starts a fresh broadcast from whatever `my_secrets.py` says |

### Current settings

| Setting | Value |
| --- | --- |
| `CAM_NAME` | `"picam-ot2"` |
| `WORKFLOW_NAME` | `"atomizer"`. Was `"OT-2"` until 2026-10-01, see [Renaming the workflow](#renaming-the-workflow) |
| `RESOLUTION` | `"240p"` (426×240). Was `"720p"` until 2026-10-01, see [Change log](#change-log) |
| `FRAME_RATE` | `2`. Was `10` until 2026-10-01 |
| `SENSOR_MODE` | `"2304:1296"`, the full-field binned imx708 mode. Without it the sensor picks a cropped mode for small outputs |
| `TIMESTAMP_OVERLAY` | `True`: lab local time, top left. This also forces the libx264 re-encode |
| `CAMERA_VFLIP` / `CAMERA_HFLIP` | `True` / `True` (the camera is mounted upside down) |
| `CAMERA_ROTATION` | `0` |
| `PRIVACY_STATUS` | `"public"` |

### Changing a setting

Edit the one line, then restart once:

```bash
ssh "$OT2_STREAM_CAM_USERNAME@$OT2_STREAM_CAM_HOSTNAME" \
  'cd ~/ac-training-lab/src/ac_training_lab/picam &&
   sed -i "s/^RESOLUTION = .*/RESOLUTION = \"240p\"/" my_secrets.py &&
   grep -n "^RESOLUTION" my_secrets.py &&
   sudo -S -p "" systemctl restart device.service' <<< "$OT2_STREAM_CAM_PASSWORD"
```

`device.py` reads `my_secrets.py` only when it starts, so nothing changes until the
restart. A restart ends the current broadcast and creates a new one with a new video ID, and the
stream is off the air for 20–30 s while that happens. Every start also counts against `device.service`'s
`StartLimitBurst=3` per hour, so don't restart in a loop. `systemctl reset-failed device.service`
zeroes that count, if a third restart within the hour can't wait. If systemd does give up, the
watchdog starts the unit again after 10 minutes.

`RESOLUTION` accepts `144p`, `240p`, `360p`, `480p`, `720p` and `1080p`. The overlay font
scales as `max(16, height // 20)`: 36 px at 720p, 16 px at 240p.

**Read the `Output #0` line after changing `FRAME_RATE`.** ffmpeg takes its output rate from
its own estimate of the piped input's rate (the `tbr` on the `Input #1` line), and at low rates
that estimate wanders. The first start at `FRAME_RATE = 2` estimated 1.50, so ffmpeg sent
1.5 fps and dropped a quarter of the frames. The next start estimated 2. At 10 fps the estimate
was 20 and ffmpeg still sent 10, which is why this never showed before. The `-r FRAME_RATE` in
the local patch pins the output to the camera's rate whatever the estimate, so expect
`Output #0 … 2 fps`.

**`systemctl status device.service` prints the stream key.** Its process list shows ffmpeg's
full command line, RTMP URL and all. The journal's `Streaming to:` and `create` response lines
carry it too. For the unit's state use `systemctl show device.service -p ActiveState -p SubState
-p ActiveEnterTimestamp -p NRestarts`, and pipe journal output through
`sed -E 's#live2/[A-Za-z0-9_-]+#live2/<key>#g'`.

### Renaming the workflow

The Lambda ([`vertical-cloud-lab/streamingLambda`](https://github.com/vertical-cloud-lab/streamingLambda/blob/05eb749/chalicelib/ytb_api_utils.py))
matches on `WORKFLOW_NAME` twice per start. Both matches are case-insensitive substring
matches:

- `end` completes every live broadcast whose *title* contains the name.
- `create` adds the new broadcast to the first playlist whose *title* contains the name. It
  creates `"<name> Livestreams Playlist"` only if no title does.

That has two consequences for a rename:

- **End the old name's broadcast yourself.** On start, the device only ends broadcasts that
  match the new name. Broadcasts are created with `enableAutoStop` off, so without this step
  the old one would sit "live" with no video coming in. Stop the service, end the old
  broadcast with the device's own call, then start the service again:

  ```bash
  cd ~/ac-training-lab/src/ac_training_lab/picam
  venv/bin/python -c "from device import call_lambda; call_lambda('end', 'picam-ot2', 'OT-2')"
  ```

- **A name that looks unused may still match a playlist.** The channel's Playlists tab, and
  yt-dlp's listing of it, leave some public playlists out. The atomizer one is among them.
  A fragment also matches: `doser` would put broadcasts in the powder doser's playlist. The
  complete list is `playlists.list(mine=True)` with the channel's own credentials, which is
  what the Lambda uses.

### Change log

| When (MDT) | Change | Why |
| --- | --- | --- |
| 2026-10-01 17:01 | `RESOLUTION` `"720p"` → `"240p"`, then one restart of `device.service` | [#250](https://github.com/vertical-cloud-lab/byu-vcl/issues/250) |
| 2026-10-01 17:38 | `WORKFLOW_NAME` `"OT-2"` → `"Atomizer"` and `FRAME_RATE` `10` → `2`. Stopped the service, ended the OT-2 broadcast `KhqPemW8hhc` [by hand](#renaming-the-workflow), started it | [#252](https://github.com/vertical-cloud-lab/byu-vcl/pull/252#issuecomment-5942678722) |
| 2026-10-01 17:44 | `WORKFLOW_NAME` `"Atomizer"` → `"atomizer"`, to match the existing playlist's title and `powder doser`. `device.py` gains `-r FRAME_RATE`. `reset-failed`, then one restart | ffmpeg was sending 1.5 fps, see [above](#changing-a-setting) |

#### 720p → 240p

Measured on either side of that change. The "before" figures are averages over the 720p
pipeline's 3 h 15 min run, and the "after" figures cover its first 5 minutes:

| | 720p (before) | 240p (after) |
| --- | --- | --- |
| `rpicam-vid` output | 1280×720 | 426×240 |
| ffmpeg CPU (of 400 %) | 111 % | 23 % |
| ffmpeg memory (of 415 MB) | 31 % | 18 % |
| Load average, 1 min | 1.29 | 0.36 |
| SoC temperature | 61.8 °C | 51.5 °C |
| Upload to YouTube | 2.54 Mbit/s | 0.29 Mbit/s |
| Renditions YouTube serves | up to 1280×720 (format 232) | 426×240 (229) and 256×144 (269) |
| Broadcast | [`3zjB1Q9Je_o`](https://www.youtube.com/watch?v=3zjB1Q9Je_o) (ended by the restart) | [`KhqPemW8hhc`](https://www.youtube.com/watch?v=KhqPemW8hhc) |

Upload is RTMP bytes acknowledged by YouTube, read with `ss -tin`, which is the counter
the watchdog also uses. That was 3.72 GB over the 720p socket's life, and 2.14 MB over
60 s at 240p. The Wi‑Fi signal was −61 dBm before the change. The renditions are from `yt-dlp -F`, run on
the other stream-cam Pi because YouTube refuses player extraction from a CI runner. The
watchdog logged no failed checks after the restart.

The view and overlay are the same in both, with the full field of view kept at 240p:

| 720p, before | 240p, after |
| --- | --- |
| ![720p frame of the atomizer room](images/stream-cam-picam-ot2-720p-2026-10-01.jpg) | ![240p frame of the atomizer room](images/stream-cam-picam-ot2-240p-2026-10-01.jpg) |

#### 10 fps → 2 fps, and the `atomizer` workflow

Both columns are at 240p. The 10 fps figures average over that pipeline's first 35 minutes,
and the 2 fps ones over its first 3:

| | 10 fps (before) | 2 fps (after) |
| --- | --- | --- |
| ffmpeg output | 10 fps, keyframe every 20 frames | 2 fps, keyframe every 4 frames (2 s in both) |
| ffmpeg CPU (of 400 %) | 23 % | 12 % |
| `rpicam-vid` CPU | 5.0 % | 1.2 % |
| SoC temperature | 49.4 °C | 46.2 °C |
| Upload to YouTube, over 60 s | 0.30 Mbit/s | 0.18 Mbit/s |
| Broadcast | [`KhqPemW8hhc`](https://www.youtube.com/watch?v=KhqPemW8hhc), workflow `OT-2` | [`Lf4QFrrJ-lA`](https://www.youtube.com/watch?v=Lf4QFrrJ-lA), workflow `atomizer` |

Upload falls less than the frame rate does because the keyframe interval stays at 2 s, so at
2 fps one frame in four is a keyframe. ffmpeg's own counter read 439 frames in 219.5 s,
i.e. 2.0 fps. YouTube still serves 30 fps renditions (`229` and `269`), and repeats each
picture to fill them. Comparing consecutive decoded frames over 16 s of `229` showed a new
picture every 15 frames (0.5 s), with an occasional one held for a full second. The watchdog
logged no failed checks after either restart.

The intermediate broadcast [`TZ79Tej1hHY`](https://www.youtube.com/watch?v=TZ79Tej1hHY)
(17:38–17:44, titled *Atomizer …*) is the one that went out at 1.5 fps.

**The atomizer playlist already existed.** *atomizer Livestreams Playlist* (`PLeosQpHvsjiY`,
public) was made for this camera's move into the atomizer enclosure on 2026-09-29. Its
description says so, but it is missing from the channel's Playlists tab. The Lambda matched
the new name to it, so broadcasts now go straight there. Every OT-2 broadcast from
2026-09-29 15:27 UTC to `KhqPemW8hhc` was already in it. The Pi's journal shows the Lambda
filed each of them into the OT-2 playlist, so something else moved them. `KhqPemW8hhc` was
moved within 40 minutes of its creation. Nothing on either stream-cam Pi does that (no cron
jobs or timers, no playlist code), so it is somewhere else, or done by hand. With the rename
it has nothing left to move.

**The archive tooling assumes 720p.** `wireless-color-sensor/ot2/stream_grab_pi.py` asks
yt-dlp for format `232` (720p), and so does `~/ytframes/grab.py` on the other stream-cam Pi.
Broadcasts from this camera after 2026-10-01 23:01 UTC do not have that format, and their top
rendition is `229`. `frames_from_stream.py`'s `OVERLAY_CROP` likewise assumes the size of the
720p overlay. Both still work on the earlier 720p archives, such as the 2026-09-09 colour
session. At 2 fps a frame grabbed at a given offset can be up to 0.5 s old. The overlay
still shows its true time.

**Not yet observed:** a scheduled reboot after these changes. The first is at 21:00 MDT on
2026-10-01. It should come back as `atomizer` at 240p and 2 fps, since all three are in the
file, but nobody has watched one do so yet.

Older records for this Pi are not on `main` yet:

- the original setup: [#172](https://github.com/vertical-cloud-lab/byu-vcl/issues/172), `docs/ot2-stream-cam.md` on branch `claude/issue-172-20260731-0633`
- the NetworkManager ACD change: [#237](https://github.com/vertical-cloud-lab/byu-vcl/issues/237), branch `claude/issue-237-20260926-0939`
- copies of the watchdog: [#202](https://github.com/vertical-cloud-lab/byu-vcl/pull/202), `wireless-color-sensor/ot2/livestream-pi/`
