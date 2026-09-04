"""Negative control: prove the broker path really runs over the Pico's own radio.

Run ON the Pico:  mpremote connect /dev/ttyACM0 run board_wifi_negative_control.py

When the board is driven over USB it is fair to ask whether a "broker connected"
message means the board reached the internet, or whether the host did it. Turning
the radio off answers that: the USB link keeps printing while the broker becomes
unreachable, then recovers when the radio comes back.
"""
import network
import ssl
import time
from umqtt.simple import MQTTClient
from my_secrets import SSID, PASSWORD, HIVEMQ_HOST, HIVEMQ_USERNAME, HIVEMQ_PASSWORD

with open("hivemq-com-chain.der", "rb") as f:
    cacert = f.read()


def mk():
    return MQTTClient(
        b"negctl", HIVEMQ_HOST, 8883, HIVEMQ_USERNAME, HIVEMQ_PASSWORD,
        keepalive=30, ssl=True,
        ssl_params={"server_side": False, "key": None, "cert": None,
                    "cert_reqs": ssl.CERT_REQUIRED, "cadata": cacert,
                    "server_hostname": HIVEMQ_HOST},
    )


w = network.WLAN(network.STA_IF)

print("=== A. radio OFF ===")
w.active(False)
time.sleep(3)
print("    wifi active:", w.active(), " connected:", w.isconnected())
print("    (this line still reaches you -- the USB/SSH link is alive)")
try:
    mk().connect()
    print("    broker connect: SUCCEEDED  <-- unexpected; the path is not what we think")
except Exception as e:
    print("    broker connect: FAILED as expected ->", repr(e)[:70])

print("=== B. radio back ON ===")
w.active(True)
w.connect(SSID, PASSWORD)
for _ in range(40):
    if w.isconnected():
        break
    time.sleep(0.5)
print("    wifi connected:", w.isconnected(), " IP:", w.ifconfig()[0])
try:
    c = mk()
    c.connect()
    print("    broker connect: SUCCEEDED")
    c.disconnect()
except Exception as e:
    print("    broker connect: FAILED ->", repr(e)[:70])
