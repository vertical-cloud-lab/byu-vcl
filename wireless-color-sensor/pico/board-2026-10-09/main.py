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
                

                # Run the color experiment with the specified RGB values
                sensor_data = run_color_experiment(R, Y, B)

                # Combine the sensor data with the original command
                payload_data = incoming_dict.copy()
                payload_data.update({"sensor_data": sensor_data})
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
