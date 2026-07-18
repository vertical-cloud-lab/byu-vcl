"""Holistic analysis of the CB 154 AirGradient sensor history (issue #42).

Fetches the full retained history for the CB 154 monitor from the AirGradient
public API, plus outdoor weather / air quality for Provo, UT from Open-Meteo,
then renders an overview figure of every data channel with event annotations.

API notes (verified empirically on 2026-07-18):
  - Auth: `token` query param, read from the AIRGRADIENT_API_KEY env var.
  - GET /public/api/v1/locations/{id}/measures/past?from=...&to=... with
    timestamps like 20260718T170000Z; max 10 days per request (422 beyond).
  - 5-minute buckets are retained for 150 days on a rolling basis; older data
    is served in 1-hour buckets. Raw (unbucketed) data is only kept ~10 days.
  - First stored record for CB 154: 2026-02-05T20:00Z (sensor came online).

Usage:
    AIRGRADIENT_API_KEY=... python full_history_analysis.py

Cached CSVs in this directory are reused if present; delete them to refetch.
"""

import datetime as dt
import os
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import requests

HERE = Path(__file__).parent
BASE = "https://api.airgradient.com/public/api/v1"
LOCATION_ID = 184200  # "CB 154"
LAT, LON = 40.246, -111.649  # BYU campus, Provo, UT
START = dt.datetime(2026, 2, 5)
END = dt.datetime(2026, 7, 18, 17, 30)
TZ = "America/Denver"

INDOOR_CSV = HERE / "cb154_full_history_20260205_20260718.csv.gz"
WEATHER_CSV = HERE / "provo_weather_20260205_20260718.csv"
AQ_CSV = HERE / "provo_airquality_20260205_20260718.csv"

# palette (dataviz skill reference, light mode)
BLUE = "#2a78d6"  # indoor series
GREEN = "#008300"  # outdoor series
INK = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"


def fetch_indoor() -> pd.DataFrame:
    if INDOOR_CSV.exists():
        df = pd.read_csv(INDOOR_CSV, parse_dates=["timestamp"])
    else:
        token = os.environ["AIRGRADIENT_API_KEY"]
        rows, cur = [], START
        while cur < END:
            to = min(cur + dt.timedelta(days=10), END)
            r = requests.get(
                f"{BASE}/locations/{LOCATION_ID}/measures/past",
                params={
                    "token": token,
                    "from": cur.strftime("%Y%m%dT%H%M%SZ"),
                    "to": to.strftime("%Y%m%dT%H%M%SZ"),
                },
                timeout=180,
            )
            r.raise_for_status()
            rows.extend(r.json())
            cur = to
        df = pd.DataFrame(rows).drop_duplicates(subset="timestamp")
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)
        df.to_csv(INDOOR_CSV, index=False)
    return df.set_index("timestamp").tz_convert(TZ)


def fetch_open_meteo(url: str, hourly: str, path: Path) -> pd.DataFrame:
    if path.exists():
        df = pd.read_csv(path, parse_dates=["time"])
        if df["time"].dt.tz is None:
            df["time"] = df["time"].dt.tz_localize("UTC")
    else:
        r = requests.get(
            url,
            params=dict(
                latitude=LAT,
                longitude=LON,
                start_date=START.strftime("%Y-%m-%d"),
                end_date=END.strftime("%Y-%m-%d"),
                hourly=hourly,
                timezone="UTC",
            ),
            timeout=120,
        )
        r.raise_for_status()
        df = pd.DataFrame(r.json()["hourly"])
        df.to_csv(path, index=False)
        df["time"] = pd.to_datetime(df["time"]).dt.tz_localize("UTC")
    return df.set_index("time").tz_convert(TZ)


def style_axis(ax, ylabel):
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, linewidth=0.7)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.set_ylabel(ylabel, color=SECONDARY, fontsize=10)


EVENTS = [  # (label, start, end) in local time
    ("A", "2026-03-12", "2026-03-15"),  # regional dust storm
    ("B", "2026-05-15 14:52", "2026-05-18 09:22"),  # dehumidifier test 1
    ("C", "2026-06-20", "2026-06-26"),  # wildfire smoke
    ("D", "2026-07-04 18:00", "2026-07-05 06:00"),  # July 4 fireworks
    ("E", "2026-07-17 12:32", "2026-07-17 16:57"),  # dehumidifier test 2
]
RETENTION_EDGE = pd.Timestamp("2026-02-18 10:40", tz=TZ)


def main():
    df = fetch_indoor()
    w = fetch_open_meteo(
        "https://archive-api.open-meteo.com/v1/archive",
        "temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,"
        "snowfall,surface_pressure,wind_speed_10m",
        WEATHER_CSV,
    )
    aq = fetch_open_meteo(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        "pm2_5,pm10,us_aqi,carbon_monoxide",
        AQ_CSV,
    )

    d = df.resample("D")
    panels = [
        ("Relative humidity (%)", "rhum", w["relative_humidity_2m"], "mean"),
        ("Temperature (°C)", "atmp", w["temperature_2m"], "mean"),
        ("CO₂ (ppm)", "rco2", None, "mean"),
        ("PM2.5, daily max (µg/m³)", "pm02_corrected", aq["pm2_5"], "max"),
        ("TVOC index", "tvocIndex", None, "mean"),
        ("NOx index, daily max", "noxIndex", None, "max"),
    ]

    fig, axes = plt.subplots(
        len(panels), 1, figsize=(12.5, 14), sharex=True, constrained_layout=True
    )
    fig.set_facecolor(SURFACE)

    for ax, (ylabel, col, outdoor, agg) in zip(axes, panels):
        style_axis(ax, ylabel)
        stat = d[col].mean() if agg == "mean" else d[col].max()
        if agg == "mean":
            ax.fill_between(
                d[col].min().index, d[col].min(), d[col].max(),
                color=BLUE, alpha=0.18, linewidth=0,
            )
        ax.plot(stat.index, stat, color=BLUE, linewidth=1.8,
                label=f"indoor daily {agg}")
        if outdoor is not None:
            od = outdoor.resample("D").mean() if agg == "mean" else outdoor.resample("D").max()
            ax.plot(od.index, od, color=GREEN, linewidth=1.2, alpha=0.9,
                    label=f"outdoor daily {agg}")
            ax.legend(loc="upper left", fontsize=8, frameon=False,
                      labelcolor=SECONDARY)
        for label, s, e in EVENTS:
            ax.axvspan(pd.Timestamp(s, tz=TZ), pd.Timestamp(e, tz=TZ),
                       color="#eda100", alpha=0.14, linewidth=0)
        ax.axvline(RETENTION_EDGE, color=MUTED, linewidth=0.9, linestyle=":")

    # event letters on the top panel
    top = axes[0]
    for label, s, e in EVENTS:
        mid = pd.Timestamp(s, tz=TZ) + (pd.Timestamp(e, tz=TZ) - pd.Timestamp(s, tz=TZ)) / 2
        top.annotate(label, (mid, 1.02), xycoords=("data", "axes fraction"),
                     ha="center", fontsize=10, color=SECONDARY, fontweight="bold")
    top.annotate("hourly-only ⟵ ⟶ 5-min data", (RETENTION_EDGE, 1.02),
                 xycoords=("data", "axes fraction"), ha="right", fontsize=8,
                 color=MUTED)

    axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.suptitle(
        "CB 154 (Vertical Cloud Lab @ BYU) — full AirGradient history vs outdoor conditions\n"
        "Feb 5 – Jul 18, 2026 · indoor = blue · outdoor (Open-Meteo, Provo) = green\n"
        "A dust storm · B dehumidifier test 1 · C wildfire smoke · D fireworks · E dehumidifier test 2",
        fontsize=10.5, color=INK,
    )
    out = HERE / "cb154_holistic_overview.png"
    fig.savefig(out, dpi=140, facecolor=SURFACE)
    print("wrote", out)

    # indoor RH vs outdoor dew point (the moisture driver)
    fig2, ax2 = plt.subplots(figsize=(6.4, 5.4), constrained_layout=True)
    fig2.set_facecolor(SURFACE)
    style_axis(ax2, "Indoor RH, daily mean (%)")
    ax2.set_xlabel("Outdoor dew point, daily mean (°C)", color=SECONDARY, fontsize=10)
    rh = d["rhum"].mean()
    dp = w["dew_point_2m"].resample("D").mean()
    j = pd.concat([rh.rename("rh"), dp.rename("dp")], axis=1, sort=False).dropna()
    months = j.index.month
    # sequential blue ramp steps 250->700 by month (Feb..Jul)
    ramp = ["#86b6ef", "#5598e7", "#2a78d6", "#256abf", "#1c5cab", "#0d366b"]
    for m, c in zip(range(2, 8), ramp):
        sel = j[months == m]
        ax2.scatter(sel["dp"], sel["rh"], s=22, color=c,
                    label=dt.date(2026, m, 1).strftime("%b"), edgecolors=SURFACE,
                    linewidths=0.8)
    r = j.corr().iloc[0, 1]
    ax2.legend(fontsize=8, frameon=False, labelcolor=SECONDARY, title="month",
               title_fontsize=8)
    ax2.set_title(
        f"Lab humidity is driven by outdoor moisture (r = {r:.2f})",
        fontsize=11, color=INK,
    )
    out2 = HERE / "cb154_rh_vs_outdoor_dewpoint.png"
    fig2.savefig(out2, dpi=140, facecolor=SURFACE)
    print("wrote", out2)


if __name__ == "__main__":
    main()
