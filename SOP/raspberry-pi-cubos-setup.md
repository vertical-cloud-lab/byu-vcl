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

- **Local CubOS patches** — `~/CubOS` on the Pi carries local fixes that are not upstream. They're recorded in [`cubos/patches/`](../cubos/patches/) with the reason for each; `cd ~/CubOS && git diff --stat` shows what's currently applied. As of 2026-08-03 that's two patches, both needed before the Pawduino capper works at all: one so it can connect, one so `cap` can confirm a release.
- **Two serial devices** — on this Pi the GRBL controller is `/dev/ttyUSB0` (`1a86:7523` CH340) and the capper Arduino is `/dev/ttyACM0` (`2341:0043` Uno R3). Confirm with `lsusb` before trusting a config, since the numbering can move.
- **One serial connection at a time** — if UGS, a calibration script, or anything else on the Pi holds the serial port, the API can't. If the server "fails to even connect to the gantry", check nothing else has the port open (and reseat any loose motor/limit-switch connectors).
- **Tunnel vs. LAN exposure**: SSH tunneling is the recommended default. To make the UI reachable by multiple lab machines without tunnels, set `CUBOS_HOST=0.0.0.0`, add the Pi's hostname/IP to `CUBOS_TRUSTED_HOSTS`, and set a `CUBOS_API_TOKEN` — but skip that until there's a real need.
- **Sharing the OT-2's RPi 5** (per the [#154](https://github.com/vertical-cloud-lab/byu-vcl/issues/154) plan) is fine — CubOS is just a Python venv + one port, so it coexists with the OT-2 tooling as long as port 8742 is free.
- Ursa also has [PiCub-Protocol-Relay](https://github.com/Ursa-Laboratories/PiCub-Protocol-Relay) ("Send CubOS protocols to a Raspberry Pi server") — a lightweight worker (port 8000) for pushing protocol bundles to the Pi from a controller machine. That's complementary to the Operator UI: same Pi-as-server idea, aimed at scripted protocol submission rather than interactive use.
- Open question for Ursa (@alexc2684): whether BYU should use the `asmi` extra shown in the README or a different driver group for the CubXL configuration.
