# 2026-09-26 — the Pi is back and healthy; the trio did not run, because the gantry was recalibrated (and apparently moved) since 09-24

> **Superseded the same evening.** Ben recalibrated again (391 / 236.665 / 124)
> and sent the new gantry and deck files. §2's "what is needed" is done, and
> the gantry file now matches the controller. The trio fails validation on two
> new numbers. See [`../pipette_test_20260926b/`](../pipette_test_20260926b/README.md).

Asked for: *"run the trio quickly as well. I want to make sure the Pi is online
and everything is working correctly (note that the ports might have switched,
I am unsure)"*

**No motion was commanded.** Everything below is a read-only check. The trio
was not sent to the machine, for the reason in §2.

| check | result |
|---|---|
| Pi | ✅ online. Booted 2026-09-25 17:36:59 lab-local. `throttled=0x0`, so no undervoltage or throttling since boot: the repaired USB-C input is supplying clean power, at least at idle |
| serial ports | ✅ **unchanged**: GRBL (CH340 `1a86:7523`) on `/dev/ttyUSB0`, capper + pipette Arduino (Uno `2341:0043`, serial `…018130`) on `/dev/ttyACM0`. Both free, no process holding either |
| Arduino link | ✅ `PawduinoLink.connect()` in 3.77 s. `STATUS` 5/5 clean. Cap sensor `value1: 0` (nothing held). `CMD_EMAG_OFF` acknowledged |
| firmware | ✅ `panda_vcl_p20gen2_20260917.hex`, **17382 bytes of flash verified** (`avrdude -U flash:v:`, read-only; sha256 matches the repo) |
| `CMD 29` | `comm = 0` ×3, unchanged. The bridge resistor is still the blocker (see the 09-24 write-up) |
| GRBL | `Alarm`, no `Pn:` field, `$20=1`. 🔴 **`$130/$131/$132` and `G54` rewritten** (§1) |
| cameras | ⚠️ **1 of 2 detected** (§4) |
| offline gates | ✅ `validate_setup` PASS · `--mock` 12/12 · `passive_shadow` 0 nominal, 0 tip-stuck. These check the files against each other, not against the controller or the deck |
| **the trio** | ⛔ **not run** (§2) |

## 1. The controller was recalibrated

Read live, twice, before anything else (`grbl_settings_20260926.json`,
`grbl_offsets_20260926.txt`):

| | committed gantry file · last read 09-24 | **controller now** | change |
|---|---|---|---|
| `$130` `max_travel_x` | 409.000 | **410.000** | +1.000 |
| `$131` `max_travel_y` | 309.000 | **281.000** | **−28.000** |
| `$132` `max_travel_z` | 124.000 | **125.003** | +1.003 |
| `G54` | −409, −309, −124 | **−410, −281, −125.003** | |

Every other setting is unchanged (`$20=1 $21=0 $22=1 $23=0 $27=3 $100–$102=400`),
and the build is the same (`1.1h.20190825`), so this is the same board with its
travel extents and work offset rewritten together. That is what a calibration
pass does. `125.003` is a measured value, not a typed one.

It was **not** done by this Pi's CubOS. `~/.cubos/logs/gantry/` ends with the
cut run on 2026-09-24 16:17 lab-local, still reading 409/309/124. Nothing in
the home directory had changed since boot (caches and venvs excluded) before
this session's checks. The GRBL USB first appeared on this
boot at 17:59 lab-local, 22 minutes after the Pi came up. So the recalibration
was done from another computer, or before the controller was plugged back into
the Pi.

## 2. Why that stops the trio

**CubOS refuses to run it as committed.** `Gantry._validate_grbl_settings` at
`496819c` treats `$3 $20 $22 $23 $100–$102 $130 $131 $132` as critical, compared
at 0.001 mm. The gantry file still expects 409/309/124, so `run_protocol` would
abort at connect with *"Critical GRBL settings mismatch"* before any G-code is
sent. It would also run the pipette `HOME` seek twice (about 53 s) on the way,
because instruments connect before the gantry.

**Changing those three numbers to match the controller is the wrong fix.** The
deck file's coordinates are jog readings (WPos) in the old frame, and
`WCO = −max_travel` on every axis. So if the homing switches have not moved
relative to the deck, the same physical point now reads:

```
new reading = old reading + (+1.000, -28.000, +1.003)
```

In practice that means:

- **vial_1's old physical position is outside the machine's new Y travel.**
  Capper-frame (206, 27) now reads (207, **−1**). Y is now [0, 281] in work
  coordinates.
- **Running the committed deck in the new frame is a collision.** A capper
  target of (206, 27) lands physically at old-frame (205, 55). That is 5 mm off
  **vial_2's** axis, inside its 28 mm footprint, engaging 1 mm deeper than
  intended. The capper would engage the wrong vial off-centre, and the aspirate
  "into vial_1" would then put the 35 mm tip down into, or onto, vial_2.
- **The switches may not have stayed put at all.** The camera frame
  (`frames/deck_now__cam0_csi0.jpg`) shows **wood** under the acrylic deck
  plate, where every earlier frame shows the grey speckled bench. The machine
  appears to have been moved to a different table. So the positions need
  **re-jogging, not converting**.

`validate_setup` passes either way. It checks that a coordinate is reachable,
never that it is the right one.

### What is needed to run it

1. **The updated gantry file** from whoever recalibrated, or the
   `$130/$131/$132` above plus anything else that changed (for example
   `working_volume`, and `safe_z` if the Z range moved).
2. **The deck re-measured in the new frame.** Either the updated deck file, or
   jog readings for:
   - vial_1 and vial_2 centres with the capper (the display reads the capper
     frame, so no conversion is needed);
   - tip-rack A1 with the pipette hovering over it (converted by the
     pipette↔capper offset, (+52, +12), as before);
   - the cap engage Z.

Then the gantry file's travel values get synced in the same edit, and the trio
runs. Until then, the settings mismatch is the only thing standing between a
stale deck and real motion, so it was deliberately left in place.

### Why no standalone `$H`

Homing does not depend on the frame, and it would have confirmed that the gantry
has power and working switches. It was not done. `run_protocol` itself would
never have reached its `home` step (connect fails first). The machine is on a
new bench, where the Pi's power-cable routing is unknown, and on 09-24 exactly
that cable was pulled out, which damaged the Pi's USB-C input. Homing drives to
the far corner. Say *"home it"* to do only that, or send the files and the trio
homes as step 0.

## 3. Ports: unchanged, but the stable names are the `by-id` ones

```
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0                               -> ttyUSB0  (GRBL)
/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00  -> ttyACM0  (capper + pipette)
```

The gantry file names `/dev/ttyUSB0` and `/dev/ttyACM0`. Those are assigned in
enumeration order, so they are the names that *can* swap. The `by-id` paths
cannot. Worth switching when the file is next edited for the new calibration,
with one constraint: **the capper and the pipette must name the identical
string.** `PawduinoLink.acquire` keys its shared link on the raw port string
(`_registry.get(port)`, no path resolution). One `by-id` and one `ttyACM0` would
open the Arduino twice, and the second open resets the board mid-session.

## 4. Cameras: one of two

`rpicam-still --list-cameras` finds a single `imx708_wide` (at `i2c@80000`), and
the kernel probed only one sensor at boot. Its view is not the view any earlier
`cam0` frame has. The second camera needs its CSI ribbon reseated **with the Pi
powered off**, then a boot: CSI sensors are probed at boot, not hot-plugged. The
frame committed here contains no people, so it is committed uncropped.

## 5. Machine state, untouched

| | |
|---|---|
| motion | **none commanded**: no homing, no G-code, no plunger command |
| GRBL | port opened twice for `?`, `$$`, `$#` and `$I`. Each open resets the board, which was already in `Alarm` |
| Arduino | opened for the reads above and `CMD_EMAG_OFF`, then an `avrdude` **verify** (read-only; it also resets the board) |
| `$20` | `1` |
| anything written | nothing, on either board or on the Pi |

## Files

| file | what |
|---|---|
| `pi_health.txt` | uptime, `get_throttled`, `by-id`, `lsusb`, USB events since boot, cameras, CubOS tree |
| `grbl_settings_20260926.json` | banner, four status reads, the full `$$` |
| `grbl_offsets_20260926.txt` | `$#` (G54–G59, G28, G30, G92) and `$I` |
| `arduino_and_flash.txt` | link probe, `CMD 29` ×3, `CMD_EMAG_OFF`, the flash verify |
| `validate.log` `mock.log` `shadow.log` `shadow_ts.log` | the four offline gates, on the Pi, against the committed trio (byte-identical to this branch) |
| `frames/deck_now__cam0_csi0.jpg` | the one camera, as it sees the deck now |
