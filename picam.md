# Pi Camera (picam) Equipment Monitoring — BYU VCL Setup & Troubleshooting

BYU VCL setup notes and runbook for the Raspberry Pi streaming camera used for
equipment monitoring. The hardware/software design and the canonical setup
instructions are maintained upstream:

- Device docs: <https://ac-training-lab.readthedocs.io/en/latest/devices/picam.html>
- Pi-side code: <https://github.com/AccelerationConsortium/ac-training-lab/tree/main/src/ac_training_lab/picam>
- Streaming Lambda: <https://github.com/AccelerationConsortium/streamingLambda>

This document captures the parts that are specific to the BYU VCL deployment and
the diagnosis/fixes for [issue #9](https://github.com/vertical-cloud-lab/byu-vcl/issues/9).

## How it fits together

```
RPi Zero 2W (picam) --HTTPS--> AWS Lambda Function URL --> YouTube Data API
        |                              |
        | only secret on the Pi is     | holds token.pickle (YouTube OAuth) in S3,
        | LAMBDA_FUNCTION_URL          | creates/starts/ends broadcasts
        |
        +--RTMP--> YouTube ingestion (ffmpeg)
```

- The Pi only ever holds the **Lambda Function URL** (plus a GitHub-issued JWT it
  fetches at runtime). It never holds `token.pickle`. Anyone with the Lambda URL
  can start/end streams, but cannot obtain full YouTube account control. Keep the
  OAuth `token.pickle` only in S3, accessed by the Lambda — never on the Pi.
- The Pi calls the Lambda to `create`/`testing`/`live`/`end` a broadcast, then
  pipes the camera to YouTube over RTMP with `ffmpeg`.

## Stream quality configuration (resolution / FPS / bitrate)

The Pi-side `device.py` reads these environment variables (defaults shown). Set
them in the `device.service` systemd unit (`Environment=` lines) or the shell
that launches `device.py`:

| Variable | Default | BYU VCL (reported in #9) | Notes |
| --- | --- | --- | --- |
| `PICAM_WIDTH` | `640` | `256` (≈144p) | Frame width in px |
| `PICAM_HEIGHT` | `360` | `144` (144p) | Frame height in px |
| `PICAM_FPS` | `15` | `15` | Frames per second |
| `PICAM_VIDEO_BITRATE` | `1000k` | — | Target ffmpeg bitrate |
| `PICAM_VIDEO_MAXRATE` | = bitrate | — | ffmpeg max bitrate |
| `PICAM_VIDEO_BUFSIZE` | `2000k` | — | ffmpeg buffer size |

Source: [`device.py` `start_stream`](https://github.com/AccelerationConsortium/ac-training-lab/blob/main/src/ac_training_lab/picam/device.py).

To raise quality (there is headroom in GPU/VRAM per the free memory reported on
the Pi), bump back toward the defaults, e.g. 360p:

```ini
# /etc/systemd/system/device.service  ([Service] section)
Environment=PICAM_WIDTH=640
Environment=PICAM_HEIGHT=360
Environment=PICAM_FPS=15
```

Then `sudo systemctl daemon-reload && sudo systemctl restart device.service`.

> Tip: increase resolution/FPS in small steps and watch YouTube Studio "Stream
> health". The stream hangs reported in #9 were dominated by the BYU **devices**
> Wi-Fi network dropping packets, not by VRAM. If health stays poor at higher
> bitrate, the bottleneck is the network (consider eduroam/wired), not the Pi.

## Diagnosis of the YouTube Studio symptoms reported in #9

### 1. Grayed-out latency / stream options in YouTube Studio

This is expected, **not a bug**. The broadcast is created programmatically by the
Lambda, which sets the latency at creation time:

```python
"contentDetails": {
    "enableAutoStart": True,
    "enableAutoStop": False,
    "latencyPreference": "Low",
    "monitorStream": {"enableMonitorStream": False},
}
```

Source: [`streamingLambda/chalicelib/ytb_api_utils.py`](https://github.com/AccelerationConsortium/streamingLambda/blob/main/chalicelib/ytb_api_utils.py).

Because latency (and the reusable stream key's `frameRate`/`resolution`, which are
set to `"variable"`) are fixed via the API, YouTube Studio grays them out. To
change latency, edit `latencyPreference` in the Lambda (`Low`, `ultraLow`, or
`normal`) and redeploy — not in Studio. `enableMonitorStream: False` also disables
the Studio monitor/preview, which is why several controls appear inactive.

### 2. "Stream health" / encoder error and intermittent hangs

These come from the very low, bursty bitrate at 144p plus packet loss on the BYU
devices network. Mitigations, in order:

1. Confirm the camera pipeline is alive (`sudo journalctl -u device.service -f`).
2. Raise resolution/FPS modestly (see table above) so YouTube receives a steadier
   keyframe cadence (`-g` GOP is `fps*2`).
3. If health is still poor, move the Pi to a more reliable network
   (eduroam or wired) — the network, not the Pi, is the limiting factor.

### 3. `token.pickle` keeps getting auto-revoked

Google now enforces MFA for accounts using Google Cloud / the YouTube Data API
(<https://docs.cloud.google.com/docs/authentication/mfa-requirement>). If the
account backing the OAuth client lacks 2FA, Google invalidates the refresh token,
so `token.pickle` goes stale and streams fail with `401 Unauthorized`.

Fix: enable 2FA on the Google account that owns the OAuth client, regenerate
`token.pickle`, and upload it to the S3 key the Lambda reads. Note that enabling
live streaming on a fresh YouTube channel also imposes a one-time 24-hour wait.

## AWS / Lambda ownership (migration to the shared VCL org account)

The Lambda + S3 should run under the **shared VCL AWS organization** account, not a
personal account, so logs/traffic/changes aren't tied to one person. Creating the
Lambda requires permissions that the plain `seth-leavitt` IAM user lacks
(`iam:CreateRole`, `iam:ListRoles`, `lambda:CreateFunction`). Two viable paths:

- Use a role that already grants Lambda/S3 management in the org account (an IAM
  user/role with the needed policies — root-user object ownership is a symptom of
  using the management account directly rather than an org IAM principal).
- If picking an existing execution role when creating the function, the roles
  confirmed usable in #9 were `lambda_role_multipart_upload`, `PowerBuilder`, and
  `ReadOnly` (the Lambda execution role only needs S3 read for `token.pickle` plus
  basic logging; it does not need `iam:CreateRole`).

Once the Lambda runs in the org account, update the Pi's `LAMBDA_FUNCTION_URL`
(in `my_secrets.py`) to the new Function URL — that is the only Pi-side change
needed.

## YouTube channels

- Current/interim: BYU VCL channel.
- Long-term hardware streams channel: <https://www.youtube.com/@vcl-hardware-streams>
  (ownership/credentials kept separate from the BYU VCL channel). Remember to
  update the stream/video description (it previously inherited the AC Toronto VCL
  text).
