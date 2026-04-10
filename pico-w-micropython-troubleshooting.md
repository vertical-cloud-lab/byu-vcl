# Pico W MicroPython Troubleshooting Guide

Troubleshooting guide for common issues when setting up the Raspberry Pi Pico W with MicroPython for the [wireless color sensor](https://accelerationconsortium.github.io/wireless-color-sensor/) project (see [issue #33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33)).

## 1. SSL Import Error After Flashing MicroPython

### Symptoms

- `import ssl` raises an `ImportError` or `OSError`
- SSL/TLS connections fail with errors like `MBEDTLS_ERR_SSL_CONN_EOF` or `TypeError: extra keyword arguments given`
- MQTT or HTTPS connections that previously worked now fail after a firmware update

### Cause

MicroPython v1.22+ introduced breaking changes to the `ssl` module API. Code written for older versions (including the wireless color sensor project code) uses the older `ssl_params` pattern, which is incompatible with the new `ssl.SSLContext` API.

### Fix: Downgrade to MicroPython v1.21.0

1. **Download the required files:**
   - [`flash_nuke.uf2`](https://datasheets.raspberrypi.com/soft/flash_nuke.uf2) — completely wipes the Pico W flash
   - [MicroPython v1.21.0 for Pico W](https://micropython.org/download/rp2-pico-w/) — scroll to "Releases" and find v1.21.0. **Use the Pico W version**, not the regular Pico version.

2. **Wipe the Pico W flash:**
   - Unplug the Pico W from USB and disconnect the battery
   - **Hold the BOOTSEL button** on the Pico W
   - While holding BOOTSEL, plug it into your computer via USB
   - It should appear as a USB drive called **RPI-RP2**
   - Drag and drop `flash_nuke.uf2` onto the RPI-RP2 drive
   - Wait for it to reboot (~5 seconds)

3. **Flash MicroPython v1.21.0:**
   - Repeat the BOOTSEL hold + plug-in process (hold BOOTSEL, plug in USB, wait for RPI-RP2)
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

### Alternative: Update Code for Newer MicroPython

If you want to keep a newer firmware (v1.22+), update SSL code to use the new `ssl.SSLContext` API:

```python
# Old pattern (v1.21 and earlier):
# MQTTClient(..., ssl=True, ssl_params={...})

# New pattern (v1.22+):
import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# Configure verify_mode and load certificates as needed
# MQTTClient(..., ssl=context)
```

For the wireless color sensor project, downgrading to v1.21.0 is simpler since the existing code was written for the older API.

## 2. Pico W Not Staying Connected via USB

### Symptoms

- Pico W disconnects intermittently from the computer
- Thonny cannot detect the Pico W
- Pico W appears briefly then disappears from the system

### Common Causes and Fixes

#### A. USB Cable (Most Common Cause)

Many micro-USB cables are **charge-only** and lack data lines. Use a cable that you know supports data transfer (e.g., one that came with a device that syncs data, not just a phone charger cable). Try multiple cables if unsure.

#### B. `boot.py` or `main.py` Blocking USB

If the Pico has a `main.py` that starts an infinite loop (e.g., Wi-Fi connection loop) immediately on boot, it can prevent the USB serial interface from initializing.

**Fix:**
- Use `flash_nuke.uf2` (see Section 1, Step 2) to wipe everything, then re-flash MicroPython
- After re-flashing, connect in Thonny **before** uploading any `main.py` or `boot.py`

#### C. Windows Driver Issues

The Pico W may show up as "Android Device" or not appear at all in Device Manager.

**Fix:**
- Open Device Manager and look for the Pico under "Ports (COM & LPT)" or "Other devices"
- If it's misidentified, use the [Zadig tool](https://zadig.akeo.ie/) to install the "USB Serial (CDC)" driver

#### D. USB Port Power

Avoid USB hubs or front-panel USB ports. Use a port directly on the computer (back panel on desktop, or a direct port on laptop).

#### E. Thonny Configuration

- Set interpreter to **"MicroPython (Raspberry Pi Pico)"**
- Select the correct COM port (Windows) or `/dev/ttyACM0` (Linux/Mac)
- If the port doesn't show: close Thonny → unplug Pico → plug Pico back in → reopen Thonny

#### F. LiPo SHIM Interference

Since the wireless color sensor uses a LiPo SHIM soldered to the Pico W, make sure the SHIM's power button isn't inadvertently toggling. When debugging via USB, the Pico should be powered through USB, not the battery. Try disconnecting the battery during USB debugging sessions.

## 3. Quick Recovery Procedure

If the Pico W seems "bricked" or unresponsive:

1. Unplug everything (USB and battery)
2. Hold BOOTSEL
3. Plug in USB (still holding BOOTSEL)
4. Wait for RPI-RP2 drive to appear, then release BOOTSEL
5. Drag `flash_nuke.uf2` onto the drive
6. After reboot, repeat steps 2–4
7. Drag the MicroPython v1.21.0 `.uf2` onto the drive
8. Open Thonny and verify the connection

## 4. Useful References

- [MicroPython downloads for Pico W](https://micropython.org/download/rp2-pico-w/)
- [MicroPython SSL module docs](https://docs.micropython.org/en/latest/library/ssl.html)
- [Wireless color sensor build guide](https://accelerationconsortium.github.io/wireless-color-sensor/)
- [AC Hello World course (Thonny + MicroPython setup)](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/index.html)
- [Raspberry Pi Forums — Pico W serial port not detected](https://forums.raspberrypi.com/viewtopic.php?t=393458)
- [Zadig USB driver tool](https://zadig.akeo.ie/)
