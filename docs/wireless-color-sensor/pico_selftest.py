"""Staged self-test for the wireless color sensor (Pico W + AS7341).

Run this ON the Pico W in MicroPython (Thonny: open + Run, or `mpremote run
pico_selftest.py`). Every stage prints PASS or FAIL with the specific remedy,
so a failure tells you *which* link in the chain broke rather than just that
something broke.

Stages 1-3 need no network -- run those first to prove the sensor itself works.
Stages 4-8 exercise the upload path (WiFi -> NTP -> TLS -> HiveMQ -> publish).

Usage:
    STOP_AFTER = 3   # sensor-only check, no credentials needed
    STOP_AFTER = 8   # full chain, requires my_secrets.py on the device
"""

STOP_AFTER = 8  # set to 3 to run the offline sensor check only

# AS7341 spectral channel names, in wavelength order (nm).
CHANNEL_NAMES = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]

AS7341_I2C_ADDR = 0x39  # fixed for the Adafruit STEMMA QT AS7341 breakout

_results = []


def _stage(n, title):
    print("\n[{}/8] {}".format(n, title))
    print("-" * 52)


def _passed(n, detail=""):
    _results.append((n, True))
    print("  PASS {}".format(detail))


def _failed(n, err, remedy):
    _results.append((n, False))
    print("  FAIL {}".format(err))
    print("  -> {}".format(remedy))


# --------------------------------------------------------------------------
# Stage 1: I2C bus -- is the sensor physically wired and powered?
# --------------------------------------------------------------------------
_stage(1, "I2C bus scan (is the AS7341 wired up?)")
i2c = None
try:
    from machine import I2C, Pin

    i2c = I2C(0, scl=Pin(5), sda=Pin(4))
    found = i2c.scan()
    print("  devices found: {}".format([hex(a) for a in found]))
    if AS7341_I2C_ADDR in found:
        _passed(1, "AS7341 present at 0x39")
    else:
        _failed(
            1,
            "no device at 0x39",
            "Check the STEMMA QT cable is seated at BOTH ends and that the Qwiic "
            "cable colors match. An empty scan list ([]) means no power or a dead "
            "cable; a non-empty list without 0x39 means a different board is attached.",
        )
except Exception as e:
    _failed(1, repr(e), "I2C(0, scl=Pin(5), sda=Pin(4)) failed. Confirm you are running "
                        "MicroPython ON the Pico W, not desktop CPython -- 'no module "
                        "named machine' means the script ran on your laptop.")


# --------------------------------------------------------------------------
# Stage 2: read all 8 spectral channels
# --------------------------------------------------------------------------
_stage(2, "Read 8 spectral channels")
sensor = None
baseline = None
try:
    from as7341_sensor import Sensor

    sensor = Sensor(i2c=i2c)
    baseline = list(sensor.all_channels)
    reading = dict(zip(CHANNEL_NAMES, baseline))
    for name in CHANNEL_NAMES:
        print("  {}: {}".format(name, reading[name]))
    if len(baseline) != 8:
        _failed(2, "expected 8 channels, got {}".format(len(baseline)),
                "The as7341_sensor.py wrapper on the device may be an old version.")
    elif all(v == 0 for v in baseline):
        _failed(2, "all channels read 0",
                "Sensor responds on I2C but returns no counts. Usually integration "
                "time/gain is unset, or the sensor is in total darkness. Try again "
                "under room light before assuming the part is bad.")
    elif all(v == baseline[0] for v in baseline):
        _failed(2, "all channels identical ({})".format(baseline[0]),
                "Identical counts across channels usually means a stale/failed read "
                "rather than real spectral data. Power-cycle the Pico and retry.")
    else:
        _passed(2, "8 channels, range {}-{}".format(min(baseline), max(baseline)))
except Exception as e:
    _failed(2, repr(e), "Copy lib/as7341.py and lib/as7341_sensor.py from the "
                        "wireless-color-sensor repo into /lib on the Pico.")


# --------------------------------------------------------------------------
# Stage 3: does the reading actually respond to light? (the real "color" test)
# --------------------------------------------------------------------------
_stage(3, "Light response check (LED off vs. on)")
try:
    if sensor is None or baseline is None:
        raise RuntimeError("stage 2 did not produce a baseline reading")

    from time import sleep

    from neopixel import NeoPixel
    from machine import Pin

    # Onboard NeoPixel on the sensor package; adjust the pin if your build differs.
    pixels = NeoPixel(Pin(28), 1)

    def _read_under(color, label):
        pixels[0] = color
        pixels.write()
        sleep(0.5)
        vals = list(sensor.all_channels)
        print("  {:<14} {}".format(label + ":", vals))
        return vals

    dark = _read_under((0, 0, 0), "off")
    red = _read_under((255, 0, 0), "red")
    green = _read_under((0, 255, 0), "green")
    blue = _read_under((0, 0, 255), "blue")
    _read_under((0, 0, 0), "off again")

    # Red light should push the long-wavelength channels (ch620/ch670) hardest;
    # blue should push the short ones (ch410/ch440). That asymmetry is what proves
    # we are reading *color* and not just total brightness.
    red_long = red[6] + red[7]
    blue_short = blue[0] + blue[1]
    dark_long = dark[6] + dark[7]
    dark_short = dark[0] + dark[1]

    print("  red  -> long-wavelength (ch620+ch670): {} vs dark {}".format(red_long, dark_long))
    print("  blue -> short-wavelength (ch410+ch440): {} vs dark {}".format(blue_short, dark_short))

    if red_long > dark_long and blue_short > dark_short:
        _passed(3, "channels track the illumination color")
    elif max(red) > max(dark) or max(green) > max(dark) or max(blue) > max(dark):
        _failed(3, "responds to light, but not in the expected spectral direction",
                "The sensor sees brightness changes but the per-channel response is "
                "off. Check that the LED is actually inside the sensor housing and "
                "that nothing is blocking the AS7341 aperture.")
    else:
        _failed(3, "no change between LED off and LED on",
                "Either the NeoPixel pin is wrong (try a different Pin number) or the "
                "LED is not illuminating the sensor. Watch the LED by eye while this "
                "runs -- if it never lights up, the problem is the LED, not the sensor.")
except Exception as e:
    _failed(3, repr(e), "NeoPixel setup failed. If your build has no onboard LED, "
                        "skip this stage and instead wave a colored object in front of "
                        "the sensor while re-running stage 2 -- the counts should move.")


if STOP_AFTER <= 3:
    print("\nStopping after stage 3 (STOP_AFTER=3). Sensor-only check complete.")
else:
    # ----------------------------------------------------------------------
    # Stage 4: secrets file
    # ----------------------------------------------------------------------
    _stage(4, "Load credentials from my_secrets.py")
    SSID = PASSWORD = HIVEMQ_HOST = HIVEMQ_USERNAME = HIVEMQ_PASSWORD = PICO_ID = None
    try:
        from my_secrets import (
            SSID,
            PASSWORD,
            HIVEMQ_HOST,
            HIVEMQ_USERNAME,
            HIVEMQ_PASSWORD,
            PICO_ID,
        )

        missing = [
            n
            for n, v in [
                ("SSID", SSID),
                ("PASSWORD", PASSWORD),
                ("HIVEMQ_HOST", HIVEMQ_HOST),
                ("HIVEMQ_USERNAME", HIVEMQ_USERNAME),
                ("HIVEMQ_PASSWORD", HIVEMQ_PASSWORD),
                ("PICO_ID", PICO_ID),
            ]
            if not v
        ]
        if missing:
            _failed(4, "empty values: {}".format(missing),
                    "Fill these in in my_secrets.py on the device.")
        else:
            _passed(4, "all 6 values present (PICO_ID={})".format(PICO_ID))
    except Exception as e:
        _failed(4, repr(e), "Create /my_secrets.py on the Pico with SSID, PASSWORD, "
                            "HIVEMQ_HOST, HIVEMQ_USERNAME, HIVEMQ_PASSWORD, PICO_ID. "
                            "This file is gitignored by design -- it never leaves the device.")

    # ----------------------------------------------------------------------
    # Stage 5: WiFi
    # ----------------------------------------------------------------------
    _stage(5, "WiFi association")
    try:
        import network
        from time import sleep

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        visible = []
        try:
            visible = [n[0].decode() for n in wlan.scan()]
            print("  visible SSIDs: {}".format(visible[:10]))
        except Exception:
            pass

        if SSID and SSID not in visible and visible:
            print("  NOTE: target SSID not in scan results")

        wlan.connect(SSID, PASSWORD)
        for _ in range(30):
            if wlan.isconnected():
                break
            sleep(1)

        if wlan.isconnected():
            _passed(5, "IP {}".format(wlan.ifconfig()[0]))
        else:
            _failed(5, "status={} after 30s".format(wlan.status()),
                    "MicroPython only supports WPA2-PSK on 2.4 GHz. It CANNOT join "
                    "eduroam or any WPA2-Enterprise network, and it cannot see 5 GHz-only "
                    "SSIDs. Use a dedicated IoT SSID, a travel router, or a phone hotspot "
                    "set to 2.4 GHz.")
    except Exception as e:
        _failed(5, repr(e), "WiFi stack failed to initialize -- reflash MicroPython "
                            "for the Pico W (not the plain Pico build).")

    # ----------------------------------------------------------------------
    # Stage 6: clock (TLS cert validation needs a correct date)
    # ----------------------------------------------------------------------
    _stage(6, "NTP time sync (required for TLS)")
    try:
        import ntptime
        from time import localtime, sleep

        ntptime.timeout = 5
        ok = False
        for host in ("time.google.com", "pool.ntp.org"):
            ntptime.host = host
            try:
                ntptime.settime()
                ok = True
                print("  synced via {}".format(host))
                break
            except Exception as e:
                print("  {} failed: {}".format(host, e))
                sleep(2)

        year = localtime()[0]
        if ok and year >= 2024:
            _passed(6, "clock = {}".format(localtime()[:6]))
        else:
            _failed(6, "clock year is {}".format(year),
                    "Without a correct clock, TLS certificate validation in stage 8 "
                    "will fail with a confusing cert error. If NTP is blocked on this "
                    "network, that is the root cause -- fix it here, not in stage 8.")
    except Exception as e:
        _failed(6, repr(e), "ntptime import/sync failed.")

    # ----------------------------------------------------------------------
    # Stage 7: TLS prerequisites
    # ----------------------------------------------------------------------
    _stage(7, "TLS module + CA certificate")
    cacert = None
    ssl_mod = None
    try:
        try:
            import ssl as ssl_mod
            print("  using 'ssl' module")
        except ImportError:
            import ussl as ssl_mod  # older MicroPython builds
            print("  using legacy 'ussl' module")

        with open("hivemq-com-chain.der", "rb") as f:
            cacert = f.read()
        if not cacert:
            raise ValueError("hivemq-com-chain.der is empty")
        _passed(7, "CA cert loaded ({} bytes)".format(len(cacert)))
    except ImportError as e:
        _failed(7, repr(e), "Neither 'ssl' nor 'ussl' exists in this firmware. That "
                            "means the board was flashed with a non-standard or "
                            "stripped MicroPython build. Reflash using the official "
                            "RPI_PICO_W .uf2 from micropython.org/download/RPI_PICO_W/ "
                            "by holding BOOTSEL, plugging in USB, and dragging the .uf2 "
                            "onto the RPI-RP2 drive.")
    except OSError as e:
        _failed(7, repr(e), "hivemq-com-chain.der is missing from the device filesystem. "
                            "Copy it from the wireless-color-sensor repo to the Pico root.")
    except Exception as e:
        _failed(7, repr(e), "Unexpected TLS setup failure.")

    # ----------------------------------------------------------------------
    # Stage 8: MQTT connect + publish a real reading
    # ----------------------------------------------------------------------
    _stage(8, "MQTT connect + publish reading to HiveMQ")
    try:
        import json
        from umqtt.simple import MQTTClient

        topic = "color-mixing/picow/{}/as7341".format(PICO_ID)
        payload = json.dumps(
            {
                "experiment_id": "selftest",
                "command": {"R": 0, "Y": 0, "B": 0},
                "sensor_data": dict(zip(CHANNEL_NAMES, list(sensor.all_channels))),
            }
        )

        client = MQTTClient(
            client_id="pico-selftest-{}".format(PICO_ID),
            server=HIVEMQ_HOST,
            port=8883,
            user=HIVEMQ_USERNAME,
            password=HIVEMQ_PASSWORD,
            keepalive=30,
            ssl=True,
            ssl_params={"server_hostname": HIVEMQ_HOST, "cadata": cacert},
        )
        client.connect()
        print("  connected to broker")
        client.publish(topic, payload)
        client.disconnect()
        print("  topic:   {}".format(topic))
        print("  payload: {}".format(payload))
        _passed(8, "published")
    except Exception as e:
        msg = repr(e)
        if "EHOSTUNREACH" in msg or "-2" in msg:
            remedy = ("Cannot resolve/reach HIVEMQ_HOST. Check the hostname has no "
                      "'https://' prefix and no trailing slash.")
        elif "5" in msg and "MQTT" in msg.upper():
            remedy = ("Broker refused the credentials. In the HiveMQ console, confirm "
                      "the credential exists AND has explicit publish permission for "
                      "'color-mixing/#'. Missing topic permissions is the most common "
                      "silent failure here.")
        elif "cert" in msg.lower() or "ssl" in msg.lower():
            remedy = ("TLS handshake failed. Re-check stage 6 (clock) first -- a wrong "
                      "date is the usual cause -- then confirm hivemq-com-chain.der "
                      "matches your cluster.")
        else:
            remedy = "See the HiveMQ web console 'Clients' tab to check for a connection attempt."
        _failed(8, msg, remedy)


# --------------------------------------------------------------------------
print("\n" + "=" * 52)
print("SUMMARY")
print("=" * 52)
for n, ok in _results:
    print("  stage {}: {}".format(n, "PASS" if ok else "FAIL"))
_bad = [n for n, ok in _results if not ok]
if _bad:
    print("\nFirst failure: stage {}. Fix that one first -- later stages".format(_bad[0]))
    print("depend on it, so their failures are probably just downstream noise.")
else:
    print("\nAll stages passed.")
