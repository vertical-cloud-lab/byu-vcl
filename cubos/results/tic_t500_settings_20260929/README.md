# Tic T500: the three STEP/DIR settings applied, 2026-09-29

Bring-up step 1 of [`tic-t500-pipette-setup.md`](../../docs/tic-t500-pipette-setup.md):
USB only, no 12 V, apply the three settings. Done from the CubXL Pi over the
Tic's USB, at Ben's request after he plugged the Tic into the Pi.

Nothing moved. No gantry command was sent, no plunger command was sent, and
the Arduino was not opened. The only thing written was the Tic's own settings
memory.

## The device

| | |
| --- | --- |
| model | Tic T500 (`1ffb:00bd`) |
| serial number | `00510573` |
| firmware | 1.09 |
| USB interfaces | one, vendor-specific. The Tic has **no USB serial port**, so it adds no `/dev/ttyACM*` device |
| VIN during the change | **0.051 V**: 12 V was off, as step 1 requires |

The Pi had rebooted at 21:47 UTC. The Tic enumerated as `usb 1-1` before the
Arduino (`usb 1-2`), and the Arduino still came up as `/dev/ttyACM0`, with GRBL
on `/dev/ttyUSB0`. The `by-id` paths are unchanged.

## What changed

Three lines, and nothing else:

```
$ diff before_settings.txt after_settings.txt
4c4
< control_mode: serial
---
> control_mode: step_dir
45,46c45,46
< step_mode: 1
< current_limit: 174
---
> step_mode: 8
> current_limit: 990
```

| setting | before (factory) | after | read back in `--status` |
| --- | --- | --- | --- |
| control mode | Serial / I²C / USB | **STEP/DIR** | — (settings file: `step_dir`) |
| step mode | full step | **1/8** | `Step mode: 1/8 step` |
| current limit | 174 mA (code 2) | **990 mA** (code 8) | `Current limit: 990 mA` |

Errors stopping the motor went from *Low VIN, Command timeout, Safe start
violation* to **Low VIN** only. The other two don't apply in STEP/DIR mode.
So once 12 V is present nothing else stands between it and an energized
driver: the Tic will hold the plunger at 990 mA as soon as VIN comes up.

## How it was done

1. `ticcmd --get-settings` → [`before_settings.txt`](before_settings.txt), and
   `--status --full` → [`before_status_full.txt`](before_status_full.txt).
2. `sed` changed exactly the three lines, then `ticcmd --fix-settings` checked
   the file offline. It adjusted nothing, so [`intended_settings_fixed.txt`](intended_settings_fixed.txt)
   is byte-identical to the edited file.
3. `ticcmd --settings intended_settings_fixed.txt` wrote it
   ([`apply_output.txt`](apply_output.txt): exit 0) at 21:54:51 UTC.
4. Read back: [`after_settings.txt`](after_settings.txt) is **byte-identical to
   the file written**, and [`after_status_full.txt`](after_status_full.txt)
   shows the new step mode and current limit live.

[`read_state.sh`](read_state.sh) and [`apply.sh`](apply.sh) are the two scripts
exactly as run (as root, via `sudo`).

The same settings are kept as [`cubos/docs/tic_p20.txt`](../../docs/tic_p20.txt)
for loading onto another T500: `ticcmd --settings tic_p20.txt`.

## `ticcmd` on the Pi

- **Where:** Pololu Tic software 1.8.1, the "Linux (Raspberry Pi)" build
  ([`pololu-tic-1.8.1-linux-rpi.tar.xz`](https://www.pololu.com/file/0J1349/pololu-tic-1.8.1-linux-rpi.tar.xz),
  sha256 `f345404215ad6a18968c5c3d28de0019f75adb756d0b15f8e268aca9ab2f3382`), unpacked
  to `~/.local/opt/pololu-tic-1.8.1-linux-rpi/`. Nothing was installed
  system-wide.
- **It runs on the Pi 5.** It is a 32-bit ARM static binary, and the Pi runs a
  64-bit kernel with 16 KB pages. The kernel has `CONFIG_COMPAT=y`, and the
  binary's segments are 64 KB-aligned, so it loads fine.
- **It needs `sudo`.** Pololu's `install.sh` also adds a udev rule granting
  every user access to Pololu USB devices. That step was skipped, to leave the
  system untouched. Without the rule, `/dev/bus/usb/…` is not writable by the
  login user, so `ticcmd --list` works but `--status`/`--settings` need root:

  ```bash
  sudo ~/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd --status
  ```

  If non-root access is wanted later, the whole change is one file,
  `/etc/udev/rules.d/99-pololu.rules`. Pololu's version is
  `SUBSYSTEM=="usb", ATTRS{idVendor}=="1ffb", MODE="0666"`; a narrower
  alternative is `GROUP="plugdev", MODE="0660"`, since the login user is in
  `plugdev`.
- The working files are also on the Pi, in `~/tic-setup-20260929/`.
