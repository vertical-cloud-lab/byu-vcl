import sys
import json
import ssl
import asyncio
import ntptime
from uio import StringIO
from time import time, sleep

from machine import I2C, SoftI2C, Pin

# WiFi
from netman import connectWiFi

# Hardware
import machine
from neopixel import NeoPixel
from as7341_sensor import Sensor

# MQTT
from mqtt_as import MQTTClient, config

from my_secrets import (
    SSID,
    PASSWORD,
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_USERNAME,
    COURSE_ID,
    PICO_ID,
)


def get_onboard_led():
    try:
        onboard_led = Pin("LED", Pin.OUT)  # only works for Pico W
    except Exception as e:
        print(e)
        onboard_led = Pin(25, Pin.OUT)
    return onboard_led

onboard_led = get_onboard_led()


def sign_of_life(led, first, blink_interval_ms=5000):
    global last_blink
    if first:
        led.on()
        last_blink = ticks_ms()
    time_since = ticks_diff(ticks_ms(), last_blink)
    if led.value() == 0 and time_since >= blink_interval_ms:
        led.toggle()
        last_blink = ticks_ms()
    elif led.value() == 1 and time_since >= 500:
        led.toggle()
        last_blink = ticks_ms()


# Instantiate the Sensor class
# REQUIRES MicroPython >= 1.29.0. On 1.26-1.28 the RP2040 hardware I2C driver
# has a regression: i2c.scan() ACKs the AS7341 at 0x39, but every register
# read/write returns OSError: [Errno 5] EIO at any bus speed. Confirmed on two
# separate Pico W boards; fixed in 1.29.0. If you must run an older build, swap
# I2C(...) for SoftI2C(scl=Pin(5), sda=Pin(4)), which works on both.
# See micropython/micropython#19087 and #18257.
sensor = Sensor(i2c = I2C(0, scl=Pin(5), sda=Pin(4)))

# Per-reading settings: gain (added 2026-10-09), integration time and the
# breakout's white LED (added 2026-10-10). A read command may carry
# "settings": {"gain": G, "atime": A, "astep": S, "led_ma": L}, any subset.
# A setting left out reads as Sensor() has always set it: 128x, ATIME 100,
# ASTEP 999 (2 x 281 ms), LED off. So a command without "settings" reads
# exactly as before, and every setting is put back after each reading.
GAINS = (0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512)  # index = AGAIN code
DEFAULT_GAIN_CODE = 8  # Sensor(gain=8): code 8 = 128x
DEFAULT_ATIME, DEFAULT_ASTEP = 100, 999  # Sensor() defaults
MAX_INTEGRATION_MS = 1500  # per half; a reading takes two halves
LED_MA_MIN, LED_MA_MAX = 4, 20  # lib/as7341.py's own limits, even mA only


def whole(settings, key, default, lo, hi):
    value = settings.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
        raise ValueError("%s must be a whole number from %d to %d; got %r" % (key, lo, hi, value))
    return value


def read_settings(settings):
    """(AGAIN code, ATIME, ASTEP, LED mA) for a command's optional "settings"."""
    if settings is None:
        settings = {}
    if not isinstance(settings, dict):
        raise ValueError("settings must be an object")
    for key in settings:
        if key not in ("gain", "atime", "astep", "led_ma"):
            raise ValueError("unknown setting %r: use gain, atime, astep or led_ma" % (key,))
    code = None
    gain = settings.get("gain", GAINS[DEFAULT_GAIN_CODE])
    if not isinstance(gain, bool):
        for c, g in enumerate(GAINS):
            if gain == g:
                code = c
    if code is None:
        raise ValueError("gain must be one of 0.5, 1, 2, 4, ... 512; got %r" % (gain,))
    atime = whole(settings, "atime", DEFAULT_ATIME, 0, 255)
    astep = whole(settings, "astep", DEFAULT_ASTEP, 0, 65534)
    if integration_ms(atime, astep) > MAX_INTEGRATION_MS:
        raise ValueError("(atime + 1) x (astep + 1) x 2.78 us must be at most %d ms; got %.1f"
                         % (MAX_INTEGRATION_MS, integration_ms(atime, astep)))
    led = whole(settings, "led_ma", 0, 0, LED_MA_MAX)
    if led and (led < LED_MA_MIN or led % 2):
        raise ValueError("led_ma must be 0 (off) or an even number from 4 to 20; got %r" % (led,))
    return code, atime, astep, led


def integration_ms(atime, astep):
    return (atime + 1) * (astep + 1) * 2.78 / 1000


CHANNEL_NAMES = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")


def read_with(code, atime, astep, led):
    """One reading at these settings, then the defaults back whatever happens.

    Returns F1-F8 as read_sensor_data() does, plus each half's Clear, NIR and
    ASTATUS (0x94, read straight after the counts: the gain code the chip used
    in bits 0-3, analog saturation in bit 7; the driver's own copy from its bulk
    read always showed code 8 on 2026-10-09, whatever the gain).
    """
    chip = sensor.sensor
    timing = (atime, astep) != (DEFAULT_ATIME, DEFAULT_ASTEP)
    chip.set_again(code)
    try:
        if timing:
            chip.set_atime(atime)
            chip.set_astep(astep)
        if led:
            chip.set_led_current(led)  # also waits 100 ms
        counts, clear, nir, astatus = [], [], [], []
        for half in ("F1F4CN", "F5F8CN"):  # the two halves Sensor.all_channels reads
            chip.start_measure(half)
            data = chip.get_spectral_data()
            counts += list(data[:4])
            clear.append(data[4])
            nir.append(data[5])
            try:
                astatus.append(sensor.i2c.readfrom_mem(0x39, 0x94, 1)[0])
            except OSError:
                astatus.append(None)
    finally:
        if led:
            chip.set_led_current(0)
        if timing:
            chip.set_atime(DEFAULT_ATIME)
            chip.set_astep(DEFAULT_ASTEP)
        chip.set_again(DEFAULT_GAIN_CODE)
    known = None not in astatus
    sensor_data = dict(zip(CHANNEL_NAMES, counts))
    print(sensor_data)
    return sensor_data, {
        "gain": GAINS[code],
        "again_code": astatus[-1] & 0x0F if known else None,
        "analog_saturated": any(s & 0x80 for s in astatus) if known else None,
        "atime": atime,
        "astep": astep,
        "integration_ms": round(integration_ms(atime, astep), 1),
        "full_scale": min(65535, (atime + 1) * (astep + 1)),
        "led_ma": led,
    }, {"clear": clear, "nir": nir}



def read_sensor_data():
    """Read dictionary of sensor data"""
   # sensor.LED = True

    # Get all channel data from the sensor
    channel_data = sensor.all_channels
  #  sensor.LED = False

    CHANNEL_NAMES = [
        "ch410",
        "ch440",
        "ch470",
        "ch510",
        "ch550",
        "ch583",
        "ch620",
        "ch670",
    ]

    # Return a dictionary that maps channel names to sensor data
    return dict(zip(CHANNEL_NAMES, channel_data))


print("Testing sensor...")
sensor_data = read_sensor_data()
print(sensor_data)


# Description: Receive commands from HiveMQ and send dummy sensor data to HiveMQ

connectWiFi(SSID, PASSWORD, country="CA")

# To validate certificates, a valid time is required
ntptime.timeout = 5  # type: ignore
ntptime.host = "time.google.com"
try:
    ntptime.settime()
except Exception as e:
    print(f"{e} with {ntptime.host}. Trying again after 5 seconds")
    sleep(5)
    try:
        ntptime.settime()
    except Exception as e:
        print(f"{e} with {ntptime.host}. Trying again with pool.ntp.org")
        sleep(5)
        ntptime.host = "pool.ntp.org"
        ntptime.settime()

print("Obtaining CA Certificate from file")
with open("hivemq-com-chain.der", "rb") as f:
    cacert = f.read()
f.close()

# Local configuration
config.update(
    {
        "ssid": SSID,
        "wifi_pw": PASSWORD,
        "server": HIVEMQ_HOST,
        "user": HIVEMQ_USERNAME,
        "password": HIVEMQ_PASSWORD,
        "ssl": True,
        "ssl_params": {
            "server_side": False,
            "key": None,
            "cert": None,
            "cert_reqs": ssl.CERT_REQUIRED,
            "cadata": cacert,
            "server_hostname": HIVEMQ_HOST,
        },
        "keepalive": 15,
    }
)


# Dummy function for running a color experiment
def run_color_experiment(R, Y, B):

    # set_color(R, Y, B)
    sensor_data = read_sensor_data()
    print(sensor_data)
    # clear_color()

    return sensor_data


# MQTT Topics, not used in LCM
command_topic = f"{COURSE_ID}/request"

# my_id = hexlify(machine.unique_id()).decode()

# MQTT Topics
command_topic = f"command/picow/{PICO_ID}/as7341/read"
sensor_data_topic = f"color-mixing/picow/{PICO_ID}/as7341"

print(f"Command topic: {command_topic}")
print(f"Sensor data topic: {sensor_data_topic}")

async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        try:
            topic = topic.decode()
            msg = msg.decode()
            retained = str(retained)
            print((topic, msg, retained))

            if topic == command_topic:
                # Parse the incoming message as JSON
                incoming_dict = json.loads(msg)
                command = incoming_dict["command"]
                experiment_id = incoming_dict["experiment_id"]

                # Extract the RGB values and experiment_id from the command
                R = command["R"]
                Y = command["Y"]
                B = command["B"]
                

                # Settings for this reading; a bad "settings" gets an error reply
                try:
                    code, atime, astep, led = read_settings(incoming_dict.get("settings"))
                except ValueError as e:
                    await client.publish(sensor_data_topic, json.dumps(
                        {"experiment_id": experiment_id, "error": str(e)}))
                    continue

                # Read at those settings; read_with() puts the defaults back
                sensor_data, sensor_settings, extra = read_with(code, atime, astep, led)

                # Combine the sensor data with the original command
                payload_data = incoming_dict.copy()
                payload_data.update({"sensor_data": sensor_data,
                                     "sensor_settings": sensor_settings,
                                     "sensor_extra": extra})
                #payload_data["course_id"] = COURSE_ID

                # Convert the payload data to a JSON string
                payload = json.dumps(payload_data)

                # Publish the payload to the sensor data topic
                await client.publish(sensor_data_topic, payload)
                print("sensor results published")

        except Exception as e:
            with StringIO() as f:  # type: ignore
                sys.print_exception(e, f)  # type: ignore
                print(f.getvalue())  # type: ignore


async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe(command_topic, 1)  # renew subscriptions


async def main(client):
    await client.connect()
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))

    start_time = time()
    # must have the while True loop to keep the program running
    while True:
        await asyncio.sleep(5)
        onboard_led.toggle()
        elapsed_time = round(time() - start_time)
        print(f"Elapsed: {elapsed_time}s")


config["queue_len"] = 5  # Use event interface with specified queue length
MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
