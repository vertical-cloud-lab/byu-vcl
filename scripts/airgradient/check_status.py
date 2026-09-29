"""Status check for the CB 154 AirGradient monitor (issue #42).

Reports when the monitor last uploaded, every offline span since --since, and
how the room's humidity compares with what outdoor moisture predicts, then
plots it. The prediction is there because there is only one monitor: once it
moves into the dehumidified enclosure, "expected room RH" is the stand-in for
the room reading it can no longer take.

API notes (see also the full-history script on claude/issue-42-20260718-1733):
  - Auth: `token` query param, read from the AIRGRADIENT_API_KEY env var. The
    request URL carries the token, so errors report the path only.
  - measures/current returns the *last* reading with its timestamp, even when
    the monitor has been offline for days. Check the timestamp.
  - measures/past serves 5-minute buckets for 150 days, max 10 days per call.
  - A reboot shows up as a bucket with datapoints=1 and null sensor fields,
    followed by a TVOC index restarting near 100.

Usage:
    AIRGRADIENT_API_KEY=... python check_status.py [--since 2026-07-18]
"""

import argparse
import datetime as dt
import os
import time
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).parent
API_BASE = "https://api.airgradient.com/public/api/v1"
LOCATION_ID = 184200  # "CB 154"
LAT, LON = 40.246, -111.649  # BYU campus, Provo, UT
TZ = "America/Denver"
GAP = pd.Timedelta("15min")
BUCKET = pd.Timedelta("5min")

# (local time, label). Sep 29: Sterling plugged in and switched on the Quest
# 155 (pump unplugged); AirGradient still at its old spot outside the enclosure.
EVENTS = [("2026-09-29 13:30", "dehumidifier on\n~1:30 pm Sep 29")]

MEASURES = [
    "timestamp", "pm01", "pm02", "pm10", "pm01_corrected", "pm02_corrected",
    "pm10_corrected", "pm003Count", "atmp", "rhum", "rco2", "atmp_corrected",
    "rhum_corrected", "rco2_corrected", "tvoc", "tvocIndex", "noxIndex",
    "wifi", "datapoints",
]

# palette (dataviz skill reference, light mode)
BLUE = "#2a78d6"  # room
GREEN = "#008300"  # outdoor
INK = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"
OFFLINE = "#f0efec"


def api_get(path: str, **params) -> object:
    r = requests.get(
        f"{API_BASE}{path}",
        params={"token": os.environ["AIRGRADIENT_API_KEY"], **params},
        timeout=180,
    )
    if not r.ok:
        raise RuntimeError(f"AirGradient {path} returned HTTP {r.status_code}")
    return r.json()


def fetch_indoor(start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
    rows, cur = [], start
    while cur < end:
        to = min(cur + dt.timedelta(days=10), end)
        rows += api_get(
            f"/locations/{LOCATION_ID}/measures/past",
            **{"from": cur.strftime("%Y%m%dT%H%M%SZ"),
               "to": to.strftime("%Y%m%dT%H%M%SZ")},
        )
        cur = to
    df = pd.DataFrame(rows)[MEASURES].drop_duplicates(subset="timestamp")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def fetch_outdoor(start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
    # Historical-forecast API: the high-resolution models, archived, through
    # today. Its daily dew point tracks the room better (r 0.975) than the
    # ERA5 archive API's (0.962), which ran 1-8 C wetter over Provo.
    for attempt in range(4):  # Open-Meteo times out now and then from CI
        try:
            r = requests.get(
                "https://historical-forecast-api.open-meteo.com/v1/forecast",
                params=dict(latitude=LAT, longitude=LON, timezone="UTC",
                            start_date=f"{start:%Y-%m-%d}",
                            end_date=f"{end:%Y-%m-%d}",
                            hourly="temperature_2m,relative_humidity_2m,dew_point_2m"),
                timeout=60,
            )
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(20 * (attempt + 1))
    w = pd.DataFrame(r.json()["hourly"])
    w["time"] = pd.to_datetime(w["time"]).dt.tz_localize("UTC")
    return w


def dew_point(t, rh):
    b, c = 17.62, 243.12  # Magnus, over water
    g = np.log(rh / 100) + b * t / (c + t)
    return c * g / (b - g)


def rh_at(td, t):
    b, c = 17.62, 243.12
    return 100 * np.exp(b * td / (c + td) - b * t / (c + t))


def offline_spans(df: pd.DataFrame, last_seen: pd.Timestamp,
                  now: pd.Timestamp) -> list:
    ts = df["timestamp"]
    spans = [(ts[i - 1] + BUCKET, ts[i]) for i in df.index[ts.diff() > GAP]]
    if now - last_seen > GAP:
        spans.append((last_seen, None))  # still offline
    return spans


def style_axis(ax, ylabel):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.set_ylabel(ylabel, color=SECONDARY, fontsize=10)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-07-18")
    args = ap.parse_args()
    start = pd.Timestamp(args.since, tz=TZ).tz_convert("UTC").to_pydatetime()
    now = pd.Timestamp.now(tz="UTC")

    current = api_get("/locations/measures/current")
    current = next(c for c in current if c["locationId"] == LOCATION_ID)
    last_seen = pd.Timestamp(current["timestamp"])
    print(f"last upload {last_seen.tz_convert(TZ):%a %b %d %H:%M:%S %Z} "
          f"({(now - last_seen).total_seconds() / 3600:.1f} h ago), "
          f"firmware {current['firmwareVersion']}, wifi {current['wifi']} dBm")

    df = fetch_indoor(start, now.to_pydatetime())
    w = fetch_outdoor(start, now)
    stem = f"{start:%Y%m%d}_{now:%Y%m%d}"
    df.to_csv(HERE / f"cb154_5min_{stem}.csv.gz", index=False)
    w.to_csv(HERE / f"provo_weather_hourly_{stem}.csv", index=False)

    spans = offline_spans(df, last_seen, now)
    for a, b in spans:
        end = b.tz_convert(TZ) if b is not None else "still offline"
        dur = (b if b is not None else now) - a
        print(f"offline: {a.tz_convert(TZ):%Y-%m-%d %H:%M} -> {end}  ({dur})")

    df = df.set_index("timestamp").tz_convert(TZ)
    df["dew"] = dew_point(df["atmp"], df["rhum"])
    w = w.set_index("time").tz_convert(TZ)
    hourly = df[["rhum", "atmp", "dew"]].resample("1h").mean()

    # Room dew point follows outdoor dew point (the room's air is replaced
    # fast: CO2 sits near outdoor levels), so fit daily means and turn the
    # prediction back into RH at the room's temperature, carried forward
    # through outages.
    daily = hourly.resample("D").mean().join(
        w["dew_point_2m"].resample("D").mean().rename("out_dew"), how="outer")
    full = hourly["rhum"].resample("D").count() >= 20
    fit = daily[full.reindex(daily.index, fill_value=False)].dropna()
    slope, icept = np.polyfit(fit["out_dew"], fit["dew"], 1)
    r = np.corrcoef(fit["out_dew"], fit["dew"])[0, 1]
    daily["expected_rh"] = rh_at(slope * daily["out_dew"] + icept,
                                 daily["atmp"].ffill())
    resid = fit["rhum"] - daily.loc[fit.index, "expected_rh"]
    print(f"room dew = {slope:.2f} x outdoor dew + {icept:.1f} C "
          f"(daily r = {r:.3f}, n = {len(fit)} days); expected RH is "
          f"within +/-{resid.std():.1f}% (1 sd)")
    print(daily[["rhum", "expected_rh", "out_dew"]].tail(7).round(1).to_string())

    x_end = now.tz_convert(TZ) + pd.Timedelta("12h")
    fig, (ax_rh, ax_dp) = plt.subplots(
        2, 1, figsize=(11.5, 7), sharex=True, constrained_layout=True)
    fig.set_facecolor(SURFACE)
    style_axis(ax_rh, "Relative humidity (%)")
    style_axis(ax_dp, "Dew point (\N{DEGREE SIGN}C)")

    ax_rh.plot(hourly.index, hourly["rhum"], color=BLUE, linewidth=1.4,
               label="room (AirGradient, hourly)")
    expected = daily["expected_rh"].dropna()
    expected[x_end] = expected.iloc[-1]  # carry the last day to the edge
    ax_rh.step(expected.index, expected, where="post", color=MUTED,
               linewidth=1.2,
               label=f"expected from outdoor dew point (daily, ±{resid.std():.0f}%)")
    ax_dp.plot(hourly.index, hourly["dew"], color=BLUE, linewidth=1.4,
               label="room")
    out_dew = w["dew_point_2m"].rolling(24, center=True, min_periods=12).mean()
    ax_dp.plot(out_dew.index, out_dew, color=GREEN, linewidth=1.4,
               label="outdoor, Provo (24 h mean, Open-Meteo)")

    for a, b in spans:
        a, b = a.tz_convert(TZ), (x_end if b is None else b.tz_convert(TZ))
        for ax in (ax_rh, ax_dp):
            ax.axvspan(a, b, color=OFFLINE, linewidth=0, zorder=0)
        ax_rh.annotate("offline", (a + (b - a) / 2, 0.97),
                       xycoords=("data", "axes fraction"), ha="center",
                       va="top", fontsize=9, color=SECONDARY)
    for when, label in EVENTS:
        t = pd.Timestamp(when, tz=TZ)
        for ax in (ax_rh, ax_dp):
            ax.axvline(t, color=SECONDARY, linewidth=1)
        ax_rh.annotate(label, (t, 0.04), xycoords=("data", "axes fraction"),
                       xytext=(-6, 0), textcoords="offset points", ha="right",
                       va="bottom", fontsize=9, color=SECONDARY)

    for ax in (ax_rh, ax_dp):
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1), ncol=2,
                  fontsize=8.5, frameon=False, labelcolor=SECONDARY)
    ax_dp.set_xlim(hourly.index[0], x_end)
    ax_dp.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, tz=TZ))
    ax_dp.xaxis.set_major_formatter(mdates.DateFormatter("%b %d", tz=TZ))
    status = (f"no uploads since {last_seen.tz_convert(TZ):%a %b %d, %H:%M}"
              if now - last_seen > GAP else "online")
    fig.suptitle(
        f"CB 154 AirGradient, {hourly.index[0]:%b %d} \N{EN DASH} "
        f"{now.tz_convert(TZ):%b %d, %Y}: {status}. "
        "Hourly means, America/Denver time.",
        x=0.01, ha="left", fontsize=11, color=INK)

    out = HERE / f"cb154_status_{now:%Y%m%d}.png"
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print("wrote", out)


if __name__ == "__main__":
    main()
