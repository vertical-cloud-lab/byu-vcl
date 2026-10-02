# jog_test_20261002

Requested by @benwhitney5463 on [#165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165)
after he unplugged and replugged everything on the CubXL: a picture from both
cameras, then −200 mm X, −200 mm Y and +175 mm X with pictures after each, then home.
**No Z motion at all.**

✅ **All three jogs ran, with pictures before and after each. Z never moved.** Every
one of the 157 GRBL status reports in [`grbl.log`](grbl.log) has Z at 125.000, and no
limit switch tripped (no `Pn:`).

⚠️ **The machine was not homed.** GRBL's `$H` homes Z first and this firmware has no
X-only or Y-only homing (`[OPT:V,15,128]`, no `H`), so any homing cycle would have
moved Z. X and Y were jogged back to where they started instead.

## What ran

2026-10-02, 21:52:57–21:59:00 UTC (15:52–15:59 MDT). Jogs used `$J=G91 G21 <axis><mm> F1000`
(a third of the protocols' F3000). X and Y were the only axes ever sent.

| request | GRBL `WPos` after | position on the deck* | pictures |
|---|---|---|---|
| unlock (`$X`) | 364, 281, 125 | 361, 278, 122 | [`00_before`](frames/00_before__cam0_csi0.jpg) ([cam1](frames/00_before__cam1_csi1.jpg)) |
| X −10 (probe) | 354, 281, 125 | 351, 278, 122 | [`probe_x-10`](frames/probe_x-10__cam0_csi0.jpg) ([cam1](frames/probe_x-10__cam1_csi1.jpg)) |
| X −190 | 164, 281, 125 | 161, 278, 122 | [`01_after_x-200`](frames/01_after_x-200__cam0_csi0.jpg) ([cam1](frames/01_after_x-200__cam1_csi1.jpg)) |
| Y −10 (probe) | 164, 271, 125 | 161, 268, 122 | [`probe_y-10`](frames/probe_y-10__cam0_csi0.jpg) ([cam1](frames/probe_y-10__cam1_csi1.jpg)) |
| Y −190 | 164, 81, 125 | 161, 78, 122 | [`02_after_y-200`](frames/02_after_y-200__cam0_csi0.jpg) ([cam1](frames/02_after_y-200__cam1_csi1.jpg)) |
| X +175 | 339, 81, 125 | 336, 78, 122 | [`03_after_x+175`](frames/03_after_x+175__cam0_csi0.jpg) ([cam1](frames/03_after_x+175__cam1_csi1.jpg)) |
| X +25, then Y +200 (back to start) | 364, 281, 125 | 361, 278, 122 | [`04_back_at_start`](frames/04_back_at_start__cam0_csi0.jpg) ([cam1](frames/04_back_at_start__cam1_csi1.jpg)) |

\* GRBL's counter was zeroed where the head stood when the board powered up. That was
the homed pose, 3 mm short of each limit switch, so the true position is the reported
one minus 3 mm on every axis. It matches `working_volume` max (361, 278, 122) in
today's `cub_xl_ben_3_instrument.yaml`.

Each 200 mm move was split into 10 mm + 190 mm, and the pictures were checked between
the two parts. This confirms that each motor still drives the axis and direction it
should after the replug. −X moved the head away from the right-hand rail and −Y moved
it toward the capped vials at the front of the deck. The −Y probe showed no sign of
racking.

## Why `$X` and a jog were acceptable here

The lab's rule since a Y overrun on 2026-09-18: once the position is lost, re-home, and
never `$X` and jog away from the homed corner
([pipette thread](../../docs/pipette-thread/04-firmware-and-p20-gen2.md),
[troubleshooting](../../docs/pipette-setup-and-troubleshooting.md)). GRBL's counter was
meaningless after the power cycle, and `$H` was ruled out by the no-Z rule. The jogs went ahead because the head's real position was known from two
independent sources:

- **The run record.** Campaign 98 (`~/cubxl_runs/pipette_test_20261002c` on the Pi) ended
  with `$H` at 14:07:37 MDT ("Homing completed"). CubOS's gantry log has nothing after
  it, and the 15:23 MDT session on #165 only took a picture.
- **The before pictures.** The head (the silver Z housing with the capper's black
  electromagnet) sits against the right-hand rail, at the back end of the deck. That is
  +X and +Y, the corner `$23=0` homes to.

From that corner the requested moves leave at least 78 mm to the −Y end and 161 mm to
the −X end. The settings check in [`tools/grbl_xy.py`](tools/grbl_xy.py) also refused to
unlock unless `$20=1` (soft limits), `$21=1` (hard limits), `$22=1`, `$23=0`, steps/mm and
travel all matched the gantry file. It halted motion if Z ever changed.

## Findings

- **GRBL travel and G54 changed since the committed gantry file.** They are now `$130`–`$132`
  = 364 / 281 / 125 and G54 = −364, −281, −125, up from 391 / 236.665 / 124. They match
  `cub_xl_ben_3_instrument.yaml` in the Pi's `~/byu-vcl-pipette` checkout (`021ad70`), not
  [`configs/gantry/cub_xl_ben_pipette_capper.yaml`](../../configs/gantry/cub_xl_ben_pipette_capper.yaml).
  The first open used the old expectations and refused to unlock
  ([`grbl_first_open.log`](grbl_first_open.log)). Nothing was written to EEPROM.
- **Both cameras are detected again** after the restart, both `imx708_wide` (Camera
  Module 3 Wide). `rpicam` index 0 is CAM/DISP 0 (I²C bus 10, `csi@110000`). Index 1 is
  CAM/DISP 1 (I²C bus 11, `csi@128000`), the camera from 2026-10-01.
- **Both cameras move with the head.** Every jog moved the whole scene in both pictures.
  - cam0 sees the whole deck only while the head is parked at the homed corner.
  - cam1 sits beside the capper's electromagnet.
  - cam1's last picture lines up with its first within the 4 px resolution of the check
    (phase correlation), so the head came back to where it started.
  - cam0's last picture is about 45 px lower than its first, which is about 2° of tilt.
    Its view also dropped about 30 px during the 10 mm X probe, which should only have
    shifted it sideways. Its mount flexes when the head moves.
- **The `deckcam` live view now shows CAM/DISP 0.** `deckcam.py` does not pass `--camera`,
  so `rpicam-vid` opens index 0. That index belonged to the CAM/DISP 1 camera while it was
  the only one connected.

## State left behind

- GRBL is `Idle`, unlocked and **not homed**. Its counter matches the head (the start
  pose), but nothing has re-referenced it.
- The next program to open the port resets the board back to `Alarm`. The next protocol's
  step 0 `$H` will then move Z: up about 3 mm to its switch and back.
- The port was closed at 21:59:41 UTC and nothing holds it. The pipette, the capper and
  the Tic were not touched.
- Nothing persistent was changed on the Pi. The working files in `/tmp` were deleted.

## Files

- `frames/` holds one 2304 × 1296 still per camera per step. The `.json` files are the
  `rpicam-still --metadata` dumps (exposure 40–50 ms at gain 2.0–2.8, autofocus on).
- `grbl.log` is every request, command, reply and status report, in UTC.
- `grbl_before.json` is `$I`, `$$`, `$#` and `?` at the open used for the jogs.
  `grbl_first_open.*` is the first open, which refused to unlock.
- `cmds.txt` lists the requests in the order they were sent.
- `tools/` has the scripts that ran:
  - `grbl_xy.py` holds the port open, because each open resets the board. It accepts X/Y
    jogs only.
  - `req.sh` sends one request and waits for its result.
  - `cap.sh` takes one still per camera.
