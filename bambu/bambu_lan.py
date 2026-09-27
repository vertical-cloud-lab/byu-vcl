#!/usr/bin/env python3
"""LAN client for the lab's Bambu Lab printers, reached through a Pi.

The printers are on the lab LAN, not the tailnet, so every connection goes
through an ``ssh -L`` forward to a Pi on the same LAN. Only the forwarded
printer ports are reachable (unlike a SOCKS proxy), TLS runs end to end from
here to the printer, and the access code never reaches the Pi.

Read-only subcommands, safe at any time:

  status      one full status report (``pushall`` + ``get_version``), summarised
  snapshot    one camera frame (A1 / P1 series: JPEG stream on port 6000)
  preflight   status + snapshot + the go/no-go checks from README.md

Nothing here uploads, starts, pauses or stops anything. See README.md for the
procedure that does, and for why each check exists.

Credentials come from the environment: ``{PRINTER}_IP``, ``{PRINTER}_ACCESS_CODE``
and ``{PRINTER}_SERIAL`` (``--printer A1_MINI``). The Pi comes from
``{VIA}_USERNAME`` / ``{VIA}_HOSTNAME`` (``--via CUBXL_PI``). The IP, access code,
serial and Pi hostname are never printed; files written with ``--out`` are
redacted the same way.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import io
import json
import os
import socket
import ssl
import struct
import subprocess
import sys
import time
import uuid

MQTT_PORT, CAMERA_PORT = 8883, 6000

# gcode_state values in which the printer is not doing anything.
IDLE_STATES = {"IDLE", "FINISH", "FAILED"}

# Keys whose values identify the device or the network; dropped from anything saved.
SENSITIVE_KEYS = {"sn", "net", "ip", "rtsp_url", "tutk_server", "dev_id", "ipcam_dev", "wifi_ssid",
                  "task_id", "subtask_id", "project_id", "profile_id", "job_id"}


# --------------------------------------------------------------------------- env


class Printer:
    def __init__(self, prefix: str):
        try:
            self.ip = os.environ[f"{prefix}_IP"]
            self.code = os.environ[f"{prefix}_ACCESS_CODE"]
            self.serial = os.environ[f"{prefix}_SERIAL"]
        except KeyError as e:
            sys.exit(f"missing environment variable {e.args[0]}")
        self.prefix = prefix

    def redact(self, obj):
        """Drop identifying keys and mask the IP / serial / access code anywhere."""
        if isinstance(obj, dict):
            return {k: self.redact(v) for k, v in obj.items() if k not in SENSITIVE_KEYS}
        if isinstance(obj, list):
            return [self.redact(v) for v in obj]
        if isinstance(obj, str):
            for secret, mask in ((self.code, "<code>"), (self.serial, "<serial>"), (self.ip, "<ip>")):
                obj = obj.replace(secret, mask)
        return obj


# ------------------------------------------------------------------------ tunnel


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def tunnel(via: str | None, ip: str, ports: list[int]):
    """Yield {remote_port: (host, port)}; with --via, through an ssh -L forward."""
    if not via:
        yield {p: (ip, p) for p in ports}
        return
    user, host = os.environ[f"{via}_USERNAME"], os.environ[f"{via}_HOSTNAME"]
    local = {p: _free_port() for p in ports}
    args = ["ssh", "-N", "-o", "BatchMode=yes", "-o", "ExitOnForwardFailure=yes",
            "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=15",
            "-o", "StrictHostKeyChecking=accept-new"]
    for p, lp in local.items():
        args += ["-L", f"127.0.0.1:{lp}:{ip}:{p}"]
    proc = subprocess.Popen(args + [f"{user}@{host}"], stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        deadline = time.time() + 30
        pending = set(local.values())
        while pending:
            if proc.poll() is not None:
                sys.exit(f"ssh tunnel via {via} exited with code {proc.returncode}")
            if time.time() > deadline:
                sys.exit(f"ssh tunnel via {via} did not come up in 30 s")
            for lp in list(pending):
                with contextlib.suppress(OSError), socket.create_connection(("127.0.0.1", lp), 1):
                    pending.discard(lp)
            time.sleep(0.3)
        yield {p: ("127.0.0.1", lp) for p, lp in local.items()}
    finally:
        proc.terminate()
        with contextlib.suppress(subprocess.TimeoutExpired):
            proc.wait(5)


# --------------------------------------------------------------------------- TLS


def _tls_context() -> ssl.SSLContext:
    # The printer's certificate is self-signed per device (CN = serial). It is
    # checked by hand in peer_identity() instead of by a CA bundle.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def peer_identity(addr: tuple[str, int], printer: Printer) -> dict:
    """Read the printer's TLS certificate and check its CN is the expected serial."""
    with socket.create_connection(addr, timeout=15) as raw, \
            _tls_context().wrap_socket(raw, server_hostname=printer.serial) as s:
        der = s.getpeercert(binary_form=True)
        tls = s.version()
    out = {"tls_version": tls, "cert_sha256": hashlib.sha256(der).hexdigest()[:16] + "…"}
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        cert = x509.load_der_x509_certificate(der)
        cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        issuer = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        out["cn_matches_serial"] = bool(cn) and cn[0].value == printer.serial
        out["issuer_cn"] = issuer[0].value if issuer else None
        out["not_after"] = cert.not_valid_after_utc.date().isoformat()
    except ImportError:
        out["cn_matches_serial"] = None
    return out


# -------------------------------------------------------------------------- MQTT


def _deep_update(dst: dict, src: dict) -> dict:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v
    return dst


def read_status(addr: tuple[str, int], printer: Printer, wait: float = 12.0) -> dict:
    """Connect, ask for one full report and the firmware versions, disconnect.

    Publishes only ``pushall`` and ``get_version``, the two requests that make
    the printer *send* data. Bambu advise against frequent ``pushall`` on the
    P1/A1 series, so this is done once per call.
    """
    import paho.mqtt.client as mqtt

    report, version, meta = {}, {}, {"messages": 0, "connected": False, "rc": None}
    topic_report = f"device/{printer.serial}/report"
    topic_request = f"device/{printer.serial}/request"

    def on_connect(client, userdata, flags, rc, properties=None):
        meta["rc"] = str(rc)
        if rc == 0:
            meta["connected"] = True
            client.subscribe(topic_report, qos=0)
            client.publish(topic_request, json.dumps(
                {"pushing": {"sequence_id": "1", "command": "pushall", "version": 1, "push_target": 1}}))
            client.publish(topic_request, json.dumps(
                {"info": {"sequence_id": "2", "command": "get_version"}}))

    def on_message(client, userdata, msg):
        meta["messages"] += 1
        with contextlib.suppress(ValueError):
            data = json.loads(msg.payload)
            if isinstance(data.get("print"), dict):
                _deep_update(report, data["print"])
            if isinstance(data.get("info"), dict) and data["info"].get("command") == "get_version":
                version.update(data["info"])

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id=f"vcl-probe-{uuid.uuid4().hex[:8]}", protocol=mqtt.MQTTv311)
    client.username_pw_set("bblp", printer.code)
    client.tls_set_context(_tls_context())
    client.tls_insecure_set(True)
    client.on_connect, client.on_message = on_connect, on_message
    t0 = time.time()
    client.connect(addr[0], addr[1], keepalive=30)
    client.loop_start()
    try:
        while time.time() - t0 < wait:
            if "gcode_state" in report and "nozzle_temper" in report and version.get("module"):
                break
            time.sleep(0.2)
    finally:
        client.disconnect()
        client.loop_stop()
    meta["seconds"] = round(time.time() - t0, 1)
    return {"meta": meta, "print": report, "version": version}


# ------------------------------------------------------------------------ camera


def _recv_exact(sock, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"camera closed the connection after {len(buf)}/{n} bytes")
        buf += chunk
    return bytes(buf)


def grab_frame(addr: tuple[str, int], printer: Printer, timeout: float = 20.0) -> bytes:
    """One JPEG from the A1 / P1 camera stream (TLS on port 6000).

    The stream wants an 80-byte login: four little-endian words
    (0x40, 0x3000, 0, 0), then the user ``bblp`` and the access code, each
    NUL-padded to 32 bytes. Every frame then arrives as a 16-byte header, whose
    first word is the JPEG length, followed by the JPEG itself.
    """
    login = struct.pack("<IIII", 0x40, 0x3000, 0, 0) + b"bblp".ljust(32, b"\0") \
        + printer.code.encode().ljust(32, b"\0")
    with socket.create_connection(addr, timeout=timeout) as raw, \
            _tls_context().wrap_socket(raw, server_hostname=printer.serial) as s:
        s.sendall(login)
        size = struct.unpack("<I", _recv_exact(s, 16)[:4])[0]
        if not 0 < size < 10_000_000:
            raise ValueError(f"implausible frame size {size}")
        jpg = _recv_exact(s, size)
    if jpg[:2] != b"\xff\xd8" or jpg[-2:] != b"\xff\xd9":
        raise ValueError("camera payload is not a complete JPEG")
    return jpg


def image_stats(jpg: bytes) -> dict:
    from PIL import Image, ImageStat
    img = Image.open(io.BytesIO(jpg))
    grey = img.convert("L")
    st = ImageStat.Stat(grey)
    return {"width": img.width, "height": img.height, "mean_luma": round(st.mean[0], 1),
            "luma_stddev": round(st.stddev[0], 1)}


# ------------------------------------------------------------------- sliced 3MF


def plate_info(path: str, plate: int) -> dict:
    """What a sliced Bambu 3MF plate expects of the printer, read from the file itself."""
    import re
    import xml.etree.ElementTree as ET
    import zipfile

    with zipfile.ZipFile(path) as z:
        gcode = z.read(f"Metadata/plate_{plate}.gcode")
        md5_stored = z.read(f"Metadata/plate_{plate}.gcode.md5").decode().strip().lower()
        slice_info = ET.fromstring(z.read("Metadata/slice_info.config"))
    head = gcode[:200_000].decode(errors="replace")
    cfg = dict(re.findall(r"^; (\w+) = (.*)$", head, re.M))
    hdr = dict(re.findall(r"^; ([^:=\n]+?)\s*[:=]\s*(.+)$", head.split("; HEADER_BLOCK_END")[0], re.M))
    body = gcode.decode(errors="replace")
    bed = [int(m) for m in re.findall(r"^M190 S(\d+)", body, re.M)]
    info = {"file": os.path.basename(path), "plate": plate,
            "file_md5": hashlib.md5(open(path, "rb").read()).hexdigest(),
            "gcode_md5_ok": hashlib.md5(gcode).hexdigest() == md5_stored,
            "printer_model": cfg.get("printer_model"),
            "nozzle_diameter": _num(cfg.get("nozzle_diameter")),
            "bed_type": cfg.get("curr_bed_type"),
            "filament_type": cfg.get("filament_type"),
            "filament_preset": cfg.get("filament_settings_id", "").strip('"'),
            "nozzle_c": _num(cfg.get("nozzle_temperature")),
            "bed_c": bed[0] if bed else None,
            "max_z_mm": _num(hdr.get("max_z_height")),
            "estimated_time": hdr.get("model printing time"),
            "filament_g": _num(hdr.get("total filament weight [g]")),
            "filaments": [], "warnings": []}
    for p in slice_info.iter("plate"):
        if p.find("metadata[@key='index']").get("value") == str(plate):
            info["filaments"] = [{k: f.get(k) for k in ("id", "tray_info_idx", "type", "color", "used_g")}
                                 for f in p.iter("filament")]
            info["warnings"] = sorted({w.get("msg") for w in p.iter("warning")})
    return info


# ------------------------------------------------------------------------ checks


def summarise(status: dict) -> dict:
    p = status["print"]
    ams_trays = []
    for unit in (p.get("ams") or {}).get("ams", []) or []:
        for tray in unit.get("tray", []) or []:
            if tray.get("tray_type"):
                ams_trays.append({"unit": unit.get("id"), "slot": tray.get("id"),
                                  "type": tray.get("tray_type"), "idx": tray.get("tray_info_idx"),
                                  "name": tray.get("tray_sub_brands"), "colour": tray.get("tray_color"),
                                  "remain_pct": tray.get("remain")})
    ext = p.get("vt_tray") or {}
    modules = {m.get("name"): m.get("sw_ver") for m in status["version"].get("module", []) or []}
    return {
        "gcode_state": p.get("gcode_state"),
        "stage": p.get("stg_cur"),
        "print_error": p.get("print_error"),
        "hms": p.get("hms"),
        "percent": p.get("mc_percent"),
        "remaining_min": p.get("mc_remaining_time"),
        "layer": [p.get("layer_num"), p.get("total_layer_num")],
        "nozzle_c": [p.get("nozzle_temper"), p.get("nozzle_target_temper")],
        "bed_c": [p.get("bed_temper"), p.get("bed_target_temper")],
        "nozzle": {"diameter": p.get("nozzle_diameter"), "type": p.get("nozzle_type")},
        "sdcard": p.get("sdcard"),
        "wifi_signal": p.get("wifi_signal"),
        "external_spool": {"type": ext.get("tray_type"), "colour": ext.get("tray_color")} if ext else None,
        "ams_trays": ams_trays,
        "ams_units": len((p.get("ams") or {}).get("ams", []) or []),
        "xcam": p.get("xcam"),
        "ipcam": {k: v for k, v in (p.get("ipcam") or {}).items() if k not in SENSITIVE_KEYS},
        "last_job": {"subtask_name": p.get("subtask_name"), "gcode_file": p.get("gcode_file")},
        "firmware": modules,
        "fun": p.get("fun"),
    }


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def preflight_checks(s: dict, ident: dict, cam: dict | None, plate: dict | None,
                     model: str | None) -> list[dict]:
    """Go/no-go checks. 'fail' blocks a print; 'warn' needs a human decision."""
    checks = []

    def add(name, ok, detail, severity="fail"):
        checks.append({"check": name, "result": "pass" if ok else severity, "detail": detail})

    add("right printer (TLS CN = serial)", ident.get("cn_matches_serial") is True,
        f"issuer {ident.get('issuer_cn')}")
    add("printer idle", s["gcode_state"] in IDLE_STATES, f"gcode_state={s['gcode_state']}")
    add("no print error", s["print_error"] in (0, None), f"print_error={s['print_error']}")
    add("no HMS alerts", not s["hms"], f"hms={s['hms']}")
    nz, nzt = (_num(v) for v in s["nozzle_c"])
    bd, bdt = (_num(v) for v in s["bed_c"])
    add("heaters off", nzt == 0 and bdt == 0, f"targets nozzle={nzt} bed={bdt}")
    add("nozzle thermistor plausible", nz is not None and 5 <= nz <= 60, f"nozzle={nz} °C")
    add("bed thermistor plausible", bd is not None and 5 <= bd <= 45, f"bed={bd} °C", "warn")
    add("SD card present", s["sdcard"] is True, f"sdcard={s['sdcard']}")
    if plate:
        add("3MF plate G-code intact (md5)", plate["gcode_md5_ok"], f"plate {plate['plate']}")
        add("sliced for this printer model", plate["printer_model"] == model,
            f"slice {plate['printer_model']!r}, printer {model!r}")
        add("nozzle matches the slice", _num(s["nozzle"]["diameter"]) == plate["nozzle_diameter"],
            f"printer {s['nozzle']['diameter']} mm, slice {plate['nozzle_diameter']} mm")
        add("fits the A1 mini build volume", (plate["max_z_mm"] or 0) <= 180, f"max Z {plate['max_z_mm']} mm")
        extra = set(plate["warnings"]) - {"not_support_traditional_timelapse"}
        add("no slicer warnings (beyond timelapse)", not extra, f"{sorted(plate['warnings'])}", "warn")
        want = {f["tray_info_idx"] for f in plate["filaments"]}
        slots = [t for t in s["ams_trays"] if t["idx"] in want]
        add("the sliced filament is loaded", bool(slots),
            f"slice wants {sorted(want)} ({plate['filament_preset']}); matching AMS slots (0-based): "
            f"{[(t['slot'], t['name'], t['colour']) for t in slots]}", "warn")
        add("build plate is the sliced one", False,
            f"slice assumes {plate['bed_type']} (bed {plate['bed_c']} °C); confirm on the frame or in person",
            "warn")
    sig = _num(str(s["wifi_signal"] or "").replace("dBm", ""))
    add("Wi-Fi signal usable", sig is None or sig >= -75, f"{s['wifi_signal']}", "warn")
    if s["gcode_state"] in ("FINISH", "FAILED"):
        add("last job's part removed", False,
            f"state {s['gcode_state']}: the last part may still be on the plate", "warn")
    if cam is None:
        add("camera frame", False, "no frame")
    else:
        add("camera frame", "error" not in cam, cam.get("error", f"{cam.get('width')}×{cam.get('height')}"))
        if "mean_luma" in cam:
            add("frame bright enough to judge the plate", cam["mean_luma"] >= 40,
                f"mean luma {cam['mean_luma']}/255", "warn")
        add("plate empty (human/visual check of the frame)", False,
            "not automatable yet: look at the frame", "warn")
    return checks


# --------------------------------------------------------------------------- CLI


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["status", "snapshot", "preflight"])
    ap.add_argument("--printer", default="A1_MINI", help="env prefix: A1_MINI or H2D")
    ap.add_argument("--via", default="CUBXL_PI", help="env prefix of the Pi to tunnel through; '' for direct")
    ap.add_argument("--out", default="bambu_out", help="directory for the redacted JSON and JPEG")
    ap.add_argument("--3mf", dest="threemf", help="sliced 3MF to check the printer against (preflight)")
    ap.add_argument("--plate", type=int, default=1, help="plate number in the 3MF")
    args = ap.parse_args(argv)

    printer = Printer(args.printer)
    os.makedirs(args.out, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result = {"utc": stamp, "printer": args.printer, "via": args.via or None, "command": args.command}

    with tunnel(args.via, printer.ip, [MQTT_PORT, CAMERA_PORT]) as addrs:
        if args.command in ("status", "preflight"):
            result["tls"] = peer_identity(addrs[MQTT_PORT], printer)
            status = read_status(addrs[MQTT_PORT], printer)
            result["mqtt"] = status["meta"]
            if not status["print"]:
                sys.exit(f"no status report received (mqtt {status['meta']})")
            result["summary"] = summarise(status)
            with open(os.path.join(args.out, f"{stamp}_report_redacted.json"), "w") as f:
                json.dump(printer.redact(status), f, indent=1, sort_keys=True)
        if args.command in ("snapshot", "preflight"):
            try:
                jpg = grab_frame(addrs[CAMERA_PORT], printer)
                path = os.path.join(args.out, f"{stamp}_camera.jpg")
                with open(path, "wb") as f:
                    f.write(jpg)
                result["camera"] = {"file": path, **image_stats(jpg)}
            except Exception as e:  # report, don't crash: a missing frame is itself a finding
                result["camera"] = {"error": f"{type(e).__name__}: {e}"}

    if args.command == "preflight":
        plate = plate_info(args.threemf, args.plate) if args.threemf else None
        result["plate"] = plate
        model = next((m.get("product_name") for m in status["version"].get("module", [])
                      if m.get("name") == "ota"), None)
        checks = preflight_checks(result["summary"], result["tls"], result.get("camera"), plate, model)
        result["checks"] = checks
        result["verdict"] = ("NO-GO" if any(c["result"] == "fail" for c in checks)
                             else "HUMAN-DECISION" if any(c["result"] == "warn" for c in checks)
                             else "GO")
    result = printer.redact(result)
    with open(os.path.join(args.out, f"{stamp}_{args.command}.json"), "w") as f:
        json.dump(result, f, indent=1)
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
