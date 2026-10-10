"""Watch a print through Bambu Studio's Device page, for when the LAN route is shut.

    python watch_studio.py MINUTES FRAME_EVERY_S OUTDIR

Written for the H2D on 2026-10-08, when the printer refused H2D_ACCESS_CODE over LAN
(../README.md, section 11). Studio must be maximised on :99 (1920x1080), on the Device page,
with the printer selected and the camera playing; the screen regions below assume that layout.
Every 10 s: screenshot :99, OCR the temperatures and the job panel, log a JSON line.
Every FRAME_EVERY_S: save the camera pane as a JPEG named by time and layer.
Exit 0: the job panel shows 100 % and its "Printing" label has gone, after printing was seen.
Not the word "Finished": Studio puts it in place of "Estimated finish time" as soon as the
remaining time reaches 0 min, which on 2026-10-08 was at layer 21 of 28, 70 s before the
H2D finished. (Matching "finish" ended the first run at layer 1.) This rule was checked
against that day's recording, not yet live.
Exit 10: time budget used.  Exit 20: needs a decision (a new dialog window, a nozzle over
260 or bed over 80 degC, the layer unchanged for 15 min, the camera pane blank for 3 min).
Targets other than the file's 220/55 are only noted. Only reads the screen; never clicks.
"""
import json, os, re, subprocess, sys, time
from PIL import Image, ImageOps, ImageStat

MINUTES, FRAME_EVERY, OUT = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
os.makedirs(f"{OUT}/frames", exist_ok=True)
ENV = dict(os.environ, DISPLAY=":99")
REG = {"nozL": (1368, 158, 1480, 192), "nozR": (1368, 208, 1480, 242), "bed": (1350, 262, 1480, 292),
       "chamber": (1350, 317, 1480, 347), "job": (420, 895, 1300, 1012)}
CAM = (274, 136, 1298, 794)

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
t0, last_frame, last_layer, last_layer_t, saw_print, dead_since = time.time(), 0, None, time.time(), False, None
log = open(f"{OUT}/monitor.jsonl", "a")
code, why = 10, "time budget used"
while time.time() - t0 < MINUTES * 60:
    now = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    full = os.path.join(OUT, "screen.png")
    subprocess.run(["import", "-window", "root", full], env=ENV)
    img = Image.open(full).convert("RGB")
    rec = {"utc": now}
    for k in ("nozL", "nozR", "bed", "chamber"):
        rec[k] = temps(ocr(img, REG[k], 7))
    job = re.sub(r"\s+", " ", ocr(img, REG["job"]))
    rec["job"] = job
    m = re.search(r"Layer[:;]?\s*(\d+)\s*/\s*(\d+)", job); rec["layer"] = [int(m.group(1)), int(m.group(2))] if m else None
    m = re.search(r"(\d{1,3})\s*%", job); rec["percent"] = int(m.group(1)) if m else None
    cam = img.crop(CAM); st = ImageStat.Stat(ImageOps.grayscale(cam))
    rec["cam_luma"], rec["cam_std"] = round(st.mean[0], 1), round(st.stddev[0], 1)
    w = windows(); new = [x for x in w if x not in base_windows]
    rec["new_windows"] = new
    log.write(json.dumps(rec) + "\n"); log.flush()
    if rec["layer"] and rec["layer"][0] > 0:
        saw_print = True
    if rec["layer"] != last_layer:
        last_layer, last_layer_t = rec["layer"], time.time()
    if time.time() - last_frame >= FRAME_EVERY:
        L = rec["layer"][0] if rec["layer"] else "x"
        cam.save(f"{OUT}/frames/{now}_L{L}.jpg", quality=88); last_frame = time.time()
        print(f"{now} L={rec['layer']} {rec['percent']}% nozL={rec['nozL']} bed={rec['bed']} ch={rec['chamber']} cam={rec['cam_luma']}/{rec['cam_std']} | {job[:90]}", flush=True)
    # decisions
    if new:
        img.save(f"{OUT}/dialog_{now}.png"); code, why = 20, f"new window(s): {new}"; break
    for k, hi in (("nozL", 260), ("nozR", 260), ("bed", 80)):
        if rec[k] and (rec[k][0] > hi or rec[k][1] > hi):
            code, why = 20, f"hard limit: {k}={rec[k]}"; break
    if code == 20:
        break
    if saw_print and rec["layer"] and rec["layer"][0] >= 2:
        if rec["nozL"] and rec["nozL"][1] not in (0, 220) and rec["nozL"][1] < 260:
            print(f"{now} note: left nozzle target {rec['nozL'][1]} (file says 220)", flush=True)
        if rec["bed"] and rec["bed"][1] not in (0, 55):
            print(f"{now} note: bed target {rec['bed'][1]} (file says 55)", flush=True)
    if saw_print and rec["percent"] == 100 and not re.search(r"Pr\w{0,2}nt\w{0,3}g", job):  # OCR gives "Printng" too
        img.save(f"{OUT}/finished_{now}.png"); cam.save(f"{OUT}/frames/{now}_finished.jpg", quality=90)
        code, why = 0, "job shows finished"; break
    if saw_print and time.time() - last_layer_t > 15 * 60:
        code, why = 20, "layer unchanged for 15 min"; break
    if rec["cam_std"] < 4:
        dead_since = dead_since or time.time()
        if time.time() - dead_since > 180:
            code, why = 20, "camera pane blank for 3 min"; break
    else:
        dead_since = None
    time.sleep(10)
print("EXIT", code, why, flush=True)
sys.exit(code)
