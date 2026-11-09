#!/usr/bin/env python3
"""Watch an A1 mini print from Studio's Device page with no camera (2026-11-06).

    python watch_a1mini_nocam.py MINUTES OUTDIR

A copy of bambu/studio/watch_studio.py (PR #234's branch) for a printer whose camera sends nothing:
the blank-camera stop is dropped, the job panel is read where it sits when the live view is not
playing (y 815-925), and a crop of the job panel and temperatures is saved on every layer change
instead of a camera frame. Limits for PETG: nozzle over 280 C before layer 1 (the A1 mini's start
G-code flushes PETG at about 270 C) or over 260 C from layer 1, bed over 80 C. Only reads the
screen; never clicks. Exit 0 finished, 10 time budget used, 20 needs a decision.
"""
import json, os, re, subprocess, sys, time
from PIL import Image, ImageOps

MINUTES, OUT = float(sys.argv[1]), sys.argv[2]
os.makedirs(f"{OUT}/panels", exist_ok=True)
ENV = dict(os.environ, DISPLAY=":99")
REG = {"noz": (1340, 158, 1480, 192), "bed": (1340, 208, 1480, 246), "job": (420, 815, 1300, 925)}
PANEL = (274, 760, 1298, 990)
TEMPS = (1316, 140, 1470, 260)

def ocr(img, box, psm=6):
    c = img.crop(box)
    c = ImageOps.grayscale(c).resize((c.width * 3, c.height * 3))
    c = c.point(lambda v: 255 if v > 150 else 0)
    p = os.path.join(OUT, "ocr_tmp.png"); c.save(p)
    return subprocess.run(["tesseract", p, "-", "--psm", str(psm)], capture_output=True, text=True).stdout.strip()

def temps(s):
    m = re.search(r"(\d{1,3})\s*/\s*(\d{1,3})", s) or re.search(r"(\d{1,3})\D+(\d{1,3})", s)
    return [int(m.group(1)), int(m.group(2))] if m else None

def windows():
    out = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, env=ENV).stdout
    return sorted(l.split(None, 3)[-1] for l in out.splitlines() if l.strip())

base_windows = windows()
t0, last_layer, last_layer_t, saw_print, fin_count = time.time(), None, time.time(), False, 0
log = open(f"{OUT}/monitor.jsonl", "a")
code, why = 10, "time budget used"
while time.time() - t0 < MINUTES * 60:
    now = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    full = os.path.join(OUT, "screen.png")
    subprocess.run(["import", "-window", "root", full], env=ENV)
    img = Image.open(full).convert("RGB")
    rec = {"utc": now, "noz": temps(ocr(img, REG["noz"], 7)), "bed": temps(ocr(img, REG["bed"], 7))}
    job = re.sub(r"\s+", " ", ocr(img, REG["job"]))
    rec["job"] = job
    m = re.search(r"Layer[:;.,]?\s*(\d+)\s*/\s*(\d+)", job); rec["layer"] = [int(m.group(1)), int(m.group(2))] if m else None
    m = re.search(r"(\d{1,3})\s*%", job); rec["percent"] = int(m.group(1)) if m else None
    w = windows(); new = [x for x in w if x not in base_windows]; rec["new_windows"] = new
    log.write(json.dumps(rec) + "\n"); log.flush()
    if rec["layer"] and rec["layer"][0] > 0:
        saw_print = True
    if rec["layer"] != last_layer:
        L = rec["layer"][0] if rec["layer"] else "x"
        img.crop(PANEL).save(f"{OUT}/panels/{now}_L{L}.png")
        last_layer, last_layer_t = rec["layer"], time.time()
        print(f"{now} L={rec['layer']} {rec['percent']}% noz={rec['noz']} bed={rec['bed']} | {job[:100]}", flush=True)
    if new:
        img.save(f"{OUT}/dialog_{now}.png"); code, why = 20, f"new window(s): {new}"; break
    noz_hi = 260 if saw_print else 280
    if rec["noz"] and rec["noz"][0] > noz_hi:
        img.save(f"{OUT}/limit_{now}.png"); code, why = 20, f"hard limit: nozzle {rec['noz']} > {noz_hi}"; break
    if rec["bed"] and rec["bed"][0] > 80:
        img.save(f"{OUT}/limit_{now}.png"); code, why = 20, f"hard limit: bed {rec['bed']} > 80"; break
    if saw_print and rec["percent"] == 100 and re.search(r"Finish", job):
        fin_count += 1
        if fin_count >= 2:
            img.save(f"{OUT}/finished_{now}.png"); img.crop(PANEL).save(f"{OUT}/panels/{now}_finished.png")
            code, why = 0, "job shows 100 % and Finished"; break
    else:
        fin_count = 0
    if saw_print and time.time() - last_layer_t > 15 * 60:
        code, why = 20, "layer unchanged for 15 min"; break
    time.sleep(10)
print("EXIT", code, why, flush=True)
sys.exit(code)
