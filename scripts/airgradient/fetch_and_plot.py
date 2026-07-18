"""Fetch AirGradient measures for the CB 154 monitor and plot RH/temperature.

Usage:
    AIRGRADIENT_API_KEY=... python fetch_and_plot.py [FROM] [TO]

FROM/TO are ISO 8601 basic-format UTC timestamps (e.g. 20260715T000000Z).
The API token comes from the AIRGRADIENT_API_KEY environment variable and is
never written to disk or printed. Docs: https://api.airgradient.com/public/docs/api/v1/
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

API_BASE = "https://api.airgradient.com/public/api/v1"
LOCAL_TZ = ZoneInfo("America/Denver")

# July 17, 2026 dehumidifier test: AirGradient ~2.5 in from the Quest 155
# output, driest setting (issue #42).
EXPERIMENT_START = pd.Timestamp("2026-07-17 12:32", tz=LOCAL_TZ)
EXPERIMENT_END = pd.Timestamp("2026-07-17 16:57", tz=LOCAL_TZ)

# dataviz palette (light mode)
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
SERIES_RH = "#2a78d6"
SERIES_TEMP = "#008300"
BAND = "#f0efec"


def api_get(path: str, **params) -> object:
    token = os.environ["AIRGRADIENT_API_KEY"]
    query = urllib.parse.urlencode({"token": token, **params})
    with urllib.request.urlopen(f"{API_BASE}{path}?{query}") as resp:
        return json.load(resp)


def main() -> None:
    date_from = sys.argv[1] if len(sys.argv) > 1 else "20260715T000000Z"
    date_to = sys.argv[2] if len(sys.argv) > 2 else "20260718T060000Z"

    locations = api_get("/locations/measures/current")
    location = locations[0]
    location_id = location["locationId"]
    location_name = location["locationName"]

    records = api_get(f"/locations/{location_id}/measures/past",
                      **{"from": date_from, "to": date_to})
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert(LOCAL_TZ)
    df = df.sort_values("timestamp")

    out_stem = f"{location_name.lower().replace(' ', '')}_rh_temp_{date_from[:8]}_{date_to[:8]}"
    df[["timestamp", "rhum", "atmp", "rco2", "pm02", "tvocIndex"]].to_csv(
        f"{out_stem}.csv", index=False)

    during = df["timestamp"].between(EXPERIMENT_START, EXPERIMENT_END)
    before = df["timestamp"] < EXPERIMENT_START
    after = df["timestamp"] > EXPERIMENT_END
    for label, mask in [("before", before), ("during", during), ("after", after)]:
        sub = df[mask]
        print(f"{label}: n={len(sub)}  RH mean={sub['rhum'].mean():.1f}% "
              f"(min {sub['rhum'].min():.0f}, max {sub['rhum'].max():.0f})  "
              f"T mean={sub['atmp'].mean():.1f} C")

    fig, (ax_rh, ax_t) = plt.subplots(
        2, 1, sharex=True, figsize=(11, 6.5), facecolor=SURFACE,
        gridspec_kw={"hspace": 0.12})

    for ax, col, color, ylabel in [
        (ax_rh, "rhum", SERIES_RH, "Relative humidity (%)"),
        (ax_t, "atmp", SERIES_TEMP, "Temperature (\N{DEGREE SIGN}C)"),
    ]:
        ax.set_facecolor(SURFACE)
        ax.axvspan(EXPERIMENT_START, EXPERIMENT_END, color=BAND, zorder=0)
        ax.plot(df["timestamp"], df[col], color=color, linewidth=2)
        ax.set_ylabel(ylabel, color=TEXT_SECONDARY)
        ax.grid(axis="y", color="#e8e7e3", linewidth=0.8)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color(TEXT_SECONDARY)
        ax.tick_params(colors=TEXT_SECONDARY)

    ax_rh.annotate("dehumidifier ON\n(driest setting)",
                   xy=(EXPERIMENT_START, 40), xytext=(-8, 0),
                   textcoords="offset points", ha="right", va="center",
                   fontsize=9, color=TEXT_SECONDARY)
    ax_rh.set_title(
        f"AirGradient \N{QUOTATION MARK}{location_name}\N{QUOTATION MARK} "
        "\N{EM DASH} sensor at dehumidifier output from Jul 17 12:32 PM "
        "(times in America/Denver)",
        color=TEXT_PRIMARY, fontsize=11, loc="left")
    ax_t.xaxis.set_major_formatter(
        mdates.DateFormatter("%b %d\n%H:%M", tz=LOCAL_TZ))

    fig.savefig(f"{out_stem}.png", dpi=150, bbox_inches="tight",
                facecolor=SURFACE)
    print(f"wrote {out_stem}.png and {out_stem}.csv")


if __name__ == "__main__":
    main()
