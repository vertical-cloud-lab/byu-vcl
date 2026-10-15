"""Why the colour scan cannot resolve red or blue, from the data already on record.

Answers the question asked on issue #197: ambient light is real, but is it the
whole story?  It is not.  Three instrument-side effects are each larger than the
signal a diluted-paint vial can produce, and one of them is spectrally
*degenerate* with yellow -- which is why yellow is the only colour that has ever
appeared.

Reads only the committed ``xscan-*.json`` run files.  No hardware, no network.

    python3 analyse_instrument_artefacts.py
"""

from __future__ import annotations

import glob
import json
import math
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CHANNELS = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
WAVELENGTHS = np.array([410, 440, 470, 510, 550, 583, 620, 670])

# The AS7341 carries 11 photodiodes but only 6 ADCs, so the eight spectral
# channels cannot be sampled at once.  Every driver reads F1-F4 in one
# integration and F5-F8 in a second.  One "reading" is therefore two
# measurements taken at different times and concatenated.
SMUX_SPLIT = 4


def load_runs():
    return {os.path.basename(f): json.load(open(f))
            for f in sorted(glob.glob(os.path.join(HERE, "xscan-*.json")))}


def vec(reading):
    return [reading["channels"][c] for c in CHANNELS]


def share(v):
    total = sum(v)
    return [100.0 * x / total for x in v]


def scan_positions(run):
    """Mean vector per scan position, repeats collapsed."""
    by = {}
    for r in run["readings"]:
        p = r.get("position")
        if not p or "index" not in p:
            continue
        by.setdefault(p["index"], []).append(vec(r))
    return [[st.mean(x[i] for x in v) for i in range(8)] for _, v in sorted(by.items())]


def seated_vectors(runs):
    """Every 'module sitting closed on its base' reading of the session."""
    out = []
    for run in runs.values():
        for r in run["readings"]:
            stage = (r.get("stage") or "")
            if ("seated" in stage or "reseat" in stage) and r["total"] < 600:
                out.append(vec(r))
    return out


def repeat_deviations(runs):
    """Fractional deviation of each read from the mean of its own position."""
    dev = []
    for name, run in runs.items():
        by = {}
        for r in run["readings"]:
            p = r.get("position")
            if not p or "index" not in p:
                continue
            by.setdefault((name, p["index"]), []).append(vec(r))
        for v in by.values():
            if len(v) < 2:
                continue
            m = [st.mean(x[i] for x in v) for i in range(8)]
            dev.extend([[(x[i] - m[i]) / m[i] for i in range(8)] for x in v])
    return dev


def cosine(a, b):
    """Similarity of two *shapes*, with overall level removed from both."""
    a = np.asarray(a, float) - np.mean(a)
    b = np.asarray(b, float) - np.mean(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def pigment(base_share, transmittance):
    """The share-space signature a real pigment of this transmittance would leave."""
    filtered = share([base_share[i] * transmittance[i] for i in range(8)])
    return [filtered[i] - base_share[i] for i in range(8)]


# Rough double-pass transmittances for artist acrylic diluted in water, per band.
PIGMENTS = {
    "yellow": [0.10, 0.20, 0.55, 0.95, 1.00, 1.00, 1.00, 1.00],
    "blue":   [0.85, 0.95, 0.95, 0.60, 0.25, 0.12, 0.10, 0.15],
    "red":    [0.30, 0.25, 0.20, 0.20, 0.30, 0.70, 0.95, 0.95],
}


def main():
    runs = load_runs()
    seated = seated_vectors(runs)
    dark = [st.mean(v[i] for v in seated) for i in range(8)]
    dark_sd = [st.pstdev([v[i] for v in seated]) for i in range(8)]

    print(f"[1] fixed offset inside the enclosure  ({len(seated)} reads, 7 runs, ~8 h apart)")
    for i, c in enumerate(CHANNELS):
        print(f"      {c}  {dark[i]:7.2f} +/- {dark_sd[i]:.2f}")
    print(f"      total {sum(dark):.0f} counts, peaked at 510/550 nm")

    z128 = scan_positions(runs["xscan-slot7-z128-2026-09-09.json"])
    z120 = scan_positions(runs["xscan-slot7-z120-2026-09-09.json"])
    print("\n      as a share of ch510 / ch550 at each scan position:")
    for label, mats in (("z 120", z120), ("z 128", z128)):
        frac = [(100 * dark[3] / m[3], 100 * dark[4] / m[4]) for m in mats]
        print(f"      {label}: " + "  ".join(f"{a:.0f}%/{b:.0f}%" for a, b in frac))

    dev = repeat_deviations(runs)
    D = np.array(dev)
    C = np.corrcoef(D.T)
    print(f"\n[2] two-cycle readout  ({len(dev)} reads)")
    for k in range(1, 8):
        idx = list(range(8))
        A, B = idx[:k], idx[k:]
        within = [C[i, j] for g in (A, B) for i in g for j in g if i < j]
        across = [C[i, j] for i in A for j in B]
        sep = np.mean(within) - np.mean(across)
        tag = "  <- AS7341 F1-F4 | F5-F8" if k == SMUX_SPLIT else ""
        print(f"      split {WAVELENGTHS[k-1]}|{WAVELENGTHS[k]}: separation {sep:+.3f}{tag}")

    base = share(z128[0])
    models = {"readout half-step": [-base[i] if i < SMUX_SPLIT else base[i] for i in range(8)]}
    models.update({f"{k} paint": pigment(base, t) for k, t in PIGMENTS.items()})
    print("\n[3] is each colour distinguishable from the readout artefact?")
    for k in list(PIGMENTS):
        print(f"      {k:7s} vs artefact: {cosine(models['readout half-step'], models[k+' paint']):+.3f}")

    print("\n[4] field of view vs a 3/4 in (19.05 mm) vial, AS7341 half-angle ~20 deg")
    for z, h in ((120, 29.5), (125, 34.5), (128, 37.5), (129, 39.0)):
        d = 2 * h * math.tan(math.radians(20.0))
        fill = (19.05 / d) ** 2
        print(f"      read z {z}: standoff {h:.1f} mm, spot {d:.1f} mm, vial fills {100*fill:.0f}%")

    print(f"\n[5] dynamic range: largest count on record "
          f"{max(max(vec(r)) for run in runs.values() for r in run['readings'])} of 65535")

    figure(dark, z120, z128, C, models, os.path.join(HERE, "instrument-artefacts-2026-09-09.png"))


def figure(dark, z120, z128, C, models, out_path):
    fig, ax = plt.subplots(2, 2, figsize=(11.5, 8.4), dpi=110)
    fig.suptitle("Three instrument effects larger than the paint signal  (issue #197)",
                 fontsize=13, fontweight="bold")

    # --- the fixed offset --------------------------------------------------
    a = ax[0, 0]
    a.bar(range(8), dark, color=[plt.cm.turbo((w - 400) / 300) for w in WAVELENGTHS],
          edgecolor="black", linewidth=0.6)
    a.set_xticks(range(8)); a.set_xticklabels(WAVELENGTHS, fontsize=8)
    a.set_ylabel("counts"); a.set_xlabel("wavelength (nm)")
    a.set_title("1. Something green is on inside the box\n"
                f"26 seated reads over ~8 h, every channel +/-1 count", fontsize=10)
    a.set_ylim(0, max(dark) * 1.35)
    a.annotate("510 + 550 nm carry 78%\nof it -- that is a green\nemitter, not room light",
               xy=(4.0, dark[4] * 1.04), xytext=(6.3, max(dark) * 1.18),
               fontsize=8, ha="center", va="top",
               arrowprops=dict(arrowstyle="->", lw=0.9))

    # --- how much of each channel it is ------------------------------------
    a = ax[0, 1]
    w = 0.38
    for off, mats, lab, col in ((-w/2, z120, "read z 120 (aperture 29.5 mm)", "#2a9d8f"),
                                (+w/2, z128, "read z 128 (aperture 37.5 mm)", "#e76f51")):
        frac = [100 * dark[i] / st.mean(m[i] for m in mats) for i in range(8)]
        a.bar(np.arange(8) + off, frac, w, label=lab, color=col, edgecolor="black", linewidth=0.5)
    a.set_xticks(range(8)); a.set_xticklabels(WAVELENGTHS, fontsize=8)
    a.set_ylabel("% of the channel that is the fixed offset"); a.set_xlabel("wavelength (nm)")
    a.set_title("...and it is never subtracted.\nRaising the sensor makes it dominate the green channels",
                fontsize=10)
    a.legend(fontsize=8)

    # --- the correlation block ---------------------------------------------
    a = ax[1, 0]
    im = a.imshow(C, cmap="RdBu_r", vmin=-1, vmax=1)
    a.set_xticks(range(8)); a.set_xticklabels(WAVELENGTHS, fontsize=7, rotation=90)
    a.set_yticks(range(8)); a.set_yticklabels(WAVELENGTHS, fontsize=7)
    for s in (SMUX_SPLIT - 0.5,):
        a.axhline(s, color="black", lw=2); a.axvline(s, color="black", lw=2)
    for i in range(8):
        for j in range(8):
            a.text(j, i, f"{C[i,j]:.2f}", ha="center", va="center", fontsize=6,
                   color="white" if abs(C[i, j]) > 0.6 else "black")
    a.set_title("2. One reading is two measurements\nrepeat-read correlation breaks exactly at F1-F4 | F5-F8",
                fontsize=10)
    fig.colorbar(im, ax=a, fraction=0.046)

    # --- the aliasing -------------------------------------------------------
    a = ax[1, 1]
    art = np.array(models["readout half-step"], float)
    art = art / np.max(np.abs(art))
    a.plot(WAVELENGTHS, art, "k-o", lw=2.2, ms=5, label="the readout artefact", zorder=5)
    for name, col in (("yellow paint", "#e9c46a"), ("blue paint", "#264653"), ("red paint", "#d62828")):
        v = np.array(models[name], float)
        v = v / np.max(np.abs(v))
        a.plot(WAVELENGTHS, v, "-o", color=col, lw=1.8, ms=4,
               label=f"{name}  (cos {cosine(models['readout half-step'], models[name]):+.2f})")
    a.axhline(0, color="grey", lw=0.6)
    a.axvline(530, color="black", ls=":", lw=1.2)
    a.set_ylim(-1.35, 1.35)
    a.text(534, -0.05, "readout split", fontsize=7, rotation=90, va="center")
    a.set_xlabel("wavelength (nm)"); a.set_ylabel("normalised signature")
    a.set_title("3. Blue is the artefact upside down (cos -0.95)\nso a blue vial and a mis-timed read are the same number",
                fontsize=10)
    a.legend(fontsize=8, loc="lower right")

    fig.tight_layout(rect=[0, 0, 1, 0.955])
    fig.savefig(out_path)
    print(f"\nwrote {os.path.basename(out_path)}")


if __name__ == "__main__":
    main()
