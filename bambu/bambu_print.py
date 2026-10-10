#!/usr/bin/env python3
"""Upload, start, watch, pause, resume and stop a print on the lab's Bambu printers.

Every subcommand except ``watch`` CHANGES PRINTER STATE. Follow README.md; the
guards here back that procedure up, they don't replace it.

  upload FILE              put a sliced 3MF on the SD card root, then read it back
                           over a fresh connection and compare MD5s
  start FILE               start plate N of an uploaded file. Refuses without a
                           preflight JSON under 15 min old for the same file and
                           plate, and --confirmed-by naming who confirmed the plate
                           is clear. --dry-run prints the command without sending it
  watch                    follow a print: log every status change, save a camera
                           frame every --frame-every s, and stop with a non-zero
                           exit code when something needs a decision
  pause | resume | stop    print control, each confirmed by the state change

Connection details, credentials and the tunnel are as in bambu_lan.py.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import threading
import time
import uuid

from bambu_lan import (CAMERA_PORT, IDLE_STATES, MQTT_PORT, Printer, _deep_update, _num, _tls_context,
                       ftps, grab_frame, image_stats, list_files, plate_info, tunnel)

SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")  # spaces gave 0500-C010 on the A1 mini

# watch exit codes
DONE, TIME_UP, NEEDS_DECISION, LOST_CONTACT, HARD_ALARM = 0, 10, 20, 30, 40


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def error_hex(n) -> str | None:
    """print_error arrives as a decimal int; Bambu's tables use XXXX-XXXX."""
    n = int(n or 0)
    return f"{n >> 16:04X}-{n & 0xFFFF:04X}" if n else None


# HMS codes this tooling has met, with what they meant here.
KNOWN_HMS = {
    # The A1 mini's answer to our first project_file (2026-09-27, firmware 01.08.00.00, printer
    # bound to Bambu's cloud): nothing moved, no ack, just this. Bambu's wiki calls it "MQTT
    # Command verification failed, please update Studio or Handy".
    "0500_0500_0001_0007": "command refused: the firmware only accepts control commands signed by "
                           "Bambu's own apps, unless LAN Only Mode and Developer Mode are on (README §2)",
}
REFUSED = "0500_0500_0001_0007"


def hms_codes(hms) -> list[dict]:
    """HMS entries as the XXXX_XXXX_XXXX_XXXX codes of Bambu's wiki, with severity."""
    levels = {1: "fatal", 2: "serious", 3: "common", 4: "info"}
    out = []
    for h in hms or []:
        a, c = int(h.get("attr", 0)), int(h.get("code", 0))
        code = f"{a >> 16:04X}_{a & 0xFFFF:04X}_{c >> 16:04X}_{c & 0xFFFF:04X}"
        out.append({"code": code, "severity": levels.get(c >> 16, str(c >> 16)),
                    **({"meaning": KNOWN_HMS[code]} if code in KNOWN_HMS else {})})
    return out


# ------------------------------------------------------------------------ MQTT


class Session:
    """One MQTT connection: merged status, plus acks for the commands we send."""

    def __init__(self, addr, printer: Printer):
        import paho.mqtt.client as mqtt
        self.printer, self.state, self.acks = printer, {}, {}
        self.last_msg = time.time()
        self.connected = threading.Event()
        self.lock = threading.Lock()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                  client_id=f"vcl-print-{uuid.uuid4().hex[:8]}", protocol=mqtt.MQTTv311)
        self.client.username_pw_set("bblp", printer.code)
        self.client.tls_set_context(_tls_context())
        self.client.tls_insecure_set(True)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = lambda *a, **k: self.connected.clear()
        self.client.reconnect_delay_set(2, 30)
        self.client.connect(addr[0], addr[1], keepalive=30)
        self.client.loop_start()
        if not self.connected.wait(20):
            raise ConnectionError("MQTT did not connect within 20 s")

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            client.subscribe(f"device/{self.printer.serial}/report")
            self.connected.set()

    def _on_message(self, client, userdata, msg):
        with contextlib.suppress(ValueError):
            data = json.loads(msg.payload)
            p = data.get("print")
            if isinstance(p, dict):
                with self.lock:
                    self.last_msg = time.time()
                    if "result" in p and "sequence_id" in p:  # the echo of a command we sent
                        self.acks[str(p["sequence_id"])] = {k: p.get(k) for k in ("command", "result", "reason")}
                    else:
                        _deep_update(self.state, p)

    def send(self, body: dict) -> str:
        seq = str(int(time.time() * 1000) % 10**9)
        key = next(iter(body))
        body[key]["sequence_id"] = seq
        self.client.publish(f"device/{self.printer.serial}/request", json.dumps(body), qos=1)
        return seq

    def pushall(self):
        self.send({"pushing": {"command": "pushall", "version": 1, "push_target": 1}})

    def get(self, key, default=None):
        with self.lock:
            return self.state.get(key, default)

    def wait(self, pred, timeout: float) -> bool:
        t0 = time.time()
        while time.time() - t0 < timeout:
            with self.lock:
                if pred(self.state, self.acks):
                    return True
            time.sleep(0.3)
        return False

    def close(self):
        self.client.disconnect()
        self.client.loop_stop()


# ---------------------------------------------------------------------- upload


def cmd_upload(args, printer):
    name = args.name or os.path.basename(args.file)
    if not SAFE_NAME.match(name):
        sys.exit(f"refusing: file name {name!r} must match {SAFE_NAME.pattern} (spaces gave 0500-C010)")
    data = open(args.file, "rb").read()
    md5 = hashlib.md5(data).hexdigest()
    with ftps(printer, args.via or None) as f:
        existing = {e["name"]: e for e in list_files(f, "/")}
        if name in existing and not args.overwrite:
            sys.exit(f"refusing: {name} already on the SD card (size {existing[name]['size']}); pass --overwrite")
        t0 = time.time()
        # The root, not /cache: /cache gave 0500-4003 on the A1 mini.
        f.storbinary(f"STOR {name}", io.BytesIO(data))
        seconds = round(time.time() - t0, 1)
    # A fresh connection to read it back: a transfer's end is where these servers misbehave.
    with ftps(printer, args.via or None) as f:
        listed = {e["name"]: e for e in list_files(f, "/")}.get(name)
        back = io.BytesIO()
        f.retrbinary(f"RETR {name}", back.write)
    ok = listed is not None and listed["size"] == len(data) and hashlib.md5(back.getvalue()).hexdigest() == md5
    print(json.dumps({"uploaded": name, "bytes": len(data), "md5": md5, "seconds": seconds,
                      "listed_size": listed and listed["size"], "read_back_md5_matches": ok}, indent=1))
    return 0 if ok else 1


# ----------------------------------------------------------------------- start


def project_file_command(name: str, plate: int, ams_slot: int | None) -> dict:
    """The payload that started this A1 mini's first programmatic print (powder-doser PR #23,
    a1_mini_send_print.py, 2026-07-27), with the task named after the file."""
    return {"print": {
        "command": "project_file",
        "param": f"Metadata/plate_{plate}.gcode",
        "project_id": "0", "profile_id": "0", "task_id": "0", "subtask_id": "0",
        "subtask_name": os.path.splitext(name.replace(".gcode.3mf", ".3mf"))[0],
        "url": f"ftp:///{name}", "file": name, "md5": "",
        "timelapse": False,  # every A1 mini 3MF warns not_support_traditional_timelapse
        "bed_type": "auto",  # take it from the file
        "bed_levelling": True, "flow_cali": True, "vibration_cali": True, "layer_inspect": True,
        "use_ams": ams_slot is not None,
        "ams_mapping": [ams_slot] if ams_slot is not None else "",  # 0-based tray index
    }}


def cmd_start(args, printer):
    name = os.path.basename(args.file)
    if not SAFE_NAME.match(name):
        sys.exit(f"refusing: file name {name!r} must match {SAFE_NAME.pattern}")
    plate = plate_info(args.file, args.plate)
    pre = json.load(open(args.preflight)) if args.preflight else {"utc": "19700101T000000Z", "summary": {"ams_trays": []}}
    age_min = (dt.datetime.now(dt.timezone.utc) - dt.datetime.strptime(pre["utc"], "%Y%m%dT%H%M%SZ")
               .replace(tzinfo=dt.timezone.utc)).total_seconds() / 60
    problems = []
    if not args.preflight:
        problems.append("no --preflight")
    elif age_min > 15:
        problems.append(f"preflight is {age_min:.0f} min old (max 15)")
    if pre.get("verdict") not in ("GO", "HUMAN-DECISION"):
        problems.append(f"preflight verdict {pre.get('verdict')}")
    if (pre.get("plate") or {}).get("file_md5") != plate["file_md5"] or pre["plate"]["plate"] != args.plate:
        problems.append("preflight was run against a different file or plate")
    if not args.confirmed_by:
        problems.append("--confirmed-by is required: who confirmed the plate is clear and is the sliced plate type")
    if args.ams_slot is not None and not any(t["slot"] == str(args.ams_slot) and
                                             t["idx"] in {f["tray_info_idx"] for f in plate["filaments"]}
                                             for t in pre["summary"]["ams_trays"]):
        problems.append(f"AMS slot {args.ams_slot} (0-based) does not hold the sliced filament")
    if problems and not args.dry_run:
        sys.exit("refusing to start:\n  - " + "\n  - ".join(problems))

    body = project_file_command(name, args.plate, args.ams_slot)
    if args.dry_run:
        print(json.dumps({"would_send": body, "problems": problems}, indent=1))
        return 0

    with ftps(printer, args.via or None) as f:
        listed = {e["name"]: e for e in list_files(f, "/")}.get(name)
    if not listed or listed["size"] != os.path.getsize(args.file):
        sys.exit(f"refusing: {name} is not on the SD card at the right size; run upload first")

    with tunnel(args.via, printer.ip, [MQTT_PORT]) as addrs:
        s = Session(addrs[MQTT_PORT], printer)
        try:
            s.pushall()
            if not s.wait(lambda st, a: "gcode_state" in st, 15):
                sys.exit("refusing: no status from the printer")
            before = {k: s.get(k) for k in ("gcode_state", "print_error", "hms")}
            if before["gcode_state"] not in IDLE_STATES or before["print_error"] or before["hms"]:
                sys.exit(f"refusing: printer not ready: {before}")
            seq = s.send(body)
            print(f"{now()} sent project_file for {name} plate {args.plate}, "
                  f"AMS slot {args.ams_slot}, confirmed by {args.confirmed_by}", flush=True)
            # A refusal comes back as an HMS entry, not as an ack.
            started = s.wait(lambda st, a: st.get("gcode_state") in ("PREPARE", "RUNNING")
                             or a.get(seq, {}).get("result") not in (None, "success")
                             or REFUSED in {h["code"] for h in hms_codes(st.get("hms"))}, 90)
            result = {"ack": s.acks.get(seq), "gcode_state": s.get("gcode_state"),
                      "print_error": error_hex(s.get("print_error")), "hms": hms_codes(s.get("hms")),
                      "started": started and s.get("gcode_state") in ("PREPARE", "RUNNING")}
        finally:
            s.close()
    print(json.dumps(result, indent=1))
    return 0 if result["started"] else 1


# ----------------------------------------------------------------------- watch


def cmd_watch(args, printer):
    expect = plate_info(args.threemf, args.plate) if args.threemf else {}
    os.makedirs(args.out, exist_ok=True)
    log = open(os.path.join(args.out, "watch.jsonl"), "a")
    deadline = time.time() + 60 * args.minutes
    code, reason = TIME_UP, "time budget reached; still printing"
    seen_running, first = False, True
    last_layer, last_layer_t = None, time.time()
    off_temp_since: dict[str, float] = {}
    next_frame, last_line, last_push = 0.0, 0.0, 0.0

    with tunnel(args.via, printer.ip, [MQTT_PORT, CAMERA_PORT]) as addrs:
        s = Session(addrs[MQTT_PORT], printer)
        s.pushall()
        s.wait(lambda st, a: "gcode_state" in st, 15)
        try:
            while time.time() < deadline:
                time.sleep(2)
                st = {k: s.get(k) for k in ("gcode_state", "mc_percent", "mc_remaining_time", "layer_num",
                                            "total_layer_num", "nozzle_temper", "nozzle_target_temper",
                                            "bed_temper", "bed_target_temper", "print_error", "hms",
                                            "stg_cur")}
                st["t"] = now()
                state = st["gcode_state"]
                seen_running |= state == "RUNNING"
                nz, nzt, bd, bdt = (_num(st[k]) for k in ("nozzle_temper", "nozzle_target_temper",
                                                           "bed_temper", "bed_target_temper"))
                alarms = []

                # Hard limits, any phase: the A1 mini tops out at 300 °C nozzle, 80 °C bed,
                # and a PLA job never asks for more than the 250 °C flush.
                if (nz or 0) > args.max_nozzle or (bd or 0) > args.max_bed:
                    alarms.append(("hard", f"temperature over limit: nozzle {nz}, bed {bd}"))
                if (nzt or 0) > args.max_nozzle or (bdt or 0) > args.max_bed:
                    alarms.append(("hard", f"target over limit: nozzle {nzt}, bed {bdt}"))
                # An HMS entry or error someone has already looked at can be acknowledged
                # with --ack-hms / --ack-error; anything else ends the watch.
                if st["print_error"] and error_hex(st["print_error"]) not in args.ack_error:
                    alarms.append(("decision", f"print_error {error_hex(st['print_error'])}"))
                new_hms = [h for h in hms_codes(st["hms"]) if h["code"] not in args.ack_hms]
                if new_hms:
                    alarms.append(("decision", f"HMS {new_hms}"))
                if state in ("PAUSE", "FAILED"):
                    alarms.append(("decision", f"printer is {state}"))

                # Past layer 1: each heater should hold its target (a heater or sensor fault),
                # and each target should be the file's value (someone changed it, or wrong file).
                if state == "RUNNING" and (st["layer_num"] or 0) >= 2:
                    for key, val, target, want, tol in (
                            ("nozzle", nz, nzt, expect.get("nozzle_c"), args.nozzle_tol),
                            ("bed", bd, bdt, expect.get("bed_c"), args.bed_tol)):
                        off = []
                        if val is not None and target and abs(val - target) > tol:
                            off.append(f"{key} {val} °C vs target {target}")
                        if target is not None and want and abs(target - want) > tol:
                            off.append(f"{key} target {target} °C vs the file's {want}")
                        if off:
                            off_temp_since.setdefault(key, time.time())
                            if time.time() - off_temp_since[key] > 90:
                                alarms.append(("decision", "; ".join(off) + f" (± {tol}) for 90 s"))
                        else:
                            off_temp_since.pop(key, None)

                # Stalled: layer unchanged for too long while RUNNING.
                if st["layer_num"] != last_layer:
                    last_layer, last_layer_t = st["layer_num"], time.time()
                elif state == "RUNNING" and time.time() - last_layer_t > 60 * args.stall_min:
                    alarms.append(("decision", f"layer {last_layer} unchanged for {args.stall_min} min"))

                silent = time.time() - s.last_msg
                if silent > 60 and state in ("RUNNING", "PREPARE") and time.time() - last_push > 60:
                    s.pushall()  # the A1 mini only sends deltas; ask before assuming the worst
                    last_push = time.time()
                if silent > 300:
                    code, reason = LOST_CONTACT, f"no status for {silent:.0f} s"
                    break

                if time.time() >= next_frame:
                    next_frame = time.time() + args.frame_every
                    try:
                        jpg = grab_frame(addrs[CAMERA_PORT], printer)
                        path = os.path.join(args.out, f"{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%SZ}"
                                                      f"_L{st['layer_num']}.jpg")
                        open(path, "wb").write(jpg)
                        st["frame"] = {"file": os.path.basename(path), **image_stats(jpg)}
                    except Exception as e:
                        st["frame"] = {"error": f"{type(e).__name__}: {e}"}

                st["alarms"] = alarms
                st["hms"], st["print_error"] = hms_codes(st["hms"]), error_hex(st["print_error"])
                log.write(json.dumps(st) + "\n")
                log.flush()
                if time.time() - last_line > 60 or alarms or "frame" in st:
                    last_line = time.time()
                    print(f"{st['t']} {state} {st['mc_percent']}% layer {st['layer_num']}/{st['total_layer_num']} "
                          f"nozzle {nz}/{nzt} bed {bd}/{bdt} left {st['mc_remaining_time']} min"
                          + (f" frame {st['frame'].get('file', st['frame'].get('error'))}" if "frame" in st else "")
                          + (f" ALARMS {alarms}" if alarms else ""), flush=True)

                if any(kind == "hard" for kind, _ in alarms):
                    code, reason = HARD_ALARM, "; ".join(m for _, m in alarms)
                    if args.auto_stop:
                        s.send({"print": {"command": "stop", "param": ""}})
                        stopped = s.wait(lambda st, a: st.get("gcode_state") in ("FAILED", "IDLE", "FINISH"), 60)
                        reason += " -> stop sent, " + ("confirmed" if stopped else "NOT confirmed within 60 s")
                    break
                if alarms:
                    code, reason = NEEDS_DECISION, "; ".join(m for _, m in alarms)
                    break
                if state == "FINISH" and seen_running:
                    code, reason = DONE, "print finished"
                    break
                if first and state in IDLE_STATES:
                    code, reason = NEEDS_DECISION, (f"printer is {state} at {st['mc_percent']}%: nothing is printing"
                                                    " (a job that ended between two watches reads this way too)")
                    break
                first = False
        finally:
            s.close()
    print(json.dumps({"exit": code, "reason": reason, "t": now()}), flush=True)
    return code


# --------------------------------------------------------------------- control


def cmd_control(args, printer):
    if args.command == "stop" and not args.yes_stop:
        sys.exit("stop cancels the print for good; pass --yes-stop")
    want = {"pause": {"PAUSE"}, "resume": {"RUNNING"}, "stop": {"FAILED", "IDLE", "FINISH"}}[args.command]
    with tunnel(args.via, printer.ip, [MQTT_PORT]) as addrs:
        s = Session(addrs[MQTT_PORT], printer)
        try:
            s.pushall()
            s.wait(lambda st, a: "gcode_state" in st, 15)
            before = s.get("gcode_state")
            seq = s.send({"print": {"command": args.command, "param": ""}})
            ok = s.wait(lambda st, a: st.get("gcode_state") in want, 60)
            out = {"command": args.command, "before": before, "after": s.get("gcode_state"),
                   "ack": s.acks.get(seq), "confirmed": ok}
        finally:
            s.close()
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["upload", "start", "watch", "pause", "resume", "stop"])
    ap.add_argument("file", nargs="?", help="sliced 3MF (upload, start)")
    ap.add_argument("--printer", default="A1_MINI")
    ap.add_argument("--via", default="CUBXL_PI", help="env prefix of the Pi; '' for direct")
    ap.add_argument("--name", help="upload: name on the SD card (default: the file's)")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--plate", type=int, default=1)
    ap.add_argument("--ams-slot", type=int, help="0-based AMS tray for filament 1; omit for the external spool")
    ap.add_argument("--preflight", help="start: the JSON bambu_lan.py preflight --3mf wrote")
    ap.add_argument("--confirmed-by", help="start: who confirmed the plate is clear (GitHub user)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--3mf", dest="threemf", help="watch: the sliced file, for its temperatures")
    ap.add_argument("--minutes", type=float, default=50, help="watch: time budget (<60 per Bash call)")
    ap.add_argument("--frame-every", type=float, default=60, help="watch: seconds between camera frames")
    ap.add_argument("--out", default="bambu_watch")
    ap.add_argument("--stall-min", type=float, default=15)
    ap.add_argument("--nozzle-tol", type=float, default=15)
    ap.add_argument("--bed-tol", type=float, default=8)
    ap.add_argument("--max-nozzle", type=float, default=260)
    ap.add_argument("--max-bed", type=float, default=80)
    ap.add_argument("--auto-stop", action="store_true", help="watch: send stop on a hard temperature alarm")
    ap.add_argument("--ack-hms", default="", type=lambda v: set(filter(None, v.split(","))),
                    help="watch: HMS codes (XXXX_XXXX_XXXX_XXXX) already looked at, comma-separated")
    ap.add_argument("--ack-error", default="", type=lambda v: set(filter(None, v.split(","))),
                    help="watch: print_error codes (XXXX-XXXX) already looked at")
    ap.add_argument("--yes-stop", action="store_true")
    args = ap.parse_args(argv)
    if args.command in ("upload", "start") and not args.file:
        ap.error(f"{args.command} needs FILE")
    if args.command == "start" and not args.dry_run and not args.preflight:
        ap.error("start needs --preflight")
    printer = Printer(args.printer)
    fn = {"upload": cmd_upload, "start": cmd_start, "watch": cmd_watch}.get(args.command, cmd_control)
    return fn(args, printer)


if __name__ == "__main__":
    sys.exit(main())
