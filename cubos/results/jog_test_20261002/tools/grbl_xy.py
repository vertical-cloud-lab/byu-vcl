#!/usr/bin/env python3
"""Hold the CubXL's GRBL port open and run X/Y-only jogs, one request at a time.

Written for #165 on 2026-10-02: Ben asked for -200 X, -200 Y, +175 X with
pictures in between, then home, and NO Z motion at all. Two constraints shape
this file:

* Opening the port resets the GRBL board (DTR), which zeroes its counter and
  re-locks it. So the port is opened once and held, and requests arrive as lines
  appended to cmds.txt, letting pictures be checked between moves.
* Z is never sent. Any request naming another axis is refused, and every status
  report is checked for an unchanged Z; a change halts motion.

Requests (one per line, "<id> <verb> ..."): status | unlock | jog X|Y <mm> | quit.
Each prints "DONE <id>" or "FAIL <id>" to grbl.log.
"""
import datetime, json, os, re, sys, time
import serial

PORT = "/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0"
OUT = "/tmp/jog_20261002"
CMDS, LOG = OUT + "/cmds.txt", OUT + "/grbl.log"
FEED = 1000            # mm/min, a third of what protocols use
MAX_JOG = 250.0        # mm, refuse anything longer
IDLE_EXIT_S = 1800     # close the port if no request arrives for 30 min
EXPECT = {"$3": 1, "$10": 0, "$20": 1, "$21": 1, "$22": 1, "$23": 0, "$27": 3.0,
          "$100": 400.0, "$101": 400.0, "$102": 400.0,
          "$130": 364.0, "$131": 281.0, "$132": 125.0}
EXPECT_G54 = (-364.0, -281.0, -125.0)   # cub_xl_ben_3_instrument.yaml, 2026-10-02

def log(msg):
    line = f"{datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S.%f')[:-3]}Z {msg}"
    with open(LOG, "a") as f:
        f.write(line + "\n")

s = None
halted = None          # reason string once motion is no longer allowed
z_ref = None           # Z as first reported; must never change

def read_for(seconds, until=None):
    buf, t0 = b"", time.time()
    while time.time() - t0 < seconds:
        buf += s.read(4096)
        if until and until(buf):
            break
    return buf.decode(errors="replace")

def send(line, wait=5.0):
    s.reset_input_buffer()
    s.write((line + "\n").encode())
    out = read_for(wait, lambda b: b"ok" in b or b"error:" in b or b"ALARM:" in b)
    log(f"> {line}  <  {out.strip()!r}")
    return out

def status():
    s.reset_input_buffer()
    s.write(b"?")
    out = read_for(1.5, lambda b: b">" in b)
    m = re.search(r"<([^|>]+)\|[MW]Pos:([-\d.]+),([-\d.]+),([-\d.]+)([^>]*)>", out)
    if not m:
        return None, None, out.strip()
    return m.group(1), tuple(float(m.group(i)) for i in (2, 3, 4)), out.strip()

def check_z(pos, raw):
    global halted
    if pos is not None and z_ref is not None and abs(pos[2] - z_ref) > 0.0005:
        s.write(b"\x85"); s.write(b"!")    # jog cancel + feed hold
        halted = f"Z changed: {z_ref} -> {pos[2]} ({raw})"
        log("HALT " + halted)
        return False
    return True

def jog(axis, mm):
    global halted
    if halted:
        return False, "halted: " + halted
    if axis not in ("X", "Y"):
        return False, f"refused: axis {axis!r} (X and Y only)"
    if not (0 < abs(mm) <= MAX_JOG):
        return False, f"refused: {mm} mm"
    st0, p0, raw0 = status()
    log(f"before: {raw0}")
    if st0 != "Idle" or p0 is None:
        return False, f"not Idle before jog: {raw0}"
    if not check_z(p0, raw0):
        return False, halted
    out = send(f"$J=G91 G21 {axis}{mm:.3f} F{FEED}")
    if "ok" not in out:
        return False, f"jog not accepted: {out.strip()!r}"
    deadline = time.time() + abs(mm) / FEED * 60 + 15
    seen_motion, last = False, None
    while time.time() < deadline:
        time.sleep(0.25)
        st, p, raw = status()
        if p is not None and p != last:
            log(f"  {raw}")
            last = p
        if not check_z(p, raw):
            return False, halted
        if st and st.startswith(("Alarm", "Hold", "Door")):
            halted = f"state {st}: {raw}"
            log("HALT " + halted)
            return False, halted
        if st in ("Jog", "Run"):
            seen_motion = True
        if st == "Idle" and (seen_motion or (p and p != p0)):
            break
    else:
        s.write(b"\x85")
        halted = "jog did not finish in time"
        log("HALT " + halted)
        return False, halted
    st, p, raw = status()
    log(f"after: {raw}")
    i = "XY".index(axis)
    want = list(p0); want[i] += mm
    err = max(abs(a - b) for a, b in zip(p, want))
    if err > 0.002:
        halted = f"ended at {p}, expected {tuple(want)}"
        log("HALT " + halted)
        return False, halted
    return True, f"{axis}{mm:+.3f} done: {p0} -> {p} (Z unchanged)"

def main():
    global s, halted, z_ref
    os.makedirs(OUT, exist_ok=True)
    open(CMDS, "a").close()
    log(f"opening {PORT} (this resets the GRBL board)")
    s = serial.Serial(PORT, 115200, timeout=0.1)
    banner = read_for(2.5)
    log(f"banner: {banner.strip()!r}")
    snap = {"t_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "banner": banner}
    snap["build"] = send("$I")
    dd = send("$$", wait=4)
    snap["settings"] = dict(re.findall(r"^(\$\d+)=([-\d.]+)", dd, re.M))
    snap["offsets"] = send("$#", wait=4)
    st, p, raw = status()
    snap["status"] = raw
    json.dump(snap, open(OUT + "/grbl_before.json", "w"), indent=2)
    got = snap["settings"]
    bad = [k for k, v in EXPECT.items()
           if k not in got or abs(float(got[k]) - v) > 0.001]
    g54 = re.search(r"\[G54:([-\d.]+),([-\d.]+),([-\d.]+)\]", snap["offsets"])
    if bad:
        halted = f"settings differ from the gantry file: {bad}"
    elif not g54 or any(abs(float(a) - b) > 0.001 for a, b in zip(g54.groups(), EXPECT_G54)):
        halted = f"G54 differs: {g54.groups() if g54 else None}"
    log(f"state {st}, pos {p}; settings check: {'FAILED ' + halted if halted else 'ok'}")
    z_ref = p[2] if p else None
    done, last_t = 0, time.time()
    while True:
        lines = open(CMDS).read().splitlines()
        if len(lines) <= done:
            if time.time() - last_t > IDLE_EXIT_S:
                log("idle timeout, closing port"); break
            time.sleep(0.2); continue
        line = lines[done].strip(); done += 1; last_t = time.time()
        parts = line.split()
        if len(parts) < 2:
            continue
        cid, verb, args = parts[0], parts[1], parts[2:]
        log(f"request {cid}: {' '.join(parts[1:])}")
        ok, msg = False, "unknown request"
        try:
            if verb == "status":
                st, p, raw = status(); ok, msg = True, raw
            elif verb == "unlock":
                if halted:
                    ok, msg = False, "halted: " + halted
                else:
                    out = send("$X"); ok, msg = "ok" in out, out.strip()
                    st, p, raw = status()
                    if p is not None and z_ref is None:
                        z_ref = p[2]
                    msg += " | " + raw
            elif verb == "jog" and len(args) == 2:
                ok, msg = jog(args[0].upper(), float(args[1]))
            elif verb == "quit":
                log(f"DONE {cid} quit"); break
        except Exception as e:
            ok, msg = False, f"exception {e!r}"
        log(f"{'DONE' if ok else 'FAIL'} {cid} {msg}")
    s.close()
    log("port closed")

if __name__ == "__main__":
    main()
