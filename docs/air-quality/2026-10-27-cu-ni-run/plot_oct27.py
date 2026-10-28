"""AirGradient (CB 154, inside the atomizer enclosure) on 2026-10-27, with the
Cu70/Ni30 run's events from Gage's videos. One measure per panel, one time axis.

    python plot_oct27.py airgradient_raw.csv airgradient_2026-10-27.png
"""
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

RAW, OUT = sys.argv[1], sys.argv[2]
TZ = "America/Denver"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, SECONDARY, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE, SURFACE, BAND = "#e1e0d9", "#c3c2b7", "#fcfcfb", "#f0efec"

r = pd.read_csv(RAW, parse_dates=["timestamp"])
r = r.set_index(r.timestamp.dt.tz_convert(TZ)).sort_index()
day = "2026-10-27"
T = lambda hm: pd.Timestamp(f"{day} {hm}", tz=TZ)
t0, t1 = T("13:30"), T("17:30")
s = r.loc[t0:t1]

# Video coverage. V4 is pinned to about +-45 s by the CO2 value Gage reads off the
# monitor at 23:11 (486 ppm, logged at 16:56:45); V5 is matched to V4 by the same
# lines; V3 ends just before V4 starts; V1 ends at least 34 min before Ronnie's
# #219 post (14:20:01), since the post quotes things said at 33:07 and 34:03.
videos = [("Video 1", T("13:45"), T("14:45:40")), ("Video 3", T("15:47:45"), T("16:32:40")),
          ("Video 4", T("16:33:30"), T("16:58:45")), ("Video 5 (Audrey)", T("16:40:50"), T("16:53:05"))]
atomizing = (T("16:48:30"), T("16:53:00"))
events = [  # (time, label); numbered in order
    (T("13:50:30"), "BN-coated crucible brought in (V1 ~5:00)"),
    (T("14:04"), "Cu-Ni rods washed (V1 19:02)"),
    (T("14:09"), "IPA on the seal (V1 24:15)"),
    (T("16:19"), "unplugged cooling-water line reconnected (V3 31:00)"),
    (T("16:24:37"), "500 °C: smoke in the furnace; \"Something smells weird\" (V3 36:52)"),
    (T("16:30:25"), "gas wash to clear it: \"almost smells like fish\" (V3 42:40)"),
    (T("16:39"), "heat to 1,300 °C (V4 5:23)"),
    (T("16:44:50"), "melting: \"It smells like fish\" (V4 11:21)"),
    (T("16:51:07"), "atomizing: \"You can really smell it though\" (V4 17:37)"),
    (T("16:56:00"), "alert e-mail; \"it smells weird in here\" (V4 23:02)"),
]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5,
                     "axes.edgecolor": BASELINE, "axes.labelcolor": SECONDARY,
                     "xtick.color": MUTED, "ytick.color": MUTED})
fig = plt.figure(figsize=(11, 11.0), facecolor=SURFACE)
gs = fig.add_gridspec(6, 1, height_ratios=[0.8, 2, 2, 1.6, 0.42, 1.25], hspace=0.13)
ev = fig.add_subplot(gs[0]); ax_voc = fig.add_subplot(gs[1], sharex=ev)
ax_pm = fig.add_subplot(gs[2], sharex=ev); ax_co2 = fig.add_subplot(gs[3], sharex=ev)
key = fig.add_subplot(gs[5])
for ax in (ev, ax_voc, ax_pm, ax_co2):
    ax.set_facecolor(SURFACE)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.tick_params(length=0)
    for t, _ in events:
        ax.axvline(t, color=MUTED, lw=0.7, ls=(0, (2, 3)), zorder=0)
for ax in (ax_voc, ax_pm, ax_co2):
    ax.axvspan(*atomizing, color=BAND, zorder=-1, lw=0)
    plt.setp(ax.get_xticklabels(), visible=ax is ax_co2)
plt.setp(ev.get_xticklabels(), visible=False)

# Events strip: what each video covers, and the event numbers.
ev.set_ylim(0, 4.0); ev.set_yticks([]); ev.grid(False); ev.spines["left"].set_visible(False)
for i, (name, a, b) in enumerate(videos):
    y = 0.4 + 0.62 * (i if i < 3 else 2.0) + (0.62 if i == 3 else 0)
    ev.barh(y, b - a, left=a, height=0.42, color=BAND, edgecolor=BASELINE, lw=0.6)
    ev.text(a if i < 3 else b, y, f" {name} " , va="center", ha="left" if i < 3 else "left",
            fontsize=7.5, color=SECONDARY)
for k, (t, _) in enumerate(events, 1):
    y = 3.05 + 0.7 * ((k + 1) % 2) if k >= 4 else 3.4
    ev.text(t, y, str(k), fontsize=8, color=INK, ha="center", va="center", fontweight="bold",
            bbox=dict(boxstyle="circle,pad=0.18", fc=SURFACE, ec=MUTED, lw=0.7))
ev.set_title("CB 154 AirGradient, inside the atomizer enclosure, 27 Oct 2026: the Cu70/Ni30 run",
             loc="left", fontsize=11.5, color=INK, pad=6)

ax_voc.plot(s.index, s.tvocIndex, color=BLUE, lw=1.6)
ax_voc.axhline(500, color=BASELINE, lw=1)
ax_voc.text(t1, 503, "500 = top of scale ", ha="right", va="bottom", fontsize=7.5, color=MUTED)
ax_voc.set_ylim(0, 560); ax_voc.set_ylabel("TVOC index\n(100 = sensor's 24 h average)")

ax_pm.plot(s.index, s.pm02_corrected, color=ORANGE, lw=1.6, label="corrected, which the alert uses (0.02 × the 0.3 µm count)")
ax_pm.plot(s.index, s.pm02, color=AQUA, lw=1.6, label="raw sensor mass")
ax_pm.axhline(5, color=SECONDARY, lw=0.9, ls=(0, (5, 3)))
ax_pm.text(t0, 5.15, " 5 µg/m³ alert threshold (WHO annual guideline)", fontsize=7.5, color=SECONDARY, va="bottom")
ax_pm.set_ylim(0, 10); ax_pm.set_ylabel("PM2.5, µg/m³")
ax_pm.legend(loc="upper left", bbox_to_anchor=(0.0, 0.92), frameon=False, fontsize=8)
pk = s.pm02_corrected.idxmax()
ax_pm.annotate(f"{s.pm02_corrected.max():.1f} at {pk:%H:%M}", (pk, s.pm02_corrected.max()),
               xytext=(8, -2), textcoords="offset points", fontsize=7.8, color=INK, va="center")
ax_pm.text(atomizing[0], 9.6, "atomizing ", ha="right", va="top", fontsize=7.5, color=MUTED)

ax_co2.plot(s.index, s.rco2, color=BLUE, lw=1.6)
ax_co2.set_ylim(380, 620); ax_co2.set_ylabel("CO₂, ppm")
ax_co2.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30], tz=s.index.tz))
ax_co2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=s.index.tz))
ax_co2.set_xlim(t0, t1)
ax_co2.set_xlabel("Mountain Daylight Time (UTC−6); the monitor logs one reading a minute")

key.axis("off")
half = (len(events) + 1) // 2
for k, (t, lab) in enumerate(events, 1):
    col, row = (0, k - 1) if k <= half else (1, k - 1 - half)
    key.text(0.0 + 0.5 * col, 0.95 - row * 0.2, f"{k}", fontsize=8, fontweight="bold", color=INK,
             transform=key.transAxes, va="top")
    key.text(0.028 + 0.5 * col, 0.95 - row * 0.2, f"{t:%H:%M}  {lab}", fontsize=7.8, color=SECONDARY,
             transform=key.transAxes, va="top")
fig.savefig(OUT, dpi=150, bbox_inches="tight", facecolor=SURFACE)
print("wrote", OUT)
