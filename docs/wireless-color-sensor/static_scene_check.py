#!/usr/bin/env python3
"""Separate 'the sensor is stuck' from 'nothing in front of it changed'.

Identical readings across a colour sweep are the *expected* result for this
device. In the OT-2 liquid-colour-mixing deployment the R/Y/B values in a
command are metadata -- the dye volumes the robot dispensed -- not instructions
to the sensor. The firmware echoes them back beside the reading and never acts
on them (`set_color` is commented out and `run_color_experiment` is labelled a
"Dummy function" upstream). So a stationary sensor over an unchanged well
returns the same numbers, and that is correct behaviour, not a fault.

What is worth measuring is the difference between two timescales:

  * within a burst (seconds)  -- should be flat; quantifies the noise floor
  * between bursts (minutes)  -- drifts, because the AS7341's own LED is
                                 commented out in main.py, so every reading is
                                 of uncontrolled ambient room light

If the second is much larger than the first, the room is part of the
measurement. Turning the sensor LED on removes it: lit readings run ~600x the
ambient level, so ambient stops mattering.

Requires MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, PICO_ID.
MONGODB_URI / MONGODB_DATABASE are optional and only used for --history.

    python static_scene_check.py --repeat 8 --history
"""
import argparse, json, os, ssl, statistics as stats, sys, time

import paho.mqtt.client as mqtt

CHANNELS = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]


def burst(n, timeout):
    pico = os.environ["PICO_ID"]
    data_topic = f"color-mixing/picow/{pico}/as7341"
    cmd_topic = f"command/picow/{pico}/as7341/read"
    probe_topic = f"{data_topic}/_probe"
    readings, probes = [], []

    def on_connect(c, _u, _f, rc, _p=None):
        print(f"[connect] CONNACK rc={rc}")
        c.subscribe([(data_topic, 1), (probe_topic, 1)])

    def on_subscribe(_c, _u, _m, granted, _p=None):
        print(f"[subscribe] SUBACK granted={granted}")

    def on_message(_c, _u, msg):
        if msg.topic == probe_topic:
            probes.append(1)
            return
        try:
            readings.append(json.loads(msg.payload.decode())["sensor_data"])
        except Exception as exc:                       # noqa: BLE001
            print(f"[rx] unparseable payload: {exc}", file=sys.stderr)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    client.username_pw_set(os.environ["MQTT_USERNAME"], os.environ["MQTT_PASSWORD"])
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.on_connect, client.on_subscribe, client.on_message = (
        on_connect, on_subscribe, on_message)
    client.connect(os.environ["MQTT_BROKER"], int(os.environ["MQTT_PORT"]), 30)
    client.loop_start()
    time.sleep(2.5)

    # Positive control. A broker can grant a subscription and then deliver
    # nothing when the credential lacks read permission, which is
    # indistinguishable from a silent board.
    client.publish(probe_topic, "ping", qos=1)
    time.sleep(2)
    if not probes:
        print("[loopback] FAIL -- broker acknowledged the subscription but did not\n"
              "           deliver our own probe. This is a BROKER PERMISSION problem,\n"
              "           not a sensor problem. Grant this credential subscribe as\n"
              "           well as publish.")
        client.loop_stop()
        return []
    print("[loopback] PASS -- the broker delivers to us on this topic")

    for i in range(n):
        before, t0 = len(readings), time.time()
        client.publish(cmd_topic, json.dumps({
            # The firmware indexes a *nested* payload. A flat one raises KeyError
            # inside its handler, where a bare except swallows it -- the board then
            # looks exactly like it is switched off.
            "command": {"R": 0, "Y": 0, "B": 0},
            "experiment_id": f"static-scene-{i}-{int(time.time())}",
        }), qos=1)
        while time.time() - t0 < timeout and len(readings) == before:
            time.sleep(0.05)
        if len(readings) == before:
            print(f"  [{i}] TIMEOUT after {timeout}s")
        else:
            total = sum(readings[-1][c] for c in CHANNELS)
            print(f"  [{i}] {time.time() - t0:5.2f}s  total={total:>7}")
        time.sleep(1)

    client.loop_stop()
    client.disconnect()
    return readings


def report(readings):
    print(f"\n{'chan':<8}{'mean':>9}{'min':>7}{'max':>7}{'stdev':>8}{'spread':>9}")
    for ch in CHANNELS:
        v = [r[ch] for r in readings]
        m = stats.mean(v)
        print(f"{ch:<8}{m:>9.1f}{min(v):>7}{max(v):>7}{stats.stdev(v):>8.2f}"
              f"{100 * (max(v) - min(v)) / max(m, 1):>8.2f}%")
    totals = [sum(r[c] for c in CHANNELS) for r in readings]
    m, sd = stats.mean(totals), stats.stdev(totals)
    print(f"{'TOTAL':<8}{m:>9.1f}{min(totals):>7}{max(totals):>7}{sd:>8.2f}"
          f"{100 * (max(totals) - min(totals)) / m:>8.2f}%")
    print(f"\n[noise floor] a static scene reads {m:.0f} +/- {sd:.1f} counts "
          f"({100 * sd / m:.2f}%) over seconds.")
    return m, sd


def history(now_mean, now_sd):
    """Compare against earlier bursts, which is where ambient drift shows up."""
    try:
        from pymongo import MongoClient
    except ImportError:
        print("[history] pymongo not installed, skipping")
        return
    client = MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=15000)
    docs = list(client[os.environ["MONGODB_DATABASE"]]["sensor-data"]
                .find({}).sort("_id", 1))
    groups = {}
    for d in docs:
        sd = d.get("sensor_data") or {}
        if not all(c in sd for c in CHANNELS):
            continue
        # Lit readings are ~600x ambient, so mixing them in would swamp the
        # comparison we are actually trying to make.
        if d.get("led") is True:
            continue
        key = d["_id"].generation_time.strftime("%Y-%m-%d %H:%M")
        groups.setdefault(key, []).append(sum(sd[c] for c in CHANNELS))

    print(f"\n[history] {len(groups)} earlier unlit capture session(s)\n")
    print(f"{'utc':<18}{'n':>3}{'mean total':>12}")
    for key in sorted(groups):
        g = groups[key]
        print(f"{key:<18}{len(g):>3}{stats.mean(g):>12.0f}")
    print(f"{'now':<18}{'':>3}{now_mean:>12.0f}")

    means = [stats.mean(g) for g in groups.values()] + [now_mean]
    drift = max(means) - min(means)
    print(f"\n[between bursts] spread {drift:.0f} counts, versus a {now_sd:.1f}-count\n"
          f"                 noise floor within a burst.")
    if now_sd and drift > 10 * now_sd:
        print("  -> The scene is not the only thing setting these numbers. With\n"
              "     `sensor.LED = True` commented out in main.py the AS7341 reads\n"
              "     ambient room light, so the baseline follows the room. Restore\n"
              "     that line (with gain=4) to make the measurement self-illuminated.\n"
              "  -> Caveat: moving or re-seating the board changes the baseline too.\n"
              "     Only compare sessions where nobody touched it in between.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repeat", type=int, default=8, help="readings in the burst")
    ap.add_argument("--timeout", type=float, default=12.0, help="seconds per reading")
    ap.add_argument("--history", action="store_true",
                    help="also compare against earlier bursts in MongoDB")
    args = ap.parse_args()

    readings = burst(args.repeat, args.timeout)
    print(f"\n[replies] {len(readings)}/{args.repeat}")
    if len(readings) < 3:
        print("\nToo few replies to characterise. If the loopback passed, the board\n"
              "is not answering: check that it is switched on (the LiPo SHIM boots\n"
              "off -- short press to turn on) and that the battery is charged.")
        return 1
    mean, sd = report(readings)
    if args.history:
        history(mean, sd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
