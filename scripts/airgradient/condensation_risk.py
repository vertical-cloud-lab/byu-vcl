"""When do the atomizer's cold surfaces sweat in CB 154? (issue #42, PR #247)

A surface collects condensate when it is colder than the air's dew point, and
it sees a high RH well before that. Air temperature does not enter into it, so
the enclosure's extra warmth neither causes nor prevents condensation; only its
lower dew point helps. This script takes the AirGradient's dew point history
and asks how often a surface held at a given temperature would be at or below
it, in the room (Feb 5 - Sep 29) and in the enclosure (since the dehumidifier
went on), and what RH a cold surface or cold powder sees in each.

Surfaces of interest, from the commissioning and training videos (#255):
  - Facility chilled water, upstream of the heat exchanger: cold enough that,
    with no heat load, the atomizer's own loop fell below its 10 C "water too
    cold" alarm, which was lowered to 7 C on Sep 28. Its temperature has not
    been measured.
  - The atomizer loop (chamber water jacket, cone, coil): about 23 C during
    the Sep 30 melt with the facility valve throttled, colder at idle and
    during cooldown, when the chamber is opened.

Data: the 5-minute archive on this branch (Jul 18 - Oct 3) and the Feb 5 -
Jul 18 archive on claude/issue-42-20260718-1733. Get the latter with
    git show origin/claude/issue-42-20260718-1733:scripts/airgradient/\
cb154_full_history_20260205_20260718.csv.gz > /tmp/cb154_feb_jul.csv.gz

Usage:
    python condensation_risk.py --history /tmp/cb154_feb_jul.csv.gz
"""

import argparse
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from check_status import (BLUE, INK, MUTED, ORANGE, SECONDARY, SURFACE, TZ,
                          dew_point, rh_at, style_axis)

HERE = Path(__file__).parent
RECENT = HERE / "cb154_5min_20260718_20261003.csv.gz"
DEHUMIDIFIER_ON = "2026-09-29 13:30"
# The monitor reached the enclosure late on Sep 29; the first evening was
# still pulling down, so the enclosure statistics start the next morning.
ENCLOSURE_FROM = "2026-09-29 18:00"
STEADY_FROM = "2026-09-30 00:00"
# Candidate surface temperatures, C
SURFACES = [
    (7, "7 \N{DEGREE SIGN}C: loop alarm as set on Sep 28"),
    (10, "10 \N{DEGREE SIGN}C: factory alarm; the facility water tripped it"),
    (15, "15 \N{DEGREE SIGN}C: suggested floor for the loop"),
]
TABLE_T = [5, 7, 10, 12, 15, 18, 20, 23]
CORROSION_RH = 70  # onset of atmospheric corrosion of clean Al (Graedel 1989)


def hourly(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["timestamp", "atmp", "rhum"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.set_index("timestamp").tz_convert(TZ).resample("1h").mean()


def share_at_or_above(dew: pd.Series, temps) -> np.ndarray:
    """Share of hours (%) whose dew point is at or above each temperature."""
    d = dew.dropna().to_numpy()
    return np.array([100 * (d >= t).mean() for t in temps])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", type=Path, required=True,
                    help="Feb 5 - Jul 18 archive (see the module docstring)")
    args = ap.parse_args()

    recent = hourly(RECENT)
    old = hourly(args.history)
    h = pd.concat([old[old.index < recent.index[0]], recent])
    h["dew"] = dew_point(h["atmp"], h["rhum"])
    on = pd.Timestamp(DEHUMIDIFIER_ON, tz=TZ)
    room = h[h.index < on].dropna()
    enc = h[h.index >= pd.Timestamp(ENCLOSURE_FROM, tz=TZ)].dropna()
    steady = enc[enc.index >= pd.Timestamp(STEADY_FROM, tz=TZ)]
    spring = room[room.index < pd.Timestamp("2026-06-01", tz=TZ)]
    summer = room[room.index >= pd.Timestamp("2026-06-01", tz=TZ)]
    groups = [
        (f"room, {spring.index[0]:%b %-d} \N{EN DASH} May 31", spring, BLUE, "--"),
        (f"room, Jun 1 \N{EN DASH} {summer.index[-1]:%b %-d}", summer, BLUE, "-"),
        (f"enclosure, {steady.index[0]:%b %-d} \N{EN DASH} "
         f"{steady.index[-1]:%b %-d}", steady, ORANGE, "-"),
    ]

    print("dew point (C), hourly means:")
    for name, g, *_ in groups:
        q = g["dew"].quantile([0.5, 0.9, 0.99])
        print(f"  {name:<28} n={len(g):5d} h  median {q[0.5]:5.1f}  p90 "
              f"{q[0.9]:5.1f}  p99 {q[0.99]:5.1f}  max {g['dew'].max():5.1f}")
    print("share of hours (%) a surface at T would be at or below the dew point:")
    print(f"  {'surface T (C)':<36}" + "".join(f"{t:>6}" for t in TABLE_T))
    for name, g, *_ in groups:
        print(f"  {name:<36}" + "".join(
            f"{v:6.1f}" for v in share_at_or_above(g["dew"], TABLE_T)))
    print("RH (%) at a surface at T, for air at a given dew point "
          "(wet = condensing):")
    for td, what in [(steady["dew"].median(), "enclosure median"),
                     (steady["dew"].max(), "enclosure max"),
                     (summer["dew"].median(), "room Jun-Sep median"),
                     (summer["dew"].max(), "room Jun-Sep max")]:
        print(f"  {f'dew {td:4.1f} C, {what}':<36}" + "".join(
            f"{'wet' if rh_at(td, t) >= 100 else f'{rh_at(td, t):.0f}':>6}"
            for t in TABLE_T))

    fig = plt.figure(figsize=(11.5, 9), constrained_layout=True)
    fig.set_facecolor(SURFACE)
    grid = fig.add_gridspec(2, 2, height_ratios=[1, 1.05])
    ax_t = fig.add_subplot(grid[0, :])
    ax_x = fig.add_subplot(grid[1, 0])
    ax_rh = fig.add_subplot(grid[1, 1])

    # 1. dew point over time against the candidate surface temperatures
    style_axis(ax_t, "Dew point (\N{DEGREE SIGN}C)")
    ax_t.plot(room.reindex(h.index[h.index < on]).index,
              h.loc[h.index < on, "dew"], color=BLUE, linewidth=0.8,
              label="room (hourly)")
    ax_t.plot(enc.index, enc["dew"], color=ORANGE, linewidth=1.2,
              label="enclosure, dehumidifier on (hourly)")
    for t, label in SURFACES:
        ax_t.axhline(t, color=SECONDARY, linewidth=0.9, linestyle=":")
        ax_t.annotate(label, (0.005, t), xycoords=("axes fraction", "data"),
                      xytext=(0, 2), textcoords="offset points", va="bottom",
                      fontsize=8.5, color=SECONDARY,
                      bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1))
    ax_t.set_xlim(h.index[0], h.index[-1] + pd.Timedelta("2D"))
    ax_t.xaxis.set_major_locator(mdates.MonthLocator(tz=TZ))
    ax_t.xaxis.set_major_formatter(mdates.DateFormatter("%b", tz=TZ))
    ax_t.legend(loc="lower left", bbox_to_anchor=(0, 1), ncol=2, fontsize=8.5,
                frameon=False, labelcolor=SECONDARY)
    ax_t.annotate("a surface held at a line's temperature collects condensate\n"
                  "whenever the dew point is above that line; air temperature\n"
                  "plays no part",
                  (0.995, 0.03), xycoords="axes fraction", ha="right",
                  va="bottom", fontsize=8.5, color=SECONDARY)

    # 2. how often a surface at T sweats
    temps = np.arange(0, 20.01, 0.1)
    style_axis(ax_x, "Hours at or below the dew point (%)")
    for name, g, color, ls in groups:
        y = share_at_or_above(g["dew"], temps)
        ax_x.plot(temps, y, color=color, linestyle=ls, linewidth=2,
                  label=f"{name} ({len(g)} h)")
    for t, _ in SURFACES:
        ax_x.axvline(t, color=SECONDARY, linewidth=0.9, linestyle=":")
    ax_x.set_xlabel("Surface temperature (\N{DEGREE SIGN}C)", color=SECONDARY,
                    fontsize=10)
    ax_x.set_xlim(0, 20)
    ax_x.set_ylim(0, 100)
    ax_x.legend(loc="upper right", fontsize=8.5, frameon=True,
                facecolor=SURFACE, edgecolor="none", framealpha=1,
                labelcolor=SECONDARY)
    ax_x.set_title("How often a surface at that temperature would sweat",
                   loc="left", fontsize=10, color=INK)

    # 3. the RH a cold surface or cold powder sees
    ts = np.arange(4, 28.01, 0.1)
    style_axis(ax_rh, "RH at the surface (%)")
    cases = [
        (summer["dew"].median(), f"room air, Jun\N{EN DASH}Sep median dew point",
         BLUE, "-"),
        (steady["dew"].max(), "enclosure air, highest dew point since Sep 30",
         ORANGE, "--"),
        (steady["dew"].median(), "enclosure air, median dew point", ORANGE, "-"),
    ]
    for td, label, color, ls in cases:
        rh = rh_at(td, ts)
        keep = rh <= 100
        ax_rh.plot(ts[keep], rh[keep], color=color, linestyle=ls, linewidth=2,
                   label=f"{label}, {td:.1f} \N{DEGREE SIGN}C")
    ax_rh.axhline(CORROSION_RH, color=SECONDARY, linewidth=0.9, linestyle=":")
    ax_rh.annotate("~70%: atmospheric corrosion\nof clean Al begins",
                   (27.8, CORROSION_RH), ha="right", va="bottom", fontsize=8.5,
                   color=SECONDARY, xytext=(0, 2), textcoords="offset points")
    t_enc = steady["atmp"].median()
    ax_rh.plot([t_enc], [rh_at(steady["dew"].median(), t_enc)], "o",
               color=ORANGE, markersize=8, markeredgecolor=SURFACE,
               markeredgewidth=2)
    ax_rh.annotate(f"enclosure air at the monitor,\n{t_enc:.1f} \N{DEGREE SIGN}C",
                   (t_enc, rh_at(steady["dew"].median(), t_enc)),
                   xytext=(-6, -10), textcoords="offset points", ha="right",
                   va="top", fontsize=8.5, color=SECONDARY)
    ax_rh.set_xlabel("Surface or powder temperature (\N{DEGREE SIGN}C)",
                     color=SECONDARY, fontsize=10)
    ax_rh.set_xlim(4, 28)
    ax_rh.set_ylim(0, 100)
    ax_rh.legend(loc="lower left", fontsize=8.5, frameon=False,
                 labelcolor=SECONDARY)
    ax_rh.set_title("What a cold surface, or cold powder, sees", loc="left",
                    fontsize=10, color=INK)

    fig.suptitle(
        f"CB 154: dew point vs the atomizer's cold surfaces, "
        f"{h.index[0]:%b %-d} \N{EN DASH} {h.index[-1]:%b %-d, %Y}. "
        "AirGradient hourly means; the Aug 11 \N{EN DASH} Sep 11 gap is an outage.",
        x=0.01, ha="left", fontsize=11, color=INK)
    out = HERE / f"cb154_condensation_{h.index[-1]:%Y%m%d}.png"
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print("wrote", out)


if __name__ == "__main__":
    main()
