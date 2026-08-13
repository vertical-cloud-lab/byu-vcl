## Coding Agent

- Set environment variables `PIP_TIMEOUT=600` and `PIP_RETRIES=2` prior to `conda` or `pip` installs
- Include plots directly in your comment reply via `![image name](https://github.com/<user/org>/<repo>/blob/<shortened-commit-hash>/<filename>?raw=true)`. Truncate the commit hash to the first 7 characters only. For example, `https://github.com/AccelerationConsortium/evaluation-metrics/blob/52754e7/scripts/bo_benchmarks/demonstrations/branin_campaign_demonstration_results.png?raw=true`. For provenance, ensure you use the shortened (7-character) commit hash, not the branch name
- If you mention files in your comment reply, add direct hyperlinks based on the shortened (7-character) commit hash
- IMPORTANT: Never echo/grep/print environment secrets. These should never be exposed in your terminal history or other outputs

## OneDrive/SharePoint PowerPoint decks (remote access & editing)

Applies to any presentation file shared via an OneDrive/SharePoint sharing link. The
full validated recipe with working code lives in
[docs/onedrive-sharepoint-ppt-access.md](docs/onedrive-sharepoint-ppt-access.md) — read
it before touching the file. Summary of the rules and gotchas:

- **Password-protected links**: the link password is injected as a workflow secret
  (e.g. `ONEDRIVE_EDIT_LINK_PASSWORD`) — never echo/print it. Unlock by submitting the
  `guestaccess.aspx` ASP.NET form postback (`__EVENTTARGET=btnSubmitPassword` + viewstate
  fields); success redirects to `Doc.aspx` and issues a guest `FedAuth` cookie that
  authorizes the SharePoint REST API as "Guest Contributor" (view + download + edit).
- **Download** via `GET /_api/web/GetFileById(guid'<UniqueId>')/$value` with that cookie
  jar. (`GetFileByUniqueId` does not exist on this endpoint.)
- **Two write paths — pick based on whether anyone has the file open:**
  1. *Headless-browser co-authoring* — **the preferred/default path, and the only one
     that works while the owner is editing.** If no browser tool is available in the
     environment: `pip install playwright`, then launch with `channel="chrome"` to use
     the system Chrome (no browser download). Inject the `FedAuth` cookie from the unlock
     step into the browser context to skip the password page, load the sharing link,
     and wait ~40 s for the Office WOPI editor iframe to boot — it opens directly in
     Editing mode and autosaves/merges with any live human session.
  2. *REST upload* (`POST .../$value` with `X-HTTP-Method: PUT` + `X-RequestDigest`
     from `/_api/contextinfo`): a backup, only if explicitly requested by the user or required (download →
     modify with `python-pptx` → upload), but it is a **whole-file replace** and
     returns **HTTP 423 `SPFileLockException` whenever anyone has the file open**
     (co-authoring lock, not a permission failure; it lingers ~10 min after they
     close). If retrying, re-download the latest copy and re-apply your changes
     before every attempt so you never clobber concurrent human edits. Do not sit in
     a retry loop for tens of minutes — switch to path 2.
- **Verify persistence by re-downloading the stored blob** (and checking the pptx XML)
  1–2 minutes after editing. Never trust the editor's "Saved" indicator or an
  apparently-successful upload alone — a prior run believed an upload had landed when
  it hadn't.
- **PowerPoint for the web cannot edit slide masters/layouts** (no Slide Master view —
  a Microsoft limitation, not a permissions issue). Master/layout work requires
  `python-pptx` + REST upload while the file is closed, or desktop PowerPoint.
- Precision drawing in the web editor (exact inch sizes via the Shape ribbon's numeric
  fields, pixel↔inch mapping, screenshot-verified drags, `%2B` encoding for `+` in key
  combos) is documented in the recipe doc — use those techniques rather than freehand.
- Make edits reversible where possible (SharePoint version history exists) and label test
  edits clearly.

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
