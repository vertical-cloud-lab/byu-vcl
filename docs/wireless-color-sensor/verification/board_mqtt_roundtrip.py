"""Full wireless round trip, executed ON the Pico using its own my_secrets.py.

Run ON the Pico:  mpremote connect /dev/ttyACM0 run board_mqtt_roundtrip.py

Subscribing to our own topic before publishing is deliberate. A broker can
acknowledge a subscription and then deliver nothing when the credential lacks
read permission, which from the subscriber's side is indistinguishable from a
silent sensor. Waiting for our own message to come back tells those apart.
"""
import network
import ntptime
import ssl
import json
import time
import socket
from machine import I2C, Pin
from as7341_sensor import Sensor
from umqtt.simple import MQTTClient
from my_secrets import (
    SSID, PASSWORD, HIVEMQ_HOST, HIVEMQ_USERNAME, HIVEMQ_PASSWORD, PICO_ID,
)

CHANNELS = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]

print("[1] sensor")
s = Sensor(gain=4, i2c=I2C(0, scl=Pin(5), sda=Pin(4)))
s.LED = True
time.sleep(1)
lit = s.all_channels
s.LED = False
time.sleep(0.5)
dark = s.all_channels
print("    lit total =", sum(lit), " dark total =", sum(dark))

print("[2] wifi")
w = network.WLAN(network.STA_IF)
w.active(True)
if not w.isconnected():
    w.connect(SSID, PASSWORD)
    for _ in range(40):
        if w.isconnected():
            break
        time.sleep(0.5)
print("    connected =", w.isconnected())
ip, _, gw, _ = w.ifconfig()
print("    pico IP   =", ip, " gateway =", gw, " RSSI =", w.status("rssi"))

print("[3] ntp")
ntptime.timeout = 5
ntptime.host = "time.google.com"
try:
    ntptime.settime()
    print("    clock set:", time.localtime()[:6])
except Exception as e:
    # A wrong clock invalidates every certificate, so this failing explains a
    # later TLS failure that would otherwise look like a bad CA file.
    print("    ntp failed:", e)

print("[4] resolve broker")
print("    broker addr =", socket.getaddrinfo(HIVEMQ_HOST, 8883)[0][-1])

print("[5] tls + broker connect")
with open("hivemq-com-chain.der", "rb") as f:
    cacert = f.read()
topic = ("color-mixing/picow/%s/as7341" % PICO_ID).encode()
c = MQTTClient(
    ("verify-%s" % PICO_ID).encode(), HIVEMQ_HOST, 8883,
    HIVEMQ_USERNAME, HIVEMQ_PASSWORD, keepalive=30, ssl=True,
    ssl_params={"server_side": False, "key": None, "cert": None,
                "cert_reqs": ssl.CERT_REQUIRED, "cadata": cacert,
                "server_hostname": HIVEMQ_HOST},
)
got = []
c.set_callback(lambda t, m: got.append((t, m)))
c.connect()
print("    CONNECTED to", HIVEMQ_HOST[:6] + "..." + HIVEMQ_HOST[-18:])

print("[6] subscribe to own topic, then publish -- loopback proof")
c.subscribe(topic)
for trial in range(3):
    got.clear()
    payload = json.dumps({
        "trial": trial,
        "_input_message": "verify",
        "sensor_data": dict(zip(CHANNELS, [int(x) for x in lit])),
    })
    c.publish(topic, payload.encode())
    deadline = time.time() + 10
    while not got and time.time() < deadline:
        c.check_msg()
        time.sleep(0.2)
    if got:
        print("    trial %d: ROUND TRIP OK  (%d bytes returned by broker)"
              % (trial, len(got[0][1])))
    else:
        print("    trial %d: published but NOTHING came back -- broker permission,"
              " not the sensor" % trial)
c.disconnect()
print("[7] done")
