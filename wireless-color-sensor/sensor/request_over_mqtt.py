"""Host-side driver: request a reading from the Pico W over HiveMQ (MQTT).

This is the *wireless* path -- it matches the topic/payload contract in the
upstream demo firmware (``sensor_file/main.py`` of
AccelerationConsortium/wireless-color-sensor):

* publish to   ``command/picow/{PICO_ID}/as7341/read``
* subscribe to ``color-mixing/picow/{PICO_ID}/as7341``

The request payload must carry ``command`` (with ``R``/``Y``/``B``, unused by
the sensor itself but required by the firmware's parser) and ``experiment_id``.
The reply echoes the request with a ``sensor_data`` dict added.

Credentials come from ``my_secrets.py`` next to this file (git-ignored; copy
``my_secrets.example.py``) or from the environment:

    HIVEMQ_HOST  HIVEMQ_USERNAME  HIVEMQ_PASSWORD  PICO_ID

Usage::

    pip install paho-mqtt
    python request_over_mqtt.py --out reading.json

Caveat worth knowing before you rely on this: the demo firmware currently
returns **only the 8 spectral channels** -- no Clear, no NIR, and no flicker
frequency. To get intensity + flicker wirelessly, the Pico's ``main.py`` has to
be extended (see ``README.md`` in this directory). Until then, the USB path
(``collect_over_serial.py``) is the one that returns the full set.
"""

import argparse
import json
import os
import ssl
import sys
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:  # pragma: no cover - dependency hint
    sys.exit("paho-mqtt is required:  pip install paho-mqtt")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def load_config():
    """Read broker settings from my_secrets.py, falling back to the env."""
    cfg = {}
    try:
        import my_secrets  # type: ignore

        for key in ("HIVEMQ_HOST", "HIVEMQ_USERNAME", "HIVEMQ_PASSWORD", "PICO_ID"):
            value = getattr(my_secrets, key, None)
            if value and value.strip():
                cfg[key] = value.strip()
    except ImportError:
        pass

    for key in ("HIVEMQ_HOST", "HIVEMQ_USERNAME", "HIVEMQ_PASSWORD", "PICO_ID"):
        cfg.setdefault(key, os.environ.get(key, "").strip())

    missing = [k for k, v in cfg.items() if not v]
    if missing:
        raise SystemExit(
            "Missing MQTT settings: %s. Copy my_secrets.example.py to "
            "my_secrets.py and fill it in, or set them in the environment."
            % ", ".join(sorted(missing))
        )
    return cfg


def request(cfg, timeout=30.0, port=8883):
    command_topic = "command/picow/%s/as7341/read" % cfg["PICO_ID"]
    data_topic = "color-mixing/picow/%s/as7341" % cfg["PICO_ID"]
    experiment_id = "wcs-%d" % int(time.time())

    received = {}

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc != 0:
            raise SystemExit("MQTT connect failed with code %s" % rc)
        client.subscribe(data_topic, qos=1)

    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        payload = json.dumps(
            {
                "command": {"R": 0, "Y": 0, "B": 0},
                "experiment_id": experiment_id,
            }
        )
        client.publish(command_topic, payload, qos=1)

    def on_message(client, userdata, msg):
        received["payload"] = json.loads(msg.payload.decode())
        client.disconnect()

    try:  # paho-mqtt 2.x
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:  # paho-mqtt 1.x
        client = mqtt.Client()

    client.username_pw_set(cfg["HIVEMQ_USERNAME"], cfg["HIVEMQ_PASSWORD"])
    client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    print("connecting to %s:%d ..." % (cfg["HIVEMQ_HOST"], port))
    client.connect(cfg["HIVEMQ_HOST"], port, keepalive=60)
    client.loop_start()

    deadline = time.time() + timeout
    while "payload" not in received and time.time() < deadline:
        time.sleep(0.1)
    client.loop_stop()

    if "payload" not in received:
        raise SystemExit(
            "No reply on %s within %.0f s -- is the Pico powered, on WiFi, and "
            "running main.py?" % (data_topic, timeout)
        )
    return received["payload"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--port", type=int, default=8883, help="broker TLS port")
    ap.add_argument("--out", help="write the reply as JSON to this path")
    args = ap.parse_args()

    payload = request(load_config(), timeout=args.timeout, port=args.port)
    print(json.dumps(payload, indent=2))

    if args.out:
        with open(args.out, "w") as fh:
            json.dump(payload, fh, indent=2)
        print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
