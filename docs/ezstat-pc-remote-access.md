# Remote access to the EZstat-Pro's PC

The NuVant EZstat-Pro ([#231](https://github.com/vertical-cloud-lab/byu-vcl/issues/231),
[PR #291](https://github.com/vertical-cloud-lab/byu-vcl/pull/291)) is driven by EZware on a
Windows 7 PC. Windows 7 gets no security updates, so the PC stays off BYU's network and the
internet. It is cabled by Ethernet to the CubXL Pi (des4) and nothing else, and des4 forwards
Remote Desktop to it from the tailnet as a Tailscale subnet router.

```
your laptop --tailnet--> CubXL Pi, des4 (Wi-Fi uplink) --eth0, 192.168.231.0/24--> Windows 7 PC (192.168.231.10)
```

The plan is in [@sgbaird's #231 comment](https://github.com/vertical-cloud-lab/byu-vcl/issues/231#issuecomment-6327249004).
It named `rpi-5-76zj` as the router, but the PC was cabled to des4 instead before step 2
was run, on 2026-10-21. byu-vcl's CI runners carry `tag:rpi-5-des4`, so they can SSH to des4
but not to 76zj.

## What is set, and where

| | |
| --- | --- |
| Windows 7 PC | Set at the PC in step 1 of the plan: `192.168.231.10/24`, no gateway, no DNS, and Remote Desktop on with its firewall rules limited to remote IP `192.168.231.1`. From des4 you can confirm the address and that Remote Desktop answers. You can't confirm the firewall limit, because des4 *is* `192.168.231.1`. Windows 7 SP1 (build 7601) |
| des4, `eth0` | NetworkManager profile `ezstat-pc-link`: `192.168.231.1/24`, manual, `ipv4.never-default`, IPv6 link-local only, autoconnect priority 10. Saved as `/etc/NetworkManager/system-connections/ezstat-pc-link.nmconnection`, a keyfile rather than netplan YAML |
| des4, forwarding | `/etc/sysctl.d/99-ezstat-pc-router.conf`: `net.ipv4.ip_forward = 1`. IPv6 forwarding stays off |
| des4, Tailscale | `tailscale set --advertise-routes=192.168.231.10/32`. SNAT is left on (the default), so the PC sees every connection as coming from `192.168.231.1`, the only address its firewall lets in |
| Tailnet | The route has to be approved before anyone can use it; see below |

Wi-Fi is still des4's only uplink and default route. `eth0` is a private link, not an uplink.

## Approving the route (tailnet admin)

Either of these works:

- Merge [tailscale-policy#21](https://github.com/vertical-cloud-lab/tailscale-policy/pull/21) and
  add `tag:ezstat-pc-router` to **des4**, keeping its existing tags (`tag:rpi-5-des4`,
  `tag:tailscale-ssh`). Leave it off 76zj.
- Or approve it by hand: admin console → Machines → des4 → ⋯ → **Edit route settings** → tick
  `192.168.231.10/32`.

Don't auto-approve the route for `tag:rpi-5-des4`. byu-vcl's CI runners carry that tag, so a
runner could advertise the same address, have it approved, and receive the PC's Remote Desktop
traffic.

## Connecting

- From any device on the tailnet, open Remote Desktop to `192.168.231.10`. Expect a warning
  about the PC's self-signed certificate.
- **Linux devices ignore subnet routes until told otherwise:** `sudo tailscale set --accept-routes`.
  Windows, macOS, iOS and Android accept them by default.
- The PC doesn't answer ping. Windows blocks it on a network with no gateway, which it treats
  as public, so a failed ping is not a fault. Test port 3389 instead.
- A CI session reaches the PC through des4: SSH in, then connect to `192.168.231.10` from there.

## Checks on 2026-10-21, about 22:24 UTC

All of these were run from des4. The handshake checks stop before login and send no user name
or password.

| Check | Result |
| --- | --- |
| TCP 3389 on `192.168.231.10` | Open |
| Security the PC offers | CredSSP (Network Level Authentication, NLA), over TLS 1.2 (`ECDHE-RSA-AES256-SHA384`) |
| Security it accepts | Also TLS without NLA, and the older standard RDP security. **NLA is offered but not required** |
| CredSSP version | 5. On Windows 7 that's the version with the 2018 CredSSP fix (CVE-2018-0886), so up-to-date clients shouldn't stop with the "CredSSP encryption oracle remediation" error |
| Windows version, from the NTLM challenge | 6.1, build 7601: Windows 7 SP1 |
| des4's own workload | `deckcam` still active with no restarts. Wi-Fi is still the only default route, the two CubXL serial devices are unchanged, and Tailscale reports no health warnings |

## Recommended: make the PC require NLA

Without NLA, a connection reaches the Windows login screen before proving who it is. Windows 7's
Remote Desktop had a bug that let such a connection run code on the PC: BlueKeep,
CVE-2019-0708, patched in May 2019. Requiring NLA means a Windows password is needed first.

The PC is reachable from des4, and so from every byu-vcl CI run, since those can SSH to des4.
Once the route is approved, everyone on the tailnet can reach it too. The checks above show NLA
works on this PC, so requiring it shouldn't lock out a modern client. To turn it on, either:

- go to System Properties → Remote and pick *Allow connections only from computers running
  Remote Desktop with Network Level Authentication*, or
- in an administrator Command Prompt, run:

```bat
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v UserAuthentication /t REG_DWORD /d 1 /f
```

## How step 2 was run on des4

This is the plan's step 2 with three changes:

- **"Wired connection 1" was left alone.** On des4 it is NetworkManager's in-memory default
  profile (autoconnect priority −999, DHCP), so `ezstat-pc-link` (priority 10) takes `eth0`
  without it. Modifying it would only have saved a copy to disk.
- **The sysctl file is written by the root script** rather than with `echo … | sudo tee`, because
  sudo gets its password on stdin (see CLAUDE.md).
- **The script refuses to overwrite routes des4 already advertises,** since `tailscale set
  --advertise-routes` replaces the whole list. There were none.

```bash
#!/bin/bash
# Step 2 of the EZstat-Pro PC remote-access plan (#231), on the CubXL Pi (des4).
# Run as root. Safe to re-run: it skips anything already in place.
set -euo pipefail
exec </dev/null
trap '' HUP

PROFILE=ezstat-pc-link
PI_ADDR=192.168.231.1/24
ROUTE=192.168.231.10/32
SYSCTL=/etc/sysctl.d/99-ezstat-pc-router.conf

echo "== start $(date -u +%FT%TZ)"
echo "== profiles before"
nmcli -t -f NAME,DEVICE,ACTIVE,AUTOCONNECT,AUTOCONNECT-PRIORITY con show

[ "$(cat /sys/class/net/eth0/carrier 2>/dev/null)" = 1 ] || { echo "ABORT: eth0 has no carrier"; exit 1; }

# 1. Static address on eth0. "Wired connection 1" is NetworkManager's in-memory
#    default here (autoconnect-priority -999), so this profile (priority 10)
#    wins without modifying it.
if nmcli -t -f NAME con show | grep -qx "$PROFILE"; then
  echo "== $PROFILE already exists, not adding it again"
else
  echo "== adding $PROFILE"
  nmcli con add type ethernet ifname eth0 con-name "$PROFILE" \
    connection.autoconnect-priority 10 ipv4.method manual \
    ipv4.addresses "$PI_ADDR" ipv4.never-default yes ipv6.method link-local
fi
echo "== activating $PROFILE"
nmcli --wait 30 con up "$PROFILE"

# 2. Forwarding, kept across reboots
echo "== forwarding"
printf 'net.ipv4.ip_forward = 1\n' > "$SYSCTL"
chmod 0644 "$SYSCTL"
sysctl -p "$SYSCTL"

# 3. Offer the PC's address to the tailnet, without overwriting any other route
cur=$(tailscale debug prefs | python3 -I -c 'import json,sys; print(",".join(json.load(sys.stdin).get("AdvertiseRoutes") or []))')
echo "== advertised routes before: ${cur:-none}"
if [ -n "$cur" ] && [ "$cur" != "$ROUTE" ]; then
  echo "ABORT: already advertising $cur; not overwriting"; exit 1
fi
tailscale set --advertise-routes="$ROUTE"

echo "== after"
ip -br -4 addr show dev eth0
nmcli -t -f NAME,DEVICE,ACTIVE,AUTOCONNECT,AUTOCONNECT-PRIORITY con show
echo "ip_forward=$(cat /proc/sys/net/ipv4/ip_forward)"
ip -4 route show default | sed -E 's/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/<ip>/g'
tailscale debug prefs | python3 -I -c 'import json,sys; print("AdvertiseRoutes:", json.load(sys.stdin).get("AdvertiseRoutes"))'
ls -l /etc/netplan/ "$SYSCTL"
echo "== done $(date -u +%FT%TZ)"
```

From a CI runner, it was uploaded and then started detached, so that a dropped SSH connection
couldn't stop it halfway. `sudo -k` makes sudo always read the password line, so the password
is never left on stdin for the script to read. Both files were deleted from des4 afterwards.

```bash
H="$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME"
ssh "$H" 'umask 077; cat > /tmp/ezstat-step2.sh' < ezstat-step2.sh
ssh "$H" "sudo -k -S -p '' bash -c 'setsid bash /tmp/ezstat-step2.sh > /tmp/ezstat-step2.log 2>&1 < /dev/null &'" <<< "$CUBXL_PI_PASSWORD"
ssh "$H" 'cat /tmp/ezstat-step2.log'
```

## Undo, on des4

```bash
sudo tailscale set --advertise-routes=
sudo nmcli con delete ezstat-pc-link
sudo rm /etc/sysctl.d/99-ezstat-pc-router.conf
sudo sysctl -w net.ipv4.ip_forward=0
```

No reboot is needed. NetworkManager puts `eth0` back on its DHCP default. Then remove
`tag:ezstat-pc-router` from des4, if it was added.
