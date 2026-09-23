# Calibrating the OT-2 in the Opentrons App

Everything below was checked against this robot (`OT2CEP20210722R13`) on
2026-09-11 and against Opentrons' own docs and app source, not from memory. The
robot's state at that moment is in
[`calibration-state-2026-09-11.json`](calibration-state-2026-09-11.json), and
[`calibration_status.py`](calibration_status.py) re-derives it in one read-only
command.

## What actually needs calibrating

There are **four** calibrations, and only the last one is Labware Position
Check. They must be done in this order, because **calibrating the deck clears
the other two** — that is the Opentrons App's own wording:

> "Calibrating pipette offset before deck calibration when both are needed
> isn't suggested. Calibrating the deck clears all other calibration data."
> — `deck_calibration_modal_description`, Opentrons App localisation

| # | calibration | scope | where |
| --- | --- | --- | --- |
| 1 | **Deck** | the robot | Robot Settings → Calibration |
| 2 | **Tip length** | per pipette **× per tip-rack type** | Robot Settings → Calibration |
| 3 | **Pipette offset** | per pipette × per mount | Robot Settings → Calibration |
| 4 | **Labware Position Check** | per labware type **× per deck slot** | a protocol's Setup tab |

Steps 1–3 are "robot calibration" and live under Robot Settings. Step 4 is not
there at all — **LPC only exists inside a protocol run**, which is why it cannot
be done ahead of time or from the Devices screen.

## State of this robot, 2026-09-11

```
deck calibration        OK  last 2026-01-27  with pipette P20SV202020030408
left mount              p300_single_v2.1  P3HSV212021083111
  tip length     MISSING   (robot holds 17 entries, none for this pipette)
  pipette offset MISSING
  tiprack custom_beta/ac_color_sensor_charging_port/1  ->  MISSING
labware offsets (LPC)   0 stored
networking              limited  eth0=connected  wlan0=disconnected
```

Three things follow from that:

- **The deck calibration is stale.** It is dated 2026-01-27 and the robot was
  physically moved on 2026-09-10. The app: *"Calibrating the deck is required
  for new robots or after you relocate your robot."*
- **The attached P300 has no calibration data at all.** The robot holds 17 tip
  length calibrations and 1 pipette offset calibration, none of them for
  `P3HSV212021083111`. The app blocks a run in this state — *"Please calibrate
  all pipettes specified in loaded protocol to proceed."*
- **The app cannot see the robot.** `wlan0` is disconnected and `eth0` has a
  link-local address with no gateway, so the only machine that can reach the
  OT-2 is the stream-cam Pi it is cabled to. Calibration happens in the
  Opentrons App, which runs on a computer — so this has to be solved first.

## Step 0 — get an app that still supports the OT-2

**Download the separate Opentrons OT-2 App, not the Opentrons App.** Since
**v9.1.1** (24 June 2026) the main Opentrons App is Flex-only. Opentrons' own
release notes for that version:

> **"OT-2 robots will no longer appear in the Opentrons App."** v9.1.1 will
> prompt you to get the separate Opentrons OT-2 App, or you can download it
> directly from <https://opentrons.com/app>.
> — [`app-shell/build/release-notes.md`](https://github.com/Opentrons/opentrons/blob/edge/app-shell/build/release-notes.md)

So updating the app to "the current version" is what makes an OT-2 *disappear*
from the Devices tab. The Devices screen shows **"No robots found"** and no
amount of cable-checking will change it.

<https://opentrons.com/app> now offers two separate downloads:

| app | for | direct link | build seen 2026-09-23 |
| --- | --- | --- | --- |
| Opentrons App | **Flex only** | `builds.opentrons.com/Opentrons.{exe,dmg,AppImage}` | v9.1.2 |
| **Opentrons OT-2 App** | **OT-2** | `ot2.builds.opentrons.com/Opentrons-OT2.{exe,dmg,AppImage}` | **v26.6.0** (b10562, 2026-06-24) |

The OT-2 App is calendar-versioned (`v26.6.0`) and is a different product from
the `v9.x` line, so the two version numbers cannot be compared. Installing it
alongside the Flex app is fine.

The same architecture limit applies to it: the Linux build
`Opentrons OT-2-v26.6.0-linux-b10562.AppImage` is ELF `e_machine 0x3e`, i.e.
**x86-64 only**, with no arm64 asset. It will **not** run on Raspberry Pi OS, so
the stream-cam Pi cannot host it. Any x86-64 Linux machine works; a Windows
machine is not required.

### Installing it on Ubuntu

The lab computer runs Ubuntu, and the Linux build is an **AppImage** — one
executable file, not a `.deb`. There is no apt repository and nothing to
install; it needs a permission bit and, usually, one library.

```bash
uname -m                        # must print x86_64
cd ~/Downloads
curl -L -o Opentrons-OT2.AppImage https://ot2.builds.opentrons.com/Opentrons-OT2.AppImage
chmod +x Opentrons-OT2.AppImage
./Opentrons-OT2.AppImage
```

**If it exits at once with `dlopen(): error loading libfuse.so.2`, that is the
one Ubuntu-specific trap.** This is a **type 2** AppImage — byte `0x0A` of the
download is `0x02`, checked on 2026-09-23 — and type 2 mounts itself with FUSE
**2**, which Ubuntu stopped shipping when it moved to FUSE 3:

```bash
sudo apt install libfuse2t64     # Ubuntu 24.04 "noble"
sudo apt install libfuse2        # Ubuntu 22.04 "jammy" — the package was renamed in 24.04
```

It installs alongside the system's FUSE 3 and conflicts with nothing
([AppImage docs](https://docs.appimage.org/user-guide/troubleshooting/fuse.html)).
If installing it is genuinely not an option,
`./Opentrons-OT2.AppImage --appimage-extract-and-run` unpacks to a temporary
directory and runs from there — slow and wasteful, so a fallback rather than the
plan.

One smaller thing: an AppImage does not add itself to the Activities menu, so
**launch it from a terminal** the first time. Any error it hits on startup goes
to that terminal and nowhere else, which is the whole reason to start there.

### There is no USB-B port on this robot

An earlier revision of this file said to connect the app over USB-B. **That was
wrong for this machine.** Its rear panel carries an RJ45 Ethernet jack and a
power connector, and nothing else — confirmed at the machine on 2026-09-23, and
consistent with Opentrons' current documentation, which lists the side panel as
carrying only the "on/off switch, an Ethernet port, and the power port"
([Robot Components](https://docs.opentrons.com/ot-2/system-description/robot/)).
The four USB-A ports are *inside* the enclosure, behind the gantry, and are for
Opentrons modules, not for a host computer.

Opentrons' own first-run instructions are Ethernet-only and say so plainly:

> "Connect the Ethernet cable to the OT-2 and your computer. If your computer
> does not have an Ethernet port, use the provided Ethernet-to-USB dongle."
> — [OT-2 First Run](https://docs.opentrons.com/ot-2/installation/first-run/)

Note which end that dongle is for: the **computer's**, not the robot's. That is
the source of the confusion. Opentrons do sell an
[internal USB-to-Ethernet adapter](https://support.opentrons.com/s/article/Replacing-the-OT-2-s-internal-USB-to-Ethernet-adapter)
as a replacement part, but it lives *inside* the robot, bridging the Compute
Module to the rear RJ45 jack. Older OT-2s additionally exposed a rear USB-B port
backed by that same bridge — the app still ships a Realtek driver-version check
for it (`usb_to_ethernet_adapter_info_description`: *"Some OT-2s have an
internal USB-to-Ethernet adapter"*). **This unit is not one of them.**

### One RJ45 jack, two things that want it

The robot has exactly **one** Ethernet jack, and the Pi's RTL8153 dongle
(`0bda:8153`) normally occupies it. So connecting a laptop means unplugging the
Pi, and that takes the robot off the tailnet: `run_xscan_test.py`,
`deck_photo.py`, `calibration_status.py` and every CI check stop working until
the cable goes back. This is visible in the Pi's journal as a plain USB
disconnect — on 2026-09-23 the dongle was live from 09:47:36 MDT and pulled at
10:09:14:

```
r8152-cfgselector 2-1: USB disconnect, device number 2
device (eth1): state change: activated -> unmanaged (reason 'unmanaged-link-not-init')
```

After that `lsusb` on the Pi lists no Realtek device at all and `eth1` is gone —
which is the honest signature of "somebody unplugged it", as distinct from the
`status -71` wedge that
[`ot2_link_recover.sh`](ot2_link_recover.sh) exists for, where `eth1` survives
and lies about `carrier`.

**Plug the dongle back into the Pi when calibration is done.** Better, put a
cheap unmanaged Ethernet switch between them: link-local addressing (IPv4LL)
works normally across a switch, each host self-assigns a unique `169.254/16`
address with ARP conflict detection, and the Pi and a laptop can then both hold
the robot at once. Untested here, but it is ordinary Ethernet behaviour and it
removes the unplug/replug dance.

### If the app still cannot find the robot

Establish whether it is a *network* problem or an *app* problem before touching
either. [`find_ot2.sh`](find_ot2.sh) answers that in one command — copy it to
the Ubuntu machine that has the robot's cable, then:

```bash
chmod +x find_ot2.sh
./find_ot2.sh
```

It is read-only and needs no root. It lists every interface and its address,
asks `avahi-browse` what it can see, *and* sends the same `_http._tcp.local`
mDNS query the app's Devices tab sends (so it works whether or not
`avahi-utils` is installed), collects every candidate address it can (mDNS
responders, the neighbour table, `<name>.local`, the previously-seen address),
tries `GET /health` on each, and prints a verdict. On a Windows machine use
[`find_ot2.ps1`](find_ot2.ps1) instead — same three questions, same output
shape. Doing it by hand instead:

```bash
ip -4 addr show                       # the wired interface should hold a 169.254.x.x address
nmcli device status                   # and NetworkManager should call it "connected"
ping -c3 169.254.51.252               # the address this robot has been using
avahi-resolve -n OT2CEP20210722R13.local     # mDNS name lookup; apt install avahi-utils
curl -s http://169.254.51.252:31950/health
```

That last line is the decisive one, and a browser at
**`http://169.254.51.252:31950/health`** does the same thing — type the
`http://` prefix explicitly, because an address with a port and no scheme can go
to the search engine instead. It should return JSON naming
`OT2CEP20210722R13`. That single test splits the problem:

- **JSON comes back, app still shows nothing** → app-side, i.e. discovery. Skip
  straight to *Add the robot by IP* below; everything else on this page is then
  optional.
- **No JSON** → link-side. The adapter has no usable address, or nothing is on
  the other end of the cable. See *When the link itself is the problem*.

**A blank page is not evidence that the robot is down.** Three different faults
give it — this machine has no link-local address of its own, the robot's address
is not the one you typed, or the cable/adapter is dead — and they need opposite
fixes. Do not skip to the next step until you know which.

#### Discovery is mDNS, and it backs off to one query every two minutes

The app does not poll the network for robots. Each OT-2 advertises itself over
multicast DNS as `<name>._http._tcp.local`, and the app runs an `mdns-js`
browser that listens for it and keeps services whose port is `31950`
([`discovery-client/src/mdns-browser/index.ts`](https://github.com/Opentrons/opentrons/blob/edge/discovery-client/src/mdns-browser/index.ts)).
Two constants in that file explain almost every "I plugged it in and nothing
happened":

```ts
const IFACE_POLL_INTERVAL_MS = 5000
const QUERY_INTERVAL_MS = [4000, 8000, 16000, 32000, 64000, 128000]
```

`repeatCall` walks that array and then **holds the last value forever**
([`repeat-call.ts`](https://github.com/Opentrons/opentrons/blob/edge/discovery-client/src/mdns-browser/repeat-call.ts)),
so an app that has been open for more than about four minutes is asking **once
every 128 seconds**. Waiting 30 seconds and concluding it failed is too quick.

The redeeming detail is `pollNetworkInterfaces`: every 5 s the app compares its
browser's bound interfaces against the system's and, on any mismatch, tears the
browser down and starts a new one — which re-queries **immediately**
(`callImmediately: true`) and resets the backoff to 4 s. So:

> **Unplugging and replugging the USB-Ethernet adapter is the fastest way to
> force a fresh scan** — faster and more reliable than restarting the app,
> because it is a *guaranteed* interface change.

The comparison is on `{name, address}` pairs, so the moment the adapter goes
from no address to `169.254.x.x`, that too counts as a change and restarts
discovery on its own. On Ubuntu that transition does not happen on its own —
see step 3 of *When the link itself is the problem* — but when you do make it
happen, the app notices within 5 s. Which means the honest reading of a Devices
tab that has said **"No robots found"** for several minutes is: *the adapter
never got a link-local address*, or *the mDNS packets are not arriving*.

#### Add the robot by IP — the reliable way past all of it

Gear icon (bottom-left) → **Advanced** → **Connect to a Robot via IP Address** →
*Set up connection* → enter `169.254.51.252` → **Add**. The strings are
`"connect_ip": "Connect to a Robot via IP Address"` and
`"ip_description_first": "Enter an IP address or hostname to connect to a
robot."` in the app's own localisation.

This bypasses mDNS entirely: the app polls `GET /health` on the address you gave
it. If the browser test above returned JSON, this will work. It is worth doing
**first**, not last — a working connection is more useful than a diagnosis, and
the entry is remembered.

#### Things that break mDNS while leaving HTTP working

Each of these produces exactly "No robots found" *and* a `/health` that answers
fine from `curl` or a browser. The Ubuntu list is shorter than the Windows one,
because the usual Windows culprit — a new wired network auto-classified
**Public**, where inbound UDP 5353 is blocked — has no counterpart here.
**Ubuntu Desktop ships `ufw` inactive** and has no per-network firewall
profiles, so there is nothing to reclassify.

- **A firewall, only if somebody enabled one.** `sudo ufw status`. If it reports
  `inactive`, this is not the problem and nothing needs changing. If it reports
  `active`, allow the multicast port: `sudo ufw allow 5353/udp`.
- **Both Opentrons apps running at once.** The Flex app and the OT-2 app each
  create their own mDNS browser. `pgrep -af -i opentrons` finds a stray one.
  This is *less* likely to bite on Linux than on Windows: the browser's socket is
  created with `reuseAddr: true`
  ([`node-mdns-js/lib/networking.js`](https://github.com/mdns-js/node-mdns-js/blob/master/lib/networking.js)),
  which is what lets it share UDP 5353 with Ubuntu's own `avahi-daemon` instead
  of failing to bind. Still worth ruling out.
- **More than one active network interface.** Discovery has a history of failing
  outright when several adapters — particularly several USB-to-Ethernet ones —
  are present, the robot appearing only once the extra adapter is removed.
  `nmcli device status` lists them and `nmcli radio wifi off` takes Wi-Fi out of
  the picture for the duration; fewest interfaces wins. Note a `docker0` bridge
  or a `tailscale0` counts as an interface too.

#### When the link itself is the problem

If `ip -4 addr show` shows no `169.254.x.x` address on the wired interface, no
amount of app configuration will help. Work through these in order; each one is
a different fault, and **step 3 is the one that bites on Ubuntu.**

**1. Is the robot itself up?** The front button should be lit, and
`robot-server` takes about three minutes after power-on before it answers
anything. A robot that was power-cycled a minute ago looks exactly like a dead
cable.

**2. Does the adapter exist, and does it have a link?**

```bash
lsusb                      # the dongle itself, e.g. 0bda:8153 Realtek RTL8153
ip link show               # the interface it created, and whether it is UP
sudo dmesg | tail -30      # which driver bound it, e.g. r8152
sudo ethtool enp0s20u1     # "Link detected: yes" — the Media-State equivalent
```

- **Nothing in `lsusb`** → the dongle is not enumerating at all. Another USB
  port, another USB cable, then suspect the dongle.
- **Present in `lsusb` but no matching interface in `ip link`** → the driver did
  not bind. `dmesg` says why, usually in the last few lines.
- **`Link detected: no`** → nothing on the other end of the Ethernet cable.
  Check both plugs and swap the cable: cheapest test on the list.

⚠️ **One caveat on `ethtool`, specific to the RTL8153 this lab owns.** Once that
adapter hits its `Stop submitting intr, status -71` fault its register reads are
garbage — it has reported `Link detected: yes` for a link carrying nothing, and
`/sys/class/net/*/carrier` freezes at its last value. **Judge this link by a ping
to the robot, never by `carrier` or `ethtool`.**
[`ot2_link_recover.sh`](ot2_link_recover.sh) exists for that fault; it locates
the adapter by USB ID (`0bda:8153`) rather than by hostname or interface name,
so it should run on any Linux host holding that dongle, the Ubuntu lab computer
included — though it has only ever been exercised on the Pi.

**3. Does *this machine* have a `169.254.x.x` address?** This is the step most
often missed, it is the one that makes a browser show a blank page while the
robot is perfectly healthy, and **on Ubuntu it will not happen by itself.** Both
ends have to be link-local; the robot cannot route to a machine that has no
address on its subnet.

Windows falls back to APIPA when DHCP times out, so on Windows this is a matter
of waiting 60 s. **Ubuntu has no equivalent.** NetworkManager's
`ipv4.link-local` defaults to `default`, which falls through to the global
default of `auto`, and `auto` means *"assign a link-local address only if
`ipv4.method` is itself `link-local`"*
([NetworkManager `ipv4` settings](https://networkmanager.dev/docs/api/latest/settings-ipv4.html)).
A wired connection left on DHCP with nothing serving DHCP therefore ends up with
**no IPv4 address at all**, indefinitely — there is no timer that rescues it.
NetworkManager 1.52 added an `ipv4.link-local=fallback` value that would do the
Windows thing; **Ubuntu 24.04 ships 1.46**, so it is not available here.

So set it explicitly. In the GUI: **Settings → Network → the wired connection's
⚙ → IPv4 → Link-Local Only → Apply**, then toggle that connection off and on.
Or:

```bash
nmcli device status                                    # find the wired device
nmcli -g GENERAL.CONNECTION device show enp0s20u1      # its connection name
sudo nmcli connection modify "Wired connection 1" ipv4.method link-local
sudo nmcli connection up "Wired connection 1"
ip -4 addr show enp0s20u1                              # now shows 169.254.x.x/16
```

**Link-Local Only is better than a hand-picked static address**, because
NetworkManager then runs real IPv4LL: it ARP-probes before claiming an address
and moves off one that collides, which matters on a link where the robot is
self-assigning too. If you would rather pin it anyway — Method **Manual**,
address `169.254.51.100`, netmask `255.255.0.0`, gateway and DNS **blank** — or:

```bash
sudo nmcli connection modify "Wired connection 1" \
    ipv4.method manual ipv4.addresses 169.254.51.100/16 \
    ipv4.gateway "" ipv4.dns ""
```

Leave the gateway blank either way: this link goes nowhere else, and filling it
in can hijack the machine's default route. ⚠️ **Set the connection back with
`sudo nmcli connection modify "Wired connection 1" ipv4.method auto` if that
cable is ever plugged into a real network**, or it will not work there.

On a server-style install using **netplan** with `systemd-networkd` rather than
NetworkManager, the equivalent is `link-local: [ ipv4 ]` on that interface in
`/etc/netplan/*.yaml` followed by `sudo netplan apply`. Ubuntu Desktop uses
NetworkManager, so reach for `nmcli` first — `nmcli device status` printing
something rather than erroring is the quickest way to tell which you have.

**4. Is the robot's address still the one you typed?** It is self-assigned, and
Opentrons warn that it ["will change periodically, especially after the OT-2 is
restarted or reconnected"](https://support.opentrons.com/ot-2/getting-started-software-setup/networking-requirements-for-the-ot-2).
`169.254.51.252` has held across every reconnect on the Pi's cable since
2026-09-09, so it is a good first guess and nothing more. To find the current
one without guessing, use [`find_ot2.sh`](find_ot2.sh), or
`avahi-resolve -n OT2CEP20210722R13.local`, or read *Robot Settings →
Networking* in the app once it is connected by any means.

**5. Suspect the dongle, especially if it came off the Pi.** The Pi's RTL8153
(`0bda:8153`) is a known-bad part here: on 2026-09-23 it collapsed with
`Stop submitting intr, status -71` within 18 s of each repair, and only a hard
port power cycle recovered it. See [`ot2_link_recover.sh`](ot2_link_recover.sh)
and the README. It fails the same way on any Linux host, `r8152` being the same
driver on Ubuntu as on Raspberry Pi OS, so watch for it in `sudo dmesg -w`:

```
r8152 2-1:1.0 enp0s20u1: Stop submitting intr, status -71
```

Move the dongle to a **black USB 2.0 port** rather than a blue USB 3 one —
`-EPROTO` on an RTL8153 at SuperSpeed is the classic signature — or use the
dongle Opentrons shipped with the robot instead. `lsusb -t` shows which speed a
device actually negotiated (`5000M` is USB 3, `480M` is USB 2).

#### Two things that are *not* the cause

- **Prior SSH access does not lock the robot out of the app.** SSH is TCP 22;
  discovery is UDP 5353 and control is HTTP on TCP 31950 — different daemons,
  different ports. The OT-2 has no concept of an exclusive client session, and
  enabling SSH only appends a public key to the robot's `authorized_keys`. The
  proof is in this repo's own history: on 2026-09-23 the app found
  `OT2CEP20210722R13` on a robot that had been SSH'd into for weeks, and HTTP
  calls from the Pi (`/health`, `/pipettes`, `POST /camera/picture`) all returned
  200 during the same period.
- **A greyed-out robot card is not a hardware fault.** The app **caches robots it
  cannot reach**, and *"Robot must be on the network to see connected
  instruments, modules, and peripherals"* is its `offline_instruments_and_modules`
  string — the HTTP API did not answer. It is not reporting that the pipette is
  undetected. Note this is a *different* screen from "No robots found": cached
  robot vs. nothing discovered at all.

Finally, only step 3 needs `sudo`, and none of this changes a setting on the
robot. If it is still stuck, run [`find_ot2.sh`](find_ot2.sh) and keep its whole
output — it records the interface list, the mDNS result and the `/health` result
together, which is what distinguishes these faults from each other after the
fact.

### Putting the robot on Wi-Fi instead

Devices → ⋮ → **Robot Settings** → **Networking**. Opentrons recommend doing
this *while connected by cable*, because changing Wi-Fi over Wi-Fi can strand
the app. It would let the laptop and the Pi coexist without a switch, but it is
not a sure thing here: the lab's wireless is a campus network, and client
isolation on such networks blocks the mDNS the app discovers robots with. The
switch is the more predictable fix.

### Why not just do this over HTTP

Protocol runs do not need the app at all — `run_xscan_test.py` already drives
the robot over HTTP. Calibration is *also* reachable over HTTP: the app writes
it by POSTing `calibration/moveToMaintenancePosition` and
`calibration/calibratePipette` into `/maintenance_runs` (there is no
`POST /calibration/...`; those routes are `get`/`delete` only). What is not
automatable is the loop in the middle — a human jogs the pipette down and
confirms by eye that the tip is touching the deck cross or the calibration
block. Replacing the app means re-implementing its jog UI for a one-off, which
is why the app is the recommended path here rather than a hard requirement.

## Step 1 — deck calibration

Devices → select the OT-2 → ⋮ → **Robot Settings** → **Calibration** →
**Calibrate deck**. Jog the pipette onto the etched crosses; the app walks
through the sequence.

Do this **first and once**. Everything else is downstream of it.

## Steps 2 and 3 — tip length, then pipette offset

Same screen, under **Pipette Offset Calibrations**. The flow asks you to choose
a tip rack first, then measures tip length and pipette offset in one pass.

Use `opentrons_96_tiprack_300ul` — the stock 300 µL rack the protocol uses,
which is also what the P300 is meant to be characterised on. The app is explicit
that calibrating on Opentrons tips matters.

## Step 4 — add the custom labware

Only **one** definition is custom. Left sidebar → **Labware** → **Import**, and
select the `.json` file:

| labware | load name | slot (AC protocol) | custom? |
| --- | --- | --- | --- |
| 96-well plate | `corning_96_wellplate_360ul_flat` | 1 | **no — stock, already on the robot** |
| 300 µL tip rack | `opentrons_96_tiprack_300ul` | 9 | **no — stock** |
| sensor dock | `ac_color_sensor_charging_port` | 10 | **yes** |
| paint reservoir, 6 × 15 mL tubes | `ac_6_tuberack_15000ul` | 3 | yes, *only if the robot dispenses the paint itself* |

The sensor dock is committed here as
[`protocols/ac_color_sensor_charging_port.json`](protocols/ac_color_sensor_charging_port.json)
— import *that* file, since the app's Import screen needs a standalone `.json`
and the copies embedded in the protocol scripts cannot be selected. Both custom
definitions are also upstream in
[`ac-dev-lab/src/ac_training_lab/ot-2/_scripts/`](https://github.com/AccelerationConsortium/ac-dev-lab/tree/main/src/ac_training_lab/ot-2/_scripts).

The tube rack is the **stock-solution reservoir** — six positions for 15 mL
tubes (20 mm bore, 58 mm deep), from which the P300 aspirates red, yellow and
blue out of `B1`/`B2`/`B3`. It is not a measurement target. If you pipette the
paint into the well plate by hand, you do not need it.

## Step 5 — tip length calibration for the sensor dock

**This is the step that is easy to miss.** The sensor dock is declared as a tip
rack:

```json
"parameters": { "loadName": "ac_color_sensor_charging_port",
                "isTiprack": true, "tipLength": 84 }
```

The protocol picks the module up with `p300.pick_up_tip(dock["A2"])`, so as far
as the robot is concerned the module *is* a tip — and **every tip rack a
protocol picks up from needs its own tip length calibration with the attached
pipette.** The app matches on the labware URI, here
`custom_beta/ac_color_sensor_charging_port/1`, which is why a calibration
against the 300 µL rack does not satisfy it.

Once the definition is imported it appears in the calibration flow's tip-rack
picker, under a "custom" group beneath the Opentrons racks. Re-run the pipette
calibration flow and pick it there.

## Step 6 — Labware Position Check

LPC lives inside a protocol. Import the protocol, open its **Setup** tab, expand
**Labware Offsets**, and click **Run Labware Position Check**. Jog the pipette
over each piece of labware in turn and click **Complete**.

Two properties worth knowing:

- An offset is stored against an **exact labware-type-and-slot pair**. Move the
  plate from slot 1 to slot 2 and the offset does not follow it.
- Robot software 6.0.0 and later reuses a stored offset across *different*
  protocols, as long as that labware-and-slot pair matches. So LPC is done once
  per layout, not once per protocol.

## What this does and does not reach

`run_xscan_test.py` drives the robot with `moveToCoordinates` inside a
**maintenance run**, with absolute deck numbers. No labware is loaded on that
path, so **no LPC offset is ever applied to it.** Calibrating in the app pays
off only once the motion half is ported to a real protocol that loads labware
and addresses wells by name.

That port is the point of doing this: `plate["A1"].top(z=-1.3)` is a read height
expressed relative to the well, so it survives a re-calibration or a plate swap
without a code edit — which is what the hand-tuned `--read-z` / `--drop-dx`
constants cannot do.

One more gotcha if any of this is ever run from Jupyter or `opentrons.execute`
rather than the app: **LPC offsets are not applied automatically on that path.**
Read the numbers off the app and pass them to `labware.set_offset(x, y, z)` —
and note `set_offset()` raises at protocol API 2.14–2.17, so request 2.18 or
later.

## Geometry, for the 96-well plate

Stock `corning_96_wellplate_360ul_flat`, version 2: wells 6.86 mm across,
10.67 mm deep, 360 µL, A1 at (14.38, 74.24) within the slot.

The AS7341's roughly ±20° field of view spans about 21 mm at the read heights
used so far, so a 6.86 mm well fills well under half of it. **A per-well blank
is not optional with this plate** — most of what the sensor sees is plate, not
liquid. The upside is that `.top(z=)` puts the aperture a millimetre or two off
the liquid surface with no collision risk, which is exactly what standing vials
made impossible.

## Sources

- [OT-2 robot calibration](https://docs.opentrons.com/ot-2/calibration/robot-calibration/)
- [OT-2 labware offsets](https://docs.opentrons.com/ot-2/calibration/labware-offsets/)
- [Using Labware Position Check](https://docs.opentrons.com/v2/robot_position.html#using-labware-position-check)
- [Custom labware](https://docs.opentrons.com/v2/new_labware.html#custom-labware) · [Labware Creator](https://labware.opentrons.com/create/) · [Labware Library](https://labware.opentrons.com/)
- [Connect to the OT-2 over USB](https://support.opentrons.com/s/article/Get-started-Connect-to-your-OT-2-over-USB) · [Connect over Wi-Fi](https://support.opentrons.com/s/article/Get-started-Connect-to-your-OT-2-over-Wi-Fi-optional)
- Ubuntu side: [NetworkManager `ipv4` settings](https://networkmanager.dev/docs/api/latest/settings-ipv4.html) (`link-local` defaults to `auto`, i.e. off unless `method=link-local`; `fallback` only since 1.52) · [AppImage and FUSE](https://docs.appimage.org/user-guide/troubleshooting/fuse.html) (type 2 needs FUSE 2; `libfuse2` → `libfuse2t64` in 24.04) · [`node-mdns-js/lib/networking.js`](https://github.com/mdns-js/node-mdns-js/blob/master/lib/networking.js) (`reuseAddr: true`, so it shares 5353 with `avahi-daemon`)
- Discovery source: [`mdns-browser/index.ts`](https://github.com/Opentrons/opentrons/blob/edge/discovery-client/src/mdns-browser/index.ts) (`QUERY_INTERVAL_MS` backoff, `IFACE_POLL_INTERVAL_MS`, port filter) · [`repeat-call.ts`](https://github.com/Opentrons/opentrons/blob/edge/discovery-client/src/mdns-browser/repeat-call.ts) (the interval array holds its last value) · [`interfaces.ts`](https://github.com/Opentrons/opentrons/blob/edge/discovery-client/src/mdns-browser/interfaces.ts) (`{name, address}` comparison) · [`base-browser.ts`](https://github.com/Opentrons/opentrons/blob/edge/discovery-client/src/mdns-browser/base-browser.ts) (`createBrowser(tcp('http'))`)
- App source: [`useRunPipetteInfoByMount.ts`](https://github.com/Opentrons/opentrons/blob/edge/app/src/resources/runs/useRunPipetteInfoByMount.ts) (tip-length cal is matched per tiprack URI × pipette serial) · [`ChooseTipRack.tsx`](https://github.com/Opentrons/opentrons/blob/edge/app/src/organisms/Desktop/CalibrationPanels/ChooseTipRack.tsx) (custom tip racks are concatenated into the picker)
