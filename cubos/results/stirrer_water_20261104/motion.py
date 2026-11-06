"""Did anything move? Frame-to-frame change over the vial in camera 1's video.

usage: motion.py <label>     (reads <label>.mjpeg, <label>_pts.txt, <label>_camera.json
                              and <label>.jsonl; writes <label>_motion.csv and motion.png)

For each frame, the mean absolute difference (0-255 grey levels) from the previous frame
and from the first frame, inside VIAL (all of the vial camera 1 sees: the glass and water
above the cup, and the cup's far finger through them) and inside STILL (a patch of deck
with nothing on it, which gives the camera's own noise). The bar itself is down in the cup,
out of sight, but a bar turning would move the water and whatever is seen through it, and
a twitch at a kick would show up as a spike.
"""
import csv, json, sys
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

label = sys.argv[1]
VIAL = (0, 150, 440, 368)      # x0, y0, x1, y1 in the 864 x 368 frame
STILL = (100, 20, 200, 90)     # deck plate, top left


def secs(hms):
    h, m, s = hms.rstrip("Z").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


t0 = secs(json.load(open(f"{label}_camera.json"))["first_bytes_utc"])
pts = [float(l) for l in open(f"{label}_pts.txt") if l.strip() and not l.startswith("#")]
data = open(f"{label}.mjpeg", "rb").read()
rows, prev, first, i, k = [], {}, {}, 0, 0
while True:
    a = data.find(b"\xff\xd8", i)
    b = data.find(b"\xff\xd9", a + 2) if a >= 0 else -1
    if b < 0:
        break
    i = b + 2
    g = cv2.imdecode(np.frombuffer(data[a:i], np.uint8), cv2.IMREAD_GRAYSCALE).astype(np.float32)
    row = {"frame": k, "utc_s": round(t0 + pts[k] / 1000, 3)}
    for name, (x0, y0, x1, y1) in (("vial", VIAL), ("still", STILL)):
        p = g[y0:y1, x0:x1]
        row[f"{name}_vs_prev"] = round(float(np.abs(p - prev[name]).mean()), 3) if name in prev else 0.0
        first.setdefault(name, p)
        row[f"{name}_vs_first"] = round(float(np.abs(p - first[name]).mean()), 3)
        prev[name] = p
    rows.append(row)
    k += 1

with open(f"{label}_motion.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

steps = [json.loads(l) for l in open(f"{label}.jsonl")]
starts = [(secs(r["utc"]) - t0, r["cmd"].split(",")[1]) for r in steps if r.get("event") == "step"]
stop = [secs(r["utc"]) - t0 for r in steps if r.get("event") == "stop"]
t = np.array([r["utc_s"] - t0 for r in rows])
fig, ax = plt.subplots(figsize=(11, 3.6))
for name, colour in (("vial", "#d1495b"), ("still", "#7a7a7a")):
    ax.plot(t, [r[f"{name}_vs_prev"] for r in rows], lw=0.8, color=colour,
            label={"vial": "vial and water", "still": "bare deck (camera noise)"}[name] + ", change from the previous frame")
for s, rpm in starts:
    ax.axvline(s, color="#00798c", lw=0.8, ls="--")
    ax.text(s + 1, ax.get_ylim()[1] * 0.92, f"{rpm} rpm", color="#00798c", fontsize=8)
for s in stop:
    ax.axvline(s, color="black", lw=0.8, ls=":")
ax.set_xlabel("s since the camera started (23:19:13.94 UTC)")
ax.set_ylabel("mean |difference|, grey levels")
ax.set_title("Camera 1, 2026-11-04: the vial changes no more than bare deck does, through all six steps", fontsize=10)
ax.legend(loc="lower right", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig("motion.png", dpi=130)
vial = np.array([r["vial_vs_prev"] for r in rows[1:]])
still = np.array([r["still_vs_prev"] for r in rows[1:]])
print(f"frames {len(rows)}; vial vs prev: median {np.median(vial):.3f}, p99 {np.percentile(vial, 99):.3f}, "
      f"max {vial.max():.3f} (frame {int(vial.argmax()) + 1}); still vs prev: median {np.median(still):.3f}, "
      f"p99 {np.percentile(still, 99):.3f}, max {still.max():.3f}")
print(f"vial vs first frame: max {max(r['vial_vs_first'] for r in rows):.3f}; "
      f"still vs first: max {max(r['still_vs_first'] for r in rows):.3f}")
