#!/usr/bin/env python3
"""The 2026-10-23 back-focus sweep: one lid-camera still per whole turn of the knurled ring.

    python back_focus_sweep.py

@timothy-commins started with the knurled back-focus ring all the way out (down, away from the
deck) and turned it up one whole turn at a time, 5.5 turns to the top, with the focus thumbscrew
near NEAR throughout. After each turn he posted the turn number on PR #234 and a still was taken
while the stream ran. The stills are in frames/2026-10-23/back_focus_sweep/ (1600 x 1200 copies of
the 4056 x 3040 originals).

Two measurements per still, both made on the paint-filled wells, which are uniform discs:

sharpness  colour contrast of the red and yellow wells (peak of the paint map above its median),
           as a percentage of the grey plate's brightness. Once the blur spot is bigger than a
           well, the well's colour is spread over the spot, so the peak falls roughly as
           (well area / spot area). Dividing by the plate's brightness cancels the auto-exposure.
skew       vertical skewness of each well's core (above 30 % of its peak). The iris makes the blur
           spot a rounded triangle; negative skew is apex up, as at 18:08 (ring all the way in),
           where the picture forms behind the sensor. Only meaningful while the wells are still
           apart (turns 0-2); after that neighbouring wells run together.

Writes frames/2026-10-23/back_focus_sweep.json and back_focus_sweep.png.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = Path(__file__).resolve().parent
OUT = HERE / "frames/2026-10-23"
SWEEP = OUT / "back_focus_sweep"

# turn, still, taken (UTC), Tim's comment (UTC)
TURNS = [
    (0.0, "turn00_2016Z.jpg", "20:16:44", "20:14:02 (the request)"),
    (1.0, "turn01_2019Z.jpg", "20:19:47", "20:18:53"),
    (2.0, "turn02_2021Z.jpg", "20:21:50", "20:20:36"),
    (3.0, "turn03_2022Z.jpg", "20:22:33", "20:22:33"),
    (4.0, "turn04_2023Z.jpg", "20:23:44", "20:23:43"),
    (5.0, "turn05_2026Z.jpg", "20:26:07", "20:26:06"),
    (5.5, "turn05.5_top_2028Z.jpg", "20:28:00", "20:27:59 ('all the way up is 5.5')"),
]
# picam_source.py /status at each still (exposure in us); none was saved for turn 0
CAMERA = {
    1.0: (49963, 3.39, 46.9), 2.0: (49963, 2.92, 56.0), 3.0: (49963, 2.53, 64.0),
    4.0: (49963, 2.29, 71.6), 5.0: (48940, 2.00, 83.0), 5.5: (49963, 2.09, 78.3),
}
COLOUR_GAINS = [3.083, 1.486]   # unchanged to 0.1 % through the sweep, so the colour maps compare
REFERENCE = {   # same measurement on the earlier stills of the day (narrower iris, see README)
    "18:08": ("still_1808Z_focus_at_near.jpg", "ring all the way in, focus thumbscrew at NEAR"),
    "19:04": ("still_1904Z_ring_all_the_way_out.jpg", "ring all the way out, focus thumbscrew at NEAR"),
}
EXPOSURE_1854 = (66654, 15.52)  # still_1854Z.json, rail lights on then as now

BLUE, INK, INK2, GRID = "#2a78d6", "#0b0b0b", "#52514e", "#e4e3df"


def peaks(m: np.ndarray, n: int = 2, sig: float = 6, min_dist: int = 60):
    s = ndi.gaussian_filter(m, sig)
    bg = np.median(s)
    mx = ndi.maximum_filter(s, size=2 * min_dist + 1)
    ys, xs = np.nonzero((s == mx) & (s > bg + 0.4 * (s.max() - bg)))
    out = []
    for i in np.argsort(s[ys, xs])[::-1]:
        if all(np.hypot(xs[i] - x, ys[i] - y) >= min_dist for x, y, _ in out):
            out.append((int(xs[i]), int(ys[i]), float(s[ys[i], xs[i]] - bg)))
        if len(out) == n:
            break
    return out, s, bg


def core_skew(s, bg, x, y, others, frac=0.3) -> float:
    near = min([np.hypot(x - ox, y - oy) for ox, oy in others] + [300])
    w_ = int(max(20, 0.5 * near))
    y0, y1, x0, x1 = max(0, y - w_), min(s.shape[0], y + w_), max(0, x - w_), min(s.shape[1], x + w_)
    v = s[y0:y1, x0:x1] - bg
    yy, xx = np.mgrid[y0:y1, x0:x1]
    w = np.where((v > frac * (s[y, x] - bg)) & (np.hypot(xx - x, yy - y) <= w_), v, 0)
    my = (w * yy).sum() / w.sum()
    vy = (w * (yy - my) ** 2).sum() / w.sum()
    return float((w * (yy - my) ** 3).sum() / w.sum() / vy ** 1.5)


def paint_maps(path: Path):
    a = np.asarray(Image.open(path).convert("RGB").resize((1014, 760), Image.BILINEAR)).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return {"red": r - np.maximum(g, b), "yellow": np.minimum(r, g) - b}, (r + g + b) / 3


def measure(path: Path) -> dict:
    maps, lum = paint_maps(path)
    plate = float(np.median(lum[150:380, 250:760]))   # upper middle of the frame is always plate
    found = {k: peaks(m) for k, m in maps.items()}
    allpk = [(x, y) for k in found for x, y, _ in found[k][0]]
    contrast = [found[k][0][0][2] / plate for k in found if found[k][0]]
    skews = []
    for k, (pk, s, bg) in found.items():
        for x, y, _ in pk:
            skews.append(round(core_skew(s, bg, x, y, [p for p in allpk if p != (x, y)]), 3))
    # well pitch from the two red wells, (col c+3, row r) and (col c+1, row r+2): 2 sqrt2 wells apart
    pitch = None
    pk = sorted(found["red"][0], key=lambda q: q[1])
    if len(pk) == 2 and pk[1][0] < pk[0][0]:
        pitch = round(float(np.hypot(pk[0][0] - pk[1][0], pk[0][1] - pk[1][1]) / (2 * np.sqrt(2)) * 4056 / 1014), 1)
    return {"sharpness": round(100 * float(np.mean(contrast)), 1), "plate_brightness": round(plate, 1),
            "well_core_skews": skews, "skew_median": round(float(np.median(skews)), 3),
            "well_pitch_px_full_res": pitch}


def false_colour(path: Path) -> np.ndarray:
    """Red paint in red, yellow paint in yellow, everything else black, stretched per still."""
    maps, _ = paint_maps(path)
    out = np.zeros(maps["red"].shape + (3,))
    for k, rgb in (("red", (1.0, 0.12, 0.08)), ("yellow", (1.0, 0.85, 0.0))):
        m = ndi.gaussian_filter(maps[k], 2)
        lo, hi = np.percentile(m, 50), np.percentile(m, 99.9)
        out += np.clip((m - lo) / (hi - lo), 0, 1)[..., None] * np.array(rgb)
    return np.clip(out, 0, 1)


def main() -> None:
    rows = []
    for turn, name, taken, posted in TURNS:
        m = measure(SWEEP / name)
        if turn > 0:   # blurred triangles bias the peaks, and later the wells run together
            m["well_pitch_px_full_res"] = None
        cam = CAMERA.get(turn)
        rows.append({"turn": turn, "still": f"back_focus_sweep/{name}", "taken_utc": taken, "tim_posted_utc": posted,
                     **m, "camera": None if cam is None else
                     {"exposure_us": cam[0], "analogue_gain": cam[1], "lux": cam[2]}})
        print(turn, name, m["sharpness"], m["skew_median"], m["well_pitch_px_full_res"])
    ref = {t: {**measure(OUT / f), "still": f, "state": what} for t, (f, what) in REFERENCE.items()}

    # spot size ~ 1/sqrt(sharpness) while the spot is bigger than a well; extrapolate turns 0-2 to zero
    t = np.array([r["turn"] for r in rows[:3]])
    d = 1 / np.sqrt([r["sharpness"] for r in rows[:3]])
    slope, icpt = np.polyfit(t, d, 1)
    turns_short = float(icpt / slope)
    mm_per_turn = 9.9 / 5.5
    exp_1854 = EXPOSURE_1854[0] * EXPOSURE_1854[1]
    exp_now = CAMERA[1.0][0] * CAMERA[1.0][1]
    summary = {
        "trend": "sharpest at the start (ring all the way out); every turn up blurrier; the top blurriest",
        "picture_side": "behind the sensor at every ring position: blurrier as the lens moves towards the sensor "
                        "(the picture also shrinks each turn), and the spot points apex up in turns 0-1 as at 18:08",
        "extra_room_needed": {
            "turns_beyond_all_the_way_out": round(turns_short, 1),
            "mm_if_5.5_turns_is_the_whole_9.9_mm_travel": round(turns_short * mm_per_turn, 1),
            "how": "1/sqrt(sharpness), roughly proportional to the spot's diameter while it is bigger than a well, "
                   "fitted over turns 0-2 and extrapolated to zero; rough, several mm either way",
        },
        "exposure_vs_1854": {"exposure_times_gain_1854": exp_1854, "exposure_times_gain_now": exp_now,
                             "ratio": round(exp_1854 / exp_now, 1),
                             "reading": "rail lights on both times, so the iris is wider now; a wider iris makes the "
                                        "same focus error a bigger blur, so compare the sweep's stills with each "
                                        "other, not with 18:08 or 19:04"},
        "colour_gains": COLOUR_GAINS,
    }
    (OUT / "back_focus_sweep.json").write_text(json.dumps(
        {"what": "Lid camera stills, one per whole turn of the knurled back-focus ring, 2026-10-23",
         "request": "https://github.com/vertical-cloud-lab/byu-vcl/pull/234 (timothy-commins, 20:14 UTC)",
         "how": "ssh to the lid camera Pi, curl -s localhost:8081/still while the stream ran; "
                "focus thumbscrew near NEAR throughout (Tim, 20:28 UTC); rail lights on",
         "measured_on": "the committed 1600 x 1200 copies, resized to 1014 x 760",
         "well_pitch_note": "from the two red wells' peaks; given only for the start and the references, since the "
                            "blurred triangles bias the peaks and the wells later run together",
         "turns": rows, "reference": ref, "summary": summary}, indent=1) + "\n")

    fig = plt.figure(figsize=(12, 7.0), facecolor="#fcfcfb")
    gs = fig.add_gridspec(2, 7, height_ratios=[1.3, 1], hspace=0.45, wspace=0.06,
                          left=0.07, right=0.98, top=0.93, bottom=0.11)
    ax = fig.add_subplot(gs[0, :])
    ax.set_facecolor("#fcfcfb")
    xs = [r["turn"] for r in rows]
    ys = [r["sharpness"] for r in rows]
    ax.plot(xs, ys, color=BLUE, lw=2, marker="o", ms=8, mec="#fcfcfb", mew=2, zorder=3)
    for x, y in ((xs[0], ys[0]), (xs[-1], ys[-1])):
        ax.annotate(f"{y:.0f}", (x, y), textcoords="offset points", xytext=(0, 10), ha="center", color=INK, fontsize=10)
    ax.set_xticks(xs, ["0\nall the way out\n(start)", "1", "2", "3", "4", "5", "5.5\ntop"])
    ax.set_xlim(-0.35, 5.85)
    ax.set_ylim(0, 100)
    ax.set_ylabel("sharpness (higher is sharper)", color=INK2)
    ax.set_xlabel("whole turns of the knurled ring, up towards the deck", color=INK2)
    ax.grid(axis="y", color=GRID, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2)
    ax.set_title("Sharpness of the paint wells after each turn: best at the start, worse every turn up",
                 loc="left", color=INK, fontsize=12)
    for i, (r, (turn, name, _, _)) in enumerate(zip(rows, TURNS)):
        a = fig.add_subplot(gs[1, i])
        a.imshow(false_colour(SWEEP / name)[int(0.33 * 760):int(0.95 * 760), :int(0.6 * 1014)])   # the paint wells
        a.set_xticks([]), a.set_yticks([])
        a.set_title(f"turn {turn:g}" + (" (start)" if turn == 0 else " (top)" if turn == 5.5 else ""), fontsize=9.5, color=INK)
    fig.text(0.07, 0.025, "Below: only the red and yellow paint, from the lower left of each still. Each well's blur is a rounded "
             "triangle with its apex up (clearest in turns 0-2,\nbefore the wells run together), as with the ring all the "
             "way in at 18:08: the picture forms behind the sensor, and it gets bigger every turn up.",
             fontsize=9, color=INK2)
    fig.savefig(OUT / "back_focus_sweep.png", dpi=110, facecolor=fig.get_facecolor())
    print("extra turns", round(turns_short, 2), "->", round(turns_short * mm_per_turn, 1), "mm;",
          "exposure ratio", round(exp_1854 / exp_now, 1))
    print("wrote", OUT / "back_focus_sweep.json", "and", OUT / "back_focus_sweep.png")


if __name__ == "__main__":
    main()
