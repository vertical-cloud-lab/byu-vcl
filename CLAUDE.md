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


## CubXL / CubOS — commanding physical motion

This section applies whenever a task *could* command motion on the lab's CubXL gantry —
directly, over the Tailscale/Pi connection below, or through any CubOS entry point. The
CubXL is a live machine with a rigid head carrying both a pipette and a vial
capper/decapper; a wrong Z or a stale offset is a tool strike, not a failed test. Also read
CubOS's own [`AGENTS.md`](https://github.com/Ursa-Laboratories/CubOS/blob/main/AGENTS.md)
and [`CLAUDE.md`](https://github.com/Ursa-Laboratories/CubOS/blob/main/CLAUDE.md) — this
section is BYU-specific and additive, not a replacement.

### The rule that matters most

**One human authorization buys exactly one hardware run.** If a run fails, aborts, alarms,
or makes contact with anything, **stop and report**. Do not adjust a number and try again,
do not run a probe or a shortened variant to isolate the cause, do not "just confirm the
fix." The next hardware run needs a new, explicit go-ahead from the human in the thread,
after they have seen what happened. This is not a formality: on 2026-08-03 an unrequested
follow-up run dragged the pipette stand-in along the right X rail (#133, #171).

The same holds for the first run. "Here are my configs", "why did this fail?", and "what
should `engage_depth_mm` be?" are **not** authorization to touch hardware. Answer with the
analysis and the exact command you would run, and let the operator run it or say go.

### Never do these unless the human asked for that specific action

- `python -m cubos.tools.run_protocol` **without** `--mock` (hardware is the default;
  `--mock` is the opt-out — "Run gantry and instruments offline; never connect to hardware")
- `cubos.tools.calibrate_gantry`, `cubos.tools.hello_world`, `cubos.tools.home_gantry_config`,
  `cubos.tools.test_connection` — every one of these connects and moves
- Raw GRBL on the serial port (`$H`, `$X`, `$J=`, `G0`/`G1`) or any `pyserial` script that
  writes motion or actuates the electromagnet
- Any ad-hoc probe or sweep script that descends toward the deck
- Any Operator UI / `cubos_api` action that jogs, homes, or runs a protocol
- Starting a hardware run in the background, on a schedule, in a retry loop, or in any way
  where you would not see the outcome before posting. **A human must be at the machine, able
  to cut power, for the entire run** — you cannot press the e-stop, they can.

### The gate ladder — every rung, in order, every time

1. **`validate_setup`** — pure offline bounds/reachability check, no port opened:
   `python -m cubos.tools.validate_setup <gantry> <deck> <protocol> [initial_fluids]`
2. **`run_protocol --mock`** — offline dry run of the full sequence, gantry and instruments
   stubbed: `python -m cubos.tools.run_protocol --mock <gantry> <deck> <protocol>`
3. **Bare-deck rehearsal, human-witnessed** — real machine, real motion, **no labware, no
   vials, no caps**, markers where labware will go. Per @alexc2684: "before you run a
   protocol, run it without any labware (or maybe markers for where the labware should be)
   and verify the positions look correct before running with real labware."
4. **Hardware run with labware** — only after 1–3 pass *and* the operator says go **for this
   run**.

Report the exact command and observed output for each rung. Never claim a rung you skipped.

### Use a 3D-printed pipette stand-in, not a screwdriver

Motion rehearsals should carry a printed dummy with the real nozzle geometry. An improvised
tool has the wrong length and stiffness, so a rehearsal that "passes" says nothing about the
real tip plane, and a strike bends the head instead of a cheap reprintable part. See
[`docs/pipette-selection-cubxl.md`](docs/pipette-selection-cubxl.md) for the head being selected.

### What offline validation does NOT catch

A green `validate_setup` + `--mock` is **not** "safe to run." Each of these was found the
hard way on this machine:

- **The other instrument's swept volume.** Both tools are rigid on one head, and
  `gantry = deck − offset`, `gantry_z = deck_z + depth`. With the capper at
  `offset (0, 0) / depth −25` and the pipette at `offset (+135, +20) / depth 0`, commanding
  the capper to deck `(x, y, z)` puts the pipette nozzle — the lowest thing on the head — at
  deck `(x+135, y+20, z−25)`, a third of the bed away in X. `validate_setup` only
  bounds-checks the *commanded* instrument. **Work out by hand where every other tool on the
  head goes, for every step, before any hardware run.**
- **Transit paths on a `move` with no explicit `travel_z`.** That move's lift/lower segment
  is not modeled at all, so a path that clips the Cub XL X-max rail passes silently. Give the
  first move out of the homed corner an explicit `travel_z`.
- **Whether the target makes sense.** Bounds checking asks "is this coordinate reachable",
  never "is this the vial you just opened." A protocol that decaps `vial_1` and then descends
  the pipette into still-capped `vial_7` validates PASS.
- **`offline: true` on an instrument.** It stubs *that instrument only* — the gantry still
  moves for real. A capper left `offline: true` on a hardware run drives the head down onto
  every vial, reports "decap successful", never fires the magnet, and the pipette then
  descends into a capped vial. `offline: true` is for `--mock` runs only.
- **A `working_volume.z_max` above the machine's real travel.** That field is what
  `validate_setup` bounds-checks against; if it exceeds GRBL `$132` the guard is simply gone
  and you get soft-limit alarms instead. Confirm `$132`, `$20`, `$23` against the controller
  rather than trusting the YAML.

### Config values are measured, not derived

`engage_depth_mm`, `safe_z`, `depth`, and the instrument offsets describe *this* machine. Do
not compute a plausible value from the deck YAML and then run it — on this CubXL the deck Z
column and the `depth` field have both been wrong by >10 mm in the same direction, so an
estimate from either one misses. If a number is unknown, say so and hand the operator a
measurement procedure instead of a guess. (`CAPPER_ENGAGE_DEPTH_MM = -15.0` in
`tools/panda_bear_import/constants.py` is a placeholder whose own comment says it was "never
measured against real PANDA hardware.")

### If something goes wrong

1. Stop the run. Report exactly what happened — failing step, command, log — **before**
   proposing anything.
2. Leave the machine in a known state and say what that state is: tool at `safe_z`,
   electromagnet de-energized, sensor reading taken. A failed capture can raise without ever
   calling `release_cap()`; closing the port resets the Arduino and drops the pin, which is
   why an exiting `run_protocol` is safe and a long-lived API server is not. To de-energize
   explicitly, send `6` (`CMD_EMAG_OFF`) on the capper port.
3. Ask before doing anything else. Diagnosis that requires motion is a new hardware run and
   needs new authorization.

@alexc2684 (CubOS author) on this: "since I started this project I have not let AI run
hardware. I'll always validate motion before hand without instruments, or run it through the
validation script … it's a little too easy for AI to access underlying gantry movement."
Treat that as the ceiling on autonomy here, not an opening position.

### Housekeeping

- **One process per serial port.** UGS, the Operator UI / `cubos_api`, a calibration script,
  and `run_protocol` all want the same port and only one can hold it. Close the others first
  — this is the most common connection failure on this machine. On the lab Pi:
  `/dev/ttyUSB0` (CH340) is the gantry, `/dev/ttyACM0` (Arduino Uno) is the capper.
- **Record what you change.** Local edits to `~/CubOS` on the Pi do not live in that repo —
  capture them as patches with a written cause/fix under `cubos/patches/`, and file CubOS
  bugs at https://github.com/Ursa-Laboratories/CubOS/issues (upstream tracks them there).
- For labware placement relative to instruments, see
  https://github.com/Ursa-Laboratories/Instrument-Overlap-Viewer.

## Tailscale → Raspberry Pi connection

If you are doing remote work with the physical Pi device (be very careful!) and claude.yml pre-connects you to tailscale, this section is applicable. Regardless, **you are already on the tailnet for the Raspberry Pi device.** As this is connected to a locally owned machine, this is a high-risk activity. The workflow joins the runner via the official
[Tailscale GitHub Action](https://tailscale.com/kb/1276/tailscale-github-action) (OAuth
client + device tag) before you start. Run `tailscale status` to confirm — do **not**
install Tailscale, mint auth keys via the API, or run `tailscale up` unless status
genuinely shows you disconnected. Access to the Pi is
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
