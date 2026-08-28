#!/usr/bin/env python3
"""End-to-end: read the wireless color sensor over MQTT and upload to MongoDB.

Requested by @timothy-commins in PR #60: *"run a simple test where the color
sensor reads for some colors and to see if it can upload that data to our
database ... document the whole process so that we can tell where errors occur
if they show up"*.

The point of this script is **failure localization**. The path from the AS7341
to the database crosses six independent systems (this host's network, the
HiveMQ broker, the lab WiFi, the Pico W, the sensor's I2C bus, MongoDB Atlas),
and "it didn't work" is useless when any of them can be the culprit. So the run
is split into numbered stages, each of which prints ``PASS``/``FAIL`` with a
distinct exit code and a one-line remedy:

    stage                          exit  what a failure means
    S1  broker DNS + TCP             10  this host has no route/DNS to HiveMQ
    S2  TLS + MQTT auth              20  credentials wrong, or account suspended
    S3  subscribe to reply topic     30  broker ACL forbids the topic
    S4  sensor round-trip            40  Pico offline / off WiFi / main.py dead
    S5  payload validation           50  Pico replied but the reading is unusable
    S6  color derivation             60  (pure math; only fails on a code bug)
    S7  local artifact write         70  disk/permissions -- data would be lost
    S8  MongoDB connect              80  MONGODB_URI unset/wrong, or IP not allowed
    S9  upsert + read-back verify    90  wrote but could not confirm

Stages S1-S4 are the *acquisition* half and S7-S9 the *storage* half; they are
deliberately decoupled by S7, which writes every reading to disk **before** any
upload is attempted. A database outage therefore costs you nothing but a
backfill (re-run with ``--replay``), and a sensor outage still lets you prove
the storage half works.

Usage::

    pip install paho-mqtt pymongo
    export HIVEMQ_PASSWORD=...            # or fill in my_secrets.py
    export MONGODB_URI=...                # only needed for --upload

    # take three readings and store them
    python read_and_upload.py --n 3 --label "bench ambient" --upload

    # storage half only, replaying readings captured earlier (backfill)
    python read_and_upload.py --replay ../camera/.../sensor_reading_*.json --upload

    # prove the whole storage half without a sensor or a database
    python read_and_upload.py --self-test

Credentials are read from ``my_secrets.py`` next to this file (git-ignored) or
from the environment; the MongoDB connection string is only ever read from
``MONGODB_URI`` and is never printed or accepted on the command line -- the
same rule ``powder-doser``'s ``dose_run_capture.py`` follows.
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
import socket
import ssl
import sys
import time
import uuid

SCHEMA_VERSION = 1
DOC_TYPE = "color_reading"

# The 8 AS7341 spectral channels, in the order main.py's read_sensor_data()
# builds them. Wavelengths are the channel centres from the datasheet.
CHANNELS = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
WAVELENGTHS_NM = [410, 440, 470, 510, 550, 583, 620, 670]

# CIE 1931 2-degree colour-matching functions sampled at those 8 wavelengths.
# Eight samples is a coarse basis for a 390-830 nm integral, so the colour this
# yields is a *relative* estimate for telling "reddish" from "bluish" and for
# tracking change between readings -- it is not a calibrated colorimeter
# reading. (The AS7341 reports counts, not radiance; without a reference
# white and a per-channel responsivity calibration no absolute claim is
# possible.) Recorded in the document so the derivation is reproducible.
CIE_XYZ_BAR = {
    410: (0.04351, 0.00121, 0.20740),
    440: (0.34828, 0.02300, 1.74706),
    470: (0.19536, 0.09098, 1.28250),
    510: (0.00930, 0.50300, 0.15820),
    550: (0.43345, 0.99495, 0.00875),
    583: (0.95370, 0.83780, 0.00150),
    620: (0.85630, 0.38100, 0.00000),
    670: (0.11319, 0.04102, 0.00000),
}

# Broker defaults. Host/username/pico-id are published in the upstream demo
# (AccelerationConsortium/wireless-color-sensor, sensor_file/test_sensor.ipynb)
# so they are not secret; the password deliberately has no default so it is
# never committed here. See the runbook's "Credentials" section.
DEFAULT_HIVEMQ_HOST = "248cc294c37642359297f75b7b023374.s2.eu.hivemq.cloud"
DEFAULT_HIVEMQ_USERNAME = "sgbaird"
DEFAULT_PICO_ID = "test"
DEFAULT_PORT = 8883

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Exit codes, one per stage, so a CI job or a wrapper script can branch on
# *where* it broke rather than parsing prose.
EXIT = {"S1": 10, "S2": 20, "S3": 30, "S4": 40, "S5": 50,
        "S6": 60, "S7": 70, "S8": 80, "S9": 90}

_t0 = time.time()


def log(stage, verdict, message):
    """One line per stage transition; the only output format this script has."""
    print("[%7.2fs] %-3s %-4s %s" % (time.time() - _t0, stage, verdict, message),
          flush=True)


def die(stage, message, remedy):
    log(stage, "FAIL", message)
    log(stage, "->", "remedy: %s" % remedy)
    sys.exit(EXIT[stage])


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config():
    """Broker settings from my_secrets.py, overridden by the environment."""
    cfg = {"HIVEMQ_HOST": DEFAULT_HIVEMQ_HOST,
           "HIVEMQ_USERNAME": DEFAULT_HIVEMQ_USERNAME,
           "HIVEMQ_PASSWORD": "",
           "PICO_ID": DEFAULT_PICO_ID}
    try:
        import my_secrets  # type: ignore
        for key in cfg:
            value = getattr(my_secrets, key, None)
            if value and str(value).strip():
                cfg[key] = str(value).strip()
    except ImportError:
        pass
    for key in cfg:
        env = os.environ.get(key, "").strip()
        if env:
            cfg[key] = env
    return cfg


# ---------------------------------------------------------------------------
# S1-S4: acquisition
# ---------------------------------------------------------------------------

def stage1_reachable(host, port):
    """DNS + TCP. Separates 'this host has no internet' from everything else."""
    try:
        ip = socket.gethostbyname(host)
    except Exception as exc:
        die("S1", "DNS lookup of %s failed: %s" % (host, exc),
            "check this machine's DNS/network; the broker hostname is public")
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
    except Exception as exc:
        die("S1", "TCP %s:%d refused/timed out: %s" % (host, port, exc),
            "port 8883 outbound is blocked -- check the firewall/proxy")
    log("S1", "PASS", "%s -> %s, tcp/%d open" % (host, ip, port))
    return ip


def connect_broker(cfg, port):
    """S2 (TLS + auth) and S3 (subscribe), which share one client object."""
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        die("S2", "paho-mqtt is not installed", "pip install paho-mqtt")

    if not cfg["HIVEMQ_PASSWORD"]:
        die("S2", "HIVEMQ_PASSWORD is empty",
            "export HIVEMQ_PASSWORD=... or fill in my_secrets.py "
            "(see the runbook's Credentials section)")

    data_topic = "color-mixing/picow/%s/as7341" % cfg["PICO_ID"]
    state = {"rc": None, "granted": None, "messages": []}

    def on_connect(client, userdata, flags, rc, properties=None):
        state["rc"] = rc
        if rc == 0:
            client.subscribe(data_topic, qos=1)

    def on_subscribe(client, userdata, mid, granted, properties=None):
        state["granted"] = [str(g) for g in granted]

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except Exception:
            payload = {"_unparsable": msg.payload.decode(errors="replace")}
        state["messages"].append(payload)

    try:  # paho-mqtt 2.x
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                             client_id="wcs-%s" % uuid.uuid4().hex[:8])
    except AttributeError:  # paho-mqtt 1.x
        client = mqtt.Client()
    client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
    client.username_pw_set(cfg["HIVEMQ_USERNAME"], cfg["HIVEMQ_PASSWORD"])
    client.on_connect, client.on_subscribe, client.on_message = (
        on_connect, on_subscribe, on_message)

    try:
        client.connect(cfg["HIVEMQ_HOST"], port, keepalive=60)
    except Exception as exc:
        die("S2", "TLS/MQTT connect raised: %s" % exc,
            "wrong host or port, or the TLS handshake was intercepted")
    client.loop_start()

    deadline = time.time() + 20
    while state["rc"] is None and time.time() < deadline:
        time.sleep(0.1)
    if state["rc"] is None:
        client.loop_stop()
        die("S2", "no CONNACK within 20 s",
            "broker unreachable through the TLS layer -- retry, then check "
            "the HiveMQ Cloud console for cluster status")
    if str(state["rc"]) not in ("0", "Success"):
        client.loop_stop()
        die("S2", "broker refused the connection: CONNACK=%s" % state["rc"],
            "bad username/password, or the HiveMQ credential was rotated/"
            "the cluster suspended")
    log("S2", "PASS", "CONNACK=%s as user %r" % (state["rc"], cfg["HIVEMQ_USERNAME"]))

    while state["granted"] is None and time.time() < deadline:
        time.sleep(0.1)
    if state["granted"] is None:
        client.loop_stop()
        die("S3", "no SUBACK for %s" % data_topic,
            "broker accepted the login but not the subscription")
    if any("Denied" in g or "Failure" in g or g == "128" for g in state["granted"]):
        client.loop_stop()
        die("S3", "subscription to %s denied: %s" % (data_topic, state["granted"]),
            "the HiveMQ credential's ACL does not permit this topic")
    log("S3", "PASS", "subscribed %s (%s)" % (data_topic, ", ".join(state["granted"])))
    return client, state, data_topic


def stage4_read(client, state, cfg, index, total, ryb, timeout):
    """One request/response round-trip. This is the stage the sensor owns."""
    command_topic = "command/picow/%s/as7341/read" % cfg["PICO_ID"]
    experiment_id = str(uuid.uuid4())
    request = {"command": {"R": ryb[0], "Y": ryb[1], "B": ryb[2]},
               "experiment_id": experiment_id}
    seen_before = len(state["messages"])

    sent_utc = utcnow()
    info = client.publish(command_topic, json.dumps(request), qos=1)
    info.wait_for_publish(timeout=10)
    if not info.is_published():
        die("S4", "broker never PUBACKed the read command",
            "connection dropped mid-publish -- re-run")
    log("S4", "....", "read %d/%d sent (R/Y/B=%d/%d/%d, experiment_id=%s)"
        % (index, total, ryb[0], ryb[1], ryb[2], experiment_id[:8]))

    start = time.time()
    while time.time() - start < timeout:
        for message in state["messages"][seen_before:]:
            if message.get("experiment_id") == experiment_id:
                latency = time.time() - start
                log("S4", "PASS", "reply in %.1f s" % latency)
                return {"request": request, "reply": message,
                        "latency_s": round(latency, 2),
                        "sent_utc": sent_utc.isoformat().replace("+00:00", "Z")}
        time.sleep(0.2)

    log("S4", "FAIL", "no reply on the data topic within %.0f s" % timeout)
    return None


# ---------------------------------------------------------------------------
# S5-S6: validation and colour
# ---------------------------------------------------------------------------

def stage5_validate(reply):
    """A reply is not the same as a *reading*. Catch the sensor-side failures.

    The firmware publishes whatever ``sensor.all_channels`` returned, so an
    unplugged/wedged I2C bus still produces a well-formed MQTT message -- with
    zeros, or with missing channels. Those must not reach the database looking
    like data.
    """
    problems = []
    data = reply.get("sensor_data")
    if not isinstance(data, dict):
        return None, ["reply has no sensor_data object (firmware error path)"]

    missing = [c for c in CHANNELS if c not in data]
    if missing:
        problems.append("missing channels: %s" % ", ".join(missing))
    counts = {}
    for channel in CHANNELS:
        value = data.get(channel)
        if value is None:
            continue
        if not isinstance(value, (int, float)):
            problems.append("%s is %r, not a number" % (channel, value))
            continue
        counts[channel] = int(value)

    if counts and all(v == 0 for v in counts.values()):
        problems.append("every channel reads 0 -- the AS7341 is almost "
                        "certainly not answering on I2C (check the Qwiic cable)")
    # The AS7341's ADC is 16-bit; at the firmware's default gain/atime a
    # channel pinned at 65535 means the reading is clipped and its true value
    # is unknown, so downstream ratios are meaningless.
    saturated = [c for c, v in counts.items() if v >= 65535]
    if saturated:
        problems.append("saturated channels (clipped, value unusable): %s"
                        % ", ".join(saturated))
    return counts, problems


def stage6_color(counts):
    """8 channel counts -> a relative colour estimate.

    Returns CIE xy, an sRGB hex triple, the dominant channel, and an
    approximate correlated colour temperature. All of it is relative -- see
    the note on CIE_XYZ_BAR.
    """
    x_sum = y_sum = z_sum = 0.0
    for wavelength, channel in zip(WAVELENGTHS_NM, CHANNELS):
        weight = float(counts.get(channel, 0))
        xbar, ybar, zbar = CIE_XYZ_BAR[wavelength]
        x_sum += weight * xbar
        y_sum += weight * ybar
        z_sum += weight * zbar

    total = x_sum + y_sum + z_sum
    if total <= 0:
        return {"valid": False, "reason": "zero total signal"}
    cie_x, cie_y = x_sum / total, y_sum / total

    # Normalise on Y so the hex is a hue/brightness impression, not a
    # radiometric quantity.
    scale = y_sum if y_sum > 0 else 1.0
    X, Y, Z = x_sum / scale, y_sum / scale, z_sum / scale
    r = 3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    b = 0.0557 * X - 0.2040 * Y + 1.0570 * Z

    def gamma(channel_value):
        channel_value = max(0.0, min(1.0, channel_value))
        if channel_value <= 0.0031308:
            return 12.92 * channel_value
        return 1.055 * (channel_value ** (1 / 2.4)) - 0.055

    rgb = [int(round(255 * gamma(v))) for v in (r, g, b)]

    # McCamy's cubic approximation; only meaningful near the Planckian locus,
    # so it is reported with that caveat attached.
    try:
        n = (cie_x - 0.3320) / (0.1858 - cie_y)
        cct = 449 * n ** 3 + 3525 * n ** 2 + 6823.3 * n + 5520.33
    except ZeroDivisionError:
        cct = None

    dominant = max(CHANNELS, key=lambda c: counts.get(c, 0))
    return {"valid": True,
            "cie_x": round(cie_x, 4), "cie_y": round(cie_y, 4),
            "srgb_hex": "#%02X%02X%02X" % tuple(rgb),
            "srgb": rgb,
            "dominant_channel": dominant,
            "dominant_nm": WAVELENGTHS_NM[CHANNELS.index(dominant)],
            "cct_k_approx": int(cct) if cct and 1000 < cct < 25000 else None,
            "basis": "CIE 1931 2-deg CMF sampled at 8 channel centres "
                     "(relative estimate, not a calibrated colorimeter)"}


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

def build_document(round_trip, counts, problems, color, cfg, label, notes):
    """One document per reading, keyed by a deterministic reading_uid.

    The uid hashes the experiment_id and the counts, so re-uploading the same
    captured reply upserts instead of duplicating -- the idempotency rule from
    powder-doser's dose_run_capture.py.
    """
    reply = round_trip["reply"]
    fingerprint = json.dumps({"experiment_id": reply.get("experiment_id"),
                              "counts": counts}, sort_keys=True)
    reading_uid = hashlib.sha1(fingerprint.encode()).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "doc_type": DOC_TYPE,
        "reading_uid": reading_uid,
        "experiment_id": reply.get("experiment_id"),
        "recorded_utc": utcnow().isoformat().replace("+00:00", "Z"),
        "sent_utc": round_trip.get("sent_utc"),
        "latency_s": round_trip.get("latency_s"),
        "device": {"pico_id": cfg["PICO_ID"], "sensor": "AS7341",
                   "broker_host": cfg["HIVEMQ_HOST"],
                   "firmware": "sensor_file/main.py (upstream demo)"},
        "command": reply.get("command"),
        "counts": counts,
        "wavelengths_nm": dict(zip(CHANNELS, WAVELENGTHS_NM)),
        "color": color,
        "quality": {"ok": not problems, "problems": problems},
        "label": label,
        "notes": notes,
        # Provenance: the firmware returns only the 8 spectral channels, so
        # any consumer expecting clear/nir/flicker must know they are absent
        # rather than zero. See sensor/README.md.
        "fields_not_reported": ["clear", "nir", "flicker_hz", "gain", "atime",
                                "astep", "basic_counts"],
    }


# ---------------------------------------------------------------------------
# S7-S9: storage
# ---------------------------------------------------------------------------

def stage7_write(documents, out_path):
    """Always runs, before any upload. Losing a reading to a DB outage is
    the one failure mode this pipeline refuses to have."""
    if not out_path:
        log("S7", "SKIP", "no --out given (nothing written to disk)")
        return None
    try:
        directory = os.path.dirname(os.path.abspath(out_path))
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(out_path, "w") as handle:
            json.dump(documents, handle, indent=2)
    except Exception as exc:
        die("S7", "could not write %s: %s" % (out_path, exc),
            "pick a writable --out path; the readings are otherwise lost")
    log("S7", "PASS", "wrote %d document(s) to %s" % (len(documents), out_path))
    return out_path


def stage8_connect(uri_env):
    uri = os.environ.get(uri_env, "").strip()
    if not uri:
        die("S8", "%s is not set" % uri_env,
            "export %s='mongodb+srv://...' (the VCL Atlas string, kept as a "
            "GitHub Actions secret) -- the readings are already saved by S7, "
            "so re-run later with --replay to backfill" % uri_env)
    try:
        from pymongo import MongoClient
    except ImportError:
        die("S8", "pymongo is not installed", "pip install pymongo")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=15000)
        info = client.server_info()
    except Exception as exc:
        # Never echo the URI: it carries the password.
        die("S8", "could not reach MongoDB: %s" % type(exc).__name__,
            "check that %s is correct and that this host's IP is on the "
            "Atlas access list (Atlas denies unknown IPs -- a GitHub Actions "
            "runner needs 0.0.0.0/0 or a fixed egress)" % uri_env)
    log("S8", "PASS", "connected to MongoDB %s" % info.get("version", "?"))
    return client


def ensure_indexes(client, db_name, collection):
    coll = client[db_name][collection]
    coll.create_index("reading_uid", unique=True, name="reading_uid_unique")
    coll.create_index([("device.pico_id", 1), ("recorded_utc", -1)],
                      name="device_recorded")
    coll.create_index("doc_type", name="doc_type")
    return sorted(coll.index_information())


def stage9_upsert(client, documents, db_name, collection):
    """Upsert, then read back. A write that cannot be read back is not a
    successful upload -- that is what the verify step is for."""
    coll = client[db_name][collection]
    try:
        ensure_indexes(client, db_name, collection)
    except Exception as exc:
        log("S9", "WARN", "could not create indexes (%s); continuing"
            % type(exc).__name__)

    written = []
    for document in documents:
        try:
            result = coll.replace_one({"reading_uid": document["reading_uid"]},
                                      document, upsert=True)
        except Exception as exc:
            die("S9", "upsert failed: %s" % type(exc).__name__,
                "the connection succeeded but the write did not -- most often "
                "the Atlas user lacks readWrite on this database")
        action = "inserted" if result.upserted_id else "updated"
        readback = coll.find_one({"reading_uid": document["reading_uid"]},
                                 {"_id": 0, "reading_uid": 1, "counts": 1})
        if not readback or readback.get("counts") != document["counts"]:
            die("S9", "read-back of %s did not match what was written"
                % document["reading_uid"][:12],
                "the write reported success but the document is not queryable")
        log("S9", "PASS", "%s %s.%s reading_uid=%s (read-back verified)"
            % (action, db_name, collection, document["reading_uid"][:12]))
        written.append(document["reading_uid"])
    return written


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_table(documents):
    if not documents:
        return
    print("\n%-22s %6s %6s %6s %6s %6s %6s %6s %6s  %-9s %s"
          % ("label", *[str(w) for w in WAVELENGTHS_NM], "sRGB", "dominant"))
    for document in documents:
        counts = document["counts"]
        color = document.get("color") or {}
        print("%-22s %6s %6s %6s %6s %6s %6s %6s %6s  %-9s %s"
              % (str(document.get("label"))[:22],
                 *[counts.get(c, "-") for c in CHANNELS],
                 color.get("srgb_hex", "-"),
                 "%s (%s nm)" % (color.get("dominant_channel", "-"),
                                 color.get("dominant_nm", "-"))))
    print("channel order: %s (nm)\n" % ", ".join(str(w) for w in WAVELENGTHS_NM))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def load_replays(patterns):
    """Rebuild round-trip records from previously captured reply JSON."""
    round_trips = []
    for pattern in patterns:
        for path in sorted(glob.glob(pattern)):
            with open(path) as handle:
                reply = json.load(handle)
            round_trips.append({"request": {"command": reply.get("command")},
                                "reply": reply, "latency_s": None,
                                "sent_utc": None,
                                "_source": os.path.basename(path),
                                "_label": reply.get("_label")})
    return round_trips


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read the wireless color sensor over MQTT and upload to "
                    "MongoDB, one numbered stage at a time.")
    parser.add_argument("--n", type=int, default=3,
                        help="number of readings to take (default 3)")
    parser.add_argument("--period", type=float, default=2.0,
                        help="seconds between readings")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="seconds to wait for each reply")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--label", default="",
                        help="what the sensor is looking at, e.g. 'red dye A1'")
    parser.add_argument("--notes", default="")
    parser.add_argument("--out", default=None, help="write documents here (JSON)")
    parser.add_argument("--replay", nargs="+", metavar="GLOB",
                        help="skip S1-S4 and rebuild documents from captured "
                             "reply JSON files (backfill)")
    parser.add_argument("--self-test", action="store_true",
                        help="replay the readings committed under camera/ to "
                             "exercise S5-S9 with no sensor attached")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--db", default="wireless_color_sensor")
    parser.add_argument("--collection", default="sensor_readings")
    parser.add_argument("--uri-env", default="MONGODB_URI",
                        help="env var holding the MongoDB connection string")
    args = parser.parse_args(argv)

    cfg = load_config()
    documents, failures = [], 0

    # S7 is what makes a database outage survivable, so it must not be
    # possible to upload without also landing the readings on disk.
    if args.upload and not args.out:
        args.out = os.path.join(
            "readings", "wcs_%s.json" % utcnow().strftime("%Y%m%dT%H%M%SZ"))

    if args.self_test:
        args.replay = [os.path.join(
            HERE, "..", "camera", "pickup-test-2026-08-10-full-cycle-sensor-read",
            "sensor_reading_*.json")]
        log("S0", "INFO", "self-test: replaying the 2026-08-10 readings; "
                          "S1-S4 are skipped (no sensor needed)")

    if args.replay:
        round_trips = load_replays(args.replay)
        if not round_trips:
            die("S5", "no reply files matched %s" % args.replay,
                "check the --replay glob")
        log("S4", "SKIP", "replaying %d captured reply file(s)" % len(round_trips))
    else:
        stage1_reachable(cfg["HIVEMQ_HOST"], args.port)
        client, state, _ = connect_broker(cfg, args.port)
        round_trips = []
        # Alternate the LED command between readings. On this build it makes
        # no difference (see camera/pickup-test-2026-08-10-*/README.md), but
        # keeping it exercised means a future firmware with a working LED
        # produces two genuinely different colours in one run.
        patterns = [(0, 0, 0), (50, 50, 50)]
        for index in range(args.n):
            round_trip = stage4_read(client, state, cfg, index + 1, args.n,
                                     patterns[index % len(patterns)],
                                     args.timeout)
            if round_trip:
                round_trips.append(round_trip)
            else:
                failures += 1
            if index + 1 < args.n:
                time.sleep(args.period)
        client.loop_stop()
        client.disconnect()

        if not round_trips:
            log("S4", "FAIL", "%d/%d reads timed out -- the broker accepted "
                              "every command, so the Pico W never answered"
                % (failures, args.n))
            log("S4", "->", "remedy: the Pico is powered off, off WiFi, or "
                            "main.py has stopped. Power-cycle it and watch the "
                            "onboard LED (it blinks once main.py is running); "
                            "if it stays dark, charge the LiPo. Use "
                            "collect_over_serial.py over USB to test the "
                            "sensor without WiFi.")
            sys.exit(EXIT["S4"])

    # ---- S5/S6 -----------------------------------------------------------
    for index, round_trip in enumerate(round_trips):
        counts, problems = stage5_validate(round_trip["reply"])
        if counts is None:
            log("S5", "FAIL", "reading %d: %s" % (index + 1, problems[0]))
            failures += 1
            continue
        if problems:
            log("S5", "WARN", "reading %d: %s" % (index + 1, "; ".join(problems)))
        else:
            log("S5", "PASS", "reading %d: 8/8 channels, none saturated"
                % (index + 1))
        color = stage6_color(counts)
        if not color.get("valid"):
            log("S6", "WARN", "reading %d: %s" % (index + 1, color.get("reason")))
        else:
            log("S6", "PASS", "reading %d: %s, dominant %s nm"
                % (index + 1, color["srgb_hex"], color["dominant_nm"]))
        documents.append(build_document(
            round_trip, counts, problems, color, cfg,
            round_trip.get("_label") or args.label or None, args.notes or None))

    if not documents:
        die("S5", "no usable readings", "see the S5 messages above")

    print_table(documents)

    # ---- S7 --------------------------------------------------------------
    stage7_write(documents, args.out)

    # ---- S8/S9 -----------------------------------------------------------
    if args.upload:
        client = stage8_connect(args.uri_env)
        stage9_upsert(client, documents, args.db, args.collection)
        client.close()
    else:
        log("S8", "SKIP", "--upload not given (nothing sent to the database)")

    log("--", "DONE", "%d reading(s) processed, %d failure(s)"
        % (len(documents), failures))
    return 0


if __name__ == "__main__":
    sys.exit(main())
