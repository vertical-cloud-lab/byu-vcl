#!/usr/bin/env python3
"""2026-10-14: the board LED with the rail lights off, empty-well backgrounds, and the plate that moved.

Asked on PR #202 by @sgbaird (10-10): read wells empty, dispense, read again and
subtract; and read the black and white wells with the board's LED on and the
rail lights off. One enclosure trip did the empty reads and the LED test. The
paint was never dispensed: lifting off the black well after resting on it
carried the plate up with the enclosure, and it dropped back ~11.5 mm towards
the front, out of its slot.

Reads ``led-background-2026-10-14.json`` (every reading of the trip) and, if
present, two robot-camera photos in ``photos-2026-10-14/``. Writes
``led-background-analysis-2026-10-14.json`` and ``led-background-2026-10-14.png``.

    python3 analyse_led_background.py

Black / white is computed per channel, 410-670 nm, after subtracting what the
sensor reads with no light from outside the enclosure: the sealed board lamp
(``LAMP``, as in ``analyse_paint_accuracy.py``) for the rail-light readings, and
the LED-off reading at the same gain, position and moment for the LED readings.
0 would be a perfect black against a perfect white; 1 means the sensor can't
tell them apart.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "led-background-2026-10-14.json")
OUT = os.path.join(HERE, "led-background-analysis-2026-10-14.json")
PNG = os.path.join(HERE, "led-background-2026-10-14.png")
PHOTOS = os.path.join(HERE, "photos-2026-10-14")
CH = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
NM = [410, 440, 470, 510, 550, 583, 620, 670]
# The board's own green lamp, read sealed in the base with no other light (09-10).
LAMP = np.array([4, 3, 8, 160.5, 168.5, 35, 16, 11.5])


def load():
    with open(DATA) as fh:
        return json.load(fh)


def groups(rows):
    g = defaultdict(list)
    for r in rows:
        g[r["label"]].append(np.array([r["channels"][c] for c in CH], float))
    return {k: np.array(v) for k, v in g.items()}


def spread(a):
    """Largest (max - min) / mean of the total over a group of repeat readings."""
    t = a.sum(1)
    return float((t.max() - t.min()) / t.mean())


def led_ratios(g, where):
    out = {}
    for ma in (4, 10, 20):
        dark = g[f"dark-H7-{where}"].mean(0), g[f"dark-H12-{where}"].mean(0)
        black = g[f"led{ma}-H7-{where}"].mean(0) - dark[0]
        white = g[f"led{ma}-H12-{where}"].mean(0) - dark[1]
        out[ma] = {"black_over_white": (black / white).round(4).tolist(),
                   "total_black_over_white": round(float(black.sum() / white.sum()), 4),
                   "black_total": round(float(black.sum()), 1),
                   "white_total": round(float(white.sum()), 1),
                   "white_minus_black_share_of_white": round(float((white - black).sum()
                                                                   / white.sum()), 4)}
    return out


def rail_ratios(g, black_label, white_label):
    black = g[black_label].mean(0) - LAMP
    white = g[white_label].mean(0) - LAMP
    return {"black_over_white": (black / white).round(4).tolist(),
            "total_black_over_white": round(float(black.sum() / white.sum()), 4),
            "black_total": round(float(g[black_label].mean(0).sum()), 1),
            "white_total": round(float(g[white_label].mean(0).sum()), 1)}


def plate_shift():
    """Where the plate went, from the paint spots in two photos taken with the nozzle away.

    Saturation picks out the paint, the only coloured thing on the plate, so it
    has no repeating pattern to alias on (the well grid aliases by one row:
    phase correlation on the bare grid said ~3 px). The pixel shift becomes deck
    millimetres through the 3x4 camera model fitted on 2026-09-30 to 40 photos
    of the bare nozzle (``paint-plate-2026-09-30.json``), at the plate's top.
    """
    a = os.path.join(PHOTOS, "02_align_hover_z150_robot.jpg")
    b = os.path.join(PHOTOS, "57_homed_robot.jpg")
    if not (os.path.exists(a) and os.path.exists(b)):
        return None
    from PIL import Image
    from scipy import ndimage, optimize

    def sat(p):
        im = np.asarray(Image.open(p).convert("HSV"), dtype=float)
        return ndimage.gaussian_filter(im[..., 1], 1.0)

    A, B = sat(a), sat(b)
    r0, r1, c0, c1 = 235, 285, 140, 275              # the H row's five paint spots
    T = A[r0:r1, c0:c1]
    T = (T - T.mean()) / T.std()

    def score(dy, dx):
        P = ndimage.shift(B, (-dy, -dx), order=3)[r0:r1, c0:c1]
        return float(((P - P.mean()) / P.std() * T).mean())

    coarse = max(((score(dy, dx), dy, dx) for dy in range(-5, 26) for dx in range(-10, 11)))
    fit = optimize.minimize(lambda v: -score(*v), coarse[1:], method="Nelder-Mead",
                            options={"xatol": 0.02, "fatol": 1e-6})
    dy, dx = fit.x
    with open(os.path.join(HERE, "paint-plate-2026-09-30.json")) as fh:
        cam = json.load(fh)["camera_model"]
    X, U = [], []
    for p in cam["points"]:
        x, y, z = p["commanded"]
        X.append([x, y, z + (cam["stall_offset_mm_fitted"] if p["after_stall"] else 0.0)])
        U.append(p["pixel"])
    rows = []
    for (x, y, z), (u, v) in zip(X, U):
        rows.append([x, y, z, 1, 0, 0, 0, 0, -u * x, -u * y, -u * z, -u])
        rows.append([0, 0, 0, 0, x, y, z, 1, -v * x, -v * y, -v * z, -v])
    P = np.linalg.svd(np.array(rows))[2][-1].reshape(3, 4)

    def proj(p):
        h = P @ np.r_[p, 1.0]
        return h[:2] / h[2]

    centre = np.array([68.38, 223.74, 14.4])      # the plate's centre and top, as placed
    J = np.column_stack([proj(centre + e) - proj(centre) for e in np.eye(3)[:2]])
    mm = np.linalg.solve(J, [dx, dy])
    return {"pixels_cols_rows": [round(float(dx), 2), round(float(dy), 2)],
            "match": round(-float(fit.fun), 3),
            "deck_mm_dx_dy": [round(float(mm[0]), 2), round(float(mm[1]), 2)],
            "px_per_mm_at_plate": {"+x": J[:, 0].round(3).tolist(), "+y": J[:, 1].round(3).tolist()}}


def chart(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, muted, grid = "#0b0b0b", "#52514e", "#e4e3df"
    rail, led = "#2a78d6", "#eb6834"
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=130)
    for ax in (a, b):
        ax.set_facecolor("#fcfcfb")
        ax.grid(axis="y", color=grid, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(muted)
        ax.tick_params(colors=muted, labelsize=9)
        ax.set_xticks(NM)
        ax.set_xticklabels([str(n) for n in NM], fontsize=8)
        ax.set_xlabel("channel (nm)", color=muted, fontsize=9)
    series = [
        ("rail lights, z 92", res["rail_lights"]["z92"]["black_over_white"], rail, "-", "o", -5),
        ("rail lights, resting", res["rail_lights"]["rest"]["black_over_white"], rail, "--", "s", 5),
        ("board LED 10 mA, z 92", res["led"]["z92"][10]["black_over_white"], led, "-", "o", 6),
        ("board LED 10 mA, resting", res["led"]["rest"][10]["black_over_white"], led, "--", "s", -6),
    ]
    for name, y, col, ls, mk, dy in series:
        a.plot(NM, y, ls=ls, color=col, lw=2, marker=mk, ms=6, label=name,
               markeredgecolor="#fcfcfb", markeredgewidth=1.2)
        a.annotate(name, (NM[-1], y[-1]), xytext=(6, dy), textcoords="offset points",
                   va="center", fontsize=8, color=ink)
    a.set_ylim(0, 1.05)
    a.set_xlim(395, 760)
    a.set_ylabel("black well ÷ white well", color=muted, fontsize=9)
    a.set_title("a) The LED can't tell the black well from the white one",
                loc="left", fontsize=10, color=ink)
    a.text(400, 0.04, "0 = perfect black vs perfect white. The LED reads 0.99 at z 92 and\n"
           "0.97 resting at 4, 10 and 20 mA alike (10 mA shown).",
           fontsize=7.5, color=muted)
    a.legend(loc="lower right", fontsize=7.5, frameon=False, bbox_to_anchor=(1.0, 0.12))
    cols = {"F3": "#1baf7a", "F6": "#6250d6", "F9": "#e34948"}
    marks = {"F3": "o", "F6": "s", "F9": "^"}
    for w, y in res["empty_wells_z92"]["over_black"].items():
        b.plot(NM, y, color=cols[w], lw=2, marker=marks[w], ms=6, label=f"empty {w}",
               markeredgecolor="#fcfcfb", markeredgewidth=1.2)
        b.annotate(f"empty {w}", (NM[-1], y[-1]), xytext=(6, 0), textcoords="offset points",
                   va="center", fontsize=8, color=ink)
    b.axhline(1.0, color=muted, lw=1, ls=":")
    b.text(400, 1.003, "black well H7", fontsize=7.5, color=muted, va="bottom")
    b.set_xlim(395, 740)
    b.set_ylabel("empty well ÷ black well H7, z 92, rail lights", color=muted, fontsize=9)
    b.set_title("b) What an empty well reads depends on where it is",
                loc="left", fontsize=10, color=ink)
    b.legend(loc="upper left", fontsize=7.5, frameon=False)
    fig.text(0.01, 0.01, "2026-10-14, one enclosure trip, black paper under the plate in slot 7. "
             "Lamp offset subtracted from rail-light readings; the LED-off reading at gain 4 "
             "from LED readings. analyse_led_background.py", fontsize=7, color=muted)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(PNG)


def main():
    d = load()
    rows = d["readings"]
    g = groups(rows)
    res = {"led": {"z92": led_ratios(g, "z92"), "rest": led_ratios(g, "rest")},
           "rail_lights": {"z92": rail_ratios(g, "black-H7-z92", "white-H12-z92"),
                           "rest": rail_ratios(g, "black-H7-rest", "white-H12-rest")}}
    # LED brightness against current: the board's light only, dark subtracted
    lin = {}
    for w, where in (("H7", "z92"), ("H12", "z92"), ("H7", "rest"), ("H12", "rest")):
        dk = g[f"dark-{w}-{where}"].mean(0).sum()
        t = {ma: g[f"led{ma}-{w}-{where}"].mean(0).sum() - dk for ma in (4, 10, 20)}
        lin[f"{w} {where}"] = {"10/4": round(t[10] / t[4], 3), "20/4": round(t[20] / t[4], 3)}
    res["led_vs_current"] = lin
    sat = [r for r in rows if (r.get("sensor_settings") or {}).get("analog_saturated")]
    peak = max(max(r["channels"].values()) for r in rows if r.get("settings"))
    clear = max(max((r.get("sensor_extra") or {}).get("clear") or [0]) for r in rows)
    res["led_saturation"] = {"analog_saturated_readings": len(sat), "highest_channel": peak,
                             "highest_clear": clear, "full_scale": 65535}
    # The LED's paint-dependent light against the rail lights', in the same units (128x)
    for where in ("z92", "rest"):
        led = res["led"][where][4]
        span_led_128 = (led["white_total"] - led["black_total"]) * 128 / 4
        rl = res["rail_lights"][where]
        span_rail = rl["white_total"] - rl["black_total"]
        res["led"][where]["span_vs_rail_at_128x"] = {
            "led_4mA_white_minus_black": round(span_led_128),
            "rail_white_minus_black": round(span_rail, 1),
            "ratio": round(span_led_128 / span_rail, 2)}
    # Empty wells against the black and white wells, z 92, rail lights, lamp subtracted
    black = g["black-H7-z92"].mean(0) - LAMP
    white = g["white-H12-z92"].mean(0) - LAMP
    res["empty_wells_z92"] = {
        "over_black": {w: ((g[f"empty-{w}"].mean(0) - LAMP) / black).round(4).tolist()
                       for w in ("F3", "F6", "F9")},
        "calibrated_R": {w: ((g[f"empty-{w}"].mean(0) - LAMP - black) / (white - black))
                         .round(4).tolist() for w in ("F3", "F6", "F9")},
        "totals": {w: round(float(g[f"empty-{w}"].mean(0).sum()), 1) for w in ("F3", "F6", "F9")},
        "black_total": round(float(g["black-H7-z92"].mean(0).sum()), 1),
        "white_total": round(float(g["white-H12-z92"].mean(0).sum()), 1)}
    res["repeatability_max_spread"] = {k: round(spread(v), 5) for k, v in g.items()
                                       if len(v) >= 4}
    # The landings, by light (two readings per step, rail lights on)
    steps = defaultdict(list)
    for r in rows:
        if r["label"].startswith("z") and r["well"] in ("H7", "H12") and r["seq"] >= 32:
            steps[(r["well"], r["seq"], r["nozzle"][2])].append(r["total"])
    res["landings"] = [{"well": w, "photo": s, "z": z, "total": round(sum(v) / len(v), 1)}
                       for (w, s, z), v in sorted(steps.items(), key=lambda kv: kv[0][1])]
    res["after_h7_landing"] = {
        "H7_z92_before": res["empty_wells_z92"]["black_total"],
        "H7_z92_after": round(float(np.mean([r["total"] for r in rows
                                             if r["seq"] == 47])), 1),
        "H7_rest": round(float(g["black-H7-rest"].mean(0).sum()), 1),
        "H12_z92_before": res["empty_wells_z92"]["white_total"],
        "H12_z92_after": round(float(g["white-H12-z92-again"].mean(0).sum()), 1)}
    res["plate_shift"] = plate_shift()
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1)
    chart(res)
    z = res["led"]
    print("LED black/white z92:", {k: v["total_black_over_white"] for k, v in z["z92"].items()
                                   if isinstance(k, int)},
          "rest:", {k: v["total_black_over_white"] for k, v in z["rest"].items()
                    if isinstance(k, int)})
    print("rail black/white z92", res["rail_lights"]["z92"]["total_black_over_white"],
          "rest", res["rail_lights"]["rest"]["total_black_over_white"])
    print("empty / black totals", res["empty_wells_z92"]["totals"], res["empty_wells_z92"]["black_total"])
    print("plate shift", res["plate_shift"])


if __name__ == "__main__":
    main()
