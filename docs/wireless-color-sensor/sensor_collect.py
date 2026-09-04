#!/usr/bin/env python3
"""Command the wireless color sensor over MQTT and store its readings in MongoDB.

This is the missing link in the pipeline. The Pico W never writes to a database --
it only answers commands on MQTT:

    this script --> HiveMQ --> Pico W (AS7341) --> HiveMQ --> this script --> MongoDB

Requires MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, PICO_ID, and
(unless --no-store) MONGODB_URI / MONGODB_DATABASE.

    python sensor_collect.py --colors dark,red,yellow,blue,white
    python sensor_collect.py --repeat 10 --no-store
"""
import argparse, datetime, json, os, ssl, sys, time

import paho.mqtt.client as mqtt

PRESETS = {
    "dark": (0, 0, 0), "red": (255, 0, 0), "yellow": (0, 255, 0),
    "blue": (0, 0, 255), "white": (255, 255, 255),
}
CHANNELS = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]


def collect(args):
    pico = os.environ["PICO_ID"]
    data_topic = f"color-mixing/picow/{pico}/as7341"
    cmd_topic = f"command/picow/{pico}/as7341/read"
    probe_topic = f"{data_topic}/_probe"

    state = {"suback": None, "loopback": False, "msgs": []}

    def on_connect(c, u, flags, rc, props=None):
        print(f"[connect] CONNACK rc={rc}", flush=True)
        c.subscribe([(data_topic, 1), (probe_topic, 1)])

    def on_subscribe(c, u, mid, granted, props=None):
        state["suback"] = granted

    def on_message(c, u, msg):
        if msg.topic == probe_topic:
            state["loopback"] = True
            return
        state["msgs"].append((time.time(), msg.payload.decode("utf-8", "replace")))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    client.username_pw_set(os.environ["MQTT_USERNAME"], os.environ["MQTT_PASSWORD"])
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS_CLIENT)
    client.on_connect, client.on_subscribe, client.on_message = on_connect, on_subscribe, on_message
    client.connect(os.environ["MQTT_BROKER"], int(os.environ.get("MQTT_PORT", "8883")), 60)
    client.loop_start()

    deadline = time.time() + 20
    while state["suback"] is None and time.time() < deadline:
        time.sleep(0.2)
    if state["suback"] is None:
        sys.exit("[FAIL] no SUBACK -- broker refused the subscription")

    # A broker can answer "Granted QoS 1" and then deliver nothing when the
    # credential lacks read permission, which looks exactly like a silent sensor.
    # Echo a probe off our own topic to tell those two apart.
    client.publish(probe_topic, "probe", qos=1)
    time.sleep(3)
    print(f"[loopback] {'PASS' if state['loopback'] else 'FAIL -- broker permissions, not the sensor'}")

    rows, latencies = [], []
    for i, name in enumerate(args.colors * args.repeat):
        r, y, b = PRESETS[name]
        eid = f"{args.tag}-{name}-{i}-{int(time.time())}"
        # The firmware indexes incoming_dict["command"]["R"] and ["experiment_id"].
        # A flatter payload raises KeyError inside its handler and is swallowed by
        # the try/except, so the board stays silent and looks dead.
        payload = json.dumps({"command": {"R": r, "Y": y, "B": b}, "experiment_id": eid})
        n, sent = len(state["msgs"]), time.time()
        client.publish(cmd_topic, payload, qos=1)
        while len(state["msgs"]) == n and time.time() - sent < args.timeout:
            time.sleep(0.2)
        if len(state["msgs"]) == n:
            print(f"[{name:<6}] no reply within {args.timeout}s")
            continue
        rx_time, raw = state["msgs"][-1]
        latencies.append(rx_time - sent)
        doc = json.loads(raw)
        total = sum(doc["sensor_data"][c] for c in CHANNELS)
        print(f"[{name:<6}] {rx_time - sent:5.2f}s  total={total:<8} {doc['sensor_data']}")
        rows.append({
            "device_id": pico, "topic": data_topic, "experiment_id": doc.get("experiment_id"),
            "command": doc.get("command"), "sensor_data": doc.get("sensor_data"),
            "raw_payload": raw, "total_counts": total, "source": args.tag,
            "received_at": datetime.datetime.fromtimestamp(rx_time, datetime.timezone.utc),
        })
        time.sleep(args.interval)

    client.loop_stop()
    client.disconnect()
    if latencies:
        print(f"\n{len(rows)} reading(s), latency min={min(latencies):.2f}s max={max(latencies):.2f}s")
    return rows


def store(rows):
    from pymongo import MongoClient

    client = MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=20000)
    client.admin.command("ping")
    collection = client[os.environ.get("MONGODB_DATABASE", "digital-wetlab")]["sensor-data"]
    result = collection.insert_many(rows)
    print(f"[mongodb] stored {len(result.inserted_ids)} document(s) in sensor-data")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--colors", default="dark,red,yellow,blue,white",
                   help="comma-separated presets: " + ", ".join(PRESETS))
    p.add_argument("--repeat", type=int, default=1, help="passes over the colour list")
    p.add_argument("--interval", type=float, default=1.0, help="seconds between commands")
    p.add_argument("--timeout", type=float, default=25.0, help="seconds to await each reply")
    p.add_argument("--tag", default="sensor_collect", help="value stored in the `source` field")
    p.add_argument("--no-store", action="store_true", help="skip MongoDB, print only")
    args = p.parse_args()

    args.colors = [c.strip() for c in args.colors.split(",") if c.strip()]
    unknown = [c for c in args.colors if c not in PRESETS]
    if unknown:
        sys.exit(f"unknown colour(s): {unknown}")

    rows = collect(args)
    if not rows:
        sys.exit("[FAIL] the board answered nothing -- is it powered and off USB? see README.md")
    if not args.no_store:
        store(rows)


if __name__ == "__main__":
    main()
