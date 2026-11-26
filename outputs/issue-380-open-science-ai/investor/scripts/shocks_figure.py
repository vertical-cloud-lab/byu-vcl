#!/usr/bin/env python3
"""Two shocks to open-science business models: US science money held but awards fell (top), and AI cut the
human-attention funnel open-source companies sell through (bottom)."""
import pandas as pd, matplotlib.pyplot as plt, matplotlib.dates as mdates
from viz import style, OPEN, CLOSED, THIRD, INK, INK2, MUTED, SURFACE
style()
f = pd.read_csv("data/us_science_funding.csv")
so = pd.read_csv("data/stackoverflow_monthly_questions.csv", parse_dates=["month"])
fig, axs = plt.subplots(2, 2, figsize=(12, 8.2), gridspec_kw={"hspace": 0.55, "wspace": 0.28})
C = {"NSF": OPEN, "NIH": CLOSED, "DOE Office of Science": THIRD}
# (a) appropriations indexed to FY2024, with the FY2026 requests
ax = axs[0, 0]
for ag, col in C.items():
    a = f[(f.agency == ag) & (f.measure == "appropriation")].sort_values("fy")
    base = a.value.iloc[0]
    ax.plot(a.fy, a.value / base * 100, color=col, lw=2, marker="o", ms=6)
    r = f[(f.agency == ag) & (f.measure == "request")]
    ax.scatter(r.fy, r.value / base * 100, s=60, facecolor=SURFACE, edgecolor=col, linewidth=2, zorder=3)
    dy = {"NSF": -7, "NIH": 2, "DOE Office of Science": 11}[ag]
    ax.annotate(ag.replace(" Office of Science", " Science"), (2026, a.value.iloc[-1] / base * 100), xytext=(8, dy),
                textcoords="offset points", va="center", fontsize=9, color=INK2)
ax.text(2025.05, 47, "hollow: FY2026\nPresident's request", fontsize=8.5, color=INK2)
ax.set_xticks([2024, 2025, 2026]); ax.set_xlim(2023.8, 2026.75); ax.set_ylim(35, 112)
ax.set_ylabel("Appropriation, FY2024 = 100 (nominal)"); ax.set_title("Congress held the money roughly flat", fontsize=11.5)
# (b) awards indexed
ax = axs[0, 1]
for ag in ["NSF", "NIH"]:
    a = f[(f.agency == ag) & (f.measure == "awards")].sort_values("fy")
    ax.plot(a.fy, a.value / a.value.iloc[0] * 100, color=C[ag], lw=2, marker="o", ms=6)
    lab = "NSF, all awards" if ag == "NSF" else "NIH, competing\nresearch grants"
    off, ha = ((8, 0), "left") if ag == "NSF" else ((-12, -34), "right")
    ax.annotate(f"{lab}\n{int(a.value.iloc[-1]):,}", (a.fy.iloc[-1], a.value.iloc[-1] / a.value.iloc[0] * 100), xytext=off,
                textcoords="offset points", va="center", ha=ha, fontsize=9, color=INK2)
ax.set_xticks([2024, 2025, 2026]); ax.set_xlim(2023.8, 2026.75); ax.set_ylim(35, 112)
ax.set_ylabel("Awards, FY2024 = 100"); ax.set_title("…but far fewer new awards went out", fontsize=11.5)
# (c) Stack Overflow monthly questions
ax = axs[1, 0]
ax.plot(so.month, so.questions, color=OPEN, lw=2)
ax.set_yscale("log"); ax.axvline(pd.Timestamp("2022-11-30"), color=MUTED, lw=1.2)
ax.text(pd.Timestamp("2022-10-01"), 30000, "ChatGPT\nreleased", fontsize=8.5, color=INK2, va="top", ha="right")
ax.annotate(f"{so.questions.iloc[-1]:,} in Oct 2026", (so.month.iloc[-1], so.questions.iloc[-1]), xytext=(-110, 6),
            textcoords="offset points", fontsize=9, color=INK2)
ax.set_ylabel("New questions a month (log scale)"); ax.xaxis.set_major_locator(mdates.YearLocator(2)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_title("Stack Overflow: the public Q&A funnel emptied", fontsize=11.5)
# (d) Tailwind: indexed bars on a log axis
ax = axs[1, 1]
labs = ["npm downloads\n(Jan 2023 → Oct 2026)", "docs traffic\n(early 2023 → Jan 2026)", "revenue\n(to Jan 2026)"]
vals = [631.9 / 19.9, 0.60, 0.20]; cols = [THIRD, CLOSED, CLOSED]
y = [2, 1, 0]
for yy, v, c in zip(y, vals, cols):
    ax.barh(yy, v - 1 if v > 1 else 1 - v, left=1 if v > 1 else v, height=0.5, color=c)
    ax.text(v * (1.15 if v > 1 else 0.87), yy, f"×{v:.0f}" if v > 1 else f"{(v - 1) * 100:+.0f}%", va="center",
            ha="left" if v > 1 else "right", fontsize=10, fontweight="bold", color=INK)
ax.set_xscale("log"); ax.set_xlim(0.08, 80); ax.axvline(1, color=MUTED, lw=1.2)
ax.set_xticks([0.1, 0.3, 1, 3, 10, 30]); ax.set_xticklabels(["0.1×", "0.3×", "1×", "3×", "10×", "30×"]); ax.minorticks_off()
ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=9); ax.grid(axis="y", visible=False)
ax.set_xlabel("Change since early 2023 (log scale)")
ax.set_title("Tailwind: usage soared, the paid funnel shrank", fontsize=11.5)
fig.suptitle("Two shocks to open-science business models, 2023–26", x=0.06, ha="left", fontsize=14, fontweight="bold", y=0.99)
fig.text(0.06, -0.02, "Sources: data/us_science_funding.csv (NSF budget request, CRS, AIP, NIH Extramural Nexus); Stack Exchange API (deleted questions excluded); "
         "Tailwind's founder on GitHub, 2026-01-07, and the npm API.\nDownloads include automated and AI-agent installs, so they overstate users. Stack Overflow questions were already falling before ChatGPT.",
         fontsize=8, color=INK2)
fig.savefig("figures/two_shocks.png"); print("saved")
