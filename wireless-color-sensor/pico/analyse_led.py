"""The AS7341's white LED, switched on from the robot Pi on 2026-10-10: the numbers and chart.

Reads ``led-test-2026-10-10.json`` (written from ``led_check.py``'s output) and, for the
rail lights, the 10-06 evening white well (H12) in ``../ot2/black-paper-2026-10-06.json``.
No hardware. Prints a summary and writes ``led-test-analysis-2026-10-10.json`` and
``led-test-2026-10-10.png``.

    registers   CONFIG (0x70) and LED (0x74) after each set_led_current() call
    current     counts at 32x for 10 mA and 20 mA over 4 mA, per unsaturated channel
    colour      each light's 8 channels over its own brightest channel: the LED as the
                sensor saw it on the bench, minus the LED-off reading scaled to 32x; the
                rail lights over the white well at z 125, minus the board's sealed lamp
    brightness  the LED at 4 mA, scaled to 128x, over the rail lights on the white well
                (rough: what the bench sensor faced is unknown)
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CH = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
NM = [410, 440, 470, 510, 550, 583, 620, 670]
CENTRE = [415, 445, 480, 515, 555, 590, 630, 680]   # DS000504 peak wavelengths, as in ../ot2
LAMP = np.array([4, 3, 8, 160.5, 168.5, 35, 16, 11.5])  # sealed board lamp, 09-10 (../ot2)
CAP = 65535

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
LED_C, RAIL_C = "#2a78d6", "#eb6834"   # validated pair (dataviz validator, light mode)


def load():
    led = json.load(open(os.path.join(HERE, "led-test-2026-10-10.json")))
    rail = json.load(open(os.path.join(HERE, "..", "ot2", "black-paper-2026-10-06.json")))
    return led, rail


def block(readings, tag, ma):
    rows = [r for r in readings if r["tag"] == tag and r["mA"] == ma]
    return np.array([r["ch"] for r in rows], float), rows


def analyse(led, rail):
    rd = led["led_check"]["readings"]
    out = {"registers": [{k: e.get(k) for k in ("event", "mA")} | {
        "CONFIG": e["regs"]["CONFIG"], "LED": e["regs"]["LED"], "CFG1": e["regs"]["CFG1"]}
        for e in led["led_check"]["events"]]}

    off, _ = block(rd, "off", 0)
    off_after, _ = block(rd, "off-after", 0)
    on4_128, rows4 = block(rd, "on", 4)
    on32 = {ma: block(rd, "on-32x", ma) for ma in (4, 10, 20)}
    gain_ratio = float(on4_128[:, 0].mean() / on32[4][0][:, 0].mean())  # ch410: unsaturated at both
    out["saturation"] = {
        f"{tag} {ma} mA": {"channels_at_cap": int((block(rd, tag, ma)[0] >= CAP).any(0).sum()),
                           "analog_flag": any(s & 0x80 for r in block(rd, tag, ma)[1] for s in r["astatus"])}
        for tag, ma in (("on", 4), ("on", 10), ("on", 20), ("on-32x", 4), ("on-32x", 10), ("on-32x", 20))}
    out["gain_128x_over_32x_ch410"] = round(gain_ratio, 3)

    m32 = {ma: on32[ma][0].mean(0) for ma in on32}
    ratios = {}
    for ma in (10, 20):
        ok = (m32[ma] < CAP) & (m32[4] < CAP)
        ratios[f"{ma}/4 mA"] = {"expected": ma / 4, "channels": {
            CH[i]: round(float(m32[ma][i] / m32[4][i]), 3) for i in range(8) if ok[i]}}
    out["current_ratios_32x"] = ratios
    rep = on32[4][0]
    out["repeat_spread_32x_4mA_pct"] = round(float(((rep.max(0) - rep.min(0)) / rep.mean(0)).max() * 100), 2)

    led_net = m32[4] - off.mean(0) / gain_ratio
    led_norm = led_net / led_net.max()
    h12 = np.array([[r["channels"][c] for c in CH] for r in rail["readings"]
                    if r.get("well") == "H12" and r.get("pass") == 1 and r.get("nozzle")
                    and r["nozzle"][2] == 125.0], float)
    rail_net = h12.mean(0) - LAMP
    rail_norm = rail_net / rail_net.max()
    out["colour"] = {
        "led_4mA_32x_net": np.round(led_net, 1).tolist(),
        "led_norm": np.round(led_norm, 3).tolist(),
        "rail_white_z125_net": np.round(rail_net, 1).tolist(),
        "rail_norm": np.round(rail_norm, 3).tolist(),
        "led_over_rail": np.round(led_norm / rail_norm, 2).tolist(),
        "rail_readings": len(h12),
    }
    out["brightness_led4mA_over_rail_white"] = round(float(led_net.sum() * gain_ratio / rail_net.sum()), 1)
    out["off_before_total"] = round(float(off.sum(1).mean()), 1)
    out["off_after_total"] = round(float(off_after.sum(1).mean()), 1)
    out["mqtt_before_total"] = [r["total"] for r in led["mqtt_before"]]
    out["mqtt_after_total"] = [r["total"] for r in led["mqtt_after"]]
    return out, led_norm, rail_norm


def plot(led_norm, rail_norm, path):
    fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for y, c, name in ((led_norm, LED_C, "board LED, 4 mA (bench)"),
                       (rail_norm, RAIL_C, "OT-2 rail lights, white well (10-06)")):
        ax.plot(CENTRE, y, color=c, lw=2, zorder=3)
        ax.scatter(CENTRE, y, s=42, color=c, edgecolor=SURFACE, linewidth=2, zorder=4, label=name)
    ax.annotate("board LED", (CENTRE[2], led_norm[2]), xytext=(6, 8), textcoords="offset points",
                color=INK, fontsize=8.5)
    ax.annotate("rail lights", (CENTRE[2], rail_norm[2]), xytext=(6, -14), textcoords="offset points",
                color=INK, fontsize=8.5)
    ax.set_xticks(CENTRE, [str(n) for n in NM])
    ax.set_xlabel("AS7341 channel (nm)", color=INK2, fontsize=9)
    ax.set_ylabel("light, as a share of the brightest channel", color=INK2, fontsize=9)
    ax.set_ylim(0, 1.08)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.tick_params(colors=INK2, labelsize=8.5, length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right", labelcolor=INK)
    ax.set_title("The board's LED is bluer than the rail lights, but just as weak at 410 nm",
                 color=INK, fontsize=10.5, loc="left")
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)


def main():
    led, rail = load()
    out, led_norm, rail_norm = analyse(led, rail)
    json.dump(out, open(os.path.join(HERE, "led-test-analysis-2026-10-10.json"), "w"), indent=1)
    plot(led_norm, rail_norm, os.path.join(HERE, "led-test-2026-10-10.png"))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
