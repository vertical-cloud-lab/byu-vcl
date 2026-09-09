"""One small spectrum per colour measurement, in the light-mixing house style.

Follows ``scripts/basic_plotting.py`` from
https://huggingface.co/spaces/AccelerationConsortium/light-mixing -- the same
rainbow strip under the axis, the same rainbow-mapped scatter with a black
edge, the same dashed stems down to zero -- shrunk to a 300 px thumbnail that
can sit next to a video frame in a table.

Two departures from the original, both to keep a column of these comparable at
a glance rather than each one auto-scaling to its own maximum:

* ``--ymax`` fixes the y axis across a set of plots.
* the title carries the instant of the measurement, so a plot is never
  separated from the moment it belongs to.

Usage::

    python3 plot_spectra.py                       # every scan position
    python3 plot_spectra.py --run xscan-slot7-sweep-2026-09-09.json
"""

from __future__ import annotations

import argparse
import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WAVELENGTHS = np.array([410, 440, 470, 510, 550, 583, 620, 670])
CHANNELS = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]


def plot_spectra(sensor_data, out_path, title=None, subtitle=None, ymax=None,
                 num_points=100, width_px=300, dpi=100):
    """The basic_plotting.py figure, sized for a thumbnail."""
    intensities = np.array([sensor_data[c] for c in CHANNELS], dtype=float)
    top = ymax if ymax else max(intensities) * 1.12 + 10

    fig, ax = plt.subplots(figsize=(width_px / dpi, width_px * 0.72 / dpi), dpi=dpi)

    # The rainbow strip under the axis, as in the original.
    span = WAVELENGTHS.max() - WAVELENGTHS.min()
    rect_height = top * 0.03
    for dw in np.linspace(WAVELENGTHS.min(), WAVELENGTHS.max(), num_points):
        ax.add_patch(Rectangle(
            (dw - span / num_points / 2, -rect_height * 2),
            span / num_points, rect_height * 3,
            facecolor=plt.cm.rainbow((dw - WAVELENGTHS.min()) / span),
            edgecolor="none"))

    for wl, inten in zip(WAVELENGTHS, intensities):
        ax.vlines(wl, 0, inten, color="gray", linestyle="--", linewidth=0.6)
    ax.scatter(WAVELENGTHS, intensities, c=WAVELENGTHS, cmap="rainbow",
               edgecolor="k", linewidths=0.4, s=18, zorder=3)

    ax.set_xlim(WAVELENGTHS.min() - 10, WAVELENGTHS.max() + 10)
    ax.set_ylim(-rect_height * 2, top)
    ax.set_xticks([410, 470, 550, 620, 670])
    ax.tick_params(labelsize=5, length=2, pad=1)
    ax.set_xlabel("Wavelength (nm)", fontsize=5.5, labelpad=1)
    ax.set_ylabel("Intensity", fontsize=5.5, labelpad=1)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    if title or subtitle:
        ax.set_title("\n".join(t for t in (title, subtitle) if t),
                     fontsize=6, pad=3, linespacing=1.5)
    fig.tight_layout(pad=0.35)
    fig.savefig(out_path)
    plt.close(fig)


def mean_channels(readings):
    return {c: sum(r["channels"][c] for r in readings) / float(len(readings))
            for c in CHANNELS}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--index", default=os.path.join(HERE, "measurement-stream-index.json"))
    p.add_argument("--out-dir", default=os.path.join(HERE, "spectra"))
    p.add_argument("--run", help="limit to one run file")
    p.add_argument("--ymax", type=float, default=None,
                   help="fix the y axis across every plot (default: per-run maximum)")
    p.add_argument("--width", type=int, default=300)
    args = p.parse_args(argv)

    rows = json.load(open(args.index))["readings"]
    rows = [r for r in rows if r["stage"].startswith("pos")]
    if args.run:
        rows = [r for r in rows if r["run_file"] == args.run]

    groups = {}
    for r in rows:
        groups.setdefault((r["run_file"], r["stage"]), []).append(r)

    os.makedirs(args.out_dir, exist_ok=True)
    manifest = []
    # One y scale per run, so the three (or nine) stops of a scan are directly
    # comparable; different runs sat at different heights and are not.
    run_max = {}
    for (run_file, _stage), reads in groups.items():
        m = max(max(r["channels"][c] for c in CHANNELS) for r in reads)
        run_max[run_file] = max(run_max.get(run_file, 0), m)

    for (run_file, stage), reads in sorted(groups.items(),
                                           key=lambda kv: kv[1][0]["t_response_epoch"]):
        reads.sort(key=lambda r: r["t_response_epoch"])
        name = "%s-%s.png" % (os.path.splitext(run_file)[0].replace("xscan-", ""),
                              stage.replace("+", "p"))
        out = os.path.join(args.out_dir, name)
        pos = reads[0]["position"] or {}
        title = "x = %.2f mm  ·  n=%d" % (pos.get("x", float("nan")), len(reads))
        subtitle = "%s UTC" % reads[0]["t_response_utc"][11:19]
        plot_spectra(mean_channels(reads), out, title=title, subtitle=subtitle,
                     ymax=args.ymax or run_max[run_file] * 1.15, width_px=args.width)
        manifest.append({"file": name, "run_file": run_file, "stage": stage,
                         "x": pos.get("x"), "n_reads": len(reads),
                         "t_first_utc": reads[0]["t_response_utc"],
                         "mean_total": round(sum(r["total"] for r in reads) / len(reads), 1)})

    json.dump(manifest, open(os.path.join(args.out_dir, "spectra.json"), "w"), indent=2)
    print("%d spectra -> %s" % (len(manifest), args.out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
