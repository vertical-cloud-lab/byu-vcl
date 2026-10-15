#!/usr/bin/env python3
"""What did blacking out the OT-2 do to the accuracy? Before/after, from runs already on file.

    python3 analyse_blackout.py

No hardware. Asked on PR #202, 2026-10-02: now that the OT-2 is temporarily blacked
out, how did that affect the accuracy? The OT-2 went dark in two steps:

    sides     black panels on its sides, between the 11:18 and 13:19 runs of
              2026-09-30 (Tim noted them at 13:47)
    cardboard spare cardboard and a piece of wood over the rest, 2026-10-01 ~13:30

Three questions, each answered from readings that were taken anyway:

1. How much outside light did each step remove? Every run picks the enclosure up
   from socket A2 (92.8, 316.5) and reads at the same three spots on the way out:
   just lifted (z 93), above the socket (z 110) and at carry height (z 190). No
   paint and no plate are involved there, so those readings change only with the
   light. The board's own lamp (the sealed reading of 2026-09-10) is subtracted.
2. Do the readings jitter less? Two readings in a row at one spot, ~1.5 s apart,
   in every run of 2026-09-30 and 2026-10-01 that logged them in pairs.
3. Are the colours more accurate? The 2026-09-30 evening run (sides only) and the
   2026-10-01 run (cardboard) read the same five wells (H2 yellow, H4 red, H7
   black, H10 blue, H12 white) at the same nozzle heights z 125 and 90-86.5. Both
   are scored the way analyse_height_series.py scores 2026-10-01: white/black
   calibrated at each height, mean distance outside the published pigment range
   at 440-670 nm. 10-01's near-plate heights use the re-scored values from
   landing_shift.py (the white from the second H12 landing). Between these two
   runs the plate also moved from slot 1 to slot 7 and the paint aged ~19 h.

Writes blackout-2026-10-02.json and blackout-2026-10-02.png.
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from analyse_paint_accuracy import CHANNELS, NM, OFFSET, load_reference, per_channel  # noqa: E402
from analyse_white_black import BLACKS, WHITES, calibrate  # noqa: E402
from analyse_white_black_correction import KEEP, references, score  # noqa: E402

LAMP = float(OFFSET.sum())            # 406.5 counts: the board's own lamp, sealed
STAGES = ["none", "sides", "cardboard"]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
# Colour is the blackout stage, the same in both panels.
STAGE_LOOK = {"none": ("no blackout", "#8f8c85"),
              "sides": ("sides covered", "#eb6834"),
              "cardboard": ("sides + cardboard", "#2a78d6")}
COLOURS = {"H2": "yellow", "H4": "red", "H10": "blue"}


def load(name):
    return json.load(open(os.path.join(HERE, name)))


def spec(r):
    return [r["channels"][c] for c in CHANNELS]


def fixed_poses():
    """Totals at the three spots over socket A2, run by run."""
    e = load("enclosure-height-2026-09-30.json")
    a = load("enclosure-height-a1-2026-09-30.json")
    p = load("paint-plate-2026-09-30.json")
    w = load("paint-white-black-2026-09-30.json")
    h = load("height-series-2026-10-01.json")
    runs = [
        ("09-30 10:22", "none", e["run2"]["reads_after_lift"], e["run2"]["up_110_reads"],
         e["run2"]["carry"]["carry_start_z190_reads"]),
        ("09-30 10:46", "none", e["run3"]["reads_after_lift_z93"], e["run3"]["up_110_reads"],
         e["run3"]["carry"]["carry_start_z190_reads"]),
        ("09-30 11:18", "none", a["reads_after_lift_z93"], a["up_110_reads"],
         a["carry"]["carry_start_z190_reads"]),
    ]
    lad = {x["label"]: x["totals"] for x in p["enclosure"]["ladder"]}
    runs.append(("09-30 13:19", "sides", lad["lifted_z93"], lad["up_z110"], lad["carry_start_z190"]))
    spectra = {"sides": {}, "cardboard": {}}
    for ps, t in ((1, "09-30 15:36"), (2, "09-30 16:13")):
        rows = [s for s in w["steps"] if s.get("pass") == ps]
        got = {k: [s["total"] for s in rows if s["label"] == k]
               for k in ("lifted_z93", "up_z110", "carry_start_z190")}
        runs.append((t, "sides", got["lifted_z93"], got["up_z110"], got["carry_start_z190"]))
        for k in ("up_z110", "carry_start_z190"):
            spectra["sides"].setdefault(k, []).extend(spec(s) for s in rows if s["label"] == k)
    got = {k: [r["total"] for r in h["readings"] if r["label"] == k]
           for k in ("lifted_z93", "up_z110", "carry_start_z190")}
    runs.append(("10-01 13:43", "cardboard", got["lifted_z93"], got["up_z110"], got["carry_start_z190"]))
    for k in ("up_z110", "carry_start_z190"):
        spectra["cardboard"][k] = [spec(r) for r in h["readings"] if r["label"] == k]

    poses = {"z93": 2, "z110": 3, "z190": 4}
    out = {"runs": [{"run": r[0], "stage": r[1], "z93": r[2], "z110": r[3], "z190": r[4]} for r in runs],
           "lamp_subtracted": LAMP, "by_stage": {}}
    for pose, i in poses.items():
        level = {s: float(np.mean([np.mean(r[i]) for r in runs if r[1] == s])) - LAMP for s in STAGES}
        spread = {s: [float(min(np.mean(r[i]) for r in runs if r[1] == s)) - LAMP,
                      float(max(np.mean(r[i]) for r in runs if r[1] == s)) - LAMP] for s in STAGES}
        out["by_stage"][pose] = {
            "outside_light_counts": {s: round(v, 1) for s, v in level.items()},
            "run_to_run_range_counts": {s: [round(x, 1) for x in v] for s, v in spread.items()},
            "percent_of_no_blackout": {s: round(100 * level[s] / level["none"], 1) for s in STAGES},
            "sides_removed_percent": round(100 * (1 - level["sides"] / level["none"]), 1),
            "cardboard_removed_percent_of_what_sides_left": round(100 * (1 - level["cardboard"] / level["sides"]), 1),
        }
    # What colour was the light the cardboard took out? (only these two have 8 channels)
    step = {}
    for k in ("up_z110", "carry_start_z190"):
        before = np.mean(spectra["sides"][k], axis=0)
        after = np.mean(spectra["cardboard"][k], axis=0)
        removed = before - after
        i440, i620 = list(NM).index(440), list(NM).index(620)
        step[k] = {"sides": before.round(1).tolist(), "cardboard": after.round(1).tolist(),
                   "removed": removed.round(1).tolist(),
                   "removed_440_over_620": round(float(removed[i440] / removed[i620]), 2),
                   "remaining_440_over_620": round(float(after[i440] / after[i620]), 2)}
    out["cardboard_step_spectra"] = step
    return out


def pairs():
    """Relative difference of two readings in a row at one spot, every run."""
    def rel(x, y):
        return abs(x - y) / ((x + y) / 2)

    runs = []
    e = load("enclosure-height-2026-09-30.json")
    for t, lad in (("09-30 09:53", e["ladder"]), ("09-30 10:31", e["run2"]["ladder"]),
                   ("09-30 10:54", e["run3"]["ladder"])):
        runs.append((t, "none", [(x["z"], rel(*x["reads"][:2])) for x in lad
                                 if x.get("z") is not None and len(x["reads"]) >= 2]))
    a = load("enclosure-height-a1-2026-09-30.json")
    runs.append(("09-30 11:26", "none", [(x["z"], rel(*x["reads"][:2])) for k in
                                         ("descent_1", "descent_2", "descent_3") for x in a[k]
                                         if x.get("z") is not None and len(x["reads"]) >= 2]))
    p = load("paint-plate-2026-09-30.json")
    pr = [(x["pos"][2], rel(*x["totals"][:2])) for x in p["enclosure"]["ladder"]
          if x.get("pos") and len(x.get("totals", [])) >= 2]
    for rs in p["readings"].values():
        t = [r["total"] for r in rs]
        pr += [(86.5, rel(t[i], t[i + 1])) for i in range(len(t) - 1)]
    runs.append(("09-30 13:19", "sides", pr))
    w = load("paint-white-black-2026-09-30.json")
    for ps, t in ((1, "09-30 15:36"), (2, "09-30 16:13")):
        rows = [s for s in w["steps"] if s.get("pass") == ps and s.get("pos")]
        runs.append((t, "sides", [(rows[i]["pos"][2], rel(rows[i]["total"], rows[i + 1]["total"]))
                                  for i in range(len(rows) - 1)
                                  if rows[i]["label"] == rows[i + 1]["label"]
                                  and rows[i]["pos"] == rows[i + 1]["pos"]]))
    s = load("paint-spaced-2026-09-30.json")
    lad, pr = s["ladder"], []
    for i in range(len(lad) - 1):
        lab = lad[i]["label"]
        if lab == lad[i + 1]["label"] and lab not in ("seated", "backed_out", "homed"):
            z = 125.0 if lab.startswith(("xy", "over_plate")) else (float(lab[1:]) if lab.startswith("z") else None)
            pr.append((z, rel(lad[i]["total"], lad[i + 1]["total"])))
    rs = s["readings"]
    pr += [(86.5, rel(rs[i]["total"], rs[i + 1]["total"])) for i in range(len(rs) - 1)
           if (rs[i]["well"], rs[i]["visit"]) == (rs[i + 1]["well"], rs[i + 1]["visit"])]
    runs.append(("09-30 19:14", "sides", pr))
    h = load("height-series-2026-10-01.json")
    lit = [r for r in h["readings"] if r["nozzle"] and r["rail_lights"] == "on"]
    runs.append(("10-01 13:49", "cardboard", [(lit[i]["nozzle"][2], rel(lit[i]["total"], lit[i + 1]["total"]))
                                             for i in range(len(lit) - 1)
                                             if (lit[i]["nozzle"], lit[i]["seq"]) == (lit[i + 1]["nozzle"], lit[i + 1]["seq"])]))
    out = []
    for t, stage, pr in runs:
        v = 100 * np.array([x for _, x in pr])
        hang = 100 * np.array([x for z, x in pr if z is not None and z >= 92])
        out.append({"run": t, "stage": stage, "pairs": len(v),
                    "median_percent": round(float(np.median(v)), 3),
                    "max_percent": round(float(v.max()), 2),
                    "over_0.5_percent": int((v > 0.5).sum()),
                    "hanging_z92_up_max_percent": round(float(hang.max()), 2) if len(hang) else None,
                    "differences_percent": np.round(v, 3).tolist()})
    return out


def matched_heights(ref, rw, rb):
    """09-30 evening (sides only) scored at the heights 10-01 (cardboard) also used."""
    s = load("paint-spaced-2026-09-30.json")
    order = iter(["H7", "H12", "H10", "H4", "H2", "H4-2"])   # the run's landing order
    by, cur, prev = {}, None, None
    for r in s["ladder"]:
        lab = r["label"]
        if lab.startswith(("xy", "over_plate")):
            if lab != prev:
                cur = next(order)
            z = 125.0
        elif lab.startswith("z") and cur:
            z = float(lab[1:])
        else:
            prev = lab
            continue
        prev = lab
        by.setdefault((cur, z), []).append(spec(r))
    for r in s["readings"]:                     # the 8 at z 86.5 after each landing
        by.setdefault((r["well"] if r["visit"] == 1 else "H4-2", 86.5), []).append(spec(r))

    a = load("height-series-analysis-2026-10-01.json")["heights"]
    rescored = load("landing-shift-2026-10-01.json")["light"]["rescored"]
    out = {}
    for z in (125.0, 90.0, 89.0, 88.0, 87.0, 86.5):
        row = {}
        for red in ("H4", "H4-2"):
            m = {w: np.mean(by[(w, z)], axis=0) for w in ("H2", "H10", "H7", "H12")}
            m["H4"] = np.mean(by[(red, z)], axis=0)
            v = {COLOURS[w]: calibrate(m[w], m["H12"], m["H7"], rw, rb) for w in COLOURS}
            sc = score(v, ref)
            row["sides_red_visit_1" if red == "H4" else "sides_red_visit_2"] = {
                "miss": sc["miss_mean"], "black_reads": sc["fit_mid"]["a_black_reads"],
                "squeeze": sc["fit_mid"]["differences_too_small_by"]}
        after = a[str(z)]
        row["cardboard"] = {"miss": after["miss_mean"], "black_reads": after["fit_mid"]["a_black_reads"],
                            "squeeze": after["fit_mid"]["differences_too_small_by"]}
        if str(z) in rescored:
            row["cardboard_rescored_second_white"] = rescored[str(z)]["second"]["miss"]
        out[str(z)] = row
    out["cardboard_only_heights"] = {z: a[z]["miss_mean"] for z in ("110.0", "100.0", "95.0", "92.0")}
    return out, by


def scatter_at_contact(by, rw, rb):
    """How much one reading's calibrated colour wanders within a landing (440-670 nm)."""
    out = {}
    s = load("paint-spaced-2026-09-30.json")
    blk = {}
    for r in s["readings"]:
        blk.setdefault((r["well"], r["visit"]), []).append(spec(r))
    W, B = np.mean(blk[("H12", 1)], axis=0), np.mean(blk[("H7", 1)], axis=0)
    for key, name in ((("H2", 1), "yellow"), (("H4", 1), "red, 1st landing"),
                      (("H4", 2), "red, 2nd landing"), (("H10", 1), "blue")):
        v = calibrate(np.array(blk[key], float), W, B, rw, rb)[:, KEEP]
        out.setdefault("sides", {})[name] = {"sd": round(float(v.std(0, ddof=1).mean()), 4),
                                             "max_from_mean": round(float(np.abs(v - v.mean(0)).max()), 3)}
    jump = [r for r in s["ladder"] if r["label"] == "z86.5"][-2:]          # H4, 2nd landing
    d = calibrate(np.array([spec(r) for r in jump], float), W, B, rw, rb)
    out["sides_largest_jump"] = {"totals": [r["total"] for r in jump],
                                 "calibrated_change_per_channel": np.abs(d[0] - d[1]).round(3).tolist()}
    h = load("height-series-2026-10-01.json")
    blk = {}
    for r in h["readings"]:
        if r["rail_lights"] == "on" and r["well"] and r["nozzle"][2] == 86.5:
            blk.setdefault((r["well"], r["visit"]), []).append(spec(r))
    W, B = np.mean(blk[("H12", 2)], axis=0), np.mean(blk[("H7", 1)], axis=0)
    for key, name in ((("H2", 1), "yellow"), (("H4", 1), "red"), (("H10", 1), "blue")):
        v = calibrate(np.array(blk[key], float), W, B, rw, rb)[:, KEEP]
        out.setdefault("cardboard", {})[name] = {"sd": round(float(v.std(0, ddof=1).mean()), 4),
                                                 "max_from_mean": round(float(np.abs(v - v.mean(0)).max()), 3)}
    return out


def main():
    spectra = load_reference()
    ref = references(spectra)
    rw = np.array([per_channel(spectra[k]) for k in WHITES]).mean(axis=0)
    rb = np.array([per_channel(spectra[k]) for k in BLACKS]).mean(axis=0)

    light = fixed_poses()
    jitter = pairs()
    heights, by = matched_heights(ref, rw, rb)
    scatter = scatter_at_contact(by, rw, rb)
    dark = load("height-series-analysis-2026-10-01.json")["rail_lights_off_on_white_86.5"]
    out = {
        "what": "the OT-2 blackout, before and after, from runs already on file (no hardware)",
        "stages": {"none": "2026-09-30 morning runs", "sides": "sides blacked out; 2026-09-30 from the 13:19 run",
                   "cardboard": "sides + cardboard and wood over the rest; 2026-10-01"},
        "outside_light_at_fixed_spots": light,
        "rail_lights_off_at_contact_10_01": dark,
        "two_readings_in_a_row": [{k: v for k, v in r.items() if k != "differences_percent"} for r in jitter],
        "colour_error_same_wells_same_heights": heights,
        "colour_scatter_within_one_landing_at_contact": scatter,
        "confounded_with": "between the 09-30 evening and 10-01 runs the plate moved from slot 1 to slot 7 "
                           "and the paint aged ~19 h; the enclosure hung from a different socket (A1 vs A2)",
    }
    json.dump(out, open(os.path.join(HERE, "blackout-2026-10-02.json"), "w"), indent=1)

    print("outside light at the fixed spots, % of no blackout (lamp subtracted):")
    for pose, v in light["by_stage"].items():
        print(f"  {pose:5s} {v['percent_of_no_blackout']}  sides -{v['sides_removed_percent']}%, "
              f"cardboard -{v['cardboard_removed_percent_of_what_sides_left']}% of the rest")
    for k, v in light["cardboard_step_spectra"].items():
        print(f"  cardboard step at {k}: removed {v['removed']} (440/620 {v['removed_440_over_620']}, "
              f"remaining {v['remaining_440_over_620']})")
    print("two readings in a row:")
    for r in jitter:
        print(f"  {r['run']} {r['stage']:9s} n={r['pairs']:3d} median {r['median_percent']:.3f}% "
              f"max {r['max_percent']:.2f}% >0.5%: {r['over_0.5_percent']}")
    print("colour error, same wells, same heights:")
    for z in ("125.0", "90.0", "89.0", "88.0", "87.0", "86.5"):
        h = heights[z]
        print(f"  z {z:5s} sides {h['sides_red_visit_1']['miss']:.3f} / {h['sides_red_visit_2']['miss']:.3f} (red 2nd)"
              f"  cardboard {h['cardboard']['miss']:.3f}  rescored {h.get('cardboard_rescored_second_white', '-')}")
    print("scatter at contact:", json.dumps(scatter))
    plot(light, heights)


def style(ax, title):
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title(title, loc="left", color=INK, fontsize=10.5)


def plot(light, heights):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "font.family": "DejaVu Sans"})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.9), facecolor=SURFACE,
                                   gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.42})

    # 1. Outside light at the three fixed spots over the base, by blackout stage.
    style(ax1, "Light reaching the sensor at the same three spots")
    names = {"z190": "z 190, carry height", "z110": "z 110, above the socket", "z93": "z 93, just lifted"}
    for pose, label in names.items():
        pc = light["by_stage"][pose]["percent_of_no_blackout"]
        y = [pc[s] for s in STAGES]
        ax1.plot(range(3), y, color=INK2, lw=1.5, zorder=2)
        for i, s in enumerate(STAGES):
            ax1.plot(i, y[i], "o", ms=8, color=STAGE_LOOK[s][1], mec=SURFACE, mew=2, zorder=3)
        ax1.annotate(label, (2, y[2]), xytext=(10, 0), textcoords="offset points",
                     va="center", color=INK2, fontsize=8.5)
    ax1.set_xticks(range(3))
    ax1.set_xticklabels(["no blackout\n09-30 morning", "sides covered\n09-30 afternoon",
                         "+ cardboard\n10-01"])
    ax1.set_xlim(-0.3, 3.1)
    ax1.set_ylim(55, 105)
    ax1.set_ylabel("light from outside the board, % of no blackout")

    # 2. Colour error at the heights both runs used.
    style(ax2, "Colour error, same five wells, same heights")
    zs = [86.5, 87.0, 88.0, 89.0, 90.0]
    before = [heights[str(z)]["sides_red_visit_1"]["miss"] for z in zs]
    after_z = [86.5, 87.0, 88.0, 89.0, 90.0, 92.0, 95.0, 100.0, 110.0, 125.0]
    after = ([heights[str(z)]["cardboard_rescored_second_white"] for z in zs]
             + [heights["cardboard_only_heights"][str(z)] for z in (92.0, 95.0, 100.0, 110.0)]
             + [heights["125.0"]["cardboard"]["miss"]])
    ax2.axvspan(86.2, 87.9, color=GRID, alpha=0.7, lw=0, zorder=1)
    ax2.annotate("foot resting\non the plate", (87.05, 0.015), ha="center", va="bottom", color=INK2,
                 fontsize=8)
    b125 = heights["125.0"]["sides_red_visit_1"]["miss"]
    for x, y, s, lab in ((zs, before, "sides", "09-30 evening: sides covered (slot 1, paint ~0.5 h old)"),
                         (after_z, after, "cardboard", "10-01: + cardboard (slot 7, paint ~19 h old)")):
        col = STAGE_LOOK[s][1]
        ax2.plot(x, y, color=col, lw=2, marker="o", ms=7, mec=SURFACE, mew=1.5, zorder=3, label=lab)
    ax2.plot([125.0], [b125], "o", ms=7, color=STAGE_LOOK["sides"][1], mec=SURFACE, mew=1.5, zorder=3)
    ax2.annotate("sides covered", (125.0, b125), xytext=(-8, 10), textcoords="offset points", ha="right",
                 color=INK2, fontsize=8.5)
    ax2.annotate("+ cardboard", (110.0, after[8]), xytext=(0, -14), textcoords="offset points",
                 ha="center", va="top", color=INK2, fontsize=8.5)
    ax2.annotate("no 09-30 readings between z 90 and 125", (107.5, 0.205), ha="center", color=INK2,
                 fontsize=8)
    ax2.legend(frameon=False, fontsize=8, loc="upper right")
    ax2.set_xlim(85.5, 127)
    ax2.set_ylim(0, 0.5)
    ax2.set_xlabel("nozzle z (mm)")
    ax2.set_ylabel("mean miss vs published pigments (0 = inside)")
    fig.text(0.01, -0.06,
             "Left: socket A2, the board's own lamp (406.5 counts) subtracted; each point is the mean of every run at that "
             "stage (3, 3 and 1 runs). Right: white/black-calibrated at each height, 440-670 nm; 10-01 at z 86.5-90 uses\n"
             "the white from the second H12 landing (landing_shift.py). The plate moved and the paint aged between the "
             "two runs on the right, so their difference is not the blackout alone. Data: blackout-2026-10-02.json",
             color=INK2, fontsize=7.5)
    fig.savefig(os.path.join(HERE, "blackout-2026-10-02.png"), dpi=130, facecolor=SURFACE,
                bbox_inches="tight")


if __name__ == "__main__":
    main()
