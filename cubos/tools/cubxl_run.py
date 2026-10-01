#!/usr/bin/env python3
"""One command for a CubXL hardware run: checks, gates, run, post-run, summary.

Run it on the CubXL Pi with CubOS's own interpreter, from a checkout of this
repo (``git pull`` it first, so the configs that run are the committed ones):

    ~/CubOS/.venv/bin/python ~/byu-vcl-pipette/cubos/tools/cubxl_run.py \\
        --name pipette_test_20261001

That runs the pipette trio (the default gantry / deck / protocol below) and
writes everything into ``~/cubxl_runs/<name>/``, with ``SUMMARY.md`` as the
one-screen answer. That folder is outside the checkout so ``git pull`` never
trips over it; copy it into ``cubos/results/`` to commit it. Stages, in order; any refusal before stage 3 stops the run
with nothing moved:

  1. checks   versions and applied CubOS patches; ports present, not held by
              another process, and named identically wherever they are shared;
              protocol step 0 is ``home``; GRBL ``$$``/``$#`` against the gantry
              file, ``G54 == -max_travel``, the feed rate within ``$110``-``$112``;
              the Arduino answers, nothing is held on the magnet; the Tic's
              settings equal ``cubos/docs/tic_p20.txt``, then it is energized.
  2. gates    ``validate_setup``, ``run_protocol --mock``, ``passive_shadow``
              nominal and ``--tip-stuck``. All must pass.
  3. run      ``run_with_camera_and_plunger_trace.py``, with the Tic polled and
              CubOS's gantry logs sliced to this run.
  4. post-run magnet off, cap sensor, plunger STATUS; optionally a plunger HOME
              whose duration checks the plunger lost no steps; Tic de-energized.
  5. summary  ``SUMMARY.md`` and ``summary.json``.

Nothing here jogs the gantry or unlocks it. Opening the GRBL port resets the
board, which is why step 0 has to be ``home``: an unhomed GRBL accepts moves
against a position it no longer knows (the 2026-09-18 Y overrun).

Exit status: 0 the protocol completed, 1 it ran and failed, 2 a check or gate
refused it (nothing moved), 3 the runner itself broke.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import shutil
import signal
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent.parent
DEFAULT_GANTRY = REPO / "cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml"
DEFAULT_DECK = REPO / "cubos/configs/deck/ben_6vials_tiprack.yaml"
DEFAULT_PROTOCOL = REPO / "cubos/configs/protocol/vcl/pipette_test.yaml"
TIC_SETTINGS = REPO / "cubos/docs/tic_p20.txt"
TICCMD = Path.home() / ".local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd"
LAB_UTC_OFFSET_H = -6          # lab local time, which CubOS's logs are written in

# gantry-file grbl_settings key -> GRBL setting
GRBL_KEYS = {
    "dir_invert_mask": "$3", "status_report": "$10", "soft_limits": "$20",
    "hard_limits": "$21", "homing_enable": "$22", "homing_dir_mask": "$23",
    "homing_pull_off": "$27", "steps_per_mm_x": "$100", "steps_per_mm_y": "$101",
    "steps_per_mm_z": "$102", "max_rate_x": "$110", "max_rate_y": "$111",
    "max_rate_z": "$112", "acceleration_x": "$120", "acceleration_y": "$121",
    "acceleration_z": "$122", "max_travel_x": "$130", "max_travel_y": "$131",
    "max_travel_z": "$132",
}
CUBOS_DEFAULT_FEED = 3000.0    # gantry_driver/driver.py DEFAULT_FEED_RATE at 496819c
PLUNGER = {10: "HOME", 11: "MOVE_TO", 12: "ASPIRATE", 13: "DISPENSE", 14: "STATUS"}
# Post-run HOME calibration, from 2026-09-30 (campaign 68): a HOME from firmware
# position 28.0 mm took 12.680 s. The seek and the 796-step back-off both run
# at ~10 + 500 us per step plus loop overhead; the rest is the 100 ms debounce.
HOME_FIXED_S = 0.11
HOME_S_PER_STEP = (12.680 - HOME_FIXED_S) / (28.0 * 796 + 796)
STEPS_PER_MM = 796.0


class Refused(Exception):
    """A check or gate said no. Nothing has moved."""


class Out:
    def __init__(self, outdir: Path):
        self.dir = outdir
        self.log = open(outdir / "runner.log", "a", buffering=1)

    def say(self, msg: str = "") -> None:
        line = f"{dt.datetime.now(dt.timezone.utc):%H:%M:%S}Z  {msg}" if msg else ""
        self.log.write(line + "\n")
        try:
            print(line, flush=True)
        except OSError:          # the terminal went away; the file keeps everything
            pass

    def write(self, name: str, text: str) -> Path:
        p = self.dir / name
        p.write_text(text)
        return p


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def num(x, spec="g") -> str:
    return "?" if x is None else format(x, spec)


def lab(t: dt.datetime) -> str:
    return (t + dt.timedelta(hours=LAB_UTC_OFFSET_H)).strftime("%H:%M:%S")


def sh(cmd, timeout=120, cwd=None, env=None) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                           timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)
    except FileNotFoundError as e:
        return 127, str(e)
    except subprocess.TimeoutExpired as e:
        return 124, f"timeout after {timeout}s: {e}"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def load_yaml(path: Path):
    import yaml
    return yaml.safe_load(path.read_text())


# --------------------------------------------------------------------- checks
def check_versions(a, out: Out, rec: dict) -> None:
    rc, head = sh(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"])
    rc2, dirty = sh(["git", "-C", str(REPO), "status", "--porcelain", "--",
                     str(a.gantry), str(a.deck), str(a.protocol)])
    rec["byu_vcl"] = {"commit": head.strip(), "configs_dirty": bool(dirty.strip())}
    _, cub = sh(["git", "-C", str(a.cubos), "rev-parse", "--short", "HEAD"])
    applied = []
    for patch in sorted((REPO / "cubos/patches").glob("*.patch")):
        rc, _ = sh(["git", "-C", str(a.cubos), "apply", "--reverse", "--check", str(patch)])
        if rc == 0:
            applied.append(patch.name)
    rec["cubos"] = {"commit": cub.strip(), "patches_applied": applied}
    rec["configs"] = {p.name: sha(p) for p in (a.gantry, a.deck, a.protocol)}
    out.say(f"byu-vcl {head.strip()}{' (configs MODIFIED vs commit)' if dirty.strip() else ''}"
            f" | CubOS {cub.strip()} + {len(applied)} patch(es): {', '.join(applied) or 'none'}")
    _, thr = sh(["vcgencmd", "get_throttled"])
    _, up = sh(["uptime", "-p"])
    rec["pi"] = {"throttled": thr.strip(), "uptime": up.strip()}
    out.say(f"Pi {up.strip()}, {thr.strip() or 'throttled=?'}")


def _holders(real: str) -> list[str]:
    pids = []
    for fd in glob.glob("/proc/[0-9]*/fd/*"):
        try:
            if os.path.realpath(fd) == real:
                pids.append(fd.split("/")[2])
        except OSError:
            pass
    return sorted(set(pids) - {str(os.getpid())})


def check_ports(a, g: dict, out: Out, rec: dict) -> dict:
    ports = {"gantry": g["serial_port"]}
    for name, inst in (g.get("instruments") or {}).items():
        if inst.get("port") and not inst.get("offline"):
            ports[name] = inst["port"]
    by_id = {os.path.realpath(p): p for p in glob.glob("/dev/serial/by-id/*")}
    res, seen = {}, {}
    for who, port in ports.items():
        if not os.path.exists(port):
            raise Refused(f"{who}: port {port} does not exist")
        real = os.path.realpath(port)
        if real in seen and seen[real] != port:
            raise Refused(f"{who} names {port} but another instrument names {seen[real]} for "
                          f"the same device; CubOS would open it twice and reset the board")
        seen[real] = port
        held = _holders(real)
        if held:
            raise Refused(f"{who}: {port} is held open by pid(s) {held}")
        res[who] = {"port": port, "device": real, "by_id": by_id.get(real, "")}
    rec["ports"] = res
    out.say("ports: " + ", ".join(f"{k} {v['port']} -> {v['device']}" for k, v in res.items())
            + " (none held open)")
    return res


def check_protocol_starts_with_home(a, out: Out, rec: dict) -> list:
    proto = load_yaml(a.protocol)
    steps = proto.get("protocol", proto) if isinstance(proto, dict) else proto
    first = steps[0] if steps else None
    first_cmd = (next(iter(first)) if isinstance(first, dict) else str(first)) if first else None
    cmds = [next(iter(x)) if isinstance(x, dict) else str(x) for x in steps]
    rec["protocol"] = {"steps": len(steps), "first": first_cmd, "commands": cmds}
    if "breakpoint" in cmds:
        raise Refused("the protocol has a breakpoint, and this run is headless (stdin is "
                      "/dev/null), so CubOS would skip it and carry on. Run it by hand in a "
                      "foreground terminal instead")
    if first_cmd != "home" and not a.allow_no_home:
        raise Refused(f"protocol step 0 is {first_cmd!r}, not 'home'. Opening the GRBL port "
                      f"resets the board, so without a home the run would move against a "
                      f"position GRBL no longer knows (--allow-no-home overrides)")
    out.say(f"protocol: {len(steps)} steps, step 0 = {first_cmd}")
    return steps


def check_grbl(a, g: dict, out: Out, rec: dict) -> None:
    import serial
    port = g["serial_port"]
    s = serial.Serial(port, 115200, timeout=0.2)
    try:
        time.sleep(2.5)                           # the port open reset the board
        banner = s.read(4096).decode(errors="replace").strip()

        def q(cmd: bytes, until: bytes = b"ok", wait: float = 3.0) -> str:
            s.reset_input_buffer()
            s.write(cmd)
            buf, t0 = b"", time.time()
            while time.time() - t0 < wait:
                buf += s.read(4096)
                if until in buf:
                    break
            return buf.decode(errors="replace").strip()

        dd, off, st = q(b"$$\n"), q(b"$#\n"), q(b"?", until=b">", wait=1.5)
    finally:
        s.close()
    vals = {k: float(v) for k, v in re.findall(r"^(\$\d+)=([-\d.]+)", dd, re.M)}
    m = re.search(r"\[G54:([-\d.]+),([-\d.]+),([-\d.]+)\]", off)
    g54 = [float(x) for x in m.groups()] if m else None
    (out.dir / "grbl_before.json").write_text(json.dumps(
        {"t_utc": utc_now().isoformat(timespec="seconds"), "banner": banner,
         "settings": vals, "offsets_raw": off, "status": st}, indent=2))
    bad = []
    for key, want in (g.get("grbl_settings") or {}).items():
        code = GRBL_KEYS.get(key)
        if code is None:
            continue
        want = float(want) if not isinstance(want, bool) else (1.0 if want else 0.0)
        got = vals.get(code)
        if got is None or abs(got - want) > 0.001:
            bad.append(f"{code} ({key}) is {got}, gantry file says {want}")
    travel = [vals.get("$130"), vals.get("$131"), vals.get("$132")]
    if g54 is None or None in travel or any(abs(o + t) > 0.001 for o, t in zip(g54, travel)):
        bad.append(f"G54 {g54} is not -max_travel {travel}: the work frame the deck was "
                   f"measured in is gone (a factory reset does this)")
    feed = float((g.get("cnc") or {}).get("default_feed_rate_mm_min") or CUBOS_DEFAULT_FEED)
    rates = [vals.get(c) for c in ("$110", "$111", "$112")]
    if None in rates or feed > min(rates):
        bad.append(f"feed {feed} mm/min exceeds a max rate {rates}")
    rec["grbl"] = {"status": st, "g54": g54, "max_travel": travel, "feed_mm_min": feed,
                   "max_rate": rates, "accel": [vals.get(c) for c in ("$120", "$121", "$122")],
                   "soft_limits": vals.get("$20"), "hard_limits": vals.get("$21"),
                   "mismatches": bad}
    out.say(f"GRBL: {st} | $20={num(vals.get('$20'))} $21={num(vals.get('$21'))} "
            f"travel {travel} G54 {g54} | feed F{feed:g} vs max {rates}")
    if bad:
        raise Refused("GRBL does not match the gantry file: " + "; ".join(bad))


def arduino(a, port: str, out: Out, cmds, label: str) -> list[dict]:
    from cubos.instruments.controllers.pawduino import PawduinoLink
    link = PawduinoLink.acquire(port, 115200)
    t0 = time.monotonic()
    link.connect()
    rows = [{"cmd": "connect", "dt_s": round(time.monotonic() - t0, 3), "reply": "ok"}]
    try:
        for name, code, timeout in cmds:
            t0 = time.monotonic()
            t_wall = utc_now()
            try:
                r = link.send_command(code, timeout=timeout)
            except Exception as e:                       # noqa: BLE001  ERR replies raise
                r = f"RAISED {e!r}"
            rows.append({"cmd": name, "code": code, "t": t_wall.isoformat(timespec="milliseconds"),
                         "dt_s": round(time.monotonic() - t0, 3), "reply": r})
    finally:
        link.disconnect()
    lines = [f"{r.get('t', '')[11:23]:<12} {r['cmd']:<16} dt={r['dt_s']:7.3f}s  {r['reply']}"
             for r in rows]
    out.write(f"arduino_{label}.log", "\n".join(lines) + "\n")
    for ln in lines:
        out.say(f"  {ln}")
    return rows


def tic(*args: str) -> tuple[int, str]:
    return sh([str(TICCMD), *args], timeout=20)


def tic_status() -> dict:
    rc, s = tic("--status")
    d = {"rc": rc}
    for key, pat in (("vin", r"VIN voltage:\s+([\d.]+)"), ("energized", r"Energized:\s+(\w+)"),
                     ("state", r"Operation state:\s+(.+)")):
        m = re.search(pat, s)
        d[key] = m.group(1).strip() if m else None
    m = re.search(r"Errors currently stopping the motor:\s*(.*?)\n(?:Errors that|\Z)", s, re.S)
    d["stopping"] = " ".join(x.strip(" -") for x in m.group(1).splitlines() if x.strip()) if m else None
    m = re.search(r"Errors that occurred since last check:\s*(.*?)(?:\n\S|\Z)", s, re.S)
    d["since_last"] = " ".join(x.strip(" -") for x in m.group(1).splitlines() if x.strip()) if m else None
    d["raw"] = s
    return d


def check_tic(a, out: Out, rec: dict) -> None:
    if a.no_tic:
        rec["tic"] = "skipped (--no-tic)"
        return
    found = out.dir / "tic_settings.txt"
    rc, msg = tic("--get-settings", str(found))
    if rc != 0 or not found.exists():
        raise Refused(f"ticcmd failed ({rc}): {msg.strip()[:200]}")
    norm = lambda t: [ln.rstrip() for ln in t.strip().splitlines()]   # noqa: E731
    if norm(found.read_text()) != norm(TIC_SETTINGS.read_text()):
        raise Refused(f"Tic settings differ from {TIC_SETTINGS.relative_to(REPO)} "
                      f"(read back into tic_settings.txt)")
    before = tic_status()
    out.write("tic_before.txt", before.pop("raw"))
    rc, msg = tic("--energize")
    time.sleep(1.0)
    st = tic_status()
    out.write("tic_energized.txt", st.pop("raw"))
    rec["tic"] = {"before": before, "energized": st}
    out.say(f"Tic: settings = tic_p20.txt; was {before['state']}, VIN {before['vin']} V; "
            f"now energized={st['energized']}, VIN {st['vin']} V, stopping: {st['stopping']}")
    if rc != 0 or st["energized"] != "Yes" or (st["stopping"] or "None") != "None":
        raise Refused(f"Tic did not energize cleanly: rc={rc} {msg.strip()[:120]} {st}")
    if float(st["vin"] or 0) < 10.0:
        raise Refused(f"Tic VIN {st['vin']} V is under 10 V")


# ---------------------------------------------------------------------- gates
def gates(a, out: Out, rec: dict) -> None:
    py, env = sys.executable, dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    G, D, P = str(a.gantry), str(a.deck), str(a.protocol)
    runs = [
        ("validate", [py, "-m", "cubos.tools.validate_setup", G, D, P],
         lambda rc, t: "RESULT: PASS" in t),
        ("mock", [py, "-m", "cubos.tools.run_protocol", G, D, P, "--mock"],
         lambda rc, t: "Protocol complete" in t),
        ("shadow", [py, str(TOOLS / "passive_shadow.py"), G, D, P],
         lambda rc, t: rc == 0),
        ("shadow_tipstuck", [py, str(TOOLS / "passive_shadow.py"), G, D, P, "--tip-stuck"],
         lambda rc, t: rc == 0),
    ]
    res = {}
    for name, cmd, ok in runs:
        t0 = time.monotonic()
        rc, text = sh(cmd, timeout=600, cwd=str(a.cubos), env=env)
        out.write(f"gate_{name}.log", text)
        passed = ok(rc, text)
        res[name] = {"pass": passed, "rc": rc, "s": round(time.monotonic() - t0, 1)}
        tail = [ln for ln in text.splitlines() if ln.strip()][-1:] or [""]
        out.say(f"gate {name:<16} {'PASS' if passed else 'FAIL'}  ({res[name]['s']} s)  {tail[0][:100]}")
    rec["gates"] = res
    failed = [k for k, v in res.items() if not v["pass"]]
    if failed:
        raise Refused(f"gate(s) failed: {failed} (see gate_*.log)")


# ------------------------------------------------------------------------ run
class TicPoller(threading.Thread):
    def __init__(self, path: Path):
        super().__init__(daemon=True)
        self.path, self.stop, self.rows = path, threading.Event(), []

    def run(self):
        with open(self.path, "w", buffering=1) as fh:
            while not self.stop.is_set():
                st = tic_status()
                st.pop("raw", None)
                st["t"] = utc_now().isoformat(timespec="milliseconds")
                self.rows.append(st)
                fh.write(json.dumps(st) + "\n")
                self.stop.wait(0.5)


def log_offsets() -> dict:
    return {p: os.path.getsize(p) for p in glob.glob(str(Path.home() / ".cubos/logs/gantry/*.log"))}


def slice_logs(before: dict, out: Out) -> dict:
    sliced = {}
    for p, off in before.items():
        with open(p, "rb") as fh:
            fh.seek(off)
            data = fh.read()
        name = "gantry_" + Path(p).name
        (out.dir / name).write_bytes(data)
        sliced[Path(p).name] = name
    return sliced


def run(a, out: Out, rec: dict) -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PLUNGER_TRACE_OUT=str(out.dir / "plunger_trace.json"),
               STEP_TRACE_OUT=str(out.dir / "step_trace.json"))
    cmd = [sys.executable, str(TOOLS / "run_with_camera_and_plunger_trace.py")]
    if a.no_camera:
        env["CUBXL_NO_CAMERA"] = "1"
    else:
        cmd += ["--outdir", str(out.dir / "frames"), "--at", a.frames_at,
                "--width", "1536", "--height", "864"]
    cmd += ["--", str(a.gantry), str(a.deck), str(a.protocol)]
    offsets = log_offsets()
    campaigns_before = set(glob.glob(str(a.cubos / "packages/core/src/cubos/data/results/campaign_*")))
    poller = TicPoller(out.dir / "tic_poll.jsonl") if not a.no_tic else None
    if poller:
        poller.start()
    t_start = utc_now()
    out.say(f"RUN start {t_start:%H:%M:%S}Z ({lab(t_start)} lab)")
    with open(out.dir / "run_hardware.log", "w") as fh:
        p = subprocess.Popen(cmd, cwd=str(a.cubos), env=env, stdout=fh, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL)
        rc = p.wait()
    t_end = utc_now()
    if poller:
        poller.stop.set()
        poller.join(5)
    out.say(f"RUN end   {t_end:%H:%M:%S}Z ({lab(t_end)} lab), {(t_end - t_start).total_seconds():.1f} s, rc={rc}")
    sliced = slice_logs(offsets, out)
    new = sorted(set(glob.glob(str(a.cubos / "packages/core/src/cubos/data/results/campaign_*")))
                 - campaigns_before, key=os.path.getmtime)
    for c in new:
        shutil.copytree(c, out.dir / Path(c).name, dirs_exist_ok=True)
    _, k = sh(["journalctl", "-k", "--no-pager", "-o", "short-iso",
               f"--since=@{int(t_start.timestamp())}", f"--until=@{int(t_end.timestamp()) + 1}"])
    out.write("kernel_during_run.log", k)
    return {"rc": rc, "t_start": t_start, "t_end": t_end, "logs": sliced,
            "campaigns": [Path(c).name for c in new],
            "tic_rows": poller.rows if poller else []}


# ------------------------------------------------------------------- post-run
def plunger_end_position(trace: list) -> float | None:
    pos = None
    for r in trace:
        if r.get("error") or not str(r.get("reply") or "").startswith("OK"):
            continue
        code, args = r.get("code"), [a.strip("'\"") for a in r.get("args", [])]
        m = re.search(r'"v":\[([^\]]*)\]', r["reply"] or "")
        v = [float(x) for x in m.group(1).split(",")] if m else []
        if code == 10:
            pos = 0.0
        elif code == 11 and args:
            pos = float(args[0])
        elif code == 12 and len(v) >= 2:
            pos = v[1]
    return pos


def post_run(a, ports: dict, out: Out, rec: dict, trace: list) -> None:
    pipette_port = (ports.get("pipette") or ports.get("vial_capper_decapper") or {}).get("port")
    cmds = [("EMAG_OFF", 6, 10), ("cap sensor", 7, 10), ("STATUS", 14, 10)]
    if a.home_check:
        cmds.append(("HOME", 10, 60))
    if pipette_port:
        out.say("post-run Arduino:")
        rows = arduino(a, pipette_port, out, cmds, "after")
        rec["arduino_after"] = rows
        home = next((r for r in rows if r["cmd"] == "HOME"), None)
        end = plunger_end_position(trace)
        if home and end is not None and str(home["reply"]).startswith("OK"):
            implied = ((home["dt_s"] - HOME_FIXED_S) / HOME_S_PER_STEP - 796) / STEPS_PER_MM
            rec["home_check"] = {"firmware_end_mm": end, "home_dt_s": home["dt_s"],
                                 "implied_mm": round(implied, 2),
                                 "lost_mm": round(implied - end, 2)}
            out.say(f"HOME check: plunger ended at {end} mm (firmware); HOME took "
                    f"{home['dt_s']:.3f} s, which implies {implied:.2f} mm "
                    f"({implied - end:+.2f} mm)")
    if not a.no_tic:
        if a.keep_energized:
            st = tic_status()
        else:
            tic("--deenergize")
            time.sleep(1.0)
            st = tic_status()
        out.write("tic_after.txt", st.pop("raw"))
        rec["tic_after"] = st
        out.say(f"Tic after: energized={st['energized']}, VIN {st['vin']} V, "
                f"errors since last check: {st['since_last']}")


# -------------------------------------------------------------------- summary
def parse_gcode_timing(path: Path) -> dict:
    if not path.exists():
        return {}
    rows, pending = [], None
    for ln in path.read_text(errors="replace").splitlines():
        m = re.match(r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3})&.*?&(Command sent|Returned|Homing completed)(?:: )?(.*)", ln)
        if not m:
            continue
        t = dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S,%f")
        kind, body = m.group(2), m.group(3)
        if kind == "Command sent":
            pending = (t, body.strip())
        elif pending and ((kind == "Returned" and pending[1] != "$H")
                          or (kind == "Homing completed" and pending[1] == "$H")):
            rows.append((pending[1], (t - pending[0]).total_seconds()))
            pending = None
    g01 = [d for c, d in rows if c.startswith("G01")]
    homes = [d for c, d in rows if c == "$H"]
    feeds = sorted({c.split("F")[-1] for c, _ in rows if c.startswith("G01") and "F" in c})
    return {"g01_count": len(g01), "g01_total_s": round(sum(g01), 1),
            "g01_median_s": round(statistics.median(g01), 3) if g01 else None,
            "g01_min_s": round(min(g01), 3) if g01 else None,
            "home_s": [round(h, 1) for h in homes], "feeds": feeds}


def summarize(a, out: Out, rec: dict, r: dict | None, status: str, err: str = "") -> str:
    def jl(name):
        p = out.dir / name
        return json.loads(p.read_text()) if p.exists() else []
    steps, trace = jl("step_trace.json"), jl("plunger_trace.json")
    log = (out.dir / "run_hardware.log").read_text(errors="replace") if (out.dir / "run_hardware.log").exists() else ""
    m = re.search(r"Protocol complete — (\d+) steps", log)
    m2 = re.search(r"Protocol did not complete — (\d+) steps", log)
    errs = re.findall(r"ERROR during execution: (.*)", log)
    timing = parse_gcode_timing(out.dir / "gantry_mill_control.log")
    rec["gcode"] = timing
    proto_s = sum(s["dt_s"] for s in steps) if steps else None
    total_steps = (rec.get("protocol") or {}).get("steps")
    if m:
        headline = f"✅ **{m.group(1)}/{total_steps} steps, protocol complete**"
    elif m2 or errs:
        headline = (f"❌ **stopped after {m2.group(1) if m2 else '?'}/{total_steps} steps**"
                    + (f": `{errs[0][:160]}`" if errs else ""))
    elif status.startswith("checks only"):
        headline = f"✅ **{status}**"
    else:
        headline = f"⛔ **{status}**" + (f": {err}" if err else "")
    L = [f"# {a.name}", "", headline, ""]
    if r:
        L += [f"- **When:** {r['t_start']:%Y-%m-%d %H:%M:%S}Z → {r['t_end']:%H:%M:%S}Z "
              f"({lab(r['t_start'])}–{lab(r['t_end'])} lab), "
              f"**{(r['t_end'] - r['t_start']).total_seconds():.0f} s** wall, run process start to end"
              + (f"; steps themselves {proto_s:.0f} s" if proto_s else "")]
    v = rec.get("byu_vcl", {}), rec.get("cubos", {})
    L += [f"- **Code:** byu-vcl `{v[0].get('commit')}`"
          + (" (configs modified!)" if v[0].get("configs_dirty") else "")
          + f" · CubOS `{v[1].get('commit')}` + {', '.join('`' + p.removesuffix('.patch') + '`' for p in v[1].get('patches_applied', []))}"]
    gr = rec.get("grbl") or {}
    if gr:
        L += [f"- **GRBL:** travel {gr.get('max_travel')}, G54 {gr.get('g54')}, `$20={num(gr.get('soft_limits'))}` "
              f"`$21={num(gr.get('hard_limits'))}`, feed F{num(gr.get('feed_mm_min'))}"]
    if timing:
        L += [f"- **G-code:** {timing['g01_count']} `G01` in {timing['g01_total_s']} s "
              f"(median {timing['g01_median_s']} s, shortest {timing['g01_min_s']} s), "
              f"F {', '.join(timing['feeds'])}; `$H` {timing['home_s']} s"]
    tr = (r or {}).get("tic_rows") or []
    if tr:
        vins = [float(x["vin"]) for x in tr if x.get("vin")]
        errs_t = sorted({x["stopping"] for x in tr if x.get("stopping") not in (None, "None")})
        L += [f"- **Tic during run:** {len(tr)} polls, VIN {min(vins):.1f}–{max(vins):.1f} V, "
              f"stopping errors: {', '.join(errs_t) or 'none'}"]
    if r:
        kern = (out.dir / "kernel_during_run.log").read_text(errors="replace")
        usb = [ln for ln in kern.splitlines() if re.search(r"usb|over-current", ln, re.I)]
        L += [f"- **Kernel:** {len(usb)} USB line(s) during the run"
              + (f" — first: `{usb[0][:120]}`" if usb else "")]
    hc = rec.get("home_check")
    if hc:
        L += [f"- **Plunger HOME check:** ended at {hc['firmware_end_mm']} mm by the firmware; "
              f"HOME took {hc['home_dt_s']} s ⇒ {hc['implied_mm']} mm (**{hc['lost_mm']:+.2f} mm**)"]
    if steps:
        L += ["", "| step | command | s |", "|---:|---|---:|"]
        L += [f"| {s['index']} | {s['command']}{'' if s['ok'] else ' ❌'} | {s['dt_s']:.1f} |" for s in steps]
    if trace:
        L += ["", "| plunger (UTC) | command | args | s | reply |", "|---|---|---|---:|---|"]
        for t in trace:
            rep = (t.get("reply") or t.get("error") or "")[:60].replace("|", "/")
            L += [f"| {t['t'][11:19]} | {PLUNGER.get(t['code'], t['code'])} | "
                  f"{', '.join(x.strip(chr(39)) for x in t['args'])} | {t['dt_s']:.2f} | `{rep}` |"]
    if a.baseline and Path(a.baseline, "summary.json").exists():
        b = json.loads(Path(a.baseline, "summary.json").read_text())
        L += ["", f"Baseline `{Path(a.baseline).name}`: wall {b.get('wall_s')} s, "
              f"G01 total {(b.get('gcode') or {}).get('g01_total_s')} s"]
    L += ["", "Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, "
          "`step_trace.json`, `plunger_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`."]
    text = "\n".join(L) + "\n"
    out.write("SUMMARY.md", text)
    rec["status"] = status
    rec["wall_s"] = round((r["t_end"] - r["t_start"]).total_seconds(), 1) if r else None
    rec["steps_s"] = round(proto_s, 1) if proto_s else None
    rec["steps"] = steps
    out.write("summary.json", json.dumps(rec, indent=2, default=str))
    return text


# ----------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="results folder name, ~/cubxl_runs/<name>/")
    ap.add_argument("--gantry", type=Path, default=DEFAULT_GANTRY)
    ap.add_argument("--deck", type=Path, default=DEFAULT_DECK)
    ap.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    ap.add_argument("--cubos", type=Path, default=Path.home() / "CubOS")
    ap.add_argument("--outdir", type=Path, default=None, help="default ~/cubxl_runs/<name>")
    ap.add_argument("--frames-at", default="2,4,8,9", help="steps to photograph after")
    ap.add_argument("--no-camera", action="store_true")
    ap.add_argument("--no-tic", action="store_true", help="no pipette Tic on this machine")
    ap.add_argument("--home-check", action="store_true",
                    help="plunger HOME after the run; its duration checks for lost steps")
    ap.add_argument("--keep-energized", action="store_true", help="leave the Tic energized after")
    ap.add_argument("--checks-only", action="store_true", help="stages 1-2 only; nothing moves")
    ap.add_argument("--allow-no-home", action="store_true")
    ap.add_argument("--baseline", default=None, help="an earlier results folder to compare with")
    a = ap.parse_args()
    for k in ("gantry", "deck", "protocol"):
        setattr(a, k, getattr(a, k).resolve())
    outdir = (a.outdir or Path.home() / "cubxl_runs" / a.name).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)   # an SSH drop must not kill a run
    out = Out(outdir)
    rec: dict = {"name": a.name, "argv": sys.argv[1:], "outdir": str(outdir)}
    sys.path.insert(0, str(a.cubos / "packages/core/src"))
    out.say(f"== {a.name}: {a.gantry.name} | {a.deck.name} | {a.protocol.name}")
    cfg = outdir / "configs"
    cfg.mkdir(exist_ok=True)
    for p in (a.gantry, a.deck, a.protocol):
        shutil.copy2(p, cfg / p.name)
    r, status, err, rc = None, "refused", "", 2
    tic_energized = False
    try:
        out.say("-- 1. checks")
        check_versions(a, out, rec)
        g = load_yaml(a.gantry)
        ports = check_ports(a, g, out, rec)
        check_protocol_starts_with_home(a, out, rec)
        check_grbl(a, g, out, rec)
        ard_port = (ports.get("pipette") or ports.get("vial_capper_decapper") or {}).get("port")
        if ard_port:
            cmds = [("STATUS", 14, 10), ("cap sensor", 7, 10), ("EMAG_OFF", 6, 10)]
            out.say("Arduino:")
            rows = arduino(a, ard_port, out, cmds, "before")
            rec["arduino_before"] = rows
            bad = [x for x in rows[1:] if not str(x["reply"]).startswith("OK")]
            cap = next((x for x in rows if x["cmd"] == "cap sensor"), {})
            if bad:
                raise Refused(f"Arduino: {bad[0]['cmd']} replied {bad[0]['reply']}")
            if '"value1":0' not in str(cap.get("reply", "")).replace(" ", ""):
                raise Refused(f"cap sensor reads {cap.get('reply')}: something is held on the head")
        out.say("-- 2. gates")
        gates(a, out, rec)
        if not a.no_tic:
            check_tic(a, out, rec)
            tic_energized = True
        (outdir / "checks.json").write_text(json.dumps(rec, indent=2, default=str))
        if a.checks_only:
            status, rc = "checks only: all passed, nothing run", 0
            if tic_energized:
                tic("--deenergize")
            return rc
        out.say("-- 3. run")
        r = run(a, out, rec)
        trace = json.loads((outdir / "plunger_trace.json").read_text()) \
            if (outdir / "plunger_trace.json").exists() else []
        out.say("-- 4. post-run")
        post_run(a, ports, out, rec, trace)
        tic_energized = False
        log = (outdir / "run_hardware.log").read_text(errors="replace")
        ok = "Protocol complete" in log
        status, rc = ("completed", 0) if ok else ("failed", 1)
        return rc
    except Refused as e:
        status, err, rc = "refused before any motion", str(e), 2
        out.say(f"REFUSED: {e}")
        return rc
    except Exception as e:                                   # noqa: BLE001
        import traceback
        status, err, rc = "runner error", repr(e), 3
        out.say("RUNNER ERROR:\n" + traceback.format_exc())
        return rc
    finally:
        if tic_energized and not a.keep_energized:
            tic("--deenergize")
            out.say("Tic de-energized")
        try:
            text = summarize(a, out, rec, r, status, err)
            out.say("-- 5. summary\n" + text)
        except Exception as e:                               # noqa: BLE001
            out.say(f"summary failed: {e!r}")


if __name__ == "__main__":
    sys.exit(main())
