# Read the AS7341 and publish over the board's own radio, so the reading
# travels wifi -> TLS -> broker rather than back down the USB cable.
import json, time, ssl, ntptime
from machine import Pin, I2C
from as7341_sensor import Sensor
import netman, my_secrets
from umqtt.simple import MQTTClient

CHAN = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
sensor = Sensor(i2c=i2c, gain=4)

print("[1] wifi ...")
netman.connectWiFi(my_secrets.SSID, my_secrets.PASSWORD, country="US")
import network
w = network.WLAN(network.STA_IF)
print("    connected:", w.isconnected(), " ip:", w.ifconfig()[0])

print("[2] ntp ...")
for _ in range(3):
    try:
        ntptime.settime(); print("    clock set"); break
    except Exception as e:
        print("    retry:", e); time.sleep(1)

print("[3] broker ...")
with open("hivemq-com-chain.der", "rb") as f:
    cadata = f.read()
c = MQTTClient("picow-issue33", my_secrets.HIVEMQ_HOST, port=8883,
               user=my_secrets.HIVEMQ_USERNAME, password=my_secrets.HIVEMQ_PASSWORD,
               keepalive=60, ssl=True,
               ssl_params={"server_hostname": my_secrets.HIVEMQ_HOST, "cadata": cadata})
c.connect()
print("    CONNECTED")

topic = "color-mixing/picow/%s/as7341" % my_secrets.PICO_ID
print("[4] publishing to", topic)
for i, (label, led) in enumerate((("dark", False), ("led_on", True),
                                  ("dark2", False), ("led_on2", True))):
    sensor.LED = led
    time.sleep(1.0 if led else 0.5)
    vals = list(sensor.all_channels)
    payload = {"sensor_data": dict(zip(CHAN, vals)),
               "experiment_id": "usb-wireless-%s-%d" % (label, i),
               "led": led, "gain": 4, "_utc": time.time()}
    c.publish(topic, json.dumps(payload).encode(), qos=0)
    print("    [%d] %-8s LED=%-5s total=%6d  published" % (i, label, led, sum(vals)))
    time.sleep(1.5)
sensor.LED = False
c.disconnect()
print("[5] done -- 4 readings published over wifi")
