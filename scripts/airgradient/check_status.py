"""Status check for the CB 154 AirGradient monitor (issue #42).

Reports when the monitor last uploaded, every offline span and restart, and
how its humidity compares with what outdoor moisture predicts for the room,
then plots it. The prediction is there because there is only one monitor:
since Sep 29 it sits in the dehumidified enclosure, so "expected room RH" is
the stand-in for the room reading it can no longer take.

API notes (see also the full-history script on claude/issue-42-20260718-1733):
  - Auth: `token` query param, read from the AIRGRADIENT_API_KEY env var. The
    request URL carries the token, so errors report the path only.
  - measures/current returns the *last* reading with its timestamp, even when
    the monitor has been offline for days. Check the timestamp.
  - measures/past serves 5-minute buckets for 150 days, max 10 days per call.
  - measures/raw serves every upload (about one a minute), max 200 records
    and 2 days per call. A restart shows up there as an upload with no sensor
    values. The 5-minute buckets usually average it away.
  - After a restart the TVOC index starts over near 100.

Usage:
    AIRGRADIENT_API_KEY=... python check_status.py [--since 2026-07-18]
        [--zoom-from "2026-09-29 12:00"]
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

# (local time, label); restarts are found in the raw uploads and marked on
# their own. Sep 29: Sterling plugged in and switched on the Quest 155 (pump
# unplugged) while the monitor was offline. It came back at a 3:55 pm restart,
# and after a second restart at 5:36 pm its Wi-Fi signal changed, which fits
# Sterling moving it into the enclosure "around 5:00 pm".
EVENTS = [("2026-09-29 13:30", "~1:30 pm,\ndehumidifier on")]
# Room baseline ends here. Only earlier readings go into the room fit, and
# later ones are drawn as "dehumidifier on".
ROOM_UNTIL = "2026-09-29 13:30"

MEASURES = [
    "timestamp", "pm01", "pm02", "pm10", "pm01_corrected", "pm02_corrected",
    "pm10_corrected", "pm003Count", "atmp", "rhum", "rco2", "atmp_corrected",
    "rhum_corrected", "rco2_corrected", "tvoc", "tvocIndex", "noxIndex",
    "wifi", "datapoints",
]
SENSORS = ["atmp", "rhum", "rco2", "pm02"]

# palette (dataviz skill reference, light mode; slots 1-3 validated all-pairs)
BLUE = "#2a78d6"  # room
ORANGE = "#eb6834"  # dehumidifier on
AQUA = "#1baf7a"  # outdoor
INK = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"
OFFLINE = "#f0efec"


def api_get(path: str, empty_if_404: bool = False, **params) -> object:
    r = requests.get(
        f"{API_BASE}{path}",
        params={"token": os.environ["AIRGRADIENT_API_KEY"], **params},
        timeout=180,
    )
    if r.status_code == 404 and empty_if_404:
        return []
    if not r.ok:
        raise RuntimeError(f"AirGradient {path} returned HTTP {r.status_code}")
    return r.json()


def api_time(t: dt.datetime) -> str:
    return t.strftime("%Y%m%dT%H%M%SZ")


def fetch_indoor(start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
    rows, cur = [], start
    while cur < end:
        to = min(cur + dt.timedelta(days=10), end)
        rows += api_get(f"/locations/{LOCATION_ID}/measures/past",
                        **{"from": api_time(cur), "to": api_time(to)})
        cur = to
    df = pd.DataFrame(rows)[MEASURES].drop_duplicates(subset="timestamp")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def fetch_raw(start: dt.datetime, end: dt.datetime) -> pd.DataFrame:
    # 3 h per call stays under the 200-record cap at one upload a minute.
    # A window with no uploads (the monitor offline) comes back as a 404.
    rows, cur = [], start
    while cur < end:
        to = min(cur + dt.timedelta(hours=3), end)
        rows += api_get(f"/locations/{LOCATION_ID}/measures/raw",
                        empty_if_404=True,
                        **{"from": api_time(cur), "to": api_time(to)})
        cur = to
    df = pd.DataFrame(rows)[MEASURES[:-1] + ["firmwareVersion"]]
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.drop_duplicates(subset="timestamp").sort_values("timestamp")


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


def dbm(v: float) -> str:
    return "n/a" if np.isnan(v) else f"{v:.0f}".replace("-", "\N{MINUS SIGN}")


def restarts(raw: pd.DataFrame, spans: list) -> list:
    """(time, label) for each boot, i.e. each upload with no sensor values.

    Back-to-back empty uploads count as one boot. The label notes a boot that
    ended an outage, or a Wi-Fi signal shift across it (a sign of a move).
    """
    raw = raw.set_index("timestamp")
    empty = raw[SENSORS].isna().all(axis=1)
    boots = raw.index[empty].to_series()
    boots = boots[boots.diff().isna() | (boots.diff() > GAP)]
    wifi = raw.loc[~empty, "wifi"]
    half_hour = pd.Timedelta("30min")
    out = []
    for t in boots:
        local = t.tz_convert(TZ)
        label = f"{local:%-I:%M %p} restart".replace("AM", "am").replace("PM", "pm")
        before = wifi.loc[t - half_hour:t].median()
        after = wifi.loc[t:t + half_hour].median()
        if any(b is not None and abs(t - b) < BUCKET for _, b in spans):
            label += ",\nback online"
        elif abs(after - before) >= 3:
            label += f",\nWi-Fi {dbm(before)} \N{RIGHTWARDS ARROW} {dbm(after)} dBm"
        print(f"restart: {local:%Y-%m-%d %H:%M:%S}  Wi-Fi median "
              f"{dbm(before)} dBm before, {dbm(after)} dBm after")
        out.append((local, label))
    return out


def style_axis(ax, ylabel):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.set_ylabel(ylabel, color=SECONDARY, fontsize=10)


def step_to(series: pd.Series, x_end, x_start=None) -> pd.Series:
    """Daily values as a step line carried out to x_end."""
    s = series.dropna()
    s = s[s.index <= x_end]
    if x_start is not None:  # keep y autoscaling to the days on show
        s = s[s.index >= x_start.floor("D")]
    s[x_end] = s.iloc[-1]
    return s


def shade_offline(axes, spans, x_end, label_ax=None, y=0.97):
    for a, b in spans:
        a, b = a.tz_convert(TZ), (x_end if b is None else b.tz_convert(TZ))
        for ax in axes:
            ax.axvspan(a, b, color=OFFLINE, linewidth=0, zorder=0)
        if label_ax is not None:
            left, right = (mdates.num2date(v, tz=TZ) for v in label_ax.get_xlim())
            a, b = max(a, left), min(b, right)
            if a < b:
                label_ax.annotate("offline", (a + (b - a) / 2, y),
                                  xycoords=("data", "axes fraction"),
                                  ha="center", va="top", fontsize=9,
                                  color=SECONDARY)


def mark_events(axes, events, label_ax, y, ha, dx):
    for t, label in events:
        for ax in axes:
            ax.axvline(t, color=SECONDARY, linewidth=1)
        label_ax.annotate(label, (t, y), xycoords=("data", "axes fraction"),
                          xytext=(dx, 0), textcoords="offset points", ha=ha,
                          va="top" if y > 0.5 else "bottom", fontsize=9,
                          color=SECONDARY)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-07-18")
    ap.add_argument("--zoom-from", default="2026-09-29 12:00",
                    help="local start of the close-up figure")
    args = ap.parse_args()
    start = pd.Timestamp(args.since, tz=TZ).tz_convert("UTC").to_pydatetime()
    zoom_from = pd.Timestamp(args.zoom_from, tz=TZ)
    room_until = pd.Timestamp(ROOM_UNTIL, tz=TZ)
    now = pd.Timestamp.now(tz="UTC")

    current = api_get("/locations/measures/current")
    current = next(c for c in current if c["locationId"] == LOCATION_ID)
    last_seen = pd.Timestamp(current["timestamp"])
    print(f"last upload {last_seen.tz_convert(TZ):%a %b %d %H:%M:%S %Z} "
          f"({(now - last_seen).total_seconds() / 3600:.1f} h ago), "
          f"firmware {current['firmwareVersion']}, wifi {current['wifi']} dBm")

    df = fetch_indoor(start, now.to_pydatetime())
    raw = fetch_raw(zoom_from.tz_convert("UTC").to_pydatetime(),
                    now.to_pydatetime())
    w = fetch_outdoor(start, now)
    w = w[w["time"] <= now]  # the API also returns today's forecast hours
    stem = f"{start:%Y%m%d}_{now:%Y%m%d}"
    df.to_csv(HERE / f"cb154_5min_{stem}.csv.gz", index=False)
    raw.to_csv(HERE / f"cb154_raw_{zoom_from:%Y%m%d}_{now:%Y%m%d}.csv.gz",
               index=False)
    w.to_csv(HERE / f"provo_weather_hourly_{stem}.csv", index=False)

    spans = offline_spans(df, last_seen, now)
    for a, b in spans:
        end = b.tz_convert(TZ) if b is not None else "still offline"
        dur = (b if b is not None else now) - a
        print(f"offline: {a.tz_convert(TZ):%Y-%m-%d %H:%M} -> {end}  ({dur})")
    boots = restarts(raw, spans)

    df = df.set_index("timestamp").tz_convert(TZ)
    df["dew"] = dew_point(df["atmp"], df["rhum"])
    w = w.set_index("time").tz_convert(TZ)
    hourly = df[["rhum", "atmp", "dew"]].resample("1h").mean()
    room = hourly[hourly.index < room_until]

    # Room dew point follows outdoor dew point (the room's air is replaced
    # fast: CO2 sits near outdoor levels), so fit daily means of the room
    # baseline and turn the prediction back into RH at the room's last
    # measured temperature.
    daily = room.resample("D").mean().join(
        w["dew_point_2m"].resample("D").mean().rename("out_dew"), how="outer")
    full = room["rhum"].resample("D").count() >= 20
    fit = daily[full.reindex(daily.index, fill_value=False)].dropna()
    slope, icept = np.polyfit(fit["out_dew"], fit["dew"], 1)
    r = np.corrcoef(fit["out_dew"], fit["dew"])[0, 1]
    daily["expected_dew"] = slope * daily["out_dew"] + icept
    daily["room_t"] = daily["atmp"].ffill()
    daily["expected_rh"] = rh_at(daily["expected_dew"], daily["room_t"])
    resid = fit["rhum"] - daily.loc[fit.index, "expected_rh"]
    print(f"room dew = {slope:.2f} x outdoor dew + {icept:.1f} C "
          f"(daily r = {r:.3f}, n = {len(fit)} days); expected RH is "
          f"within +/-{resid.std():.1f}% (1 sd)")
    print(daily[["rhum", "expected_rh", "expected_dew", "out_dew"]]
          .tail(7).round(1).to_string())

    after = df[df.index >= room_until].copy()
    after["expected_dew"] = daily["expected_dew"].reindex(
        after.index, method="ffill")
    after["room_rh"] = daily["expected_rh"].reindex(after.index, method="ffill")
    print("since the dehumidifier went on (monitor vs expected room):")
    print(after[["rhum", "atmp", "dew", "room_rh", "expected_dew"]]
          .resample("1h").mean().round(1).to_string())

    x_end = now.tz_convert(TZ) + pd.Timedelta("12h")
    events = [(pd.Timestamp(t, tz=TZ), label) for t, label in EVENTS]
    plot_overview(hourly, room_until, daily, w, spans, events, resid, x_end,
                  last_seen, now)
    plot_zoom(df, room_until, daily, spans, events + boots, resid, zoom_from,
              now)


def plot_overview(hourly, room_until, daily, w, spans, events, resid, x_end,
                  last_seen, now):
    fig, (ax_rh, ax_dp) = plt.subplots(
        2, 1, figsize=(11.5, 7), sharex=True, constrained_layout=True)
    fig.set_facecolor(SURFACE)
    style_axis(ax_rh, "Relative humidity (%)")
    style_axis(ax_dp, "Dew point (\N{DEGREE SIGN}C)")

    room = hourly.index < room_until
    ax_rh.plot(hourly.index[room], hourly["rhum"][room], color=BLUE,
               linewidth=1.4, label="room (AirGradient, hourly)")
    ax_rh.plot(hourly.index[~room], hourly["rhum"][~room], color=ORANGE,
               linewidth=1.4, label="dehumidifier on")
    expected = step_to(daily["expected_rh"], x_end)
    ax_rh.step(expected.index, expected, where="post", color=MUTED,
               linewidth=1.2,
               label=f"room, expected from outdoor dew point (daily, ±{resid.std():.0f}%)")
    ax_dp.plot(hourly.index[room], hourly["dew"][room], color=BLUE,
               linewidth=1.4, label="room")
    ax_dp.plot(hourly.index[~room], hourly["dew"][~room], color=ORANGE,
               linewidth=1.4, label="dehumidifier on")
    out_dew = w["dew_point_2m"].rolling(24, center=True, min_periods=12).mean()
    ax_dp.plot(out_dew.index, out_dew, color=AQUA, linewidth=1.4,
               label="outdoor, Provo (24 h mean, Open-Meteo)")

    ax_dp.set_xlim(hourly.index[0], x_end)
    shade_offline((ax_rh, ax_dp), spans, x_end, label_ax=ax_rh)
    mark_events((ax_rh, ax_dp), events, ax_rh, 0.04, "right", -6)

    for ax in (ax_rh, ax_dp):
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1), ncol=3,
                  fontsize=8.5, frameon=False, labelcolor=SECONDARY)
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


def plot_zoom(df, room_until, daily, spans, events, resid, zoom_from, now):
    x_end = now.tz_convert(TZ) + pd.Timedelta("30min")
    win = df[df.index >= zoom_from]
    last_room = df.index[df.index < room_until][-1]
    fig, axes = plt.subplots(3, 1, figsize=(11.5, 9), sharex=True,
                             constrained_layout=True)
    fig.set_facecolor(SURFACE)
    panels = [
        ("Relative humidity (%)", "rhum", "expected_rh",
         f"room, expected from outdoor dew point (±{resid.std():.0f}%)"),
        ("Temperature (\N{DEGREE SIGN}C)", "atmp", "room_t",
         f"room, last measured ({last_room:%b %d})"),
        ("Dew point (\N{DEGREE SIGN}C)", "dew", "expected_dew",
         "room, expected from outdoor dew point"),
    ]
    room = win.index < room_until
    for ax, (ylabel, col, ref_col, ref_label) in zip(axes, panels):
        style_axis(ax, ylabel)
        if room.any():
            ax.plot(win.index[room], win[col][room], color=BLUE,
                    linewidth=1.4, label="room")
        ax.plot(win.index[~room], win[col][~room], color=ORANGE,
                linewidth=1.4, label="monitor, dehumidifier on")
        ref = step_to(daily[ref_col], x_end, x_start=zoom_from)
        ax.step(ref.index, ref, where="post", color=MUTED, linewidth=1.2,
                label=ref_label)
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1), ncol=2,
                  fontsize=8.5, frameon=False, labelcolor=SECONDARY)
    axes[-1].set_xlim(zoom_from, x_end)
    lo, hi = axes[0].get_ylim()
    axes[0].set_ylim(lo, hi + 0.2 * (hi - lo))  # room for the event labels
    shade_offline(axes, spans, x_end, label_ax=axes[0], y=0.5)
    mark_events(axes, events, axes[0], 0.97, "left", 4)
    axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=2, tz=TZ))
    axes[-1].xaxis.set_major_formatter(
        lambda x, _: f"{mdates.num2date(x, tz=TZ):%-I %p}".lower())
    fig.suptitle(
        f"CB 154 AirGradient, {zoom_from:%b %d, %-I %p} to "
        f"{now.tz_convert(TZ):%-I:%M %p}".replace("AM", "am").replace("PM", "pm")
        + ": after the dehumidifier went on. 5-minute means. "
        "America/Denver time.",
        x=0.01, ha="left", fontsize=11, color=INK)

    out = HERE / f"cb154_enclosure_{now:%Y%m%d}.png"
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print("wrote", out)


if __name__ == "__main__":
    main()
