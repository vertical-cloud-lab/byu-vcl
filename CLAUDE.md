## Coding Agent

- Set environment variables `PIP_TIMEOUT=600` and `PIP_RETRIES=2` prior to `conda` or `pip` installs
- Include plots directly in your comment reply via `![image name](https://github.com/<user/org>/<repo>/blob/<shortened-commit-hash>/<filename>?raw=true)`. Truncate the commit hash to the first 7 characters only. For example, `https://github.com/AccelerationConsortium/evaluation-metrics/blob/52754e7/scripts/bo_benchmarks/demonstrations/branin_campaign_demonstration_results.png?raw=true`. For provenance, ensure you use the shortened (7-character) commit hash, not the branch name
- If you mention files in your comment reply, add direct hyperlinks based on the shortened (7-character) commit hash
- IMPORTANT: Never echo/grep/print environment secrets. These should never be exposed in your terminal history or other outputs

## Edison Scientific

When waiting on an Edison task in GitHub Actions, NEVER run the polling script in the background (run_in_background, nohup, &, or the Monitor tool) — the runner is destroyed the moment you post your final comment, killing background processes; Monitor counts as background and dies the same way. Also be aware that the agent harness BLOCKS the shell `sleep` builtin in foreground Bash calls (the error message suggests Monitor — do NOT follow that suggestion, it recreates the background-death failure; this killed several past sessions). The pattern that works: put the wait INSIDE a single blocking Python call — Python-side `time.sleep` is not blocked — and run it as ONE foreground Bash call with an explicit long timeout (max 3600000 ms). Run exactly this (adjust only the task-id path):

```bash
# ONE foreground Bash tool call with timeout: 3600000
python - <<'EOF'
import json, os, time
from edison_client import EdisonClient

client = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
task_id = json.load(open("outputs/<...>/_task_id.json"))["task_id"]
while True:
    task = client.get_task(task_id=task_id, verbose=True)
    status = str(task.status)
    print("status:", status, flush=True)
    if status in {"success", "fail", "failed", "cancelled", "error"}:
        break
    time.sleep(240)
EOF
```

Equivalently, run a repo script whose own `while ... time.sleep(...)` loop does the waiting (e.g. `python scripts/explore_case_studies.py stage8-wait`) as a single long-timeout Bash call. Do not post your final comment until results are fetched and committed, or ~45 minutes of wall-clock have elapsed — in which case commit the task-id file and state that a follow-up @claude comment is needed to fetch. If you need to upload files, use analysis query type. See the docs: https://edisonscientific.gitbook.io/edison-cookbook/edison-client. Here is the endpoint you should use: https://api.platform.edisonscientific.com. The API key is `EDISON_PLATFORM_API_KEY`. Don't expose this secret, e.g., by echoing or grepping it. Pass the API key in explicitly:

```
from edison_client import EdisonClient, JobNames
client = EdisonClient(api_key=EDISON_PLATFORM_API_KEY)
```

Whenever you retrieve results (either during the current agent session or during the next session), make sure to fetch and commit all artifacts associated with a trajectory.

If using Edison Analysis, refer to https://docs.edisonscientific.com/edison-client/file-management#upload for instructions on how to upload files. If able to use Context7, to better inform use of EdisonClient, see https://context7.com/future-house/edison-client-docs/llms.txt?tokens=10000


## Tailscale → Raspberry Pi connection

If you are doing remote work with the physical Pi device (be very careful!) and claude.yml pre-connects you to tailscale, this section is applicable. Regardless, **you are already on the tailnet for the Raspberry Pi device.** As this is connected to a locally owned machine, this is a high-risk activity. The workflow joins the runner via the official
[Tailscale GitHub Action](https://tailscale.com/kb/1276/tailscale-github-action) (OAuth
client + device tag) before you start. Run `tailscale status` to confirm — do **not**
install Tailscale, mint auth keys via the API, or run `tailscale up` unless status
genuinely shows you disconnected.

**As of 2026-09-09 the `Connect to Tailscale` step is no longer in `claude.yml`,** so
`tailscale status` reports `command not found` and you are genuinely disconnected. Until a
human restores that step (the Claude GitHub App cannot edit `.github/workflows/`), bring up
an ephemeral node yourself:

```bash
curl -fsSL https://tailscale.com/install.sh | sudo bash
sudo tailscale up --authkey="${TS_OAUTH_SECRET}?ephemeral=true&preauthorized=true" \
  --advertise-tags=tag:stream-cam-test --hostname=gh-runner-<issue>
```

The install script leaves `tailscaled` running as a systemd service with a real TUN device,
so **there is no need to start `tailscaled` by hand** and no need for
`--tun=userspace-networking`. With the service in charge, MagicDNS resolves and the plain
`ssh` client works directly — `ssh "$RPI_STREAM_CAM_USERNAME@$RPI_STREAM_CAM_HOSTNAME"`
(confirmed 2026-09-09). Only if you deliberately run `tailscaled` in userspace mode do you
need the `tailscale ssh` / raw-`100.x`-address workaround.

**The tag must be `tag:stream-cam-test`** — that is the only tag this OAuth client owns, and
any other is rejected with `requested tags are invalid or not permitted`. The client is
scoped `auth_keys` only, so the device- and ACL-listing API endpoints all return
`calling actor does not have enough permissions`; you cannot discover the tag from the API.
Run `tailscale logout` when done. Under userspace networking the plain `ssh` client fails
with `Connection closed by UNKNOWN port 65535` and MagicDNS names do not resolve — use
`tailscale ssh -- <ssh-args> "$USER@<100.x address>"`, taking the address from
`tailscale status --json`.

Access to the Pi is
[Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh), authorized by
[tailnet ACLs](https://tailscale.com/kb/1018/acls) rather than SSH keys — there is no key
to find or generate. The Pi's login username, hostname, and sudo password are injected as
environment variables (check `env` names rather than assuming them);
always reference them as `"$VAR"` and never print the hostname or any credential in
comments, commits, or logs. If SSH is refused (`tailnet policy does not permit you to SSH
to this node`), the fix is an ACL/tag change only the tailnet admin can make — report it
and stop rather than working around it.

**sudo on the Pi is password-gated** — no passwordless sudo, and polkit rejects
non-interactive `systemctl`. Feed the password over stdin so it never appears in a process
list or shell history: `ssh … "sudo -S -p '' <cmd>" <<< "$RPI_PASSWORD_VAR"`.

**You have two machines — use the right one.** Your runner terminal and the Pi are
separate environments: Use the Pi only for what
genuinely requires it — its residential IP (some services block
datacenter IPs). The Pi is typically on constrained residential Wi‑Fi and may be carrying
live workloads, so rate-cap any large transfer (`--limit-rate` or equivalent) and never
run full-bandwidth speed tests on it.

**Treat the Pi as a live production device.** Inspect read-only first (`systemctl status`,
`journalctl`, `crontab -l` as root) before changing state: scheduled reboots, watchdog
timers, and `Restart=` policies may already exist, so an unreachable or restarting device
may be behaving as designed — check the clock and the existing automation before declaring
an outage or adding new monitoring. Restart services only when necessary and verify the
device's workload is healthy end-to-end afterwards, reporting failures as failures.
Changes made on the Pi (systemd units, cron, scripts, config) do not live in this repo —
record them in the repo's docs so they can be reproduced or upstreamed.

## Secret inventory

Names and purposes only — **never** echo, grep, or print the values. Every secret below is
set on both `vertical-cloud-lab/byu-vcl` and `vertical-cloud-lab/digital-wetlab`, and is
passed through the `env:` block of `.github/workflows/claude.yml`. Adding a new secret means
editing that block too; the Claude GitHub App cannot modify `.github/workflows/`, so that
step is always a human commit.

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

**Other services**

| Secret | Purpose |
| --- | --- |
| `HF_TOKEN` | Hugging Face `byu-vcl` account, fine-grained: read + write contents/settings of own repos. Enough to duplicate Spaces (`duplicate_space`), upload files, and set Space-side secrets (`add_space_secret`). |
| `ZENODO_API_TOKEN` | Zenodo personal access token, scopes `deposit:write` + `deposit:actions`. |
| `OT2_SERIAL` | `OT2CEP20210722R13`. Namespaces the `command/ot2/<serial>/pipette` and `status/ot2/<serial>/complete` topics. Read from the robot's own `/health` endpoint, where `robot_serial` and `name` agree. |
| `PICO_ID` | `e6647c15673a2438`, the Pico W's `machine.unique_id()`. Namespaces the `command/picow/<id>/as7341/read` and `color-mixing/picow/<id>/as7341` topics. Must match the `PICO_ID` in that board's `my_secrets.py`, or the Space and the sensor talk past each other in silence. |

**Hugging Face Space secrets are a separate place to keep in sync.** A duplicated
light-mixing / OT-2-LCM Space reads its own settings, not GitHub's, and expects these exact
names: `blinded_connection_string`, `MONGODB_PASSWORD`, `MQTT_BROKER`, `MQTT_PORT`,
`MQTT_USERNAME`, `MQTT_PASSWORD`, and `YT_API_KEY`. Set them with `add_space_secret` using
`HF_TOKEN` so the two sides cannot drift.

**Reaching the OT-2.** The robot is not on the tailnet. It is wired directly to a Pi and
answers only on the link-local address `http://169.254.51.252:31950`, so every OT-2 HTTP API
call has to be made *from that Pi* — you cannot reach the robot from a runner or a laptop.
Send `Opentrons-Version: 3` on every request. `GET /health` is read-only and safe; anything
under `/maintenance_runs` moves real hardware.

**Which Pi, though — the name is misleading.** Despite the naming, the USB-Ethernet adapter
is on `RPI_STREAM_CAM_HOSTNAME`, *not* `OT2_STREAM_CAM_HOSTNAME` (verified 2026-09-09): a
Realtek RTL8153 on `eth1` holding `169.254.210.205/16`, alongside the Arduino and the
`~/ot2ctl.py` wrapper and every past `~/run_*` directory. The `OT2_STREAM_CAM_HOSTNAME` Pi
has no ethernet interface and no USB devices at all. Check `ip -4 -br addr` on both before
concluding the robot is offline — a session in September 2026 reported the OT-2 dead when it
was simply being probed from the wrong host.

**`POST /camera/picture` shows you the deck.** The OT-2 has an onboard camera looking down at
the deck, and it is the cheapest possible preflight: one HTTP call, no motion, and it answers
"is the labware actually there?" before a protocol presses down on an empty slot. Note it is
a **POST** — a GET returns 405, which is easy to misread as "no camera". The frame comes back
640x480, rotated a quarter turn because the camera is mounted on its side.
`wireless-color-sensor/ot2/deck_photo.py` wraps this.

**The camera rides on the gantry, so it cannot show you its own nozzle tip.** The viewpoint
shifts with every move, and when the gantry is parked over the slot you care about, the
pipette body occludes exactly the spot you were trying to inspect. That makes the camera
excellent for "is the labware present?" and useless for "is the nozzle centred on the
socket?" — `run_xscan_test.py --align` plus a photo will not settle an alignment question,
and a human has to eyeball it. What *does* verify engagement automatically is the script's
grip check: seated counts vs lifted counts, which on 2026-09-09 read 436 -> 2253 = **5.2x**
against a 2.0x threshold.

**Ambient light dominates any reading taken off the base.** On 2026-09-09 the module was
carried to three X positions 30 mm apart in an *empty* slot 8, same Y and Z at each. Totals
came out 4489 / 3691 / 5401 — a **46% swing with nothing in the slot at all**. The deck is
not evenly lit, so raw counts are not comparable between positions: a paint measurement has
to be divided by an empty-slot reading taken at that same X, or the enclosure has to be
light-tight. Do not read a colour difference out of two positions without that baseline.
For scale, the module *seated on its base* reads only ~437, about 10x lower than any lifted
reading, which is why the seated baseline is not a usable dark reference either.

**Every scan on record so far was taken with the module's own LEDs off**, which is why
ambient dominates. `run_xscan_test.py --rgb` defaults to `0,0,0` and `SensorLink.read()`
publishes it straight through as `{"command": {"R": 0, "Y": 0, "B": 0}}`, so the counts are
room and deck light leaking into the enclosure, not a controlled measurement. Before
measuring anything real -- diluted paint included -- set `--rgb` and re-baseline; that also
makes enclosure light-tightness, rather than a normalisation scheme, the thing worth fixing.

**Slot 7 at read Z 120 is the best measurement pose found so far, and higher is worse.**
Measured 2026-09-09 across four empty-slot scans:

| pose | totals across the three X positions | read-to-read spread |
| --- | --- | --- |
| slot 7, z 120 | 7263 / 7084 / 6861 (-5.5% over 60 mm) | **0.03-0.07%** |
| slot 7, z 125 | 4238 / 5144 / 6227 (+47%) | 1-11% |
| slot 8, z 120 | 4489 / 3691 / 5401 (+46%, V-shaped) | 0.1-28% |

Raising the nozzle 5 mm -- aperture 29.5 mm to 34.5 mm off the deck -- costs 9-42% of the
signal and makes repeatability 30-300x worse, and it *reverses* the sign of the positional
gradient. At the centre position the falloff matches inverse-square exactly
(`(29.5/34.5)^2 = 0.731` predicted, 0.726 measured), but the off-centre positions do not, so
the illumination only behaves like a point source directly under the slot centre. Slot 7
also beats slot 8 outright on both signal and flatness. Default to slot 7 at z 120 and do
not raise the aperture looking for a better view -- there isn't one.

**Reaching the Pico W.** The sensor board plugs into the OT-2 stream-cam Pi over USB and is
driven with `mpremote`, installed there as a venv at `~/.venvs/mpremote/bin/mpremote`
(1.29.0 + pyserial). It went in as a venv rather than apt so it needs no sudo and touches
nothing system-wide; that Pi also runs CubOS gantry work, so keep changes to it contained.

**Always address the board by USB serial, never by device path:**

```bash
~/.venvs/mpremote/bin/mpremote connect id:e6647c15673a2438 fs ls
```

An Arduino (`2341:0043`) already owns `/dev/ttyACM0` on that Pi, so the Pico comes up as
`ttyACM1` — and `mpremote`'s bare auto-connect grabs the *first* ACM device. Targeting a
path, or letting it auto-detect, opens a REPL against the Arduino instead, which may be
driving real gantry hardware. Match on `2e8a` / the serial and nothing else.

Two more gotchas. Connecting with `mpremote` interrupts whatever `main.py` is running and
its buffered `log.txt` is lost, so an empty log after a reset means "I interrupted it", not
"it never ran" — to watch a boot, `mpremote ... run <local copy of main.py>` and read the
stream instead. And the reference `main.py` calls `connectWiFi(..., country="CA")`; for US
operation that should be `"US"`, since the country code governs the usable 2.4 GHz channels.

**The board has no controllable illumination — `--rgb` is inert.** `sensor_read.py`
publishes `{"command": {"R":r,"Y":y,"B":b}}` and the board answers with a reading, so the
message is understood, but nothing lights. Measured 2026-09-09 with the module seated in
its closed base: `0,0,0`, `32,32,32`, `128,128,128`, `255,255,255`, and each channel alone
at 255 all return 437–439 counts (`wireless-color-sensor/ot2/led_probe.py`, one MQTT round
trip, no robot motion). **Every colour measurement is therefore ambient room light
reflected off the sample**, and raw counts are comparable only against an empty reading at
the same X, Y and Z. Do not plan a measurement around switching the LEDs on until someone
has established that there are any.

**An X-only scan crosses one row of the deck.** `run_xscan_test.py` varies X at a fixed
`--scan-dy`, so labware laid out along Y is missed however fine the X pitch. On 2026-09-09
a 9-position 10 mm sweep across slot 7 found exactly one of three vials for this reason.
`--scan-dy` takes a single float; a Y sweep would need a code change.

**The module can come off the nozzle during a long run.** The same sweep ended with the
enclosure lying on the deck instead of on its base — the reseat-confirm read 15084 counts
against a seated 440, which is the signature (~34x seated) and is why that check exists.
Watch for it *during* a run too: the sweep's spatial profile changed shape, not just level,
against two earlier runs at identical coordinates, which is what a tilting module looks
like. Do not command more motion after this happens; re-seating by robot means pressing the
nozzle onto an object whose position and orientation are unknown.

**A deeper pickup press also raises the read height.** `--press-z` (added 2026-09-09)
sets how far the nozzle is driven into the module's socket; lower is deeper and grips
harder. But seating the nozzle further in makes the module ride that much higher on it, so
the aperture ends up higher off the deck at the same `--read-z`. `--read-z 129 --press-z
90.0` gives a 39.0 mm aperture against the 37.5 mm of `--read-z 128 --press-z 90.5` — 1.5 mm
higher, not 1.0. **Compare `aperture_height_mm` in the run JSON across runs, never
`--read-z`.** `--press-z` also shifts the release height by the same delta, so the module is
set down from the height the proven recipe used rather than dropped from 0.5 mm up.

**A grip ratio is not a measure of grip.** It is a light reading at the lift height, so it
answers "did the module leave its base" and nothing more; changing the press depth moves the
aperture and shifts the ratio for reasons unrelated to how tightly the module is held.
Equally, **one clean cycle does not validate a grip fix** — on 2026-09-09 the three-position
cycle completed cleanly and the module was then lost during the longer sweep that followed.
Stress a fix before believing it.

**Bare deck is not spectrally flat, and is not the same at every position.** At x = 93.88 in
slot 7 the 620 nm share is 28.6% against 20.9% at the slot centre — in the empty-slot run and
both paint runs alike. So a reddish-looking spectrum is not evidence of a red sample, and the
only valid reference is an empty reading at the *same* X, Y and Z. Note also that a sample
sitting outside the scan slot still shows up: with no light-tight enclosure the aperture
picks up stray light from labware tens of mm away, brightest samples dominating, which reads
like a weak detection at the nearest X.

**MicroPython 1.29.0 or newer is required.** On 1.26–1.28 the RP2040 hardware I2C driver has
a regression: `i2c.scan()` ACKs the AS7341 at `0x39`, but every register read or write
returns `OSError: [Errno 5] EIO`, at any bus speed, with or without a repeated START. It
cost real time to find because it looks exactly like a wiring or power fault, and because it
reproduces on *every* board — two different Pico Ws, two different sensors and two different
base boards all failed identically. That cross-board consistency is the tell: a shared
firmware bug, not a shared hardware fault. Bit-banged `SoftI2C` works on the same pins on the
affected versions and is the fallback if an older build is ever unavoidable. See
[micropython#19087](https://github.com/micropython/micropython/issues/19087) and
[micropython#18257](https://github.com/micropython/micropython/issues/18257).

**Do not judge the sensor from a board plugged into the Pi.** `main.py` prints continuously
(`waiting for connection...`, `Elapsed: Ns`, `RAM free ...`). With USB enumerated but nothing
reading the serial port, the RP2040 CDC TX buffer fills and `print()` blocks, so `main.py`
starts and then wedges before it ever reaches the broker. Under `mpremote run` a host is
draining the buffer, so the same code runs fine — which makes this look like an intermittent
network problem. On mains or battery power with no USB host, MicroPython discards stdout and
it behaves normally. Verify the MQTT path with the board on its own power, not on the Pi.

Board backups (including the pre-existing `my_secrets.py`) are on the Pi under
`~/pico-backups/<timestamp>/`, and the board keeps its own `my_secrets.py.bak`.

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

**YouTube.** Channel `UCZ5KNGkEEqDsRVn0Nlfn0IA` ("BYU VCL Hardware Streams"), OT-2 playlist
`PLdKz1vXA-rfQ` ("OT-2 Livestreams Playlist"). Both are stored as Space *variables*, not
secrets, since they are public identifiers. `YT_FALLBACK_VIDEO_ID` is the embed shown when
the API is unavailable. Note the playlist ID is unusually short — that is genuine, not a
truncation.

**Not yet provisioned** — `YT_API_KEY` (a YouTube Data API v3 key from the Google Cloud
console; until it exists the Space falls back to a fixed embed instead of tracking the
current stream), `ONEDRIVE_EDIT_LINK_URL` (the password is stored without the link it
unlocks), and a Box share link for image backup. Note that sandbox is a wholly separate instance with its own
account, its own token, *and its own base URL* (`sandbox.zenodo.org/api`) — code that only
swaps the token will still write to production.
