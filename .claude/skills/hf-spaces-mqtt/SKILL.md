---
name: hf-spaces-mqtt
description: The OT-2 color-mixing cloud stack - MongoDB Atlas (cluster alloy, digital-wetlab database, MONGODB_*), HiveMQ Cloud MQTT credentials per client and the topic scheme (MQTT_*), and the private Hugging Face Spaces byu-vcl/OT-2-LCM and byu-vcl/light-mixing (Space secrets via HF_TOKEN, local code edits to re-apply, sensor timestamps, unprovisioned keys). Use when touching those services or Spaces.
---

# MongoDB, MQTT and the Hugging Face Spaces

**MongoDB Atlas** — org *Vertical Cloud Lab @ BYU*, project `byu-vcl`, cluster `alloy`
(M0 free, AWS Oregon). The database user is scoped `readWrite` on the `digital-wetlab`
database only, so it cannot read the alloy lab's data in the same cluster.

| Secret | Purpose |
| --- | --- |
| `MONGODB_URI` | Full `mongodb+srv://` string with the password already substituted. |
| `MONGODB_BLINDED_URI` | Same string but keeping the literal `<db_password>` placeholder. This is the `blinded_connection_string` convention the OT-2-LCM Hugging Face Space expects — pair it with `MONGODB_PASSWORD`. |
| `MONGODB_USERNAME` | `digital-wetlab-rw`. |
| `MONGODB_PASSWORD` | Substituted into `MONGODB_BLINDED_URI`. |
| `MONGODB_DATABASE` | `digital-wetlab`. Collections: `sensor-data`, `ot2-runs`. |

**HiveMQ Cloud** — free Serverless cluster, TLS on 8883 (WebSocket 8884). The free tier has
no per-topic permissions: every credential is `PUBLISH_SUBSCRIBE` across all topics, so
topic isolation is a convention, not an enforced boundary. Credentials are split per client
only so that one can be rotated without disturbing the others.

| Secret | Purpose |
| --- | --- |
| `MQTT_BROKER`, `MQTT_PORT`, `MQTT_WEBSOCKET_PORT` | Broker host and ports. |
| `MQTT_USERNAME` / `MQTT_PASSWORD` | `vcl-agent` — CI and local debugging. |
| `MQTT_PICOW_USERNAME` / `MQTT_PICOW_PASSWORD` | `picow-color-sensor` — goes in the Pico W's on-device `my_secrets.py`. |
| `MQTT_HF_SPACE_USERNAME` / `MQTT_HF_SPACE_PASSWORD` | `hf-space` — the Hugging Face Space subscriber. |
| `MQTT_OT2_USERNAME` / `MQTT_OT2_PASSWORD` | `ot2-robot`. |

Topic scheme, matching `AccelerationConsortium/OT-2-LCM`:

```
command/picow/{PICO_ID}/as7341/read      # ask the sensor for a reading
color-mixing/picow/{PICO_ID}/as7341      # sensor publishes readings here
command/ot2/{OT2_SERIAL}/pipette         # OT-2 commands
status/ot2/{OT2_SERIAL}/complete         # OT-2 completion status
```

**Hugging Face Space secrets are a separate place to keep in sync.** A duplicated
light-mixing / OT-2-LCM Space reads its own settings, not GitHub's, and expects these exact
names: `blinded_connection_string`, `MONGODB_PASSWORD`, `MQTT_BROKER`, `MQTT_PORT`,
`MQTT_USERNAME`, `MQTT_PASSWORD`, and `YT_API_KEY`. Set them with `add_space_secret` using
`HF_TOKEN` so the two sides cannot drift.

## Hugging Face Spaces

`byu-vcl/OT-2-LCM` and `byu-vcl/light-mixing`, both **private**, `cpu-basic`, duplicated
from the Acceleration Consortium originals. Their secrets live in the Space's own settings,
not in GitHub, so the two places have to be kept in sync by hand — set them with
`HfApi.add_space_secret` using `HF_TOKEN` rather than clicking through the UI.

The Space reads `blinded_connection_string`, `MONGODB_PASSWORD`, `MONGODB_DATABASE`,
`MQTT_BROKER`, `MQTT_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD`, and `YT_API_KEY`. Its MQTT
credential is `hf-space`, deliberately separate from the device and CI credentials.

Three edits were needed on top of the duplicate, and they will need re-applying if the
Spaces are ever re-duplicated from upstream:

- `app.py` — `OT2_SERIAL` and `PICO_ID` were hardcoded to the AC's own devices. They now
  read from env, defaulting to ours.
- `DB_utils.py` — every collection was opened on database `LCM-OT-2-SLD`. Our database user
  is scoped `readWrite` on `digital-wetlab` alone, so left alone *every write would fail
  authorization*. It now reads `MONGODB_DATABASE`.
- `app.py` — the YouTube lookup is now fail-soft. `yt_utils.get_latest_video_id` calls
  `raise_for_status()`, and `app.py` called it at import time, so a missing or invalid
  `YT_API_KEY` took the **whole Space down at startup** rather than merely hiding the video.

**Sensor readings carry their own time now.** `sensor_read.read()` returns
`t_request_utc`/`t_response_utc`; before 2026-09-09 the only recoverable instant was the
epoch-ms that `experiment_id` happens to embed. The MongoDB `timestamp` field used to be
`utcnow()` at *insert*, shared by every document of a run and up to three minutes after the
reading it described; it is now the reading's own response time, with the write time kept
separately as `stored_at`. Old documents in `digital-wetlab.sensor-data` still have the
insert-time value — reconstruct from `experiment_id` instead.

**Not yet provisioned** — `YT_API_KEY` (a YouTube Data API v3 key from the Google Cloud
console; until it exists the Space falls back to a fixed embed instead of tracking the
current stream), `ONEDRIVE_EDIT_LINK_URL` (the password is stored without the link it
unlocks), and a Box share link for image backup. Note that sandbox is a wholly separate instance with its own
account, its own token, *and its own base URL* (`sandbox.zenodo.org/api`) — code that only
swaps the token will still write to production.
