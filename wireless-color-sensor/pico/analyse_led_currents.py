#!/usr/bin/env python3
"""Does the board LED give different information at different brightnesses?

    python3 analyse_led_currents.py

No hardware. Asked on PR #202 (2026-10-10): would reading each experiment with the
AS7341 breakout's white LED at several currents (off, dim, bright, brightest) give
more varied or useful information than one setting? Answers the part that does not
need a paint plate: does the LED's *colour* change with current, or only its
brightness?

Data: led-currents-2026-10-10.json, 41 readings over MQTT with the settings firmware
(main.py, installed 10-10), the board on the robot Pi's USB facing the same unknown
scene throughout. At 4x gain: every even current 4-20 mA twice (an up-and-down order,
so drift and current are not confounded) with the LED off at the start, middle and
end; 12 repeats at 20 mA; one ATIME 50 reading. At 16x: 0, 4, 8, 12 mA and off.

    net        reading minus the mean LED-off reading at the same gain (ambient)
    share      a channel's net / the sum of all 8: the LED's colour as the sensor sees it
               on this scene, independent of brightness
    change     share at a current / share at 10 mA - 1, in %
    noise      the 20 mA repeats' standard deviation of each share, in %
    SVD        of the 9 x 8 matrix of shares (each column divided by its mean): the
               first singular value is the common colour, the second what changing the
               current adds, the third and beyond what is left (noise)

Writes led-currents-analysis-2026-10-10.json and led-currents-2026-10-10.png.
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CHANNELS = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")
NM = [int(c[2:]) for c in CHANNELS]
REF_MA = 10
# sequential blue ramp, steps 250-700 (light = low current)
RAMP = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#0d366b"]
SURFACE, INK, INK2, MUTED, GRID, BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#d9d7cf"


def counts(r):
    return np.array([r["channels"][c] for c in CHANNELS], float)


def main():
    src = os.path.join(HERE, "led-currents-2026-10-10.json")
    rows = json.load(open(src))["readings"]
    pick = lambda block, gain, ma: [counts(r) for r in rows if r["block"] == block  # noqa: E731
                                    and r["settings"]["gain"] == gain and r["settings"]["led_ma"] == ma
                                    and "atime" not in r["settings"]]
    off4 = np.mean([counts(r) for r in rows if r["settings"]["gain"] == 4 and r["settings"]["led_ma"] == 0], axis=0)
    off16 = np.mean(pick("gain16", 16, 0), axis=0)
    currents = sorted({r["settings"]["led_ma"] for r in rows if r["block"] == "shape" and r["settings"]["led_ma"]})
    passes = {i: [v - off4 for v in pick("shape", 4, i)] for i in currents}
    net = {i: np.mean(passes[i], axis=0) for i in currents}
    share = {i: net[i] / net[i].sum() for i in currents}
    change = {i: 100 * (share[i] / share[REF_MA] - 1) for i in currents}

    rep = np.array([v - off4 for v in pick("repeat20", 4, 20)])
    rep_share = rep / rep.sum(axis=1, keepdims=True)
    noise = 100 * rep_share.std(axis=0, ddof=1) / rep_share.mean(axis=0)
    pass_diff = {i: float(np.abs(100 * ((p[0] / p[0].sum()) / (p[1] / p[1].sum()) - 1)).max())
                 for i, p in passes.items()}

    m = np.array([share[i] for i in currents])
    m = m / m.mean(axis=0)
    u, s, vt = np.linalg.svd(m, full_matrices=False)
    rank1 = np.outer(u[:, 0] * s[0], vt[0])
    beyond1 = float(100 * np.sqrt(((m - rank1) ** 2).mean()))
    rank2 = rank1 + np.outer(u[:, 1] * s[1], vt[1])
    beyond2 = float(100 * np.sqrt(((m - rank2) ** 2).mean()))

    per_ma = {i: float(net[i].sum() / i) for i in currents}
    g16 = {i: (pick("gain16", 16, i)[0] - off16) for i in (4, 8)}
    atime50 = [counts(r) for r in rows if r["settings"].get("atime") == 50][0] - off4 * 51 / 101

    out = {
        "source": os.path.basename(src),
        "what": "share = a channel's LED-on minus LED-off counts over the sum of all 8; change = vs 10 mA",
        "led_off_counts_4x": off4.round(2).tolist(),
        "net_counts_4x": {str(i): net[i].round(1).tolist() for i in currents},
        "share_change_vs_10mA_percent": {str(i): change[i].round(2).tolist() for i in currents},
        "change_4_to_20mA_percent": (100 * (share[20] / share[4] - 1)).round(2).tolist(),
        "repeat_20mA": {"n": int(len(rep)), "total_sd_percent": round(float(100 * rep.sum(1).std(ddof=1) / rep.sum(1).mean()), 3),
                        "share_sd_percent": noise.round(3).tolist()},
        "two_passes_max_share_difference_percent": {str(i): round(v, 3) for i, v in pass_diff.items()},
        "svd": {"singular_values": [round(float(x), 5) for x in s],
                "second_over_first": round(float(s[1] / s[0]), 4),
                "third_over_first": round(float(s[2] / s[0]), 5),
                "rms_left_after_1_component_percent": round(beyond1, 3),
                "rms_left_after_2_components_percent": round(beyond2, 3),
                "component_2_by_channel": [round(float(x), 3) for x in vt[1]]},
        "counts_per_mA_relative_to_10mA": {str(i): round(per_ma[i] / per_ma[REF_MA], 4) for i in currents},
        "gain_16x_over_4x": {str(i): {"ratio": round(float(g16[i].sum() / net[i].sum()), 4),
                                      "share_change_percent": (100 * ((g16[i] / g16[i].sum()) / share[i] - 1)).round(2).tolist()}
                             for i in g16},
        "atime_50_over_100_at_20mA": {"ratio": round(float(atime50.sum() / net[20].sum()), 4), "expected": round(51 / 101, 4)},
    }
    json.dump(out, open(os.path.join(HERE, "led-currents-analysis-2026-10-10.json"), "w"), indent=1)

    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw={"width_ratios": [1.55, 1]}, facecolor=SURFACE)
    for ax in (a, b):
        ax.set_facecolor(SURFACE)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(MUTED)
        ax.tick_params(colors=INK2, labelsize=9)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)

    x = np.arange(len(NM))
    a.fill_between(x, -2 * noise, 2 * noise, color=BAND, lw=0, zorder=1)
    a.axhline(0, color=MUTED, lw=0.8, zorder=1)
    for k, i in enumerate(currents):
        a.plot(x, change[i], color=RAMP[k], lw=2, marker="o", ms=4.5, zorder=3,
               markeredgecolor=SURFACE, markeredgewidth=1)
    for i in (4, 20):
        a.annotate(f"{i} mA", (x[2], change[i][2]), xytext=(9, 0), textcoords="offset points",
                   va="center", color=INK, fontsize=9)
    a.text(0.985, 0.97, "every curve is the same pattern, scaled:\nchanging the current adds one colour\n"
                        "component, ~1% in size\n\ngrey band at 0: ±2 SD of 12 repeat\nreadings at 20 mA (≤ 0.1%)",
           transform=a.transAxes, ha="right", va="top", color=INK2, fontsize=8.5)
    cmap = matplotlib.colors.ListedColormap(RAMP)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=matplotlib.colors.BoundaryNorm(np.arange(3, 22, 2), cmap.N))
    cb = fig.colorbar(sm, ax=a, ticks=currents, fraction=0.035, pad=0.02, aspect=28)
    cb.set_label("LED current (mA)", color=INK2, fontsize=9)
    cb.ax.tick_params(colors=INK2, labelsize=8.5, length=0)
    cb.outline.set_visible(False)
    a.set_xticks(x, [f"{n}" for n in NM])
    a.set_xlim(-0.4, len(NM) - 0.2)
    a.set_xlabel("sensor channel (nm)", color=INK2, fontsize=9.5)
    a.set_ylabel("change in the channel's share of the light\nvs the LED at 10 mA (%)", color=INK2, fontsize=9.5)
    a.set_title("Brighter LED, slightly bluer light: 440 nm rises, 470 nm falls", color=INK, fontsize=11,
                loc="left", pad=10)

    rel = [per_ma[i] / per_ma[REF_MA] for i in currents]
    b.axhline(1, color=MUTED, lw=0.8)
    b.plot(currents, rel, color=RAMP[4], lw=2, marker="o", ms=5, markeredgecolor=SURFACE, markeredgewidth=1)
    b.set_ylim(0.95, 1.05)
    b.set_xticks(currents)
    b.set_xlabel("LED current (mA)", color=INK2, fontsize=9.5)
    b.set_ylabel("light per mA, relative to 10 mA", color=INK2, fontsize=9.5)
    b.set_title("Brightness tracks the current within ±2%", color=INK, fontsize=11, loc="left", pad=10)
    b.text(0.03, 0.06, f"second colour component: {100 * s[1] / s[0]:.1f}% of the first;\n"
                       f"left after two components: {beyond2:.3f}% rms (noise)",
           transform=b.transAxes, color=INK2, fontsize=8.5)

    fig.text(0.01, 0.005, "AS7341 breakout LED, 4x gain, 2 x 281 ms, LED-off reading subtracted; board on the robot Pi's "
                          "USB facing the same scene throughout (2026-10-10). Data: led-currents-2026-10-10.json",
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(HERE, "led-currents-2026-10-10.png"), dpi=150, facecolor=SURFACE)
    print(json.dumps({k: out[k] for k in ("change_4_to_20mA_percent", "svd", "repeat_20mA")}, indent=1))


if __name__ == "__main__":
    main()
