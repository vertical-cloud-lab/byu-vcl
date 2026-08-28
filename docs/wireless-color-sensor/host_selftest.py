"""Staged diagnostic for the color sensor's upload path (host side).

Runs on a laptop, a Raspberry Pi, or a GitHub Actions runner -- anywhere with
normal CPython. It verifies the half of the pipeline that lives off the Pico:

    HiveMQ broker  ->  subscriber  ->  MongoDB

Each stage prints PASS/FAIL with a specific remedy, so a failure identifies the
broken link instead of just reporting "no data".

    pip install paho-mqtt pymongo

    export HIVEMQ_HOST=...            # e.g. abc123.s1.eu.hivemq.cloud
    export HIVEMQ_USERNAME=...
    export HIVEMQ_PASSWORD=...
    export PICO_ID=...                # the sensor's device id
    export MONGODB_CONNECTION_STRING=...   # optional; stages G-H skip without it

    python host_selftest.py            # listen only
    python host_selftest.py --command  # also send a read command to the sensor

Exit code is 0 if every attempted stage passed, 1 otherwise.
"""

import argparse
import json
import os
import socket
import ssl
import sys
import time
import uuid

CHANNEL_NAMES = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]

results = []


def stage(letter, title):
    print("\n[{}] {}".format(letter, title))
    print("-" * 60)


def ok(letter, detail=""):
    results.append((letter, "PASS"))
    print("  PASS {}".format(detail))


def bad(letter, err, remedy):
    results.append((letter, "FAIL"))
    print("  FAIL {}".format(err))
    print("  -> {}".format(remedy))


def skip(letter, why):
    results.append((letter, "SKIP"))
    print("  SKIP {}".format(why))


parser = argparse.ArgumentParser()
parser.add_argument("--command", action="store_true",
                    help="publish a read command and wait for the sensor to answer")
parser.add_argument("--listen-seconds", type=int, default=30,
                    help="how long to wait for sensor data (default 30)")
parser.add_argument("--anonymous", action="store_true",
                    help="connect without credentials -- use against a local mosquitto "
                         "broker to prove the sensor/subscriber logic works "
                         "independently of HiveMQ auth")
parser.add_argument("--ca-cert", default=os.getenv("MQTT_CA_CERT"),
                    help="CA bundle for a broker using a private certificate; "
                         "omit for HiveMQ Cloud, which uses a public CA")
args = parser.parse_args()

HIVEMQ_HOST = os.getenv("HIVEMQ_HOST", "")
HIVEMQ_USERNAME = os.getenv("HIVEMQ_USERNAME", "")
HIVEMQ_PASSWORD = os.getenv("HIVEMQ_PASSWORD", "")
HIVEMQ_PORT = int(os.getenv("HIVEMQ_PORT", "8883"))
PICO_ID = os.getenv("PICO_ID", "")
MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING", "")

DATA_TOPIC = "color-mixing/picow/{}/as7341".format(PICO_ID or "+")
COMMAND_TOPIC = "command/picow/{}/as7341/read".format(PICO_ID)


# --------------------------------------------------------------------------
stage("A", "Credentials present in the environment")
required = {"HIVEMQ_HOST": HIVEMQ_HOST, "PICO_ID": PICO_ID}
if not args.anonymous:
    required["HIVEMQ_USERNAME"] = HIVEMQ_USERNAME
    required["HIVEMQ_PASSWORD"] = HIVEMQ_PASSWORD
missing = [k for k, v in required.items() if not v]
for k, v in required.items():
    print("  {:<20} {}".format(k, "set" if v else "MISSING"))
print("  {:<20} {}".format("MONGODB_CONNECTION_STRING", "set" if MONGO_URI else "not set (stages G-H will skip)"))
if missing:
    bad("A", "missing: {}".format(", ".join(missing)),
        "Export these before running. In CI they must also be added to the env: "
        "block of .github/workflows/claude.yml, which requires a human commit -- "
        "the GitHub App cannot edit workflow files.")
    print("\nCannot continue without broker credentials.")
    sys.exit(1)
ok("A", "broker credentials present")


# --------------------------------------------------------------------------
stage("B", "DNS resolution of the broker hostname")
try:
    addrs = socket.getaddrinfo(HIVEMQ_HOST, HIVEMQ_PORT, proto=socket.IPPROTO_TCP)
    print("  resolved to {} address(es)".format(len(addrs)))
    ok("B")
except Exception as e:
    bad("B", repr(e),
        "HIVEMQ_HOST should be a bare hostname like 'abc123.s1.eu.hivemq.cloud' -- "
        "no 'https://', no port, no trailing slash.")
    sys.exit(1)


# --------------------------------------------------------------------------
stage("C", "TCP + TLS handshake on port {}".format(HIVEMQ_PORT))
try:
    ctx = ssl.create_default_context(cafile=args.ca_cert) if args.ca_cert \
        else ssl.create_default_context()
    with socket.create_connection((HIVEMQ_HOST, HIVEMQ_PORT), timeout=15) as raw:
        with ctx.wrap_socket(raw, server_hostname=HIVEMQ_HOST) as tls:
            print("  TLS {} / {}".format(tls.version(), tls.cipher()[0]))
    ok("C", "handshake succeeded")
except ssl.SSLCertVerificationError as e:
    bad("C", repr(e), "Certificate verification failed -- check the system clock first.")
    sys.exit(1)
except Exception as e:
    bad("C", repr(e),
        "Port 8883 is likely blocked by a firewall. Campus networks often block "
        "non-standard outbound ports; try a phone hotspot to confirm.")
    sys.exit(1)


# --------------------------------------------------------------------------
stage("D", "MQTT authentication")
try:
    import paho.mqtt.client as mqtt
except ImportError:
    bad("D", "paho-mqtt not installed", "pip install paho-mqtt")
    sys.exit(1)

# paho 2.x renamed the constructor; support both so this runs anywhere.
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,
                         client_id="host-selftest-" + uuid.uuid4().hex[:8])
except AttributeError:
    client = mqtt.Client(client_id="host-selftest-" + uuid.uuid4().hex[:8])

if args.anonymous:
    print("  --anonymous: connecting without credentials")
else:
    client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
client.tls_set(ca_certs=args.ca_cert, tls_version=ssl.PROTOCOL_TLS_CLIENT)

state = {"rc": None, "messages": [], "suback": False}


def on_connect(c, userdata, flags, rc, *a):
    state["rc"] = rc


def on_subscribe(c, userdata, mid, granted_qos, *a):
    state["suback"] = True


def on_message(c, userdata, msg):
    state["messages"].append((msg.topic, msg.payload))


client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message

try:
    client.connect(HIVEMQ_HOST, HIVEMQ_PORT, keepalive=30)
    client.loop_start()
    for _ in range(150):
        if state["rc"] is not None:
            break
        time.sleep(0.1)

    rc = state["rc"]
    if rc == 0:
        ok("D", "connected anonymously" if args.anonymous
                 else "authenticated as '{}'".format(HIVEMQ_USERNAME))
    else:
        hints = {
            4: "Bad username or password.",
            5: "Not authorized -- the credential exists but lacks permissions.",
        }
        bad("D", "CONNACK rc={}".format(rc),
            hints.get(rc, "Broker refused the connection.") +
            " Check HiveMQ console -> Access Management.")
        client.loop_stop()
        sys.exit(1)
except Exception as e:
    bad("D", repr(e), "Connection attempt raised before CONNACK.")
    sys.exit(1)


# --------------------------------------------------------------------------
stage("E", "Subscribe to the sensor data topic")
print("  topic: {}".format(DATA_TOPIC))
try:
    client.subscribe(DATA_TOPIC, qos=1)
    for _ in range(100):
        if state["suback"]:
            break
        time.sleep(0.1)
    if state["suback"]:
        ok("E", "SUBACK received")
    else:
        bad("E", "no SUBACK within 10s",
            "The credential can connect but may not have SUBSCRIBE permission for "
            "this topic. In HiveMQ, grant subscribe on 'color-mixing/#'.")
except Exception as e:
    bad("E", repr(e), "Subscribe failed.")


# --------------------------------------------------------------------------
stage("F", "Receive a reading from the sensor")
if args.command:
    experiment_id = "selftest-" + uuid.uuid4().hex[:8]
    cmd = json.dumps({"command": {"R": 0, "Y": 0, "B": 0}, "experiment_id": experiment_id})
    print("  publishing command to {}".format(COMMAND_TOPIC))
    client.publish(COMMAND_TOPIC, cmd, qos=1)
else:
    print("  passive listen (pass --command to actively trigger a reading)")

print("  waiting up to {}s...".format(args.listen_seconds))
deadline = time.time() + args.listen_seconds
while time.time() < deadline and not state["messages"]:
    time.sleep(0.5)

reading = None
if state["messages"]:
    topic, raw = state["messages"][0]
    print("  received on {}".format(topic))
    try:
        parsed = json.loads(raw.decode())
        print("  {}".format(json.dumps(parsed, indent=2)[:600]))
        sensor_data = parsed.get("sensor_data", {})
        got = [c for c in CHANNEL_NAMES if c in sensor_data]
        if len(got) == 8:
            reading = parsed
            ok("F", "all 8 channels present")
        else:
            bad("F", "payload has {}/8 expected channels".format(len(got)),
                "The sensor published, but not in the expected schema. Check that "
                "main.py on the Pico is the current version.")
    except Exception as e:
        bad("F", "unparseable payload: {}".format(e), "Expected JSON.")
else:
    bad("F", "no message received in {}s".format(args.listen_seconds),
        "Broker connectivity is fine (stages C-E passed), so the sensor itself is "
        "not publishing. Check: (1) is the Pico powered and running main.py, not "
        "sitting at the REPL? (2) did it join WiFi? (3) does PICO_ID here match the "
        "device exactly? Run pico_selftest.py on the board to find out which.")


# --------------------------------------------------------------------------
stage("G", "MongoDB connection")
db = None
if not MONGO_URI:
    skip("G", "MONGODB_CONNECTION_STRING not set -- no database provisioned yet")
else:
    try:
        from pymongo import MongoClient

        mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000)
        mongo.admin.command("ping")
        db = mongo[os.getenv("MONGODB_DATABASE", "byu-vcl")]
        ok("G", "ping succeeded, database '{}'".format(db.name))
    except ImportError:
        bad("G", "pymongo not installed", "pip install pymongo")
    except Exception as e:
        bad("G", repr(e),
            "Common causes: the runner's IP is not in the Atlas network access list "
            "(set 0.0.0.0/0 -- CI runners have dynamic IPs), a wrong password, or an "
            "unescaped special character in the password inside the URI.")


# --------------------------------------------------------------------------
stage("H", "Write a reading to MongoDB and read it back")
if db is None:
    skip("H", "no database connection")
else:
    try:
        from datetime import datetime, timezone

        collection = db[os.getenv("MONGODB_COLLECTION", "color_sensor_readings")]
        doc = {
            "source": "host_selftest",
            "pico_id": PICO_ID,
            "timestamp": datetime.now(timezone.utc),
            "sensor_data": (reading or {}).get(
                "sensor_data", {c: None for c in CHANNEL_NAMES}
            ),
            "synthetic": reading is None,
        }
        inserted = collection.insert_one(doc).inserted_id
        print("  inserted _id={}".format(inserted))

        back = collection.find_one({"_id": inserted})
        if back is None:
            bad("H", "insert reported success but read-back returned nothing",
                "Check that the DB user has read permission, not just write.")
        else:
            ok("H", "round-trip verified in '{}.{}'".format(db.name, collection.name))
            if reading is None:
                print("  NOTE: stage F produced no real reading, so this document is")
                print("  synthetic. It proves the DB path works, not the full chain.")
    except Exception as e:
        bad("H", repr(e),
            "Connection succeeded but the write failed -- almost always a "
            "least-privilege DB user without readWrite on this database.")


# --------------------------------------------------------------------------
try:
    client.loop_stop()
    client.disconnect()
except Exception:
    pass

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for letter, status in results:
    print("  stage {}: {}".format(letter, status))

failures = [l for l, s in results if s == "FAIL"]
if failures:
    print("\nFirst failure: stage {}. Later stages depend on it.".format(failures[0]))
    sys.exit(1)
print("\nAll attempted stages passed.")
sys.exit(0)
