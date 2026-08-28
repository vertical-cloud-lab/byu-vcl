"""Stand in for the Pico W: publish AS7341 readings over MQTT.

Exists so the upload half of the pipeline can be tested while the hardware is
on someone's desk. It publishes the exact payload shape the real firmware
publishes, on the same topic, so a bridge or subscriber cannot tell the
difference.

    export HIVEMQ_HOST=... HIVEMQ_USERNAME=... HIVEMQ_PASSWORD=... PICO_ID=...
    python simulate_sensor.py --colors red green blue

If a run of the real pipeline fails, this tells you which side to blame: swap
the real sensor for this and if the reading lands in MongoDB, the broker,
bridge and database are all fine and the problem is on the device.
"""

import argparse
import json
import os
import ssl
import sys
import time
import uuid

try:
    import paho.mqtt.client as mqtt
except ImportError:
    sys.exit("missing dependency: pip install paho-mqtt")

CHANNEL_NAMES = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]

# Channel counts roughly as an AS7341 reports them under its NeoPixel at full
# brightness -- the point is the spectral shape, not absolute calibration.
# Under red light the long-wavelength channels dominate, under blue the short.
PROFILES = {
    "off":   [12, 15, 18, 20, 22, 21, 19, 14],
    "red":   [31, 38, 45, 78, 190, 402, 921, 874],
    "green": [44, 96, 210, 688, 812, 402, 150, 88],
    "blue":  [742, 908, 655, 214, 96, 52, 38, 30],
    "white": [512, 588, 604, 631, 655, 620, 588, 540],
}


def reading(color):
    counts = PROFILES[color]
    return {c: v for c, v in zip(CHANNEL_NAMES, counts)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--colors", nargs="+", default=["red", "green", "blue"],
                        choices=sorted(PROFILES), help="colors to publish, in order")
    parser.add_argument("--interval", type=float, default=1.0, help="seconds between publishes")
    parser.add_argument("--no-tls", action="store_true")
    parser.add_argument("--ca-cert", default=os.environ.get("MQTT_CA_CERT"))
    args = parser.parse_args()

    host = os.environ.get("HIVEMQ_HOST") or os.environ.get("MQTT_HOST")
    username = os.environ.get("HIVEMQ_USERNAME") or os.environ.get("MQTT_USERNAME")
    password = os.environ.get("HIVEMQ_PASSWORD") or os.environ.get("MQTT_PASSWORD")
    port = int(os.environ.get("HIVEMQ_PORT") or os.environ.get("MQTT_PORT") or
               (1883 if args.no_tls else 8883))
    pico_id = os.environ.get("PICO_ID", "simulated")
    if not host:
        sys.exit("HIVEMQ_HOST is not set")

    topic = "color-mixing/picow/{}/as7341".format(pico_id)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id="vcl-sim-{}".format(int(time.time())))
    if username:
        client.username_pw_set(username, password)
    if not args.no_tls:
        if args.ca_cert:
            client.tls_set(ca_certs=args.ca_cert, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        else:
            client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

    client.connect(host, port, keepalive=60)
    client.loop_start()
    print("publishing to {}".format(topic), flush=True)

    for color in args.colors:
        payload = {
            "experiment_id": str(uuid.uuid4()),
            "command": {"R": 255 if color == "red" else 0,
                        "Y": 255 if color == "green" else 0,
                        "B": 255 if color == "blue" else 0},
            "sensor_data": reading(color),
            "simulated": True,
            "simulated_color": color,
        }
        info = client.publish(topic, json.dumps(payload), qos=1)
        info.wait_for_publish(timeout=10)
        print("  published {:>5}  {}".format(color, json.dumps(payload["sensor_data"])), flush=True)
        time.sleep(args.interval)

    client.loop_stop()
    client.disconnect()
    print("done -- {} reading(s) published".format(len(args.colors)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
