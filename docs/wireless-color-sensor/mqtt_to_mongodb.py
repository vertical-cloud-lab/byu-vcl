"""Bridge: subscribe to the color sensor's MQTT topic, write readings to MongoDB.

The sensor never talks to the database. It publishes MQTT and stops there, so
something has to sit in the middle:

    Pico W  --TLS-->  broker  -->  THIS SCRIPT  -->  MongoDB

In the Acceleration Consortium deployment that middle box is a Hugging Face
Space, which only persists at the end of a full OT-2 experiment flow. This is
the standalone equivalent: every reading that arrives is stored, immediately,
with no experiment orchestration in the way. That makes it usable both as the
real bridge and as the "did the upload path work?" test.

    pip install paho-mqtt pymongo

    export HIVEMQ_HOST=abc123.s1.eu.hivemq.cloud   # bare host, no https://
    export HIVEMQ_USERNAME=... HIVEMQ_PASSWORD=...
    export MONGODB_CONNECTION_STRING=mongodb+srv://...
    export PICO_ID=...            # omit to accept readings from any device

    python mqtt_to_mongodb.py                 # run until interrupted
    python mqtt_to_mongodb.py --expect 3      # exit 0 after storing 3 readings
    python mqtt_to_mongodb.py --dry-run       # parse and print, never write

Exit code is 0 if the run met its expectation, 1 otherwise, so it works in CI.
"""

import argparse
import json
import os
import ssl
import sys
import time
import uuid
from datetime import datetime, timezone

try:
    import paho.mqtt.client as mqtt
except ImportError:
    sys.exit("missing dependency: pip install paho-mqtt")

CHANNEL_NAMES = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]

# CONNACK codes are the single most useful diagnostic this script produces, and
# paho's own string for them is vaguer than the fix that each one implies.
# Both numbering schemes appear in the wild: MQTT 3.1.1 brokers return 1-5,
# MQTT 5 brokers return 128+. paho reports whichever the broker used, so a table
# covering only one of them prints "see broker logs" exactly when the operator
# most needs the answer.
CONNACK_HELP = {
    # MQTT 3.1.1
    1: "broker refused the protocol version",
    2: "client id rejected",
    3: "broker unavailable",
    4: "bad username or password -- check HIVEMQ_USERNAME / HIVEMQ_PASSWORD",
    5: "not authorized -- the credential exists but lacks permission on this topic",
    # MQTT 5
    128: "unspecified error",
    132: "unsupported protocol version",
    133: "client id invalid",
    134: "bad username or password -- check HIVEMQ_USERNAME / HIVEMQ_PASSWORD",
    135: "not authorized -- wrong password, or the credential lacks permission "
         "on this topic (HiveMQ grants publish and subscribe separately)",
    136: "server unavailable",
    137: "server busy",
    138: "banned",
    140: "bad authentication method",
    144: "topic name invalid",
    149: "packet too large",
    151: "quota exceeded",
    153: "payload format invalid",
    159: "connection rate exceeded",
}


def log(msg):
    print("{}  {}".format(datetime.now(timezone.utc).strftime("%H:%M:%S"), msg), flush=True)


def build_document(topic, payload_text):
    """Turn one MQTT message into the document that gets stored.

    Kept deliberately flat and explicit: the sensor's own fields are preserved
    verbatim under `sensor_data` so that a document is always traceable back to
    what the device actually sent, with the bridge's additions alongside rather
    than mixed in.
    """
    doc = {
        "received_at": datetime.now(timezone.utc),
        "topic": topic,
        "device_id": None,
        "experiment_id": None,
        "command": None,
        "sensor_data": None,
        "raw": payload_text,
        "malformed": False,
    }

    # topic looks like color-mixing/picow/{PICO_ID}/as7341
    parts = topic.split("/")
    if len(parts) >= 3:
        doc["device_id"] = parts[2]

    try:
        payload = json.loads(payload_text)
    except (ValueError, TypeError):
        # Store it anyway. A malformed payload that is silently dropped is far
        # harder to debug later than one sitting in the collection flagged.
        doc["malformed"] = True
        return doc

    if not isinstance(payload, dict):
        doc["malformed"] = True
        return doc

    doc["experiment_id"] = payload.get("experiment_id")
    doc["command"] = payload.get("command")

    sensor_data = payload.get("sensor_data")
    if isinstance(sensor_data, dict):
        doc["sensor_data"] = sensor_data
    elif all(k in payload for k in CHANNEL_NAMES):
        # Some firmware revisions publish the channels at the top level.
        doc["sensor_data"] = {k: payload[k] for k in CHANNEL_NAMES}
    else:
        doc["malformed"] = True

    if isinstance(doc["sensor_data"], dict):
        missing = [c for c in CHANNEL_NAMES if c not in doc["sensor_data"]]
        if missing:
            doc["missing_channels"] = missing

    return doc


def describe(doc):
    """One-line human summary, including which color the reading looks like."""
    sd = doc.get("sensor_data")
    if not isinstance(sd, dict):
        return "malformed payload ({} bytes)".format(len(doc.get("raw") or ""))
    vals = {}
    for c in CHANNEL_NAMES:
        try:
            vals[c] = float(sd.get(c, 0))
        except (TypeError, ValueError):
            vals[c] = 0.0

    # Average rather than sum: blue spans three channels and red and green two
    # each, so summing would report a neutral white reading as blue.
    def mean(names):
        return sum(vals[n] for n in names) / len(names)

    blue = mean(["ch410", "ch440", "ch470"])
    green = mean(["ch510", "ch550"])
    red = mean(["ch620", "ch670"])

    bands = [("blue", blue), ("green", green), ("red", red)]
    name, high = max(bands, key=lambda x: x[1])
    low = min(v for _, v in bands)

    if high < 30:
        label = "dark"
    elif low <= 0 or high / low < 1.25:
        # No band stands out -- broadband illumination, not a hue.
        label = "white"
    else:
        label = name

    return "{} looks {:>5}  (B={:.0f} G={:.0f} R={:.0f})".format(
        doc.get("experiment_id") or "-", label, blue, green, red
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect", type=int, default=0,
                        help="exit 0 once this many readings are stored (0 = run forever)")
    parser.add_argument("--timeout", type=float, default=60.0,
                        help="seconds to wait for --expect readings")
    parser.add_argument("--dry-run", action="store_true", help="never write to MongoDB")
    parser.add_argument("--no-tls", action="store_true", help="plaintext broker (local testing)")
    parser.add_argument("--ca-cert", default=os.environ.get("MQTT_CA_CERT"),
                        help="CA bundle for a broker with a private cert")
    parser.add_argument("--topic", default=None, help="override the subscribe topic")
    parser.add_argument("--loopback", action="store_true",
                        help="publish a probe to our own topic to prove the subscribe "
                             "path works before blaming the sensor for silence")
    args = parser.parse_args()

    host = os.environ.get("HIVEMQ_HOST") or os.environ.get("MQTT_HOST")
    username = os.environ.get("HIVEMQ_USERNAME") or os.environ.get("MQTT_USERNAME")
    password = os.environ.get("HIVEMQ_PASSWORD") or os.environ.get("MQTT_PASSWORD")
    port = int(os.environ.get("HIVEMQ_PORT") or os.environ.get("MQTT_PORT") or
               (1883 if args.no_tls else 8883))
    pico_id = os.environ.get("PICO_ID")
    mongo_uri = os.environ.get("MONGODB_CONNECTION_STRING")
    mongo_db = os.environ.get("MONGODB_DATABASE", "vcl")
    mongo_coll = os.environ.get("MONGODB_COLLECTION", "color_sensor_readings")

    if not host:
        sys.exit("HIVEMQ_HOST is not set -- nothing to connect to")

    topic = args.topic or "color-mixing/picow/{}/as7341".format(pico_id or "+")
    log("broker    {}:{} tls={}".format(host, port, not args.no_tls))
    log("topic     {}".format(topic))

    collection = None
    if args.dry_run:
        log("mongo     (dry run -- not writing)")
    elif not mongo_uri:
        log("mongo     MONGODB_CONNECTION_STRING not set -- readings will be printed only")
    else:
        try:
            from pymongo import MongoClient
        except ImportError:
            sys.exit("missing dependency: pip install pymongo")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        try:
            client.admin.command("ping")
        except Exception as exc:
            sys.exit("MongoDB unreachable: {}\n-> check the connection string, the "
                     "database user's password, and that network access allows "
                     "0.0.0.0/0 (CI runners have dynamic IPs)".format(exc))
        collection = client[mongo_db][mongo_coll]
        log("mongo     connected -> {}.{}".format(mongo_db, mongo_coll))

    probe_nonce = "loopback-{}".format(uuid.uuid4())
    state = {"stored": 0, "seen": 0, "subscribed": False, "connack": None,
             "probe_echoed": False}

    def on_connect(client, userdata, flags, rc, properties=None):
        code = getattr(rc, "value", rc)
        state["connack"] = code
        if code != 0:
            log("CONNECT REFUSED rc={} -- {}".format(code, CONNACK_HELP.get(code, "see broker logs")))
            return
        log("connected")
        client.subscribe(topic, qos=1)

    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        # A granted QoS of 128 is a *rejected* subscription that otherwise looks
        # like success -- the classic silent failure with per-topic ACLs.
        codes = [getattr(g, "value", g) for g in granted_qos] if granted_qos else []
        if any(c == 128 for c in codes):
            log("SUBSCRIBE REJECTED for {} -- the credential lacks subscribe "
                "permission on this topic".format(topic))
            return
        state["subscribed"] = True
        log("subscribed to {}".format(topic))
        if args.loopback:
            # A SUBACK of "success" does not prove the broker will actually
            # deliver: with per-topic permissions a credential can be granted
            # the subscription and then silently receive nothing. Publishing to
            # our own topic and waiting for the echo is the only way to tell
            # that apart from a sensor that simply is not publishing.
            client.publish(topic, json.dumps({"loopback_probe": probe_nonce}), qos=1)
            log("loopback  probe published, waiting for it to come back...")

    def on_message(client, userdata, msg):
        payload_text = msg.payload.decode("utf-8", "replace")
        if probe_nonce in payload_text:
            state["probe_echoed"] = True
            log("loopback  PASS -- the broker delivers on this topic, so the "
                "subscribe path is good")
            return
        state["seen"] += 1
        doc = build_document(msg.topic, payload_text)
        if collection is not None:
            try:
                result = collection.insert_one(doc)
                state["stored"] += 1
                log("stored _id={}  {}".format(result.inserted_id, describe(doc)))
            except Exception as exc:
                log("INSERT FAILED: {} -- check the database user's write permission".format(exc))
        else:
            state["stored"] += 1
            log("received      {}".format(describe(doc)))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id="vcl-bridge-{}".format(int(time.time())))
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    if username:
        client.username_pw_set(username, password)
    if not args.no_tls:
        if args.ca_cert:
            client.tls_set(ca_certs=args.ca_cert, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        else:
            client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

    try:
        client.connect(host, port, keepalive=60)
    except Exception as exc:
        sys.exit("could not reach the broker: {}\n-> check HIVEMQ_HOST is a bare "
                 "hostname (no https://) and that port {} is open".format(exc, port))

    client.loop_start()
    deadline = time.time() + args.timeout
    try:
        while True:
            if args.expect and state["stored"] >= args.expect:
                break
            if args.expect and time.time() > deadline:
                break
            if state["connack"] not in (None, 0):
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        log("interrupted")
    finally:
        client.loop_stop()
        client.disconnect()

    log("done -- {} message(s) received, {} stored".format(state["seen"], state["stored"]))

    if args.expect:
        if state["stored"] >= args.expect:
            return 0
        if not state["subscribed"]:
            log("never subscribed -- see the CONNECT/SUBSCRIBE lines above")
        elif args.loopback and not state["probe_echoed"]:
            log("loopback  FAIL -- the broker acknowledged the subscription but did "
                "not deliver our own probe back to us.")
            log("-> this is a BROKER PERMISSION problem, not a sensor problem: the "
                "credential lacks subscribe/read access on {}".format(topic))
            log("-> in HiveMQ, grant this credential both publish AND subscribe on "
                "the topic pattern (they are separate permissions)")
        elif args.loopback:
            log("the subscribe path is proven good (loopback passed), so the silence "
                "is the sensor's: is it powered, running main.py rather than sitting "
                "at the REPL, and publishing on {}?".format(topic))
        else:
            log("subscribed but nothing arrived. This is ambiguous -- the sensor may "
                "be silent, OR the credential may lack subscribe permission (a broker "
                "can ACK a subscription and still deliver nothing).")
            log("-> re-run with --loopback to tell those two apart")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
