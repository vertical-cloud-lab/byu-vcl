# CubXL systems check, 2026-10-08

Ben asked for this on [#165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165) after
unplugging everything and replacing some cables. The gantry was powered off. The
final run was at 16:11 MDT (22:11 UTC), with
[`cubos/tools/cubxl_syscheck.py`](../../tools/cubxl_syscheck.py). Its output is in
[`syscheck.txt`](syscheck.txt).

## Result: everything answered except the Tic T500, which is not on USB

| | Result |
| --- | --- |
| Pi | ✅ Booted at 15:50 MDT, when it was plugged back in. `throttled=0x0`: no under-voltage or throttling since boot. 5.13 V in, and a 5,000 mA supply negotiated. 40 °C. 13% of the disk used. 735 of 991 MiB of memory available. Wi-Fi at −44 dBm. No failed systemd units. |
| Arduino | ✅ Same board (USB serial `03535343335351018130`), on `/dev/ttyACM0` as the gantry files expect. `OK:Ready` came 3.80 s after the port opened; on 2026-10-01 it took 3.77 s. HELLO, plunger STATUS and the cap sensor all answered `OK`. |
| Gantry CH340 | ✅ On USB as `/dev/ttyUSB0`, as the gantry files expect. The gantry was off, so the port was not opened. |
| Tic T500 | ❌ **Not on USB.** See below. |
| Cameras | ✅ Both Camera Module 3 Wide modules were detected at boot. Both took a sharp still (`AfState` 2, focused). |
| `deckcam` | ✅ Active, with no viewers. Its page answers on `127.0.0.1:8743`. |

What the Arduino said:

| command | reply | meaning |
| --- | --- | --- |
| 0 HELLO | `OK:{"msg":"Hello from Pawduino!"}` | the firmware is running |
| 14 STATUS | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` | `max_vol` 20.00 is the VCL P20 GEN2 image ([`../../firmware/`](../../firmware/README.md)); stock firmware says 300. `homed` 0 is normal after any reset, and every protocol starts with `home`. |
| 7 LINE_BREAK | `OK:{"value1":0}` | the cap sensor's beam is clear, so nothing is held on the head |

Nothing else was sent to it: no plunger move, capper, magnet or light command.

## The Tic T500 is not connected to the Pi over USB

- `ticcmd --list` finds no Tic.
- Since boot, the kernel has enumerated exactly two USB devices: the Arduino (`usb 3-1`) and the
  CH340 (`usb 3-2`), both on controller `xhci-hcd.1` ([`usb.txt`](usb.txt)).
- Nothing has tried to connect on the Pi's other two ports, not even unsuccessfully. A
  device whose data lines are connected but which fails to enumerate leaves `error -71` or
  `unable to enumerate` lines, and there are none.
- An unplugged cable looks like this. So does a charge-only micro-USB cable, which has no
  data wires at all.
- On 2026-09-29 the Tic enumerated as `usb 1-1` (`1ffb:00bd`, "Pololu Tic T500"), on the
  other controller ([kernel log](../pipette_test_20260930/kernel_usb_18-22_18-30.log)).

What this changes:

- **No protocol will run until it is back.** `cubxl_run.py` reads the Tic's settings and
  energizes it over USB during its checks. With no Tic it stops there with `ticcmd failed`,
  before anything moves.
- **Its motor current can't be switched from the Pi.** The Tic is in STEP/DIR mode
  ([setup](../../docs/tic-t500-pipette-setup.md)). In that mode it energizes the plunger
  motor at 990 mA as soon as its 12 V `VIN` comes up. It does that without USB too, because
  its settings are stored on the Tic. A motor holding at 990 mA puts about 4 W into the
  pipette body, which the lab avoids between runs. Without USB, the only way to stop that
  is to switch off the 12 V supply. Pololu's guide says the Tic's yellow LED is "on solid most of the time"
  while the motor is energized.

To fix it, plug the Tic's micro-USB into one of the Pi's two free USB ports, using a data
cable. USB is hot-pluggable, so the Pi doesn't need a restart, and
`/etc/udev/rules.d/99-pololu.rules` gives the login user access as soon as the Tic
appears. Pololu's guide says the green LED "will start blinking slowly" when the Tic is
connected to a computer, then stays on. If it stays off, the cable or port isn't carrying
data. Then re-run the check.

## Not checked

- **The gantry and GRBL**, because they were off. The next `cubxl_run.py` run checks
  GRBL's `$$` settings and G54 against the gantry file before anything moves.
- **Anything that moves or switches**: the plunger, the capper, the magnet and the
  lights. The plunger's limit switch has no read-only command.
- **The Tic's settings and status**, which need USB.

## Notes

- **Opening the Arduino's port resets the board**, as CubOS does every time. Its `setup()`
  only initialises its modules and prints `OK:Ready`, and it moves nothing. The board was
  reset 4 times in this session: twice by hand while developing the check, and once by
  each run of the script.
- **Wait for the boot banner before sending HELLO.** On the first hand-run attempt, HELLO
  went out 3.0 s after the port opened. The banner `OK:Ready` (3.8 s) was then read as
  HELLO's reply. The STATUS and LINE_BREAK replies were still correctly paired, because
  the buffer was flushed before each command. CubOS's `PawduinoLink` guards against this
  with `expect="Hello"`. The script waits for the banner.
- **The 12:25 timestamps in [`usb.txt`](usb.txt) are not when the Pi booted.** The Pi's
  clock read 12:25 when it booted at 15:50 MDT, before it synced its clock. The symlinks were
  created at boot.
- One `sudo` call in this session went out with no password, by mistake, and was rejected.
  It changed nothing.
- Nothing on the Pi was changed. The stills were written to `/tmp` and deleted after they
  were copied off.

## Files

- [`syscheck.txt`](syscheck.txt): the script's output.
- [`usb.txt`](usb.txt): `lsusb`, the serial device paths, `ticcmd --list`, and every USB
  device the kernel enumerated since boot. The hostname is replaced with `<pi>`.
- [`frames/`](frames/): one still from each camera (2304 × 1296, the full field of view),
  each with its `rpicam-still` metadata.

## Re-running it

From a machine on the tailnet, with this repo checked out:

```bash
ssh <user>@<cubxl-pi> '~/CubOS/.venv/bin/python - --frames /tmp/syscheck' \
    < cubos/tools/cubxl_syscheck.py
```

`--frames` is optional. Without it, no camera is opened. `--no-arduino` leaves the
Arduino's port closed.
