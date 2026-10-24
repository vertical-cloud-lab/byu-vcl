#!/usr/bin/env python3
"""A stand-in A1 mini for exercising bambu_print.py without touching the real printer.

Talks to a local MQTT broker (TLS, user bblp) as the printer would, and serves a
camera stream on --camera-port with the same 80-byte login and framing. A
`project_file` command runs a short fake print: PREPARE, then RUNNING through
--layers layers at 220/65 °C, then FINISH. --fault injects one problem at
layer --fault-layer: `hms` (a serious HMS alert, and the printer pauses itself),
`hot` (nozzle runs away to 280 °C) or `cold-bed` (bed drops to 40 °C).

See test/README.md for the broker and FTPS server it pairs with.
"""
import argparse
import io
import json
import socket
import ssl
import struct
import threading
import time

import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("--serial", default="TESTSERIAL")
ap.add_argument("--code", default="testcode1")
ap.add_argument("--mqtt-port", type=int, default=18883)
ap.add_argument("--camera-port", type=int, default=16000)
ap.add_argument("--cert", default="/tmp/vsftpd.pem")
ap.add_argument("--key", default="/tmp/vsftpd.key")
ap.add_argument("--layers", type=int, default=12)
ap.add_argument("--layer-s", type=float, default=2.0)
ap.add_argument("--fault", choices=["none", "hms", "hot", "cold-bed"], default="none")
ap.add_argument("--fault-layer", type=int, default=6)
args = ap.parse_args()

S = {"gcode_state": "FINISH", "mc_percent": 100, "mc_remaining_time": 0, "layer_num": 128,
     "total_layer_num": 128, "nozzle_temper": 21.0, "nozzle_target_temper": 0, "bed_temper": 21.0,
     "bed_target_temper": 0, "print_error": 0, "hms": [], "stg_cur": 255, "sdcard": True,
     "nozzle_diameter": "0.4", "wifi_signal": "-45dBm",
     "ams": {"ams": [{"id": "0", "tray": [{"id": "0", "tray_type": "PLA", "tray_info_idx": "GFA00",
                                           "tray_sub_brands": "PLA Basic", "tray_color": "0A2989FF"}]}]}}
lock = threading.Lock()
paused = threading.Event()
stopped = threading.Event()
cl = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="fake-printer")


def report(fields=None, full=False):
    with lock:
        body = dict(S) if full else dict(fields or {})
    body["command"] = "push_status"
    cl.publish(f"device/{args.serial}/report", json.dumps({"print": body}))


def setf(**kw):
    with lock:
        S.update(kw)
    report(kw)


def fake_print():
    paused.clear(); stopped.clear()
    setf(gcode_state="PREPARE", mc_percent=0, layer_num=0, total_layer_num=args.layers,
         nozzle_target_temper=220, bed_target_temper=65, stg_cur=2)
    for i in range(5):
        setf(nozzle_temper=21 + 40 * (i + 1), bed_temper=21 + 9 * (i + 1))
        time.sleep(1)
    setf(gcode_state="RUNNING", nozzle_temper=220.0, bed_temper=65.0, stg_cur=0)
    layer = 0
    while layer < args.layers:
        if stopped.is_set():
            setf(gcode_state="FAILED", nozzle_target_temper=0, bed_target_temper=0, print_error=50348044)
            return
        if paused.is_set():
            time.sleep(0.5)
            continue
        layer += 1
        fields = {"layer_num": layer, "mc_percent": int(100 * layer / args.layers),
                  "mc_remaining_time": args.layers - layer, "nozzle_temper": 219.5 + (layer % 2)}
        if layer == args.fault_layer:
            if args.fault == "hms":
                fields.update(hms=[{"attr": 0x07000200, "code": 0x00020001}], gcode_state="PAUSE")
                paused.set()
            elif args.fault == "hot":
                fields.update(nozzle_temper=280.0)
            elif args.fault == "cold-bed":
                fields.update(bed_temper=40.0)
        if layer > args.fault_layer and args.fault == "hot":
            fields["nozzle_temper"] = 280.0
        if layer > args.fault_layer and args.fault == "cold-bed":
            fields["bed_temper"] = 40.0
        setf(**fields)
        time.sleep(args.layer_s)
    setf(gcode_state="FINISH", mc_percent=100, nozzle_target_temper=0, bed_target_temper=0, stg_cur=255)


def on_message(client, userdata, msg):
    req = json.loads(msg.payload)
    if "pushing" in req:
        report(full=True)
    elif req.get("info", {}).get("command") == "get_version":
        cl.publish(f"device/{args.serial}/report", json.dumps({"info": {
            "command": "get_version", "sequence_id": req["info"].get("sequence_id"),
            "module": [{"name": "ota", "product_name": "Bambu Lab A1 mini", "sw_ver": "00.00.00.00"}]}}))
    elif "print" in req:
        p = req["print"]
        cmd, seq = p.get("command"), p.get("sequence_id")
        print("request:", json.dumps(p), flush=True)
        ok = True
        if cmd == "project_file":
            ok = S["gcode_state"] in ("IDLE", "FINISH", "FAILED")
            if ok:
                threading.Thread(target=fake_print, daemon=True).start()
        elif cmd == "pause":
            paused.set(); setf(gcode_state="PAUSE")
        elif cmd == "resume":
            paused.clear(); setf(gcode_state="RUNNING", hms=[])
        elif cmd == "stop":
            stopped.set(); paused.clear()
        cl.publish(f"device/{args.serial}/report", json.dumps(
            {"print": {"command": cmd, "sequence_id": seq, "result": "success" if ok else "fail",
                       "reason": "" if ok else "busy"}}))


def camera_server():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(args.cert, args.key)
    srv = socket.create_server(("127.0.0.1", args.camera_port))
    while True:
        raw, _ = srv.accept()
        try:
            s = ctx.wrap_socket(raw, server_side=True)
            login = s.recv(80)
            if login[48:80].rstrip(b"\0").decode() != args.code:
                s.close(); continue
            img = Image.new("RGB", (1680, 1080), (90, 90, 90))
            ImageDraw.Draw(img).text((50, 50), f"layer {S['layer_num']}", fill=(255, 255, 255))
            buf = io.BytesIO(); img.save(buf, "JPEG")
            jpg = buf.getvalue()
            s.sendall(struct.pack("<IIII", len(jpg), 0, 0, 0) + jpg)
            time.sleep(0.2)
            s.close()
        except (ssl.SSLError, OSError):
            raw.close()


threading.Thread(target=camera_server, daemon=True).start()
cl.username_pw_set("bblp", args.code)
cl.tls_set(cert_reqs=ssl.CERT_NONE)
cl.tls_insecure_set(True)
cl.on_connect = lambda c, u, f, rc, p=None: c.subscribe(f"device/{args.serial}/request")
cl.on_message = on_message
cl.connect("127.0.0.1", args.mqtt_port)
cl.loop_forever()
