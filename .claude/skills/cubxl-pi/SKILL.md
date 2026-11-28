---
name: cubxl-pi
description: The CubXL Pi 5 (CUBXL_PI_HOSTNAME / CUBXL_PI_USERNAME / CUBXL_PI_PASSWORD) and what hangs off it - reaching it over Tailscale SSH, its Arduino Uno and CH340 serial devices (by-id paths), Wi-Fi-only networking, and the Windows 7 potentiostat PC (EZstat Pro / EZware, POTENTIOSTAT_PC_*) over Remote Desktop with xfreerdp3. Use for any CubXL, potentiostat or vial-stirrer hardware task.
---

# CubXL Pi and potentiostat PC

The rules in the root `CLAUDE.md` apply throughout: never print a credential, hostname or IP, and treat every Pi as a live production device.

**Reaching the CubXL Pi.** A Pi 5 on the tailnet at `CUBXL_PI_HOSTNAME`, reachable over
Tailscale SSH as `CUBXL_PI_USERNAME` the same way the stream-cam Pis are. It is the access
point Ben Whitney uses by commenting `@claude` on this repo: the runner joins the tailnet
and SSHes in, so what matters is the *runner's* tag, not a user identity. The policy file
grants SSH **within** each tag, so the runner has to carry the Pi's tag to reach the Pi.
Because the source is a tagged node the rule is `"action": "accept"` — [check mode cannot be
used from a tagged device](https://tailscale.com/kb/1193/tailscale-ssh), as there is no
human to re-authenticate. Ben also has a direct user-scoped rule, which works the moment he
joins the tailnet; that path needs no CI at all.

The Pi itself: Debian 13 (trixie) on arm64, Tailscale 1.86.2 with `--ssh`, one
`sudo`-capable user (in `dialout`, so serial ports need no sudo). It is joined over **wifi
only** (`eth0` is down), so moving it out of range of that SSID takes it off the tailnet
until it is given credentials for the new network. Its tailnet name and IP survive the move;
nothing else does.

**The CubXL hardware is attached; the software is not (as of 12 September 2026).** Two USB
serial devices, both part of the CubXL:

| Device | USB ID | Stable path |
| --- | --- | --- |
| Arduino Uno R3, serial `03535343335351018130` | `2341:0043` | `/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00` |
| CH340 USB–serial converter | `1a86:7523` | `/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0` |

**Address them by the `by-id` path, never by `/dev/ttyACM0` or `/dev/ttyUSB0`.** Those names
are assigned in enumeration order and swap if a board is re-plugged or a third device
appears — the same trap CLAUDE.md already documents for the stream-cam Pi, where a bare
`mpremote` auto-connect opened a REPL against the wrong board. The CH340 exposes no unique
serial, so its `by-id` path stops being unique the moment a second CH340 is plugged in; if
that ever happens, distinguish them by USB port path (`/dev/serial/by-path/`) instead.

Nothing CubXL-specific is installed yet: no non-stock services, nothing listening beyond
`sshd` and `tailscaled`, an empty home directory. When software does land, remember the
tailnet grant to this Pi is `tcp:22` only — a control service bound to `0.0.0.0` is
unreachable from CI until its port is added to the `tag:rpi-5-des4` grant, and the safer
default is to bind it to `127.0.0.1` and reach it over SSH.

**The potentiostat PC (`POTENTIOSTAT_PC_USERNAME` / `POTENTIOSTAT_PC_PASSWORD`).** Windows account on the Windows 7 PC that runs EZware for the CubXL's EZstat Pro ([#231](https://github.com/vertical-cloud-lab/byu-vcl/issues/231)), for Remote Desktop (tcp:3389) to `192.168.231.10`. The PC runs no Tailscale and has no gateway; it sits on a point-to-point Ethernet link to the CubXL Pi, which advertises that one address as a subnet route. Only people are granted that route — devices are not, and CI runners carry `tag:rpi-5-des4`, so they deliberately cannot. From a CI session, reach the PC from the CubXL Pi itself, which is on the link directly: SSH in and run the RDP client there, passing the credentials over stdin or env, never as arguments. The Pi has FreeRDP 3 and Xvfb (`apt install --no-install-recommends freerdp3-x11 xvfb`, 2026-10-21). Feed every argument through `xfreerdp3 /args-from:stdin`, one per line, since it cannot be combined with other arguments. Include `/tls:seclevel:0`: without it OpenSSL 3 refuses Windows 7's TLS and the handshake fails with `ERRCONNECT_TLS_CONNECT_FAILED`, before any password is sent. FreeRDP prints a parse error for that line but applies it. `/cert:tofu` pins the PC's self-signed certificate in `~/.config/freerdp/server/`. To check the login without disturbing the PC, add `/sec:nla /auth-only`: it authenticates and stops before creating a session. A full session takes over the PC's only desktop on Windows 7 and locks out whoever is at the console, mid-experiment perhaps.
