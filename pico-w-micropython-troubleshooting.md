# Pico W MicroPython Troubleshooting Guide

Troubleshooting guide for common issues when setting up the Raspberry Pi Pico W with MicroPython for the [wireless color sensor](https://accelerationconsortium.github.io/wireless-color-sensor/) project (see [issue #33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33)).

## 1. SSL/TLS Errors After Flashing MicroPython

### Symptoms

- `import ssl` raises an `ImportError` or `AttributeError`
- SSL/TLS connections fail with errors like `MBEDTLS_ERR_SSL_CONN_EOF` or `TypeError: extra keyword arguments given`
- MQTT or HTTPS connections that previously worked now fail after a firmware update

### Cause

MicroPython **v1.22.0** (released Dec 2023) introduced [breaking changes to the `ssl` module](https://github.com/micropython/micropython/releases/tag/v1.22.0). Specifically:

- The old `ssl_params` dictionary pattern (used by `umqtt` and `mqtt_as`) was replaced with an `ssl.SSLContext` API
- `ssl.CERT_REQUIRED` and other constants moved or changed
- Certificate/key loading now uses `SSLContext.load_cert_chain()` and `SSLContext.load_verify_locations()`

The [wireless color sensor `main.py`](https://github.com/AccelerationConsortium/wireless-color-sensor/blob/main/sensor_file/main.py) uses the older `ssl_params` pattern:

```python
config.update({
    "ssl": True,
    "ssl_params": {
        "server_side": False,
        "cert_reqs": ssl.CERT_REQUIRED,
        "cadata": cacert,
        "server_hostname": HIVEMQ_HOST,
    },
})
```

This pattern works on MicroPython **v1.21.0 and earlier**, but breaks on **v1.22.0+**.

### Fix Option A: Use a Compatible MicroPython Version (≤ v1.21.0)

If you want to avoid modifying the wireless color sensor code, downgrade to MicroPython v1.21.0:

1. **Download the required files:**
   - [`flash_nuke.uf2`](https://datasheets.raspberrypi.com/soft/flash_nuke.uf2) — completely wipes the Pico W flash memory
   - [MicroPython v1.21.0 for **Pico W**](https://micropython.org/download/rp2-pico-w/) — scroll to "Releases" and find v1.21.0. **Important:** use the **Pico W** version (`rp2-pico-w`), not the regular Pico version (`rp2-pico`).

2. **Enter BOOTSEL mode and wipe the flash** (see [Section 3](#3-bootsel-mode-and-rpi-rp2-drive-not-appearing) if the RPI-RP2 drive does not appear):
   - Disconnect everything from the Pico W (USB and battery)
   - **Press and hold the BOOTSEL button** on the Pico W
   - While still holding BOOTSEL, plug it into your computer via USB
   - Wait for the **RPI-RP2** USB drive to appear, then release BOOTSEL
   - Drag and drop `flash_nuke.uf2` onto the RPI-RP2 drive
   - Wait for it to reboot (~5 seconds)

3. **Flash MicroPython v1.21.0:**
   - Repeat the BOOTSEL procedure (hold BOOTSEL → plug in USB → wait for RPI-RP2)
   - Drag and drop the MicroPython v1.21.0 `.uf2` file onto the RPI-RP2 drive
   - Wait for it to reboot

4. **Verify in Thonny** (or any serial terminal):
   ```python
   import sys
   print(sys.version)
   # Should show 1.21.0

   import ssl
   # Should succeed without error
   ```

### Fix Option B: Update the Code for Newer MicroPython (v1.22.0+)

If you prefer to use a newer MicroPython version (e.g., v1.26.x, v1.27.x, v1.28.x), you can update the SSL configuration in `main.py` to use the new `ssl.SSLContext` API:

```python
# Old pattern (v1.21.0 and earlier):
# config.update({
#     "ssl": True,
#     "ssl_params": {
#         "server_side": False,
#         "cert_reqs": ssl.CERT_REQUIRED,
#         "cadata": cacert,
#         "server_hostname": HIVEMQ_HOST,
#     },
# })

# New pattern (v1.22.0+):
import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(cadata=cacert)

config.update({
    "ssl": context,
    "server": HIVEMQ_HOST,
})
```

> **Note:** The `mqtt_as` library (used by the wireless color sensor) has been [updated](https://github.com/peterhinch/micropython-mqtt) to support the newer `SSLContext` API. If you update `mqtt_as.py` to the latest version from [Peter Hinch's repo](https://github.com/peterhinch/micropython-mqtt/tree/master/mqtt_as), the `ssl` config parameter accepts an `SSLContext` directly. Make sure to also update the certificate file — newer MicroPython requires **DER format** (the project already uses `hivemq-com-chain.der`, so this should be fine).

### Which MicroPython Version Should I Use?

| Approach | MicroPython Version | Code Changes Needed? |
|---|---|---|
| Use existing code as-is | v1.21.0 | No |
| Update SSL config + mqtt_as | v1.22.0 or later (e.g., v1.28.0) | Yes (see Option B above) |

For a quick start, **Option A** (v1.21.0) is simplest. For long-term use, **Option B** is recommended since v1.21.0 will not receive security or bug fixes.

## 2. Pico W Not Staying Connected via USB

### Symptoms

- Pico W disconnects intermittently from the computer
- Thonny cannot detect the Pico W
- Pico W appears briefly then disappears from the system

### Common Causes and Fixes

#### A. USB Cable (Most Common Cause)

Many micro-USB cables are **charge-only** and lack data lines. Use a cable you know supports data transfer (e.g., one that came with a device that syncs data). Try multiple cables if unsure — a cable that charges a phone does not necessarily transfer data.

#### B. `boot.py` or `main.py` Blocking the REPL

If the Pico has a `main.py` or `boot.py` that immediately starts a long-running or infinite loop (for example, a Wi-Fi connection loop), the USB interface will usually still enumerate, but the board may appear "busy" because the REPL/Thonny prompt is blocked by the running code.

**Fix (try in order):**
1. Connect in Thonny and interrupt the running program (**Stop/Restart** button, or press `Ctrl+C`) to regain the REPL
2. If you can access the files, remove or rename the problematic `main.py` or `boot.py`, then reset the board
3. If normal recovery does not work, use `flash_nuke.uf2` (see [Section 1, Step 2](#fix-option-a-use-a-compatible-micropython-version--v1210)) to wipe everything, then re-flash MicroPython
4. After re-flashing, connect in Thonny **before** uploading any new `main.py` or `boot.py`

#### C. Windows Driver Issues

The Pico W may show up as an unrecognized device or "Android Device" in Device Manager.

**Fix:**
1. Open **Device Manager** and look for the Pico under "Ports (COM & LPT)" or "Other devices"
2. If the device is misidentified, right-click it → **Uninstall device** (check "Delete the driver software" if the option appears)
3. Unplug the Pico W, wait a few seconds, then plug it back in — Windows should reinstall the built-in **USB Serial Device** (CDC-ACM) driver automatically
4. If the correct driver still does not install, see the [Raspberry Pi Pico Windows driver documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)

> **Note:** The Zadig tool is sometimes recommended for USB driver issues, but for the Pico W it can make things worse — Zadig installs WinUSB/libusb-style drivers, which can **remove** the COM port that Thonny relies on. Stick with the built-in Windows CDC-ACM driver.

#### D. USB Port Power

Avoid USB hubs or front-panel USB ports. Use a port directly on the computer (back panel on desktop, or a direct port on laptop).

#### E. Thonny Configuration

- Set interpreter to **"MicroPython (Raspberry Pi Pico)"**
- Select the port Thonny detects for the Pico: **COMx** on Windows, `/dev/ttyACM0` (or similar) on Linux, or `/dev/tty.usbmodem*` (or similar) on macOS
- If the port doesn't show: close Thonny → unplug Pico → plug Pico back in → reopen Thonny

#### F. LiPo SHIM Interference

The wireless color sensor uses a [LiPo SHIM](https://shop.pimoroni.com/products/pico-lipo-shim) soldered to the Pico W. This can cause connection issues:

- The SHIM's power button may inadvertently toggle or interfere with USB enumeration
- When debugging via USB, the Pico should be powered through USB, not the battery — **disconnect the battery** during USB debugging sessions
- Poor solder joints between the SHIM and Pico W can cause intermittent connections — inspect joints under good lighting and reflow any cold or bridged joints

## 3. BOOTSEL Mode and RPI-RP2 Drive Not Appearing

If the RPI-RP2 drive does not appear when you enter BOOTSEL mode (a [common issue](https://forums.raspberrypi.com/viewtopic.php?t=357809) reported by many users), work through these checks:

### Standard BOOTSEL Procedure

1. Disconnect **everything** from the Pico W — USB cable **and** battery
2. **Press and hold the BOOTSEL button** (small white button on the board)
3. While still holding BOOTSEL, plug the USB cable into your computer
4. Wait 2–3 seconds, then release BOOTSEL
5. The Pico W should appear as a USB drive named **RPI-RP2**

### If RPI-RP2 Still Does Not Appear

#### Check the USB cable
Even if the cable works for Thonny/serial, some cables have marginal data connections that fail in BOOTSEL mode. Try at least 2–3 different known-good data cables.

#### Disconnect the LiPo SHIM battery
If a battery is connected to the LiPo SHIM, it can hold the Pico in a state that prevents BOOTSEL mode from engaging properly. **Always disconnect the battery** before attempting BOOTSEL mode.

#### Inspect solder joints (if LiPo SHIM is attached)
The LiPo SHIM is soldered back-to-back with the Pico W. Poor solder joints — especially on USB-related pins or the BOOTSEL trace — can prevent the board from entering BOOTSEL mode. Under good lighting (magnification if available):
- Look for cold joints (dull/grainy rather than shiny)
- Look for solder bridges between adjacent pins
- Reflow any suspicious joints with a soldering iron

#### Try a different computer or OS
Some Windows 10/11 configurations have USB driver issues that prevent the RPI-RP2 drive from appearing. Testing on a different computer (or booting a Linux USB stick) can help isolate whether the issue is the computer or the board. On Linux, run `lsusb` after plugging in to check if the RP2040 is detected at all.

#### Check Windows USB power management
On Windows, USB power-saving can interfere with BOOTSEL detection:
1. Open **Device Manager** → expand **Universal Serial Bus controllers**
2. For each **USB Root Hub**, right-click → **Properties** → **Power Management**
3. Uncheck **"Allow the computer to turn off this device to save power"**

#### Try the TP (test point) method
If the BOOTSEL button itself is damaged or unreliable (especially after soldering), you can enter BOOTSEL mode by shorting the **TP6** test point to **GND** while plugging in USB. See the [Raspberry Pi Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) for the TP6 location.

#### If nothing works
If the Pico W never appears as RPI-RP2 with multiple cables, multiple computers, and the battery disconnected, the board may be defective. Contact the vendor for a replacement. If possible, test with a bare Pico W (without the LiPo SHIM) to confirm.

## 4. Quick Recovery Procedure

If the Pico W seems "bricked" or unresponsive:

1. Unplug everything (USB and battery)
2. Hold BOOTSEL
3. Plug in USB (still holding BOOTSEL)
4. Wait for RPI-RP2 drive to appear, then release BOOTSEL
5. Drag `flash_nuke.uf2` onto the drive
6. After reboot, repeat steps 2–4
7. Drag the desired MicroPython `.uf2` onto the drive (see [Section 1](#1-ssltls-errors-after-flashing-micropython) for version guidance)
8. Open Thonny and verify the connection

If the RPI-RP2 drive does not appear, see [Section 3](#3-bootsel-mode-and-rpi-rp2-drive-not-appearing) for additional troubleshooting steps.

## 5. Useful References

- [MicroPython downloads for Pico W](https://micropython.org/download/rp2-pico-w/)
- [MicroPython v1.22.0 release notes (SSL breaking changes)](https://github.com/micropython/micropython/releases/tag/v1.22.0)
- [MicroPython SSL module documentation](https://docs.micropython.org/en/latest/library/ssl.html)
- [Wireless color sensor build guide](https://accelerationconsortium.github.io/wireless-color-sensor/)
- [Wireless color sensor source code (`main.py`)](https://github.com/AccelerationConsortium/wireless-color-sensor/blob/main/sensor_file/main.py)
- [Peter Hinch's `mqtt_as` library (updated for newer MicroPython)](https://github.com/peterhinch/micropython-mqtt)
- [AC Hello World course (Thonny + MicroPython setup)](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/index.html)
- [Raspberry Pi Pico W documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- [Raspberry Pi Forums — Pico W not recognized in BOOTSEL mode](https://forums.raspberrypi.com/viewtopic.php?t=357809)
- [Pimoroni LiPo SHIM product page](https://shop.pimoroni.com/products/pico-lipo-shim)
