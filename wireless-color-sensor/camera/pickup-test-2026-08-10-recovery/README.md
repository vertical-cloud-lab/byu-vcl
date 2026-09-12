# Recovery: interrupted 2026-08-10 cycle completed — module reseated

Follow-up to
[`pickup-test-2026-08-10-sensor-read-midair/`](../pickup-test-2026-08-10-sensor-read-midair/),
which ended with the sensor module still gripped on the P300 nozzle at
(169.05, 225.0, 110) because the RPi-5 (the OT-2's only network bridge)
dropped offline before the return leg. Triggered by @timothy-commins on PR
#60 after he restored the OT-2's USB connection.

## State found at session start

- The RPi-5 was back on the tailnet (rebooted ~20 min earlier, on BYU Wi-Fi
  with working internet), **but the OT-2 was unreachable**: no `eth1`
  interface existed even though the USB cable was connected — see the
  troubleshooting section below.
- After restoring the link: `savePosition` returned **exactly**
  (169.05, 225.0, 110.0) — the gantry had not moved since the interruption —
  and the camera frame `01_before_module_still_gripped_z110.jpg` shows the
  crown still engaged on the nozzle with the module hanging above its base.
  So despite the earlier report, the module had **not** yet been returned;
  the interrupted cycle was still pending, ~95 min after the outage (the
  interference fit held the whole time, as in every prior dwell test).
- The stale maintenance run `84e56185` from the interrupted session was still
  current on the robot.

## What ran

[`cad/recover_reseat.py`](../../cad/recover_reseat.py), executed from the
RPi-5, exactly as written — position pre-check passed with 0.0 mm offset:

```
current nozzle position: x=169.05 y=225.00 z=110.00
lateral shift to drop x=163.05 at z=110.0
staged descent z 108 -> 101 -> 95.5
dropTipInPlace
clearance retreat to z=128, home
maintenance run deleted
```

`02_after_module_reseated_gantry_homed.jpg` confirms the module is seated
back on its slot-8 base with the crown free, the gantry homed away, and the
overhead wire intact. No maintenance run is left on the robot (the stale one
was superseded and the new one deleted). **The wire-attached recipe is now
7-for-7 on completed reseats.**

## Troubleshooting: OT-2 unreachable with the USB cable connected

Root cause: the OT-2's USB-Ethernet bridge (Realtek RTL8153) had enumerated
in its fake **"driver CD-ROM" mode** — it showed up as `0bda:8151`, a USB
mass-storage device presenting a virtual Windows-driver CD, instead of
`0bda:8153`, the NIC. In that mode no `eth1` exists, so the `ot2-usb`
NetworkManager profile has nothing to attach to. This can happen after a
reboot or replug. The fix (run on the RPi-5):

```bash
sudo apt-get install -y usb-modeswitch     # one-time
sudo usb_modeswitch -v 0bda -p 8151 -K -R  # eject virtual CD + USB reset
```

The device re-enumerates as `0bda:8153`, the `r8152` driver binds, `eth1`
comes up, and the existing `ot2-usb` link-local profile connects — the robot
answers at `http://169.254.51.252:31950` again.

**Made persistent on the RPi-5** (recorded here because Pi changes don't live
in this repo): `usb-modeswitch` is now installed, and
`/etc/udev/rules.d/40-ot2-usb-ethernet-cdrom-fix.rules` runs the switch
automatically whenever a `0bda:8151` device appears:

```
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0bda", ATTR{idProduct}=="8151", RUN+="/usr/sbin/usb_modeswitch -v 0bda -p 8151 -K -R"
```

## Connectivity model (confirmed)

The RPi-5 needs exactly two links, and neither involves the Windows computer:

1. **Wi-Fi** (BYU network) → internet + tailnet. Verified working; the Pi
   does not need to tether through a computer for internet.
2. **USB** → OT-2 (appears as the RTL8153 NIC above, link-local addressing).

The Windows box is only needed if the OT-2's USB cable is physically plugged
into it instead of the Pi — in which case the Pi path is down and vice versa.
