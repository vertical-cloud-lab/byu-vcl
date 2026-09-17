# Raspberry Pi + CubOS Setup (Operator UI over SSH tunnel)

How to run the [CubOS](https://github.com/Ursa-Laboratories/CubOS) Operator UI on a Raspberry Pi connected to the CubXL gantry, and reach it from any laptop on the network via SSH port forwarding.

**The idea:** the Pi (connected to the gantry over the USB-B cable) runs the `cubos_api` FastAPI server, which serves the compiled Operator Web app on port **8742**. The laptop never runs any CubOS code — it SSH-tunnels port 8742 over WiFi/Ethernet and opens it in a normal browser. This works cleanly with CubOS's Host-checking middleware because, through the tunnel, the browser sees the app as `localhost:8742`, which is always trusted.

> Origin: [issue #133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5062458374), tracked in [issue #165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165). Steps verified against the CubOS repo as of July 2026.

## 1. Prepare the Raspberry Pi

Flash **Raspberry Pi OS (64-bit, Bookworm)** with Raspberry Pi Imager — in the Imager's settings gear, set a hostname (e.g. `cubxl-pi`), enable SSH, and configure WiFi credentials (skip WiFi config if using Ethernet). Then over SSH or a directly attached keyboard/monitor:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git
python3 --version   # needs 3.10+; Bookworm ships 3.11 ✓
```

The Operator Web build needs a recent Node.js — the apt version is too old, so install Node 20 from NodeSource:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Give your user serial-port access for the gantry (log out/in after):

```bash
sudo usermod -aG dialout $USER
```

## 2. Install CubOS and build the Operator UI

This is the [standard install from the API README](https://github.com/Ursa-Laboratories/CubOS/tree/main/services/api#install-and-run), run on the Pi:

```bash
git clone https://github.com/Ursa-Laboratories/CubOS.git
cd CubOS
python3 -m venv .venv
source .venv/bin/activate
pip install -e "packages/core[asmi]"
pip install -e "services/api[dev]"

cd apps/operator-web
npm ci
npm run build        # runs tsc + vite; can take several minutes on a Pi — that's normal
cd ../..
```

`npm run build` writes the compiled UI to `apps/operator-web/dist/`, which `cubos_api` serves directly — Node.js is only needed for this one-time build, not at runtime.

## 3. Point it at your configs and the gantry

Plug the gantry's USB-B cable into the Pi and confirm the serial device appears:

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

Put the CubXL config files (the Google Drive folder Alex shared in [#133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133)) somewhere like `~/cubxl-configs`, and make sure the gantry YAML's serial port matches what `ls` showed (e.g. `/dev/ttyUSB0`). Those configs were written with macOS/Linux-style ports, so they need little or no change on the Pi — unlike on a Windows machine. You'll point the server at that folder with `CUBOS_CONFIG_DIR` in the next step (CubOS also remembers a config dir in `~/.cubos/settings.json` once set).

## 4. Run the server on the Pi

```bash
cd ~/CubOS
source .venv/bin/activate
CUBOS_OPEN_BROWSER=false CUBOS_CONFIG_DIR=~/cubxl-configs python -m cubos_api
```

`CUBOS_OPEN_BROWSER=false` matters on a headless Pi — by default the server tries to pop open a browser. Leave the host/port defaults alone (`127.0.0.1:8742`): binding to localhost-only is exactly what you want for SSH tunneling, and it keeps the API unreachable from the rest of the network.

## 5. SSH port forward from your laptop

On the laptop (same network as the Pi — WiFi or Ethernet, doesn't matter as long as you can reach the Pi's address; Windows PowerShell, macOS, and Linux all have `ssh` built in):

```bash
ssh -L 8742:127.0.0.1:8742 <username>@cubxl-pi.local
```

Then open **http://localhost:8742** in your browser. The Operator UI loads from the Pi, and everything it does goes through the tunnel. The tunnel lives as long as that SSH session — closing the terminal closes the UI's connection (add `-N` if you want a tunnel-only session with no shell).

If `.local` hostname resolution doesn't work on your network (mDNS is sometimes blocked on university WiFi), find the Pi's IP with `hostname -I` on the Pi and use `ssh -L 8742:127.0.0.1:8742 <username>@<pi-ip>` instead. For a direct Ethernet cable from laptop to Pi (no router), this also works — the Pi gets a link-local `169.254.x.x` address, discoverable the same way.

## 6. Optional: start on boot with systemd

So the server survives reboots and you never have to SSH in just to start it:

```bash
sudo tee /etc/systemd/system/cubos.service > /dev/null <<'EOF'
[Unit]
Description=CubOS API + Operator UI
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/CubOS
Environment=CUBOS_OPEN_BROWSER=false
Environment=CUBOS_CONFIG_DIR=/home/pi/cubxl-configs
ExecStart=/home/pi/CubOS/.venv/bin/python -m cubos_api
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable --now cubos
```

(Adjust `pi` to your actual username. `journalctl -u cubos -f` tails the logs.)

## Notes

- **Remote access needs the Tailscale step in the workflow** — the Pi is reachable only over Tailscale SSH (residential NAT), and the GitHub runner gets onto the tailnet from a `Connect to Tailscale` step in `.github/workflows/claude.yml`. `issue_comment` events run the **default branch's** workflow, so removing that step from `main` (as [`429fe34`](https://github.com/vertical-cloud-lab/byu-vcl/commit/429fe34) did on 2026-08-26) leaves every `@claude` job with no `tailscale` binary and no route to the Pi — `tailscale status` returns `command not found`. The OAuth secrets are still passed to the job; only the step that consumes them is gone. Re-adding the four-line step restores hardware access.
- **Local CubOS patches** — `~/CubOS` on the Pi carries local fixes that are not upstream. They're recorded in [`cubos/patches/`](../cubos/patches/) with the reason for each; `cd ~/CubOS && git diff --stat` shows what's currently applied. As of the **2026-09-15 migration to upstream `main` (`496819c`)** that's **two** patches (8 files, 125 insertions): the tipped-hover clamp, which lets a tipped pipette travel on a machine whose Z ceiling is below `safe_z + tip_length`, and one escape hatch that is **not** a bug fix — see the warning in the patches README before leaving it applied. The two capper patches the Pi used to need are now fixed upstream. Migration record: [`cubos/results/cubos_migration_20260915/`](../cubos/results/cubos_migration_20260915/README.md).
- **Two serial devices** — on this Pi the GRBL controller is `/dev/ttyUSB0` (`1a86:7523` CH340) and the capper Arduino is `/dev/ttyACM0` (`2341:0043` Uno R3). Confirm with `lsusb` before trusting a config, since the numbering can move. Better still, name the stable `by-id` paths: `/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0` and `/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00`.
- **One serial connection at a time** — if UGS, a calibration script, or anything else on the Pi holds the serial port, the API can't. If the server "fails to even connect to the gantry", check nothing else has the port open (and reseat any loose motor/limit-switch connectors).
- **Tunnel vs. LAN exposure**: SSH tunneling is the recommended default. To make the UI reachable by multiple lab machines without tunnels, set `CUBOS_HOST=0.0.0.0`, add the Pi's hostname/IP to `CUBOS_TRUSTED_HOSTS`, and set a `CUBOS_API_TOKEN` — but skip that until there's a real need.
- **Sharing the OT-2's RPi 5** (per the [#154](https://github.com/vertical-cloud-lab/byu-vcl/issues/154) plan) is fine — CubOS is just a Python venv + one port, so it coexists with the OT-2 tooling as long as port 8742 is free.
- Ursa also has [PiCub-Protocol-Relay](https://github.com/Ursa-Laboratories/PiCub-Protocol-Relay) ("Send CubOS protocols to a Raspberry Pi server") — a lightweight worker (port 8000) for pushing protocol bundles to the Pi from a controller machine. That's complementary to the Operator UI: same Pi-as-server idea, aimed at scripted protocol submission rather than interactive use.
- Open question for Ursa (@alexc2684): whether BYU should use the `asmi` extra shown in the README or a different driver group for the CubXL configuration.

## Appendix: provisioning the CubXL Pi (`rpi-5-des4`), as done 2026-09-14

The CubXL moved off the OT-2 stream-cam Pi onto a dedicated Pi 5 in September 2026. This is
what a from-scratch install on that host actually took, recorded so it can be repeated. The
full verification evidence is in
[`cubos/results/pi5_des4_provision_20260914/`](../cubos/results/pi5_des4_provision_20260914/).

**Starting point:** Debian 13 (trixie) arm64, Python 3.13.5, empty home directory, nothing
CubXL-specific installed. Pi 5 Model B with **1 GB RAM** — small, but CubOS core only needs
`pyserial`, `pyyaml` and `pydantic`, all of which have arm64 wheels, so nothing compiles.

**Only one package was missing: `git`.** `python3 -m venv` already bundles pip on this
image, and `patch`, `curl`, `wget`, `gcc`, `make`, `v4l2-ctl` and `rpicam-still` are all
present. `ffmpeg` is absent and is only needed for USB UVC cameras — the two cameras on this
Pi are CSI.

```bash
sudo apt-get install -y --no-install-recommends git

# CubOS at the commit every geometry number on this branch was validated against.
# Blobless clone keeps the transfer small; the Pi is on residential wifi (eth0 is down).
cd ~ && git clone --filter=blob:none https://github.com/Ursa-Laboratories/CubOS.git
cd ~/CubOS && git checkout --detach 496819c   # upstream main as of 2026-09-15
export PIP_TIMEOUT=600 PIP_RETRIES=2
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e packages/core
.venv/bin/python -m pip install pytest

cd ~ && git clone --filter=blob:none --single-branch \
  --branch <branch> https://github.com/vertical-cloud-lab/byu-vcl.git

cd ~/CubOS
for p in tipped-hover-clamp-main pipette-connect-tolerate-failed-home-main; do
  git apply ~/byu-vcl/cubos/patches/$p.patch
done
```

> Before 2026-09-15 this Pi ran `cbc33dc` with **four** patches. That form is still
> reproducible — `git checkout --detach cbc33dc` plus the four files without a `-main`
> suffix — and is the rollback path. It also needs `cnc.default_feed_rate_mm_min`
> removed from the gantry file, since `CncYaml` at `cbc33dc` is `extra="forbid"`.

Things worth knowing when you repeat it:

- **Upgrading CubOS is a deliberate exercise, not a `git pull`.** Patches are written
  against a specific revision and so is every validated coordinate on this branch, so an
  upgrade means re-basing the patches *and* re-validating the geometry. The 2026-09-15
  migration is the worked example: audit first
  ([`cubos_update_audit_20260915`](../cubos/results/cubos_update_audit_20260915/README.md)),
  then execute against the verified recipe
  ([`cubos_migration_20260915`](../cubos/results/cubos_migration_20260915/README.md)).
  Pin the exact commit (`git checkout --detach <sha>`) rather than `origin/main`, so a
  later fetch cannot silently change what is installed.
- **Check the feed rate after any upgrade.** `cnc.default_feed_rate_mm_min` was added
  upstream in `7ff4d7f` with a module default of 3000 mm/min, up from a hardcoded 2000.
  A gantry file that omits the field inherits whatever the installed version defaults to
  — i.e. an upgrade can silently change how fast the machine moves. Ours pins it.
- **The tools in this repo are run by path**, not as `-m cubos.tools.X`. They are
  deliberately *not* copied into the CubOS tree so that `cd ~/CubOS && git diff --stat`
  stays a truthful report of exactly which patches are applied and nothing else.
- **The suite should be all green.** On `496819c` + the two `-main` patches, expect
  `2544 passed, 17 skipped, 14 subtests passed` — the ports rewrite the upstream tests
  whose behaviour they change, so nothing is left red. (The old `cbc33dc` + four-patch
  tree reported `2020 passed, 3 failed`; those three were the patch-induced failures. If
  you ever need to prove a failure is patch-induced rather than an install problem, run it
  in a pristine worktree: `git worktree add --detach /tmp/cubos-pristine <sha>` with
  `PYTHONPATH=/tmp/cubos-pristine/packages/core/src`.)
- **Verify the GRBL settings before trusting a run.** `$130/$131/$132` and `$20` are in
  `Gantry._validate_grbl_settings`' critical set and are compared at 0.001 mm, so a gantry
  file that disagrees with the controller aborts at connect before any motion. Reading
  `$$` over pyserial is harmless; the board simply resets into `Alarm` when the port opens.
- **Campaign numbering restarts on a new Pi** — the data store is `~/.cubos/panda_data.db`
  and a fresh one starts at campaign 1. Mock runs consume numbers too. Don't try to
  correlate campaign numbers across hosts.
- **No service was created.** CubOS here is a venv invoked by hand; nothing starts on boot,
  and the only thing listening on a tailnet-facing address is `sshd`. That matches the
  `tag:rpi-5-des4` grant, which is `tcp:22` only — a service bound to `0.0.0.0` would be
  unreachable from CI until its port is added to that grant, so bind new services to
  loopback and reach them over SSH.

## Appendix: check the stepper supply before diagnosing a motion fault

`WPos` in GRBL's `?` response is the controller's **internal step counter**, not a
measurement. With the stepper supply switched off, GRBL accepts every `G01`, emits the
steps, and reports a perfectly plausible position while the machine stands still. Jogging
"successfully" therefore proves nothing about whether anything moved.

This cost two sessions on 2026-09-16/17: an unpowered gantry was diagnosed as two
independent limit-switch faults, because `$H` failing with `ALARM:9` plus an axis that
"jogged smoothly" looks exactly like a dead switch.

Two power-independent checks, both free:

- **`Pn:`** in the status response is driven by the limit switch inputs, not the step
  generator. If an axis really travelled to its switch, `Pn:` names it. If a carriage
  really moved off a switch, `Pn:` loses it.
- **Any instrument with a sensor.** The capper's `decap` is an interlocked probe: it only
  confirms if a cap is physically at the head. A clean capture is proof the gantry moved.

So before concluding a switch is faulty, confirm the supply is on and that some *sensor*
— not the counter — agrees that motion happened.

⚠️ On `rpi-5-des4` the Pi shares power with the gantry: switching the gantry supply
reboots the Pi and takes it off the tailnet for several minutes. Do not power-cycle while
a protocol is running.
