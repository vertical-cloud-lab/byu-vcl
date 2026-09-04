"""End-to-end wireless check, run entirely on the Pico W.

The board already holds its own broker credentials in `my_secrets.py`, so this
proves the whole chain -- sensor, WiFi, NTP, TLS, broker, publish -- without the
operator needing any credential at all. It subscribes to its own data topic and
waits for its own publish to come back, which distinguishes "the broker accepted
the subscription" from "the broker actually delivers on it"; a credential that
lacks read permission ACKs a SUBSCRIBE and then silently delivers nothing.

    ~/.venvs/mpremote/bin/mpremote connect id:e6647c15673a2438 reset
    ~/.venvs/mpremote/bin/mpremote connect id:e6647c15673a2438 run board_e2e_mqtt.py
"""

import asyncio
import json
import ssl
from time import sleep

import ntptime
from machine import I2C, Pin

from as7341_sensor import Sensor
from mqtt_as import MQTTClient, config
from my_secrets import (
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_USERNAME,
    PASSWORD,
    PICO_ID,
    SSID,
)
from netman import connectWiFi

CHANNELS = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
DATA_TOPIC = "color-mixing/picow/%s/as7341" % PICO_ID

print("[1] sensor")
sensor = Sensor(i2c=I2C(0, scl=Pin(5), sda=Pin(4)), gain=4)
sensor.LED = False
sleep(0.3)
sensor.LED = True  # the deployed main.py leaves this commented out, so it reads dark
sleep(0.8)
reading = dict(zip(CHANNELS, sensor.all_channels))
sensor.LED = False
print("    ", reading)

print("[2] wifi")
connectWiFi(SSID, PASSWORD, country="US")  # US, not the reference firmware's CA

print("[3] ntp -- certificates cannot validate against a wrong clock")
ntptime.timeout = 5
ntptime.host = "time.google.com"
try:
    ntptime.settime()
    print("     clock set")
except Exception as e:
    print("     ntp failed:", e)

with open("hivemq-com-chain.der", "rb") as f:
    cacert = f.read()

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
        "queue_len": 5,
    }
)
client = MQTTClient(config)
received = []


async def reader(c):
    async for topic, msg, retained in c.queue:
        received.append(msg.decode())
        print("     <-- delivered back on", topic.decode())


async def run():
    print("[4] mqtt connect over TLS")
    await asyncio.wait_for(client.connect(), 45)
    print("     broker connected")
    asyncio.create_task(reader(client))
    await client.subscribe(DATA_TOPIC, 1)
    print("[5] subscribed to", DATA_TOPIC)
    payload = json.dumps({"experiment_id": "board-e2e", "sensor_data": reading})
    await client.publish(DATA_TOPIC, payload, qos=1)
    print("[6] published %d bytes" % len(payload))
    for _ in range(30):
        await asyncio.sleep(1)
        if received:
            break
    if received:
        print("[7] PASS -- round trip complete")
    else:
        print("[7] FAIL -- the broker took the subscription but delivered nothing.")
        print("     That is a broker permission problem, not a sensor problem.")


try:
    asyncio.run(asyncio.wait_for(run(), 120))
except Exception as e:
    print("ERROR:", repr(e))
finally:
    try:
        client.close()  # prevents LmacRxBlk:1 errors on the next run
    except Exception:
        pass
