"""Does the timestamp work from PR #201 actually hold up?

PR #201 made three claims. This file tries to break each of them.

1. ``sensor_read.SensorLink.read`` brackets every reading with
   ``t_request_utc`` / ``t_response_utc``, taken from the same clock read that
   mints ``experiment_id``, so the two can never disagree.
2. ``run_xscan_test.store_in_mongodb`` writes the *reading's* own instant as
   ``timestamp`` and keeps the batch write time separately as ``stored_at``.
   Before the fix every document of a run shared one ``utcnow()`` taken after
   the last read, so readings landed up to three minutes late.
3. ``stream_index.py`` turns those instants into livestream links, with a
   -67 s archive correction that ``frames_from_stream.py`` verified against the
   clock burned into each frame.

The offline checks need nothing but the repository. The live checks command a
real reading over MQTT and write it to MongoDB; **neither moves the robot** --
nothing here talks to the OT-2 at all.

Usage::

    python3 test_measurement_timestamps.py            # offline only
    python3 test_measurement_timestamps.py --live     # + MQTT and MongoDB
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import sensor_read  # noqa: E402
import run_xscan_test  # noqa: E402
import stream_index  # noqa: E402

RESULTS = []
FAKE_CHANNELS = {"ch410": 6, "ch440": 4, "ch470": 10, "ch510": 168,
                 "ch550": 173, "ch583": 39, "ch620": 21, "ch670": 18}


def check(name, ok, detail=""):
    RESULTS.append({"name": name, "ok": bool(ok), "detail": detail})
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  --  {detail}" if detail else ""),
          flush=True)
    return ok


def section(title):
    print(f"\n=== {title} ===", flush=True)


def parse_iso(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


# --------------------------------------------------------------------------
# offline: a fake broker, so the read path is exercised without hardware
# --------------------------------------------------------------------------
class _Msg:
    def __init__(self, topic, payload):
        self.topic, self.payload = topic, payload


class FakeClient:
    """Just enough broker to drive SensorLink, with a controllable delay."""

    def __init__(self, *a, **kw):
        self.on_connect = self.on_message = None
        self.delay = 0.4
        self.published = []

    def username_pw_set(self, *a, **kw):
        pass

    def tls_set(self, *a, **kw):
        pass

    def connect(self, host, port, keepalive=60):
        self.on_connect(self, None, {}, 0)

    def loop_start(self):
        pass

    def loop_stop(self):
        pass

    def disconnect(self):
        pass

    def subscribe(self, subs):
        pass

    def publish(self, topic, payload, qos=0):
        self.published.append((topic, payload))
        if topic.endswith("/_probe"):
            self.on_message(self, None, _Msg(topic, payload.encode()))
            return
        data_topic = topic.replace("command/", "color-mixing/").replace("/read", "")

        def answer():
            time.sleep(self.delay)
            body = {"sensor_data": dict(FAKE_CHANNELS),
                    "experiment_id": json.loads(payload)["experiment_id"]}
            self.on_message(self, None, _Msg(data_topic, json.dumps(body).encode()))

        threading.Thread(target=answer, daemon=True).start()


def test_read_brackets_the_measurement():
    section("1. sensor_read brackets every reading (fake broker)")
    real = sensor_read.mqtt.Client
    sensor_read.mqtt.Client = FakeClient
    try:
        link = sensor_read.SensorLink(broker="fake", port=8883, username="u",
                                      password="p", pico_id="deadbeef", timeout=5)
        link.connect()
        link.check_delivery(timeout=3)
        before = time.time()
        r = link.read(label="pos1-dx+0")
        after = time.time()
        link.close()
    finally:
        sensor_read.mqtt.Client = real

    fields = ("t_request_utc", "t_response_utc", "t_request_epoch",
              "t_response_epoch", "latency_s")
    check("read() returns all five time fields",
          all(f in r for f in fields),
          ", ".join(f for f in fields if f in r))

    tail = int(r["experiment_id"].rsplit("-", 1)[-1])
    check("experiment_id epoch == t_request_epoch (one clock read, not two)",
          tail == int(r["t_request_epoch"] * 1000),
          f"id ms {tail} vs field ms {int(r['t_request_epoch'] * 1000)}")

    check("ISO strings agree with the epochs to the millisecond",
          abs(parse_iso(r["t_request_utc"]).timestamp() - r["t_request_epoch"]) < 0.0015
          and abs(parse_iso(r["t_response_utc"]).timestamp() - r["t_response_epoch"]) < 0.0015)

    check("request <= response, and both inside an independent bracket",
          before - 0.002 <= r["t_request_epoch"] <= r["t_response_epoch"] <= after + 0.002,
          f"outer {after - before:.3f}s, inner {r['latency_s']:.3f}s")

    check("latency_s is the measured round trip, not a constant",
          abs(r["latency_s"] - (r["t_response_epoch"] - r["t_request_epoch"])) < 0.002
          and 0.35 < r["latency_s"] < 1.5,
          f"{r['latency_s']:.3f}s against an injected 0.4s delay")
    return r


# --------------------------------------------------------------------------
# offline: the MongoDB document shape, with a fake client
# --------------------------------------------------------------------------
class FakeCollection:
    def __init__(self):
        self.docs = []

    def insert_many(self, docs):
        self.docs.extend(docs)

        class R:
            inserted_ids = list(range(len(docs)))
        return R()


class FakeMongo:
    last = None

    def __init__(self, *a, **kw):
        self.coll = FakeCollection()
        self.admin = type("A", (), {"command": staticmethod(lambda *a, **k: {"ok": 1})})()
        FakeMongo.last = self

    def __getitem__(self, db):
        return {"sensor-data": self.coll}

    def close(self):
        pass


def _record(label, response_epoch, with_times=True):
    request_epoch = response_epoch - 1.4
    r = {"stage": label, "label": label, "position": None,
         "experiment_id": f"{label}-{int(request_epoch * 1000)}",
         "command": {"R": 0, "Y": 0, "B": 0},
         "channels": dict(FAKE_CHANNELS), "total": sum(FAKE_CHANNELS.values()),
         "latency_s": 1.4}
    if with_times:
        r["t_request_utc"] = sensor_read._iso(request_epoch)
        r["t_response_utc"] = sensor_read._iso(response_epoch)
        r["t_request_epoch"] = int(request_epoch * 1000) / 1000.0
        r["t_response_epoch"] = int(response_epoch * 1000) / 1000.0
    return r


def test_mongo_document_shape():
    section("2. MongoDB documents carry the reading's time, not the write time")
    import pymongo
    real = pymongo.MongoClient
    pymongo.MongoClient = FakeMongo
    try:
        now = time.time()
        # Two readings three minutes apart -- the exact spread the old bug
        # collapsed to a single value.
        recs = [_record("pos1", now - 200), _record("pos3", now - 20)]
        run_xscan_test.store_in_mongodb(recs, {"note": "offline test"}, "mongodb://fake", "db")
        docs = FakeMongo.last.coll.docs
    finally:
        pymongo.MongoClient = real

    ts = [d["timestamp"] for d in docs]
    check("each document gets its own timestamp",
          ts[0] != ts[1],
          f"{(ts[1] - ts[0]).total_seconds():.1f}s apart, as the readings were")
    check("timestamp == the reading's own response time",
          all(abs((d["timestamp"] - parse_iso(r["t_response_utc"])).total_seconds()) < 0.002
              for d, r in zip(docs, recs)))
    check("stored_at is the shared write time and is later than both readings",
          docs[0]["stored_at"] == docs[1]["stored_at"]
          and docs[0]["stored_at"] > ts[0] and docs[0]["stored_at"] > ts[1],
          f"write time is {(docs[0]['stored_at'] - ts[0]).total_seconds():.0f}s "
          f"after the first reading")
    check("t_request is carried too, so the bracket survives the write",
          all(d["t_request"] is not None and d["t_request"] < d["timestamp"] for d in docs))

    # A reading from before the fix must degrade, not crash.
    pymongo.MongoClient = FakeMongo
    try:
        run_xscan_test.store_in_mongodb([_record("legacy", time.time() - 500, with_times=False)],
                                        {"note": "legacy"}, "mongodb://fake", "db")
        legacy = FakeMongo.last.coll.docs[0]
        ok = legacy["timestamp"] == legacy["stored_at"] and legacy["t_request"] is None
    finally:
        pymongo.MongoClient = real
    check("a pre-fix reading falls back to the write time instead of raising", ok)


# --------------------------------------------------------------------------
# offline: the index, and the frames that verified it
# --------------------------------------------------------------------------
def test_stream_index_time_recovery():
    section("3. stream_index recovers the instant both ways")
    new = {"experiment_id": "pos1-1788999999999", "t_request_epoch": 1788000000.25}
    check("prefers the explicit field when a reading has one",
          stream_index.request_epoch(new) == 1788000000.25)
    check("falls back to the experiment_id epoch for 2026-09-09 data",
          stream_index.request_epoch({"experiment_id": "pos1-dx+0-2-1788916407689"})
          == 1788916407.689)
    check("a malformed id costs one row, not the index",
          stream_index.request_epoch({"experiment_id": "no-epoch-here"}) is None)


def test_index_regenerates_identically():
    section("4. the committed index regenerates byte-for-byte")
    committed = json.load(open(os.path.join(HERE, "measurement-stream-index.json")))
    with tempfile.TemporaryDirectory() as tmp:
        j, m = os.path.join(tmp, "i.json"), os.path.join(tmp, "i.md")
        stream_index.main(["--json-out", j, "--md-out", m])
        fresh = json.load(open(j))
        fresh_md = open(m).read()
    check("same number of readings",
          len(fresh["readings"]) == len(committed["readings"]) == 114,
          f"{len(fresh['readings'])} readings")
    check("every row identical (times, offsets, links)",
          fresh["readings"] == committed["readings"])
    check("markdown identical",
          fresh_md == open(os.path.join(HERE, "measurement-stream-index.md")).read())
    linked = [r for r in fresh["readings"] if "url" in r]
    check("all 114 fall inside the known stream segment", len(linked) == 114)
    return fresh


def test_frames_agree_with_the_burned_in_clock(index):
    section("5. the frames independently confirm the links")
    frames = json.load(open(os.path.join(HERE, "frames", "frames.json")))
    committed = json.load(open(os.path.join(HERE, "measurement-stream-index.json")))
    rows = {r["experiment_id"]: r for r in index["readings"]}
    worst, missing, mismatched = 0.0, [], []
    for f in frames["frames"]:
        # The overlay is drawn in lab local time (UTC-6); this is the only
        # clock in the chain that did not come from the machine taking the
        # readings, which is what makes it worth checking against.
        stamp = (datetime.strptime(f["overlay_local"], "%Y-%m-%d_%H-%M-%S")
                 .replace(tzinfo=timezone.utc) + timedelta(hours=6))
        err = (stamp - parse_iso(f["t_response_utc"])).total_seconds()
        worst = max(worst, abs(err))
        row = rows.get(f["experiment_id"])
        if row is None:
            missing.append(f["name"])
        elif abs(row["video_offset_s"] - f["video_offset_s"]) > 0.05:
            mismatched.append(f["name"])
    check("every frame's OCR'd clock matches the reading it belongs to",
          worst <= 1.5, f"{len(frames['frames'])} frames, worst error {worst:.1f}s")
    check("every frame's reading is in the index", not missing, ", ".join(missing))
    check("frame offsets and index offsets agree", not mismatched, ", ".join(mismatched))
    check("the -67 s archive correction is what both sides used",
          frames["shift_used_s"] == -67.0
          and committed["meta"]["offset_shift_s"] == -67.0,
          f"frames {frames['shift_used_s']}s, index "
          f"{committed['meta']['offset_shift_s']}s")
    # Every frame file the index promises actually exists on disk.
    absent = [f["name"] for f in frames["frames"]
              if not os.path.exists(os.path.join(HERE, "frames", f["name"]))]
    check("every frame named in frames.json is committed", not absent, ", ".join(absent))


def test_spectra_regenerate():
    section("6. the 300 px spectra regenerate from the index")
    out = subprocess.run([sys.executable, os.path.join(HERE, "plot_spectra.py"),
                          "--out-dir", os.path.join(tempfile.gettempdir(), "spectra-test")],
                         capture_output=True, text=True)
    made = [f for f in os.listdir(os.path.join(tempfile.gettempdir(), "spectra-test"))
            if f.endswith(".png")] if out.returncode == 0 else []
    committed = [f for f in os.listdir(os.path.join(HERE, "spectra")) if f.endswith(".png")]
    check("plot_spectra.py runs clean", out.returncode == 0, out.stderr.strip()[-200:])
    check("same set of spectra as committed",
          sorted(made) == sorted(committed), f"{len(made)} plots")
    try:
        import struct
        p = os.path.join(tempfile.gettempdir(), "spectra-test", sorted(made)[0])
        with open(p, "rb") as fh:
            fh.read(16)
            w, h = struct.unpack(">II", fh.read(8))
        check("still 300 px wide, as asked for", w == 300, f"{w}x{h} px")
    except Exception as e:  # noqa: BLE001
        check("still 300 px wide, as asked for", False, str(e))


# --------------------------------------------------------------------------
# live: real broker, real database, no robot
# --------------------------------------------------------------------------
def test_runner_clock():
    section("7. the clock the timestamps come from is itself right")
    try:
        req = urllib.request.Request("https://www.google.com", method="HEAD")
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=15) as resp:
            served = resp.headers["Date"]
        t1 = time.time()
        theirs = datetime.strptime(served, "%a, %d %b %Y %H:%M:%S %Z").replace(
            tzinfo=timezone.utc).timestamp()
        skew = theirs - (t0 + t1) / 2
        check("this machine's UTC agrees with an internet time source",
              abs(skew) < 3.0, f"skew {skew:+.1f}s (HTTP Date, 1 s resolution)")
    except Exception as e:  # noqa: BLE001
        check("this machine's UTC agrees with an internet time source", False, str(e))


def test_live_broker_and_sensor():
    """Command a real reading. Returns [] if the board is silent, which is a
    finding about the board and not about the fix under test."""
    section("8. a real reading over MQTT (no robot motion)")
    readings = []
    try:
        link = sensor_read.SensorLink()
        link.connect()
    except Exception as e:  # noqa: BLE001
        check("broker reachable from here", False, str(e))
        return readings
    try:
        link.check_delivery()
        check("broker reachable and delivering, straight from the runner", True,
              "no Pi, no tailnet needed for the sensor link")
        for i in (1, 2):
            before = time.time()
            try:
                r = link.read(label=f"fixcheck-{i}", timeout=15, retries=1)
            except sensor_read.SensorError as e:
                check(f"reading {i}: the board answers", False, str(e).split(".")[0])
                return readings
            after = time.time()
            r["stage"] = f"fix-verification-{i}"
            r["position"] = None
            check(f"reading {i}: bracketed by an independent clock",
                  before - 0.002 <= r["t_request_epoch"]
                  <= r["t_response_epoch"] <= after + 0.002,
                  f"total={r['total']}, latency={r['latency_s']:.2f}s, "
                  f"t_response={r['t_response_utc']}")
            check(f"reading {i}: experiment_id epoch == t_request_epoch",
                  int(r["experiment_id"].rsplit("-", 1)[-1])
                  == int(r["t_request_epoch"] * 1000))
            readings.append(r)
            if i == 1:
                time.sleep(12)
        gap = readings[1]["t_response_epoch"] - readings[0]["t_response_epoch"]
        check("two readings 12 s apart get two different instants", gap > 11.0,
              f"{gap:.1f}s apart")
    finally:
        link.close()
    return readings


def _synthetic_pair():
    """Two records with known, deliberately-far-apart instants.

    Stands in for a pair of real readings when the board is asleep. It exercises
    exactly the same write path; what it cannot show is that the instants came
    from a sensor, which is what section 8 is for.
    """
    now = time.time()
    return [_record("selftest-pos1", now - 174.0), _record("selftest-pos3", now - 11.0)]


def test_live_mongo_roundtrip(readings):
    section("9. the real database: does the reading's instant survive the write?")
    uri = os.environ.get("MONGODB_URI")
    db = os.environ.get("MONGODB_DATABASE", "digital-wetlab")
    if not uri:
        check("MONGODB_URI present", False, "not set; skipping the round trip")
        return
    synthetic = not readings
    recs = readings or _synthetic_pair()
    # A pair of self-test documents has no business in sensor-data, so the write
    # goes to a scratch collection in the same database and is deleted after.
    # Everything else -- driver, cluster, BSON date handling -- is the real thing.
    collection = "sensor-data" if not synthetic else "sensor-data-selftest"
    real_collection = run_xscan_test.MONGO_COLLECTION
    run_xscan_test.MONGO_COLLECTION = collection
    meta = {"started": recs[0].get("t_request_utc"),
            "note": "PR #201 timestamp verification -- no robot motion",
            "test": "test_measurement_timestamps.py", "synthetic": synthetic}
    wrote_at = time.time()
    try:
        ids = run_xscan_test.store_in_mongodb(recs, meta, uri, db)
    except Exception as e:  # noqa: BLE001
        check("write to MongoDB Atlas", False, str(e)[:160])
        run_xscan_test.MONGO_COLLECTION = real_collection
        return
    finally:
        run_xscan_test.MONGO_COLLECTION = real_collection

    from bson import ObjectId
    from pymongo import MongoClient
    client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    try:
        docs = list(client[db][collection].find(
            {"_id": {"$in": [ObjectId(i) for i in ids]}}).sort("timestamp", 1))
        check(f"both documents come back from {db}.{collection}",
              len(docs) == 2, f"{len(docs)} found"
              + ("  (synthetic records: the board was asleep)" if synthetic else ""))
        if len(docs) != 2:
            return
        # BSON dates are ms-resolution, so the tolerance is one millisecond.
        drift = max(abs(d["timestamp"].replace(tzinfo=timezone.utc).timestamp()
                        - parse_iso(r["t_response_utc"]).timestamp())
                    for d, r in zip(docs, recs))
        check("stored timestamp == the reading's own instant, through BSON and back",
              drift <= 0.001, f"worst drift {drift * 1000:.1f} ms")
        spread = (docs[1]["timestamp"] - docs[0]["timestamp"]).total_seconds()
        check("the two documents do NOT share one timestamp (this was the bug)",
              spread > 10.0, f"{spread:.0f}s apart in the database")
        lag = (docs[0]["stored_at"].replace(tzinfo=timezone.utc).timestamp()
               - docs[0]["timestamp"].replace(tzinfo=timezone.utc).timestamp())
        check("stored_at kept separately, equal to the write time",
              docs[0]["stored_at"] == docs[1]["stored_at"]
              and abs(docs[0]["stored_at"].replace(tzinfo=timezone.utc).timestamp()
                      - wrote_at) < 60,
              f"the first reading would have been {lag:.0f}s late under the old scheme")
        check("t_request survives the write, so the bracket is queryable",
              all(d.get("t_request") is not None and d["t_request"] < d["timestamp"]
                  for d in docs))
        check("stream_index reads the new fields on a brand-new reading",
              all(abs(stream_index.request_epoch(r) - parse_iso(r["t_request_utc"]).timestamp())
                  < 0.0015 for r in recs))
        if synthetic:
            client[db][collection].delete_many({"_id": {"$in": [ObjectId(i) for i in ids]}})
            left = client[db][collection].count_documents({})
            check("scratch documents cleaned up again", left == 0,
                  f"{left} left in {collection}")
        else:
            print("    inserted _ids: " + ", ".join(ids))
    finally:
        client.close()


def test_existing_documents_carry_the_old_bug():
    section("10. the bug, still measurable in the documents written before the fix")
    uri = os.environ.get("MONGODB_URI")
    db = os.environ.get("MONGODB_DATABASE", "digital-wetlab")
    if not uri:
        check("MONGODB_URI present", False, "not set")
        return
    from pymongo import MongoClient
    client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    try:
        coll = client[db]["sensor-data"]
        docs = list(coll.find({"source": "ot2-xscan-test"}))
        check("the xscan documents are there to check", len(docs) > 100,
              f"{len(docs)} documents from {len(set(d['run']['started'] for d in docs))} runs")
        post_fix = [d for d in docs if d.get("stored_at") is not None]
        check("none of them were written by the fixed code -- it has never run for real",
              not post_fix,
              f"{len(post_fix)} carry stored_at; the fix landed after the last run")

        # How wrong was the old field? Recover each reading's true instant from
        # the epoch-ms in its experiment_id and compare.
        late = []
        for d in docs:
            tail = d["experiment_id"].rsplit("-", 1)[-1]
            if not tail.isdigit():
                continue
            true_s = int(tail) / 1000.0
            stored_s = d["timestamp"].replace(tzinfo=timezone.utc).timestamp()
            late.append(stored_s - true_s)
        check("the stored timestamp was always LATER than the reading, never earlier",
              late and min(late) > 0, f"n={len(late)}, min {min(late):.1f}s")
        check("and it was late by minutes, not milliseconds",
              max(late) > 60,
              f"median {sorted(late)[len(late) // 2]:.0f}s, worst {max(late):.0f}s late")

        runs = {}
        for d in docs:
            runs.setdefault(d["run"]["started"], []).append(d["timestamp"])
        collapsed = [k for k, v in runs.items() if len(v) > 1 and len(set(v)) <= 2]
        check("every multi-reading run collapsed onto one write instant",
              len(collapsed) == len([k for k, v in runs.items() if len(v) > 1]),
              f"{len(collapsed)} runs; the one with two distinct values straddled a "
              "millisecond boundary while looping, which is the same defect")
    except Exception as e:  # noqa: BLE001
        check("query the existing documents", False, str(e)[:160])
    finally:
        client.close()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--live", action="store_true",
                   help="also command a real reading over MQTT and write it to MongoDB")
    p.add_argument("--no-store", action="store_true", help="live read, but do not write")
    p.add_argument("--json-out")
    args = p.parse_args(argv)

    test_read_brackets_the_measurement()
    test_mongo_document_shape()
    test_stream_index_time_recovery()
    index = test_index_regenerates_identically()
    test_frames_agree_with_the_burned_in_clock(index)
    test_spectra_regenerate()
    if args.live:
        test_runner_clock()
        readings = test_live_broker_and_sensor()
        if not args.no_store:
            test_live_mongo_roundtrip(readings)
            test_existing_documents_carry_the_old_bug()

    failed = [r for r in RESULTS if not r["ok"]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed"
          + (f"; FAILED: {', '.join(r['name'] for r in failed)}" if failed else ""))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                       "live": args.live, "checks": RESULTS}, fh, indent=2)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
