"""Fast wireless-color-sensor check: broker -> Pico W -> AS7341 -> broker -> MongoDB."""
import json, os, ssl, sys, time
import paho.mqtt.client as mqtt

BROKER = os.environ["MQTT_BROKER"]
PORT = int(os.environ.get("MQTT_PORT", 8883))
USER = os.environ["MQTT_USERNAME"]
PW = os.environ["MQTT_PASSWORD"]
PICO = os.environ["PICO_ID"]

CMD = f"command/picow/{PICO}/as7341/read"
DATA = f"color-mixing/picow/{PICO}/as7341"
PROBE = f"color-mixing/picow/{PICO}/_probe"

state = {"loopback": False, "msgs": [], "connack": None, "suback": False}

def on_connect(c, u, f, rc, props=None):
    state["connack"] = rc
    print(f"[connect] CONNACK = {rc}", flush=True)
    c.subscribe([(DATA, 1), (PROBE, 1)])

def on_subscribe(c, u, mid, granted, props=None):
    state["suback"] = True
    print(f"[subscribe] SUBACK granted={granted}", flush=True)

def on_message(c, u, m):
    if m.topic == PROBE:
        state["loopback"] = True
        print("[loopback] PASS -- broker is delivering to us", flush=True)
        return
    try:
        payload = json.loads(m.payload.decode())
    except Exception:
        payload = {"_raw": m.payload.decode(errors="replace")}
    payload["_recv_ts"] = time.time()
    state["msgs"].append(payload)
    sd = payload.get("sensor_data", {})
    tot = sum(v for v in sd.values() if isinstance(v, (int, float)))
    print(f"[RX] {payload.get('experiment_id','?'):32s} total={tot}  {sd}", flush=True)

try:
    cli = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"ci-fast-{int(time.time())}")
except AttributeError:
    cli = mqtt.Client(client_id=f"ci-fast-{int(time.time())}")
cli.username_pw_set(USER, PW)
cli.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS_CLIENT)
cli.on_connect, cli.on_subscribe, cli.on_message = on_connect, on_subscribe, on_message

t0 = time.time()
cli.connect(BROKER, PORT, keepalive=30)
cli.loop_start()

# wait for SUBACK
while not state["suback"] and time.time() - t0 < 15:
    time.sleep(0.1)
if not state["suback"]:
    print("[FATAL] no SUBACK -- broker did not accept the subscription"); sys.exit(2)

# positive control: can the broker deliver to us at all?
cli.publish(PROBE, json.dumps({"probe": 1}), qos=1)
p0 = time.time()
while not state["loopback"] and time.time() - p0 < 8:
    time.sleep(0.05)
if not state["loopback"]:
    print("[loopback] FAIL -- broker permission problem, NOT the board"); sys.exit(3)

# command the board -- payload MUST be nested or the firmware raises KeyError silently
COLORS = [("dark", 0, 0, 0), ("red", 255, 0, 0), ("green", 0, 255, 0), ("blue", 0, 0, 255), ("white", 255, 255, 255)]
sent = []
for name, R, Y, B in COLORS:
    eid = f"ci-fast-{name}-{int(time.time())}"
    msg = {"command": {"R": R, "Y": Y, "B": B}, "experiment_id": eid, "_input_message_id": eid}
    before = len(state["msgs"])
    ts = time.time()
    cli.publish(CMD, json.dumps(msg), qos=1)
    print(f"[TX] {name:6s} {json.dumps(msg['command'])}", flush=True)
    while len(state["msgs"]) == before and time.time() - ts < 12:
        time.sleep(0.05)
    if len(state["msgs"]) > before:
        state["msgs"][-1]["_cmd"] = {"R": R, "Y": Y, "B": B}
        state["msgs"][-1]["_color"] = name
        print(f"     latency {time.time()-ts:.2f}s", flush=True)
    else:
        print(f"     NO REPLY after 12s", flush=True)
    sent.append(name)

cli.loop_stop(); cli.disconnect()
print(f"\n===== SUMMARY =====\nloopback : {'PASS' if state['loopback'] else 'FAIL'}")
print(f"replies  : {len(state['msgs'])} / {len(COLORS)}")
print(f"elapsed  : {time.time()-t0:.1f}s")
json.dump(state["msgs"], open("/tmp/wcs/readings.json", "w"), indent=1)
sys.exit(0 if state["msgs"] else 4)
