# Security cameras instead of the Pi HQ/Wide units (#303)

Sterling (PR #318, 2026-11-20): "Considering a swap to mostly or all security cameras (with lots of adjustability in
terms of angle, resolution, night vision, onboard temperature/humidity logging, etc.) with a Pi 5 handling the
streaming and control (similar to borysgroup/aurora-cloud-infra PR 35, but doesn't have to be that brand, and I also
need an approximate cost here) ... Note that for a security camera, the power requirements might be higher than what a
typical Pi 5 charger would handle." And for the bay: "two side-by-side, one focused on wide capture and another that
could point closely at whatever workflow is happening. Keeping in mind also that there would be a gripper camera too",
"multiple overhead cameras in the bay to get different angles (e.g., ceiling middle back, ceiling middle front)".

This is research and a recommendation. The Pi camera units in `services.py` and every animation in PR #318 are
unchanged. [`security_cams.py`](../security_cams.py) does the geometry, the power and the cost;
[`out/security_cameras.json`](../out/security_cameras.json) has every number below.

<!-- SUMMARY -->

## What aurora's rig already showed (borysgroup/aurora-cloud-infra PR 35)

Two Amcrest **IP5M-T1179EW-AI-V3** turrets (5 MP, Dahua OEM) in the Aurora glovebox stream to YouTube through a Pi 5
on the same switch, since 2026-11-19:

- **The Pi 5 only copies the streams.** `ffmpeg` pulls each camera's H.264 over RTSP (TCP) and writes it to YouTube's
  ingest with `-c:v copy`: no decode, no encode, **about 3 % of one core per camera**. Each 1080p, 20 fps, 4 Mbit/s
  CBR stream with a 2 s GOP comes in at 4.2 Mbit/s and goes out at 5.7 Mbit/s over RTMPS.
- **The cameras have no way out.** They sit on a segment with no DHCP and a dead gateway; the Pi's `eth0` has a fixed
  address there, no gateway and `ip_forward` 0. The Pi serves them NTP (their clocks were an hour and two minutes
  off). A `relay` viewer account, not admin, holds the RTSP login.
- **ONVIF Profile S answers** (media, imaging, events), so stream URIs can be discovered once logged in.
- **Its limits:** a fixed lens (no zoom, no motorized focus, no PTZ: re-aiming is by hand), and a privacy blur that
  needs the Pi to decode and re-encode: 0.8-1.3 cores per 1080p stream at 20 fps. Cropping or masking in the
  camera, before it encodes, keeps the copy relay.

So the pattern carries over as is: **one Pi 5 per group of cameras, not one per camera.** A tray's two or three
cameras are under a tenth of one core.

<!-- CANDIDATES -->

## The bay

### Where a camera can go

- **A roof at the opening's clear height leaves 95.5 mm.** The presented tray's floor is at 857 mm. Kardex's goods
  envelope with its 20 mm clearance tops out at 1733.5 mm; the 996 mm opening's 856.5 mm product height is itself an
  estimate (`vlm.py`). The header's underside, where the bay's side walls and the LED light stop, is at 1829 mm. A
  camera hung from a roof there, anywhere over the tray, has 95.5 mm before the tallest goods would reach it. The
  HQ/Wide bay unit sits higher only because the model draws the bay open up to tray F1 (1950 mm).
- **The front strip is free of goods.** A tray slides in from the shaft and stops with its front edge at
  y = -1462 mm. So the 110 mm strip from there to the front of the LED light (y = -1572 mm) is never swept by
  anything on a tray. A taller camera can hang there, limited only by the arm and the operator: that is where a PTZ
  goes.
- **The sides are no use.** The bay's walls stand 25 mm outside the tray, and the shutter's path takes the back.
- **The UR10e** (`services.bay_arm_clearance`'s 320 poses: the workflow's seats and the presented tray on a 100 mm
  grid, gripper down at 100 and 250 mm; the arm as 75 mm capsules from the shoulder to the TCP). Reaching the tray's
  front half, its elbow rises to 1.56-1.57 m just in front of the opening:

  | A camera there | Lowest point | Nearest the arm |
  |---|---|---|
  | Ø130 x 180 mm (a PTZ), front strip, x = 0 | 1649 mm | 17 mm |
  | the same, x = 170 mm | 1649 mm | 31 mm |
  | the same, x = 650 mm | 1649 mm | 137 mm |
  | Ø110 x 100 mm (a turret), front strip, x = 450 mm | 1729 mm | 171 mm |
  | Ø110 x 95 mm, the roof's middle back (y = -645) | 1734 mm | 281 mm |
  | Ø110 x 95 mm, the roof's middle (y = -1030) | 1734 mm | 236 mm |

  So the front pair stands right of the middle, at x = 450 and 650 mm.

<!-- BAY -->

## On the trays

<!-- TRAYS_INTRO -->

### Slot height: the trays' real limit

Kardex's 856.5 mm product height is nowhere near a camera on a tray: the HQ/Wide heads top out at 706 mm. What a
camera does decide is **each tray's slot**, since a slot is the tray's tallest top plus 20 mm, rounded up to 25 mm
(`vlm.py`, `setup_lab.py fit`). The camera heads are the tallest thing on seven of the twelve powered trays:

<!-- BEGIN:HEADROOM_TABLE -->
<!-- END:HEADROOM_TABLE -->

So a camera that replaces a head on the same post, aimed at the same point, must keep its top within 2 mm (tray E) to
25 mm (A, D, F) of today's heads, or that tray's slot grows by a 25 mm step. The other way round, **small cameras set
at or below their tray's tallest instrument would free 425 mm of slot height** across A, C, F, G, I and L (the last
column), more than half a tray slot; that is a reason to prefer the small ones and the module-side mounts.

<!-- BEGIN:POSTFIT_TABLE -->
<!-- END:POSTFIT_TABLE -->

![Each candidate to scale under the bay's roof and on a tray post](../out/security_cameras_fit.png)

### Mounting: tray, module top, module side, bay ceiling

<!-- MOUNTING -->

### Seeing in the dark

The trays spend most of their time in their slots, unlit, and some keep working there: the printers (C, G), the
CubXL (A), the furnace (F). The HQ/Wide units see nothing there (the Wide has an IR-cut filter and neither has a light).
Every security camera here has infrared LEDs and switches to night mode by itself, so a tray in its slot can still be
watched. Keep IR off in the lit bay and near anything optical (the colour sensor's NIR channel on the OT-2's tray, the
OpenFlexures on D): ONVIF's imaging service, or the camera's own day/night schedule, holds it off.

### Temperature and humidity

<!-- TH -->

## Power

### What a camera draws

IEEE 802.3 sets the classes; a camera's class is what the switch reserves for it unless the switch allocates by
measured draw.

| Class | Standard | At the switch (PSE) | At the camera (PD) |
|---|---|---|---|
| 1 | 802.3af | 4.0 W | 3.84 W |
| 2 | 802.3af | 7.0 W | 6.49 W |
| 3 | 802.3af | 15.4 W | 12.95 W |
| 4 | 802.3at (PoE+) | 30 W | 25.5 W |
| 5-6 | 802.3bt (PoE++) | 45-60 W | 40-51 W |
| 7-8 | 802.3bt | 75-90 W | 62-71.3 W |

<!-- POWER_CAMS -->

### The Pi 5 doesn't power them

A Pi 5 takes 5 V at up to 5 A on its USB-C (the 27 W supply) and gives out nothing a camera can use: it has no PoE
output, and its USB ports share 1.6 A. Every camera here wants PoE (or 12 V DC). So the cameras hang off a **PoE
switch**, and the Pi 5 is just another device on it, on its own 27 W supply or on a PoE+ HAT from the same switch.

### Through the tray's dock

Nothing changes at the CombiTac. The dock brings 208Y/120 V (L1, L2, N, PE on Ø3 mm contacts, 39 A; a 30 A breaker)
and one Ethernet line (the CT-10GBIT-RJ45 module, Cat 6A, 10 Gbit/s). PoE is made **on the tray**, by the tray's own
switch, which `ups.py` already puts on every powered tray's UPS-backed branch (a Ubiquiti USW-Lite-8-PoE-class switch:
8 W typical, 60 W rated, a 52 W PoE budget on four PoE+ ports). So:

- **no PoE crosses the dock**, and nothing new does: the cameras need only the 120 V branch and the one data line;
- **the cameras ride through a transit** (6-8 s off the dock) and a stranded tray (the UPS's 10 minutes and more),
  as the HQ/Wide units do; only the uplink drops, so the YouTube stream stalls for the transit and the relay picks it
  up again. A camera's own microSD card (edge recording, ONVIF Profile G) keeps the footage across the gap;
- **the tray's switch must be managed**, with a camera VLAN that has no gateway (aurora's isolation), since the
  same switch carries the tray's instruments and PCs to the lab network.

<!-- POWER_TRAYS -->

### The bay

The bay's cameras are on the machine, not a tray. `notes/services.md` already has a PoE+ switch on the VLM's side that
feeds the service risers and the bay camera; the bay's set and its Pi 5 go on that switch.

<!-- POWER_BAY -->

## Streaming and control on the Pi 5

- **One Pi 5 per powered tray and one per bay**, each relaying its cameras with `ffmpeg -c:v copy` as aurora does
  (`amcrest_relay.py`'s pattern: probe the camera, ask the picam Lambda for a broadcast, copy, restart on stall, end the
  broadcast before YouTube's 12 h archive limit).
- **H.264 on the main stream.** The Pi 5 has a hardware HEVC decoder and no H.264 encoder or decoder, so anything that
  isn't a straight copy costs CPU (aurora: 0.54 cores to re-encode 720p20). Set each camera's main stream to H.264,
  CBR, a 2 s GOP, at the resolution YouTube is to get; keep H.265 for local recording if wanted.
- **Masks in the camera.** Every candidate below has privacy masks applied before its encoder, so the cameras that
  see the room (the bay's middle back unit; a few tray units) need no blur on the Pi.
- **The PTZ's control is ONVIF.** A small service on the bay's Pi (python-onvif-zeep, or the camera's own HTTP API)
  moves it to a preset per workflow seat when the arm is about to work there; the workflow already knows the seat
  (`reach.seats`). Presets avoid closed-loop tracking; a wrist camera (the D405) gives the arm's own view anyway.
- **Isolation as in aurora:** cameras on a VLAN with no gateway; P2P, cloud, UPnP and the vendor app off; NTP from the
  Pi; a viewer account for RTSP and the admin login kept off the Pi; firmware loaded by hand.

<!-- BOM -->

## Open questions

**Kardex** (to add to PR #331's questions for the dealer):
1. Is there a roof over the access opening, and at what height? This note assumes 1829 mm, the 996 mm opening's top.
   May cameras be fixed to it and to the header's underside (M6 rivnuts or a strip), and can the LED light under the
   header be split for the front pair? Where may a camera's Cat 6 run to the side cavity?
2. The largest product height through the 996 mm opening. 856.5 mm is our estimate; the band is 95.5 mm only if it
   holds.
3. Is anything in the front strip under the header (a light curtain, a height check, a sensor), which would decide
   between the strip and the roof for the PTZ?

**The camera makers** (for each model on the shortlist):
1. The minimum focus distance at the long end of the zoom. The bay's PTZ works at 0.79-1.14 m from the workflow's
   seats, and most PTZ makers publish none.
2. The PoE class and the maximum draw with IR on and IR off; whether IR can be held off for good.
3. ONVIF PTZ: absolute moves and presets, how repeatable a preset is, and how fast.
4. Does it run with no cloud account or app ever, with P2P and UPnP off, and take firmware from a file?
5. H.264 main stream at its full resolution, CBR, a 2 s GOP: what the copy relay needs.
6. A US NDAA Section 889 / 2 CFR 200.216 statement, for anything bought on federal grant money.
7. A low ceiling or in-ceiling mount that keeps a turret within 95 mm of the roof.

**BYU:**
1. Will the cameras be bought on a federal grant (the ONR YIP, say)? Then 2 CFR 200.216 rules out anything Hikvision
   or Dahua made, including their OEM brands.
2. Does OIT allow IP cameras on a lab VLAN with no gateway and a Pi 5 as the only way out, as aurora does? Is there a
   campus policy on cameras that can see people (the bay's middle back unit sees the floor in front of the opening)?

**Ubiquiti** (or whichever switch): does the USW-Lite-8-PoE reserve a port's class or allocate by measured draw? With
class reservation, three class-3 cameras (46 W) and a PoE+ Pi (30 W) would be over its 52 W budget even though they
draw a third of it.

## Caveats

- **Many figures are search snippets or retailer pages**, marked so in `CANDIDATES` (`kind`); prices are what one
  retailer showed on the date given, before tax and shipping, and move often.
- **The lenses are drawn rectilinear.** A 2.8 mm security lens has strong barrel distortion (aurora measured it), so
  its published angle is the distorted picture's; coverage at the corners is a little different from what's computed.
- **Nothing occludes.** Coverage counts every point of the tray's floor in the picture, whatever stands in front of it;
  the instruments, the arm and the goods hide some of it.
- **The arm check is reach.py's poses only**, as `services.bay_arm_clearance`: the chapters' own paths between poses,
  and the mobile manipulator's own cameras (another PR), aren't checked.
- **Typical draws are ours** where a maker gives only a maximum (70 % of it, IR off), and so is the 88 % PoE
  efficiency.
- **The roof is assumed.** If Kardex's roof is higher than 1829 mm, the band grows (up to 216.5 mm under tray F1's
  1950 mm in today's tray plan, less the roof's own depth) and a PTZ could hang over the tray too.
